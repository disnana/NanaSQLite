"""
BUG-01 [High] pop() が v2 モードで直接 DB 書き込みを行いバックグラウンドフラッシュと競合する

問題: v2 モードで pop() を呼ぶと _delete_from_db() が直接 DB へ DELETE を発行し、
     v2 エンジンの staging buffer を完全にバイパスする。
     staging buffer には元の SET 操作が残ったままになるため、
     その後の flush() でデータが DB に再挿入（データ復活）する。

修正後: pop() が v2 エンジンを経由して削除を行い、staging buffer から
        SET 操作がキャンセル相当の kvs_delete によって上書きされる。
"""

import os
import tempfile
import warnings
from nanasqlite import NanaSQLite

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # v2 manual モードでは明示的に flush() を呼ぶまで staging buffer がフラッシュされない
        with NanaSQLite(path, v2_mode=True, flush_mode="manual") as db:
            # ①書き込み: staging buffer に SET が積まれ、キャッシュも更新される
            db["mykey"] = "hello"

            # ②pop(): キャッシュから削除 + _delete_from_db() (no-op: まだ DB に存在しない)
            #   しかし staging buffer の SET はキャンセルされない!
            val = db.pop("mykey", None)
            assert val == "hello", f"pop() の戻り値が正しくない: {val}"

            # ③flush(): staging buffer の SET が DB に書き込まれてしまう (BUG!)
            db.flush(wait=True)

            # ④キャッシュをクリアして DB を直接参照させる
            db.clear_cache()

            # ⑤get(): DB から取得 → 修正前は "hello" が復活している
            result = db.get("mykey", "DELETED")

            if result == "DELETED":
                print("PASS: pop() 後に flush() + clear_cache() しても削除済みキーは復活しない")
            else:
                print(f"BUG: pop() した 'mykey' が flush() 後に復活した: {result!r} (期待値: 'DELETED')")

except Exception as e:
    print(f"BUG: 予期しない例外が発生: {type(e).__name__}: {e}")
finally:
    try:
        os.unlink(path)
    except OSError:
        pass
    for suffix in ("-wal", "-shm", "-journal"):
        try:
            os.unlink(path + suffix)
        except OSError:
            pass
