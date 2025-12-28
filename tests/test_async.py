"""
NanaSQLite Async テストスイート

非同期機能の包括的なテスト
- 非同期dict風インターフェース
- 非同期バッチ操作
- 非同期SQL実行
- 非同期Pydanticサポート
- コンテキストマネージャ
"""

import asyncio
import os
import sys
import tempfile

import pytest

# テスト実行時のパス設定
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from nanasqlite import AsyncNanaSQLite

# ==================== Fixtures ====================


@pytest.fixture
def db_path():
    """一時DBパスを提供"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test_async.db")


@pytest.fixture
async def async_db(db_path):
    """AsyncNanaSQLiteインスタンスを提供"""
    db = AsyncNanaSQLite(db_path)
    yield db
    await db.close()


# ==================== 基本的な非同期操作テスト ====================


class TestAsyncBasicOperations:
    """基本的な非同期操作のテスト"""

    @pytest.mark.asyncio
    async def test_async_set_and_get_string(self, db_path):
        """文字列の非同期設定と取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("name", "Nana")
            result = await db.aget("name")

            assert result == "Nana"
            assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_async_set_and_get_integer(self, db_path):
        """整数の非同期設定と取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("age", 20)
            result = await db.aget("age")

            assert result == 20
            assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_async_set_and_get_dict(self, db_path):
        """辞書の非同期設定と取得"""
        async with AsyncNanaSQLite(db_path) as db:
            data = {"name": "Nana", "age": 20, "tags": ["admin", "active"]}
            await db.aset("user", data)
            result = await db.aget("user")

            assert result == data
            assert isinstance(result, dict)
            assert result["name"] == "Nana"
            assert result["age"] == 20
            assert result["tags"] == ["admin", "active"]

    @pytest.mark.asyncio
    async def test_async_set_and_get_list(self, db_path):
        """リストの非同期設定と取得"""
        async with AsyncNanaSQLite(db_path) as db:
            data = [1, 2, 3, "four", 5.0, None, True]
            await db.aset("list", data)
            result = await db.aget("list")

            assert result == data
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_async_get_with_default(self, db_path):
        """デフォルト値を使った非同期取得"""
        async with AsyncNanaSQLite(db_path) as db:
            result = await db.aget("nonexistent", "default_value")
            assert result == "default_value"

    @pytest.mark.asyncio
    async def test_async_contains(self, db_path):
        """非同期存在確認"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")

            exists = await db.acontains("key1")
            assert exists is True

            not_exists = await db.acontains("key2")
            assert not_exists is False

    @pytest.mark.asyncio
    async def test_async_delete(self, db_path):
        """非同期削除"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("temp", "data")
            assert await db.acontains("temp")

            await db.adelete("temp")
            assert not await db.acontains("temp")

    @pytest.mark.asyncio
    async def test_async_len(self, db_path):
        """非同期長さ取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")
            await db.aset("key2", "value2")
            await db.aset("key3", "value3")

            length = await db.alen()
            assert length == 3


# ==================== 非同期dict風メソッドテスト ====================


