"""
NanaSQLite v1.5.1 - PERF-01〜04 パフォーマンス修正の回帰テスト

PERF-01: getattr() ホットパス最適化 — フックを持つ各操作のカバレッジ確認
PERF-02: V2モード ロック競合解消 — v2 batch_update / batch_delete のカバレッジ確認
PERF-03: _update_cache のhasattr()事前計算 — _use_cache_set フラグ確認
PERF-04: _acquire_lock を @contextmanager から直接 RLock 返却に変更
"""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from nanasqlite import NanaSQLite
from nanasqlite.exceptions import NanaSQLiteLockError, NanaSQLiteValidationError
from nanasqlite.hooks import CheckHook


# ====================================================================
# Fixtures
# ====================================================================


@pytest.fixture
def db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test_perf.db")


@pytest.fixture
def db(db_path):
    inst = NanaSQLite(db_path)
    yield inst
    inst.close()


@pytest.fixture
def db_with_hook(db_path):
    """CheckHook 付き NanaSQLite インスタンス（PERF-01 フックパスのカバレッジ用）"""
    inst = NanaSQLite(db_path)
    inst.add_hook(CheckHook(lambda k, v: True))  # passthrough hook
    yield inst
    inst.close()


@pytest.fixture
def v2_db(db_path):
    inst = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
    yield inst
    inst.close()


@pytest.fixture
def v2_db_with_hook(db_path):
    """CheckHook 付き V2 NanaSQLite（PERF-02 v2 フックパスのカバレッジ用）"""
    inst = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
    inst.add_hook(CheckHook(lambda k, v: True))  # passthrough hook
    yield inst
    inst.close()


# ====================================================================
# PERF-01: フックのホットパス最適化 — コードパスカバレッジ
# ====================================================================


class TestPerf01HookHotPaths:
    """フックが登録されている場合に各操作がフック処理パスを通ることを確認する"""

    def test_setitem_with_hook_calls_before_write(self, db_with_hook):
        """__setitem__ がフック付きで before_write を呼び出す（lines 962-964）"""
        calls = []

        class RecordHook(CheckHook):
            def before_write(self, db, key, value):
                calls.append(("before_write", key, value))
                return value

        db_with_hook._hooks.clear()
        db_with_hook.add_hook(RecordHook(lambda k, v: True))

        db_with_hook["key1"] = "value1"

        assert ("before_write", "key1", "value1") in calls

    def test_delitem_with_hook_calls_before_delete(self, db_with_hook):
        """__delitem__ がフック付きで before_delete を呼び出す（lines 992-994）"""
        calls = []

        class RecordHook(CheckHook):
            def before_delete(self, db, key):
                calls.append(("before_delete", key))

        db_with_hook._hooks.clear()
        db_with_hook.add_hook(RecordHook(lambda k, v: True))

        db_with_hook["key_del"] = "val"
        del db_with_hook["key_del"]

        assert ("before_delete", "key_del") in calls

    def test_getitem_with_hook_calls_after_read(self, db_with_hook):
        """__getitem__ がフック付きで after_read を呼び出す"""
        original = "original_value"
        db_with_hook["key_read"] = original

        read_calls = []

        class RecordHook(CheckHook):
            def after_read(self, db, key, value):
                read_calls.append(("after_read", key, value))
                return value

        db_with_hook._hooks.clear()
        db_with_hook.add_hook(RecordHook(lambda k, v: True))

        result = db_with_hook["key_read"]
        assert result == original
        assert len(read_calls) == 1
        assert read_calls[0][1] == "key_read"

    def test_pop_with_hook_calls_before_delete(self, db_with_hook):
        """pop() がフック付きで before_delete を呼び出す（lines 1198-1200）"""
        calls = []

        class RecordHook(CheckHook):
            def before_delete(self, db, key):
                calls.append(("before_delete", key))

        db_with_hook._hooks.clear()
        db_with_hook.add_hook(RecordHook(lambda k, v: True))

        db_with_hook["pop_key"] = "pop_value"
        val = db_with_hook.pop("pop_key")

        assert val == "pop_value"
        assert ("before_delete", "pop_key") in calls

    def test_batch_update_with_hook(self, db_with_hook):
        """batch_update がフック付きで before_write を呼び出す"""
        calls = []

        class RecordHook(CheckHook):
            def before_write(self, db, key, value):
                calls.append(key)
                return value

        db_with_hook._hooks.clear()
        db_with_hook.add_hook(RecordHook(lambda k, v: True))

        db_with_hook.batch_update({"a": 1, "b": 2, "c": 3})

        assert set(calls) == {"a", "b", "c"}

    def test_batch_delete_with_hook_calls_before_delete(self, db_with_hook):
        """batch_delete がフック付きで before_delete を呼び出す（lines 1527-1528）"""
        for i in range(3):
            db_with_hook[f"del_k{i}"] = i

        calls = []

        class RecordHook(CheckHook):
            def before_delete(self, db, key):
                calls.append(key)

        db_with_hook._hooks.clear()
        db_with_hook.add_hook(RecordHook(lambda k, v: True))

        db_with_hook.batch_delete([f"del_k{i}" for i in range(3)])

        assert set(calls) == {"del_k0", "del_k1", "del_k2"}

    def test_check_hook_raises_on_validation_failure(self, db):
        """CheckHook が条件を満たさない値で例外を送出する（before_write ブランチ確認）"""
        db.add_hook(CheckHook(lambda k, v: isinstance(v, int), "must be int"))

        db["ok"] = 42

        with pytest.raises(NanaSQLiteValidationError, match="must be int"):
            db["fail"] = "not_an_int"


