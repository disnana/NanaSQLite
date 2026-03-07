"""TDD cycle 8 — Fix CI failures from test_tdd_cycle_7.py.

Issues found in CI:
1. Ruff I001: import block in test_tdd_cycle_7.py was unsorted (now fixed).
2. test_mypy_installed hard-asserts mypy is installed → fails in CI where mypy
   is not a test-job dependency (only a dev/lint dependency).

Fix:
1. ruff --fix applied (import sort).
2. test_mypy_installed must call _skip_if_mypy_not_installed() so it skips
   gracefully when mypy is absent, rather than failing with AssertionError.

TDD: all tests written BEFORE the fix is applied.
"""

import ast
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
TEST_CYCLE_7 = REPO_ROOT / "tests" / "test_tdd_cycle_7.py"


class TestRuffCleanCycle7:
    """tests/test_tdd_cycle_7.py must pass ruff check (I001 fix)."""

    def test_ruff_clean(self):
        """ruff check must report no errors on test_tdd_cycle_7.py."""
        if shutil.which("ruff") is None:
            pytest.skip("ruff not installed")
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", str(TEST_CYCLE_7)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"ruff errors in test_tdd_cycle_7.py:\n{result.stdout}"
        )


class TestMypyInstalledSkipsGracefully:
    """test_mypy_installed must skip (not fail) when mypy is absent."""

    def _get_test_mypy_installed_node(self) -> ast.FunctionDef:
        """Parse test_tdd_cycle_7.py and return the test_mypy_installed function node."""
        source = TEST_CYCLE_7.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ClassDef)
                and node.name == "TestMypyPassesWithEllipsisType"
            ):
                for item in node.body:
                    if (
                        isinstance(item, ast.FunctionDef)
                        and item.name == "test_mypy_installed"
                    ):
                        return item
        raise AssertionError(
            "test_mypy_installed not found in TestMypyPassesWithEllipsisType"
        )

    def test_mypy_installed_calls_skip_helper(self):
        """test_mypy_installed must call _skip_if_mypy_not_installed() so CI skips it."""
        func_node = self._get_test_mypy_installed_node()
        # Look for a call to _skip_if_mypy_not_installed in the function body
        skip_calls = [
            n
            for n in ast.walk(func_node)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == "_skip_if_mypy_not_installed"
        ]
        assert len(skip_calls) > 0, (
            "test_mypy_installed does not call _skip_if_mypy_not_installed(). "
            "Add _skip_if_mypy_not_installed() at the start of the function so it "
            "skips gracefully when mypy is absent in CI."
        )

    def test_mypy_installed_has_no_unconditional_hard_assert(self):
        """test_mypy_installed must not unconditionally assert mypy spec is not None."""
        func_node = self._get_test_mypy_installed_node()
        # Collect assert statements that check find_spec("mypy") is not None
        # before any skip call
        first_stmt = func_node.body[0] if func_node.body else None
        if first_stmt is None:
            return
        # If the very first statement is an unconditional assert on mypy's find_spec,
        # that is the pattern that fails in CI.
        if isinstance(first_stmt, ast.Assert):
            # Check if the test value is a comparison involving find_spec
            test_src = ast.unparse(first_stmt.test)
            assert "find_spec" not in test_src or "_skip_if" in "".join(
                ast.unparse(n) for n in func_node.body
            ), (
                "test_mypy_installed starts with an unconditional assert on "
                "importlib.util.find_spec('mypy'), which fails in CI when mypy is "
                "not installed. Use _skip_if_mypy_not_installed() instead."
            )