class TestAsyncDictMethods:
    """非同期dict風メソッドのテスト"""

    @pytest.mark.asyncio
    async def test_async_keys(self, db_path):
        """非同期キー取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")
            await db.aset("key2", "value2")
            await db.aset("key3", "value3")

            keys = await db.akeys()
            assert sorted(keys) == ["key1", "key2", "key3"]

    @pytest.mark.asyncio
    async def test_async_values(self, db_path):
        """非同期値取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")
            await db.aset("key2", "value2")

            values = await db.avalues()
            assert sorted(values) == ["value1", "value2"]

    @pytest.mark.asyncio
    async def test_async_items(self, db_path):
        """非同期アイテム取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")
            await db.aset("key2", "value2")

            items = await db.aitems()
            items_dict = dict(items)
            assert items_dict == {"key1": "value1", "key2": "value2"}

    @pytest.mark.asyncio
    async def test_async_pop(self, db_path):
        """非同期pop"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")

            value = await db.apop("key1")
            assert value == "value1"
            assert not await db.acontains("key1")

    @pytest.mark.asyncio
    async def test_async_pop_with_default(self, db_path):
        """デフォルト値を使った非同期pop"""
        async with AsyncNanaSQLite(db_path) as db:
            value = await db.apop("nonexistent", "default")
            assert value == "default"

    @pytest.mark.asyncio
    async def test_async_update(self, db_path):
        """非同期update"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aupdate({"key1": "value1", "key2": "value2"})

            assert await db.aget("key1") == "value1"
            assert await db.aget("key2") == "value2"

    @pytest.mark.asyncio
    async def test_async_update_kwargs(self, db_path):
        """キーワード引数を使った非同期update"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aupdate(key1="value1", key2="value2")

            assert await db.aget("key1") == "value1"
            assert await db.aget("key2") == "value2"

    @pytest.mark.asyncio
    async def test_async_clear(self, db_path):
        """非同期clear"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")
            await db.aset("key2", "value2")

            await db.aclear()

            assert await db.alen() == 0

    @pytest.mark.asyncio
    async def test_async_setdefault(self, db_path):
        """非同期setdefault"""
        async with AsyncNanaSQLite(db_path) as db:
            # 存在しないキー
            value = await db.asetdefault("key1", "default1")
            assert value == "default1"
            assert await db.aget("key1") == "default1"

            # 既存のキー
            value = await db.asetdefault("key1", "default2")
            assert value == "default1"  # 既存の値が返される


# ==================== 非同期特殊メソッドテスト ====================


class TestAsyncSpecialMethods:
    """非同期特殊メソッドのテスト"""

    @pytest.mark.asyncio
    async def test_async_load_all(self, db_path):
        """非同期一括ロード"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")
            await db.aset("key2", "value2")

            await db.load_all()

            # キャッシュされているか確認
            assert await db.is_cached("key1")
            assert await db.is_cached("key2")

    @pytest.mark.asyncio
    async def test_async_refresh(self, db_path):
        """非同期refresh"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")
            await db.refresh("key1")

            # 全リフレッシュ
            await db.refresh()

    @pytest.mark.asyncio
    async def test_async_batch_update(self, db_path):
        """非同期バッチ更新"""
        async with AsyncNanaSQLite(db_path) as db:
            data = {"key1": "value1", "key2": "value2", "key3": {"nested": "data"}, "key4": [1, 2, 3]}

            await db.batch_update(data)

            assert await db.aget("key1") == "value1"
            assert await db.aget("key2") == "value2"
            assert await db.aget("key3") == {"nested": "data"}
            assert await db.aget("key4") == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_async_batch_delete(self, db_path):
        """非同期バッチ削除"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")
            await db.aset("key2", "value2")
            await db.aset("key3", "value3")

            await db.batch_delete(["key1", "key2"])

            assert not await db.acontains("key1")
            assert not await db.acontains("key2")
            assert await db.acontains("key3")

    @pytest.mark.asyncio
    async def test_async_batch_get(self, db_path):
        """非同期バッチ取得"""
        async with AsyncNanaSQLite(db_path) as db:
            data = {f"k{i}": i for i in range(10)}
            await db.batch_update(data)

            keys = ["k0", "k2", "k5", "nonexistent"]
            result = await db.abatch_get(keys)

            assert result["k0"] == 0
            assert result["k2"] == 2
            assert result["k5"] == 5
            assert "nonexistent" not in result
            assert len(result) == 3

    @pytest.mark.asyncio
    async def test_async_to_dict(self, db_path):
        """非同期to_dict"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")
            await db.aset("key2", "value2")

            data = await db.to_dict()
            assert data == {"key1": "value1", "key2": "value2"}

    @pytest.mark.asyncio
    async def test_async_copy(self, db_path):
        """非同期copy"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")
            await db.aset("key2", "value2")

            data = await db.copy()
            assert data == {"key1": "value1", "key2": "value2"}

    @pytest.mark.asyncio
    async def test_async_get_fresh(self, db_path):
        """非同期get_fresh"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")

            # DBから直接読み込み
            value = await db.get_fresh("key1")
            assert value == "value1"


# ==================== 非同期SQL実行テスト ====================


class TestAsyncSQLExecution:
    """非同期SQL実行のテスト"""

    @pytest.mark.asyncio
    async def test_async_execute(self, db_path):
        """非同期SQL実行"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("user1", {"name": "Alice"})
            await db.aset("user2", {"name": "Bob"})

            cursor = await db.execute("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
            rows = list(cursor)
            assert len(rows) == 2

    @pytest.mark.asyncio
    async def test_async_aexecute_many(self, db_path):
        """非同期aexecute_manyテスト"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})

            users = [(1, "Alice"), (2, "Bob"), (3, "Charlie")]

            await db.aexecute_many("INSERT INTO users (id, name) VALUES (?, ?)", users)

            results = await db.query("users", order_by="id")
            assert len(results) == 3
            assert results[0]["name"] == "Alice"
            assert results[2]["name"] == "Charlie"

    @pytest.mark.asyncio
    async def test_async_fetch_one(self, db_path):
        """非同期fetch_one"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("user", {"name": "Alice"})

            row = await db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
            assert row is not None

    @pytest.mark.asyncio
    async def test_async_fetch_all(self, db_path):
        """非同期fetch_all"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("user1", {"name": "Alice"})
            await db.aset("user2", {"name": "Bob"})

            rows = await db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
            assert len(rows) == 2


# ==================== 非同期SQLiteラッパー関数テスト ====================


class TestAsyncSQLiteWrappers:
    """非同期SQLiteラッパー関数のテスト"""

    @pytest.mark.asyncio
    async def test_async_create_table(self, db_path):
        """非同期テーブル作成"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table(
                "users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT NOT NULL", "email": "TEXT UNIQUE"}
            )

            exists = await db.table_exists("users")
            assert exists is True

    @pytest.mark.asyncio
    async def test_async_create_index(self, db_path):
        """非同期インデックス作成"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "email": "TEXT"})

            await db.create_index("idx_users_email", "users", ["email"])

    @pytest.mark.asyncio
    async def test_async_query(self, db_path):
        """非同期クエリ"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"})

            await db.sql_insert("users", {"id": 1, "name": "Alice", "age": 25})
            await db.sql_insert("users", {"id": 2, "name": "Bob", "age": 30})

            results = await db.query(
                table_name="users",
                columns=["id", "name", "age"],
                where="age > ?",
                parameters=(20,),
                order_by="name ASC",
            )

            assert len(results) == 2
            assert results[0]["name"] == "Alice"
            assert results[1]["name"] == "Bob"

    @pytest.mark.asyncio
    async def test_async_list_tables(self, db_path):
        """非同期テーブル一覧取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY"})
            await db.create_table("posts", {"id": "INTEGER PRIMARY KEY"})

            tables = await db.list_tables()
            assert "users" in tables
            assert "posts" in tables

    @pytest.mark.asyncio
    async def test_async_drop_table(self, db_path):
        """非同期テーブル削除"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("temp", {"id": "INTEGER PRIMARY KEY"})
            assert await db.table_exists("temp")

            await db.drop_table("temp")
            assert not await db.table_exists("temp")

    @pytest.mark.asyncio
    async def test_async_sql_insert(self, db_path):
        """非同期SQL INSERT"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"})

            rowid = await db.sql_insert("users", {"name": "Alice", "age": 25})

            assert rowid > 0

    @pytest.mark.asyncio
    async def test_async_sql_update(self, db_path):
        """非同期SQL UPDATE"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"})

            await db.sql_insert("users", {"name": "Alice", "age": 25})

            count = await db.sql_update("users", {"age": 26}, "name = ?", ("Alice",))
            assert count == 1

    @pytest.mark.asyncio
    async def test_async_sql_delete(self, db_path):
        """非同期SQL DELETE"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"})

            await db.sql_insert("users", {"name": "Alice", "age": 25})
            await db.sql_insert("users", {"name": "Bob", "age": 17})

            count = await db.sql_delete("users", "age < ?", (18,))
            assert count == 1

    @pytest.mark.asyncio
    async def test_async_vacuum(self, db_path):
        """非同期VACUUM"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")
            await db.adelete("key1")

            await db.vacuum()


