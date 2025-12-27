# Synchronous API Reference

List of synchronous methods for the NanaSQLite class.

## NanaSQLite

A dictionary-like wrapper backed by APSW SQLite with enhanced security and connection management (v1.2.0).

It holds an internal Python dict and synchronizes with SQLite during operations.
v1.2.0 introduces enhanced dynamic SQL validation, ReDoS protection, and strict connection management.

#### 📥 Arguments
- **db_path**: Path to the SQLite database file
- **table**: Default: "data"
- **bulk_load**: If True, loads all data into memory during initialization
- **strict_sql_validation**: v1.2.0
- **max_clause_length**: Maximum length of SQL clauses (ReDoS protection, v1.2.0)

---

## Methods

### __init__

```python
__init__(self, db_path: 'str', table: 'str' = 'data', bulk_load: 'bool' = False, optimize: 'bool' = True, cache_size_mb: 'int' = 64, strict_sql_validation: 'bool' = True, allowed_sql_functions: 'list[str] | None' = None, forbidden_sql_functions: 'list[str] | None' = None, max_clause_length: 'int | None' = 1000, _shared_connection: 'apsw.Connection | None' = None, _shared_lock: 'threading.RLock | None' = None)
```

#### 📥 Arguments
- **db_path**: Path to the SQLite database file
- **table**: Default: "data"
- **bulk_load**: If True, loads all data into memory during initialization
- **optimize**: If True, applies performance settings like WAL mode
- **cache_size_mb**: SQLite cache size (MB), default 64MB
- **strict_sql_validation**: If True, rejects queries containing unauthorized functions
- **allowed_sql_functions**: List of additional allowed SQL functions
- **forbidden_sql_functions**: List of explicitly forbidden SQL functions
- **max_clause_length**: Maximum length of SQL clauses (ReDoS protection). None for no limit
- **_shared_connection**: Internal use: shared connection (used by table() method)
- **_shared_lock**: Internal use: shared lock (used by table() method)

---

### keys

```python
keys(self) -> 'list'
```

Get all keys (from DB).

---

### values

```python
values(self) -> 'list'
```

Get all values (triggers bulk load, then from memory).

---

### items

```python
items(self) -> 'list'
```

Get all items (triggers bulk load, then from memory).

---

### get

```python
get(self, key: 'str', default: 'Any' = None) -> 'Any'
```

Get value by key, or default if not found.

---

### get_fresh

```python
get_fresh(self, key: 'str', default: 'Any' = None) -> 'Any'
```

Read directly from DB, update cache, and return value.

Bypasses cache to get the latest value from DB.
Used after modifying DB directly with `execute()`.

Has more overhead than normal `get()`, so use only when cache inconsistency is expected.

#### 📥 Arguments
- **key**: Key to retrieve
- **default**: Default value if key does not exist

#### 📤 Returns
    Latest value retrieved from DB (or default if not found)

#### 💡 Example
```python
    >>> db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new"', "key"))
    >>> value = db.get_fresh("key")  # Get latest value from DB
```

---

### batch_get

```python
batch_get(self, keys: 'list[str]') -> 'dict[str, Any]'
```

Get multiple keys at once (efficient bulk load).

Retrieves multiple keys from DB in a single `SELECT IN (...)` query.
Retrieved values are automatically saved to cache.

#### 📥 Arguments
- **keys**: List of keys to retrieve

#### 📤 Returns
    Dictionary of successfully retrieved keys and values

#### 💡 Example
```python
    >>> results = db.batch_get(["user1", "user2", "user3"])
    >>> print(results)  # {"user1": {...}, "user2": {...}}
```

---

### pop

```python
pop(self, key: 'str', *args) -> 'Any'
```

Remove and return value by key.

---

### update

```python
update(self, mapping: 'dict' = None, **kwargs) -> 'None'
```

Update multiple keys.

---

### clear

```python
clear(self) -> 'None'
```

Remove all items.

---

### setdefault

```python
setdefault(self, key: 'str', default: 'Any' = None) -> 'Any'
```

Get value, setting default if not exists.

---

### load_all

```python
load_all(self) -> 'None'
```

Load all data into memory.

---

### refresh

```python
refresh(self, key: 'str' = None) -> 'None'
```

Update cache (reload from DB).

