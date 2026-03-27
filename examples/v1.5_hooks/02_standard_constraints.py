"""
v1.5.0dev1機能解説: 02. 標準制約フック (Standard Constraints)

NanaSQLite v1.5.0dev1 では、よく使われる RDBMS（リレーショナルデータベース）的な制約を
簡単に実装できる組み込みフッククラスが導入されました。
これにより、NoSQLのような手軽さを保ちつつ、データの整合性を厳格に保護できます。

◆ このサンプルで学べること
1. `CheckHook`: シンプルな条件チェック（例: 年齢は0以上でなければならない）
2. `UniqueHook`: データの重複禁止（ユニーク制約、例: メールアドレスの重複登録防止）
3. `ForeignKeyHook`: 他テーブルのキー参照（外部キー制約、例: 存在しないユーザーIDの指定防止）
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
    print("\n[Case 1: CheckHook を用いた値のバリデーション]")
    # 条件を判定する関数を定義します。Trueを返せば許可、Falseなら拒否されます。
    def is_valid_age(key: str, value: Any) -> bool:
        if isinstance(value, dict) and "age" in value:
            return value["age"] >= 0
        return True

    # フックを登録します。バリデーションに失敗した際のエラーメッセージも指定できます。
    db.add_hook(CheckHook(is_valid_age, "年齢(age)は0以上である必要があります"))

    # 不正なデータ（年齢がマイナス）をテスト
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
    print("\n[Case 2: UniqueHook を用いた一意性制約]")
    # field="email" を指定することで、辞書内の 'email' キーの値が
    # データベース全体で重複していないかを自動的に監視します。
    db.add_hook(UniqueHook(field="email"))

    # 'alice@example.com' はすでに user:1 で使用されています。
    # そのため、別のキー（user:2）で同じメールアドレスを登録しようとするとエラーになります。
    try:
        db["user:2"] = {"name": "Bob", "age": 25, "email": "alice@example.com"}
    except NanaSQLiteValidationError as e:
        print(f"-> [FAIL] 一意性違反ブロック成功: {e}")

    # emailが異なっていれば正常に保存できます。
    db["user:2"] = {"name": "Bob", "age": 25, "email": "bob@example.com"}
    print(f"-> [OK] 重複しないデータを保存しました: {db['user:2']}")


    # ==============================================================================
    # 3. ForeignKeyHook の使用例 (注文データの user_id が実在するか)
    # ==============================================================================
    print("\n[Case 3: ForeignKeyHook を用いた参照整合性維持]")
    # 注文データを管理するための新しいテーブル(サブデータベース)を作成します。
    orders_db = db.table("orders")
    
    # 'user_id' フィールドに入力された文字列が、メインテーブル (db) の
    # 有効なキーとして実際に存在しているかをチェックします。
    orders_db.add_hook(ForeignKeyHook(field="user_id", target_db=db))

    # 存在しないユーザー(user:99)への注文作成を試みる
    try:
        orders_db["order:1001"] = {"item": "Laptop", "user_id": "user:99", "price": 1000}
    except NanaSQLiteValidationError as e:
        print(f"-> [FAIL] 参照整合性違反ブロック成功: {e}")

    # 実際に存在するユーザー(user:1)であれば保存できる
    orders_db["order:1001"] = {"item": "Laptop", "user_id": "user:1", "price": 1000}
    print(f"-> [OK] 参照先が存在するデータを保存しました: {orders_db['order:1001']}")


    # 終了処理
    db.close()

if __name__ == "__main__":
    main()
