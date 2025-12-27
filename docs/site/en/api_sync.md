# NanaSQLite API Reference

Complete documentation for the synchronous `NanaSQLite` class.

## Class: `NanaSQLite`

```python
class NanaSQLite(MutableMapping)
```

A dictionary-like wrapper for SQLite with instant persistence and intelligent caching.
Designed for use cases where you want the simplicity of a dictionary but the persistence and querying power of SQLite.

---

## Constructor

### `__init__`

```python
def __init__(self, db_path: str, table: str = "data", bulk_load: bool = False,
             optimize: bool = True, cache_size_mb: int = 64,
             strict_sql_validation: bool = True,
             allowed_sql_functions: list[str] | None = None,
             forbidden_sql_functions: list[str] | None = None,
             max_clause_length: int | None = 1000)
```

Initializes the NanaSQLite database connection.

**Parameters:**

- `db_path` (str): Path to the SQLite database file.
- `table` (str, optional): Table name to use for storage. Defaults to `"data"`.
- `bulk_load` (bool, optional): If `True`, loads all data into memory at initialization. Useful for smaller datasets requiring fast read access. Defaults to `False`.
- `optimize` (bool, optional): If `True`, applies performance optimizations such as WAL mode and memory-mapped I/O. Defaults to `True`.
- `cache_size_mb` (int, optional): SQLite cache size in megabytes. Defaults to `64`.
- `strict_sql_validation` (bool, optional): If `True`, rejects queries containing unknown SQL functions to prevent potential injection vectors. Defaults to `True` (v1.2.0+).
- `allowed_sql_functions` (list[str] | None, optional): List of additional SQL functions to allow.
- `forbidden_sql_functions` (list[str] | None, optional): List of SQL functions to explicitly forbid.
- `max_clause_length` (int | None, optional): Maximum length for SQL clauses (ReDoS protection). Defaults to `1000`.

---

## Core Methods

### `close`

```python
def close(self) -> None
```

Closes the database connection.

**Raises:**
- `NanaSQLiteTransactionError`: If called while a transaction is in progress.

**Note:** If the instance was created via `.table()`, only the original connection owner will close the database.

### `table`

```python
def table(self, table_name: str) -> NanaSQLite
```

Returns a new `NanaSQLite` instance for a specific sub-table.

The new instance shares the same underlying connection and lock as the parent, ensuring thread safety and preventing database locking issues.

**Parameters:**
- `table_name` (str): The name of the sub-table.

**Returns:**
- `NanaSQLite`: A new instance targeting the specified table.

---

## Dictionary Interface

NanaSQLite implements the `MutableMapping` interface, so it behaves like a standard Python `dict`.

### `__getitem__`
```python
db["key"]
```
Gets a value. Uses lazy loading (reads from DB if not in memory). Raises `KeyError` if missing.

### `__setitem__`
```python
db["key"] = value
```
Sets a value. Immediately persists to SQLite and updates the in-memory cache.

### `__delitem__`
```python
del db["key"]
```
Deletes a key from both memory and SQLite. Raises `KeyError` if missing.

### `__contains__`
```python
"key" in db
```
Checks existence. Uses an optimized `SELECT 1` query if the key is not in memory.

### `__len__`
```python
len(db)
```
Returns the total number of keys in the database.

### `get`
```python
def get(self, key: str, default: Any = None) -> Any
```
Returns the value for `key` if it exists, else `default`.

### `setdefault`
```python
def setdefault(self, key: str, default: Any = None) -> Any
```
If `key` is in the database, returns its value. If not, inserts `key` with a value of `default` and returns `default`.

### `pop`
```python
def pop(self, key: str, *args) -> Any
```
Removes `key` and returns its value. If `key` is not found, returns `default` if provided, otherwise raises `KeyError`.

### `update`
```python
def update(self, mapping: dict = None, **kwargs) -> None
```
Updates the database with keys and values from `mapping` or keywords. For bulk updates, consider using `batch_update()` for better performance.

