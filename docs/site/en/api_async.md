# Asynchronous API Reference

Reference for the asynchronous AsyncNanaSQLite class.

## AsyncNanaSQLite

```python
class AsyncNanaSQLite(db_path: str, table: str = 'data', bulk_load: bool = False, optimize: bool = True, cache_size_mb: int = 64, max_workers: int = 5, thread_name_prefix: str = 'AsyncNanaSQLite', strict_sql_validation: bool = True, allowed_sql_functions: list[str] | None = None, forbidden_sql_functions: list[str] | None = None, max_clause_length: int | None = 1000, read_pool_size: int = 0, cache_strategy: CacheType | str = <CacheType.UNBOUNDED: unbounded>, cache_size: int | None = None, cache_ttl: float | None = None, cache_persistence_ttl: bool = False, encryption_key: str | bytes | None = None, encryption_mode: Literal['aes-gcm', 'chacha20', 'fernet'] = 'aes-gcm', validator: Any | None = None, coerce: bool = False, v2_mode: bool = False, flush_mode: Literal['immediate', 'count', 'time', 'manual'] = 'immediate', flush_interval: float = 3.0, flush_count: int = 100, v2_chunk_size: int = 1000, v2_enable_metrics: bool = False) -> None
```

Async wrapper for NanaSQLite with optimized thread pool executor.

All database operations are executed in a dedicated thread pool executor to prevent
blocking the async event loop. This allows NanaSQLite to be used safely
in async applications like FastAPI, aiohttp, etc.

The implementation uses a configurable thread pool for optimal concurrency
and performance in high-load scenarios.

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `db_path` | `str` |  |
| `table` | `str` |  |
| `bulk_load` | `bool` |  |
| `optimize` | `bool` |  |
| `cache_size_mb` | `int` |  |
| `max_workers` | `int` |  |
| `thread_name_prefix` | `str` |  |
| `strict_sql_validation` | `bool` |  |
| `allowed_sql_functions` | `list[str] | None` |  |
| `forbidden_sql_functions` | `list[str] | None` |  |
| `max_clause_length` | `int | None` |  |
| `read_pool_size` | `int` |  |
| `cache_strategy` | `CacheType | str` |  |
| `cache_size` | `int | None` |  |
| `cache_ttl` | `float | None` |  |
| `cache_persistence_ttl` | `bool` |  |
| `encryption_key` | `str | bytes | None` |  |
| `encryption_mode` | `Literal[aes-gcm, chacha20, fernet]` |  |
| `validator` | `Any | None` |  |
| `coerce` | `bool` | ``True`` の場合、validkit-py の自動変換機能を有効にする。 バリデーション後、変換済みの値をDBに書き込む。デフォルト: ``False``。 |
| `v2_mode` | `bool` |  |
| `flush_mode` | `Literal[immediate, count, time, manual]` |  |
| `flush_interval` | `float` |  |
| `flush_count` | `int` |  |
| `v2_chunk_size` | `int` |  |
| `v2_enable_metrics` | `bool` |  |

::: tip Example
```python
    async with AsyncNanaSQLite("mydata.db") as db:
        await db.aset("config", {"theme": "dark"})
        config = await db.aget("config")
        print(config)
```

```python
    # 高負荷環境向けの設定
    async with AsyncNanaSQLite("mydata.db", max_workers=10) as db:
        # 並行処理が多い場合に最適化
        results = await asyncio.gather(*[db.aget(f"key_{i}") for i in range(100)])
```

:::


---

## Constructor

## Core Methods

### `close`

```python
def close() -> None
```

::: tip Example
```python
    await db.close()
```
:::


---

### `table`

```python
def table(table_name: str, validator: Any | None | types.EllipsisType = Ellipsis, coerce: bool | types.EllipsisType = Ellipsis) -> AsyncNanaSQLite
```

sub1 = await db.table("users")

    users_db = await db.table("users")

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `validator` | `Any | None | types.EllipsisType` |  |
| `coerce` | `bool | types.EllipsisType` | ``True`` の場合、validkit-py の自動変換機能を有効にする。 |

