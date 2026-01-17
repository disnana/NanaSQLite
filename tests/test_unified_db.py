import os
import sys
import tempfile
import pytest

# Ensure local src is importable when running tests directly
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from nanasqlite import NanaDB, AsyncNanaDB


@pytest.fixture
def db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "unified.db")


def test_nana_db_sqlite_path_basic(db_path):
    db = NanaDB(db_path)
    try:
        db["k"] = {"v": 1}
        assert db["k"] == {"v": 1}
        assert "k" in db
        del db["k"]
        assert "k" not in db
    finally:
        db.close()


def test_nana_db_sqlite_url_basic(db_path):
    url = f"sqlite:///{db_path}"
    db = NanaDB(url)
    try:
        db["a"] = 123
        assert db["a"] == 123
        assert len(list(db.keys())) == 1
    finally:
        db.close()


def test_nana_db_postgres_not_implemented():
    with pytest.raises(NotImplementedError):
        NanaDB("postgresql://user:pass@localhost:5432/testdb")


@pytest.mark.asyncio
async def test_async_nana_db_sqlite_basic(db_path):
    async with AsyncNanaDB(db_path) as db:
        await db.aset("x", [1, 2, 3])
        got = await db.aget("x")
        assert got == [1, 2, 3]
