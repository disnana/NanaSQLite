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

## 回帰テスト

```powershell
python -m pytest tests\test_audit_poc.py::TestV140Sec01CreateTableInjection::test_top_level_comma_in_column_type_blocked tests\test_audit_poc.py::TestV156Sec01ColumnSubqueryInjection tests\test_audit_poc.py::TestQual02V154DLQEntryDataclass::test_dlq_max_size_evicts_oldest_entry tests\test_audit_poc.py::TestQual02V154DLQEntryDataclass::test_v2_config_passes_max_dlq_size -q
```
