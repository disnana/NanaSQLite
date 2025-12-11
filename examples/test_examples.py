#!/usr/bin/env python3
"""
Test script to validate NanaSQLite example files.

This script tests the core NanaSQLite patterns used in the framework
integration examples without requiring the actual frameworks to be installed.
"""

import sys
import asyncio
import tempfile
import os
from datetime import datetime, timezone
import uuid

# Import NanaSQLite
try:
    from nanasqlite import NanaSQLite, AsyncNanaSQLite
except ImportError:
    print("Error: NanaSQLite is not installed. Run: pip install nanasqlite")
    sys.exit(1)


def test_flask_patterns():
    """Test patterns used in Flask integration example"""
    print("Testing Flask example patterns...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_blog.db")
        db = NanaSQLite(db_path, bulk_load=False)
        
        try:
            # Test 1: Create a blog post
            post_id = str(uuid.uuid4())
            post_data = {
                "title": "Test Post",
                "content": "Test content for validation",
                "author": "Test Author",
                "tags": ["test", "demo"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            db[f"post_{post_id}"] = post_data
            print("  ✓ Create post")
            
            # Test 2: Retrieve post
            retrieved = db[f"post_{post_id}"]
            assert retrieved["title"] == "Test Post"
            assert retrieved["author"] == "Test Author"
            assert "test" in retrieved["tags"]
            print("  ✓ Retrieve post")
            
            # Test 3: Update post
            retrieved["title"] = "Updated Post"
            retrieved["updated_at"] = datetime.now(timezone.utc).isoformat()
            db[f"post_{post_id}"] = retrieved
            updated = db[f"post_{post_id}"]
            assert updated["title"] == "Updated Post"
            print("  ✓ Update post")
            
            # Test 4: Search by tag
            results = []
            for key in db.keys():
                if key.startswith("post_"):
                    post = db[key]
                    if "test" in [t.lower() for t in post.get('tags', [])]:
                        results.append(post)
            assert len(results) == 1
            print("  ✓ Search by tag")
            
            # Test 5: Delete post
            del db[f"post_{post_id}"]
            assert f"post_{post_id}" not in db
            print("  ✓ Delete post")
            
            # Test 6: Stats calculation
            # Add multiple posts
            for i in range(5):
                pid = str(uuid.uuid4())
                db[f"post_{pid}"] = {
                    "title": f"Post {i}",
                    "content": "Content",
                    "tags": ["tag1", "tag2"] if i % 2 == 0 else ["tag3"]
                }
            
            post_count = sum(1 for key in db.keys() if key.startswith("post_"))
            assert post_count == 5
            
            all_tags = set()
            for key in db.keys():
                if key.startswith("post_"):
                    post = db[key]
                    all_tags.update(post.get('tags', []))
            assert len(all_tags) == 3
            print("  ✓ Statistics calculation")
            
        finally:
            db.close()
    
    print("✅ Flask example patterns validated successfully!\n")


async def test_fastapi_patterns():
    """Test patterns used in FastAPI integration example"""
    print("Testing FastAPI example patterns...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_users.db")
        
        async with AsyncNanaSQLite(db_path, max_workers=10, bulk_load=False) as db:
            # Test 1: Create user
            user_id = str(uuid.uuid4())
            user_data = {
                "name": "Alice",
                "email": "alice@example.com",
                "age": 30
            }
            
            await db.aset(f"user_{user_id}", user_data)
            print("  ✓ Create user")
            
            # Test 2: Retrieve user
            retrieved = await db.aget(f"user_{user_id}")
            assert retrieved["name"] == "Alice"
            assert retrieved["email"] == "alice@example.com"
            assert retrieved["age"] == 30
            print("  ✓ Retrieve user")
            
            # Test 3: List users with pagination
            # Create multiple users
            for i in range(10):
                uid = str(uuid.uuid4())
                await db.aset(f"user_{uid}", {
                    "name": f"User{i}",
                    "email": f"user{i}@example.com",
                    "age": 20 + i
                })
            
            all_keys = await db.akeys()
            user_keys = [k for k in all_keys if k.startswith("user_")]
            assert len(user_keys) == 11  # 1 original + 10 new
            
            # Simulate pagination
            skip = 0
            limit = 5
            page_keys = user_keys[skip:skip + limit]
            assert len(page_keys) == 5
            print("  ✓ List users with pagination")
            
            # Test 4: Update user
            user_data["age"] = 31
            user_data["name"] = "Alice Updated"
            await db.aset(f"user_{user_id}", user_data)
            updated = await db.aget(f"user_{user_id}")
            assert updated["age"] == 31
            assert updated["name"] == "Alice Updated"
            print("  ✓ Update user")
            
            # Test 5: Check duplicate email
            all_users = await db.akeys()
            emails = set()
            for key in all_users:
                if key.startswith("user_"):
                    user = await db.aget(key)
                    if user:
                        emails.add(user.get("email"))
            assert "alice@example.com" in emails
            print("  ✓ Duplicate email check")
            
            # Test 6: Delete user
            await db.adelete(f"user_{user_id}")
            deleted = await db.aget(f"user_{user_id}")
            assert deleted is None
            print("  ✓ Delete user")
            
            # Test 7: Get stats
            total_users = await db.alen()
            assert total_users == 10  # 11 - 1 deleted
            print("  ✓ Statistics")
            
            # Test 8: Concurrent operations
            results = await asyncio.gather(
                db.aget("user_" + str(uuid.uuid4())),  # Non-existent
                db.alen(),
                db.acontains(user_keys[0])
            )
            assert results[0] is None  # Non-existent user
            assert results[1] == 10  # Total count
            assert results[2] is True  # Key exists
            print("  ✓ Concurrent operations")
    
    print("✅ FastAPI example patterns validated successfully!\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("NanaSQLite Examples Validation")
    print("=" * 60)
    print()
    
    # Test Flask patterns (sync)
    try:
        test_flask_patterns()
    except Exception as e:
        print(f"❌ Flask example validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test FastAPI patterns (async)
    try:
        asyncio.run(test_fastapi_patterns())
    except Exception as e:
        print(f"❌ FastAPI example validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("=" * 60)
    print("✅ All example patterns validated successfully!")
    print("=" * 60)
    print()
    print("Note: This test validates the NanaSQLite patterns used in")
    print("the examples. To run the actual examples, install:")
    print("  - FastAPI example: pip install fastapi uvicorn")
    print("  - Flask example: pip install flask")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