# ====================================================================
# PERF-02: V2モード ロック競合解消 — コードパスカバレッジ
# ====================================================================


class TestPerf02V2LockFreeCache:
    """V2モードで batch_update / batch_delete がロックなしでキャッシュ更新するパスを確認"""

    def test_v2_batch_update_updates_cache_without_lock(self, v2_db):
        """V2モードの batch_update がメモリキャッシュをロックなしで更新する（lines 1393-1399）"""
        mapping = {f"k{i}": i for i in range(5)}
        v2_db.batch_update(mapping)

        # v2モードでは staged_writes が即時 DB に反映されないが、
        # メモリキャッシュは即時更新されているため in-memory get は成功するはず
        for key, expected in mapping.items():
            assert v2_db.get(key) == expected

    def test_v2_batch_delete_updates_cache_without_lock(self, v2_db):
        """V2モードの batch_delete がメモリキャッシュをロックなしで更新する（lines 1534-1539）"""
        keys = [f"del{i}" for i in range(4)]
        v2_db.batch_update({k: "val" for k in keys})

        v2_db.batch_delete(keys)

        for key in keys:
            assert key not in v2_db

    def test_v2_setitem_updates_cache_without_lock(self, v2_db):
        """V2モードの __setitem__ がロックなしでキャッシュを更新する"""
        v2_db["item"] = {"data": 99}
        assert v2_db["item"] == {"data": 99}

    def test_v2_delitem_updates_cache_without_lock(self, v2_db):
        """V2モードの __delitem__ がロックなしでキャッシュを更新する"""
        v2_db["to_del"] = "value"
        assert "to_del" in v2_db
        del v2_db["to_del"]
        assert "to_del" not in v2_db

    def test_v2_batch_update_with_hook(self, v2_db_with_hook):
        """V2モードでフック付き batch_update がフックを呼び出す"""
        calls = []

        class RecordHook(CheckHook):
            def before_write(self, db, key, value):
                calls.append(key)
                return value

        v2_db_with_hook._hooks.clear()
        v2_db_with_hook.add_hook(RecordHook(lambda k, v: True))

        v2_db_with_hook.batch_update({"a": 1, "b": 2})

        assert set(calls) == {"a", "b"}

    def test_v2_batch_delete_with_hook(self, v2_db_with_hook):
        """V2モードでフック付き batch_delete がフックを呼び出す"""
        v2_db_with_hook.batch_update({"x": 1, "y": 2})

        calls = []

        class RecordHook(CheckHook):
            def before_delete(self, db, key):
                calls.append(key)

        v2_db_with_hook._hooks.clear()
        v2_db_with_hook.add_hook(RecordHook(lambda k, v: True))

        v2_db_with_hook.batch_delete(["x", "y"])

        assert set(calls) == {"x", "y"}


