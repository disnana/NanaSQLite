"""
BUG-03 [High] No nonce length check before AEAD decrypt

12バイト未満のデータで復号しようとすると暗号ライブラリの
低レベル例外がそのまま送出されていた。
修正後: NanaSQLiteDatabaseError("Corrupted encrypted data") が発生する。
"""

import os
import sqlite3
import tempfile

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from nanasqlite import NanaSQLite
from nanasqlite.exceptions import NanaSQLiteDatabaseError

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

key = AESGCM.generate_key(bit_length=256)

# Write short (< 13 bytes) binary data directly to DB
conn = sqlite3.connect(path)
conn.execute("CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value BLOB)")
conn.execute("INSERT INTO data (key, value) VALUES (?, ?)", ("test", b"\x00" * 5))
conn.commit()
conn.close()

db = NanaSQLite(path, encryption_key=key)
try:
    _ = db["test"]
    print("BUG: No error raised for short encrypted data!")
except NanaSQLiteDatabaseError as e:
    if "too short" in str(e):
        print(f"PASS: NanaSQLiteDatabaseError raised: {e}")
    else:
        print(f"PARTIAL: NanaSQLiteDatabaseError but unexpected message: {e}")
except Exception as e:
    print(f"BUG: Wrong exception type: {type(e).__name__}: {e}")
finally:
    db.close()
    os.unlink(path)
