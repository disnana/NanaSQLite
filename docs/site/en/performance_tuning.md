# Performance Tuning Guide

NanaSQLite is designed to run fast with standard configuration, but choosing appropriate development patterns and settings can boost performance by several times to tens of times.

---

## 🚀 Core Optimization: Utilizing Batch Operations

The most expensive operation in SQLite is "starting and committing a transaction".

### ❌ Anti-Pattern: Individual Writes in Loop
The following code is very slow because disk I/O occurs for each loop iteration.
```python
# 1000 disk commits occur (can take seconds)
for i in range(1000):
    db[f"key_{i}"] = i
```

### ✅ Recommended Pattern: `batch_update` / `batch_get`
Using NanaSQLite's batch operation methods processes everything in a single transaction, resulting in dramatic speed improvements.
```python
# Completed in a single disk commit (finished in milliseconds)
data = {f"key_{i}": i for i in range(1000)}
db.batch_update(data)
```

**Benchmark Metric**: For large volume writes, expect a speedup of **10x to 100x** or more compared to individual updates.

---

## ⚡ optimizing Database Settings

### WAL (Write-Ahead Logging) Mode
NanaSQLite enables **WAL mode** by default when `optimize=True` is set.
- **Benefit**: Reads are not blocked during writes, improving concurrency.
- **Note**: WAL mode may not work or be unstable on network drives (NFS/SMB).

### Memory Mapped I/O (mmap)
To improve read performance, SQLite's `mmap_size` is utilized. It defaults to 256MB.

---

## 🧠 Cache Strategy

NanaSQLite is equipped with a "Lazy Loading" memory cache.

1.  **bulk_load=True (At Logic)**:
    -   Loads all data into memory at startup.
    -   **Use Case**: Data volume is around tens of thousands, and fast random access is needed immediately after startup.
2.  **Default (Lazy Load)**:
    -   Keeps only accessed data in memory.
    -   **Use Case**: Data volume is huge and you want to suppress memory usage.

> [!TIP]
> If you want to refresh the cache, use `db.refresh()` or `db.get_fresh(key)`.

---

## 🔍 Faster Search with Indexing

Indexing is essential when searching for data other than Key-Value pairs (such as specific fields in JSON) using `query()` or `query_with_pagination()`.

```python
# Create an index on the search target JSON field
db.create_index("idx_user_age", "data", ["age"])
```

**Indications for Index Creation**:
- When frequently searching with a `WHERE` clause on data exceeding several thousand records.
- When search speed is prioritized over data insertion speed.

---

## 💻 OS / Environment Specific Notes

### Windows Environment
- **Antivirus Software**: If virus scanning runs during SQLite file writing, `database is locked` is likely to occur. It is recommended to exclude DB files (.db, .db-wal, .db-shm) from scanning.

### SSD vs HDD
- SQLite is sensitive to disk "seeks". On HDD environments, extreme settings like `synchronous=OFF` (risk of data loss) might be necessary, but operation on **SSD** is recommended whenever possible.

---

## Checklist
- [ ] Are you using `batch_update` for bulk processing?
- [ ] Are you applying `create_index` for frequent searches?
- [ ] Are you using `optimize=True` (default)?
- [ ] Are you running on an SSD environment?
