"""
PERF-13 [Medium] `values()` / `items()` が Unbounded モードで MISSING フィルタを不要適用する問題

問題: Unbounded モードでは _data に MISSING センチネルが格納されることはないため、
     `if v is not MISSING` フィルタは常に全要素を通過するだけの無駄なオーバーヘッド。
修正後: Unbounded モードでは list(self._data.values()) / list(self._data.items()) を直接返す。
"""

import os
import tempfile

try:
    from nanasqlite import CacheType, NanaSQLite
    from nanasqlite.cache import MISSING

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        db = NanaSQLite(path)  # Unbounded mode (default)

        data = {f"k{i}": i * 10 for i in range(50)}
        db.batch_update(data)

        # --- Test 1: values() returns correct values, no MISSING ---
        vals = db.values()
        if MISSING in vals:
            print("BUG: values() returned MISSING sentinel in Unbounded mode")
        elif set(vals) == set(range(0, 500, 10)):
            print("PASS: values() returns correct values without MISSING in Unbounded mode")
        else:
            print(f"BUG: values() returned unexpected data: {vals[:5]}...")

        # --- Test 2: items() returns correct pairs, no MISSING ---
        items = db.items()
        if any(v is MISSING for _, v in items):
            print("BUG: items() returned MISSING sentinel in Unbounded mode")
        elif len(items) == 50 and all(isinstance(v, int) for _, v in items):
            print("PASS: items() returns correct key-value pairs without MISSING in Unbounded mode")
        else:
            print(f"BUG: items() returned unexpected data: {items[:3]}...")

        # --- Test 3: values() in LRU mode filters MISSING correctly (BUG-03 regression) ---
        db.close()
        os.unlink(path)

        fd2, path2 = tempfile.mkstemp(suffix=".db")
        os.close(fd2)

        db2 = NanaSQLite(path2, cache_strategy=CacheType.LRU, cache_size=64)
        for i in range(20):
            db2[f"m{i}"] = i
        lru_vals = db2.values()
        if MISSING in lru_vals:
            print("BUG: values() returned MISSING in LRU mode (BUG-03 regression)")
        elif len(lru_vals) == 20:
            print("PASS: values() in LRU mode has no MISSING sentinels")
        else:
            print(f"BUG: values() in LRU mode returned wrong count: {len(lru_vals)}")

        lru_items = db2.items()
        if any(v is MISSING for _, v in lru_items):
            print("BUG: items() returned MISSING in LRU mode (BUG-03 regression)")
        elif len(lru_items) == 20:
            print("PASS: items() in LRU mode has no MISSING sentinels")
        else:
            print(f"BUG: items() in LRU mode returned wrong count: {len(lru_items)}")

        db2.close()
        os.unlink(path2)

    except Exception as e:
        import traceback
        print(f"BUG: Unexpected exception: {e}")
        traceback.print_exc()

except Exception as e:
    import traceback
    print(f"BUG: Import error: {e}")
    traceback.print_exc()
