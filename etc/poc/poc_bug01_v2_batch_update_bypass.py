"""
BUG-01 [Critical] batch_update / batch_delete の V2 モードバイパスと競合

batch_update を呼び出した時、V2 エンジンのキューに入らず直接DBを更新してしまうため、
その後に非同期フラッシュが起きると、古い値（キューに残っていた値）で上書きされる不整合が発生する。
修正後: batch_update も V2 バッファを経由し、一貫した順番で書き込まれること。
"""

import os
import tempfile
import time

from nanasqlite import NanaSQLite

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    # manualフラッシュモードにしてフラッシュタイミングを制御可能にする
    db = NanaSQLite(path, v2_mode=True, flush_mode="manual", optimize=False)

    # 1. kvs_set でバックグラウンドキューに "v2_value" を入れる（まだDBへは書き込まれていない）
    db["test_key"] = "v2_value"

    # 2. batch_update は現在の実装だと V2 キューを無視して直接書き込む
    # そのためDB上は "batch_value" になる
    db.batch_update({"test_key": "batch_value"})

    # 3. 意図的にフラッシュを実行
    db.flush()
    # ワーカー完了待ち (shutdownするとその後のload_all->flushでエラーになるため)
    import time

    time.sleep(1)

    # キャッシュをクリアしてDBから直接読み込む
    db.clear_cache()
    db.load_all()

    # フラッシュによって、1でキューに入れた "v2_value" が後から書き込まれ、
    # 2で同期的に書き込んだ "batch_value" が上書きされていれば BUG
    actual = db.get("test_key")
    if actual == "v2_value":
        print(f"BUG: batch_update was overwritten by old V2 staging data. (Expected 'batch_value', got '{actual}')")
    elif actual == "batch_value":
        print("PASS: batch_update correctly handled in V2 mode.")
    else:
        print(f"BUG: Unexpected value '{actual}'")

finally:
    try:
        os.unlink(path)
    except OSError:
        pass
