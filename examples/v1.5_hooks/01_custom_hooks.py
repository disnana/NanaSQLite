"""
v1.5.0dev1機能解説: 01. カスタムフックの基本 (Custom Hooks)

v1.5.0dev1で導入された「Ultimate Hooks」機能の基盤となるのが `NanaHook` プロトコルです。
フックを使用することで、NanaSQLiteがデータを「書き込む前」「読み込んだ後」「削除する前」の
タイミングに独自の処理を注入（介入）させることができます。

◆ このサンプルで学べること
1. `before_write` を使ったデータの自動補完（タイムスタンプの自動付与）
2. `after_read` と `before_delete` を使った操作のロギング
3. `add_hook()` メソッドを使ったフックの登録方法
"""

import time
from typing import Any

from nanasqlite import NanaSQLite
from nanasqlite.protocols import NanaHook

# ==============================================================================
# 1. カスタムフックの定義
# ==============================================================================

class TimestampHook(NanaHook):
    """
    データ保存時に、自動的に作成日時(created_at)と更新日時(updated_at)を記録するフック。
    ※ `before_write` は必ず dict を返すか変更を加える必要があります。
    """
    def before_write(self, db: NanaSQLite, key: str, value: Any) -> Any:
        # dict以外が渡された場合はそのまま通過させる（あるいはエラーにする）
        if isinstance(value, dict):
            now = time.time()
            # 初回作成時のみ created_at を付与
            if "created_at"  not in value:
                # すでにDBに存在するか確認（get_freshで直接DBを引くなど）
                # ここでは簡易的に現在のキャッシュ/DB存在確認を行います
                if key not in db:
                    value["created_at"] = now

            # 更新日時は常に現在時刻で上書き
            value["updated_at"] = now

        return value


class LoggingHook(NanaHook):
    """
    読み込みと削除のタイミングで、ログをコンソールに出力するフック。
    """
    def after_read(self, db: NanaSQLite, key: str, value: Any) -> Any:
        print(f"[LOG: READ] キー '{key}' が読み込まれました。内容: {value}")
        return value

    def before_delete(self, db: NanaSQLite, key: str) -> None:
        print(f"[LOG: DELETE] キー '{key}' が削除されようとしています。")


# ==============================================================================
# 2. フックの適用と実行
# ==============================================================================

def main():
    print("--- 01. カスタムフック의 基本 ---")

    # 1. データベースの初期化
    db = NanaSQLite(":memory:")

    # 2. 作成したフックをデータベースに登録
    db.add_hook(TimestampHook())
    db.add_hook(LoggingHook())

    # 3. データの書き込み（before_write がトリガーされる）
    print(">> 'user:1' を保存します")
    db["user:1"] = {"name": "Alice", "age": 20}

    # 4. データの読み込み（after_read がトリガーされる）
    print("\n>> 'user:1' を読み込みます")
    user_data = db["user:1"]

    # TimestampHookによって自動付与されたデータを確認する
    print("=> 取得されたデータ全体:", user_data)
    print(f"=> created_at: {user_data.get('created_at')}")
    print(f"=> updated_at: {user_data.get('updated_at')}")

    # 5. 少し待ってから更新テスト
    time.sleep(1.0)
    print("\n>> データの一部を更新します (upsert)")
    # updateやupsertでの保存もbefore_writeを通るため、updated_at が更新されます
    # 修正後のupsertロジックにより、第一引数がキーであっても正しく動作します
    db.upsert("user:1", {"name": "Alice Liddell", "age": 21, "created_at": user_data["created_at"]})

    print("\n>> 更新後のデータを読み込みます")
    updated_data = db["user:1"]
    print("=> 取得されたデータ全体:", updated_data)

    # 6. データの削除（before_delete がトリガーされる）
    print("\n>> 'user:1' を削除します")
    del db["user:1"]

    db.close()


if __name__ == "__main__":
    main()
