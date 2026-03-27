"""
Hooks and Constraints system for NanaSQLite.
"""

from typing import TYPE_CHECKING, Any, Callable, Protocol

from .exceptions import NanaSQLiteValidationError

if TYPE_CHECKING:
    from .core import NanaSQLite


class NanaHook(Protocol):
    """
    Protocol for NanaSQLite hooks that can intercept and mutate read/write/delete operations.
    """

    def before_write(self, db: "NanaSQLite", key: str, value: Any) -> Any:
        """Called before writing. Can validate or mutate the value."""
        ...

    def after_read(self, db: "NanaSQLite", key: str, value: Any) -> Any:
        """Called after reading. Can mutate the value."""
        ...

    def before_delete(self, db: "NanaSQLite", key: str) -> None:
        """Called before deleting. Can abort the deletion."""
        ...


class BaseHook:
    """Base class providing default pass-through implementations for NanaHook."""

    def before_write(self, db: "NanaSQLite", key: str, value: Any) -> Any:
        return value

    def after_read(self, db: "NanaSQLite", key: str, value: Any) -> Any:
        return value

    def before_delete(self, db: "NanaSQLite", key: str) -> None:
        pass


class CheckHook(BaseHook):
    """Simple check constraint."""

    def __init__(self, check_func: Callable[[str, Any], bool], error_msg: str = "Check constraint failed"):
        self.check_func = check_func
        self.error_msg = error_msg

    def before_write(self, db: "NanaSQLite", key: str, value: Any) -> Any:
        if not self.check_func(key, value):
            raise NanaSQLiteValidationError(self.error_msg)
        return value


class UniqueHook(BaseHook):
    """Ensures a specific field in a dictionary value is unique across the table."""

    def __init__(self, field: str):
        self.field = field

    def before_write(self, db: "NanaSQLite", key: str, value: Any) -> Any:
        if isinstance(value, dict) and self.field in value:
            check_val = value[self.field]
            # O(N) iteration over cached/DB values to ensure uniqueness
            # We skip the current key
            for k, v in db.items():
                if k != key and isinstance(v, dict) and v.get(self.field) == check_val:
                    raise NanaSQLiteValidationError(
                        f"Unique constraint violated: '{self.field}' = {check_val} already exists."
                    )
        return value


class ForeignKeyHook(BaseHook):
    """Ensures a specific field refers to an existing key in a target table."""

    def __init__(self, field: str, target_table: "NanaSQLite"):
        self.field = field
        self.target_table = target_table

    def before_write(self, db: "NanaSQLite", key: str, value: Any) -> Any:
        if isinstance(value, dict) and self.field in value:
            ref_key = value[self.field]
            if ref_key not in self.target_table:
                raise NanaSQLiteValidationError(
                    f"Foreign key constraint violated: key '{ref_key}' not found in target table."
                )
        return value


class ValidkitHook(BaseHook):
    """Integration with validkit-py for schema validation."""

    def __init__(self, schema: Any, coerce: bool = False):
        self.schema = schema
        self.coerce = coerce

        try:
            from validkit import validate

            self._validate_func = validate
        except ImportError:
            raise ImportError(
                "The 'validkit-py' library is required for validation. "
                "Install it with: pip install nanasqlite[validation]"
            )

    def before_write(self, db: "NanaSQLite", key: str, value: Any) -> Any:
        try:
            if self.coerce:
                return self._validate_func(value, self.schema)
            else:
                self._validate_func(value, self.schema)
                return value
        except Exception as exc:
            raise NanaSQLiteValidationError(
                f"Value for key '{key}' failed schema validation: {exc} "
                f"/ キー '{key}' の値がスキーマに違反しています: {exc}"
            ) from exc


class PydanticHook(BaseHook):
    """Automatic cast to/from a Pydantic model for seamless integration."""

    def __init__(self, model_class: type):
        self.model_class = model_class

    def before_write(self, db: "NanaSQLite", key: str, value: Any) -> Any:
        if isinstance(value, self.model_class):
            if hasattr(value, "model_dump"):
                return value.model_dump()
            elif hasattr(value, "dict"):
                return value.dict()

        try:
            if hasattr(self.model_class, "model_validate"):
                model = self.model_class.model_validate(value)
                return model.model_dump()
            elif hasattr(self.model_class, "parse_obj"):
                model = self.model_class.parse_obj(value)
                return model.dict()
            return value
        except Exception as exc:
            raise NanaSQLiteValidationError(f"Pydantic validation failed for key '{key}': {exc}") from exc

    def after_read(self, db: "NanaSQLite", key: str, value: Any) -> Any:
        try:
            if hasattr(self.model_class, "model_validate"):
                return self.model_class.model_validate(value)
            elif hasattr(self.model_class, "parse_obj"):
                return self.model_class.parse_obj(value)
        except Exception:
            # If conversion back to the Pydantic model fails, silently fall back to the original value.
            pass
        return value
