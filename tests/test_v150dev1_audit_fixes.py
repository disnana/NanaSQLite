"""
NanaSQLite v1.5.0dev1 - 監査修正の回帰テスト

BUG-01: batch_update / batch_delete が v2 モードをバイパスして
        直接 DB に書き込んでいたため、staging buffer と競合していた。

BUG-02: clear() / load_all() が flush() の完了を wait しなかったため、
        バックグラウンドフラッシュがデータを「巻き戻し」する可能性があった。
"""

import os
import sys
import tempfile
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from nanasqlite import NanaSQLite


# ====================================================================
# Fixtures
# ====================================================================


@pytest.fixture
def db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test_audit.db")


@pytest.fixture
def v2db_manual(db_path):
    db = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
    yield db
    db.close()


@pytest.fixture
def v2db_immediate(db_path):
    db = NanaSQLite(db_path, v2_mode=True, flush_mode="immediate")
    yield db
    db.close()


# ====================================================================
# BUG-01: batch_update / batch_delete の V2 ルーティング
# ====================================================================


class TestBug01BatchV2Routing:
    """BUG-01: batch_update / batch_delete が v2 バッファを経由するか検証"""

    def test_batch_update_v2_mode_does_not_override_staging(self, db_path):
        """
        batch_update 後に v2 staging に入っていた同一キーの値に
        フラッシュによって上書きされないことを検証。

        修正前: batch_update は直接 DB 書き込み → flush 時にキューの古い値が DB を上書き
        修正後: batch_update も v2 バッファ経由 → FIFO 順で正しく処理される
        """
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
        try:
            # 1. KVS で "staging_value" をバッファに入れる
            db["conflict_key"] = "staging_value"

            # 2. batch_update で "batch_value" を書き込む
            db.batch_update({"conflict_key": "batch_value"})

            # batch_update 後, メモリは "batch_value"
            assert db["conflict_key"] == "batch_value"

            # 3. flush + 完了待ち
            db.flush(wait=True)

            # 4. DB から直接確認 (cache bypass)
            db.clear_cache()
            actual = db.get_fresh("conflict_key")

            # 修正済み: batch_value が最後に書かれた値として永続化されること
            assert actual == "batch_value", (
                f"Expected 'batch_value' but got '{actual}'. "
                "Possible ghost re-insert from old staging buffer."
            )
        finally:
            db.close()

    def test_batch_update_persists_all_keys_in_v2_mode(self, db_path):
        """v2 モードで batch_update した全キーが flush 後にDBに永続化されること"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
        try:
            mapping = {f"bu_key_{i}": f"bu_value_{i}" for i in range(20)}
            db.batch_update(mapping)
            db.flush(wait=True)
            db.clear_cache()

            for k, v in mapping.items():
                assert db.get_fresh(k) == v, f"Key {k!r} was not persisted after batch_update in v2 mode"
        finally:
            db.close()

    def test_batch_update_partial_persists_accepted_keys(self, db_path):
        """batch_update_partial で受理されたキーが flush 後に永続化されること"""
        from nanasqlite.hooks import CheckHook

        db = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
        try:
            # int のみ受付するフックを追加
            # CheckHook(check_func, error_msg) の順
            db.add_hook(CheckHook(lambda _k, v: isinstance(v, int), "int only allowed"))

            failed = db.batch_update_partial({"ok_key": 42, "bad_key": "not_an_int"})

            assert "bad_key" in failed
            assert "ok_key" not in failed

            db.flush(wait=True)
            db.clear_cache()

            assert db.get_fresh("ok_key") == 42
            assert db.get_fresh("bad_key") is None
        finally:
            db.close()

    def test_batch_delete_v2_mode_removes_keys(self, db_path):
        """v2 モードで batch_delete した後、flush で全キーが削除されること"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
        try:
            keys = [f"del_key_{i}" for i in range(10)]
            for k in keys:
                db[k] = "to_be_deleted"

            db.flush(wait=True)

            # バッチ削除
            db.batch_delete(keys)
            db.flush(wait=True)
            db.clear_cache()

            for k in keys:
                assert db.get_fresh(k) is None, f"{k!r} was not deleted in v2 mode"
        finally:
            db.close()

    def test_batch_delete_v2_does_not_bypass_hooks(self, db_path):
        """v2 モードの batch_delete でも before_delete フックが実行されること"""
        from nanasqlite.protocols import NanaHook

        class DeleteRecorder(NanaHook):
            def __init__(self):
                self.deleted = []

            def before_write(self, db, key, value):
                return value

            def after_read(self, db, key, value):
                return value

            def before_delete(self, db, key):
                self.deleted.append(key)

        db = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
        recorder = DeleteRecorder()
        db.add_hook(recorder)

        try:
            for k in ["k1", "k2", "k3"]:
                db[k] = "val"
            db.flush(wait=True)

            db.batch_delete(["k1", "k2"])
            assert set(recorder.deleted) >= {"k1", "k2"}
        finally:
            db.close()

    def test_flush_wait_true_blocks_until_done(self, v2db_manual):
        """flush(wait=True) が完了するまでブロックすること"""
        v2db_manual["key"] = "value"
        # wait=True なら sleep 無しで完了していること
        v2db_manual.flush(wait=True)
        actual = v2db_manual.get_fresh("key")
        assert actual == "value"


