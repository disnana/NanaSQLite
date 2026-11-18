from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from contextlib import closing
from threading import Event

import apsw
import pytest

import nanasqlite.core as core
from nanasqlite import (
    AsyncNanaSQLite,
    NanaSQLite,
    NanaSQLiteClosedError,
    NanaSQLiteDatabaseError,
    NanaSQLiteValidationError,
)
from nanasqlite.hooks import BaseHook, UniqueHook


def test_v2_child_close_keeps_shared_engine_running(tmp_path):
    path = str(tmp_path / "child.db")
    with NanaSQLite(path, v2_mode=True, flush_mode="manual") as db:
        with db.table("child") as child:
            grandchild = child.table("grandchild")
            grandchild["before"] = 1
        with pytest.raises(NanaSQLiteClosedError):
            grandchild["after"] = 2
        db["after"] = 3
        db.execute("CREATE TABLE continued (id INTEGER)")
        db.flush(wait=True, check_errors=True)
    with NanaSQLite(path) as db:
        assert db["after"] == 3
        assert db.table("grandchild")["before"] == 1
        assert db.table_exists("continued")


def test_v2_checked_flush_reports_busy_and_can_retry(tmp_path):
    path = str(tmp_path / "busy.db")
    with NanaSQLite(path, v2_mode=True, flush_mode="manual") as db, closing(apsw.Connection(path)) as blocker:
        blocker.execute("BEGIN IMMEDIATE")
        db["key"] = 42
        with pytest.raises(NanaSQLiteDatabaseError, match="unresolved"):
            db.flush(wait=True, check_errors=True)
        assert db.get_status()["failed_count"] == 1
        blocker.execute("ROLLBACK")
        db.retry_dlq()
        db.flush(wait=True, check_errors=True)
    with NanaSQLite(path) as db:
        assert db["key"] == 42


@pytest.mark.asyncio
@pytest.mark.parametrize("read_pool_size", [0, 1])
async def test_async_v2_sql_reads_match_sync_flush_visibility(tmp_path, read_pool_size):
    path = str(tmp_path / "async.db")
    async with AsyncNanaSQLite(path, v2_mode=True, flush_mode="manual", read_pool_size=read_pool_size) as db:
        async with await db.table("child") as child:
            await child.aset("before", 1)
        await db.aset("first", {"status": "ready"})
        assert await db.query(columns=["key"]) == [{"key": "first"}]
        await db.aset("second", {"status": "ready"})
        assert await db.fetch_one("SELECT key FROM data WHERE key = ?", ("second",)) == ("second",)
        await db.aset("third", {"status": "ready"})
        assert await db.fetch_all("SELECT key FROM data WHERE key = ?", ("third",)) == [("third",)]
        await db.create_json_index("$.status")
        await db.aset("fourth", {"status": "ready"})
        assert await db.find_by("$.status", "ready") == ["first", "second", "third"]
        await db.aflush(wait=True, check_errors=True)
        assert await db.find_by("$.status", "ready") == ["first", "fourth", "second", "third"]


def test_json_path_preserves_types_and_flushes_without_holding_lock(tmp_path):
    with NanaSQLite(str(tmp_path / "types.db"), v2_mode=True, flush_mode="manual", lock_timeout=0.5) as db:
        db["key"] = {"s": "123", "t": True, "f": False, "a": [1], "obj": {"x": "null"}, "n": None}
        for field, expected in db["key"].items():
            actual = db.get_by_path("key", field)
            assert actual == expected
            assert type(actual) is type(expected)
        assert db.get_by_path("missing", "s") is None


