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
    d["key"] = "v2" # リセット

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
    # 内部的に _scheduler_running が False になる
    assert not d._scheduler_running

def test_expiring_dict_pop():
    """pop() で削除された場合に期限切れコールバックが呼ばれないこと"""
    expired = []
    d = ExpiringDict(expiration_time=0.1, mode=ExpirationMode.SCHEDULER, on_expire=lambda k,v: expired.append(k))
    d["a"] = 1
    val = d.pop("a")
    assert val == 1
    time.sleep(0.2)
    assert len(expired) == 0
    d.clear()
