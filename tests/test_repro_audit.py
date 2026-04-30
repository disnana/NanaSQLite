import os
import pytest
import warnings
from nanasqlite import NanaSQLite, V2Config, NanaSQLiteValidationError

def test_poc_v2_batch_get_consistency():
    """PoC: batch_get ignores pending writes in V2 staging buffer."""
    db_path = "test_poc_v2.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Use V2 mode with count flush (won't flush until 100 changes)
    cfg = V2Config(flush_mode="count", flush_count=100)
    db = NanaSQLite(db_path, v2_mode=True, v2_config=cfg)
    try:
        db["key1"] = "value1" # Stays in staging buffer
        
        # Clear memory cache to force DB/staging lookup
        db.clear_cache()
        
        # batch_get should find it in staging, but currently it only checks DB
        results = db.batch_get(["key1"])
        
        assert "key1" in results, "FAIL: batch_get failed to find key in V2 staging buffer"
        assert results["key1"] == "value1"
    finally:
        db.close()
        if os.path.exists(db_path):
            os.remove(db_path)

def test_poc_sql_validation_backticks():
    """PoC: fast_validate_sql_chars rejects backticks and brackets."""
    db = NanaSQLite(":memory:", strict_sql_validation=True)
    try:
        # These should be allowed for SQLite compatibility
        # We only care that they don't raise ValueError (validation error)
        try:
            db.query(columns=["`my column`"])
        except Exception as e:
            if isinstance(e, ValueError):
                raise
        
        try:
            db.query(where="[column name] = 1")
        except Exception as e:
            if isinstance(e, ValueError):
                raise
    except ValueError as e:
        pytest.fail(f"FAIL: Legitimate SQLite syntax rejected: {e}")
    finally:
        db.close()

def test_poc_batch_get_variable_limit():
    """PoC: batch_get fails with too many keys (no chunking)."""
    db_path = "test_poc_limit.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = NanaSQLite(db_path)
    try:
        # 40000 keys will exceed the default SQLite variable limit
        keys = [f"key{i}" for i in range(40000)]
        # This is expected to raise an exception until chunking is implemented
        db.batch_get(keys)
    except Exception as e:
        if "too many SQL variables" in str(e):
            pytest.fail(f"FAIL: batch_get failed with too many variables: {e}")
        raise
    finally:
        db.close()
        if os.path.exists(db_path):
            os.remove(db_path)

def test_poc_v2_engine_sql_injection():
    """PoC: V2Engine internal methods are vulnerable to SQL injection via table_name."""
    import apsw
    from nanasqlite.v2_engine import V2Engine
    
    conn = apsw.Connection(":memory:")
    # Vulnerable f-string usage in V2Engine._process_kvs_chunk and _recover_chunk_via_dlq
    # If table_name is not sanitized, it can lead to injection.
    # While NanaSQLite sanitizes it, V2Engine should be robust.
    malicious_table = "data; DROP TABLE data; --"
    
    try:
        # SEC-02 fix: V2Engine should validate table_name in __init__
        with pytest.raises(ValueError, match="Invalid or unsafe table name"):
            engine = V2Engine(conn, table_name=malicious_table, flush_mode="manual")
            engine.kvs_set(malicious_table, "key", "value")
            engine.flush(wait=True)
            engine.shutdown()
    finally:
        pass

def test_poc_dangerous_sql_false_positive():
    """PoC: _DANGEROUS_SQL_RE causes false positives in string literals."""
    db = NanaSQLite(":memory:", strict_sql_validation=True)
    try:
        # Legitimate query containing 'DELETE' as a string value
        # Currently rejected because _DANGEROUS_SQL_RE doesn't ignore strings
        db.query(where="value = 'DELETE'")
    except ValueError as e:
        if "Potentially dangerous SQL pattern" in str(e):
            pytest.fail(f"FAIL: False positive for 'DELETE' in string literal: {e}")
        raise
    finally:
        db.close()
