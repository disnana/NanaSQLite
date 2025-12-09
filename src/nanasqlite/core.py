"""
NanaSQLite: APSW SQLite-backed dict wrapper with memory caching.

通常のPython dictをラップし、操作時にSQLite永続化処理を行う。
- 書き込み: 即時SQLiteへ永続化
- 読み込み: デフォルトは遅延ロード（使用時）、一度読み込んだらメモリ管理
- 一括ロード: bulk_load=Trueで起動時に全データをメモリに展開
"""

import json
import re
from typing import Any, Iterator, Optional, Type, List
import apsw


class NanaSQLite:
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
                 optimize: bool = True, cache_size_mb: int = 64):
        """
        Args:
            db_path: SQLiteデータベースファイルのパス
            table: 使用するテーブル名 (デフォルト: "data")
            bulk_load: Trueの場合、初期化時に全データをメモリに読み込む
            optimize: Trueの場合、WALモードなど高速化設定を適用
            cache_size_mb: SQLiteキャッシュサイズ（MB）、デフォルト64MB
        """
        self._db_path = db_path
        self._table = table
        self._connection: apsw.Connection = apsw.Connection(db_path)
        self._data: dict = {}  # 内部dict（メモリキャッシュ）
        self._cached_keys: set = set()  # キャッシュ済みキーの追跡
        self._all_loaded: bool = False  # 全データ読み込み済みフラグ
        
        # 高速化設定
        if optimize:
            self._apply_optimizations(cache_size_mb)
        
        # テーブル作成
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
            ValueError: 識別子が無効な場合
        
        Note:
            SQLiteの識別子は以下をサポート:
            - 英数字とアンダースコア
            - 数字で開始しない
            - SQLキーワードも引用符で囲めば使用可能
        """
        if not identifier:
            raise ValueError("Identifier cannot be empty")
        
        # 基本的な検証: 英数字とアンダースコアのみ許可
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            raise ValueError(
                f"Invalid identifier '{identifier}': must start with letter or underscore "
                "and contain only alphanumeric characters and underscores"
            )
        
        # SQLiteではダブルクォートで囲むことで識別子をエスケープ
        # （内部のダブルクォートは二重化）
        return f'"{identifier.replace('"', '""')}"'
    
    # ==================== Private Methods ====================
    
    def _serialize(self, value: Any) -> str:
        """値をJSON文字列にシリアライズ"""
        return json.dumps(value, ensure_ascii=False)
    
    def _deserialize(self, value: str) -> Any:
        """JSON文字列を値にデシリアライズ"""
        return json.loads(value)
    
    def _write_to_db(self, key: str, value: Any) -> None:
        """即時書き込み: SQLiteに値を保存"""
        serialized = self._serialize(value)
        self._connection.execute(
            f"INSERT OR REPLACE INTO {self._table} (key, value) VALUES (?, ?)",
            (key, serialized)
        )
    
    def _read_from_db(self, key: str) -> Optional[Any]:
        """SQLiteから値を読み込み"""
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
        self._connection.execute(
            f"DELETE FROM {self._table} WHERE key = ?",
            (key,)
        )
    
    def _get_all_keys_from_db(self) -> list:
        """SQLiteから全キーを取得"""
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
        """key in dict"""
        return self._ensure_cached(key)
    
    def __len__(self) -> int:
        """len(dict) - DBの実際の件数を返す"""
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
    
    def pop(self, key: str, *args) -> Any:
        """dict.pop(key[, default])"""
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
        
        cursor = self._connection.execute(
            f"SELECT key, value FROM {self._table}"
        )
        for key, value in cursor:
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
    
    def batch_update(self, mapping: dict) -> None:
        """
        一括書き込み（トランザクション使用で超高速）
        
        大量のデータを一度に書き込む場合、通常のupdateより10-100倍高速。
        
        Args:
            mapping: 書き込むキーと値のdict
        
        Example:
            >>> db.batch_update({"key1": "value1", "key2": "value2", ...})
        """
        cursor = self._connection.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        try:
            for key, value in mapping.items():
                serialized = self._serialize(value)
                cursor.execute(
                    f"INSERT OR REPLACE INTO {self._table} (key, value) VALUES (?, ?)",
                    (key, serialized)
                )
                self._data[key] = value
                self._cached_keys.add(key)
            cursor.execute("COMMIT")
        except Exception:
            cursor.execute("ROLLBACK")
            raise
    
    def batch_delete(self, keys: list) -> None:
        """
        一括削除（トランザクション使用で高速）
        
        Args:
            keys: 削除するキーのリスト
        """
        cursor = self._connection.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        try:
            for key in keys:
                cursor.execute(
                    f"DELETE FROM {self._table} WHERE key = ?",
                    (key,)
                )
                self._data.pop(key, None)
                self._cached_keys.discard(key)
            cursor.execute("COMMIT")
        except Exception:
            cursor.execute("ROLLBACK")
            raise
    
    def to_dict(self) -> dict:
        """全データをPython dictとして取得"""
        self.load_all()
        return dict(self._data)
    
    def close(self) -> None:
        """データベース接続を閉じる"""
        self._connection.close()
    
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
    
    def execute(self, sql: str, parameters: tuple = None) -> apsw.Cursor:
        """
        SQLを直接実行
        
        任意のSQL文を実行できる。SELECT、INSERT、UPDATE、DELETEなど。
        パラメータバインディングをサポート（SQLインジェクション対策）。
        
        Args:
            sql: 実行するSQL文
            parameters: SQLのパラメータ（?プレースホルダー用）
        
        Returns:
            APSWのCursorオブジェクト（結果の取得に使用）
        
        Example:
            >>> cursor = db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
            >>> for row in cursor:
            ...     print(row)
        """
        if parameters is None:
            return self._connection.execute(sql)
        else:
            return self._connection.execute(sql, parameters)
    
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
        cursor = self._connection.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        try:
            for parameters in parameters_list:
                cursor.execute(sql, parameters)
            cursor.execute("COMMIT")
        except Exception:
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
        
        column_defs = []
        for col_name, col_type in columns.items():
            column_defs.append(f"{col_name} {col_type}")
        
        if primary_key and not any(primary_key.upper() in col.upper() and "PRIMARY KEY" in col.upper() 
                                   for col in column_defs):
            column_defs.append(f"PRIMARY KEY ({primary_key})")
        
        columns_sql = ", ".join(column_defs)
        sql = f"CREATE TABLE {if_not_exists_clause}{table_name} ({columns_sql})"
        
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
        columns_sql = ", ".join(columns)
        
        sql = f"CREATE {unique_clause}INDEX {if_not_exists_clause}{index_name} ON {table_name} ({columns_sql})"
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
        
        # カラム指定
        if columns is None:
            columns_sql = "*"
        else:
            columns_sql = ", ".join(columns)
        
        # SQL構築
        sql = f"SELECT {columns_sql} FROM {table_name}"
        
        if where:
            sql += f" WHERE {where}"
        
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        if limit:
            sql += f" LIMIT {limit}"
        
        # 実行
        cursor = self.execute(sql, parameters)
        
        # カラム名取得
        if columns is None:
            # 全カラムの場合、テーブル情報から取得
            pragma_cursor = self.execute(f"PRAGMA table_info({table_name})")
            col_names = [row[1] for row in pragma_cursor]
        else:
            col_names = columns
        
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
        sql = f"DROP TABLE {if_exists_clause}{table_name}"
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
        sql = f"DROP INDEX {if_exists_clause}{index_name}"
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
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        if default is not None:
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
        cursor = self.execute(f"PRAGMA table_info({table_name})")
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
        columns = list(data.keys())
        values = list(data.values())
        placeholders = ", ".join(["?"] * len(values))
        columns_sql = ", ".join(columns)
        
        sql = f"INSERT INTO {table_name} ({columns_sql}) VALUES ({placeholders})"
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
        set_items = [f"{col} = ?" for col in data.keys()]
        set_clause = ", ".join(set_items)
        values = list(data.values())
        
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {where}"
        
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
        sql = f"DELETE FROM {table_name} WHERE {where}"
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
        columns = list(data.keys())
        values = list(data.values())
        placeholders = ", ".join(["?"] * len(values))
        columns_sql = ", ".join(columns)
        
        if conflict_columns:
            # ON CONFLICT を使用
            conflict_cols = ", ".join(conflict_columns)
            update_items = [f"{col} = excluded.{col}" for col in columns if col not in conflict_columns]
            
            if update_items:
                update_clause = ", ".join(update_items)
            else:
                # 全カラムが競合カラムの場合は、何もしない（既存データを保持）
                sql = f"INSERT INTO {table_name} ({columns_sql}) VALUES ({placeholders}) "
                sql += f"ON CONFLICT({conflict_cols}) DO NOTHING"
                self.execute(sql, tuple(values))
                return self.get_last_insert_rowid()
            
            sql = f"INSERT INTO {table_name} ({columns_sql}) VALUES ({placeholders}) "
            sql += f"ON CONFLICT({conflict_cols}) DO UPDATE SET {update_clause}"
        else:
            # INSERT OR REPLACE
            sql = f"INSERT OR REPLACE INTO {table_name} ({columns_sql}) VALUES ({placeholders})"
        
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
        
        sql = f"SELECT COUNT(*) FROM {table_name}"
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
        sql = f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {where})"
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
        
        # カラム指定
        if columns is None:
            columns_sql = "*"
        else:
            columns_sql = ", ".join(columns)
        
        # SQL構築
        sql = f"SELECT {columns_sql} FROM {table_name}"
        
        if where:
            sql += f" WHERE {where}"
        
        if group_by:
            sql += f" GROUP BY {group_by}"
        
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        if limit:
            sql += f" LIMIT {limit}"
        
        if offset:
            sql += f" OFFSET {offset}"
        
        # 実行
        cursor = self.execute(sql, parameters)
        
        # カラム名取得
        if columns is None:
            pragma_cursor = self.execute(f"PRAGMA table_info({table_name})")
            col_names = [row[1] for row in pragma_cursor]
        else:
            # カラム名からAS句を考慮（case-insensitive）
            col_names = []
            for col in columns:
                parts = re.split(r'\s+as\s+', col, flags=re.IGNORECASE)
                if len(parts) > 1:
                    col_names.append(parts[-1].strip())
                else:
                    col_names.append(col.strip())
        
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
        
        # 最初のdictからカラム名を取得
        columns = list(data_list[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        columns_sql = ", ".join(columns)
        sql = f"INSERT INTO {table_name} ({columns_sql}) VALUES ({placeholders})"
        
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
            >>> db.insert("users", {"name": "Alice"})
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
        if value is None:
            cursor = self.execute(f"PRAGMA {pragma_name}")
            result = cursor.fetchone()
            return result[0] if result else None
        else:
            self.execute(f"PRAGMA {pragma_name} = {value}")
            return None
    
    # ==================== Transaction Control ====================
    
    def begin_transaction(self) -> None:
        """
        トランザクションを開始
        
        Example:
            >>> db.begin_transaction()
            >>> try:
            ...     db.insert("users", {"name": "Alice"})
            ...     db.insert("users", {"name": "Bob"})
            ...     db.commit()
            ... except:
            ...     db.rollback()
        """
        self.execute("BEGIN IMMEDIATE")
    
    def commit(self) -> None:
        """
        トランザクションをコミット
        """
        self.execute("COMMIT")
    
    def rollback(self) -> None:
        """
        トランザクションをロールバック
        """
        self.execute("ROLLBACK")
    
    def transaction(self):
        """
        トランザクションのコンテキストマネージャ
        
        Example:
            >>> with db.transaction():
            ...     db.insert("users", {"name": "Alice"})
            ...     db.insert("users", {"name": "Bob"})
            ...     # 自動的にコミット、例外時はロールバック
        """
        return _TransactionContext(self)


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
