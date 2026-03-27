# Quick Reference

Complete API cheat sheet for NanaSQLite.

## Class: NanaSQLite

```python
class NanaSQLite(db_path: str, table: str = "data", bulk_load: bool = False,
                 optimize: bool = True, cache_size_mb: int = 64,
                 strict_sql_validation: bool = True,
                 allowed_sql_functions: list[str] | None = None,
                 forbidden_sql_functions: list[str] | None = None,
                 max_clause_length: int | None = 1000,
                 v2_mode: bool = False,
                 flush_mode: str = "immediate",
                 flush_interval: float = 3.0,
                 flush_count: int = 100,
                 v2_chunk_size: int = 1000,
                 v2_enable_metrics: bool = False)
```

A wrapper class that provides SQLite persistence with a dict-like interface.

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `db_path` | `str` | *Required* | Path to SQLite database file |
| `table` | `str` | `"data"` | Table name used for storage |
| `bulk_load` | `bool` | `False` | Load all data into memory at initialization |
| `optimize` | `bool` | `True` | Apply performance optimizations |
| `cache_size_mb` | `int` | `64` | SQLite cache size (MB) |
| `strict_sql_validation` | `bool` | `True` | Enable strict SQL validation (v1.2.0+) |
| `allowed_sql_functions` | `list` | `None` | List of allowed SQL functions |
| `forbidden_sql_functions` | `list` | `None` | List of forbidden SQL functions |
| `max_clause_length` | `int` | `1000` | Maximum character length for SQL clauses |
| `v2_mode` | `bool` | `False` | Enable v2 architecture (async background writes) (v1.4.0+) |
| `flush_mode` | `str` | `"immediate"` | v2 flush mode (`immediate`, `count`, `time`, `manual`) |
| `flush_interval` | `float` | `3.0` | Flush interval in seconds for `time` mode |
| `flush_count` | `int` | `100` | Write count threshold for `count` mode |
| `v2_chunk_size` | `int` | `1000` | Maximum number of records per flush transaction |
| `v2_enable_metrics` | `bool` | `False` | Collect metrics for v2 engine flushes |

### Usage Examples

```python
# Basic
db = NanaSQLite("mydata.db")

# With Bulk Load
db = NanaSQLite("mydata.db", bulk_load=True)

# Custom Table
db = NanaSQLite("app.db", table="users")

# Custom Cache Size
db = NanaSQLite("mydata.db", cache_size_mb=128)
```

## Dict Interface

### `__getitem__(key: str) -> Any`

Retrieve value by key.

```python
value = db["key"]
```

**Exception:** `KeyError` if key does not exist.

---

### `__setitem__(key: str, value: Any) -> None`

Set value by key. Persists to SQLite immediately.

```python
db["key"] = {"data": "value"}
```

**Supported Types:** `str`, `int`, `float`, `bool`, `None`, `list`, `dict`

---

### `__delitem__(key: str) -> None`

Delete key. Removes from SQLite immediately.

```python
del db["key"]
```

**Exception:** `KeyError` if key does not exist.

---

### `__contains__(key: str) -> bool`

Check existence of key.

```python
if "key" in db:
    print("Exists!")
```

---

### `__len__() -> int`

Get number of keys.

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

Get value with default.

```python
value = db.get("key")  # None if not found
value = db.get("key", "default")  # "default" if not found
```

---

### `pop(key: str, *default) -> Any`

Get value and remove.

```python
value = db.pop("key")  # KeyError if not found
value = db.pop("key", "default")  # "default" if not found
```

---

### `update(mapping: dict = None, **kwargs) -> None`

Update multiple keys at once.

```python
db.update({"a": 1, "b": 2})
db.update(c=3, d=4)
```

::: warning Note
`batch_update()` is recommended for bulk updates.
:::

---

### `setdefault(key: str, default: Any = None) -> Any`

Get value, set default if not exists.

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

## Special Methods

### `load_all() -> None`

Load all data from SQLite into memory cache.

```python
db.load_all()
# Subsequent reads are all from memory
```

---

### `refresh(key: str = None) -> None`

Update cache from database.

```python
db.refresh("key")  # Update single key
db.refresh()       # Clear entire cache
```

---

### `is_cached(key: str) -> bool`

Check if key is in memory cache.

```python
if db.is_cached("key"):
    print("Already loaded!")
```

---

### `flush() -> None` *(v1.4.0+)*

[v2 Feature] Explicitly flush the background buffer to SQLite. No-op if v2 mode is disabled.

```python
db.flush()
```


---

### `to_dict() -> dict`

Convert entire database to a standard Python dict.

```python
data = db.to_dict()
# {'key1': value1, 'key2': value2, ...}
```

---

### `close() -> None`

Close database connection.

```python
db.close()
```

::: warning Note
Helper table instances created by `table()` method share the connection, so only the first created instance (owner) closes the connection.
:::

---

### `table(table_name: str) -> NanaSQLite` *(v1.1.0dev1+)*

Get a NanaSQLite instance for a sub-table. Shares connection and lock.

```python
# Create main instance
db = NanaSQLite("app.db", table="main")

# Get sub-table instance (shares connection)
users_db = db.table("users")
config_db = db.table("config")

# Save data independently to each table
users_db["alice"] = {"name": "Alice", "age": 30}
config_db["theme"] = "dark"
```

**Parameters:**
- `table_name` (str): Table name to retrieve

**Returns:**
- `NanaSQLite`: New instance operating on specified table

**Benefits:**
- **Thread-safe**: Safe concurrent writes from multiple threads
- **Memory efficient**: Reuses SQLite connection
- **Cache isolation**: Independent memory cache for each table

## Batch Operations

### `batch_update(mapping: dict) -> None`

Bulk write in transaction (10-100x faster than individual writes).

```python
db.batch_update({
    "key1": "value1",
    "key2": "value2",
    "key3": {"nested": "data"}
})
```

---

### `batch_delete(keys: list[str]) -> None`

Bulk delete in transaction.

```python
db.batch_delete(["key1", "key2", "key3"])
```

## Context Manager

### `__enter__() / __exit__()`

Auto cleanup with `with` statement.

```python
with NanaSQLite("mydata.db") as db:
    db["key"] = "value"
# Automatically closed
```

## Performance Notes

### Write Performance

| Method | Speed | Use Case |
|--------|-------|----------|
| `db[key] = value` | Fast | Single write |
| `db.update({...})` | Fast | Few keys |
| `db.batch_update({...})` | **Fastest** | Bulk write (100+ keys) |

### Read Performance

| Mode | Init Time | Read Time | Memory |
|------|-----------|-----------|--------|
| Lazy Loading (Default) | **Fast** | Slow (First Access) | Low |
| Bulk Loading | Slow | **Fast** | High |

### Recommendations

1. Use `bulk_load=True` if reading most keys frequently
2. Use `batch_update()` for bulk writes
3. Keep `optimize=True` (Default) for best performance
4. Increase `cache_size_mb` for large databases
