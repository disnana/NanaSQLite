# Asynchronous API Reference

Reference for the asynchronous AsyncNanaSQLite class.

## AsyncNanaSQLite

Async wrapper for NanaSQLite with optimized thread pool executor.

All database operations are executed in a dedicated thread pool executor to prevent
blocking the async event loop. This allows NanaSQLite to be used safely
in async applications like FastAPI, aiohttp, etc.

The implementation uses a configurable thread pool for optimal concurrency
and performance in high-load scenarios.

#### 📥 Arguments

    - **db_path:**  SQLiteデータベースファイルのパス
    - **table:**  使用するテーブル名
    - **bulk_load:**  Trueの場合、初期化時に全データをメモリに読み込む
    - **optimize:**  Trueの場合、WALモードなど高速化設定を適用
    - **cache_size_mb:**  SQLiteキャッシュサイズ（MB）、デフォルト64MB
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **max_clause_length:**  SQL句の最大長（ReDoS対策、v1.2.0）
    - **max_workers:**  スレッドプール内の最大ワーカー数（デフォルト: 5）
    - **thread_name_prefix:**  スレッド名のプレフィックス（デフォルト: "AsyncNanaSQLite"）

#### 💡 Example

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

## Methods

### __init__

```python
__init__(self, db_path: 'str', table: 'str' = 'data', bulk_load: 'bool' = False, optimize: 'bool' = True, cache_size_mb: 'int' = 64, max_workers: 'int' = 5, thread_name_prefix: 'str' = 'AsyncNanaSQLite', strict_sql_validation: 'bool' = True, allowed_sql_functions: 'list[str] | None' = None, forbidden_sql_functions: 'list[str] | None' = None, max_clause_length: 'int | None' = 1000, read_pool_size: 'int' = 0)
```


#### 📥 Arguments

    - **db_path:**  SQLiteデータベースファイルのパス
    - **table:**  使用するテーブル名
    - **bulk_load:**  Trueの場合、初期化時に全データをメモリに読み込む
    - **optimize:**  Trueの場合、WALモードなど高速化設定を適用
    - **cache_size_mb:**  SQLiteキャッシュサイズ（MB）、デフォルト64MB
    - **max_workers:**  スレッドプール内の最大ワーカー数（デフォルト: 5）
    - **thread_name_prefix:**  スレッド名のプレフィックス（デフォルト: "AsyncNanaSQLite"）
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **allowed_sql_functions:**  追加で許可するSQL関数のリスト
    - **forbidden_sql_functions:**  明示的に禁止するSQL関数のリスト
    - **max_clause_length:**  SQL句の最大長（ReDoS対策）。Noneで制限なし
    - **read_pool_size:**  読み取り専用プールサイズ

---

### aget

```python
aget(self, key: 'str', default: 'Any' = None) -> 'Any'
```


#### 📥 Arguments

    - **key:**  取得するキー
    - **default:**  キーが存在しない場合のデフォルト値

#### 📤 Returns

#### 💡 Example

```python
    >>> user = await db.aget("user")
    >>> config = await db.aget("config", {})
```

---

### get

```python
get(self, key: 'str', default: 'Any' = None) -> 'Any'
```


#### 📥 Arguments

    - **key:**  取得するキー
    - **default:**  キーが存在しない場合のデフォルト値

#### 📤 Returns

#### 💡 Example

```python
    >>> user = await db.aget("user")
    >>> config = await db.aget("config", {})
```

---

### aset

```python
aset(self, key: 'str', value: 'Any') -> 'None'
```


#### 📥 Arguments

    - **key:**  設定するキー
    - **value:**  設定する値

#### 💡 Example

```python
    >>> await db.aset("user", {"name": "Nana", "age": 20})
```

---

### adelete

```python
adelete(self, key: 'str') -> 'None'
```


#### 📥 Arguments

    - **key:**  削除するキー

#### ⚠️ Raises

    - **KeyError:**  キーが存在しない場合

#### 💡 Example

```python
    >>> await db.adelete("old_data")
```

---

