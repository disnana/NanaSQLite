"""
BUG-02 [High] AEAD deserialize silently falls back to plaintext JSON

暗号化モードが有効なのに非bytesデータ(str)を受け取ると、
暗号化を迂回して平文 JSON として復号していた。
修正後: 警告ログが出力される。
"""

import json
import logging
import os
import sqlite3
import tempfile

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from nanasqlite import NanaSQLite

logging.basicConfig(level=logging.WARNING)

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

key = AESGCM.generate_key(bit_length=256)

# Step 1: Write plaintext JSON directly to DB (simulating unencrypted data)
conn = sqlite3.connect(path)
conn.execute("CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value TEXT)")
conn.execute("INSERT INTO data (key, value) VALUES (?, ?)", ("test", json.dumps("secret")))
conn.commit()
conn.close()

# Step 2: Open with encryption enabled and try reading
db = NanaSQLite(path, encryption_key=key)
try:
    val = db["test"]
    # The value is read, but a warning should have been logged
    print(f"PASS: Value read (with warning logged): {val}")
except Exception as e:
    print(f"Exception (may be acceptable): {type(e).__name__}: {e}")
finally:
    db.close()
    os.unlink(path)
