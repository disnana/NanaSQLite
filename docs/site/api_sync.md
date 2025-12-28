# NanaSQLite API リファレンス

同期版 `NanaSQLite` クラスの完全なドキュメントです。

## クラス: `NanaSQLite`

```python
class NanaSQLite(MutableMapping)
```

SQLiteを使用した、dict互換のラッパーです。即時永続化とインテリジェントなキャッシュを提供します。
辞書のシンプルさとSQLiteの永続性・クエリ能力を両立させたい用途に最適です。

---

## コンストラクタ

### `__init__`

```python
def __init__(self, db_path: str, table: str = "data", bulk_load: bool = False,
             optimize: bool = True, cache_size_mb: int = 64,
             cache_strategy: CacheType = CacheType.UNBOUNDED,
             cache_size: int = 0,
             cache_ttl: float | None = None,
             cache_persistence_ttl: bool = False,
             encryption_key: str | bytes | None = None,
             encryption_mode: str = "aes-gcm",
             strict_sql_validation: bool = True,
             allowed_sql_functions: list[str] | None = None,
             forbidden_sql_functions: list[str] | None = None,
             max_clause_length: int | None = 1000)
```

NanaSQLiteデータベース接続を初期化します。

**パラメータ:**

- `db_path` (str): SQLiteデータベースファイルのパス。
- `table` (str, 任意): ストレージに使用するテーブル名。デフォルトは `"data"`。
- `bulk_load` (bool, 任意): `True` の場合、初期化時に全データをメモリに読み込みます。デフォルトは `False`。
- `optimize` (bool, 任意): `True` の場合、WALモードなどの最適化を適用します。デフォルトは `True`。
- `cache_size_mb` (int, 任意): SQLiteキャッシュサイズ（MB）。デフォルトは `64`。
- `cache_strategy` (CacheType, 任意): `CacheType.UNBOUNDED` or `LRU` or `TTL`. v1.3.0以降。
- `cache_size` (int, 任意): `LRU`/`FIFO` 戦略時の最大項目数。
- `cache_ttl` (float, 任意): `TTL` 戦略時の有効期限（秒）。
- `cache_persistence_ttl` (bool, 任意): `True` の場合、期限切れ時にDBからも削除。
- `encryption_key` (str | bytes, 任意): 暗号化キー。 v1.3.1以降。
- `encryption_mode` (str, 任意): `"aes-gcm"` (標準), `"chacha20"`, `"fernet"`。
- `strict_sql_validation` (bool, 任意): SQLインジェクション防止。デフォルトは `True`。
- `allowed_sql_functions` (list[str], 任意): 許可するSQL関数。
- `forbidden_sql_functions` (list[str], 任意): 禁止するSQL関数。
- `max_clause_length` (int, 任意): SQL句の最大長。デフォルトは `1000`。

---

## コアメソッド

### `close`

```python
def close(self) -> None
```

データベース接続を閉じます。

**例外:**
- `NanaSQLiteTransactionError`: トランザクション中に呼び出された場合。

**注意:** `.table()` で作成されたインスタンスの場合、元の接続所有者のみがデータベースを閉じます。

### `table`

```python
def table(self, table_name: str, cache_strategy: CacheType = None,
          cache_size: int = None) -> NanaSQLite
```

指定したサブテーブル用の新しい `NanaSQLite` インスタンスを返します。

新しいインスタンスは親と同じ接続とロックを共有するため、スレッドセーフであり、データベースロックの問題を防ぎます。

**パラメータ:**
- `table_name` (str): サブテーブルの名前。
- `cache_strategy` (CacheType, 任意): このテーブル専用のキャッシュ戦略。指定しない場合は親の設定を継承。
- `cache_size` (int, 任意): このテーブル専用のキャッシュサイズ。

**戻り値:**
- `NanaSQLite`: 指定したテーブルを操作する新しいインスタンス。

---

## 辞書インターフェース

NanaSQLiteは `MutableMapping` を実装しているため、標準のPython `dict` のように動作します。

### `__getitem__`
```python
db["key"]
```
値を取得します。遅延ロード（メモリにない場合はDBから読み込み）を使用します。

### `__setitem__`
```python
db["key"] = value
```
値を設定します。即座にSQLiteに永続化し、メモリキャッシュを更新します。

### `__delitem__`
```python
del db["key"]
```
キーを削除します。メモリとSQLiteの両方から即座に削除されます。

### `__contains__`
```python
"key" in db
```
存在確認を行います。メモリにない場合は最適化された `SELECT 1` クエリを使用します。

### `__len__`
```python
len(db)
```
データベース内の総キー数を返します。

