import inspect
import re
import sys
from pathlib import Path

# Add src to path so we can import nanasqlite
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import nanasqlite  # noqa: F401  # imported for side effects / inspection

METHOD_GROUPS = {
    "Constructor": ["__init__"],
    "Core Methods": ["close", "table"],
    "Dictionary Interface": [
        "__getitem__", "__setitem__", "__delitem__", "__contains__", "__len__", "__iter__",
        "get", "setdefault", "pop", "update", "clear", "clear_cache", "keys", "values", "items", "to_dict", "copy"
    ],
    "Data Management": ["load_all", "refresh", "get_fresh", "batch_get", "batch_update", "batch_update_partial", "batch_delete", "is_cached", "flush"],
    "Transaction Control": ["begin_transaction", "commit", "rollback", "in_transaction", "transaction"],
    "SQL Wrapper": ["sql_insert", "sql_update", "sql_delete", "upsert"],
    "Query": ["query", "query_with_pagination", "count", "exists"],
    "Direct SQL": ["execute", "execute_many", "fetch_one", "fetch_all"],
    "Schema Management": ["create_table", "create_index", "alter_table_add_column", "drop_table", "drop_index", "list_tables", "list_indexes", "get_table_schema", "table_exists"],
    "Utils": ["vacuum", "get_db_size", "pragma", "get_last_insert_rowid"],
    "Backup & Restore": ["backup", "restore"],
    "Pydantic Support": ["set_model", "get_model"]
}

GROUP_HEADERS = {
    "Constructor": {"en": "Constructor", "ja": "コンストラクタ"},
    "Core Methods": {"en": "Core Methods", "ja": "コアメソッド"},
    "Dictionary Interface": {"en": "Dictionary Interface", "ja": "辞書インターフェース"},
    "Data Management": {"en": "Data Management", "ja": "データ管理"},
    "Transaction Control": {"en": "Transaction Control", "ja": "トランザクション制御"},
    "SQL Wrapper": {"en": "SQL Wrapper (CRUD)", "ja": "SQLラッパー (CRUD)"},
    "Query": {"en": "Query", "ja": "クエリ"},
    "Direct SQL": {"en": "Direct SQL Execution", "ja": "直接SQL実行"},
    "Schema Management": {"en": "Schema Management", "ja": "スキーマ管理"},
    "Utils": {"en": "Utility Functions", "ja": "ユーティリティ関数"},
    "Backup & Restore": {"en": "Backup & Restore", "ja": "バックアップ & リストア"},
    "Pydantic Support": {"en": "Pydantic Support", "ja": "Pydantic サポート"},
    "Other Methods": {"en": "Other Methods", "ja": "その他のメソッド"}
}

def extract_lang(text, lang='ja'):
    """
    Intelligently extracts the desired language while preserving structure and code.
    """
    if not text:
        return ""

    lines = text.split('\n')
    result_lines = []

    for line in lines:
        clean = line.strip()

        # Spacing
        if not clean:
            result_lines.append("")
            continue

        # Example blocks
        if clean.startswith('>>>') or clean.startswith('...'):
            result_lines.append(line)
            continue

        # Technical terms/inline code
        if '`' in line:
            result_lines.append(line)
            continue

        # We drop the parenthesis split logic because it breaks descriptions like "(default: x)"
        # Instead, we just rely on presence of Japanese characters to filter Japanese lines
        has_ja = bool(re.search(r'[ぁ-んァ-ヶー一-龠]', line))
        
        # Keep lines that start with argument patterns (we don't want to lose English args in Ja mode if they have no jap text, 
        # but wait, if it's an arg, keep it)
        is_arg = bool(re.match(r'^(\s*[-*]?\s*)([\w_]+:)', line))

        if lang == 'ja':
            if has_ja or is_arg or not clean:
                result_lines.append(line)
        else: # en mode
            # Ideally we only keep english, but if it has jap, we might drop it.
            if not has_ja or not clean:
                result_lines.append(line)

    return "\n".join(result_lines).strip()

def get_type_name(annotation):
    if annotation == inspect._empty:
        return "Any"
    if hasattr(annotation, "__name__"):
        return annotation.__name__
    return str(annotation).replace("typing.", "").replace("'", "")