### acontains

```python
acontains(self, key: 'str') -> 'bool'
```


#### 📥 Arguments

    - **key:**  確認するキー

#### 📤 Returns

#### 💡 Example

```python
    >>> if await db.acontains("user"):
    ...     print("User exists")
```

---

### contains

```python
contains(self, key: 'str') -> 'bool'
```


#### 📥 Arguments

    - **key:**  確認するキー

#### 📤 Returns

#### 💡 Example

```python
    >>> if await db.acontains("user"):
    ...     print("User exists")
```

---

### alen

```python
alen(self) -> 'int'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> count = await db.alen()
```

---

### akeys

```python
akeys(self) -> 'list[str]'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> keys = await db.akeys()
```

---

### keys

```python
keys(self) -> 'list[str]'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> keys = await db.akeys()
```

---

### avalues

```python
avalues(self) -> 'list[Any]'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> values = await db.avalues()
```

---

### values

```python
values(self) -> 'list[Any]'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> values = await db.avalues()
```

---

### aitems

```python
aitems(self) -> 'list[tuple[str, Any]]'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> items = await db.aitems()
```

---

### items

```python
items(self) -> 'list[tuple[str, Any]]'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> items = await db.aitems()
```

---

### apop

```python
apop(self, key: 'str', *args) -> 'Any'
```


#### 📥 Arguments

    - **key:**  削除するキー
    *args: デフォルト値（オプション）

#### 📤 Returns

#### 💡 Example

```python
    >>> value = await db.apop("temp_data")
    >>> value = await db.apop("maybe_missing", "default")
```

---

### aupdate

```python
aupdate(self, mapping: 'dict' = None, **kwargs) -> 'None'
```


#### 📥 Arguments

    - **mapping:**  更新するキーと値のdict

#### 💡 Example

```python
    >>> await db.aupdate({"key1": "value1", "key2": "value2"})
    >>> await db.aupdate(key3="value3", key4="value4")
```

---

### aclear

```python
aclear(self) -> 'None'
```


#### 💡 Example

```python
    >>> await db.aclear()
```

---

### asetdefault

```python
asetdefault(self, key: 'str', default: 'Any' = None) -> 'Any'
```


#### 📥 Arguments

    - **key:**  キー
    - **default:**  デフォルト値

#### 📤 Returns

#### 💡 Example

```python
    >>> value = await db.asetdefault("config", {})
```

---

### aload_all

```python
aload_all(self) -> 'None'
```


#### 💡 Example

```python
    >>> await db.load_all()
```

---

### load_all

```python
load_all(self) -> 'None'
```


#### 💡 Example

```python
    >>> await db.load_all()
```

---

### arefresh

```python
arefresh(self, key: 'str' = None) -> 'None'
```


#### 📥 Arguments

    - **key:**  更新するキー（Noneの場合は全キャッシュ）

#### 💡 Example

```python
    >>> await db.refresh("user")
    >>> await db.refresh()  # 全キャッシュ更新
```

---

### refresh

```python
refresh(self, key: 'str' = None) -> 'None'
```


#### 📥 Arguments

    - **key:**  更新するキー（Noneの場合は全キャッシュ）

#### 💡 Example

```python
    >>> await db.refresh("user")
    >>> await db.refresh()  # 全キャッシュ更新
```

---

### ais_cached

```python
ais_cached(self, key: 'str') -> 'bool'
```


#### 📥 Arguments

    - **key:**  確認するキー

#### 📤 Returns

#### 💡 Example

```python
    >>> cached = await db.is_cached("user")
```

---

### is_cached

```python
is_cached(self, key: 'str') -> 'bool'
```


#### 📥 Arguments

    - **key:**  確認するキー

#### 📤 Returns

#### 💡 Example

```python
    >>> cached = await db.is_cached("user")
```

---

### abatch_update

```python
abatch_update(self, mapping: 'dict[str, Any]') -> 'None'
```


#### 📥 Arguments

    - **mapping:**  書き込むキーと値のdict

#### 💡 Example

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


