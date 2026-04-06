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
- `_cached_keys` は known-absent 判定に限定
- 公開API仕様（`KeyError` / `default` / `in` 判定）を維持

---

## 推奨対応優先度

| 優先度 | 内容 |
|---|---|
| リリース前に修正すべき | PERF-06（適用済み） |
| 次バージョンで対応可能 | `_cached_keys` 在/不在混在設計の分離検討 |
| 将来的な改善 | Unbounded モードの absent-only メタデータ化（破壊的変更評価含む） |
