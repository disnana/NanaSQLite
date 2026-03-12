# Exceptions Reference

NanaSQLite provides fine-grained exception classes for each operation type.

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

## NanaSQLiteError

Base class for all NanaSQLite exceptions.

## NanaSQLiteValidationError

Raised when data validation fails (with `validkit-py` schema validation).

## NanaSQLiteDatabaseError

Raised during SQLite operations. Has `original_error` attribute for the underlying error.

## NanaSQLiteTransactionError

Raised for transaction issues: double-begin, commit/rollback outside transaction.

## NanaSQLiteConnectionError

Raised for database connection errors.

### NanaSQLiteClosedError

Subclass of `NanaSQLiteConnectionError`. Raised when operating on a closed database.

## NanaSQLiteLockError

Raised when database lock acquisition fails within `lock_timeout`.

## NanaSQLiteCacheError

Raised during cache operation errors.

## Imports

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
