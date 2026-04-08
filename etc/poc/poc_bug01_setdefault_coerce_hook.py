"""
BUG-01 [Medium] setdefault() + before_write 変換フックが値を取り違える

PERF-18 最適化で self[key] = default の後に self[key] を再読みせず、
before_write フックによる変換を無視して元の default を after_read に渡してしまう。

修正後: before_write 変換後のキャッシュ値に対して after_read を適用して返す。
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from nanasqlite import NanaSQLite


class UpperCaseHook:
    """before_write で str 値を大文字化する変換フック (コーション相当)"""

    def before_write(self, db, key, value):
        if isinstance(value, str):
            return value.upper()
        return value

    def after_read(self, db, key, value):
        return value

    def before_delete(self, db, key):
        pass


fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    db = NanaSQLite(path)
    db.add_hook(UpperCaseHook())

    # setdefault for a new key: before_write converts "hello" → "HELLO"
    # The returned value should be "HELLO" (what was actually stored)
    result = db.setdefault("greeting", "hello")

    stored = db["greeting"]  # reads from cache/DB

    if result != "HELLO":
        print(
            f"BUG: setdefault returned '{result}' (original default) instead of "
            f"'{stored}' (before_write-transformed cached value)"
        )
    else:
        print("PASS: setdefault() correctly returns the before_write-transformed value")

    db.close()
except Exception as e:
    print(f"BUG: Unexpected error: {e}")
finally:
    os.unlink(path)
