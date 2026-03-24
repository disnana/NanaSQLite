# Synchronous API Reference

Reference for the synchronous NanaSQLite class.

## NanaSQLite

```python
class NanaSQLite(db_path: str, table: str = 'data', bulk_load: bool = False, optimize: bool = True, cache_size_mb: int = 64, strict_sql_validation: bool = True, allowed_sql_functions: list[str] | None = None, forbidden_sql_functions: list[str] | None = None, max_clause_length: int | None = 1000, cache_strategy: CacheType | Literal['unbounded', 'lru', 'ttl'] = <CacheType.UNBOUNDED: unbounded>, cache_size: int | None = None, cache_ttl: float | None = None, cache_persistence_ttl: bool = False, encryption_key: str | bytes | None = None, encryption_mode: Literal['aes-gcm', 'chacha20', 'fernet'] = 'aes-gcm', lock_timeout: float | None = None, validator: Any | None = None, coerce: bool = False, v2_mode: bool = False, flush_mode: Literal['immediate', 'count', 'time', 'manual'] = 'immediate', flush_interval: float = 3.0, flush_count: int = 100, v2_chunk_size: int = 1000, v2_enable_metrics: bool = False, _shared_connection: apsw.Connection | None = None, _shared_lock: threading.RLock | None = None)
```

APSW SQLite-backed dict wrapper with Security and Connection Enhancements (v1.2.0).

Internally maintains a Python dict and synchronizes with SQLite during operations.
In v1.2.0, enhanced dynamic SQL validation, ReDoS protection, and strict connection management are introduced.

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `db_path` | `str` |  |
| `table` | `str` |  |
| `bulk_load` | `bool` |  |
| `optimize` | `bool` |  |
| `cache_size_mb` | `int` |  |
| `strict_sql_validation` | `bool` |  |
| `allowed_sql_functions` | `list[str] | None` |  |
| `forbidden_sql_functions` | `list[str] | None` |  |
| `max_clause_length` | `int | None` |  |
| `cache_strategy` | `CacheType | Literal[unbounded, lru, ttl]` |  |
| `cache_size` | `int | None` |  |
| `cache_ttl` | `float | None` |  |
| `cache_persistence_ttl` | `bool` |  |
| `encryption_key` | `str | bytes | None` |  |
| `encryption_mode` | `Literal[aes-gcm, chacha20, fernet]` |  |
| `lock_timeout` | `float | None` |  |
| `validator` | `Any | None` |  |
| `coerce` | `bool` | ``True`` の場合、validkit-py の自動変換（コアース）機能を有効にする。 |
| `v2_mode` | `bool` |  |
| `flush_mode` | `Literal[immediate, count, time, manual]` |  |
| `flush_interval` | `float` |  |
| `flush_count` | `int` |  |
| `v2_chunk_size` | `int` |  |
| `v2_enable_metrics` | `bool` |  |
| `_shared_connection` | `apsw.Connection | None` |  |
| `_shared_lock` | `threading.RLock | None` |  |



---

## Constructor

## Core Methods

### `close`

```python
def close() -> None
```

---

### `table`

```python
def table(table_name: str, cache_strategy: CacheType | Literal['unbounded', 'lru', 'ttl'] | None = None, cache_size: int | None = None, cache_ttl: float | None = None, cache_persistence_ttl: bool | None = None, validator: Any | None | types.EllipsisType = Ellipsis, coerce: bool | types.EllipsisType = Ellipsis, v2_enable_metrics: bool | types.EllipsisType = Ellipsis)
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `cache_strategy` | `CacheType | Literal[unbounded, lru, ttl] | None` |  |
| `cache_size` | `int | None` |  |
| `cache_ttl` | `float | None` |  |
| `cache_persistence_ttl` | `bool | None` |  |
| `validator` | `Any | None | types.EllipsisType` |  |
| `coerce` | `bool | types.EllipsisType` | ``True`` の場合、validkit-py の自動変換機能を有効にする。 sub1 = db.table("users") users_db = db.table("users") |
| `v2_enable_metrics` | `bool | types.EllipsisType` |  |

::: warning Raises
:::

::: tip Example
```python
    from validkit import v
    with NanaSQLite("app.db", table="main") as main_db:
        users_schema = {"name": v.str(), "age": v.int()}
        users_db = main_db.table("users", validator=users_schema)
        products_db = main_db.table("products")
        users_db["user1"] = {"name": "Alice", "age": 30}
        products_db["prod1"] = {"name": "Laptop"}
