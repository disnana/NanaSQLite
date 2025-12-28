"""
トランザクションとエラーハンドリングの強化機能テスト
"""

import pytest

from nanasqlite import (
    NanaSQLite,
    NanaSQLiteConnectionError,
    NanaSQLiteDatabaseError,
    NanaSQLiteError,
    NanaSQLiteTransactionError,
    NanaSQLiteValidationError,
)


class TestCustomExceptions:
    """カスタム例外クラスのテスト"""

    def test_validation_error_invalid_identifier(self, tmp_path):
        """不正な識別子でValidationErrorが発生"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))

        with pytest.raises(NanaSQLiteValidationError) as exc_info:
            db.create_table("123invalid", {"id": "INTEGER"})

        assert "must start with letter or underscore" in str(exc_info.value)

    def test_validation_error_empty_identifier(self, tmp_path):
        """空の識別子でValidationErrorが発生"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))

        with pytest.raises(NanaSQLiteValidationError) as exc_info:
            db.create_table("", {"id": "INTEGER"})

        assert "Identifier cannot be empty" in str(exc_info.value)

    def test_database_error_invalid_sql(self, tmp_path):
        """不正なSQLでDatabaseErrorが発生"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))

        with pytest.raises(NanaSQLiteDatabaseError) as exc_info:
            db.execute("INVALID SQL STATEMENT")

        assert "Failed to execute SQL" in str(exc_info.value)
        assert exc_info.value.original_error is not None

    def test_connection_error_closed_connection(self, tmp_path):
        """閉じた接続の使用でConnectionErrorが発生"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))
        db.close()

        with pytest.raises(NanaSQLiteConnectionError) as exc_info:
            db["key"] = "value"

        assert "connection is closed" in str(exc_info.value).lower()

    def test_exception_hierarchy(self):
        """例外の階層構造を確認"""
        assert issubclass(NanaSQLiteValidationError, NanaSQLiteError)
        assert issubclass(NanaSQLiteDatabaseError, NanaSQLiteError)
        assert issubclass(NanaSQLiteTransactionError, NanaSQLiteError)
        assert issubclass(NanaSQLiteConnectionError, NanaSQLiteError)


class TestTransactionEnhancements:
    """トランザクション機能の強化テスト"""

    def test_nested_transaction_detection(self, tmp_path):
        """ネストしたトランザクションの検出"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))

        db.begin_transaction()

        with pytest.raises(NanaSQLiteTransactionError) as exc_info:
            db.begin_transaction()

        assert "already in progress" in str(exc_info.value).lower()
        db.rollback()

    def test_commit_without_transaction(self, tmp_path):
        """トランザクション外でのコミット"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))

        with pytest.raises(NanaSQLiteTransactionError) as exc_info:
            db.commit()

        assert "no transaction in progress" in str(exc_info.value).lower()

    def test_rollback_without_transaction(self, tmp_path):
        """トランザクション外でのロールバック"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))

        with pytest.raises(NanaSQLiteTransactionError) as exc_info:
            db.rollback()

        assert "no transaction in progress" in str(exc_info.value).lower()

    def test_in_transaction_status(self, tmp_path):
        """トランザクション状態の確認"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))

        assert not db.in_transaction()

        db.begin_transaction()
        assert db.in_transaction()

        db.commit()
        assert not db.in_transaction()

    def test_close_during_transaction(self, tmp_path):
        """トランザクション中の接続クローズ"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))

        db.begin_transaction()
        db["key"] = "value"

        with pytest.raises(NanaSQLiteTransactionError) as exc_info:
            db.close()

        assert "transaction is in progress" in str(exc_info.value).lower()

        # クリーンアップ
        db.rollback()
        db.close()

    def test_transaction_state_after_commit_error(self, tmp_path):
        """コミットエラー後のトランザクション状態"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))
        db.create_table("test", {"id": "INTEGER PRIMARY KEY", "value": "TEXT"})

        db.begin_transaction()
        db.sql_insert("test", {"id": 1, "value": "data"})

        # 状態確認
        assert db.in_transaction()

        # 正常にコミット
        db.commit()
        assert not db.in_transaction()


