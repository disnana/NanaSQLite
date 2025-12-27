# Synchronous API Reference

Reference for the synchronous NanaSQLite class.

## NanaSQLite

APSW SQLite-backed dict wrapper with Security and Connection Enhancements (v1.2.0).

Internally maintains a Python dict and synchronizes with SQLite during operations.
In v1.2.0, enhanced dynamic SQL validation, ReDoS protection, and strict connection management are introduced.

#### 📥 Arguments

    - **db_path:**  SQLiteデータベースファイルのパス
    - **table:**  使用するテーブル名
    - **bulk_load:**  Trueの場合、初期化時に全データをメモリに読み込む
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **max_clause_length:**  SQL句の最大長（ReDoS対策、v1.2.0）

---

## Methods

### __init__

```python
__init__(self, db_path: 'str', table: 'str' = 'data', bulk_load: 'bool' = False, optimize: 'bool' = True, cache_size_mb: 'int' = 64, strict_sql_validation: 'bool' = True, allowed_sql_functions: 'list[str] | None' = None, forbidden_sql_functions: 'list[str] | None' = None, max_clause_length: 'int | None' = 1000, _shared_connection: 'apsw.Connection | None' = None, _shared_lock: 'threading.RLock | None' = None)
```


#### 📥 Arguments

    - **db_path:**  SQLiteデータベースファイルのパス
    - **table:**  使用するテーブル名
    - **bulk_load:**  Trueの場合、初期化時に全データをメモリに読み込む
    - **optimize:**  Trueの場合、WALモードなど高速化設定を適用
    - **cache_size_mb:**  SQLiteキャッシュサイズ（MB）、デフォルト64MB
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **allowed_sql_functions:**  追加で許可するSQL関数のリスト
    - **forbidden_sql_functions:**  明示的に禁止するSQL関数のリスト
    - **max_clause_length:**  SQL句の最大長（ReDoS対策）。Noneで制限なし
    - **_shared_connection:**  内部用：共有する接続（table()メソッドで使用）
    - **_shared_lock:**  内部用：共有するロック（table()メソッドで使用）

---

### keys

```python
keys(self) -> 'list'
```

---

### values

```python
values(self) -> 'list'
```

---

### items

```python
items(self) -> 'list'
```

---

### get

```python
get(self, key: 'str', default: 'Any' = None) -> 'Any'
```

dict.get

---

### get_fresh

```python
get_fresh(self, key: 'str', default: 'Any' = None) -> 'Any'
```

`execute()`でDBを直接変更した後などに使用。

通常の`get()`よりオーバーヘッドがあるため、

#### 📥 Arguments

    - **key:**  取得するキー
    - **default:**  キーが存在しない場合のデフォルト値

#### 📤 Returns

#### 💡 Example

```python
    >>> db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new"', "key"))
    >>> value = db.get_fresh("key")  # DBから最新値を取得
```

---

### batch_get

```python
batch_get(self, keys: 'list[str]') -> 'dict[str, Any]'
```

1回の `SELECT IN (...)` クエリで複数のキーをDBから取得する。

#### 📥 Arguments

    - **keys:**  取得するキーのリスト

#### 📤 Returns

#### 💡 Example

```python
    >>> results = db.batch_get(["user1", "user2", "user3"])
    >>> print(results)  # {"user1": {...}, "user2": {...}}
```

---

### pop

```python
pop(self, key: 'str', *args) -> 'Any'
```

dict.pop

---

### update

```python
update(self, mapping: 'dict' = None, **kwargs) -> 'None'
```

---

### clear

```python
clear(self) -> 'None'
```

---

### setdefault

```python
setdefault(self, key: 'str', default: 'Any' = None) -> 'Any'
```

dict.setdefault

---

### load_all

```python
load_all(self) -> 'None'
```

- **一括読み込み:**  全データをメモリに展開

---

### refresh

```python
refresh(self, key: 'str' = None) -> 'None'
```


#### 📥 Arguments

    - **key:**  特定のキーのみ更新。Noneの場合は全キャッシュをクリアして再読み込み

---

### is_cached

```python
is_cached(self, key: 'str') -> 'bool'
```

---

### batch_update

```python
batch_update(self, mapping: 'dict[str, Any]') -> 'None'
```


#### 📥 Arguments

    - **mapping:**  書き込むキーと値のdict

#### 📤 Returns

    None

#### 💡 Example

```python
    >>> db.batch_update({"key1": "value1", "key2": "value2", ...})
```

