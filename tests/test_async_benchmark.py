"""
NanaSQLite Async Performance Benchmarks

pytest-benchmarkを使用した非同期操作のパフォーマンス計測
"""

import asyncio
import importlib.util
import os
import tempfile

import pytest

# pytest-benchmarkがインストールされているか確認
pytest_benchmark_available = importlib.util.find_spec("pytest_benchmark") is not None


# ==================== Fixtures ====================


@pytest.fixture
def db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "async_bench.db")


@pytest.fixture
def async_db_instance(db_path):
    """AsyncNanaSQLiteインスタンスをベンチマーク全体で共有（接続オーバーヘッドを排除）"""
    from nanasqlite import AsyncNanaSQLite

    db = AsyncNanaSQLite(db_path)
    yield db
    # 完全にクリーンアップ
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 実行中のループがある場合はタスクとして追加
            loop.create_task(db.close())
        else:
            loop.run_until_complete(db.close())
    except Exception:
        pass


@pytest.fixture
def async_db_with_data_instance(db_path):
    """1000件のデータが入ったAsync DBインスタンス"""
    from nanasqlite import AsyncNanaSQLite

    async def setup():
        db = AsyncNanaSQLite(db_path)
        data = {f"key_{i}": {"index": i, "data": "x" * 100} for i in range(1000)}
        await db.batch_update(data)
        return db

    loop = asyncio.get_event_loop()
    db = loop.run_until_complete(setup())
    yield db
    try:
        loop.run_until_complete(db.close())
    except Exception:
        pass


# ベンチマーク用の永続的イベントループ
_benchmark_loop = asyncio.new_event_loop()


def run_async(coro):
    """非同期関数を同期的に実行するヘルパー（ループを再利用）"""
    return _benchmark_loop.run_until_complete(coro)


# ==================== Async Write Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestAsyncWriteBenchmarks:
    """非同期書き込みパフォーマンスのベンチマーク"""

    def test_async_single_write(self, benchmark, async_db_instance):
        """非同期単一書き込み"""
        counter = [0]

        def write_single():
            async def _write():
                await async_db_instance.aset(f"key_{counter[0]}", {"data": "value", "number": counter[0]})
                counter[0] += 1

            run_async(_write())

        benchmark(write_single)

    def test_async_nested_write(self, benchmark, async_db_instance):
        """ネストしたデータの非同期書き込み"""
        counter = [0]
        nested_data = {"level1": {"level2": {"level3": {"data": [1, 2, 3, {"nested": True}]}}}}

        def write_nested():
            async def _write():
                await async_db_instance.aset(f"nested_{counter[0]}", nested_data)
                counter[0] += 1

            run_async(_write())

        benchmark(write_nested)

    def test_async_batch_write_100(self, benchmark, async_db_instance):
        """非同期バッチ書き込み（100件）"""
        counter = [0]

        def batch_write():
            async def _batch():
                data = {f"batch_{counter[0]}_{i}": {"index": i} for i in range(100)}
                await async_db_instance.abatch_update(data)
                counter[0] += 1

            run_async(_batch())

        benchmark(batch_write)

    def test_async_batch_write_1000(self, benchmark, async_db_instance):
        """非同期バッチ書き込み（1000件）"""
        counter = [0]

        def batch_write():
            async def _batch():
                data = {f"batch_{counter[0]}_{i}": {"index": i} for i in range(1000)}
                await async_db_instance.abatch_update(data)
                counter[0] += 1

            run_async(_batch())

        benchmark(batch_write)


