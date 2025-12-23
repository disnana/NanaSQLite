
import pytest
import os
from nanasqlite import AsyncNanaSQLite, NanaSQLiteValidationError

@pytest.mark.asyncio
async def test_query_reserved_keyword_column(tmp_path):
    """
    AsyncNanaSQLite.query で予約語（group）をカラム名に使用できることを検証
    """
    db_path = str(tmp_path / "test_sanitization.db")
    db = AsyncNanaSQLite(db_path)
    await db.create_table("test", {"group": "TEXT", "name": "TEXT"})
    await db.sql_insert("test", {"group": "Admin", "name": "Alice"})
    
    # 修正前はここで syntax error が発生していた
    results = await db.query(table_name="test", columns=["group", "name"])
    assert len(results) == 1
    assert results[0]["group"] == "Admin"
    await db.close()

@pytest.mark.asyncio
async def test_query_per_query_validation(tmp_path):
    """
    AsyncNanaSQLite.query でクエリ単位の関数許可（allowed_sql_functions）が機能することを検証
    """
    db_path = str(tmp_path / "test_validation.db")
    db = AsyncNanaSQLite(db_path, strict_sql_validation=True)
    await db.create_table("test", {"name": "TEXT"})
    await db.sql_insert("test", {"name": "Alice"})
    
    # HEX はデフォルトで許可されていないためエラーになるはず
    with pytest.raises((NanaSQLiteValidationError, ValueError)):
        await db.query(table_name="test", columns=["HEX(name)"])
        
    # クエリ単位で許可すれば成功するはず
    results = await db.query(table_name="test", columns=["HEX(name)"], allowed_sql_functions=["HEX"])
    hex_value = results[0]["HEX(name)"]
    assert hex_value == "416C696365"
    # HEX値をデコードして元の文字列と一致することを確認 (#4)
    assert bytes.fromhex(hex_value).decode("utf-8") == "Alice"
    await db.close()

@pytest.mark.asyncio
async def test_groupby_validation_in_pagination(tmp_path):
    """
    query_with_pagination で group_by 句のバリデーションが機能することを検証
    """
    db_path = str(tmp_path / "test_groupby.db")
    db = AsyncNanaSQLite(db_path, strict_sql_validation=True)
    await db.create_table("test", {"category": "TEXT", "val": "INTEGER"})
    await db.sql_insert("test", {"category": "A", "val": 10})
    
    # HEX を group_by に含めるとエラーになるはず
    with pytest.raises((NanaSQLiteValidationError, ValueError)):
        await db.query_with_pagination(
            table_name="test", 
            columns=["category", "SUM(val)"], 
            group_by="HEX(category)"
        )
        
    # 許可すれば成功する
    results = await db.query_with_pagination(
        table_name="test", 
        columns=["category", "SUM(val)"], 
        group_by="HEX(category)",
        allowed_sql_functions=["HEX"]
    )
    assert len(results) == 1
    await db.close()

@pytest.mark.asyncio
async def test_complex_column_aliases_metadata(tmp_path):
    """
    cursor.description を使用したカラム名抽出が複雑な式でも正常に動作することを検証 (#2)
    """
    db_path = str(tmp_path / "test_complex_cols.db")
    db = AsyncNanaSQLite(db_path)
    await db.create_table("test", {"name": "TEXT", "val": "INTEGER"})
    await db.sql_insert("test", {"name": "Alice as Bob", "val": 10})
    
    # " as " を含む文字列リテラルや複雑なエイリアス
    # 以前の正規表現パースでは "Alice as Bob" の " as " で誤分割される可能性があった
    sql_cols = [
        "name as \"user_name\"",
        "val + 100 as total",
        "'prefix as ' || name as complex_label"
    ]
    results = await db.query(table_name="test", columns=sql_cols)
    
    assert len(results) == 1
    assert results[0]["user_name"] == "Alice as Bob"
    assert results[0]["total"] == 110
    assert results[0]["complex_label"] == "prefix as Alice as Bob"
    await db.close()

def test_eq_when_closed(tmp_path):
    """
    DB接続が閉じている場合に == 演算子が False を返すことを検証 (#5)
    """
    from nanasqlite import NanaSQLite
    db_path = str(tmp_path / "test_eq_closed.db")
    db1 = NanaSQLite(db_path)
    db1["k"] = "v"
    
    db2 = {"k": "v"}
    assert db1 == db2 # 接続中は True
    
    db1.close()
    # 以前はここで NanaSQLiteClosedError が発生していた
    assert (db1 == db2) is False # クローズ後は False
