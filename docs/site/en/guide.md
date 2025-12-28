# NanaSQLite Tutorial

A step-by-step guide to learning NanaSQLite from basics to advanced features.

## Prerequisites

- Python 3.9 or higher
- Basic understanding of Python dictionaries
- Familiarity with SQLite is helpful but not required

## Installation

```bash
pip install nanasqlite
```

## Lesson 1: Your First Database

### Creating a Database

```python
from nanasqlite import NanaSQLite

# Create or open a database file
db = NanaSQLite("tutorial.db")

# Store some data
db["greeting"] = "Hello, World!"
db["number"] = 42
db["pi"] = 3.14159

# Retrieve data
print(db["greeting"])  # Hello, World!
print(db["number"])    # 42

# Close when done
db.close()
```

**What happened?**
- A SQLite database file `tutorial.db` was created
- Data was immediately saved to disk
- The data persists even after the program ends

### Using Context Manager

```python
from nanasqlite import NanaSQLite

# Automatically closes database when done
with NanaSQLite("tutorial.db") as db:
    db["message"] = "Using context manager!"
    print(db["message"])
# Database automatically closed here
```

**Best Practice:** Always use the context manager (`with` statement) to ensure proper cleanup.

## Lesson 2: Working with Complex Data

### Storing Nested Structures

```python
with NanaSQLite("tutorial.db") as db:
    # Store a user profile
    db["user_alice"] = {
        "name": "Alice",
        "age": 30,
        "email": "alice@example.com",
        "preferences": {
            "theme": "dark",
            "notifications": True,
            "language": "en"
        },
        "tags": ["admin", "developer", "python"]
    }
    
    # Access nested data
    user = db["user_alice"]
    print(user["name"])                      # Alice
    print(user["preferences"]["theme"])      # dark
    print(user["tags"][0])                   # admin
```

### Supported Data Types

```python
with NanaSQLite("tutorial.db") as db:
    db["string"] = "text"
    db["integer"] = 100
    db["float"] = 99.99
    db["boolean"] = True
    db["none"] = None
    db["list"] = [1, 2, 3, "four"]
    db["dict"] = {"nested": {"deeply": {"value": 123}}}
```

**Note:** NanaSQLite automatically serializes complex Python objects to JSON.

## Lesson 3: Dictionary Operations

### Checking Existence

```python
with NanaSQLite("tutorial.db") as db:
    db["config"] = {"theme": "dark"}
    
    # Check if key exists
    if "config" in db:
        print("Config exists!")
    
    if "missing" not in db:
        print("This key doesn't exist")
    
    # Get with default value
    value = db.get("missing", "default_value")
    print(value)  # default_value
```

### Iterating Over Data

```python
with NanaSQLite("tutorial.db") as db:
    # Add some data
    db["user_1"] = {"name": "Alice"}
    db["user_2"] = {"name": "Bob"}
    db["user_3"] = {"name": "Charlie"}
    
    # Iterate over keys
    for key in db.keys():
        print(key)
    
    # Iterate over values
    for value in db.values():
        print(value)
    
    # Iterate over key-value pairs
    for key, value in db.items():
        print(f"{key}: {value}")
```

### Updating and Deleting

```python
with NanaSQLite("tutorial.db") as db:
    # Update a single key
    db["counter"] = 0
    db["counter"] = db["counter"] + 1
    print(db["counter"])  # 1
    
    # Update multiple keys at once
    db.update({
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    })
    
    # Delete a key
    del db["key1"]
    
    # Pop (get and delete)
    value = db.pop("key2")
    print(value)  # value2
    
    # Clear all data
    # db.clear()  # Uncomment to delete everything
```

## Lesson 4: Performance Optimization

### Bulk Loading

```python
# For read-heavy workloads, load all data at startup
with NanaSQLite("tutorial.db", bulk_load=True) as db:
    # All data is now in memory
    # Subsequent reads are ultra-fast
    for key in db.keys():
        print(db[key])  # No database queries!
```

