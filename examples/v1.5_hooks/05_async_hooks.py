"""
v1.5.0dev1機能解説: 05. 非同期データベースでのフック活用 (Async Hooks)

NanaSQLiteが持つ強力な非同期処理用インターフェース「AsyncNanaSQLite」でも、
v1.5.0dev1 以降導入された Ultimate Hooks は完全な互換性を持ってサポートされています。

◆ このサンプルで学べること
1. AsyncNanaSQLite に対する `add_hook()` の使用方法（同期版とほぼ同じです）
2. 複数のフック（独自ロギング＋標準制約など）を同時に連携するアプローチ
3. 非同期環境下でも安全にフックが実行される仕組みの理解
   ※ NanaSQLite は内部でフック処理を ThreadPool Executor 上にオフロードするため、
      同期的に記述された重いフックであってもメインのイベントループをブロックしません。
"""

import asyncio
from typing import Any

from nanasqlite import AsyncNanaSQLite
from nanasqlite.exceptions import NanaSQLiteValidationError
from nanasqlite.hooks import CheckHook
from nanasqlite.protocols import NanaHook


# ==============================================================================
# 1. カスタム非同期用ロギングフックの定義
# ※フック自体の実装は同期インターフェース(def)のまま記述します。
#   AsyncNanaSQLite 内部で自動的に別スレッド(Executor)上で安全に実行されます。
# ==============================================================================
class AsyncLoggingHook(NanaHook):
    def before_write(self, db: Any, key: str, value: Any) -> Any:
        # 書き込み前のフック
        print(f"[Async LOG: WRITE] '{key}': {value}")
        # 仮にここで時間のかかる処理(Sleepや通信など)を行っても、
        # asyncioループはブロックされず並行処理が維持されます。
        return value

    def after_read(self, db: Any, key: str, value: Any) -> Any:
        # 読み込み後のフック
        print(f"[Async LOG: READ] '{key}': {value}")
        return value


async def main():
    print("--- 05. 非同期データベースでのフック活用 (Async Hooks) ---")

    # ==============================================================================
    # 2. データベースの初期化とフックの登録
    # ==============================================================================
    # 非同期モードでの初期化は AsyncNanaSQLite を使用します。
    db = AsyncNanaSQLite(":memory:")

    # 非同期操作であっても、フックの追加は await 付きで同様に行えます。
    # 1. 自作のロギングフックを追加
    await db.add_hook(AsyncLoggingHook())

    # 2. NanaSQLite組み込みの CheckHook(制約フック) を追加
    # point が 0 以上の値しか受け付けないルールを定義します。
    def is_positive_point(key: str, value: Any) -> bool:
        if isinstance(value, dict) and "point" in value:
            return value["point"] >= 0
        return True

    await db.add_hook(CheckHook(is_positive_point, "ポイント(point)は0以上である必要があります"))

    # ==============================================================================
    # 3. 非同期操作の実行（複数タスクによる並行動作）
    # ==============================================================================
    print("\n>> 3つの並行書き込みタスクを実行します...")

    # 並行で動作するタスクを定義
    async def write_task(user_id: str, point: int):
        print(f"  [Task] {user_id} の保存を開始します (point: {point})")
        try:
            # aset 等の非同期書き込みメソッドを呼ぶと、
            # 内部で before_write フックが自動的に作動します。
            await db.aset(user_id, {"username": f"Player_{user_id}", "point": point})
            print(f"  [Task] [OK] {user_id} の保存に成功しました")
        except NanaSQLiteValidationError as e:
            # CheckHookの制約に引っかかるとこの例外が発生します
            print(f"  [Task] [FAIL] {user_id} の保存がフックによってブロックされました: {e}")

    # asyncio.gather() を用いて、正常なデータ2件と無効なデータ(-10ポイント)1件を
    # 完全に同時に（並行に）書き込みます。
    await asyncio.gather(
        write_task("user:101", 50),
        write_task("user:102", 120),
        write_task("user:103", -10),  # pointがマイナスなので CheckHook にブロックされる
    )

    # ==============================================================================
    # 4. 非同期読み込みの実行
    # ==============================================================================
    print("\n>> データの読み込みを実行します...")

    # aget でデータを取得すると、after_read フック（今回はログ出力）が実行されます。
    user_101 = await db.aget("user:101")
    user_102 = await db.aget("user:102")

    print(f"読み込み結果 user_101: {user_101}")
    print(f"読み込み結果 user_102: {user_102}")

    # ==============================================================================
    # 5. 非同期削除の実行
    # ==============================================================================
    # adelete (非同期削除) を呼ぶ際にも before_delete が発火します
    # (※このサンプルでは after_read ばかりですが、仕組み上対応しています)
    await db.adelete("user:101")
    print("\n>> user:101 を削除しました")

    # 最後に、リソースを正しく解放するため close を呼び出します。
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
