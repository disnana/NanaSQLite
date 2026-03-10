"""
SEC-01 [High] alter_table_add_column() column_type bypass

旧実装のブラックリスト方式では開き括弧 '(' 等が未チェックのため
制約注入（TEXT CHECK(1=1)）が可能だった。
修正後: ホワイトリスト正規表現により拒否される。
"""

import os
import tempfile

from nanasqlite import NanaSQLite

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

db = NanaSQLite(path)
db.create_table("target", {"id": "INTEGER", "name": "TEXT"})

injection_payloads = [
    "TEXT CHECK(1=1)",          # constraint injection via '('
    "TEXT; DROP TABLE target",  # semicolon injection
    "TEXT\x00DROP",             # null byte truncation
    "TEXT'--",                  # quote + comment
]

blocked = 0
for payload in injection_payloads:
    try:
        db.alter_table_add_column("target", f"col_{blocked}", payload)
        print(f"BUG: Payload not blocked: {payload!r}")
    except (ValueError, Exception):
        blocked += 1

if blocked == len(injection_payloads):
    print(f"PASS: All {blocked} injection payloads blocked.")
else:
    print(f"FAIL: Only {blocked}/{len(injection_payloads)} payloads blocked.")

db.close()
os.unlink(path)
