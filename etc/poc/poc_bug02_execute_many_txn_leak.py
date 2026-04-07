"""
BUG-02 [High] execute_many: 非 apsw.Error 例外でトランザクションがリークする

問題: execute_many の非 v2 パスで `except apsw.Error:` のみを補足するため、
     TypeError 等の非 apsw 例外が発生した場合 ROLLBACK が実行されず、
     BEGIN IMMEDIATE が残ったまま後続の書き込みがすべてブロックされる。
修正後: `except Exception:` に変更し、あらゆる例外で ROLLBACK を保証する。
"""

import os
import tempfile

from nanasqlite import NanaSQLite

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    db = NanaSQLite(path)
    db["seed"] = "ok"

    # executemany に不正なパラメータを渡して TypeError を誘発する
    try:
        db.execute_many(
            "INSERT OR REPLACE INTO data(key, value) VALUES (?, ?)",
            [("k1", "v1"), object()],  # object() は展開できず TypeError
        )
    except Exception:
        pass  # 例外は想定内

    # 修正後: トランザクションがリークしていなければ書き込みが成功する
    try:
        db["after"] = "still_works"
        val = db["after"]
        assert val == "still_works", f"Expected 'still_works', got {val!r}"
        print("PASS: トランザクションリークなし - 書き込み成功")
    except Exception as e:
        print(f"BUG: トランザクションがリーク - 後続書き込みが失敗: {e}")

    db.close()
finally:
    os.unlink(path)
