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
             strict_sql_validation: bool = True,
             allowed_sql_functions: list[str] | None = None,
             forbidden_sql_functions: list[str] | None = None,
             max_clause_length: int | None = 1000,
             lock_timeout: float | None = None,
             validator: Any | None = None,
             coerce: bool = False)
```

NanaSQLiteデータベース接続を初期化します。

**パラメータ:**

- `db_path` (str): SQLiteデータベースファイルのパス。
- `table` (str, 任意): ストレージに使用するテーブル名。デフォルトは `"data"`。
- `bulk_load` (bool, 任意): `True` の場合、初期化時に全データをメモリに読み込みます。高速な読み込みが必要な小規模データセット向け。デフォルトは `False`。
- `optimize` (bool, 任意): `True` の場合、WALモードやメモリマップドI/Oなどの最適化を適用します。デフォルトは `True`。
- `cache_size_mb` (int, 任意): SQLiteキャッシュサイズ（MB）。デフォルトは `64`。
- `strict_sql_validation` (bool, 任意): `True` の場合、未知のSQL関数を含むクエリを拒否し、インジェクションを防ぎます。デフォルトは `True` (v1.2.0以降)。
- `allowed_sql_functions` (list[str], 任意): 追加で許可するSQL関数のリスト。
- `forbidden_sql_functions` (list[str], 任意): 明示的に禁止するSQL関数のリスト。
- `max_clause_length` (int, 任意): SQL句の最大長（ReDoS対策）。デフォルトは `1000`。
- `lock_timeout` (float | None, 任意): 内部ロック取得の最大待機秒数。指定時間内にロックを取得できない場合は `NanaSQLiteLockError` を送出します。`None`（デフォルト）は無制限待機。(v1.3.4b1以降)
- `validator` (dict | Schema | None, 任意): validkit-py のバリデーションスキーマ（辞書または `Schema` オブジェクト）。指定すると `__setitem__` （`db["key"] = value`）の実行時にスキーマ検証を実行します。スキーマ違反の場合は `NanaSQLiteValidationError` を送出します。使用には `pip install nanasqlite[validation]` が必要です。(v1.3.4b2以降)
- `coerce` (bool, 任意): `True` の場合、validkit-py が返す変換済みの値をDBに保存します。
  **重要**: 型変換が実際に行われるためには、スキーマの各フィールドバリデーターに `.coerce()` を呼び出す必要があります（例: `v.int().coerce()`）。フィールドに `.coerce()` がない場合、型が一致しない値は `coerce=True` が設定されていてもバリデーションエラーになります。このパラメータは「変換済みの値を保存するか」を制御するだけです。`validator` が設定されている場合のみ有効。デフォルトは `False`。(v1.3.4b2以降)

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
def table(self, table_name: str,
          cache_strategy: CacheType | str | None = ...,
          cache_size: int | None = ...,
          cache_ttl: float | None = ...,
          cache_persistence_ttl: bool | None = ...,
          validator: Any | None = ...,
          coerce: bool = ...) -> NanaSQLite
```

指定したサブテーブル用の新しい `NanaSQLite` インスタンスを返します。

新しいインスタンスは親と同じ接続とロックを共有するため、スレッドセーフであり、データベースロックの問題を防ぎます。

**パラメータ:**
- `table_name` (str): サブテーブルの名前。
- `cache_strategy` (CacheType | str | None, 任意): このテーブル用のキャッシュ戦略。省略時は親と同じ設定を使用。
- `cache_size` (int | None, 任意): このテーブル用のキャッシュサイズ。省略時は親と同じ設定を使用。
- `cache_ttl` (float | None, 任意): このテーブル用のキャッシュ TTL（秒）。`cache_strategy` が `CacheType.TTL` で親が非TTLの場合は必須。省略時は親の TTL を継承。(v1.3.4b2以降)
- `cache_persistence_ttl` (bool | None, 任意): TTL が切れたキャッシュエントリをディスクに永続化するか。省略時は親の設定を継承。(v1.3.4b2以降)
- `validator` (dict | Schema | None, 任意): このサブテーブル用の validkit-py スキーマ。省略時は親インスタンスのスキーマを自動継承します。`None` を明示的に渡すとバリデーションを無効化できます。(v1.3.4b2以降)
- `coerce` (bool, 任意): `True` の場合、このサブテーブルで validkit-py の変換済みの値を保存します。スキーマのフィールドバリデーターに `.coerce()` が必要です。省略時は親インスタンスの設定を引き継ぎます。(v1.3.4b2以降)

