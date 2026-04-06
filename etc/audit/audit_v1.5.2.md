# NanaSQLite v1.5.2 プレリリース監査レポート

**対象バージョン:** v1.5.2  
**監査日:** 2026-04-06  
**監査対象ファイル（差分中心）:**
- `src/nanasqlite/core.py`
- `tests/test_v152_perf_fastpath.py`
- `docs/ja/guide/performance.md`
- `docs/en/guide/performance.md`
- `CHANGELOG.md`

---

## 総括テーブル

| カテゴリ | Critical | High | Medium | Low | 計 |
|---------|----------|------|--------|-----|-----|
| バグ / 潜在バグ (BUG) | 0 | 0 | 0 | 0 | 0 |
| パフォーマンス (PERF) | 0 | 1 | 0 | 0 | 1 |
| コード品質 (QUAL) | 0 | 0 | 0 | 0 | 0 |
| セキュリティ (SEC) | 0 | 0 | 0 | 0 | 0 |
| **合計** | **0** | **1** | **0** | **0** | **1** |

---

## 発見事項

### PERF-06 [High] Unbounded キャッシュ read hot-path の分岐コスト

**ファイル:** `src/nanasqlite/core.py`（`_ensure_cached`, `__getitem__`, `get`, `__contains__`）

v1.5.1 時点でも、Unbounded モードで `_cached_keys` 先行判定が残っており、正のキャッシュヒット時にも追加の membership 判定が必要でした。  
`_cached_keys` は在/不在状態を同じ集合で保持するため、可読性・分岐効率の両面で read hot-path 最適化の障害になっていました。

**修正案（適用済み）:**
- `_data` を最優先 fast-path として確認
- known-absent 専用セット `_absent_keys` を導入（`_cached_keys` 依存を排除）
- 公開API仕様（`KeyError` / `default` / `in` 判定）を維持

---

## audit_prompt.md 準拠チェック（差分対象）

- フェーズ1（監査）: 本レポートを更新（日本語）
- フェーズ2（POC）: 今回は既存バグ/脆弱性再現ではなく設計変更のため新規POC不要
- フェーズ3（パッチ）: `core.py` に破壊的変更（内部属性）を適用
- フェーズ4（pytest）: `tests/test_v152_perf_fastpath.py` を更新し回帰確認
- フェーズ5（CI相当）: lint/type/pytest（ベンチ除外）を実施予定
- フェーズ6（リリース準備）: v1.5.2 向け changelog/docs を破壊的変更内容に合わせて更新

---

## 追加の徹底調査（review follow-up）

レビュー指摘に基づき、`_absent_keys` 導入後の全 delete 系経路を再監査したところ、以下を確認:

- `pop()` の v1 経路で `_cache.delete()` のみ実行し、Unbounded の known-absent メタデータ更新が抜けるケースがあった
- `batch_delete()` の v1 経路でも同様に `_cache.delete()` のみで `_absent_keys` 更新が不足していた
- `batch_get()` の DB miss 後 mark 経路は Unbounded では `_absent_keys` に直接反映したほうが実装意図と整合する

**適用済み改善:**
- `pop()` v1 経路: `_data.pop()` + `_absent_keys.add()` を追加
- `batch_delete()` v1 経路: 各 key で `_data.pop()` + `_absent_keys.add()` を追加
- `batch_get()` DB miss 後: Unbounded では `_absent_keys` に記録（LRU/TTL は既存の `mark_cached()` 維持）

**結果:**
- 公開 API の意味は不変
- `_absent_keys` 設計への内部整合性が向上
- 追加テストで delete 系の一貫性を固定

### 追加改善（2nd follow-up）

さらにレビュー指摘を踏まえ、Unbounded モードでの delete 系キャッシュ更新を再精査し、以下を適用:

- `__delitem__` / `pop` / `batch_delete` の Unbounded 経路で `self._cache.delete()` を呼ばないよう整理
  - 理由: Unbounded では `_data` + `_absent_keys` が実質の内部メタデータであり、`self._cache.delete()`（UnboundedCache.delete）は `_cached_keys` 更新を伴って冗長
  - 対応: Unbounded は `self._data.pop(key, None)` + `self._absent_keys.add(key)` の単一路線へ統一
- CodeQL 指摘（assert side-effect）への予防対応
  - テストの `assert db.pop(...) == ...` を 2段階（代入→assert）へ変更

**期待効果:**
- Unbounded delete hot-path の不要処理を削減
- `_cached_keys` 依存残骸の縮小
- セキュリティスキャン観点（assert side-effect）への整合

---

## 推奨対応優先度

| 優先度 | 内容 |
|---|---|
| リリース前に修正すべき | PERF-06（適用済み） |
| 次バージョンで対応可能 | `_cached_keys` 在/不在混在設計の分離検討 |
| 将来的な改善 | Unbounded モードの absent-only メタデータ化（破壊的変更評価含む） |