def format_docstring(doc, lang='ja', sig=None):
    if not doc:
        return ""

    doc = inspect.cleandoc(doc)
    doc = extract_lang(doc, lang)

    # Initialize segments
    description_lines = []
    args_lines = []
    returns_lines = []
    raises_lines = []
    example_lines = []
    
    current_section = "description"
    
    # Simple state machine to parse the docstring
    for line in doc.split('\n'):
        clean = line.strip()
        
        # Detect section changes
        if re.match(r'^(Args|引数):', clean, re.I):
            current_section = "args"
            continue
        elif re.match(r'^(Returns|戻り値):', clean, re.I):
            current_section = "returns"
            continue
        elif re.match(r'^(Raises|例外):', clean, re.I):
            current_section = "raises"
            continue
        elif re.match(r'^(Example|Examples|使用例):', clean, re.I):
            current_section = "example"
            continue
            
        if current_section == "description":
            description_lines.append(line)
        elif current_section == "args":
            args_lines.append(line)
        elif current_section == "returns":
            returns_lines.append(line)
        elif current_section == "raises":
            raises_lines.append(line)
        elif current_section == "example":
            example_lines.append(line)

    # Build final markdown
    final_md = []
    
    # Description
    if description_lines:
        final_md.append("\n".join(description_lines).strip() + "\n")
        
    # Args Table
    if args_lines and sig:
        param_dict = dict(sig.parameters)
        th_name = "引数名" if lang == 'ja' else "Parameter"
        th_type = "型" if lang == 'ja' else "Type"
        th_desc = "説明" if lang == 'ja' else "Description"
        final_md.append(f"#### {th_name}\n")
        final_md.append(f"| {th_name} | {th_type} | {th_desc} |")
        final_md.append("|---|---|---|")
        
        for line in args_lines:
            m = re.match(r'^\s*([\w_]+):(.*)$', line.strip())
            if m:
                p_name, p_desc = m.groups()
                p_desc = p_desc.strip()
                p_type = "Any"
                if p_name in param_dict:
                    p_type = get_type_name(param_dict[p_name].annotation)
                # markdown escape
                p_type_text = f"`{p_type}`" if p_type != "Any" else ""
                final_md.append(f"| `{p_name}` | {p_type_text} | {p_desc} |")
            elif line.strip():
                # Continuation of description or unmatched line
                final_md.append(f"| | | {line.strip()} |")
        final_md.append("\n")

    # Returns section
    if returns_lines:
        val_name = "戻り値" if lang == 'ja' else "Returns"
        final_md.append(f"#### {val_name}")
        ret_type = "Any"
        if sig and sig.return_annotation != inspect._empty:
            ret_type = get_type_name(sig.return_annotation)
        
        if ret_type != "Any" and ret_type != "None":
            final_md.append(f"\n**Type:** `{ret_type}`\n")
        else:
            final_md.append("\n")
        final_md.append("\n".join(returns_lines).strip() + "\n")

    # Raises container (VitePress warning)
    if raises_lines:
        title = "例外" if lang == 'ja' else "Raises"
        final_md.append(f"::: warning {title}")
        # Make bulleted
        for r_line in raises_lines:
            if r_line.strip() and not r_line.strip().startswith("-"):
                final_md.append(f"- {r_line.strip()}")
            elif r_line.strip():
                final_md.append(r_line.strip())
        final_md.append(":::\n")
        
    # Example container (VitePress tip)
    if example_lines:
        title = "使用例" if lang == 'ja' else "Example"
        final_md.append(f"::: tip {title}")
        
        in_code_block = False
        has_code_fences = any("```" in l for l in example_lines)
        
        if not has_code_fences:
             final_md.append("```python")
             
        for e_line in example_lines:
            final_md.append(e_line)
            
        if not has_code_fences:
             final_md.append("```")
             
        final_md.append(":::\n")

    doc = "\n".join(final_md)
    doc = re.sub(r'\n{3,}', '\n\n', doc)

    return doc

