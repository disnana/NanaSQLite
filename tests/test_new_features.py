"""
NanaSQLite 新機能テストスイート

- Pydantic互換性
- 直接SQL実行
- SQLiteラッパー関数
"""

import importlib.util
import json
import os
import sys
import tempfile

import pytest

# テスト実行時のパス設定
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nanasqlite import NanaSQLite

# Pydanticが利用可能かチェック
PYDANTIC_AVAILABLE = importlib.util.find_spec("pydantic") is not None


# ==================== Fixtures ====================


@pytest.fixture
def db_path():
    """一時DBパスを提供"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test.db")


@pytest.fixture
def db(db_path):
    """NanaSQLiteインスタンスを提供"""
    database = NanaSQLite(db_path)
    yield database
    database.close()


# ==================== Pydantic互換性テスト ====================


@pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not installed")
class TestPydanticSupport:
    """Pydantic互換性のテスト"""

    def test_set_and_get_simple_model(self, db):
        """シンプルなPydanticモデルの保存と取得"""
        from pydantic import BaseModel

        class User(BaseModel):
            name: str
            age: int
            active: bool

        # モデル作成
        user = User(name="Nana", age=20, active=True)

        # 保存
        db.set_model("user", user)

        # 取得
        retrieved = db.get_model("user", User)

        # 検証
        assert isinstance(retrieved, User)
        assert retrieved.name == "Nana"
        assert retrieved.age == 20
        assert retrieved.active is True

    def test_set_and_get_nested_model(self, db):
        """ネストしたPydanticモデルの保存と取得"""
        from pydantic import BaseModel

        class Address(BaseModel):
            street: str
            city: str
            country: str

        class UserWithAddress(BaseModel):
            name: str
            age: int
            address: Address

        # ネストしたモデル作成
        user = UserWithAddress(
            name="Alice", age=25, address=Address(street="123 Main St", city="Tokyo", country="Japan")
        )

        # 保存
        db.set_model("user_addr", user)

        # 取得
        retrieved = db.get_model("user_addr", UserWithAddress)

        # 検証
        assert isinstance(retrieved, UserWithAddress)
        assert retrieved.name == "Alice"
        assert retrieved.age == 25
        assert isinstance(retrieved.address, Address)
        assert retrieved.address.street == "123 Main St"
        assert retrieved.address.city == "Tokyo"
        assert retrieved.address.country == "Japan"

    def test_set_and_get_model_with_optional_fields(self, db):
        """オプショナルフィールドを持つPydanticモデル"""
        from typing import Optional

        from pydantic import BaseModel

        class Product(BaseModel):
            name: str
            price: float
            description: Optional[str] = None
            stock: int = 0

        # デフォルト値を使ったモデル
        product1 = Product(name="Widget", price=9.99)
        db.set_model("product1", product1)

        retrieved1 = db.get_model("product1", Product)
        assert retrieved1.name == "Widget"
        assert retrieved1.price == 9.99
        assert retrieved1.description is None
        assert retrieved1.stock == 0

        # 全フィールド指定
        product2 = Product(name="Gadget", price=19.99, description="Amazing", stock=100)
        db.set_model("product2", product2)

        retrieved2 = db.get_model("product2", Product)
        assert retrieved2.name == "Gadget"
        assert retrieved2.price == 19.99
        assert retrieved2.description == "Amazing"
        assert retrieved2.stock == 100

    def test_set_model_with_non_pydantic_raises_error(self, db):
        """Pydanticモデルでないオブジェクトでエラー"""

        class NotPydantic:
            pass

        obj = NotPydantic()

        with pytest.raises(TypeError):
            db.set_model("invalid", obj)

    def test_get_model_without_class_raises_error(self, db):
        """model_classなしでget_modelを呼ぶとエラー"""
        from pydantic import BaseModel

        class User(BaseModel):
            name: str

        user = User(name="Test")
        db.set_model("user", user)

        with pytest.raises(ValueError):
            db.get_model("user")

    def test_pydantic_persistence(self, db_path):
        """Pydanticモデルの永続化確認"""
        from pydantic import BaseModel

        class Config(BaseModel):
            setting1: str
            setting2: int
            enabled: bool

        # 保存
        db1 = NanaSQLite(db_path)
        config = Config(setting1="value1", setting2=42, enabled=True)
        db1.set_model("config", config)
        db1.close()

        # 再度開いて取得
        db2 = NanaSQLite(db_path)
        retrieved = db2.get_model("config", Config)

        assert retrieved.setting1 == "value1"
        assert retrieved.setting2 == 42
        assert retrieved.enabled is True

        db2.close()


# ==================== 直接SQL実行テスト ====================


class TestDirectSQLExecution:
    """直接SQL実行機能のテスト"""

    def test_execute_select(self, db):
        """SELECT文の実行"""
        # データ準備
        db["test1"] = "value1"
        db["test2"] = "value2"

        # SQL実行
        cursor = db.execute(f"SELECT key, value FROM {db._table} ORDER BY key")
        rows = cursor.fetchall()

        assert len(rows) == 2
        assert rows[0][0] == "test1"
        assert rows[1][0] == "test2"

    def test_execute_with_parameters(self, db):
        """パラメータ付きSELECT"""
        db["user1"] = "Alice"
        db["user2"] = "Bob"
        db["post1"] = "Hello"

        # パラメータバインディング
        cursor = db.execute(f"SELECT key, value FROM {db._table} WHERE key LIKE ?", ("user%",))
        rows = cursor.fetchall()

        assert len(rows) == 2
        assert all(row[0].startswith("user") for row in rows)

    def test_execute_insert(self, db):
        """INSERT文の実行"""
        # カスタムテーブル作成
        db.execute("""
            CREATE TABLE IF NOT EXISTS custom (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
        """)

        # INSERT
        db.execute("INSERT INTO custom (id, name, value) VALUES (?, ?, ?)", (1, "test", 100))

        # 確認
        cursor = db.execute("SELECT * FROM custom WHERE id = ?", (1,))
        row = cursor.fetchone()

        assert row[0] == 1
        assert row[1] == "test"
        assert row[2] == 100

    def test_execute_update(self, db):
        """UPDATE文の実行"""
        db["key"] = "original"

        # 直接UPDATE
        db.execute(f"UPDATE {db._table} SET value = ? WHERE key = ?", ('"updated"', "key"))

        # 直接SQLで確認（キャッシュをバイパス）
        cursor = db.execute(f"SELECT value FROM {db._table} WHERE key = ?", ("key",))
        row = cursor.fetchone()
        assert row is not None
        # JSONでシリアライズされているので、デシリアライズして確認
        assert json.loads(row[0]) == "updated"

    def test_execute_delete(self, db):
        """DELETE文の実行"""
        db["to_delete"] = "value"
        assert "to_delete" in db

        # 直接DELETE
        db.execute(f"DELETE FROM {db._table} WHERE key = ?", ("to_delete",))

        # 直接SQLで確認（キャッシュをバイパス）
        cursor = db.execute(f"SELECT key FROM {db._table} WHERE key = ?", ("to_delete",))
        assert cursor.fetchone() is None

    def test_execute_many(self, db):
        """execute_many で一括INSERT"""
        # カスタムテーブル作成
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER
            )
        """)

        # 一括INSERT
        data = [(1, "Alice", 25), (2, "Bob", 30), (3, "Charlie", 35), (4, "Diana", 28)]
        db.execute_many("INSERT INTO users (id, name, age) VALUES (?, ?, ?)", data)

        # 確認
        cursor = db.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        assert count == 4

        cursor = db.execute("SELECT name FROM users WHERE age > 30")
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0][0] == "Charlie"

    def test_fetch_one(self, db):
        """fetch_oneで1行取得"""
        db["single"] = "value"

        row = db.fetch_one(f"SELECT key, value FROM {db._table} WHERE key = ?", ("single",))

        assert row is not None
        assert row[0] == "single"

    def test_fetch_one_no_result(self, db):
        """fetch_oneで結果なし"""
        row = db.fetch_one(f"SELECT * FROM {db._table} WHERE key = ?", ("nonexistent",))

        assert row is None

    def test_fetch_all(self, db):
        """fetch_allで全行取得"""
        for i in range(5):
            db[f"key{i}"] = f"value{i}"

        rows = db.fetch_all(f"SELECT key FROM {db._table} ORDER BY key")

        assert len(rows) == 5
        assert rows[0][0] == "key0"
        assert rows[4][0] == "key4"