#### 📥 Arguments

    - **mapping:**  書き込むキーと値のdict

#### 💡 Example

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


#### 📥 Arguments

    - **keys:**  削除するキーのリスト

#### 💡 Example

```python
    >>> await db.batch_delete(["key1", "key2", "key3"])
```

---

### batch_delete

```python
batch_delete(self, keys: 'list[str]') -> 'None'
```


#### 📥 Arguments

    - **keys:**  削除するキーのリスト

#### 💡 Example

```python
    >>> await db.batch_delete(["key1", "key2", "key3"])
```

---

### ato_dict

```python
ato_dict(self) -> 'dict'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> data = await db.to_dict()
```

---

### to_dict

```python
to_dict(self) -> 'dict'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> data = await db.to_dict()
```

---

### acopy

```python
acopy(self) -> 'dict'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> data_copy = await db.copy()
```

---

### copy

```python
copy(self) -> 'dict'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> data_copy = await db.copy()
```

---

### aget_fresh

```python
aget_fresh(self, key: 'str', default: 'Any' = None) -> 'Any'
```


#### 📥 Arguments

    - **key:**  取得するキー
    - **default:**  キーが存在しない場合のデフォルト値

#### 📤 Returns

#### 💡 Example

```python
    >>> value = await db.get_fresh("key")
```

---

### get_fresh

```python
get_fresh(self, key: 'str', default: 'Any' = None) -> 'Any'
```


#### 📥 Arguments

    - **key:**  取得するキー
    - **default:**  キーが存在しない場合のデフォルト値

#### 📤 Returns

#### 💡 Example

```python
    >>> value = await db.get_fresh("key")
```

---

### abatch_get

```python
abatch_get(self, keys: 'list[str]') -> 'dict[str, Any]'
```


#### 📥 Arguments

    - **keys:**  取得するキーのリスト

#### 📤 Returns

#### 💡 Example

```python
    >>> results = await db.abatch_get(["key1", "key2"])
```

---

### aset_model

```python
aset_model(self, key: 'str', model: 'Any') -> 'None'
```


#### 📥 Arguments

    - **key:**  保存するキー
    - **model:**  Pydanticモデルのインスタンス

#### 💡 Example

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


#### 📥 Arguments

    - **key:**  保存するキー
    - **model:**  Pydanticモデルのインスタンス

#### 💡 Example

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


#### 📥 Arguments

    - **key:**  取得するキー
    - **model_class:**  Pydanticモデルのクラス

#### 📤 Returns

#### 💡 Example

```python
    >>> user = await db.get_model("user", User)
```

---

### get_model

```python
get_model(self, key: 'str', model_class: 'type' = None) -> 'Any'
```


#### 📥 Arguments

    - **key:**  取得するキー
    - **model_class:**  Pydanticモデルのクラス

#### 📤 Returns

#### 💡 Example

```python
    >>> user = await db.get_model("user", User)
```

---

### aexecute

```python
aexecute(self, sql: 'str', parameters: 'tuple | None' = None) -> 'Any'
```


#### 📥 Arguments

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 Returns

#### 💡 Example

```python
    >>> cursor = await db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
```

---

### execute

```python
execute(self, sql: 'str', parameters: 'tuple | None' = None) -> 'Any'
```


#### 📥 Arguments

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 Returns

#### 💡 Example

```python
    >>> cursor = await db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
```

---

### aexecute_many

```python
aexecute_many(self, sql: 'str', parameters_list: 'list[tuple]') -> 'None'
```


#### 📥 Arguments

    - **sql:**  実行するSQL文
    - **parameters_list:**  パラメータのリスト

#### 💡 Example

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


#### 📥 Arguments

    - **sql:**  実行するSQL文
    - **parameters_list:**  パラメータのリスト

#### 💡 Example

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


#### 📥 Arguments

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 Returns

#### 💡 Example

```python
    >>> row = await db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
```

---

### fetch_one

```python
fetch_one(self, sql: 'str', parameters: 'tuple' = None) -> 'tuple | None'
```


#### 📥 Arguments

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 Returns

