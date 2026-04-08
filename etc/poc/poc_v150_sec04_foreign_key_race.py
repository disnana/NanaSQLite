#!/usr/bin/env python3
"""
POC for SEC-04: ForeignKeyHook TOCTOU Race Condition

This script demonstrates how ForeignKeyHook.before_write() can be bypassed
when the referenced key is deleted between the constraint check and write.
"""

import os
import threading
import time
import tempfile
from nanasqlite import NanaSQLite
from nanasqlite.hooks import ForeignKeyHook


def test_foreign_key_hook_race():
    """Test TOCTOU race condition in ForeignKeyHook constraint checking."""
    # Use temporary files for testing
    with tempfile.NamedTemporaryFile(delete=False) as f:
        db_path = f.name
    
    try:
        # Initialize two related tables
        groups = NanaSQLite(db_path, table="groups")
        users = NanaSQLite(db_path, table="users")
        
        # Add foreign key constraint: users.group_id -> groups table
        users.add_hook(ForeignKeyHook("group_id", groups))
        
        # Insert initial group
        groups["admin_group"] = {"name": "Administrators"}
        
        # Racing threads with barrier synchronization
        barrier = threading.Barrier(2)
        results = []
        
        def writer_thread():
            """Thread that tries to insert user referencing a group."""
            try:
                barrier.wait()  # Synchronize with deleter
                time.sleep(0.01)  # Small delay to let FK check happen first
                
                # This should normally fail FK constraint, but race window allows it
                users["user1"] = {
                    "name": "Alice",
                    "group_id": "admin_group"  # This group will be deleted concurrently
                }
                results.append(("writer", "SUCCESS"))
            except Exception as e:
                results.append(("writer", f"ERROR: {type(e).__name__}"))
        
        def deleter_thread():
            """Thread that deletes the referenced group."""
            try:
                barrier.wait()  # Synchronize with writer
                time.sleep(0.02)  # Let writer's FK check pass first
                
                # Delete the group that user wants to reference
                del groups["admin_group"]
                results.append(("deleter", "SUCCESS"))
            except Exception as e:
                results.append(("deleter", f"ERROR: {type(e).__name__}"))
        
        # Start racing threads
        writer = threading.Thread(target=writer_thread)
        deleter = threading.Thread(target=deleter_thread)
        
        writer.start()
        deleter.start()
        
        writer.join()
        deleter.join()
        
        # Check results
        print("=== ForeignKeyHook TOCTOU Race Condition Test ===")
        print(f"Thread results: {results}")
        
        # Check final database state
        try:
            user1 = users.get("user1")
            print(f"User1 data: {user1}")
            
            if user1 and user1.get("group_id") == "admin_group":
                # Check if the referenced group still exists
                referenced_group = groups.get("admin_group")
                print(f"Referenced group exists: {referenced_group is not None}")
                
                if referenced_group is None:
                    print("🐛 BUG: Foreign key constraint violated! User references deleted group.")
                    return "BUG"
                else:
                    print("✅ PASS: Foreign key constraint properly enforced.")
                    return "PASS"
            else:
                print("✅ PASS: User insertion was properly rejected or group wasn't deleted.")
                return "PASS"
                
        except Exception as e:
            print(f"Error checking final state: {e}")
            return "ERROR"
    
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_simplified_foreign_key_race():
    """Simplified version focusing on the race condition."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        db_path = f.name
    
    try:
        # Setup
        target_db = NanaSQLite(db_path, table="target")
        source_db = NanaSQLite(db_path, table="source")
        
        target_db["ref1"] = {"name": "Reference 1"}
        source_db.add_hook(ForeignKeyHook("ref_id", target_db))
        
        # Test normal case first
        try:
            source_db["item1"] = {"name": "Item 1", "ref_id": "ref1"}
            print("Normal FK constraint: PASS")
        except Exception as e:
            print(f"Normal FK constraint failed unexpectedly: {e}")
            return "ERROR"
        
        # Test race condition
        def race_test():
            """Quick race test with manual timing."""
            import threading
            exception_caught = threading.Event()
            
            def quick_writer():
                try:
                    # This should trigger FK check for "ref2"
                    source_db["item2"] = {"name": "Item 2", "ref_id": "ref2"}
                except Exception:
                    exception_caught.set()
            
            # Insert ref2, start writer, then quickly delete ref2
            target_db["ref2"] = {"name": "Reference 2"}
            writer_thread = threading.Thread(target=quick_writer)
            writer_thread.start()
            
            # Try to delete during writer's execution
            time.sleep(0.001)  # Tiny delay
            try:
                del target_db["ref2"]
            except Exception:
                # key may already be absent; ignore during cleanup
                pass
            
            writer_thread.join()
            
            # Check if race condition occurred
            item2 = source_db.get("item2")
            ref2_exists = target_db.get("ref2") is not None
            
            if item2 and not ref2_exists:
                print("🐛 BUG: FK race condition detected - orphaned reference created!")
                return "BUG"
            else:
                print("✅ PASS: No FK race condition detected.")
                return "PASS"
        
        return race_test()
    
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    print("Running comprehensive FK race test...")
    result1 = test_foreign_key_hook_race()
    
    print("\nRunning simplified FK race test...")
    result2 = test_simplified_foreign_key_race()
    
    if result1 == "BUG" or result2 == "BUG":
        final_result = "BUG"
    else:
        final_result = "PASS"
    
    print(f"\nOverall test result: {final_result}")