#### 📥 Arguments
- **key**: Update only specific key. If None, clear entire cache and reload.

---

### is_cached

```python
is_cached(self, key: 'str') -> 'bool'
```

Check if key is cached in memory.

---

### batch_update

```python
batch_update(self, mapping: 'dict[str, Any]') -> 'None'
```

Bulk write (Ultra-fast using transaction + executemany).

10-100x faster than normal update when writing large amounts of data.
Optimization with executemany added in v1.0.3rc5.

#### 📥 Arguments
- **mapping**: Dict of keys and values to write

#### 💡 Example
```python
    >>> db.batch_update({"key1": "value1", "key2": "value2", ...})
```

---

### batch_delete

```python
batch_delete(self, keys: 'list[str]') -> 'None'
```

Bulk delete (Fast using transaction + executemany).

Optimization with executemany added in v1.0.3rc5.

#### 📥 Arguments
- **keys**: List of keys to delete

---

### to_dict

```python
to_dict(self) -> 'dict'
```

Get all data as a Python dict.

---

### copy

```python
copy(self) -> 'dict'
```

Create a shallow copy (returns standard dict).

---

### close

```python
close(self) -> 'None'
```

Close database connection.

- **Note**: Instances created by `table()` share the connection, so only the connection owner (the first created instance) closes the connection.

#### ⚠️ Exceptions
- **NanaSQLiteTransactionError**: If attempted to close during a transaction.

---

### set_model

```python
set_model(self, key: 'str', model: 'Any') -> 'None'
```

Save Pydantic model.

Serializes and saves a Pydantic model (class inheriting from BaseModel).
Converts to dict using model_dump() and also saves model class info.

#### 📥 Arguments
- **key**: Key to save
- **model**: An instance of Pydantic model

#### 💡 Example
```python
    >>> from pydantic import BaseModel
    >>> class User(BaseModel):
    ...     name: str
    ...     age: int
    >>> user = User(name="Nana", age=20)
    >>> db.set_model("user", user)
```

---

### get_model

```python
get_model(self, key: 'str', model_class: 'type' = None) -> 'Any'
```

Get Pydantic model.

Deserializes and restores a saved Pydantic model.
If model_class is not specified, uses the saved class info.

#### 📥 Arguments
- **key**: Key to retrieve
- **model_class**: Pydantic model class (If None, attempts auto-detection)

#### 📤 Returns
    Instance of Pydantic model

#### 💡 Example
```python
    >>> user = db.get_model("user", User)
    >>> print(user.name)  # "Nana"
```

---

### execute

```python
execute(self, sql: 'str', parameters: 'tuple | None' = None) -> 'apsw.Cursor'
```

Execute SQL directly.

Can execute arbitrary SQL statements like SELECT, INSERT, UPDATE, DELETE.
Supports parameter binding (SQL injection prevention).

    If you modify the default table (data) directly with this method,
    inconsistency with internal cache (_data) may occur.
    Call `refresh()` to update the cache.

#### 📥 Arguments
- **sql**: SQL statement to execute
- **parameters**: SQL parameters (for ? placeholders)

#### 📤 Returns
    APSW Cursor object (used to fetch results)

#### ⚠️ Exceptions
- **NanaSQLiteConnectionError**: If connection is closed
- **NanaSQLiteDatabaseError**: SQL execution error

#### 💡 Example
```python
    >>> cursor = db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
    >>> for row in cursor:
    ...     print(row)
```

    # If cache update is needed:
```python
    >>> db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new"', "key"))
    >>> db.refresh("key")  # Update cache
```

---

### execute_many

```python
execute_many(self, sql: 'str', parameters_list: 'list[tuple]') -> 'None'
```

Execute SQL repeatedly with parameters.

Executes the same SQL statement with multiple parameter sets (uses transaction).
Can execute bulk INSERT or UPDATE rapidly.

#### 📥 Arguments
- **sql**: SQL statement to execute
- **parameters_list**: List of parameters

#### 💡 Example
```python
    >>> db.execute_many(
    ...     "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
    ...     [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
    ... )
```

---

### fetch_one

```python
fetch_one(self, sql: 'str', parameters: 'tuple' = None) -> 'tuple | None'
```

Execute SQL and fetch one row.

