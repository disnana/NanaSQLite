# 非同期 API リファレンス

AsyncNanaSQLiteクラスの非同期メソッド一覧です。

## AsyncNanaSQLite

```python
class AsyncNanaSQLite(db_path: str, table: str = 'data', bulk_load: bool = False, optimize: bool = True, cache_size_mb: int = 64, max_workers: int = 5, thread_name_prefix: str = 'AsyncNanaSQLite', strict_sql_validation: bool = True, allowed_sql_functions: list[str] | None = None, forbidden_sql_functions: list[str] | None = None, max_clause_length: int | None = 1000, read_pool_size: int = 0, cache_strategy: CacheType | str = <CacheType.UNBOUNDED: unbounded>, cache_size: int | None = None, cache_ttl: float | None = None, cache_persistence_ttl: bool = False, encryption_key: str | bytes | None = None, encryption_mode: Literal['aes-gcm', 'chacha20', 'fernet'] = 'aes-gcm', validator: Any | None = None, coerce: bool = False, v2_mode: bool = False, flush_mode: Literal['immediate', 'count', 'time', 'manual'] = 'immediate', flush_interval: float = 3.0, flush_count: int = 100, v2_chunk_size: int = 1000, v2_enable_metrics: bool = False) -> None
```

(最適化されたスレッドプールを使用するNanaSQLiteの非同期ラッパー)

データベース操作はすべて専用のスレッドプール内で実行され、非同期イベントループのブロックを防ぎます。
これにより、FastAPIやaiohttpなどの非同期アプリケーションで安全に使用できます。

高負荷なシナリオにおいて最適な並行性とパフォーマンスを実現するため、
カスタマイズ可能なスレッドプールを使用しています。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `db_path` | `str` | SQLiteデータベースファイルのパス |
| `table` | `str` | 使用するテーブル名 (デフォルト: "data") |
| `bulk_load` | `bool` | Trueの場合、初期化時に全データをメモリに読み込む |
| `optimize` | `bool` | Trueの場合、WALモードなど高速化設定を適用 |
| `cache_size_mb` | `int` | SQLiteキャッシュサイズ（MB）、デフォルト64MB |
| `max_workers` | `int` | スレッドプール内の最大ワーカー数（デフォルト: 5） |
| `thread_name_prefix` | `str` | スレッド名のプレフィックス（デフォルト: "AsyncNanaSQLite"） |
| `strict_sql_validation` | `bool` | Trueの場合、未許可の関数等を含むクエリを拒否 (v1.2.0) |
| `allowed_sql_functions` | `list[str] | None` | 追加で許可するSQL関数のリスト (v1.2.0) |
| `forbidden_sql_functions` | `list[str] | None` | 明示的に禁止するSQL関数のリスト (v1.2.0) |
| `max_clause_length` | `int | None` | SQL句の最大長（ReDoS対策）。Noneで制限なし (v1.2.0) |
| `read_pool_size` | `int` | 読み取り専用プールサイズ (デフォルト: 0 = 無効) (v1.1.0) |
| `cache_strategy` | `CacheType | str` |  |
| `cache_size` | `int | None` |  |
| `cache_ttl` | `float | None` |  |
| `cache_persistence_ttl` | `bool` |  |
| `encryption_key` | `str | bytes | None` | 暗号化キー (v1.3.1) |
| `encryption_mode` | `Literal[aes-gcm, chacha20, fernet]` |  |
| `validator` | `Any | None` | validkit-py のスキーマ（辞書または Schema オブジェクト）。 指定すると、値の書き込み時にバリデーションを実行する。 ``pip install nanasqlite[validation]`` が必要。 |
| `coerce` | `bool` | ``True`` の場合、validkit-py の自動変換機能を有効にする。 バリデーション後、変換済みの値をDBに書き込む。デフォルト: ``False``。 |
| `v2_mode` | `bool` | True の場合、新アーキテクチャ（バックグラウンド非同期書き込み）を有効化 |
| `flush_mode` | `Literal[immediate, count, time, manual]` | v2のフラッシュモード (immediate, count, time, manual) |
| `flush_interval` | `float` | v2のtimeモード時の秒数 |
| `flush_count` | `int` | v2のcountモード時の書き込み閾値 |
| `v2_chunk_size` | `int` | v2モード時の1トランザクションあたりの最大アイテム数 |
| `v2_enable_metrics` | `bool` | True の場合、v2エンジンのフラッシュメトリクスを収集する。 |

::: tip 使用例
```python
    >>> async with AsyncNanaSQLite("mydata.db") as db:
    ...     await db.aset("config", {"theme": "dark"})
    ...     config = await db.aget("config")
    ...     print(config)

    >>> # 高負荷環境向けの設定
    >>> async with AsyncNanaSQLite("mydata.db", max_workers=10) as db:
    ...     # 並行処理が多い場合に最適化
    ...     results = await asyncio.gather(*[db.aget(f"key_{i}") for i in range(100)])

```
:::


---

## コンストラクタ

## コアメソッド

### `close`

```python
def close() -> None
```

非同期でデータベース接続を閉じる

スレッドプールエグゼキューターもシャットダウンします。

::: tip 使用例
```python
    >>> await db.close()
```
:::


---

### `table`

```python
def table(table_name: str, validator: Any | None | types.EllipsisType = Ellipsis, coerce: bool | types.EllipsisType = Ellipsis) -> AsyncNanaSQLite
```

非同期でサブテーブルのAsyncNanaSQLiteインスタンスを取得

既に初期化済みの親インスタンスから呼ばれることを想定しています。
接続とエグゼキューターは親インスタンスと共有されます。

⚠️ 重要な注意事項:
- 同じテーブルに対して複数のインスタンスを作成しないでください
  各インスタンスは独立したキャッシュを持つため、キャッシュ不整合が発生します
