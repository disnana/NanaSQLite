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


# ========================== table() per-table validator tests ==========================


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_table_inherits_parent_validator(tmp_path):
    """table() で validator を指定しない場合、親の validator が引き継がれる。"""
    from validkit import v

    schema = {"name": v.str(), "age": v.int()}
    db = NanaSQLite(str(tmp_path / "inherit.db"), validator=schema)
    users_db = db.table("users")

    # 子テーブルでも有効な値は保存できる
    users_db["u1"] = {"name": "Dave", "age": 25}
    assert users_db["u1"] == {"name": "Dave", "age": 25}

    # 子テーブルでもスキーマ違反は拒否される
    with pytest.raises(NanaSQLiteValidationError):
        users_db["u2"] = {"name": "Eve", "age": "bad"}


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_table_override_validator(tmp_path):
    """table() で独自の validator を渡すと、親のスキーマではなくそのスキーマが使われる。"""
    from validkit import v

    parent_schema = {"x": v.int()}
    child_schema = {"name": v.str(), "score": v.float()}
    db = NanaSQLite(str(tmp_path / "override.db"), validator=parent_schema)
    scores_db = db.table("scores", validator=child_schema)

    # 子スキーマ準拠の値は保存できる
    scores_db["s1"] = {"name": "Frank", "score": 9.5}
    assert scores_db["s1"] == {"name": "Frank", "score": 9.5}

    # 子スキーマ違反は拒否される
    with pytest.raises(NanaSQLiteValidationError):
        scores_db["s2"] = {"name": "Grace", "score": "not_a_float"}


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_table_no_parent_validator_no_child_validator(tmp_path):
    """親も子も validator なしの場合、任意の値を書き込める。"""
    db = NanaSQLite(str(tmp_path / "novalidator.db"))
    child_db = db.table("misc")

    child_db["k"] = {"anything": True, "nums": [1, 2]}
    assert child_db["k"]["anything"] is True


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_table_explicit_none_disables_parent_validator(tmp_path):
    """table(validator=None) を明示すると親のスキーマを無効化して任意値を書き込める。"""
    from validkit import v

    parent_schema = {"name": v.str(), "age": v.int()}
    db = NanaSQLite(str(tmp_path / "disable.db"), validator=parent_schema)
    # validator=None を明示すると親スキーマを引き継がない
    free_db = db.table("free_table", validator=None)

    # バリデーションなしなので任意の値を書き込める
    free_db["k"] = {"anything": True, "n": 99}
    assert free_db["k"]["anything"] is True


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_table_child_does_not_affect_parent_validator(tmp_path):
    """table() で別スキーマを指定しても親インスタンスのバリデーションは変わらない。"""
    from validkit import v

    parent_schema = {"x": v.int()}
    child_schema = {"name": v.str()}
    db = NanaSQLite(str(tmp_path / "separate.db"), validator=parent_schema)
    child_db = db.table("child", validator=child_schema)

    # 親テーブルは親スキーマで検証される
    db["valid"] = {"x": 42}
    with pytest.raises(NanaSQLiteValidationError):
        db["bad"] = {"x": "not_int"}

    # 子テーブルは子スキーマで検証される
    child_db["c1"] = {"name": "Helen"}
    with pytest.raises(NanaSQLiteValidationError):
        child_db["c2"] = {"name": 999}
