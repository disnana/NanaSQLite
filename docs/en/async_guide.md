# Async Support Quick Guide

## Why Async?

The traditional synchronous `NanaSQLite` blocks processing until database operations complete. While this is fine for regular Python applications, it becomes problematic for async applications such as:

- **FastAPI, Quart, Sanic**: Async web frameworks
- **aiohttp**: Async HTTP client/server
- **Discord.py, Telegram Bot API**: Async bots
- **Other asyncio-based applications**

In these applications, blocking operations halt the event loop and degrade overall performance.

## AsyncNanaSQLite Solution

`AsyncNanaSQLite` uses a dedicated **thread pool executor** to run all database operations, preventing event loop blocking.

### Key Features

- **Dedicated thread pool**: Configurable worker count (default: 5)
- **High performance**: APSW-based optimization
- **Concurrent processing**: Execute multiple operations simultaneously
- **Resource management**: Automatic thread pool cleanup

```python
# ❌ Sync version (blocks async apps)
from nanasqlite import NanaSQLite
db = NanaSQLite("app.db")
user = db["user"]  # Blocks event loop!

# ✅ Async version (non-blocking with thread pool)
from nanasqlite import AsyncNanaSQLite
async with AsyncNanaSQLite("app.db", max_workers=10) as db:
    user = await db.aget("user")  # Does not block event loop
```

## Basic Usage

### 1. Import and Initialize

```python
import asyncio
from nanasqlite import AsyncNanaSQLite

async def main():
    # Use context manager (recommended)
    # max_workers: adjust based on concurrency needs
    async with AsyncNanaSQLite("mydata.db", max_workers=5) as db:
        # Database operations
        await db.aset("key", "value")
        value = await db.aget("key")
        print(value)

asyncio.run(main())
```

### Thread Pool Configuration Guidelines

| Scenario | Recommended max_workers | Reason |
|----------|------------------------|--------|
| Low load (few concurrent connections) | 3-5 | Resource conservation |
| Medium load (dozens of concurrent connections) | 5-10 | Balanced |
| High load (100+ concurrent connections) | 10-20 | High concurrency |
| Very high load (1000+ concurrent connections) | 20-50 | Maximum performance |

### 2. CRUD Operations

```python
async with AsyncNanaSQLite("mydata.db") as db:
    # Create
    await db.aset("user_1", {"name": "Alice", "age": 25})
    
    # Read
    user = await db.aget("user_1")
    
    # Update
    user["age"] = 26
    await db.aset("user_1", user)
    
    # Delete
    await db.adelete("user_1")
```

### 3. Batch Operations

For handling large amounts of data, batch operations are faster:

```python
async with AsyncNanaSQLite("mydata.db") as db:
    # Batch write
    data = {f"user_{i}": {"name": f"User{i}"} for i in range(1000)}
    await db.batch_update(data)
    
    # Batch delete
    keys = [f"user_{i}" for i in range(500)]
    await db.batch_delete(keys)
```

### 4. Concurrent Operations

Execute multiple operations simultaneously:

```python
import asyncio

async with AsyncNanaSQLite("mydata.db") as db:
    # Concurrent reads
    users = await asyncio.gather(
        db.aget("user_1"),
        db.aget("user_2"),
        db.aget("user_3")
    )
```

## Web Framework Usage

### FastAPI Example

```python
from fastapi import FastAPI
from nanasqlite import AsyncNanaSQLite

app = FastAPI()

# Initialize database on application startup
@app.on_event("startup")
async def startup():
    app.state.db = AsyncNanaSQLite("app.db")

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()

# Endpoints
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await app.state.db.aget(f"user_{user_id}")
    if user is None:
        return {"error": "User not found"}
    return user

@app.post("/users")
async def create_user(user: dict):
    await app.state.db.aset(f"user_{user['id']}", user)
    return {"status": "created", "id": user['id']}
```

### Quart Example

```python
from quart import Quart, request, jsonify
from nanasqlite import AsyncNanaSQLite

app = Quart(__name__)
db = None

@app.before_serving
async def startup():
    global db
    db = AsyncNanaSQLite("app.db")

@app.after_serving
async def shutdown():
    await db.close()

@app.route("/users/<user_id>")
async def get_user(user_id):
    user = await db.aget(f"user_{user_id}")
    return jsonify(user)
```

