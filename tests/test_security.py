"""
Security tests for SQL injection protection in NanaSQLite
"""

import os
import tempfile

import pytest

from nanasqlite import NanaSQLite


@pytest.fixture
def db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    database = NanaSQLite(path)
    yield database
    database.close()
    try:
        os.unlink(path)
    except OSError:
        # Ignore errors during cleanup; file may already be deleted or locked.
        pass


class TestSQLInjectionProtection:
    """Test SQL injection protection mechanisms."""

    def test_malicious_order_by_query(self, db):
        """Test that malicious order_by parameter is rejected in query()."""
        db.create_table("test", {"id": "INTEGER", "name": "TEXT"})
        db.sql_insert("test", {"id": 1, "name": "Alice"})

        # Attempt SQL injection through order_by
        with pytest.raises(ValueError, match="Invalid order_by clause"):
            db.query("test", order_by="id; DROP TABLE test--")

    def test_malicious_order_by_pagination(self, db):
        """Test that malicious order_by parameter is rejected in query_with_pagination()."""
        db.create_table("test", {"id": "INTEGER", "name": "TEXT"})
        db.sql_insert("test", {"id": 1, "name": "Alice"})

        # Attempt SQL injection through order_by
        with pytest.raises(ValueError, match="Invalid order_by clause"):
            db.query_with_pagination("test", order_by="id; DROP TABLE test--")

    def test_malicious_group_by(self, db):
        """Test that malicious group_by parameter is rejected."""
        db.create_table("test", {"id": "INTEGER", "category": "TEXT"})
        db.sql_insert("test", {"id": 1, "category": "A"})

        # Attempt SQL injection through group_by
        with pytest.raises(ValueError, match="Invalid group_by clause"):
            db.query_with_pagination("test", group_by="category; DROP TABLE test--")

    def test_malicious_column_expression(self, db):
        """Test that malicious column expressions are rejected."""
        db.create_table("test", {"id": "INTEGER", "name": "TEXT"})
        db.sql_insert("test", {"id": 1, "name": "Alice"})

        # Attempt SQL injection through column expression
        with pytest.raises(ValueError, match="Potentially dangerous SQL pattern"):
            db.query_with_pagination("test", columns=["id); DROP TABLE test--"])

    def test_disallowed_pragma_name(self, db):
        """Test that disallowed PRAGMA commands are rejected."""
        # database_list is actually in the whitelist, so use a truly disallowed one
        with pytest.raises(ValueError, match="PRAGMA.*is not allowed"):
            db.pragma("compile_options")

    def test_malicious_pragma_value(self, db):
        """Test that malicious PRAGMA values are rejected."""
        # Attempt SQL injection through PRAGMA value
        with pytest.raises(ValueError, match="PRAGMA string value"):
            db.pragma("journal_mode", "WAL; DROP TABLE test--")

    def test_dangerous_column_type(self, db):
        """Test that dangerous column types are rejected."""
        db.create_table("test", {"id": "INTEGER"})

        # Attempt SQL injection through column_type
        with pytest.raises(ValueError, match="Invalid or dangerous column type"):
            db.alter_table_add_column("test", "new_col", "TEXT; DROP TABLE test--")

    def test_invalid_table_name(self, db):
        """Test that invalid table names are rejected."""
        from nanasqlite import NanaSQLiteValidationError

        # Attempt to use SQL injection in table name
        with pytest.raises(NanaSQLiteValidationError, match="Invalid identifier"):
            db.create_table("test; DROP TABLE users--", {"id": "INTEGER"})

    def test_invalid_column_name(self, db):
        """Test that invalid column names are rejected."""
        from nanasqlite import NanaSQLiteValidationError

        # Attempt to use SQL injection in column name
        with pytest.raises(NanaSQLiteValidationError, match="Invalid identifier"):
            db.create_table("test", {"id; DROP TABLE": "INTEGER"})

    def test_invalid_index_name(self, db):
        """Test that invalid index names are rejected."""
        from nanasqlite import NanaSQLiteValidationError

        db.create_table("test", {"id": "INTEGER"})

        # Attempt to use SQL injection in index name
        with pytest.raises(NanaSQLiteValidationError, match="Invalid identifier"):
            db.create_index("idx; DROP TABLE test--", "test", ["id"])

    def test_negative_limit(self, db):
        """Test that negative limit values are rejected."""
        db.create_table("test", {"id": "INTEGER"})
        db.sql_insert("test", {"id": 1})

        # Attempt to use negative limit
        with pytest.raises(ValueError, match="limit must be non-negative"):
            db.query("test", limit=-1)

    def test_negative_offset(self, db):
        """Test that negative offset values are rejected."""
        db.create_table("test", {"id": "INTEGER"})
        db.sql_insert("test", {"id": 1})

        # Attempt to use negative offset
        with pytest.raises(ValueError, match="offset must be non-negative"):
            db.query_with_pagination("test", offset=-1)

    def test_valid_complex_query(self, db):
        """Test that valid complex queries still work."""
        db.create_table("test", {"id": "INTEGER", "value": "INTEGER"})
        db.sql_insert("test", {"id": 1, "value": 10})
        db.sql_insert("test", {"id": 2, "value": 20})

        # These should all work fine
        results = db.query_with_pagination(
            "test", columns=["COUNT(*) as count", "SUM(value) as total"], group_by="id", order_by="id DESC"
        )
        assert len(results) > 0

    def test_valid_order_by_patterns(self, db):
        """Test that valid ORDER BY patterns are accepted."""
        db.create_table("test", {"id": "INTEGER", "name": "TEXT"})
        db.sql_insert("test", {"id": 1, "name": "Alice"})
        db.sql_insert("test", {"id": 2, "name": "Bob"})

        # Valid order_by patterns
        results = db.query("test", order_by="id ASC")
        assert len(results) == 2

        results = db.query("test", order_by="id DESC, name ASC")
        assert len(results) == 2

        results = db.query("test", order_by="name")
        assert len(results) == 2
