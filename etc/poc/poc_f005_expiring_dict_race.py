import time

from nanasqlite.utils import ExpirationMode, ExpiringDict


def main():
    INITIAL_TTL = 0.2  # initial value's TTL
    SLEEP_TO_ALMOST_EXPIRE = 0.18  # wait until almost expired

    cache = ExpiringDict(expiration_time=INITIAL_TTL, mode=ExpirationMode.SCHEDULER)

    key = "test_key"
    results = []

    for trial in range(10):
        # Insert key with initial TTL
        cache[key] = f"original_value_{trial}"

        # Wait until it's nearly expired but still valid
        time.sleep(SLEEP_TO_ALMOST_EXPIRE)

        # Refresh the key (new TTL starts now)
        cache[key] = f"NEW_VALUE_{trial}"

        # Wait long enough for the ORIGINAL TTL window to pass (scheduler may evict)
        # but NOT long enough for the new TTL to expire
        # Original would expire ~0.02s after update (INITIAL_TTL - SLEEP_TO_ALMOST_EXPIRE)
        # New TTL = INITIAL_TTL from point of update, so it should survive for full INITIAL_TTL
        time.sleep(0.05)  # gives scheduler time to run its eviction loop

        if key in cache:
            results.append("SAFE")
        else:
            results.append("VULNERABLE")

        # Cleanup for next trial
        try:
            del cache[key]
        except KeyError:
            pass
        time.sleep(0.05)  # Small gap between trials

    vulnerable_count = results.count("VULNERABLE")
    safe_count = results.count("SAFE")

    print(f"Results over {len(results)} trials: {safe_count} SAFE, {vulnerable_count} VULNERABLE")
    if vulnerable_count == 0:
        print("[-] FIXED: All trials passed. F-005 vulnerability resolved.")
    else:
        print("[!] VULNERABILITY CONFIRMED: Key was purged despite being updated!")
        print(f"    Details: {results}")

if __name__ == "__main__":
    main()
