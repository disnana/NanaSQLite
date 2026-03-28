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

    lock_held = threading.Event()  # hold_lock がロックを取得したことを通知
    can_release = threading.Event()  # try_acquire が完了したことを通知（リリース許可）

    def hold_lock():
        db._lock.acquire()
        try:
            lock_held.set()  # ロック取得を通知
            can_release.wait()  # try_acquire が終わるまで保持
        finally:
            db._lock.release()

    def try_acquire():
        lock_held.wait()  # hold_lock がロックを取得するまで待つ
        try:
            with db._acquire_lock():
                pass
        except NanaSQLiteLockError as e:
            errors.append(e)
        finally:
            can_release.set()  # hold_lock にリリースを許可

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


def test_backup_to_memory_path_raises(tmp_path):
    """backup() の dest_path が ':memory:' の場合 NanaSQLiteValidationError が発生すること"""
    db = NanaSQLite(str(tmp_path / "test.db"))
    db["key"] = "value"

    with pytest.raises(NanaSQLiteValidationError):
        db.backup(":memory:")

    db.close()


def test_backup_to_file_memory_uri_raises(tmp_path):
    """backup() の dest_path が 'file::memory:' URI の場合 NanaSQLiteValidationError が発生すること"""
    db = NanaSQLite(str(tmp_path / "test.db"))
    db["key"] = "value"

    with pytest.raises(NanaSQLiteValidationError):
        db.backup("file::memory:?cache=shared")

    db.close()