**戻り値:**
- `NanaSQLite`: 指定したテーブルを操作する新しいインスタンス。

**使用例:**
```python
from validkit import v

db = NanaSQLite("app.db", validator={"name": v.str(), "age": v.int()})

# validator を省略 → 親のスキーマを継承
users_db = db.table("users")
users_db["u1"] = {"name": "Alice", "age": 30}  # OK

# validator を上書き → テーブル専用スキーマ
scores_db = db.table("scores", validator={"score": v.float()})
scores_db["s1"] = {"score": 9.5}  # OK

# validator=None → バリデーションを無効化
cache_db = db.table("cache", validator=None)
cache_db["k"] = {"anything": True}  # OK（スキーマ検証なし）

# coerce=True → 自動変換を有効化
coerce_db = db.table("users2", validator={"age": v.int().coerce()}, coerce=True)
coerce_db["u1"] = {"age": "30"}  # {"age": 30} として保存
```

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

## バックアップ & リストア (v1.3.4b1以降)

### `backup`

```python
def backup(self, dest_path: str) -> None
```

APSW の SQLite オンラインバックアップ API を使用して、現在のデータベースをファイルにバックアップします。
バックアップはページ単位で実行されるため、他の SQLite 接続が同時に読み書きしていても安全に動作します。
バックアップ実行中に NanaSQLite の内部ロックを保持しないため、同一プロセス内の他の NanaSQLite 操作をブロックしません。

**パラメータ:**
- `dest_path` (str): バックアップ先のファイルパス。

**例外:**
- `NanaSQLiteClosedError`: 接続が閉じられている場合。
- `NanaSQLiteValidationError`: `dest_path` が DB ファイル自身と同一である場合（自己コピー防止）、または `':memory:'` / `'file::memory:...'` などインメモリDB文字列が指定された場合（永続化されないため）。
- `NanaSQLiteDatabaseError`: バックアップ中にエラーが発生した場合。
- `NanaSQLiteLockError`: `lock_timeout` 設定によりロック取得がタイムアウトした場合。

**使用例:**
```python
db = NanaSQLite("app.db")
db["user"] = {"name": "Nana"}
db.backup("app_backup.db")
# app_backup.db に app.db の完全なコピーが保存されます
```

### `restore`

```python
def restore(self, src_path: str) -> None
```

バックアップファイルからデータベースをリストアします。
現在の接続を閉じ、バックアップファイルを DB ファイルに上書きコピーし、
stale な WAL/SHM/journal サイドカーファイル（`-wal`/`-shm`/`-journal`）を削除してから接続を再確立します。
リストア後はメモリキャッシュが自動的にクリアされます。

**パラメータ:**
- `src_path` (str): リストア元のバックアップファイルパス。

**例外:**
- `NanaSQLiteClosedError`: 接続が閉じられている場合。
- `NanaSQLiteConnectionError`: `.table()` で取得した（接続を所有しない）インスタンスから呼び出した場合。
- `NanaSQLiteTransactionError`: トランザクション中に呼び出した場合。`restore()` を呼ぶ前にコミットまたはロールバックしてください。
- `NanaSQLiteValidationError`: 現在の DB が `':memory:'` または `'file::memory:...'` などのインメモリDBの場合（ファイルによるリストアが不可能なため）。
- `NanaSQLiteDatabaseError`: リストア中にエラーが発生した場合（例：ファイルが存在しない、stale な WAL サイドカーファイルを削除できない場合）。
- `NanaSQLiteLockError`: `lock_timeout` 設定によりロック取得がタイムアウトした場合。

**使用例:**
```python
db = NanaSQLite("app.db")
db["user"] = {"name": "Nana"}
db.backup("snapshot.db")

db["user"] = {"name": "変更後"}
db.restore("snapshot.db")
print(db["user"])  # {'name': 'Nana'}
```

---

## Validkit バリデーション (v1.3.4b2以降)