#### 📥 Arguments
- **sql**: SQL statement to execute
- **parameters**: SQL parameters

#### 📤 Returns
    One row result (tuple), or None if no result

#### 💡 Example
```python
    >>> row = db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
    >>> print(row[0])
```

---

### fetch_all

```python
fetch_all(self, sql: 'str', parameters: 'tuple' = None) -> 'list[tuple]'
```

Execute SQL and fetch all rows.

#### 📥 Arguments
- **sql**: SQL statement to execute
- **parameters**: SQL parameters

#### 📤 Returns
    All row results (list of tuples)

#### 💡 Example
```python
    >>> rows = db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
    >>> for key, value in rows:
    ...     print(key, value)
```

---

### create_table

```python
create_table(self, table_name: 'str', columns: 'dict', if_not_exists: 'bool' = True, primary_key: 'str' = None) -> 'None'
```

Create a table.

#### 📥 Arguments
- **table_name**: Table name
- **columns**: Dict of column definitions (name: SQL type)
- **if_not_exists**: If True, create only if not exists
- **primary_key**: Column name of primary key (None if not specified)

#### 💡 Example
```python
    >>> db.create_table("users", {
    ...     "id": "INTEGER PRIMARY KEY",
    ...     "name": "TEXT NOT NULL",
    ...     "email": "TEXT UNIQUE",
    ...     "age": "INTEGER"
    ... })
```

---

### create_index

```python
create_index(self, index_name: 'str', table_name: 'str', columns: 'list[str]', unique: 'bool' = False, if_not_exists: 'bool' = True) -> 'None'
```

Create an index.

#### 📥 Arguments
- **index_name**: Index name
- **table_name**: Table name
- **columns**: List of columns to index
- **unique**: If True, create unique index
- **if_not_exists**: If True, create only if not exists

#### 💡 Example
```python
    >>> db.create_index("idx_users_email", "users", ["email"], unique=True)
```

---

### query

```python
query(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```

Execute simple SELECT query.

#### 📥 Arguments
- **table_name**: Table name (Default table if None)
- **columns**: List of columns to select (All columns if None)
- **where**: WHERE clause condition (Parameter binding recommended)
- **parameters**: WHERE clause parameters
- **order_by**: ORDER BY clause
- **limit**: LIMIT clause
- **strict_sql_validation**: If True, reject queries with unauthorized functions
- **allowed_sql_functions**: List of SQL functions allowed temporarily for this query
- **forbidden_sql_functions**: List of SQL functions forbidden temporarily for this query
- **override_allowed**: If True, ignore instance allow settings

#### 📤 Returns
    List of results (each row is a dict)

#### 💡 Example
```python
    >>> # Get all data from default table
    >>> results = db.query()
```

```python
    >>> # Search with condition
    >>> results = db.query(
    ...     table_name="users",
    ...     columns=["id", "name", "email"],
    ...     where="age > ?",
    ...     parameters=(20,),
    ...     order_by="name ASC",
    ...     limit=10
    ... )
```

---

### table_exists

```python
table_exists(self, table_name: 'str') -> 'bool'
```

Check if table exists.

#### 📥 Arguments
- **table_name**: Table name

#### 📤 Returns
    True if exists, False otherwise

---

### list_tables

```python
list_tables(self) -> 'list[str]'
```

Get list of all tables in the database.

#### 📤 Returns
    List of table names

---

### drop_table

```python
drop_table(self, table_name: 'str', if_exists: 'bool' = True) -> 'None'
```

Delete a table.

#### 📥 Arguments
- **table_name**: Table name
- **if_exists**: If True, delete only if exists

---

### drop_index

```python
drop_index(self, index_name: 'str', if_exists: 'bool' = True) -> 'None'
```

Delete an index.

#### 📥 Arguments
- **index_name**: Index name
- **if_exists**: If True, delete only if exists

---

### alter_table_add_column

```python
alter_table_add_column(self, table_name: 'str', column_name: 'str', column_type: 'str', default: 'Any' = None) -> 'None'
```

Add a column to an existing table.

#### 📥 Arguments
- **table_name**: Table name
- **column_name**: Column name
- **column_type**: Column type (SQL type)
- **default**: Default value (None for no default)

---

### get_table_schema

```python
get_table_schema(self, table_name: 'str') -> 'list[dict]'
```

