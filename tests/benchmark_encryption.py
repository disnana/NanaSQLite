import os
import tempfile
import pytest
import asyncio
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.fernet import Fernet
from nanasqlite import NanaSQLite, AsyncNanaSQLite

# Keys for benchmarking
AES_KEY = AESGCM.generate_key(bit_length=256)
CHACHA_KEY = ChaCha20Poly1305.generate_key()
FERNET_KEY = Fernet.generate_key()

SMALL_DATA = {"msg": "hello", "id": 1}
LARGE_DATA = {"data": "x" * 1024 * 10}  # 10KB

@pytest.fixture
def db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "bench_enc.db")

@pytest.fixture
def sync_dbs(db_path):
    plaintext = NanaSQLite(os.path.join(os.path.dirname(db_path), "plain.db"))
    aes = NanaSQLite(os.path.join(os.path.dirname(db_path), "aes.db"), encryption_key=AES_KEY)
    chacha = NanaSQLite(os.path.join(os.path.dirname(db_path), "chacha.db"), encryption_key=CHACHA_KEY, encryption_mode="chacha20")
    fernet = NanaSQLite(os.path.join(os.path.dirname(db_path), "fernet.db"), encryption_key=FERNET_KEY, encryption_mode="fernet")
    
    yield {
        "plaintext": plaintext,
        "aes-gcm": aes,
        "chacha20": chacha,
        "fernet": fernet
    }
    
    plaintext.close()
    aes.close()
    chacha.close()
    fernet.close()

class TestEncryptionSyncBenchmarks:
    @pytest.mark.parametrize("mode", ["plaintext", "aes-gcm", "chacha20", "fernet"])
    def test_write_small(self, benchmark, sync_dbs, mode):
        db = sync_dbs[mode]
        counter = [0]
        def write():
            db[f"k_{counter[0]}"] = SMALL_DATA
            counter[0] += 1
        benchmark(write)

    @pytest.mark.parametrize("mode", ["plaintext", "aes-gcm", "chacha20", "fernet"])
    def test_write_large(self, benchmark, sync_dbs, mode):
        db = sync_dbs[mode]
        counter = [0]
        def write():
            db[f"k_{counter[0]}"] = LARGE_DATA
            counter[0] += 1
        benchmark(write)

    @pytest.mark.parametrize("mode", ["plaintext", "aes-gcm", "chacha20", "fernet"])
    def test_read_uncached(self, benchmark, sync_dbs, mode):
        db = sync_dbs[mode]
        # Prev-fill
        db["bench_key"] = LARGE_DATA
        
        def read():
            db.refresh() # Force bypass cache
            return db["bench_key"]
        benchmark(read)

class TestEncryptionAsyncBenchmarks:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("mode", ["plaintext", "aes-gcm", "chacha20"])
    async def test_async_write_small(self, benchmark, db_path, mode):
        key = None
        enc_mode = "aes-gcm"
        if mode == "aes-gcm":
            key = AES_KEY
        elif mode == "chacha20":
            key = CHACHA_KEY
            enc_mode = "chacha20"
            
        async with AsyncNanaSQLite(db_path, encryption_key=key, encryption_mode=enc_mode) as db:
            counter = [0]
            async def write():
                await db.aset(f"k_{counter[0]}", SMALL_DATA)
                counter[0] += 1
            
            # Using benchmark.pedantic to handle async if possible or just normal wrapper if supported
            # Note: pytest-benchmark doesn't support async natively easily without wrapper
            def sync_wrapper():
                asyncio.run(db.aset(f"k_{counter[0]}", SMALL_DATA))
                counter[0] += 1
                
            benchmark(sync_wrapper)
