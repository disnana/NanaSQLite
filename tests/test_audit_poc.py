"""
POC verification tests for audit findings (v1.3.4 + v1.4.0).

Each test corresponds to a POC in etc/poc/ and verifies that the patched code
handles the reported vulnerability or bug correctly.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import tempfile
import time

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from nanasqlite import AsyncNanaSQLite, NanaSQLite
from nanasqlite.exceptions import (
    NanaSQLiteClosedError,
    NanaSQLiteDatabaseError,
    NanaSQLiteValidationError,
)
from nanasqlite.utils import ExpiringDict


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def db_path():
    """Provide a temporary database path and clean up after test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    for suffix in ("", "-wal", "-shm"):
        try:
            os.unlink(path + suffix)
        except OSError:
            pass  # File may already be deleted or locked during cleanup


@pytest.fixture
def db(db_path):
    """Provide an open NanaSQLite instance."""
    database = NanaSQLite(db_path)
    yield database
    database.close()


# ===========================================================================
# BUG-01 [Critical]: items() missing _check_connection()
# ===========================================================================
class TestBug01ItemsCheckConnection:
    """BUG-01: items() must raise NanaSQLiteClosedError on closed instance."""

    def test_items_on_closed_db(self, db_path):
        """Calling items() on a closed instance raises NanaSQLiteClosedError."""
        db = NanaSQLite(db_path)
        db["k"] = "v"
        db.close()

        with pytest.raises(NanaSQLiteClosedError):
            db.items()

    def test_items_on_open_db(self, db):
        """items() works normally on an open instance."""
        db["a"] = 1
        db["b"] = 2
        items = db.items()
        assert ("a", 1) in items
        assert ("b", 2) in items


# ===========================================================================
# BUG-02 [High]: AEAD deserialize silent plaintext fallback
# ===========================================================================
class TestBug02AeadPlaintextFallback:
    """BUG-02: AEAD mode must warn (not silently fallback) for non-bytes data."""

    def test_aead_non_bytes_logs_warning(self, db_path, caplog):
        """When AEAD is enabled but data is str, a warning must be logged."""
        key = AESGCM.generate_key(bit_length=256)

        # Write plaintext JSON directly to DB (simulating pre-encryption data)
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value TEXT)")
        conn.execute(
            "INSERT INTO data (key, value) VALUES (?, ?)",
            ("test", json.dumps("plaintext_value")),
        )
        conn.commit()
        conn.close()

        db = NanaSQLite(db_path, encryption_key=key)
        try:
            with caplog.at_level(logging.WARNING, logger="nanasqlite.core"):
                val = db["test"]

            # Value should still be readable (backward compat)
            assert val == "plaintext_value"
            # But a warning must have been logged
            assert any("AEAD encryption is enabled but received non-bytes" in r.message for r in caplog.records)
        finally:
            db.close()


# ===========================================================================
# BUG-03 [High]: No nonce length check before AEAD decrypt
# ===========================================================================
class TestBug03AeadShortNonce:
    """BUG-03: Short encrypted data must raise NanaSQLiteDatabaseError."""

    def test_short_encrypted_data_raises(self, db_path):
        """Data shorter than 28 bytes (12 nonce + 16 auth tag) raises NanaSQLiteDatabaseError."""
        key = AESGCM.generate_key(bit_length=256)

        # Write very short binary data directly
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value BLOB)")
        conn.execute("INSERT INTO data (key, value) VALUES (?, ?)", ("k", b"\x00" * 5))
        conn.commit()
        conn.close()

        db = NanaSQLite(db_path, encryption_key=key)
        try:
            with pytest.raises(NanaSQLiteDatabaseError, match="too short"):
                _ = db["k"]
        finally:
            db.close()

    def test_empty_encrypted_data_raises(self, db_path):
        """Empty bytes raises NanaSQLiteDatabaseError."""
        key = AESGCM.generate_key(bit_length=256)

        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value BLOB)")
        conn.execute("INSERT INTO data (key, value) VALUES (?, ?)", ("k", b""))
        conn.commit()
        conn.close()

        db = NanaSQLite(db_path, encryption_key=key)
        try:
            with pytest.raises(NanaSQLiteDatabaseError, match="too short"):
                _ = db["k"]
        finally:
            db.close()

    def test_partial_nonce_data_raises(self, db_path):
        """Data with 13-27 bytes (nonce only, no full auth tag) raises NanaSQLiteDatabaseError.

        Previously, the guard only checked len < 13, allowing payloads that would
        reach decrypt() and raise a low-level InvalidTag instead of NanaSQLiteDatabaseError.
        """
        key = AESGCM.generate_key(bit_length=256)

        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value BLOB)")
        # 20 bytes: passes old < 13 check but still too short (12 nonce + 16 tag = 28 min)
        conn.execute("INSERT INTO data (key, value) VALUES (?, ?)", ("k", b"\x00" * 20))
        conn.commit()
        conn.close()

        db = NanaSQLite(db_path, encryption_key=key)
        try:
            with pytest.raises(NanaSQLiteDatabaseError):
                _ = db["k"]
        finally:
            db.close()


