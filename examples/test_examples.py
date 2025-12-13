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

# Import Pydantic (optional, for Pydantic test)
try:
    from pydantic import BaseModel, ValidationError, field_validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

# Import Quart (optional, for Quart test)
try:
    from quart import Quart
    QUART_AVAILABLE = True
except ImportError:
    QUART_AVAILABLE = False


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
                    assert user is not None, f"Data integrity error: key '{key}' exists but has no value"
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


def test_pydantic_patterns():
    """Test patterns used in Pydantic demo example"""
    if not PYDANTIC_AVAILABLE:
        print("Skipping Pydantic example patterns (Pydantic not installed)...")
        return

    print("Testing Pydantic example patterns...")

    # Define test models
    class User(BaseModel):
        id: str
        name: str
        email: str
        age: int
        active: bool = True

        @field_validator('age')
        @classmethod
        def age_must_be_positive(cls, v):
            if v < 0:
                raise ValueError('Age must be positive')
            return v

        @field_validator('email')
        @classmethod
        def email_must_contain_at(cls, v):
            if '@' not in v:
                raise ValueError('Email must contain @')
            return v

    class UserCreate(BaseModel):
        name: str
        email: str
        age: int
        active: bool = True

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_pydantic.db")
        db = NanaSQLite(db_path, bulk_load=False)

        try:
            # Test 1: Create users with validation
            users_data = [
                {"name": "Alice", "email": "alice@example.com", "age": 25},
                {"name": "Bob", "email": "bob@example.com", "age": 30},
            ]

            created_users = []
            for user_data in users_data:
                user_create = UserCreate(**user_data)
                user = User(id=str(uuid.uuid4()), **user_create.model_dump())
                db[user.id] = user.model_dump()
                created_users.append(user)
                print(f"  ✓ Created user: {user.name}")

            # Test 2: Validation error handling
            try:
                invalid_user = UserCreate(name="Invalid", email="invalid-email", age=-5)
                # UserCreate doesn't have validators, so create User to trigger validation
                invalid_full_user = User(id=str(uuid.uuid4()), **invalid_user.model_dump())
                assert False, "Should have raised ValidationError"
            except ValidationError:
                print("  ✓ Validation error caught for invalid data")

            # Test 3: Retrieve and validate users
            for user in created_users:
                user_data = db[user.id]
                retrieved_user = User(**user_data)
                assert retrieved_user.name == user.name
                assert retrieved_user.email == user.email
                assert retrieved_user.age == user.age
                print(f"  ✓ Retrieved and validated user: {retrieved_user.name}")

            # Test 4: Update user
            user_to_update = created_users[0]
            user_data = db[user_to_update.id]
            user = User(**user_data)
            user.age += 1
            db[user.id] = user.model_dump()
            updated_data = db[user.id]
            updated_user = User(**updated_data)
            assert updated_user.age == user.age
            print(f"  ✓ Updated user age to {updated_user.age}")

            # Test 5: Model serialization
            user_dict = user.model_dump()
            assert isinstance(user_dict, dict)
            assert 'name' in user_dict

            user_json = user.model_dump_json()
            assert isinstance(user_json, str)
            print("  ✓ Model serialization works")

        finally:
            db.close()

    print("✅ Pydantic example patterns validated successfully!\n")


def test_quart_patterns():
    """Test patterns used in Quart demo example"""
    if not QUART_AVAILABLE:
        print("Skipping Quart example patterns (Quart not installed)...")
        return

    print("Testing Quart example patterns...")

    # Create a minimal Quart app for testing
    app = Quart(__name__)

    @app.route('/test')
    async def test_route():
        return {"message": "test"}

    # Test that Quart app can be created
    assert app is not None
    print("  ✓ Quart app creation")

    # Test async context manager pattern (similar to the demo)
    async def test_async_db():
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_quart.db")

            async with AsyncNanaSQLite(db_path, max_workers=5, bulk_load=False) as db:
                # Test basic async operations
                task_id = f"task_{uuid.uuid4()}"
                task_data = {
                    "title": "Test Task",
                    "completed": False,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }

                await db.aset(task_id, task_data)
                retrieved = await db.aget(task_id)
                assert retrieved["title"] == "Test Task"
                assert retrieved["completed"] is False
                print("  ✓ Async database operations")

                # Test task listing
                tasks = []
                keys = await db.akeys()
                for key in keys:
                    if key.startswith("task_"):
                        task = await db.aget(key)
                        task['id'] = key
                        tasks.append(task)
                assert len(tasks) == 1
                print("  ✓ Task listing")

                # Test task toggle
                task_data["completed"] = True
                await db.aset(task_id, task_data)
                updated = await db.aget(task_id)
                assert updated["completed"] is True
                print("  ✓ Task completion toggle")

                # Test task deletion
                await db.adelete(task_id)
                deleted = await db.aget(task_id)
                assert deleted is None
                print("  ✓ Task deletion")

    # Run async test
    asyncio.run(test_async_db())

    print("✅ Quart example patterns validated successfully!\n")


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

    # Test Pydantic patterns (optional)
    try:
        test_pydantic_patterns()
    except Exception as e:
        print(f"❌ Pydantic example validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test Quart patterns (optional)
    try:
        test_quart_patterns()
    except Exception as e:
        print(f"❌ Quart example validation failed: {e}")
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
    print("  - Pydantic example: pip install pydantic")
    print("  - Quart example: pip install quart hypercorn")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
