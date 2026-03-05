"""TDD cycle 4: batch_update() optimization.

The code review identified that batch_update() builds a full coerced_mapping dict
even when self._coerce is False, wasting O(n) memory/time.

These tests are written FIRST (they should FAIL before the fix).
After the fix they must all PASS.
"""
import inspect

import pytest

from nanasqlite import NanaSQLite


class TestBatchUpdateCodeStructure:
    """Verify batch_update() has the optimized two-path structure."""

    def test_batch_update_does_not_use_ternary_coerce_pattern(self):
        """batch_update should NOT use 'coerced if self._coerce else value' anti-pattern.

        The optimized code separates the coerce vs validate-only loops entirely,
        so no unnecessary dict allocation occurs when coerce=False.
        """
        source = inspect.getsource(NanaSQLite.batch_update)
        assert "coerced if self._coerce else value" not in source, (
            "batch_update() should not build an unnecessary dict when coerce=False. "
            "Use separate code paths: build coerced_mapping only when self._coerce is True."
        )

    def test_batch_update_has_separate_coerce_branch(self):
        """batch_update should have an explicit 'if self._coerce:' branch."""
        source = inspect.getsource(NanaSQLite.batch_update)
        assert "if self._coerce:" in source, (
            "batch_update() should have an explicit 'if self._coerce:' branch "
            "to avoid unnecessary dict allocation when not coercing."
        )

    def test_batch_update_validate_only_branch_does_not_store_coerced(self):
        """The validate-only branch must not store coerced values in a new dict.

        When coerce=False, validation should iterate and call validkit_validate
        without allocating a new mapping dict.
        """
        source = inspect.getsource(NanaSQLite.batch_update)
        # The validate-only (else) branch must not contain 'coerced_mapping[key] = '
        # after the 'else:' for the self._coerce check.
        # A simpler check: the source should NOT have both 'coerced_mapping[key] ='
        # in a context where self._coerce is False.
        # We verify by checking that the logic separates coerce and validate-only.
        # The old pattern is: single loop with 'coerced_mapping[key] = coerced if self._coerce else value'
        # The new pattern must not have this combined ternary.
        assert "coerced if self._coerce else value" not in source, (
            "The validate-only path should not store values in a new dict. "
            "Only the coerce path (if self._coerce:) should build coerced_mapping."
        )


class TestBatchUpdateBehaviourWithMockedValidkit:
    """Verify batch_update() behavior with a mock validator (validkit not installed)."""

    def _patch_validkit(self, monkeypatch, mock_fn):
        """Helper: enable HAS_VALIDKIT and patch validkit_validate on the module."""
        import nanasqlite.core as core_module

        monkeypatch.setattr(core_module, "HAS_VALIDKIT", True)
        # validkit_validate may not exist as a module attr when validkit is absent
        monkeypatch.setattr(core_module, "validkit_validate", mock_fn, raising=False)

    def test_batch_update_coerce_false_preserves_original_values(self, tmp_path, monkeypatch):
        """With coerce=False and a validator, batch_update should store original values."""
        coerced_sentinel = object()
        calls: list[tuple] = []

        def mock_validate(value, schema):
            calls.append((value, schema))
            return coerced_sentinel  # always return a different object

        self._patch_validkit(monkeypatch, mock_validate)

        db_path = str(tmp_path / "test_coerce_false.db")
        db = NanaSQLite(db_path, validator={"type": "string"}, coerce=False)

        db.batch_update({"key1": "hello", "key2": "world"})

        # Validator should have been called for each key
        assert len(calls) == 2

        # Original values (not coerced_sentinel) should be stored
        assert db["key1"] == "hello"
        assert db["key2"] == "world"

    def test_batch_update_coerce_true_stores_coerced_values(self, tmp_path, monkeypatch):
        """With coerce=True and a validator, batch_update should store coerced values."""

        def mock_validate(value, schema):
            return str(value) + "_coerced"

        self._patch_validkit(monkeypatch, mock_validate)

        db_path = str(tmp_path / "test_coerce_true.db")
        db = NanaSQLite(db_path, validator={"type": "string"}, coerce=True)

        db.batch_update({"key1": "hello", "key2": "world"})

        # Coerced values should be stored
        assert db["key1"] == "hello_coerced"
        assert db["key2"] == "world_coerced"

    def test_batch_update_validates_all_before_writing_when_coerce_false(
        self, tmp_path, monkeypatch
    ):
        """batch_update with coerce=False must validate all items atomically.

        If any item fails validation, nothing should be written.
        """
        from nanasqlite.exceptions import NanaSQLiteValidationError

        def mock_validate(value, schema):
            if value == "bad":
                raise ValueError("invalid value")
            return value

        self._patch_validkit(monkeypatch, mock_validate)

        db_path = str(tmp_path / "test_atomic.db")
        db = NanaSQLite(db_path, validator={"type": "string"}, coerce=False)

        with pytest.raises(NanaSQLiteValidationError):
            db.batch_update({"key1": "good", "key2": "bad", "key3": "also_good"})

        # Nothing should be written because validation failed
        assert "key1" not in db
        assert "key2" not in db
        assert "key3" not in db

    def test_batch_update_validates_all_before_writing_when_coerce_true(
        self, tmp_path, monkeypatch
    ):
        """batch_update with coerce=True must validate all items atomically.

        If any item fails coercion, nothing should be written.
        """
        from nanasqlite.exceptions import NanaSQLiteValidationError

        def mock_validate(value, schema):
            if value == "bad":
                raise ValueError("invalid value")
            return str(value) + "_coerced"

        self._patch_validkit(monkeypatch, mock_validate)

        db_path = str(tmp_path / "test_atomic_coerce.db")
        db = NanaSQLite(db_path, validator={"type": "string"}, coerce=True)

        with pytest.raises(NanaSQLiteValidationError):
            db.batch_update({"key1": "good", "key2": "bad", "key3": "also_good"})

        # Nothing should be written because coercion failed
        assert "key1" not in db
        assert "key2" not in db
        assert "key3" not in db
