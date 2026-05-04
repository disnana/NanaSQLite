# Ultimate Hooks (汎用フック＆制約)

`NanaSQLite` v1.5.0 から導入された **Ultimate Hooks** は、データベースのあらゆる操作（書き込み・読み込み・削除）をインターセプトし、独自のロジックや制約を適用するための汎用アーキテクチャです。

従来の `validator` 引数によるバリデーションも、内部的にはこのフック機構を利用して動作しています。

::: tip 推奨
独自のバリデーションロジックや Pydantic との統合が必要な場合は、従来の `validator` よりも Ultimate Hooks の使用を強く推奨します。
:::

## ライフサイクルイベント

フックは以下の 5 つのイベントに応答できます：

- `before_write(key, value)`: DB への書き込み（`set`, `update`, `batch_update`等）の直前に実行。値を変換して返すか、例外を投げて書き込みを拒否できます。
- `on_write_success(key, value, old_value)`: DB への書き込みが正常に完了した直後に実行。インデックスの更新など、書き込み成功時のみ実行したい処理に適しています。
- `after_read(key, value)`: DB からの読み込み（`get`, `items`等）の直後、アプリケーションに値を返す前に実行。値を変換して返せます。
- `before_delete(key)`: DB からの削除（`del`, `pop`等）の直前に実行。例外を投げて削除を拒否できます。
- `on_delete_success(key, old_value)`: DB からの削除が正常に完了した直後に実行。インデックスの破棄などに適しています。

## 標準フック (Standard Hooks)

すぐに使える便利なフックが `nanasqlite.hooks` モジュールに用意されています。

### UniqueHook
特定のフィールドの一意性を保証します。

```python
from nanasqlite.hooks import UniqueHook

# "email" フィールドの値がテーブル全体で重複しないことを保証
db.add_hook(UniqueHook("email"))

db["user1"] = {"email": "alice@example.com"}
db["user2"] = {"email": "alice@example.com"} # NanaSQLiteValidationError
```

### CheckHook
カスタム関数による値の検証を行います。SQLite の `CHECK` 制約のコード版です。

```python
from nanasqlite.hooks import CheckHook

# 年齢が 18 歳以上であることを検証
db.add_hook(CheckHook(lambda k, v: v.get("age", 0) >= 18, "Age must be >= 18"))
```

### ForeignKeyHook
他のテーブルとの参照整合性をチェックします。

```python
from nanasqlite.hooks import ForeignKeyHook

orders = db.table("orders")
users = db.table("users")

# orders の "user_id" が users テーブルのキーとして存在することを保証
orders.add_hook(ForeignKeyHook("user_id", users))
```

### PydanticHook
Pydantic モデルとのシームレスな統合を提供します。書き込み時にモデルで検証し、読み込み時に自動的に Pydantic インスタンスに変換します。

```python
from pydantic import BaseModel
from nanasqlite.hooks import PydanticHook

class User(BaseModel):
    name: str
    age: int

db.add_hook(PydanticHook(User))

db["u1"] = {"name": "Nana", "age": 20}
user = db["u1"]
print(type(user)) # <class 'User'>
print(user.name)  # Nana
```

## カスタムフックの作成

`NanaHook` プロトコルを実装することで、独自のフックを作成できます。

```python
class MyLoggerHook:
    def before_write(self, key, value):
        print(f"Writing {key}")
        return value # 変換が必要ない場合はそのまま返す

db.add_hook(MyLoggerHook())
```

## 注意事項

- **パフォーマンス**: フックはすべての操作で実行されるため、重い処理を行うと全体のパフォーマンスに影響します。
- **互換性**: 従来の `validator` 引数を使用すると、内部的に自動で `ValidkitHook` が追加されます。これらは共存可能です。
