# Asynchronous API Reference

List of asynchronous methods for the AsyncNanaSQLite class.

## AsyncNanaSQLite

Asynchronous wrapper for NanaSQLite using optimized thread pool.

All database operations are executed within a dedicated thread pool, preventing blocking of the asynchronous event loop.
This makes it safe to use in asynchronous applications like FastAPI or aiohttp.

Uses a customizable thread pool to achieve optimal concurrency and performance in high-load scenarios.

#### 📥 Arguments
- **db_path**: Path to the SQLite database file
- **table**: Default: "data"
- **bulk_load**: If True, loads all data into memory during initialization
- **optimize**: If True, applies performance settings like WAL mode
- **cache_size_mb**: SQLite cache size (MB), default 64MB
- **strict_sql_validation**: v1.2.0
- **max_clause_length**: v1.2.0
- **max_workers**: Max workers in thread pool (default: 5)
- **thread_name_prefix**: Thread name prefix (default: "AsyncNanaSQLite")

#### 💡 Example
```python
    >>> async with AsyncNanaSQLite("mydata.db") as db:
    ...     await db.aset("config", {"theme": "dark"})
    ...     config = await db.aget("config")
    ...     print(config)
```

```python
    >>> # Settings for high load
    >>> async with AsyncNanaSQLite("mydata.db", max_workers=10) as db:
    ...     # Optimized for high concurrency
    ...     results = await asyncio.gather(*[db.aget(f"key_{i}") for i in range(100)])
```

---

## Methods

### __init__

```python
__init__(self, db_path: 'str', table: 'str' = 'data', bulk_load: 'bool' = False, optimize: 'bool' = True, cache_size_mb: 'int' = 64, max_workers: 'int' = 5, thread_name_prefix: 'str' = 'AsyncNanaSQLite', strict_sql_validation: 'bool' = True, allowed_sql_functions: 'list[str] | None' = None, forbidden_sql_functions: 'list[str] | None' = None, max_clause_length: 'int | None' = 1000, read_pool_size: 'int' = 0)
```

#### 📥 Arguments
- **db_path**: Path to SQLite database file
- **max_workers**: Max workers (default: 5)
- **read_pool_size**: Default: 0 = Disabled (v1.1.0)
- ... (Same as Sync)

---

### aget

```python
aget(self, key: 'str', default: 'Any' = None) -> 'Any'
```

Get value asynchronously.

---

### get

```python
get(self, key: 'str', default: 'Any' = None) -> 'Any'
```

Get value asynchronously.

---

### aset

```python
aset(self, key: 'str', value: 'Any') -> 'None'
```

Set value asynchronously.

---

### adelete

```python
adelete(self, key: 'str') -> 'None'
```

Delete key asynchronously.

---

### acontains

```python
acontains(self, key: 'str') -> 'bool'
```

Check existence asynchronously.

---

### contains

```python
contains(self, key: 'str') -> 'bool'
```

Check existence asynchronously.

---

### alen

```python
alen(self) -> 'int'
```

Get database size asynchronously.

---

### akeys

```python
akeys(self) -> 'list[str]'
```

Get all keys asynchronously.

---

### keys

```python
keys(self) -> 'list[str]'
```

Get all keys asynchronously.

---

### avalues

```python
avalues(self) -> 'list[Any]'
```

Get all values asynchronously.

---

### values

```python
values(self) -> 'list[Any]'
```

Get all values asynchronously.

---

### aitems

```python
aitems(self) -> 'list[tuple[str, Any]]'
```

Get all items asynchronously.

---

### items

```python
items(self) -> 'list[tuple[str, Any]]'
```

Get all items asynchronously.

---

### apop

```python
apop(self, key: 'str', *args) -> 'Any'
```

Remove and return value asynchronously.

---

### aupdate

```python
aupdate(self, mapping: 'dict' = None, **kwargs) -> 'None'
```

Update multiple keys asynchronously.

---

### aclear

```python
aclear(self) -> 'None'
```

Clear all data asynchronously.

---

### asetdefault

```python
asetdefault(self, key: 'str', default: 'Any' = None) -> 'Any'
```

Set default if key not exists asynchronously.

---

### aload_all

```python
aload_all(self) -> 'None'
```

Load all data asynchronously.

---

### load_all

```python
load_all(self) -> 'None'
```

Load all data asynchronously.

---

### arefresh

```python
arefresh(self, key: 'str' = None) -> 'None'
```

Refresh cache asynchronously.

---

### refresh

```python
refresh(self, key: 'str' = None) -> 'None'
```

Refresh cache asynchronously.

---

### ais_cached

```python
ais_cached(self, key: 'str') -> 'bool'
```

Check if cached asynchronously.

---

### is_cached

```python
is_cached(self, key: 'str') -> 'bool'
```

Check if cached asynchronously.

