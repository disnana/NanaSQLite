# NanaSQLite v1.5.3rc3 プレリリース監査レポート

**対象バージョン:** 1.5.3rc3  
**監査日:** 2026-04-08  
**監査対象差分:** v1.5.3rc2 → v1.5.3rc3（PERF-21〜29 の最適化コミット）

## 対象ファイル

| ファイル | 変更種別 |
|---|---|
| `src/nanasqlite/core.py` | 修正（PERF-21〜29 適用） |

---

## 総括テーブル

| カテゴリ | Critical | High | Medium | Low | 計 |
|---|---|---|---|---|---|
| 不具合・潜在バグ | 0 | 2 | 1 | 0 | 3 |
| 高速化の余地 | 0 | 0 | 0 | 0 | 0 |
| 改善点（コード品質） | 0 | 0 | 1 | 1 | 2 |
| 脆弱性 | 0 | 0 | 0 | 0 | 0 |
| **合計** | **0** | **2** | **2** | **1** | **5** |

---

## 各発見事項

---

### BUG-02 [High] `execute_many` が非 `apsw.Error` 例外でトランザクションをリークする

**ファイル:** `src/nanasqlite/core.py` L2276（修正前）

```python
# 修正前
except apsw.Error:
    cursor.execute("ROLLBACK")
    raise
```

`execute_many` の非 v2 パスでは `BEGIN IMMEDIATE` を発行してから `cursor.executemany()` を実行するが、例外捕捉が `except apsw.Error:` に限定されている。`cursor.executemany()` に不正なパラメータを渡した場合（例: `object()` を含むタプルリスト）、Python レベルの `TypeError` が送出される。この例外は `apsw.Error` の派生ではないため `ROLLBACK` が実行されず、トランザクションが BEGIN IMMEDIATE のまま残る。その結果、後続の `__setitem__` / `batch_update` 等がすべて「既にトランザクション中」エラーで失敗し、インスタンスが実質的に使用不能になる。

`batch_update` や `batch_delete` は同様のパターンで `except Exception:` を使用しており、一貫性の観点でも問題がある。

**修正案（適用済み）:**

```python
except Exception:
    cursor.execute("ROLLBACK")
    raise
```

**POC:** `etc/poc/poc_bug02_execute_many_txn_leak.py`

---

### BUG-03 [High] `begin_transaction` が `_in_transaction` フラグをロック外で更新する

**ファイル:** `src/nanasqlite/core.py` L3288-3295（修正前）

```python
# 修正前
with self._acquire_lock():
    self._connection.execute("BEGIN IMMEDIATE")
self._in_transaction = True       # ← ロック解放後
self._transaction_depth = 1
```

PERF-26 最適化で `execute()` ディスパッチを省略した際、`_in_transaction = True` の代入がロック解放後に行われるようになった。マルチスレッド環境では次のような競合状態が発生する：

1. スレッド T1 が `begin_transaction()` を呼ぶ → `_in_transaction` チェックをパス（False）→ ロック取得 → `BEGIN IMMEDIATE` 実行 → **ロック解放**（この時点で `_in_transaction` はまだ False）
2. スレッド T2 が `begin_transaction()` を呼ぶ → `_in_transaction` チェックをパス（まだ False）→ ロック取得 → `BEGIN IMMEDIATE` を試みる → SQLite エラー（"cannot start a transaction within a transaction"）

Python レベルでは `NanaSQLiteTransactionError`（意図した動作）を出すべき場面で、T2 は `NanaSQLiteDatabaseError` を受け取る。また `_in_transaction` フラグが SQLite のトランザクション状態と短時間ズレることで、診断が困難なエラーが発生しうる。

**修正案（適用済み）:**

```python
with self._acquire_lock():
    self._connection.execute("BEGIN IMMEDIATE")
    self._in_transaction = True   # ← ロック内
    self._transaction_depth = 1
```

**POC:** `etc/poc/poc_bug03_begin_txn_race.py`

---

### BUG-04 [Medium] `batch_update` のシリアライズ外出しによるキャッシュ不整合（PERF-23）

**ファイル:** `src/nanasqlite/core.py` L1571-1587

```python
# ロック外でシリアライズ
params = [(key, self._serialize(value)) for key, value in mapping.items()]

with self._acquire_lock():
    cursor.executemany(self._sql_kv_insert, params)  # params 由来の値
    ...
    self._data.update(mapping)  # mapping 由来の値（変化している可能性）
```

