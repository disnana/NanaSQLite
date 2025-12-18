"""
NanaSQLite: APSW SQLite-backed dict wrapper with memory caching.

通常のPython dictをラップし、操作時にSQLite永続化処理を行う。
- 書き込み: 即時SQLiteへ永続化
- 読み込み: デフォルトは遅延ロード（使用時）、一度読み込んだらメモリ管理
- 一括ロード: bulk_load=Trueで起動時に全データをメモリに展開
"""

from __future__ import annotations

import json
import re
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, Type, Union
from collections.abc import MutableMapping
import apsw
import threading
import weakref

from .exceptions import (
    NanaSQLiteError,
    NanaSQLiteValidationError,
    NanaSQLiteDatabaseError,
    NanaSQLiteTransactionError,
    NanaSQLiteConnectionError,
    NanaSQLiteLockError,
)


class NanaSQLite(MutableMapping):
    """
    APSW SQLite-backed dict wrapper.
    
    内部でPython dictを保持し、操作時にSQLiteとの同期を行う。
    
    Args:
        db_path: SQLiteデータベースファイルのパス
        table: 使用するテーブル名 (デフォルト: "data")
        bulk_load: Trueの場合、初期化時に全データをメモリに読み込む
    
    Example:
        >>> db = NanaSQLite("mydata.db")
        >>> db["user"] = {"name": "Nana", "age": 20}
        >>> print(db["user"])
        {'name': 'Nana', 'age': 20}
    """
    
    def __init__(self, db_path: str, table: str = "data", bulk_load: bool = False,
                 optimize: bool = True, cache_size_mb: int = 64,
                 _shared_connection: Optional[apsw.Connection] = None,
                 _shared_lock: Optional[threading.RLock] = None):
        """
        Args:
            db_path: SQLiteデータベースファイルのパス
            table: 使用するテーブル名 (デフォルト: "data")
            bulk_load: Trueの場合、初期化時に全データをメモリに読み込む
            optimize: Trueの場合、WALモードなど高速化設定を適用
            cache_size_mb: SQLiteキャッシュサイズ（MB）、デフォルト64MB
            _shared_connection: 内部用：共有する接続（table()メソッドで使用）
            _shared_lock: 内部用：共有するロック（table()メソッドで使用）
        """
        self._db_path: str = db_path
        self._table: str = table
        self._data: Dict[str, Any] = {}  # 内部dict（メモリキャッシュ）
        self._cached_keys: Set[str] = set()  # キャッシュ済みキーの追跡
        self._all_loaded: bool = False  # 全データ読み込み済みフラグ

        # トランザクション状態管理
        self._in_transaction: bool = False  # トランザクション中かどうか
        self._transaction_depth: int = 0  # ネストレベル（警告用）

        # 子インスタンスの追跡（リソース管理用）
        self._child_instances: List[weakref.ref] = []  # 弱参照で追跡
        self._is_closed: bool = False  # 接続が閉じられたか
        self._parent_closed: bool = False  # 親接続が閉じられたか

        # 接続とロックの共有または新規作成
        if _shared_connection is not None:
            # 接続を共有（table()メソッドから呼ばれた場合）
            self._connection: apsw.Connection = _shared_connection
            self._lock = _shared_lock if _shared_lock is not None else threading.RLock()
            self._is_connection_owner = False  # 接続の所有者ではない
        else:
            # 新規接続を作成（通常の初期化）
            try:
                self._connection: apsw.Connection = apsw.Connection(db_path)
            except apsw.Error as e:
                raise NanaSQLiteConnectionError(f"Failed to connect to database: {e}") from e
            self._lock = threading.RLock()
            self._is_connection_owner = True  # 接続の所有者

            # 高速化設定（接続の所有者のみ）
            if optimize:
                self._apply_optimizations(cache_size_mb)

        # テーブル作成
        with self._lock:
            self._connection.execute(f"""
                CREATE TABLE IF NOT EXISTS {self._table} (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

        # 一括ロード
        if bulk_load:
            self.load_all()
    
    def _apply_optimizations(self, cache_size_mb: int = 64) -> None:
        """
        APSWの高速化設定を適用
        
        - WALモード: 書き込み並行性向上、30ms+ -> 1ms以下に改善
        - synchronous=NORMAL: 安全性を保ちつつ高速化
        - mmap: メモリマップドI/Oで読み込み高速化
        - cache_size: SQLiteのメモリキャッシュ増加
        - temp_store=MEMORY: 一時テーブルをメモリに
        """
        cursor = self._connection.cursor()
        
        # WALモード（Write-Ahead Logging）- 書き込み高速化の核心
        cursor.execute("PRAGMA journal_mode = WAL")
        
        # synchronous=NORMAL: WALモードでは安全かつ高速
        cursor.execute("PRAGMA synchronous = NORMAL")
        
        # メモリマップドI/O（256MB）- 読み込み高速化
        cursor.execute("PRAGMA mmap_size = 268435456")
        
        # キャッシュサイズ（負の値=KB単位）
        cache_kb = cache_size_mb * 1024
        cursor.execute(f"PRAGMA cache_size = -{cache_kb}")
        
        # 一時テーブルをメモリに
        cursor.execute("PRAGMA temp_store = MEMORY")
        
        # ページサイズ最適化（新規DBのみ効果あり）
        cursor.execute("PRAGMA page_size = 4096")
    
    @staticmethod
    def _sanitize_identifier(identifier: str) -> str:
        """
        SQLiteの識別子（テーブル名、カラム名など）を検証
        
        Args:
            identifier: 検証する識別子
        
        Returns:
            検証済み識別子（ダブルクォートで囲まれる）
        
        Raises:
            NanaSQLiteValidationError: 識別子が無効な場合

        Note:
            SQLiteの識別子は以下をサポート:
            - 英数字とアンダースコア
            - 数字で開始しない
            - SQLキーワードも引用符で囲めば使用可能
        """
        if not identifier:
            raise NanaSQLiteValidationError("Identifier cannot be empty")

        # 基本的な検証: 英数字とアンダースコアのみ許可
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            raise NanaSQLiteValidationError(
                f"Invalid identifier '{identifier}': must start with letter or underscore "
                "and contain only alphanumeric characters and underscores"
            )
        
        # SQLiteではダブルクォートで囲むことで識別子をエスケープ
        return f'"{identifier}"'
    
    # ==================== Private Methods ====================
    
    def _check_connection(self) -> None:
        """
        接続が有効かチェック

        Raises:
            NanaSQLiteConnectionError: 接続が閉じられている、または親が閉じられている場合
        """
        if self._is_closed:
            raise NanaSQLiteConnectionError("Database connection is closed")
        if self._parent_closed:
            raise NanaSQLiteConnectionError(
                "Parent database connection is closed. "
                "This table instance cannot be used anymore."
            )

    def _mark_parent_closed(self) -> None:
        """
        親インスタンスから呼ばれ、親が閉じられたことをマークする
        """
        self._parent_closed = True

    def _serialize(self, value: Any) -> str:
        """値をJSON文字列にシリアライズ"""
        return json.dumps(value, ensure_ascii=False)
    
    def _deserialize(self, value: str) -> Any:
        """JSON文字列を値にデシリアライズ"""
        return json.loads(value)
    
    def _write_to_db(self, key: str, value: Any) -> None:
        """即時書き込み: SQLiteに値を保存"""
        serialized = self._serialize(value)
        with self._lock:
            self._connection.execute(
                f"INSERT OR REPLACE INTO {self._table} (key, value) VALUES (?, ?)",
                (key, serialized)
            )

    def _read_from_db(self, key: str) -> Optional[Any]:
        """SQLiteから値を読み込み"""
        with self._lock:
            cursor = self._connection.execute(
                f"SELECT value FROM {self._table} WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._deserialize(row[0])

    def _delete_from_db(self, key: str) -> None:
        """SQLiteから値を削除"""
        with self._lock:
            self._connection.execute(
                f"DELETE FROM {self._table} WHERE key = ?",
                (key,)
            )

    def _get_all_keys_from_db(self) -> list:
        """SQLiteから全キーを取得"""
        with self._lock:
            cursor = self._connection.execute(
                f"SELECT key FROM {self._table}"
            )
            return [row[0] for row in cursor]

    def _ensure_cached(self, key: str) -> bool:
        """
        キーがキャッシュにない場合、DBから読み込む（遅延ロード）
        Returns: キーが存在するかどうか
        """
        if key in self._cached_keys:
            return key in self._data
        
        # DBから読み込み
        value = self._read_from_db(key)
        self._cached_keys.add(key)
        
        if value is not None:
            self._data[key] = value
            return True
        return False
    
    # ==================== Dict Interface ====================
    
    def __getitem__(self, key: str) -> Any:
        """dict[key] - 遅延ロード後、メモリから取得"""
        if self._ensure_cached(key):
            return self._data[key]
        raise KeyError(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """dict[key] = value - 即時書き込み + メモリ更新"""
        self._check_connection()
        # メモリ更新
        self._data[key] = value
        self._cached_keys.add(key)
        # 即時書き込み
        self._write_to_db(key, value)
    
    def __delitem__(self, key: str) -> None:
        """del dict[key] - 即時削除"""
        if not self._ensure_cached(key):
            raise KeyError(key)
        # メモリから削除
        del self._data[key]
        self._cached_keys.add(key)  # 削除済みとしてマーク
        # DBから削除
        self._delete_from_db(key)
    
    def __contains__(self, key: str) -> bool:
        """
        key in dict - キーの存在確認
        
        キャッシュにある場合はO(1)、ない場合は軽量なEXISTSクエリを使用。
        存在確認のみの場合、value全体を読み込まないため高速。
        """
        if key in self._cached_keys:
            return key in self._data
        
        # 軽量な存在確認クエリ（valueを読み込まない）
        with self._lock:
            cursor = self._connection.execute(
                f"SELECT 1 FROM {self._table} WHERE key = ? LIMIT 1", (key,)
            )
            exists = cursor.fetchone() is not None

        if exists:
            # 存在する場合のみキャッシュに読み込む（遅延ロード）
            self._ensure_cached(key)
        else:
            # 存在しないこともキャッシュ（次回の高速化のため）
            self._cached_keys.add(key)
        
        return exists
    
    def __len__(self) -> int:
        """len(dict) - DBの実際の件数を返す"""
        with self._lock:
            cursor = self._connection.execute(
                f"SELECT COUNT(*) FROM {self._table}"
            )
            return cursor.fetchone()[0]

    def __iter__(self) -> Iterator[str]:
        """for key in dict"""
        return iter(self.keys())
    
    def __repr__(self) -> str:
        return f"NanaSQLite({self._db_path!r}, table={self._table!r}, cached={len(self._cached_keys)})"
    
    # ==================== Dict Methods ====================
    
    def keys(self) -> list:
        """全キーを取得（DBから）"""
        return self._get_all_keys_from_db()
    
    def values(self) -> list:
        """全値を取得（一括ロードしてからメモリから）"""
        self._check_connection()
        self.load_all()
        return list(self._data.values())
    
    def items(self) -> list:
        """全アイテムを取得（一括ロードしてからメモリから）"""
        self.load_all()
        return list(self._data.items())
    
    def get(self, key: str, default: Any = None) -> Any:
        """dict.get(key, default)"""
        if self._ensure_cached(key):
            return self._data[key]
        return default
    
    def get_fresh(self, key: str, default: Any = None) -> Any:
        """
        DBから直接読み込み、キャッシュを更新して値を返す
        
        キャッシュをバイパスしてDBから最新の値を取得する。
        `execute()`でDBを直接変更した後などに使用。
        
        通常の`get()`よりオーバーヘッドがあるため、
        キャッシュとDBの不整合が想定される場合のみ使用推奨。
        
        Args:
            key: 取得するキー
            default: キーが存在しない場合のデフォルト値
        
        Returns:
            DBから取得した最新の値（存在しない場合はdefault）
        
        Example:
            >>> db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new"', "key"))
            >>> value = db.get_fresh("key")  # DBから最新値を取得
        """
        # DBから直接読み込み（_read_from_dbを使用してオーバーヘッド最小化）
        value = self._read_from_db(key)
        
        if value is not None:
            # キャッシュを更新
            self._data[key] = value
            self._cached_keys.add(key)
            return value
        else:
            # 存在しない場合はキャッシュからも削除
            self._data.pop(key, None)
            self._cached_keys.add(key)  # 「存在しない」ことをキャッシュ
            return default
    
    def pop(self, key: str, *args) -> Any:
        """dict.pop(key[, default])"""
        self._check_connection()
        if self._ensure_cached(key):
            value = self._data.pop(key)
            self._delete_from_db(key)
            return value
        if args:
            return args[0]
        raise KeyError(key)
    
    def update(self, mapping: dict = None, **kwargs) -> None:
        """dict.update(mapping) - 一括更新"""
        if mapping:
            for key, value in mapping.items():
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value
    
    def clear(self) -> None:
        """dict.clear() - 全削除"""
        self._data.clear()
        self._cached_keys.clear()
        self._all_loaded = False
        with self._lock:
            self._connection.execute(f"DELETE FROM {self._table}")

    def setdefault(self, key: str, default: Any = None) -> Any:
        """dict.setdefault(key, default)"""
        if self._ensure_cached(key):
            return self._data[key]
        self[key] = default
        return default
    
    # ==================== Special Methods ====================
    
    def load_all(self) -> None:
        """一括読み込み: 全データをメモリに展開"""
        if self._all_loaded:
            return

        with self._lock:
            cursor = self._connection.execute(
                f"SELECT key, value FROM {self._table}"
            )
            rows = list(cursor)  # ロック内でフェッチ

        for key, value in rows:
            self._data[key] = self._deserialize(value)
            self._cached_keys.add(key)
        
        self._all_loaded = True
    
    def refresh(self, key: str = None) -> None:
        """
        キャッシュを更新（DBから再読み込み）
        
        Args:
            key: 特定のキーのみ更新。Noneの場合は全キャッシュをクリアして再読み込み
        """
        if key is not None:
            self._cached_keys.discard(key)
            if key in self._data:
                del self._data[key]
            self._ensure_cached(key)
        else:
            self._data.clear()
            self._cached_keys.clear()
            self._all_loaded = False
    
    def is_cached(self, key: str) -> bool:
        """キーがキャッシュ済みかどうか"""
        return key in self._cached_keys
    
    def batch_update(self, mapping: Dict[str, Any]) -> None:
        """
        一括書き込み（トランザクション + executemany使用で超高速）
        
        大量のデータを一度に書き込む場合、通常のupdateより10-100倍高速。
        v1.0.3rc5でexecutemanyによる最適化を追加。
        
        Args:
            mapping: 書き込むキーと値のdict
        
        Returns:
            None
        
        Example:
            >>> db.batch_update({"key1": "value1", "key2": "value2", ...})
        """
        if not mapping:
            return  # 空の場合は何もしない
        
        cursor = self._connection.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        try:
            # 事前にシリアライズしてexecutemany用のタプルリストを作成
            params = [(key, self._serialize(value)) for key, value in mapping.items()]
            cursor.executemany(
                f"INSERT OR REPLACE INTO {self._table} (key, value) VALUES (?, ?)",
                params
            )
            # キャッシュ更新
            for key, value in mapping.items():
                self._data[key] = value
                self._cached_keys.add(key)
            cursor.execute("COMMIT")
        except Exception:
            cursor.execute("ROLLBACK")
            raise
    
    def batch_delete(self, keys: List[str]) -> None:
        """
        一括削除（トランザクション + executemany使用で高速）
        
        v1.0.3rc5でexecutemanyによる最適化を追加。
        
        Args:
            keys: 削除するキーのリスト
        
        Returns:
            None
        """
        self._check_connection()
        if not keys:
            return  # 空の場合は何もしない
        
        cursor = self._connection.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        try:
            # executemany用のタプルリストを作成
            params = [(key,) for key in keys]
            cursor.executemany(
                f"DELETE FROM {self._table} WHERE key = ?",
                params
            )
            # キャッシュ更新
            for key in keys:
                self._data.pop(key, None)
                self._cached_keys.discard(key)
            cursor.execute("COMMIT")
        except Exception:
            cursor.execute("ROLLBACK")
            raise
    
    def to_dict(self) -> dict:
        """全データをPython dictとして取得"""
        self._check_connection()
        self.load_all()
        return dict(self._data)
    
    def copy(self) -> dict:
        """浅いコピーを作成（標準dictを返す）"""
        return self.to_dict()
    
    def close(self) -> None:
        """
        データベース接続を閉じる

        注意: table()メソッドで作成されたインスタンスは接続を共有しているため、
        接続の所有者（最初に作成されたインスタンス）のみが接続を閉じます。

        Raises:
            NanaSQLiteTransactionError: トランザクション中にクローズを試みた場合
        """
        if self._is_closed:
            return  # 既に閉じられている場合は何もしない

        if self._in_transaction:
            raise NanaSQLiteTransactionError(
                "Cannot close connection while transaction is in progress. "
                "Please commit or rollback first."
            )

        # 子インスタンスに通知
        for child_ref in self._child_instances:
            child = child_ref()
            if child is not None:
                child._mark_parent_closed()

        self._is_closed = True

        if self._is_connection_owner:
            try:
                self._connection.close()
            except apsw.Error as e:
                # 接続クローズの失敗は警告に留める
                import warnings
                warnings.warn(f"Failed to close database connection: {e}")

    def __enter__(self):
        """コンテキストマネージャ対応"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャ対応"""
        self.close()
        return False
    
    # ==================== Pydantic Support ====================
    
    def set_model(self, key: str, model: Any) -> None:
        """
        Pydanticモデルを保存
        
        Pydanticモデル（BaseModelを継承したクラス）をシリアライズして保存。
        model_dump()メソッドを使用してdictに変換し、モデルのクラス情報も保存。
        
        Args:
            key: 保存するキー
            model: Pydanticモデルのインスタンス
        
        Example:
            >>> from pydantic import BaseModel
            >>> class User(BaseModel):
            ...     name: str
            ...     age: int
            >>> user = User(name="Nana", age=20)
            >>> db.set_model("user", user)
        """
        try:
            # Pydanticモデルかチェック (model_dump メソッドの存在で判定)
            if hasattr(model, 'model_dump'):
                data = {
                    '__pydantic_model__': f"{model.__class__.__module__}.{model.__class__.__qualname__}",
                    '__pydantic_data__': model.model_dump()
                }
                self[key] = data
            else:
                raise TypeError(f"Object of type {type(model)} is not a Pydantic model")
        except Exception as e:
            raise TypeError(f"Failed to serialize Pydantic model: {e}")
    
    def get_model(self, key: str, model_class: Type = None) -> Any:
        """
        Pydanticモデルを取得
        
        保存されたPydanticモデルをデシリアライズして復元。
        model_classが指定されていない場合は、保存時のクラス情報を使用。
        
        Args:
            key: 取得するキー
            model_class: Pydanticモデルのクラス（Noneの場合は自動検出を試みる）
        
        Returns:
            Pydanticモデルのインスタンス
        
        Example:
            >>> user = db.get_model("user", User)
            >>> print(user.name)  # "Nana"
        """
        data = self[key]
        
        if isinstance(data, dict) and '__pydantic_model__' in data and '__pydantic_data__' in data:
            if model_class is None:
                # 自動検出は複雑なため、model_classを推奨
                raise ValueError("model_class must be provided for get_model()")
            
            # Pydanticモデルとして復元
            try:
                return model_class(**data['__pydantic_data__'])
            except Exception as e:
                raise ValueError(f"Failed to deserialize Pydantic model: {e}")
        elif model_class is not None:
            # 通常のdictをPydanticモデルに変換
            try:
                return model_class(**data)
            except Exception as e:
                raise ValueError(f"Failed to create Pydantic model from data: {e}")
        else:
            raise ValueError("Data is not a Pydantic model and no model_class provided")
    
    # ==================== Direct SQL Execution ====================
    
    def execute(self, sql: str, parameters: Optional[Tuple] = None) -> apsw.Cursor:
        """
        SQLを直接実行
        
        任意のSQL文を実行できる。SELECT、INSERT、UPDATE、DELETEなど。
        パラメータバインディングをサポート（SQLインジェクション対策）。
        
        .. warning::
            このメソッドで直接デフォルトテーブル（data）を操作した場合、
            内部キャッシュ（_data）と不整合が発生する可能性があります。
            キャッシュを更新するには `refresh()` を呼び出してください。
        
        Args:
            sql: 実行するSQL文
            parameters: SQLのパラメータ（?プレースホルダー用）
        
        Returns:
            APSWのCursorオブジェクト（結果の取得に使用）
        
        Raises:
            NanaSQLiteConnectionError: 接続が閉じられている場合
            NanaSQLiteDatabaseError: SQL実行エラー

        Example:
            >>> cursor = db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
            >>> for row in cursor:
            ...     print(row)
            
            # キャッシュ更新が必要な場合:
            >>> db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new"', "key"))
            >>> db.refresh("key")  # キャッシュを更新
        """
        self._check_connection()

        try:
            with self._lock:
                if parameters is None:
                    return self._connection.execute(sql)
                else:
                    return self._connection.execute(sql, parameters)
        except apsw.Error as e:
            raise NanaSQLiteDatabaseError(f"Failed to execute SQL: {e}", original_error=e) from e

    def execute_many(self, sql: str, parameters_list: List[tuple]) -> None:
        """
        SQLを複数のパラメータで一括実行
        
        同じSQL文を複数のパラメータセットで実行（トランザクション使用）。
        大量のINSERTやUPDATEを高速に実行できる。
        
        Args:
            sql: 実行するSQL文
            parameters_list: パラメータのリスト
        
        Example:
            >>> db.execute_many(
            ...     "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
            ...     [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
            ... )
        """
        with self._lock:
            cursor = self._connection.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            try:
                for parameters in parameters_list:
                    cursor.execute(sql, parameters)
                cursor.execute("COMMIT")
            except apsw.Error:
                cursor.execute("ROLLBACK")
                raise

    def fetch_one(self, sql: str, parameters: tuple = None) -> Optional[tuple]:
        """
        SQLを実行して1行取得
        
        Args:
            sql: 実行するSQL文
            parameters: SQLのパラメータ
        
        Returns:
            1行の結果（tuple）、結果がない場合はNone
        
        Example:
            >>> row = db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
            >>> print(row[0])
        """
        cursor = self.execute(sql, parameters)
        return cursor.fetchone()
    
    def fetch_all(self, sql: str, parameters: tuple = None) -> List[tuple]:
        """
        SQLを実行して全行取得
        
        Args:
            sql: 実行するSQL文
            parameters: SQLのパラメータ
        
        Returns:
            全行の結果（tupleのリスト）
        
        Example:
            >>> rows = db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
            >>> for key, value in rows:
            ...     print(key, value)
        """
        cursor = self.execute(sql, parameters)
        return cursor.fetchall()
    
    # ==================== SQLite Wrapper Functions ====================
    
    def create_table(self, table_name: str, columns: dict, 
                    if_not_exists: bool = True, primary_key: str = None) -> None:
        """
        テーブルを作成
        
        Args:
            table_name: テーブル名
            columns: カラム定義のdict（カラム名: SQL型）
            if_not_exists: Trueの場合、存在しない場合のみ作成
            primary_key: プライマリキーのカラム名（Noneの場合は指定なし）
        
        Example:
            >>> db.create_table("users", {
            ...     "id": "INTEGER PRIMARY KEY",
            ...     "name": "TEXT NOT NULL",
            ...     "email": "TEXT UNIQUE",
            ...     "age": "INTEGER"
            ... })
            >>> db.create_table("posts", {
            ...     "id": "INTEGER",
            ...     "title": "TEXT",
            ...     "content": "TEXT"
            ... }, primary_key="id")
        """
        if_not_exists_clause = "IF NOT EXISTS " if if_not_exists else ""
        safe_table_name = self._sanitize_identifier(table_name)
        
        column_defs = []
        for col_name, col_type in columns.items():
            safe_col_name = self._sanitize_identifier(col_name)
            column_defs.append(f"{safe_col_name} {col_type}")
        
        if primary_key:
            safe_pk = self._sanitize_identifier(primary_key)
            if not any(primary_key.upper() in col.upper() and "PRIMARY KEY" in col.upper() 
                                       for col in column_defs):
                column_defs.append(f"PRIMARY KEY ({safe_pk})")
        
        columns_sql = ", ".join(column_defs)
        sql = f"CREATE TABLE {if_not_exists_clause}{safe_table_name} ({columns_sql})"
        
        self.execute(sql)
    
    def create_index(self, index_name: str, table_name: str, columns: List[str],
                    unique: bool = False, if_not_exists: bool = True) -> None:
        """
        インデックスを作成
        
        Args:
            index_name: インデックス名
            table_name: テーブル名
            columns: インデックスを作成するカラムのリスト
            unique: Trueの場合、ユニークインデックスを作成
            if_not_exists: Trueの場合、存在しない場合のみ作成
        
        Example:
            >>> db.create_index("idx_users_email", "users", ["email"], unique=True)
            >>> db.create_index("idx_posts_user", "posts", ["user_id", "created_at"])
        """
        unique_clause = "UNIQUE " if unique else ""
        if_not_exists_clause = "IF NOT EXISTS " if if_not_exists else ""
        safe_index_name = self._sanitize_identifier(index_name)
        safe_table_name = self._sanitize_identifier(table_name)
        safe_columns = [self._sanitize_identifier(col) for col in columns]
        columns_sql = ", ".join(safe_columns)
        
        sql = f"CREATE {unique_clause}INDEX {if_not_exists_clause}{safe_index_name} ON {safe_table_name} ({columns_sql})"
        self.execute(sql)
    
    def query(self, table_name: str = None, columns: List[str] = None,
             where: str = None, parameters: tuple = None,
             order_by: str = None, limit: int = None) -> List[dict]:
        """
        シンプルなSELECTクエリを実行
        
        Args:
            table_name: テーブル名（Noneの場合はデフォルトテーブル）
            columns: 取得するカラムのリスト（Noneの場合は全カラム）
            where: WHERE句の条件（パラメータバインディング使用推奨）
            parameters: WHERE句のパラメータ
            order_by: ORDER BY句
            limit: LIMIT句
        
        Returns:
            結果のリスト（各行はdict）
        
        Example:
            >>> # デフォルトテーブルから全データ取得
            >>> results = db.query()
            
            >>> # 条件付き検索
            >>> results = db.query(
            ...     table_name="users",
            ...     columns=["id", "name", "email"],
            ...     where="age > ?",
            ...     parameters=(20,),
            ...     order_by="name ASC",
            ...     limit=10
            ... )
        """
        if table_name is None:
            table_name = self._table
        
        safe_table_name = self._sanitize_identifier(table_name)
        
        # カラム指定
        if columns is None:
            columns_sql = "*"
            # カラム名は後でPRAGMAから取得
        else:
            # Allow complex column expressions (functions, aliases) with validation
            safe_columns = []
            for col in columns:
                # Accept simple identifiers, or expressions like COUNT(*), MAX(age), etc.
                # Allow: alphanumeric, underscore, *, spaces, parentheses, commas, periods, AS clauses
                # Disallow dangerous patterns: semicolon, --, /*, */, DROP, DELETE, INSERT, UPDATE, etc.
                if re.match(r'^[\w\*\s\(\),\.]+(?:\s+as\s+\w+)?$', col, re.IGNORECASE):
                    # Additional check: block SQL keywords that could be dangerous (using word boundaries)
                    if not re.search(r'(;|--|/\*|\*/)|\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE)\b', col, re.IGNORECASE):
                        safe_columns.append(col)
                    else:
                        raise ValueError(f"Invalid or dangerous column expression: {col}")
                else:
                    raise ValueError(f"Invalid column expression: {col}")
            columns_sql = ", ".join(safe_columns)
        
        # Validate limit is an integer and non-negative if provided
        if limit is not None:
            if not isinstance(limit, int):
                raise ValueError(f"limit must be an integer, got {type(limit).__name__}")
            if limit < 0:
                raise ValueError("limit must be non-negative")
        
        # SQL構築
        sql = f"SELECT {columns_sql} FROM {safe_table_name}"
        
        if where:
            sql += f" WHERE {where}"
        
        if order_by:
            # Validate order_by to prevent SQL injection and ReDoS
            # Split by comma and validate each part separately (O(n) complexity, no backtracking)
            order_parts = [part.strip() for part in order_by.split(',')]
            for part in order_parts:
                # Each part should be: column_name [ASC|DESC]
                if not re.match(r'^[a-zA-Z0-9_]+(?:\s+(?:ASC|DESC))?$', part, re.IGNORECASE):
                    raise ValueError(f"Invalid order_by clause: {order_by}")
            sql += f" ORDER BY {order_by}"
        
        if limit:
            sql += f" LIMIT {limit}"
        
        # 実行
        cursor = self.execute(sql, parameters)
        
        # カラム名取得
        if columns is None:
            # 全カラムの場合、テーブル情報から取得
            pragma_cursor = self.execute(f"PRAGMA table_info({safe_table_name})")
            col_names = [row[1] for row in pragma_cursor]
        else:
            # Extract aliases from AS clauses, similar to query_with_pagination
            col_names = []
            for col in columns:
                parts = re.split(r'\s+as\s+', col, flags=re.IGNORECASE)
                if len(parts) > 1:
                    # Use the alias (after AS)
                    col_names.append(parts[-1].strip().strip('"').strip("'"))
                else:
                    # Use the column expression as-is
                    col_names.append(col.strip())
        
        # 結果をdictのリストに変換
        results = []
        for row in cursor:
            results.append(dict(zip(col_names, row)))
        
        return results
    
    def table_exists(self, table_name: str) -> bool:
        """
        テーブルの存在確認
        
        Args:
            table_name: テーブル名
        
        Returns:
            存在する場合True、しない場合False
        
        Example:
            >>> if db.table_exists("users"):
            ...     print("users table exists")
        """
        cursor = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None
    
    def list_tables(self) -> List[str]:
        """
        データベース内の全テーブル一覧を取得
        
        Returns:
            テーブル名のリスト
        
        Example:
            >>> tables = db.list_tables()
            >>> print(tables)  # ['data', 'users', 'posts']
        """
        cursor = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row[0] for row in cursor]
    
    def drop_table(self, table_name: str, if_exists: bool = True) -> None:
        """
        テーブルを削除
        
        Args:
            table_name: テーブル名
            if_exists: Trueの場合、存在する場合のみ削除（エラーを防ぐ）
        
        Example:
            >>> db.drop_table("old_table")
            >>> db.drop_table("temp", if_exists=True)
        """
        if_exists_clause = "IF EXISTS " if if_exists else ""
        safe_table_name = self._sanitize_identifier(table_name)
        sql = f"DROP TABLE {if_exists_clause}{safe_table_name}"
        self.execute(sql)
    
    def drop_index(self, index_name: str, if_exists: bool = True) -> None:
        """
        インデックスを削除
        
        Args:
            index_name: インデックス名
            if_exists: Trueの場合、存在する場合のみ削除
        
        Example:
            >>> db.drop_index("idx_users_email")
        """
        if_exists_clause = "IF EXISTS " if if_exists else ""
        safe_index_name = self._sanitize_identifier(index_name)
        sql = f"DROP INDEX {if_exists_clause}{safe_index_name}"
        self.execute(sql)
    
    def alter_table_add_column(self, table_name: str, column_name: str, 
                               column_type: str, default: Any = None) -> None:
        """
        既存テーブルにカラムを追加
        
        Args:
            table_name: テーブル名
            column_name: カラム名
            column_type: カラムの型（SQL型）
            default: デフォルト値（Noneの場合は指定なし）
        
        Example:
            >>> db.alter_table_add_column("users", "phone", "TEXT")
            >>> db.alter_table_add_column("users", "status", "TEXT", default="'active'")
        """
        safe_table_name = self._sanitize_identifier(table_name)
        safe_column_name = self._sanitize_identifier(column_name)
        # column_type is a SQL type string - validate it doesn't contain dangerous characters
        # Also check for closing parenthesis which could break out of ALTER TABLE structure
        if any(c in column_type for c in [";", "'", ")"]) or "--" in column_type or "/*" in column_type:
            raise ValueError(f"Invalid or dangerous column type: {column_type}")
        
        sql = f"ALTER TABLE {safe_table_name} ADD COLUMN {safe_column_name} {column_type}"
        if default is not None:
            # For default values, if it's a string, ensure it's properly quoted and escaped
            if isinstance(default, str):
                # Strip leading/trailing single quotes if present, then escape and re-quote
                stripped = default
                if stripped.startswith("'") and stripped.endswith("'") and len(stripped) >= 2:
                    stripped = stripped[1:-1]
                # Escape single quotes for SQL string literal (double them: ' becomes '')
                escaped_default = stripped.replace("'", "''")
                default = f"'{escaped_default}'"
            sql += f" DEFAULT {default}"
        self.execute(sql)
    
    def get_table_schema(self, table_name: str) -> List[dict]:
        """
        テーブル構造を取得
        
        Args:
            table_name: テーブル名
        
        Returns:
            カラム情報のリスト（各カラムはdict）
        
        Example:
            >>> schema = db.get_table_schema("users")
            >>> for col in schema:
            ...     print(f"{col['name']}: {col['type']}")
        """
        safe_table_name = self._sanitize_identifier(table_name)
        cursor = self.execute(f"PRAGMA table_info({safe_table_name})")
        columns = []
        for row in cursor:
            columns.append({
                'cid': row[0],
                'name': row[1],
                'type': row[2],
                'notnull': bool(row[3]),
                'default_value': row[4],
                'pk': bool(row[5])
            })
        return columns
    
    def list_indexes(self, table_name: str = None) -> List[dict]:
        """
        インデックス一覧を取得
        
        Args:
            table_name: テーブル名（Noneの場合は全インデックス）
        
        Returns:
            インデックス情報のリスト
        
        Example:
            >>> indexes = db.list_indexes("users")
            >>> for idx in indexes:
            ...     print(f"{idx['name']}: {idx['columns']}")
        """
        if table_name:
            cursor = self.execute(
                "SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND tbl_name=? ORDER BY name",
                (table_name,)
            )
        else:
            cursor = self.execute(
                "SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' ORDER BY name"
            )
        
        indexes = []
        for row in cursor:
            if row[0] and not row[0].startswith('sqlite_'):  # Skip auto-created indexes
                indexes.append({
                    'name': row[0],
                    'table': row[1],
                    'sql': row[2]
                })
        return indexes
    
    # ==================== Data Operation Wrappers ====================
    
    def sql_insert(self, table_name: str, data: dict) -> int:
        """
        dictから直接INSERT
        
        Args:
            table_name: テーブル名
            data: カラム名と値のdict
        
        Returns:
            挿入されたROWID
        
        Example:
            >>> rowid = db.sql_insert("users", {
            ...     "name": "Alice",
            ...     "email": "alice@example.com",
            ...     "age": 25
            ... })
        """
        safe_table_name = self._sanitize_identifier(table_name)
        safe_columns = [self._sanitize_identifier(col) for col in data.keys()]
        values = list(data.values())
        placeholders = ", ".join(["?"] * len(values))
        columns_sql = ", ".join(safe_columns)
        
        sql = f"INSERT INTO {safe_table_name} ({columns_sql}) VALUES ({placeholders})"
        self.execute(sql, tuple(values))
        
        return self.get_last_insert_rowid()
    
    def sql_update(self, table_name: str, data: dict, where: str, 
              parameters: tuple = None) -> int:
        """
        dictとwhere条件でUPDATE
        
        Args:
            table_name: テーブル名
            data: 更新するカラム名と値のdict
            where: WHERE句の条件
            parameters: WHERE句のパラメータ
        
        Returns:
            更新された行数
        
        Example:
            >>> count = db.sql_update("users", 
            ...     {"age": 26, "status": "active"},
            ...     "name = ?",
            ...     ("Alice",)
            ... )
        """
        safe_table_name = self._sanitize_identifier(table_name)
        safe_set_items = [f"{self._sanitize_identifier(col)} = ?" for col in data.keys()]
        set_clause = ", ".join(safe_set_items)
        values = list(data.values())
        
        sql = f"UPDATE {safe_table_name} SET {set_clause} WHERE {where}"
        
        if parameters:
            values.extend(parameters)
        
        self.execute(sql, tuple(values))
        return self._connection.changes()
    
    def sql_delete(self, table_name: str, where: str, parameters: tuple = None) -> int:
        """
        where条件でDELETE
        
        Args:
            table_name: テーブル名
            where: WHERE句の条件
            parameters: WHERE句のパラメータ
        
        Returns:
            削除された行数
        
        Example:
            >>> count = db.sql_delete("users", "age < ?", (18,))
        """
        safe_table_name = self._sanitize_identifier(table_name)
        sql = f"DELETE FROM {safe_table_name} WHERE {where}"
        self.execute(sql, parameters)
        return self._connection.changes()
    
    def upsert(self, table_name: str, data: dict, 
              conflict_columns: List[str] = None) -> int:
        """
        INSERT OR REPLACE の簡易版（upsert）
        
        Args:
            table_name: テーブル名
            data: カラム名と値のdict
            conflict_columns: 競合判定に使用するカラム（Noneの場合はINSERT OR REPLACE）
        
        Returns:
            挿入/更新されたROWID
        
        Example:
            >>> # 単純なINSERT OR REPLACE
            >>> db.upsert("users", {"id": 1, "name": "Alice", "age": 25})
            
            >>> # ON CONFLICT句を使用
            >>> db.upsert("users", 
            ...     {"email": "alice@example.com", "name": "Alice", "age": 26},
            ...     conflict_columns=["email"]
            ... )
        """
        safe_table_name = self._sanitize_identifier(table_name)
        safe_columns = [self._sanitize_identifier(col) for col in data.keys()]
        values = list(data.values())
        placeholders = ", ".join(["?"] * len(values))
        columns_sql = ", ".join(safe_columns)
        
        if conflict_columns:
            # ON CONFLICT を使用
            safe_conflict_cols = [self._sanitize_identifier(col) for col in conflict_columns]
            conflict_cols_sql = ", ".join(safe_conflict_cols)
            
            update_items = [f"{self._sanitize_identifier(col)} = excluded.{self._sanitize_identifier(col)}" 
                           for col in data.keys() if col not in conflict_columns]
            
            if update_items:
                update_clause = ", ".join(update_items)
            else:
                # 全カラムが競合カラムの場合は、何もしない（既存データを保持）
                sql = f"INSERT INTO {safe_table_name} ({columns_sql}) VALUES ({placeholders}) "
                sql += f"ON CONFLICT({conflict_cols_sql}) DO NOTHING"
                self.execute(sql, tuple(values))
                # When DO NOTHING is triggered, no row is inserted, return 0
                # Check only the most recent operation's change count
                if self._connection.changes() == 0:
                    return 0
                return self.get_last_insert_rowid()
            
            sql = f"INSERT INTO {safe_table_name} ({columns_sql}) VALUES ({placeholders}) "
            sql += f"ON CONFLICT({conflict_cols_sql}) DO UPDATE SET {update_clause}"
        else:
            # INSERT OR REPLACE
            sql = f"INSERT OR REPLACE INTO {safe_table_name} ({columns_sql}) VALUES ({placeholders})"
        
        self.execute(sql, tuple(values))
        return self.get_last_insert_rowid()
    
    def count(self, table_name: str = None, where: str = None, 
             parameters: tuple = None) -> int:
        """
        レコード数を取得
        
        Args:
            table_name: テーブル名（Noneの場合はデフォルトテーブル）
            where: WHERE句の条件（オプション）
            parameters: WHERE句のパラメータ
        
        Returns:
            レコード数
        
        Example:
            >>> total = db.count("users")
            >>> adults = db.count("users", "age >= ?", (18,))
        """
        if table_name is None:
            table_name = self._table
        
        safe_table_name = self._sanitize_identifier(table_name)
        
        sql = f"SELECT COUNT(*) FROM {safe_table_name}"
        if where:
            sql += f" WHERE {where}"
        
        cursor = self.execute(sql, parameters)
        return cursor.fetchone()[0]
    
    def exists(self, table_name: str, where: str, parameters: tuple = None) -> bool:
        """
        レコードの存在確認
        
        Args:
            table_name: テーブル名
            where: WHERE句の条件
            parameters: WHERE句のパラメータ
        
        Returns:
            存在する場合True
        
        Example:
            >>> if db.exists("users", "email = ?", ("alice@example.com",)):
            ...     print("User exists")
        """
        safe_table_name = self._sanitize_identifier(table_name)
        sql = f"SELECT EXISTS(SELECT 1 FROM {safe_table_name} WHERE {where})"
        cursor = self.execute(sql, parameters)
        return bool(cursor.fetchone()[0])
    
    # ==================== Query Extensions ====================
    
    def query_with_pagination(self, table_name: str = None, columns: List[str] = None,
                             where: str = None, parameters: tuple = None,
                             order_by: str = None, limit: int = None, 
                             offset: int = None, group_by: str = None) -> List[dict]:
        """
        拡張されたクエリ（offset、group_by対応）
        
        Args:
            table_name: テーブル名
            columns: 取得するカラム
            where: WHERE句
            parameters: パラメータ
            order_by: ORDER BY句
            limit: LIMIT句
            offset: OFFSET句（ページネーション用）
            group_by: GROUP BY句
        
        Returns:
            結果のリスト
        
        Example:
            >>> # ページネーション
            >>> page2 = db.query_with_pagination("users", 
            ...     limit=10, offset=10, order_by="id ASC")
            
            >>> # グループ集計
            >>> stats = db.query_with_pagination("orders",
            ...     columns=["user_id", "COUNT(*) as order_count"],
            ...     group_by="user_id"
            ... )
        """
        if table_name is None:
            table_name = self._table
        
        safe_table_name = self._sanitize_identifier(table_name)
        
        # Validate limit and offset are non-negative integers if provided
        if limit is not None:
            if not isinstance(limit, int):
                raise ValueError(f"limit must be an integer, got {type(limit).__name__}")
            if limit < 0:
                raise ValueError("limit must be non-negative")
        
        if offset is not None:
            if not isinstance(offset, int):
                raise ValueError(f"offset must be an integer, got {type(offset).__name__}")
            if offset < 0:
                raise ValueError("offset must be non-negative")
        
        # カラム指定
        if columns is None:
            columns_sql = "*"
        else:
            # For columns with aggregation functions or AS clauses, we keep the original
            # but sanitize the column names that are simple identifiers
            safe_column_list = []
            for col in columns:
                # Check if it's a simple identifier
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', col.strip()):
                    safe_column_list.append(self._sanitize_identifier(col.strip()))
                else:
                    # Contains functions, AS clauses, or other SQL
                    # Validate for dangerous patterns to prevent SQL injection (consistent with query())
                    if re.search(r'(;|--|/\*|\*/)|\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE)\b', col, re.IGNORECASE):
                        raise ValueError(f"Potentially dangerous SQL pattern in column: {col}")
                    safe_column_list.append(col)
            columns_sql = ", ".join(safe_column_list)
        
        # SQL構築
        sql = f"SELECT {columns_sql} FROM {safe_table_name}"
        
        if where:
            sql += f" WHERE {where}"
        
        if group_by:
            # Validate group_by to prevent SQL injection
            # Allow column names, spaces, commas only
            if not re.match(r'^[\w\s,]+$', group_by):
                raise ValueError(f"Invalid group_by clause: {group_by}")
            sql += f" GROUP BY {group_by}"
        
        if order_by:
            # Validate order_by to prevent SQL injection and ReDoS
            # Split by comma and validate each part separately (O(n) complexity, no backtracking)
            order_parts = [part.strip() for part in order_by.split(',')]
            for part in order_parts:
                # Each part should be: column_name [ASC|DESC]
                if not re.match(r'^[a-zA-Z0-9_]+(?:\s+(?:ASC|DESC))?$', part, re.IGNORECASE):
                    raise ValueError(f"Invalid order_by clause: {order_by}")
            sql += f" ORDER BY {order_by}"
        
        if limit:
            sql += f" LIMIT {limit}"
        
        if offset:
            sql += f" OFFSET {offset}"
        
        # 実行
        cursor = self.execute(sql, parameters)
        
        # カラム名取得
        if columns is None:
            pragma_cursor = self.execute(f"PRAGMA table_info({safe_table_name})")
            col_names = [row[1] for row in pragma_cursor]
        else:
            # カラム名からAS句を考慮（case-insensitive）
            col_names = []
            for col in columns:
                parts = re.split(r'\s+as\s+', col, flags=re.IGNORECASE)
                if len(parts) > 1:
                    col_names.append(parts[-1].strip().strip('"').strip("'"))
                else:
                    col_names.append(col.strip().strip('"').strip("'"))
        
        # 結果をdictのリストに変換
        results = []
        for row in cursor:
            results.append(dict(zip(col_names, row)))
        
        return results
    
    # ==================== Utility Functions ====================
    
    def vacuum(self) -> None:
        """
        データベースを最適化（VACUUM実行）
        
        削除されたレコードの領域を回収し、データベースファイルを最適化。
        
        Example:
            >>> db.vacuum()
        """
        self.execute("VACUUM")
    
    def get_db_size(self) -> int:
        """
        データベースファイルのサイズを取得（バイト単位）
        
        Returns:
            データベースファイルのサイズ
        
        Example:
            >>> size = db.get_db_size()
            >>> print(f"DB size: {size / 1024 / 1024:.2f} MB")
        """
        import os
        return os.path.getsize(self._db_path)
    
    def export_table_to_dict(self, table_name: str) -> List[dict]:
        """
        テーブル全体をdictのリストとして取得
        
        Args:
            table_name: テーブル名
        
        Returns:
            全レコードのリスト
        
        Example:
            >>> all_users = db.export_table_to_dict("users")
        """
        return self.query_with_pagination(table_name=table_name)
    
    def import_from_dict_list(self, table_name: str, data_list: List[dict]) -> int:
        """
        dictのリストからテーブルに一括挿入
        
        Args:
            table_name: テーブル名
            data_list: 挿入するデータのリスト
        
        Returns:
            挿入された行数
        
        Example:
            >>> users = [
            ...     {"name": "Alice", "age": 25},
            ...     {"name": "Bob", "age": 30}
            ... ]
            >>> count = db.import_from_dict_list("users", users)
        """
        if not data_list:
            return 0
        
        safe_table_name = self._sanitize_identifier(table_name)
        
        # 最初のdictからカラム名を取得
        columns = list(data_list[0].keys())
        safe_columns = [self._sanitize_identifier(col) for col in columns]
        placeholders = ", ".join(["?"] * len(columns))
        columns_sql = ", ".join(safe_columns)
        sql = f"INSERT INTO {safe_table_name} ({columns_sql}) VALUES ({placeholders})"
        
        # 各dictから値を抽出
        parameters_list = []
        for data in data_list:
            values = [data.get(col) for col in columns]
            parameters_list.append(tuple(values))
        
        self.execute_many(sql, parameters_list)
        return len(data_list)
    
    def get_last_insert_rowid(self) -> int:
        """
        最後に挿入されたROWIDを取得
        
        Returns:
            最後に挿入されたROWID
        
        Example:
            >>> db.sql_insert("users", {"name": "Alice"})
            >>> rowid = db.get_last_insert_rowid()
        """
        return self._connection.last_insert_rowid()
    
    def pragma(self, pragma_name: str, value: Any = None) -> Any:
        """
        PRAGMA設定の取得/設定
        
        Args:
            pragma_name: PRAGMA名
            value: 設定値（Noneの場合は取得のみ）
        
        Returns:
            valueがNoneの場合は現在の値、そうでない場合はNone
        
        Example:
            >>> # 取得
            >>> mode = db.pragma("journal_mode")
            
            >>> # 設定
            >>> db.pragma("foreign_keys", 1)
        """
        # Whitelist of allowed PRAGMA commands for security
        ALLOWED_PRAGMAS = {
            'foreign_keys', 'journal_mode', 'synchronous', 'cache_size',
            'temp_store', 'locking_mode', 'auto_vacuum', 'page_size',
            'encoding', 'user_version', 'schema_version', 'wal_autocheckpoint',
            'busy_timeout', 'query_only', 'recursive_triggers', 'secure_delete',
            'table_info', 'index_list', 'index_info', 'database_list'
        }
        
        if pragma_name not in ALLOWED_PRAGMAS:
            raise ValueError(f"PRAGMA '{pragma_name}' is not allowed. Allowed: {', '.join(sorted(ALLOWED_PRAGMAS))}")
        
        if value is None:
            cursor = self.execute(f"PRAGMA {pragma_name}")
            result = cursor.fetchone()
            return result[0] if result else None
        else:
            # Validate value is safe (int, float, or simple string)
            if not isinstance(value, (int, float, str)):
                raise ValueError(f"PRAGMA value must be int, float, or str, got {type(value).__name__}")
            
            # For string values, validate to prevent SQL injection
            if isinstance(value, str):
                # Only allow alphanumeric, underscore, dash, and dots for string values
                if not re.match(r'^[\w\-\.]+$', value):
                    raise ValueError("PRAGMA string value must contain only alphanumeric, underscore, dash, or dot characters")
                value_str = f"'{value}'"
            else:
                value_str = str(value)
            
            self.execute(f"PRAGMA {pragma_name} = {value_str}")
            return None
    
    # ==================== Transaction Control ====================
    
    def begin_transaction(self) -> None:
        """
        トランザクションを開始
        
        Note:
            SQLiteはネストされたトランザクションをサポートしていません。
            既にトランザクション中の場合、NanaSQLiteTransactionErrorが発生します。

        Raises:
            NanaSQLiteTransactionError: 既にトランザクション中の場合
            NanaSQLiteConnectionError: 接続が閉じられている場合
            NanaSQLiteDatabaseError: トランザクション開始に失敗した場合

        Example:
            >>> db.begin_transaction()
            >>> try:
            ...     db.sql_insert("users", {"name": "Alice"})
            ...     db.sql_insert("users", {"name": "Bob"})
            ...     db.commit()
            ... except:
            ...     db.rollback()
        """
        self._check_connection()

        if self._in_transaction:
            raise NanaSQLiteTransactionError(
                "Transaction already in progress. "
                "SQLite does not support nested transactions. "
                "Please commit or rollback the current transaction first."
            )

        try:
            self.execute("BEGIN IMMEDIATE")
            self._in_transaction = True
            self._transaction_depth = 1
        except Exception as e:
            raise NanaSQLiteDatabaseError(
                f"Failed to begin transaction: {e}",
                original_error=e if isinstance(e, apsw.Error) else None
            ) from e

    def commit(self) -> None:
        """
        トランザクションをコミット

        Raises:
            NanaSQLiteTransactionError: トランザクション外でコミットを試みた場合
            NanaSQLiteConnectionError: 接続が閉じられている場合
            NanaSQLiteDatabaseError: コミットに失敗した場合
        """
        self._check_connection()

        if not self._in_transaction:
            raise NanaSQLiteTransactionError(
                "No transaction in progress. "
                "Call begin_transaction() first or use the transaction() context manager."
            )

        try:
            self.execute("COMMIT")
            self._in_transaction = False
            self._transaction_depth = 0
        except Exception as e:
            # コミット失敗時は状態を維持（ロールバックが必要）
            raise NanaSQLiteDatabaseError(
                f"Failed to commit transaction: {e}",
                original_error=e if isinstance(e, apsw.Error) else None
            ) from e

    def rollback(self) -> None:
        """
        トランザクションをロールバック

        Raises:
            NanaSQLiteTransactionError: トランザクション外でロールバックを試みた場合
            NanaSQLiteConnectionError: 接続が閉じられている場合
            NanaSQLiteDatabaseError: ロールバックに失敗した場合
        """
        self._check_connection()

        if not self._in_transaction:
            raise NanaSQLiteTransactionError(
                "No transaction in progress. "
                "Call begin_transaction() first or use the transaction() context manager."
            )

        try:
            self.execute("ROLLBACK")
            self._in_transaction = False
            self._transaction_depth = 0
        except Exception as e:
            # ロールバック失敗は深刻なので状態をリセット
            self._in_transaction = False
            self._transaction_depth = 0
            raise NanaSQLiteDatabaseError(
                f"Failed to rollback transaction: {e}",
                original_error=e if isinstance(e, apsw.Error) else None
            ) from e

    def in_transaction(self) -> bool:
        """
        現在トランザクション中かどうかを返す

        Returns:
            bool: トランザクション中の場合True

        Example:
            >>> db.begin_transaction()
            >>> print(db.in_transaction())  # True
            >>> db.commit()
            >>> print(db.in_transaction())  # False
        """
        return self._in_transaction

    def transaction(self):
        """
        トランザクションのコンテキストマネージャ
        
        コンテキストマネージャ内で例外が発生しない場合は自動的にコミット、
        例外が発生した場合は自動的にロールバックします。

        Raises:
            NanaSQLiteTransactionError: 既にトランザクション中の場合

        Example:
            >>> with db.transaction():
            ...     db.sql_insert("users", {"name": "Alice"})
            ...     db.sql_insert("users", {"name": "Bob"})
            ...     # 自動的にコミット、例外時はロールバック
        """
        return _TransactionContext(self)

    def table(self, table_name: str):
        """
        サブテーブル用のNanaSQLiteインスタンスを取得

        新しいインスタンスを作成しますが、SQLite接続とロックは共有します。
        これにより、複数のテーブルインスタンスが同じ接続を使用して
        スレッドセーフに動作します。

        ⚠️ 重要な注意事項:
        - 同じテーブルに対して複数のインスタンスを作成しないでください
          各インスタンスは独立したキャッシュを持つため、キャッシュ不整合が発生します
        - 推奨: テーブルインスタンスを変数に保存して再利用してください

        非推奨:
            sub1 = db.table("users")
            sub2 = db.table("users")  # キャッシュ不整合の原因

        推奨:
            users_db = db.table("users")
            # users_dbを使い回す

        :param table_name: テーブル名
        :return NanaSQLite: 新しいテーブルインスタンス

        Raises:
            NanaSQLiteConnectionError: 接続が閉じられている場合

        Example:
            >>> with NanaSQLite("app.db", table="main") as main_db:
            ...     users_db = main_db.table("users")
            ...     products_db = main_db.table("products")
            ...     users_db["user1"] = {"name": "Alice"}
            ...     products_db["prod1"] = {"name": "Laptop"}
        """
        self._check_connection()

        child = NanaSQLite(
            self._db_path,
            table=table_name,
            _shared_connection=self._connection,
            _shared_lock=self._lock
        )

        # 弱参照で子インスタンスを追跡
        self._child_instances.append(weakref.ref(child))

        return child


class _TransactionContext:
    """トランザクションのコンテキストマネージャ"""
    
    def __init__(self, db: NanaSQLite):
        self.db = db
    
    def __enter__(self):
        self.db.begin_transaction()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.db.commit()
        else:
            self.db.rollback()
        return False
