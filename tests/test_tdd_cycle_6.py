"""TDD cycle 6 — 2 items from code review after cycle 5.

Issues to address:
1. NanaSQLite.__init__ validator: dict | Any | None — `dict |` is redundant (Any subsumes dict)
   → Simplify to validator: Any | None
2. NanaSQLite.table() and AsyncNanaSQLite.table() use `dict | Any | None` / `bool | Any`
   with `# type: ignore[assignment]` — sentinel _UNSET is already Ellipsis, so use
   types.EllipsisType to properly type it, removing the need for type: ignore[assignment]

TDD: all tests written BEFORE fixes are applied.
"""

import inspect
import types

from nanasqlite import NanaSQLite
from nanasqlite.async_core import AsyncNanaSQLite


class TestInitValidatorAnnotation:
    """NanaSQLite.__init__ validator annotation should be Any | None, not dict | Any | None."""

    def test_init_validator_annotation_has_no_redundant_dict(self):
        """dict | is redundant with Any — annotation should be Any | None."""
        sig = inspect.signature(NanaSQLite.__init__)
        ann = sig.parameters["validator"].annotation
        ann_str = str(ann)
        # Should NOT contain 'dict' (redundant since Any already subsumes it)
        assert "dict" not in ann_str, (
            f"__init__ validator annotation '{ann_str}' still contains redundant 'dict |'"
        )

    def test_async_init_validator_annotation_has_no_redundant_dict(self):
        """AsyncNanaSQLite.__init__ same fix."""
        sig = inspect.signature(AsyncNanaSQLite.__init__)
        ann = sig.parameters["validator"].annotation
        ann_str = str(ann)
        assert "dict" not in ann_str, (
            f"AsyncNanaSQLite.__init__ validator annotation '{ann_str}' contains redundant 'dict |'"
        )


class TestTableSentinelTypeAnnotation:
    """table() validator/coerce annotations should use EllipsisType for sentinel, no type: ignore."""

    def test_table_source_has_no_type_ignore_for_validator(self):
        """After using EllipsisType, type: ignore[assignment] should be gone for validator."""
        source = inspect.getsource(NanaSQLite.table)
        # Neither validator nor coerce should need type: ignore[assignment]
        assert "type: ignore[assignment]" not in source, (
            "NanaSQLite.table() still has '# type: ignore[assignment]' — "
            "use types.EllipsisType for sentinel annotation to fix this"
        )

    def test_async_table_source_has_no_type_ignore_for_validator(self):
        """AsyncNanaSQLite.table() same fix."""
        source = inspect.getsource(AsyncNanaSQLite.table)
        assert "type: ignore[assignment]" not in source, (
            "AsyncNanaSQLite.table() still has '# type: ignore[assignment]'"
        )

    def test_table_validator_annotation_includes_ellipsis_type(self):
        """validator in table() should allow EllipsisType as a valid annotation."""
        sig = inspect.signature(NanaSQLite.table)
        ann = sig.parameters["validator"].annotation
        # The annotation string should reference EllipsisType or ellipsis
        ann_str = str(ann)
        assert "ellipsis" in ann_str.lower() or "EllipsisType" in ann_str, (
            f"NanaSQLite.table() validator annotation '{ann_str}' does not include EllipsisType"
        )

    def test_table_coerce_annotation_includes_ellipsis_type(self):
        """coerce in table() should allow EllipsisType as a valid annotation."""
        sig = inspect.signature(NanaSQLite.table)
        ann = sig.parameters["coerce"].annotation
        ann_str = str(ann)
        assert "ellipsis" in ann_str.lower() or "EllipsisType" in ann_str, (
            f"NanaSQLite.table() coerce annotation '{ann_str}' does not include EllipsisType"
        )

    def test_async_table_validator_annotation_includes_ellipsis_type(self):
        """AsyncNanaSQLite.table() validator annotation should include EllipsisType."""
        sig = inspect.signature(AsyncNanaSQLite.table)
        ann = sig.parameters["validator"].annotation
        ann_str = str(ann)
        assert "ellipsis" in ann_str.lower() or "EllipsisType" in ann_str, (
            f"AsyncNanaSQLite.table() validator annotation '{ann_str}' does not include EllipsisType"
        )

    def test_async_table_coerce_annotation_includes_ellipsis_type(self):
        """AsyncNanaSQLite.table() coerce annotation should include EllipsisType."""
        sig = inspect.signature(AsyncNanaSQLite.table)
        ann = sig.parameters["coerce"].annotation
        ann_str = str(ann)
        assert "ellipsis" in ann_str.lower() or "EllipsisType" in ann_str, (
            f"AsyncNanaSQLite.table() coerce annotation '{ann_str}' does not include EllipsisType"
        )

    def test_table_validator_annotation_has_no_redundant_dict(self):
        """dict | is redundant in table() too."""
        sig = inspect.signature(NanaSQLite.table)
        ann = sig.parameters["validator"].annotation
        ann_str = str(ann)
        assert "dict" not in ann_str, (
            f"NanaSQLite.table() validator annotation '{ann_str}' still has redundant 'dict |'"
        )

    def test_async_table_validator_annotation_has_no_redundant_dict(self):
        """AsyncNanaSQLite.table() same."""
        sig = inspect.signature(AsyncNanaSQLite.table)
        ann = sig.parameters["validator"].annotation
        ann_str = str(ann)
        assert "dict" not in ann_str, (
            f"AsyncNanaSQLite.table() validator annotation '{ann_str}' still has redundant 'dict |'"
        )


class TestBehavioralSanityAfterAnnotationChange:
    """Ensure annotation changes don't break runtime behavior."""

    def test_table_validator_default_is_ellipsis(self):
        """Sentinel must remain Ellipsis after annotation change."""
        sig = inspect.signature(NanaSQLite.table)
        default = sig.parameters["validator"].default
        assert default is ..., f"table() validator default should be ... but got {default!r}"

    def test_table_coerce_default_is_ellipsis(self):
        """Sentinel must remain Ellipsis after annotation change."""
        sig = inspect.signature(NanaSQLite.table)
        default = sig.parameters["coerce"].default
        assert default is ..., f"table() coerce default should be ... but got {default!r}"

    def test_init_validator_default_is_none(self):
        """__init__ validator default should remain None."""
        sig = inspect.signature(NanaSQLite.__init__)
        default = sig.parameters["validator"].default
        assert default is None, f"__init__ validator default should be None but got {default!r}"

    def test_ellipsis_type_is_available(self):
        """Confirm types.EllipsisType is available in this Python version."""
        assert hasattr(types, "EllipsisType"), "types.EllipsisType not available (need Python 3.10+)"
        assert isinstance(..., types.EllipsisType), "... should be instance of EllipsisType"
