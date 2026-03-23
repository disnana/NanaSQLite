# NanaSQLite v1.4.0 プレリリース監査レポート

> 対象バージョン: 1.4.0 (dev2)  
> 監査日: 2026-03-12  
> 対象ファイル: src/nanasqlite/ 配下すべて (core.py, async_core.py, cache.py, utils.py, sql_utils.py, exceptions.py, v2_engine.py)

---

## 総括

| カテゴリ | Critical | High | Medium | Low | 計 |
|---|---|---|---|---|---|
| 脆弱性 | 1 | — | — | — | 1 |
| 不具合・潜在バグ | — | 1 | 2 | 1 | 4 |
| 高速化の余地 | — | — | — | 1 | 1 |
| 改善点（コード品質） | — | — | — | 1 | 1 |
| **合計** | **1** | **1** | **2** | **3** | **7** |

---

## 1. 脆弱性

### SEC-01 [Critical] `create_table()` のカラム型に対するバリデーション欠如 — SQLインジェクション

**ファイル:** `core.py` L1864-1867

```python
for col_name, col_type in columns.items():
    safe_col_name = self._sanitize_identifier(col_name)
    column_defs.append(f"{safe_col_name} {col_type}")
```

`alter_table_add_column()` にはホワイトリスト正規表現によるバリデーションが適用されているが、`create_table()` にはカラム型に対するバリデーションが一切存在しない。APSW はセミコロン区切りの複数文を一度に実行するため、`"TEXT); DELETE FROM victim WHERE 1=1; --"` のようなペイロードで任意のSQLを実行可能。実際にデータの削除が確認済み。

**修正案:** `create_table()` の `columns` dict の値に対して、セミコロン (`;`)、ラインコメント (`--`)、ブロックコメント (`/*`) を含む文字列を拒否するバリデーションを追加する。`alter_table_add_column()` のような厳格なホワイトリストは `NOT NULL`, `DEFAULT`, `CHECK()`, `REFERENCES` 等の制約が使えなくなるため、ブラックリスト方式の危険パターン検出が適切。

---

## 2. 不具合・潜在バグ

### BUG-01 [High] V2Engine `on_success` コールバックがトランザクションコミット前に呼ばれる

**ファイル:** `v2_engine.py` L305-335

```python
def _process_strict_queue(self, cursor):
    while not self._strict_queue.empty():
        task = self._strict_queue.get_nowait()
        try:
            # ... execute task ...
            if task.on_success:
                task.on_success()  # ← COMMIT前に呼ばれる
        except Exception as e:
            if task.on_error:
                task.on_error(e)
            self._add_to_dlq(...)
            raise  # → ROLLBACK
```

`_process_strict_queue()` はトランザクション内で呼ばれるが、各タスクの `on_success` コールバックは COMMIT 前に呼ばれる。同一バッチ内の後続タスクが失敗すると ROLLBACK されるが、先行タスクの呼び出し元は既に成功通知を受け取っている。`core.py` の `execute()` はこのコールバックで `event.set()` して呼び出し元に復帰を通知するため、データの書き込みが成功したと誤認するリスクがある。

**修正案:** 成功コールバックを即座に呼ばず、成功したタスクリストに蓄積し、トランザクション COMMIT 成功後にまとめて `on_success` を呼ぶ。

---

### BUG-02 [Medium] `AsyncNanaSQLite.table()` で子インスタンスに v2/キャッシュ/暗号化属性が設定されない

**ファイル:** `async_core.py` L1362-1391

```python
async_sub_db = object.__new__(AsyncNanaSQLite)
async_sub_db._db_path = self._db_path
# ... (一部の属性のみ設定)
# _v2_mode, _cache_strategy, _encryption_key 等が未設定
```

`table()` メソッドは `object.__new__()` で `__init__` をバイパスして子インスタンスを生成するが、`_v2_mode`, `_flush_mode`, `_flush_interval`, `_flush_count`, `_v2_chunk_size`, `_cache_strategy`, `_cache_size`, `_cache_ttl`, `_cache_persistence_ttl`, `_encryption_key`, `_encryption_mode` が設定されていない。子インスタンスでこれらの属性にアクセスすると `AttributeError` が発生する。

