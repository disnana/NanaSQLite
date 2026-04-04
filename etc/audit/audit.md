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

# NanaSQLite v1.4.1 最終リリース監査レポート

> 対象バージョン: 1.4.1  
> 監査日: 2026-03-25  
> 対象ファイル: src/nanasqlite/ 配下すべて (core.py, async_core.py, cache.py, utils.py, sql_utils.py, exceptions.py)

---

## 総括

| カテゴリ | Critical | High | Medium | Low | 計 |
|---|---|---|---|---|---|
| 脆弱性 | — | — | 1 | — | 1 |
| 不具合・潜在バグ | — | 2 | — | — | 2 |
| 高速化の余地 | — | — | — | 1 | 1 |
| 改善点（コード品質） | — | — | — | 3 | 3 |
| **合計** | **—** | **2** | **1** | **4** | **7** |

---

## 1. 脆弱性

### SEC-02 [Medium] `core.py` における `column_type` バリデーションの ReDoS 脆弱性

**ファイル:** `core.py` (v1.4.1)

SonarQubeが指摘していた `column_type` バリデーションにおける `[\w ]*` の正規表現パターンが、評価文字列によってはバックトラッキングを多発させる ReDoS 脆弱性を伴うことを確認。これを利用して `alter_table_add_column` に細工された文字列を入力することで遅延を引き起こすリスクが存在した。

**POC:** `etc/poc/poc_sec02_redos.py` — 時間差を計測して再現確認済み -> **FIXED**

**修正案:** `column_type` のバリデーション正規表現を `^[A-Za-z][a-zA-Z0-9_]*(?:\s+[a-zA-Z0-9_]+)*(\s*\([\d,\s]+\))?$` へ修正し、バックトラッキングを抑制する。 — **[FIXED]**

---

## 2. 不具合・潜在バグ

### BUG-01 [High] `upsert()` でデータ辞書を第1引数に渡した場合の AttributeError

**ファイル:** `core.py`

`upsert` メソッドで `(data_dict, conflict_columns)` パターンで呼ばれた際に、内部変数 `target_data` ではなく `data` の `.keys()` を参照するコードパスがあり `AttributeError` が発生する問題を修正。 — **[FIXED]**

### QUAL-02 [High] `AsyncNanaSQLite` 初期化時のスレッドプール二重初期化（競合状態）

**ファイル:** `async_core.py`

`AsyncNanaSQLite` の初期化時（`_ensure_initialized()`）において、複数の非同期タスクが同時にアクセスした場合に `NanaSQLite` とスレッドプールが複数回生成される競合状態のリスクを修正。`asyncio.Lock` を導入して直列化した。 — **[FIXED]**

---

## 3. 高速化の余地

### PERF-01 [Low] LRU/TTLキャッシュ使用時のネガティブキャッシュ欠如

`LRU` および `TTL` キャッシュ戦略に「存在しないキー」を追跡する仕組み（ネガティブキャッシュ）を導入し、存在しないキーへの反復アクセス時のSQLiteクエリ負荷をゼロにした。
（これに伴い発生した内部センチネル混入バグもリリース前に検知し修正済み） — **[FIXED]**

---

## 4. 改善点（コード品質）

### QUAL-01 [Low] `ExpiringDict` スケジューラスレッド停止処理の向上

`clear()` および `__del__` におけるデーモンスレッドのタイムアウト後処理を改善し、参照を適切にクリアしてResourceWarningを防止した。 — **[FIXED]**

### QUAL-03 [Low] ソースコード内マジックリテラルの定数化

ソースコード内で使用される `"BEGIN IMMEDIATE"` などのマジックリテラルを一元化し、モジュールレベルのプレフィックス定数に置き換えた（保守性向上）。 — **[FIXED]**

### CI-01 [Low] SonarQube Quality Gate の誤検知解消

SonarQube Cloudの解析対象から非Pythonファイルやモック、テストスクリプトを除外し、認知複雑度の誤った低下警告を抑止した（CI/CDの安定化）。 — **[FIXED]**

---

## 推奨対応優先度

### 対応済み

| ID | 概要 |
|---|---|
| BUG-01 | `upsert()` の AttributeError — 修正完了 |
| QUAL-02 | `AsyncNanaSQLite` の初期化時 Race Condition 修正 — 修正完了 |
| SEC-02 | `column_type` バリデーションの ReDoS 脆弱性 — 修正完了 |
| PERF-01 | LRU/TTLのネガティブキャッシュ導入 — 修正完了 |
| QUAL-01 | `ExpiringDict` 停止処理の向上 — 修正完了 |
| QUAL-03 | マジックリテラルの共通定数化 — 修正完了 |
| CI-01 | SonarQube Quality Gate 誤検知解消 — 修正完了 |

### 将来的な改善

該当なし（v1.4.1リリースにおける全指摘項目は本バージョン内で対応済み）

---

# NanaSQLite v1.5.0 プレリリース監査レポート