def test_json_index_uses_existing_rows_and_tracks_writes(tmp_path):
    path = str(tmp_path / "search.db")
    field = "$.owner's"
    with NanaSQLite(path) as db:
        db.batch_update({"a": {"owner's": "ok"}, "b": {"owner's": "ok"}, "c": {}, "d": {"owner's": None}})
        idx = db.create_json_index(field)
        assert db.create_json_index(field) == idx
        assert db.find_by(field, "ok", limit=1) == ["a"]
        assert db.find_by(field, None) == ["c", "d"]
        plan = db.fetch_all(
            "EXPLAIN QUERY PLAN SELECT key FROM data WHERE json_extract(value, '$.owner''s') IS ? ORDER BY key LIMIT ?",
            ("ok", 1),
        )
        assert any(idx in row[3] for row in plan)
        db["array"] = {"owner's": [1]}
        assert db.find_by(field, "[1]") == []
        db["a"] = {"owner's": "updated"}
        db.batch_delete(["b"])
    with NanaSQLite(path) as db:
        assert db.find_by(field, "ok") == []
        assert db.find_by(field, "updated") == ["a"]


@pytest.mark.parametrize("index_options", [None, {}, {"include_type": True}, {"include_type": True, "order_by_key": False}])
def test_find_by_distinguishes_json_scalars(tmp_path, index_options):
    with NanaSQLite(str(tmp_path / "scalars.db")) as db:
        db.batch_update({
            "bool-false": False, "bool-true": True, "zero": 0, "one": 1, "real-one": 1.0,
            "null": None, "str-zero": "0", "array": [1], "str-array": "[1]",
            "object": {"x": 2}, "str-object": '{"x":2}', "text": "active",
        })
        if index_options is not None:
            db.create_json_index("$", **index_options)
        for value, keys in [
            (False, ["bool-false"]), (True, ["bool-true"]), (0, ["zero"]), (1, ["one", "real-one"]),
            (1.0, ["one", "real-one"]), (None, ["null"]), ("0", ["str-zero"]), ("[1]", ["str-array"]),
            ('{"x":2}', ["str-object"]), ("active", ["text"]),
        ]:
            assert db.find_by("$", value) == keys
        for value in (float("nan"), float("inf"), -float("inf")):
            with pytest.raises(NanaSQLiteValidationError, match="finite"):
                db.find_by("$", value)


async def test_async_type_covering_index_and_bounded_mapping(tmp_path):
    path = str(tmp_path / "async-index.db")
    async with AsyncNanaSQLite(path, cache_strategy="lru", cache_size=1) as db:
        await db.abatch_update({"bool": {"flag": True}, "one": {"flag": 1}, "zero": {"flag": 0}})
        index = await db.create_json_index("$.flag", include_type=True)
        assert await db.find_by("$.flag", True) == ["bool"]
        assert len(await db.to_dict()) == len(await db.aitems()) == len(await db.avalues()) == 3
    with NanaSQLite(path) as db:
        plan = db.fetch_all(
            "EXPLAIN QUERY PLAN SELECT key FROM data WHERE json_extract(value,'$.flag') IS ? "
            "AND json_type(value,'$.flag') = 'true' ORDER BY key LIMIT ?", (True, 20),
        )
        assert any(index in row[-1] for row in plan)
        assert not any("TEMP B-TREE" in row[-1] for row in plan)


@pytest.mark.parametrize("path", ["$.", "$.items[", "$.items[3].", '$."open', "$.items[#-]"])
def test_invalid_path_never_installs_an_index(tmp_path, path):
    with NanaSQLite(str(tmp_path / "paths.db")) as db:
        with pytest.raises(NanaSQLiteValidationError):
            db.create_json_index(path)
        with pytest.raises(NanaSQLiteValidationError):
            db.find_by(path, None)
        assert not db.fetch_all("SELECT name FROM sqlite_schema WHERE name GLOB 'nanasqlite_json_*'")
        db["sample"] = {"items": [0, 1, 2, 3]}
        assert db["sample"]["items"][-1] == 3


@pytest.mark.parametrize(("path", "wanted"), [
    ('$."a.b"[0].name', "first"), ('$."a.b"[#-1].name', "last"), ('$."a.b"[#]', None),
    ('$.""', "empty"), ("$.所有者's", "owner"), ("$." + "a" * 300, "long"),
])
def test_valid_sqlite_paths_keep_working(tmp_path, path, wanted):
    with NanaSQLite(str(tmp_path / "valid.db")) as db:
        db.create_json_index(path)
        db["sample"] = {"a.b": [{"name": "first"}, {"name": "last"}], "": "empty", "所有者's": "owner", "a" * 300: "long"}
        assert db.find_by(path, wanted) == ["sample"]
        assert db.get_by_path("sample", path) == wanted


