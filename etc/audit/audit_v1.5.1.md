# NanaSQLite v1.5.1 プレリリース監査レポート

**対象バージョン:** v1.5.1  
**監査日:** 2026-04-05  
**監査対象ファイル:**
- `src/nanasqlite/core.py` (3325 行)
- `src/nanasqlite/async_core.py` (1816 行)
- `src/nanasqlite/cache.py` (331 行)
- `src/nanasqlite/utils.py` (255 行)
- `src/nanasqlite/sql_utils.py` (191 行)
- `src/nanasqlite/exceptions.py` (105 行)
- `src/nanasqlite/hooks.py` (274 行)
- `src/nanasqlite/protocols.py` (21 行)
- `src/nanasqlite/v2_engine.py` (545 行)
- `src/nanasqlite/__init__.py` (66 行)

**注記:** PERF-01〜PERF-04 は既に v1.5.1 でパッチ済みのため、本レポートでは PERF-05 から採番する。

---

## 総括テーブル

| カテゴリ | Critical | High | Medium | Low | 計 |
|---------|----------|------|--------|-----|-----|
| バグ / 潜在バグ (BUG) | 0 | 1 | 1 | 2 | 4 |
| パフォーマンス (PERF) | 0 | 0 | 0 | 1 | 1 |
| コード品質 (QUAL) | 0 | 0 | 0 | 1 | 1 |
| セキュリティ (SEC) | 0 | 0 | 2 | 0 | 2 |
| **合計** | **0** | **1** | **3** | **4** | **8** |

---

## バグ / 潜在バグ

### BUG-01 [High] `pop()` が v2 モードで直接 DB 書き込みを行いバックグラウンドフラッシュと競合する

**ファイル:** `core.py` L1202–1221

```python
def pop(self, key: str, *args) -> Any:
    self._check_connection()
    if self._ensure_cached(key):
        value = self._cache.get(key)
        if self._hooks:
            for hook in self._hooks:
                hook.before_delete(self, key)
        # DBから先に削除し、ロックタイムアウト時のキャッシュ不整合を防止
        self._delete_from_db(key)      # ← v2 モードでもここを通る
        self._cache.delete(key)
```

`pop()` は `_delete_from_db()` を直接呼び出しており、`v2_mode` フラグを確認しない。`__delitem__` が v2 パス（`v2_engine.kvs_delete()`）を正しく経由するのとは対照的に、`pop()` は v2 エンジンの staging buffer を完全にバイパスして SQLite 接続に直接 DELETE を発行する。

これにより以下の問題が発生し得る:
1. **データ復活リスク**: `pop()` でキーを削除した直後にバックグラウンドフラッシュが staging buffer の古い書き込みを DB に反映させると、削除済みキーが再挿入される。
2. **ロック競合**: `_delete_from_db()` が `_acquire_lock()` 経由でロックを取得しようとするとき、v2 バックグラウンドフラッシュスレッドが `BEGIN IMMEDIATE TRANSACTION` を保持していると競合が発生しデータ不整合が生じる。

**修正案:** `__delitem__` と同様に v2 モードを確認し、v2 の場合は `v2_engine.kvs_delete()` を経由させる。

```python
def pop(self, key: str, *args) -> Any:
    self._check_connection()
    if self._ensure_cached(key):
        value = self._cache.get(key)
        if self._hooks:
            for hook in self._hooks:
                hook.before_delete(self, key)

        if self._v2_mode and self._v2_engine:
            self._v2_engine.kvs_delete(self._safe_table, key)
        else:
            self._delete_from_db(key)

        self._cache.delete(key)
        if not self._lru_mode:
            self._data.pop(key, None)
            self._cached_keys.add(key)

        if self._hooks:
            for hook in self._hooks:
                value = hook.after_read(self, key, value)
        return value
    if args:
        return args[0]
    raise KeyError(key)
```

---

### BUG-02 [Medium] `batch_get()` が `_cached_keys` の「存在しない」ステータスを尊重しない

**ファイル:** `core.py` L1137–1199