# ==================== 並行性テスト ====================


class TestAsyncConcurrency:
    """非同期並行処理のテスト"""

    @pytest.mark.asyncio
    async def test_concurrent_reads(self, db_path):
        """並行読み込み"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key1", "value1")
            await db.aset("key2", "value2")
            await db.aset("key3", "value3")

            # 並行読み込み
            results = await asyncio.gather(db.aget("key1"), db.aget("key2"), db.aget("key3"))

            assert results == ["value1", "value2", "value3"]

    @pytest.mark.asyncio
    async def test_concurrent_writes(self, db_path):
        """並行書き込み"""
        async with AsyncNanaSQLite(db_path) as db:
            # 並行書き込み
            await asyncio.gather(db.aset("key1", "value1"), db.aset("key2", "value2"), db.aset("key3", "value3"))

            assert await db.aget("key1") == "value1"
            assert await db.aget("key2") == "value2"
            assert await db.aget("key3") == "value3"

    @pytest.mark.asyncio
    async def test_concurrent_mixed_operations(self, db_path):
        """並行混合操作"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("initial", "data")

            # 読み書き混合の並行操作
            _ = await asyncio.gather(
                db.aset("key1", "value1"),
                db.aget("initial"),
                db.aset("key2", "value2"),
                db.acontains("initial"),
                db.aset("key3", "value3"),
            )

            # 最後の書き込みが完了していることを確認
            assert await db.acontains("key1")
            assert await db.acontains("key2")
            assert await db.acontains("key3")


