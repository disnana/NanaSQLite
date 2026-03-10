# NanaSQLite v1.3.4 プレリリース監査レポート

> 対象バージョン: 1.3.4r5  
> 監査日: 2026-03-10  
> 対象ファイル: `src/nanasqlite/` 配下すべて (core.py, async_core.py, cache.py, utils.py, sql_utils.py, exceptions.py)

---

## 総括

| カテゴリ | Critical | High | Medium | Low | 計 |
|---|---|---|---|---|---|
| 不具合・潜在バグ | 1 | 3 | 5 | 3 | 12 |
| 高速化の余地 | — | 1 | 4 | 2 | 7 |
| 改善点 (コード品質) | — | — | 4 | 5 | 9 |
| 脆弱性 | — | 2 | 3 | 2 | 7 |
| **合計** | **1** | **6** | **16** | **12** | **35** |

---

## 1. 不具合・潜在バグ

### BUG-01 [Critical] `items()` で `_check_connection()` が呼ばれない

**ファイル:** `core.py` L831-834

```python
def items(self) -> list:
    """全アイテムを取得（一括ロードしてからメモリから）"""
    self.load_all()                           # ← _check_connection() なし
    return list(self._cache.get_data().items())
```

`values()` (L825-829) は `self._check_connection()` を呼んでから `load_all()` するが、`items()` は呼ばない。クローズ済みまたは親が閉じた子インスタンスで `items()` を呼ぶと `NanaSQLiteClosedError` ではなく APSW の低レベル例外が漏洩する。

**修正案:** `items()` の先頭に `self._check_connection()` を追加。

---

### BUG-02 [High] AEAD 有効時に非 bytes データを暗黙に平文 JSON として返す

**ファイル:** `core.py` L639-644

```python
if self._aead:
    if not isinstance(value, bytes):
        # Fallback or manual check if stored as string accidentally
        if HAS_ORJSON:
            return orjson.loads(value)
        return json.loads(value)
```

暗号化モード (`aes-gcm` / `chacha20`) が有効にもかかわらず、DB から取得した値が `bytes` でなければ暗号化を一切行わず平文 JSON として復号する。暗号化前にマイグレーション無しで書き込まれた古いデータや、型変換の不整合で文字列が入り込んだ場合に **暗号化を迂回して平文を返す** リスクがある。

**修正案:** 非 bytes を受け取った場合は明示的に `NanaSQLiteDatabaseError("Encrypted data expected but got str")` を送出するか、警告ログを出す。少なくともサイレントフォールバックは避ける。

---

### BUG-03 [High] AEAD 復号時に nonce 長の検証がない

**ファイル:** `core.py` L646-648

```python
nonce = value[:12]
ciphertext = value[12:]
decoded = self._aead.decrypt(nonce, ciphertext, None).decode("utf-8")
```

`value` が 12 バイト未満の場合、`nonce` は不正な長さになり、`self._aead.decrypt()` が暗号ライブラリの低レベル例外をそのまま送出する。エラーメッセージからデータ破損かキー不一致かを判別できない。

**修正案:** `if len(value) < 13: raise NanaSQLiteDatabaseError("Corrupted encrypted data: too short")`

---

### BUG-04 [High] `async_core.py` の `acontains()` で二重初期化チェック

**ファイル:** `async_core.py` L317-321

```python
await self._ensure_initialized()
if self._db is None:
    await self._ensure_initialized()
    if self._db is None:
        raise RuntimeError("Database not initialized")
```

`_ensure_initialized()` の直後に `self._db is None` を再チェックしている。正常なら冗長であり、`close()` と並行実行された場合は 2 回目の `_ensure_initialized()` で閉じたばかりの DB を再初期化してしまう可能性がある。

**修正案:** 2 つ目の `if self._db is None` ブロック (L318-321) を削除。

---

### BUG-05 [Medium] `async_core.py` の `_shared_query_impl()` で `offset` が未検証

**ファイル:** `async_core.py` L1446-1464

`limit` は型・非負チェックされるが (L1447-1451)、`offset` は一切検証されず SQL に直接埋め込まれる (L1464)。負数や非整数を渡すと SQLite エラーが発生する。

```python
if offset is not None:
    sql += f" OFFSET {offset}"   # 未検証
```

**修正案:** `limit` と同様に `isinstance(offset, int)` および `offset >= 0` のチェックを追加。

---

### BUG-06 [Medium] `async_core.py` の `fetch_one` / `fetch_all` 型アノテーション不正

**ファイル:** `async_core.py` L685, L709

