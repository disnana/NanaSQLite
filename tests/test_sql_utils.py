"""
Unit tests for SQL utility functions.

This module contains comprehensive tests for the sql_utils module,
particularly focusing on the sanitize_sql_for_function_scan function.
"""

from nanasqlite.sql_utils import sanitize_sql_for_function_scan


class TestSanitizeSqlForFunctionScan:
    """Test suite for the sanitize_sql_for_function_scan function."""

    def test_empty_string(self):
        """Test with empty input."""
        assert sanitize_sql_for_function_scan("") == ""

    def test_simple_sql_no_literals(self):
        """Test simple SQL without string literals or comments."""
        sql = "SELECT COUNT(*) FROM users"
        result = sanitize_sql_for_function_scan(sql)
        assert result == sql
        assert "COUNT" in result

    def test_single_quoted_string(self):
        """Test single-quoted string literals are replaced with spaces."""
        sql = "SELECT 'COUNT(*)' FROM table"
        result = sanitize_sql_for_function_scan(sql)
        assert "COUNT" not in result
        assert result == "SELECT            FROM table"
        assert len(result) == len(sql)

    def test_double_quoted_identifier(self):
        """Test double-quoted identifiers are replaced with spaces."""
        sql = 'SELECT "user_id" FROM table'
        result = sanitize_sql_for_function_scan(sql)
        assert result == "SELECT           FROM table"
        assert len(result) == len(sql)

    def test_escaped_single_quotes(self):
        """Test SQL-style escaped single quotes ('')."""
        sql = "SELECT 'John''s data' FROM users"
        result = sanitize_sql_for_function_scan(sql)
        # The entire string including escaped quote should be spaces
        assert "'s data'" not in result
        assert result == "SELECT                FROM users"
        assert len(result) == len(sql)

    def test_escaped_double_quotes(self):
        """Test SQL-style escaped double quotes ("")."""
        sql = 'SELECT "column""name" FROM table'
        result = sanitize_sql_for_function_scan(sql)
        assert result == "SELECT                FROM table"
        assert len(result) == len(sql)

    def test_line_comment(self):
        """Test line comments (--) are replaced with spaces."""
        sql = "SELECT COUNT(*) -- this is a comment\nFROM table"
        result = sanitize_sql_for_function_scan(sql)
        assert "comment" not in result
        assert "COUNT" in result
        assert "\n" in result  # Newlines are preserved
        assert result == "SELECT COUNT(*)                     \nFROM table"

    def test_block_comment(self):
        """Test block comments (/* */) are replaced with spaces."""
        sql = "SELECT COUNT(*) /* comment */ FROM table"
        result = sanitize_sql_for_function_scan(sql)
        assert "comment" not in result
        assert "COUNT" in result
        assert result == "SELECT COUNT(*)               FROM table"
        assert len(result) == len(sql)

    def test_multiline_block_comment(self):
        """Test multiline block comments."""
        sql = "SELECT COUNT(*) /* line1\nline2 */ FROM table"
        result = sanitize_sql_for_function_scan(sql)
        assert "line1" not in result
        assert "line2" not in result
        assert "COUNT" in result
        # Note: newlines inside block comments are also replaced with spaces
        assert len(result) == len(sql)

    def test_nested_quotes_in_string(self):
        """Test double quotes inside single-quoted string."""
        sql = """SELECT 'he said "hello"' FROM table"""
        result = sanitize_sql_for_function_scan(sql)
        assert '"hello"' not in result
        assert result == "SELECT                   FROM table"

    def test_function_call_in_string(self):
        """Test that function calls inside strings are sanitized."""
        sql = "SELECT 'LOAD_EXTENSION(evil)' FROM table"
        result = sanitize_sql_for_function_scan(sql)
        assert "LOAD_EXTENSION" not in result
        assert "evil" not in result

    def test_function_call_in_comment(self):
        """Test that function calls inside comments are sanitized."""
        sql = "SELECT id -- LOAD_EXTENSION(evil)\nFROM table"
        result = sanitize_sql_for_function_scan(sql)
        assert "LOAD_EXTENSION" not in result
        assert "evil" not in result
        assert "SELECT id" in result

    def test_complex_sql_with_all_elements(self):
        """Test complex SQL with strings, comments, and regular code."""
        sql = """
        SELECT
            COUNT(*) as cnt,
            'value''s test' as str1,
            "col""name" as str2,
            -- line comment with EVIL()
            SUM(amount) /* block comment MALICIOUS() */
        FROM table
        WHERE name = 'O''Reilly'
        """
        result = sanitize_sql_for_function_scan(sql)

        # Check that actual function calls are preserved
        assert "COUNT" in result
        assert "SUM" in result

        # Check that content in strings is removed
        assert "value''s test" not in result
        assert "O''Reilly" not in result

        # Check that content in comments is removed
        assert "EVIL" not in result
        assert "MALICIOUS" not in result

        # Length should be preserved
        assert len(result) == len(sql)

    def test_edge_case_quote_at_end(self):
        """Test single quote at the end of string."""
        sql = "SELECT * FROM table WHERE name = 'test'"
        result = sanitize_sql_for_function_scan(sql)
        assert "test" not in result
        assert "SELECT * FROM table WHERE name =       " == result

    def test_edge_case_unclosed_quote(self):
        """Test behavior with unclosed quote (malformed SQL)."""
        sql = "SELECT 'unclosed FROM table"
        result = sanitize_sql_for_function_scan(sql)
        # Everything after the opening quote should be spaces
        assert result == "SELECT                     "

    def test_edge_case_unclosed_block_comment(self):
        """Test behavior with unclosed block comment."""
        sql = "SELECT COUNT(*) /* unclosed comment"
        result = sanitize_sql_for_function_scan(sql)
        assert "COUNT" in result
        assert "unclosed comment" not in result

    def test_consecutive_comments(self):
        """Test multiple consecutive comments."""
        sql = "SELECT id -- comment1\n-- comment2\nFROM table"
        result = sanitize_sql_for_function_scan(sql)
        assert "comment1" not in result
        assert "comment2" not in result
        assert "SELECT id" in result

    def test_empty_string_literals(self):
        """Test empty string literals."""
        sql = "SELECT '' as empty, \"\" as empty2"
        result = sanitize_sql_for_function_scan(sql)
        assert result == "SELECT    as empty,    as empty2"

    def test_only_whitespace_preserved(self):
        """Test that whitespace outside strings is preserved."""
        sql = "SELECT    COUNT(*)    FROM    table"
        result = sanitize_sql_for_function_scan(sql)
        assert result == sql

    def test_special_characters_outside_strings(self):
        """Test special characters in SQL code are preserved."""
        sql = "SELECT id, name, (age + 10) * 2 FROM users"
        result = sanitize_sql_for_function_scan(sql)
        assert result == sql
        assert "+" in result
        assert "*" in result
        assert "(" in result

    def test_dash_not_comment(self):
        """Test single dash doesn't trigger comment."""
        sql = "SELECT age-10 FROM users"
        result = sanitize_sql_for_function_scan(sql)
        assert result == sql
        assert "-" in result

    def test_slash_not_comment(self):
        """Test single slash doesn't trigger comment."""
        sql = "SELECT price/quantity FROM items"
        result = sanitize_sql_for_function_scan(sql)
        assert result == sql
        assert "/" in result

    def test_asterisk_not_comment_end(self):
        """Test asterisk not at block comment end."""
        sql = "SELECT COUNT(*) FROM users"
        result = sanitize_sql_for_function_scan(sql)
        assert result == sql
        assert "*" in result

    def test_preserves_case(self):
        """Test that case is preserved in non-sanitized portions."""
        sql = "SeLeCt CoUnT(*) FrOm TaBlE"
        result = sanitize_sql_for_function_scan(sql)
        assert result == sql

    def test_unicode_characters(self):
        """Test handling of unicode characters in strings."""
        sql = "SELECT '日本語テスト' FROM table"
        result = sanitize_sql_for_function_scan(sql)
        assert "日本語" not in result
        assert "テスト" not in result
        # Should still preserve length
        assert len(result) == len(sql)

    def test_real_world_injection_attempt(self):
        """Test realistic SQL injection attempt is properly sanitized."""
        # This tests that malicious code in strings doesn't get detected
        sql = "SELECT name FROM users WHERE id = 'x'' OR ''1''=''1' -- '"
        result = sanitize_sql_for_function_scan(sql)
        # The OR condition should be sanitized out
        assert "OR" not in result
        assert result == "SELECT name FROM users WHERE id =                        "

    def test_backslash_not_escape(self):
        """Test that backslashes are NOT treated as escape characters (SQL standard)."""
        # In standard SQL, backslash is NOT an escape character
        # Only '' escapes a quote
        sql = r"SELECT 'test\' FROM table"
        result = sanitize_sql_for_function_scan(sql)
        # Everything after the opening quote should be sanitized until closing quote
        # The \' doesn't close the string in SQL standard
        assert "test" not in result