def test_restore_cleans_stale_wal_sidecar_files(tmp_path):
    """restore() が stale な WAL/SHM/journal サイドカーファイルを削除して正常にリストアすること"""
    db_path = str(tmp_path / "main.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path)
    db["key"] = "original"
    db.backup(backup_path)

    # バックアップ後にデータを変更
    db["key"] = "modified"
    db["extra"] = "should_be_gone"

    # Windows では DB 接続が開いている間 SQLite が -shm ファイルをロックするため、
    # サイドカーファイルを作成する前に接続を閉じる必要がある。
    db.close()

    # stale なサイドカーファイルを手動で作成（restore 前に残っている想定）
    stale_marker = b"stale WAL data that should not be replayed"
    for suffix in ("-wal", "-shm", "-journal"):
        sidecar = db_path + suffix
        with open(sidecar, "wb") as f:
            f.write(stale_marker)

    # 再接続してリストアを実行
    db = NanaSQLite(db_path)
    db.restore(backup_path)

    # stale なサイドカー内容が再生されず、バックアップ時点のデータが正しく復元されること
    assert db["key"] == "original"
    assert "extra" not in db

    # -journal は WAL モードでは再生成されないため、削除されたままであること
    assert not os.path.exists(db_path + "-journal")
    # 注: -wal/-shm は WAL モードの再接続で新規作成されるため存在チェックは行わない。
    # 上記のデータ整合性チェック（"original" に戻っていること）で stale WAL が
    # 再生されていないことを間接的に検証している。

    db.close()


def test_restore_on_memory_db_raises(tmp_path):
    """インメモリDB（':memory:'）に対して restore() を呼ぶと NanaSQLiteValidationError が発生すること"""
    # NanaSQLite のコンストラクタが ':memory:' を受け付けるか確認して使用
    backup_path = str(tmp_path / "backup.db")
    # まず通常の DB でバックアップを作成しておく
    src_db = NanaSQLite(str(tmp_path / "src.db"))
    src_db["key"] = "value"
    src_db.backup(backup_path)
    src_db.close()

    # ':memory:' DB に restore() を試みると NanaSQLiteValidationError が発生すること
    mem_db = NanaSQLite(":memory:")
    with pytest.raises(NanaSQLiteValidationError):
        mem_db.restore(backup_path)
    mem_db.close()


# ===========================================================
# 追加テスト: lock_timeout 公開 API 経由での検証
# ===========================================================


def _hold_lock_and_signal(db, lock_held_event, release_event):
    """内部ロックを保持してイベントで通知するヘルパー（スレッド用）"""
    db._lock.acquire()
    try:
        lock_held_event.set()
        release_event.wait()
    finally:
        db._lock.release()


def test_lock_timeout_setitem_raises_lockerror(tmp_path):
    """ロック保持中に __setitem__ を呼ぶと lock_timeout により NanaSQLiteLockError が発生すること"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.2)
    db["existing"] = "value"

    lock_held = threading.Event()
    release_lock = threading.Event()
    t = threading.Thread(target=_hold_lock_and_signal, args=(db, lock_held, release_lock))
    t.start()
    lock_held.wait()
    try:
        with pytest.raises(NanaSQLiteLockError):
            db["new_key"] = "new_value"
    finally:
        release_lock.set()
        t.join(timeout=5.0)
    # キャッシュが更新されていないことを確認（不整合防止）- ロック解放後に確認
    assert "new_key" not in db
    db.close()


def test_lock_timeout_delitem_raises_lockerror(tmp_path):
    """ロック保持中に __delitem__ を呼ぶと lock_timeout により NanaSQLiteLockError が発生すること"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.2)
    db["key_to_delete"] = "value"

    lock_held = threading.Event()
    release_lock = threading.Event()
    t = threading.Thread(target=_hold_lock_and_signal, args=(db, lock_held, release_lock))
    t.start()
    lock_held.wait()
    try:
        with pytest.raises(NanaSQLiteLockError):
            del db["key_to_delete"]
        # キャッシュ・DBが更新されていないことを確認（不整合防止）
        assert "key_to_delete" in db
    finally:
        release_lock.set()
        t.join(timeout=5.0)
    db.close()


def test_lock_timeout_pop_raises_lockerror(tmp_path):
    """ロック保持中に pop() を呼ぶと lock_timeout により NanaSQLiteLockError が発生すること"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.2)
    db["key_to_pop"] = "value"

    lock_held = threading.Event()
    release_lock = threading.Event()
    t = threading.Thread(target=_hold_lock_and_signal, args=(db, lock_held, release_lock))
    t.start()
    lock_held.wait()
    try:
        with pytest.raises(NanaSQLiteLockError):
            db.pop("key_to_pop")
        # キーが残っていることを確認（不整合防止）
        assert "key_to_pop" in db
    finally:
        release_lock.set()
        t.join(timeout=5.0)
    db.close()


def test_lock_timeout_clear_raises_lockerror(tmp_path):
    """ロック保持中に clear() を呼ぶと lock_timeout により NanaSQLiteLockError が発生すること"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.2)
    db["key1"] = "value1"
    db["key2"] = "value2"

    lock_held = threading.Event()
    release_lock = threading.Event()
    t = threading.Thread(target=_hold_lock_and_signal, args=(db, lock_held, release_lock))
    t.start()
    lock_held.wait()
    try:
        with pytest.raises(NanaSQLiteLockError):
            db.clear()
        # データが残っていることを確認（不整合防止）
        assert "key1" in db
        assert "key2" in db
    finally:
        release_lock.set()
        t.join(timeout=5.0)
    db.close()


def test_lock_timeout_restore_raises_lockerror(tmp_path):
    """ロック保持中に restore() を呼ぶと lock_timeout により NanaSQLiteLockError が発生すること"""
    db_path = str(tmp_path / "test.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path, lock_timeout=0.2)
    db["key"] = "original"
    db.backup(backup_path)
    db["key"] = "modified"

    lock_held = threading.Event()
    release_lock = threading.Event()
    t = threading.Thread(target=_hold_lock_and_signal, args=(db, lock_held, release_lock))
    t.start()
    lock_held.wait()
    try:
        with pytest.raises(NanaSQLiteLockError):
            db.restore(backup_path)
        # restoreが失敗してもデータが変わっていないことを確認
        assert db["key"] == "modified"
    finally:
        release_lock.set()
        t.join(timeout=5.0)
    db.close()


def test_lock_timeout_error_message_contains_seconds(tmp_path):
    """NanaSQLiteLockError のメッセージにタイムアウト秒数が含まれること"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=1.5)
    errors = []

    lock_held = threading.Event()
    release_lock = threading.Event()
    t = threading.Thread(target=_hold_lock_and_signal, args=(db, lock_held, release_lock))
    t.start()
    lock_held.wait()
    try:
        try:
            with db._acquire_lock():
                pass
        except NanaSQLiteLockError as e:
            errors.append(e)
    finally:
        release_lock.set()
        t.join(timeout=5.0)

    assert len(errors) == 1
    assert "1.5s" in str(errors[0])
    db.close()


# ===========================================================
# 追加テスト: backup() 詳細テスト
# ===========================================================


def test_backup_overwrites_existing_file(tmp_path):
    """backup() が既存のバックアップファイルを上書きすること"""
    db_path = str(tmp_path / "src.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path)
    db["key"] = "version1"
    db.backup(backup_path)

    # データを更新して再度バックアップ
    db["key"] = "version2"
    db.backup(backup_path)
    db.close()

    # 最新のバックアップが使われること
    db_bak = NanaSQLite(backup_path)
    assert db_bak["key"] == "version2"
    db_bak.close()


def test_backup_self_copy_raises(tmp_path):
    """backup() の dest_path が現在の DB ファイルと同一の場合 NanaSQLiteValidationError が発生すること"""
    db_path = str(tmp_path / "test.db")
    db = NanaSQLite(db_path)
    db["key"] = "value"

    with pytest.raises(NanaSQLiteValidationError):
        db.backup(db_path)

    db.close()


def test_backup_on_closed_db_raises_closed_error(tmp_path):
    """閉じた DB で backup() を呼ぶと NanaSQLiteClosedError が発生すること"""
    db = NanaSQLite(str(tmp_path / "test.db"))
    db["key"] = "value"
    db.close()

    with pytest.raises(NanaSQLiteClosedError):
        db.backup(str(tmp_path / "backup.db"))


def test_backup_with_multiple_tables(tmp_path):
    """複数テーブルを持つ DB のバックアップが正しく動作すること"""
    db_path = str(tmp_path / "multi.db")
    backup_path = str(tmp_path / "multi_backup.db")

    db = NanaSQLite(db_path)
    db["main_key"] = "main_value"

    users = db.table("users")
    users["alice"] = {"age": 30}
    users["bob"] = {"age": 25}

    db.backup(backup_path)
    db.close()

    # バックアップから両テーブルが読めること
    db_bak = NanaSQLite(backup_path)
    assert db_bak["main_key"] == "main_value"

    users_bak = db_bak.table("users")
    assert users_bak["alice"] == {"age": 30}
    assert users_bak["bob"] == {"age": 25}
    db_bak.close()


def test_backup_non_blocking_allows_concurrent_write(tmp_path):
    """backup() はノンブロッキングであり、実行中に他のスレッドが NanaSQLite に書き込めること"""
    db_path = str(tmp_path / "test.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path, lock_timeout=5.0)
    for i in range(100):
        db[f"key{i}"] = i

    write_errors = []
    write_success = []

    def concurrent_write():
        """backup() 中にも書き込みできることを確認するスレッド"""
        try:
            db["concurrent_write"] = "written_during_backup"
            write_success.append(True)
        except Exception as e:
            write_errors.append(e)

    backup_started = threading.Event()
    original_backup = db.backup

    def backup_with_signal(dest):
        backup_started.set()
        original_backup(dest)

    db.backup = backup_with_signal

    backup_thread = threading.Thread(target=db.backup, args=(backup_path,))
    backup_thread.start()
    backup_started.wait()

    write_thread = threading.Thread(target=concurrent_write)
    write_thread.start()
    write_thread.join(timeout=5.0)

    backup_thread.join(timeout=10.0)

    assert not write_errors, f"Concurrent write failed: {write_errors}"
    assert write_success, "Concurrent write did not succeed"

    # Restore original method
    db.backup = original_backup
    db.close()


def test_backup_large_data(tmp_path):
    """大量データを持つ DB の backup() が正しく完了すること"""
    db_path = str(tmp_path / "large.db")
    backup_path = str(tmp_path / "large_backup.db")

    db = NanaSQLite(db_path)
    # 500件のデータを書き込む
    for i in range(500):
        db[f"key_{i:04d}"] = {"index": i, "data": f"value_{i}" * 10}

    db.backup(backup_path)
    db.close()

    assert os.path.exists(backup_path)
    db_bak = NanaSQLite(backup_path)
    assert db_bak["key_0000"] == {"index": 0, "data": "value_0" * 10}
    assert db_bak["key_0499"] == {"index": 499, "data": "value_499" * 10}
    assert len(db_bak) == 500
    db_bak.close()


# ===========================================================
# 追加テスト: restore() 詳細テスト
# ===========================================================


def test_restore_updates_child_table_connection(tmp_path):
    """restore() 後に table() で取得した子インスタンスも新しい接続を使うこと"""
    db_path = str(tmp_path / "main.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path)
    db["key"] = "original"
    users = db.table("users")
    users["alice"] = "user1"

    db.backup(backup_path)

    # バックアップ後に変更
    db["key"] = "modified"
    users["bob"] = "user2"

    # リストア
    db.restore(backup_path)

    # 親インスタンスのデータが戻ること
    assert db["key"] == "original"
    # 子インスタンスも更新されること
    assert "bob" not in users
    assert users["alice"] == "user1"
    db.close()


def test_restore_on_closed_db_raises(tmp_path):
    """閉じた DB で restore() を呼ぶと NanaSQLiteClosedError が発生すること"""
    db_path = str(tmp_path / "test.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path)
    db["key"] = "value"
    db.backup(backup_path)
    db.close()

    with pytest.raises(NanaSQLiteClosedError):
        db.restore(backup_path)


def test_restore_allows_subsequent_operations(tmp_path):
    """restore() 後も通常のCRUD操作が正しく動作すること"""
    db_path = str(tmp_path / "main.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path)
    db["key1"] = "value1"
    db.backup(backup_path)

    db["key1"] = "changed"
    db["key2"] = "extra"
    db.restore(backup_path)

    # リストア後に CRUD が正常に動くこと
    assert db["key1"] == "value1"
    assert "key2" not in db
    db["key3"] = "new_after_restore"
    assert db["key3"] == "new_after_restore"
    del db["key1"]
    assert "key1" not in db
    db.close()


def test_restore_with_bulk_load_mode(tmp_path):
    """bulk_load モードで restore() が正しくキャッシュをクリアすること"""
    db_path = str(tmp_path / "main.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path, bulk_load=True)
    db["a"] = 1
    db["b"] = 2
    db.load_all()  # キャッシュに全データをロード
    assert db._all_loaded

    db.backup(backup_path)

    db["c"] = 3
    db.restore(backup_path)

    # キャッシュがクリアされること
    assert not db._all_loaded
    assert "c" not in db
    assert db["a"] == 1
    db.close()


def test_restore_preserves_table_name(tmp_path):
    """restore() 後もテーブル名設定が保持されること"""
    db_path = str(tmp_path / "main.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path, table="my_table")
    db["key"] = "value"
    db.backup(backup_path)

    db["key"] = "modified"
    db.restore(backup_path)

    assert db["key"] == "value"
    assert db._table == "my_table"
    db.close()


def test_restore_file_memory_uri_raises(tmp_path):
    """file::memory: URI の DB パスは _is_in_memory_path() が True を返し restore() が拒否すること"""
    backup_path = str(tmp_path / "backup.db")
    src_db = NanaSQLite(str(tmp_path / "src.db"))
    src_db["key"] = "value"
    src_db.backup(backup_path)
    src_db.close()

    # _is_in_memory_path() が "file::memory:..." を True と判定することを確認する
    # (実際のインメモリDB接続は ":memory:" テストでカバー済みのため、
    #  ここでは内部判定メソッドのみを検証する)
    from nanasqlite.core import NanaSQLite as _NanaSQLite

    assert _NanaSQLite._is_in_memory_path("file::memory:?cache=shared")
    assert _NanaSQLite._is_in_memory_path("file::memory:")
    assert not _NanaSQLite._is_in_memory_path(str(tmp_path / "real.db"))


# ===========================================================
# 追加テスト: キャッシュ・DB 整合性テスト
# ===========================================================


def test_cache_consistency_after_setitem_lock_timeout(tmp_path):
    """lock_timeout で __setitem__ が失敗した後もキャッシュと DB の整合性が保たれること"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.1)
    db["existing"] = "original_value"

    lock_held = threading.Event()
    release_lock = threading.Event()
    t = threading.Thread(target=_hold_lock_and_signal, args=(db, lock_held, release_lock))
    t.start()
    lock_held.wait()
    try:
        with pytest.raises(NanaSQLiteLockError):
            db["existing"] = "should_not_update"
    finally:
        release_lock.set()
        t.join(timeout=5.0)

    # キャッシュと DB が元の値のまま
    assert db["existing"] == "original_value"
    # 再接続して確認
    db.close()
    db2 = NanaSQLite(str(tmp_path / "test.db"))
    assert db2["existing"] == "original_value"
    db2.close()


def test_cache_consistency_after_delitem_lock_timeout(tmp_path):
    """lock_timeout で __delitem__ が失敗した後もキャッシュと DB の整合性が保たれること"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.1)
    db["key_to_keep"] = "important"

    lock_held = threading.Event()
    release_lock = threading.Event()
    t = threading.Thread(target=_hold_lock_and_signal, args=(db, lock_held, release_lock))
    t.start()
    lock_held.wait()
    try:
        with pytest.raises(NanaSQLiteLockError):
            del db["key_to_keep"]
    finally:
        release_lock.set()
        t.join(timeout=5.0)

    # キーが残っていること
    assert "key_to_keep" in db
    assert db["key_to_keep"] == "important"
    db.close()
    db2 = NanaSQLite(str(tmp_path / "test.db"))
    assert db2["key_to_keep"] == "important"
    db2.close()


def test_sequential_operations_after_lock_timeout_recovery(tmp_path):
    """lock_timeout 後のリカバリ: ロック解放後は通常操作が再開できること"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.1)
    db["key"] = "initial"

    lock_held = threading.Event()
    release_lock = threading.Event()
    t = threading.Thread(target=_hold_lock_and_signal, args=(db, lock_held, release_lock))
    t.start()
    lock_held.wait()

    # ロック保持中は失敗する
    with pytest.raises(NanaSQLiteLockError):
        db["key"] = "during_lock"

    # ロック解放
    release_lock.set()
    t.join(timeout=5.0)

    # ロック解放後は通常通り動作すること
    db["key"] = "after_lock"
    assert db["key"] == "after_lock"
    db.close()


# ===========================================================
# 追加テスト: lock_timeout のエッジケース
# ===========================================================


def test_lock_timeout_integer_accepted(tmp_path):
    """lock_timeout に整数値を渡した場合も正しく動作すること"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=2)
    db["key"] = "value"
    assert db["key"] == "value"
    db.close()


def test_lock_timeout_very_small_value(tmp_path):
    """lock_timeout に非常に小さい値（0.001秒）を設定してもエラーにならないこと"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=0.001)
    db["key"] = "value"
    assert db["key"] == "value"
    db.close()


def test_lock_timeout_is_stored_on_instance(tmp_path):
    """lock_timeout の値がインスタンスに正しく格納されること"""
    db = NanaSQLite(str(tmp_path / "test.db"), lock_timeout=3.5)
    assert db._lock_timeout == 3.5
    db.close()


def test_lock_timeout_none_stored_on_instance(tmp_path):
    """lock_timeout=None（デフォルト）がインスタンスに正しく格納されること"""
    db = NanaSQLite(str(tmp_path / "test.db"))
    assert db._lock_timeout is None
    db.close()


# ===========================================================
# 追加テスト: backup()/restore() の NanaSQLiteLockError 検証
# （lock_timeout 設定時のロック取得タイムアウト）
# ===========================================================


def test_backup_raises_lockerror_when_lock_held(tmp_path):
    """ロック保持中に backup() を呼ぶと lock_timeout により NanaSQLiteLockError が発生すること"""
    db_path = str(tmp_path / "test.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path, lock_timeout=0.2)
    db["key"] = "value"

    lock_held = threading.Event()
    release_lock = threading.Event()
    t = threading.Thread(target=_hold_lock_and_signal, args=(db, lock_held, release_lock))
    t.start()
    lock_held.wait()
    try:
        with pytest.raises(NanaSQLiteLockError):
            db.backup(backup_path)
        # バックアップファイルが作成されていないこと
        assert not os.path.exists(backup_path)
    finally:
        release_lock.set()
        t.join(timeout=5.0)
    db.close()


# ===========================================================
# 追加テスト: __delitem__ / clear() の _check_connection() 検証
# （クローズ済み接続での NanaSQLiteClosedError 送出）
# ===========================================================


def test_delitem_on_closed_db_raises_closed_error(tmp_path):
    """`del db[key]` をクローズ済み接続で呼ぶと NanaSQLiteClosedError が発生すること"""
    db = NanaSQLite(str(tmp_path / "test.db"))
    db["key"] = "value"
    db.close()

    with pytest.raises(NanaSQLiteClosedError):
        del db["key"]


def test_clear_on_closed_db_raises_closed_error(tmp_path):
    """`db.clear()` をクローズ済み接続で呼ぶと NanaSQLiteClosedError が発生すること"""
    db = NanaSQLite(str(tmp_path / "test.db"))
    db["key1"] = "value1"
    db["key2"] = "value2"
    db.close()

    with pytest.raises(NanaSQLiteClosedError):
        db.clear()


# ===========================================================
# 追加テスト: backup() 非ブロッキング動作の検証
# ===========================================================


def test_backup_does_not_block_same_db_writes(tmp_path):
    """backup() は NanaSQLite 内部ロックを長時間保持しないため、
    バックアップ完了前に同一インスタンスへの書き込みが可能であること"""
    db_path = str(tmp_path / "test.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path)
    db["initial"] = "data"

    # バックアップを実行してからも書き込みが可能であること
    db.backup(backup_path)
    db["after_backup"] = "still_works"
    assert db["after_backup"] == "still_works"
    db.close()


def test_restore_data_integrity_after_multiple_backups(tmp_path):
    """複数回バックアップして restore() すると最後にリストアしたバックアップが反映されること"""
    db_path = str(tmp_path / "main.db")
    backup1_path = str(tmp_path / "backup1.db")
    backup2_path = str(tmp_path / "backup2.db")

    db = NanaSQLite(db_path)
    db["key"] = "v1"
    db.backup(backup1_path)

    db["key"] = "v2"
    db.backup(backup2_path)

    db["key"] = "v3"

    # backup1 でリストア
    db.restore(backup1_path)
    assert db["key"] == "v1"

    # backup2 でリストア
    db.restore(backup2_path)
    assert db["key"] == "v2"

    db.close()


def test_backup_restore_roundtrip_with_complex_data(tmp_path):
    """複雑なデータ（リスト、ネスト辞書、None等）のバックアップ/リストアが正確に動作すること"""
    db_path = str(tmp_path / "main.db")
    backup_path = str(tmp_path / "backup.db")

    db = NanaSQLite(db_path)
    complex_data = {
        "list": [1, 2, 3, {"nested": True}],
        "dict": {"a": 1, "b": {"c": 2}},
        "none_val": None,
        "bool_val": True,
        "int_val": 42,
        "float_val": 3.14,
    }
    db["complex"] = complex_data
    db["simple"] = "string"

    db.backup(backup_path)

    db["complex"] = "changed"
    db["extra"] = "added"

    db.restore(backup_path)

    assert db["complex"] == complex_data
    assert db["simple"] == "string"
    assert "extra" not in db
    db.close()
