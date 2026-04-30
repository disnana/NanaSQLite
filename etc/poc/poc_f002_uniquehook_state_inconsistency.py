from nanasqlite.core import NanaSQLite
from nanasqlite.exceptions import NanaSQLiteValidationError
from nanasqlite.hooks import CheckHook, UniqueHook


def main():
    db = NanaSQLite(":memory:")

    # 1. Add a UniqueHook (with index)
    unique_hook = UniqueHook(field="email", use_index=True)
    db.add_hook(unique_hook)

    # 2. Add a CheckHook that ALWAYS fails
    def fail_func(key, value):
        return False

    check_hook = CheckHook(check_func=fail_func, error_msg="Intentional failure")
    db.add_hook(check_hook)

    email = "test@example.com"
    data = {"email": email}

    print(f"Attempting first write with email='{email}'...")
    try:
        db["user:1"] = data
    except NanaSQLiteValidationError as e:
        print(f"Expected failure: {e}")

    # Verify DB is empty
    if "user:1" not in db:
        print("Confirmed: user:1 not in DB.")

    # 3. Try to insert the SAME email again (to another key)
    # If UniqueHook index was updated and not rolled back, this will fail with duplicate error
    print(f"\nAttempting second write with SAME email='{email}'...")
    try:
        db["user:2"] = data
    except NanaSQLiteValidationError as e:
        print(f"Caught exception: {e}")
        if "Unique constraint violation" in str(e):
            print("[!] VULNERABILITY CONFIRMED: UniqueHook state is inconsistent (dirty index).")
        else:
            print(f"Other failure: {e}")
    else:
        print("[-] SAFE: Second write passed (or didn't trigger unique error).")

if __name__ == "__main__":
    main()