def test_strict_clause_limit_precedes_scanning(tmp_path, monkeypatch):
    def unexpected_scan(_):
        pytest.fail("the strict length check must run before scanning the expression")

    with NanaSQLite(str(tmp_path / "length.db"), max_clause_length=8) as db:
        monkeypatch.setattr(core, "fast_validate_sql_chars", unexpected_scan)
        with pytest.raises(NanaSQLiteValidationError, match="maximum length"):
            db.query(where="key = key")


@pytest.mark.parametrize("strategy", ["unbounded", "lru", "ttl"])
@pytest.mark.parametrize("v2", [False, True])
def test_complete_mapping_with_evicting_cache(tmp_path, strategy, v2):
    path = str(tmp_path / "bounded.db")
    with NanaSQLite(path, cache_strategy=strategy, cache_size=2, cache_ttl=100,
                    v2_mode=v2, flush_mode="manual") as db:
        expected = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
        db.batch_update(expected)
        assert db._cache.size <= 2
        assert dict(db.items()) == expected
        assert db.batch_update_partial({"b": 7, "f": 6}) == {}
        expected.update({"b": 7, "f": 6})
        del db["d"]
        del expected["d"]
        assert sorted(db.values()) == sorted(expected.values())
        assert db.to_dict() == expected
        assert db.get("missing") is None
        assert db.copy() == expected
        assert db._cache.size <= 2
    with NanaSQLite(path) as reopened:
        assert reopened.to_dict() == expected


def test_bounded_snapshot_includes_in_flight_and_newer_staging(tmp_path, monkeypatch):
    with NanaSQLite(str(tmp_path / "flush.db"), cache_strategy="lru", cache_size=1,
                    v2_mode=True, flush_mode="manual") as db, db.table("child") as child:
        assert db.to_dict() == {}
        entered, resume = Event(), Event()
        process = db._v2_engine._process_kvs_chunk

        def pause(chunk):
            entered.set()
            assert resume.wait(3)
            process(chunk)

        monkeypatch.setattr(db._v2_engine, "_process_kvs_chunk", pause)
        db.batch_update({"change": 1, "retain": 2, "delete": 3})
        child["other"] = 4
        db.flush()
        try:
            assert entered.wait(3)
            db["change"] = 5
            del db["delete"]
            assert db.to_dict() == {"change": 5, "retain": 2}
        finally:
            resume.set()
        db.flush(wait=True, check_errors=True)
        assert child.to_dict() == {"other": 4}


def test_v2_repeated_table_validation_and_mixed_chunk(tmp_path):
    with NanaSQLite(str(tmp_path / "tables.db"), v2_mode=True, flush_mode="manual") as db:
        with db.table("short_name") as short, db.table("table_" + "x" * 150) as long_table:
            for table in (short, long_table, short):
                table["record"] = table._table
            for invalid in ("two names", "short_name\n"):
                with pytest.raises(ValueError, match="table name"):
                    db._v2_engine.kvs_set(invalid, "record", 1)
            db.flush(wait=True, check_errors=True)
            assert short.get_fresh("record") == short._table
            assert long_table.get_fresh("record") == long_table._table


@pytest.mark.parametrize("use_index", [False, True])
def test_unique_hook_checks_rows_outside_cache(tmp_path, use_index):
    path = str(tmp_path / "bounded-unique.db")
    with NanaSQLite(path) as db:
        db.batch_update({str(i): {"name": f"name-{i}"} for i in range(5)})
    with NanaSQLite(path, cache_strategy="lru", cache_size=2, hooks=[UniqueHook("name", use_index=use_index)]) as db:
        with pytest.raises(NanaSQLiteValidationError, match="duplicate"):
            db["new"] = {"name": "name-0"}
        assert "new" not in db


def test_negative_cache_is_bounded(tmp_path):
    for memory_first in (False, True):
        with NanaSQLite(str(tmp_path / f"{memory_first}.db"), memory_first=memory_first) as db:
            keys = [f"missing-{i}" for i in range(5000)]
            assert db.batch_get(keys) == {}
            for key in keys:
                assert db.get(key) is None
            assert len(db._absent_keys) <= (0 if memory_first else 4096)
            db[keys[0]] = 7
            assert db.get(keys[0]) == 7


