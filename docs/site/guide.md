# NanaSQLite チュートリアル

基礎から応用まで、NanaSQLiteを段階的に学ぶガイドです。

## 前提条件

- Python 3.9以上
- Pythonの辞書の基本的な理解
- SQLiteの知識があると役立ちますが、必須ではありません

## インストール

```bash
pip install nanasqlite
```

## レッスン1: 最初のデータベース

### データベースの作成

```python
from nanasqlite import NanaSQLite

# データベースファイルを作成または開く
db = NanaSQLite("tutorial.db")

# データを保存
db["greeting"] = "こんにちは、世界！"
db["number"] = 42
db["pi"] = 3.14159

# データを取得
print(db["greeting"])  # こんにちは、世界！
print(db["number"])    # 42

# 終了時にクローズ
db.close()
```

**何が起こったか？**
- SQLiteデータベースファイル `tutorial.db` が作成されました
- データは即座にディスクに保存されました
- プログラム終了後もデータは永続化されています

### コンテキストマネージャの使用

```python
from nanasqlite import NanaSQLite

# 自動的にデータベースをクローズ
with NanaSQLite("tutorial.db") as db:
    db["message"] = "コンテキストマネージャを使用！"
    print(db["message"])
# ここでデータベースは自動的にクローズされます
```

**ベストプラクティス:** 常にコンテキストマネージャ（`with`文）を使用して、適切なクリーンアップを保証しましょう。

## レッスン2: 複雑なデータの扱い

### ネスト構造の保存

```python
with NanaSQLite("tutorial.db") as db:
    # ユーザープロファイルを保存
    db["user_alice"] = {
        "name": "Alice",
        "age": 30,
        "email": "alice@example.com",
        "preferences": {
            "theme": "dark",
            "notifications": True,
            "language": "ja"
        },
        "tags": ["admin", "developer", "python"]
    }
    
    # ネストしたデータにアクセス
    user = db["user_alice"]
    print(user["name"])                      # Alice
    print(user["preferences"]["theme"])      # dark
    print(user["tags"][0])                   # admin
```

### サポートされるデータ型

```python
with NanaSQLite("tutorial.db") as db:
    db["string"] = "テキスト"
    db["integer"] = 100
    db["float"] = 99.99
    db["boolean"] = True
    db["none"] = None
    db["list"] = [1, 2, 3, "four"]
    db["dict"] = {"nested": {"deeply": {"value": 123}}}
```

**注意:** NanaSQLiteは複雑なPythonオブジェクトを自動的にJSONにシリアライズします。

## レッスン3: 辞書操作

### 存在確認

```python
with NanaSQLite("tutorial.db") as db:
    db["config"] = {"theme": "dark"}
    
    # キーの存在を確認
    if "config" in db:
        print("設定が存在します！")
    
    if "missing" not in db:
        print("このキーは存在しません")
    
    # デフォルト値付きで取得
    value = db.get("missing", "デフォルト値")
    print(value)  # デフォルト値
```

### データの反復処理

```python
with NanaSQLite("tutorial.db") as db:
    # データを追加
    db["user_1"] = {"name": "Alice"}
    db["user_2"] = {"name": "Bob"}
    db["user_3"] = {"name": "Charlie"}
    
    # キーを反復
    for key in db.keys():
        print(key)
    
    # 値を反復
    for value in db.values():
        print(value)
    
    # キーと値のペアを反復
    for key, value in db.items():
        print(f"{key}: {value}")
```

### 更新と削除

```python
with NanaSQLite("tutorial.db") as db:
    # 単一キーの更新
    db["counter"] = 0
    db["counter"] = db["counter"] + 1
    print(db["counter"])  # 1
    
    # 複数キーを一度に更新
    db.update({
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    })
    
    # キーを削除
    del db["key1"]
    
    # Pop（取得して削除）
    value = db.pop("key2")
    print(value)  # value2
    
    # 全データをクリア
    # db.clear()  # コメントを外すとすべて削除されます
```

## レッスン4: パフォーマンス最適化

### 一括ロード

```python
# 読み込み重視のワークロードには、起動時に全データをロード
with NanaSQLite("tutorial.db", bulk_load=True) as db:
    # 全データがメモリに展開されています
    # 以降の読み込みは超高速
    for key in db.keys():
        print(db[key])  # データベースクエリなし！
```

**bulk_loadを使用するとき:**
- 小～中規模のデータベース（<100MB）
- ほとんどのキーを頻繁に読み込む
- アプリケーション起動時間が重要でない

