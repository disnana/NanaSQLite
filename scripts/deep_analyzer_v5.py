#!/usr/bin/env python3
import ast
import re
import sys
import os
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

MAX_CHUNK_NODES = int(os.environ.get("MAX_CHUNK_NODES", 30))
APPROX_CHARS_PER_TOKEN = 4

TAINT_SOURCES = {
    "input": "cli_input",
    "sys.argv": "cli_input",
    "request.args.get": "http_query",
    "request.form.get": "http_form",
    "request.json": "http_json",
    "request.data": "http_body",
    "request.cookies.get": "http_cookie",
    "request.headers.get": "http_header",
    "os.environ.get": "env_var",
    "os.getenv": "env_var",
    "json.loads": "deserialized",
    "yaml.load": "deserialized",
    "pickle.loads": "deserialized",
    "socket.recv": "network_input",
    "socket.recvfrom": "network_input",
    "open": "file_input",
}

TAINT_SINKS = {
    "eval": {"type": "code_injection", "severity": "CRITICAL", "cwe": "CWE-94"},
    "exec": {"type": "code_injection", "severity": "CRITICAL", "cwe": "CWE-94"},
    "compile": {"type": "code_injection", "severity": "HIGH", "cwe": "CWE-94"},
    "os.system": {"type": "command_injection", "severity": "CRITICAL", "cwe": "CWE-78"},
    "os.popen": {"type": "command_injection", "severity": "CRITICAL", "cwe": "CWE-78"},
    "subprocess.call": {"type": "command_injection", "severity": "CRITICAL", "cwe": "CWE-78"},
    "subprocess.Popen": {"type": "command_injection", "severity": "CRITICAL", "cwe": "CWE-78"},
    "subprocess.run": {"type": "command_injection", "severity": "CRITICAL", "cwe": "CWE-78"},
    "subprocess.check_output": {"type": "command_injection", "severity": "CRITICAL", "cwe": "CWE-78"},
    "cursor.execute": {"type": "sql_injection", "severity": "CRITICAL", "cwe": "CWE-89"},
    "db.execute": {"type": "sql_injection", "severity": "CRITICAL", "cwe": "CWE-89"},
    "session.execute": {"type": "sql_injection", "severity": "CRITICAL", "cwe": "CWE-89"},
    "connection.execute": {"type": "sql_injection", "severity": "CRITICAL", "cwe": "CWE-89"},
    "open": {"type": "path_traversal", "severity": "HIGH", "cwe": "CWE-22"},
    "os.path.join": {"type": "path_traversal", "severity": "MEDIUM", "cwe": "CWE-22"},
    "pathlib.Path": {"type": "path_traversal", "severity": "MEDIUM", "cwe": "CWE-22"},
    "pickle.loads": {"type": "insecure_deser", "severity": "CRITICAL", "cwe": "CWE-502"},
    "marshal.loads": {"type": "insecure_deser", "severity": "CRITICAL", "cwe": "CWE-502"},
    "yaml.load": {"type": "insecure_deser", "severity": "HIGH", "cwe": "CWE-502"},
    "requests.get": {"type": "ssrf", "severity": "HIGH", "cwe": "CWE-918"},
    "requests.post": {"type": "ssrf", "severity": "HIGH", "cwe": "CWE-918"},
    "urllib.request.urlopen": {"type": "ssrf", "severity": "HIGH", "cwe": "CWE-918"},
    "httpx.get": {"type": "ssrf", "severity": "HIGH", "cwe": "CWE-918"},
    "render_template_string": {"type": "ssti", "severity": "CRITICAL", "cwe": "CWE-1336"},
    "Template": {"type": "ssti", "severity": "HIGH", "cwe": "CWE-1336"},
    "Markup": {"type": "xss", "severity": "HIGH", "cwe": "CWE-79"},
    "etree.parse": {"type": "xxe", "severity": "HIGH", "cwe": "CWE-611"},
    "minidom.parse": {"type": "xxe", "severity": "HIGH", "cwe": "CWE-611"},
}

WEAK_CRYPTO = {
    "md5": "CWE-327 (弱いハッシュ)",
    "sha1": "CWE-327 (弱いハッシュ)",
    "DES": "CWE-327 (弱い暗号)",
    "RC4": "CWE-327 (弱い暗号)",
    "random": "CWE-338 (非暗号論的乱数)",
}

