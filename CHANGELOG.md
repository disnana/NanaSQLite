# 変更履歴 / Changelog

[日本語](#日本語) | [English](#english)

---

## 日本語

### [1.1.0] - 2025-12-19

#### 追加
- **カスタム例外クラスの導入**:
  - `NanaSQLiteError` (基底クラス)
  - `NanaSQLiteValidationError` (バリデーションエラー)
  - `NanaSQLiteDatabaseError` (データベース操作エラー)
  - `NanaSQLiteTransactionError` (トランザクション関連エラー)
  - `NanaSQLiteConnectionError` (接続エラー)
  - `NanaSQLiteLockError` (ロックエラー、将来用)
  - `NanaSQLiteCacheError` (キャッシュエラー、将来用)

- **バッチ取得機能 (`batch_get`)**:
  - `batch_get(keys: List[str])` による効率的な複数キーの一括ロード
  - `AsyncNanaSQLite.abatch_get(keys)` による非同期サポート
  - 1回のクエリで複数データを取得しキャッシュを最適化
- **トランザクション管理の強化**:
  - トランザクション状態の追跡（`_in_transaction`, `_transaction_depth`）
  - ネストしたトランザクションの検出とエラー発生
  - `in_transaction()` メソッドの追加
  - トランザクション中の接続クローズを防止
  - トランザクション外でのcommit/rollbackを検出

- **非同期版トランザクション対応**:
  - `AsyncNanaSQLite.begin_transaction()`
  - `AsyncNanaSQLite.commit()`
  - `AsyncNanaSQLite.rollback()`
  - `AsyncNanaSQLite.in_transaction()`
  - `AsyncNanaSQLite.transaction()` (コンテキストマネージャ)
  - `_AsyncTransactionContext` クラスの実装

- **リソースリーク対策**:
  - 親インスタンスが子インスタンスを弱参照で追跡
  - 親が閉じられた際、子インスタンスに通知
  - 孤立した子インスタンスの使用を防止
  - `_check_connection()` メソッドの追加
  - `_mark_parent_closed()` メソッドの追加

#### 改善
- **エラーハンドリングの強化**:
  - `execute()` メソッドにエラーハンドリングを追加
  - APSWの例外を `NanaSQLiteDatabaseError` でラップ
  - 元のエラー情報を保持（`original_error` 属性）
  - 接続状態のチェックを各メソッドに追加
  - `_sanitize_identifier()` で `NanaSQLiteValidationError` を使用

- **`__setitem__` メソッドに接続チェックを追加**

#### ドキュメント
- **新規ドキュメント**:
  - `docs/ja/error_handling.md` - エラーハンドリングガイド
  - `docs/ja/transaction_guide.md` - トランザクションガイド
  - `docs/ja/implementation_status.md` - 実装状況と今後の計画
  - `tests/test_enhancements.py` - 強化機能のテスト（21件）

- **README更新**:
  - トランザクションサポートのセクションを追加
  - カスタム例外のサンプルコードを追加
  - 非同期版のトランザクションサンプルを追加

#### テスト
- **新規テスト**（21件）:
  - カスタム例外クラスのテスト（5件）
  - トランザクション機能の強化テスト（6件）
  - リソース管理のテスト（3件）
  - エラーハンドリングのテスト（2件）
  - トランザクションと例外の組み合わせテスト（2件）
  - 非同期版トランザクションのテスト（3件）

#### 修正
- セキュリティテストで `NanaSQLiteValidationError` を期待するように修正

---

### [1.1.0a3] - 2025-12-17

#### ドキュメント改善
- **`table()`メソッドの使用上の注意を追加**:
  - README.mdに重要な使用上の注意セクションを追加（英語・日本語）
  - 同じテーブルへの複数インスタンス作成に関する警告
  - コンテキストマネージャ使用の推奨
  - ベストプラクティスの明記
- **docstring改善**:
  - `NanaSQLite.table()`のdocstringに詳細な注意事項を追加
  - `AsyncNanaSQLite.table()`のdocstringに詳細な注意事項を追加
  - 非推奨パターンと推奨パターンの具体例を追加
- **将来的な改善計画**:
  - `etc/future_plans/`ディレクトリに改善提案を文書化
  - 重複インスタンス検出警告機能（提案B）
  - 接続状態チェック機能（提案B）
  - 共有キャッシュ機構（提案C - 保留）

#### 分析・調査
- **table()機能の包括的な調査を実施**:
  - ストレステスト: 7件すべて合格
  - エッジケーステスト: 10件実施
  - 並行処理テスト: 5件すべて合格
  - **発見された問題**: 2件（軽微な設計上の制限）
    1. 同一テーブルへの複数インスタンスでキャッシュ不整合（ドキュメント化で対応）
    2. close後のサブインスタンスアクセス（ドキュメント化で対応）
  - **結論**: 本番環境で使用可能、パフォーマンス問題なし

### [1.1.0dev2] - 2025-12-16

#### 現在の開発状況
- 開発中のバージョン
- テスト実施中（`test_concurrent_table_writes.py`で15個のテスト全てパス）

### [1.1.0dev1] - 2025-12-15

#### 追加
- **マルチテーブルサポート（`table()`メソッド）**: 同一データベース内の複数テーブルを安全に操作
  - `db.table(table_name)`で別テーブル用のインスタンスを取得
  - **接続とロックの共有**: 複数のテーブルインスタンスが同じSQLite接続とスレッドロックを共有
  - スレッドセーフ: 複数スレッドから異なるテーブルへの同時書き込みが安全に動作
  - メモリ効率: 接続を再利用することでリソースを節約
  - **同期版**: `NanaSQLite.table(table_name)` → `NanaSQLite`インスタンス
  - **非同期版**: `await AsyncNanaSQLite.table(table_name)` → `AsyncNanaSQLite`インスタンス
  - キャッシュ分離: 各テーブルインスタンスは独立したメモリキャッシュを保持

#### 内部実装の改善
- **スレッドセーフティの強化**: 全データベース操作に`threading.RLock`を追加
  - 読み込み（`_read_from_db`）、書き込み（`_write_to_db`）、削除（`_delete_from_db`）
  - クエリ実行（`execute`, `execute_many`）
  - トランザクション操作
- **接続管理の改善**:
  - `_shared_connection`パラメータで接続の共有をサポート
  - `_shared_lock`パラメータでロックの共有をサポート
  - `_is_connection_owner`フラグで接続の所有権を管理
  - `close()`メソッドは接続の所有者のみが実行

#### テスト
- **15の包括的なテストケース**（全てパス）:
  - 同期版マルチテーブル並行書き込みテスト（2テーブル、複数テーブル）
  - 非同期版マルチテーブル並行書き込みテスト（2テーブル、複数テーブル）
  - ストレステスト（1000件の並行書き込み）
  - キャッシュ分離テスト
  - テーブル切り替えテスト
  - エッジケーステスト

#### 互換性
- **完全な後方互換性**: 既存のコードに影響なし
- 新しいパラメータはすべてオプショナル（内部使用）

### [1.0.3rc7] - 2025-12-10

#### 追加
- **非同期サポート（AsyncNanaSQLite）**: 非同期アプリケーション向けの完全な非同期インターフェース
  - `AsyncNanaSQLite`クラス: 全操作の非同期版を提供
  - **専用スレッドプールエグゼキューター**: 設定可能なmax_workers（デフォルト5）で最適化
  - `ThreadPoolExecutor`による高性能な並行処理
  - FastAPI、aiohttp等の非同期フレームワークで安全に使用可能
  - 非同期dict風インターフェース: `await db.aget()`, `await db.aset()`, `await db.adelete()`
  - 非同期バッチ操作: `await db.batch_update()`, `await db.batch_delete()`
  - 非同期SQL実行: `await db.execute()`, `await db.query()`
  - 非同期コンテキストマネージャ: `async with AsyncNanaSQLite(...) as db:`
  - 並行処理サポート: 複数の非同期操作を並行実行可能
  - 自動リソース管理: スレッドプールの自動クリーンアップ
- **包括的なテストスイート**: 100以上の非同期テストケース
  - 基本操作、並行処理、エラーハンドリング、パフォーマンステスト
  - 全テストが合格
- **完全な後方互換性**: 既存の`NanaSQLite`クラスは変更なし

#### パフォーマンス改善
- 非同期アプリでのブロッキング防止により、イベントループの応答性が向上
- 専用スレッドプールによる高効率な並行処理（設定可能なワーカー数）
- APSW + スレッドプールの組み合わせで最適なパフォーマンス
- 高負荷環境向けにmax_workersを調整可能（5～50）

### [1.0.3rc6] - 2025-12-10

#### 追加
- **`get_fresh(key, default=None)`メソッド**: DBから直接読み込み、キャッシュを更新して値を返す
  - `execute()`でDBを直接変更した後のキャッシュ同期に便利
  - `_read_from_db`を直接使用してオーバーヘッドを最小化

### [1.0.3rc5] - 2025-12-10

#### パフォーマンス改善
- **`batch_update()`の最適化**: `executemany`使用で大量データ処理が10-30%高速化
- **`batch_delete()`の最適化**: `executemany`使用で一括削除が高速化
- **`__contains__()`の最適化**: 軽量なEXISTSクエリ使用で存在確認が高速化（大きなvalueの場合に効果大）

#### IDE/型サポート強化
- `from __future__ import annotations` 追加
- `Dict[str, Any]`、`Set[str]`等の具体的な型アノテーション
- `Optional[Tuple]`等のより明確な引数型

#### ドキュメント
- `execute()`メソッドにキャッシュ一貫性に関する警告を追加
- docstringの改善（Returns、警告セクション追加）

#### バグ修正
- Gitマージコンフリクトの解消（order_by検証の正規表現）
- ReDoS脆弱性の修正（カンマ分割方式に変更）

### [1.0.3rc4] - 2025-12-09

#### 追加
- **22の新しいSQLiteラッパー関数**
  - スキーマ管理: `drop_table()`, `drop_index()`, `alter_table_add_column()`, `get_table_schema()`, `list_indexes()`
  - データ操作: `sql_insert()`, `sql_update()`, `sql_delete()`, `upsert()`, `count()`, `exists()`
  - クエリ拡張: `query_with_pagination()` (offset/group_by対応)
  - ユーティリティ: `vacuum()`, `get_db_size()`, `export_table_to_dict()`, `import_from_dict_list()`, `get_last_insert_rowid()`, `pragma()`
  - トランザクション: `begin_transaction()`, `commit()`, `rollback()`, `transaction()`コンテキストマネージャ
- 35の新しいテストケース（全て合格）
- 完全な後方互換性維持

### [1.0.3rc3] - 2025-12-09

#### 追加
- **Pydantic互換性**
  - `set_model()`, `get_model()` メソッド
  - ネストされたモデルとオプショナルフィールドのサポート
- **直接SQL実行機能**
  - `execute()`, `execute_many()`, `fetch_one()`, `fetch_all()` メソッド
  - パラメータバインディングによるSQLインジェクション対策
- **SQLiteラッパー関数**
  - `create_table()`, `create_index()`, `query()` メソッド
  - `table_exists()`, `list_tables()` ヘルパー関数
- 32の新しいテストケース
- 英語・日本語ドキュメントの更新
- 非同期対応に関する相談文書

### [1.0.0] - 2025-12-09

#### 追加
- 初回リリース
- dict風インターフェース（`db["key"] = value`）
- APSWによるSQLite即時永続化
- 遅延ロード（アクセス時にキャッシュ）
- 一括ロード（`bulk_load=True`）
- ネスト構造サポート（30階層テスト済み）
- パフォーマンス最適化（WAL、mmap、cache_size）
- バッチ操作（`batch_update`、`batch_delete`）
- コンテキストマネージャ対応
- 完全なdictメソッド互換性
- 型ヒント（PEP 561）
- バイリンガルドキュメント（英語/日本語）
- GitHub Actions CI（Python 3.9-3.13、Ubuntu/Windows/macOS）

---

## English

### [1.1.0] - 2025-12-19

#### Added
- **Custom Exception Classes**:
  - `NanaSQLiteError` (base class)
  - `NanaSQLiteValidationError` (validation errors)
  - `NanaSQLiteDatabaseError` (database operation errors)
  - `NanaSQLiteTransactionError` (transaction-related errors)
  - `NanaSQLiteConnectionError` (connection errors)
  - `NanaSQLiteLockError` (lock errors, for future use)
  - `NanaSQLiteCacheError` (cache errors, for future use)

- **Batch Retrieval (`batch_get`)**:
  - Efficiently load multiple keys with `batch_get(keys: List[str])`
  - Async support via `AsyncNanaSQLite.abatch_get(keys)`
  - Optimizes cache by fetching multiple items in a single query
- **Enhanced Transaction Management**:
  - Transaction state tracking (`_in_transaction`, `_transaction_depth`)
  - Detection and error reporting for nested transactions
  - Added `in_transaction()` method
  - Prevention of connection closure during transactions
  - Detection of commit/rollback outside transactions

- **Async Transaction Support**:
  - `AsyncNanaSQLite.begin_transaction()`
  - `AsyncNanaSQLite.commit()`
  - `AsyncNanaSQLite.rollback()`
  - `AsyncNanaSQLite.in_transaction()`
  - `AsyncNanaSQLite.transaction()` (context manager)
  - `_AsyncTransactionContext` class implementation

- **Resource Leak Prevention**:
  - Parent instance tracks child instances with weak references
  - Notification to child instances when parent is closed
  - Prevention of orphaned child instance usage
  - Added `_check_connection()` method
  - Added `_mark_parent_closed()` method

#### Improvements
- **Enhanced Error Handling**:
  - Added error handling to `execute()` method
  - Wraps APSW exceptions with `NanaSQLiteDatabaseError`
  - Preserves original error information (`original_error` attribute)
  - Added connection state checks to each method
  - Uses `NanaSQLiteValidationError` in `_sanitize_identifier()`

- **Added connection check to `__setitem__` method**

#### Documentation
- **New Documentation**:
  - `docs/en/error_handling.md` - Error handling guide
  - `docs/en/transaction_guide.md` - Transaction guide
  - `tests/test_enhancements.py` - Tests for enhanced features (21 tests)

- **README Updates**:
  - Added transaction support section
  - Added custom exception sample code
  - Added async transaction samples

#### Tests
- **New Tests** (21 tests):
  - Custom exception class tests (5 tests)
  - Transaction feature enhancement tests (6 tests)
  - Resource management tests (3 tests)
  - Error handling tests (2 tests)
  - Transaction and exception combination tests (2 tests)
  - Async transaction tests (3 tests)

#### Fixes
- Fixed security tests to expect `NanaSQLiteValidationError`

---

### [1.1.0a3] - 2025-12-17

#### Documentation Improvements
- **Added usage notes for `table()` method**:
  - Added important usage notes section to README.md (English & Japanese)
  - Warning about creating multiple instances for the same table
  - Recommendation to use context managers
  - Best practices clarification
- **Improved docstrings**:
  - Added detailed notes to `NanaSQLite.table()` docstring
  - Added detailed notes to `AsyncNanaSQLite.table()` docstring
  - Added specific examples of deprecated and recommended patterns
- **Future improvement plans**:
  - Documented improvement proposals in `etc/future_plans/` directory
  - Duplicate instance detection warning feature (Proposal B)
  - Connection state check feature (Proposal B)
  - Shared cache mechanism (Proposal C - on hold)

#### Analysis & Investigation
- **Comprehensive investigation of table() functionality**:
  - Stress tests: All 7 tests passed
  - Edge case tests: 10 tests conducted
  - Concurrency tests: All 5 tests passed
  - **Issues found**: 2 (minor design limitations)
    1. Cache inconsistency with multiple instances for same table (addressed with documentation)
    2. Sub-instance access after close (addressed with documentation)
  - **Conclusion**: Ready for production use, no performance issues

---

### [1.1.0dev2] - 2025-12-16

#### Current Development Status
- Development version in progress
- Testing in progress (all 15 tests in `test_concurrent_table_writes.py` passing)

### [1.1.0dev1] - 2025-12-15

#### Added
- **Multi-table Support (`table()` method)**: Safely operate on multiple tables within the same database
  - Get an instance for another table with `db.table(table_name)`
  - **Shared connection and lock**: Multiple table instances share the same SQLite connection and thread lock
  - Thread-safe: Concurrent writes to different tables from multiple threads work safely
  - Memory efficient: Reuses connections to save resources
  - **Sync version**: `NanaSQLite.table(table_name)` → `NanaSQLite` instance
  - **Async version**: `await AsyncNanaSQLite.table(table_name)` → `AsyncNanaSQLite` instance
  - Cache isolation: Each table instance maintains independent in-memory cache

#### Internal Implementation Improvements
- **Enhanced thread safety**: Added `threading.RLock` to all database operations
  - Read (`_read_from_db`), write (`_write_to_db`), delete (`_delete_from_db`)
  - Query execution (`execute`, `execute_many`)
  - Transaction operations
- **Improved connection management**:
  - `_shared_connection` parameter for connection sharing
  - `_shared_lock` parameter for lock sharing
  - `_is_connection_owner` flag for connection ownership management
  - `close()` method only executed by connection owner

#### Tests
- **15 comprehensive test cases** (all passing):
  - Sync multi-table concurrent write tests (2 tables, multiple tables)
  - Async multi-table concurrent write tests (2 tables, multiple tables)
  - Stress test (1000 concurrent writes)
  - Cache isolation tests
  - Table switching tests
  - Edge case tests

#### Compatibility
- **Full backward compatibility**: No impact on existing code
- All new parameters are optional (internal use)

### [1.0.3rc7] - 2025-12-10

#### Added
- **Async Support (AsyncNanaSQLite)**: Complete async interface for async applications
  - `AsyncNanaSQLite` class: Provides async versions of all operations
  - **Dedicated ThreadPoolExecutor**: Configurable max_workers (default 5) for optimization
  - High-performance concurrent processing with `ThreadPoolExecutor`
  - Safe to use with async frameworks like FastAPI, aiohttp
  - Async dict-like interface: `await db.aget()`, `await db.aset()`, `await db.adelete()`
  - Async batch operations: `await db.batch_update()`, `await db.batch_delete()`
  - Async SQL execution: `await db.execute()`, `await db.query()`
  - Async context manager: `async with AsyncNanaSQLite(...) as db:`
  - Concurrent operations support: Multiple async operations can run concurrently
  - Automatic resource management: Thread pool auto-cleanup
- **Comprehensive test suite**: 100+ async test cases
  - Basic operations, concurrency, error handling, performance tests
  - All tests passing
- **Full backward compatibility**: Existing `NanaSQLite` class unchanged

#### Performance Improvements
- Prevents blocking in async apps, improving event loop responsiveness
- Dedicated thread pool enables highly efficient concurrent processing (configurable workers)
- Optimal performance with APSW + thread pool combination
- Tunable max_workers for high-load environments (5-50)

### [1.0.3rc6] - 2025-12-10

#### Added
- **`get_fresh(key, default=None)` method**: Read directly from DB, update cache, and return value
  - Useful for cache synchronization after direct DB changes via `execute()`
  - Uses `_read_from_db` directly to minimize overhead

### [1.0.3rc5] - 2025-12-10

#### Performance Improvements
- **`batch_update()` optimization**: 10-30% faster with `executemany`
- **`batch_delete()` optimization**: Faster bulk deletion with `executemany`
- **`__contains__()` optimization**: Lightweight EXISTS query (faster for large values)

#### IDE/Type Support Enhancements
- Added `from __future__ import annotations`
- Specific type annotations: `Dict[str, Any]`, `Set[str]`
- Clearer parameter types: `Optional[Tuple]`

#### Documentation
- Added cache consistency warning to `execute()` method
- Improved docstrings (Returns, Warning sections)

#### Bug Fixes
- Resolved Git merge conflicts (order_by regex validation)
- Fixed ReDoS vulnerability (switched to comma-split approach)

### [1.0.3rc4] - 2025-12-09

#### Added
- **22 new SQLite wrapper functions**
  - Schema management: `drop_table()`, `drop_index()`, `alter_table_add_column()`, `get_table_schema()`, `list_indexes()`
  - Data operations: `sql_insert()`, `sql_update()`, `sql_delete()`, `upsert()`, `count()`, `exists()`
  - Query extensions: `query_with_pagination()` (with offset/group_by support)
  - Utilities: `vacuum()`, `get_db_size()`, `export_table_to_dict()`, `import_from_dict_list()`, `get_last_insert_rowid()`, `pragma()`
  - Transactions: `begin_transaction()`, `commit()`, `rollback()`, `transaction()` context manager
- 35 new test cases (all passing)
- Complete backward compatibility maintained

### [1.0.3rc3] - 2025-12-09

#### Added
- **Pydantic compatibility**
  - `set_model()`, `get_model()` methods
  - Support for nested models and optional fields
- **Direct SQL execution**
  - `execute()`, `execute_many()`, `fetch_one()`, `fetch_all()` methods
  - SQL injection protection via parameter binding
- **SQLite wrapper functions**
  - `create_table()`, `create_index()`, `query()` methods
  - `table_exists()`, `list_tables()` helper functions
- 32 new test cases
- Updated English/Japanese documentation
- Async support consultation document

### [1.0.0] - 2025-12-09

#### Added
- Initial release
- Dict-like interface (`db["key"] = value`)
- Instant persistence to SQLite via APSW
- Lazy load (on-access) caching
- Bulk load (`bulk_load=True`) for startup loading
- Nested structure support (tested up to 30 levels)
- Performance optimizations (WAL, mmap, cache_size)
- Batch operations (`batch_update`, `batch_delete`)
- Context manager support
- Full dict method compatibility
- Type hints (PEP 561)
- Bilingual documentation (English/Japanese)
- GitHub Actions CI (Python 3.9-3.13, Ubuntu/Windows/macOS)
