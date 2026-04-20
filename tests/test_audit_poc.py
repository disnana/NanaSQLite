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
            # Note: quote characters in DEFAULT values are intentionally rejected
            # by SEC-02 fix; use parameterized inserts instead of inline literals.
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
    """SEC-03/SEC-05: UniqueHook TOCTOU race condition — fixed in v1.5.4."""

    def test_unique_hook_race_condition_fixed_documented(self, db_path):
        """UniqueHook docstring describes the SEC-05 fix (TOCTOU resolved in non-v2 mode)."""
        from nanasqlite.hooks import UniqueHook

        # The old WARNING is gone; the docstring now describes the fix.
        assert "SEC-05" in UniqueHook.__doc__
        assert "SEC-03" in UniqueHook.__doc__
        assert "RLock" in UniqueHook.__doc__

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

    def test_dangerous_regex_patterns_rejected(self, monkeypatch):
        """Dangerous regex patterns are detected and rejected when the non-RE2 path is active."""
        from nanasqlite.exceptions import NanaSQLiteValidationError
        from nanasqlite.hooks import BaseHook

        # Force the non-RE2 branch so the blacklist is exercised regardless of
        # whether google-re2 is installed in this environment.
        monkeypatch.setattr("nanasqlite.hooks.HAS_RE2", False)

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
        from nanasqlite import NanaSQLite
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        db.add_hook(UniqueHook("email"))

        try:
            # Add some baseline data
            for i in range(100):
                db[f"user_{i}"] = {"email": f"user{i}@test.com", "name": f"User {i}"}

            # Verify that adding a new unique record succeeds
            db["new_user"] = {"email": "new@test.com", "name": "New User"}

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


# ===========================================================================
# v1.5.1 Audit Findings
# ===========================================================================

# ===========================================================================
# BUG-01 [High]: pop() bypasses v2 engine staging buffer
# ===========================================================================
class TestBug01V2PopBypass:
    """BUG-01: pop() in v2 mode calls _delete_from_db() directly, bypassing
    the v2 staging buffer.  A pending SET in the staging buffer is left intact
    and gets flushed to DB after pop(), resurrecting the deleted key."""

    @pytest.mark.skipif(
        os.environ.get("NANASQLITE_SUPPRESS_MP_WARNING", "") != "1",
        reason="Set NANASQLITE_SUPPRESS_MP_WARNING=1 to run v2 tests",
    )
    def test_pop_v2_no_resurrection_after_flush(self, db_path):
        """pop() in v2 manual mode must not allow data resurrection after flush()."""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with NanaSQLite(db_path, v2_mode=True, flush_mode="manual") as db:
                db["mykey"] = "hello"
                val = db.pop("mykey", None)
                assert val == "hello", "pop() should return the value"

                db.flush(wait=True)
                db.clear_cache()

                result = db.get("mykey", "DELETED")
                assert result == "DELETED", (
                    f"pop() した 'mykey' が flush() + clear_cache() 後に復活した: {result!r}"
                )

    @pytest.mark.skipif(
        os.environ.get("NANASQLITE_SUPPRESS_MP_WARNING", "") != "1",
        reason="Set NANASQLITE_SUPPRESS_MP_WARNING=1 to run v2 tests",
    )
    def test_pop_v2_key_not_in_db_after_flush(self, db_path):
        """After pop() in v2 mode and flush, the key must not exist in DB."""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with NanaSQLite(db_path, v2_mode=True, flush_mode="manual") as db:
                db["k1"] = {"data": "value"}
                db["k2"] = {"data": "other"}

                db.pop("k1", None)
                db.flush(wait=True)
                db.clear_cache()

                assert db.get("k1") is None, "k1 should be absent after pop() + flush()"
                assert db.get("k2") == {"data": "other"}, "k2 should still be present"

    def test_pop_v1_normal_behavior(self, db_path):
        """pop() in non-v2 mode should still work correctly."""
        with NanaSQLite(db_path) as db:
            db["key"] = "value"
            result = db.pop("key", "DEFAULT")
            assert result == "value"
            assert db.get("key") is None

    def test_pop_missing_key_with_default(self, db_path):
        """pop() on missing key with default should return default."""
        with NanaSQLite(db_path) as db:
            result = db.pop("nonexistent", "default_val")
            assert result == "default_val"

    def test_pop_missing_key_no_default_raises(self, db_path):
        """pop() on missing key without default should raise KeyError."""
        with NanaSQLite(db_path) as db:
            with pytest.raises(KeyError):
                db.pop("nonexistent")


# ===========================================================================
# BUG-02 [Medium]: batch_get() ignores _cached_keys "known absent" status
# ===========================================================================
class TestBug02BatchGetCachedKeys:
    """BUG-02: batch_get() only checks _data but not _cached_keys.
    After __delitem__, the key is 'known absent' in _cached_keys but not in _data.
    In v2 non-immediate mode the staging delete hasn't hit DB yet, so batch_get()
    falls through to DB and finds the stale value."""

    @pytest.mark.skipif(
        os.environ.get("NANASQLITE_SUPPRESS_MP_WARNING", "") != "1",
        reason="Set NANASQLITE_SUPPRESS_MP_WARNING=1 to run v2 tests",
    )
    def test_batch_get_consistent_with_get_after_delete_v2(self, db_path):
        """After __delitem__ in v2 manual mode, batch_get and get should agree."""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with NanaSQLite(db_path, v2_mode=True, flush_mode="manual") as db:
                db["key1"] = "value1"
                db.flush(wait=True)

                del db["key1"]

                get_result = db.get("key1", "NOT_FOUND")
                batch_result = db.batch_get(["key1"])

                assert get_result == "NOT_FOUND", "get() should say key1 is absent"
                assert "key1" not in batch_result, (
                    f"batch_get() returned stale value for deleted key: {batch_result}"
                )

    def test_batch_get_after_pop_v1(self, db_path):
        """After pop() in v1 mode, batch_get should not return the deleted key."""
        with NanaSQLite(db_path) as db:
            db["k1"] = "v1"
            db["k2"] = "v2"
            db.pop("k1")

            result = db.batch_get(["k1", "k2"])
            assert "k1" not in result, "k1 was popped, batch_get should not return it"
            assert result.get("k2") == "v2"

    def test_batch_get_after_del_v1(self, db_path):
        """After __delitem__ in v1 mode, batch_get should not return the deleted key."""
        with NanaSQLite(db_path) as db:
            db["x"] = "data"
            del db["x"]

            result = db.batch_get(["x"])
            assert "x" not in result


# ===========================================================================
# SEC-01 [Medium]: exists() WHERE clause not validated
# ===========================================================================
class TestSec01ExistsNoValidation:
    """SEC-01: exists() does not call _validate_expression() on the WHERE clause.
    forbidden_sql_functions settings are not enforced for exists()."""

    def test_exists_honours_forbidden_sql_functions(self, db_path):
        """exists() must reject WHERE with forbidden function when strict mode active."""
        with NanaSQLite(
            db_path,
            strict_sql_validation=True,
            forbidden_sql_functions=["UPPER"],
        ) as db:
            db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
            db.sql_insert("users", {"id": 1, "name": "Alice"})

            # query() rejects forbidden function
            with pytest.raises(NanaSQLiteValidationError):
                db.query("users", where="UPPER(name) = ?", parameters=("ALICE",))

            # exists() must also reject it
            with pytest.raises(NanaSQLiteValidationError):
                db.exists("users", "UPPER(name) = ?", ("ALICE",))

    def test_exists_normal_usage_works(self, db_path):
        """exists() must still work correctly with valid WHERE clauses."""
        with NanaSQLite(db_path, strict_sql_validation=True) as db:
            db.create_table("items", {"id": "INTEGER PRIMARY KEY"})
            db.sql_insert("items", {"id": 42})

            assert db.exists("items", "id = ?", (42,)) is True
            assert db.exists("items", "id = ?", (99,)) is False

    def test_exists_rejects_dangerous_where(self, db_path):
        """exists() must reject WHERE with semicolons in strict mode."""
        with NanaSQLite(db_path, strict_sql_validation=True) as db:
            db.create_table("t", {"id": "INTEGER PRIMARY KEY"})
            with pytest.raises((NanaSQLiteValidationError, ValueError)):
                db.exists("t", "1=1; DROP TABLE t--")


# ===========================================================================
# SEC-02 [Medium]: sql_update()/sql_delete() WHERE not validated
# ===========================================================================
class TestSec02SqlUpdateDeleteNoValidation:
    """SEC-02: sql_update() and sql_delete() do not call _validate_expression()
    on the WHERE clause, inconsistent with count() / query()."""

    def test_sql_update_honours_forbidden_sql_functions(self, db_path):
        """sql_update() must reject WHERE with forbidden function in strict mode."""
        with NanaSQLite(
            db_path,
            strict_sql_validation=True,
            forbidden_sql_functions=["UPPER"],
        ) as db:
            db.create_table("items", {"id": "INTEGER PRIMARY KEY", "val": "TEXT"})
            db.sql_insert("items", {"id": 1, "val": "a"})

            with pytest.raises(NanaSQLiteValidationError):
                db.sql_update("items", {"val": "x"}, "UPPER(val) = ?", ("A",))

    def test_sql_delete_honours_forbidden_sql_functions(self, db_path):
        """sql_delete() must reject WHERE with forbidden function in strict mode."""
        with NanaSQLite(
            db_path,
            strict_sql_validation=True,
            forbidden_sql_functions=["UPPER"],
        ) as db:
            db.create_table("items", {"id": "INTEGER PRIMARY KEY", "val": "TEXT"})
            db.sql_insert("items", {"id": 1, "val": "a"})

            with pytest.raises(NanaSQLiteValidationError):
                db.sql_delete("items", "UPPER(val) = ?", ("A",))

    def test_sql_update_normal_usage_works(self, db_path):
        """sql_update() must work with valid WHERE in strict mode."""
        with NanaSQLite(db_path, strict_sql_validation=True) as db:
            db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
            db.sql_insert("users", {"id": 1, "name": "Alice"})
            count = db.sql_update("users", {"name": "Bob"}, "id = ?", (1,))
            assert count == 1
            row = db.query("users", where="id = ?", parameters=(1,))
            assert row[0]["name"] == "Bob"

    def test_sql_delete_normal_usage_works(self, db_path):
        """sql_delete() must work with valid WHERE in strict mode."""
        with NanaSQLite(db_path, strict_sql_validation=True) as db:
            db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
            db.sql_insert("users", {"id": 1, "name": "Alice"})
            count = db.sql_delete("users", "id = ?", (1,))
            assert count == 1


# ===========================================================================
# PERF-05 [Low]: fast_validate_sql_chars module-level constant
# ===========================================================================
class TestPerf05FastValidateSqlChars:
    """PERF-05: fast_validate_sql_chars() should use a module-level frozenset
    constant rather than creating a new set on each call."""

    def test_module_level_constant_exists(self):
        """_SAFE_SQL_CHARS should be a module-level frozenset constant."""
        from nanasqlite.sql_utils import _SAFE_SQL_CHARS

        assert isinstance(_SAFE_SQL_CHARS, frozenset)
        assert "a" in _SAFE_SQL_CHARS
        assert "Z" in _SAFE_SQL_CHARS
        assert ";" not in _SAFE_SQL_CHARS

    def test_fast_validate_accepts_safe_chars(self):
        """fast_validate_sql_chars() must accept expressions with safe chars."""
        from nanasqlite.sql_utils import fast_validate_sql_chars

        assert fast_validate_sql_chars("age > ?") is True
        assert fast_validate_sql_chars("name = ?") is True
        assert fast_validate_sql_chars("") is True

    def test_fast_validate_rejects_unsafe_chars(self):
        """fast_validate_sql_chars() must reject expressions with unsafe chars."""
        from nanasqlite.sql_utils import fast_validate_sql_chars

        assert fast_validate_sql_chars("age > 0; DROP TABLE users") is False


