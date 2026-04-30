# benchmark.py
import argparse
import os
import shutil
import tempfile
import time

try:
    import apsw
except ImportError:
    pass

import sys
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from nanasqlite import NanaSQLite


class Benchmark:
    def __init__(self, in_memory=False, use_shm=False, v2_mode=False, multiplier=1.0):
        self.in_memory = in_memory
        self.v2_mode = v2_mode
        self.multiplier = multiplier

        # RAMディスクの使用可否を判定
        self.use_shm = use_shm and os.path.exists("/dev/shm") and os.access("/dev/shm", os.W_OK)
        
        base_dir = "/dev/shm" if self.use_shm else None
        # 一時ディレクトリを作成（Windows対策およびshm利用）
        self.temp_dir = tempfile.mkdtemp(dir=base_dir)
        self.results = {}
        
        # in_memory使用時のURIごとのマスター接続保持用
        self.master_connections = {}

    def cleanup(self):
        """Windowsでファイルロックが解除されるまで待機して削除"""
        # メモリDBのマスター接続を閉じる
        for conn in self.master_connections.values():
            try:
                conn.close()
            except Exception:
                pass
        self.master_connections.clear()
        
        time.sleep(0.1)  # ファイルハンドルの解放を待つ
        try:
            shutil.rmtree(self.temp_dir)
        except PermissionError:
            # Windowsでロックが残っている場合はリトライ
            time.sleep(0.5)
            shutil.rmtree(self.temp_dir)

    def get_db_path(self, name):
        """一時ディレクトリ内のDBパスを取得、またはインメモリURIを生成"""
        if self.in_memory:
            uri = f"file:{name}?mode=memory&cache=shared"
            if name not in self.master_connections and "apsw" in globals():
                # そのテストフェーズ中、データが消えないようにマスター接続を保持
                self.master_connections[name] = apsw.Connection(
                    uri, 
                    flags=apsw.SQLITE_OPEN_READWRITE | apsw.SQLITE_OPEN_CREATE | apsw.SQLITE_OPEN_URI | apsw.SQLITE_OPEN_SHAREDCACHE
                )
            return uri
        return os.path.join(self.temp_dir, f"{name}.db")

    def _create_db(self, path, **kwargs):
        """設定を反映したNanaSQLiteインスタンスを生成"""
        if self.v2_mode:
            kwargs["v2_mode"] = True
        return NanaSQLite(path, **kwargs)

    def benchmark_init(self, iterations=100):
        """初期化速度テスト"""
        print("🔧 初期化速度テスト...")
        times = []

        for i in range(iterations):
            db_path = self.get_db_path(f"init_{i}")

            start = time.perf_counter()
            db = self._create_db(db_path)
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

        db = self._create_db(db_path)

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

        db = self._create_db(db_path)

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
        db = self._create_db(db_path)
        batch_data = {f"key_{i}": {"id": i, "name": f"user_{i}", "score": i * 10} for i in range(count)}
        db.batch_update(batch_data)
        db.close()

        # Windows対策: ファイルハンドル解放待機
        time.sleep(0.1)

        # 読み取りテスト
        db = self._create_db(db_path)

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
        db = self._create_db(db_path)
        batch_data = {f"key_{i}": {"id": i, "name": f"user_{i}", "score": i * 10} for i in range(count)}
        db.batch_update(batch_data)
        db.close()

        # Windows対策: ファイルハンドル解放待機
        time.sleep(0.1)

        # 一括ロードして読み取り
        start = time.perf_counter()
        db = self._create_db(db_path, bulk_load=True)
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

        db = self._create_db(db_path)

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

        db = self._create_db(db_path)

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
            self.benchmark_init(iterations=int(100 * self.multiplier))
            self.benchmark_write(count=int(1000 * self.multiplier))
            self.benchmark_batch_write(count=int(1000 * self.multiplier))
            self.benchmark_read(count=int(1000 * self.multiplier))
            self.benchmark_bulk_read(count=int(1000 * self.multiplier))
            self.benchmark_nested_data(count=int(100 * self.multiplier))
            self.benchmark_mixed_operations(count=int(500 * self.multiplier))

            self.print_summary()

        finally:
            print("\n🧹 クリーンアップ中...")
            self.cleanup()
            print("✅ 完了！")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NanaSQLite Benchmark Script")
    parser.add_argument("--in-memory", action="store_true", help="Use in-memory database (:memory:)")
    parser.add_argument("--use-shm", action="store_true", help="Use RAM disk (/dev/shm) if available")
    parser.add_argument("--v2", action="store_true", help="Enable V2 engine for the benchmark")
    parser.add_argument("--multiplier", type=float, default=1.0, help="Multiplier for iteration counts")
    
    args = parser.parse_args()

    benchmark = Benchmark(
        in_memory=args.in_memory,
        use_shm=args.use_shm,
        v2_mode=args.v2,
        multiplier=args.multiplier
    )
    
    print("=" * 50)
    print(" Benchmarks Configuration")
    print("=" * 50)
    print(f" In-Memory Mode : {benchmark.in_memory}")
    print(f" RAM Disk (shm) : {benchmark.use_shm}")
    print(f" V2 Engine      : {benchmark.v2_mode}")
    print(f" Multiplier     : {benchmark.multiplier}")
    print("=" * 50 + "\n")
    
    benchmark.run_all()
