#!/usr/bin/env python3
"""
POC for BUG-05: PydanticHook Silent Exception Suppression

This script demonstrates how PydanticHook.after_read() suppresses all exceptions,
potentially masking critical errors and returning corrupted data.
"""

import os
import tempfile

from nanasqlite import NanaSQLite
from nanasqlite.hooks import PydanticHook


class MockPydanticModel:
    """Mock Pydantic model that can raise different types of exceptions."""

    @classmethod
    def model_validate(cls, value):
        if value.get("trigger_validation_error"):
            from pydantic import ValidationError
            raise ValidationError("Validation failed", cls)
        elif value.get("trigger_connection_error"):
            raise ConnectionError("Database connection lost")
        elif value.get("trigger_memory_error"):
            raise MemoryError("Out of memory during deserialization")
        elif value.get("trigger_system_error"):
            raise OSError("System I/O error")
        else:
            # Normal successful case
            instance = cls()
            instance.data = value
            return instance


def test_pydantic_hook_exception_suppression():
    """Test that PydanticHook improperly suppresses critical exceptions."""

    print("=== PydanticHook Exception Suppression Test ===")

    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(delete=False) as f:
        db_path = f.name

    try:
        db = NanaSQLite(db_path, table="test_data")
        hook = PydanticHook(MockPydanticModel)
        db.add_hook(hook)

        test_cases = [
            {
                "key": "normal_data",
                "value": {"name": "Normal", "trigger_validation_error": False},
                "description": "Normal data - should work fine",
                "should_suppress": False
            },
            {
                "key": "validation_error_data",
                "value": {"name": "Invalid", "trigger_validation_error": True},
                "description": "Validation error - should be caught and suppressed",
                "should_suppress": True
            },
            {
                "key": "connection_error_data",
                "value": {"name": "Connection Issue", "trigger_connection_error": True},
                "description": "Connection error - should NOT be suppressed",
                "should_suppress": False
            },
            {
                "key": "memory_error_data",
                "value": {"name": "Memory Issue", "trigger_memory_error": True},
                "description": "Memory error - should NOT be suppressed",
                "should_suppress": False
            },
            {
                "key": "system_error_data",
                "value": {"name": "System Issue", "trigger_system_error": True},
                "description": "System error - should NOT be suppressed",
                "should_suppress": False
            }
        ]

        # First, insert data into database
        print("\n--- Inserting test data ---")
        for test_case in test_cases:
            key = test_case["key"]
            value = test_case["value"]
            print(f"Inserting {key}: {value}")

            # Store raw data in DB (bypassing hooks for insertion)
            with db._acquire_lock():
                cursor = db._connection.cursor()
                sql = f"INSERT OR REPLACE INTO {db._safe_table} (key, value) VALUES (?, ?)"
                cursor.execute(sql, (key, db._serialize(value)))

        print("\n--- Testing hook.after_read() behavior ---")

        bug_detected = False

        for test_case in test_cases:
            key = test_case["key"]
            value = test_case["value"]
            description = test_case["description"]
            should_suppress = test_case["should_suppress"]

            print(f"\nTest: {description}")
            print(f"Key: {key}")
            print(f"Expected suppression: {should_suppress}")

            # Test direct hook behavior
            try:
                result = hook.after_read(db, key, value)
                print(f"Hook result: {type(result).__name__} - {getattr(result, 'data', result)}")

                if not should_suppress and value.get("trigger_connection_error"):
                    print("🐛 BUG: ConnectionError was suppressed but should not be!")
                    bug_detected = True
                elif not should_suppress and value.get("trigger_memory_error"):
                    print("🐛 BUG: MemoryError was suppressed but should not be!")
                    bug_detected = True
                elif not should_suppress and value.get("trigger_system_error"):
                    print("🐛 BUG: OSError was suppressed but should not be!")
                    bug_detected = True
                else:
                    print("✅ Behavior as expected (though may still be incorrect)")

            except Exception as e:
                print(f"Exception raised: {type(e).__name__}: {e}")
                if should_suppress:
                    print("❌ UNEXPECTED: Exception should have been suppressed")
                else:
                    print("✅ CORRECT: Critical exception was properly raised")

        print("\n--- Testing real database read with hooks ---")

        # Test actual database read operations
        for test_case in test_cases:
            key = test_case["key"]
            description = test_case["description"]
            should_suppress = test_case["should_suppress"]

            print(f"\nReading {key} from database...")
            print(f"\nReading {description} from database...")

            try:
                # This triggers the full read path including after_read hooks
                result = db[key]
                print(f"Database read result: {result}")

                # Check if we got back the original corrupted data or transformed data
                if isinstance(result, dict) and any(key.startswith("trigger_") for key in result.keys()):
                    if not should_suppress:
                        print("🐛 BUG: Got back raw corrupted data instead of proper error!")
                        bug_detected = True
                    else:
                        print("✅ Validation error properly handled")
                else:
                    print("✅ Data transformation worked or error was handled")

            except Exception as e:
                print(f"Database read exception: {type(e).__name__}: {e}")
                if should_suppress:
                    print("❌ UNEXPECTED: Database operation failed when hook should suppress")

        print("\n--- Summary ---")
        if bug_detected:
            print("🐛 BUG: PydanticHook improperly suppresses critical system exceptions!")
            print("This can mask real errors like connection failures and memory issues.")
            return "BUG"
        else:
            print("✅ PASS: No critical exception suppression detected.")
            return "PASS"

    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_simple_exception_suppression():
    """Simplified test focusing on the bare except clause."""
    print("\n=== Simplified Exception Suppression Test ===")

    hook = PydanticHook(MockPydanticModel)

    # Test data that will trigger different exceptions
    test_data = {"trigger_connection_error": True}

    print("Testing if ConnectionError gets suppressed in after_read()...")

    try:
        # This should raise ConnectionError, but after_read() suppresses it
        result = hook.after_read(None, "test_key", test_data)

        # If we get here, the exception was suppressed
        print(f"Result: {result}")
        print("🐛 BUG: ConnectionError was suppressed! This should not happen.")
        return "BUG"

    except ConnectionError:
        print("✅ PASS: ConnectionError was properly raised.")
        return "PASS"
    except Exception as e:
        print(f"Unexpected exception: {type(e).__name__}: {e}")
        return "ERROR"


if __name__ == "__main__":
    print("Testing PydanticHook exception suppression vulnerability...\n")

    result1 = test_pydantic_hook_exception_suppression()
    result2 = test_simple_exception_suppression()

    if result1 == "BUG" or result2 == "BUG":
        final_result = "BUG"
    else:
        final_result = "PASS"

    print(f"\nFinal test result: {final_result}")
