---
outline: [2, 3]
---

# Changelog

### [1.5.3rc3] - 2026-04-07

#### Performance Improvements

- **PERF-21: `execute_many()` — Python loop → `cursor.executemany()`** (`core.py`)
  - Eliminates per-item Python function-call overhead. ~15% improvement for `test_execute_many` and `test_import_from_dict_list`.

- **PERF-22: `batch_delete()` — skip pre-check loop when no hooks** (`core.py`)
  - When `_has_hooks=False` (default), the full `_ensure_cached()` loop over all keys is skipped entirely.

- **PERF-23: `batch_update()` — serialize outside lock, `dict.update()`, `_absent_keys` guard** (`core.py`)
  - Serialization moved outside the lock. Cache update uses `dict.update()` (~6× faster than a per-key loop). `_absent_keys` update guarded and batched with `difference_update()`. ~9% overall improvement.

- **PERF-24: `batch_update_partial()` — `dict.update()` + `_absent_keys` guard** (`core.py`)
  - Same optimizations as PERF-23 applied to both v1 and v2 paths.

- **PERF-25: `batch_delete()` — `_absent_keys.update(keys)` bulk call** (`core.py`)
  - Per-key `add()` loop replaced with a single `update(keys)` call.

- **PERF-26: `begin_transaction()` / `commit()` / `rollback()` — bypass `execute()` overhead** (`core.py`)
  - Call `self._connection.execute()` directly under the lock, skipping v2-mode dispatch, SQL `strip().upper()`, and redundant `_check_connection()`.

- **PERF-29: `_serialize()` — early return for no-encryption case** (`core.py`)
  - `_no_encrypt` bool flag pre-computed in `__init__`. Eliminates `_fernet`/`_aead` attribute lookups on every write when encryption is disabled.

---

### [1.5.3rc2] - 2026-04-07

#### Bug Fixes

- **[Medium] BUG-01: `setdefault()` returns wrong value when `before_write` hook transforms the default** (`core.py`)
  - With `ValidkitHook(coerce=True)` or `PydanticHook`, PERF-18 was applying `after_read` to the original `default` rather than the stored (transformed) value. Fixed by reading from cache when `_has_hooks` is True.

#### Performance Fixes (v1.5.3rc2 benchmark regression fix)

- **[High] PERF-14/15/16: try/except fast path for Unbounded mode read hot paths** (`core.py`)
  - Replaced `.get(key, sentinel)` with direct `d[key]` + `try/except` in `__getitem__`, `get()`, and `__contains__`. Approximately **1.9x** faster for the cache-hit case. Measured **-15%** on `test_single_read_cached`.

- **[Medium] PERF-17: Guard empty `_absent_keys.discard()` in `_update_cache()`** (`core.py`)
  - Added `if self._absent_keys:` guard to skip unnecessary hash computation in write-heavy workloads.

- **[Medium] PERF-18: Eliminate redundant `self[key]` in `setdefault()`** (`core.py`)
  - Return the default value directly after writing instead of re-entering `__getitem__`.

- **[Medium] PERF-19: Direct `_data` access in `pop()` for Unbounded mode** (`core.py`)
  - Use `self._data[key]` instead of `self._cache.get()` to avoid polymorphic method dispatch.

- **[Medium] PERF-20: Pre-computed `_has_hooks` flag** (`core.py`)
  - Replace `if self._hooks:` with a pre-computed `bool` flag `_has_hooks` across all KV hot paths, eliminating `list.__len__` overhead on every operation.

### [1.5.3rc1] - 2026-04-07

#### Performance Fixes (v1.5.3 pre-release audit)

- **[High] PERF-07: Pre-compute common SQL strings at `__init__`** (`core.py`)
  - All KV hot paths were rebuilding the same table-qualified SQL via f-strings on every call. Six SQL template strings are now pre-computed once at init time and stored as instance attributes.
  - **Impact**: Eliminates string-construction overhead from all KV operations (write, read, delete, contains, count).

- **[Medium] PERF-08: Skip MISSING filter in `to_dict()` / `copy()` for Unbounded mode** (`core.py`)
  - MISSING is never stored in Unbounded `_data`, so `dict(self._data)` is returned directly without a per-element predicate.
  - **Impact**: Improves `test_to_dict_1000` / `test_copy`.

- **[Medium] PERF-09: Eliminate double cache lookup in LRU/TTL `__getitem__`** (`core.py`)
  - Restructured to check `_data` membership first, then one `cache.get()` call — eliminating a redundant `move_to_end()` on every cache hit.
  - **Impact**: Reduces cache-hit overhead for LRU/TTL `__getitem__`.

- **[Medium] PERF-10: Regex consolidation and function-scan skip in `_validate_expression()`** (`core.py`)
  - Four separate `re.search()` calls replaced by one pre-compiled module-level `_DANGEROUS_SQL_RE`. Expressions with no `(` skip the function-scan entirely.
  - **Note**: In non-strict mode, multiple dangerous patterns in one expression now emit a single `UserWarning` instead of one per pattern. Strict mode (exception) behavior unchanged.

- **[Medium] PERF-11: Lock-free fast path in `ExpiringDict._check_expiry()`** (`utils.py`)
  - Adds an optimistic lock-free pre-check for live keys, skipping the `RLock` acquire/release for the common non-expired case.
  - **Impact**: Reduces lock acquisitions on TTL cache hit paths.

- **[High] PERF-12: Eliminate double cache lookup in LRU/TTL `get()`** (`core.py`) *(found by v1.5.3 audit)*
  - Applied the same fix as PERF-09 to `get()`, which had the same double-lookup issue.

- **[Medium] PERF-13: Skip MISSING filter in `values()` / `items()` for Unbounded mode** (`core.py`) *(found by v1.5.3 audit)*
  - Applied the same PERF-08 optimisation to `values()` and `items()`.

#### Tests

- Added `tests/test_v153_perf_fixes.py` (19 regression tests covering PERF-07 through PERF-11).
- Added `TestPerf12GetDoubleLookup` / `TestPerf13ValuesItemsFilter` to `tests/test_audit_poc.py`.

### [1.5.2] - 2026-04-06

#### Performance Fixes (Follow-up for regression since v1.5.0dev1)

- **[High] PERF-06: Fast-path optimization for Unbounded cache reads** (`core.py`)
  - In Unbounded mode, read-heavy paths (`__getitem__`, `get`, `__contains__`, `_ensure_cached`) still had extra branching before the `_data` check on hot read paths, adding avoidable membership checks even for positive cache hits.
  - Reorganized the path to prioritize `_data` lookup first and use `_absent_keys` only for known-absent fast return.
  - **Impact**: Lower overhead for cached reads and contains checks while preserving existing behavior.

#### Breaking Change (approved)

- In Unbounded mode, internal mixed-state metadata was split from `_cached_keys` to `_absent_keys` (known-absent only).
  - No public API change, but code depending on internal `_cached_keys` semantics is not compatible.
  - Migration: use public APIs (`in`, `get`, `is_cached`) instead of internal metadata fields.

#### Tests

- Added `tests/test_v152_perf_fastpath.py` to verify the `_data`-first fast-path and preserved negative-cache semantics.

### [1.5.1] - 2026-04-05

#### Security Fixes (v1.5.1 Pre-Release Audit)

- **[Medium] SEC-01: Apply `_validate_expression()` to `exists()` WHERE clause** (`core.py`)
  - `query()` / `count()` / `query_with_pagination()` all validate the WHERE clause through `_validate_expression()`, enforcing `forbidden_sql_functions` and `strict_sql_validation` policies. `exists()` skipped this validation, allowing a forbidden function to be used in its WHERE clause while being rejected by all other query methods — an inconsistency that undermined application-level SQL policy enforcement. Fixed by adding `_validate_expression(where, context="where")` to `exists()`.

- **[Medium] SEC-02: Apply `_validate_expression()` to `sql_update()` / `sql_delete()` WHERE clause** (`core.py`)
  - Same as SEC-01: `sql_update()` and `sql_delete()` did not validate their WHERE clause, so `strict_sql_validation` / `forbidden_sql_functions` settings had no effect on these methods. Fixed with `_validate_expression(where, context="where")` in both methods.

#### Bug Fixes (v1.5.1 Pre-Release Audit)

- **[High] BUG-01: Fix `pop()` bypassing v2 engine staging buffer** (`core.py`)
  - In v2 mode, `pop()` called `_delete_from_db()` directly instead of routing through `v2_engine.kvs_delete()`. If the key had a pending SET in the staging buffer (not yet flushed), the direct DB DELETE was a no-op (key not in DB yet), but the staging SET was left intact. On the next `flush()`, the SET was applied to the DB, resurrecting the deleted key. Fixed by routing v2-mode `pop()` through `v2_engine.kvs_delete()`, matching `__delitem__`.

- **[Medium] BUG-02: Fix `batch_get()` ignoring `_cached_keys` "known absent" status** (`core.py`)
  - After `__delitem__`, the key is recorded as "known absent" in `_cached_keys` but removed from `_data`. `get()` (via `_ensure_cached`) correctly honours this and returns the default. `batch_get()` only checked `_data`, so a cache miss caused it to fall through to a DB query — in v2 non-immediate mode, the pending delete may not yet be in DB, so `batch_get()` would return the stale old value while `get()` returned absent. Fixed by checking `_cached_keys` in `batch_get()`'s cache-miss path.

