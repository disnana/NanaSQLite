"""
NanaSQLite Performance Benchmarks

pytest-benchmarkを使用したパフォーマンス計測
"""

import importlib.util
import os
import tempfile

import pytest

# pytest-benchmarkがインストールされているか確認
pytest_benchmark_available = importlib.util.find_spec("pytest_benchmark") is not None


# テスト用のフィクスチャ
@pytest.fixture
def db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "bench.db")


@pytest.fixture
def db(db_path):
    from nanasqlite import NanaSQLite

    database = NanaSQLite(db_path)
    yield database
    database.close()


@pytest.fixture
def db_with_data(db_path):
    """1000件のデータが入ったDB"""
    from nanasqlite import NanaSQLite

    database = NanaSQLite(db_path)
    for i in range(1000):
        database[f"key_{i}"] = {"index": i, "data": "x" * 100}
    yield database
    database.close()


# ==================== Write Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestWriteBenchmarks:
    """書き込みパフォーマンスのベンチマーク"""

    def test_single_write(self, benchmark, db):
        """単一書き込み"""
        counter = [0]

        def write_single():
            db[f"key_{counter[0]}"] = {"data": "value", "number": counter[0]}
            counter[0] += 1

        benchmark(write_single)

    def test_nested_write(self, benchmark, db):
        """ネストしたデータの書き込み"""
        counter = [0]
        nested_data = {"level1": {"level2": {"level3": {"data": [1, 2, 3, {"nested": True}]}}}}

        def write_nested():
            db[f"nested_{counter[0]}"] = nested_data
            counter[0] += 1

        benchmark(write_nested)

    def test_batch_write_100(self, benchmark, db_path):
        """バッチ書き込み（100件）"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        counter = [0]

        def batch_write():
            data = {f"batch_{counter[0]}_{i}": {"index": i} for i in range(100)}
            db.batch_update(data)
            counter[0] += 1

        benchmark(batch_write)
        db.close()


# ==================== Read Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestReadBenchmarks:
    """読み込みパフォーマンスのベンチマーク"""

    def test_single_read_cached(self, benchmark, db_with_data):
        """単一読み込み（キャッシュ済み）"""
        # まずキャッシュに入れる
        _ = db_with_data["key_500"]

        def read_cached():
            return db_with_data["key_500"]

        benchmark(read_cached)

    def test_single_read_uncached(self, benchmark, db_path):
        """単一読み込み（未キャッシュ）"""
        from nanasqlite import NanaSQLite

        # 大量のデータを準備して、キャッシュをバイパスするようにする
        db = NanaSQLite(db_path)
        try:
            keys = [f"uncached_{i}" for i in range(1000)]
            db.batch_update({k: {"data": "value"} for k in keys})

            counter = [0]

            def read_uncached():
                # キャッシュにないキーを順番に取得していく
                key = keys[counter[0] % 1000]
                result = db[key]
                # キャッシュをクリアして次のラウンドに備える（refresh()を使用）
                db.refresh()
                counter[0] += 1
                return result

            benchmark(read_uncached)
        finally:
            db.close()

    def test_bulk_load_1000(self, benchmark, db_path):
        """一括ロード（1000件）"""
        from nanasqlite import NanaSQLite

        # データ準備
        db = NanaSQLite(db_path)
        db.batch_update({f"key_{i}": {"index": i} for i in range(1000)})
        db.close()

        def bulk_load():
            database = NanaSQLite(db_path, bulk_load=True)
            database.close()

        benchmark(bulk_load)


# ==================== Dict Operations Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestDictOperationsBenchmarks:
    """dict操作のベンチマーク"""

    def test_keys_1000(self, benchmark, db_with_data):
        """keys()取得（1000件）"""
        benchmark(db_with_data.keys)

    def test_contains_check(self, benchmark, db_with_data):
        """存在確認（in演算子）"""

        def check_contains():
            return "key_500" in db_with_data

        benchmark(check_contains)

    def test_len(self, benchmark, db_with_data):
        """len()取得"""
        benchmark(len, db_with_data)

    def test_to_dict_1000(self, benchmark, db_with_data):
        """to_dict()変換（1000件）"""
        benchmark(db_with_data.to_dict)

    def test_batch_get(self, benchmark, db_with_data):
        """batch_get()取得（100件）"""
        keys = [f"key_{i}" for i in range(100)]
        benchmark(db_with_data.batch_get, keys)

    def test_is_cached(self, benchmark, db_with_data):
        """is_cached()チェック"""
        _ = db_with_data["key_0"]
        benchmark(db_with_data.is_cached, "key_0")

    def test_refresh(self, benchmark, db_with_data):
        """refresh()全件再読み込み"""
        benchmark(db_with_data.refresh)

    def test_copy(self, benchmark, db_with_data):
        """copy()浅いコピー"""
        benchmark(db_with_data.copy)

    def test_nested_read_deep(self, benchmark, db):
        """ネストしたデータの読み込み（30層）"""
        data = "value"
        for _ in range(30):
            data = {"nested": data}
        db["deep"] = data
        db.refresh()  # キャッシュクリアしてDBから読ませる

        def read_deep():
            res = db["deep"]
            db.refresh()
            return res

        benchmark(read_deep)

    def test_nested_write_deep(self, benchmark, db):
        """ネストしたデータの書き込み（30層）"""
        data = "value"
        for _ in range(30):
            data = {"nested": data}

        counter = [0]

        def write_deep():
            db[f"deep_{counter[0]}"] = data
            counter[0] += 1

        benchmark(write_deep)


# ==================== New Wrapper Functions Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestWrapperFunctionsBenchmarks:
    """新しいラッパー関数のベンチマーク"""

    def test_sql_insert_single(self, benchmark, db_path):
        """sql_insert()単一挿入"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("users", {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "name": "TEXT", "age": "INTEGER"})

        counter = [0]

        def insert_single():
            db.sql_insert("users", {"name": f"User{counter[0]}", "age": 25})
            counter[0] += 1

        benchmark(insert_single)
        db.close()

    def test_sql_update_single(self, benchmark, db_path):
        """sql_update()単一更新"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("users", {"id": "INTEGER", "name": "TEXT", "age": "INTEGER"})

        # データ準備
        for i in range(100):
            db.sql_insert("users", {"id": i, "name": f"User{i}", "age": 25})

        counter = [0]

        def update_single():
            db.sql_update("users", {"age": 26}, "id = ?", (counter[0] % 100,))
            counter[0] += 1

        benchmark(update_single)
        db.close()

    def test_upsert(self, benchmark, db_path):
        """upsert()操作"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"})

        counter = [0]

        def upsert_op():
            db.upsert("users", {"id": counter[0] % 50, "name": f"User{counter[0]}", "age": 25})
            counter[0] += 1

        benchmark(upsert_op)
        db.close()

    def test_query_with_pagination(self, benchmark, db_path):
        """query_with_pagination()ページネーション"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("items", {"id": "INTEGER", "name": "TEXT"})

        # データ準備
        for i in range(1000):
            db.sql_insert("items", {"id": i, "name": f"Item{i}"})

        def query_page():
            return db.query_with_pagination("items", limit=10, offset=0, order_by="id ASC")

        benchmark(query_page)
        db.close()

    def test_count_operation(self, benchmark, db_path):
        """count()レコード数取得"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("items", {"id": "INTEGER", "value": "INTEGER"})

        # データ準備
        for i in range(1000):
            db.sql_insert("items", {"id": i, "value": i})

        def count_records():
            return db.count("items", "value > ?", (500,))

        benchmark(count_records)
        db.close()

    def test_exists_check(self, benchmark, db_path):
        """exists()存在確認"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("users", {"id": "INTEGER", "email": "TEXT"})

        # データ準備
        for i in range(1000):
            db.sql_insert("users", {"id": i, "email": f"user{i}@example.com"})

        def check_exists():
            return db.exists("users", "email = ?", ("user500@example.com",))

        benchmark(check_exists)
        db.close()

    def test_export_import_roundtrip(self, benchmark, db_path):
        """export/import往復（エクスポート部分のみ計測）"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("export_test", {"id": "INTEGER", "value": "TEXT"})

        # データ準備
        data_list = [{"id": i, "value": f"data{i}"} for i in range(100)]
        db.import_from_dict_list("export_test", data_list)

        def export_operation():
            # エクスポート操作のパフォーマンスを計測
            exported = db.export_table_to_dict("export_test")
            return exported

        benchmark(export_operation)
        db.close()

    def test_transaction_context(self, benchmark, db_path):
        """transaction()コンテキストマネージャ"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("logs", {"id": "INTEGER", "message": "TEXT"})

        counter = [0]

        def transaction_op():
            with db.transaction():
                db.sql_insert("logs", {"id": counter[0], "message": f"Log{counter[0]}"})
                counter[0] += 1

        benchmark(transaction_op)
        db.close()


# ==================== DDL Operations Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestDDLOperationsBenchmarks:
    """DDL操作のベンチマーク"""

    def test_create_index(self, benchmark, db_path):
        """create_index()インデックス作成"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("idx_create_test", {"id": "INTEGER", "name": "TEXT"})
        counter = [0]

        def create_idx():
            idx_name = f"idx_{counter[0]}"
            db.create_index(idx_name, "idx_create_test", ["name"], if_not_exists=True)
            db.drop_index(idx_name)  # 次のラウンドのために削除
            counter[0] += 1

        benchmark(create_idx)
        db.close()

    def test_drop_table(self, benchmark, db_path):
        """drop_table()テーブル削除"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        counter = [0]

        def drop_tbl():
            table_name = f"drop_test_{counter[0]}"
            db.create_table(table_name, {"id": "INTEGER"})
            db.drop_table(table_name)
            counter[0] += 1

        benchmark(drop_tbl)
        db.close()

    def test_drop_index(self, benchmark, db_path):
        """drop_index()インデックス削除"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("idx_test", {"id": "INTEGER", "name": "TEXT"})
        counter = [0]

        def drop_idx():
            idx_name = f"idx_drop_{counter[0]}"
            db.create_index(idx_name, "idx_test", ["name"], if_not_exists=True)
            db.drop_index(idx_name)
            counter[0] += 1

        benchmark(drop_idx)
        db.close()

    def test_alter_table_add_column(self, benchmark, db_path):
        """alter_table_add_column()カラム追加"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        counter = [0]

        def add_col():
            table_name = f"alter_test_{counter[0]}"
            db.create_table(table_name, {"id": "INTEGER"})
            db.alter_table_add_column(table_name, "new_col", "TEXT")
            counter[0] += 1

        benchmark(add_col)
        db.close()

    def test_sql_delete(self, benchmark, db_path):
        """sql_delete()行削除"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("delete_test", {"id": "INTEGER", "name": "TEXT"})

        # 事前にデータを準備
        for i in range(10000):
            db.sql_insert("delete_test", {"id": i, "name": f"User{i}"})

        counter = [0]

        def delete_op():
            db.sql_delete("delete_test", "id = ?", (counter[0] % 10000,))
            # 削除したデータを再挿入して次のラウンドに備える
            db.sql_insert("delete_test", {"id": counter[0] % 10000, "name": f"User{counter[0]}"})
            counter[0] += 1

        benchmark(delete_op)
        db.close()


