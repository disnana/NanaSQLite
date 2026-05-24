"""インメモリ DB に対する get_db_size() の実行 PoC。

現行の期待挙動:
    NanaSQLite(":memory:").get_db_size() は例外を出さず 0 を返す。
"""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    try:
        from nanasqlite import NanaSQLite
    except ModuleNotFoundError as exc:
        print(f"スキップ: 実行時依存が不足しています: {exc}")
        return 0

    with NanaSQLite(":memory:") as db:
        db["k"] = {"v": 1}
        size = db.get_db_size()
        print(f"NanaSQLite(':memory:').get_db_size() -> {size!r}")
        if size != 0:
            print("再現: 0 以外の値が返った、または保護処理が期待通りではありません。")
            return 1

    print("修正済み: インメモリ DB のサイズは 0 を返します。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
