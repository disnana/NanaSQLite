"""
NanaDB: Unified dict-like DB wrapper facade for multiple backends.

現状はSQLiteバックエンド（NanaSQLite/AsyncNanaSQLite）のみを実装し、
将来的にPostgreSQL等へ拡張できる軽量ラッパーを提供します。

使い方:
    >>> from nanasqlite import NanaDB
    >>> db = NanaDB("mydata.db")  # パスだけでもOK（SQLite）
    >>> db["user"] = {"name": "Nana"}
    >>> print(db["user"])  # {'name': 'Nana'}

URL形式も対応（SQLite）:
    >>> db = NanaDB("sqlite:///./mydata.db")

未対応エンジン（例: PostgreSQL）は明示的に NotImplementedError を送出します。
"""

from __future__ import annotations

from typing import Any, Literal
from urllib.parse import urlparse, unquote

from .async_core import AsyncNanaSQLite
from .core import NanaSQLite


def _detect_backend(target: str | None) -> tuple[str, str | None]:
    """Detect backend from a path or URL.

    Returns:
        (backend, normalized_location)

    backend is one of: "sqlite", "postgresql", "unknown"
    normalized_location is a DB path/DSN suitable for the backend (if applicable)
    """
    if not target:
        return "unknown", None

    # If looks like a URL with scheme
    if "://" in target:
        parsed = urlparse(target)
        scheme = (parsed.scheme or "").lower()
        if scheme in {"sqlite", "file"}:  # accept sqlite:///... or file:///...
            # For sqlite URLs, path may be percent-encoded
            path = unquote(parsed.path or "")
            # Special handling for windows drive letters (urlparse keeps leading /)
            if path.startswith("/") and len(path) > 3 and path[2] == ":":
                path = path.lstrip("/")
            return "sqlite", path or ":memory:"
        if scheme in {"postgresql", "postgres"}:
            return "postgresql", target
        return "unknown", target

    # Otherwise treat as filesystem path (SQLite)
    return "sqlite", target


class NanaDB:
    """
    Unified synchronous DB facade.

    現在はSQLite用にNanaSQLiteへフォワードします。PostgreSQL等が指定された場合、
    NotImplementedError を送出して将来拡張の余地を残します。
    """

    def __init__(
        self,
        target: str,
        *,
        table: str = "data",
        bulk_load: bool = False,
        optimize: bool = True,
        cache_size_mb: int = 64,
        strict_sql_validation: bool = True,
        allowed_sql_functions: list[str] | None = None,
        forbidden_sql_functions: list[str] | None = None,
        max_clause_length: int | None = 1000,
        cache_strategy: Literal["unbounded", "lru", "ttl"] = "unbounded",
        cache_size: int | None = None,
        cache_ttl: float | None = None,
        cache_persistence_ttl: bool = False,
        encryption_key: str | bytes | None = None,
        encryption_mode: Literal["aes-gcm", "chacha20", "fernet"] = "aes-gcm",
    ) -> None:
        backend, location = _detect_backend(target)
        self.engine: str = backend

        if backend == "sqlite":
            # Delegate to NanaSQLite
            self._backend = NanaSQLite(
                location or target,
                table=table,
                bulk_load=bulk_load,
                optimize=optimize,
                cache_size_mb=cache_size_mb,
                strict_sql_validation=strict_sql_validation,
                allowed_sql_functions=allowed_sql_functions,
                forbidden_sql_functions=forbidden_sql_functions,
                max_clause_length=max_clause_length,
                cache_strategy=cache_strategy,  # type: ignore[arg-type]
                cache_size=cache_size,
                cache_ttl=cache_ttl,
                cache_persistence_ttl=cache_persistence_ttl,
                encryption_key=encryption_key,
                encryption_mode=encryption_mode,
            )
        elif backend == "postgresql":
            raise NotImplementedError(
                "PostgreSQL backend is not implemented yet. "
                "Please use SQLite (path or sqlite:/// URL)."
            )
        else:
            raise ValueError(f"Unsupported or unknown DB target: {target}")

    # --- Dict-like interface delegation ---
    def __getitem__(self, key: str) -> Any:
        return self._backend[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._backend[key] = value

    def __delitem__(self, key: str) -> None:
        del self._backend[key]

    def __contains__(self, key: object) -> bool:  # type: ignore[override]
        return key in self._backend

    def __iter__(self):
        return iter(self._backend)

    def __len__(self) -> int:
        return len(self._backend)

    # Expose common NanaSQLite API via attribute forwarding
    def __getattr__(self, name: str) -> Any:  # pragma: no cover - simple delegation
        return getattr(self._backend, name)

    def close(self) -> None:
        self._backend.close()


class AsyncNanaDB:
    """
    Unified asynchronous DB facade.

    現在はSQLite用にAsyncNanaSQLiteへフォワードします。PostgreSQL等が指定された場合、
    NotImplementedError を送出します。
    """

    def __init__(
        self,
        target: str,
        *,
        table: str = "data",
        bulk_load: bool = False,
        optimize: bool = True,
        cache_size_mb: int = 64,
        strict_sql_validation: bool = True,
        allowed_sql_functions: list[str] | None = None,
        forbidden_sql_functions: list[str] | None = None,
        max_clause_length: int | None = 1000,
        read_pool_size: int = 0,
        cache_strategy: Literal["unbounded", "lru", "ttl"] = "unbounded",
        cache_size: int | None = None,
        cache_ttl: float | None = None,
        cache_persistence_ttl: bool = False,
        encryption_key: str | bytes | None = None,
        encryption_mode: Literal["aes-gcm", "chacha20", "fernet"] = "aes-gcm",
        max_workers: int = 5,
        thread_name_prefix: str = "AsyncNanaDB",
    ) -> None:
        backend, location = _detect_backend(target)
        self.engine: str = backend

        if backend == "sqlite":
            self._backend = AsyncNanaSQLite(
                location or target,
                table=table,
                bulk_load=bulk_load,
                optimize=optimize,
                cache_size_mb=cache_size_mb,
                max_workers=max_workers,
                thread_name_prefix=thread_name_prefix,
                strict_sql_validation=strict_sql_validation,
                allowed_sql_functions=allowed_sql_functions,
                forbidden_sql_functions=forbidden_sql_functions,
                max_clause_length=max_clause_length,
                read_pool_size=read_pool_size,
                cache_strategy=cache_strategy,  # type: ignore[arg-type]
                cache_size=cache_size,
                cache_ttl=cache_ttl,
                cache_persistence_ttl=cache_persistence_ttl,
                encryption_key=encryption_key,
                encryption_mode=encryption_mode,
            )
        elif backend == "postgresql":
            raise NotImplementedError(
                "PostgreSQL backend is not implemented yet. "
                "Please use SQLite (path or sqlite:/// URL)."
            )
        else:
            raise ValueError(f"Unsupported or unknown DB target: {target}")

    # Attribute delegation to async backend
    def __getattr__(self, name: str) -> Any:  # pragma: no cover - simple delegation
        return getattr(self._backend, name)

    async def aclose(self) -> None:
        await self._backend.aclose()

    # Async context manager passthrough
    async def __aenter__(self):  # pragma: no cover - thin wrapper
        return await self._backend.__aenter__()

    async def __aexit__(self, exc_type, exc, tb):  # pragma: no cover - thin wrapper
        return await self._backend.__aexit__(exc_type, exc, tb)
