# Security / Performance Audit Report (2026-07-22)

**Target:** NanaSQLite v1.6.0 (current HEAD)<br>
**Scope:** `src/nanasqlite/`, SQL construction, encryption, backup/restore, Async/V2 boundaries, and regression tests.

## Conclusion

No new reproducible Critical or High vulnerability was found through intended library input paths. Known identifier, column-type, expression, and PRAGMA injection regressions remain covered by review and tests.

| Area | Critical | High | Medium | Low | Status |
|---|---:|---:|---:|---:|---|
| New reproducible vulnerabilities | 0 | 0 | 0 | 0 | None found |
| Design trust boundaries | 0 | 0 | 0 | 3 | Operational guidance required |

## Checks performed

- Dynamic SQL construction, AEAD, backup/restore, and Async/V2 boundaries reviewed
- `python -m tox -e lint,type` — PASS
- `python -m pytest tests -x -q` — **1051 passed, 12 skipped**

## Trust boundaries

`execute()` / `execute_many()` intentionally accept arbitrary SQL, and `query()` accepts SQL expressions. Never concatenate external input into SQL; bind values instead.

```python
db.query("users", where="email = ?", parameters=(email,))
```

Validate user-provided paths before calling `backup()` / `restore()`, and limit async request concurrency at the service boundary. `strict_sql_validation=True` is defense in depth, not a safe-SQL parser.

Dependency CVEs are outside this source-code audit and should be audited separately against the release lockfile.
