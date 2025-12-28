"""
Tests for the cache strategy feature (v1.3.0).
"""

import pytest

from nanasqlite import CacheType, NanaSQLite


class TestCacheType:
    """Test CacheType enum."""

    def test_cache_type_values(self):
        assert CacheType.UNBOUNDED.value == "unbounded"
        assert CacheType.LRU.value == "lru"


class TestUnboundedCache:
    """Test Unbounded (default) cache strategy."""

    def test_default_is_unbounded(self, tmp_path):
        db_path = tmp_path / "test.db"
        with NanaSQLite(str(db_path)) as db:
            # Default should be unbounded
            db["key1"] = "value1"
            assert db["key1"] == "value1"

    def test_explicit_unbounded(self, tmp_path):
        db_path = tmp_path / "test.db"
        with NanaSQLite(str(db_path), cache_strategy=CacheType.UNBOUNDED) as db:
            for i in range(100):
                db[f"key{i}"] = f"value{i}"
            # All 100 keys should be in cache (unbounded)
            assert db._cache.size == 100


class TestLRUCache:
    """Test LRU cache strategy."""

    def test_lru_requires_size(self, tmp_path):
        db_path = tmp_path / "test.db"
        with pytest.raises(ValueError, match="cache_size must be"):
            NanaSQLite(str(db_path), cache_strategy=CacheType.LRU)

    def test_lru_basic_operations(self, tmp_path):
        db_path = tmp_path / "test.db"
        with NanaSQLite(str(db_path), cache_strategy=CacheType.LRU, cache_size=10) as db:
            db["a"] = 1
            db["b"] = 2
            assert db["a"] == 1
            assert db["b"] == 2

    def test_lru_eviction(self, tmp_path):
        """Test that LRU evicts oldest entries when full."""
        db_path = tmp_path / "test.db"
        with NanaSQLite(str(db_path), cache_strategy=CacheType.LRU, cache_size=3) as db:
            # Insert 5 items into cache of size 3
            for i in range(5):
                db[f"key{i}"] = f"value{i}"

            # Cache should only have 3 items (key2, key3, key4)
            assert db._cache.size == 3
            cache_keys = list(db._cache.get_data().keys())
            assert "key2" in cache_keys
            assert "key3" in cache_keys
            assert "key4" in cache_keys
            # key0 and key1 should be evicted
            assert "key0" not in cache_keys
            assert "key1" not in cache_keys

    def test_lru_db_persistence(self, tmp_path):
        """Test that evicted items are still in DB."""
        db_path = tmp_path / "test.db"
        with NanaSQLite(str(db_path), cache_strategy=CacheType.LRU, cache_size=2) as db:
            db["a"] = 1
            db["b"] = 2
            db["c"] = 3  # This evicts 'a' from cache

            # 'a' is not in cache but should be in DB
            assert "a" not in db._cache.get_data()
            # Accessing 'a' should reload from DB
            assert db["a"] == 1

    def test_lru_access_updates_order(self, tmp_path):
        """Test that accessing an item moves it to end (most recently used)."""
        db_path = tmp_path / "test.db"
        with NanaSQLite(str(db_path), cache_strategy=CacheType.LRU, cache_size=3) as db:
            db["a"] = 1
            db["b"] = 2
            db["c"] = 3
            # Access 'a' to make it recently used
            _ = db["a"]
            # Add new item, should evict 'b' (oldest)
            db["d"] = 4
            cache_keys = list(db._cache.get_data().keys())
            assert "b" not in cache_keys
            assert "a" in cache_keys


class TestTableCacheStrategy:
    """Test cache strategy on sub-tables."""

    def test_table_inherits_default(self, tmp_path):
        db_path = tmp_path / "test.db"
        with NanaSQLite(str(db_path)) as db:
            sub = db.table("users")
            sub["user1"] = {"name": "Alice"}
            assert sub["user1"]["name"] == "Alice"

    def test_table_custom_strategy(self, tmp_path):
        db_path = tmp_path / "test.db"
        with NanaSQLite(str(db_path)) as db:
            # Main db is unbounded
            logs = db.table("logs", cache_strategy=CacheType.LRU, cache_size=5)
            for i in range(10):
                logs[f"log{i}"] = f"message{i}"
            # Logs table should only cache 5 items
            assert logs._cache.size == 5


class TestCacheClearAndRefresh:
    """Test cache clearing and refreshing."""

    def test_clear_cache(self, tmp_path):
        db_path = tmp_path / "test.db"
        with NanaSQLite(str(db_path), cache_strategy=CacheType.LRU, cache_size=10) as db:
            db["a"] = 1
            db["b"] = 2
            assert db._cache.size == 2
            db.clear_cache()
            assert db._cache.size == 0
            # Data should still be in DB
            assert db["a"] == 1

    def test_refresh(self, tmp_path):
        db_path = tmp_path / "test.db"
        with NanaSQLite(str(db_path), cache_strategy=CacheType.LRU, cache_size=10) as db:
            db["a"] = 1
            # Manually modify cache for testing
            db._cache.set("a", 999)
            assert db["a"] == 999  # Cache hit
            # Refresh should reload from DB
            db.refresh("a")
            assert db["a"] == 1
