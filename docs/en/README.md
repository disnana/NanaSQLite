# NanaSQLite Documentation

A dict-like SQLite wrapper with instant persistence and intelligent caching.

## Table of Contents

- [Concept](#concept)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [API Reference](reference.md)

---

## Concept

### The Problem

Python dicts are fast and convenient, but they're volatile - when your program ends, all data is lost. Traditional database solutions require learning SQL, managing connections, and handling serialization manually.

### The Solution

**NanaSQLite** bridges this gap by wrapping a standard Python dict with transparent SQLite persistence:

```
┌─────────────────────────────────────────────────────┐
│                  Your Python Code                    │
│                                                      │
│    db["user"] = {"name": "Nana", "age": 20}         │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│                   NanaSQLite                         │
│  ┌───────────────┐     ┌───────────────────────┐    │
│  │ Memory Cache  │ ←→  │ APSW SQLite Backend   │    │
│  │ (Python dict) │     │ (Persistent Storage)  │    │
│  └───────────────┘     └───────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

### Design Principles

1. **Instant Write**: Every write operation is immediately persisted to SQLite
2. **Smart Read**: Data is loaded on-demand (lazy) or all-at-once (bulk)
3. **Memory First**: Once loaded, data is served from memory for speed
4. **Zero Config**: Sensible defaults optimized for performance

### Performance Optimizations

NanaSQLite applies these SQLite optimizations by default:

| Setting | Effect |
|---------|--------|
| **WAL Mode** | Write speed: 30ms+ → <1ms |
| **synchronous=NORMAL** | Safe + Fast |
| **mmap (256MB)** | Faster reads via memory-mapped I/O |
| **cache_size (64MB)** | Larger SQLite page cache |
| **temp_store=MEMORY** | Temp tables in RAM |

---

## Installation

```bash
pip install nanasqlite
```

**Requirements:**
- Python 3.9+
- APSW (installed automatically)

---

## Quick Start

### Basic Usage

```python
from nanasqlite import NanaSQLite

# Create or open a database
db = NanaSQLite("mydata.db")

# Store data (instantly persisted)
db["config"] = {"theme": "dark", "language": "en"}
db["users"] = ["Alice", "Bob", "Charlie"]
db["count"] = 42

# Retrieve data
print(db["config"]["theme"])  # 'dark'
print(db["users"][0])          # 'Alice'
print(db["count"])             # 42

# Check existence
if "config" in db:
    print("Config exists!")

# Delete data
del db["count"]

# Close when done
db.close()
```

### Context Manager

```python
with NanaSQLite("mydata.db") as db:
    db["key"] = "value"
    # Automatically closed at the end
```

### Bulk Loading for Speed

```python
# Load all data into memory at startup
db = NanaSQLite("mydata.db", bulk_load=True)

# All subsequent reads are from memory (ultra-fast)
for key in db.keys():
    print(db[key])  # No database queries!
```

---

## Usage Guide

### Supported Data Types

NanaSQLite supports all JSON-serializable types:

```python
db["string"] = "Hello, World!"
db["integer"] = 42
db["float"] = 3.14159
db["boolean"] = True
db["null"] = None
db["list"] = [1, 2, 3, "four", 5.0]
db["dict"] = {"nested": {"deep": {"value": 123}}}
```

### Nested Structures

Deeply nested structures are fully supported (tested up to 30 levels):

```python
db["deep"] = {
    "level1": {
        "level2": {
            "level3": {
                "data": [1, 2, {"key": "value"}]
            }
        }
    }
}

# Access nested data
print(db["deep"]["level1"]["level2"]["level3"]["data"][2]["key"])  # 'value'
```

### Dict Methods

All standard dict methods are available:

```python
# Keys, values, items
print(db.keys())    # ['key1', 'key2', ...]
print(db.values())  # [value1, value2, ...]
print(db.items())   # [('key1', value1), ...]

# Get with default
value = db.get("missing", "default")

# Pop (get and delete)
value = db.pop("key")

# Update multiple keys
db.update({"a": 1, "b": 2, "c": 3})

# Set default
db.setdefault("new_key", "default_value")

# Clear all
db.clear()

# Convert to regular dict
regular_dict = db.to_dict()
```

### Batch Operations

For bulk writes, use batch methods for 10-100x speedup:

```python
# Batch update (uses transactions)
db.batch_update({
    f"key_{i}": {"data": i} for i in range(10000)
})

# Batch delete
db.batch_delete(["key_0", "key_1", "key_2"])
```

### Cache Management

```python
# Check if a key is in memory cache
if db.is_cached("key"):
    print("Already in memory!")

# Force reload from database
db.refresh("key")  # Single key
db.refresh()       # All keys

# Load everything into memory
db.load_all()
```

### Multiple Tables

```python
# Use different tables in the same database
users_db = NanaSQLite("app.db", table="users")
config_db = NanaSQLite("app.db", table="config")

users_db["alice"] = {"name": "Alice", "age": 30}
config_db["theme"] = "dark"
```

### Performance Tuning

```python
# Disable optimizations (not recommended)
db = NanaSQLite("mydata.db", optimize=False)

# Custom cache size (default: 64MB)
db = NanaSQLite("mydata.db", cache_size_mb=128)
```

---

## Next Steps

- [API Reference](reference.md) - Detailed method documentation