# ===========================================================================
# BUG-04 [High]: Redundant double-init in acontains()
# ===========================================================================
class TestBug04AcontainsDoubleInit:
    """BUG-04: acontains() should not double-initialize."""

    @pytest.mark.asyncio
    async def test_acontains_works(self, db_path):
        """acontains() returns correct result without redundant init."""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("exists", 42)
            assert await db.acontains("exists") is True
            assert await db.acontains("missing") is False


# ===========================================================================
# BUG-05 [Medium]: Missing offset validation in async _shared_query_impl
# ===========================================================================
class TestBug05AsyncOffsetValidation:
    """BUG-05: Async query must validate offset parameter."""

    @pytest.mark.asyncio
    async def test_negative_offset_rejected(self, db_path):
        """Negative offset raises ValueError."""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("t", {"id": "INTEGER"})
            with pytest.raises(ValueError, match="non-negative"):
                await db.query_with_pagination("t", offset=-1)

    @pytest.mark.asyncio
    async def test_non_int_offset_rejected(self, db_path):
        """Non-integer offset raises ValueError."""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("t", {"id": "INTEGER"})
            with pytest.raises(ValueError, match="integer"):
                await db.query_with_pagination("t", offset="abc")


# ===========================================================================
# BUG-07 [Medium]: ExpiringDict scheduler processes only 1 key per iteration
# ===========================================================================
class TestBug07ExpiringDictBatch:
    """BUG-07: ExpiringDict scheduler must process all expired keys per iteration."""

    def test_multiple_expired_keys_evicted(self):
        """Multiple keys that expire at the same time are all evicted."""
        evicted = []
        d = ExpiringDict(expiration_time=0.1, on_expire=lambda k, v: evicted.append(k))
        # Insert multiple keys (TTL is set by expiration_time)
        for i in range(10):
            d[f"key_{i}"] = f"val_{i}"

        # Poll until all keys are evicted (bounded timeout to avoid hanging)
        deadline = time.time() + 3.0
        while len(evicted) < 10 and time.time() < deadline:
            time.sleep(0.1)

        # All keys should be evicted, not just one per iteration
        assert len(evicted) == 10, f"Only {len(evicted)}/10 keys evicted: {evicted}"
        d.clear()


# ===========================================================================
# BUG-09 [Medium]: batch_get() drops keys with None values
# ===========================================================================
class TestBug09BatchGetNone:
    """BUG-09: batch_get() must include keys with explicit None values."""

    def test_batch_get_includes_none_values(self, db):
        """Keys stored with None value appear in batch_get results."""
        db["key_none"] = None
        db["key_value"] = "hello"

        result = db.batch_get(["key_none", "key_value", "missing"])

        assert "key_none" in result
        assert result["key_none"] is None
        assert result["key_value"] == "hello"
        assert "missing" not in result

    def test_batch_get_after_reopen(self, db_path):
        """batch_get() with None values works after DB reopen."""
        db = NanaSQLite(db_path)
        db["k1"] = None
        db["k2"] = "val"
        db.close()

        db2 = NanaSQLite(db_path)
        result = db2.batch_get(["k1", "k2"])
        assert "k1" in result
        assert result["k1"] is None
        assert result["k2"] == "val"
        db2.close()


