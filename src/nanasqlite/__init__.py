"""
NanaSQLite: A dict-like SQLite wrapper with instant persistence and intelligent caching.

Example:
    >>> from nanasqlite import NanaSQLite
    >>> db = NanaSQLite("mydata.db")
    >>> db["user"] = {"name": "Nana", "age": 20}
    >>> print(db["user"])
    {'name': 'Nana', 'age': 20}

Async Example:
    >>> import asyncio
    >>> from nanasqlite import AsyncNanaSQLite
    >>>
    >>> async def main():
    ...     async with AsyncNanaSQLite("mydata.db") as db:
    ...         await db.aset("user", {"name": "Nana", "age": 20})
    ...         user = await db.aget("user")
    ...         print(user)
    >>>
    >>> asyncio.run(main())
"""

from .async_core import AsyncNanaSQLite
from .cache import CacheType
from .core import NanaSQLite
from .exceptions import (
    NanaSQLiteCacheError,
    NanaSQLiteClosedError,
    NanaSQLiteConnectionError,
    NanaSQLiteDatabaseError,
    NanaSQLiteError,
    NanaSQLiteLockError,
    NanaSQLiteTransactionError,
    NanaSQLiteValidationError,
)

__version__ = "1.3.0"
__author__ = "Disnana"
__all__ = [
    "NanaSQLite",
    "AsyncNanaSQLite",
    "CacheType",
    "NanaSQLiteError",
    "NanaSQLiteValidationError",
    "NanaSQLiteDatabaseError",
    "NanaSQLiteTransactionError",
    "NanaSQLiteConnectionError",
    "NanaSQLiteLockError",
    "NanaSQLiteCacheError",
    "NanaSQLiteClosedError",
]
