"""
v1.5.0dev1機能解説: 05. 非同期データベースでのフック活用 (Async Hooks)

NanaSQLiteの強力な非同期インターフェース「AsyncNanaSQLite」でも、
v1.5.0dev1から Ultimate Hooks が完全サポートされました。

◆ このサンプルで学べること
1. AsyncNanaSQLite に対する `add_hook` の使用方法
2. 複数のフック（独自ロギング＋標準制約など）を同時に登録するアプローチ
3. 非同期環境下でも安全に（スレッドプール Executor を経由して）
   同期的に記述されたフックが実行される仕組み
"""

import asyncio
from typing import Any

from nanasqlite import AsyncNanaSQLite
from nanasqlite.exceptions import NanaSQLiteValidationError
from nanasqlite.hooks import CheckHook
from nanasqlite.protocols import NanaHook


# ==============================================================================
# 1. カスタム非同期用ロギングフック
# ※フック自体の実装は同期インターフェース(def)のままですが、
#   AsyncNanaSQLite 内部で適切に Executor 上で実行され、イベントループをブロックしません。
# ==============================================================================
class AsyncLoggingHook(NanaHook):
    def before_write(self, db: Any, key: str, value: Any) -> Any:
        print(f"[Async LOG: WRITE] '{key}': {value}")
        # 時間のかかるバリデーションなどの処理があっても、裏側で別スレッドで実行されます
        return value

    def after_read(self, db: Any, key: str, value: Any) -> Any:
        print(f"[Async LOG: READ] '{key}': {value}")
        return value


async def main():
    print("--- 05. 非同期データベースでのフック活用 (Async Hooks) ---")

    # ==============================================================================
    # 2. データベースの初期化とフックの登録
    # ==============================================================================
    # 非同期モードでも、使い方は同期版とほぼ同じです。
    db = AsyncNanaSQLite(":memory:")

    # 複数のフックを追加できます。
    # 1. データ操作のログを取る自作フック
    await db.add_hook(AsyncLoggingHook())

    # 2. point が 0 以上の値しか受け付けない制約フック
    def is_positive_point(key: str, value: Any) -> bool:
        if isinstance(value, dict) and "point" in value:
            return value["point"] >= 0
        return True

    await db.add_hook(CheckHook(is_positive_point, "ポイント(point)は0以上である必要があります"))


    # ==============================================================================
    # 3. 非同期操作の実行（複数タスクによる並行動作）
    # ==============================================================================
    print("\n>> 3つの並行書き込みタスクを実行します...")

    async def write_task(user_id: str, point: int):
        print(f"  [Task] {user_id} の保存を開始します (point: {point})")
        try:
            # aset は非同期で書き込みを行います。内部でフックが自動実行されます。
            await db.aset(user_id, {"username": f"Player_{user_id}", "point": point})
            print(f"  [Task] [OK] {user_id} の保存に成功しました")
        except NanaSQLiteValidationError as e:
            print(f"  [Task] [FAIL] {user_id} の保存がフックによってブロックされました: {e}")

    # 正常なデータ2件と、無効なデータ(-10ポイント)1件を同時に走らせる
    await asyncio.gather(
        write_task("user:101", 50),
        write_task("user:102", 120),
        write_task("user:103", -10)  # CheckHook にブロックされるはず
    )

    # ==============================================================================
    # 4. 非同期読み込みの実行
    # ==============================================================================
    print("\n>> データの読み込みを実行します...")

    # aget で取得すると、after_read フックが実行されます
    user_101 = await db.aget("user:101")
    user_102 = await db.aget("user:102")

    print(f"読み込み結果 user_101: {user_101}")
    print(f"読み込み結果 user_102: {user_102}")

    # ==============================================================================
    # 5. 非同期削除の実行
    # ==============================================================================
    # adelete で削除する際にも before_delete が発火します
    await db.adelete("user:101")
    print("\n>> user:101 を削除しました")

    # リソースのクリーンアップ
    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
