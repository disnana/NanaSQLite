"""
POC: BUG-02 — get_db_size() raises FileNotFoundError for :memory: databases

Before the patch, NanaSQLite(":memory:").get_db_size() delegates directly to
os.path.getsize(":memory:"), which raises FileNotFoundError because ":memory:"
is not a real file path — it is SQLite's sentinel for an in-memory database.

After the patch, get_db_size() detects the ":memory:" path and returns 0.
"""

from nanasqlite import NanaSQLite

db = NanaSQLite(":memory:")
db["key1"] = {"value": 42}
db["key2"] = {"value": 99}

try:
    size = db.get_db_size()
    print(f"[PATCHED] get_db_size() returned {size} (expected 0 for :memory:)")
    assert size == 0, f"Expected 0, got {size}"
except FileNotFoundError as exc:
    print(f"[VULNERABLE] FileNotFoundError raised: {exc}")
finally:
    db.close()
