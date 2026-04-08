"""
NanaSQLite v2 Engine: Background worker for high-performance, non-blocking SQLite persistence.

This module implements the core "hybrid lane" architecture for v2:
- Lane 1 (KVS Normal Lane): A staging dictionary for write coalescing.
- Lane 2 (Strict Lane): A priority queue for explicitly ordered SQL tasks.

Features:
- 4 Flush Modes: immediate, count, time, manual.
- Write Coalescing: Multiple writes to the same key are merged before hitting the disk.
- Sequence ID: Prevents priority queue crashes when timestamps collide.
- Chunk Flushing: Breaks down large buffers into smaller transactions.
- Dead Letter Queue (DLQ): Isolates corrupt data to prevent poison pill scenarios.
- Graceful Shutdown: Ensures data is flushed via atexit.
"""

from __future__ import annotations

import atexit
import contextlib
import itertools
import logging
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

import apsw

logger = logging.getLogger(__name__)

# Task types for the strict lane
TASK_EXECUTE = "execute"
TASK_EXECUTEMANY = "executemany"


@dataclass(order=True)
class StrictTask:
    """A single task for the strict/raw SQL lane (Lane 2)."""

    priority: int
    sequence_id: int
    task_type: str = field(compare=False)
    sql: str = field(compare=False)
    parameters: tuple | list | dict | None = field(compare=False)
    # Future-proof: Callback for when the task is successfully executed in the background
    on_success: Callable | None = field(compare=False, default=None)
    on_error: Callable[[Exception], None] | None = field(compare=False, default=None)


