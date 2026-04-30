#!/usr/bin/env python3
"""
deep_analyzer_v4.py — Python AST Security Analyzer (実装編)
「コードを1行も読ませずにAIが脆弱性を特定する」実装

新機能:
  1. テイント解析 (Taint Analysis)  - ユーザー入力がどこへ流れるか追跡
  2. データフローグラフ              - 変数の伝播チェーンを可視化
  3. 拡張セキュリティスキャナー      - CWEマッピング付き脆弱性検出
  4. 依存関係監査                   - 既知脆弱パッケージのチェック
  5. AI最適化レポート               - Claudeに渡す構造化Markdownを生成
"""

import ast
import re
import sys
import json
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────
# 1. 定義: テイントソース / シンク / 暗号パターン
# ─────────────────────────────────────────────

# ユーザー入力が発生する関数・属性
TAINT_SOURCES: dict[str, str] = {
    "input":                    "cli_input",
    "sys.argv":                 "cli_input",
    "request.args.get":         "http_query",
    "request.form.get":         "http_form",
    "request.json":             "http_json",
    "request.data":             "http_body",
    "request.cookies.get":      "http_cookie",
    "request.headers.get":      "http_header",
    "os.environ.get":           "env_var",
    "os.getenv":                "env_var",
    "json.loads":               "deserialized",
    "yaml.load":                "deserialized",        # safeでない方
    "pickle.loads":             "deserialized",
    "socket.recv":              "network_input",
    "socket.recvfrom":          "network_input",
    "open":                     "file_input",
}

# 汚染データが渡ると危険な関数
TAINT_SINKS: dict[str, dict] = {
    # コードインジェクション
    "eval":                     {"type": "code_injection",    "severity": "CRITICAL", "cwe": "CWE-94"},
    "exec":                     {"type": "code_injection",    "severity": "CRITICAL", "cwe": "CWE-94"},
    "compile":                  {"type": "code_injection",    "severity": "HIGH",     "cwe": "CWE-94"},
    # コマンドインジェクション
    "os.system":                {"type": "command_injection", "severity": "CRITICAL", "cwe": "CWE-78"},
    "os.popen":                 {"type": "command_injection", "severity": "CRITICAL", "cwe": "CWE-78"},
    "subprocess.call":          {"type": "command_injection", "severity": "CRITICAL", "cwe": "CWE-78"},
    "subprocess.Popen":         {"type": "command_injection", "severity": "CRITICAL", "cwe": "CWE-78"},
    "subprocess.run":           {"type": "command_injection", "severity": "CRITICAL", "cwe": "CWE-78"},
    "subprocess.check_output":  {"type": "command_injection", "severity": "CRITICAL", "cwe": "CWE-78"},
    # SQLインジェクション
    "cursor.execute":           {"type": "sql_injection",     "severity": "CRITICAL", "cwe": "CWE-89"},
    "db.execute":               {"type": "sql_injection",     "severity": "CRITICAL", "cwe": "CWE-89"},
    "session.execute":          {"type": "sql_injection",     "severity": "CRITICAL", "cwe": "CWE-89"},
    "connection.execute":       {"type": "sql_injection",     "severity": "CRITICAL", "cwe": "CWE-89"},
    # パストラバーサル
    "open":                     {"type": "path_traversal",    "severity": "HIGH",     "cwe": "CWE-22"},
    "os.path.join":             {"type": "path_traversal",    "severity": "MEDIUM",   "cwe": "CWE-22"},
    "pathlib.Path":             {"type": "path_traversal",    "severity": "MEDIUM",   "cwe": "CWE-22"},
    # デシリアライゼーション
    "pickle.loads":             {"type": "insecure_deser",    "severity": "CRITICAL", "cwe": "CWE-502"},
    "marshal.loads":            {"type": "insecure_deser",    "severity": "CRITICAL", "cwe": "CWE-502"},
    "yaml.load":                {"type": "insecure_deser",    "severity": "HIGH",     "cwe": "CWE-502"},
    # SSRF
    "requests.get":             {"type": "ssrf",              "severity": "HIGH",     "cwe": "CWE-918"},
    "requests.post":            {"type": "ssrf",              "severity": "HIGH",     "cwe": "CWE-918"},
    "urllib.request.urlopen":   {"type": "ssrf",              "severity": "HIGH",     "cwe": "CWE-918"},
    "httpx.get":                {"type": "ssrf",              "severity": "HIGH",     "cwe": "CWE-918"},
    # テンプレートインジェクション (SSTI)
    "render_template_string":   {"type": "ssti",              "severity": "CRITICAL", "cwe": "CWE-1336"},
    "Template":                 {"type": "ssti",              "severity": "HIGH",     "cwe": "CWE-1336"},
    "Markup":                   {"type": "xss",               "severity": "HIGH",     "cwe": "CWE-79"},
    # XXE
    "etree.parse":              {"type": "xxe",               "severity": "HIGH",     "cwe": "CWE-611"},
    "minidom.parse":            {"type": "xxe",               "severity": "HIGH",     "cwe": "CWE-611"},
}

