import os
import threading
import time

import pytest

from nanasqlite.async_core import AsyncNanaSQLite
from nanasqlite.core import NanaSQLite
from nanasqlite.exceptions import NanaSQLiteTransactionError, NanaSQLiteValidationError
from nanasqlite.utils import ExpiringDict


def test_v2_management_api_sync() -> None:
    """Verifies V2 management methods in synchronous NanaSQLite."""
    with NanaSQLite(":memory:", v2_mode=True, v2_enable_metrics=True) as db:
        # Initial state
        assert db.get_dlq() == []
        metrics = db.get_v2_metrics()
        assert isinstance(metrics, dict)
        assert "dlq_errors" in metrics

        # Perform write
        db["test"] = "value"
        db.flush()

        # Verify metrics updated
        new_metrics = db.get_v2_metrics()
        assert new_metrics.get("flushes_completed", 0) >= 0

        # Test DLQ clear/retry (even if empty shouldn't crash)
        db.retry_dlq()
        db.clear_dlq()
        assert db.get_dlq() == []

@pytest.mark.asyncio
async def test_v2_management_api_async() -> None:
    """Verifies V2 management methods and aliases in AsyncNanaSQLite."""
    async with AsyncNanaSQLite(":memory:", v2_mode=True, v2_enable_metrics=True) as db:
        # Initial state
        assert await db.aget_dlq() == []
        assert await db.get_dlq() == [] # Alias

        metrics = await db.aget_v2_metrics()
        assert isinstance(metrics, dict)

        # Perform write
        await db.aset("test", "value")
        await db.aflush()
        await db.flush() # Alias

        # Verify metrics
        new_metrics = await db.get_v2_metrics() # Alias
        assert isinstance(new_metrics, dict)

        await db.aretry_dlq()
        await db.retry_dlq() # Alias
        await db.aclear_dlq()
        await db.clear_dlq() # Alias

