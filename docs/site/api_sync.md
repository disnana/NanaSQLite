# 同期 API リファレンス

NanaSQLiteクラスの同期メソッド一覧です。

## NanaSQLite

```python
class NanaSQLite(db_path: str, table: str = 'data', bulk_load: bool = False, optimize: bool = True, cache_size_mb: int = 64, strict_sql_validation: bool = True, allowed_sql_functions: list[str] | None = None, forbidden_sql_functions: list[str] | None = None, max_clause_length: int | None = 1000, cache_strategy: CacheType | Literal['unbounded', 'lru', 'ttl'] = <CacheType.UNBOUNDED: unbounded>, cache_size: int | None = None, cache_ttl: float | None = None, cache_persistence_ttl: bool = False, encryption_key: str | bytes | None = None, encryption_mode: Literal['aes-gcm', 'chacha20', 'fernet'] = 'aes-gcm', lock_timeout: float | None = None, validator: Any | None = None, coerce: bool = False, v2_mode: bool = False, flush_mode: Literal['immediate', 'count', 'time', 'manual'] = 'immediate', flush_interval: float = 3.0, flush_count: int = 100, v2_chunk_size: int = 1000, v2_enable_metrics: bool = False, _shared_connection: apsw.Connection | None = None, _shared_lock: threading.RLock | None = None)
```

(APSW SQLiteをバックエンドとした、セキュリティ・接続管理強化版の辞書型ラッパー (v1.2.0))

内部でPython dictを保持し、操作時にSQLiteとの同期を行います。
v1.2.0では、動的SQLのバリデーション強化、ReDoS対策、および厳格な接続管理が導入されています。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `db_path` | `str` | SQLiteデータベースファイルのパス |
| `table` | `str` | 使用するテーブル名 (デフォルト: "data") |
| `bulk_load` | `bool` | Trueの場合、初期化時に全データをメモリに読み込む |
| `optimize` | `bool` | Trueの場合、WALモードなど高速化設定を適用 |
| `cache_size_mb` | `int` | SQLiteキャッシュサイズ（MB）、デフォルト64MB |
| `strict_sql_validation` | `bool` | Trueの場合、未許可の関数等を含むクエリを拒否 |
| `allowed_sql_functions` | `list[str] | None` | 追加で許可するSQL関数のリスト |
| `forbidden_sql_functions` | `list[str] | None` | 明示的に禁止するSQL関数のリスト |
| `max_clause_length` | `int | None` | SQL句の最大長（ReDoS対策）。Noneで制限なし |
| `cache_strategy` | `CacheType | Literal[unbounded, lru, ttl]` |  |
| `cache_size` | `int | None` |  |
| `cache_ttl` | `float | None` |  |
| `cache_persistence_ttl` | `bool` |  |
| `encryption_key` | `str | bytes | None` |  |
| `encryption_mode` | `Literal[aes-gcm, chacha20, fernet]` |  |
| `lock_timeout` | `float | None` | ロック取得のタイムアウト秒数。Noneで無制限待機 |
| `validator` | `Any | None` | validkit-py のスキーマ（辞書または Schema オブジェクト）。 |
| `coerce` | `bool` | ``True`` の場合、validkit-py の自動変換（コアース）機能を有効にする。 |
| `v2_mode` | `bool` | True の場合、新アーキテクチャ（バックグラウンド非同期書き込み）を有効化 |
| `flush_mode` | `Literal[immediate, count, time, manual]` | v2のフラッシュモード (immediate, count, time, manual) |
| `flush_interval` | `float` | v2のtimeモード時の秒数 |
| `flush_count` | `int` | v2のcountモード時の書き込み閾値 |
| `v2_chunk_size` | `int` | v2フラッシュ時のトランザクション最大件数 |
| `v2_enable_metrics` | `bool` | True の場合、v2エンジンのフラッシュメトリクスを収集する（オプション） |
| `_shared_connection` | `apsw.Connection | None` | 内部用：共有する接続 |
| `_shared_lock` | `threading.RLock | None` | 内部用：共有するロック |



---

## コンストラクタ

## コアメソッド

### `close`

```python
def close() -> None
```

データベース接続を閉じる