### `get`
```python
def get(self, key: str, default: Any = None) -> Any
```
キーが存在すればその値を、なければ `default` を返します。

### `setdefault`
```python
def setdefault(self, key: str, default: Any = None) -> Any
```
キーが存在すればその値を返します。なければ `default` で挿入し、その値を返します。

### `pop`
```python
def pop(self, key: str, *args) -> Any
```
キーを削除してその値を返します。キーがない場合、`default` があればそれを返し、なければ `KeyError` を発生させます。

### `update`
```python
def update(self, mapping: dict = None, **kwargs) -> None
```
辞書やキーワード引数でデータベースを更新します。大量の更新には `batch_update()` を推奨します。

### `clear`
```python
def clear(self) -> None
```
データベースから全アイテムを削除（テーブルを空にする）し、メモリキャッシュもクリアします。

### `clear_cache`
```python
def clear_cache(self) -> None
```
データベースには影響を与えず、メモリ上のキャッシュのみを完全にクリアします。

### `keys`
```python
def keys(self) -> list[str]
```
全キーのリストを返します。

### `values`
```python
def values(self) -> list[Any]
```
全値のリストを返します。**一括ロード（全データのメモリ読み込み）が発生します。**

### `items`
```python
def items(self) -> list[tuple[str, Any]]
```
全キー・値ペアのリストを返します。**一括ロードが発生します。**

### `to_dict`
```python
def to_dict(self) -> dict
```
データベース全体を標準のPython辞書に変換します。

### `copy`
```python
def copy(self) -> dict
```
`to_dict()` のエイリアスです。

---

## データ管理

### `load_all`

```python
def load_all(self) -> None
```

データベースの全データをメモリキャッシュに読み込みます。以降の読み込みはメモリのみとなるため高速です。

### `refresh`

```python
def refresh(self, key: str = None) -> None
```

内部キャッシュをデータベースから更新します。

**パラメータ:**
- `key` (str, 任意): 指定された場合、そのキーのみ更新します。`None` の場合、キャッシュ全体をクリアして再読み込みします。

### `get_fresh`

```python
def get_fresh(self, key: str, default: Any = None) -> Any
```

キャッシュをバイパスしてDBから最新の値を直接取得し、キャッシュを更新します。

### `batch_get`

```python
def batch_get(self, keys: list[str]) -> dict[str, Any]
```

複数のキーを1回のクエリで効率的に取得します。

### `batch_update`

```python
def batch_update(self, mapping: dict[str, Any]) -> None
```

単一のトランザクションを使用して一括書き込みを行います。個別の更新より大幅に（10〜100倍）高速です。

### `batch_delete`

```python
def batch_delete(self, keys: list[str]) -> None
```

単一のトランザクションを使用して一括削除を行います。

### `is_cached`

```python
def is_cached(self, key: str) -> bool
```

キーが現在メモリキャッシュに読み込まれているかを確認します。

---

## トランザクション制御

### `begin_transaction`

```python
def begin_transaction(self) -> None
```
手動でトランザクションを開始します (`BEGIN IMMEDIATE`)。
**例外:** 既にトランザクション中の場合 `NanaSQLiteTransactionError`。

### `commit`

```python
def commit(self) -> None
```
現在のトランザクションをコミットします。

### `rollback`

```python
def rollback(self) -> None
```
現在のトランザクションをロールバックします。

### `in_transaction`

```python
def in_transaction(self) -> bool
```
現在トランザクション中の場合 `True` を返します。

### `transaction`

```python
def transaction(self)
```
自動トランザクション処理のためのコンテキストマネージャです。
正常終了時にコミット、例外発生時にロールバックします。

```python
with db.transaction():
    db["a"] = 1
    db["b"] = 2
```

---

## SQLラッパー (CRUD)

生のSQLを書かずに一般的なSQL操作を安全に行うためのヘルパーメソッドです。

### `sql_insert`

```python
def sql_insert(self, table_name: str, data: dict) -> int
```
指定したテーブルに行を挿入します。
**戻り値:** 挿入された行の `ROWID`。

### `sql_update`

```python
def sql_update(self, table_name: str, data: dict, where: str, parameters: tuple = None) -> int
```
`where` 条件に一致する行を更新します。
**戻り値:** 影響を受けた行数。

### `sql_delete`

```python
def sql_delete(self, table_name: str, where: str, parameters: tuple = None) -> int
```
`where` 条件に一致する行を削除します。
**戻り値:** 影響を受けた行数。

### `upsert`

```python
def upsert(self, table_name: str, data: dict, conflict_columns: list[str] = None) -> int
```
"Insert or Replace" または "Insert ... ON CONFLICT DO UPDATE" 操作を行います。