# ==================== Async Read Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestAsyncReadBenchmarks:
    """非同期読み込みパフォーマンスのベンチマーク"""

    def test_async_single_read(self, benchmark, async_db_with_data_instance):
        """非同期単一読み込み"""

        def read_single():
            async def _read():
                return await async_db_with_data_instance.aget("key_500")

            return run_async(_read())

        benchmark(read_single)

    def test_async_batch_get(self, benchmark, async_db_with_data_instance):
        """非同期バッチ取得（100件）"""
        keys = [f"key_{i}" for i in range(100)]

        def batch_get():
            async def _get():
                return await async_db_with_data_instance.abatch_get(keys)

            return run_async(_get())

        benchmark(batch_get)

    def test_async_bulk_load_1000(self, benchmark, db_path):
        """非同期一括ロード（1000件）"""
        from nanasqlite import AsyncNanaSQLite

        # データ準備（ここだけは新規接続でロード性能を測る必要があるため async with を使用）
        async def setup():
            async with AsyncNanaSQLite(db_path) as db:
                await db.batch_update({f"key_{i}": {"index": i} for i in range(1000)})

        run_async(setup())

        def bulk_load():
            async def _load():
                async with AsyncNanaSQLite(db_path, bulk_load=True):
                    pass

            run_async(_load())

        benchmark(bulk_load)

    def test_async_get_fresh(self, benchmark, async_db_with_data_instance):
        """非同期get_fresh（キャッシュバイパス）"""

        def get_fresh():
            async def _get():
                return await async_db_with_data_instance.get_fresh("key_500")

            return run_async(_get())

        benchmark(get_fresh)


# ==================== Async Dict Operations Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestAsyncDictOperationsBenchmarks:
    """非同期dict操作のベンチマーク"""

    def test_async_keys_1000(self, benchmark, async_db_with_data_instance):
        """非同期keys()取得（1000件）"""

        def get_keys():
            async def _keys():
                return await async_db_with_data_instance.akeys()

            return run_async(_keys())

        benchmark(get_keys)

    def test_async_values_1000(self, benchmark, async_db_with_data_instance):
        """非同期values()取得（1000件）"""

        def get_values():
            async def _values():
                return await async_db_with_data_instance.avalues()

            return run_async(_values())

        benchmark(get_values)

    def test_async_contains_check(self, benchmark, async_db_with_data_instance):
        """非同期存在確認"""

        def check_contains():
            async def _check():
                return await async_db_with_data_instance.acontains("key_500")

            return run_async(_check())

        benchmark(check_contains)

    def test_async_len(self, benchmark, async_db_with_data_instance):
        """非同期len()取得"""

        def get_len():
            async def _len():
                return await async_db_with_data_instance.alen()

            return run_async(_len())

        benchmark(get_len)

    def test_async_to_dict_1000(self, benchmark, async_db_with_data_instance):
        """非同期to_dict()変換（1000件）"""

        def get_to_dict():
            async def _to_dict():
                return await async_db_with_data_instance.ato_dict()

            return run_async(_to_dict())

        benchmark(get_to_dict)

    def test_async_pop(self, benchmark, async_db_instance):
        """非同期pop()操作"""
        counter = [0]

        def pop_op():
            async def _pop():
                await async_db_instance.aset(f"pop_key_{counter[0]}", {"value": counter[0]})
                result = await async_db_instance.apop(f"pop_key_{counter[0]}")
                counter[0] += 1
                return result

            return run_async(_pop())

        benchmark(pop_op)

    def test_async_setdefault(self, benchmark, async_db_instance):
        """非同期setdefault()操作"""
        counter = [0]

        def setdefault_op():
            async def _setdefault():
                result = await async_db_instance.asetdefault(f"default_key_{counter[0]}", {"default": True})
                counter[0] += 1
                return result

            return run_async(_setdefault())

        benchmark(setdefault_op)

    def test_async_batch_get_100(self, benchmark, async_db_with_data_instance):
        """非同期バッチ取得（100件）"""
        keys = [f"key_{i}" for i in range(100)]

        def batch_get_op():
            async def _get():
                return await async_db_with_data_instance.abatch_get(keys)

            return run_async(_get())

        benchmark(batch_get_op)

    def test_async_batch_delete_100(self, benchmark, async_db_instance):
        """非同期バッチ削除（100件）"""
        counter = [0]

        def batch_del_op():
            async def _del_prepare():
                keys = [f"delbatch_{counter[0]}_{i}" for i in range(100)]
                await async_db_instance.abatch_update({k: {"v": 1} for k in keys})
                await async_db_instance.abatch_delete(keys)
                counter[0] += 1

            run_async(_del_prepare())

        benchmark(batch_del_op)


