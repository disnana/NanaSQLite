# AsyncNanaSQLite API Reference

## Overview

`AsyncNanaSQLite` is an async/await wrapper for using NanaSQLite in async applications. All database operations are executed in a thread pool to prevent blocking the event loop.

## Classes

### AsyncNanaSQLite

```python
from nanasqlite import AsyncNanaSQLite

async with AsyncNanaSQLite(
    db_path="mydata.db",
    table="data",
    bulk_load=False,
    optimize=True,
    cache_size_mb=64,
    max_workers=5,
    thread_name_prefix="AsyncNanaSQLite"
) as db:
    await db.aset("key", "value")
```

**Parameters:**
- `db_path` (str): Path to SQLite database file
- `table` (str): Table name to use (default: "data")
- `bulk_load` (bool): Load all data on initialization (default: False)
- `optimize` (bool): Apply performance optimizations like WAL mode (default: True)
- `cache_size_mb` (int): SQLite cache size in MB (default: 64)
- `max_workers` (int): Maximum number of workers in thread pool (default: 5)
- `thread_name_prefix` (str): Prefix for thread names (default: "AsyncNanaSQLite")

## Async Dict-like Interface

### aget()
```python
value = await db.aget(key, default=None)
```
Get value for key asynchronously. Returns default if key doesn't exist.

### aset()
```python
await db.aset(key, value)
```
Set value for key asynchronously. Immediately persisted to database.

### adelete()
```python
await db.adelete(key)
```
Delete key asynchronously. Raises KeyError if key doesn't exist.

### acontains()
```python
exists = await db.acontains(key)
```
Check if key exists asynchronously.

### alen()
```python
count = await db.alen()
```
Get number of keys in database asynchronously.

### akeys()
```python
keys = await db.akeys()
```
Get list of all keys asynchronously.

### avalues()
```python
values = await db.avalues()
```
Get list of all values asynchronously.

### aitems()
```python
items = await db.aitems()
```
Get list of all items (key-value tuples) asynchronously.

### apop()
```python
value = await db.apop(key)
value = await db.apop(key, default)
```
Delete key and return its value asynchronously.

### aupdate()
```python
await db.aupdate({"key1": "value1", "key2": "value2"})
await db.aupdate(key1="value1", key2="value2")
```
Update multiple keys asynchronously.

### aclear()
```python
await db.aclear()
```
Delete all data asynchronously.

### asetdefault()
```python
value = await db.asetdefault(key, default=None)
```
Set value only if key doesn't exist asynchronously.

## Async Special Methods

### load_all()
```python
await db.load_all()
```
Load all data into memory asynchronously.

### refresh()
```python
await db.refresh()  # Refresh all cache
await db.refresh(key)  # Refresh specific key only
```
Refresh cache asynchronously.

### is_cached()
```python
cached = await db.is_cached(key)
```
Check if key is cached asynchronously.

### batch_update()
```python
await db.batch_update({
    "key1": "value1",
    "key2": "value2",
    "key3": {"nested": "data"}
})
```
Batch write asynchronously (fast with transactions).

### batch_delete()
```python
await db.batch_delete(["key1", "key2", "key3"])
```
Batch delete asynchronously.

### to_dict()
```python
data = await db.to_dict()
```
Get all data as Python dict asynchronously.

### copy()
```python
data_copy = await db.copy()
```
Create shallow copy asynchronously.

### get_fresh()
```python
value = await db.get_fresh(key, default=None)
```
Read directly from DB and update cache asynchronously.

## Async Pydantic Support

### set_model()
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

