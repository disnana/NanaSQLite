# 暗号化ガイド

NanaSQLite は v1.3.1 以降、透過的なデータ暗号化をサポートしています。データは保存時に自動的に暗号化され、読み取り時に自動的に復号されます。

## サポートされる暗号化モード

| モード | アルゴリズム | 鍵の長さ | 特徴 |
|--------|------------|---------|------|
| `aes-gcm` | AES-256-GCM | 32 バイト | **デフォルト** 高速・認証付き暗号化 |
| `chacha20` | ChaCha20-Poly1305 | 32 バイト | ハードウェア AES 非対応環境向き |
| `fernet` | Fernet (AES-CBC) | 32 バイト (base64) | シンプルで安全なデフォルト |

## インストール

暗号化機能を使用するには `cryptography` パッケージが必要です:

```bash
pip install nanasqlite[encryption]

# または全機能をインストール
pip install nanasqlite[all]
```

## 基本的な使い方

### AES-GCM（デフォルト）

最も高速で推奨される暗号化モードです:

```python
import os
import base64
from nanasqlite import NanaSQLite

# 32 バイトの暗号化キーを生成
raw_key = os.urandom(32)

with NanaSQLite("secure.db", encryption_key=raw_key) as db:
    # 通常通りデータを操作 — 暗号化/復号は自動
    db["secret"] = {"password": "s3cret", "api_key": "abc123"}
    
    data = db["secret"]
    print(data)  # {"password": "s3cret", "api_key": "abc123"}
```

### ChaCha20-Poly1305

ARM デバイスやハードウェア AES が利用できない環境で高速に動作します:

```python
import os
from nanasqlite import NanaSQLite

raw_key = os.urandom(32)

with NanaSQLite(
    "secure.db",
    encryption_key=raw_key,
    encryption_mode="chacha20",
) as db:
    db["data"] = {"sensitive": True}
```

### Fernet

シンプルな暗号化が必要な場合に適しています:

```python
from cryptography.fernet import Fernet
from nanasqlite import NanaSQLite

# Fernet キーを生成（base64 エンコード済み）
key = Fernet.generate_key()

with NanaSQLite(
    "secure.db",
    encryption_key=key,
    encryption_mode="fernet",
) as db:
    db["token"] = "sensitive-token-value"
```

## 暗号化の仕組み

### AES-GCM / ChaCha20-Poly1305

1. **書き込み時**: JSON シリアライズ → 12 バイトランダムノンス生成 → AEAD 暗号化 → `nonce + ciphertext` として保存
2. **読み取り時**: 最初の 12 バイトをノンスとして分離 → 残りを復号 → JSON デシリアライズ

```
保存フォーマット:
┌──────────┬─────────────────────────────┐
│ Nonce    │ Ciphertext + Auth Tag       │
│ (12B)    │ (可変長)                     │
└──────────┴─────────────────────────────┘
```

### Fernet

1. **書き込み時**: JSON シリアライズ → Fernet 暗号化（AES-CBC + HMAC）
2. **読み取り時**: Fernet 復号 → JSON デシリアライズ

## 暗号化モードの選択

```
ハードウェア AES 対応?
├─ Yes → aes-gcm（最速）
└─ No
   ├─ ARM/モバイル → chacha20
   └─ シンプルさ重視 → fernet
```

| 基準 | AES-GCM | ChaCha20 | Fernet |
|------|---------|----------|--------|
| 速度（x86） | ★★★★★ | ★★★★ | ★★★ |
| 速度（ARM） | ★★★ | ★★★★★ | ★★★ |
| セキュリティ | ★★★★★ | ★★★★★ | ★★★★ |
| シンプルさ | ★★★★ | ★★★★ | ★★★★★ |

## 鍵管理のベストプラクティス

### 鍵の生成

```python
import os
import base64

# AES-GCM / ChaCha20 用: 32 バイトのランダムキー
raw_key = os.urandom(32)

# Fernet 用: base64 エンコードされたキー
from cryptography.fernet import Fernet
fernet_key = Fernet.generate_key()
```

### 鍵の保管

::: danger 絶対にやってはいけないこと
- ソースコードに鍵をハードコードする
- 暗号化キーをデータベースと同じ場所に保存する
- バージョン管理システムに鍵をコミットする
:::

推奨される鍵の保管方法:

```python
import os

# 環境変数から読み込み
key = os.environ["NANASQLITE_KEY"].encode("utf-8")

# ファイルから読み込み
with open("/etc/secrets/db.key", "rb") as f:
    key = f.read()
```

## 非同期での暗号化利用

`AsyncNanaSQLite` でも同じ暗号化オプションが使用できます:

```python
import os
from nanasqlite import AsyncNanaSQLite

raw_key = os.urandom(32)

async def main():
    db = AsyncNanaSQLite(
        "secure.db",
        encryption_key=raw_key,
        encryption_mode="aes-gcm",
    )

    await db.aset("secret", {"api_key": "xyz789"})
    data = await db.aget("secret")

    db.close()
```

## 既存データベースの暗号化移行

既存の非暗号化データベースを暗号化データベースに移行するには:

```python
import os
from nanasqlite import NanaSQLite

# 1. 既存の非暗号化 DB を読み込み
with NanaSQLite("old.db", bulk_load=True) as old_db:
    all_data = old_db.to_dict()

# 2. 暗号化 DB に書き込み
raw_key = os.urandom(32)
with NanaSQLite("new_encrypted.db", encryption_key=raw_key) as new_db:
    new_db.batch_update(all_data)
```

::: warning 注意
暗号化モードや鍵を変更した場合、既存のデータは復号できなくなります。必ずバックアップを取得してから変更してください。
:::

## エラーハンドリング

```python
from nanasqlite import NanaSQLite, NanaSQLiteDatabaseError

try:
    with NanaSQLite("secure.db", encryption_key=wrong_key) as db:
        data = db["secret"]
except NanaSQLiteDatabaseError as e:
    # 復号失敗: 鍵が間違っているか、データが破損
    print(f"復号エラー: {e}")
```

暗号化関連の主なエラー:

| エラー | 原因 |
|--------|------|
| `ImportError` | `cryptography` がインストールされていない |
| `NanaSQLiteDatabaseError` | 復号失敗（鍵不一致・データ破損） |
| `ValueError` | サポートされていない `encryption_mode` |
