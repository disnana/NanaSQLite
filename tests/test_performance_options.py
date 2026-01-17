import pytest

from nanasqlite import AsyncNanaSQLite, NanaSQLite


def test_opt_in_pragmas_apply(tmp_path):
    db_path = str(tmp_path / "opts.db")

    db = NanaSQLite(
        db_path,
        optimize=True,
        busy_timeout=1234,
        exclusive_lock=True,
        wal_autocheckpoint=777,
    )

    # busy_timeout
    assert db.pragma("busy_timeout") == 1234

    # locking_mode returns a string like 'exclusive'
    mode = db.pragma("locking_mode")
    assert isinstance(mode, str)
    assert mode.lower() == "exclusive"

    # wal_autocheckpoint
    assert db.pragma("wal_autocheckpoint") == 777


def test_checkpoint_returns_tuple(tmp_path):
    db_path = str(tmp_path / "cp.db")
    db = NanaSQLite(db_path, optimize=True)
    # Do some writes to create a WAL file
    for i in range(100):
        db[f"k{i}"] = {"v": i}

    res = db.checkpoint("TRUNCATE")
    assert isinstance(res, tuple) and len(res) == 3
    assert all(isinstance(x, int) for x in res)


@pytest.mark.asyncio
async def test_async_checkpoint(tmp_path):
    db_path = str(tmp_path / "acp.db")
    async with AsyncNanaSQLite(db_path, optimize=True) as adb:
        for i in range(50):
            await adb.aset(f"k{i}", {"v": i})

        res = await adb.acheckpoint("FULL")
        assert isinstance(res, tuple) and len(res) == 3
        assert all(isinstance(x, int) for x in res)