HARDCODED_SECRET_RE = re.compile(
    r'(?i)(password|passwd|pwd|secret|api_key|apikey|token|auth_token|private_key|aws_access|aws_secret)\s*=\s*["\'][^"\']{6,}["\']'
)
SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}

KNOWN_VULNERABLE_PACKAGES = {
    "pyyaml": {"safe_from": "6.0", "cve": "CVE-2022-1471", "desc": "任意コード実行"},
    "pillow": {"safe_from": "10.0.1", "cve": "CVE-2023-44271", "desc": "DoS"},
    "cryptography": {"safe_from": "41.0.0", "cve": "CVE-2023-49083", "desc": "NULL dereference"},
    "requests": {"safe_from": "2.31.0", "cve": "CVE-2023-32681", "desc": "Proxy-Auth header leak"},
    "werkzeug": {"safe_from": "3.0.1", "cve": "CVE-2023-46136", "desc": "DoS"},
    "flask": {"safe_from": "3.0.0", "cve": "CVE-2023-30861", "desc": "Session cookie漏洩"},
    "django": {"safe_from": "4.2.7", "cve": "CVE-2023-41164", "desc": "DoS"},
    "paramiko": {"safe_from": "3.4.0", "cve": "CVE-2023-48795", "desc": "Terrapin Attack"},
    "aiohttp": {"safe_from": "3.9.0", "cve": "CVE-2023-49082", "desc": "CRLF injection"},
    "urllib3": {"safe_from": "2.0.7", "cve": "CVE-2023-45803", "desc": "Request body漏洩"},
}

@dataclass
class TaintFlow:
    source_var: str
    source_type: str
    source_func: str
    source_line: int
    sink_call: str
    sink_func: str
    sink_line: int
    sink_type: str
    severity: str
    cwe: str
    path: list[str] = field(default_factory=list)
    cross_chunk: bool = False

@dataclass
class VulnFinding:
    vuln_type: str
    severity: str
    cwe: str
    location: str
    line: int
    evidence: str
    description: str

@dataclass
class FunctionTaintSummary:
    func_id: str
    tainted_params: list[int]
    returns_tainted: bool
    taint_sources: list[str]
    sink_calls: list[str]

@dataclass
class AnalysisChunk:
    chunk_id: str
    func_ids: list[str]
    taint_flows: list[TaintFlow] = field(default_factory=list)
    findings: list[VulnFinding] = field(default_factory=list)
    summaries: list[FunctionTaintSummary] = field(default_factory=list)

    @property
    def node_count(self) -> int:
        return len(self.func_ids)

    @property
    def is_oversized(self) -> bool:
        return self.node_count > MAX_CHUNK_NODES

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.score = 1
    def visit_If(self, n): self.score += 1; self.generic_visit(n)
    def visit_For(self, n): self.score += 1; self.generic_visit(n)
    def visit_While(self, n): self.score += 1; self.generic_visit(n)
    def visit_Try(self, n): self.score += len(n.handlers); self.generic_visit(n)
    def visit_BoolOp(self, n): self.score += len(n.values) - 1; self.generic_visit(n)
    def visit_Match(self, n): self.score += len(n.cases); self.generic_visit(n)

