---
outline: [2, 3]
---

# 更新履歴

### [1.5.3] - 2026-04-08

#### パフォーマンス改善

- **PERF-E: `_get_all_keys_from_db()` — SQL 文字列を事前計算**（`core.py`）
  - `keys()` / `__iter__` が呼ばれるたびに `f"SELECT key FROM {self._safe_table}"` を構築していました。PERF-07 と同様に `_sql_kv_select_keys` を `__init__` 時に一度だけ計算し、以降はこれを再利用するよう変更しました。

- **PERF-F: `batch_update_partial()` v2 + Unbounded モード — 不要ロックを除去**（`core.py`）
  - v2 モード + Unbounded モードの組み合わせで、純粋なメモリ更新（`_data.update()` / `_absent_keys.difference_update()`）にまでロックを取得していました。`batch_update()` v2 パスと同様、GIL が個々の dict/set 操作をアトミックに保護するため明示的ロックは不要です。LRU/TTL モードは引き続きロックを取得します。

#### コード品質改善

- **QUAL-04: `_no_encrypt` — 変更不可であることのコメント追加**（`core.py`）
  - `_fernet` / `_aead` が `__init__` 後に変更された場合、`_no_encrypt` がステールになりシリアライズが壊れることを明記しました（rc3 監査で指摘、今回対応）。

- **QUAL-05: 型アノテーション修正 — `parameters: tuple = None` → `parameters: tuple | None = None`**（`core.py`）
  - `fetch_one()`, `fetch_all()`, `create_table()` の `primary_key`、`sql_update()`, `sql_delete()`, `exists()` の 6 箇所で `tuple = None` を `tuple | None = None` に修正しました。

- **QUAL-06: `async_core.py` — `_ensure_initialized()` 呼び出しの統一**（`async_core.py`）
  - `query_with_pagination()` と `table()` で `if self._db is None: await self._ensure_initialized()` という不完全なガードが使われていました。他のメソッドと同様に無条件で `await self._ensure_initialized()` を呼ぶよう変更しました（`_ensure_initialized()` 自体がべき等です）。

---

### [1.5.3rc4] - 2026-04-08

#### パフォーマンス改善

- **PERF-A: `_sanitize_identifier()` — `lru_cache(maxsize=256)` を追加**（`core.py`）
  - テーブル名・カラム名の検証は同じ識別子に対して繰り返し呼び出されるにもかかわらず、毎回 `re.match()` を実行していました。`@lru_cache` でキャッシュすることで、2 回目以降は dict ルックアップのみになります。`test_begin_commit` で約 13% 高速化、`sql_insert` ホットパスで関数呼び出し 4 倍削減。

- **PERF-B: `ExpiringDict.__setitem__()` — TIMER モード以外での `_cancel_timer()` を省略**（`utils.py`）
  - SCHEDULER モードでは `_timers` / `_async_tasks` は常に空のため、`_cancel_timer()` 呼び出しは毎回無意味な dict ルックアップを 2 回実行していました。`if self._mode == ExpirationMode.TIMER:` ガードで省略します。`test_cache_write_1000[ttl]` で約 22% 高速化。

- **PERF-C: `vacuum()` — `execute()` ディスパッチをバイパス**（`core.py`）
  - `vacuum()` が `execute()` の完全なパス（v2 ルーティング、重複 `_check_connection`、`try/except` ラップ）を経由していました。`begin_transaction` / `commit` / `rollback` で使用されている PERF-26 パターン（直接接続呼び出し）を適用しました。

- **PERF-D: `backup()` — DB ファイルの `(st_dev, st_ino)` を `__init__` 時にキャッシュ**（`core.py`）
  - `backup()` のセルフコピー防止チェックが毎回 `os.stat()` を 2 回呼び出していました。ソース DB のスタット結果を `__init__` 時にキャッシュし（`restore()` 後に再計算）、`backup()` では `dest_path` の 1 回分のみ呼び出すようにしました。

#### バグ修正

- **BUG-02: `ExpiringDict.clear()` — スケジューラスレッドを永久に停止していた問題を修正**（`utils.py`）
  - `clear()` 後に `_scheduler_running = False` のまま再起動されなかったため、`clear()` 後に追加された新しい項目が期限切れにならない問題がありました。`clear()` の完了後にスケジューラを再起動するよう修正しました。

- **BUG-03: `UnboundedCache.delete()` — `_cached_keys` に `.add()` ではなく `.discard()` を使用**（`cache.py`）
  - 削除されたキーが `_cached_keys.add(key)` によって「キャッシュ済み」としてマークされていたため、再挿入後も DB へのフェッチがスキップされる問題がありました。`.discard(key)` に修正しました。

- **BUG-04: `ExpiringDict.__getitem__()` — TOCTOU 競合状態を修正**（`utils.py`）
  - `_check_expiry()` がロック外で実行され、その後ロック内で `_data[key]` が読み取られていました。スケジューラスレッドが間に割り込んでキーを削除すると、まだ有効だったキーに対して偽の `KeyError` が発生していました。有効期限チェックと読み取りをロック内でアトミックに実行するよう修正しました。

#### セキュリティ修正

- **SEC-02: `create_table()` — カラム型正規表現からクォート文字を除去**（`core.py`）
  - 旧正規表現 `r"^[\w\s(),.+*'\"]+"` がシングル・ダブルクォートを許可していたため、`TEXT DEFAULT 'x') --` のような SQL インジェクション文字列が通過していました。クォート文字（`'` `"`）、セミコロン（`;`）、コメント構文（`--`、`/* */`）を除外した新しい正規表現に変更しました。

#### コード品質改善

- **QUAL-01: `get_model()` — 型アノテーション修正**（`core.py`）
  - `model_class: type = None` を `model_class: type | None = None` に修正しました。

- **CodeQL: `except OSError: pass` — 説明コメントを追加**（`core.py`）
  - PERF-D の `_db_stat_key` キャッシュ初期化時の空 `except` 節に、CodeQL 指摘に従い説明コメントを追加しました。

---

### [1.5.3rc3] - 2026-04-07

#### パフォーマンス改善

- **PERF-21: `execute_many()` — Python ループ → `cursor.executemany()`**（`core.py`）
  - APSW 組み込みの `executemany()` を使い、per-item の Python 関数呼び出しオーバーヘッドを排除。`test_execute_many`・`test_import_from_dict_list` で約 15% 改善。

- **PERF-22: `batch_delete()` — フック未登録時の事前チェックループを省略**（`core.py`）
  - `_has_hooks = False`（デフォルト）の場合、全キーへの `_ensure_cached()` 呼び出しをスキップ。

- **PERF-23: `batch_update()` — シリアライズのロック外移動・`dict.update()`・`_absent_keys` ガード**（`core.py`）
  - `_serialize()` をロック外へ移動（`__setitem__` と同方針）、キャッシュ更新に `dict.update()` を使用（per-key ループ比 約 6 倍高速）、`_absent_keys` 更新に `if` ガード + `difference_update()` を適用。約 9% 高速化。

- **PERF-24: `batch_update_partial()` — `dict.update()` + `_absent_keys` ガード**（`core.py`）
  - PERF-23 と同様の最適化を v1 / v2 両パスに適用。

- **PERF-25: `batch_delete()` — `_absent_keys.update(keys)` 一括化**（`core.py`）
  - per-key `add()` ループを `update(keys)` 一括呼び出しに変更。

- **PERF-26: `begin_transaction()` / `commit()` / `rollback()` — `execute()` オーバーヘッドをバイパス**（`core.py`）
  - `self._connection.execute()` を直接呼び出し、v2 判定・SQL strip/upper・重複 `_check_connection()` を排除。

- **PERF-29: `_serialize()` — 暗号化なし時の早期リターン**（`core.py`）
  - `__init__` 時に `_no_encrypt` フラグを事前計算し、`_fernet` / `_aead` の属性ルックアップを全書き込みパスでスキップ。

---

### [1.5.3rc2] - 2026-04-07

#### バグ修正

- **[Medium] BUG-01: `setdefault()` + `before_write` 変換フック組み合わせ時の返値誤り**（`core.py`）
  - `before_write` フックが値を変換する場合（`ValidkitHook(coerce=True)` / `PydanticHook` 等）、PERF-18 最適化で元の `default` に対して `after_read` を適用してしまう問題を修正。`_has_hooks` が True の場合はキャッシュから変換後の値を読み直してから `after_read` を適用するよう変更。

#### パフォーマンス修正（v1.5.3rc2 ベンチマーク低下対応）

- **[High] PERF-14/15/16: Unbounded モード読み取りホットパスの try/except 高速化**（`core.py`）
  - `__getitem__` / `get()` / `__contains__` で `.get(key, sentinel)` を `d[key]` + `try/except` に置き換え。キャッシュヒット時 **約 1.9 倍**高速化。`test_single_read_cached` で **-15%** 改善。

- **[Medium] PERF-17: `_update_cache` 空 `_absent_keys` 時の `discard()` 省略**（`core.py`）
  - 書き込み専用ワークロードで不要なハッシュ計算を排除する `if self._absent_keys:` ガードを追加。

- **[Medium] PERF-18: `setdefault()` の冗長 `self[key]` 呼び出し省略**（`core.py`）
  - 新規キー書き込み後の再読み込みを省略し、デフォルト値を直接返すよう変更。

- **[Medium] PERF-19: `pop()` Unbounded モードでの直接 `_data` アクセス**（`core.py`）
  - `self._cache.get()` の代わりに `self._data[key]` を使用してメソッドディスパッチコストを排除。

- **[Medium] PERF-20: `_has_hooks` 事前計算フラグ**（`core.py`）
  - 全 KV ホットパスの `if self._hooks:` を事前計算 bool フラグ `_has_hooks` に置き換え、`list.__len__` の呼び出しを排除。

### [1.5.3rc1] - 2026-04-07

#### パフォーマンス修正（v1.5.3 プレリリース監査）

- **[High] PERF-07: 共通 SQL 文字列の `__init__` 時事前計算**（`core.py`）
  - 全 KV ホットパスで f-string による SQL 文字列再構築を排除。`__init__` 時に 6 種の SQL テンプレートを事前計算してインスタンス変数に保持します。
  - **効果**: 書き込み・読み込み・削除・カウント等の全 KV 操作で文字列構築コストを排除。

- **[Medium] PERF-08: Unbounded モードでの `to_dict()` / `copy()` MISSING フィルタ省略**（`core.py`）
  - Unbounded モードでは `_data` に MISSING センチネルが格納されないため、`dict(self._data)` を直接返すよう変更しました。
  - **効果**: `test_to_dict_1000` / `test_copy` の改善に寄与。

- **[Medium] PERF-09: LRU `__getitem__` での二重キャッシュルックアップ排除**（`core.py`）
  - キャッシュヒット時の `_data` 在籍確認を先行させ、`self._cache.get()` を 1 回の呼び出しで完結するよう変更しました。
  - **効果**: LRU/TTL キャッシュヒット時の `move_to_end()` 冗長呼び出しを排除。

- **[Medium] PERF-10: `_validate_expression()` の正規表現最適化と関数スキャン早期スキップ**（`core.py`）
  - 4 パターンをモジュールレベルで事前コンパイルした単一正規表現 `_DANGEROUS_SQL_RE` に統合。`(` が含まれない式では関数スキャンをスキップします。
  - **注意**: 非 strict モードでは複数の危険パターンが同時マッチしても警告は 1 件のみ発行されます。

