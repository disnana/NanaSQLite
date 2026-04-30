#!/usr/bin/env python3
"""
Security Report Generator v6 - AI-Native Edition
使い方:
  python gen_report_v6.py ./src --output report.md
  python gen_report_v6.py ./src --output report.md --snapshot snap.json
  python gen_report_v6.py ./src --output report.md --diff snap.json --snapshot snap_new.json
"""

import ast
import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from collections import defaultdict


# ══════════════════════════════════════════════════════════════════
# データモデル
# ══════════════════════════════════════════════════════════════════

@dataclass
class ChunkInfo:
    chunk_id: str
    file_path: str
    class_name: Optional[str]
    func_name: str
    full_name: str
    line_start: int
    line_end: int
    cc: int
    tier: int           # 1=TIER1, 2=TIER2, 3=TIER3, 0=SKIP
    args: list
    return_annotation: str
    calls: list         # このチャンクが呼ぶ関数名リスト
    called_by: list     # このチャンクを呼ぶ関数名リスト
    taint_in: bool      # 外部入力を受け取る引数が存在するか
    taint_out: bool     # 汚染された値を返すか
    content_hash: str   # diff用のMD5


# ══════════════════════════════════════════════════════════════════
# 循環複雑度（CC）計算
# ══════════════════════════════════════════════════════════════════