注意: table()メソッドで作成されたインスタンスは接続を共有しているため、
接続の所有者（最初に作成されたインスタンス）のみが接続を閉じます。

::: warning 例外
- NanaSQLiteTransactionError: トランザクション中にクローズを試みた場合
:::


---

### `table`

```python
def table(table_name: str, cache_strategy: CacheType | Literal['unbounded', 'lru', 'ttl'] | None = None, cache_size: int | None = None, cache_ttl: float | None = None, cache_persistence_ttl: bool | None = None, validator: Any | None | types.EllipsisType = Ellipsis, coerce: bool | types.EllipsisType = Ellipsis, v2_enable_metrics: bool | types.EllipsisType = Ellipsis)
```

新しいインスタンスを作成しますが、SQLite接続とロックは共有します。
これにより、複数のテーブルインスタンスが同じ接続を使用して
スレッドセーフに動作します。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `cache_strategy` | `CacheType | Literal[unbounded, lru, ttl] | None` | このテーブル用のキャッシュ戦略 (デフォルト: 親と同じ) |
| `cache_size` | `int | None` | このテーブル用のキャッシュサイズ (デフォルト: 親と同じ) |
| `cache_ttl` | `float | None` | TTL 戦略使用時のキャッシュ有効期限（秒）。省略時は親の設定を継承する。 親が非TTLの場合に TTL 戦略を指定する際は必須。 |
| `cache_persistence_ttl` | `bool | None` | TTL 戦略使用時に期限切れキーを DB に永続化するか。 省略時は親の設定を継承する。 |
| `validator` | `Any | None | types.EllipsisType` | このテーブル用の validkit-py スキーマ。 指定しない場合は親インスタンスのスキーマを引き継ぐ。 ``None`` を明示的に渡すとバリデーションなしで使用できる。 |
| `coerce` | `bool | types.EllipsisType` | ``True`` の場合、validkit-py の自動変換機能を有効にする。 指定しない場合は親インスタンスの設定を引き継ぐ。 ⚠️ 重要な注意事項: - 同じテーブルに対して複数のインスタンスを作成しないでください 各インスタンスは独立したキャッシュを持つため、キャッシュ不整合が発生します - 推奨: テーブルインスタンスを変数に保存して再利用してください |
| `v2_enable_metrics` | `bool | types.EllipsisType` |  |

::: warning 例外
- NanaSQLiteConnectionError: 接続が閉じられている場合
:::

::: tip 使用例
```python
    from validkit import v
    with NanaSQLite("app.db", table="main") as main_db:
        users_schema = {"name": v.str(), "age": v.int()}
        users_db = main_db.table("users", validator=users_schema)
        products_db = main_db.table("products")
        users_db["user1"] = {"name": "Alice", "age": 30}
        products_db["prod1"] = {"name": "Laptop"}
```
:::


---

## 辞書インターフェース

### `__getitem__`

```python
def __getitem__(key: str) -> Any
```

dict[key] - 遅延ロード後、メモリから取得


---

### `__setitem__`

```python
def __setitem__(key: str, value: Any) -> None
```

dict[key] = value - 即時書き込み + メモリ更新


---

### `__delitem__`

```python
def __delitem__(key: str) -> None
```

del dict[key] - 即時削除


---

### `__contains__`

```python
def __contains__(key: str) -> bool
```

key in dict - キーの存在確認

軽量な SELECT 1 ... LIMIT 1 クエリで存在確認を行う。
値の読み込みは __getitem__ の _ensure_cached に委譲する。


---

### `__len__`

```python
def __len__() -> int
```

len(dict) - DBの実際の件数を返す


---

### `__iter__`

```python
def __iter__() -> Iterator[str]
```




---

### `keys`

```python
def keys() -> list
```

全キーを取得（DBから）


---

### `values`

```python
def values() -> list
```

全値を取得（一括ロードしてからメモリから）


---

### `items`

```python
def items() -> list
```

全アイテムを取得（一括ロードしてからメモリから）


---

### `get`

```python
def get(key: str, default: Any = None) -> Any
```




---

### `pop`

```python
def pop(key: str, *args) -> Any
```




---

### `update`

```python
def update(mapping: dict | None = None, **kwargs) -> None
```