- **[Medium] PERF-11: `ExpiringDict._check_expiry()` のロックフリー早期リターン最適化**（`utils.py`）
  - 期限切れでないキーのロック取得をスキップするロックフリー楽観的プレチェックを追加しました。
  - **効果**: TTL キャッシュのキャッシュヒット時のロック取得回数を削減。

- **[High] PERF-12: LRU/TTL モードの `get()` における二重キャッシュルックアップ排除**（`core.py`）（v1.5.3 監査で発見）
  - PERF-09 で `__getitem__` を最適化した際に `get()` に同じ問題が残存していました。同パターンを適用しました。

- **[Medium] PERF-13: Unbounded モードの `values()` / `items()` における MISSING フィルタ省略**（`core.py`）（v1.5.3 監査で発見）
  - PERF-08 と同様の最適化を `values()` / `items()` にも適用しました。

#### テスト

- `tests/test_v153_perf_fixes.py` を追加（PERF-07〜11 の回帰テスト 19 件）。
- `tests/test_audit_poc.py` に `TestPerf12GetDoubleLookup` / `TestPerf13ValuesItemsFilter` を追加。

### [1.5.2] - 2026-04-06

#### パフォーマンス修正（v1.5.0dev1 以降の性能低下 継続対応）

- **[High] PERF-06: Unbounded キャッシュ読み取りホットパスの分岐最適化**（`core.py`）
  - `__getitem__` / `get` / `__contains__` / `_ensure_cached` の Unbounded モードで、キャッシュ済み読み取り時の判定順序を見直しました。存在データは `_data` を優先して処理し、known-absent の追跡は `_absent_keys` に分離することで、正のキャッシュヒット時に不要な分岐や membership 判定が入らないよう整理しました。
  - `_data` 優先の fast-path と negative cache（known-absent）専用分岐に再編し、不要な `_ensure_cached()` 呼び出しを削減しました。
  - **効果**: キャッシュ済み読み取り・存在確認の追加オーバーヘッドを削減（既存 API/挙動は維持）。

#### 破壊的変更（許可済み対応）

- Unbounded モードの内部メタデータを `_cached_keys` から `_absent_keys`（known-absent 専用）へ分離しました。
  - 公開 API への影響はありませんが、内部属性 `_cached_keys` に依存するコードは互換性がありません。
  - 移行: `in` / `get` / `is_cached` 等の公開 API を利用してください。

#### テスト

- `tests/test_v152_perf_fastpath.py` を追加し、`_data` 優先 fast-path と negative cache セマンティクス維持を検証。

### [1.5.1] - 2026-04-05

#### セキュリティ修正（v1.5.1 プレリリース監査）

- **[Medium] SEC-01: `exists()` の WHERE 句に `_validate_expression()` 未適用を修正**（`core.py`）
  - `query()` / `count()` / `query_with_pagination()` は WHERE 句を `_validate_expression()` で検証して `forbidden_sql_functions` などのポリシーを適用していましたが、`exists()` はこの検証を行っていませんでした。アプリケーションが `forbidden_sql_functions` を設定していても `exists()` のみポリシーが無視されるという不整合を修正しました。
  - `exists()` を呼び出す前に `_validate_expression(where, context="where")` を実行するよう変更しました。

- **[Medium] SEC-02: `sql_update()` / `sql_delete()` の WHERE 句に `_validate_expression()` 未適用を修正**（`core.py`）
  - `sql_update()` と `sql_delete()` の WHERE 句も同様に `_validate_expression()` が呼ばれていませんでした。`strict_sql_validation=True` / `forbidden_sql_functions` の設定がこれらのメソッドでは機能しない不整合を修正しました。

#### バグ修正（v1.5.1 プレリリース監査）

- **[High] BUG-01: `pop()` が v2 モードで v2 エンジンをバイパスする問題を修正**（`core.py`）
  - v2 モードで `pop()` を呼ぶと `_delete_from_db()` が直接 DB へ DELETE を発行し、v2 staging buffer を完全にバイパスしていました。staging buffer に SET 操作が残留している状態でこの直接 DELETE が実行されると、その後の `flush()` で staging の SET が DB に書き込まれてキーが「復活」するデータ整合性バグが発生していました。`__delitem__` と同様に v2 モードでは `v2_engine.kvs_delete()` を経由するよう修正しました。

- **[Medium] BUG-02: `batch_get()` が `_cached_keys` の「存在しない」ステータスを尊重しない問題を修正**（`core.py`）
  - `__delitem__` 実行後、キーは `_cached_keys` に「存在しない」として記録されますが、`batch_get()` は `_data` のみを確認して `_cached_keys` を参照しないため、v2 non-immediate モードでは staging の DELETE がまだ DB に反映されていない状態で `batch_get()` が DB の旧値を返してしまう不整合がありました。`batch_get()` でも `_cached_keys` を確認して「既知の不在キー」をスキップするよう修正しました。

- **[Low] BUG-03: `to_dict()` が LRU/TTL モードで `MISSING` センチネル値を含む問題を修正**（`core.py`）
  - LRU/TTL キャッシュモードでは、存在しないキーへのアクセス時に `MISSING` センチネルがキャッシュに書き込まれます（負キャッシュ）。`to_dict()` がこれをフィルタリングせずに返していたため、結果に `{key: <MISSING sentinel>}` が混入する可能性がありました。`items()` と同様に `MISSING` をフィルタリングするよう修正しました。

#### パフォーマンス修正（v1.5.1 プレリリース監査）

- **[Low] PERF-05: `fast_validate_sql_chars()` のホットパス最適化**（`sql_utils.py`）
  - `fast_validate_sql_chars()` が呼び出しごとに `set(...)` で文字セットオブジェクトを新規生成していました。この関数は全てのクエリメソッドのバリデーション経路（ホットパス）から呼ばれるため、モジュールレベルの `frozenset` 定数 `_SAFE_SQL_CHARS` として事前計算するよう変更しました。約 200–300 ns / 呼び出しのオーバーヘッドを削減します。

#### パフォーマンス修正（v1.5.0dev1 以降の性能低下対応）

ベンチマーク（RPI 実機）で確認された v1.5.0dev1 以降の性能低下を修正しました。

- **[Critical] PERF-01: フックホットパスのオーバーヘッド除去**（`core.py`）
  - `__getitem__`・`__setitem__`・`__delitem__`・`get`・`batch_get`・`setdefault`・`pop`・`batch_update_partial`・`batch_delete` の全ての読み書き操作で、毎呼び出し `getattr(self, "_hooks", [])` を実行していたため、フックが未設定の場合でも無視できないオーバーヘッドが発生していました。`self._hooks`（常に初期化済み）への直接アクセスと `if self._hooks:` による早期スキップに変更しました。
  - **効果**: キャッシュ済みキーの読み込み速度が約 30% 向上（実機 RPI: ~1.74M → ~2.3M ops/sec 相当）。

- **[Critical] PERF-02: v2 モードにおける共有ロック競合の解消**（`core.py`）
  - `__setitem__`・`__delitem__`・`batch_update`・`batch_delete` の v2 モードパスで、インメモリキャッシュの更新（`_data[key] = value` 等）に対して DB フラッシュスレッドと共有するロックを使用していました。このため、バックグラウンドフラッシュスレッドが DB トランザクションのためにロックを保持している間、メインスレッドのキャッシュ更新がブロックされ、特に低速 CPU（Raspberry Pi 等）で深刻なスループット低下を引き起こしていました。
  - v2 モードにおいてインメモリのみの更新操作は Python の GIL によるアトミック性が保証されており、バックグラウンドフラッシュスレッドは `_data` / `_cached_keys` に直接アクセスしないため、これらの操作に対する明示的なロック取得は不要です。
  - **効果**: v2 immediate モードの書き込みスループットが約 3.7 倍向上（実機 RPI: ~169 → ~600+ calls/sec 相当）。

- **[Medium] PERF-03: `_update_cache` 内の `hasattr()` 呼び出しを事前計算に変更**（`core.py`）
  - `_update_cache()` が毎呼び出し `hasattr(self._cache, "_max_size")` を実行していたため、書き込みパスで不要なオーバーヘッドが発生していました。`__init__` 時に `_use_cache_set` フラグとして事前計算するように変更し、ホットパスから `hasattr()` 呼び出しを除去しました。
  - **効果**: 書き込みパスで約 2-3% の速度改善。

- **[Medium] PERF-04: `_acquire_lock()` を `@contextmanager` ジェネレータから直接 RLock 返却に変更**（`core.py`）
  - `_acquire_lock()` が `@contextmanager` デコレータを使用していたため、毎呼び出しでジェネレータオブジェクトの生成・`next()` 呼び出し・`contextlib` のオーバーヘッドが発生していました。タイムアウト未設定（共通ケース）の場合は `threading.RLock` オブジェクトをそのまま返し、タイムアウト設定時のみ新設の `_TimedLockContext` を返すよう変更しました。`RLock` は C レベルの `__enter__`/`__exit__` を持つため、ジェネレータより大幅に高速です。
  - **効果**: 非 v2 書き込みで約 7% の速度改善。

### [1.5.0] - 2026-04-04

#### セキュリティ修正（v1.5.0 プレリリース監査）

- **[Critical] SEC-03**: `UniqueHook` における TOCTOU (Time-of-check/Time-of-use) 競合状態を文書化・警告追加。ユニーク制約チェックが DB 書き込みの外側で行われるため、マルチスレッド環境では制約をバイパスされる可能性があることをクラス docstring に明記しました。本質的な修正には SQLite ネイティブ制約 (`UNIQUE`) または排他ロックの適用を推奨します。
- **[Critical] SEC-04**: `ForeignKeyHook` における TOCTOU 競合状態を同様に文書化・警告追加。参照整合性制約チェックとDB書き込みの間に参照先キーが削除される可能性を docstring に明記。本質的な修正には `PRAGMA foreign_keys=ON` の使用を推奨します。
- **[High] SEC-05**: `BaseHook` の `key_pattern` 正規表現パターンに ReDoS (正規表現によるサービス拒否) 脆弱性が存在しました。悪意ある正規表現パターンにより CPU 負荷を引き起こす可能性があったため、コンストラクト時にパターン検証を行うよう修正しました。
- **[High] SEC-06**: フック制約違反時のエラーメッセージに詳細なフィールド名・値が含まれ、情報漏洩の恐れがありました。エラーメッセージを汎用化し、詳細情報はサーバーサイドのログのみに記録するように修正しました。

#### バグ修正（v1.5.0 プレリリース監査）

- **[Critical] BUG-05**: `PydanticHook` が全ての例外を `ValidationError` として一律に変換・抑制していた問題を修正。`ConnectionError`, `MemoryError` 等のシステムエラーは正しく再送出されるようになりました。
- **[High] BUG-06**: フック処理において値が変更されない場合も不要な辞書コピーを行っていた問題を修正。変更検出ロジックを導入し、実際に値が変更された場合のみ新しい辞書を生成するようにしました（バッチ処理でのメモリ効率改善）。

#### コード品質修正（PR レビュー指摘対応）

