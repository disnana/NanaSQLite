"""
Additional security and functionality tests for NanaSQLite
Tests for edge cases and security issues identified in code review
"""

import os
import tempfile

import pytest

from nanasqlite import NanaSQLite


@pytest.fixture
def db():
    """テスト用データベースフィクスチャ（pytest-xdist対応）"""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    db = NanaSQLite(db_path)
    yield db

    db.close()
    try:
        os.unlink(db_path)
    except OSError:
        # Ignore errors during cleanup; file may already be deleted or locked.
        pass


def test_alter_table_default_with_quotes(db):
    """Test ALTER TABLE with default values containing single quotes"""
    db.create_table("test", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})

    # Test default value with single quote (SQL injection test)
    db.alter_table_add_column("test", "description", "TEXT", default="it's okay")
    schema = db.get_table_schema("test")

    # Find the description column
    desc_col = [col for col in schema if col["name"] == "description"][0]
    # The value should be properly escaped: 'it''s okay'
    # Note: SQLite stores it with the outer quotes
    assert "'it''s okay'" in str(desc_col.get("default_value", ""))

    # Insert a row and verify the default value works
    db.sql_insert("test", {"id": 1, "name": "Test"})
    result = db.query("test", where="id = ?", parameters=(1,))
    assert result[0]["description"] == "it's okay"


def test_upsert_do_nothing_rowid(db):
    """Test upsert returns 0 when DO NOTHING is triggered"""
    db.create_table("test", {"id": "INTEGER PRIMARY KEY", "value": "TEXT UNIQUE"})

    # First insert
    rowid1 = db.upsert("test", {"id": 1, "value": "first"}, conflict_columns=["value"])
    assert rowid1 == 1

    # Attempt to insert with same value (should trigger DO NOTHING since all columns are conflict columns)
    rowid2 = db.upsert("test", {"value": "first"}, conflict_columns=["value"])
    assert rowid2 == 0  # Should return 0 when DO NOTHING is triggered

    # Verify only one row exists
    result = db.query("test")
    assert len(result) == 1


def test_query_with_as_clauses(db):
    """Test query() handles AS clauses properly"""
    db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"})
    db.sql_insert("users", {"id": 1, "name": "Alice", "age": 30})
    db.sql_insert("users", {"id": 2, "name": "Bob", "age": 25})

    # Test with AS clause
    results = db.query("users", columns=["name AS username", "age AS user_age"])
    assert len(results) == 2
    assert "username" in results[0]
    assert "user_age" in results[0]
    assert results[0]["username"] == "Alice"
    assert results[0]["user_age"] == 30


def test_query_with_aggregate_functions(db):
    """Test query() supports aggregate functions"""
    db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"})
    db.sql_insert("users", {"id": 1, "name": "Alice", "age": 30})
    db.sql_insert("users", {"id": 2, "name": "Bob", "age": 25})
    db.sql_insert("users", {"id": 3, "name": "Charlie", "age": 35})

    # Test with COUNT
    results = db.query("users", columns=["COUNT(*) as total"])
    assert len(results) == 1
    assert results[0]["total"] == 3

    # Test with MAX and MIN
    results = db.query("users", columns=["MAX(age) as max_age", "MIN(age) as min_age"])
    assert len(results) == 1
    assert results[0]["max_age"] == 35
    assert results[0]["min_age"] == 25

    # Test with AVG
    results = db.query("users", columns=["AVG(age) as avg_age"])
    assert len(results) == 1
    assert results[0]["avg_age"] == 30.0


def test_query_blocks_dangerous_column_expressions(db):
    """Test that query() blocks dangerous SQL patterns in column expressions"""
    db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})

    # Should block semicolon
    with pytest.raises(ValueError, match="Invalid"):
        db.query("users", columns=["id; DROP TABLE users"])

    # Should block SQL comments
    with pytest.raises(ValueError, match="Invalid"):
        db.query("users", columns=["id -- comment"])

    # Should block SQL keywords
    with pytest.raises(ValueError, match="Invalid"):
        db.query("users", columns=["id, DELETE FROM users"])


def test_order_by_no_backtracking(db):
    """Test that ORDER BY regex doesn't cause exponential backtracking"""
    db.create_table("test", {"a": "INTEGER", "b": "INTEGER", "c": "INTEGER"})

    # This should validate quickly even with many columns
    # The old regex could cause exponential backtracking
    long_order = ", ".join([f"col{i} ASC" for i in range(50)])

    # This should either pass validation or fail quickly (not hang)
    import time

    start = time.time()
    try:
        db.query("test", order_by=long_order)
    except Exception:
        # Query might fail because columns don't exist, but it shouldn't hang
        pass
    elapsed = time.time() - start

    # Should complete in under 1 second (old regex could take minutes)
    assert elapsed < 1.0, f"ORDER BY validation took too long: {elapsed}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