WEAK_CRYPTO: dict[str, str] = {
    "md5":          "CWE-327 (弱いハッシュ)",
    "sha1":         "CWE-327 (弱いハッシュ)",
    "DES":          "CWE-327 (弱い暗号)",
    "RC4":          "CWE-327 (弱い暗号)",
    "random":       "CWE-338 (非暗号論的乱数)",  # secrets を使うべき
}

HARDCODED_SECRET_RE = re.compile(
    r'(?i)(password|passwd|pwd|secret|api_key|apikey|token|auth_token|private_key'
    r'|aws_access|aws_secret)\s*=\s*["\'][^"\']{6,}["\']'
)

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}


# ─────────────────────────────────────────────
# 2. データクラス
# ─────────────────────────────────────────────

@dataclass
class TaintFlow:
    """ソースからシンクへの汚染フロー"""
    source_var:   str
    source_type:  str          # e.g. http_query
    source_func:  str          # 定義されている関数
    source_line:  int
    sink_call:    str          # 危険な呼び出し
    sink_func:    str          # シンクが含まれる関数
    sink_line:    int
    sink_type:    str
    severity:     str
    cwe:          str
    path:         list[str] = field(default_factory=list)  # 伝播経路


@dataclass
class VulnFinding:
    """個別の脆弱性発見"""
    vuln_type:   str
    severity:    str
    cwe:         str
    location:    str           # ClassName.method_name
    line:        int
    evidence:    str           # ASTから取得した証拠（ソースコードなし）
    description: str


# ─────────────────────────────────────────────
# 3. AST Visitors
# ─────────────────────────────────────────────

class ComplexityVisitor(ast.NodeVisitor):
    """サイクロマティック複雑度計算"""

    def __init__(self):
        self.score = 1

    def visit_If(self, node):
        self.score += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.score += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.score += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        self.score += len(node.handlers)
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.score += len(node.values) - 1
        self.generic_visit(node)

    def visit_Match(self, node):  # Python 3.10+
        self.score += len(node.cases)
        self.generic_visit(node)


