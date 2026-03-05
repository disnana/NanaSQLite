"""
table() 継承セマンティクスとキャッシュ戦略の包括的テスト
(Comprehensive tests for table() inheritance semantics and cache strategies)

このテストファイルは以下を網羅的にテストします:
1. table() のキャッシュ戦略継承 (UNBOUNDED / LRU / TTL)
   - TTL: cache_ttl / cache_persistence_ttl の継承（省略時の ValueError 防止）
2. table() の validator / coerce 継承セマンティクス
3. table() の cache_strategy 型アノテーション（"ttl" 文字列含む）
4. HAS_VALIDKIT / HAS_ORJSON フラグの整合性
5. optional import の例外絞り込み（ImportError のみ捕捉）
6. per-table バリデーション全パス
7. coerce 動作の全パス（デュアル要件）
8. batch_update() バリデーション（アトミック失敗）
9. AsyncNanaSQLite の各種パス
"""
from __future__ import annotations

import pytest

from nanasqlite import CacheType, NanaSQLite

# validkit availability detection (try/except import, not find_spec)
try:
    import validkit  # noqa: F401

    validkit_installed = True
except ImportError:
    validkit_installed = False


# ===========================================================================
# セクション 1: table() キャッシュ戦略継承
# ===========================================================================


class TestTableCacheStrategyInheritance:
    """table() が親のキャッシュ戦略を正しく継承することを確認する。"""

    def test_table_inherits_unbounded_strategy(self, tmp_path):
        """親が UNBOUNDED の場合、子も UNBOUNDED を継承する。"""
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.UNBOUNDED)
        child = db.table("child")
        assert child._cache_strategy_raw == CacheType.UNBOUNDED
        # 子テーブルに書き込みと読み込みが正常に動作する
        child["k"] = "v"
        assert child["k"] == "v"

    def test_table_inherits_lru_strategy(self, tmp_path):
        """親が LRU の場合、子も LRU を継承し同じサイズを使う。"""
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.LRU, cache_size=10)
        child = db.table("child")
        assert child._cache_strategy_raw == CacheType.LRU
        assert child._cache_size_raw == 10
        child["a"] = 1
        child["b"] = 2
        assert child["a"] == 1

    def test_table_override_cache_strategy(self, tmp_path):
        """table() で明示的に cache_strategy を渡すと、親の戦略を上書きできる。"""
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.UNBOUNDED)
        child = db.table("child", cache_strategy=CacheType.LRU, cache_size=5)
        assert child._cache_strategy_raw == CacheType.LRU
        assert child._cache_size_raw == 5

    def test_table_inherits_lru_eviction(self, tmp_path):
        """LRU 継承した子テーブルでエビクションが正しく機能する。"""
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.LRU, cache_size=3)
        child = db.table("child")
        for i in range(5):
            child[f"k{i}"] = i
        # DB にはすべての値が保存されている
        for i in range(5):
            assert child[f"k{i}"] == i

    def test_table_override_with_lru_string(self, tmp_path):
        """table() に文字列 'lru' を渡して LRU 戦略を指定できる。"""
        db = NanaSQLite(str(tmp_path / "db.db"))
        child = db.table("child", cache_strategy="lru", cache_size=5)
        child["x"] = 42
        assert child["x"] == 42

    def test_table_override_with_unbounded_string(self, tmp_path):
        """table() に文字列 'unbounded' を渡して UNBOUNDED 戦略を指定できる。"""
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.LRU, cache_size=5)
        child = db.table("child", cache_strategy="unbounded")
        child["x"] = "hello"
        assert child["x"] == "hello"


