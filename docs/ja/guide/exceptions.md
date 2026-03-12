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

## NanaSQLiteError

すべての NanaSQLite 例外の基底クラスです。

## NanaSQLiteValidationError

データバリデーションに失敗した場合（`validkit-py` スキーマ検証）。

## NanaSQLiteDatabaseError

SQLite 操作中のエラー。`original_error` 属性で元の例外を保持。

## NanaSQLiteTransactionError

トランザクションの二重開始、外部での commit/rollback 呼び出し。

## NanaSQLiteConnectionError

データベース接続エラー。

### NanaSQLiteClosedError

`NanaSQLiteConnectionError` のサブクラス。クローズ済みDBへの操作。

## NanaSQLiteLockError

`lock_timeout` 内にロック取得できなかった場合。

## NanaSQLiteCacheError

キャッシュ操作中のエラー。

## インポート

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
