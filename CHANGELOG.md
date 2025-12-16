# 変更履歴 / Changelog

[日本語](#日本語) | [English](#english)

---

## 日本語

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
