"""Public-API outcomes checked against independently reopened SQLite files."""

import asyncio
import json
import sqlite3
import subprocess
import sys
import threading
from contextlib import closing

import pytest

from nanasqlite import AsyncNanaSQLite, NanaSQLite
from nanasqlite.exceptions import NanaSQLiteClosedError, NanaSQLiteTransactionError
from nanasqlite.hooks import BaseHook


class TransformRead(BaseHook):
    def after_read(self, db, key, value):
        return {"decoded": value}


@pytest.mark.parametrize("strategy,options", [
    ("unbounded", {}), ("lru", {"cache_size": 4}), ("ttl", {"cache_ttl": 60}),
])
def test_batch_read_hook_is_independent_of_cache_state(tmp_path, strategy, options):
    with NanaSQLite(str(tmp_path / "hooks.db"), hooks=[TransformRead()], cache_strategy=strategy, **options) as db:
        db.batch_update({"a": 1, "b": 2})
        expected = {"a": {"decoded": 1}, "b": {"decoded": 2}}
        assert db.batch_get(["a", "b"]) == expected
        db.clear_cache()
        assert db.batch_get(["a", "b"]) == expected
        assert db.batch_get(["a", "b", "absent"]) == expected
        assert db.batch_get(["a", "b", "absent"]) == expected


@pytest.mark.asyncio
async def test_async_batch_read_hook_on_repeated_reads(tmp_path):
    async with AsyncNanaSQLite(str(tmp_path / "async-hooks.db"), hooks=[TransformRead()]) as db:
        await db.aset("a", 1)
        assert await db.abatch_get(["a"]) == {"a": await db.aget("a")}
        assert await db.abatch_get(["a"]) == {"a": await db.aget("a")}


def persisted(path):
    with closing(sqlite3.connect(path)) as conn:
        return {k: json.loads(v) for k, v in conn.execute("SELECT key, value FROM data")}


def test_external_write_lock_recovers_every_failed_row(tmp_path):
    path = str(tmp_path / "locked.db")
    with NanaSQLite(path, v2_mode=True, flush_mode="manual") as db:
        db.pragma("busy_timeout", 1)
        # A separate process is essential: same-process SQLite libraries may
        # share POSIX advisory-lock ownership instead of contending.
        code = "\n".join([
            "import sqlite3, sys",
            "with sqlite3.connect(sys.argv[1]) as connection:",
            " connection.execute('BEGIN IMMEDIATE')",
            " print('locked', flush=True)",
            " sys.stdin.readline()",
            " connection.rollback()",
        ])
        blocker = subprocess.Popen(
            [sys.executable, "-c", code, path], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            assert blocker.stdout.readline().strip() == "locked"
            db.batch_update({"a": 1, "b": 2, "c": 3})
            db.flush(wait=True)
            assert db.get_status()["failed_count"] == 3
        finally:
            try:
                _, error = blocker.communicate("release\n", timeout=5)
            except subprocess.TimeoutExpired:
                blocker.kill()
                blocker.communicate()
                raise
        assert blocker.returncode == 0, error
        db.retry_dlq()
        db.flush(wait=True)
        assert db.get_status()["failed_count"] == 0
    assert persisted(path) == {"a": 1, "b": 2, "c": 3}


@pytest.mark.parametrize("new_operation", ["pending", "committed", "delete"])
def test_dlq_retry_never_overwrites_newer_accepted_values(tmp_path, new_operation):
    path = str(tmp_path / "retry.db")
    with NanaSQLite(path, v2_mode=True, flush_mode="manual") as db:
        db.execute("CREATE TRIGGER reject_old BEFORE INSERT ON data WHEN NEW.value = '1' "
                   "BEGIN SELECT RAISE(ABORT, 'rejected'); END")
        db["k"] = 1
        db.flush(wait=True)
        assert db.get_status()["failed_count"] == 1
        db.execute("DROP TRIGGER reject_old")
        if new_operation == "delete":
            del db["k"]
        else:
            db["k"] = 2
        if new_operation != "pending":
            db.flush(wait=True)
        db.retry_dlq()
        db.flush(wait=True)
    assert persisted(path) == ({} if new_operation == "delete" else {"k": 2})


class BlockingWrite(BaseHook):
    def __init__(self, entered, release):
        super().__init__()
        self.entered, self.release = entered, release

    def before_write(self, db, key, value):
        self.entered.set()
        assert self.release.wait(5), "worker was not released"
        return value


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [None, 2])
async def test_close_drains_public_write_even_if_caller_cancelled(tmp_path, limit):
    path = str(tmp_path / "drain.db")
    entered, release = threading.Event(), threading.Event()
    db = AsyncNanaSQLite(path, max_pending_operations=limit, hooks=[BlockingWrite(entered, release)])
    write = asyncio.create_task(db.aset("accepted", 42))
    closer = None
    try:
        assert await asyncio.to_thread(entered.wait, 5)
        write.cancel()
        with pytest.raises(asyncio.CancelledError):
            await write
        closer = asyncio.create_task(db.close())
        # The write is held by an event, not a guessed write duration.
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(asyncio.shield(closer), 0.05)
    finally:
        release.set()
        await db.close()
        if closer:
            await closer
    assert persisted(path) == {"accepted": 42}