dict.update(mapping) - 一括更新


---

### `clear`

```python
def clear() -> None
```

dict.clear() - 全削除


---

### `setdefault`

```python
def setdefault(key: str, default: Any = None) -> Any
```




---

### `to_dict`

```python
def to_dict() -> dict
```

全データをPython dictとして取得


---

### `copy`

```python
def copy() -> dict
```

浅いコピーを作成（標準dictを返す）


---

### `clear_cache`

```python
def clear_cache() -> None
```

メモリキャッシュをクリア

DBのデータは削除せず、メモリ上のキャッシュのみ破棄します。


---

## データ管理

### `get_fresh`

```python
def get_fresh(key: str, default: Any = None) -> Any
```

DBから直接読み込み、キャッシュを更新して値を返す

キャッシュをバイパスしてDBから最新の値を取得する。
`execute()`でDBを直接変更した後などに使用。

通常の`get()`よりオーバーヘッドがあるため、
キャッシュとDBの不整合が想定される場合のみ使用推奨。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 取得するキー |
| `default` |  | キーが存在しない場合のデフォルト値 |

#### 戻り値

DBから取得した最新の値（存在しない場合はdefault）

::: tip 使用例
```python
    db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new"', "key"))
    value = db.get_fresh("key")  # DBから最新値を取得
```
:::


---

### `batch_get`

```python
def batch_get(keys: list[str]) -> dict[str, Any]
```

複数のキーを一度に取得（効率的な一括ロード）

1回の `SELECT IN (...)` クエリで複数のキーをDBから取得する。
取得した値は自動的にキャッシュに保存される。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `keys` | `list[str]` | 取得するキーのリスト |

#### 戻り値

**Type:** `dict[str, Any]`

取得に成功したキーと値の dict

::: tip 使用例
```python
    results = db.batch_get(["user1", "user2", "user3"])
    print(results)  # {"user1": {...}, "user2": {...}}
```
:::


---

### `flush`

```python
def flush() -> None
```




---

### `load_all`

```python
def load_all() -> None
```

一括読み込み: 全データをメモリに展開


---

### `refresh`

```python
def refresh(key: str = None) -> None
```

キャッシュを更新（DBから再読み込み）

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 特定のキーのみ更新。Noneの場合は全キャッシュをクリアして再読み込み |



---

### `is_cached`

```python
def is_cached(key: str) -> bool
```

キーがキャッシュ済みかどうか


---

### `batch_update`

```python
def batch_update(mapping: dict[str, Any]) -> None
```

一括書き込み（トランザクション + executemany使用で超高速）

大量のデータを一度に書き込む場合、通常のupdateより10-100倍高速。
v1.0.3rc5でexecutemanyによる最適化を追加。
v1.3.4b2より、validkit バリデーター設定時は全値を事前に検証する。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `mapping` | `dict[str, Any]` | 書き込むキーと値のdict |

#### 戻り値

::: tip 使用例
```python
    db.batch_update({"key1": "value1", "key2": "value2", ...})
```
:::


---

### `batch_update_partial`

```python
def batch_update_partial(mapping: dict[str, Any]) -> dict[str, str]
```

一括書き込み（部分成功モード）

`batch_update()` のアトミック契約は維持したまま、各キーを個別に準備し、
バリデーションまたはシリアライズに失敗したキーだけをスキップして残りを書き込む。
返り値は、拒否されたキーとその理由の辞書。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `mapping` | `dict[str, Any]` | 書き込むキーと値のdict |

#### 戻り値

**Type:** `dict[str, str]`

拒否されたキー -> エラーメッセージ のdict

::: tip 使用例
```python
    failed = db.batch_update_partial({"ok": 1, "bad": object()})
    print(failed)
```
:::


---

### `batch_delete`

```python
def batch_delete(keys: list[str]) -> None
```

一括削除（トランザクション + executemany使用で高速）

v1.0.3rc5でexecutemanyによる最適化を追加。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `keys` | `list[str]` | 削除するキーのリスト |



---

## トランザクション制御

### `begin_transaction`

```python
def begin_transaction() -> None
```

トランザクションを開始

Note:
    SQLiteはネストされたトランザクションをサポートしていません。
    既にトランザクション中の場合、NanaSQLiteTransactionErrorが発生します。

