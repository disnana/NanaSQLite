# クイックリファレンス

NanaSQLiteの主要な機能を素早く確認するためのチートシートです。

---

## クラス: NanaSQLite

```python
class NanaSQLite(db_path: str, table: str = "data", bulk_load: bool = False,
                 optimize: bool = True, cache_size_mb: int = 64,
                 strict_sql_validation: bool = True,
                 allowed_sql_functions: list[str] | None = None,
                 forbidden_sql_functions: list[str] | None = None,
                 max_clause_length: int | None = 1000)
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
| `strict_sql_validation` | `bool` | `True` | 厳格なSQLバリデーションを有効にする (v1.2.0+) |
| `allowed_sql_functions` | `list` | `None` | 許可するSQL関数のリスト |
| `forbidden_sql_functions` | `list` | `None` | 禁止するSQL関数のリスト |
| `max_clause_length` | `int` | `1000` | WHERE句などの最大文字数制限 |

### 使用例

```python
# 基本的な使用方法
db = NanaSQLite("mydata.db")

# 一括ロードを有効化
db = NanaSQLite("mydata.db", bulk_load=True)

# カスタムテーブル名の指定
db = NanaSQLite("app.db", table="users")

# キャッシュサイズの変更
db = NanaSQLite("mydata.db", cache_size_mb=128)
```

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

### `__len__() -> int`

キーの総数を取得します。

```python
count = len(db)
```

---

### `__iter__() -> Iterator[str]`

キーを反復処理します。

```python
for key in db:
    print(key)
```

---

## Dictメソッド

### `keys() -> list[str]`

すべてのキーを取得します。

```python
all_keys = db.keys()
# ['key1', 'key2', 'key3']
```

---

### `values() -> list[Any]`

すべての値を取得します。一括ロードがトリガーされます。

```python
all_values = db.values()
# [value1, value2, value3]
```

---

### `items() -> list[tuple[str, Any]]`

すべてのキーと値のペアを取得します。一括ロードがトリガーされます。

```python
all_items = db.items()
# [('key1', value1), ('key2', value2)]

# 標準の dict に変換する場合
data = dict(db.items())
```

---

### `get(key: str, default: Any = None) -> Any`

デフォルト値付きで値を取得します。

```python
value = db.get("key")  # 見つからない場合は None
value = db.get("key", "default")  # 見つからない場合は "default"
```

---

### `pop(key: str, *default) -> Any`

値を取得し、同時に削除します。

```python
value = db.pop("key")  # 見つからない場合は KeyError
value = db.pop("key", "default")  # 見つからない場合は "default"
```

---

### `update(mapping: dict = None, **kwargs) -> None`

複数のキーを一度に更新します。

```python
db.update({"a": 1, "b": 2})
db.update(c=3, d=4)
```

**注意:** 大量更新には `batch_update()` を推奨します。

---

### `setdefault(key: str, default: Any = None) -> Any`

値を取得します。キーが存在しない場合はデフォルト値を設定して返します。

```python
value = db.setdefault("key", "default")
```

---

### `clear() -> None`

すべてのキーを削除します。

```python
db.clear()
assert len(db) == 0
```

---

## 特殊メソッド

### `load_all() -> None`

すべてのデータをSQLiteからメモリキャッシュへロードします。

```python
db.load_all()
# 以降の読み取りはすべてメモリから行われます
```

---

### `refresh(key: str = None) -> None`

データベースの内容でキャッシュを更新します。

```python
db.refresh("key")  # 特定のキーを更新
db.refresh()       # キャッシュ全体をクリア（再読み込み待ち状態へ）
```

---

### `is_cached(key: str) -> bool`

キーがメモリキャッシュに存在するか確認します。

```python
if db.is_cached("key"):
    print("ロード済みです！")
```

---

### `to_dict() -> dict`

データベース全体の内容を標準の Python dict として返します。

```python
data = db.to_dict()
# {'key1': value1, 'key2': value2, ...}
```

---

### `close() -> None`

データベース接続を閉じます。

```python
db.close()
```

**注意:** `table()` メソッドで作成されたサブテーブルインスタンスは接続を共有しているため、最初に作成されたインスタンス（オーナー）のみが実際に接続を閉じます。

---

### `table(table_name: str) -> NanaSQLite` *(v1.1.0+)*

サブテーブル用のインスタンスを取得します。接続とロックを共有します。

```python
# メインインスタンスの作成
db = NanaSQLite("app.db", table="main")

# サブテーブル用インスタンスの取得（接続を共有）
users_db = db.table("users")
config_db = db.table("config")

# 各テーブルに独立して保存
users_db["alice"] = {"name": "Alice", "age": 30}
config_db["theme"] = "dark"
```

**引数:**
- `table_name` (str): 取得するテーブル名

**戻り値:**
- `NanaSQLite`: 指定されたテーブルを操作する新しいインスタンス

**メリット:**
- **スレッドセーフ**: 複数のスレッドからの並行書き込みに対応
- **メモリ効率**: SQLiteの接続を再利用
- **キャッシュの分離**: テーブルごとに独立したメモリキャッシュを保持

---

## 一括操作 (Batch Operations)

### `batch_update(mapping: dict) -> None`

トランザクション内で一括書き込みを行います。個別書き込みより10〜100倍高速です。

```python
db.batch_update({
    "key1": "value1",
    "key2": "value2",
    "key3": {"nested": "data"}
})
```

---

### `batch_delete(keys: list[str]) -> None`

トランザクション内で一括削除を行います。

```python
db.batch_delete(["key1", "key2", "key3"])
```

---

## コンテキストマネージャ

### `__enter__() / __exit__()`

`with` 文による自動的なクリーンアップをサポートします。

```python
with NanaSQLite("mydata.db") as db:
    db["key"] = "value"
# 自動的に close() が呼ばれます
```

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
4. 大規模なデータベースでは `cache_size_mb` を増やす
