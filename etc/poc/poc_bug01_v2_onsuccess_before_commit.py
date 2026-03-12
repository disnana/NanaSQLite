"""
BUG-01 [High] V2Engine on_success コールバックがCOMMIT前に呼ばれる

修正前: on_success がトランザクション内で即座に呼ばれるため、
後続タスクの失敗でロールバックが発生しても成功通知が先行する。
修正後: on_success は COMMIT 成功後にのみ呼ばれる。
"""

import os
import tempfile

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    import apsw

    from nanasqlite.v2_engine import StrictTask, V2Engine

    conn = apsw.Connection(path)
    conn.execute("CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value TEXT)")

    engine = V2Engine(
        connection=conn,
        table_name='"data"',
        flush_mode="manual",
    )

    # Track callback invocation order
    callback_log = []

    task1 = StrictTask(
        priority=10,
        sequence_id=0,
        task_type="execute",
        sql="INSERT INTO data (key, value) VALUES ('k1', 'v1')",
        parameters=None,
        on_success=lambda: callback_log.append("task1_success"),
        on_error=lambda e: callback_log.append(f"task1_error: {e}"),
    )
    task2 = StrictTask(
        priority=10,
        sequence_id=1,
        task_type="execute",
        sql="INVALID SQL THAT WILL FAIL",
        parameters=None,
        on_success=lambda: callback_log.append("task2_success"),
        on_error=lambda e: callback_log.append("task2_error"),
    )

    engine._strict_queue.put(task1)
    engine._strict_queue.put(task2)

    try:
        engine._perform_flush()
    except Exception:
        pass

    # Verify task1's on_success was NOT called (transaction rolled back)
    if "task1_success" in callback_log:
        print(f"BUG: task1 on_success called despite rollback. Log: {callback_log}")
    else:
        has_error = any("task2_error" in entry for entry in callback_log)
        if has_error:
            print(f"PASS: task1 on_success not called after rollback. Log: {callback_log}")
        else:
            print(f"UNEXPECTED: Log: {callback_log}")

    engine.shutdown()
    conn.close()
finally:
    os.unlink(path)