# ==================== Query Operations Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestQueryOperationsBenchmarks:
    """クエリ操作のベンチマーク"""

    def test_query_simple(self, benchmark, db_path):
        """query()シンプルクエリ"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("query_test", {"id": "INTEGER", "name": "TEXT", "age": "INTEGER"})

        # データ準備
        for i in range(1000):
            db.sql_insert("query_test", {"id": i, "name": f"User{i}", "age": i % 100})

        def query_op():
            return db.query("query_test", columns=["id", "name"], where="age > ?", parameters=(50,), limit=10)

        benchmark(query_op)
        db.close()

    def test_fetch_one(self, benchmark, db_path):
        """fetch_one()1行取得"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("fetch_test", {"id": "INTEGER", "value": "TEXT"})

        for i in range(1000):
            db.sql_insert("fetch_test", {"id": i, "value": f"data{i}"})

        def fetch_one_op():
            return db.fetch_one("SELECT * FROM fetch_test WHERE id = ?", (500,))

        benchmark(fetch_one_op)
        db.close()

    def test_fetch_all_1000(self, benchmark, db_path):
        """fetch_all()全行取得（1000件）"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("fetch_all_test", {"id": "INTEGER", "value": "TEXT"})

        for i in range(1000):
            db.sql_insert("fetch_all_test", {"id": i, "value": f"data{i}"})

        def fetch_all_op():
            return db.fetch_all("SELECT * FROM fetch_all_test")

        benchmark(fetch_all_op)
        db.close()


# ==================== Schema Operations Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestSchemaOperationsBenchmarks:
    """スキーマ操作のベンチマーク"""

    def test_table_exists(self, benchmark, db_path):
        """table_exists()テーブル存在確認"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("exists_test", {"id": "INTEGER"})

        def table_exists_op():
            return db.table_exists("exists_test")

        benchmark(table_exists_op)
        db.close()

    def test_list_tables(self, benchmark, db_path):
        """list_tables()テーブル一覧"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        # 20個のテーブルを作成
        for i in range(20):
            db.create_table(f"list_test_{i}", {"id": "INTEGER"})

        def list_tables_op():
            return db.list_tables()

        benchmark(list_tables_op)
        db.close()

    def test_get_table_schema(self, benchmark, db_path):
        """get_table_schema()スキーマ取得"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table(
            "schema_test",
            {
                "id": "INTEGER PRIMARY KEY",
                "name": "TEXT NOT NULL",
                "email": "TEXT",
                "age": "INTEGER",
                "created_at": "TEXT",
            },
        )

        def get_schema_op():
            return db.get_table_schema("schema_test")

        benchmark(get_schema_op)
        db.close()

    def test_list_indexes(self, benchmark, db_path):
        """list_indexes()インデックス一覧"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("index_list_test", {"id": "INTEGER", "name": "TEXT", "email": "TEXT"})
        db.create_index("idx_name", "index_list_test", ["name"])
        db.create_index("idx_email", "index_list_test", ["email"])
        db.create_index("idx_name_email", "index_list_test", ["name", "email"])

        def list_indexes_op():
            return db.list_indexes("index_list_test")

        benchmark(list_indexes_op)
        db.close()


# ==================== Utility Operations Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestUtilityOperationsBenchmarks:
    """ユーティリティ操作のベンチマーク"""

    def test_get_fresh(self, benchmark, db_path):
        """get_fresh()キャッシュバイパス読み込み"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db["target_key"] = {"data": "value", "number": 123}

        def get_fresh_op():
            return db.get_fresh("target_key")

        benchmark(get_fresh_op)
        db.close()

    def test_batch_delete(self, benchmark, db_path):
        """batch_delete()一括削除"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        counter = [0]

        def batch_delete_op():
            # データ作成
            keys = [f"batch_del_{counter[0]}_{i}" for i in range(100)]
            db.batch_update({k: {"value": i} for i, k in enumerate(keys)})
            # 一括削除
            db.batch_delete(keys)
            counter[0] += 1

        benchmark(batch_delete_op)
        db.close()

    def test_vacuum(self, benchmark, db_path):
        """vacuum()最適化"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        # データを追加して削除（断片化を発生させる）
        for i in range(100):
            db[f"vac_key_{i}"] = {"data": "x" * 100}
        for i in range(50):  # 半分だけ削除して断片化を維持
            del db[f"vac_key_{i}"]

        counter = [0]

        def vacuum_op():
            # 各ラウンドでデータを追加・削除して断片化を維持
            db[f"vac_extra_{counter[0]}"] = {"data": "y" * 100}
            if counter[0] > 0:
                del db[f"vac_extra_{counter[0] - 1}"]
            db.vacuum()
            counter[0] += 1

        benchmark(vacuum_op)
        db.close()

    def test_get_db_size(self, benchmark, db_path):
        """get_db_size()サイズ取得"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        for i in range(100):
            db[f"size_key_{i}"] = {"data": "x" * 100}

        def get_db_size_op():
            return db.get_db_size()

        benchmark(get_db_size_op)
        db.close()

    def test_get_last_insert_rowid(self, benchmark, db_path):
        """get_last_insert_rowid()ROWID取得"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("rowid_test", {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "name": "TEXT"})

        counter = [0]

        def get_rowid_op():
            db.sql_insert("rowid_test", {"name": f"User{counter[0]}"})
            rowid = db.get_last_insert_rowid()
            counter[0] += 1
            return rowid

        benchmark(get_rowid_op)
        db.close()

    def test_pragma(self, benchmark, db_path):
        """pragma()設定取得"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)

        def pragma_op():
            return db.pragma("journal_mode")

        benchmark(pragma_op)
        db.close()

    def test_execute_raw(self, benchmark, db_path):
        """execute()直接SQL実行"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("exec_test", {"id": "INTEGER", "value": "TEXT"})

        counter = [0]

        def execute_op():
            db.execute("INSERT INTO exec_test (id, value) VALUES (?, ?)", (counter[0], f"val{counter[0]}"))
            counter[0] += 1

        benchmark(execute_op)
        db.close()

    def test_execute_many(self, benchmark, db_path):
        """execute_many()一括SQL実行"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("exec_many_test", {"id": "INTEGER", "value": "TEXT"})
        counter = [0]

        def execute_many_op():
            base = counter[0] * 100
            params = [(base + i, f"val{i}") for i in range(100)]
            db.execute_many("INSERT INTO exec_many_test (id, value) VALUES (?, ?)", params)
            counter[0] += 1

        benchmark(execute_many_op)
        db.close()

    def test_import_from_dict_list(self, benchmark, db_path):
        """import_from_dict_list()一括インポート"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("import_test", {"id": "INTEGER", "name": "TEXT", "age": "INTEGER"})
        counter = [0]

        def import_op():
            base = counter[0] * 100
            data_list = [{"id": base + i, "name": f"User{i}", "age": i % 100} for i in range(100)]
            db.import_from_dict_list("import_test", data_list)
            counter[0] += 1

        benchmark(import_op)
        db.close()


