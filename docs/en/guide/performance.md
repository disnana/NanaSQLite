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
 
NanaSQLite provides several caching strategies to balance memory usage and speed.

### 1. Unbounded Cache (`CacheType.UNBOUNDED`)
The **default behavior**. Data is cached in memory indefinitely once accessed.

### 2. LRU Cache (`CacheType.LRU`)
**Introduced in v1.3.0**. Set a limit on the number of cached items; oldest are automatically evicted.

### 3. TTL Cache (`CacheType.TTL`)
**Introduced in v1.3.1**. Set an expiration time for data. `cache_persistence_ttl=True` enables automatic deletion from the DB.

### ⚡ Speedup Options: `orjson` + `lru-dict`
Accelerate JSON serialization (orjson) and cache operations (lru-dict).
```bash
pip install "nanasqlite[speed]"
```

### ⚡ Loading Methods
1.  **bulk_load=True (at initialization)**: Loads all data into memory at startup.
2.  **Default (Lazy Loading)**: Only stores accessed data in memory.

> [!TIP]
> If you need to refresh the cache, use `db.refresh(key)` or `db.get_fresh(key)`.
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
