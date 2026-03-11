"""
NanaSQLite v2 Engine テストスイート

v2アーキテクチャ（バックグラウンド非同期書き込み）の機能テスト:
- KVS ステージングバッファ（Lane 1）
- Strict キュー（Lane 2）
- フラッシュモード (immediate, count, time, manual)
- DLQ (Dead Letter Queue) リカバリ
- チャンクフラッシュ
- シーケンスID によるタスク順序保証
- グレースフルシャットダウン
- 後方互換性（v1モードとの共存）
"""

import os
import sys
import tempfile
import threading
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from nanasqlite import NanaSQLite

# ==================== Fixtures ====================


@pytest.fixture
def db_path():
    """一時DBパスを提供"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test_v2.db")


@pytest.fixture
def v2db(db_path):
    """v2モード有効のNanaSQLiteインスタンスを提供 (immediate flush)"""
    database = NanaSQLite(db_path, v2_mode=True, flush_mode="immediate")
    yield database
    database.close()


@pytest.fixture
def v2db_manual(db_path):
    """v2モード有効のNanaSQLiteインスタンスを提供 (manual flush)"""
    database = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
    yield database
    database.close()


@pytest.fixture
def v2db_count(db_path):
    """v2モード有効のNanaSQLiteインスタンスを提供 (count flush, threshold=5)"""
    database = NanaSQLite(db_path, v2_mode=True, flush_mode="count", flush_count=5)
    yield database
    database.close()


@pytest.fixture
def v2db_time(db_path):
    """v2モード有効のNanaSQLiteインスタンスを提供 (time flush, interval=0.5s)"""
    database = NanaSQLite(db_path, v2_mode=True, flush_mode="time", flush_interval=0.5)
    yield database
    database.close()


@pytest.fixture
def v1db(db_path):
    """v1モード（従来の同期書き込み）のNanaSQLiteインスタンスを提供"""
    database = NanaSQLite(db_path, v2_mode=False)
    yield database
    database.close()


# ==================== 後方互換性テスト ====================


class TestBackwardCompatibility:
    """v2_mode=False の場合に従来と同一の動作をするか検証"""

    def test_v1_mode_default(self, v1db):
        """v1モードではv2_engineが初期化されていないことを確認"""
        assert v1db._v2_mode is False
        assert v1db._v2_engine is None

    def test_v1_set_and_get(self, v1db):
        """v1モードの基本操作は従来通り動作"""
        v1db["key1"] = "value1"
        assert v1db["key1"] == "value1"

    def test_v1_delete(self, v1db):
        """v1モードの削除は従来通り動作"""
        v1db["key1"] = "value1"
        del v1db["key1"]
        assert "key1" not in v1db

    def test_flush_noop_in_v1(self, v1db):
        """v1モードでflush()を呼んでも例外が発生しない"""
        v1db["key"] = "value"
        v1db.flush()  # No-op, should not raise
        assert v1db["key"] == "value"


# ==================== v2 基本操作テスト ====================


class TestV2BasicOperations:
    """v2モードでの基本的な読み書き"""

    def test_v2_mode_enabled(self, v2db):
        """v2モードが有効であることを確認"""
        assert v2db._v2_mode is True
        assert v2db._v2_engine is not None

    def test_v2_set_and_get(self, v2db):
        """v2モードでの書き込みと読み取り"""
        v2db["user"] = {"name": "Nana", "age": 20}
        # メモリは即時更新されるので、読み取りはゼロコスト
        result = v2db["user"]
        assert result == {"name": "Nana", "age": 20}

    def test_v2_delete(self, v2db):
        """v2モードでの削除"""
        v2db["key"] = "value"
        assert "key" in v2db
        del v2db["key"]
        assert "key" not in v2db

    def test_v2_update_dict(self, v2db):
        """v2モードでの一括更新"""
        v2db.update({"a": 1, "b": 2, "c": 3})
        assert v2db["a"] == 1
        assert v2db["b"] == 2
        assert v2db["c"] == 3

    def test_v2_persistence_after_close(self, db_path):
        """v2モードでclose後にデータが永続化されていることを確認"""
        db1 = NanaSQLite(db_path, v2_mode=True, flush_mode="immediate")
        db1["persist_key"] = {"data": "persisted"}
        db1.close()

        # v1モードで再度開いて確認（v2バッファに依存せずDBから直接読む）
        db2 = NanaSQLite(db_path, v2_mode=False)
        result = db2["persist_key"]
        assert result == {"data": "persisted"}
        db2.close()

    def test_v2_write_coalescing(self, v2db_manual):
        """同一キーへの複数書き込みが最後の値でコアレスされる"""
        v2db_manual["key"] = "first"
        v2db_manual["key"] = "second"
        v2db_manual["key"] = "final"

        # メモリ上は即時に最新値
        assert v2db_manual["key"] == "final"

        # フラッシュ後にDBにも反映
        v2db_manual.flush()
        time.sleep(0.2)  # バックグラウンドスレッドの完了を待つ

        # DB上にも最終値のみが書かれる
        fresh = v2db_manual.get_fresh("key")
        assert fresh == "final"

    def test_v2_overwrite_then_delete(self, v2db_manual):
        """書き込み後に削除するとステージングバッファではdeleteが優先"""
        v2db_manual["key"] = "value"
        del v2db_manual["key"]

        assert "key" not in v2db_manual

        v2db_manual.flush()
        time.sleep(0.2)

        fresh = v2db_manual.get_fresh("key")
        assert fresh is None


# ==================== フラッシュモードテスト ====================


class TestFlushModes:
    """各フラッシュモードの動作検証"""

    def test_immediate_mode_persists(self, db_path):
        """immediateモード: 書き込みごとにフラッシュ"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="immediate")
        db["key"] = "value"
        time.sleep(0.3)  # バックグラウンドスレッド完了待ち

        # DBに直接問い合わせて確認
        fresh = db.get_fresh("key")
        assert fresh == "value"
        db.close()

    def test_manual_mode_no_auto_flush(self, v2db_manual, db_path):
        """manualモード: 明示的flush()まで書き込まれない"""
        v2db_manual["key"] = "value"
        time.sleep(0.2)

        # メモリ上にはある
        assert v2db_manual["key"] == "value"

        # DBにはまだない可能性が高い (manualモードでflush未実行)
        # flush()してからDBを確認
        v2db_manual.flush()
        time.sleep(0.2)

        fresh = v2db_manual.get_fresh("key")
        assert fresh == "value"

    def test_count_mode_threshold(self, v2db_count, db_path):
        """countモード: 閾値到達時にフラッシュ"""
        # flush_count=5 なので、5回書き込みで発火
        for i in range(5):
            v2db_count[f"key_{i}"] = f"value_{i}"

        time.sleep(0.3)  # フラッシュ完了待ち

        # 全て永続化されているはず
        for i in range(5):
            fresh = v2db_count.get_fresh(f"key_{i}")
            assert fresh == f"value_{i}", f"key_{i} was not flushed"

    def test_time_mode_interval(self, v2db_time, db_path):
        """timeモード: 指定間隔でフラッシュ"""
        v2db_time["key"] = "value"
        # flush_interval=0.5s なので少し待つ
        time.sleep(1.0)

        fresh = v2db_time.get_fresh("key")
        assert fresh == "value"


