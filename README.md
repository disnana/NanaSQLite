# NanaSQLite

[![PyPI version](https://img.shields.io/pypi/v/nanasqlite.svg)](https://pypi.org/project/nanasqlite/)
[![Python versions](https://img.shields.io/pypi/pyversions/nanasqlite.svg)](https://pypi.org/project/nanasqlite/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/nanasqlite)](https://pepy.tech/project/nanasqlite)
[![Tests](https://github.com/disnana/nanasqlite/actions/workflows/ci.yml/badge.svg)](https://github.com/disnana/nanasqlite/actions/workflows/ci.yml)

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
- **Security & Stability (v1.2.0)**: SQL validation, ReDoS protection, and strict connection management
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

# Batch operations for high-speed reads/writes
db.batch_update({"k1": "v1", "k2": "v2"})
results = db.batch_get(["k1", "k2"])

# Context manager support
with NanaSQLite("mydata.db") as db:
    db["temp"] = "value"
```

### 📚 Documentation

- [English Documentation](docs/en/README.md)
- [API Reference](docs/en/reference.md)
- [Benchmark Results](https://disnana.github.io/NanaSQLite/dev/bench/)
- [Migration Guide (v1.1.x to v1.2.0)](MIGRATION_GUIDE.md)
- [Development Guide](DEVELOPMENT_GUIDE.md)

### ✨ v1.2.0 New Features

**Security Enhancements & Strict Connection Management:**

```python
# v1.2.0 Security Features
db = NanaSQLite("mydata.db", 
    strict_sql_validation=True,  # Disallow unauthorized SQL functions
    max_clause_length=500        # Limit SQL length to prevent ReDoS
)

# v1.2.0 Read-Only Connection Pool (Async only)
async with AsyncNanaSQLite("mydata.db", read_pool_size=5) as db:
    # Heavy read operations (query, fetch_all) use the pool automatically
    # allowing parallel execution without blocking writes or other reads
    results = await asyncio.gather(
        db.query("logs", where="level=?", parameters=("ERROR",)),
        db.query("logs", where="level=?", parameters=("INFO",)),
        db.query("logs", where="level=?", parameters=("WARN",))
    )

# Strict Connection Management
with db.transaction():
    sub_db = db.table("sub")
    # ... operations ...
db.close()
# Accessing sub_db now raises NanaSQLiteClosedError for safety!
```

**Consistent Async API:**
```python
# All methods now have 'a' prefixed aliases in AsyncNanaSQLite
await db.abatch_update(data)
await db.abatch_get(keys)
await db.ato_dict()
```

### ✨ v1.1.0 New Features

**Safely operate multiple tables in the same database with shared connections:**

```python
from nanasqlite import NanaSQLite

# Create main table instance
main_db = NanaSQLite("mydata.db", table="users")

# Get another table instance sharing the same connection
products_db = main_db.table("products")
orders_db = main_db.table("orders")

# Each table has isolated cache and operations
main_db["user1"] = {"name": "Alice", "email": "alice@example.com"}
products_db["prod1"] = {"name": "Laptop", "price": 999}
orders_db["order1"] = {"user": "user1", "product": "prod1"}
```

**Transaction Support & Error Handling (v1.1.0+):**

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

with db.transaction():
    db["key1"] = "value1"
    db["key2"] = "value2"
```

**Full async/await support (v1.1.0+):**

```python
async with AsyncNanaSQLite("mydata.db") as db:
    await db.aset("user", {"name": "Nana"})
    results = await db.abatch_get(["k1", "k2"])
```

### ✨ v1.0.3+ Legacy Features

**Pydantic Support & Direct SQL:**

```python
# Pydantic support
db.set_model("user", User(name="Nana", age=20))

# Direct SQL execution
db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))

# 22 new SQLite wrapper functions (sql_insert, sql_update, count, etc.)
db.sql_insert("users", {"name": "Alice", "age": 25})
```

---

---

---

## 日本語

### 🚀 特徴

- **dict風インターフェース**: おなじみの `db["key"] = value` 構文で操作
- **即時永続化**: 書き込みは即座にSQLiteに保存
- **スマートキャッシュ**: 遅延ロード（アクセス時）または一括ロード（起動時）
- **ネスト構造対応**: 30階層以上のネストしたdict/listをサポート
- **高性能**: WALモード、mmap、バッチ操作で最高速度を実現
- **セキュリティと安定性 (v1.2.0)**: SQL検証、ReDoS対策、厳格な接続管理を導入
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

# バッチ操作で高速な読み書き
db.batch_update({"k1": "v1", "k2": "v2"})
results = db.batch_get(["k1", "k2"])

# コンテキストマネージャ対応
with NanaSQLite("mydata.db") as db:
    db["temp"] = "value"
```

### 📚 ドキュメント

- [日本語ドキュメント](docs/ja/README.md)
- [APIリファレンス](docs/ja/reference.md)
- [ベンチマーク結果](https://disnana.github.io/NanaSQLite/dev/bench/)
- [移行ガイド (v1.1.x から v1.2.0)](MIGRATION_GUIDE.md)
- [開発ガイド](DEVELOPMENT_GUIDE.md)

### ✨ v1.2.0 新機能

**セキュリティ強化と厳格な接続管理:**

```python
# v1.2.0 セキュリティ機能
db = NanaSQLite("mydata.db", 
    strict_sql_validation=True,  # 未許可のSQL関数を禁止
    max_clause_length=500        # SQLの長さを制限してReDoSを防止
)

# v1.2.0 読み取り専用接続プール（非同期のみ）
async with AsyncNanaSQLite("mydata.db", read_pool_size=5) as db:
    # 重い読み取り操作（query, fetch_all）は自動的にプールを使用
    results = await asyncio.gather(
        db.query("logs", where="level=?", parameters=("ERROR",)),
        db.query("logs", where="level=?", parameters=("INFO",))
    )

# 厳格な接続管理
db.close()
# 無効化されたインスタンスへのアクセスは NanaSQLiteClosedError を送出します。
```

**一貫性のある非同期API:**
```python
# AsyncNanaSQLiteの全てのメソッドに 'a' プレフィックス付きのエイリアスを追加
await db.abatch_update(data)
await db.abatch_get(keys)
await db.ato_dict()
```

### ✨ v1.1.0 新機能

**同一データベース内の複数テーブルを接続共有で安全に操作:**

```python
from nanasqlite import NanaSQLite

# メインテーブルインスタンスを作成
main_db = NanaSQLite("mydata.db", table="users")

# 同じ接続を共有する別のテーブルインスタンスを取得
products_db = main_db.table("products")
orders_db = main_db.table("orders")

# 各テーブルは独立したキャッシュと操作を持つ
main_db["user1"] = {"name": "Alice"}
products_db["prod1"] = {"name": "Laptop"}
```

**トランザクションサポートとエラーハンドリング (v1.1.0+):**

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

with db.transaction():
    db["key1"] = "value1"
    db["key2"] = "value2"
```

**完全な非同期サポート (v1.1.0+):**

```python
async with AsyncNanaSQLite("mydata.db") as db:
    await db.aset("user", {"name": "Nana"})
    results = await db.abatch_get(["k1", "k2"])
```

### ✨ v1.0.3+ レガシー機能

**Pydantic互換性と直接SQL実行:**

```python
# Pydantic互換性
db.set_model("user", User(name="Nana", age=20))

# 直接SQL実行
db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))

# 22種類のSQLiteラッパー関数 (sql_insert, sql_update, count等)
db.sql_insert("users", {"name": "Alice", "age": 25})
```

---

---

## License

MIT License - see [LICENSE](LICENSE) for details.
