# etc/ ディレクトリ

NanaSQLiteの設計ドキュメント・改善計画を管理するディレクトリです。

ファイルは**実装状態**によって以下のサブディレクトリに分類しています。

---

## 📁 ディレクトリ構成

### ✅ implemented/ — 実装済み

すでにコードに反映済みの設計書・実装記録。

| ファイル | 内容 |
|---|---|
| `v1.3.0_cache_design.md` | v1.3.0 キャッシュ改善の設計書（`ExpiringDict`, `TTLCache`, `UnboundedCache` 等） |
| `implementation_status.md` | v1.1.0 で実装済みの改善一覧（例外クラス、トランザクション、リソースリーク対策 等） |

---

### 🔄 in_progress/ — 進行中

一部実装済み、または対応が認識・着手されているドキュメント。

| ファイル | 内容 |
|---|---|
| `roadmap_2025.md` | 2025年ロードマップ（フェーズ1=v1.2.0は完了、フェーズ2/3は継続中） |
| `copilot_review_recommendations.md` | Copilotレビューに基づく改善検討（v1.3.0/v2.0.0対象） |
| `refactor_query_dry.md` | `query`/`query_with_pagination` の重複排除リファクタリング（保留中） |

---

### 📋 planned/ — 計画中（未実装）

まだ実装されていない将来計画・提案書。

| ファイル | 内容 |
|---|---|
| `future_features_proposal.md` | ORM風モデル定義、マイグレーション機能等の提案 |
| `table_feature_improvements.md` | `table()` 機能の改善提案（提案B/C、重複インスタンス検出等） |
| `potential_issues_proposal.md` | 潜在的問題の分析・改善提案（v1.1.0a4時点の調査） |
