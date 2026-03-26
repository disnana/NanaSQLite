import threading
import time
import os
import sys
import pytest

# テスト実行時のパス設定
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from nanasqlite import NanaSQLite

def test_v2_engine_sharing_leak_fix():
    """table()を大量に呼び出してもV2Engine（スレッド）が量産されないことを確認"""
    db_path = "test_leak_fix.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    try:
        # v2_mode=TrueでメインDBを作成
        db = NanaSQLite(db_path, v2_mode=True)
        
        initial_threads = threading.active_count()
        print(f"\nInitial threads: {initial_threads}")
        
        # 100個のテーブル（サブインスタンス）を作成
        tables = []
        for i in range(100):
            tables.append(db.table(f"table_{i}"))
            
        current_threads = threading.active_count()
        print(f"Threads after 100 tables: {current_threads}")
        
        # 以前の実装ではここでスレッドが100個増えていたはず。
        # 修正後は1つ（メインDBのV2Engine）のみ増えるはず。
        # (正確には既存スレッド数に対して微増に留まるはず)
        assert current_threads < initial_threads + 20, f"Too many threads created: {current_threads - initial_threads}"
        
        # 共有されていることを確認
        for t in tables:
            assert t._v2_engine is db._v2_engine
            
        db.close()
        time.sleep(0.5)
        
        final_threads = threading.active_count()
        print(f"Final threads: {final_threads}")
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

if __name__ == "__main__":
    test_v2_engine_sharing_leak_fix()
