# PySentinel 脆弱性チェックレポート 審議結果・対応提案書

**レポート日時:** 2026-04-11 19:49  
**対象スキャンツール:** PySentinel v3.2.0 (Gemini-flash-latest)  
**対象バージョン:** NanaSQLite v1.5.3  
**本書作成日:** 2026-04-11  
**対応完了バージョン:** NanaSQLite v1.5.4  

---

## 審議概要

PySentinel v3.2.0 が生成した AI コードレビューレポートの指摘事項（11 件）を、
現行ソースコードと照合して評価しました。

| 深刻度    | 指摘件数 | 評価後（対応不要/誤検知） | 評価後（対応要/検討）|
| --------- | -------- | ------------------------- | -------------------- |
| HIGH      | 4        | 1                         | 3                    |
| MEDIUM    | 5        | 1                         | 4                    |
| LOW       | 2        | 0                         | 2                    |
| **合計**  | **11**   | **2**                     | **9**                |

**即時修正対応（本 PR、v1.5.4）:** 3 件  
**ドキュメント・追加対応:** 3 件  
**誤検知（False Positive）:** 2 件  
**既知の制限（対応済みまたはドキュメント化済み）:** 2 件  
**次期対応推奨:** 4 件  

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
**✅ 本 PR（v1.5.4）で修正済み（SEC-05）**

`core.py` の `__setitem__` において `before_write` の呼び出しを `_acquire_lock()` の内側に移動しました。
`self._lock` は `threading.RLock` のためフック内の `db.items()` からの再入呼び出しでもデッドロックは発生しません。
一意性チェックと DB 書き込みがアトミックに実行されるため TOCTOU 競合は解消されます。

v2 モードでは非同期フラッシュ構造上、完全なアトミック化は困難です。
v2 モードで厳格な一意制約が必要な場合は SQLite UNIQUE 制約を推奨します。

---

### 2. VULN-001 ｜ AsyncNanaSQLite の共有キャッシュ スレッド安全性
**ファイル:** `async_core.py` L.110  
**報告深刻度:** HIGH  
**CWE:** CWE-362  

#### 評価
**誤検知（False Positive）**

`NanaSQLite` は `threading.RLock`（`self._lock`）でキャッシュへのすべてのアクセスを保護しています。
`AsyncNanaSQLite` が `ThreadPoolExecutor` に投入する同期操作もこの RLock を通じてシリアライズされます。

#### 推奨対応
現行の内部アーキテクチャに変更は不要。

---

### 3. VULN-002 ｜ ReDoS 保護の不完全さ（ブラックリスト方式）
**ファイル:** `hooks.py` L.40  
**報告深刻度:** MEDIUM  
**CWE:** CWE-1333  

#### 評価
**✅ 本 PR（v1.5.4）で強化済み（SEC-06 opt-in）**

`pip install nanasqlite[re2]` で `google-re2` をインストールすることで、
BaseHook のすべての正規表現処理が RE2 エンジン（線形時間計算量保証）を使用するようになります。
RE2 使用時は `nanasqlite.compat` ロガーへ `logging.info` でメッセージを出力します。
RE2 非インストール時は従来のブラックリスト検証が機能します。

---

### 4. VULN-002 ｜ テーブル識別子の SQL インジェクション
**ファイル:** `async_core.py` L.115  
**報告深刻度:** MEDIUM  
**CWE:** CWE-89  

#### 評価
**誤検知（False Positive）**

`core.py:213` で `_sanitize_identifier(table)` が確実に呼び出されており、
v1.3.4 で既に修正済みです。

---

### 5. VULN-003 ｜ UnboundedCache FIFO エビクションの競合条件
**ファイル:** `cache.py` L.105  
**報告深刻度:** HIGH  
**CWE:** CWE-362  

#### 評価
**設計上の保護あり（NanaSQLite 内部使用では実際のリスク限定的）**

NanaSQLite の外部の RLock が排他制御を担保。ただし、`UnboundedCache` をスタンドアロンで
並行使用する場合はリスクがあります。

#### 推奨対応（P1）
`UnboundedCache` 内部への自前ロック追加。

---

