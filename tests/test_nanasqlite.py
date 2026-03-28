"""
NanaSQLite 強化テストスイート

- 応答データの詳細検証
- ネスト構造テスト（1〜30階層）
- データ型の厳密な検証
- エッジケースのテスト
"""

import os
import sys
import tempfile
import time

import pytest

# テスト実行時のパス設定
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from nanasqlite import NanaSQLite

# ==================== Fixtures ====================


@pytest.fixture
def db_path():
    """一時DBパスを提供"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test.db")


@pytest.fixture
def db(db_path):
    """NanaSQLiteインスタンスを提供"""
    database = NanaSQLite(db_path)
    yield database
    database.close()


# ==================== 基本操作テスト ====================


class TestBasicOperations:
    """基本的な操作のテスト"""

    def test_set_and_get_string(self, db):
        """文字列の設定と取得"""
        db["name"] = "Nana"
        result = db["name"]

        assert result == "Nana"
        assert isinstance(result, str)
        assert len(result) == 4

    def test_set_and_get_integer(self, db):
        """整数の設定と取得"""
        db["age"] = 20
        result = db["age"]

        assert result == 20
        assert isinstance(result, int)
        assert result > 0

    def test_set_and_get_float(self, db):
        """浮動小数点の設定と取得"""
        db["pi"] = 3.14159
        result = db["pi"]

        assert result == 3.14159
        assert isinstance(result, float)
        assert 3.14 < result < 3.15

    def test_set_and_get_boolean(self, db):
        """ブール値の設定と取得"""
        db["active"] = True
        db["deleted"] = False

        assert db["active"] is True
        assert db["deleted"] is False
        assert isinstance(db["active"], bool)
        assert isinstance(db["deleted"], bool)

    def test_set_and_get_none(self, db):
        """None値の設定と取得"""
        db["empty"] = None
        result = db["empty"]

        assert result is None

    def test_set_and_get_list(self, db):
        """リストの設定と取得"""
        original = [1, 2, 3, "four", 5.0, None, True]
        db["list"] = original
        result = db["list"]

        assert result == original
        assert isinstance(result, list)
        assert len(result) == 7
        assert result[0] == 1
        assert result[3] == "four"
        assert result[5] is None
        assert result[6] is True

    def test_set_and_get_dict(self, db):
        """辞書の設定と取得"""
        original = {"name": "Nana", "age": 20, "active": True}
        db["user"] = original
        result = db["user"]

        assert result == original
        assert isinstance(result, dict)
        assert len(result) == 3
        assert result["name"] == "Nana"
        assert result["age"] == 20
        assert result["active"] is True

    def test_contains(self, db):
        """キーの存在確認"""
        db["exists"] = "value"

        assert "exists" in db
        assert "not_exists" not in db

    def test_len(self, db):
        """長さの確認"""
        assert len(db) == 0

        db["a"] = 1
        assert len(db) == 1

        db["b"] = 2
        db["c"] = 3
        assert len(db) == 3

    def test_delete(self, db):
        """削除操作"""
        db["to_delete"] = "value"
        assert "to_delete" in db

        del db["to_delete"]
        assert "to_delete" not in db

    def test_delete_nonexistent_raises_keyerror(self, db):
        """存在しないキーの削除でKeyError"""
        with pytest.raises(KeyError):
            del db["nonexistent"]

    def test_get_nonexistent_raises_keyerror(self, db):
        """存在しないキーの取得でKeyError"""
        with pytest.raises(KeyError):
            _ = db["nonexistent"]

    def test_extract_column_aliases(self):
        """内部メソッド _extract_column_aliases のテスト"""
        # Note: _extract_column_aliases is a staticmethod
        columns = [
            "id",
            "name AS user_name",
            "age as user_age",
            "data  AS  info",
            "count",
            '"quoted" AS "alias"',
            "'quoted_single' as 'alias_single'",
        ]
        expected = ["id", "user_name", "user_age", "info", "count", "alias", "alias_single"]
        # Accessing private member for testing purposes
        # pylint: disable=protected-access
        result = NanaSQLite._extract_column_aliases(columns)
        assert result == expected


# ==================== ネスト構造テスト ====================


class TestNestedStructures:
    """ネストしたデータ構造のテスト（1〜30階層）"""

    def _create_nested_dict(self, depth: int) -> dict:
        """指定階層のネストしたdictを作成"""
        if depth <= 0:
            return {"leaf": "value", "number": depth}
        return {"level": depth, "child": self._create_nested_dict(depth - 1)}

    def _verify_nested_dict(self, data: dict, expected_depth: int) -> bool:
        """ネストしたdictの構造を検証"""
        if expected_depth <= 0:
            return data == {"leaf": "value", "number": 0}

        assert "level" in data, f"Missing 'level' at depth {expected_depth}"
        assert data["level"] == expected_depth, f"Wrong level value at depth {expected_depth}"
        assert "child" in data, f"Missing 'child' at depth {expected_depth}"
        assert isinstance(data["child"], dict), f"Child is not dict at depth {expected_depth}"

        return self._verify_nested_dict(data["child"], expected_depth - 1)

    @pytest.mark.parametrize("depth", range(1, 31))
    def test_nested_dict_depth(self, db, depth):
        """階層ごとのネストしたdictのテスト（1〜30階層）"""
        # 作成
        original = self._create_nested_dict(depth)
        key = f"nested_{depth}"

        # 保存
        db[key] = original

        # 取得
        result = db[key]

        # 検証: 完全一致
        assert result == original, f"Mismatch at depth {depth}"

        # 検証: 構造確認
        assert self._verify_nested_dict(result, depth)

    def test_deeply_nested_list(self, db):
        """深くネストしたリストのテスト"""
        # 30階層のネストしたリスト
        nested = "deepest"
        for i in range(30):
            nested = [nested, i]

        db["nested_list"] = nested
        result = db["nested_list"]

        assert result == nested

        # 構造確認
        current = result
        for i in range(29, -1, -1):
            assert isinstance(current, list)
            assert len(current) == 2
            assert current[1] == i
            current = current[0]

        assert current == "deepest"

    def test_mixed_nested_structure(self, db):
        """混合ネスト構造（dict + list）のテスト"""
        original = {
            "users": [
                {
                    "name": "Alice",
                    "friends": ["Bob", "Charlie"],
                    "metadata": {
                        "created": "2024-01-01",
                        "tags": ["admin", "active"],
                        "settings": {
                            "theme": "dark",
                            "notifications": {"email": True, "push": False, "preferences": [1, 2, 3]},
                        },
                    },
                },
                {"name": "Bob", "friends": [], "metadata": None},
            ],
            "count": 2,
            "version": 1.5,
        }

        db["complex"] = original
        result = db["complex"]

        # 完全一致
        assert result == original

        # 詳細検証
        assert isinstance(result["users"], list)
        assert len(result["users"]) == 2

        alice = result["users"][0]
        assert alice["name"] == "Alice"
        assert alice["friends"] == ["Bob", "Charlie"]
        assert alice["metadata"]["settings"]["notifications"]["email"] is True
        assert alice["metadata"]["settings"]["notifications"]["preferences"] == [1, 2, 3]

        bob = result["users"][1]
        assert bob["name"] == "Bob"
        assert bob["friends"] == []
        assert bob["metadata"] is None


# ==================== 永続化テスト ====================


class TestPersistence:
    """永続化の詳細テスト"""

    def test_persistence_after_close(self, db_path):
        """closeした後もデータが永続化されている"""
        # 書き込み
        db1 = NanaSQLite(db_path)
        db1["persistent"] = {"message": "Hello, SQLite!", "count": 42}
        db1.close()

        # 再度開く
        db2 = NanaSQLite(db_path)
        result = db2["persistent"]

        assert result["message"] == "Hello, SQLite!"
        assert result["count"] == 42
        assert isinstance(result["count"], int)

        db2.close()

    def test_persistence_multiple_keys(self, db_path):
        """複数キーの永続化"""
        # 書き込み
        db1 = NanaSQLite(db_path)
        for i in range(100):
            db1[f"key_{i}"] = {"index": i, "square": i * i}
        db1.close()

        # 検証
        db2 = NanaSQLite(db_path)
        assert len(db2) == 100

        for i in range(100):
            result = db2[f"key_{i}"]
            assert result["index"] == i
            assert result["square"] == i * i

        db2.close()

    def test_persistence_with_updates(self, db_path):
        """更新後の永続化"""
        # 初期書き込み
        db1 = NanaSQLite(db_path)
        db1["data"] = {"version": 1, "value": "original"}
        db1.close()

        # 更新
        db2 = NanaSQLite(db_path)
        db2["data"] = {"version": 2, "value": "updated"}
        db2.close()

        # 検証
        db3 = NanaSQLite(db_path)
        result = db3["data"]

        assert result["version"] == 2
        assert result["value"] == "updated"

        db3.close()


# ==================== キャッシュ動作テスト ====================


class TestCacheBehavior:
    """キャッシュ動作の詳細テスト"""

    def test_lazy_load_behavior(self, db_path):
        """遅延ロードの動作確認"""
        # データ作成
        db1 = NanaSQLite(db_path)
        db1["key1"] = "value1"
        db1["key2"] = "value2"
        db1["key3"] = "value3"
        db1.close()

        # 遅延ロードで開く
        db2 = NanaSQLite(db_path, bulk_load=False)

        # 初期状態: 全てキャッシュされていない
        assert not db2.is_cached("key1")
        assert not db2.is_cached("key2")
        assert not db2.is_cached("key3")

        # key1にアクセス
        _ = db2["key1"]

        # key1のみキャッシュ済み
        assert db2.is_cached("key1")
        assert not db2.is_cached("key2")
        assert not db2.is_cached("key3")

        db2.close()

    def test_bulk_load_behavior(self, db_path):
        """一括ロードの動作確認"""
        # データ作成
        db1 = NanaSQLite(db_path)
        for i in range(50):
            db1[f"key_{i}"] = f"value_{i}"
        db1.close()

        # 一括ロードで開く
        db2 = NanaSQLite(db_path, bulk_load=True)

        # 全てキャッシュ済み
        for i in range(50):
            assert db2.is_cached(f"key_{i}"), f"key_{i} should be cached"

        db2.close()

    def test_refresh_single_key(self, db_path):
        """単一キーのリフレッシュ"""
        with NanaSQLite(db_path) as db:
            db["key1"] = "value1"

            # キャッシュ済み
            assert db.is_cached("key1")

            # リフレッシュ
            db.refresh("key1")

            # 再度アクセスでキャッシュ
            _ = db["key1"]
            assert db.is_cached("key1")

    def test_refresh_all(self, db_path):
        """全キャッシュのリフレッシュ"""
        db = NanaSQLite(db_path)
        db["k"] = "v"
        assert db.is_cached("k")

        # 全リフレッシュ
        db.refresh()

        # キャッシュがクリアされていること
        assert not db.is_cached("k")

        # 再取得可能
        assert db["k"] == "v"
        db.close()

    def test_get_fresh_after_direct_update(self, db_path):
        """get_freshでDB直接変更後のキャッシュ同期"""
        import json

        db = NanaSQLite(db_path)
        db["key"] = "original_value"

        # キャッシュされていることを確認
        assert db.is_cached("key")
        cached_value = db["key"]
        assert cached_value == "original_value"

        # execute()で直接DBを変更（キャッシュは更新されない）
        new_value = json.dumps("updated_value")
        db.execute(f"UPDATE {db._safe_table} SET value = ? WHERE key = ?", (new_value, "key"))

        # 通常のget()はキャッシュから古い値を返す
        assert db.get("key") == "original_value"

        # get_fresh()はDBから最新を取得しキャッシュを更新
        fresh_value = db.get_fresh("key")
        assert fresh_value == "updated_value"

        # 以降のアクセスも更新された値を返す
        assert db["key"] == "updated_value"

        db.close()

    def test_get_fresh_nonexistent_key(self, db_path):
        """get_freshで存在しないキーにdefaultを返す"""
        db = NanaSQLite(db_path)

        # 存在しないキー
        result = db.get_fresh("nonexistent")
        assert result is None

        # デフォルト値
        result = db.get_fresh("nonexistent", "default_value")
        assert result == "default_value"

        db.close()

    def test_get_fresh_after_delete(self, db_path):
        """get_freshで削除されたキーを検出"""

        db = NanaSQLite(db_path)
        db["to_delete"] = "value"
        assert db.is_cached("to_delete")

        # execute()で直接削除
        db.execute(f"DELETE FROM {db._safe_table} WHERE key = ?", ("to_delete",))

        # 通常のget()はまだキャッシュから返す
        assert db.get("to_delete") == "value"

        # get_fresh()はDBから最新を取得（削除されているのでdefault）
        result = db.get_fresh("to_delete", "deleted")
        assert result == "deleted"

        db.close()


# ==================== dictメソッドテスト ====================


class TestDictMethods:
    """dictメソッドの詳細テスト"""

    def test_keys(self, db):
        """keysメソッドの検証"""
        db["a"] = 1
        db["b"] = 2
        db["c"] = 3

        keys = db.keys()

        assert isinstance(keys, list)
        assert set(keys) == {"a", "b", "c"}
        assert len(keys) == 3

    def test_values(self, db):
        """valuesメソッドの検証"""
        db["a"] = {"x": 1}
        db["b"] = {"y": 2}
        db["c"] = {"z": 3}

        values = db.values()

        assert isinstance(values, list)
        assert len(values) == 3
        assert {"x": 1} in values
        assert {"y": 2} in values
        assert {"z": 3} in values

    def test_items(self, db):
        """itemsメソッドの検証"""
        db["key1"] = "value1"
        db["key2"] = "value2"

        items = db.items()

        assert isinstance(items, list)
        assert len(items) == 2

        items_dict = dict(items)
        assert items_dict == {"key1": "value1", "key2": "value2"}

    def test_get_with_default(self, db):
        """getメソッドのデフォルト値"""
        db["exists"] = "value"

        assert db.get("exists") == "value"
        assert db.get("not_exists") is None
        assert db.get("not_exists", "default") == "default"
        assert db.get("not_exists", 42) == 42

    def test_pop(self, db):
        """popメソッドの検証"""
        db["to_pop"] = {"data": "important"}

        result = db.pop("to_pop")

        assert result == {"data": "important"}
        assert "to_pop" not in db

    def test_pop_with_default(self, db):
        """popメソッドのデフォルト値"""
        result = db.pop("not_exists", "default")
        assert result == "default"

    def test_pop_nonexistent_raises_keyerror(self, db):
        """存在しないキーのpopでKeyError"""
        with pytest.raises(KeyError):
            db.pop("nonexistent")

    def test_update_from_dict(self, db):
        """updateメソッド（dictから）"""
        db.update({"a": 1, "b": 2, "c": 3})

        assert db["a"] == 1
        assert db["b"] == 2
        assert db["c"] == 3
        assert len(db) == 3

    def test_update_from_kwargs(self, db):
        """updateメソッド（kwargsから）"""
        db.update(x=10, y=20, z=30)

        assert db["x"] == 10
        assert db["y"] == 20
        assert db["z"] == 30

    def test_setdefault(self, db):
        """setdefaultメソッドの検証"""
        # 新規キー
        result1 = db.setdefault("new_key", "default_value")
        assert result1 == "default_value"
        assert db["new_key"] == "default_value"

        # 既存キー（上書きされない）
        result2 = db.setdefault("new_key", "other_value")
        assert result2 == "default_value"
        assert db["new_key"] == "default_value"

    def test_clear(self, db):
        """clearメソッドの検証"""
        db["a"] = 1
        db["b"] = 2
        db["c"] = 3

        assert len(db) == 3

        db.clear()

        assert len(db) == 0
        assert "a" not in db
        assert "b" not in db
        assert "c" not in db

    def test_to_dict(self, db):
        """to_dictメソッドの検証"""
        db["x"] = {"nested": True}
        db["y"] = [1, 2, 3]

        result = db.to_dict()

        assert isinstance(result, dict)
        assert result == {"x": {"nested": True}, "y": [1, 2, 3]}


class TestStandardCompatibility:
    """標準dict機能との互換性テスト"""

    def test_popitem(self, db):
        """popitemの動作検証"""
        db["a"] = 1
        db["b"] = 2

        item = db.popitem()
        assert item in [("a", 1), ("b", 2)]
        assert len(db) == 1

        db.popitem()
        assert len(db) == 0

        with pytest.raises(KeyError):
            db.popitem()

    def test_copy(self, db):
        """copyの動作検証"""
        db["a"] = 1
        copied = db.copy()

        assert isinstance(copied, dict)
        assert copied == {"a": 1}
        assert copied is not db

        # 構造の変更が波及しないこと
        copied["b"] = 2
        assert "b" not in db

    def test_equality(self, db):
        """等価比較の検証"""
        db["a"] = 1
        assert db == {"a": 1}
        assert {"a": 1} == db
        assert db != {"a": 2}

    def test_equality_closed_connection(self, db):
        """閉じられた接続での等価比較はNanaSQLiteClosedErrorを発生させる"""
        from nanasqlite import NanaSQLiteClosedError

        db["a"] = 1
        db.close()

        # Closed connection should raise NanaSQLiteClosedError on equality check
        with pytest.raises(NanaSQLiteClosedError):
            _ = db == {"a": 1}


# ==================== バッチ操作テスト ====================


class TestBatchOperations:
    """バッチ操作のテスト"""

    def test_batch_update(self, db):
        """batch_updateの検証"""
        data = {f"key_{i}": {"index": i, "value": f"value_{i}"} for i in range(100)}

        db.batch_update(data)

        assert len(db) == 100

        for i in range(100):
            result = db[f"key_{i}"]
            assert result["index"] == i
            assert result["value"] == f"value_{i}"

    def test_batch_delete(self, db):
        """batch_deleteの検証"""
        # 準備
        for i in range(50):
            db[f"key_{i}"] = f"value_{i}"

        assert len(db) == 50

        # 半分を削除
        keys_to_delete = [f"key_{i}" for i in range(25)]
        db.batch_delete(keys_to_delete)

        assert len(db) == 25

        for i in range(25):
            assert f"key_{i}" not in db

        for i in range(25, 50):
            assert f"key_{i}" in db

    def test_batch_get(self, db):
        """batch_getの検証"""
        data = {f"k{i}": i for i in range(10)}
        db.batch_update(data)

        keys = ["k0", "k2", "k5", "nonexistent"]
        result = db.batch_get(keys)

        assert result["k0"] == 0
        assert result["k2"] == 2
        assert result["k5"] == 5
        assert "nonexistent" not in result
        assert len(result) == 3


# ==================== パフォーマンステスト ====================


class TestPerformance:
    """パフォーマンスのテスト"""

    def test_bulk_vs_lazy_load_performance(self, db_path):
        """Bulk Load vs Lazy Loadのパフォーマンス比較"""
        n = 500

        # データ作成
        db = NanaSQLite(db_path)
        db.batch_update({f"key_{i}": {"data": "x" * 100, "index": i} for i in range(n)})
        db.close()

        # Lazy Load
        start = time.perf_counter()
        db_lazy = NanaSQLite(db_path, bulk_load=False)
        lazy_init = time.perf_counter() - start

        start = time.perf_counter()
        for i in range(n):
            _ = db_lazy[f"key_{i}"]
        lazy_access = time.perf_counter() - start
        db_lazy.close()

        # Bulk Load
        start = time.perf_counter()
        db_bulk = NanaSQLite(db_path, bulk_load=True)
        bulk_init = time.perf_counter() - start

        start = time.perf_counter()
        for i in range(n):
            _ = db_bulk[f"key_{i}"]
        bulk_access = time.perf_counter() - start
        db_bulk.close()

        print(f"\n  [Performance] n={n}")
        print(f"  Lazy: init={lazy_init * 1000:.2f}ms, access={lazy_access * 1000:.2f}ms")
        print(f"  Bulk: init={bulk_init * 1000:.2f}ms, access={bulk_access * 1000:.2f}ms")

        # Bulk Loadのアクセスは高速であるべき
        assert bulk_access < lazy_access


# ==================== エッジケーステスト ====================


class TestEdgeCases:
    """エッジケースのテスト"""

    def test_empty_string_key(self, db):
        """空文字列のキー"""
        db[""] = "empty_key_value"

        assert db[""] == "empty_key_value"
        assert "" in db

    def test_unicode_key_and_value(self, db):
        """Unicodeのキーと値"""
        db["日本語キー"] = {"メッセージ": "こんにちは世界", "絵文字": "🎉🚀"}

        result = db["日本語キー"]

        assert result["メッセージ"] == "こんにちは世界"
        assert result["絵文字"] == "🎉🚀"

    def test_special_characters_in_key(self, db):
        """特殊文字を含むキー"""
        special_keys = [
            "key with spaces",
            "key\twith\ttabs",
            "key\nwith\nnewlines",
            "key'with'quotes",
            'key"with"doublequotes',
            "key\\with\\backslashes",
        ]

        for key in special_keys:
            db[key] = f"value_for_{key}"

        for key in special_keys:
            assert key in db
            assert db[key] == f"value_for_{key}"

    def test_large_value(self, db):
        """大きな値"""
        large_data = {
            "big_string": "x" * 100000,
            "big_list": list(range(10000)),
        }

        db["large"] = large_data
        result = db["large"]

        assert len(result["big_string"]) == 100000
        assert len(result["big_list"]) == 10000
        assert result["big_list"][9999] == 9999

    def test_context_manager(self, db_path):
        """コンテキストマネージャの動作"""
        with NanaSQLite(db_path) as db:
            db["test"] = "value"
            assert db["test"] == "value"

        # 閉じた後でも永続化されている
        db2 = NanaSQLite(db_path)
        assert db2["test"] == "value"
        db2.close()


# ==================== 実行用 ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
