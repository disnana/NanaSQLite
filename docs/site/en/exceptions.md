# Exceptions Reference

NanaSQLite provides fine-grained exception classes categorized by operation type.

## Exception Hierarchy

```
NanaSQLiteError (base class)
├── NanaSQLiteValidationError    # Data validation errors
├── NanaSQLiteDatabaseError      # DB operation errors
├── NanaSQLiteTransactionError   # Transaction errors
├── NanaSQLiteConnectionError    # Connection errors
│   └── NanaSQLiteClosedError    # Closed-state errors
├── NanaSQLiteLockError          # Lock acquisition errors
└── NanaSQLiteCacheError         # Cache errors
```

## Exception Class Details

### NanaSQLiteError

Base class for all NanaSQLite exceptions.

```python
from nanasqlite import NanaSQLiteError

try:
    db["key"]
except NanaSQLiteError as e:
    # Catches all NanaSQLite errors
    print(f"Error: {e}")
```

### NanaSQLiteValidationError

Raised when data validation fails. Used with `validkit-py` schema validation.

```python
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

db = NanaSQLite("app.db", validator={"name": str, "age": int})

try:
    db["user1"] = {"name": "Alice", "age": "not_a_number"}
except NanaSQLiteValidationError as e:
    print(f"Validation error: {e}")
```

**Raised by:**
- `__setitem__` when schema validation fails
- `batch_update()` when schema validation fails
- `batch_update_partial()` when schema validation fails

### NanaSQLiteDatabaseError

Raised when an error occurs during SQLite database operations. Retains the original exception via the `original_error` attribute.

```python
from nanasqlite import NanaSQLiteDatabaseError

try:
    db.execute("INVALID SQL STATEMENT")
except NanaSQLiteDatabaseError as e:
    print(f"DB error: {e}")
    if e.original_error:
        print(f"Original error: {e.original_error}")
```

**Raised by:**
- Invalid SQL execution
- Table/index creation failures
- Encrypted data decryption failures
- Data serialization/deserialization failures

### NanaSQLiteTransactionError

Raised when an error occurs during transaction operations.

```python
from nanasqlite import NanaSQLiteTransactionError

try:
    db.begin_transaction()
    db.begin_transaction()  # Nesting not allowed
except NanaSQLiteTransactionError as e:
    print(f"Transaction error: {e}")
```

**Raised by:**
- Starting a transaction when one is already active
- Calling `commit()` / `rollback()` outside a transaction
- Calling `close()` during a transaction

### NanaSQLiteConnectionError

Raised when a database connection error occurs.

```python
from nanasqlite import NanaSQLiteConnectionError

try:
    db = NanaSQLite("/invalid/path/db.sqlite")
except NanaSQLiteConnectionError as e:
    print(f"Connection error: {e}")
```

**Raised by:**
- Inability to access the database file
- Connection establishment failure

### NanaSQLiteClosedError

Raised when performing operations on a closed database. Subclass of `NanaSQLiteConnectionError`.

```python
from nanasqlite import NanaSQLiteClosedError

db = NanaSQLite("app.db")
db.close()

try:
    db["key"] = "value"
except NanaSQLiteClosedError as e:
    print(f"Database closed: {e}")
```

**Raised by:**
- Read/write operations after `close()`
- Operating on a child table after the parent instance is closed

### NanaSQLiteLockError

Raised when database lock acquisition fails.

```python
from nanasqlite import NanaSQLite, NanaSQLiteLockError

db = NanaSQLite("app.db", lock_timeout=5.0)

try:
    db["key"] = "value"
except NanaSQLiteLockError as e:
    print(f"Lock error: {e}")
```

**Raised by:**
- Failure to acquire lock within `lock_timeout`
- Another process holding the database lock

### NanaSQLiteCacheError

Raised when an error occurs during cache operations.

```python
from nanasqlite import NanaSQLiteCacheError

try:
    db.clear_cache()
except NanaSQLiteCacheError as e:
    print(f"Cache error: {e}")
```

**Raised by:**
- Cache initialization failure
- Cache strategy inconsistencies

## Error Handling Best Practices

### 1. Catch Specific Exceptions

```python
from nanasqlite import (
    NanaSQLiteValidationError,
    NanaSQLiteDatabaseError,
    NanaSQLiteTransactionError,
    NanaSQLiteLockError,
    NanaSQLiteClosedError,
)

try:
    db["key"] = data
except NanaSQLiteValidationError:
    # Data format issue → ask user for correct input
    pass
except NanaSQLiteLockError:
    # Lock contention → retry
    pass
except NanaSQLiteClosedError:
    # Connection lost → reconnect
    pass
except NanaSQLiteDatabaseError:
    # DB operation failure → log the error
    pass
```

### 2. Catch All with Base Class

```python
from nanasqlite import NanaSQLiteError

try:
    db["key"] = data
except NanaSQLiteError as e:
    # Handle all NanaSQLite errors uniformly
    logger.error(f"NanaSQLite error: {e}")
```

### 3. Transaction Error Handling

```python
try:
    with db.transaction():
        db["key1"] = "value1"
        db["key2"] = "value2"
except NanaSQLiteTransactionError:
    # Transaction failed → already auto-rolled-back
    pass
```

## Imports

All exception classes can be imported directly from the `nanasqlite` package:

```python
from nanasqlite import (
    NanaSQLiteError,
    NanaSQLiteValidationError,
    NanaSQLiteDatabaseError,
    NanaSQLiteTransactionError,
    NanaSQLiteConnectionError,
    NanaSQLiteClosedError,
    NanaSQLiteLockError,
    NanaSQLiteCacheError,
)
```
