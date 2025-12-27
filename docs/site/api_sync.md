# 同期 API リファレンス

NanaSQLiteクラスの同期メソッド一覧です。

## NanaSQLite

APSW SQLiteをバックエンドとした、セキュリティ・接続管理強化版の辞書型ラッパー (v1.2.0)

内部でPython dictを保持し、操作時にSQLiteとの同期を行います。
v1.2.0では、動的SQLのバリデーション強化、ReDoS対策、および厳格な接続管理が導入されています。

#### 📥 引数

    - **db_path:**  SQLiteデータベースファイルのパス
    - **table:**  デフォルト: "data"
    - **bulk_load:**  Trueの場合、初期化時に全データをメモリに読み込む
    - **strict_sql_validation:**  v1.2.0
    - **max_clause_length:**  SQL句の最大長（ReDoS対策、v1.2.0）

---

## メソッド

### __init__

```python
__init__(self, db_path: 'str', table: 'str' = 'data', bulk_load: 'bool' = False, optimize: 'bool' = True, cache_size_mb: 'int' = 64, strict_sql_validation: 'bool' = True, allowed_sql_functions: 'list[str] | None' = None, forbidden_sql_functions: 'list[str] | None' = None, max_clause_length: 'int | None' = 1000, _shared_connection: 'apsw.Connection | None' = None, _shared_lock: 'threading.RLock | None' = None)
```


#### 📥 引数

    - **db_path:**  SQLiteデータベースファイルのパス
    - **table:**  デフォルト: "data"
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

全キーを取得（DBから）

---

### values

```python
values(self) -> 'list'
```

全値を取得（一括ロードしてからメモリから）

---

### items

```python
items(self) -> 'list'
```

全アイテムを取得（一括ロードしてからメモリから）

---

### get

```python
get(self, key: 'str', default: 'Any' = None) -> 'Any'
```

key, default

---

### get_fresh

```python
get_fresh(self, key: 'str', default: 'Any' = None) -> 'Any'
```

DBから直接読み込み、キャッシュを更新して値を返す

キャッシュをバイパスしてDBから最新の値を取得する。
`execute()`でDBを直接変更した後などに使用。

通常の`get()`よりオーバーヘッドがあるため、
キャッシュとDBの不整合が想定される場合のみ使用推奨。

#### 📥 引数

    - **key:**  取得するキー
    - **default:**  キーが存在しない場合のデフォルト値

#### 📤 戻り値

    DBから取得した最新の値（存在しない場合はdefault）

#### 💡 使用例

```python
    >>> db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new"', "key"))
    >>> value = db.get_fresh("key")  # DBから最新値を取得
```

---

### batch_get

```python
batch_get(self, keys: 'list[str]') -> 'dict[str, Any]'
```

複数のキーを一度に取得（効率的な一括ロード）

1回の `SELECT IN (...)` クエリで複数のキーをDBから取得する。
取得した値は自動的にキャッシュに保存される。

#### 📥 引数

    - **keys:**  取得するキーのリスト

#### 📤 戻り値

    取得に成功したキーと値の dict

#### 💡 使用例

```python
    >>> results = db.batch_get(["user1", "user2", "user3"])
    >>> print(results)  # {"user1": {...}, "user2": {...}}
```

---

### pop

```python
pop(self, key: 'str', *args) -> 'Any'
```

key[, default]

---

### update

```python
update(self, mapping: 'dict' = None, **kwargs) -> 'None'
```

dict.update(mapping) - 一括更新

---

### clear

```python
clear(self) -> 'None'
```

dict.clear() - 全削除

---

### setdefault

```python
setdefault(self, key: 'str', default: 'Any' = None) -> 'Any'
```

key, default

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

キャッシュを更新（DBから再読み込み）

#### 📥 引数

    - **key:**  特定のキーのみ更新。Noneの場合は全キャッシュをクリアして再読み込み

---

### is_cached

```python
is_cached(self, key: 'str') -> 'bool'
```

