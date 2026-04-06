"""
NanaSQLite v1.5.2 - 追加パフォーマンス回帰テスト

PERF-06: Unbounded キャッシュの read / contains ホットパス最適化
"""

from __future__ import annotations

import os
import tempfile

import pytest

from nanasqlite import NanaSQLite


@pytest.fixture
def db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test_v152_perf.db")


def test_unbounded_getitem_and_get_use_data_first(db_path):
    """
    Unbounded モードでキャッシュヒット時は known-absent セットを見に行かず、
    _data だけで即時に値取得できることを確認する。

    注: このテストは公開API仕様ではなく、v1.5.2 の内部 fast-path
    最適化（実装詳細）を固定化する目的で内部状態を直接操作する。
    """
    db = NanaSQLite(db_path)
    try:
        db["k1"] = {"v": 1}
        # _absent_keys を意図的に壊しても、_data 優先なら読み出せる
        db._absent_keys.add("k1")

        assert db["k1"] == {"v": 1}
        assert db.get("k1") == {"v": 1}
    finally:
        db.close()


def test_unbounded_contains_and_missing_semantics_preserved(db_path):
    """
    最適化後も既知の不在キー判定と通常の contains/get 挙動が保持されることを確認。
    """
    db = NanaSQLite(db_path)
    try:
        db["present"] = 123
        assert "present" in db
        assert db.get("present") == 123

        # 1回目の contains で negative cache 化される
        assert "missing" not in db
        assert "missing" in db._absent_keys
        assert db.get("missing", "d") == "d"
        with pytest.raises(KeyError):
            _ = db["missing"]
    finally:
        db.close()


def test_unbounded_delete_paths_keep_known_absent_metadata_consistent(db_path):
    """
    Verify known-absent metadata is consistently updated after delete APIs
    in unbounded mode.
    """
    db = NanaSQLite(db_path)
    try:
        db["k1"] = "v1"
        db["k2"] = "v2"
        db["k3"] = "v3"

        popped = db.pop("k1")
        assert popped == "v1"
        db.batch_delete(["k2", "k3"])

        assert "k1" in db._absent_keys
        assert "k2" in db._absent_keys
        assert "k3" in db._absent_keys
        assert db.get("k1", "d") == "d"
        assert db.get("k2", "d") == "d"
        assert db.get("k3", "d") == "d"
    finally:
        db.close()


def test_unbounded_update_cache_clears_stale_absent_marker_with_cache_size(db_path):
    """
    In unbounded mode with cache_size (self._use_cache_set=True), cache updates must
    clear stale known-absent markers.
    """
    db = NanaSQLite(db_path, cache_size=2)
    try:
        db._absent_keys.add("k1")
        db._update_cache("k1", "v1")
        assert "k1" not in db._absent_keys
        assert db.get("k1") == "v1"
    finally:
        db.close()


def test_unbounded_batch_get_db_hit_discards_absent_marker(db_path):
    """
    batch_get() DB-hit path should discard _absent_keys markers in unbounded mode.
    """
    class _AlwaysMissSet(set):
        def __contains__(self, key):
            # Force DB query path while retaining marker storage behavior.
            return False

    db = NanaSQLite(db_path)
    try:
        db._write_to_db("revived", "v")
        spy_absent = _AlwaysMissSet(["revived"])
        db._absent_keys = spy_absent

        result = db.batch_get(["revived"])
        assert result["revived"] == "v"
        assert "revived" not in spy_absent
        assert len(spy_absent) == 0
        assert db.get("revived") == "v"
    finally:
        db.close()
