# NanaSQLite セキュリティ分析レポート

---

## CRITICAL

### 1. SQLインジェクション — `pragma()` メソッド (core.py:3346, 3365)

**根拠**  
静的スキャン（セクション7）で最も危険なのが `pragma()` 関数です。`_sanitize_identifier` を**経由せずに** `pragma_name` および `value_str` を直接 f-string でSQL文に埋め込んでいます。変数スコープ（セクション4）を見ると `allowed_pragmas` という変数が存在しますが、呼び出しグラフ上では `_validate_expression` も `_sanitize_identifier` も呼ばれていません。

```
NanaSQLite.pragma --> re_match (パターン確認のみ)
                  --> self_execute (そのまま実行)
```

**悪用シナリオ**  
```python
# 攻撃者が細工した pragma_name を渡せる場合
db.pragma("cache_size; ATTACH DATABASE '/etc/passwd' AS pwned; --")
# → PRAGMA cache_size; ATTACH ... が実行される
```

**修正骨格**
```python
# 1. pragma_name を厳格な許可リストで検証
ALLOWED_PRAGMA_NAMES = frozenset({"cache_size", "journal_mode", "wal_autocheckpoint", ...})
if pragma_name not in ALLOWED_PRAGMA_NAMES:
    raise NanaSQLiteValidationError(...)

# 2. value は型別にパラメータバインド可能な形式に変換
#    文字列値は引用符付きリストから選択制にする
#    数値は int/float キャストで検証
```

---

### 2. SQLインジェクション — `V2Engine._recover_chunk_via_dlq()` (v2_engine.py:467, 471)

**根拠**  
DLQ（Dead Letter Queue）からのリカバリ処理で `table_name` を直接 f-string に埋め込んでいます。呼び出しグラフを見ると `_recover_chunk_via_dlq` は `_sanitize_identifier` を**呼んでいません**（`_process_kvs_chunk` も同様）。DLQエントリは一度失敗したデータなので、その `table_name` が正規化済みとは限りません。

```
V2Engine._perform_flush --> V2Engine._recover_chunk_via_dlq
                             --> cursor.execute(f"INSERT OR REPLACE INTO {table_name}...")
```

**悪用シナリオ**  
DLQにエントリを意図的に蓄積させた後、table_name を細工したオペレーションでリカバリをトリガーすると、任意のDDL/DML文が実行される可能性があります。

**修正骨格**
```python
# kvs_set/kvs_delete 受付時点で table_name をサニタイズし、
# sanitized 済みの名前のみ DLQ に格納する
def kvs_set(self, table_name, key, value):
    safe_name = _sanitize_identifier(table_name)  # ここで検証
    self._staging[safe_name][key] = ...
```

---

### 3. SQLインジェクション — `_shared_query_impl` / `query()` / `query_with_pagination()` の PRAGMA 呼び出し

**根拠**  
`PRAGMA table_info({safe_table_name})` という形で f-string を使っています。変数名に `safe_` プレフィックスが付いているので `_sanitize_identifier` は通っているはずですが、呼び出しグラフ上で `AsyncNanaSQLite._shared_query_impl` → `self._db._sanitize_identifier` の経路は確認できます。ただし `_sanitize_identifier` の実装（core.py:523）のキャッシュ（`lru_cache`）が正しく機能しない edge case — たとえば `"` で囲まれた識別子が内側でさらに `"` を含む場合 — にリスクが残ります。

**修正骨格**
```python
# _sanitize_identifier で内側の " を必ずエスケープ
inner = identifier.replace('"', '""')
return f'"{inner}"'
# さらに PRAGMA は識別子引用符が効かないため、
# PRAGMA table_info では許可リスト方式のみ使用する
```

---

## HIGH

### 4. テイントフロー — SSRF疑い (セクション6)

**根拠**  
スキャナーは `coerce` パラメータが `http_query` 経由で `kwargs.get` に流れると報告しています。構造上、`AsyncNanaSQLite.__init__` が `**kwargs` をそのまま下位に渡している可能性があります。`db_path` がユーザー入力から来る場合、`file::memory:?cache=shared` や `file:///etc/` など任意パスへのアクセスが可能です（SQLite URI filename の問題）。

**悪用シナリオ**
```python
# HTTP リクエストの query string から db_path が来る場合
db_path = request.args.get("db")  # "file:///etc/shadow?mode=ro"
db = AsyncNanaSQLite(db_path=db_path, ...)
```

**修正骨格**
```python
# db_path の受付時に URI スキームと絶対パスを検証
import os, re
def _validate_db_path(path: str) -> str:
    if path in (":memory:", ""):
        return path
    if path.startswith("file:"):
        raise NanaSQLiteValidationError("URI形式は許可されていません")
    abs_path = os.path.realpath(path)
    if not abs_path.startswith(ALLOWED_BASE_DIR):
        raise NanaSQLiteValidationError("許可されたディレクトリ外です")
    return abs_path
```

---

### 5. 認証チェック回避経路 — `table()` メソッド (core.py:3514)

**根拠**  
呼び出しグラフを見ると `NanaSQLite.table()` は：

