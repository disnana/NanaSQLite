# Transaction Guide

NanaSQLite provides an easy-to-use API for SQLite transaction functionality. This guide covers everything from basics to advanced usage of transactions.

## Table of Contents

1. [What are Transactions?](#what-are-transactions)
2. [Basic Usage](#basic-usage)
3. [Context Manager (Recommended)](#context-manager-recommended)
4. [Transaction Behavior](#transaction-behavior)
5. [Error Handling](#error-handling)
6. [Performance Optimization](#performance-optimization)
7. [Limitations and Notes](#limitations-and-notes)
8. [Async Transactions](#async-transactions)

---

## What are Transactions?

Transactions combine multiple database operations into a single logical unit. Transactions have ACID properties:

- **Atomicity**: All operations succeed or all fail
- **Consistency**: Database maintains a consistent state
- **Isolation**: Concurrent transactions don't affect each other
- **Durability**: Committed data is permanently saved

### When to Use Transactions

- Execute multiple related operations together
- Rollback everything if an operation fails midway
- Guarantee data consistency
- Write large amounts of data quickly

---

## Basic Usage

### Explicit Transaction Control

Use `begin_transaction()`, `commit()`, and `rollback()` to explicitly control transactions.

```python
from nanasqlite import NanaSQLite

db = NanaSQLite("mydata.db")
db.create_table("accounts", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT",
    "balance": "REAL"
})

# Begin transaction
db.begin_transaction()

try:
    # Execute multiple operations
    db.sql_insert("accounts", {"id": 1, "name": "Alice", "balance": 1000.0})
    db.sql_insert("accounts", {"id": 2, "name": "Bob", "balance": 500.0})
    
    # Transfer from account A to B
    db.sql_update("accounts", {"balance": 900.0}, "id = ?", (1,))
    db.sql_update("accounts", {"balance": 600.0}, "id = ?", (2,))
    
    # Commit on success
    db.commit()
    print("Transfer completed")
    
except Exception as e:
    # Rollback on error
    db.rollback()
    print(f"Transfer failed: {e}")
```

### Check Transaction State

```python
db = NanaSQLite("mydata.db")

print(db.in_transaction())  # False

db.begin_transaction()
print(db.in_transaction())  # True

db.commit()
print(db.in_transaction())  # False
```

---

## Context Manager (Recommended)

Using a context manager automates transaction management and simplifies code.

### Basic Usage

```python
from nanasqlite import NanaSQLite

db = NanaSQLite("mydata.db")
db.create_table("users", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT",
    "email": "TEXT"
})

# Auto-managed with context manager
with db.transaction():
    db.sql_insert("users", {"id": 1, "name": "Alice", "email": "alice@example.com"})
    db.sql_insert("users", {"id": 2, "name": "Bob", "email": "bob@example.com"})
    # Auto commit when exiting block

print("Users added")
```

### Automatic Rollback on Exception

If an exception occurs within the context manager, it automatically rolls back.

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
        
        # Intentionally cause error (duplicate key)
        db.sql_insert("products", {"id": 1, "name": "Duplicate", "price": 0.0})
        
except Exception as e:
    print(f"Error occurred: {e}")
    # Transaction automatically rolled back

# First 2 items also rolled back, table is empty
print(f"Product count: {db.count('products')}")  # 0
```

---

## Transaction Behavior

### Default Auto-Commit

Without transactions, each operation is automatically committed (auto-commit mode).

```python
db = NanaSQLite("mydata.db")

# Each is individually committed
db["key1"] = "value1"  # Auto commit
db["key2"] = "value2"  # Auto commit
db["key3"] = "value3"  # Auto commit
```

### Transaction Mode

NanaSQLite uses `BEGIN IMMEDIATE`, which:

- Acquires write lock when transaction begins
- Allows reads from other processes
- Blocks writes from other processes

```python
db = NanaSQLite("mydata.db")

db.begin_transaction()  # Executes BEGIN IMMEDIATE
# Write lock acquired
db["key"] = "value"
db.commit()
```

### Combined with WAL Mode

NanaSQLite uses WAL (Write-Ahead Logging) mode by default, which:

- Enables concurrent reads and writes
- Improves transaction performance
- Reduces database locks

```python
db = NanaSQLite("mydata.db", optimize=True)  # WAL mode enabled (default)

# Verify WAL mode
mode = db.pragma("journal_mode")
print(f"Journal mode: {mode}")  # "wal"
```

---

## Error Handling

### Transaction-Related Exceptions

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

db = NanaSQLite("mydata.db")

# 1. Nested transaction
try:
    db.begin_transaction()
    db.begin_transaction()  # Error!
except NanaSQLiteTransactionError as e:
    print(f"Error: {e}")
    db.rollback()

# 2. Commit outside transaction
try:
    db.commit()  # No transaction started
except NanaSQLiteTransactionError as e:
    print(f"Error: {e}")

# 3. Rollback outside transaction
try:
    db.rollback()  # No transaction started
except NanaSQLiteTransactionError as e:
    print(f"Error: {e}")
```

---

## Performance Optimization

### Speed-up with Transactions

Using transactions dramatically speeds up bulk writes.

```python
import time
from nanasqlite import NanaSQLite

db = NanaSQLite("test.db")
db.create_table("items", {"id": "INTEGER", "value": "TEXT"})

# Without transaction (slow)
start = time.time()
for i in range(1000):
    db.sql_insert("items", {"id": i, "value": f"item_{i}"})
elapsed_without = time.time() - start
print(f"Without transaction: {elapsed_without:.2f}s")

db.clear()

# With transaction (fast)
start = time.time()
with db.transaction():
    for i in range(1000):
        db.sql_insert("items", {"id": i, "value": f"item_{i}"})
elapsed_with = time.time() - start
print(f"With transaction: {elapsed_with:.2f}s")

print(f"Speed improvement: {elapsed_without / elapsed_with:.1f}x")
```

### Combined with Batch Operations

`batch_update()` internally uses transactions, making it even faster.

```python
from nanasqlite import NanaSQLite

db = NanaSQLite("test.db")

# Method 1: Transaction + loop (fast)
with db.transaction():
    for i in range(10000):
        db[f"key_{i}"] = f"value_{i}"

# Method 2: batch_update (even faster)
data = {f"key_{i}": f"value_{i}" for i in range(10000)}
db.batch_update(data)
```

---

## Limitations and Notes

### 1. Nested Transactions

SQLite doesn't support nested transactions.

```python
db = NanaSQLite("mydata.db")

# ❌ This causes error
db.begin_transaction()
db.begin_transaction()  # NanaSQLiteTransactionError

# ✅ Check transaction state
if not db.in_transaction():
    db.begin_transaction()
```

### 2. Long-Running Transactions

Avoid long-running transactions:

- Database lock held for extended period
- Other processes get blocked
- WAL file grows large

```python
# ❌ Avoid
with db.transaction():
    for i in range(1000000):
        db.sql_insert("items", {"id": i, "value": f"item_{i}"})
        time.sleep(0.01)  # Long execution

# ✅ Split into batches
BATCH_SIZE = 10000
for batch in range(0, 1000000, BATCH_SIZE):
    with db.transaction():
        for i in range(batch, batch + BATCH_SIZE):
            db.sql_insert("items", {"id": i, "value": f"item_{i}"})
```

---

## Async Transactions

`AsyncNanaSQLite` also supports transactions.

### Basic Usage

```python
import asyncio
from nanasqlite import AsyncNanaSQLite

async def main():
    async with AsyncNanaSQLite("mydata.db") as db:
        # Context manager
        async with db.transaction():
            await db.aset("key1", "value1")
            await db.aset("key2", "value2")
            # Auto commit
        
        print("Transaction complete")

asyncio.run(main())
```

### Explicit Control

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
            print(f"Error: {e}")

asyncio.run(main())
```

### Check Transaction State

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

---

## Summary

- **Use context manager**: `with db.transaction():` for auto-management
- **Error handling**: Auto rollback on exception
- **Performance**: Speed up bulk writes with transactions
- **Limitations**: No nested transactions, avoid long-running transactions
- **Async support**: Same usage available with `AsyncNanaSQLite`

Properly using transactions enables fast database operations while maintaining data integrity.

