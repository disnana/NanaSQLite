#!/usr/bin/env python3
"""Parse benchmark.json and output markdown table."""
import json
import sys

try:
    with open('benchmark.json') as f:
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
except Exception as e:
    print(f"Error parsing benchmark.json: {e}", file=sys.stderr)
    sys.exit(1)