class TestTableTTLCacheInheritance:
    """table() が TTL キャッシュ設定を正しく継承することを確認する（TTL ValueError 防止）。"""

    def test_table_inherits_ttl_strategy_does_not_raise(self, tmp_path):
        """親が TTL 戦略の場合、table() 呼び出しが ValueError を送出しないこと。

        これは修正されたバグ: cache_ttl を継承しないと ValueError が発生していた。
        """
        db = NanaSQLite(
            str(tmp_path / "db.db"),
            cache_strategy=CacheType.TTL,
            cache_ttl=60.0,
        )
        # table() は ValueError を送出してはいけない
        child = db.table("child")
        assert child._cache_strategy_raw == CacheType.TTL
        assert child._cache_ttl_raw == 60.0

    def test_table_inherits_ttl_value(self, tmp_path):
        """子テーブルが親の cache_ttl 値を正しく継承する。"""
        db = NanaSQLite(
            str(tmp_path / "db.db"),
            cache_strategy=CacheType.TTL,
            cache_ttl=30.0,
        )
        child = db.table("child")
        assert child._cache_ttl_raw == 30.0

    def test_table_inherits_ttl_with_persistence(self, tmp_path):
        """子テーブルが cache_persistence_ttl も継承する。"""
        db = NanaSQLite(
            str(tmp_path / "db.db"),
            cache_strategy=CacheType.TTL,
            cache_ttl=60.0,
            cache_persistence_ttl=True,
        )
        child = db.table("child")
        assert child._cache_strategy_raw == CacheType.TTL
        assert child._cache_ttl_raw == 60.0
        assert child._cache_persistence_ttl_raw is True

    def test_table_ttl_child_can_read_write(self, tmp_path):
        """TTL を継承した子テーブルで読み書きが正常に動作する。"""
        db = NanaSQLite(
            str(tmp_path / "db.db"),
            cache_strategy=CacheType.TTL,
            cache_ttl=60.0,
        )
        child = db.table("child")
        child["key"] = {"value": 123}
        assert child["key"] == {"value": 123}

    def test_table_override_ttl_strategy(self, tmp_path):
        """table() で TTL を上書き指定する場合、親が TTL なら cache_ttl も継承される。"""
        db = NanaSQLite(
            str(tmp_path / "db.db"),
            cache_strategy=CacheType.TTL,
            cache_ttl=30.0,
        )
        # 子で TTL を明示し、cache_ttl は親から継承される（ValueError にならない）
        child = db.table("child", cache_strategy=CacheType.TTL)
        assert child._cache_strategy_raw == CacheType.TTL
        assert child._cache_ttl_raw == 30.0

    def test_table_inherits_ttl_string_strategy(self, tmp_path):
        """文字列 'ttl' で指定された親の戦略も table() で継承される。"""
        db = NanaSQLite(
            str(tmp_path / "db.db"),
            cache_strategy="ttl",
            cache_ttl=20.0,
        )
        child = db.table("child")
        assert child._cache_strategy_raw == "ttl"
        assert child._cache_ttl_raw == 20.0
        child["z"] = 99
        assert child["z"] == 99

    def test_multiple_children_from_ttl_parent(self, tmp_path):
        """TTL 親から複数の子テーブルを作成しても全て成功する。"""
        db = NanaSQLite(
            str(tmp_path / "db.db"),
            cache_strategy=CacheType.TTL,
            cache_ttl=60.0,
        )
        children = [db.table(f"child{i}") for i in range(5)]
        for i, child in enumerate(children):
            child[f"k{i}"] = i * 10
            assert child[f"k{i}"] == i * 10


class TestTableCacheSizeInheritance:
    """table() が親の cache_size を正しく継承することを確認する。"""

    def test_table_inherits_cache_size(self, tmp_path):
        """子テーブルが親の cache_size を継承する。"""
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.LRU, cache_size=20)
        child = db.table("child")
        assert child._cache_size_raw == 20

    def test_table_overrides_cache_size(self, tmp_path):
        """table() で cache_size を明示指定すると親の値を上書きできる。"""
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.LRU, cache_size=20)
        child = db.table("child", cache_size=5)
        assert child._cache_size_raw == 5

    def test_table_none_cache_size_inherits_parent(self, tmp_path):
        """cache_size=None を渡さずに省略すると、親の値が継承される。"""
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.LRU, cache_size=15)
        child = db.table("child")
        assert child._cache_size_raw == 15


# ===========================================================================
# セクション 2: _UNSET センチネル / validator・coerce 継承
# ===========================================================================


