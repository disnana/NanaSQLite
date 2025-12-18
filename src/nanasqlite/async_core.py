"""
NanaSQLite Async Wrapper: Non-blocking async interface for NanaSQLite.

Provides async/await support for all NanaSQLite operations, preventing blocking
in async applications by running database operations in a thread pool.

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
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Tuple, Type

from .core import NanaSQLite


class AsyncNanaSQLite:
    """
    Async wrapper for NanaSQLite with optimized thread pool executor.
    
    All database operations are executed in a dedicated thread pool executor to prevent
    blocking the async event loop. This allows NanaSQLite to be used safely
    in async applications like FastAPI, aiohttp, etc.
    
    The implementation uses a configurable thread pool for optimal concurrency
    and performance in high-load scenarios.
    
    Args:
        db_path: SQLiteデータベースファイルのパス
        table: 使用するテーブル名 (デフォルト: "data")
        bulk_load: Trueの場合、初期化時に全データをメモリに読み込む
        optimize: Trueの場合、WALモードなど高速化設定を適用
        cache_size_mb: SQLiteキャッシュサイズ（MB）、デフォルト64MB
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
        thread_name_prefix: str = "AsyncNanaSQLite"
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
        """
        self._db_path = db_path
        self._table = table
        self._bulk_load = bulk_load
        self._optimize = optimize
        self._cache_size_mb = cache_size_mb
        self._max_workers = max_workers
        self._thread_name_prefix = thread_name_prefix
        
        # 専用スレッドプールエグゼキューターを作成
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix
        )
        self._db: Optional[NanaSQLite] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._owns_executor = True  # このインスタンスがエグゼキューターを所有
    
    async def _ensure_initialized(self) -> None:
        """Ensure the underlying sync database is initialized"""
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
                    cache_size_mb=self._cache_size_mb
                )
            )
    
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
        return await loop.run_in_executor(
            self._executor,
            self._db.get,
            key,
            default
        )
    
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
        await loop.run_in_executor(
            self._executor,
            self._db.__setitem__,
            key,
            value
        )
    
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
        await loop.run_in_executor(
            self._executor,
            self._db.__delitem__,
            key
        )
    
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
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self._db.__contains__,
            key
        )
    
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
        return await loop.run_in_executor(
            self._executor,
            self._db.__len__
        )
    
    async def akeys(self) -> List[str]:
        """
        非同期で全キーを取得
        
        Returns:
            全キーのリスト
        
        Example:
            >>> keys = await db.akeys()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self._db.keys
        )
    
    async def avalues(self) -> List[Any]:
        """
        非同期で全値を取得
        
        Returns:
            全値のリスト
        
        Example:
            >>> values = await db.avalues()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self._db.values
        )
    
    async def aitems(self) -> List[Tuple[str, Any]]:
        """
        非同期で全アイテムを取得
        
        Returns:
            全アイテムのリスト（キーと値のタプル）
        
        Example:
            >>> items = await db.aitems()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self._db.items
        )
    
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
        return await loop.run_in_executor(
            self._executor,
            self._db.pop,
            key,
            *args
        )
    
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
        
        await loop.run_in_executor(
            self._executor,
            update_wrapper
        )
    
    async def aclear(self) -> None:
        """
        非同期で全データを削除
        
        Example:
            >>> await db.aclear()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self._executor,
            self._db.clear
        )
    
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
        return await loop.run_in_executor(
            self._executor,
            self._db.setdefault,
            key,
            default
        )
    
    # ==================== Async Special Methods ====================
    
    async def load_all(self) -> None:
        """
        非同期で全データを一括ロード
        
        Example:
            >>> await db.load_all()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self._executor,
            self._db.load_all
        )
    
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
        await loop.run_in_executor(
            self._executor,
            self._db.refresh,
            key
        )
    
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
        return await loop.run_in_executor(
            self._executor,
            self._db.is_cached,
            key
        )
    
    async def batch_update(self, mapping: Dict[str, Any]) -> None:
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
        await loop.run_in_executor(
            self._executor,
            self._db.batch_update,
            mapping
        )
    
    async def batch_delete(self, keys: List[str]) -> None:
        """
        非同期で一括削除（高速）
        
        Args:
            keys: 削除するキーのリスト
        
        Example:
            >>> await db.batch_delete(["key1", "key2", "key3"])
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self._executor,
            self._db.batch_delete,
            keys
        )
    
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
        return await loop.run_in_executor(
            self._executor,
            self._db.to_dict
        )
    
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
        return await loop.run_in_executor(
            self._executor,
            self._db.copy
        )
    
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
        return await loop.run_in_executor(
            self._executor,
            self._db.get_fresh,
            key,
            default
        )
    
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
        await loop.run_in_executor(
            self._executor,
            self._db.set_model,
            key,
            model
        )
    
    async def get_model(self, key: str, model_class: Type = None) -> Any:
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
        return await loop.run_in_executor(
            self._executor,
            self._db.get_model,
            key,
            model_class
        )
    
    # ==================== Async SQL Execution ====================
    
    async def execute(self, sql: str, parameters: Optional[Tuple] = None) -> Any:
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
        return await loop.run_in_executor(
            self._executor,
            self._db.execute,
            sql,
            parameters
        )
    
    async def execute_many(self, sql: str, parameters_list: List[tuple]) -> None:
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
        await loop.run_in_executor(
            self._executor,
            self._db.execute_many,
            sql,
            parameters_list
        )
    
    async def fetch_one(self, sql: str, parameters: tuple = None) -> Optional[tuple]:
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
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self._db.fetch_one,
            sql,
            parameters
        )
    
    async def fetch_all(self, sql: str, parameters: tuple = None) -> List[tuple]:
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
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self._db.fetch_all,
            sql,
            parameters
        )
    
    # ==================== Async SQLite Wrapper Functions ====================
    
    async def create_table(
        self,
        table_name: str,
        columns: dict,
        if_not_exists: bool = True,
        primary_key: str = None
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
            self._executor,
            self._db.create_table,
            table_name,
            columns,
            if_not_exists,
            primary_key
        )
    
    async def create_index(
        self,
        index_name: str,
        table_name: str,
        columns: List[str],
        unique: bool = False,
        if_not_exists: bool = True
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
            self._executor,
            self._db.create_index,
            index_name,
            table_name,
            columns,
            unique,
            if_not_exists
        )
    
    async def query(
        self,
        table_name: str = None,
        columns: List[str] = None,
        where: str = None,
        parameters: tuple = None,
        order_by: str = None,
        limit: int = None
    ) -> List[dict]:
        """
        非同期でSELECTクエリを実行
        
        Args:
            table_name: テーブル名
            columns: 取得するカラムのリスト
            where: WHERE句の条件
            parameters: WHERE句のパラメータ
            order_by: ORDER BY句
            limit: LIMIT句
        
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
            self._db.query,
            table_name,
            columns,
            where,
            parameters,
            order_by,
            limit
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
        return await loop.run_in_executor(
            self._executor,
            self._db.table_exists,
            table_name
        )
    
    async def list_tables(self) -> List[str]:
        """
        非同期でデータベース内の全テーブル一覧を取得
        
        Returns:
            テーブル名のリスト
        
        Example:
            >>> tables = await db.list_tables()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self._db.list_tables
        )
    
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
        await loop.run_in_executor(
            self._executor,
            self._db.drop_table,
            table_name,
            if_exists
        )
    
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
        await loop.run_in_executor(
            self._executor,
            self._db.drop_index,
            index_name,
            if_exists
        )
    
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
        return await loop.run_in_executor(
            self._executor,
            self._db.sql_insert,
            table_name,
            data
        )
    
    async def sql_update(
        self,
        table_name: str,
        data: dict,
        where: str,
        parameters: tuple = None
    ) -> int:
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
        return await loop.run_in_executor(
            self._executor,
            self._db.sql_update,
            table_name,
            data,
            where,
            parameters
        )
    
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
        return await loop.run_in_executor(
            self._executor,
            self._db.sql_delete,
            table_name,
            where,
            parameters
        )
    
    async def vacuum(self) -> None:
        """
        非同期でデータベースを最適化（VACUUM実行）
        
        Example:
            >>> await db.vacuum()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self._executor,
            self._db.vacuum
        )
    
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
        await loop.run_in_executor(
            self._executor,
            self._db.begin_transaction
        )

    async def commit(self) -> None:
        """
        非同期でトランザクションをコミット

        Example:
            >>> await db.commit()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self._executor,
            self._db.commit
        )

    async def rollback(self) -> None:
        """
        非同期でトランザクションをロールバック

        Example:
            >>> await db.rollback()
        """
        await self._ensure_initialized()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self._executor,
            self._db.rollback
        )

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
        return await loop.run_in_executor(
            self._executor,
            self._db.in_transaction
        )

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
        if self._db is not None:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                self._executor,
                self._db.close
            )
            self._db = None
        
        # 所有しているエグゼキューターをシャットダウン（ノンブロッキング）
        if self._owns_executor and self._executor is not None:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._executor.shutdown, True)
            self._executor = None
    
    def __repr__(self) -> str:
        if self._db is not None:
            return f"AsyncNanaSQLite({self._db_path!r}, table={self._table!r}, max_workers={self._max_workers}, initialized=True)"
        return f"AsyncNanaSQLite({self._db_path!r}, table={self._table!r}, max_workers={self._max_workers}, initialized=False)"
    
    # ==================== Sync DB Access (for advanced use) ====================
    
    @property
    def sync_db(self) -> Optional[NanaSQLite]:
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
        sub_db = await loop.run_in_executor(
            self._executor,
            self._db.table,
            table_name
        )

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
        async_sub_db._loop = loop  # イベントループを共有
        async_sub_db._executor = self._executor  # 同じエグゼキューターを共有
        async_sub_db._owns_executor = False  # エグゼキューターは所有しない
        return async_sub_db


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

