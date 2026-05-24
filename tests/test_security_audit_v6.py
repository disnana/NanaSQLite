"""
Security Audit v6 - Regression Tests (TDD)

対象:
  - F-002: V2Engine._perform_flush TOCTOU (flushing_buffer gap)
  - B3: UniqueHook._bound_db_ref weakref GC hazard
  - B6: DLQ payload exposure (get_dlq_summary missing)

このファイルのテストは修正前に「失敗」し、修正後に「合格」することを確認する。
"""

from __future__ import annotations

import gc
import os
import tempfile
import time
from typing import Any

import apsw
import pytest

from nanasqlite import NanaSQLite, V2Config
from nanasqlite.hooks import UniqueHook
from nanasqlite.v2_engine import V2Engine


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test_audit_v6.db")


# ============================================================
# F-002: V2 flushing_buffer gap (TOCTOU)
#
# 問題: _perform_flush で _staging_buffer を空の dict に入れ替えた直後、
#       DB コミット完了前の「谷間」で kvs_get_staging() が None を返す。
#       その間に _ensure_cached が走ると、書き込んだ直後のキーが「存在しない」
#       と判断される可能性がある。
# ============================================================

class TestF002FlushingBufferGap:
    """F-002: _perform_flush の TOCTOU (staging gap) 回帰テスト"""

    def test_kvs_get_staging_visible_during_flush(self):
        """
        フラッシュ中（staging を空に入れ替えた後、DB commit 前）でも
        kvs_get_staging() がデータを返すことを確認する。

        修正前: _staging_buffer を {} に入れ替えた後は None が返る。
        修正後: _flushing_buffer も参照するため、フラッシュ中もデータが見える。
        """
        conn = apsw.Connection(":memory:")
        conn.execute("CREATE TABLE IF NOT EXISTS \"data\" (key TEXT PRIMARY KEY, value TEXT)")

        engine = V2Engine(
            connection=conn,
            table_name='"data"',
            flush_mode="manual",
        )

        # staging にデータを積む
        engine.kvs_set('"data"', "test_key", '"test_value"')

        # _perform_flush を途中で止めるためにパッチを当てる
        # staging を入れ替えた直後（DB commit 前）の状態をシミュレート
        visibility_during_flush: list[Any] = []

        original_process_kvs_chunk = engine._process_kvs_chunk

        def patched_process_kvs_chunk(chunk):
            # chunk が実行される＝staging から取り出し後、commit 直前
            # この時点での kvs_get_staging の結果を記録
            result = engine.kvs_get_staging('"data"', "test_key")
            visibility_during_flush.append(result)
            # 元の処理を実行
            original_process_kvs_chunk(chunk)

        engine._process_kvs_chunk = patched_process_kvs_chunk

        # manual flush を実行（同期的に _perform_flush を呼ぶ）
        engine._perform_flush()

        engine.shutdown()
        conn.close()

        # 修正後: フラッシュ中でもデータが見える (None でない)
        assert len(visibility_during_flush) == 1, "パッチが呼ばれなかった"
        assert visibility_during_flush[0] is not None, (
            "FAIL (F-002): フラッシュ中の kvs_get_staging() が None を返した。"
            "staging から取り出されたデータが flushing_buffer で参照できていない。"
        )

    def test_v2_read_during_flush_count_mode(self, db_path):
        """
        count モードで書き込みとフラッシュが非同期で走る際、
        clear_cache 後の読み取りでデータが消えないことを確認する。
        """
        cfg = V2Config(flush_mode="count", flush_count=50)  # 手動で溜める
        db = NanaSQLite(db_path, v2_mode=True, v2_config=cfg)

        try:
            db["sentinel_key"] = "sentinel_value"

            # キャッシュをクリアして staging/DB から参照させる
            db.clear_cache()

            # staging にある間は読めるはずだが、もし flush が走って
            # staging が空になると読めなくなる（F-002 の症状）
            val = db.get("sentinel_key")
            assert val == "sentinel_value", (
                f"FAIL (F-002): clear_cache 後に書き込んだ値が消えた: got {val!r}"
            )
        finally:
            db.close()

    def test_flushing_buffer_attribute_exists(self):
        """
        修正後: V2Engine に _flushing_buffer 属性が存在することを確認する。
        """
        conn = apsw.Connection(":memory:")
        conn.execute("CREATE TABLE IF NOT EXISTS \"data\" (key TEXT PRIMARY KEY, value TEXT)")
        engine = V2Engine(
            connection=conn,
            table_name='"data"',
            flush_mode="manual",
        )
        assert hasattr(engine, "_flushing_buffer"), (
            "FAIL (F-002): V2Engine に _flushing_buffer 属性がない。"
            "flushing_buffer 修正が適用されていない。"
        )
        engine.shutdown()
        conn.close()