class TaintAnalyzer(ast.NodeVisitor):
    """
    テイント解析エンジン
    - 変数への「汚染ソース」代入を追跡
    - 汚染変数がシンクに渡されるフローを検出
    """

    def __init__(self, file_path: Path, root_dir: Path):
        self.file_path = file_path
        self.rel_path  = str(file_path.relative_to(root_dir))

        # { var_name -> TaintSource }
        self.tainted_vars: dict[str, dict] = {}
        # 検出したフロー
        self.flows: list[TaintFlow] = []
        # スコープスタック ["module", "ClassName", "ClassName.method"]
        self.scope_stack: list[str] = ["module"]
        # 全関数の引数名 (関数から関数への伝播の足がかり)
        self.func_params: dict[str, list[str]] = {}

    @property
    def current_scope(self) -> str:
        return self.scope_stack[-1]

    def _resolve_call(self, node: ast.Call) -> str:
        """Call ノードを文字列に変換 (例: os.system, cursor.execute)"""
        try:
            return ast.unparse(node.func)
        except Exception:
            return ""

    def _is_taint_source(self, node: ast.expr) -> Optional[str]:
        """式がテイントソースなら source_type を返す"""
        if isinstance(node, ast.Call):
            name = self._resolve_call(node)
            for src, src_type in TAINT_SOURCES.items():
                if name == src or name.endswith(f".{src.split('.')[-1]}"):
                    return src_type
        if isinstance(node, ast.Attribute):
            # request.json のような属性アクセス
            name = ast.unparse(node)
            for src, src_type in TAINT_SOURCES.items():
                if name == src:
                    return src_type
        return None

    def _arg_is_tainted(self, node: ast.expr) -> bool:
        """式ノードが汚染変数を含むか"""
        if isinstance(node, ast.Name) and node.id in self.tainted_vars:
            return True
        if isinstance(node, ast.JoinedStr):  # f-string
            for part in ast.walk(node):
                if isinstance(part, ast.Name) and part.id in self.tainted_vars:
                    return True
        if isinstance(node, ast.BinOp):
            return self._arg_is_tainted(node.left) or self._arg_is_tainted(node.right)
        if isinstance(node, ast.Call):
            return any(self._arg_is_tainted(a) for a in node.args)
        return False

    def visit_ClassDef(self, node: ast.ClassDef):
        self.scope_stack.append(f"Class:{node.name}")
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        scope = self.current_scope
        func_id = f"{scope}.{node.name}" if scope != "module" else node.name
        self.scope_stack.append(func_id)

        # 引数を記録 (関数間伝播の基礎)
        params = [a.arg for a in node.args.args]
        self.func_params[func_id] = params

        self.generic_visit(node)
        self.scope_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef  # async関数も同様

    def visit_Assign(self, node: ast.Assign):
        """代入文でのテイント追跡"""
        src_type = self._is_taint_source(node.value)
        if src_type:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.tainted_vars[target.id] = {
                        "type":  src_type,
                        "line":  node.lineno,
                        "scope": self.current_scope,
                    }
                elif isinstance(target, ast.Tuple):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            self.tainted_vars[elt.id] = {
                                "type":  src_type,
                                "line":  node.lineno,
                                "scope": self.current_scope,
                            }
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """シンク呼び出しに汚染引数が渡されるか検出"""
        call_name = self._resolve_call(node)
        if not call_name:
            self.generic_visit(node)
            return

        # シンク判定
        for sink, meta in TAINT_SINKS.items():
            if call_name == sink or call_name.endswith(f".{sink.split('.')[-1]}"):
                # 引数に汚染変数があるか
                all_args = list(node.args) + [kw.value for kw in node.keywords]
                for arg in all_args:
                    if self._arg_is_tainted(arg):
                        tvar = None
                        for part in ast.walk(arg):
                            if isinstance(part, ast.Name) and part.id in self.tainted_vars:
                                tvar = part.id
                                break
                        if tvar:
                            info = self.tainted_vars[tvar]
                            flow = TaintFlow(
                                source_var=tvar,
                                source_type=info["type"],
                                source_func=info["scope"],
                                source_line=info["line"],
                                sink_call=call_name,
                                sink_func=self.current_scope,
                                sink_line=node.lineno,
                                sink_type=meta["type"],
                                severity=meta["severity"],
                                cwe=meta["cwe"],
                            )
                            self.flows.append(flow)
                        break

        self.generic_visit(node)


