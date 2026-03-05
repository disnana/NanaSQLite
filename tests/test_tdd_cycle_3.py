"""TDD cycle 3: 失敗するテストを書いてから修正する。

対応した問題（コードレビューコメント from 1a9d4e4）:
1. TestNoUnusedImports が ruff 未インストール環境でエラーになる
   → ruff が利用できない場合は pytest.skip すべき
2. docs/en/api/nanasqlite.md の table() シグネチャに cache_ttl / cache_persistence_ttl がない
3. docs/ja/api/nanasqlite.md の table() シグネチャに cache_ttl / cache_persistence_ttl がない
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def get_table_signature_block(doc_path: Path) -> str:
    """指定された Markdown ドキュメントから table() シグネチャのコードブロックを取得する。

    python コードブロック（バッククォート3つ + python）の中で "def table(" を含むブロックを探し、
    そのブロックの内容（区切り文字を除いたコード部分）を返す。
    一致するブロックが見つからない場合は空文字列を返す。
    """
    content = doc_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    in_python_block = False
    in_table_block = False
    block_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```python"):
            in_python_block = True
            in_table_block = False
            block_lines = []
            continue
        if stripped == "```" and in_python_block:
            if in_table_block:
                # table() ブロックが終了した — 収集完了
                return "\n".join(block_lines)
            # table() を含まないブロックが終わった — 状態をリセット
            in_python_block = False
            in_table_block = False
            block_lines = []
            continue
        if in_python_block:
            block_lines.append(line)
            if "def table(" in line:
                in_table_block = True
    return "\n".join(block_lines) if in_table_block else ""


class TestRuffAvailabilitySkip:
    """TestNoUnusedImports が ruff 未利用時にスキップすることを確認する。"""

    def test_tdd_cycle_2_ruff_check_handles_unavailable(self):
        """test_tdd_cycle_2.py の TestNoUnusedImports が ruff 未インストール時に対応していること。

        subprocess が 'No module named ruff' 相当のエラーを返した場合に
        テストが誤判定しないことを確認する。
        """
        src = (REPO_ROOT / "tests" / "test_tdd_cycle_2.py").read_text(encoding="utf-8")
        # TestNoUnusedImports クラス部分を抽出する
        class_start = src.find("class TestNoUnusedImports:")
        assert class_start != -1, "TestNoUnusedImports クラスが test_tdd_cycle_2.py に見つからない"
        class_src = src[class_start:]
        # ruff が利用できるかチェックしているか確認する
        has_availability_check = (
            "shutil.which" in class_src
            or "pytest.skip" in class_src
            or "importorskip" in class_src
        )
        assert has_availability_check, (
            "TestNoUnusedImports は ruff が利用できない場合の処理"
            "（shutil.which + pytest.skip など）を含む必要があります。"
            " ruff が CI にインストールされていない場合にテストが誤って失敗します。"
        )


class TestTableSignatureInEnDocs:
    """docs/en/api/nanasqlite.md の table() シグネチャに cache_ttl/cache_persistence_ttl が含まれること。"""

    def test_en_docs_table_signature_has_cache_ttl(self):
        """docs/en/api/nanasqlite.md の table() シグネチャに cache_ttl が含まれること。"""
        doc_path = REPO_ROOT / "docs" / "en" / "api" / "nanasqlite.md"
        block = get_table_signature_block(doc_path)
        assert "cache_ttl" in block, (
            "docs/en/api/nanasqlite.md の table() シグネチャに cache_ttl が含まれていません。"
            f"\n見つかったブロック:\n{block}"
        )

    def test_en_docs_table_signature_has_cache_persistence_ttl(self):
        """docs/en/api/nanasqlite.md の table() シグネチャに cache_persistence_ttl が含まれること。"""
        doc_path = REPO_ROOT / "docs" / "en" / "api" / "nanasqlite.md"
        block = get_table_signature_block(doc_path)
        assert "cache_persistence_ttl" in block, (
            "docs/en/api/nanasqlite.md の table() シグネチャに cache_persistence_ttl が含まれていません。"
            f"\n見つかったブロック:\n{block}"
        )


class TestTableSignatureInJaDocs:
    """docs/ja/api/nanasqlite.md の table() シグネチャに cache_ttl/cache_persistence_ttl が含まれること。"""

    def test_ja_docs_table_signature_has_cache_ttl(self):
        """docs/ja/api/nanasqlite.md の table() シグネチャに cache_ttl が含まれること。"""
        doc_path = REPO_ROOT / "docs" / "ja" / "api" / "nanasqlite.md"
        block = get_table_signature_block(doc_path)
        assert "cache_ttl" in block, (
            "docs/ja/api/nanasqlite.md の table() シグネチャに cache_ttl が含まれていません。"
            f"\n見つかったブロック:\n{block}"
        )

    def test_ja_docs_table_signature_has_cache_persistence_ttl(self):
        """docs/ja/api/nanasqlite.md の table() シグネチャに cache_persistence_ttl が含まれること。"""
        doc_path = REPO_ROOT / "docs" / "ja" / "api" / "nanasqlite.md"
        block = get_table_signature_block(doc_path)
        assert "cache_persistence_ttl" in block, (
            "docs/ja/api/nanasqlite.md の table() シグネチャに cache_persistence_ttl が含まれていません。"
            f"\n見つかったブロック:\n{block}"
        )