class TaintAnalyzer(ast.NodeVisitor):
    def __init__(self, file_path: Path, root_dir: Path, func_summaries: dict[str, 'FunctionTaintSummary'] | None = None):
        self.file_path = file_path
        self.rel_path = str(file_path.relative_to(root_dir))
        self.tainted_vars = {}
        self.flows = []
        self.scope_stack = ["module"]
        self.func_params = {}
        self.func_summaries = func_summaries or {}
        self._func_taint_summary = {}

    @property
    def current_scope(self) -> str:
        return self.scope_stack[-1]

    def _resolve_call(self, node: ast.Call) -> str:
        try:
            return ast.unparse(node.func)
        except Exception:
            return ""

    def _is_taint_source(self, node: ast.expr) -> Optional[str]:
        if isinstance(node, ast.Call):
            name = self._resolve_call(node)
            for src, src_type in TAINT_SOURCES.items():
                if name == src or name.endswith(f".{src.split('.')[-1]}"):
                    return src_type
            for fid, summary in self.func_summaries.items():
                fid_short = fid.split(".")[-1]
                if (name == fid or name.endswith(f".{fid_short}")) and summary.returns_tainted:
                    return "propagated"
        if isinstance(node, ast.Attribute):
            name = ast.unparse(node)
            for src, src_type in TAINT_SOURCES.items():
                if name == src:
                    return src_type
        return None

    def _arg_is_tainted(self, node: ast.expr) -> bool:
        if isinstance(node, ast.Name) and node.id in self.tainted_vars:
            return True
        if isinstance(node, ast.JoinedStr):
            for part in ast.walk(node):
                if isinstance(part, ast.Name) and part.id in self.tainted_vars:
                    return True
        if isinstance(node, ast.BinOp):
            return self._arg_is_tainted(node.left) or self._arg_is_tainted(node.right)
        if isinstance(node, ast.Call):
            if self._is_taint_source(node):
                return True
            return any(self._arg_is_tainted(a) for a in node.args)
        return False

    def visit_ClassDef(self, node):
        self.scope_stack.append(f"Class:{node.name}")
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node):
        scope = self.current_scope
        func_id = f"{scope}.{node.name}" if scope != "module" else node.name
        self.scope_stack.append(func_id)
        params = [a.arg for a in node.args.args]
        self.func_params[func_id] = params
        self._func_taint_summary[func_id] = FunctionTaintSummary(
            func_id=func_id, tainted_params=[], returns_tainted=False, taint_sources=[], sink_calls=[]
        )
        for idx, p in enumerate(params):
            self.tainted_vars[p] = {"type": "param", "line": node.lineno, "scope": func_id}
            self._func_taint_summary[func_id].tainted_params.append(idx)
        self.generic_visit(node)
        self.scope_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Assign(self, node):
        src_type = self._is_taint_source(node.value)
        if src_type:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.tainted_vars[target.id] = {"type": src_type, "line": node.lineno, "scope": self.current_scope}
                    if self.current_scope in self._func_taint_summary:
                        s = self._func_taint_summary[self.current_scope]
                        if src_type not in s.taint_sources:
                            s.taint_sources.append(src_type)
                elif isinstance(target, ast.Tuple):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            self.tainted_vars[elt.id] = {"type": src_type, "line": node.lineno, "scope": self.current_scope}
        self.generic_visit(node)

    def visit_Return(self, node):
        if node.value and self._arg_is_tainted(node.value):
            if self.current_scope in self._func_taint_summary:
                self._func_taint_summary[self.current_scope].returns_tainted = True
        self.generic_visit(node)

    def visit_Call(self, node):
        call_name = self._resolve_call(node)
        if not call_name:
            self.generic_visit(node)
            return
        for sink, meta in TAINT_SINKS.items():
            if call_name == sink or call_name.endswith(f".{sink.split('.')[-1]}"):
                all_args = list(node.args) + [kw.value for kw in node.keywords]
                for arg in all_args:
                    if self._arg_is_tainted(arg):
                        tvar = next((p.id for p in ast.walk(arg) if isinstance(p, ast.Name) and p.id in self.tainted_vars), None)
                        if tvar is None and isinstance(arg, ast.Call) and self._is_taint_source(arg):
                            tvar = ast.unparse(arg)
                            info = {"type": self._is_taint_source(arg), "line": getattr(arg, 'lineno', 0), "scope": self.current_scope}
                        else:
                            info = self.tainted_vars.get(tvar, {"type": "propagated", "line": getattr(arg, 'lineno', 0), "scope": self.current_scope})
                        self.flows.append(TaintFlow(
                            source_var=tvar or "<expr>", source_type=info['type'], source_func=info['scope'], source_line=info['line'],
                            sink_call=call_name, sink_func=self.current_scope, sink_line=node.lineno,
                            sink_type=meta['type'], severity=meta['severity'], cwe=meta['cwe']
                        ))
                        if self.current_scope in self._func_taint_summary:
                            s = self._func_taint_summary[self.current_scope]
                            if call_name not in s.sink_calls:
                                s.sink_calls.append(call_name)
                        break
        self.generic_visit(node)

    @property
    def function_taint_summaries(self):
        return list(self._func_taint_summary.values())

