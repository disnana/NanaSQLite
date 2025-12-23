# NanaSQLite

[![PyPI version](https://img.shields.io/pypi/v/nanasqlite.svg)](https://pypi.org/project/nanasqlite/)
[![Python versions](https://img.shields.io/pypi/pyversions/nanasqlite.svg)](https://pypi.org/project/nanasqlite/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/nanasqlite)](https://pepy.tech/project/nanasqlite)
[![Tests](https://github.com/disnana/nanasqlite/actions/workflows/test.yml/badge.svg)](https://github.com/disnana/nanasqlite/actions/workflows/test.yml)

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
- [Migration Guide (v1.1.x to v1.2.0)](MIGRATION_GUIDE.md)
- [Development Guide](DEVELOPMENT_GUIDE.md)

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

# Thread-safe concurrent writes to different tables
from concurrent.futures import ThreadPoolExecutor

def write_users(i):
    main_db[f"user{i}"] = {"name": f"User{i}"}

def write_products(i):
    products_db[f"prod{i}"] = {"name": f"Product{i}"}

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(write_users, range(100))
    executor.map(write_products, range(100))

# Close only the main instance (closes shared connection)
main_db.close()
```

**Key features:**
- **Shared connection & lock**: All table instances share the same SQLite connection and thread lock
- **Thread-safe**: Concurrent writes to different tables are safely synchronized
- **Memory efficient**: Reuses connections instead of creating new ones
- **Isolated cache**: Each table maintains its own memory cache
- **Works with async**: `await db.table("table_name")` for AsyncNanaSQLite

**⚠️ Important Usage Notes:**

1. **Do not create multiple instances for the same table:**
   ```python
   # ❌ Not recommended: Causes cache inconsistency
   users1 = db.table("users")
   users2 = db.table("users")  # Different cache, same DB table!
   
   # ✅ Recommended: Reuse the same instance
   users_db = db.table("users")
   # Use users_db throughout your code
   ```

2. **Use context managers to avoid issues after close:**
   ```python
   # ✅ Recommended: Proper cleanup with context manager
   with NanaSQLite("app.db", table="main") as main_db:
       sub_db = main_db.table("sub")
       sub_db["key"] = "value"
   # Automatically closed, no orphaned instances
   ```

3. **About chained table() calls:**
   ```python
   # ✅ Works: sub2 is created as a child of sub
   sub = db.table("sub")
   sub2 = sub.table("sub2")  # Creates sub2 table
   
   # ✅ More recommended: Get directly from parent
   sub = db.table("sub")
   sub2 = db.table("sub2")  # Clearer parent-child relationship
   ```

**Best Practices:**
- Store table instances in variables and reuse them
- Prefer context managers (`with` statement) for automatic resource management
- Close the parent instance when done (child instances share the same connection)

### ✨ Transaction Support & Error Handling (v1.1.0+)

**Enhanced transaction management with proper error handling:**

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

db = NanaSQLite("mydata.db")

# Context manager (recommended - auto commit/rollback)
with db.transaction():
    db["key1"] = "value1"
    db["key2"] = "value2"
    # Automatically commits on success, rolls back on exception

# Manual transaction control
db.begin_transaction()
try:
    db.sql_insert("users", {"name": "Alice"})
    db.sql_insert("users", {"name": "Bob"})
    db.commit()
except Exception:
    db.rollback()

# Check transaction state
if not db.in_transaction():
    db.begin_transaction()
```

**Custom exceptions for better error handling:**

```python
from nanasqlite import (
    NanaSQLiteError,           # Base exception
    NanaSQLiteValidationError, # Invalid input/parameters
    NanaSQLiteDatabaseError,   # Database operation errors
    NanaSQLiteTransactionError,# Transaction-related errors
    NanaSQLiteConnectionError, # Connection errors
)

try:
    db = NanaSQLite("mydata.db")
    db.begin_transaction()
    # Nested transactions are not supported
    db.begin_transaction()  # Raises NanaSQLiteTransactionError
except NanaSQLiteTransactionError as e:
    print(f"Transaction error: {e}")
```

**⚠️ Important Usage Notes:**

1. **Do not create multiple instances for the same table:**
   ```python
   # ❌ BAD: Creates cache inconsistency
   users1 = db.table("users")
   users2 = db.table("users")  # Different cache, same DB table!
   
   # ✅ GOOD: Reuse the same instance
   users_db = db.table("users")
   # Use users_db throughout your code
   ```
   
   Each instance has its own independent cache. Multiple instances of the same table can lead to cache inconsistency at the memory level (though database writes remain correct).

2. **Use context managers to avoid issues after close:**
   ```python
   # ✅ RECOMMENDED: Context manager ensures proper cleanup
   with NanaSQLite("app.db", table="main") as main_db:
       sub_db = main_db.table("sub")
       sub_db["key"] = "value"
   # Automatically closed, no orphaned instances
   
   # ❌ AVOID: Manual close can leave orphaned sub-instances
   main_db = NanaSQLite("app.db")
   sub_db = main_db.table("sub")
   main_db.close()  # sub_db may still access cached data
   ```

**Best practices:**
- Store table instances in variables and reuse them
- Prefer context managers (`with` statement) for automatic resource management
- Close the parent instance when done; child instances share the same connection

### ✨ Async Support (v1.0.3rc7+)

**Full async/await support with optimized thread pool for high-performance non-blocking operations:**

```python
import asyncio
from nanasqlite import AsyncNanaSQLite

async def main():
    # Use async context manager with optimized thread pool
    async with AsyncNanaSQLite("mydata.db", max_workers=10) as db:
        # Async dict-like operations
        await db.aset("user", {"name": "Nana", "age": 20})
        user = await db.aget("user")
        print(user)  # {'name': 'Nana', 'age': 20}
        
        # Async batch operations
        await db.batch_update({
            "key1": "value1",
            "key2": "value2",
            "key3": {"nested": "data"}
        })
        
        # Concurrent operations (high-performance with thread pool)
        results = await asyncio.gather(
            db.aget("key1"),
            db.aget("key2"),
            db.aget("key3")
        )
        
        # Async SQL execution
        await db.create_table("users", {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT",
            "age": "INTEGER"
        })
        await db.sql_insert("users", {"name": "Alice", "age": 25})
        users = await db.query("users", where="age > ?", parameters=(20,))
        
        # Multi-table support in async
        products_db = await db.table("products")
        await products_db.aset("prod1", {"name": "Laptop", "price": 999})
        
        # Async transaction support (v1.1.0+)
        async with db.transaction():
            await db.sql_insert("users", {"name": "Bob", "age": 30})
            await db.sql_insert("users", {"name": "Charlie", "age": 35})
            # Auto commit on success, rollback on exception

        # Batch retrieval (v1.1.0+)
        results = await db.abatch_get(["key1", "key2"])
        
asyncio.run(main())
```

**Performance optimizations:**
- Dedicated thread pool executor (configurable with `max_workers`)
- APSW-based for maximum SQLite performance
- WAL mode and connection optimizations
- Ideal for high-concurrency scenarios

**Perfect for async frameworks:**
- FastAPI, Quart, Sanic (async web frameworks)
- aiohttp (async HTTP client/server)
- Discord.py, Telegram bots (async bots)
- Any asyncio-based application
### ✨ v1.2.0 New Features

**Security Enhancements & Strict Connection Management:**

```python
# v1.2.0 Security Features
db = NanaSQLite("mydata.db", 
    strict_sql_validation=True,  # Disallow unauthorized SQL functions
    max_clause_length=500        # Limit SQL length to prevent ReDoS
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
- [移行ガイド (v1.1.x から v1.2.0)](MIGRATION_GUIDE.md)
- [開発ガイド](DEVELOPMENT_GUIDE.md)

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
main_db["user1"] = {"name": "Alice", "email": "alice@example.com"}
products_db["prod1"] = {"name": "Laptop", "price": 999}
orders_db["order1"] = {"user": "user1", "product": "prod1"}

# 異なるテーブルへのスレッドセーフな並行書き込み
from concurrent.futures import ThreadPoolExecutor

def write_users(i):
    main_db[f"user{i}"] = {"name": f"User{i}"}

def write_products(i):
    products_db[f"prod{i}"] = {"name": f"Product{i}"}

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(write_users, range(100))
    executor.map(write_products, range(100))

# メインインスタンスのみをクローズ（共有接続を閉じる）
main_db.close()
```

**主な特徴:**
- **接続とロックの共有**: 全てのテーブルインスタンスが同じSQLite接続とスレッドロックを共有
- **スレッドセーフ**: 異なるテーブルへの並行書き込みが安全に同期される
- **メモリ効率**: 新しい接続を作成せず、既存の接続を再利用
- **キャッシュ分離**: 各テーブルは独自のメモリキャッシュを保持
- **非同期対応**: AsyncNanaSQLiteでは `await db.table("table_name")` で使用可能

**⚠️ 重要な使用上の注意:**

1. **同じテーブルに対して複数のインスタンスを作成しないでください:**
   ```python
   # ❌ 非推奨: キャッシュ不整合を引き起こす
   users1 = db.table("users")
   users2 = db.table("users")  # 異なるキャッシュ、同じDBテーブル！
   
   # ✅ 推奨: 同じインスタンスを再利用
   users_db = db.table("users")
   # コード全体でusers_dbを使用する
   ```
   
   各インスタンスは独立したキャッシュを持ちます。同じテーブルに対して複数のインスタンスを作成すると、メモリレベルでのキャッシュ不整合が発生する可能性があります（ただし、データベースへの書き込みは正しく行われます）。

2. **close後の問題を避けるため、コンテキストマネージャを使用してください:**
   ```python
   # ✅ 推奨: コンテキストマネージャで適切にクリーンアップ
   with NanaSQLite("app.db", table="main") as main_db:
       sub_db = main_db.table("sub")
       sub_db["key"] = "value"
   # 自動的にクローズされ、孤立したインスタンスなし
   
   # ❌ 非推奨: 手動closeは孤立したサブインスタンスを残す可能性
   main_db = NanaSQLite("app.db")
   sub_db = main_db.table("sub")
   main_db.close()  # sub_dbはまだキャッシュデータにアクセスできる
   ```

3. **table()のチェーン呼び出しについて:**
   ```python
   # ✅ 動作します: sub2はsubの子として作成される
   sub = db.table("sub")
   sub2 = sub.table("sub2")  # sub2テーブルが作成される
   
   # ✅ より推奨: 親から直接取得
   sub = db.table("sub")
   sub2 = db.table("sub2")  # より明確な親子関係
   ```
   
   `table().table()`のチェーンは技術的には動作しますが、以下の点に注意：
   - すべてのインスタンスは同じ接続を共有するため安全です
   - `sub2`は`sub`の子として追跡されますが、実際には別のテーブルです
   - より明確なコードのため、ルートDBから直接テーブルを取得することを推奨

**ベストプラクティス:**
- テーブルインスタンスを変数に保存して再利用する
- 自動リソース管理のためコンテキストマネージャ（`with`文）を優先する
- 完了時は親インスタンスをクローズする（子インスタンスは同じ接続を共有）

### ✨ トランザクションサポートとエラーハンドリング (v1.1.0+)

**適切なエラーハンドリング機能を備えた強化されたトランザクション管理:**

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

db = NanaSQLite("mydata.db")

# コンテキストマネージャ（推奨 - 自動コミット/ロールバック）
with db.transaction():
    db["key1"] = "value1"
    db["key2"] = "value2"
    # 成功時は自動コミット、例外発生時は自動ロールバック

# 手動トランザクション制御
db.begin_transaction()
try:
    db.sql_insert("users", {"name": "Alice"})
    db.sql_insert("users", {"name": "Bob"})
    db.commit()
except Exception:
    db.rollback()

# トランザクション状態の確認
if not db.in_transaction():
    db.begin_transaction()
```

**より良いエラーハンドリングのためのカスタム例外:**

```python
from nanasqlite import (
    NanaSQLiteError,           # 基底例外
    NanaSQLiteValidationError, # 不正な入力/パラメータ
    NanaSQLiteDatabaseError,   # データベース操作エラー
    NanaSQLiteTransactionError,# トランザクション関連エラー
    NanaSQLiteConnectionError, # 接続エラー
)

try:
    db = NanaSQLite("mydata.db")
    db.begin_transaction()
    # ネストしたトランザクションはサポートされていません
    db.begin_transaction()  # NanaSQLiteTransactionErrorを発生
except NanaSQLiteTransactionError as e:
    print(f"トランザクションエラー: {e}")
```

### ✨ 非同期サポート (v1.0.3rc7+)

**高速化されたスレッドプールによる完全な async/await サポート:**

```python
import asyncio
from nanasqlite import AsyncNanaSQLite

async def main():
    # 最適化されたスレッドプールで非同期コンテキストマネージャを使用
    async with AsyncNanaSQLite("mydata.db", max_workers=10) as db:
        # 非同期dict風操作
        await db.aset("user", {"name": "Nana", "age": 20})
        user = await db.aget("user")
        print(user)  # {'name': 'Nana', 'age': 20}
        
        # 非同期バッチ操作
        await db.batch_update({
            "key1": "value1",
            "key2": "value2",
            "key3": {"nested": "data"}
        })
        
        # 並行操作（スレッドプールにより高性能）
        results = await asyncio.gather(
            db.aget("key1"),
            db.aget("key2"),
            db.aget("key3")
        )
        
        # 非同期SQL実行
        await db.create_table("users", {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT",
            "age": "INTEGER"
        })
        await db.sql_insert("users", {"name": "Alice", "age": 25})
        users = await db.query("users", where="age > ?", parameters=(20,))
        
        # 非同期でのマルチテーブルサポート
        products_db = await db.table("products")
        await products_db.aset("prod1", {"name": "Laptop", "price": 999})
        
        # 非同期トランザクションサポート (v1.1.0+)
        async with db.transaction():
            await db.sql_insert("users", {"name": "Bob", "age": 30})
            await db.sql_insert("users", {"name": "Charlie", "age": 35})
            # 成功時は自動コミット、例外発生時は自動ロールバック

asyncio.run(main())
```

**パフォーマンス最適化:**
- 専用スレッドプールエグゼキューター（`max_workers`で設定可能）
- 高性能なAPSWベース
- WALモードと接続最適化
- 高並行性シナリオに最適

**非同期フレームワークに最適:**
- FastAPI, Quart, Sanic（非同期Webフレームワーク）
- aiohttp（非同期HTTP クライアント/サーバー）
- Discord.py, Telegramボット（非同期ボット）
- あらゆるasyncioベースのアプリケーション
### ✨ v1.2.0 新機能

**セキュリティ強化と厳格な接続管理:**

```python
# v1.2.0 セキュリティ機能
db = NanaSQLite("mydata.db", 
    strict_sql_validation=True,  # 未許可のSQL関数を禁止
    max_clause_length=500        # SQLの長さを制限してReDoSを防止
)

# 厳格な接続管理
with db.transaction():
    sub_db = db.table("sub")
    # ... 操作 ...
db.close()
# 無効化された sub_db へのアクセスは、安全のために NanaSQLiteClosedError を送出します。
```

**一貫性のある非同期API:**
```python
# AsyncNanaSQLiteの全てのメソッドに 'a' プレフィックス付きのエイリアスを追加
await db.abatch_update(data)
await db.abatch_get(keys)
await db.ato_dict()
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