- 推奨: テーブルインスタンスを変数に保存して再利用してください

非推奨:
    sub2 = await db.table("users")  # キャッシュ不整合の原因

推奨:
    # users_dbを使い回す

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | 取得するサブテーブル名 |
| `validator` | `Any | None | types.EllipsisType` | このテーブル用の validkit-py スキーマ。 指定しない場合は親インスタンスのスキーマを引き継ぐ。 ``None`` を明示的に渡すとバリデーションなしで使用できる。 |
| `coerce` | `bool | types.EllipsisType` | ``True`` の場合、validkit-py の自動変換機能を有効にする。 指定しない場合は親インスタンスの設定を引き継ぐ。 |

#### 戻り値

**Type:** `AsyncNanaSQLite`

指定したテーブルを操作するAsyncNanaSQLiteインスタンス

::: tip 使用例
```python
    >>> async with AsyncNanaSQLite("mydata.db", table="main") as db:
    ...     users_db = await db.table("users")
    ...     products_db = await db.table("products")
    ...     await users_db.aset("user1", {"name": "Alice"})
    ...     await products_db.aset("prod1", {"name": "Laptop"})
```
:::


---

## 辞書インターフェース

### `get`

```python
def get(key: str, default: Any = None) -> Any
```

非同期でキーの値を取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 取得するキー |
| `default` |  | キーが存在しない場合のデフォルト値 |

#### 戻り値

キーの値（存在しない場合はdefault）

::: tip 使用例
```python
    >>> user = await db.aget("user")
    >>> config = await db.aget("config", {})
```
:::


---

### `keys`

```python
def keys() -> list[str]
```

非同期で全キーを取得

#### 戻り値

**Type:** `list[str]`

全キーのリスト

::: tip 使用例
```python
    >>> keys = await db.akeys()
```
:::


---

### `values`

```python
def values() -> list[Any]
```

非同期で全値を取得

#### 戻り値

**Type:** `list[Any]`

全値のリスト

::: tip 使用例
```python
    >>> values = await db.avalues()
```
:::


---

### `items`

```python
def items() -> list[tuple[str, Any]]
```

非同期で全アイテムを取得

#### 戻り値

**Type:** `list[tuple[str, Any]]`

全アイテムのリスト（キーと値のタプル）

::: tip 使用例
```python
    >>> items = await db.aitems()
```
:::


---

### `to_dict`

```python
def to_dict() -> dict
```

非同期で全データをPython dictとして取得

#### 戻り値

**Type:** `dict`

全データを含むdict

::: tip 使用例
```python
    >>> data = await db.to_dict()
```
:::


---

### `copy`

```python
def copy() -> dict
```

非同期で浅いコピーを作成

#### 戻り値

**Type:** `dict`

全データのコピー

::: tip 使用例
```python
    >>> data_copy = await db.copy()
```
:::


---

### `clear_cache`

```python
def clear_cache() -> None
```

aclear_cache のエイリアス


---

## データ管理

### `load_all`

```python
def load_all() -> None
```

非同期で全データを一括ロード

::: tip 使用例
```python
    >>> await db.load_all()
```
:::


---

### `refresh`

```python
def refresh(key: str = None) -> None
```

非同期でキャッシュを更新

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 更新するキー（Noneの場合は全キャッシュ） |

::: tip 使用例
```python
    >>> await db.refresh("user")
    >>> await db.refresh()  # 全キャッシュ更新
```
:::


---

### `is_cached`

```python
def is_cached(key: str) -> bool
```

非同期でキーがキャッシュ済みか確認

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 確認するキー |

#### 戻り値

**Type:** `bool`

キャッシュ済みの場合True

::: tip 使用例
```python
    >>> cached = await db.is_cached("user")
```
:::


---

### `batch_update`

```python
def batch_update(mapping: dict[str, Any]) -> None
```

非同期で一括書き込み（高速）

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `mapping` | `dict[str, Any]` | 書き込むキーと値のdict |

::: tip 使用例
```python
    >>> await db.batch_update({
    ...     "key1": "value1",
    ...     "key2": "value2",
    ...     "key3": {"nested": "data"}
    ... })
```
:::


---

### `batch_update_partial`

```python
def batch_update_partial(mapping: dict[str, Any]) -> dict[str, str]
```

非同期で一括書き込み（部分成功モード）

バリデーションまたはシリアライズに失敗したキーだけを拒否し、
正常なキーは一括で保存する。返り値は拒否されたキーと理由の辞書。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `mapping` | `dict[str, Any]` | 書き込むキーと値のdict |

#### 戻り値

**Type:** `dict[str, str]`

拒否されたキー -> エラーメッセージ のdict


---

### `batch_delete`

```python
def batch_delete(keys: list[str]) -> None
```

非同期で一括削除（高速）

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `keys` | `list[str]` | 削除するキーのリスト |

::: tip 使用例
```python
    >>> await db.batch_delete(["key1", "key2", "key3"])
```
:::


---

### `get_fresh`

```python
def get_fresh(key: str, default: Any = None) -> Any
```

非同期でDBから直接読み込み、キャッシュを更新

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 取得するキー |
| `default` |  | キーが存在しない場合のデフォルト値 |

#### 戻り値

DBから取得した最新の値

::: tip 使用例
```python
    >>> value = await db.get_fresh("key")
```
:::


---

## トランザクション制御

### `begin_transaction`

```python
def begin_transaction() -> None
```

非同期でトランザクションを開始

::: tip 使用例
```python
    >>> await db.begin_transaction()
    >>> try:
    ...     await db.sql_insert("users", {"name": "Alice"})
    ...     await db.sql_insert("users", {"name": "Bob"})
    ...     await db.commit()
    ... except:
    ...     await db.rollback()
```
:::


