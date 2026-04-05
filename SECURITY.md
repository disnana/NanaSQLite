# セキュリティポリシー (Japanese)

## 脆弱性の報告

セキュリティ上の脆弱性を発見した場合は、公開Issueを立てず、**security@disnana.com** に直接ご連絡ください。

## サポート対象バージョン

現在、セキュリティアップデートを提供しているバージョンは以下の通りです。

| バージョン | サポート状況       |
| ---------- | ------------------ |
| >= v1.4.0  | :white_check_mark: |
| < v1.4.0   | :x:                |

---

## 既知の脆弱性・修正済み問題

### 1. `table` 引数経由のSQLインジェクション（v1.3.4 で修正済み）

**深刻度:** 重大 (Critical)

**概要:** 旧バージョンでは、`NanaSQLite` クラスの初期化時に渡す `table` 引数が適切にサニタイズされていませんでした。攻撃者は悪意のあるテーブル名（例: `"data; DROP TABLE users; --"`）を渡すことで、任意のSQLコマンドを実行できました。

**修正内容:** `__init__` および `table()` メソッドで `_sanitize_identifier` を使用し、英数字とアンダースコアのみを許可するよう実装しました。不正な識別子には `NanaSQLiteValidationError` を送出します。

### 2. `None` 値保存時のデータ消失（v1.3.4 で修正済み）

**深刻度:** 高 (High) ― データ整合性

**概要:** `None`（JSON `null`）を明示的に保存した場合（`db["key"] = None`）、データはSQLiteに正しく書き込まれます。しかし DB 再オープン後の遅延ロード時に、`__contains__` が値をキャッシュしないまま `_cached_keys` にキーを登録していたため、その後の `__getitem__` でキーが「値なし」と判定され `KeyError` が発生し、データが消失したように見えました。

**修正内容:**
- `_read_from_db` に `_NOT_FOUND` センチネルを導入して「キー不在」と「値が `None`」を区別しました。
- `__contains__` が SQLite に対して `SELECT 1 ... LIMIT 1` を発行し、このセンチネルを用いてキーの存在判定を行うことで、`None` 値が誤って「値なし」と解釈されないように変更しました。

### 3. `create_table()` のカラム型に対するSQLインジェクション脆弱性（v1.4.0 で修正済み）

**深刻度:** 重大 (Critical)

**概要:** APSW はセミコロン区切りの複数文を一度に実行するため、カラム型定義を通じて任意のSQLを実行可能でした。

**修正内容:** セミコロン (;)、ラインコメント (--)、ブロックコメント (/*) を含む文字列を拒否するバリデーションを追加しました。

## 組み込みのセキュリティ機能

NanaSQLite は複数のセキュリティ層を備えています（v1.2.0以降）。

- **厳格なSQL検証 (Strict SQL Validation):** 未許可のSQL関数の実行を防止します。
- **ReDoS対策 (ReDoS Protection):** SQL句の最大文字数制限により過負荷攻撃を防ぎます。
- **保存データの暗号化 (Encryption at Rest):** `cryptography` ライブラリによる `AES-GCM`、`ChaCha20Poly1305`、`Fernet` をサポートします。

\pagebreak

# Security Policy (English)

## Reporting a Vulnerability

If you discover a security vulnerability, please do **NOT** open a public issue. Instead, contact us at **security@disnana.com**.

## Supported Versions

We currently provide security updates for the following versions:

| Version    | Supported          |
| ---------- | ------------------ |
| >= v1.3.4  | :white_check_mark: |
| < v1.3.4   | :x:                |

---

## Known Vulnerabilities & Fixed Issues

### 1. SQL Injection via `table` Parameter (Fixed in v1.3.4)

**Severity:** Critical

**Description:** In older versions, the `table` parameter in the `NanaSQLite` class initialization was not properly sanitized. An attacker could execute arbitrary SQL commands by passing a malicious table name (e.g., `"data; DROP TABLE users; --"`).

**Fix:** `_sanitize_identifier` is now applied to the `table` argument during `__init__` and `table()` calls, allowing only alphanumeric characters and underscores. Invalid identifiers raise `NanaSQLiteValidationError`.

### 2. Data Loss on `None` Value Storage (Fixed in v1.3.4)

**Severity:** High (Data Integrity)

**Description:** When explicitly saving `None` (JSON `null`) as a value (`db["key"] = None`), the value was correctly persisted to SQLite. However, upon lazy loading after reopening the database, `__contains__` registered the key in `_cached_keys` without loading the value into `_data`. A subsequent `__getitem__` call found the key in `_cached_keys` but not in `_data`, causing a `KeyError` and apparent data loss.

**Fix/Mitigation:**
- A sentinel object (`_NOT_FOUND`) was introduced in the internal read mechanism to accurately distinguish between missing records and explicitly stored `None` values.
- `__contains__` now performs a dedicated existence query without mutating the in-memory caches, avoiding inconsistent cache state while correctly handling explicitly stored `None` values in combination with the `_NOT_FOUND` sentinel.

## Built-in Security Features

NanaSQLite is designed with multiple security layers (v1.2.0+):

- **Strict SQL Validation:** Prevents execution of unauthorized SQL functions.
- **ReDoS Protection:** Maximum clause length limits prevent regex denial-of-service attacks.
- **Encryption at Rest:** Data-at-rest encryption via `AES-GCM`, `ChaCha20Poly1305`, and `Fernet` through the `cryptography` library.