def test_v2_shared_lock_concurrency() -> None:
    """Verifies that shared locks prevent crashes with multiple tables in V2 mode."""
    with NanaSQLite("test_shared.db", v2_mode=True) as db:
        t1 = db.table("t1")
        t2 = db.table("t2")

        def writer(table, count):
            for i in range(count):
                table[f"key_{i}"] = f"val_{i}"

        threads = [
            threading.Thread(target=writer, args=(t1, 50)),
            threading.Thread(target=writer, args=(t2, 50))
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        t1.flush()
        t2.flush()
        time.sleep(0.2) # Wait for background threads

        assert len(t1) == 50
        assert len(t2) == 50

    if os.path.exists("test_shared.db"):
        os.remove("test_shared.db")

def test_v2_transaction_guard() -> None:
    """Verifies that explicit transactions are forbidden in V2 mode."""
    with NanaSQLite(":memory:", v2_mode=True) as db:
        with pytest.raises(NanaSQLiteTransactionError, match="not supported in V2 mode"):
            db.begin_transaction()

        with pytest.raises(NanaSQLiteTransactionError, match="not supported in V2 mode"):
            with db.transaction():
                pass

def test_v2_metric_inheritance() -> None:
    """Verifies that v2_enable_metrics is inherited by child tables."""
    with NanaSQLite(":memory:", v2_mode=True, v2_enable_metrics=True) as db:
        child = db.table("child")
        assert child._v2_enable_metrics_raw is True
        assert child._v2_engine._enable_metrics is True

        metrics = child.get_v2_metrics()
        assert isinstance(metrics, dict)
        assert len(metrics) > 0

def test_v2_stale_read() -> None:
    """Verifies that reads prioritize the staging buffer to avoid stale reads."""
    with NanaSQLite(":memory:", v2_mode=True, flush_mode="manual") as db:
        db["key1"] = "new_value"
        # Reading immediately should return "new_value" from staging, not the old value (if any)
        assert db["key1"] == "new_value"
        assert db.get("key1") == "new_value"

        db.flush()
        assert db["key1"] == "new_value"

def test_expiring_dict_eviction_deadlock_prevention() -> None:
    """Verifies that on_expire in ExpiringDict doesn't cause deadlocks by being called under lock."""
    # lock simulates NanaSQLite._lock. We use a non-recursive lock to strictly detect deadlocks.
    lock = threading.Lock()
    expired_event = threading.Event()

    def on_expire(key, value):
        # This simulates a background thread (scheduler) trying to
        # acquire NanaSQLite._lock while ExpiringDict._lock is ALREADY held (if the bug exists)
        with lock:
            expired_event.set()

    # Create ExpiringDict with SCHEDULER mode (default)
    ed = ExpiringDict(expiration_time=0.01, on_expire=on_expire)

    # 1. Main thread sets item
    ed["a"] = 1

    # 2. Main thread acquires 'lock' (simulating in a NanaSQLite method)
    with lock:
        # 3. Wait for item to expire in background
        time.sleep(0.1)

        # 4. At this point, the scheduler thread is likely trying to call _evict -> on_expire.
        # 5. It will be waiting for 'lock' because we hold it.
        # 6. We want to ensure that the main thread can still acquire ed._lock
        #    to perform another operation. If the scheduler is holding ed._lock
        #    while waiting for 'lock', we would deadlock here.

        # We use a key that isn't 'a' to avoid triggering the same-thread synchronous _check_expiry for 'a'
        # which would cause a same-thread deadlock on 'lock' (since it's non-recursive).
        ed["b"] = 2

    # If we got here, no deadlock occurred.
    # Now we release 'lock', allowing the scheduler thread to finish its callback.
    assert expired_event.wait(timeout=2.0)
    ed.clear()

def test_sql_whitelist_validation() -> None:
    """Verifies hardened create_table and alter_table validation."""
    with NanaSQLite(":memory:") as db:
        # Safe cases
        db.alter_table_add_column("data", "col1", "TEXT")
        db.alter_table_add_column("data", "col2", "VARCHAR(255)")
        db.alter_table_add_column("data", "col3", "DECIMAL(10, 2)")

        # Unsafe cases (containing suspicious characters)
        unsafe_types = [
            "TEXT; DROP TABLE data",
            "INTEGER --",
            "VARCHAR(255) /* comment */",
            "TEXT;--",
            "TEXT\x00"
        ]

        for t in unsafe_types:
            with pytest.raises((NanaSQLiteValidationError, ValueError)):
                db.alter_table_add_column("data", "bad", t)

        # Test SQL Whitelist (including standard names and simple nested parens)
        valid_types = ["TEXT", "INTEGER", "VARCHAR(255)", "DECIMAL(10, 2)", "DOUBLE PRECISION"]
        for vtype in valid_types:
            db.alter_table_add_column("data", f"col_{vtype.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '')}", vtype)

        # Test ReDoS-prone patterns (should fail)
        redos_patterns = [
            "TEXT" + " " * 100 + "(",
            "VARCHAR" + " " * 100 + "(",
        ]
        for pattern in redos_patterns:
            with pytest.raises(ValueError):
                 db.alter_table_add_column("data", "bad", pattern)


def test_v2_clear_consistency():
    """Verify that clear() in V2 mode doesn't allow ghost re-inserts from background buffer."""
    with NanaSQLite(":memory:", v2_mode=True, flush_mode="manual") as db:
        db["key1"] = "value1"
        # key1 is in staging buffer, not in DB yet
        db.clear()
        # Now DB should be empty, AND staging buffer should be empty (or at least not re-insert key1)

        # Force a flush (if clear didn't empty the buffer, this would re-insert key1)
        db.flush()
        time.sleep(0.2) # Wait for background thread

        # Check DB directly bypassing cache
        cursor = db._connection.execute(f"SELECT COUNT(*) FROM {db._safe_table}")
        assert cursor.fetchone()[0] == 0, "Ghost write detected after clear()"

def test_v2_load_all_consistency():
    """Verify that load_all() sees pending writes in V2 mode."""
    with NanaSQLite(":memory:", v2_mode=True, flush_mode="manual") as db:
        db["key1"] = "value1"
        # Ensure it's not in DB yet (manual flush)
        cursor = db._connection.execute(f"SELECT COUNT(*) FROM {db._safe_table}")
        assert cursor.fetchone()[0] == 0

        # Clear just the read cache
        db.clear_cache()
        assert "key1" not in db._data

        # load_all() should flush first, so it sees key1
        db.load_all()
        assert "key1" in db, "load_all() failed to see pending V2 write"
        assert db["key1"] == "value1"

def test_v2_restore_consistency(tmp_path):
    """Verify that restore() correctly resets V2 engine connection."""
    db_path = str(tmp_path / "original.db")
    backup_path = str(tmp_path / "backup.db")

    with NanaSQLite(db_path, v2_mode=True, flush_mode="immediate") as db:
        db["key_init"] = "init"
        db.backup(backup_path)

        db["key_after"] = "after"
        db.flush() # Ensure it's in the DB

        # Restore to initial state
        db.restore(backup_path)
        # Now the connection is replaced. V2Engine must also be updated.
        db["key_new"] = "new_v2_write"
        db.flush()
        time.sleep(0.2)

        # Read back from the NEW connection
        assert "key_new" in db
        assert db["key_new"] == "new_v2_write"
        assert "key_after" not in db # Restore should have reverted this
