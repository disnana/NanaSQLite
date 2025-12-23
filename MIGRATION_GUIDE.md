# NanaSQLite v1.2.0 Migration Guide / 移行ガイド

This document explains how to migrate from NanaSQLite v1.1.x to v1.2.0 and highlights the major changes.
このドキュメントでは、NanaSQLite v1.1.x から v1.2.0 への移行方法と主な変更点について説明します。

## ⚠️ Breaking Changes / 破壊的変更

### Strict Connection Management / 接続管理の厳格化
In v1.2.0, child instances (created via `db.table()`) are invalidated when the parent instance is closed.
v1.2.0では、親インスタンスがクリーンアップ（`close()`）されると、それに関連付けられた子インスタンス（`db.table()` で作成したもの）も無効化されます。

**Previous Behavior / 以前の挙動:**
Child instances might remain functional or exhibit unstable behavior after the parent was closed.
親を閉じた後も子インスタンスが動作し続けるか、不安定な挙動を示すことがありました。

**New Behavior / 新しい挙動:**
Operations on invalidated child instances will raise a `NanaSQLiteClosedError`.
無効化された子インスタンスに対する操作は `NanaSQLiteClosedError` を送出します。

---

## 🔒 Security Enhancements / セキュリティ強化

### SQL Expression Validation / SQL式の検証
The new `strict_sql_validation` parameter controls how the library handles potentially unauthorized SQL functions in clauses like `order_by`, `group_by`, and `columns`.
新しい `strict_sql_validation` パラメータは、`order_by`、`group_by`、`columns` などの句に含まれる未許可のSQL関数の扱いを制御します。

- **`strict=False` (Default)**: Emits a `UserWarning`. / `UserWarning` を発行します。
- **`strict=True`**: Raises a `NanaSQLiteValidationError`. / `NanaSQLiteValidationError` を送出します。

### ReDoS Protection / ReDoS対策
A new `max_clause_length` (default: 1000) limits the length of dynamic SQL clauses to prevent Regular Expression Denial of Service attacks.
動的なSQL句の長さを制限する `max_clause_length` (デフォルト: 1000) が導入され、ReDoS攻撃を防止します。

---

## 🔄 Async API Consistency / 非同期APIの一貫性

`AsyncNanaSQLite` now supports `a`-prefixed aliases for all methods.
`AsyncNanaSQLite` は、すべてのメソッドに対して `a` プレフィックス付きのエイリアスをサポートするようになりました。

```python
# Before / 以前
await db.batch_update(data)
await db.to_dict()

# Recommended in v1.2.0 / v1.2.0での推奨
await db.abatch_update(data)
await db.ato_dict()
```