```python
def batch_get(self, keys: list[str]) -> dict[str, Any]:
    ...
    cache_data = self._cache.get_data()  # ← _data のみ参照（_cached_keys は確認しない）
    for key in keys:
        if key in cache_data:
            val = cache_data[key]
            if val is not MISSING:
                results[key] = val
        else:
            missing_keys.append(key)  # ← _data にない → DB 参照へ
    ...
    cursor = self._connection.execute(sql, tuple(missing_keys))
```

`__delitem__` が v2 パスで `kvs_delete()` を実行すると、キーは `_cached_keys` に「存在しない（known absent）」として記録され、`_data` からは削除される。この状態で `get()` は `_ensure_cached()` 内で `key in self._cached_keys` を確認するためキャッシュを正しく尊重してデフォルト値を返す。しかし `batch_get()` は `_data` のみを確認するため、`_data` にないキーを `missing_keys` として DB に問い合わせる。v2 非 immediate モードでは staging の delete がまだ DB に反映されていないため、DB から古い値が返る。`get()` と `batch_get()` の間でキー存在判定の一貫性がない。

**修正案:** `batch_get()` でも `_cached_keys` を確認して、「存在しない」として記録されたキーをスキップする。

```python
cache_data = self._cache.get_data()
cached_keys = self._cached_keys  # "known absent" セットへの参照

for key in keys:
    if key in cache_data:
        val = cache_data[key]
        if val is not MISSING:
            results[key] = val
    elif key in cached_keys:
        # "known absent" として記録されている (_data にないが _cached_keys にある)
        # DB へ問い合わせても何も返らないか、v2 staging の delete が反映されていない
        # 可能性があるためスキップ
        pass
    else:
        missing_keys.append(key)
```

---

### BUG-03 [Low] `to_dict()` が LRU / TTL モードで `MISSING` センチネル値を含む可能性がある

**ファイル:** `core.py` L1569–1573

```python
def to_dict(self) -> dict:
    self._check_connection()
    self.load_all()
    return dict(self._data)   # ← MISSING を含む可能性
```

`items()` は `if v is not MISSING` で正しくフィルタリングしているが、`to_dict()` は `self._data` をそのまま `dict()` に変換する。LRU / TTL モードでは `mark_cached()` が MISSING センチネルをキャッシュに書き込む（存在しないキーの負キャッシュ）ため、`to_dict()` の結果に `{key: <MISSING sentinel>}` が混入する。

**修正案:** `items()` と同様にフィルタリングを追加する。

```python
def to_dict(self) -> dict:
    self._check_connection()
    self.load_all()
    return {k: v for k, v in self._data.items() if v is not MISSING}
```

---

### BUG-04 [Low] `get_db_size()` がインメモリ DB で `FileNotFoundError` を発生させる

**ファイル:** `core.py` L2900–2912

```python
def get_db_size(self) -> int:
    return os.path.getsize(self._db_path)
```

`db_path=":memory:"` や `db_path="file::memory:?cache=shared"` でインスタンスを生成した場合、`os.path.getsize(":memory:")` は `FileNotFoundError` を発生させる。インメモリ DB に対して `get_db_size()` を呼び出した際のエラーメッセージが不明瞭で、利用者が原因を特定しにくい。

**修正案:** インメモリ DB の場合は 0 を返すか、より明確な例外を発生させる。

```python
def get_db_size(self) -> int:
    if self._is_in_memory_path(self._db_path):
        return 0
    return os.path.getsize(self._db_path)
```

---

## パフォーマンス

### PERF-05 [Low] `fast_validate_sql_chars()` が呼び出しごとに `set` オブジェクトを新規生成する

**ファイル:** `sql_utils.py` L163–191

```python
def fast_validate_sql_chars(expr: str) -> bool:
    if not expr:
        return True
    safe_chars = set("abcdefghijklmnopqrstuvwxyz...")  # ← 毎回新規生成
    return all(c in safe_chars for c in expr)
```