- **[Low] BUG-03: Fix `to_dict()` returning `MISSING` sentinel in LRU/TTL mode** (`core.py`)
  - In LRU/TTL cache mode, lookups for non-existent keys write the `MISSING` sentinel into the cache as a negative entry. `to_dict()` returned `dict(self._data)` which included these sentinel values, unlike `items()` which correctly filtered them. Fixed by using a dict comprehension with `if v is not MISSING`.

#### Performance Improvements (v1.5.1 Pre-Release Audit)

- **[Low] PERF-05: Pre-compute `_SAFE_SQL_CHARS` as a module-level `frozenset`** (`sql_utils.py`)
  - `fast_validate_sql_chars()` re-created a `set(...)` object on every call. Because this function is called on every `_validate_expression()` invocation (hot path for all query methods), building the same immutable set repeatedly wasted ~200–300 ns per call. Moved to a module-level `frozenset` constant `_SAFE_SQL_CHARS` computed once at import time.

#### Performance Fixes (Regression since v1.5.0dev1)

Fixed performance regressions observed in RPI benchmarks that appeared starting from v1.5.0dev1.

- **[Critical] PERF-01: Remove hook hot-path overhead** (`core.py`)
  - All read/write operations (`__getitem__`, `__setitem__`, `__delitem__`, `get`, `batch_get`, `setdefault`, `pop`, `batch_update_partial`, `batch_delete`) were calling `getattr(self, "_hooks", [])` on every invocation, causing measurable overhead even when no hooks are registered. Changed to direct `self._hooks` access (always initialized) with an `if self._hooks:` early-exit guard.
  - **Impact**: ~30% throughput improvement for cached reads (RPI: ~1.74M → ~2.3M ops/sec equivalent).

- **[Critical] PERF-02: Eliminate shared-lock contention in v2 mode** (`core.py`)
  - In the v2-mode paths of `__setitem__`, `__delitem__`, `batch_update`, and `batch_delete`, the in-memory cache update (`_data[key] = value`, etc.) was being wrapped in the same lock used by the background flush thread for database transactions. On slow CPUs (Raspberry Pi and similar ARM devices) this caused severe throughput degradation because the main thread and background flush thread constantly competed for the same lock.
  - In v2 mode, in-memory-only updates are atomic under Python's GIL, and the background flush thread never accesses `_data` or `_cached_keys` directly, so no explicit lock is required for these operations.
  - **Impact**: ~3.7× throughput improvement for v2 immediate-mode writes (RPI: ~169 → ~600+ calls/sec equivalent).

- **[Medium] PERF-03: Pre-compute `_update_cache` dispatch flag** (`core.py`)
  - `_update_cache()` called `hasattr(self._cache, "_max_size")` on every invocation, adding unnecessary overhead on the write hot path. The result is now pre-computed as `_use_cache_set` during `__init__`, eliminating the `hasattr()` call entirely.
  - **Impact**: ~2-3% write throughput improvement.

- **[Medium] PERF-04: Replace `@contextmanager` with direct RLock return in `_acquire_lock()`** (`core.py`)
  - `_acquire_lock()` used a `@contextmanager` generator, incurring `contextlib` overhead (object allocation, `next()` calls) on every lock acquisition. For the common case (no timeout), the method now returns `self._lock` (a `threading.RLock`) directly — `RLock` is itself a context manager with highly-optimised C-level `__enter__`/`__exit__`. When `lock_timeout` is set, a lightweight `_TimedLockContext` helper is returned instead.
  - **Impact**: ~7% write throughput improvement for non-v2 paths.

### [1.5.0] - 2026-04-04

#### Security Fixes (v1.5.0 Pre-Release Audit)

- **[Critical] SEC-03**: Documented and added warnings for the TOCTOU (Time-of-check/Time-of-use) race condition in `UniqueHook`. The uniqueness check occurs outside the database write transaction, meaning multiple threads can bypass the constraint in concurrent environments. Class docstring now clearly warns against this and recommends using SQLite native `UNIQUE` constraints or application-level exclusive locks.
- **[Critical] SEC-04**: Similarly documented and added warnings for the TOCTOU race condition in `ForeignKeyHook`, where a referenced key can be deleted between the constraint check and the write operation. Class docstring recommends `PRAGMA foreign_keys=ON` for strict referential integrity.
- **[High] SEC-05**: Fixed a ReDoS (Regular Expression Denial of Service) vulnerability in `BaseHook`'s `key_pattern` regex parameter. Malicious regex patterns could cause excessive CPU load. Pattern validation is now enforced at construction time.
- **[High] SEC-06**: Fixed information leakage in hook constraint violation error messages that exposed field names and values. Error messages are now generic, with detailed information logged server-side only.

#### Bug Fixes (v1.5.0 Pre-Release Audit)

- **[Critical] BUG-05**: Fixed `PydanticHook` silently converting all exceptions to `ValidationError`. System-level errors such as `ConnectionError` and `MemoryError` are now properly re-raised.
- **[High] BUG-06**: Fixed unnecessary dictionary copying in hook processing when no values were actually changed. Introduced change detection to allocate new dicts only when values are actually modified (improves memory efficiency in batch operations).

#### Code Quality Fixes (PR Review Follow-up)

- **[Low] BANDIT-B110**: Replaced empty `try/except/pass` around `atexit.unregister` in `v2_engine.py` with `contextlib.suppress(Exception)` to resolve the Bandit B110 warning.
- **[Low] POC Cleanup**: Fixed all CodeQL and Bandit warnings raised in POC scripts (unused imports, unused variables, bare `except`, and hard-coded ReDoS pattern literals). Removed duplicate `import sqlite3` in test file.

#### Packaging and IDE Support Improvements

- **[High] PEP 561 Compliance and Autocompletion Fix**:
  - Refactored `tool.setuptools` in `pyproject.toml` to use standard `src-layout` auto-discovery. Fixed the issue where IntelliSense/autocompletion failed for the PyPI distribution.
  - Enabled `include-package-data = true` and added `MANIFEST.in` to ensure the `py.typed` file is correctly bundled in both wheel (.whl) and source distributions (sdist).
  - This enables full autocompletion support for `NanaSQLite`, `PydanticHook`, and other exports in major IDEs like VS Code (Pylance) and PyCharm out of the box.

#### Improvements from Release Audit

- **[Critical] BUG-01**: Fixed a bug where `batch_update`, `batch_update_partial`, and `batch_delete` methods bypassed V2 mode and performed direct database writes. Routed these operations through the V2 engine's staging buffer to ensure data integrity and FIFO order.
- **[Critical] BUG-02**: Resolved "Ghost Re-inserts" in `clear()` and `load_all()` methods, where database operations executed before the V2 engine's background `flush()` completed. Introduced synchronous waiting via `flush(wait=True)`.
- **[High] QUAL-01**: Refactored `AsyncNanaSQLite.add_hook()` implementation to harden hook registration logic before and after base database initialization, improving stability in asynchronous environments.
- **[Non-Breaking] API Extension**: Added a `wait` parameter to `flush()` (sync) and `aflush()` (async) methods, allowing for synchronous waiting of background worker completion.
- **[High] Full Restoration of Python 3.9 Compatibility**:
  - Added `from __future__ import annotations` to all source files, allowing Python 3.10+ `|` (Union) operators in type hints to function correctly on Python 3.9.
  - Introduced an `EllipsisType` compatibility layer in `compat.py` to ensure stable `mypy` static analysis and runtime type validation on Python 3.9.
  - Updated `pyproject.toml` to target `mypy` for Python 3.9, guaranteeing continuous compatibility.

#### New Features: Ultimate Hooks (General-purpose Hook & Constraint Architecture)

- **Powerful Hook Mechanism**:
  - Introduced the `NanaHook` protocol, allowing interception of 3 lifecycle events: `before_write`, `after_read`, and `before_delete`.
  - Custom hooks can be easily authored to implement data validation, custom encryption, logging, or integrations with external systems.
- **Built-in Standard Constraints**:
  - `CheckHook`: Provides function-based validation similar to SQLite's `CHECK` constraint.
  - `UniqueHook`: Ensures uniqueness of values for a specified key or nested field (TOCTOU warning applies, see SEC-03).
  - `ForeignKeyHook`: Grants referential integrity against keys in other `NanaSQLite` tables (TOCTOU warning applies, see SEC-04).
- **Transparent External Library Integrations**:
  - `ValidkitHook`: Maintains 100% backward compatibility with the legacy `validator` parameter, providing high-performance validation via `validkit-py`.
  - `PydanticHook`: Allows direct registration of `Pydantic` models as hooks, enabling automatic serialization/deserialization and strict type validation on read/write.
- **Method Extensions**:
  - Added `NanaSQLite.add_hook()` and `AsyncNanaSQLite.add_hook()` for dynamic hook registration.

#### Architectural Enhancements & Backward Compatibility

- The legacy `validator` parameter is internally converted to a `ValidkitHook`, preserving 100% backward compatibility.
- Internal logic has been unified and hardened to ensure hooks are equally applied across all access paths, including `batch_update`, `get`, `batch_get`, `setdefault`, and `pop`.

#### Audit & Testing