# ==================== SQLiteラッパー関数テスト ====================


class TestSQLiteWrapperFunctions:
    """SQLiteラッパー関数のテスト"""

    def test_create_table(self, db):
        """テーブル作成"""
        db.create_table(
            "users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT NOT NULL", "email": "TEXT", "age": "INTEGER"}
        )

        # テーブルが作成されたか確認
        cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is not None

        # データ挿入して確認
        db.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", ("Alice", "alice@example.com", 25))
        row = db.fetch_one("SELECT * FROM users WHERE name = ?", ("Alice",))
        assert row is not None
        assert row[1] == "Alice"

    def test_create_table_with_primary_key_parameter(self, db):
        """primary_keyパラメータでテーブル作成"""
        db.create_table("posts", {"id": "INTEGER", "title": "TEXT", "content": "TEXT"}, primary_key="id")

        # テーブルが作成されたか確認
        cursor = db.execute("PRAGMA table_info(posts)")
        columns = cursor.fetchall()

        # idカラムがプライマリキーか確認
        id_col = [col for col in columns if col[1] == "id"][0]
        assert id_col[5] == 1  # pk列が1

    def test_create_table_if_not_exists(self, db):
        """IF NOT EXISTSでテーブル作成"""
        db.create_table("temp", {"id": "INTEGER", "data": "TEXT"}, if_not_exists=True)

        # 同じテーブルを再度作成してもエラーにならない
        db.create_table("temp", {"id": "INTEGER", "data": "TEXT"}, if_not_exists=True)

        # テーブルは1つだけ
        cursor = db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='temp'")
        assert cursor.fetchone()[0] == 1

    def test_create_index(self, db):
        """インデックス作成"""
        # テーブル作成
        db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "email": "TEXT"})

        # インデックス作成
        db.create_index("idx_users_email", "users", ["email"])

        # インデックスが作成されたか確認
        cursor = db.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_users_email'")
        assert cursor.fetchone() is not None

    def test_create_unique_index(self, db):
        """ユニークインデックス作成"""
        db.create_table("products", {"id": "INTEGER PRIMARY KEY", "sku": "TEXT"})

        db.create_index("idx_products_sku", "products", ["sku"], unique=True)

        # データ挿入
        db.execute("INSERT INTO products (sku) VALUES (?)", ("SKU001",))

        # 重複挿入はエラー
        with pytest.raises(Exception):  # UNIQUE制約違反
            db.execute("INSERT INTO products (sku) VALUES (?)", ("SKU001",))

    def test_create_composite_index(self, db):
        """複合インデックス作成"""
        db.create_table(
            "logs", {"id": "INTEGER PRIMARY KEY", "user_id": "INTEGER", "timestamp": "INTEGER", "action": "TEXT"}
        )

        db.create_index("idx_logs_user_time", "logs", ["user_id", "timestamp"])

        cursor = db.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_logs_user_time'")
        assert cursor.fetchone() is not None

    def test_query_default_table(self, db):
        """デフォルトテーブルへのクエリ"""
        db["key1"] = "value1"
        db["key2"] = "value2"
        db["key3"] = "value3"

        results = db.query()

        assert len(results) == 3
        assert all(isinstance(r, dict) for r in results)
        assert all("key" in r and "value" in r for r in results)

    def test_query_with_columns(self, db):
        """カラム指定クエリ"""
        db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "email": "TEXT", "age": "INTEGER"})

        db.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", ("Alice", "alice@example.com", 25))
        db.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", ("Bob", "bob@example.com", 30))

        results = db.query(table_name="users", columns=["name", "age"])

        assert len(results) == 2
        assert all("name" in r and "age" in r for r in results)
        assert all("email" not in r for r in results)

    def test_query_with_where(self, db):
        """WHERE条件付きクエリ"""
        db.create_table("products", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "price": "REAL"})

        db.execute("INSERT INTO products (name, price) VALUES (?, ?)", ("Item A", 10.0))
        db.execute("INSERT INTO products (name, price) VALUES (?, ?)", ("Item B", 20.0))
        db.execute("INSERT INTO products (name, price) VALUES (?, ?)", ("Item C", 15.0))

        results = db.query(table_name="products", where="price > ?", parameters=(12.0,))

        assert len(results) == 2
        assert all(r["price"] > 12.0 for r in results)

    def test_query_with_order_by(self, db):
        """ORDER BY付きクエリ"""
        db.create_table("items", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "value": "INTEGER"})

        db.execute("INSERT INTO items (name, value) VALUES (?, ?)", ("C", 3))
        db.execute("INSERT INTO items (name, value) VALUES (?, ?)", ("A", 1))
        db.execute("INSERT INTO items (name, value) VALUES (?, ?)", ("B", 2))

        results = db.query(table_name="items", order_by="value ASC")

        assert len(results) == 3
        assert results[0]["value"] == 1
        assert results[1]["value"] == 2
        assert results[2]["value"] == 3

    def test_query_with_limit(self, db):
        """LIMIT付きクエリ"""
        for i in range(10):
            db[f"key{i}"] = f"value{i}"

        results = db.query(limit=3)

        assert len(results) == 3

    def test_query_combined_conditions(self, db):
        """複合条件のクエリ"""
        db.create_table("scores", {"id": "INTEGER PRIMARY KEY", "student": "TEXT", "score": "INTEGER"})

        students = [("Alice", 85), ("Bob", 92), ("Charlie", 78), ("Diana", 95), ("Eve", 88)]
        db.execute_many("INSERT INTO scores (student, score) VALUES (?, ?)", students)

        results = db.query(
            table_name="scores",
            columns=["student", "score"],
            where="score >= ?",
            parameters=(85,),
            order_by="score DESC",
            limit=3,
        )

        assert len(results) == 3
        assert results[0]["score"] == 95
        assert results[1]["score"] == 92
        assert results[2]["score"] == 88

    def test_table_exists(self, db):
        """テーブル存在確認"""
        # デフォルトテーブルは存在する
        assert db.table_exists(db._table) is True

        # 存在しないテーブル
        assert db.table_exists("nonexistent") is False

        # テーブル作成後
        db.create_table("new_table", {"id": "INTEGER"})
        assert db.table_exists("new_table") is True

    def test_list_tables(self, db):
        """テーブル一覧取得"""
        # 初期状態（dataテーブルのみ）
        tables = db.list_tables()
        assert db._table in tables

        # テーブル追加
        db.create_table("users", {"id": "INTEGER"})
        db.create_table("posts", {"id": "INTEGER"})

        tables = db.list_tables()
        assert "users" in tables
        assert "posts" in tables
        assert len(tables) >= 3


