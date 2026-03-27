"""
v1.5.0dev1機能解説: 04. 外部ライブラリ連携 - ValidkitHook

v1.5.0dev1では、NanaSQLiteの推奨バリデーションライブラリである
「validkit-py」との連携も、Ultimate Hooksアーキテクチャに乗っかる形で強化されました。

◆ このサンプルで学べること
1. ValidkitHookによる高速なデータ検証
2. `coerce=True` を使ったデータの自動変換（文字列から数値へのパース等）
3. 従来の `validator` 引数との後方互換性
"""

try:
    from validkit import v
except ImportError:
    print("このサンプルを実行するには validkit-py が必要です。")
    print("インストールコマンド: pip install validkit")
    exit(1)

from nanasqlite import NanaSQLite
from nanasqlite.hooks import ValidkitHook
from nanasqlite.exceptions import NanaSQLiteValidationError


# ==============================================================================
# 1. Validkit スキーマの定義
# ==============================================================================
# Validkit は Pydantic より軽量で超高速なバリデーションライブラリです。
# スキーマを辞書形式で定義します。
product_schema = {
    "name": v.str().min_length(2).max_length(50),
    
    # coerce() を指定することで、保存時に型変換（文字列 "10" -> 数値 10 など）を試みます
    "price": v.int().min(0).coerce(),
    
    # 選択肢の制限
    "category": v.str().choices(["electronics", "books", "clothing", "other"])
}


def main():
    print("--- 04. Validkit との連携 (ValidkitHook) ---")
    
    # データベースの初期化
    db = NanaSQLite(":memory:")
    
    # ==============================================================================
    # 2. ValidkitHook の登録
    # ==============================================================================
    # "product:" で始まるキーに対して、作成したスキーマに基づく検証を適用します。
    # coerce=True を指定すると、検証後に変換されたデータがDBに書き込まれます。
    # (※スキーマ定義側にも `.coerce()` が宣言されている必要があります)
    
    db.add_hook(ValidkitHook(product_schema, coerce=True, key_pattern=r"^product:"))

    # ==============================================================================
    # 3. 正常なデータの保存と自動型変換 (coerce)
    # ==============================================================================
    print("\n>> データを保存します（'price' に文字列の '1500' を渡します）")
    
    db["product:1"] = {
        "name": "Wireless Mouse",
        "price": "1500",  # <- 文字列ですが、ValidkitHook が int に変換します
        "category": "electronics"
    }
    
    # 保存後のデータを取得してみると、'price' が数値に変換されています
    saved_product = db["product:1"]
    print(f"-> 変換後のデータ: {saved_product}")
    print(f"-> 'price' の型: {type(saved_product['price'])}")


    # ==============================================================================
    # 4. 無効なデータの拒否
    # ==============================================================================
    print("\n>> 無効なデータを保存しようとします（'price'がマイナス、'category'が無効な値）")
    
    try:
        db["product:2"] = {
            "name": "P",  # 文字数が足りない(min_length(2))
            "price": -500,  # マイナス値(min(0))
            "category": "food"  # 許可されていないカテゴリ(choices)
        }
        print("-> ❌ (ここは表示されません)")
    except NanaSQLiteValidationError as e:
        print(f"-> ❌ 保存ブロック成功: データの検証に失敗しました。")
        print(f"エラー詳細: {e}")


    # ==============================================================================
    # 5. 【補足】レガシーインターフェース (後方互換性)
    # ==============================================================================
    print("\n>> 【補足】NanaSQLite は従来の初期化パラメータもサポートしています")
    
    # v1.4.x までのように __init__ で validator と coerce を指定することも可能です。
    # 内部的には ValidkitHook(schema, coerce=True) に自動変換され、全キーに対して適用されます。
    db_legacy = NanaSQLite(":memory:", validator=product_schema, coerce=True)
    
    db_legacy["legacy:1"] = {
        "name": "Keyboard",
        "price": "5000",
        "category": "electronics"
    }
    print(f"-> 従来の方法でも同様に型変換されます: {db_legacy['legacy:1']}")

    db.close()
    db_legacy.close()

if __name__ == "__main__":
    main()
