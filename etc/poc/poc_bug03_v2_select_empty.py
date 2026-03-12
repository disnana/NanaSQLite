"""
BUG-03 [Medium] v2モードで SELECT クエリが空結果を返す

修正前: v2モードでは execute() がすべてのSQLをバックグラウンドキューに送るため、
SELECT の結果が空のカーソルに置き換わる。
修正後: SELECT/PRAGMA/EXPLAIN はバックグラウンドキューをバイパスし直接実行される。
"""

import os
import tempfile

from nanasqlite import NanaSQLite

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    os.environ["NANASQLITE_SUPPRESS_MP_WARNING"] = "1"
    db = NanaSQLite(path, v2_mode=True)
    db.create_table("t", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
    db.sql_insert("t", {"id": 1, "name": "test"})
    db.flush()

    rows = db.query("t")

    if len(rows) == 0:
        print("BUG: v2 mode query returned empty result")
    elif rows[0]["name"] == "test":
        print("PASS: v2 mode query returned correct result")
    else:
        print(f"BUG: Unexpected result: {rows}")

    db.close()
finally:
    os.unlink(path)