class TestTableValidatorInheritance:
    """table() での validator / coerce の継承と上書きを確認する。"""

    def test_table_inherits_none_validator(self, tmp_path):
        """親に validator がない場合、子も validator なしで動作する。"""
        db = NanaSQLite(str(tmp_path / "db.db"))
        child = db.table("child")
        assert child._validator is None
        child["k"] = {"any": "value"}
        assert child["k"]["any"] == "value"

    @pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
    def test_table_inherits_validator_from_parent(self, tmp_path):
        """親の validator が子テーブルに継承される。"""
        from validkit import v

        schema = {"name": v.str()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema)
        child = db.table("child")
        assert child._validator is schema

    @pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
    def test_table_explicit_none_overrides_validator(self, tmp_path):
        """table(validator=None) は親の validator を無効化する。"""
        from validkit import v

        schema = {"name": v.str()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema)
        child = db.table("child", validator=None)
        assert child._validator is None
        # バリデーションなしで任意の値が書き込める
        child["k"] = {"anything": 42}
        assert child["k"]["anything"] == 42

    @pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
    def test_table_override_with_new_validator(self, tmp_path):
        """table() で別のスキーマを指定すると、子テーブルはそのスキーマを使う。"""
        from validkit import v

        from nanasqlite import NanaSQLiteValidationError

        parent_schema = {"x": v.int()}
        child_schema = {"name": v.str()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=parent_schema)
        child = db.table("child", validator=child_schema)

        child["c"] = {"name": "Alice"}
        assert child["c"] == {"name": "Alice"}

        with pytest.raises(NanaSQLiteValidationError):
            child["bad"] = {"name": 999}

    def test_table_inherits_coerce_false(self, tmp_path):
        """親の coerce=False (デフォルト) が子に継承される。"""
        db = NanaSQLite(str(tmp_path / "db.db"))
        child = db.table("child")
        assert child._coerce is False

    @pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
    def test_table_inherits_coerce_true(self, tmp_path):
        """親の coerce=True が子に継承される。"""
        from validkit import v

        schema = {"age": v.int().coerce()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema, coerce=True)
        child = db.table("child")
        assert child._coerce is True
        child["c"] = {"age": "5"}
        assert child["c"] == {"age": 5}

    @pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
    def test_table_override_coerce_to_false(self, tmp_path):
        """table(coerce=False) で子テーブルの coerce を無効化できる。"""
        from validkit import v

        schema = {"age": v.int()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema, coerce=True)
        child = db.table("child", coerce=False)
        assert child._coerce is False
        # coerce=False なので正しい型のみ受け付ける
        child["c"] = {"age": 10}
        assert child["c"] == {"age": 10}


# ===========================================================================
# セクション 3: HAS_VALIDKIT / HAS_ORJSON フラグ整合性
# ===========================================================================


class TestOptionalImportFlags:
    """HAS_VALIDKIT / HAS_ORJSON フラグが正しく設定されていることを確認する。"""

    def test_has_validkit_flag_is_bool(self):
        """HAS_VALIDKIT は bool 型であること。"""
        from nanasqlite import core as core_mod

        assert isinstance(core_mod.HAS_VALIDKIT, bool)

    def test_has_validkit_matches_actual_import(self):
        """HAS_VALIDKIT の値が実際の validkit インポート成否と一致する。"""
        from nanasqlite import HAS_VALIDKIT

        assert HAS_VALIDKIT is validkit_installed

    def test_has_orjson_flag_is_bool(self):
        """HAS_ORJSON は bool 型であること。"""
        from nanasqlite import core as core_mod

        assert isinstance(core_mod.HAS_ORJSON, bool)

    def test_has_orjson_matches_actual_import(self):
        """HAS_ORJSON の値が実際の orjson インポート成否と一致する。"""
        from nanasqlite import core as core_mod

        try:
            import orjson  # noqa: F401
            expected = True
        except ImportError:
            expected = False
        assert core_mod.HAS_ORJSON is expected

    def test_has_validkit_exportable_from_package(self):
        """HAS_VALIDKIT は nanasqlite パッケージから直接インポートできる。"""
        from nanasqlite import HAS_VALIDKIT  # noqa: F401 — must not raise

    @pytest.mark.skipif(validkit_installed, reason="validkit-py がインストールされている環境ではスキップ")
    def test_import_error_raised_when_validkit_missing(self, tmp_path):
        """HAS_VALIDKIT=False 環境で validator を渡すと ImportError が送出される。"""
        with pytest.raises(ImportError, match="validkit-py"):
            NanaSQLite(str(tmp_path / "err.db"), validator={"key": "val"})

    @pytest.mark.skipif(validkit_installed, reason="validkit-py がインストールされている環境ではスキップ")
    @pytest.mark.asyncio
    async def test_async_import_error_raised_when_validkit_missing(self, tmp_path):
        """HAS_VALIDKIT=False 環境で AsyncNanaSQLite に validator を渡すと ImportError が送出される。"""
        from nanasqlite import AsyncNanaSQLite

        with pytest.raises(ImportError, match="validkit-py"):
            AsyncNanaSQLite(str(tmp_path / "async_err.db"), validator={"key": "val"})


