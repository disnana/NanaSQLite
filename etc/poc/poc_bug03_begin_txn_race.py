"""
BUG-03 [High] begin_transaction: _in_transaction フラグをロック外で更新する競合状態

問題: BEGIN IMMEDIATE 成功後、_in_transaction = True をロック解放後に設定するため、
     マルチスレッド環境で 2 スレッドが同時に begin_transaction() を呼ぶと
     Python レベルのチェックをすり抜け、SQLite レベルのエラーが発生する可能性がある。
修正後: _in_transaction = True を with self._acquire_lock() ブロック内で設定する。
"""

import os
import tempfile
import threading

from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    db = NanaSQLite(path)

    errors = []
    success_count = [0]

    def try_begin():
        try:
            db.begin_transaction()
            success_count[0] += 1
        except NanaSQLiteTransactionError:
            pass  # 正常: 2 つ目のトランザクションは拒否されるべき
        except Exception as e:
            errors.append(str(e))

    t1 = threading.Thread(target=try_begin)
    t2 = threading.Thread(target=try_begin)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # どちらかが成功しているはず
    if success_count[0] == 1:
        db.rollback()

    if errors:
        print(f"BUG: 予期しないエラーが発生: {errors}")
    else:
        print("PASS: トランザクション競合が正しく処理された")

    db.close()
finally:
    os.unlink(path)
