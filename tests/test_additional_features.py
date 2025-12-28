"""
NanaSQLite 追加機能テストスイート

- スキーマ管理機能
- データ操作機能
- クエリ拡張機能
- ユーティリティ機能
- トランザクション制御
"""

import os
import sys
import tempfile

import pytest

# テスト実行時のパス設定
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nanasqlite import NanaSQLite

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


# ==================== スキーマ管理機能テスト ====================


class TestSchemaManagement:
    """スキーマ管理機能のテスト"""

    def test_drop_table(self, db):
        """テーブル削除"""
        # テーブル作成
        db.create_table("temp_table", {"id": "INTEGER", "name": "TEXT"})
        assert db.table_exists("temp_table")

        # 削除
        db.drop_table("temp_table")
        assert not db.table_exists("temp_table")

    def test_drop_table_if_exists(self, db):
        """IF EXISTS付きでテーブル削除"""
        # 存在しないテーブルを削除してもエラーにならない
        db.drop_table("nonexistent", if_exists=True)

        # テーブル作成して削除
        db.create_table("temp", {"id": "INTEGER"})
        db.drop_table("temp", if_exists=True)
        assert not db.table_exists("temp")

    def test_drop_index(self, db):
        """インデックス削除"""
        db.create_table("users", {"id": "INTEGER", "email": "TEXT"})
        db.create_index("idx_test", "users", ["email"])

        # インデックスが存在することを確認
        indexes = db.list_indexes("users")
        assert any(idx["name"] == "idx_test" for idx in indexes)

        # 削除
        db.drop_index("idx_test")

        # 削除されたことを確認
        indexes = db.list_indexes("users")
        assert not any(idx["name"] == "idx_test" for idx in indexes)

    def test_alter_table_add_column(self, db):
        """カラム追加"""
        db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})

        # カラム追加
        db.alter_table_add_column("users", "email", "TEXT")

        # スキーマ確認
        schema = db.get_table_schema("users")
        col_names = [col["name"] for col in schema]
        assert "email" in col_names

    def test_alter_table_add_column_with_default(self, db):
        """デフォルト値付きカラム追加"""
        db.create_table("users", {"id": "INTEGER", "name": "TEXT"})
        db.sql_insert("users", {"id": 1, "name": "Alice"})

        # デフォルト値付きカラム追加
        db.alter_table_add_column("users", "status", "TEXT", default="'active'")

        # デフォルト値が設定されていることを確認
        result = db.query_with_pagination("users", where="id = ?", parameters=(1,))
        assert result[0]["status"] == "active"

    def test_get_table_schema(self, db):
        """テーブル構造取得"""
        db.create_table(
            "users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT NOT NULL", "email": "TEXT", "age": "INTEGER"}
        )

        schema = db.get_table_schema("users")

        assert len(schema) == 4
        assert schema[0]["name"] == "id"
        assert schema[0]["pk"] is True
        assert schema[1]["name"] == "name"
        assert schema[1]["notnull"] is True

    def test_list_indexes(self, db):
        """インデックス一覧取得"""
        db.create_table("users", {"id": "INTEGER", "name": "TEXT", "email": "TEXT"})
        db.create_index("idx_name", "users", ["name"])
        db.create_index("idx_email", "users", ["email"], unique=True)

        indexes = db.list_indexes("users")

        assert len(indexes) >= 2
        index_names = [idx["name"] for idx in indexes]
        assert "idx_name" in index_names
        assert "idx_email" in index_names

    def test_list_indexes_all_tables(self, db):
        """全テーブルのインデックス取得"""
        db.create_table("users", {"id": "INTEGER", "email": "TEXT"})
        db.create_table("posts", {"id": "INTEGER", "title": "TEXT"})
        db.create_index("idx_users_email", "users", ["email"])
        db.create_index("idx_posts_title", "posts", ["title"])

        all_indexes = db.list_indexes()

        assert len(all_indexes) >= 2
        tables = [idx["table"] for idx in all_indexes]
        assert "users" in tables
        assert "posts" in tables


# ==================== データ操作機能テスト ====================


