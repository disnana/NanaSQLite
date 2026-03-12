# Cache Strategies Guide

NanaSQLite provides multiple caching strategies to achieve optimal performance for your use case.

## Cache Types Overview

| Strategy | `CacheType` | Characteristics | Recommended For |
|----------|-------------|----------------|-----------------|
| **Unbounded** | `UNBOUNDED` | Keeps all data in memory | Small–medium DBs (default) |
| **LRU** | `LRU` | Evicts least-recently-used entries | Large DBs with memory constraints |
| **TTL** | `TTL` | Auto-expires data after a set duration | Sessions and temporary data |

## Unbounded Cache (UNBOUNDED)

The default caching strategy. Keeps all data in memory for the fastest possible access.

```python
from nanasqlite import NanaSQLite

# Default: unbounded cache
db = NanaSQLite("app.db")

# Explicitly specifying
db = NanaSQLite("app.db", cache_strategy="unbounded")
```

### Characteristics
- O(1) memory reads
- Every database entry is kept in memory
- Memory usage grows proportionally with data size
- Use `bulk_load=True` to load all data into cache at startup

```python
# Bulk-load all data into cache at startup
db = NanaSQLite("app.db", bulk_load=True)

# Load all data into cache later
db.load_all()
```

### Considerations
- High memory consumption with large datasets
- Consider switching to LRU when exceeding 100,000 entries

## LRU Cache

Least Recently Used cache that automatically evicts the oldest-accessed entries.

```python
from nanasqlite import NanaSQLite, CacheType

# LRU cache: keep at most 1000 entries
db = NanaSQLite(
    "app.db",
    cache_strategy=CacheType.LRU,
    cache_size=1000,
)
```

### How It Works

1. If data is in cache, return immediately (cache hit)
2. If not in cache, read from database (cache miss)
3. When cache reaches `cache_size`, the least-recently-accessed entry is evicted

```python
# LRU cache usage example
db = NanaSQLite("app.db", cache_strategy="lru", cache_size=500)

db["key1"] = "value1"  # Added to cache
db["key2"] = "value2"  # Added to cache

val = db["key1"]       # Cache hit (fast)
val = db.get_fresh("key1")  # Bypass cache, read directly from DB
```

### Fast LRU (lru-dict)

When the `lru-dict` package is installed, a C-extension-based fast LRU is automatically used.

```bash
pip install nanasqlite[speed]  # Installs lru-dict + orjson
```

Speed comparison:

| Implementation | Read Speed |
|---------------|-----------|
| Standard LRU (OrderedDict) | 1x |
| FastLRU (lru-dict) | ~2–3x |

### Recommended Settings

| Data Size | Recommended `cache_size` |
|-----------|------------------------|
| Up to 10K entries | 1,000 |
| 10K–100K entries | 5,000 |
| 100K+ entries | 10,000 |

## TTL Cache

Time-To-Live cache that automatically expires data after a specified duration.

```python
from nanasqlite import NanaSQLite, CacheType

# TTL cache: expire after 60 seconds
db = NanaSQLite(
    "app.db",
    cache_strategy=CacheType.TTL,
    cache_ttl=60.0,         # in seconds
)
```

### How It Works

1. When data is added to cache, a timestamp is recorded
2. After TTL elapses, the entry is expired on next access (lazy expiration)
3. Expired data is re-read from the database

```python
import time

db = NanaSQLite("app.db", cache_strategy="ttl", cache_ttl=30.0)

db["session"] = {"user": "alice", "token": "abc123"}

# Within 30 seconds: returned from cache
val = db["session"]  # Fast

time.sleep(31)

# After 30 seconds: reloaded from DB
val = db["session"]  # DB access occurs
```

### TTL + Size Limit

You can also add a size limit to TTL caches:

```python
db = NanaSQLite(
    "app.db",
    cache_strategy="ttl",
    cache_ttl=300.0,     # Expire after 5 minutes
    cache_size=2000,     # Maximum 2000 entries
)
```

### Recommended Use Cases

| Scenario | Recommended `cache_ttl` |
|----------|------------------------|
| Session store | 300–3,600 seconds |
| API response cache | 30–300 seconds |
| Config file cache | 3,600+ seconds |
| Real-time data | 1–10 seconds |

## Cache Persistence TTL

Set `cache_persistence_ttl=True` to trigger a write-back to the database when a TTL entry expires.

```python
db = NanaSQLite(
    "app.db",
    cache_strategy="ttl",
    cache_ttl=60.0,
    cache_persistence_ttl=True,  # Sync to DB on TTL expiration
)
```

## Cache Management Methods

### Inspect and Control

```python
# Check whether a key is in the cache
db.is_cached("key1")  # True / False

# Clear the entire cache
db.clear_cache()

# Load all data into cache
db.load_all()

# Refresh a specific key's cache entry
db.refresh("key1")

# Bypass cache and read directly from DB
value = db.get_fresh("key1")
```

### Batch Operations and Cache

Batch operations automatically update the cache as well:

```python
# Batch update (cache updated simultaneously)
db.batch_update({"k1": "v1", "k2": "v2", "k3": "v3"})

# Batch get (maximizes cache hits)
results = db.batch_get(["k1", "k2", "k3"])

# Batch delete (removes from cache too)
db.batch_delete(["k1", "k2"])
```

## Cache Usage with Async

The same cache strategies are available with `AsyncNanaSQLite`:

```python
from nanasqlite import AsyncNanaSQLite, CacheType

async def main():
    db = AsyncNanaSQLite(
        "app.db",
        cache_strategy=CacheType.LRU,
        cache_size=1000,
    )

    await db.aset("key", "value")
    val = await db.aget("key")  # Cache hit

    await db.aclear_cache()
    await db.aload_all()

    db.close()
```

## Strategy Selection Flowchart

```
Number of entries < 10K?
├─ Yes → UNBOUNDED (default)
└─ No
   ├─ Data needs expiration?
   │  ├─ Yes → TTL
   │  └─ No → LRU
   └─ Plenty of memory available?
      ├─ Yes → UNBOUNDED + bulk_load
      └─ No → LRU (tune cache_size)
```

## Performance Comparison

| Operation | UNBOUNDED | LRU | TTL |
|-----------|-----------|-----|-----|
| Read (hit) | O(1) | O(1) | O(1) |
| Read (miss) | O(DB) | O(DB) | O(DB) |
| Write | O(1) | O(1) | O(1) |
| Memory usage | High | Bounded | Bounded |
| Initial load | `bulk_load` | Lazy | Lazy |
