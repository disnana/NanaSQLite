"""
v1.5.0dev1機能解説: 04. Validkitによる高度なバリデーション (Validkit Integration)

NanaSQLite v1.5.0dev1 は、サードパーティ製ライブラリ `validkit-py` との連携をサポートしました。
`ValidkitHook` を使用すると、ネストされた複雑な辞書データの構造、型、制約を
非常にシンプルかつ宣言的に記述・検証することができます。

◆ このサンプルで学べること
1. `ValidkitHook` の登録と基本的な使い方
2. スキーマ（構造定義）に基づいた自動バリデーション
3. バリデーションエラーのハンドリング
"""

import validkit

from nanasqlite import NanaSQLite
from nanasqlite.exceptions import NanaSQLiteValidationError
from nanasqlite.hooks import ValidkitHook

# ==============================================================================
# 1. バリデーションスキーマの定義
# ==============================================================================

# validkit-pyの文法を使用してスキーマを定義
# ここでは「ユーザーはname(文字列)とage(0-150の整数)を必須とし、
# tags(リスト)は任意」というルールを定義します。
USER_SCHEMA = {
    "name": str,
    "age": validkit.All(int, validkit.Range(min=0, max=150)),
    "tags": validkit.Optional([str], default=[])
}


# ==============================================================================
# 2. 連携テスト
# ==============================================================================

def main():
    print("--- 04. Validkitによる高度なバリデーション ---")

    db = NanaSQLite(":memory:")

    # ValidkitHook を登録する。
    # schema に定義したルールを指定します。
    # coerce=True にすると、入力データをスキーマに合わせて自動変換します。
    db.add_hook(ValidkitHook(USER_SCHEMA, coerce=True))

    # 3. データの書き込み（スキーマを満たす正常系）
    print("\n>> データを保存します (正常系)")
    # tags を省略していますが、coerce=True によりデフォルト値 [] が補完されます
    db["user:1"] = {"name": "nana", "age": "18"} # ageを文字列で渡してもintに変換されます

    user_data = db["user:1"]
    print(f"-> [OK] 正常なデータを保存しました: {user_data}")
    print(f"   (ageの型: {type(user_data['age'])}, tags: {user_data['tags']})")

    # 4. バリデーションエラーの発生
    print("\n>> 不正なデータを保存します (異常系: 年齢が範囲外)")
    try:
        db["user:2"] = {"name": "bad_age", "age": 200}
    except NanaSQLiteValidationError as e:
        print(f"-> [FAIL] バリデーションエラーの検知に成功しました: {e}")

    print("\n>> 不正なデータを保存します (異常系: 必須項目が欠如)")
    try:
        db["user:3"] = {"age": 20} # name が欠如
    except NanaSQLiteValidationError as e:
        print(f"-> [FAIL] 必須項目の欠如を検知しました: {e}")

    db.close()

if __name__ == "__main__":
    main()
