# NanaSQLite

[![PyPI version](https://badge.fury.io/py/nanasqlite.svg)](https://badge.fury.io/py/nanasqlite)
[![Tests](https://github.com/disnana/nanasqlite/actions/workflows/test.yml/badge.svg)](https://github.com/disnana/nanasqlite/actions/workflows/test.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A dict-like SQLite wrapper with instant persistence and intelligent caching.**

[English](#english) | [日本語](#日本語)

---

## English

### 🚀 Features

- **Dict-like Interface**: Use familiar `db["key"] = value` syntax
- **Instant Persistence**: All writes are immediately saved to SQLite
- **Smart Caching**: Lazy load (on-access) or bulk load (all at once)
- **Nested Structures**: Full support for nested dicts and lists (up to 30+ levels)
- **High Performance**: WAL mode, mmap, and batch operations for maximum speed
- **Zero Configuration**: Works out of the box with sensible defaults

### 📦 Installation

```bash
pip install nanasqlite
```

### ⚡ Quick Start

```python
from nanasqlite import NanaSQLite

# Create or open a database
db = NanaSQLite("mydata.db")

# Use it like a dict
db["user"] = {"name": "Nana", "age": 20, "tags": ["admin", "active"]}
print(db["user"])  # {'name': 'Nana', 'age': 20, 'tags': ['admin', 'active']}

# Data persists automatically
db.close()

# Reopen later - data is still there!
db = NanaSQLite("mydata.db")
print(db["user"]["name"])  # 'Nana'
```

### 🔧 Advanced Usage

```python
# Bulk load for faster repeated access
db = NanaSQLite("mydata.db", bulk_load=True)

# Batch operations for high-speed writes
db.batch_update({
    "key1": "value1",
    "key2": "value2",
    "key3": {"nested": "data"}
})

# Context manager support
with NanaSQLite("mydata.db") as db:
    db["temp"] = "value"
```

### 📚 Documentation

- [English Documentation](docs/en/README.md)
- [API Reference](docs/en/reference.md)

---

## 日本語

### 🚀 特徴

- **dict風インターフェース**: おなじみの `db["key"] = value` 構文で操作
- **即時永続化**: 書き込みは即座にSQLiteに保存
- **スマートキャッシュ**: 遅延ロード（アクセス時）または一括ロード（起動時）
- **ネスト構造対応**: 30階層以上のネストしたdict/listをサポート
- **高性能**: WALモード、mmap、バッチ操作で最高速度を実現
- **設定不要**: 合理的なデフォルト設定でそのまま動作

### 📦 インストール

```bash
pip install nanasqlite
```

### ⚡ クイックスタート

```python
from nanasqlite import NanaSQLite

# データベースを作成または開く
db = NanaSQLite("mydata.db")

# dictのように使う
db["user"] = {"name": "Nana", "age": 20, "tags": ["admin", "active"]}
print(db["user"])  # {'name': 'Nana', 'age': 20, 'tags': ['admin', 'active']}

# データは自動的に永続化
db.close()

# 後で再度開いても、データはそのまま！
db = NanaSQLite("mydata.db")
print(db["user"]["name"])  # 'Nana'
```

### 🔧 高度な使い方

```python
# 一括ロードで繰り返しアクセスを高速化
db = NanaSQLite("mydata.db", bulk_load=True)

# バッチ操作で高速書き込み
db.batch_update({
    "key1": "value1",
    "key2": "value2",
    "key3": {"nested": "data"}
})

# コンテキストマネージャ対応
with NanaSQLite("mydata.db") as db:
    db["temp"] = "value"
```

### 📚 ドキュメント

- [日本語ドキュメント](docs/ja/README.md)
- [APIリファレンス](docs/ja/reference.md)

---

## License

MIT License - see [LICENSE](LICENSE) for details.
