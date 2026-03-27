"""
v1.5.0dev1機能解説: 02. 標準制約フック (Standard Constraints)

NanaSQLite v1.5.0dev1 では、よく使われる RDBMS 的な制約を
簡単に実装できる組み込みフッククラスが導入されました。

◆ このサンプルで学べること
1. `CheckHook`: シンプルな条件チェック
2. `UniqueHook`: 重複禁止（ユニーク制約）
3. `ForeignKeyHook`: 他テーブルのキー参照（外部キー制約）
"""

from typing import Any
from nanasqlite import NanaSQLite
from nanasqlite.hooks import CheckHook, UniqueHook, ForeignKeyHook
from nanasqlite.exceptions import NanaSQLiteValidationError

def main():
    print("--- 02. 標準制約フック (Standard Constraints) ---")

    db = NanaSQLite(":memory:")
    
    # ==============================================================================
    # 1. CheckHook の使用例 (age は 0 以上)
    # ==============================================================================
    print("\n[Case 1: CheckHook]")
    def is_valid_age(key: str, value: Any) -> bool:
        if isinstance(value, dict) and "age" in value:
            return value["age"] >= 0
        return True

    db.add_hook(CheckHook(is_valid_age, "年齢(age)は0以上である必要があります"))

    # 不正なデータをテスト
    try:
        db["user:1"] = {"name": "Alice", "age": -5}
    except NanaSQLiteValidationError as e:
        print(f"-> [FAIL] 制約違反ブロック成功: {e}")

    # 正常なデータは保存できる
    db["user:1"] = {"name": "Alice", "age": 20, "email": "alice@example.com"}
    print(f"-> [OK] 正常なデータを保存しました: {db['user:1']}")


    # ==============================================================================
    # 2. UniqueHook の使用例 (email の重複禁止)
    # ==============================================================================
    print("\n[Case 2: UniqueHook]")
    # field="email" を指定することで、辞書内の 'email' キーの値が重複しないか監視します。
    db.add_hook(UniqueHook(field="email"))

    # 'alice@example.com' は既に使用されているので、別のユーザーで使うとエラーになるはず
    try:
        db["user:2"] = {"name": "Bob", "age": 25, "email": "alice@example.com"}
    except NanaSQLiteValidationError as e:
        print(f"-> [FAIL] 一意性違反ブロック成功: {e}")

    # emailが異なれば保存できる
    db["user:2"] = {"name": "Bob", "age": 25, "email": "bob@example.com"}
    print(f"-> [OK] 重複しないデータを保存しました: {db['user:2']}")


    # ==============================================================================
    # 3. ForeignKeyHook の使用例 (注文データの user_id が実在するか)
    # ==============================================================================
    print("\n[Case 3: ForeignKeyHook]")
    orders_db = db.table("orders")
    
    # 'user_id' フィールドが、メインテーブル (db) のキーとして存在するかチェック
    orders_db.add_hook(ForeignKeyHook(field="user_id", target_db=db))

    # 存在しないユーザー(user:99)への注文を試みる
    try:
        orders_db["order:1001"] = {"item": "Laptop", "user_id": "user:99", "price": 1000}
    except NanaSQLiteValidationError as e:
        print(f"-> [FAIL] 参照整合性違反ブロック成功: {e}")

    # 存在するユーザー(user:1)であれば保存できる
    orders_db["order:1001"] = {"item": "Laptop", "user_id": "user:1", "price": 1000}
    print(f"-> [OK] 参照先が存在するデータを保存しました: {orders_db['order:1001']}")


    # 終了処理
    db.close()

if __name__ == "__main__":
    main()
