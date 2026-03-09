# NanaSQLite セキュリティ／性能監査レポート（2026-03-09）

速度と後方互換性を優先しつつ、現行リポジトリを対象に脆弱性と高速化余地を確認した結果をまとめます。

## 対象と方法

- 対象コード:
  - `src/nanasqlite/core.py`
  - `src/nanasqlite/async_core.py`
  - `src/nanasqlite/sql_utils.py`
  - `tests/test_security.py`
  - `tests/test_benchmark.py`
  - `etc/poc/poc_sqli.py`
  - `etc/poc/poc_none.py`
- 実施した確認:
  - `pip install -e ".[dev]"`
  - `python -m tox -e lint`
  - `python -m tox -e type`
  - `python -m pytest tests/ -x`
  - 既存 PoC の再実行

## 結論（要約）

1. **現行 HEAD で再現できる新規クリティカル脆弱性は確認できませんでした。**
2. 既知の重要問題である **`table` 引数経由の SQL injection** は、`NanaSQLite._sanitize_identifier()` により現行版ではブロックされます（`src/nanasqlite/core.py:341-377`）。
3. 既知の **`None` 値再読込時の整合性問題** は `_NOT_FOUND` センチネルで修正済みです（`src/nanasqlite/core.py:74-75`, `src/nanasqlite/core.py:631-655`, `src/nanasqlite/core.py:865-882`）。
4. 速度面では、**既存 API を壊さずに改善できる余地**がまだあります。特に `values()` / `items()` の全件ロード、`batch_get()` のキャッシュ確認、PRAGMA のまとめ実行は低リスクです（`src/nanasqlite/core.py:309-338`, `src/nanasqlite/core.py:825-929`）。

## PoC で確認した事項

### 1. `table` 引数経由の SQL injection（既知・修正済み）

- PoC: `etc/poc/poc_sqli.py`
- 関連コード:
  - `src/nanasqlite/core.py:143-151`
  - `src/nanasqlite/core.py:341-377`
  - `tests/test_security.py:95-102`

#### 再現コマンド

```bash
python etc/poc/poc_sqli.py
```

#### 現行版での確認結果

- 悪意あるテーブル名は `NanaSQLiteValidationError` で拒否される
- 既存の `users` テーブルは削除されない

#### 評価

- **深刻度（現行版）:** 修正済み
- **深刻度（未修正版の想定）:** Critical
- **後方互換性重視の推奨:** 現状維持で問題ありません。将来も識別子を受ける新 API は必ず `_sanitize_identifier()` を通してください。

### 2. `None` 値の再読込問題（既知・修正済み）

- PoC: `etc/poc/poc_none.py`
- 関連コード:
  - `src/nanasqlite/core.py:74-75`
  - `src/nanasqlite/core.py:631-655`
  - `src/nanasqlite/core.py:865-882`

#### 再現コマンド

```bash
python etc/poc/poc_none.py
```

#### 現行版での確認結果

- DB 再オープン後も `None` が正しく取得できる
- `KeyError` は発生しない

#### 評価

- **深刻度（現行版）:** 修正済み
- **性質:** データ整合性
- **後方互換性重視の推奨:** `_NOT_FOUND` センチネルの利用を継続し、呼び出し側では `is not _NOT_FOUND` 比較を維持してください。

## 現行版で見つかった「要監視」項目

ここからは **現時点で即時の破壊的変更を入れるより、まず運用ガイドと opt-in 強化で対処すべき項目** です。

### A. `backup()` / `restore()` のパスは呼び出し元の信頼境界に依存

- 関連コード: `src/nanasqlite/core.py:1222-1424`
- 現状:
  - 自己コピー防止 (`os.path.samefile`) はある
  - インメモリ DB 文字列の拒否もある
  - ただし、`dest_path` / `src_path` 自体は「アプリが信頼したパス」であることを前提にしている

#### リスク

ライブラリ単体の致命的欠陥というより、**アプリ側が未検証のユーザー入力をそのまま `backup()` / `restore()` に渡した場合の運用リスク** です。

#### 推奨対応

1. **最優先（非破壊）:** ドキュメントで「ユーザー入力を直接渡さない」ことを明記する
2. **次点（opt-in）:** `safe_base_dir` や `path_validator` のような追加引数で許可ディレクトリを制限する
3. **互換性優先:** 既定動作は変えず、厳格化は opt-in に留める

### B. `AsyncNanaSQLite` は高負荷時にスレッドプール待ち行列が伸び得る

