# NanaSQLite v1.5.3 プレリリース最終監査レポート

**対象バージョン:** v1.5.3（1.5.3rc4 からの差分）  
**監査日:** 2026-04-08  
**監査対象ファイル:**
- `src/nanasqlite/core.py`
- `src/nanasqlite/async_core.py`

---

## 総括テーブル

| カテゴリ | Critical | High | Medium | Low | 計 |
|---------|----------|------|--------|-----|-----|
| 不具合・潜在バグ | 0 | 0 | 0 | 0 | 0 |
| パフォーマンス | 0 | 0 | 2 | 0 | 2 |
| コード品質 | 0 | 0 | 0 | 3 | 3 |
| 脆弱性 | 0 | 0 | 0 | 0 | 0 |
| **合計** | **0** | **0** | **2** | **3** | **5** |

---

## 各発見事項

---

### PERF-E [Medium] `_get_all_keys_from_db()` が毎回 f-string SQL を構築する

**ファイル:** `src/nanasqlite/core.py` L932–938（修正前）

```python
def _get_all_keys_from_db(self) -> list[str]:
    with self._acquire_lock():
        cursor = self._connection.execute(
            f"SELECT key FROM {self._safe_table}"  # nosec ← 毎回構築
        )
        return [row[0] for row in cursor]
```

`keys()` / `__iter__` が呼ばれるたびに f-string を評価しており、PERF-07 で他の KV SQL 文字列が `__init__` 時に事前計算されたパターンと一貫性がありませんでした。

**修正案（適用済み）:**

`__init__` に `self._sql_kv_select_keys` を追加し、`_get_all_keys_from_db()` でそれを使用。

---

### PERF-F [Medium] `batch_update_partial()` v2 + Unbounded モードで不要ロック取得

**ファイル:** `src/nanasqlite/core.py` L1668–1681（修正前）

```python
if self._v2_mode and self._v2_engine:
    for key, _ in params:
        self._v2_engine.kvs_set(...)
    with self._acquire_lock():           # ← 不要
        if self._lru_mode:
            ...
        else:
            self._data.update(accepted_values)
            if self._absent_keys:
                self._absent_keys.difference_update(...)
    return failed
```

`batch_update()` の v2 パスはロックなしで `_data.update()` / `_absent_keys.difference_update()` を実行しています（`__setitem__` と同じ方針）。`batch_update_partial()` だけがロックを取得しており、不必要な競合が発生していました。Unbounded モードの `dict`/`set` 操作は GIL が個々の操作をアトミックに保護するため、明示的ロックは不要です。LRU/TTL モードは `ExpiringDict` の操作に引き続きロックが必要です。

**修正案（適用済み）:**

Unbounded パスのみロックを外し、LRU パスは `with self._acquire_lock():` を維持。

---

### QUAL-04 [Low] `_no_encrypt` の変更不可コメント不足

**ファイル:** `src/nanasqlite/core.py` L279（修正前）

```python
# PERF-29: Pre-compute a single bool ...
self._no_encrypt: bool = not bool(self._fernet or self._aead)
```

rc3 監査（QUAL-04）で指摘済みでしたが未対応でした。`_fernet` / `_aead` を `__init__` 後に変更すると `_no_encrypt` がステールになり、暗号化なしのパスが誤って実行されます。

**修正案（適用済み）:**

コメントに「`_fernet` / `_aead` を `__init__` 後に変更してはならない」旨を追記。

---

### QUAL-05 [Low] `parameters: tuple = None` アノテーション不正確

**ファイル:** `src/nanasqlite/core.py`（修正前）

| メソッド | 行 |
|---|---|
| `fetch_one()` | L2323 |
| `fetch_all()` | L2341 |
| `create_table()` (`primary_key`) | L2362 |
| `sql_update()` | L2766 |
| `sql_delete()` | L2802 |
| `exists()` | L2955 |

`parameters: tuple = None` は型として不正確（`None` は `tuple` ではない）。mypy の `--no-strict-optional` モードでは見逃されますが、厳格な型チェック環境では警告が発生します。

**修正案（適用済み）:**

全 6 箇所を `parameters: tuple | None = None`（および `primary_key: str | None = None`）に変更。

---

### QUAL-06 [Low] `async_core.py` `_ensure_initialized()` ガードの不統一

**ファイル:** `src/nanasqlite/async_core.py`（修正前）

```python
# query_with_pagination() L1073
if self._db is None:
    await self._ensure_initialized()

# table() L1501
if self._db is None:
    await self._ensure_initialized()
```

他の非同期メソッドはすべて無条件で `await self._ensure_initialized()` を呼び出しています。この 2 メソッドだけが `if self._db is None:` ガードを持っており、`_ensure_initialized()` の内部で行う close 状態チェックがスキップされる可能性がありました（`_ensure_initialized()` はべき等であるため、常に呼ぶのが正しいパターン）。

**修正案（適用済み）:**

両メソッドとも `await self._ensure_initialized()` を無条件で呼ぶよう変更。

---

## 推奨対応優先度

### 今バージョン（v1.5.3）で修正済み

| ID | 重要度 | 内容 | 対応状況 |
|---|---|---|---|
| PERF-E | Medium | `_get_all_keys_from_db()` 毎回 f-string 構築 | ✅ 修正済み |
| PERF-F | Medium | `batch_update_partial()` v2+Unbounded 不要ロック | ✅ 修正済み |
| QUAL-04 | Low | `_no_encrypt` 変更不可コメント不足 | ✅ 修正済み |
| QUAL-05 | Low | `parameters: tuple = None` 型アノテーション不正確（6 箇所） | ✅ 修正済み |
| QUAL-06 | Low | `async_core.py` `_ensure_initialized()` ガード不統一 | ✅ 修正済み |

---

## 変更前後の最終監査サマリー

### rc1 〜 rc4 からの累積修正

| バージョン | 修正内容 |
|---|---|
| rc1 | PERF-07〜13（SQL 事前計算、to_dict/values/items 最適化） |
| rc2 | BUG-01（setdefault フック返値）、PERF-14〜20（try/except 高速パス、_has_hooks フラグ） |
| rc3 | BUG-02〜04（tx リーク、ロック外状態更新）、PERF-21〜26/29（executemany、dict.update、begin/commit 直接呼び出し）、QUAL-03/SEC-02 |
| rc4 | PERF-A〜D（lru_cache、ExpiringDict 最適化、vacuum、backup stat）、BUG-02〜04（utils）、SEC-02（列型正規表現）、QUAL-01、CodeQL |
| **v1.5.3 本番** | **PERF-E/F（SQL 事前計算、不要ロック除去）、QUAL-04/05/06（コメント、型アノテーション、async 統一）** |