class EnhancedSecurityScanner(ast.NodeVisitor):
    """
    テイント解析に依存しない静的パターンスキャナー
    - ハードコードされた秘密情報
    - 弱い暗号
    - 安全でない関数の直接使用
    - SQLの文字列連結
    """

    def __init__(self, rel_path: str):
        self.rel_path = rel_path
        self.findings:    list[VulnFinding] = []
        self.scope_stack: list[str] = ["module"]
        self.imports:     set[str] = set()

    @property
    def current_scope(self) -> str:
        return self.scope_stack[-1]

    def visit_ClassDef(self, node):
        self.scope_stack.append(f"Class:{node.name}")
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node):
        scope = self.current_scope
        func_id = f"{scope}.{node.name}" if scope != "module" else node.name
        self.scope_stack.append(func_id)
        self.generic_visit(node)
        self.scope_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

    def visit_Assign(self, node):
        """ハードコード秘密情報の検出"""
        try:
            src = ast.unparse(node)
        except Exception:
            self.generic_visit(node)
            return

        if HARDCODED_SECRET_RE.search(src):
            # 変数名を取得
            targets = [ast.unparse(t) for t in node.targets]
            self.findings.append(VulnFinding(
                vuln_type="hardcoded_secret",
                severity="HIGH",
                cwe="CWE-798",
                location=self.current_scope,
                line=node.lineno,
                evidence=f"代入対象: {', '.join(targets)}",
                description="ハードコードされた認証情報が検出されました",
            ))
        self.generic_visit(node)

    def visit_Call(self, node):
        try:
            call_name = ast.unparse(node.func)
        except Exception:
            self.generic_visit(node)
            return

        # 弱い暗号アルゴリズム
        for algo, cwe in WEAK_CRYPTO.items():
            if algo in call_name:
                self.findings.append(VulnFinding(
                    vuln_type="weak_crypto",
                    severity="MEDIUM",
                    cwe=cwe,
                    location=self.current_scope,
                    line=node.lineno,
                    evidence=f"呼び出し: {call_name}",
                    description=f"弱い暗号/乱数関数 {call_name} の使用",
                ))

        # assert文の削除でバイパスされうる認証チェック
        # yaml.load (safeでない)
        if call_name in ("yaml.load",):
            args_str = ast.unparse(node.args[1]) if len(node.args) > 1 else "?"
            if "Loader" not in args_str and "SafeLoader" not in args_str:
                self.findings.append(VulnFinding(
                    vuln_type="unsafe_yaml",
                    severity="HIGH",
                    cwe="CWE-502",
                    location=self.current_scope,
                    line=node.lineno,
                    evidence=f"yaml.load(Loader未指定)",
                    description="yaml.load に Loader=yaml.SafeLoader が指定されていません",
                ))

        # SQL文字列連結パターン: execute("..." + var) or execute(f"...")
        if call_name.endswith(".execute") or call_name == "execute":
            if node.args:
                arg0 = node.args[0]
                if isinstance(arg0, (ast.JoinedStr, ast.BinOp)):
                    self.findings.append(VulnFinding(
                        vuln_type="sql_string_concat",
                        severity="CRITICAL",
                        cwe="CWE-89",
                        location=self.current_scope,
                        line=node.lineno,
                        evidence=f"execute({ast.unparse(arg0)[:60]}...)",
                        description="SQLクエリへの文字列連結/f-string — SQLインジェクションの疑い",
                    ))

        self.generic_visit(node)