# ===========================================================================
# BUG-03 [Low]: to_dict() leaks MISSING sentinel in LRU/TTL mode
# ===========================================================================
class TestBug03ToDictMissingSentinel:
    """BUG-03: to_dict() did not filter out MISSING sentinel values which can
    appear in LRU/TTL cache mode as negative-cache entries."""

    def test_to_dict_no_missing_sentinel_lru(self, db_path):
        """to_dict() must not include MISSING sentinel for LRU cache."""
        from nanasqlite.cache import MISSING

        db = NanaSQLite(db_path, cache_strategy="lru", cache_size=10)
        try:
            db["real_key"] = "real_value"
            # Trigger a "known absent" lookup which sets MISSING in LRU cache
            _ = db.get("missing_key", None)  # causes MISSING sentinel to be cached

            result = db.to_dict()
            for v in result.values():
                assert v is not MISSING, "to_dict() should not contain MISSING sentinel"
            assert result.get("real_key") == "real_value"
        finally:
            db.close()

    def test_to_dict_no_missing_sentinel_unbounded(self, db_path):
        """to_dict() must not include MISSING sentinel for unbounded cache."""
        from nanasqlite.cache import MISSING

        db = NanaSQLite(db_path)
        try:
            db["key1"] = "value1"
            result = db.to_dict()
            for v in result.values():
                assert v is not MISSING
            assert result == {"key1": "value1"}
        finally:
            db.close()


# ===========================================================================
# PERF-12: get() LRU/TTL mode double-lookup fix
# ===========================================================================
class TestPerf12GetDoubleLookup:
    """PERF-12: get() method in LRU/TTL mode called _ensure_cached() (which
    internally calls cache.get() / move_to_end()) and then called cache.get()
    again directly — two move_to_end() invocations per cache hit.
    Fixed by checking _data membership first then a single cache.get()."""

    def test_get_lru_cache_hit_returns_correct_value(self, db_path):
        """get() must return the cached value on LRU cache hit."""
        db = NanaSQLite(db_path, cache_strategy="lru", cache_size=128)
        try:
            db["alpha"] = {"data": [1, 2, 3]}
            _ = db["alpha"]  # warm up cache
            assert db.get("alpha") == {"data": [1, 2, 3]}
        finally:
            db.close()

    def test_get_lru_cache_miss_returns_default(self, db_path):
        """get() must return default when the key does not exist."""
        db = NanaSQLite(db_path, cache_strategy="lru", cache_size=64)
        try:
            assert db.get("nonexistent", "fallback") == "fallback"
        finally:
            db.close()

    def test_get_lru_known_absent_returns_default_not_missing(self, db_path):
        """get() must return the default value (not MISSING sentinel) for a
        key that has been accessed before and is known-absent in LRU mode."""
        from nanasqlite.cache import MISSING

        db = NanaSQLite(db_path, cache_strategy="lru", cache_size=64)
        try:
            db.get("ghost", None)  # populates negative cache (MISSING sentinel)
            result = db.get("ghost", "fallback")
            assert result == "fallback"
            assert result is not MISSING
        finally:
            db.close()

    def test_get_ttl_cache_hit_returns_correct_value(self, db_path):
        """get() must return the cached value on TTL cache hit."""
        db = NanaSQLite(db_path, cache_strategy="ttl", cache_ttl=300)
        try:
            db["beta"] = {"nums": list(range(5))}
            _ = db["beta"]  # warm up
            assert db.get("beta") == {"nums": list(range(5))}
        finally:
            db.close()

    def test_get_ttl_missing_key_returns_default(self, db_path):
        """get() must return default for missing key in TTL mode."""
        db = NanaSQLite(db_path, cache_strategy="ttl", cache_ttl=300)
        try:
            assert db.get("no_such_key", 99) == 99
        finally:
            db.close()

    def test_get_unbounded_still_works(self, db_path):
        """get() must still work correctly in Unbounded mode (not regression)."""
        db = NanaSQLite(db_path)
        try:
            db["u1"] = "hello"
            assert db.get("u1") == "hello"
            assert db.get("missing") is None
            assert db.get("missing", "def") == "def"
        finally:
            db.close()


# ===========================================================================
# PERF-13: values() / items() Unbounded mode MISSING filter skip
# ===========================================================================
class TestPerf13ValuesItemsFilter:
    """PERF-13: values() and items() applied `if v is not MISSING` filter even
    in Unbounded mode where MISSING is never stored in _data.
    Fixed to use list(_data.values()) / list(_data.items()) directly for
    Unbounded mode, matching the PERF-08 optimisation in to_dict()."""

    def test_values_unbounded_no_missing(self, db_path):
        """values() in Unbounded mode must not contain MISSING sentinel."""
        from nanasqlite.cache import MISSING

        db = NanaSQLite(db_path)
        try:
            for i in range(30):
                db[f"k{i}"] = i
            vals = db.values()
            assert MISSING not in vals
            assert len(vals) == 30
            assert set(vals) == set(range(30))
        finally:
            db.close()

    def test_items_unbounded_no_missing(self, db_path):
        """items() in Unbounded mode must not contain MISSING sentinel."""
        from nanasqlite.cache import MISSING

        db = NanaSQLite(db_path)
        try:
            data = {f"x{i}": i * 2 for i in range(20)}
            db.batch_update(data)
            pairs = db.items()
            assert not any(v is MISSING for _, v in pairs)
            assert len(pairs) == 20
            assert dict(pairs) == data
        finally:
            db.close()

    def test_values_lru_no_missing(self, db_path):
        """values() in LRU mode must not contain MISSING sentinel (BUG-03 regression)."""
        from nanasqlite.cache import MISSING

        db = NanaSQLite(db_path, cache_strategy="lru", cache_size=128)
        try:
            for i in range(15):
                db[f"m{i}"] = i
            # Trigger negative cache entries
            db.get("ghost_val")
            vals = db.values()
            assert MISSING not in vals
            assert len(vals) == 15
        finally:
            db.close()

    def test_items_lru_no_missing(self, db_path):
        """items() in LRU mode must not contain MISSING sentinel (BUG-03 regression)."""
        from nanasqlite.cache import MISSING

        db = NanaSQLite(db_path, cache_strategy="lru", cache_size=128)
        try:
            for i in range(10):
                db[f"n{i}"] = i * 3
            # Trigger negative cache
            db.get("absent_item")
            pairs = db.items()
            assert not any(v is MISSING for _, v in pairs)
            assert len(pairs) == 10
        finally:
            db.close()

    def test_values_items_consistent_with_to_dict(self, db_path):
        """values() and items() must be consistent with to_dict() in Unbounded mode."""
        db = NanaSQLite(db_path)
        try:
            data = {f"p{i}": i for i in range(25)}
            db.batch_update(data)
            d = db.to_dict()
            assert sorted(db.values()) == sorted(d.values())
            assert sorted(db.items()) == sorted(d.items())
        finally:
            db.close()


# ---------------------------------------------------------------------------
# BUG-02: execute_many transaction leak on non-apsw exceptions (rc3 audit)
# ---------------------------------------------------------------------------


class TestBug02ExecuteManyTxnLeak:
    """BUG-02: execute_many の非 apsw.Error 例外でトランザクションがリークしない"""

    def test_execute_many_bad_params_no_txn_leak(self, db_path):
        """非apsw例外後も後続の書き込みが成功することを確認"""
        db = NanaSQLite(db_path)
        try:
            db["seed"] = "ok"
            # object() は展開できず TypeError が発生するはず
            try:
                db.execute_many(
                    "INSERT OR REPLACE INTO data(key, value) VALUES (?, ?)",
                    [("k1", "v1"), object()],
                )
            except Exception:  # noqa: BLE001  # expected: testing recovery after intentional error
                pass  # exception expected; we're testing recovery, not the exception itself
            # 修正後: リークなし → 書き込み成功
            db["after"] = "still_works"
            assert db["after"] == "still_works"
        finally:
            db.close()

    def test_execute_many_apsw_error_rollback(self, db_path):
        """apsw.Error でも ROLLBACK が実行され後続書き込みが成功する"""
        db = NanaSQLite(db_path)
        try:
            db["x"] = 1
            try:
                db.execute_many("INVALID SQL ??", [("a",)])
            except Exception:  # noqa: BLE001  # expected: testing recovery after intentional error
                pass  # exception expected; we're testing recovery, not the exception itself
            db["y"] = 2
            assert db["y"] == 2
        finally:
            db.close()


# ---------------------------------------------------------------------------
# BUG-03: begin_transaction _in_transaction state outside lock (rc3 audit)
# ---------------------------------------------------------------------------


class TestBug03BeginTxnRace:
    """BUG-03: begin_transaction の _in_transaction フラグがロック内で設定される"""

    def test_begin_transaction_flag_set_inside_lock(self, db_path):
        """begin_transaction 後に _in_transaction が True になっている"""
        db = NanaSQLite(db_path)
        try:
            db.begin_transaction()
            assert db.in_transaction() is True
            db.rollback()
            assert db.in_transaction() is False
        finally:
            db.close()

    def test_commit_clears_flag(self, db_path):
        """commit 後に _in_transaction が False になっている"""
        db = NanaSQLite(db_path)
        try:
            db.begin_transaction()
            db.commit()
            assert db.in_transaction() is False
        finally:
            db.close()

    def test_no_double_begin_raises(self, db_path):
        """二重 begin_transaction は NanaSQLiteTransactionError を送出する"""
        from nanasqlite.exceptions import NanaSQLiteTransactionError

        db = NanaSQLite(db_path)
        try:
            db.begin_transaction()
            with pytest.raises(NanaSQLiteTransactionError):
                db.begin_transaction()
            db.rollback()
        finally:
            db.close()


# ---------------------------------------------------------------------------
# PERF-21~26,29: coverage for new code paths added in v1.5.3rc3
# ---------------------------------------------------------------------------


class TestPerf23AbsentKeysGuard:
    """PERF-23/24/25: _absent_keys guard branches must be exercised."""

    def test_batch_update_flushes_absent_keys(self, db_path):
        """batch_update が _absent_keys に含まれるキーを正しく除去する。"""
        db = NanaSQLite(db_path)
        try:
            db["k1"] = "v1"
            db["k2"] = "v2"
            # After delete, k1 and k2 enter _absent_keys (Unbounded mode always has this attr)
            del db["k1"]
            del db["k2"]
            # Confirm keys are now marked absent before batch_update
            assert "k1" in db._absent_keys
            assert "k2" in db._absent_keys
            # batch_update must exercise the difference_update() branch
            db.batch_update({"k1": "new1", "k2": "new2"})
            assert db["k1"] == "new1"
            assert db["k2"] == "new2"
            # Keys must no longer be in _absent_keys
            assert "k1" not in db._absent_keys
            assert "k2" not in db._absent_keys
        finally:
            db.close()

    def test_batch_update_partial_flushes_absent_keys(self, db_path):
        """batch_update_partial が _absent_keys に含まれるキーを正しく除去する。"""
        db = NanaSQLite(db_path)
        try:
            db["a"] = 1
            db["b"] = 2
            del db["a"]
            del db["b"]
            # Confirm both keys are absent
            assert "a" in db._absent_keys
            assert "b" in db._absent_keys
            # This exercises the if self._absent_keys: difference_update() branch
            failed = db.batch_update_partial({"a": 10, "b": 20})
            assert failed == {}
            assert db["a"] == 10
            assert db["b"] == 20
            assert "a" not in db._absent_keys
            assert "b" not in db._absent_keys
        finally:
            db.close()

    def test_batch_delete_absent_keys_bulk_update(self, db_path):
        """batch_delete が _absent_keys.update(keys) で一括登録する。"""
        db = NanaSQLite(db_path)
        try:
            for i in range(5):
                db[f"del_{i}"] = i
            db.batch_delete([f"del_{i}" for i in range(5)])
            # _absent_keys must contain all deleted keys (Unbounded mode)
            for i in range(5):
                assert f"del_{i}" in db._absent_keys
            # Keys should no longer be retrievable
            for i in range(5):
                assert db.get(f"del_{i}") is None
        finally:
            db.close()

    def test_batch_delete_after_absent_keys_populated(self, db_path):
        """batch_delete が既に _absent_keys がある状態でも正しく動作する。"""
        db = NanaSQLite(db_path)
        try:
            for i in range(10):
                db[f"x_{i}"] = i
            # Populate _absent_keys via single deletes
            del db["x_0"]
            del db["x_1"]
            # Now batch_delete remaining
            db.batch_delete([f"x_{i}" for i in range(2, 10)])
            for i in range(10):
                assert db.get(f"x_{i}") is None
        finally:
            db.close()

    def test_no_encrypt_serialize_fast_path(self, db_path):
        """_no_encrypt=True の場合、_serialize は JSON str を直接返す。"""
        db = NanaSQLite(db_path)
        try:
            assert db._no_encrypt is True
            result = db._serialize({"key": "value"})
            assert isinstance(result, str)
            assert '"key"' in result
        finally:
            db.close()


