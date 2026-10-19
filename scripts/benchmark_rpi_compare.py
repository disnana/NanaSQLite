"""Compare two immutable release snapshots inside one offline RPI container."""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from benchmark_operational import CASES
from benchmark_operational import main as run_paired

ROOT = Path(__file__).resolve().parents[1]


def run_suite(source: Path, version: str, suite: str, output: Path) -> dict:
    # Import and assert the selected snapshot before pytest can import the installed package.
    code = (
        "import sys; from pathlib import Path; import nanasqlite; "
        f"assert Path(nanasqlite.__file__).resolve().is_relative_to(Path({str(source)!r}).resolve()); "
        f"assert nanasqlite.__version__ == {version!r}; "
        "import pytest; raise SystemExit(pytest.main(sys.argv[1:]))"
    )
    env = dict(os.environ, PYTHONPATH=str(source), PYTHONHASHSEED="0",
               USE_RAMDISK="1", NANASQLITE_SUPPRESS_MP_WARNING="1")
    subprocess.run(
        [sys.executable, "-c", code, str(ROOT / "tests" / f"test_{suite}.py"),
         "-o", "addopts=", "--benchmark-only", f"--benchmark-json={output}", "-q"],
        env=env, cwd=ROOT, check=True, timeout=900,
    )
    result = json.loads(output.read_text(encoding="utf-8"))
    if not result["benchmarks"]:
        raise RuntimeError(f"No measurements: {output}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-source", type=Path, required=True)
    parser.add_argument("--candidate-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    metadata = {"python": sys.version, "platform": platform.platform(), "machine": platform.machine(),
                "storage": "RAM disk /dev/shm", "network": "Docker --network none",
                "pythonhashseed": "0", "legacy_pytest_repetitions": 1, "paired_repetitions": 7}
    (args.output / "environment.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    freeze = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    (args.output / "dependencies.txt").write_text(freeze, encoding="utf-8")
    sources = {"baseline": args.baseline_source.resolve(), "candidate": args.candidate_source.resolve()}
    versions = {"baseline": "1.6.1", "candidate": "1.6.2"}
    lines = ["# RPI release comparison", "", "Baseline: v1.6.1; candidate: v1.6.2.", "",
             "One container, shared dependencies, RAM disk, network disabled.", "",
             "## Original pytest benchmarks", "",
             "One suite run per version; diagnostic medians, not evidence of a reproducible regression.", "",
             "| Workload | v1.6.1 median us | v1.6.2 median us | Ratio |", "| --- | ---: | ---: | ---: |"]
    for suite, order in (("benchmark", ("baseline", "candidate")),
                         ("async_benchmark", ("candidate", "baseline"))):
        results = {}
        for label in order:
            data = run_suite(sources[label], versions[label], suite, args.output / f"{label}-{suite}.json")
            results[label] = {b["fullname"]: b for b in data["benchmarks"]}
        assert results["baseline"].keys() == results["candidate"].keys(), "Workload sets differ"
        for name in sorted(results["baseline"]):
            before = results["baseline"][name]["stats"]["median"]
            after = results["candidate"][name]["stats"]["median"]
            lines.append(f"| {name} | {before * 1e6:.3f} | {after * 1e6:.3f} | {after / before:.3f} |")
    (args.output / "original-suite-comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    run_paired(SimpleNamespace(
        baseline_source=sources["baseline"], source=sources["candidate"],
        baseline_ref=None, repeats=7, db_dir=Path("/dev/shm"), cases=list(CASES),
        rows=3000, operations=100000, writes=300, seed=20260905,
        output=args.output / "paired.json", markdown=args.output / "paired.md",
    ))


if __name__ == "__main__":
    main()