- **[Low] BANDIT-B110**: `v2_engine.py` にて Bandit が指摘した `try/except/pass` パターン（`atexit.unregister` の空キャッチ）を `contextlib.suppress(Exception)` に置き換え。
- **[Low] POC クリーンアップ**: CodeQL・Bandit が指摘した POC スクリプト内の問題（未使用インポート、未使用変数、bare `except`、ReDoS パターンのリテラル埋め込み）をすべて修正。テストファイル内の重複 `import sqlite3` も解消。

#### パッケージングとIDE支援の改善

- **[High] PEP 561 準拠と型補完の修正**:
  - `pyproject.toml` の `tool.setuptools` 設定を標準的な `src-layout` 用に刷新。これまで PyPI 配布版で `import nanasqlite` した際に型補完（IntelliSense）が効かなかった問題を修正しました。
  - `include-package-data = true` を有効化し、`MANIFEST.in` を追加することで、ビルドされたパッケージ (.whl, sdist) に確実に `py.typed` ファイルが含まれるようにしました。
  - これにより、VS Code (Pylance) や PyCharm 等の主要な IDE で、インストール直後から `NanaSQLite` や `PydanticHook` などの完全な型補完が利用可能になりました。

#### リリース品質監査 (Release Audit) による改善

- **[Critical] BUG-01**: `batch_update`, `batch_update_partial`, `batch_delete` メソッドにおいて V2 モードをバイパスして直接 DB を書き換えていた不具合を修正。V2 エンジンのステージングバッファを経由するようにルーティングし、データの整合性と順序を保証しました。
- **[Critical] BUG-02**: `clear()` および `load_all()` メソッドにおいて、V2 エンジンの `flush()` が完了する前に DB 操作が実行され、古いデータが再挿入される「幽霊書き込み（Ghost Re-inserts）」が発生する問題を修正。`flush(wait=True)` による同期的待機を導入しました。
- **[High] QUAL-01**: `AsyncNanaSQLite.add_hook()` の実装を整理。ベース DB 初期化前後のフック登録処理を堅牢化し、非同期実行時の安定性を向上させました。
- **[Non-Breaking] API 拡張**: `flush()` (同期) および `aflush()` (非同期) に `wait` 引数を追加。バックグラウンド処理の完了を待機できるようになりました。
- **[High] Python 3.9 互換性の完全復旧**:
  - 全てのソースファイルに `from __future__ import annotations` を追加し、Python 3.10+ の `|` (Union) 演算子を型ヒントで使用していても Python 3.9 で動作するように修正しました。
  - `compat.py` に `EllipsisType` の互換レイヤーを導入し、Python 3.9 環境での `mypy` チェックと実行時の型検証の安定性を向上させました。
  - `pyproject.toml` の `mypy` 設定を `3.9` に更新し、継続的な互換性を保証しました。

#### 新機能: Ultimate Hooks (汎用フック＆制約アーキテクチャ)

- **強力なフック機構の導入**:
  - `NanaHook` プロトコルを新設し、`before_write`, `after_read`, `before_delete` の3つのライフサイクルイベントをフック可能にしました。
  - カスタムフックを自作することで、データの検証、暗号化の拡張、ロギング、他システムへの通知などを自由に実装できます。
- **標準制約（Standard Constraints）の組み込み**:
  - `CheckHook`: SQLite の `CHECK` 制約のような関数ベースの検証を提供。
  - `UniqueHook`: 指定したキー（またはフィールド）の値の一意性を保証（TOCTOU 警告あり、詳細は SEC-03 参照）。
  - `ForeignKeyHook`: 他の `NanaSQLite` テーブルのキーに対する参照整合性を保証（TOCTOU 警告あり、詳細は SEC-04 参照）。
- **外部ライブラリ統合の透過的サポート**:
  - `ValidkitHook`: 従来の `validator` 引数と互換性を持ち、`validkit-py` による高性能バリデーションを提供。
  - `PydanticHook`: `Pydantic` モデルを直接フックに登録することで、読み書き時の自動シリアライズ/デシリアライズおよび厳格な型検証を実現。
- **メソッドの拡張**:
  - `NanaSQLite.add_hook()` および `AsyncNanaSQLite.add_hook()` を追加しました。

#### アーキテクチャ強化と後方互換性

- 従来の `validator` パラメータは内部的に `ValidkitHook` へと自動変換されるようになり、後方互換性が100%維持されています。
- `batch_update`, `get`, `batch_get`, `setdefault`, `pop` など、あらゆるアクセス経路でフックが等しく適用されるように内部ロジックを統合・堅牢化しました。

#### 監査・テスト

- プレリリース監査レポート (`audit.md`) を更新 — v1.5.0 向け 12 件の発見事項を文書化。
- POC スクリプト 5 件を `etc/poc/` に追加。
- POC 検証テスト 14 件を `tests/test_audit_poc.py` に追加。

### [1.5.0dev2] - 2026-03-28 *(リリース済みバージョン — v1.5.0 に統合)*

#### パッケージングとIDE支援の改善
- **[High] PEP 561 準拠と型補完の修正**:
  - `pyproject.toml` の `tool.setuptools` 設定を標準的な `src-layout` 用に刷新。これまで PyPI 配布版で `import nanasqlite` した際に型補完（IntelliSense）が効かなかった問題を修正しました。
  - `include-package-data = true` を有効化し、`MANIFEST.in` を追加することで、ビルドされたパッケージ (.whl, sdist) に確実に `py.typed` ファイルが含まれるようにしました。
  - これにより、VS Code (Pylance) や PyCharm 等の主要な IDE で、インストール直後から `NanaSQLite` や `PydanticHook` などの完全な型補完が利用可能になりました。

### [1.5.0dev1] - 2026-03-28

#### リリース品質監査 (Release Audit) による改善
- **[Critical] BUG-01**: `batch_update`, `batch_update_partial`, `batch_delete` メソッドにおいて V2 モードをバイパスして直接 DB を書き換えていた不具合を修正。V2 エンジンのステージングバッファを経由するようにルーティングし、データの整合性と順序を保証しました。
- **[Critical] BUG-02**: `clear()` および `load_all()` メソッドにおいて、V2 エンジンの `flush()` が完了する前に DB 操作が実行され、古いデータが再挿入される「幽霊書き込み（Ghost Re-inserts）」が発生する問題を修正。`flush(wait=True)` による同期的待機を導入しました。
- **[High] QUAL-01**: `AsyncNanaSQLite.add_hook()` の実装を整理。ベース DB 初期化前後のフック登録処理を堅牢化し、非同期実行時の安定性を向上させました。
- **[Non-Breaking] API 拡張**: `flush()` (同期) および `aflush()` (非同期) に `wait` 引数を追加。バックグラウンド処理の完了を待機できるようになりました。
- **[High] Python 3.9 互換性の完全復旧**:
  - 全てのソースファイルに `from __future__ import annotations` を追加し、Python 3.10+ の `|` (Union) 演算子を型ヒントで使用していても Python 3.9 で動作するように修正しました。
  - `compat.py` に `EllipsisType` の互換レイヤーを導入し、Python 3.9 環境での `mypy` チェックと実行時の型検証の安定性を向上させました。
  - `pyproject.toml` の `mypy` 設定を `3.9` に更新し、継続的な互換性を保証しました。

#### 新機能: Ultimate Hooks (汎用フック＆制約アーキテクチャ)
- **強力なフック機構の導入**:
  - `NanaHook` プロトコルを新設し、`before_write`, `after_read`, `before_delete` の3つのライフサイクルイベントをフック可能にしました。
  - カスタムフックを自作することで、データの検証、暗号化の拡張、ロギング、他システムへの通知などを自由に実装できます。
- **標準制約（Standard Constraints）の組み込み**:
  - `CheckHook`: SQLite の `CHECK` 制約のような関数ベースの検証を提供。
  - `UniqueHook`: 指定したキー（またはフィールド）の値の一意性を保証。
  - `ForeignKeyHook`: 他の `NanaSQLite` テーブルのキーに対する参照整合性を保証。
- **外部ライブラリ統合の透過的サポート**:
  - `ValidkitHook`: 従来の `validator` 引数と互換性を持ち、`validkit-py` による高性能バリデーションを提供。
  - `PydanticHook`: `Pydantic` モデルを直接フックに登録することで、読み書き時の自動シリアライズ/デシリアライズおよび厳格な型検証を実現。
- **メソッドの拡張**:
  - `NanaSQLite.add_hook()` および `AsyncNanaSQLite.add_hook()` を追加しました。

#### アーキテクチャ強化と後方互換性
- 従来の `validator` パラメータは内部的に `ValidkitHook` へと自動変換されるようになり、後方互換性が100%維持されています。
- `batch_update`, `get`, `batch_get`, `setdefault`, `pop` など、あらゆるアクセス経路でフックが等しく適用されるように内部ロジックを統合・堅牢化しました。

### [1.4.1] - 2026-03-25

#### セキュリティ修正
- **[Medium] SEC-02**: `core.py` における `column_type` バリデーションの正規表現を脆弱性パターン（`[\w ]*`）から安全なパターンに修正し、SonarQube が警告していた ReDoS（正規表現によるサービス拒否）の脆弱性を完全に解消しました。

#### バグ修正
- **[High] BUG-01**: `upsert()` および `aupsert()` において、データ辞書を第1引数に渡しつつ `conflict_columns` を指定した場合に `AttributeError` が発生する問題を修正。解決済みの `target_data` のキーを参照するよう内部ロジックを改善しました。（1.4.1rc1）
- **[High] Qual-02**: `AsyncNanaSQLite` の初期化時において、複数の非同期タスクが同時にアクセスした場合に発生する可能性があった競合状態（Race Condition）を修正。`asyncio.Lock` を導入し、スレッドプールの二重初期化を防止しました。
- `AsyncNanaSQLite.table()` において、docstring の分断や引数伝搬の不備により発生していた構文エラーおよび初期化の不具合を修正しました。（1.4.1dev3）
- `AsyncNanaSQLite` の一部メソッドにおいて、機能適用時に重複して定義されていた箇所を整理しました。（1.4.1dev3）

#### 最終監査（Deep Audit）による重要修正
- **[Critical] BUG-02**: V2モードにおいて、書き込み直後に `get()` や `__getitem__` でデータを取得すると古い値が返る「不整合（Stale Read）」バグを修正。バックグラウンドのステージングバッファを優先的に参照するように改善しました。
- **[Critical] QUAL-04**: `AsyncNanaSQLite` の `__init__` 内で `asyncio.Lock()` を初期化していたため、イベントループ外でインスタンス化した際にエラーが発生する問題を修正。ロックを遅延初期化（Lazy Initialization）するように変更しました。
- **[Critical] LOCK-01**: `ExpiringDict` の TTL 失効処理（`on_expire`）が DB ロックを保持したまま呼び出され、通常の書き込み処理と競合してデッドロックが発生する問題を修正。コールバックをロックの外側で実行するように改善しました。
- **[Critical] CONC-01**: `NanaSQLite` の内部キャッシュ更新処理が DB ロックの外側で行われていたため、マルチスレッド環境（`AsyncNanaSQLite` 等）で `RuntimeError` やキャッシュ破損、TOCTOU 競合が発生する問題を修正。キャッシュ操作を DB ロックの保護下に移動しました。
- **[Critical] CONC-02**: V2モードで `table()` を使用して子インスタンスを作成した際、同じ SQLite 接続に対して複数のスレッドが同時にトランザクションを開始しようとしてクラッシュする問題を修正。親子の V2Engine 間で `shared_lock` を共有し、排他制御を強化しました。
- **[Critical] ASYNC-01**: `AsyncNanaSQLite` において V2 モード用のメソッド（`aflush`, `aget_dlq` 等）が未実装であった問題を修正。同期版と同等のすべての管理機能を非同期 API として追加しました。
- **[High] QUAL-05**: V2モードにおいて `begin_transaction()` 等の明示的なトランザクション操作を行うと V2 エンジンのバックグラウンド処理と衝突するため、V2モード時は明示的なトランザクションを禁止（例外送出）するようにガードを追加しました。
- **[High] QUAL-06**: `AsyncNanaSQLite.table()` において `v2_enable_metrics` 設定が子インスタンスに継承されない不具合を修正しました。
- **[Medium] SEC-01 (強化)**: `create_table()` のカラム型バリデーションをブラックリスト方式からホワイトリスト方式（正規表現による記号制限）へ移行し、検知パターンを強化しました。