# ===========================================================================
# セクション 4: _cache_strategy_raw の保持と継承チェーン
# ===========================================================================


class TestCacheRawAttributeStorage:
    """__init__ で _cache_*_raw 属性が正しく保存されることを確認する。"""

    def test_cache_strategy_raw_stored_unbounded(self, tmp_path):
        db = NanaSQLite(str(tmp_path / "db.db"))
        assert db._cache_strategy_raw == CacheType.UNBOUNDED

    def test_cache_strategy_raw_stored_lru(self, tmp_path):
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.LRU, cache_size=5)
        assert db._cache_strategy_raw == CacheType.LRU

    def test_cache_strategy_raw_stored_ttl(self, tmp_path):
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.TTL, cache_ttl=30.0)
        assert db._cache_strategy_raw == CacheType.TTL

    def test_cache_size_raw_stored(self, tmp_path):
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.LRU, cache_size=7)
        assert db._cache_size_raw == 7

    def test_cache_size_raw_none_when_not_provided(self, tmp_path):
        db = NanaSQLite(str(tmp_path / "db.db"))
        assert db._cache_size_raw is None

    def test_cache_ttl_raw_stored(self, tmp_path):
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.TTL, cache_ttl=45.0)
        assert db._cache_ttl_raw == 45.0

    def test_cache_ttl_raw_none_when_not_provided(self, tmp_path):
        db = NanaSQLite(str(tmp_path / "db.db"))
        assert db._cache_ttl_raw is None

    def test_cache_persistence_ttl_raw_stored(self, tmp_path):
        db = NanaSQLite(
            str(tmp_path / "db.db"),
            cache_strategy=CacheType.TTL,
            cache_ttl=60.0,
            cache_persistence_ttl=True,
        )
        assert db._cache_persistence_ttl_raw is True

    def test_cache_persistence_ttl_raw_default_false(self, tmp_path):
        db = NanaSQLite(str(tmp_path / "db.db"))
        assert db._cache_persistence_ttl_raw is False


