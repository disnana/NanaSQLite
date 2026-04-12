# NanaSQLite v1.5.4 プレリリース監査レポート

**対象バージョン:** v1.5.4  
**監査日:** 2026-04-11  
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
| バグ / 潜在バグ (BUG) | 0 | 0 | 1 | 1 | 2 |
| パフォーマンス (PERF) | 0 | 0 | 1 | 1 | 2 |
| コード品質 (QUAL) | 0 | 0 | 0 | 2 | 2 |
| セキュリティ (SEC) | 0 | 0 | 1 | 0 | 1 |
| **合計** | **0** | **0** | **3** | **4** | **7** |

---

## 発見事項

### BUG-01 [Medium] `__delitem__` — `before_delete` フックがロック外で呼ばれる

**ファイル:** `src/nanasqlite/core.py` L.1098–1101

```python
# PERF-20: use pre-computed flag instead of bool(self._hooks)
if self._has_hooks:
    for hook in self._hooks:
        hook.before_delete(self, key)  # ← ロック外
```

`__setitem__` では SEC-05 の修正によって `before_write` がロック内で呼ばれるようになったが、
`__delitem__` の `before_delete` は依然ロック外で実行されている。
`ForeignKeyHook.before_delete` 等がロック内の状態を前提とした読み取りを行う場合に
TOCTOU 競合が発生しうる。

現在 `before_delete` に読み取りを伴うフックの実装は存在しないが、
`__setitem__` との一貫性のためにロック内に移動することが望ましい。

**修正案（後方互換）:**

```python
# 非 v2 モード
else:
    with self._acquire_lock():
        if self._has_hooks:
            for hook in self._hooks:
                hook.before_delete(self, key)
        self._connection.execute(self._sql_kv_delete, (key,))
        ...
```

---

### BUG-02 [Low] `v2_engine.py` — Dead Letter Queue に上限なし

**ファイル:** `src/nanasqlite/v2_engine.py` L.98–99

```python
self.dlq: list[tuple[str, Any, float]] = []
```

「ポイズンピル」タスクが高頻度で失敗し続けると DLQ が無制限に成長し、
長期稼働アプリケーションで OOM を引き起こす可能性がある。

**修正案:**
`__init__` に `max_dlq_size: int = 1000` パラメータを追加し、
上限超過時は最古のエントリを FIFO で削除して `logger.warning` を出力する。

---

### PERF-01 [Medium] `UniqueHook.before_write` — O(N) 全件スキャン

**ファイル:** `src/nanasqlite/hooks.py` L.136–154

```python
for k, v in db.items():  # ← O(N)、全件 load_all() を呼ぶ
    if k == key:
        continue
    ...
    if other_val == check_val:
        raise NanaSQLiteValidationError(...)
```

`UniqueHook` は一意性確認のために `db.items()` を呼んでおり、内部で `load_all()` が実行される。
大規模 DB では O(N) の全件ロードが書き込みのたびに発生する。

**修正案（後方互換・追加 opt-in）:**
1. 逆引きインデックス（`{field_value → key}`）をメモリに保持し、O(1) で検索する高速モードを opt-in で追加。  
2. 既存の `O(N)` 動作はデフォルトのまま維持して後方互換を保つ。

---

### PERF-02 [Low] `hooks.py` — `re.compile` オブジェクトが `Pattern` 型チェックを経由

**ファイル:** `src/nanasqlite/hooks.py` L.31–34

```python
elif isinstance(key_pattern, Pattern):
    self._validate_regex_pattern(key_pattern.pattern)
    self._key_regex = key_pattern
```

`re.compile()` の結果を再度 `Pattern` として渡した場合、
既コンパイル済みにもかかわらず `_validate_regex_pattern` が再び呼ばれる。
通常は初期化時のみのため影響は軽微だが、一貫性のために
`Pattern` 型入力時はバリデーションをスキップする選択肢もある。

**修正案（Low Priority）:**
`Pattern` 型入力時のバリデーション呼び出しを省略してもよい（既にコンパイル済みのため安全）。
ただし、後から `pattern.pattern` だけを取り出して別途コンパイルするケースとの一貫性を考慮すること。

---

### QUAL-01 [Low] `compat.py` — `re2_module` の型アノテーション

**ファイル:** `src/nanasqlite/compat.py` L.52–57

```python
re2_module = _re2_module
...
re2_module = None  # type: ignore[assignment]
```

`re2_module` の型を `Any` として `# type: ignore` で押さえているが、
`types.ModuleType | None` を使うことで型安全性が向上する。

