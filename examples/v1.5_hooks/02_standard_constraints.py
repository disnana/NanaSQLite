"""
v1.5.0dev1機能解説: 02. 標準制約フック (Standard Constraints)

NoSQLライクに手軽に使えるNanaSQLiteですが、v1.5.0dev1からは
リレーショナルデータベース（RDBMS）のような「データ整合性」を保証するための
「標準制約フック」が組み込まれました。

◆ このサンプルで学べること
1. CheckHook: カスタム関数を使用して、保存前のデータが条件を満たすか検査する
2. UniqueHook: データベース全体で特定のフィールド（例: e-mail）が重複しないことを保証する
3. ForeignKeyHook: 別のキーが存在していることを保証し、孤立したデータ（オーファン）を防ぐ
"""

from typing import Any
from nanasqlite import NanaSQLite
from nanasqlite.hooks import CheckHook, UniqueHook, ForeignKeyHook
from nanasqlite.exceptions import NanaSQLiteValidationError

def main():
    print("--- 02. 標準制約フック ---")
    
    # 1. データベースの初期化
    db = NanaSQLite(":memory:")
    
    # ==============================================================================
    # 2. CheckHook の追加 (CHECK制約)
    # データベースに保存されるユーザーデータにおいて、「age」が0以上であることを強制します。
    # ==============================================================================
    def is_valid_age(key: str, value: Any) -> bool:
        if isinstance(value, dict) and "age" in value:
            return value["age"] >= 0
        return True # ageが含まれない場合は検査パスとする

    db.add_hook(CheckHook(is_valid_age, "ユーザーの年齢(age)は0以上である必要があります。"))

    print("\n>> CheckHook のテスト (age = -5 を保存しようとします)")
    try:
        db["user:1"] = {"name": "Alice", "age": -5}
    except NanaSQLiteValidationError as e:
        print(f"-> [FAIL] 制約違反ブロック成功: {e}")

    # 正常なデータは保存できる
    db["user:1"] = {"name": "Alice", "age": 20, "email": "alice@example.com"}
    print(f"-> [OK] 正常なデータを保存しました: {db['user:1']}")


    # ==============================================================================
    # 3. UniqueHook の追加 (UNIQUE制約)
    # emailアドレスが重複して登録されるのを防ぎます。
    # ==============================================================================
    # 辞書の "email" キーを対象にして重複チェックを行います。
    # Noneを指定したフィールドはチェックをスキップするため、emailが含まれないデータは許可されます。
    db.add_hook(UniqueHook("email"))

    print("\n>> UniqueHook のテスト (同じemailを持つ別のユーザーを保存しようとします)")
    try:
        db["user:2"] = {"name": "Bob", "age": 25, "email": "alice@example.com"}
    except NanaSQLiteValidationError as e:
        print(f"-> [FAIL] 一意性違反ブロック成功: {e}")

    # emailが異なれば保存できる
    db["user:2"] = {"name": "Bob", "age": 25, "email": "bob@example.com"}
    print(f"-> [OK] 重複しないデータを保存しました: {db['user:2']}")


    # ==============================================================================
    # 4. ForeignKeyHook の追加 (FOREIGN KEY制約 / 外部キー制約)
    # e-コマースの「注文(Order)」データなどを保存する際、
    # その注文を行う「ユーザー(User)」が実際にデータベース上に存在するかを保証します。
    # ==============================================================================
    # この例では、キーが "order:" で始まるデータが保存されるとき、
    # 辞書内の "user_id" フィールドが指し示すキーが NanaSQLite 内に存在するかチェックします。
    def extract_user_key(key: str, value: Any) -> str | None:
        if key.startswith("order:") and isinstance(value, dict) and "user_id" in value:
            return value["user_id"]
        return None

    # db インスタンス自身をチェック先(target_db)として指定します
    db.add_hook(ForeignKeyHook(extract_user_key, target_db=db))

    print("\n>> ForeignKeyHook のテスト (存在しないユーザー user:99 の注文を保存しようとします)")
    try:
        db["order:1001"] = {"item": "Laptop", "user_id": "user:99", "price": 1000}
    except NanaSQLiteValidationError as e:
        print(f"-> [FAIL] 参照整合性違反ブロック成功: {e}")

    # 存在するユーザー(user:1)であれば保存できる
    db["order:1001"] = {"item": "Laptop", "user_id": "user:1", "price": 1000}
    print(f"-> [OK] 参照先が存在するデータを保存しました: {db['order:1001']}")


    # 終了処理
    db.close()


if __name__ == "__main__":
    main()
