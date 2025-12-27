# Introduction Guide

NanaSQLite is a library that combines the ease of use of Python's `dict` with robust persistence using SQLite and fast memory caching.

---

## ⚡ Quick Start

Installation is simple:

```bash
pip install nanasqlite
```

Here is the basic usage:

```python
from nanasqlite import NanaSQLite

# Open database (created if it doesn't exist)
db = NanaSQLite("mydata.db")

# Save data like a dict
db["user_1"] = {"name": "Nana", "age": 20}

# Retrieve data
user = db["user_1"]
print(user["name"]) # Nana

# Data persists even after the program ends
```

---

## 🌟 Key Features

::: info Cache and Performance
NanaSQLite supports "Bulk Load" (loads all data at startup) and "Lazy Load" (loads on access). It also uses WAL mode, so reads are not blocked during writes.
:::

### 1. Nested Structures
You can save complex dictionaries and lists as they are, supporting deep nesting of over 30 levels.

### 2. Powerful Security (v1.2.0+)
Includes strict validation as a countermeasure against SQL injection, and length limits/character set verification to prevent ReDoS (Regular Expression DoS) attacks.

### 3. Async Support
Using the `AsyncNanaSQLite` class delivers maximum performance in asynchronous frameworks like FastAPI and Discord.py.
A dedicated thread pool allows fast DB operations without blocking the event loop.

### 4. Transactions and Multi-Table
Safe operation of multiple tables within the same database sharing a connection.
Supports automatic commit/rollback using `with db.transaction():`.

### 5. Pydantic Compatibility
You can directly save and retrieve Pydantic models. Validated data can be persisted to the DB as is.

```python
async with AsyncNanaSQLite("async.db") as db:
    await db.aset("key", "value")
```

---

## 🛠️ Next Steps

- [Performance Optimization](./performance_tuning)
- [Error Handling and Troubleshooting](./error_handling)
- [API Reference (Sync)](./api_sync)
- [API Reference (Async)](./api_async)
