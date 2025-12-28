#!/usr/bin/env python3
"""
NanaSQLite AsyncDemo: Demonstrate async/await support

This script demonstrates the async features of NanaSQLite rc7,
showing how to use it in async applications without blocking.
"""

import asyncio
import time

from nanasqlite import AsyncNanaSQLite


async def basic_async_demo():
    """Basic async operations demo"""
    print("\n=== Basic Async Operations Demo ===")

    async with AsyncNanaSQLite("demo_async.db") as db:
        # Set data asynchronously
        print("Setting data...")
        await db.aset("user", {"name": "Nana", "age": 20, "role": "admin"})
        await db.aset("config", {"theme": "dark", "language": "ja"})

        # Get data asynchronously
        print("Getting data...")
        user = await db.aget("user")
        print(f"User: {user}")

        config = await db.aget("config")
        print(f"Config: {config}")

        # Check existence
        if await db.acontains("user"):
            print("User exists in database")

        # Update data
        await db.aupdate({"settings": {"notifications": True}})
        print("Settings updated")


async def concurrent_operations_demo():
    """Demonstrate concurrent async operations"""
    print("\n=== Concurrent Operations Demo ===")

    async with AsyncNanaSQLite("demo_async.db") as db:
        # Prepare some data
        await db.batch_update({
            f"user_{i}": {"name": f"User{i}", "score": i * 10}
            for i in range(10)
        })

        # Fetch multiple keys concurrently
        print("Fetching 10 users concurrently...")
        start = time.time()

        results = await asyncio.gather(
            *[db.aget(f"user_{i}") for i in range(10)]
        )

        elapsed = time.time() - start
        print(f"Fetched {len(results)} users in {elapsed:.4f} seconds")
        print(f"First user: {results[0]}")
        print(f"Last user: {results[-1]}")


async def batch_operations_demo():
    """Demonstrate batch operations"""
    print("\n=== Batch Operations Demo ===")

    async with AsyncNanaSQLite("demo_async.db") as db:
        # Batch update
        print("Batch updating 1000 items...")
        start = time.time()

        data = {f"item_{i}": {"value": i, "status": "active"} for i in range(1000)}
        await db.batch_update(data)

        elapsed = time.time() - start
        print(f"Batch update completed in {elapsed:.4f} seconds")

        # Get count
        count = await db.alen()
        print(f"Total items in database: {count}")

        # Batch delete
        print("Batch deleting 500 items...")
        start = time.time()

        keys_to_delete = [f"item_{i}" for i in range(500)]
        await db.batch_delete(keys_to_delete)

        elapsed = time.time() - start
        print(f"Batch delete completed in {elapsed:.4f} seconds")

        count = await db.alen()
        print(f"Remaining items: {count}")


async def sql_operations_demo():
    """Demonstrate async SQL operations"""
    print("\n=== Async SQL Operations Demo ===")

    async with AsyncNanaSQLite("demo_async.db") as db:
        # Create a table
        print("Creating users table...")
        await db.create_table("users", {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT NOT NULL",
            "email": "TEXT UNIQUE",
            "age": "INTEGER"
        })

        # Insert data
        print("Inserting users...")
        await db.sql_insert("users", {"name": "Alice", "email": "alice@example.com", "age": 25})
        await db.sql_insert("users", {"name": "Bob", "email": "bob@example.com", "age": 30})
        await db.sql_insert("users", {"name": "Charlie", "email": "charlie@example.com", "age": 22})

        # Query data
        print("Querying users...")
        results = await db.query(
            table_name="users",
            columns=["name", "email", "age"],
            where="age > ?",
            parameters=(23,),
            order_by="age ASC"
        )

        print(f"Found {len(results)} users over 23:")
        for user in results:
            print(f"  - {user['name']} ({user['age']}): {user['email']}")

        # Update data
        print("Updating Bob's age...")
        count = await db.sql_update("users", {"age": 31}, "name = ?", ("Bob",))
        print(f"Updated {count} user(s)")


async def fastapi_simulation_demo():
    """Simulate async web framework usage (like FastAPI)"""
    print("\n=== FastAPI Simulation Demo ===")
    print("Simulating multiple concurrent web requests...")

    async with AsyncNanaSQLite("demo_async.db") as db:
        # Prepare user data
        await db.batch_update({
            f"user_{i}": {"name": f"User{i}", "status": "active"}
            for i in range(100)
        })

        # Simulate 10 concurrent API requests
        async def handle_request(user_id):
            """Simulate an API request handler"""
            await asyncio.sleep(0.01)  # Simulate network delay
            user = await db.aget(f"user_{user_id}")
            return {"user_id": user_id, "data": user}

        print("Processing 10 concurrent requests...")
        start = time.time()

        responses = await asyncio.gather(
            *[handle_request(i) for i in range(10)]
        )

        elapsed = time.time() - start
        print(f"All requests completed in {elapsed:.4f} seconds")
        print(f"Sample response: {responses[0]}")
        print("✓ No blocking occurred!")


async def main():
    """Run all demos"""
    print("╔═══════════════════════════════════════════╗")
    print("║  NanaSQLite rc7 - Async Support Demo     ║")
    print("╚═══════════════════════════════════════════╝")

    try:
        await basic_async_demo()
        await concurrent_operations_demo()
        await batch_operations_demo()
        await sql_operations_demo()
        await fastapi_simulation_demo()

        print("\n" + "="*50)
        print("✓ All demos completed successfully!")
        print("="*50)

    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        raise

    finally:
        # Clean up demo database
        import os
        if os.path.exists("demo_async.db"):
            os.remove("demo_async.db")
        if os.path.exists("demo_async.db-wal"):
            os.remove("demo_async.db-wal")
        if os.path.exists("demo_async.db-shm"):
            os.remove("demo_async.db-shm")
        print("\nDemo database cleaned up.")


if __name__ == "__main__":
    asyncio.run(main())
