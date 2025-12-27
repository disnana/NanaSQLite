# 非同期 API リファレンス

AsyncNanaSQLiteクラスの非同期メソッド一覧です。

## AsyncNanaSQLite

最適化されたスレッドプールを使用するNanaSQLiteの非同期ラッパー

データベース操作はすべて専用のスレッドプール内で実行され、非同期イベントループのブロックを防ぎます。
これにより、FastAPIやaiohttpなどの非同期アプリケーションで安全に使用できます。

高負荷なシナリオにおいて最適な並行性とパフォーマンスを実現するため、
カスタマイズ可能なスレッドプールを使用しています。

#### 📥 引数

    - **db_path:**  SQLiteデータベースファイルのパス
    - **table:**  デフォルト: "data"
    - **bulk_load:**  Trueの場合、初期化時に全データをメモリに読み込む
    - **optimize:**  Trueの場合、WALモードなど高速化設定を適用
    - **cache_size_mb:**  SQLiteキャッシュサイズ（MB）、デフォルト64MB
    - **strict_sql_validation:**  v1.2.0
    - **max_clause_length:**  SQL句の最大長（ReDoS対策、v1.2.0）
    - **max_workers:**  スレッドプール内の最大ワーカー数（デフォルト: 5）
    - **thread_name_prefix:**  スレッド名のプレフィックス（デフォルト: "AsyncNanaSQLite"）

#### 💡 使用例

```python
    >>> async with AsyncNanaSQLite("mydata.db") as db:
    ...     await db.aset("config", {"theme": "dark"})
    ...     config = await db.aget("config")
    ...     print(config)
```

```python
    >>> # 高負荷環境向けの設定
    >>> async with AsyncNanaSQLite("mydata.db", max_workers=10) as db:
    ...     # 並行処理が多い場合に最適化
    ...     results = await asyncio.gather(*[db.aget(f"key_{i}") for i in range(100)])
```

---

## メソッド

### __init__

```python
__init__(self, db_path: 'str', table: 'str' = 'data', bulk_load: 'bool' = False, optimize: 'bool' = True, cache_size_mb: 'int' = 64, max_workers: 'int' = 5, thread_name_prefix: 'str' = 'AsyncNanaSQLite', strict_sql_validation: 'bool' = True, allowed_sql_functions: 'list[str] | None' = None, forbidden_sql_functions: 'list[str] | None' = None, max_clause_length: 'int | None' = 1000, read_pool_size: 'int' = 0)
```


