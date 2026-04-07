"""
NanaSQLite v1.5.3 - パフォーマンス回帰修正テスト

以下の修正を検証する:
- PERF-07: 共通 SQL 文字列の __init__ 時事前計算
- PERF-08: Unbounded モードでの to_dict() / copy() MISSING フィルタ省略
- PERF-09: LRU __getitem__ での二重キャッシュルックアップ排除
- PERF-10: _validate_expression() コンパイル済み正規表現 + 関数スキャンの早期スキップ
- PERF-11: ExpiringDict._check_expiry() のロックフリー早期終了パス
"""

from __future__ import annotations

import os
import tempfile
import time

import pytest

from nanasqlite import CacheType, NanaSQLite


@pytest.fixture
def db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test_v153_perf.db")


# ==================== PERF-07: Pre-computed SQL strings ====================


def test_precomputed_sql_strings_exist(db_path):
    """
    PERF-07: __init__ 時に共通 SQL 文字列が事前計算されていることを確認する。
    """
    db = NanaSQLite(db_path)
    try:
        assert hasattr(db, "_sql_kv_insert"), "_sql_kv_insert が存在しない"
        assert hasattr(db, "_sql_kv_delete"), "_sql_kv_delete が存在しない"
        assert hasattr(db, "_sql_kv_select"), "_sql_kv_select が存在しない"
        assert hasattr(db, "_sql_kv_contains"), "_sql_kv_contains が存在しない"
        assert hasattr(db, "_sql_kv_select_all"), "_sql_kv_select_all が存在しない"
        assert hasattr(db, "_sql_kv_count"), "_sql_kv_count が存在しない"

        # Ensure the table name is embedded correctly
        assert db._safe_table in db._sql_kv_insert
        assert db._safe_table in db._sql_kv_delete
        assert db._safe_table in db._sql_kv_select
        assert db._safe_table in db._sql_kv_contains
        assert db._safe_table in db._sql_kv_select_all
        assert db._safe_table in db._sql_kv_count
    finally:
        db.close()


def test_precomputed_sql_strings_correct_table(db_path):
    """
    PERF-07: カスタムテーブル名でも SQL 文字列が正しく生成されることを確認する。
    """
    db = NanaSQLite(db_path, table="my_store")
    try:
        assert '"my_store"' in db._sql_kv_insert
        assert '"my_store"' in db._sql_kv_delete
        assert '"my_store"' in db._sql_kv_select
    finally:
        db.close()


def test_single_write_uses_precomputed_sql(db_path):
    """
    PERF-07: __setitem__ が事前計算済み SQL を使って正常に書き込めることを確認する。
    """
    db = NanaSQLite(db_path)
    try:
        for i in range(50):
            db[f"key_{i}"] = {"value": i}
        assert len(db) == 50
        assert db["key_0"] == {"value": 0}
        assert db["key_49"] == {"value": 49}
    finally:
        db.close()


# ==================== PERF-08: to_dict() / copy() Unbounded optimization ====================


def test_to_dict_unbounded_mode_no_missing_sentinels(db_path):
    """
    PERF-08: Unbounded モードで to_dict() が MISSING センチネルを含まず、
    正しいデータを返すことを確認する。
    """
    db = NanaSQLite(db_path)
    try:
        for i in range(100):
            db[f"k{i}"] = i
        result = db.to_dict()
        assert len(result) == 100
        for i in range(100):
            assert result[f"k{i}"] == i
        # No MISSING values
        from nanasqlite.cache import MISSING

        assert not any(v is MISSING for v in result.values())
    finally:
        db.close()


def test_to_dict_lru_mode_no_missing_sentinels(db_path):
    """
    PERF-08: LRU モードで to_dict() も MISSING センチネルを含まないことを確認する
    （BUG-03 fix の維持）。
    """
    db = NanaSQLite(db_path, cache_strategy=CacheType.LRU, cache_size=50)
    try:
        for i in range(30):
            db[f"k{i}"] = i
        result = db.to_dict()
        assert len(result) == 30
        from nanasqlite.cache import MISSING

        assert not any(v is MISSING for v in result.values())
    finally:
        db.close()


