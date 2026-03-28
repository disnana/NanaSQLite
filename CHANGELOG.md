# 変更履歴 / Changelog

[日本語](#日本語) | [English](#english)

---

## 日本語

### [1.5.0dev2] - 2026-03-28

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

### [1.4.1] - 2026-03-27

#### セキュリティ修正
- QUAL-07 [High] 同期版 `NanaSQLite` クラスに V2 エンジンの管理メソッドを追加し、完全な機能パリティを実現しました。
- CORE [Critical] `clear()`、`load_all()`、`restore()` メソッドにおける V2 エンジンの整合性を強化し、データの不整合や「幽霊書き込み」を防止しました。
- SEC-01/02 [Critical] `column_type` バリデーションに ReDoS 対策を施したホワイトリスト方式を導入し、セキュリティを強化しました。
- CONC-01/02 [High] V2 エンジンと `ExpiringDict` におけるマルチスレッド実行時のレースコンディションおよびデッドロックを修正しました。
- **[Critical] PERF-02**: `table()` メソッドで作成された子インスタンスが親の `V2Engine` を共有するように改善。これにより、テーブルごとにスレッドや `atexit` ハンドラが生成されるリソースリーク（およびプロセス終了時のハングアップ）を解消しました。
- **[Critical] DEADLOCK-01**: `V2Engine` において `StrictTask` の処理中にデッドロックが発生し、`pytest` 等の並列実行中にプロセスがハングアップする問題を修正しました。タスク処理のトランザクション分離と、`shutdown` 時の確実なイベント解放を実装しました。
- **[Critical] MULTI-TENANT-01**: `V2Engine` が単一のテーブル名に依存していた不具合を修正。複数のテーブルインスタンスが一つのエンジンを共有しても、データが混同されないマルチテナント（テーブル単位の分離）に対応しました。
- **[High] QUAL-08**: `V2Engine.shutdown()` の堅牢性を強化。二重実行の防止、`atexit` ハンドラの確実な解除、およびシャットダウン時のフラッシュ処理の安全性を向上させました。
- QUAL-05 [Medium] V2 モードでの明示的な `begin_transaction()` 呼び出しに対するガードを追加し、バックグラウンドフラッシュとの衝突を防止しました。
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
- **[High] QUAL-07**: 同期版 `NanaSQLite` にも V2 管理メソッドを追加し、非同期版との完全な機能パリティを実現。
- **[High] QUAL-05**: V2モードにおいて `begin_transaction()` 等の明示的なトランザクション操作を行うと V2 エンジンのバックグラウンド処理と衝突するため、V2モード時は明示的なトランザクションを禁止（例外送出）するようにガードを追加しました。
- **[High] QUAL-06**: `AsyncNanaSQLite.table()` において `v2_enable_metrics` 設定が子インスタンスに継承されない不具合を修正しました。
- **[Medium] SEC-01 (強化)**: `create_table()` のカラム型バリデーションをブラックリスト方式からホワイトリスト方式（正規表現による記号制限）へ移行し、検知パターンを強化しました。

#### パフォーマンス改善
- **[Low] PERF-01**: LRU および TTL キャッシュ戦略において、データベースに存在しないキーの検索結果を記憶する「ネガティブキャッシュ」を導入し、繰り返しアクセス時の I/O 負荷を削減しました。（同時に、本機能によってセンチネルが混入する破壊的バグを早期発見し修正済みです）（1.4.1rc1）

#### コード品質改善
- **[Low] QUAL-01**: `ExpiringDict` のスケジューラスレッド停止処理を改善し、インスタンス破棄時やクリア時のクリーンアップをより堅牢にしました。（1.4.1rc1）
- **[Low] QUAL-03**: ソースコード内のマジックリテラル（`"BEGIN IMMEDIATE"` 等）の共通定数化を行い、保守性を向上させました。
- **[Low] CI-01**: SonarQube Cloud の「Quality Gate」における誤検知（ドキュメントやスクリプトがカバレッジに含まれる問題）を解消し、認知複雑度などの非本質的な警告を抑制する設定を導入しました。
- **[Low] QUAL-09**: `utils.py` の `list(dict.keys())` を `list(dict)` に変更し、不要な `.keys()` 呼び出しを削除しました（SonarCloud指摘対応）。
- **[Low] QUAL-10 (新機能)**: `V2Config` データクラスを追加し、v2関連パラメータ（`flush_mode`, `flush_interval`, `flush_count`, `chunk_size`, `enable_metrics`）をひとまとめにして渡せるようにしました。既存の個別引数は後方互換のためすべて維持されます。SonarCloud の「パラメータが多すぎる（brain-overload）」警告への対応です。
  ```python
  from nanasqlite import NanaSQLite, V2Config
  cfg = V2Config(flush_mode="time", flush_interval=5.0, enable_metrics=True)
  db = NanaSQLite("mydata.db", v2_mode=True, v2_config=cfg)
  ```
- **[Low] CI-02**: `bench-rpi.yml` において、`docker run` 実行前に `docker rm -f` を追加し、キャンセル後の再実行時にコンテナ名が競合するエラー（`"Conflict. The container name is already in use"`）を解消しました。


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


## English

### [1.5.0dev2] - 2026-03-28

#### Packaging and IDE Support Improvements
- **[High] PEP 561 Compliance and Autocompletion Fix**:
  - Refactored `tool.setuptools` in `pyproject.toml` to use standard `src-layout` auto-discovery. Fixed the issue where IntelliSense/autocompletion failed for the PyPI distribution.
  - Enabled `include-package-data = true` and added `MANIFEST.in` to ensure the `py.typed` file is correctly bundled in both wheel (.whl) and source distributions (sdist).
  - This enables full autocompletion support for `NanaSQLite`, `PydanticHook`, and other exports in major IDEs like VS Code (Pylance) and PyCharm out of the box.

### [1.5.0dev1] - 2026-03-28

#### Improvements from Release Audit
- **[Critical] BUG-01**: Fixed a bug where `batch_update`, `batch_update_partial`, and `batch_delete` methods bypassed V2 mode and performed direct database writes. Routed these operations through the V2 engine's staging buffer to ensure data integrity and FIFO order.
- **[Critical] BUG-02**: Resolved "Ghost Re-inserts" in `clear()` and `load_all()` methods, where database operations executed before the V2 engine's background `flush()` completed. Introduced synchronous waiting via `flush(wait=True)`.
- **[High] QUAL-01**: Refactored `AsyncNanaSQLite.add_hook()` implementation to harden hook registration logic before and after base database initialization, improving stability in asynchronous environments.
- **[Non-Breaking] API Extension**: Added a `wait` parameter to `flush()` (sync) and `aflush()` (async) methods, allowing for synchronous waiting of background worker completion.
- **[High] Full Restoration of Python 3.9 Compatibility**:
  - Added `from __future__ import annotations` to all source files, allowing Python 3.10+ `|` (Union) operators in type hints to function correctly on Python 3.9.
  - Introduced an `EllipsisType` compatibility layer in `compat.py` to ensure stable `mypy` static analysis and runtime type validation on Python 3.9.
  - Updated `pyproject.toml` to target `mypy` for Python 3.9, guaranteeing continuous compatibility.

#### New Features: Ultimate Hooks (General-purpose Hook & Constraint Architecture)
- **Powerful Hook Mechanism**:
  - Introduced the `NanaHook` protocol, allowing interception of 3 lifecycle events: `before_write`, `after_read`, and `before_delete`.
  - Custom hooks can be easily authored to implement data validation, custom encryption, logging, or integrations with external systems.
- **Built-in Standard Constraints**:
  - `CheckHook`: Provides function-based validation similar to SQLite's `CHECK` constraint.
  - `UniqueHook`: Ensures uniqueness of values for a specified key (or nested field).
  - `ForeignKeyHook`: Grants referential integrity against keys in other `NanaSQLite` tables.
- **Transparent External Library Integrations**:
  - `ValidkitHook`: Maintains 100% backward compatibility with the legacy `validator` parameter, providing high-performance validation via `validkit-py`.
  - `PydanticHook`: Allows direct registration of `Pydantic` models as hooks, enabling automatic serialization/deserialization and strict type validation on read/write.
- **Method Extensions**:
  - Added `NanaSQLite.add_hook()` and `AsyncNanaSQLite.add_hook()` for dynamic hook registration.

#### Architectural Enhancements & Backward Compatibility
- The legacy `validator` parameter is internally converted to a `ValidkitHook`, preserving 100% backward compatibility.
- Internal logic has been unified and hardened to ensure hooks are equally applied across all access paths, including `batch_update`, `get`, `batch_get`, `setdefault`, and `pop`.

### [1.4.1] - 2026-03-27

#### Security Fixes
- **QUAL-07 [High]**: Added V2 engine management methods to the synchronous `NanaSQLite` class, achieving full feature parity between sync and async versions.
- **CORE [Critical]**: Hardened V2 engine consistency in `clear()`, `load_all()`, and `restore()` methods to prevent data desynchronization and "ghost writes" during state transitions.
- **SEC-01/02 [Critical]**: Introduced whitelist-based validation for `column_type` with ReDoS-safe patterns, enhancing protection against SQL injection and denial-of-service.
- **CONC-01/02 [High]**: Fixed race conditions and deadlocks in the V2 engine and `ExpiringDict` during multi-threaded execution.
- **[Critical] PERF-02**: Improved `table()` method to share the parent's `V2Engine` instance. This resolves resource leaks (thread and `atexit` handler accumulation) that caused hangs during process exit.
- **[Critical] DEADLOCK-01**: Resolved deadlocks in `V2Engine` during `StrictTask` processing that caused processes to hang during parallel execution (e.g., `pytest-xdist`). Implemented transaction isolation for task processing and reliable event release during `shutdown`.
- **[Critical] MULTI-TENANT-01**: Fixed a bug where `V2Engine` was tied to a single table name. Refactored the engine to support multi-tenancy (table-level isolation), ensuring data is not mixed when multiple table instances share the same engine.
- **[High] QUAL-08**: Enhanced `V2Engine.shutdown()` robustness with double-invocation prevention, reliable `atexit` unregistration, and safer final flush logic.
- **QUAL-05 [Medium]**: Added guards against explicit `begin_transaction()` calls in V2 mode to prevent conflicts with background flushing operations.
- **[Medium] SEC-02**: Fixed the `column_type` validation regular expression in `core.py` from a vulnerable pattern (`[\w ]*`) to a safe pattern, completely resolving the ReDoS (Regular Expression Denial of Service) vulnerability warned by SonarQube.

#### Bug Fixes
- **[High] BUG-01**: Fixed `AttributeError` in `upsert()` and `aupsert()` when passing a data dictionary as the first argument while specifying `conflict_columns`. Improved internal logic to reference the correct keys in `target_data`. (1.4.1rc1)
- **[High] QUAL-02**: Fixed a potential race condition in `AsyncNanaSQLite` initialization where multiple concurrent async tasks could trigger redundant background initializations. Introduced `asyncio.Lock` to ensure thread-safe startup.
- Resolved syntax errors and initialization issues in `AsyncNanaSQLite.table()` caused by docstring fragmentation and incomplete argument propagation. (1.4.1dev3)
- Cleaned up duplicate method definitions in `AsyncNanaSQLite` that occurred during feature application. (1.4.1dev3)

#### Critical Fixes from Deep Audit
- **[Critical] BUG-02**: Resolved a "Stale Read" inconsistency in V2 mode where reading data via `get()` or `__getitem__` immediately after a write could return outdated values. Optimized the read path to prioritize the background staging buffer.
- **[Critical] QUAL-04**: Fixed a crash in `AsyncNanaSQLite` when instantiated outside an event loop due to unsafe `asyncio.Lock()` initialization in `__init__`. Implemented lazy initialization for the lock within the event loop context.
- **[Critical] LOCK-01**: Resolved a deadlock scenario in `ExpiringDict` where the TTL expiration callback (`on_expire`) was executed while holding the DB lock, conflicting with concurrent write operations. Callbacks are now executed outside the locking scope.
- **[Critical] CONC-01**: Fixed potential `RuntimeError`, cache corruption, and TOCTOU races in multi-threaded environments (e.g., `AsyncNanaSQLite`) by moving internal cache mutations into the scope of the database lock.
- **[Critical] CONC-02**: Resolved a crash when using `table()` in V2 mode where multiple background engines sharing the same SQLite connection would attempt to start overlapping transactions. Implemented `shared_lock` propagation across parent/child V2 engines.
- **[Critical] ASYNC-01**: Implemented missing V2 management methods (`aflush`, `aget_dlq`, `aretry_dlq`, `aclear_dlq`, `aget_v2_metrics`) in `AsyncNanaSQLite`.
- **[High] QUAL-07**: Added V2 management methods to the synchronous `NanaSQLite` class, achieving full feature parity between sync and async engines.
- **[High] QUAL-05**: Added guards to forbid explicit transaction operations (`begin_transaction`, etc.) in V2 mode, preventing fatal conflicts with the engine's automated background flushing.
- **[High] QUAL-06**: Fixed a bug where `v2_enable_metrics` setting was not inherited by child instances in `AsyncNanaSQLite.table()`.
- **[Medium] SEC-01 (Hardened)**: Upgraded `create_table()` column type validation from a blacklist approach to a strict whitelist-based regular expression for enhanced security.

#### Performance Improvements
- **[Low] PERF-01**: Introduced "negative caching" for LRU and TTL cache strategies to store the result of searches for keys that do not exist in the database, reducing I/O load during repeated access. (Also discovered and fixed a breaking bug before release where internal sentinels could leak due to this feature). (1.4.1rc1)

#### Code Quality Improvements
- **[Low] QUAL-01**: Improved the `ExpiringDict` scheduler thread stop logic to ensure more robust cleanup during instance destruction or clearing. (1.4.1rc1)
- **[Low] QUAL-03**: Deduplicated magic literals (e.g., `"BEGIN IMMEDIATE"`) into module-level constants to improve maintainability.
- **[Low] CI-01**: Resolved SonarQube Cloud "Quality Gate" false positives by excluding non-source files (docs, scripts) from coverage and suppressing non-essential maintainability warnings through configuration.
- **[Low] QUAL-09**: Removed unnecessary `.keys()` calls in `utils.py` (`list(dict.keys())` → `list(dict)`) to address SonarCloud code smell warnings.
- **[Low] QUAL-10 (New Feature)**: Introduced `V2Config` dataclass to group v2-related parameters (`flush_mode`, `flush_interval`, `flush_count`, `chunk_size`, `enable_metrics`) into a single object. All existing individual parameters remain available for full backward compatibility. This addresses SonarCloud's "brain-overload" warning for the `__init__` method having too many parameters.
  ```python
  from nanasqlite import NanaSQLite, V2Config
  cfg = V2Config(flush_mode="time", flush_interval=5.0, enable_metrics=True)
  db = NanaSQLite("mydata.db", v2_mode=True, v2_config=cfg)
  ```
- **[Low] CI-02**: Added `docker rm -f` before `docker run` in `bench-rpi.yml` to resolve container name conflicts (`"Conflict. The container name is already in use"`) that occurred when a prior workflow run was cancelled.

#### New Features: Enhanced V2 Engine Usability and Observability (Opt-in)
- **Dead Letter Queue (DLQ) Visibility**:
    - Added `get_dlq()`, `retry_dlq()`, and `clear_dlq()` methods to both synchronous and asynchronous (`a*`) interfaces.
    - Allows direct inspection, manual retry, or clearing of background operation errors.
- **Metrics Collection**:
    - Introduced a `v2_enable_metrics` parameter to enable detailed engine statistics collection.
    - `get_v2_metrics()` provides metrics such as total flush count, processing time, and DLQ error counts.
- **Configuration Inheritance**:
    - Ensured that V2-specific settings like `v2_enable_metrics` are correctly propagated to child instances created via the `table()` method.

#### Documentation
- **Enhanced API Documentation Generator**: Overhauled `scripts/gen_api_docs.py` to produce modern, highly readable API references utilizing VitePress tables and custom containers.
- **Site-wide Documentation Modernization**: Standardized all manual documentation by batch-converting callouts and warnings to the VitePress native format.

### [1.4.0] - 2026-03-12

#### Security Fixes
- **[Critical] SEC-01**: Fixed SQL injection vulnerability in `create_table()` column type definitions. APSW executes all semicolon-separated statements, allowing arbitrary SQL execution through crafted column type strings. Added validation that rejects column types containing `;`, `--`, or `/*`.

#### Bug Fixes
- **[High] BUG-01**: Fixed V2Engine `_process_strict_queue()` calling `on_success` callbacks before transaction COMMIT. If a later task failed and caused a ROLLBACK, earlier callers would receive false success notifications. Callbacks are now deferred until after COMMIT succeeds.
- **[Medium] BUG-02**: Fixed `AsyncNanaSQLite.table()` child instances missing `_v2_mode`, `_cache_strategy`, `_encryption_key` and other attributes, causing `AttributeError`. All parent settings are now properly inherited.
- **[Medium] BUG-03**: Fixed v2 mode `execute()` returning empty results for SELECT/PRAGMA/EXPLAIN queries. Read queries now bypass the background queue and execute directly.

#### Code Quality Improvements
- **[Low] BUG-04**: Replaced duplicated alias extraction logic in `_shared_query_impl()` with a call to `NanaSQLite._extract_column_aliases()`.
- **[Low] QUAL-01**: Fixed `update()` method type annotation from `dict` to `dict | None`.

### [1.4.0dev2] - 2026-03-12

#### Improvements: Async API Completion
- Implemented and exposed all key methods in `AsyncNanaSQLite` as asynchronous versions (`abackup`, `arestore`, `apragma`, `aget_table_schema`, `alist_indexes`, `aalter_table_add_column`, `aupsert`, `aget_dlq`, `aretry_dlq`, etc.) to achieve full feature parity with the synchronous version.

#### Changes: Unified and Enhanced upsert() Method
- Unified the `upsert()` method signature to support both `(table_name, data_dict, conflict_columns)` and `(key, value)` patterns in a single method.
- When `v2_mode` is enabled, the `(key, value)` pattern is automatically routed to the background persistence queue.

#### Testing: Expanded Benchmark Coverage
- Increased benchmark tests from 158 to **177**.
- Added coverage for previously unmeasured operations: `backup`, `restore`, `pragma`, `DDL (alter table/index)`, `export/import`, etc.
- Significantly enhanced asynchronous benchmarks (`tests/test_async_benchmark.py`).

#### Fixes
- Fixed `get_table_schema` to accept an optional `table_name` argument (defaulting to the current table) and handle cases where the `table` property is missing.
- Resolved all project-wide `ruff` linting errors (31 items) and `mypy` type check issues.

### [1.4.0dev1] - 2026-03-12

#### New Features: v2 Architecture (Optional)
- **Non-blocking Background Persistence**:
  - Enable the v2 architecture by passing `v2_mode=True` to `NanaSQLite`.
  - All write operations (KVS updates and explicit SQL execution) are temporarily buffered in memory or queued, and then flushed to SQLite asynchronously by a background thread.
  - This eliminates disk I/O blocking on the main thread entirely, dramatically improving write latency.
  - Read latency remains zero-cost as data is still fetched directly from the in-memory cache.
  - **Flush Modes**: Customize flushing behavior using the `flush_mode` parameter (`immediate`, `count`, `time`, or `manual`).
  - **Dead Letter Queue (DLQ)**: If a background SQL execution fails, the problematic task is isolated to a DLQ, allowing the rest of the data persistence pipeline to proceed without halting the system. Use `get_dlq()` to inspect and `retry_dlq()` to re-enqueue failed tasks.
  - **Chunk Flushing**: Automatically splits large write batches (default: 1000 items) to prevent long-held database locks.
  - **Warning**: The v2 architecture is designed exclusively for SINGLE-PROCESS systems. A warning is emitted if used in multi-process environments (e.g., Gunicorn with multiple workers) as parallel background threads will cause data corruption.

#### Changes
- Added `v2_mode`, `flush_mode`, `flush_interval`, `flush_count`, and `v2_chunk_size` parameters to `NanaSQLite` and `AsyncNanaSQLite` initialization.
- Added explicit `flush()` (sync) and `aflush()` (async) methods.
- Added `get_dlq()` and `retry_dlq()` methods to `V2Engine` for DLQ management.

#### Fixes
- Fixed a race condition when accessing the Dead Letter Queue (DLQ) concurrently in the v2 engine.
- Fixed a bug where strict queue tasks were not processed if the KVS staging buffer was empty.

### [1.3.4] - 2026-03-10

#### Security Fixes

- **SEC-01 [High]**: Switched `alter_table_add_column()` `column_type` validation from blacklist to whitelist regex. Reliably blocks injection payloads like `TEXT; DROP TABLE`.
- **SEC-02 [High]**: Fixed `sanitize_sql_for_function_scan()` to preserve double-quoted SQL identifier content. `_validate_expression()` now correctly detects quoted function name bypasses like `"LOAD_EXTENSION"()`.

#### Bug Fixes

- **BUG-01 [Critical]**: Added `_check_connection()` check to `items()`. Calling on a closed instance now raises `NanaSQLiteClosedError` instead of leaking a low-level APSW exception.
- **BUG-02 [High]**: AEAD deserialization now logs a warning instead of silently falling back to plaintext JSON when receiving non-bytes values.
- **BUG-03 [High]**: Added payload length validation (≥28 bytes = 12-byte nonce + 16-byte auth tag) before AEAD decrypt. Short data now raises a clear `NanaSQLiteDatabaseError`. `InvalidTag` and other low-level crypto exceptions are also wrapped into `NanaSQLiteDatabaseError`.
- **BUG-04 [High]**: Removed redundant double `_ensure_initialized()` call in `AsyncNanaSQLite.acontains()`.
- **BUG-05 [Medium]**: Added `offset` type and non-negative validation in async `_shared_query_impl()`.
- **BUG-06 [Medium]**: Fixed `parameters: tuple = None` → `tuple | None = None` type annotations in `async_core.py` (mypy strict compliance).
- **BUG-07 [Medium]**: `ExpiringDict` scheduler now processes all expired keys per iteration instead of just one.
- **BUG-09 [Medium]**: `batch_get()` now correctly includes keys with explicit `None` values in results.
- **BUG-10 [Low]**: Reuse compiled `IDENTIFIER_PATTERN` in `_sanitize_identifier()`.
- **BUG-12 [Low]**: Fixed `NanaSQLiteDatabaseError.__init__` `original_error` type annotation to `Exception | None`.

#### Performance Improvements

- **PERF-03 [Medium]**: Extracted `_extract_column_aliases()` helper, deduplicating column-alias extraction from 3 call sites.

#### Code Quality

- **QUAL-01 [Medium]**: Fixed `_get_all_keys_from_db()` return type to `list[str]`.
- **QUAL-03 [Medium]**: Harmonized column-name quote stripping between `query()` and `query_with_pagination()`.

#### Audit & Testing

- Added pre-release audit report (`audit.md`) — 35 findings documented.
- Added 6 POC scripts in `etc/poc/`.
- Added 20 POC verification tests in `tests/test_audit_poc.py`.
- Updated `audit_prompt.md` to 6-phase workflow (audit → POC → patch → pytest → CI verification → release preparation).

### [1.3.4rc4] - 2026-03-08

#### CI Fixes

- **Least-privilege cleanup for the provenance job** (PR [#127](https://github.com/disnana/NanaSQLite/pull/127)):
  - Downgraded `contents: write` to `contents: read` in the `provenance` job; write access was only needed for `upload-assets`, which was already removed.
  - Removed the dead `upload-assets: true` option — this workflow has no tag-based trigger, so the SLSA generator would always skip it.
  - Provenance is still attached to GitHub Releases by the `release` job as before.
  - Added inline comments explaining the two expected CI annotations (`go.sum not found` warning and PyPI attestation notice) to prevent confusion.
  - Synced `CHANGELOG.md` from the latest `main` branch.

### [1.3.4rc3] - 2026-03-08

#### CI Fixes

- **Restored and hardened the SLSA3 provenance release flow** (PR [#123](https://github.com/disnana/NanaSQLite/pull/123)):
  - Added `actions: read` and `contents: read` permissions to the provenance verification job in GitHub Actions.
  - Constructed the expected provenance filename from the `provenance-name` output and now fail fast if the file is missing.
  - Updated GitHub Release asset upload to reference the exact generated provenance file instead of a wildcard, preventing release-time artifact mismatches.

### [1.3.4rc2] - 2026-03-08

#### Security Fixes

- **Implemented SQL injection protection for table names** (PR [#121](https://github.com/disnana/NanaSQLite/pull/121), [#122](https://github.com/disnana/NanaSQLite/pull/122)):
  - Table names were interpolated directly into SQL queries, making crafted names exploitable for injection.
  - Sanitized (double-quoted) table name is now cached in `self._safe_table` and used in all SQL execution paths.
  - `self._table` retains the raw name for `__repr__` and backwards compatibility.
  - Updated SECURITY.md with disclosure history and remediation details.
  - Added PoC scripts (`etc/poc/poc_sqli.py`, `etc/poc/poc_none.py`) to document the risk.

#### Bug Fixes & Code Quality

- **Applied `_NOT_FOUND` sentinel to `get_fresh()` and `__contains__`** (PR [#121](https://github.com/disnana/NanaSQLite/pull/121)):
  - `get_fresh()` previously returned `None` on a DB miss, making it impossible to distinguish from a stored `None` value.
  - Switched to the `_NOT_FOUND = object()` sentinel so DB misses and stored `None` are reliably distinguished.
  - Restored a lightweight `__contains__` implementation to reduce unnecessary DB reads.

#### CI Fixes

- **Fixed validkit-py CI test guards** (PR [#119](https://github.com/disnana/NanaSQLite/pull/119)):
  - Updated CI to install the `validation` extra so validkit-related tests are executed correctly.

#### Documentation

- **Added validkit-py validation guide** (PR [#117](https://github.com/disnana/NanaSQLite/pull/117)):
  - Added validkit-py usage and validation guides to both the English and Japanese documentation sites.
- **Reordered and classified guide lessons** (PR [#116](https://github.com/disnana/NanaSQLite/pull/116)):
  - Reorganised and categorised guide lessons in the JA/EN site documentation.
- **Fixed docs inconsistencies, broken links, and factual errors** (PR [#115](https://github.com/disnana/NanaSQLite/pull/115)):
  - Resolved inconsistencies between English and Japanese documentation, fixed broken links, corrected factual errors, and added missing documentation.

### [1.3.4rc1] - 2026-03-07

#### New Features

- **Added `batch_update_partial()` method** (sync and async):
  - New method that writes a batch in "best-effort" mode when a `validator` is set.
  - Each entry is validated individually; only entries that pass are written to the database.
  - Returns a `dict` of `{key: error_message}` for failed entries — no exception is raised.
  - When `coerce=True`, coerced values are stored for successful entries.
  - The existing `batch_update()` retains its atomic behaviour (all-or-nothing).
  - Async counterpart added as `AsyncNanaSQLite.abatch_update_partial()`.

#### Bug Fixes & Code Quality

- **Fixed mypy error in `core.py`**:
  - `_serialize()` returned `json_str` which mypy inferred as `str | None` in the `HAS_ORJSON=False` path; suppressed with `type: ignore` since `json_str` is guaranteed `str` at that point.
- **Fixed ruff violations in examples**:
  - `examples/test_examples.py`: import sort (I001), `assert False` → `raise AssertionError()` (B011), class name to CapWords (N801).
  - `examples/validkit_batch_demo.py`: import sort (I001).

#### Added Examples

- **Added `examples/validkit_batch_demo.py`**:
  - Demonstrates atomic `batch_update()` and best-effort `batch_update_partial()`.
  - Includes `coerce=True` usage with field-level `.coerce()`.
- **Extended `examples/test_examples.py`** with validkit batch operation validation:
  - Atomic rollback verification, partial write verification, coerce mode verification.

### [1.3.4b3] - 2026-03-05

#### Bug Fixes & Stability Improvements

- **Fixed test instability on Python 3.9** (`tests/test_tdd_cycle_6.py`) (PR [#113](https://github.com/disnana/NanaSQLite/pull/113)):
  - `test_ellipsis_type_is_available` checks for `types.EllipsisType` (added in Python 3.10),
    but was unconditionally asserting its presence and therefore always failed on Python 3.9.
  - Added `@pytest.mark.skipif(sys.version_info < (3, 10), ...)` so the test is skipped on
    Python 3.9 and still runs on Python 3.10+.
  - Because both `core.py` and `async_core.py` use `from __future__ import annotations`, the
    `types.EllipsisType` in their type annotations is stored as a string and is never evaluated
    at runtime, so the library itself already works correctly on Python 3.9. This was a
    test-only issue.
  - No impact on library behaviour or public API.

- **Fixed `table()` cache settings inheritance** (PR [#112](https://github.com/disnana/NanaSQLite/pull/112)):
  - Child instances created via `table()` did not inherit `cache_ttl` / `cache_persistence_ttl` from
    their parent, causing `ValueError` when the parent used a TTL cache strategy.
  - Introduced `_cache_strategy_raw`, `_cache_size_raw`, `_cache_ttl_raw`, and
    `_cache_persistence_ttl_raw` to store the original arguments; `table()` now propagates
    all cache settings correctly.

- **`AsyncNanaSQLite` now raises `ImportError` eagerly when validkit-py is missing** (PR [#112](https://github.com/disnana/NanaSQLite/pull/112)):
  - Previously the error was deferred until a write occurred. `AsyncNanaSQLite.__init__` now
    raises `ImportError` immediately when `validator` is supplied without validkit-py installed,
    aligning behaviour with the synchronous `NanaSQLite`.
  - Added `HAS_VALIDKIT` flag to `async_core.py`.

- **Exception narrowing in `core.py`**:
  - Replaced broad `except Exception:` clauses guarding optional imports (orjson / validkit-py)
    with the more specific `except ImportError:`.

- **Type annotation fixes**:
  - Added `"ttl"` to the `Literal` type of the `cache_strategy` argument in `table()`.
  - Changed the `_UNSET` sentinel type annotation to `types.EllipsisType` for improved type safety.

- **mypy configuration update** (`pyproject.toml`):
  - Bumped `python_version` from `3.9` to `3.10` so that `types.EllipsisType` is recognised
    during static type checking.

#### API Documentation Fixes (PR [#112](https://github.com/disnana/NanaSQLite/pull/112))

- Updated `NanaSQLite.table()` and `AsyncNanaSQLite.table()` API docs (English and Japanese)
  to show `validator=...` and `coerce=...` (sentinel default indicating parent-inheritance).

#### Tests & Quality Improvements (PR [#112](https://github.com/disnana/NanaSQLite/pull/112))

- **Added comprehensive test suites**:
  - `tests/test_table_inheritance_comprehensive.py`: 75 test cases covering all `table()` inheritance scenarios.
  - `tests/test_validkit_integration.py`: Integration tests for validkit-py (sync and async).
  - `tests/test_tdd_review_fixes.py`: Regression tests for review-comment fixes.
  - `tests/test_tdd_cycle_2.py` through `tests/test_tdd_cycle_10.py`: Per-cycle regression tests.
- **Improved validkit availability check**:
  - Replaced `importlib.util.find_spec` with a `try/except import` check so broken installations
    are also correctly detected.

### [1.3.4b2] - 2026-03-04

#### New Features

- **`validator` parameter (optional dependency: validkit-py)**:
  - Added `validator` parameter to `NanaSQLite.__init__` and `AsyncNanaSQLite.__init__`.
  - Accepts a validkit-py schema (plain dict or `Schema` object). When supplied, values are validated before every write.
  - Raises `NanaSQLiteValidationError` on schema violation.
  - Raises `ImportError` with an install hint when `validator` is supplied but `validkit-py` is not installed.
  - Install via `pip install nanasqlite[validation]`.
  - Exposes `HAS_VALIDKIT` flag from the `nanasqlite` package (and `core` module).

- **Per-table `validator` support in `table()`**:
  - Added `validator` parameter to `NanaSQLite.table()` and `AsyncNanaSQLite.table()`.
  - Different schemas can now be applied per sub-table.
  - When `validator` is omitted, the parent instance's schema is inherited automatically.

- **`coerce` parameter (auto-conversion option)**:
  - Added `coerce: bool = False` parameter to `NanaSQLite.__init__`, `NanaSQLite.table()`, `AsyncNanaSQLite.__init__`, and `AsyncNanaSQLite.table()`.
  - When `True`, the coerced value returned by validkit-py (e.g. `"42"` → `42`) is stored instead of the original value.
  - **Important**: Auto-conversion requires **both** `coerce=True` on `NanaSQLite` AND `.coerce()` on each field validator in the schema (e.g., `v.int().coerce()`). Without `.coerce()` on the field, values whose types don't match the schema will still raise `NanaSQLiteValidationError` even with `coerce=True`.
  - Works in conjunction with `validator`; has no effect when no validator is set.
  - When omitted in `table()`, the parent's `coerce` setting is inherited automatically.

- **`batch_update()` validation support**:
  - When a `validator` is set, `batch_update()` now validates all values before touching the database.
  - If any value fails validation, nothing is written (atomic failure guarantee).
  - When `coerce=True`, coerced values are bulk-written instead of the originals.

#### Bug Fixes

- **`table()` no longer drops the parent `validator` on child instances**:
  - In b1, child instances created via `table()` did not inherit `_validator`, so writes to
    sub-tables bypassed validation entirely.
  - The same issue was present in `AsyncNanaSQLite.table()` where `_validator` was never
    assigned to `async_sub_db`; this is now fixed.

### [1.3.4b1] - 2026-03-04

#### New Features

- **`lock_timeout` parameter** (P2-1):
  - Added `lock_timeout: float | None = None` parameter to `NanaSQLite.__init__`.
  - When set, raises `NanaSQLiteLockError` if the lock cannot be acquired within the specified seconds.
  - Default `None` preserves the existing unlimited-wait behaviour. Fully backward-compatible.
  - Introduced `_acquire_lock()` context manager internally so user-facing exclusive operations respect the timeout (some internal operations such as TTL expiry deletion continue to use blocking acquisition).

- **`backup()` / `restore()` methods** (P2-3):
  - `NanaSQLite.backup(dest_path)`: Backs up the current database to `dest_path` using APSW's SQLite online backup API.
  - `NanaSQLite.restore(src_path)`: Restores the database from a backup file, re-establishes the connection, and clears the in-memory cache. Explicitly removes WAL/SHM/journal sidecar files (`-wal`/`-shm`/`-journal`) before reopening to prevent stale WAL replay causing an inconsistent state.
  - Both are new public methods only; no backward-compatibility impact.

#### Thread Safety Improvements

- **Lock-protected child instance creation in `table()`**:
  - Wrapped child instance creation and `WeakSet` registration in `table()` with `_acquire_lock()` to prevent race conditions with `restore()`'s connection replacement, eliminating the risk of child instances referencing a closed connection.

#### Bug Fixes

- **Added `_check_connection()` to `__delitem__`**:
  - `del db[key]` on a closed connection now raises `NanaSQLiteClosedError` consistently, matching the behaviour of `__setitem__`, `pop()`, and `clear()`.

### [1.3.4b0] - 2026-03-04

#### Code Quality Improvements
- **Async pool cleanup log level fix**:
  - Changed the log level from `ERROR` to `WARNING` for `AttributeError` occurrences during read-only pool drain in `AsyncNanaSQLite.close()`.
  - Updated the comment wording from "Programming error" to "Unexpected AttributeError - log and continue cleanup for resilience" to better reflect intent.
  - Log output only; no behaviour or backward-compatibility impact.

#### Documentation & Planning
- **Added v1.3.x plan review document** (`etc/in_progress/v1.3.x_plan_review.md`):
  - Cross-referenced all `etc/` planning docs against the v1.3.x changelog to surface remaining work and set priorities.
  - Documented priorities for roadmap Phase 2 items still outstanding (lock timeout, validation foundation, backup/restore).
  - Included a draft release schedule from v1.3.4b0 through v1.4.0.
- **Updated `etc/README.md`**: Added the new review document to the `in_progress/` table.
- **Reorganised `etc/` directory** (PR [#109](https://github.com/disnana/NanaSQLite/pull/109)):
  - Replaced the flat `future_plans/` folder with three status-based subdirectories: `implemented/`, `in_progress/`, and `planned/`.
  - Verified that all v1.3.0 cache features (`ExpiringDict`, `UnboundedCache`, `TTLCache`, etc.) are fully implemented.

#### Dependency Updates (docs/site Maintenance)
- **docs/site dependency updates** (Renovate):
  - Updated `autoprefixer` from v10.4.24 to v10.4.27. ([#105](https://github.com/disnana/NanaSQLite/pull/105))
  - Updated `postcss` from v8.5.6 to v8.5.8. ([#106](https://github.com/disnana/NanaSQLite/pull/106))
  - Updated `vue` from v3.5.27 to v3.5.29. ([#107](https://github.com/disnana/NanaSQLite/pull/107))
  - Updated `tailwindcss` / `@tailwindcss/postcss` from v4.1.18 to v4.2.1. ([#108](https://github.com/disnana/NanaSQLite/pull/108))

### [1.3.4dev0] - 2026-03-02

#### CI / Development Environment
- **SLSA provenance cache restore warning — investigation and revert**:
  - Added an empty `go.sum` at the repo root to suppress the `Restore cache failed` warning emitted by the `provenance / generator` job (PR [#103](https://github.com/disnana/NanaSQLite/pull/103)).
  - Determined that the fix was ineffective: the `provenance / generator` job runs on an isolated runner that does not check out this repository, so the warning cannot be silenced by a local file. The empty `go.sum` was subsequently removed (PR [#104](https://github.com/disnana/NanaSQLite/pull/104)).

#### Other
- Bumped version to `1.3.4dev0` (development snapshot following the `1.3.3` release).

### [1.3.3] - 2026-03-02

#### Security
- **docs/site dependency vulnerability fixes**:
  - Updated/pinned rollup to a safe version (`>=4.59.0`) to address the rollup vulnerability (GHSA-mw96-cpmx-2vgc).
  - Related PRs: [#99](https://github.com/disnana/NanaSQLite/pull/99), [#102](https://github.com/disnana/NanaSQLite/pull/102)

#### CI / Development Environment
- **GitHub Actions updates**:
  - Bumped `actions/download-artifact` to v8. ([#100](https://github.com/disnana/NanaSQLite/pull/100))
  - Bumped `actions/upload-artifact` to v7. ([#101](https://github.com/disnana/NanaSQLite/pull/101))
  - Bumped `google/osv-scanner-action` (reusable / reusable-pr) to 2.3.3. ([#97](https://github.com/disnana/NanaSQLite/pull/97), [#98](https://github.com/disnana/NanaSQLite/pull/98))

#### Dependency Updates (Maintenance)
- **Release automation action update**:
  - Updated `softprops/action-gh-release` to v2. ([#96](https://github.com/disnana/NanaSQLite/pull/96))

#### Notes
- This release is primarily a maintenance update (security/CI/dependency bumps) and does not include breaking changes to the public API.

### [1.3.2] - 2026-01-17

#### Performance Optimization
- **orjson Integration Refinement**:
  - Removed unnecessary variable allocation in `_serialize()` method to improve code readability and maintainability.
  - Verified and validated that orjson JSON encoding/decoding is effectively utilized across all encryption paths (Fernet, AES-GCM, ChaCha20).
  - Expected **3-5x performance improvement** compared to standard `json` module.
  - Confirmed that async processing (`AsyncNanaSQLite`) automatically benefits from orjson via ThreadPoolExecutor.

#### Code Quality Improvements
- **Core Code Optimization**:
  - Enhanced code readability and clarified variable scope.

#### Testing & Validation
- **orjson Tests Verification**:
  - Confirmed all tests in `tests/test_json_backends.py` run correctly.
  - Verified compatibility in both orjson-available and fallback environments.
  - Confirmed automatic JSON backend switching (HAS_ORJSON flag) functions correctly.

### [1.3.1] - 2025-12-28

#### New Features: Optional Data Encryption
- **Multi-mode Encryption**: Transparent encryption using `cryptography`.
    - **AES-GCM (Default)**: Secure and fast, optimized for hardware acceleration (AES-NI).
    - **ChaCha20-Poly1305**: High software-only performance, ideal for devices without AES-NI.
    - **Fernet**: High-level API for compatibility and ease of use.
    - Added `encryption_key` and `encryption_mode` parameters to `NanaSQLite` and `AsyncNanaSQLite`.
- **Extra Installation**: `pip install nanasqlite[encryption]` to install required dependencies.

#### New Features: Flexible Cache Strategy & TTL Support (v1.3.1-alpha.0)
- **TTL (Time-To-Live) Cache**: Set expiration for cached data using `cache_strategy=CacheType.TTL, cache_ttl=seconds`.
- **Persistence TTL**: Automatically delete expired data from the SQLite database with `cache_persistence_ttl=True`.
- **FIFO-limited Unbounded Cache**: Specify `cache_size` in `UNBOUNDED` mode for FIFO (First-In-First-Out) eviction.
- **Cache Clearing API**: Added `db.clear_cache()` and async `aclear_cache()`.

#### Improvements & Fixes
- **Optimized `ExpiringDict`**: Internal utility for high-precision, low-overhead expiration management.
- **Maintained Performance**: Preserved the fast-path for the default `UNBOUNDED` mode while ensuring limits are strictly enforced when configured.
- **Enhanced Type Safety**: Fully compliant with `mypy` and `ruff` strict checks.
- **Unified Benchmarks**: Consolidated encryption and cache strategy benchmarks into `tests/test_benchmark.py` (Sync) and `tests/test_async_benchmark.py` (Async).
- **Test Coverage**: Added `tests/test_async_cache.py` to verify async cache behaviors (LRU eviction, TTL expiration).

### [1.3.0dev0] - 2025-12-27

#### New Features: Flexible Cache Strategy
- **Added `CacheType` Enum**: Choose between `UNBOUNDED` (infinite, legacy behavior) and `LRU` (eviction-based).
- **LRU Cache Implementation**: Limit memory usage with `cache_strategy=CacheType.LRU, cache_size=N`.
- **Per-Table Configuration**: Configure specific tables via `db.table("logs", cache_strategy=CacheType.LRU, cache_size=100)`.
- **Performance Option**: Install `lru-dict` C-extension via `pip install nanasqlite[speed]` for up to 2x speedup.
- **Automated Fallback**: Automatically falls back to standard library `OrderedDict` if `lru-dict` is not installed.

#### New Tests
- `tests/test_cache.py`: Comprehensive test suite for cache strategies (eviction, persistence, per-table configuration).

### [1.2.2b1] - 2025-12-27

#### Documentation & Brand Overhaul
- **Ultra-Modern Documentation Site**:
  - Built a new high-end official site using VitePress + Tailwind CSS in `docs/site`, significantly improving design and UX.
  - **Official SVG Identity**: Created an original 'Dict-Stack' symbol. Features 100% transparency, automatic dark mode support (via inverted filters), and infinite vector resolution.
  - **Truly Isolated Bilingual API Docs**: Implemented an intelligent extraction engine to parse docstrings and generate purely localized references for both Japanese and English.
- **Automation & Deployment**:
  - Introduced automated deployment via GitHub Actions (`deploy-docs.yml`).
  - Implemented smart history preservation that automatically merges previous benchmark data from `gh-pages` into the new documentation build.

#### Security & CI Improvements
- **SQL Validation Refinement**:
  - Added the `||` (concatenation) operator to the fast-validation safe set, resolving false positives in complex SQL alias queries.
- **CI/CD Stability**:
  - Strict re-sorting of imports in `core.py` and `gen_api_docs.py` to comply with the latest `ruff` linting rules.
  - Enhanced dependency management for documentation builds.

### [1.2.2a1] - 2025-12-26

#### Development Tools (Benchmarks & CI/CD)
- **Fixed Benchmark Comparison Logic**:
  - Standardized comparison to use ops/sec; higher values now correctly show as positive (🚀/✅) improvements.
  - Added absolute ops/sec difference (e.g., `+2.1M ops`) to the performance summary table.
  - **Ops/sec Accuracy**: Switched to using raw `ops` data from the benchmark tool instead of calculating from mean time (approximation). This also fixed the bug where OS details showed `(0.0)`.
  - Corrected time formatting for sub-microsecond values to explicitly use `ns` (nanoseconds).
  - Introduced status emojis (🚀, ✅, ➖, ⚠️, 🔴) for quick visual performance assessment.
- **Workflow Optimizations**:
  - `benchmark.yml`: Changed benchmarks to be informational-only to prevent CI failures caused by GitHub Actions runner performance variance (~10-60%).
  - `ci.yml`: Optimized triggers by restricting automatic `push` runs to the `main` branch. Added `workflow_dispatch` for manual runs on other branches.
  - Simplified `should-run` check logic.


### [1.2.1b2] - 2025-12-25

#### Development Tools
- **CI/CD Workflow Consolidation**:
  - Consolidated `lint.yml`, `test.yml`, `publish.yml`, and `quality-gate.yml` into a single `ci.yml`.
  - Added direct links to PyPI and GitHub Release, and detailed job statuses (Cancelled/Skipped support) in the final summary.
- **Test Environment Optimization**:
  - Refined the CI test matrix. Ubuntu runs all versions, while Windows/macOS focus on popular versions (3.11 and 3.13) to reduce execution time.
  - Added `pytest-xdist` to dev dependencies for parallel testing support.
- **Type Checking Improvements**:
  - Resolved 156 mypy errors by refining the configuration (introduced `--no-strict-optional` and fine-tuned error code controls).

#### Development Tools
- **Lint & CI Environment**:
  - Added `tox.ini` with environments for `tox -e lint` (ruff), `tox -e type` (mypy), `tox -e format`, and `tox -e fix`.
  - Added ruff configuration to `pyproject.toml` (E/W/F/I/B/UP/N/ASYNC rules, Python 3.9+ support, line-length: 120).
  - Added mypy configuration to `pyproject.toml` (using `--no-strict-optional` flag for practical type checking).
  - Added `.github/workflows/lint.yml`: PyPA/twine-style CI workflow with tox integration, FORCE_COLOR support, and summary output.
  - Added `.github/workflows/quality-gate.yml`: All-green gate with main branch detection and publish readiness check.
  - Added dev dependencies: `tox>=4.0.0`, `ruff>=0.8.0`, `mypy>=1.13.0`.
- **Code Quality Improvements**:
  - Fixed 1373 lint errors via ruff auto-fix (import ordering, unused imports removal, pyupgrade, whitespace, etc.).
  - Added B904 (raise without from) and B017 (assert raises Exception) to ignore list.
  - Adjusted mypy configuration for practical use (156 errors → 0 errors).

### [1.2.0b1] - 2025-12-24

#### Security & Robustness
- **Enhanced `ORDER BY` Parsing**:
  - Implemented a dedicated parser `_parse_order_by_clause` in `NanaSQLite` to safely handle and validate complex `ORDER BY` clauses.
  - Improved protection against SQL injection while supporting legitimate complex sorting patterns.
- **Strict Validation Fixes**:
  - Standardized error messages for dangerous patterns (`;`, `--`, `/*`) to consistently follow the `Invalid [label]: [message]` format.
  - Ensured consistent behavior between legacy and new security tests by applying a unified message format for all validation failures.

#### Refactoring
- **Code Organization**:
  - Extracted `_sanitize_sql_for_function_scan` logic to a new `nanasqlite.sql_utils` module for better maintainability.
  - Eliminated code duplication in `AsyncNanaSQLite` by consolidating `query` and `query_with_pagination` methods into a shared `_shared_query_impl` helper method (~150 lines reduced).
- **Type Safety**:
  - Added `Literal` type hints for `context` parameter to improve IDE support and type checking (PR #36).

#### Fixes & Improvements
- **Async Logging**:
  - Increased log level from DEBUG to WARNING for errors occurring during read-pool cleanup to ensure resource issues are visible.
  - Added connection context to cleanup error messages.
- **Improved Async Pool Cleanup Robustness**:
  - Enhanced `AsyncNanaSQLite.close()` method to ensure all pool connections are cleaned up even if some connections encounter errors.
  - Changed error handling to continue cleanup instead of breaking on `AttributeError`, preventing resource leaks.
- **Tests**:
  - Fixed `__eq__` method to correctly propagate `NanaSQLiteClosedError` when instances are closed (PR #44).
  - Improved exception handling specificity in security tests (PR #43).
  - Clarified comments in security tests regarding validation timing (PR #35).
  - Removed duplicate `pytest` imports and cleaned up temporary test files (`temp_test_parser.py`).

### [1.2.0a2] - 2025-12-23

- **Enhanced Async Security Features**:
  - Fixed `AsyncNanaSQLite.query` and `query_with_pagination` to correctly pass `allowed_sql_functions`, `forbidden_sql_functions`, and `override_allowed` to `_validate_expression`.
  - Added comprehensive asynchronous security tests in `tests/test_security_async_v120.py`.
- **Improved Async Connection Management**:
  - Added `_closed` flag to `AsyncNanaSQLite` to track the connection state.
  - Improved child instance invalidation: sub-instances created via `table()` are now immediately marked as closed when the parent is closed.
  - Fixed `close()` behavior to ensure that even uninitialized instances correctly transition to a closed state, raising `NanaSQLiteClosedError` on subsequent operations.

### [1.2.0a1] - 2025-12-23

- **Async Read-Only Connection Pool**:
  - Added `read_pool_size` logic to `AsyncNanaSQLite`.
  - Enables parallel execution for `query`, `query_with_pagination`, `fetch_all`, `fetch_one`.
  - Enforces `read-only` mode for pool connections for safety.
- **Bug Fixes**:
  - Fixed `apsw.ExecutionCompleteError` occurring in `query` and `query_with_pagination` when results are empty (0 rows).
  - Aligned column metadata extraction with sync implementation using `PRAGMA table_info` and manual parsing instead of relying on `cursor.description`.

### [1.2.0dev1] - 2025-12-23

#### Fixed
- **Async API Consistency**:
  - Added `a`-prefixed aliases for all methods in `AsyncNanaSQLite` (e.g., `abatch_update`, `ato_dict`).
  - Resolved "method not defined" errors in `test_async_benchmark.py`.
- **Backward Compatibility Fixes**:
  - Re-aligned SQL injection error messages to match legacy test expectations (e.g., "Invalid order_by clause").
  - Updated `test_enhancements.py` to handle `NanaSQLiteClosedError` alongside class name checks.
- **Windows Stability**:
  - Refactored `test_security_v120.py` to use `tmp_path` fixture, resolving `BusyError` and `IOError` on Windows.
- **`query`/`query_with_pagination` Bug Fix**:
  - Fixed issue where `limit=0` and `offset=0` were ignored. Changed `if limit:` to `if limit is not None:`.
  - ⚠️ **Backward Compatibility**: Previously, passing `limit=0` returned all rows. Now it correctly returns 0 rows. If you used `limit=0` to mean "no limit", change to `limit=None`.
- **Edge Case Tests Added**:
  - Created `tests/test_edge_cases_v120.py` with tests for empty `batch_*` operations and pagination boundary conditions.

### [1.2.0dev0] - 2025-12-22

#### Added
- **Security Enhancements (Phase 1)**:
  - Introduced `strict_sql_validation` flag (Exception or Warning for unauthorized functions).
  - Introduced `max_clause_length` to limit dynamic SQL length (ReDoS protection).
  - Enhanced detection for dangerous SQL patterns (`;`, `--`, `/*`) and keywords (`DROP`, `DELETE`, etc.).
- **Strict Connection Management**:
  - Introduced `NanaSQLiteClosedError`.
  - Implemented child instance tracking/invalidation when the parent instance is closed.
- **Maintenance**:
  - Created `DEVELOPMENT_GUIDE.md` (Bilingual).
  - Codified environment sync rule: `pip install -e . -U`.

### [1.1.0] - 2025-12-19

#### Added
- **Custom Exception Classes**:
  - `NanaSQLiteError` (base class)
  - `NanaSQLiteValidationError` (validation errors)
  - `NanaSQLiteDatabaseError` (database operation errors)
  - `NanaSQLiteTransactionError` (transaction-related errors)
  - `NanaSQLiteConnectionError` (connection errors)
  - `NanaSQLiteLockError` (lock errors, for future use)
  - `NanaSQLiteCacheError` (cache errors, for future use)

- **Batch Retrieval (`batch_get`)**:
  - Efficiently load multiple keys with `batch_get(keys: List[str])`
  - Async support via `AsyncNanaSQLite.abatch_get(keys)`
  - Optimizes cache by fetching multiple items in a single query
- **Enhanced Transaction Management**:
  - Transaction state tracking (`_in_transaction`, `_transaction_depth`)
  - Detection and error reporting for nested transactions
  - Added `in_transaction()` method
  - Prevention of connection closure during transactions
  - Detection of commit/rollback outside transactions

- **Async Transaction Support**:
  - `AsyncNanaSQLite.begin_transaction()`
  - `AsyncNanaSQLite.commit()`
  - `AsyncNanaSQLite.rollback()`
  - `AsyncNanaSQLite.in_transaction()`
  - `AsyncNanaSQLite.transaction()` (context manager)
  - `_AsyncTransactionContext` class implementation

- **Resource Leak Prevention**:
  - Parent instance tracks child instances with weak references
  - Notification to child instances when parent is closed
  - Prevention of orphaned child instance usage
  - Added `_check_connection()` method
  - Added `_mark_parent_closed()` method

#### Improvements
- **Enhanced Error Handling**:
  - Added error handling to `execute()` method
  - Wraps APSW exceptions with `NanaSQLiteDatabaseError`
  - Preserves original error information (`original_error` attribute)
  - Added connection state checks to each method
  - Uses `NanaSQLiteValidationError` in `_sanitize_identifier()`

- **Added connection check to `__setitem__` method**

#### Documentation
- **New Documentation**:
  - `docs/en/error_handling.md` - Error handling guide
  - `docs/en/transaction_guide.md` - Transaction guide
  - `tests/test_enhancements.py` - Tests for enhanced features (21 tests)

- **README Updates**:
  - Added transaction support section
  - Added custom exception sample code
  - Added async transaction samples

#### Tests
- **New Tests** (21 tests):
  - Custom exception class tests (5 tests)
  - Transaction feature enhancement tests (6 tests)
  - Resource management tests (3 tests)
  - Error handling tests (2 tests)
  - Transaction and exception combination tests (2 tests)
  - Async transaction tests (3 tests)

#### Fixes
- Fixed security tests to expect `NanaSQLiteValidationError`

---

### [1.1.0a3] - 2025-12-17

#### Documentation Improvements
- **Added usage notes for `table()` method**:
  - Added important usage notes section to README.md (English & Japanese)
  - Warning about creating multiple instances for the same table
  - Recommendation to use context managers
  - Best practices clarification
- **Improved docstrings**:
  - Added detailed notes to `NanaSQLite.table()` docstring
  - Added detailed notes to `AsyncNanaSQLite.table()` docstring
  - Added specific examples of deprecated and recommended patterns
- **Future improvement plans**:
  - Documented improvement proposals in `etc/future_plans/` directory
  - Duplicate instance detection warning feature (Proposal B)
  - Connection state check feature (Proposal B)
  - Shared cache mechanism (Proposal C - on hold)

#### Analysis & Investigation
- **Comprehensive investigation of table() functionality**:
  - Stress tests: All 7 tests passed
  - Edge case tests: 10 tests conducted
  - Concurrency tests: All 5 tests passed
  - **Issues found**: 2 (minor design limitations)
    1. Cache inconsistency with multiple instances for same table (addressed with documentation)
    2. Sub-instance access after close (addressed with documentation)
  - **Conclusion**: Ready for production use, no performance issues

---

### [1.1.0dev2] - 2025-12-16

#### Current Development Status
- Development version in progress
- Testing in progress (all 15 tests in `test_concurrent_table_writes.py` passing)

### [1.1.0dev1] - 2025-12-15

#### Added
- **Multi-table Support (`table()` method)**: Safely operate on multiple tables within the same database
  - Get an instance for another table with `db.table(table_name)`
  - **Shared connection and lock**: Multiple table instances share the same SQLite connection and thread lock
  - Thread-safe: Concurrent writes to different tables from multiple threads work safely
  - Memory efficient: Reuses connections to save resources
  - **Sync version**: `NanaSQLite.table(table_name)` → `NanaSQLite` instance
  - **Async version**: `await AsyncNanaSQLite.table(table_name)` → `AsyncNanaSQLite` instance
  - Cache isolation: Each table instance maintains independent in-memory cache

#### Internal Implementation Improvements
- **Enhanced thread safety**: Added `threading.RLock` to all database operations
  - Read (`_read_from_db`), write (`_write_to_db`), delete (`_delete_from_db`)
  - Query execution (`execute`, `execute_many`)
  - Transaction operations
- **Improved connection management**:
  - `_shared_connection` parameter for connection sharing
  - `_shared_lock` parameter for lock sharing
  - `_is_connection_owner` flag for connection ownership management
  - `close()` method only executed by connection owner

#### Tests
- **15 comprehensive test cases** (all passing):
  - Sync multi-table concurrent write tests (2 tables, multiple tables)
  - Async multi-table concurrent write tests (2 tables, multiple tables)
  - Stress test (1000 concurrent writes)
  - Cache isolation tests
  - Table switching tests
  - Edge case tests

#### Compatibility
- **Full backward compatibility**: No impact on existing code
- All new parameters are optional (internal use)

### [1.0.3rc7] - 2025-12-10

#### Added
- **Async Support (AsyncNanaSQLite)**: Complete async interface for async applications
  - `AsyncNanaSQLite` class: Provides async versions of all operations
  - **Dedicated ThreadPoolExecutor**: Configurable max_workers (default 5) for optimization
  - High-performance concurrent processing with `ThreadPoolExecutor`
  - Safe to use with async frameworks like FastAPI, aiohttp
  - Async dict-like interface: `await db.aget()`, `await db.aset()`, `await db.adelete()`
  - Async batch operations: `await db.batch_update()`, `await db.batch_delete()`
  - Async SQL execution: `await db.execute()`, `await db.query()`
  - Async context manager: `async with AsyncNanaSQLite(...) as db:`
  - Concurrent operations support: Multiple async operations can run concurrently
  - Automatic resource management: Thread pool auto-cleanup
- **Comprehensive test suite**: 100+ async test cases
  - Basic operations, concurrency, error handling, performance tests
  - All tests passing
- **Full backward compatibility**: Existing `NanaSQLite` class unchanged

#### Performance Improvements
- Prevents blocking in async apps, improving event loop responsiveness
- Dedicated thread pool enables highly efficient concurrent processing (configurable workers)
- Optimal performance with APSW + thread pool combination
- Tunable max_workers for high-load environments (5-50)

### [1.0.3rc6] - 2025-12-10

#### Added
- **`get_fresh(key, default=None)` method**: Read directly from DB, update cache, and return value
  - Useful for cache synchronization after direct DB changes via `execute()`
  - Uses `_read_from_db` directly to minimize overhead

### [1.0.3rc5] - 2025-12-10

#### Performance Improvements
- **`batch_update()` optimization**: 10-30% faster with `executemany`
- **`batch_delete()` optimization**: Faster bulk deletion with `executemany`
- **`__contains__()` optimization**: Lightweight EXISTS query (faster for large values)

#### IDE/Type Support Enhancements
- Added `from __future__ import annotations`
- Specific type annotations: `Dict[str, Any]`, `Set[str]`
- Clearer parameter types: `Optional[Tuple]`

#### Documentation
- Added cache consistency warning to `execute()` method
- Improved docstrings (Returns, Warning sections)

#### Bug Fixes
- Resolved Git merge conflicts (order_by regex validation)
- Fixed ReDoS vulnerability (switched to comma-split approach)

### [1.0.3rc4] - 2025-12-09

#### Added
- **22 new SQLite wrapper functions**
  - Schema management: `drop_table()`, `drop_index()`, `alter_table_add_column()`, `get_table_schema()`, `list_indexes()`
  - Data operations: `sql_insert()`, `sql_update()`, `sql_delete()`, `upsert()`, `count()`, `exists()`
  - Query extensions: `query_with_pagination()` (with offset/group_by support)
  - Utilities: `vacuum()`, `get_db_size()`, `export_table_to_dict()`, `import_from_dict_list()`, `get_last_insert_rowid()`, `pragma()`
  - Transactions: `begin_transaction()`, `commit()`, `rollback()`, `transaction()` context manager
- 35 new test cases (all passing)
- Complete backward compatibility maintained

### [1.0.3rc3] - 2025-12-09

#### Added
- **Pydantic compatibility**
  - `set_model()`, `get_model()` methods
  - Support for nested models and optional fields
- **Direct SQL execution**
  - `execute()`, `execute_many()`, `fetch_one()`, `fetch_all()` methods
  - SQL injection protection via parameter binding
- **SQLite wrapper functions**
  - `create_table()`, `create_index()`, `query()` methods
  - `table_exists()`, `list_tables()` helper functions
- 32 new test cases
- Updated English/Japanese documentation
- Async support consultation document

### [1.0.0] - 2025-12-09

#### Added
- Initial release
- Dict-like interface (`db["key"] = value`)
- Instant persistence to SQLite via APSW
- Lazy load (on-access) caching
- Bulk load (`bulk_load=True`) for startup loading
- Nested structure support (tested up to 30 levels)
- Performance optimizations (WAL, mmap, cache_size)
- Batch operations (`batch_update`, `batch_delete`)
- Context manager support
- Full dict method compatibility
- Type hints (PEP 561)
- Bilingual documentation (English/Japanese)
- GitHub Actions CI (Python 3.9-3.13, Ubuntu/Windows/macOS)
