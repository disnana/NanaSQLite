# PySentinel 脆弱性チェックレポート 審議結果・対応提案書

**レポート日時:** 2026-04-11 19:49  
**対象スキャンツール:** PySentinel v3.2.0 (Gemini-flash-latest)  
**対象バージョン:** NanaSQLite v1.5.3  
**対象ディレクトリ:** `src/nanasqlite/`（10ファイル）  
**作成日:** 2026-04-11  

---

## 審議概要

PySentinel v3.2.0 が生成した AI コードレビューレポートの指摘事項（11 件）を、
現行ソースコードと照合して評価しました。

| 深刻度    | 指摘件数 | 評価後（対応不要/誤検知） | 評価後（対応要/検討）|
| --------- | -------- | ------------------------- | -------------------- |
| HIGH      | 4        | 2                         | 2                    |
| MEDIUM    | 5        | 2                         | 3                    |
| LOW       | 2        | 0                         | 2                    |
| **合計**  | **11**   | **4**                     | **7**                |

**即時修正対応:** 1 件（`compat.py` VULN-005）  
**ドキュメント・追加対応推奨:** 6 件  
**誤検知（False Positive）:** 2 件  
**既知の制限（対応済みまたはドキュメント化済み）:** 3 件  

---

## 指摘事項の詳細評価

### 1. VULN-001 ｜ UniqueHook の TOCTOU 競合条件
**ファイル:** `hooks.py` L.105  
**報告深刻度:** HIGH  
**CWE:** CWE-367  

#### 内容
`UniqueHook` は書き込み前にフィールドの一意性チェックを行うが、
チェックと書き込みの間に別スレッドが同じ値を書き込むことで
一意制約を回避できる（TOCTOU: Time-of-Check Time-of-Use 競合）。

#### 評価
**対応済み・既知の制限**

この問題は **v1.5.0 監査レポートで SEC-03 として既に認識・文書化** されており、
`UniqueHook` クラスの docstring に以下の警告が明記されています。

```
WARNING: This implementation has a known TOCTOU race condition in multi-threaded
environments. The uniqueness check occurs before the database write, creating
a race window where multiple threads can bypass the constraint.
```

#### 推奨対応（実装済み対応を含む）

- **現状維持 + ドキュメント強化（優先度: P0）:** ユーザー向けドキュメントで
  「厳密な一意制約が必要な場合は SQLite の UNIQUE 制約を使用すること」を明記。
- UniqueHook はアプリレベルの「ソフト制約」として位置付け、
  データベースレベルの保証が必要な場合は SQLite UNIQUE 制約の使用を推奨。

---

### 2. VULN-001 ｜ AsyncNanaSQLite の共有キャッシュ スレッド安全性
**ファイル:** `async_core.py` L.110  
**報告深刻度:** HIGH  
**CWE:** CWE-362  

#### 内容
`AsyncNanaSQLite` は `ThreadPoolExecutor` を使うが、内部の
`UnboundedCache` はスレッド安全でなく、高並行時にクラッシュする可能性がある。

#### 評価
**誤検知（False Positive）**

`NanaSQLite` は **`threading.RLock`（`self._lock`）でキャッシュへのすべてのアクセスを保護** しています。
`_acquire_lock()` コンテキストマネージャーを介してすべての読み書き・削除操作にロックが掛かっており、
`AsyncNanaSQLite` が `ThreadPoolExecutor` に投入する同期操作も
この RLock を通じてシリアライズされます（`core.py:428, 436`）。

`UnboundedCache` 自体に内部ロックはありませんが、NanaSQLite の設計上
**外側の RLock が排他制御を担保**しているため、実際のリスクは存在しません。

#### 推奨対応
- **将来の拡張時の注意事項:** キャッシュクラスを NanaSQLite の外側から
  直接使用するユースケースが発生した場合は、`UnboundedCache` 自体にスレッドロックを追加すること。
- 現行の内部アーキテクチャに変更は不要。

---

### 3. VULN-002 ｜ ReDoS 保護の不完全さ（ブラックリスト方式）
**ファイル:** `hooks.py` L.40  
**報告深刻度:** MEDIUM  
**CWE:** CWE-1333  

#### 内容
`_validate_regex_pattern` が危険な正規表現パターンを**ブラックリスト方式**で検出しているが、
ブラックリストは不完全であり、代替の壊滅的バックトラックパターンで回避できる可能性がある。

#### 評価
**部分的に有効な指摘**

