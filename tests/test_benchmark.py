"""
NanaSQLite Performance Benchmarks

pytest-benchmarkを使用したパフォーマンス計測
"""

import os
import tempfile
import pytest

# pytest-benchmarkがインストールされているか確認
pytest_benchmark_available = True
try:
    import pytest_benchmark
except ImportError:
    pytest_benchmark_available = False


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