---

### `commit`

```python
def commit() -> None
```

非同期でトランザクションをコミット

::: tip 使用例
```python
    >>> await db.commit()
```
:::


---

### `rollback`

```python
def rollback() -> None
```

非同期でトランザクションをロールバック

::: tip 使用例
```python
    >>> await db.rollback()
```
:::


---

### `in_transaction`

```python
def in_transaction() -> bool
```

非同期でトランザクション状態を確認

#### 戻り値

**Type:** `bool`

bool: トランザクション中の場合True

::: tip 使用例
```python
    >>> status = await db.in_transaction()
    >>> print(f"In transaction: {status}")
```
:::


---

### `transaction`

```python
def transaction()
```

非同期トランザクションのコンテキストマネージャ

::: tip 使用例
```python
    >>> async with db.transaction():
    ...     await db.sql_insert("users", {"name": "Alice"})
    ...     await db.sql_insert("users", {"name": "Bob"})
    ...     # 自動的にコミット、例外時はロールバック
```
:::


---

## SQLラッパー (CRUD)

### `sql_insert`

```python
def sql_insert(table_name: str, data: dict) -> int
```

非同期でdictから直接INSERT

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `data` | `dict` | カラム名と値のdict |

#### 戻り値

**Type:** `int`

挿入されたROWID

::: tip 使用例
```python
    >>> rowid = await db.sql_insert("users", {
    ...     "name": "Alice",
    ...     "email": "alice@example.com",
    ...     "age": 25
    ... })
```
:::


---

### `sql_update`

```python
def sql_update(table_name: str, data: dict, where: str, parameters: tuple | None = None) -> int
```

非同期でdictとwhere条件でUPDATE

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `data` | `dict` | 更新するカラム名と値のdict |
| `where` | `str` | WHERE句の条件 |
| `parameters` | `tuple | None` | WHERE句のパラメータ |

#### 戻り値

**Type:** `int`

更新された行数

::: tip 使用例
```python
    >>> count = await db.sql_update("users",
    ...     {"age": 26, "status": "active"},
    ...     "name = ?",
    ...     ("Alice",)
    ... )
```
:::


---

### `sql_delete`

```python
def sql_delete(table_name: str, where: str, parameters: tuple | None = None) -> int
```

非同期でwhere条件でDELETE

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `where` | `str` | WHERE句の条件 |
| `parameters` | `tuple | None` | WHERE句のパラメータ |

#### 戻り値

**Type:** `int`

削除された行数

::: tip 使用例
```python
    >>> count = await db.sql_delete("users", "age < ?", (18,))
```
:::


---

## クエリ

### `query`

```python
def query(table_name: str = None, columns: list[str] = None, where: str = None, parameters: tuple | None = None, order_by: str = None, limit: int = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> list[dict]
```

非同期でSELECTクエリを実行

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `columns` | `list[str]` | 取得するカラムのリスト |
| `where` | `str` | WHERE句の条件 |
| `parameters` | `tuple | None` | WHERE句のパラメータ |
| `order_by` | `str` | ORDER BY句 |
| `limit` | `int` | LIMIT句 |
| `strict_sql_validation` | `bool` | Trueの場合、未許可の関数等を含むクエリを拒否 |
| `allowed_sql_functions` | `list[str]` | このクエリで一時的に許可するSQL関数のリスト |
| `forbidden_sql_functions` | `list[str]` | このクエリで一時的に禁止するSQL関数のリスト |
| `override_allowed` | `bool` | Trueの場合、インスタンス許可設定を無視 |

#### 戻り値

**Type:** `list[dict]`

結果のリスト（各行はdict）

::: tip 使用例
```python
    >>> results = await db.query(
    ...     table_name="users",
    ...     columns=["id", "name", "email"],
    ...     where="age > ?",
    ...     parameters=(20,),
    ...     order_by="name ASC",
    ...     limit=10
    ... )
```
:::


---

### `query_with_pagination`

```python
def query_with_pagination(table_name: str = None, columns: list[str] = None, where: str = None, parameters: tuple | None = None, order_by: str = None, limit: int = None, offset: int = None, group_by: str = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> list[dict]
```

非同期で拡張されたクエリを実行

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `columns` | `list[str]` | 取得するカラム |
| `where` | `str` | WHERE句 |
| `parameters` | `tuple | None` | パラメータ |
| `order_by` | `str` | ORDER BY句 |
| `limit` | `int` | LIMIT句 |
| `offset` | `int` | OFFSET句 |
| `group_by` | `str` | GROUP BY句 |
| `strict_sql_validation` | `bool` | Trueの場合、未許可の関数等を含むクエリを拒否 |
| `allowed_sql_functions` | `list[str]` | このクエリで一時的に許可するSQL関数のリスト |
| `forbidden_sql_functions` | `list[str]` | このクエリで一時的に禁止するSQL関数のリスト |
| `override_allowed` | `bool` | Trueの場合、インスタンス許可設定を無視 |

#### 戻り値

**Type:** `list[dict]`

結果のリスト（各行はdict）

::: tip 使用例
```python
    >>> results = await db.query_with_pagination(
    ...     table_name="users",
    ...     columns=["id", "name", "email"],
    ...     where="age > ?",
    ...     parameters=(20,),
    ...     order_by="name ASC",
    ...     limit=10,
    ...     offset=0
    ... )
```
:::


---

### `count`

```python
def count(table_name: str = None, where: str = None, parameters: tuple | None = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> int
```

