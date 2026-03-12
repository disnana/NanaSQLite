# 暗号化ガイド

NanaSQLite は v1.3.1 以降、透過的なデータ暗号化をサポートしています。

## サポートされる暗号化モード

| モード | アルゴリズム | 鍵の長さ | 特徴 |
|--------|------------|---------|------|
| `aes-gcm` | AES-256-GCM | 32 バイト | **デフォルト** 高速・認証付き暗号化 |
| `chacha20` | ChaCha20-Poly1305 | 32 バイト | ハードウェア AES 非対応環境向き |
| `fernet` | Fernet (AES-CBC) | 32 バイト (base64) | シンプルで安全 |

## インストール

```bash
pip install nanasqlite[encryption]
```

## 基本的な使い方

### AES-GCM（デフォルト）

```python
import os
from nanasqlite import NanaSQLite

raw_key = os.urandom(32)

with NanaSQLite("secure.db", encryption_key=raw_key) as db:
    db["secret"] = {"password": "s3cret"}
    data = db["secret"]
```

### ChaCha20-Poly1305

```python
import os
from nanasqlite import NanaSQLite

raw_key = os.urandom(32)

with NanaSQLite("secure.db", encryption_key=raw_key, encryption_mode="chacha20") as db:
    db["data"] = {"sensitive": True}
```

### Fernet

```python
from cryptography.fernet import Fernet
from nanasqlite import NanaSQLite

key = Fernet.generate_key()

with NanaSQLite("secure.db", encryption_key=key, encryption_mode="fernet") as db:
    db["token"] = "sensitive-token-value"
```

## 鍵管理のベストプラクティス

- ソースコードに鍵をハードコードしない
- 暗号化キーをデータベースと同じ場所に保存しない
- バージョン管理に鍵をコミットしない
- 環境変数やシークレットファイルを使用する

```python
import os
key = os.environ["NANASQLITE_KEY"].encode("utf-8")
```

## エラー

| エラー | 原因 |
|--------|------|
| `ImportError` | `cryptography` がインストールされていない |
| `NanaSQLiteDatabaseError` | 復号失敗（鍵不一致・データ破損） |
| `ValueError` | サポートされていない `encryption_mode` |
