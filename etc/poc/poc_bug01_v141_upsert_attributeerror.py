"""
BUG-01 [High] (v1.4.1dev3): upsert(table, data_dict, conflict_columns) の AttributeError 再現スクリプト

問題:
    upsert(table_name, data_dict, conflict_columns=["col"]) 形式で呼び出した場合に、
    core.py 内部で target_data ではなく data (= None) の .keys() が参照され、
    AttributeError が発生していた。

修正:
    core.py L2377: `for col in data.keys()` → `for col in target_data.keys()`
"""
import os
import sys

from nanasqlite import NanaSQLite


def run_poc() -> None:
    db_path = "poc_bug01_v141.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    print("--- NanaSQLite [BUG-01] POC (v1.4.1dev3) ---")
    print("Test Case: upsert(table_name, data_dict, conflict_columns=[...])")
    print("Expected:  Success (row inserted/updated)")
    print("Pre-fix:   AttributeError: 'NoneType' object has no attribute 'keys'")

    db = NanaSQLite(db_path)
    try:
        db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})

        # --- 再現パターン: table_name + data_dict + conflict_columns ---
        db.upsert("users", {"id": 1, "name": "Alice"}, conflict_columns=["id"])

        rows = db.query("users")
        assert len(rows) == 1, "挿入に失敗"
        assert rows[0]["name"] == "Alice", "値が正しくない"

        # --- UPSERT (UPDATE) パターン ---
        db.upsert("users", {"id": 1, "name": "Bob"}, conflict_columns=["id"])
        rows = db.query("users")
        assert rows[0]["name"] == "Bob", "更新に失敗"

        print("POC result: FIXED (Success - no AttributeError raised)")
        sys.exit(0)

    except AttributeError as e:
        print(f"POC result: REPRODUCED (Caught expected AttributeError: {e})")
        sys.exit(1)
    except AssertionError as e:
        print(f"POC result: ASSERTION FAILED ({e})")
        sys.exit(1)
    except Exception as e:
        print(f"POC result: FAILED (Unexpected exception: {type(e).__name__}: {e})")
        sys.exit(1)
    finally:
        db.close()
        for suffix in ("", "-wal", "-shm"):
            try:
                os.remove(db_path + suffix)
            except OSError as e:
                print(f"Warning: failed to remove {db_path + suffix}: {e}", file=sys.stderr)


if __name__ == "__main__":
    run_poc()