非同期でレコード数を取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `where` | `str` | WHERE句の条件 |
| `parameters` | `tuple | None` | WHERE句のパラメータ |
| `strict_sql_validation` | `bool` | Trueの場合、未許可の関数等を含むクエリを拒否 |
| `allowed_sql_functions` | `list[str]` | このクエリで一時的に許可するSQL関数のリスト |
| `forbidden_sql_functions` | `list[str]` | このクエリで一時的に禁止するSQL関数のリスト |
| `override_allowed` | `bool` | Trueの場合、インスタンス許可設定を無視 |

#### 戻り値

**Type:** `int`

レコード数

::: tip 使用例
```python
    >>> count = await db.count("users", "age < ?", (18,))
```
:::


---

## 直接SQL実行

### `execute`

```python
def execute(sql: str, parameters: tuple | None = None) -> Any
```

非同期でSQLを直接実行

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `sql` | `str` | 実行するSQL文 |
| `parameters` | `tuple | None` | SQLのパラメータ |

#### 戻り値

APSWのCursorオブジェクト

::: tip 使用例
```python
    >>> cursor = await db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
```
:::


---

### `execute_many`

```python
def execute_many(sql: str, parameters_list: list[tuple]) -> None
```

非同期でSQLを複数のパラメータで一括実行

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `sql` | `str` | 実行するSQL文 |
| `parameters_list` | `list[tuple]` | パラメータのリスト |

::: tip 使用例
```python
    >>> await db.execute_many(
    ...     "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
    ...     [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
    ... )
```
:::


---

### `fetch_one`

```python
def fetch_one(sql: str, parameters: tuple | None = None) -> tuple | None
```

非同期でSQLを実行して1行取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `sql` | `str` | 実行するSQL文 |
| `parameters` | `tuple | None` | SQLのパラメータ |

#### 戻り値

**Type:** `tuple | None`

1行の結果（tuple）

::: tip 使用例
```python
    >>> row = await db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
```
:::


---

### `fetch_all`

```python
def fetch_all(sql: str, parameters: tuple | None = None) -> list[tuple]
```

非同期でSQLを実行して全行取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `sql` | `str` | 実行するSQL文 |
| `parameters` | `tuple | None` | SQLのパラメータ |

#### 戻り値

**Type:** `list[tuple]`

全行の結果（tupleのリスト）

::: tip 使用例
```python
    >>> rows = await db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
```
:::


---

## スキーマ管理

### `create_table`

```python
def create_table(table_name: str, columns: dict, if_not_exists: bool = True, primary_key: str = None) -> None
```

非同期でテーブルを作成

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `columns` | `dict` | カラム定義のdict |
| `if_not_exists` | `bool` | Trueの場合、存在しない場合のみ作成 |
| `primary_key` | `str` | プライマリキーのカラム名 |

::: tip 使用例
```python
    >>> await db.create_table("users", {
    ...     "id": "INTEGER PRIMARY KEY",
    ...     "name": "TEXT NOT NULL",
    ...     "email": "TEXT UNIQUE"
    ... })
```
:::


---

### `create_index`

```python
def create_index(index_name: str, table_name: str, columns: list[str], unique: bool = False, if_not_exists: bool = True) -> None
```

非同期でインデックスを作成

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `index_name` | `str` | インデックス名 |
| `table_name` | `str` | テーブル名 |
| `columns` | `list[str]` | インデックスを作成するカラムのリスト |
| `unique` | `bool` | Trueの場合、ユニークインデックスを作成 |
| `if_not_exists` | `bool` | Trueの場合、存在しない場合のみ作成 |

::: tip 使用例
```python
    >>> await db.create_index("idx_users_email", "users", ["email"], unique=True)
```
:::


---

### `table_exists`

```python
def table_exists(table_name: str) -> bool
```

非同期でテーブルの存在確認

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |

#### 戻り値

**Type:** `bool`

存在する場合True

::: tip 使用例
```python
    >>> exists = await db.table_exists("users")
```
:::


---

### `list_tables`

```python
def list_tables() -> list[str]
```

非同期でデータベース内の全テーブル一覧を取得

#### 戻り値

**Type:** `list[str]`

テーブル名のリスト

::: tip 使用例
```python
    >>> tables = await db.list_tables()
```
:::


---

### `drop_table`

```python
def drop_table(table_name: str, if_exists: bool = True) -> None
```

非同期でテーブルを削除

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `if_exists` | `bool` | Trueの場合、存在する場合のみ削除 |

::: tip 使用例
```python
    >>> await db.drop_table("old_table")
```
:::


---

### `drop_index`

```python
def drop_index(index_name: str, if_exists: bool = True) -> None
```

非同期でインデックスを削除

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `index_name` | `str` | インデックス名 |
| `if_exists` | `bool` | Trueの場合、存在する場合のみ削除 |

::: tip 使用例
```python
    >>> await db.drop_index("idx_users_email")
```
:::


---

## ユーティリティ関数

### `vacuum`

```python
def vacuum() -> None
```

非同期でデータベースを最適化（VACUUM実行）

::: tip 使用例
```python
    >>> await db.vacuum()
```
:::


---

## Pydantic サポート

### `set_model`

```python
def set_model(key: str, model: Any) -> None
```

非同期でPydanticモデルを保存

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 保存するキー |
| `model` |  | Pydanticモデルのインスタンス |

::: tip 使用例
```python
    >>> from pydantic import BaseModel
    >>> class User(BaseModel):
    ...     name: str
    ...     age: int
    >>> user = User(name="Nana", age=20)
    >>> await db.set_model("user", user)
```
:::


---

### `get_model`

```python
def get_model(key: str, model_class: type = None) -> Any
```

非同期でPydanticモデルを取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 取得するキー |
| `model_class` | `type` | Pydanticモデルのクラス |

#### 戻り値

Pydanticモデルのインスタンス

::: tip 使用例
```python
    >>> user = await db.get_model("user", User)
```
:::