# ==================== 統合テスト ====================


class TestIntegration:
    """新機能と既存機能の統合テスト"""

    def test_pydantic_and_dict_mixed(self, db):
        """Pydanticモデルとdictの混在"""
        if not PYDANTIC_AVAILABLE:
            pytest.skip("Pydantic not available")

        from pydantic import BaseModel

        class User(BaseModel):
            name: str
            age: int

        # Pydanticモデルを保存
        user = User(name="Alice", age=25)
        db.set_model("pydantic_user", user)

        # 通常のdictも保存
        db["dict_user"] = {"name": "Bob", "age": 30}

        # 両方取得できる
        pydantic_user = db.get_model("pydantic_user", User)
        dict_user = db["dict_user"]

        assert pydantic_user.name == "Alice"
        assert dict_user["name"] == "Bob"

    def test_custom_table_with_wrapper_functions(self, db):
        """カスタムテーブルとラッパー関数"""
        # カスタムテーブル作成
        db.create_table(
            "articles",
            {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "title": "TEXT NOT NULL",
                "content": "TEXT",
                "views": "INTEGER DEFAULT 0",
            },
        )

        # インデックス作成
        db.create_index("idx_articles_title", "articles", ["title"])

        # データ挿入（execute_many使用）
        articles = [("Article 1", "Content 1", 100), ("Article 2", "Content 2", 200), ("Article 3", "Content 3", 150)]
        db.execute_many("INSERT INTO articles (title, content, views) VALUES (?, ?, ?)", articles)

        # クエリで取得
        popular = db.query(
            table_name="articles",
            columns=["title", "views"],
            where="views > ?",
            parameters=(120,),
            order_by="views DESC",
        )

        assert len(popular) == 2
        assert popular[0]["views"] == 200
        assert popular[1]["views"] == 150

    def test_all_features_together(self, db):
        """全機能を組み合わせたテスト"""
        # 1. カスタムテーブル作成
        db.create_table(
            "projects", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "status": "TEXT", "priority": "INTEGER"}
        )

        # 2. インデックス作成
        db.create_index("idx_projects_status", "projects", ["status"])

        # 3. 一括データ挿入
        projects = [
            (1, "Project A", "active", 1),
            (2, "Project B", "completed", 2),
            (3, "Project C", "active", 3),
            (4, "Project D", "pending", 1),
        ]
        db.execute_many("INSERT INTO projects (id, name, status, priority) VALUES (?, ?, ?, ?)", projects)

        # 4. クエリで検索
        active_projects = db.query(
            table_name="projects", where="status = ?", parameters=("active",), order_by="priority ASC"
        )

        assert len(active_projects) == 2
        assert active_projects[0]["name"] == "Project A"

        # 5. デフォルトテーブルにも保存（既存機能）
        db["config"] = {"version": "1.0", "features": ["new1", "new2"]}

        # 6. 全て正常に動作
        assert len(db) >= 1
        assert db["config"]["version"] == "1.0"
        assert db.table_exists("projects")
        assert "projects" in db.list_tables()


# ==================== 実行用 ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
