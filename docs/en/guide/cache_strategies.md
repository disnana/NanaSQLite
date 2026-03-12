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

### Fast LRU (lru-dict)

When the `lru-dict` package is installed, a C-extension-based fast LRU is automatically used.

```bash
pip install nanasqlite[speed]  # Installs lru-dict + orjson
```

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
    cache_ttl=60.0,
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
    cache_persistence_ttl=True,
)
```

## Cache Management Methods

```python
db.is_cached("key1")       # Check whether a key is in the cache
db.clear_cache()           # Clear the entire cache
db.load_all()              # Load all data into cache
db.refresh("key1")         # Refresh a specific key's cache entry
value = db.get_fresh("key1")  # Bypass cache, read directly from DB
```

## Performance Comparison

| Operation | UNBOUNDED | LRU | TTL |
|-----------|-----------|-----|-----|
| Read (hit) | O(1) | O(1) | O(1) |
| Read (miss) | O(DB) | O(DB) | O(DB) |
| Write | O(1) | O(1) | O(1) |
| Memory usage | High | Bounded | Bounded |
| Initial load | `bulk_load` | Lazy | Lazy |
