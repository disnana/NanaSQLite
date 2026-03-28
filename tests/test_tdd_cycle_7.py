"""TDD cycle 7 — Fix mypy rejection of types.EllipsisType.

Issue:
  mypy (python_version = "3.9") does not know types.EllipsisType, which was
  added in Python 3.10.  Running `mypy src/nanasqlite/core.py` produces:

      error: Name "types.EllipsisType" is not defined  [name-defined]

  Fix: update [tool.mypy] python_version from "3.8" to "3.9" in pyproject.toml
  (Python 3.9 is now the target).

TDD: all tests written BEFORE the fix is applied.
"""

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"


def _run_mypy(*src_paths: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "mypy", *src_paths],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )


def _skip_if_mypy_not_installed() -> None:
    """Skip the current test if mypy is not available in the environment."""
    import pytest

    if shutil.which("mypy") is None and not importlib.util.find_spec("mypy"):
        pytest.skip("mypy not installed")


class TestMypyPassesWithEllipsisType:
    """mypy must not report name-defined errors for types.EllipsisType."""

    def test_mypy_installed(self):
        """Mypy must be importable (installed in the test environment)."""
        _skip_if_mypy_not_installed()
        assert importlib.util.find_spec("mypy") is not None, (
            "mypy is not installed — install it to run type-checking tests"
        )

    def test_mypy_no_name_defined_error_in_core(self):
        """mypy must not report 'Name types.EllipsisType is not defined' in core.py."""
        _skip_if_mypy_not_installed()

        result = _run_mypy("src/nanasqlite/core.py")
        name_defined_errors = [
            line for line in result.stdout.splitlines() if "EllipsisType" in line and "name-defined" in line
        ]
        assert name_defined_errors == [], (
            "mypy reports name-defined errors for types.EllipsisType in core.py:\n"
            + "\n".join(name_defined_errors)
            + "\nFix: ensure python_version is set correctly in pyproject.toml [tool.mypy]"
        )

    def test_mypy_no_name_defined_error_in_async_core(self):
        """mypy must not report 'Name types.EllipsisType is not defined' in async_core.py."""
        _skip_if_mypy_not_installed()

        result = _run_mypy("src/nanasqlite/async_core.py")
        name_defined_errors = [
            line for line in result.stdout.splitlines() if "EllipsisType" in line and "name-defined" in line
        ]
        assert name_defined_errors == [], (
            "mypy reports name-defined errors for types.EllipsisType in async_core.py:\n"
            + "\n".join(name_defined_errors)
            + "\nFix: ensure python_version is set correctly in pyproject.toml [tool.mypy]"
        )

    def test_mypy_python_version_in_config_is_at_least_39(self):
        """[tool.mypy] python_version must be >= '3.9' to support Python 3.9+ environments."""
        content = PYPROJECT.read_text()
        # Find the python_version setting under [tool.mypy]
        in_mypy_section = False
        for line in content.splitlines():
            if line.strip() == "[tool.mypy]":
                in_mypy_section = True
                continue
            if in_mypy_section and line.startswith("["):
                # Entered next section without finding python_version
                break
            if in_mypy_section and line.strip().startswith("python_version"):
                # e.g. python_version = "3.9"
                version_str = line.split("=", 1)[1].strip().strip('"').strip("'")
                major, minor = map(int, version_str.split(".")[:2])
                assert (major, minor) >= (3, 9), (
                    f"[tool.mypy] python_version = '{version_str}' is too old. Update to '3.9' or higher."
                )
                return
        # If we reach here, python_version was not found in [tool.mypy]
        raise AssertionError("python_version not found in [tool.mypy] section of pyproject.toml")
