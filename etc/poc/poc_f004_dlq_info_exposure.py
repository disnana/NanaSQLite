import io
import logging

from nanasqlite.core import NanaSQLite


def main():
    # Setup logging capture
    log_output = io.StringIO()
    handler = logging.StreamHandler(log_output)
    logging.getLogger("nanasqlite.v2_engine").addHandler(handler)
    logging.getLogger("nanasqlite.v2_engine").setLevel(logging.ERROR)

    db = NanaSQLite("f004_test.db", v2_mode=True)

    # Secret data that should NOT be in logs
    secret_value = "SUPER_SECRET_TOKEN_12345"

    # We need to trigger a failure in Lane 1 (KVS) to get it into DLQ.
    # One way is to manually corrupt the engine's internal state or mock a DB failure.
    # But let's try to trigger a real SQLite error during flush.
    # e.g. Trying to insert into a table that was dropped?

    # Force immediate mode to trigger flush
    db._v2_engine._flush_mode = "immediate"

    print("Triggering a failure that goes to DLQ...")

    # We'll drop the table behind the engine's back to cause a flush failure
    db.execute(f"DROP TABLE {db._safe_table}")

    try:
        db["secret_key"] = {"token": secret_value}
        # Force flush
        db.flush(wait=True)
    except Exception as e:
        print(f"Caught expected flush error: {e}")

    logs = log_output.getvalue()
    if secret_value in logs:
        print("[!] VULNERABILITY CONFIRMED: Secret value found in logs!")
        print(f"Log snippet: {logs}")
    else:
        print("[-] SAFE: Secret value not found in logs.")

    dlq = db.get_dlq()
    if dlq:
        item_str = str(dlq[0].item)
        if secret_value in item_str:
             print("[!] VULNERABILITY CONFIRMED: Secret value found in DLQ item!")

    db.close()

if __name__ == "__main__":
    main()