class CCVisitor(ast.NodeVisitor):
    """AST を走査して循環複雑度を算出する。"""

    def __init__(self):
        self.cc = 1  # 関数本体のベース値

    def visit_If(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        # and / or の連鎖ごとに +1
        self.cc += len(node.values) - 1
        self.generic_visit(node)

    def visit_IfExp(self, node):
        # 三項演算子
        self.cc += 1
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_comprehension(self, node):
        self.cc += 1
        self.generic_visit(node)

    # Python 3.10+ match/case
    def visit_match_case(self, node):
        self.cc += 1
        self.generic_visit(node)


def calc_cc(func_node: ast.FunctionDef) -> int:
    v = CCVisitor()
    v.visit(func_node)
    return v.cc


# ══════════════════════════════════════════════════════════════════
# 呼び出しグラフ抽出
# ══════════════════════════════════════════════════════════════════

class CallVisitor(ast.NodeVisitor):
    """関数本体内の呼び出し式を列挙する。"""

    def __init__(self):
        self.calls: list[str] = []

    def visit_Call(self, node):
        name = self._unparse_func(node.func)
        if name:
            self.calls.append(name)
        self.generic_visit(node)

    def _unparse_func(self, node) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parent = self._unparse_func(node.value)
            return f"{parent}.{node.attr}" if parent else node.attr
        if isinstance(node, ast.Call):
            return self._unparse_func(node.func)
        return ""


def extract_calls(func_node: ast.FunctionDef) -> list[str]:
    v = CallVisitor()
    v.visit(func_node)
    # 重複排除・順序保持
    seen, result = set(), []
    for c in v.calls:
        if c not in seen:
            seen.add(c)
            result.append(c)
    return result


# ══════════════════════════════════════════════════════════════════
# TIER 判定ルール
# ══════════════════════════════════════════════════════════════════

# cc 値に関係なく TIER-1 に強制昇格
FORCE_TIER1: set[str] = {
    "NanaSQLite._validate_expression",
    "sanitize_sql_for_function_scan",
    "NanaSQLite.restore",
    "NanaSQLite.backup",
    "fast_validate_sql_chars",
}

# 信頼境界に直接触れる関数 → TIER-2 に昇格
TRUST_BOUNDARY: set[str] = {
    "NanaSQLite._sanitize_identifier",
    "NanaSQLite._serialize",
    "NanaSQLite._deserialize",
    "NanaSQLite.pragma",
    "NanaSQLite.execute",
    "NanaSQLite.execute_many",
    "V2Engine._add_to_dlq",
    "V2Engine.get_dlq",
    "NanaSQLite.get_dlq",
}

# 常にスキップ（cc=1 の AsyncWrapper 群など）
SKIP_CLASS_PREFIXES: tuple[str, ...] = (
    "AsyncNanaSQLite.",
    "CacheStrategy.",
    "NanaHook.",
)

SKIP_EXACT: set[str] = {
    "_AsyncTransactionContext.__init__",
    "_AsyncTransactionContext.__aenter__",
    "_AsyncTransactionContext.__aexit__",
    "_TransactionContext.__init__",
    "_TransactionContext.__enter__",
    "_TransactionContext.__exit__",
}

# テイント判定キーワード
TAINT_ARG_KEYWORDS: frozenset[str] = frozenset({
    "sql", "query", "key", "value", "path", "src_path",
    "dest_path", "table", "table_name", "expr", "where",
    "order_by", "group_by", "columns", "pragma_name",
    "encryption_key", "identifier", "column_name",
})

NON_TAINT_RETURNS: frozenset[str] = frozenset({"None", "bool", "int", "", "?"})


def assign_tier(chunk: ChunkInfo) -> int:
    name = chunk.full_name

    # 強制スキップ
    if name in SKIP_EXACT:
        return 0
    if any(name.startswith(p) for p in SKIP_CLASS_PREFIXES) and chunk.cc <= 2:
        return 0

    # 強制 TIER-1
    if name in FORCE_TIER1:
        return 1
    if chunk.cc >= 18:
        return 1

    # TIER-2
    if chunk.cc >= 8:
        return 2
    if name in TRUST_BOUNDARY:
        return 2

    # TIER-3
    if chunk.cc >= 4:
        return 3

    # SKIP
    return 0


# ══════════════════════════════════════════════════════════════════
# ファイル単位の解析
# ══════════════════════════════════════════════════════════════════

class FileAnalyzer:

    def __init__(self, file_path: Path, base_dir: Path):
        self.file_path = file_path
        self.base_dir = base_dir
        self.source = file_path.read_text(encoding="utf-8", errors="replace")
        self.tree = ast.parse(self.source, filename=str(file_path))
        self._class_map: dict[int, str] = {}  # node id → class name
        self._build_class_map()

    def _build_class_map(self):
        """各関数ノードがどのクラスに属するかを事前計算する。"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                for child in ast.walk(node):
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        self._class_map[id(child)] = node.name

    def analyze(self) -> list[ChunkInfo]:
        chunks: list[ChunkInfo] = []
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                chunk = self._make_chunk(node)
                if chunk:
                    chunks.append(chunk)
        chunks.sort(key=lambda c: c.line_start)
        return chunks

    def _make_chunk(self, node) -> Optional["ChunkInfo"]:
        class_name = self._class_map.get(id(node))
        func_name  = node.name
        full_name  = f"{class_name}.{func_name}" if class_name else func_name

        args = [a.arg for a in node.args.args]

        ret = ast.unparse(node.returns) if node.returns else "?"

        cc    = calc_cc(node)
        calls = extract_calls(node)

        # ハッシュ（diff 用）
        seg = ast.get_source_segment(self.source, node) or func_name
        h   = hashlib.md5(seg.encode()).hexdigest()[:8]

        taint_in  = any(a.lower() in TAINT_ARG_KEYWORDS for a in args)
        taint_out = ret not in NON_TAINT_RETURNS

        rel_path = str(self.file_path.relative_to(self.base_dir))

        return ChunkInfo(
            chunk_id="",        # 後で付与
            file_path=rel_path,
            class_name=class_name,
            func_name=func_name,
            full_name=full_name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            cc=cc,
            tier=0,             # 後で計算
            args=args,
            return_annotation=ret,
            calls=calls,
            called_by=[],       # 後で逆引き
            taint_in=taint_in,
            taint_out=taint_out,
            content_hash=h,
        )


# ══════════════════════════════════════════════════════════════════
# プロジェクト全体の解析
# ══════════════════════════════════════════════════════════════════

class ProjectAnalyzer:

    def __init__(self, target_dir: Path):
        self.target_dir = target_dir
        self.chunks: list[ChunkInfo] = []
        self.chunk_map: dict[str, ChunkInfo] = {}

    def analyze(self) -> "ProjectAnalyzer":
        py_files = sorted(self.target_dir.rglob("*.py"))
        all_chunks: list[ChunkInfo] = []

        for py_file in py_files:
            try:
                fa = FileAnalyzer(py_file, self.target_dir)
                all_chunks.extend(fa.analyze())
            except SyntaxError as e:
                print(f"  ⚠️  構文エラー: {py_file}: {e}", file=sys.stderr)

        # ChunkID 付与（グローバル通し番号）
        for i, chunk in enumerate(all_chunks):
            chunk.chunk_id = f"C{i:03d}"
            chunk.tier = assign_tier(chunk)

        self.chunks = all_chunks
        self.chunk_map = {c.full_name: c for c in all_chunks}
        self._build_called_by()
        return self

    def _build_called_by(self):
        all_names = {c.full_name for c in self.chunks}
        for chunk in self.chunks:
            for callee in chunk.calls:
                # 完全一致 or 末尾一致でマッチ
                for target in self.chunks:
                    if (target.full_name == callee
                            or target.func_name == callee
                            or target.full_name.endswith(f".{callee}")):
                        if chunk.full_name not in target.called_by:
                            target.called_by.append(chunk.full_name)

    def get_by_tier(self, tier: int) -> list[ChunkInfo]:
        return [c for c in self.chunks if c.tier == tier]

    def stats(self) -> dict:
        return {
            "files":        len(set(c.file_path for c in self.chunks)),
            "total":        len(self.chunks),
            "tier1":        len(self.get_by_tier(1)),
            "tier2":        len(self.get_by_tier(2)),
            "tier3":        len(self.get_by_tier(3)),
            "skip":         len(self.get_by_tier(0)),
            "classes":      sorted(set(c.class_name for c in self.chunks if c.class_name)),
            "file_list":    sorted(set(c.file_path for c in self.chunks)),
        }


# ══════════════════════════════════════════════════════════════════
# Diff エンジン
# ══════════════════════════════════════════════════════════════════

class DiffEngine:

    def __init__(self, prev_snapshot: dict):
        self.prev = prev_snapshot  # {full_name: hash}

    def compute(self, chunks: list[ChunkInfo]) -> dict:
        cur = {c.full_name: c.content_hash for c in chunks}
        added   = [n for n in cur  if n not in self.prev]
        removed = [n for n in self.prev if n not in cur]
        changed = [n for n in cur  if n in self.prev and cur[n] != self.prev[n]]
        return {"added": added, "removed": removed, "changed": changed}

    @staticmethod
    def save(chunks: list[ChunkInfo], path: Path):
        snap = {c.full_name: c.content_hash for c in chunks}
        path.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")


# ══════════════════════════════════════════════════════════════════
# Mermaid 呼び出しグラフ生成
# ══════════════════════════════════════════════════════════════════

def make_mermaid(chunk: ChunkInfo, all_full_names: set[str]) -> str:
    lines = ["graph LR"]
    src = chunk.full_name.replace(".", "_").replace("<", "").replace(">", "")

    if not chunk.calls:
        lines.append("    classDef external fill:#555,color:#fff,stroke-dasharray:4")
        return "\n".join(lines)

    seen: set[str] = set()
    for callee in chunk.calls[:15]:
        if callee in seen:
            continue
        seen.add(callee)
        safe = (callee.replace(".", "_").replace("(", "")
                      .replace(")", "").replace(" ", "_"))
        is_internal = (
            callee in all_full_names
            or any(n.endswith(f".{callee}") for n in all_full_names)
        )
        if is_internal:
            lines.append(f'    {src} --> {safe}["{callee}"]')
        else:
            lines.append(f'    EXT_{safe}(["⬛ {callee}"]):::external')
            lines.append(f"    {src} -.-> EXT_{safe}")

    lines.append("    classDef external fill:#555,color:#fff,stroke-dasharray:4")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
# レポート生成
# ══════════════════════════════════════════════════════════════════

TIER_EMOJI = {1: "🔴", 2: "🟠", 3: "🟡", 0: "⬜"}
TIER_LABEL = {1: "TIER-1 必読", 2: "TIER-2 文脈依存", 3: "TIER-3 参考", 0: "SKIP 読まなくてよい"}


class ReportGenerator:

    def __init__(
        self,
        project: ProjectAnalyzer,
        diff_info: Optional[dict] = None,
        tier1_only: bool = False,
    ):
        self.project    = project
        self.diff_info  = diff_info or {}
        self.tier1_only = tier1_only
        self.stats      = project.stats()
        self.all_names  = {c.full_name for c in project.chunks}
        self.now        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── diff ユーティリティ ──────────────────────────────────────

    def _diff_mark(self, full_name: str) -> str:
        if not self.diff_info:
            return ""
        if full_name in self.diff_info.get("added", []):
            return " 🆕"
        if full_name in self.diff_info.get("changed", []):
            return " 🔄"
        return ""

    # ── セクション: ENTRY POINT ──────────────────────────────────

    def _entry_point(self) -> str:
        s = self.stats
        tier1_count = s["tier1"]
        total       = s["total"]
        recommended = tier1_count + s["tier2"]

        diff_block = ""
        if self.diff_info:
            d = self.diff_info
            diff_block = (
                f"\n⚡ DIFF MODE 有効\n"
                f"  追加: {len(d.get('added', []))} 変更: {len(d.get('changed', []))} "
                f"削除: {len(d.get('removed', []))}\n"
                f"  → 変更のあった関数を優先的に分析せよ（[CHUNKS目次]に★マーク付き）\n"
            )

        return f"""\
<!--
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI ENTRY POINT — まずここだけ読め（このブロックは約50行）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

あなたは: シニアセキュリティアーキテクト
プロジェクト: {self.project.target_dir.name}
生成日時: {self.now}
{diff_block}
あなたの仕事:
  このレポートを読み、脆弱性を発見し、[OUTPUT]形式で統合レポートを出力すること

▼ 作業手順（この順番で進めよ）

  STEP 1 → [TRIAGE]      を読む  … システム全体像・信頼境界の把握
  STEP 2 → [HOTMAP]      を読む  … 読む関数を自分で絞り込む
  STEP 3 → [CALLCHAIN]   を読む  … データが流れる経路を追跡する
  STEP 4 → [BLIND]       を読む  … 静的解析が見落とす領域を推論する
  STEP 5 → 必要なら[CHUNKS目次]で行番号を確認し、その箇所だけ参照する
  STEP 6 → [OUTPUT]形式で統合レポートを1本出力する

⚠️ 読まなくていいもの（時間とトークンの無駄）
  - cc=1 の AsyncWrapper 群・抽象基底クラスの stub（SKIP 指定済み）
  - [CHUNKS目次] の全行 → 必要なチャンクだけ参照せよ
  - CVEリスト・静的解析スコア → このレポートには存在しない。AIの推論で代替する

💡 推奨戦略
  TIER-1（{tier1_count}関数）だけ読めば主要リスクの8割はカバーできる。
  推奨読み込み範囲: TIER-1 + TIER-2 = {recommended}関数 / 全{total}チャンク中

▶ では [TRIAGE] セクションへ進め
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-->"""

    # ── セクション: 概要 ─────────────────────────────────────────

    def _overview(self) -> str:
        s = self.stats
        return f"""\
# Python セキュリティ構造マップ v6 (AI-Native Edition)

> 対象: `{self.project.target_dir}` — {s['files']}ファイル / {s['total']}チャンク
> 生成: {self.now}
> ⚠️ ソースコードを含みません。構造・シグネチャ・呼び出しグラフのみです。
> CVEマッチングは行いません。AIの文脈推論に完全委譲します。

| 項目 | 値 |
|:---|---:|
| 解析ファイル | {s['files']} |
| 総チャンク数 | {s['total']} |
| 🔴 TIER-1（必読） | {s['tier1']} |
| 🟠 TIER-2（文脈依存） | {s['tier2']} |
| 🟡 TIER-3（参考） | {s['tier3']} |
| ⬜ SKIP（読む必要なし） | {s['skip']} |"""

    # ── セクション: セクション目次 ───────────────────────────────

    def _section_toc(self) -> str:
        return """\
## 📑 セクション目次

| セクション | 内容 | 読むべきか |
|:---|:---|:---:|
| [TRIAGE]     | 信頼境界・アーキテクチャ・暗号化・非同期モデル | ✅ 必読 |
| [HOTMAP]     | 優先関数リスト TIER-1〜3・スキップ対象 | ✅ 必読 |
| [CALLCHAIN]  | データフロー追跡（書き込み/クエリ/暗号化/ファイル） | ✅ 必読 |
| [BLIND]      | 静的解析の盲点 7カテゴリ | ✅ 必読 |
| [CHUNKS目次] | 全チャンクの関数名・行範囲・cc・TIER | 🔍 必要時のみ |
| [CHUNKS本体] | 各チャンクの詳細（TIER-1→2→3→SKIP順） | 🔍 TIER-1のみ推奨 |
| [OUTPUT]     | 統合レポートの出力フォーマット定義 | ✅ 最後に参照 |"""

    # ── セクション: TRIAGE ───────────────────────────────────────

    def _triage(self) -> str:
        s = self.stats
        files_str   = "\n".join(f"  {f}" for f in s["file_list"])
        classes_str = "\n".join(f"  {cl}" for cl in s["classes"])

        # 実際に検出された引数キーワードを集計
        found_taint_args = sorted(set(
            a.lower()
            for c in self.project.chunks
            for a in c.args
            if a.lower() in TAINT_ARG_KEYWORDS
        ))
        taint_args_str = ", ".join(found_taint_args) if found_taint_args else "（検出なし）"

        return f"""\
---

## [TRIAGE] — システム全体像と信頼境界

### 解析対象ファイル

```
{files_str}
```

### 検出クラス一覧

```
{classes_str}
```

### 信頼境界（外部入力が触れる引数キーワード）

```
このコードベースで検出された危険な引数名:
  {taint_args_str}

リスクカテゴリ別:
  sql, query, expr, where, order_by, group_by
      → SQL インジェクション系
  key, value
      → KV ストア操作・シリアライズ
  table_name, column_name, identifier
      → DDL/DML での identifier injection
  path, src_path, dest_path
      → ファイルシステム操作・パストラバーサル
  pragma_name
      → PRAGMA injection
  encryption_key
      → 暗号鍵の管理・保管
```

### アーキテクチャ概要（解析から推定）

```
外部コード
  │
  ├─ AsyncNanaSQLite     ← asyncio ラッパー層
  │    ほぼ全メソッドが run_in_executor で NanaSQLite に委譲
  │
  ├─ NanaSQLite          ← 本体・全ロジックはここ
  │   ├─ Cache 層        UnboundedCache / StdLRUCache
  │   │                  FastLRUCache / TTLCache / ExpiringDict
  │   ├─ Hook 層         CheckHook / UniqueHook / ForeignKeyHook
  │   │                  PydanticHook / ValidkitHook
  │   └─ V2Engine        非同期書き込みキュー + DLQ
  │
  └─ apsw（SQLite）      ← 標準 sqlite3 より低レベルなバインディング
```

### 非同期書き込みモデル（V2Engine）

```
write 要求
  → kvs_set()        staging dict に積む（メモリ）
  → _check_auto_flush()
  → flush()          ThreadPoolExecutor で非同期実行
  → _perform_flush()
  → _process_kvs_chunk()  apsw cursor.executemany
  → 失敗時 → _recover_chunk_via_dlq() → _add_to_dlq()

重要: staging 中のデータは SQLite に未反映
      close() / read() との競合タイミングが存在する
```"""

    # ── セクション: HOTMAP ───────────────────────────────────────

    def _hotmap(self) -> str:
        def tier_table(chunks: list[ChunkInfo]) -> str:
            if not chunks:
                return "（対象なし）\n"
            header = (
                "| 関数名 | ChunkID | cc | 場所 |\n"
                "|:---|:---:|:---:|:---|\n"
            )
            rows = []
            for c in chunks:
                dm = self._diff_mark(c.full_name)
                rows.append(
                    f"| `{c.full_name}{dm}` | {c.chunk_id} | {c.cc} "
                    f"| `{c.file_path}:{c.line_start}` |"
                )
            return header + "\n".join(rows) + "\n"

        t1 = sorted(self.project.get_by_tier(1), key=lambda c: -c.cc)
        t2 = sorted(self.project.get_by_tier(2), key=lambda c: -c.cc)
        t3 = sorted(self.project.get_by_tier(3), key=lambda c: -c.cc)
        sk = self.project.get_by_tier(0)

        skip_classes = sorted(set(
            c.class_name or c.func_name for c in sk
        ))
        skip_str = ", ".join(skip_classes[:10])
        if len(skip_classes) > 10:
            skip_str += f" ... 他{len(skip_classes)-10}クラス"

        return f"""\
---

## [HOTMAP] — 読む関数の優先度リスト

### 🔴 TIER-1: 必読（cc≥18 または 信頼境界直結の高リスク関数）

{tier_table(t1)}

### 🟠 TIER-2: 文脈依存（呼び出し関係で危険になりうる関数）

{tier_table(t2)}

### 🟡 TIER-3: 参考（cc 4〜7、文脈によっては重要）

{tier_table(t3)}

### ⬜ SKIP推奨（{len(sk)}個）

```
{skip_str}
理由: cc=1 のラッパー・pass のみの stub・run_in_executor 委譲のみ
```"""

    # ── セクション: CALLCHAIN ────────────────────────────────────

    def _callchain(self) -> str:
        def find_chain(*keywords: str) -> str:
            matches = [
                c for c in self.project.chunks
                if any(kw in c.full_name for kw in keywords)
            ]
            matches.sort(key=lambda c: c.line_start)
            return "\n".join(
                f"  {c.full_name} [{c.chunk_id}, cc={c.cc}]"
                for c in matches[:8]
            )

        write_chain = find_chain("__setitem__", "batch_update", "kvs_set", "_write_to_db", "_serialize")
        query_chain = find_chain("query", "_validate_expression", "_sanitize_identifier", "execute", "_extract_column")
        crypto_chain = find_chain("_serialize", "_deserialize", "encrypt", "decrypt")
        file_chain   = find_chain("backup", "restore", "mkstemp", "rename", "copyfileobj")

        return f"""\
---

## [CALLCHAIN] — データフロー追跡

### フロー① KV書き込みパス

```
外部入力: key, value
  ↓
{write_chain}

【AIが推論すべき問い】
  Q1: hook.before_write が例外を投げた後、V2 staging の状態は？
  Q2: staging 中に close() されたら未 flushed データはどうなる？
  Q3: UniqueHook が index 更新後に DB 書き込みが失敗した場合の整合性は？
  Q4: DLQ エントリにはどの情報が含まれ、外部に見えるか？
```

### フロー② クエリ実行パス（SQLインジェクション系）

```
外部入力: table_name, where, order_by, group_by, columns
  ↓
{query_chain}

【AIが推論すべき問い】
  Q1: order_by / group_by はパラメータ化されているか？直接埋め込みか？
  Q2: @lru_cache された _sanitize_identifier はキャッシュ汚染可能か？
  Q3: override_allowed=True を外部から制御できるか？
  Q4: _extract_column_aliases での AS 句パースはインジェクション耐性があるか？
```

### フロー③ 暗号化パス

```
外部入力: value（書き込み）/ DB raw bytes（読み込み）
  ↓
{crypto_chain}

write: value → JSON 化 → encrypt(Fernet/AES-GCM/ChaCha20) → DB
read:  DB → decrypt → json.loads(★任意データ) → value

【AIが推論すべき問い】
  Q1: nonce = os.urandom(12) の一意性は大量書き込み時に十分か？
  Q2: 暗号化なし→あり移行時、混在データの _deserialize はどう動くか？
  Q3: DB が外部から書き換えられた場合、json.loads への影響は？
  Q4: 復号失敗時のエラーハンドリングは情報を漏洩しないか？
```

### フロー④ ファイル操作パス（backup / restore）

```
外部入力: dest_path（backup）/ src_path（restore）
  ↓
{file_chain}

backup:  stat → samefile → apsw.Connection(dest) → backup.step(-1)
restore: stat → close() → mkstemp → copyfileobj → rename → 再接続 → 子通知

【AIが推論すべき問い】
  Q1: src_path にパストラバーサル（../etc/passwd）は防げるか？
  Q2: restore 中に別スレッドが DB 操作した場合の影響は？
  Q3: restore で V2Engine の staging データが消えるのは意図した動作か？
  Q4: WeakSet で管理された child への通知が GC で消えた場合は？
  Q5: tempfile のパーミッションが元 DB より緩い場合の rename 前リスクは？
```"""

    # ── セクション: BLIND ────────────────────────────────────────

    def _blind(self) -> str:
        # BLIND に関連するチャンクを実際のデータから補完
        def find(name: str) -> str:
            c = self.project.chunk_map.get(name)
            return f"[{c.chunk_id}, cc={c.cc}]" if c else "[未検出]"

        ensure_cached = find("NanaSQLite._ensure_cached")
        kvs_chunk     = find("V2Engine._process_kvs_chunk")
        setitem       = find("NanaSQLite.__setitem__")
        unique_bw     = find("UniqueHook.before_write")
        sanitize      = find("NanaSQLite._sanitize_identifier")
        expire_cb     = find("NanaSQLite._delete_from_db_on_expire")
        evict         = find("ExpiringDict._evict")
        add_dlq       = find("V2Engine._add_to_dlq")
        get_dlq       = find("V2Engine.get_dlq")
        v2_init       = find("V2Engine.__init__")
        v2_shutdown   = find("V2Engine.shutdown")
        ns_close      = find("NanaSQLite.close")

        return f"""\
---

## [BLIND] — 静的解析が見落とす7領域

### B1: 状態機械の不整合（V2Engine × キャッシュ）
```
検証対象: {ensure_cached} × {kvs_chunk}

_ensure_cached は staging → DB の順に確認するが
flush 実行中にread が来た場合、staging から消えて DB にまだ書かれていない
「データが存在しない」ように見える瞬間が発生する可能性がある。
```

### B2: Hookチェーンの原子性
```
検証対象: {setitem} × {unique_bw}

hook1.before_write → 成功・副作用あり（UniqueHook が index を更新）
hook2.before_write → 例外発生
→ hook1 の副作用（_value_to_key dict 更新）はロールバックされない
  DB 書き込みは行われないが、メモリ上のインデックスが汚染される。
```

### B3: WeakrefによるGCハザード
```
AsyncNanaSQLite._child_instances = weakref.WeakSet()
UniqueHook._bound_db_ref = weakref.ref(db)

検証対象: UniqueHook.before_write での _bound_db_ref() が None を返す場合
          close() / _mark_parent_closed() の WeakSet 反復中の GC
```

### B4: lru_cache × セキュリティ境界
```
検証対象: {sanitize}

@lru_cache はプロセス全体で共有される。
複数の NanaSQLite インスタンスが同一プロセス内に存在する場合、
検証結果が異なるコンテキストに誤って再利用される可能性がある。
また、悪意ある identifier を先にキャッシュさせるキャッシュ毒入り攻撃。
```

### B5: スレッドとasyncioの混在
```
検証対象: {evict} × {expire_cb}

ExpiringDict._set_timer() は状況に応じて
  asyncio ループあり → loop.call_later()
  なし              → threading.Timer()

_evict() が on_expire → _delete_from_db_on_expire を呼ぶ際、
呼び出しスレッドと DB 操作スレッドが異なる場合の安全性を検証せよ。
```

### B6: DLQからの情報漏洩
```
検証対象: {add_dlq} → {get_dlq}

DLQ エントリに含まれる可能性のある情報:
  error_msg（例外メッセージ・スタックトレース含む可能性）
  table_name（内部テーブル名）
  key / value（失敗した書き込みデータ）
  action / timestamp

get_dlq() はこのリストをそのまま呼び出し元に返す。
アクセス制御が存在するか確認せよ。
```

### B7: atexit登録の競合とシャットダウン順序
```
検証対象: {v2_init} → {v2_shutdown} × {ns_close}

V2Engine.__init__ で atexit.register(self.shutdown) を登録。
複数インスタンスが存在する場合、シャットダウン順序は LIFO。
→ 子より先に親が shutdown され、子の V2Engine が孤立する可能性。
→ 既に close() 済みのインスタンスの atexit が後から走るリスク。
```"""

    # ── セクション: CHUNKS目次 ───────────────────────────────────

    def _chunks_toc(self) -> str:
        lines = [
            "---\n",
            "## [CHUNKS目次] — 全チャンク索引（必要時のみ参照）\n",
            "> TIER-1以外は原則スキップせよ。行番号で直接ジャンプせよ。\n",
        ]

        for tier_num in [1, 2, 3, 0]:
            label = f"{TIER_EMOJI[tier_num]} {TIER_LABEL[tier_num]}"
            chunks = sorted(
                [c for c in self.project.chunks if c.tier == tier_num],
                key=lambda c: (-c.cc, c.chunk_id),
            )
            if not chunks:
                continue
            lines.append(f"\n### {label}\n")
            lines.append("| ChunkID | 関数名 | 行範囲 | cc | ファイル |")
            lines.append("|:---:|:---|:---:|:---:|:---|")
            for c in chunks:
                dm = self._diff_mark(c.full_name)
                lines.append(
                    f"| {c.chunk_id} | `{c.full_name}{dm}` | "
                    f"L{c.line_start}-L{c.line_end} | {c.cc} | {c.file_path} |"
                )

        return "\n".join(lines)

    # ── セクション: CHUNKS本体 ───────────────────────────────────

    def _chunks_body(self) -> str:
        lines = ["---\n", "## [CHUNKS本体] — チャンク詳細（TIER-1→2→3→SKIP順）\n"]

        tiers = [1, 2, 3] if not self.tier1_only else [1]
        if not self.tier1_only:
            tiers.append(0)

        for tier_num in tiers:
            label = f"{TIER_EMOJI[tier_num]} {TIER_LABEL[tier_num]}"
            chunks = sorted(
                [c for c in self.project.chunks if c.tier == tier_num],
                key=lambda c: (-c.cc, c.chunk_id),
            )
            if not chunks:
                continue
            lines.append(f"\n### {label} チャンク群\n")
            for chunk in chunks:
                lines.append(self._render_chunk(chunk))

        return "\n".join(lines)

    def _render_chunk(self, chunk: ChunkInfo) -> str:
        taint_str = f"{'T' if chunk.taint_in else '.'}→{'T' if chunk.taint_out else '.'}"
        args_str  = ", ".join(chunk.args)
        sig       = f"{chunk.full_name}({args_str}) -> {chunk.return_annotation}"
        dm        = self._diff_mark(chunk.full_name)
        tier_em   = TIER_EMOJI[chunk.tier]
        mermaid   = make_mermaid(chunk, self.all_names)

        called_by_line = ""
        if chunk.called_by:
            cb = ", ".join(f"`{n}`" for n in chunk.called_by[:5])
            if len(chunk.called_by) > 5:
                cb += f" 他{len(chunk.called_by)-5}件"
            called_by_line = f"> 呼び出し元: {cb}\n"

        return (
            f"\n---\n\n"
            f"#### {chunk.chunk_id} {tier_em} `{chunk.full_name}`{dm}\n\n"
            f"> `{chunk.file_path}` L{chunk.line_start}-L{chunk.line_end} "
            f"| cc={chunk.cc} | taint={taint_str}\n"
            f"{called_by_line}"
            f"\n**シグネチャ**:\n"
            f"```\n{sig}  [cc={chunk.cc}] [{taint_str}]\n```\n\n"
            f"**呼び出しグラフ**:\n"
            f"```mermaid\n{mermaid}\n```\n"
        )

    # ── セクション: OUTPUT フォーマット ─────────────────────────

    def _output_format(self) -> str:
        return f"""\
---

## [OUTPUT] — 統合レポートの出力フォーマット

> AIはこのフォーマットで統合レポートを1本出力すること。

---

### 🔍 発見サマリーテーブル

| ID | 関数 | カテゴリ | 深刻度 | CWE | BLINDカテゴリ |
|:---|:---|:---|:---:|:---|:---:|
| F-001 | `xxx` | SQLインジェクション | 🔴 CRITICAL | CWE-89 | - |
| F-002 | `xxx` | TOCTOU | 🟠 HIGH | CWE-367 | B1 |

---

### 📋 発見詳細（上位5件）

#### FINDING-001

**関数**: `xxx` (ChunkID: Cxxx)
**深刻度**: CRITICAL / HIGH / MEDIUM / LOW
**カテゴリ**: SQLi / TOCTOU / 情報漏洩 / 暗号化不備 / 状態不整合
**CWE**: CWE-xxx

**攻撃シナリオ**:
```
Step 1: 攻撃者が xxx を呼び出す
Step 2: xxx が xxx の状態を利用して
Step 3: xxx が実行される
Step 4: 結果として xxx が達成される
```

**根本原因**:
```
問題のある呼び出し: xxx → xxx
ガード条件の欠落: xxx
```

**修正方針**:
```python
# 修正前（問題）
def xxx(self, input):
    self.execute(f"SELECT * FROM {{input}}")   # 直接埋め込み

# 修正後
def xxx(self, input):
    safe = self._sanitize_identifier(input)
    self.execute("SELECT * FROM ?", (safe,))
```

**副作用リスク**: xxx への影響、後方互換性 xxx

---

### 🕳️ BLINDカテゴリへのコメント

| カテゴリ | AIによる評価 | 深刻度 |
|:---|:---|:---:|
| B1: V2Engine×キャッシュ競合 | （推論結果） | ? |
| B2: Hookチェーンの原子性 | （推論結果） | ? |
| B3: WeakrefのGCハザード | （推論結果） | ? |
| B4: lru_cache汚染 | （推論結果） | ? |
| B5: Thread×asyncio混在 | （推論結果） | ? |
| B6: DLQ情報漏洩 | （推論結果） | ? |
| B7: atexit競合 | （推論結果） | ? |

---

### 📌 追加調査推奨箇所

```
AIが判断できなかった箇所（ソースコード確認が必要）:
  1. xxx → 理由: シグネチャのみでは判断不能
  2. xxx → 理由: 外部ライブラリの実装が不明
```

---
*Security Report v6 AI-Native | generated: {self.now}*"""

    # ── 統合生成 ─────────────────────────────────────────────────

    def generate(self) -> str:
        parts = [
            self._entry_point(),
            "",
            self._overview(),
            "",
            self._section_toc(),
            "",
            self._triage(),
            "",
            self._hotmap(),
            "",
            self._callchain(),
            "",
            self._blind(),
            "",
            self._chunks_toc(),
            "",
            self._chunks_body(),
            "",
            self._output_format(),
        ]
        return "\n".join(parts)


# ══════════════════════════════════════════════════════════════════
# エントリーポイント
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Security Report Generator v6 - AI-Native Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
使用例:
  # 初回実行
  python gen_report_v6.py ./src

  # スナップショット付き（次回 diff 用に保存）
  python gen_report_v6.py ./src --snapshot snap.json

  # diff モード（前回との変更箇所を★表示）
  python gen_report_v6.py ./src --diff snap.json --snapshot snap_new.json

  # TIER-1 チャンクのみ出力（高速・軽量）
  python gen_report_v6.py ./src --tier1-only

  # 出力ファイル名を指定
  python gen_report_v6.py ./src --output my_report.md
""",
    )
    parser.add_argument("target",      type=Path, help="解析対象ディレクトリ")
    parser.add_argument("--output",    type=Path, default=Path("security_report_v6.md"))
    parser.add_argument("--diff",      type=Path, default=None,
                        help="前回スナップショット JSON（差分モード）")
    parser.add_argument("--snapshot",  type=Path, default=None,
                        help="今回のスナップショットを保存するパス")
    parser.add_argument("--tier1-only", action="store_true",
                        help="CHUNKS本体に TIER-1 のみ出力（高速モード）")
    args = parser.parse_args()

    if not args.target.exists():
        print(f"❌  ディレクトリが存在しません: {args.target}", file=sys.stderr)
        sys.exit(1)

    # ─ 解析 ─────────────────────────────────────────────────────
    print(f"🔍  解析開始: {args.target}")
    project = ProjectAnalyzer(args.target).analyze()
    s = project.stats()
    print(
        f"    ✅  {s['files']}ファイル / {s['total']}チャンク  "
        f"TIER-1:{s['tier1']}  TIER-2:{s['tier2']}  "
        f"TIER-3:{s['tier3']}  SKIP:{s['skip']}"
    )

    # ─ diff ──────────────────────────────────────────────────────
    diff_info: Optional[dict] = None
    if args.diff and args.diff.exists():
        prev = json.loads(args.diff.read_text(encoding="utf-8"))
        engine = DiffEngine(prev)
        diff_info = engine.compute(project.chunks)
        d = diff_info
        print(
            f"    🔄  Diff: 追加 {len(d['added'])}  "
            f"変更 {len(d['changed'])}  削除 {len(d['removed'])}"
        )

    # ─ スナップショット保存 ──────────────────────────────────────
    if args.snapshot:
        DiffEngine.save(project.chunks, args.snapshot)
        print(f"    💾  スナップショット保存: {args.snapshot}")

    # ─ レポート生成 ──────────────────────────────────────────────
    print("📝  レポート生成中...")
    gen    = ReportGenerator(project, diff_info=diff_info, tier1_only=args.tier1_only)
    report = gen.generate()

    args.output.write_text(report, encoding="utf-8")
    print(f"✅  完了: {args.output}  ({len(report):,} 文字)")

    # ─ サマリー表示 ──────────────────────────────────────────────
    print("\n📊  TIER-1 優先関数（cc 降順）:")
    for c in sorted(project.get_by_tier(1), key=lambda c: -c.cc)[:8]:
        print(f"    {c.chunk_id}  cc={c.cc:2d}  {c.full_name}")
    if s["tier1"] > 8:
        print(f"    ... 他 {s['tier1'] - 8} 関数")


if __name__ == "__main__":
    main()