```
:::


---

## Dictionary Interface

### `__getitem__`

```python
def __getitem__(key: str) -> Any
```




---

### `__setitem__`

```python
def __setitem__(key: str, value: Any) -> None
```




---

### `__delitem__`

```python
def __delitem__(key: str) -> None
```




---

### `__contains__`

```python
def __contains__(key: str) -> bool
```




---

### `__len__`

```python
def __len__() -> int
```




---

### `__iter__`

```python
def __iter__() -> Iterator[str]
```

for key in dict


---

### `keys`

```python
def keys() -> list
```




---

### `values`

```python
def values() -> list
```




---

### `items`

```python
def items() -> list
```




---

### `get`

```python
def get(key: str, default: Any = None) -> Any
```

dict.get(key, default)


---

### `pop`

```python
def pop(key: str, *args) -> Any
```

dict.pop(key[, default])


---

### `update`

```python
def update(mapping: dict | None = None, **kwargs) -> None
```




---

### `clear`

```python
def clear() -> None
```




---

### `setdefault`

```python
def setdefault(key: str, default: Any = None) -> Any
```

dict.setdefault(key, default)


---

### `to_dict`

```python
def to_dict() -> dict
```




---

### `copy`

```python
def copy() -> dict
```




---

### `clear_cache`

```python
def clear_cache() -> None
```




---

## Data Management

### `get_fresh`

```python
def get_fresh(key: str, default: Any = None) -> Any
```

`execute()`でDBを直接変更した後などに使用。

通常の`get()`よりオーバーヘッドがあるため、

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` |  |

#### Returns

::: tip Example
```python
    db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new"', "key"))
    value = db.get_fresh("key")  # DBから最新値を取得
```
:::


---

### `batch_get`

```python
def batch_get(keys: list[str]) -> dict[str, Any]
```

1回の `SELECT IN (...)` クエリで複数のキーをDBから取得する。

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `keys` | `list[str]` |  |

#### Returns

**Type:** `dict[str, Any]`

::: tip Example
```python
    results = db.batch_get(["user1", "user2", "user3"])
    print(results)  # {"user1": {...}, "user2": {...}}
```
:::


---

### `flush`

```python
def flush() -> None
```

[v2 Feature] Explicitly flush the v2 engine's background buffer and queue to SQLite.
If v2_mode is False, this operates as a no-op.


---

### `load_all`

```python
def load_all() -> None
```




---

### `refresh`

```python
def refresh(key: str = None) -> None
```

---

### `is_cached`

```python
def is_cached(key: str) -> bool
```




---

### `batch_update`

```python
def batch_update(mapping: dict[str, Any]) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `mapping` | `dict[str, Any]` |  |

#### Returns

None

::: tip Example
```python
    db.batch_update({"key1": "value1", "key2": "value2", ...})
```
:::


---

### `batch_update_partial`

```python
def batch_update_partial(mapping: dict[str, Any]) -> dict[str, str]
```

`batch_update()` のアトミック契約は維持したまま、各キーを個別に準備し、

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `mapping` | `dict[str, Any]` |  |

#### Returns

**Type:** `dict[str, str]`

::: tip Example
```python
    failed = db.batch_update_partial({"ok": 1, "bad": object()})
    print(failed)
```
:::


---

### `batch_delete`

```python
def batch_delete(keys: list[str]) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `keys` | `list[str]` |  |

#### Returns

None


---

## Transaction Control

### `begin_transaction`

```python
def begin_transaction() -> None
```

Note:

::: warning Raises
:::

::: tip Example
```python
    db.begin_transaction()
    try:
        db.sql_insert("users", {"name": "Alice"})
        db.sql_insert("users", {"name": "Bob"})
        db.commit()
    except:
        db.rollback()
```
:::


---

### `commit`

```python
def commit() -> None
```

---

### `rollback`

```python
def rollback() -> None
```

---

### `in_transaction`

```python
def in_transaction() -> bool
```

#### Returns

**Type:** `bool`

::: tip Example
```python
    db.begin_transaction()
    print(db.in_transaction())  # True
    db.commit()
    print(db.in_transaction())  # False
```
:::


---

### `transaction`

```python
def transaction()
```

::: warning Raises
:::