# ==================== Async Concurrency Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestAsyncConcurrencyBenchmarks:
    """非同期並行処理のベンチマーク"""

    def test_async_concurrent_reads_10(self, benchmark, db_path):
        """並行読み込み（10件同時）"""
        from nanasqlite import AsyncNanaSQLite

        # データ準備
        async def setup():
            async with AsyncNanaSQLite(db_path) as db:
                await db.batch_update({f"key_{i}": {"index": i} for i in range(100)})

        run_async(setup())

        def concurrent_reads():
            async def _reads():
                async with AsyncNanaSQLite(db_path) as db:
                    tasks = [db.aget(f"key_{i}") for i in range(10)]
                    return await asyncio.gather(*tasks)

            return run_async(_reads())

        benchmark(concurrent_reads)

    def test_async_concurrent_reads_100(self, benchmark, db_path):
        """並行読み込み（100件同時）"""
        from nanasqlite import AsyncNanaSQLite

        # データ準備
        async def setup():
            async with AsyncNanaSQLite(db_path) as db:
                await db.batch_update({f"key_{i}": {"index": i} for i in range(100)})

        run_async(setup())

        def concurrent_reads():
            async def _reads():
                async with AsyncNanaSQLite(db_path) as db:
                    tasks = [db.aget(f"key_{i}") for i in range(100)]
                    return await asyncio.gather(*tasks)

            return run_async(_reads())

        benchmark(concurrent_reads)

    def test_async_concurrent_writes_10(self, benchmark, db_path):
        """並行書き込み（10件同時）"""
        from nanasqlite import AsyncNanaSQLite

        counter = [0]

        def concurrent_writes():
            async def _writes():
                async with AsyncNanaSQLite(db_path) as db:
                    base = counter[0] * 10
                    tasks = [db.aset(f"cw_{base + i}", {"value": i}) for i in range(10)]
                    await asyncio.gather(*tasks)
                    counter[0] += 1

            run_async(_writes())

        benchmark(concurrent_writes)

    def test_async_concurrent_writes_100(self, benchmark, db_path):
        """並行書き込み（100件同時）"""
        from nanasqlite import AsyncNanaSQLite

        counter = [0]

        def concurrent_writes():
            async def _writes():
                async with AsyncNanaSQLite(db_path) as db:
                    base = counter[0] * 100
                    tasks = [db.aset(f"cw_{base + i}", {"value": i}) for i in range(100)]
                    await asyncio.gather(*tasks)
                    counter[0] += 1

            run_async(_writes())

        benchmark(concurrent_writes)

    def test_async_concurrent_mixed_50(self, benchmark, db_path):
        """並行混合操作（読み書き各25件）"""
        from nanasqlite import AsyncNanaSQLite

        # データ準備
        async def setup():
            async with AsyncNanaSQLite(db_path) as db:
                await db.batch_update({f"read_key_{i}": {"index": i} for i in range(25)})

        run_async(setup())

        counter = [0]

        def concurrent_mixed():
            async def _mixed():
                async with AsyncNanaSQLite(db_path) as db:
                    base = counter[0] * 25
                    read_tasks = [db.aget(f"read_key_{i}") for i in range(25)]
                    write_tasks = [db.aset(f"write_key_{base + i}", {"value": i}) for i in range(25)]
                    await asyncio.gather(*(read_tasks + write_tasks))
                    counter[0] += 1

            run_async(_mixed())

        benchmark(concurrent_mixed)