**修正案:** 不足している属性を親インスタンスから継承して設定する。

---

### BUG-03 [Medium] v2モードで `execute()` 経由の SELECT クエリが常に空結果を返す

**ファイル:** `core.py` L1696-1734

```python
if self._v2_mode and self._v2_engine:
    # ... enqueue strict task and wait ...
    with self._acquire_lock():
        return self._connection.cursor()  # ← 空のカーソル
```

v2モードでは `execute()` がバックグラウンドタスクとしてSQLを実行するが、戻り値は新規作成された空のカーソル。SELECT クエリの結果はバックグラウンドワーカーで消費され、呼び出し元には空の結果が返される。`query()`, `fetch_one()`, `fetch_all()` がすべて影響を受ける。

**修正案:** SELECT文（読み取りクエリ）を検出し、v2バックグラウンドキューを経由せずメインスレッドで直接実行する。

---

### BUG-04 [Low] `_shared_query_impl()` のエイリアス抽出ロジックが `_extract_column_aliases()` と重複

**ファイル:** `async_core.py` L1643-1649

`_shared_query_impl` のフォールバック分岐にあるインラインのエイリアス抽出ロジックが、`NanaSQLite._extract_column_aliases()` ヘルパーメソッドと機能が重複している。現在のところ動作上の問題はないが、一方のロジックのみが修正された場合に不整合が生じるリスクがある。

**修正案:** 重複コードを `_extract_column_aliases()` の呼び出しに置き換える。

---

## 3. 高速化の余地

### PERF-01 [Low] `batch_get()` の `IN (...)` 句がプレースホルダ数無制限

**ファイル:** `core.py` L1023

```python
placeholders = ",".join(["?"] * len(missing_keys))
sql = f"SELECT key, value FROM {self._safe_table} WHERE key IN ({placeholders})"
```

大量のキーリストを渡すと、SQLite の `SQLITE_MAX_VARIABLE_NUMBER` 制限（デフォルト999〜32766）に抵触する可能性がある。キー数が数千を超える規模の `batch_get()` 呼び出しでランタイムエラーとなり得る。

**修正案:** キーリストを 500 件ずつのチャンクに分割して複数回クエリを実行する。チャンク分割により若干のオーバーヘッドが発生するが、大量キーでの安定性が向上する。

---

## 4. 改善点（コード品質）

### QUAL-01 [Low] `update()` メソッドの型アノテーション不整合

**ファイル:** `core.py` L1054

```python
def update(self, mapping: dict = None, **kwargs) -> None:
```

`mapping` パラメータのデフォルト値が `None` だが型アノテーションが `dict` のみとなっている。`None` がデフォルト値として許容されているにもかかわらず、型が `Optional[dict]` または `dict | None` でないため、静的型チェッカー（mypy 等）で警告が発生する可能性がある。

**修正案:** 型アノテーションを `mapping: dict | None = None` に修正する。

---

## 推奨対応優先度

### リリース前に修正すべき

| ID | 概要 |
|---|---|
| SEC-01 | `create_table()` カラム型のSQLインジェクション — 任意SQL実行が可能 |
| BUG-01 | V2Engine `on_success` コールバックの早期呼び出し — データ整合性リスク |
| BUG-03 | v2モードで SELECT クエリが常に空結果を返す — 機能不全 |

### 次バージョンで対応可能

| ID | 概要 |
|---|---|
| BUG-02 | `AsyncNanaSQLite.table()` の属性欠落 — v2/キャッシュ/暗号化使用時に `AttributeError` |
| PERF-01 | `batch_get()` の `IN` 句プレースホルダ数制限 — 大量キーでのエラー防止 |

### 将来的な改善

| ID | 概要 |
|---|---|
| BUG-04 | エイリアス抽出ロジックの重複解消 |
| QUAL-01 | `update()` の型アノテーション不整合修正 |

---

# NanaSQLite v1.4.1dev3 プレリリース監査レポート

