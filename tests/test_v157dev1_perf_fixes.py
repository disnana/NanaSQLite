"""
NanaSQLite v1.5.7dev1 - パフォーマンス回帰修正テスト

以下の修正を検証する:
- PERF-30: フック無し __setitem__ で不要な old_value 取得を省略
- PERF-31: batch_get() の DB ヒット追跡を missing_keys のみに限定
- PERF-32: batch_get() のフルチャンク用プレースホルダーを事前計算
- PERF-33: AsyncNanaSQLite.abatch_get() の全件キャッシュ既知ホットパス
- PERF-34: load_all() のデフォルト unbounded キャッシュ一括投入
"""

from __future__ import annotations

import os
import tempfile
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
    db = NanaSQLite(db_path)
    try:
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
    finally:
        db.close()


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

    db = NanaSQLite(db_path)
    hook = RecordingHook()
    db.add_hook(hook)
    try:
        db["k"] = "first"
        db["k"] = "second"

        assert hook.events == [
            ("k", "first", None),
            ("k", "second", "first"),
        ]
        assert db["k"] == "second"
    finally:
        db.close()


def test_batch_get_mixed_cache_db_and_missing_keys(db_path):
    """
    PERF-31 regression: キャッシュヒットが多い batch_get() でも、DBから
    実際に見つかったキーだけを DB-hit として扱い、未存在キーだけを negative cache 化する。
    """
    db = NanaSQLite(db_path)
    try:
        db.batch_update({"cached": 1, "db_only": 2})
        assert db["cached"] == 1
        db.clear_cache()
        assert db["cached"] == 1  # cache hit

        result = db.batch_get(["cached", "db_only", "missing"])

        assert result == {"cached": 1, "db_only": 2}
        assert "missing" in db._absent_keys
        assert "db_only" not in db._absent_keys
        assert "cached" not in db._absent_keys
    finally:
        db.close()


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
    setup_db = NanaSQLite(db_path)
    try:
        setup_db.batch_update({f"k{i}": i for i in range(5)})
    finally:
        setup_db.close()

    db = NanaSQLite(db_path)
    try:
        calls = []
        original_set = db._cache.set

        def spy_set(key, value):
            calls.append((key, value))
            original_set(key, value)

        db._cache.set = spy_set

        db.load_all()

        assert calls == []
        assert db.to_dict() == {f"k{i}": i for i in range(5)}
    finally:
        db.close()