キーがキャッシュ済みかどうか

---

### batch_update

```python
batch_update(self, mapping: 'dict[str, Any]') -> 'None'
```

一括書き込み（トランザクション + executemany使用で超高速）

大量のデータを一度に書き込む場合、通常のupdateより10-100倍高速。
v1.0.3rc5でexecutemanyによる最適化を追加。

#### 📥 引数

    - **mapping:**  書き込むキーと値のdict

#### 📤 戻り値

#### 💡 使用例

```python
    >>> db.batch_update({"key1": "value1", "key2": "value2", ...})
```

---

### batch_delete

```python
batch_delete(self, keys: 'list[str]') -> 'None'
```

一括削除（トランザクション + executemany使用で高速）

v1.0.3rc5でexecutemanyによる最適化を追加。

#### 📥 引数

    - **keys:**  削除するキーのリスト

#### 📤 戻り値


---

### to_dict

```python
to_dict(self) -> 'dict'
```

全データをPython dictとして取得

---

### copy

```python
copy(self) -> 'dict'
```

浅いコピーを作成（標準dictを返す）

---

### close

```python
close(self) -> 'None'
```

データベース接続を閉じる

- **注意:**  table()メソッドで作成されたインスタンスは接続を共有しているため、
接続の所有者（最初に作成されたインスタンス）のみが接続を閉じます。

#### ⚠️ 例外

    - **NanaSQLiteTransactionError:**  トランザクション中にクローズを試みた場合

---

### set_model

```python
set_model(self, key: 'str', model: 'Any') -> 'None'
```

Pydanticモデルを保存

Pydanticモデル（BaseModelを継承したクラス）をシリアライズして保存。
model_dump()メソッドを使用してdictに変換し、モデルのクラス情報も保存。

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
    >>> db.set_model("user", user)
```

---

### get_model

```python
get_model(self, key: 'str', model_class: 'type' = None) -> 'Any'
```

Pydanticモデルを取得

保存されたPydanticモデルをデシリアライズして復元。
model_classが指定されていない場合は、保存時のクラス情報を使用。

#### 📥 引数

    - **key:**  取得するキー
    - **model_class:**  Pydanticモデルのクラス（Noneの場合は自動検出を試みる）

#### 📤 戻り値

    Pydanticモデルのインスタンス

#### 💡 使用例

```python
    >>> user = db.get_model("user", User)
    >>> print(user.name)  # "Nana"
```

---

### execute

```python
execute(self, sql: 'str', parameters: 'tuple | None' = None) -> 'apsw.Cursor'
```

SQLを直接実行

任意のSQL文を実行できる。SELECT、INSERT、UPDATE、DELETEなど。
パラメータバインディングをサポート（SQLインジェクション対策）。

    このメソッドで直接デフォルトテーブル（data）を操作した場合、
    内部キャッシュ（_data）と不整合が発生する可能性があります。
    キャッシュを更新するには `refresh()` を呼び出してください。

#### 📥 引数

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ（?プレースホルダー用）

#### 📤 戻り値

    APSWのCursorオブジェクト（結果の取得に使用）

#### ⚠️ 例外

    - **NanaSQLiteConnectionError:**  接続が閉じられている場合
    - **NanaSQLiteDatabaseError:**  SQL実行エラー

#### 💡 使用例

```python
    >>> cursor = db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
    >>> for row in cursor:
    ...     print(row)
```

    # キャッシュ更新が必要な場合:
```python
    >>> db.execute("UPDATE data SET value = ? WHERE key = ?", ('"new"', "key"))
    >>> db.refresh("key")  # キャッシュを更新
```

---

### execute_many

```python
execute_many(self, sql: 'str', parameters_list: 'list[tuple]') -> 'None'
```

SQLを複数のパラメータで一括実行

同じSQL文を複数のパラメータセットで実行（トランザクション使用）。
大量のINSERTやUPDATEを高速に実行できる。

#### 📥 引数

    - **sql:**  実行するSQL文
    - **parameters_list:**  パラメータのリスト

#### 💡 使用例

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

SQLを実行して1行取得

#### 📥 引数

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 戻り値

    1行の結果（tuple）、結果がない場合はNone

#### 💡 使用例

```python
    >>> row = db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
    >>> print(row[0])
