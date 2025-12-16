# AsyncNanaSQLite API リファレンス

## 概要

`AsyncNanaSQLite`は、非同期アプリケーションでNanaSQLiteを使用するためのasync/awaitラッパーです。すべてのデータベース操作がスレッドプールで実行されるため、イベントループをブロックしません。

## クラス

### AsyncNanaSQLite

```python
from nanasqlite import AsyncNanaSQLite

async with AsyncNanaSQLite(
    db_path="mydata.db",
    table="data",
    bulk_load=False,
    optimize=True,
    cache_size_mb=64,
    max_workers=5,
    thread_name_prefix="AsyncNanaSQLite"
) as db:
    await db.aset("key", "value")
```

**パラメータ:**
- `db_path` (str): SQLiteデータベースファイルのパス
- `table` (str): 使用するテーブル名（デフォルト: "data"）
- `bulk_load` (bool): 初期化時に全データをロード（デフォルト: False）
- `optimize` (bool): WALモードなど高速化設定を適用（デフォルト: True）
- `cache_size_mb` (int): SQLiteキャッシュサイズ（MB、デフォルト: 64）
- `max_workers` (int): スレッドプール内の最大ワーカー数（デフォルト: 5）
- `thread_name_prefix` (str): スレッド名のプレフィックス（デフォルト: "AsyncNanaSQLite"）

## 非同期dict風インターフェース

### aget()
```python
value = await db.aget(key, default=None)
```
非同期でキーの値を取得。キーが存在しない場合はdefaultを返す。

### aset()
```python
await db.aset(key, value)
```
非同期でキーに値を設定。即座にDBに永続化される。

### adelete()
```python
await db.adelete(key)
```
非同期でキーを削除。キーが存在しない場合はKeyErrorを発生。

### acontains()
```python
exists = await db.acontains(key)
```
非同期でキーの存在を確認。

### alen()
```python
count = await db.alen()
```
非同期でデータベース内のキー数を取得。

### akeys()
```python
keys = await db.akeys()
```
非同期で全キーのリストを取得。

### avalues()
```python
values = await db.avalues()
```
非同期で全値のリストを取得。

### aitems()
```python
items = await db.aitems()
```
非同期で全アイテム（キーと値のタプル）のリストを取得。

### apop()
```python
value = await db.apop(key)
value = await db.apop(key, default)
```
非同期でキーを削除して値を返す。

### aupdate()
```python
await db.aupdate({"key1": "value1", "key2": "value2"})
await db.aupdate(key1="value1", key2="value2")
```
非同期で複数のキーを更新。

### aclear()
```python
await db.aclear()
```
非同期で全データを削除。

### asetdefault()
```python
value = await db.asetdefault(key, default=None)
```
非同期でキーが存在しない場合のみ値を設定。

## 非同期特殊メソッド

### load_all()
```python
await db.load_all()
```
非同期で全データを一括ロード。

### refresh()
```python
await db.refresh()  # 全キャッシュ更新
await db.refresh(key)  # 特定キーのみ更新
```
非同期でキャッシュを更新。

### is_cached()
```python
cached = await db.is_cached(key)
```
非同期でキーがキャッシュ済みか確認。

### batch_update()
```python
await db.batch_update({
    "key1": "value1",
    "key2": "value2",
    "key3": {"nested": "data"}
})
```
非同期で一括書き込み（トランザクション使用で高速）。

### batch_delete()
```python
await db.batch_delete(["key1", "key2", "key3"])
```
非同期で一括削除。

### to_dict()
```python
data = await db.to_dict()
```
非同期で全データをPython dictとして取得。

### copy()
```python
data_copy = await db.copy()
```
非同期で浅いコピーを作成。

### get_fresh()
```python
value = await db.get_fresh(key, default=None)
```
非同期でDBから直接読み込み、キャッシュを更新。

## 非同期Pydanticサポート

### set_model()
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

