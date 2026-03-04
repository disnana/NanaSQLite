"""
v1.3.4b1 新機能テスト

- P2-1: lock_timeout パラメータ
- P2-3: backup / restore メソッド
"""

import os
import threading

import pytest

from nanasqlite import NanaSQLite, NanaSQLiteLockError
from nanasqlite.exceptions import (
    NanaSQLiteClosedError,
    NanaSQLiteConnectionError,
    NanaSQLiteDatabaseError,
    NanaSQLiteTransactionError,
    NanaSQLiteValidationError,
)

# ===========================================================
# P2-1: lock_timeout パラメータ
# ===========================================================


def test_lock_timeout_default_none(tmp_path):
    """lock_timeout デフォルト (None) で通常操作が問題なく動作すること"""
    db = NanaSQLite(str(tmp_path / "test.db"))
    db["key"] = "value"
    assert db["key"] == "value"
    db.close()


def test_lock_timeout_positive(tmp_path):
    """lock_timeout に正の値を設定して通常操作が問題なく動作すること"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=5.0)
    db["key"] = "value"
    assert db["key"] == "value"
    db.close()


def test_lock_timeout_raises_on_deadlock(tmp_path):
    """ロックを保持したまま別スレッドが lock_timeout 内に取得できない場合 NanaSQLiteLockError が発生すること"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.2)
    errors = []

    lock_held = threading.Event()   # hold_lock がロックを取得したことを通知
    can_release = threading.Event()  # try_acquire が完了したことを通知（リリース許可）

    def hold_lock():
        db._lock.acquire()
        lock_held.set()           # ロック取得を通知
        can_release.wait()        # try_acquire が終わるまで保持
        db._lock.release()

    def try_acquire():
        lock_held.wait()          # hold_lock がロックを取得するまで待つ
        try:
            with db._acquire_lock():
                pass
        except NanaSQLiteLockError as e:
            errors.append(e)
        finally:
            can_release.set()     # hold_lock にリリースを許可

    t1 = threading.Thread(target=hold_lock)
    t2 = threading.Thread(target=try_acquire)
    t1.start()
    t2.start()
    t2.join(timeout=5.0)
    assert not t2.is_alive(), "try_acquire thread did not finish in time"
    t1.join(timeout=5.0)
    assert not t1.is_alive(), "hold_lock thread did not finish in time"

    assert len(errors) == 1
    assert "0.2s" in str(errors[0])
    db.close()


def test_lock_timeout_negative_raises(tmp_path):
    """lock_timeout に負値を渡した場合 NanaSQLiteValidationError が発生すること"""
    with pytest.raises(NanaSQLiteValidationError):
        NanaSQLite(str(tmp_path / "test.db"), lock_timeout=-1.0)


def test_lock_timeout_zero_allowed(tmp_path):
    """lock_timeout=0.0 は即時タイムアウトとして有効な値であること"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.0)
    # ロックが競合していない場合は RLock は即座に取得できる
    db["key"] = "value"
    assert db["key"] == "value"
    db.close()


# ===========================================================
# P2-3: backup / restore メソッド
# ===========================================================


def test_backup_creates_file(tmp_path):
    """backup() がファイルを作成すること"""
    db_path = str(tmp_path / "src.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path)
    db["a"] = 1
    db["b"] = {"x": 2}
    db.backup(backup_path)

    assert os.path.exists(backup_path)
    db.close()


def test_backup_content_matches(tmp_path):
    """backup() で作成されたファイルの内容が元 DB と同じであること"""
    db_path = str(tmp_path / "src.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path)
    db["key1"] = "value1"
    db["key2"] = [1, 2, 3]
    db.backup(backup_path)
    db.close()

    # バックアップから読み込んで検証
    db_bak = NanaSQLite(backup_path)
    assert db_bak["key1"] == "value1"
    assert db_bak["key2"] == [1, 2, 3]
    db_bak.close()


def test_restore_replaces_data(tmp_path):
    """restore() 後に DB の内容がバックアップ時点に戻ること"""
    db_path = str(tmp_path / "main.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path)
    db["key1"] = "original"
    db.backup(backup_path)

    # バックアップ後にデータを変更
    db["key1"] = "modified"
    db["key2"] = "new_key"
    assert db["key1"] == "modified"

    # リストア
    db.restore(backup_path)
    assert db["key1"] == "original"
    assert "key2" not in db
    db.close()


def test_restore_clears_cache(tmp_path):
    """restore() 後にメモリキャッシュがクリアされること"""
    db_path = str(tmp_path / "main.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path, bulk_load=True)
    db["cached_key"] = "cached_value"
    db.backup(backup_path)

    db["new_key"] = "new_value"
    db.restore(backup_path)

    assert not db._all_loaded
    assert "new_key" not in db
    db.close()


def test_restore_on_child_instance_raises(tmp_path):
    """table() で取得した子インスタンスで restore() を呼ぶと NanaSQLiteConnectionError が発生すること"""
    db_path = str(tmp_path / "main.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path)
    db["key"] = "value"
    db.backup(backup_path)

    child = db.table("other")
    with pytest.raises(NanaSQLiteConnectionError):
        child.restore(backup_path)

    db.close()


def test_backup_on_closed_db_raises(tmp_path):
    """閉じた DB で backup() を呼ぶと例外が発生すること"""
    db = NanaSQLite(str(tmp_path / "test.db"))
    db["key"] = "value"
    db.close()

    with pytest.raises(NanaSQLiteClosedError):
        db.backup(str(tmp_path / "backup.db"))


def test_restore_invalid_path_raises(tmp_path):
    """存在しないパスから restore() すると NanaSQLiteDatabaseError が発生すること"""
    db = NanaSQLite(str(tmp_path / "test.db"))
    db["key"] = "value"

    with pytest.raises(NanaSQLiteDatabaseError):
        db.restore(str(tmp_path / "nonexistent.db"))

    db.close()


def test_restore_during_transaction_raises(tmp_path):
    """トランザクション中に restore() を呼ぶと NanaSQLiteTransactionError が発生すること"""
    db_path = str(tmp_path / "main.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path)
    db["key"] = "value"
    db.backup(backup_path)

    with pytest.raises(NanaSQLiteTransactionError):
        with db.transaction():
            db["key"] = "in-transaction"
            db.restore(backup_path)  # トランザクション中なので例外が発生するはず

    db.close()