---

### batch_delete

```python
batch_delete(self, keys: 'list[str]') -> 'None'
```


#### 📥 Arguments

    - **keys:**  削除するキーのリスト

#### 📤 Returns

    None

---

### to_dict

```python
to_dict(self) -> 'dict'
```

---

### copy

```python
copy(self) -> 'dict'
```

---

### close

```python
close(self) -> 'None'
```

- **注意:**  table()メソッドで作成されたインスタンスは接続を共有しているため、

#### ⚠️ Raises

    - **NanaSQLiteTransactionError:**  トランザクション中にクローズを試みた場合

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
    >>> db.set_model("user", user)
```

---

### get_model

```python
get_model(self, key: 'str', model_class: 'type' = None) -> 'Any'
```


#### 📥 Arguments

    - **key:**  取得するキー
    - **model_class:**  Pydanticモデルのクラス（Noneの場合は自動検出を試みる）

#### 📤 Returns

#### 💡 Example

```python
    >>> user = db.get_model("user", User)
    >>> print(user.name)  # "Nana"
```

---

### execute

```python
execute(self, sql: 'str', parameters: 'tuple | None' = None) -> 'apsw.Cursor'
```

.. warning::
    キャッシュを更新するには `refresh()` を呼び出してください。

#### 📥 Arguments

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ（?プレースホルダー用）

#### 📤 Returns

#### ⚠️ Raises

    - **NanaSQLiteConnectionError:**  接続が閉じられている場合
    - **NanaSQLiteDatabaseError:**  SQL実行エラー

#### 💡 Example

```python
    >>> cursor = db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
    >>> for row in cursor:
    ...     print(row)