# ===========================================================================
# セクション 5: バリデーション全パス (validkit 必須)
# ===========================================================================


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
class TestValidkitValidationPaths:
    """validkit-py バリデーションの全パスを網羅するテスト。"""

    def test_valid_value_is_accepted(self, tmp_path):
        """スキーマに一致する値は正常に保存される。"""
        from validkit import v

        schema = {"name": v.str(), "age": v.int()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema)
        db["u"] = {"name": "Alice", "age": 30}
        assert db["u"] == {"name": "Alice", "age": 30}

    def test_invalid_value_raises_validation_error(self, tmp_path):
        """スキーマ違反の値は NanaSQLiteValidationError を送出する。"""
        from validkit import v

        from nanasqlite import NanaSQLiteValidationError

        schema = {"name": v.str(), "age": v.int()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema)
        with pytest.raises(NanaSQLiteValidationError):
            db["u"] = {"name": "Bob", "age": "bad"}

    def test_invalid_value_not_written_to_db(self, tmp_path):
        """バリデーションエラー時は DB に値が保存されない。"""
        from validkit import v

        from nanasqlite import NanaSQLiteValidationError

        schema = {"score": v.int()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema)
        with pytest.raises(NanaSQLiteValidationError):
            db["e"] = {"score": "oops"}
        assert "e" not in db

    def test_validator_none_explicit_no_validation(self, tmp_path):
        """validator=None を明示すると任意の値が保存される。"""
        db = NanaSQLite(str(tmp_path / "db.db"), validator=None)
        db["k"] = {"anything": [1, 2, 3]}
        assert db["k"]["anything"] == [1, 2, 3]

    def test_validator_not_provided_no_validation(self, tmp_path):
        """validator を省略した場合も任意の値が保存される。"""
        db = NanaSQLite(str(tmp_path / "db.db"))
        db["k"] = {"x": True, "y": "z"}
        assert db["k"]["x"] is True

    def test_multiple_schemas_independent(self, tmp_path):
        """異なるスキーマを持つ複数のインスタンスが互いに独立している。"""
        from validkit import v

        from nanasqlite import NanaSQLiteValidationError

        schema_a = {"x": v.int()}
        schema_b = {"name": v.str()}
        db_a = NanaSQLite(str(tmp_path / "a.db"), validator=schema_a)
        db_b = NanaSQLite(str(tmp_path / "b.db"), validator=schema_b)

        db_a["k"] = {"x": 1}
        db_b["k"] = {"name": "hello"}

        with pytest.raises(NanaSQLiteValidationError):
            db_a["bad"] = {"x": "not_int"}
        with pytest.raises(NanaSQLiteValidationError):
            db_b["bad"] = {"name": 999}

    def test_batch_update_atomic_failure(self, tmp_path):
        """batch_update() は1件でもバリデーション違反があれば全件書き込まない。"""
        from validkit import v

        from nanasqlite import NanaSQLiteValidationError

        schema = {"age": v.int()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema)
        with pytest.raises(NanaSQLiteValidationError):
            db.batch_update({
                "u1": {"age": 20},
                "u2": {"age": "bad"},
            })
        assert "u1" not in db
        assert "u2" not in db

    def test_batch_update_all_valid_writes_all(self, tmp_path):
        """batch_update() は全件バリデーションが通れば全件書き込む。"""
        from validkit import v

        schema = {"age": v.int()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema)
        db.batch_update({
            "u1": {"age": 20},
            "u2": {"age": 30},
        })
        assert db["u1"]["age"] == 20
        assert db["u2"]["age"] == 30

    def test_per_table_validator_isolation(self, tmp_path):
        """異なるテーブルで別スキーマを使うと、テーブルごとにバリデーションが独立する。"""
        from validkit import v

        from nanasqlite import NanaSQLiteValidationError

        parent_schema = {"x": v.int()}
        child_schema = {"name": v.str()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=parent_schema)
        child = db.table("child", validator=child_schema)

        db["p"] = {"x": 1}
        child["c"] = {"name": "hello"}

        with pytest.raises(NanaSQLiteValidationError):
            db["bad"] = {"x": "not_int"}
        with pytest.raises(NanaSQLiteValidationError):
            child["bad"] = {"name": 999}