**bulk_loadを使用しないとき:**
- 大規模データベース（>1GB）
- まばらなアクセスパターン（少数のキーのみアクセス）
- メモリに制約がある環境

### バッチ操作

```python
with NanaSQLite("tutorial.db") as db:
    # ❌ 遅い: 個別の挿入
    for i in range(1000):
        db[f"item_{i}"] = {"value": i}
    
    # ✅ 速い: バッチ挿入（10-100倍高速）
    data = {f"item_{i}": {"value": i} for i in range(1000)}
    db.batch_update(data)
    
    # バッチ削除
    keys_to_delete = [f"item_{i}" for i in range(500)]
    db.batch_delete(keys_to_delete)
```

**パフォーマンスのヒント:** 100以上の操作には、常にバッチメソッドを使用しましょう。

## レッスン5: Pydanticモデルの使用

```python
from pydantic import BaseModel
from nanasqlite import NanaSQLite

class User(BaseModel):
    name: str
    age: int
    email: str

with NanaSQLite("tutorial.db") as db:
    # Pydanticモデルを保存
    user = User(name="Alice", age=30, email="alice@example.com")
    db.set_model("user_alice", user)
    
    # Pydanticモデルとして取得
    retrieved = db.get_model("user_alice", User)
    print(retrieved.name)   # Alice
    print(retrieved.age)    # 30
    print(type(retrieved))  # <class '__main__.User'>
```

## レッスン6: 直接SQLクエリ

### 基本的なクエリ

```python
with NanaSQLite("tutorial.db") as db:
    # カスタムテーブルを作成
    db.create_table("users", {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "email": "TEXT UNIQUE",
        "age": "INTEGER"
    })
    
    # データを挿入
    db.sql_insert("users", {"name": "Alice", "email": "alice@example.com", "age": 30})
    db.sql_insert("users", {"name": "Bob", "email": "bob@example.com", "age": 25})
    
    # データをクエリ
    results = db.query(
        table_name="users",
        columns=["name", "age"],
        where="age > ?",
        parameters=(25,),
        order_by="name ASC"
    )
    
    for row in results:
        print(f"{row['name']}: {row['age']}")
```

### 高度なSQL

```python
with NanaSQLite("tutorial.db") as db:
    # カスタムSQLを実行
    cursor = db.execute("SELECT * FROM users WHERE name LIKE ?", ("A%",))
    for row in cursor:
        print(row)
    
    # 全結果を取得
    rows = db.fetch_all("SELECT name, age FROM users ORDER BY age DESC")
    
    # 1つの結果を取得
    row = db.fetch_one("SELECT * FROM users WHERE email = ?", ("alice@example.com",))
```

## レッスン7: エラーハンドリング

```python
from nanasqlite import NanaSQLite

with NanaSQLite("tutorial.db") as db:
    # 存在しないキーを処理
    try:
        value = db["nonexistent"]
    except KeyError:
        print("キーが見つかりません！")
    
    # より良い方法: デフォルト値付きでget()を使用
    value = db.get("nonexistent", "デフォルト")
    
    # SQLエラーを処理
    import apsw
    try:
        db.execute("INVALID SQL")
    except apsw.Error as e:
        print(f"SQLエラー: {e}")
```

## レッスン8: 複数テーブル

ひとつのデータベースファイル内で、異なるデータタイプごとにテーブルを分けることができます。`.table()` メソッドを使用すると、同じ接続を共有しながら独立したテーブルを操作できます。

```python
from nanasqlite import NanaSQLite

# メインインスタンスの作成
db = NanaSQLite("app.db")

# サブテーブル用インスタンスの取得（接続を共有するため効率的）
users_db = db.table("users")
config_db = db.table("config")
cache_db = db.table("cache")

# それぞれが独立して動作
users_db["alice"] = {"name": "Alice", "role": "admin"}
config_db["theme"] = "dark"
cache_db["temp_data"] = {"expires": "2024-12-31"}

# 親を閉じればすべてクローズされます
db.close()
```

## レッスン9: 非同期の使用（上級）

FastAPIなどの非同期フレームワーク向け:

```python
import asyncio
from nanasqlite import AsyncNanaSQLite

async def main():
    async with AsyncNanaSQLite("tutorial.db") as db:
        # 非同期操作
        await db.aset("user", {"name": "Alice"})
        user = await db.aget("user")
        print(user)
        
        # 並行操作
        results = await asyncio.gather(
            db.aget("key1"),
            db.aget("key2"),
            db.aget("key3")
        )

asyncio.run(main())
```

