"""
v1.5.0dev1機能解説: 03. Pydanticとの透過的連携 (Pydantic Integration)

NanaSQLite v1.5.0dev1 では、Pydantic モデルを直接 `set` や `upsert` に渡せるようになりました。
`PydanticHook` を使用することで、データの保存時に自動的に dict へ変換し、
読み込み時に自動的に Pydantic モデルとして復元します。

◆ このサンプルで学べること
1. `PydanticHook` の登録と基本的な使い方
2. モデルオブジェクトを直接データベース操作に渡す方法
3. 取得したデータを取り回しやすいオブジェクトとして扱う方法
"""

from typing import Any
from pydantic import BaseModel, Field, EmailStr
from nanasqlite import NanaSQLite
from nanasqlite.hooks import PydanticHook
from nanasqlite.exceptions import NanaSQLiteValidationError

# ==============================================================================
# 1. Pydanticモデルの定義
# ==============================================================================

class UserProfile(BaseModel):
    """ユーザープロファイルを表すPydanticモデル"""
    username: str = Field(..., min_length=3)
    age: int = Field(..., ge=0, le=150)
    email: str  # 本来は EmailStr ですが、シンプルさのため str


# ==============================================================================
# 2. 連携テスト
# ==============================================================================

def main():
    print("--- 03. Pydanticとの透過的連携 ---")

    db = NanaSQLite(":memory:")
    
    # PydanticHook を登録する。
    # model_class を指定することで、そのモデルとの相互変換を自動化します。
    db.add_hook(PydanticHook(UserProfile))

    # 3. データの書き込み（Pydanticモデルを直接渡す）
    print("\n>> Pydanticモデルを直接保存します")
    user = UserProfile(username="nana_chan", age=17, email="nana@example.com")
    
    # 内部で dict に変換されてSQLiteに保存されます
    db["user:101"] = user
    print(f"-> [OK] Pydanticモデルを直接保存しました: {db['user:101']}")

    # 4. バリデーションの自動実行
    print("\n>> 不正なデータ（年齢がマイナス）の保存を試みます")
    try:
        # dict で渡しても、Hookが Pydantic を通じてバリデーションを行います
        db["user:102"] = {"username": "bad_user", "age": -5, "email": "test@xxx"}
    except NanaSQLiteValidationError as e:
        print(f"-> [FAIL] 制約違反ブロック成功: {e}")

    # 5. データの読み込み（モデルとして復元）
    print("\n>> データを読み込みます")
    user_data = db["user:101"]
    
    print(f"=> 取得されたデータの型: {type(user_data)}")
    if isinstance(user_data, UserProfile):
        print(f"-> [OK] 読み込み時にPydanticモデルに復元されました: {user_data.username}")
    
    db.close()

if __name__ == "__main__":
    main()
