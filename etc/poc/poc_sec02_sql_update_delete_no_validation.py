"""
SEC-02 [Medium] sql_update() / sql_delete() の where 句が _validate_expression() を経由しない

問題: forbidden_sql_functions=['UPPER'] のインスタンスで sql_update() / sql_delete() の
     where 引数は _validate_expression() を通らないため、query() 等との一貫性がなく、
     アプリケーションの関数制限ポリシーが部分的にしか機能しない。

修正後: sql_update() / sql_delete() でも _validate_expression() が実行される。
"""

import os
import tempfile

from nanasqlite import NanaSQLite
from nanasqlite.exceptions import NanaSQLiteValidationError

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    with NanaSQLite(path, strict_sql_validation=True, forbidden_sql_functions=["UPPER"]) as db:
        db.create_table("items", {"id": "INTEGER PRIMARY KEY", "val": "TEXT"})
        db.sql_insert("items", {"id": 1, "val": "a"})

        # query() は forbidden 関数を含む where 句を拒否する
        try:
            db.query("items", where="UPPER(val) = ?", parameters=("A",))
            query_rejected = False
        except NanaSQLiteValidationError:
            query_rejected = True

        # sql_update() も同様に拒否されるべき
        try:
            db.sql_update("items", {"val": "x"}, "UPPER(val) = ?", ("A",))
            update_rejected = False
        except NanaSQLiteValidationError:
            update_rejected = True

        # sql_delete() も同様に拒否されるべき
        try:
            db.sql_delete("items", "UPPER(val) = ?", ("A",))
            delete_rejected = False
        except NanaSQLiteValidationError:
            delete_rejected = True

        if query_rejected and update_rejected and delete_rejected:
            print("PASS: sql_update()/sql_delete() が forbidden_sql_functions を正しく適用する")
        else:
            results = {
                "query_rejected": query_rejected,
                "update_rejected": update_rejected,
                "delete_rejected": delete_rejected,
            }
            not_rejected = [k for k, v in results.items() if not v]
            print(f"BUG: 以下の操作が forbidden 関数を含む where 句を通してしまう: {not_rejected}")

except Exception as e:
    print(f"BUG: 予期しない例外が発生: {type(e).__name__}: {e}")
finally:
    try:
        os.unlink(path)
    except OSError:
        pass  # file may already have been removed or never created; safe to ignore
    for suffix in ("-wal", "-shm", "-journal"):
        try:
            os.unlink(path + suffix)
        except OSError:
            pass  # WAL/SHM/journal files are optional; absence is not an error