::: warning 例外
- NanaSQLiteTransactionError: 既にトランザクション中の場合
- NanaSQLiteConnectionError: 接続が閉じられている場合
- NanaSQLiteDatabaseError: トランザクション開始に失敗した場合
:::

::: tip 使用例
```python
    db.begin_transaction()
    try:
        db.sql_insert("users", {"name": "Alice"})
        db.sql_insert("users", {"name": "Bob"})
        db.commit()
    except:
        db.rollback()
```
:::


---

### `commit`

```python
def commit() -> None
```

トランザクションをコミット

::: warning 例外
- NanaSQLiteTransactionError: トランザクション外でコミットを試みた場合
- NanaSQLiteConnectionError: 接続が閉じられている場合
- NanaSQLiteDatabaseError: コミットに失敗した場合
:::


---

### `rollback`

```python
def rollback() -> None
```

トランザクションをロールバック

::: warning 例外
- NanaSQLiteTransactionError: トランザクション外でロールバックを試みた場合
- NanaSQLiteConnectionError: 接続が閉じられている場合
- NanaSQLiteDatabaseError: ロールバックに失敗した場合
:::


---

### `in_transaction`

```python
def in_transaction() -> bool
```

現在トランザクション中かどうかを返す

#### 戻り値

**Type:** `bool`

bool: トランザクション中の場合True

::: tip 使用例
```python
    db.begin_transaction()
    print(db.in_transaction())  # True
    db.commit()
    print(db.in_transaction())  # False
```
:::


---

### `transaction`

```python
def transaction()
```

トランザクションのコンテキストマネージャ

コンテキストマネージャ内で例外が発生しない場合は自動的にコミット、
例外が発生した場合は自動的にロールバックします。

::: warning 例外
- NanaSQLiteTransactionError: 既にトランザクション中の場合
:::

::: tip 使用例
```python
    with db.transaction():
        db.sql_insert("users", {"name": "Alice"})
        db.sql_insert("users", {"name": "Bob"})
        # 自動的にコミット、例外時はロールバック
```
:::


---

## SQLラッパー (CRUD)

### `sql_insert`

```python
def sql_insert(table_name: str, data: dict) -> int
```

dictから直接INSERT

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
    rowid = db.sql_insert("users", {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 25
    })
```
:::


---

### `sql_update`

```python
def sql_update(table_name: str, data: dict, where: str, parameters: tuple = None) -> int
```

dictとwhere条件でUPDATE

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `data` | `dict` | 更新するカラム名と値のdict |
| `where` | `str` | WHERE句の条件 |
| `parameters` | `tuple` | WHERE句のパラメータ |

#### 戻り値

**Type:** `int`

更新された行数

::: tip 使用例
```python
    count = db.sql_update("users",
        {"age": 26, "status": "active"},
        "name = ?",
        ("Alice",)
    )
```
:::


---

### `sql_delete`

```python
def sql_delete(table_name: str, where: str, parameters: tuple = None) -> int
```

where条件でDELETE

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `where` | `str` | WHERE句の条件 |
| `parameters` | `tuple` | WHERE句のパラメータ |

#### 戻り値

**Type:** `int`

削除された行数

::: tip 使用例
```python
    count = db.sql_delete("users", "age < ?", (18,))
```
:::


---

### `upsert`

```python
def upsert(table_name: str | Any = None, data: Any = None, conflict_columns: list[str] = None) -> int | None
```

INSERT OR REPLACE の簡易版（upsert）
v2モードが有効で、キー/値のペアとして呼び出された場合はバックグラウンドキューに送られます。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str | Any` | テーブル名、または第2引数がNoneの場合はキー名 |
| `data` |  | カラム名と値のdict、または第1引数がキー名の場合は値 |
| `conflict_columns` | `list[str]` | 競合判定に使用するカラム（Noneの場合はINSERT OR REPLACE）。 キー/値のペア指定時は無視されます。 |

#### 戻り値

**Type:** `int | None`

挿入/更新されたROWID。v2モードでのキー/値ペア指定時はNone。