#### 💡 Example

```python
    >>> row = await db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
```

---

### afetch_all

```python
afetch_all(self, sql: 'str', parameters: 'tuple' = None) -> 'list[tuple]'
```


#### 📥 Arguments

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 Returns

#### 💡 Example

```python
    >>> rows = await db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
```

---

### fetch_all

```python
fetch_all(self, sql: 'str', parameters: 'tuple' = None) -> 'list[tuple]'
```


#### 📥 Arguments

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 Returns

#### 💡 Example

```python
    >>> rows = await db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
```

---

### acreate_table

```python
acreate_table(self, table_name: 'str', columns: 'dict', if_not_exists: 'bool' = True, primary_key: 'str' = None) -> 'None'
```


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **columns:**  カラム定義のdict
    - **if_not_exists:**  Trueの場合、存在しない場合のみ作成
    - **primary_key:**  プライマリキーのカラム名

#### 💡 Example

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


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **columns:**  カラム定義のdict
    - **if_not_exists:**  Trueの場合、存在しない場合のみ作成
    - **primary_key:**  プライマリキーのカラム名

#### 💡 Example

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


#### 📥 Arguments

    - **index_name:**  インデックス名
    - **table_name:**  テーブル名
    - **columns:**  インデックスを作成するカラムのリスト
    - **unique:**  Trueの場合、ユニークインデックスを作成
    - **if_not_exists:**  Trueの場合、存在しない場合のみ作成

#### 💡 Example

```python
    >>> await db.create_index("idx_users_email", "users", ["email"], unique=True)
```

---

### create_index

```python
create_index(self, index_name: 'str', table_name: 'str', columns: 'list[str]', unique: 'bool' = False, if_not_exists: 'bool' = True) -> 'None'
```


#### 📥 Arguments

    - **index_name:**  インデックス名
    - **table_name:**  テーブル名
    - **columns:**  インデックスを作成するカラムのリスト
    - **unique:**  Trueの場合、ユニークインデックスを作成
    - **if_not_exists:**  Trueの場合、存在しない場合のみ作成

#### 💡 Example

```python
    >>> await db.create_index("idx_users_email", "users", ["email"], unique=True)
```

---

### aquery

```python
aquery(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```


#### 📥 Arguments

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

#### 📤 Returns

#### 💡 Example

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


#### 📥 Arguments

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

#### 📤 Returns

#### 💡 Example

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


#### 📥 Arguments

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

#### 📤 Returns

#### 💡 Example

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


#### 📥 Arguments

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

#### 📤 Returns

#### 💡 Example

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


#### 📥 Arguments

    - **table_name:**  テーブル名

#### 📤 Returns

#### 💡 Example

```python
    >>> exists = await db.table_exists("users")
```

---

### table_exists

```python
table_exists(self, table_name: 'str') -> 'bool'
```


#### 📥 Arguments

    - **table_name:**  テーブル名

#### 📤 Returns

#### 💡 Example

```python
    >>> exists = await db.table_exists("users")
```

---

### alist_tables

```python
alist_tables(self) -> 'list[str]'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> tables = await db.list_tables()
```

---

### list_tables

```python
list_tables(self) -> 'list[str]'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> tables = await db.list_tables()
```

---

### adrop_table

```python
adrop_table(self, table_name: 'str', if_exists: 'bool' = True) -> 'None'
```


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **if_exists:**  Trueの場合、存在する場合のみ削除

#### 💡 Example

```python
    >>> await db.drop_table("old_table")
```

---

### drop_table

```python
drop_table(self, table_name: 'str', if_exists: 'bool' = True) -> 'None'
```


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **if_exists:**  Trueの場合、存在する場合のみ削除

#### 💡 Example

```python
    >>> await db.drop_table("old_table")
```

---

### drop_index

```python
drop_index(self, index_name: 'str', if_exists: 'bool' = True) -> 'None'
```


#### 📥 Arguments

    - **index_name:**  インデックス名
    - **if_exists:**  Trueの場合、存在する場合のみ削除

