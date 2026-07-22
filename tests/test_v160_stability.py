import threading

import pytest

from nanasqlite import (
    AsyncNanaSQLite,
    NanaSQLite,
    NanaSQLiteDatabaseError,
    NanaSQLiteValidationError,
    UniqueHook,
)


def test_increment_scalar_and_missing_default(tmp_path):
    with NanaSQLite(str(tmp_path / "increment.db")) as db:
        db["count"] = 2
        assert db.increment("count", 3) == 5
        assert db["count"] == 5
        assert db.increment("new", 2, default=10) == 12
        with pytest.raises(KeyError):
            db.increment("missing")


def test_increment_dict_field_and_validation(tmp_path):
    with NanaSQLite(str(tmp_path / "increment-field.db")) as db:
        db["user"] = {"name": "Nana", "score": 4}
        assert db.increment("user", 2, field="score") == {"name": "Nana", "score": 6}
        assert db.increment("user", field="visits", default=0)["visits"] == 1
        with pytest.raises(KeyError):
            db.increment("user", field="missing")
        with pytest.raises(NanaSQLiteValidationError):
            db.increment("user", True, field="score")
        with pytest.raises(NanaSQLiteValidationError):
            db.increment("user", float("inf"), field="score")


def test_patch_shallow_merge_and_create(tmp_path):
    with NanaSQLite(str(tmp_path / "patch.db")) as db:
        db["user"] = {"name": "Nana", "nested": {"a": 1}}
        assert db.patch("user", {"active": True, "nested": {"b": 2}}) == {
            "name": "Nana",
            "active": True,
            "nested": {"b": 2},
        }
        assert db.patch("created", {"ok": True}, create=True) == {"ok": True}
        with pytest.raises(KeyError):
            db.patch("missing", {})
        db["scalar"] = 1
        with pytest.raises(NanaSQLiteValidationError):
            db.patch("scalar", {"x": 1})


