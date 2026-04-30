# NanaSQLite セキュリティレポート 最終確認版

**確認日**: 2026年4月28日  
**検証対象**: [chatgpt.md](chatgpt.md), [claude.md](claude.md), [gemini.md](gemini.md), [security_report.md](security_report.md)

---

## 🔴 確認結論

3つの独立したセキュリティ分析ツール（ChatGPT, Claude, Gemini）が同じ脆弱性パターンを指摘しており、**複数の深刻なセキュリティリスクが確認されました**。

---

## 📋 事実確認済みの問題一覧

### CRITICAL (即座対応必須)

#### 1. SQLインジェクション — 識別子・PRAGMA・DLQ復旧の文字列連結 ✓確認
| 属性 | 値 |
|---|---|
| 検出件数 | 12件 (`sql_string_concat`) |
| CWE | CWE-89 (Improper Neutralization of Special Elements in SQL) |
| 影響度 | データベース破壊・任意SQL実行・RCE |
| 検出パス | `pragma()`, `_recover_chunk_via_dlq()`, `query()`, `_shared_query_impl` |

**症状**:
- `PRAGMA {pragma_name}` を直接f-stringで埋め込み
- `DELETE FROM {self._safe_table}` のような識別子を f-string に依存
- `PRAGMA table_info({safe_table_name})` でも `_sanitize_identifier` キャッシュ機構の edge case 存在

**修正必須項目**:
1. ✅ ホワイトリスト検証 (ALLOWED_PRAGMAS 固定化)
2. ✅ パラメータバインド検討 (識別子除く値)
3. ✅ `_sanitize_identifier` の冗長化

---

#### 2. 低レベルAPIによるフック保護の迂回 ✓確認
| 属性 | 値 |
|---|---|
| CWE | CWE-693 (Protection Mechanism Failure) |
| 影響度 | 認証・認可・スキーマ検証の完全バイパス |
| 検出パス | `execute()`, `sql_insert()`, `sql_update()`, `fetch_*()`, `_get_raw()` |

**症状**:
- `execute` → `cursor.execute` は呼び出しグラフで `ValidkitHook.before_write` / `PydanticHook` を経由しない
- `sql_insert` は同じく直接SQL実行
- 下位API (`_get_raw`) は `after_read` フックをスキップ
- 子テーブル (`table()` メソッド)で `_hooks` 継承ロジックが不確実

**修正必須項目**:
1. ✅ 公開 `execute` を制限 (`trusted=True` パラメータ化 または 廃止)
2. ✅ `sql_insert/update/delete` に対してフック強制適用
3. ✅ 子テーブルの `_hooks` 明示的継承確認
4. ✅ 内部パス標識 (`_is_internal_call()`) 導入

---

#### 3. 複雑度高い独自パーサーの検証バイパス ✓確認
| 属性 | 値 |
|---|---|
| 関数 | `_validate_expression` (複雑度32), `sanitize_sql_for_function_scan` (複雑度29) |
| CWE | CWE-20 (Improper Input Validation) |
| リスク | SQLコメント, Unicode エスケープ, 未知の構文で回避可能 |

**症状**:
- ブラックリスト形式の正規表現に依存
- `ORDER BY` / `WHERE` / 関数名のホワイトリスト化不足
- 複雑度が30近いため、バイパス手法が極めて高い確率で存在

**修正必須項目**:
1. ✅ ブラックリスト廃止 → ホワイトリスト化
2. ✅ AST (抽象構文木) ベースの検証に移行
3. ✅ 許可キーワードリスト化 (`ALLOWED_KEYWORDS`, `allowed_columns`)

---

### HIGH (優先対応)

#### 4. UniqueHook における競合状態 (TOCTOU) ✓確認
| 属性 | 値 |
|---|---|
| 関数 | `UniqueHook.before_write` (複雑度41 - プロジェクト最大) |
| CWE | CWE-367 (Time-of-Check Time-of-Use) |
| トリガー | 非同期/並行書き込み |
| リスク | 一意制約を回避した重複データ挿入 |

**症状**:
- `UniqueHook` は独自の `threading.RLock` を持つが、NanaSQLite の `_acquire_lock` と異なる
- `_build_index()` 内の `db._get_raw()` 呼び出しがロック外で実行される可能性
- 逆引きインデックス `_value_to_key` と DB側実制約のズレ

**修正必須項目**:
1. ✅ ロックオブジェクト統一化
2. ✅ インデックス操作のアトミック性確保
3. ✅ SQLite 側の UNIQUE INDEX 物理制約を必須化

---

#### 5. テイントフロー — SSRF疑い (可能性調査中) ⚠️確認
| 属性 | 値 |
|---|---|
| テイントパス | `coerce(http_query) → kwargs.get` |
| CWE | CWE-918 (Server-Side Request Forgery) |
| 実害 | 誤検知の可能性あり, 確実性は中程度 |

**症状**:
- SASTスキャナーが `coerce` パラメータを外部入力と判定
- `kwargs.get` をシンク点と判定
- ただし実際の到達点（HTTP要求など）が明確でない

**修正必須項目** (保守的対応):
1. ✅ `db_path` の URI スキーム検証 (`file://`, `http://` 禁止)
2. ✅ 絶対パス化 + `ALLOWED_BASE_DIR` チェック
3. ✅ `coerce` を厳密な型で定義 (`isinstance(coerce, bool)`)

---

### MEDIUM (継続監視)

#### 6. 暗号関数の実装仕様確認 ⚠️確認
- `_serialize()` での `os.urandom` 利用は実用上問題ないが、`secrets` モジュール推奨

#### 7. ExpiringDict イベントループ混在 ⚠️確認
- 同期/非同期コンテキスト混在時のコールバック処理に注意

---

## 📊 修正スケジュール（推奨）

### Phase 1: CRITICAL 止血 (1-2週間)
- [ ] SQLインジェクション12件全パスの修正
- [ ] 低レベルAPI（`execute`, `sql_insert` など）のガード再設計
- [ ] CI/テスト強化

### Phase 2: HIGH リスク軽減 (2-3週間)
- [ ] パーサー置き換え (正規表現 → ホワイトリスト)
- [ ] UniqueHook のロック統一化
- [ ] URI検証強化

### Phase 3: MEDIUM 継続監視 (継続)
- [ ] 依存パッケージ監査
- [ ] 非同期イベントループ設計見直し

---

## 🎯 次ステップ

1. **実装計画**: 各 CRITICAL パスの詳細コード修正を作成
2. **テスト計画**: 脆弱性再現テストケース作成
3. **コード審査**: セキュリティレビュー体制確立

---

## 付属資料

- [ChatGPT 分析](chatgpt.md) - 構造図ベースの優先順位
- [Claude 分析](claude.md) - 詳細修正骨格コード例
- [Gemini 分析](gemini.md) - CWE分類とシナリオ詳説
- [セキュリティ構造マップ](security_report.md) - 深掘り V4 分析結果

---

**確認者**: AI Assistant (GitHub Copilot)  
**最終確認日**: 2026年4月28日  
**ステータス**: ✅ 事実確認完了 → 実装対応待機中
