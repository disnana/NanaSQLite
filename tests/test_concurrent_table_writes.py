"""
テーブル間の同時書き込みの徹底テスト
メインテーブルとサブテーブルに同時に大量書き込みを行い、データ整合性を確認
"""

import asyncio
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from src.nanasqlite import AsyncNanaSQLite, NanaSQLite


class TestConcurrentTableWrites:
    """同期版: メインテーブルとサブテーブルへの同時書き込みテスト"""

    def test_sync_two_tables_concurrent_writes(self):
        """2つのテーブルに同時に書き込み"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            # メインインスタンスを作成し、table()メソッドでサブテーブルインスタンスを取得
            # これにより接続とロックが共有される
            main_db = NanaSQLite(db_path, table="main")
            sub_db = main_db.table("sub")

            def write_to_main(index):
                key = f"main_item_{index}"
                value = {"table": "main", "index": index, "data": f"main_data_{index}"}
                main_db[key] = value
                return key, value

            def write_to_sub(index):
                key = f"sub_item_{index}"
                value = {"table": "sub", "index": index, "data": f"sub_data_{index}"}
                sub_db[key] = value
                return key, value

            # 同時書き込み実行
            with ThreadPoolExecutor(max_workers=10) as executor:
                main_futures = [executor.submit(write_to_main, i) for i in range(100)]
                sub_futures = [executor.submit(write_to_sub, i) for i in range(100)]

                all_futures = main_futures + sub_futures
                for future in as_completed(all_futures):
                    future.result()  # 例外があれば発生

            # 検証: 全データが正しく書き込まれているか
            for i in range(100):
                main_key = f"main_item_{i}"
                assert main_key in main_db
                main_value = main_db[main_key]
                assert main_value["table"] == "main"
                assert main_value["index"] == i
                assert main_value["data"] == f"main_data_{i}"

                sub_key = f"sub_item_{i}"
                assert sub_key in sub_db
                sub_value = sub_db[sub_key]
                assert sub_value["table"] == "sub"
                assert sub_value["index"] == i
                assert sub_value["data"] == f"sub_data_{i}"

            # 接続を閉じる
            main_db.close()

        finally:
            os.unlink(db_path)

    def test_sync_multiple_tables_heavy_load(self):
        """複数テーブル（3つ以上）に高負荷で書き込み"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            # メインインスタンスから各テーブルインスタンスを作成して接続を共有
            main_db = NanaSQLite(db_path, table="table_a")
            tables = {
                "table_a": main_db,
                "table_b": main_db.table("table_b"),
                "table_c": main_db.table("table_c"),
                "table_d": main_db.table("table_d"),
            }

            def write_to_table(table_name, index):
                db = tables[table_name]
                key = f"{table_name}_item_{index}"
                value = {
                    "table": table_name,
                    "index": index,
                    "large_data": "x" * 1000,  # 1KB程度のデータ
                }
                db[key] = value
                return table_name, key

            # 各テーブルに500件ずつ、合計2000件を同時書き込み
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = []
                for table_name in tables.keys():
                    for i in range(500):
                        futures.append(executor.submit(write_to_table, table_name, i))

                for future in as_completed(futures):
                    future.result()

            # 検証
            for table_name, db in tables.items():
                for i in range(500):
                    key = f"{table_name}_item_{i}"
                    assert key in db
                    value = db[key]
                    assert value["table"] == table_name
                    assert value["index"] == i
                    assert len(value["large_data"]) == 1000

            # 接続を閉じる（最初のインスタンスのみ）
            tables["table_a"].close()

        finally:
            os.unlink(db_path)

    def test_sync_same_key_different_tables(self):
        """異なるテーブルに同じキーで同時書き込み（競合しないことを確認）"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            # table()メソッドで接続を共有
            main_db = NanaSQLite(db_path, table="main")
            sub_db = main_db.table("sub")

            def write_same_key_to_main(index):
                key = "shared_key"
                value = {"source": "main", "write_num": index}
                main_db[key] = value

            def write_same_key_to_sub(index):
                key = "shared_key"
                value = {"source": "sub", "write_num": index}
                sub_db[key] = value

            # 同じキーに複数回書き込み
            with ThreadPoolExecutor(max_workers=10) as executor:
                main_futures = [executor.submit(write_same_key_to_main, i) for i in range(50)]
                sub_futures = [executor.submit(write_same_key_to_sub, i) for i in range(50)]

                for future in as_completed(main_futures + sub_futures):
                    future.result()

            # 検証: 両方のテーブルに"shared_key"が存在し、異なる値を持つ
            assert "shared_key" in main_db
            assert "shared_key" in sub_db

            main_value = main_db["shared_key"]
            sub_value = sub_db["shared_key"]

            assert main_value["source"] == "main"
            assert sub_value["source"] == "sub"
            # 最後の書き込みが保持されている
            assert 0 <= main_value["write_num"] < 50
            assert 0 <= sub_value["write_num"] < 50

            # 接続を閉じる
            main_db.close()

        finally:
            os.unlink(db_path)

    def test_sync_read_write_concurrent(self):
        """読み取りと書き込みを同時に実行"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            # table()メソッドで接続を共有
            main_db = NanaSQLite(db_path, table="main")
            sub_db = main_db.table("sub")

            # 初期データを投入
            for i in range(50):
                main_db[f"item_{i}"] = {"value": i}
                sub_db[f"item_{i}"] = {"value": i * 2}

            read_results = {"main": [], "sub": []}
            write_count = {"main": 0, "sub": 0}

            def read_from_main(index):
                key = f"item_{index % 50}"
                if key in main_db:
                    value = main_db[key]
                    read_results["main"].append(value)

            def write_to_main(index):
                key = f"new_item_{index}"
                main_db[key] = {"value": index}
                write_count["main"] += 1

            def read_from_sub(index):
                key = f"item_{index % 50}"
                if key in sub_db:
                    value = sub_db[key]
                    read_results["sub"].append(value)

            def write_to_sub(index):
                key = f"new_item_{index}"
                sub_db[key] = {"value": index * 2}
                write_count["sub"] += 1

            # 読み書き同時実行
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = []
                for i in range(100):
                    futures.append(executor.submit(read_from_main, i))
                    futures.append(executor.submit(write_to_main, i))
                    futures.append(executor.submit(read_from_sub, i))
                    futures.append(executor.submit(write_to_sub, i))

                for future in as_completed(futures):
                    future.result()

            # 検証
            assert len(read_results["main"]) > 0
            assert len(read_results["sub"]) > 0
            assert write_count["main"] == 100
            assert write_count["sub"] == 100

            # 新しく書き込まれたデータの検証
            for i in range(100):
                assert f"new_item_{i}" in main_db
                assert main_db[f"new_item_{i}"]["value"] == i
                assert f"new_item_{i}" in sub_db
                assert sub_db[f"new_item_{i}"]["value"] == i * 2

            # 接続を閉じる
            main_db.close()

        finally:
            os.unlink(db_path)

    def test_sync_cache_isolation_between_tables(self):
        """テーブル間でキャッシュが独立していることを確認"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            # table()メソッドで接続を共有
            # Note: use_cache, cache_limitパラメータは将来の実装で対応予定
            main_db = NanaSQLite(db_path, table="main")
            sub_db = main_db.table("sub")

            # 各テーブルに100件書き込み（キャッシュ上限を超える）
            for i in range(100):
                main_db[f"item_{i}"] = {"table": "main", "value": i}
                sub_db[f"item_{i}"] = {"table": "sub", "value": i * 2}

            # キャッシュ統計を確認（実装されている場合）
            print(f"Main DB: {main_db}")
            print(f"Sub DB: {sub_db}")

            # 全データが正しく読み取れることを確認（キャッシュに関係なくDBから取得できる）
            for i in range(100):
                main_value = main_db[f"item_{i}"]
                assert main_value["table"] == "main"
                assert main_value["value"] == i

                sub_value = sub_db[f"item_{i}"]
                assert sub_value["table"] == "sub"
                assert sub_value["value"] == i * 2

            # 接続を閉じる
            main_db.close()

        finally:
            os.unlink(db_path)


class TestAsyncConcurrentTableWrites:
    """非同期版: メインテーブルとサブテーブルへの同時書き込みテスト"""

    @pytest.mark.asyncio
    async def test_async_two_tables_concurrent_writes(self):
        """2つのテーブルに非同期で同時書き込み"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            async with AsyncNanaSQLite(db_path, table="main") as main_db:
                async with await main_db.table("sub") as sub_db:

                    async def write_to_main(index):
                        key = f"main_item_{index}"
                        value = {"table": "main", "index": index}
                        await main_db.aset(key, value)

                    async def write_to_sub(index):
                        key = f"sub_item_{index}"
                        value = {"table": "sub", "index": index}
                        await sub_db.aset(key, value)

                    # 同時書き込み
                    main_tasks = [write_to_main(i) for i in range(100)]
                    sub_tasks = [write_to_sub(i) for i in range(100)]
                    await asyncio.gather(*main_tasks, *sub_tasks)

                    # 検証
                    for i in range(100):
                        main_key = f"main_item_{i}"
                        assert await main_db.acontains(main_key)
                        main_value = await main_db.aget(main_key)
                        assert main_value["table"] == "main"
                        assert main_value["index"] == i

                        sub_key = f"sub_item_{i}"
                        assert await sub_db.acontains(sub_key)
                        sub_value = await sub_db.aget(sub_key)
                        assert sub_value["table"] == "sub"
                        assert sub_value["index"] == i

        finally:
            os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_async_multiple_tables_heavy_load(self):
        """複数テーブルに非同期で高負荷書き込み"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            async with AsyncNanaSQLite(db_path, table="table_a") as db_a:
                async with await db_a.table("table_b") as db_b:
                    async with await db_a.table("table_c") as db_c:
                        async with await db_a.table("table_d") as db_d:
                            tables = {
                                "table_a": db_a,
                                "table_b": db_b,
                                "table_c": db_c,
                                "table_d": db_d,
                            }

                            async def write_to_table(table_name, db, index):
                                key = f"{table_name}_item_{index}"
                                value = {"table": table_name, "index": index, "large_data": "x" * 1000}
                                await db.aset(key, value)

                            # 各テーブルに500件ずつ同時書き込み
                            tasks = []
                            for table_name, db in tables.items():
                                for i in range(500):
                                    tasks.append(write_to_table(table_name, db, i))

                            await asyncio.gather(*tasks)

                            # 検証
                            for table_name, db in tables.items():
                                for i in range(500):
                                    key = f"{table_name}_item_{i}"
                                    assert await db.acontains(key)
                                    value = await db.aget(key)
                                    assert value["table"] == table_name
                                    assert value["index"] == i
                                    assert len(value["large_data"]) == 1000

        finally:
            os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_async_same_key_different_tables(self):
        """異なるテーブルに同じキーで非同期同時書き込み"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            async with AsyncNanaSQLite(db_path, table="main") as main_db:
                async with await main_db.table("sub") as sub_db:

                    async def write_same_key_to_main(index):
                        await main_db.aset("shared_key", {"source": "main", "write_num": index})

                    async def write_same_key_to_sub(index):
                        await sub_db.aset("shared_key", {"source": "sub", "write_num": index})

                    # 同時書き込み
                    main_tasks = [write_same_key_to_main(i) for i in range(50)]
                    sub_tasks = [write_same_key_to_sub(i) for i in range(50)]
                    await asyncio.gather(*main_tasks, *sub_tasks)

                    # 検証
                    assert await main_db.acontains("shared_key")
                    assert await sub_db.acontains("shared_key")

                    main_value = await main_db.aget("shared_key")
                    sub_value = await sub_db.aget("shared_key")

                    assert main_value["source"] == "main"
                    assert sub_value["source"] == "sub"

        finally:
            os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_async_read_write_concurrent(self):
        """非同期での読み書き同時実行"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            async with AsyncNanaSQLite(db_path, table="main") as main_db:
                async with await main_db.table("sub") as sub_db:
                    # 初期データ投入
                    for i in range(50):
                        await main_db.aset(f"item_{i}", {"value": i})
                        await sub_db.aset(f"item_{i}", {"value": i * 2})

                    read_results = {"main": [], "sub": []}

                    async def read_from_main(index):
                        key = f"item_{index % 50}"
                        if await main_db.acontains(key):
                            value = await main_db.aget(key)
                            read_results["main"].append(value)

                    async def write_to_main(index):
                        key = f"new_item_{index}"
                        await main_db.aset(key, {"value": index})

                    async def read_from_sub(index):
                        key = f"item_{index % 50}"
                        if await sub_db.acontains(key):
                            value = await sub_db.aget(key)
                            read_results["sub"].append(value)

                    async def write_to_sub(index):
                        key = f"new_item_{index}"
                        await sub_db.aset(key, {"value": index * 2})

                    # 読み書き同時実行
                    tasks = []
                    for i in range(100):
                        tasks.append(read_from_main(i))
                        tasks.append(write_to_main(i))
                        tasks.append(read_from_sub(i))
                        tasks.append(write_to_sub(i))

                    await asyncio.gather(*tasks)

                    # 検証
                    assert len(read_results["main"]) > 0
                    assert len(read_results["sub"]) > 0

                    for i in range(100):
                        assert await main_db.acontains(f"new_item_{i}")
                        main_value = await main_db.aget(f"new_item_{i}")
                        assert main_value["value"] == i

                        assert await sub_db.acontains(f"new_item_{i}")
                        sub_value = await sub_db.aget(f"new_item_{i}")
                        assert sub_value["value"] == i * 2

        finally:
            os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_async_stress_test_1000_concurrent_writes(self):
        """ストレステスト: 1000件の同時書き込み"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            async with AsyncNanaSQLite(db_path, table="main", max_workers=10) as main_db:
                async with await main_db.table("sub") as sub_db:

                    async def write_pair(index):
                        await main_db.aset(f"item_{index}", {"table": "main", "value": index})
                        await sub_db.aset(f"item_{index}", {"table": "sub", "value": index * 2})

                    # 1000ペアの同時書き込み
                    tasks = [write_pair(i) for i in range(1000)]
                    await asyncio.gather(*tasks)

                    # サンプル検証（全件チェックすると時間がかかるので）
                    for i in range(0, 1000, 10):
                        assert await main_db.acontains(f"item_{i}")
                        main_value = await main_db.aget(f"item_{i}")
                        assert main_value["value"] == i

                        assert await sub_db.acontains(f"item_{i}")
                        sub_value = await sub_db.aget(f"item_{i}")
                        assert sub_value["value"] == i * 2

        finally:
            os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_async_cache_isolation_between_tables(self):
        """非同期でのテーブル間キャッシュ独立性確認"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            # Note: use_cache, cache_limitパラメータは将来の実装で対応予定
            async with AsyncNanaSQLite(db_path, table="main") as main_db:
                async with await main_db.table("sub") as sub_db:
                    # 各テーブルに100件書き込み
                    tasks = []
                    for i in range(100):
                        tasks.append(main_db.aset(f"item_{i}", {"table": "main", "value": i}))
                        tasks.append(sub_db.aset(f"item_{i}", {"table": "sub", "value": i * 2}))
                    await asyncio.gather(*tasks)

                    print(f"Main DB: {main_db}")
                    print(f"Sub DB: {sub_db}")

                    # 全データが正しく読み取れることを確認
                    for i in range(100):
                        main_value = await main_db.aget(f"item_{i}")
                        assert main_value["table"] == "main"
                        assert main_value["value"] == i

                        sub_value = await sub_db.aget(f"item_{i}")
                        assert sub_value["table"] == "sub"
                        assert sub_value["value"] == i * 2

        finally:
            os.unlink(db_path)


class TestEdgeCases:
    """エッジケースのテスト"""

    def test_sync_table_switch_during_operations(self):
        """操作中にテーブルを切り替えても問題ないことを確認"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            db = NanaSQLite(db_path, table="main")

            # mainに書き込み
            db["key1"] = {"value": 1}

            # subに切り替え
            sub_db = db.table("sub")
            sub_db["key1"] = {"value": 2}

            # 再度mainに切り替え
            main_db2 = sub_db.table("main")

            # 値を確認
            assert db["key1"]["value"] == 1
            assert sub_db["key1"]["value"] == 2
            assert main_db2["key1"]["value"] == 1

            # 接続を閉じる
            db.close()

        finally:
            os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_async_table_switch_during_operations(self):
        """非同期版: 操作中にテーブルを切り替えても問題ないことを確認"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            async with AsyncNanaSQLite(db_path, table="main") as main_db:
                await main_db.aset("key1", {"value": 1})

                async with await main_db.table("sub") as sub_db:
                    await sub_db.aset("key1", {"value": 2})

                    async with await sub_db.table("main") as main_db2:
                        # 値を確認
                        main_value = await main_db.aget("key1")
                        sub_value = await sub_db.aget("key1")
                        main_value2 = await main_db2.aget("key1")

                        assert main_value["value"] == 1
                        assert sub_value["value"] == 2
                        assert main_value2["value"] == 1

        finally:
            os.unlink(db_path)

    def test_sync_empty_table_operations(self):
        """空のテーブルでの操作"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            # 接続を共有
            main_db = NanaSQLite(db_path, table="main")
            sub_db = main_db.table("sub")

            # 空の状態で読み取り試行
            assert "nonexistent" not in main_db
            assert "nonexistent" not in sub_db

            with pytest.raises(KeyError):
                _ = main_db["nonexistent"]

            with pytest.raises(KeyError):
                _ = sub_db["nonexistent"]

            # 接続を閉じる
            main_db.close()

        finally:
            os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_async_empty_table_operations(self):
        """非同期版: 空のテーブルでの操作"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            async with AsyncNanaSQLite(db_path, table="main") as main_db:
                async with await main_db.table("sub") as sub_db:
                    # 空の状態で読み取り試行
                    assert not await main_db.acontains("nonexistent")
                    assert not await sub_db.acontains("nonexistent")

                    # aget()はdefault=Noneを返す（KeyErrorは発生しない）
                    assert await main_db.aget("nonexistent") is None
                    assert await sub_db.aget("nonexistent") is None

                    # カスタムdefault値も機能する
                    assert await main_db.aget("nonexistent", "default") == "default"
                    assert await sub_db.aget("nonexistent", {}) == {}

        finally:
            os.unlink(db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
