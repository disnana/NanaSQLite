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

- **[Official Documentation Website ↗](https://nanasqlite.disnana.com/)** (Best Experience)
- [English Guide](https://nanasqlite.disnana.com/en/guide)
- [API Reference (Sync)](https://nanasqlite.disnana.com/en/api_sync)
- [API Reference (Async)](https://nanasqlite.disnana.com/en/api_async)
- [Benchmark Trends 📊](https://nanasqlite.disnana.com/dev/bench/)
- [Migration Guide (v1.1.x to v1.2.0)](MIGRATION_GUIDE.md)

### ✨ v1.3.x New Features

- **Advanced Cache Strategies**: LRU and TTL support. [Learn more](https://nanasqlite.disnana.com/en/guide#lesson-10-cache-strategies)
- **Data Encryption**: Secure storage with AES-GCM (default), ChaCha20, or Fernet. [Learn more](https://nanasqlite.disnana.com/en/guide#lesson-11-encryption)
- **Persistence TTL**: Self-expiring data for sessions and temporary storage.

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

**[Read Secure Development Guide ↗](https://nanasqlite.disnana.com/en/guide#_2-security-v1-2-0-)**

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

**[Explore Multi-table & Transactions ↗](https://nanasqlite.disnana.com/en/guide#_4-transactions-multi-table)**

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

- **[公式サイト ↗](https://nanasqlite.disnana.com/)** (推奨)
- [スタートアップガイド](https://nanasqlite.disnana.com/guide)
- [APIリファレンス (同期)](https://nanasqlite.disnana.com/api_sync)
- [APIリファレンス (非同期)](https://nanasqlite.disnana.com/api_async)
- [ベンチマーク履歴 📊](https://nanasqlite.disnana.com/dev/bench/)
- [移行ガイド (v1.1.x から v1.2.0)](MIGRATION_GUIDE.md)

### ✨ v1.3.x 新機能

- **キャッシュ戦略**: LRU / TTL サポート ([ドキュメント](https://nanasqlite.disnana.com/guide#lesson-10-キャッシュ戦略))
- **データ暗号化**: AES-GCM / ChaCha20 / Fernet ([ドキュメント](https://nanasqlite.disnana.com/guide#lesson-11-暗号化))
- **永続化 TTL**: SQLite上のデータの自動消去。

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

**[セキュリティ詳細を見る ↗](https://nanasqlite.disnana.com/guide#_2-強力なセキュリティ-v1-2-0-)**

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

**オプションのデータ暗号化 (v1.3.1a1+):**

```python
from nanasqlite import NanaSQLite

# 事前にインストール: pip install nanasqlite[encryption]
db = NanaSQLite("secure.db", encryption_key=b"your-32-byte-key") # デフォルトで AES-GCM

# モードを明示的に指定する場合
db_chacha = NanaSQLite("secure_cc.db", 
    encryption_key=b"your-32-byte-key", 
    encryption_mode="chacha20"
)

# SQLite内では暗号化されますが、メモリ上（キャッシュ）では平文で高速に扱えます
db["secret"] = {"password": "123"}
```

**トランザクションサポートとエラーハンドリング (v1.1.0+):**

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

with db.transaction():
    db["key1"] = "value1"
    db["key2"] = "value2"
```

**[マルチテーブルと非同期を詳しく ↗](https://nanasqlite.disnana.com/guide#_4-トランザクションとマルチテーブル)**

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
