# 例外クラスリファレンス

NanaSQLite は操作の種類ごとに細分化された例外クラスを提供しています。

## 例外階層

```
NanaSQLiteError（基底クラス）
├── NanaSQLiteValidationError    # データ検証エラー
├── NanaSQLiteDatabaseError      # DB 操作エラー
├── NanaSQLiteTransactionError   # トランザクションエラー
├── NanaSQLiteConnectionError    # 接続エラー
│   └── NanaSQLiteClosedError    # クローズ済みエラー
├── NanaSQLiteLockError          # ロック取得エラー
└── NanaSQLiteCacheError         # キャッシュエラー
```

## 各例外クラスの詳細

### NanaSQLiteError

すべての NanaSQLite 例外の基底クラスです。

```python
from nanasqlite import NanaSQLiteError

try:
    db["key"]
except NanaSQLiteError as e:
    # NanaSQLite のすべてのエラーをキャッチ
    print(f"エラー: {e}")
```

### NanaSQLiteValidationError

データバリデーションに失敗した場合にスローされます。`validkit-py` によるスキーマ検証で使用されます。

```python
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

db = NanaSQLite("app.db", validator={"name": str, "age": int})

try:
    db["user1"] = {"name": "Alice", "age": "not_a_number"}
except NanaSQLiteValidationError as e:
    print(f"バリデーションエラー: {e}")
```

**発生する場面:**
- `__setitem__` でスキーマ検証に失敗した場合
- `batch_update()` でスキーマ検証に失敗した場合
- `batch_update_partial()` でスキーマ検証に失敗した場合

### NanaSQLiteDatabaseError

SQLite のデータベース操作中にエラーが発生した場合にスローされます。元の例外を `original_error` 属性で保持します。

```python
from nanasqlite import NanaSQLiteDatabaseError

try:
    db.execute("INVALID SQL STATEMENT")
except NanaSQLiteDatabaseError as e:
    print(f"DB エラー: {e}")
    if e.original_error:
        print(f"元のエラー: {e.original_error}")
```

**発生する場面:**
- 不正な SQL の実行
- テーブル/インデックスの作成失敗
- 暗号化データの復号失敗
- データのシリアライズ/デシリアライズ失敗

### NanaSQLiteTransactionError

トランザクション操作中にエラーが発生した場合にスローされます。

```python
from nanasqlite import NanaSQLiteTransactionError

try:
    db.begin_transaction()
    db.begin_transaction()  # ネストは不可
except NanaSQLiteTransactionError as e:
    print(f"トランザクションエラー: {e}")
```

**発生する場面:**
- トランザクションの二重開始
- トランザクション外での `commit()` / `rollback()` 呼び出し
- トランザクション中の `close()` 呼び出し

### NanaSQLiteConnectionError

データベース接続に関するエラーが発生した場合にスローされます。

```python
from nanasqlite import NanaSQLiteConnectionError

try:
    db = NanaSQLite("/invalid/path/db.sqlite")
except NanaSQLiteConnectionError as e:
    print(f"接続エラー: {e}")
```

**発生する場面:**
- データベースファイルへのアクセス不能
- 接続の確立失敗

### NanaSQLiteClosedError

クローズ済みのデータベースに対して操作を行おうとした場合にスローされます。`NanaSQLiteConnectionError` のサブクラスです。

```python
from nanasqlite import NanaSQLiteClosedError

db = NanaSQLite("app.db")
db.close()

try:
    db["key"] = "value"
except NanaSQLiteClosedError as e:
    print(f"クローズ済み: {e}")
```

**発生する場面:**
- `close()` 後の読み取り/書き込み操作
- 親インスタンスのクローズ後に子テーブルを操作

### NanaSQLiteLockError

データベースロックの取得に失敗した場合にスローされます。

```python
from nanasqlite import NanaSQLite, NanaSQLiteLockError

db = NanaSQLite("app.db", lock_timeout=5.0)

try:
    db["key"] = "value"
except NanaSQLiteLockError as e:
    print(f"ロックエラー: {e}")
```

**発生する場面:**
- `lock_timeout` 内にロックを取得できなかった場合
- 他のプロセスがデータベースをロックしている場合

### NanaSQLiteCacheError

キャッシュ操作中にエラーが発生した場合にスローされます。

```python
from nanasqlite import NanaSQLiteCacheError

try:
    db.clear_cache()
except NanaSQLiteCacheError as e:
    print(f"キャッシュエラー: {e}")
```

**発生する場面:**
- キャッシュの初期化失敗
- キャッシュ戦略の不整合

## エラーハンドリングのベストプラクティス

### 1. 具体的な例外をキャッチする

```python
from nanasqlite import (
    NanaSQLiteValidationError,
    NanaSQLiteDatabaseError,
    NanaSQLiteTransactionError,
    NanaSQLiteLockError,
    NanaSQLiteClosedError,
)

try:
    db["key"] = data
except NanaSQLiteValidationError:
    # データ形式の問題 → ユーザーに再入力を求める
    pass
except NanaSQLiteLockError:
    # ロック競合 → リトライ
    pass
except NanaSQLiteClosedError:
    # 接続切れ → 再接続
    pass
except NanaSQLiteDatabaseError:
    # DB 操作失敗 → ログ記録
    pass
```

### 2. 基底クラスでまとめてキャッチ

```python
from nanasqlite import NanaSQLiteError

try:
    db["key"] = data
except NanaSQLiteError as e:
    # すべての NanaSQLite エラーを一括処理
    logger.error(f"NanaSQLite error: {e}")
```

### 3. トランザクションでのエラーハンドリング

```python
try:
    with db.transaction():
        db["key1"] = "value1"
        db["key2"] = "value2"
except NanaSQLiteTransactionError:
    # トランザクション失敗 → 自動ロールバック済み
    pass
```

## インポート

すべての例外クラスは `nanasqlite` パッケージから直接インポートできます:

```python
from nanasqlite import (
    NanaSQLiteError,
    NanaSQLiteValidationError,
    NanaSQLiteDatabaseError,
    NanaSQLiteTransactionError,
    NanaSQLiteConnectionError,
    NanaSQLiteClosedError,
    NanaSQLiteLockError,
    NanaSQLiteCacheError,
)
```