#### Returns

**Type:** `AsyncNanaSQLite`

::: tip Example
```python
    async with AsyncNanaSQLite("mydata.db", table="main") as db:
        users_db = await db.table("users")
        products_db = await db.table("products")
        await users_db.aset("user1", {"name": "Alice"})
        await products_db.aset("prod1", {"name": "Laptop"})
```
:::


---

## Dictionary Interface

### `get`

```python
def get(key: str, default: Any = None) -> Any
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

#### Returns

::: tip Example
```python
    user = await db.aget("user")
    config = await db.aget("config", {})
```
:::


---

### `keys`

```python
def keys() -> list[str]
```

#### Returns

**Type:** `list[str]`

::: tip Example
```python
    keys = await db.akeys()
```
:::


---

### `values`

```python
def values() -> list[Any]
```

#### Returns

**Type:** `list[Any]`

::: tip Example
```python
    values = await db.avalues()
```
:::


---

### `items`

```python
def items() -> list[tuple[str, Any]]
```

#### Returns

**Type:** `list[tuple[str, Any]]`

::: tip Example
```python
    items = await db.aitems()
```
:::


---

### `to_dict`

```python
def to_dict() -> dict
```

#### Returns

**Type:** `dict`

::: tip Example
```python
    data = await db.to_dict()
```
:::


---

### `copy`

```python
def copy() -> dict
```

#### Returns

**Type:** `dict`

::: tip Example
```python
    data_copy = await db.copy()
```
:::


---

### `clear_cache`

```python
def clear_cache() -> None
```




---

## Data Management

### `load_all`

```python
def load_all() -> None
```

::: tip Example
```python
    await db.load_all()
```
:::


---

### `refresh`

```python
def refresh(key: str = None) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

::: tip Example
```python
    await db.refresh("user")
    await db.refresh()  # 全キャッシュ更新
```
:::


---

### `is_cached`

```python
def is_cached(key: str) -> bool
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

#### Returns

**Type:** `bool`

::: tip Example
```python
    cached = await db.is_cached("user")
```
:::


---

### `batch_update`

```python
def batch_update(mapping: dict[str, Any]) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `mapping` | `dict[str, Any]` |  |

::: tip Example
```python
    await db.batch_update({
        "key1": "value1",
        "key2": "value2",
        "key3": {"nested": "data"}
    })
```
:::


---

### `batch_update_partial`

```python
def batch_update_partial(mapping: dict[str, Any]) -> dict[str, str]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `mapping` | `dict[str, Any]` |  |



---

### `batch_delete`

```python
def batch_delete(keys: list[str]) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `keys` | `list[str]` |  |

::: tip Example
```python
    await db.batch_delete(["key1", "key2", "key3"])
```
:::


---

### `get_fresh`

```python
def get_fresh(key: str, default: Any = None) -> Any
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

#### Returns

::: tip Example
```python
    value = await db.get_fresh("key")
```
:::


---

### `aflush`

```python
def aflush() -> None
```




---

### `flush`

```python
def flush() -> None
```




---

### `aget_dlq`

```python
def aget_dlq() -> list[dict[str, Any]]
```




---

### `get_dlq`

```python
def get_dlq() -> list[dict[str, Any]]
```




---

### `aretry_dlq`

```python
def aretry_dlq() -> None
```




---

### `retry_dlq`

```python
def retry_dlq() -> None
```




---

### `aclear_dlq`

```python
def aclear_dlq() -> None
```




---

### `clear_dlq`

```python
def clear_dlq() -> None
```




---

### `aget_v2_metrics`

```python
def aget_v2_metrics() -> dict[str, Any]
```




---

### `get_v2_metrics`

```python
def get_v2_metrics() -> dict[str, Any]
```




---

## Transaction Control

### `begin_transaction`

```python
def begin_transaction() -> None
```

::: tip Example
```python
    await db.begin_transaction()
    try:
        await db.sql_insert("users", {"name": "Alice"})
        await db.sql_insert("users", {"name": "Bob"})
        await db.commit()
    except:
        await db.rollback()