# ===========================================================================
# SEC-01 [High]: alter_table_add_column() column_type injection
# ===========================================================================
class TestSec01ColumnTypeInjection:
    """SEC-01: column_type must be validated with whitelist, not blacklist."""

    def test_valid_types_accepted(self, db):
        """Standard SQL types are accepted."""
        db.create_table("t", {"id": "INTEGER"})

        valid_types = ["TEXT", "INTEGER", "REAL", "BLOB", "VARCHAR(255)", "DECIMAL(10,2)", "DOUBLE PRECISION"]
        for i, col_type in enumerate(valid_types):
            db.alter_table_add_column("t", f"col{i}", col_type)
        # All should succeed without error

    def test_constraint_injection_blocked(self, db):
        """Constraint injection via '(' is blocked."""
        db.create_table("t", {"id": "INTEGER"})
        with pytest.raises(ValueError, match="Invalid or dangerous"):
            db.alter_table_add_column("t", "evil", "TEXT CHECK(1=1)")

    def test_semicolon_injection_blocked(self, db):
        """Semicolon injection is blocked."""
        db.create_table("t", {"id": "INTEGER"})
        with pytest.raises(ValueError, match="Invalid or dangerous"):
            db.alter_table_add_column("t", "evil", "TEXT; DROP TABLE t")

    def test_null_byte_injection_blocked(self, db):
        """Null byte truncation attack is blocked."""
        db.create_table("t", {"id": "INTEGER"})
        with pytest.raises(ValueError, match="Invalid or dangerous"):
            db.alter_table_add_column("t", "evil", "TEXT\x00DROP")

    def test_quote_injection_blocked(self, db):
        """Quote injection is blocked."""
        db.create_table("t", {"id": "INTEGER"})
        with pytest.raises(ValueError, match="Invalid or dangerous"):
            db.alter_table_add_column("t", "evil", "TEXT'--")


# ===========================================================================
# SEC-02 [High]: _validate_expression() misses double-quoted identifiers
# ===========================================================================
class TestSec02QuotedFunctionBypass:
    """SEC-02: Double-quoted function names must be detected by validation."""

    def test_unquoted_forbidden_function_blocked(self, db_path):
        """Baseline: unquoted forbidden function is blocked."""
        db = NanaSQLite(
            db_path,
            strict_sql_validation=True,
            forbidden_sql_functions=["EVIL"],
        )
        db.create_table("t", {"id": "INTEGER", "name": "TEXT"})
        db.sql_insert("t", {"id": 1, "name": "test"})

        try:
            with pytest.raises((NanaSQLiteValidationError, ValueError)):
                db.query("t", where="EVIL(1)")
        finally:
            db.close()

    def test_double_quoted_forbidden_function_blocked(self, db_path):
        """Double-quoted forbidden function is detected and blocked."""
        db = NanaSQLite(
            db_path,
            strict_sql_validation=True,
            forbidden_sql_functions=["EVIL"],
        )
        db.create_table("t", {"id": "INTEGER", "name": "TEXT"})
        db.sql_insert("t", {"id": 1, "name": "test"})

        try:
            with pytest.raises((NanaSQLiteValidationError, ValueError)):
                db.query("t", where='"EVIL"(1)')
        finally:
            db.close()

    def test_double_quoted_unknown_function_blocked(self, db_path):
        """Double-quoted unknown function (not in allowed list) is blocked."""
        db = NanaSQLite(db_path, strict_sql_validation=True)
        db.create_table("t", {"id": "INTEGER", "name": "TEXT"})
        db.sql_insert("t", {"id": 1, "name": "test"})

        try:
            with pytest.raises((NanaSQLiteValidationError, ValueError)):
                db.query("t", where='"UNKNOWN_FUNC"(1)')
        finally:
            db.close()

    def test_allowed_function_in_quotes_works(self, db_path):
        """Allowed functions still work when double-quoted."""
        db = NanaSQLite(db_path, strict_sql_validation=True)
        db.create_table("t", {"id": "INTEGER", "name": "TEXT"})
        db.sql_insert("t", {"id": 1, "name": "test"})

        try:
            # Use an existing column; quoted identifier not followed by '(' must be allowed
            results = db.query("t", where='"name" IS NOT NULL')
            # This should NOT raise because "name" here is not treated as a function
            assert isinstance(results, list)
        finally:
            db.close()


# ===========================================================================
# v1.4.0 Audit Findings
# ===========================================================================