class TestDataOperations:
    """データ操作機能のテスト"""

    def test_insert(self, db):
        """INSERT操作"""
        db.create_table("users", {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "name": "TEXT", "age": "INTEGER"})

        rowid = db.sql_insert("users", {"name": "Alice", "age": 25})

        assert rowid > 0
        result = db.query_with_pagination("users", where="name = ?", parameters=("Alice",))
        assert len(result) == 1
        assert result[0]["name"] == "Alice"
        assert result[0]["age"] == 25

    def test_update(self, db):
        """UPDATE操作"""
        db.create_table("users", {"id": "INTEGER", "name": "TEXT", "age": "INTEGER"})
        db.sql_insert("users", {"id": 1, "name": "Alice", "age": 25})

        count = db.sql_update("users", {"age": 26}, "name = ?", ("Alice",))

        assert count == 1
        result = db.query_with_pagination("users", where="id = ?", parameters=(1,))
        assert result[0]["age"] == 26

    def test_delete(self, db):
        """DELETE操作"""
        db.create_table("users", {"id": "INTEGER", "name": "TEXT"})
        db.sql_insert("users", {"id": 1, "name": "Alice"})
        db.sql_insert("users", {"id": 2, "name": "Bob"})
        db.sql_insert("users", {"id": 3, "name": "Charlie"})

        count = db.sql_delete("users", "id > ?", (1,))

        assert count == 2
        remaining = db.count("users")
        assert remaining == 1

    def test_upsert_insert_or_replace(self, db):
        """UPSERT（INSERT OR REPLACE）"""
        db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"})

        # 最初の挿入
        db.upsert("users", {"id": 1, "name": "Alice", "age": 25})
        assert db.count("users") == 1

        # 同じIDで更新
        db.upsert("users", {"id": 1, "name": "Alice Updated", "age": 26})
        assert db.count("users") == 1

        result = db.query_with_pagination("users", where="id = ?", parameters=(1,))
        assert result[0]["name"] == "Alice Updated"
        assert result[0]["age"] == 26

    def test_upsert_on_conflict(self, db):
        """UPSERT（ON CONFLICT）"""
        db.create_table(
            "users",
            {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "email": "TEXT UNIQUE", "name": "TEXT", "age": "INTEGER"},
        )

        # 最初の挿入
        db.upsert("users", {"email": "alice@example.com", "name": "Alice", "age": 25}, conflict_columns=["email"])

        # 同じemailで更新
        db.upsert(
            "users", {"email": "alice@example.com", "name": "Alice Updated", "age": 26}, conflict_columns=["email"]
        )

        assert db.count("users") == 1
        result = db.query_with_pagination("users", where="email = ?", parameters=("alice@example.com",))
        assert result[0]["name"] == "Alice Updated"

    def test_count(self, db):
        """レコード数取得"""
        db.create_table("users", {"id": "INTEGER", "age": "INTEGER"})
        for i in range(10):
            db.sql_insert("users", {"id": i, "age": 20 + i})

        # 全件数
        total = db.count("users")
        assert total == 10

        # 条件付き
        count_filtered = db.count("users", "age >= ?", (25,))
        assert count_filtered == 5

    def test_count_default_table(self, db):
        """デフォルトテーブルのレコード数"""
        db["key1"] = "value1"
        db["key2"] = "value2"

        count = db.count()
        assert count == 2

    def test_exists(self, db):
        """レコード存在確認"""
        db.create_table("users", {"id": "INTEGER", "email": "TEXT"})
        db.sql_insert("users", {"id": 1, "email": "alice@example.com"})

        assert db.exists("users", "email = ?", ("alice@example.com",)) is True
        assert db.exists("users", "email = ?", ("bob@example.com",)) is False


# ==================== クエリ拡張機能テスト ====================


class TestQueryExtensions:
    """クエリ拡張機能のテスト"""

    def test_query_with_offset(self, db):
        """OFFSET付きクエリ（ページネーション）"""
        db.create_table("items", {"id": "INTEGER", "name": "TEXT"})
        for i in range(20):
            db.sql_insert("items", {"id": i, "name": f"Item {i}"})

        # 1ページ目
        page1 = db.query_with_pagination("items", limit=5, offset=0, order_by="id ASC")
        assert len(page1) == 5
        assert page1[0]["id"] == 0

        # 2ページ目
        page2 = db.query_with_pagination("items", limit=5, offset=5, order_by="id ASC")
        assert len(page2) == 5
        assert page2[0]["id"] == 5

    def test_query_with_group_by(self, db):
        """GROUP BY付きクエリ"""
        db.create_table(
            "orders", {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "user_id": "INTEGER", "amount": "INTEGER"}
        )

        # テストデータ挿入
        orders = [
            {"user_id": 1, "amount": 100},
            {"user_id": 1, "amount": 200},
            {"user_id": 2, "amount": 150},
            {"user_id": 2, "amount": 250},
            {"user_id": 3, "amount": 300},
        ]
        for order in orders:
            db.sql_insert("orders", order)

        # ユーザーごとの注文数を集計
        results = db.query_with_pagination(
            "orders",
            columns=["user_id", "COUNT(*) as order_count", "SUM(amount) as total"],
            group_by="user_id",
            order_by="user_id ASC",
        )

        assert len(results) == 3
        assert results[0]["user_id"] == 1
        assert results[0]["order_count"] == 2
        assert results[0]["total"] == 300

    def test_query_combined_pagination_and_group(self, db):
        """ページネーションとグループ化の組み合わせ"""
        db.create_table("sales", {"category": "TEXT", "amount": "INTEGER"})

        for _ in range(3):
            db.sql_insert("sales", {"category": "A", "amount": 100})
            db.sql_insert("sales", {"category": "B", "amount": 200})
            db.sql_insert("sales", {"category": "C", "amount": 300})

        results = db.query_with_pagination(
            "sales", columns=["category", "SUM(amount) as total"], group_by="category", order_by="total DESC", limit=2
        )

        assert len(results) == 2
        assert results[0]["category"] == "C"
        assert results[0]["total"] == 900