#### 📥 引数

    - **db_path:**  SQLiteデータベースファイルのパス
    - **table:**  デフォルト: "data"
    - **bulk_load:**  Trueの場合、初期化時に全データをメモリに読み込む
    - **optimize:**  Trueの場合、WALモードなど高速化設定を適用
    - **cache_size_mb:**  SQLiteキャッシュサイズ（MB）、デフォルト64MB
    - **max_workers:**  スレッドプール内の最大ワーカー数（デフォルト: 5）
    - **thread_name_prefix:**  スレッド名のプレフィックス（デフォルト: "AsyncNanaSQLite"）
    - **strict_sql_validation:**  v1.2.0
    - **allowed_sql_functions:**  v1.2.0
    - **forbidden_sql_functions:**  v1.2.0
    - **max_clause_length:**  v1.2.0
    - **read_pool_size:**  デフォルト: 0 = 無効) (v1.1.0

---

### aget

```python
aget(self, key: 'str', default: 'Any' = None) -> 'Any'
```

非同期でキーの値を取得

#### 📥 引数

    - **key:**  取得するキー
    - **default:**  キーが存在しない場合のデフォルト値

#### 📤 戻り値

    キーの値（存在しない場合はdefault）

#### 💡 使用例

```python
    >>> user = await db.aget("user")
    >>> config = await db.aget("config", {})
```

---

### get

```python
get(self, key: 'str', default: 'Any' = None) -> 'Any'
```

非同期でキーの値を取得

#### 📥 引数

    - **key:**  取得するキー
    - **default:**  キーが存在しない場合のデフォルト値

#### 📤 戻り値

    キーの値（存在しない場合はdefault）

#### 💡 使用例

```python
    >>> user = await db.aget("user")
    >>> config = await db.aget("config", {})
```

---

### aset

```python
aset(self, key: 'str', value: 'Any') -> 'None'
```

非同期でキーに値を設定

#### 📥 引数

    - **key:**  設定するキー
    - **value:**  設定する値

#### 💡 使用例

```python
    >>> await db.aset("user", {"name": "Nana", "age": 20})
```

---

### adelete

```python
adelete(self, key: 'str') -> 'None'
```

非同期でキーを削除

#### 📥 引数

    - **key:**  削除するキー

#### ⚠️ 例外

    - **KeyError:**  キーが存在しない場合

#### 💡 使用例

```python
    >>> await db.adelete("old_data")
```

---

### acontains

```python
acontains(self, key: 'str') -> 'bool'
```

非同期でキーの存在確認

#### 📥 引数

    - **key:**  確認するキー

#### 📤 戻り値

    キーが存在する場合True

#### 💡 使用例

```python
    >>> if await db.acontains("user"):
    ...     print("User exists")
```

---

### contains

```python
contains(self, key: 'str') -> 'bool'
```

非同期でキーの存在確認

#### 📥 引数

    - **key:**  確認するキー

#### 📤 戻り値

    キーが存在する場合True

#### 💡 使用例

```python
    >>> if await db.acontains("user"):
    ...     print("User exists")
```

---

### alen

```python
alen(self) -> 'int'
```

非同期でデータベースの件数を取得

#### 📤 戻り値

    データベース内のキーの数

#### 💡 使用例

```python
    >>> count = await db.alen()
```

---

### akeys

```python
akeys(self) -> 'list[str]'
```

非同期で全キーを取得

#### 📤 戻り値

    全キーのリスト

#### 💡 使用例

```python
    >>> keys = await db.akeys()
```

---

### keys

```python
keys(self) -> 'list[str]'
```

非同期で全キーを取得

#### 📤 戻り値

    全キーのリスト

#### 💡 使用例

```python
    >>> keys = await db.akeys()
```

---

### avalues

```python
avalues(self) -> 'list[Any]'
```

非同期で全値を取得

#### 📤 戻り値

    全値のリスト

#### 💡 使用例

```python
    >>> values = await db.avalues()
```

---

### values

```python
values(self) -> 'list[Any]'
```

非同期で全値を取得

#### 📤 戻り値

    全値のリスト

#### 💡 使用例

```python
    >>> values = await db.avalues()
```

---

### aitems

```python
aitems(self) -> 'list[tuple[str, Any]]'
```

非同期で全アイテムを取得

#### 📤 戻り値

    全アイテムのリスト（キーと値のタプル）

#### 💡 使用例

```python
    >>> items = await db.aitems()
```

---

### items

```python
items(self) -> 'list[tuple[str, Any]]'
```

非同期で全アイテムを取得

#### 📤 戻り値

    全アイテムのリスト（キーと値のタプル）

#### 💡 使用例

```python
    >>> items = await db.aitems()
```

---

### apop

```python
apop(self, key: 'str', *args) -> 'Any'
```

非同期でキーを削除して値を返す

#### 📥 引数

    - **key:**  削除するキー
    *args: デフォルト値（オプション）

#### 📤 戻り値

    削除されたキーの値

#### 💡 使用例

```python
    >>> value = await db.apop("temp_data")
    >>> value = await db.apop("maybe_missing", "default")
```

---

### aupdate

```python
aupdate(self, mapping: 'dict' = None, **kwargs) -> 'None'
```

非同期で複数のキーを更新

#### 📥 引数

    - **mapping:**  更新するキーと値のdict
    **kwargs: キーワード引数として渡す更新

#### 💡 使用例

```python
    >>> await db.aupdate({"key1": "value1", "key2": "value2"})
    >>> await db.aupdate(key3="value3", key4="value4")
```

---

### aclear

```python
aclear(self) -> 'None'
```

非同期で全データを削除

#### 💡 使用例

```python
    >>> await db.aclear()
```

---

### asetdefault

```python
asetdefault(self, key: 'str', default: 'Any' = None) -> 'Any'
```

非同期でキーが存在しない場合のみ値を設定

#### 📥 引数

    - **key:**  キー
    - **default:**  デフォルト値

#### 📤 戻り値

    キーの値（既存または新規設定した値）

#### 💡 使用例

```python
    >>> value = await db.asetdefault("config", {})
```

---

### aload_all

```python
aload_all(self) -> 'None'
```

非同期で全データを一括ロード

#### 💡 使用例

```python
    >>> await db.load_all()
```

---

### load_all

```python
load_all(self) -> 'None'
```

非同期で全データを一括ロード

#### 💡 使用例

```python
    >>> await db.load_all()
```

---

### arefresh

```python
arefresh(self, key: 'str' = None) -> 'None'
```

非同期でキャッシュを更新

#### 📥 引数

    - **key:**  更新するキー（Noneの場合は全キャッシュ）

#### 💡 使用例

```python
    >>> await db.refresh("user")
    >>> await db.refresh()  # 全キャッシュ更新
```

---

### refresh

```python
refresh(self, key: 'str' = None) -> 'None'
```

非同期でキャッシュを更新

#### 📥 引数

    - **key:**  更新するキー（Noneの場合は全キャッシュ）

#### 💡 使用例

```python
    >>> await db.refresh("user")
    >>> await db.refresh()  # 全キャッシュ更新
```

---

### ais_cached

```python
ais_cached(self, key: 'str') -> 'bool'
```

非同期でキーがキャッシュ済みか確認

#### 📥 引数

    - **key:**  確認するキー

#### 📤 戻り値

    キャッシュ済みの場合True

#### 💡 使用例

```python
    >>> cached = await db.is_cached("user")
```

---

### is_cached

```python
is_cached(self, key: 'str') -> 'bool'
```

非同期でキーがキャッシュ済みか確認

#### 📥 引数

    - **key:**  確認するキー

#### 📤 戻り値

    キャッシュ済みの場合True

#### 💡 使用例

```python
    >>> cached = await db.is_cached("user")
```

---

### abatch_update

```python
abatch_update(self, mapping: 'dict[str, Any]') -> 'None'
```

非同期で一括書き込み（高速）

#### 📥 引数

    - **mapping:**  書き込むキーと値のdict

#### 💡 使用例

```python
    >>> await db.batch_update({
    ...     "key1": "value1",
    ...     "key2": "value2",
    ...     "key3": {"nested": "data"}
    ... })
```

---

### batch_update

```python
batch_update(self, mapping: 'dict[str, Any]') -> 'None'
```

非同期で一括書き込み（高速）

#### 📥 引数

    - **mapping:**  書き込むキーと値のdict

#### 💡 使用例

```python
    >>> await db.batch_update({
    ...     "key1": "value1",
    ...     "key2": "value2",
    ...     "key3": {"nested": "data"}
    ... })
```

---

### abatch_delete

```python
abatch_delete(self, keys: 'list[str]') -> 'None'
```

非同期で一括削除（高速）

#### 📥 引数

    - **keys:**  削除するキーのリスト

#### 💡 使用例

```python
    >>> await db.batch_delete(["key1", "key2", "key3"])
```

---

### batch_delete

```python
batch_delete(self, keys: 'list[str]') -> 'None'
```

非同期で一括削除（高速）

#### 📥 引数

    - **keys:**  削除するキーのリスト

#### 💡 使用例

```python
    >>> await db.batch_delete(["key1", "key2", "key3"])
```

---

### ato_dict

```python
ato_dict(self) -> 'dict'
```

非同期で全データをPython dictとして取得

#### 📤 戻り値

    全データを含むdict

#### 💡 使用例

```python
    >>> data = await db.to_dict()
```

---

### to_dict

```python
to_dict(self) -> 'dict'
```

非同期で全データをPython dictとして取得

#### 📤 戻り値

    全データを含むdict

#### 💡 使用例

```python
    >>> data = await db.to_dict()
```

---

### acopy

```python
acopy(self) -> 'dict'
```

非同期で浅いコピーを作成

#### 📤 戻り値

    全データのコピー

#### 💡 使用例

```python
    >>> data_copy = await db.copy()
```

---

### copy

```python
copy(self) -> 'dict'
```

非同期で浅いコピーを作成

#### 📤 戻り値

    全データのコピー

#### 💡 使用例

```python
    >>> data_copy = await db.copy()
```

---

### aget_fresh

```python
aget_fresh(self, key: 'str', default: 'Any' = None) -> 'Any'
```

非同期でDBから直接読み込み、キャッシュを更新

#### 📥 引数

    - **key:**  取得するキー
    - **default:**  キーが存在しない場合のデフォルト値

#### 📤 戻り値

    DBから取得した最新の値

#### 💡 使用例

```python
    >>> value = await db.get_fresh("key")
```

---

### get_fresh

```python
get_fresh(self, key: 'str', default: 'Any' = None) -> 'Any'
```

非同期でDBから直接読み込み、キャッシュを更新

#### 📥 引数

    - **key:**  取得するキー
    - **default:**  キーが存在しない場合のデフォルト値

#### 📤 戻り値

    DBから取得した最新の値

#### 💡 使用例

```python
    >>> value = await db.get_fresh("key")
```

---

### abatch_get

```python
abatch_get(self, keys: 'list[str]') -> 'dict[str, Any]'
```

非同期で複数のキーを一度に取得

#### 📥 引数

    - **keys:**  取得するキーのリスト

#### 📤 戻り値

    取得に成功したキーと値の dict

#### 💡 使用例

```python
    >>> results = await db.abatch_get(["key1", "key2"])
```

---

### aset_model

```python
aset_model(self, key: 'str', model: 'Any') -> 'None'
```

非同期でPydanticモデルを保存

#### 📥 引数

    - **key:**  保存するキー
    - **model:**  Pydanticモデルのインスタンス

#### 💡 使用例

```python
    >>> from pydantic import BaseModel
    >>> class User(BaseModel):
    ...     name: str
    ...     age: int
    >>> user = User(name="Nana", age=20)
    >>> await db.set_model("user", user)
```

---

### set_model

```python
set_model(self, key: 'str', model: 'Any') -> 'None'
```

非同期でPydanticモデルを保存

#### 📥 引数

    - **key:**  保存するキー
    - **model:**  Pydanticモデルのインスタンス

#### 💡 使用例

```python
    >>> from pydantic import BaseModel
    >>> class User(BaseModel):
    ...     name: str
    ...     age: int
    >>> user = User(name="Nana", age=20)
    >>> await db.set_model("user", user)
```

---

### aget_model

```python
aget_model(self, key: 'str', model_class: 'type' = None) -> 'Any'
```

非同期でPydanticモデルを取得

#### 📥 引数

    - **key:**  取得するキー
    - **model_class:**  Pydanticモデルのクラス

#### 📤 戻り値

    Pydanticモデルのインスタンス

#### 💡 使用例

```python
    >>> user = await db.get_model("user", User)
```

---

### get_model

```python
get_model(self, key: 'str', model_class: 'type' = None) -> 'Any'
```

非同期でPydanticモデルを取得

#### 📥 引数

    - **key:**  取得するキー
    - **model_class:**  Pydanticモデルのクラス

#### 📤 戻り値

    Pydanticモデルのインスタンス

#### 💡 使用例

```python
    >>> user = await db.get_model("user", User)
```

---

### aexecute

```python
aexecute(self, sql: 'str', parameters: 'tuple | None' = None) -> 'Any'
```

非同期でSQLを直接実行

#### 📥 引数

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 戻り値

    APSWのCursorオブジェクト

#### 💡 使用例

```python
    >>> cursor = await db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
```

---

### execute

```python
execute(self, sql: 'str', parameters: 'tuple | None' = None) -> 'Any'
```

非同期でSQLを直接実行

#### 📥 引数

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 戻り値

    APSWのCursorオブジェクト

#### 💡 使用例

```python
    >>> cursor = await db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
```

---

### aexecute_many

```python
aexecute_many(self, sql: 'str', parameters_list: 'list[tuple]') -> 'None'
```

非同期でSQLを複数のパラメータで一括実行

#### 📥 引数

    - **sql:**  実行するSQL文
    - **parameters_list:**  パラメータのリスト

#### 💡 使用例

```python
    >>> await db.execute_many(
    ...     "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
    ...     [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
    ... )
```

---

### execute_many

```python
execute_many(self, sql: 'str', parameters_list: 'list[tuple]') -> 'None'
```

非同期でSQLを複数のパラメータで一括実行

#### 📥 引数

    - **sql:**  実行するSQL文
    - **parameters_list:**  パラメータのリスト

#### 💡 使用例

```python
    >>> await db.execute_many(
    ...     "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
    ...     [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
    ... )
```

---

### afetch_one

```python
afetch_one(self, sql: 'str', parameters: 'tuple' = None) -> 'tuple | None'
```

非同期でSQLを実行して1行取得

#### 📥 引数

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 戻り値

    1行の結果（tuple）

#### 💡 使用例

```python
    >>> row = await db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
```

---

### fetch_one

```python
fetch_one(self, sql: 'str', parameters: 'tuple' = None) -> 'tuple | None'
```

非同期でSQLを実行して1行取得

#### 📥 引数

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 戻り値

    1行の結果（tuple）

#### 💡 使用例

```python
    >>> row = await db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
```

---

### afetch_all

```python
afetch_all(self, sql: 'str', parameters: 'tuple' = None) -> 'list[tuple]'
```

非同期でSQLを実行して全行取得

#### 📥 引数

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 戻り値

    全行の結果（tupleのリスト）

#### 💡 使用例

```python
    >>> rows = await db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
```

---

### fetch_all

```python
fetch_all(self, sql: 'str', parameters: 'tuple' = None) -> 'list[tuple]'
```

非同期でSQLを実行して全行取得

#### 📥 引数

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 戻り値

    全行の結果（tupleのリスト）

#### 💡 使用例

```python
    >>> rows = await db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
```

---

### acreate_table

```python
acreate_table(self, table_name: 'str', columns: 'dict', if_not_exists: 'bool' = True, primary_key: 'str' = None) -> 'None'
```

非同期でテーブルを作成

#### 📥 引数

    - **table_name:**  テーブル名
    - **columns:**  カラム定義のdict
    - **if_not_exists:**  Trueの場合、存在しない場合のみ作成
    - **primary_key:**  プライマリキーのカラム名

#### 💡 使用例

```python
    >>> await db.create_table("users", {
    ...     "id": "INTEGER PRIMARY KEY",
    ...     "name": "TEXT NOT NULL",
    ...     "email": "TEXT UNIQUE"
    ... })
```

---

### create_table

```python
create_table(self, table_name: 'str', columns: 'dict', if_not_exists: 'bool' = True, primary_key: 'str' = None) -> 'None'
```

非同期でテーブルを作成

#### 📥 引数

    - **table_name:**  テーブル名
    - **columns:**  カラム定義のdict
    - **if_not_exists:**  Trueの場合、存在しない場合のみ作成
    - **primary_key:**  プライマリキーのカラム名

#### 💡 使用例

```python
    >>> await db.create_table("users", {
    ...     "id": "INTEGER PRIMARY KEY",
    ...     "name": "TEXT NOT NULL",
    ...     "email": "TEXT UNIQUE"
    ... })
```

---

### acreate_index

```python
acreate_index(self, index_name: 'str', table_name: 'str', columns: 'list[str]', unique: 'bool' = False, if_not_exists: 'bool' = True) -> 'None'
```

非同期でインデックスを作成

#### 📥 引数

    - **index_name:**  インデックス名
    - **table_name:**  テーブル名
    - **columns:**  インデックスを作成するカラムのリスト
    - **unique:**  Trueの場合、ユニークインデックスを作成
    - **if_not_exists:**  Trueの場合、存在しない場合のみ作成

#### 💡 使用例

```python
    >>> await db.create_index("idx_users_email", "users", ["email"], unique=True)
```

---

### create_index

```python
create_index(self, index_name: 'str', table_name: 'str', columns: 'list[str]', unique: 'bool' = False, if_not_exists: 'bool' = True) -> 'None'
```

非同期でインデックスを作成

#### 📥 引数

    - **index_name:**  インデックス名
    - **table_name:**  テーブル名
    - **columns:**  インデックスを作成するカラムのリスト
    - **unique:**  Trueの場合、ユニークインデックスを作成
    - **if_not_exists:**  Trueの場合、存在しない場合のみ作成

#### 💡 使用例

```python
    >>> await db.create_index("idx_users_email", "users", ["email"], unique=True)
```

---

### aquery

```python
aquery(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```

非同期でSELECTクエリを実行

#### 📥 引数

    - **table_name:**  テーブル名
    - **columns:**  取得するカラムのリスト
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ
    - **order_by:**  ORDER BY句
    - **limit:**  LIMIT句
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **allowed_sql_functions:**  このクエリで一時的に許可するSQL関数のリスト
    - **forbidden_sql_functions:**  このクエリで一時的に禁止するSQL関数のリスト
    - **override_allowed:**  Trueの場合、インスタンス許可設定を無視

#### 📤 戻り値

    結果のリスト（各行はdict）

#### 💡 使用例

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

---

### query

```python
query(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```

非同期でSELECTクエリを実行

#### 📥 引数

    - **table_name:**  テーブル名
    - **columns:**  取得するカラムのリスト
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ
    - **order_by:**  ORDER BY句
    - **limit:**  LIMIT句
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **allowed_sql_functions:**  このクエリで一時的に許可するSQL関数のリスト
    - **forbidden_sql_functions:**  このクエリで一時的に禁止するSQL関数のリスト
    - **override_allowed:**  Trueの場合、インスタンス許可設定を無視

#### 📤 戻り値

    結果のリスト（各行はdict）

#### 💡 使用例

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

---

### aquery_with_pagination

```python
aquery_with_pagination(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, offset: 'int' = None, group_by: 'str' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```

非同期で拡張されたクエリを実行

#### 📥 引数

    - **table_name:**  テーブル名
    - **columns:**  取得するカラム
    - **where:**  WHERE句
    - **parameters:**  パラメータ
    - **order_by:**  ORDER BY句
    - **limit:**  LIMIT句
    - **offset:**  OFFSET句
    - **group_by:**  GROUP BY句
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **allowed_sql_functions:**  このクエリで一時的に許可するSQL関数のリスト
    - **forbidden_sql_functions:**  このクエリで一時的に禁止するSQL関数のリスト
    - **override_allowed:**  Trueの場合、インスタンス許可設定を無視

#### 📤 戻り値

    結果のリスト（各行はdict）

#### 💡 使用例

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

---

### query_with_pagination

```python
query_with_pagination(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, offset: 'int' = None, group_by: 'str' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```

非同期で拡張されたクエリを実行

#### 📥 引数

    - **table_name:**  テーブル名
    - **columns:**  取得するカラム
    - **where:**  WHERE句
    - **parameters:**  パラメータ
    - **order_by:**  ORDER BY句
    - **limit:**  LIMIT句
    - **offset:**  OFFSET句
    - **group_by:**  GROUP BY句
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **allowed_sql_functions:**  このクエリで一時的に許可するSQL関数のリスト
    - **forbidden_sql_functions:**  このクエリで一時的に禁止するSQL関数のリスト
    - **override_allowed:**  Trueの場合、インスタンス許可設定を無視

#### 📤 戻り値

    結果のリスト（各行はdict）

#### 💡 使用例

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

---

### atable_exists

```python
atable_exists(self, table_name: 'str') -> 'bool'
```

非同期でテーブルの存在確認

#### 📥 引数

    - **table_name:**  テーブル名

#### 📤 戻り値

    存在する場合True

#### 💡 使用例

```python
    >>> exists = await db.table_exists("users")
```

---

### table_exists

```python
table_exists(self, table_name: 'str') -> 'bool'
```

非同期でテーブルの存在確認

#### 📥 引数

    - **table_name:**  テーブル名

#### 📤 戻り値

    存在する場合True

#### 💡 使用例

```python
    >>> exists = await db.table_exists("users")
```

---

### alist_tables

```python
alist_tables(self) -> 'list[str]'
```

非同期でデータベース内の全テーブル一覧を取得

#### 📤 戻り値

    テーブル名のリスト

#### 💡 使用例

```python
    >>> tables = await db.list_tables()
```

---

### list_tables

```python
list_tables(self) -> 'list[str]'
```

非同期でデータベース内の全テーブル一覧を取得

#### 📤 戻り値

    テーブル名のリスト

#### 💡 使用例

```python
    >>> tables = await db.list_tables()
```

---

### adrop_table

```python
adrop_table(self, table_name: 'str', if_exists: 'bool' = True) -> 'None'
```

非同期でテーブルを削除

#### 📥 引数

    - **table_name:**  テーブル名
    - **if_exists:**  Trueの場合、存在する場合のみ削除

#### 💡 使用例

```python
    >>> await db.drop_table("old_table")
```

---

### drop_table

```python
drop_table(self, table_name: 'str', if_exists: 'bool' = True) -> 'None'
```

非同期でテーブルを削除

#### 📥 引数

    - **table_name:**  テーブル名
    - **if_exists:**  Trueの場合、存在する場合のみ削除

#### 💡 使用例

```python
    >>> await db.drop_table("old_table")
```

---

### drop_index

```python
drop_index(self, index_name: 'str', if_exists: 'bool' = True) -> 'None'
```

非同期でインデックスを削除

#### 📥 引数

    - **index_name:**  インデックス名
    - **if_exists:**  Trueの場合、存在する場合のみ削除

#### 💡 使用例

```python
    >>> await db.drop_index("idx_users_email")
```

---

### asql_insert

```python
asql_insert(self, table_name: 'str', data: 'dict') -> 'int'
```

非同期でdictから直接INSERT

#### 📥 引数

    - **table_name:**  テーブル名
    - **data:**  カラム名と値のdict

#### 📤 戻り値

    挿入されたROWID

#### 💡 使用例

```python
    >>> rowid = await db.sql_insert("users", {
    ...     "name": "Alice",
    ...     "email": "alice@example.com",
    ...     "age": 25
    ... })
```

---

### sql_insert

```python
sql_insert(self, table_name: 'str', data: 'dict') -> 'int'
```

非同期でdictから直接INSERT

#### 📥 引数

    - **table_name:**  テーブル名
    - **data:**  カラム名と値のdict

#### 📤 戻り値

    挿入されたROWID

#### 💡 使用例

```python
    >>> rowid = await db.sql_insert("users", {
    ...     "name": "Alice",
    ...     "email": "alice@example.com",
    ...     "age": 25
    ... })
```

---

### asql_update

```python
asql_update(self, table_name: 'str', data: 'dict', where: 'str', parameters: 'tuple' = None) -> 'int'
```

非同期でdictとwhere条件でUPDATE

#### 📥 引数

    - **table_name:**  テーブル名
    - **data:**  更新するカラム名と値のdict
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ

#### 📤 戻り値

    更新された行数

#### 💡 使用例

```python
    >>> count = await db.sql_update("users",
    ...     {"age": 26, "status": "active"},
    ...     "name = ?",
    ...     ("Alice",)
    ... )
```

---

### sql_update

```python
sql_update(self, table_name: 'str', data: 'dict', where: 'str', parameters: 'tuple' = None) -> 'int'
```

非同期でdictとwhere条件でUPDATE

#### 📥 引数

    - **table_name:**  テーブル名
    - **data:**  更新するカラム名と値のdict
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ

#### 📤 戻り値

    更新された行数

#### 💡 使用例

```python
    >>> count = await db.sql_update("users",
    ...     {"age": 26, "status": "active"},
    ...     "name = ?",
    ...     ("Alice",)
    ... )
```

---

### asql_delete

```python
asql_delete(self, table_name: 'str', where: 'str', parameters: 'tuple' = None) -> 'int'
```

非同期でwhere条件でDELETE

#### 📥 引数

    - **table_name:**  テーブル名
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ

#### 📤 戻り値

    削除された行数

#### 💡 使用例

```python
    >>> count = await db.sql_delete("users", "age < ?", (18,))
```

---

### sql_delete

```python
sql_delete(self, table_name: 'str', where: 'str', parameters: 'tuple' = None) -> 'int'
```

非同期でwhere条件でDELETE

#### 📥 引数

    - **table_name:**  テーブル名
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ

#### 📤 戻り値

    削除された行数

#### 💡 使用例

```python
    >>> count = await db.sql_delete("users", "age < ?", (18,))
```

---

### acount

```python
acount(self, table_name: 'str' = None, where: 'str' = None, parameters: 'tuple' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'int'
```

非同期でレコード数を取得

#### 📥 引数

    - **table_name:**  テーブル名
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **allowed_sql_functions:**  このクエリで一時的に許可するSQL関数のリスト
    - **forbidden_sql_functions:**  このクエリで一時的に禁止するSQL関数のリスト
    - **override_allowed:**  Trueの場合、インスタンス許可設定を無視

#### 📤 戻り値

    レコード数

#### 💡 使用例

```python
    >>> count = await db.count("users", "age < ?", (18,))
```

---

### count

```python
count(self, table_name: 'str' = None, where: 'str' = None, parameters: 'tuple' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'int'
```

非同期でレコード数を取得

#### 📥 引数

    - **table_name:**  テーブル名
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **allowed_sql_functions:**  このクエリで一時的に許可するSQL関数のリスト
    - **forbidden_sql_functions:**  このクエリで一時的に禁止するSQL関数のリスト
    - **override_allowed:**  Trueの場合、インスタンス許可設定を無視

#### 📤 戻り値

    レコード数

#### 💡 使用例

```python
    >>> count = await db.count("users", "age < ?", (18,))
```

---

### avacuum

```python
avacuum(self) -> 'None'
```

非同期でデータベースを最適化（VACUUM実行）

#### 💡 使用例

```python
    >>> await db.vacuum()
```

---

### vacuum

```python
vacuum(self) -> 'None'
```

非同期でデータベースを最適化（VACUUM実行）

#### 💡 使用例

```python
    >>> await db.vacuum()
```

---

### begin_transaction

```python
begin_transaction(self) -> 'None'
```

非同期でトランザクションを開始

#### 💡 使用例

```python
    >>> await db.begin_transaction()
    >>> try:
    ...     await db.sql_insert("users", {"name": "Alice"})
    ...     await db.sql_insert("users", {"name": "Bob"})
    ...     await db.commit()
    ... except:
    ...     await db.rollback()
```

---

### commit

```python
commit(self) -> 'None'
```

非同期でトランザクションをコミット

#### 💡 使用例

```python
    >>> await db.commit()
```

---

### rollback

```python
rollback(self) -> 'None'
```

非同期でトランザクションをロールバック

#### 💡 使用例

```python
    >>> await db.rollback()
```

---

### in_transaction

```python
in_transaction(self) -> 'bool'
```

非同期でトランザクション状態を確認

#### 📤 戻り値

    - **bool:**  トランザクション中の場合True

#### 💡 使用例

```python
    >>> status = await db.in_transaction()
    >>> print(f"In transaction: {status}")
```

---

### transaction

```python
transaction(self)
```

非同期トランザクションのコンテキストマネージャ

#### 💡 使用例

```python
    >>> async with db.transaction():
    ...     await db.sql_insert("users", {"name": "Alice"})
    ...     await db.sql_insert("users", {"name": "Bob"})
    ...     # 自動的にコミット、例外時はロールバック
```

---

### close

```python
close(self) -> 'None'
```

非同期でデータベース接続を閉じる

スレッドプールエグゼキューターもシャットダウンします。

#### 💡 使用例

```python
    >>> await db.close()
```

---

### atable

```python
atable(self, table_name: 'str') -> 'AsyncNanaSQLite'
```

非同期でサブテーブルのAsyncNanaSQLiteインスタンスを取得

既に初期化済みの親インスタンスから呼ばれることを想定しています。
接続とエグゼキューターは親インスタンスと共有されます。

⚠️ 重要な注意事項:
- 同じテーブルに対して複数のインスタンスを作成しないでください
  各インスタンスは独立したキャッシュを持つため、キャッシュ不整合が発生します
- 推奨: テーブルインスタンスを変数に保存して再利用してください

- **非推奨:** 
    "users"
    sub2 = await db.table("users")  # キャッシュ不整合の原因

- **推奨:** 
    "users"
    # users_dbを使い回す

#### 📥 引数

    - **table_name:**  取得するサブテーブル名

#### 📤 戻り値

    指定したテーブルを操作するAsyncNanaSQLiteインスタンス

#### 💡 使用例

```python
    >>> async with AsyncNanaSQLite("mydata.db", table="main") as db:
    ...     users_db = await db.table("users")
    ...     products_db = await db.table("products")
    ...     await users_db.aset("user1", {"name": "Alice"})
    ...     await products_db.aset("prod1", {"name": "Laptop"})
```

---

### table

```python
table(self, table_name: 'str') -> 'AsyncNanaSQLite'
```

非同期でサブテーブルのAsyncNanaSQLiteインスタンスを取得

既に初期化済みの親インスタンスから呼ばれることを想定しています。
接続とエグゼキューターは親インスタンスと共有されます。

⚠️ 重要な注意事項:
- 同じテーブルに対して複数のインスタンスを作成しないでください
  各インスタンスは独立したキャッシュを持つため、キャッシュ不整合が発生します
- 推奨: テーブルインスタンスを変数に保存して再利用してください

- **非推奨:** 
    "users"
    sub2 = await db.table("users")  # キャッシュ不整合の原因

- **推奨:** 
    "users"
    # users_dbを使い回す

#### 📥 引数

    - **table_name:**  取得するサブテーブル名

#### 📤 戻り値

    指定したテーブルを操作するAsyncNanaSQLiteインスタンス

#### 💡 使用例

```python
    >>> async with AsyncNanaSQLite("mydata.db", table="main") as db:
    ...     users_db = await db.table("users")
    ...     products_db = await db.table("products")
    ...     await users_db.aset("user1", {"name": "Alice"})
    ...     await products_db.aset("prod1", {"name": "Laptop"})
```

---