```
:::


---

### `commit`

```python
def commit() -> None
```

::: tip Example
```python
    await db.commit()
```
:::


---

### `rollback`

```python
def rollback() -> None
```

::: tip Example
```python
    await db.rollback()
```
:::


---

### `in_transaction`

```python
def in_transaction() -> bool
```

#### Returns

**Type:** `bool`

::: tip Example
```python
    status = await db.in_transaction()
    print(f"In transaction: {status}")
```
:::


---

### `transaction`

```python
def transaction()
```

::: tip Example
```python
    async with db.transaction():
        await db.sql_insert("users", {"name": "Alice"})
        await db.sql_insert("users", {"name": "Bob"})
        # 自動的にコミット、例外時はロールバック
```
:::


---

## SQL Wrapper (CRUD)

### `sql_insert`

```python
def sql_insert(table_name: str, data: dict) -> int
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `data` | `dict` |  |

#### Returns

**Type:** `int`

::: tip Example
```python
    rowid = await db.sql_insert("users", {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 25
    })
```
:::


---

### `sql_update`

```python
def sql_update(table_name: str, data: dict, where: str, parameters: tuple | None = None) -> int
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `data` | `dict` |  |
| `where` | `str` |  |
| `parameters` | `tuple | None` |  |

#### Returns

**Type:** `int`

::: tip Example
```python
    count = await db.sql_update("users",
        {"age": 26, "status": "active"},
        "name = ?",
        ("Alice",)
    )
```
:::


---

### `sql_delete`

```python
def sql_delete(table_name: str, where: str, parameters: tuple | None = None) -> int
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `where` | `str` |  |
| `parameters` | `tuple | None` |  |

#### Returns

**Type:** `int`

::: tip Example
```python
    count = await db.sql_delete("users", "age < ?", (18,))
```
:::


---

## Query

### `query`

```python
def query(table_name: str = None, columns: list[str] = None, where: str = None, parameters: tuple | None = None, order_by: str = None, limit: int = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> list[dict]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `columns` | `list[str]` |  |
| `where` | `str` |  |
| `parameters` | `tuple | None` |  |
| `order_by` | `str` |  |
| `limit` | `int` |  |
| `strict_sql_validation` | `bool` |  |
| `allowed_sql_functions` | `list[str]` |  |
| `forbidden_sql_functions` | `list[str]` |  |
| `override_allowed` | `bool` |  |

#### Returns

**Type:** `list[dict]`

::: tip Example
```python
    results = await db.query(
        table_name="users",
        columns=["id", "name", "email"],
        where="age > ?",
        parameters=(20,),
        order_by="name ASC",
        limit=10
    )