- Updated pre-release audit report (`audit.md`) — documented 12 findings for v1.5.0.
- Added 5 POC scripts to `etc/poc/`.
- Added 14 POC verification tests to `tests/test_audit_poc.py`.

### [1.5.0dev2] - 2026-03-28 *(released — consolidated into v1.5.0)*

#### Packaging and IDE Support Improvements
- **[High] PEP 561 Compliance and Autocompletion Fix**:
  - Refactored `tool.setuptools` in `pyproject.toml` to use standard `src-layout` auto-discovery. Fixed the issue where IntelliSense/autocompletion failed for the PyPI distribution.
  - Enabled `include-package-data = true` and added `MANIFEST.in` to ensure the `py.typed` file is correctly bundled in both wheel (.whl) and source distributions (sdist).
  - This enables full autocompletion support for `NanaSQLite`, `PydanticHook`, and other exports in major IDEs like VS Code (Pylance) and PyCharm out of the box.

### [1.5.0dev1] - 2026-03-28

#### Improvements from Release Audit
- **[Critical] BUG-01**: Fixed a bug where `batch_update`, `batch_update_partial`, and `batch_delete` methods bypassed V2 mode and performed direct database writes. Routed these operations through the V2 engine's staging buffer to ensure data integrity and FIFO order.
- **[Critical] BUG-02**: Resolved "Ghost Re-inserts" in `clear()` and `load_all()` methods, where database operations executed before the V2 engine's background `flush()` completed. Introduced synchronous waiting via `flush(wait=True)`.
- **[High] QUAL-01**: Refactored `AsyncNanaSQLite.add_hook()` implementation to harden hook registration logic before and after base database initialization, improving stability in asynchronous environments.
- **[Non-Breaking] API Extension**: Added a `wait` parameter to `flush()` (sync) and `aflush()` (async) methods, allowing for synchronous waiting of background worker completion.
- **[High] Full Restoration of Python 3.9 Compatibility**:
  - Added `from __future__ import annotations` to all source files, allowing Python 3.10+ `|` (Union) operators in type hints to function correctly on Python 3.9.
  - Introduced an `EllipsisType` compatibility layer in `compat.py` to ensure stable `mypy` static analysis and runtime type validation on Python 3.9.
  - Updated `pyproject.toml` to target `mypy` for Python 3.9, guaranteeing continuous compatibility.

#### New Features: Ultimate Hooks (General-purpose Hook & Constraint Architecture)
- **Powerful Hook Mechanism**:
  - Introduced the `NanaHook` protocol, allowing interception of 3 lifecycle events: `before_write`, `after_read`, and `before_delete`.
  - Custom hooks can be easily authored to implement data validation, custom encryption, logging, or integrations with external systems.
- **Built-in Standard Constraints**:
  - `CheckHook`: Provides function-based validation similar to SQLite's `CHECK` constraint.
  - `UniqueHook`: Ensures uniqueness of values for a specified key (or nested field).
  - `ForeignKeyHook`: Grants referential integrity against keys in other `NanaSQLite` tables.
- **Transparent External Library Integrations**:
  - `ValidkitHook`: Maintains 100% backward compatibility with the legacy `validator` parameter, providing high-performance validation via `validkit-py`.
  - `PydanticHook`: Allows direct registration of `Pydantic` models as hooks, enabling automatic serialization/deserialization and strict type validation on read/write.
- **Method Extensions**:
  - Added `NanaSQLite.add_hook()` and `AsyncNanaSQLite.add_hook()` for dynamic hook registration.

#### Architectural Enhancements & Backward Compatibility
- The legacy `validator` parameter is internally converted to a `ValidkitHook`, preserving 100% backward compatibility.
- Internal logic has been unified and hardened to ensure hooks are equally applied across all access paths, including `batch_update`, `get`, `batch_get`, `setdefault`, and `pop`.

### [1.4.1] - 2026-03-25

#### Security Fixes
- **[Medium] SEC-02**: Fixed the `column_type` validation regular expression in `core.py` from a vulnerable pattern (`[\w ]*`) to a safe pattern, completely resolving the ReDoS (Regular Expression Denial of Service) vulnerability warned by SonarQube.

#### Bug Fixes
- **[High] BUG-01**: Fixed `AttributeError` in `upsert()` and `aupsert()` when passing a data dictionary as the first argument while specifying `conflict_columns`. Improved internal logic to reference the correct keys in `target_data`. (1.4.1rc1)
- **[High] QUAL-02**: Fixed a potential race condition in `AsyncNanaSQLite` initialization where multiple concurrent async tasks could trigger redundant background initializations. Introduced `asyncio.Lock` to ensure thread-safe startup.
- Resolved syntax errors and initialization issues in `AsyncNanaSQLite.table()` caused by docstring fragmentation and incomplete argument propagation. (1.4.1dev3)
- Cleaned up duplicate method definitions in `AsyncNanaSQLite` that occurred during feature application. (1.4.1dev3)

#### Critical Fixes from Deep Audit
- **[Critical] BUG-02**: Resolved a "Stale Read" inconsistency in V2 mode where reading data via `get()` or `__getitem__` immediately after a write could return outdated values. Optimized the read path to prioritize the background staging buffer.
- **[Critical] QUAL-04**: Fixed a crash in `AsyncNanaSQLite` when instantiated outside an event loop due to unsafe `asyncio.Lock()` initialization in `__init__`. Implemented lazy initialization for the lock within the event loop context.
- **[Critical] LOCK-01**: Resolved a deadlock scenario in `ExpiringDict` where the TTL expiration callback (`on_expire`) was executed while holding the DB lock, conflicting with concurrent write operations. Callbacks are now executed outside the locking scope.
- **[Critical] CONC-01**: Fixed potential `RuntimeError`, cache corruption, and TOCTOU races in multi-threaded environments (e.g., `AsyncNanaSQLite`) by moving internal cache mutations into the scope of the database lock.
- **[Critical] CONC-02**: Resolved a crash when using `table()` in V2 mode where multiple background engines sharing the same SQLite connection would attempt to start overlapping transactions. Implemented `shared_lock` propagation across parent/child V2 engines.
- **[Critical] ASYNC-01**: Implemented missing V2 management methods (`aflush`, `aget_dlq`, `aretry_dlq`, `aclear_dlq`, `aget_v2_metrics`) in `AsyncNanaSQLite`.
- **[High] QUAL-05**: Added guards to forbid explicit transaction operations (`begin_transaction`, etc.) in V2 mode, preventing fatal conflicts with the engine's automated background flushing.
- **[High] QUAL-06**: Fixed a bug where `v2_enable_metrics` setting was not inherited by child instances in `AsyncNanaSQLite.table()`.
- **[Medium] SEC-01 (Hardened)**: Upgraded `create_table()` column type validation from a blacklist approach to a strict whitelist-based regular expression for enhanced security.
- **[Medium] SEC-02**: Resolved a sonar-reported ReDoS vulnerability in `core.py` by replacing the loose `[\w ]*` regex with a safe pattern for column type validation.

#### Performance Improvements
- **[Low] PERF-01**: Introduced "negative caching" for LRU and TTL cache strategies to store the result of searches for keys that do not exist in the database, reducing I/O load during repeated access. (Also discovered and fixed a breaking bug before release where internal sentinels could leak due to this feature). (1.4.1rc1)

#### Code Quality Improvements
- **[Low] QUAL-01**: Improved the `ExpiringDict` scheduler thread stop logic to ensure more robust cleanup during instance destruction or clearing. (1.4.1rc1)
- **[Low] QUAL-03**: Deduplicated magic literals (e.g., `"BEGIN IMMEDIATE"`) into module-level constants to improve maintainability.
- **[Low] CI-01**: Resolved SonarQube Cloud "Quality Gate" false positives by excluding non-source files (docs, scripts) from coverage and suppressing non-essential maintainability warnings through configuration.

#### New Features: Enhanced V2 Engine Usability and Observability (Opt-in)
- **Dead Letter Queue (DLQ) Visibility**:
    - Added `get_dlq()`, `retry_dlq()`, and `clear_dlq()` methods to both synchronous and asynchronous (`a*`) interfaces.
    - Allows direct inspection, manual retry, or clearing of background operation errors.
- **Metrics Collection**:
    - Introduced a `v2_enable_metrics` parameter to enable detailed engine statistics collection.
    - `get_v2_metrics()` provides metrics such as total flush count, processing time, and DLQ error counts.
- **Configuration Inheritance**:
    - Ensured that V2-specific settings like `v2_enable_metrics` are correctly propagated to child instances created via the `table()` method.

#### Documentation
- **Enhanced API Documentation Generator**: Overhauled `scripts/gen_api_docs.py` to produce modern, highly readable API references utilizing VitePress tables and custom containers.
- **Site-wide Documentation Modernization**: Standardized all manual documentation by batch-converting callouts and warnings to the VitePress native format.

### [1.4.0] - 2026-03-12

#### Security Fixes
- **[Critical] SEC-01**: Fixed SQL injection vulnerability in `create_table()` column type definitions. APSW executes all semicolon-separated statements, allowing arbitrary SQL execution through crafted column type strings. Added validation that rejects column types containing `;`, `--`, or `/*`.

