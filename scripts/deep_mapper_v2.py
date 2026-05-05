import ast
import re
import sys
from collections import defaultdict
from pathlib import Path


class DeepAnalyzer(ast.NodeVisitor):
    def __init__(self, file_path):
        self.file_path = file_path
        self.classes = {}
        self.functions = {}
        self.call_graph = []

        # スコープ管理: 'global', 'Class:Name', 'Function:Name'
        self.scope_stack = ['global']

        # 変数の記録
        self.variables = defaultdict(lambda: {'globals': set(), 'locals': set(), 'instance': set()})

    @property
    def current_scope(self):
        return self.scope_stack[-1]

    @property
    def current_class(self):
        for scope in reversed(self.scope_stack):
            if scope.startswith('Class:'):
                return scope.split(':')[1]
        return None

    def visit_ClassDef(self, node):
        class_name = node.name
        self.classes[class_name] = {
            "bases": [ast.unparse(b) for b in node.bases],
            "methods": []
        }
        self.scope_stack.append(f"Class:{class_name}")
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node):
        func_name = node.name
        args = [(arg.arg, ast.unparse(arg.annotation) if arg.annotation else "Any") for arg in node.args.args]
        returns = ast.unparse(node.returns) if node.returns else "Any"

        func_id = f"{self.current_class}.{func_name}" if self.current_class else func_name

        if self.current_class:
            self.classes[self.current_class]["methods"].append({"name": func_name, "args": args, "returns": returns})
        else:
            self.functions[func_name] = {"args": args, "returns": returns}

        self.scope_stack.append(f"Function:{func_id}")
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_Assign(self, node):
        self._analyze_assignment(node.targets)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self._analyze_assignment([node.target])
        self.generic_visit(node)

    def _analyze_assignment(self, targets):
        for target in targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                if self.current_scope == 'global':
                    self.variables[self.current_scope]['globals'].add(var_name)
                else:
                    self.variables[self.current_scope]['locals'].add(var_name)
            elif isinstance(target, ast.Attribute):
                if isinstance(target.value, ast.Name) and target.value.id == 'self':
                    if self.current_class:
                        self.variables[f"Class:{self.current_class}"]['instance'].add(target.attr)
                else:
                    try:
                        self.variables[self.current_scope]['locals'].add(ast.unparse(target))
                    except Exception:
                        pass

    def visit_Global(self, node):
        for name in node.names:
            self.variables[self.current_scope]['globals'].add(name)
        self.generic_visit(node)

    def visit_Call(self, node):
        caller = self.current_scope.replace('Function:',
                                            '') if 'Function:' in self.current_scope else self.current_scope

        callee = None
        if isinstance(node.func, ast.Name):
            callee = node.func.id
        elif isinstance(node.func, ast.Attribute):
            # self.method や obj.method を抽出。深すぎるチェーンは末尾の属性名のみ。
            if isinstance(node.func.value, ast.Name):
                callee = f"{node.func.value.id}.{node.func.attr}"
            else:
                callee = node.func.attr

        if callee and caller != 'global':
            self.call_graph.append((caller, callee))

        self.generic_visit(node)


def generate_markdown(root_path, output_file="project_map.md"):
    root = Path(root_path)
    all_classes = {}
    all_functions = {}
    all_calls = []
    all_vars = defaultdict(lambda: {'globals': set(), 'locals': set(), 'instance': set()})

    print(f"Scanning directory: {root.absolute()}")

    for py_file in root.rglob("*.py"):
        if ".venv" in str(py_file) or "__pycache__" in str(py_file):
            continue

        with open(py_file, encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                print(f"Syntax error skipped: {py_file}")
                continue

            analyzer = DeepAnalyzer(py_file)
            analyzer.visit(tree)

            all_classes.update(analyzer.classes)
            all_functions.update(analyzer.functions)
            all_calls.extend(analyzer.call_graph)
            for scope, v_types in analyzer.variables.items():
                all_vars[scope]['globals'].update(v_types['globals'])
                all_vars[scope]['locals'].update(v_types['locals'])
                all_vars[scope]['instance'].update(v_types['instance'])

    md = ["# Python Deep Structure Map\n"]

    # 1. Class Architecture
    md.append("## 1. Class Architecture\n```mermaid\nclassDiagram")
    for cls_name, info in all_classes.items():
        for base in info["bases"]:
            md.append(f"    {base} <|-- {cls_name}")

        if f"Class:{cls_name}" in all_vars:
            for ivar in all_vars[f"Class:{cls_name}"]['instance']:
                md.append(f"    class {cls_name} {{ +{ivar} }}")

        for m in info["methods"]:
            args_str = ", ".join([f"{n}:{t}" for n, t in m["args"] if n != 'self'])
            md.append(f"    class {cls_name} {{ +{m['name']}({args_str}) {m['returns']} }}")
    md.append("```\n")

    # 2. Call Graph
    md.append("## 2. Call Graph\n```mermaid\ngraph TD")
    unique_calls = set(all_calls)

    # MermaidのノードID用サニタイザー（英数字とアンダースコア以外を置換）
    def safe_id(text):
        return re.sub(r'[^a-zA-Z0-9_]', '_', text)

    for caller, callee in unique_calls:
        cid_caller = safe_id(caller)
        cid_callee = safe_id(callee)

        if cid_caller and cid_callee:
            # ID[ラベル] の形式にして、ラベル部分はダブルクォートで保護
            md.append(f"    {cid_caller}[\"{caller}\"] --> {cid_callee}[\"{callee}\"]")
    md.append("```\n")

    # 3. Variable Scopes
    md.append("## 3. Variable Scopes\n")
    md.append("| Scope Context | Global Variables | Instance Variables (`self.*`) | Local / Temp Variables |")
    md.append("| :--- | :--- | :--- | :--- |")

    for scope, v_types in sorted(all_vars.items()):
        if not v_types['globals'] and not v_types['instance'] and not v_types['locals']:
            continue

        g_str = ", ".join(v_types['globals']) or "-"
        i_str = ", ".join(v_types['instance']) or "-"
        l_str = ", ".join(v_types['locals']) or "-"
        md.append(f"| `{scope}` | {g_str} | {i_str} | {l_str} |")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"\nSuccessfully generated mapping file: {Path(output_file).absolute()}")


if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_markdown(target_dir)
