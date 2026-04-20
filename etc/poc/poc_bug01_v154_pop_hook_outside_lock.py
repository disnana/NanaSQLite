"""
BUG-01 [Medium] pop() の before_delete フックがロック外で呼ばれる

現行: pop() の before_delete は RLock 取得前に実行される（非 v2 モード）。
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
        # threading.RLock._is_owned() returns True when current thread holds the lock
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
    db["k"] = "v"
    result = db.pop("k")

    if hook.lock_held_during_delete and hook.lock_held_during_delete[0] is True:
        print("PASS: pop() の before_delete はロック内で実行された")
    elif hook.lock_held_during_delete and hook.lock_held_during_delete[0] is False:
        print("BUG: pop() の before_delete はロック外で実行された")
    else:
        print(f"UNKNOWN: lock_held={hook.lock_held_during_delete}")
    db.close()
finally:
    os.unlink(path)
