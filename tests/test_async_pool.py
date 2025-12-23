
import pytest
import asyncio
import apsw
from nanasqlite import AsyncNanaSQLite

@pytest.fixture
async def db(tmp_path):
    db_path = str(tmp_path / "test_async_pool.db")
    
    # Initialize with pool enabled
    # We don't need manual cleanup because tmp_path is cleaned by pytest
    async with AsyncNanaSQLite(db_path, read_pool_size=2) as _db:
        # Create table and insert initial data
        await _db.aset("user:1", {"name": "Alice"})
        await _db.aset("user:2", {"name": "Bob"})
        await _db.aset("user:3", {"name": "Charlie"})
        yield _db

@pytest.mark.asyncio
async def test_pool_fetch_all(db):
    """Test that fetch_all works via pool"""
    # Since pool uses WAL, it should see committed data.
    # NanaSQLite commits on updates.
    
    rows = await db.fetch_all("SELECT key, value FROM data ORDER BY key")
    assert len(rows) == 3
    assert rows[0][0] == "user:1"

@pytest.mark.asyncio
async def test_pool_query(db):
    """Test that query works via pool"""
    results = await db.query(where="key = ?", parameters=("user:2",))
    assert len(results) == 1
    # query returns raw SQL row. key='user:2', value='{"name": "Bob"}' (JSON string)
    assert results[0]["key"] == "user:2"
    import json
    val = json.loads(results[0]["value"])
    assert val["name"] == "Bob"

@pytest.mark.asyncio
async def test_pool_readonly_safety(db):
    """Test that pool enforces Read-Only mode"""
    # Attempt to write via fetch_all/query should fail
    
    # Note: executing INSERT/UPDATE via fetch_all usually returns empty list if successful,
    # but here it should raise apsw.ReadOnlyError because connection is read-only.
    
    with pytest.raises(apsw.ReadOnlyError):
        await db.fetch_all("DELETE FROM data WHERE key = ?", ("user:1",))

    # Verify data is still there
    assert await db.acontains("user:1")

@pytest.mark.asyncio
async def test_pool_mixed_workload(db):
    """Test mixed workload: writes (main) and reads (pool)"""
    
    # Write on main
    await db.aset("user:4", {"name": "Dave"})
    
    # Read on pool (WAL should make it visible immediately or eventually)
    # NanaSQLite uses synchronous=NORMAL/WAL, so it should be visible.
    
    rows = await db.fetch_all("SELECT key FROM data WHERE key = ?", ("user:4",))
    assert len(rows) == 1
    assert rows[0][0] == "user:4"

@pytest.mark.asyncio
async def test_pool_default_disabled(tmp_path):
    """Test backward compatibility (pool disabled by default)"""
    db_path = str(tmp_path / "test_no_pool.db")
        
    async with AsyncNanaSQLite(db_path) as db0:
        # Default read_pool_size is 0
        assert db0._read_pool is None
        
        await db0.aset("key", "val")
        # Should still work (uses main connection)
        rows = await db0.fetch_all("SELECT * FROM data")
        assert len(rows) == 1
        
        # Writes via fetch_all should succeed (if not strictly read-only on main)
        # Main connection is NOT read-only.
        # We must insert VALID JSON because check_connection/read checks might try to parse it later if accessed.
        # Or specifically acontains checks existence, but if we read it...
        # Let's insert valid JSON: "v2" -> "\"v2\""
        await db0.fetch_all("INSERT OR IGNORE INTO data (key, value) VALUES (?, ?)", ("k2", '"v2"'))
        assert await db0.acontains("k2")