# ==================== コンテキストマネージャテスト ====================


class TestAsyncContextManager:
    """非同期コンテキストマネージャのテスト"""

    @pytest.mark.asyncio
    async def test_async_context_manager(self, db_path):
        """非同期コンテキストマネージャ"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("key", "value")
            assert await db.aget("key") == "value"

        # コンテキスト外ではクローズされている
        # 新しいインスタンスでデータが永続化されていることを確認
        async with AsyncNanaSQLite(db_path) as db2:
            assert await db2.aget("key") == "value"


# ==================== Pydanticサポートテスト ====================


class TestAsyncPydanticSupport:
    """非同期Pydanticサポートのテスト"""

    @pytest.mark.asyncio
    async def test_async_pydantic_model(self, db_path):
        """非同期Pydanticモデル操作"""
        try:
            from pydantic import BaseModel

            class User(BaseModel):
                name: str
                age: int
                email: str

            async with AsyncNanaSQLite(db_path) as db:
                user = User(name="Alice", age=25, email="alice@example.com")
                await db.set_model("user", user)

                retrieved = await db.get_model("user", User)
                assert retrieved.name == "Alice"
                assert retrieved.age == 25
                assert retrieved.email == "alice@example.com"

        except ImportError:
            pytest.skip("Pydantic not installed")


# ==================== パフォーマンステスト ====================


class TestAsyncPerformance:
    """非同期パフォーマンステスト"""

    @pytest.mark.asyncio
    async def test_large_batch_update(self, db_path):
        """大量データの非同期バッチ更新"""
        async with AsyncNanaSQLite(db_path) as db:
            # 1000件のデータを準備
            data = {f"key_{i}": f"value_{i}" for i in range(1000)}

            await db.batch_update(data)

            # 確認
            assert await db.alen() == 1000
            assert await db.aget("key_0") == "value_0"
            assert await db.aget("key_999") == "value_999"

    @pytest.mark.asyncio
    async def test_large_batch_delete(self, db_path):
        """大量データの非同期バッチ削除"""
        async with AsyncNanaSQLite(db_path) as db:
            # 1000件のデータを準備
            data = {f"key_{i}": f"value_{i}" for i in range(1000)}
            await db.batch_update(data)

            # 500件削除
            keys_to_delete = [f"key_{i}" for i in range(500)]
            await db.batch_delete(keys_to_delete)

            # 確認
            assert await db.alen() == 500
            assert not await db.acontains("key_0")
            assert await db.acontains("key_500")


# ==================== エラーハンドリングテスト ====================


class TestAsyncErrorHandling:
    """非同期エラーハンドリングのテスト"""

    @pytest.mark.asyncio
    async def test_async_key_error(self, db_path):
        """存在しないキーの削除でKeyError"""
        async with AsyncNanaSQLite(db_path) as db:
            with pytest.raises(KeyError):
                await db.adelete("nonexistent")

    @pytest.mark.asyncio
    async def test_async_get_nonexistent(self, db_path):
        """存在しないキーの取得"""
        async with AsyncNanaSQLite(db_path) as db:
            # デフォルト値なしの場合はNoneが返る（getの仕様）
            result = await db.aget("nonexistent")
            assert result is None

            # デフォルト値ありの場合
            result = await db.aget("nonexistent", "default")
            assert result == "default"


# ==================== データ型テスト ====================


class TestAsyncDataTypes:
    """非同期データ型テスト"""

    @pytest.mark.asyncio
    async def test_async_set_and_get_float(self, db_path):
        """浮動小数点の非同期設定と取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("pi", 3.14159)
            result = await db.aget("pi")

            assert result == 3.14159
            assert isinstance(result, float)

    @pytest.mark.asyncio
    async def test_async_set_and_get_boolean(self, db_path):
        """ブール値の非同期設定と取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("active", True)
            await db.aset("deleted", False)

            assert await db.aget("active") is True
            assert await db.aget("deleted") is False

    @pytest.mark.asyncio
    async def test_async_set_and_get_none(self, db_path):
        """None値の非同期設定と取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("empty", None)
            result = await db.aget("empty")

            assert result is None


