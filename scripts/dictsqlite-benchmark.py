# benchmark_dictsqlite.py
import os
import shutil
import tempfile
import time

from dictsqlite import DictSQLite


class BenchmarkDictSQLite:
    def __init__(self):
        # 一時ディレクトリを作成（Windows対策）
        self.temp_dir = tempfile.mkdtemp()
        self.results = {}

    def cleanup(self):
        """Windowsでファイルロックが解除されるまで待機して削除"""
        time.sleep(0.1)
        try:
            shutil.rmtree(self.temp_dir)
        except PermissionError:
            time.sleep(0.5)
            shutil.rmtree(self.temp_dir)

    def get_db_path(self, name):
        """一時ディレクトリ内のDBパスを取得"""
        return os.path.join(self.temp_dir, f"{name}.db")

    def benchmark_init(self, iterations=100):
        """初期化速度テスト"""
        print("🔧 初期化速度テスト...")
        times = []

        for i in range(iterations):
            db_path = self.get_db_path(f"init_{i}")

            start = time.perf_counter()
            db = DictSQLite(db_path)
            db.close()
            end = time.perf_counter()

            times.append(end - start)
            time.sleep(0.01)

        avg_time = sum(times) / len(times)
        self.results["初期化"] = avg_time
        print(f"   平均: {avg_time * 1000:.2f}ms")

    def benchmark_write(self, count=1000):
        """書き込み速度テスト"""
        print(f"✍️  単純書き込みテスト ({count}件)...")
        db_path = self.get_db_path("write")

        db = DictSQLite(db_path)

        start = time.perf_counter()
        for i in range(count):
            db[f"key_{i}"] = {"id": i, "name": f"user_{i}", "score": i * 10}
        end = time.perf_counter()

        db.close()

        elapsed = end - start
        self.results[f"単純書き込み({count}件)"] = elapsed
        print(f"   合計: {elapsed:.3f}秒 ({count / elapsed:.0f}件/秒)")

    def benchmark_batch_write(self, count=1000):
        """バッチ書き込み速度テスト"""
        print(f"⚡ バッチ書き込みテスト ({count}件)...")
        db_path = self.get_db_path("batch_write")

        db = DictSQLite(db_path)

        # バッチデータ準備
        batch_data = {f"key_{i}": {"id": i, "name": f"user_{i}", "score": i * 10} for i in range(count)}

        start = time.perf_counter()
        # DictSQLiteのバッチ操作（存在する場合）
        if hasattr(db, "batch_update"):
            db.batch_update(batch_data)
        else:
            # なければ通常の書き込み
            for key, value in batch_data.items():
                db[key] = value
        end = time.perf_counter()

        db.close()

        elapsed = end - start
        self.results[f"バッチ書き込み({count}件)"] = elapsed
        print(f"   合計: {elapsed:.3f}秒 ({count / elapsed:.0f}件/秒)")

    def benchmark_read(self, count=1000):
        """読み取り速度テスト"""
        print(f"📖 読み取りテスト ({count}件)...")
        db_path = self.get_db_path("read")

        # データを準備
        db = DictSQLite(db_path)
        batch_data = {f"key_{i}": {"id": i, "name": f"user_{i}", "score": i * 10} for i in range(count)}
        for key, value in batch_data.items():
            db[key] = value
        db.close()

        time.sleep(0.1)

        # 読み取りテスト
        db = DictSQLite(db_path)

        start = time.perf_counter()
        for i in range(count):
            _ = db[f"key_{i}"]
        end = time.perf_counter()

        db.close()

        elapsed = end - start
        self.results[f"読み取り({count}件)"] = elapsed
        print(f"   合計: {elapsed:.3f}秒 ({count / elapsed:.0f}件/秒)")

    def benchmark_nested_data(self, count=100):
        """ネストデータ処理テスト"""
        print(f"🎯 ネストデータ処理テスト ({count}件)...")
        db_path = self.get_db_path("nested")

        db = DictSQLite(db_path)

        nested_data = {"level1": {"level2": {"level3": {"level4": {"level5": {"data": list(range(100))}}}}}}

        start = time.perf_counter()
        for i in range(count):
            db[f"nested_{i}"] = nested_data
        end = time.perf_counter()

        db.close()

        elapsed = end - start
        self.results[f"ネストデータ({count}件)"] = elapsed
        print(f"   合計: {elapsed:.3f}秒 ({count / elapsed:.0f}件/秒)")

    def benchmark_mixed_operations(self, count=500):
        """混合操作テスト"""
        print(f"🔀 混合操作テスト (読み書き {count}件ずつ)...")
        db_path = self.get_db_path("mixed")

        db = DictSQLite(db_path)

        # 初期データ
        for i in range(count):
            db[f"key_{i}"] = {"value": i}

        start = time.perf_counter()
        for i in range(count):
            _ = db[f"key_{i}"]
            db[f"key_{i}"] = {"value": i * 2}
            db[f"new_key_{i}"] = {"value": i * 3}
        end = time.perf_counter()

        db.close()

        elapsed = end - start
        self.results[f"混合操作({count * 3}操作)"] = elapsed
        print(f"   合計: {elapsed:.3f}秒 ({(count * 3) / elapsed:.0f}操作/秒)")

    def print_summary(self):
        """結果サマリー表示"""
        print("\n" + "=" * 50)
        print("📊 ベンチマーク結果サマリー")
        print("=" * 50)

        for name, time_val in self.results.items():
            print(f"{name:30s}: {time_val * 1000:8.2f}ms")

        print("=" * 50)

    def run_all(self):
        """全ベンチマーク実行"""
        print("🚀 DictSQLite ベンチマーク開始\n")

        try:
            self.benchmark_init(iterations=100)
            self.benchmark_write(count=1000)
            self.benchmark_batch_write(count=1000)
            self.benchmark_read(count=1000)
            self.benchmark_nested_data(count=100)
            self.benchmark_mixed_operations(count=500)

            self.print_summary()

        finally:
            print("\n🧹 クリーンアップ中...")
            self.cleanup()
            print("✅ 完了！")


if __name__ == "__main__":
    benchmark = BenchmarkDictSQLite()
    benchmark.run_all()
