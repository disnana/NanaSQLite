"""TDD cycle 9: docs validator type annotation should match implementation.

Problem: All four docs files show `validator: dict | Any | None` in the
`__init__` and `table()` signatures, but the implementation uses
`validator: Any | None` (redundant `dict |` was removed in cycle 6).

Tests are written first (all expected to FAIL before the fix).
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOCS_EN_NANASQLITE = REPO_ROOT / "docs" / "en" / "api" / "nanasqlite.md"
DOCS_JA_NANASQLITE = REPO_ROOT / "docs" / "ja" / "api" / "nanasqlite.md"
DOCS_EN_ASYNC = REPO_ROOT / "docs" / "en" / "api" / "async_nanasqlite.md"
DOCS_JA_ASYNC = REPO_ROOT / "docs" / "ja" / "api" / "async_nanasqlite.md"

REDUNDANT_TYPE = "dict | Any | None"


class TestDocsValidatorTypeNanaSQLite:
    """NanaSQLite docs must not contain redundant `dict | Any | None`."""

    def test_en_nanasqlite_init_validator_no_dict_prefix(self) -> None:
        """docs/en/api/nanasqlite.md __init__ signature: validator should be Any | None, not dict | Any | None."""
        content = DOCS_EN_NANASQLITE.read_text(encoding="utf-8")
        assert REDUNDANT_TYPE not in content, (
            f"Found redundant `{REDUNDANT_TYPE}` in {DOCS_EN_NANASQLITE}. "
            "Should be `Any | None` to match the implementation."
        )

    def test_ja_nanasqlite_init_validator_no_dict_prefix(self) -> None:
        """docs/ja/api/nanasqlite.md __init__ signature: validator should be Any | None, not dict | Any | None."""
        content = DOCS_JA_NANASQLITE.read_text(encoding="utf-8")
        assert REDUNDANT_TYPE not in content, (
            f"Found redundant `{REDUNDANT_TYPE}` in {DOCS_JA_NANASQLITE}. "
            "Should be `Any | None` to match the implementation."
        )


class TestDocsValidatorTypeAsyncNanaSQLite:
    """AsyncNanaSQLite docs must not contain redundant `dict | Any | None`."""

    def test_en_async_nanasqlite_init_validator_no_dict_prefix(self) -> None:
        """docs/en/api/async_nanasqlite.md __init__ signature: validator should be Any | None."""
        content = DOCS_EN_ASYNC.read_text(encoding="utf-8")
        assert REDUNDANT_TYPE not in content, (
            f"Found redundant `{REDUNDANT_TYPE}` in {DOCS_EN_ASYNC}. "
            "Should be `Any | None` to match the implementation."
        )

    def test_ja_async_nanasqlite_init_validator_no_dict_prefix(self) -> None:
        """docs/ja/api/async_nanasqlite.md __init__ signature: validator should be Any | None."""
        content = DOCS_JA_ASYNC.read_text(encoding="utf-8")
        assert REDUNDANT_TYPE not in content, (
            f"Found redundant `{REDUNDANT_TYPE}` in {DOCS_JA_ASYNC}. "
            "Should be `Any | None` to match the implementation."
        )