```python
async def fetch_one(self, sql: str, parameters: tuple = None) -> tuple | None:
async def fetch_all(self, sql: str, parameters: tuple = None) -> list[tuple]:
```

デフォルト値 `None` なのに型は `tuple`。正しくは `tuple | None = None`。mypy の strict モードで型エラーになる。

**修正案:** `parameters: tuple | None = None` に修正。

---

### BUG-07 [Medium] `ExpiringDict` スケジューラが 1 反復で 1 キーしか期限切れ処理しない

**ファイル:** `utils.py` L75-99

```python
if expiry <= now:
    expired_keys.append(first_key)   # 先頭1件のみ
    sleep_time = 0
```

スケジューラループは 1 回の反復で最初の 1 キーしか処理しない。短期間に大量のキーが期限切れになると、処理が追いつかず期限切れアイテムが長時間残留する。

**修正案:** `while` ループで `_exptimes` の先頭が `<= now` である限り回収し続ける。

---

### BUG-08 [Medium] `ExpiringDict.clear()` でスケジューラスレッドの join がない

**ファイル:** `utils.py` L193-199

```python
def clear(self) -> None:
    with self._lock:
        ...
        self._scheduler_running = False
```

`_scheduler_running = False` にするだけでスレッドの完了を待たない。`clear()` 直後に再利用すると、古いスレッドとの競合状態が生じる可能性がある。

**修正案:** フラグ設定後に `self._scheduler_thread.join(timeout=2)` を追加。

---

### BUG-09 [Medium] `batch_get()` でキャッシュ値が `None` のとき結果に含まれない

**ファイル:** `core.py` L908-912

```python
for key in keys:
    if self._cache.is_cached(key):
        val = self._cache.get(key)
        if val is not None:        # ← None を格納したキーが除外される
            results[key] = val
```

`db["k"] = None` で格納した値はキャッシュヒットしても `val is not None` で弾かれ、`results` に含まれない。その後 `missing_keys` にも入らないため、存在するのに返却されないキーが発生する。

**修正案:** `_NOT_FOUND` sentinel を使ってキャッシュミスと `None` 値を区別する。

---

### BUG-10 [Low] `_sanitize_identifier()` で `IDENTIFIER_PATTERN` を再利用していない

**ファイル:** `core.py` L370

```python
if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", inner_identifier):
```

L49 で `IDENTIFIER_PATTERN = re.compile(...)` をモジュールレベルでコンパイル済みだが、ここでは `re.match()` で毎回コンパイルし直している。機能的にはバグではないが、意図しないパターン不一致のリスクがある。

**修正案:** `if not IDENTIFIER_PATTERN.match(inner_identifier):` に統一。

---

### BUG-11 [Low] `ExpiringDict.__del__` でスレッドの join がない

**ファイル:** `utils.py` L201-202

```python
def __del__(self):
    self._scheduler_running = False
```

デーモンスレッドの終了を待たない。GC タイミングによってはリソースリークの可能性がある。

**修正案:** `self._scheduler_running = False` の後に `if self._scheduler_thread: self._scheduler_thread.join(timeout=1)` を追加。

---

### BUG-12 [Low] `exceptions.py` の `NanaSQLiteDatabaseError.__init__` 型アノテーション

**ファイル:** `exceptions.py` L42

```python
def __init__(self, message: str, original_error: Exception = None):
```

`None` をデフォルト値にしているが型ヒントは `Exception`。mypy strict で不正。

**修正案:** `original_error: Exception | None = None` に修正。

---

## 2. 高速化の余地

### PERF-01 [High] `values()` / `items()` が毎回全データをメモリロードする

**ファイル:** `core.py` L825-834

```python
def values(self) -> list:
    self._check_connection()
    self.load_all()             # 全テーブル読み込み
    return list(self._cache.get_data().values())
```

`load_all()` が未ロードのとき、テーブル全体をメモリにロードする。大規模テーブルではメモリ消費と初回レイテンシが問題になる。`_all_loaded` フラグにより 2 回目以降は高速だが、初回のペナルティが大きい。

**改善案:** イテレータベースの `SELECT key, value FROM ...` でストリーミング返却するオプションを追加。または `load_all()` 済みならキャッシュ、未ロードなら DB から直接 SQL で返す分岐を検討。

---

### PERF-02 [Medium] `query()` で毎回 `PRAGMA table_info()` が実行される

**ファイル:** `core.py` L1838-1841

```python
if columns is None:
    pragma_cursor = self.execute(f"PRAGMA table_info({safe_table_name})")
    col_names = [row[1] for row in pragma_cursor]
```