# ==================== ユーティリティ機能テスト ====================


class TestUtilityFunctions:
    """ユーティリティ機能のテスト"""

    def test_vacuum(self, db):
        """VACUUM実行"""
        db.create_table("temp", {"id": "INTEGER", "data": "TEXT"})
        for i in range(100):
            db.sql_insert("temp", {"id": i, "data": "x" * 1000})

        # データ削除
        db.sql_delete("temp", "id < ?", (50,))

        # VACUUM実行（エラーが出ないことを確認）
        db.vacuum()

    def test_get_db_size(self, db):
        """データベースサイズ取得"""
        size = db.get_db_size()
        assert size > 0

        # データ追加後はサイズが増える（または同じページ内に収まる場合もある）
        db.create_table("testdata", {"id": "INTEGER", "content": "TEXT"})
        for i in range(1000):
            db.sql_insert("testdata", {"id": i, "content": "x" * 1000})

        new_size = db.get_db_size()
        assert new_size >= size  # 最低でも同じかそれ以上

    def test_export_table_to_dict(self, db):
        """テーブルをdictリストとしてエクスポート"""
        db.create_table("users", {"id": "INTEGER", "name": "TEXT", "age": "INTEGER"})
        db.sql_insert("users", {"id": 1, "name": "Alice", "age": 25})
        db.sql_insert("users", {"id": 2, "name": "Bob", "age": 30})
        db.sql_insert("users", {"id": 3, "name": "Charlie", "age": 35})

        exported = db.export_table_to_dict("users")

        assert len(exported) == 3
        assert all(isinstance(item, dict) for item in exported)
        assert exported[0]["name"] == "Alice"

    def test_import_from_dict_list(self, db):
        """dictリストからインポート"""
        db.create_table("products", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "price": "REAL"})

        products = [
            {"id": 1, "name": "Product A", "price": 10.99},
            {"id": 2, "name": "Product B", "price": 20.99},
            {"id": 3, "name": "Product C", "price": 15.99},
        ]

        count = db.import_from_dict_list("products", products)

        assert count == 3
        assert db.count("products") == 3

    def test_import_empty_list(self, db):
        """空リストのインポート"""
        db.create_table("empty", {"id": "INTEGER"})
        count = db.import_from_dict_list("empty", [])
        assert count == 0

    def test_get_last_insert_rowid(self, db):
        """最後のROWID取得"""
        db.create_table("test", {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "data": "TEXT"})

        db.sql_insert("test", {"data": "first"})
        rowid1 = db.get_last_insert_rowid()

        db.sql_insert("test", {"data": "second"})
        rowid2 = db.get_last_insert_rowid()

        assert rowid2 > rowid1

    def test_pragma_get(self, db):
        """PRAGMA取得"""
        mode = db.pragma("journal_mode")
        assert mode is not None

    def test_pragma_set(self, db):
        """PRAGMA設定"""
        # foreign_keysを有効化
        db.pragma("foreign_keys", 1)
        result = db.pragma("foreign_keys")
        assert result == 1


# ==================== トランザクション制御テスト ====================


