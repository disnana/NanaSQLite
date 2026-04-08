import asyncio
import time

import pytest

from nanasqlite.utils import ExpirationMode, ExpiringDict


def test_expiring_dict_lazy():
    """LAZYモード（アクセス時のみチェック）のテスト"""
    d = ExpiringDict(expiration_time=0.5, mode=ExpirationMode.LAZY)
    d["key1"] = "val1"

    assert "key1" in d
    assert d["key1"] == "val1"

    time.sleep(0.6)

    # key1 は期限切れだが、__contains__ や __getitem__ 前まで内部的には残っている可能性がある
    # ただし ExpiringDict は __contains__ や __getitem__ 内でチェックする
    assert "key1" not in d
    with pytest.raises(KeyError):
        _ = d["key1"]


def test_expiring_dict_scheduler():
    """SCHEDULERモード（バックグラウンドワーカー）のテスト"""
    expired_keys = []

    def on_expire(k, v):
        expired_keys.append(k)

    d = ExpiringDict(expiration_time=0.3, mode=ExpirationMode.SCHEDULER, on_expire=on_expire)
    d["a"] = 1
    d["b"] = 2

    assert len(d) == 2

    # 0.3秒 + 余裕を持って待機
    time.sleep(0.8)

    # ワーカーによって削除されているはず
    assert "a" not in d
    assert "b" not in d
    assert len(d) == 0
    assert "a" in expired_keys
    assert "b" in expired_keys

    d.clear()


def test_expiring_dict_timer():
    """TIMERモード（個別タイマー）のテスト"""
    # 同期的な環境でも threading.Timer を使う
    expired_keys = []

    def on_expire(k, v):
        expired_keys.append(k)

    d = ExpiringDict(expiration_time=0.2, mode=ExpirationMode.TIMER, on_expire=on_expire)
    d["x"] = 10

    assert "x" in d
    time.sleep(0.5)

    assert "x" not in d
    assert "x" in expired_keys
    d.clear()


@pytest.mark.asyncio
async def test_expiring_dict_async_timer():
    """TIMERモードでの asyncio.call_later テスト"""
    expired_keys = []

    def on_expire(k, v):
        expired_keys.append(k)

    # loop がある環境では asyncio.call_later が優先されるはず
    d = ExpiringDict(expiration_time=0.1, mode=ExpirationMode.TIMER, on_expire=on_expire)
    d["y"] = 20

    assert "y" in d
    await asyncio.sleep(0.3)

    assert "y" not in d
    assert "y" in expired_keys
    d.clear()


def test_expiring_dict_update_ttl():
    """値を更新したときに有効期限がリセットされるかテスト"""
    d = ExpiringDict(expiration_time=0.5, mode=ExpirationMode.SCHEDULER)
    d["key"] = "v1"

    time.sleep(0.3)
    d["key"] = "v2"  # リセット

    time.sleep(0.3)
    # 最初にセットしてから 0.6秒経っているが、途中で更新したのでまだ残っているはず
    assert "key" in d
    assert d["key"] == "v2"

    time.sleep(0.3)
    assert "key" not in d
    d.clear()


def test_expiring_dict_clear():
    """clear() でタイマーやワーカーが正しく処理されるかテスト"""
    d = ExpiringDict(expiration_time=1.0, mode=ExpirationMode.SCHEDULER)
    d["a"] = 1
    d.clear()
    assert len(d) == 0
    # BUG-02 fix: the scheduler is restarted after clear() so future insertions
    # are still evicted.  _scheduler_running must be True (not False) after clear().
    assert d._scheduler_running
    # Verify new items added after clear() are evicted correctly.
    d2 = ExpiringDict(expiration_time=0.2, mode=ExpirationMode.SCHEDULER)
    d2["b"] = 2
    d2.clear()
    d2["c"] = 3
    time.sleep(0.5)
    assert "c" not in d2
    d2.clear()
    d.clear()


def test_expiring_dict_pop():
    """pop() で削除された場合に期限切れコールバックが呼ばれないこと"""
    expired = []
    d = ExpiringDict(expiration_time=0.1, mode=ExpirationMode.SCHEDULER, on_expire=lambda k, v: expired.append(k))
    d["a"] = 1
    val = d.pop("a")
    assert val == 1
    time.sleep(0.2)
    assert len(expired) == 0
    d.clear()


def test_expiring_dict_timer_mode_key_update_cancels_existing_timer():
    """PERF-B coverage: updating an existing key in TIMER mode calls _cancel_timer."""
    d = ExpiringDict(expiration_time=5.0, mode=ExpirationMode.TIMER)
    d["x"] = 1
    # Overwrite the key – must cancel the existing timer (line 175 in utils.py)
    d["x"] = 2
    assert d["x"] == 2
    d.clear()


def test_expiring_dict_getitem_fires_on_expire_callback_for_expired_key():
    """BUG-04 coverage: __getitem__ on an expired key fires the on_expire callback
    and raises KeyError (lines 221 and 227-230 in utils.py)."""
    fired = []

    def callback(k, v):
        fired.append((k, v))

    d = ExpiringDict(expiration_time=0.1, mode=ExpirationMode.LAZY, on_expire=callback)
    d["k"] = "hello"
    time.sleep(0.3)
    with pytest.raises(KeyError):
        _ = d["k"]
    # Callback must have been called
    assert ("k", "hello") in fired


def test_expiring_dict_getitem_on_expire_callback_exception_is_logged():
    """BUG-04 coverage: exception from on_expire callback in __getitem__ is
    caught and logged, does not propagate (lines 228-230 in utils.py)."""

    def bad_callback(k, v):
        raise RuntimeError("callback boom")

    d = ExpiringDict(expiration_time=0.1, mode=ExpirationMode.LAZY, on_expire=bad_callback)
    d["k"] = "v"
    time.sleep(0.3)
    # Even though the callback raises, __getitem__ must still raise KeyError
    # (not RuntimeError) – the exception is swallowed/logged internally.
    with pytest.raises(KeyError):
        _ = d["k"]
