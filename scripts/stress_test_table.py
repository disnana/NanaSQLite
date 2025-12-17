"""
table()機能のストレステスト
潜在的な問題を検出するためのストレステスト
"""
import tempfile
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.nanasqlite import NanaSQLite, AsyncNanaSQLite


def test_sync_memory_leak():
    """メモリリークの可能性をチェック"""
    print("=== Test 1: 同期版メモリリーク検証 ===")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        main_db = NanaSQLite(db_path, table="main")
        
        # 多数のサブテーブルインスタンスを作成
        for i in range(100):
            sub_db = main_db.table(f"sub_{i}")
            sub_db[f"key_{i}"] = f"value_{i}"
            # sub_dbは明示的にclose()していない（ガベージコレクションに任せる）
        
        # メインDBは正常に動作するか
        main_db["test"] = "value"
        assert main_db["test"] == "value"
        
        main_db.close()
        print("✓ メモリリーク検証完了")
    finally:
        os.unlink(db_path)


def test_sync_connection_ownership():
    """接続所有権の管理が正しいかチェック"""
    print("\n=== Test 2: 同期版接続所有権検証 ===")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        main_db = NanaSQLite(db_path, table="main")
        sub_db = main_db.table("sub")
        
        # サブインスタンスをclose()してもメインは動作するか
        sub_db["sub_key"] = "sub_value"
        sub_db.close()  # これは何もしないはず（接続の所有者ではない）
        
        # メインDBはまだ動作する
        main_db["main_key"] = "main_value"
        assert main_db["main_key"] == "main_value"
        
        # サブテーブルに新しいインスタンスでアクセスできる
        sub_db2 = main_db.table("sub")
        assert sub_db2["sub_key"] == "sub_value"
        
        main_db.close()
        print("✓ 接続所有権検証完了")
    finally:
        os.unlink(db_path)


def test_sync_heavy_concurrent_access():
    """高負荷並行アクセスのストレステスト"""
    print("\n=== Test 3: 同期版高負荷並行アクセス ===")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        main_db = NanaSQLite(db_path, table="main")
        tables = [main_db.table(f"table_{i}") for i in range(10)]
        
        def heavy_write(table_idx, item_idx):
            db = tables[table_idx]
            key = f"item_{item_idx}"
            # 大きなデータを書き込み
            value = {
                "data": "x" * 10000,  # 10KB
                "idx": item_idx,
                "table": table_idx
            }
            db[key] = value
            return table_idx, item_idx
        
        start = time.time()
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for table_idx in range(10):
                for item_idx in range(100):
                    futures.append(executor.submit(heavy_write, table_idx, item_idx))
            
            for future in as_completed(futures):
                table_idx, item_idx = future.result()
        
        elapsed = time.time() - start
        
        # 検証
        for table_idx in range(10):
            db = tables[table_idx]
            for item_idx in range(100):
                key = f"item_{item_idx}"
                assert key in db
                value = db[key]
                assert len(value["data"]) == 10000
                assert value["idx"] == item_idx
                assert value["table"] == table_idx
        
        print(f"✓ 高負荷並行アクセス検証完了: {elapsed:.2f}秒で1000件の10KB書き込み")
        main_db.close()
    finally:
        os.unlink(db_path)


async def test_async_executor_sharing():
    """非同期版のエグゼキューター共有が正しいかチェック"""
    print("\n=== Test 4: 非同期版エグゼキューター共有検証 ===")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        async with AsyncNanaSQLite(db_path, table="main", max_workers=5) as main_db:
            sub_db = await main_db.table("sub")
            
            # 両方が同じエグゼキューターを使用しているか
            assert main_db._executor is sub_db._executor
            assert main_db._owns_executor is True
            assert sub_db._owns_executor is False
            
            # 同時に大量の操作を実行
            async def write_many(db, prefix, count):
                for i in range(count):
                    await db.aset(f"{prefix}_{i}", {"value": i})
            
            await asyncio.gather(
                write_many(main_db, "main", 50),
                write_many(sub_db, "sub", 50)
            )
            
            # 検証
            for i in range(50):
                assert await main_db.acontains(f"main_{i}")
                assert await sub_db.acontains(f"sub_{i}")
            
            # サブインスタンスをclose()してもエグゼキューターは残る
            await sub_db.close()
            await main_db.aset("after_sub_close", "value")
            assert await main_db.aget("after_sub_close") == "value"
        
        print("✓ 非同期版エグゼキューター共有検証完了")
    finally:
        os.unlink(db_path)


