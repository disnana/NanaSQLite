# Error Handling Guide

NanaSQLite v1.1.0+ provides unified custom exception classes to make error handling more predictable and easier to manage.

## Table of Contents

1. [Custom Exception Classes](#custom-exception-classes)
2. [Exception Hierarchy](#exception-hierarchy)
3. [Common Error Scenarios](#common-error-scenarios)
4. [Best Practices](#best-practices)
5. [Debugging and Troubleshooting](#debugging-and-troubleshooting)
6. [Async Error Handling](#async-error-handling)
7. [FAQ](#faq)

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
- Connection initialization failure
- Using orphaned child instance

#### `NanaSQLiteClosedError` *(v1.2.0+)*

Raised when attempting an operation on a closed instance or a child instance whose parent has been closed. It is a subclass of `NanaSQLiteConnectionError`.

**Common cases**:
- Operations after calling `close()`
- Operations on a `table()` instance after its parent has been closed

```python
from nanasqlite import NanaSQLite, NanaSQLiteClosedError

db = NanaSQLite("mydata.db")
db.close()

try:
    db["key"] = "value"
except NanaSQLiteClosedError as e:
    print(f"Closed error: {e}")
```

#### `NanaSQLiteLockError`

Reserved for future use regarding lock acquisition failures.

#### `NanaSQLiteCacheError`

Reserved for future use regarding cache inconsistencies.

---

## Exception Hierarchy

```
Exception
└── NanaSQLiteError (base class)
    ├── NanaSQLiteValidationError
    ├── NanaSQLiteDatabaseError
    ├── NanaSQLiteTransactionError
    ├── NanaSQLiteConnectionError
    │   └── NanaSQLiteClosedError
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

### 4. Orphaned Child Instances

**Problem**: Trying to use a child instance (`.table()`) after the parent connection has been closed.

```python
main_db = NanaSQLite("app.db")
sub_db = main_db.table("users")

main_db.close()  # Close parent

try:
    sub_db["key"] = "value"  # Error!
except NanaSQLiteConnectionError as e:
    print(f"Parent connection closed: {e}")
```

**Solution**: Manage parent and child scope together.

```python
with NanaSQLite("app.db") as main_db:
    sub_db = main_db.table("users")
    sub_db["key"] = "value"
```

### 5. Invalid Identifiers

**Problem**: Identifiers are strictly validated to prevent SQL injection.

```python
try:
    db.create_table("my table", {"id": "INTEGER"}) # contains space
except NanaSQLiteValidationError as e:
    print(f"Invalid identifier: {e}")
```

**Solution**: Use valid alphanumeric characters and underscores.

```python
db.create_table("my_table", {"id": "INTEGER"})
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

### 4. Use Logging

```python
import logging
from nanasqlite import NanaSQLite, NanaSQLiteError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    db = NanaSQLite("mydata.db")
    db["key"] = "value"
    logger.info("Data saved successfully")
except NanaSQLiteError as e:
    logger.error(f"Error occurred: {e}", exc_info=True)
```

---

## Debugging and Troubleshooting

### Retrieving Error Information

`NanaSQLiteDatabaseError` holds the original APSW error.

```python
from nanasqlite import NanaSQLite, NanaSQLiteDatabaseError

try:
    db = NanaSQLite("mydata.db")
    db.execute("INVALID SQL")
except NanaSQLiteDatabaseError as e:
    print(f"Message: {e}")
    if e.original_error:
        print(f"Original APSW Error: {e.original_error}")
        print(f"Error Type: {type(e.original_error)}")
```

### Checking Transaction State

```python
db = NanaSQLite("mydata.db")

print(f"In transaction: {db.in_transaction()}")  # False

db.begin_transaction()
print(f"In transaction: {db.in_transaction()}")  # True

db.commit()
print(f"In transaction: {db.in_transaction()}")  # False
```

### Checking Connection State

```python
db = NanaSQLite("mydata.db")
print(f"Is owner: {db._is_connection_owner}")
print(f"Is closed: {db._is_closed}")

sub_db = db.table("users")
print(f"Child is owner: {sub_db._is_connection_owner}")  # False
print(f"Parent closed: {sub_db._parent_closed}")  # False

db.close()
print(f"Child check parent closed: {sub_db._parent_closed}")  # True
```

### Enabling Debug Mode

You can use Python's `-v` flag or `PYTHONVERBOSE` environment variable to see module loading and some internal details.

```bash
# Windows
$env:PYTHONVERBOSE=1
python your_script.py

# Linux/Mac
PYTHONVERBOSE=1 python your_script.py
```

### Detailed Traceback

```python
import traceback
from nanasqlite import NanaSQLite, NanaSQLiteError

try:
    db = NanaSQLite("mydata.db")
    # ... operations ...
except NanaSQLiteError as e:
    print("Error occurred:")
    print(traceback.format_exc())
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

## FAQ

### Q: I frequently encounter "database is locked" errors

**Cause**: Multiple processes or threads are attempting to write simultaneously, or a long-running transaction is holding the connection.

**Solutions**:
1.  **Check WAL Mode**: It's enabled by default, but verify that `db.pragma("journal_mode")` returns `wal`.
2.  **Set Busy Timeout**: Use `db.pragma("busy_timeout", 5000)` to wait for the lock to be released.
3.  **Shorten Transactions**: Commit as soon as write operations are done, or keep `with db.transaction():` blocks as small as possible.
4.  **Exclude from Antivirus**: (Windows) Exclude your database files from real-time scans.

### Q: Memory usage keeps increasing

**Cause**: The in-memory cache is accumulating data as you read more keys.

**Solutions**:
1.  **Refresh Cache**: Periodically call `db.refresh()` to clear the memory and free up space.
2.  **Use Lazy Loading**: Avoid `bulk_load=True` and only load data as needed.
3.  **Recreate Instance**: For long-running processes, occasionally closing and reopening the connection can help.

### Q: Updates to specific keys aren't being reflected

**Cause**: Inconsistent connections (e.g., direct manipulation via `execute()`) are causing a mismatch between the memory cache and the database content.

**Solutions**:
1.  **Use `get_fresh(key)`**: Bypass the cache to get the latest data directly from the DB.
2.  **Call `refresh()` after `execute()`**: If you modify data via raw SQL, always call `db.refresh(key)` to synchronize the cache.

---

## Summary

- **Unified exceptions**: All NanaSQLite exceptions inherit from `NanaSQLiteError`
- **Specific error handling**: Catch specific exceptions for appropriate handling
- **Context managers**: Automatic resource management
- **Transactions**: Maintain data consistency
- **Logging**: Track and diagnose errors

Proper error handling enables you to build robust and reliable applications.