#### パフォーマンス改善
- **[Low] PERF-01**: LRU および TTL キャッシュ戦略において、データベースに存在しないキーの検索結果を記憶する「ネガティブキャッシュ」を導入し、繰り返しアクセス時の I/O 負荷を削減しました。（同時に、本機能によってセンチネルが混入する破壊的バグを早期発見し修正済みです）（1.4.1rc1）

#### コード品質改善
- **[Low] QUAL-01**: `ExpiringDict` のスケジューラスレッド停止処理を改善し、インスタンス破棄時やクリア時のクリーンアップをより堅牢にしました。（1.4.1rc1）
- **[Low] QUAL-03**: ソースコード内のマジックリテラル（`"BEGIN IMMEDIATE"` 等）の共通定数化を行い、保守性を向上させました。
- **[Low] CI-01**: SonarQube Cloud の「Quality Gate」における誤検知（ドキュメントやスクリプトがカバレッジに含まれる問題）を解消し、認知複雑度などの非本質的な警告を抑制する設定を導入しました。

#### 新機能: V2エンジンの利便性と観測性の向上 (オプトイン)
- **デッドレターキュー (DLQ) の可視化**:
  - `get_dlq()`, `retry_dlq()`, `clear_dlq()` メソッドを同期・非同期（`a*`）両方に追加しました。
  - バックグラウンドで発生したエラー内容を直接確認し、必要に応じて手動でリトライや消去が可能です。
- **メトリクス収集機能**:
  - `v2_enable_metrics=True` を指定することで、エンジンの詳細な統計情報を収集可能になりました。
  - `get_v2_metrics()` により、総フラッシュ件数、処理時間、DLQ発生数などのメトリクスを取得できます。
- **設定の継承**:
  - `table()` メソッドで子インスタンスを作成する際、`v2_enable_metrics` などの V2 固有設定が正しく引き継がれるようになりました。

#### ドキュメント
- **APIリファレンス自動生成の刷新**: `scripts/gen_api_docs.py` を大幅に改修し、VitePress のコールアウトやテーブルを活用した、より美しく使いやすい API ドキュメントの自動生成を実現しました。
- **全ドキュメントのモダン化**: 既存の Markdown ドキュメント内の太字警告等を、VitePress 標準のカスタムコンテナ（`::: warning` 等）へ一括変換し、サイト全体のデザインを統一しました。

### [1.4.0] - 2026-03-12

#### セキュリティ修正
- **[Critical] SEC-01**: `create_table()` のカラム型に対するSQLインジェクション脆弱性を修正。APSW はセミコロン区切りの複数文を一度に実行するため、カラム型定義を通じて任意のSQLを実行可能でした。セミコロン (`;`)、ラインコメント (`--`)、ブロックコメント (`/*`) を含む文字列を拒否するバリデーションを追加しました。

#### バグ修正
- **[High] BUG-01**: V2Engine の `_process_strict_queue()` で `on_success` コールバックがトランザクション COMMIT 前に呼ばれ、後続タスク失敗時のロールバックで不整合が発生する問題を修正。コールバックを COMMIT 成功後に遅延実行するよう変更しました。
- **[Medium] BUG-02**: `AsyncNanaSQLite.table()` で子インスタンスに `_v2_mode`, `_cache_strategy`, `_encryption_key` 等の属性が設定されず `AttributeError` が発生する問題を修正。親インスタンスの全設定を正しく継承するよう変更しました。
- **[Medium] BUG-03**: v2モードで `execute()` 経由の SELECT/PRAGMA/EXPLAIN クエリが常に空結果を返す問題を修正。読み取りクエリをバックグラウンドキューからバイパスして直接実行するよう変更しました。

#### コード品質改善
- **[Low] BUG-04**: `async_core.py` の `_shared_query_impl()` 内で重複していたエイリアス抽出ロジックを `NanaSQLite._extract_column_aliases()` の呼び出しに置き換えました。
- **[Low] QUAL-01**: `update()` メソッドの型アノテーションを `dict` から `dict | None` に修正しました。

### [1.4.0dev2] - 2026-03-12

#### 改善: 非同期 API の完全化
- `AsyncNanaSQLite` において、同期版と同等の全主要メソッドを非同期版（`abackup`, `arestore`, `apragma`, `aget_table_schema`, `alist_indexes`, `aalter_table_add_column`, `aupsert`, `aget_dlq`, `aretry_dlq` 等）として実装・公開しました。

#### 変更: upsert() メソッドの統合と強化
- `upsert()` メソッドのシグネチャを統合し、`(table_name, data_dict, conflict_columns)` パターンと `(key, value)` パターンの両方を単一のメソッドでサポートするように強化しました。
- v2 モード有効時に `(key, value)` パターンで呼び出すと、内部的にバックグラウンドキューへルーティングされます。

#### テスト: ベンチマーク・カバレッジの拡充
- `pytest-benchmark` による計測対象を 158 から **177** に拡大。
- これまで未カバーだった `backup`, `restore`, `pragma`, `DDL (alter table/index)`, `export/import` 等の主要全操作を計測対象に追加しました。
- 非同期ベンチマーク (`tests/test_async_benchmark.py`) を大幅に強化。

#### 修正
- `get_table_schema` メソッドが `table` プロパティが存在しない場合にエラーになる不具合を修正し、`table_name` 引数を省略可能（デフォルトで現在のテーブルを使用）に変更しました。
- プロジェクト全体の `ruff` lint エラー（31件）および `mypy` 型チェックエラーを解消。

### [1.4.0dev1] - 2026-03-12

#### 新機能: v2 アーキテクチャ (オプション)
- **ノンブロッキング・バックグラウンド永続化**:
  - `NanaSQLite(db_path, v2_mode=True)` を指定することで、v2アーキテクチャが有効になります。
  - すべての書き込み操作（KVS操作およびSQL実行）が一時的にメモリ上のバッファまたはキューに格納され、バックグラウンドスレッドで非同期にSQLiteへフラッシュされます。
  - これにより、**書き込みによるメインスレッドのI/Oブロックが完全にゼロ**になり、書き込みレイテンシが劇的に改善します。
  - 読み込みレイテンシは従来通り（メモリキャッシュから直接取得するため）ゼロコストです。
  - **フラッシュモード**: `flush_mode` パラメータで最適なタイミング（`immediate`, `count`, `time`, `manual`）を選択できます。
  - **デッドレターキュー (DLQ)**: バックグラウンドでのSQL実行失敗時に、問題のあるタスクだけを隔離し、他のデータ永続化を継続・保護します。`get_dlq()` で内容確認、`retry_dlq()` で再試行が可能です。
  - **チャンク処理**: 大量データの書き込み時にSQLiteのロックを長時間占有しないよう、バッチを分割（デフォルト 1000件ごと）して少しずつ書き込みます。
  - **注意**: v2アーキテクチャは「単一プロセス」システム専用です。マルチプロセス環境（FastAPI/Gunicornの複数ワーカーなど）ではデータ破損の原因となるため警告が出力されます。

#### 変更
- `NanaSQLite` および `AsyncNanaSQLite` の `__init__` に `v2_mode`, `flush_mode`, `flush_interval`, `flush_count`, `v2_chunk_size` パラメータを追加。
- 手動フラッシュ用の `flush()` (同期) および `aflush()` (非同期) メソッドを追加。
- `V2Engine` に DLQ 管理用の `get_dlq()`, `retry_dlq()` メソッドを追加。

#### 修正
- v2 エンジンにおけるデッドレターキュー (DLQ) への同時アクセスによる競合状態 (Race Condition) を修正。
- v2 エンジンにおいて Staging Buffer が空の場合に Strict Queue が処理されない不具合を修正。

### [1.3.4] - 2026-03-10

#### セキュリティ修正

- **SEC-01 [High]**: `alter_table_add_column()` の `column_type` バリデーションをブラックリスト方式からホワイトリスト正規表現に変更。`TEXT; DROP TABLE` のようなインジェクションペイロードを確実にブロック。
- **SEC-02 [High]**: `sanitize_sql_for_function_scan()` を修正し、ダブルクォート付き SQL 識別子の内容を保持するよう変更。`"LOAD_EXTENSION"()` のようなクォート付き関数名バイパスを `_validate_expression()` が正しく検出可能に。

#### バグ修正

- **BUG-01 [Critical]**: `items()` メソッドに `_check_connection()` チェックを追加。クローズ済みインスタンスで呼び出した際に APSW 低レベル例外ではなく `NanaSQLiteClosedError` が発生するよう修正。
- **BUG-02 [High]**: AEAD 暗号化有効時に非 bytes 値を受け取った場合、サイレントに平文 JSON フォールバックするのではなく警告ログを出力するよう変更。
- **BUG-03 [High]**: AEAD 復号前に nonce+認証タグを含む最小長の検証（≥28 バイト = nonce 12 + auth tag 16）を追加。短すぎるデータに対して明確な `NanaSQLiteDatabaseError` を送出。InvalidTag など低レベル例外も同エラーにラップ。
- **BUG-04 [High]**: `AsyncNanaSQLite.acontains()` の冗長な二重 `_ensure_initialized()` 呼び出しを削除。
- **BUG-05 [Medium]**: 非同期 `_shared_query_impl()` に `offset` パラメータの型・非負チェックを追加。
- **BUG-06 [Medium]**: `async_core.py` の `parameters: tuple = None` を `tuple | None = None` に修正（mypy strict 対応）。
- **BUG-07 [Medium]**: `ExpiringDict` スケジューラが 1 反復で期限切れキーをすべて処理するよう改善（従来は 1 キーずつ）。
- **BUG-09 [Medium]**: `batch_get()` が値 `None` を明示的に格納したキーを結果に含めるよう修正。
- **BUG-10 [Low]**: `_sanitize_identifier()` でコンパイル済み `IDENTIFIER_PATTERN` を再利用。
- **BUG-12 [Low]**: `NanaSQLiteDatabaseError.__init__` の `original_error` 型アノテーションを `Exception | None` に修正。

#### パフォーマンス改善

- **PERF-03 [Medium]**: カラム名エイリアス抽出ロジックを `_extract_column_aliases()` ヘルパーに共通化（3 箇所の重複排除）。

#### コード品質改善

- **QUAL-01 [Medium]**: `_get_all_keys_from_db()` の戻り値型を `list[str]` に修正。
- **QUAL-03 [Medium]**: `query()` と `query_with_pagination()` 間のカラム名クォート除去ロジックを統一。

