# NanaSQLite ドキュメント

dict風インターフェースでSQLite永続化を実現するライブラリ。

## 目次

- [コンセプト](#コンセプト)
- [インストール](#インストール)
- [クイックスタート](#クイックスタート)
- [使い方ガイド](#使い方ガイド)
- [APIリファレンス](reference.md)

---

## コンセプト

### 課題

Pythonのdictは高速で便利ですが、揮発性です。プログラムが終了すると全てのデータが失われます。従来のデータベースソリューションはSQLの学習、接続管理、シリアライズの手動処理が必要です。

### 解決策

**NanaSQLite**は標準のPython dictを透過的なSQLite永続化でラップし、このギャップを埋めます：

```
┌─────────────────────────────────────────────────────┐
│                  Pythonコード                        │
│                                                      │
│    db["user"] = {"name": "Nana", "age": 20}         │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│                   NanaSQLite                         │
│  ┌───────────────┐     ┌───────────────────────┐    │
│  │ メモリキャッシュ │ ←→  │ APSW SQLite バックエンド │    │
│  │ (Python dict) │     │ (永続ストレージ)         │    │
│  └───────────────┘     └───────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

### 設計原則

1. **即時書き込み**: すべての書き込み操作は即座にSQLiteに永続化
2. **スマートリード**: データはオンデマンド（遅延）または一括でロード
3. **メモリ優先**: 一度ロードしたデータはメモリから高速に提供
4. **設定不要**: パフォーマンス最適化された合理的なデフォルト

### パフォーマンス最適化

NanaSQLiteはデフォルトで以下のSQLite最適化を適用します：

| 設定 | 効果 |
|------|------|
| **WALモード** | 書き込み速度: 30ms+ → 1ms以下 |
| **synchronous=NORMAL** | 安全 + 高速 |
| **mmap (256MB)** | メモリマップドI/Oで読み込み高速化 |
| **cache_size (64MB)** | SQLiteページキャッシュ拡大 |
| **temp_store=MEMORY** | 一時テーブルをRAMに |

---

## インストール

```bash
pip install nanasqlite
```

**必要条件:**
- Python 3.9以上
- APSW（自動でインストール）

---

## クイックスタート

### 基本的な使い方

```python
from nanasqlite import NanaSQLite

# データベースを作成または開く
db = NanaSQLite("mydata.db")

# データを保存（即座に永続化）
db["config"] = {"theme": "dark", "language": "ja"}
db["users"] = ["Alice", "Bob", "Charlie"]
db["count"] = 42

# データを取得
print(db["config"]["theme"])  # 'dark'
print(db["users"][0])          # 'Alice'
print(db["count"])             # 42

# 存在確認
if "config" in db:
    print("設定が存在します！")

# データを削除
del db["count"]

# 終了時にクローズ
db.close()
```

### コンテキストマネージャ

```python
with NanaSQLite("mydata.db") as db:
    db["key"] = "value"
    # 終了時に自動的にクローズ
```

### 一括ロードで高速化

```python
# 起動時に全データをメモリにロード
db = NanaSQLite("mydata.db", bulk_load=True)

# 以降の読み込みはすべてメモリから（超高速）
for key in db.keys():
    print(db[key])  # データベースクエリなし！
```

---

## 使い方ガイド

### サポートされるデータ型

NanaSQLiteはすべてのJSON直列化可能な型をサポート：

```python
db["string"] = "Hello, World!"
db["integer"] = 42
db["float"] = 3.14159
db["boolean"] = True
db["null"] = None
db["list"] = [1, 2, 3, "four", 5.0]
db["dict"] = {"nested": {"deep": {"value": 123}}}
```

### ネスト構造

深くネストした構造を完全サポート（30階層以上でテスト済み）：

```python
db["deep"] = {
    "level1": {
        "level2": {
            "level3": {
                "data": [1, 2, {"key": "value"}]
            }
        }
    }
}

# ネストしたデータにアクセス
print(db["deep"]["level1"]["level2"]["level3"]["data"][2]["key"])  # 'value'
```

### dictメソッド

標準的なdictメソッドをすべて利用可能：

```python
# keys, values, items
print(db.keys())    # ['key1', 'key2', ...]
print(db.values())  # [value1, value2, ...]
print(db.items())   # [('key1', value1), ...]

# デフォルト値付きget
value = db.get("missing", "default")

# pop（取得して削除）
value = db.pop("key")

# 複数キーを更新
db.update({"a": 1, "b": 2, "c": 3})

# デフォルト値を設定
db.setdefault("new_key", "default_value")

# 全削除
db.clear()

# 通常のdictに変換
regular_dict = db.to_dict()
```

### バッチ操作

大量書き込みにはバッチメソッドで10〜100倍高速化：

```python
# バッチ更新（トランザクション使用）
db.batch_update({
    f"key_{i}": {"data": i} for i in range(10000)
})

# バッチ削除
db.batch_delete(["key_0", "key_1", "key_2"])
```

### キャッシュ管理

```python
# キーがメモリキャッシュにあるか確認
if db.is_cached("key"):
    print("すでにメモリにロード済み！")

# データベースから強制再読み込み
db.refresh("key")  # 単一キー
db.refresh()       # 全キー

# すべてをメモリにロード
db.load_all()
```

### 複数テーブル

```python
# 同じデータベースで異なるテーブルを使用
users_db = NanaSQLite("app.db", table="users")
config_db = NanaSQLite("app.db", table="config")

users_db["alice"] = {"name": "Alice", "age": 30}
config_db["theme"] = "dark"
```

### Pydantic互換性 (v1.0.3rc3+)

PydanticモデルをそのままNanaSQLiteに保存・取得できます：

```python
from pydantic import BaseModel
from nanasqlite import NanaSQLite

# Pydanticモデルの定義
class User(BaseModel):
    name: str
    age: int
    email: str

# データベース作成
db = NanaSQLite("mydata.db")

# Pydanticモデルを保存
user = User(name="Nana", age=20, email="nana@example.com")
db.set_model("user", user)

# Pydanticモデルとして取得
retrieved_user = db.get_model("user", User)
print(retrieved_user.name)  # "Nana"
print(retrieved_user.age)   # 20
```

### 直接SQL実行 (v1.0.3rc3+)

SQLiteの全機能を活用するために、カスタムSQLを直接実行できます：

```python
# SELECT文の実行
cursor = db.execute("SELECT key, value FROM data WHERE key LIKE ?", ("user%",))
for row in cursor:
    print(row)

# 複数パラメータで一括実行
db.execute_many(
    "INSERT INTO custom (id, name) VALUES (?, ?)",
    [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
)

# 便利な取得メソッド
row = db.fetch_one("SELECT * FROM data WHERE key = ?", ("config",))
rows = db.fetch_all("SELECT * FROM data ORDER BY key")
```

### SQLiteラッパー関数 (v1.0.3rc3+)

SQLiteを簡単に使えるラッパー関数を提供：

```python
# テーブル作成
db.create_table("users", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT NOT NULL",
    "email": "TEXT UNIQUE",
    "age": "INTEGER"
})

# インデックス作成
db.create_index("idx_users_email", "users", ["email"], unique=True)

# シンプルなクエリ
results = db.query(
    table_name="users",
    columns=["name", "age"],
    where="age > ?",
    parameters=(20,),
    order_by="name ASC",
    limit=10
)

# テーブル管理
if db.table_exists("users"):
    print("usersテーブルが存在します")

tables = db.list_tables()
print(f"データベース内のテーブル: {tables}")
```

### 追加のSQLiteラッパー関数 (v1.0.3rc4+)

より多くの便利な機能を追加：

```python
# データ操作
rowid = db.sql_insert("users", {"name": "Alice", "email": "alice@example.com", "age": 25})
count = db.sql_update("users", {"age": 26}, "name = ?", ("Alice",))
count = db.sql_delete("users", "age < ?", (18,))

# UPSERT（存在すれば更新、なければ挿入）
db.upsert("users", {"id": 1, "name": "Alice", "age": 25})

# レコード数と存在確認
total = db.count("users")
adults = db.count("users", "age >= ?", (18,))
if db.exists("users", "email = ?", ("alice@example.com",)):
    print("ユーザーが存在します")

# ページネーションとグループ化
page2 = db.query_with_pagination("users", limit=10, offset=10, order_by="id ASC")
stats = db.query_with_pagination("orders",
    columns=["user_id", "COUNT(*) as count"],
    group_by="user_id"
)

# スキーマ管理
db.alter_table_add_column("users", "phone", "TEXT")
schema = db.get_table_schema("users")
indexes = db.list_indexes("users")
db.drop_table("old_table", if_exists=True)
db.drop_index("old_index", if_exists=True)

# ユーティリティ
db.vacuum()  # データベース最適化
size = db.get_db_size()  # DBサイズ（バイト）
exported = db.export_table_to_dict("users")  # テーブルエクスポート
db.import_from_dict_list("users", data_list)  # 一括インポート
rowid = db.get_last_insert_rowid()  # 最後のROWID
mode = db.pragma("journal_mode")  # PRAGMA取得

# トランザクション制御
with db.transaction():
    db.sql_insert("users", {"name": "Alice"})
    db.sql_insert("users", {"name": "Bob"})
    # 自動的にコミット、例外時はロールバック
```

### パフォーマンスチューニング

```python
# 最適化を無効化（非推奨）
db = NanaSQLite("mydata.db", optimize=False)

# カスタムキャッシュサイズ（デフォルト: 64MB）
db = NanaSQLite("mydata.db", cache_size_mb=128)
```

---

## 次のステップ

- [APIリファレンス](reference.md) - 詳細なメソッドドキュメント