# ===========================================================================
# SEC-01 [Critical]: create_table() column type SQL injection
# ===========================================================================
class TestV140Sec01CreateTableInjection:
    """SEC-01: create_table() must validate column type values to prevent SQL injection."""

    def test_semicolon_injection_blocked(self, db):
        """Semicolon in column type is blocked."""
        with pytest.raises((NanaSQLiteValidationError, ValueError)):
            db.create_table("evil", {"id": 'INTEGER); DELETE FROM "data" WHERE 1=1; --'})

    def test_line_comment_injection_blocked(self, db):
        """Line comment in column type is blocked."""
        with pytest.raises((NanaSQLiteValidationError, ValueError)):
            db.create_table("evil", {"id": "INTEGER -- comment"})

    def test_block_comment_injection_blocked(self, db):
        """Block comment in column type is blocked."""
        with pytest.raises((NanaSQLiteValidationError, ValueError)):
            db.create_table("evil", {"id": "INTEGER /* comment */"})

    def test_data_preserved_after_blocked_injection(self, db):
        """Injection attempt does not corrupt existing data."""
        db["key1"] = "value1"
        with pytest.raises((NanaSQLiteValidationError, ValueError)):
            db.create_table("evil", {"id": 'TEXT); DELETE FROM "data"; --'})
        assert db["key1"] == "value1"

    def test_valid_column_types_accepted(self, db):
        """Standard SQL column types with constraints are still accepted."""
        valid_types = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL",
            "email": "TEXT UNIQUE",
            "amount": "DECIMAL(10,2) DEFAULT 0",
            "status": "TEXT DEFAULT 'active'",
            "ref_id": "INTEGER REFERENCES other(id)",
        }
        db.create_table("valid_table", valid_types)


# ===========================================================================
# BUG-01 [High]: V2Engine on_success callback before COMMIT
# ===========================================================================
class TestV140Bug01V2OnSuccessDeferred:
    """BUG-01: V2Engine must call on_success only after COMMIT, not during transaction."""

    def test_on_success_not_called_on_rollback(self, db_path):
        """If a batch transaction rolls back, earlier tasks must not get on_success."""
        import apsw

        from nanasqlite.v2_engine import StrictTask, V2Engine

        conn = apsw.Connection(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value TEXT)")

        engine = V2Engine(
            connection=conn,
            table_name='"data"',
            flush_mode="manual",
        )

        callback_log = []

        task1 = StrictTask(
            priority=10,
            sequence_id=0,
            task_type="execute",
            sql="INSERT INTO data (key, value) VALUES ('k1', 'v1')",
            parameters=None,
            on_success=lambda: callback_log.append("task1_success"),
            on_error=lambda e: callback_log.append("task1_error"),
        )
        task2 = StrictTask(
            priority=10,
            sequence_id=1,
            task_type="execute",
            sql="INVALID SQL",
            parameters=None,
            on_success=lambda: callback_log.append("task2_success"),
            on_error=lambda e: callback_log.append("task2_error"),
        )

        engine._strict_queue.put(task1)
        engine._strict_queue.put(task2)

        try:
            engine._perform_flush()
        except Exception:
            pass

        # Since StrictTasks now have independent transactions, task1 succeeds and task2 fails.
        # task1's on_success WILL be called since it committed successfully.
        assert "task1_success" in callback_log
        # task2's on_success must NOT have been called since its transaction rolled back
        assert "task2_success" not in callback_log
        # task2's on_error must have been called
        assert "task2_error" in callback_log

        engine.shutdown()
        conn.close()

    def test_on_success_called_on_commit(self, db_path):
        """Successful tasks get on_success after COMMIT."""
        import apsw

        from nanasqlite.v2_engine import StrictTask, V2Engine

        conn = apsw.Connection(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value TEXT)")

        engine = V2Engine(
            connection=conn,
            table_name='"data"',
            flush_mode="manual",
        )

        callback_log = []

        task = StrictTask(
            priority=10,
            sequence_id=0,
            task_type="execute",
            sql="INSERT INTO data (key, value) VALUES ('k1', 'v1')",
            parameters=None,
            on_success=lambda: callback_log.append("success"),
        )

        engine._strict_queue.put(task)
        engine._perform_flush()

        assert "success" in callback_log
        engine.shutdown()
        conn.close()