## SQL Operations

Async SQL execution is also available:

```python
async with AsyncNanaSQLite("mydata.db") as db:
    # Create table
    await db.create_table("users", {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "email": "TEXT UNIQUE"
    })
    
    # Insert data
    await db.sql_insert("users", {
        "name": "Alice",
        "email": "alice@example.com"
    })
    
    # Execute query
    users = await db.query(
        table_name="users",
        where="name LIKE ?",
        parameters=("A%",)
    )
```

## Performance Tips

### 1. Thread Pool Optimization

Adjust max_workers based on load:

```python
# Low load application (default)
async with AsyncNanaSQLite("mydata.db") as db:
    pass

# High load application (many concurrent connections)
async with AsyncNanaSQLite("mydata.db", max_workers=20) as db:
    # Efficiently handle 100 concurrent operations
    results = await asyncio.gather(*[db.aget(f"key_{i}") for i in range(100)])
```

**Recommended settings:**
- **Development**: max_workers=5 (default)
- **Production (medium)**: max_workers=10-15
- **Production (large)**: max_workers=20-50

### 2. Use Batch Operations

```python
# ❌ Slow (1000 DB operations)
for i in range(1000):
    await db.aset(f"key_{i}", f"value_{i}")

# ✅ Fast (1 transaction)
data = {f"key_{i}": f"value_{i}" for i in range(1000)}
await db.batch_update(data)
```

### 3. Leverage Concurrent Operations

```python
# ❌ Sequential execution (slow)
user1 = await db.aget("user_1")
user2 = await db.aget("user_2")
user3 = await db.aget("user_3")

# ✅ Concurrent execution (fast, processed by thread pool)
users = await asyncio.gather(
    db.aget("user_1"),
    db.aget("user_2"),
    db.aget("user_3")
)
```

### 4. Use bulk_load Appropriately

When you have frequently accessed data:

```python
# Load all data at startup (read-heavy workload)
db = AsyncNanaSQLite("mydata.db", bulk_load=True, max_workers=10)
```

### 5. Reuse Connections and Thread Pools

```python
# ❌ Create new instance each time (slow)
async def handler():
    async with AsyncNanaSQLite("app.db") as db:
        return await db.aget("data")

# ✅ Reuse instance (fast)
db = None

async def startup():
    global db
    db = AsyncNanaSQLite("app.db", max_workers=15)

async def handler():
    return await db.aget("data")

async def shutdown():
    await db.close()  # Also auto-cleans up thread pool
```

## Sync vs Async Usage

| Use Case | Recommended Class |
|----------|------------------|
| FastAPI, aiohttp async frameworks | `AsyncNanaSQLite` |
| Discord.py, Telegram bots | `AsyncNanaSQLite` |
| Regular Python scripts | `NanaSQLite` |
| Django (sync framework) | `NanaSQLite` |
| Command-line tools | `NanaSQLite` |

## Troubleshooting

### RuntimeError: Event loop is closed

Use context manager:

```python
# ❌ Manual close (may error)
db = AsyncNanaSQLite("app.db")
await db.aset("key", "value")
await db.close()

# ✅ Context manager (recommended)
async with AsyncNanaSQLite("app.db") as db:
    await db.aset("key", "value")
```

### Migrating Sync Code to Async

Method mapping table:

| Sync Version | Async Version |
|--------------|---------------|
| `db[key]` or `db.get(key)` | `await db.aget(key)` |
| `db[key] = value` | `await db.aset(key, value)` |
| `del db[key]` | `await db.adelete(key)` |
| `key in db` | `await db.acontains(key)` |
| `len(db)` | `await db.alen()` |
| `db.keys()` | `await db.akeys()` |
| `db.batch_update(data)` | `await db.batch_update(data)` |

## Summary

- `AsyncNanaSQLite` prevents blocking in async applications
- All operations require `await`
- Concurrent operations enable speedup
- Ideal for async frameworks like FastAPI
- Compatible with sync version

See [async_demo.py](../../examples/async_demo.py) for detailed usage examples.