**When to use bulk_load:**
- Small to medium databases (<100MB)
- Frequent reads of most keys
- Application startup time is not critical

**When NOT to use bulk_load:**
- Large databases (>1GB)
- Sparse access patterns (only few keys accessed)
- Memory-constrained environments

### Batch Operations

```python
with NanaSQLite("tutorial.db") as db:
    # ❌ Slow: Individual inserts
    for i in range(1000):
        db[f"item_{i}"] = {"value": i}
    
    # ✅ Fast: Batch insert (10-100x faster)
    data = {f"item_{i}": {"value": i} for i in range(1000)}
    db.batch_update(data)
    
    # Batch delete
    keys_to_delete = [f"item_{i}" for i in range(500)]
    db.batch_delete(keys_to_delete)
```

**Performance Tip:** For 100+ operations, always use batch methods.

## Lesson 5: Working with Pydantic Models

```python
from pydantic import BaseModel
from nanasqlite import NanaSQLite

class User(BaseModel):
    name: str
    age: int
    email: str

with NanaSQLite("tutorial.db") as db:
    # Save Pydantic model
    user = User(name="Alice", age=30, email="alice@example.com")
    db.set_model("user_alice", user)
    
    # Retrieve as Pydantic model
    retrieved = db.get_model("user_alice", User)
    print(retrieved.name)   # Alice
    print(retrieved.age)    # 30
    print(type(retrieved))  # <class '__main__.User'>
```

## Lesson 6: Direct SQL Queries

### Basic Queries

```python
with NanaSQLite("tutorial.db") as db:
    # Create a custom table
    db.create_table("users", {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "email": "TEXT UNIQUE",
        "age": "INTEGER"
    })
    
    # Insert data
    db.sql_insert("users", {"name": "Alice", "email": "alice@example.com", "age": 30})
    db.sql_insert("users", {"name": "Bob", "email": "bob@example.com", "age": 25})
    
    # Query data
    results = db.query(
        table_name="users",
        columns=["name", "age"],
        where="age > ?",
        parameters=(25,),
        order_by="name ASC"
    )
    
    for row in results:
        print(f"{row['name']}: {row['age']}")
```

### Advanced SQL

```python
with NanaSQLite("tutorial.db") as db:
    # Execute custom SQL
    cursor = db.execute("SELECT * FROM users WHERE name LIKE ?", ("A%",))
    for row in cursor:
        print(row)
    
    # Fetch all results
    rows = db.fetch_all("SELECT name, age FROM users ORDER BY age DESC")
    
    # Fetch one result
    row = db.fetch_one("SELECT * FROM users WHERE email = ?", ("alice@example.com",))
```

## Lesson 7: Error Handling

```python
from nanasqlite import NanaSQLite

with NanaSQLite("tutorial.db") as db:
    # Handle missing keys
    try:
        value = db["nonexistent"]
    except KeyError:
        print("Key not found!")
    
    # Better: Use get() with default
    value = db.get("nonexistent", "default")
    
    # Handle SQL errors
    import apsw
    try:
        db.execute("INVALID SQL")
    except apsw.Error as e:
        print(f"SQL error: {e}")
```

## Lesson 8: Multiple Tables

You can use different tables for different data types within a single database file. Using the `.table()` method allows you to operate on independent tables while sharing the same underlying connection.

```python
from nanasqlite import NanaSQLite

# Create the main instance
db = NanaSQLite("app.db")

# Get sub-table instances (efficient as they share the connection)
users_db = db.table("users")
config_db = db.table("config")
cache_db = db.table("cache")

# Each operates independently
users_db["alice"] = {"name": "Alice", "role": "admin"}
config_db["theme"] = "dark"
cache_db["temp_data"] = {"expires": "2024-12-31"}

# Closing the main instance closes all related connections
db.close()
```

## Lesson 9: Async Usage (Advanced)

For async frameworks like FastAPI:

