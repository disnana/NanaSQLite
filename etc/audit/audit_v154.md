# NanaSQLite v1.5.4 プレリリース監査レポート

**対象バージョン:** v1.5.4rc1 → v1.5.4  
**監査日:** 2026-04-19  
**対象ファイル:**
- `src/nanasqlite/core.py`
- `src/nanasqlite/async_core.py`
- `src/nanasqlite/cache.py`
- `src/nanasqlite/utils.py`
- `src/nanasqlite/hooks.py`
- `src/nanasqlite/compat.py`
- `src/nanasqlite/sql_utils.py`
- `src/nanasqlite/v2_engine.py`
- `src/nanasqlite/exceptions.py`
- `src/nanasqlite/protocols.py`

---

## 総括テーブル

| カテゴリ | Critical | High | Medium | Low | 計 |
|---------|----------|------|--------|-----|-----|
| バグ / 潜在バグ (BUG) | 0 | 0 | 2 | 1 | 3 |
| パフォーマンス (PERF) | 0 | 0 | 1 | 1 | 2 |
| コード品質 (QUAL) | 0 | 0 | 0 | 2 | 2 |
| セキュリティ (SEC) | 0 | 0 | 1 | 0 | 1 |
| **合計** | **0** | **0** | **4** | **4** | **8** |

---

## 発見事項

### BUG-01 [Medium] `pop()` — `before_delete` フックがロック外で呼ばれる

**ファイル:** `src/nanasqlite/core.py` L.1358–1361

```python
if self._has_hooks:
    for hook in self._hooks:
        hook.before_delete(self, key)  # ← ロック外（v2 / 非v2 共通パス）
```

`__delitem__` の非 v2 パスは v1.5.4rc1 の SEC-05 修正でロック内になったが、
`pop()` の `before_delete` 呼び出しは非 v2 パスでもロック外のままである。
`__delitem__` との一貫性が失われており、`before_delete` とDB削除の間に
別スレッドがDBを変更する TOCTOU 窓が残る。

**修正案:** 非 v2 パスの `before_delete` を `_acquire_lock()` のブロック内に移動する。
`self._lock` は `threading.RLock` なので再入呼び出し可能。

---

### BUG-02 [Medium] `batch_update()` — non-coerce パスでフック返り値が破棄される

**ファイル:** `src/nanasqlite/core.py` L.1582–1587

```python
else:
    # Validate only path (no new dict allocation)
    for k, v in mapping.items():
        temp_v = v
        for hook in hooks:
            temp_v = hook.before_write(self, k, temp_v)
        # temp_v は破棄される ← バグ
```

`coerce=False`（デフォルト）の場合、`before_write` フックの返り値が使われず
元の `v` がそのまま DB に書き込まれる。`__setitem__` では `coerce` 設定に関わらず
常にフック返り値が使用されるため、挙動が一致しない。
`PydanticHook` などの変換フックを `batch_update` で使用すると
変換が無効になりサイレントなデータ不整合が生じる。

**修正案:** non-coerce パスでも copy-on-write 方式でフック変換値を保持・使用する
（coerce パスと同じロジックを適用する）。

---

### BUG-03 [Low] `batch_delete()` — `before_delete` フックがロック外で呼ばれる

**ファイル:** `src/nanasqlite/core.py` L.1742–1746

```python
if self._has_hooks:
    for key in keys:
        if self._ensure_cached(key):
            for hook in self._hooks:
                hook.before_delete(self, key)  # ← ロック外
```

`batch_delete` は非 v2 モードで `before_delete` をロック外で呼ぶため、
フック呼び出しとDBへの実際の削除の間に TOCTOU 窓が存在する。
`__delitem__` の SEC-05 修正と一致させるべきである。

**修正案:** 非 v2 パスではロック取得後に `before_delete` を呼び出す。

---

### PERF-01 [Medium] `UniqueHook.before_write` — O(N) 全件スキャン

**ファイル:** `src/nanasqlite/hooks.py` L.272

```python
for k, v in db.items():  # ← O(N)、全件 load_all() を呼ぶ
```

一意性確認のたびに全件読み込みが発生する。大規模 DB では致命的なボトルネックになる。

**修正案（後方互換・opt-in）:** `use_index=True` パラメータで逆引きインデックスを使う
高速モードをオプションで追加する（次バージョンで対応可能）。

---

### PERF-02 [Low] `BaseHook.__init__` — `Pattern` 型入力時に再コンパイル

**ファイル:** `src/nanasqlite/hooks.py` L.70–72

```python
elif isinstance(key_pattern, Pattern):
    self._validate_regex_pattern(key_pattern.pattern)
    self._key_regex = key_pattern
```

既コンパイル済みの `Pattern` オブジェクトを渡した場合でも `re.compile()` で再コンパイルが
発生していた。初期化時のみの影響で軽微だが、再コンパイルは不要。

**修正案（Low Priority）:** `Pattern` 型入力時は `re.compile()` の再コンパイルをスキップし、
コンパイル済みオブジェクトをそのまま利用する。セキュリティ上、`_validate_regex_pattern(key_pattern.pattern)`
による ReDoS バリデーションは引き続き実行すること（コンパイル済み Pattern 経由のブラックリスト迂回を防止）。

---

### QUAL-01 [Low] `compat.py` — `re2_module` の型アノテーション

