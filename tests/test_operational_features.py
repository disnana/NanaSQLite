"""Operational contracts: bounded work, streaming, freshness and diagnostics."""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from nanasqlite import AsyncNanaSQLite, NanaSQLite
from nanasqlite.exceptions import NanaSQLiteClosedError, NanaSQLiteDatabaseError, NanaSQLiteValidationError
from nanasqlite.hooks import BaseHook


def test_status_tracks_coalescing_failures_and_recovery(tmp_path, caplog):
    with NanaSQLite(str(tmp_path / "status.db"), v2_mode=True, flush_mode="manual", v2_max_dlq_size=1) as db:
        db["secret-key"] = "secret-value"
        db["secret-key"] = "replacement"
        assert db.get_status()["pending_kvs_count"] == 1
        assert db.get_status()["oldest_pending_age_seconds"] >= 0
        db.flush(wait=True)
        status = db.get_status()
        assert status["pending_kvs_count"] == status["flushing_kvs_count"] == 0
        assert status["oldest_pending_age_seconds"] is None
        assert status["last_successful_flush_time"] is not None
        # A SQLite trigger supplies an application-controlled error message.
        db._connection.execute(
            "CREATE TRIGGER fail_write BEFORE INSERT ON data BEGIN SELECT RAISE(ABORT, 'secret-error'); END"
        )
        db["a"] = "secret-value"
        db["b"] = "secret-value"
        db.flush(wait=True)
        failed = db.get_status()
        assert failed["failed_count"] == 1
        assert failed["failure_count"] == 2
        assert failed["dropped_failure_count"] == 1
        assert failed["last_failure_time"] is not None
        assert failed["last_successful_flush_time"] == status["last_successful_flush_time"]
        assert "secret" not in repr(failed) + repr(db.get_dlq_summary())
        assert "secret" not in caplog.text
        with pytest.raises(NanaSQLiteDatabaseError, match="failed writes"):
            list(db.iter_items())
        assert db.get_status()["last_successful_flush_time"] == status["last_successful_flush_time"]
        db._connection.execute("DROP TRIGGER fail_write")
        db.retry_dlq()
        db.flush(wait=True)
        assert db.get_status()["failed_count"] == 0
        assert db.get_status()["dropped_failure_count"] == 1


def test_status_distinguishes_running_flush(tmp_path, monkeypatch):
    with NanaSQLite(str(tmp_path / "running.db"), v2_mode=True, flush_mode="manual") as db:
        entered, release = threading.Event(), threading.Event()
        process = db._v2_engine._process_kvs_chunk

        def blocked(chunk):
            entered.set()
            assert release.wait(5)
            process(chunk)

        monkeypatch.setattr(db._v2_engine, "_process_kvs_chunk", blocked)
        db["k"] = 1
        db.flush()
        try:
            assert entered.wait(5)
            state = db.get_status()
            assert state["flush_active"]
            assert state["flushing_kvs_count"] == 1
            assert state["pending_kvs_count"] == 0
            assert state["last_successful_flush_time"] is None
        finally:
            release.set()
        db.flush(wait=True)


@pytest.mark.parametrize("strategy", ["unbounded", "lru", "ttl"])
def test_auto_cache_external_update_delete_and_negative_cache(tmp_path, strategy):
    path = str(tmp_path / "fresh.db")
    options = {"cache_size": 20} if strategy == "lru" else {"cache_ttl": 60} if strategy == "ttl" else {}
    with NanaSQLite(path) as writer, NanaSQLite(path, cache_consistency="auto", cache_strategy=strategy, **options) as reader:
        writer["k"] = 1
        assert reader["k"] == 1
        assert reader.get("absent") is None
        writer["k"] = 2
        writer["absent"] = 3
        assert reader.batch_get(["k", "absent"]) == {"k": 2, "absent": 3}
        del writer["k"]
        assert "k" not in reader
        assert reader.get("k") is None


def test_auto_cache_shared_connection_raw_sql_and_rollback(tmp_path):
    with NanaSQLite(str(tmp_path / "shared.db"), cache_consistency="auto", warn_duplicate_table_instance=False) as db:
        a, b = db.table("users"), db.table("users")
        a["k"] = 1
        assert b["k"] == 1
        a["k"] = 2
        assert b["k"] == 2
        db.execute('UPDATE users SET value = ? WHERE key = ?', ("3", "k"))
        assert b["k"] == 3
        with pytest.raises(RuntimeError), a.transaction():
            a["k"] = 4
            assert b["k"] == 4
            raise RuntimeError("rollback")
        assert a["k"] == b["k"] == 3