### `clear`
```python
def clear(self) -> None
```
Removes all items from the database (truncates the table) and clears the memory cache.

### `keys`
```python
def keys(self) -> list[str]
```
Returns a list of all keys in the database.

### `values`
```python
def values(self) -> list[Any]
```
Returns a list of all values. **Triggers a full bulk load.**

### `items`
```python
def items(self) -> list[tuple[str, Any]]
```
Returns a list of all (key, value) pairs. **Triggers a full bulk load.**

### `to_dict`
```python
def to_dict(self) -> dict
```
Converts the entire database to a standard Python dictionary.

### `copy`
```python
def copy(self) -> dict
```
Returns a shallow copy of the database as a dictionary (alias for `to_dict()`).

---

## Data Management

### `load_all`

```python
def load_all(self) -> None
```

Loads all data from the database into the memory cache. Subsequent reads will be memory-only (fast).

### `refresh`

```python
def refresh(self, key: str = None) -> None
```

Refreshes the internal cache from the database.

**Parameters:**
- `key` (str, optional): If provided, refreshes only that specific key. If `None`, clears and reloads the entire cache state.

### `get_fresh`

```python
def get_fresh(self, key: str, default: Any = None) -> Any
```

Accesses the database directly to get the latest value, bypassing the cache, and then updates the cache.

### `batch_get`

```python
def batch_get(self, keys: list[str]) -> dict[str, Any]
```

Efficiently retrieves multiple keys in a single query.

### `batch_update`

```python
def batch_update(self, mapping: dict[str, Any]) -> None
```

Performs a bulk write operation using a single transaction. Significantly faster (10-100x) than individual updates.

### `batch_delete`

```python
def batch_delete(self, keys: list[str]) -> None
```

Performs a bulk delete operation using a single transaction.

### `is_cached`

```python
def is_cached(self, key: str) -> bool
```

Checks if a key is currently loaded in the memory cache.

---

## Transaction Control

### `begin_transaction`

```python
def begin_transaction(self) -> None
```
Starts a manual transaction (`BEGIN IMMEDIATE`).
**Raises:** `NanaSQLiteTransactionError` if a transaction is already in progress.

### `commit`

```python
def commit(self) -> None
```
Commits the current transaction.

### `rollback`

```python
def rollback(self) -> None
```
Rolls back the current transaction.

### `in_transaction`

```python
def in_transaction(self) -> bool
```
Returns `True` if a transaction is currently in progress.

### `transaction`

```python
def transaction(self)
```
Context manager for automatic transaction handling.
Commits on success, rolls back on exception.

```python
with db.transaction():
    db["a"] = 1
    db["b"] = 2
```

---

## SQL Wrappers (CRUD)

Helper methods for executing common SQL operations safely without writing raw SQL.

### `sql_insert`

```python
def sql_insert(self, table_name: str, data: dict) -> int
```
Inserts a new row into the specified table.
**Returns:** The `ROWID` of the inserted row.

### `sql_update`

```python
def sql_update(self, table_name: str, data: dict, where: str, parameters: tuple = None) -> int
```
Updates rows matching the `where` clause.
**Returns:** The number of affected rows.

### `sql_delete`

```python
def sql_delete(self, table_name: str, where: str, parameters: tuple = None) -> int
```
Deletes rows matching the `where` clause.
**Returns:** The number of affected rows.

### `upsert`

```python
def upsert(self, table_name: str, data: dict, conflict_columns: list[str] = None) -> int
```
Performs an "Insert or Replace" or "Insert ... ON CONFLICT DO UPDATE" operation.

**Parameters:**
- `conflict_columns`: If provided, generates `ON CONFLICT (...) DO UPDATE`. If `None`, uses `INSERT OR REPLACE`.

---

## Querying

### `query`

```python
def query(self, table_name: str = None, columns: list[str] = None,
          where: str = None, parameters: tuple = None,
          order_by: str = None, limit: int = None,
          strict_sql_validation: bool = None, ...) -> list[dict]
```

