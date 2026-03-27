from __future__ import annotations

from typing import Any, Protocol


class NanaHook(Protocol):
    """
    Protocol for NanaSQLite hooks that can intercept and mutate read/write/delete operations.
    """

    def before_write(self, db: Any, key: str, value: Any) -> Any:
        """Called before writing. Can validate or mutate the value."""
        return value

    def after_read(self, db: Any, key: str, value: Any) -> Any:
        """Called after reading. Can mutate the value."""
        return value

    def before_delete(self, db: Any, key: str) -> None:
        """Called before deleting. Can abort the deletion."""
        pass
