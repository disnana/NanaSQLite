"""
BUG-01 [Critical] items() missing _check_connection()

items() を閉じたインスタンスで呼ぶと NanaSQLiteClosedError ではなく
APSW の低レベル例外が漏洩する。
修正後: NanaSQLiteClosedError が発生する。
"""

import os
import tempfile

from nanasqlite import NanaSQLite
from nanasqlite.exceptions import NanaSQLiteClosedError

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

db = NanaSQLite(path)
db["key1"] = "value1"
db.close()

try:
    db.items()
    print("BUG: No error raised on closed instance!")
except NanaSQLiteClosedError:
    print("PASS: NanaSQLiteClosedError raised correctly.")
except Exception as e:
    print(f"BUG: Wrong exception type: {type(e).__name__}: {e}")
finally:
    os.unlink(path)