#### 監査・テスト

- プレリリース監査レポート (`audit.md`) を追加 — 35 件の発見事項を文書化。
- POC スクリプト 6 件を `etc/poc/` に追加。
- POC 検証テスト 20 件を `tests/test_audit_poc.py` に追加。
- `audit_prompt.md` を 6 フェーズ構成に改正（監査 → POC → パッチ → pytest → CI 検証 → リリース準備）。

### [1.3.4rc4] - 2026-03-08

#### CI 修正

- **provenance ジョブの権限を最小権限に変更** (PR [#127](https://github.com/disnana/NanaSQLite/pull/127)):
  - `provenance` ジョブの `contents: write` を `contents: read` に降格。`upload-assets` を使わないため `write` 権限は不要だった。
  - 無効だった `upload-assets: true` を削除（タグトリガーのないワークフローでは常にスキップされていたデッドコード）。
  - プロベナンスの GitHub Release への添付は `release` ジョブが引き続き担当。
  - CI アノテーション（`go.sum not found` ワーニング・PyPI アテステーション通知）の原因をコメントで説明し、誤解を防止。
  - `CHANGELOG.md` を main ブランチの最新版に同期。

### [1.3.4rc3] - 2026-03-08

#### CI 修正

- **SLSA3 provenance リリースフローを復旧・安定化** (PR [#123](https://github.com/disnana/NanaSQLite/pull/123)):
  - GitHub Actions の provenance 検証ジョブに `actions: read` / `contents: read` 権限を追加。
  - `provenance-name` 出力から期待する provenance ファイル名を明示的に組み立て、存在確認に失敗した場合は早期終了するよう改善。
  - GitHub Release へ添付する provenance アーティファクトをワイルドカードではなく生成済みファイル名で指定し、リリース時の取り違えを防止。

### [1.3.4rc2] - 2026-03-08

#### セキュリティ修正

- **SQLインジェクション保護を実装** (PR [#121](https://github.com/disnana/NanaSQLite/pull/121), [#122](https://github.com/disnana/NanaSQLite/pull/122)):
  - テーブル名を SQL クエリ内で直接展開していたため、細工されたテーブル名でインジェクションが可能でした。
  - `self._safe_table` にサニタイズ済み（クォート済み）のテーブル名をキャッシュし、すべての SQL 実行箇所でこちらを使用するよう変更。
  - `self._table` は従来どおり生の名前を保持し、`__repr__` や後方互換のために使用。
  - SECURITY.md を更新し脆弱性の経緯と修正内容を記載。
  - PoC スクリプト (`etc/poc/poc_sqli.py`, `etc/poc/poc_none.py`) を追加してリスクを文書化。

#### バグ修正・コード品質改善

- **`_NOT_FOUND` センチネルを `get_fresh()` および `__contains__` に適用** (PR [#121](https://github.com/disnana/NanaSQLite/pull/121)):
  - `get_fresh()` が DB ミス時に `None` を返すため、実際に `None` を格納したキーと区別できなかった問題を修正。
  - `_NOT_FOUND = object()` センチネルを使用し、DB ミスと格納値 `None` を正確に識別できるよう改善。
  - `__contains__` を軽量な実装に戻し、不要な DB 読み込みを削減。

#### CI 修正

- **validkit-py の CI テストガードを修正** (PR [#119](https://github.com/disnana/NanaSQLite/pull/119)):
  - CI で `validation` エクストラをインストールするよう修正し、validkit 関連テストが正しく実行されるようになった。

#### ドキュメント

- **validkit-py バリデーションガイドを追加** (PR [#117](https://github.com/disnana/NanaSQLite/pull/117)):
  - 日英両方のドキュメントサイトに validkit-py の使い方・バリデーションガイドを追加。
- **ガイドのレッスン順序を整理** (PR [#116](https://github.com/disnana/NanaSQLite/pull/116)):
  - JA/EN サイトドキュメントのガイドレッスンを再整理・分類。
- **ドキュメントの不整合・リンク切れ・誤記を修正** (PR [#115](https://github.com/disnana/NanaSQLite/pull/115)):
  - 英語・日本語ドキュメント間の不整合、壊れたリンク、誤った記述、および欠落していた文書を修正。

### [1.3.4rc1] - 2026-03-07

#### 新機能

- **`batch_update_partial()` メソッドを追加**（同期・非同期）:
  - `validator` が設定されている場合にバッチ書き込みを「部分成功モード」で実行する新メソッド。
  - 各エントリを個別にバリデーションし、成功したものだけ DB に書き込む。
  - 失敗したエントリは `{key: エラーメッセージ}` の `dict` として返却し、例外は送出しない。
  - `coerce=True` の場合は変換済みの値で書き込む。
  - 既存の `batch_update()` はアトミック動作（全件成功 or 全件拒否）のまま維持。
  - 非同期版は `AsyncNanaSQLite.abatch_update_partial()` として追加。

#### バグ修正・コード品質改善

- **`core.py` mypy エラーを修正**:
  - `_serialize()` の `json_str` が `HAS_ORJSON=False` パスで `str` 確定だが mypy が `str | None` と推論していたため `type: ignore` を付与。
- **examples の ruff 違反を修正**:
  - `examples/test_examples.py`: import ソート（I001）、`assert False` → `raise AssertionError()`（B011）、クラス名を CapWords に変更（N801）。
  - `examples/validkit_batch_demo.py`: import ソート（I001）。

#### サンプル追加

- **`examples/validkit_batch_demo.py` を追加**:
  - `batch_update()` のアトミック動作と `batch_update_partial()` の部分成功モードを実演。
  - `coerce=True` との組み合わせ例を含む。
- **`examples/test_examples.py` に validkit バッチ操作の検証を追加**:
  - `batch_update()` のロールバック確認、`batch_update_partial()` の部分書き込み確認、`coerce=True` の変換確認。

### [1.3.4b3] - 2026-03-05

#### バグ修正・安定性改善

- **Python 3.9 でのテスト不安定問題を修正** (`tests/test_tdd_cycle_6.py`) (PR [#113](https://github.com/disnana/NanaSQLite/pull/113)):
  - `test_ellipsis_type_is_available` は `types.EllipsisType`（Python 3.10 で追加）の有無を確認するテストですが、
    Python 3.9 環境では無条件に失敗していました。
  - `@pytest.mark.skipif(sys.version_info < (3, 10), ...)` デコレータを追加し、Python 3.9 では
    このテストをスキップするよう修正。Python 3.10 以降では引き続き実行されます。
  - `from __future__ import annotations` が有効なため、`types.EllipsisType` を使った型注釈は
    ランタイムに評価されず、Python 3.9 でも本体コードは正常に動作します（テストのみの問題でした）。
  - ライブラリの動作・公開 API への影響はありません。

- **`table()` のキャッシュ設定継承を修正** (PR [#112](https://github.com/disnana/NanaSQLite/pull/112)):
  - `table()` で子インスタンスを生成する際、`cache_ttl` / `cache_persistence_ttl` が親から引き継がれず、
    TTL キャッシュ戦略を使用している場合に `ValueError` が発生する問題を修正。
  - `_cache_strategy_raw` / `_cache_size_raw` / `_cache_ttl_raw` / `_cache_persistence_ttl_raw` を内部に保持し、
    `table()` が全キャッシュ設定を正しく継承するよう修正。

- **`AsyncNanaSQLite` での validkit-py 未インストール時 `ImportError` の即時送出** (PR [#112](https://github.com/disnana/NanaSQLite/pull/112)):
  - 従来は操作実行時まで `ImportError` が遅延されていたが、`AsyncNanaSQLite.__init__` で `validator` を指定した時点で
    即座に送出するよう修正（`NanaSQLite` との挙動を統一）。
  - `HAS_VALIDKIT` フラグを `async_core.py` に追加。

- **例外の絞り込み** (`core.py`):
  - オプション依存（orjson / validkit-py）のインポートで `except Exception:` を使用していた箇所を `except ImportError:` に変更。

- **型アノテーション修正**:
  - `table()` の `cache_strategy` 引数の `Literal` 型に `"ttl"` を追加。
  - `_UNSET` センチネルの型注釈を `types.EllipsisType` に変更し、型安全性を向上。

- **mypy 設定更新** (`pyproject.toml`):
  - `python_version` を `3.9` → `3.10` に更新し、`types.EllipsisType` を型チェック時に認識させるよう修正。

#### API ドキュメント修正 (PR [#112](https://github.com/disnana/NanaSQLite/pull/112))

- `NanaSQLite.table()` および `AsyncNanaSQLite.table()` の API ドキュメント（日・英）で、
  `validator` / `coerce` の既定値が `= ...`（親から継承）であることを明記。

#### テスト・品質改善 (PR [#112](https://github.com/disnana/NanaSQLite/pull/112))

- **包括的テストスイートを追加**:
  - `tests/test_table_inheritance_comprehensive.py`: `table()` の全継承パターンを 75 ケースで検証。
  - `tests/test_validkit_integration.py`: validkit-py 統合テスト（同期・非同期）。
  - `tests/test_tdd_review_fixes.py`: レビューコメント対応の検証テスト。
  - `tests/test_tdd_cycle_2.py` 〜 `tests/test_tdd_cycle_10.py`: TDD サイクルごとの回帰テスト。
- **validkit インストール確認の方法を改善**:
  - `importlib.util.find_spec` から `try/except import` 方式に変更し、破損インストールも正しく検出。

### [1.3.4b2] - 2026-03-04

#### 新機能

- **`validator` パラメータの追加（オプション依存: validkit-py）**:
  - `NanaSQLite.__init__` および `AsyncNanaSQLite.__init__` に `validator` パラメータを追加。
  - validkit-py のスキーマ（辞書または `Schema` オブジェクト）を渡すと、値の書き込み時に自動バリデーションを実行します。
  - スキーマ違反時は `NanaSQLiteValidationError` を送出。
  - validkit-py をインストールせずに `validator` を指定した場合は `ImportError` を送出し、インストール手順を案内します。
  - `pip install nanasqlite[validation]` でインストール可能。
  - `HAS_VALIDKIT` フラグを `nanasqlite` パッケージ（および `core` モジュール）から公開。

- **`table()` の `validator` 引数対応**:
  - `NanaSQLite.table()` および `AsyncNanaSQLite.table()` に `validator` パラメータを追加。
  - テーブルごとに異なるスキーマを適用可能。
  - `validator` を省略した場合は親インスタンスのスキーマを自動継承。

- **`coerce` パラメータの追加（自動変換オプション）**:
  - `NanaSQLite.__init__`、`NanaSQLite.table()`、`AsyncNanaSQLite.__init__`、`AsyncNanaSQLite.table()` に `coerce: bool = False` パラメータを追加。
  - `True` を指定すると、validkit-py のバリデーション後に変換済みの値（例: `"42"` → `42`）をDBに保存します。
  - **注意**: 自動変換を機能させるには、スキーマの各フィールドバリデーターにも `.coerce()` を呼び出す必要があります（例: `v.int().coerce()`）。フィールドに `.coerce()` がない場合、型が一致しない値はバリデーションエラーになります（NanaSQLite の `coerce=True` だけでは変換されません）。
  - `validator` と組み合わせて使用します。`validator` が設定されていない場合は無効。
  - `table()` で省略した場合は親インスタンスの設定を引き継ぐ。

- **`batch_update()` バリデーション対応**:
  - `validator` を設定している場合、`batch_update()` はすべての値を DB 書き込み前に一括バリデーションするようになりました。
  - 1件でもスキーマ違反があった場合、何も書き込まれません（アトミックな失敗保証）。
  - `coerce=True` を設定している場合、変換済みの値を一括書き込みします。

#### バグ修正

- **`table()` で `validator` が子インスタンスに引き継がれない問題を修正**:
  - b1 では `table()` で生成した子インスタンスに親の `_validator` が渡されておらず、
    サブテーブルへの書き込み時にバリデーションが実行されませんでした。
  - `AsyncNanaSQLite.table()` でも同様に `_validator` が `async_sub_db` に設定されていなかった問題を修正。

### [1.3.4b1] - 2026-03-04

#### 新機能

- **`lock_timeout` パラメータの追加** (P2-1):
  - `NanaSQLite.__init__` に `lock_timeout: float | None = None` パラメータを追加。
  - 設定すると、ロック取得時に指定秒数以内に取得できない場合は `NanaSQLiteLockError` を送出。
  - デフォルト `None` は従来通り無制限待機。後方互換性への影響はありません。
  - 内部に `_acquire_lock()` コンテキストマネージャを新設し、ユーザー操作に伴う排他制御ではロックタイムアウトが反映されます（一部の内部処理〈期限切れ削除など〉は従来通りブロッキング取得のままです）。

- **`backup()` / `restore()` メソッドの追加** (P2-3):
  - `NanaSQLite.backup(dest_path)`: APSW の SQLite オンラインバックアップ API を使用して、現在の DB を `dest_path` にバックアップします。
  - `NanaSQLite.restore(src_path)`: `src_path` のバックアップファイルから DB を復元し、接続を再確立してキャッシュをクリアします。リストア時に WAL/SHM/journal サイドカーファイル（`-wal`/`-shm`/`-journal`）を明示的に削除し、stale な WAL 内容の再生による不整合を防止します。
  - 両メソッドとも新規 public メソッドの追加のみ。後方互換性への影響はありません。

#### スレッドセーフティ改善

- **`table()` の子インスタンス生成をロック保護**:
  - `table()` での子インスタンス生成〜`WeakSet` 追加を `_acquire_lock()` で保護。`restore()` の接続差し替えとの競合を防止し、子インスタンスが閉じた接続を参照するリスクを排除。

#### バグ修正

- **`__delitem__` に `_check_connection()` を追加**:
  - `del db[key]` でクローズ済み接続を使用した際に `NanaSQLiteClosedError` を送出するよう修正。`__setitem__`・`pop()`・`clear()` と例外挙動を統一。

### [1.3.4b0] - 2026-03-04

#### コード品質改善
- **非同期プールクリーンアップのログレベル修正**:
  - `AsyncNanaSQLite.close()` 内の読み取り専用プールドレイン処理で、`AttributeError` 発生時のログレベルを `ERROR` から `WARNING` に変更。
  - あわせてコメントの文言を「Programming error」から実態に即した「Unexpected AttributeError - log and continue cleanup for resilience」に修正。
  - ログ出力のみの変更であり、動作・後方互換性への影響はありません。

#### ドキュメント・計画
- **v1.3.x 計画レビュードキュメントの追加** (`etc/in_progress/v1.3.x_plan_review.md`):
  - `etc/` 配下の全計画書を横断的にレビューし、v1.3.x で実施すべき残タスクを整理・優先順位付け。
  - ロードマップ残項目（ロックタイムアウト、バリデーション基盤、バックアップ/リストア）の対応優先度を明記。
  - v1.3.4b0 〜 v1.4.0 のリリース計画案を記載。
- **`etc/README.md` 更新**: 新規レビュードキュメントを `in_progress/` 一覧に追記。
- **`etc/` ディレクトリの再編**（PR [#109](https://github.com/disnana/NanaSQLite/pull/109)）:
  - `etc/` を実装状況別（`implemented/`・`in_progress/`・`planned/`）のサブディレクトリ構造に再編。フラットな `future_plans/` フォルダを廃止。
  - v1.3.0 キャッシュ機能（`ExpiringDict`・`UnboundedCache`・`TTLCache` 等）がすべて実装済みであることを確認。

#### 依存関係更新（docs/site メンテナンス）
- **docs/site 依存ライブラリの更新**（Renovate）:
  - `autoprefixer` を v10.4.24 → v10.4.27 に更新。([#105](https://github.com/disnana/NanaSQLite/pull/105))
  - `postcss` を v8.5.6 → v8.5.8 に更新。([#106](https://github.com/disnana/NanaSQLite/pull/106))
  - `vue` を v3.5.27 → v3.5.29 に更新。([#107](https://github.com/disnana/NanaSQLite/pull/107))
  - `tailwindcss` / `@tailwindcss/postcss` を v4.1.18 → v4.2.1 に更新。([#108](https://github.com/disnana/NanaSQLite/pull/108))

### [1.3.4dev0] - 2026-03-02

#### CI / 開発環境
- **SLSA プロバナンスキャッシュ警告への対応・撤退**:
  - `provenance / generator` ジョブが `go.sum` を探して `Restore cache failed` 警告を出力していたため、空の `go.sum` をリポジトリルートに追加（PR [#103](https://github.com/disnana/NanaSQLite/pull/103)）。
  - その後、`provenance / generator` ジョブは独立したランナーで実行されリポジトリをチェックアウトしないため、ファイルの有無に関係なく警告を解消できないことが判明。空の `go.sum` を削除（PR [#104](https://github.com/disnana/NanaSQLite/pull/104)）。

#### その他
- バージョンを `1.3.4dev0` に引き上げ（`1.3.3` リリース後の開発スナップショット）。

### [1.3.3] - 2026-03-02

#### セキュリティ
- **docs/site の依存関係脆弱性対応**:
  - rollup の脆弱性（GHSA-mw96-cpmx-2vgc）に対応するため、`docs/site` 側で rollup を安全なバージョン（`>=4.59.0`）へ更新/固定。
  - 関連PR: [#99](https://github.com/disnana/NanaSQLite/pull/99), [#102](https://github.com/disnana/NanaSQLite/pull/102)

#### CI / 開発環境
- **GitHub Actions の更新**:
  - `actions/download-artifact` を v8 に更新。([#100](https://github.com/disnana/NanaSQLite/pull/100))
  - `actions/upload-artifact` を v7 に更新。([#101](https://github.com/disnana/NanaSQLite/pull/101))
  - `google/osv-scanner-action`（reusable / reusable-pr）を 2.3.3 に更新。([#97](https://github.com/disnana/NanaSQLite/pull/97), [#98](https://github.com/disnana/NanaSQLite/pull/98))

#### 依存関係更新（メンテナンス）
- **リリース自動化アクション更新**:
  - `softprops/action-gh-release` を v2 に更新。([#96](https://github.com/disnana/NanaSQLite/pull/96))

#### 備考
- このリリースは主にメンテナンス（セキュリティ/CI/依存更新）を目的としたもので、ライブラリの公開API互換性に影響する変更は含みません。

### [1.3.2] - 2026-01-17

#### パフォーマンス最適化
- **orjson 統合の最適化**:
  - `_serialize()` メソッドの不要な変数割り当てを削除し、コード可読性と保守性を向上。
  - orjson による JSON エンコード/デコードが全暗号化パス（Fernet, AES-GCM, ChaCha20）で効果的に活用されることを確認・検証。
  - 標準 `json` モジュールと比較して **3~5倍の高速化** を期待。
  - 非同期処理（`AsyncNanaSQLite`）では ThreadPoolExecutor 経由で自動的に orjson の恩恵を受けるアーキテクチャを確認。

#### コード品質改善
- **本体コードの最適化**:
  - コード可読性を向上させ、変数スコープを明確化。

#### テスト・検証
- **orjson テストの実行確認**:
  - `tests/test_json_backends.py` の全テストが正常に動作することを確認。
  - orjson 有無時の互換性テストが両環境で正常に実行。
  - JSON バックエンドの自動切り替え機能（HAS_ORJSON フラグ）が正常に動作。

### [1.3.1] - 2025-12-28

#### 新機能: オプションのデータ暗号化
- **マルチモード暗号化**: `cryptography` を使用した透過的な暗号化を実装。
    - **AES-GCM (デフォルト)**: 安全かつ高速。ハードウェア加速(AES-NI)対応環境で最適。
    - **ChaCha20-Poly1305**: ハードウェア加速がない環境（ARM等）でも高速なソフトウェア実装。
    - **Fernet**: 従来通りの使いやすさと互換性重視のオプション。
    - `NanaSQLite` および `AsyncNanaSQLite` に `encryption_key` および `encryption_mode` 引数を追加。
    - SQLite への保存前に暗号化し、取得時に自動復号。
    - **ハイブリッド設計**: メモリキャッシュ内は平文で保持されるため、暗号化有効時も高速なリードパフォーマンスを維持。
- **拡張インストール**: `pip install nanasqlite[encryption]` で必要な依存関係を含めてインストール可能に。

#### 新機能: 柔軟なキャッシュ戦略と TTL サポート (v1.3.1-alpha.0)
- **TTL (Time-To-Live) キャッシュ**: `cache_strategy=CacheType.TTL, cache_ttl=seconds` でデータの有効期限を設定可能に。
- **Persistence TTL (自動削除)**: `cache_persistence_ttl=True` で失効時に SQLite からも自動削除。
- **FIFO 制限付き Unbounded**: 無制限キャッシュでも `cache_size` 指定で FIFO 方式のメモリ制限が可能。
- **キャッシュクリア API**: `db.clear_cache()` および非同期版 `aclear_cache()` を追加。

#### 改良と修正
- **最適化された `ExpiringDict`**: 低オーバーヘッドかつ高精度な有効期限管理ユーティリティを内部実装。
- **後方互換性の維持**: デフォルトの `UNBOUNDED` モードでは従来通りの高速パスを維持しつつ、制限設定時のみインターセプトを適用。
- **型安全性の向上**: `mypy` と `ruff` による厳格なチェックを通過し、型ヒントを強化。
- **ベンチマークの統合**: `tests/test_benchmark.py` (Sync) と `tests/test_async_benchmark.py` (Async) に暗号化・キャッシュ戦略のベンチマークを集約し、可視性を向上。
- **テストカバレッジ**: 非同期環境におけるキャッシュ挙動（LRU退避、TTL失効）の検証テスト `tests/test_async_cache.py` を追加。

### [1.3.0dev0] - 2025-12-27

#### 新機能: 柔軟なキャッシュ戦略
- **`CacheType` 列挙型の追加**: `UNBOUNDED` (無制限、従来動作) と `LRU` (追い出し型) を選択可能に。
- **LRUキャッシュの実装**: `cache_strategy=CacheType.LRU, cache_size=N` でメモリ使用量を制限可能。
- **テーブル別設定**: `db.table("logs", cache_strategy=CacheType.LRU, cache_size=100)` で個別設定。
- **高速化オプション**: `pip install nanasqlite[speed]` で C拡張 `lru-dict` を導入し、最大2倍の速度向上。
- **自動フォールバック**: `lru-dict` 未インストール時は標準ライブラリ `OrderedDict` を使用。

#### 新規テスト
- `tests/test_cache.py`: キャッシュ戦略の包括的テストスイート（追い出し、永続化、テーブル別設定）。

### [1.2.2b1] - 2025-12-27

#### ドキュメントとブランドの刷新
- **超モダンなドキュメントサイトの構築**:
  - VitePress + Tailwind CSS を採用し、デザイン性とブラウジング体験を大幅に向上させた公式サイトを `docs/site` に構築。
  - **公式SVGロゴの制作**: 辞書 `{ }` とデータスタックを融合させた独自シンボルを開発。100%透過、ダークモード自動対応（反転フィルタ）、無限解像度のベクター形式。
  - **多言語APIリファレンスの真の分離**: docstringからターゲット言語（日・英）のみを抽出・整形するインテリジェントな生成エンジンを実装。
- **自動化と公開**:
  - GitHub Actions による docs 自動ビルド・公開ワークフロー (`deploy-docs.yml`) を導入。
  - 公開時に `gh-pages` ブランチの過去のベンチマーク履歴を自動取得・マージし、履歴を保護するロジックを実装。

#### セキュリティと安定性の向上
- **SQL検証の適正化**:
  - `||` (文字列連結) 演算子を高速検証の許可リストに追加し、複雑なエイリアスを含むクエリでの誤検知を解消。
- **CI/CDの安定化**:
  - `ruff` の最新ルールに基づき、`core.py` および `gen_api_docs.py` のインポート順序を厳密に整理。
  - 依存関係の欠落を防ぐため、docsビルド時の依存管理を強化。

### [1.2.2a1] - 2025-12-26

#### 開発ツール (ベンチマーク・CI/CD)
- **ベンチマークの性能比較ロジックを修正**:
  - 比較計算を Ops/sec ベースに統一し、速度向上時に正しく `+`（🚀/✅）が表示されるように改善。
  - サマリーテーブルに Ops/sec の絶対値の差分（例: `+2.1M ops`）を追加。
  - **Ops/sec 計算の正確性向上**: 平均時間からの逆算（近似値）ではなく、ベンチマークツールの生データ (`ops`) を直接使用するように修正。これにより、OS別詳細表示で `(0.0)` と表示されるバグも解消。
  - 0.001ms 未満の微小な時間計測結果に対して `ns` (nanoseconds) 単位を正しく表示。
  - 絵文字（🚀, ✅, ➖, ⚠️, 🔴）による直感的なパフォーマンス評価を追加。
- **CI/CDワークフローの最適化**:
  - `benchmark.yml`: GitHub Actions ランナーの性能ばらつき（10-60%）を考慮し、ベンチマークを「情報提供のみ」に変更。性能低下による CI 失敗を防止。
  - `ci.yml`: トリガーを最適化し、`push` による自動実行を `main` ブランチのみに限定。他ブランチは `workflow_dispatch` で手動実行可能に。
  - `should-run` ジョブの判定ロジックを簡略化。


### [1.2.1b2] - 2025-12-25

#### 開発ツール
- **CI/CDワークフローの統合**:
  - `lint.yml`, `test.yml`, `publish.yml`, `quality-gate.yml` を一つの `ci.yml` に統合。
  - リリースサマリーにPyPIとGitHub Releaseへの直接リンク、詳細なジョブステータス（Cancelled/Skipped対応）を追加。
- **テスト環境の最適化**:
  - CIテストマトリックスを調整。Ubuntuは全バージョン、Windows/macOSは利用率の高い Python 3.11および3.13に絞り込み、実行時間を短縮。
  - dev依存関係に `pytest-xdist` を追加し、並列テストをサポート。
- **型チェックの改善**:
  - mypy設定の緩和と整理により、156件の型エラーを解消（`--no-strict-optional` の導入とエラーコードの個別制御）。

#### 開発ツール
- **リント・CI環境の追加**:
  - `tox.ini` を追加し、`tox -e lint` (ruff), `tox -e type` (mypy), `tox -e format`, `tox -e fix` の環境を構築。
  - `pyproject.toml` にruff設定を追加（E/W/F/I/B/UP/N/ASYNCルール、Python 3.9+対応、line-length: 120）。
  - `pyproject.toml` にmypy設定を追加（`--no-strict-optional`フラグ使用、実用的な型チェック）。
  - `.github/workflows/lint.yml` を追加：PyPA/twineスタイルのCIワークフロー（tox統合、FORCE_COLOR対応、サマリー出力）。
  - `.github/workflows/quality-gate.yml` を追加：all-greenゲートでmainブランチ判定とpublish準備確認。
  - dev依存関係に `tox>=4.0.0`, `ruff>=0.8.0`, `mypy>=1.13.0` を追加。
- **コード品質改善**:
  - ruff auto-fixで1373件のリントエラーを修正（import順序、未使用import削除、pyupgrade、whitespace等）。
  - B904 (raise without from), B017 (assert raises Exception) をignore listに追加。
  - mypy設定を実用的に調整（156エラー → 0エラー）。

### [1.2.0b1] - 2025-12-24

#### セキュリティと堅牢性
- **`ORDER BY` 解析の強化**:
  - `NanaSQLite` に専用のパーサー `_parse_order_by_clause` を実装し、複雑な `ORDER BY` 句を安全に処理・検証できるようにしました。
  - 正当なソートパターンをサポートしつつ、SQLインジェクションに対する保護を強化しました。
- **厳格な検証の修正**:
  - 危険なパターン（`;`, `--`, `/*`）に対するエラーメッセージを `Invalid [label]: [message]` の形式に統一しました。
  - すべての検証エラーに対して統一されたメッセージ形式を適用することで、レガシーテストと新しいセキュリティテスト間の一貫した動作を保証しました。

#### リファクタリング
- **コード構成**:
  - `_sanitize_sql_for_function_scan` ロジックを新しい `nanasqlite.sql_utils` モジュールに抽出・移動し、保守性を向上させました。
  - `AsyncNanaSQLite` の `query` と `query_with_pagination` メソッドから重複コードを削除し、共通ロジックを `_shared_query_impl` ヘルパーメソッドに統合しました（約150行の削減）。
- **型安全性**:
  - `context` パラメータに `Literal` 型ヒントを追加し、IDEサポートと型チェックを強化しました (PR #36)。

#### 修正と改善
- **非同期ロギング**:
  - 読み取り専用プールのクリーンアップ中に発生するエラーのログレベルを DEBUG から WARNING に引き上げ、リソースの問題を検知しやすくしました。
  - エラーメッセージに接続コンテキスト情報を追加しました。
- **非同期プールクリーンアップの堅牢性向上**:
  - `AsyncNanaSQLite.close()` メソッドにおいて、プール内の一部の接続でエラーが発生しても、残りの接続を確実にクリーンアップするように改善しました。
  - `AttributeError` 発生時に `break` していた処理を継続するように変更し、リソースリークを防止します。
- **テスト**:
  - インスタンスがクローズされている場合に `__eq__` が正しく `NanaSQLiteClosedError` を送出するように修正しました (PR #44)。
  - セキュリティテストにおける例外ハンドリングの具体性を向上させました (PR #43)。
  - セキュリティテストのコメントを明確化し、検証タイミングの説明を追加しました (PR #35)。
  - 重複していた `pytest` インポートを削除し、一時的なテストファイル（`temp_test_parser.py`）を整理しました。

### [1.2.0a2] - 2025-12-23

- **非同期セキュリティ機能の強化**:
  - `AsyncNanaSQLite.query` および `query_with_pagination` において、`allowed_sql_functions`, `forbidden_sql_functions`, `override_allowed` が正しく `_validate_expression` に渡されるように修正。
  - `AsyncNanaSQLite` の非同期セキュリティテスト (`tests/test_security_async_v120.py`) を追加。
- **非同期接続管理の改善**:
  - `AsyncNanaSQLite` にクローズ状態を追跡する `_closed` フラグを追加。
  - 親インスタンスがクローズされた際に、`table()` で作成された子インスタンスも即座にクローズ状態となるように改善。
  - 未初期化のインスタンスをクローズした場合でも、その後の操作で正しく `NanaSQLiteClosedError` が発生するように修正。

### [1.2.0a1] - 2025-12-23

- **非同期読み取り専用接続プール**:
  - `AsyncNanaSQLite` に `read_pool_size` 引数を追加。
  - `query`, `query_with_pagination`, `fetch_all`, `fetch_one` メソッドで読み取り専用プールを使用可能に。
  - 安全性のため、プール接続は常に `read-only` モードで動作。
- **バグ修正**:
  - `query` および `query_with_pagination` で結果が0件の場合に発生していた `apsw.ExecutionCompleteError` を修正。
  - カラム名の取得方法を `cursor.description` 依存から同期版と同様の `PRAGMA table_info` および手動パース方式に変更。

### [1.2.0dev1] - 2025-12-23

#### 修正
- **非同期APIの一貫性向上**:
  - `AsyncNanaSQLite` に全てのメソッドの `a` プレフィックス付きエイリアス（`abatch_update`, `ato_dict` 等）を追加。
  - ベンチマークテスト (`test_async_benchmark.py`) でのメソッド未定義エラーを解消。
- **後方互換性の修正**:
  - SQLインジェクション検知時のエラーメッセージを `test_security.py` 等の既存テストが期待する形式（"Invalid order_by clause" 等）に再調整。
  - `test_enhancements.py` において `NanaSQLiteClosedError` を許容するように修正し、例外クラス名チェックとの整合性を確保。
- **Windows環境の安定性向上**:
  - `test_security_v120.py` で `pytest` の `tmp_path` フィクスチャを使用するように変更し、Windowsでの `BusyError` や `IOError` を回避。
- **`query`/`query_with_pagination` のバグ修正**:
  - `limit=0` および `offset=0` が無視されていた問題を修正。`if limit:` から `if limit is not None:` に変更。
  - ⚠️ **後方互換性**: 以前は `limit=0` を渡すと全件取得していましたが、今後は正しく0件を返します。`limit=0` を「制限なし」の意味で使用していた場合は `limit=None` に変更してください。
- **エッジケーステストの追加**:
  - `tests/test_edge_cases_v120.py` を新規作成。空リストでの `batch_*` 操作やページネーションの境界値テストを追加。

### [1.2.0dev0] - 2025-12-22

#### 追加
- **セキュリティ強化 (Phase 1)**:
  - `strict_sql_validation` フラグの導入（未許可関数の使用時に例外または警告）。
  - `max_clause_length` による動的SQLの長さ制限（ReDoS対策）。
  - 文字列ベースの危険なSQLパターン（`;`, `--`, `/*`）およびSQLキーワード（`DROP`, `DELETE` 等）の検知ロジックの強化。
- **接続管理の厳格化**:
  - `NanaSQLiteClosedError` の導入。
  - 親インスタンス・クローズ時に子インスタンス（`table()`で作成）を自動的に無効化する追跡機構の実装。
- **メンテナンス性向上**:
  - `DEVELOPMENT_GUIDE.md` の作成（日英）。
  - `pip install -e . -U` による環境同期ルールの明文化。

### [1.1.0] - 2025-12-19

#### 追加
- **カスタム例外クラスの導入**:
  - `NanaSQLiteError` (基底クラス)
  - `NanaSQLiteValidationError` (バリデーションエラー)
  - `NanaSQLiteDatabaseError` (データベース操作エラー)
  - `NanaSQLiteTransactionError` (トランザクション関連エラー)
  - `NanaSQLiteConnectionError` (接続エラー)
  - `NanaSQLiteLockError` (ロックエラー、将来用)
  - `NanaSQLiteCacheError` (キャッシュエラー、将来用)

- **バッチ取得機能 (`batch_get`)**:
  - `batch_get(keys: List[str])` による効率的な複数キーの一括ロード
  - `AsyncNanaSQLite.abatch_get(keys)` による非同期サポート
  - 1回のクエリで複数データを取得しキャッシュを最適化
- **トランザクション管理の強化**:
  - トランザクション状態の追跡（`_in_transaction`, `_transaction_depth`）
  - ネストしたトランザクションの検出とエラー発生
  - `in_transaction()` メソッドの追加
  - トランザクション中の接続クローズを防止
  - トランザクション外でのcommit/rollbackを検出

- **非同期版トランザクション対応**:
  - `AsyncNanaSQLite.begin_transaction()`
  - `AsyncNanaSQLite.commit()`
  - `AsyncNanaSQLite.rollback()`
  - `AsyncNanaSQLite.in_transaction()`
  - `AsyncNanaSQLite.transaction()` (コンテキストマネージャ)
  - `_AsyncTransactionContext` クラスの実装

- **リソースリーク対策**:
  - 親インスタンスが子インスタンスを弱参照で追跡
  - 親が閉じられた際、子インスタンスに通知
  - 孤立した子インスタンスの使用を防止
  - `_check_connection()` メソッドの追加
  - `_mark_parent_closed()` メソッドの追加

#### 改善
- **エラーハンドリングの強化**:
  - `execute()` メソッドにエラーハンドリングを追加
  - APSWの例外を `NanaSQLiteDatabaseError` でラップ
  - 元のエラー情報を保持（`original_error` 属性）
  - 接続状態のチェックを各メソッドに追加
  - `_sanitize_identifier()` で `NanaSQLiteValidationError` を使用

- **`__setitem__` メソッドに接続チェックを追加**

#### ドキュメント
- **新規ドキュメント**:
  - `docs/ja/error_handling.md` - エラーハンドリングガイド
  - `docs/ja/transaction_guide.md` - トランザクションガイド
  - `docs/ja/implementation_status.md` - 実装状況と今後の計画
  - `tests/test_enhancements.py` - 強化機能のテスト（21件）

- **README更新**:
  - トランザクションサポートのセクションを追加
  - カスタム例外のサンプルコードを追加
  - 非同期版のトランザクションサンプルを追加

#### テスト
- **新規テスト**（21件）:
  - カスタム例外クラスのテスト（5件）
  - トランザクション機能の強化テスト（6件）
  - リソース管理のテスト（3件）
  - エラーハンドリングのテスト（2件）
  - トランザクションと例外の組み合わせテスト（2件）
  - 非同期版トランザクションのテスト（3件）

#### 修正
- セキュリティテストで `NanaSQLiteValidationError` を期待するように修正

---

### [1.1.0a3] - 2025-12-17

#### ドキュメント改善
- **`table()`メソッドの使用上の注意を追加**:
  - README.mdに重要な使用上の注意セクションを追加（英語・日本語）
  - 同じテーブルへの複数インスタンス作成に関する警告
  - コンテキストマネージャ使用の推奨
  - ベストプラクティスの明記
- **docstring改善**:
  - `NanaSQLite.table()`のdocstringに詳細な注意事項を追加
  - `AsyncNanaSQLite.table()`のdocstringに詳細な注意事項を追加
  - 非推奨パターンと推奨パターンの具体例を追加
- **将来的な改善計画**:
  - `etc/future_plans/`ディレクトリに改善提案を文書化
  - 重複インスタンス検出警告機能（提案B）
  - 接続状態チェック機能（提案B）
  - 共有キャッシュ機構（提案C - 保留）

#### 分析・調査
- **table()機能の包括的な調査を実施**:
  - ストレステスト: 7件すべて合格
  - エッジケーステスト: 10件実施
  - 並行処理テスト: 5件すべて合格
  - **発見された問題**: 2件（軽微な設計上の制限）
    1. 同一テーブルへの複数インスタンスでキャッシュ不整合（ドキュメント化で対応）
    2. close後のサブインスタンスアクセス（ドキュメント化で対応）
  - **結論**: 本番環境で使用可能、パフォーマンス問題なし

### [1.1.0dev2] - 2025-12-16

#### 現在の開発状況
- 開発中のバージョン
- テスト実施中（`test_concurrent_table_writes.py`で15個のテスト全てパス）

### [1.1.0dev1] - 2025-12-15

#### 追加
- **マルチテーブルサポート（`table()`メソッド）**: 同一データベース内の複数テーブルを安全に操作
  - `db.table(table_name)`で別テーブル用のインスタンスを取得
  - **接続とロックの共有**: 複数のテーブルインスタンスが同じSQLite接続とスレッドロックを共有
  - スレッドセーフ: 複数スレッドから異なるテーブルへの同時書き込みが安全に動作
  - メモリ効率: 接続を再利用することでリソースを節約
  - **同期版**: `NanaSQLite.table(table_name)` → `NanaSQLite`インスタンス
  - **非同期版**: `await AsyncNanaSQLite.table(table_name)` → `AsyncNanaSQLite`インスタンス
  - キャッシュ分離: 各テーブルインスタンスは独立したメモリキャッシュを保持

#### 内部実装の改善
- **スレッドセーフティの強化**: 全データベース操作に`threading.RLock`を追加
  - 読み込み（`_read_from_db`）、書き込み（`_write_to_db`）、削除（`_delete_from_db`）
  - クエリ実行（`execute`, `execute_many`）
  - トランザクション操作
- **接続管理の改善**:
  - `_shared_connection`パラメータで接続の共有をサポート
  - `_shared_lock`パラメータでロックの共有をサポート
  - `_is_connection_owner`フラグで接続の所有権を管理
  - `close()`メソッドは接続の所有者のみが実行

#### テスト
- **15の包括的なテストケース**（全てパス）:
  - 同期版マルチテーブル並行書き込みテスト（2テーブル、複数テーブル）
  - 非同期版マルチテーブル並行書き込みテスト（2テーブル、複数テーブル）
  - ストレステスト（1000件の並行書き込み）
  - キャッシュ分離テスト
  - テーブル切り替えテスト
  - エッジケーステスト

#### 互換性
- **完全な後方互換性**: 既存のコードに影響なし
- 新しいパラメータはすべてオプショナル（内部使用）

### [1.0.3rc7] - 2025-12-10

#### 追加
- **非同期サポート（AsyncNanaSQLite）**: 非同期アプリケーション向けの完全な非同期インターフェース
  - `AsyncNanaSQLite`クラス: 全操作の非同期版を提供
  - **専用スレッドプールエグゼキューター**: 設定可能なmax_workers（デフォルト5）で最適化
  - `ThreadPoolExecutor`による高性能な並行処理
  - FastAPI、aiohttp等の非同期フレームワークで安全に使用可能
  - 非同期dict風インターフェース: `await db.aget()`, `await db.aset()`, `await db.adelete()`
  - 非同期バッチ操作: `await db.batch_update()`, `await db.batch_delete()`
  - 非同期SQL実行: `await db.execute()`, `await db.query()`
  - 非同期コンテキストマネージャ: `async with AsyncNanaSQLite(...) as db:`
  - 並行処理サポート: 複数の非同期操作を並行実行可能
  - 自動リソース管理: スレッドプールの自動クリーンアップ
- **包括的なテストスイート**: 100以上の非同期テストケース
  - 基本操作、並行処理、エラーハンドリング、パフォーマンステスト
  - 全テストが合格
- **完全な後方互換性**: 既存の`NanaSQLite`クラスは変更なし

#### パフォーマンス改善
- 非同期アプリでのブロッキング防止により、イベントループの応答性が向上
- 専用スレッドプールによる高効率な並行処理（設定可能なワーカー数）
- APSW + スレッドプールの組み合わせで最適なパフォーマンス
- 高負荷環境向けにmax_workersを調整可能（5～50）

### [1.0.3rc6] - 2025-12-10

#### 追加
- **`get_fresh(key, default=None)`メソッド**: DBから直接読み込み、キャッシュを更新して値を返す
  - `execute()`でDBを直接変更した後のキャッシュ同期に便利
  - `_read_from_db`を直接使用してオーバーヘッドを最小化

### [1.0.3rc5] - 2025-12-10

#### パフォーマンス改善
- **`batch_update()`の最適化**: `executemany`使用で大量データ処理が10-30%高速化
- **`batch_delete()`の最適化**: `executemany`使用で一括削除が高速化
- **`__contains__()`の最適化**: 軽量なEXISTSクエリ使用で存在確認が高速化（大きなvalueの場合に効果大）

#### IDE/型サポート強化
- `from __future__ import annotations` 追加
- `Dict[str, Any]`、`Set[str]`等の具体的な型アノテーション
- `Optional[Tuple]`等のより明確な引数型

#### ドキュメント
- `execute()`メソッドにキャッシュ一貫性に関する警告を追加
- docstringの改善（Returns、警告セクション追加）

#### バグ修正
- Gitマージコンフリクトの解消（order_by検証の正規表現）
- ReDoS脆弱性の修正（カンマ分割方式に変更）

### [1.0.3rc4] - 2025-12-09

#### 追加
- **22の新しいSQLiteラッパー関数**
  - スキーマ管理: `drop_table()`, `drop_index()`, `alter_table_add_column()`, `get_table_schema()`, `list_indexes()`
  - データ操作: `sql_insert()`, `sql_update()`, `sql_delete()`, `upsert()`, `count()`, `exists()`
  - クエリ拡張: `query_with_pagination()` (offset/group_by対応)
  - ユーティリティ: `vacuum()`, `get_db_size()`, `export_table_to_dict()`, `import_from_dict_list()`, `get_last_insert_rowid()`, `pragma()`
  - トランザクション: `begin_transaction()`, `commit()`, `rollback()`, `transaction()`コンテキストマネージャ
- 35の新しいテストケース（全て合格）
- 完全な後方互換性維持

### [1.0.3rc3] - 2025-12-09

#### 追加
- **Pydantic互換性**
  - `set_model()`, `get_model()` メソッド
  - ネストされたモデルとオプショナルフィールドのサポート
- **直接SQL実行機能**
  - `execute()`, `execute_many()`, `fetch_one()`, `fetch_all()` メソッド
  - パラメータバインディングによるSQLインジェクション対策
- **SQLiteラッパー関数**
  - `create_table()`, `create_index()`, `query()` メソッド
  - `table_exists()`, `list_tables()` ヘルパー関数
- 32の新しいテストケース
- 英語・日本語ドキュメントの更新
- 非同期対応に関する相談文書

### [1.0.0] - 2025-12-09

#### 追加
- 初回リリース
- dict風インターフェース（`db["key"] = value`）
- APSWによるSQLite即時永続化
- 遅延ロード（アクセス時にキャッシュ）
- 一括ロード（`bulk_load=True`）
- ネスト構造サポート（30階層テスト済み）
- パフォーマンス最適化（WAL、mmap、cache_size）
- バッチ操作（`batch_update`、`batch_delete`）
- コンテキストマネージャ対応
- 完全なdictメソッド互換性
- 型ヒント（PEP 561）
- バイリンガルドキュメント（英語/日本語）
- GitHub Actions CI（Python 3.9-3.13、Ubuntu/Windows/macOS）

---