```

```python
    >>> db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new"', "key"))
    >>> db.refresh("key")  # キャッシュを更新
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
    >>> db.execute_many(
    ...     "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
    ...     [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
    ... )
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
    >>> row = db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
    >>> print(row[0])
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
    >>> rows = db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
    >>> for key, value in rows:
    ...     print(key, value)
```

---

### create_table

```python
create_table(self, table_name: 'str', columns: 'dict', if_not_exists: 'bool' = True, primary_key: 'str' = None) -> 'None'
```


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **columns:**  カラム定義のdict（カラム名: SQL型）
    - **if_not_exists:**  Trueの場合、存在しない場合のみ作成
    - **primary_key:**  プライマリキーのカラム名（Noneの場合は指定なし）

#### 💡 Example

```python
    >>> db.create_table("users", {
    ...     "id": "INTEGER PRIMARY KEY",
    ...     "name": "TEXT NOT NULL",
    ...     "email": "TEXT UNIQUE",
    ...     "age": "INTEGER"
    ... })
    >>> db.create_table("posts", {
    ...     "id": "INTEGER",
    ...     "title": "TEXT",
    ...     "content": "TEXT"
    ... }, primary_key="id")
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
    >>> db.create_index("idx_users_email", "users", ["email"], unique=True)
    >>> db.create_index("idx_posts_user", "posts", ["user_id", "created_at"])
```

---

### query

```python
query(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```


#### 📥 Arguments

    - **table_name:**  テーブル名（Noneの場合はデフォルトテーブル）
    - **columns:**  取得するカラムのリスト（Noneの場合は全カラム）
    - **where:**  WHERE句の条件（パラメータバインディング使用推奨）
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
    >>> # デフォルトテーブルから全データ取得
    >>> results = db.query()
```

```python
    >>> # 条件付き検索
    >>> results = db.query(
    ...     table_name="users",
    ...     columns=["id", "name", "email"],
    ...     where="age > ?",
    ...     parameters=(20,),
    ...     order_by="name ASC",
    ...     limit=10
    ... )
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
    >>> if db.table_exists("users"):
    ...     print("users table exists")
```

---

### list_tables

```python
list_tables(self) -> 'list[str]'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> tables = db.list_tables()
    >>> print(tables)  # ['data', 'users', 'posts']
```

---

### drop_table

```python
drop_table(self, table_name: 'str', if_exists: 'bool' = True) -> 'None'
```


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **if_exists:**  Trueの場合、存在する場合のみ削除（エラーを防ぐ）

#### 💡 Example

```python
    >>> db.drop_table("old_table")
    >>> db.drop_table("temp", if_exists=True)
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
    >>> db.drop_index("idx_users_email")
```

---

### alter_table_add_column

```python
alter_table_add_column(self, table_name: 'str', column_name: 'str', column_type: 'str', default: 'Any' = None) -> 'None'
```


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **column_name:**  カラム名
    - **column_type:**  カラムの型（SQL型）
    - **default:**  デフォルト値（Noneの場合は指定なし）

#### 💡 Example

```python
    >>> db.alter_table_add_column("users", "phone", "TEXT")
    >>> db.alter_table_add_column("users", "status", "TEXT", default="'active'")
```

---

### get_table_schema

```python
get_table_schema(self, table_name: 'str') -> 'list[dict]'
```


#### 📥 Arguments

    - **table_name:**  テーブル名

#### 📤 Returns

#### 💡 Example

```python
    >>> schema = db.get_table_schema("users")
    >>> for col in schema:
    ...     print(f"{col['name']}: {col['type']}")
```

---

### list_indexes

```python
list_indexes(self, table_name: 'str' = None) -> 'list[dict]'
```


#### 📥 Arguments

    - **table_name:**  テーブル名（Noneの場合は全インデックス）

#### 📤 Returns

#### 💡 Example

```python
    >>> indexes = db.list_indexes("users")
    >>> for idx in indexes:
    ...     print(f"{idx['name']}: {idx['columns']}")
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
    >>> rowid = db.sql_insert("users", {
    ...     "name": "Alice",
    ...     "email": "alice@example.com",
    ...     "age": 25
    ... })
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
    >>> count = db.sql_update("users",
    ...     {"age": 26, "status": "active"},
    ...     "name = ?",
    ...     ("Alice",)
    ... )
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
    >>> count = db.sql_delete("users", "age < ?", (18,))
```

---

### upsert

```python
upsert(self, table_name: 'str', data: 'dict', conflict_columns: 'list[str]' = None) -> 'int'
```


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **data:**  カラム名と値のdict
    - **conflict_columns:**  競合判定に使用するカラム（Noneの場合はINSERT OR REPLACE）

#### 📤 Returns

#### 💡 Example

```python
    >>> # 単純なINSERT OR REPLACE
    >>> db.upsert("users", {"id": 1, "name": "Alice", "age": 25})
```

```python
    >>> # ON CONFLICT句を使用
    >>> db.upsert("users",
    ...     {"email": "alice@example.com", "name": "Alice", "age": 26},
    ...     conflict_columns=["email"]
    ... )
```

---

### count

```python
count(self, table_name: 'str' = None, where: 'str' = None, parameters: 'tuple' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'int'
```


#### 📥 Arguments

    - **table_name:**  テーブル名（Noneの場合はデフォルトテーブル）
    - **where:**  WHERE句の条件（オプション）
    - **parameters:**  WHERE句のパラメータ
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **allowed_sql_functions:**  このクエリで一時的に許可するSQL関数のリスト
    - **forbidden_sql_functions:**  このクエリで一時的に禁止するSQL関数のリスト
    - **override_allowed:**  Trueの場合、インスタンス許可設定を無視

#### 💡 Example

```python
    >>> total = db.count("users")
    >>> adults = db.count("users", "age >= ?", (18,))
```

---

### exists

```python
exists(self, table_name: 'str', where: 'str', parameters: 'tuple' = None) -> 'bool'
```


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ

#### 📤 Returns

#### 💡 Example

```python
    >>> if db.exists("users", "email = ?", ("alice@example.com",)):
    ...     print("User exists")
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
    - **offset:**  OFFSET句（ページネーション用）
    - **group_by:**  GROUP BY句
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **allowed_sql_functions:**  このクエリで一時的に許可するSQL関数のリスト
    - **forbidden_sql_functions:**  このクエリで一時的に禁止するSQL関数のリスト
    - **override_allowed:**  Trueの場合、インスタンス許可設定を無視

#### 📤 Returns

#### 💡 Example

```python
    >>> # ページネーション
    >>> page2 = db.query_with_pagination("users",
    ...     limit=10, offset=10, order_by="id ASC")
```

```python
    >>> # グループ集計
    >>> stats = db.query_with_pagination("orders",
    ...     columns=["user_id", "COUNT(*) as order_count"],
    ...     group_by="user_id"
    ... )
```

---

### vacuum

```python
vacuum(self) -> 'None'
```


#### 💡 Example

```python
    >>> db.vacuum()
```

---

### get_db_size

```python
get_db_size(self) -> 'int'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> size = db.get_db_size()
    >>> print(f"DB size: {size / 1024 / 1024:.2f} MB")
```

---

### export_table_to_dict

```python
export_table_to_dict(self, table_name: 'str') -> 'list[dict]'
```


#### 📥 Arguments

    - **table_name:**  テーブル名

#### 📤 Returns

#### 💡 Example

```python
    >>> all_users = db.export_table_to_dict("users")
```

---

### import_from_dict_list

```python
import_from_dict_list(self, table_name: 'str', data_list: 'list[dict]') -> 'int'
```


#### 📥 Arguments

    - **table_name:**  テーブル名
    - **data_list:**  挿入するデータのリスト

#### 📤 Returns

#### 💡 Example

```python
    >>> users = [
    ...     {"name": "Alice", "age": 25},
    ...     {"name": "Bob", "age": 30}
    ... ]
    >>> count = db.import_from_dict_list("users", users)
```

---

### get_last_insert_rowid

```python
get_last_insert_rowid(self) -> 'int'
```


#### 📤 Returns

#### 💡 Example

```python
    >>> db.sql_insert("users", {"name": "Alice"})
    >>> rowid = db.get_last_insert_rowid()
```

---

### pragma

```python
pragma(self, pragma_name: 'str', value: 'Any' = None) -> 'Any'
```


#### 📥 Arguments

    - **pragma_name:**  PRAGMA名
    - **value:**  設定値（Noneの場合は取得のみ）

#### 📤 Returns

#### 💡 Example

```python
    >>> # 取得
    >>> mode = db.pragma("journal_mode")
```

```python
    >>> # 設定
    >>> db.pragma("foreign_keys", 1)
```

---

### begin_transaction

```python
begin_transaction(self) -> 'None'
```

- **Note:** 

#### ⚠️ Raises

    - **NanaSQLiteTransactionError:**  既にトランザクション中の場合
    - **NanaSQLiteConnectionError:**  接続が閉じられている場合
    - **NanaSQLiteDatabaseError:**  トランザクション開始に失敗した場合

#### 💡 Example

```python
    >>> db.begin_transaction()
    >>> try:
    ...     db.sql_insert("users", {"name": "Alice"})
    ...     db.sql_insert("users", {"name": "Bob"})
    ...     db.commit()
    ... except:
    ...     db.rollback()
```

---

### commit

```python
commit(self) -> 'None'
```


#### ⚠️ Raises

    - **NanaSQLiteTransactionError:**  トランザクション外でコミットを試みた場合
    - **NanaSQLiteConnectionError:**  接続が閉じられている場合
    - **NanaSQLiteDatabaseError:**  コミットに失敗した場合

---

### rollback

```python
rollback(self) -> 'None'
```


#### ⚠️ Raises

    - **NanaSQLiteTransactionError:**  トランザクション外でロールバックを試みた場合
    - **NanaSQLiteConnectionError:**  接続が閉じられている場合
    - **NanaSQLiteDatabaseError:**  ロールバックに失敗した場合

---

### in_transaction

```python
in_transaction(self) -> 'bool'
```


#### 📤 Returns

    - **bool:**  トランザクション中の場合True

#### 💡 Example

```python
    >>> db.begin_transaction()
    >>> print(db.in_transaction())  # True
    >>> db.commit()
    >>> print(db.in_transaction())  # False
```

---

### transaction

```python
transaction(self)
```


#### ⚠️ Raises

    - **NanaSQLiteTransactionError:**  既にトランザクション中の場合

#### 💡 Example

```python
    >>> with db.transaction():
    ...     db.sql_insert("users", {"name": "Alice"})
    ...     db.sql_insert("users", {"name": "Bob"})
    ...     # 自動的にコミット、例外時はロールバック
```

---

### table

```python
table(self, table_name: 'str')
```

- 推奨: テーブルインスタンスを変数に保存して再利用してください

- **非推奨:** 
    sub1 = db.table

- **推奨:** 
    users_db = db.table

#### ⚠️ Raises

    - **NanaSQLiteConnectionError:**  接続が閉じられている場合

#### 💡 Example

```python
    >>> with NanaSQLite("app.db", table="main") as main_db:
    ...     users_db = main_db.table("users")
    ...     products_db = main_db.table("products")
    ...     users_db["user1"] = {"name": "Alice"}
    ...     products_db["prod1"] = {"name": "Laptop"}
```

---

### popitem

```python
popitem(self)
```

D.popitem() -> (k, v), remove and return some (key, value) pair
as a 2-tuple; but raise KeyError if D is empty.

---