---

### abatch_update

```python
abatch_update(self, mapping: 'dict[str, Any]') -> 'None'
```

Batch write asynchronously.

---

### batch_update

```python
batch_update(self, mapping: 'dict[str, Any]') -> 'None'
```

Batch write asynchronously.

---

### abatch_delete

```python
abatch_delete(self, keys: 'list[str]') -> 'None'
```

Batch delete asynchronously.

---

### batch_delete

```python
batch_delete(self, keys: 'list[str]') -> 'None'
```

Batch delete asynchronously.

---

### ato_dict

```python
ato_dict(self) -> 'dict'
```

Get as dict asynchronously.

---

### to_dict

```python
to_dict(self) -> 'dict'
```

Get as dict asynchronously.

---

### acopy

```python
acopy(self) -> 'dict'
```

Create shallow copy asynchronously.

---

### copy

```python
copy(self) -> 'dict'
```

Create shallow copy asynchronously.

---

### aget_fresh

```python
aget_fresh(self, key: 'str', default: 'Any' = None) -> 'Any'
```

Get fresh from DB asynchronously.

---

### get_fresh

```python
get_fresh(self, key: 'str', default: 'Any' = None) -> 'Any'
```

Get fresh from DB asynchronously.

---

### abatch_get

```python
abatch_get(self, keys: 'list[str]') -> 'dict[str, Any]'
```

Batch get asynchronously.

---

### aset_model

```python
aset_model(self, key: 'str', model: 'Any') -> 'None'
```

Save Pydantic model asynchronously.

---

### set_model

```python
set_model(self, key: 'str', model: 'Any') -> 'None'
```

Save Pydantic model asynchronously.

---

### aget_model

```python
aget_model(self, key: 'str', model_class: 'type' = None) -> 'Any'
```

Get Pydantic model asynchronously.

---

### get_model

```python
get_model(self, key: 'str', model_class: 'type' = None) -> 'Any'
```

Get Pydantic model asynchronously.

---

### aexecute

```python
aexecute(self, sql: 'str', parameters: 'tuple | None' = None) -> 'Any'
```

Execute SQL asynchronously.

---

### execute

```python
execute(self, sql: 'str', parameters: 'tuple | None' = None) -> 'Any'
```

Execute SQL asynchronously.

---

### aexecute_many

```python
aexecute_many(self, sql: 'str', parameters_list: 'list[tuple]') -> 'None'
```

Execute many SQL asynchronously.

---

### execute_many

```python
execute_many(self, sql: 'str', parameters_list: 'list[tuple]') -> 'None'
```

Execute many SQL asynchronously.

---

### afetch_one

```python
afetch_one(self, sql: 'str', parameters: 'tuple' = None) -> 'tuple | None'
```

Fetch one row asynchronously.

---

### fetch_one

```python
fetch_one(self, sql: 'str', parameters: 'tuple' = None) -> 'tuple | None'
```

Fetch one row asynchronously.

---

### afetch_all

```python
afetch_all(self, sql: 'str', parameters: 'tuple' = None) -> 'list[tuple]'
```

Fetch all rows asynchronously.

---

### fetch_all

```python
fetch_all(self, sql: 'str', parameters: 'tuple' = None) -> 'list[tuple]'
```

Fetch all rows asynchronously.

---

### acreate_table

```python
acreate_table(self, table_name: 'str', columns: 'dict', if_not_exists: 'bool' = True, primary_key: 'str' = None) -> 'None'
```

Create table asynchronously.

---

### create_table

```python
create_table(self, table_name: 'str', columns: 'dict', if_not_exists: 'bool' = True, primary_key: 'str' = None) -> 'None'
```

Create table asynchronously.

---

### acreate_index

```python
acreate_index(self, index_name: 'str', table_name: 'str', columns: 'list[str]', unique: 'bool' = False, if_not_exists: 'bool' = True) -> 'None'
```

Create index asynchronously.

---

### create_index

```python
create_index(self, index_name: 'str', table_name: 'str', columns: 'list[str]', unique: 'bool' = False, if_not_exists: 'bool' = True) -> 'None'
```

Create index asynchronously.

---

### aquery

```python
aquery(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```

Query asynchronously.

---

### query

```python
query(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```

Query asynchronously.

---

### aquery_with_pagination

```python
aquery_with_pagination(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, offset: 'int' = None, group_by: 'str' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```

Query with pagination asynchronously.

---

### query_with_pagination

```python
query_with_pagination(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, offset: 'int' = None, group_by: 'str' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```

Query with pagination asynchronously.

---

### atable_exists

```python
atable_exists(self, table_name: 'str') -> 'bool'
```

Check table existence asynchronously.

---

### table_exists

```python
table_exists(self, table_name: 'str') -> 'bool'
```

Check table existence asynchronously.

