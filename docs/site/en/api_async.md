# AsyncNanaSQLite API Reference

Complete documentation for the asynchronous `AsyncNanaSQLite` class.

## Class: `AsyncNanaSQLite`

```python
class AsyncNanaSQLite
```

A non-blocking, async wrapper for `NanaSQLite`.
It delegates all database operations to a thread pool executor, ensuring that the main asyncio event loop is never blocked. This is essential for high-concurrency applications like FastAPI or discord.py bots.

---

## Constructor

### `__init__`

```python
def __init__(
    self,
    db_path: str,
    table: str = "data",
    bulk_load: bool = False,
    optimize: bool = True,
    cache_size_mb: int = 64,
    max_workers: int = 5,
    thread_name_prefix: str = "AsyncNanaSQLite",
    strict_sql_validation: bool = True,
    allowed_sql_functions: list[str] | None = None,
    forbidden_sql_functions: list[str] | None = None,
    max_clause_length: int | None = 1000,
    read_pool_size: int = 0,
    cache_strategy: CacheType = CacheType.UNBOUNDED,
    cache_size: int = 0,
    cache_ttl: float | None = None,
    cache_persistence_ttl: bool = False,
    encryption_key: str | bytes | None = None,
    encryption_mode: str = "aes-gcm",
)
```

Initializes the AsyncNanaSQLite interface.

**Parameters:**

- `db_path` (str): Path to the SQLite database file.
- `table` (str, optional): Table name to use for storage. Defaults to `"data"`.
- `max_workers` (int, optional): Maximum number of threads in the thread pool. Defaults to `5`.
  - Increase this for high-concurrency read workloads.
- `read_pool_size` (int, optional): Size of the dedicated read-only connection pool. Defaults to `0` (disabled).
  - Enable this (e.g., `read_pool_size=4`) to allow concurrent reads to bypass the write lock.
- `cache_strategy` (CacheType, optional): `CacheType.UNBOUNDED` / `LRU` / `TTL`. (v1.3.0+)
- `cache_size` (int, optional): Max items for cache.
- `cache_ttl` (float, optional): TTL in seconds.
- `cache_persistence_ttl` (bool, optional): Automatic DB deletion on TTL expiry.
- `encryption_key` (str | bytes, optional): Encryption key. (v1.3.1+)
- `encryption_mode` (str, optional): `"aes-gcm"` (default), `"chacha20"`, `"fernet"`.
- `strict_sql_validation` etc.: Same security parameters as `NanaSQLite`.

---

## Core Methods

### `close`

```python
async def close(self) -> None
```

Closes the database connection and shuts down the thread pool.

### `table`

```python
async def table(self, table_name: str) -> AsyncNanaSQLite
```

Asynchronously creates a new `AsyncNanaSQLite` instance for a sub-table.
Shares the thread pool and connection with the parent.

---

## Async Dict-like Interface

These methods mirror standard dictionary operations but are `async`.

### `aget` (Alias: `get`)
```python
async def aget(self, key: str, default: Any = None) -> Any
```
Asynchronously retrieves a value.

### `aset`
```python
async def aset(self, key: str, value: Any) -> None
```
Asynchronously sets a value.

### `adelete`
```python
async def adelete(self, key: str) -> None
```
Asynchronously deletes a key.

### `acontains` (Alias: `contains`)
```python
async def acontains(self, key: str) -> bool
```
Asynchronously checks for key existence.

### `alen`
```python
async def alen(self) -> int
```
Asynchronously returns the number of items.

### `akeys` (Alias: `keys`)
```python
async def akeys(self) -> list[str]
```
Asynchronously returns all keys.

### `avalues` (Alias: `values`)
```python
async def avalues(self) -> list[Any]
```
Asynchronously returns all values.

### `aitems` (Alias: `items`)
```python
async def aitems(self) -> list[tuple[str, Any]]
```
Asynchronously returns all items.

### `aupdate`
```python
async def aupdate(self, mapping: dict = None, **kwargs) -> None
```
Asynchronously updates multiple keys.

### `aclear`
```python
async def aclear(self) -> None
```
Asynchronously effectively clears the database.

### `apop`
```python
async def apop(self, key: str, *args) -> Any
```
Asynchronously pops a value.

### `asetdefault`
```python
async def asetdefault(self, key: str, default: Any = None) -> Any
```
Asynchronously sets a default value if missing.

---

## Data Management

### `load_all`

```python
async def load_all(self) -> None
```
Loads all data into memory asynchronously.

### `refresh`

```python
async def refresh(self, key: str = None) -> None
```
Asynchronously refreshes the cache.

### `get_fresh`

```python
async def get_fresh(self, key: str, default: Any = None) -> Any
```
Asynchronously fetches fresh data from DB.

### `batch_update`

```python
async def batch_update(self, mapping: dict[str, Any]) -> None
```
Asynchronous bulk update.