async def test_async_nested_contexts():
    """非同期版のネストしたコンテキストマネージャーの動作確認"""
    print("\n=== Test 5: 非同期版ネストコンテキスト検証 ===")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        # ネストしたコンテキスト
        async with AsyncNanaSQLite(db_path, table="main") as main_db:
            sub_db = await main_db.table("sub")
            # async withを使わずに直接使用
            await sub_db.aset("key1", "value1")
            
            # 内側でasync withを使用
            async with await main_db.table("sub2") as sub_db2:
                await sub_db2.aset("key2", "value2")
            
            # sub_db2はcloseされているが、mainとsubは動作する
            await main_db.aset("main_key", "main_value")
            await sub_db.aset("sub_key", "sub_value")
            
            # 検証
            assert await main_db.aget("main_key") == "main_value"
            assert await sub_db.aget("sub_key") == "sub_value"
            
            # sub2のデータも永続化されている
            sub_db3 = await main_db.table("sub2")
            assert await sub_db3.aget("key2") == "value2"
        
        print("✓ 非同期版ネストコンテキスト検証完了")
    finally:
        os.unlink(db_path)


async def test_async_heavy_concurrent():
    """非同期版の高負荷並行処理"""
    print("\n=== Test 6: 非同期版高負荷並行処理 ===")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        async with AsyncNanaSQLite(db_path, table="main", max_workers=10) as main_db:
            tables = []
            for i in range(10):
                sub_db = await main_db.table(f"table_{i}")
                tables.append((f"table_{i}", sub_db))
            
            async def write_heavy(table_name, db, count):
                for i in range(count):
                    await db.aset(f"{table_name}_item_{i}", {"data": "x" * 1000, "idx": i})
            
            start = time.time()
            tasks = [write_heavy(name, db, 100) for name, db in tables]
            await asyncio.gather(*tasks)
            elapsed = time.time() - start
            
            # 検証
            for table_name, db in tables:
                for i in range(100):
                    key = f"{table_name}_item_{i}"
                    assert await db.acontains(key)
                    value = await db.aget(key)
                    assert len(value["data"]) == 1000
            
            print(f"✓ 非同期版高負荷並行処理完了: {elapsed:.2f}秒で1000件書き込み")
    finally:
        os.unlink(db_path)


def test_cache_isolation():
    """キャッシュが正しく分離されているか"""
    print("\n=== Test 7: キャッシュ分離検証 ===")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        main_db = NanaSQLite(db_path, table="main")
        sub_db = main_db.table("sub")
        
        # 同じキーを両方のテーブルに保存
        main_db["shared_key"] = {"source": "main"}
        sub_db["shared_key"] = {"source": "sub"}
        
        # キャッシュが分離されているか確認
        assert main_db["shared_key"]["source"] == "main"
        assert sub_db["shared_key"]["source"] == "sub"
        
        # データベースに永続化されているか確認（新しいインスタンスで）
        main_db2 = NanaSQLite(db_path, table="main")
        sub_db2 = main_db2.table("sub")
        
        assert main_db2["shared_key"]["source"] == "main"
        assert sub_db2["shared_key"]["source"] == "sub"
        
        main_db.close()
        main_db2.close()
        print("✓ キャッシュ分離検証完了")
    finally:
        os.unlink(db_path)


def main():
    print("table()機能のストレステスト開始\n")
    
    # 同期版テスト
    test_sync_memory_leak()
    test_sync_connection_ownership()
    test_sync_heavy_concurrent_access()
    test_cache_isolation()
    
    # 非同期版テスト
    asyncio.run(test_async_executor_sharing())
    asyncio.run(test_async_nested_contexts())
    asyncio.run(test_async_heavy_concurrent())
    
    print("\n" + "=" * 60)
    print("全てのストレステストが正常に完了しました！")
    print("=" * 60)


if __name__ == "__main__":
    main()

