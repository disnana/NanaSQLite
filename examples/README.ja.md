# NanaSQLite 例集（日本語）

このディレクトリには、NanaSQLite を使った実践的なサンプルが収められています。
下記は各サンプルの日本語による簡潔な説明と実行方法です。より詳しくは各ファイルのコメントや `docs/` を参照してください。

## 利用可能な例と実行方法

1. FastAPI 統合 (`fastapi_integration.py`)
   - 非同期版 `AsyncNanaSQLite` を利用したユーザー管理 API の例です。
   - 特長: 非同期処理、Pydantic による入力検証、CRUD、ページネーション。
   - 要件: `pip install fastapi uvicorn pydantic[email]`
   - 実行: `python fastapi_integration.py` → http://localhost:8000/docs

2. Flask 統合 (`flask_integration.py`)
   - 同期版 `NanaSQLite` を使った簡易ブログ API の例です。
   - 要件: `pip install flask`
   - 実行: `python flask_integration.py` → http://localhost:5000

3. Async デモ (`async_demo.py`)
   - NanaSQLite の非同期機能（並列操作、バッチ更新、SQL 実行など）を示すサンプル。
   - 実行: `python async_demo.py`

4. Pydantic デモ (`pydantic_demo.py`)
   - Pydantic モデルを使った入力検証と安全なシリアライズの例。
   - 要件: `pip install pydantic`
   - 実行: `python pydantic_demo.py`

5. Quart デモ（クリーン版）(`quart_demo_clean.py`)
   - Quart（非同期フレームワーク）と Tailwind CSS を使ったワンファイルの Todo アプリ例（ダークテーマ）。
   - 要件: `pip install quart hypercorn nanasqlite`
   - 実行: `python quart_demo_clean.py` → http://localhost:5000

---

## テストと検証

テストスクリプト `examples/test_examples.py` を使うと、各サンプルで示している NanaSQLite の基本パターンが動作するかを自動で検証できます。Pydantic や Quart がインストールされていない場合は、該当テストがスキップされます。

実行例:

```bash
python examples/test_examples.py
```

---

## 主要な設計パターン（日本語まとめ）

- 非同期パターン（FastAPI / Quart）
  - `AsyncNanaSQLite` をアプリのライフサイクルに結びつけて起動時に生成し、終了時にクローズします。例: `app.before_serving` / `app.after_serving` を利用。

- 同期パターン（Flask）
  - アプリコンテキストで `NanaSQLite` を再利用する（シングルトン）ことでコネクションの再利用を図ります。

- シリアライズと検証
  - 入力は保存前に検証（Pydantic 等）し、日時は ISO 文字列へ変換して保存する方針が安全です。

- ベストプラクティス（簡潔）
  1. リソースはコンテキストマネージャで自動クリーンアップする
  2. DB 接続は再利用する（シングルトン）
  3. 非同期フレームワークでは `AsyncNanaSQLite` を使う
  4. 入力は必ず検証する（Pydantic 推奨）
  5. アプリ終了時に DB を閉じる
