"""
PERF-12 [High] `get()` の LRU/TTL モードで二重キャッシュルックアップが発生する問題

問題: get() の LRU/TTL ブランチで _ensure_cached() が cache.get() を内部呼び出し後、
     さらに呼び元も cache.get() を再度実行するため、キャッシュヒットで move_to_end() が 2 回発生する。
修正後: _data 在籍確認 → cache.get() 1 回のみ (PERF-09 と同じパターン)。
"""

import os
import tempfile
import time

try:
    from nanasqlite import CacheType, NanaSQLite
    from nanasqlite.cache import MISSING

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        # --- Test 1: LRU cache hit returns correct value ---
        db = NanaSQLite(path, cache_strategy=CacheType.LRU, cache_size=128)
        db["key1"] = {"payload": [1, 2, 3]}
        _ = db["key1"]  # warm up cache

        result = db.get("key1")
        if result == {"payload": [1, 2, 3]}:
            print("PASS: get() returns correct value on LRU cache hit")
        else:
            print(f"BUG: get() returned unexpected value: {result}")

        # --- Test 2: LRU cache miss returns default ---
        result = db.get("nonexistent", "fallback")
        if result == "fallback":
            print("PASS: get() returns default on cache miss")
        else:
            print(f"BUG: get() returned unexpected value for missing key: {result}")

        # --- Test 3: LRU known-absent key returns default (not MISSING) ---
        _ = db.get("ghost", None)  # first access: populates negative cache
        result2 = db.get("ghost", "fallback2")
        if result2 == "fallback2" and result2 is not MISSING:
            print("PASS: get() returns default (not MISSING) for known-absent key")
        else:
            print(f"BUG: get() returned MISSING sentinel: {result2!r}")

        db.close()

        # --- Test 4: TTL cache hit returns correct value ---
        db2 = NanaSQLite(path + "2", cache_strategy=CacheType.TTL, cache_ttl=300)
        db2["ttl_key"] = {"nums": list(range(5))}
        _ = db2["ttl_key"]  # warm up

        result = db2.get("ttl_key")
        if result == {"nums": list(range(5))}:
            print("PASS: get() returns correct value on TTL cache hit")
        else:
            print(f"BUG: get() returned unexpected value on TTL: {result}")

        # --- Test 5: Performance benchmark - verify single cache.get() call ---
        # Measure relative performance: get() hot path should be fast (< 2x overhead vs __getitem__)
        N = 5000
        db2["bench"] = 42
        _ = db2["bench"]  # warm up

        t0 = time.perf_counter()
        for _ in range(N):
            _ = db2["bench"]
        getitem_time = time.perf_counter() - t0

        t0 = time.perf_counter()
        for _ in range(N):
            _ = db2.get("bench")
        get_time = time.perf_counter() - t0

        ratio = get_time / max(getitem_time, 1e-9)
        if ratio < 3.0:
            print(f"PASS: get() vs __getitem__ overhead ratio={ratio:.2f} (< 3.0)")
        else:
            print(f"BUG: get() overhead ratio={ratio:.2f} is suspiciously high (may indicate double lookup)")

        db2.close()
        try:
            os.unlink(path + "2")
        except OSError:
            pass  # Ignore cleanup errors; file may already be absent.

    finally:
        try:
            if not db._is_closed:
                db.close()
        except Exception:  # noqa: BLE001
            pass  # Suppress any db.close() error during POC teardown.
        os.unlink(path)

except Exception as e:
    import traceback
    print(f"BUG: Unexpected exception: {e}")
    traceback.print_exc()
