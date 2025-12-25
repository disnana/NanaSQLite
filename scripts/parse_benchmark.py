#!/usr/bin/env python3
"""Parse multiple benchmark.json files and output improved markdown summary.

New format:
- Top 10 fastest/slowest operations
- Category-based grouping with collapsible sections
- OS comparison in horizontal format
- Performance diff vs previous run (when available)
"""
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def parse_single_benchmark(filepath):
    """1つのbenchmark.jsonをパース"""
    with open(filepath, encoding='utf-8') as f:
        return json.load(f)


def load_previous_benchmark():
    """Load previous benchmark data from gh-pages branch if available."""
    try:
        # Try to get the benchmark data from gh-pages branch
        result = subprocess.run(
            ['git', 'show', 'gh-pages:dev/bench/data.js'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return {}
        
        # Parse the JS file (format: window.BENCHMARK_DATA = {...})
        content = result.stdout
        if 'window.BENCHMARK_DATA' not in content:
            return {}
        
        # Extract JSON part
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start == -1 or json_end == 0:
            return {}
        
        data = json.loads(content[json_start:json_end])
        
        # Get the most recent benchmark entry
        previous = {}
        for entry_name, entries in data.get('entries', {}).items():
            if entries:
                # Get the latest entry
                latest = entries[-1]
                for bench in latest.get('benches', []):
                    name = bench.get('name', '')
                    if '::' in name:
                        name = name.split('::')[-1]
                    if name:
                        # value is in iter/sec, convert to ms: 1000 / (iter/sec) = ms/iter
                        iter_per_sec = bench.get('value', 0)
                        if iter_per_sec > 0:
                            previous[name] = 1000.0 / iter_per_sec  # Convert iter/sec to ms
                        else:
                            previous[name] = 0
        
        return previous
    except Exception:
        return {}


def format_time(ms):
    """時間を適切な単位でフォーマット"""
    if ms < 0.001:
        # 1 ms = 1,000,000 ns, so ms * 1,000,000 = ns
        return f"{ms * 1000000:.2f}ns"
    elif ms < 1:
        # 1 ms = 1,000 µs, so ms * 1,000 = µs
        return f"{ms * 1000:.2f}µs"
    elif ms < 1000:
        return f"{ms:.3f}ms"
    else:
        return f"{ms / 1000:.2f}s"


def format_ops(ms):
    """1秒あたりの操作回数(Ops/sec)をフォーマット"""
    if ms <= 0:
        return "0"
    ops = 1000.0 / ms
    if ops >= 1000000:
        return f"{ops / 1000000:.2f}M"
    elif ops >= 1000:
        return f"{ops / 1000:.1f}k"
    else:
        return f"{ops:.1f}"


def format_diff(current_ms, previous_ms):
    """Format performance difference with emoji indicator."""
    if previous_ms is None or previous_ms <= 0:
        return "-"
    
    diff_ms = current_ms - previous_ms
    diff_pct = ((current_ms / previous_ms) - 1) * 100
    
    # Determine emoji based on performance change
    if diff_pct <= -5:
        emoji = "🚀"  # Significant improvement
    elif diff_pct <= -1:
        emoji = "✅"  # Minor improvement
    elif diff_pct < 1:
        emoji = "➖"  # No change
    elif diff_pct < 5:
        emoji = "⚠️"  # Minor regression
    else:
        emoji = "🔴"  # Significant regression
    
    # Format the difference string
    if diff_ms >= 0:
        sign = "+"
    else:
        sign = ""
    
    return f"{emoji} {sign}{diff_pct:.1f}%"


def categorize_test(test_name):
    """テスト名からカテゴリを判定"""
    name_lower = test_name.lower()
    
    if 'write' in name_lower or 'insert' in name_lower or 'set' in name_lower:
        return "✍️ Write Operations"
    elif 'read' in name_lower or 'get' in name_lower or 'fetch' in name_lower or 'load' in name_lower:
        return "📖 Read Operations"
    elif 'batch' in name_lower:
        return "📦 Batch Operations"
    elif 'concurrent' in name_lower or 'mixed' in name_lower:
        return "🔄 Concurrency"
    elif 'query' in name_lower or 'sql' in name_lower or 'execute' in name_lower:
        return "🗃️ SQL Operations"
    elif 'table' in name_lower or 'index' in name_lower or 'schema' in name_lower or 'drop' in name_lower or 'create' in name_lower:
        return "🏗️ Schema Operations"
    elif 'pydantic' in name_lower or 'model' in name_lower:
        return "🔷 Pydantic Operations"
    elif 'dict' in name_lower or 'keys' in name_lower or 'values' in name_lower or 'items' in name_lower or 'contains' in name_lower or 'len' in name_lower or 'pop' in name_lower or 'setdefault' in name_lower or 'to_dict' in name_lower:
        return "📋 Dict Operations"
    elif 'vacuum' in name_lower or 'refresh' in name_lower or 'pragma' in name_lower or 'copy' in name_lower or 'clear' in name_lower or 'update' in name_lower:
        return "🔧 Utility Operations"
    elif 'transaction' in name_lower or 'commit' in name_lower or 'rollback' in name_lower:
        return "💾 Transaction Operations"
    else:
        return "📊 Other Operations"


def get_os_emoji(os_name):
    """OS名から絵文字を取得"""
    if 'ubuntu' in os_name.lower():
        return '🐧'
    elif 'windows' in os_name.lower():
        return '🪟'
    elif 'macos' in os_name.lower():
        return '🍎'
    else:
        return '💻'


def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    benchmark_type = sys.argv[2] if len(sys.argv) > 2 else 'sync'  # 'sync' or 'async'
    results_path = Path(results_dir)
    
    # Load previous benchmark data for comparison
    previous_data = load_previous_benchmark()
    
    # 全ベンチマーク結果を収集
    all_results = {}
    
    # ベンチマーク結果ファイルのパターン
    if benchmark_type == 'async':
        dir_pattern = 'async-benchmark-results-'
        file_name = 'async-benchmark.json'
    else:
        dir_pattern = 'benchmark-results-'
        file_name = 'benchmark.json'
    
    # ディレクトリ内のベンチマーク結果を探す
    if results_path.is_dir():
        for subdir in results_path.iterdir():
            if subdir.is_dir() and subdir.name.startswith(dir_pattern):
                benchmark_file = subdir / file_name
                if benchmark_file.exists():
                    platform = subdir.name.replace(dir_pattern, '')
                    try:
                        all_results[platform] = parse_single_benchmark(benchmark_file)
                    except json.JSONDecodeError:
                        print(f"Warning: Failed to parse {benchmark_file}", file=sys.stderr)
    
    if not all_results:
        print("No benchmark results found.")
        return
    
    # 全テスト結果を集計
    test_data = defaultdict(lambda: {'by_os': defaultdict(list), 'all_means': []})
    os_set = set()
    
    for platform, data in all_results.items():
        parts = platform.rsplit('-py', 1)
        if len(parts) == 2:
            os_name = parts[0]
            py_version = parts[1]
        else:
            os_name = platform
            py_version = 'unknown'
        
        os_set.add(os_name)
        
        for b in data.get('benchmarks', []):
            name = b['name'].split('::')[-1]
            mean = b['stats']['mean'] * 1000  # ms
            
            test_data[name]['by_os'][os_name].append({
                'py': py_version,
                'mean': mean
            })
            test_data[name]['all_means'].append({
                'os': os_name,
                'py': py_version,
                'mean': mean
            })
    
    if not test_data:
        print("No benchmark data to display.")
        return
    
    # OS名をソート
    sorted_os = sorted(os_set)
    
    # ========== Top 10 Fastest / Slowest ==========
    # 各テストの平均時間を計算
    test_averages = []
    for test_name, data in test_data.items():
        means = [x['mean'] for x in data['all_means']]
        avg = sum(means) / len(means) if means else 0
        fastest = min(data['all_means'], key=lambda x: x['mean']) if data['all_means'] else None
        test_averages.append({
            'name': test_name,
            'avg': avg,
            'fastest': fastest
        })
    
    # Top 10 Fastest
    sorted_by_speed = sorted(test_averages, key=lambda x: x['avg'])
    print("#### 🏆 Top 10 Fastest Operations\n")
    print("| Rank | Test | Avg Time | Ops/sec | vs Prev | Fastest Platform |")
    print("|------|------|----------|---------|---------|------------------|")
    
    for i, item in enumerate(sorted_by_speed[:10], 1):
        fastest_str = f"{item['fastest']['os']} py{item['fastest']['py']}" if item['fastest'] else "-"
        prev_ms = previous_data.get(item['name'])
        diff_str = format_diff(item['avg'], prev_ms)
        print(f"| {i} | {item['name']} | {format_time(item['avg'])} | {format_ops(item['avg'])} | {diff_str} | {fastest_str} |")
    
    print()
    
    # Top 10 Slowest
    sorted_by_slow = sorted(test_averages, key=lambda x: x['avg'], reverse=True)
    print("#### 🐢 Top 10 Slowest Operations\n")
    print("| Rank | Test | Avg Time | Ops/sec | vs Prev | Slowest Platform |")
    print("|------|------|----------|---------|---------|------------------|")
    
    for i, item in enumerate(sorted_by_slow[:10], 1):
        slowest = max(test_data[item['name']]['all_means'], key=lambda x: x['mean']) if test_data[item['name']]['all_means'] else None
        slowest_str = f"{slowest['os']} py{slowest['py']}" if slowest else "-"
        prev_ms = previous_data.get(item['name'])
        diff_str = format_diff(item['avg'], prev_ms)
        print(f"| {i} | {item['name']} | {format_time(item['avg'])} | {format_ops(item['avg'])} | {diff_str} | {slowest_str} |")
    
    print()
    
    # ========== Category-based Grouping ==========
    categories = defaultdict(list)
    for test_name, data in test_data.items():
        category = categorize_test(test_name)
        means = [x['mean'] for x in data['all_means']]
        avg = sum(means) / len(means) if means else 0
        
        # OS別の平均値を計算
        os_avgs = {}
        for os_name in sorted_os:
            os_means = [x['mean'] for x in data['by_os'].get(os_name, [])]
            os_avgs[os_name] = sum(os_means) / len(os_means) if os_means else None
        
        categories[category].append({
            'name': test_name,
            'avg': avg,
            'os_avgs': os_avgs
        })
    
    print("#### 📋 Results by Category\n")
    
    # カテゴリごとに出力
    for category in sorted(categories.keys()):
        tests = categories[category]
        tests_sorted = sorted(tests, key=lambda x: x['avg'])
        
        # ヘッダー作成
        os_headers = " | ".join([f"{get_os_emoji(os)} {os.replace('-latest', '')}" for os in sorted_os])
        
        print(f"<details><summary>{category} ({len(tests)} tests)</summary>\n")
        print(f"| Test | Avg | Ops/sec | vs Prev | {os_headers} |")
        print(f"|------|-----|---------|---------|" + "|".join(["-----"] * len(sorted_os)) + "|")
        
        for test in tests_sorted:
            os_values = []
            for os_name in sorted_os:
                val = test['os_avgs'].get(os_name)
                if val:
                    os_values.append(f"{format_time(val)}<br>({format_ops(val)})")
                else:
                    os_values.append("-")
            
            os_cells = " | ".join(os_values)
            prev_ms = previous_data.get(test['name'])
            diff_str = format_diff(test['avg'], prev_ms)
            print(f"| {test['name']} | {format_time(test['avg'])} | {format_ops(test['avg'])} | {diff_str} | {os_cells} |")
        
        print("\n</details>\n")
    
    # ========== Summary Stats ==========
    has_significant_regression = False
    if test_averages:
        improvements = 0
        regressions = 0
        severe_regressions = 0  # >20% slower
        unchanged = 0
        no_data = 0
        
        regression_threshold = float(os.environ.get('BENCHMARK_REGRESSION_THRESHOLD', '20'))
        
        for item in test_averages:
            prev_ms = previous_data.get(item['name'])
            if prev_ms and prev_ms > 0:
                diff_pct = ((item['avg'] / prev_ms) - 1) * 100
                if diff_pct <= -1:
                    improvements += 1
                elif diff_pct >= regression_threshold:
                    severe_regressions += 1
                    regressions += 1
                elif diff_pct >= 1:
                    regressions += 1
                else:
                    unchanged += 1
            else:
                no_data += 1
        
        total_compared = improvements + regressions + unchanged
        if total_compared > 0:
            print("#### 📈 Performance Summary vs Previous\n")
            print(f"- 🚀 **Improved**: {improvements} tests")
            print(f"- ➖ **Unchanged**: {unchanged} tests")
            print(f"- ⚠️ **Regressed**: {regressions} tests")
            if severe_regressions > 0:
                print(f"- 🔴 **Severe (>{regression_threshold:.0f}%)**: {severe_regressions} tests")
                has_significant_regression = True
            if no_data > 0:
                print(f"- ❓ **No previous data**: {no_data} tests")
            print()
    
    # Return exit code 2 if significant regression detected
    # (exit code 1 is reserved for errors)
    return 2 if has_significant_regression else 0


if __name__ == '__main__':
    import os
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error parsing benchmark results: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

