"""
NanaSQLite Async Wrapper: Non-blocking async interface for NanaSQLite.
(NanaSQLite 非同期ラッパー: NanaSQLiteのための非ブロッキング非同期インターフェース)

Provides async/await support for all NanaSQLite operations, preventing blocking
in async applications by running database operations in a thread pool.

データベース操作をスレッドプールで実行することにより、非同期アプリケーションでのブロッキングを防ぎ、
すべてのNanaSQLite操作に対してasync/awaitサポートを提供します。

Example:
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

from __future__ import annotations

import asyncio
import logging
import queue
import re
import weakref
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import Any

import apsw

from .cache import CacheType
from .core import IDENTIFIER_PATTERN, NanaSQLite
from .exceptions import NanaSQLiteClosedError, NanaSQLiteDatabaseError


class AsyncNanaSQLite:
    """
    Async wrapper for NanaSQLite with optimized thread pool executor.
    (最適化されたスレッドプールを使用するNanaSQLiteの非同期ラッパー)

    All database operations are executed in a dedicated thread pool executor to prevent
    blocking the async event loop. This allows NanaSQLite to be used safely
    in async applications like FastAPI, aiohttp, etc.

    データベース操作はすべて専用のスレッドプール内で実行され、非同期イベントループのブロックを防ぎます。
    これにより、FastAPIやaiohttpなどの非同期アプリケーションで安全に使用できます。

    The implementation uses a configurable thread pool for optimal concurrency
    and performance in high-load scenarios.

    高負荷なシナリオにおいて最適な並行性とパフォーマンスを実現するため、
    カスタマイズ可能なスレッドプールを使用しています。

    Args:
        db_path: SQLiteデータベースファイルのパス
        table: 使用するテーブル名 (デフォルト: "data")
        bulk_load: Trueの場合、初期化時に全データをメモリに読み込む
        optimize: Trueの場合、WALモードなど高速化設定を適用
        cache_size_mb: SQLiteキャッシュサイズ（MB）、デフォルト64MB
        strict_sql_validation: Trueの場合、未許可の関数等を含むクエリを拒否 (v1.2.0)
        max_clause_length: SQL句の最大長（ReDoS対策、v1.2.0）
        max_workers: スレッドプール内の最大ワーカー数（デフォルト: 5）
        thread_name_prefix: スレッド名のプレフィックス（デフォルト: "AsyncNanaSQLite"）

    Example:
        >>> async with AsyncNanaSQLite("mydata.db") as db:
        ...     await db.aset("config", {"theme": "dark"})
        ...     config = await db.aget("config")
        ...     print(config)

        >>> # 高負荷環境向けの設定
        >>> async with AsyncNanaSQLite("mydata.db", max_workers=10) as db:
        ...     # 並行処理が多い場合に最適化
        ...     results = await asyncio.gather(*[db.aget(f"key_{i}") for i in range(100)])
    """

    def __init__(
        self,
        db_path: str,
        table: str = "data",
        bulk_load: bool = False,
        optimize: bool = True,
        cache_size_mb: int = 64,
        max_workers: int = 5,
        thread_name_prefix: str = "AsyncNanaSQLite",
        strict_sql_validation: bool = True,
        allowed_sql_functions: list[str] | None = None,
        forbidden_sql_functions: list[str] | None = None,
        max_clause_length: int | None = 1000,
        read_pool_size: int = 0,
        cache_strategy: CacheType | str = CacheType.UNBOUNDED,
        cache_size: int | None = None,
    ):
        """
        Args:
            db_path: SQLiteデータベースファイルのパス
            table: 使用するテーブル名 (デフォルト: "data")
            bulk_load: Trueの場合、初期化時に全データをメモリに読み込む
            optimize: Trueの場合、WALモードなど高速化設定を適用
            cache_size_mb: SQLiteキャッシュサイズ（MB）、デフォルト64MB
            max_workers: スレッドプール内の最大ワーカー数（デフォルト: 5）
            thread_name_prefix: スレッド名のプレフィックス（デフォルト: "AsyncNanaSQLite"）
            strict_sql_validation: Trueの場合、未許可の関数等を含むクエリを拒否 (v1.2.0)
            allowed_sql_functions: 追加で許可するSQL関数のリスト (v1.2.0)
            forbidden_sql_functions: 明示的に禁止するSQL関数のリスト (v1.2.0)
            max_clause_length: SQL句の最大長（ReDoS対策）。Noneで制限なし (v1.2.0)
            read_pool_size: 読み取り専用プールサイズ (デフォルト: 0 = 無効) (v1.1.0)
        """
        self._db_path = db_path
        self._table = table
        self._bulk_load = bulk_load
        self._optimize = optimize
        self._cache_size_mb = cache_size_mb
        self._max_workers = max_workers
        self._thread_name_prefix = thread_name_prefix
        self._read_pool_size = read_pool_size
        self._read_pool: queue.Queue | None = None
        self._strict_sql_validation = strict_sql_validation
        self._allowed_sql_functions = allowed_sql_functions
        self._forbidden_sql_functions = forbidden_sql_functions
        self._max_clause_length = max_clause_length
        self._cache_strategy = cache_strategy
        self._cache_size = cache_size
        self._closed = False
        self._child_instances = weakref.WeakSet()  # WeakSetによる弱参照追跡（死んだ参照は自動的にクリーンアップ）
        self._is_connection_owner = True

        # 専用スレッドプールエグゼキューターを作成
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix=thread_name_prefix)
        self._db: NanaSQLite | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._owns_executor = True  # このインスタンスがエグゼキューターを所有

    async def _ensure_initialized(self) -> None:
        """Ensure the underlying sync database is initialized"""
        if self._closed:
            if not getattr(self, "_is_connection_owner", True):
                raise NanaSQLiteClosedError(f"Parent database connection is closed (table: {self._table!r})")
            raise NanaSQLiteClosedError("Database connection is closed")

        if self._db is None:
            # Initialize in thread pool to avoid blocking
            loop = asyncio.get_running_loop()
            self._loop = loop
            self._db = await loop.run_in_executor(
                self._executor,
                lambda: NanaSQLite(
                    self._db_path,
                    table=self._table,
                    bulk_load=self._bulk_load,
                    optimize=self._optimize,
                    cache_size_mb=self._cache_size_mb,
                    strict_sql_validation=self._strict_sql_validation,
                    allowed_sql_functions=self._allowed_sql_functions,
                    forbidden_sql_functions=self._forbidden_sql_functions,
                    max_clause_length=self._max_clause_length,
                    cache_strategy=self._cache_strategy,
                    cache_size=self._cache_size,
                ),
            )

            # Initialize Read-Only Pool if requested
            if self._read_pool_size > 0:
                self._read_pool = queue.Queue(maxsize=self._read_pool_size)

                def _init_pool_connection():
                    # mode=ro (Read-Only) is mandatory for safety
                    flags = apsw.SQLITE_OPEN_READONLY | apsw.SQLITE_OPEN_URI
                    uri_path = f"file:{self._db_path}?mode=ro"

                    for _ in range(self._read_pool_size):
                        conn = apsw.Connection(uri_path, flags=flags)
                        # Apply optimizations to pool connections too (WAL, mmap)
                        # We use a cursor to set PRAGMAs
                        c = conn.cursor()
                        c.execute("PRAGMA journal_mode = WAL")
                        c.execute("PRAGMA synchronous = NORMAL")
                        c.execute("PRAGMA mmap_size = 268435456")
                        # Smaller cache for pool connections (don't hog memory)
                        c.execute("PRAGMA cache_size = -2000")  # ~2MB
                        c.execute("PRAGMA temp_store = MEMORY")
                        self._read_pool.put(conn)

                await loop.run_in_executor(self._executor, _init_pool_connection)

    @contextmanager
    def _read_connection(self):
        """
        Context manager to yield a connection for read-only operations.
        Yields a pooled connection if available, otherwise yields the main DB connection.
        """
        if self._read_pool is None:
            with self._db._lock:
                yield self._db._connection
            return

        # Capture reference locally to ensure safety even if self._read_pool is set to None elsewhere
        pool = self._read_pool
        conn = pool.get()
        try:
            yield conn
        finally:
            pool.put(conn)

    async def _run_in_executor(self, func, *args):
        """Run a synchronous function in the executor"""
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, func, *args)

    # ==================== Async Dict-like Interface ====================

    async def aget(self, key: str, default: Any = None) -> Any:
        """
        非同期でキーの値を取得

        Args:
            key: 取得するキー
            default: キーが存在しない場合のデフォルト値

        Returns:
            キーの値（存在しない場合はdefault）

        Example:
            >>> user = await db.aget("user")
            >>> config = await db.aget("config", {})
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.get, key, default)

    async def aset(self, key: str, value: Any) -> None:
        """
        非同期でキーに値を設定

        Args:
            key: 設定するキー
            value: 設定する値

        Example:
            >>> await db.aset("user", {"name": "Nana", "age": 20})
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.__setitem__, key, value)

    async def adelete(self, key: str) -> None:
        """
        非同期でキーを削除

        Args:
            key: 削除するキー

        Raises:
            KeyError: キーが存在しない場合

        Example:
            >>> await db.adelete("old_data")
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.__delitem__, key)

    async def acontains(self, key: str) -> bool:
        """
        非同期でキーの存在確認

        Args:
            key: 確認するキー

        Returns:
            キーが存在する場合True

        Example:
            >>> if await db.acontains("user"):
            ...     print("User exists")
        """
        await self._ensure_initialized()
        assert self._db is not None
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.__contains__, key)

    async def alen(self) -> int:
        """
        非同期でデータベースの件数を取得

        Returns:
            データベース内のキーの数

        Example:
            >>> count = await db.alen()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.__len__)

    async def akeys(self) -> list[str]:
        """
        非同期で全キーを取得

        Returns:
            全キーのリスト

        Example:
            >>> keys = await db.akeys()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.keys)

    async def avalues(self) -> list[Any]:
        """
        非同期で全値を取得

        Returns:
            全値のリスト

        Example:
            >>> values = await db.avalues()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.values)

    async def aitems(self) -> list[tuple[str, Any]]:
        """
        非同期で全アイテムを取得

        Returns:
            全アイテムのリスト（キーと値のタプル）

        Example:
            >>> items = await db.aitems()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.items)

    async def apop(self, key: str, *args) -> Any:
        """
        非同期でキーを削除して値を返す

        Args:
            key: 削除するキー
            *args: デフォルト値（オプション）

        Returns:
            削除されたキーの値

        Example:
            >>> value = await db.apop("temp_data")
            >>> value = await db.apop("maybe_missing", "default")
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.pop, key, *args)

    async def aupdate(self, mapping: dict = None, **kwargs) -> None:
        """
        非同期で複数のキーを更新

        Args:
            mapping: 更新するキーと値のdict
            **kwargs: キーワード引数として渡す更新

        Example:
            >>> await db.aupdate({"key1": "value1", "key2": "value2"})
            >>> await db.aupdate(key3="value3", key4="value4")
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()

        # Create a wrapper function that captures kwargs
        def update_wrapper():
            self._db.update(mapping, **kwargs)

        await loop.run_in_executor(self._executor, update_wrapper)

    async def aclear(self) -> None:
        """
        非同期で全データを削除

        Example:
            >>> await db.aclear()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.clear)

    async def asetdefault(self, key: str, default: Any = None) -> Any:
        """
        非同期でキーが存在しない場合のみ値を設定

        Args:
            key: キー
            default: デフォルト値

        Returns:
            キーの値（既存または新規設定した値）

        Example:
            >>> value = await db.asetdefault("config", {})
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.setdefault, key, default)

    # ==================== Async Special Methods ====================

    async def load_all(self) -> None:
        """
        非同期で全データを一括ロード

        Example:
            >>> await db.load_all()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.load_all)

    async def refresh(self, key: str = None) -> None:
        """
        非同期でキャッシュを更新

        Args:
            key: 更新するキー（Noneの場合は全キャッシュ）

        Example:
            >>> await db.refresh("user")
            >>> await db.refresh()  # 全キャッシュ更新
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.refresh, key)

    async def is_cached(self, key: str) -> bool:
        """
        非同期でキーがキャッシュ済みか確認

        Args:
            key: 確認するキー

        Returns:
            キャッシュ済みの場合True

        Example:
            >>> cached = await db.is_cached("user")
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.is_cached, key)

    async def batch_update(self, mapping: dict[str, Any]) -> None:
        """
        非同期で一括書き込み（高速）

        Args:
            mapping: 書き込むキーと値のdict

        Example:
            >>> await db.batch_update({
            ...     "key1": "value1",
            ...     "key2": "value2",
            ...     "key3": {"nested": "data"}
            ... })
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.batch_update, mapping)

    async def batch_delete(self, keys: list[str]) -> None:
        """
        非同期で一括削除（高速）

        Args:
            keys: 削除するキーのリスト

        Example:
            >>> await db.batch_delete(["key1", "key2", "key3"])
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.batch_delete, keys)

    async def to_dict(self) -> dict:
        """
        非同期で全データをPython dictとして取得

        Returns:
            全データを含むdict

        Example:
            >>> data = await db.to_dict()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.to_dict)

    async def copy(self) -> dict:
        """
        非同期で浅いコピーを作成

        Returns:
            全データのコピー

        Example:
            >>> data_copy = await db.copy()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.copy)

    async def get_fresh(self, key: str, default: Any = None) -> Any:
        """
        非同期でDBから直接読み込み、キャッシュを更新

        Args:
            key: 取得するキー
            default: キーが存在しない場合のデフォルト値

        Returns:
            DBから取得した最新の値

        Example:
            >>> value = await db.get_fresh("key")
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.get_fresh, key, default)

    async def abatch_get(self, keys: list[str]) -> dict[str, Any]:
        """
        非同期で複数のキーを一度に取得

        Args:
            keys: 取得するキーのリスト

        Returns:
            取得に成功したキーと値の dict

        Example:
            >>> results = await db.abatch_get(["key1", "key2"])
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.batch_get, keys)

    # ==================== Async Pydantic Support ====================

    async def set_model(self, key: str, model: Any) -> None:
        """
        非同期でPydanticモデルを保存

        Args:
            key: 保存するキー
            model: Pydanticモデルのインスタンス

        Example:
            >>> from pydantic import BaseModel
            >>> class User(BaseModel):
            ...     name: str
            ...     age: int
            >>> user = User(name="Nana", age=20)
            >>> await db.set_model("user", user)
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.set_model, key, model)

    async def get_model(self, key: str, model_class: type = None) -> Any:
        """
        非同期でPydanticモデルを取得

        Args:
            key: 取得するキー
            model_class: Pydanticモデルのクラス

        Returns:
            Pydanticモデルのインスタンス

        Example:
            >>> user = await db.get_model("user", User)
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.get_model, key, model_class)

    # ==================== Async SQL Execution ====================

    async def execute(self, sql: str, parameters: tuple | None = None) -> Any:
        """
        非同期でSQLを直接実行

        Args:
            sql: 実行するSQL文
            parameters: SQLのパラメータ

        Returns:
            APSWのCursorオブジェクト

        Example:
            >>> cursor = await db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.execute, sql, parameters)

    async def execute_many(self, sql: str, parameters_list: list[tuple]) -> None:
        """
        非同期でSQLを複数のパラメータで一括実行

        Args:
            sql: 実行するSQL文
            parameters_list: パラメータのリスト

        Example:
            >>> await db.execute_many(
            ...     "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
            ...     [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
            ... )
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.execute_many, sql, parameters_list)

    async def fetch_one(self, sql: str, parameters: tuple = None) -> tuple | None:
        """
        非同期でSQLを実行して1行取得

        Args:
            sql: 実行するSQL文
            parameters: SQLのパラメータ

        Returns:
            1行の結果（tuple）

        Example:
            >>> row = await db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
        """
        await self._ensure_initialized()

        def _fetch_one_impl():
            with self._read_connection() as conn:
                cursor = conn.execute(sql, parameters)
                return cursor.fetchone()

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, _fetch_one_impl)

    async def fetch_all(self, sql: str, parameters: tuple = None) -> list[tuple]:
        """
        非同期でSQLを実行して全行取得

        Args:
            sql: 実行するSQL文
            parameters: SQLのパラメータ

        Returns:
            全行の結果（tupleのリスト）

        Example:
            >>> rows = await db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
        """
        await self._ensure_initialized()

        def _fetch_all_impl():
            with self._read_connection() as conn:
                cursor = conn.execute(sql, parameters)
                return list(cursor)

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, _fetch_all_impl)

    # ==================== Async SQLite Wrapper Functions ====================

    async def create_table(
        self, table_name: str, columns: dict, if_not_exists: bool = True, primary_key: str = None
    ) -> None:
        """
        非同期でテーブルを作成

        Args:
            table_name: テーブル名
            columns: カラム定義のdict
            if_not_exists: Trueの場合、存在しない場合のみ作成
            primary_key: プライマリキーのカラム名

        Example:
            >>> await db.create_table("users", {
            ...     "id": "INTEGER PRIMARY KEY",
            ...     "name": "TEXT NOT NULL",
            ...     "email": "TEXT UNIQUE"
            ... })
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self._executor, self._db.create_table, table_name, columns, if_not_exists, primary_key
        )

    async def create_index(
        self, index_name: str, table_name: str, columns: list[str], unique: bool = False, if_not_exists: bool = True
    ) -> None:
        """
        非同期でインデックスを作成

        Args:
            index_name: インデックス名
            table_name: テーブル名
            columns: インデックスを作成するカラムのリスト
            unique: Trueの場合、ユニークインデックスを作成
            if_not_exists: Trueの場合、存在しない場合のみ作成

        Example:
            >>> await db.create_index("idx_users_email", "users", ["email"], unique=True)
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self._executor, self._db.create_index, index_name, table_name, columns, unique, if_not_exists
        )

    async def query(
        self,
        table_name: str = None,
        columns: list[str] = None,
        where: str = None,
        parameters: tuple = None,
        order_by: str = None,
        limit: int = None,
        strict_sql_validation: bool = None,
        allowed_sql_functions: list[str] = None,
        forbidden_sql_functions: list[str] = None,
        override_allowed: bool = False,
    ) -> list[dict]:
        """
        非同期でSELECTクエリを実行

        Args:
            table_name: テーブル名
            columns: 取得するカラムのリスト
            where: WHERE句の条件
            parameters: WHERE句のパラメータ
            order_by: ORDER BY句
            limit: LIMIT句
            strict_sql_validation: Trueの場合、未許可の関数等を含むクエリを拒否
            allowed_sql_functions: このクエリで一時的に許可するSQL関数のリスト
            forbidden_sql_functions: このクエリで一時的に禁止するSQL関数のリスト
            override_allowed: Trueの場合、インスタンス許可設定を無視

        Returns:
            結果のリスト（各行はdict）

        Example:
            >>> results = await db.query(
            ...     table_name="users",
            ...     columns=["id", "name", "email"],
            ...     where="age > ?",
            ...     parameters=(20,),
            ...     order_by="name ASC",
            ...     limit=10
            ... )
        """
        await self._ensure_initialized()

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self._shared_query_impl,
            table_name,
            columns,
            where,
            parameters,
            order_by,
            limit,
            None,  # offset
            None,  # group_by
            strict_sql_validation,
            allowed_sql_functions,
            forbidden_sql_functions,
            override_allowed,
        )

    async def query_with_pagination(
        self,
        table_name: str = None,
        columns: list[str] = None,
        where: str = None,
        parameters: tuple = None,
        order_by: str = None,
        limit: int = None,
        offset: int = None,
        group_by: str = None,
        strict_sql_validation: bool = None,
        allowed_sql_functions: list[str] = None,
        forbidden_sql_functions: list[str] = None,
        override_allowed: bool = False,
    ) -> list[dict]:
        """
        非同期で拡張されたクエリを実行

        Args:
            table_name: テーブル名
            columns: 取得するカラム
            where: WHERE句
            parameters: パラメータ
            order_by: ORDER BY句
            limit: LIMIT句
            offset: OFFSET句
            group_by: GROUP BY句
            strict_sql_validation: Trueの場合、未許可の関数等を含むクエリを拒否
            allowed_sql_functions: このクエリで一時的に許可するSQL関数のリスト
            forbidden_sql_functions: このクエリで一時的に禁止するSQL関数のリスト
            override_allowed: Trueの場合、インスタンス許可設定を無視

        Returns:
            結果のリスト（各行はdict）

        Example:
            >>> results = await db.query_with_pagination(
            ...     table_name="users",
            ...     columns=["id", "name", "email"],
            ...     where="age > ?",
            ...     parameters=(20,),
            ...     order_by="name ASC",
            ...     limit=10,
            ...     offset=0
            ... )
        """
        if self._db is None:
            await self._ensure_initialized()

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self._shared_query_impl,
            table_name,
            columns,
            where,
            parameters,
            order_by,
            limit,
            offset,
            group_by,
            strict_sql_validation,
            allowed_sql_functions,
            forbidden_sql_functions,
            override_allowed,
        )

    async def table_exists(self, table_name: str) -> bool:
        """
        非同期でテーブルの存在確認

        Args:
            table_name: テーブル名

        Returns:
            存在する場合True

        Example:
            >>> exists = await db.table_exists("users")
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.table_exists, table_name)

    async def list_tables(self) -> list[str]:
        """
        非同期でデータベース内の全テーブル一覧を取得

        Returns:
            テーブル名のリスト

        Example:
            >>> tables = await db.list_tables()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.list_tables)

    async def drop_table(self, table_name: str, if_exists: bool = True) -> None:
        """
        非同期でテーブルを削除

        Args:
            table_name: テーブル名
            if_exists: Trueの場合、存在する場合のみ削除

        Example:
            >>> await db.drop_table("old_table")
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.drop_table, table_name, if_exists)

    async def drop_index(self, index_name: str, if_exists: bool = True) -> None:
        """
        非同期でインデックスを削除

        Args:
            index_name: インデックス名
            if_exists: Trueの場合、存在する場合のみ削除

        Example:
            >>> await db.drop_index("idx_users_email")
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.drop_index, index_name, if_exists)

    async def sql_insert(self, table_name: str, data: dict) -> int:
        """
        非同期でdictから直接INSERT

        Args:
            table_name: テーブル名
            data: カラム名と値のdict

        Returns:
            挿入されたROWID

        Example:
            >>> rowid = await db.sql_insert("users", {
            ...     "name": "Alice",
            ...     "email": "alice@example.com",
            ...     "age": 25
            ... })
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.sql_insert, table_name, data)

    async def sql_update(self, table_name: str, data: dict, where: str, parameters: tuple = None) -> int:
        """
        非同期でdictとwhere条件でUPDATE

        Args:
            table_name: テーブル名
            data: 更新するカラム名と値のdict
            where: WHERE句の条件
            parameters: WHERE句のパラメータ

        Returns:
            更新された行数

        Example:
            >>> count = await db.sql_update("users",
            ...     {"age": 26, "status": "active"},
            ...     "name = ?",
            ...     ("Alice",)
            ... )
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.sql_update, table_name, data, where, parameters)

    async def sql_delete(self, table_name: str, where: str, parameters: tuple = None) -> int:
        """
        非同期でwhere条件でDELETE

        Args:
            table_name: テーブル名
            where: WHERE句の条件
            parameters: WHERE句のパラメータ

        Returns:
            削除された行数

        Example:
            >>> count = await db.sql_delete("users", "age < ?", (18,))
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.sql_delete, table_name, where, parameters)

    async def count(
        self,
        table_name: str = None,
        where: str = None,
        parameters: tuple = None,
        strict_sql_validation: bool = None,
        allowed_sql_functions: list[str] = None,
        forbidden_sql_functions: list[str] = None,
        override_allowed: bool = False,
    ) -> int:
        """
        非同期でレコード数を取得

        Args:
            table_name: テーブル名
            where: WHERE句の条件
            parameters: WHERE句のパラメータ
            strict_sql_validation: Trueの場合、未許可の関数等を含むクエリを拒否
            allowed_sql_functions: このクエリで一時的に許可するSQL関数のリスト
            forbidden_sql_functions: このクエリで一時的に禁止するSQL関数のリスト
            override_allowed: Trueの場合、インスタンス許可設定を無視

        Returns:
            レコード数

        Example:
            >>> count = await db.count("users", "age < ?", (18,))
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self._db.count,
            table_name,
            where,
            parameters,
            strict_sql_validation,
            allowed_sql_functions,
            forbidden_sql_functions,
            override_allowed,
        )

    async def vacuum(self) -> None:
        """
        非同期でデータベースを最適化（VACUUM実行）

        Example:
            >>> await db.vacuum()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.vacuum)

    # ==================== Transaction Control ====================

    async def begin_transaction(self) -> None:
        """
        非同期でトランザクションを開始

        Example:
            >>> await db.begin_transaction()
            >>> try:
            ...     await db.sql_insert("users", {"name": "Alice"})
            ...     await db.sql_insert("users", {"name": "Bob"})
            ...     await db.commit()
            ... except:
            ...     await db.rollback()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.begin_transaction)

    async def commit(self) -> None:
        """
        非同期でトランザクションをコミット

        Example:
            >>> await db.commit()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.commit)

    async def rollback(self) -> None:
        """
        非同期でトランザクションをロールバック

        Example:
            >>> await db.rollback()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self._executor, self._db.rollback)

    async def in_transaction(self) -> bool:
        """
        非同期でトランザクション状態を確認

        Returns:
            bool: トランザクション中の場合True

        Example:
            >>> status = await db.in_transaction()
            >>> print(f"In transaction: {status}")
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self._db.in_transaction)

    def transaction(self):
        """
        非同期トランザクションのコンテキストマネージャ

        Example:
            >>> async with db.transaction():
            ...     await db.sql_insert("users", {"name": "Alice"})
            ...     await db.sql_insert("users", {"name": "Bob"})
            ...     # 自動的にコミット、例外時はロールバック
        """
        return _AsyncTransactionContext(self)

    # ==================== Context Manager Support ====================

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_initialized()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        return False

    async def close(self) -> None:
        """
        非同期でデータベース接続を閉じる

        スレッドプールエグゼキューターもシャットダウンします。

        Example:
            >>> await db.close()
        """
        if self._closed:
            return

        if self._db is not None:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(self._executor, self._db.close)
            self._db = None

        self._closed = True

        # 子インスタンスに通知
        for child in self._child_instances:
            child._mark_parent_closed()
        self._child_instances.clear()

        # Close Read-Only Pool
        if self._read_pool:
            while True:
                conn = None
                try:
                    conn = self._read_pool.get_nowait()
                    conn.close()
                except queue.Empty:
                    # Queue is empty; safe to stop draining
                    break
                except AttributeError as e:
                    # Programming error: conn is not an apsw.Connection
                    logging.getLogger(__name__).error(
                        "AttributeError during pool cleanup - possible programming error: %s (conn=%r)",
                        e,
                        conn,
                    )
                    # continue draining the queue instead of breaking
                except apsw.Error as e:
                    # Ignore close errors during best-effort cleanup but log at warning level
                    logging.getLogger(__name__).warning(
                        "Error while closing read-only NanaSQLite connection %r: %s",
                        conn,
                        e,
                    )
            self._read_pool = None

        # 所有しているエグゼキューターをシャットダウン（ノンブロッキング）
        if self._owns_executor and self._executor is not None:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._executor.shutdown, True)
            self._executor = None

    def _mark_parent_closed(self) -> None:
        """親インスタンスが閉じられた際に呼ばれる"""
        self._closed = True
        self._db = None
        # 子がさらに子を持っている場合も再帰的に閉じる
        for child in self._child_instances:
            child._mark_parent_closed()
        self._child_instances.clear()

    def __repr__(self) -> str:
        if self._db is not None:
            return f"AsyncNanaSQLite({self._db_path!r}, table={self._table!r}, max_workers={self._max_workers}, initialized=True)"
        return f"AsyncNanaSQLite({self._db_path!r}, table={self._table!r}, max_workers={self._max_workers}, initialized=False)"

    # ==================== Sync DB Access (for advanced use) ====================

    @property
    def sync_db(self) -> NanaSQLite | None:
        """
        同期DBインスタンスへのアクセス（上級者向け）

        Warning:
            このプロパティは上級者向けです。
            非同期コンテキストで同期操作を行うとイベントループがブロックされる可能性があります。
            通常は非同期メソッドを使用してください。

        Returns:
            内部のNanaSQLiteインスタンス
        """
        return self._db

    async def table(self, table_name: str) -> AsyncNanaSQLite:
        """
        非同期でサブテーブルのAsyncNanaSQLiteインスタンスを取得

        既に初期化済みの親インスタンスから呼ばれることを想定しています。
        接続とエグゼキューターは親インスタンスと共有されます。

        ⚠️ 重要な注意事項:
        - 同じテーブルに対して複数のインスタンスを作成しないでください
          各インスタンスは独立したキャッシュを持つため、キャッシュ不整合が発生します
        - 推奨: テーブルインスタンスを変数に保存して再利用してください

        非推奨:
            sub1 = await db.table("users")
            sub2 = await db.table("users")  # キャッシュ不整合の原因

        推奨:
            users_db = await db.table("users")
            # users_dbを使い回す

        Args:
            table_name: 取得するサブテーブル名

        Returns:
            指定したテーブルを操作するAsyncNanaSQLiteインスタンス

        Example:
            >>> async with AsyncNanaSQLite("mydata.db", table="main") as db:
            ...     users_db = await db.table("users")
            ...     products_db = await db.table("products")
            ...     await users_db.aset("user1", {"name": "Alice"})
            ...     await products_db.aset("prod1", {"name": "Laptop"})
        """
        # 親インスタンスが初期化済みであることを確認
        if self._db is None:
            await self._ensure_initialized()

        loop = asyncio.get_running_loop()
        sub_db = await loop.run_in_executor(self._executor, self._db.table, table_name)

        # 新しいAsyncNanaSQLiteラッパーを作成（__init__をバイパス）
        async_sub_db = object.__new__(AsyncNanaSQLite)
        async_sub_db._db_path = self._db_path
        async_sub_db._table = table_name
        async_sub_db._bulk_load = self._bulk_load
        async_sub_db._optimize = self._optimize
        async_sub_db._cache_size_mb = self._cache_size_mb
        async_sub_db._max_workers = self._max_workers
        async_sub_db._thread_name_prefix = self._thread_name_prefix + f"_{table_name}"
        async_sub_db._db = sub_db  # 接続を共有した同期版DBを設定
        async_sub_db._closed = False  # クローズ状態を初期化
        async_sub_db._loop = loop  # イベントループを共有
        async_sub_db._executor = self._executor  # 同じエグゼキューターを共有
        async_sub_db._owns_executor = False  # エグゼキューターは所有しない
        async_sub_db._is_connection_owner = False  # 接続の所有権はない
        # セキュリティ関連の設定も親インスタンスから継承する
        async_sub_db._strict_sql_validation = self._strict_sql_validation
        async_sub_db._allowed_sql_functions = self._allowed_sql_functions
        async_sub_db._forbidden_sql_functions = self._forbidden_sql_functions
        async_sub_db._max_clause_length = self._max_clause_length
        # 子インスタンス管理
        async_sub_db._child_instances = weakref.WeakSet()
        self._child_instances.add(async_sub_db)

        # Read-Only Pool は sub-instance では使用しない (シンプルさと後方互換性のため)
        async_sub_db._read_pool_size = 0
        async_sub_db._read_pool = None
        return async_sub_db

    # ==================== Async Method Aliases (Consistency & Stability) ====================
    # For a fully 'a'-prefixed API and compatibility with all tests/benchmarks

    aload_all = load_all
    arefresh = refresh
    ais_cached = is_cached
    abatch_update = batch_update
    abatch_delete = batch_delete
    ato_dict = to_dict
    acopy = copy
    aget_fresh = get_fresh
    aset_model = set_model
    aget_model = get_model
    aexecute = execute
    aexecute_many = execute_many
    afetch_one = fetch_one
    afetch_all = fetch_all
    acreate_table = create_table
    acreate_index = create_index
    aquery = query
    aquery_with_pagination = query_with_pagination
    atable = table
    atable_exists = table_exists
    alist_tables = list_tables
    adrop_table = drop_table
    asql_insert = sql_insert
    asql_update = sql_update
    asql_delete = sql_delete
    acount = count
    avacuum = vacuum

    def _shared_query_impl(
        self,
        table_name: str,
        columns: list[str],
        where: str,
        parameters: tuple,
        order_by: str,
        limit: int,
        offset: int = None,
        group_by: str = None,
        strict_sql_validation: bool = None,
        allowed_sql_functions: list[str] = None,
        forbidden_sql_functions: list[str] = None,
        override_allowed: bool = False,
    ) -> list[dict]:
        """Internal shared implementation for query execution"""
        target_table = self._db._sanitize_identifier(table_name) if table_name else self._db._table

        # Validation (Delegated to Main Instance logic)
        v_args = {
            "strict": strict_sql_validation,
            "allowed": allowed_sql_functions,
            "forbidden": forbidden_sql_functions,
            "override_allowed": override_allowed,
        }

        # table_name is already validated via _sanitize_identifier above
        self._db._validate_expression(where, **v_args, context="where")
        self._db._validate_expression(order_by, **v_args, context="order_by")
        self._db._validate_expression(group_by, **v_args, context="group_by")
        if columns:
            for col in columns:
                self._db._validate_expression(col, **v_args, context="column")

        # Column handling
        if columns is None:
            columns_sql = "*"
        else:
            safe_cols = []
            for col in columns:
                if IDENTIFIER_PATTERN.match(col):
                    safe_cols.append(self._db._sanitize_identifier(col))
                else:
                    safe_cols.append(col)
            columns_sql = ", ".join(safe_cols)

        # Validate limit
        if limit is not None:
            if not isinstance(limit, int):
                raise ValueError(f"limit must be an integer, got {type(limit).__name__}")
            if limit < 0:
                raise ValueError("limit must be non-negative")

        # SQL Construction
        sql = f"SELECT {columns_sql} FROM {target_table}"  # nosec
        if where:
            sql += f" WHERE {where}"
        if group_by:
            sql += f" GROUP BY {group_by}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit is not None:
            sql += f" LIMIT {limit}"
        if offset is not None:
            sql += f" OFFSET {offset}"

        # Execute on pool
        try:
            with self._read_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, parameters)

                # Column name extraction using cursor metadata (robust against AS alias parsing issues)
                try:
                    description = cursor.getdescription()
                    col_names = [col_info[0] for col_info in description]
                except apsw.ExecutionCompleteError:
                    # Fallback for zero-row results (e.g., limit=0)
                    if columns is None:
                        # Get column names from table metadata
                        p_cursor = conn.cursor()
                        p_cursor.execute(f"PRAGMA table_info({target_table})")
                        col_names = [row[1] for row in p_cursor]
                    else:
                        # Extract aliases from provided columns list
                        col_names = []
                        for col in columns:
                            parts = re.split(r"\s+as\s+", col, flags=re.IGNORECASE)
                            if len(parts) > 1:
                                col_names.append(parts[-1].strip().strip('"').strip("'"))
                            else:
                                col_names.append(col.strip())

                # Convert to dict list
                return [dict(zip(col_names, row)) for row in cursor]
        except apsw.Error as e:
            raise NanaSQLiteDatabaseError(f"Failed to execute query: {e}", original_error=e) from e

    get = aget
    contains = acontains
    keys = akeys
    values = avalues
    items = aitems


class _AsyncTransactionContext:
    """非同期トランザクションのコンテキストマネージャ"""

    def __init__(self, db: AsyncNanaSQLite):
        self.db = db

    async def __aenter__(self):
        await self.db.begin_transaction()
        return self.db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.db.commit()
        else:
            await self.db.rollback()
        return False
