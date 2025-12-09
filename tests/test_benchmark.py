"""
NanaSQLite Performance Benchmarks

pytest-benchmarkを使用したパフォーマンス計測
"""

import os
import tempfile
import pytest

import importlib.util

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
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "data": [1, 2, 3, {"nested": True}]
                    }
                }
            }
        }
        def write_nested():
            db[f"nested_{counter[0]}"] = nested_data
            counter[0] += 1
        
        benchmark(write_nested)
    
    def test_batch_write_100(self, benchmark, db_path):
        """バッチ書き込み（100件）"""
        from nanasqlite import NanaSQLite
        
        def batch_write():
            database = NanaSQLite(db_path)
            data = {f"batch_{i}": {"index": i} for i in range(100)}
            database.batch_update(data)
            database.close()
        
        benchmark(batch_write)


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
        
        # データ準備
        db = NanaSQLite(db_path)
        db["target"] = {"data": "value"}
        db.close()
        
        def read_uncached():
            database = NanaSQLite(db_path, bulk_load=False)
            result = database["target"]
            database.close()
            return result
        
        benchmark(read_uncached)
    
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


# ==================== New Wrapper Functions Benchmarks ====================

@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestWrapperFunctionsBenchmarks:
    """新しいラッパー関数のベンチマーク"""
    
    def test_sql_insert_single(self, benchmark, db_path):
        """sql_insert()単一挿入"""
        from nanasqlite import NanaSQLite
        
        db = NanaSQLite(db_path)
        db.create_table("users", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT",
            "age": "INTEGER"
        })
        
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
        db.create_table("users", {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT",
            "age": "INTEGER"
        })
        
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
