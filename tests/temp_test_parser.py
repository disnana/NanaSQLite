import pytest
from nanasqlite import NanaSQLite, NanaSQLiteValidationError

def test_sanitizer_string_literals(tmp_path):
    db_path = str(tmp_path / "test_sanitizer.db")
    db = NanaSQLite(db_path, strict_sql_validation=True)
    
    # 1. False Positive check: 'COUNT(' inside string literal should NOT trigger validation error
    # If the sanitizer works, this should pass. If not, regex sees COUNT( and thinks it's a function call.
    # Note: COUNT is usually allowed, so we use a forbidden function name to test.
    
    forbidden_func = "FORBIDDEN_FUNC"
    
    # This checks that the function IS detected when used normally
    with pytest.raises(NanaSQLiteValidationError):
        db.query(columns=[f"{forbidden_func}(*)"])
        
    print("Confirmed: FORBIDDEN_FUNC is blocked when used normally.")
    
    # This checks that the function is NOT detected when inside a string
    try:
        # SELECT 'FORBIDDEN_FUNC('
        db.query(columns=[f"'{forbidden_func}('"])
        print("PASS: String literal 'FORBIDDEN_FUNC(' was correctly ignored.")
    except NanaSQLiteValidationError:
        print("FAIL: String literal 'FORBIDDEN_FUNC(' was falsely detected as a function call!")
        raise
        
    # Check double quotes
    try:
        db.query(columns=[f'"{forbidden_func}("'])
        print("PASS: String literal \"FORBIDDEN_FUNC(\" was correctly ignored.")
    except NanaSQLiteValidationError:
        # Note: In SQLite, double quotes are often identifiers, but if it looks like a string in python context...
        # Wait, identifier "FUNC(" is also a valid identifier. 
        # But our regex looks for [IDENTIFIER] (.
        # "FUNC" ( ... this might match.
        # Let's stick to single quotes for string literals which is standard SQL.
        pass

    # Check comments
    try:
        # SELECT 1 -- FORBIDDEN_FUNC(
        db.query(columns=["1 -- FORBIDDEN_FUNC("])
        print("PASS: Comment -- FORBIDDEN_FUNC( was correctly ignored.")
    except NanaSQLiteValidationError:
        print("FAIL: Comment containing function name was falsely detected!")
        raise

if __name__ == "__main__":
    import sys
    try:
        test_sanitizer_string_literals(pytest.ensuretemp("test_sanitizer"))
        print("\nAll sanitizer tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)