# ==================== Async SQL Operations Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestAsyncSQLOperationsBenchmarks:
    """非同期SQL操作のベンチマーク"""

    def test_async_create_table(self, benchmark, db_path):
        """非同期テーブル作成"""
        from nanasqlite import AsyncNanaSQLite

        counter = [0]

        def create_table():
            async def _create():
                async with AsyncNanaSQLite(db_path) as db:
                    await db.create_table(
                        f"test_table_{counter[0]}", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"}
                    )
                    counter[0] += 1

            run_async(_create())

        benchmark(create_table)

    def test_async_sql_insert(self, benchmark, db_path):
        """非同期SQL INSERT"""
        from nanasqlite import AsyncNanaSQLite

        # テーブル作成
        async def setup():
            async with AsyncNanaSQLite(db_path) as db:
                await db.create_table(
                    "users", {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "name": "TEXT", "age": "INTEGER"}
                )

        run_async(setup())

        counter = [0]

        def insert_single():
            async def _insert():
                async with AsyncNanaSQLite(db_path) as db:
                    await db.sql_insert("users", {"name": f"User{counter[0]}", "age": 25})
                    counter[0] += 1

            run_async(_insert())

        benchmark(insert_single)

    def test_async_sql_update(self, benchmark, async_db_instance):
        """非同期SQL UPDATE"""

        # データ準備
        async def setup():
            await async_db_instance.create_table("users_upd", {"id": "INTEGER", "name": "TEXT", "age": "INTEGER"})
            for i in range(100):
                await async_db_instance.sql_insert("users_upd", {"id": i, "name": f"User{i}", "age": 25})

        run_async(setup())

        counter = [0]

        def update_single():
            async def _update():
                await async_db_instance.sql_update("users_upd", {"age": 26}, "id = ?", (counter[0] % 100,))
                counter[0] += 1

            run_async(_update())

        benchmark(update_single)

    def test_async_sql_delete(self, benchmark, async_db_instance):
        """非同期SQL DELETE"""
        counter = [0]

        def delete_op():
            async def _delete():
                # テーブル作成はこの操作に含まれても良いとするが、
                # 削除そのものを測るならテーブル作成は外出しした方が良い。
                # しかし動的にテーブル名を変えないと前回の残りがある。
                table = f"del_test_{counter[0]}"
                await async_db_instance.create_table(table, {"id": "INTEGER", "name": "TEXT"})
                await async_db_instance.sql_insert(table, {"id": 1, "name": "Test"})
                await async_db_instance.sql_delete(table, "id = ?", (1,))
                counter[0] += 1

            run_async(_delete())

        benchmark(delete_op)

    def test_async_query_simple(self, benchmark, async_db_instance):
        """非同期シンプルクエリ"""

        # データ準備
        async def setup():
            await async_db_instance.create_table("items_q", {"id": "INTEGER", "name": "TEXT", "value": "INTEGER"})
            data = [{"id": i, "name": f"Item{i}", "value": i % 100} for i in range(1000)]
            # batch_updateはdict用なのでSQLテーブルには直接使えないかもしれないが、
            # queryのテストなので準備は一括で行いたい。
            for i in range(1000):
                await async_db_instance.sql_insert("items_q", data[i])

        run_async(setup())

        def query_simple():
            async def _query():
                return await async_db_instance.query(
                    "items_q", columns=["id", "name"], where="value > ?", parameters=(50,), limit=10
                )

            return run_async(_query())

        benchmark(query_simple)

    def test_async_fetch_one(self, benchmark, db_path):
        """非同期fetch_one"""
        from nanasqlite import AsyncNanaSQLite

        # データ準備
        async def setup():
            async with AsyncNanaSQLite(db_path) as db:
                await db.create_table("items", {"id": "INTEGER", "value": "TEXT"})
                for i in range(1000):
                    await db.sql_insert("items", {"id": i, "value": f"data{i}"})

        run_async(setup())

        def fetch_one():
            async def _fetch():
                async with AsyncNanaSQLite(db_path) as db:
                    return await db.fetch_one("SELECT * FROM items WHERE id = ?", (500,))

            return run_async(_fetch())

        benchmark(fetch_one)

    def test_async_fetch_all_1000(self, benchmark, db_path):
        """非同期fetch_all（1000件）"""
        from nanasqlite import AsyncNanaSQLite

        # データ準備
        async def setup():
            async with AsyncNanaSQLite(db_path) as db:
                await db.create_table("items", {"id": "INTEGER", "value": "TEXT"})
                for i in range(1000):
                    await db.sql_insert("items", {"id": i, "value": f"data{i}"})

        run_async(setup())

        def fetch_all():
            async def _fetch():
                async with AsyncNanaSQLite(db_path) as db:
                    return await db.fetch_all("SELECT * FROM items")

            return run_async(_fetch())

        benchmark(fetch_all)

    def test_async_execute_raw(self, benchmark, db_path):
        """非同期直接SQL実行"""
        from nanasqlite import AsyncNanaSQLite

        async def setup():
            async with AsyncNanaSQLite(db_path) as db:
                await db.create_table("exec_test", {"id": "INTEGER", "value": "TEXT"})

        run_async(setup())

        counter = [0]

        def execute_raw():
            async def _exec():
                async with AsyncNanaSQLite(db_path) as db:
                    await db.execute(
                        "INSERT INTO exec_test (id, value) VALUES (?, ?)", (counter[0], f"val{counter[0]}")
                    )
                    counter[0] += 1

            run_async(_exec())

        benchmark(execute_raw)