# ====================================================================
# BUG-02: clear() / load_all() の同期的フラッシュ
# ====================================================================


class TestBug02ClearAndLoadAllSync:
    """BUG-02: clear() と load_all() が flush 完了を待つか検証"""

    def test_clear_does_not_allow_ghost_reinsert(self, db_path):
        """
        clear() 後にバックグラウンドフラッシュがデータを再挿入しないことを検証。

        修正前: clear() が flush() を非同期で呼ぶだけなので、
                DELETE 後にフラッシュがデータを書き込む「幽霊再挿入」が起きた。
        修正後: clear() は flush(wait=True) を呼び、全フラッシュ完了後に DELETE する。
        """

        def slow_flush(original_chunk_fn):
            def wrapper(chunk):
                time.sleep(0.3)  # フラッシュを意図的に遅延
                original_chunk_fn(chunk)
            return wrapper

        db = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
        try:
            original_fn = db._v2_engine._process_kvs_chunk
            db._v2_engine._process_kvs_chunk = slow_flush(original_fn)

            db["ghost_key"] = "ghost_value"

            # clear() はフラッシュ完了まで待機してから全削除するはず
            db.clear()

            # DB から直接確認 (内部で load_all もしない)
            with db._acquire_lock():
                cursor = db._connection.execute(
                    f"SELECT COUNT(*) FROM {db._safe_table}"
                )
                count = cursor.fetchone()[0]

            assert count == 0, (
                f"clear() left {count} row(s) in DB. "
                "Ghost re-insert from async flush was not prevented."
            )
        finally:
            db.close()

    def test_load_all_reflects_latest_data(self, db_path):
        """
        load_all() が flush 完了後の最新データを読み込むことを検証。

        修正前: load_all() が flush() を非同期で呼ぶだけなので、
                古い DB 状態をキャッシュに展開する可能性があった。
        修正後: load_all() は flush(wait=True) を呼んでから DB を読む。
        """
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
        try:
            # バッファにデータ投入
            for i in range(10):
                db[f"load_key_{i}"] = f"load_value_{i}"

            # キャッシュをクリアして load_all を呼ぶ
            # (修正後は flush 完了後にロードされるので全件取得できるはず)
            db.clear_cache()
            db.load_all()

            for i in range(10):
                assert db.get(f"load_key_{i}") == f"load_value_{i}", (
                    f"load_key_{i} was missing after load_all(). "
                    "Possible stale DB read before flush completed."
                )
        finally:
            db.close()

    def test_clear_then_set_persists_correctly(self, db_path):
        """clear() 後に新しいデータを書いても正しく永続化されること"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
        try:
            db["old_key"] = "old_value"
            db.flush(wait=True)

            db.clear()
            db["new_key"] = "new_value"
            db.flush(wait=True)
            db.clear_cache()

            assert db.get_fresh("old_key") is None
            assert db.get_fresh("new_key") == "new_value"
        finally:
            db.close()


# ====================================================================
# flush(wait=True) API
# ====================================================================


class TestFlushWaitAPI:
    """flush(wait=True) 公開 API のスモークテスト"""

    def test_flush_wait_false_is_default(self, v2db_immediate):
        """flush() は wait=False がデフォルト → 従来互換"""
        v2db_immediate["k"] = "v"
        v2db_immediate.flush()  # 引数なしでもエラーにならない

    def test_flush_wait_true_synchronous(self, db_path):
        """flush(wait=True) 後はSleep なしでもDBに値が存在する"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
        try:
            db["sync_key"] = "sync_value"
            db.flush(wait=True)
            # sleep なしで即時確認
            val = db.get_fresh("sync_key")
            assert val == "sync_value"
        finally:
            db.close()

    def test_flush_wait_true_noop_in_v1_mode(self, db_path):
        """v1 モードで flush(wait=True) を呼んでも例外にならない"""
        db = NanaSQLite(db_path, v2_mode=False)
        try:
            db["k"] = "v"
            db.flush(wait=True)  # no-op, should not raise
            assert db["k"] == "v"
        finally:
            db.close()
