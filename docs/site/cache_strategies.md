# キャッシュ戦略ガイド

NanaSQLite は複数のキャッシュ戦略を提供し、ユースケースに応じた最適なパフォーマンスを実現します。

## キャッシュタイプ一覧

| 戦略 | `CacheType` | 特徴 | 推奨用途 |
|------|-------------|------|----------|
| **無制限** | `UNBOUNDED` | 全データをメモリに保持 | 小〜中規模DB（デフォルト） |
| **LRU** | `LRU` | 最近使われていないデータを自動削除 | 大規模DB・メモリ制限あり |
| **TTL** | `TTL` | 一定時間経過後にデータを自動失効 | セッション・一時データ |

## 無制限キャッシュ（UNBOUNDED）

デフォルトのキャッシュ戦略です。全データをメモリ上に保持し、最速のアクセスを実現します。

```python
from nanasqlite import NanaSQLite

# デフォルト: 無制限キャッシュ
db = NanaSQLite("app.db")

# 明示的に指定する場合
db = NanaSQLite("app.db", cache_strategy="unbounded")
```

### 特徴
- 読み取りは O(1) のメモリアクセス
- データベースの全エントリがメモリに載る
- メモリ使用量はデータ量に比例して増加
- `bulk_load=True` で起動時に全データを一括ロード

```python
# 一括ロードで起動時に全データをキャッシュ
db = NanaSQLite("app.db", bulk_load=True)

# 後から全データをロードすることも可能
db.load_all()
```

### 注意点
- 大量のデータがある場合、メモリを大量に消費します
- データ件数が 10 万件を超える場合は LRU の使用を検討してください

## LRU キャッシュ

Least Recently Used（最近最も使われていない）データを自動的に削除するキャッシュです。

```python
from nanasqlite import NanaSQLite, CacheType

# LRU キャッシュ: 最大 1000 件を保持
db = NanaSQLite(
    "app.db",
    cache_strategy=CacheType.LRU,
    cache_size=1000,
)
```

### 動作の仕組み

1. キャッシュにデータがあれば即座に返す（ヒット）
2. キャッシュになければデータベースから読み取る（ミス）
3. キャッシュが `cache_size` に達すると、最も古いアクセスのデータを削除

```python
# LRU キャッシュの使用例
db = NanaSQLite("app.db", cache_strategy="lru", cache_size=500)

db["key1"] = "value1"  # キャッシュに追加
db["key2"] = "value2"  # キャッシュに追加

val = db["key1"]       # キャッシュヒット（高速）
val = db.get_fresh("key1")  # キャッシュをバイパスしてDBから直接読み取り
```

### 高速 LRU（lru-dict）

`lru-dict` パッケージがインストールされている場合、C 拡張による高速 LRU が自動的に使用されます。

```bash
pip install nanasqlite[speed]  # lru-dict + orjson をインストール
```

速度比較:

| 実装 | 読み取り速度 |
|------|-------------|
| 標準 LRU（OrderedDict） | 1x |
| FastLRU（lru-dict） | 約 2-3x |

### 推奨設定

| データ規模 | `cache_size` 推奨値 |
|-----------|-------------------|
| 〜1 万件 | 1,000 |
| 1 万〜10 万件 | 5,000 |
| 10 万件以上 | 10,000 |

## TTL キャッシュ

Time-To-Live（有効期限付き）キャッシュです。一定時間が経過すると自動的にデータが失効します。

```python
from nanasqlite import NanaSQLite, CacheType

# TTL キャッシュ: 60 秒で失効
db = NanaSQLite(
    "app.db",
    cache_strategy=CacheType.TTL,
    cache_ttl=60.0,         # 秒単位
)
```

### 動作の仕組み

1. データがキャッシュに追加されると、タイムスタンプが記録される
2. TTL 経過後、次のアクセス時にデータが失効（遅延削除方式）
3. 失効したデータはデータベースから再読み込みされる

```python
import time

db = NanaSQLite("app.db", cache_strategy="ttl", cache_ttl=30.0)

db["session"] = {"user": "alice", "token": "abc123"}

# 30 秒以内: キャッシュから返される
val = db["session"]  # 高速

time.sleep(31)

# 30 秒経過後: DB から再読み込み
val = db["session"]  # DB アクセスが発生
```

### TTL + サイズ制限

TTL キャッシュにもサイズ制限を追加できます:

```python
db = NanaSQLite(
    "app.db",
    cache_strategy="ttl",
    cache_ttl=300.0,     # 5 分で失効
    cache_size=2000,     # 最大 2000 件
)
```

### 推奨ユースケース

| シナリオ | `cache_ttl` 推奨値 |
|---------|-------------------|
| セッションストア | 300〜3600 秒 |
| API レスポンスキャッシュ | 30〜300 秒 |
| 設定ファイルキャッシュ | 3600 秒以上 |
| リアルタイムデータ | 1〜10 秒 |

## キャッシュ永続化 TTL

`cache_persistence_ttl=True` を指定すると、TTL が切れた際にコールバックを発火してデータベースへの書き戻しを行います。

```python
db = NanaSQLite(
    "app.db",
    cache_strategy="ttl",
    cache_ttl=60.0,
    cache_persistence_ttl=True,  # TTL 失効時にDB同期
)
```

## キャッシュ管理メソッド

### キャッシュの確認と操作

```python
# キーがキャッシュに存在するか確認
db.is_cached("key1")  # True / False

# キャッシュを全クリア
db.clear_cache()

# 全データをキャッシュにロード
db.load_all()

# 特定キーのキャッシュを更新
db.refresh("key1")

# キャッシュをバイパスして DB から直接取得
value = db.get_fresh("key1")
```

### バッチ操作とキャッシュ

バッチ操作はキャッシュも自動的に更新します:

```python
# バッチ更新（キャッシュも同時に更新）
db.batch_update({"k1": "v1", "k2": "v2", "k3": "v3"})

# バッチ取得（キャッシュヒットを最大化）
results = db.batch_get(["k1", "k2", "k3"])

# バッチ削除（キャッシュからも削除）
db.batch_delete(["k1", "k2"])
```

## 非同期でのキャッシュ利用

`AsyncNanaSQLite` でも同じキャッシュ戦略が利用できます:

```python
from nanasqlite import AsyncNanaSQLite, CacheType

async def main():
    db = AsyncNanaSQLite(
        "app.db",
        cache_strategy=CacheType.LRU,
        cache_size=1000,
    )

    await db.aset("key", "value")
    val = await db.aget("key")  # キャッシュヒット

    await db.aclear_cache()
    await db.aload_all()

    db.close()
```

## 戦略選択フローチャート

```
データ件数 < 1万件?
├─ Yes → UNBOUNDED（デフォルト）
└─ No
   ├─ データに有効期限が必要?
   │  ├─ Yes → TTL
   │  └─ No → LRU
   └─ メモリが十分にある?
      ├─ Yes → UNBOUNDED + bulk_load
      └─ No → LRU (cache_size を調整)
```

## パフォーマンス比較

| 操作 | UNBOUNDED | LRU | TTL |
|------|-----------|-----|-----|
| 読み取り（ヒット） | O(1) | O(1) | O(1) |
| 読み取り（ミス） | O(DB) | O(DB) | O(DB) |
| 書き込み | O(1) | O(1) | O(1) |
| メモリ使用量 | 高 | 制限付き | 制限付き |
| 初期ロード | `bulk_load` 対応 | 遅延ロード | 遅延ロード |