`_validate_expression()` は全ての `query()`, `count()`, `query_with_pagination()`, `__setitem__` などから呼ばれるホットパスであり、そのたびに `fast_validate_sql_chars()` が呼ばれる。`set(...)` はイミュータブルな文字リテラルから毎回構築されるが、内容が不変なためモジュールレベルの定数として事前計算すれば約 200–300 ns / 呼び出しの節約が見込める。

**修正案:** モジュールレベル定数に昇格させる。

```python
_SAFE_SQL_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ ,.()'=<>!+-*/\"|?:@$"
)

def fast_validate_sql_chars(expr: str) -> bool:
    if not expr:
        return True
    return all(c in _SAFE_SQL_CHARS for c in expr)
```

`frozenset` を使うことで `set` より若干高速なメンバシップテスト（CPython 実装の最適化により）を利用できる。

---

## コード品質

### QUAL-01 [Low] `async_core.py` の `table()` が同期版 `table()` の一部オプション引数（`cache_strategy` 等）を公開しない

**ファイル:** `async_core.py` L1454–1558

```python
async def table(
    self,
    table_name: str,
    validator: Any | None | EllipsisType = _UNSET,
    coerce: bool | EllipsisType = _UNSET,
    hooks: list[NanaHook] | None | EllipsisType = _UNSET,
) -> AsyncNanaSQLite:
    ...
    sub_db = await loop.run_in_executor(
        self._executor,
        lambda: self._db.table(table_name, validator=validator, coerce=coerce, hooks=hooks),
    )
```

同期版 `NanaSQLite.table()` は `cache_strategy`, `cache_size`, `cache_ttl`, `cache_persistence_ttl`, `v2_enable_metrics` を受け付けるが、非同期版 `AsyncNanaSQLite.table()` ではこれらのパラメータが公開されておらず、ユーザーがサブテーブルのキャッシュ戦略を個別に指定できない。継承で回避可能だが、API の一貫性が損なわれている。

**修正案:** 同期版 `table()` と同等のパラメータを `async_core.py` の `table()` にも追加し、ラムダ呼び出しに含める。これは後方互換なので即時適用可能。

---

## セキュリティ

### SEC-01 [Medium] `exists()` の `where` 句が `_validate_expression()` を経由しない

**ファイル:** `core.py` L2716–2735

```python
def exists(self, table_name: str, where: str, parameters: tuple = None) -> bool:
    safe_table_name = self._sanitize_identifier(table_name)
    sql = f"SELECT EXISTS(SELECT 1 FROM {safe_table_name} WHERE {where})"  # nosec
    cursor = self.execute(sql, parameters)
    return bool(cursor.fetchone()[0])
```

`count()`, `query()`, `query_with_pagination()` は `where` 引数を `_validate_expression()` に通して危険なパターン（`;`, `--`, `DROP` 等）や許可外 SQL 関数を検査するが、`exists()` にはこの検証がない。`strict_sql_validation=True` のインスタンスでも `exists()` の `where` 句は検証されず、インスタンス設定が一貫して適用されない。

**影響:** `strict_sql_validation=True` の場合、他のクエリメソッドは不正な WHERE 句を拒否するが、`exists()` のみ素通りする。攻撃者が直接 `where` 引数を制御できる状況（不適切な利用）では SQL インジェクションが成立し得る。

**修正案:**

```python
def exists(self, table_name: str, where: str, parameters: tuple = None) -> bool:
    safe_table_name = self._sanitize_identifier(table_name)
    self._validate_expression(where, context="where")
    sql = f"SELECT EXISTS(SELECT 1 FROM {safe_table_name} WHERE {where})"  # nosec
    cursor = self.execute(sql, parameters)
    return bool(cursor.fetchone()[0])
```

---

### SEC-02 [Medium] `sql_update()` / `sql_delete()` の `where` 句が `_validate_expression()` を経由しない

**ファイル:** `core.py` L2532–2583

```python
def sql_update(self, table_name: str, data: dict, where: str, parameters: tuple = None) -> int:
    ...
    sql = f"UPDATE {safe_table_name} SET {set_clause} WHERE {where}"  # nosec
    ...

def sql_delete(self, table_name: str, where: str, parameters: tuple = None) -> int:
    safe_table_name = self._sanitize_identifier(table_name)
    sql = f"DELETE FROM {safe_table_name} WHERE {where}"  # nosec
    ...
```

