"""
BUG-02 [Medium] AsyncNanaSQLite.table() 子インスタンスに属性が設定されない

修正前: object.__new__() で __init__ バイパスのため _v2_mode 等が未設定。
AttributeError が発生する。
修正後: 親インスタンスの設定が正しく継承される。
"""

import asyncio
import os
import tempfile

from nanasqlite import AsyncNanaSQLite


async def main():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        async with AsyncNanaSQLite(path) as db:
            child = await db.table("sub")
            errors = []
            for attr in [
                "_v2_mode",
                "_flush_mode",
                "_flush_interval",
                "_flush_count",
                "_v2_chunk_size",
                "_cache_strategy",
                "_cache_size",
                "_cache_ttl",
                "_cache_persistence_ttl",
                "_encryption_key",
                "_encryption_mode",
            ]:
                try:
                    getattr(child, attr)
                except AttributeError:
                    errors.append(attr)

            if errors:
                print(f"BUG: Missing attributes: {errors}")
            else:
                print("PASS: All attributes accessible on child instance")
    finally:
        os.unlink(path)


asyncio.run(main())