---

## その他のメソッド

### `aget`

```python
def aget(key: str, default: Any = None) -> Any
```

非同期でキーの値を取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 取得するキー |
| `default` |  | キーが存在しない場合のデフォルト値 |

#### 戻り値

キーの値（存在しない場合はdefault）

::: tip 使用例
```python
    >>> user = await db.aget("user")
    >>> config = await db.aget("config", {})
```
:::


---

### `aset`

```python
def aset(key: str, value: Any) -> None
```

非同期でキーに値を設定

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 設定するキー |
| `value` |  | 設定する値 |

::: tip 使用例
```python
    >>> await db.aset("user", {"name": "Nana", "age": 20})
```
:::


---

### `adelete`

```python
def adelete(key: str) -> None
```

非同期でキーを削除

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 削除するキー |

::: warning 例外
- KeyError: キーが存在しない場合
:::

::: tip 使用例
```python
    >>> await db.adelete("old_data")
```
:::


---

### `acontains`

```python
def acontains(key: str) -> bool
```

非同期でキーの存在確認

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 確認するキー |

#### 戻り値

**Type:** `bool`

キーが存在する場合True

::: tip 使用例
```python
    >>> if await db.acontains("user"):
    ...     print("User exists")
```
:::


---

### `contains`

```python
def contains(key: str) -> bool
```

非同期でキーの存在確認

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 確認するキー |

#### 戻り値

**Type:** `bool`

キーが存在する場合True

::: tip 使用例
```python
    >>> if await db.acontains("user"):
    ...     print("User exists")
```
:::


---

### `alen`

```python
def alen() -> int
```

非同期でデータベースの件数を取得

#### 戻り値

**Type:** `int`

データベース内のキーの数

::: tip 使用例
```python
    >>> count = await db.alen()
```
:::


---

### `akeys`

```python
def akeys() -> list[str]
```

非同期で全キーを取得

#### 戻り値

**Type:** `list[str]`

全キーのリスト

::: tip 使用例
```python
    >>> keys = await db.akeys()
```
:::


---

### `avalues`

```python
def avalues() -> list[Any]
```

非同期で全値を取得

#### 戻り値

**Type:** `list[Any]`

全値のリスト

::: tip 使用例
```python
    >>> values = await db.avalues()
```
:::


---

### `aitems`

```python
def aitems() -> list[tuple[str, Any]]
```

非同期で全アイテムを取得

#### 戻り値

**Type:** `list[tuple[str, Any]]`

全アイテムのリスト（キーと値のタプル）

::: tip 使用例
```python
    >>> items = await db.aitems()
```
:::


---

### `apop`

```python
def apop(key: str, *args) -> Any
```

非同期でキーを削除して値を返す

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 削除するキー *args: デフォルト値（オプション） |

#### 戻り値

削除されたキーの値

::: tip 使用例
```python
    >>> value = await db.apop("temp_data")
    >>> value = await db.apop("maybe_missing", "default")
```
:::


---

### `aupdate`

```python
def aupdate(mapping: dict = None, **kwargs) -> None
```

非同期で複数のキーを更新

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `mapping` | `dict` | 更新するキーと値のdict **kwargs: キーワード引数として渡す更新 |

::: tip 使用例
```python
    >>> await db.aupdate({"key1": "value1", "key2": "value2"})
    >>> await db.aupdate(key3="value3", key4="value4")
```
:::


---

### `aflush`

```python
def aflush() -> None
```

[v2 Feature] 非同期でv2エンジンのバックグラウンドバッファとキューをSQLiteに明示的にフラッシュする。
v2_modeがFalseの場合は何もしない。

::: tip 使用例
```python
    >>> await db.aflush()
```
:::


---

### `aclear`

```python
def aclear() -> None
```

非同期で全データを削除

::: tip 使用例
```python
    >>> await db.aclear()
```
:::


---

### `aget_dlq`

```python
def aget_dlq() -> list[dict[str, Any]]
```

[v2 Feature] 非同期でデッドレターキュー（DLQ）の内容を取得します。
v2モードが無効な場合は空のリストを返します。

::: tip 使用例
```python
    >>> failed = await db.aget_dlq()
```
:::


---

### `aretry_dlq`

```python
def aretry_dlq() -> None
```

[v2 Feature] 非同期でDLQ内の全アイテムを再試行キューに戻します。
v2モードが無効な場合は何もしません。

::: tip 使用例
```python
    >>> await db.aretry_dlq()
```
:::


---

### `aclear_dlq`

```python
def aclear_dlq() -> None
```

[v2 Feature] 非同期でDLQの内容をクリアします。
v2モードが無効な場合は何もしません。

::: tip 使用例
```python
    >>> await db.aclear_dlq()
```
:::


---

### `aget_v2_metrics`

```python
def aget_v2_metrics() -> dict[str, Any]
```

[v2 Feature] 非同期でメトリクス情報を取得します( v2_enable_metrics=True 時のみ有効)。
v2モード自体またはメトリクスが無効な場合は空の辞書を返します。

::: tip 使用例
```python
    >>> metrics = await db.aget_v2_metrics()
    >>> print(metrics["flush_count"])
```
:::


---

### `asetdefault`

```python
def asetdefault(key: str, default: Any = None) -> Any
```

非同期でキーが存在しない場合のみ値を設定

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | キー |
| `default` |  | デフォルト値 |

#### 戻り値

キーの値（既存または新規設定した値）

::: tip 使用例
```python
    >>> value = await db.asetdefault("config", {})
```
:::


---

### `aload_all`

```python
def aload_all() -> None
```

非同期で全データを一括ロード

::: tip 使用例
```python
    >>> await db.load_all()
```
:::


---

### `arefresh`

