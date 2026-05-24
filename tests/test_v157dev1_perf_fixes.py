"""
NanaSQLite v1.5.7dev1 - パフォーマンス回帰修正テスト

以下の修正を検証する:
- PERF-30: フック無し __setitem__ で不要な old_value 取得を省略
- PERF-31: batch_get() の DB ヒット追跡を missing_keys のみに限定
- PERF-32: batch_get() のフルチャンク用プレースホルダーを事前計算
- PERF-33: AsyncNanaSQLite.abatch_get() の全件キャッシュ既知ホットパス
- PERF-34: load_all() のデフォルト unbounded キャッシュ一括投入
- PERF-35: memory_first=True の KVS CRUD メモリ優先モード
"""

from __future__ import annotations

import os
import tempfile
import time
from types import MethodType

import pytest

from nanasqlite import AsyncNanaSQLite, NanaSQLite
from nanasqlite.core import _BATCH_GET_CHUNK_SIZE, _BATCH_GET_FULL_PLACEHOLDERS


@pytest.fixture
def db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test_v157dev1_perf.db")


def test_setitem_without_hooks_skips_old_value_lookup(db_path):
    """
    PERF-30: フック無しの単体書き込みでは old_value が観測されないため、
    _get_raw() による余分なキャッシュ/DB確認を行わない。
    """
    with NanaSQLite(db_path) as db:
        calls = []

        def spy_get_raw(self, key, default=None):
            calls.append((key, default))
            return default

        db._get_raw = MethodType(spy_get_raw, db)

        db["k1"] = {"value": 1}
        db["k2"] = {"value": 2}

        assert calls == []
        assert db["k1"] == {"value": 1}
        assert db["k2"] == {"value": 2}


def test_setitem_with_hooks_keeps_old_value_for_success_hook(db_path):
    """
    PERF-30 regression: フック付きでは on_write_success の old_value 契約を維持する。
    """

    class RecordingHook:
        def __init__(self):
            self.events = []

        def before_write(self, db, key, value):
            return value

        def after_read(self, db, key, value):
            return value

        def before_delete(self, db, key):
            pass

        def on_write_success(self, db, key, value, old_value):
            self.events.append((key, value, old_value))

    hook = RecordingHook()
    with NanaSQLite(db_path) as db:
        db.add_hook(hook)
        db["k"] = "first"
        db["k"] = "second"

        assert hook.events == [
            ("k", "first", None),
            ("k", "second", "first"),
        ]
        assert db["k"] == "second"


def test_batch_get_mixed_cache_db_and_missing_keys(db_path):
    """
    PERF-31 regression: キャッシュヒットが多い batch_get() でも、DBから
    実際に見つかったキーだけを DB-hit として扱い、未存在キーだけを negative cache 化する。
    """
    with NanaSQLite(db_path) as db:
        db.batch_update({"cached": 1, "db_only": 2})
        assert db["cached"] == 1
        db.clear_cache()
        assert db["cached"] == 1  # cache hit

        result = db.batch_get(["cached", "db_only", "missing"])

        assert result == {"cached": 1, "db_only": 2}
        assert "missing" in db._absent_keys
        assert "db_only" not in db._absent_keys
        assert "cached" not in db._absent_keys


def test_batch_get_full_chunk_placeholder_is_precomputed():
    """
    PERF-32: フルチャンク用プレースホルダーは module import 時に一度だけ作る。
    """
    assert _BATCH_GET_CHUNK_SIZE == 900
    assert _BATCH_GET_FULL_PLACEHOLDERS.count("?") == _BATCH_GET_CHUNK_SIZE
    assert _BATCH_GET_FULL_PLACEHOLDERS.count(",") == _BATCH_GET_CHUNK_SIZE - 1


@pytest.mark.asyncio
async def test_async_batch_get_all_cache_known_skips_executor_path(db_path):
    """
    PERF-33: abatch_get() は全キーが unbounded キャッシュ上で既知なら、
    同期側 batch_get() へ渡さず即時に返す。
    """
    db = AsyncNanaSQLite(db_path)
    try:
        await db.abatch_update({"k1": 1, "k2": 2})
        assert await db.aget("missing", None) is None

        calls = []
        original_batch_get = db._db.batch_get

        def spy_batch_get(keys):
            calls.append(list(keys))
            return original_batch_get(keys)

        db._db.batch_get = spy_batch_get

        result = await db.abatch_get(["k1", "missing", "k2"])

        assert result == {"k1": 1, "k2": 2}
        assert calls == []
    finally:
        await db.close()


