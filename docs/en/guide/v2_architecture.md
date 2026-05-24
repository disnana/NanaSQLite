# v2 Architecture Guide

> [!IMPORTANT]
> The v2 architecture is an **optional feature introduced in v1.4.0dev1**. It is designed **exclusively for single-process environments**. Using it in multi-process environments (e.g., Gunicorn with multiple workers) will cause **data corruption**.

---

## Overview

The v2 architecture eliminates I/O blocking on the main thread by executing all SQLite writes **asynchronously in a background thread**.

### What problem does it solve?

In the standard v1 mode, calling `db["key"] = value` causes the main thread to wait for disk I/O. When your application writes to the KVS frequently (e.g., inside HTTP request handlers), this I/O latency can become a significant bottleneck.

In v2 mode, writes are buffered in memory and flushed to SQLite in the background, making write latency effectively zero.

---

## Architecture Internals

```
Main Thread
    │
    ├── KVS writes (db["key"] = val)
    │       └──→ [Lane 1: KVS Staging Buffer]  ← protected by dict + lock
    │
    └── SQL execution (db.execute(...))
            └──→ [Lane 2: Strict SQL Queue]    ← ordered by monotonic sequence IDs
                                ↓
                    ┌─ Background Thread ──────┐
                    │   (periodic flush)       │
                    │   BEGIN TRANSACTION      │
                    │   Flush Lane 1 KVS       │
                    │   Execute Lane 2 SQL     │
                    │   COMMIT                 │
                    └──────────────────────────┘
                         on failure → [DLQ] isolated
```

### Two-Lane Hybrid Design

| Lane | Purpose | Key Feature |
|------|---------|-------------|
| **Lane 1** - KVS Staging Buffer | `db["key"] = val` / `del db["key"]` | Write coalescing: merges redundant writes to the same key |
| **Lane 2** - Strict SQL Queue   | `db.execute(sql, params)` etc.      | Monotonic sequence IDs guarantee strict execution order |

---

## Basic Usage

### Enabling v2 Mode

```python
from nanasqlite import NanaSQLite

# Enable v2 mode (defaults to immediate flush)
db = NanaSQLite("mydb.db", v2_mode=True)

# Writes are non-blocking on the main thread
db["user:1"] = {"name": "Alice", "score": 100}
db["user:2"] = {"name": "Bob",   "score": 200}

# Reads return instantly from the in-memory cache (zero latency)
user = db["user:1"]

db.close()  # Flushes remaining buffer to SQLite on shutdown
```

### Batch Configuration with V2Config (v1.4.1+)

To address the issue of having too many parameters, a `V2Config` dataclass has been introduced to group all v2-related settings.

```python
from nanasqlite import NanaSQLite, V2Config

# Group settings using V2Config
cfg = V2Config(
    flush_mode="time",
    flush_interval=1.0,
    chunk_size=500,
    max_dlq_size=1000,
    enable_metrics=True
)

db = NanaSQLite("mydb.db", v2_mode=True, v2_config=cfg)
```

### CRUD-Optimized Memory-First Mode (v1.5.7dev1+)

`memory_first=True` is a CRUD-optimized option built on the v2 engine's time-based flush. It loads the whole KVS table into memory at startup, then serves `get` / `set` / `delete` / `len` / `keys` / `batch_get` and similar CRUD operations from memory. Only changed keys are flushed back to SQLite in the background.

```python
from nanasqlite import NanaSQLite

db = NanaSQLite(
    "mydb.db",
    memory_first=True,
    memory_flush_interval=5.0,  # Default: 5 seconds
)

db["session:1"] = {"user": "alice"}
assert db["session:1"]["user"] == "alice"

db.flush(wait=True)  # Explicit persistence checkpoint
db.close()
```

Regular `v2_mode=True` is for asynchronous writes. `memory_first=True` goes further: memory becomes the source of truth for CRUD operations, and SQLite is updated by periodic delta flushes. Use it only when the full dataset fits comfortably in memory and the application is single-process.

> [!CAUTION]
> `memory_first=True` is not compatible with LRU / TTL / `cache_size` / `cache_persistence_ttl`. If the process is forcibly killed, changes since the last flush may be lost. Call `db.flush(wait=True)` at important boundaries.

### Async (AsyncNanaSQLite)

```python
from nanasqlite import AsyncNanaSQLite

async with AsyncNanaSQLite("mydb.db", v2_mode=True) as db:
    await db.aset("key", "value")
    # Background flush happens automatically
    await db.aflush()  # Or trigger a manual flush explicitly
```

---

## Choosing a Flush Mode

The `flush_mode` parameter controls when writes are persisted to SQLite.

