# NanaSQLite v1.5.3 プレリリース最終監査レポート（全ファイル対象）

**対象バージョン:** v1.5.3  
**監査日:** 2026-04-08  
**監査対象ファイル:**
- `src/nanasqlite/core.py`
- `src/nanasqlite/async_core.py`
- `src/nanasqlite/cache.py`
- `src/nanasqlite/utils.py`
- `src/nanasqlite/sql_utils.py`
- `src/nanasqlite/exceptions.py`
- `src/nanasqlite/v2_engine.py`
- `src/nanasqlite/hooks.py`
- `src/nanasqlite/protocols.py`
- `src/nanasqlite/compat.py`

---

## 総括テーブル

| カテゴリ | Critical | High | Medium | Low | 計 |
|---------|----------|------|--------|-----|-----|
| 不具合・潜在バグ | 0 | 0 | 0 | 0 | 0 |
| パフォーマンス | 0 | 0 | 0 | 0 | 0 |
| コード品質 | 0 | 0 | 0 | 3 | 3 |
| 脆弱性 | 0 | 0 | 0 | 0 | 0 |
| **合計** | **0** | **0** | **0** | **3** | **3** |

---

## 各発見事項

---

### QUAL-07 [Low] `core.py` — `get_table_schema()` 型アノテーション不正確

**ファイル:** `src/nanasqlite/core.py` L2679（修正前）

```python
def get_table_schema(self, table_name: str = None) -> list[dict]:
```

`table_name` は `None` を受け取れるが、型が `str` のみで `None` が許容されていないことを示している。  
`from __future__ import annotations` があるため実行時エラーにはならないが、型チェッカー（strict モード）および IDEの補完が不正確になる。

**修正案（適用済み）:**

```python
def get_table_schema(self, table_name: str | None = None) -> list[dict]:
```

---

### QUAL-08 [Low] `core.py` — `upsert()` `conflict_columns` 型アノテーション不正確

**ファイル:** `src/nanasqlite/core.py` L2829（修正前）

```python
def upsert(self, table_name: str | Any = None, data: Any = None, conflict_columns: list[str] = None) -> int | None:
```

`conflict_columns` はデフォルト `None` を受け取れるが型が `list[str]` のみ。

**修正案（適用済み）:**

```python
def upsert(..., conflict_columns: list[str] | None = None) -> int | None:
```

---

### QUAL-09 [Low] `async_core.py` — 複数メソッドで型アノテーション不正確

**ファイル:** `src/nanasqlite/async_core.py`（修正前）

以下のメソッドシグネチャで `= None` デフォルトを持つが `| None` が欠落していたパラメータ（合計 20 箇所）：

| メソッド | 影響パラメータ |
|---|---|
| `create_table()` | `primary_key: str` |
| `query()` | `table_name: str`, `columns: list[str]`, `where: str`, `order_by: str`, `limit: int`, `strict_sql_validation: bool`, `allowed_sql_functions: list[str]`, `forbidden_sql_functions: list[str]` |
| `query_with_pagination()` | `table_name: str`, `columns: list[str]`, `where: str`, `order_by: str`, `limit: int`, `offset: int`, `group_by: str`, `strict_sql_validation: bool`, `allowed_sql_functions: list[str]`, `forbidden_sql_functions: list[str]` |
| `count()` | `table_name: str`, `where: str`, `strict_sql_validation: bool`, `allowed_sql_functions: list[str]`, `forbidden_sql_functions: list[str]` |
| `aupsert()` | `conflict_columns: list[str]` |

**修正案（適用済み）:**

各パラメータを `T | None = None` 形式に修正。

---

## その他の点検結果

以下のモジュールは問題なし（Critical/High/Medium なし）：

| ファイル | 状態 |
|---|---|
| `cache.py` | 異常なし。`UnboundedCache.delete()` の BUG-03 修正済み。`TTLCache.is_cached()` ロジック正確。`create_cache()` 全3戦略をカバー。 |
| `utils.py` | 異常なし。`ExpiringDict` の BUG-02/04 修正済み。PERF-B 最適化済み。スケジューラスレッド安全に再起動。 |
| `sql_utils.py` | 異常なし。`sanitize_sql_for_function_scan()` ステートマシン正確。`_SAFE_SQL_CHARS` モジュールレベル frozenset で PERF-05 対応済み。 |
| `exceptions.py` | 異常なし。例外クラス階層明確。 |
| `v2_engine.py` | 異常なし。`_flush_pending` ロックによるフラッシュ重複防止正確。DLQ リカバリ正確。シャットダウン時 atexit 登録解除済み。 |
| `hooks.py` | 異常なし。ReDoS 検知パターンを適用。`_validate_regex_pattern()` 4 種の危険パターンをチェック。 |

---

## 推奨対応優先度

### 今バージョン（v1.5.3）で修正済み

| ID | 重要度 | 内容 | 対応状況 |
|---|---|---|---|
| QUAL-07 | Low | `core.py` `get_table_schema()` 型アノテーション不正確 | ✅ 修正済み |
| QUAL-08 | Low | `core.py` `upsert()` `conflict_columns` 型アノテーション不正確 | ✅ 修正済み |
| QUAL-09 | Low | `async_core.py` 複数メソッド 型アノテーション不正確（20 箇所） | ✅ 修正済み |

---

## 審査員コメント（PR レビュー）への回答

PR レビューで「`tuple | None` は Python 3.10 以上が必要」との指摘がありましたが、`core.py` および `async_core.py` の両ファイルは先頭で `from __future__ import annotations` を宣言しており、これによりすべてのアノテーションが実行時に評価されない文字列として扱われます。したがって PEP 604 の `X | Y` 構文は Python 3.9 でも問題なく動作します（Python 3.7 以降で利用可能な機能）。コードベース全体で既に同様のパターンが使われており、変更不要と判断しました。

---

## 全監査サイクル累積修正サマリー（v1.4.0 → v1.5.3）

| 監査版 | 主な修正 |
|---|---|
| v1.4.0 | SEC-01（SQL インジェクション）、BUG-01〜04（on_success/ExpiringDict/UnboundedCache/TOCTOU）、PERF-01〜06 |
| v1.5.0 | フックシステム、Pydantic サポート |
| v1.5.1 | QUAL 系 7 件、PERF 系 6 件 |
| v1.5.2 | UnboundedCache _absent_keys 移行、PERF-14〜17 |
| v1.5.3rc1 | PERF-07〜13（SQL 事前計算）、to_dict/values/items 最適化 |
| v1.5.3rc2 | BUG-01（setdefault）、PERF-14〜20（try/except 高速パス、_has_hooks） |
| v1.5.3rc3 | BUG-02/03（tx リーク、状態更新ロック外）、QUAL-03、PERF-21〜26/29 |
| v1.5.3rc4 | PERF-A〜D（lru_cache、ExpiringDict、vacuum、backup stat）、BUG-02〜04（utils）、SEC-02、QUAL-01、CodeQL |
| **v1.5.3 (最終)** | **PERF-E/F、QUAL-04〜09（型アノテーション全修正、async ガード統一）** |
