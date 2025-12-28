import apsw
import pytest

from nanasqlite import (
    NanaSQLite,
    NanaSQLiteClosedError,
    NanaSQLiteDatabaseError,
    NanaSQLiteError,
    NanaSQLiteValidationError,
)


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_security.db")


def test_sql_validation_strict_mode(db_path):
    db = NanaSQLite(db_path, strict_sql_validation=True)

    # Normal execution (COUNT is default allowed)
    db.query(columns=["COUNT(*)"])

    # Unauthorized function in strict mode
    with pytest.raises(NanaSQLiteValidationError) as excinfo:
        db.query(columns=["DANGEROUS_FUNC(*)"])
    assert "DANGEROUS_FUNC" in str(excinfo.value)
    db.close()


def test_sql_validation_warning_mode(db_path):
    db = NanaSQLite(db_path, strict_sql_validation=False)

    # NanaSQLite emits a warning during validation but allows the query to execute.
    # Execution will fail in SQLite because the function doesn't exist,
    # but we only care about the warning here.
    with pytest.warns(UserWarning, match="DANGEROUS_FUNC"):
        try:
            db.query(columns=["DANGEROUS_FUNC(*)"])
        except (apsw.Error, ValueError, NanaSQLiteError):
            # SQLite may fail because DANGEROUS_FUNC is not defined;
            # this test only asserts that a warning was emitted.
            pass

    # Test WHERE clause warning in non-strict mode (#3)
    with pytest.warns(UserWarning, match="Potentially dangerous SQL pattern"):
        try:
            db.query(where="1=1; DROP TABLE data")
        except (apsw.Error, ValueError, NanaSQLiteError):
            # SQLite might fail due to multiple statements or syntax,
            # but we check if NanaSQLite emitted a validation warning.
            pass
    db.close()


def test_allowed_sql_functions_init(db_path):
    """
    インスタンス初期化時にallowed_sql_functionsで許可した関数が
    バリデーションを通過することを検証。

    実行時にSQLiteで関数が未定義の場合、NanaSQLiteDatabaseErrorが
    発生することを確認（バリデーション成功の証明）。
    """
    db = NanaSQLite(db_path, strict_sql_validation=True, allowed_sql_functions=["MY_CUSTOM_FUNC"])

    # バリデーションは成功するはずだが、実行時にSQLiteで関数が未定義のため失敗
    # NanaSQLiteValidationErrorが発生しないことでバリデーション成功を確認
    with pytest.raises(NanaSQLiteDatabaseError) as excinfo:
        db.query(columns=["MY_CUSTOM_FUNC(*)"])

    # データベースエラーであり、"no such function"が含まれることを確認
    assert "no such function" in str(excinfo.value).lower()

    db.close()


def test_allowed_sql_functions_query(db_path):
    """
    クエリレベルでallowed_sql_functionsを指定した場合の動作を検証。
    """
    db = NanaSQLite(db_path, strict_sql_validation=True)

    # Should fail by default
    with pytest.raises(NanaSQLiteValidationError):
        db.query(columns=["LOCAL_FUNC(*)"])

    # クエリレベルの許可でバリデーション成功、実行時にデータベースエラー
    with pytest.raises(NanaSQLiteDatabaseError) as excinfo:
        db.query(columns=["LOCAL_FUNC(*)"], allowed_sql_functions=["LOCAL_FUNC"])

    assert "no such function" in str(excinfo.value).lower()
    db.close()


def test_forbidden_sql_functions(db_path):
    """
    forbidden_sql_functionsパラメータの動作を検証。
    """
    db = NanaSQLite(db_path, strict_sql_validation=True, allowed_sql_functions=["SOME_FUNC"])

    # SOME_FUNCは許可されているため、バリデーション成功、実行時エラー
    with pytest.raises(NanaSQLiteDatabaseError) as excinfo:
        db.query(columns=["SOME_FUNC(*)"])

    assert "no such function" in str(excinfo.value).lower()

    # クエリレベルでの明示的な禁止
    with pytest.raises(NanaSQLiteValidationError):
        db.query(columns=["SOME_FUNC(*)"], forbidden_sql_functions=["SOME_FUNC"])
    db.close()


def test_override_allowed(db_path):
    """
    override_allowedパラメータの動作を検証。
    """
    db = NanaSQLite(db_path, strict_sql_validation=True, allowed_sql_functions=["FUNC_A"])

    # FUNC_Aはグローバルに許可されている（バリデーション成功、実行時エラー）
    with pytest.raises(NanaSQLiteDatabaseError) as excinfo:
        db.query(columns=["FUNC_A(*)"])

    assert "no such function" in str(excinfo.value).lower()

    # override_allowed=Trueの場合、FUNC_Aはメソッド呼び出しで指定しない限り不許可
    with pytest.raises(NanaSQLiteValidationError):
        db.query(columns=["FUNC_A(*)"], allowed_sql_functions=["FUNC_B"], override_allowed=True)

    # FUNC_Bのみが許可される（バリデーション成功、実行時エラー）
    with pytest.raises(NanaSQLiteDatabaseError) as excinfo:
        db.query(columns=["FUNC_B(*)"], allowed_sql_functions=["FUNC_B"], override_allowed=True)

    assert "no such function" in str(excinfo.value).lower()
    db.close()


def test_redos_protection(db_path):
    db = NanaSQLite(db_path, max_clause_length=10, strict_sql_validation=True)

    # Ensure table and schema exists for execution test
    db["test"] = "data"

    # Normal length
    db.query(where="key = ?", parameters=("test",))

    # Too long
    with pytest.raises(NanaSQLiteValidationError) as excinfo:
        db.query(where="key = " + "?" * 20)
    assert "exceeds maximum length" in str(excinfo.value)
    db.close()


def test_connection_closed_error(tmp_path):
    db_path = str(tmp_path / "test_connection.db")
    db = NanaSQLite(db_path)
    child = db.table("slave")

    db.close()

    # Operations on closed connection
    with pytest.raises(NanaSQLiteClosedError):
        db["key"] = "value"

    # Operations on child of closed connection
    with pytest.raises(NanaSQLiteClosedError) as excinfo:
        child["key"] = "value"
    assert "Parent database connection is closed" in str(excinfo.value)
    assert "table: 'slave'" in str(excinfo.value)

    # Self closed
    db2_path = str(tmp_path / "test2.db")
    db2 = NanaSQLite(db2_path)
    db2.close()
    with pytest.raises(NanaSQLiteClosedError):
        db2["key"] = "val"
