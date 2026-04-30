"""
SQL utility functions for NanaSQLite.

This module provides utility functions for SQL string processing,
particularly for sanitizing SQL expressions to prevent injection attacks
and handle edge cases in SQL parsing.
"""

from __future__ import annotations

from typing import Any

# Rust拡張モジュールがあればインポートを試みる
# 型アノテーションを付けておくことで mypy がモジュールの属性参照を
# 許容するようにします。
nanalib: Any
try:
    import nanalib  # type: ignore
except ImportError:
    nanalib = None


def sanitize_sql_for_function_scan(sql: str) -> str:
    """
    Return a sanitized version of the SQL string for function-call scanning.

    The sanitizer uses a character-by-character state machine with the
    following rules:

    - **Single-quoted string literals** (``'...'``): content replaced with
      spaces so that function-like patterns inside string values are not
      matched by the validation regex.
    - **Double-quoted identifiers** (``"identifier"``): content is
      **preserved as-is** so that quoted function names such as
      ``"LOAD_EXTENSION"(...)`` can still be detected by the validation
      regex.  Only the surrounding quote characters themselves are replaced
      with spaces.
    - **Line comments** (``-- ...``): replaced with spaces up to the
      newline, which is preserved.
    - **Block comments** (``/* ... */``): replaced with spaces.
    - **Outside any of the above**: characters are passed through unchanged.

    Args:
        sql: The SQL string to sanitize.

    Returns:
        A sanitized version of the SQL string that preserves the original
        length and newline positions.  Single-quoted literal content and
        comment content are blanked out; double-quoted identifier content
        is kept intact for pattern matching.

    Example:
        >>> sanitize_sql_for_function_scan("SELECT 'COUNT(*)' FROM table")
        'SELECT           FROM table'
        >>> sanitize_sql_for_function_scan('SELECT "LOAD_EXTENSION"(x)')
        'SELECT  LOAD_EXTENSION (x)'
        >>> sanitize_sql_for_function_scan("SELECT COUNT(*) -- comment")
        'SELECT COUNT(*)            '

    Note:
        SQL escaping rules applied:
        - Single quotes escaped as ``''`` (both chars blanked)
        - Double quotes escaped as ``""`` (both chars blanked, identifier
          content still visible on either side)
        - Line comments end at the first newline
        - Block comments may span multiple lines
    """
    if not sql:
        return sql

    result = []
    i = 0
    length = len(sql)
    in_single = False
    in_double = False
    in_line_comment = False
    in_block_comment = False

    while i < length:
        ch = sql[i]

        # Inside line comment
        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
                result.append(ch)
            else:
                result.append(" ")
            i += 1
            continue

        # Inside block comment
        if in_block_comment:
            if ch == "*" and i + 1 < length and sql[i + 1] == "/":
                in_block_comment = False
                result.append("  ")  # Replace */
                i += 2
            else:
                result.append(" ")
                i += 1
            continue

        # Inside single-quoted string literal
        if in_single:
            if ch == "'" and i + 1 < length and sql[i + 1] == "'":
                # Escaped single quote (SQL standard: '')
                result.append("  ")
                i += 2
            elif ch == "'":
                in_single = False
                result.append(" ")
                i += 1
            else:
                result.append(" ")
                i += 1
            continue

        # Inside double-quoted identifier - preserve content for function detection
        # In SQL, double-quoted strings are identifiers (not string literals),
        # so we keep the content visible for function-call pattern matching.
        if in_double:
            if ch == '"' and i + 1 < length and sql[i + 1] == '"':
                # Escaped double quote ("") → replace both chars with spaces
                result.append("  ")
                i += 2
            elif ch == '"':
                in_double = False
                # Replace closing quote with space (strip quote, keep position)
                result.append(" ")
                i += 1
            else:
                # Preserve the identifier character as-is for regex matching
                result.append(ch)
                i += 1
            continue

        # Outside literals/comments - check for delimiters

        # Line comment start
        if ch == "-" and i + 1 < length and sql[i + 1] == "-":
            in_line_comment = True
            result.append("  ")
            i += 2
            continue

        # Block comment start
        if ch == "/" and i + 1 < length and sql[i + 1] == "*":
            in_block_comment = True
            result.append("  ")
            i += 2
            continue

        # Single-quoted string start
        if ch == "'":
            in_single = True
            result.append(" ")
            i += 1
            continue

        # Double-quoted identifier start
        if ch == '"':
            in_double = True
            result.append(" ")
            i += 1
            continue

        # Normal code - preserve as-is
        result.append(ch)
        i += 1

    return "".join(result)


# PERF-05 fix: Pre-compute the safe character set as a module-level constant (frozenset)
# rather than re-creating a new set() on every call.  fast_validate_sql_chars() is invoked
# on every _validate_expression() call (hot path), so avoiding the per-call set construction
# saves ~200-300 ns per invocation.
_SAFE_SQL_CHARS: frozenset[str] = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ ,.()'=<>!+-*/\"|?:@$`[]"
)



def fast_validate_sql_chars(expr: str) -> bool:
    """
    Validate that a SQL expression contains only safe characters.
    This is a ReDoS-resistant alternative to complex regex for basic validation.

    Safe characters include:
    - Alphanumeric characters
    - Underscore (_)
    - Space ( )
    - Comma (,) -- for ORDER BY/GROUP BY
    - Dot (.) -- for table.column
    - Parentheses (()) -- for function calls
    - Operators: =, <, >, !, +, -, *, /
    - Quotes: ', " (handled carefully by other layers)
    - Backticks: `
    - Brackets: [ ]

    Args:
        expr: The SQL expression to validate

    Returns:
        True if all characters are within the safe set, False otherwise.
    """
    if not expr:
        return True

    return all(c in _SAFE_SQL_CHARS for c in expr)


def sanitize_identifier(identifier: str) -> str:
    """
    Sanitize a SQL identifier (table name or column name) by wrapping it in
    double quotes and escaping internal double quotes.

    Args:
        identifier: The identifier to sanitize.

    Returns:
        The sanitized identifier wrapped in double quotes.
    """
    if not identifier:
        return identifier
    sanitized = identifier.replace('"', '""')
    return f'"{sanitized}"'
