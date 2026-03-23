import os
import sys
from nanasqlite import NanaSQLite

# 接続先データベース
db_path = "poc_bug01.db"

def run_poc():
    print("--- NanaSQLite [BUG-01] POC (Reproduction) ---")
    
    # クリーンアップ
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = NanaSQLite(db_path)
    try:
        # テーブル作成
        db.create_table("test_table", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
        
        print("Test Case: upsert(data_dict, conflict_columns)")
        print("Expected: Success or Database Error")
        print("Actual: AttributeError (if bug exists)")
        
        # この呼び出し方は core.py L2352 の elif に入り、target_data に dict がセットされるが、
        # その後の L2377 で元の data (None) にアクセスしてクラッシュする。
        db.upsert({"id": 1, "name": "Alice"}, conflict_columns=["id"])
        
        print("POC result: SUCCESS (Bug not reproduced or already fixed)")
        
    except AttributeError as e:
        print(f"POC result: REPRODUCED (Caught expected AttributeError: {e})")
        # 異常終了コードを返す
        sys.exit(1)
    except Exception as e:
        print(f"POC result: FAILED (Caught unexpected exception: {type(e).__name__}: {e})")
        sys.exit(1)
    finally:
        db.close()
        if os.path.exists(db_path):
            os.remove(db_path)

if __name__ == "__main__":
    run_poc()