[validkit-py](https://github.com/disnana/Validkit) を使用したスキーマベースの書き込みバリデーション機能です。

**インストール:**
```bash
pip install nanasqlite[validation]
```

### 基本的な使い方

```python
from validkit import v
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

schema = {"name": v.str(), "age": v.int().range(0, 150)}
db = NanaSQLite("mydata.db", validator=schema)

db["user"] = {"name": "Alice", "age": 30}        # OK
db["user"] = {"name": "Bob", "age": "invalid"}   # → NanaSQLiteValidationError
```

### 自動変換（coerce）

`coerce=True` を指定すると、validkit-py が変換した値（例: `"42"` → `42`）がDBに保存されます。

> **重要 — 2つの設定が必要**: 自動変換を機能させるには以下の両方が必要です。
> 1. スキーマの各フィールドバリデーターに `.coerce()` を呼び出す（例: `v.int().coerce()`）。これにより validkit-py がバリデーション中に型変換を試みます。
> 2. `NanaSQLite`（または `table()`）に `coerce=True` を渡す。これにより NanaSQLite が変換済みの値をDBに保存します。
>
> フィールドに `.coerce()` がない場合、`coerce=True` が設定されていても型が一致しない値はバリデーションエラーになります。

```python
from validkit import v
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

# 正しい使い方: フィールドに .coerce() + NanaSQLite に coerce=True
schema = {"age": v.int().coerce(), "score": v.float().coerce()}
db = NanaSQLite("mydata.db", validator=schema, coerce=True)

db["user"] = {"age": "30", "score": "9.5"}
print(db["user"])  # {"age": 30, "score": 9.5}  ← 変換済み

# 誤った使い方: フィールドに .coerce() がない場合は変換されない
schema_bad = {"age": v.int()}  # .coerce() なし
db_bad = NanaSQLite("bad.db", validator=schema_bad, coerce=True)
db_bad["user"] = {"age": "30"}  # → NanaSQLiteValidationError（型不一致）
```

### テーブルごとのバリデーション

```python
from validkit import v
from nanasqlite import NanaSQLite

user_schema = {"name": v.str(), "age": v.int()}
score_schema = {"player": v.str(), "score": v.float().range(0.0, 100.0)}

db = NanaSQLite("app.db")

# テーブルごとに異なるスキーマを適用
users_db = db.table("users", validator=user_schema)
scores_db = db.table("scores", validator=score_schema)

# 親からスキーマを継承したい場合
db2 = NanaSQLite("app2.db", validator=user_schema)
child_db = db2.table("users2")         # 親のスキーマを自動継承
free_db  = db2.table("cache", validator=None)  # バリデーション無効化

# テーブルごとに coerce を設定（フィールドに .coerce() が必要）
coerce_schema = {"age": v.int().coerce()}
coerce_db = db2.table("users3", validator=coerce_schema, coerce=True)
coerce_db["u1"] = {"age": "30"}  # {"age": 30} として保存
```

### batch_update のバリデーション

`validator` を設定している場合、`batch_update()` はDBに触れる前に**全値を一括バリデーション**します。1件でも違反があれば何も書き込まれません（アトミックな失敗保証）。

```python
from validkit import v
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

schema = {"name": v.str(), "age": v.int()}
db = NanaSQLite("batch.db", validator=schema)

try:
    db.batch_update({
        "u1": {"name": "Alice", "age": 30},
        "u2": {"name": "Bob", "age": "bad"},  # スキーマ違反
    })
except NanaSQLiteValidationError:
    print("u1" in db)  # False — 何も書き込まれていない
```

### 機能フラグの確認

```python
from nanasqlite import HAS_VALIDKIT

if HAS_VALIDKIT:
    print("validkit-py が利用可能です")
else:
    print("validkit-py は未インストールです")
```

### バリデーションエラーの処理

```python
from nanasqlite import NanaSQLite, NanaSQLiteValidationError
from validkit import v

schema = {"name": v.str(), "score": v.int().range(0, 100)}
db = NanaSQLite("game.db", validator=schema)

try:
    db["player1"] = {"name": "Alice", "score": 150}  # range 違反
except NanaSQLiteValidationError as e:
    print(f"バリデーションエラー: {e}")
    # DB には書き込まれていない
```

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
