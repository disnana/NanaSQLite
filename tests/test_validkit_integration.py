"""
validkit-py オプション連携のテスト
(Tests for optional validkit-py integration)
"""
import importlib.util

import pytest

from nanasqlite import AsyncNanaSQLite, NanaSQLite, NanaSQLiteValidationError

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


# ========================== AsyncNanaSQLite validator tests ==========================


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
@pytest.mark.asyncio
async def test_async_validator_accepts_valid_value(tmp_path):
    """AsyncNanaSQLite: バリデーションスキーマに一致する値は正常に保存される。"""
    from validkit import v

    schema = {"name": v.str(), "age": v.int()}
    async with AsyncNanaSQLite(str(tmp_path / "async_valid.db"), validator=schema) as db:
        await db.aset("user", {"name": "Alice", "age": 30})
        assert await db.aget("user") == {"name": "Alice", "age": 30}


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
@pytest.mark.asyncio
async def test_async_validator_rejects_invalid_value(tmp_path):
    """AsyncNanaSQLite: バリデーションスキーマに違反する値は NanaSQLiteValidationError が送出される。"""
    from validkit import v

    schema = {"name": v.str(), "age": v.int()}
    async with AsyncNanaSQLite(str(tmp_path / "async_invalid.db"), validator=schema) as db:
        with pytest.raises(NanaSQLiteValidationError):
            await db.aset("user", {"name": "Bob", "age": "not_an_int"})


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
@pytest.mark.asyncio
async def test_async_validator_does_not_affect_db_when_invalid(tmp_path):
    """AsyncNanaSQLite: バリデーションエラー時はDBに値が保存されないことを確認する。"""
    from validkit import v

    schema = {"name": v.str(), "score": v.int()}
    async with AsyncNanaSQLite(str(tmp_path / "async_no_write.db"), validator=schema) as db:
        with pytest.raises(NanaSQLiteValidationError):
            await db.aset("entry", {"name": "Carol", "score": "oops"})
        assert not await db.acontains("entry")


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
@pytest.mark.asyncio
async def test_async_table_inherits_parent_validator(tmp_path):
    """AsyncNanaSQLite: table() で validator を指定しない場合、親の validator が引き継がれる。"""
    from validkit import v

    schema = {"name": v.str(), "age": v.int()}
    async with AsyncNanaSQLite(str(tmp_path / "async_inherit.db"), validator=schema) as db:
        users_db = await db.table("users")

        await users_db.aset("u1", {"name": "Dave", "age": 25})
        assert await users_db.aget("u1") == {"name": "Dave", "age": 25}

        with pytest.raises(NanaSQLiteValidationError):
            await users_db.aset("u2", {"name": "Eve", "age": "bad"})


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
@pytest.mark.asyncio
async def test_async_table_override_validator(tmp_path):
    """AsyncNanaSQLite: table() で独自の validator を渡すと、そのスキーマが使われる。"""
    from validkit import v

    parent_schema = {"x": v.int()}
    child_schema = {"name": v.str(), "score": v.float()}
    async with AsyncNanaSQLite(str(tmp_path / "async_override.db"), validator=parent_schema) as db:
        scores_db = await db.table("scores", validator=child_schema)

        await scores_db.aset("s1", {"name": "Frank", "score": 9.5})
        assert await scores_db.aget("s1") == {"name": "Frank", "score": 9.5}

        with pytest.raises(NanaSQLiteValidationError):
            await scores_db.aset("s2", {"name": "Grace", "score": "not_a_float"})


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
@pytest.mark.asyncio
async def test_async_table_explicit_none_disables_parent_validator(tmp_path):
    """AsyncNanaSQLite: table(validator=None) を明示すると親のスキーマを無効化できる。"""
    from validkit import v

    parent_schema = {"name": v.str(), "age": v.int()}
    async with AsyncNanaSQLite(str(tmp_path / "async_disable.db"), validator=parent_schema) as db:
        free_db = await db.table("free_table", validator=None)

        # バリデーションなしなので任意の値を書き込める
        await free_db.aset("k", {"anything": True, "n": 99})
        assert (await free_db.aget("k"))["anything"] is True


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
@pytest.mark.asyncio
async def test_async_no_validator_allows_any_value(tmp_path):
    """AsyncNanaSQLite: validator を指定しない場合は任意の値を保存できる。"""
    async with AsyncNanaSQLite(str(tmp_path / "async_novalidator.db")) as db:
        await db.aset("misc", {"anything": [1, 2, 3], "flag": True})
        result = await db.aget("misc")
        assert result["flag"] is True