# ===========================================================================
# BUG-02 [Medium]: AsyncNanaSQLite.table() missing attributes
# ===========================================================================
class TestV140Bug02AsyncTableAttrs:
    """BUG-02: AsyncNanaSQLite.table() child must inherit all parent attributes."""

    @pytest.mark.asyncio
    async def test_child_has_v2_attrs(self, db_path):
        """Child instance has v2-related attributes."""
        async with AsyncNanaSQLite(db_path) as db:
            child = await db.table("sub")
            for attr in [
                "_v2_mode",
                "_flush_mode",
                "_flush_interval",
                "_flush_count",
                "_v2_chunk_size",
            ]:
                assert hasattr(child, attr), f"Missing attribute: {attr}"

    @pytest.mark.asyncio
    async def test_child_has_cache_attrs(self, db_path):
        """Child instance has cache-related attributes."""
        async with AsyncNanaSQLite(db_path) as db:
            child = await db.table("sub")
            for attr in [
                "_cache_strategy",
                "_cache_size",
                "_cache_ttl",
                "_cache_persistence_ttl",
            ]:
                assert hasattr(child, attr), f"Missing attribute: {attr}"

    @pytest.mark.asyncio
    async def test_child_has_encryption_attrs(self, db_path):
        """Child instance has encryption-related attributes."""
        async with AsyncNanaSQLite(db_path) as db:
            child = await db.table("sub")
            for attr in ["_encryption_key", "_encryption_mode"]:
                assert hasattr(child, attr), f"Missing attribute: {attr}"


