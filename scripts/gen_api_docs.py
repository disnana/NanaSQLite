import inspect
import re
import sys
from pathlib import Path

# Add src to path so we can import nanasqlite
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import nanasqlite  # noqa: F401  # imported for side effects / inspection


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

        # Parameter definitions
        # Pattern match: "parameter: description"
        param_match = re.match(r'^(\s*[-*]?\s*)([\w_]+:)(.*)$', line)
        if param_match:
            indent, key, desc = param_match.groups()

            # Bilingual desc
            desc_match = re.search(r'^(.*?)\((.*?)\)$', desc.strip())
            if desc_match:
                en, ja = desc_match.groups()
                # Store cleaned version, we'll bulletize it later
                result_lines.append(f"{key} {ja.strip() if lang == 'ja' else en.strip()}")
            else:
                result_lines.append(f"{key} {desc.strip()}")
            continue

        # Technical terms/inline code
        if '`' in line:
            result_lines.append(line)
            continue

        # Narrative
        match = re.search(r'^(.*?)\((.*?)\)$', clean)
        if match:
            en, ja = match.groups()
            processed = line.replace(clean, ja.strip() if lang == 'ja' else en.strip())
            result_lines.append(processed)
            continue

        has_ja = bool(re.search(r'[ぁ-んァ-ヶー一-龠]', line))
        if lang == 'ja':
            if has_ja or not clean:
                result_lines.append(line)
        else: # en mode
            if not has_ja or not clean:
                result_lines.append(line)

    return "\n".join(result_lines).strip()

def format_docstring(doc, lang='ja'):
    if not doc:
        return ""

    doc = inspect.cleandoc(doc)
    doc = extract_lang(doc, lang)

    # Headers
    if lang == 'ja':
        labels = {'args': '📥 引数', 'returns': '📤 戻り値', 'raises': '⚠️ 例外', 'example': '💡 使用例'}
    else:
        labels = {'args': '📥 Arguments', 'returns': '📤 Returns', 'raises': '⚠️ Raises', 'example': '💡 Example'}

    # Use single newlines for headers followed by lists for compact look,
    # but ensure no leading spaces on bullets.
    doc = re.sub(r'^(Args|引数):', f'#### {labels["args"]}', doc, flags=re.M | re.I)
    doc = re.sub(r'^(Returns|戻り値):', f'#### {labels["returns"]}', doc, flags=re.M | re.I)
    doc = re.sub(r'^(Raises|例外):', f'#### {labels["raises"]}', doc, flags=re.M | re.I)
    doc = re.sub(r'^(Example|使用例):', f'#### {labels["example"]}', doc, flags=re.M | re.I)

    # Bulletize parameters: Remove leading whitespace completely
    # Match "name: description" NOT preceded by backticks or within code
    def make_bullet(m):
        key, desc = m.groups()
        # Remove colon from key if present
        clean_key = key.rstrip(':')
        return f"- **{clean_key}**: {desc.strip()}"

    # Only match at start of line (after clean_doc and extract_lang, indents are minimized)
    doc = re.sub(r'^([\w_]+:)(.*)$', make_bullet, doc, flags=re.M)

    # Code block wrapping
    final_lines = []
    current_block = []
    for line in doc.split('\n'):
        if line.strip().startswith('>>>') or line.strip().startswith('...'):
            if not current_block:
                final_lines.append("```python")
            current_block.append(line)
            final_lines.append(line)
        else:
            if current_block:
                final_lines.append("```")
                current_block = []
            final_lines.append(line)
    if current_block:
        final_lines.append("```")

    doc = "\n".join(final_lines)

    # Final cleanup: ensure spacing between elements
    doc = re.sub(r'(#### .*)\n([^-])', r'\1\n\n\2', doc) # Header vs text
    doc = re.sub(r'\n{3,}', '\n\n', doc)

    return doc

def generate_class_md(cls_obj, title, description="", lang='ja'):
    md = f"# {title}\n\n"
    if description:
        md += f"{description}\n\n"
    md += f"## {cls_obj.__name__}\n\n"
    md += format_docstring(cls_obj.__doc__, lang) + "\n\n"
    md += "---\n\n"
    md += "## Methods\n\n" if lang == 'en' else "## メソッド\n\n"

    members = inspect.getmembers(cls_obj, predicate=lambda x: inspect.isfunction(x) or inspect.ismethod(x))
    def get_lnum(obj):
        try:
            return inspect.getsourcelines(obj)[1]
        except Exception:
            return 9999
    members.sort(key=lambda x: get_lnum(x[1]))

    for name, method in members:
        if name.startswith("_") and name != "__init__":
            continue
        sig = inspect.signature(method)
        md += f"### {name}\n\n"
        md += f"```python\n{name}{str(sig).replace('NoneType', 'None')}\n```\n\n"
        doc = format_docstring(method.__doc__, lang)
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
    print("API docs regenerated with zero-indent bullet points.")

if __name__ == "__main__":
    main()