PERF-23 でシリアライズをロック外に移動した結果、`params`（DB に書き込む値）と `self._data.update(mapping)`（キャッシュに入る値）の取得タイミングがズレた。呼び出し元が `mapping` を別スレッドから同時に変更した場合、DB とキャッシュで異なる値が格納されるサイレントなデータ不整合が発生する。

この問題を安全に修正するにはシリアライズ時のスナップショット（`dict(mapping)`）を使うか、キャッシュ更新も `params` から逆算する必要があるが、前者はメモリコスト、後者は実装複雑度を増す。**呼び出し元が同一 `mapping` を並行変更するのはアンチパターンであり**、本バージョンでは API ドキュメントに注意事項を追記する対応とする。

**修正案（次バージョン）:** `batch_update` のドキュメントに「引数の `mapping` はロック外でスナップショットを取らないため、呼び出し中に別スレッドから変更しないこと」を明記する。

---

### QUAL-03 [Medium] `commit` / `rollback` が `_in_transaction` をロック外で更新する

**ファイル:** `src/nanasqlite/core.py` L3317-3318, L3345-3346（修正前）

```python
# commit() 修正前
with self._acquire_lock():
    self._connection.execute("COMMIT")
self._in_transaction = False   # ← ロック外
self._transaction_depth = 0
```

BUG-03 と同様に、PERF-26 で `commit()` / `rollback()` の `_in_transaction = False` 代入がロック外に移動した。COMMIT/ROLLBACK 成功後、フラグが更新される前に別スレッドが `begin_transaction()` を呼ぶと、Python レベルでは「トランザクション中」と判断して `NanaSQLiteTransactionError` を送出する可能性がある（実際には COMMIT/ROLLBACK 済みで SQLite レベルではトランザクションが終了しているにもかかわらず）。

**修正案（適用済み）:** `_in_transaction` 更新を `with self._acquire_lock():` ブロック内に移動する。

---

### QUAL-04 [Low] PERF-29 `_no_encrypt` は動的変更不可だがコメント不足

**ファイル:** `src/nanasqlite/core.py` L278

```python
self._no_encrypt: bool = not bool(self._fernet or self._aead)
```

`_no_encrypt` は `__init__` でのみ計算され、`_fernet` / `_aead` を後から変更する公開 API は存在しないため、現バージョンでは同期ズレは起きない。ただし、サブクラスやテストモックが `_fernet` を直接代入した場合、`_no_encrypt` が stale になることに気づきにくい。コメントで「`_fernet` / `_aead` を __init__ 後に変更してはならない」旨を明記することが望ましい。

**修正案:** コメント追加のみ（次バージョン対応可）。

---

## 推奨対応優先度

### リリース前に修正すべき

| ID | 重要度 | 内容 | 対応状況 |
|---|---|---|---|
| BUG-02 | High | `execute_many` 非 apsw.Error 例外でトランザクションリーク | ✅ 修正済み |
| BUG-03 | High | `begin_transaction` `_in_transaction` ロック外更新 | ✅ 修正済み |
| QUAL-03 | Medium | `commit`/`rollback` `_in_transaction` ロック外更新 | ✅ 修正済み |

### 次バージョン（v1.5.4）で対応可能

| ID | 重要度 | 内容 |
|---|---|---|
| BUG-04 | Medium | `batch_update` シリアライズ外出しによるキャッシュ不整合（API ドキュメント注記） |

### 将来的な改善

| ID | 重要度 | 内容 |
|---|---|---|
| QUAL-04 | Low | PERF-29 `_no_encrypt` 動的変更不可のコメント追記 |

---

## PERF-21〜29 変更の評価サマリー

| 変更 ID | 評価 | 備考 |
|---|---|---|
| PERF-21 `execute_many` executemany 化 | ⚠️ BUG-02 | `except apsw.Error` → `except Exception` 修正済み |
| PERF-22 `batch_delete` フックなし時スキップ | ✅ 正常 | フックあり時の `_ensure_cached` 呼び出しは維持 |
| PERF-23 `batch_update` シリアライズ外出し | ⚠️ BUG-04 | 単一スレッドでは問題なし。並行変更は API 上の禁止事項として文書化 |
| PERF-24 `batch_update_partial` dict.update | ✅ 正常 | v2/非v2 両パスとも正しく適用 |
| PERF-25 `batch_delete` `_absent_keys.update` | ✅ 正常 | 既存の per-key add と等価 |
| PERF-26 `begin_transaction/commit/rollback` | ⚠️ BUG-03/QUAL-03 | 状態更新をロック内に移動して修正済み |
| PERF-29 `_serialize` `_no_encrypt` フラグ | ✅ 正常 | `__init__` 外での変更 API なし。理論的リスクのみ |
