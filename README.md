# NanaSQLite

[![PyPI version](https://badge.fury.io/py/nanasqlite.svg)](https://badge.fury.io/py/nanasqlite)
[![Tests](https://github.com/disnana/nanasqlite/actions/workflows/test.yml/badge.svg)](https://github.com/disnana/nanasqlite/actions/workflows/test.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A dict-like SQLite wrapper with instant persistence and intelligent caching.**

[English](#english) | [日本語](#日本語)

---

## English

### 🚀 Features

- **Dict-like Interface**: Use familiar `db["key"] = value` syntax
- **Instant Persistence**: All writes are immediately saved to SQLite
- **Smart Caching**: Lazy load (on-access) or bulk load (all at once)
- **Nested Structures**: Full support for nested dicts and lists (up to 30+ levels)
- **High Performance**: WAL mode, mmap, and batch operations for maximum speed
- **Zero Configuration**: Works out of the box with sensible defaults

### 📦 Installation

```bash
pip install nanasqlite
```

### ⚡ Quick Start

```python
from nanasqlite import NanaSQLite

# Create or open a database
db = NanaSQLite("mydata.db")

# Use it like a dict
db["user"] = {"name": "Nana", "age": 20, "tags": ["admin", "active"]}
print(db["user"])  # {'name': 'Nana', 'age': 20, 'tags': ['admin', 'active']}

# Data persists automatically
db.close()

# Reopen later - data is still there!
db = NanaSQLite("mydata.db")
print(db["user"]["name"])  # 'Nana'
```

### 🔧 Advanced Usage

```python
# Bulk load for faster repeated access
db = NanaSQLite("mydata.db", bulk_load=True)

# Batch operations for high-speed writes
db.batch_update({
    "key1": "value1",
    "key2": "value2",
    "key3": {"nested": "data"}
})

# Context manager support
with NanaSQLite("mydata.db") as db:
    db["temp"] = "value"
```

### 📚 Documentation

- [English Documentation](docs/en/README.md)
- [API Reference](docs/en/reference.md)

### ✨ New Features (v1.0.3rc3+)

**Pydantic Support:**
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

db.set_model("user", User(name="Nana", age=20))
user = db.get_model("user", User)
```

**Direct SQL Execution:**
```python
# Execute custom SQL
cursor = db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
rows = db.fetch_all("SELECT key, value FROM data")
```

**SQLite Wrapper Functions:**
```python
# Create tables and indexes easily
db.create_table("users", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT NOT NULL",
    "email": "TEXT UNIQUE"
})
db.create_index("idx_users_email", "users", ["email"])

# Simple queries
results = db.query(table_name="users", where="age > ?", parameters=(20,))
```

### ✨ Additional Features (v1.0.3rc4+)

**22 new wrapper functions for comprehensive SQLite operations:**

```python
# Data operations
rowid = db.sql_insert("users", {"name": "Alice", "age": 25})
db.sql_update("users", {"age": 26}, "name = ?", ("Alice",))
db.upsert("users", {"id": 1, "name": "Alice", "age": 25})
total = db.count("users", "age >= ?", (18,))

# Query extensions (pagination, grouping)
page2 = db.query_with_pagination("users", limit=10, offset=10)
stats = db.query_with_pagination("orders", 
    columns=["user_id", "COUNT(*) as count"], group_by="user_id")

# Schema management
db.alter_table_add_column("users", "phone", "TEXT")
schema = db.get_table_schema("users")
db.drop_table("old_table", if_exists=True)

# Utilities & transactions
db.vacuum()  # Optimize database
with db.transaction():
    db.sql_insert("logs", {"message": "Event"})
```

---

## 日本語

### 🚀 特徴

- **dict風インターフェース**: おなじみの `db["key"] = value` 構文で操作
- **即時永続化**: 書き込みは即座にSQLiteに保存
- **スマートキャッシュ**: 遅延ロード（アクセス時）または一括ロード（起動時）
- **ネスト構造対応**: 30階層以上のネストしたdict/listをサポート
- **高性能**: WALモード、mmap、バッチ操作で最高速度を実現
- **設定不要**: 合理的なデフォルト設定でそのまま動作

### 📦 インストール

```bash
pip install nanasqlite
```

### ⚡ クイックスタート

```python
from nanasqlite import NanaSQLite

# データベースを作成または開く
db = NanaSQLite("mydata.db")

# dictのように使う
db["user"] = {"name": "Nana", "age": 20, "tags": ["admin", "active"]}
print(db["user"])  # {'name': 'Nana', 'age': 20, 'tags': ['admin', 'active']}

# データは自動的に永続化
db.close()

# 後で再度開いても、データはそのまま！
db = NanaSQLite("mydata.db")
print(db["user"]["name"])  # 'Nana'
```

### 🔧 高度な使い方

```python
# 一括ロードで繰り返しアクセスを高速化
db = NanaSQLite("mydata.db", bulk_load=True)

# バッチ操作で高速書き込み
db.batch_update({
    "key1": "value1",
    "key2": "value2",
    "key3": {"nested": "data"}
})

# コンテキストマネージャ対応
with NanaSQLite("mydata.db") as db:
    db["temp"] = "value"
```

### 📚 ドキュメント

- [日本語ドキュメント](docs/ja/README.md)
- [APIリファレンス](docs/ja/reference.md)

### ✨ 新機能 (v1.0.3rc3+)

**Pydantic互換性:**
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

db.set_model("user", User(name="Nana", age=20))
user = db.get_model("user", User)
```

**直接SQL実行:**
```python
# カスタムSQLの実行
cursor = db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
rows = db.fetch_all("SELECT key, value FROM data")
```

**SQLiteラッパー関数:**
```python
# テーブルとインデックスを簡単に作成
db.create_table("users", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT NOT NULL",
    "email": "TEXT UNIQUE"
})
db.create_index("idx_users_email", "users", ["email"])

# シンプルなクエリ
results = db.query(table_name="users", where="age > ?", parameters=(20,))
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
