#!/usr/bin/env python3
"""
POC for SEC-03: UniqueHook TOCTOU Race Condition

This script demonstrates how UniqueHook.before_write() can be bypassed
in multi-threaded environments due to the race window between constraint
checking and actual database write.
"""

import os
import threading
import time
import tempfile
from nanasqlite import NanaSQLite
from nanasqlite.hooks import UniqueHook


def test_unique_hook_race():
    """Test TOCTOU race condition in UniqueHook constraint checking."""
    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(delete=False) as f:
        db_path = f.name
    
    try:
        # Initialize database with UniqueHook for email field
        db = NanaSQLite(db_path, table="users")
        db.add_hook(UniqueHook("email"))
        
        # Insert initial user to establish constraint
        db["user1"] = {"email": "test@example.com", "name": "Test User"}
        
        # Prepare racing threads with barrier synchronization
        results = []
        barrier = threading.Barrier(3)  # 3 threads will race
        
        def writer_thread(thread_id):
            """Each thread tries to write the same email value."""
            try:
                barrier.wait()  # Synchronize start time
                # All threads try to write the same email - should violate unique constraint
                db[f"user_{thread_id}"] = {
                    "email": "duplicate@example.com",  # Same email for all
                    "name": f"User {thread_id}"
                }
                results.append((thread_id, "SUCCESS"))
            except Exception as e:
                results.append((thread_id, f"ERROR: {type(e).__name__}"))
        
        # Start racing threads
        threads = []
        for i in range(2, 5):  # thread IDs 2, 3, 4
            t = threading.Thread(target=writer_thread, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Check results
        success_count = sum(1 for _, result in results if result == "SUCCESS")
        
        print("=== UniqueHook TOCTOU Race Condition Test ===")
        print(f"Racing threads results: {results}")
        print(f"Successful writes: {success_count}")
        
        # Check database state
        all_users = dict(db.items())
        duplicate_emails = []
        for key, user in all_users.items():
            if user.get("email") == "duplicate@example.com":
                duplicate_emails.append(key)
        
        print(f"Users with duplicate email: {duplicate_emails}")
        print(f"Total duplicate count: {len(duplicate_emails)}")
        
        if len(duplicate_emails) > 1:
            print("🐛 BUG: Unique constraint violated! Multiple users have same email.")
            return "BUG"
        elif success_count == 1 and len(duplicate_emails) == 1:
            print("✅ PASS: Unique constraint properly enforced.")
            return "PASS"
        else:
            print("🤔 UNKNOWN: Unexpected result pattern.")
            return "UNKNOWN"
    
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    result = test_unique_hook_race()
    print(f"\nTest result: {result}")