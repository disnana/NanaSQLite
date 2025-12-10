"""
NanaSQLite: A dict-like SQLite wrapper with instant persistence and intelligent caching.

Example:
    >>> from nanasqlite import NanaSQLite
    >>> db = NanaSQLite("mydata.db")
    >>> db["user"] = {"name": "Nana", "age": 20}
    >>> print(db["user"])
    {'name': 'Nana', 'age': 20}
"""

from .core import NanaSQLite

__version__ = "1.0.3rc4"
__author__ = "Disnana"
__all__ = ["NanaSQLite"]
