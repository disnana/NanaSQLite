# V2 Architecture

NanaSQLite's V2 mode is an optional architecture that provides non-blocking writes for write-heavy workloads.

::: warning Limitation
V2 mode is designed for single-process use. Multi-process setups such as Gunicorn with multiple workers are not supported.
:::

## Overview

The V2 engine uses a **dual-lane** design:

```
Application
  │
  ├─ KVS Lane ──────→ Staging Buffer → Commit
  │   (dict ops)       (write coalescing)
  │
  └─ Strict Lane ───→ Priority Queue → Ordered Execution
      (SQL ops)        (FIFO)
```

- **KVS Lane**: Processes dict-like operations such as `db["key"] = value` at high speed. Writes to the same key are coalesced
- **Strict Lane**: Executes SQL operations like `sql_insert()` and `sql_update()` in order

## Enabling V2

```python
from nanasqlite import NanaSQLite

db = NanaSQLite(
    "app.db",
    v2_mode=True,           # Enable V2 engine
    flush_mode="immediate",  # Flush mode
)
```

## Flush Modes

The V2 engine writes data to the database in the background. Choose from four flush modes:

| Mode | Description | Data Safety | Performance |
|------|------------|-------------|-------------|
| `immediate` | Flush after every operation | ★★★★★ | ★★★ |
| `count` | Flush after N operations accumulate | ★★★★ | ★★★★ |
| `time` | Flush at regular time intervals | ★★★★ | ★★★★ |
| `manual` | Manual flush only | ★★★ | ★★★★★ |

### immediate (Default)

The safest mode. Every operation is guaranteed to be written to the database:

```python
db = NanaSQLite("app.db", v2_mode=True, flush_mode="immediate")
db["key"] = "value"  # Written to DB immediately
```

### count

Flush after a specified number of operations accumulate:

```python
db = NanaSQLite(
    "app.db",
    v2_mode=True,
    flush_mode="count",
    flush_count=100,  # Flush every 100 operations
)
```

### time

Flush at specified intervals:

```python
db = NanaSQLite(
    "app.db",
    v2_mode=True,
    flush_mode="time",
    flush_interval=3.0,  # Flush every 3 seconds
)
```

### manual

Full manual control:

```python
db = NanaSQLite("app.db", v2_mode=True, flush_mode="manual")

db["k1"] = "v1"
db["k2"] = "v2"
db["k3"] = "v3"

# Explicitly flush
db.flush()
```

::: danger Warning about manual mode
If the program exits without calling `flush()`, buffered data will be lost.
:::

## Chunk Size

For high-volume writes, adjust the chunk size to control transaction size:

```python
db = NanaSQLite(
    "app.db",
    v2_mode=True,
    v2_chunk_size=1000,  # 1000 operations per transaction
)
```

## Dead Letter Queue (DLQ)

Operations that fail to write are isolated in the **Dead Letter Queue**. This prevents errors from blocking subsequent operations.

### Inspecting the DLQ

```python
# Get DLQ contents
dlq = db.get_dlq()
for item in dlq:
    print(f"Failed operation: {item}")
```

### Retrying the DLQ

```python
# Retry failed operations
db.retry_dlq()
```

### Clearing the DLQ

```python
# Clear all entries in the DLQ
db.clear_dlq()
```

## Metrics Collection

The V2 engine can collect detailed metrics such as processing latency, flush counts, and DLQ tracking. This is an opt-in feature.

```python
db = NanaSQLite(
    "app.db",
    v2_mode=True,
    v2_enable_metrics=True,  # Enable metrics collection
)

# Get current metrics
metrics = db.get_v2_metrics()
print(f"Total Flushes: {metrics['total_flushes']}")
print(f"DLQ Count: {metrics['dlq_count']}")
```

## StrictTask

You can enqueue custom tasks into the Strict lane:

```python
from nanasqlite.v2_engine import StrictTask

# Enqueue a task with priority
task = StrictTask(
    priority=1,
    sequence_id=0,
    task_type="sql",
    sql="INSERT INTO logs (message) VALUES (?)",
    parameters=["Important event"],
    on_success=lambda: print("Success"),
    on_error=lambda e: print(f"Failed: {e}"),
)
db._v2_engine.enqueue_strict_task(task)
```

## V2 Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `v2_mode` | `bool` | `False` | Enable V2 engine |
| `flush_mode` | `str` | `"immediate"` | Flush mode |
| `flush_interval` | `float` | `3.0` | Interval for time mode (seconds) |
| `flush_count` | `int` | `100` | Threshold for count mode |
| `v2_chunk_size` | `int` | `1000` | Transaction chunk size |
| `v2_enable_metrics` | `bool` | `False` | Enable detailed metrics collection |

## Async V2 Usage

V2 mode also works with `AsyncNanaSQLite`:

```python
from nanasqlite import AsyncNanaSQLite

async def main():
    db = AsyncNanaSQLite(
        "app.db",
        v2_mode=True,
        flush_mode="time",
        flush_interval=5.0,
    )

    await db.aset("key", "value")
    await db.aflush()

    dlq = await db.aget_dlq()

    db.close()
```

## V1 vs V2 Comparison

| Aspect | V1 (Default) | V2 |
|--------|-------------|-----|
| Writes | Synchronous, blocking | Non-blocking (buffered) |
| Reads | Cache → DB | Cache → Buffer → DB |
| Data safety | Immediate guarantee | Depends on flush mode |
| Write performance | Baseline | High throughput |
| Complexity | Simple | Requires DLQ and flush management |
| Processes | Multi-process capable | Single-process only |

## When to Use V2

**V2 is suitable for:**
- Write-heavy applications (logging, sensor data, chat)
- Minimizing write latency
- Single-process applications

**Stick with V1 when:**
- Immediate data persistence is required
- Running in a multi-process environment (e.g., Gunicorn workers)
- Simple CRUD applications