# ==================== Async Schema Operations Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestAsyncSchemaOperationsBenchmarks:
    """非同期スキーマ操作のベンチマーク"""

    def test_async_table_exists(self, benchmark, db_path):
        """非同期テーブル存在確認"""
        from nanasqlite import AsyncNanaSQLite

        async def setup():
            async with AsyncNanaSQLite(db_path) as db:
                await db.create_table("exists_test", {"id": "INTEGER"})

        run_async(setup())

        def table_exists():
            async def _exists():
                async with AsyncNanaSQLite(db_path) as db:
                    return await db.table_exists("exists_test")

            return run_async(_exists())

        benchmark(table_exists)

    def test_async_list_tables(self, benchmark, db_path):
        """非同期テーブル一覧取得"""
        from nanasqlite import AsyncNanaSQLite

        async def setup():
            async with AsyncNanaSQLite(db_path) as db:
                for i in range(20):
                    await db.create_table(f"list_test_{i}", {"id": "INTEGER"})

        run_async(setup())

        def list_tables():
            async def _list():
                async with AsyncNanaSQLite(db_path) as db:
                    return await db.list_tables()

            return run_async(_list())

        benchmark(list_tables)

    def test_async_create_index(self, benchmark, db_path):
        """非同期インデックス作成"""
        from nanasqlite import AsyncNanaSQLite

        counter = [0]

        def create_index():
            async def _create():
                async with AsyncNanaSQLite(db_path) as db:
                    await db.create_table(f"idx_test_{counter[0]}", {"id": "INTEGER", "name": "TEXT"})
                    await db.create_index(f"idx_{counter[0]}", f"idx_test_{counter[0]}", ["name"])
                    counter[0] += 1

            run_async(_create())

        benchmark(create_index)

    def test_async_drop_table(self, benchmark, db_path):
        """非同期テーブル削除"""
        from nanasqlite import AsyncNanaSQLite

        counter = [0]

        def drop_table():
            async def _drop():
                async with AsyncNanaSQLite(db_path) as db:
                    table_name = f"drop_test_{counter[0]}"
                    await db.create_table(table_name, {"id": "INTEGER"})
                    await db.drop_table(table_name)
                    counter[0] += 1

            run_async(_drop())

        benchmark(drop_table)


# ==================== Async Batch Operations Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestAsyncBatchOperationsBenchmarks:
    """非同期バッチ操作のベンチマーク"""

    def test_async_batch_delete_100(self, benchmark, db_path):
        """非同期バッチ削除（100件）"""
        from nanasqlite import AsyncNanaSQLite

        counter = [0]

        def batch_delete():
            async def _delete():
                async with AsyncNanaSQLite(db_path) as db:
                    keys = [f"bd_{counter[0]}_{i}" for i in range(100)]
                    await db.batch_update({k: {"value": i} for i, k in enumerate(keys)})
                    await db.batch_delete(keys)
                    counter[0] += 1

            run_async(_delete())

        benchmark(batch_delete)

    def test_async_update_dict(self, benchmark, db_path):
        """非同期update()複数キー更新"""
        from nanasqlite import AsyncNanaSQLite

        counter = [0]

        def update_op():
            async def _update():
                async with AsyncNanaSQLite(db_path) as db:
                    await db.aupdate({f"up_{counter[0]}_{i}": f"value_{i}" for i in range(50)})
                    counter[0] += 1

            run_async(_update())

        benchmark(update_op)

    def test_async_clear(self, benchmark, db_path):
        """非同期clear()全削除"""
        from nanasqlite import AsyncNanaSQLite

        counter = [0]

        def clear_op():
            async def _clear():
                async with AsyncNanaSQLite(db_path) as db:
                    await db.batch_update({f"clear_{counter[0]}_{i}": {"v": i} for i in range(100)})
                    await db.aclear()
                    counter[0] += 1

            run_async(_clear())

        benchmark(clear_op)