def test_copy_matches_to_dict(db_path):
    """
    PERF-08: copy() が to_dict() と同じ結果を返すことを確認する。
    """
    db = NanaSQLite(db_path)
    try:
        data = {f"k{i}": i * 10 for i in range(20)}
        db.batch_update(data)
        assert db.copy() == db.to_dict()
        assert db.copy() == data
    finally:
        db.close()


# ==================== PERF-09: LRU __getitem__ single cache lookup ====================


def test_lru_getitem_cache_hit_returns_correct_value(db_path):
    """
    PERF-09: LRU キャッシュヒット時に正しい値を返すことを確認する。
    """
    db = NanaSQLite(db_path, cache_strategy=CacheType.LRU, cache_size=128)
    try:
        db["alpha"] = {"payload": [1, 2, 3]}
        # Warm up cache
        _ = db["alpha"]
        # Second read (cache hit path)
        assert db["alpha"] == {"payload": [1, 2, 3]}
    finally:
        db.close()


def test_lru_getitem_missing_key_raises(db_path):
    """
    PERF-09: LRU モードで存在しないキーにアクセスすると KeyError が発生することを確認する。
    """
    db = NanaSQLite(db_path, cache_strategy=CacheType.LRU, cache_size=64)
    try:
        db["existing"] = 42
        with pytest.raises(KeyError):
            _ = db["nonexistent"]
    finally:
        db.close()


def test_lru_getitem_missing_sentinel_raises(db_path):
    """
    PERF-09: LRU モードで既知の不在キー (MISSING sentinel) でも KeyError が発生することを確認する。
    """
    db = NanaSQLite(db_path, cache_strategy=CacheType.LRU, cache_size=64)
    try:
        # Access non-existent key once to populate negative cache
        with pytest.raises(KeyError):
            _ = db["ghost"]
        # Second access should still raise KeyError (not return MISSING sentinel)
        with pytest.raises(KeyError):
            _ = db["ghost"]
    finally:
        db.close()


def test_ttl_getitem_cache_hit_returns_correct_value(db_path):
    """
    TTL キャッシュヒット時に正しい値を返すことを確認する (PERF-09 / PERF-11)。
    """
    db = NanaSQLite(db_path, cache_strategy=CacheType.TTL, cache_ttl=300)
    try:
        db["beta"] = {"nums": list(range(10))}
        _ = db["beta"]  # warm up
        assert db["beta"] == {"nums": list(range(10))}
    finally:
        db.close()


# ==================== PERF-10: _validate_expression() optimization ====================


def test_validate_expression_simple_where_no_exception(db_path):
    """
    PERF-10: 単純な WHERE 句（関数呼び出しなし）で _validate_expression が
    例外を発生させないことを確認する。
    """
    db = NanaSQLite(db_path)
    try:
        db.create_table("users", {"id": "INTEGER", "email": "TEXT"})
        for i in range(10):
            db.sql_insert("users", {"id": i, "email": f"user{i}@example.com"})
        # Simple parameterized WHERE – should pass without error
        assert db.exists("users", "email = ?", ("user5@example.com",)) is True
        assert db.exists("users", "id = ?", (3,)) is True
        assert db.exists("users", "id = ?", (999,)) is False
    finally:
        db.close()


def test_validate_expression_function_call_allowed(db_path):
    """
    PERF-10: 許可リストにある関数呼び出しを含む WHERE 句が正常に通過することを確認する。
    """
    db = NanaSQLite(db_path)
    try:
        db.create_table("items", {"id": "INTEGER", "name": "TEXT"})
        for i in range(5):
            db.sql_insert("items", {"id": i, "name": f"item{i}"})
        # LENGTH() is in the default allowed list
        results = db.query("items", where="LENGTH(name) > ?", parameters=(4,))
        assert isinstance(results, list)
    finally:
        db.close()


def test_validate_expression_dangerous_pattern_detected(db_path):
    """
    PERF-10: 危険なパターン（セミコロン等）が検出されることを確認する。
    """
    db = NanaSQLite(db_path, strict_sql_validation=True)
    try:
        db.create_table("t", {"id": "INTEGER"})
        with pytest.raises((ValueError, Exception)):
            db.exists("t", "id = 1; DROP TABLE t")
    finally:
        db.close()