# ========================== batch_update() validation tests ==========================


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_batch_update_validates_all_before_writing(tmp_path):
    """batch_update() はすべての値をDB書き込み前に検証し、1件でも違反があれば何も書かない。"""
    from validkit import v

    schema = {"name": v.str(), "age": v.int()}
    db = NanaSQLite(str(tmp_path / "batch.db"), validator=schema)

    valid_mapping = {
        "u1": {"name": "Alice", "age": 30},
        "u2": {"name": "Bob", "age": "bad"},  # 不正な値
    }

    with pytest.raises(NanaSQLiteValidationError):
        db.batch_update(valid_mapping)

    # 1件でも失敗した場合、全件DBに書き込まれない（アトミックな失敗保証）
    assert "u1" not in db
    assert "u2" not in db


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_batch_update_all_valid_writes_all(tmp_path):
    """batch_update() は全値がバリデーションを通過すれば全件書き込む。"""
    from validkit import v

    schema = {"name": v.str(), "age": v.int()}
    db = NanaSQLite(str(tmp_path / "batch_valid.db"), validator=schema)

    db.batch_update({
        "u1": {"name": "Alice", "age": 30},
        "u2": {"name": "Bob", "age": 25},
    })

    assert db["u1"] == {"name": "Alice", "age": 30}
    assert db["u2"] == {"name": "Bob", "age": 25}


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
@pytest.mark.asyncio
async def test_async_batch_update_validates_all_before_writing(tmp_path):
    """AsyncNanaSQLite: batch_update() は1件でも違反があれば何も書かない。"""
    from validkit import v

    schema = {"name": v.str(), "age": v.int()}
    async with AsyncNanaSQLite(str(tmp_path / "async_batch.db"), validator=schema) as db:
        valid_mapping = {
            "u1": {"name": "Alice", "age": 30},
            "u2": {"name": "Bob", "age": "bad"},
        }

        with pytest.raises(NanaSQLiteValidationError):
            await db.abatch_update(valid_mapping)

        assert not await db.acontains("u1")
        assert not await db.acontains("u2")


# ========================== coerce mode tests ==========================


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_coerce_converts_value_on_setitem(tmp_path):
    """coerce=True のとき、__setitem__ が変換済みの値を保存する。"""
    from validkit import v

    schema = {"age": v.int().coerce()}
    db = NanaSQLite(str(tmp_path / "coerce.db"), validator=schema, coerce=True)

    db["user"] = {"age": "42"}  # 文字列 → int に自動変換
    assert db["user"] == {"age": 42}


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_no_coerce_keeps_original_value(tmp_path):
    """coerce=False（デフォルト）のとき、バリデーションは通っても元の値がそのまま保存される。"""
    from validkit import v

    schema = {"age": v.int()}
    db = NanaSQLite(str(tmp_path / "no_coerce.db"), validator=schema)

    db["user"] = {"age": 42}
    assert db["user"] == {"age": 42}


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_coerce_in_batch_update(tmp_path):
    """coerce=True のとき、batch_update() も変換済みの値を保存する。"""
    from validkit import v

    schema = {"score": v.float().coerce()}
    db = NanaSQLite(str(tmp_path / "batch_coerce.db"), validator=schema, coerce=True)

    db.batch_update({
        "a": {"score": "1.5"},
        "b": {"score": "2.0"},
    })

    assert db["a"] == {"score": 1.5}
    assert db["b"] == {"score": 2.0}


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_coerce_inherited_by_table(tmp_path):
    """coerce=True は table() で子テーブルに引き継がれる。"""
    from validkit import v

    schema = {"age": v.int().coerce()}
    db = NanaSQLite(str(tmp_path / "coerce_inherit.db"), validator=schema, coerce=True)
    child_db = db.table("child")

    child_db["c1"] = {"age": "7"}
    assert child_db["c1"] == {"age": 7}


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
def test_coerce_can_be_disabled_per_table(tmp_path):
    """table(coerce=False) で子テーブルの自動変換を無効にできる。"""
    from validkit import v

    schema = {"age": v.int()}
    db = NanaSQLite(str(tmp_path / "coerce_override.db"), validator=schema, coerce=True)
    child_db = db.table("child", coerce=False)

    # 子テーブルは coerce=False なので、変換なしで型が一致する値のみ受け付ける
    child_db["c1"] = {"age": 5}
    assert child_db["c1"] == {"age": 5}


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
@pytest.mark.asyncio
async def test_async_coerce_converts_value(tmp_path):
    """AsyncNanaSQLite: coerce=True のとき自動変換が有効になる。"""
    from validkit import v

    schema = {"age": v.int().coerce()}
    async with AsyncNanaSQLite(str(tmp_path / "async_coerce.db"), validator=schema, coerce=True) as db:
        await db.aset("user", {"age": "99"})
        assert await db.aget("user") == {"age": 99}


@pytest.mark.skipif(not validkit_installed, reason="validkit-py が未インストールのためスキップ")
@pytest.mark.asyncio
async def test_async_coerce_inherited_by_table(tmp_path):
    """AsyncNanaSQLite: coerce=True は table() で子テーブルに引き継がれる。"""
    from validkit import v

    schema = {"age": v.int().coerce()}
    async with AsyncNanaSQLite(str(tmp_path / "async_coerce_inherit.db"), validator=schema, coerce=True) as db:
        child_db = await db.table("child")
        await child_db.aset("c1", {"age": "3"})
        assert await child_db.aget("c1") == {"age": 3}