# ==================== ネスト構造テスト ====================


class TestAsyncNestedStructures:
    """非同期ネスト構造テスト"""

    def _create_nested_dict(self, depth: int) -> dict:
        """指定階層のネストしたdictを作成"""
        if depth <= 0:
            return {"leaf": "value", "number": depth}
        return {"level": depth, "child": self._create_nested_dict(depth - 1)}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("depth", range(1, 11))
    async def test_async_nested_dict_depth(self, db_path, depth):
        """階層ごとのネストしたdictのテスト（1〜10階層）"""
        async with AsyncNanaSQLite(db_path) as db:
            original = self._create_nested_dict(depth)
            key = f"nested_{depth}"

            await db.aset(key, original)
            result = await db.aget(key)

            assert result == original

    @pytest.mark.asyncio
    async def test_async_deeply_nested_list(self, db_path):
        """深くネストしたリストのテスト"""
        async with AsyncNanaSQLite(db_path) as db:
            # 15階層のネストしたリスト
            nested = "deepest"
            for i in range(15):
                nested = [nested, i]

            await db.aset("nested_list", nested)
            result = await db.aget("nested_list")

            assert result == nested

    @pytest.mark.asyncio
    async def test_async_mixed_nested_structure(self, db_path):
        """混合ネスト構造（dict + list）のテスト"""
        async with AsyncNanaSQLite(db_path) as db:
            original = {
                "users": [
                    {
                        "name": "Alice",
                        "friends": ["Bob", "Charlie"],
                        "metadata": {
                            "created": "2024-01-01",
                            "tags": ["admin", "active"],
                            "settings": {"theme": "dark", "notifications": {"email": True, "push": False}},
                        },
                    }
                ],
                "count": 1,
            }

            await db.aset("complex", original)
            result = await db.aget("complex")

            assert result == original