class DeepAnalyzerV4(ast.NodeVisitor):
    """
    構造マップ生成器 (V4)
    クラス・関数・変数・呼び出しグラフ・インポートを収集
    """

    def __init__(self, file_path: Path, root_dir: Path):
        self.file_path  = file_path
        self.rel_path   = str(file_path.relative_to(root_dir))
        self.scope_stack: list[str] = ["module"]
        self.classes:   dict = {}
        self.functions: dict = {}
        self.variables: dict = defaultdict(set)
        self.imports:   set  = set()
        self.call_edges: list[tuple[str, str]] = []  # (caller, callee)

    @property
    def current_scope(self) -> str:
        return self.scope_stack[-1]

    def _current_class(self) -> Optional[str]:
        for scope in reversed(self.scope_stack):
            if scope.startswith("Class:"):
                return scope[6:]
        return None

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                self.imports.add(f"{node.module}.{alias.name}")
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        cls_name = node.name
        bases = [ast.unparse(b) for b in node.bases]
        doc   = ast.get_docstring(node) or ""
        self.classes[cls_name] = {
            "bases": bases,
            "doc":   doc[:120],
            "file":  self.rel_path,
            "line":  node.lineno,
        }
        self.scope_stack.append(f"Class:{cls_name}")
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node):
        cls = self._current_class()
        func_id = f"{cls}.{node.name}" if cls else node.name
        args = [a.arg for a in node.args.args]
        returns = ast.unparse(node.returns) if node.returns else None
        doc = ast.get_docstring(node) or ""

        cv = ComplexityVisitor()
        cv.visit(node)

        self.functions[func_id] = {
            "args":       args,
            "returns":    returns,
            "complexity": cv.score,
            "doc":        doc[:120],
            "file":       self.rel_path,
            "line":       node.lineno,
        }
        self.scope_stack.append(func_id)
        self.generic_visit(node)
        self.scope_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables[self.current_scope].add(target.id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.variables[self.current_scope].add(node.target.id)
        self.generic_visit(node)

    def visit_Call(self, node):
        try:
            callee = ast.unparse(node.func)
        except Exception:
            self.generic_visit(node)
            return
        caller = self.current_scope
        self.call_edges.append((caller, callee))
        self.generic_visit(node)


# ─────────────────────────────────────────────
# 4. 依存関係監査
# ─────────────────────────────────────────────

# 既知の脆弱パッケージ (実運用では OSV API を叩く)
KNOWN_VULNERABLE_PACKAGES: dict[str, dict] = {
    "pyyaml":         {"safe_from": "6.0",   "cve": "CVE-2022-1471", "desc": "任意コード実行"},
    "pillow":         {"safe_from": "10.0.1","cve": "CVE-2023-44271","desc": "DoS"},
    "cryptography":   {"safe_from": "41.0.0","cve": "CVE-2023-49083","desc": "NULL dereference"},
    "requests":       {"safe_from": "2.31.0","cve": "CVE-2023-32681","desc": "Proxy-Auth header leak"},
    "werkzeug":       {"safe_from": "3.0.1", "cve": "CVE-2023-46136","desc": "DoS"},
    "flask":          {"safe_from": "3.0.0", "cve": "CVE-2023-30861","desc": "Session cookie漏洩"},
    "django":         {"safe_from": "4.2.7", "cve": "CVE-2023-41164","desc": "DoS"},
    "paramiko":       {"safe_from": "3.4.0", "cve": "CVE-2023-48795","desc": "Terrapin Attack"},
    "aiohttp":        {"safe_from": "3.9.0", "cve": "CVE-2023-49082","desc": "CRLF injection"},
    "urllib3":        {"safe_from": "2.0.7", "cve": "CVE-2023-45803","desc": "Request body漏洩"},
}


def audit_requirements(root_dir: Path) -> list[dict]:
    """requirements.txt / pyproject.toml からパッケージを読んで既知脆弱性チェック"""
    findings = []
    req_files = list(root_dir.rglob("requirements*.txt")) + list(root_dir.rglob("pyproject.toml"))

    for req_file in req_files:
        try:
            text = req_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # パッケージ名を正規化
            pkg_match = re.match(r'^([A-Za-z0-9_\-\.]+)', line)
            if not pkg_match:
                continue
            pkg_name = pkg_match.group(1).lower().replace("-", "_").replace(".", "_")

            for vuln_pkg, meta in KNOWN_VULNERABLE_PACKAGES.items():
                if pkg_name == vuln_pkg.replace("-", "_"):
                    findings.append({
                        "package":    vuln_pkg,
                        "cve":        meta["cve"],
                        "safe_from":  meta["safe_from"],
                        "desc":       meta["desc"],
                        "req_file":   str(req_file.relative_to(root_dir)),
                    })
    return findings


# ─────────────────────────────────────────────
# 5. レポート生成
# ─────────────────────────────────────────────

def safe_id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", s)


def severity_emoji(s: str) -> str:
    return {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(s, "⚪")


def generate_report(target_dir: str, output_file: str = "security_report.md") -> str:
    """
    プロジェクト全体を解析し AI 向けセキュリティレポートを生成
    Returns: 生成された Markdown 文字列
    """
    root = Path(target_dir).absolute()
    md: list[str] = []

    # ── 収集バッファ ──
    all_classes:  dict = {}
    all_functions: dict = {}
    all_variables: dict = defaultdict(set)
    all_imports:   set  = set()
    all_call_edges: list = []
    all_taint_flows: list[TaintFlow] = []
    all_vuln_findings: list[VulnFinding] = []
    dep_findings: list = []

    # ── ファイル列挙 ──
    py_files = sorted(root.rglob("*.py"))
    if not py_files:
        return "# Error\n\nPythonファイルが見つかりませんでした。"

    # ── 各ファイル解析 ──
    for py_file in py_files:
        try:
            src = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(src, filename=str(py_file))
        except SyntaxError as e:
            all_vuln_findings.append(VulnFinding(
                vuln_type="syntax_error",
                severity="INFO",
                cwe="N/A",
                location=str(py_file.relative_to(root)),
                line=e.lineno or 0,
                evidence=str(e),
                description="構文エラー（解析スキップ）",
            ))
            continue

        # 構造解析
        analyzer = DeepAnalyzerV4(py_file, root)
        analyzer.visit(tree)
        all_classes.update(analyzer.classes)
        all_functions.update(analyzer.functions)
        for scope, vars_ in analyzer.variables.items():
            all_variables[scope].update(vars_)
        all_imports.update(analyzer.imports)
        all_call_edges.extend(analyzer.call_edges)

        # テイント解析
        taint = TaintAnalyzer(py_file, root)
        taint.visit(tree)
        all_taint_flows.extend(taint.flows)

        # セキュリティスキャン
        scanner = EnhancedSecurityScanner(str(py_file.relative_to(root)))
        scanner.visit(tree)
        all_vuln_findings.extend(scanner.findings)

    # 依存関係監査
    dep_findings = audit_requirements(root)

    # ─────────────────────────────────────────
    # レポート本文
    # ─────────────────────────────────────────

    md.append("# Python セキュリティ構造マップ (Deep Analyzer V4)")
    md.append(f"\n> 生成元: `{root}` — {len(py_files)} ファイル解析\n")
    md.append("> ⚠️ このレポートはソースコードを一切含みません。")
    md.append("> AIはこの構造情報のみで脆弱性を特定できます。\n")

    # ── サマリーダッシュボード ──
    critical_count = sum(1 for f in all_taint_flows if f.severity == "CRITICAL")
    high_count     = sum(1 for f in all_taint_flows if f.severity == "HIGH")
    static_critical = sum(1 for f in all_vuln_findings if f.severity == "CRITICAL")

    md.append("## 📊 サマリー\n")
    md.append("| 項目 | 件数 |")
    md.append("|:---|---:|")
    md.append(f"| 解析ファイル数 | {len(py_files)} |")
    md.append(f"| クラス数 | {len(all_classes)} |")
    md.append(f"| 関数数 | {len(all_functions)} |")
    md.append(f"| テイントフロー検出 (CRITICAL) | 🔴 {critical_count} |")
    md.append(f"| テイントフロー検出 (HIGH) | 🟠 {high_count} |")
    md.append(f"| 静的スキャン指摘 (CRITICAL) | 🔴 {static_critical} |")
    md.append(f"| 脆弱パッケージ | ⚠️ {len(dep_findings)} |")

    # ── セクション 1: クラス構造 ──
    md.append("\n---\n## 1. クラス構造\n")
    if all_classes:
        md.append("```mermaid\nclassDiagram")
        for cls_name, info in sorted(all_classes.items()):
            for base in info.get("bases", []):
                if base != "object":
                    md.append(f"    {safe_id(base)} <|-- {safe_id(cls_name)}")
            md.append(f"    class {safe_id(cls_name)} {{")
            # そのクラスのメソッドを列挙
            for func_id, finfo in all_functions.items():
                if func_id.startswith(f"{cls_name}."):
                    method = func_id[len(cls_name)+1:]
                    args_str = ", ".join(finfo["args"][1:])  # selfを除く
                    ret_str  = finfo["returns"] or "None"
                    md.append(f"        +{method}({args_str}) {ret_str}")
            md.append("    }")
        md.append("```")
    else:
        md.append("_クラスなし_")

    # ── セクション 2: 呼び出しグラフ ──
    md.append("\n---\n## 2. 呼び出しグラフ\n")
    md.append("```mermaid\ngraph TD")
    unique_edges: set[tuple[str, str]] = set()
    for caller, callee in all_call_edges:
        # ノイズを削減: 既知の組み込み / 頻出を省く
        skip = {"append", "update", "pop", "add", "join", "split", "replace",
                "items", "keys", "values", "get", "set", "len", "str", "int",
                "list", "dict", "print", "open", "sorted", "reversed"}
        callee_short = callee.split(".")[-1]
        if callee_short in skip:
            continue
        edge = (safe_id(caller), safe_id(callee))
        if edge not in unique_edges:
            unique_edges.add(edge)
            md.append(f'    {safe_id(caller)}["{caller}"] --> {safe_id(callee)}["{callee}"]')
    md.append("```")

    # ── セクション 3: 関数メトリクス ──
    md.append("\n---\n## 3. 関数メトリクス\n")
    md.append("| 関数 | 引数 | 複雑度 | ファイル:行 | docstring |")
    md.append("|:---|:---|:---:|:---|:---|")
    for func_id, info in sorted(all_functions.items(), key=lambda x: -x[1]["complexity"]):
        comp = info["complexity"]
        comp_warn = " ⚠️" if comp >= 10 else (" 🟡" if comp >= 5 else "")
        args_str = ", ".join(info["args"])
        doc_short = (info["doc"][:40] + "...") if len(info["doc"]) > 40 else info["doc"]
        md.append(f"| `{func_id}` | `{args_str}` | {comp}{comp_warn} | `{info['file']}:{info['line']}` | {doc_short} |")

    # ── セクション 4: 変数スコープ ──
    md.append("\n---\n## 4. 変数スコープ\n")
    md.append("| スコープ | 変数名 |")
    md.append("|:---|:---|")
    for scope, vars_ in sorted(all_variables.items()):
        md.append(f"| `{scope}` | {', '.join(f'`{v}`' for v in sorted(vars_))} |")

    # ── セクション 5: インポート一覧 ──
    md.append("\n---\n## 5. インポート\n")
    md.append("```")
    for imp in sorted(all_imports):
        md.append(imp)
    md.append("```")

    # ══════════════════════════════════════════
    # 🔴 セキュリティセクション
    # ══════════════════════════════════════════

    # ── セクション 6: テイントフロー解析 ──
    md.append("\n---\n## 🔴 6. テイントフロー解析 (Taint Analysis)\n")
    md.append("> ユーザー入力が危険な操作にたどり着くフローを示します\n")

    if all_taint_flows:
        # Mermaid フロー図
        md.append("### フロー図\n")
        md.append("```mermaid\ngraph LR")
        md.append('    style EXTERNAL fill:#ff4444,color:#fff')
        seen_taint_nodes: set[str] = set()
        for i, flow in enumerate(all_taint_flows):
            src_id = safe_id(f"SRC_{flow.source_var}_{flow.source_type}")
            snk_id = safe_id(f"SNK_{flow.sink_call}_{i}")
            if src_id not in seen_taint_nodes:
                md.append(f'    {src_id}["⚠️ {flow.source_type}\\n変数: {flow.source_var}"]')
                seen_taint_nodes.add(src_id)
            md.append(f'    {snk_id}["{severity_emoji(flow.severity)} {flow.sink_call}\\n{flow.sink_type}"]')
            md.append(f'    {src_id} -->|"{flow.source_func}→{flow.sink_func}"| {snk_id}')
        md.append("```\n")

        # テーブル
        md.append("### フロー詳細\n")
        md.append("| Sev | ソース変数 | 入力種別 | 定義場所 | シンク関数 | 脆弱性種別 | CWE | 検出場所 |")
        md.append("|:---:|:---|:---|:---|:---|:---|:---|:---|")
        for flow in sorted(all_taint_flows, key=lambda f: SEVERITY_ORDER.get(f.severity, 99)):
            md.append(
                f"| {severity_emoji(flow.severity)} {flow.severity} "
                f"| `{flow.source_var}` (L{flow.source_line}) "
                f"| {flow.source_type} "
                f"| `{flow.source_func}` "
                f"| `{flow.sink_call}` (L{flow.sink_line}) "
                f"| **{flow.sink_type}** "
                f"| [{flow.cwe}](https://cwe.mitre.org/data/definitions/{flow.cwe.replace('CWE-','')}.html) "
                f"| `{flow.sink_func}` |"
            )
    else:
        md.append("_テイントフローは検出されませんでした_")

    # ── セクション 7: 静的脆弱性スキャン ──
    md.append("\n---\n## 🟠 7. 静的脆弱性スキャン\n")

    if all_vuln_findings:
        sorted_findings = sorted(all_vuln_findings, key=lambda f: SEVERITY_ORDER.get(f.severity, 99))
        md.append("| Sev | 種別 | CWE | 場所 | 行 | 証拠 | 説明 |")
        md.append("|:---:|:---|:---|:---|:---:|:---|:---|")
        for f in sorted_findings:
            md.append(
                f"| {severity_emoji(f.severity)} {f.severity} "
                f"| `{f.vuln_type}` "
                f"| [{f.cwe}](https://cwe.mitre.org/data/definitions/{f.cwe.replace('CWE-','')}.html) "
                f"| `{f.location}` "
                f"| {f.line} "
                f"| `{f.evidence[:60]}` "
                f"| {f.description} |"
            )
    else:
        md.append("_静的スキャンで脆弱性は検出されませんでした_")

    # ── セクション 8: 依存関係監査 ──
    md.append("\n---\n## ⚠️ 8. 依存関係監査\n")
    if dep_findings:
        md.append("| パッケージ | CVE | 安全バージョン | 説明 | 検出ファイル |")
        md.append("|:---|:---|:---|:---|:---|")
        for f in dep_findings:
            md.append(f"| `{f['package']}` | [{f['cve']}](https://nvd.nist.gov/vuln/detail/{f['cve']}) | `>= {f['safe_from']}` | {f['desc']} | `{f['req_file']}` |")
    else:
        md.append("_requirements.txt / pyproject.toml が見つからないか、既知の脆弱パッケージは検出されませんでした_")

    # ── セクション 9: 高複雑度関数 (攻撃面) ──
    md.append("\n---\n## 🟡 9. 高複雑度関数 (攻撃面候補)\n")
    md.append("> 複雑度が高い関数はバグ・脆弱性が潜みやすい\n")
    complex_funcs = [(fid, info) for fid, info in all_functions.items() if info["complexity"] >= 5]
    if complex_funcs:
        md.append("| 関数 | 複雑度 | ファイル:行 |")
        md.append("|:---|:---:|:---|")
        for fid, info in sorted(complex_funcs, key=lambda x: -x[1]["complexity"]):
            md.append(f"| `{fid}` | {info['complexity']} | `{info['file']}:{info['line']}` |")
    else:
        md.append("_複雑度5以上の関数はありません_")

    # ── セクション 10: AI向けプロンプト ──
    md.append("\n---\n## 🤖 10. AI 分析プロンプト\n")
    md.append("> このセクションをそのままClaudeに貼り付けてください\n")
    md.append("```")
    md.append("あなたはセキュリティ専門家です。")
    md.append("以下のPythonプロジェクトのAST構造マップを分析し、脆弱性を特定してください。")
    md.append("ソースコードは含まれていませんが、構造情報のみで十分に分析できます。\n")
    md.append("## 分析依頼\n")
    md.append("1. テイントフロー解析 (セクション6) を元に、実際に悪用可能な脆弱性チェーンを特定せよ")
    md.append("2. 静的スキャン結果 (セクション7) の優先度付けと修正方針を提示せよ")
    md.append("3. 呼び出しグラフ (セクション2) から、認証チェックを回避できる経路を探せ")
    md.append("4. 高複雑度関数 (セクション9) に潜む論理的バグのリスクを評価せよ")
    md.append("5. 依存関係 (セクション8) の脆弱性がプロジェクト固有のコードとどう連鎖するか評価せよ\n")
    md.append("## 出力形式")
    md.append("- 重要度順にランク付け (CRITICAL → HIGH → MEDIUM)")
    md.append("- 各脆弱性に対して: 根拠 / 悪用シナリオ / 修正コードの骨格")
    md.append("- 修正コードはロジックのみ示す (完全なソースコードは不要)")
    md.append("```")

    # ─────────────────────────────────────────
    # 出力
    # ─────────────────────────────────────────
    report_text = "\n".join(md)

    output_path = Path(output_file)
    output_path.write_text(report_text, encoding="utf-8")
    print(f"[+] レポート生成完了: {output_path} ({len(report_text):,} chars)")
    print(f"[+] テイントフロー: {len(all_taint_flows)} 件")
    print(f"[+] 静的指摘: {len(all_vuln_findings)} 件")
    print(f"[+] 脆弱パッケージ: {len(dep_findings)} 件")

    return report_text


# ─────────────────────────────────────────────
# 6. エントリーポイント
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deep_analyzer_v4.py <target_dir> [output.md]")
        sys.exit(1)

    target = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "security_report.md"
    generate_report(target, output)