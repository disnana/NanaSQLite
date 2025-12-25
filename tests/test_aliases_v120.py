import pytest

from nanasqlite import AsyncNanaSQLite


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_aliases.db")


@pytest.mark.asyncio
async def test_async_get_alias(db_path):
    """get エイリアスが aget と同じ動作をすることを確認"""
    async with AsyncNanaSQLite(db_path) as db:
        await db.aset("test_key", {"value": "test_data"})

        # aget を使用
        result_aget = await db.aget("test_key")
        # get エイリアスを使用
        result_get = await db.get("test_key")

        assert result_aget == result_get
        assert result_get == {"value": "test_data"}


@pytest.mark.asyncio
async def test_async_contains_alias(db_path):
    """contains エイリアスが acontains と同じ動作をすることを確認"""
    async with AsyncNanaSQLite(db_path) as db:
        await db.aset("existing_key", "data")

        # acontains を使用
        result_acontains = await db.acontains("existing_key")
        # contains エイリアスを使用
        result_contains = await db.contains("existing_key")

        assert result_acontains == result_contains
        assert result_contains is True

        # 存在しないキー
        assert await db.contains("nonexistent") is False


@pytest.mark.asyncio
async def test_async_keys_alias(db_path):
    """keys エイリアスが akeys と同じ動作をすることを確認"""
    async with AsyncNanaSQLite(db_path) as db:
        await db.aset("key1", "value1")
        await db.aset("key2", "value2")
        await db.aset("key3", "value3")

        # akeys を使用
        result_akeys = await db.akeys()
        # keys エイリアスを使用
        result_keys = await db.keys()

        assert set(result_akeys) == set(result_keys)
        assert set(result_keys) == {"key1", "key2", "key3"}


@pytest.mark.asyncio
async def test_async_values_alias(db_path):
    """values エイリアスが avalues と同じ動作をすることを確認"""
    async with AsyncNanaSQLite(db_path) as db:
        await db.aset("key1", "value1")
        await db.aset("key2", "value2")

        # avalues を使用
        result_avalues = await db.avalues()
        # values エイリアスを使用
        result_values = await db.values()

        assert result_avalues == result_values
        assert set(result_values) == {"value1", "value2"}


@pytest.mark.asyncio
async def test_async_items_alias(db_path):
    """items エイリアスが aitems と同じ動作をすることを確認"""
    async with AsyncNanaSQLite(db_path) as db:
        await db.aset("key1", "value1")
        await db.aset("key2", "value2")

        # aitems を使用
        result_aitems = await db.aitems()
        # items エイリアスを使用
        result_items = await db.items()

        assert result_aitems == result_items
        assert set(result_items) == {("key1", "value1"), ("key2", "value2")}