現状の実装は 4 パターンのブラックリストで基本的な危険パターン（`(a+)+`, `(a*)*`, `(a|b)*`, `(a|b)+`）を
検出しており、既知の典型的な ReDoS パターンは防げます。
ただし、完全な保護にはホワイトリスト方式またはタイムアウト付きエンジンが必要です。

Python 標準の `re` モジュールにはタイムアウト機能がないため、
完全な対策には外部ライブラリが必要です。

#### 推奨対応（優先度順）

1. **P1: 入力長の制限（非破壊）**
   `key_pattern` 文字列の最大長を制限（例: 200 文字）して、
   複雑なパターン自体を受け付けないようにする。
2. **P2: RE2 エンジンへの移行（opt-in）**
   `google-re2`（線形時間計算量保証）をオプション依存として追加し、
   インストール済みの場合に使用する。
3. **P3: パターンのホワイトリスト化**
   アプリ側でユーザー入力からの正規表現を受け付けない設計を推奨として文書化。

---

### 4. VULN-002 ｜ テーブル識別子の SQL インジェクション
**ファイル:** `async_core.py` L.115  
**報告深刻度:** MEDIUM  
**CWE:** CWE-89  

#### 内容
`table` パラメータが適切に検証されずに SQL へ展開される可能性がある。

#### 評価
**誤検知（False Positive）**

`core.py:213` で `_sanitize_identifier(table)` が **確実に呼び出されており**、
IDENTIFIER_PATTERN（`^[a-zA-Z_]\w*$`）に一致しない識別子は
`NanaSQLiteValidationError` として拒否されます。
この問題は **v1.3.4 で修正済み** であり、`SECURITY.md` にも記載されています。

#### 推奨対応
- 現行実装の維持。追加変更は不要。

---

### 5. VULN-003 ｜ UnboundedCache FIFO エビクションの競合条件
**ファイル:** `cache.py` L.105  
**報告深刻度:** HIGH  
**CWE:** CWE-362  

#### 内容
`UnboundedCache.set()` において `len(self._data) >= self._max_size` のチェックと
`next(iter(self._data))` の操作がアトミックでなく、マルチスレッドで競合が起きる可能性がある。

#### 評価
**設計上の保護あり（実際のリスクは限定的）**

[2. VULN-001 async_core.py] と同じく、`UnboundedCache` へのすべての呼び出しは
`NanaSQLite._lock`（RLock）によって保護されており、同時アクセスは発生しません。
したがって、NanaSQLite の通常使用では実際のリスクはありません。

ただし、`UnboundedCache` を NanaSQLite 外部から直接かつ並行的に使用する場合は
競合が発生し得ます。

#### 推奨対応
- **P1: キャッシュクラスへの内部ロック追加（将来の保護強化）**
  `UnboundedCache.set()` の FIFO エビクションブロックを内部ロックで保護することで、
  キャッシュクラスをスタンドアロンでも安全に使用できるようにする。

```python
# 推奨修正例（cache.py）
def set(self, key: str, value: Any) -> None:
    with self._lock:  # 内部ロックを追加
        if self._max_size and self._max_size > 0:
            if key not in self._data and len(self._data) >= self._max_size:
                oldest_key = next(iter(self._data))
                del self._data[oldest_key]
                self._cached_keys.discard(oldest_key)
        self._data[key] = value
        self._cached_keys.add(key)
```

---

### 6. VULN-003 ｜ 手動 SQL パーサーの脆弱性
**ファイル:** `sql_utils.py` L.65  
**報告深刻度:** HIGH  
**CWE:** CWE-89  

#### 内容
`sanitize_sql_for_function_scan()` が手動ステートマシンで SQL を解析しており、
方言固有のエスケープ処理の漏れで悪意のある内容が文字列リテラル内に隠蔽される可能性がある。

#### 評価
**部分的に有効な指摘（実装済みの軽減措置あり）**

現在の `sql_utils.py` は以下の軽減措置を実装しています。

1. **Rust 実装（nanalib）が主要パス:** `nanalib` が利用可能な場合（デフォルト）は
   Python の手動ステートマシンではなく Rust 実装を使用します。
   Rust 実装はより堅牢で型安全です。
2. **フォールバックとしての Python 実装:** `nanalib` が利用できない環境でのみ
   Python 実装が使われます。

ただし、Python フォールバック実装における
バックスラッシュエスケープ（`\'`）や非標準コメントスタイルへの対応は
確認が必要です。

#### 推奨対応

1. **P1: Python フォールバック実装の強化**
   `sanitize_sql_for_function_scan()` に対して、
   バックスラッシュエスケープやドル引用符（`$$...$$`）など
   非標準エスケープのテストケースを追加する。