# ==================== Pydantic Operations Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestPydanticOperationsBenchmarks:
    """Pydantic操作のベンチマーク"""

    def test_set_model(self, benchmark, db_path):
        """set_model()モデル保存"""
        try:
            from pydantic import BaseModel
        except ImportError:
            pytest.skip("pydantic not installed")

        from nanasqlite import NanaSQLite

        class TestUser(BaseModel):
            name: str
            age: int
            email: str

        db = NanaSQLite(db_path)
        counter = [0]

        def set_model_op():
            user = TestUser(name=f"User{counter[0]}", age=25, email=f"user{counter[0]}@example.com")
            db.set_model(f"user_{counter[0]}", user)
            counter[0] += 1

        benchmark(set_model_op)
        db.close()

    def test_get_model(self, benchmark, db_path):
        """get_model()モデル取得"""
        try:
            from pydantic import BaseModel
        except ImportError:
            pytest.skip("pydantic not installed")

        from nanasqlite import NanaSQLite

        class TestUser(BaseModel):
            name: str
            age: int
            email: str

        db = NanaSQLite(db_path)
        # 事前にモデルを保存
        for i in range(100):
            user = TestUser(name=f"User{i}", age=25, email=f"user{i}@example.com")
            db.set_model(f"model_user_{i}", user)

        counter = [0]

        def get_model_op():
            result = db.get_model(f"model_user_{counter[0] % 100}", TestUser)
            counter[0] += 1
            return result

        benchmark(get_model_op)
        db.close()


