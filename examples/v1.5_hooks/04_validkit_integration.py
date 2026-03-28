"""
v1.5.0dev1機能解説: 04. Validkitによる高度なバリデーション (Validkit Integration)

NanaSQLite v1.5.0dev1 は、サードパーティ製の軽量なバリデーションライブラリ
「validkit-py」との公式な連携(Integration)をサポートしました。

`ValidkitHook` を使用すると、ネストされた複雑な辞書データの構造、型、そして制約を
Pydanticのようなクラスベースではなく、辞書表現でシンプルかつ宣言的に記述・検証することができます。
（※CerberusやJSON Schemaに似た使用感です）

◆ このサンプルで学べること
1. `ValidkitHook` の登録と基本的な使い方
2. スキーマ（構造定義）に基づいた自動バリデーションの動作
3. `coerce=True` によるデータの自動型変換とデフォルト値の補完
4. バリデーションエラーのハンドリング
"""

import validkit

from nanasqlite import NanaSQLite
from nanasqlite.exceptions import NanaSQLiteValidationError
from nanasqlite.hooks import ValidkitHook

# ==============================================================================
# 1. バリデーションスキーマの定義
# ==============================================================================

# validkit-pyの文法を使用して、データの許容スキーマ（構造）を定義します。
# ここでは「ユーザーデータ」を定義しています。
# - name: 文字列型（必須項目）
# - age: 整数型であり、0から150の範囲内であること（必須項目）
# - tags: 文字列型のリスト（任意項目。指定がなければ空リスト[]が設定される）
USER_SCHEMA = {
    "name": str,
    "age": validkit.All(int, validkit.Range(min=0, max=150)),
    "tags": validkit.Optional([str], default=[]),
}


# ==============================================================================
# 2. 連携テスト
# ==============================================================================


def main():
    print("--- 04. Validkitによる高度なバリデーション ---")

    db = NanaSQLite(":memory:")

    # ValidkitHook を登録する。
    # schema に↑で定義したルールを指定します。
    # `coerce=True` に指定すると、入力されたデータがスキーマの型に合うように
    # （例えば、文字列の"18"を整数の18に）自動変換を試み、デフォルト値の補完も行います。
    db.add_hook(ValidkitHook(USER_SCHEMA, coerce=True))

    # ==============================================================================
    # 3. データの書き込み（スキーマを満たす正常系）
    # ==============================================================================
    print("\n>> データを保存します (正常系)")
    # 'age' に文字列 "18" を渡していますが、coerce=True により整数に変換されます。
    # 'tags' は省略されていますが、デフォルト設定により [] (空リスト)が自動で追加されます。
    db["user:1"] = {"name": "nana", "age": "18"}

    user_data = db["user:1"]
    print(f"-> [OK] 正常なデータを保存しました: {user_data}")
    print(f"   (ageの型が変換されています: {type(user_data['age'])}, tagsが補完されています: {user_data['tags']})")

    # ==============================================================================
    # 4. バリデーションエラーの発生（異常系）
    # ==============================================================================

    # 異常系 1: age の範囲外
    print("\n>> 不正なデータを保存します (異常系: 年齢が範囲外)")
    try:
        # age が 200 なので、Range(min=0, max=150) の制約に違反します。
        db["user:2"] = {"name": "bad_age", "age": 200}
    except NanaSQLiteValidationError as e:
        print(f"-> [FAIL] バリデーションエラーの検知に成功しました: {e}")

    # 異常系 2: 必須項目の欠落
    print("\n>> 不正なデータを保存します (異常系: 必須項目が欠如)")
    try:
        # 必須項目である 'name' が指定されていません。
        db["user:3"] = {"age": 20}
    except NanaSQLiteValidationError as e:
        print(f"-> [FAIL] 必須項目の欠如を検知しました: {e}")

    # データベースを安全に閉じます。
    db.close()


if __name__ == "__main__":
    main()
