"""
NanaSQLite: APSW SQLite-backed dict wrapper with memory caching.

通常のPython dictをラップし、操作時にSQLite永続化処理を行う。
- 書き込み: 即時SQLiteへ永続化
- 読み込み: デフォルトは遅延ロード（使用時）、一度読み込んだらメモリ管理
- 一括ロード: bulk_load=Trueで起動時に全データをメモリに展開
"""

import json
from typing import Any, Iterator, Optional, Union
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
