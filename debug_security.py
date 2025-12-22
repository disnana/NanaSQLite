
import sys
from nanasqlite import NanaSQLite
try:
    db = NanaSQLite("test_debug.db", strict_sql_validation=True)
    print("Init OK")
    db.query(columns=["COUNT(*)"])
    print("Query OK")
    db.close()
    print("Close OK")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
