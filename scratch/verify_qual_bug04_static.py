"""QUAL-01 と BUG-04 指摘の静的検証スクリプト。

このスクリプトは nanasqlite や APSW を import しない。
現在のソースコードを AST で確認するため、依存関係が入っていない環境でも実行できる。
"""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASYNC_CORE = ROOT / "src" / "nanasqlite" / "async_core.py"
CORE = ROOT / "src" / "nanasqlite" / "core.py"


def find_class(tree: ast.AST, class_name: str) -> ast.ClassDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    raise AssertionError(f"クラス {class_name} が見つかりません")


def find_method(cls: ast.ClassDef, method_name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in cls.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method_name:
            return node
    raise AssertionError(f"メソッド {cls.name}.{method_name} が見つかりません")


def arg_names(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    return [arg.arg for arg in fn.args.args] + [arg.arg for arg in fn.args.kwonlyargs]


def has_kwarg_get(fn: ast.FunctionDef | ast.AsyncFunctionDef, key: str) -> bool:
    for node in ast.walk(fn):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "kwargs"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == key
        ):
            return True
    return False


def nana_sqlite_call_keywords(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    keywords: set[str] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "NanaSQLite":
            for kw in node.keywords:
                if kw.arg:
                    keywords.add(kw.arg)
    return keywords


def method_contains_memory_guard(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for node in ast.walk(fn):
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Attribute):
            if node.left.attr == "_db_path":
                for comparator in node.comparators:
                    if isinstance(comparator, (ast.Tuple, ast.List)):
                        values = [
                            elt.value
                            for elt in comparator.elts
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                        ]
                        if ":memory:" in values and "" in values:
                            return True
    return False


def main() -> int:
    async_tree = ast.parse(ASYNC_CORE.read_text(encoding="utf-8"))
    core_tree = ast.parse(CORE.read_text(encoding="utf-8"))

    async_cls = find_class(async_tree, "AsyncNanaSQLite")
    async_init = find_method(async_cls, "__init__")
    async_ensure = find_method(async_cls, "_ensure_initialized")
    async_table = find_method(async_cls, "table")

    sync_cls = find_class(core_tree, "NanaSQLite")
    sync_table = find_method(sync_cls, "table")
    get_db_size = find_method(sync_cls, "get_db_size")

    results = {
        "async_init_reads_lock_timeout": has_kwarg_get(async_init, "lock_timeout"),
        "async_inner_nanasqlite_receives_lock_timeout": "lock_timeout" in nana_sqlite_call_keywords(async_ensure),
        "async_table_has_lock_timeout_arg": "lock_timeout" in arg_names(async_table),
        "sync_table_has_lock_timeout_arg": "lock_timeout" in arg_names(sync_table),
        "get_db_size_has_memory_guard": method_contains_memory_guard(get_db_size),
    }
    labels = {
        "async_init_reads_lock_timeout": "AsyncNanaSQLite.__init__() が lock_timeout を読む",
        "async_inner_nanasqlite_receives_lock_timeout": "内部 NanaSQLite(...) に lock_timeout を渡す",
        "async_table_has_lock_timeout_arg": "AsyncNanaSQLite.table() に lock_timeout 引数がある",
        "sync_table_has_lock_timeout_arg": "NanaSQLite.table() に lock_timeout 引数がある",
        "get_db_size_has_memory_guard": "get_db_size() に :memory: / 空パス guard がある",
    }

    print("静的検証結果")
    for key, value in results.items():
        print(f"- {labels[key]}: {value}")

    print()
    print("解釈")
    if not results["async_init_reads_lock_timeout"] and not results["async_inner_nanasqlite_receives_lock_timeout"]:
        print("- QUAL-01 は広い意味で実在します: AsyncNanaSQLite は生成時の lock_timeout を無視しています。")
    if results["async_init_reads_lock_timeout"] and results["async_inner_nanasqlite_receives_lock_timeout"]:
        print("- QUAL-01 の中核問題は修正済みです: AsyncNanaSQLite は lock_timeout を内部 DB に転送します。")
    if not results["async_table_has_lock_timeout_arg"] and not results["sync_table_has_lock_timeout_arg"]:
        print("- ただし table() だけの問題という説明は不正確です: async/sync のどちらも個別上書きに未対応です。")
    if results["get_db_size_has_memory_guard"]:
        print("- BUG-04 は現行ソースでは修正済みです: get_db_size() は :memory: と空パスを保護しています。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
