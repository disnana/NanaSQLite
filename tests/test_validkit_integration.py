"""
validkit-py オプション連携のテスト
(Tests for optional validkit-py integration)
"""
import importlib.util

import pytest

from nanasqlite import NanaSQLite, NanaSQLiteValidationError

# validkit がインストールされていない場合はほとんどのテストをスキップ
validkit_installed = importlib.util.find_spec("validkit") is not None


def test_has_validkit_flag():
    """HAS_VALIDKIT フラグが正しく設定されているか確認する。"""
    from nanasqlite import core as core_mod

    assert hasattr(core_mod, "HAS_VALIDKIT")
    assert isinstance(core_mod.HAS_VALIDKIT, bool)


def test_has_validkit_flag_from_package():
    """HAS_VALIDKIT が nanasqlite パッケージから直接インポートできることを確認する。"""
    from nanasqlite import HAS_VALIDKIT

    assert isinstance(HAS_VALIDKIT, bool)
    assert HAS_VALIDKIT is validkit_installed


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_validator_accepts_valid_value(tmp_path):
    """バリデーションスキーマに一致する値は正常に保存される。"""
    from validkit import v

    schema = {"name": v.str(), "age": v.int()}
    db = NanaSQLite(str(tmp_path / "valid.db"), validator=schema)

    db["user"] = {"name": "Alice", "age": 30}
    assert db["user"] == {"name": "Alice", "age": 30}


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_validator_rejects_invalid_value(tmp_path):
    """バリデーションスキーマに違反する値を設定すると NanaSQLiteValidationError が送出される。"""
    from validkit import v

    schema = {"name": v.str(), "age": v.int()}
    db = NanaSQLite(str(tmp_path / "invalid.db"), validator=schema)

    with pytest.raises(NanaSQLiteValidationError):
        db["user"] = {"name": "Bob", "age": "not_an_int"}


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_validator_does_not_affect_db_when_invalid(tmp_path):
    """バリデーションエラー時はDBに値が保存されないことを確認する。"""
    from validkit import v

    schema = {"name": v.str(), "score": v.int()}
    db = NanaSQLite(str(tmp_path / "no_write.db"), validator=schema)

    with pytest.raises(NanaSQLiteValidationError):
        db["entry"] = {"name": "Carol", "score": "oops"}

    assert "entry" not in db


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_no_validator_allows_any_value(tmp_path):
    """validator を指定しない場合は任意の値を保存できる。"""
    db = NanaSQLite(str(tmp_path / "novalidator.db"))

    db["misc"] = {"anything": [1, 2, 3], "flag": True}
    assert db["misc"]["flag"] is True


@pytest.mark.skipif(validkit_installed, reason="このテストは validkit-py 未インストール環境でのみ実行します")
def test_validator_raises_import_error_when_validkit_missing(tmp_path):
    """validkit-py が未インストールの状態で validator を渡すと ImportError が送出される。"""
    with pytest.raises(ImportError, match="validkit-py"):
        NanaSQLite(str(tmp_path / "err.db"), validator={"key": "value"})