```python
def arefresh(key: str = None) -> None
```

非同期でキャッシュを更新

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 更新するキー（Noneの場合は全キャッシュ） |

::: tip 使用例
```python
    >>> await db.refresh("user")
    >>> await db.refresh()  # 全キャッシュ更新
```
:::


---

### `ais_cached`

```python
def ais_cached(key: str) -> bool
```

非同期でキーがキャッシュ済みか確認

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 確認するキー |

#### 戻り値

**Type:** `bool`

キャッシュ済みの場合True

::: tip 使用例
```python
    >>> cached = await db.is_cached("user")
```
:::


---

### `abatch_update`

```python
def abatch_update(mapping: dict[str, Any]) -> None
```

非同期で一括書き込み（高速）

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `mapping` | `dict[str, Any]` | 書き込むキーと値のdict |

::: tip 使用例
```python
    >>> await db.batch_update({
    ...     "key1": "value1",
    ...     "key2": "value2",
    ...     "key3": {"nested": "data"}
    ... })
```
:::


---

### `abatch_update_partial`

```python
def abatch_update_partial(mapping: dict[str, Any]) -> dict[str, str]
```

非同期で一括書き込み（部分成功モード）

バリデーションまたはシリアライズに失敗したキーだけを拒否し、
正常なキーは一括で保存する。返り値は拒否されたキーと理由の辞書。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `mapping` | `dict[str, Any]` | 書き込むキーと値のdict |

#### 戻り値

**Type:** `dict[str, str]`

拒否されたキー -> エラーメッセージ のdict


---

### `abatch_delete`

```python
def abatch_delete(keys: list[str]) -> None
```

非同期で一括削除（高速）

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `keys` | `list[str]` | 削除するキーのリスト |

::: tip 使用例
```python
    >>> await db.batch_delete(["key1", "key2", "key3"])
```
:::


---

### `ato_dict`

```python
def ato_dict() -> dict
```

非同期で全データをPython dictとして取得

#### 戻り値

**Type:** `dict`

全データを含むdict

::: tip 使用例
```python
    >>> data = await db.to_dict()
```
:::


---

### `acopy`

```python
def acopy() -> dict
```

非同期で浅いコピーを作成

#### 戻り値

**Type:** `dict`

全データのコピー

::: tip 使用例
```python
    >>> data_copy = await db.copy()
```
:::


---

### `aget_fresh`

```python
def aget_fresh(key: str, default: Any = None) -> Any
```

非同期でDBから直接読み込み、キャッシュを更新

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 取得するキー |
| `default` |  | キーが存在しない場合のデフォルト値 |

#### 戻り値

DBから取得した最新の値

::: tip 使用例
```python
    >>> value = await db.get_fresh("key")
```
:::


---

### `abatch_get`

```python
def abatch_get(keys: list[str]) -> dict[str, Any]
```

非同期で複数のキーを一度に取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `keys` | `list[str]` | 取得するキーのリスト |

#### 戻り値

**Type:** `dict[str, Any]`

取得に成功したキーと値の dict

::: tip 使用例
```python
    >>> results = await db.abatch_get(["key1", "key2"])
```
:::


---

### `aset_model`

```python
def aset_model(key: str, model: Any) -> None
```

非同期でPydanticモデルを保存

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 保存するキー |
| `model` |  | Pydanticモデルのインスタンス |

::: tip 使用例
```python
    >>> from pydantic import BaseModel
    >>> class User(BaseModel):
    ...     name: str
    ...     age: int
    >>> user = User(name="Nana", age=20)
    >>> await db.set_model("user", user)
```
:::


---

### `aget_model`

```python
def aget_model(key: str, model_class: type = None) -> Any
```

非同期でPydanticモデルを取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 取得するキー |
| `model_class` | `type` | Pydanticモデルのクラス |

#### 戻り値

Pydanticモデルのインスタンス

::: tip 使用例
```python
    >>> user = await db.get_model("user", User)
```
:::


---

### `aexecute`

```python
def aexecute(sql: str, parameters: tuple | None = None) -> Any
```

非同期でSQLを直接実行

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `sql` | `str` | 実行するSQL文 |
| `parameters` | `tuple | None` | SQLのパラメータ |

#### 戻り値

APSWのCursorオブジェクト

::: tip 使用例
```python
    >>> cursor = await db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
```
:::


---

### `aexecute_many`

```python
def aexecute_many(sql: str, parameters_list: list[tuple]) -> None
```

非同期でSQLを複数のパラメータで一括実行

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `sql` | `str` | 実行するSQL文 |
| `parameters_list` | `list[tuple]` | パラメータのリスト |

::: tip 使用例
```python
    >>> await db.execute_many(
    ...     "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
    ...     [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
    ... )
```
:::


---

### `afetch_one`

```python
def afetch_one(sql: str, parameters: tuple | None = None) -> tuple | None
```

非同期でSQLを実行して1行取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `sql` | `str` | 実行するSQL文 |
| `parameters` | `tuple | None` | SQLのパラメータ |

#### 戻り値

**Type:** `tuple | None`

1行の結果（tuple）

::: tip 使用例
```python
    >>> row = await db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
```
:::


---

### `afetch_all`

```python
def afetch_all(sql: str, parameters: tuple | None = None) -> list[tuple]
```

非同期でSQLを実行して全行取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `sql` | `str` | 実行するSQL文 |
| `parameters` | `tuple | None` | SQLのパラメータ |

#### 戻り値

**Type:** `list[tuple]`

全行の結果（tupleのリスト）

::: tip 使用例
```python
    >>> rows = await db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
```
:::


---

### `acreate_table`

```python
def acreate_table(table_name: str, columns: dict, if_not_exists: bool = True, primary_key: str = None) -> None
```

