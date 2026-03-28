"""TDD cycle 5 — 3 items from code review after cycle 4.

Issues to address:
1. NanaSQLite.table() shows <object object at 0x...> as default for validator/coerce
   → Change _UNSET sentinel to Ellipsis (...) so inspect.signature is user-readable
2. AsyncNanaSQLite.table() has the same sentinel issue
3. test_validkit_integration.py: variable named 'valid_mapping' contains an invalid entry
   → Rename to 'mapping_with_invalid' for clarity

Run BEFORE fixes → all fail.
Run AFTER fixes → all pass.
"""

import inspect
import pathlib


class TestTableSignatureUsesEllipsis:
    """NanaSQLite.table() should use Ellipsis as the sentinel for validator/coerce."""

    def test_table_validator_default_is_ellipsis(self):
        from nanasqlite import NanaSQLite

        sig = inspect.signature(NanaSQLite.table)
        default = sig.parameters["validator"].default
        assert default is ..., (
            f"NanaSQLite.table() validator default should be Ellipsis (...), got {default!r}. "
            "Using object() leaks an opaque sentinel into the public signature."
        )

    def test_table_coerce_default_is_ellipsis(self):
        from nanasqlite import NanaSQLite

        sig = inspect.signature(NanaSQLite.table)
        default = sig.parameters["coerce"].default
        assert default is ..., f"NanaSQLite.table() coerce default should be Ellipsis (...), got {default!r}."

    def test_table_validator_default_is_not_opaque_object(self):
        """Regression: ensure the sentinel is not an opaque object()."""
        from nanasqlite import NanaSQLite

        sig = inspect.signature(NanaSQLite.table)
        default = sig.parameters["validator"].default
        assert repr(default) != "<object object at ...>", "Should not be opaque object()"
        # More direct check: type should not be 'object'
        assert type(default) is not object, "Default is still a raw object() sentinel; should be Ellipsis"


class TestAsyncTableSignatureUsesEllipsis:
    """AsyncNanaSQLite.table() should use Ellipsis as the sentinel for validator/coerce."""

    def test_async_table_validator_default_is_ellipsis(self):
        from nanasqlite.async_core import AsyncNanaSQLite

        sig = inspect.signature(AsyncNanaSQLite.table)
        default = sig.parameters["validator"].default
        assert default is ..., f"AsyncNanaSQLite.table() validator default should be Ellipsis (...), got {default!r}."

    def test_async_table_coerce_default_is_ellipsis(self):
        from nanasqlite.async_core import AsyncNanaSQLite

        sig = inspect.signature(AsyncNanaSQLite.table)
        default = sig.parameters["coerce"].default
        assert default is ..., f"AsyncNanaSQLite.table() coerce default should be Ellipsis (...), got {default!r}."

    def test_async_table_validator_default_is_not_opaque_object(self):
        from nanasqlite.async_core import AsyncNanaSQLite

        sig = inspect.signature(AsyncNanaSQLite.table)
        default = sig.parameters["validator"].default
        assert type(default) is not object, (
            "AsyncNanaSQLite.table() default is still a raw object() sentinel; should be Ellipsis"
        )


class TestEllipsisSentinelBehavior:
    """Functional tests: Ellipsis sentinel correctly triggers inheritance."""

    def test_table_inherits_validator_when_ellipsis(self, tmp_path):
        """When validator=... (default), child inherits parent's validator."""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(str(tmp_path / "test.db"))
        child = db.table("child")
        # With Ellipsis sentinel, child inherits parent's validator (None in this case)
        assert child._validator == db._validator

    def test_table_overrides_validator_when_none(self, tmp_path):
        """When validator=None explicitly, child sets validator to None (clears parent)."""
        from nanasqlite import NanaSQLite

        db = NanaSQLite(str(tmp_path / "test.db"))
        # Explicitly passing None should still work as an override
        child = db.table("child", validator=None)
        assert child._validator is None


class TestValidkitIntegrationVariableNaming:
    """The variable 'valid_mapping' in test_validkit_integration.py is misleading
    because it actually contains invalid data. It should be renamed."""

    def test_misleading_variable_name_not_in_test_file(self):
        """Check that the misleading name 'valid_mapping' is not used in
        test_batch_update_validates_all_before_writing."""
        test_file = pathlib.Path(__file__).parent / "test_validkit_integration.py"
        source = test_file.read_text(encoding="utf-8")

        # Find the relevant function
        func_start = source.find("def test_batch_update_validates_all_before_writing")
        assert func_start != -1, "Function not found in test file"

        # Find the next function definition after this one
        next_def = source.find("\ndef ", func_start + 1)
        if next_def == -1:
            func_body = source[func_start:]
        else:
            func_body = source[func_start:next_def]

        assert "valid_mapping" not in func_body, (
            "Variable 'valid_mapping' is misleadingly named in "
            "test_batch_update_validates_all_before_writing — it contains invalid data. "
            "Rename to 'mapping_with_invalid' or similar."
        )

    def test_misleading_variable_name_not_in_async_test_func(self):
        """Same check for async variant."""
        test_file = pathlib.Path(__file__).parent / "test_validkit_integration.py"
        source = test_file.read_text(encoding="utf-8")

        func_start = source.find("async def test_async_batch_update_validates_all_before_writing")
        assert func_start != -1, "Async function not found in test file"

        next_def = source.find("\ndef ", func_start + 1)
        next_async_def = source.find("\nasync def ", func_start + 1)
        end = min(x for x in [next_def, next_async_def, len(source)] if x > func_start)
        func_body = source[func_start:end]

        assert "valid_mapping" not in func_body, (
            "Variable 'valid_mapping' is misleadingly named in async test function — "
            "rename to 'mapping_with_invalid' or similar."
        )
