# 変更履歴 / Changelog

[日本語](#日本語) | [English](#english)

---

## 日本語

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