def test_db_read_does_not_overwrite_newer_cached_write(tmp_path, monkeypatch):
    with NanaSQLite(str(tmp_path / "read-race.db")) as db, ThreadPoolExecutor(1) as worker:
        db["key"] = "old"
        db.clear_cache()
        original_read = db._read_from_db
        fetched = Event()
        resume = Event()

        def pause_after_read(key, **kwargs):
            result = original_read(key, **kwargs)
            fetched.set()
            assert resume.wait(3)
            return result

        monkeypatch.setattr(db, "_read_from_db", pause_after_read)
        in_flight = worker.submit(db.get, "key")
        try:
            assert fetched.wait(3)
            db["key"] = "new"
        finally:
            resume.set()
        assert in_flight.result(timeout=3) in ("old", "new")
        assert db.get("key") == "new"


@pytest.mark.asyncio
async def test_async_v2_idle_query_does_not_submit_flush(tmp_path, monkeypatch):
    path = str(tmp_path / "idle.db")
    with NanaSQLite(path) as db:
        db["key"] = 42
    async with AsyncNanaSQLite(path, v2_mode=True, flush_mode="manual") as db:
        def unexpected_submission(*args, **kwargs):
            pytest.fail("idle SQL read submitted a v2 flush")

        monkeypatch.setattr(db.sync_db._v2_engine._worker, "submit", unexpected_submission)
        assert await db.query(columns=["key"]) == [{"key": "key"}]


def test_idle_skip_waits_for_in_flight_chunk(tmp_path, monkeypatch):
    with NanaSQLite(str(tmp_path / "active.db"), v2_mode=True, flush_mode="manual") as db:
        engine = db._v2_engine
        entered = Event()
        release = Event()
        original = engine._process_kvs_chunk

        def pause_chunk(chunk):
            entered.set()
            assert release.wait(3)
            original(chunk)

        monkeypatch.setattr(engine, "_process_kvs_chunk", pause_chunk)
        db["key"] = 42
        db.flush()
        try:
            assert entered.wait(3)
            # The worker has removed the chunk from staging without committing.
            assert db.get_status()["pending_kvs_count"] == 0
            with ThreadPoolExecutor(1) as executor:
                reader = executor.submit(engine.flush, wait=True, skip_if_idle=True)
                try:
                    with pytest.raises(FutureTimeoutError):
                        reader.result(timeout=0.05)
                finally:
                    release.set()
                reader.result(timeout=3)
        finally:
            release.set()
        assert db.fetch_one("SELECT value FROM data WHERE key = ?", ("key",)) == ("42",)


@pytest.mark.parametrize("operation", ["set", "update", "partial", "delete", "pop", "batch_delete"])
@pytest.mark.parametrize("cache_strategy", ["unbounded", "lru", "ttl", "persistent_ttl"])
def test_v2_delayed_success_hook_does_not_overwrite_newer_cached_value(tmp_path, operation, cache_strategy):
    entered = Event()
    release = Event()

    class DelayedSuccessHook(BaseHook):
        def on_write_success(self, db, key, value, old_value):
            if value == 1:
                # User hooks can wait for SQLite without retaining the staging lock.
                db.flush(wait=True, check_errors=True)
                entered.set()
                assert release.wait(3)

        def on_delete_success(self, db, key, old_value):
            db.flush(wait=True, check_errors=True)
            entered.set()
            assert release.wait(3)

    path = str(tmp_path / "v2-cache.db")
    with NanaSQLite(
        path,
        v2_mode=True,
        flush_mode="manual",
        cache_strategy="ttl" if cache_strategy == "persistent_ttl" else cache_strategy,
        cache_size=32,
        cache_ttl=60.0,
        cache_persistence_ttl=cache_strategy == "persistent_ttl",
    ) as db:
        db["key"] = 0
        db.add_hook(DelayedSuccessHook())
        operations = {
            "set": lambda: db.__setitem__("key", 1),
            "update": lambda: db.batch_update({"key": 1}),
            "partial": lambda: db.batch_update_partial({"key": 1}),
            "delete": lambda: db.__delitem__("key"),
            "pop": lambda: db.pop("key"),
            "batch_delete": lambda: db.batch_delete(["key"]),
        }

        with ThreadPoolExecutor(1) as executor:
            earlier = executor.submit(operations[operation])
            try:
                assert entered.wait(3)
                db["key"] = 2
                assert db["key"] == 2
            finally:
                release.set()
            earlier.result(timeout=3)

        db.flush(wait=True, check_errors=True)
        assert db["key"] == 2
    with NanaSQLite(path) as reopened:
        assert reopened["key"] == 2


