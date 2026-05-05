# Ultimate Hooks (General-purpose Hooks & Constraints)

Introduced in `NanaSQLite` v1.5.0, **Ultimate Hooks** is a general-purpose architecture for intercepting database operations (write, read, delete) to apply custom logic or constraints.

The legacy `validator` argument also utilizes this hook mechanism internally.

::: tip Recommendation
If you need custom validation logic or integration with Pydantic, using Ultimate Hooks is highly recommended over the legacy `validator` approach.
:::

## Lifecycle Events

Hooks can respond to the following five events:

- `before_write(key, value)`: Executed just before writing to the DB (`set`, `update`, `batch_update`, etc.). You can transform the value or raise an exception to reject the write.
- `on_write_success(key, value, old_value)`: Executed immediately after a successful DB write. Ideal for operations that should only run if persistence succeeded, such as index updates.
- `after_read(key, value)`: Executed just after reading from the DB (`get`, `items`, etc.), before returning the value to the application. You can transform the value.
- `before_delete(key)`: Executed just before deleting from the DB (`del`, `pop`, etc.). You can raise an exception to reject the deletion.
- `on_delete_success(key, old_value)`: Executed immediately after a successful DB deletion. Ideal for cleaning up associated state or indices.

## Standard Hooks

Useful built-in hooks are available in the `nanasqlite.hooks` module.

### UniqueHook
Enforces uniqueness of a specific field.

```python
from nanasqlite.hooks import UniqueHook

# Ensure the "email" field serves as a unique identifier across the table
db.add_hook(UniqueHook("email"))

db["user1"] = {"email": "alice@example.com"}
db["user2"] = {"email": "alice@example.com"} # Raises NanaSQLiteValidationError
```

### CheckHook
Validates values using a custom function. This is essentially a programmatic version of SQLite's `CHECK` constraint.

```python
from nanasqlite.hooks import CheckHook

# Verify that age is 18 or older
db.add_hook(CheckHook(lambda k, v: v.get("age", 0) >= 18, "Age must be >= 18"))
```

### ForeignKeyHook
Checks referential integrity with another table.

```python
from nanasqlite.hooks import ForeignKeyHook

orders = db.table("orders")
users = db.table("users")

# Ensure that "user_id" in 'orders' exists as a key in the 'users' table
orders.add_hook(ForeignKeyHook("user_id", users))
```

### PydanticHook
Provides seamless integration with Pydantic models. It validates the model on write and automatically converts the data back into a Pydantic instance on read.

```python
from pydantic import BaseModel
from nanasqlite.hooks import PydanticHook

class User(BaseModel):
    name: str
    age: int

db.add_hook(PydanticHook(User))

db["u1"] = {"name": "Nana", "age": 20}
user = db["u1"]
print(type(user)) # <class 'User'>
print(user.name)  # Nana
```

## Creating Custom Hooks

You can create your own hooks by implementing the `NanaHook` protocol.

```python
class MyLoggerHook:
    def before_write(self, key, value):
        print(f"Writing {key}")
        return value # Return as-is if no transformation is needed
```

## Notes

- **Performance**: Since hooks are executed on every operation, heavy logic will impact overall performance.
- **Compatibility**: Using the legacy `validator` argument automatically adds a `ValidkitHook` internally. These methods can coexist.