class TestResourceManagement:
    """リソース管理のテスト"""

    def test_child_instance_after_parent_close(self, tmp_path):
        """親インスタンスを閉じた後の子インスタンス"""
        db_path = tmp_path / "test.db"
        main_db = NanaSQLite(str(db_path))
        sub_db = main_db.table("subtable")

        # 親を閉じる
        main_db.close()

        # 子インスタンスの使用でエラー
        with pytest.raises(NanaSQLiteConnectionError) as exc_info:
            sub_db["key"] = "value"

        assert "parent" in str(exc_info.value).lower() or "closed" in str(exc_info.value).lower()

    def test_context_manager_with_child_instances(self, tmp_path):
        """コンテキストマネージャでの親子インスタンス"""
        db_path = tmp_path / "test.db"

        with NanaSQLite(str(db_path)) as main_db:
            sub_db = main_db.table("subtable")
            sub_db["key"] = "value"
            assert sub_db["key"] == "value"

        # コンテキスト外では使用不可
        with pytest.raises(NanaSQLiteConnectionError):
            sub_db["key2"] = "value2"

    def test_multiple_close_safe(self, tmp_path):
        """複数回のclose()が安全"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))

        db.close()
        db.close()  # 2回目のcloseは問題なし
        db.close()  # 3回目も問題なし


class TestErrorHandling:
    """エラーハンドリングの改善テスト"""

    def test_database_error_with_original_error(self, tmp_path):
        """DatabaseErrorが元のエラーを保持"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))

        try:
            db.execute("SELECT * FROM nonexistent_table")
        except NanaSQLiteDatabaseError as e:
            assert e.original_error is not None
            assert "original_error" in dir(e)

    def test_catch_all_nanasqlite_errors(self, tmp_path):
        """すべてのNanaSQLiteエラーをキャッチ"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))

        errors_caught = []

        # ValidationError
        try:
            db.create_table("123", {"id": "INTEGER"})
        except NanaSQLiteError as e:
            errors_caught.append(type(e).__name__)

        # DatabaseError
        try:
            db.execute("INVALID SQL")
        except NanaSQLiteError as e:
            errors_caught.append(type(e).__name__)

        # ConnectionError
        db.close()
        try:
            db["key"] = "value"
        except NanaSQLiteError as e:
            errors_caught.append(type(e).__name__)

        assert len(errors_caught) == 3
        assert "NanaSQLiteValidationError" in errors_caught
        assert "NanaSQLiteDatabaseError" in errors_caught
        # accept either broad ConnectionError or specific ClosedError
        assert any(name in errors_caught for name in ["NanaSQLiteConnectionError", "NanaSQLiteClosedError"])


class TestTransactionWithExceptions:
    """トランザクションと例外の組み合わせテスト"""

    def test_transaction_rollback_on_validation_error(self, tmp_path):
        """ValidationError時のトランザクションロールバック"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))
        db.create_table("test", {"id": "INTEGER", "value": "TEXT"})

        try:
            with db.transaction():
                db.sql_insert("test", {"id": 1, "value": "data1"})
                # 不正な識別子でエラー
                db.create_table("123invalid", {"id": "INTEGER"})
        except NanaSQLiteValidationError:
            pass

        # ロールバックされているので、挿入されていない
        assert db.count("test") == 0

    def test_transaction_rollback_on_database_error(self, tmp_path):
        """DatabaseError時のトランザクションロールバック"""
        db_path = tmp_path / "test.db"
        db = NanaSQLite(str(db_path))
        db.create_table("test", {"id": "INTEGER PRIMARY KEY", "value": "TEXT"})

        try:
            with db.transaction():
                db.sql_insert("test", {"id": 1, "value": "data1"})
                db.sql_insert("test", {"id": 2, "value": "data2"})
                # 重複キーでエラー
                db.sql_insert("test", {"id": 1, "value": "duplicate"})
        except NanaSQLiteDatabaseError:
            pass

        # ロールバックされているので、何も挿入されていない
        assert db.count("test") == 0


@pytest.mark.asyncio
class TestAsyncTransactions:
    """非同期版トランザクションのテスト"""

    async def test_async_transaction_context(self, tmp_path):
        """非同期トランザクションコンテキストマネージャ"""
        from nanasqlite import AsyncNanaSQLite

        db_path = tmp_path / "async_test.db"
        async with AsyncNanaSQLite(str(db_path)) as db:
            await db.create_table("test", {"id": "INTEGER", "value": "TEXT"})

            async with db.transaction():
                await db.sql_insert("test", {"id": 1, "value": "data1"})
                await db.sql_insert("test", {"id": 2, "value": "data2"})

            count = await db.fetch_one("SELECT COUNT(*) FROM test")
            assert count[0] == 2

    async def test_async_transaction_rollback(self, tmp_path):
        """非同期トランザクションのロールバック"""
        from nanasqlite import AsyncNanaSQLite

        db_path = tmp_path / "async_test.db"
        async with AsyncNanaSQLite(str(db_path)) as db:
            await db.create_table("test", {"id": "INTEGER PRIMARY KEY", "value": "TEXT"})

            try:
                async with db.transaction():
                    await db.sql_insert("test", {"id": 1, "value": "data1"})
                    await db.sql_insert("test", {"id": 2, "value": "data2"})
                    # エラーを発生させる
                    await db.sql_insert("test", {"id": 1, "value": "duplicate"})
            except Exception:
                pass

            count = await db.fetch_one("SELECT COUNT(*) FROM test")
            assert count[0] == 0  # ロールバックされている

    async def test_async_in_transaction(self, tmp_path):
        """非同期版のトランザクション状態確認"""
        from nanasqlite import AsyncNanaSQLite

        db_path = tmp_path / "async_test.db"
        async with AsyncNanaSQLite(str(db_path)) as db:
            assert not await db.in_transaction()

            await db.begin_transaction()
            assert await db.in_transaction()

            await db.commit()
            assert not await db.in_transaction()
