# NanaSQLite v1.5.0dev1: Ultimate Hooks サンプル集

NanaSQLite v1.5.0dev1で導入された、強力なフックおよび制約アーキテクチャ「Ultimate Hooks」のサンプルコード集です。
このディレクトリのスクリプトを実行することで、実際の動作を確認しながら新機能を学ぶことができます。

## ディレクトリ構成と学習内容

各スクリプトは独立して実行可能です。以下の順序で学習することをお勧めします。

### 1. 基礎を学ぶ
* **[`01_custom_hooks.py`](./01_custom_hooks.py)**
  - カスタムフックの基本（`NanaHook`プロトコルの実装）
  - データのライフサイクルへの介入（`before_write`, `after_read`, `before_delete`）
  - `add_hook()` を使った登録方法と、タイムスタンプ自動付与の具体例

### 2. データ整合性を保証する（標準制約）
* **[`02_standard_constraints.py`](./02_standard_constraints.py)**
  - `CheckHook`: コールバック関数による値の検証（RDBMSの`CHECK`制約相当）
  - `UniqueHook`: 指定フィールドの値の一意性保証（RDBMSの`UNIQUE`制約相当）
  - `ForeignKeyHook`: 他データモデルとの参照整合性保証（RDBMSの`FOREIGN KEY`制約相当）

### 3. 高度な外部ライブラリ連携
* **[`03_pydantic_integration.py`](./03_pydantic_integration.py)**
  - Python標準のデータ検証ライブラリ「Pydantic」との公式連携（`PydanticHook`）
  - Pydanticモデル（`BaseModel`）を使ったシリアライズ・デシリアライズの完全自動化
  - 厳格な型チェックとバリデーションルールの適用
* **[`04_validkit_integration.py`](./04_validkit_integration.py)**
  - NanaSQLite推奨の超高速バリデーションライブラリ「validkit-py」との連携（`ValidkitHook`）
  - `coerce=True` を使用したデータの自動型変換（例: 文字列の数値をintへパース）
  - レガシーAPI(`validator`パラメータ)との互換性・関係性

### 4. 非同期環境への適用
* **[`05_async_hooks.py`](./05_async_hooks.py)**
  - `AsyncNanaSQLite` に対するフックの登録と動作確認
  - スレッドプール（Executor）を活用した非同期安全性と、イベントループをブロックしない仕組み
  - 複数タスクによる並行動作時のフック挙動

## 実行方法

任意のスクリプトをPythonコマンドで実行してください。
※ 実行には `nanasqlite` パッケージが必要です。一部スクリプトでは `pydantic`, `validkit` などの外部ライブラリも必要になります。

```bash
# 基本的な実行例
python 01_custom_hooks.py

# Pydantic サンプルを実行する場合（要 pydantic インストール）
pip install pydantic email-validator
python 03_pydantic_integration.py

# Validkit サンプルを実行する場合（要 validkit インストール）
pip install validkit
python 04_validkit_integration.py
```
