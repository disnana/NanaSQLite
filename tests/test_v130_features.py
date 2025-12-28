import time

import pytest

from nanasqlite import AsyncNanaSQLite, CacheType, NanaSQLite


def test_unbounded_fifo_limit(tmp_path):
    """UNBOUNDEDモードでFIFO制限が正しく機能するかテスト"""
    db_path = str(tmp_path / "fifo.db")
    # 上限を2に設定
    db = NanaSQLite(db_path, cache_strategy=CacheType.UNBOUNDED, cache_size=2)

    db["a"] = 1
    db["b"] = 2
    assert len(db._data) == 2

    # 3つ目を追加。FIFOなので "a" が消えるはず
    db["c"] = 3
    assert len(db._data) == 2
    assert "a" not in db._data
    assert "b" in db._data
    assert "c" in db._data

    # 更新時は消えないはず
    db["b"] = 20
    assert len(db._data) == 2
    assert "b" in db._data
    assert "c" in db._data

def test_ttl_cache_expiration(tmp_path):
    """TTLキャッシュが指定時間後に消去されるかテスト"""
    db_path = str(tmp_path / "ttl.db")
    # TTLを0.5秒に設定
    db = NanaSQLite(db_path, cache_strategy=CacheType.TTL, cache_ttl=0.5)

    db["key1"] = "val1"
    assert "key1" in db._data

    time.sleep(0.7)
    # アクセス時に消える(Lazy)かワーカーが消すはず
    # 内部辞書の存在チェック
    assert "key1" not in db._cache.get_data()

    # DBからは消えていないので、再ロードされるはず（Persistence TTL=False のデフォルト）
    assert db["key1"] == "val1"
    assert "key1" in db._data

def test_persistence_ttl(tmp_path):
    """Persistence TTL=True の場合、DBからもデータが消えるかテスト"""
    db_path = str(tmp_path / "per_ttl.db")
    db = NanaSQLite(db_path, cache_strategy=CacheType.TTL, cache_ttl=0.5, cache_persistence_ttl=True)

    db["session1"] = "data1"
    assert "session1" in db

    time.sleep(1.0) # ワーカーによる削除を待つ

    # メモリから消えている
    assert "session1" not in db._cache.get_data()

    # DBからも消えているはずなので、再ロードしても None (または KeyError)
    # NanaSQLite は dict ライクなので、存在しないキーへのアクセスは KeyError
    with pytest.raises(KeyError):
        _ = db["session1"]

@pytest.mark.asyncio
async def test_async_clear_cache(tmp_path):
    """非同期でのキャッシュクリアが機能するかテスト"""
    db_path = str(tmp_path / "async_clear.db")
    async with AsyncNanaSQLite(db_path) as db:
        await db.aset("k1", "v1")
        # 直接内部DBのキャッシュを確認（同期インスタンス）
        sync_db = db._db
        assert "k1" in sync_db._data

        await db.aclear_cache()
        assert "k1" not in sync_db._data

        # DBには残っているので取得は可能
        assert await db.aget("k1") == "v1"

def test_clear_cache_sync(tmp_path):
    """同期でのキャッシュクリアが機能するかテスト"""
    db_path = str(tmp_path / "sync_clear.db")
    db = NanaSQLite(db_path)
    db["k1"] = "v1"
    assert "k1" in db._data

    db.clear_cache()
    assert "k1" not in db._data
    assert db["k1"] == "v1"