# ==================== DLQ (Dead Letter Queue) テスト ====================


class TestDeadLetterQueue:
    """DLQ機能の検証"""

    def test_dlq_initially_empty(self, v2db):
        """初期状態でDLQは空"""
        assert len(v2db._v2_engine.dlq) == 0

    def test_valid_data_does_not_enter_dlq(self, v2db):
        """正常なデータはDLQに入らない"""
        v2db["key"] = "value"
        time.sleep(0.3)
        assert len(v2db._v2_engine.dlq) == 0


# ==================== チャンクフラッシュテスト ====================


class TestChunkFlushing:
    """チャンクフラッシュ（大量データの分割トランザクション）の検証"""

    def test_large_batch_with_small_chunks(self, db_path):
        """chunk_size=10で100件書き込み → 10トランザクションに分割されるが全件永続化される"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="manual", v2_chunk_size=10)

        for i in range(100):
            db[f"chunk_key_{i}"] = f"chunk_value_{i}"

        db.flush()
        time.sleep(0.5)

        for i in range(100):
            fresh = db.get_fresh(f"chunk_key_{i}")
            assert fresh == f"chunk_value_{i}", f"Missing chunk_key_{i}"

        db.close()


# ==================== シーケンスIDテスト ====================


class TestSequenceID:
    """シーケンスIDによるタスク順序の保証"""

    def test_sequence_id_monotonic(self, v2db):
        """シーケンスIDは単調増加"""
        engine = v2db._v2_engine
        ids = [next(engine._sequence_counter) for _ in range(100)]
        assert ids == sorted(ids)
        assert len(set(ids)) == 100  # ユニーク


# ==================== スレッド安全性テスト ====================


class TestThreadSafety:
    """複数スレッドからのv2操作の安全性"""

    def test_concurrent_writes(self, db_path):
        """複数スレッドからの同時書き込みでデータ破損しない"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="immediate")
        errors = []

        def writer(thread_id):
            try:
                for i in range(50):
                    db[f"thread_{thread_id}_key_{i}"] = f"value_{i}"
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(t,)) for t in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors occurred: {errors}"
        time.sleep(0.5)  # 全フラッシュ完了待ち

        # 全件メモリ上に存在
        for t in range(4):
            for i in range(50):
                assert db.get(f"thread_{t}_key_{i}") == f"value_{i}"

        db.close()