# ==================== Async Pydantic Operations Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestAsyncPydanticOperationsBenchmarks:
    """非同期Pydantic操作のベンチマーク"""

    def test_async_set_model(self, benchmark, db_path):
        """非同期set_model()モデル保存"""
        try:
            from pydantic import BaseModel
        except ImportError:
            pytest.skip("pydantic not installed")

        from nanasqlite import AsyncNanaSQLite

        class TestUser(BaseModel):
            name: str
            age: int
            email: str

        counter = [0]

        def set_model():
            async def _set():
                async with AsyncNanaSQLite(db_path) as db:
                    user = TestUser(name=f"User{counter[0]}", age=25, email=f"user{counter[0]}@example.com")
                    await db.set_model(f"user_{counter[0]}", user)
                    counter[0] += 1

            run_async(_set())

        benchmark(set_model)

    def test_async_get_model(self, benchmark, db_path):
        """非同期get_model()モデル取得"""
        try:
            from pydantic import BaseModel
        except ImportError:
            pytest.skip("pydantic not installed")

        from nanasqlite import AsyncNanaSQLite

        class TestUser(BaseModel):
            name: str
            age: int
            email: str

        # 事前にモデルを保存
        async def setup():
            async with AsyncNanaSQLite(db_path) as db:
                for i in range(100):
                    user = TestUser(name=f"User{i}", age=25, email=f"user{i}@example.com")
                    await db.set_model(f"model_user_{i}", user)

        run_async(setup())

        counter = [0]

        def get_model():
            async def _get():
                async with AsyncNanaSQLite(db_path) as db:
                    result = await db.get_model(f"model_user_{counter[0] % 100}", TestUser)
                    counter[0] += 1
                    return result

            return run_async(_get())

        benchmark(get_model)


# ==================== Async Utility Operations Benchmarks ====================


@pytest.mark.skipif(not pytest_benchmark_available, reason="pytest-benchmark not installed")
class TestAsyncUtilityOperationsBenchmarks:
    """非同期ユーティリティ操作のベンチマーク"""

    def test_async_vacuum(self, benchmark, async_db_instance):
        """非同期vacuum()最適化"""

        async def setup():
            for i in range(100):
                await async_db_instance.aset(f"vac_key_{i}", {"data": "x" * 100})
            for i in range(100):
                await async_db_instance.adelete(f"vac_key_{i}")

        run_async(setup())

        def vacuum_op():
            async def _vacuum():
                await async_db_instance.vacuum()

            run_async(_vacuum())

        benchmark(vacuum_op)

    def test_async_refresh_all(self, benchmark, async_db_with_data_instance):
        """非同期refresh()全件"""

        def refresh_op():
            async def _refresh():
                await async_db_with_data_instance.arefresh()

            run_async(_refresh())

        benchmark(refresh_op)

    def test_async_load_all(self, benchmark, async_db_instance):
        """非同期load_all()一括ロード"""

        async def setup():
            await async_db_instance.abatch_update({f"load_key_{i}": {"index": i} for i in range(1000)})

        run_async(setup())

        def load_all():
            async def _load():
                await async_db_instance.aload_all()

            run_async(_load())

        benchmark(load_all)

    def test_async_copy(self, benchmark, async_db_with_data_instance):
        """非同期copy()浅いコピー"""

        def copy_op():
            async def _copy():
                return await async_db_with_data_instance.copy()

            return run_async(_copy())

        benchmark(copy_op)

    def test_async_is_cached(self, benchmark, async_db_with_data_instance):
        """非同期is_cached()"""
        # 初回アクセスしてキャッシュさせる
        run_async(async_db_with_data_instance.aget("key_0"))

        def is_cached_op():
            async def _check():
                return await async_db_with_data_instance.is_cached("key_0")

            return run_async(_check())

        benchmark(is_cached_op)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
