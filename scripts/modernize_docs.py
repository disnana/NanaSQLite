import re
import sys
from pathlib import Path

def wrap_callout(match, c_type):
    full_indent = match.group(1)
    title = match.group(2)
    content = match.group(3)

    # Determine base indent (spaces corresponding to the bullet)
    base_indent = re.sub(r'[-*]\s', '  ', full_indent)

    # Clean up content: strip leading/trailing whitespace
    content = content.strip()

    # Split content and prefix with base_indent if needed
    lines = content.split('\n')
    processed_lines = []
    for i, line in enumerate(lines):
        if not line.strip():
            processed_lines.append("")
        else:
            if i == 0:
                # First line is appended directly after the tag in VitePress usually, 
                # but we put it on a new line for consistency.
                processed_lines.append(base_indent + line.lstrip())
            else:
                # For subsequent lines, only add indent if they aren't already indented properly
                if not line.startswith(base_indent):
                    processed_lines.append(base_indent + line.lstrip())
                else:
                    processed_lines.append(line)

    inner_content = "\n".join(processed_lines)

    # Build the final block
    # VitePress syntax: 
    # ::: warning 注意
    # ...
    # :::
    
    # If the prefix was a list item, we put the ::: right after the list bullet
    opening = f"{full_indent}::: {c_type} {title}"
    closing = f"{base_indent}:::"

    return f"{opening}\n{inner_content}\n{closing}"

def process_file(filepath):
    content = filepath.read_text(encoding="utf-8")
    
    patterns = [
        (re.compile(r'^([ \t]*(?:[-*]\s+)?)\*\*(注意|警告|Note|Warning):?\*\*\s*(.*?)(?=\n[ \t]*\n|\n[ \t]*[-*]|\Z)', re.DOTALL | re.MULTILINE), 'warning'),
        (re.compile(r'^([ \t]*(?:[-*]\s+)?)\*\*(ヒント|Tip):?\*\*\s*(.*?)(?=\n[ \t]*\n|\n[ \t]*[-*]|\Z)', re.DOTALL | re.MULTILINE), 'tip'),
        (re.compile(r'^([ \t]*(?:[-*]\s+)?)\*\*(重要(?:なポイント)?|Important):?\*\*\s*(.*?)(?=\n[ \t]*\n|\n[ \t]*[-*]|\Z)', re.DOTALL | re.MULTILINE), 'danger')
    ]
    
    new_content = content
    for pattern, c_type in patterns:
        # We need to pass the c_type into the replacer. Since re.sub only takes a match object, we use a lambda.
        new_content = pattern.sub(lambda m, t=c_type: wrap_callout(m, t), new_content)
        
    if new_content != content:
        filepath.write_text(new_content, encoding="utf-8")
        return True
    return False

def main():
    docs_dir = Path(__file__).parent.parent / "docs" / "site"
    changed = 0
    for file in docs_dir.glob("**/*.md"):
        # explicitly exclude generated ones to avoid double processing if not careful, 
        # though our script only targets `**Note:**` which isn't generated anymore.
        if file.name in ["api_sync.md", "api_async.md"]:
            continue
            
        if process_file(file):
            print(f"Updated {file.relative_to(docs_dir)}")
            changed += 1
            
    print(f"Total files updated: {changed}")

if __name__ == "__main__":
    main()