```
NanaSQLite.table --> self._check_connection (OK)
                  --> NanaSQLite(NanaSQLite) [新インスタンス作成]
```

新インスタンスは `_shared_connection` と `_shared_lock` を共有しますが、**親の `_validator` や `_hooks` を引き継がない可能性**があります。変数スコープを見ると `resolved_validator`, `resolved_hooks` として別途解決しています。Hookが引き継がれない場合、子テーブルインスタンスではバリデーション・外部キー制約・UniqueHookが無効になります。

**悪用シナリオ**
```python
parent = NanaSQLite("db.sqlite", validator=strict_schema, hooks=[unique_hook])
child = parent.table("other_table")  # バリデーションが外れる可能性
child["evil_key"] = malicious_data   # バリデーション無しで書き込める
```

**修正骨格**
```python
# table() 内で hooks の継承ロジックを明示的に確認
resolved_hooks = hooks if hooks is not None else list(self._hooks)  # 明示的コピー
# validator も同様に親から継承することをデフォルトに
```

---

### 6. 競合状態 — `UniqueHook.before_write` (complexity=41, hooks.py:363)

**根拠**  
最高複雑度(41)の関数であり、`_value_to_key`（逆引きインデックス）の操作中にロック競合が発生しうる構造です。`UniqueHook` は独自に `threading.RLock` を持ちますが（`__init__` で確認）、`_build_index(db)` が `db._get_raw()` を呼び出す際に NanaSQLite 側のロックと異なるロックオブジェクトを使用しています。これはデッドロックまたは TOCTOU（Time-of-Check Time-of-Use）の温床です。

**悪用シナリオ**  
並行書き込み時に一意制約が正しく機能せず、重複データが挿入される。

**修正骨格**
```python
# before_write 全体を NanaSQLite の _acquire_lock コンテキスト内で実行するか、
# UniqueHook のロックと NanaSQLite のロックを同一オブジェクトに統一する
# または db._get_raw() 呼び出しを UniqueHook のロック取得前に完了させる
with self._lock:
    # インデックス確認と更新をアトミックに
    old_val = db._get_raw(key)  # ← この呼び出しはロック外に出してはいけない
    ...
```

---

## MEDIUM

### 7. `os.urandom` の誤検知 — 実際は問題なし

**根拠**  
スキャナーが `weak_crypto (CWE-338)` と報告していますが、`os.urandom` は暗号論的に安全な乱数生成器です。これは**誤検知**です。ただし `_serialize` で AEAD（AES-GCM / ChaCha20-Poly1305）のノンス生成に使っているなら正しい実装です。

**ただし注意点**: `_serialize` で `os.urandom` によるノンスを生成し、同じキーで**ノンスが衝突した場合**（AES-GCM では 96bit ノンス＝約50億回で誕生日衝突確率が上昇）に暗号テキストの完全性が破られます。

**修正骨格**
```python
# AES-GCM ノンスはカウンターベースにするか、
# 大容量書き込みが想定される場合は ChaCha20-Poly1305 を推奨
# または同一キーでの書き込み回数をメトリクスで監視し、
# 一定回数でキーローテーションを促す警告を出す
```

---

### 8. `ExpiringDict._set_timer` でのイベントループ混在

**根拠**  
呼び出しグラフを見ると：
```
ExpiringDict._set_timer --> asyncio.get_running_loop --> loop.call_later
                         --> threading.Timer (フォールバック)
```

同期コンテキスト（スレッド）から `asyncio.get_running_loop()` を呼ぶと `RuntimeError` が発生し、`threading.Timer` にフォールバックします。しかし async コンテキストから呼ばれた場合、`loop.call_later` で登録したコールバックが `_delete_from_db_on_expire` → `self._connection.execute` を呼び出すと、スレッドセーフでない操作になります（apsw の Connection はスレッドローカルです）。

**修正骨格**
```python
# 有効期限コールバックは常にスレッドプール経由で実行するか、
# asyncio.run_coroutine_threadsafe を使って正しいループに投げる
# または TTL管理は DB層（SQLite の rowid + timestamp列）に委譲する
```

---

## 総括・優先修正順位

| 優先度 | 項目 | 対応工数 |
|:---|:---|:---|
| **今すぐ** | `pragma()` の許可リスト化 | 小 |
| **今すぐ** | `_recover_chunk_via_dlq` の識別子サニタイズ | 小 |
| **今すぐ** | `db_path` のパス検証 | 中 |
| **次スプリント** | `table()` のフック継承明示化 | 中 |
| **次スプリント** | `UniqueHook` のロック戦略統一 | 大 |
| **計画的に** | AES-GCM ノンス管理 | 中 |
| **計画的に** | `ExpiringDict` のスレッド/async混在解消 | 大 |

**重要な注記**: セクション7の12件のCRITICAL `sql_string_concat` のうち、`_sanitize_identifier` を通過している箇所（`clear`、`_delete_from_db_on_expire`、`__init__` での自テーブル名など）は識別子がコード内部で固定されているため**実際のリスクは低い**です。真に危険なのは外部入力が届く `pragma()`、`_recover_chunk_via_dlq`、および引数経由で識別子が渡される箇所に絞られます。