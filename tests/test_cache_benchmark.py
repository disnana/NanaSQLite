"""
Benchmark tests for cache strategies (v1.3.0).

Run with: pytest tests/test_cache_benchmark.py -v --benchmark-only
"""

import importlib.util

import pytest

from nanasqlite import CacheType, NanaSQLite

# pytest-benchmarkがインストールされているか確認
pytest_benchmark_available = importlib.util.find_spec("pytest_benchmark") is not None


@pytest.fixture
def db_unbounded(tmp_path):
    db_path = tmp_path / "bench_unbounded.db"
    with NanaSQLite(str(db_path), cache_strategy=CacheType.UNBOUNDED) as db:
        yield db


@pytest.fixture
def db_lru(tmp_path):
    db_path = tmp_path / "bench_lru.db"
    with NanaSQLite(str(db_path), cache_strategy=CacheType.LRU, cache_size=1000) as db:
        yield db


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestCacheBenchmarks:
    """Benchmark cache performance."""

    def test_unbounded_write_1000(self, db_unbounded, benchmark):
        """Benchmark: Write 1000 items with unbounded cache."""

        def write():
            for i in range(1000):
                db_unbounded[f"key_{i}"] = {"value": i}

        benchmark(write)

    def test_lru_write_1000(self, db_lru, benchmark):
        """Benchmark: Write 1000 items with LRU cache (size=1000)."""

        def write():
            for i in range(1000):
                db_lru[f"key_{i}"] = {"value": i}

        benchmark(write)

    def test_unbounded_read_cached(self, db_unbounded, benchmark):
        """Benchmark: Read cached items (unbounded)."""
        # Setup
        for i in range(100):
            db_unbounded[f"key_{i}"] = {"value": i}

        def read():
            for i in range(100):
                _ = db_unbounded[f"key_{i}"]

        benchmark(read)

    def test_lru_read_cached(self, db_lru, benchmark):
        """Benchmark: Read cached items (LRU)."""
        # Setup
        for i in range(100):
            db_lru[f"key_{i}"] = {"value": i}

        def read():
            for i in range(100):
                _ = db_lru[f"key_{i}"]

        benchmark(read)

    def test_lru_eviction_overhead(self, tmp_path, benchmark):
        """Benchmark: LRU eviction overhead when cache is always full."""
        db_path = tmp_path / "eviction.db"
        with NanaSQLite(str(db_path), cache_strategy=CacheType.LRU, cache_size=10) as db:
            # Fill cache
            for i in range(10):
                db[f"init_{i}"] = i

            # Benchmark: Every write causes eviction
            def eviction_writes():
                for i in range(100):
                    db[f"new_{i}"] = i

            benchmark(eviction_writes)
