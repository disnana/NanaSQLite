# クイックリファレンス

NanaSQLiteの主要な機能を素早く確認するためのチートシートです。

---

## クラス: NanaSQLite

```python
class NanaSQLite(db_path: str, table: str = "data", bulk_load: bool = False,
                 optimize: bool = True, cache_size_mb: int = 64)
```

SQLiteの永続化をdict形式のインターフェースで提供するラッパークラス。

### コンストラクタ引数

| 引数 | 型 | デフォルト | 説明 |
|-----------|------|---------|-------------|
| `db_path` | `str` | *必須* | SQLite データベースファイルへのパス |
| `table` | `str` | `"data"` | ストレージに使用するテーブル名 |
| `bulk_load` | `bool` | `False` | 初期化時に全データをメモリにロード |
| `optimize` | `bool` | `True` | パフォーマンス最適化を適用 |
| `cache_size_mb` | `int` | `64` | SQLiteのキャッシュサイズ (MB) |

---

## Dictインターフェース

### `__getitem__(key: str) -> Any`

キーで値を取得します。

```python
value = db["key"]
```

**例外:** キーが存在しない場合は `KeyError`。

---

### `__setitem__(key: str, value: Any) -> None`

キーで値を設定します。SQLiteに即座に永続化されます。

```python
db["key"] = {"data": "value"}
```

**サポート型:** `str`, `int`, `float`, `bool`, `None`, `list`, `dict`

---

### `__delitem__(key: str) -> None`

キーを削除します。SQLiteから即座に削除されます。

```python
del db["key"]
```

**例外:** キーが存在しない場合は `KeyError`。

---

### `__contains__(key: str) -> bool`

キーの存在を確認します。

```python
if "key" in db:
    print("存在します！")
```

---

## 主要メソッド

### `keys() -> list[str]`

すべてのキーを取得します。

### `get(key: str, default: Any = None) -> Any`

デフォルト値付きで値を取得します。

### `update(mapping: dict = None, **kwargs) -> None`

複数のキーを一度に更新します。一括更新には `batch_update()` を推奨します。

### `clear() -> None`

すべてのキーを削除します。

### `load_all() -> None`

すべてのデータをSQLiteからメモリキャッシュへロードします。

### `table(table_name: str) -> NanaSQLite`

サブテーブル用のインスタンスを取得します。接続とロックを共有します。

---

## 一括操作 (Batch Operations)

### `batch_update(mapping: dict) -> None`

トランザクション内で一括書き込みを行います。個別書き込みより10〜100倍高速です。

```python
db.batch_update({
    "key1": "value1",
    "key2": "value2"
})
```

### `batch_delete(keys: list[str]) -> None`

トランザクション内で一括削除を行います。

---

## パフォーマンス

### 書き込み速度

| メソッド | 速度 | 用途 |
|--------|-------|----------|
| `db[key] = value` | 高速 | 単一書き込み |
| `db.update({...})` | 高速 | 数個のキー |
| `db.batch_update({...})` | **最速** | 大量書き込み (100個〜) |

### 読み込み速度

| モード | 初期化時間 | 読み込み時間 | メモリ |
|------|-----------|-----------|--------|
| 遅延ロード (デフォルト) | **高速** | 低速 (初回のみ) | 低 |
| 一括ロード (Bulk) | 低速 | **高速** | 高 |

### 推奨事項

1. 頻繁に多くのキーを読み込む場合は `bulk_load=True` を使用する
2. 一括書き込みには `batch_update()` を使用する
3. 最善のパフォーマンスのために `optimize=True` (デフォルト) を維持する