@pytest.mark.parametrize("source,reader", [
    ("sqlite", "get"), ("sqlite", "get_fresh"), ("sqlite", "batch_get"),
    ("staging", "get"), ("staging", "batch_get"),
])
def test_v2_in_flight_read_does_not_overwrite_newer_write(tmp_path, monkeypatch, source, reader):
    path = str(tmp_path / "v2-read.db")
    with NanaSQLite(path, v2_mode=True, flush_mode="manual") as db, ThreadPoolExecutor(1) as executor:
        db["key"] = 1
        if source == "sqlite":
            db.flush(wait=True, check_errors=True)
        db.clear_cache()
        original = db._deserialize
        read = Event()
        release = Event()

        def delayed_deserialize(raw):
            value = original(raw)
            if value == 1:
                read.set()
                assert release.wait(3)
            return value

        monkeypatch.setattr(db, "_deserialize", delayed_deserialize)
        key_arg = ["key"] if reader == "batch_get" else "key"
        pending = executor.submit(getattr(db, reader), key_arg)
        try:
            assert read.wait(3)
            db["key"] = 2
        finally:
            release.set()
        pending.result(timeout=3)
        db.flush(wait=True, check_errors=True)
        assert db["key"] == 2

    with NanaSQLite(path) as reopened:
        assert reopened["key"] == 2


@pytest.mark.parametrize("earlier", ["write", "delete"])
def test_unique_v2_index_reconciles_out_of_order_callbacks(tmp_path, earlier):
    entered, release = Event(), Event()

    class Delay(BaseHook):
        def on_write_success(self, db, key, value, old_value):
            if value["email"] == "intermediate":
                entered.set()
                assert release.wait(3)

        def on_delete_success(self, db, key, old_value):
            entered.set()
            assert release.wait(3)

    path = str(tmp_path / "unique.db")
    hook = UniqueHook("email", use_index=True)
    with NanaSQLite(path, v2_mode=True, flush_mode="manual", hooks=[Delay(), hook]) as db:
        db["a"] = {"email": "initial"}
        with ThreadPoolExecutor(1) as executor:
            pending = (
                executor.submit(db.__setitem__, "a", {"email": "intermediate"})
                if earlier == "write"
                else executor.submit(db.__delitem__, "a")
            )
            try:
                assert entered.wait(3)
                db["a"] = {"email": "current"}
            finally:
                release.set()
            pending.result(timeout=3)
        db["b"] = {"email": "intermediate"}
        db["c"] = {"email": "initial"}
        with pytest.raises(NanaSQLiteValidationError, match="duplicate value"):
            db["d"] = {"email": "current"}
        db.flush(wait=True, check_errors=True)
    with NanaSQLite(path) as db:
        assert db["a"] == {"email": "current"}
        assert db["b"] == {"email": "intermediate"}
        assert db["c"] == {"email": "initial"}


def test_unique_v2_index_tracks_atomic_patch(tmp_path):
    hook = UniqueHook("email", use_index=True)
    with NanaSQLite(str(tmp_path / "patch.db"), v2_mode=True, flush_mode="manual", hooks=[hook]) as db:
        db["a"] = {"email": "old"}
        db.patch("a", {"email": "new"})
        db["b"] = {"email": "old"}
        with pytest.raises(NanaSQLiteValidationError, match="duplicate value"):
            db["c"] = {"email": "new"}
