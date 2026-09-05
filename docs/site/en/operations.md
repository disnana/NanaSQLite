# Persistence diagnostics, admission limits and streaming

These APIs are available starting in v1.6.1. Existing settings remain the default.

## Persistence diagnostics

Use `db.get_status()` / `await db.aget_status()` without enabling metrics. Table children report the shared engine's state. Immediate mode has zero queue counts and `None` timestamps.

The result includes `mode`, `pending_kvs_count` (distinct staged keys), `flushing_kvs_count` (the in-flight batch), `pending_sql_count` (queued SQL, excluding running work), `oldest_pending_age_seconds` (queued work only, reset on retry), and `flush_active`. It also includes current `failed_count`, cumulative `failure_count`, cumulative `dropped_failure_count`, `last_failure_time`, and `last_successful_flush_time`. Timestamps are UNIX seconds. Empty queues have no age; an empty flush does not advance the last successful flush timestamp.

This is a best-effort diagnostic snapshot sampled under separate locks, not a durability barrier. An in-flight KVS batch can include already committed rows. Queue age collection traverses queued SQL tasks only when diagnostics are requested.

```python
from nanasqlite import NanaSQLite

with NanaSQLite("app.db", v2_mode=True, flush_mode="manual") as db:
    db["settings"] = {"theme": "dark"}
    db.flush(wait=True)
    if db.get_status()["failed_count"]:
        print(db.get_dlq_summary())
        # Resolve the underlying failure before retrying.
        db.retry_dlq()
        db.flush(wait=True)
```

`get_dlq_summary()` / `aget_dlq_summary()` returns only the fixed error code `write_failed` and timestamps. Raw exception text can disclose keys, SQL or values, so the existing engine summary now redacts it as well. Use existing `get_dlq()` only in a trusted context for details. Retrying or clearing the DLQ does not reset cumulative counters. Evicted failures cannot be retried. Retrying skips old failed KVS operations superseded by a newer write or deletion for the same table/key. This key-level protection does not apply to arbitrary SQL retries.

## Bound asynchronous submissions

```python
from nanasqlite import AsyncNanaSQLite

async def save():
    async with AsyncNanaSQLite(
        "app.db", max_workers=5,
        max_pending_operations=100, admission_timeout=2.0,
    ) as db:
        await db.aset("settings", {"theme": "dark"})
```

The optional limit covers running plus queued executor jobs and is shared by table children. Cache-only reads do not need a slot. The default `None` preserves unbounded admission. A positive `admission_timeout` raises `asyncio.TimeoutError` before submission; `None` waits for capacity. It does not limit SQL execution time.

Cancellation after submission does not undo a write or free capacity until the actual worker completes. Check the outcome before retrying a cancelled write. Closing rejects new work and drains accepted work even with the default unbounded admission. Cancellation of the caller awaiting `close()` does not cancel cleanup; await `close()` again to observe completion. Lazy initialization is also shielded and drained. If an open transaction prevents closing, roll it back or commit it before retrying `close()`.

This does not bound user-created waiting coroutines or the separate v2 write-back buffer. Process application input in bounded batches too.

## Stream persisted pairs

`db.iter_items(batch_size=256)` and `db.aiter_items(batch_size=256)` yield key/value pairs in key order with bounded keyset pages. Decryption and read hooks are applied without populating the cache. No cursor or connection lock survives a yield. Memory also depends on individual value sizes.

```python
with NanaSQLite("app.db") as db:
    for key, value in db.iter_items(256):
        process(key, value)  # Your application's consumer
```

Write-back modes flush first and reject unresolved DLQ entries. Iteration is not a whole-export snapshot: changes may affect later pages, and insertions behind the current key are omitted. Iterate a verified `backup()` database when a stable snapshot is needed.

## Automatic cache consistency

Set `cache_consistency="auto"` on sync or async constructors. The default `manual` retains explicit `refresh()`. Auto mode checks other-connection commits using [SQLite `PRAGMA data_version`](https://www.sqlite.org/pragma.html#pragma_data_version), plus shared-connection writes using `total_changes()` and transaction state. Changed versions invalidate positive and negative cache entries and hook indexes. Children inherit this option.

Checks and cache use share a lock. Transactional entries are not reused, protecting against rollback on another wrapper sharing the connection. This is freshness at a check, not snapshot isolation across reads or new cross-process atomicity for hook constraints.

Auto mode supports immediate persistence, including normal TTL/LRU caches and encryption. It rejects v2, memory-first and persistence TTL, avoiding conflicts with unsaved values and expiration management. Polling costs extra time, and own-connection writes also invalidate caches; retain manual mode for the fastest cached reads.