`columns=None` のとき、カラム名取得のために毎回 PRAGMA クエリが発行される。テーブルスキーマは変更頻度が低いため、結果をインスタンス変数にキャッシュすれば不要なラウンドトリップを削減できる。

**改善案:** `self._column_names_cache: dict[str, list[str]]` にテーブル名→カラム名リストをキャッシュ。`alter_table_add_column()` 実行時にキャッシュを無効化。

---

### PERF-03 [Medium] カラム名 AS 句抽出ロジックが 3 箇所で重複

**ファイル:** `core.py` L1843-1852, `core.py` L2370-2377, `async_core.py` L1484-1491

同一の正規表現分割ロジック (`re.split(r"\s+as\s+", ...)`) が 3 箇所に重複している。保守性が低く、一方だけ修正されてバグが残るリスクがある。

**改善案:** ヘルパーメソッド `_extract_column_aliases(columns: list[str]) -> list[str]` を作成し共通化。

---

### PERF-04 [Medium] `async_core.py` で `asyncio.get_running_loop()` が毎メソッドで呼ばれる

**ファイル:** `async_core.py` (45 箇所以上)

ほぼ全ての async メソッドで `loop = asyncio.get_running_loop()` を個別に呼んでいる。`_ensure_initialized()` 内でインスタンス変数にキャッシュすればオーバーヘッドを削減できる。

**改善案:** `self._loop = asyncio.get_running_loop()` を初期化時に保存し再利用。ただしイベントループ変更時の整合性に注意。

---

### PERF-05 [Medium] `async_core.py` の `_read_connection()` が同期コンテキストマネージャ

**ファイル:** `async_core.py` L224-241

```python
@contextmanager
def _read_connection(self):
    ...
    conn = pool.get()   # 同期的ブロッキング
```

`queue.Queue.get()` は同期ブロッキング呼び出しであり、プール枯渇時にイベントループをブロックする。`run_in_executor` 内で使う分には問題ないが、プールサイズが小さい場合のスケーラビリティに影響する。

**改善案:** `asyncio.Queue` ベースの非同期プールを検討。または `pool.get(timeout=...)` でタイムアウトを設定。

---

### PERF-06 [Low] `_sanitize_identifier()` で毎回 `re.match()` 呼び出し

**ファイル:** `core.py` L370

モジュールレベルでコンパイル済みの `IDENTIFIER_PATTERN` が L49 に存在するが、`_sanitize_identifier()` では `re.match()` を都度呼んでいる。

**改善案:** `IDENTIFIER_PATTERN.match(inner_identifier)` に変更。

---

### PERF-07 [Low] `batch_update()` 内の validkit バリデーションループが重複

**ファイル:** `core.py` L1040-1056

`coerce=True` と `coerce=False` で 2 つの別々のループがあるが、分岐を `coerce` フラグで統一すれば 1 ループにまとめられる。

**改善案:**
```python
validated: dict[str, Any] = {}
for key, value in mapping.items():
    result = validkit_validate(value, self._validator)
    validated[key] = result if self._coerce else value
mapping = validated if self._coerce else mapping
```

---

## 3. 改善点 (コード品質)

### QUAL-01 [Medium] `_get_all_keys_from_db()` の戻り値型が不完全

**ファイル:** `core.py` L691

```python
def _get_all_keys_from_db(self) -> list:
```

`list` ではなく `list[str]` とすべき。

---

### QUAL-02 [Medium] マジックナンバーが定数化されていない

**ファイル:** `core.py` L328, L331, L620

```python
cursor.execute("PRAGMA mmap_size = 268435456")   # 256MB
nonce = os.urandom(12)                             # 12 bytes
```

`MMAP_SIZE_BYTES = 268_435_456` や `AEAD_NONCE_SIZE = 12` のようにモジュールレベル定数にすると可読性と保守性が向上する。

---

### QUAL-03 [Medium] `query()` と `query_with_pagination()` のカラム名取得ロジック不整合

**ファイル:** `core.py` L1852 vs L2377

`query()` ではカラム名のクォート除去をしないが (`col.strip()`)、`query_with_pagination()` では行う (`col.strip().strip('"').strip("'")`)。挙動が微妙に異なる。

---

### QUAL-04 [Medium] `async_core.py` に `__all__` がない

**ファイル:** `async_core.py`

公開 API と内部 API の境界が不明確。`__all__ = ["AsyncNanaSQLite"]` を追加すべき。

---

### QUAL-05 [Low] `_TransactionContext` にドキュメント文字列が不足

**ファイル:** `core.py` L2780-2795

