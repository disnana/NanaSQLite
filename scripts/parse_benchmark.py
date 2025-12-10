#!/usr/bin/env python3
"""Parse multiple benchmark.json files and output combined markdown table."""
import json
import sys
import os
from pathlib import Path
from collections import defaultdict


def parse_single_benchmark(filepath):
    """1つのbenchmark.jsonをパース"""
    with open(filepath, encoding='utf-8') as f:
        return json.load(f)


def format_time(ms):
    """時間を適切な単位でフォーマット"""
    if ms < 0.001:
        return f"{ms * 1000000:.2f}µs"
    elif ms < 1:
        return f"{ms * 1000:.2f}µs"
    elif ms < 1000:
        return f"{ms:.3f}ms"
    else:
        return f"{ms / 1000:.2f}s"


def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    results_path = Path(results_dir)
    
    # 全ベンチマーク結果を収集
    all_results = {}
    
    # ディレクトリ内のベンチマーク結果を探す
    if results_path.is_dir():
        for subdir in results_path.iterdir():
            if subdir.is_dir() and subdir.name.startswith('benchmark-results-'):
                benchmark_file = subdir / 'benchmark.json'
                if benchmark_file.exists():
                    # プラットフォーム名を抽出 (例: ubuntu-latest-py3.11)
                    platform = subdir.name.replace('benchmark-results-', '')
                    try:
                        all_results[platform] = parse_single_benchmark(benchmark_file)
                    except json.JSONDecodeError:
                        print(f"Warning: Failed to parse {benchmark_file}", file=sys.stderr)
    
    if not all_results:
        # 従来の動作: 単一ファイル (後方互換性)
        single_file = Path('benchmark.json')
        if single_file.exists():
            with open(single_file, encoding='utf-8') as f:
                data = json.load(f)
            print("| Test | Mean (ms) | Min (ms) | Max (ms) | Rounds |")
            print("|------|-----------|----------|----------|--------|")
            for b in data.get('benchmarks', []):
                name = b['name'].split('::')[-1]
                mean = b['stats']['mean'] * 1000
                min_t = b['stats']['min'] * 1000
                max_t = b['stats']['max'] * 1000
                rounds = b['stats']['rounds']
                print(f"| {name} | {mean:.3f} | {min_t:.3f} | {max_t:.3f} | {rounds} |")
            return
        else:
            print("No benchmark results found.", file=sys.stderr)
            sys.exit(1)
    
    # OS別にグループ化
    os_groups = defaultdict(dict)
    for platform, data in all_results.items():
        # platform形式: ubuntu-latest-py3.11 または windows-latest-py3.11
        parts = platform.rsplit('-py', 1)
        if len(parts) == 2:
            os_name = parts[0]
            py_version = parts[1]
            os_groups[os_name][py_version] = data
        else:
            os_groups[platform]['unknown'] = data
    
    # テスト名ごとの結果を集計（全体比較用）
    test_summary = defaultdict(list)
    
    # OS別に出力
    for os_name in sorted(os_groups.keys()):
        py_versions = os_groups[os_name]
        
        # OSの絵文字
        if 'ubuntu' in os_name.lower():
            os_emoji = '🐧'
        elif 'windows' in os_name.lower():
            os_emoji = '🪟'
        elif 'macos' in os_name.lower():
            os_emoji = '🍎'
        else:
            os_emoji = '💻'
        
        print(f"\n### {os_emoji} {os_name}\n")
        
        # Pythonバージョンでソート
        sorted_versions = sorted(py_versions.keys(), key=lambda x: tuple(map(int, x.split('.'))) if x != 'unknown' else (0,))
        
        for py_version in sorted_versions:
            data = py_versions[py_version]
            benchmarks = data.get('benchmarks', [])
            
            if not benchmarks:
                print(f"<details><summary>Python {py_version}: No benchmark data</summary></details>\n")
                continue
            
            print(f"<details><summary>Python {py_version} ({len(benchmarks)} tests)</summary>\n")
            print("| Test | Mean | Min | Max | Rounds |")
            print("|------|------|-----|-----|--------|")
            
            for b in benchmarks:
                name = b['name'].split('::')[-1]
                mean = b['stats']['mean'] * 1000
                min_t = b['stats']['min'] * 1000
                max_t = b['stats']['max'] * 1000
                rounds = b['stats']['rounds']
                
                # サマリー用に記録
                test_summary[name].append({
                    'os': os_name,
                    'py': py_version,
                    'mean': mean
                })
                
                print(f"| {name} | {format_time(mean)} | {format_time(min_t)} | {format_time(max_t)} | {rounds} |")
            
            print("\n</details>\n")
    
    # 全体サマリー（最速/最遅の比較）
    if test_summary:
        print("\n### 📈 Performance Summary (Average across all platforms)\n")
        print("| Test | Avg Mean | Fastest | Slowest |")
        print("|------|----------|---------|---------|")
        
        for test_name in sorted(test_summary.keys()):
            results = test_summary[test_name]
            if results:
                means = [r['mean'] for r in results]
                avg = sum(means) / len(means)
                fastest = min(results, key=lambda x: x['mean'])
                slowest = max(results, key=lambda x: x['mean'])
                
                fastest_str = f"{fastest['os']} py{fastest['py']}"
                slowest_str = f"{slowest['os']} py{slowest['py']}"
                
                print(f"| {test_name} | {format_time(avg)} | {fastest_str} | {slowest_str} |")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error parsing benchmark results: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
