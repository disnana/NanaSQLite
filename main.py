from nanasqlite import NanaSQLite

# 基本的な使い方
db = NanaSQLite("test.db")
db["user"] = {"name": "Nana", "age": 20}
print(db["user"])  # {'name': 'Nana', 'age': 20}

# 一括ロードで高速化
db = NanaSQLite("test.db", bulk_load=True)

# コンテキストマネージャ
with NanaSQLite("test.db") as db:
    db["key"] = "value"
    if "key" in db:
        print("key exists")
    else:
        print("key does not exist")
    if db["key"] == "value":
        print("value is value")
    else:
        print("value is not value")
    for key in db:
        print(key)
    