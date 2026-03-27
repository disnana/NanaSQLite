import re
from re import Pattern
from typing import Any, Callable

from .compat import HAS_VALIDKIT
from .exceptions import NanaSQLiteValidationError
from .protocols import NanaHook as NanaHook


class BaseHook:
    """Base class providing default pass-through implementations for NanaHook.
    Supports filtering by key_pattern (regex) or key_filter (callable).
    """

    def __init__(
        self,
        key_pattern: str | Pattern | None = None,
        key_filter: Callable[[str], bool] | None = None,
    ):
        self._key_regex = re.compile(key_pattern) if isinstance(key_pattern, str) else key_pattern
        self._key_filter = key_filter

    def _should_run(self, key: str) -> bool:
        """Determines if the hook should run for the given key."""
        if self._key_regex is not None and not self._key_regex.search(key):
            return False
        if self._key_filter is not None and not self._key_filter(key):
            return False
        return True

    def before_write(self, db: Any, key: str, value: Any) -> Any:
        """Default passthrough for before_write.
        (書き込み前のデフォルトパススルー実装)
        """
        return value

    def after_read(self, db: Any, key: str, value: Any) -> Any:
        """Default passthrough for after_read.
        (読み取り後のデフォルトパススルー実装)
        """
        return value

    def before_delete(self, db: Any, key: str) -> None:
        """Default implementation for before_delete. Does nothing.
        (削除前のデフォルト実装。何もしません)
        """
        pass


class CheckHook(BaseHook):
    """Simple check constraint."""

    def __init__(
        self,
        check_func: Callable[[str, Any], bool],
        error_msg: str = "Check constraint failed",
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.check_func = check_func
        self.error_msg = error_msg

    def before_write(self, db: Any, key: str, value: Any) -> Any:
        if not self._should_run(key):
            return value
        if not self.check_func(key, value):
            raise NanaSQLiteValidationError(self.error_msg)
        return value


class UniqueHook(BaseHook):
    """Ensures a specific field in a dictionary value is unique across the table."""

    def __init__(self, field: str | Callable[[str, Any], Any], **kwargs: Any):
        super().__init__(**kwargs)
        self.field = field

    def before_write(self, db: Any, key: str, value: Any) -> Any:
        if not self._should_run(key):
            return value

        if callable(self.field):
            check_val = self.field(key, value)
        elif isinstance(value, dict) and self.field in value:
            check_val = value[self.field]
        else:
            return value

        if check_val is None:
            return value

        # O(N) iteration over items to ensure uniqueness
        for k, v in db.items():
            if k == key:
                continue

            if callable(self.field):
                other_val = self.field(k, v)
            elif isinstance(v, dict):
                other_val = v.get(self.field)
            else:
                other_val = None

            if other_val == check_val:
                field_name = self.field.__name__ if callable(self.field) else str(self.field)
                raise NanaSQLiteValidationError(
                    f"Unique constraint violated: '{field_name}' = {check_val} already exists."
                )
        return value


class ForeignKeyHook(BaseHook):
    """Ensures a specific field refers to an existing key in a target table."""

    def __init__(self, field: str | Callable[[str, Any], Any], target_db: Any, **kwargs: Any):
        super().__init__(**kwargs)
        self.field = field
        self.target_db = target_db

    def before_write(self, db: Any, key: str, value: Any) -> Any:
        if not self._should_run(key):
            return value

        if callable(self.field):
            ref_key = self.field(key, value)
        elif isinstance(value, dict) and self.field in value:
            ref_key = value[self.field]
        else:
            return value

        if ref_key is not None and ref_key not in self.target_db:
            field_name = self.field.__name__ if callable(self.field) else str(self.field)
            raise NanaSQLiteValidationError(
                f"Foreign key constraint violated: key '{ref_key}' (from '{field_name}') not found in target table."
            )
        return value


class ValidkitHook(BaseHook):
    """Integration with validkit-py for schema validation."""

    _is_validkit_hook = True

    def __init__(self, schema: Any, coerce: bool = False, **kwargs: Any):
        super().__init__(**kwargs)
        self.schema = schema
        self.coerce = coerce

        if not HAS_VALIDKIT:
            raise ImportError(
                "The 'validkit-py' library is required for validation. "
                "Install it with: pip install nanasqlite[validation]"
            )
        from .compat import validkit_validate

        self._validate_func = validkit_validate

    def before_write(self, db: Any, key: str, value: Any) -> Any:
        if not self._should_run(key):
            return value
        try:
            if self.coerce:
                return self._validate_func(value, self.schema)
            else:
                self._validate_func(value, self.schema)
                return value
        except Exception as exc:
            raise NanaSQLiteValidationError(
                f"Value for key '{key}' failed schema validation: {exc}"
            ) from exc


class PydanticHook(BaseHook):
    """Automatic cast to/from a Pydantic model for seamless integration."""

    def __init__(self, model_class: type, **kwargs: Any):
        super().__init__(**kwargs)
        self.model_class = model_class

    def before_write(self, db: Any, key: str, value: Any) -> Any:
        if not self._should_run(key):
            return value

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

    def after_read(self, db: Any, key: str, value: Any) -> Any:
        if not self._should_run(key):
            return value
        try:
            if hasattr(self.model_class, "model_validate"):
                return self.model_class.model_validate(value)
            elif hasattr(self.model_class, "parse_obj"):
                return self.model_class.parse_obj(value)
        except Exception:
            pass
        return value
