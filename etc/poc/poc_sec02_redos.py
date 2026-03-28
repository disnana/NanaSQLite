# etc/poc/poc_sec02_redos.py
import re
import time


def evaluate_regex(pattern: str, test_string: str) -> float:
    start = time.perf_counter()
    re.match(pattern, test_string)
    end = time.perf_counter()
    return end - start


def main():
    print("--- SEC-02 column_type ReDoS POC ---")

    # SonarQubeで警告された脆弱なパターン
    vulnerable_pattern = r"^[A-Za-z][\w ]*(\([\d, ]+\))?$"

    # 修正後の安全なパターン
    safe_pattern = r"^[A-Za-z][a-zA-Z0-9_]*(?:\s+[a-zA-Z0-9_]+)*(\s*\([\d,\s]+\))?$"

    # テストケース
    # 長大な空白文字列の末尾にマッチしない文字 (!) を付与
    test_string = "A" + " " * 1000000 + "!"

    print("Evaluating vulnerable pattern...")
    vuln_time = evaluate_regex(vulnerable_pattern, test_string)
    print(f"Vulnerable pattern time: {vuln_time:.6f} seconds")

    print("Evaluating safe pattern...")
    safe_time = evaluate_regex(safe_pattern, test_string)
    print(f"Safe pattern time: {safe_time:.6f} seconds")

    print("--- 正常系テスト ---")
    valid_types = ["INTEGER", "DOUBLE PRECISION", "VARCHAR(255)", "DECIMAL (10, 2)"]
    for v in valid_types:
        assert re.match(safe_pattern, v) is not None, f"Failed to match valid type: {v}"
    print("全ての正常な型にマッチしました。")


if __name__ == "__main__":
    main()
