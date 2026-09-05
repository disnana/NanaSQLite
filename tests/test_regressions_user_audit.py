"""Regression tests for issues found during the ordinary-use audit."""

from __future__ import annotations

import asyncio
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from nanasqlite import NanaSQLite, V2Config
from nanasqlite.exceptions import NanaSQLiteDatabaseError, NanaSQLiteValidationError
from nanasqlite.hooks import UniqueHook
from nanasqlite.utils import ExpirationMode, ExpiringDict


def test_v2_pending_writes_are_visible_to_dict_and_cte_reads(tmp_path):
    db = NanaSQLite(str(tmp_path / "v2.db"), v2_mode=True, flush_mode="manual")
    try:
        db["k"] = "v"

        assert len(db) == 1
        assert db.keys() == ["k"]
        assert db.get_fresh("k") == "v"
        assert db.fetch_all("/* leading comment */ WITH q AS (SELECT 1 AS x) SELECT x FROM q") == [(1,)]
    finally:
        db.close()


def test_v2_cte_write_is_not_misclassified_as_a_read(tmp_path):
    db = NanaSQLite(str(tmp_path / "cte.db"), v2_mode=True, flush_mode="manual")
    try:
        db.create_table("items", {"id": "INTEGER PRIMARY KEY", "value": "INTEGER"})
        db.execute("INSERT INTO items (id, value) VALUES (?, ?)", (1, 1))
        db.execute(
            "-- write through the strict lane\n"
            "WITH target AS (SELECT 1 AS id) "
            "UPDATE items SET value = 2 WHERE id IN (SELECT id FROM target)"
        )

        assert db.fetch_all("WITH target AS (SELECT 1 AS id) SELECT value FROM items WHERE id IN (SELECT id FROM target)") == [
            (2,)
        ]
    finally:
        db.close()


def test_unique_hook_batch_lifecycle_stays_in_sync(tmp_path):
    hook = UniqueHook("email", use_index=True)
    db = NanaSQLite(str(tmp_path / "unique.db"), hooks=[hook])
    try:
        db.batch_update({"a": {"email": "a@example.test"}})
        with pytest.raises(NanaSQLiteValidationError, match="Unique constraint"):
            db["b"] = {"email": "a@example.test"}

        db.batch_update({"a": {"email": "b@example.test"}})
        db["c"] = {"email": "a@example.test"}

        failed = db.batch_update_partial({"c": {"email": "c@example.test"}})
        assert failed == {}
        db["d"] = {"email": "a@example.test"}

        db.batch_delete(["c"])
        db["e"] = {"email": "c@example.test"}

        with pytest.raises(NanaSQLiteValidationError, match="Unique constraint"):
            db.batch_update({"x": {"email": "same@example.test"}, "y": {"email": "same@example.test"}})
    finally:
        db.close()


def test_alter_table_default_rejects_arbitrary_objects(tmp_path):
    class DangerousDefault:
        def __str__(self) -> str:
            return '0; DROP TABLE "data"; --'

    db = NanaSQLite(str(tmp_path / "sql-boundary.db"))
    try:
        with pytest.raises(NanaSQLiteValidationError, match="arbitrary"):
            db.alter_table_add_column("data", "extra", "TEXT", default=DangerousDefault())
        assert db.table_exists("data")

        with pytest.raises(NanaSQLiteValidationError, match="Column type"):
            db.create_table("unsafe_types", {"value": DangerousDefault()})
    finally:
        db.close()


def test_v2_configuration_rejects_non_positive_scheduling_values(tmp_path):
    with pytest.raises(ValueError, match="flush_interval"):
        V2Config(flush_interval=0)
    with pytest.raises(ValueError, match="flush_count"):
        V2Config(flush_count=0)
    with pytest.raises(ValueError, match="chunk_size"):
        V2Config(chunk_size=-1)

    with pytest.raises(ValueError, match="chunk_size"):
        NanaSQLite(str(tmp_path / "invalid-v2.db"), v2_mode=True, v2_chunk_size=0)


def test_ttl_database_close_stops_scheduler(tmp_path):
    db = NanaSQLite(str(tmp_path / "ttl.db"), cache_strategy="ttl", cache_ttl=60.0)
    scheduler = db._cache._data._scheduler_thread
    assert scheduler is not None and scheduler.is_alive()

    db.close()

    assert not scheduler.is_alive()


def test_expiring_none_value_still_calls_expiration_callback():
    expired: list[tuple[str, object]] = []
    cache = ExpiringDict(0.01, mode=ExpirationMode.LAZY, on_expire=lambda key, value: expired.append((key, value)))
    cache["none"] = None
    time.sleep(0.02)

    with pytest.raises(KeyError):
        _ = cache["none"]
    assert expired == [("none", None)]
    cache.close()


@pytest.mark.asyncio
async def test_expiring_close_cancels_event_loop_timer():
    cache = ExpiringDict(60.0, mode=ExpirationMode.TIMER)
    cache["key"] = "value"
    handle = cache._async_tasks["key"]

    cache.close()
    await asyncio.sleep(0)

    assert handle.cancelled()


def test_aead_rejects_plaintext_by_default(tmp_path):
    path = tmp_path / "plaintext.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE data (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute("INSERT INTO data (key, value) VALUES (?, ?)", ("legacy", '"value"'))
    conn.commit()
    conn.close()

    key = AESGCM.generate_key(bit_length=256)
    db = NanaSQLite(str(path), encryption_key=key)
    try:
        with pytest.raises(NanaSQLiteDatabaseError, match="legacy plaintext"):
            _ = db["legacy"]
    finally:
        db.close()


def test_empty_encryption_key_is_rejected(tmp_path):
    with pytest.raises(NanaSQLiteValidationError, match="non-empty"):
        NanaSQLite(str(tmp_path / "empty-key.db"), encryption_key=b"")


def test_connection_local_insert_result_is_captured_atomically(tmp_path):
    db = NanaSQLite(str(tmp_path / "rowid.db"))
    db.create_table("items", {"value": "INTEGER"})
    real_connection = db._connection

    class SlowConnectionProxy:
        def __init__(self, connection):
            self._connection = connection

        def __getattr__(self, name):
            return getattr(self._connection, name)

        def last_insert_rowid(self):
            # Make the old execute-then-read sequence reliably overlap.
            time.sleep(0.002)
            return self._connection.last_insert_rowid()

    db._connection = SlowConnectionProxy(real_connection)
    try:
        with ThreadPoolExecutor(max_workers=16) as executor:
            rowids = list(executor.map(lambda value: db.sql_insert("items", {"value": value}), range(32)))
    finally:
        db.close()

    assert sorted(rowids) == list(range(1, 33))
