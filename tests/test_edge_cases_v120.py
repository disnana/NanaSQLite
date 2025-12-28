import pytest

from nanasqlite import AsyncNanaSQLite, NanaSQLite

# ==================== Synchronous Edge Cases ====================


class TestSyncEdgeCases:
    @pytest.fixture
    def db(self, tmp_path):
        db_path = str(tmp_path / "edge_cases_sync.db")
        conn = NanaSQLite(db_path)
        yield conn
        conn.close()

    def test_batch_operations_empty(self, db):
        """Verify behavior with empty inputs for batch operations."""
        # batch_get with empty list -> empty dict
        assert db.batch_get([]) == {}

        # batch_update with empty dict -> no error
        db.batch_update({})

        # batch_delete with empty list -> no error
        db.batch_delete([])

    def test_pagination_edge_cases(self, db):
        """Verify pagination edge cases."""
        # Setup data
        db.batch_update({f"k{i}": i for i in range(10)})
        table = "data"  # default table

        # limit=0 -> empty list
        results = db.query_with_pagination(table_name=table, limit=0)
        assert len(results) == 0

        # offset > total -> empty list
        results = db.query_with_pagination(table_name=table, limit=5, offset=100)
        assert len(results) == 0

        # offset=0 -> start from beginning
        results = db.query_with_pagination(table_name=table, limit=5, offset=0)
        assert len(results) == 5

    def test_pagination_negative_values(self, db):
        """Verify negative values in pagination (Validation Check)."""
        # NanaSQLite explicitly invalidates negative limits
        db.batch_update({"a": 1, "b": 2})

        with pytest.raises(ValueError, match="limit must be non-negative"):
            db.query_with_pagination(limit=-1)


# ==================== Asynchronous Edge Cases ====================


class TestAsyncEdgeCases:
    @pytest.fixture
    def db_path(self, tmp_path):
        return str(tmp_path / "edge_cases_async.db")

    @pytest.mark.asyncio
    async def test_async_batch_operations_empty(self, db_path):
        """Verify async behavior with empty inputs."""
        async with AsyncNanaSQLite(db_path) as db:
            # abatch_get
            res = await db.abatch_get([])
            assert res == {}

            # abatch_update
            await db.abatch_update({})

            # abatch_delete
            await db.abatch_delete([])

    @pytest.mark.asyncio
    async def test_async_pagination_edge_cases(self, db_path):
        """Verify async pagination edge cases."""
        async with AsyncNanaSQLite(db_path) as db:
            # Setup
            await db.abatch_update({f"k{i}": i for i in range(10)})

            # limit=0
            results = await db.aquery_with_pagination(limit=0)
            assert len(results) == 0

            # offset > total
            results = await db.aquery_with_pagination(limit=5, offset=100)
            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_async_query_empty_conditions(self, db_path):
        """Verify query behavior with minimal arguments."""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key", "value")

            # No args -> essentially 'SELECT *' (depends on implementation defaults)
            # Core implementation of `query` constructs SELECT specific columns or *
            results = await db.aquery()
            assert len(results) > 0
            assert results[0]["key"] == "key"
