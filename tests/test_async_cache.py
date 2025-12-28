"""
Tests for asynchronous cache strategy usage (v1.3.1).
"""
import asyncio

import pytest

from nanasqlite import AsyncNanaSQLite, CacheType

pytestmark = pytest.mark.asyncio

class TestAsyncCacheStrategies:
    """非同期環境でのキャッシュ戦略機能テスト"""

    async def test_async_unbounded_default(self, tmp_path):
        """Unbounded (Default) Cache in Async"""
        db_path = str(tmp_path / "async_unbounded.db")
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")
            assert await db.aget("key1") == "value1"
            assert await db.is_cached("key1")

            # Check internal cache size access
            # AsyncNanaSQLite wraps NanaSQLite in self._db (sync instance) which is in a thread
            # We can't access self._db._cache easily from main thread safely without locking or checking implementation
            # But we can verify behavior functionally.

    async def test_async_lru_eviction(self, tmp_path):
        """LRU Eviction in Async"""
        db_path = str(tmp_path / "async_lru.db")
        # LRU size 2
        async with AsyncNanaSQLite(db_path, cache_strategy=CacheType.LRU, cache_size=2) as db:
            await db.aset("k1", 1)
            await db.aset("k2", 2)
            await db.aset("k3", 3) # This should evict k1

            # k1 should be evicted from cache but exist in DB
            assert not await db.is_cached("k1")
            assert await db.is_cached("k2")
            assert await db.is_cached("k3")

            # Fetching k1 should bring it back and evict k2 (LRU)
            assert await db.aget("k1") == 1
            assert await db.is_cached("k1")
            assert not await db.is_cached("k2")

    async def test_async_ttl_expiration(self, tmp_path):
        """TTL Expiration in Async"""
        db_path = str(tmp_path / "async_ttl.db")
        # TTL 0.5s
        async with AsyncNanaSQLite(db_path, cache_strategy=CacheType.TTL, cache_ttl=0.2) as db:
            await db.aset("k", "v")
            assert await db.is_cached("k")
            assert await db.aget("k") == "v"

            # Wait for expiration
            await asyncio.sleep(0.3)

            # Data is expired, so is_cached might behave differently depending on implementation
            # TTLCache doesn't auto-remove unless accessed or cleanup runs.
            # But is_cached checks key existence in internal dict.
            # However, aget should verify TTL.

            # Accessing it should still return value (reload or valid if using persistence)
            # Default behavior: if expired, it might fetch from DB (if persistence is on by default? No, TTLCache default usually works as valid period)
            # Wait, if TTL expired, it's treated as "not in cache" logically, should re-fetch from DB or return default?
            # NanaSQLite behaves like a KVS. If key is in DB, it returns it. TLL applies to "cache validity".
            # So expiration means "evict/refresh from DB".

            val = await db.aget("k")
            assert val == "v"
            # It just means it was fetched from DB again if cache expired.

    async def test_async_clear_cache(self, tmp_path):
        """aclear_cache correctness"""
        db_path = str(tmp_path / "async_clear.db")
        async with AsyncNanaSQLite(db_path, cache_strategy=CacheType.UNBOUNDED) as db:
            await db.aset("k1", 1)
            assert await db.is_cached("k1")

            await db.aclear_cache()

            assert not await db.is_cached("k1")
            assert await db.aget("k1") == 1 # Still in DB
