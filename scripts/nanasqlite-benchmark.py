# benchmark.py
import os
import shutil
import tempfile
import time

from src.nanasqlite import NanaSQLite


class Benchmark:
    def __init__(self):
        # 一時ディレクトリを作成（Windows対策）
        self.temp_dir = tempfile.mkdtemp()
        self.results = {}

    def cleanup(self):
        """Windowsでファイルロックが解除されるまで待機して削除"""
        time.sleep(0.1)  # ファイルハンドルの解放を待つ
        try:
            shutil.rmtree(self.temp_dir)
        except PermissionError:
            # Windowsでロックが残っている場合はリトライ
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
            db = NanaSQLite(db_path)
            db.close()
            end = time.perf_counter()

            times.append(end - start)

            # Windows対策: ファイルハンドルを確実に閉じる
            time.sleep(0.01)

        avg_time = sum(times) / len(times)
        self.results["初期化"] = avg_time
        print(f"   平均: {avg_time * 1000:.2f}ms")

    def benchmark_write(self, count=1000):
        """書き込み速度テスト"""
        print(f"✍️  単純書き込みテスト ({count}件)...")
        db_path = self.get_db_path("write")

        db = NanaSQLite(db_path)

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

        db = NanaSQLite(db_path)

        # バッチデータ準備
        batch_data = {f"key_{i}": {"id": i, "name": f"user_{i}", "score": i * 10} for i in range(count)}

        start = time.perf_counter()
        db.batch_update(batch_data)
        end = time.perf_counter()

        db.close()

        elapsed = end - start
        self.results[f"バッチ書き込み({count}件)"] = elapsed
        print(f"   合計: {elapsed:.3f}秒 ({count / elapsed:.0f}件/秒)")

    def benchmark_read(self, count=1000):
        """読み取り速度テスト（遅延ロード）"""
        print(f"📖 読み取りテスト - 遅延ロード ({count}件)...")
        db_path = self.get_db_path("read")

        # データを準備
        db = NanaSQLite(db_path)
        batch_data = {f"key_{i}": {"id": i, "name": f"user_{i}", "score": i * 10} for i in range(count)}
        db.batch_update(batch_data)
        db.close()

        # Windows対策: ファイルハンドル解放待機
        time.sleep(0.1)

        # 読み取りテスト
        db = NanaSQLite(db_path)

        start = time.perf_counter()
        for i in range(count):
            _ = db[f"key_{i}"]
        end = time.perf_counter()

        db.close()

        elapsed = end - start
        self.results[f"遅延ロード読み取り({count}件)"] = elapsed
        print(f"   合計: {elapsed:.3f}秒 ({count / elapsed:.0f}件/秒)")

    def benchmark_bulk_read(self, count=1000):
        """読み取り速度テスト（一括ロード）"""
        print(f"📚 読み取りテスト - 一括ロード ({count}件)...")
        db_path = self.get_db_path("bulk_read")

        # データを準備
        db = NanaSQLite(db_path)
        batch_data = {f"key_{i}": {"id": i, "name": f"user_{i}", "score": i * 10} for i in range(count)}
        db.batch_update(batch_data)
        db.close()

        # Windows対策: ファイルハンドル解放待機
        time.sleep(0.1)

        # 一括ロードして読み取り
        start = time.perf_counter()
        db = NanaSQLite(db_path, bulk_load=True)
        load_time = time.perf_counter() - start

        read_start = time.perf_counter()
        for i in range(count):
            _ = db[f"key_{i}"]
        read_end = time.perf_counter()

        db.close()

        total_elapsed = read_end - start
        read_elapsed = read_end - read_start
        self.results[f"一括ロード({count}件)"] = load_time
        self.results[f"一括ロード後読み取り({count}件)"] = read_elapsed
        print(f"   ロード時間: {load_time:.3f}秒")
        print(f"   読み取り時間: {read_elapsed:.3f}秒 ({count / read_elapsed:.0f}件/秒)")
        print(f"   合計: {total_elapsed:.3f}秒")

    def benchmark_nested_data(self, count=100):
        """ネストデータ処理テスト"""
        print(f"🎯 ネストデータ処理テスト ({count}件)...")
        db_path = self.get_db_path("nested")

        db = NanaSQLite(db_path)

        # 深くネストしたデータ
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

        db = NanaSQLite(db_path)

        # 初期データ
        for i in range(count):
            db[f"key_{i}"] = {"value": i}

        start = time.perf_counter()
        for i in range(count):
            # 読み取り
            _ = db[f"key_{i}"]
            # 更新
            db[f"key_{i}"] = {"value": i * 2}
            # 新規追加
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
        print("🚀 NanaSQLite ベンチマーク開始\n")

        try:
            self.benchmark_init(iterations=100)
            self.benchmark_write(count=1000)
            self.benchmark_batch_write(count=1000)
            self.benchmark_read(count=1000)
            self.benchmark_bulk_read(count=1000)
            self.benchmark_nested_data(count=100)
            self.benchmark_mixed_operations(count=500)

            self.print_summary()

        finally:
            print("\n🧹 クリーンアップ中...")
            self.cleanup()
            print("✅ 完了！")


if __name__ == "__main__":
    benchmark = Benchmark()
    benchmark.run_all()
