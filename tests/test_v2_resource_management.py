import threading
import time

from nanasqlite import NanaSQLite


def test_v2_engine_sharing_leak_fix(tmp_path):
    """table()を大量に呼び出してもV2Engine（スレッド）が量産されないことを確認

    V2モード時に sub-table インスタンスが親のエンジンを正しく共有し、
    スレッドおよび atexit ハンドラの累積によるプロセス終了時のハングやメモリリークを
    防止していることを検証します。
    """
    db_path = str(tmp_path / "test_leak_fix.db")

    # v2_mode=TrueでメインDBを作成
    db = NanaSQLite(db_path, v2_mode=True)

    try:
        # V2EngineのThreadPoolExecutorは最初のタスクまでスレッドを作らないため、
        # 確実にスレッドを起動させるためにダミーの書き込みを行う
        db["__init_v2__"] = True

        initial_threads = threading.active_count()

        # 100個のテーブル（サブインスタンス）を作成
        tables = []
        for i in range(100):
            t = db.table(f"table_{i}")
            # 子インスタンスでも、エンジンが正しくセットされているか確認
            assert t._v2_engine is not None, f"table_{i} has no V2Engine!"
            tables.append(t)

        current_threads = threading.active_count()

        # 以前の実装ではここでスレッドが100個増えていたはず。
        # 修正後は1つ（メインDBのV2Engine）のみ増えるはず。
        # (並列実行環境も考慮して余裕を持たせつつ、100は大きく下回ることを確認)
        assert current_threads < initial_threads + 5, (
            f"Too many threads created: {current_threads - initial_threads}. Engines are not being shared correctly."
        )

        # すべてのテーブルインスタンスが同一のV2Engineオブジェクトを共有していることを確認
        for t in tables:
            assert t._v2_engine is db._v2_engine, "V2Engine instance is not shared!"

    finally:
        db.close()
        # シャットダウン処理の完了を少し待機
        time.sleep(0.5)


def test_v2_engine_multiple_connections_resource_cleanup(tmp_path):
    """複数の独立した接続を閉じても、スレッドが正常にクリーンアップされることを確認"""
    initial_threads = threading.active_count()

    dbs = []
    for i in range(5):
        path = str(tmp_path / f"db_{i}.db")
        db = NanaSQLite(path, v2_mode=True)
        # スレッド起動を強制
        db["trigger"] = i
        dbs.append(db)

    threads_with_engines = threading.active_count()
    # エンジンごとにスレッドが作成されているはず
    assert threads_with_engines > initial_threads

    # 全て閉じる
    for db in dbs:
        db.close()

    # スレッドが終了するのを待機（最大1秒）
    time.sleep(1.0)
    final_threads = threading.active_count()

    # 完全に元に戻るか、少なくともエンジン分は減っているはず
    assert final_threads < threads_with_engines
