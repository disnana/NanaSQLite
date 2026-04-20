"""
BUG-03 [Low] batch_delete() の before_delete フックがロック外で呼ばれる

現行: batch_delete() の before_delete は RLock 取得前に実行される（非 v2 モード）。
修正後: 非 v2 モードでは before_delete もロック内で実行される。
"""

import os
import tempfile
from nanasqlite import NanaSQLite
from nanasqlite.hooks import BaseHook


class LockInspectDeleteHook(BaseHook):
    def __init__(self):
        super().__init__()
        self.lock_held_during_delete = []

    def before_delete(self, db, key):
        try:
            held = db._lock._is_owned()
        except AttributeError:
            held = None
        self.lock_held_during_delete.append(held)


fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)
try:
    db = NanaSQLite(path)
    hook = LockInspectDeleteHook()
    db.add_hook(hook)
    db["k1"] = "v1"
    db["k2"] = "v2"
    db.batch_delete(["k1", "k2"])

    all_held = all(h is True for h in hook.lock_held_during_delete)
    if all_held and len(hook.lock_held_during_delete) == 2:
        print("PASS: batch_delete() の before_delete はロック内で実行された")
    elif hook.lock_held_during_delete and not all_held:
        print(f"BUG: batch_delete() の before_delete はロック外で実行された: {hook.lock_held_during_delete}")
    else:
        print(f"UNKNOWN: lock_held={hook.lock_held_during_delete}")
    db.close()
finally:
    os.unlink(path)