```python
class _TransactionContext:
    """トランザクションのコンテキストマネージャ"""
```

一行のみ。`__enter__` / `__exit__` の挙動（例外時はロールバック、正常時はコミット）をドキュメントに記載すべき。

---

### QUAL-06 [Low] ロギングの粒度が一貫していない

**ファイル:** `core.py` 全般

一部のエラーパスは `logger.error()` / `logger.warning()` でログ出力するが (L1259)、他のエラーパスはログなしで例外を送出するのみ (L1943)。クリティカルな操作 (`restore`, `backup`, `close`) のエラーは統一的にログを出すべき。

---

### QUAL-07 [Low] `broad-exception-caught` の pylint 無効化コメントが多い

**ファイル:** `core.py` L1048, L1055 等

```python
except Exception as exc:  # pylint: disable=broad-exception-caught
```

validkit の例外型が不確定であることが理由と思われるが、`validkit.ValidationError` が利用可能なら、それを具体的にキャッチすべき。

---

### QUAL-08 [Low] `async_core.py` の `_run_in_executor()` に型アノテーションがない

**ファイル:** `async_core.py` L243-247

```python
async def _run_in_executor(self, func, *args):
```

戻り値型が `Any` で推論に頼っている。`-> Any` を明示すべき。

---

### QUAL-09 [Low] `ExpiringDict` の `__len__` が期限切れアイテムを含む

**ファイル:** `utils.py` L179-182

```python
def __len__(self) -> int:
    # Note: could be inaccurate if items expired but not yet evicted
    return len(self._data)
```

コメントで認識はされているが、ドキュメントに「近似値を返す」旨の明記がない。

---

## 4. 脆弱性

### SEC-01 [High] `alter_table_add_column()` の `column_type` がブラックリスト方式

**ファイル:** `core.py` L1941-1944

```python
if any(c in column_type for c in [";", "'", ")"]) or "--" in column_type or "/*" in column_type:
    raise ValueError(f"Invalid or dangerous column type: {column_type}")
```

禁止文字のブラックリスト (`; ' ) -- /*`) でフィルタしているが、以下が未考慮:
- 開き括弧 `(` を使った `TEXT CHECK(1=1)` のような制約注入
- バッククォートやユニコード正規化を利用した回避
- `\x00` (NULL バイト) による截断

**修正案:** ホワイトリスト方式に変更。`re.match(r'^[A-Z][A-Z0-9 (),.]+$', column_type.upper())` のように許可パターンのみ通す。あるいは既知の SQLite 型 (`TEXT`, `INTEGER`, `REAL`, `BLOB`, `NUMERIC` 等) のホワイトリストに限定。

---

### SEC-02 [High] `_validate_expression()` がクォートされた関数名を検出できない

**ファイル:** `core.py` L574-575

```python
sanitized_expr = sanitize_sql_for_function_scan(expr)
matches = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", sanitized_expr)
```

正規表現は引用符で囲まれた識別子 (例: `"LOAD_EXTENSION"(`) にマッチしない。`sanitize_sql_for_function_scan()` は文字列リテラルをマスクするが、ダブルクォートで囲まれた識別子は残る。`"SYSTEM"()` のようなパターンで禁止関数を呼び出せる可能性がある。

**修正案:** 正規表現を `(?:"[a-zA-Z_][a-zA-Z0-9_]*"|[a-zA-Z_][a-zA-Z0-9_]*)\s*\(` に拡張し、クォート付き識別子も捕捉する。

---

### SEC-03 [Medium] `backup()` でシンボリックリンク経由のパス操作リスク

**ファイル:** `core.py` L1243-1264

```python
if self._is_in_memory_path(dest_path):
    raise NanaSQLiteValidationError(...)
try:
    if os.path.samefile(dest_path, self._db_path):
        raise NanaSQLiteValidationError(...)
```

`dest_path` が信頼できないユーザー入力の場合、シンボリックリンクを介して意図しないファイルを上書きされる可能性がある。`os.path.samefile()` はシンボリックリンクを解決するが、バックアップ処理自体が別のファイルを対象にすることは防げない。

**修正案:** `dest_path = os.path.realpath(dest_path)` で正規化してから検証。信頼できない入力の場合は `os.O_NOFOLLOW` フラグでのオープンを検討。

---

### SEC-04 [Medium] `execute()` メソッドで PRAGMA ホワイトリストを迂回可能

**ファイル:** `core.py`

`pragma()` メソッドには安全な PRAGMA のホワイトリストがあるが、`execute()` は任意の SQL を実行できるため、`execute("PRAGMA journal_mode = OFF")` のように安全設定を変更できる。

