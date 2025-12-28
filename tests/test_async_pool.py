import apsw
import pytest
import pytest_asyncio

from nanasqlite import AsyncNanaSQLite


@pytest_asyncio.fixture
async def db(tmp_path):
    """Fixture with read_pool_size=2"""
    db_path = str(tmp_path / "test_async_pool.db")
    async with AsyncNanaSQLite(db_path, read_pool_size=2) as _db:
        await _db.aset("user:1", {"name": "Alice"})
        await _db.aset("user:2", {"name": "Bob"})
        await _db.aset("user:3", {"name": "Charlie"})
        yield _db


@pytest.mark.asyncio
async def test_pool_fetch_all(db):
    """Test that fetch_all works via pool"""
    rows = await db.fetch_all("SELECT key, value FROM data ORDER BY key")
    assert len(rows) == 3
    assert rows[0][0] == "user:1"


@pytest.mark.asyncio
async def test_pool_readonly_safety(db):
    """Test that pool enforces Read-Only mode"""
    with pytest.raises(apsw.ReadOnlyError):
        await db.fetch_all("DELETE FROM data WHERE key = ?", ("user:1",))
    # Verify data is still there
    assert await db.acontains("user:1")


@pytest.mark.asyncio
async def test_pool_mixed_workload(db):
    """Test mixed workload: writes (main) and reads (pool)"""
    await db.aset("user:4", {"name": "Dave"})
    rows = await db.fetch_all("SELECT key FROM data WHERE key = ?", ("user:4",))
    assert len(rows) == 1
    assert rows[0][0] == "user:4"


@pytest.mark.asyncio
async def test_pool_default_disabled(tmp_path):
    """Test backward compatibility (pool disabled by default)"""
    db_path = str(tmp_path / "test_no_pool.db")
    async with AsyncNanaSQLite(db_path) as db0:
        assert db0._read_pool is None
        await db0.aset("key", "val")
        rows = await db0.fetch_all("SELECT * FROM data")
        assert len(rows) == 1


@pytest.mark.asyncio
async def test_pool_query_with_pagination(db):
    """Test that query_with_pagination uses the pool"""
    results = await db.query_with_pagination(table_name="data", columns=["key", "value"], limit=1)
    assert len(results) == 1
