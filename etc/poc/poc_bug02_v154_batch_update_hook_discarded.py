"""
BUG-02 [Medium] batch_update() の non-coerce パスでフック返り値が破棄される

現行: coerce=False の場合、batch_update() では before_write フックの返り値が無視される。
修正後: coerce フラグに関わらずフック返り値は常に使用される。
"""

import os
import tempfile
from nanasqlite import NanaSQLite
from nanasqlite.hooks import BaseHook


class UpperCaseHook(BaseHook):
    """before_write で文字列値を大文字に変換するフック（変換フックの例）"""

    def before_write(self, db, key, value):
        if isinstance(value, str):
            return value.upper()
        return value


fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)
try:
    db = NanaSQLite(path)
    hook = UpperCaseHook()
    db.add_hook(hook)

    # batch_update でフック変換が適用されるか確認
    db.batch_update({"greeting": "hello", "name": "world"})

    greeting = db["greeting"]
    name = db["name"]

    if greeting == "HELLO" and name == "WORLD":
        print("PASS: batch_update() でフック変換が正しく適用された")
    else:
        print(f"BUG: batch_update() でフック変換が無視された: greeting={greeting!r}, name={name!r}")
        print("  期待値: greeting='HELLO', name='WORLD'")

    db.close()
finally:
    os.unlink(path)
