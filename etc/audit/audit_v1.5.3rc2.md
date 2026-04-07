# NanaSQLite v1.5.3rc2 プレリリース監査レポート

**対象バージョン:** 1.5.3rc2  
**監査日:** 2026-04-07  
**監査対象差分:** v1.5.3rc1 → v1.5.3rc2（PERF-14〜20 の最適化コミット）

## 対象ファイル

| ファイル | 変更種別 |
|---|---|
| `src/nanasqlite/core.py` | 修正（PERF-14〜20 適用） |
| `tests/test_v153_perf_fixes.py` | 修正（テスト追加） |

---

## 総括テーブル

| カテゴリ | Critical | High | Medium | Low | 計 |
|---|---|---|---|---|---|
| 不具合・潜在バグ | 0 | 0 | 1 | 0 | 1 |
| 高速化の余地 | 0 | 0 | 0 | 1 | 1 |
| 改善点（コード品質） | 0 | 0 | 0 | 2 | 2 |
| 脆弱性 | 0 | 0 | 0 | 0 | 0 |
| **合計** | **0** | **0** | **1** | **3** | **4** |

---

## 各発見事項

---

### BUG-01 [Medium] `setdefault()` + `before_write` 変換フックが値を取り違える

**ファイル:** `src/nanasqlite/core.py` L1427-1433

```python
self[key] = default
if self._has_hooks:
    val = default          # ← BUG: before_write 変換後の値ではなく元の default を使用
    for hook in self._hooks:
        val = hook.after_read(self, key, val)
    return val
return default
```

PERF-18 の最適化として「書き込み後の `self[key]` 再読み込みを省略する」変更を加えた際、`before_write` フックが値を変換する場合（例: `ValidkitHook(coerce=True)` や `PydanticHook` による型変換）のケースを考慮していなかった。

**例:**
```python
schema = {"count": v.int()}
db = NanaSQLite("test.db", validator=schema, coerce=True)
# before_write フックが "5"（str）→ {"count": 5}（dict）に変換する場合
result = db.setdefault("k", "5")
# 旧実装: result == {"count": 5} (DBに保存された変換後の値)
# 新実装: result == "5"         (変換前の default を after_read に渡す → 誤り)
```

具体的には `ValidkitHook(coerce=True)` の `before_write` が値を変換する場合、`_data[key]` にはフック変換後の値が格納されているが、PERF-18 パスでは元の `default` に対して `after_read` フックを適用してしまう。

**修正案:** `self[key] = default` の後にキャッシュから実際に格納された値を読み直し、それに対して `after_read` フックを適用する。

```python
self[key] = default
if self._has_hooks:
    # before_write フックが default を変換した可能性があるため、
    # キャッシュから実際に格納された値を読み直す
    if not self._lru_mode:
        val = self._data[key]
    else:
        val = self._cache.get(key)
    for hook in self._hooks:
        val = hook.after_read(self, key, val)
    return val
return default
```

---

### PERF-21 [Low] `_check_connection()` の属性アクセス二重コスト

**ファイル:** `src/nanasqlite/core.py` L636-650

```python
def _check_connection(self) -> None:
    if self._is_closed:
        raise NanaSQLiteClosedError(...)
    if self._parent_closed:
        raise NanaSQLiteClosedError(...)
```

`_check_connection()` は `__setitem__` 等から毎回呼び出されるが、2 回の属性アクセス（`self._is_closed`, `self._parent_closed`）を毎回行っている。大多数のケースでは接続は開いており、両方とも False のはずである。

単一フラグ `_is_open: bool` を事前計算し、`if not self._is_open:` の 1 回アクセスで早期リターンできれば、書き込みパスで ~0.025 µs/write の削減が期待できる。

**修正案（将来的な改善）:** `__init__` でフラグを設定し、`close()` および `restore()` で更新する。当バージョンでは後回し可能。

---

### QUAL-01 [Low] `_ensure_cached()` の不要変数 `_`

**ファイル:** `src/nanasqlite/core.py` L934-935

```python
try:
    _ = self._data[key]
    return True
```

`_` 変数はキャッシュヒット確認のためだけに存在し、値を使用しない。Python の慣例として `_` は使い捨て変数に使われるが、`__getitem__` および `get()` では同じ内容を `val = self._data[key]` として読み込む実装になっている。

`_ensure_cached()` は `__contains__` や `__delitem__` など値を必要としないパスでも呼ばれるため、分離して置くことに意義はあるが、`_` ではなくコメントで意図を明確化することが望ましい。

**修正案:** リントルールに違反しない軽微な改善。当バージョンでは対応不要。

---

### QUAL-02 [Low] コメント「Hooks can only be added, never removed」が不正確

**ファイル:** `src/nanasqlite/core.py` L290-291

```python
# PERF-20: Pre-compute a single bool so hot-path read/write code avoids
# the cost of checking ``bool(self._hooks)`` (which must call __len__ on
# the list) on every operation.  Hooks can only be added, never removed.
```

コメントに「Hooks can only be added, never removed」と記載しているが、インスタンスを再作成すれば実質的にフックを削除できる。また `table()` の `hooks=None` または `hooks=[]` で子インスタンスのフックを空にすることもできる。`_has_hooks` フラグのスコープとして「このインスタンスのライフタイム中にフックが追加されたら True になり、False に戻らない」という意味である。

**修正案:** コメントを「フックはインスタンスのライフタイム中に追加可能だが削除はできない（`_has_hooks` は一度 True になると戻らない）」という正確な内容に修正する。

---

## 推奨対応優先度

### リリース前に修正すべき

| ID | 重要度 | 内容 |
|---|---|---|
| BUG-01 | Medium | `setdefault()` + コート変換フック組み合わせ時の返値誤り |

### 次バージョン（v1.5.3 final）で対応可能

| ID | 重要度 | 内容 |
|---|---|---|
| PERF-21 | Low | `_check_connection()` フラグ事前計算 |

### 将来的な改善

| ID | 重要度 | 内容 |
|---|---|---|
| QUAL-01 | Low | `_ensure_cached()` の `_ =` パターン改善 |
| QUAL-02 | Low | PERF-20 コメントの精度向上 |