### 6. VULN-003 ｜ 手動 SQL パーサーの脆弱性
**ファイル:** `sql_utils.py` L.65  
**報告深刻度:** HIGH  
**CWE:** CWE-89  

#### 評価
**部分的に有効（Rust 実装が主要パス）**

`nanalib` が利用可能な場合はより堅牢な Rust 実装を使用します。
Python フォールバック実装の強化は P1 対応推奨。

---

### 7. VULN-004 ｜ メモリ枯渇による DoS（UnboundedCache）
**ファイル:** `cache.py` L.95  
**報告深刻度:** MEDIUM  
**CWE:** CWE-770  

#### 評価
**設計上のトレードオフ**

`CacheType.LRU` + `cache_size` を使用することで制限できます。
長期稼働サービスへの警告をドキュメントに追記することを P0 推奨。

---

### 8. VULN-004 ｜ ExpiringDict スケジューラの競合
**ファイル:** `utils.py` L.95  
**報告深刻度:** MEDIUM  
**CWE:** CWE-362  

#### 評価
**影響軽微（最大 1 秒の TTL 誤差）**

`sleep_time = min(first_expiry - now, 1.0)` により最大スリープ時間は 1 秒に制限。
セキュリティへの直接的影響なし。

---

### 9. VULN-005 ｜ 上限なし Dead Letter Queue (DLQ)
**ファイル:** `v2_engine.py` L.115  
**報告深刻度:** MEDIUM  
**CWE:** CWE-770  

#### 評価
**有効な指摘**

DLQ にサイズ上限がなく、高頻度エラー時にメモリが増大する可能性があります。

#### 推奨対応（P1）
`max_dlq_size` パラメータの追加（推奨デフォルト: 1000）。

---

### 10. VULN-005 ｜ compat.py の NoneType 呼び出しリスク
**ファイル:** `compat.py` L.29  
**報告深刻度:** LOW  

#### 評価
**✅ 本 PR（v1.5.4）で修正済み（QUAL-10）**

`validkit_validate = None` を `ImportError` を送出するダミー関数に変更しました。

---

### 11. VULN-006 ｜ デフォルトシリアライズの弱点
**ファイル:** `v2_engine.py` L.88  
**報告深刻度:** LOW  

#### 評価
**実際の影響は軽微（設計上の意図あり）**

`V2Engine` 直接利用向けドキュメント強化を P2 推奨。

---

## 総合評価・対応優先度

### 優先度 P0: 本 PR（v1.5.4）で完了

| # | 対象 | 内容 | 状態 |
|---|------|------|------|
| 1 | `core.py` + `hooks.py` | UniqueHook TOCTOU 修正（SEC-05）| ✅ 修正済み |
| 2 | `compat.py` + `hooks.py` | google-re2 opt-in（SEC-06）| ✅ 実施済み |
| 3 | `compat.py` | `validkit_validate = None` → ImportError スタブ（QUAL-10）| ✅ 修正済み |
| 4 | `SECURITY.md` / ドキュメント | SEC-05 修正内容を反映 | ✅ 更新済み |
| 5 | `SECURITY.md` / ドキュメント | テーブル識別子 SQL インジェクション（既存） | ✅ 対応済み |

### 優先度 P1: 次期リリースで対応推奨

| # | 対象 | 内容 |
|---|------|------|
| 1 | `v2_engine.py` | `max_dlq_size` パラメータ追加（推奨デフォルト: 1000） |
| 2 | `cache.py` | `UnboundedCache` 内部ロックの追加 |
| 3 | `docs/` | UnboundedCache の長期稼働リスクをドキュメントへ追記 |
| 4 | `sql_utils.py` | Python フォールバックのバックスラッシュエスケープテスト追加 |

### 優先度 P2: 中期的に検討

| # | 対象 | 内容 |
|---|------|------|
| 1 | `sql_utils.py` | `sqlparse` への移行検討（nanalib なし環境） |
| 2 | `v2_engine.py` | `V2Engine` の直接利用向け API ドキュメント強化 |

---

## 誤検知・対応不要項目のまとめ

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
- 本 PR の新規テスト: `tests/test_audit_poc.py` (`TestSec05UniqueHookTOCTOUFix`, `TestRE2Integration`)
- 変更履歴: `CHANGELOG.md` v1.5.4 セクション
