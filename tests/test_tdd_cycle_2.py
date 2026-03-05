"""TDD cycle 2: 失敗するテストを書いてから修正する。

対象の問題（コードレビューコメント from 54c4a16）:
1. NanaSQLite.__init__ の validator デフォルトが _UNSET → None に変更すべき
   (コンストラクターに「親から継承」の概念はないため)
2. table() に cache_ttl / cache_persistence_ttl パラメーターを追加すべき
   (親が非 TTL の場合でも cache_strategy=TTL で table() を呼べるよう)
3. test_table_inheritance_comprehensive.py に未使用 `import time` (Ruff F401)
4. test_tdd_review_fixes.py に未使用 `import pytest` (Ruff F401)
5. test_table_inheritance_comprehensive.py に未使用 `NanaSQLiteValidationError` (Ruff F401)
"""
from __future__ import annotations

import inspect
import subprocess
import sys
from pathlib import Path

import pytest

from nanasqlite import CacheType, NanaSQLite

REPO_ROOT = Path(__file__).parent.parent


class TestNanaSQLiteInitValidatorDefault:
    """NanaSQLite.__init__ の validator デフォルトが None であることを確認する。"""

    def test_validator_default_is_none(self):
        """NanaSQLite.__init__ の validator パラメーターのデフォルトが None であること。

        _UNSET は table() での「省略 = 親継承」セマンティクスのためのセンチネルであり、
        コンストラクターでは親から継承する概念がないため、None をデフォルトにすべき。
        """
        sig = inspect.signature(NanaSQLite.__init__)
        validator_param = sig.parameters.get("validator")
        assert validator_param is not None, "NanaSQLite.__init__ に validator パラメーターが存在しない"
        default = validator_param.default
        assert default is None, (
            f"NanaSQLite.__init__ の validator デフォルトが None ではなく {default!r} になっている。"
            " _UNSET は table() 専用のセンチネルであり、コンストラクターでは None を使用すべき。"
        )

    def test_no_validator_means_no_validation(self, tmp_path):
        """引数なしで NanaSQLite を生成すると _validator が None になること。"""
        db = NanaSQLite(str(tmp_path / "test.db"), table="t")
        assert db._validator is None

    def test_explicit_none_validator_works(self, tmp_path):
        """validator=None を明示的に渡すと _validator が None になること。"""
        db = NanaSQLite(str(tmp_path / "test.db"), table="t", validator=None)
        assert db._validator is None


class TestTableCacheTTLParam:
    """table() に cache_ttl / cache_persistence_ttl パラメーターがあることを確認する。"""

    def test_table_signature_has_cache_ttl(self):
        """table() に cache_ttl パラメーターが存在すること。"""
        sig = inspect.signature(NanaSQLite.table)
        assert "cache_ttl" in sig.parameters, (
            "NanaSQLite.table() に cache_ttl パラメーターが存在しない。"
            " 親が非TTLの場合でも cache_strategy=TTL で table() を呼べるよう追加してください。"
        )

    def test_table_signature_has_cache_persistence_ttl(self):
        """table() に cache_persistence_ttl パラメーターが存在すること。"""
        sig = inspect.signature(NanaSQLite.table)
        assert "cache_persistence_ttl" in sig.parameters, (
            "NanaSQLite.table() に cache_persistence_ttl パラメーターが存在しない。"
        )

    def test_table_can_set_ttl_strategy_on_non_ttl_parent(self, tmp_path):
        """非TTL親から table() で TTL 戦略の子を作れること。"""
        parent = NanaSQLite(str(tmp_path / "test.db"), table="parent")
        # 親は UNBOUNDED (デフォルト)。子は TTL 戦略を明示的に指定 — ValueError が出ないこと
        child = parent.table("child", cache_strategy=CacheType.TTL, cache_ttl=30.0)
        assert child._cache_ttl_raw == 30.0

    def test_table_ttl_strategy_without_cache_ttl_raises(self, tmp_path):
        """非TTL親から cache_strategy=TTL だけ指定して table() を呼ぶと ValueError が発生すること。"""
        parent = NanaSQLite(str(tmp_path / "test.db"), table="parent")
        with pytest.raises(ValueError, match="cache_ttl"):
            parent.table("child", cache_strategy=CacheType.TTL)

    def test_table_inherits_parent_ttl(self, tmp_path):
        """TTL 親から省略で table() を呼ぶと cache_ttl が継承されること。"""
        parent = NanaSQLite(
            str(tmp_path / "test.db"), table="parent",
            cache_strategy=CacheType.TTL, cache_ttl=60.0,
        )
        child = parent.table("child")
        assert child._cache_ttl_raw == 60.0

    def test_table_inherits_parent_persistence_ttl(self, tmp_path):
        """TTL 親の cache_persistence_ttl も子に継承されること。"""
        parent = NanaSQLite(
            str(tmp_path / "test.db"), table="parent",
            cache_strategy=CacheType.TTL, cache_ttl=60.0, cache_persistence_ttl=True,
        )
        child = parent.table("child")
        assert child._cache_persistence_ttl_raw is True

    def test_table_explicit_cache_ttl_overrides_parent(self, tmp_path):
        """TTL 親から table() で cache_ttl を上書きできること。"""
        parent = NanaSQLite(
            str(tmp_path / "test.db"), table="parent",
            cache_strategy=CacheType.TTL, cache_ttl=60.0,
        )
        child = parent.table("child", cache_ttl=10.0)
        assert child._cache_ttl_raw == 10.0


class TestNoUnusedImports:
    """Ruff F401: 未使用インポートがないことを確認する。"""

    def _run_ruff_f401(self, filepath: str) -> str:
        """指定ファイルに対して ruff F401 チェックを実行し、エラーがあれば返す。"""
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", filepath, "--select", "F401"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        return result.stdout if result.returncode != 0 else ""

    def test_no_unused_import_time_in_comprehensive(self):
        """test_table_inheritance_comprehensive.py に未使用の `import time` がないこと。"""
        errors = self._run_ruff_f401("tests/test_table_inheritance_comprehensive.py")
        assert not errors, f"Ruff F401 errors:\n{errors}"

    def test_no_unused_import_pytest_in_tdd_fixes(self):
        """test_tdd_review_fixes.py に未使用の `import pytest` がないこと。"""
        errors = self._run_ruff_f401("tests/test_tdd_review_fixes.py")
        assert not errors, f"Ruff F401 errors:\n{errors}"
