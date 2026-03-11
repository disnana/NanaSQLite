import os

from nanasqlite import NanaSQLite

db_path = "test_none.db"
if os.path.exists(db_path):
    os.remove(db_path)

db = NanaSQLite(db_path)
db["my_key"] = None
print("In cache directly after set:", "my_key" in db, "value:", db.get("my_key"))

# Close and reopen to force DB read
db.close()

db2 = NanaSQLite(db_path)
print("After reopen - is key in DB (in operator):", "my_key" in db2)
try:
    print("After reopen - getting value:", db2["my_key"])
except KeyError:
    print("KeyError! my_key was not found after reopening. BUG DETECTED!")
except Exception as e:
    print(f"Other error: {e}")

db2.close()
if os.path.exists(db_path):
    os.remove(db_path)
