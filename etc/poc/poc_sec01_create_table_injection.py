"""
SEC-01 [Critical] create_table() カラム型に対するSQLインジェクション

create_table() の columns dict の値（カラム型）にバリデーションがなく、
セミコロンを含む文字列で任意のSQLを実行可能。
修正後: NanaSQLiteValidationError が発生し、インジェクションが防止される。
"""

import os
import tempfile

from nanasqlite import NanaSQLite
from nanasqlite.exceptions import NanaSQLiteValidationError

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    db = NanaSQLite(path)
    db.create_table("victim", {"id": "INTEGER", "name": "TEXT"})
    db.sql_insert("victim", {"id": 1, "name": "Alice"})

    # Attempt SQL injection through column type
    try:
        db.create_table("evil", {
            "id": 'INTEGER); DELETE FROM "victim" WHERE 1=1; --'
        })
        # If we get here, the injection was not blocked
        rows = db.query("victim")
        if len(rows) == 0:
            print("BUG: SQL injection succeeded - data deleted")
        else:
            print("BUG: Injection not blocked but data survived (APSW behavior)")
    except (NanaSQLiteValidationError, ValueError):
        # Verify data is preserved
        rows = db.query("victim")
        if len(rows) == 1:
            print("PASS: Injection blocked, data preserved")
        else:
            print(f"BUG: Injection blocked but data inconsistent: {rows}")
    except Exception as e:
        print(f"BUG: Unexpected exception: {type(e).__name__}: {e}")

    db.close()
finally:
    os.unlink(path)