user = User(name="Nana", age=20)
await db.set_model("user", user)
```
Save Pydantic model asynchronously.

### get_model()
```python
user = await db.get_model("user", User)
```
Get Pydantic model asynchronously.

## Async SQL Execution

### execute()
```python
cursor = await db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
```
Execute SQL directly asynchronously.

### execute_many()
```python
await db.execute_many(
    "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
    [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
)
```
Execute SQL with multiple parameters asynchronously.

### fetch_one()
```python
row = await db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
```
Execute SQL and fetch one row asynchronously.

### fetch_all()
```python
rows = await db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
```
Execute SQL and fetch all rows asynchronously.

## Async SQLite Wrapper Functions

### create_table()
```python
await db.create_table("users", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT NOT NULL",
    "email": "TEXT UNIQUE"
})
```
Create table asynchronously.

### create_index()
```python
await db.create_index("idx_users_email", "users", ["email"], unique=True)
```
Create index asynchronously.

### query()
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
Execute SELECT query asynchronously.

### table_exists()
```python
exists = await db.table_exists("users")
```
Check if table exists asynchronously.

### list_tables()
```python
tables = await db.list_tables()
```
Get list of all tables asynchronously.

### drop_table()
```python
await db.drop_table("old_table")
```
Drop table asynchronously.

### drop_index()
```python
await db.drop_index("idx_users_email")
```
Drop index asynchronously.

### sql_insert()
```python
rowid = await db.sql_insert("users", {
    "name": "Alice",
    "email": "alice@example.com",
    "age": 25
})
```
Insert from dict asynchronously.

### sql_update()
```python
count = await db.sql_update("users",
    {"age": 26, "status": "active"},
    "name = ?",
    ("Alice",)
)
```
Update with dict and where clause asynchronously.

### sql_delete()
```python
count = await db.sql_delete("users", "age < ?", (18,))
```
Delete with where clause asynchronously.

### vacuum()
```python
await db.vacuum()
```
Optimize database (run VACUUM) asynchronously.

## Async Context Manager

```python
async with AsyncNanaSQLite("mydata.db") as db:
    await db.aset("key", "value")
    value = await db.aget("key")
# Automatically closed
```

## Concurrent Operations

Run multiple async operations concurrently:

```python
import asyncio

async with AsyncNanaSQLite("mydata.db") as db:
    # Concurrent reads
    results = await asyncio.gather(
        db.aget("key1"),
        db.aget("key2"),
        db.aget("key3")
    )
    
    # Concurrent writes
    await asyncio.gather(
        db.aset("key1", "value1"),
        db.aset("key2", "value2"),
        db.aset("key3", "value3")
    )
```

## Usage Examples

### With FastAPI

```python
from fastapi import FastAPI
from nanasqlite import AsyncNanaSQLite

app = FastAPI()
db = AsyncNanaSQLite("app.db")

@app.on_event("startup")
async def startup():
    global db
    db = AsyncNanaSQLite("app.db")

@app.on_event("shutdown")
async def shutdown():
    await db.close()

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await db.aget(f"user_{user_id}")
    return user

@app.post("/users")
async def create_user(user: dict):
    await db.aset(f"user_{user['id']}", user)
    return {"status": "created"}
```

### With aiohttp

```python
from aiohttp import web
from nanasqlite import AsyncNanaSQLite

async def get_user(request):
    user_id = request.match_info['user_id']
    db = request.app['db']
    user = await db.aget(f"user_{user_id}")
    return web.json_response(user)

async def init_app():
    app = web.Application()
    app['db'] = AsyncNanaSQLite("app.db")
    app.add_routes([web.get('/users/{user_id}', get_user)])
    return app

if __name__ == '__main__':
    web.run_app(init_app())
```

## Multi-table Support (v1.1.0dev1+)

### table()

```python
sub_db = await db.table(table_name)
```

Asynchronously get an AsyncNanaSQLite instance for a sub-table. Shares connection and thread pool executor.

**Parameters:**
- `table_name` (str): Name of the table to access

**Returns:**
- `AsyncNanaSQLite`: A new instance operating on the specified table

**Example:**

```python
async with AsyncNanaSQLite("app.db", table="main") as db:
    # Get sub-table instances
    users_db = await db.table("users")
    config_db = await db.table("config")
    
    # Store data independently in each table
    await users_db.aset("alice", {"name": "Alice", "age": 30})
    await config_db.aset("theme", "dark")
    
    # Retrieve from each table
    user = await users_db.aget("alice")
    theme = await config_db.aget("theme")
```

**Benefits:**
- **Thread-safe**: Concurrent writes from multiple async tasks are safe
- **Resource efficient**: Reuses SQLite connection and thread pool
- **Cache isolation**: Each table maintains independent in-memory cache

---

## Important Notes

1. **Thread Safety**: `AsyncNanaSQLite` is thread-safe as it uses a thread pool internally.
2. **Performance**: Async operations run in a thread pool, so they're not suitable for CPU-intensive tasks. They're most effective for I/O-bound operations.
3. **Sync DB Access**: The `db.sync_db` property provides access to the internal sync DB, but it's not recommended (risk of blocking).

## Compatibility with Sync Version

The existing sync version `NanaSQLite` is fully compatible and uses the same API. If you don't need async, continue using `NanaSQLite`.