def clean_signature(sig_str):
    """Clean the signature string from unnecessary quotes and verbose paths"""
    # Remove quotes around type hints like `: 'str'` -> `: str`
    s = re.sub(r": '([^']+)'", r": \1", sig_str)
    s = re.sub(r"-> '([^']+)'", r"-> \1", s)
    # Remove quotes around complex type hints like `"Literal['a']"` -> `Literal['a']`
    s = re.sub(r': "([^"]+)"', r': \1', s)
    
    s = s.replace("NoneType", "None")
    # Simplify common generic types
    s = re.sub(r'<CacheType\.[A-Z]+:\s*\'[a-z]+\'>', 'CacheType', s)
    return s

def format_docstring(doc, lang='ja', sig=None):
    if not doc:
        return ""

    doc = inspect.cleandoc(doc)
    doc = extract_lang(doc, lang)

    # Initialize segments
    description_lines = []
    args_lines = []
    returns_lines = []
    raises_lines = []
    example_lines = []
    
    current_section = "description"
    
    # Simple state machine to parse the docstring
    for line in doc.split('\n'):
        clean = line.strip()
        
        # Detect section changes
        if re.match(r'^(Args|引数):', clean, re.I):
            current_section = "args"
            continue
        elif re.match(r'^(Returns|戻り値):', clean, re.I):
            current_section = "returns"
            continue
        elif re.match(r'^(Raises|例外):', clean, re.I):
            current_section = "raises"
            continue
        elif re.match(r'^(Example|Examples|使用例):', clean, re.I):
            current_section = "example"
            continue
            
        if current_section == "description":
            description_lines.append(line)
        elif current_section == "args":
            args_lines.append(line)
        elif current_section == "returns":
            returns_lines.append(line)
        elif current_section == "raises":
            raises_lines.append(line)
        elif current_section == "example":
            example_lines.append(line)

    # Build final markdown
    final_md = []
    
    # Description
    if description_lines:
        final_md.append("\n".join(description_lines).strip() + "\n")
        
    # Args Table
    if args_lines and sig:
        param_dict = dict(sig.parameters)
        th_name = "引数名" if lang == 'ja' else "Parameter"
        th_type = "型" if lang == 'ja' else "Type"
        th_desc = "説明" if lang == 'ja' else "Description"
        final_md.append(f"#### {th_name}\n")
        final_md.append(f"| {th_name} | {th_type} | {th_desc} |")
        final_md.append("|---|---|---|")
        
        # Parse descriptions into a dict to deduplicate
        parsed_args = {}
        last_arg = None
        for line in args_lines:
            m = re.match(r'^\s*([\w_]+):(.*)$', line.strip())
            if m:
                p_name, p_desc = m.groups()
                parsed_args[p_name] = p_desc.strip()
                last_arg = p_name
            elif line.strip() and last_arg:
                parsed_args[last_arg] += " " + line.strip()
                
        # Iterate over signature parameters to retain order and include all args
        for p_name, p_param in param_dict.items():
            if p_name == 'self':
                continue
            
            p_desc = parsed_args.get(p_name, "")
            p_type = get_type_name(p_param.annotation)
            p_type_text = f"`{p_type}`" if p_type != "Any" else ""
            
            # If no description in docstring, we still list the argument if it has a type
            if p_desc or p_type_text:
                final_md.append(f"| `{p_name}` | {p_type_text} | {p_desc} |")
                
        final_md.append("\n")

    # Returns section
    if returns_lines:
        val_name = "戻り値" if lang == 'ja' else "Returns"
        final_md.append(f"#### {val_name}")
        ret_type = "Any"
        if sig and sig.return_annotation != inspect._empty:
            ret_type = get_type_name(sig.return_annotation)
        
        if ret_type != "Any" and ret_type != "None":
            final_md.append(f"\n**Type:** `{ret_type}`\n")
        else:
            final_md.append("\n")
        final_md.append("\n".join(returns_lines).strip() + "\n")

    # Raises container (VitePress warning)
    if raises_lines:
        title = "例外" if lang == 'ja' else "Raises"
        final_md.append(f"::: warning {title}")
        # Make bulleted
        for r_line in raises_lines:
            if r_line.strip() and not r_line.strip().startswith("-"):
                final_md.append(f"- {r_line.strip()}")
            elif r_line.strip():
                final_md.append(r_line.strip())
        final_md.append(":::\n")
        
    # Example container (VitePress tip)
    if example_lines:
        title = "使用例" if lang == 'ja' else "Example"
        final_md.append(f"::: tip {title}")
        
        has_code_fences = any("```" in l for l in example_lines)
        if not has_code_fences:
             final_md.append("```python")
             
        for e_line in example_lines:
            final_md.append(e_line)
            
        if not has_code_fences:
             final_md.append("```")
             
        final_md.append(":::\n")

    doc = "\n".join(final_md)
    doc = re.sub(r'\n{3,}', '\n\n', doc)

    return doc