```
:::


---

### `query_with_pagination`

```python
def query_with_pagination(table_name: str = None, columns: list[str] = None, where: str = None, parameters: tuple | None = None, order_by: str = None, limit: int = None, offset: int = None, group_by: str = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> list[dict]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `columns` | `list[str]` |  |
| `where` | `str` |  |
| `parameters` | `tuple | None` |  |
| `order_by` | `str` |  |
| `limit` | `int` |  |
| `offset` | `int` |  |
| `group_by` | `str` |  |
| `strict_sql_validation` | `bool` |  |
| `allowed_sql_functions` | `list[str]` |  |
| `forbidden_sql_functions` | `list[str]` |  |
| `override_allowed` | `bool` |  |

#### Returns

**Type:** `list[dict]`

::: tip Example
```python
    results = await db.query_with_pagination(
        table_name="users",
        columns=["id", "name", "email"],
        where="age > ?",
        parameters=(20,),
        order_by="name ASC",
        limit=10,
        offset=0
    )
```
:::


---

### `count`

```python
def count(table_name: str = None, where: str = None, parameters: tuple | None = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> int
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `where` | `str` |  |
| `parameters` | `tuple | None` |  |
| `strict_sql_validation` | `bool` |  |
| `allowed_sql_functions` | `list[str]` |  |
| `forbidden_sql_functions` | `list[str]` |  |
| `override_allowed` | `bool` |  |

#### Returns

**Type:** `int`

::: tip Example
```python
    count = await db.count("users", "age < ?", (18,))
```
:::


---

## Direct SQL Execution

### `execute`

```python
def execute(sql: str, parameters: tuple | None = None) -> Any
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `sql` | `str` |  |
| `parameters` | `tuple | None` |  |

#### Returns

::: tip Example
```python
    cursor = await db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
```
:::


---

### `execute_many`

```python
def execute_many(sql: str, parameters_list: list[tuple]) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `sql` | `str` |  |
| `parameters_list` | `list[tuple]` |  |

::: tip Example
```python
    await db.execute_many(
        "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
        [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
    )
```
:::


---

### `fetch_one`

```python
def fetch_one(sql: str, parameters: tuple | None = None) -> tuple | None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `sql` | `str` |  |
| `parameters` | `tuple | None` |  |

#### Returns

**Type:** `tuple | None`

::: tip Example
```python
    row = await db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
```
:::


---

### `fetch_all`

```python
def fetch_all(sql: str, parameters: tuple | None = None) -> list[tuple]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `sql` | `str` |  |
| `parameters` | `tuple | None` |  |

#### Returns

**Type:** `list[tuple]`

::: tip Example
```python
    rows = await db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
```
:::


---

## Schema Management

### `create_table`

```python
def create_table(table_name: str, columns: dict, if_not_exists: bool = True, primary_key: str = None) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `columns` | `dict` |  |
| `if_not_exists` | `bool` |  |
| `primary_key` | `str` |  |

::: tip Example
```python
    await db.create_table("users", {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "email": "TEXT UNIQUE"
    })
```
:::


---

### `create_index`

```python
def create_index(index_name: str, table_name: str, columns: list[str], unique: bool = False, if_not_exists: bool = True) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `index_name` | `str` |  |
| `table_name` | `str` |  |
| `columns` | `list[str]` |  |
| `unique` | `bool` |  |
| `if_not_exists` | `bool` |  |

::: tip Example
```python
    await db.create_index("idx_users_email", "users", ["email"], unique=True)
```
:::


---

### `table_exists`

```python
def table_exists(table_name: str) -> bool
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |

#### Returns

**Type:** `bool`

::: tip Example
```python
    exists = await db.table_exists("users")
```
:::


---

### `list_tables`

```python
def list_tables() -> list[str]
```

#### Returns

**Type:** `list[str]`

::: tip Example
```python
    tables = await db.list_tables()
```
:::


---

### `drop_table`

```python
def drop_table(table_name: str, if_exists: bool = True) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `if_exists` | `bool` |  |

::: tip Example
```python
    await db.drop_table("old_table")
```
:::


---

### `drop_index`

```python
def drop_index(index_name: str, if_exists: bool = True) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `index_name` | `str` |  |
| `if_exists` | `bool` |  |

::: tip Example
```python
    await db.drop_index("idx_users_email")
```
:::


---

## Utility Functions

### `vacuum`

```python
def vacuum() -> None
```

::: tip Example
```python
    await db.vacuum()
```
:::


---

## Pydantic Support

### `set_model`

```python
def set_model(key: str, model: Any) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

::: tip Example
```python
    from pydantic import BaseModel
    class User(BaseModel):
        name: str
        age: int
    user = User(name="Nana", age=20)
    await db.set_model("user", user)
```
:::


---

### `get_model`

```python
def get_model(key: str, model_class: type = None) -> Any
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |
| `model_class` | `type` |  |

#### Returns

::: tip Example
```python
    user = await db.get_model("user", User)
```
:::


---

## Other Methods

### `aget`

```python
def aget(key: str, default: Any = None) -> Any
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

#### Returns

::: tip Example
```python
    user = await db.aget("user")
    config = await db.aget("config", {})
```
:::


---

### `aset`

```python
def aset(key: str, value: Any) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

::: tip Example
```python
    await db.aset("user", {"name": "Nana", "age": 20})
```
:::


---

### `adelete`

```python
def adelete(key: str) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

::: warning Raises
:::

::: tip Example
```python
    await db.adelete("old_data")
```
:::


---

### `acontains`

```python
def acontains(key: str) -> bool
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

#### Returns

**Type:** `bool`

::: tip Example
```python
    if await db.acontains("user"):
        print("User exists")
```
:::


---

### `contains`

```python
def contains(key: str) -> bool
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

#### Returns

**Type:** `bool`

::: tip Example
```python
    if await db.acontains("user"):
        print("User exists")
```
:::


---

### `alen`

```python
def alen() -> int
```

#### Returns

**Type:** `int`

::: tip Example
```python
    count = await db.alen()
```
:::


---

### `akeys`

```python
def akeys() -> list[str]
```

#### Returns

**Type:** `list[str]`

::: tip Example
```python
    keys = await db.akeys()
```
:::


---

### `avalues`

```python
def avalues() -> list[Any]
```

#### Returns

**Type:** `list[Any]`

::: tip Example
```python
    values = await db.avalues()
```
:::


---

### `aitems`

```python
def aitems() -> list[tuple[str, Any]]
```

#### Returns

**Type:** `list[tuple[str, Any]]`

::: tip Example
```python
    items = await db.aitems()
```
:::


---

### `apop`

```python
def apop(key: str, *args) -> Any
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

#### Returns

::: tip Example
```python
    value = await db.apop("temp_data")
    value = await db.apop("maybe_missing", "default")
```
:::


---

### `aupdate`

```python
def aupdate(mapping: dict = None, **kwargs) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `mapping` | `dict` |  |

::: tip Example
```python
    await db.aupdate({"key1": "value1", "key2": "value2"})
    await db.aupdate(key3="value3", key4="value4")
```
:::


---

### `aclear`

```python
def aclear() -> None
```

::: tip Example
```python
    await db.aclear()
```
:::


---

### `asetdefault`

```python
def asetdefault(key: str, default: Any = None) -> Any
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

#### Returns

::: tip Example
```python
    value = await db.asetdefault("config", {})
```
:::


---

### `aload_all`

```python
def aload_all() -> None
```

::: tip Example
```python
    await db.load_all()
```
:::


---

### `arefresh`

```python
def arefresh(key: str = None) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

::: tip Example
```python
    await db.refresh("user")
    await db.refresh()  # 全キャッシュ更新
```
:::


---

### `ais_cached`

```python
def ais_cached(key: str) -> bool
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

#### Returns

**Type:** `bool`

::: tip Example
```python
    cached = await db.is_cached("user")
```
:::


---

### `abatch_update`

```python
def abatch_update(mapping: dict[str, Any]) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `mapping` | `dict[str, Any]` |  |

::: tip Example
```python
    await db.batch_update({
        "key1": "value1",
        "key2": "value2",
        "key3": {"nested": "data"}
    })
```
:::


---

### `abatch_update_partial`

```python
def abatch_update_partial(mapping: dict[str, Any]) -> dict[str, str]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `mapping` | `dict[str, Any]` |  |



---

### `abatch_delete`

```python
def abatch_delete(keys: list[str]) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `keys` | `list[str]` |  |

::: tip Example
```python
    await db.batch_delete(["key1", "key2", "key3"])
```
:::


---

### `ato_dict`

```python
def ato_dict() -> dict
```

#### Returns

**Type:** `dict`

::: tip Example
```python
    data = await db.to_dict()
```
:::


---

### `acopy`

```python
def acopy() -> dict
```

#### Returns

**Type:** `dict`

::: tip Example
```python
    data_copy = await db.copy()
```
:::


---

### `aget_fresh`

```python
def aget_fresh(key: str, default: Any = None) -> Any
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

#### Returns

::: tip Example
```python
    value = await db.get_fresh("key")
```
:::


---

### `abatch_get`

```python
def abatch_get(keys: list[str]) -> dict[str, Any]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `keys` | `list[str]` |  |

#### Returns

**Type:** `dict[str, Any]`

::: tip Example
```python
    results = await db.abatch_get(["key1", "key2"])
```
:::


---

### `aset_model`

```python
def aset_model(key: str, model: Any) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

::: tip Example
```python
    from pydantic import BaseModel
    class User(BaseModel):
        name: str
        age: int
    user = User(name="Nana", age=20)
    await db.set_model("user", user)
```
:::


---

### `aget_model`

```python
def aget_model(key: str, model_class: type = None) -> Any
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |
| `model_class` | `type` |  |

#### Returns

::: tip Example
```python
    user = await db.get_model("user", User)
```
:::


---

### `aexecute`

```python
def aexecute(sql: str, parameters: tuple | None = None) -> Any
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `sql` | `str` |  |
| `parameters` | `tuple | None` |  |

#### Returns

::: tip Example
```python
    cursor = await db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
```
:::


---

### `aexecute_many`

```python
def aexecute_many(sql: str, parameters_list: list[tuple]) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `sql` | `str` |  |
| `parameters_list` | `list[tuple]` |  |

::: tip Example
```python
    await db.execute_many(
        "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
        [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
    )
```
:::


---

### `afetch_one`

```python
def afetch_one(sql: str, parameters: tuple | None = None) -> tuple | None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `sql` | `str` |  |
| `parameters` | `tuple | None` |  |

#### Returns

**Type:** `tuple | None`

::: tip Example
```python
    row = await db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
```
:::


---

### `afetch_all`

```python
def afetch_all(sql: str, parameters: tuple | None = None) -> list[tuple]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `sql` | `str` |  |
| `parameters` | `tuple | None` |  |

#### Returns

**Type:** `list[tuple]`

::: tip Example
```python
    rows = await db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
```
:::


---

### `acreate_table`

```python
def acreate_table(table_name: str, columns: dict, if_not_exists: bool = True, primary_key: str = None) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `columns` | `dict` |  |
| `if_not_exists` | `bool` |  |
| `primary_key` | `str` |  |

::: tip Example
```python
    await db.create_table("users", {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "email": "TEXT UNIQUE"
    })
```
:::


---

### `acreate_index`

```python
def acreate_index(index_name: str, table_name: str, columns: list[str], unique: bool = False, if_not_exists: bool = True) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `index_name` | `str` |  |
| `table_name` | `str` |  |
| `columns` | `list[str]` |  |
| `unique` | `bool` |  |
| `if_not_exists` | `bool` |  |

::: tip Example
```python
    await db.create_index("idx_users_email", "users", ["email"], unique=True)
```
:::


---

### `aquery`

```python
def aquery(table_name: str = None, columns: list[str] = None, where: str = None, parameters: tuple | None = None, order_by: str = None, limit: int = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> list[dict]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `columns` | `list[str]` |  |
| `where` | `str` |  |
| `parameters` | `tuple | None` |  |
| `order_by` | `str` |  |
| `limit` | `int` |  |
| `strict_sql_validation` | `bool` |  |
| `allowed_sql_functions` | `list[str]` |  |
| `forbidden_sql_functions` | `list[str]` |  |
| `override_allowed` | `bool` |  |

#### Returns

**Type:** `list[dict]`

::: tip Example
```python
    results = await db.query(
        table_name="users",
        columns=["id", "name", "email"],
        where="age > ?",
        parameters=(20,),
        order_by="name ASC",
        limit=10
    )
```
:::


---

### `aquery_with_pagination`

```python
def aquery_with_pagination(table_name: str = None, columns: list[str] = None, where: str = None, parameters: tuple | None = None, order_by: str = None, limit: int = None, offset: int = None, group_by: str = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> list[dict]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `columns` | `list[str]` |  |
| `where` | `str` |  |
| `parameters` | `tuple | None` |  |
| `order_by` | `str` |  |
| `limit` | `int` |  |
| `offset` | `int` |  |
| `group_by` | `str` |  |
| `strict_sql_validation` | `bool` |  |
| `allowed_sql_functions` | `list[str]` |  |
| `forbidden_sql_functions` | `list[str]` |  |
| `override_allowed` | `bool` |  |

#### Returns

**Type:** `list[dict]`

::: tip Example
```python
    results = await db.query_with_pagination(
        table_name="users",
        columns=["id", "name", "email"],
        where="age > ?",
        parameters=(20,),
        order_by="name ASC",
        limit=10,
        offset=0
    )
```
:::


---

### `atable_exists`

```python
def atable_exists(table_name: str) -> bool
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |

#### Returns

**Type:** `bool`

::: tip Example
```python
    exists = await db.table_exists("users")
```
:::


---

### `alist_tables`

```python
def alist_tables() -> list[str]
```

#### Returns

**Type:** `list[str]`

::: tip Example
```python
    tables = await db.list_tables()
```
:::


---

### `adrop_table`

```python
def adrop_table(table_name: str, if_exists: bool = True) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `if_exists` | `bool` |  |

::: tip Example
```python
    await db.drop_table("old_table")
```
:::


---

### `asql_insert`

```python
def asql_insert(table_name: str, data: dict) -> int
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `data` | `dict` |  |

#### Returns

**Type:** `int`

::: tip Example
```python
    rowid = await db.sql_insert("users", {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 25
    })
```
:::


---

### `asql_update`

```python
def asql_update(table_name: str, data: dict, where: str, parameters: tuple | None = None) -> int
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `data` | `dict` |  |
| `where` | `str` |  |
| `parameters` | `tuple | None` |  |

#### Returns

**Type:** `int`

::: tip Example
```python
    count = await db.sql_update("users",
        {"age": 26, "status": "active"},
        "name = ?",
        ("Alice",)
    )
```
:::


---

### `asql_delete`

```python
def asql_delete(table_name: str, where: str, parameters: tuple | None = None) -> int
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `where` | `str` |  |
| `parameters` | `tuple | None` |  |

#### Returns

**Type:** `int`

::: tip Example
```python
    count = await db.sql_delete("users", "age < ?", (18,))
```
:::


---

### `acount`

```python
def acount(table_name: str = None, where: str = None, parameters: tuple | None = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> int
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `where` | `str` |  |
| `parameters` | `tuple | None` |  |
| `strict_sql_validation` | `bool` |  |
| `allowed_sql_functions` | `list[str]` |  |
| `forbidden_sql_functions` | `list[str]` |  |
| `override_allowed` | `bool` |  |

#### Returns

**Type:** `int`

::: tip Example
```python
    count = await db.count("users", "age < ?", (18,))
```
:::


---

### `avacuum`

```python
def avacuum() -> None
```

::: tip Example
```python
    await db.vacuum()
```
:::


---

### `aclear_cache`

```python
def aclear_cache() -> None
```




---

### `atable`

```python
def atable(table_name: str, validator: Any | None | types.EllipsisType = Ellipsis, coerce: bool | types.EllipsisType = Ellipsis) -> AsyncNanaSQLite
```

sub1 = await db.table("users")

    users_db = await db.table("users")

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `validator` | `Any | None | types.EllipsisType` |  |
| `coerce` | `bool | types.EllipsisType` | ``True`` の場合、validkit-py の自動変換機能を有効にする。 |

#### Returns

**Type:** `AsyncNanaSQLite`

::: tip Example
```python
    async with AsyncNanaSQLite("mydata.db", table="main") as db:
        users_db = await db.table("users")
        products_db = await db.table("products")
        await users_db.aset("user1", {"name": "Alice"})
        await products_db.aset("prod1", {"name": "Laptop"})
```
:::


---

### `abackup`

```python
def abackup(target_path: str) -> None
```

---

### `arestore`

```python
def arestore(source_path: str) -> None
```

---

### `apragma`

```python
def apragma(pragma_name: str, value: Any = None) -> Any
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `pragma_name` | `str` |  |



---

### `aget_table_schema`

```python
def aget_table_schema(table_name: str = None) -> list[dict]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |



---

### `alist_indexes`

```python
def alist_indexes(table_name: str = None) -> list[str]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |



---

### `aalter_table_add_column`

```python
def aalter_table_add_column(table_name: str, column_name: str, column_type: str) -> None
```

---

### `aupsert`

```python
def aupsert(table_name: str | Any = None, data: Any = None, conflict_columns: list[str] = None) -> int | None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str | Any` |  |
| `conflict_columns` | `list[str]` |  |



---