# ==================== 永続化テスト ====================


class TestAsyncPersistence:
    """非同期永続化テスト"""

    @pytest.mark.asyncio
    async def test_async_persistence_after_close(self, db_path):
        """closeした後もデータが永続化されている"""
        # 書き込み
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("persistent", {"message": "Hello!", "count": 42})

        # 再度開いて確認
        async with AsyncNanaSQLite(db_path) as db2:
            result = await db2.aget("persistent")
            assert result["message"] == "Hello!"
            assert result["count"] == 42

    @pytest.mark.asyncio
    async def test_async_persistence_multiple_keys(self, db_path):
        """複数キーの永続化"""
        # 書き込み
        async with AsyncNanaSQLite(db_path) as db:
            for i in range(50):
                await db.aset(f"key_{i}", {"index": i, "square": i * i})

        # 検証
        async with AsyncNanaSQLite(db_path) as db2:
            assert await db2.alen() == 50
            for i in range(50):
                result = await db2.aget(f"key_{i}")
                assert result["index"] == i
                assert result["square"] == i * i

    @pytest.mark.asyncio
    async def test_async_persistence_with_updates(self, db_path):
        """更新後の永続化"""
        # 初期書き込み
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("data", {"version": 1})

        # 更新
        async with AsyncNanaSQLite(db_path) as db2:
            await db2.aset("data", {"version": 2})

        # 検証
        async with AsyncNanaSQLite(db_path) as db3:
            result = await db3.aget("data")
            assert result["version"] == 2


# ==================== スキーマ管理テスト ====================


class TestAsyncSchemaManagement:
    """非同期スキーマ管理テスト"""

    @pytest.mark.asyncio
    async def test_async_drop_index(self, db_path):
        """非同期インデックス削除"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "email": "TEXT"})
            await db.create_index("idx_email", "users", ["email"])

            await db.drop_index("idx_email")
            # 削除後もテーブルは存在
            assert await db.table_exists("users")

    @pytest.mark.asyncio
    async def test_async_alter_table_add_column(self, db_path):
        """非同期カラム追加"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})

            # sync_dbを使用してカラム追加
            db.sync_db.alter_table_add_column("users", "age", "INTEGER", default=0)

            # 追加されたカラムを確認
            schema = db.sync_db.get_table_schema("users")
            column_names = [col["name"] for col in schema]
            assert "age" in column_names

    @pytest.mark.asyncio
    async def test_async_get_table_schema(self, db_path):
        """非同期スキーマ取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT NOT NULL", "email": "TEXT"})

            schema = db.sync_db.get_table_schema("users")
            column_names = [col["name"] for col in schema]
            assert "id" in column_names
            assert "name" in column_names
            assert "email" in column_names

    @pytest.mark.asyncio
    async def test_async_list_indexes(self, db_path):
        """非同期インデックス一覧"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "email": "TEXT"})
            await db.create_index("idx_email", "users", ["email"])

            indexes = db.sync_db.list_indexes("users")
            index_names = [idx["name"] for idx in indexes]
            assert "idx_email" in index_names


# ==================== データ操作テスト ====================


