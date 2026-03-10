"""
POC verification tests for audit findings (v1.3.4).

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
            pass


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
        """Data shorter than 13 bytes raises NanaSQLiteDatabaseError."""
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

        # Wait for expiry + scheduler cycle
        time.sleep(0.5)

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
            # COUNT is in default allowed list
            results = db.query("t", where='"COUNT" IS NOT NULL')
            # This should NOT raise because "COUNT" here is not followed by (
            assert isinstance(results, list)
        finally:
            db.close()
