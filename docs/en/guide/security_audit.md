# Security / Performance Audit Report (2026-07-22)

**Target:** NanaSQLite v1.6.0 (current HEAD)<br>
**Scope:** all `src/nanasqlite/` code; SQL construction, encryption, backup/restore, Async/V2 boundaries, and regression tests.

## Conclusion

No new reproducible Critical or High vulnerability was found through the library's intended input paths. Previously fixed SQL-injection issues involving identifiers, column types, expressions, and PRAGMA handling remain covered by implementation review and regression tests.

This conclusion assumes applications do not pass untrusted input directly as SQL text or filesystem paths.

| Area | Critical | High | Medium | Low | Status |
|---|---:|---:|---:|---:|---|
| New reproducible vulnerabilities | 0 | 0 | 0 | 0 | None found |
| Design trust boundaries | 0 | 0 | 0 | 3 | Operational guidance required |

## Checks performed

- Reviewed every dynamic SQL construction path, including identifier, column-type, expression, and PRAGMA validation.
- Reviewed AES-GCM / ChaCha20-Poly1305 use, backup/restore integrity checks and atomic replacement, plus Async/V2 boundaries.
- `python -m tox -e lint,type` — PASS
- `python -m pytest tests -x -q` — **1051 passed, 12 skipped**

## Verified controls

| Attack surface | Control |
|---|---|
| Tables, columns, and indexes | Allowlisted identifiers, always double-quoted |
| Column types | Character and parenthesis-depth validation rejects injected definitions |
| SQL expressions | Checks structural SQL, subquery keywords, and unapproved functions |
| PRAGMA | Separate read and write allowlists |
| Encrypted values | AEAD uses random nonces and never falls back to plaintext after decryption failure |
| Backup / restore | Integrity checks, temporary files with atomic replacement, and WAL/SHM handling |
| V2 direct use | Safe table-name validation is also enforced within V2 Engine |

## Trust boundaries

### SQL-text APIs

`execute()` and `execute_many()` are administrator APIs that intentionally accept arbitrary SQL. `query()` also accepts SQL expressions in `where`, non-identifier `columns`, and `order_by`. Do not concatenate external input into these strings; bind values instead.

```python
db.query("users", where="email = ?", parameters=(email,))
```

`strict_sql_validation=True` is defense in depth, not a conversion of arbitrary SQL into a safe search DSL. Applications that expose expressions must allowlist columns and operators themselves.

### Backup and restore paths

Validate and resolve user-provided paths against an application-owned directory before calling `backup()` or `restore()`.

### Sustained async load

Limit request concurrency at the service boundary (for example, with a semaphore). Unbounded submission can grow the executor queue and memory use.

## Notes and follow-up

The current AEAD format does not bind metadata with AAD. This is not a present vulnerability; a future AAD design should introduce a versioned format while retaining readable legacy data.

Dependency CVEs are outside this source-code audit and should be checked separately against the release lockfile.
