# NanaSQLite 監査レポート生成プロンプト

> このファイルは AI に `audit.md` 形式の監査レポートを生成させ、  
> POC による検証・パッチ適用・テスト・リリース準備まで一貫して実行させるためのプロンプトテンプレートです。  
> リリース前の品質チェックに使用してください。

---

## 使い方

1. AI アシスタント（GitHub Copilot, Claude 等）のチャットにこのファイルの「プロンプト本文」セクションをコピー＆ペーストする
2. `{{VERSION}}` をリリース予定バージョンに置き換える
3. 必要に応じて対象ファイルやカテゴリを追加・変更する

---

## プロンプト本文

```
v{{VERSION}}リリース前に、以下のソースファイルすべてを精査し、監査→POC→修正→テスト→リリース準備の全フローを実行してください。

## フェーズ 1: 監査レポート作成

### 対象ファイル
- src/nanasqlite/core.py
- src/nanasqlite/async_core.py
- src/nanasqlite/cache.py
- src/nanasqlite/utils.py
- src/nanasqlite/sql_utils.py
- src/nanasqlite/exceptions.py
- その他 src/nanasqlite/配下のファイルすべて

### 調査カテゴリ（4 分類）
1. **不具合・潜在バグ** — レースコンディション、ロジックエラー、例外処理の抜け、リソースリーク、未処理のエッジケース、sentinel の誤用、off-by-one など
2. **高速化の余地** — 不要なメモリ確保、重複計算、非効率な SQL、インデックス不足、ロック競合、不要なシリアライズ/デシリアライズ、データ構造の最適化余地など
3. **改善点（コード品質）** — 型アノテーション不足、一貫性のないエラー処理、デッドコード、過度に複雑なロジック、docstring 不足、コード重複など
4. **脆弱性** — SQL インジェクション、パストラバーサル、安全でない暗号処理、タイミング攻撃、エラーメッセージからの情報漏洩、TOCTOU など

### レポート形式

**重要: `audit.md` は日本語で記述すること。**

#### ヘッダー
- タイトル: `# NanaSQLite v{{VERSION}} プレリリース監査レポート`
- 対象バージョン、監査日、対象ファイル一覧

#### 総括テーブル
カテゴリごとに Critical / High / Medium / Low / 計 の件数を表にまとめる。

#### 各発見事項のフォーマット
各項目は以下の構成にすること:

```markdown
### ID [重要度] タイトル

**ファイル:** `filename.py` L行番号

（該当コードの抜粋をコードブロックで示す）

問題の説明（なぜ問題なのか、どういう条件で発現するか）。

**修正案:** 具体的な修正方法を記載。
```

- **ID 命名規則**: `BUG-01`, `PERF-01`, `QUAL-01`, `SEC-01` のようにカテゴリ接頭辞＋連番
- **重要度**: Critical > High > Medium > Low

#### 推奨対応優先度セクション
最後に「リリース前に修正すべき」「次バージョンで対応可能」「将来的な改善」の 3 段階でテーブルを作成する。

### 注意事項
- 各項目には必ず正確なファイル名と行番号を付けること
- 後方互換性を壊す修正案は避け、互換性を維持した修正案を記載すること
- パフォーマンスに影響する修正案は、トレードオフを明記すること
- 既存テストで検出されていない問題に特に注目すること
- サイレントなデータ破損や暗号化迂回など「見えない」不具合を最優先で報告すること

---

## フェーズ 2: POC スクリプト作成

監査レポートの Critical / High / Medium (バグ・脆弱性) の各項目に対し、
`etc/poc/` ディレクトリに POC スクリプトを作成してください。

### POC 命名規則
- `poc_{id}_{短い説明}.py` (例: `poc_bug01_items_no_check.py`, `poc_sec01_column_type_injection.py`)

### POC の要件
1. **独立実行可能**: `python etc/poc/poc_xxx.py` で単体実行でき、PASS/BUG の結果を標準出力に表示すること
2. **パッチ適用前**: 修正前のコードで実行すると BUG (脆弱性再現) が確認できること
3. **パッチ適用後**: 修正後のコードで実行すると PASS (修正済み) が確認できること
4. **クリーンアップ**: 一時ファイル・DB を必ず後始末すること

### POC テンプレート
```python
\"\"\"
{ID} [{重要度}] {タイトル}

{問題の簡潔な説明}
修正後: {期待する動作}
\"\"\"

import os
import tempfile
from nanasqlite import NanaSQLite

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    # ... 再現手順 ...
    print("PASS: {期待する結果}")
except ExpectedException:
    print("PASS: {例外が正しく発生}")
except Exception as e:
    print(f"BUG: {予期しない動作}: {e}")
finally:
    os.unlink(path)
```