user = User(name="Nana", age=20)
await db.set_model("user", user)
```
非同期でPydanticモデルを保存。

### get_model()
```python
user = await db.get_model("user", User)
```
非同期でPydanticモデルを取得。

## 非同期SQL実行

### execute()
```python
cursor = await db.execute("SELECT * FROM data WHERE key LIKE ?", ("user%",))
```
非同期でSQLを直接実行。

### execute_many()
```python
await db.execute_many(
    "INSERT OR REPLACE INTO custom (id, name) VALUES (?, ?)",
    [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
)
```
非同期でSQLを複数のパラメータで一括実行。

### fetch_one()
```python
row = await db.fetch_one("SELECT value FROM data WHERE key = ?", ("user",))
```
非同期でSQLを実行して1行取得。

### fetch_all()
```python
rows = await db.fetch_all("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
```
非同期でSQLを実行して全行取得。

## 非同期SQLiteラッパー関数

### create_table()
```python
await db.create_table("users", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT NOT NULL",
    "email": "TEXT UNIQUE"
})
```
非同期でテーブルを作成。

### create_index()
```python
await db.create_index("idx_users_email", "users", ["email"], unique=True)
```
非同期でインデックスを作成。

### query()
```python
results = await db.query(
    table_name="users",
    columns=["id", "name", "email"],
    where="age > ?",
    parameters=(20,),
    order_by="name ASC",
    limit=10
)
```
非同期でSELECTクエリを実行。

### table_exists()
```python
exists = await db.table_exists("users")
```
非同期でテーブルの存在を確認。

### list_tables()
```python
tables = await db.list_tables()
```
非同期でデータベース内の全テーブル一覧を取得。

### drop_table()
```python
await db.drop_table("old_table")
```
非同期でテーブルを削除。

### drop_index()
```python
await db.drop_index("idx_users_email")
```
非同期でインデックスを削除。

### sql_insert()
```python
rowid = await db.sql_insert("users", {
    "name": "Alice",
    "email": "alice@example.com",
    "age": 25
})
```
非同期でdictから直接INSERT。

### sql_update()
```python
count = await db.sql_update("users",
    {"age": 26, "status": "active"},
    "name = ?",
    ("Alice",)
)
```
非同期でdictとwhere条件でUPDATE。

### sql_delete()
```python
count = await db.sql_delete("users", "age < ?", (18,))
```
非同期でwhere条件でDELETE。

### vacuum()
```python
await db.vacuum()
```
非同期でデータベースを最適化（VACUUM実行）。

## 非同期コンテキストマネージャ

```python
async with AsyncNanaSQLite("mydata.db") as db:
    await db.aset("key", "value")
    value = await db.aget("key")
# 自動的にクローズされる
```

## 並行処理

複数の非同期操作を並行実行:

```python
import asyncio

async with AsyncNanaSQLite("mydata.db") as db:
    # 並行読み込み
    results = await asyncio.gather(
        db.aget("key1"),
        db.aget("key2"),
        db.aget("key3")
    )
    
    # 並行書き込み
    await asyncio.gather(
        db.aset("key1", "value1"),
        db.aset("key2", "value2"),
        db.aset("key3", "value3")
    )
```

## 使用例

### FastAPIでの使用

```python
from fastapi import FastAPI
from nanasqlite import AsyncNanaSQLite

app = FastAPI()
db = AsyncNanaSQLite("app.db")

@app.on_event("startup")
async def startup():
    global db
    db = AsyncNanaSQLite("app.db")

@app.on_event("shutdown")
async def shutdown():
    await db.close()

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await db.aget(f"user_{user_id}")
    return user

@app.post("/users")
async def create_user(user: dict):
    await db.aset(f"user_{user['id']}", user)
    return {"status": "created"}
```

### aiohttpでの使用

```python
from aiohttp import web
from nanasqlite import AsyncNanaSQLite

async def get_user(request):
    user_id = request.match_info['user_id']
    db = request.app['db']
    user = await db.aget(f"user_{user_id}")
    return web.json_response(user)

async def init_app():
    app = web.Application()
    app['db'] = AsyncNanaSQLite("app.db")
    app.add_routes([web.get('/users/{user_id}', get_user)])
    return app

if __name__ == '__main__':
    web.run_app(init_app())
```

## マルチテーブルサポート (v1.1.0dev1+)

### table()

```python
sub_db = await db.table(table_name)
```

非同期でサブテーブルのAsyncNanaSQLiteインスタンスを取得。接続とスレッドプールエグゼキューターを共有します。

**パラメータ:**
- `table_name` (str): 取得するテーブル名

**戻り値:**
- `AsyncNanaSQLite`: 指定したテーブルを操作する新しいインスタンス

**使用例:**

```python
async with AsyncNanaSQLite("app.db", table="main") as db:
    # サブテーブルのインスタンスを取得
    users_db = await db.table("users")
    config_db = await db.table("config")
    
    # 各テーブルに独立してデータを保存
    await users_db.aset("alice", {"name": "Alice", "age": 30})
    await config_db.aset("theme", "dark")
    
    # 各テーブルから取得
    user = await users_db.aget("alice")
    theme = await config_db.aget("theme")
```

**利点:**
- **スレッドセーフ**: 複数の非同期タスクからの同時書き込みが安全
- **リソース効率**: SQLite接続とスレッドプールを再利用
- **キャッシュ分離**: 各テーブルは独立したメモリキャッシュ

---

## 注意事項

1. **スレッドセーフティ**: `AsyncNanaSQLite`は内部でスレッドプールを使用するため、スレッドセーフです。
2. **パフォーマンス**: 非同期操作はスレッドプールで実行されるため、CPU負荷の高い操作には向いていません。I/O待機が多い場合に効果的です。
3. **同期DBへのアクセス**: `db.sync_db`プロパティで内部の同期DBにアクセスできますが、推奨されません（ブロッキングの可能性）。

## 同期版との互換性

既存の同期版`NanaSQLite`は完全に互換性が保たれており、同じAPIを使用できます。非同期が不要な場合は、引き続き`NanaSQLite`を使用してください。
