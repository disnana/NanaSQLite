"""
TDD cycle 10: test_validkit_integration.py should use nanasqlite.HAS_VALIDKIT
for skip logic, not `import validkit` directly.

The issue: `import validkit` succeeds even if `from validkit import validate`
fails (e.g., wrong package version). NanaSQLite's HAS_VALIDKIT is set by
trying `from validkit import validate`, so tests should use HAS_VALIDKIT as
the skip sentinel to accurately reflect whether integration is available.
"""
import inspect
import re

import pytest


def _get_integration_test_source() -> str:
    """tests/test_validkit_integration.py のソースコードを返す。"""
    import test_validkit_integration as mod

    return inspect.getsource(mod)


def test_integration_file_imports_has_validkit_from_nanasqlite():
    """test_validkit_integration.py がモジュールレベルで HAS_VALIDKIT を nanasqlite からインポートすること。"""
    src = _get_integration_test_source()
    # HAS_VALIDKIT が nanasqlite インポート文に含まれているか確認
    assert re.search(
        r"from nanasqlite import.*HAS_VALIDKIT",
        src,
        re.MULTILINE,
    ), "test_validkit_integration.py should import HAS_VALIDKIT from nanasqlite at module level"


def test_integration_file_uses_has_validkit_as_skip_flag():
    """test_validkit_integration.py が validkit_installed = HAS_VALIDKIT で skip フラグを設定すること。"""
    src = _get_integration_test_source()
    # validkit_installed が HAS_VALIDKIT に基づいていること
    assert re.search(
        r"validkit_installed\s*=\s*HAS_VALIDKIT",
        src,
    ), "test_validkit_integration.py: validkit_installed should be set to HAS_VALIDKIT"


def test_integration_file_does_not_use_bare_import_validkit_for_detection():
    """test_validkit_integration.py がスキップ判定のために `import validkit` を直接使わないこと。"""
    src = _get_integration_test_source()
    # try: import validkit ... validkit_installed = True のパターンが無いことを確認
    pattern = r"try:\s*\n\s+import validkit.*\n\s+validkit_installed\s*=\s*True"
    assert not re.search(
        pattern,
        src,
        re.MULTILINE,
    ), "test_validkit_integration.py should not use `import validkit` to set validkit_installed"


def test_has_validkit_consistency_with_integration_skip_flag():
    """nanasqlite.HAS_VALIDKIT と test_validkit_integration.validkit_installed が一致すること。"""
    import test_validkit_integration as mod

    from nanasqlite import HAS_VALIDKIT

    assert mod.validkit_installed is HAS_VALIDKIT, (
        f"validkit_installed ({mod.validkit_installed}) must equal "
        f"nanasqlite.HAS_VALIDKIT ({HAS_VALIDKIT}). "
        "Use HAS_VALIDKIT directly as the skip flag."
    )


@pytest.mark.parametrize(
    "test_name",
    [
        "test_validator_accepts_valid_value",
        "test_validator_rejects_invalid_value",
        "test_batch_update_validates_all_before_writing",
    ],
)
def test_skip_markers_reference_validkit_installed(test_name: str):
    """各テストの skipif マーカーが validkit_installed を参照していること。"""
    src = _get_integration_test_source()
    # skipif の条件が validkit_installed を使っているかチェック
    pattern = rf"@pytest\.mark\.skipif\(not validkit_installed.*\)\s*\ndef {test_name}"
    assert re.search(pattern, src, re.MULTILINE), (
        f"{test_name} should use `not validkit_installed` in its skipif marker"
    )
