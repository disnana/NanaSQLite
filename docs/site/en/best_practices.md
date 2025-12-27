# NanaSQLite Best Practices

A comprehensive guide to using NanaSQLite effectively in production environments.

## Table of Contents

- [Performance Optimization](#performance-optimization)
- [Security Guidelines](#security-guidelines)
- [Error Handling](#error-handling)
- [Resource Management](#resource-management)
- [Design Patterns](#design-patterns)
- [Testing](#testing)

---

## Performance Optimization

### Choose the Right Cache Strategy

**Lazy Loading (Default)**
```python
# Best for: Large databases, sparse access patterns
db = NanaSQLite("large.db")
# Only loads data when accessed
user = db["user_123"]  # First access: loads from DB
user = db["user_123"]  # Second access: from memory
```

**Bulk Loading**
```python
# Best for: Small databases (<100MB), frequent access to most keys
db = NanaSQLite("small.db", bulk_load=True)
# All data loaded at startup
# All subsequent reads from memory (ultra-fast)
```

**Decision Matrix:**

| Database Size | Access Pattern | Recommendation |
|--------------|----------------|----------------|
| < 10MB | Read-heavy | `bulk_load=True` |
| 10-100MB | Most keys accessed | `bulk_load=True` |
| 100MB-1GB | Some keys accessed | `bulk_load=False` (default) |
| > 1GB | Any pattern | `bulk_load=False` (default) |

### Use Batch Operations

**❌ Anti-pattern: Individual writes**
```python
# Slow: 1000 separate transactions
for i in range(1000):
    db[f"user_{i}"] = {"name": f"User{i}"}
```

**✅ Best practice: Batch writes**
```python
# Fast: Single transaction (10-100x faster)
users = {f"user_{i}": {"name": f"User{i}"} for i in range(1000)}
db.batch_update(users)
```

**Performance Comparison:**

| Operation | Individual | Batch | Speedup |
|-----------|-----------|-------|---------|
| 100 writes | ~200ms | ~2ms | 100x |
| 1000 writes | ~2000ms | ~15ms | 133x |
| 10000 writes | ~20000ms | ~150ms | 133x |

### Optimize SQLite Cache Size

The `cache_size_mb` parameter controls SQLite's internal page cache (PRAGMA cache_size), not NanaSQLite's dictionary cache. This affects how many database pages SQLite keeps in memory for faster disk I/O.

```python
# Default: 64MB SQLite page cache (good for most cases)
db = NanaSQLite("data.db")

# Large datasets: increase SQLite page cache
db = NanaSQLite("large.db", cache_size_mb=256)

# Memory-constrained: reduce SQLite page cache
db = NanaSQLite("data.db", cache_size_mb=32)
```

**Guidelines:**
- **Small DB (<100MB)**: 32-64MB SQLite cache
- **Medium DB (100MB-1GB)**: 128-256MB SQLite cache
- **Large DB (>1GB)**: 256-512MB SQLite cache

**Note:** This parameter does NOT affect the memory used by NanaSQLite's internal dictionary cache (`_data`), which stores loaded values in Python memory. To control that, use `bulk_load=False` (default) for lazy loading.

### Context Manager for Auto-Cleanup

**✅ Always use context manager**
```python
with NanaSQLite("data.db") as db:
    db["key"] = "value"
# Automatically closed and resources freed
```

**❌ Avoid manual management**
```python
db = NanaSQLite("data.db")
db["key"] = "value"
db.close()  # Easy to forget!
```

---

## Security Guidelines

### Prevent SQL Injection

**✅ Use parameter binding**
```python
# Safe: parameters are properly escaped
results = db.query(
    table_name="users",
    where="name = ?",
    parameters=(user_input,)
)
```

**❌ Never concatenate user input**
```python
# DANGEROUS: SQL injection vulnerability
# Never do this!
db.execute(f"SELECT * FROM users WHERE name = '{user_input}'")
```

### Validate File Paths

```python
import os

def safe_db_path(user_input: str) -> str:
    """Validate database path to prevent directory traversal"""
    # Remove path separators and relative paths
    if ".." in user_input or "/" in user_input or "\\" in user_input:
        raise ValueError("Invalid database path")
    
    # Ensure it's in a safe directory
    safe_dir = "/var/lib/myapp/databases"
    return os.path.join(safe_dir, f"{user_input}.db")

# Usage
db_path = safe_db_path(user_provided_name)
db = NanaSQLite(db_path)
```

### Protect Sensitive Data

```python
# Don't store plain-text secrets
# ❌ Bad
db["config"] = {
    "api_key": "sk-1234567890abcdef",
    "password": "mypassword123"
}

# ✅ Good: Encrypt sensitive values
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

encrypted_api_key = cipher.encrypt(b"sk-1234567890abcdef")
db["config"] = {
    "api_key": encrypted_api_key.decode(),
    # Use bcrypt: import bcrypt; bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    "password_hash": hash_password("mypassword123")  # Replace with actual hashing
}
```

### File Permissions

```python
import os
import stat

# Create database with restricted permissions
db = NanaSQLite("secure.db")
db.close()

# Set file permissions to owner-only read/write
os.chmod("secure.db", stat.S_IRUSR | stat.S_IWUSR)
```

---

## Error Handling

### Handle Missing Keys Gracefully

**✅ Use get() with default**
```python
# Preferred: No exception handling needed
value = db.get("key", default="default_value")
```

**✅ Use try/except for required keys**
```python
try:
    value = db["required_key"]
except KeyError:
    logger.error("Required configuration missing")
    # Use ValueError or define your own ConfigurationError exception class
    raise ValueError("Missing required_key")
```

### Handle Database Errors

```python
import apsw
import logging

logger = logging.getLogger(__name__)

try:
    with NanaSQLite("data.db") as db:
        db.create_table("users", {
            "id": "INTEGER PRIMARY KEY",
            "email": "TEXT UNIQUE"
        })
        db.sql_insert("users", {"email": "test@example.com"})
except apsw.Error as e:
    logger.error(f"Database error: {e}")
    # Handle appropriately (retry, fallback, etc.)
```

### Validate Data Before Insertion

```python
def save_user(db: NanaSQLite, user_data: dict) -> bool:
    """Save user with validation"""
    # Validate required fields
    required = ["name", "email", "age"]
    if not all(field in user_data for field in required):
        raise ValueError(f"Missing required fields: {required}")
    
    # Validate data types
    if not isinstance(user_data["age"], int):
        raise TypeError("Age must be an integer")
    
    if user_data["age"] < 0 or user_data["age"] > 150:
        raise ValueError("Invalid age")
    
    # Save
    db[f"user_{user_data['email']}"] = user_data
    return True
```

---

## Resource Management

### Connection Pooling for Web Applications

**FastAPI Example**
```python
from fastapi import FastAPI, Depends
from nanasqlite import AsyncNanaSQLite
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database connection
    app.state.db = AsyncNanaSQLite("app.db", max_workers=10)
    yield
    # Shutdown: Close database
    await app.state.db.close()

app = FastAPI(lifespan=lifespan)

async def get_db() -> AsyncNanaSQLite:
    """Dependency injection for database"""
    return app.state.db

@app.get("/users/{user_id}")
async def get_user(user_id: str, db: AsyncNanaSQLite = Depends(get_db)):
    return await db.aget(f"user_{user_id}")
```

### Memory Management

```python
# For long-running processes, periodically clear unused cache
class CachedDB:
    def __init__(self, db_path: str):
        self.db = NanaSQLite(db_path)
        self.access_count = 0
    
    def get(self, key: str):
        self.access_count += 1
        
        # Every 10000 operations, refresh cache
        if self.access_count % 10000 == 0:
            self.db.refresh()  # Clear cache
            
        return self.db.get(key)
```

---

## Design Patterns

### Separation of Concerns

```python
# Use different tables for different concerns
class AppDatabase:
    def __init__(self, db_path: str):
        self.users = NanaSQLite(db_path, table="users")
        self.sessions = NanaSQLite(db_path, table="sessions")
        self.cache = NanaSQLite(db_path, table="cache")
        self.config = NanaSQLite(db_path, table="config")
    
    def close_all(self):
        self.users.close()
        self.sessions.close()
        self.cache.close()
        self.config.close()

# Usage
app_db = AppDatabase("app.db")
app_db.users["alice"] = {"role": "admin"}
app_db.sessions["sess_123"] = {"user_id": "alice"}
app_db.close_all()
```

### Repository Pattern

```python
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class User:
    id: str
    name: str
    email: str
    age: int

class UserRepository:
    def __init__(self, db: NanaSQLite):
        self.db = db
    
    def save(self, user: User) -> None:
        self.db[f"user_{user.id}"] = {
            "name": user.name,
            "email": user.email,
            "age": user.age
        }
    
    def find_by_id(self, user_id: str) -> Optional[User]:
        data = self.db.get(f"user_{user_id}")
        if data:
            return User(id=user_id, **data)
        return None
    
    def find_all(self) -> List[User]:
        users = []
        for key in self.db.keys():
            if key.startswith("user_"):
                user_id = key[5:]  # Remove "user_" prefix
                data = self.db[key]
                users.append(User(id=user_id, **data))
        return users

# Usage
with NanaSQLite("app.db") as db:
    repo = UserRepository(db)
    
    user = User(id="1", name="Alice", email="alice@example.com", age=30)
    repo.save(user)
    
    found = repo.find_by_id("1")
    print(found.name)  # Alice
```

---

## Testing

### Unit Testing

```python
import pytest
import tempfile
import os

@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)

def test_basic_operations(temp_db):
    with NanaSQLite(temp_db) as db:
        # Test write
        db["test_key"] = {"value": 123}
        
        # Test read
        assert db["test_key"] == {"value": 123}
        
        # Test delete
        del db["test_key"]
        assert "test_key" not in db

def test_batch_operations(temp_db):
    with NanaSQLite(temp_db) as db:
        # Test batch write
        data = {f"key_{i}": i for i in range(100)}
        db.batch_update(data)
        
        assert len(db) == 100
        assert db["key_50"] == 50
```

### Mocking

```python
from unittest.mock import MagicMock, patch

def test_with_mock():
    mock_db = MagicMock(spec=NanaSQLite)
    mock_db.get.return_value = {"name": "Test User"}
    
    # Your function that uses the database
    def get_user_name(db, user_id):
        user = db.get(f"user_{user_id}")
        return user["name"] if user else None
    
    result = get_user_name(mock_db, "123")
    assert result == "Test User"
    mock_db.get.assert_called_once_with("user_123")
```

---

## Summary

**Key Takeaways:**

1. ✅ Use `bulk_load=True` for small, frequently accessed databases
2. ✅ Always use batch operations for 100+ writes
3. ✅ Use context managers (`with` statement) for automatic cleanup
4. ✅ Use parameter binding to prevent SQL injection
5. ✅ Validate user input, especially file paths
6. ✅ Handle errors gracefully with `get()` and try/except
7. ✅ Separate concerns with different tables
8. ✅ Test with temporary databases
9. ✅ Monitor memory usage in long-running processes
10. ✅ Use async version for async frameworks (FastAPI, aiohttp)

**Common Pitfalls to Avoid:**

1. ❌ Using `bulk_load=True` with large databases (>1GB)
2. ❌ Individual writes instead of batch operations
3. ❌ Forgetting to close databases (use `with` statement)
4. ❌ SQL injection via string concatenation
5. ❌ Storing sensitive data without encryption
6. ❌ Ignoring KeyError exceptions
7. ❌ Not validating user input

For more examples, see:
- [Tutorial](guide) - Step-by-step learning guide
- [API Reference](./api_sync) - Complete method documentation
- [Async Guide](async_guide) - Async/await usage