#### Bug Fixes
- **[High] BUG-01**: Fixed V2Engine `_process_strict_queue()` calling `on_success` callbacks before transaction COMMIT. If a later task failed and caused a ROLLBACK, earlier callers would receive false success notifications. Callbacks are now deferred until after COMMIT succeeds.
- **[Medium] BUG-02**: Fixed `AsyncNanaSQLite.table()` child instances missing `_v2_mode`, `_cache_strategy`, `_encryption_key` and other attributes, causing `AttributeError`. All parent settings are now properly inherited.
- **[Medium] BUG-03**: Fixed v2 mode `execute()` returning empty results for SELECT/PRAGMA/EXPLAIN queries. Read queries now bypass the background queue and execute directly.

#### Code Quality Improvements
- **[Low] BUG-04**: Replaced duplicated alias extraction logic in `_shared_query_impl()` with a call to `NanaSQLite._extract_column_aliases()`.
- **[Low] QUAL-01**: Fixed `update()` method type annotation from `dict` to `dict | None`.

### [1.4.0dev2] - 2026-03-12

#### Improvements: Async API Completion
- Implemented and exposed all key methods in `AsyncNanaSQLite` as asynchronous versions (`abackup`, `arestore`, `apragma`, `aget_table_schema`, `alist_indexes`, `aalter_table_add_column`, `aupsert`, `aget_dlq`, `aretry_dlq`, etc.) to achieve full feature parity with the synchronous version.

#### Changes: Unified and Enhanced upsert() Method
- Unified the `upsert()` method signature to support both `(table_name, data_dict, conflict_columns)` and `(key, value)` patterns in a single method.
- When `v2_mode` is enabled, the `(key, value)` pattern is automatically routed to the background persistence queue.

#### Testing: Expanded Benchmark Coverage
- Increased benchmark tests from 158 to **177**.
- Added coverage for previously unmeasured operations: `backup`, `restore`, `pragma`, `DDL (alter table/index)`, `export/import`, etc.
- Significantly enhanced asynchronous benchmarks (`tests/test_async_benchmark.py`).

#### Fixes
- Fixed `get_table_schema` to accept an optional `table_name` argument (defaulting to the current table) and handle cases where the `table` property is missing.
- Resolved all project-wide `ruff` linting errors (31 items) and `mypy` type check issues.

### [1.4.0dev1] - 2026-03-12

#### New Features: v2 Architecture (Optional)
- **Non-blocking Background Persistence**:
  - Enable the v2 architecture by passing `v2_mode=True` to `NanaSQLite`.
  - All write operations (KVS updates and explicit SQL execution) are temporarily buffered in memory or queued, and then flushed to SQLite asynchronously by a background thread.
  - This eliminates disk I/O blocking on the main thread entirely, dramatically improving write latency.
  - Read latency remains zero-cost as data is still fetched directly from the in-memory cache.
  - **Flush Modes**: Customize flushing behavior using the `flush_mode` parameter (`immediate`, `count`, `time`, or `manual`).
  - **Dead Letter Queue (DLQ)**: If a background SQL execution fails, the problematic task is isolated to a DLQ, allowing the rest of the data persistence pipeline to proceed without halting the system. Use `get_dlq()` to inspect and `retry_dlq()` to re-enqueue failed tasks.
  - **Chunk Flushing**: Automatically splits large write batches (default: 1000 items) to prevent long-held database locks.
  - **Warning**: The v2 architecture is designed exclusively for SINGLE-PROCESS systems. A warning is emitted if used in multi-process environments (e.g., Gunicorn with multiple workers) as parallel background threads will cause data corruption.

#### Changes
- Added `v2_mode`, `flush_mode`, `flush_interval`, `flush_count`, and `v2_chunk_size` parameters to `NanaSQLite` and `AsyncNanaSQLite` initialization.
- Added explicit `flush()` (sync) and `aflush()` (async) methods.
- Added `get_dlq()` and `retry_dlq()` methods to `V2Engine` for DLQ management.

#### Fixes
- Fixed a race condition when accessing the Dead Letter Queue (DLQ) concurrently in the v2 engine.
- Fixed a bug where strict queue tasks were not processed if the KVS staging buffer was empty.

### [1.3.4] - 2026-03-10

#### Security Fixes

- **SEC-01 [High]**: Switched `alter_table_add_column()` `column_type` validation from blacklist to whitelist regex. Reliably blocks injection payloads like `TEXT; DROP TABLE`.
- **SEC-02 [High]**: Fixed `sanitize_sql_for_function_scan()` to preserve double-quoted SQL identifier content. `_validate_expression()` now correctly detects quoted function name bypasses like `"LOAD_EXTENSION"()`.

#### Bug Fixes

- **BUG-01 [Critical]**: Added `_check_connection()` check to `items()`. Calling on a closed instance now raises `NanaSQLiteClosedError` instead of leaking a low-level APSW exception.
- **BUG-02 [High]**: AEAD deserialization now logs a warning instead of silently falling back to plaintext JSON when receiving non-bytes values.
- **BUG-03 [High]**: Added payload length validation (≥28 bytes = 12-byte nonce + 16-byte auth tag) before AEAD decrypt. Short data now raises a clear `NanaSQLiteDatabaseError`. `InvalidTag` and other low-level crypto exceptions are also wrapped into `NanaSQLiteDatabaseError`.
- **BUG-04 [High]**: Removed redundant double `_ensure_initialized()` call in `AsyncNanaSQLite.acontains()`.
- **BUG-05 [Medium]**: Added `offset` type and non-negative validation in async `_shared_query_impl()`.
- **BUG-06 [Medium]**: Fixed `parameters: tuple = None` → `tuple | None = None` type annotations in `async_core.py` (mypy strict compliance).
- **BUG-07 [Medium]**: `ExpiringDict` scheduler now processes all expired keys per iteration instead of just one.
- **BUG-09 [Medium]**: `batch_get()` now correctly includes keys with explicit `None` values in results.
- **BUG-10 [Low]**: Reuse compiled `IDENTIFIER_PATTERN` in `_sanitize_identifier()`.
- **BUG-12 [Low]**: Fixed `NanaSQLiteDatabaseError.__init__` `original_error` type annotation to `Exception | None`.

#### Performance Improvements

- **PERF-03 [Medium]**: Extracted `_extract_column_aliases()` helper, deduplicating column-alias extraction from 3 call sites.

#### Code Quality

- **QUAL-01 [Medium]**: Fixed `_get_all_keys_from_db()` return type to `list[str]`.
- **QUAL-03 [Medium]**: Harmonized column-name quote stripping between `query()` and `query_with_pagination()`.

#### Audit & Testing

- Added pre-release audit report (`audit.md`) — 35 findings documented.
- Added 6 POC scripts in `etc/poc/`.
- Added 20 POC verification tests in `tests/test_audit_poc.py`.
- Updated `audit_prompt.md` to 6-phase workflow (audit → POC → patch → pytest → CI verification → release preparation).

### [1.3.4rc4] - 2026-03-08

#### CI Fixes