**修正案:** `execute()` 内で `PRAGMA` 文を検出した場合に警告を出すか、`pragma()` 経由に限定するオプションを提供。

---

### SEC-05 [Medium] エラーメッセージから内部情報が漏洩する可能性

**ファイル:** `core.py` L372, L456, `async_core.py` L1496

```python
raise NanaSQLiteValidationError(
    f"Invalid identifier '{inner_identifier}': must start with letter ..."
)
```

```python
raise NanaSQLiteDatabaseError(f"Failed to execute query: {e}", original_error=e)
```

例外メッセージに生の識別子名や APSW のエラー詳細が含まれる。ログが外部に露出した場合、DB スキーマやファイルパスが漏洩する。

**修正案:** ユーザー向け例外メッセージからはパスや内部構造を除去し、詳細は `logger.debug()` に限定。

---

### SEC-06 [Low] AEAD 暗号化で nonce 再利用の理論的リスク

**ファイル:** `core.py` L620

```python
nonce = os.urandom(12)
```

`os.urandom()` は暗号学的に安全だが、96 bit nonce の場合 2^48 回の暗号化で約 50% の衝突確率に達する (Birthday Paradox)。同一鍵・同一 nonce の組み合わせは AES-GCM で致命的（認証タグの無効化、平文の漏洩）。現実的にはほぼ問題にならないが、超大規模ユースケースではリスクがゼロではない。

**緩和案:** ドキュメントに nonce 制限を明記。長期運用では鍵ローテーションを推奨。

---

### SEC-07 [Low] `restore()` で一時ファイルの権限が一時的に緩い

**ファイル:** `core.py` L1341-1349

```python
fd, tmp_path = tempfile.mkstemp(dir=db_dir)
with os.fdopen(fd, "wb") as tmp_f:
    shutil.copyfileobj(src_f, tmp_f)
    ...
# 元DBのパーミッションを一時ファイルに適用してから原子的に置き換える
if original_mode is not None:
    os.chmod(tmp_path, stat.S_IMODE(original_mode))
os.replace(tmp_path, self._db_path)
```

`mkstemp` のデフォルトモードは `0o600` で、元 DB のパーミッションは `os.replace()` 直前に `chmod` で適用される。`mkstemp` 作成〜`chmod` 適用までの間、一時ファイルは `0o600` (所有者のみ) のため、元 DB がグループ読み取り可能だった場合に一時的にアクセスできない期間が生じる。逆に `0o600` は安全側に倒れているため、深刻度は低い。

---

## 5. 推奨対応優先度

### v1.3.4 リリース前に修正すべき (Critical / High)

| ID | 概要 |
|---|---|
| BUG-01 | `items()` に `_check_connection()` を追加 |
| BUG-02 | AEAD デシリアライズのサイレントフォールバックを排除 |
| BUG-03 | AEAD 復号時の nonce 長検証を追加 |
| BUG-09 | `batch_get()` の `None` 値ハンドリングを修正 |
| SEC-01 | `alter_table_add_column()` の column_type をホワイトリスト方式に変更 |
| SEC-02 | `_validate_expression()` のクォート付き識別子対応 |
| PERF-01 | `values()` / `items()` の大規模テーブル対応を検討 |

### v1.3.5 以降で対応可能 (Medium)

| ID | 概要 |
|---|---|
| BUG-04 | `acontains()` の二重初期化チェック削除 |
| BUG-05 | `offset` パラメータの検証追加 |
| BUG-06 | `fetch_one` / `fetch_all` の型アノテーション修正 |
| BUG-07 | `ExpiringDict` スケジューラの一括処理化 |
| BUG-08 | `ExpiringDict.clear()` のスレッド join |
| SEC-03 | `backup()` のシンボリックリンク対策 |
| SEC-04 | `execute()` での PRAGMA 制限 |
| SEC-05 | エラーメッセージの情報漏洩対策 |
| PERF-02 | PRAGMA table_info のキャッシュ |
| PERF-03 | カラム名抽出ロジックの共通化 |
| PERF-04 | `asyncio.get_running_loop()` のキャッシュ |
| PERF-05 | 非同期読み込みプールの改善 |
| QUAL-01〜04 | 型ヒント・コード品質改善 |

### 将来的な改善 (Low)

| ID | 概要 |
|---|---|
| BUG-10〜12 | 軽微なバグ修正 |
| PERF-06〜07 | 軽微なパフォーマンス改善 |
| QUAL-05〜09 | ドキュメント・コード品質改善 |
| SEC-06〜07 | 低リスクのセキュリティ改善 |
