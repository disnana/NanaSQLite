# APIリファレンス

NanaSQLiteの完全なAPIドキュメント。

---

## クラス: NanaSQLite

```python
class NanaSQLite(db_path: str, table: str = "data", bulk_load: bool = False,
                 optimize: bool = True, cache_size_mb: int = 64)
```

dict風インターフェースでSQLite永続化を実現するラッパークラス。

### コンストラクタパラメータ

| パラメータ | 型 | デフォルト | 説明 |
|-----------|------|---------|-------------|
| `db_path` | `str` | *必須* | SQLiteデータベースファイルのパス |
| `table` | `str` | `"data"` | ストレージに使用するテーブル名 |
| `bulk_load` | `bool` | `False` | 初期化時に全データをメモリにロード |
| `optimize` | `bool` | `True` | パフォーマンス最適化を適用 |
| `cache_size_mb` | `int` | `64` | SQLiteキャッシュサイズ（MB） |

### 使用例

```python
# 基本
db = NanaSQLite("mydata.db")

# 一括ロード付き
db = NanaSQLite("mydata.db", bulk_load=True)

# カスタムテーブル
db = NanaSQLite("app.db", table="users")

# カスタムキャッシュサイズ
db = NanaSQLite("mydata.db", cache_size_mb=128)
```

---

## dictインターフェース

### `__getitem__(key: str) -> Any`

キーで値を取得。

```python
value = db["key"]
```

**例外:** キーが存在しない場合 `KeyError`

---

### `__setitem__(key: str, value: Any) -> None`

キーで値を設定。即座にSQLiteに永続化。

```python
db["key"] = {"data": "value"}
```

**サポートされる型:** `str`, `int`, `float`, `bool`, `None`, `list`, `dict`

---

### `__delitem__(key: str) -> None`

キーを削除。即座にSQLiteから削除。

```python
del db["key"]
```

**例外:** キーが存在しない場合 `KeyError`

---

### `__contains__(key: str) -> bool`

キーの存在確認。

```python
if "key" in db:
    print("存在します！")
```

---

### `__len__() -> int`

キーの数を取得。

```python
count = len(db)
```

---

### `__iter__() -> Iterator[str]`

キーをイテレート。

```python
for key in db:
    print(key)
```

---

## dictメソッド

### `keys() -> list[str]`

全キーを取得。

```python
all_keys = db.keys()
# ['key1', 'key2', 'key3']
```

---

### `values() -> list[Any]`

全値を取得。一括ロードをトリガー。

```python
all_values = db.values()
# [value1, value2, value3]
```

---

### `items() -> list[tuple[str, Any]]`

全キー・値ペアを取得。一括ロードをトリガー。

```python
all_items = db.items()
# [('key1', value1), ('key2', value2)]

# dictに変換
data = dict(db.items())
```

---

### `get(key: str, default: Any = None) -> Any`

デフォルト値付きで値を取得。

```python
value = db.get("key")  # 見つからない場合None
value = db.get("key", "default")  # 見つからない場合"default"
```

---

### `pop(key: str, *default) -> Any`

値を取得して削除。

```python
value = db.pop("key")  # 見つからない場合KeyError
value = db.pop("key", "default")  # 見つからない場合"default"
```

---

### `update(mapping: dict = None, **kwargs) -> None`

複数キーを一度に更新。

```python
db.update({"a": 1, "b": 2})
db.update(c=3, d=4)
```

**注意:** 大量更新には `batch_update()` を推奨。

---

### `setdefault(key: str, default: Any = None) -> Any`

値を取得、存在しない場合はデフォルトを設定。

```python
value = db.setdefault("key", "default")
```

---

### `clear() -> None`

全キーを削除。

```python
db.clear()
assert len(db) == 0
```

---

## 特殊メソッド

### `load_all() -> None`

SQLiteから全データをメモリキャッシュにロード。

```python
db.load_all()
# 以降の読み込みはすべてメモリから
```

---

### `refresh(key: str = None) -> None`

データベースからキャッシュを更新。

```python
db.refresh("key")  # 単一キーを更新
db.refresh()       # キャッシュ全体をクリア
```

---

### `is_cached(key: str) -> bool`

キーがメモリキャッシュにあるか確認。

```python
if db.is_cached("key"):
    print("すでにロード済み！")
```

---

### `to_dict() -> dict`

データベース全体を通常のPython dictに変換。

```python
data = db.to_dict()
# {'key1': value1, 'key2': value2, ...}
```

---

### `close() -> None`

データベース接続を閉じる。

```python
db.close()
```

---

## バッチ操作

### `batch_update(mapping: dict) -> None`

トランザクションで一括書き込み（個別書き込みより10〜100倍高速）。

```python
db.batch_update({
    "key1": "value1",
    "key2": "value2",
    "key3": {"nested": "data"}
})
```

---

### `batch_delete(keys: list[str]) -> None`

トランザクションで一括削除。

```python
db.batch_delete(["key1", "key2", "key3"])
```

---

## コンテキストマネージャ

### `__enter__() / __exit__()`

`with`文で自動クリーンアップ。

```python
with NanaSQLite("mydata.db") as db:
    db["key"] = "value"
# 自動的にクローズ
```

---

## パフォーマンスノート

### 書き込みパフォーマンス

| メソッド | 速度 | ユースケース |
|----------|------|----------|
| `db[key] = value` | 高速 | 単一書き込み |
| `db.update({...})` | 高速 | 少数キー |
| `db.batch_update({...})` | **最速** | 大量書き込み（100+キー） |

### 読み込みパフォーマンス

| モード | 初期化時間 | 読み込み時間 | メモリ |
|--------|-----------|-----------|--------|
| 遅延ロード（デフォルト） | **高速** | 遅い（初回アクセス） | 少 |
| 一括ロード | 遅い | **高速** | 多 |

### 推奨事項

1. ほとんどのキーを頻繁に読む場合は `bulk_load=True` を使用
2. 大量書き込みには `batch_update()` を使用
3. 最高のパフォーマンスのため `optimize=True`（デフォルト）を維持
4. 大規模データベースでは `cache_size_mb` を増加