詳細な非同期ドキュメントは[async_guide](async_guide)を参照してください。

## レッスン 10: キャッシュ戦略 (v1.3.0)

メモリ使用量を抑えつつ高速に動作させるために、キャッシュの追い出し（LRU）戦略を選択できます。

### LRU キャッシュの使用

```python
from nanasqlite import NanaSQLite, CacheType

# 最新の 1000 件のみをメモリにキャッシュ
with NanaSQLite("app.db", cache_strategy=CacheType.LRU, cache_size=1000) as db:
    db["key"] = "value"
```

### パフォーマンスの最大化

`lru-dict` がインストールされている場合、C拡張による超高速なキャッシュ操作が可能です。

```bash
pip install nanasqlite[speed]
```

詳細は[パフォーマンスチューニングガイド](performance_tuning)を参照してください。

## 一般的なパターン

### 設定の保存

```python
with NanaSQLite("config.db") as db:
    # アプリケーション設定を保存
    db["app_config"] = {
        "version": "1.0.0",
        "debug": False,
        "database_url": "sqlite:///data.db",
        "secret_key": "your-secret-key"
    }
    
    # 設定を取得
    config = db["app_config"]
    if config["debug"]:
        print("デバッグモード有効")
```

### キャッシング

```python
import time

with NanaSQLite("cache.db") as db:
    # タイムスタンプ付きでキャッシュデータを保存
    db["api_response"] = {
        "data": {"users": [...]},
        "cached_at": time.time()
    }
    
    # キャッシュの年齢を確認
    cached = db.get("api_response")
    if cached and (time.time() - cached["cached_at"]) < 3600:
        # キャッシュが新鮮（1時間未満）
        data = cached["data"]
    else:
        # APIから新しいデータを取得
        # 例: data = requests.get("https://api.example.com/data").json()
        data = fetch_from_api()  # 実際のAPIコール関数に置き換えてください
        db["api_response"] = {"data": data, "cached_at": time.time()}
```

### セッション保存

```python
import uuid
import time

with NanaSQLite("sessions.db") as db:
    # セッションを作成
    session_id = str(uuid.uuid4())
    db[f"session_{session_id}"] = {
        "user_id": "alice",
        "created_at": time.time(),
        "data": {"cart": ["item1", "item2"]}
    }
    
    # セッションを取得
    session = db.get(f"session_{session_id}")
    if session:
        print(f"ユーザー: {session['user_id']}")
        print(f"カート: {session['data']['cart']}")
```

## ベストプラクティス

1. **常にコンテキストマネージャを使用**（`with`文）
2. **複数書き込みにはバッチ操作を使用**（100以上のアイテム）
3. **読み込み重視のワークロードには`bulk_load=True`を使用**
4. **`try/except KeyError`の代わりにデフォルト値付きで`get()`を使用**
5. **異なるテーブルで関心事を分離**
6. **終了時にデータベースをクローズ**（コンテキストマネージャで自動）

## 次のステップ

- 完全なメソッドドキュメントは[APIリファレンス](./api_sync)を参照
- async/await の使用方法は[Async Guide](async_guide)を探索
- 本番環境のヒントは[Best Practices](best_practices)を確認
- 実際のコードサンプルは[examples/](https://github.com/disnana/nanasqlite/tree/main/examples/)を参照

## トラブルシューティング

### データベースがロックされている

```python
# SQLiteは一度に1つの書き込みのみ許可
# 複数書き込みにはトランザクションを使用
with db.transaction():
    db["key1"] = "value1"
    db["key2"] = "value2"
```

### メモリ使用量が多い

```python
# 大規模データベースにはbulk_loadを使用しない
# デフォルトの遅延ロードを使用
db = NanaSQLite("large.db", bulk_load=False)
```

### パフォーマンスが遅い

```python
# 一括書き込みにはバッチ操作を使用
data = {f"key_{i}": value for i in range(10000)}
db.batch_update(data)  # 個別書き込みよりはるかに高速
```

## まとめ

学習内容:
- ✅ 基本的なCRUD操作
- ✅ 複雑なネストデータの扱い
- ✅ パフォーマンス最適化（bulk_load、バッチ操作）
- ✅ Pydantic統合
- ✅ 直接SQLクエリ
- ✅ エラーハンドリング
- ✅ 一般的な使用パターン

NanaSQLiteを楽しんでコーディングしてください！