**修正案（Low Priority）:**
```python
import types
re2_module: types.ModuleType | None = _re2_module  # または None
```

---

### QUAL-02 [Low] `v2_engine.py` — DLQ エントリの型定義が `Any`

**ファイル:** `src/nanasqlite/v2_engine.py` L.98

```python
self.dlq: list[tuple[str, Any, float]] = []
```

`Any` を使うと mypy がペイロードの型を追跡できない。
NamedTuple や dataclass を使うとより安全で IDE サポートも向上する。

**修正案（Low Priority）:**
```python
from dataclasses import dataclass, field

@dataclass
class DLQEntry:
    error_msg: str
    item: object
    timestamp: float

self.dlq: list[DLQEntry] = field(default_factory=list)
```

---

### SEC-01 [Medium] `v2_engine.py` — `_staging_buffer` は DLQ に直接情報漏洩する

**ファイル:** `src/nanasqlite/v2_engine.py` L.295–310

```python
self.dlq.append((error_msg, item, time.time()))
```

DLQ エントリに含まれる `item` はスタック上の staging buffer オブジェクト全体を参照している。
`get_dlq()` が外部に公開されているため、エラー時に暗号化前のシリアライズ済み値が
アプリケーションコードに漏洩するリスクがある（ログ出力・monitoring 連携時）。

現時点では内部 API であり通常の使用では問題は露出しないが、
v2 モードのドキュメントにこのリスクを明記することを推奨。

**修正案:**
1. DLQ エントリの `item` を鍵名と操作種別のみを保持するサマリに削減する（値は含めない）。
2. または DLQ エントリのシリアライズ表現をドキュメントに明記する。

---

## 優先対応テーブル

### リリース前に修正すべき項目

| ID | カテゴリ | 深刻度 | 内容 |
|----|---------|--------|------|
| BUG-01 | BUG | Medium | `before_delete` をロック内に移動 |

### 次バージョンで対応可能

| ID | カテゴリ | 深刻度 | 内容 |
|----|---------|--------|------|
| BUG-02 | BUG | Low | DLQ への `max_dlq_size` 追加 |
| PERF-01 | PERF | Medium | `UniqueHook` の O(1) opt-in 高速化 |
| SEC-01 | SEC | Medium | DLQ のペイロード情報漏洩リスクのドキュメント化 |

### 将来的な改善

| ID | カテゴリ | 深刻度 | 内容 |
|----|---------|--------|------|
| PERF-02 | PERF | Low | `Pattern` 型入力時の再バリデーション省略 |
| QUAL-01 | QUAL | Low | `re2_module` の型アノテーション改善 |
| QUAL-02 | QUAL | Low | DLQ エントリの型定義改善 |

---

## フェーズ 2: POC 確認

### BUG-01 POC（`etc/poc/poc_bug01_before_delete_outside_lock.py`）

```python
"""
BUG-01 [Medium] __delitem__ の before_delete がロック外で呼ばれる

現行: before_delete はロック取得前に実行される。
修正後: 非 v2 モードでは before_delete もロック内で実行される。
"""
import threading
import tempfile, os
from nanasqlite import NanaSQLite
from nanasqlite.hooks import BaseHook

class LockInspectDeleteHook(BaseHook):
    def __init__(self):
        super().__init__()
        self.lock_held_during_delete = []
    def before_delete(self, db, key):
        self.lock_held_during_delete.append(db._lock._is_owned())

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)
try:
    db = NanaSQLite(path)
    hook = LockInspectDeleteHook()
    db.add_hook(hook)
    db["k"] = "v"
    del db["k"]
    if hook.lock_held_during_delete and hook.lock_held_during_delete[0]:
        print("PASS: before_delete はロック内で実行された")
    else:
        print("BUG: before_delete はロック外で実行された")
    db.close()
finally:
    os.unlink(path)
```

現行実装ではこの POC は `BUG: before_delete はロック外で実行された` を出力します。

---

## フェーズ 3: パッチ状況

| ID | 修正状況 | 備考 |
|----|---------|------|
| SEC-05 (UniqueHook TOCTOU) | ✅ v1.5.4 で修正済み | `__setitem__` の before_write をロック内に移動 |
| SEC-06 (RE2 opt-in) | ✅ v1.5.4 で実施済み | google-re2 オプション追加、`re_fallback` パラメータ追加 |
| QUAL-10 (validkit stub) | ✅ v1.5.4 で修正済み | ImportError スタブ |
| BUG-01 (before_delete) | ⬜ 次期バージョンで対応 | |
| BUG-02 (DLQ上限) | ⬜ 次期バージョンで対応 | |