Executes a `SELECT` query and returns the results as a list of dictionaries.

**Parameters:**
- `table_name`: Target table. Defaults to the main data table.
- `columns`: List of columns to select. Defaults to `*`.
- `where`: SQL `WHERE` clause (without the word "WHERE").
- `parameters`: Tuple of values for placeholders in the `where` clause.
- `limit`: Maximum number of rows to return.

### `query_with_pagination`

```python
def query_with_pagination(self, table_name: str = None, ..., offset: int = None, group_by: str = None) -> list[dict]
```

Extended version of `query` that supports `offset` (pagination) and `group_by`.

### `count`

```python
def count(self, table_name: str = None, where: str = None, parameters: tuple = None, ...) -> int
```
Returns the count of rows matching the criteria.

### `exists`

```python
def exists(self, table_name: str, where: str, parameters: tuple = None) -> bool
```
Checks efficiently if any row matches the criteria (uses `SELECT 1 ... LIMIT 1`).

---

## Direct SQL Execution

### `execute`

```python
def execute(self, sql: str, parameters: tuple | None = None) -> apsw.Cursor
```
Executes a raw SQL statement.
**Returns:** `apsw.Cursor` object.

### `execute_many`

```python
def execute_many(self, sql: str, parameters_list: list[tuple]) -> None
```
Executes the same SQL statement multiple times with different parameters (bulk execution).

### `fetch_one`

```python
def fetch_one(self, sql: str, parameters: tuple = None) -> tuple | None
```
Executes SQL and returns the first row (or `None`).

### `fetch_all`

```python
def fetch_all(self, sql: str, parameters: tuple = None) -> list[tuple]
```
Executes SQL and returns all rows.

---

## Schema Management

### `create_table`

```python
def create_table(self, table_name: str, columns: dict, if_not_exists: bool = True, primary_key: str = None) -> None
```
Creates a new table.
**Example:** `db.create_table("users", {"id": "INTEGER", "name": "TEXT"}, primary_key="id")`

### `create_index`

```python
def create_index(self, index_name: str, table_name: str, columns: list[str], unique: bool = False, if_not_exists: bool = True) -> None
```
Creates an index on a table.

### `alter_table_add_column`

```python
def alter_table_add_column(self, table_name: str, column_name: str, column_type: str, default: Any = None) -> None
```
Adds a column to an existing table.

### `drop_table`

```python
def drop_table(self, table_name: str, if_exists: bool = True) -> None
```
Drops (deletes) a table.

### `drop_index`

```python
def drop_index(self, index_name: str, if_exists: bool = True) -> None
```
Drops an index.

### `list_tables`

```python
def list_tables(self) -> list[str]
```
Returns a list of all tables in the database.

### `list_indexes`

```python
def list_indexes(self, table_name: str = None) -> list[dict]
```
Returns a list of indexes (optionally filtered by table).

### `get_table_schema`

```python
def get_table_schema(self, table_name: str) -> list[dict]
```
Returns detailed schema information for a table.

### `table_exists`

```python
def table_exists(self, table_name: str) -> bool
```
Checks if a table exists.

---

## Utility Functions

### `vacuum`

```python
def vacuum(self) -> None
```
Optimizes the database file to reduce size (runs `VACUUM`).

### `get_db_size`

```python
def get_db_size(self) -> int
```
Returns the database file size in bytes.

### `pragma`

```python
def pragma(self, pragma_name: str, value: Any = None) -> Any
```
Gets or sets a SQLite PRAGMA value.

### `get_last_insert_rowid`

```python
def get_last_insert_rowid(self) -> int
```
Returns the `ROWID` of the last inserted row.

---

## Pydantic Support

### `set_model`

```python
def set_model(self, key: str, model: Any) -> None
```
Serializes and stores a Pydantic model.

### `get_model`

```python
def get_model(self, key: str, model_class: type = None) -> Any
```
Retrieves and deserializes a Pydantic model.