# ===========================================================================
# セクション 6: coerce 全パス (dual-requirement)
# ===========================================================================


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
class TestCoercePaths:
    """coerce モードの全パスを網羅するテスト。"""

    def test_coerce_true_with_field_coerce_converts(self, tmp_path):
        """NanaSQLite coerce=True + フィールド .coerce() で型変換が有効になる。"""
        from validkit import v

        schema = {"age": v.int().coerce()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema, coerce=True)
        db["u"] = {"age": "42"}
        assert db["u"] == {"age": 42}

    def test_coerce_true_without_field_coerce_fails(self, tmp_path):
        """NanaSQLite coerce=True でもフィールドに .coerce() がなければ型不一致は失敗する。"""
        from validkit import v

        from nanasqlite import NanaSQLiteValidationError

        schema = {"age": v.int()}  # .coerce() なし
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema, coerce=True)
        with pytest.raises(NanaSQLiteValidationError):
            db["u"] = {"age": "42"}
        # 正しい型は通る
        db["u"] = {"age": 42}
        assert db["u"] == {"age": 42}

    def test_coerce_false_with_field_coerce_stores_original(self, tmp_path):
        """coerce=False (デフォルト) + フィールド .coerce() の場合、変換後ではなく元の値が保存される。"""
        from validkit import v

        schema = {"age": v.int().coerce()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema, coerce=False)
        db["u"] = {"age": "30"}
        assert db["u"] == {"age": "30"}  # 元の文字列が保存される

    def test_coerce_inherited_in_batch_update(self, tmp_path):
        """coerce=True は batch_update() でも機能する。"""
        from validkit import v

        schema = {"score": v.float().coerce()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema, coerce=True)
        db.batch_update({"a": {"score": "1.5"}, "b": {"score": "2.0"}})
        assert db["a"] == {"score": 1.5}
        assert db["b"] == {"score": 2.0}

    def test_coerce_inherited_by_child_table(self, tmp_path):
        """子テーブルは親の coerce=True を継承する。"""
        from validkit import v

        schema = {"age": v.int().coerce()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema, coerce=True)
        child = db.table("child")
        child["c"] = {"age": "7"}
        assert child["c"] == {"age": 7}

    def test_coerce_can_be_disabled_in_child(self, tmp_path):
        """table(coerce=False) で子テーブルの coerce を無効化できる。"""
        from validkit import v

        schema = {"age": v.int()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema, coerce=True)
        child = db.table("child", coerce=False)
        assert child._coerce is False
        child["c"] = {"age": 5}
        assert child["c"] == {"age": 5}

    def test_coerce_can_be_enabled_in_child(self, tmp_path):
        """table(coerce=True) で子テーブルの coerce を有効化できる。"""
        from validkit import v

        schema = {"age": v.int().coerce()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=schema, coerce=False)
        child = db.table("child", coerce=True)
        assert child._coerce is True
        child["c"] = {"age": "8"}
        assert child["c"] == {"age": 8}


# ===========================================================================
# セクション 7: AsyncNanaSQLite 継承パス
# ===========================================================================


class TestAsyncTableInheritance:
    """AsyncNanaSQLite の table() 継承セマンティクスを確認する。"""

    @pytest.mark.asyncio
    async def test_async_table_inherits_cache_strategy(self, tmp_path):
        """AsyncNanaSQLite: table() が親のキャッシュ戦略を継承する。"""
        from nanasqlite import AsyncNanaSQLite

        async with AsyncNanaSQLite(
            str(tmp_path / "db.db"),
            cache_strategy=CacheType.LRU,
            cache_size=10,
        ) as db:
            child = await db.table("child")
            await child.aset("k", "v")
            assert await child.aget("k") == "v"

    @pytest.mark.asyncio
    async def test_async_table_inherits_ttl_does_not_raise(self, tmp_path):
        """AsyncNanaSQLite: TTL 戦略の親から table() を作成しても ValueError が出ない。"""
        from nanasqlite import AsyncNanaSQLite

        async with AsyncNanaSQLite(
            str(tmp_path / "db.db"),
            cache_strategy=CacheType.TTL,
            cache_ttl=60.0,
        ) as db:
            child = await db.table("child")
            await child.aset("key", "value")
            assert await child.aget("key") == "value"

    @pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
    @pytest.mark.asyncio
    async def test_async_table_inherits_validator(self, tmp_path):
        """AsyncNanaSQLite: 親の validator が子テーブルに継承される。"""
        from validkit import v

        from nanasqlite import AsyncNanaSQLite, NanaSQLiteValidationError

        schema = {"name": v.str()}
        async with AsyncNanaSQLite(str(tmp_path / "db.db"), validator=schema) as db:
            child = await db.table("child")
            await child.aset("c", {"name": "hello"})
            assert (await child.aget("c"))["name"] == "hello"
            with pytest.raises(NanaSQLiteValidationError):
                await child.aset("bad", {"name": 999})

    @pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
    @pytest.mark.asyncio
    async def test_async_table_explicit_none_disables_validator(self, tmp_path):
        """AsyncNanaSQLite: table(validator=None) で親の validator を無効化できる。"""
        from validkit import v

        from nanasqlite import AsyncNanaSQLite

        schema = {"name": v.str()}
        async with AsyncNanaSQLite(str(tmp_path / "db.db"), validator=schema) as db:
            child = await db.table("child", validator=None)
            await child.aset("k", {"anything": 42})
            assert (await child.aget("k"))["anything"] == 42

    @pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
    @pytest.mark.asyncio
    async def test_async_coerce_inherited(self, tmp_path):
        """AsyncNanaSQLite: coerce=True が子テーブルに継承される。"""
        from validkit import v

        from nanasqlite import AsyncNanaSQLite

        schema = {"age": v.int().coerce()}
        async with AsyncNanaSQLite(
            str(tmp_path / "db.db"), validator=schema, coerce=True
        ) as db:
            child = await db.table("child")
            await child.aset("c", {"age": "12"})
            assert (await child.aget("c")) == {"age": 12}

    @pytest.mark.skipif(validkit_installed, reason="validkit-py がインストールされている環境ではスキップ")
    @pytest.mark.asyncio
    async def test_async_import_error_on_constructor_when_validkit_missing(self, tmp_path):
        """validkit-py が未インストールの場合、AsyncNanaSQLite コンストラクタで ImportError が出る。"""
        from nanasqlite import AsyncNanaSQLite

        with pytest.raises(ImportError, match="validkit-py"):
            AsyncNanaSQLite(str(tmp_path / "err.db"), validator={"k": "v"})


