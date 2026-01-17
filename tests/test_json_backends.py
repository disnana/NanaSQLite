import importlib.util
import json
import sqlite3

import pytest

from nanasqlite import NanaSQLite


def test_plaintext_storage_is_text_and_roundtrip(tmp_path):
    """非暗号化の保存形式は常にTEXT(str)で、orjson有無に関わらず往復できる。"""
    db_path = str(tmp_path / "backend_plaintext.db")
    db = NanaSQLite(db_path)

    value = {
        "msg": "こんにちは🌸",
        "nums": [1, 2, 3],
        "nested": {"ok": True, "n": None},
    }

    db["k"] = value
    assert db["k"] == value

    # DBの実体がTEXT(str)であることを確認し、json.loadsで復元できることを検証
    conn = sqlite3.connect(db_path)
    raw = conn.execute("SELECT value FROM data WHERE key=?", ("k",)).fetchone()[0]
    conn.close()

    assert isinstance(raw, str)
    assert json.loads(raw) == value


def test_backend_flag_orjson_present():
    """orjson がインストールされている環境では HAS_ORJSON が True。"""
    pytest.importorskip("orjson")
    from nanasqlite import core as core_mod  # noqa: WPS433 (import inside test)

    assert getattr(core_mod, "HAS_ORJSON", False) is True


@pytest.mark.skipif(
    importlib.util.find_spec("orjson") is not None,
    reason="このテストは orjson 未インストール環境でのみ実行します",
)
def test_backend_flag_std_json_when_orjson_missing():
    """orjson が無い環境では HAS_ORJSON が False。"""
    from nanasqlite import core as core_mod  # noqa: WPS433 (import inside test)

    assert getattr(core_mod, "HAS_ORJSON", True) is False
