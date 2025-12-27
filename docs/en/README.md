# NanaSQLite Documentation

A dict-like SQLite wrapper with instant persistence and intelligent caching.

## Table of Contents

- [Concept](#concept)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Guides](#guides)
  - [Tutorial](guide/tutorial.md)
  - [Async Support](guide/async.md)
  - [Transactions](guide/transactions.md)
  - [Error Handling](guide/error_handling.md)
  - [Performance](guide/performance.md)
  - [Best Practices](guide/best_practices.md)
- [API Reference](#api-reference)
  - [NanaSQLite (Sync)](api/nanasqlite.md)
  - [AsyncNanaSQLite (Async)](api/async_nanasqlite.md)

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

## Guides

For more detailed information, please refer to the following guides:

- **[Tutorial](guide/tutorial.md)**: Extended examples including multiple tables and advanced features.
- **[Async Support](guide/async.md)**: How to use `AsyncNanaSQLite` for non-blocking operations.
- **[Transactions](guide/transactions.md)**: ensuring data integrity and optimizing bulk writes.
- **[Error Handling](guide/error_handling.md)**: Handling exceptions and troubleshooting.
- **[Performance](guide/performance.md)**: Tuning NanaSQLite for maximum speed.
- **[Best Practices](guide/best_practices.md)**: Recommended patterns for production use.

---

## API Reference

Complete documentation for all classes and methods.

- **[NanaSQLite (Sync)](api/nanasqlite.md)**
- **[AsyncNanaSQLite (Async)](api/async_nanasqlite.md)**