- **Least-privilege cleanup for the provenance job** (PR [#127](https://github.com/disnana/NanaSQLite/pull/127)):
  - Downgraded `contents: write` to `contents: read` in the `provenance` job; write access was only needed for `upload-assets`, which was already removed.
  - Removed the dead `upload-assets: true` option — this workflow has no tag-based trigger, so the SLSA generator would always skip it.
  - Provenance is still attached to GitHub Releases by the `release` job as before.
  - Added inline comments explaining the two expected CI annotations (`go.sum not found` warning and PyPI attestation notice) to prevent confusion.
  - Synced `CHANGELOG.md` from the latest `main` branch.

### [1.3.4rc3] - 2026-03-08

#### CI Fixes

- **Restored and hardened the SLSA3 provenance release flow** (PR [#123](https://github.com/disnana/NanaSQLite/pull/123)):
  - Added `actions: read` and `contents: read` permissions to the provenance verification job in GitHub Actions.
  - Constructed the expected provenance filename from the `provenance-name` output and now fail fast if the file is missing.
  - Updated GitHub Release asset upload to reference the exact generated provenance file instead of a wildcard, preventing release-time artifact mismatches.

### [1.3.4rc2] - 2026-03-08

#### Security Fixes

- **Implemented SQL injection protection for table names** (PR [#121](https://github.com/disnana/NanaSQLite/pull/121), [#122](https://github.com/disnana/NanaSQLite/pull/122)):
  - Table names were interpolated directly into SQL queries, making crafted names exploitable for injection.
  - Sanitized (double-quoted) table name is now cached in `self._safe_table` and used in all SQL execution paths.
  - `self._table` retains the raw name for `__repr__` and backwards compatibility.
  - Updated SECURITY.md with disclosure history and remediation details.
  - Added PoC scripts (`etc/poc/poc_sqli.py`, `etc/poc/poc_none.py`) to document the risk.

#### Bug Fixes & Code Quality

- **Applied `_NOT_FOUND` sentinel to `get_fresh()` and `__contains__`** (PR [#121](https://github.com/disnana/NanaSQLite/pull/121)):
  - `get_fresh()` previously returned `None` on a DB miss, making it impossible to distinguish from a stored `None` value.
  - Switched to the `_NOT_FOUND = object()` sentinel so DB misses and stored `None` are reliably distinguished.
  - Restored a lightweight `__contains__` implementation to reduce unnecessary DB reads.

#### CI Fixes

- **Fixed validkit-py CI test guards** (PR [#119](https://github.com/disnana/NanaSQLite/pull/119)):
  - Updated CI to install the `validation` extra so validkit-related tests are executed correctly.

#### Documentation

- **Added validkit-py validation guide** (PR [#117](https://github.com/disnana/NanaSQLite/pull/117)):
  - Added validkit-py usage and validation guides to both the English and Japanese documentation sites.
- **Reordered and classified guide lessons** (PR [#116](https://github.com/disnana/NanaSQLite/pull/116)):
  - Reorganised and categorised guide lessons in the JA/EN site documentation.
- **Fixed docs inconsistencies, broken links, and factual errors** (PR [#115](https://github.com/disnana/NanaSQLite/pull/115)):
  - Resolved inconsistencies between English and Japanese documentation, fixed broken links, corrected factual errors, and added missing documentation.

### [1.3.4rc1] - 2026-03-07

#### New Features

- **Added `batch_update_partial()` method** (sync and async):
  - New method that writes a batch in "best-effort" mode when a `validator` is set.
  - Each entry is validated individually; only entries that pass are written to the database.
  - Returns a `dict` of `{key: error_message}` for failed entries — no exception is raised.
  - When `coerce=True`, coerced values are stored for successful entries.
  - The existing `batch_update()` retains its atomic behaviour (all-or-nothing).
  - Async counterpart added as `AsyncNanaSQLite.abatch_update_partial()`.

#### Bug Fixes & Code Quality

- **Fixed mypy error in `core.py`**:
  - `_serialize()` returned `json_str` which mypy inferred as `str | None` in the `HAS_ORJSON=False` path; suppressed with `type: ignore` since `json_str` is guaranteed `str` at that point.
- **Fixed ruff violations in examples**:
  - `examples/test_examples.py`: import sort (I001), `assert False` → `raise AssertionError()` (B011), class name to CapWords (N801).
  - `examples/validkit_batch_demo.py`: import sort (I001).

#### Added Examples

- **Added `examples/validkit_batch_demo.py`**:
  - Demonstrates atomic `batch_update()` and best-effort `batch_update_partial()`.
  - Includes `coerce=True` usage with field-level `.coerce()`.
- **Extended `examples/test_examples.py`** with validkit batch operation validation:
  - Atomic rollback verification, partial write verification, coerce mode verification.

### [1.3.4b3] - 2026-03-05

#### Bug Fixes & Stability Improvements

- **Fixed test instability on Python 3.9** (`tests/test_tdd_cycle_6.py`) (PR [#113](https://github.com/disnana/NanaSQLite/pull/113)):
  - `test_ellipsis_type_is_available` checks for `types.EllipsisType` (added in Python 3.10),
    but was unconditionally asserting its presence and therefore always failed on Python 3.9.
  - Added `@pytest.mark.skipif(sys.version_info < (3, 10), ...)` so the test is skipped on
    Python 3.9 and still runs on Python 3.10+.
  - Because both `core.py` and `async_core.py` use `from __future__ import annotations`, the
    `types.EllipsisType` in their type annotations is stored as a string and is never evaluated
    at runtime, so the library itself already works correctly on Python 3.9. This was a
    test-only issue.
  - No impact on library behaviour or public API.

- **Fixed `table()` cache settings inheritance** (PR [#112](https://github.com/disnana/NanaSQLite/pull/112)):
  - Child instances created via `table()` did not inherit `cache_ttl` / `cache_persistence_ttl` from
    their parent, causing `ValueError` when the parent used a TTL cache strategy.
  - Introduced `_cache_strategy_raw`, `_cache_size_raw`, `_cache_ttl_raw`, and
    `_cache_persistence_ttl_raw` to store the original arguments; `table()` now propagates
    all cache settings correctly.

- **`AsyncNanaSQLite` now raises `ImportError` eagerly when validkit-py is missing** (PR [#112](https://github.com/disnana/NanaSQLite/pull/112)):
  - Previously the error was deferred until a write occurred. `AsyncNanaSQLite.__init__` now
    raises `ImportError` immediately when `validator` is supplied without validkit-py installed,
    aligning behaviour with the synchronous `NanaSQLite`.
  - Added `HAS_VALIDKIT` flag to `async_core.py`.

- **Exception narrowing in `core.py`**:
  - Replaced broad `except Exception:` clauses guarding optional imports (orjson / validkit-py)
    with the more specific `except ImportError:`.

- **Type annotation fixes**:
  - Added `"ttl"` to the `Literal` type of the `cache_strategy` argument in `table()`.
  - Changed the `_UNSET` sentinel type annotation to `types.EllipsisType` for improved type safety.

- **mypy configuration update** (`pyproject.toml`):
  - Bumped `python_version` from `3.9` to `3.10` so that `types.EllipsisType` is recognised
    during static type checking.

#### API Documentation Fixes (PR [#112](https://github.com/disnana/NanaSQLite/pull/112))

- Updated `NanaSQLite.table()` and `AsyncNanaSQLite.table()` API docs (English and Japanese)
  to show `validator=...` and `coerce=...` (sentinel default indicating parent-inheritance).

#### Tests & Quality Improvements (PR [#112](https://github.com/disnana/NanaSQLite/pull/112))

- **Added comprehensive test suites**:
  - `tests/test_table_inheritance_comprehensive.py`: 75 test cases covering all `table()` inheritance scenarios.
  - `tests/test_validkit_integration.py`: Integration tests for validkit-py (sync and async).
  - `tests/test_tdd_review_fixes.py`: Regression tests for review-comment fixes.
  - `tests/test_tdd_cycle_2.py` through `tests/test_tdd_cycle_10.py`: Per-cycle regression tests.
- **Improved validkit availability check**:
  - Replaced `importlib.util.find_spec` with a `try/except import` check so broken installations
    are also correctly detected.

### [1.3.4b2] - 2026-03-04

#### New Features

- **`validator` parameter (optional dependency: validkit-py)**:
  - Added `validator` parameter to `NanaSQLite.__init__` and `AsyncNanaSQLite.__init__`.
  - Accepts a validkit-py schema (plain dict or `Schema` object). When supplied, values are validated before every write.
  - Raises `NanaSQLiteValidationError` on schema violation.
  - Raises `ImportError` with an install hint when `validator` is supplied but `validkit-py` is not installed.
  - Install via `pip install nanasqlite[validation]`.
  - Exposes `HAS_VALIDKIT` flag from the `nanasqlite` package (and `core` module).

- **Per-table `validator` support in `table()`**:
  - Added `validator` parameter to `NanaSQLite.table()` and `AsyncNanaSQLite.table()`.
  - Different schemas can now be applied per sub-table.
  - When `validator` is omitted, the parent instance's schema is inherited automatically.

- **`coerce` parameter (auto-conversion option)**:
  - Added `coerce: bool = False` parameter to `NanaSQLite.__init__`, `NanaSQLite.table()`, `AsyncNanaSQLite.__init__`, and `AsyncNanaSQLite.table()`.
  - When `True`, the coerced value returned by validkit-py (e.g. `"42"` → `42`) is stored instead of the original value.
  - **Important**: Auto-conversion requires **both** `coerce=True` on `NanaSQLite` AND `.coerce()` on each field validator in the schema (e.g., `v.int().coerce()`). Without `.coerce()` on the field, values whose types don't match the schema will still raise `NanaSQLiteValidationError` even with `coerce=True`.
  - Works in conjunction with `validator`; has no effect when no validator is set.
  - When omitted in `table()`, the parent's `coerce` setting is inherited automatically.

- **`batch_update()` validation support**:
  - When a `validator` is set, `batch_update()` now validates all values before touching the database.
  - If any value fails validation, nothing is written (atomic failure guarantee).
  - When `coerce=True`, coerced values are bulk-written instead of the originals.

#### Bug Fixes

- **`table()` no longer drops the parent `validator` on child instances**:
  - In b1, child instances created via `table()` did not inherit `_validator`, so writes to
    sub-tables bypassed validation entirely.
  - The same issue was present in `AsyncNanaSQLite.table()` where `_validator` was never
    assigned to `async_sub_db`; this is now fixed.

### [1.3.4b1] - 2026-03-04

#### New Features

- **`lock_timeout` parameter** (P2-1):
  - Added `lock_timeout: float | None = None` parameter to `NanaSQLite.__init__`.
  - When set, raises `NanaSQLiteLockError` if the lock cannot be acquired within the specified seconds.
  - Default `None` preserves the existing unlimited-wait behaviour. Fully backward-compatible.
  - Introduced `_acquire_lock()` context manager internally so user-facing exclusive operations respect the timeout (some internal operations such as TTL expiry deletion continue to use blocking acquisition).

- **`backup()` / `restore()` methods** (P2-3):
  - `NanaSQLite.backup(dest_path)`: Backs up the current database to `dest_path` using APSW's SQLite online backup API.
  - `NanaSQLite.restore(src_path)`: Restores the database from a backup file, re-establishes the connection, and clears the in-memory cache. Explicitly removes WAL/SHM/journal sidecar files (`-wal`/`-shm`/`-journal`) before reopening to prevent stale WAL replay causing an inconsistent state.
  - Both are new public methods only; no backward-compatibility impact.

#### Thread Safety Improvements

- **Lock-protected child instance creation in `table()`**:
  - Wrapped child instance creation and `WeakSet` registration in `table()` with `_acquire_lock()` to prevent race conditions with `restore()`'s connection replacement, eliminating the risk of child instances referencing a closed connection.

#### Bug Fixes

- **Added `_check_connection()` to `__delitem__`**:
  - `del db[key]` on a closed connection now raises `NanaSQLiteClosedError` consistently, matching the behaviour of `__setitem__`, `pop()`, and `clear()`.

### [1.3.4b0] - 2026-03-04

#### Code Quality Improvements
- **Async pool cleanup log level fix**:
  - Changed the log level from `ERROR` to `WARNING` for `AttributeError` occurrences during read-only pool drain in `AsyncNanaSQLite.close()`.
  - Updated the comment wording from "Programming error" to "Unexpected AttributeError - log and continue cleanup for resilience" to better reflect intent.
  - Log output only; no behaviour or backward-compatibility impact.

#### Documentation & Planning
- **Added v1.3.x plan review document** (`etc/in_progress/v1.3.x_plan_review.md`):
  - Cross-referenced all `etc/` planning docs against the v1.3.x changelog to surface remaining work and set priorities.
  - Documented priorities for roadmap Phase 2 items still outstanding (lock timeout, validation foundation, backup/restore).
  - Included a draft release schedule from v1.3.4b0 through v1.4.0.
- **Updated `etc/README.md`**: Added the new review document to the `in_progress/` table.
- **Reorganised `etc/` directory** (PR [#109](https://github.com/disnana/NanaSQLite/pull/109)):
  - Replaced the flat `future_plans/` folder with three status-based subdirectories: `implemented/`, `in_progress/`, and `planned/`.
  - Verified that all v1.3.0 cache features (`ExpiringDict`, `UnboundedCache`, `TTLCache`, etc.) are fully implemented.

#### Dependency Updates (docs/site Maintenance)
- **docs/site dependency updates** (Renovate):
  - Updated `autoprefixer` from v10.4.24 to v10.4.27. ([#105](https://github.com/disnana/NanaSQLite/pull/105))
  - Updated `postcss` from v8.5.6 to v8.5.8. ([#106](https://github.com/disnana/NanaSQLite/pull/106))
  - Updated `vue` from v3.5.27 to v3.5.29. ([#107](https://github.com/disnana/NanaSQLite/pull/107))
  - Updated `tailwindcss` / `@tailwindcss/postcss` from v4.1.18 to v4.2.1. ([#108](https://github.com/disnana/NanaSQLite/pull/108))

### [1.3.4dev0] - 2026-03-02

#### CI / Development Environment
- **SLSA provenance cache restore warning — investigation and revert**:
  - Added an empty `go.sum` at the repo root to suppress the `Restore cache failed` warning emitted by the `provenance / generator` job (PR [#103](https://github.com/disnana/NanaSQLite/pull/103)).
  - Determined that the fix was ineffective: the `provenance / generator` job runs on an isolated runner that does not check out this repository, so the warning cannot be silenced by a local file. The empty `go.sum` was subsequently removed (PR [#104](https://github.com/disnana/NanaSQLite/pull/104)).

#### Other
- Bumped version to `1.3.4dev0` (development snapshot following the `1.3.3` release).

### [1.3.3] - 2026-03-02

#### Security
- **docs/site dependency vulnerability fixes**:
  - Updated/pinned rollup to a safe version (`>=4.59.0`) to address the rollup vulnerability (GHSA-mw96-cpmx-2vgc).
  - Related PRs: [#99](https://github.com/disnana/NanaSQLite/pull/99), [#102](https://github.com/disnana/NanaSQLite/pull/102)

#### CI / Development Environment
- **GitHub Actions updates**:
  - Bumped `actions/download-artifact` to v8. ([#100](https://github.com/disnana/NanaSQLite/pull/100))
  - Bumped `actions/upload-artifact` to v7. ([#101](https://github.com/disnana/NanaSQLite/pull/101))
  - Bumped `google/osv-scanner-action` (reusable / reusable-pr) to 2.3.3. ([#97](https://github.com/disnana/NanaSQLite/pull/97), [#98](https://github.com/disnana/NanaSQLite/pull/98))

#### Dependency Updates (Maintenance)
- **Release automation action update**:
  - Updated `softprops/action-gh-release` to v2. ([#96](https://github.com/disnana/NanaSQLite/pull/96))

#### Notes
- This release is primarily a maintenance update (security/CI/dependency bumps) and does not include breaking changes to the public API.

### [1.3.2] - 2026-01-17

#### Performance Optimization
- **orjson Integration Refinement**:
  - Removed unnecessary variable allocation in `_serialize()` method to improve code readability and maintainability.
  - Verified and validated that orjson JSON encoding/decoding is effectively utilized across all encryption paths (Fernet, AES-GCM, ChaCha20).
  - Expected **3-5x performance improvement** compared to standard `json` module.
  - Confirmed that async processing (`AsyncNanaSQLite`) automatically benefits from orjson via ThreadPoolExecutor.

#### Code Quality Improvements
- **Core Code Optimization**:
  - Enhanced code readability and clarified variable scope.

#### Testing & Validation
- **orjson Tests Verification**:
  - Confirmed all tests in `tests/test_json_backends.py` run correctly.
  - Verified compatibility in both orjson-available and fallback environments.
  - Confirmed automatic JSON backend switching (HAS_ORJSON flag) functions correctly.

### [1.3.1] - 2025-12-28

#### New Features: Optional Data Encryption
- **Multi-mode Encryption**: Transparent encryption using `cryptography`.
    - **AES-GCM (Default)**: Secure and fast, optimized for hardware acceleration (AES-NI).
    - **ChaCha20-Poly1305**: High software-only performance, ideal for devices without AES-NI.
    - **Fernet**: High-level API for compatibility and ease of use.
    - Added `encryption_key` and `encryption_mode` parameters to `NanaSQLite` and `AsyncNanaSQLite`.
- **Extra Installation**: `pip install nanasqlite[encryption]` to install required dependencies.

#### New Features: Flexible Cache Strategy & TTL Support (v1.3.1-alpha.0)
- **TTL (Time-To-Live) Cache**: Set expiration for cached data using `cache_strategy=CacheType.TTL, cache_ttl=seconds`.
- **Persistence TTL**: Automatically delete expired data from the SQLite database with `cache_persistence_ttl=True`.
- **FIFO-limited Unbounded Cache**: Specify `cache_size` in `UNBOUNDED` mode for FIFO (First-In-First-Out) eviction.
- **Cache Clearing API**: Added `db.clear_cache()` and async `aclear_cache()`.

#### Improvements & Fixes
- **Optimized `ExpiringDict`**: Internal utility for high-precision, low-overhead expiration management.
- **Maintained Performance**: Preserved the fast-path for the default `UNBOUNDED` mode while ensuring limits are strictly enforced when configured.
- **Enhanced Type Safety**: Fully compliant with `mypy` and `ruff` strict checks.
- **Unified Benchmarks**: Consolidated encryption and cache strategy benchmarks into `tests/test_benchmark.py` (Sync) and `tests/test_async_benchmark.py` (Async).
- **Test Coverage**: Added `tests/test_async_cache.py` to verify async cache behaviors (LRU eviction, TTL expiration).

### [1.3.0dev0] - 2025-12-27

#### New Features: Flexible Cache Strategy
- **Added `CacheType` Enum**: Choose between `UNBOUNDED` (infinite, legacy behavior) and `LRU` (eviction-based).
- **LRU Cache Implementation**: Limit memory usage with `cache_strategy=CacheType.LRU, cache_size=N`.
- **Per-Table Configuration**: Configure specific tables via `db.table("logs", cache_strategy=CacheType.LRU, cache_size=100)`.
- **Performance Option**: Install `lru-dict` C-extension via `pip install nanasqlite[speed]` for up to 2x speedup.
- **Automated Fallback**: Automatically falls back to standard library `OrderedDict` if `lru-dict` is not installed.

#### New Tests
- `tests/test_cache.py`: Comprehensive test suite for cache strategies (eviction, persistence, per-table configuration).

### [1.2.2b1] - 2025-12-27

#### Documentation & Brand Overhaul
- **Ultra-Modern Documentation Site**:
  - Built a new high-end official site using VitePress + Tailwind CSS in `docs/site`, significantly improving design and UX.
  - **Official SVG Identity**: Created an original 'Dict-Stack' symbol. Features 100% transparency, automatic dark mode support (via inverted filters), and infinite vector resolution.
  - **Truly Isolated Bilingual API Docs**: Implemented an intelligent extraction engine to parse docstrings and generate purely localized references for both Japanese and English.
- **Automation & Deployment**:
  - Introduced automated deployment via GitHub Actions (`deploy-docs.yml`).
  - Implemented smart history preservation that automatically merges previous benchmark data from `gh-pages` into the new documentation build.

#### Security & CI Improvements
- **SQL Validation Refinement**:
  - Added the `||` (concatenation) operator to the fast-validation safe set, resolving false positives in complex SQL alias queries.
- **CI/CD Stability**:
  - Strict re-sorting of imports in `core.py` and `gen_api_docs.py` to comply with the latest `ruff` linting rules.
  - Enhanced dependency management for documentation builds.

### [1.2.2a1] - 2025-12-26

#### Development Tools (Benchmarks & CI/CD)
- **Fixed Benchmark Comparison Logic**:
  - Standardized comparison to use ops/sec; higher values now correctly show as positive (🚀/✅) improvements.
  - Added absolute ops/sec difference (e.g., `+2.1M ops`) to the performance summary table.
  - **Ops/sec Accuracy**: Switched to using raw `ops` data from the benchmark tool instead of calculating from mean time (approximation). This also fixed the bug where OS details showed `(0.0)`.
  - Corrected time formatting for sub-microsecond values to explicitly use `ns` (nanoseconds).
  - Introduced status emojis (🚀, ✅, ➖, ⚠️, 🔴) for quick visual performance assessment.
- **Workflow Optimizations**:
  - `benchmark.yml`: Changed benchmarks to be informational-only to prevent CI failures caused by GitHub Actions runner performance variance (~10-60%).
  - `ci.yml`: Optimized triggers by restricting automatic `push` runs to the `main` branch. Added `workflow_dispatch` for manual runs on other branches.
  - Simplified `should-run` check logic.


### [1.2.1b2] - 2025-12-25

#### Development Tools
- **CI/CD Workflow Consolidation**:
  - Consolidated `lint.yml`, `test.yml`, `publish.yml`, and `quality-gate.yml` into a single `ci.yml`.
  - Added direct links to PyPI and GitHub Release, and detailed job statuses (Cancelled/Skipped support) in the final summary.
- **Test Environment Optimization**:
  - Refined the CI test matrix. Ubuntu runs all versions, while Windows/macOS focus on popular versions (3.11 and 3.13) to reduce execution time.
  - Added `pytest-xdist` to dev dependencies for parallel testing support.
- **Type Checking Improvements**:
  - Resolved 156 mypy errors by refining the configuration (introduced `--no-strict-optional` and fine-tuned error code controls).

#### Development Tools
- **Lint & CI Environment**:
  - Added `tox.ini` with environments for `tox -e lint` (ruff), `tox -e type` (mypy), `tox -e format`, and `tox -e fix`.
  - Added ruff configuration to `pyproject.toml` (E/W/F/I/B/UP/N/ASYNC rules, Python 3.9+ support, line-length: 120).
  - Added mypy configuration to `pyproject.toml` (using `--no-strict-optional` flag for practical type checking).
  - Added `.github/workflows/lint.yml`: PyPA/twine-style CI workflow with tox integration, FORCE_COLOR support, and summary output.
  - Added `.github/workflows/quality-gate.yml`: All-green gate with main branch detection and publish readiness check.
  - Added dev dependencies: `tox>=4.0.0`, `ruff>=0.8.0`, `mypy>=1.13.0`.
- **Code Quality Improvements**:
  - Fixed 1373 lint errors via ruff auto-fix (import ordering, unused imports removal, pyupgrade, whitespace, etc.).
  - Added B904 (raise without from) and B017 (assert raises Exception) to ignore list.
  - Adjusted mypy configuration for practical use (156 errors → 0 errors).

### [1.2.0b1] - 2025-12-24

#### Security & Robustness
- **Enhanced `ORDER BY` Parsing**:
  - Implemented a dedicated parser `_parse_order_by_clause` in `NanaSQLite` to safely handle and validate complex `ORDER BY` clauses.
  - Improved protection against SQL injection while supporting legitimate complex sorting patterns.
- **Strict Validation Fixes**:
  - Standardized error messages for dangerous patterns (`;`, `--`, `/*`) to consistently follow the `Invalid [label]: [message]` format.
  - Ensured consistent behavior between legacy and new security tests by applying a unified message format for all validation failures.

#### Refactoring
- **Code Organization**:
  - Extracted `_sanitize_sql_for_function_scan` logic to a new `nanasqlite.sql_utils` module for better maintainability.
  - Eliminated code duplication in `AsyncNanaSQLite` by consolidating `query` and `query_with_pagination` methods into a shared `_shared_query_impl` helper method (~150 lines reduced).
- **Type Safety**:
  - Added `Literal` type hints for `context` parameter to improve IDE support and type checking (PR #36).

#### Fixes & Improvements
- **Async Logging**:
  - Increased log level from DEBUG to WARNING for errors occurring during read-pool cleanup to ensure resource issues are visible.
  - Added connection context to cleanup error messages.
- **Improved Async Pool Cleanup Robustness**:
  - Enhanced `AsyncNanaSQLite.close()` method to ensure all pool connections are cleaned up even if some connections encounter errors.
  - Changed error handling to continue cleanup instead of breaking on `AttributeError`, preventing resource leaks.
- **Tests**:
  - Fixed `__eq__` method to correctly propagate `NanaSQLiteClosedError` when instances are closed (PR #44).
  - Improved exception handling specificity in security tests (PR #43).
  - Clarified comments in security tests regarding validation timing (PR #35).
  - Removed duplicate `pytest` imports and cleaned up temporary test files (`temp_test_parser.py`).

### [1.2.0a2] - 2025-12-23

- **Enhanced Async Security Features**:
  - Fixed `AsyncNanaSQLite.query` and `query_with_pagination` to correctly pass `allowed_sql_functions`, `forbidden_sql_functions`, and `override_allowed` to `_validate_expression`.
  - Added comprehensive asynchronous security tests in `tests/test_security_async_v120.py`.
- **Improved Async Connection Management**:
  - Added `_closed` flag to `AsyncNanaSQLite` to track the connection state.
  - Improved child instance invalidation: sub-instances created via `table()` are now immediately marked as closed when the parent is closed.
  - Fixed `close()` behavior to ensure that even uninitialized instances correctly transition to a closed state, raising `NanaSQLiteClosedError` on subsequent operations.

### [1.2.0a1] - 2025-12-23

- **Async Read-Only Connection Pool**:
  - Added `read_pool_size` logic to `AsyncNanaSQLite`.
  - Enables parallel execution for `query`, `query_with_pagination`, `fetch_all`, `fetch_one`.
  - Enforces `read-only` mode for pool connections for safety.
- **Bug Fixes**:
  - Fixed `apsw.ExecutionCompleteError` occurring in `query` and `query_with_pagination` when results are empty (0 rows).
  - Aligned column metadata extraction with sync implementation using `PRAGMA table_info` and manual parsing instead of relying on `cursor.description`.

### [1.2.0dev1] - 2025-12-23

#### Fixed
- **Async API Consistency**:
  - Added `a`-prefixed aliases for all methods in `AsyncNanaSQLite` (e.g., `abatch_update`, `ato_dict`).
  - Resolved "method not defined" errors in `test_async_benchmark.py`.
- **Backward Compatibility Fixes**:
  - Re-aligned SQL injection error messages to match legacy test expectations (e.g., "Invalid order_by clause").
  - Updated `test_enhancements.py` to handle `NanaSQLiteClosedError` alongside class name checks.
- **Windows Stability**:
  - Refactored `test_security_v120.py` to use `tmp_path` fixture, resolving `BusyError` and `IOError` on Windows.
- **`query`/`query_with_pagination` Bug Fix**:
  - Fixed issue where `limit=0` and `offset=0` were ignored. Changed `if limit:` to `if limit is not None:`.
  - ⚠️ **Backward Compatibility**: Previously, passing `limit=0` returned all rows. Now it correctly returns 0 rows. If you used `limit=0` to mean "no limit", change to `limit=None`.
- **Edge Case Tests Added**:
  - Created `tests/test_edge_cases_v120.py` with tests for empty `batch_*` operations and pagination boundary conditions.

### [1.2.0dev0] - 2025-12-22

#### Added
- **Security Enhancements (Phase 1)**:
  - Introduced `strict_sql_validation` flag (Exception or Warning for unauthorized functions).
  - Introduced `max_clause_length` to limit dynamic SQL length (ReDoS protection).
  - Enhanced detection for dangerous SQL patterns (`;`, `--`, `/*`) and keywords (`DROP`, `DELETE`, etc.).
- **Strict Connection Management**:
  - Introduced `NanaSQLiteClosedError`.
  - Implemented child instance tracking/invalidation when the parent instance is closed.
- **Maintenance**:
  - Created `DEVELOPMENT_GUIDE.md` (Bilingual).
  - Codified environment sync rule: `pip install -e . -U`.

### [1.1.0] - 2025-12-19

#### Added
- **Custom Exception Classes**:
  - `NanaSQLiteError` (base class)
  - `NanaSQLiteValidationError` (validation errors)
  - `NanaSQLiteDatabaseError` (database operation errors)
  - `NanaSQLiteTransactionError` (transaction-related errors)
  - `NanaSQLiteConnectionError` (connection errors)
  - `NanaSQLiteLockError` (lock errors, for future use)
  - `NanaSQLiteCacheError` (cache errors, for future use)

- **Batch Retrieval (`batch_get`)**:
  - Efficiently load multiple keys with `batch_get(keys: List[str])`
  - Async support via `AsyncNanaSQLite.abatch_get(keys)`
  - Optimizes cache by fetching multiple items in a single query
- **Enhanced Transaction Management**:
  - Transaction state tracking (`_in_transaction`, `_transaction_depth`)
  - Detection and error reporting for nested transactions
  - Added `in_transaction()` method
  - Prevention of connection closure during transactions
  - Detection of commit/rollback outside transactions

- **Async Transaction Support**:
  - `AsyncNanaSQLite.begin_transaction()`
  - `AsyncNanaSQLite.commit()`
  - `AsyncNanaSQLite.rollback()`
  - `AsyncNanaSQLite.in_transaction()`
  - `AsyncNanaSQLite.transaction()` (context manager)
  - `_AsyncTransactionContext` class implementation

- **Resource Leak Prevention**:
  - Parent instance tracks child instances with weak references
  - Notification to child instances when parent is closed
  - Prevention of orphaned child instance usage
  - Added `_check_connection()` method
  - Added `_mark_parent_closed()` method

#### Improvements
- **Enhanced Error Handling**:
  - Added error handling to `execute()` method
  - Wraps APSW exceptions with `NanaSQLiteDatabaseError`
  - Preserves original error information (`original_error` attribute)
  - Added connection state checks to each method
  - Uses `NanaSQLiteValidationError` in `_sanitize_identifier()`

- **Added connection check to `__setitem__` method**

#### Documentation
- **New Documentation**:
  - `docs/en/error_handling.md` - Error handling guide
  - `docs/en/transaction_guide.md` - Transaction guide
  - `tests/test_enhancements.py` - Tests for enhanced features (21 tests)

- **README Updates**:
  - Added transaction support section
  - Added custom exception sample code
  - Added async transaction samples

#### Tests
- **New Tests** (21 tests):
  - Custom exception class tests (5 tests)
  - Transaction feature enhancement tests (6 tests)
  - Resource management tests (3 tests)
  - Error handling tests (2 tests)
  - Transaction and exception combination tests (2 tests)
  - Async transaction tests (3 tests)

#### Fixes
- Fixed security tests to expect `NanaSQLiteValidationError`

---

### [1.1.0a3] - 2025-12-17

#### Documentation Improvements
- **Added usage notes for `table()` method**:
  - Added important usage notes section to README.md (English & Japanese)
  - Warning about creating multiple instances for the same table
  - Recommendation to use context managers
  - Best practices clarification
- **Improved docstrings**:
  - Added detailed notes to `NanaSQLite.table()` docstring
  - Added detailed notes to `AsyncNanaSQLite.table()` docstring
  - Added specific examples of deprecated and recommended patterns
- **Future improvement plans**:
  - Documented improvement proposals in `etc/future_plans/` directory
  - Duplicate instance detection warning feature (Proposal B)
  - Connection state check feature (Proposal B)
  - Shared cache mechanism (Proposal C - on hold)

#### Analysis & Investigation
- **Comprehensive investigation of table() functionality**:
  - Stress tests: All 7 tests passed
  - Edge case tests: 10 tests conducted
  - Concurrency tests: All 5 tests passed
  - **Issues found**: 2 (minor design limitations)
    1. Cache inconsistency with multiple instances for same table (addressed with documentation)
    2. Sub-instance access after close (addressed with documentation)
  - **Conclusion**: Ready for production use, no performance issues

---

### [1.1.0dev2] - 2025-12-16

#### Current Development Status
- Development version in progress
- Testing in progress (all 15 tests in `test_concurrent_table_writes.py` passing)

### [1.1.0dev1] - 2025-12-15

#### Added
- **Multi-table Support (`table()` method)**: Safely operate on multiple tables within the same database
  - Get an instance for another table with `db.table(table_name)`
  - **Shared connection and lock**: Multiple table instances share the same SQLite connection and thread lock
  - Thread-safe: Concurrent writes to different tables from multiple threads work safely
  - Memory efficient: Reuses connections to save resources
  - **Sync version**: `NanaSQLite.table(table_name)` → `NanaSQLite` instance
  - **Async version**: `await AsyncNanaSQLite.table(table_name)` → `AsyncNanaSQLite` instance
  - Cache isolation: Each table instance maintains independent in-memory cache

#### Internal Implementation Improvements
- **Enhanced thread safety**: Added `threading.RLock` to all database operations
  - Read (`_read_from_db`), write (`_write_to_db`), delete (`_delete_from_db`)
  - Query execution (`execute`, `execute_many`)
  - Transaction operations
- **Improved connection management**:
  - `_shared_connection` parameter for connection sharing
  - `_shared_lock` parameter for lock sharing
  - `_is_connection_owner` flag for connection ownership management
  - `close()` method only executed by connection owner

#### Tests
- **15 comprehensive test cases** (all passing):
  - Sync multi-table concurrent write tests (2 tables, multiple tables)
  - Async multi-table concurrent write tests (2 tables, multiple tables)
  - Stress test (1000 concurrent writes)
  - Cache isolation tests
  - Table switching tests
  - Edge case tests

#### Compatibility
- **Full backward compatibility**: No impact on existing code
- All new parameters are optional (internal use)

### [1.0.3rc7] - 2025-12-10

#### Added
- **Async Support (AsyncNanaSQLite)**: Complete async interface for async applications
  - `AsyncNanaSQLite` class: Provides async versions of all operations
  - **Dedicated ThreadPoolExecutor**: Configurable max_workers (default 5) for optimization
  - High-performance concurrent processing with `ThreadPoolExecutor`
  - Safe to use with async frameworks like FastAPI, aiohttp
  - Async dict-like interface: `await db.aget()`, `await db.aset()`, `await db.adelete()`
  - Async batch operations: `await db.batch_update()`, `await db.batch_delete()`
  - Async SQL execution: `await db.execute()`, `await db.query()`
  - Async context manager: `async with AsyncNanaSQLite(...) as db:`
  - Concurrent operations support: Multiple async operations can run concurrently
  - Automatic resource management: Thread pool auto-cleanup
- **Comprehensive test suite**: 100+ async test cases
  - Basic operations, concurrency, error handling, performance tests
  - All tests passing
- **Full backward compatibility**: Existing `NanaSQLite` class unchanged

#### Performance Improvements
- Prevents blocking in async apps, improving event loop responsiveness
- Dedicated thread pool enables highly efficient concurrent processing (configurable workers)
- Optimal performance with APSW + thread pool combination
- Tunable max_workers for high-load environments (5-50)

### [1.0.3rc6] - 2025-12-10

#### Added
- **`get_fresh(key, default=None)` method**: Read directly from DB, update cache, and return value
  - Useful for cache synchronization after direct DB changes via `execute()`
  - Uses `_read_from_db` directly to minimize overhead

### [1.0.3rc5] - 2025-12-10

#### Performance Improvements
- **`batch_update()` optimization**: 10-30% faster with `executemany`
- **`batch_delete()` optimization**: Faster bulk deletion with `executemany`
- **`__contains__()` optimization**: Lightweight EXISTS query (faster for large values)

#### IDE/Type Support Enhancements
- Added `from __future__ import annotations`
- Specific type annotations: `Dict[str, Any]`, `Set[str]`
- Clearer parameter types: `Optional[Tuple]`

#### Documentation
- Added cache consistency warning to `execute()` method
- Improved docstrings (Returns, Warning sections)

#### Bug Fixes
- Resolved Git merge conflicts (order_by regex validation)
- Fixed ReDoS vulnerability (switched to comma-split approach)

### [1.0.3rc4] - 2025-12-09

#### Added
- **22 new SQLite wrapper functions**
  - Schema management: `drop_table()`, `drop_index()`, `alter_table_add_column()`, `get_table_schema()`, `list_indexes()`
  - Data operations: `sql_insert()`, `sql_update()`, `sql_delete()`, `upsert()`, `count()`, `exists()`
  - Query extensions: `query_with_pagination()` (with offset/group_by support)
  - Utilities: `vacuum()`, `get_db_size()`, `export_table_to_dict()`, `import_from_dict_list()`, `get_last_insert_rowid()`, `pragma()`
  - Transactions: `begin_transaction()`, `commit()`, `rollback()`, `transaction()` context manager
- 35 new test cases (all passing)
- Complete backward compatibility maintained

### [1.0.3rc3] - 2025-12-09

#### Added
- **Pydantic compatibility**
  - `set_model()`, `get_model()` methods
  - Support for nested models and optional fields
- **Direct SQL execution**
  - `execute()`, `execute_many()`, `fetch_one()`, `fetch_all()` methods
  - SQL injection protection via parameter binding
- **SQLite wrapper functions**
  - `create_table()`, `create_index()`, `query()` methods
  - `table_exists()`, `list_tables()` helper functions
- 32 new test cases
- Updated English/Japanese documentation
- Async support consultation document

### [1.0.0] - 2025-12-09

#### Added
- Initial release
- Dict-like interface (`db["key"] = value`)
- Instant persistence to SQLite via APSW
- Lazy load (on-access) caching
- Bulk load (`bulk_load=True`) for startup loading
- Nested structure support (tested up to 30 levels)
- Performance optimizations (WAL, mmap, cache_size)
- Batch operations (`batch_update`, `batch_delete`)
- Context manager support
- Full dict method compatibility
- Type hints (PEP 561)
- Bilingual documentation (English/Japanese)
- GitHub Actions CI (Python 3.9-3.13, Ubuntu/Windows/macOS)