class TestAsyncDataOperations:
    """非同期データ操作テスト"""

    @pytest.mark.asyncio
    async def test_async_upsert(self, db_path):
        """非同期UPSERT"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"})

            # Insert
            rowid1 = db.sync_db.upsert("users", {"id": 1, "name": "Alice", "age": 25})
            assert rowid1 > 0

            # Update (same id)
            db.sync_db.upsert("users", {"id": 1, "name": "Alice", "age": 26})

            # 確認
            results = await db.query("users", where="id = ?", parameters=(1,))
            assert len(results) == 1
            assert results[0]["age"] == 26

    @pytest.mark.asyncio
    async def test_async_count(self, db_path):
        """非同期レコード数取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"})

            await db.sql_insert("users", {"name": "Alice", "age": 25})
            await db.sql_insert("users", {"name": "Bob", "age": 30})
            await db.sql_insert("users", {"name": "Charlie", "age": 17})

            # 全件数
            total = db.sync_db.count("users")
            assert total == 3

            # 条件付き
            adults = db.sync_db.count("users", "age >= ?", (18,))
            assert adults == 2

    @pytest.mark.asyncio
    async def test_async_exists(self, db_path):
        """非同期レコード存在確認"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "email": "TEXT UNIQUE"})

            await db.sql_insert("users", {"email": "alice@example.com"})

            assert db.sync_db.exists("users", "email = ?", ("alice@example.com",))
            assert not db.sync_db.exists("users", "email = ?", ("bob@example.com",))

    @pytest.mark.asyncio
    async def test_async_execute_many(self, db_path):
        """非同期一括SQL実行"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})

            await db.execute_many("INSERT INTO users (name) VALUES (?)", [("Alice",), ("Bob",), ("Charlie",)])

            results = await db.query("users")
            assert len(results) == 3


# ==================== クエリ拡張テスト ====================


class TestAsyncQueryExtensions:
    """非同期クエリ拡張テスト"""

    @pytest.mark.asyncio
    async def test_async_query_with_limit(self, db_path):
        """非同期LIMIT付きクエリ"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
            for i in range(10):
                await db.sql_insert("users", {"name": f"User{i}"})

            results = await db.query("users", limit=5)
            assert len(results) == 5

    @pytest.mark.asyncio
    async def test_async_query_with_order_and_limit(self, db_path):
        """非同期ORDER BY + LIMITクエリ"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
            await db.sql_insert("users", {"name": "Charlie"})
            await db.sql_insert("users", {"name": "Alice"})
            await db.sql_insert("users", {"name": "Bob"})

            results = await db.query("users", order_by="name ASC", limit=2)
            assert len(results) == 2
            assert results[0]["name"] == "Alice"
            assert results[1]["name"] == "Bob"


# ==================== ユーティリティテスト ====================


class TestAsyncUtilities:
    """非同期ユーティリティテスト"""

    @pytest.mark.asyncio
    async def test_async_get_db_size(self, db_path):
        """非同期DBサイズ取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("data", "x" * 1000)

            size = db.sync_db.get_db_size()
            assert size > 0

    @pytest.mark.asyncio
    async def test_async_export_table_to_dict(self, db_path):
        """非同期テーブルエクスポート"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
            await db.sql_insert("users", {"name": "Alice"})
            await db.sql_insert("users", {"name": "Bob"})

            exported = db.sync_db.export_table_to_dict("users")
            assert len(exported) == 2
            names = [row["name"] for row in exported]
            assert "Alice" in names
            assert "Bob" in names

    @pytest.mark.asyncio
    async def test_async_import_from_dict_list(self, db_path):
        """非同期dictリストインポート"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"})

            users = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]

            count = db.sync_db.import_from_dict_list("users", users)
            assert count == 2

            results = await db.query("users")
            assert len(results) == 2

    @pytest.mark.asyncio
    async def test_async_get_last_insert_rowid(self, db_path):
        """非同期ROWID取得"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
            await db.sql_insert("users", {"name": "Alice"})

            rowid = db.sync_db.get_last_insert_rowid()
            assert rowid > 0

    @pytest.mark.asyncio
    async def test_async_pragma(self, db_path):
        """非同期PRAGMA"""
        async with AsyncNanaSQLite(db_path) as db:
            # 取得
            mode = db.sync_db.pragma("journal_mode")
            assert mode is not None

            # 設定
            db.sync_db.pragma("cache_size", -2000)
            cache_size = db.sync_db.pragma("cache_size")
            assert cache_size == -2000