```python
import asyncio
from nanasqlite import AsyncNanaSQLite

async def main():
    async with AsyncNanaSQLite("tutorial.db") as db:
        # Async operations
        await db.aset("user", {"name": "Alice"})
        user = await db.aget("user")
        print(user)
        
        # Concurrent operations
        results = await asyncio.gather(
            db.aget("key1"),
            db.aget("key2"),
            db.aget("key3")
        )

asyncio.run(main())
```

## Lesson 10: Cache Strategies (v1.3.0)

To keep memory usage under control while maintaining high speed, you can choose an eviction strategy (LRU).

### Using LRU Cache

```python
from nanasqlite import NanaSQLite, CacheType

# Cache only the most recent 1000 items in memory
with NanaSQLite("app.db", cache_strategy=CacheType.LRU, cache_size=1000) as db:
    db["key"] = "value"
```

### Maximizing Performance

If `lru-dict` is installed, NanaSQLite uses a C-extension for ultra-fast cache operations.

```bash
pip install nanasqlite[speed]
```

For more details, see the [Performance Tuning Guide](performance_tuning).

## Common Patterns

### Configuration Storage

```python
with NanaSQLite("config.db") as db:
    # Store app configuration
    db["app_config"] = {
        "version": "1.0.0",
        "debug": False,
        "database_url": "sqlite:///data.db",
        "secret_key": "your-secret-key"
    }
    
    # Retrieve configuration
    config = db["app_config"]
    if config["debug"]:
        print("Debug mode enabled")
```

### Caching

```python
import time

with NanaSQLite("cache.db") as db:
    # Store cached data with timestamp
    db["api_response"] = {
        "data": {"users": [...]},
        "cached_at": time.time()
    }
    
    # Check cache age
    cached = db.get("api_response")
    if cached and (time.time() - cached["cached_at"]) < 3600:
        # Cache is fresh (less than 1 hour old)
        data = cached["data"]
    else:
        # Fetch fresh data from your API
        # Example: data = requests.get("https://api.example.com/data").json()
        data = fetch_from_api()  # Replace with your actual API call
        db["api_response"] = {"data": data, "cached_at": time.time()}
```

### Session Storage

```python
import uuid
import time

with NanaSQLite("sessions.db") as db:
    # Create session
    session_id = str(uuid.uuid4())
    db[f"session_{session_id}"] = {
        "user_id": "alice",
        "created_at": time.time(),
        "data": {"cart": ["item1", "item2"]}
    }
    
    # Retrieve session
    session = db.get(f"session_{session_id}")
    if session:
        print(f"User: {session['user_id']}")
        print(f"Cart: {session['data']['cart']}")
```

## Best Practices

1. **Always use context managers** (`with` statement)
2. **Use batch operations** for multiple writes (100+ items)
3. **Use `bulk_load=True`** for read-heavy workloads
4. **Use `get()` with defaults** instead of `try/except KeyError`
5. **Separate concerns** with different tables
6. **Close databases** when done (automatic with context manager)

## Next Steps

- Read the [API Reference](./api_sync) for complete method documentation
- Explore [Async Guide](async_guide) for async/await usage
- Check [Best Practices](best_practices) for production tips
- See [examples/](https://github.com/disnana/nanasqlite/tree/main/examples/) for real-world code samples

## Troubleshooting

### Database is locked

```python
# SQLite only allows one writer at a time
# Use transactions for multiple writes
with db.transaction():
    db["key1"] = "value1"
    db["key2"] = "value2"
```

### Memory usage is high

```python
# Don't use bulk_load for large databases
# Use default lazy loading instead
db = NanaSQLite("large.db", bulk_load=False)
```

### Performance is slow

```python
# Use batch operations for bulk writes
data = {f"key_{i}": value for i in range(10000)}
db.batch_update(data)  # Much faster than individual writes
```

## Summary

You've learned:
- ✅ Basic CRUD operations
- ✅ Working with complex nested data
- ✅ Performance optimization (bulk_load, batch operations)
- ✅ Pydantic integration
- ✅ Direct SQL queries
- ✅ Error handling
- ✅ Common usage patterns

Happy coding with NanaSQLite!
