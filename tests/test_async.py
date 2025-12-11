"""
NanaSQLite Async テストスイート

非同期機能の包括的なテスト
- 非同期dict風インターフェース
- 非同期バッチ操作
- 非同期SQL実行
- 非同期Pydanticサポート
- コンテキストマネージャ
"""

import os
import sys
import tempfile
import asyncio
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
            data = {
                "key1": "value1",
                "key2": "value2",
                "key3": {"nested": "data"},
                "key4": [1, 2, 3]
            }
            
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
            await db.create_table("users", {
                "id": "INTEGER PRIMARY KEY",
                "name": "TEXT NOT NULL",
                "email": "TEXT UNIQUE"
            })
            
            exists = await db.table_exists("users")
            assert exists is True
    
    @pytest.mark.asyncio
    async def test_async_create_index(self, db_path):
        """非同期インデックス作成"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {
                "id": "INTEGER PRIMARY KEY",
                "email": "TEXT"
            })
            
            await db.create_index("idx_users_email", "users", ["email"])
    
    @pytest.mark.asyncio
    async def test_async_query(self, db_path):
        """非同期クエリ"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {
                "id": "INTEGER PRIMARY KEY",
                "name": "TEXT",
                "age": "INTEGER"
            })
            
            await db.sql_insert("users", {"id": 1, "name": "Alice", "age": 25})
            await db.sql_insert("users", {"id": 2, "name": "Bob", "age": 30})
            
            results = await db.query(
                table_name="users",
                columns=["id", "name", "age"],
                where="age > ?",
                parameters=(20,),
                order_by="name ASC"
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
            await db.create_table("users", {
                "id": "INTEGER PRIMARY KEY",
                "name": "TEXT",
                "age": "INTEGER"
            })
            
            rowid = await db.sql_insert("users", {
                "name": "Alice",
                "age": 25
            })
            
            assert rowid > 0
    
    @pytest.mark.asyncio
    async def test_async_sql_update(self, db_path):
        """非同期SQL UPDATE"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {
                "id": "INTEGER PRIMARY KEY",
                "name": "TEXT",
                "age": "INTEGER"
            })
            
            await db.sql_insert("users", {"name": "Alice", "age": 25})
            
            count = await db.sql_update("users", {"age": 26}, "name = ?", ("Alice",))
            assert count == 1
    
    @pytest.mark.asyncio
    async def test_async_sql_delete(self, db_path):
        """非同期SQL DELETE"""
        async with AsyncNanaSQLite(db_path) as db:
            await db.create_table("users", {
                "id": "INTEGER PRIMARY KEY",
                "name": "TEXT",
                "age": "INTEGER"
            })
            
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
            results = await asyncio.gather(
                db.aget("key1"),
                db.aget("key2"),
                db.aget("key3")
            )
            
            assert results == ["value1", "value2", "value3"]
    
    @pytest.mark.asyncio
    async def test_concurrent_writes(self, db_path):
        """並行書き込み"""
        async with AsyncNanaSQLite(db_path) as db:
            # 並行書き込み
            await asyncio.gather(
                db.aset("key1", "value1"),
                db.aset("key2", "value2"),
                db.aset("key3", "value3")
            )
            
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
                db.aset("key3", "value3")
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
