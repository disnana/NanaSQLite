# Contributing to NanaSQLite / 開発への貢献

[日本語](#日本語) | [English](#english)

---

## 日本語

### 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/disnana/nanasqlite.git
cd nanasqlite

# 開発モードでインストール
pip install -e ".[dev]"

# テスト実行
pytest tests/ -v
```

### バージョン指定方法

バージョンは `src/nanasqlite/__init__.py` の `__version__` で管理します。

#### バージョン形式（PEP 440準拠）

| バージョン | 意味 | GitHub Release |
|-----------|------|----------------|
| `1.0.0` | 正式リリース | Release |
| `1.0.1a1` | Alpha版（テスト初期段階） | Pre-release |
| `1.0.1b1` | Beta版（機能完成、テスト中） | Pre-release |
| `1.0.1rc1` | Release Candidate（リリース候補） | Pre-release |
| `1.0.1dev` | 開発版（不安定） | Pre-release |

#### バージョン更新例

```python
# src/nanasqlite/__init__.py

# 開発中
__version__ = "1.1.0dev"

# Alpha版
__version__ = "1.1.0a1"

# Beta版
__version__ = "1.1.0b1"

# Release Candidate
__version__ = "1.1.0rc1"

# 正式リリース
__version__ = "1.1.0"
```

### リリースフロー

1. **機能開発** → `__version__ = "X.X.Xdev"`
2. **テスト段階** → `__version__ = "X.X.Xb1"` (Beta)
3. **最終確認** → `__version__ = "X.X.Xrc1"` (RC)
4. **正式リリース** → `__version__ = "X.X.X"`
5. **mainにpush** → 自動でPyPI公開 & GitHub Release作成

### 自動化の仕組み

mainブランチにpushすると：

1. バージョンをPyPIと比較
2. 異なる場合のみ処理続行
3. テスト実行（3 OS × Python 3.11）
4. パッケージビルド
5. PyPIに公開
6. GitHub Releaseを作成（プレリリースは自動判定）

### コーディング規約

- 型ヒントを使用
- docstringを記述（日本語OK）
- テストを追加

---

## English

### Development Setup

```bash
# Clone repository
git clone https://github.com/disnana/nanasqlite.git
cd nanasqlite

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

### Version Specification

Version is managed in `src/nanasqlite/__init__.py` via `__version__`.

#### Version Format (PEP 440)

| Version | Meaning | GitHub Release |
|---------|---------|----------------|
| `1.0.0` | Stable release | Release |
| `1.0.1a1` | Alpha (early testing) | Pre-release |
| `1.0.1b1` | Beta (feature complete, testing) | Pre-release |
| `1.0.1rc1` | Release Candidate | Pre-release |
| `1.0.1dev` | Development (unstable) | Pre-release |

#### Version Update Examples

```python
# src/nanasqlite/__init__.py

# During development
__version__ = "1.1.0dev"

# Alpha release
__version__ = "1.1.0a1"

# Beta release
__version__ = "1.1.0b1"

# Release Candidate
__version__ = "1.1.0rc1"

# Stable release
__version__ = "1.1.0"
```

### Release Flow

1. **Development** → `__version__ = "X.X.Xdev"`
2. **Testing** → `__version__ = "X.X.Xb1"` (Beta)
3. **Final check** → `__version__ = "X.X.Xrc1"` (RC)
4. **Stable release** → `__version__ = "X.X.X"`
5. **Push to main** → Auto-publish to PyPI & create GitHub Release

### Automation

When you push to main branch:

1. Compare version with PyPI
2. Continue only if different
3. Run tests (3 OS × Python 3.11)
4. Build package
5. Publish to PyPI
6. Create GitHub Release (prerelease auto-detected)

### Coding Guidelines

- Use type hints
- Write docstrings
- Add tests for new features