def test_load_all_default_unbounded_bulk_populates_without_cache_set(db_path):
    """
    PERF-34: サイズ制限なし unbounded キャッシュでは、load_all() が cache.set()
    を1件ずつ呼ばず、背後の dict をまとめて更新する。
    """
    with NanaSQLite(db_path) as setup_db:
        setup_db.batch_update({f"k{i}": i for i in range(5)})

    with NanaSQLite(db_path) as db:
        calls = []
        original_set = db._cache.set

        def spy_set(key, value):
            calls.append((key, value))
            original_set(key, value)

        db._cache.set = spy_set

        db.load_all()

        assert calls == []
        assert db.to_dict() == {f"k{i}": i for i in range(5)}


def test_memory_first_crud_uses_memory_before_flush(db_path):
    """
    PERF-35: memory_first=True では CRUD の真実をメモリに置き、
    SQLite への永続化はバックグラウンド flush / close に任せる。
    """
    with NanaSQLite(db_path, memory_first=True) as db:
        assert db._memory_first is True
        assert db._v2_mode is True
        assert db._v2_flush_mode == "time"
        assert db._all_loaded is True

        db["a"] = 1
        db["b"] = 2
        del db["a"]

        assert "a" not in db
        assert db.get("a") is None
        assert db["b"] == 2
        assert len(db) == 1
        assert db.keys() == ["b"]
        assert db.batch_get(["a", "b", "missing"]) == {"b": 2}

    with NanaSQLite(db_path) as reopened:
        assert "a" not in reopened
        assert reopened["b"] == 2


def test_memory_first_rejects_bounded_or_ttl_cache(db_path):
    """PERF-35: memory_first は全件メモリ保持が前提なので eviction 付きキャッシュを拒否する。"""
    from nanasqlite import CacheType
    from nanasqlite.exceptions import NanaSQLiteValidationError

    with pytest.raises(NanaSQLiteValidationError):
        NanaSQLite(db_path, memory_first=True, cache_size=10)

    with pytest.raises(NanaSQLiteValidationError):
        NanaSQLite(db_path, memory_first=True, cache_strategy=CacheType.LRU, cache_size=10)


def test_memory_first_clear_keeps_memory_truth_for_new_writes(db_path):
    """
    PERF-35 regression: clear() 後も memory_first の全件ロード済み状態を維持し、
    未 flush の新規書き込みを len()/keys()/batch_get() がメモリから見られるようにする。
    """
    with NanaSQLite(db_path, memory_first=True) as db:
        db.batch_update({"old": 1})
        db.clear()
        db["new"] = 2

        assert db._all_loaded is True
        assert len(db) == 1
        assert db.keys() == ["new"]
        assert db.batch_get(["old", "new"]) == {"new": 2}


def test_memory_first_time_flush_persists_without_close(db_path):
    """
    PERF-35: close() を待たなくても、変更があれば time flush で差分が永続化される。
    """
    with NanaSQLite(db_path, memory_first=True, memory_flush_interval=0.05) as db:
        db["timed"] = {"ok": True}

        deadline = time.time() + 2.0
        persisted = False
        while time.time() < deadline:
            with NanaSQLite(db_path) as reader:
                persisted = reader.get("timed") == {"ok": True}
            if persisted:
                break
            time.sleep(0.05)

        assert persisted is True


def test_memory_first_get_fresh_flushes_pending_delta(db_path):
    """
    PERF-35: get_fresh() は memory_first の pending delta を先に flush してから DB を読む。
    """
    with NanaSQLite(db_path, memory_first=True, flush_mode="manual") as db:
        db["fresh"] = "pending"

        assert db.get_fresh("fresh") == "pending"

        with NanaSQLite(db_path) as reader:
            assert reader["fresh"] == "pending"
