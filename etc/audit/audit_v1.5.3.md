# NanaSQLite v1.5.3 プレリリース監査レポート

**対象バージョン:** v1.5.3  
**監査日:** 2026-04-07  
**監査対象ファイル（差分中心）:**
- `src/nanasqlite/core.py`
- `src/nanasqlite/utils.py`
- `tests/test_v153_perf_fixes.py`
- `tests/test_benchmark.py`
- `CHANGELOG.md`
- `src/nanasqlite/__init__.py`

---

## 総括テーブル

| カテゴリ | Critical | High | Medium | Low | 計 |
|---------|----------|------|--------|-----|-----|
| バグ / 潜在バグ (BUG) | 0 | 0 | 0 | 0 | 0 |
| パフォーマンス (PERF) | 0 | 1 | 1 | 0 | 2 |
| コード品質 (QUAL) | 0 | 0 | 0 | 1 | 1 |
| セキュリティ (SEC) | 0 | 0 | 0 | 0 | 0 |
| **合計** | **0** | **1** | **1** | **1** | **3** |

---

## 発見事項

### PERF-12 [High] `get()` メソッドの LRU/TTL モードで二重キャッシュルックアップが残存

**ファイル:** `src/nanasqlite/core.py` L1115–1132

```python
def get(self, key: str, default: Any = None) -> Any:
    ...
    else:  # LRU/TTL モード
        if not self._ensure_cached(key):   # ← _ensure_cached 内で cache.get() が呼ばれる
            return default
        val = self._cache.get(key)         # ← もう一度 cache.get() を呼んでいる
```

v1.5.3 の PERF-09 で `__getitem__` の LRU/TTL ブランチは「`_data` 在籍確認 → `cache.get()` 1 回」に最適化されましたが、同じ構造を持つ `get()` メソッドは修正が漏れています。

`_ensure_cached()` は LRU/TTL モードでキャッシュヒット時に `self._cache.get()` を内部で呼び出し、続いて呼び元も `self._cache.get()` を再度呼ぶため、1 回の読み取りに対して `move_to_end()` が 2 回実行されます。`get()` は `to_dict()` / `items()` のホットパスでも利用されるため、影響範囲が大きいです。

**修正案:**

```python
else:  # LRU/TTL モード（PERF-12）
    if key in self._data:
        val = self._cache.get(key)
        if val is MISSING:
            return default
    else:
        if not self._ensure_cached(key):
            return default
        val = self._cache.get(key)
```

---

### PERF-13 [Medium] `values()` / `items()` が Unbounded モードでも MISSING フィルタを適用

**ファイル:** `src/nanasqlite/core.py` L1103–1113

```python
def values(self) -> list:
    ...
    return [v for v in self._cache.get_data().values() if v is not MISSING]

def items(self) -> list:
    ...
    return [(k, v) for k, v in self._cache.get_data().items() if v is not MISSING]
```

PERF-08 では `to_dict()` を Unbounded モードで `dict(self._data)` を直接返すよう最適化しましたが、`values()` と `items()` には同じ最適化が適用されていません。Unbounded モードでは `_data` に MISSING センチネルが格納されることはなく、フィルタは常に無効です。

**修正案:**

```python
def values(self) -> list:
    self._check_connection()
    self.load_all()
    if not self._lru_mode:
        return list(self._data.values())
    return [v for v in self._cache.get_data().values() if v is not MISSING]

def items(self) -> list:
    self._check_connection()
    self.load_all()
    if not self._lru_mode:
        return list(self._data.items())
    return [(k, v) for k, v in self._cache.get_data().items() if v is not MISSING]
```

---

### QUAL-01 [Low] PERF-10 により非 strict モードの警告発火回数が暗黙的に変化

**ファイル:** `src/nanasqlite/core.py` L718–724

```python
# 旧: 各パターンに個別 re.search() → 複数パターンにマッチすると複数回 warnings.warn()
for pattern, msg in dangerous_patterns:
    if re.search(pattern, str(expr), re.IGNORECASE):
        warnings.warn(msg, UserWarning, stacklevel=2)

# 新: 1 つの正規表現 → 1 件しか warnings.warn() しない
if _DANGEROUS_SQL_RE.search(str(expr)):
    warnings.warn(full_msg, UserWarning, stacklevel=2)
```

strict=False（警告モード）のとき、式に複数の危険パターン（例: `; DROP TABLE`）が含まれる場合、以前は 2 つの `UserWarning` が発火していたが、新実装では 1 つのみになります。コードの正確性・セキュリティには影響しませんが、`warnings.catch_warnings()` などで警告カウントに依存するコードがあると動作が変わります。

CHANGELOG やコメントへの追記で対応可能な低優先度の品質問題です。

**修正案:** コードの変更は不要。ただし `_validate_expression()` の docstring または CHANGELOG の PERF-10 エントリに以下を追記する:

> 非 strict モードでは、複数の危険パターンが同時にマッチしても警告は 1 件のみ発行される（以前は複数件）。

---

## 推奨対応優先度

| ID | 重要度 | タイトル | 優先度 |
|----|--------|---------|--------|
| PERF-12 | High | `get()` の二重キャッシュルックアップ除去 | リリース前に修正 |
| PERF-13 | Medium | `values()` / `items()` の Unbounded モード最適化 | リリース前に修正 |
| QUAL-01 | Low | PERF-10 の警告回数変化を changelog に明記 | 次バージョンで対応可能 |

---

## audit_prompt.md 準拠チェック

- フェーズ1（監査）: 本レポート（日本語）✅
- フェーズ2（POC）: `etc/poc/poc_perf12_get_double_lookup.py`, `etc/poc/poc_perf13_values_items_filter.py` を作成
- フェーズ3（パッチ）: `core.py` に PERF-12 / PERF-13 を修正適用
- フェーズ4（pytest）: `tests/test_audit_poc.py` に検証テストを追加
- フェーズ5（CI）: lint / type / pytest（ベンチ除外）を実施
- フェーズ6（リリース準備）: CHANGELOG.md v1.5.3 エントリを更新