class EnhancedSecurityScanner(ast.NodeVisitor):
    def __init__(self, rel_path: str):
        self.rel_path = rel_path
        self.findings = []
        self.scope_stack = ["module"]

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

    def visit_Assign(self, node):
        try:
            src = ast.unparse(node)
        except Exception:
            self.generic_visit(node)
            return
        if HARDCODED_SECRET_RE.search(src):
            targets = [ast.unparse(t) for t in node.targets]
            self.findings.append(VulnFinding(
                vuln_type="hardcoded_secret", severity="HIGH", cwe="CWE-798",
                location=self.current_scope, line=node.lineno,
                evidence=f"代入対象: {', '.join(targets)}", description="ハードコードされた認証情報"
            ))
        self.generic_visit(node)

    def visit_Call(self, node):
        try:
            call_name = ast.unparse(node.func)
        except Exception:
            self.generic_visit(node)
            return
        for algo, cwe in WEAK_CRYPTO.items():
            if algo in call_name:
                self.findings.append(VulnFinding(
                    vuln_type="weak_crypto", severity="MEDIUM", cwe=cwe,
                    location=self.current_scope, line=node.lineno,
                    evidence=f"呼び出し: {call_name}", description=f"弱い暗号/乱数関数 {call_name}"
                ))
        if call_name == "yaml.load":
            args_str = ast.unparse(node.args[1]) if len(node.args) > 1 else "?"
            if "SafeLoader" not in args_str:
                self.findings.append(VulnFinding(
                    vuln_type="unsafe_yaml", severity="HIGH", cwe="CWE-502",
                    location=self.current_scope, line=node.lineno,
                    evidence="yaml.load(Loader未指定)", description="unsafe yaml.load"
                ))
        if call_name.endswith(".execute") or call_name == "execute":
            if node.args:
                arg0 = node.args[0]
                if isinstance(arg0, (ast.JoinedStr, ast.BinOp)):
                    self.findings.append(VulnFinding(
                        vuln_type="sql_string_concat", severity="CRITICAL", cwe="CWE-89",
                        location=self.current_scope, line=node.lineno,
                        evidence=f"execute({ast.unparse(arg0)[:60]}...)", description="SQLクエリへの文字列連結/f-string"
                    ))
        self.generic_visit(node)

class StructureCollector(ast.NodeVisitor):
    def __init__(self, file_path: Path, root_dir: Path):
        self.rel_path = str(file_path.relative_to(root_dir))
        self.scope_stack = ["module"]
        self.functions = {}
        self.classes = {}
        self.call_edges = []
        self.imports = set()

    @property
    def current_scope(self) -> str:
        return self.scope_stack[-1]

    def _current_class(self) -> Optional[str]:
        for s in reversed(self.scope_stack):
            if s.startswith("Class:"):
                return s[6:]
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
        self.classes[node.name] = {
            "bases": [ast.unparse(b) for b in node.bases],
            "doc": (ast.get_docstring(node) or "")[:120],
            "file": self.rel_path,
            "line": node.lineno,
        }
        self.scope_stack.append(f"Class:{node.name}")
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node):
        cls = self._current_class()
        func_id = f"{cls}.{node.name}" if cls else node.name
        cv = ComplexityVisitor()
        cv.visit(node)
        self.functions[func_id] = {
            "args": [a.arg for a in node.args.args],
            "returns": ast.unparse(node.returns) if node.returns else None,
            "complexity": cv.score,
            "doc": (ast.get_docstring(node) or "")[:120],
            "file": self.rel_path,
            "line": node.lineno,
        }
        self.scope_stack.append(func_id)
        self.generic_visit(node)
        self.scope_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        try:
            callee = ast.unparse(node.func)
        except Exception:
            self.generic_visit(node)
            return
        skip = {"append","update","pop","add","join","split","replace","items","keys","values","get","set","len","str","int","list","dict","print","sorted","reversed","isinstance","hasattr"}
        if callee.split(".")[-1] not in skip:
            self.call_edges.append((self.current_scope, callee))
        self.generic_visit(node)