::: tip Example
```python
    with db.transaction():
        db.sql_insert("users", {"name": "Alice"})
        db.sql_insert("users", {"name": "Bob"})
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
    rowid = db.sql_insert("users", {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 25
    })
```
:::


---

### `sql_update`

```python
def sql_update(table_name: str, data: dict, where: str, parameters: tuple = None) -> int
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `data` | `dict` |  |
| `where` | `str` |  |
| `parameters` | `tuple` |  |

#### Returns

**Type:** `int`

::: tip Example
```python
    count = db.sql_update("users",
        {"age": 26, "status": "active"},
        "name = ?",
        ("Alice",)
    )
```
:::


---

### `sql_delete`

```python
def sql_delete(table_name: str, where: str, parameters: tuple = None) -> int
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `where` | `str` |  |
| `parameters` | `tuple` |  |

#### Returns

**Type:** `int`

::: tip Example
```python
    count = db.sql_delete("users", "age < ?", (18,))
```
:::


---

### `upsert`

```python
def upsert(table_name: str | Any = None, data: Any = None, conflict_columns: list[str] = None) -> int | None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str | Any` |  |
| `conflict_columns` | `list[str]` |  |

#### Returns

**Type:** `int | None`

::: tip Example
```python
    # テーブル指定（標準）
    db.upsert("users", {"id": 1, "name": "Alice", "age": 25})
    # キー/値指定 (v2互換)
    db.upsert("user:1", {"name": "Nana"})
```
:::


---

## Query

### `query`

```python
def query(table_name: str = None, columns: list[str] = None, where: str = None, parameters: tuple = None, order_by: str = None, limit: int = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> list[dict]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `columns` | `list[str]` |  |
| `where` | `str` |  |
| `parameters` | `tuple` |  |
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
    # デフォルトテーブルから全データ取得
    results = db.query()
```