#### 💡 Example

```python
    >>> await db.drop_index("idx_users_email")
```

---

### asql_insert

```python
asql_insert(self, table_name: 'str', data: 'dict') -> 'int'
```


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **data:**  カラム名と値のdict

#### 📤 Returns

#### 💡 Example

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


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **data:**  カラム名と値のdict

#### 📤 Returns

#### 💡 Example

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


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **data:**  更新するカラム名と値のdict
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ

#### 📤 Returns

#### 💡 Example

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


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **data:**  更新するカラム名と値のdict
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ

#### 📤 Returns

#### 💡 Example

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


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ

#### 📤 Returns

#### 💡 Example

```python
    >>> count = await db.sql_delete("users", "age < ?", (18,))
```

---

### sql_delete

```python
sql_delete(self, table_name: 'str', where: 'str', parameters: 'tuple' = None) -> 'int'
```


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ

#### 📤 Returns

#### 💡 Example

```python
    >>> count = await db.sql_delete("users", "age < ?", (18,))
```

---

### acount

```python
acount(self, table_name: 'str' = None, where: 'str' = None, parameters: 'tuple' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'int'
```


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **allowed_sql_functions:**  このクエリで一時的に許可するSQL関数のリスト
    - **forbidden_sql_functions:**  このクエリで一時的に禁止するSQL関数のリスト
    - **override_allowed:**  Trueの場合、インスタンス許可設定を無視

#### 📤 Returns

#### 💡 Example

```python
    >>> count = await db.count("users", "age < ?", (18,))
```

---

### count

```python
count(self, table_name: 'str' = None, where: 'str' = None, parameters: 'tuple' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'int'
```


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **allowed_sql_functions:**  このクエリで一時的に許可するSQL関数のリスト
    - **forbidden_sql_functions:**  このクエリで一時的に禁止するSQL関数のリスト
    - **override_allowed:**  Trueの場合、インスタンス許可設定を無視

#### 📤 Returns

#### 💡 Example

```python
    >>> count = await db.count("users", "age < ?", (18,))
```

---

### avacuum

```python
avacuum(self) -> 'None'
```


#### 💡 Example

```python
    >>> await db.vacuum()
```

---

### vacuum

```python
vacuum(self) -> 'None'
```


#### 💡 Example

```python
    >>> await db.vacuum()
```

---

### begin_transaction

```python
begin_transaction(self) -> 'None'
```


#### 💡 Example

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


#### 💡 Example

```python
    >>> await db.commit()
```

---

### rollback

```python
rollback(self) -> 'None'
```


#### 💡 Example

```python
    >>> await db.rollback()
```

---

### in_transaction

```python
in_transaction(self) -> 'bool'
```


#### 📤 Returns

    - **bool:**  トランザクション中の場合True

#### 💡 Example

```python
    >>> status = await db.in_transaction()
    >>> print(f"In transaction: {status}")
```

---

### transaction

```python
transaction(self)
```


#### 💡 Example

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


#### 💡 Example

```python
    >>> await db.close()
```

---

### atable

```python
atable(self, table_name: 'str') -> 'AsyncNanaSQLite'
```

- 推奨: テーブルインスタンスを変数に保存して再利用してください

- **非推奨:** 
    sub1 = await db.table

- **推奨:** 
    users_db = await db.table

#### 📥 Arguments

    - **table_name:**  取得するサブテーブル名

#### 📤 Returns

#### 💡 Example

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

- 推奨: テーブルインスタンスを変数に保存して再利用してください

- **非推奨:** 
    sub1 = await db.table

- **推奨:** 
    users_db = await db.table

#### 📥 Arguments

    - **table_name:**  取得するサブテーブル名

#### 📤 Returns

#### 💡 Example

```python
    >>> async with AsyncNanaSQLite("mydata.db", table="main") as db:
    ...     users_db = await db.table("users")
    ...     products_db = await db.table("products")
    ...     await users_db.aset("user1", {"name": "Alice"})
    ...     await products_db.aset("prod1", {"name": "Laptop"})
```

---

