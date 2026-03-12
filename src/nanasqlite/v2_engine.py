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
    ):
        self._connection = connection
        self._table_name = table_name

        # Serialization function injected from core.py
        self._serialize = serialize_func if serialize_func else lambda v: str(v)

        # Flush Settings
        if flush_mode not in ("immediate", "count", "time", "manual"):
            raise ValueError(f"Invalid flush_mode: {flush_mode}")
        self._flush_mode = flush_mode
        self._flush_interval = flush_interval
        self._flush_count = flush_count
        self._max_chunk_size = max_chunk_size

        # Lane 1: KVS Normal Lane (Staging Buffer)
        # Structure: {"key": {"action": "set"|"delete", "value": ...}}
        self._staging_lock = threading.Lock()
        self._staging_buffer: dict[str, dict[str, Any]] = {}
        self._staging_changes = 0 # Track number of mutations since last flush

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
        logger.error("NanaSQLite DLQ Entry: %s", error_msg)

    # ==================== KVS Lane (Lane 1) Public API ====================

    def kvs_set(self, key: str, value: Any) -> None:
        """Queue a set operation in the staging buffer."""
        # Serialize immediately on the calling thread to catch type errors early
        # and prevent slow serialization during the flush transaction.
        serialized_value = self._serialize(value)

        with self._staging_lock:
            self._staging_buffer[key] = {"action": "set", "value": serialized_value}
            self._staging_changes += 1

        self._check_auto_flush()

    def kvs_delete(self, key: str) -> None:
        """Queue a delete operation in the staging buffer."""
        with self._staging_lock:
            self._staging_buffer[key] = {"action": "delete"}
            self._staging_changes += 1

        self._check_auto_flush()

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

    def flush(self) -> None:
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
        if self._flush_pending.acquire(blocking=False):
            self._worker.submit(self._run_flush)

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
        # 1. Capture current snapshot of staging buffer
        with self._staging_lock:
            if not self._staging_buffer and self._strict_queue.empty():
                return

            # Take a copy and clear the running buffer to unblock incoming writes
            current_buffer = self._staging_buffer
            self._staging_buffer = {}
            self._staging_changes = 0

        # We need to process KVS in chunks to avoid locking the DB for too long
        kvs_items = list(current_buffer.items())
        total_kvs = len(kvs_items)
        chunk_size = self._max_chunk_size

        if total_kvs == 0:
            # No KVS items but might be strict queue items — process those in one batch
            try:
                self._process_transaction_chunk([])
            except Exception as e:
                logger.warning("NanaSQLite v2 Engine: Strict-only chunk failed. Error: %s", e)
        else:
            for i in range(0, total_kvs, chunk_size):
                chunk = kvs_items[i : i + chunk_size]
                # Create a localized transaction per chunk
                try:
                    self._process_transaction_chunk(chunk)
                except Exception as e:
                    # If a chunk fails, we enter a recovery mode for that specific chunk
                    logger.warning("NanaSQLite v2 Engine: Chunk transaction failed, entering DLQ recovery. Error: %s", e)
                    self._recover_chunk_via_dlq(chunk)


    def _process_transaction_chunk(self, kvs_chunk: list[tuple[str, dict[str, Any]]]) -> None:
        """Process a single KVS chunk and run all pending strict tasks in one transaction."""
        sets = []
        deletes = []
        for key, op in kvs_chunk:
            if op["action"] == "set":
                sets.append((key, op["value"]))
            elif op["action"] == "delete":
                deletes.append((key,))

        cursor = self._connection.cursor()

        # Start Transaction
        cursor.execute("BEGIN IMMEDIATE TRANSACTION;")
        try:
            # 1. Process KVS sets (UPSERT)
            if sets:
                cursor.executemany(
                    f"INSERT OR REPLACE INTO {self._table_name} (key, value) VALUES (?, ?)",
                    sets
                )

            # 2. Process KVS deletes
            if deletes:
                cursor.executemany(
                    f"DELETE FROM {self._table_name} WHERE key = ?",
                    deletes
                )

            # 3. Process Strict Lane
            self._process_strict_queue(cursor)

            # Commit Transaction
            cursor.execute("COMMIT;")
        except Exception:
            cursor.execute("ROLLBACK;")
            raise

    def _process_strict_queue(self, cursor: apsw.Cursor) -> None:
        """Process all pending tasks in the strict priority queue."""
        # Empty the queue entirely into the transaction
        while not self._strict_queue.empty():
            task: StrictTask = self._strict_queue.get_nowait()
            try:
                if task.task_type == TASK_EXECUTE:
                    if task.parameters:
                        cursor.execute(task.sql, task.parameters)
                    else:
                        cursor.execute(task.sql)
                elif task.task_type == TASK_EXECUTEMANY:
                    cursor.executemany(task.sql, task.parameters) # type: ignore

                if task.on_success:
                    task.on_success()

            except Exception as e:
                # Individual StrictTask failed. Add to DLQ and re-raise to rollback the transaction
                if task.on_error:
                    # Notify the caller
                    try:
                        task.on_error(e)
                    except Exception as handler_err:
                        logger.error("Error in on_error callback: %s", handler_err)

                self._add_to_dlq(f"StrictTask failed: {e}", task)
                # Raising here ensures the chunk rolls back, but since we pulled from the queue
                # using get_nowait(), the task is already out of the queue (it's in the DLQ).
                # The next retry of the KVS chunk will NOT include this failed strict task.
                raise

    def _recover_chunk_via_dlq(self, failed_kvs_chunk: list[tuple[str, dict[str, Any]]]) -> None:
        """
        When a chunk flush fails (due to a poison pill in KVS data), process it row-by-row.
        If a row fails, put it in the DLQ and continue.
        """
        cursor = self._connection.cursor()

        for key, op in failed_kvs_chunk:
            try:
                cursor.execute("BEGIN IMMEDIATE TRANSACTION;")
                if op["action"] == "set":
                    cursor.execute(f"INSERT OR REPLACE INTO {self._table_name} (key, value) VALUES (?, ?)", (key, op["value"]))
                elif op["action"] == "delete":
                    cursor.execute(f"DELETE FROM {self._table_name} WHERE key = ?", (key,))

                # We attempt to drain any NEW strict queue items here per-row as well,
                # though strictly speaking they should be clean by now.
                self._process_strict_queue(cursor)
                cursor.execute("COMMIT;")
            except Exception as e:
                cursor.execute("ROLLBACK;")
                self._add_to_dlq(f"KVS Poison Pill row '{key}' failed: {e}", (key, op))
                # Row is skipped, system continues processing

    def get_dlq(self) -> list[dict[str, Any]]:
        """Return a copy of the Dead Letter Queue for inspection."""
        with self._dlq_lock:
            return [
                {"error": err, "item": item, "timestamp": ts}
                for err, item, ts in self.dlq
            ]

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
                # It's a KVS row (key, op)
                key, op = item
                with self._staging_lock:
                    self._staging_buffer[key] = op
                    self._staging_changes += 1
            else:
                logger.warning("NanaSQLite v2 Engine: Unknown item type in DLQ, cannot retry: %s", item)

        self._check_auto_flush()

    def shutdown(self) -> None:
        """Gracefully shutdown the engine, forcing a synchronous final flush."""
        if not self._running:
            return

        self._running = False
        if self._timer_thread:
            # Wake up the timer thread to let it exit
            self._flush_event.set()
            # Do not join timer thread here to avoid deadlocks in atexit, let it die daemonically if needed

        # Unregister to avoid multiple calls
        atexit.unregister(self.shutdown)

        # Cancel any pending (not yet started) futures so that shutdown()
        # returns promptly.  The final synchronous _perform_flush() below
        # guarantees all staged data is committed before we return.
        self._worker.shutdown(wait=True, cancel_futures=True)

        # Ensure final data is flushed synchronously on main/exit thread
        self._perform_flush()