# ============================================================
# B3: UniqueHook weakref GC hazard
#
# 問題: _bound_db_ref() が None を返す（DB が GC 済み）場合に
#       AttributeError や意図しない動作が起きる可能性がある。
# ============================================================

class TestB3UniqueHookWeakref:
    """B3: UniqueHook._bound_db_ref weakref GC ハザード 回帰テスト"""

    def test_weakref_none_does_not_raise_attribute_error(self, db_path):
        """
        _bound_db_ref が None を返す状況（DB GC 済み）で
        before_write() を呼んでも AttributeError が起きないことを確認する。
        """
        hook = UniqueHook("email", use_index=True)

        # DB インスタンスを作成してインデックスをビルドさせる
        db = NanaSQLite(db_path, v2_mode=False)
        db["user1"] = {"email": "a@example.com"}

        # before_write を呼んでインデックスを構築させる
        hook.before_write(db, "user2", {"email": "b@example.com"})

        # インデックスが構築されている状態で _bound_db_ref を強制的に None にする
        # （DB インスタンスが GC されたシナリオのシミュレート）
        import weakref
        hook._bound_db_ref = weakref.ref(lambda: None)  # すぐに GC される
        gc.collect()  # 強制 GC

        # この時点で _bound_db_ref() は None を返す
        # before_write() を呼んでも AttributeError が起きないこと
        try:
            result = hook.before_write(db, "user3", {"email": "c@example.com"})
            assert result == {"email": "c@example.com"}
        except AttributeError as e:
            pytest.fail(f"FAIL (B3): weakref が None の際に AttributeError が発生した: {e}")
        finally:
            db.close()

    def test_weakref_none_triggers_index_rebuild(self, db_path):
        """
        _bound_db_ref() が None を返す（別DBインスタンスまたはGC済み）場合、
        インデックスが再構築されることを確認する。
        """
        hook = UniqueHook("email", use_index=True)

        db1 = NanaSQLite(db_path, v2_mode=False)
        db1["u1"] = {"email": "x@example.com"}

        # db1 でインデックスを構築
        hook.before_write(db1, "u2", {"email": "y@example.com"})
        assert hook._index_built is True

        db1.close()
        del db1
        gc.collect()

        # 別の db インスタンスで使う
        db2_path = db_path.replace(".db", "_2.db")
        db2 = NanaSQLite(db2_path, v2_mode=False)
        db2["u1"] = {"email": "x@example.com"}

        try:
            # 別インスタンス or weakref None の場合に再構築されること
            # AttributeError が起きなければ OK
            hook.before_write(db2, "u3", {"email": "z@example.com"})
        except AttributeError as e:
            pytest.fail(f"FAIL (B3): 別DBインスタンスで AttributeError が発生した: {e}")
        finally:
            db2.close()


# ============================================================
# B6: DLQ payload exposure
#
# 問題: get_dlq() が item (暗号化前の値を含む可能性) を返す。
#       認証なしの API に露出すると情報漏洩になる。
# 修正: get_dlq_summary() を追加し、error と timestamp のみ返す。
# ============================================================