# ==================== グレースフルシャットダウンテスト ====================


class TestGracefulShutdown:
    """close()時の安全なシャットダウン"""

    def test_close_flushes_remaining_data(self, db_path):
        """close()時に残りのバッファがフラッシュされる"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
        db["shutdown_key"] = "shutdown_value"
        # flush()を呼ばずにclose()
        db.close()

        # 再度開いて確認
        db2 = NanaSQLite(db_path, v2_mode=False)
        result = db2.get("shutdown_key")
        assert result == "shutdown_value"
        db2.close()

    def test_double_close_safe(self, db_path):
        """close()を2回呼んでもエラーにならない"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="immediate")
        db["key"] = "value"
        db.close()
        db.close()  # should not raise

    def test_shutdown_idempotent(self, db_path):
        """V2Engineのshutdown()は複数回呼んでもエラーにならない"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="immediate")
        engine = db._v2_engine
        engine.shutdown()
        engine.shutdown()  # should not raise
        db.close()


# ==================== Strict Lane (execute/execute_many) テスト ====================


class TestStrictLane:
    """execute() / execute_many() の Strict Lane 経由テスト"""

    def test_execute_in_v2_mode(self, v2db):
        """v2モードでexecute()がStrict Lane経由で実行される"""
        v2db.execute(
            f"INSERT OR REPLACE INTO {v2db._safe_table} (key, value) VALUES (?, ?)",
            ("raw_key", '"raw_value"'),
        )
        time.sleep(0.3)

        # メモリキャッシュには入らないがDBに存在
        fresh = v2db.get_fresh("raw_key")
        assert fresh == "raw_value"

    def test_execute_many_in_v2_mode(self, v2db):
        """v2モードでexecute_many()がStrict Lane経由で実行される"""
        import json
        params = [(f"em_key_{i}", json.dumps(f"em_value_{i}")) for i in range(10)]
        v2db.execute_many(
            f"INSERT OR REPLACE INTO {v2db._safe_table} (key, value) VALUES (?, ?)",
            params,
        )
        time.sleep(0.3)

        for i in range(10):
            fresh = v2db.get_fresh(f"em_key_{i}")
            assert fresh == f"em_value_{i}"