def test_default_cache_keeps_manual_contract(tmp_path):
    path = str(tmp_path / "manual.db")
    with NanaSQLite(path) as a, NanaSQLite(path) as b:
        a["k"] = 1
        assert b["k"] == 1
        a["k"] = 2
        assert b["k"] == 1
        b.refresh("k")
        assert b["k"] == 2


def test_auto_cache_concurrent_reads_and_shared_writes(tmp_path):
    with NanaSQLite(str(tmp_path / "threads.db"), cache_consistency="auto", warn_duplicate_table_instance=False) as db:
        a, b = db.table("items"), db.table("items")
        a["k"] = 0

        def write():
            for i in range(150):
                a["k"] = i

        def read():
            for _ in range(200):
                assert isinstance(b["k"], int)
                assert b.get("absent") is None

        with ThreadPoolExecutor(max_workers=3) as pool:
            tasks = [pool.submit(write), pool.submit(read), pool.submit(read)]
            for task in tasks:
                task.result(timeout=10)
        assert b["k"] == 149


@pytest.mark.parametrize("options", [{"v2_mode": True}, {"memory_first": True}, {"cache_persistence_ttl": True}])
def test_auto_cache_rejects_incompatible_modes(options):
    with pytest.raises(NanaSQLiteValidationError):
        NanaSQLite(":memory:", cache_consistency="auto", **options)


class ReadHook(BaseHook):
    def after_read(self, db, key, value):
        return {"wrapped": value}


@pytest.mark.parametrize("mode", [{}, {"v2_mode": True, "flush_mode": "manual"}, {"memory_first": True}])
def test_iterator_reads_decrypted_hooked_pages_without_cache(tmp_path, mode):
    with NanaSQLite(str(tmp_path / "iter.db"), encryption_key=AESGCM.generate_key(128), hooks=[ReadHook()], **mode) as db:
        values = {f"k{i:03d}": {"n": i} for i in range(31)}
        db.batch_update(values)
        db.flush(wait=True)
        db.clear_cache()
        assert list(db.iter_items(batch_size=7)) == [(k, {"wrapped": v}) for k, v in sorted(values.items())]
        assert db._cache.size == 0
        assert not db._all_loaded


def test_iterator_releases_cursor_and_lock_between_pages(tmp_path):
    with NanaSQLite(str(tmp_path / "iter.db")) as db:
        db.batch_update({"a": 1, "b": 2, "c": 3})
        stream = db.iter_items(1)
        assert next(stream) == ("a", 1)
        db["b"] = 20
        del db["c"]
        db["d"] = 4
        assert list(stream) == [("b", 20), ("d", 4)]
        stream.close()
        assert db.backup(str(tmp_path / "snapshot.db")) is None


@pytest.mark.parametrize("size", [0, -1, True, 1.5, "1"])
def test_iterator_validates_batch_size(size):
    with NanaSQLite(":memory:") as db, pytest.raises(NanaSQLiteValidationError):
        list(db.iter_items(size))


@pytest.mark.asyncio
async def test_async_features_and_child_inheritance(tmp_path):
    path = str(tmp_path / "async.db")
    async with AsyncNanaSQLite(path, cache_consistency="auto", max_pending_operations=2) as db:
        child = await db.table("data", warn_duplicate_table_instance=False)
        assert child._admission is db._admission
        await db.aset("k", 1)
        assert await child.aget("k") == 1
        with NanaSQLite(path) as other:
            other["k"] = 2
            other["new"] = 3
        assert await child.aget("k") == 2
        assert await db.abatch_get(["k", "new"]) == {"k": 2, "new": 3}
        assert [pair async for pair in child.aiter_items(1)] == [("k", 2), ("new", 3)]
        assert (await db.aget_status())["mode"] == "immediate"
        assert await db.aget_dlq_summary() == []
        await child.close()


@pytest.mark.asyncio
async def test_admission_timeout_and_cancelled_worker_retains_slot(tmp_path):
    async with AsyncNanaSQLite(str(tmp_path / "bound.db"), max_pending_operations=1, admission_timeout=0.03) as db:
        await db.aset("initial", 1)
        entered, release = threading.Event(), threading.Event()

        def slow_write():
            entered.set()
            assert release.wait(5)
            db._db["accepted"] = True

        task = asyncio.create_task(db._run_in_executor(slow_write))
        try:
            assert await asyncio.to_thread(entered.wait, 5)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            with pytest.raises(asyncio.TimeoutError):
                await db.aset("rejected", True)
            assert len(db._admission.active) == 1
        finally:
            release.set()
        await asyncio.gather(*tuple(db._admission.active))
        assert await db.aget("accepted") is True
        assert await db.aget("rejected") is None
        await db.aset("after", True)


