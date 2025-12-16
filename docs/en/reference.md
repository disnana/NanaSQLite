# API Reference

Complete API documentation for NanaSQLite.

---

## Class: NanaSQLite

```python
class NanaSQLite(db_path: str, table: str = "data", bulk_load: bool = False,
                 optimize: bool = True, cache_size_mb: int = 64)
```

A dict-like SQLite wrapper with instant persistence and intelligent caching.

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `db_path` | `str` | *required* | Path to SQLite database file |
| `table` | `str` | `"data"` | Table name to use for storage |
| `bulk_load` | `bool` | `False` | Load all data into memory on init |
| `optimize` | `bool` | `True` | Apply performance optimizations |
| `cache_size_mb` | `int` | `64` | SQLite cache size in megabytes |

### Example

```python
# Basic
db = NanaSQLite("mydata.db")

# With bulk loading
db = NanaSQLite("mydata.db", bulk_load=True)

# Custom table
db = NanaSQLite("app.db", table="users")

# Custom cache size
db = NanaSQLite("mydata.db", cache_size_mb=128)
```

---

## Dict Interface

### `__getitem__(key: str) -> Any`

Get a value by key.

```python
value = db["key"]
```

**Raises:** `KeyError` if key does not exist.

---

### `__setitem__(key: str, value: Any) -> None`

Set a value by key. Immediately persisted to SQLite.

```python
db["key"] = {"data": "value"}
```

**Supported types:** `str`, `int`, `float`, `bool`, `None`, `list`, `dict`

---

### `__delitem__(key: str) -> None`

Delete a key. Immediately removed from SQLite.

```python
del db["key"]
```

**Raises:** `KeyError` if key does not exist.

---

### `__contains__(key: str) -> bool`

Check if a key exists.

```python
if "key" in db:
    print("Exists!")
```

---

### `__len__() -> int`

Get the number of keys.

```python
count = len(db)
```

---

### `__iter__() -> Iterator[str]`

Iterate over keys.

```python
for key in db:
    print(key)
```

---

## Dict Methods

### `keys() -> list[str]`

Get all keys.

```python
all_keys = db.keys()
# ['key1', 'key2', 'key3']
```

---

### `values() -> list[Any]`

Get all values. Triggers bulk load.

```python
all_values = db.values()
# [value1, value2, value3]
```

---

### `items() -> list[tuple[str, Any]]`

Get all key-value pairs. Triggers bulk load.

```python
all_items = db.items()
# [('key1', value1), ('key2', value2)]

# Convert to dict
data = dict(db.items())
```

---

### `get(key: str, default: Any = None) -> Any`

Get a value with optional default.

```python
value = db.get("key")  # Returns None if not found
value = db.get("key", "default")  # Returns "default" if not found
```

---

### `pop(key: str, *default) -> Any`

Get and remove a key.

```python
value = db.pop("key")  # Raises KeyError if not found
value = db.pop("key", "default")  # Returns "default" if not found
```

---

### `update(mapping: dict = None, **kwargs) -> None`

Update multiple keys at once.

```python
db.update({"a": 1, "b": 2})
db.update(c=3, d=4)
```

**Note:** For bulk updates, prefer `batch_update()` for better performance.

---

### `setdefault(key: str, default: Any = None) -> Any`

Get value or set default if not exists.

```python
value = db.setdefault("key", "default")
```

---

### `clear() -> None`

Remove all keys.

```python
db.clear()
assert len(db) == 0
```

---

## Special Methods

### `load_all() -> None`

Load all data from SQLite into memory cache.

```python
db.load_all()
# All subsequent reads are from memory
```

---

### `refresh(key: str = None) -> None`

Refresh cache from database.

```python
db.refresh("key")  # Refresh single key
db.refresh()       # Clear entire cache
```

---

### `is_cached(key: str) -> bool`

Check if a key is in memory cache.

```python
if db.is_cached("key"):
    print("Already loaded!")
```

---

### `to_dict() -> dict`

Convert entire database to a regular Python dict.

```python
data = db.to_dict()
# {'key1': value1, 'key2': value2, ...}
```

---

### `close() -> None`

Close the database connection.

```python
db.close()
```

**Note:** Sub-table instances created with `table()` method share the connection, so only the connection owner (the first instance created) will close the connection.

---

### `table(table_name: str) -> NanaSQLite` *(v1.1.0dev1+)*

Get a NanaSQLite instance for a sub-table. Shares the connection and lock.

```python
# Create main instance
db = NanaSQLite("app.db", table="main")

# Get sub-table instances (share connection)
users_db = db.table("users")
config_db = db.table("config")

# Store data independently in each table
users_db["alice"] = {"name": "Alice", "age": 30}
config_db["theme"] = "dark"
```

**Parameters:**
- `table_name` (str): Name of the table to access

**Returns:**
- `NanaSQLite`: A new instance operating on the specified table

**Benefits:**
- **Thread-safe**: Concurrent writes from multiple threads are safe
- **Memory efficient**: Reuses SQLite connection
- **Cache isolation**: Each table maintains independent in-memory cache

---

## Batch Operations

### `batch_update(mapping: dict) -> None`

Bulk write with transaction (10-100x faster than individual writes).

```python
db.batch_update({
    "key1": "value1",
    "key2": "value2",
    "key3": {"nested": "data"}
})
```

---

### `batch_delete(keys: list[str]) -> None`

Bulk delete with transaction.

```python
db.batch_delete(["key1", "key2", "key3"])
```

---

## Context Manager

### `__enter__() / __exit__()`

Use with `with` statement for automatic cleanup.

```python
with NanaSQLite("mydata.db") as db:
    db["key"] = "value"
# Automatically closed
```

---

## Performance Notes

### Write Performance

| Method | Speed | Use Case |
|--------|-------|----------|
| `db[key] = value` | Fast | Single writes |
| `db.update({...})` | Fast | Few keys |
| `db.batch_update({...})` | **Fastest** | Bulk writes (100+ keys) |

### Read Performance

| Mode | Init Time | Read Time | Memory |
|------|-----------|-----------|--------|
| Lazy Load (default) | **Fast** | Slow (first access) | Low |
| Bulk Load | Slow | **Fast** | High |

### Recommendations

1. Use `bulk_load=True` if you read most keys frequently
2. Use `batch_update()` for bulk writes
3. Keep `optimize=True` (default) for best performance
4. Increase `cache_size_mb` for large databases
