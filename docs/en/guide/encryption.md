# Encryption Guide

NanaSQLite supports transparent data encryption since v1.3.1. Data is automatically encrypted on write and decrypted on read.

## Supported Encryption Modes

| Mode | Algorithm | Key Length | Characteristics |
|------|-----------|-----------|----------------|
| `aes-gcm` | AES-256-GCM | 32 bytes | **Default** — fast, authenticated encryption |
| `chacha20` | ChaCha20-Poly1305 | 32 bytes | Best for non-hardware-AES environments |
| `fernet` | Fernet (AES-CBC) | 32 bytes (base64) | Simple and secure default |

## Installation

```bash
pip install nanasqlite[encryption]
```

## Basic Usage

### AES-GCM (Default)

```python
import os
from nanasqlite import NanaSQLite

raw_key = os.urandom(32)

with NanaSQLite("secure.db", encryption_key=raw_key) as db:
    db["secret"] = {"password": "s3cret", "api_key": "abc123"}
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

## Key Management Best Practices

- Never hard-code keys in source code
- Never store encryption keys alongside the database
- Never commit keys to version control
- Use environment variables or secrets files

```python
import os
key = os.environ["NANASQLITE_KEY"].encode("utf-8")
```

## Error Handling

| Error | Cause |
|-------|-------|
| `ImportError` | `cryptography` is not installed |
| `NanaSQLiteDatabaseError` | Decryption failure (key mismatch or data corruption) |
| `ValueError` | Unsupported `encryption_mode` |
