"""Documentation regression tests for the validation guide."""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def assert_contains_all(path: Path, snippets: list[str]) -> None:
    """Assert that a documentation file contains all expected snippets."""
    content = path.read_text(encoding="utf-8")
    for snippet in snippets:
        assert snippet in content, f"Expected to find {snippet!r} in {path}"


class TestStructuredDocsValidationGuide:
    """The parallel docs/en and docs/ja trees should expose the validation guide."""

    def test_en_validation_guide_exists_with_core_topics(self) -> None:
        guide = REPO_ROOT / "docs" / "en" / "guide" / "validation.md"
        assert guide.exists(), f"Missing validation guide: {guide}"
        assert_contains_all(
            guide,
            [
                "validkit-py",
                "pip install nanasqlite[validation]",
                "coerce=True",
                "batch_update()",
                "HAS_VALIDKIT",
            ],
        )

    def test_ja_validation_guide_exists_with_core_topics(self) -> None:
        guide = REPO_ROOT / "docs" / "ja" / "guide" / "validation.md"
        assert guide.exists(), f"Missing validation guide: {guide}"
        assert_contains_all(
            guide,
            [
                "validkit-py",
                "pip install nanasqlite[validation]",
                "coerce=True",
                "batch_update()",
                "HAS_VALIDKIT",
            ],
        )

    def test_readmes_link_to_validation_guide(self) -> None:
        assert_contains_all(
            REPO_ROOT / "docs" / "en" / "README.md",
            ["guide/validation.md", "[Validation]"],
        )
        assert_contains_all(
            REPO_ROOT / "docs" / "ja" / "README.md",
            ["guide/validation.md", "[バリデーション]"],
        )


class TestSiteValidationGuide:
    """The published VitePress site should expose the validation guide."""

    def test_site_validation_guides_exist(self) -> None:
        assert_contains_all(
            REPO_ROOT / "docs" / "site" / "en" / "validation_guide.md",
            ["validkit-py", "pip install nanasqlite[validation]", "coerce=True"],
        )
        assert_contains_all(
            REPO_ROOT / "docs" / "site" / "validation_guide.md",
            ["validkit-py", "pip install nanasqlite[validation]", "coerce=True"],
        )

    def test_site_sidebar_links_include_validation_guide(self) -> None:
        config = REPO_ROOT / "docs" / "site" / ".vitepress" / "config.mts"
        assert_contains_all(
            config,
            [
                "/validation_guide",
                "/en/validation_guide",
            ],
        )
