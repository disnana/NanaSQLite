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
