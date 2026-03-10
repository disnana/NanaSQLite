"""
BUG-09 [Medium] batch_get() drops keys with None values

db["k"] = None で格納した値が batch_get() で返されない。
修正後: None 値のキーも結果に含まれる。
"""

import os
import tempfile

from nanasqlite import NanaSQLite

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

db = NanaSQLite(path)
db["key_none"] = None
db["key_value"] = "hello"

result = db.batch_get(["key_none", "key_value", "missing"])

if "key_none" in result:
    print(f"PASS: key_none included in batch_get result: {result}")
else:
    print(f"BUG: key_none missing from batch_get result: {result}")

db.close()
os.unlink(path)
