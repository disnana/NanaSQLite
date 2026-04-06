"""
BUG-02 [Medium] batch_get() が _cached_keys の「存在しない」ステータスを尊重しない

問題: v2 モードで __delitem__ を実行すると:
     - キャッシュ (_cached_keys) にキーが「存在しない」として記録される
     - v2 staging buffer に削除操作がキューされる（DB はまだ更新されていない）
     この状態で get() はキャッシュを参照して「存在しない」と正しく返すが、
     batch_get() は _cached_keys ではなく _data のみを確認するため、
     cache miss → DB 参照 → DB にはまだ古い値 → 「存在する」と誤って返す。
     単一キーの get() と batch_get() の間で一貫性がない。

修正後: batch_get() が _cached_keys を確認して「存在しない」として記録されたキーを
        missing_keys に回さないようにする。
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
        # v2 manual モード: flush しない限り DB は更新されない
        with NanaSQLite(path, v2_mode=True, flush_mode="manual") as db:
            # ① DB にキーを書き込む（まず即時 flush して DB に入れる）
            db["key1"] = "value1"
            db.flush(wait=True)  # DB に書き込む

            # ② DB には key1 が存在する; cache もある
            # ③ __delitem__ で削除: v2 パス → staging に delete が積まれる、cache では absent
            del db["key1"]

            # この時点での状態:
            # - cache: key1 は "known absent" (_cached_keys にあるが _data にはない)
            # - staging: key1 → {action: delete} (DB はまだ更新されていない)
            # - DB: key1 は "value1" (まだ削除されていない)

            # ④ get() → _ensure_cached → key1 は _cached_keys にあり _data にはない → False → None を返す
            get_result = db.get("key1", "NOT_FOUND")

            # ⑤ batch_get() → key1 は _data にない → missing_keys → DB 参照 → "value1" を返してしまう
            batch_result = db.batch_get(["key1"])

            # get() は正しく "NOT_FOUND" を返すが batch_get() は誤って "value1" を返す
            if get_result == "NOT_FOUND" and "key1" not in batch_result:
                print("PASS: get() と batch_get() が一致して削除済みキーを返さない")
            elif get_result == "NOT_FOUND" and "key1" in batch_result:
                print(
                    f"BUG: get()={get_result!r} vs batch_get()={batch_result.get('key1')!r} - "
                    f"単一キーは削除済みを返すが batch_get は DB の古い値を返す（不整合）"
                )
            else:
                print(f"INFO: get_result={get_result!r}, batch_result={batch_result}")

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