class TestTransactionControl:
    """トランザクション制御のテスト"""

    def test_begin_commit(self, db):
        """明示的トランザクション（コミット）"""
        db.create_table("test", {"id": "INTEGER", "value": "TEXT"})

        db.begin_transaction()
        db.sql_insert("test", {"id": 1, "value": "data1"})
        db.sql_insert("test", {"id": 2, "value": "data2"})
        db.commit()

        assert db.count("test") == 2

    def test_begin_rollback(self, db):
        """明示的トランザクション（ロールバック）"""
        db.create_table("test", {"id": "INTEGER", "value": "TEXT"})
        db.sql_insert("test", {"id": 1, "value": "existing"})

        db.begin_transaction()
        db.sql_insert("test", {"id": 2, "value": "new1"})
        db.sql_insert("test", {"id": 3, "value": "new2"})
        db.rollback()

        # ロールバックされたので追加されていない
        assert db.count("test") == 1

    def test_transaction_context_success(self, db):
        """トランザクションコンテキストマネージャ（成功）"""
        db.create_table("test", {"id": "INTEGER", "value": "TEXT"})

        with db.transaction():
            db.sql_insert("test", {"id": 1, "value": "data1"})
            db.sql_insert("test", {"id": 2, "value": "data2"})

        # 自動的にコミットされる
        assert db.count("test") == 2

    def test_transaction_context_rollback_on_exception(self, db):
        """トランザクションコンテキストマネージャ（例外時ロールバック）"""
        db.create_table("test", {"id": "INTEGER PRIMARY KEY", "value": "TEXT"})

        # 重複キーでエラーが発生し、ロールバックされることを確認
        with pytest.raises(Exception):
            with db.transaction():
                db.sql_insert("test", {"id": 1, "value": "data1"})
                db.sql_insert("test", {"id": 2, "value": "data2"})
                # 重複キーでエラー発生
                db.sql_insert("test", {"id": 1, "value": "duplicate"})

        # ロールバックされたので何も追加されていない
        assert db.count("test") == 0

    def test_nested_transactions_not_supported(self, db):
        """ネストしたトランザクション（SQLiteは非対応）"""
        db.create_table("test", {"id": "INTEGER"})

        # 外側のトランザクション
        db.begin_transaction()
        db.sql_insert("test", {"id": 1})

        # 内側のトランザクション開始は通常エラーになる可能性があるが、
        # 実装によっては無視される場合もある
        # ここでは単にロールバックできることを確認
        db.rollback()

        assert db.count("test") == 0


# ==================== 統合テスト ====================


class TestIntegrationAdvanced:
    """高度な統合テスト"""

    def test_complete_crud_workflow(self, db):
        """完全なCRUDワークフロー"""
        # テーブル作成
        db.create_table(
            "users",
            {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "name": "TEXT NOT NULL",
                "email": "TEXT UNIQUE",
                "age": "INTEGER",
            },
        )
        db.create_index("idx_email", "users", ["email"], unique=True)

        # CREATE
        db.sql_insert("users", {"name": "Alice", "email": "alice@example.com", "age": 25})
        db.sql_insert("users", {"name": "Bob", "email": "bob@example.com", "age": 30})

        # READ
        users = db.query_with_pagination("users", order_by="name ASC")
        assert len(users) == 2

        # UPDATE
        db.sql_update("users", {"age": 26}, "name = ?", ("Alice",))

        # READ again
        alice = db.query_with_pagination("users", where="name = ?", parameters=("Alice",))
        assert alice[0]["age"] == 26

        # DELETE
        db.sql_delete("users", "name = ?", ("Bob",))

        # Verify
        assert db.count("users") == 1
        assert db.exists("users", "name = ?", ("Alice",))
        assert not db.exists("users", "name = ?", ("Bob",))

    def test_bulk_operations_with_transaction(self, db):
        """トランザクション内での一括操作"""
        db.create_table("logs", {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "message": "TEXT", "timestamp": "INTEGER"})

        # 大量データを一括挿入
        import time

        logs = [{"message": f"Log {i}", "timestamp": int(time.time())} for i in range(1000)]

        # import_from_dict_listは内部でexecute_manyを使い、それがトランザクションを使用するため
        # 外側でトランザクションを開始しない
        db.import_from_dict_list("logs", logs)

        assert db.count("logs") == 1000

    def test_export_import_roundtrip(self, db):
        """エクスポート・インポートの往復テスト"""
        # データ作成
        db.create_table("original", {"id": "INTEGER", "data": "TEXT"})
        original_data = [{"id": i, "data": f"data_{i}"} for i in range(50)]
        db.import_from_dict_list("original", original_data)

        # エクスポート
        exported = db.export_table_to_dict("original")

        # 別テーブルにインポート
        db.create_table("copy", {"id": "INTEGER", "data": "TEXT"})
        db.import_from_dict_list("copy", exported)

        # 検証
        assert db.count("original") == db.count("copy")
        original_items = db.query_with_pagination("original", order_by="id ASC")
        copy_items = db.query_with_pagination("copy", order_by="id ASC")
        assert original_items == copy_items


# ==================== 実行用 ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
