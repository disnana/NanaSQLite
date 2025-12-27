# AsyncNanaSQLite API リファレンス

非同期版 `AsyncNanaSQLite` クラスの完全なドキュメントです。

## クラス: `AsyncNanaSQLite`

```python
class AsyncNanaSQLite
```

`NanaSQLite` の非ブロッキング非同期ラッパーです。
すべてのデータベース操作をスレッドプールエグゼキュータに委譲し、メインの `asyncio` イベントループが決してブロックされないようにします。これはFastAPIやdiscord.pyボットのような高並行性アプリケーションに不可欠です。

---

## コンストラクタ

### `__init__`

```python
def __init__(
    self,
    db_path: str,
    table: str = "data",
    bulk_load: bool = False,
    optimize: bool = True,
    cache_size_mb: int = 64,
    max_workers: int = 5,
    thread_name_prefix: str = "AsyncNanaSQLite",
    strict_sql_validation: bool = True,
    allowed_sql_functions: list[str] | None = None,
    forbidden_sql_functions: list[str] | None = None,
    max_clause_length: int | None = 1000,
    read_pool_size: int = 0,
)
```

AsyncNanaSQLiteインターフェースを初期化します。

**パラメータ:**

- `db_path` (str): SQLiteデータベースファイルのパス。
- `table` (str, 任意): ストレージに使用するテーブル名。デフォルトは `"data"`。
- `max_workers` (int, 任意): スレッドプールの最大スレッド数。デフォルトは `5`。
  - 読み取り負荷が高い並行処理の場合、この値を増やします。
- `read_pool_size` (int, 任意): 専用の読み取り専用接続プールのサイズ。デフォルトは `0`（無効）。
  - これを有効にする（例: `read_pool_size=4`）と、書き込みロックをバイパスして並列読み取りが可能になります。
- `strict_sql_validation` など: `NanaSQLite` と同じセキュリティパラメータ。

---

## コアメソッド

### `close`

```python
async def close(self) -> None
```

データベース接続を閉じ、スレッドプールをシャットダウンします。

### `table`

```python
async def table(self, table_name: str) -> AsyncNanaSQLite
```

サブテーブル用の新しい `AsyncNanaSQLite` インスタンスを非同期に作成します。
スレッドプールと接続は親と共有されます。

---

## 非同期辞書インターフェース

これらのメソッドは標準の辞書操作をミラーリングしていますが、`async` です。

### `aget` (エイリアス: `get`)
```python
async def aget(self, key: str, default: Any = None) -> Any
```
非同期で値を取得します。

### `aset`
```python
async def aset(self, key: str, value: Any) -> None
```
非同期で値を設定します。

### `adelete`
```python
async def adelete(self, key: str) -> None
```
非同期でキーを削除します。

### `acontains` (エイリアス: `contains`)
```python
async def acontains(self, key: str) -> bool
```
非同期で存在確認を行います。

### `alen`
```python
async def alen(self) -> int
```
非同期でアイテム数を返します。

### `akeys` (エイリアス: `keys`)
```python
async def akeys(self) -> list[str]
```
非同期で全キーを返します。

### `avalues` (エイリアス: `values`)
```python
async def avalues(self) -> list[Any]
```
非同期で全値を返します。

### `aitems` (エイリアス: `items`)
```python
async def aitems(self) -> list[tuple[str, Any]]
```
非同期で全アイテムを返します。

### `aupdate`
```python
async def aupdate(self, mapping: dict = None, **kwargs) -> None
```
非同期で複数キーを更新します。

### `aclear`
```python
async def aclear(self) -> None
```
非同期でデータベースを実質的に空にします。

### `apop`
```python
async def apop(self, key: str, *args) -> Any
```
非同期で値をポップします。

### `asetdefault`
```python
async def asetdefault(self, key: str, default: Any = None) -> Any
```
非同期でデフォルト値を設定します。

---

## データ管理

### `load_all`

```python
async def load_all(self) -> None
```
非同期で全データをメモリに読み込みます。

### `refresh`

```python
async def refresh(self, key: str = None) -> None
```
非同期でキャッシュをリフレッシュします。

### `get_fresh`

```python
async def get_fresh(self, key: str, default: Any = None) -> Any
```
非同期でDBから最新データを取得します。

### `batch_update`

```python
async def batch_update(self, mapping: dict[str, Any]) -> None
```
非同期の一括更新。

### `batch_delete`

```python
async def batch_delete(self, keys: list[str]) -> None
```
非同期の一括削除。

### `abatch_get`

```python
async def abatch_get(self, keys: list[str]) -> dict[str, Any]
```
非同期の一括取得。

---

## トランザクション制御

### `begin_transaction`

```python
async def begin_transaction(self) -> None
```
トランザクションを開始します。

### `commit`

```python
async def commit(self) -> None
```
トランザクションをコミットします。

### `rollback`

```python
async def rollback(self) -> None
```
トランザクションをロールバックします。

### `in_transaction`

```python
async def in_transaction(self) -> bool
```
トランザクション状態を確認します。

### `transaction`

```python
def transaction(self)
```
トランザクション用の非同期コンテキストマネージャです。

```python
async with db.transaction():
    await db.aset("a", 1)
```

---

## クエリ & SQL

`NanaSQLite` で利用可能なすべてのSQLおよびクエリメソッドは、ここで `async` メソッドとして利用可能です。

### `query` (エイリアス: `aquery`)
```python
async def query(self, ...) -> list[dict]
```

### `query_with_pagination` (エイリアス: `aquery_with_pagination`)
```python
async def query_with_pagination(self, ...) -> list[dict]
```

### `execute` (エイリアス: `aexecute`)
```python
async def execute(self, sql: str, parameters: tuple | None = None) -> Any
```

### `fetch_all` (エイリアス: `afetch_all`)
```python
async def fetch_all(self, sql: str, parameters: tuple = None) -> list[tuple]
```

### `sql_insert` (エイリアス: `asql_insert`)
```python
async def sql_insert(self, table_name: str, data: dict) -> int
```

*（`sql_update`, `sql_delete`, `count`, `create_table`, `create_index` 等も同様）*

---

## Pydantic サポート

### `set_model`

```python
async def set_model(self, key: str, model: Any) -> None
```

### `get_model`

```python
async def get_model(self, key: str, model_class: type = None) -> Any
```

---

## 上級者向け

### `sync_db`

```python
@property
def sync_db(self) -> NanaSQLite | None
```
内部の同期 `NanaSQLite` インスタンスへのアクセス。
**警告**: 非同期関数から `sync_db` のメソッドを呼び出すと、イベントループがブロックされます。注意して使用してください。