### POC 合格基準
- すべての POC スクリプトがパッチ適用後に PASS を出力すること
- `python etc/poc/poc_xxx.py` で個別実行して確認すること

---

## フェーズ 3: パッチ適用

監査レポートの指摘事項のうち、以下の条件を満たすものを修正してください:

1. **後方互換性を維持** すること
2. **パフォーマンスを劣化させない** こと
3. Critical / High の全項目、および修正が容易な Medium 項目

各パッチ適用後に:
- 対応する POC スクリプトが PASS することを確認
- 既存テスト（ベンチマークを除外して実行）が全パスすることを確認:
  ```bash
  python -m pytest tests/ -x --ignore=tests/test_benchmark.py --ignore=tests/test_async_benchmark.py --ignore=tests/test_cache_benchmark.py --ignore=tests/benchmark_encryption.py
  ```

---

## フェーズ 4: POC 検証テスト (pytest)

`tests/test_audit_poc.py` を作成し、すべての POC を pytest 形式に変換してください。

### テスト要件
1. 各 POC に対して 1 つ以上の pytest テストケースを作成
2. テストクラス名は `TestBug01...`, `TestSec01...` のように監査 ID に対応させる
3. 正常系・異常系の両方をテスト
4. `tmp_path` や `db_path` fixture を使い、一時ファイルを適切に管理
5. 非同期テストには `@pytest.mark.asyncio` を付与

### テスト合格基準
- `python -m pytest tests/test_audit_poc.py -v` で全テストが PASS すること
- ベンチマークを除外した全テストが PASS すること:
  ```bash
  python -m pytest tests/ -x --ignore=tests/test_benchmark.py --ignore=tests/test_async_benchmark.py --ignore=tests/test_cache_benchmark.py --ignore=tests/benchmark_encryption.py
  ```

---

## フェーズ 5: CI 検証

コミット前に以下の CI チェックすべてに合格すること:

### 必須チェック
1. **Ruff (リント)**: `python -m tox -e lint` でエラーなし
2. **mypy (型チェック)**: `python -m tox -e type` でエラーなし
3. **pytest (テスト)**: ベンチマークを除外して全テスト PASS
   ```bash
   python -m pytest tests/ -x --ignore=tests/test_benchmark.py --ignore=tests/test_async_benchmark.py --ignore=tests/test_cache_benchmark.py --ignore=tests/benchmark_encryption.py
   ```

### 確認手順
これらは `ci.yml` で定義されている CI ジョブと一致する:
- `lint` ジョブ → `python -m tox -e lint`
- `type` ジョブ → `python -m tox -e type`
- `test` ジョブ → `pytest tests/ ... --ignore=tests/test_benchmark.py ...`

---

## フェーズ 6: リリース準備

監査修正の適用後、以下のリリース関連ファイルを更新してください:

### 必須更新
1. **バージョン番号**: `src/nanasqlite/__init__.py` の `__version__` を `"{{VERSION}}"` に更新
2. **CHANGELOG.md**: 日本語・英語の両セクションに v{{VERSION}} エントリを追加
   - 修正した監査項目を箇条書きで列挙（ID・重要度・概要）
   - セキュリティ修正・バグ修正・パフォーマンス改善・コード品質改善のカテゴリで分類
3. **README.md**: 新機能やセキュリティ改善がある場合は該当セクションを更新
4. **ドキュメント** (`docs/en/`, `docs/ja/`): 必要に応じて API ドキュメントやガイドを更新

### 更新基準
- CHANGELOG は既存のフォーマット・スタイルに合わせること
- README の更新は新しい公開 API やセキュリティ強化がある場合のみ
- ドキュメントの更新は破壊的変更や新機能がある場合のみ
```

---

## カスタマイズ例

### 特定カテゴリのみ調査する場合

```
v{{VERSION}}リリース前に、src/nanasqlite/ 配下のすべてのファイルについて
**脆弱性** のみを精査し、上記フェーズ 1〜6 を実行してください。
```

### 新規追加ファイルがある場合

対象ファイルリストに新しいファイルを追加してください:
```
- src/nanasqlite/new_module.py
```

### 差分のみ調査する場合

```
前回の監査 (v{{PREV_VERSION}}) 以降に変更されたファイルのみを対象に
上記フェーズ 1〜6 を実行してください。
`git diff v{{PREV_VERSION}}..HEAD -- src/nanasqlite/` で変更範囲を特定してから
調査してください。
```