# ===========================================================================
# セクション 8: table() の cache_strategy 型アノテーション（文字列値）
# ===========================================================================


class TestTableCacheStrategyStringAnnotation:
    """table() の cache_strategy に文字列 'ttl' / 'lru' / 'unbounded' を渡せることを確認する。"""

    def test_table_accepts_ttl_string(self, tmp_path):
        """table() に 'ttl' 文字列を渡せる（ValueError が出ない）。"""
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.TTL, cache_ttl=60.0)
        # TTL を親から継承した子を 'ttl' 文字列でも作れる
        child = db.table("child", cache_strategy="ttl")
        # cache_ttl は親から継承されるので ValueError にならない
        child["k"] = "v"
        assert child["k"] == "v"

    def test_table_accepts_lru_string(self, tmp_path):
        """table() に 'lru' 文字列と cache_size を渡せる。"""
        db = NanaSQLite(str(tmp_path / "db.db"))
        child = db.table("child", cache_strategy="lru", cache_size=10)
        child["k"] = "v"
        assert child["k"] == "v"

    def test_table_accepts_unbounded_string(self, tmp_path):
        """table() に 'unbounded' 文字列を渡せる。"""
        db = NanaSQLite(str(tmp_path / "db.db"))
        child = db.table("child", cache_strategy="unbounded")
        child["k"] = "v"
        assert child["k"] == "v"


# ===========================================================================
# セクション 9: 接続共有と多テーブル同時操作
# ===========================================================================


