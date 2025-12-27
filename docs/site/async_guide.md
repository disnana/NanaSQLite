# 非同期サポート クイックガイド

## なぜ非同期が必要なのか？

従来の同期版`NanaSQLite`は、データベース操作が完了するまで処理をブロックします。これは通常のPythonアプリケーションでは問題ありませんが、以下のような非同期アプリケーションでは問題になります：

- **FastAPI, Quart, Sanic**: 非同期Webフレームワーク
- **aiohttp**: 非同期HTTPクライアント/サーバー
- **Discord.py, Telegram Bot API**: 非同期ボット
- **その他asyncioベースのアプリケーション**

これらのアプリケーションでは、ブロッキング操作がイベントループを停止させ、全体のパフォーマンスを低下させます。

## AsyncNanaSQLiteの解決策

`AsyncNanaSQLite`は、専用の**スレッドプールエグゼキューター**を使用してすべてのデータベース操作を実行することで、イベントループをブロックしません。

### 主な特徴

- **専用スレッドプール**: 設定可能なワーカー数（デフォルト5）
- **高性能**: APSWベースで最適化
- **並行処理**: 複数の操作を同時に実行可能
- **リソース管理**: 自動的にスレッドプールをクリーンアップ

```python
# ❌ 同期版（非同期アプリでブロッキング発生）
from nanasqlite import NanaSQLite
db = NanaSQLite("app.db")
user = db["user"]  # イベントループをブロック！

# ✅ 非同期版（ブロッキングなし、スレッドプール使用）
from nanasqlite import AsyncNanaSQLite
# 書き込み/重い処理には max_workers、並列読み込みには read_pool_size を調整
async with AsyncNanaSQLite("app.db", max_workers=10, read_pool_size=4) as db:
    user = await db.aget("user")  # イベントループをブロックしない
```

## 基本的な使い方

### 1. インポートと初期化

```python
import asyncio
from nanasqlite import AsyncNanaSQLite

async def main():
    # コンテキストマネージャを使用（推奨）
    # max_workers: 一般的なタスク用のスレッド数
    # read_pool_size: 並列読み込み専用の接続数 (v1.2.0+)
    async with AsyncNanaSQLite("mydata.db", max_workers=5, read_pool_size=4) as db:
        # データベース操作
        await db.aset("key", "value")
        value = await db.aget("key")
        print(value)

asyncio.run(main())
```

### スレッドプール設定のガイドライン

| シナリオ | 推奨max_workers | 理由 |
|---------|----------------|------|
| 低負荷（数個の同時接続） | 3-5 | リソース節約 |
| 中負荷（数十の同時接続） | 5-10 | バランス型 |
| 高負荷（100+の同時接続） | 10-20 | 高並行性 |
| 超高負荷（1000+の同時接続） | 20-50 | 最大パフォーマンス |

### 2. CRUD操作

```python
async with AsyncNanaSQLite("mydata.db") as db:
    # Create
    await db.aset("user_1", {"name": "Alice", "age": 25})
    
    # Read
    user = await db.aget("user_1")
    
    # Update
    user["age"] = 26
    await db.aset("user_1", user)
    
    # Delete
    await db.adelete("user_1")
```

### 3. バッチ操作

大量のデータを扱う場合は、バッチ操作が高速です：

```python
async with AsyncNanaSQLite("mydata.db") as db:
    # バッチ書き込み
    data = {f"user_{i}": {"name": f"User{i}"} for i in range(1000)}
    await db.batch_update(data)
    
    # バッチ削除
    keys = [f"user_{i}" for i in range(500)]
    await db.batch_delete(keys)
```

### 4. 並行操作

複数の操作を同時に実行：

```python
import asyncio

async with AsyncNanaSQLite("mydata.db") as db:
    # 並行読み込み
    users = await asyncio.gather(
        db.aget("user_1"),
        db.aget("user_2"),
        db.aget("user_3")
    )
```

## Webフレームワークでの使用

### FastAPIの例

```python
from fastapi import FastAPI
from nanasqlite import AsyncNanaSQLite
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時にデータベース接続を作成
    app.state.db = AsyncNanaSQLite("app.db")
    yield
    # シャットダウン時にデータベースをクローズ
    await app.state.db.close()

app = FastAPI(lifespan=lifespan)

# エンドポイント
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await app.state.db.aget(f"user_{user_id}")
    if user is None:
        return {"error": "User not found"}
    return user

@app.post("/users")
async def create_user(user: dict):
    await app.state.db.aset(f"user_{user['id']}", user)
    return {"status": "created", "id": user['id']}
```

### Quartsの例

```python
from quart import Quart, request, jsonify
from nanasqlite import AsyncNanaSQLite

app = Quart(__name__)
db = None

@app.before_serving
async def startup():
    global db
    db = AsyncNanaSQLite("app.db")

@app.after_serving
async def shutdown():
    await db.close()

@app.route("/users/<user_id>")
async def get_user(user_id):
    user = await db.aget(f"user_{user_id}")
    return jsonify(user)
```

## SQL操作

非同期でSQLも実行可能：