# ==================== エッジケーステスト ====================


class TestAsyncEdgeCases:
    """非同期エッジケーステスト"""

    @pytest.mark.asyncio
    async def test_async_empty_string_key(self, db_path):
        """空文字列のキー"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("", "empty_key_value")

            assert await db.aget("") == "empty_key_value"
            assert await db.acontains("")

    @pytest.mark.asyncio
    async def test_async_unicode_key_and_value(self, db_path):
        """Unicodeのキーと値"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.aset("日本語キー", {"メッセージ": "こんにちは世界", "絵文字": "🎉🚀"})

            result = await db.aget("日本語キー")
            assert result["メッセージ"] == "こんにちは世界"
            assert result["絵文字"] == "🎉🚀"

    @pytest.mark.asyncio
    async def test_async_special_characters_in_key(self, db_path):
        """特殊文字を含むキー"""
        async with AsyncNanaSQLite(db_path) as db:
            special_keys = [
                "key with spaces",
                "key\twith\ttabs",
                "key'with'quotes",
            ]

            for key in special_keys:
                await db.aset(key, f"value_for_{key}")

            for key in special_keys:
                assert await db.acontains(key)
                assert await db.aget(key) == f"value_for_{key}"

    @pytest.mark.asyncio
    async def test_async_large_value(self, db_path):
        """大きな値"""
        async with AsyncNanaSQLite(db_path) as db:
            large_data = {
                "big_string": "x" * 50000,
                "big_list": list(range(5000)),
            }

            await db.aset("large", large_data)
            result = await db.aget("large")

            assert len(result["big_string"]) == 50000
            assert len(result["big_list"]) == 5000


# ==================== Pydantic詳細テスト ====================


class TestAsyncPydanticDetailed:
    """非同期Pydantic詳細テスト"""

    @pytest.mark.asyncio
    async def test_async_pydantic_nested_model(self, db_path):
        """ネストしたPydanticモデル"""
        try:
            from pydantic import BaseModel

            class Address(BaseModel):
                street: str
                city: str

            class User(BaseModel):
                name: str
                address: Address

            async with AsyncNanaSQLite(db_path) as db:
                user = User(name="Alice", address=Address(street="123 Main", city="NYC"))
                await db.set_model("user", user)

                retrieved = await db.get_model("user", User)
                assert retrieved.name == "Alice"
                assert retrieved.address.city == "NYC"

        except ImportError:
            pytest.skip("Pydantic not installed")

    @pytest.mark.asyncio
    async def test_async_pydantic_optional_fields(self, db_path):
        """オプショナルフィールドを持つPydanticモデル"""
        try:
            from typing import Optional

            from pydantic import BaseModel

            class Product(BaseModel):
                name: str
                description: Optional[str] = None
                stock: int = 0

            async with AsyncNanaSQLite(db_path) as db:
                # デフォルト値使用
                product = Product(name="Widget")
                await db.set_model("product", product)

                retrieved = await db.get_model("product", Product)
                assert retrieved.name == "Widget"
                assert retrieved.description is None
                assert retrieved.stock == 0

        except ImportError:
            pytest.skip("Pydantic not installed")

    @pytest.mark.asyncio
    async def test_async_pydantic_persistence(self, db_path):
        """Pydanticモデルの永続化"""
        try:
            from pydantic import BaseModel

            class Config(BaseModel):
                setting1: str
                setting2: int

            # 保存
            async with AsyncNanaSQLite(db_path) as db:
                config = Config(setting1="value1", setting2=42)
                await db.set_model("config", config)

            # 再読み込み
            async with AsyncNanaSQLite(db_path) as db2:
                retrieved = await db2.get_model("config", Config)
                assert retrieved.setting1 == "value1"
                assert retrieved.setting2 == 42

        except ImportError:
            pytest.skip("Pydantic not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