# ====================================================================
# PERF-03: _update_cache の hasattr() 事前計算
# ====================================================================


class TestPerf03UseCacheSetFlag:
    """_use_cache_set フラグが __init__ で正しく設定されることを確認"""

    def test_unbounded_cache_flag_false(self, db_path):
        """デフォルト（アンバウンド）モードでは _use_cache_set = False"""
        db = NanaSQLite(db_path)
        assert db._use_cache_set is False
        db.close()

    def test_lru_cache_flag_true(self, db_path):
        """LRU モードでは _use_cache_set = True"""
        db = NanaSQLite(db_path, cache_strategy="lru", cache_size=100)
        assert db._use_cache_set is True
        db.close()

    def test_ttl_cache_flag_true(self, db_path):
        """TTL モードでは _use_cache_set = True"""
        db = NanaSQLite(db_path, cache_strategy="ttl", cache_ttl=60.0)
        assert db._use_cache_set is True
        db.close()

    def test_update_cache_uses_flag(self, db):
        """_update_cache が _use_cache_set フラグに従って正しく動作する"""
        # Unbounded mode: direct dict update
        db._update_cache("k", "v")
        assert db._data.get("k") == "v"


# ====================================================================
# PERF-04: _acquire_lock を @contextmanager から直接 RLock 返却に変更
# ====================================================================


class TestPerf04AcquireLock:
    """_acquire_lock が適切なコンテキストマネージャを返すことを確認"""

    def test_no_timeout_returns_rlock(self, db):
        """lock_timeout = None のとき _acquire_lock() が RLock 自身を返す"""
        assert db._lock_timeout is None
        cm = db._acquire_lock()
        # RLock は _thread.RLock を返すファクトリ関数なので、同一オブジェクトと比較する
        assert cm is db._lock

    def test_lock_acquired_and_released(self, db):
        """_acquire_lock() が with 文で正しくロックを取得・解放する"""
        with db._acquire_lock():
            # ロック保持中: 再入可能（RLock なので自スレッドは取得できる）
            acquired = db._lock.acquire(blocking=False)
            if acquired:
                db._lock.release()
            assert acquired, "RLock は再入可能なので自スレッドは取得できるはず"

    def test_timeout_returns_timed_lock_context(self, db_path):
        """lock_timeout が設定されている場合 _TimedLockContext を返す"""
        from nanasqlite.core import _TimedLockContext

        db = NanaSQLite(db_path, lock_timeout=5.0)
        assert db._lock_timeout == 5.0
        cm = db._acquire_lock()
        assert isinstance(cm, _TimedLockContext)
        db.close()

    def test_timeout_lock_context_acquires_and_releases(self, db_path):
        """_TimedLockContext が with 文で正しくロックを取得・解放する"""
        db = NanaSQLite(db_path, lock_timeout=5.0)
        with db._acquire_lock():
            pass  # no exception = success
        db.close()

    def test_timeout_lock_raises_on_contention(self, db_path):
        """ロック競合時に NanaSQLiteLockError が送出される"""
        import threading

        db = NanaSQLite(db_path, lock_timeout=0.05)
        # 別スレッドがロックを保持
        ready = threading.Event()
        released = threading.Event()

        def hold_lock():
            db._lock.acquire()
            ready.set()
            released.wait(timeout=3)
            db._lock.release()

        t = threading.Thread(target=hold_lock, daemon=True)
        t.start()
        ready.wait(timeout=2)

        try:
            with pytest.raises(NanaSQLiteLockError):
                with db._acquire_lock():
                    pass
        finally:
            released.set()
            t.join(timeout=3)
            db.close()
