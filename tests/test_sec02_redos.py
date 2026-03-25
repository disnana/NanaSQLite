import pytest
import time
from nanasqlite.core import NanaSQLite

def test_sec02_redos_column_type():
    db = NanaSQLite(":memory:")
    
    # 正常な型のテスト
    db.alter_table_add_column("data", "new_col", "DOUBLE PRECISION")
    schema = db.get_table_schema()
    cols = [col["name"] for col in schema]
    assert "new_col" in cols
    
    db.alter_table_add_column("data", "new_col2", "VARCHAR(255)")
    schema = db.get_table_schema()
    cols = [col["name"] for col in schema]
    assert "new_col2" in cols

    # 長大な不正文字列でのパフォーマンス（ReDoS）テスト
    # 脆弱な正規表現ではバックトラッキングにより時間がかかるかエラーになる
    long_invalid_type = "A" + " " * 100000 + "!"
    
    start_time = time.time()
    with pytest.raises(ValueError, match="Invalid or dangerous column type"):
        db.alter_table_add_column("data", "bad_col", long_invalid_type)
    end_time = time.time()
    
    # 修正後の正規表現はバックトラッキングが制御されているため、非常に高速に処理される
    assert (end_time - start_time) < 0.1  # 十分に高速であることを確認