Get table structure.

#### 📥 Arguments
- **table_name**: Table name

#### 📤 Returns
    List of column info (each column is a dict)

#### 💡 Example
```python
    >>> schema = db.get_table_schema("users")
    >>> for col in schema:
    ...     print(f"{col['name']}: {col['type']}")
```

---

### list_indexes

```python
list_indexes(self, table_name: 'str' = None) -> 'list[dict]'
```

Get list of indexes.

#### 📥 Arguments
- **table_name**: Table name (All indexes if None)

#### 📤 Returns
    List of index info

---

### sql_insert

```python
sql_insert(self, table_name: 'str', data: 'dict') -> 'int'
```

INSERT directly from dict.

#### 📥 Arguments
- **table_name**: Table name
- **data**: Dict of column names and values

#### 📤 Returns
    Inserted ROWID

#### 💡 Example
```python
    >>> rowid = db.sql_insert("users", {
    ...     "name": "Alice",
    ...     "email": "alice@example.com",
    ...     "age": 25
    ... })
```

---

### sql_update

```python
sql_update(self, table_name: 'str', data: 'dict', where: 'str', parameters: 'tuple' = None) -> 'int'
```

UPDATE with dict and where condition.

#### 📥 Arguments
- **table_name**: Table name
- **data**: Dict of column names and values to update
- **where**: WHERE clause condition
- **parameters**: WHERE clause parameters

#### 📤 Returns
    Number of updated rows

---

### sql_delete

```python
sql_delete(self, table_name: 'str', where: 'str', parameters: 'tuple' = None) -> 'int'
```

DELETE with where condition.

#### 📥 Arguments
- **table_name**: Table name
- **where**: WHERE clause condition
- **parameters**: WHERE clause parameters

#### 📤 Returns
    Number of deleted rows

#### 💡 Example
```python
    >>> count = db.sql_delete("users", "age < ?", (18,))
```

---

### upsert

```python
upsert(self, table_name: 'str', data: 'dict', conflict_columns: 'list[str]' = None) -> 'int'
```

Simplified INSERT OR REPLACE (upsert).

#### 📥 Arguments
- **table_name**: Table name
- **data**: Dict of column names and values
- **conflict_columns**: Columns used for conflict resolution (INSERT OR REPLACE if None)

#### 📤 Returns
    Inserted/Updated ROWID

#### 💡 Example
```python
    >>> # Simple INSERT OR REPLACE
    >>> db.upsert("users", {"id": 1, "name": "Alice", "age": 25})
```

```python
    >>> # Using ON CONFLICT
    >>> db.upsert("users",
    ...     {"email": "alice@example.com", "name": "Alice", "age": 26},
    ...     conflict_columns=["email"]
    ... )
```

---

### count

```python
count(self, table_name: 'str' = None, where: 'str' = None, parameters: 'tuple' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'int'
```

Get record count.

#### 📥 Arguments
- **table_name**: Table name (Default table if None)
- **where**: WHERE clause condition (optional)
- **parameters**: WHERE clause parameters
- **strict_sql_validation**: If True, reject queries with unauthorized functions
- ... (other validation params)

#### 💡 Example
```python
    >>> total = db.count("users")
    >>> adults = db.count("users", "age >= ?", (18,))
```

---

### exists

```python
exists(self, table_name: 'str', where: 'str', parameters: 'tuple' = None) -> 'bool'
```

Check record existence.

#### 📥 Arguments
- **table_name**: Table name
- **where**: WHERE clause condition
- **parameters**: WHERE clause parameters

#### 📤 Returns
    True if exists

---

### query_with_pagination

```python
query_with_pagination(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, offset: 'int' = None, group_by: 'str' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```

Extended query (supports offset, group_by).

#### 📥 Arguments
- **table_name**: Table name
- **columns**: Columns to Select
- **where**: WHERE clause
- **parameters**: Parameters
- **order_by**: ORDER BY clause
- **limit**: LIMIT clause
- **offset**: OFFSET clause (for pagination)
- **group_by**: GROUP BY clause
- ... (validation params)

#### 📤 Returns
    List of results

#### 💡 Example
```python
    >>> # Pagination
    >>> page2 = db.query_with_pagination("users",
    ...     limit=10, offset=10, order_by="id ASC")
```

