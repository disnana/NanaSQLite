"""TDD: 最初に失敗するテストを書き、次に修正する。

対象の問題:
1. NanaSQLite クラスレベル docstring の Args 欄に `coerce` の記述がない
2. AsyncNanaSQLite.__init__ の `validator` デフォルトが `_UNSET` (内部センチネル) → `None` に変更すべき
"""
from __future__ import annotations

import inspect

import pytest

from nanasqlite import AsyncNanaSQLite, NanaSQLite


class TestNanaSQLiteClassDocstringCoerce:
    """NanaSQLite クラスレベル docstring に coerce が記載されているかを確認する。"""

    def test_class_docstring_mentions_coerce(self):
        """NanaSQLite クラスレベル docstring の Args 欄に 'coerce' が含まれていること。"""
        docstring = NanaSQLite.__doc__
        assert docstring is not None, "NanaSQLite クラスに docstring が存在しない"
        assert "coerce" in docstring, (
            "NanaSQLite クラスレベル docstring の Args 欄に 'coerce' の記述がない。"
            " validator の次に coerce を追記してください。"
        )

    def test_class_docstring_mentions_validator(self):
        """NanaSQLite クラスレベル docstring の Args 欄に 'validator' が含まれていること (既存の確認)。"""
        docstring = NanaSQLite.__doc__
        assert docstring is not None
        assert "validator" in docstring


class TestAsyncNanaSQLiteInitSignature:
    """AsyncNanaSQLite.__init__ の validator デフォルト値が None であることを確認する。"""

    def test_validator_default_is_none(self):
        """AsyncNanaSQLite.__init__ の validator パラメーターのデフォルトが None であること。

        _UNSET は table() での「省略 = 親継承」セマンティクスのためのセンチネルであり、
        コンストラクターでは親から継承する概念がないため、None をデフォルトにすべき。
        """
        sig = inspect.signature(AsyncNanaSQLite.__init__)
        validator_param = sig.parameters.get("validator")
        assert validator_param is not None, "AsyncNanaSQLite.__init__ に validator パラメーターが存在しない"
        default = validator_param.default
        assert default is None, (
            f"AsyncNanaSQLite.__init__ の validator デフォルトが None ではなく {default!r} になっている。"
            " _UNSET は table() 専用のセンチネルであり、コンストラクターでは None を使用すべき。"
        )

    def test_validator_none_means_no_validation(self, tmp_path):
        """AsyncNanaSQLite(db_path) を引数なしで生成すると _validator が None になること。"""
        db = AsyncNanaSQLite(str(tmp_path / "test.db"))
        assert db._validator is None

    def test_explicit_none_validator_works(self, tmp_path):
        """AsyncNanaSQLite(db_path, validator=None) が正常に動作すること。"""
        db = AsyncNanaSQLite(str(tmp_path / "test.db"), validator=None)
        assert db._validator is None

    def test_coerce_default_still_false(self):
        """AsyncNanaSQLite.__init__ の coerce のデフォルトは False のままであること。"""
        sig = inspect.signature(AsyncNanaSQLite.__init__)
        coerce_param = sig.parameters.get("coerce")
        assert coerce_param is not None
        assert coerce_param.default is False


class TestNanaSQLiteInitSignature:
    """NanaSQLite.__init__ のシグネチャを補完的に確認する。"""

    def test_init_docstring_mentions_coerce(self):
        """NanaSQLite.__init__ の docstring の Args 欄に 'coerce' が含まれていること (既存の確認)。"""
        docstring = NanaSQLite.__init__.__doc__
        assert docstring is not None
        assert "coerce" in docstring

    def test_init_docstring_mentions_validator(self):
        """NanaSQLite.__init__ の docstring の Args 欄に 'validator' が含まれていること (既存の確認)。"""
        docstring = NanaSQLite.__init__.__doc__
        assert docstring is not None
        assert "validator" in docstring
