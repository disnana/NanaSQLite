import os
import sqlite3

import pytest
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from nanasqlite import AsyncNanaSQLite, NanaSQLite


def test_encryption_aes_gcm_default(tmp_path):
    """Test AES-GCM (default mode)."""
    db_path = str(tmp_path / "aes_gcm.db")
    key = AESGCM.generate_key(bit_length=256)

    with NanaSQLite(db_path, encryption_key=key) as db:
        db["data"] = {"msg": "hello gcm"}
        assert db["data"]["msg"] == "hello gcm"

    # Verify raw database content
    conn = sqlite3.connect(db_path)
    raw = conn.execute("SELECT value FROM data").fetchone()[0]
    conn.close()
    assert isinstance(raw, bytes)
    assert b"hello gcm" not in raw
    assert len(raw) > 28 # 12 (nonce) + len(json) + 16 (tag)

def test_encryption_fernet_mode(tmp_path):
    """Test Fernet mode."""
    db_path = str(tmp_path / "fernet.db")
    key = Fernet.generate_key()

    with NanaSQLite(db_path, encryption_key=key, encryption_mode="fernet") as db:
        db["data"] = "fernet secret"
        assert db["data"] == "fernet secret"

    # Verify it's actually Fernet (starts with gAAAA...)
    # Actually it's saved as bytes usually in our implementation if Fernet returns bytes
    conn = sqlite3.connect(db_path)
    raw = conn.execute("SELECT value FROM data").fetchone()[0]
    conn.close()
    assert raw.startswith(b"gAAAA")

def test_encryption_chacha20_mode(tmp_path):
    """Test ChaCha20-Poly1305 mode."""
    db_path = str(tmp_path / "chacha.db")
    key = ChaCha20Poly1305.generate_key()

    with NanaSQLite(db_path, encryption_key=key, encryption_mode="chacha20") as db:
        db["data"] = [1, 2, 3]
        assert db["data"] == [1, 2, 3]

def test_encryption_cross_mode_failure(tmp_path):
    """Verify that using the wrong mode for existing data fails."""
    db_path = str(tmp_path / "cross.db")
    key = os.urandom(32) # Suitable for both GCM and ChaCha

    with NanaSQLite(db_path, encryption_key=key, encryption_mode="aes-gcm") as db:
        db["k"] = "v"

    # Try reading with chacha
    with pytest.raises(Exception):
        with NanaSQLite(db_path, encryption_key=key, encryption_mode="chacha20") as db:
            _ = db["k"]

def test_encryption_wrong_key(tmp_path):
    """Verify that wrong key raises error."""
    db_path = str(tmp_path / "wrong.db")
    key1 = AESGCM.generate_key(bit_length=256)
    key2 = AESGCM.generate_key(bit_length=256)

    with NanaSQLite(db_path, encryption_key=key1) as db:
        db["k"] = "secure"

    with pytest.raises(Exception):
        with NanaSQLite(db_path, encryption_key=key2) as db:
            _ = db["k"]

@pytest.mark.asyncio
async def test_async_multi_mode_encryption(tmp_path):
    """Test various modes in AsyncNanaSQLite."""
    db_path = str(tmp_path / "async_multi.db")
    key = AESGCM.generate_key(bit_length=256)

    # AES-GCM (auto default)
    async with AsyncNanaSQLite(db_path, encryption_key=key) as db:
        await db.aset("a", "async gcm")
        assert await db.aget("a") == "async gcm"

    # ChaCha20
    db_path_cc = str(tmp_path / "async_chacha.db")
    key_cc = ChaCha20Poly1305.generate_key()
    async with AsyncNanaSQLite(db_path_cc, encryption_key=key_cc, encryption_mode="chacha20") as db:
        await db.aset("b", "async chacha")
        assert await db.aget("b") == "async chacha"

def test_encryption_unsupported_mode(tmp_path):
    """Verify that unsupported mode raises error."""
    with pytest.raises(ValueError):
        NanaSQLite(str(tmp_path / "err.db"), encryption_key=b"123", encryption_mode="invalid")