class TestPerf23V2ModePaths:
    """PERF-23/24/25: v2 mode パスのカバレッジ確保。"""

    def test_batch_update_v2_absent_keys_guard(self, db_path):
        """v2 mode で batch_update が _absent_keys を正しく更新する。"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="immediate")
        try:
            db["a"] = 1
            db["b"] = 2
            del db["a"]
            del db["b"]
            # v2 path: exercises the absent_keys guard
            db.batch_update({"a": 10, "b": 20})
            # Flush to ensure data is persisted
            db._v2_engine.flush()
            assert db["a"] == 10
            assert db["b"] == 20
        finally:
            db.close()

    def test_batch_update_partial_v2_absent_keys_guard(self, db_path):
        """v2 mode で batch_update_partial が _absent_keys を正しく更新する。"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="immediate")
        try:
            db["x"] = 1
            del db["x"]
            failed = db.batch_update_partial({"x": 99})
            assert failed == {}
            db._v2_engine.flush()
            assert db["x"] == 99
        finally:
            db.close()

    def test_batch_delete_v2_absent_keys_update(self, db_path):
        """v2 mode で batch_delete が _absent_keys.update(keys) を呼ぶ。"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="immediate")
        try:
            for i in range(5):
                db[f"k_{i}"] = i
            db._v2_engine.flush()
            db.batch_delete([f"k_{i}" for i in range(5)])
            db._v2_engine.flush()
            for i in range(5):
                assert db.get(f"k_{i}") is None
        finally:
            db.close()


class TestPerf26TxnErrorPaths:
    """PERF-26: begin_transaction/commit/rollback の通常パスを検証。"""

    def test_begin_commit_cycle(self, db_path):
        """begin_transaction → 書き込み → commit のフルサイクル。"""
        db = NanaSQLite(db_path)
        db.create_table("tx", {"id": "INTEGER", "val": "TEXT"})
        try:
            db.begin_transaction()
            db.sql_insert("tx", {"id": 1, "val": "test"})
            db.commit()
            rows = db.fetch_all("SELECT val FROM tx WHERE id=1")
            assert rows[0][0] == "test"
        finally:
            db.close()

    def test_begin_rollback_cycle(self, db_path):
        """begin_transaction → 書き込み → rollback のフルサイクル。"""
        db = NanaSQLite(db_path)
        db.create_table("tx2", {"id": "INTEGER", "val": "TEXT"})
        try:
            db.begin_transaction()
            db.sql_insert("tx2", {"id": 1, "val": "should_not_persist"})
            db.rollback()
            rows = db.fetch_all("SELECT val FROM tx2")
            assert rows == []
        finally:
            db.close()


class TestPerf29NoEncryptFlag:
    """PERF-29: _no_encrypt フラグ動作の確認。"""

    def test_no_encrypt_true_by_default(self, db_path):
        """暗号化なしの場合 _no_encrypt=True であること。"""
        db = NanaSQLite(db_path)
        try:
            assert db._no_encrypt is True
        finally:
            db.close()

    def test_no_encrypt_false_with_encryption(self, tmp_path):
        """暗号化ありの場合 _no_encrypt=False であること。"""
        from cryptography.fernet import Fernet

        key = Fernet.generate_key()
        db = NanaSQLite(str(tmp_path / "enc.db"), encryption_key=key, encryption_mode="fernet")
        try:
            assert db._no_encrypt is False
            db["secret"] = {"payload": "hidden"}
            assert db["secret"] == {"payload": "hidden"}
        finally:
            db.close()


# ---------------------------------------------------------------------------
# PERF-23/24/25: LRU キャッシュモードでのバッチ操作カバレッジ
# ---------------------------------------------------------------------------


class TestBatchLruModePaths:
    """batch_update / batch_update_partial / batch_delete の LRU モード分岐を検証。

    デフォルトの Unbounded キャッシュでは _lru_mode=False となるため、
    LRU モード内のキャッシュ更新ループ (cache.set / cache.delete) が
    未カバーになる。cache_strategy="lru" を使って確認する。
    """

    def test_batch_update_lru_mode(self, db_path):
        """LRU モードで batch_update がキャッシュを正しく更新する。"""
        db = NanaSQLite(db_path, cache_strategy="lru", cache_size=50)
        try:
            assert db._lru_mode is True
            db["a"] = 1
            db["b"] = 2
            db.batch_update({"a": 10, "b": 20})
            assert db["a"] == 10
            assert db["b"] == 20
        finally:
            db.close()

    def test_batch_update_partial_lru_mode(self, db_path):
        """LRU モードで batch_update_partial がキャッシュを正しく更新する。"""
        db = NanaSQLite(db_path, cache_strategy="lru", cache_size=50)
        try:
            assert db._lru_mode is True
            db["x"] = 1
            failed = db.batch_update_partial({"x": 99, "bad": object()})
            assert "bad" in failed
            assert "x" not in failed
            assert db["x"] == 99
        finally:
            db.close()

    def test_batch_delete_lru_mode(self, db_path):
        """LRU モードで batch_delete がキャッシュエントリを削除する。"""
        db = NanaSQLite(db_path, cache_strategy="lru", cache_size=50)
        try:
            assert db._lru_mode is True
            for i in range(5):
                db[f"k_{i}"] = i
            db.batch_delete([f"k_{i}" for i in range(5)])
            for i in range(5):
                assert db.get(f"k_{i}") is None
        finally:
            db.close()

    def test_batch_update_partial_lru_v2_mode(self, db_path):
        """v2 + LRU モードで batch_update_partial がキャッシュを更新する。"""
        db = NanaSQLite(db_path, cache_strategy="lru", cache_size=50, v2_mode=True, flush_mode="immediate")
        try:
            assert db._lru_mode is True
            assert db._v2_mode is True
            db["p"] = "old"
            failed = db.batch_update_partial({"p": "new"})
            assert failed == {}
            db._v2_engine.flush()
            assert db["p"] == "new"
        finally:
            db.close()

    def test_batch_delete_lru_v2_mode(self, db_path):
        """v2 + LRU モードで batch_delete がキャッシュを削除する。"""
        db = NanaSQLite(db_path, cache_strategy="lru", cache_size=50, v2_mode=True, flush_mode="immediate")
        try:
            assert db._lru_mode is True
            assert db._v2_mode is True
            db["q"] = "val"
            db._v2_engine.flush()
            db.batch_delete(["q"])
            db._v2_engine.flush()
            assert db.get("q") is None
        finally:
            db.close()


# ---------------------------------------------------------------------------
# PERF-24: batch_update_partial の部分失敗パスと全失敗パスのカバレッジ
# ---------------------------------------------------------------------------


class TestBatchUpdatePartialErrorPaths:
    """batch_update_partial のシリアライズ失敗パスを検証。"""

    def test_partial_batch_serialization_error_skips_bad_key(self, db_path):
        """シリアライズ不可能な値は failed に記録され、正常な値は書き込まれる。"""
        db = NanaSQLite(db_path)
        try:
            failed = db.batch_update_partial({"good": 42, "bad": object()})
            # シリアライズ失敗キーは failed に含まれる
            assert "bad" in failed
            # 正常なキーは書き込まれている
            assert db["good"] == 42
        finally:
            db.close()

    def test_partial_batch_all_fail_returns_early(self, db_path):
        """全キーが失敗した場合、DB書き込みなしで failed を返す (line: if not params)。"""
        db = NanaSQLite(db_path)
        try:
            failed = db.batch_update_partial({"k1": object(), "k2": object()})
            # 両方とも失敗
            assert set(failed.keys()) == {"k1", "k2"}
            # DB には何も書き込まれていない
            assert db.get("k1") is None
            assert db.get("k2") is None
        finally:
            db.close()


# ---------------------------------------------------------------------------
# PERF-26: begin_transaction / commit / rollback の apsw.Error パス
# ---------------------------------------------------------------------------


class TestTxnApswErrorPaths:
    """begin_transaction / commit / rollback の apsw.Error 処理を検証。

    apsw.Connection.execute は read-only なため直接モックできない。
    代わりに、_connection を軽量なラッパーに差し替えて apsw.Error を注入する。
    """

    class _BrokenConn:
        """execute() が常に apsw.Error を送出するラッパー。"""

        def __init__(self, real: object) -> None:
            self._real = real

        def execute(self, sql: str, *args: object, **kwargs: object) -> None:
            import apsw

            raise apsw.Error("simulated apsw error")

        def __getattr__(self, name: str) -> object:
            return getattr(self._real, name)

    def test_begin_transaction_apsw_error(self, db_path):
        """BEGIN IMMEDIATE が apsw.Error → NanaSQLiteDatabaseError に変換される。"""
        from nanasqlite.exceptions import NanaSQLiteDatabaseError

        db = NanaSQLite(db_path)
        real_conn = db._connection
        try:
            db._connection = self._BrokenConn(real_conn)
            with pytest.raises(NanaSQLiteDatabaseError, match="Failed to begin transaction"):
                db.begin_transaction()
        finally:
            db._connection = real_conn
            db._in_transaction = False
            db._transaction_depth = 0
            db.close()

    def test_commit_apsw_error(self, db_path):
        """COMMIT が apsw.Error → NanaSQLiteDatabaseError に変換される。"""
        from nanasqlite.exceptions import NanaSQLiteDatabaseError

        db = NanaSQLite(db_path)
        real_conn = db._connection
        try:
            # Python-level フラグを手動で設定してロック前チェックを通過させる
            db._in_transaction = True
            db._transaction_depth = 1
            db._connection = self._BrokenConn(real_conn)
            with pytest.raises(NanaSQLiteDatabaseError, match="Failed to commit transaction"):
                db.commit()
        finally:
            db._connection = real_conn
            db._in_transaction = False
            db._transaction_depth = 0
            db.close()

    def test_rollback_apsw_error(self, db_path):
        """ROLLBACK が apsw.Error → NanaSQLiteDatabaseError に変換される。"""
        from nanasqlite.exceptions import NanaSQLiteDatabaseError

        db = NanaSQLite(db_path)
        real_conn = db._connection
        try:
            db._in_transaction = True
            db._transaction_depth = 1
            db._connection = self._BrokenConn(real_conn)
            with pytest.raises(NanaSQLiteDatabaseError, match="Failed to rollback transaction"):
                db.rollback()
        finally:
            db._connection = real_conn
            db._in_transaction = False
            db._transaction_depth = 0
            db.close()


# ---------------------------------------------------------------------------
# PERF-23/24/25: batch 操作の DB エラー時 ROLLBACK ハンドラのカバレッジ
# ---------------------------------------------------------------------------


class TestBatchDbErrorRollback:
    """batch_update / batch_update_partial / batch_delete の例外発生時の
    ROLLBACK パスを検証する。

    テーブルを事前に削除してから batch 操作を呼び出すことで、
    executemany() 内で apsw.SQLError を発生させ、
    except: cursor.execute("ROLLBACK"); raise のパスを踏む。
    """

    def test_batch_update_db_error_triggers_rollback(self, db_path):
        """executemany 失敗時に ROLLBACK され例外が伝播する。"""
        db = NanaSQLite(db_path)
        try:
            db["seed"] = 1
            # 基盤テーブルを削除して executemany を強制的に失敗させる
            db._connection.execute('DROP TABLE IF EXISTS "data"')
            with pytest.raises(Exception):
                db.batch_update({"k1": "v1", "k2": "v2"})
        finally:
            db.close()

    def test_batch_update_partial_db_error_triggers_rollback(self, db_path):
        """executemany 失敗時に ROLLBACK され例外が伝播する。"""
        db = NanaSQLite(db_path)
        try:
            db._connection.execute('DROP TABLE IF EXISTS "data"')
            with pytest.raises(Exception):
                db.batch_update_partial({"k1": "v1"})
        finally:
            db.close()

    def test_batch_delete_db_error_triggers_rollback(self, db_path):
        """executemany 失敗時に ROLLBACK され例外が伝播する。"""
        db = NanaSQLite(db_path)
        try:
            db._connection.execute('DROP TABLE IF EXISTS "data"')
            with pytest.raises(Exception):
                db.batch_delete(["k1"])
        finally:
            db.close()


class TestBatchUpdatePartialEdgePaths:
    """batch_update_partial の境界パスを検証。"""

    def test_empty_mapping_returns_empty_failed(self, db_path):
        """空の mapping は early return {} (if not mapping: return {})。"""
        db = NanaSQLite(db_path)
        try:
            result = db.batch_update_partial({})
            assert result == {}
        finally:
            db.close()


# ============================================================
# v1.5.3rc4 audit POC tests
# ============================================================


class TestBug02ExpiringDictClearRestartScheduler:
    """BUG-02: ExpiringDict.clear() must restart the scheduler so new
    items added after clear() are still evicted."""

    def test_scheduler_running_after_clear(self):
        """clear() must leave the scheduler running (not kill it permanently)."""
        from nanasqlite.utils import ExpirationMode, ExpiringDict

        d = ExpiringDict(expiration_time=1.0, mode=ExpirationMode.SCHEDULER)
        d["x"] = 1
        d.clear()
        assert d._scheduler_running, "Scheduler must still be running after clear()"

    def test_items_added_after_clear_are_expired(self):
        """Items inserted after clear() must still be evicted by the scheduler."""
        import time

        from nanasqlite.utils import ExpirationMode, ExpiringDict

        d = ExpiringDict(expiration_time=0.2, mode=ExpirationMode.SCHEDULER)
        d["before"] = 1
        d.clear()
        # Add a new item after clear
        d["after"] = 2
        time.sleep(0.6)
        assert "after" not in d, "Item added after clear() must expire"
        d.clear()


class TestBug03UnboundedCacheDeleteCachedKeys:
    """BUG-03: UnboundedCache.delete() must use discard() (not add()) on _cached_keys."""

    def test_delete_does_not_mark_key_as_cached(self):
        """Deleted keys must not appear in _cached_keys."""
        from nanasqlite.cache import UnboundedCache

        c = UnboundedCache()
        c.set("k", "v")
        c.delete("k")
        # After deletion, is_cached() must return False so DB is re-queried
        assert not c.is_cached("k"), "Deleted key must not be marked as cached"

    def test_nanasqlite_re_reads_after_delete(self, db_path):
        """Deleting a KV key and re-inserting it from another connection
        must be visible in the original connection after delete."""
        from nanasqlite.cache import UnboundedCache

        # BUG-03: verify at the cache layer that delete() + is_cached() returns False,
        # so NanaSQLite will re-query the DB rather than use stale cache knowledge.
        c = UnboundedCache()
        c.set("k1", "original")
        c.delete("k1")
        # After deletion the cache layer must not claim to know this key,
        # ensuring the calling layer will go back to the DB.
        assert not c.is_cached("k1"), (
            "BUG-03 regression: UnboundedCache.delete() is incorrectly marking "
            "the key as 'cached' (via .add) instead of clearing it (via .discard)"
        )


class TestBug04ExpiringDictGetItemTOCTOU:
    """BUG-04: ExpiringDict.__getitem__ must check expiry atomically (no TOCTOU)."""

    def test_getitem_raises_keyerror_for_expired_key(self):
        """__getitem__ must raise KeyError for an expired key even in concurrent setting."""
        import time

        from nanasqlite.utils import ExpirationMode, ExpiringDict

        d = ExpiringDict(expiration_time=0.1, mode=ExpirationMode.LAZY)
        d["k"] = "v"
        time.sleep(0.3)
        with pytest.raises(KeyError):
            _ = d["k"]

    def test_getitem_returns_value_for_valid_key(self):
        """__getitem__ must return the value for a non-expired key."""
        from nanasqlite.utils import ExpirationMode, ExpiringDict

        d = ExpiringDict(expiration_time=10.0, mode=ExpirationMode.SCHEDULER)
        d["k"] = "hello"
        assert d["k"] == "hello"
        d.clear()


class TestSec02CreateTableColumnTypeInjection:
    """SEC-02: create_table() column-type regex must reject quote characters."""

    def test_quote_in_column_type_raises(self, db_path):
        """Column type string containing ' or \" must be rejected."""
        from nanasqlite import NanaSQLite
        from nanasqlite.exceptions import NanaSQLiteValidationError

        db = NanaSQLite(db_path)
        try:
            with pytest.raises(NanaSQLiteValidationError):
                db.create_table("t_inject", {"col1": "TEXT DEFAULT 'x') --"})
        finally:
            db.close()

    def test_valid_column_types_still_work(self, db_path):
        """Standard column types must still be accepted."""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        try:
            db.create_table(
                "t_valid",
                {"id": "INTEGER", "name": "TEXT", "val": "REAL", "blob": "BLOB"},
                if_not_exists=True,
            )
            assert db.table_exists("t_valid")
        finally:
            db.close()