# ==================== Transaction Operations Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestTransactionOperationsBenchmarks:
    """トランザクション操作のベンチマーク"""

    def test_begin_commit(self, benchmark, db_path):
        """begin_transaction() + commit()"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("tx_test", {"id": "INTEGER", "value": "TEXT"})

        counter = [0]

        def begin_commit_op():
            db.begin_transaction()
            db.sql_insert("tx_test", {"id": counter[0], "value": f"val{counter[0]}"})
            db.commit()
            counter[0] += 1

        benchmark(begin_commit_op)
        db.close()

    def test_begin_rollback(self, benchmark, db_path):
        """begin_transaction() + rollback()"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("tx_rollback_test", {"id": "INTEGER", "value": "TEXT"})

        counter = [0]

        def begin_rollback_op():
            db.begin_transaction()
            db.sql_insert("tx_rollback_test", {"id": counter[0], "value": f"val{counter[0]}"})
            db.rollback()
            counter[0] += 1

        benchmark(begin_rollback_op)
        db.close()

    def test_context_manager_transaction(self, benchmark, db_path):
        """transaction()コンテキストマネージャ（成功時）"""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(db_path)
        db.create_table("tx_ctx_test", {"id": "INTEGER", "value": "TEXT"})

        counter = [0]

        def ctx_tx_op():
            with db.transaction():
                db.sql_insert("tx_ctx_test", {"id": counter[0], "value": f"val{counter[0]}"})
            counter[0] += 1

        benchmark(ctx_tx_op)
        db.close()


# ==================== Summary Test ====================


def test_benchmark_summary(db_path, capsys):
    """ベンチマーク結果サマリー（pytest-benchmark無しでも実行可能）"""
    import time

    from nanasqlite import NanaSQLite

    results = {}

    # 書き込みテスト
    db = NanaSQLite(db_path)
    start = time.perf_counter()
    for i in range(100):
        db[f"key_{i}"] = {"data": i}
    results["write_100"] = (time.perf_counter() - start) * 1000

    # 読み込みテスト（キャッシュ済み）
    start = time.perf_counter()
    for i in range(100):
        _ = db[f"key_{i}"]
    results["read_100_cached"] = (time.perf_counter() - start) * 1000

    db.close()

    # 一括ロードテスト
    start = time.perf_counter()
    db2 = NanaSQLite(db_path, bulk_load=True)
    results["bulk_load_100"] = (time.perf_counter() - start) * 1000
    db2.close()

    # 結果表示
    print("\n" + "=" * 50)
    print("📊 NanaSQLite Benchmark Summary")
    print("=" * 50)
    for name, ms in results.items():
        print(f"  {name}: {ms:.2f}ms")
    print("=" * 50)