2. **P2: `sqlparse` ライブラリの導入検討**
   nanalib なし環境での Python フォールバックを
   `sqlparse` ライブラリへ置き換えることで、パーサーの信頼性を高める。

---

### 7. VULN-004 ｜ メモリ枯渇による DoS（UnboundedCache）
**ファイル:** `cache.py` L.95  
**報告深刻度:** MEDIUM  
**CWE:** CWE-770  

#### 内容
`UnboundedCache` のデフォルト `max_size=None` は上限なし増大を許し、
長期稼働アプリケーションで OOM（Out-of-Memory）を引き起こす可能性がある。

#### 評価
**有効な指摘（設計上のトレードオフ）**

`UnboundedCache` は名称の通り「無制限成長・最高速度」を目的としたキャッシュ戦略です。
ユーザーは `cache_strategy=CacheType.LRU` と `cache_size` を組み合わせることで
サイズ制限を設定できます。

ただし、長期稼働サービスにおけるリスクをドキュメントで明示することは重要です。

#### 推奨対応

1. **P0: ドキュメントへの警告追加**
   `UnboundedCache`（`CacheType.UNBOUNDED`）を使用する際の
   長期稼働リスクをガイドと API ドキュメントに明記する。
2. **P1: ベストプラクティスの強化**
   長期稼働アプリケーションでは `CacheType.LRU` + `cache_size` を推奨する
   記述をベストプラクティスガイドに追加する。

---

### 8. VULN-004 ｜ ExpiringDict スケジューラの競合
**ファイル:** `utils.py` L.95  
**報告深刻度:** MEDIUM  
**CWE:** CWE-362  

#### 内容
SCHEDULER モードのスケジューラループが最初の失効時刻に基づいてスリープするが、
スリープ中により短い TTL のアイテムが追加されても即座に再チェックしない。

#### 評価
**有効だが影響は軽微**

`sleep_time = min(first_expiry - now, 1.0)` により
**最大スリープ時間は 1 秒に制限** されています。
そのため、新しいアイテムが追加されても最大 1 秒の追加遅延が発生するにとどまります。
これはキャッシュの失効精度に関する軽微な問題であり、セキュリティへの直接的影響はありません。

#### 推奨対応

より短い TTL のアイテムが挿入されたとき、スケジューラスレッドに通知する改善が可能ですが、
実装の複雑さを増すため、現時点では対応不要と判断します。
将来的には `_stop_event` を `wakeup_event` と `stop_event` に分離して対応できます。

---

### 9. VULN-005 ｜ 上限なし Dead Letter Queue (DLQ)
**ファイル:** `v2_engine.py` L.115  
**報告深刻度:** MEDIUM  
**CWE:** CWE-770  

#### 内容
`V2Engine` の DLQ（`self.dlq`）にサイズ制限がなく、
高頻度エラー時にメモリが無制限に増大する可能性がある。

#### 評価
**有効な指摘**

現在の実装：
```python
self.dlq: list[tuple[str, Any, float]] = []
```
DLQ は `_add_to_dlq()` で追加、`get_dlq()` / `retry_dlq()` / `clear_dlq()` で管理されますが、
サイズ上限は設定されていません。
「ポイズンピル」タスクが継続的に失敗する場合、メモリが増大します。

#### 推奨対応

**P1: `max_dlq_size` パラメータの追加**

`V2Engine.__init__` に `max_dlq_size: int = 1000` パラメータを追加し、
DLQ が上限に達した場合は最古のエントリを削除（または警告ログを出力）する。

```python
# 推奨修正例（v2_engine.py）
def _add_to_dlq(self, error_msg: str, item: Any) -> None:
    """Adds a failed item to the Dead Letter Queue."""
    with self._dlq_lock:
        self.dlq.append((error_msg, item, time.time()))
        # DLQ サイズ上限: 古いエントリから削除
        if self._max_dlq_size and len(self.dlq) > self._max_dlq_size:
            dropped = self.dlq.pop(0)
            logger.warning("DLQ size exceeded %d; dropped oldest entry: %s", self._max_dlq_size, dropped[0])
    if self._enable_metrics:
        with self._metrics_lock:
            self._metrics["dlq_errors"] += 1
    logger.error("NanaSQLite DLQ Entry: %s", error_msg)
```

---

### 10. VULN-005 ｜ compat.py の NoneType 呼び出しリスク
**ファイル:** `compat.py` L.29  
**報告深刻度:** LOW  