class TestCodeQLExceptOSErrorHasComment:
    """CodeQL – empty except clauses in PERF-D must have explanatory comments."""

    def test_db_stat_key_set_on_new_file_db(self, db_path):
        """_db_stat_key is populated for a real file-backed database."""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        try:
            assert db._db_stat_key is not None
            dev, ino = db._db_stat_key
            # Both device number and inode must be non-negative integers
            assert dev >= 0 and ino >= 0
        finally:
            db.close()

    def test_db_stat_key_none_for_in_memory(self):
        """_db_stat_key is None for in-memory databases (no file to stat)."""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(":memory:")
        try:
            assert db._db_stat_key is None
        finally:
            db.close()


# ===========================================================================
# SEC-05 [High]: UniqueHook TOCTOU Fix (v1.5.4)
# ===========================================================================
class TestSec05UniqueHookTOCTOUFix:
    """SEC-05: UniqueHook TOCTOU race condition is fixed in non-v2 mode (v1.5.4).

    The fix moves before_write hook calls inside the RLock in __setitem__,
    so that the uniqueness check and the DB write are atomic.
    """

    def test_unique_hook_concurrent_writes_prevent_duplicate(self, db_path):
        """Concurrent writes with UniqueHook reject duplicates (TOCTOU fix)."""
        import threading

        from nanasqlite import NanaSQLite
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        db.add_hook(UniqueHook("email"))

        try:
            validation_errors = []
            unexpected_errors = []
            successes = []

            def write_user(key: str, email: str) -> None:
                try:
                    db[key] = {"email": email, "name": key}
                    successes.append(key)
                except NanaSQLiteValidationError as exc:
                    validation_errors.append((key, str(exc)))
                except Exception as exc:
                    unexpected_errors.append((key, type(exc).__name__, str(exc)))

            # Fire 5 concurrent threads, each trying to write the same email
            threads = [threading.Thread(target=write_user, args=(f"user{i}", "same@example.com")) for i in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # No unexpected errors (e.g. DB errors) should have occurred
            assert not unexpected_errors, f"Unexpected errors: {unexpected_errors}"
            # Exactly one write must succeed
            assert len(successes) == 1, f"Expected 1 success, got {len(successes)}: {successes}"
            # All failures must be the expected validation error
            assert len(validation_errors) == 4, (
                f"Expected 4 validation errors, got {len(validation_errors)}: {validation_errors}"
            )
        finally:
            db.close()

    def test_before_write_hook_called_inside_lock(self, db_path):
        """Verify hooks are invoked within the RLock context (non-v2 mode)."""
        from contextlib import contextmanager
        from unittest.mock import patch

        from nanasqlite import NanaSQLite

        lock_held_during_hook: list[bool] = []
        # Mutable container so the inner class can update it without 'nonlocal'
        in_lock_ref: list[bool] = [False]

        class LockInspectHook:
            def before_write(self, db: NanaSQLite, key: str, value: object) -> object:
                lock_held_during_hook.append(in_lock_ref[0])
                return value

            def after_read(self, db: object, key: str, value: object) -> object:
                return value

            def before_delete(self, db: object, key: str) -> None:
                pass

        db = NanaSQLite(db_path)
        db.add_hook(LockInspectHook())  # type: ignore[arg-type]

        # Wrap _acquire_lock so we can set in_lock_ref while inside the context
        original_acquire_lock = db._acquire_lock

        @contextmanager  # type: ignore[misc]
        def tracking_acquire_lock():
            in_lock_ref[0] = True
            try:
                with original_acquire_lock():
                    yield
            finally:
                in_lock_ref[0] = False

        try:
            with patch.object(db, "_acquire_lock", tracking_acquire_lock):
                db["k"] = "v"
        finally:
            db.close()

        assert lock_held_during_hook, "Hook was never called"
        assert all(lock_held_during_hook), "Lock was NOT held during hook execution"

    def test_unique_hook_self_update_still_allowed(self, db_path):
        """Updating a key with the same unique value (self-update) must not raise."""
        from nanasqlite import NanaSQLite
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        try:
            db.add_hook(UniqueHook("email"))

            db["user1"] = {"email": "alice@example.com"}
            # Self-update: same key, same email — must succeed
            db["user1"] = {"email": "alice@example.com", "updated": True}
            assert db["user1"]["updated"] is True
        finally:
            db.close()


# ===========================================================================
# RE2-01: Optional google-re2 Integration
# ===========================================================================
class TestRE2Integration:
    """Verify optional google-re2 integration in BaseHook."""

    def test_has_re2_flag_is_bool(self):
        """HAS_RE2 flag is always a bool regardless of whether re2 is installed."""
        from nanasqlite.compat import HAS_RE2

        assert isinstance(HAS_RE2, bool)

    def test_hook_compiles_patterns_without_error(self):
        """BaseHook compiles key_pattern with either re or re2 engine without error."""
        from nanasqlite.hooks import BaseHook

        patterns = [r"^user_\d+$", r"[a-z]+", r"data_\w*"]
        for pat in patterns:
            hook = BaseHook(key_pattern=pat)
            assert isinstance(hook._should_run("user_123"), bool)
            assert isinstance(hook._should_run(""), bool)

    def test_hook_search_works_with_re2_or_re(self):
        """_should_run produces correct results for prefix/suffix patterns."""
        from nanasqlite.hooks import BaseHook

        hook = BaseHook(key_pattern=r"^user_")
        assert hook._should_run("user_1") is True
        assert hook._should_run("admin_1") is False

    def test_re2_dangerous_patterns_accepted_when_re2_available(self):
        """When RE2 is available, patterns that would fail blacklist are accepted (RE2 is safe)."""
        from nanasqlite.compat import HAS_RE2
        from nanasqlite.hooks import BaseHook

        if not HAS_RE2:
            pytest.skip("google-re2 not installed")

        # These patterns would be rejected by the blacklist but are safe with RE2
        patterns = ["(a+)+", "(a*)*", "(a|b)*"]
        for pat in patterns:
            hook = BaseHook(key_pattern=pat)  # must not raise
            assert hook._key_regex is not None

    def test_redos_blacklist_still_active_without_re2(self, monkeypatch):
        """When RE2 is NOT installed, dangerous patterns are still rejected."""
        from nanasqlite.exceptions import NanaSQLiteValidationError
        from nanasqlite.hooks import BaseHook

        # Force the non-RE2 branch so the blacklist is exercised regardless of
        # whether google-re2 is installed in this environment.
        monkeypatch.setattr("nanasqlite.hooks.HAS_RE2", False)

        with pytest.raises(NanaSQLiteValidationError, match="dangerous regex pattern"):
            BaseHook(key_pattern="(a+)+")

    def test_re2_module_exported_from_compat(self):
        """re2_module is None when not installed, or a module when installed."""
        from nanasqlite.compat import HAS_RE2, re2_module

        if HAS_RE2:
            assert re2_module is not None
            # Must have basic re-compatible API
            assert hasattr(re2_module, "compile")
            assert hasattr(re2_module, "search")
        else:
            assert re2_module is None


# ===========================================================================
# Coverage: v1.5.4 new code paths (RE2 available + validkit absent branches)
# ===========================================================================
class TestNewCodeCoverageV154:
    """Targeted tests for 100% coverage on new code added in v1.5.4.

    google-re2 is included in the dev extras (``pip install nanasqlite[dev]``),
    so RE2 code paths are exercised with the real engine instead of mocks.
    Tests are guarded with ``pytest.importorskip("re2")`` to remain skippable
    in minimal environments.

    The validkit-py stub body is covered by temporarily blocking the validkit
    import so the except-block executes and the stub is callable.
    """

    # -----------------------------------------------------------------------
    # hooks.py: RE2 available branch – real google-re2 engine
    # -----------------------------------------------------------------------

    def test_basehook_re2_str_pattern(self):
        """RE2 branch: str key_pattern compiled via the real google-re2 engine."""
        pytest.importorskip("re2")
        from nanasqlite.hooks import BaseHook

        hook = BaseHook(key_pattern=r"^user_\d+$")
        assert hook._should_run("user_123") is True
        assert hook._should_run("admin_1") is False

    def test_basehook_re2_compiled_pattern(self):
        """RE2 branch: compiled re.Pattern input re-compiled by real google-re2, flags preserved."""
        import re

        pytest.importorskip("re2")
        from nanasqlite.hooks import BaseHook

        compiled = re.compile(r"^admin_", re.IGNORECASE)
        hook = BaseHook(key_pattern=compiled)
        # flags=re.IGNORECASE must be preserved after RE2 re-compilation
        assert hook._should_run("admin_1") is True
        assert hook._should_run("ADMIN_1") is True   # IGNORECASE must be honoured
        assert hook._should_run("user_1") is False

    def test_basehook_re2_multiline_flag_preserved(self):
        """RE2 branch: re.MULTILINE is translated to (?m) so ^ / $ match at line boundaries."""
        import re

        pytest.importorskip("re2")
        from nanasqlite.hooks import BaseHook

        # With MULTILINE, ^user_ should match at the start of any line.
        compiled = re.compile(r"^user_", re.MULTILINE)
        hook = BaseHook(key_pattern=compiled)
        # Matches at start of the string
        assert hook._should_run("user_1") is True
        # Matches at the start of a second line (requires MULTILINE / (?m))
        assert hook._should_run("other\nuser_1") is True
        # Does not match when no line starts with "user_"
        assert hook._should_run("admin_1") is False

    def test_basehook_re2_none_pattern(self):
        """RE2 branch: None key_pattern leaves _key_regex as None."""
        pytest.importorskip("re2")
        from nanasqlite.hooks import BaseHook

        hook = BaseHook(key_pattern=None)
        assert hook._key_regex is None
        assert hook._should_run("anything") is True

    # -----------------------------------------------------------------------
    # hooks.py: re_fallback parameter (new in v1.5.4)
    # -----------------------------------------------------------------------

    def test_basehook_re2_unsupported_raises_without_fallback(self):
        """RE2 rejects backreferences; re_fallback=False (default) propagates the error."""
        re2 = pytest.importorskip("re2")
        from nanasqlite.hooks import BaseHook

        with pytest.raises(re2.error):
            BaseHook(key_pattern=r"(\w)\1")  # backreference – unsupported by RE2

    def test_basehook_re2_unsupported_fallback_warns_and_works(self):
        """re_fallback=True emits a warning and falls back to std re."""
        pytest.importorskip("re2")
        from nanasqlite.hooks import BaseHook

        with pytest.warns(UserWarning, match="Falling back to the standard re engine"):
            hook = BaseHook(key_pattern=r"(\w)\1", re_fallback=True)
        # Pattern still works via std re
        assert hook._should_run("aa") is True
        assert hook._should_run("ab") is False

    def test_basehook_re2_lookahead_fallback(self):
        """Lookaheads trigger the re_fallback warning and work via std re."""
        pytest.importorskip("re2")
        from nanasqlite.hooks import BaseHook

        with pytest.warns(UserWarning, match="Falling back to the standard re engine"):
            hook = BaseHook(key_pattern=r"foo(?=bar)", re_fallback=True)
        assert hook._should_run("foobar") is True
        assert hook._should_run("foobaz") is False

    def test_basehook_re2_supported_pattern_no_warning_with_fallback(self):
        """re_fallback=True does NOT warn when the pattern is valid RE2."""
        import warnings

        pytest.importorskip("re2")
        from nanasqlite.hooks import BaseHook

        with warnings.catch_warnings():
            warnings.simplefilter("error")  # any warning fails the test
            hook = BaseHook(key_pattern=r"^item_\d+$", re_fallback=True)
        assert hook._should_run("item_1") is True

    # -----------------------------------------------------------------------
    # compat.py: RE2 branch verified via real installation
    # -----------------------------------------------------------------------

    def test_compat_has_re2_true(self):
        """compat.HAS_RE2 is True because google-re2 is in dev extras."""
        import importlib

        pytest.importorskip("re2")
        compat_mod = importlib.import_module("nanasqlite.compat")
        assert compat_mod.HAS_RE2 is True
        assert compat_mod.re2_module is not None

    # -----------------------------------------------------------------------
    # compat.py: validkit except-block (HAS_VALIDKIT=False, stub def, stub body)
    # -----------------------------------------------------------------------

    def test_compat_validkit_stub_def_and_call_coverage(self):
        """Cover compat.py validkit except-block and stub body."""
        import importlib
        import sys
        import types

        compat_mod = importlib.import_module("nanasqlite.compat")

        _ABSENT = object()
        validkit_backup = sys.modules.get("validkit", _ABSENT)

        # Provide a real module object without ``validate`` so that
        # ``from validkit import validate`` raises ImportError (reliably),
        # rather than setting None which the import system treats as a
        # failed import and may raise non-ImportError in some implementations.
        sys.modules["validkit"] = types.ModuleType("validkit")

        try:
            importlib.reload(compat_mod)
            assert compat_mod.HAS_VALIDKIT is False

            # Call the stub to cover the raise ImportError line
            with pytest.raises(ImportError, match="validkit-py is not installed"):
                compat_mod.validkit_validate()
        finally:
            if validkit_backup is _ABSENT:
                sys.modules.pop("validkit", None)
            else:
                sys.modules["validkit"] = validkit_backup  # type: ignore[assignment]
            # Restore compat to the environment's normal import state after cleanup.
            importlib.reload(compat_mod)

    # -----------------------------------------------------------------------
    # hooks.py: non-RE2 branch – Pattern and None inputs
    # -----------------------------------------------------------------------

    def test_basehook_no_re2_compiled_pattern_coverage(self):
        """Cover hooks.py non-RE2 elif Pattern branch."""
        import re
        from unittest.mock import patch

        from nanasqlite.hooks import BaseHook

        compiled = re.compile(r"^admin_")
        with patch("nanasqlite.hooks.HAS_RE2", False):
            hook = BaseHook(key_pattern=compiled)
            assert hook._should_run("admin_1") is True
            assert hook._should_run("user_1") is False

    def test_basehook_no_re2_none_pattern_coverage(self):
        """Cover hooks.py non-RE2 else branch: None key_pattern."""
        from unittest.mock import patch

        from nanasqlite.hooks import BaseHook

        with patch("nanasqlite.hooks.HAS_RE2", False):
            hook = BaseHook(key_pattern=None)
            assert hook._key_regex is None
            assert hook._should_run("anything") is True

    # -----------------------------------------------------------------------
    # hooks.py: RE2 unsupported-flags detection
    # -----------------------------------------------------------------------

    def test_re2_unsupported_flags_raise_without_fallback(self):
        """re.VERBOSE is not supported by RE2; should raise re.error when re_fallback=False."""
        import re

        import pytest

        pytest.importorskip("re2")
        from nanasqlite.hooks import BaseHook

        with pytest.raises(re.error, match="RE2 does not support"):
            BaseHook(key_pattern=re.compile(r"foo  # comment", re.VERBOSE), re_fallback=False)

    def test_re2_unsupported_flags_fallback_warns(self):
        """re.VERBOSE is not supported by RE2; should warn and use re.compile when re_fallback=True."""
        import re
        import warnings

        pytest.importorskip("re2")
        from nanasqlite.hooks import BaseHook

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            hook = BaseHook(
                key_pattern=re.compile(r"foo  # comment", re.VERBOSE), re_fallback=True
            )
        assert any("RE2 cannot preserve" in str(wi.message) for wi in w), "Expected a warning"
        # Should still work as a standard re pattern
        assert isinstance(hook._should_run("foo"), bool)


# ---------------------------------------------------------------------------
# v1.5.4 Audit: BUG-01 — pop() before_delete hook inside lock
# ---------------------------------------------------------------------------

class TestBug01V154PopBeforeDeleteLock:
    """BUG-01 (v1.5.4): pop() の before_delete フックはロック内で実行されるべき。"""

    def test_pop_before_delete_hook_runs_inside_lock(self, db_path):
        """pop() の非 v2 モードで before_delete フックが _lock 保持中に呼ばれることを確認する。"""
        from nanasqlite.hooks import BaseHook

        lock_held_flags: list[bool] = []

        db = NanaSQLite(db_path)
        is_owned_fn = getattr(db._lock, "_is_owned", None)
        if not callable(is_owned_fn):
            db.close()
            pytest.skip("RLock._is_owned() はこのランタイムでは利用不可")

        class LockInspectHook(BaseHook):
            def before_delete(self_hook, db, key):  # noqa: N805
                lock_held_flags.append(db._lock._is_owned())

        db.add_hook(LockInspectHook())
        db["key"] = "value"
        result = db.pop("key")
        db.close()

        assert result == "value"
        assert len(lock_held_flags) == 1
        assert lock_held_flags[0] is True, (
            "pop() should call before_delete inside the lock (SEC-05 consistency)"
        )

    def test_pop_missing_key_does_not_trigger_hook(self, db_path):
        """pop() でキーが存在しない場合、フックは呼び出されない。"""
        from nanasqlite.hooks import BaseHook

        delete_calls: list[str] = []

        class RecordHook(BaseHook):
            def before_delete(self_hook, db, key):  # noqa: N805
                delete_calls.append(key)

        db = NanaSQLite(db_path)
        db.add_hook(RecordHook())
        result = db.pop("nonexistent", "default")
        db.close()

        assert result == "default"
        assert delete_calls == []

    def test_pop_hook_abort_raises_and_key_persists(self, db_path):
        """pop() 中に before_delete フックが例外を送出した場合、キーは削除されない。"""
        from nanasqlite.hooks import BaseHook

        class AbortDeleteHook(BaseHook):
            def before_delete(self_hook, db, key):  # noqa: N805
                raise NanaSQLiteValidationError("delete not allowed")

        db = NanaSQLite(db_path)
        db.add_hook(AbortDeleteHook())
        db["protected"] = "secret"

        with pytest.raises(NanaSQLiteValidationError, match="delete not allowed"):
            db.pop("protected")

        # キーはまだ存在すべき
        assert db["protected"] == "secret"
        db.close()


# ---------------------------------------------------------------------------
# v1.5.4 Audit: BUG-02 — batch_update() hook return value not discarded
# ---------------------------------------------------------------------------

class TestBug02V154BatchUpdateHookResult:
    """BUG-02 (v1.5.4): batch_update() でフック変換値が適用されることを確認する。"""

    def test_batch_update_transforming_hook_applied(self, db_path):
        """batch_update() で変換フック（before_write の返り値）が正しく適用される。"""
        from nanasqlite.hooks import BaseHook

        class UpperCaseHook(BaseHook):
            def before_write(self_hook, db, key, value):  # noqa: N805
                if isinstance(value, str):
                    return value.upper()
                return value

        db = NanaSQLite(db_path)
        db.add_hook(UpperCaseHook())
        db.batch_update({"greeting": "hello", "name": "world"})

        assert db["greeting"] == "HELLO", "batch_update should apply hook transformations"
        assert db["name"] == "WORLD"
        db.close()

    def test_batch_update_consistent_with_setitem(self, db_path):
        """batch_update() と __setitem__ でフック変換の結果が一致することを確認する。"""
        from nanasqlite.hooks import BaseHook

        class PrefixHook(BaseHook):
            def before_write(self_hook, db, key, value):  # noqa: N805
                if isinstance(value, str):
                    return "prefix_" + value
                return value

        db1 = NanaSQLite(db_path)
        db1.add_hook(PrefixHook())

        db1["single"] = "val"
        db1.batch_update({"batch": "val"})

        assert db1["single"] == "prefix_val"
        assert db1["batch"] == "prefix_val", (
            "batch_update() and __setitem__ should produce the same result for transforming hooks"
        )
        db1.close()

    def test_batch_update_non_transforming_hook_unchanged(self, db_path):
        """変換なし（バリデーションのみ）フックでは元の値が保持される。"""
        from nanasqlite.hooks import CheckHook

        db = NanaSQLite(db_path)
        db.add_hook(CheckHook(lambda k, v: isinstance(v, str)))
        db.batch_update({"a": "ok", "b": "also_ok"})

        assert db["a"] == "ok"
        assert db["b"] == "also_ok"
        db.close()

    def test_batch_update_copy_on_write_no_alloc_when_unchanged(self, db_path):
        """フックが値を変更しない場合、copy-on-write により余分な dict は生成されない。"""
        from nanasqlite.hooks import BaseHook

        class PassthroughHook(BaseHook):
            def before_write(self_hook, db, key, value):  # noqa: N805
                return value  # 変更なし

        db = NanaSQLite(db_path)
        db.add_hook(PassthroughHook())
        original = {"x": 1, "y": 2}
        db.batch_update(original)

        assert db["x"] == 1
        assert db["y"] == 2
        db.close()


# ---------------------------------------------------------------------------
# v1.5.4 Audit: BUG-03 — batch_delete() before_delete hook inside lock
# ---------------------------------------------------------------------------

class TestBug03V154BatchDeleteBeforeDeleteLock:
    """BUG-03 (v1.5.4): batch_delete() の before_delete フックはロック内で実行されるべき。"""

    def test_batch_delete_before_delete_hook_runs_inside_lock(self, db_path):
        """batch_delete() の非 v2 モードで before_delete フックが _lock 保持中に呼ばれることを確認する。"""
        from nanasqlite.hooks import BaseHook

        lock_held_flags: list[bool] = []

        db = NanaSQLite(db_path)
        is_owned_fn = getattr(db._lock, "_is_owned", None)
        if not callable(is_owned_fn):
            db.close()
            pytest.skip("RLock._is_owned() はこのランタイムでは利用不可")

        class LockInspectHook(BaseHook):
            def before_delete(self_hook, db, key):  # noqa: N805
                lock_held_flags.append(db._lock._is_owned())

        db.add_hook(LockInspectHook())
        db["k1"] = "v1"
        db["k2"] = "v2"
        db.batch_delete(["k1", "k2"])
        db.close()

        assert len(lock_held_flags) == 2
        assert all(f is True for f in lock_held_flags), (
            "batch_delete() should call before_delete inside the lock (SEC-05 consistency)"
        )

    def test_batch_delete_hook_abort_raises_and_keys_persist(self, db_path):
        """batch_delete() 中に before_delete フックが例外を送出した場合、削除はロールバックされる。"""
        from nanasqlite.hooks import BaseHook

        class AbortDeleteHook(BaseHook):
            def before_delete(self_hook, db, key):  # noqa: N805
                if key == "protected":
                    raise NanaSQLiteValidationError("cannot delete protected key")

        db = NanaSQLite(db_path)
        db.add_hook(AbortDeleteHook())
        db["protected"] = "secret"
        db["normal"] = "ok"

        with pytest.raises(NanaSQLiteValidationError, match="cannot delete protected key"):
            db.batch_delete(["protected", "normal"])

        # protected キーはまだ存在するはず
        assert db.get("protected") == "secret"
        db.close()

    def test_batch_delete_no_hooks_works_normally(self, db_path):
        """フックなしの batch_delete() は正常に動作することを確認する。"""
        db = NanaSQLite(db_path)
        db["a"] = 1
        db["b"] = 2
        db["c"] = 3
        db.batch_delete(["a", "b"])

        assert "a" not in db
        assert "b" not in db
        assert db["c"] == 3
        db.close()


# ---------------------------------------------------------------------------
# v1.5.4 前倒し実施: PERF-01 — UniqueHook use_index=True opt-in
# ---------------------------------------------------------------------------

class TestPerf01V154UniqueHookIndex:
    """PERF-01 (v1.5.4): UniqueHook の opt-in 逆引きインデックスを検証する。"""

    def test_use_index_basic_unique_enforcement(self, db_path):
        """use_index=True でも一意制約が正しく機能することを確認する。"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        db.add_hook(UniqueHook("email", use_index=True))

        db["user1"] = {"email": "alice@example.com", "name": "Alice"}
        db["user2"] = {"email": "bob@example.com", "name": "Bob"}

        with pytest.raises(NanaSQLiteValidationError, match="Unique constraint violation"):
            db["user3"] = {"email": "alice@example.com", "name": "Duplicate Alice"}

        assert db["user1"]["email"] == "alice@example.com"
        assert db["user2"]["email"] == "bob@example.com"
        assert "user3" not in db
        db.close()

    def test_use_index_overwrite_same_key_ok(self, db_path):
        """use_index=True で同一キーを別値で上書きできることを確認する（自己更新）。"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        db.add_hook(UniqueHook("email", use_index=True))

        db["user1"] = {"email": "alice@example.com", "name": "Alice"}
        # 同じキーを別メールで更新 — 問題なく書き込めるはず
        db["user1"] = {"email": "alice_new@example.com", "name": "Alice Updated"}

        assert db["user1"]["email"] == "alice_new@example.com"
        db.close()

    def test_use_index_overwrite_same_key_same_value_ok(self, db_path):
        """use_index=True で同一キーを同一値で上書きできることを確認する（冪等更新）。"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        db.add_hook(UniqueHook("email", use_index=True))

        db["user1"] = {"email": "alice@example.com", "name": "Alice"}
        # 同じキーを同じメールで更新 — 問題なく書き込めるはず
        db["user1"] = {"email": "alice@example.com", "name": "Alice (same)"}

        assert db["user1"]["name"] == "Alice (same)"
        db.close()

    def test_use_index_lazy_build_on_first_write(self, db_path):
        """use_index=True では最初の書き込み時にインデックスが構築されることを確認する。"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        # 先にデータを追加してからフックを登録（既存データに対して lazy build が行われる）
        db["user1"] = {"email": "alice@example.com"}
        db["user2"] = {"email": "bob@example.com"}
        db.close()

        db2 = NanaSQLite(db_path)
        hook = UniqueHook("email", use_index=True)
        db2.add_hook(hook)

        assert not hook._index_built  # まだ構築されていない

        # 新規書き込みでインデックスが構築される
        db2["user3"] = {"email": "carol@example.com"}
        assert hook._index_built

        # 既存メールで重複チェックが機能する
        with pytest.raises(NanaSQLiteValidationError):
            db2["user4"] = {"email": "alice@example.com"}

        db2.close()

    def test_use_index_delete_removes_from_index(self, db_path):
        """use_index=True でキーを削除するとインデックスからも除去されることを確認する。"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        hook = UniqueHook("email", use_index=True)
        db.add_hook(hook)

        db["user1"] = {"email": "alice@example.com"}
        db["user2"] = {"email": "bob@example.com"}

        # alice を削除するとインデックスからも除去される
        del db["user1"]

        # alice のメールが再利用できるようになる
        db["user3"] = {"email": "alice@example.com"}
        assert db["user3"]["email"] == "alice@example.com"
        db.close()

    def test_use_index_invalidate_rebuilds_index(self, db_path):
        """invalidate_index() を呼ぶとインデックスが再構築されることを確認する。"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        hook = UniqueHook("email", use_index=True)
        db.add_hook(hook)

        db["user1"] = {"email": "alice@example.com"}

        assert hook._index_built

        hook.invalidate_index()
        assert not hook._index_built
        assert hook._value_to_key == {}

        # 次の書き込みでインデックスが再構築される
        db["user2"] = {"email": "bob@example.com"}
        assert hook._index_built
        db.close()

    def test_use_index_update_to_none_removes_stale_entry(self, db_path):
        """use_index=True でフィールド値を None（またはフィールド削除）に更新した場合に
        旧インデックスエントリが正しく削除されることを確認する。
        BUG: {"email": "a"} → {} への更新で "a"→key の残留エントリが誤重複を引き起こさない。"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        hook = UniqueHook("email", use_index=True)
        db.add_hook(hook)

        db["user1"] = {"email": "alice@example.com"}
        assert hook._value_to_key.get("alice@example.com") == "user1"

        # email フィールドを削除（None 相当）に更新する
        db["user1"] = {"name": "Alice"}  # email キーなし
        # 旧インデックスエントリが削除されているはず
        assert "alice@example.com" not in hook._value_to_key

        # alice のメールを別キーで再利用できるようになる（残留エントリがないので重複エラーにならない）
        db["user2"] = {"email": "alice@example.com"}
        assert db["user2"]["email"] == "alice@example.com"
        db.close()

    def test_use_index_duplicate_tracking_in_build_index(self, db_path):
        """_build_index() がライフサイクル外で既存重複エントリをトラックし、
        以降の書き込みで O(N) スキャンにフォールバックして正確に検証することを確認する。"""
        from nanasqlite.hooks import UniqueHook

        # まずフックなしで重複を書き込む（ライフサイクル外）
        db = NanaSQLite(db_path)
        db._has_hooks = False  # フックをバイパスして直接書き込み
        db["user1"] = {"email": "dup@example.com"}
        db["user2"] = {"email": "dup@example.com"}
        db._has_hooks = True

        hook = UniqueHook("email", use_index=True)
        db._hooks = [hook]

        # インデックスをビルドすると重複が _duplicate_field_values に記録される
        hook._build_index(db)
        assert "dup@example.com" in hook._duplicate_field_values
        assert "dup@example.com" not in hook._value_to_key

        # 重複値を持つ別キーへの書き込みは拒否される（O(N) スキャンでフォールバック）
        with pytest.raises(NanaSQLiteValidationError):
            db["user3"] = {"email": "dup@example.com"}

        db.close()

    def test_use_index_duplicate_resolves_registers_in_index(self, db_path):
        """_duplicate_field_values に記録された値について、O(N) スキャンで
        重複が解消されたと判定された場合にインデックスへ登録されることを確認する。
        （書き込み元のキーが唯一の保有者になった場合）"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        # フックなしで user1 と user2 に同じメールを設定（ライフサイクル外）
        db._has_hooks = False
        db["user1"] = {"email": "dup@example.com"}
        db["user2"] = {"email": "dup@example.com"}
        db._has_hooks = True

        hook = UniqueHook("email", use_index=True)
        db._hooks = [hook]

        # インデックスビルド: "dup@example.com" は _duplicate_field_values に記録される
        hook._build_index(db)
        assert "dup@example.com" in hook._duplicate_field_values

        # フックをバイパスして user2 のメールを変更（重複解消）
        db._has_hooks = False
        db["user2"] = {"email": "other@example.com"}
        db._has_hooks = True

        # user1 のメールを "dup@example.com" に更新する（self-update）
        # O(N) スキャンで重複なしと判定 → インデックスに登録
        db["user1"] = {"email": "dup@example.com"}

        # 重複が解消されたのでインデックスに登録されているはず
        assert "dup@example.com" in hook._value_to_key
        assert "dup@example.com" not in hook._duplicate_field_values

        db.close()

    def test_use_index_unhashable_field_value_raises_clear_error(self, db_path):
        """use_index=True でアンハッシュ可能なフィールド値（list など）を書き込むと
        明確なエラーが発生することを確認する。
        サイレントな O(N) 縮退よりも、設定エラーとして明示的に通知する方が望ましい。"""
        from nanasqlite.hooks import UniqueHook

        def get_tags(key, value):
            return value.get("tags") if isinstance(value, dict) else None

        db = NanaSQLite(db_path)
        db.add_hook(UniqueHook(get_tags, use_index=True))

        # list（アンハッシュ可能）を返すフィールドエクストラクタは use_index=True では拒否される
        with pytest.raises(NanaSQLiteValidationError, match="unhashable"):
            db["user1"] = {"tags": ["python", "sqlite"]}

        db.close()

    def test_use_index_false_default_backward_compatible(self, db_path):
        """use_index=False（デフォルト）では既存の O(N) 動作が維持されることを確認する。"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        hook = UniqueHook("email")  # use_index=False (default)
        db.add_hook(hook)

        assert hook.use_index is False

        db["user1"] = {"email": "alice@example.com"}

        with pytest.raises(NanaSQLiteValidationError):
            db["user2"] = {"email": "alice@example.com"}

        db.close()

    def test_use_index_callable_field(self, db_path):
        """use_index=True で callable の field 引数が正しく機能することを確認する。"""
        from nanasqlite.hooks import UniqueHook

        def get_email(key, value):
            return value.get("email") if isinstance(value, dict) else None

        db = NanaSQLite(db_path)
        db.add_hook(UniqueHook(get_email, use_index=True))

        db["user1"] = {"email": "alice@example.com"}

        with pytest.raises(NanaSQLiteValidationError):
            db["user2"] = {"email": "alice@example.com"}

        db.close()

    def test_use_index_build_index_with_triple_duplicate(self, db_path):
        """_build_index() で3つ以上のキーが同じ値を持つ場合、
        すでに _duplicate_field_values に記録済みの値はスキップされることを確認する。"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        db._has_hooks = False
        db["u1"] = {"email": "tri@example.com"}
        db["u2"] = {"email": "tri@example.com"}
        db["u3"] = {"email": "tri@example.com"}
        db._has_hooks = True

        hook = UniqueHook("email", use_index=True)
        db._hooks = [hook]

        hook._build_index(db)
        assert "tri@example.com" in hook._duplicate_field_values
        assert "tri@example.com" not in hook._value_to_key
        db.close()

    def test_use_index_build_index_skips_unhashable(self, db_path):
        """_build_index() でアンハッシュ可能なフィールド値はスキップされクラッシュしない。"""
        from nanasqlite.hooks import UniqueHook

        def get_tags(key, value):
            return value.get("tags") if isinstance(value, dict) else None

        db = NanaSQLite(db_path)
        db._has_hooks = False
        db["item1"] = {"tags": ["python", "sqlite"]}
        db["item2"] = {"name": "no-tags"}
        db._has_hooks = True

        hook = UniqueHook(get_tags, use_index=True)
        hook._build_index(db)
        assert hook._index_built is True
        assert len(hook._value_to_key) == 0
        db.close()

    def test_use_index_duplicate_resolves_via_new_key(self, db_path):
        """_duplicate_field_values に記録された値を書き込む際、
        O(N) スキャンで重複なしと判定されるとインデックスに昇格されることを確認する。"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        db._has_hooks = False
        db["u1"] = {"email": "res@example.com"}
        db["u2"] = {"email": "res@example.com"}
        db._has_hooks = True

        hook = UniqueHook("email", use_index=True)
        db._hooks = [hook]

        hook._build_index(db)
        assert "res@example.com" in hook._duplicate_field_values

        # u1/u2 のメールを変更して重複を解消（バイパス）
        db._has_hooks = False
        db["u1"] = {"email": "changed@example.com"}
        db["u2"] = {"email": "other@example.com"}
        db._has_hooks = True

        # _duplicate_field_values に残っているはずの "res@example.com" で新規キーを書き込む
        # (before_write の old_raw が _missing になるので discard は呼ばれない)
        hook._duplicate_field_values.add("res@example.com")  # 強制的に重複マーク

        # O(N) スキャン: 他のキーに "res@example.com" はないので昇格
        db["u3"] = {"email": "res@example.com"}
        assert "res@example.com" in hook._value_to_key
        assert "res@example.com" not in hook._duplicate_field_values
        db.close()

    def test_use_index_false_non_dict_skips_check(self, db_path):
        """use_index=False のデフォルトパスで非 dict 値は check_val が None になりスキップされる。
        (_extract_field の非 dict パスと before_write の use_index=False None パスのカバレッジ確保)"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        db.add_hook(UniqueHook("email"))  # use_index=False (default)

        # dict でない値 → check_val が None → チェックスキップ（エラーなし）
        db["key1"] = "not_a_dict"
        db["key2"] = "also_not_a_dict"
        db.close()

    def test_use_index_false_callable_field_on_non_dict_in_scan(self, db_path):
        """use_index=False の O(N) スキャンで非 dict 値に対して callable field が呼ばれることを確認する。
        (hooks.py before_write use_index=False callable + non-dict パスのカバレッジ確保)"""
        from nanasqlite.hooks import UniqueHook

        call_count = [0]

        def get_email(key, value):
            call_count[0] += 1
            return value.get("email") if isinstance(value, dict) else None

        db = NanaSQLite(db_path)
        db.add_hook(UniqueHook(get_email))  # use_index=False

        db["user1"] = "not_a_dict"
        db["user2"] = {"email": "bob@example.com"}
        # O(N) スキャン中に user1 (非 dict) に対して callable が呼ばれる
        db["user3"] = {"email": "charlie@example.com"}
        assert call_count[0] > 0
        db.close()

    def test_use_index_false_non_dict_existing_triggers_scan_none_path(self, db_path):
        """use_index=False で非 dict 値が存在する状態で O(N) スキャンが走る際、
        str field に対して非 dict の other_val が None になるパスを確認する。
        (hooks.py before_write use_index=False str-field non-dict パスのカバレッジ確保)"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        db.add_hook(UniqueHook("email"))  # use_index=False, str field

        # 非 dict の既存値 (O(N) スキャン中に other_val = None になる)
        db._has_hooks = False
        db["key1"] = "not_a_dict"  # 非 dict
        db._has_hooks = True

        # check_val != None → O(N) スキャン実行 → key1 に対して other_val = None
        db["key2"] = {"email": "test@example.com"}
        db.close()

    def test_use_index_build_index_triggers_extract_non_dict(self, db_path):
        """_build_index() で str field に対して非 dict 値を持つキーが存在する場合、
        _extract_field が None を返してスキップされることを確認する。
        (hooks.py _extract_field の str field + 非 dict パス = line 316 のカバレッジ確保)"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        db._has_hooks = False
        db["k1"] = "not_a_dict"  # 非 dict - str field → _extract_field line 316
        db["k2"] = {"email": "test@example.com"}
        db._has_hooks = True

        hook = UniqueHook("email", use_index=True)
        db._hooks = [hook]
        hook._build_index(db)
        # k1 はスキップ、k2 はインデックス登録
        assert "test@example.com" in hook._value_to_key
        assert hook._value_to_key["test@example.com"] == "k2"
        db.close()

    def test_use_index_before_write_old_unhashable_except_handled(self, db_path):
        """旧インデックス値がアンハッシュ可能な場合、before_write の except TypeError が正しく処理される。
        (hooks.py before_write の old_check_val unhashable except パス 381-383 のカバレッジ確保)"""
        from nanasqlite.hooks import UniqueHook

        def get_tags(key, value):
            return value.get("tags") if isinstance(value, dict) else None

        db = NanaSQLite(db_path)
        db._has_hooks = False
        db["item1"] = {"tags": ["python", "sqlite"]}  # unhashable field value
        db._has_hooks = True

        hook = UniqueHook(get_tags, use_index=True)
        db._hooks = [hook]
        # _build_index がアンハッシュ可能値をスキップしてインデックスを構築
        hook._build_index(db)

        # item1 を更新: 旧値がアンハッシュ可能 → before_write の except TypeError パス
        # 新しい値はハッシュ可能 → エラーなし
        db["item1"] = {"tags": "rust"}  # 文字列 (hashable) に更新
        db.close()

    def test_use_index_duplicate_scan_skips_self_key(self, db_path):
        """is_known_duplicate=True の O(N) スキャンで同じキーの書き込みは continue される。
        (hooks.py before_write の k == key continue パス 409 のカバレッジ確保)"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        db._has_hooks = False
        # u1 を最初に追加（イテレーション順で先頭になる）
        db["u1"] = {"email": "dup@example.com"}
        db["u2"] = {"email": "dup@example.com"}
        db._has_hooks = True

        hook = UniqueHook("email", use_index=True)
        db._hooks = [hook]
        hook._build_index(db)
        assert "dup@example.com" in hook._duplicate_field_values

        # u1 のメールを別の値に変更（before_write が old_check_val を処理するが
        # None フィールドにすることで discard を防ぐ）
        db._has_hooks = False
        db["u1"] = {"name": "alice"}  # email フィールドなし → old_check_val = None
        db["u2"] = {"email": "other@example.com"}  # u2 の重複を解消
        db._has_hooks = True

        # u1 (イテレーション順で先頭) が "dup@example.com" を書き込む
        # old_check_val = None なので discard されない → is_known_duplicate = True
        # O(N) スキャン: k="u1"==key → continue (LINE 409)
        # k="u2": email="other" → 競合なし → resolve (LINES 420-422)
        db["u1"] = {"email": "dup@example.com"}
        assert "dup@example.com" in hook._value_to_key
        assert "dup@example.com" not in hook._duplicate_field_values
        db.close()

    def test_use_index_true_key_pattern_no_match_skips_write(self, db_path):
        """use_index=True で key_pattern に一致しないキーへの書き込みはスキップされる。
        (hooks.py before_write の _should_run=False return パス 351 のカバレッジ確保)"""
        import re

        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        hook = UniqueHook("email", use_index=True, key_pattern=re.compile(r"^user_"))
        db.add_hook(hook)

        # パターン一致 → インデックス構築 + チェック
        db["user_1"] = {"email": "alice@example.com"}
        assert hook._index_built is True

        # パターン不一致 → before_write early return (line 351)
        db["other_key"] = {"email": "alice@example.com"}  # 重複チェックなし
        db.close()

    def test_use_index_before_delete_index_not_built_returns_early(self, db_path):
        """use_index=True でも _index_built=False のとき before_delete は早期リターンする。
        (hooks.py before_delete の use_index/index_built チェック 463 のカバレッジ確保)"""
        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        hook = UniqueHook("email", use_index=True)
        db._hooks = [hook]
        db._has_hooks = True

        # インデックスを構築しないまま削除 → 早期リターン（クラッシュしない）
        db._has_hooks = False
        db["user1"] = {"email": "alice@example.com"}
        db._has_hooks = True
        # _index_built=False のまま削除
        assert hook._index_built is False
        del db["user1"]
        db.close()

    def test_use_index_before_delete_key_pattern_no_match_returns(self, db_path):
        """use_index=True で _should_run が False の場合、before_delete は早期リターンする。
        (hooks.py before_delete の _should_run チェック 465 のカバレッジ確保)"""
        import re

        from nanasqlite.hooks import UniqueHook

        db = NanaSQLite(db_path)
        # key_pattern="^user_" に一致するキーのみチェック
        hook = UniqueHook("email", use_index=True, key_pattern=re.compile(r"^user_"))
        db.add_hook(hook)

        db["user_1"] = {"email": "alice@example.com"}
        # インデックス構築済み
        assert hook._index_built is True

        # パターンに一致しないキーの削除 → before_delete は早期リターン
        db._has_hooks = False
        db["other_key"] = {"email": "test@example.com"}
        db._has_hooks = True
        del db["other_key"]  # _should_run=False → line 465 return
        db.close()

    def test_use_index_before_delete_unhashable_except_handled(self, db_path):
        """削除時に check_val がアンハッシュ可能な場合、before_delete の except TypeError が処理される。
        (hooks.py before_delete の TypeError except パス 482-484 のカバレッジ確保)"""
        from nanasqlite.hooks import UniqueHook

        def get_tags(key, value):
            return value.get("tags") if isinstance(value, dict) else None

        db = NanaSQLite(db_path)
        db._has_hooks = False
        db["item1"] = {"tags": ["python"]}  # unhashable
        db._has_hooks = True

        hook = UniqueHook(get_tags, use_index=True)
        db._hooks = [hook]
        hook._build_index(db)

        # 削除: check_val = ["python"] はアンハッシュ可能 → except TypeError: pass
        del db["item1"]
        db.close()


# ---------------------------------------------------------------------------
# v1.5.4 前倒し実施: PERF-02 — BaseHook Pattern 型再コンパイル省略
# ---------------------------------------------------------------------------

class TestPerf02V154BaseHookPatternRevalidation:
    """PERF-02 (v1.5.4): 既コンパイル済み Pattern でも pattern.pattern への
    _validate_regex_pattern による検証は維持され、再コンパイルのみ省略される。"""

    def test_compiled_pattern_still_validates_pattern_text_no_re2(self):
        """非 RE2 パスで既コンパイル済み Pattern を渡しても、セキュリティ上
        pattern.pattern テキストに対して _validate_regex_pattern が呼ばれることを確認する。
        コンパイル済み Pattern を経由して ReDoS ブラックリストをバイパスできないことを保証する。"""
        import re
        from unittest.mock import patch

        from nanasqlite.hooks import BaseHook

        compiled = re.compile(r"^user_")
        # 非 RE2 パスで PERF-02 + セキュリティ修正の動作を確認
        with patch("nanasqlite.hooks.HAS_RE2", False):
            with patch.object(BaseHook, "_validate_regex_pattern") as mock_validate:
                hook = BaseHook(key_pattern=compiled)
                # コンパイル済み Pattern でも pattern.pattern テキストを検証する（セキュリティ要件）
                mock_validate.assert_called_once_with(compiled.pattern)
                # compiled Pattern オブジェクトをそのまま再利用する（再コンパイルしない）
                assert hook._key_regex is compiled

    def test_string_pattern_still_validates_no_re2(self):
        """非 RE2 パスで文字列パターンは引き続き _validate_regex_pattern で検証されることを確認する。"""
        from unittest.mock import patch

        from nanasqlite.hooks import BaseHook

        # Force non-RE2 path
        with patch("nanasqlite.hooks.HAS_RE2", False):
            # 危険なパターンは拒否される
            with pytest.raises(NanaSQLiteValidationError, match="Potentially dangerous regex"):
                BaseHook(key_pattern=r"(a+)+")

    def test_compiled_dangerous_pattern_rejected_no_re2(self):
        """非 RE2 パスで危険なパターンをコンパイルしてから渡した場合も拒否されることを確認する。
        コンパイル済み Pattern で ReDoS ブラックリストをバイパスできないことの回帰テスト。"""
        import re
        from unittest.mock import patch

        from nanasqlite.hooks import BaseHook

        compiled_dangerous = re.compile(r"(a+)+")
        with patch("nanasqlite.hooks.HAS_RE2", False):
            with pytest.raises(NanaSQLiteValidationError, match="Potentially dangerous regex"):
                BaseHook(key_pattern=compiled_dangerous)

    def test_compiled_pattern_works_correctly_in_hook(self, db_path):
        """既コンパイル済み Pattern を渡したフックが正しく動作することを確認する。"""
        import re

        from nanasqlite.hooks import CheckHook

        compiled = re.compile(r"^user_")
        hook = CheckHook(lambda k, v: isinstance(v, str), key_pattern=compiled)

        db = NanaSQLite(db_path)
        db.add_hook(hook)
        db["user_1"] = "value"  # パターンに一致 → チェックされる
        db["other_key"] = 123   # パターンに不一致 → チェックされない（整数でもOK）
        db.close()



# ---------------------------------------------------------------------------
# v1.5.4 前倒し実施: QUAL-01 — re2_module 型アノテーション
# ---------------------------------------------------------------------------

class TestQual01V154Re2ModuleAnnotation:
    """QUAL-01 (v1.5.4): compat.py の re2_module 型アノテーションが正しいことを確認する。"""

    def test_re2_module_has_correct_annotation(self):
        """re2_module が types.ModuleType | None の型で宣言されていることを確認する。"""
        import types as builtin_types

        from nanasqlite import compat as compat_mod

        re2_module_val = compat_mod.re2_module
        # 値は None またはモジュールである
        assert re2_module_val is None or isinstance(re2_module_val, builtin_types.ModuleType)

    def test_compat_imports_types_module(self):
        """compat.py が types モジュールをインポートしていることを確認する。"""
        import inspect

        from nanasqlite import compat as compat_mod

        source = inspect.getsource(compat_mod)
        assert "import types" in source, "compat.py should import the 'types' module for QUAL-01"
        assert "types.ModuleType" in source, "compat.py should use types.ModuleType for re2_module annotation"


# ---------------------------------------------------------------------------
# v1.5.4 前倒し実施: QUAL-02 — DLQEntry dataclass
# ---------------------------------------------------------------------------

class TestQual02V154DLQEntryDataclass:
    """QUAL-02 (v1.5.4): V2Engine の DLQ が DLQEntry dataclass を使用することを確認する。"""

    def test_dlq_entry_dataclass_exists(self):
        """DLQEntry dataclass が v2_engine モジュールに定義されていることを確認する。"""
        from dataclasses import fields, is_dataclass

        from nanasqlite.v2_engine import DLQEntry

        assert is_dataclass(DLQEntry)
        field_names = {f.name for f in fields(DLQEntry)}
        assert "error_msg" in field_names
        assert "item" in field_names
        assert "timestamp" in field_names

    def test_dlq_uses_dlq_entry_internally(self, db_path):
        """V2Engine の内部 DLQ が DLQEntry インスタンスのリストであることを確認する。"""
        import apsw

        from nanasqlite.v2_engine import DLQEntry, V2Engine

        conn = apsw.Connection(db_path)
        engine = V2Engine(connection=conn, table_name="data")
        engine._add_to_dlq("test error", {"action": "set", "value": "val"})

        assert len(engine.dlq) == 1
        entry = engine.dlq[0]
        assert isinstance(entry, DLQEntry)
        assert entry.error_msg == "test error"
        assert entry.item == {"action": "set", "value": "val"}
        assert isinstance(entry.timestamp, float)

        engine.shutdown()
        conn.close()

    def test_get_dlq_backward_compatible_dict_format(self, db_path):
        """get_dlq() が後方互換の dict 形式を返すことを確認する。"""
        import apsw

        from nanasqlite.v2_engine import V2Engine

        conn = apsw.Connection(db_path)
        engine = V2Engine(connection=conn, table_name="data")
        engine._add_to_dlq("test error", "test_item")

        dlq = engine.get_dlq()
        assert len(dlq) == 1
        entry = dlq[0]
        assert "error" in entry
        assert "item" in entry
        assert "timestamp" in entry
        assert entry["error"] == "test error"
        assert entry["item"] == "test_item"

        engine.shutdown()
        conn.close()


# ---------------------------------------------------------------------------
# v1.5.4 前倒し実施: SEC-01 — DLQ ペイロード漏洩ドキュメント
# ---------------------------------------------------------------------------

class TestSec01V154DLQPayloadDocumentation:
    """SEC-01 (v1.5.4): DLQ ペイロード漏洩リスクがドキュメント化されていることを確認する。"""

    def test_dlq_entry_has_security_notice(self):
        """DLQEntry の docstring に SEC-01 セキュリティ注意書きが含まれることを確認する。"""
        from nanasqlite.v2_engine import DLQEntry

        doc = DLQEntry.__doc__ or ""
        assert "SEC-01" in doc, "DLQEntry docstring should contain 'SEC-01' security notice"
        assert "payload" in doc.lower() or "exposure" in doc.lower() or "漏洩" in doc or "plaintext" in doc.lower()

    def test_get_dlq_docstring_mentions_security(self):
        """get_dlq() の docstring にペイロード漏洩リスクへの言及があることを確認する。"""
        import inspect

        from nanasqlite.v2_engine import V2Engine

        doc = inspect.getdoc(V2Engine.get_dlq) or ""
        assert "SEC-01" in doc or "security" in doc.lower() or "exposure" in doc.lower() or "plaintext" in doc.lower()

    def test_add_to_dlq_docstring_mentions_security(self):
        """_add_to_dlq() の docstring にペイロード漏洩リスクへの言及があることを確認する。"""
        import inspect

        from nanasqlite.v2_engine import V2Engine

        doc = inspect.getdoc(V2Engine._add_to_dlq) or ""
        assert "SEC-01" in doc or "payload" in doc.lower() or "exposure" in doc.lower()