def test_sql_update_single_with_precomputed_validation(db_path):
    """
    PERF-10: sql_update() の WHERE 句バリデーションが最適化後も正常に動作することを確認する。
    """
    db = NanaSQLite(db_path)
    try:
        db.create_table("users", {"id": "INTEGER", "age": "INTEGER"})
        for i in range(5):
            db.sql_insert("users", {"id": i, "age": 20 + i})
        updated = db.sql_update("users", {"age": 30}, "id = ?", (2,))
        assert updated == 1
        rows = db.query("users", where="id = ?", parameters=(2,))
        assert rows[0]["age"] == 30
    finally:
        db.close()


# ==================== PERF-11: ExpiringDict._check_expiry() fast path ====================


def test_expiry_check_fast_path_for_valid_key():
    """
    PERF-11: 有効期限が切れていないキーに対して _check_expiry() が False を返し、
    ロックを取得せずに早期リターンすることを検証する（動作保証テスト）。
    """
    from nanasqlite.utils import ExpiringDict

    d = ExpiringDict(expiration_time=300)
    try:
        d["k"] = "v"
        # Key has 300s TTL; should not be expired
        assert d._check_expiry("k") is False
        assert d["k"] == "v"
    finally:
        d.clear()


def test_expiry_check_expired_key_removed():
    """
    PERF-11: 有効期限が切れたキーが _check_expiry() で削除されることを確認する。
    """
    from nanasqlite.utils import ExpirationMode, ExpiringDict

    d = ExpiringDict(expiration_time=0.05, mode=ExpirationMode.LAZY)
    try:
        d["short"] = "hello"
        assert "short" in d
        time.sleep(0.15)
        # After sleeping past TTL, check_expiry should return True and remove key
        assert d._check_expiry("short") is True
        assert "short" not in d._data
    finally:
        d.clear()


def test_expiry_check_unknown_key_returns_false():
    """
    PERF-11: 存在しないキーに対して _check_expiry() が False を返すことを確認する。
    """
    from nanasqlite.utils import ExpiringDict

    d = ExpiringDict(expiration_time=60)
    try:
        assert d._check_expiry("nonexistent") is False
    finally:
        d.clear()


def test_ttl_cache_repeated_reads_consistent(db_path):
    """
    PERF-11: TTL キャッシュで同じキーへの繰り返し読み込みが一貫した値を返すことを確認する。
    """
    db = NanaSQLite(db_path, cache_strategy=CacheType.TTL, cache_ttl=300)
    try:
        db["stable"] = {"count": 42}
        for _ in range(20):
            assert db["stable"] == {"count": 42}
    finally:
        db.close()


def test_ttl_cache_expiry_removes_key(db_path):
    """
    PERF-11: TTL 期限切れ後にキャッシュから削除されることを確認する。
    cache_persistence_ttl=True を指定した場合は DB からも削除される。
    """
    db = NanaSQLite(db_path, cache_strategy=CacheType.TTL, cache_ttl=0.05, cache_persistence_ttl=True)
    try:
        db["tmp"] = "temporary"
        assert db.get("tmp") == "temporary"
        time.sleep(0.2)
        # After TTL with persistence, key should not be accessible from cache or DB
        assert db.get("tmp") is None
    finally:
        db.close()


# ==================== PERF-14 / PERF-15 / PERF-16 / PERF-17 / PERF-18 / PERF-19 / PERF-20 ====================


def test_perf14_getitem_cached_hit(db_path):
    """PERF-14: __getitem__ cached hit returns correct value (try/except path)."""
    db = NanaSQLite(db_path)
    try:
        db["k"] = {"x": 1}
        assert db["k"] == {"x": 1}
        # Second access still correct (purely from _data)
        assert db["k"] == {"x": 1}
    finally:
        db.close()


def test_perf14_getitem_missing_raises_keyerror(db_path):
    """PERF-14: __getitem__ for missing key raises KeyError."""
    db = NanaSQLite(db_path)
    try:
        import pytest
        with pytest.raises(KeyError):
            _ = db["does_not_exist"]
    finally:
        db.close()