| Mode | Behavior | Best For |
|------|----------|----------|
| `immediate` (default) | Flush after every write | Minimizing data loss risk |
| `count` | Flush when N items are buffered | Throughput-optimized batch processing |
| `time` | Flush at fixed time intervals | Periodic batch workloads |
| `manual` | Flush only when `db.flush()` is called | Full manual control |

```python
# Flush every 100 items (throughput-focused)
db = NanaSQLite("mydb.db", v2_mode=True, flush_mode="count", flush_count=100)

# Flush every 500ms
db = NanaSQLite("mydb.db", v2_mode=True, flush_mode="time", flush_interval=0.5)

# Manual flush
db = NanaSQLite("mydb.db", v2_mode=True, flush_mode="manual")
db["key"] = "value"
db.flush()  # Data is only persisted to disk here
```

---

## Dead Letter Queue (DLQ)

If a background SQL task fails (e.g., type violation, syntax error), it is isolated to the **Dead Letter Queue (DLQ)** instead of halting the entire system. This allows other data to continue being persisted.

Previously, accessing the DLQ required direct interaction with the internal engine. It is now accessible via public APIs.

The DLQ keeps up to 1000 entries by default. When the limit is reached, the oldest entry is evicted so the newest failure remains visible. Tune it with `V2Config(max_dlq_size=...)` or `NanaSQLite(..., v2_max_dlq_size=...)`; pass `None` for unbounded behavior.

```python
# Inspect DLQ contents
dlq_items = db.get_dlq()  # async: await db.aget_dlq()
for item in dlq_items:
    print(f"Task: {item['task']}, Error: {item['error']}")

# Retry after fixing the issue
db.retry_dlq()  # async: await db.aretry_dlq()

# Clear the DLQ
db.clear_dlq()  # async: await db.aclear_dlq()
```

---

## Metrics Collection (Monitoring)

If you need to monitor the engine's health (flush frequency, processing time, error counts, etc.), you can enable the metrics collection feature.

### Enabling Metrics
Set `v2_enable_metrics=True` when creating the instance. This setting is automatically inherited by child instances created via the `table()` method.

```python
db = NanaSQLite("mydb.db", v2_mode=True, v2_enable_metrics=True)
```

### Retrieving Statistics
Use the `get_v2_metrics()` method to fetch real-time statistics.

```python
stats = db.get_v2_metrics()  # async: await db.aget_v2_metrics()

print(f"Total Flushes: {stats['flush_count']}")
print(f"Total Items Flushed: {stats['kvs_items_flushed']}")
print(f"Total Flush Time: {stats['total_flush_time']:.4f}s")
print(f"Last Flush Duration: {stats['last_flush_time']:.4f}s")
print(f"DLQ Error Count: {stats['dlq_errors']}")
```

---

## Chunk Flushing

When flushing large batches, writes are automatically split into smaller chunks (default: 1000 items) to avoid holding SQLite locks for extended periods.

```python
# Adjust chunk size (default: 1000)
db = NanaSQLite("mydb.db", v2_mode=True, v2_chunk_size=500)
```

---

## Warnings and Limitations

> [!CAUTION]
> The v2 architecture is **single-process only**. Do NOT use it in:
>
> - `gunicorn --workers=N` (N > 1) with FastAPI/Flask
> - Applications using `multiprocessing` workers
> - Daemons using `fork`
> - Multiple processes using `memory_first=True` against the same database file

### Data Consistency
- In `manual` or `count` mode, if the process is killed forcibly, **buffered data will be lost**.
- In `memory_first=True`, changes since the last periodic flush may be lost.
- **IMPORTANT**: While the `atexit` handler automatically flushes data on normal process termination, it cannot protect against OS-level forced kills (`SIGKILL`) or power failures.
- For mission-critical data, it is recommended to call `db.flush(wait=True)` explicitly or use the default `immediate` mode.
- Always call `db.close()` on shutdown to flush any remaining buffer.

### Read Consistency

v2 mode is a **Write-Back Cache** design. Data written to the KVS is immediately readable from the in-memory cache, but may not yet be persisted to the SQLite file.

If another process reads the same SQLite file before the flush completes, it may see stale data.

---

## Checklist

- [ ] Is v2 mode only used in a single-process environment?
- [ ] Is the data-loss risk understood for `manual` / `count` modes?
- [ ] For `memory_first=True`, does the whole dataset fit in memory and can important boundaries call `flush(wait=True)`?
- [ ] Is `db.close()` or `atexit` guaranteed to be called in production?
- [ ] Has `v2_chunk_size` been tuned for large batch workloads?
