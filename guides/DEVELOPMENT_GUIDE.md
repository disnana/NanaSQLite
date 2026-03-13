# NanaSQLite Development Guide / 開発ガイド

This guide outlines the rules and best practices for maintaining and developing NanaSQLite.
このガイドは、NanaSQLiteのメンテナンスおよび開発のためのルールとベストプラクティスをまとめたものです。

## ⚙️ Environment Maintenance / 環境維持ルール

### 1. Synchronizing the Environment / 環境の同期
Whenever you switch branches or pull new changes, **always** run the following command to ensure your local installation matches the source code:
ブランチを切り替えたり、新しい変更をプルしたときは、**必ず**以下のコマンドを実行して、ローカルのインストール状態をソースコードに同期させてください。

```bash
# Install package in editable mode with dev tools (pytest, ruff, mypy, tox, etc.)
pip install -e .[dev] -U
```

> [!IMPORTANT]
> Failure to do this may lead to `ModuleNotFoundError` or test failures because the installed version of `nanasqlite` does not reflect your local changes.
> これを怠ると、インストールされている `nanasqlite` にローカルの変更が反映されず、`ModuleNotFoundError` やテスト失敗の原因になります。

### 2. Testing Before Committing / コミット前のテスト
Always run the full test suite before pushing any changes:
変更をプロジェクトに反映する前に、必ず全テストスイートを実行してください。

Windows環境では、以下のコマンドを推奨します。
```bash
pytest tests/ -v -n 4 --ignore=tests/test_benchmark.py --ignore=tests/test_async_benchmark.py
```

Linux/macOS環境では、以下のコマンドを推奨します。
```bash
pytest tests/ -v -n auto --ignore=tests/test_benchmark.py --ignore=tests/test_async_benchmark.py
```

You can also use tox (recommended CI parity):
toxでも実行できます（CI相当の環境での実行を推奨）:

```bash
# Linting
tox -e lint

# Type checking
tox -e type

# Run tests
tox -e test
```

## 🛠️ Coding Standards / コーディング規格

### 1. Bilingual Docstrings / 日英併記のDocstring
New features and complex logic should be documented in both Japanese (primary) and English (as a supplement where possible, or via clear naming).
新機能や複雑なロジックは、日本語（主）と英語（補助、または明確な命名による補完）の両方でドキュメント化されるべきです。

### 2. Security Validation / セキュリティ検証
When adding new SQL-related methods, always use `_validate_expression` to ensure protection against SQL injection and ReDoS.
SQLに関連する新しいメソッドを追加する場合は、必ず `_validate_expression` を使用して、SQLインジェクションやReDoSに対する保護を確保してください。

## 🚀 Release Flow / リリースフロー

1. Update version in `pyproject.toml` and `src/nanasqlite/__init__.py`.
2. Update `CHANGELOG.md` (Bilingual).
3. Ensure 100% test pass rate across all platforms via GitHub Actions.