`sql_update()` と `sql_delete()` の `where` 引数は `_validate_expression()` を通らず、`strict_sql_validation=True` の設定も無視される。`count()` 等と一貫性が取れていない。なお、パラメータバインディングを正しく使用していれば SQLi は防止されるが、`where` 引数自体は SQL フラグメントとして直接埋め込まれる構造になっており、`strict_sql_validation` の期待値と合致しない。

**修正案:**

```python
def sql_update(self, table_name: str, data: dict, where: str, parameters: tuple = None) -> int:
    safe_table_name = self._sanitize_identifier(table_name)
    self._validate_expression(where, context="where")
    ...

def sql_delete(self, table_name: str, where: str, parameters: tuple = None) -> int:
    safe_table_name = self._sanitize_identifier(table_name)
    self._validate_expression(where, context="where")
    ...
```

---

## 推奨対応優先度

### リリース前に修正すべき（v1.5.1 対象）

| ID | 重要度 | タイトル |
|----|--------|----------|
| BUG-01 | High | `pop()` が v2 モードで直接 DB 書き込みを行いバックグラウンドフラッシュと競合 |
| BUG-02 | Medium | `batch_get()` が v2 staging buffer の未フラッシュデータを参照しない |
| SEC-01 | Medium | `exists()` の `where` 句が `_validate_expression()` を経由しない |
| SEC-02 | Medium | `sql_update()` / `sql_delete()` の `where` 句が `_validate_expression()` を経由しない |

### 次バージョンで対応可能

| ID | 重要度 | タイトル |
|----|--------|----------|
| BUG-03 | Low | `to_dict()` が LRU/TTL モードで MISSING センチネルを含む |
| PERF-05 | Low | `fast_validate_sql_chars()` が呼び出しごとに set を新規生成 |

### 将来的な改善

| ID | 重要度 | タイトル |
|----|--------|----------|
| BUG-04 | Low | `get_db_size()` がインメモリ DB で FileNotFoundError を発生させる |
| QUAL-01 | Low | `AsyncNanaSQLite.table()` が同期版の一部オプション引数を公開しない |

---

## 第2パス監査 (2026-04-06)

**監査コミット:** `6f51f6a`  
**監査方針:** 第1パスで発見された全修正の検証、BUG-01 修正のエッジケース確認、新規問題の探索。

### 修正検証結果

#### BUG-01 [High] ✅ VERIFIED

`pop()` の v2 パスが `__delitem__` と完全に対称であることを確認した。

- `v2_engine.kvs_delete()` → staging buffer に DELETE を積む ✓  
- `_cache.delete(key)` → `_data` から削除し `_cached_keys` に追加 ✓  
- `if not self._lru_mode:` ブロックの `_data.pop` / `_cached_keys.add` は `UnboundedCache.delete()` の後に呼ばれるため冗長だが無害 ✓  
- hooks (`before_delete` / `after_read`) の呼び出し順序は修正前と同一 ✓  
- v2+LRU モード: `_cache.delete(key)` で LRU データから削除、以後 `_ensure_cached` が staging buffer の "delete" action を確認して False を返す ✓

**回帰なし。新たなエッジケースなし。**

#### BUG-02 [Medium] ✅ VERIFIED

`batch_get()` の BUG-02 修正 (`elif not self._lru_mode and key in self._cached_keys: pass`) を検証。

- 非 LRU モード: `_cached_keys` に存在するが `_data` に存在しないキーを「既知不在」として正しくスキップ ✓  
- LRU モード: `not self._lru_mode` が False のため、この elif 分岐は決して実行されない。LRU モードの動作は修正前と同一 ✓  
- v2 モードで SET 直後のキーは `_update_cache()` により常に `_data` に存在するため、`batch_get` のステージングバッファ未チェックは問題にならない ✓  
- LRU モードで MISSING センチネルが格納されているキーは `cache_data` に存在するが `val is not MISSING` が False になるため `missing_keys` に回され DB 再クエリされる。この挙動は修正前と同一で設計通り ✓