```

---

### fetch_all

```python
fetch_all(self, sql: 'str', parameters: 'tuple' = None) -> 'list[tuple]'
```

SQLを実行して全行取得

#### 📥 引数

    - **sql:**  実行するSQL文
    - **parameters:**  SQLのパラメータ

#### 📤 戻り値

    全行の結果（tupleのリスト）

#### 💡 使用例

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

テーブルを作成

#### 📥 引数

    - **table_name:**  テーブル名
    - **columns:**  カラム定義のdict（カラム名: SQL型）
    - **if_not_exists:**  Trueの場合、存在しない場合のみ作成
    - **primary_key:**  プライマリキーのカラム名（Noneの場合は指定なし）

#### 💡 使用例

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

インデックスを作成

#### 📥 引数

    - **index_name:**  インデックス名
    - **table_name:**  テーブル名
    - **columns:**  インデックスを作成するカラムのリスト
    - **unique:**  Trueの場合、ユニークインデックスを作成
    - **if_not_exists:**  Trueの場合、存在しない場合のみ作成

#### 💡 使用例

```python
    >>> db.create_index("idx_users_email", "users", ["email"], unique=True)
    >>> db.create_index("idx_posts_user", "posts", ["user_id", "created_at"])
```

---

### query

```python
query(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```

シンプルなSELECTクエリを実行

#### 📥 引数

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

#### 📤 戻り値

    結果のリスト（各行はdict）

#### 💡 使用例

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

テーブルの存在確認

#### 📥 引数

    - **table_name:**  テーブル名

#### 📤 戻り値

    存在する場合True、しない場合False

#### 💡 使用例

```python
    >>> if db.table_exists("users"):
    ...     print("users table exists")
```

---

### list_tables

```python
list_tables(self) -> 'list[str]'
```

データベース内の全テーブル一覧を取得

#### 📤 戻り値

    テーブル名のリスト

#### 💡 使用例

```python
    >>> tables = db.list_tables()
    >>> print(tables)  # ['data', 'users', 'posts']
```

---

### drop_table

```python
drop_table(self, table_name: 'str', if_exists: 'bool' = True) -> 'None'
```

テーブルを削除

#### 📥 引数

    - **table_name:**  テーブル名
    - **if_exists:**  Trueの場合、存在する場合のみ削除（エラーを防ぐ）

#### 💡 使用例

```python
    >>> db.drop_table("old_table")
    >>> db.drop_table("temp", if_exists=True)
```

---

### drop_index

```python
drop_index(self, index_name: 'str', if_exists: 'bool' = True) -> 'None'
```

インデックスを削除

#### 📥 引数

    - **index_name:**  インデックス名
    - **if_exists:**  Trueの場合、存在する場合のみ削除

#### 💡 使用例

```python
    >>> db.drop_index("idx_users_email")
```

---

### alter_table_add_column

```python
alter_table_add_column(self, table_name: 'str', column_name: 'str', column_type: 'str', default: 'Any' = None) -> 'None'
```

既存テーブルにカラムを追加

#### 📥 引数

    - **table_name:**  テーブル名
    - **column_name:**  カラム名
    - **column_type:**  カラムの型（SQL型）
    - **default:**  デフォルト値（Noneの場合は指定なし）

#### 💡 使用例

```python
    >>> db.alter_table_add_column("users", "phone", "TEXT")
    >>> db.alter_table_add_column("users", "status", "TEXT", default="'active'")
```

---

### get_table_schema

```python
get_table_schema(self, table_name: 'str') -> 'list[dict]'
```

テーブル構造を取得

#### 📥 引数

    - **table_name:**  テーブル名

#### 📤 戻り値

    カラム情報のリスト（各カラムはdict）

#### 💡 使用例

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

インデックス一覧を取得

#### 📥 引数

    - **table_name:**  テーブル名（Noneの場合は全インデックス）

#### 📤 戻り値

    インデックス情報のリスト

#### 💡 使用例

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

dictから直接INSERT

#### 📥 引数

    - **table_name:**  テーブル名
    - **data:**  カラム名と値のdict

#### 📤 戻り値

    挿入されたROWID

#### 💡 使用例

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

dictとwhere条件でUPDATE

#### 📥 引数

    - **table_name:**  テーブル名
    - **data:**  更新するカラム名と値のdict
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ

#### 📤 戻り値

    更新された行数

#### 💡 使用例

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

where条件でDELETE

#### 📥 引数

    - **table_name:**  テーブル名
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ

#### 📤 戻り値

    削除された行数

#### 💡 使用例

```python
    >>> count = db.sql_delete("users", "age < ?", (18,))
```

---

### upsert

```python
upsert(self, table_name: 'str', data: 'dict', conflict_columns: 'list[str]' = None) -> 'int'
```

INSERT OR REPLACE の簡易版（upsert）

#### 📥 引数

    - **table_name:**  テーブル名
    - **data:**  カラム名と値のdict
    - **conflict_columns:**  競合判定に使用するカラム（Noneの場合はINSERT OR REPLACE）

#### 📤 戻り値

    挿入/更新されたROWID

#### 💡 使用例

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

レコード数を取得

#### 📥 引数

    - **table_name:**  テーブル名（Noneの場合はデフォルトテーブル）
    - **where:**  WHERE句の条件（オプション）
    - **parameters:**  WHERE句のパラメータ
    - **strict_sql_validation:**  Trueの場合、未許可の関数等を含むクエリを拒否
    - **allowed_sql_functions:**  このクエリで一時的に許可するSQL関数のリスト
    - **forbidden_sql_functions:**  このクエリで一時的に禁止するSQL関数のリスト
    - **override_allowed:**  Trueの場合、インスタンス許可設定を無視

#### 💡 使用例

```python
    >>> total = db.count("users")
    >>> adults = db.count("users", "age >= ?", (18,))
```

---

### exists

```python
exists(self, table_name: 'str', where: 'str', parameters: 'tuple' = None) -> 'bool'
```

レコードの存在確認

#### 📥 引数

    - **table_name:**  テーブル名
    - **where:**  WHERE句の条件
    - **parameters:**  WHERE句のパラメータ

#### 📤 戻り値

    存在する場合True

#### 💡 使用例

```python
    >>> if db.exists("users", "email = ?", ("alice@example.com",)):
    ...     print("User exists")
```

---

### query_with_pagination

```python
query_with_pagination(self, table_name: 'str' = None, columns: 'list[str]' = None, where: 'str' = None, parameters: 'tuple' = None, order_by: 'str' = None, limit: 'int' = None, offset: 'int' = None, group_by: 'str' = None, strict_sql_validation: 'bool' = None, allowed_sql_functions: 'list[str]' = None, forbidden_sql_functions: 'list[str]' = None, override_allowed: 'bool' = False) -> 'list[dict]'
```

拡張されたクエリ（offset、group_by対応）

#### 📥 引数

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

#### 📤 戻り値

    結果のリスト

#### 💡 使用例

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

データベースを最適化（VACUUM実行）

削除されたレコードの領域を回収し、データベースファイルを最適化。

#### 💡 使用例

```python
    >>> db.vacuum()
```

---

### get_db_size

```python
get_db_size(self) -> 'int'
```

データベースファイルのサイズを取得（バイト単位）

#### 📤 戻り値

    データベースファイルのサイズ

#### 💡 使用例

```python
    >>> size = db.get_db_size()
    >>> print(f"DB size: {size / 1024 / 1024:.2f} MB")
```

---

### export_table_to_dict

```python
export_table_to_dict(self, table_name: 'str') -> 'list[dict]'
```

テーブル全体をdictのリストとして取得

#### 📥 引数

    - **table_name:**  テーブル名

#### 📤 戻り値

    全レコードのリスト

#### 💡 使用例

```python
    >>> all_users = db.export_table_to_dict("users")
```

---

### import_from_dict_list

```python
import_from_dict_list(self, table_name: 'str', data_list: 'list[dict]') -> 'int'
```

dictのリストからテーブルに一括挿入

#### 📥 引数

    - **table_name:**  テーブル名
    - **data_list:**  挿入するデータのリスト

#### 📤 戻り値

    挿入された行数

#### 💡 使用例

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

最後に挿入されたROWIDを取得

#### 📤 戻り値

    最後に挿入されたROWID

#### 💡 使用例

```python
    >>> db.sql_insert("users", {"name": "Alice"})
    >>> rowid = db.get_last_insert_rowid()
```

---

### pragma

```python
pragma(self, pragma_name: 'str', value: 'Any' = None) -> 'Any'
```

PRAGMA設定の取得/設定

#### 📥 引数

    - **pragma_name:**  PRAGMA名
    - **value:**  設定値（Noneの場合は取得のみ）

#### 📤 戻り値

    valueがNoneの場合は現在の値、そうでない場合はNone

#### 💡 使用例

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

トランザクションを開始

- **Note:** 
    SQLiteはネストされたトランザクションをサポートしていません。
    既にトランザクション中の場合、NanaSQLiteTransactionErrorが発生します。

#### ⚠️ 例外

    - **NanaSQLiteTransactionError:**  既にトランザクション中の場合
    - **NanaSQLiteConnectionError:**  接続が閉じられている場合
    - **NanaSQLiteDatabaseError:**  トランザクション開始に失敗した場合

#### 💡 使用例

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

トランザクションをコミット

#### ⚠️ 例外

    - **NanaSQLiteTransactionError:**  トランザクション外でコミットを試みた場合
    - **NanaSQLiteConnectionError:**  接続が閉じられている場合
    - **NanaSQLiteDatabaseError:**  コミットに失敗した場合

---

### rollback

```python
rollback(self) -> 'None'
```

トランザクションをロールバック

#### ⚠️ 例外

    - **NanaSQLiteTransactionError:**  トランザクション外でロールバックを試みた場合
    - **NanaSQLiteConnectionError:**  接続が閉じられている場合
    - **NanaSQLiteDatabaseError:**  ロールバックに失敗した場合

---

### in_transaction

```python
in_transaction(self) -> 'bool'
```

現在トランザクション中かどうかを返す

#### 📤 戻り値

    - **bool:**  トランザクション中の場合True

#### 💡 使用例

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

トランザクションのコンテキストマネージャ

コンテキストマネージャ内で例外が発生しない場合は自動的にコミット、
例外が発生した場合は自動的にロールバックします。

#### ⚠️ 例外

    - **NanaSQLiteTransactionError:**  既にトランザクション中の場合

#### 💡 使用例

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

サブテーブル用のNanaSQLiteインスタンスを取得

新しいインスタンスを作成しますが、SQLite接続とロックは共有します。
これにより、複数のテーブルインスタンスが同じ接続を使用して
スレッドセーフに動作します。

⚠️ 重要な注意事項:
- 同じテーブルに対して複数のインスタンスを作成しないでください
  各インスタンスは独立したキャッシュを持つため、キャッシュ不整合が発生します
- 推奨: テーブルインスタンスを変数に保存して再利用してください

- **非推奨:** 
    "users"
    sub2 = db.table("users")  # キャッシュ不整合の原因

- **推奨:** 
    "users"
    # users_dbを使い回す

:param table_name: テーブル名
:return NanaSQLite: 新しいテーブルインスタンス

#### ⚠️ 例外

    - **NanaSQLiteConnectionError:**  接続が閉じられている場合

#### 💡 使用例

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

---