### `batch_delete`

```python
async def batch_delete(self, keys: list[str]) -> None
```
Asynchronous bulk delete.

### `abatch_get`

```python
async def abatch_get(self, keys: list[str]) -> dict[str, Any]
```
Asynchronous bulk get.

---

## Transaction Control

### `begin_transaction`

```python
async def begin_transaction(self) -> None
```
Starts a transaction.

### `commit`

```python
async def commit(self) -> None
```
Commits a transaction.

### `rollback`

```python
async def rollback(self) -> None
```
Rolls back a transaction.

### `in_transaction`

```python
async def in_transaction(self) -> bool
```
Checks transaction status.

### `transaction`

```python
def transaction(self)
```
Async context manager for transactions.

```python
async with db.transaction():
    await db.aset("a", 1)
```

---

## Querying & SQL

All SQL and query methods available in `NanaSQLite` are available here as `async` methods.

### `query` (Alias: `aquery`)
```python
async def query(self, table_name: str, columns: list[str] | None = None, where: str | None = None, parameters: tuple = None, order_by: str | None = None, limit: int | None = None) -> list[dict]
```

### `query_with_pagination` (Alias: `aquery_with_pagination`)
```python
async def query_with_pagination(self, table_name: str, columns: list[str] | None = None, where: str | None = None, parameters: tuple = None, order_by: str | None = None, limit: int = 20, offset: int = 0, group_by: str | None = None) -> list[dict]
```

### `execute` (Alias: `aexecute`)
```python
async def execute(self, sql: str, parameters: tuple | None = None) -> Any
```

### `execute_many` (Alias: `aexecute_many`)
```python
async def execute_many(self, sql: str, parameters: list[tuple]) -> None
```

### `fetch_all` (Alias: `afetch_all`)
```python
async def fetch_all(self, sql: str, parameters: tuple = None) -> list[tuple]
```

### `fetch_one` (Alias: `afetch_one`)
```python
async def fetch_one(self, sql: str, parameters: tuple = None) -> tuple | None
```

### `sql_insert` (Alias: `asql_insert`)
```python
async def sql_insert(self, table_name: str, data: dict) -> int
```

### `sql_update` (Alias: `asql_update`)
```python
async def sql_update(self, table_name: str, data: dict, where: str, parameters: tuple = None) -> None
```

### `sql_delete` (Alias: `asql_delete`)
```python
async def sql_delete(self, table_name: str, where: str, parameters: tuple = None) -> None
```

### `upsert` (Alias: `aupsert`)
```python
async def upsert(self, table_name: str, data: dict, unique_keys: list[str]) -> None
```

### `count` (Alias: `acount`)
```python
async def count(self, table_name: str, where: str | None = None, parameters: tuple = None) -> int
```

### `exists` (Alias: `aexists`)
```python
async def exists(self, table_name: str, where: str, parameters: tuple = None) -> bool
```

### `create_table`
```python
async def create_table(self, table_name: str, schema: dict[str, str]) -> None
```

### `drop_table`
```python
async def drop_table(self, table_name: str) -> None
```

### `create_index`
```python
async def create_index(self, index_name: str, table_name: str, columns: list[str], unique: bool = False) -> None
```

### `drop_index`
```python
async def drop_index(self, index_name: str) -> None
```

### `alter_table_add_column`
```python
async def alter_table_add_column(self, table_name: str, column_name: str, column_type: str) -> None
```

### `get_table_schema`
```python
async def get_table_schema(self, table_name: str) -> list[dict]
```

### `list_tables`
```python
async def list_tables(self) -> list[str]
```

### `table_exists`
```python
async def table_exists(self, table_name: str) -> bool
```

### `list_indexes`
```python
async def list_indexes(self, table_name: str | None = None) -> list[dict]
```

### `vacuum`
```python
async def vacuum(self) -> None
```

### `get_db_size`
```python
async def get_db_size(self) -> int
```

### `export_table_to_dict`
```python
async def export_table_to_dict(self, table_name: str) -> dict[str, Any]
```

### `import_from_dict_list`
```python
async def import_from_dict_list(self, table_name: str, data: list[dict], unique_keys: list[str] = None) -> None
```

### `get_last_insert_rowid`
```python
async def get_last_insert_rowid(self) -> int
```

### `pragma`
```python
async def pragma(self, name: str, value: Any = None) -> Any
```

---

## Pydantic Support

### `set_model`

```python
async def set_model(self, key: str, model: Any) -> None
```

### `get_model`

```python
async def get_model(self, key: str, model_class: type = None) -> Any
```

---

## Advanced

### `sync_db`

```python
@property
def sync_db(self) -> NanaSQLite | None
```
Access to the underlying synchronous `NanaSQLite` instance.
**Warning**: Calling methods on `sync_db` from an async function will block the event loop. Use with caution.
