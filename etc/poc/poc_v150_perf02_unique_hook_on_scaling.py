#!/usr/bin/env python3
"""
POC for PERF-02: UniqueHook O(N) Performance Scaling Issue

This script demonstrates how UniqueHook.before_write() performs
O(N) linear search for uniqueness checking, causing performance
degradation with large datasets.
"""

import os
import random
import string
import tempfile
import time

from nanasqlite import NanaSQLite
from nanasqlite.hooks import UniqueHook


def generate_random_email():
    """Generate a random email address."""
    username = ''.join(random.choices(string.ascii_lowercase, k=8))
    domain = ''.join(random.choices(string.ascii_lowercase, k=6))
    return f"{username}@{domain}.com"


def test_unique_hook_performance_scaling():
    """Test performance scaling of UniqueHook with increasing data size."""

    print("=== UniqueHook O(N) Performance Scaling Test ===")

    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(delete=False) as f:
        db_path = f.name

    try:
        db = NanaSQLite(db_path, table="users")
        db.add_hook(UniqueHook("email"))

        # Test different dataset sizes
        test_sizes = [100, 500, 1000, 2000]
        performance_results = []

        print("\n--- Populating database and measuring performance ---")

        for target_size in test_sizes:
            print(f"\nTesting with {target_size} records...")

            # Add more records to reach target size
            current_size = len(list(db.keys()))
            records_to_add = target_size - current_size

            if records_to_add > 0:
                print(f"Adding {records_to_add} records...")

                # Add records without UniqueHook to build up data quickly
                db._hooks.clear()  # Temporarily disable hooks

                for i in range(records_to_add):
                    user_id = f"user_{current_size + i + 1}"
                    email = generate_random_email()
                    db[user_id] = {
                        "name": f"User {current_size + i + 1}",
                        "email": email
                    }

                # Re-enable UniqueHook for testing
                db.add_hook(UniqueHook("email"))

                print(f"Database now has {len(list(db.keys()))} records")

            # Test performance of adding one more record with UniqueHook
            print("Measuring UniqueHook performance...")

            new_email = generate_random_email()
            new_user_data = {
                "name": f"Test User {target_size + 1}",
                "email": new_email
            }

            # Measure time for uniqueness checking
            start_time = time.perf_counter()

            try:
                db[f"test_user_{target_size}"] = new_user_data
                write_time = time.perf_counter() - start_time
                success = True
            except Exception as e:
                write_time = time.perf_counter() - start_time
                success = False
                print(f"Write failed: {e}")

            performance_results.append({
                "size": target_size,
                "time_ms": write_time * 1000,
                "success": success
            })

            print(f"Write time: {write_time * 1000:.2f}ms")

        print("\n--- Performance Analysis ---")
        print("Size\tTime (ms)\tTime per record (μs)")
        print("-" * 40)

        baseline_time = None
        scaling_issue_detected = False

        for result in performance_results:
            size = result["size"]
            time_ms = result["time_ms"]
            time_per_record_us = (time_ms * 1000) / size

            print(f"{size}\t{time_ms:.2f}\t\t{time_per_record_us:.2f}")

            if baseline_time is None:
                baseline_time = time_ms
            else:
                # Check if time increased significantly more than linearly
                actual_ratio = time_ms / baseline_time
                expected_ratio = size / test_sizes[0]

                if actual_ratio > expected_ratio * 1.5:  # 50% worse than linear
                    print(f"⚠️  Performance degradation detected: {actual_ratio:.1f}x vs expected {expected_ratio:.1f}x")
                    scaling_issue_detected = True

        print("\n--- Scaling Analysis ---")
        if len(performance_results) >= 2:
            first = performance_results[0]
            last = performance_results[-1]

            size_ratio = last["size"] / first["size"]
            time_ratio = last["time_ms"] / first["time_ms"]

            print(f"Size increased by: {size_ratio:.1f}x")
            print(f"Time increased by: {time_ratio:.1f}x")

            if time_ratio > size_ratio * 1.2:  # More than 20% worse than linear
                print("🐛 BUG: Performance scaling is worse than O(N) - likely O(N²) or worse!")
                scaling_issue_detected = True
            elif time_ratio > size_ratio:
                print("⚠️  WARNING: Performance scaling appears to be O(N) - could be improved")
                scaling_issue_detected = True
            else:
                print("✅ PASS: Performance scaling is better than linear")

        # Test with duplicate email to ensure hook is working
        print("\n--- Testing duplicate detection ---")
        try:
            # Get an existing email
            existing_users = list(db.items())
            if existing_users:
                existing_email = existing_users[0][1]["email"]

                start_time = time.perf_counter()
                db["duplicate_test"] = {
                    "name": "Duplicate Test",
                    "email": existing_email  # This should fail
                }
                print("🐛 BUG: Duplicate email was allowed!")
                return "BUG"

        except Exception as e:
            duplicate_time = time.perf_counter() - start_time
            print(f"✅ Duplicate correctly rejected in {duplicate_time * 1000:.2f}ms: {type(e).__name__}")

        if scaling_issue_detected:
            print("\n🐛 BUG: UniqueHook has O(N) scaling issues with large datasets!")
            return "BUG"
        else:
            print("\n✅ PASS: No significant performance scaling issues detected.")
            return "PASS"

    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_direct_hook_performance():
    """Test the hook's direct performance without database overhead."""
    print("\n=== Direct UniqueHook Performance Test ===")

    with tempfile.NamedTemporaryFile(delete=False) as f:
        db_path = f.name

    try:
        # Create database with various sizes of data
        db = NanaSQLite(db_path, table="users")

        # Pre-populate without hooks for speed
        sizes_to_test = [1000, 5000]

        for size in sizes_to_test:
            print(f"\nTesting direct hook performance with {size} existing records...")

            # Clear and repopulate
            db.clear()

            # Add records without hooks
            for i in range(size):
                db[f"user_{i}"] = {"email": f"user{i}@test.com", "name": f"User {i}"}

            # Create hook and test performance
            hook = UniqueHook("email")

            # Test time for uniqueness check
            new_user_data = {"email": "newuser@test.com", "name": "New User"}

            start_time = time.perf_counter()
            _ = hook.before_write(db, "new_user", new_user_data)
            elapsed = time.perf_counter() - start_time

            print(f"Hook execution time: {elapsed * 1000:.2f}ms")
            print(f"Time per existing record: {(elapsed * 1000 * 1000) / size:.2f}μs")

            # Test duplicate detection performance
            duplicate_data = {"email": "user500@test.com", "name": "Duplicate User"}

            start_time = time.perf_counter()
            try:
                hook.before_write(db, "duplicate_user", duplicate_data)
                print("🐛 BUG: Duplicate not detected!")
            except Exception as e:
                elapsed = time.perf_counter() - start_time
                print(f"Duplicate detection time: {elapsed * 1000:.2f}ms")
                print(f"✅ Duplicate correctly detected: {type(e).__name__}")

        return "PASS"

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    print("Testing UniqueHook O(N) performance scaling...\n")

    result1 = test_unique_hook_performance_scaling()
    test_direct_hook_performance()

    if result1 == "BUG":
        final_result = "BUG"
    else:
        final_result = "PASS"

    print(f"\nFinal test result: {final_result}")
