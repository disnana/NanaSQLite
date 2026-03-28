"""
BUG-02 [Critical] 非同期 flush() と 同期操作 (clear(), load_all()) によるデータの巻き戻り

clear() が flush() を呼び出しても、完了を待たずに DELETE ステートメントが走るため、
非同期フラッシュが削除後に走り、消されたデータが復活してしまうというバグがある。
修正後: flush に wait=True が追加され、これらの同期操作が安全に行えること。
"""

import os
import tempfile
import time

from nanasqlite import NanaSQLite

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    db = NanaSQLite(path, v2_mode=True, optimize=False)

    # バックグラウンドワーカー内部の処理を遅延させることで
    # flush() が非同期であることの競合を引き起こす
    original_process = db._v2_engine._process_kvs_chunk

    def slow_process(chunk):
        time.sleep(1)
        original_process(chunk)

    db._v2_engine._process_kvs_chunk = slow_process

    db["ghost_key"] = "ghost_value"

    # 直後に clear() を呼ぶ。
    # 現在の clear() は self._v2_engine.flush() を呼ぶが完了を待たないため、
    # すぐに DELETE 文が発行されメモリとDBから消える。
    db.clear()

    # 2秒待ってフラッシュを終わらせる
    time.sleep(2)

    # キャッシュをクリアしてDBのみロード
    db.clear_cache()
    db.load_all()

    actual = db.get("ghost_key")
    if actual == "ghost_value":
        print("BUG: Data re-inserted after clear() because flush() was async. (Data restored from ghost buffer)")
    elif actual is None:
        print("PASS: clear() successfully waited for flush()")
    else:
        print(f"BUG: target state invalid '{actual}'")

finally:
    try:
        os.unlink(path)
    except OSError:
        pass