---

## フェーズ 4: 未対応項目 — 後方互換 vs 非後方互換 対応提案

以下では、v1.5.4 で未対応となった各発見事項について  
「後方互換を保つ修正案」と「後方互換を壊す修正案」の両観点から提案します。

---

### BUG-01 — `__delitem__` の `before_delete` がロック外で実行される

#### 後方互換を保つ修正案（推奨）

```python
# core.py __delitem__ の非 v2 パス
else:
    with self._acquire_lock():
        if self._has_hooks:
            for hook in self._hooks:
                hook.before_delete(self, key)
        self._connection.execute(self._sql_kv_delete, (key,))
        ...
```

**メリット:**
- 公開 API・シグネチャ変更なし。既存の `BaseHook` サブクラスはそのまま動作する。
- `__setitem__` の SEC-05 修正と対称的な変更であり、理解しやすい。
- `threading.RLock` を使用しているため再入可能。`before_delete` 内で `db.get()` を呼んでもデッドロックしない。

**デメリット:**
- フック内で長時間処理や I/O を行う実装では、ロック保持時間が延びてスループットが低下する。
- フック内からデッドロックしうる外部ロックを呼ぶ既存コードがあれば影響を受ける（稀）。

#### 後方互換を壊す修正案

```python
class BaseHook:
    def before_delete(self, db: Any, key: str) -> None:
        """NOTE: v1.5.5 より、このメソッドはロック保持中に呼ばれます。
        実装はリエントラントであること。"""
        pass
```

ロック内移動に加え、`before_delete` が「ロック保持中に呼ばれる」ことをドキュメントで明示し、
フック実装者に準拠を要求するコントラクト変更として扱う。

**メリット:**
- 意味的に明確であり、ロック外での `before_delete` に依存するバグを早期発見できる。
- 将来の非同期対応（`async def before_delete`）への移行とともに設計変更としてまとめられる。

**デメリット:**
- フック内で `asyncio`・外部 I/O・別スレッドのロックを取得する実装は動作変更を受ける。
- セマンティクス変更を BREAKING CHANGE としてメジャーバージョンアップが必要。

---

### BUG-02 — `v2_engine.py` DLQ にサイズ上限がない

#### 後方互換を保つ修正案（推奨）

```python
class V2Engine:
    def __init__(
        self,
        ...,
        max_dlq_size: int = 0,  # 0 = 上限なし（既存動作と同じ）
    ):
        self._max_dlq_size = max_dlq_size
        self.dlq: list[tuple[str, Any, float]] = []

    def _append_dlq(self, error_msg: str, item: Any) -> None:
        if self._max_dlq_size > 0 and len(self.dlq) >= self._max_dlq_size:
            oldest = self.dlq.pop(0)
            logger.warning("DLQ full (max=%d): evicting oldest entry: %s", self._max_dlq_size, oldest[0])
        self.dlq.append((error_msg, item, time.time()))
```

デフォルト `max_dlq_size=0` で既存動作を保ちつつ、opt-in で上限を設定できる。

**メリット:**
- デフォルト動作が変わらないため既存コードへの影響ゼロ。
- `max_dlq_size` を明示したコードは OOM リスクを回避できる。
- 段階的に導入可能（ドキュメント追記 → デフォルト変更を次のメジャーバージョンで）。

**デメリット:**
- デフォルト `0`（無制限）のままでは BUG-02 は解消されない。
  利用者が明示的に `max_dlq_size` を設定しない限り問題は残る。

#### 後方互換を壊す修正案

```python
def __init__(self, ..., max_dlq_size: int = 1000):  # デフォルト値を有限値に変更
```

デフォルト値を `1000` などの有限値に設定し、長期稼働アプリケーションでの OOM を防ぐ。

**メリット:**
- 安全なデフォルトになり、ほとんどのユースケースで OOM リスクが消える。
- 「Secure by default」の原則に沿う。

**デメリット:**
- 既存コードが `get_dlq()` でエントリ数に依存している場合に動作変更。
- テストで DLQ サイズを大量投入しているコードが失敗しうる。
- CHANGELOG に BREAKING CHANGE として明記が必要。

---

### PERF-01 — `UniqueHook.before_write` の O(N) 全件スキャン

#### 後方互換を保つ修正案（推奨）

