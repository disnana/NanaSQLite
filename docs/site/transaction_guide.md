# トランザクションガイド

NanaSQLiteは、SQLiteのトランザクション機能を簡単に使用できるAPIを提供しています。このガイドでは、トランザクションの基本から高度な使用方法まで解説します。

## 目次

1. [トランザクションとは](#トランザクションとは)
2. [基本的な使用方法](#基本的な使用方法)
3. [コンテキストマネージャ（推奨）](#コンテキストマネージャ推奨)
4. [トランザクションの挙動](#トランザクションの挙動)
5. [エラーハンドリング](#エラーハンドリング)
6. [パフォーマンス最適化](#パフォーマンス最適化)
7. [制限事項と注意点](#制限事項と注意点)
8. [非同期版のトランザクション](#非同期版のトランザクション)
9. [実践的な例](#実践的な例)

---

## トランザクションとは

トランザクションは、複数のデータベース操作を1つの論理的な単位としてまとめる機能です。トランザクションには以下の特性があります（ACID特性）：

- **Atomicity（原子性）**: すべての操作が成功するか、すべて失敗する
- **Consistency（一貫性）**: データベースは常に整合性のある状態を保つ
- **Isolation（独立性）**: 同時実行されるトランザクションは互いに影響しない
- **Durability（永続性）**: コミットされたデータは永続的に保存される

### トランザクションを使うべき場面

- 複数の関連する操作を一括で実行したい
- 操作の途中で失敗した場合、すべてをロールバックしたい
- データの一貫性を保証したい
- 大量のデータを高速に書き込みたい

---

## 基本的な使用方法

### 明示的なトランザクション制御

`begin_transaction()`, `commit()`, `rollback()`を使用して、トランザクションを明示的に制御できます。

```python
from nanasqlite import NanaSQLite

db = NanaSQLite("mydata.db")
db.create_table("accounts", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT",
    "balance": "REAL"
})

# トランザクション開始
db.begin_transaction()

try:
    # 複数の操作を実行
    db.sql_insert("accounts", {"id": 1, "name": "Alice", "balance": 1000.0})
    db.sql_insert("accounts", {"id": 2, "name": "Bob", "balance": 500.0})
    
    # 口座Aから口座Bへ送金
    db.sql_update("accounts", {"balance": 900.0}, "id = ?", (1,))
    db.sql_update("accounts", {"balance": 600.0}, "id = ?", (2,))
    
    # すべて成功したらコミット
    db.commit()
    print("送金が完了しました")
    
except Exception as e:
    # エラーが発生したらロールバック
    db.rollback()
    print(f"送金に失敗しました: {e}")
```

### トランザクション状態の確認

```python
db = NanaSQLite("mydata.db")

print(db.in_transaction())  # False

db.begin_transaction()
print(db.in_transaction())  # True

db.commit()
print(db.in_transaction())  # False
```

---

## コンテキストマネージャ（推奨）

コンテキストマネージャを使用すると、トランザクションの管理が自動化され、コードがシンプルになります。

### 基本的な使用

```python
from nanasqlite import NanaSQLite

db = NanaSQLite("mydata.db")
db.create_table("users", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT",
    "email": "TEXT"
})

# コンテキストマネージャで自動管理
with db.transaction():
    db.sql_insert("users", {"id": 1, "name": "Alice", "email": "alice@example.com"})
    db.sql_insert("users", {"id": 2, "name": "Bob", "email": "bob@example.com"})
    # ブロックを抜けると自動的にコミット

print("ユーザーが追加されました")
```

### 例外時の自動ロールバック

コンテキストマネージャ内で例外が発生すると、自動的にロールバックされます。

```python
from nanasqlite import NanaSQLite

db = NanaSQLite("mydata.db")
db.create_table("products", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT",
    "price": "REAL"
})

try:
    with db.transaction():
        db.sql_insert("products", {"id": 1, "name": "Laptop", "price": 999.99})
        db.sql_insert("products", {"id": 2, "name": "Mouse", "price": 19.99})
        
        # 意図的にエラーを発生させる（重複キー）
        db.sql_insert("products", {"id": 1, "name": "Duplicate", "price": 0.0})
        
except Exception as e:
    print(f"エラーが発生しました: {e}")
    # トランザクションは自動的にロールバックされている

# 最初の2件も含めてロールバックされているため、テーブルは空
print(f"商品数: {db.count('products')}")  # 0
```

### ネストしたコンテキスト

```python
from nanasqlite import NanaSQLite

db = NanaSQLite("mydata.db")

# 外側のトランザクション
with db.transaction():
    db["key1"] = "value1"
    
    # 内側のトランザクションは開始できない（エラーになる）
    try:
        with db.transaction():  # NanaSQLiteTransactionError
            db["key2"] = "value2"
    except Exception as e:
        print(f"ネストしたトランザクションはサポートされていません: {e}")
```

---

## トランザクションの挙動

### デフォルトの自動コミット

トランザクションを使用しない場合、各操作は自動的にコミットされます（auto-commit mode）。

```python
db = NanaSQLite("mydata.db")

# これらは個別にコミットされる
db["key1"] = "value1"  # 自動コミット
db["key2"] = "value2"  # 自動コミット
db["key3"] = "value3"  # 自動コミット
```

### トランザクションモード

NanaSQLiteは`BEGIN IMMEDIATE`を使用します。これにより：

- トランザクション開始時に書き込みロックを取得
- 他のプロセスからの読み込みは可能
- 他のプロセスからの書き込みはブロックされる

```python
db = NanaSQLite("mydata.db")

db.begin_transaction()  # BEGIN IMMEDIATE を実行
# 書き込みロックが取得される
db["key"] = "value"
db.commit()
```

### WALモードとの組み合わせ

NanaSQLiteはデフォルトでWAL（Write-Ahead Logging）モードを使用します。これにより：

- 読み込みと書き込みが並行して実行可能
- トランザクションのパフォーマンスが向上
- データベースロックが減少

```python
db = NanaSQLite("mydata.db", optimize=True)  # WALモード有効（デフォルト）

# WALモードの確認
mode = db.pragma("journal_mode")
print(f"Journal mode: {mode}")  # "wal"
```

---

## エラーハンドリング

### トランザクション関連の例外

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

db = NanaSQLite("mydata.db")

# 1. ネストしたトランザクション
try:
    db.begin_transaction()
    db.begin_transaction()  # エラー！
except NanaSQLiteTransactionError as e:
    print(f"エラー: {e}")
    db.rollback()

# 2. トランザクション外でのコミット
try:
    db.commit()  # トランザクションが開始されていない
except NanaSQLiteTransactionError as e:
    print(f"エラー: {e}")

# 3. トランザクション外でのロールバック
try:
    db.rollback()  # トランザクションが開始されていない
except NanaSQLiteTransactionError as e:
    print(f"エラー: {e}")
```

### トランザクション中の接続クローズ

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

db = NanaSQLite("mydata.db")

try:
    db.begin_transaction()
    db["key"] = "value"
    db.close()  # エラー！トランザクション中
except NanaSQLiteTransactionError as e:
    print(f"エラー: {e}")
    db.rollback()
    db.close()
```

### 安全なエラーハンドリング

```python
from nanasqlite import NanaSQLite, NanaSQLiteError

db = NanaSQLite("mydata.db")
db.create_table("logs", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "message": "TEXT",
    "timestamp": "TEXT"
})

def safe_transaction():
    try:
        with db.transaction():
            db.sql_insert("logs", {"message": "Operation started"})
            # 何らかの処理
            result = perform_operation()
            db.sql_insert("logs", {"message": f"Operation completed: {result}"})
            return result
    except NanaSQLiteError as e:
        # トランザクションは自動的にロールバック
        print(f"トランザクションエラー: {e}")
        return None
    except Exception as e:
        # その他のエラーもロールバック
        print(f"予期しないエラー: {e}")
        return None

def perform_operation():
    # 実際の処理
    return "success"

result = safe_transaction()
```

---

## パフォーマンス最適化

### トランザクションによる高速化

トランザクションを使用すると、大量の書き込みが劇的に高速化されます。

```python
import time
from nanasqlite import NanaSQLite

db = NanaSQLite("test.db")
db.create_table("items", {"id": "INTEGER", "value": "TEXT"})

# トランザクションなし（遅い）
start = time.time()
for i in range(1000):
    db.sql_insert("items", {"id": i, "value": f"item_{i}"})
elapsed_without = time.time() - start
print(f"トランザクションなし: {elapsed_without:.2f}秒")

db.clear()

# トランザクションあり（速い）
start = time.time()
with db.transaction():
    for i in range(1000):
        db.sql_insert("items", {"id": i, "value": f"item_{i}"})
elapsed_with = time.time() - start
print(f"トランザクションあり: {elapsed_with:.2f}秒")

print(f"速度向上: {elapsed_without / elapsed_with:.1f}倍")
```

### バッチ操作との組み合わせ

`batch_update()`は内部的にトランザクションを使用しているため、さらに高速です。

```python
from nanasqlite import NanaSQLite

db = NanaSQLite("test.db")

# 方法1: トランザクション + ループ（速い）
with db.transaction():
    for i in range(10000):
        db[f"key_{i}"] = f"value_{i}"

# 方法2: batch_update（さらに速い）
data = {f"key_{i}": f"value_{i}" for i in range(10000)}
db.batch_update(data)
```

### トランザクションのサイズ

大量のデータを処理する場合、トランザクションを適切なサイズに分割すると効果的です。

```python
from nanasqlite import NanaSQLite

db = NanaSQLite("large.db")
db.create_table("data", {"id": "INTEGER", "value": "TEXT"})

# バッチサイズを設定
BATCH_SIZE = 10000
total_records = 100000

for batch_start in range(0, total_records, BATCH_SIZE):
    with db.transaction():
        for i in range(batch_start, min(batch_start + BATCH_SIZE, total_records)):
            db.sql_insert("data", {"id": i, "value": f"data_{i}"})
    print(f"Processed {min(batch_start + BATCH_SIZE, total_records)}/{total_records}")
```

---

## 制限事項と注意点

### 1. ネストしたトランザクション

SQLiteはネストしたトランザクションをサポートしていません。

```python
db = NanaSQLite("mydata.db")

# ❌ これはエラーになる
db.begin_transaction()
db.begin_transaction()  # NanaSQLiteTransactionError

# ✅ トランザクション状態を確認
if not db.in_transaction():
    db.begin_transaction()
```

### 2. 長時間のトランザクション

長時間実行されるトランザクションは避けるべきです：

- データベースロックが長時間保持される
- 他のプロセスがブロックされる
- WALファイルが肥大化する

```python
# ❌ 避けるべき
with db.transaction():
    for i in range(1000000):
        db.sql_insert("items", {"id": i, "value": f"item_{i}"})
        time.sleep(0.01)  # 長時間実行

# ✅ バッチ処理に分割
BATCH_SIZE = 10000
for batch in range(0, 1000000, BATCH_SIZE):
    with db.transaction():
        for i in range(batch, batch + BATCH_SIZE):
            db.sql_insert("items", {"id": i, "value": f"item_{i}"})
```

### 3. キャッシュの一貫性

`execute()`でデータベースを直接変更した場合、キャッシュと不整合が生じる可能性があります。

```python
db = NanaSQLite("mydata.db")
db["key"] = "old_value"

# 直接SQLで更新
with db.transaction():
    db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new_value"', "key"))

# キャッシュを更新
db.refresh("key")  # または db.get_fresh("key")
print(db["key"])  # "new_value"
```

### 4. デッドロック

複数のプロセスが異なる順序でトランザクションを開始すると、デッドロックが発生する可能性があります。

```python
# プロセス1
with db1.transaction():
    db1["key1"] = "value1"
    time.sleep(1)
    db1["key2"] = "value2"  # プロセス2がロック中かもしれない

# プロセス2
with db2.transaction():
    db2["key2"] = "value2"
    time.sleep(1)
    db2["key1"] = "value1"  # プロセス1がロック中かもしれない
```

**解決策**: 常に同じ順序でロックを取得する、またはWALモードを使用する。

---

## 非同期版のトランザクション

`AsyncNanaSQLite`でもトランザクションをサポートしています。

### 基本的な使用

```python
import asyncio
from nanasqlite import AsyncNanaSQLite

async def main():
    async with AsyncNanaSQLite("mydata.db") as db:
        # コンテキストマネージャ
        async with db.transaction():
            await db.aset("key1", "value1")
            await db.aset("key2", "value2")
            # 自動的にコミット
        
        print("トランザクション完了")

asyncio.run(main())
```

### 明示的な制御

```python
import asyncio
from nanasqlite import AsyncNanaSQLite

async def main():
    async with AsyncNanaSQLite("mydata.db") as db:
        await db.begin_transaction()
        
        try:
            await db.aset("key1", "value1")
            await db.aset("key2", "value2")
            await db.commit()
        except Exception as e:
            await db.rollback()
            print(f"エラー: {e}")

asyncio.run(main())
```

### トランザクション状態の確認

```python
import asyncio
from nanasqlite import AsyncNanaSQLite

async def main():
    async with AsyncNanaSQLite("mydata.db") as db:
        print(await db.in_transaction())  # False
        
        await db.begin_transaction()
        print(await db.in_transaction())  # True
        
        await db.commit()
        print(await db.in_transaction())  # False

asyncio.run(main())
```

### 並行処理での注意点

非同期版でも、同じデータベース接続では1つのトランザクションしか実行できません。

```python
import asyncio
from nanasqlite import AsyncNanaSQLite

async def main():
    async with AsyncNanaSQLite("mydata.db") as db:
        # ❌ これはエラーになる可能性がある
        async def task1():
            async with db.transaction():
                await db.aset("key1", "value1")
                await asyncio.sleep(1)
        
        async def task2():
            async with db.transaction():  # task1のトランザクション中
                await db.aset("key2", "value2")
        
        # 同時実行はエラーになる
        try:
            await asyncio.gather(task1(), task2())
        except Exception as e:
            print(f"エラー: {e}")

asyncio.run(main())
```

**解決策**: 各タスクで独立したデータベース接続を使用する、またはトランザクションを直列化する。

---

## 実践的な例

### 例1: 銀行口座の送金

```python
from nanasqlite import NanaSQLite, NanaSQLiteError

db = NanaSQLite("bank.db")
db.create_table("accounts", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT",
    "balance": "REAL"
})

def transfer(from_id: int, to_id: int, amount: float):
    """口座間で送金を行う"""
    try:
        with db.transaction():
            # 送金元の残高を取得
            from_account = db.query("accounts", where="id = ?", parameters=(from_id,))
            if not from_account:
                raise ValueError(f"口座 {from_id} が見つかりません")
            
            from_balance = from_account[0]["balance"]
            if from_balance < amount:
                raise ValueError("残高不足です")
            
            # 送金元から引き出し
            db.sql_update("accounts", 
                         {"balance": from_balance - amount}, 
                         "id = ?", 
                         (from_id,))
            
            # 送金先の残高を取得
            to_account = db.query("accounts", where="id = ?", parameters=(to_id,))
            if not to_account:
                raise ValueError(f"口座 {to_id} が見つかりません")
            
            to_balance = to_account[0]["balance"]
            
            # 送金先に入金
            db.sql_update("accounts", 
                         {"balance": to_balance + amount}, 
                         "id = ?", 
                         (to_id,))
            
        print(f"送金完了: 口座{from_id} → 口座{to_id}, 金額: {amount}")
        return True
        
    except NanaSQLiteError as e:
        print(f"データベースエラー: {e}")
        return False
    except ValueError as e:
        print(f"送金エラー: {e}")
        return False

# テスト
db.sql_insert("accounts", {"id": 1, "name": "Alice", "balance": 1000.0})
db.sql_insert("accounts", {"id": 2, "name": "Bob", "balance": 500.0})

transfer(1, 2, 100.0)  # 成功
transfer(1, 2, 2000.0)  # 失敗（残高不足）
```

### 例2: ログの記録

```python
from nanasqlite import NanaSQLite
from datetime import datetime

db = NanaSQLite("logs.db")
db.create_table("logs", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "level": "TEXT",
    "message": "TEXT",
    "timestamp": "TEXT"
})

def log_operation(operation_name: str):
    """操作のログを記録するデコレータ"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                with db.transaction():
                    # 開始ログ
                    db.sql_insert("logs", {
                        "level": "INFO",
                        "message": f"{operation_name} started",
                        "timestamp": start_time.isoformat()
                    })
                    
                    # 実際の処理
                    result = func(*args, **kwargs)
                    
                    # 完了ログ
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    db.sql_insert("logs", {
                        "level": "INFO",
                        "message": f"{operation_name} completed in {duration:.2f}s",
                        "timestamp": end_time.isoformat()
                    })
                    
                return result
                
            except Exception as e:
                # エラーログ
                error_time = datetime.now()
                db.sql_insert("logs", {
                    "level": "ERROR",
                    "message": f"{operation_name} failed: {e}",
                    "timestamp": error_time.isoformat()
                })
                raise
        
        return wrapper
    return decorator

@log_operation("データ処理")
def process_data():
    # 何らかの処理
    import time
    time.sleep(1)
    return "success"

process_data()
```

---

## まとめ

- **コンテキストマネージャを使用**: `with db.transaction():`で自動管理
- **エラーハンドリング**: 例外が発生すると自動的にロールバック
- **パフォーマンス**: トランザクションで大量の書き込みを高速化
- **制限事項**: ネストしたトランザクションは不可、長時間のトランザクションは避ける
- **非同期対応**: `AsyncNanaSQLite`でも同様に使用可能

適切にトランザクションを使用することで、データの整合性を保ちながら高速なデータベース操作が可能になります。

