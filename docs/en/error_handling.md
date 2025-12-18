# Error Handling Guide

NanaSQLite v1.1.0+ provides unified custom exception classes to make error handling more predictable and easier to manage.

## Table of Contents

1. [Custom Exception Classes](#custom-exception-classes)
2. [Exception Hierarchy](#exception-hierarchy)
3. [Common Error Scenarios](#common-error-scenarios)
4. [Best Practices](#best-practices)

---

## Custom Exception Classes

### Base Exception

#### `NanaSQLiteError`

Base class for all NanaSQLite-specific exceptions.

```python
from nanasqlite import NanaSQLite, NanaSQLiteError

try:
    db = NanaSQLite("mydata.db")
    # Some operations
except NanaSQLiteError as e:
    print(f"NanaSQLite error occurred: {e}")
```

### Specific Exceptions

#### `NanaSQLiteValidationError`

Raised for invalid input values or parameters.

**Common cases**:
- Invalid table or column names
- Invalid SQL identifiers
- Parameter type errors

```python
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

db = NanaSQLite("mydata.db")

try:
    # Invalid table name (starts with number)
    db.create_table("123invalid", {"id": "INTEGER"})
except NanaSQLiteValidationError as e:
    print(f"Validation error: {e}")
```

#### `NanaSQLiteDatabaseError`

Wraps SQLite/APSW database operation errors.

**Common cases**:
- Database locked
- Disk space exhausted
- File permission errors
- SQL syntax errors

```python
from nanasqlite import NanaSQLite, NanaSQLiteDatabaseError

db = NanaSQLite("mydata.db")

try:
    # Invalid SQL
    db.execute("INVALID SQL STATEMENT")
except NanaSQLiteDatabaseError as e:
    print(f"Database error: {e}")
    # Access original APSW error
    if e.original_error:
        print(f"Original error: {e.original_error}")
```

#### `NanaSQLiteTransactionError`

Transaction-related errors.

**Common cases**:
- Attempting nested transactions
- Commit/rollback outside transaction
- Closing connection during transaction

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

db = NanaSQLite("mydata.db")

try:
    db.begin_transaction()
    db.begin_transaction()  # Nesting not allowed
except NanaSQLiteTransactionError as e:
    print(f"Transaction error: {e}")
```

#### `NanaSQLiteConnectionError`

Connection creation or management errors.

**Common cases**:
- Using closed connection
- Connection initialization failure
- Using orphaned child instance

```python
from nanasqlite import NanaSQLite, NanaSQLiteConnectionError

db = NanaSQLite("mydata.db")
db.close()

try:
    db["key"] = "value"  # Using closed connection
except NanaSQLiteConnectionError as e:
    print(f"Connection error: {e}")
```

---

## Exception Hierarchy

```
Exception
└── NanaSQLiteError (base class)
    ├── NanaSQLiteValidationError
    ├── NanaSQLiteDatabaseError
    ├── NanaSQLiteTransactionError
    ├── NanaSQLiteConnectionError
    ├── NanaSQLiteLockError
    └── NanaSQLiteCacheError
```

Since all NanaSQLite exceptions inherit from `NanaSQLiteError`, you can catch all of them:

```python
from nanasqlite import NanaSQLite, NanaSQLiteError

try:
    db = NanaSQLite("mydata.db")
    # Various operations
    db.begin_transaction()
    db["key"] = "value"
    db.commit()
except NanaSQLiteError as e:
    # Catches all NanaSQLite exceptions
    print(f"Error occurred: {e}")
```

---

## Common Error Scenarios

### 1. Database Locked

**Problem**: Multiple processes or threads accessing the database simultaneously.

```python
from nanasqlite import NanaSQLite, NanaSQLiteDatabaseError

db = NanaSQLite("mydata.db")

try:
    db["key"] = "value"
except NanaSQLiteDatabaseError as e:
    if "database is locked" in str(e).lower():
        print("Database is locked. Retrying...")
        # Retry logic
```

**Solutions**:
1. Enable WAL mode (enabled by default)
2. Set `busy_timeout`
3. Properly manage transactions

```python
db = NanaSQLite("mydata.db", optimize=True)  # WAL mode enabled
db.pragma("busy_timeout", 5000)  # Wait 5 seconds
```

### 2. Nested Transactions

**Problem**: SQLite doesn't support nested transactions.

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

db = NanaSQLite("mydata.db")

try:
    db.begin_transaction()
    # ... some operations ...
    db.begin_transaction()  # Error!
except NanaSQLiteTransactionError as e:
    print(f"Transaction error: {e}")
    db.rollback()
```

**Solution**: Check transaction state

```python
if not db.in_transaction():
    db.begin_transaction()
# Or use context manager
with db.transaction():
    db["key"] = "value"
    # Auto commit/rollback
```

### 3. Closed Connection

**Problem**: Attempting operations after closing the connection.

```python
from nanasqlite import NanaSQLite, NanaSQLiteConnectionError

db = NanaSQLite("mydata.db")
db.close()

try:
    db["key"] = "value"
except NanaSQLiteConnectionError as e:
    print(f"Connection is closed: {e}")
```

**Solution**: Use context manager

```python
with NanaSQLite("mydata.db") as db:
    db["key"] = "value"
    # Automatically closed
```

---

## Best Practices

### 1. Catch Specific Exceptions

```python
from nanasqlite import (
    NanaSQLite,
    NanaSQLiteValidationError,
    NanaSQLiteDatabaseError,
    NanaSQLiteConnectionError,
)

db = NanaSQLite("mydata.db")

try:
    db.create_table("users", {"id": "INTEGER", "name": "TEXT"})
    db.sql_insert("users", {"id": 1, "name": "Alice"})
except NanaSQLiteValidationError as e:
    print(f"Invalid input: {e}")
except NanaSQLiteDatabaseError as e:
    print(f"Database error: {e}")
    if e.original_error:
        print(f"Details: {e.original_error}")
except NanaSQLiteConnectionError as e:
    print(f"Connection error: {e}")
```

### 2. Use Context Managers

```python
# ✅ Recommended
with NanaSQLite("mydata.db") as db:
    db["key"] = "value"
    # Auto-closed even if exception occurs

# ❌ Not recommended
db = NanaSQLite("mydata.db")
try:
    db["key"] = "value"
finally:
    db.close()  # Manual close required
```

### 3. Use Transactions for Consistency

```python
from nanasqlite import NanaSQLite, NanaSQLiteError

db = NanaSQLite("mydata.db")

try:
    with db.transaction():
        # Withdraw from account A
        db.sql_update("accounts", {"balance": 900.0}, "id = ?", (1,))
        # Deposit to account B
        db.sql_update("accounts", {"balance": 1100.0}, "id = ?", (2,))
        # Auto commit on success
except NanaSQLiteError as e:
    # Auto rollback on exception
    print(f"Transaction failed: {e}")
```

---

## Async Error Handling

The async version (`AsyncNanaSQLite`) uses the same exception classes:

```python
import asyncio
from nanasqlite import AsyncNanaSQLite, NanaSQLiteError

async def main():
    try:
        async with AsyncNanaSQLite("mydata.db") as db:
            await db.aset("key", "value")
    except NanaSQLiteError as e:
        print(f"Error: {e}")

asyncio.run(main())
```

---

## Summary

- **Unified exceptions**: All NanaSQLite exceptions inherit from `NanaSQLiteError`
- **Specific error handling**: Catch specific exceptions for appropriate handling
- **Context managers**: Automatic resource management
- **Transactions**: Maintain data consistency
- **Logging**: Track and diagnose errors

Proper error handling enables you to build robust and reliable applications.