```python
    >>> # Group aggregation
    >>> stats = db.query_with_pagination("orders",
    ...     columns=["user_id", "COUNT(*) as order_count"],
    ...     group_by="user_id"
    ... )
```

---

### vacuum

```python
vacuum(self) -> 'None'
```

Optimize database (execute VACUUM).

Reclaims storage from deleted records and optimizes the database file.

#### 💡 Example
```python
    >>> db.vacuum()
```

---

### get_db_size

```python
get_db_size(self) -> 'int'
```

Get database file size (in bytes).

#### 📤 Returns
    Database file size

#### 💡 Example
```python
    >>> size = db.get_db_size()
    >>> print(f"DB size: {size / 1024 / 1024:.2f} MB")
```

---

### export_table_to_dict

```python
export_table_to_dict(self, table_name: 'str') -> 'list[dict]'
```

Get entire table as a list of dicts.

#### 📥 Arguments
- **table_name**: Table name

#### 📤 Returns
    List of all records

---

### import_from_dict_list

```python
import_from_dict_list(self, table_name: 'str', data_list: 'list[dict]') -> 'int'
```

Bulk insert from list of dicts.

#### 📥 Arguments
- **table_name**: Table name
- **data_list**: List of data to insert

#### 📤 Returns
    Number of inserted rows

---

### get_last_insert_rowid

```python
get_last_insert_rowid(self) -> 'int'
```

Get ROWID of the last insertion.

#### 📤 Returns
    Last inserted ROWID

---

### pragma

```python
pragma(self, pragma_name: 'str', value: 'Any' = None) -> 'Any'
```

Get/Set PRAGMA settings.

#### 📥 Arguments
- **pragma_name**: PRAGMA name
- **value**: Setting value (Get only if None)

#### 📤 Returns
    Current value if value is None, otherwise None

#### 💡 Example
```python
    >>> # Get
    >>> mode = db.pragma("journal_mode")
```

```python
    >>> # Set
    >>> db.pragma("foreign_keys", 1)
```

---

### begin_transaction

```python
begin_transaction(self) -> 'None'
```

Start a transaction.

- **Note**:
    SQLite does not support nested transactions.
    If already in a transaction, NanaSQLiteTransactionError occurs.

#### ⚠️ Exceptions
- **NanaSQLiteTransactionError**: If already in transaction
- **NanaSQLiteConnectionError**: If connection is closed
- **NanaSQLiteDatabaseError**: If transaction start fails

---

### commit

```python
commit(self) -> 'None'
```

Commit transaction.

#### ⚠️ Exceptions
- **NanaSQLiteTransactionError**: If attempted to commit outside transaction

---

### rollback

```python
rollback(self) -> 'None'
```

Rollback transaction.

#### ⚠️ Exceptions
- **NanaSQLiteTransactionError**: If attempted to rollback outside transaction

---

### in_transaction

```python
in_transaction(self) -> 'bool'
```

Return whether currently in a transaction.

#### 📤 Returns
- **bool**: True if in transaction

---

### transaction

```python
transaction(self)
```

Context manager for transactions.

Automatically commits if no exception occurs within the context,
and automatically rolls back if an exception occurs.

#### ⚠️ Exceptions
- **NanaSQLiteTransactionError**: If already in transaction

#### 💡 Example
```python
    >>> with db.transaction():
    ...     db.sql_insert("users", {"name": "Alice"})
    ...     db.sql_insert("users", {"name": "Bob"})
    ...     # Auto commit, rollback on error
```

---

### table

```python
table(self, table_name: 'str')
```

Get NanaSQLite instance for sub-table.

Creates a new instance but shares SQLite connection and lock.
This allows multiple table instances to work safely using the same connection.

⚠️ Important Notes:
- Do not create multiple instances for the same table
  It causes cache inconsistency as each instance has independent cache
- **Recommended**: Reuse table instances

:param table_name: Table name
:return NanaSQLite: New table instance

#### ⚠️ Exceptions
- **NanaSQLiteConnectionError**: If connection is closed

#### 💡 Example
```python
    >>> with NanaSQLite("app.db", table="main") as main_db:
    ...     users_db = main_db.table("users")
    ...     products_db = main_db.table("products")
```

---
