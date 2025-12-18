# エラーハンドリングガイド

NanaSQLite v1.1.0以降では、統一されたカスタム例外クラスを提供し、エラーハンドリングをより予測可能で扱いやすくしています。

## 目次

1. [カスタム例外クラス](#カスタム例外クラス)
2. [例外の階層構造](#例外の階層構造)
3. [一般的なエラーシナリオ](#一般的なエラーシナリオ)
4. [エラーハンドリングのベストプラクティス](#エラーハンドリングのベストプラクティス)
5. [デバッグとトラブルシューティング](#デバッグとトラブルシューティング)

---

## カスタム例外クラス

NanaSQLiteは以下のカスタム例外クラスを提供しています：

### 基底例外

#### `NanaSQLiteError`

すべてのNanaSQLite固有の例外の基底クラス。

```python
from nanasqlite import NanaSQLite, NanaSQLiteError

try:
    db = NanaSQLite("mydata.db")
    # 何らかの操作
except NanaSQLiteError as e:
    print(f"NanaSQLiteエラーが発生しました: {e}")
```

### 特定の例外

#### `NanaSQLiteValidationError`

不正な入力値やパラメータに対して発生します。

**発生するケース**:
- 不正なテーブル名やカラム名
- 不正なSQL識別子
- パラメータの型エラー

```python
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

db = NanaSQLite("mydata.db")

try:
    # 不正なテーブル名（数字で始まる）
    db.create_table("123invalid", {"id": "INTEGER"})
except NanaSQLiteValidationError as e:
    print(f"バリデーションエラー: {e}")
    # 出力: Invalid identifier '123invalid': must start with letter or underscore...
```

#### `NanaSQLiteDatabaseError`

SQLite/APSWのデータベース操作で発生するエラーをラップします。

**発生するケース**:
- データベースロック
- ディスク容量不足
- ファイル権限エラー
- SQL構文エラー

```python
from nanasqlite import NanaSQLite, NanaSQLiteDatabaseError

db = NanaSQLite("mydata.db")

try:
    # 不正なSQL
    db.execute("INVALID SQL STATEMENT")
except NanaSQLiteDatabaseError as e:
    print(f"データベースエラー: {e}")
    # 元のAPSWエラーにアクセス
    if e.original_error:
        print(f"元のエラー: {e.original_error}")
```

#### `NanaSQLiteTransactionError`

トランザクション関連のエラー。

**発生するケース**:
- ネストしたトランザクションの試み
- トランザクション外でのコミット/ロールバック
- トランザクション中の接続クローズ

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

db = NanaSQLite("mydata.db")

try:
    db.begin_transaction()
    db.begin_transaction()  # ネストは不可
except NanaSQLiteTransactionError as e:
    print(f"トランザクションエラー: {e}")
    # 出力: Transaction already in progress...
```

#### `NanaSQLiteConnectionError`

データベース接続の作成や管理で発生するエラー。

**発生するケース**:
- 閉じられた接続の使用
- 接続の初期化失敗
- 孤立した子インスタンスの使用

```python
from nanasqlite import NanaSQLite, NanaSQLiteConnectionError

db = NanaSQLite("mydata.db")
db.close()

try:
    db["key"] = "value"  # 閉じた接続を使用
except NanaSQLiteConnectionError as e:
    print(f"接続エラー: {e}")
    # 出力: Database connection is closed
```

#### `NanaSQLiteLockError`

ロック取得エラー（将来の機能拡張用）。

**発生するケース**:
- ロック取得タイムアウト
- デッドロック検出

#### `NanaSQLiteCacheError`

キャッシュ関連エラー（将来の機能拡張用）。

**発生するケース**:
- キャッシュサイズ超過
- キャッシュの不整合

---

## 例外の階層構造

```
Exception
└── NanaSQLiteError (基底クラス)
    ├── NanaSQLiteValidationError
    ├── NanaSQLiteDatabaseError
    ├── NanaSQLiteTransactionError
    ├── NanaSQLiteConnectionError
    ├── NanaSQLiteLockError
    └── NanaSQLiteCacheError
```

すべてのNanaSQLite例外は`NanaSQLiteError`を継承しているため、包括的なエラーハンドリングが可能です：

```python
from nanasqlite import NanaSQLite, NanaSQLiteError

try:
    db = NanaSQLite("mydata.db")
    # 様々な操作
    db.begin_transaction()
    db["key"] = "value"
    db.commit()
except NanaSQLiteError as e:
    # すべてのNanaSQLite例外をキャッチ
    print(f"エラーが発生しました: {e}")
```

---

## 一般的なエラーシナリオ

### 1. データベースロック

**問題**: 複数のプロセスまたはスレッドが同時にデータベースにアクセスしようとしている。

```python
from nanasqlite import NanaSQLite, NanaSQLiteDatabaseError

db = NanaSQLite("mydata.db")

try:
    db["key"] = "value"
except NanaSQLiteDatabaseError as e:
    if "database is locked" in str(e).lower():
        print("データベースがロックされています。リトライします...")
        # リトライロジック
```

**解決策**:
1. WALモードを有効にする（デフォルトで有効）
2. `busy_timeout`を設定する
3. トランザクションを適切に管理する

```python
db = NanaSQLite("mydata.db", optimize=True)  # WALモード有効
db.pragma("busy_timeout", 5000)  # 5秒待機
```

### 2. トランザクションのネスト

**問題**: SQLiteはネストしたトランザクションをサポートしていません。

```python
from nanasqlite import NanaSQLite, NanaSQLiteTransactionError

db = NanaSQLite("mydata.db")

try:
    db.begin_transaction()
    # ... 何らかの操作 ...
    db.begin_transaction()  # エラー！
except NanaSQLiteTransactionError as e:
    print(f"トランザクションエラー: {e}")
    db.rollback()
```

**解決策**: トランザクション状態を確認する

```python
if not db.in_transaction():
    db.begin_transaction()
# または、コンテキストマネージャを使用
with db.transaction():
    db["key"] = "value"
    # 自動的にコミット/ロールバック
```

### 3. 閉じた接続の使用

**問題**: 接続を閉じた後に操作を試みる。

```python
from nanasqlite import NanaSQLite, NanaSQLiteConnectionError

db = NanaSQLite("mydata.db")
db.close()

try:
    db["key"] = "value"
except NanaSQLiteConnectionError as e:
    print(f"接続が閉じられています: {e}")
```

**解決策**: コンテキストマネージャを使用する

```python
with NanaSQLite("mydata.db") as db:
    db["key"] = "value"
    # 自動的にクローズされる
```

### 4. 孤立した子インスタンス

**問題**: 親インスタンスを閉じた後、子インスタンスを使用しようとする。

```python
from nanasqlite import NanaSQLite, NanaSQLiteConnectionError

main_db = NanaSQLite("app.db")
sub_db = main_db.table("users")

main_db.close()  # 親を閉じる

try:
    sub_db["key"] = "value"  # エラー！
except NanaSQLiteConnectionError as e:
    print(f"親接続が閉じられています: {e}")
```

**解決策**: コンテキストマネージャで親と子を管理する

```python
with NanaSQLite("app.db") as main_db:
    sub_db = main_db.table("users")
    sub_db["key"] = "value"
    # 親が閉じるまで子も有効
```

### 5. 不正な識別子

**問題**: SQLインジェクション対策として、識別子は厳格に検証されます。

```python
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

db = NanaSQLite("mydata.db")

try:
    # スペースや特殊文字を含む識別子
    db.create_table("my table", {"id": "INTEGER"})
except NanaSQLiteValidationError as e:
    print(f"不正な識別子: {e}")
```

**解決策**: 有効な識別子を使用する

```python
# 有効: 英数字とアンダースコアのみ、数字で始まらない
db.create_table("my_table", {"id": "INTEGER"})
db.create_table("table123", {"id": "INTEGER"})
db.create_table("_private_table", {"id": "INTEGER"})
```

---

## エラーハンドリングのベストプラクティス

### 1. 具体的な例外をキャッチする

特定のエラーに対して適切な処理を行うため、具体的な例外をキャッチします。

```python
from nanasqlite import (
    NanaSQLite,
    NanaSQLiteValidationError,
    NanaSQLiteDatabaseError,
    NanaSQLiteConnectionError,
)

db = NanaSQLite("mydata.db")

try:
    db.create_table("users", {"id": "INTEGER", "name": "TEXT"})
    db.sql_insert("users", {"id": 1, "name": "Alice"})
except NanaSQLiteValidationError as e:
    print(f"入力データが不正です: {e}")
except NanaSQLiteDatabaseError as e:
    print(f"データベースエラー: {e}")
    if e.original_error:
        print(f"詳細: {e.original_error}")
except NanaSQLiteConnectionError as e:
    print(f"接続エラー: {e}")
```

### 2. コンテキストマネージャを使用する

リソースの自動管理のため、コンテキストマネージャを使用します。

```python
# ✅ 推奨
with NanaSQLite("mydata.db") as db:
    db["key"] = "value"
    # 例外が発生しても自動的にクローズ

# ❌ 非推奨
db = NanaSQLite("mydata.db")
try:
    db["key"] = "value"
finally:
    db.close()  # 手動でクローズが必要
```

### 3. トランザクションで一貫性を保つ

複数の操作をアトミックに実行するため、トランザクションを使用します。

```python
from nanasqlite import NanaSQLite, NanaSQLiteError

db = NanaSQLite("mydata.db")
db.create_table("accounts", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT",
    "balance": "REAL"
})

try:
    with db.transaction():
        # 口座Aから引き出し
        db.sql_update("accounts", {"balance": 900.0}, "id = ?", (1,))
        # 口座Bに入金
        db.sql_update("accounts", {"balance": 1100.0}, "id = ?", (2,))
        # 両方成功すれば自動的にコミット
except NanaSQLiteError as e:
    # 例外が発生すれば自動的にロールバック
    print(f"トランザクション失敗: {e}")
```

### 4. ロギングを活用する

エラーの追跡と診断のため、ロギングを使用します。

```python
import logging
from nanasqlite import NanaSQLite, NanaSQLiteError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    db = NanaSQLite("mydata.db")
    db["key"] = "value"
    logger.info("データを正常に保存しました")
except NanaSQLiteError as e:
    logger.error(f"エラーが発生しました: {e}", exc_info=True)
```

### 5. エラーメッセージをユーザーに適切に伝える

技術的な詳細を隠し、ユーザーフレンドリーなメッセージを提供します。

```python
from nanasqlite import NanaSQLite, NanaSQLiteValidationError, NanaSQLiteDatabaseError

def save_user_data(user_data):
    try:
        db = NanaSQLite("users.db")
        db.create_table("users", {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT",
            "email": "TEXT UNIQUE"
        })
        db.sql_insert("users", user_data)
        return {"success": True, "message": "ユーザーを登録しました"}
    except NanaSQLiteValidationError as e:
        return {"success": False, "message": "入力データが不正です"}
    except NanaSQLiteDatabaseError as e:
        if "unique" in str(e).lower():
            return {"success": False, "message": "このメールアドレスは既に登録されています"}
        return {"success": False, "message": "データベースエラーが発生しました"}
    except Exception as e:
        return {"success": False, "message": "予期しないエラーが発生しました"}
```

---

## デバッグとトラブルシューティング

### エラー情報の取得

`NanaSQLiteDatabaseError`は元のAPSWエラーを保持しています：

```python
from nanasqlite import NanaSQLite, NanaSQLiteDatabaseError

try:
    db = NanaSQLite("mydata.db")
    db.execute("INVALID SQL")
except NanaSQLiteDatabaseError as e:
    print(f"エラーメッセージ: {e}")
    if e.original_error:
        print(f"元のAPSWエラー: {e.original_error}")
        print(f"エラータイプ: {type(e.original_error)}")
```

### トランザクション状態の確認

```python
db = NanaSQLite("mydata.db")

print(f"トランザクション中: {db.in_transaction()}")  # False

db.begin_transaction()
print(f"トランザクション中: {db.in_transaction()}")  # True

db.commit()
print(f"トランザクション中: {db.in_transaction()}")  # False
```

### 接続状態の確認

```python
db = NanaSQLite("mydata.db")
print(f"接続の所有者: {db._is_connection_owner}")
print(f"接続が閉じられている: {db._is_closed}")

sub_db = db.table("users")
print(f"子の接続の所有者: {sub_db._is_connection_owner}")  # False
print(f"親が閉じられている: {sub_db._parent_closed}")  # False

db.close()
print(f"親が閉じられた後の子: {sub_db._parent_closed}")  # True
```

### デバッグモードの有効化

Pythonの`-v`フラグや`PYTHONVERBOSE`環境変数でデバッグ情報を表示：

```bash
# Windowsの場合
$env:PYTHONVERBOSE=1
python your_script.py

# Linux/Macの場合
PYTHONVERBOSE=1 python your_script.py
```

### トレースバックの詳細表示

```python
import traceback
from nanasqlite import NanaSQLite, NanaSQLiteError

try:
    db = NanaSQLite("mydata.db")
    # ... 操作 ...
except NanaSQLiteError as e:
    print("エラーが発生しました:")
    print(traceback.format_exc())
```

---

## 非同期版のエラーハンドリング

非同期版（`AsyncNanaSQLite`）でも同じ例外クラスが使用されます：

```python
import asyncio
from nanasqlite import AsyncNanaSQLite, NanaSQLiteError

async def main():
    try:
        async with AsyncNanaSQLite("mydata.db") as db:
            await db.aset("key", "value")
    except NanaSQLiteError as e:
        print(f"エラー: {e}")

asyncio.run(main())
```

---

## まとめ

- **統一された例外**: すべてのNanaSQLite例外は`NanaSQLiteError`を継承
- **具体的なエラーハンドリング**: 特定の例外をキャッチして適切に処理
- **コンテキストマネージャ**: リソースの自動管理
- **トランザクション**: データの一貫性を保つ
- **ロギング**: エラーの追跡と診断

適切なエラーハンドリングにより、堅牢で信頼性の高いアプリケーションを構築できます。