非同期でテーブルを作成

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `columns` | `dict` | カラム定義のdict |
| `if_not_exists` | `bool` | Trueの場合、存在しない場合のみ作成 |
| `primary_key` | `str` | プライマリキーのカラム名 |

::: tip 使用例
```python
    >>> await db.create_table("users", {
    ...     "id": "INTEGER PRIMARY KEY",
    ...     "name": "TEXT NOT NULL",
    ...     "email": "TEXT UNIQUE"
    ... })
```
:::


---

### `acreate_index`

```python
def acreate_index(index_name: str, table_name: str, columns: list[str], unique: bool = False, if_not_exists: bool = True) -> None
```

非同期でインデックスを作成

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `index_name` | `str` | インデックス名 |
| `table_name` | `str` | テーブル名 |
| `columns` | `list[str]` | インデックスを作成するカラムのリスト |
| `unique` | `bool` | Trueの場合、ユニークインデックスを作成 |
| `if_not_exists` | `bool` | Trueの場合、存在しない場合のみ作成 |

::: tip 使用例
```python
    >>> await db.create_index("idx_users_email", "users", ["email"], unique=True)
```
:::


---

### `aquery`

```python
def aquery(table_name: str = None, columns: list[str] = None, where: str = None, parameters: tuple | None = None, order_by: str = None, limit: int = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> list[dict]
```

非同期でSELECTクエリを実行

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `columns` | `list[str]` | 取得するカラムのリスト |
| `where` | `str` | WHERE句の条件 |
| `parameters` | `tuple | None` | WHERE句のパラメータ |
| `order_by` | `str` | ORDER BY句 |
| `limit` | `int` | LIMIT句 |
| `strict_sql_validation` | `bool` | Trueの場合、未許可の関数等を含むクエリを拒否 |
| `allowed_sql_functions` | `list[str]` | このクエリで一時的に許可するSQL関数のリスト |
| `forbidden_sql_functions` | `list[str]` | このクエリで一時的に禁止するSQL関数のリスト |
| `override_allowed` | `bool` | Trueの場合、インスタンス許可設定を無視 |

#### 戻り値

**Type:** `list[dict]`

結果のリスト（各行はdict）

::: tip 使用例
```python
    >>> results = await db.query(
    ...     table_name="users",
    ...     columns=["id", "name", "email"],
    ...     where="age > ?",
    ...     parameters=(20,),
    ...     order_by="name ASC",
    ...     limit=10
    ... )
```
:::


---

### `aquery_with_pagination`

```python
def aquery_with_pagination(table_name: str = None, columns: list[str] = None, where: str = None, parameters: tuple | None = None, order_by: str = None, limit: int = None, offset: int = None, group_by: str = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> list[dict]
```

非同期で拡張されたクエリを実行

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `columns` | `list[str]` | 取得するカラム |
| `where` | `str` | WHERE句 |
| `parameters` | `tuple | None` | パラメータ |
| `order_by` | `str` | ORDER BY句 |
| `limit` | `int` | LIMIT句 |
| `offset` | `int` | OFFSET句 |
| `group_by` | `str` | GROUP BY句 |
| `strict_sql_validation` | `bool` | Trueの場合、未許可の関数等を含むクエリを拒否 |
| `allowed_sql_functions` | `list[str]` | このクエリで一時的に許可するSQL関数のリスト |
| `forbidden_sql_functions` | `list[str]` | このクエリで一時的に禁止するSQL関数のリスト |
| `override_allowed` | `bool` | Trueの場合、インスタンス許可設定を無視 |

#### 戻り値

**Type:** `list[dict]`

結果のリスト（各行はdict）

::: tip 使用例
```python
    >>> results = await db.query_with_pagination(
    ...     table_name="users",
    ...     columns=["id", "name", "email"],
    ...     where="age > ?",
    ...     parameters=(20,),
    ...     order_by="name ASC",
    ...     limit=10,
    ...     offset=0
    ... )
```
:::


---

### `atable_exists`

```python
def atable_exists(table_name: str) -> bool
```

非同期でテーブルの存在確認

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |

#### 戻り値

**Type:** `bool`

存在する場合True

::: tip 使用例
```python
    >>> exists = await db.table_exists("users")
```
:::


---

### `alist_tables`

```python
def alist_tables() -> list[str]
```

非同期でデータベース内の全テーブル一覧を取得

#### 戻り値

**Type:** `list[str]`

テーブル名のリスト

::: tip 使用例
```python
    >>> tables = await db.list_tables()
```
:::


---

### `adrop_table`

```python
def adrop_table(table_name: str, if_exists: bool = True) -> None
```

非同期でテーブルを削除

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `if_exists` | `bool` | Trueの場合、存在する場合のみ削除 |

::: tip 使用例
```python
    >>> await db.drop_table("old_table")
```
:::


---

### `asql_insert`

```python
def asql_insert(table_name: str, data: dict) -> int
```

非同期でdictから直接INSERT

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `data` | `dict` | カラム名と値のdict |

#### 戻り値

**Type:** `int`

挿入されたROWID

::: tip 使用例
```python
    >>> rowid = await db.sql_insert("users", {
    ...     "name": "Alice",
    ...     "email": "alice@example.com",
    ...     "age": 25
    ... })
```
:::


---

### `asql_update`

```python
def asql_update(table_name: str, data: dict, where: str, parameters: tuple | None = None) -> int
```

非同期でdictとwhere条件でUPDATE

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `data` | `dict` | 更新するカラム名と値のdict |
| `where` | `str` | WHERE句の条件 |
| `parameters` | `tuple | None` | WHERE句のパラメータ |

#### 戻り値

**Type:** `int`

更新された行数