**ファイル:** `src/nanasqlite/compat.py` L.58–59

```python
re2_module = None  # type: ignore[assignment]
```

`types.ModuleType | None` を使うことで型安全性が向上する。

**修正案（Low Priority）:**
```python
import types
re2_module: types.ModuleType | None = None
```

---

### QUAL-02 [Low] `v2_engine.py` — DLQ エントリの型定義が `Any`

**ファイル:** `src/nanasqlite/v2_engine.py` L.99

```python
self.dlq: list[tuple[str, Any, float]] = []
```

`Any` を使うと mypy がペイロードの型を追跡できない。NamedTuple や dataclass の利用を推奨。

**修正案（Low Priority）:** `DLQEntry` dataclass を定義して型安全性を向上させる。

---

### SEC-01 [Medium] `v2_engine.py` — DLQ にシリアライズ済み値が漏洩する

**ファイル:** `src/nanasqlite/v2_engine.py` L.154, L.444

```python
self.dlq.append((error_msg, item, time.time()))
```

DLQ エントリには KVS ポイズンピルの `item`（`op["value"]` = シリアライズ済み値）が含まれる。
暗号化なしの DB では、`get_dlq()` 経由でプレーンテキストの値が外部コードに漏洩するリスクがある。
ログ出力・monitoring 連携での情報漏洩に注意が必要。

**修正案:** DLQ ドキュメントにこのリスクを明記すること（コード変更は破壊的変更になるため次バージョン以降）。

---

## 優先対応テーブル

### リリース前に修正すべき項目

| ID | カテゴリ | 深刻度 | 内容 |
|----|---------|--------|------|
| BUG-01 | BUG | Medium | `pop()` の `before_delete` をロック内へ移動（SEC-05 一貫性） ✅ |
| BUG-02 | BUG | Medium | `batch_update()` non-coerce パスのフック返り値保持 ✅ |

### 次バージョンで対応可能 → v1.5.4 で前倒し実施

| ID | カテゴリ | 深刻度 | 内容 |
|----|---------|--------|------|
| BUG-03 | BUG | Low | `batch_delete()` の `before_delete` をロック内へ移動 ✅ |
| PERF-01 | PERF | Medium | `UniqueHook` の O(1) opt-in 高速化（`use_index=True`） ✅ |
| SEC-01 | SEC | Medium | DLQ ペイロード漏洩リスクのドキュメント化 ✅ |

### 将来的な改善 → v1.5.4 で前倒し実施

| ID | カテゴリ | 深刻度 | 内容 |
|----|---------|--------|------|
| PERF-02 | PERF | Low | `Pattern` 型入力時の再バリデーション省略 ✅ |
| QUAL-01 | QUAL | Low | `re2_module` 型アノテーション改善 ✅ |
| QUAL-02 | QUAL | Low | DLQ エントリ型定義改善（`DLQEntry` dataclass） ✅ |

---

## フェーズ 2: POC スクリプト

POC スクリプトは `etc/poc/` ディレクトリに作成済み:

- `poc_bug01_v154_pop_hook_outside_lock.py` — BUG-01 再現・検証
- `poc_bug02_v154_batch_update_hook_discarded.py` — BUG-02 再現・検証
- `poc_bug03_v154_batch_delete_hook_outside_lock.py` — BUG-03 再現・検証

---

## フェーズ 3: パッチ状況

| ID | 修正状況 | 備考 |
|----|---------|------|
| BUG-01 (pop hook lock) | ✅ v1.5.4 で修正済み | 非 v2 パスで `before_delete` をロック内に移動 |
| BUG-02 (batch_update hook result) | ✅ v1.5.4 で修正済み | non-coerce パスでフック返り値を保持 |
| BUG-03 (batch_delete hook lock) | ✅ v1.5.4 で修正済み | 非 v2 パスで `before_delete` をロック内に移動 |
| PERF-01 (UniqueHook O(N)) | ✅ v1.5.4 で前倒し実施 | `use_index=True` opt-in 逆引きインデックス |
| PERF-02 (Pattern 再コンパイル) | ✅ v1.5.4 で前倒し実施 | `Pattern` 型入力時は再コンパイルを省略。`_validate_regex_pattern(key_pattern.pattern)` による ReDoS バリデーションは継続 |
| SEC-01 (DLQ exposure) | ✅ v1.5.4 で前倒し実施 | `DLQEntry`・`get_dlq()`・`_add_to_dlq()` に SEC-01 注記追加 |
| QUAL-01 (re2_module 型) | ✅ v1.5.4 で前倒し実施 | `types.ModuleType \| None` アノテーション |
| QUAL-02 (DLQ 型) | ✅ v1.5.4 で前倒し実施 | `DLQEntry` dataclass 導入 |

---

## フェーズ 5: CI 確認結果

- `python -m tox -e lint` → ✅ PASS
- `python -m tox -e type` → ✅ PASS
- `pytest tests/ --ignore=...benchmark...` → ✅ **PASS**

---

## フェーズ 6: リリース準備状況

| 項目 | 状態 |
|------|------|
| `src/nanasqlite/__init__.py` → `"1.5.4"` | ✅ 更新済み |
| `CHANGELOG.md` — 日本語・英語 v1.5.4 エントリ更新 | ✅ 更新済み |
