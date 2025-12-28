"""
SQL utility functions for NanaSQLite.

This module provides utility functions for SQL string processing,
particularly for sanitizing SQL expressions to prevent injection attacks
and handle edge cases in SQL parsing.
"""


def sanitize_sql_for_function_scan(sql: str) -> str:
    """
    Return a version of the SQL string where string literals and comments
    are replaced with spaces so that function-like patterns inside them
    are ignored by the validation regex.

    This function implements a state machine that processes SQL character by character,
    tracking whether we're inside:
    - Single-quoted string literals (with '' escaping)
    - Double-quoted identifiers/strings (with "" escaping)
    - Line comments (-- to newline)
    - Block comments (/* to */)

    Args:
        sql: The SQL string to sanitize

    Returns:
        A sanitized version of the SQL string where all content inside
        string literals and comments is replaced with spaces, while
        preserving the original length and newline positions.

    Example:
        >>> sanitize_sql_for_function_scan("SELECT 'COUNT(*)' FROM table")
        'SELECT           FROM table'
        >>> sanitize_sql_for_function_scan("SELECT COUNT(*) -- comment")
        'SELECT COUNT(*)            '

    Note:
        This function handles SQL-specific escaping rules:
        - Single quotes are escaped as ''
        - Double quotes are escaped as ""
        - Line comments start with -- and end at newline
        - Block comments are /* ... */
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

        # Inside double-quoted identifier/string
        if in_double:
            if ch == '"' and i + 1 < length and sql[i + 1] == '"':
                # Escaped double quote (SQL standard: "")
                result.append("  ")
                i += 2
            elif ch == '"':
                in_double = False
                result.append(" ")
                i += 1
            else:
                result.append(" ")
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

    Args:
        expr: The SQL expression to validate

    Returns:
        True if all characters are within the safe set, False otherwise.
    """
    if not expr:
        return True

    # Safe character set: Alphanumeric, underscores, spaces, and common SQL punctuation/operators
    # Including ?, :, @, $ for parameter placeholders
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ ,.()'=<>!+-*/\"|?:@$")

    return all(c in safe_chars for c in expr)