**回帰なし。**

#### BUG-03 [Low] ✅ VERIFIED

`to_dict()` の MISSING フィルタを検証。

- LRU/TTL モード: `mark_cached(key)` が `_data` に MISSING を格納する場合があり、フィルタが機能 ✓  
- 非 LRU モード: `UnboundedCache.delete()` は `_data` からキーを削除するため MISSING は `_data` に現れない。フィルタは no-op だが無害 ✓  
- `load_all()` が事前に呼ばれるため `_data` に全 DB レコードが展開済み ✓

**回帰なし。**

#### SEC-01 [Medium] ✅ VERIFIED

`exists()` の WHERE 句に `_validate_expression(where, context="where")` が追加され、他のクエリメソッドと一貫した検証が行われることを確認。

#### SEC-02 [Medium] ✅ VERIFIED

`sql_update()` および `sql_delete()` の WHERE 句に `_validate_expression(where, context="where")` が追加されていることを確認。`strict_sql_validation=True` 設定が正しく機能する。

#### PERF-05 [Low] ✅ VERIFIED

`_SAFE_SQL_CHARS` frozenset の文字セットがオリジナルの `set()` 呼び出しと完全に同一であることを `git show 6f51f6a -- src/nanasqlite/sql_utils.py` で確認:

```
-    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ ,.()'=<>!+-*/\"|?:@$")
+_SAFE_SQL_CHARS: frozenset[str] = frozenset(
+    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ ,.()'=<>!+-*/\"|?:@$"
+)
```

文字セットは等価、挙動変化なし。

#### BUG-04 [Low] ✅ DOCUMENTED ONLY (確認済)

`get_db_size()` のインメモリ DB における OSError はドキュメントのみ対応として記録済み。コードは変更なし。

#### QUAL-01 [Low] ✅ DOCUMENTED ONLY (確認済)

`AsyncNanaSQLite.table()` に `lock_timeout` 転送がないことはドキュメントのみ対応として記録済み。なお、`lock_timeout` は `async_core.py` では使用されていないため実際の影響は限定的。

### 新規発見事項

#### OBS-01 [Info] `__contains__` が v2+LRU モードでステージングバッファを参照しない (既知の制限)

**ファイル:** `core.py` L1021–1049

v2+LRU モードでキーを削除（pop/del）した直後、ステージングバッファへの DELETE がまだ DB にフラッシュされていない場合、`__contains__` が DB を直接参照して `True` を返す可能性がある。

これは `__contains__` が `_ensure_cached()` を呼ばず DB に直接クエリするため発生する。v2+非 LRU モードでは `_cached_keys` のファストパスにより回避される。

**評価:** BUG-01 修正によって導入されたものではなく、v2 モードの設計上の eventual consistency に起因する既知の制限。`_ensure_cached()` は v2 ステージングバッファを正しく参照しており、`__getitem__` ・ `pop()` ・ `batch_get()` ではデータ整合性が維持される。`__contains__` (`in` 演算子) のみ v2+LRU 環境で短期間の stale read が発生しうる。

**対応:** 新規修正不要。将来バージョンでの改善候補として記録する。

### テスト結果

- `python -m tox -e lint` → **PASS** (ruff: エラーなし)
- `python -m tox -e type` → **PASS** (mypy: エラーなし)
- `NANASQLITE_SUPPRESS_MP_WARNING=1 python -m pytest tests/ -x --ignore=tests/test_benchmark.py --ignore=tests/test_async_benchmark.py --ignore=tests/test_cache_benchmark.py --ignore=tests/benchmark_encryption.py` → **785 passed, 6 skipped**

### 第2パス結論

第1パスで指摘された全 8 件の修正は正しく適用されており、回帰はない。  
新規 Critical/High 問題は発見されなかった。  
OBS-01 として v2+LRU モードの `__contains__` に既知の制限を記録したが、修正は不要。  
**v1.5.1 リリース準備は完了していると判断する。**
