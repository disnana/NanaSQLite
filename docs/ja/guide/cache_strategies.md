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

db = NanaSQLite("app.db")  # デフォルト: 無制限
db = NanaSQLite("app.db", cache_strategy="unbounded")  # 明示的
```

## LRU キャッシュ

最近最も使われていないデータを自動的に削除するキャッシュです。

```python
from nanasqlite import NanaSQLite, CacheType

db = NanaSQLite("app.db", cache_strategy=CacheType.LRU, cache_size=1000)
```

`lru-dict` がインストールされている場合、C 拡張による高速 LRU が自動使用されます:

```bash
pip install nanasqlite[speed]
```

## TTL キャッシュ

一定時間経過後にデータが自動失効するキャッシュです。

```python
from nanasqlite import NanaSQLite, CacheType

db = NanaSQLite("app.db", cache_strategy=CacheType.TTL, cache_ttl=60.0)
```

## キャッシュ永続化 TTL

```python
db = NanaSQLite("app.db", cache_strategy="ttl", cache_ttl=60.0, cache_persistence_ttl=True)
```

## キャッシュ管理メソッド

```python
db.is_cached("key1")           # キャッシュ存在確認
db.clear_cache()               # キャッシュ全クリア
db.load_all()                  # 全データをキャッシュにロード
db.refresh("key1")             # 特定キーのキャッシュ更新
value = db.get_fresh("key1")   # キャッシュバイパスしてDB取得
```

## パフォーマンス比較

| 操作 | UNBOUNDED | LRU | TTL |
|------|-----------|-----|-----|
| 読み取り（ヒット） | O(1) | O(1) | O(1) |
| 読み取り（ミス） | O(DB) | O(DB) | O(DB) |
| 書き込み | O(1) | O(1) | O(1) |
| メモリ使用量 | 高 | 制限付き | 制限付き |