::: tip 使用例
```python
    >>> count = await db.sql_update("users",
    ...     {"age": 26, "status": "active"},
    ...     "name = ?",
    ...     ("Alice",)
    ... )
```
:::


---

### `asql_delete`

```python
def asql_delete(table_name: str, where: str, parameters: tuple | None = None) -> int
```

非同期でwhere条件でDELETE

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `where` | `str` | WHERE句の条件 |
| `parameters` | `tuple | None` | WHERE句のパラメータ |

#### 戻り値

**Type:** `int`

削除された行数

::: tip 使用例
```python
    >>> count = await db.sql_delete("users", "age < ?", (18,))
```
:::


---

### `acount`

```python
def acount(table_name: str = None, where: str = None, parameters: tuple | None = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> int
```

非同期でレコード数を取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `where` | `str` | WHERE句の条件 |
| `parameters` | `tuple | None` | WHERE句のパラメータ |
| `strict_sql_validation` | `bool` | Trueの場合、未許可の関数等を含むクエリを拒否 |
| `allowed_sql_functions` | `list[str]` | このクエリで一時的に許可するSQL関数のリスト |
| `forbidden_sql_functions` | `list[str]` | このクエリで一時的に禁止するSQL関数のリスト |
| `override_allowed` | `bool` | Trueの場合、インスタンス許可設定を無視 |

#### 戻り値

**Type:** `int`

レコード数

::: tip 使用例
```python
    >>> count = await db.count("users", "age < ?", (18,))
```
:::


---

### `avacuum`

```python
def avacuum() -> None
```

非同期でデータベースを最適化（VACUUM実行）

::: tip 使用例
```python
    >>> await db.vacuum()
```
:::


---

### `aclear_cache`

```python
def aclear_cache() -> None
```

メモリキャッシュをクリア (非同期)

DBのデータは削除せず、メモリ上のキャッシュのみ破棄します。


---

### `atable`

```python
def atable(table_name: str, validator: Any | None | types.EllipsisType = Ellipsis, coerce: bool | types.EllipsisType = Ellipsis) -> AsyncNanaSQLite
```

非同期でサブテーブルのAsyncNanaSQLiteインスタンスを取得

既に初期化済みの親インスタンスから呼ばれることを想定しています。
接続とエグゼキューターは親インスタンスと共有されます。

⚠️ 重要な注意事項:
- 同じテーブルに対して複数のインスタンスを作成しないでください
  各インスタンスは独立したキャッシュを持つため、キャッシュ不整合が発生します
- 推奨: テーブルインスタンスを変数に保存して再利用してください

非推奨:
    sub2 = await db.table("users")  # キャッシュ不整合の原因

推奨:
    # users_dbを使い回す

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | 取得するサブテーブル名 |
| `validator` | `Any | None | types.EllipsisType` | このテーブル用の validkit-py スキーマ。 指定しない場合は親インスタンスのスキーマを引き継ぐ。 ``None`` を明示的に渡すとバリデーションなしで使用できる。 |
| `coerce` | `bool | types.EllipsisType` | ``True`` の場合、validkit-py の自動変換機能を有効にする。 指定しない場合は親インスタンスの設定を引き継ぐ。 |

#### 戻り値

**Type:** `AsyncNanaSQLite`

指定したテーブルを操作するAsyncNanaSQLiteインスタンス

::: tip 使用例
```python
    >>> async with AsyncNanaSQLite("mydata.db", table="main") as db:
    ...     users_db = await db.table("users")
    ...     products_db = await db.table("products")
    ...     await users_db.aset("user1", {"name": "Alice"})
    ...     await products_db.aset("prod1", {"name": "Laptop"})
```
:::


---

### `abackup`

```python
def abackup(target_path: str) -> None
```

非同期でデータベースを指定のパスにバックアップします。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `target_path` | `str` | バックアップ先のファイルパス |



---

### `arestore`

```python
def arestore(source_path: str) -> None
```

非同期で指定のパスからデータベースをリストアします。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `source_path` | `str` | リストア元のファイルパス |



---

### `apragma`

```python
def apragma(pragma_name: str, value: Any = None) -> Any
```

非同期で PRAGMA を実行します。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `pragma_name` | `str` | PRAGMA名 |
| `value` |  | 設定する値（Noneの場合は取得） |

#### 戻り値

PRAGMAの結果


---

### `aget_table_schema`

```python
def aget_table_schema(table_name: str = None) -> list[dict]
```

非同期でテーブルのスキーマ情報を取得します。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | 対象のテーブル名（Noneの場合は自身のテーブル） |

#### 戻り値

**Type:** `list[dict]`

スキーマ情報のリスト


---

### `alist_indexes`

```python
def alist_indexes(table_name: str = None) -> list[str]
```

非同期でテーブルのインデックス一覧を取得します。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | 対象のテーブル名（Noneの場合は自身のテーブル） |

#### 戻り値

**Type:** `list[str]`

インデックス名のリスト


---

### `aalter_table_add_column`

```python
def aalter_table_add_column(table_name: str, column_name: str, column_type: str) -> None
```

非同期でテーブルにカラムを追加します。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `column_name` | `str` | カラム名 |
| `column_type` | `str` | カラムの型定義 |



---

### `aupsert`

```python
def aupsert(table_name: str | Any = None, data: Any = None, conflict_columns: list[str] = None) -> int | None
```

非同期で UPSERT 操作を実行します。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str | Any` | テーブル名、または第2引数がNoneの場合はキー名 |
| `data` |  | カラム名と値のdict、または第1引数がキー名の場合は値 |
| `conflict_columns` | `list[str]` | 競合判定に使用するカラム（Noneの場合はINSERT OR REPLACE） |

#### 戻り値

**Type:** `int | None`

挿入/更新されたROWID。キー/値ペア指定時はNone。


---