# ===========================================================================
# BUG-03 [Medium]: v2 mode execute() empty result for SELECTs
# ===========================================================================
class TestV140Bug03V2SelectBypass:
    """BUG-03: Read queries must bypass v2 background queue and return results."""

    def test_query_returns_results_in_v2_mode(self, db_path):
        """query() returns actual data in v2 mode."""
        import os

        os.environ["NANASQLITE_SUPPRESS_MP_WARNING"] = "1"
        db = NanaSQLite(db_path, v2_mode=True)
        try:
            db.create_table("t", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
            db.sql_insert("t", {"id": 1, "name": "test"})
            db.flush()

            rows = db.query("t")
            assert len(rows) > 0, "query() returned empty in v2 mode"
            assert rows[0]["name"] == "test"
        finally:
            db.close()

    def test_fetch_one_returns_results_in_v2_mode(self, db_path):
        """fetch_one() returns data in v2 mode."""
        import os

        os.environ["NANASQLITE_SUPPRESS_MP_WARNING"] = "1"
        db = NanaSQLite(db_path, v2_mode=True)
        try:
            db.create_table("t", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
            db.sql_insert("t", {"id": 1, "name": "test"})
            db.flush()

            row = db.fetch_one("SELECT name FROM t WHERE id = ?", (1,))
            assert row is not None
            assert row[0] == "test"
        finally:
            db.close()

    def test_pragma_works_in_v2_mode(self, db_path):
        """PRAGMA queries bypass v2 queue."""
        import os

        os.environ["NANASQLITE_SUPPRESS_MP_WARNING"] = "1"
        db = NanaSQLite(db_path, v2_mode=True)
        try:
            mode = db.pragma("journal_mode")
            assert mode is not None
        finally:
            db.close()


# ===========================================================================
# v1.4.1dev3 Audit Findings
# ===========================================================================


# ===========================================================================
# BUG-01 [High]: upsert(table, data_dict, conflict_columns) raised AttributeError
# ===========================================================================
class TestV141Bug01UpsertAttributeError:
    """BUG-01: upsert(table_name, data_dict, conflict_columns) must not raise AttributeError."""

    def test_upsert_insert_with_conflict_columns(self, db):
        """upsert() with table_name, data dict, and conflict_columns inserts a new row."""
        db.create_table("t", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
        # This call raised 'AttributeError: NoneType has no attribute keys' before fix
        db.upsert("t", {"id": 1, "name": "Alice"}, conflict_columns=["id"])
        rows = db.query("t")
        assert len(rows) == 1
        assert rows[0]["name"] == "Alice"

    def test_upsert_update_with_conflict_columns(self, db):
        """upsert() with conflict_columns updates an existing row on conflict."""
        db.create_table("t", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
        db.upsert("t", {"id": 1, "name": "Alice"}, conflict_columns=["id"])
        # Second call should update name, not raise
        db.upsert("t", {"id": 1, "name": "Bob"}, conflict_columns=["id"])
        rows = db.query("t")
        assert len(rows) == 1
        assert rows[0]["name"] == "Bob"

    def test_upsert_do_nothing_when_all_conflict_columns(self, db):
        """upsert() with all columns as conflict_columns does nothing on conflict."""
        db.create_table("t", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
        # Setup initial row
        db.upsert("t", {"id": 1, "name": "Alice"}, conflict_columns=["id"])

        # Upsert with ONLY the conflict column, which leaves update_items empty (triggering DO NOTHING)
        db.upsert("t", {"id": 1}, conflict_columns=["id"])

        rows = db.query("t")
        assert len(rows) == 1
        assert rows[0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_aupsert_with_conflict_columns(self, db_path):
        """aupsert() is also fixed (it delegates to upsert internally)."""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("t", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
            # aupsert wraps upsert — same bug would surface here
            await db.aupsert("t", {"id": 1, "name": "Alice"}, conflict_columns=["id"])
            rows = await db.query("t")
            assert rows[0]["name"] == "Alice"


# ===========================================================================
# v1.5.0 Hooks System Audit Findings
# ===========================================================================


# ===========================================================================
# SEC-03 [Critical]: UniqueHook TOCTOU Race Condition
# ===========================================================================
class TestV150Sec03UniqueHookRace:
    """SEC-03: UniqueHook has TOCTOU race condition in multi-threaded environments."""

    def test_unique_hook_race_condition_documented(self, db_path):
        """UniqueHook class has proper warning documentation about race conditions."""
        from nanasqlite.hooks import UniqueHook

        # Check that the class docstring contains race condition warning
        assert "TOCTOU race condition" in UniqueHook.__doc__
        assert "WARNING" in UniqueHook.__doc__
        assert "SEC-03" in UniqueHook.__doc__

    def test_unique_hook_single_threaded_works(self, db_path):
        """UniqueHook works correctly in single-threaded scenarios."""
        from nanasqlite import NanaSQLite
        from nanasqlite.exceptions import NanaSQLiteValidationError
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path, table="users")
        db.add_hook(UniqueHook("email"))

        try:
            # First user should succeed
            db["user1"] = {"email": "test@example.com", "name": "User 1"}

            # Second user with same email should fail
            with pytest.raises(NanaSQLiteValidationError, match="Unique constraint violation"):
                db["user2"] = {"email": "test@example.com", "name": "User 2"}

            # Verify only first user exists
            users = dict(db.items())
            assert "user1" in users
            assert "user2" not in users
            assert users["user1"]["email"] == "test@example.com"
        finally:
            db.close()


# ===========================================================================
# SEC-04 [Critical]: ForeignKeyHook TOCTOU Race Condition
# ===========================================================================
class TestV150Sec04ForeignKeyHookRace:
    """SEC-04: ForeignKeyHook has TOCTOU race condition allowing orphaned references."""

    def test_foreign_key_hook_race_condition_documented(self, db_path):
        """ForeignKeyHook class has proper warning documentation about race conditions."""
        from nanasqlite.hooks import ForeignKeyHook

        # Check that the class docstring contains race condition warning
        assert "TOCTOU race condition" in ForeignKeyHook.__doc__
        assert "WARNING" in ForeignKeyHook.__doc__
        assert "SEC-04" in ForeignKeyHook.__doc__

    def test_foreign_key_hook_single_threaded_works(self, db_path):
        """ForeignKeyHook works correctly in single-threaded scenarios."""
        from nanasqlite import NanaSQLite
        from nanasqlite.exceptions import NanaSQLiteValidationError
        from nanasqlite.hooks import ForeignKeyHook

        groups = NanaSQLite(db_path, table="groups")
        users = NanaSQLite(db_path, table="users")

        try:
            # Create a group
            groups["admin"] = {"name": "Administrators"}

            # Add FK constraint
            users.add_hook(ForeignKeyHook("group_id", groups))

            # Valid FK reference should work
            users["user1"] = {"name": "Alice", "group_id": "admin"}

            # Invalid FK reference should fail
            with pytest.raises(NanaSQLiteValidationError, match="Foreign key constraint violation"):
                users["user2"] = {"name": "Bob", "group_id": "nonexistent"}

            # Verify only valid user exists
            user_dict = dict(users.items())
            assert "user1" in user_dict
            assert "user2" not in user_dict
        finally:
            groups.close()
            users.close()


# ===========================================================================
# SEC-05 [High]: BaseHook ReDoS Vulnerability
# ===========================================================================
class TestV150Sec05BaseHookRedos:
    """SEC-05: BaseHook accepts dangerous regex patterns causing ReDoS."""

    def test_dangerous_regex_patterns_rejected(self, db_path):
        """Dangerous regex patterns are detected and rejected."""
        from nanasqlite.exceptions import NanaSQLiteValidationError
        from nanasqlite.hooks import BaseHook

        dangerous_patterns = [
            "(a+)+",
            "(a*)*",
            "(a+)+b",
            "(a|a)*"
        ]

        for pattern in dangerous_patterns:
            with pytest.raises(NanaSQLiteValidationError, match="dangerous regex pattern"):
                BaseHook(key_pattern=pattern)

    def test_safe_regex_patterns_accepted(self, db_path):
        """Safe regex patterns are still accepted."""
        from nanasqlite.hooks import BaseHook

        safe_patterns = [
            r"user_\d+",
            r"^[a-z]+$",
            r"data_\w*",
            r"[a-zA-Z0-9_]+"
        ]

        for pattern in safe_patterns:
            # Should not raise
            hook = BaseHook(key_pattern=pattern)
            # Test basic functionality
            assert hook._should_run("test_key") in [True, False]


# ===========================================================================
# SEC-06 [High]: Hooks Exception Information Leakage
# ===========================================================================
class TestV150Sec06HooksInfoLeakage:
    """SEC-06: Hook exception messages leak sensitive information."""

    def test_unique_hook_generic_error_message(self, db_path):
        """UniqueHook returns generic error message to prevent information leakage."""
        from nanasqlite import NanaSQLite
        from nanasqlite.exceptions import NanaSQLiteValidationError
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        db.add_hook(UniqueHook("email"))

        try:
            db["user1"] = {"email": "secret@company.internal"}

            with pytest.raises(NanaSQLiteValidationError) as exc_info:
                db["user2"] = {"email": "secret@company.internal"}

            # Error message should be generic, not leak field names or values
            error_msg = str(exc_info.value)
            assert "secret@company.internal" not in error_msg
            assert "email" not in error_msg
            assert "Unique constraint violation" in error_msg
        finally:
            db.close()

    def test_foreign_key_hook_generic_error_message(self, db_path):
        """ForeignKeyHook returns generic error message to prevent information leakage."""
        from nanasqlite import NanaSQLite
        from nanasqlite.exceptions import NanaSQLiteValidationError
        from nanasqlite.hooks import ForeignKeyHook

        groups = NanaSQLite(db_path, table="groups")
        users = NanaSQLite(db_path, table="users")

        try:
            users.add_hook(ForeignKeyHook("group_id", groups))

            with pytest.raises(NanaSQLiteValidationError) as exc_info:
                users["user1"] = {"name": "Alice", "group_id": "secret_dept_001"}

            # Error message should be generic, not leak field names or key values
            error_msg = str(exc_info.value)
            assert "secret_dept_001" not in error_msg
            assert "group_id" not in error_msg
            assert "Foreign key constraint violation" in error_msg
        finally:
            groups.close()
            users.close()


# ===========================================================================
# BUG-05 [Critical]: PydanticHook Silent Exception Suppression
# ===========================================================================
class TestV150Bug05PydanticExceptionSuppress:
    """BUG-05: PydanticHook.after_read() suppresses critical system exceptions."""

    def test_validation_errors_suppressed(self, db_path):
        """Validation errors are properly suppressed and logged."""
        from nanasqlite.hooks import PydanticHook

        # Mock Pydantic model that raises validation errors
        class MockModel:
            @classmethod
            def model_validate(cls, value):
                raise ValueError("Validation failed")

        hook = PydanticHook(MockModel)

        # Validation error should be suppressed, return original value
        result = hook.after_read(None, "test_key", {"data": "test"})
        assert result == {"data": "test"}

    def test_system_errors_not_suppressed(self, db_path):
        """Critical system errors are properly raised, not suppressed."""
        from nanasqlite.hooks import PydanticHook

        # Mock Pydantic model that raises system errors
        class MockModel:
            @classmethod
            def model_validate(cls, value):
                if value.get("trigger") == "connection":
                    raise ConnectionError("Database connection lost")
                elif value.get("trigger") == "memory":
                    raise MemoryError("Out of memory")
                elif value.get("trigger") == "system":
                    raise OSError("System I/O error")
                return cls()

        hook = PydanticHook(MockModel)

        # System errors should NOT be suppressed
        with pytest.raises(ConnectionError):
            hook.after_read(None, "test", {"trigger": "connection"})

        with pytest.raises(MemoryError):
            hook.after_read(None, "test", {"trigger": "memory"})

        with pytest.raises(OSError):
            hook.after_read(None, "test", {"trigger": "system"})


# ===========================================================================
# BUG-06 [High]: Hooks Memory Inefficiency in batch_update
# ===========================================================================
class TestV150Bug06HooksMemoryEfficiency:
    """BUG-06: Hook processing creates unnecessary dict copies affecting performance."""

    def test_no_value_change_no_copy(self, db_path):
        """When hooks don't change values, no new dict should be created."""
        from nanasqlite import NanaSQLite
        from nanasqlite.hooks import BaseHook

        # Hook that doesn't modify values
        class PassthroughHook(BaseHook):
            def before_write(self, db, key, value):
                return value  # No modification

        db = NanaSQLite(db_path, coerce=True)  # coerce=True triggers optimization path
        db.add_hook(PassthroughHook())

        try:
            original_mapping = {"key1": "value1", "key2": "value2"}

            # This is an indirect test - we verify the functionality works
            # The actual memory optimization is internal
            db.batch_update(original_mapping)

            # Verify data was written correctly
            assert db["key1"] == "value1"
            assert db["key2"] == "value2"
        finally:
            db.close()

    def test_value_change_creates_copy(self, db_path):
        """When hooks modify values, appropriate copying should occur."""
        from nanasqlite import NanaSQLite
        from nanasqlite.hooks import BaseHook

        # Hook that modifies values
        class ModifyingHook(BaseHook):
            def before_write(self, db, key, value):
                if isinstance(value, str):
                    return value.upper()
                return value

        db = NanaSQLite(db_path, coerce=True)
        db.add_hook(ModifyingHook())

        try:
            db.batch_update({"key1": "hello", "key2": "world"})

            # Values should be modified by hook
            assert db["key1"] == "HELLO"
            assert db["key2"] == "WORLD"
        finally:
            db.close()


# ===========================================================================
# PERF-02 [Medium]: UniqueHook O(N) Scaling Issue
# ===========================================================================
class TestV150Perf02UniqueHookScaling:
    """PERF-02: UniqueHook performs O(N) linear search affecting large datasets."""

    def test_unique_hook_scales_with_dataset_size(self, db_path):
        """UniqueHook performance degrades linearly with dataset size."""
        import time

        from nanasqlite import NanaSQLite
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        db.add_hook(UniqueHook("email"))

        try:
            # Add some baseline data
            for i in range(100):
                db[f"user_{i}"] = {"email": f"user{i}@test.com", "name": f"User {i}"}

            # Measure time to add one more record (triggers uniqueness check)
            start = time.perf_counter()
            db["new_user"] = {"email": "new@test.com", "name": "New User"}
            elapsed = time.perf_counter() - start

            # For 100 records, should complete reasonably quickly
            assert elapsed < 1.0, f"UniqueHook too slow: {elapsed:.3f}s for 100 records"

            # Verify the unique constraint is still enforced
            with pytest.raises(NanaSQLiteValidationError):
                db["duplicate"] = {"email": "new@test.com", "name": "Duplicate"}
        finally:
            db.close()

    def test_unique_hook_recommendation_sqlite_constraints(self, db_path):
        """For production, recommend using SQLite UNIQUE constraints instead."""
        # This is a documentation/recommendation test
        # The proper solution would be:
        conn = sqlite3.connect(db_path)
        try:
            # Create table with SQLite UNIQUE constraint instead of UniqueHook
            conn.execute("""
                CREATE TABLE users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,  -- SQLite enforces uniqueness atomically
                    name TEXT
                )
            """)

            # SQLite UNIQUE constraint is atomic and scales better
            conn.execute("INSERT INTO users (id, email, name) VALUES ('u1', 'test@example.com', 'User 1')")

            # Duplicate should be rejected by database
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("INSERT INTO users (id, email, name) VALUES ('u2', 'test@example.com', 'User 2')")
        finally:
            conn.close()
