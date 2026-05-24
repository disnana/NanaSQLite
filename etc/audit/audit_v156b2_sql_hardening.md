# v1.5.6b2 監査メモ: SQL 式検証の追加強化

作成日: 2026-05-24

## 対象

- `src/nanasqlite/core.py`
- `src/nanasqlite/async_core.py`
- `src/nanasqlite/v2_engine.py`
- `tests/test_audit_poc.py`
- `CHANGELOG.md`

## 結論

### SEC-01 — `query(..., columns=[...])` の列式でサブクエリを受け付ける

**判定:** 修正済み

`ORDER BY` / `GROUP BY` では `SELECT` や `FROM` などのサブクエリ系キーワードを拒否していたが、列式は関数や alias を許可する都合で同じ拒否条件が漏れていた。

修正では `_validate_expression(..., context="column")` にもサブクエリ系キーワードの拒否を適用した。`COUNT(*) AS total` のような通常の集計式は引き続き許可される。

### SEC-02 — `create_table()` の列型文字列でトップレベルのカンマを受け付ける

**判定:** 修正済み

列型文字列の文字種チェックは `DECIMAL(10,2)` のためにカンマを許可していたが、`TEXT, injected INTEGER` のようにトップレベルのカンマで列定義を追加できる余地があった。

修正では括弧の深さを走査し、カンマはバランスした括弧の内側だけ許可する。これにより `DECIMAL(10,2)` は維持し、列定義の割り込みを拒否する。

### BUG-02 — V2 DLQ にサイズ上限がない

**判定:** 修正済み

`etc/audit/audit_v154_pysentinel.md` で未対応として残っていた DLQ 上限について、現行コードでも `self.dlq.append(...)` のみで無制限に伸びる状態だった。

修正では `V2Engine(max_dlq_size=1000)` をデフォルトにし、上限到達時は最古エントリを破棄する。`V2Config(max_dlq_size=...)` と `NanaSQLite(..., v2_max_dlq_size=...)` / `AsyncNanaSQLite(..., v2_max_dlq_size=...)` から調整できる。`None` を指定した場合のみ従来通り無制限とする。

### SEC-03 — `V2Engine` 直利用時の KVS / DLQ 復旧 table_name 検証漏れ

**判定:** 修正済み

`NanaSQLite` 経由では `_sanitize_identifier()` 済みのテーブル名が渡るが、`V2Engine` 自体は公開クラスであり、`kvs_set()` / `kvs_delete()` にコンストラクタとは別の `table_name` を渡せた。さらに DLQ 復旧経路では `table_name` を f-string で SQL に連結していた。

修正では `V2Engine` 側に共通のテーブル名検証を追加し、KVS 入口、staging 参照、通常 flush、DLQ 復旧の各経路で quoted / unquoted の安全な識別子だけを受け付ける。DLQ 復旧時に unsafe table_name を見つけた場合は SQL を実行せず、その行を DLQ に隔離する。

### SEC-04 — `pragma()` の読み取り許可 PRAGMA をそのまま設定にも使える

**判定:** 修正済み

`etc/reports/claude.md` の `pragma()` SQL injection 指摘は、現行コードでは PRAGMA 名の allowlist と値検証が入っているため、直接の SQL injection としては古い。ただし読み取り用の `schema_version` / `table_info` / `index_list` / `database_list` なども、値を渡すと設定 SQL に進める設計だった。

修正では `allowed_pragmas` とは別に `writable_pragmas` を導入し、情報取得系や危険な PRAGMA は読み取りのみ許可する。既存の `foreign_keys` / `journal_mode` / `busy_timeout` などの設定用途は維持する。

## 回帰テスト

```powershell
python -m pytest tests\test_audit_poc.py::TestV140Sec01CreateTableInjection::test_top_level_comma_in_column_type_blocked tests\test_audit_poc.py::TestV156Sec01ColumnSubqueryInjection tests\test_audit_poc.py::TestQual02V154DLQEntryDataclass::test_dlq_max_size_evicts_oldest_entry tests\test_audit_poc.py::TestQual02V154DLQEntryDataclass::test_v2_config_passes_max_dlq_size tests\test_audit_poc.py::TestQual02V154DLQEntryDataclass::test_v2_engine_kvs_set_rejects_unsafe_table_name tests\test_audit_poc.py::TestQual02V154DLQEntryDataclass::test_v2_engine_dlq_recovery_rejects_unsafe_table_name tests\test_security.py::TestSQLInjectionProtection::test_read_only_pragma_cannot_be_set -q
```