class TestMultiTableOperations:
    """同一 DB から複数テーブルを操作する際の動作を確認する。"""

    def test_multiple_tables_share_connection(self, tmp_path):
        """複数の子テーブルが同じ DB ファイルを共有して動作する。"""
        db = NanaSQLite(str(tmp_path / "db.db"))
        users = db.table("users")
        products = db.table("products")
        users["u1"] = {"name": "Alice"}
        products["p1"] = {"name": "Laptop"}
        assert users["u1"]["name"] == "Alice"
        assert products["p1"]["name"] == "Laptop"

    def test_tables_data_are_isolated(self, tmp_path):
        """異なるテーブルのデータは独立していて、相互に影響しない。"""
        db = NanaSQLite(str(tmp_path / "db.db"))
        t1 = db.table("t1")
        t2 = db.table("t2")
        t1["k"] = "table1_value"
        t2["k"] = "table2_value"
        assert t1["k"] == "table1_value"
        assert t2["k"] == "table2_value"

    def test_parent_and_child_tables_independent_data(self, tmp_path):
        """親テーブルと子テーブルのデータは独立している。"""
        db = NanaSQLite(str(tmp_path / "db.db"))
        child = db.table("child")
        db["shared_key"] = "parent_value"
        child["shared_key"] = "child_value"
        assert db["shared_key"] == "parent_value"
        assert child["shared_key"] == "child_value"

    @pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
    def test_child_schema_does_not_affect_parent(self, tmp_path):
        """子テーブルのスキーマを変更しても親インスタンスのバリデーションは変わらない。"""
        from validkit import v

        from nanasqlite import NanaSQLiteValidationError

        parent_schema = {"x": v.int()}
        child_schema = {"name": v.str()}
        db = NanaSQLite(str(tmp_path / "db.db"), validator=parent_schema)
        _ = db.table("child", validator=child_schema)

        db["p"] = {"x": 42}
        with pytest.raises(NanaSQLiteValidationError):
            db["bad"] = {"x": "not_int"}

    def test_deep_chain_table_inherits_strategy(self, tmp_path):
        """table() の連鎖（孫テーブル）でもキャッシュ戦略が正しく設定される。"""
        db = NanaSQLite(str(tmp_path / "db.db"), cache_strategy=CacheType.LRU, cache_size=10)
        child = db.table("child")
        # 孫テーブルも同じ戦略を持つ
        grandchild = child.table("grandchild")
        assert grandchild._cache_strategy_raw == CacheType.LRU
        grandchild["k"] = "v"
        assert grandchild["k"] == "v"

    def test_deep_chain_ttl_does_not_raise(self, tmp_path):
        """table() の連鎖（孫テーブル）でも TTL が正しく継承されて ValueError が出ない。"""
        db = NanaSQLite(
            str(tmp_path / "db.db"),
            cache_strategy=CacheType.TTL,
            cache_ttl=60.0,
        )
        child = db.table("child")
        grandchild = child.table("grandchild")
        assert grandchild._cache_ttl_raw == 60.0
        grandchild["k"] = "v"
        assert grandchild["k"] == "v"


# ===========================================================================
# セクション 10: AsyncNanaSQLite 基本動作 (バリデーションなし)
# ===========================================================================


class TestAsyncBasicOperations:
    """AsyncNanaSQLite の基本的な読み書き操作を確認する。"""

    @pytest.mark.asyncio
    async def test_async_set_and_get(self, tmp_path):
        from nanasqlite import AsyncNanaSQLite

        async with AsyncNanaSQLite(str(tmp_path / "db.db")) as db:
            await db.aset("k", {"val": 1})
            result = await db.aget("k")
            assert result == {"val": 1}

    @pytest.mark.asyncio
    async def test_async_contains(self, tmp_path):
        from nanasqlite import AsyncNanaSQLite

        async with AsyncNanaSQLite(str(tmp_path / "db.db")) as db:
            assert not await db.acontains("k")
            await db.aset("k", 42)
            assert await db.acontains("k")

    @pytest.mark.asyncio
    async def test_async_delete(self, tmp_path):
        from nanasqlite import AsyncNanaSQLite

        async with AsyncNanaSQLite(str(tmp_path / "db.db")) as db:
            await db.aset("k", 99)
            await db.adelete("k")
            assert not await db.acontains("k")

    @pytest.mark.asyncio
    async def test_async_batch_update(self, tmp_path):
        from nanasqlite import AsyncNanaSQLite

        async with AsyncNanaSQLite(str(tmp_path / "db.db")) as db:
            await db.aupdate({"a": 1, "b": 2})
            assert await db.aget("a") == 1
            assert await db.aget("b") == 2

    @pytest.mark.asyncio
    async def test_async_len(self, tmp_path):
        from nanasqlite import AsyncNanaSQLite

        async with AsyncNanaSQLite(str(tmp_path / "db.db")) as db:
            await db.aset("a", 1)
            await db.aset("b", 2)
            assert await db.alen() == 2