#### 内容
`validkit` がインストールされていない場合、`validkit_validate = None` となり、
他のモジュールが `HAS_VALIDKIT` を確認せずに呼び出すと `TypeError` が発生する。

#### 評価
**有効な指摘**

実際のコードでは `HAS_VALIDKIT` フラグのチェックを通じて保護されていますが、
`None` を関数として呼び出すと `TypeError: 'NoneType' object is not callable` となり、
エラーメッセージが分かりにくいという問題があります。

#### 対応
**✅ 本 PR にて修正済み（`compat.py`）**

`validkit_validate = None` を適切なダミー関数に変更し、
`validkit-py` 未インストール時に明確な `ImportError` を送出するよう修正しました。

```python
# 修正後（compat.py）
def validkit_validate(*args: Any, **kwargs: Any) -> None:
    """Stub raised when validkit-py is not installed."""
    raise ImportError(
        "validkit-py is not installed. "
        "Install it with: pip install nanasqlite[validkit]"
    )
```

---

### 11. VULN-006 ｜ デフォルトシリアライズの弱点
**ファイル:** `v2_engine.py` L.88  
**報告深刻度:** LOW  

#### 内容
`V2Engine` のデフォルトシリアライズ関数が `str` であり、
複雑な Python オブジェクトが正しくシリアライズされない可能性がある。

#### 評価
**実際の影響は軽微（設計上の意図あり）**

`V2Engine` は `NanaSQLite` から使われる際、
`core.py` が適切なシリアライズ関数（JSON/orjson/暗号化付き）を注入します（`core.py:483` 付近）。
`str` フォールバックは `V2Engine` を直接・単独で使用する上級者向けのデフォルトです。

ただし、ライブラリの外部 API としてドキュメントが不十分である点は改善余地があります。

#### 推奨対応

**P2: ドキュメント強化**
`V2Engine` を直接使用する際はシリアライズ関数の明示的な指定を推奨する記述を API ドキュメントに追加する。

---

## 総合評価・対応優先度

### 優先度 P0: 即時対応（完了済みまたは本 PR で実施）

| # | 対象 | 内容 | 状態 |
|---|------|------|------|
| 1 | `compat.py` VULN-005 | `validkit_validate = None` をダミー関数に変更 | ✅ 本 PR で修正済み |
| 2 | `SECURITY.md` / ドキュメント | UniqueHook の TOCTOU 制限を明記（既存） | ✅ 対応済み |
| 3 | `SECURITY.md` / ドキュメント | テーブル識別子 SQL インジェクション（既存） | ✅ 対応済み |

### 優先度 P1: 次期リリースで対応推奨

| # | 対象 | 内容 |
|---|------|------|
| 1 | `v2_engine.py` VULN-005 | `max_dlq_size` パラメータ追加（推奨デフォルト: 1000） |
| 2 | `cache.py` VULN-003 | `UnboundedCache` 内部ロックの追加（スタンドアロン利用の安全化） |
| 3 | `docs/` | UnboundedCache の長期稼働リスクをドキュメントへ追記 |
| 4 | `sql_utils.py` VULN-003 | Python フォールバックのバックスラッシュエスケープテスト追加 |

### 優先度 P2: 中期的に検討

| # | 対象 | 内容 |
|---|------|------|
| 1 | `hooks.py` VULN-002 | ReDoS 保護の強化（入力長制限 or google-re2 導入） |
| 2 | `sql_utils.py` VULN-003 | `sqlparse` への移行検討（nanalib なし環境） |
| 3 | `v2_engine.py` VULN-006 | `V2Engine` の直接利用向け API ドキュメント強化 |

---

## 誤検知・対応不要項目のまとめ

以下の指摘は現行実装により既に対応済みです。

| 指摘 ID | ファイル | 判定 | 理由 |
|---------|---------|------|------|
| VULN-001 | `async_core.py` | 誤検知 | `NanaSQLite._lock`（RLock）によりすべてのキャッシュアクセスが保護済み |
| VULN-002 | `async_core.py` | 誤検知 | `_sanitize_identifier()` が `core.py:213` で確実に呼び出されている（v1.3.4 修正済み） |

---

## 参考資料

- PySentinel レポート: `pysentinel-report-20260411_194959.html`
- 既知の修正済み問題: `SECURITY.md`
- 過去のセキュリティ監査: `docs/ja/guide/security_audit.md`
- セキュリティ回帰テスト: `tests/test_security.py`
- hooks の既知制限（SEC-03/SEC-04）: `src/nanasqlite/hooks.py:101-154`（UniqueHook docstring）