```python
async with AsyncNanaSQLite("mydata.db") as db:
    # テーブル作成
    await db.create_table("users", {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "email": "TEXT UNIQUE"
    })
    
    # データ挿入
    await db.sql_insert("users", {
        "name": "Alice",
        "email": "alice@example.com"
    })
    
    # クエリ実行
    users = await db.query(
        table_name="users",
        where="name LIKE ?",
        parameters=("A%",)
    )
```

## パフォーマンスのヒント

### 1. スレッドプールの最適化

負荷に応じてmax_workersを調整：

```python
# 低負荷アプリケーション（デフォルト）
async with AsyncNanaSQLite("mydata.db") as db:
    pass

# 高負荷アプリケーション（並行接続が多い）
async with AsyncNanaSQLite("mydata.db", max_workers=20) as db:
    # 100個の並行操作を効率的に処理
    results = await asyncio.gather(*[db.aget(f"key_{i}") for i in range(100)])
```

**推奨設定:**
- **開発環境**: max_workers=5（デフォルト）
- **本番環境（中規模）**: max_workers=10-15
- **本番環境（大規模）**: max_workers=20-50

### 2. 読み取り専用接続プール (v1.2.0+)

デフォルトでは、すべての操作が単一の SQLite 接続を共有します。大量の並列読み取りが発生する場合、それらは順番待ちになることがあります。

`read_pool_size` を設定することで、読み取り専用の接続プールを作成し、真の並列読み取りを可能にします。

```python
# 4つの専用接続で並列読み取りを有効化
db = AsyncNanaSQLite("app.db", read_pool_size=4)

# これらの読み取りは、複数の接続にまたがって並列に実行されます
results = await asyncio.gather(
    db.aget("key1"),
    db.aget("key2"),
    db.aget("key3"),
    db.aget("key4")
)
```

**いつ使うべきか:**
- 読み取りトラフィックが多い場合（パブリックAPI等）
- 実行に時間がかかる複雑なSQLクエリがある場合
- WALモード（デフォルトで有効）で読み取りが書き込みをブロックしない利点を活かしたい場合

### 3. バッチ操作を使用

```python
# ❌ 遅い（1000回のDB操作）
for i in range(1000):
    await db.aset(f"key_{i}", f"value_{i}")

# ✅ 速い（1回のトランザクション）
data = {f"key_{i}": f"value_{i}" for i in range(1000)}
await db.batch_update(data)
```

### 3. 並行操作を活用

```python
# ❌ 順次実行（遅い）
user1 = await db.aget("user_1")
user2 = await db.aget("user_2")
user3 = await db.aget("user_3")

# ✅ 並行実行（速い、スレッドプールで処理）
users = await asyncio.gather(
    db.aget("user_1"),
    db.aget("user_2"),
    db.aget("user_3")
)
```

### 4. bulk_loadを適切に使用

頻繁にアクセスするデータがある場合：

```python
# 起動時に全データをロード（読み込み重視）
db = AsyncNanaSQLite("mydata.db", bulk_load=True, max_workers=10)
```

### 5. 接続とスレッドプールの再利用

```python
# ❌ 毎回新しいインスタンスを作成（遅い）
async def handler():
    async with AsyncNanaSQLite("app.db") as db:
        return await db.aget("data")

# ✅ インスタンスを再利用（速い）
db = None

async def startup():
    global db
    db = AsyncNanaSQLite("app.db", max_workers=15)

async def handler():
    return await db.aget("data")

async def shutdown():
    await db.close()  # スレッドプールも自動クリーンアップ
```

## 同期版との使い分け

| 使用ケース | 推奨クラス |
|----------|----------|
| FastAPI, aiohttp等の非同期フレームワーク | `AsyncNanaSQLite` |
| Discord.py, Telegram Bot等の非同期ボット | `AsyncNanaSQLite` |
| 通常のPythonスクリプト | `NanaSQLite` |
| Django（同期フレームワーク） | `NanaSQLite` |
| コマンドラインツール | `NanaSQLite` |

## トラブルシューティング

### RuntimeError: Event loop is closed

コンテキストマネージャを使用してください：

```python
# ❌ 手動クローズ（エラーになる可能性）
db = AsyncNanaSQLite("app.db")
await db.aset("key", "value")
await db.close()

# ✅ コンテキストマネージャ（推奨）
async with AsyncNanaSQLite("app.db") as db:
    await db.aset("key", "value")
```

### 既存の同期コードを非同期に移行

メソッド名の対応表：

| 同期版 | 非同期版 |
|-------|---------|
| `db[key]` または `db.get(key)` | `await db.aget(key)` |
| `db[key] = value` | `await db.aset(key, value)` |
| `del db[key]` | `await db.adelete(key)` |
| `key in db` | `await db.acontains(key)` |
| `len(db)` | `await db.alen()` |
| `db.keys()` | `await db.akeys()` |
| `db.batch_update(data)` | `await db.batch_update(data)` |

## まとめ

- `AsyncNanaSQLite`は非同期アプリケーションでのブロッキングを防ぐ
- すべての操作は`await`が必要
- 並行操作で高速化が可能
- FastAPI等の非同期フレームワークに最適
- 同期版との互換性を保ちながら使用可能

詳細な使用例は[async_demo.py](https://github.com/disnana/nanasqlite/blob/main/examples/async_demo.py)を参照してください。