def test_increment_is_atomic_across_connections(tmp_path):
    path = str(tmp_path / "concurrent.db")
    first = NanaSQLite(path)
    second = NanaSQLite(path)
    first["count"] = 0
    errors: list[Exception] = []

    def run(db):
        try:
            for _ in range(50):
                db.increment("count")
        except Exception as exc:  # pragma: no cover - asserted below
            errors.append(exc)

    threads = [threading.Thread(target=run, args=(first,)), threading.Thread(target=run, args=(second,))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    first.refresh("count")
    assert errors == []
    assert first["count"] == 100
    first.close()
    second.close()


def test_atomic_operations_work_with_v2_and_memory_first(tmp_path):
    for name, kwargs in (
        ("v2", {"v2_mode": True, "flush_mode": "manual"}),
        ("memory", {"memory_first": True}),
    ):
        path = str(tmp_path / f"{name}.db")
        with NanaSQLite(path, **kwargs) as db:
            db["item"] = {"count": 1}
            assert db.increment("item", field="count") == {"count": 2}
            assert db.patch("item", {"ready": True}) == {"count": 2, "ready": True}
        with NanaSQLite(path) as reopened:
            assert reopened["item"] == {"count": 2, "ready": True}


@pytest.mark.asyncio
async def test_async_increment_patch_and_backup(tmp_path):
    source = str(tmp_path / "async.db")
    backup = str(tmp_path / "async-backup.db")
    async with AsyncNanaSQLite(source, v2_mode=True, flush_mode="manual") as db:
        await db.aset("item", {"count": 1})
        assert await db.increment("item", field="count") == {"count": 2}
        assert await db.patch("item", {"active": True}) == {"count": 2, "active": True}
        await db.abackup(backup)
    with NanaSQLite(backup) as copied:
        assert copied["item"] == {"count": 2, "active": True}


def test_backup_flushes_verifies_and_replaces_atomically(tmp_path):
    source = str(tmp_path / "source.db")
    destination = tmp_path / "backup.db"
    destination.write_bytes(b"existing backup must survive failures")
    with NanaSQLite(source, v2_mode=True, flush_mode="manual") as db:
        db["pending"] = {"saved": True}
        db.backup(str(destination))
    with NanaSQLite(str(destination)) as copied:
        assert copied["pending"] == {"saved": True}


def test_backup_failure_preserves_existing_destination(tmp_path, monkeypatch):
    source = str(tmp_path / "source-failure.db")
    destination = tmp_path / "existing.db"
    original = b"existing destination"
    destination.write_bytes(original)
    with NanaSQLite(source) as db:
        db["value"] = 1

        def fail_verification(connection, label):
            raise NanaSQLiteDatabaseError("verification failed")

        monkeypatch.setattr(db, "_verify_connection_integrity", fail_verification)
        with pytest.raises(NanaSQLiteDatabaseError, match="verification failed"):
            db.backup(str(destination))
    assert destination.read_bytes() == original
    assert list(tmp_path.glob(".existing.db.*.tmp")) == []


def test_backup_refuses_dlq_unless_explicitly_allowed(tmp_path, monkeypatch):
    source = str(tmp_path / "dlq.db")
    destination = str(tmp_path / "dlq-backup.db")
    with NanaSQLite(source, v2_mode=True, flush_mode="manual") as db:
        monkeypatch.setattr(db._v2_engine, "get_dlq", lambda: [{"error": "failed"}])
        with pytest.raises(NanaSQLiteDatabaseError, match="dead-letter"):
            db.backup(destination)
        db.backup(destination, allow_incomplete=True)


def test_restore_rejects_corruption_without_closing_live_db(tmp_path):
    path = str(tmp_path / "live.db")
    corrupt = tmp_path / "corrupt.db"
    corrupt.write_bytes(b"not sqlite")
    with NanaSQLite(path, v2_mode=True) as db:
        db["safe"] = "value"
        with pytest.raises(NanaSQLiteDatabaseError, match="verify restore source"):
            db.restore(str(corrupt))
        assert db["safe"] == "value"


def test_restore_captures_committed_wal_from_live_source(tmp_path):
    source_path = str(tmp_path / "live-source.db")
    target_path = str(tmp_path / "restore-target.db")
    source = NanaSQLite(source_path, optimize=True)
    source["from_wal"] = {"value": 42}
    with NanaSQLite(target_path) as target:
        target["old"] = True
        target.restore(source_path)
        assert target["from_wal"] == {"value": 42}
        assert "old" not in target
    source.close()


def test_restore_snapshot_failure_restarts_v2_engine(tmp_path, monkeypatch):
    source_path = str(tmp_path / "valid-source.db")
    target_path = str(tmp_path / "v2-target.db")
    with NanaSQLite(source_path) as source:
        source["replacement"] = True
    with NanaSQLite(target_path, v2_mode=True, flush_mode="manual") as target:
        target["original"] = True
        original_verify = target._verify_connection_integrity
        calls = [0]

        def fail_snapshot(connection, label):
            calls[0] += 1
            if calls[0] == 1:
                raise NanaSQLiteDatabaseError("snapshot verification failed")
            return original_verify(connection, label)

        monkeypatch.setattr(target, "_verify_connection_integrity", fail_snapshot)
        with pytest.raises(NanaSQLiteDatabaseError, match="snapshot verification failed"):
            target.restore(source_path)
        target["after_failure"] = True
        target.flush(wait=True)
    with NanaSQLite(target_path) as reopened:
        assert reopened["original"] is True
        assert reopened["after_failure"] is True


def test_restore_keeps_one_v2_engine_for_parent_and_children(tmp_path):
    source_path = str(tmp_path / "parent-child-source.db")
    target_path = str(tmp_path / "parent-child-target.db")
    with NanaSQLite(source_path) as source:
        source["main"] = True
        source.table("children", warn_duplicate_table_instance=False)["child"] = True
    with NanaSQLite(target_path, v2_mode=True, flush_mode="manual") as target:
        child = target.table("children", warn_duplicate_table_instance=False)
        target.restore(source_path)
        assert child._v2_engine is target._v2_engine
        child["after"] = True
        target.flush(wait=True)
        assert child["child"] is True


def test_encrypted_atomic_operations(tmp_path):
    cryptography = pytest.importorskip("cryptography.hazmat.primitives.ciphers.aead")
    key = cryptography.AESGCM.generate_key(bit_length=256)
    with NanaSQLite(str(tmp_path / "encrypted.db"), encryption_key=key) as db:
        db["item"] = {"count": 1}
        assert db.increment("item", field="count") == {"count": 2}
        assert db.patch("item", {"secret": "yes"}) == {"count": 2, "secret": "yes"}


def test_atomic_operations_update_hooks_and_lru_cache(tmp_path):
    hook = UniqueHook("name", use_index=True)
    with NanaSQLite(
        str(tmp_path / "hook-cache.db"),
        hooks=[hook],
        cache_strategy="lru",
        cache_size=8,
    ) as db:
        db["first"] = {"name": "Nana", "count": 1}
        db["second"] = {"name": "Other", "count": 1}
        assert db.increment("first", field="count")["count"] == 2
        assert db.patch("first", {"name": "Updated"})["name"] == "Updated"
        with pytest.raises(NanaSQLiteValidationError, match="Unique"):
            db.patch("second", {"name": "Updated"})
        assert db["first"] == {"name": "Updated", "count": 2}


def test_rollback_invalidates_cache_and_hook_index(tmp_path):
    hook = UniqueHook("name", use_index=True)
    with NanaSQLite(str(tmp_path / "rollback.db"), hooks=[hook]) as db:
        db["item"] = {"name": "before", "count": 1}
        db.begin_transaction()
        db.patch("item", {"name": "temporary"})
        db.rollback()
        assert db["item"] == {"name": "before", "count": 1}
        db["other"] = {"name": "temporary"}