@pytest.mark.asyncio
async def test_failed_close_can_be_recovered_by_rollback(tmp_path):
    db = AsyncNanaSQLite(str(tmp_path / "transaction.db"), max_pending_operations=2)
    await db.begin_transaction()
    try:
        with pytest.raises(NanaSQLiteTransactionError):
            await db.close()
        await db.rollback()
        await db.aset("after", 1)
        await db.close()
    finally:
        # Keep a failing regression from leaving an executor alive.
        if db.sync_db is not None:
            if db.sync_db.in_transaction():
                db.sync_db.rollback()
            db.sync_db.close()
            db._executor.shutdown(wait=True)


def test_auto_cache_observes_a_separate_process(tmp_path):
    path = str(tmp_path / "process.db")
    with NanaSQLite(path, cache_consistency="auto") as db:
        db.batch_update({"change": 1, "delete": 2})
        assert db.get("new") is None
        assert db["change"] == 1
        subprocess.run([sys.executable, "-c", "\n".join([
            "import sqlite3, sys",
            "with sqlite3.connect(sys.argv[1]) as c:",
            " c.execute('UPDATE data SET value = ? WHERE key = ?', ('3', 'change'))",
            " c.execute('DELETE FROM data WHERE key = ?', ('delete',))",
            " c.execute('INSERT INTO data VALUES (?, ?)', ('new', '4'))",
        ]), path], check=True, timeout=15, capture_output=True)
        assert db.batch_get(["change", "delete", "new"]) == {"change": 3, "new": 4}


@pytest.mark.parametrize("count", [0, 1, 7, 8, 9, 25])
def test_stream_checks_values_order_and_page_boundaries(tmp_path, count):
    path = str(tmp_path / "pages.db")
    expected = {f"key'{i:03d}": {"index": i, "text": "日本語"} for i in range(count)}
    with NanaSQLite(path) as db:
        db.batch_update(expected)
    with NanaSQLite(path) as db:
        assert list(db.iter_items(8)) == sorted(expected.items())
        assert db._cache.size == 0
    assert persisted(path) == expected


@pytest.mark.asyncio
async def test_async_iterator_early_close_releases_resources(tmp_path):
    path = str(tmp_path / "early.db")
    async with AsyncNanaSQLite(path, max_pending_operations=1) as db:
        await db.abatch_update({str(i): i for i in range(20)})
        stream = db.aiter_items(3)
        assert await stream.__anext__() == ("0", 0)
        await stream.aclose()
        await asyncio.wait_for(db.aset("after", 42), 5)
    assert persisted(path)["after"] == 42
    with pytest.raises(NanaSQLiteClosedError):
        await db.aget("after")
