# Validation Guide

Use NanaSQLite with [validkit-py](https://github.com/disnana/Validkit) when you want every write to match a schema before it reaches SQLite.

This guide focuses on the practical setup and usage patterns for the recent `validator` / `coerce` support. For the full parameter reference, see the [NanaSQLite API docs](../api/nanasqlite.md).

## When to Use Validation

Validation is useful when you want to:

- reject malformed records before they are written
- keep table data shapes consistent across your application
- safely coerce string inputs such as `"42"` into typed values
- apply different schemas to different sub-tables

## Installation

Install NanaSQLite with the validation extra:

```bash
pip install nanasqlite[validation]
```

You can check whether the optional dependency is available at runtime:

```python
from nanasqlite import HAS_VALIDKIT

if HAS_VALIDKIT:
    print("validkit-py is available")
else:
    print("Install nanasqlite[validation] to enable schema validation")
```

## Basic Schema Validation

Pass a validkit schema to the `validator` parameter.

```python
from validkit import v
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

schema = {
    "name": v.str(),
    "age": v.int().range(0, 150),
    "active": v.bool(),
}

db = NanaSQLite("users.db", validator=schema)

db["alice"] = {"name": "Alice", "age": 30, "active": True}  # OK

try:
    db["bob"] = {"name": "Bob", "age": "invalid", "active": True}
except NanaSQLiteValidationError as exc:
    print(f"Validation failed: {exc}")
    print("Nothing was written to the database")
```

## Auto-Conversion with `coerce`

`coerce=True` lets NanaSQLite store the converted value returned by validkit-py, but conversion only works when the field validators also opt in with `.coerce()`.

```python
from validkit import v
from nanasqlite import NanaSQLite

schema = {
    "age": v.int().coerce(),
    "score": v.float().coerce(),
}

db = NanaSQLite("scores.db", validator=schema, coerce=True)
db["player1"] = {"age": "20", "score": "9.5"}

print(db["player1"])  # {"age": 20, "score": 9.5}
```

If the field validators do **not** use `.coerce()`, then `coerce=True` alone is not enough:

```python
from validkit import v
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

schema = {"age": v.int()}
db = NanaSQLite("bad.db", validator=schema, coerce=True)

try:
    db["player1"] = {"age": "20"}
except NanaSQLiteValidationError:
    print("The field validator still rejects the string input")
```

## Per-Table Validation

Different sub-tables can use different schemas. Child tables can also inherit the parent's schema automatically.

```python
from validkit import v
from nanasqlite import NanaSQLite

user_schema = {"name": v.str(), "age": v.int()}
score_schema = {"player": v.str(), "score": v.float().range(0.0, 100.0)}

db = NanaSQLite("app.db", validator=user_schema)

users_db = db.table("users")  # inherits user_schema
scores_db = db.table("scores", validator=score_schema)
cache_db = db.table("cache", validator=None)  # disable validation here

users_db["u1"] = {"name": "Alice", "age": 30}
scores_db["s1"] = {"player": "Alice", "score": 98.5}
cache_db["raw"] = {"anything": "goes"}
```

Per-table coercion works the same way:

```python
from validkit import v
from nanasqlite import NanaSQLite

db = NanaSQLite("app.db")
coerce_schema = {"age": v.int().coerce()}
coerce_db = db.table("users_import", validator=coerce_schema, coerce=True)
coerce_db["u2"] = {"age": "31"}  # stored as {"age": 31}
```

## Validation with `batch_update()`

When a validator is configured, `batch_update()` validates the entire batch before writing anything. If one record fails, the whole write is rejected. This is the **default atomic behavior**.

```python
from validkit import v
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

schema = {"name": v.str(), "age": v.int()}
db = NanaSQLite("batch.db", validator=schema)

try:
    db.batch_update({
        "u1": {"name": "Alice", "age": 30},
        "u2": {"name": "Bob", "age": "bad"},
    })
except NanaSQLiteValidationError:
    print("Atomic failure: no records were written")
```

If you want to **reject only the failed keys and still persist the valid ones**, use `batch_update_partial()` instead.

```python
from validkit import v
from nanasqlite import NanaSQLite

schema = {"name": v.str(), "age": v.int()}
db = NanaSQLite("batch.db", validator=schema)

failed = db.batch_update_partial({
    "u1": {"name": "Alice", "age": 30},
    "u2": {"name": "Bob", "age": "bad"},
})

print(failed)     # {"u2": "...validation..."}
print(db["u1"])  # persisted
```

- `batch_update()` for all-or-nothing writes
- `batch_update_partial()` for best-effort imports

## Error Handling Tips

- Catch `NanaSQLiteValidationError` when user input may be malformed.
- Keep schemas close to the code that owns each table.
- Use `validator=None` explicitly for tables that should accept unstructured data.
- Prefer coercion only for trusted input formats that you intentionally want to normalize.

For exception handling patterns, see the [Error Handling Guide](error_handling.md).

## Related References

- [NanaSQLite API Reference](../api/nanasqlite.md)
- [AsyncNanaSQLite API Reference](../api/async_nanasqlite.md)