- 関連コード: `src/nanasqlite/async_core.py:84-162`
- 現状:
  - `ThreadPoolExecutor(max_workers=...)` でワーカー数は制限される
  - ただし投入数自体の制御はなく、バースト時の待ち行列長は呼び出し側依存

#### リスク

可用性（availability）寄りの問題です。高負荷 API サーバーでは、急激な `await asyncio.gather(...)` 連打で遅延が増える余地があります。

#### 推奨対応

1. **最優先（非破壊）:** ドキュメントで `max_workers` の調整指針を明記する
2. **次点（opt-in）:** `max_pending_ops` または `asyncio.Semaphore` ベースの上限制御を追加する
3. **互換性優先:** デフォルト値は現状維持にして、必要な利用者だけが有効化できるようにする

### C. AEAD 暗号化は AAD なしでも安全だが、将来の文脈結合は改善余地あり

- 関連コード:
  - `src/nanasqlite/core.py:175-189`
  - `src/nanasqlite/core.py:618-623`
  - `src/nanasqlite/core.py:639-650`

#### 現状

`AES-GCM` / `ChaCha20Poly1305` は正しく使われていますが、AAD（Additional Authenticated Data）は `None` です。

#### 評価

これは **即時脆弱性というより、将来のフォーマット拡張を安全にするための改善余地** です。ここを今すぐ変えると既存 DB との互換性管理が必要になります。

#### 推奨対応

1. 互換性重視なら **いまは変更しない**
2. 将来やるなら、**バージョン付き暗号化フォーマット** を追加し、新フォーマットだけ AAD を使う
3. 旧フォーマット読み込みは残して後方互換性を守る

## 高速化の余地

### 1. `values()` / `items()` が常に `load_all()` を呼ぶ

- 関連コード: `src/nanasqlite/core.py:825-834`
- 影響:
  - 大規模 DB では全件メモリ展開コストが高い
  - 少量だけ見たいケースでも全件ロードになる

#### 推奨対応

- **後方互換性最優先:** 既存 `values()` / `items()` はそのままにする
- **追加 API で改善:** `iter_values()` / `iter_items()` のようなストリーミング API を追加する

### 2. `batch_get()` のキャッシュ確認は微小ながら改善余地あり

- 関連コード: `src/nanasqlite/core.py:884-929`
- 現状:
  - `self._cache.is_cached(key)` をキーごとに呼んでいる
- 推奨対応:
  - `CacheType.UNBOUNDED` では内部集合に直接当てる軽量分岐を入れる
- 期待効果:
  - 大量キー取得時の Python レベルのオーバーヘッド削減

### 3. `_apply_optimizations()` の PRAGMA はまとめ実行できる

- 関連コード: `src/nanasqlite/core.py:309-338`
- 推奨対応:
  - 複数の `cursor.execute(...)` をまとめて実行する
- 注意:
  - 効果は小さいため、まずは測定してから入れる

### 4. いちばん効果が大きいのは既存機能の活用

- `pip install "nanasqlite[speed]"` を使う（`pyproject.toml:44-75`）
- 書き込みは `batch_update()` を優先する（`docs/ja/guide/best_practices.md:46-68`）
- 小さな DB は `bulk_load=True`、大きな DB はデフォルトの遅延ロードを使い分ける（`docs/ja/guide/best_practices.md:16-45`）
- 既存ベンチマークは `tests/test_benchmark.py` に揃っている

## 優先順位つき推奨対応

### 優先度 P0: 今すぐやるべき（非破壊）

1. 現行の識別子サニタイズ実装を維持する
2. `backup()` / `restore()` に未検証パスを渡さないことを運用ガイドに含める
3. 高負荷 async 利用者向けに `max_workers` の調整指針を文書化する

### 優先度 P1: 小さく安全に改善できる項目

1. `iter_values()` / `iter_items()` のような追加 API
2. `batch_get()` の軽微なマイクロ最適化
3. PRAGMA のまとめ実行

### 優先度 P2: 互換性設計を伴うため、慎重に進める項目

1. `backup()` / `restore()` の opt-in パス制約
2. async キュー上限の opt-in 制御
3. AAD 付きの新しい暗号化フォーマット

## 参考資料

- セキュリティ回帰テスト: `tests/test_security.py`
- ベンチマーク: `tests/test_benchmark.py`
- 既知の修正済み問題: `SECURITY.md`
- PoC:
  - `etc/poc/poc_sqli.py`
  - `etc/poc/poc_none.py`