::: tip 使用例
```python
    # テーブル指定（標準）
    db.upsert("users", {"id": 1, "name": "Alice", "age": 25})
    # キー/値指定 (v2互換)
    db.upsert("user:1", {"name": "Nana"})
```
:::


---

## クエリ

### `query`

```python
def query(table_name: str = None, columns: list[str] = None, where: str = None, parameters: tuple = None, order_by: str = None, limit: int = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> list[dict]
```

シンプルなSELECTクエリを実行

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名（Noneの場合はデフォルトテーブル） |
| `columns` | `list[str]` | 取得するカラムのリスト（Noneの場合は全カラム） |
| `where` | `str` | WHERE句の条件（パラメータバインディング使用推奨） |
| `parameters` | `tuple` | WHERE句のパラメータ |
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
    # デフォルトテーブルから全データ取得
    results = db.query()
```

```python
    # 条件付き検索
    results = db.query(
        table_name="users",
        columns=["id", "name", "email"],
        where="age > ?",
        parameters=(20,),
        order_by="name ASC",
        limit=10
    )
```
:::


---

### `count`

```python
def count(table_name: str = None, where: str = None, parameters: tuple = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> int
```

レコード数を取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名（Noneの場合はデフォルトテーブル） |
| `where` | `str` | WHERE句の条件（オプション） |
| `parameters` | `tuple` | WHERE句のパラメータ |
| `strict_sql_validation` | `bool` | Trueの場合、未許可の関数等を含むクエリを拒否 |
| `allowed_sql_functions` | `list[str]` | このクエリで一時的に許可するSQL関数のリスト |
| `forbidden_sql_functions` | `list[str]` | このクエリで一時的に禁止するSQL関数のリスト |
| `override_allowed` | `bool` | Trueの場合、インスタンス許可設定を無視 |

::: tip 使用例
```python
    total = db.count("users")
    adults = db.count("users", "age >= ?", (18,))
```
:::


---

### `exists`

```python
def exists(table_name: str, where: str, parameters: tuple = None) -> bool
```

レコードの存在確認

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `where` | `str` | WHERE句の条件 |
| `parameters` | `tuple` | WHERE句のパラメータ |

#### 戻り値

**Type:** `bool`

存在する場合True

::: tip 使用例
```python
    if db.exists("users", "email = ?", ("alice@example.com",)):
        print("User exists")
```
:::


---

### `query_with_pagination`

```python
def query_with_pagination(table_name: str = None, columns: list[str] = None, where: str = None, parameters: tuple = None, order_by: str = None, limit: int = None, offset: int = None, group_by: str = None, strict_sql_validation: bool = None, allowed_sql_functions: list[str] = None, forbidden_sql_functions: list[str] = None, override_allowed: bool = False) -> list[dict]
```

拡張されたクエリ（offset、group_by対応）

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `columns` | `list[str]` | 取得するカラム |
| `where` | `str` | WHERE句 |
| `parameters` | `tuple` | パラメータ |
| `order_by` | `str` | ORDER BY句 |
| `limit` | `int` | LIMIT句 |
| `offset` | `int` | OFFSET句（ページネーション用） |
| `group_by` | `str` | GROUP BY句 |
| `strict_sql_validation` | `bool` | Trueの場合、未許可の関数等を含むクエリを拒否 |
| `allowed_sql_functions` | `list[str]` | このクエリで一時的に許可するSQL関数のリスト |
| `forbidden_sql_functions` | `list[str]` | このクエリで一時的に禁止するSQL関数のリスト |
| `override_allowed` | `bool` | Trueの場合、インスタンス許可設定を無視 |

#### 戻り値

**Type:** `list[dict]`

結果のリスト

::: tip 使用例
```python
    # ページネーション
    page2 = db.query_with_pagination("users",
        limit=10, offset=10, order_by="id ASC")
```

```python
    # グループ集計
    stats = db.query_with_pagination("orders",
        columns=["user_id", "COUNT(*) as order_count"],
        group_by="user_id"
    )
```
:::


---

## 直接SQL実行

### `execute`

```python
def execute(sql: str, parameters: tuple | None = None) -> apsw.Cursor
```

SQLを直接実行

任意のSQL文を実行できる。SELECT、INSERT、UPDATE、DELETEなど。
パラメータバインディングをサポート（SQLインジェクション対策）。

    このメソッドで直接デフォルトテーブル（data）を操作した場合、
    内部キャッシュ（_data）と不整合が発生する可能性があります。
    キャッシュを更新するには `refresh()` を呼び出してください。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `sql` | `str` | 実行するSQL文 |
| `parameters` | `tuple | None` | SQLのパラメータ（?プレースホルダー用） |

#### 戻り値

**Type:** `apsw.Cursor`

APSWのCursorオブジェクト（結果の取得に使用）

::: warning 例外
- NanaSQLiteConnectionError: 接続が閉じられている場合
- NanaSQLiteDatabaseError: SQL実行エラー
:::

::: tip 使用例
```python
    cursor = db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
    for row in cursor:
        print(row)
```

    # キャッシュ更新が必要な場合:
```python
    db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new"', "key"))
    db.refresh("key")  # キャッシュを更新
```
:::


---

### `execute_many`

```python
def execute_many(sql: str, parameters_list: list[tuple]) -> None
```

SQLを複数のパラメータで一括実行

同じSQL文を複数のパラメータセットで実行（トランザクション使用）。
大量のINSERTやUPDATEを高速に実行できる。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `sql` | `str` | 実行するSQL文 |
| `parameters_list` | `list[tuple]` | パラメータのリスト |

::: tip 使用例
```python
    db.execute_many(
        "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
        [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
    )
```
:::


---

### `fetch_one`

```python
def fetch_one(sql: str, parameters: tuple = None) -> tuple | None
```

SQLを実行して1行取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `sql` | `str` | 実行するSQL文 |
| `parameters` | `tuple` | SQLのパラメータ |

#### 戻り値

**Type:** `tuple | None`

1行の結果（tuple）、結果がない場合はNone

::: tip 使用例
```python
    row = db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
    print(row[0])
```
:::


---

### `fetch_all`

```python
def fetch_all(sql: str, parameters: tuple = None) -> list[tuple]
```

SQLを実行して全行取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `sql` | `str` | 実行するSQL文 |
| `parameters` | `tuple` | SQLのパラメータ |

#### 戻り値

**Type:** `list[tuple]`

全行の結果（tupleのリスト）

::: tip 使用例
```python
    rows = db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
    for key, value in rows:
        print(key, value)
```
:::


---

## スキーマ管理

### `create_table`

```python
def create_table(table_name: str, columns: dict, if_not_exists: bool = True, primary_key: str = None) -> None
```

テーブルを作成

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `columns` | `dict` | カラム定義のdict（カラム名: SQL型） |
| `if_not_exists` | `bool` | Trueの場合、存在しない場合のみ作成 |
| `primary_key` | `str` | プライマリキーのカラム名（Noneの場合は指定なし） |

::: tip 使用例
```python
    db.create_table("users", {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "email": "TEXT UNIQUE",
        "age": "INTEGER"
    })
    db.create_table("posts", {
        "id": "INTEGER",
        "title": "TEXT",
        "content": "TEXT"
    }, primary_key="id")
```
:::


---

### `create_index`

```python
def create_index(index_name: str, table_name: str, columns: list[str], unique: bool = False, if_not_exists: bool = True) -> None
```

インデックスを作成

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
    db.create_index("idx_users_email", "users", ["email"], unique=True)
    db.create_index("idx_posts_user", "posts", ["user_id", "created_at"])
```
:::


---

### `table_exists`

```python
def table_exists(table_name: str) -> bool
```

テーブルの存在確認

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |

#### 戻り値

**Type:** `bool`

存在する場合True、しない場合False

::: tip 使用例
```python
    if db.table_exists("users"):
        print("users table exists")
```
:::


---

### `list_tables`

```python
def list_tables() -> list[str]
```

データベース内の全テーブル一覧を取得

#### 戻り値

**Type:** `list[str]`

テーブル名のリスト

::: tip 使用例
```python
    tables = db.list_tables()
    print(tables)  # ['data', 'users', 'posts']
```
:::


---

### `drop_table`

```python
def drop_table(table_name: str, if_exists: bool = True) -> None
```

テーブルを削除

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `if_exists` | `bool` | Trueの場合、存在する場合のみ削除（エラーを防ぐ） |

::: tip 使用例
```python
    db.drop_table("old_table")
    db.drop_table("temp", if_exists=True)
```
:::


---

### `drop_index`

```python
def drop_index(index_name: str, if_exists: bool = True) -> None
```

インデックスを削除

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `index_name` | `str` | インデックス名 |
| `if_exists` | `bool` | Trueの場合、存在する場合のみ削除 |

::: tip 使用例
```python
    db.drop_index("idx_users_email")
```
:::


---

### `alter_table_add_column`

```python
def alter_table_add_column(table_name: str, column_name: str, column_type: str, default: Any = None) -> None
```

既存テーブルにカラムを追加

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `column_name` | `str` | カラム名 |
| `column_type` | `str` | カラムの型（SQL型） |
| `default` |  | デフォルト値（Noneの場合は指定なし） |

::: tip 使用例
```python
    db.alter_table_add_column("users", "phone", "TEXT")
    db.alter_table_add_column("users", "status", "TEXT", default="'active'")
```
:::


---

### `get_table_schema`

```python
def get_table_schema(table_name: str = None) -> list[dict]
```

テーブル構造を取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 (Noneの場合は自身のテーブル) |

#### 戻り値

**Type:** `list[dict]`

カラム情報のリスト（各カラムはdict）

::: tip 使用例
```python
    schema = db.get_table_schema("users")
    for col in schema:
        print(f"{col['name']}: {col['type']}")
```
:::


---

### `list_indexes`

```python
def list_indexes(table_name: str = None) -> list[dict]
```

インデックス一覧を取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名（Noneの場合は全インデックス） |

#### 戻り値

**Type:** `list[dict]`

インデックス情報のリスト

::: tip 使用例
```python
    indexes = db.list_indexes("users")
    for idx in indexes:
        print(f"{idx['name']}: {idx['columns']}")
```
:::


---

## ユーティリティ関数

### `vacuum`

```python
def vacuum() -> None
```

データベースを最適化（VACUUM実行）

削除されたレコードの領域を回収し、データベースファイルを最適化。

::: tip 使用例
```python
    db.vacuum()
```
:::


---

### `get_db_size`

```python
def get_db_size() -> int
```

データベースファイルのサイズを取得（バイト単位）

#### 戻り値

**Type:** `int`

データベースファイルのサイズ

::: tip 使用例
```python
    size = db.get_db_size()
    print(f"DB size: {size / 1024 / 1024:.2f} MB")
```
:::


---

### `get_last_insert_rowid`

```python
def get_last_insert_rowid() -> int
```

最後に挿入されたROWIDを取得

#### 戻り値

**Type:** `int`

最後に挿入されたROWID

::: tip 使用例
```python
    db.sql_insert("users", {"name": "Alice"})
    rowid = db.get_last_insert_rowid()
```
:::


---

### `pragma`

```python
def pragma(pragma_name: str, value: Any = None) -> Any
```

PRAGMA設定の取得/設定

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `pragma_name` | `str` | PRAGMA名 |
| `value` |  | 設定値（Noneの場合は取得のみ） |

#### 戻り値

valueがNoneの場合は現在の値、そうでない場合はNone

::: tip 使用例
```python
    # 取得
    mode = db.pragma("journal_mode")
```

```python
    # 設定
    db.pragma("foreign_keys", 1)
```
:::


---

## バックアップ & リストア

### `backup`

```python
def backup(dest_path: str) -> None
```

データベースをファイルにバックアップする

APSW の SQLite バックアップ API を使用して、現在の DB 全体を dest_path に書き出します。
SQLite のトランザクション機構により、他の SQLite 接続が同時に読み書きしていても
データの整合性を保ったままバックアップできます。
NanaSQLite の内部ロックはバックアップ中に保持しないため、同一プロセス内の
他の NanaSQLite 操作をブロックしません。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `dest_path` | `str` | バックアップ先ファイルパス |

::: warning 例外
- NanaSQLiteClosedError: 接続が閉じられている場合
- NanaSQLiteValidationError: dest_path が現在のDBファイルと同一の場合（自己コピー防止）、または
- dest_path がインメモリDB文字列（':memory:' など）の場合（永続化されないため）
- NanaSQLiteDatabaseError: バックアップ中にエラーが発生した場合
- NanaSQLiteLockError: lock_timeout 設定によりロック取得に失敗した場合
:::


---

### `restore`

```python
def restore(src_path: str) -> None
```

バックアップファイルからデータベースをリストアする

現在の接続を一時的に閉じ、src_path のファイルを DB パスにコピーし、
stale な WAL/SHM/journal サイドカーファイル（-wal/-shm/-journal）を
削除してから再接続します。
リストア後はメモリキャッシュがクリアされ、DB の内容が反映されます。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `src_path` | `str` | リストア元バックアップファイルパス |

::: warning 例外
- NanaSQLiteClosedError: 接続が閉じられている場合
- NanaSQLiteConnectionError: 接続を所有していない (table() で取得した) インスタンスから呼ばれた場合
- NanaSQLiteValidationError: 現在のDBがインメモリDB（':memory:' など）の場合（ファイル置換が不可能なため）
- NanaSQLiteTransactionError: トランザクション中に呼ばれた場合
- NanaSQLiteDatabaseError: リストア中にエラーが発生した場合
- NanaSQLiteLockError: lock_timeout 設定によりロック取得に失敗した場合
:::


---

## Pydantic サポート

### `set_model`

```python
def set_model(key: str, model: Any) -> None
```

Pydanticモデルを保存

Pydanticモデル（BaseModelを継承したクラス）をシリアライズして保存。
model_dump()メソッドを使用してdictに変換し、モデルのクラス情報も保存。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 保存するキー |
| `model` |  | Pydanticモデルのインスタンス |

::: tip 使用例
```python
    from pydantic import BaseModel
    class User(BaseModel):
        name: str
        age: int
    user = User(name="Nana", age=20)
    db.set_model("user", user)
```
:::


---

### `get_model`

```python
def get_model(key: str, model_class: type = None) -> Any
```

Pydanticモデルを取得

保存されたPydanticモデルをデシリアライズして復元。
model_classが指定されていない場合は、保存時のクラス情報を使用。

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `key` | `str` | 取得するキー |
| `model_class` | `type` | Pydanticモデルのクラス（Noneの場合は自動検出を試みる） |

#### 戻り値

Pydanticモデルのインスタンス

::: tip 使用例
```python
    user = db.get_model("user", User)
    print(user.name)  # "Nana"
```
:::


---

## その他のメソッド

### `get_dlq`

```python
def get_dlq() -> list[dict[str, Any]]
```

[v2 Feature] 現在のデッドレターキュー（DLQ）の内容を取得します。
v2モードが無効な場合は空のリストを返します。


---

### `retry_dlq`

```python
def retry_dlq() -> None
```

[v2 Feature] デッドレターキュー（DLQ）内の全アイテムを再試行キューに戻します。
v2モードが無効な場合は何もしません。


---

### `clear_dlq`

```python
def clear_dlq() -> None
```

[v2 Feature] デッドレターキュー（DLQ）の内容をクリアします。
v2モードが無効な場合は何もしません。


---

### `get_v2_metrics`

```python
def get_v2_metrics() -> dict[str, Any]
```

[v2 Feature] 現在のメトリクス情報を取得します（有効な場合）。
v2モード自体またはメトリクスが無効な場合は空の辞書を返します。


---

### `export_table_to_dict`

```python
def export_table_to_dict(table_name: str) -> list[dict]
```

テーブル全体をdictのリストとして取得

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |

#### 戻り値

**Type:** `list[dict]`

全レコードのリスト

::: tip 使用例
```python
    all_users = db.export_table_to_dict("users")
```
:::


---

### `import_from_dict_list`

```python
def import_from_dict_list(table_name: str, data_list: list[dict]) -> int
```

dictのリストからテーブルに一括挿入

#### 引数名

| 引数名 | 型 | 説明 |
|---|---|---|
| `table_name` | `str` | テーブル名 |
| `data_list` | `list[dict]` | 挿入するデータのリスト |

#### 戻り値

**Type:** `int`

挿入された行数

::: tip 使用例
```python
    users = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30}
    ]
    count = db.import_from_dict_list("users", users)
```
:::


---

### `popitem`

```python
def popitem()
```




---

