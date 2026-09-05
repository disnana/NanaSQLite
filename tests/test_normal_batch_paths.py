"""Batch fast paths must agree with stored values for mixed cache states."""

import pytest

from nanasqlite import AsyncNanaSQLite, NanaSQLite


@pytest.mark.parametrize("warm", [0, 5, 9, 10])
@pytest.mark.parametrize("negative", [False, True])
@pytest.mark.parametrize("strategy,options", [
    ("unbounded", {}), ("unbounded", {"cache_size": 5}),
    ("lru", {"cache_size": 5}), ("ttl", {"cache_ttl": 60}),
])
def test_mixed_batch_values(tmp_path, warm, negative, strategy, options):
    model = {str(i): {"value": i} for i in range(10)}
    with NanaSQLite(str(tmp_path / "data.db"), cache_strategy=strategy, **options) as db:
        db.batch_update(model)
        db.clear_cache()
        db.batch_get(list(model)[:warm])
        if negative:
            assert db.get("missing") is None
        keys = ["missing", *model, "0", "missing"]
        assert db.batch_get(keys) == model
        assert db.batch_get(keys) == model
        db["missing"] = None
        assert db.batch_get(keys) == {**model, "missing": None}


@pytest.mark.asyncio
@pytest.mark.parametrize("warm", [0, 5, 9, 10])
@pytest.mark.parametrize("negative", [False, True])
async def test_async_mixed_batch_values(tmp_path, warm, negative):
    model = {str(i): {"value": i} for i in range(10)}
    path = str(tmp_path / "data.db")
    with NanaSQLite(path) as seed:
        seed.batch_update(model)
    async with AsyncNanaSQLite(path) as db:
        await db.abatch_get(list(model)[:warm])
        if negative:
            assert await db.aget("missing") is None
        keys = ["missing", *model, "0", "missing"]
        assert await db.abatch_get(keys) == model
        assert await db.abatch_get(keys) == model
        await db.aset("missing", None)
        assert await db.abatch_get(keys) == {**model, "missing": None}