```python
    # 条件付き検索
    results = db.query(
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

### `count`

```python
def count(table_name: str = None, where: str = None, parameters: tuple = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> int
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `where` | `str` |  |
| `parameters` | `tuple` |  |
| `strict_sql_validation` | `bool` |  |
| `allowed_sql_functions` | `list[str]` |  |
| `forbidden_sql_functions` | `list[str]` |  |
| `override_allowed` | `bool` |  |

::: tip Example
```python
    total = db.count("users")
    adults = db.count("users", "age >= ?", (18,))
```
:::


---

### `exists`

```python
def exists(table_name: str, where: str, parameters: tuple = None) -> bool
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `where` | `str` |  |
| `parameters` | `tuple` |  |

#### Returns

**Type:** `bool`

::: tip Example
```python
    if db.exists("users", "email = ?", ("alice@example.com",)):
        print("User exists")
```
:::


---

### `query_with_pagination`

```python
def query_with_pagination(table_name: str = None, columns: list[str] = None, where: str = None, parameters: tuple = None, order_by: str = None, limit: int = None, offset: int = None, group_by: str = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> list[dict]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `columns` | `list[str]` |  |
| `where` | `str` |  |
| `parameters` | `tuple` |  |
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
    # ページネーション
    page2 = db.query_with_pagination("users",
        limit=10, offset=10, order_by="id ASC")
```

```python
    # グループ集計
    stats = db.query_with_pagination("orders",
        columns=["user_id", "COUNT(*) as order_count"],
        group_by="user_id"
    )
```
:::


---

## Direct SQL Execution

### `execute`

```python
def execute(sql: str, parameters: tuple | None = None) -> apsw.Cursor
```

.. warning::
    キャッシュを更新するには `refresh()` を呼び出してください。

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `sql` | `str` |  |
| `parameters` | `tuple | None` |  |

#### Returns

**Type:** `apsw.Cursor`

::: warning Raises
:::

::: tip Example
```python
    cursor = db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
    for row in cursor:
        print(row)
```

```python
    db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new"', "key"))
    db.refresh("key")  # キャッシュを更新
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
    db.execute_many(
        "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
        [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
    )
```
:::


---

### `fetch_one`

```python
def fetch_one(sql: str, parameters: tuple = None) -> tuple | None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `sql` | `str` |  |
| `parameters` | `tuple` |  |

#### Returns

**Type:** `tuple | None`

::: tip Example
```python
    row = db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
    print(row[0])
```
:::


---

### `fetch_all`

```python
def fetch_all(sql: str, parameters: tuple = None) -> list[tuple]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `sql` | `str` |  |
| `parameters` | `tuple` |  |

#### Returns

**Type:** `list[tuple]`

::: tip Example
```python
    rows = db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
    for key, value in rows:
        print(key, value)
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
    db.create_table("users", {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "email": "TEXT UNIQUE",
        "age": "INTEGER"
    })
    db.create_table("posts", {
        "id": "INTEGER",
        "title": "TEXT",
        "content": "TEXT"
    }, primary_key="id")
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
    db.create_index("idx_users_email", "users", ["email"], unique=True)
    db.create_index("idx_posts_user", "posts", ["user_id", "created_at"])
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
    if db.table_exists("users"):
        print("users table exists")
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
    tables = db.list_tables()
    print(tables)  # ['data', 'users', 'posts']
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
    db.drop_table("old_table")
    db.drop_table("temp", if_exists=True)
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
    db.drop_index("idx_users_email")
```
:::


---

### `alter_table_add_column`

```python
def alter_table_add_column(table_name: str, column_name: str, column_type: str, default: Any = None) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `column_name` | `str` |  |
| `column_type` | `str` |  |

::: tip Example
```python
    db.alter_table_add_column("users", "phone", "TEXT")
    db.alter_table_add_column("users", "status", "TEXT", default="'active'")
```
:::


---

### `get_table_schema`

```python
def get_table_schema(table_name: str = None) -> list[dict]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |

#### Returns

**Type:** `list[dict]`

::: tip Example
```python
    schema = db.get_table_schema("users")
    for col in schema:
        print(f"{col['name']}: {col['type']}")
```
:::


---

### `list_indexes`

```python
def list_indexes(table_name: str = None) -> list[dict]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |

#### Returns

**Type:** `list[dict]`

::: tip Example
```python
    indexes = db.list_indexes("users")
    for idx in indexes:
        print(f"{idx['name']}: {idx['columns']}")
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
    db.vacuum()
```
:::


---

### `get_db_size`

```python
def get_db_size() -> int
```

#### Returns

**Type:** `int`

::: tip Example
```python
    size = db.get_db_size()
    print(f"DB size: {size / 1024 / 1024:.2f} MB")
```
:::


---

### `get_last_insert_rowid`

```python
def get_last_insert_rowid() -> int
```

#### Returns

**Type:** `int`

::: tip Example
```python
    db.sql_insert("users", {"name": "Alice"})
    rowid = db.get_last_insert_rowid()
```
:::


---

### `pragma`

```python
def pragma(pragma_name: str, value: Any = None) -> Any
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `pragma_name` | `str` |  |

#### Returns

::: tip Example
```python
    # 取得
    mode = db.pragma("journal_mode")
```

```python
    # 設定
    db.pragma("foreign_keys", 1)
```
:::


---

## Backup & Restore

### `backup`

```python
def backup(dest_path: str) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `dest_path` | `str` |  |



---

### `restore`

```python
def restore(src_path: str) -> None
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `src_path` | `str` |  |



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
    db.set_model("user", user)
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
    user = db.get_model("user", User)
    print(user.name)  # "Nana"
```
:::


---

## Other Methods

### `get_dlq`

```python
def get_dlq() -> list[dict[str, Any]]
```




---

### `retry_dlq`

```python
def retry_dlq() -> None
```




---

### `clear_dlq`

```python
def clear_dlq() -> None
```




---

### `get_v2_metrics`

```python
def get_v2_metrics() -> dict[str, Any]
```




---

### `export_table_to_dict`

```python
def export_table_to_dict(table_name: str) -> list[dict]
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |

#### Returns

**Type:** `list[dict]`

::: tip Example
```python
    all_users = db.export_table_to_dict("users")
```
:::


---

### `import_from_dict_list`

```python
def import_from_dict_list(table_name: str, data_list: list[dict]) -> int
```

#### Parameter

| Parameter | Type | Description |
|---|---|---|
| `table_name` | `str` |  |
| `data_list` | `list[dict]` |  |

#### Returns

**Type:** `int`

::: tip Example
```python
    users = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30}
    ]
    count = db.import_from_dict_list("users", users)
```
:::


---

### `popitem`

```python
def popitem()
```

D.popitem() -> (k, v), remove and return some (key, value) pair
as a 2-tuple; but raise KeyError if D is empty.


---

