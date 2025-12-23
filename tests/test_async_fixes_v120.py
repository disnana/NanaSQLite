
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
    assert results[0]["HEX(name)"] == "416C696365"
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
async def test_pool_initialization_naming(tmp_path):
    """
    命名規約を修正した _init_pool_connection が正常に動作し、
    接続プールが適切に初期化されることを検証
    """
    db_path = str(tmp_path / "test_pool.db")
    # read_pool_size > 0 で初期化
    db = AsyncNanaSQLite(db_path, read_pool_size=2)
    await db.create_table("test", {"id": "INTEGER"})
    
    # 接続プールが作成されていることを間接的に確認
    assert db._read_pool is not None
    assert db._read_pool.qsize() == 2
    
    # プールからの読み取りが正常に行えるか
    results = await db.query("test")
    assert results == []
    
    await db.close()