def generate_class_md(cls_obj, title, description="", lang='ja'):
    md = f"# {title}\n\n"
    if description:
        md += f"{description}\n\n"
    
    # Class-level doc
    sig = inspect.signature(cls_obj.__init__)
    # remove `self` from sig if present
    params = list(sig.parameters.values())
    if params and params[0].name == 'self':
        sig = sig.replace(parameters=params[1:])
        
    md += f"## {cls_obj.__name__}\n\n"
    md += f"```python\nclass {cls_obj.__name__}{clean_signature(str(sig))}\n```\n\n"
    
    # Merge class docstring and __init__ docstring
    full_doc = (cls_obj.__doc__ or "") + "\n\n" + (cls_obj.__init__.__doc__ or "")
    md += format_docstring(full_doc, lang, sig) + "\n\n"
    md += "---\n\n"

    members = inspect.getmembers(cls_obj, predicate=lambda x: inspect.isfunction(x) or inspect.ismethod(x))
    
    def get_lnum(obj):
        try:
            return inspect.getsourcelines(obj)[1]
        except Exception:
            return 9999
    members.sort(key=lambda x: get_lnum(x[1]))

    # Group methods
    categorized = {k: [] for k in METHOD_GROUPS.keys()}
    categorized["Other Methods"] = []
    
    for name, method in members:
        if name.startswith("_") and name not in ["__init__", "__getitem__", "__setitem__", "__delitem__", "__contains__", "__len__", "__iter__"]:
            continue
            
        found_group = "Other Methods"
        for group, methods in METHOD_GROUPS.items():
            if name in methods:
                found_group = group
                break
                
        categorized[found_group].append((name, method))

    # Output groups
    for group, methods_in_group in categorized.items():
        if not methods_in_group:
            continue
            
        group_title = GROUP_HEADERS[group][lang]
        md += f"## {group_title}\n\n"
        
        for name, method in methods_in_group:
            if name == "__init__":
                continue # Skip init as we show it at class level
                
            sig = inspect.signature(method)
            # Remove self
            params = list(sig.parameters.values())
            if params and params[0].name == 'self':
                sig = sig.replace(parameters=params[1:])
                
            md += f"### `{name}`\n\n"
            md += f"```python\ndef {name}{clean_signature(str(sig))}\n```\n\n"
            doc = format_docstring(method.__doc__, lang, sig)
            if doc:
                md += doc + "\n\n"
            md += "---\n\n"

    return md

def main():
    root_dir = Path(__file__).parent.parent / "docs" / "site"
    ja_dir, en_dir = root_dir, root_dir / "en"
    for d in [ja_dir, en_dir]:
        d.mkdir(parents=True, exist_ok=True)
    from nanasqlite.async_core import AsyncNanaSQLite
    from nanasqlite.core import NanaSQLite

    (ja_dir / "api_sync.md").write_text(generate_class_md(NanaSQLite, "同期 API リファレンス", "NanaSQLiteクラスの同期メソッド一覧です。", 'ja'), encoding="utf-8")
    (ja_dir / "api_async.md").write_text(generate_class_md(AsyncNanaSQLite, "非同期 API リファレンス", "AsyncNanaSQLiteクラスの非同期メソッド一覧です。", 'ja'), encoding="utf-8")
    (en_dir / "api_sync.md").write_text(generate_class_md(NanaSQLite, "Synchronous API Reference", "Reference for the synchronous NanaSQLite class.", 'en'), encoding="utf-8")
    (en_dir / "api_async.md").write_text(generate_class_md(AsyncNanaSQLite, "Asynchronous API Reference", "Reference for the asynchronous AsyncNanaSQLite class.", 'en'), encoding="utf-8")
    print("API docs regenerated with modern styling.")

if __name__ == "__main__":
    main()
