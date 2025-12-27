# Error Handling Guide

Since NanaSQLite v1.1.0, unified custom exception classes are provided to make error handling more predictable and easier to manage.

## Table of Contents

1. [Custom Exception Classes](#custom-exception-classes)
2. [Exception Hierarchy](#exception-hierarchy)
3. [General Error Scenarios](#general-error-scenarios)
4. [Error Handling Best Practices](#error-handling-best-practices)
5. [Debugging and Troubleshooting](#debugging-and-troubleshooting)

---

## Custom Exception Classes

NanaSQLite provides the following custom exception classes:

### Base Exception

#### `NanaSQLiteError`

The base class for all NanaSQLite-specific exceptions.

```python
from nanasqlite import NanaSQLite, NanaSQLiteError

try:
    db = NanaSQLite("mydata.db")
    # Some operation
except NanaSQLiteError as e:
    print(f"NanaSQLite error occurred: {e}")
```

### Specific Exceptions

#### `NanaSQLiteValidationError`

Occurs for invalid input values or parameters.

**Cases**:
- Invalid table or column names
- Invalid SQL identifiers
- Parameter type errors

```python
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

db = NanaSQLite("mydata.db")

try:
    # Invalid table name (starts with a number)
    db.create_table("123invalid", {"id": "INTEGER"})
except NanaSQLiteValidationError as e:
    print(f"Validation error: {e}")
    # Output: Invalid identifier '123invalid': must start with letter or underscore...
```

#### `NanaSQLiteDatabaseError`

Wraps errors occurring in SQLite/APSW database operations.

**Cases**:
- Database locked
- Disk full
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

**Cases**:
- Attempted nested transactions
- Commit/Rollback outside of transaction
- Connection closed during transaction

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

db = NanaSQLite("mydata.db")

try:
    db.begin_transaction()
    db.begin_transaction()  # Nesting not allowed
except NanaSQLiteTransactionError as e:
    print(f"Transaction error: {e}")
    # Output: Transaction already in progress...
```

#### `NanaSQLiteConnectionError`

Errors occurring during database connection creation or management.

**Cases**:
- Using a closed connection
- Connection initialization failure
- Using an orphaned child instance

```python
from nanasqlite import NanaSQLite, NanaSQLiteConnectionError

db = NanaSQLite("mydata.db")
db.close()

try:
    db["key"] = "value"  # Using closed connection
except NanaSQLiteConnectionError as e:
    print(f"Connection error: {e}")
    # Output: Database connection is closed
```

#### `NanaSQLiteLockError`

Lock acquisition errors (for future feature expansion).

**Cases**:
- Lock acquisition timeout
- Deadlock detection

#### `NanaSQLiteCacheError`

Cache-related errors (for future feature expansion).

**Cases**:
- Cache size exceeded
- Cache inconsistency

---

## Exception Hierarchy

```
Exception
└── NanaSQLiteError (Base Class)
    ├── NanaSQLiteValidationError
    ├── NanaSQLiteDatabaseError
    ├── NanaSQLiteTransactionError
    ├── NanaSQLiteConnectionError
    ├── NanaSQLiteLockError
    └── NanaSQLiteCacheError
```

Since all NanaSQLite exceptions inherit from `NanaSQLiteError`, comprehensive error handling is possible:

```python
from nanasqlite import NanaSQLite, NanaSQLiteError

try:
    db = NanaSQLite("mydata.db")
    # Various operations
    db.begin_transaction()
    db["key"] = "value"
    db.commit()
except NanaSQLiteError as e:
    # Catch all NanaSQLite exceptions
    print(f"Error occurred: {e}")
```

---

## General Error Scenarios

### 1. Database Locked

**Problem**: Multiple processes or threads are trying to access the database simultaneously.

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

**Solution**:
1. Enable WAL mode (enabled by default)
2. Set `busy_timeout`
3. Properly manage transactions

```python
db = NanaSQLite("mydata.db", optimize=True)  # WAL mode enabled
db.pragma("busy_timeout", 5000)  # Wait 5 seconds
```

### 2. Nested Transactions

**Problem**: SQLite does not support nested transactions.

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
    # Automatically commit/rollback
```

### 3. Using Closed Connection

**Problem**: Attempting operations after closing connection.

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

### 4. Orphaned Child Instance

**Problem**: Trying to use a child instance after closing the parent instance.

```python
from nanasqlite import NanaSQLite, NanaSQLiteConnectionError

main_db = NanaSQLite("app.db")
sub_db = main_db.table("users")

main_db.close()  # Close parent

try:
    sub_db["key"] = "value"  # Error!
except NanaSQLiteConnectionError as e:
    print(f"Parent connection is closed: {e}")
```

**Solution**: Manage parent and child with context manager

```python
with NanaSQLite("app.db") as main_db:
    sub_db = main_db.table("users")
    sub_db["key"] = "value"
    # Child is valid until parent closes
```

### 5. Invalid Identifier

**Problem**: Identifiers are strictly validated as a countermeasure against SQL injection.

```python
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

db = NanaSQLite("mydata.db")

try:
    # Identifier with spaces or special characters
    db.create_table("my table", {"id": "INTEGER"})
except NanaSQLiteValidationError as e:
    print(f"Invalid identifier: {e}")
```

**Solution**: Use valid identifiers

```python
# Valid: Alphanumeric and underscore only, cannot start with a number
db.create_table("my_table", {"id": "INTEGER"})
db.create_table("table123", {"id": "INTEGER"})
db.create_table("_private_table", {"id": "INTEGER"})
```

---

## Error Handling Best Practices

### 1. Catch Specific Exceptions

Catch specific exceptions to handle errors appropriately.

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
    print(f"Invalid input data: {e}")
except NanaSQLiteDatabaseError as e:
    print(f"Database error: {e}")
    if e.original_error:
        print(f"Details: {e.original_error}")
except NanaSQLiteConnectionError as e:
    print(f"Connection error: {e}")
```

### 2. Use Context Managers

Use context managers for automatic resource management.

```python
# ✅ Recommended
with NanaSQLite("mydata.db") as db:
    db["key"] = "value"
    # Automatically closed even if exception occurs

# ❌ Not Recommended
db = NanaSQLite("mydata.db")
try:
    db["key"] = "value"
finally:
    db.close()  # Needs manual close
```

### 3. Maintain Consistency with Transactions

Use transactions to execute multiple operations atomically.

```python
from nanasqlite import NanaSQLite, NanaSQLiteError

db = NanaSQLite("mydata.db")
db.create_table("accounts", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT",
    "balance": "REAL"
})

try:
    with db.transaction():
        # Withdraw from Account A
        db.sql_update("accounts", {"balance": 900.0}, "id = ?", (1,))
        # Deposit to Account B
        db.sql_update("accounts", {"balance": 1100.0}, "id = ?", (2,))
        # Auto commit if both succeed
except NanaSQLiteError as e:
    # Auto rollback if exception occurs
    print(f"Transaction failed: {e}")
```

### 4. Utilize Logging

Use logging for error tracking and diagnosis.

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

### 5. Convey Appropriate Error Messages to Users

Hide technical details and provide user-friendly messages.

```python
from nanasqlite import NanaSQLite, NanaSQLiteValidationError, NanaSQLiteDatabaseError

def save_user_data(user_data):
    try:
        db = NanaSQLite("users.db")
        db.create_table("users", {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT",
            "email": "TEXT UNIQUE"
        })
        db.sql_insert("users", user_data)
        return {"success": True, "message": "User registered"}
    except NanaSQLiteValidationError as e:
        return {"success": False, "message": "Invalid input data"}
    except NanaSQLiteDatabaseError as e:
        if "unique" in str(e).lower():
            return {"success": False, "message": "This email is already registered"}
        return {"success": False, "message": "Database error occurred"}
    except Exception as e:
        return {"success": False, "message": "Unexpected error occurred"}
```

---

## Debugging and Troubleshooting

### Getting Error Information

`NanaSQLiteDatabaseError` holds the original APSW error:

```python
from nanasqlite import NanaSQLite, NanaSQLiteDatabaseError

try:
    db = NanaSQLite("mydata.db")
    db.execute("INVALID SQL")
except NanaSQLiteDatabaseError as e:
    print(f"Error message: {e}")
    if e.original_error:
        print(f"Original APSW error: {e.original_error}")
        print(f"Error type: {type(e.original_error)}")
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
print(f"Connection owner: {db._is_connection_owner}")
print(f"Connection closed: {db._is_closed}")

sub_db = db.table("users")
print(f"Child connection owner: {sub_db._is_connection_owner}")  # False
print(f"Parent closed: {sub_db._parent_closed}")  # False

db.close()
print(f"Child after parent closed: {sub_db._parent_closed}")  # True
```

### Enabling Debug Mode

Display debug info using Python's `-v` flag or `PYTHONVERBOSE` environment variable:

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

Currently, `AsyncNanaSQLite` uses the same exception classes:

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

## FAQ and Troubleshooting

### Q: I frequently get "database is locked" error

**Cause**: Multiple processes or threads are trying to write simultaneously, or a long-running transaction is holding the connection.

**Solution**:
1.  **Check WAL Mode**: Enabled by default, check if `db.pragma("journal_mode")` is `wal`.
2.  **Set Busy Timeout**: Set `db.pragma("busy_timeout", 5000)` to wait for the lock to be released.
3.  **Shorten Transactions**: `commit()` immediately after write operations finish, or keep `with db.transaction():` blocks minimal.
4.  **Antivirus Exclusion**: (Windows) Exclude DB files from scanning.

### Q: Memory usage keeps increasing

**Cause**: Loading large amounts of data causes cache accumulation.

**Solution**:
1.  **Refresh Cache**: Periodically run `db.refresh()` to release memory.
2.  **Use Lazy Loading**: Avoid `bulk_load=True` and load only when needed.
3.  **Recreate Instance**: For long-running processes, periodically closing and reopening the connection is also effective.

### Q: Updates to a specific key are not reflected

**Cause**: The memory cache and DB content diverged due to another inconsistent connection (e.g., direct manipulation via `execute()`).

**Solution**:
1.  **Use `get_fresh(key)`**: Ignore cache and retrieve the latest data from DB.
2.  **`refresh()` after `execute()`**: After rewriting data by executing SQL directly, always call `db.refresh(key)`.

---

## Summary

- **Unified Exceptions**: All NanaSQLite exceptions inherit from `NanaSQLiteError`
- **Specific Error Handling**: Catch specific exceptions and handle appropriately
- **Context Manager**: Automated resource management
- **Transactions**: Maintain data consistency
- **Logging**: Error tracking and diagnosis

Proper error handling allows you to build robust and reliable applications.
