# Performance Tuning Guide

NanaSQLite is designed to be fast out of the box, but you can significantly boost its performance by choosing the right development patterns and configurations.

---

## 🚀 The Core Optimization: Batch Operations

The most expensive operation in SQLite is beginning and committing a transaction.

### ❌ Anti-Pattern: Individual Writes in a Loop
The following code is very slow because every iteration triggers a disk I/O operation.
```python
# Triggers 1000 disk commits (can take seconds or even tens of seconds)
for i in range(1000):
    db[f"key_{i}"] = i
```

### ✅ Recommended Pattern: `batch_update` / `batch_get`
Using NanaSQLite's batch methods allows many operations to be processed in a single transaction, making it dramatically faster.
```python
# Completes in a single disk commit (finished in milliseconds)
data = {f"key_{i}": i for i in range(1000)}
db.batch_update(data)
```

**Benchmark Indicator**: You can expect speedups of **10x to 100x or more** compared to individual updates for bulk operations.

---

## ⚡ Database Configuration Optimizations

### WAL (Write-Ahead Logging) Mode
By default, NanaSQLite enables **WAL mode** when `optimize=True`.
- **Pros**: Readers do not block writers, and writers do not block readers, greatly improving concurrency.
- **Caveat**: WAL mode may be unstable on network drives (NFS/SMB).

### Memory-Mapped I/O (mmap)
NanaSQLite utilizes SQLite's `mmap_size` to improve read performance. It is set to 256MB by default.

---

## 🧠 Caching Strategy (v1.3.0+)

NanaSQLite provides multiple caching strategies to optimize the balance between memory usage and performance.

### 1. Unbounded Cache (`CacheType.UNBOUNDED`)
The **default behavior**. Once accessed, data is cached in memory indefinitely.
- **Pros**: Fastest re-access for the same key.
- **Caveat**: Can lead to Out-Of-Memory (OOM) errors if the dataset is extremely large.

### 2. LRU Cache (`CacheType.LRU`)
**Introduced in v1.3.0**. Set a limit on the number of items in the cache; the least recently used items are automatically evicted.
- **Usage**: Specify `cache_strategy=CacheType.LRU, cache_size=1000`.
- **Pros**: Keeps memory usage predictable and capped.

### ⚡ Speedup Options: `orjson` + `lru-dict`

You can leverage **orjson** to significantly accelerate JSON serialization and deserialization.

- **orjson**: Typically **3x to 5x faster** than the standard `json` module.
- **lru-dict**: A high-performance LRU data structure implemented as a C-extension.

```bash
# Recommendation: Use quotes to prevent shell interpretation of brackets
pip install "nanasqlite[speed]"
```

NanaSQLite automatically detects and uses these if available. Otherwise, it falls back to standard library equivalents (`json`, `OrderedDict`).

### 3. TTL Cache (`CacheType.TTL`)
**Introduced in v1.3.1**. Set an expiration time for data to automatically invalidate old entries.

- **Usage**: Set `cache_strategy=CacheType.TTL, cache_ttl=3600` (1 hour).
- **Persistence TTL**: Enable `cache_persistence_ttl=True` to automatically delete expired items from the SQLite database as well. Ideal for session management.

### 📌 Per-Table Configuration
Useful when you want to restrict memory usage only for specific tables (e.g., massive log tables).
```python
# Main DB is unbounded, but logs table caches only the latest 100 entries.
logs = db.table("logs", cache_strategy=CacheType.LRU, cache_size=100)

# Session table using 30-minute (1800s) TTL with automatic deletion from DB.
sessions = db.table("sessions", 
    cache_strategy=CacheType.TTL, 
    cache_ttl=1800, 
    cache_persistence_ttl=True
)
```

---

## ⚡ Cache Loading Methods

1.  **bulk_load=True (at initialization)**:
    -   Loads all data into memory at startup.
    -   **Use Case**: When you have tens of thousands of items and need high-speed random access immediately.
2.  **Default (Lazy Loading)**:
    -   Only stores accessed data in memory.

> [!TIP]
> If you need to force a cache refresh, use `db.refresh(key)` or `db.get_fresh(key)` to fetch directly from the DB.
> To clear all in-memory cache, call `db.clear_cache()`.

---

## 🔍 Fast Search via Indexing

When using `query()` or `query_with_pagination()` to search for data other than the primary key (e.g., searching within JSON fields), indexing is essential.

```python
# Create an index on a JSON field being searched
db.create_index("idx_user_age", "data", ["age"])
```

**Indexing Guidelines**:
- When frequently performing `WHERE` clause searches on datasets larger than a few thousand items.
- When search speed is prioritized over insertion speed.

---

## 💻 OS and Environment Notes

### Windows
- **Antivirus Software**: Real-time virus scanning during SQLite writes can lead to `database is locked` errors. We recommend excluding the database files (.db, .db-wal, .db-shm) from active scans.

### SSD vs HDD
- SQLite relies heavily on fsync for every transaction, making it highly dependent on disk persistence latency. In HDD environments, this synchronization cost dominates performance, sometimes requiring settings that sacrifice fault tolerance, such as `synchronous=OFF`. We strongly recommend operating on SSDs with high fsync performance.

---

## Checklist
- [ ] Are you using `batch_update` for bulk processing?
- [ ] Have you applied `create_index` for frequent searches?
- [ ] Are you using the default `optimize=True`?
- [ ] Is the database running on an SSD?
