"""
v1.5.0dev1機能解説: 03. 外部ライブラリ連携 - PydanticHook

v1.5.0dev1では、Pythonエコシステムで標準的なデータ検証ライブラリである
「Pydantic」との公式連携機能として `PydanticHook` が提供されました。

◆ このサンプルで学べること
1. PydanticHookによるモデル連携の設定
2. データの自動シリアライズ（モデルから辞書へ）と保存
3. データの自動デシリアライズ（辞書からモデルへ）と取得
4. 型や制約（メールアドレス形式、最大文字数等）の厳格な検証
"""

try:
    from pydantic import BaseModel, EmailStr, Field, ValidationError
except ImportError:
    print("このサンプルを実行するには Pydantic と email-validator が必要です。")
    print("インストールコマンド: pip install pydantic email-validator")
    exit(1)

from nanasqlite import NanaSQLite
from nanasqlite.hooks import PydanticHook
from nanasqlite.exceptions import NanaSQLiteValidationError


# ==============================================================================
# 1. Pydantic モデルの定義
# ==============================================================================
class UserProfile(BaseModel):
    """
    ユーザーのプロフィール情報を定義するPydanticモデル。
    各フィールドに対して厳格な型チェックとバリデーションを定義します。
    """
    username: str = Field(..., min_length=3, max_length=20, description="3〜20文字のユーザー名")
    age: int = Field(..., ge=18, description="18歳以上であること")
    email: EmailStr = Field(..., description="有効なメールアドレス")
    is_active: bool = True


def main():
    print("--- 03. Pydantic との連携 (PydanticHook) ---")
    
    # バックエンドデータベースの起動
    db = NanaSQLite(":memory:")
    
    # ==============================================================================
    # 2. PydanticHook の登録
    # "user:" で始まるキーに対して、UserProfile モデルを適用します。
    # ==============================================================================
    # PydanticHookを登録することで、NanaSQLiteが Pydantic.BaseModel を直接
    # サポートするようになり、自動的に変換(シリアライズ/デシリアライズ)を行います。
    # 
    # key_pattern: "user:*" にマッチするキーのみにこのフックを適用します
    db.add_hook(PydanticHook(UserProfile, key_pattern=r"^user:"))


    # ==============================================================================
    # 3. モデルオブジェクトの直接保存
    # ==============================================================================
    print("\n>> Pydanticモデルを直接 NanaSQLite に保存します")
    
    # 正常なモデルインスタンスを作成
    good_user = UserProfile(username="Alice123", age=25, email="alice@example.com")
    
    # 直接モデルを保存（内部で PydanticHook の before_write が働き、dictにシリアライズされて保存されます）
    db["user:1"] = good_user
    print(f"-> ✅ 保存成功")


    # ==============================================================================
    # 4. データの取得とモデルへの自動デシリアライズ
    # ==============================================================================
    print("\n>> データベースから取得すると、自動的にPydanticモデルとして返ってきます")
    
    # after_read フックが働き、保存された dict が UserProfile インスタンスに変換されます
    retrieved_user = db["user:1"]
    
    print(f"取得された型: {type(retrieved_user)}")
    if isinstance(retrieved_user, UserProfile):
        print(f"プロフィール内容: \n - 名前: {retrieved_user.username}\n - メール: {retrieved_user.email}")


    # ==============================================================================
    # 5. 無効なデータの保存による制約ブロック
    # ==============================================================================
    print("\n>> PydanticHook による入力データの検証（無効な辞書データを渡す）")
    
    try:
        # dict そのものを渡しても自動的に Pydantic モデルへパース・検証されます
        # ここでは 'age' が 18 未満、'email' が無効な形式です
        db["user:2"] = {"username": "Bo", "age": 15, "email": "invalid_email"}
        print("-> ❌ (これは表示されないはずです)")
    except NanaSQLiteValidationError as e:
        print(f"-> ❌ 保存ブロック成功: データの検証に失敗しました。")
        print(f"エラー詳細: {e}")

    # ==============================================================================
    # 6. その他のキーについての扱い
    # ==============================================================================
    print("\n>> (おまけ) パターンにマッチしないキーの動作")
    
    # "admin:" から始まるキーには PydanticHook("user:*") が適用されません
    # したがって、制限なく自由に保存できます
    db["admin:1"] = {"username": "Root", "is_super": True}
    print(f"-> プレーンな辞書として保存されます: {db['admin:1']}")

    db.close()


if __name__ == "__main__":
    main()
