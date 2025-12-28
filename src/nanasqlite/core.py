"""
NanaSQLite: APSW SQLite-backed dict wrapper with memory caching.

通常のPython dictをラップし、操作時にSQLite永続化処理を行う。
- 書き込み: 即時SQLiteへ永続化
- 読み込み: デフォルトは遅延ロード（使用時）、一度読み込んだらメモリ管理
- 一括ロード: bulk_load=Trueで起動時に全データをメモリに展開
"""

from __future__ import annotations

import json
import logging
import os
import re
import threading
import warnings
import weakref
from collections.abc import Iterator, MutableMapping
from typing import Any, Literal

import apsw

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

from .cache import CacheStrategy, CacheType, create_cache
from .exceptions import (
    NanaSQLiteClosedError,
    NanaSQLiteConnectionError,
    NanaSQLiteDatabaseError,
    NanaSQLiteTransactionError,
    NanaSQLiteValidationError,
)
from .sql_utils import fast_validate_sql_chars, sanitize_sql_for_function_scan

# 識別子バリデーション用の正規表現パターン（英数字とアンダースコアのみ、数字で開始しない）
IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

logger = logging.getLogger(__name__)


class NanaSQLite(MutableMapping):
    """
    APSW SQLite-backed dict wrapper with Security and Connection Enhancements (v1.2.0).
    (APSW SQLiteをバックエンドとした、セキュリティ・接続管理強化版の辞書型ラッパー (v1.2.0))

    Internally maintains a Python dict and synchronizes with SQLite during operations.
    In v1.2.0, enhanced dynamic SQL validation, ReDoS protection, and strict connection management are introduced.

    内部でPython dictを保持し、操作時にSQLiteとの同期を行います。
    v1.2.0では、動的SQLのバリデーション強化、ReDoS対策、および厳格な接続管理が導入されています。

    Args:
        db_path: SQLiteデータベースファイルのパス
        table: 使用するテーブル名 (デフォルト: "data")
        bulk_load: Trueの場合、初期化時に全データをメモリに読み込む
        strict_sql_validation: Trueの場合、未許可の関数等を含むクエリを拒否 (v1.2.0)
        max_clause_length: SQL句の最大長（ReDoS対策、v1.2.0）
    """

    def __init__(
        self,
        db_path: str,
        table: str = "data",
        bulk_load: bool = False,
        optimize: bool = True,
        cache_size_mb: int = 64,
        strict_sql_validation: bool = True,
        allowed_sql_functions: list[str] | None = None,
        forbidden_sql_functions: list[str] | None = None,
        max_clause_length: int | None = 1000,
        cache_strategy: CacheType | Literal["unbounded", "lru", "ttl"] = CacheType.UNBOUNDED,
        cache_size: int | None = None,
        cache_ttl: float | None = None,
        cache_persistence_ttl: bool = False,
        encryption_key: str | bytes | None = None,
        encryption_mode: Literal["aes-gcm", "chacha20", "fernet"] = "aes-gcm",
        _shared_connection: apsw.Connection | None = None,
        _shared_lock: threading.RLock | None = None,
    ):
        """
        Args:
            db_path: SQLiteデータベースファイルのパス
            table: 使用するテーブル名 (デフォルト: "data")
            bulk_load: Trueの場合、初期化時に全データをメモリに読み込む
            optimize: Trueの場合、WALモードなど高速化設定を適用
            cache_size_mb: SQLiteキャッシュサイズ（MB）、デフォルト64MB
            strict_sql_validation: Trueの場合、未許可の関数等を含むクエリを拒否
            allowed_sql_functions: 追加で許可するSQL関数のリスト
            forbidden_sql_functions: 明示的に禁止するSQL関数のリスト
            max_clause_length: SQL句の最大長（ReDoS対策）。Noneで制限なし
            _shared_connection: 内部用：共有する接続（table()メソッドで使用）
            _shared_lock: 内部用：共有するロック（table()メソッドで使用）
        """
        self._db_path: str = db_path
        self._table: str = table

        # Encryption setup
        self._encryption_key = encryption_key
        self._encryption_mode = encryption_mode
        self._fernet: Fernet | None = None
        self._aead: AESGCM | ChaCha20Poly1305 | None = None

        if encryption_key:
            if not HAS_CRYPTOGRAPHY:
                raise ImportError(
                    "Encryption requires the 'cryptography' library. "
                    "Install it with: pip install nanasqlite[encryption]"
                )
            # Support both str (base64) and bytes
            key_bytes: bytes = encryption_key.encode("utf-8") if isinstance(encryption_key, str) else encryption_key

            if encryption_mode == "fernet":
                self._fernet = Fernet(key_bytes)
            elif encryption_mode == "aes-gcm":
                self._aead = AESGCM(key_bytes)
            elif encryption_mode == "chacha20":
                self._aead = ChaCha20Poly1305(key_bytes)
            else:
                raise ValueError(f"Unsupported encryption_mode: {encryption_mode}")

        # Setup Persistence TTL callback if enabled
        on_expire = None
        if (cache_strategy == CacheType.TTL or cache_strategy == "ttl") and cache_persistence_ttl:

            def _expire_callback(key: str, value: Any) -> None:
                try:
                    # Use a new or shared connection to delete from DB
                    # Implementation detail: we need to be careful with locks
                    self._delete_from_db_on_expire(key)
                except Exception as e:
                    logger.error(f"Failed to delete expired key '{key}' from DB: {e}")

            on_expire = _expire_callback

        self._cache: CacheStrategy = create_cache(cache_strategy, cache_size, ttl=cache_ttl, on_expire=on_expire)
        self._data = self._cache.get_data()
        self._lru_mode = (
            (cache_strategy == CacheType.LRU) or (cache_strategy == "lru") or
            (cache_strategy == CacheType.TTL) or (cache_strategy == "ttl")
        )

        if not self._lru_mode:
            # Unbounded 以外のモードでは内部辞書の直接参照を使用しない場合があるが、
            # 現状の設計では _cached_keys を通じて存在チェックを行っている
            self._cached_keys = self._cache._cached_keys  # type: ignore
        else:
            # LRU/TTL モードでは、データ保持自体が存在の証
            self._cached_keys = self._data  # type: ignore

        self._all_loaded: bool = False  # 全データ読み込み済みフラグ

        # セキュリティ設定
        self.strict_sql_validation = strict_sql_validation
        self.allowed_sql_functions = set(allowed_sql_functions or [])
        self.forbidden_sql_functions = set(forbidden_sql_functions or [])
        self.max_clause_length = max_clause_length

        # デフォルトで許可されるSQL関数
        self._default_allowed_functions = {
            "COUNT",
            "SUM",
            "AVG",
            "MIN",
            "MAX",
            "ABS",
            "UPPER",
            "LOWER",
            "LENGTH",
            "ROUND",
            "COALESCE",
            "IFNULL",
            "NULLIF",
            "STRFTIME",
            "DATE",
            "TIME",
            "DATETIME",
            "JULIANDAY",
        }

        # トランザクション状態管理
        self._in_transaction: bool = False  # トランザクション中かどうか
        self._transaction_depth: int = 0  # ネストレベル（警告用）

        # 子インスタンスの追跡（リソース管理用）
        self._child_instances = weakref.WeakSet()  # WeakSetによる弱参照追跡（死んだ参照は自動的にクリーンアップ）
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
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
            raise NanaSQLiteValidationError(
                f"Invalid identifier '{identifier}': must start with letter or underscore "
                "and contain only alphanumeric characters and underscores"
            )

        # SQLiteではダブルクォートで囲むことで識別子をエスケープ
        return f'"{identifier}"'

    # ==================== Private Methods ====================

    def __hash__(self):
        # MutableMapping inhibits hashing by default because it's mutable.
        # However, we need identity-based hashing to track instances in WeakSet.
        # This is safe as long as we don't rely on content-based hashing in sets.
        # NOTE: This technically violates the rule that a==b implies hash(a)==hash(b),
        # because __eq__ implements content equivalence while __hash__ implements identity.
        # This is an intentional design choice to support WeakSet management while providing
        # convenient dict-like equality comparisons.
        return id(self)

    def __eq__(self, other):
        """
        辞書のような等価性比較を実装

        他のマッピング（dictやMutableMapping）との比較では内容ベースの比較を行い、
        それ以外では同一性（is）での比較を行う。

        Args:
            other: 比較対象のオブジェクト

        Returns:
            bool: 等価な場合True、そうでない場合False

        Raises:
            NanaSQLiteClosedError: 接続が閉じられている場合
        """
        if isinstance(other, (dict, MutableMapping)):
            # Ensure the connection is open; propagate NanaSQLiteClosedError if not.
            self._check_connection()
            return dict(self.items()) == dict(other.items())
        return self is other

    def _check_connection(self) -> None:
        """
        接続が有効かチェック

        Raises:
            NanaSQLiteClosedError: 接続が閉じられている、または親が閉じられている場合
        """
        if self._is_closed:
            raise NanaSQLiteClosedError(f"Database connection is closed (table: '{self._table}').")
        if self._parent_closed:
            raise NanaSQLiteClosedError(
                f"Parent database connection is closed (table: '{self._table}'). "
                "If you obtained this instance via .table(), ensure the primary "
                "NanaSQLite instance remains open during usage."
            )

    def _validate_expression(
        self,
        expr: str | None,
        strict: bool | None = None,
        allowed: list[str] | None = None,
        forbidden: list[str] | None = None,
        override_allowed: bool = False,
        context: Literal["order_by", "group_by", "where", "column"] | None = None,
    ) -> None:
        """
        SQL表現（ORDER BY, GROUP BY, 列名等）を検証。

        Args:
            expr: 検証するSQL表現
            strict: 強制停止モード。Noneの場合はインスタンス設定を使用。
            allowed: 今回のクエリで追加/置換して許可する関数。
            forbidden: 今回のクエリで明示的に禁止する関数。
            override_allowed: Trueの場合、インスタンス許可設定を無視して今回のallowedのみ参照。
            context: エラーメッセージのコンテキスト ("order_by", "group_by", "where", "column")

        Raises:
            NanaSQLiteValidationError: strict=True かつ不適切な表現の場合
            UserWarning: strict=False かつ不適切な表現の場合（実行は許可）
        """
        if not expr:
            return

        # 0. legacy check for SQL injection patterns
        # test_security.py compatibility: raise ValueError for strictly dangerous patterns
        # We use a combined message to satisfy both test_security.py ("Potentially dangerous...")
        # and test_security_additions.py ("Invalid...")
        warning_text = "Potentially dangerous SQL pattern"

        context_labels = {
            "order_by": "order_by clause",
            "group_by": "group_by clause",
            "where": "where clause",
            "column": "column name",
        }
        label = context_labels.get(context)

        # Standardize format: "Invalid [label]: [warning_text]" (or "Invalid: [warning_text]" if no label)
        # This satisfies both legacy and new security tests.
        if label:
            full_msg = f"Invalid {label}: {warning_text}"
        else:
            full_msg = f"Invalid: {warning_text}"

        dangerous_patterns = [
            (r";", full_msg),
            (r"--", full_msg),
            (r"/\*", full_msg),
            (r"\b(DROP|DELETE|UPDATE|INSERT|TRUNCATE|ALTER)\b", full_msg),
        ]

        # 0.5. Fast character-set validation (ReDoS countermeasure)
        if not fast_validate_sql_chars(str(expr)):
            # If invalid characters are found, we apply strict or warning
            # Note: This is a preventative layer.
            # We use full_msg to maintain compatibility with existing tests expecting "Invalid [label]: ..."
            msg = f"{full_msg} or invalid characters detected."
            if strict or (strict is None and self.strict_sql_validation):
                raise ValueError(msg)
            else:
                warnings.warn(msg, UserWarning, stacklevel=2)

        for pattern, msg in dangerous_patterns:
            if re.search(pattern, str(expr), re.IGNORECASE):
                # Block highly dangerous patterns in strict mode, but only warn in non-strict
                if strict or (strict is None and self.strict_sql_validation):
                    raise ValueError(msg)
                else:
                    warnings.warn(msg, UserWarning, stacklevel=2)

        # 1. 長さ制限 (ReDoS対策)
        max_len = self.max_clause_length
        if max_len and len(expr) > max_len:
            msg = f"SQL expression exceeds maximum length of {max_len} characters."
            if strict or (strict is None and self.strict_sql_validation):
                raise NanaSQLiteValidationError(msg)
            else:
                warnings.warn(msg, UserWarning, stacklevel=2)

        # 2. 禁止リストの整理 (メソッド指定を優先、なければインスタンス設定)
        forbidden_list = set(forbidden) if forbidden is not None else self.forbidden_sql_functions
        if "*" in forbidden_list:
            msg = "All SQL functions are forbidden for this expression."
            if strict or (strict is None and self.strict_sql_validation):
                raise NanaSQLiteValidationError(msg)
            else:
                warnings.warn(msg, UserWarning, stacklevel=2)
                return

        # 3. 許可リストの整理
        effective_allowed = set()
        if not override_allowed:
            effective_allowed.update(self._default_allowed_functions)
            effective_allowed.update(self.allowed_sql_functions)

        if allowed:
            effective_allowed.update(allowed)

        # 禁止リストに含まれるものは許可から削除
        effective_allowed -= forbidden_list

        # 4. 関数呼び出しの抽出
        # 文字列リテラルやコメントをマスクした上で関数呼び出しを検索
        # これにより、SELECT 'COUNT(' ... のようなパターンでの誤検知を防ぐ
        sanitized_expr = sanitize_sql_for_function_scan(expr)
        matches = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", sanitized_expr)

        for func in matches:
            func_upper = func.upper()

            # 明示的に禁止されている場合
            if func_upper in forbidden_list:
                msg = f"SQL function '{func_upper}' is explicitly forbidden."
                if strict or (strict is None and self.strict_sql_validation):
                    raise NanaSQLiteValidationError(msg)
                else:
                    warnings.warn(msg, UserWarning, stacklevel=2)
                continue

            # 許可リストにない場合
            if func_upper not in effective_allowed:
                msg = (
                    f"SQL function '{func_upper}' is not in the allowed list. "
                    "Use 'allowed_sql_functions' to permit it if you trust this function."
                )
                if strict or (strict is None and self.strict_sql_validation):
                    raise NanaSQLiteValidationError(msg)
                else:
                    warnings.warn(msg, UserWarning, stacklevel=2)

    def _mark_parent_closed(self) -> None:
        """
        親インスタンスから呼ばれ、親が閉じられたことをマークする
        """
        self._parent_closed = True

    def _serialize(self, value: Any) -> bytes | str:
        """シリアライズ (JSON -> Encryption if enabled)"""
        json_str = json.dumps(value, ensure_ascii=False)
        data = json_str.encode("utf-8")

        if self._fernet:
            return self._fernet.encrypt(data)

        if self._aead:
            # Generate 12 bytes nonce
            nonce = os.urandom(12)
            ciphertext = self._aead.encrypt(nonce, data, None)
            # Combine nonce + ciphertext
            return nonce + ciphertext

        return json_str

    def _deserialize(self, value: bytes | str) -> Any:
        """デシリアライズ (Decryption if enabled -> JSON)"""
        if self._fernet:
            decoded = self._fernet.decrypt(value).decode("utf-8")
            return json.loads(decoded)

        if self._aead:
            if not isinstance(value, bytes):
                # Fallback or manual check if stored as string accidentally
                return json.loads(value)

            # Split nonce (12B) and ciphertext
            nonce = value[:12]
            ciphertext = value[12:]
            decoded = self._aead.decrypt(nonce, ciphertext, None).decode("utf-8")
            return json.loads(decoded)

        return json.loads(value)

    def _write_to_db(self, key: str, value: Any) -> None:
        """即時書き込み: SQLiteに値を保存"""
        serialized = self._serialize(value)
        with self._lock:
            self._connection.execute(
                f"INSERT OR REPLACE INTO {self._table} (key, value) VALUES (?, ?)",  # nosec
                (key, serialized),
            )

    def _read_from_db(self, key: str) -> Any | None:
        """SQLiteから値を読み込み"""
        with self._lock:
            cursor = self._connection.execute(
                f"SELECT value FROM {self._table} WHERE key = ?",  # nosec
                (key,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._deserialize(row[0])

    def _delete_from_db(self, key: str) -> None:
        """SQLiteから値を削除"""
        with self._lock:
            self._connection.execute(
                f"DELETE FROM {self._table} WHERE key = ?",  # nosec
                (key,),
            )

    def _get_all_keys_from_db(self) -> list:
        """SQLiteから全キーを取得"""
        with self._lock:
            cursor = self._connection.execute(
                f"SELECT key FROM {self._table}"  # nosec
            )
            return [row[0] for row in cursor]

    def _ensure_cached(self, key: str) -> bool:
        """
        キーがキャッシュにない場合、DBから読み込む（遅延ロード）
        Returns: キーが存在するかどうか
        """
        # FAST PATH for default Unbounded mode
        if not self._lru_mode:
            if key in self._cached_keys:
                return key in self._data
        else:
            if key in self._data:
                return True

        # DBから読み込み
        value = self._read_from_db(key)

        if value is not None:
            if self._lru_mode or (hasattr(self._cache, "_max_size") and self._cache._max_size):
                self._cache.set(key, value)
            else:
                self._data[key] = value
                self._cached_keys.add(key)
            return True

        # Value is None (not in DB)
        if not self._lru_mode:
            self._cached_keys.add(key)
        return False

    # ==================== Dict Interface ====================

    def __getitem__(self, key: str) -> Any:
        """dict[key] - 遅延ロード後、メモリから取得"""
        if self._ensure_cached(key):
            # LRU updates order even on __getitem__
            if self._lru_mode:
                return self._cache.get(key)
            return self._data[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """dict[key] = value - 即時書き込み + メモリ更新"""
        self._check_connection()
        # メモリ更新
        if self._lru_mode or (hasattr(self._cache, "_max_size") and self._cache._max_size):
            self._cache.set(key, value)
        else:
            self._data[key] = value
            self._cached_keys.add(key)
        # 即時書き込み
        self._write_to_db(key, value)

    def __delitem__(self, key: str) -> None:
        """del dict[key] - 即時削除"""
        if not self._ensure_cached(key):
            raise KeyError(key)
        # メモリから削除
        if self._lru_mode:
            self._cache.delete(key)
        else:
            self._data.pop(key, None)
            self._cached_keys.discard(key)

        # DBから削除
        self._delete_from_db(key)

    def __contains__(self, key: str) -> bool:
        """
        key in dict - キーの存在確認

        キャッシュにある場合はO(1)、ない場合は軽量なEXISTSクエリを使用。
        存在確認のみの場合、value全体を読み込まないため高速。
        """
        # FAST PATH
        if key in self._cached_keys:
            return key in self._data

        # 軽量な存在確認クエリ（valueを読み込まない）
        with self._lock:
            cursor = self._connection.execute(
                f"SELECT 1 FROM {self._table} WHERE key = ? LIMIT 1",  # nosec
                (key,),  # nosec
            )
            exists = cursor.fetchone() is not None

        if exists:
            # 存在する場合のみキャッシュに読み込む（遅延ロード）
            self._ensure_cached(key)
        else:
            # 存在しないこともキャッシュ
            if not self._lru_mode:
                self._cached_keys.add(key)

        return exists

    def __len__(self) -> int:
        """len(dict) - DBの実際の件数を返す"""
        with self._lock:
            cursor = self._connection.execute(
                f"SELECT COUNT(*) FROM {self._table}"  # nosec
            )
            return cursor.fetchone()[0]

    def __iter__(self) -> Iterator[str]:
        """for key in dict"""
        return iter(self.keys())

    def __repr__(self) -> str:
        return f"NanaSQLite({self._db_path!r}, table={self._table!r}, cached={self._cache.size})"

    # ==================== Dict Methods ====================

    def keys(self) -> list:
        """全キーを取得（DBから）"""
        return self._get_all_keys_from_db()

    def values(self) -> list:
        """全値を取得（一括ロードしてからメモリから）"""
        self._check_connection()
        self.load_all()
        return list(self._cache.get_data().values())

    def items(self) -> list:
        """全アイテムを取得（一括ロードしてからメモリから）"""
        self.load_all()
        return list(self._cache.get_data().items())

    def get(self, key: str, default: Any = None) -> Any:
        """dict.get(key, default)"""
        if self._ensure_cached(key):
            if self._lru_mode:
                return self._cache.get(key)
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
        # DBから直接読み込み
        value = self._read_from_db(key)

        if value is not None:
            # キャッシュを更新
            if self._lru_mode:
                self._cache.set(key, value)
            else:
                self._data[key] = value
                self._cached_keys.add(key)
            return value
        else:
            # 存在しない場合はキャッシュからも削除
            if self._lru_mode:
                self._cache.delete(key)
            else:
                self._data.pop(key, None)
                self._cached_keys.add(key)  # 「存在しない」ことをマーク
            return default

    def batch_get(self, keys: list[str]) -> dict[str, Any]:
        """
        複数のキーを一度に取得（効率的な一括ロード）

        1回の `SELECT IN (...)` クエリで複数のキーをDBから取得する。
        取得した値は自動的にキャッシュに保存される。

        Args:
            keys: 取得するキーのリスト

        Returns:
            取得に成功したキーと値の dict

        Example:
            >>> results = db.batch_get(["user1", "user2", "user3"])
            >>> print(results)  # {"user1": {...}, "user2": {...}}
        """
        if not keys:
            return {}

        results = {}
        missing_keys = []

        # 1. キャッシュから取得可能なものをチェック
        for key in keys:
            if self._cache.is_cached(key):
                val = self._cache.get(key)
                if val is not None:
                    results[key] = val
            else:
                missing_keys.append(key)

        if not missing_keys:
            return results

        # 2. DBから足りない分を一括取得
        placeholders = ",".join(["?"] * len(missing_keys))
        sql = f"SELECT key, value FROM {self._table} WHERE key IN ({placeholders})"  # nosec

        with self._lock:
            cursor = self._connection.execute(sql, tuple(missing_keys))
            for key, val_str in cursor:
                value = self._deserialize(val_str)
                self._cache.set(key, value)
                results[key] = value

        # 3. DBにも存在しなかったキーを「存在しない」としてキャッシュ
        found_keys = set(results.keys())
        for key in missing_keys:
            if key not in found_keys:
                self._cache.mark_cached(key)

        return results

    def pop(self, key: str, *args) -> Any:
        """dict.pop(key[, default])"""
        self._check_connection()
        if self._ensure_cached(key):
            value = self._cache.get(key)
            self._cache.delete(key)
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
        self._cache.clear()
        self._all_loaded = False
        with self._lock:
            self._connection.execute(f"DELETE FROM {self._table}")  # nosec

    def setdefault(self, key: str, default: Any = None) -> Any:
        """dict.setdefault(key, default)"""
        if self._ensure_cached(key):
            return self._cache.get(key)
        self[key] = default
        return default

    # ==================== Special Methods ====================

    def load_all(self) -> None:
        """一括読み込み: 全データをメモリに展開"""
        if self._all_loaded:
            return

        with self._lock:
            cursor = self._connection.execute(
                f"SELECT key, value FROM {self._table}"  # nosec
            )
            rows = list(cursor)  # ロック内でフェッチ

        for key, value in rows:
            self._cache.set(key, self._deserialize(value))

        self._all_loaded = True

    def refresh(self, key: str = None) -> None:
        """
        キャッシュを更新（DBから再読み込み）

        Args:
            key: 特定のキーのみ更新。Noneの場合は全キャッシュをクリアして再読み込み
        """
        if key is not None:
            # FAST PATH for performance
            if not self._lru_mode:
                self._data.pop(key, None)
                self._cached_keys.discard(key)
            else:
                self._cache.invalidate(key)
            self._ensure_cached(key)
        else:
            self.clear_cache()

    def is_cached(self, key: str) -> bool:
        """キーがキャッシュ済みかどうか"""
        # FAST PATH for performance
        if not self._lru_mode:
            return key in self._cached_keys
        return self._cache.is_cached(key)

    def batch_update(self, mapping: dict[str, Any]) -> None:
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
                f"INSERT OR REPLACE INTO {self._table} (key, value) VALUES (?, ?)",  # nosec
                params,
            )
            # キャッシュ更新
            for key, value in mapping.items():
                if self._lru_mode:
                    self._cache.set(key, value)
                else:
                    self._data[key] = value
                    self._cached_keys.add(key)
            cursor.execute("COMMIT")
        except Exception:
            cursor.execute("ROLLBACK")
            raise

    def batch_delete(self, keys: list[str]) -> None:
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
                f"DELETE FROM {self._table} WHERE key = ?",  # nosec
                params,
            )
            # キャッシュ更新
            for key in keys:
                if self._lru_mode:
                    self._cache.delete(key)
                else:
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

    def clear_cache(self) -> None:
        """
        メモリキャッシュをクリア

        DBのデータは削除せず、メモリ上のキャッシュのみ破棄します。
        """
        self._cache.clear()
        self._all_loaded = False

    def _delete_from_db_on_expire(self, key: str) -> None:
        """有効期限切れ時にDBからデータを削除 (内部用)"""
        with self._lock:
            if self._is_closed:
                return
            try:
                self._connection.execute(f'DELETE FROM "{self._table}" WHERE key = ?', (key,))  # nosec
            except apsw.Error as e:
                logger.error(f"SQL error during background expiration for key '{key}': {e}")

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
                "Cannot close connection while transaction is in progress. Please commit or rollback first."
            )

        # 子インスタンスに通知
        for child in self._child_instances:
            child._mark_parent_closed()

        self._child_instances.clear()
        self._is_closed = True

        if self._is_connection_owner:
            try:
                self._connection.close()
            except apsw.Error as e:
                # 接続クローズの失敗は警告に留める
                import warnings

                warnings.warn(f"Failed to close database connection: {e}", stacklevel=2)

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
            if hasattr(model, "model_dump"):
                data = {
                    "__pydantic_model__": f"{model.__class__.__module__}.{model.__class__.__qualname__}",
                    "__pydantic_data__": model.model_dump(),
                }
                self[key] = data
            else:
                raise TypeError(f"Object of type {type(model)} is not a Pydantic model")
        except Exception as e:
            raise TypeError(f"Failed to serialize Pydantic model: {e}")

    def get_model(self, key: str, model_class: type = None) -> Any:
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

        if isinstance(data, dict) and "__pydantic_model__" in data and "__pydantic_data__" in data:
            if model_class is None:
                # 自動検出は複雑なため、model_classを推奨
                raise ValueError("model_class must be provided for get_model()")

            # Pydanticモデルとして復元
            try:
                return model_class(**data["__pydantic_data__"])
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

    def execute(self, sql: str, parameters: tuple | None = None) -> apsw.Cursor:
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

    def execute_many(self, sql: str, parameters_list: list[tuple]) -> None:
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

    def fetch_one(self, sql: str, parameters: tuple = None) -> tuple | None:
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

    def fetch_all(self, sql: str, parameters: tuple = None) -> list[tuple]:
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

    def create_table(self, table_name: str, columns: dict, if_not_exists: bool = True, primary_key: str = None) -> None:
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
            if not any(primary_key.upper() in col.upper() and "PRIMARY KEY" in col.upper() for col in column_defs):
                column_defs.append(f"PRIMARY KEY ({safe_pk})")

        columns_sql = ", ".join(column_defs)
        sql = f"CREATE TABLE {if_not_exists_clause}{safe_table_name} ({columns_sql})"

        self.execute(sql)

    def create_index(
        self, index_name: str, table_name: str, columns: list[str], unique: bool = False, if_not_exists: bool = True
    ) -> None:
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

        sql = (
            f"CREATE {unique_clause}INDEX {if_not_exists_clause}{safe_index_name} ON {safe_table_name} ({columns_sql})"
        )
        self.execute(sql)

    def query(
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
        シンプルなSELECTクエリを実行

        Args:
            table_name: テーブル名（Noneの場合はデフォルトテーブル）
            columns: 取得するカラムのリスト（Noneの場合は全カラム）
            where: WHERE句の条件（パラメータバインディング使用推奨）
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

        # バリデーション
        self._validate_expression(
            where,
            strict_sql_validation,
            allowed_sql_functions,
            forbidden_sql_functions,
            override_allowed,
            context="where",
        )
        self._validate_expression(
            order_by,
            strict_sql_validation,
            allowed_sql_functions,
            forbidden_sql_functions,
            override_allowed,
            context="order_by",
        )
        if columns:
            for col in columns:
                # 関数使用の可能性を考慮して識別子サニタイズは行わないがバリデーションは行う
                self._validate_expression(
                    col,
                    strict_sql_validation,
                    allowed_sql_functions,
                    forbidden_sql_functions,
                    override_allowed,
                    context="column",
                )

        # カラム指定
        if columns is None:
            columns_sql = "*"
            # カラム名は後でPRAGMAから取得
        else:
            # 識別子（カラム名のみ）の場合はサニタイズ、式の場合はそのまま（バリデーション済み）
            safe_cols = []
            for col in columns:
                if IDENTIFIER_PATTERN.match(col):
                    safe_cols.append(self._sanitize_identifier(col))
                else:
                    safe_cols.append(col)
            columns_sql = ", ".join(safe_cols)

        # Validate limit is an integer and non-negative if provided
        if limit is not None:
            if not isinstance(limit, int):
                raise ValueError(f"limit must be an integer, got {type(limit).__name__}")
            if limit < 0:
                raise ValueError("limit must be non-negative")

        # SQL構築
        sql = f"SELECT {columns_sql} FROM {safe_table_name}"  # nosec

        if where:
            sql += f" WHERE {where}"

        if order_by:
            sql += f" ORDER BY {order_by}"

        if limit is not None:
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
                parts = re.split(r"\s+as\s+", col, flags=re.IGNORECASE)
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
        cursor = self.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return cursor.fetchone() is not None

    def list_tables(self) -> list[str]:
        """
        データベース内の全テーブル一覧を取得

        Returns:
            テーブル名のリスト

        Example:
            >>> tables = db.list_tables()
            >>> print(tables)  # ['data', 'users', 'posts']
        """
        cursor = self.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
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

    def alter_table_add_column(self, table_name: str, column_name: str, column_type: str, default: Any = None) -> None:
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
            # For default values: if it's a string, ensure it's properly quoted and escaped
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

    def get_table_schema(self, table_name: str) -> list[dict]:
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
            columns.append(
                {
                    "cid": row[0],
                    "name": row[1],
                    "type": row[2],
                    "notnull": bool(row[3]),
                    "default_value": row[4],
                    "pk": bool(row[5]),
                }
            )
        return columns

    def list_indexes(self, table_name: str = None) -> list[dict]:
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
                (table_name,),
            )
        else:
            cursor = self.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' ORDER BY name")

        indexes = []
        for row in cursor:
            if row[0] and not row[0].startswith("sqlite_"):  # Skip auto-created indexes
                indexes.append({"name": row[0], "table": row[1], "sql": row[2]})
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

        sql = f"INSERT INTO {safe_table_name} ({columns_sql}) VALUES ({placeholders})"  # nosec
        self.execute(sql, tuple(values))

        return self.get_last_insert_rowid()

    def sql_update(self, table_name: str, data: dict, where: str, parameters: tuple = None) -> int:
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

        sql = f"UPDATE {safe_table_name} SET {set_clause} WHERE {where}"  # nosec

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
        sql = f"DELETE FROM {safe_table_name} WHERE {where}"  # nosec
        self.execute(sql, parameters)
        return self._connection.changes()

    def upsert(self, table_name: str, data: dict, conflict_columns: list[str] = None) -> int:
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

            update_items = [
                f"{self._sanitize_identifier(col)} = excluded.{self._sanitize_identifier(col)}"
                for col in data.keys()
                if col not in conflict_columns
            ]

            if update_items:
                update_clause = ", ".join(update_items)
            else:
                # 全カラムが競合カラムの場合は、何もしない（既存データを保持）
                sql = f"INSERT INTO {safe_table_name} ({columns_sql}) VALUES ({placeholders}) "  # nosec
                sql += f"ON CONFLICT({conflict_cols_sql}) DO NOTHING"  # nosec
                self.execute(sql, tuple(values))
                # When DO NOTHING is triggered, no row is inserted, return 0
                # Check only the most recent operation's change count
                if self._connection.changes() == 0:
                    return 0
                return self.get_last_insert_rowid()

            sql = f"INSERT INTO {safe_table_name} ({columns_sql}) VALUES ({placeholders}) "  # nosec
            sql += f"ON CONFLICT({conflict_cols_sql}) DO UPDATE SET {update_clause}"  # nosec
        else:
            # INSERT OR REPLACE
            sql = f"INSERT OR REPLACE INTO {safe_table_name} ({columns_sql}) VALUES ({placeholders})"  # nosec

        self.execute(sql, tuple(values))
        return self.get_last_insert_rowid()

    def count(
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
        レコード数を取得

        Args:
            table_name: テーブル名（Noneの場合はデフォルトテーブル）
            where: WHERE句の条件（オプション）
            parameters: WHERE句のパラメータ
            strict_sql_validation: Trueの場合、未許可の関数等を含むクエリを拒否
            allowed_sql_functions: このクエリで一時的に許可するSQL関数のリスト
            forbidden_sql_functions: このクエリで一時的に禁止するSQL関数のリスト
            override_allowed: Trueの場合、インスタンス許可設定を無視

        Example:
            >>> total = db.count("users")
            >>> adults = db.count("users", "age >= ?", (18,))
        """
        if table_name is None:
            table_name = self._table

        safe_table_name = self._sanitize_identifier(table_name)

        # バリデーション
        self._validate_expression(
            where, strict_sql_validation, allowed_sql_functions, forbidden_sql_functions, override_allowed
        )

        sql = f"SELECT COUNT(*) FROM {safe_table_name}"  # nosec
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
        sql = f"SELECT EXISTS(SELECT 1 FROM {safe_table_name} WHERE {where})"  # nosec
        cursor = self.execute(sql, parameters)
        return bool(cursor.fetchone()[0])

    # ==================== Query Extensions ====================

    def query_with_pagination(
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
            strict_sql_validation: Trueの場合、未許可の関数等を含むクエリを拒否
            allowed_sql_functions: このクエリで一時的に許可するSQL関数のリスト
            forbidden_sql_functions: このクエリで一時的に禁止するSQL関数のリスト
            override_allowed: Trueの場合、インスタンス許可設定を無視

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

        # バリデーション
        self._validate_expression(
            where,
            strict_sql_validation,
            allowed_sql_functions,
            forbidden_sql_functions,
            override_allowed,
            context="where",
        )
        self._validate_expression(
            order_by,
            strict_sql_validation,
            allowed_sql_functions,
            forbidden_sql_functions,
            override_allowed,
            context="order_by",
        )
        self._validate_expression(
            group_by,
            strict_sql_validation,
            allowed_sql_functions,
            forbidden_sql_functions,
            override_allowed,
            context="group_by",
        )
        if columns:
            for col in columns:
                self._validate_expression(
                    col,
                    strict_sql_validation,
                    allowed_sql_functions,
                    forbidden_sql_functions,
                    override_allowed,
                    context="column",
                )

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
            # 識別子（カラム名のみ）の場合はサニタイズ、式の場合はそのまま（バリデーション済み）
            safe_cols = []
            for col in columns:
                if IDENTIFIER_PATTERN.match(col):
                    safe_cols.append(self._sanitize_identifier(col))
                else:
                    safe_cols.append(col)
            columns_sql = ", ".join(safe_cols)

        # SQL構築
        sql = f"SELECT {columns_sql} FROM {safe_table_name}"  # nosec

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
                parts = re.split(r"\s+as\s+", col, flags=re.IGNORECASE)
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

    def export_table_to_dict(self, table_name: str) -> list[dict]:
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

    def import_from_dict_list(self, table_name: str, data_list: list[dict]) -> int:
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
        sql = f"INSERT INTO {safe_table_name} ({columns_sql}) VALUES ({placeholders})"  # nosec

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
            "foreign_keys",
            "journal_mode",
            "synchronous",
            "cache_size",
            "temp_store",
            "locking_mode",
            "auto_vacuum",
            "page_size",
            "encoding",
            "user_version",
            "schema_version",
            "wal_autocheckpoint",
            "busy_timeout",
            "query_only",
            "recursive_triggers",
            "secure_delete",
            "table_info",
            "index_list",
            "index_info",
            "database_list",
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
                if not re.match(r"^[\w\-\.]+$", value):
                    raise ValueError(
                        "PRAGMA string value must contain only alphanumeric, underscore, dash, or dot characters"
                    )
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
                f"Failed to begin transaction: {e}", original_error=e if isinstance(e, apsw.Error) else None
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
                "No transaction in progress. Call begin_transaction() first or use the transaction() context manager."
            )

        try:
            self.execute("COMMIT")
            self._in_transaction = False
            self._transaction_depth = 0
        except Exception as e:
            # コミット失敗時は状態を維持（ロールバックが必要）
            raise NanaSQLiteDatabaseError(
                f"Failed to commit transaction: {e}", original_error=e if isinstance(e, apsw.Error) else None
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
                "No transaction in progress. Call begin_transaction() first or use the transaction() context manager."
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
                f"Failed to rollback transaction: {e}", original_error=e if isinstance(e, apsw.Error) else None
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

    def table(
        self,
        table_name: str,
        cache_strategy: CacheType | Literal["unbounded", "lru"] | None = None,
        cache_size: int | None = None,
    ):
        """
        サブテーブル用のNanaSQLiteインスタンスを取得

        新しいインスタンスを作成しますが、SQLite接続とロックは共有します。
        これにより、複数のテーブルインスタンスが同じ接続を使用して
        スレッドセーフに動作します。

        Args:
            table_name: テーブル名
            cache_strategy: このテーブル用のキャッシュ戦略 (デフォルト: 親と同じ)
            cache_size: このテーブル用のキャッシュサイズ (デフォルト: 親と同じ)

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

        # 指定がなければデフォルト（UNBOUNDED）
        strat = cache_strategy if cache_strategy is not None else CacheType.UNBOUNDED
        size = cache_size

        child = NanaSQLite(
            self._db_path,
            table=table_name,
            cache_strategy=strat,
            cache_size=size,
            _shared_connection=self._connection,
            _shared_lock=self._lock,
        )

        # If the parent is the connection owner, the child is not.
        # This ensures only one instance (the owner) attempts to close the connection.
        if self._is_connection_owner:
            child._is_connection_owner = False

        # 子インスタンスを追跡 (WeakSetに直接オブジェクトを追加すると、WeakSetが弱参照を保持する)
        self._child_instances.add(child)

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
