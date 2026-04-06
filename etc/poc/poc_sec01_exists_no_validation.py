"""
SEC-01 [Medium] exists() の where 句が _validate_expression() を経由しない

問題: forbidden_sql_functions=['UPPER'] のインスタンスで query() は WHERE 句を
     _validate_expression() で検証して禁止関数を含む WHERE を拒否するが、
     exists() はこの検証をスキップするため一貫性がない。
     ユーザーが where 引数を制御できる状況では、アプリケーションが想定する
     関数制限ポリシーをバイパスされる恐れがある。

修正後: exists() でも _validate_expression() が実行され、
        forbidden_sql_functions の設定が一貫して適用される。
"""

import os
import tempfile
from nanasqlite import NanaSQLite
from nanasqlite.exceptions import NanaSQLiteValidationError

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    with NanaSQLite(path, strict_sql_validation=True, forbidden_sql_functions=["UPPER"]) as db:
        db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
        db.sql_insert("users", {"id": 1, "name": "Alice"})

        # 正常な where 句は通る
        assert db.exists("users", "id = ?", (1,)) is True, "正常な exists() は True を返すべき"

        # query() は forbidden 関数を含む where 句を拒否する
        try:
            db.query("users", where="UPPER(name) = ?", parameters=("ALICE",))
            query_rejected = False
        except NanaSQLiteValidationError:
            query_rejected = True

        # exists() も同様に拒否されるべき
        try:
            db.exists("users", "UPPER(name) = ?", ("ALICE",))
            exists_rejected = False
        except NanaSQLiteValidationError:
            exists_rejected = True

        if query_rejected and exists_rejected:
            print("PASS: exists() が forbidden_sql_functions 設定を正しく適用する")
        elif query_rejected and not exists_rejected:
            print("BUG: query() は forbidden 関数を拒否するが exists() は通してしまう（不整合）")
        else:
            print(f"INFO: query_rejected={query_rejected}, exists_rejected={exists_rejected}")

except Exception as e:
    print(f"BUG: 予期しない例外が発生: {type(e).__name__}: {e}")
finally:
    try:
        os.unlink(path)
    except OSError:
        pass
    for suffix in ("-wal", "-shm", "-journal"):
        try:
            os.unlink(path + suffix)
        except OSError:
            pass