---

### alist_tables

```python
alist_tables(self) -> 'list[str]'
```

List tables asynchronously.

---

### list_tables

```python
list_tables(self) -> 'list[str]'
```

List tables asynchronously.

---

### adrop_table

```python
adrop_table(self, table_name: 'str', if_exists: 'bool' = True) -> 'None'
```

Drop table asynchronously.

---

### drop_table

```python
drop_table(self, table_name: 'str', if_exists: 'bool' = True) -> 'None'
```

Drop table asynchronously.

---

### drop_index

```python
drop_index(self, index_name: 'str', if_exists: 'bool' = True) -> 'None'
```

Drop index asynchronously.

---

### asql_insert

```python
asql_insert(self, table_name: 'str', data: 'dict') -> 'int'
```

Insert synchronously directly from dict (async wrapper).

---

### sql_insert

```python
sql_insert(self, table_name: 'str', data: 'dict') -> 'int'
```

Insert synchronously directly from dict (async wrapper).

---

### asql_update

```python
asql_update(self, table_name: 'str', data: 'dict', where: 'str', parameters: 'tuple' = None) -> 'int'
```

Update asynchronously.

---

### sql_update

```python
sql_update(self, table_name: 'str', data: 'dict', where: 'str', parameters: 'tuple' = None) -> 'int'
```

Update asynchronously.

---

### asql_delete

```python
asql_delete(self, table_name: 'str', where: 'str', parameters: 'tuple' = None) -> 'int'
```

Delete asynchronously.

---

### sql_delete

```python
sql_delete(self, table_name: 'str', where: 'str', parameters: 'tuple' = None) -> 'int'
```

Delete asynchronously.

---

### aupsert

```python
aupsert(self, table_name: 'str', data: 'dict', conflict_columns: 'list[str]' = None) -> 'int'
```

Upsert asynchronously.

---

### upsert

```python
upsert(self, table_name: 'str', data: 'dict', conflict_columns: 'list[str]' = None) -> 'int'
```

Upsert asynchronously.

---

### acount

```python
acount(self, table_name: 'str' = None, where: 'str' = None, parameters: 'tuple' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'int'
```

Count asynchronously.

---

### count

```python
count(self, table_name: 'str' = None, where: 'str' = None, parameters: 'tuple' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'int'
```

Count asynchronously.

---

### aexists

```python
aexists(self, table_name: 'str', where: 'str', parameters: 'tuple' = None) -> 'bool'
```

Check existence asynchronously.

---

### exists

```python
exists(self, table_name: 'str', where: 'str', parameters: 'tuple' = None) -> 'bool'
```

Check existence asynchronously.

---

### avacuum

```python
avacuum(self) -> 'None'
```

Vacuum asynchronously.

---

### vacuum

```python
vacuum(self) -> 'None'
```

Vacuum asynchronously.

---

### get_db_size

```python
get_db_size(self) -> 'int'
```

Get DB size (usually fast enough to be sync, but executed in thread).

---

### aexport_table_to_dict

```python
aexport_table_to_dict(self, table_name: 'str') -> 'list[dict]'
```

Export table asynchronously.

---

### export_table_to_dict

```python
export_table_to_dict(self, table_name: 'str') -> 'list[dict]'
```

Export table asynchronously.

---

### aimport_from_dict_list

```python
aimport_from_dict_list(self, table_name: 'str', data_list: 'list[dict]') -> 'int'
```

Import dict list asynchronously.

---

### import_from_dict_list

```python
import_from_dict_list(self, table_name: 'str', data_list: 'list[dict]') -> 'int'
```

Import dict list asynchronously.

---

### get_last_insert_rowid

```python
get_last_insert_rowid(self) -> 'int'
```

Get last rowid.

---

### apragma

```python
apragma(self, pragma_name: 'str', value: 'Any' = None) -> 'Any'
```

Async PRAGMA.

---

### pragma

```python
pragma(self, pragma_name: 'str', value: 'Any' = None) -> 'Any'
```

Async PRAGMA.

---

### begin_transaction

```python
begin_transaction(self) -> 'None'
```

Begin transaction asynchronously.

---

### commit

```python
commit(self) -> 'None'
```

Commit transaction asynchronously.

---

### rollback

```python
rollback(self) -> 'None'
```

Rollback transaction asynchronously.

---

### in_transaction

```python
in_transaction(self) -> 'bool'
```

Check transaction status asynchronously.

---

### transaction

```python
transaction(self)
```

Async context manager for transaction.

```python
    >>> async with db.transaction():
    ...     await db.aset("key", "value")
```

---

### close

```python
close(self) -> 'None'
```

Close connection asynchronously.

---

### table

```python
table(self, table_name: 'str')
```

Get AsyncNanaSQLite instance for sub-table.
Shares thread pool and connection.
