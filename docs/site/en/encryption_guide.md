# Encryption Guide

NanaSQLite supports transparent data encryption since v1.3.1. Data is automatically encrypted on write and decrypted on read.

## Supported Encryption Modes

| Mode | Algorithm | Key Length | Characteristics |
|------|-----------|-----------|----------------|
| `aes-gcm` | AES-256-GCM | 32 bytes | **Default** — fast, authenticated encryption |
| `chacha20` | ChaCha20-Poly1305 | 32 bytes | Best for non-hardware-AES environments |
| `fernet` | Fernet (AES-CBC) | 32 bytes (base64) | Simple and secure default |

## Installation

The `cryptography` package is required for encryption:

```bash
pip install nanasqlite[encryption]

# Or install everything
pip install nanasqlite[all]
```

## Basic Usage

### AES-GCM (Default)

The fastest and recommended encryption mode:

```python
import os
from nanasqlite import NanaSQLite

# Generate a 32-byte encryption key
raw_key = os.urandom(32)

with NanaSQLite("secure.db", encryption_key=raw_key) as db:
    # Use as normal — encryption/decryption is automatic
    db["secret"] = {"password": "s3cret", "api_key": "abc123"}
    
    data = db["secret"]
    print(data)  # {"password": "s3cret", "api_key": "abc123"}
```

### ChaCha20-Poly1305

Performs well on ARM devices and environments without hardware AES support:

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

Suitable when you need straightforward encryption:

```python
from cryptography.fernet import Fernet
from nanasqlite import NanaSQLite

# Generate a Fernet key (base64-encoded)
key = Fernet.generate_key()

with NanaSQLite(
    "secure.db",
    encryption_key=key,
    encryption_mode="fernet",
) as db:
    db["token"] = "sensitive-token-value"
```

## How Encryption Works

### AES-GCM / ChaCha20-Poly1305

1. **On write**: JSON serialize → generate 12-byte random nonce → AEAD encrypt → store as `nonce + ciphertext`
2. **On read**: Split first 12 bytes as nonce → decrypt remainder → JSON deserialize

```
Storage format:
┌──────────┬─────────────────────────────┐
│ Nonce    │ Ciphertext + Auth Tag       │
│ (12B)    │ (variable length)           │
└──────────┴─────────────────────────────┘
```

### Fernet

1. **On write**: JSON serialize → Fernet encrypt (AES-CBC + HMAC)
2. **On read**: Fernet decrypt → JSON deserialize

## Choosing an Encryption Mode

```
Hardware AES available?
├─ Yes → aes-gcm (fastest)
└─ No
   ├─ ARM / mobile → chacha20
   └─ Simplicity preferred → fernet
```

| Criterion | AES-GCM | ChaCha20 | Fernet |
|-----------|---------|----------|--------|
| Speed (x86) | ★★★★★ | ★★★★ | ★★★ |
| Speed (ARM) | ★★★ | ★★★★★ | ★★★ |
| Security | ★★★★★ | ★★★★★ | ★★★★ |
| Simplicity | ★★★★ | ★★★★ | ★★★★★ |

## Key Management Best Practices

### Generating Keys

```python
import os

# For AES-GCM / ChaCha20: 32-byte random key
raw_key = os.urandom(32)

# For Fernet: base64-encoded key
from cryptography.fernet import Fernet
fernet_key = Fernet.generate_key()
```

### Storing Keys

::: danger Never Do This
- Hard-code keys in source code
- Store encryption keys alongside the database
- Commit keys to version control
:::

Recommended key storage:

```python
import os

# Read from environment variable
key = os.environ["NANASQLITE_KEY"].encode("utf-8")

# Read from a secrets file
with open("/etc/secrets/db.key", "rb") as f:
    key = f.read()
```

## Async Encryption Usage

The same encryption options work with `AsyncNanaSQLite`:

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

## Migrating an Existing Database to Encryption

To migrate an existing unencrypted database to an encrypted one:

```python
import os
from nanasqlite import NanaSQLite

# 1. Read all data from the unencrypted DB
with NanaSQLite("old.db", bulk_load=True) as old_db:
    all_data = old_db.to_dict()

# 2. Write to a new encrypted DB
raw_key = os.urandom(32)
with NanaSQLite("new_encrypted.db", encryption_key=raw_key) as new_db:
    new_db.batch_update(all_data)
```

::: warning Caution
If you change the encryption mode or key, existing data becomes unreadable. Always create a backup before making changes.
:::

## Error Handling

```python
from nanasqlite import NanaSQLite, NanaSQLiteDatabaseError

try:
    with NanaSQLite("secure.db", encryption_key=wrong_key) as db:
        data = db["secret"]
except NanaSQLiteDatabaseError as e:
    # Decryption failed: wrong key or corrupted data
    print(f"Decryption error: {e}")
```

Common encryption-related errors:

| Error | Cause |
|-------|-------|
| `ImportError` | `cryptography` is not installed |
| `NanaSQLiteDatabaseError` | Decryption failure (key mismatch or data corruption) |
| `ValueError` | Unsupported `encryption_mode` |
