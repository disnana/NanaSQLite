import pytest
from pydantic import BaseModel

from nanasqlite import AsyncNanaSQLite, NanaSQLite
from nanasqlite.exceptions import NanaSQLiteValidationError
from nanasqlite.hooks import CheckHook, ForeignKeyHook, PydanticHook, UniqueHook


def test_check_hook(tmp_path):
    db_path = tmp_path / "test.db"
    db = NanaSQLite(str(db_path))

    db.add_hook(CheckHook(lambda k, v: isinstance(v, dict) and v.get("age", 0) >= 18, "Age must be >= 18"))

    db["user1"] = {"name": "Alice", "age": 20}

    with pytest.raises(NanaSQLiteValidationError, match="Age must be >= 18"):
        db["user2"] = {"name": "Bob", "age": 15}

    with pytest.raises(NanaSQLiteValidationError, match="Age must be >= 18"):
        db["user3"] = "invalid format"


def test_unique_hook(tmp_path):
    db_path = tmp_path / "test.db"
    db = NanaSQLite(str(db_path))
    db.add_hook(UniqueHook("email"))

    db["user1"] = {"email": "test@example.com"}
    db["user2"] = {"email": "other@example.com"}

    # Should fail for collision
    with pytest.raises(NanaSQLiteValidationError, match="Unique constraint violation"):
        db["user3"] = {"email": "test@example.com"}

    # Self updates are allowed
    db["user1"] = {"email": "test@example.com", "updated": True}


def test_foreign_key_hook(tmp_path):
    db_path = tmp_path / "test.db"
    # Using same DB with different tables
    main_db = NanaSQLite(str(db_path), table="groups")
    main_db["group1"] = {"name": "Admins"}
    main_db["group2"] = {"name": "Users"}

    users_db = NanaSQLite(str(db_path), table="users")
    users_db.add_hook(ForeignKeyHook("group_id", main_db))

    # Should work
    users_db["user1"] = {"name": "Alice", "group_id": "group1"}

    # Should fail due to foreign key violation
    with pytest.raises(NanaSQLiteValidationError, match="Foreign key constraint violation"):
        users_db["user2"] = {"name": "Bob", "group_id": "group3"}


class UserConfig(BaseModel):
    version: int
    data: str


def test_pydantic_hook(tmp_path):
    db_path = tmp_path / "test.db"
    db = NanaSQLite(str(db_path))
    db.add_hook(PydanticHook(UserConfig))

    db["cfg1"] = UserConfig(version=1, data="hello")

    # Retrieves as Pydantic model natively
    res = db["cfg1"]
    assert isinstance(res, UserConfig)
    assert res.version == 1
    assert res.data == "hello"

    # Underlying DB stores dict
    raw_data = db._read_from_db("cfg1")
    assert raw_data == {"version": 1, "data": "hello"}

    # Writing a dict validates and converts it instantly
    db["cfg2"] = {"version": 2, "data": "world"}
    res2 = db.get("cfg2")
    assert isinstance(res2, UserConfig)
    assert res2.version == 2

    # Fails if invalid
    with pytest.raises(NanaSQLiteValidationError, match="Model validation failed"):
        db["cfg3"] = {"version": "invalid", "data": "test"}


@pytest.mark.asyncio
async def test_async_hooks(tmp_path):
    db_path = tmp_path / "test.db"
    async with AsyncNanaSQLite(str(db_path)) as db:
        await db.add_hook(CheckHook(lambda k, v: v.get("score", 0) > 0, "Score must be positive"))

        await db.aset("player1", {"score": 100})

        with pytest.raises(NanaSQLiteValidationError):
            await db.aset("player2", {"score": -10})

        res = await db.aget("player1")
        assert res["score"] == 100