> 対象バージョン: 1.5.0dev2  
> 監査日: 2026-04-04  
> 対象ファイル: src/nanasqlite/ 配下すべて (特に hooks.py, protocols.py の新規追加分)

---

## 総括

| カテゴリ | Critical | High | Medium | Low | 計 |
|---|---|---|---|---|---|
| 脆弱性 | 2 | 2 | — | — | 4 |
| 不具合・潜在バグ | 1 | 1 | 2 | 1 | 5 |
| 高速化の余地 | — | — | 1 | — | 1 |
| 改善点（コード品質） | — | — | 1 | 1 | 2 |
| **合計** | **3** | **3** | **4** | **2** | **12** |

---

## 1. 脆弱性

### SEC-03 [Critical] UniqueHook における TOCTOU 競合状態による制約違反

**ファイル:** `hooks.py` L94-111

```python
for k, v in db.items():  # CHECK 段階
    if k == key:
        continue
    if callable(self.field):
        other_val = self.field(k, v)
    elif isinstance(v, dict):
        other_val = v.get(self.field)
    else:
        other_val = None
    
    if other_val == check_val:
        field_name = self.field.__name__ if callable(self.field) else str(self.field)
        raise NanaSQLiteValidationError(...)
# ← 競合ウィンドウ: 別スレッドが同じ値で書き込み可能
return value  # ← USE 段階: core.py の __setitem__ で実際の書き込み
```

ユニーク制約チェックと実際のデータベース書き込みの間に競合ウィンドウが存在し、マルチスレッド環境でユニーク制約が違反される可能性がある。Time-of-Check-Time-of-Use (TOCTOU) 脆弱性により、複数のスレッドが同時に同じ値を書き込むと制約が迂回される。

**修正案:** 制約チェックを `_acquire_lock()` トランザクション内に移動するか、SQLite の UNIQUE 制約を使用する。

---

### SEC-04 [Critical] ForeignKeyHook における TOCTOU 競合状態による参照整合性違反

**ファイル:** `hooks.py` L133-137

```python
if ref_key is not None and ref_key not in self.target_db:  # CHECK
    field_name = self.field.__name__ if callable(self.field) else str(self.field)
    raise NanaSQLiteValidationError(...)
return value  # ← USE: 書き込み前に参照先キーが削除される可能性
```

外部キー存在チェックと書き込みの間で、参照先のキーが別のスレッドにより削除される可能性がある。これにより、存在しないキーを参照する不整合なデータが挿入される。

**修正案:** 外部キー検証をアトミックな操作とするか、SQLite の FOREIGN KEY 制約を使用する。

---

### SEC-05 [High] BaseHook における ReDoS（正規表現DoS）脆弱性

**ファイル:** `hooks.py` L22, L27

```python
self._key_regex = re.compile(key_pattern) if isinstance(key_pattern, str) else key_pattern
# ...
if self._key_regex is not None and not self._key_regex.search(key):
```

ユーザー提供の正規表現パターンを検証なしで受け入れるため、ネストした量指定子（`(a+)+`）を含む悪質なパターンで指数バックトラッキングを引き起こし、CPU DoS攻撃が可能。25文字の入力で約3秒の処理遅延を確認。

**修正案:** 正規表現パターンの事前検証、タイムアウト機能の実装、または `regex` ライブラリの atomic grouping の使用。

---

### SEC-06 [High] Hooks の例外メッセージによる情報漏洩

**ファイル:** `hooks.py` L108-109, L135-136, L170, L199

```python
raise NanaSQLiteValidationError(
    f"Unique constraint violated: '{field_name}' = {check_val} already exists."
)
```

制約違反時の例外メッセージにフィールド名、値、バリデーションエラー詳細が含まれ、アプリケーションの内部構造やデータパターンが攻撃者に露出する可能性がある。

**修正案:** ユーザー向けには汎用的なエラーメッセージを返し、詳細情報はログにのみ記録する。

---

## 2. 不具合・潜在バグ

### BUG-05 [Critical] PydanticHook.after_read() の例外抑制によるデータ破損リスク

**ファイル:** `hooks.py` L209-211

```python
except Exception:
    pass
return value
```

`PydanticHook.after_read()` がすべての例外を暗黙で抑制するため、接続エラーやシリアライゼーション失敗などの重要なエラーがマスクされ、破損データが返される可能性がある。

**修正案:** 特定の例外（`ValidationError`）のみキャッチし、システムエラーは再発生させる。

---

### BUG-06 [High] hooks 処理で値が変更された場合のメモリ効率問題

**ファイル:** `core.py` L1353-1365

```python
if hooks:
    if self._coerce:
        processed_mapping: dict[str, Any] = {}
        for k, v in mapping.items():
            for hook in hooks:
                v = hook.before_write(self, k, v)
            processed_mapping[k] = v
        mapping = processed_mapping
```