def test_perf15_get_cached_hit(db_path):
    """PERF-15: get() cached hit returns correct value (try/except path)."""
    db = NanaSQLite(db_path)
    try:
        db["k"] = 42
        assert db.get("k") == 42
        assert db.get("missing", "def") == "def"
    finally:
        db.close()


def test_perf16_contains_cached(db_path):
    """PERF-16: __contains__ cached hit/miss (try/except path)."""
    db = NanaSQLite(db_path)
    try:
        db["present"] = True
        assert "present" in db
        assert "absent" not in db
        # Second absent check uses _absent_keys fast path
        assert "absent" not in db
    finally:
        db.close()


def test_perf17_update_cache_empty_absent_keys(db_path):
    """PERF-17: _update_cache skips discard when _absent_keys is empty."""
    db = NanaSQLite(db_path)
    try:
        # Fresh DB: _absent_keys is empty; writes should still work correctly.
        assert len(db._absent_keys) == 0  # guard that PERF-17 guard applies
        db["k1"] = "v1"
        db["k2"] = "v2"
        assert db["k1"] == "v1"
        assert db["k2"] == "v2"
    finally:
        db.close()


def test_perf17_update_cache_discard_when_absent_keys_has_entry(db_path):
    """PERF-17: _update_cache discards from _absent_keys when set is non-empty."""
    db = NanaSQLite(db_path)
    try:
        # Touch a missing key to populate _absent_keys
        assert db.get("ghost") is None
        assert "ghost" in db._absent_keys
        # Re-insert the key: _absent_keys must be cleared for it
        db["ghost"] = "back"
        assert "ghost" not in db._absent_keys
        assert db["ghost"] == "back"
    finally:
        db.close()


def test_perf18_setdefault_existing_key(db_path):
    """PERF-18: setdefault() returns existing value without overwriting."""
    db = NanaSQLite(db_path)
    try:
        db["k"] = "original"
        result = db.setdefault("k", "other")
        assert result == "original"
        assert db["k"] == "original"
    finally:
        db.close()


def test_perf18_setdefault_new_key(db_path):
    """PERF-18: setdefault() for new key sets and returns default directly."""
    db = NanaSQLite(db_path)
    try:
        result = db.setdefault("new_k", "default_val")
        assert result == "default_val"
        assert db["new_k"] == "default_val"
    finally:
        db.close()


def test_perf19_pop_unbounded_returns_correct_value(db_path):
    """PERF-19: pop() in Unbounded mode returns the value via direct _data access."""
    db = NanaSQLite(db_path)
    try:
        db["target"] = {"data": 99}
        val = db.pop("target")
        assert val == {"data": 99}
        assert "target" not in db
    finally:
        db.close()


def test_perf20_has_hooks_initialized(db_path):
    """PERF-20: _has_hooks is False on fresh instance with no hooks."""
    db = NanaSQLite(db_path)
    try:
        assert db._has_hooks is False
    finally:
        db.close()


def test_perf20_has_hooks_updated_by_add_hook(db_path):
    """PERF-20: _has_hooks becomes True after add_hook()."""

    class NoopHook:
        def before_write(self, db, key, value):
            return value

        def after_read(self, db, key, value):
            return value

        def before_delete(self, db, key):
            pass

    db = NanaSQLite(db_path)
    try:
        assert db._has_hooks is False
        db.add_hook(NoopHook())
        assert db._has_hooks is True
    finally:
        db.close()


def test_perf20_has_hooks_true_with_validator(tmp_path):
    """PERF-20: _has_hooks is True when a validator is passed (ValidkitHook added)."""
    try:
        from validkit import v  # type: ignore[import]

        schema = {"name": v.str()}
        db_path = str(tmp_path / "val.db")
        db = NanaSQLite(db_path, validator=schema)
        try:
            assert db._has_hooks is True
        finally:
            db.close()
    except (ImportError, AttributeError):
        import pytest
        pytest.skip("validkit not installed or incompatible API")
