import warnings

import pytest

from nanasqlite import NanaSQLite


@pytest.fixture(autouse=True)
def clear_table_instance_registry():
    with NanaSQLite._table_instance_registry_lock:
        NanaSQLite._table_instance_registry.clear()
    yield
    with NanaSQLite._table_instance_registry_lock:
        NanaSQLite._table_instance_registry.clear()


def test_duplicate_table_instance_warns_once_for_live_instance(tmp_path):
    db = NanaSQLite(str(tmp_path / "db.db"))
    first = db.table("users")

    with pytest.warns(UserWarning, match="already has an active NanaSQLite table"):
        second = db.table("users")

    first["a"] = 1
    second["b"] = 2
    assert first["a"] == 1
    assert second["b"] == 2
    db.close()


def test_first_table_instance_does_not_warn(tmp_path):
    db = NanaSQLite(str(tmp_path / "db.db"))

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        child = db.table("users")

    assert caught == []
    child["k"] = "v"
    assert child["k"] == "v"
    db.close()


def test_duplicate_table_warning_can_be_disabled_per_call(tmp_path):
    db = NanaSQLite(str(tmp_path / "db.db"))
    db.table("users")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        db.table("users", warn_duplicate_table_instance=False)

    assert caught == []
    db.close()


def test_closed_table_instance_is_unregistered(tmp_path):
    db = NanaSQLite(str(tmp_path / "db.db"))
    first = db.table("users")
    first.close()

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        second = db.table("users")

    assert caught == []
    second["k"] = "v"
    assert second["k"] == "v"
    db.close()
