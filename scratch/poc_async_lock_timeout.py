"""AsyncNanaSQLite の lock_timeout 転送を確認する実行 PoC。

修正前の想定挙動:
    python scratch/poc_async_lock_timeout.py
    -> AsyncNanaSQLite を lock_timeout=0.2 で生成しても、
       内部の同期 DB の _lock_timeout が None になる。

この PoC は APSW などの実行時依存が必要。
依存がない環境では、隣の静的検証スクリプトを使う。
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


async def main() -> int:
    try:
        from nanasqlite import AsyncNanaSQLite
    except ModuleNotFoundError as exc:
        print(f"スキップ: 実行時依存が不足しています: {exc}")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        db_path = str(Path(tmp) / "async_lock_timeout.db")
        db = AsyncNanaSQLite(db_path, lock_timeout=0.2)
        await db.aset("k", {"v": 1})

        actual = getattr(db.sync_db, "_lock_timeout", "<missing>")
        print(f"AsyncNanaSQLite(..., lock_timeout=0.2) -> sync_db._lock_timeout = {actual!r}")

        child = await db.table("child")
        child_actual = getattr(child.sync_db, "_lock_timeout", "<missing>")
        print(f"(await db.table('child')).sync_db._lock_timeout = {child_actual!r}")

        await db.close()

        if actual != 0.2:
            print("再現: async コンストラクタが lock_timeout を内部 DB に転送していません。")
            return 1

        print("修正済み: async コンストラクタが lock_timeout を内部 DB に転送しています。")
        return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
