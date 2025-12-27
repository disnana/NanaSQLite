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

### Nested Contexts

```python
from nanasqlite import NanaSQLite

db = NanaSQLite("mydata.db")

# Outer transaction
with db.transaction():
    db["key1"] = "value1"
    
    # Inner transaction cannot be started (causes error)
    try:
        with db.transaction():  # NanaSQLiteTransactionError
            db["key2"] = "value2"
    except Exception as e:
        print(f"Nested transactions are not supported: {e}")
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

### Connection Close During Transaction

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

db = NanaSQLite("mydata.db")

try:
    db.begin_transaction()
    db["key"] = "value"
    db.close()  # Error! Inside transaction
except NanaSQLiteTransactionError as e:
    print(f"Error: {e}")
    db.rollback()
    db.close()
```

### Safe Error Handling

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
            # Look at some processing
            result = perform_operation()
            db.sql_insert("logs", {"message": f"Operation completed: {result}"})
            return result
    except NanaSQLiteError as e:
        # Transaction is automatically rolled back
        print(f"Transaction error: {e}")
        return None
    except Exception as e:
        # Other errors also trigger rollback
        print(f"Unexpected error: {e}")
        return None

def perform_operation():
    # Actual processing
    return "success"

result = safe_transaction()
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

### Transaction Size

When processing large amounts of data, splitting transactions into appropriate sizes is effective.

```python
from nanasqlite import NanaSQLite

db = NanaSQLite("large.db")
db.create_table("data", {"id": "INTEGER", "value": "TEXT"})

# Set batch size
BATCH_SIZE = 10000
total_records = 100000

for batch_start in range(0, total_records, BATCH_SIZE):
    with db.transaction():
        for i in range(batch_start, min(batch_start + BATCH_SIZE, total_records)):
            db.sql_insert("data", {"id": i, "value": f"data_{i}"})
    print(f"Processed {min(batch_start + BATCH_SIZE, total_records)}/{total_records}")
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

### 3. Cache Consistency

Modifying the database directly via `execute()` can cause cache inconsistency.

```python
db = NanaSQLite("mydata.db")
db["key"] = "old_value"

# Update via direct SQL
with db.transaction():
    db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new_value"', "key"))

# Refresh cache
db.refresh("key")  # Or db.get_fresh("key")
print(db["key"])  # "new_value"
```

### 4. Deadlocks

Deadlocks can occur if multiple processes start transactions in different orders.

```python
# Process 1
with db1.transaction():
    db1["key1"] = "value1"
    time.sleep(1)
    db1["key2"] = "value2"  # May be locked by Process 2

# Process 2
with db2.transaction():
    db2["key2"] = "value2"
    time.sleep(1)
    db2["key1"] = "value1"  # May be locked by Process 1
```

**Solution**: Always acquire locks in the same order, or use WAL mode.

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

### Notes on Concurrency

Even in async, a single database connection can only have one transaction at a time.

```python
import asyncio
from nanasqlite import AsyncNanaSQLite

async def main():
    async with AsyncNanaSQLite("mydata.db") as db:
        # ❌ This may cause error
        async def task1():
            async with db.transaction():
                await db.aset("key1", "value1")
                await asyncio.sleep(1)
        
        async def task2():
            async with db.transaction():  # During task1's transaction
                await db.aset("key2", "value2")
        
        # Concurrent execution causes error
        try:
            await asyncio.gather(task1(), task2())
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(main())
```

**Solution**: Use independent database connections for each task or serialize transactions.

---

## Practical Examples

### Example 1: Bank Account Transfer

```python
from nanasqlite import NanaSQLite, NanaSQLiteError

db = NanaSQLite("bank.db")
db.create_table("accounts", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT",
    "balance": "REAL"
})

def transfer(from_id: int, to_id: int, amount: float):
    """Transfer money between accounts"""
    try:
        with db.transaction():
            # Get sender balance
            from_account = db.query("accounts", where="id = ?", parameters=(from_id,))
            if not from_account:
                raise ValueError(f"Account {from_id} not found")
            
            from_balance = from_account[0]["balance"]
            if from_balance < amount:
                raise ValueError("Insufficient funds")
            
            # Withdraw from sender
            db.sql_update("accounts", 
                         {"balance": from_balance - amount}, 
                         "id = ?", 
                         (from_id,))
            
            # Get receiver balance
            to_account = db.query("accounts", where="id = ?", parameters=(to_id,))
            if not to_account:
                raise ValueError(f"Account {to_id} not found")
            
            to_balance = to_account[0]["balance"]
            
            # Deposit to receiver
            db.sql_update("accounts", 
                         {"balance": to_balance + amount}, 
                         "id = ?", 
                         (to_id,))
            
        print(f"Transfer complete: Account {from_id} -> Account {to_id}, Amount: {amount}")
        return True
        
    except NanaSQLiteError as e:
        print(f"Database error: {e}")
        return False
    except ValueError as e:
        print(f"Transfer error: {e}")
        return False

# Test
db.sql_insert("accounts", {"id": 1, "name": "Alice", "balance": 1000.0})
db.sql_insert("accounts", {"id": 2, "name": "Bob", "balance": 500.0})

transfer(1, 2, 100.0)  # Success
transfer(1, 2, 2000.0)  # Failed (limit exceeded)
```

### Example 2: Operation Logging

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
    """Decorator to log operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                with db.transaction():
                    # Start log
                    db.sql_insert("logs", {
                        "level": "INFO",
                        "message": f"{operation_name} started",
                        "timestamp": start_time.isoformat()
                    })
                    
                    # Actual logic
                    result = func(*args, **kwargs)
                    
                    # Completion log
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    db.sql_insert("logs", {
                        "level": "INFO",
                        "message": f"{operation_name} completed in {duration:.2f}s",
                        "timestamp": end_time.isoformat()
                    })
                    
                return result
                
            except Exception as e:
                # Error log
                error_time = datetime.now()
                db.sql_insert("logs", {
                    "level": "ERROR",
                    "message": f"{operation_name} failed: {e}",
                    "timestamp": error_time.isoformat()
                })
                raise
        
        return wrapper
    return decorator

@log_operation("Data Processing")
def process_data():
    # Some processing
    import time
    time.sleep(1)
    return "success"

process_data()
```

---

## Summary

- **Use context manager**: `with db.transaction():` for auto-management
- **Error handling**: Auto rollback on exception
- **Performance**: Speed up bulk writes with transactions
- **Limitations**: No nested transactions, avoid long-running transactions
- **Async support**: Same usage available with `AsyncNanaSQLite`

Properly using transactions enables fast database operations while maintaining data integrity.