`self._coerce = True` の場合は常に新しい辞書を作成するが、hooks が値を変更しない場合でも無駄なメモリ割り当てが発生する。大量データの batch 操作時に性能劣化とメモリ消費増大を招く。

**修正案:** フックで値が実際に変更された場合のみ新しい辞書を作成する最適化。

---

### BUG-07 [Medium] hooks のエラー発生時の部分更新リスク

**ファイル:** `core.py` L1362-1365

```python
for k, v in mapping.items():
    temp_v = v
    for hook in hooks:
        temp_v = hook.before_write(self, k, v)
```

batch 操作の途中でフックがエラーを発生させると、一部のキーは処理済み、一部は未処理となる部分更新状態が生じる可能性がある。トランザクション境界とフック実行タイミングの不整合。

**修正案:** バッチ全体をトランザクション内で処理するか、事前にすべてのフック検証を完了させる。

---

### BUG-08 [Medium] hooks 継承時の ValidkitHook 重複登録

**ファイル:** `core.py` L3232-3233

```python
resolved_hooks = [h for h in resolved_hooks if not getattr(h, "_is_validkit_hook", False)]
```

`table()` メソッドで validator と hooks を併用する際、既存の ValidkitHook を除去するロジックが `_is_validkit_hook` 属性に依存しているが、この属性を持たないカスタムフックが同様の機能を提供する場合、重複登録される可能性がある。

**修正案:** より厳密なフック重複検出ロジックの実装。

---

### BUG-09 [Low] フックチェーン実行時の例外スタックトレース喪失

**ファイル:** `hooks.py` L170, L199

```python
except Exception as exc:
    raise NanaSQLiteValidationError(...) from exc
```

フックチェーン内で複数のフックが順次実行される際、後続フックの例外により前段のフック情報が失われ、デバッグが困難になる場合がある。

**修正案:** フック実行コンテキストの情報を例外メッセージに含める。

---

## 3. 高速化の余地

### PERF-02 [Medium] UniqueHook の O(N) 線形探索によるスケーラビリティ問題

**ファイル:** `hooks.py` L95-106

```python
for k, v in db.items():  # O(N) 全件走査
    if k == key:
        continue
    # ... 重複チェック
```

`UniqueHook` はユニーク制約チェック時にテーブル全体を線形走査するため、レコード数の増加に比例して処理時間が増大する。大量データに対してスケールしない。

**修正案:** インデックスを活用したSQLクエリベースの重複チェックに変更。

---

## 4. 改善点（コード品質）

### QUAL-02 [Medium] hooks の型安全性不足

**ファイル:** `hooks.py` L33, L39, L45

```python
def before_write(self, db: Any, key: str, value: Any) -> Any:
def after_read(self, db: Any, key: str, value: Any) -> Any:
def before_delete(self, db: Any, key: str) -> None:
```

フックインターフェースの `db` パラメータが `Any` 型となっており、型安全性が不充分。実際の使用場面では `NanaSQLite` インスタンスが渡されるが、型チェッカーでは検証されない。

**修正案:** より厳密な型アノテーション（Generic や Protocol）の使用。

---

### QUAL-03 [Low] BaseHook._should_run() の冗長な条件分岐

**ファイル:** `hooks.py` L26-31

```python
if self._key_regex is not None and not self._key_regex.search(key):
    return False
if self._key_filter is not None and not self._key_filter(key):
    return False
return True
```

`_should_run()` メソッドの条件判定が冗長で、早期リターンパターンによる可読性向上が可能。

**修正案:** 条件式を統合した単一 return 文への簡素化。

---

## 推奨対応優先度

### リリース前に修正すべき（Critical）

| ID | 概要 |
|---|---|
| SEC-03 | UniqueHook の TOCTOU 競合状態 — ユニーク制約迂回リスク |
| SEC-04 | ForeignKeyHook の TOCTOU 競合状態 — 参照整合性違反リスク |
| BUG-05 | PydanticHook の例外抑制 — データ破損リスク |

### 高優先度（High）

| ID | 概要 |
|---|---|
| SEC-05 | BaseHook の ReDoS 脆弱性 — CPU DoS 攻撃可能 |
| SEC-06 | フック例外での情報漏洩 — 内部構造露出リスク |
| BUG-06 | フック処理時のメモリ効率問題 — パフォーマンス劣化 |

### 中優先度（Medium）

| ID | 概要 |
|---|---|
| BUG-07 | フックエラー時の部分更新リスク — データ整合性問題 |
| BUG-08 | ValidkitHook 重複登録 — 予期しない二重検証 |
| PERF-02 | UniqueHook の O(N) 問題 — 大量データでのスケール問題 |
| QUAL-02 | フック型安全性不足 — 開発時エラー検出問題 |

### 低優先度（Low）

| ID | 概要 |
|---|---|
| BUG-09 | フック例外スタックトレース喪失 — デバッグ難易度 |
| QUAL-03 | BaseHook 冗長条件分岐 — コード品質 |