def tarjan_scc(nodes: list[str], edges: list[tuple[str, str]]) -> list[list[str]]:
    sys.setrecursionlimit(max(10000, len(nodes) * 2 + 1000))
    index_counter = [0]
    stack = []
    lowlink = {}
    index_map = {}
    on_stack = {}
    sccs = []
    adj = defaultdict(set)
    node_set = set(nodes)
    for u, v in edges:
        if u in node_set and v in node_set:
            adj[u].add(v)
    def strongconnect(v: str):
        index_map[v] = lowlink[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack[v] = True
        for w in adj.get(v, []):
            if w not in index_map:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack.get(w):
                lowlink[v] = min(lowlink[v], index_map[w])
        if lowlink[v] == index_map[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)
    for node in nodes:
        if node not in index_map:
            strongconnect(node)
    return sccs

def build_chunks(all_functions, all_call_edges, all_taint_flows, all_findings, all_summaries):
    func_ids = list(all_functions.keys())
    sccs = tarjan_scc(func_ids, all_call_edges)
    final_groups = []
    for scc in sccs:
        if len(scc) <= MAX_CHUNK_NODES:
            final_groups.append(scc)
        else:
            by_file = defaultdict(list)
            for fid in scc:
                fname = all_functions.get(fid, {}).get("file", "unknown")
                by_file[fname].append(fid)
            for sub in by_file.values():
                for i in range(0, len(sub), MAX_CHUNK_NODES):
                    final_groups.append(sub[i:i + MAX_CHUNK_NODES])
    chunks = []
    for idx, group in enumerate(final_groups):
        group_set = set(group)
        chunk_flows = [f for f in all_taint_flows if f.source_func in group_set or f.sink_func in group_set]
        chunk_findings = [f for f in all_findings if f.location in group_set]
        chunk_summaries = [all_summaries[fid] for fid in group if fid in all_summaries]
        chunks.append(AnalysisChunk(chunk_id=f"C{idx:03d}", func_ids=group, taint_flows=chunk_flows, findings=chunk_findings, summaries=chunk_summaries))
    return chunks

def cross_chunk_reduce(chunks, all_summaries, all_call_edges):
    chunk_of = {}
    for chunk in chunks:
        for fid in chunk.func_ids:
            chunk_of[fid] = chunk.chunk_id
    propagators = {fid for fid, s in all_summaries.items() if s.returns_tainted}
    cross_flows = []
    for prop_func in propagators:
        for caller, callee in all_call_edges:
            if callee != prop_func:
                continue
            caller_summary = all_summaries.get(caller)
            if caller_summary and caller_summary.sink_calls:
                chunk_a = chunk_of.get(prop_func, "?")
                chunk_b = chunk_of.get(caller, "?")
                if chunk_a != chunk_b:
                    for sink_call in caller_summary.sink_calls:
                        sink_meta = TAINT_SINKS.get(sink_call, TAINT_SINKS.get(sink_call.split(".")[-1], {}))
                        if not sink_meta:
                            continue
                        cross_flows.append(TaintFlow(
                            source_var=f"ret({prop_func})", source_type="propagated", source_func=prop_func, source_line=0,
                            sink_call=sink_call, sink_func=caller, sink_line=0,
                            sink_type=sink_meta.get("type", "unknown"), severity=sink_meta.get("severity", "HIGH"),
                            cwe=sink_meta.get("cwe", "N/A"), path=[prop_func, caller], cross_chunk=True
                        ))
    return cross_flows

def safe_id(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", s)

def severity_emoji(s: str) -> str:
    return {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(s, "⚪")

def _render_chunk_for_ai(chunk, all_functions, all_call_edges, all_summaries) -> str:
    group_set = set(chunk.func_ids)
    md = []
    critical_n = sum(1 for f in chunk.taint_flows if f.severity == "CRITICAL")
    high_n = sum(1 for f in chunk.taint_flows if f.severity == "HIGH")
    cross_n = sum(1 for f in chunk.taint_flows if f.cross_chunk)
    rough_chars = sum(len(fid) * 5 for fid in chunk.func_ids)
    est_tokens = rough_chars // APPROX_CHARS_PER_TOKEN
    md.append(f"## Chunk {chunk.chunk_id}  [{chunk.node_count} 関数]")
    md.append(f"> 🔴 CRITICAL: {critical_n}  🟠 HIGH: {high_n}  🔗 Cross-chunk: {cross_n}  ~{est_tokens} tokens")
    md.append("")
    if chunk.is_oversized:
        md.append(f"> ⚠️ このチャンクはノード数 {chunk.node_count} で上限 {MAX_CHUNK_NODES} を超えています。精度低下に注意。")
        md.append("")
    md.append("### A. 関数シグネチャ")
    md.append("")
    md.append("```")
    md.append("# func_id (args) -> return  [cyclo] [taint_in?→taint_out?]")
    for fid in sorted(chunk.func_ids):
        info = all_functions.get(fid, {})
        args = ", ".join(info.get("args", []))
        ret = info.get("returns") or "?"
        cyclo = info.get("complexity", 1)
        summary = all_summaries.get(fid)
        taint_in = "T_IN" if (summary and summary.tainted_params) else "."
        taint_out = "T_OUT" if (summary and summary.returns_tainted) else "."
        sink_mark = " ⚠️SINK" if (summary and summary.sink_calls) else ""
        md.append(f"{fid}({args}) -> {ret}  [cc={cyclo}] [{taint_in}→{taint_out}]{sink_mark}")
    md.append("```")
    md.append("")
    md.append("### B. 呼び出しグラフ (チャンク内)")
    md.append("")
    md.append("```mermaid")
    md.append("graph LR")
    external_seen = set()
    for caller, callee in all_call_edges:
        if caller not in group_set:
            continue
        caller_id = safe_id(caller)
        if callee in group_set:
            md.append(f'    {caller_id}["{caller}"] --> {safe_id(callee)}["{callee}"]')
        else:
            ext_key = f"EXT_{safe_id(callee)}"
            if ext_key not in external_seen:
                md.append(f'    {ext_key}(["⬛ {callee}"]):::external')
                external_seen.add(ext_key)
            md.append(f'    {caller_id} -.-> {ext_key}')
    md.append('    classDef external fill:#555,color:#fff,stroke-dasharray:4')
    md.append("```")
    md.append("")
    intra_flows = [f for f in chunk.taint_flows if not f.cross_chunk]
    if intra_flows:
        md.append("### C. テイントフロー (チャンク内)")
        md.append("")
        md.append("```mermaid")
        md.append("graph LR")
        for i, flow in enumerate(intra_flows):
            src = safe_id(f"S{i}_{flow.source_type}")
            snk = safe_id(f"K{i}_{flow.sink_call}")
            md.append(f'    {src}["⚠️ {flow.source_type}\\n`{flow.source_var}`@L{flow.source_line}"]')
            md.append(f'    {snk}["{severity_emoji(flow.severity)} {flow.sink_call}\\n{flow.cwe}"]')
            md.append(f'    {src} -->|"{flow.source_func}→{flow.sink_func}"| {snk}')
        md.append("```")
        md.append("")
        md.append("| # | Sev | 変数 | 入力源 | 定義関数 | シンク | 脆弱性 | CWE |")
        md.append("|:--|:---:|:---|:---|:---|:---|:---|:---|")
        for i, f in enumerate(sorted(intra_flows, key=lambda x: SEVERITY_ORDER.get(x.severity, 9))):
            md.append(f"| {i+1} | {severity_emoji(f.severity)}{f.severity} | `{f.source_var}` | {f.source_type} | `{f.source_func}` | `{f.sink_call}` | **{f.sink_type}** | {f.cwe} |")
        md.append("")
    cross_flows = [f for f in chunk.taint_flows if f.cross_chunk]
    boundary_in = [s for fid, s in all_summaries.items() if fid not in group_set and s.returns_tainted and any(callee == fid for caller, callee in all_call_edges if caller in group_set)]
    boundary_out = [s for fid in chunk.func_ids if (s := all_summaries.get(fid)) and s.returns_tainted]
    if boundary_in or boundary_out or cross_flows:
        md.append("### D. チャンク境界サマリー")
        md.append("")
        if boundary_in:
            md.append("**このチャンクが呼び出す、汚染戻り値を持つ外部関数:**")
            for s in boundary_in:
                md.append(f"- `{s.func_id}` — sources: {s.taint_sources}")
        if boundary_out:
            md.append("")
            md.append("**このチャンクが外部に汚染を伝播させる可能性のある関数:**")
            for s in boundary_out:
                md.append(f"- `{s.func_id}` — sinks: {s.sink_calls}")
        if cross_flows:
            md.append("")
            md.append("**クロスチャンク・テイントフロー検出:**")
            for f in cross_flows:
                md.append(f"- {severity_emoji(f.severity)} `{f.source_func}` → `{f.sink_func}` ({f.sink_type}, {f.cwe})")
        md.append("")
    md.append("### E. AIタスク (このチャンク専用)")
    md.append("")
    md.append("```")
    md.append("あなたはセキュリティ専門家です。以下の構造データのみで分析してください。")
    md.append("")
    tasks = []
    if critical_n > 0:
        tasks.append(f"1. 🔴 CRITICAL テイントフローが {critical_n} 件あります。各フローについて具体的な悪用シナリオ（POCの骨格）を記述してください。")
    if cross_n > 0:
        tasks.append(f"2. 🔗 クロスチャンク伝播が {cross_n} 件あります。セクションDの境界サマリーを元に、伝播チェーンの完全パスを復元してください。")
    high_cyclo = [(fid, all_functions[fid]['complexity']) for fid in chunk.func_ids if all_functions.get(fid, {}).get('complexity', 0) >= 8]
    if high_cyclo:
        names = ", ".join(f"`{fid}`" for fid, _ in high_cyclo[:3])
        tasks.append(f"3. 🟡 高複雑度関数 {names} (cc≥8) に潜む認証バイパス・ロジックバグを推論してください。")
    if chunk.findings:
        crit_static = [f for f in chunk.findings if f.severity == 'CRITICAL']
        if crit_static:
            tasks.append(f"4. 静的スキャンで CRITICAL が {len(crit_static)} 件。テイントフローと組み合わさると悪化するケースを特定してください。")
    if not tasks:
        tasks.append("1. セクションA〜Cを精査し、潜在的リスクを優先度付きで列挙してください。")
    for t in tasks:
        md.append(t)
    md.append("")
    md.append("## 出力形式")
    md.append("- CRITICAL→HIGH→MEDIUM の順")
    md.append("- 各リスク: 根拠(セクション参照) / 悪用シナリオ / 修正骨格")
    md.append(f"- チャンクID: {chunk.chunk_id} を各発見に付記すること")
    md.append("```")
    md.append("")
    result = "\n".join(md)
    final_tokens = len(result) // APPROX_CHARS_PER_TOKEN
    if final_tokens > 6000:
        result = f"> ⚠️ **トークン警告**: このチャンクは推定 {final_tokens} tokens です。MAX_CHUNK_NODES={MAX_CHUNK_NODES} を下げることを検討してください。\n\n" + result
    return result

def audit_requirements(root_dir: Path) -> list[dict]:
    findings = []
    for req_file in list(root_dir.rglob("requirements*.txt")) + list(root_dir.rglob("pyproject.toml")):
        try:
            text = req_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r'^([A-Za-z0-9_\-\.]+)', line)
            if not m:
                continue
            pkg = m.group(1).lower().replace("-", "_").replace(".", "_")
            for vpkg, meta in KNOWN_VULNERABLE_PACKAGES.items():
                if pkg == vpkg.replace("-", "_"):
                    findings.append({
                        "package": vpkg, "cve": meta["cve"], "safe_from": meta["safe_from"],
                        "desc": meta["desc"], "req_file": str(req_file.relative_to(root_dir))
                    })
    return findings

def generate_report(target_dir: str, output_file: str = "security_report_v5.md") -> str:
    root = Path(target_dir).absolute()
    py_files = sorted(root.rglob("*.py"))
    if not py_files:
        return "# Error\n\nPythonファイルが見つかりませんでした。"
    all_functions = {}
    all_classes = {}
    all_call_edges = []
    all_imports = set()
    parse_errors = []
    for py_file in py_files:
        try:
            src = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(src, filename=str(py_file))
        except SyntaxError as e:
            parse_errors.append((str(py_file.relative_to(root)), e))
            continue
        col = StructureCollector(py_file, root)
        col.visit(tree)
        all_functions.update(col.functions)
        all_classes.update(col.classes)
        all_call_edges.extend(col.call_edges)
        all_imports.update(col.imports)
    all_summaries_pass1 = {}
    for py_file in py_files:
        try:
            src = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(src, filename=str(py_file))
        except SyntaxError:
            continue
        ta = TaintAnalyzer(py_file, root)
        ta.visit(tree)
        for s in ta.function_taint_summaries:
            all_summaries_pass1[s.func_id] = s
    all_taint_flows = []
    all_vuln_findings = []
    all_summaries = {}
    for py_file in py_files:
        try:
            src = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(src, filename=str(py_file))
        except SyntaxError:
            continue
        ta = TaintAnalyzer(py_file, root, func_summaries=all_summaries_pass1)
        ta.visit(tree)
        all_taint_flows.extend(ta.flows)
        for s in ta.function_taint_summaries:
            all_summaries[s.func_id] = s
        scanner = EnhancedSecurityScanner(str(py_file.relative_to(root)))
        scanner.visit(tree)
        all_vuln_findings.extend(scanner.findings)
    chunks = build_chunks(all_functions, all_call_edges, all_taint_flows, all_vuln_findings, all_summaries)
    cross_flows = cross_chunk_reduce(chunks, all_summaries, all_call_edges)
    for cf in cross_flows:
        for chunk in chunks:
            if cf.sink_func in chunk.func_ids:
                chunk.taint_flows.append(cf)
                break
    dep_findings = audit_requirements(root)
    total_critical = sum(1 for f in all_taint_flows if f.severity == "CRITICAL")
    total_high = sum(1 for f in all_taint_flows if f.severity == "HIGH")
    md = []
    md.append("# Python セキュリティ構造マップ v5 (チャンク分析版)")
    md.append("")
    md.append(f"> 対象: `{root}` — {len(py_files)} ファイル / {len(chunks)} チャンク / {len(all_functions)} 関数")
    md.append("")
    md.append("> ⚠️ このレポートはソースコードを含みません。")
    md.append("")
    md.append("## 📊 サマリー")
    md.append("")
    md.append("| 項目 | 値 |")
    md.append("|:---|---:|")
    md.append(f"| 解析ファイル | {len(py_files)} |")
    md.append(f"| チャンク数 | {len(chunks)} |")
    md.append(f"| 関数数 | {len(all_functions)} |")
    md.append(f"| クラス数 | {len(all_classes)} |")
    md.append(f"| テイントフロー CRITICAL | 🔴 {total_critical} |")
    md.append(f"| テイントフロー HIGH | 🟠 {total_high} |")
    md.append(f"| クロスチャンクフロー | 🔗 {len(cross_flows)} |")
    md.append(f"| 静的指摘 | {len(all_vuln_findings)} |")
    md.append(f"| 脆弱パッケージ | ⚠️ {len(dep_findings)} |")
    md.append(f"| 推定総トークン | ~{sum(len(c.func_ids)*20 for c in chunks)//APPROX_CHARS_PER_TOKEN} |")
    md.append("")
    md.append("---")
    md.append("## 🗂️ チャンク索引")
    md.append("")
    md.append("| Chunk | 関数数 | CRITICAL | HIGH | Cross | 代表関数 |")
    md.append("|:---|:---:|:---:|:---:|:---:|:---|")
    for chunk in chunks:
        c_cnt = sum(1 for f in chunk.taint_flows if f.severity == "CRITICAL" and not f.cross_chunk)
        h_cnt = sum(1 for f in chunk.taint_flows if f.severity == "HIGH" and not f.cross_chunk)
        x_cnt = sum(1 for f in chunk.taint_flows if f.cross_chunk)
        rep = chunk.func_ids[0] if chunk.func_ids else ""
        warn = " ⚠️" if chunk.is_oversized else ""
        md.append(f"| `{chunk.chunk_id}`{warn} | {chunk.node_count} | {'🔴 '+str(c_cnt) if c_cnt else '-'} | {'🟠 '+str(h_cnt) if h_cnt else '-'} | {'🔗 '+str(x_cnt) if x_cnt else '-'} | `{rep}` |")
    if dep_findings:
        md.append("")
        md.append("---")
        md.append("## ⚠️ 依存関係監査")
        md.append("")
        md.append("| パッケージ | CVE | 安全バージョン | 説明 |")
        md.append("|:---|:---|:---|:---|")
        for f in dep_findings:
            md.append(f"| `{f['package']}` | [{f['cve']}](https://nvd.nist.gov/vuln/detail/{f['cve']}) | `>= {f['safe_from']}` | {f['desc']} |")
    md.append("")
    md.append("---")
    md.append("# 📦 チャンク別AI分析セクション")
    md.append("")
    md.append("> 以下の各チャンクを**個別に**AIへ送信してください。")
    md.append("")
    for chunk in chunks:
        md.append(_render_chunk_for_ai(chunk, all_functions, all_call_edges, all_summaries))
        md.append("---")
        md.append("")
    report_text = "\n".join(md)
    Path(output_file).write_text(report_text, encoding="utf-8")
    print(f"[+] v5 レポート生成完了: {output_file} ({len(report_text):,} chars)")
    print(f"[+] チャンク数: {len(chunks)}")
    print(f"[+] クロスチャンクフロー: {len(cross_flows)} 件")
    print(f"[+] テイントフロー: {len(all_taint_flows)} 件")
    return report_text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deep_analyzer_v5.py <target_dir> [output.md]")
        print(f"       MAX_CHUNK_NODES={MAX_CHUNK_NODES} (env: MAX_CHUNK_NODES=N で変更)")
        sys.exit(1)
    target = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "security_report_v5.md"
    generate_report(target, output)
