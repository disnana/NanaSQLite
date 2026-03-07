# バリデーションガイド

[validkit-py](https://github.com/disnana/Validkit) と組み合わせることで、NanaSQLite は SQLite に書き込む前にすべての値をスキーマ検証できます。

このガイドでは、最近追加された `validator` / `coerce` 機能の実践的な使い方をまとめます。パラメータの完全な仕様は [NanaSQLite API リファレンス](./api_sync.md) を参照してください。

## どんなときに使うか

バリデーションは次のようなケースで役立ちます。

- 不正なレコードを保存前に弾きたい
- テーブルごとのデータ構造を一貫させたい
- `"42"` のような文字列入力を型付きの値へ安全に変換したい
- サブテーブルごとに異なるスキーマを適用したい

## インストール

バリデーション機能を有効にするには、extra 付きでインストールします。

```bash
pip install nanasqlite[validation]
```

実行時には、オプション依存が利用可能かどうかを確認できます。

```python
from nanasqlite import HAS_VALIDKIT

if HAS_VALIDKIT:
    print("validkit-py が利用可能です")
else:
    print("nanasqlite[validation] をインストールしてください")
```

## 基本的なスキーマ検証

`validator` に validkit のスキーマを渡します。

```python
from validkit import v
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

schema = {
    "name": v.str(),
    "age": v.int().range(0, 150),
    "active": v.bool(),
}

db = NanaSQLite("users.db", validator=schema)

db["alice"] = {"name": "Alice", "age": 30, "active": True}  # OK

try:
    db["bob"] = {"name": "Bob", "age": "invalid", "active": True}
except NanaSQLiteValidationError as exc:
    print(f"バリデーション失敗: {exc}")
    print("DB には何も書き込まれていません")
```

## `coerce` による自動変換

`coerce=True` を指定すると、validkit-py が返した変換済みの値を NanaSQLite が保存します。ただし、実際に変換を行うにはフィールド側でも `.coerce()` を指定する必要があります。

```python
from validkit import v
from nanasqlite import NanaSQLite

schema = {
    "age": v.int().coerce(),
    "score": v.float().coerce(),
}

db = NanaSQLite("scores.db", validator=schema, coerce=True)
db["player1"] = {"age": "20", "score": "9.5"}

print(db["player1"])  # {"age": 20, "score": 9.5}
```

フィールド側で `.coerce()` を指定していない場合、`coerce=True` だけでは変換されません。

```python
from validkit import v
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

schema = {"age": v.int()}
db = NanaSQLite("bad.db", validator=schema, coerce=True)

try:
    db["player1"] = {"age": "20"}
except NanaSQLiteValidationError:
    print("フィールドバリデーターが文字列入力を拒否します")
```

## テーブルごとのバリデーション

サブテーブルごとに別々のスキーマを適用できます。子テーブルは親のスキーマを自動継承することも可能です。

```python
from validkit import v
from nanasqlite import NanaSQLite

user_schema = {"name": v.str(), "age": v.int()}
score_schema = {"player": v.str(), "score": v.float().range(0.0, 100.0)}

db = NanaSQLite("app.db", validator=user_schema)

users_db = db.table("users")  # user_schema を継承
scores_db = db.table("scores", validator=score_schema)
cache_db = db.table("cache", validator=None)  # ここでは無効化

users_db["u1"] = {"name": "Alice", "age": 30}
scores_db["s1"] = {"player": "Alice", "score": 98.5}
cache_db["raw"] = {"anything": "goes"}
```

テーブル単位の `coerce` も同じ考え方です。

```python
from validkit import v
from nanasqlite import NanaSQLite

db = NanaSQLite("app.db")
coerce_schema = {"age": v.int().coerce()}
coerce_db = db.table("users_import", validator=coerce_schema, coerce=True)
coerce_db["u2"] = {"age": "31"}  # {"age": 31} として保存
```

## `batch_update()` とバリデーション

`validator` が設定されている場合、`batch_update()` は書き込み前にバッチ全体を検証します。1件でも失敗すると、全件が拒否されます。

```python
from validkit import v
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

schema = {"name": v.str(), "age": v.int()}
db = NanaSQLite("batch.db", validator=schema)

try:
    db.batch_update({
        "u1": {"name": "Alice", "age": 30},
        "u2": {"name": "Bob", "age": "bad"},
    })
except NanaSQLiteValidationError:
    print("アトミックに失敗し、何も書き込まれません")
```

## エラーハンドリングのポイント

- ユーザー入力を扱う箇所では `NanaSQLiteValidationError` を捕捉する
- スキーマはそのテーブルを所有するコードの近くに置く
- 構造の決まらないテーブルでは `validator=None` を明示する
- 自動変換は、意図的に正規化したい入力形式にだけ使う

例外処理のパターンは [エラーハンドリングガイド](./error_handling.md) を参照してください。