@pytest.mark.asyncio
async def test_cancelled_waiter_and_close_drain(tmp_path):
    db = AsyncNanaSQLite(str(tmp_path / "close.db"), max_pending_operations=1)
    await db.aset("initial", 1)
    entered, release = threading.Event(), threading.Event()

    def slow():
        entered.set()
        assert release.wait(5)
        db._db["accepted"] = 2

    task = asyncio.create_task(db._run_in_executor(slow))
    try:
        assert await asyncio.to_thread(entered.wait, 5)
        waiter = asyncio.create_task(db.aset("cancelled", 3))
        await asyncio.sleep(0)
        waiter.cancel()
        with pytest.raises(asyncio.CancelledError):
            await waiter
        closer = asyncio.create_task(db.close())
        await asyncio.sleep(0)
        assert not closer.done()
        with pytest.raises(NanaSQLiteClosedError):
            await db.aget("initial")
    finally:
        release.set()
        await task
        await db.close()
    await closer
    with NanaSQLite(str(tmp_path / "close.db")) as persisted:
        assert persisted["accepted"] == 2
        assert "cancelled" not in persisted


@pytest.mark.asyncio
async def test_cancelled_initialization_is_drained_by_close(tmp_path, monkeypatch):
    import nanasqlite.async_core as module

    entered, release = threading.Event(), threading.Event()
    constructed = []
    original = module.NanaSQLite

    def slow_init(*args, **kwargs):
        entered.set()
        assert release.wait(5)
        db = original(*args, **kwargs)
        constructed.append(db)
        return db

    monkeypatch.setattr(module, "NanaSQLite", slow_init)
    db = AsyncNanaSQLite(str(tmp_path / "init.db"), max_pending_operations=1)
    caller = asyncio.create_task(db.aset("not-accepted", 1))
    try:
        assert await asyncio.to_thread(entered.wait, 5)
        caller.cancel()
        with pytest.raises(asyncio.CancelledError):
            await caller
        closer = asyncio.create_task(db.close())
        await asyncio.sleep(0)
        assert not closer.done()
    finally:
        release.set()
        await db.close()
    await closer
    assert len(constructed) == 1 and constructed[0]._is_closed


@pytest.mark.asyncio
async def test_parent_close_rejects_waiting_child_operation(tmp_path):
    db = AsyncNanaSQLite(str(tmp_path / "parent.db"), max_pending_operations=1)
    child = await db.table("child")
    entered, release = threading.Event(), threading.Event()

    def slow():
        entered.set()
        assert release.wait(5)

    active = asyncio.create_task(db._run_in_executor(slow))
    try:
        assert await asyncio.to_thread(entered.wait, 5)
        waiter = asyncio.create_task(child.aset("rejected", 1))
        await asyncio.sleep(0)
        closer = asyncio.create_task(db.close())
        await asyncio.sleep(0)
    finally:
        release.set()
        await active
        await db.close()
    await closer
    with pytest.raises(NanaSQLiteClosedError):
        await waiter


@pytest.mark.asyncio
async def test_cancelled_close_keeps_draining(tmp_path):
    db = AsyncNanaSQLite(str(tmp_path / "cancel-close.db"), max_pending_operations=1)
    await db.aset("k", 1)
    entered, release = threading.Event(), threading.Event()

    def slow():
        entered.set()
        assert release.wait(5)

    active = asyncio.create_task(db._run_in_executor(slow))
    try:
        assert await asyncio.to_thread(entered.wait, 5)
        closer = asyncio.create_task(db.close())
        await asyncio.sleep(0)
        closer.cancel()
        with pytest.raises(asyncio.CancelledError):
            await closer
    finally:
        release.set()
        await active
        await db.close()
    assert db._closed


@pytest.mark.parametrize("options", [
    {"max_pending_operations": True}, {"max_pending_operations": 0},
    {"max_pending_operations": 1, "admission_timeout": float("nan")},
    {"admission_timeout": 1},
])
def test_admission_validation(options):
    with pytest.raises(ValueError):
        AsyncNanaSQLite(":memory:", **options)
