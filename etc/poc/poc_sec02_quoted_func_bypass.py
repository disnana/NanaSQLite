"""
SEC-02 [High] _validate_expression() misses double-quoted identifiers

旧実装の正規表現は "DANGEROUS_FUNC"( のようなクォート付き関数名を
検出できなかった。
修正後: クォート付き識別子も検出・禁止される。
"""

import os
import tempfile

from nanasqlite import NanaSQLite
from nanasqlite.exceptions import NanaSQLiteValidationError

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

# forbidden_sql_functions に DANGEROUS を追加し strict モードで検証
db = NanaSQLite(
    path,
    strict_sql_validation=True,
    forbidden_sql_functions=["DANGEROUS"],
)
db.create_table("users", {"id": "INTEGER", "name": "TEXT"})
db.sql_insert("users", {"id": 1, "name": "Alice"})

# Unquoted version should be caught (baseline)
try:
    db.query("users", where="DANGEROUS(1)")
    print("BUG: Unquoted forbidden function not blocked!")
except (NanaSQLiteValidationError, ValueError):
    print("PASS (baseline): Unquoted function blocked.")

# Double-quoted version: this was the bypass
try:
    db.query("users", where='"DANGEROUS"(1)')
    print("BUG: Double-quoted function bypass not detected!")
except (NanaSQLiteValidationError, ValueError):
    print("PASS: Double-quoted function detected and blocked.")
except Exception as e:
    print(f"Other exception: {type(e).__name__}: {e}")
finally:
    db.close()
    os.unlink(path)