> 対象バージョン: 1.4.1dev3  
> 監査日: 2026-03-24  
> 対象ファイル: src/nanasqlite/ 配下すべて (core.py, async_core.py, cache.py, utils.py, sql_utils.py, exceptions.py)

---

## 総括

| カテゴリ | Critical | High | Medium | Low | 計 |
|---|---|---|---|---|---|
| 脆弱性 | — | — | — | — | 0 |
| 不具合・潜在バグ | — | 1 | — | — | 1 |
| 高速化の余地 | — | — | — | 1 | 1 |
| 改善点（コード品質） | — | — | — | 1 | 1 |
| **合計** | **—** | **1** | **—** | **2** | **3** |

---

## 1. 脆弱性

該当なし。現バージョンにおいて重大なセキュリティ脆弱性は検出されなかった。

---

## 2. 不具合・潜在バグ

### BUG-01 [High] `upsert()` でデータ辞書を第1引数に渡した場合の AttributeError

**ファイル:** `core.py`

```python
# 問題のある呼び出し例
db.upsert({"id": 1, "name": "Alice"}, conflict_columns=["id"])
```

`upsert` メソッドは複数の呼び出しパターンを内部で振り分けるが、`(data_dict, conflict_columns)` パターンで呼ばれた際に、内部変数 `target_data` ではなく元の `data` 変数（この呼び出しパターンでは `None`）の `.keys()` を参照するコードパスが存在する。その結果 `AttributeError: 'NoneType' object has no attribute 'keys'` が発生し、処理が中断する。非同期版 `aupsert` も内部で `core.py` の `upsert` を経由するため同様の影響を受ける。

**POC:** `etc/poc/poc_bug01_v141_upsert_attributeerror.py` — 再現確認済み (exit code 1)

**修正案:** 問題箇所の `data.keys()` を `target_data.keys()` に変更する。

**対処提案:**

```python
# core.py — upsert() 内の conflict_columns 処理部分
# Before (バグあり)
updated_cols = [col for col in data.keys() if col not in conflict_columns]

# After (修正済み)
updated_cols = [col for col in target_data.keys() if col not in conflict_columns]
```

修正箇所は1行のみで、後方互換性・パフォーマンスへの影響はない。合わせて `tests/test_audit_poc.py` に以下のテストケースを追加することを推奨する。

```python
class TestV141Bug01UpsertAttributeError:
    def test_upsert_with_data_dict_and_conflict_columns(self, db):
        db.create_table("t", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
        # 修正前はここで AttributeError が発生していた
        db.upsert({"id": 1, "name": "Alice"}, conflict_columns=["id"])
        rows = db.query("t")
        assert rows[0]["name"] == "Alice"
```

---

## 3. 高速化の余地

### PERF-01 [Low] LRU/TTLキャッシュ使用時のネガティブキャッシュ欠如

`LRU` および `TTL` キャッシュ戦略では、値が存在する場合のみキャッシュされる。`UNBOUNDED` 戦略が `_cached_keys` セットで「存在しないことが確認されたキー」を追跡しているのと異なり、LRU/TTL では存在しないキーへのアクセスのたびに SQLite クエリが発行される。

**修正案:** LRU/TTL でもネガティブキャッシュ（存在しないキーの追跡）を導入する。

---

## 4. 改善点（コード品質）

### QUAL-01 [Low] `ExpiringDict` スケジューラスレッド停止処理の向上

`clear()` および `__del__` における `scheduler_thread.join(timeout=...)` でタイムアウトが発生した場合の後処理が不十分で、警告ログのみで終了する。デーモンスレッドのため致命的ではないが、テスト環境での `ResourceWarning` 発生の原因となり得る。

**修正案:** タイムアウト後のスレッド状態をより適切に管理する。

---

## 推奨対応優先度

### リリース前に修正すべき

| ID | 概要 |
|---|---|
| BUG-01 | `upsert()` の AttributeError — 特定パターンで確実にクラッシュ |

### 将来的な改善

| ID | 概要 |
|---|---|
| PERF-01 | LRU/TTLキャッシュのネガティブキャッシュ欠如 |
| QUAL-01 | `ExpiringDict` スケジューラスレッド停止処理の向上 |
