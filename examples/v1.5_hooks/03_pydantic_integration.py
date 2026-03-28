"""
v1.5.0dev1機能解説: 03. Pydanticとの透過的連携 (Pydantic Integration)

NanaSQLite v1.5.0dev1 では、Pythonで人気のデータバリデーションライブラリ
「Pydantic」のモデルを直接 `set` や `upsert` に渡せるようになりました。

`PydanticHook` をデータベースに登録しておくことで、
データの保存時には自動的に Pydantic モデルを Dict へ変換（シリアライズ）し、
読み込み時には自動的に元の Pydantic モデルとして復元（デシリアライズ）します。

◆ このサンプルで学べること
1. `PydanticHook` の登録と基本的な使い方
2. モデルオブジェクトを直接データベース操作に渡す方法
3. 取得したデータを持続性のある型付きオブジェクトとして扱う方法
"""

from pydantic import BaseModel, Field

from nanasqlite import NanaSQLite
from nanasqlite.exceptions import NanaSQLiteValidationError
from nanasqlite.hooks import PydanticHook

# ==============================================================================
# 1. Pydanticモデルの定義
# ==============================================================================


class UserProfile(BaseModel):
    """
    ユーザープロファイルを表すPydanticモデル。
    Pydanticの機能を用いて、型の定義とバリデーションルールを宣言します。
    """

    # ユーザー名。最低3文字以上の文字列である必要があります。
    username: str = Field(..., min_length=3)

    # 年齢。0歳以上150歳以下の整数である必要があります。
    age: int = Field(..., ge=0, le=150)

    # メールアドレス。シンプルな実装のためにここでは文字列型としますが、
    # 実際には EmailStr を利用することでフォーマットチェックも可能です。
    email: str


# ==============================================================================
# 2. 連携テスト
# ==============================================================================


def main():
    print("--- 03. Pydanticとの透過的連携 ---")

    db = NanaSQLite(":memory:")

    # PydanticHook を登録する。
    # 引数として連携させたい Pydantic モデルのクラスを渡します。
    db.add_hook(PydanticHook(UserProfile))

    # ==============================================================================
    # 3. データの書き込み（Pydanticモデルを直接渡す）
    # ==============================================================================
    print("\n>> Pydanticモデルを直接保存します")
    # Pythonコード上で扱いやすいように、Pydanticのインスタンスを作成します。
    user = UserProfile(username="nana_chan", age=17, email="nana@example.com")

    # 作成したインスタンスをそのままNanaSQLiteに渡して保存します。
    # 内部の before_write フックで .model_dump() 等が呼ばれ、Dictに変換されてSQLiteに保存されます。
    db["user:101"] = user
    print(f"-> [OK] Pydanticモデルを直接保存しました: {db['user:101']}")

    # ==============================================================================
    # 4. バリデーションの自動実行
    # ==============================================================================
    print("\n>> 不正なデータ（年齢がマイナス）の保存を試みます")
    try:
        # Pydanticモデルのインスタンス生成を経由せず、直接Dictを渡した場合でも、
        # Hookが裏側で Pydantic の `model_validate` を呼び出し検証を実施します。
        # 年齢(age)が -5 となっているため、Pydanticのバリデーションに失敗します。
        db["user:102"] = {"username": "bad_user", "age": -5, "email": "test@example.com"}
    except NanaSQLiteValidationError as e:
        # バリデーションエラーはNanaSQLiteValidationErrorとしてキャッチできます
        print(f"-> [FAIL] 制約違反ブロック成功: {e}")

    # ==============================================================================
    # 5. データの読み込み（モデルとして復元）
    # ==============================================================================
    print("\n>> データを読み込みます")

    # データベースから取得する際は、after_read フックが作動し、
    # 保存時のDictデータが自動的に Pydantic モデルのインスタンスとして返却されます。
    user_data = db["user:101"]

    print(f"=> 取得されたデータの型: {type(user_data)}")
    if isinstance(user_data, UserProfile):
        print(f"-> [OK] 読み込み時にPydanticモデルに復元されました: {user_data.username}")

    db.close()


if __name__ == "__main__":
    main()