class V2Engine:
    """
    Background flush engine for NanaSQLite v2 mode.
    Handles offloading I/O to a single dedicated thread.
    """

    def __init__(
        self,
        connection: apsw.Connection,
        table_name: str,
        flush_mode: Literal["immediate", "count", "time", "manual"] = "immediate",
        flush_interval: float = 3.0,
        flush_count: int = 100,
        max_chunk_size: int = 1000,
        serialize_func: Callable[[Any], str | bytes] | None = None,
        enable_metrics: bool = False,
        shared_lock: threading.RLock | None = None,
    ):
        self._connection = connection
        self._table_name = table_name

        # Serialization function injected from core.py
        self._serialize = serialize_func if serialize_func else str
        self._shared_lock = shared_lock

        # Flush Settings
        if flush_mode not in ("immediate", "count", "time", "manual"):
            raise ValueError(f"Invalid flush_mode: {flush_mode}")
        self._flush_mode = flush_mode
        self._flush_interval = flush_interval
        self._flush_count = flush_count
        self._max_chunk_size = max_chunk_size

        # Lane 1: KVS Normal Lane (Staging Buffer)
        # Structure: {(table_name, key): {"action": "set"|"delete", "value": ...}}
        self._staging_lock = threading.Lock()
        self._staging_buffer: dict[tuple[str, str], dict[str, Any]] = {}
        self._staging_changes = 0  # Track number of mutations since last flush

        # Lane 2: Strict / Raw SQL Lane (Priority Queue)
        self._strict_queue: queue.PriorityQueue[StrictTask] = queue.PriorityQueue()
        self._sequence_counter = itertools.count()

        # Dead Letter Queue (DLQ)
        # Stores keys that poisoned the batch, or StrictTasks that failed.
        # Structure: [(error_msg, object, timestamp), ...]
        self.dlq: list[tuple[str, Any, float]] = []
        self._dlq_lock = threading.Lock()

        # Threading/Worker state
        self._worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="NanaSQLite-v2Engine")
        self._running = True
        self._flush_event = threading.Event()
        self._timer_thread: threading.Thread | None = None

        # Metrics
        self._enable_metrics = enable_metrics
        self._metrics_lock = threading.Lock()
        self._metrics: dict[str, Any] = {
            "flush_count": 0,
            "kvs_items_flushed": 0,
            "strict_tasks_executed": 0,
            "dlq_errors": 0,
            "last_flush_time": None,
            "total_flush_time_ms": 0.0,
        }
        # Guard against unbounded queue growth: only one _perform_flush may be
        # pending in the executor at any time.  flush() is called on the hot
        # path (every write in "immediate" mode), so submitting one future per
        # write would pile up thousands of queued tasks and make
        # shutdown(wait=True) block for a long time.
        self._flush_pending = threading.Lock()

        # Start timer if time mode
        if self._flush_mode == "time":
            self._start_timer()

        # Register cleanup on exit
        atexit.register(self.shutdown)

    def _start_timer(self) -> None:
        """Starts the background timer thread for 'time' mode."""

        def _timer_loop() -> None:
            while self._running:
                # wait returns True if event is set, False if timeout.
                # If we timeout, it means it's time to flush.
                interrupted = self._flush_event.wait(self._flush_interval)
                if not self._running:
                    break
                if not interrupted:
                    self.flush()
                else:
                    self._flush_event.clear()

        self._timer_thread = threading.Thread(target=_timer_loop, daemon=True, name="NanaSQLite-v2Timer")
        self._timer_thread.start()

    def _add_to_dlq(self, error_msg: str, item: Any) -> None:
        """Adds a failed item to the Dead Letter Queue."""
        with self._dlq_lock:
            self.dlq.append((error_msg, item, time.time()))
        if self._enable_metrics:
            with self._metrics_lock:
                self._metrics["dlq_errors"] += 1
        logger.error("NanaSQLite DLQ Entry: %s", error_msg)

    # ==================== KVS Lane (Lane 1) Public API ====================

    def kvs_set(self, table_name: str, key: str, value: Any) -> None:
        """Queue a set operation in the staging buffer."""
        # Serialize immediately on the calling thread to catch type errors early
        # and prevent slow serialization during the flush transaction.
        serialized_value = self._serialize(value)

        with self._staging_lock:
            self._staging_buffer[(table_name, key)] = {"action": "set", "value": serialized_value}
            self._staging_changes += 1

        self._check_auto_flush()

    def kvs_delete(self, table_name: str, key: str) -> None:
        """Queue a delete operation in the staging buffer."""
        with self._staging_lock:
            self._staging_buffer[(table_name, key)] = {"action": "delete"}
            self._staging_changes += 1

        self._check_auto_flush()

    def kvs_get_staging(self, table_name: str, key: str) -> dict[str, Any] | None:
        """Read a single item from the staging buffer."""
        with self._staging_lock:
            return self._staging_buffer.get((table_name, key))

    def _check_auto_flush(self) -> None:
        """Trigger auto-flush based on the current mode."""
        if self._flush_mode == "immediate":
            self.flush()
        elif self._flush_mode == "count":
            with self._staging_lock:
                current_count = self._staging_changes
            if current_count >= self._flush_count:
                self.flush()

    # ==================== Strict Lane (Lane 2) Public API ====================

    def enqueue_strict_task(
        self,
        task_type: Literal["execute", "executemany"],
        sql: str,
        parameters: tuple | list | dict | None = None,
        priority: int = 10,
        on_success: Callable | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        """
        Enqueue a strict ordering task (raw SQL or strict insert/delete).
        priority: lower number = higher priority. Default 10.
        """
        task = StrictTask(
            priority=priority,
            sequence_id=next(self._sequence_counter),
            task_type=task_type,
            sql=sql,
            parameters=parameters,
            on_success=on_success,
            on_error=on_error,
        )
        self._strict_queue.put(task)

        # Strict tasks must always trigger a flush immediately, regardless of
        # the configured flush_mode.  Both execute() and execute_many() use
        # event.wait() (with no timeout) to synchronously await the task's
        # completion callback; if we skip the flush here the caller hangs
        # forever in count/time/manual modes.
        self.flush()

    # ==================== Flush / Sync API ====================

    def flush(self, wait: bool = False) -> None:
        """Trigger an asynchronous flush operation on the background worker."""
        if not self._running:
            return

        # Reset timer if in time mode
        if self._flush_mode == "time":
            self._flush_event.set()

        # Coalesce concurrent flush requests: only submit one _perform_flush to
        # the executor at a time.  If a submission is already queued (lock is
        # held), subsequent calls are no-ops — the already-queued future will
        # process all pending writes when it runs.
        future = None
        if self._flush_pending.acquire(blocking=False):
            future = self._worker.submit(self._run_flush)

        if wait:
            if future:
                future.result()
            else:
                # If a flush is currently pending/running, we wait for it to finish
                # by submitting a dummy task to the single-worker executor.
                self._worker.submit(lambda: None).result()

    def _run_flush(self) -> None:
        """Executor entry point: release the pending-guard then flush."""
        # Release the guard *before* the flush so that any writes arriving
        # during the flush can schedule a follow-up submission.
        self._flush_pending.release()
        self._perform_flush()

    def _perform_flush(self) -> None:
        """
        The actual flush logic executed by the single background thread.
        Combines Lane 1 (KVS) and Lane 2 (Strict Queue) into a single transaction.
        Implements chunking and DLQ error handling.
        """
        start_time = time.time() if self._enable_metrics else 0.0

        # 1. Capture current snapshot of staging buffer
        with self._staging_lock:
            current_buffer = self._staging_buffer
            self._staging_buffer = {}
            self._staging_changes = 0

        # We need to process KVS in chunks to avoid locking the DB for too long
        kvs_items = list(current_buffer.items())
        total_kvs = len(kvs_items)
        chunk_size = self._max_chunk_size

        if total_kvs > 0:
            for i in range(0, total_kvs, chunk_size):
                chunk = kvs_items[i : i + chunk_size]
                # Create a localized transaction per chunk
                try:
                    self._process_kvs_chunk(chunk)
                except Exception as e:
                    # If a chunk fails, we enter a recovery mode for that specific chunk
                    logger.warning(
                        "NanaSQLite v2 Engine: Chunk transaction failed, entering DLQ recovery. Error: %s", e
                    )
                    self._recover_chunk_via_dlq(chunk)

        # Process all remaining Strict Lane tasks
        self._process_all_strict_tasks()

        if self._enable_metrics:
            flush_duration_ms = (time.time() - start_time) * 1000
            current_time = time.time()
            with self._metrics_lock:
                self._metrics["flush_count"] += 1
                self._metrics["last_flush_time"] = current_time
                self._metrics["total_flush_time_ms"] += flush_duration_ms

    def _process_kvs_chunk(self, kvs_chunk: list[tuple[tuple[str, str], dict[str, Any]]]) -> None:
        """Process a single KVS chunk in its own transaction."""
        table_ops: dict[str, dict[str, list]] = {}

        for (table_name, key), op in kvs_chunk:
            if table_name not in table_ops:
                table_ops[table_name] = {"sets": [], "deletes": []}
            if op["action"] == "set":
                table_ops[table_name]["sets"].append((key, op["value"]))
            elif op["action"] == "delete":
                table_ops[table_name]["deletes"].append((key,))

        cursor = self._connection.cursor()
        lock_acquired = False
        if self._shared_lock is not None:
            self._shared_lock.acquire()
            lock_acquired = True

        try:
            cursor.execute("BEGIN IMMEDIATE TRANSACTION;")
            try:
                flushed_count = 0
                for table_name, ops in table_ops.items():
                    sets = ops["sets"]
                    deletes = ops["deletes"]
                    if sets:
                        cursor.executemany(
                            f"INSERT OR REPLACE INTO {table_name} (key, value) VALUES (?, ?)",  # nosec
                            sets,
                        )
                    if deletes:
                        cursor.executemany(
                            f"DELETE FROM {table_name} WHERE key = ?",  # nosec
                            deletes,
                        )
                    flushed_count += len(sets) + len(deletes)

                if self._enable_metrics:
                    with self._metrics_lock:
                        self._metrics["kvs_items_flushed"] += flushed_count

                cursor.execute("COMMIT;")
            except Exception:
                cursor.execute("ROLLBACK;")
                raise
        finally:
            if lock_acquired and self._shared_lock is not None:
                self._shared_lock.release()

    def _process_all_strict_tasks(self) -> None:
        """Process all pending tasks in the strict priority queue. Each task gets its own transaction."""
        cursor = self._connection.cursor()
        while not self._strict_queue.empty():
            try:
                task: StrictTask = self._strict_queue.get_nowait()
            except queue.Empty:
                break

            lock_acquired = False
            if self._shared_lock is not None:
                self._shared_lock.acquire()
                lock_acquired = True

            try:
                cursor.execute("BEGIN IMMEDIATE TRANSACTION;")
                try:
                    if task.task_type == TASK_EXECUTE:
                        if task.parameters:
                            cursor.execute(task.sql, task.parameters)
                        else:
                            cursor.execute(task.sql)
                    elif task.task_type == TASK_EXECUTEMANY:
                        cursor.executemany(task.sql, task.parameters)  # type: ignore

                    if self._enable_metrics:
                        with self._metrics_lock:
                            self._metrics["strict_tasks_executed"] += 1

                    cursor.execute("COMMIT;")

                    if task.on_success:
                        try:
                            task.on_success()
                        except Exception as cb_err:
                            logger.error("Error in on_success callback: %s", cb_err)

                except Exception as e:
                    cursor.execute("ROLLBACK;")
                    if task.on_error:
                        try:
                            task.on_error(e)
                        except Exception as handler_err:
                            logger.error("Error in on_error callback: %s", handler_err)
                    self._add_to_dlq(f"StrictTask failed: {e}", task)

            except Exception as e:
                # BEGIN IMMEDIATE TRANSACTION failed (e.g., BusyError)
                if task.on_error:
                    try:
                        task.on_error(e)
                    except Exception as handler_err:
                        logger.error("Error in on_error callback: %s", handler_err)
                self._add_to_dlq(f"StrictTask transaction start failed: {e}", task)

            finally:
                if lock_acquired and self._shared_lock is not None:
                    self._shared_lock.release()

    def _recover_chunk_via_dlq(self, failed_kvs_chunk: list[tuple[tuple[str, str], dict[str, Any]]]) -> None:
        """
        When a chunk flush fails (due to a poison pill in KVS data), process it row-by-row.
        If a row fails, put it in the DLQ and continue.
        """
        cursor = self._connection.cursor()
        lock_acquired = False
        if self._shared_lock is not None:
            self._shared_lock.acquire()
            lock_acquired = True

        try:
            for (table_name, key), op in failed_kvs_chunk:
                try:
                    cursor.execute("BEGIN IMMEDIATE TRANSACTION;")
                    if op["action"] == "set":
                        cursor.execute(
                            f"INSERT OR REPLACE INTO {table_name} (key, value) VALUES (?, ?)", (key, op["value"])
                        )  # nosec
                    elif op["action"] == "delete":
                        cursor.execute(f"DELETE FROM {table_name} WHERE key = ?", (key,))  # nosec

                    if self._enable_metrics:
                        with self._metrics_lock:
                            self._metrics["kvs_items_flushed"] += 1

                    cursor.execute("COMMIT;")
                except Exception as e:
                    cursor.execute("ROLLBACK;")
                    self._add_to_dlq(f"KVS Poison Pill row '{key}' failed: {e}", ((table_name, key), op))
        finally:
            if lock_acquired and self._shared_lock is not None:
                self._shared_lock.release()

    def get_dlq(self) -> list[dict[str, Any]]:
        """Return a copy of the Dead Letter Queue for inspection."""
        with self._dlq_lock:
            return [{"error": err, "item": item, "timestamp": ts} for err, item, ts in self.dlq]

    def retry_dlq(self) -> None:
        """
        Move all items from DLQ back to their respective lanes for retry.
        Note: KVS items are moved back to the staging buffer,
        and StrictTasks are re-enqueued.
        """
        with self._dlq_lock:
            items = list(self.dlq)
            self.dlq.clear()

        for _, item, _ in items:
            if isinstance(item, StrictTask):
                self._strict_queue.put(item)
            elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], dict) and "action" in item[1]:
                # It's a KVS row ((table_name, key), op)
                table_key, op = item
                with self._staging_lock:
                    self._staging_buffer[table_key] = op
                    self._staging_changes += 1
            else:
                logger.warning("NanaSQLite v2 Engine: Unknown item type in DLQ, cannot retry: %s", item)

        self._check_auto_flush()

    def clear_dlq(self) -> None:
        """Clear all items from the Dead Letter Queue."""
        with self._dlq_lock:
            self.dlq.clear()

    def get_metrics(self) -> dict[str, Any]:
        """Return the current metrics if enabled."""
        if not self._enable_metrics:
            return {}
        with self._metrics_lock:
            metrics = self._metrics.copy()
            # Dynamic metrics
            with self._staging_lock:
                metrics["current_staging_count"] = self._staging_changes
            metrics["current_strict_queue_size"] = self._strict_queue.qsize()
            return metrics

    def shutdown(self) -> None:
        """Gracefully shutdown the engine, forcing a synchronous final flush."""
        # Use a lock to ensure only one thread performs shutdown
        with self._staging_lock:
            if not self._running:
                return
            self._running = False

        # Wake up the timer thread to let it exit
        if self._timer_thread:
            self._flush_event.set()
            # Do not join timer thread here to avoid deadlocks in atexit, let it die daemonically if needed

        # Unregister to avoid multiple calls from atexit and manual close()
        with contextlib.suppress(Exception):  # pragma: no cover
            atexit.unregister(self.shutdown)

        # Shutdown worker executor.
        # cancel_futures=True ensures we don't start new flushes if they were already queued.
        # wait=True ensures the current flush (if any) is finished before we do the final sync flush.
        try:
            self._worker.shutdown(wait=True, cancel_futures=True)
        except Exception as e:
            logger.warning("NanaSQLite v2 Engine: Error during worker shutdown: %s", e)

        # Ensure final data is flushed synchronously on main/exit thread.
        # This is safe because the worker thread is now finished.
        try:
            self._perform_flush()
        except Exception as e:
            logger.error("NanaSQLite v2 Engine: Final flush failed during shutdown: %s", e)

        # Clear any remaining strict tasks to prevent deadlocks (e.g., if _perform_flush failed entirely)
        if not self._strict_queue.empty():
            from .exceptions import NanaSQLiteClosedError

            shutdown_err = NanaSQLiteClosedError("V2Engine shut down before task could complete.")
            while not self._strict_queue.empty():
                try:
                    task = self._strict_queue.get_nowait()
                    if task.on_error:
                        try:
                            task.on_error(shutdown_err)
                        except Exception as callback_exc:
                            # Do not let a buggy on_error callback break shutdown, but log it for observability.
                            logger.warning(
                                "NanaSQLite v2 Engine: on_error callback failed during shutdown: %s",
                                callback_exc,
                            )
                except queue.Empty:
                    break