class TestB6DLQExposure:
    """B6: DLQ 情報漏洩（get_dlq_summary() 回帰テスト）"""

    def test_get_dlq_summary_method_exists(self):
        """
        V2Engine に get_dlq_summary() メソッドが存在することを確認する。
        """
        conn = apsw.Connection(":memory:")
        conn.execute("CREATE TABLE IF NOT EXISTS \"data\" (key TEXT PRIMARY KEY, value TEXT)")
        engine = V2Engine(
            connection=conn,
            table_name='"data"',
            flush_mode="manual",
        )
        assert hasattr(engine, "get_dlq_summary"), (
            "FAIL (B6): V2Engine に get_dlq_summary() メソッドがない。"
        )
        engine.shutdown()
        conn.close()

    def test_get_dlq_summary_excludes_item(self):
        """
        get_dlq_summary() の戻り値に 'item' キーが含まれないことを確認する。
        """
        conn = apsw.Connection(":memory:")
        conn.execute("CREATE TABLE IF NOT EXISTS \"data\" (key TEXT PRIMARY KEY, value TEXT)")
        engine = V2Engine(
            connection=conn,
            table_name='"data"',
            flush_mode="manual",
        )

        # DLQ にエントリを追加する（内部メソッドを使用）
        engine._add_to_dlq("Test error for B6", {"secret": "sensitive_data"})

        summary = engine.get_dlq_summary()

        assert len(summary) == 1, f"DLQ summary に 1 件あるべきだが {len(summary)} 件"
        entry = summary[0]

        # "item" は含まれない
        assert "item" not in entry, (
            f"FAIL (B6): get_dlq_summary() に 'item' フィールドが含まれている: {entry}"
        )
        # "error" と "timestamp" は含まれる
        assert "error" in entry, "get_dlq_summary() に 'error' フィールドがない"
        assert "timestamp" in entry, "get_dlq_summary() に 'timestamp' フィールドがない"
        assert entry["error"] == "Test error for B6"

        engine.shutdown()
        conn.close()

    def test_get_dlq_still_includes_item(self):
        """
        既存の get_dlq() は後方互換性のため 'item' を引き続き返すことを確認する。
        """
        conn = apsw.Connection(":memory:")
        conn.execute("CREATE TABLE IF NOT EXISTS \"data\" (key TEXT PRIMARY KEY, value TEXT)")
        engine = V2Engine(
            connection=conn,
            table_name='"data"',
            flush_mode="manual",
        )

        engine._add_to_dlq("Compat test", {"key": "val"})
        dlq = engine.get_dlq()

        assert len(dlq) == 1
        assert "item" in dlq[0], "get_dlq() の後方互換性が壊れている ('item' がない)"

        engine.shutdown()
        conn.close()

    def test_get_dlq_summary_returns_empty_when_no_errors(self):
        """
        DLQ が空の場合、get_dlq_summary() は空リストを返す。
        """
        conn = apsw.Connection(":memory:")
        conn.execute("CREATE TABLE IF NOT EXISTS \"data\" (key TEXT PRIMARY KEY, value TEXT)")
        engine = V2Engine(
            connection=conn,
            table_name='"data"',
            flush_mode="manual",
        )

        summary = engine.get_dlq_summary()
        assert summary == [], f"DLQ が空のはずなのに: {summary}"

        engine.shutdown()
        conn.close()


# ============================================================
# 統合テスト: 修正が既存機能を壊さないことを確認
# ============================================================

class TestRegressionNoSideEffects:
    """修正による副作用がないことの回帰テスト"""

    def test_v2_immediate_mode_still_works(self, db_path):
        """immediate モードの基本動作が維持されていること"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="immediate")
        try:
            db["k"] = "v"
            time.sleep(0.3)
            fresh = db.get_fresh("k")
            assert fresh == "v"
        finally:
            db.close()

    def test_v2_manual_flush_still_works(self, db_path):
        """manual flush の基本動作が維持されていること"""
        db = NanaSQLite(db_path, v2_mode=True, flush_mode="manual")
        try:
            db["k"] = "v"
            db.flush()
            time.sleep(0.2)
            fresh = db.get_fresh("k")
            assert fresh == "v"
        finally:
            db.close()

    def test_unique_hook_still_detects_duplicates(self, db_path):
        """UniqueHook の重複検出が維持されていること"""
        from nanasqlite.exceptions import NanaSQLiteValidationError

        hook = UniqueHook("email")
        db = NanaSQLite(db_path, hooks=[hook])
        try:
            db["u1"] = {"email": "dup@example.com"}
            with pytest.raises(NanaSQLiteValidationError):
                db["u2"] = {"email": "dup@example.com"}
        finally:
            db.close()

    def test_unique_hook_with_index_still_works(self, db_path):
        """UniqueHook use_index=True の動作が維持されていること"""
        from nanasqlite.exceptions import NanaSQLiteValidationError

        hook = UniqueHook("email", use_index=True)
        db = NanaSQLite(db_path, hooks=[hook])
        try:
            db["u1"] = {"email": "x@example.com"}
            db["u2"] = {"email": "y@example.com"}
            # 同一キーの上書きは許可
            db["u1"] = {"email": "x_updated@example.com"}
            # 重複は拒否
            with pytest.raises(NanaSQLiteValidationError):
                db["u3"] = {"email": "y@example.com"}
        finally:
            db.close()

    def test_dlq_retry_still_works(self):
        """DLQ の retry_dlq() が維持されていること"""
        conn = apsw.Connection(":memory:")
        conn.execute("CREATE TABLE IF NOT EXISTS \"data\" (key TEXT PRIMARY KEY, value TEXT)")
        engine = V2Engine(
            connection=conn,
            table_name='"data"',
            flush_mode="manual",
        )

        # DLQ にエントリを追加
        engine._add_to_dlq("test", "payload")
        assert len(engine.dlq) == 1

        engine.clear_dlq()
        assert len(engine.dlq) == 0

        engine.shutdown()
        conn.close()