**パラメータ:**
- `conflict_columns`: 指定された場合、`ON CONFLICT (...) DO UPDATE` を生成します。`None` の場合、`INSERT OR REPLACE` を使用します。

---

## クエリ

### `query`

```python
def query(self, table_name: str = None, columns: list[str] = None,
          where: str = None, parameters: tuple = None,
          order_by: str = None, limit: int = None,
          strict_sql_validation: bool = None, ...) -> list[dict]
```

`SELECT` クエリを実行し、結果を辞書のリストとして返します。

**パラメータ:**
- `table_name`:対象テーブル。デフォルトはメインデータテーブル。
- `columns`: 取得するカラムのリスト。デフォルトは `*`。
- `where`: SQL `WHERE` 句（"WHERE" という単語は不要）。
- `parameters`: `where` 句のプレースホルダに対する値のタプル。
- `limit`: 取得する最大行数。

### `query_with_pagination`

```python
def query_with_pagination(self, table_name: str = None, ..., offset: int = None, group_by: str = None) -> list[dict]
```

`offset`（ページネーション）と `group_by` をサポートする `query` の拡張版です。

### `count`

```python
def count(self, table_name: str = None, where: str = None, parameters: tuple = None, ...) -> int
```
条件に一致する行数を返します。

### `exists`

```python
def exists(self, table_name: str, where: str, parameters: tuple = None) -> bool
```
条件に一致する行が存在するか効率的に確認します（`SELECT 1 ... LIMIT 1` を使用）。

---

## 直接SQL実行

### `execute`

```python
def execute(self, sql: str, parameters: tuple | None = None) -> apsw.Cursor
```
生のSQLステートメントを実行します。
**戻り値:** `apsw.Cursor` オブジェクト。

### `execute_many`

```python
def execute_many(self, sql: str, parameters_list: list[tuple]) -> None
```
同じSQLステートメントを異なるパラメータで複数回実行します（一括実行）。

### `fetch_one`

```python
def fetch_one(self, sql: str, parameters: tuple = None) -> tuple | None
```
SQLを実行し、最初の行（または `None`）を返します。

### `fetch_all`

```python
def fetch_all(self, sql: str, parameters: tuple = None) -> list[tuple]
```
SQLを実行し、全行を返します。

---

## スキーマ管理

### `create_table`

```python
def create_table(self, table_name: str, columns: dict, if_not_exists: bool = True, primary_key: str = None) -> None
```
新しいテーブルを作成します。
**例:** `db.create_table("users", {"id": "INTEGER", "name": "TEXT"}, primary_key="id")`

### `create_index`

```python
def create_index(self, index_name: str, table_name: str, columns: list[str], unique: bool = False, if_not_exists: bool = True) -> None
```
テーブルにインデックスを作成します。

### `alter_table_add_column`

```python
def alter_table_add_column(self, table_name: str, column_name: str, column_type: str, default: Any = None) -> None
```
既存のテーブルにカラムを追加します。

### `drop_table`

```python
def drop_table(self, table_name: str, if_exists: bool = True) -> None
```
テーブルを削除します。

### `drop_index`

```python
def drop_index(self, index_name: str, if_exists: bool = True) -> None
```
インデックスを削除します。

### `list_tables`

```python
def list_tables(self) -> list[str]
```
データベース内の全テーブルのリストを返します。

### `list_indexes`

```python
def list_indexes(self, table_name: str = None) -> list[dict]
```
インデックスのリストを返します（テーブル指定可）。

### `get_table_schema`

```python
def get_table_schema(self, table_name: str) -> list[dict]
```
テーブルの詳細なスキーマ情報を返します。

### `table_exists`

```python
def table_exists(self, table_name: str) -> bool
```
テーブルが存在するか確認します。

---

## ユーティリティ関数

### `vacuum`

```python
def vacuum(self) -> None
```
データベースファイルを最適化し、サイズを縮小します（`VACUUM` を実行）。

### `get_db_size`

```python
def get_db_size(self) -> int
```
データベースファイルのサイズをバイト単位で返します。

### `pragma`

```python
def pragma(self, pragma_name: str, value: Any = None) -> Any
```
SQLiteのPRAGMA値を取得または設定します。

### `get_last_insert_rowid`

```python
def get_last_insert_rowid(self) -> int
```
最後に挿入された行の `ROWID` を返します。

---

## Pydantic サポート

### `set_model`

```python
def set_model(self, key: str, model: Any) -> None
```
Pydanticモデルをシリアライズして保存します。

### `get_model`

```python
def get_model(self, key: str, model_class: type = None) -> Any
```
Pydanticモデルを取得してデシリアライズします。
