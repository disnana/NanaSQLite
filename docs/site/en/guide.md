# Getting Started

NanaSQLite is a high-performance Python library that combines the simplicity of a dictionary with the persistence of SQLite and an intelligent memory cache.

---

## ⚡ Quick Start

Installation:

```bash
pip install nanasqlite
```

Basic Usage:

```python
from nanasqlite import NanaSQLite

# Open a database
db = NanaSQLite("mydata.db")

# Store data like a dict
db["user_1"] = {"name": "Nana", "age": 20}

# Retrieve data
user = db["user_1"]
print(user["name"]) # Nana
```

---

## 🌟 Key Features

::: info Caching & Performance
NanaSQLite supports both "Bulk Load" and "Lazy Load". With WAL mode enabled by default, it handles concurrent reads and writes efficiently.
:::

### 1. Nested Structures
Support for deeply nested dictionaries and lists (up to 30+ levels).

### 2. Security (v1.2.0+)
Strict SQL validation, ReDoS protection, and character-set verification are built-in for maximum stability.

### 3. Full Async Support
Use `AsyncNanaSQLite` for non-blocking operations in frameworks like FastAPI or Discord.py.

---

## 🛠️ Next Steps

- [Synchronous API Reference](./api_sync)
- [Asynchronous API Reference](./api_async)
