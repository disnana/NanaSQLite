import apsw
import pytest

from nanasqlite import (
    AsyncNanaSQLite,
    NanaSQLiteClosedError,
    NanaSQLiteDatabaseError,
    NanaSQLiteError,
    NanaSQLiteValidationError,
)


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_security_async.db")


@pytest.mark.asyncio
async def test_async_sql_validation_strict_mode(db_path):
    db = AsyncNanaSQLite(db_path, strict_sql_validation=True)

    # Normal execution (COUNT is default allowed)
    await db.aquery(columns=["COUNT(*)"])

    # Unauthorized function in strict mode
    with pytest.raises(NanaSQLiteValidationError) as excinfo:
        await db.aquery(columns=["DANGEROUS_FUNC(*)"])
    assert "DANGEROUS_FUNC" in str(excinfo.value)
    await db.close()


@pytest.mark.asyncio
async def test_async_sql_validation_warning_mode(db_path):
    db = AsyncNanaSQLite(db_path, strict_sql_validation=False)

    # NanaSQLite emits a warning during validation but allows the query to execute.
    # Execution will fail in SQLite because the function doesn't exist,
    # but we only care about the warning here.
    with pytest.warns(UserWarning, match="DANGEROUS_FUNC"):
        try:
            await db.aquery(columns=["DANGEROUS_FUNC(*)"])
        except (apsw.Error, ValueError, NanaSQLiteError):
            # SQLite may fail because DANGEROUS_FUNC is not defined;
            # this test only asserts that a warning was emitted.
            pass
    await db.close()


@pytest.mark.asyncio
async def test_async_allowed_sql_functions_init(db_path):
    db = AsyncNanaSQLite(db_path, strict_sql_validation=True, allowed_sql_functions=["MY_CUSTOM_FUNC"])

    # Should pass validation, but might fail execution if function not actually defined in SQLite
    with pytest.raises(NanaSQLiteDatabaseError) as excinfo:
        await db.aquery(columns=["MY_CUSTOM_FUNC(*)"])

    assert "no such function" in str(excinfo.value).lower()
    await db.close()


@pytest.mark.asyncio
async def test_async_allowed_sql_functions_query(db_path):
    db = AsyncNanaSQLite(db_path, strict_sql_validation=True)

    # Should fail by default
    with pytest.raises(NanaSQLiteValidationError):
        await db.aquery(columns=["LOCAL_FUNC(*)"])

    # Should work with query-level permission (validation side)
    with pytest.raises(NanaSQLiteDatabaseError) as excinfo:
        await db.aquery(columns=["LOCAL_FUNC(*)"], allowed_sql_functions=["LOCAL_FUNC"])

    assert "no such function" in str(excinfo.value).lower()
    await db.close()


@pytest.mark.asyncio
async def test_async_forbidden_sql_functions(db_path):
    db = AsyncNanaSQLite(db_path, strict_sql_validation=True, allowed_sql_functions=["SOME_FUNC"])

    # Validation passes
    with pytest.raises(NanaSQLiteDatabaseError) as excinfo:
        await db.aquery(columns=["SOME_FUNC(*)"])

    assert "no such function" in str(excinfo.value).lower()

    # Specific forbidden
    with pytest.raises(NanaSQLiteValidationError):
        await db.aquery(columns=["SOME_FUNC(*)"], forbidden_sql_functions=["SOME_FUNC"])
    await db.close()


@pytest.mark.asyncio
async def test_async_override_allowed(db_path):
    db = AsyncNanaSQLite(db_path, strict_sql_validation=True, allowed_sql_functions=["FUNC_A"])

    # FUNC_A is allowed globally (validation side)
    with pytest.raises(NanaSQLiteDatabaseError) as excinfo:
        await db.aquery(columns=["FUNC_A(*)"])

    assert "no such function" in str(excinfo.value).lower()

    # With override_allowed=True, FUNC_A is no longer allowed unless included in method call
    with pytest.raises(NanaSQLiteValidationError):
        await db.aquery(columns=["FUNC_A(*)"], allowed_sql_functions=["FUNC_B"], override_allowed=True)

    # Only FUNC_B works (validation side)
    with pytest.raises(NanaSQLiteDatabaseError) as excinfo:
        await db.aquery(columns=["FUNC_B(*)"], allowed_sql_functions=["FUNC_B"], override_allowed=True)

    assert "no such function" in str(excinfo.value).lower()
    await db.close()


@pytest.mark.asyncio
async def test_async_redos_protection(db_path):
    db = AsyncNanaSQLite(db_path, max_clause_length=10, strict_sql_validation=True)

    # Ensure table and schema exists for execution test
    await db.aset("test", "data")

    # Normal length
    await db.aquery(where="key = ?", parameters=("test",))

    # Too long
    with pytest.raises(NanaSQLiteValidationError) as excinfo:
        await db.aquery(where="key = " + "?" * 20)
    assert "exceeds maximum length" in str(excinfo.value)
    await db.close()


@pytest.mark.asyncio
async def test_async_connection_closed_error(tmp_path):
    db_path = str(tmp_path / "test_connection_async.db")
    db = AsyncNanaSQLite(db_path)
    child = await db.atable("slave")

    await db.close()

    # Operations on closed connection
    with pytest.raises(NanaSQLiteClosedError):
        await db.aset("key", "value")

    # Operations on child of closed connection
    with pytest.raises(NanaSQLiteClosedError) as excinfo:
        await child.aset("key", "value")
    assert "Parent database connection is closed" in str(excinfo.value)
    assert "table: 'slave'" in str(excinfo.value)

    # Self closed
    db2_path = str(tmp_path / "test2_async.db")
    db2 = AsyncNanaSQLite(db2_path)
    await db2.close()
    with pytest.raises(NanaSQLiteClosedError):
        await db2.aset("key", "val")