```python
class UniqueHook(BaseHook):
    def __init__(self, field: str, ..., use_index: bool = False):
        super().__init__(...)
        self._use_index = use_index
        self._index: dict[Any, str] = {}  # value → key の逆引き

    def before_write(self, db, key, value):
        if self._use_index:
            # O(1) パス: 逆引きインデックスで重複チェック
            check_val = ...
            existing_key = self._index.get(check_val)
            if existing_key and existing_key != key:
                raise NanaSQLiteValidationError(...)
            self._index[check_val] = key
        else:
            # O(N) パス: 既存動作（デフォルト）
            for k, v in db.items():
                ...
```

**メリット:**
- デフォルト動作変更なし。既存の `UniqueHook` はそのまま動作する。
- `use_index=True` を opt-in で指定することで O(1) チェックが可能。
- インデックスの整合性を `UniqueHook` が自己管理するため利用者への負担が少ない。

**デメリット:**
- インデックスはインメモリのため、複数プロセスや DB の外部更新に追従しない。
- `UniqueHook` インスタンスが長期保持される場合、インデックスのメモリ使用量が増加する。
- インデックスの初期化（既存データ読み込み）のコストが初回 `before_write` 時に発生する。

#### 後方互換を壊す修正案

逆引きインデックスを `UniqueHook` のデフォルト動作にし、`use_index=False` で旧動作に戻せるようにする。

```python
class UniqueHook(BaseHook):
    def __init__(self, field: str, ..., use_index: bool = True):  # デフォルトを True に
        ...
```

**メリット:**
- 大規模 DB での書き込みパフォーマンスが自動的に改善される。
- ほとんどの用途でインデックス使用が有利。

**デメリット:**
- インメモリインデックスの同期問題（外部書き込み・マルチプロセス）により既存コードが誤動作する可能性。
- インデックスのメモリ使用量が増加し、小規模用途では無駄になる。
- BREAKING CHANGE としてメジャーバージョンアップを伴う。

---

### SEC-01 — DLQ エントリが平文値（`item`）を含む情報漏洩リスク

#### 後方互換を保つ修正案（推奨）

DLQ API を変更せず、リスクをドキュメントに明記する。

```markdown
<!-- SECURITY.md / v2_engine.py docstring に追記 -->
> **警告**: `get_dlq()` が返すエントリの `item` フィールドには、
> 書き込みに失敗したシリアライズ済み値が含まれます。
> ログ出力・monitoring 連携時に機密情報が漏洩しないよう注意してください。
```

**メリット:**
- コード変更なし。既存の `get_dlq()` 利用コードへの影響ゼロ。
- 迅速に対処可能。

**デメリット:**
- 実際の情報漏洩リスクは残る。ドキュメント未読の利用者は対策できない。

#### 後方互換を壊す修正案

DLQ エントリから `item` を削除し、エラーサマリ（鍵名・操作種別・タイムスタンプ）のみを保持する。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class DLQEntry:
    error_msg: str
    key: str          # 値ではなく鍵名のみ
    operation: str    # "write" / "delete" など
    timestamp: float

self.dlq: list[DLQEntry] = []
```

**メリット:**
- `item`（平文値）が DLQ に入らないため情報漏洩リスクが根本解消される。
- `frozen=True` にすることで不変性を保証し、監査ログとしての信頼性が向上する。

**デメリット:**
- 既存コードが `dlq[n][1]`（item フィールド）を参照している場合に破壊的変更となる。
- DLQ からリトライ処理を実装している場合、`item` がないとリトライ不可になる。
- BREAKING CHANGE としてメジャーバージョンアップが必要。

---

---

## フェーズ 5: CI 確認結果

- `python -m tox -e lint` → ✅ PASS
- `python -m tox -e type` → ✅ PASS（11 ファイル、エラーなし）
- `pytest tests/ --ignore=...benchmark...` → ✅ **899 passed, 8 skipped**（v1.5.3 の 881 から +18）
  - `google-re2` を `dev` extras に追加し、モックなしの実 RE2 テストに移行
  - `re_fallback` パラメータのテスト 4 件を追加
  - CodeQL 指摘の重複 import を修正

---

## フェーズ 6: リリース準備状況

| 項目 | 状態 |
|------|------|
| `src/nanasqlite/__init__.py` → `"1.5.4"` | ✅ 更新済み |
| `CHANGELOG.md` — 日本語・英語 v1.5.4 エントリ | ✅ 追加済み |
| `SECURITY.md` — SEC-05 / SEC-06 記載 | ✅ 更新済み |
| `docs/ja/guide/pysentinel_response_20260411.md` | ✅ 新規作成・更新済み |
| `pyproject.toml` — `re2` extra + `all` | ✅ 更新済み |
