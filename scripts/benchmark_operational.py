"""Interleaved isolated file-backed benchmarks, verified against an independent model.

python scripts/benchmark_operational.py --repeats 7 --output result.json
Timing and Python allocation tracing run in separate processes. Application
cache cold does not mean OS cache cold. No executor monkeypatching or sleeps.
"""
from __future__ import annotations

import argparse
import asyncio
import gc
import hashlib
import json
import os
import platform
import random
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    "cached_get", "cached_item", "missing_get", "cached_batch", "mixed_batch",
    "cold_get", "disk_insert", "disk_update", "async_cached", "async_disk_unbounded",
    "async_disk_bounded", "export_items", "export_stream", "export_encrypted",
    "auto_get", "v2_accept", "v2_durable",
    "batch_cold_0", "batch_cold_50", "batch_cold_90",
    "async_batch", "async_mixed_batch",
)
MEMORY_CASES = {"export_items", "export_stream", "async_disk_unbounded", "async_disk_bounded"}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "src")
    parser.add_argument("--baseline-ref", default="HEAD")
    parser.add_argument("--baseline-source", type=Path, help="Compare an immutable local source snapshot")
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--rows", type=int, default=3000)
    parser.add_argument("--operations", type=int, default=100000)
    parser.add_argument("--writes", type=int, default=300)
    parser.add_argument("--seed", type=int, default=20260905)
    parser.add_argument("--db-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--cases", nargs="+", choices=CASES, default=list(CASES))
    parser.add_argument("--worker", choices=CASES, help=argparse.SUPPRESS)
    parser.add_argument("--phase", choices=("time", "memory"), default="time", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if min(args.repeats, args.rows, args.operations, args.writes) <= 0:
        parser.error("counts must be positive")
    return args


def start_measurement(phase):
    gc.collect()
    assert not tracemalloc.is_tracing()
    if phase == "memory":
        tracemalloc.start()
    return time.perf_counter_ns()


def end_measurement(phase, start, operations):
    if phase == "memory":
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return {"python_peak_bytes": peak, "operations": operations}
    elapsed = time.perf_counter_ns() - start
    return {"seconds": elapsed / 1e9, "ns_per_operation": elapsed / operations, "operations": operations}


def worker(args):
    sys.path.insert(0, str(args.source.resolve()))
    import apsw

    import nanasqlite
    from nanasqlite import AsyncNanaSQLite, NanaSQLite, compat

    assert Path(nanasqlite.__file__).resolve().parent == (args.source / "nanasqlite").resolve(), (
        "imported package does not match requested source; refusing a false comparison"
    )
    case = args.worker
    if case in {"export_stream", "export_encrypted", "auto_get", "async_disk_bounded"} and not hasattr(NanaSQLite, "iter_items"):
        return {"unsupported": True}
    if case.startswith("v2_") and not hasattr(NanaSQLite, "flush"):
        return {"unsupported": True}
    config = {}
    encryption_key = None
    if case == "export_encrypted":
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        encryption_key = AESGCM.generate_key(128)
        config["encryption_key"] = encryption_key
    model = {f"k{i:06d}": {"i": i, "text": "日本語-" + "x" * 128} for i in range(args.rows)}
    keys = list(model)
    with tempfile.TemporaryDirectory(prefix="nanasqlite-bench-", dir=args.db_dir) as directory:
        path = str(Path(directory) / "data.db")
        with NanaSQLite(path, **config) as seed:
            seed.batch_update(model)
            pragmas = {name: seed._connection.execute(f"PRAGMA {name}").fetchone()[0]
                       for name in ("journal_mode", "synchronous", "page_size")}
        if case.startswith("async_"):
            result = asyncio.run(async_worker(AsyncNanaSQLite, path, case, args, model))
        else:
            if case == "auto_get":
                config["cache_consistency"] = "auto"
            if case.startswith("v2_"):
                config.update(v2_mode=True, flush_mode="manual")
            with NanaSQLite(path, **config) as db:
                db.load_all()  # warm SQLite/OS pages, outside measurement
                if case in {"cold_get", "export_items", "export_stream", "export_encrypted"}:
                    db.clear_cache()
                result = sync_worker(db, case, args, model, keys)
        # Reopen independently; counts alone do not prove correctness.
        with closing(sqlite3.connect(path)) as verification:
            assert verification.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            rows = dict(verification.execute("SELECT key, value FROM data"))
            if encryption_key is None:
                assert {key: json.loads(value) for key, value in rows.items()} == model
            else:
                with NanaSQLite(path, encryption_key=encryption_key) as fresh:
                    assert dict(fresh.iter_items(257)) == model
        result["verified_rows"] = len(model)
        result["environment"] = {
            "python": sys.version, "platform": platform.platform(), "apsw": apsw.apswversion(),
            "sqlite": apsw.sqlitelibversion(), "orjson": compat.HAS_ORJSON,
            "gc_enabled": gc.isenabled(), "pragmas": pragmas,
            "database_directory": str(Path(directory).parent.resolve()),
        }
        return result


def sync_worker(db, case, args, model, keys):
    count = args.operations
    if case.startswith("batch_cold_"):
        batch = keys[:100]
        warm_count = len(batch) * int(case.rsplit("_", 1)[1]) // 100
        expected = {key: model[key] for key in batch}
        repetitions = max(10, count // 10000)
        elapsed = 0.0
        for _ in range(repetitions):
            db.clear_cache()
            db.batch_get(batch[:warm_count])
            start = start_measurement(args.phase)
            actual = db.batch_get(batch)
            elapsed += end_measurement(args.phase, start, 1)["seconds"]
            assert actual == expected
        return {"seconds": elapsed, "ns_per_operation": elapsed * 1e9 / repetitions,
                "operations": repetitions}
    if case.startswith("export_"):
        expected = sorted(model.items())
        start = start_measurement(args.phase)
        pairs = db.items() if case == "export_items" else db.iter_items(256)
        seen = 0
        for seen, pair in enumerate(pairs, 1):
            assert pair == expected[seen - 1]  # identical full-value consumer
        assert seen == len(expected)
        return end_measurement(args.phase, start, len(expected))
    if case in {"disk_insert", "disk_update", "v2_accept", "v2_durable"}:
        changes = [(f"new{i:06d}" if case == "disk_insert" else keys[i % len(keys)],
                    {"i": i + 100000, "text": "updated"}) for i in range(args.writes)]
        start = start_measurement(args.phase)
        for key, value in changes:
            db[key] = value
        if case == "v2_durable":
            db.flush(wait=True)
        result = end_measurement(args.phase, start, len(changes))
        if case == "v2_accept":
            db.flush(wait=True)  # acceptance is NOT a durability measurement
        model.update(changes)
        return result
    if case in {"cached_batch", "mixed_batch"}:
        batch = keys[:100]
        if case == "mixed_batch":
            batch = batch + ["absent"]
            db.get("absent")
        repetitions = max(1, count // len(batch))
        expected = repetitions * sum(model[k]["i"] for k in batch if k in model)
        total = 0
        start = start_measurement(args.phase)
        for _ in range(repetitions):
            total += sum(v["i"] for v in db.batch_get(batch).values())
        result = end_measurement(args.phase, start, repetitions)
        assert total == expected
        return result
    if case == "cold_get":
        requests = keys  # each key read once, no warm-hit contamination
    elif case == "missing_get":
        requests = ["absent"] * count
        db.get("absent")
    else:
        requests = [keys[i % len(keys)] for i in range(count)]
    expected = sum(model[key]["i"] for key in requests if key in model)
    total = 0
    start = start_measurement(args.phase)
    if case == "cached_item":
        for key in requests:
            total += db[key]["i"]
    elif case == "missing_get":
        for key in requests:
            assert db.get(key) is None
    else:
        for key in requests:
            total += db.get(key)["i"]
    result = end_measurement(args.phase, start, len(requests))
    assert total == expected
    return result


async def async_worker(cls, path, case, args, model):
    options = {"max_pending_operations": 16} if case == "async_disk_bounded" else {}
    async with cls(path, **options) as db:
        if case in {"async_batch", "async_mixed_batch"}:
            await db.aload_all()
            batch = list(model)[:100]
            if case == "async_mixed_batch":
                batch.append("absent")
                await db.aget("absent")
            repetitions = max(1, args.operations // len(batch))
            expected = repetitions * sum(model[k]["i"] for k in batch if k in model)
            total = 0
            start = start_measurement(args.phase)
            for _ in range(repetitions):
                total += sum(v["i"] for v in (await db.abatch_get(batch)).values())
            result = end_measurement(args.phase, start, repetitions)
            assert total == expected
            return result
        if case == "async_cached":
            await db.aload_all()
            keys = list(model)
            requests = [keys[i % len(keys)] for i in range(args.operations)]
            total = 0
            start = start_measurement(args.phase)
            for key in requests:
                total += (await db.aget(key))["i"]
            result = end_measurement(args.phase, start, len(requests))
            assert total == sum(model[key]["i"] for key in requests)
            return result
        changes = {f"new{i:06d}": {"i": i + 100000, "text": "async"} for i in range(args.writes)}

        async def write(key, value):
            before = time.perf_counter_ns()
            await db.aset(key, value)
            return time.perf_counter_ns() - before

        start = start_measurement(args.phase)
        latencies = await asyncio.gather(*(write(k, v) for k, v in changes.items()))
        result = end_measurement(args.phase, start, len(changes))
        if args.phase == "time":
            rank = max(0, (len(latencies) * 95 + 99) // 100 - 1)
            result["invocation_p95_ms"] = sorted(latencies)[rank] / 1e6
        model.update(changes)
        return result


def fingerprint(source):
    digest = hashlib.sha256()
    for path in sorted((source / "nanasqlite").glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def summarize(samples):
    summary = {}
    for label in ("baseline", "candidate"):
        summary[label] = {}
        for case in sorted({s["case"] for s in samples}):
            selected = [s for s in samples if s["label"] == label and s["case"] == case and not s.get("unsupported")]
            metrics = {}
            for field in ("ns_per_operation", "seconds", "invocation_p95_ms", "python_peak_bytes"):
                values = [s[field] for s in selected if field in s]
                if values:
                    median = statistics.median(values)
                    metrics[field] = {"n": len(values), "median": median, "min": min(values), "max": max(values),
                                      "mad": statistics.median(abs(v - median) for v in values)}
            summary[label][case] = metrics
    return summary


def paired_ratios(samples):
    result = {}
    for case in sorted({s["case"] for s in samples}):
        pairs = {}
        for sample in samples:
            if sample["case"] == case and "ns_per_operation" in sample:
                pairs.setdefault(sample["repeat"], {})[sample["label"]] = sample["ns_per_operation"]
        ratios = [p["candidate"] / p["baseline"] for p in pairs.values() if len(p) == 2]
        if ratios:
            result[case] = {"n": len(ratios), "median": statistics.median(ratios),
                            "min": min(ratios), "max": max(ratios), "samples": ratios}
    return result


def render_markdown(report):
    lines = ["# Same-run performance comparison", "",
             f"Baseline: {report['baseline_revision'] or 'local source snapshot'}",
             f"Baseline source SHA256: {report['source_sha256']['baseline']}", "",
             "Both revisions run on the same runner and dependencies, in alternating order.",
             "Each sample uses a fresh process and database. Both versions use identical timing boundaries.",
             "Ratios below 1 are faster. Ranges show observed variation, not confidence intervals.", "",
             "| Workload | Baseline median ns/op | Candidate median ns/op | Paired ratio (range) |",
             "| --- | ---: | ---: | ---: |"]
    for case, candidate in report["summary"]["candidate"].items():
        after = candidate.get("ns_per_operation")
        if not after:
            continue
        before = report["summary"]["baseline"][case].get("ns_per_operation")
        ratio = report["paired_ratios"].get(case)
        base = f"{before['median']:.1f}" if before else "unsupported"
        comparison = f"{ratio['median']:.3f} ({ratio['min']:.3f}–{ratio['max']:.3f})" if ratio else "—"
        lines.append(f"| {case} | {base} | {after['median']:.1f} | {comparison} |")
    lines += ["", "## Python allocation peaks (separate samples)", "",
              "These exclude existing model/fixture memory and SQLite/native memory; they are not process RSS.", "",
              "| Workload | Baseline median bytes | Candidate median bytes |", "| --- | ---: | ---: |"]
    for case, candidate in report["summary"]["candidate"].items():
        after = candidate.get("python_peak_bytes")
        if after:
            before = report["summary"]["baseline"][case].get("python_peak_bytes")
            base = str(int(before["median"])) if before else "unsupported"
            lines.append(f"| {case} | {base} | {int(after['median'])} |")
    lines += ["", "Cold reads clear only the application cache. OS pages may be warm.",
              "batch_cold cases reset/warm outside each timed batch; value verification is outside timing.",
              "v2_accept excludes flushing; v2_durable includes it. They are different contracts.",
              "Full persisted values and database integrity are verified after each sample.",
              "Raw samples, environment and source fingerprints are in the JSON artifact.", ""]
    return "\n".join(lines)


def main(args):
    args.source = args.source.resolve()
    if args.db_dir:
        args.db_dir = args.db_dir.resolve()
        args.db_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    revision = subprocess.check_output(
        ["git", "rev-parse", "--verify", "--end-of-options", args.baseline_ref + "^{commit}"], cwd=ROOT, text=True,
    ).strip()
    samples = []
    with tempfile.TemporaryDirectory(prefix="nanasqlite-reference-") as temporary:
        baseline = Path(temporary) / "src"
        paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", revision, "src/nanasqlite"], cwd=ROOT, text=True).splitlines()
        for name in paths:
            target = Path(temporary) / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(subprocess.check_output(["git", "show", f"{revision}:{name}"], cwd=ROOT))
        sources = {"baseline": args.baseline_source.resolve() if args.baseline_source else baseline, "candidate": args.source}
        fingerprints = {label: fingerprint(source) for label, source in sources.items()}
        for phase in ("time", "memory"):
            cases = [c for c in args.cases if phase == "time" or c in MEMORY_CASES]
            if not cases:
                continue
            for repeat in range(args.repeats):
                order = list(cases)
                rng.shuffle(order)
                for case in order:
                    labels = ("baseline", "candidate") if repeat % 2 == 0 else ("candidate", "baseline")
                    for label in labels:
                        cmd = [sys.executable, str(Path(__file__).resolve()), "--worker", case, "--phase", phase,
                               "--source", str(sources[label]), "--rows", str(args.rows),
                               "--operations", str(args.operations), "--writes", str(args.writes)]
                        if args.db_dir:
                            cmd += ["--db-dir", str(args.db_dir)]
                        env = dict(os.environ, PYTHONHASHSEED="0", NANASQLITE_SUPPRESS_MP_WARNING="1")
                        run = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=90)
                        if run.returncode:
                            raise RuntimeError(f"{label}/{case}/{phase} failed:\n{run.stderr}\n{run.stdout}")
                        sample = json.loads(run.stdout)
                        sample.update(label=label, case=case, phase=phase, repeat=repeat)
                        samples.append(sample)
                print(f"{phase}: repeat {repeat + 1}/{args.repeats} complete", flush=True)
        assert all(fingerprints[label] == fingerprint(source) for label, source in sources.items()), "source changed during measurement"
    report = {
        "schema_version": 2, "baseline_revision": revision if not args.baseline_source else None,
        "baseline_source": str(args.baseline_source.resolve()) if args.baseline_source else None, "source_sha256": fingerprints,
        "parameters": {"repeats": args.repeats, "rows": args.rows, "operations": args.operations,
                       "writes": args.writes, "seed": args.seed},
        "method": "fresh process and DB per sample; AB/BA; separate timing/memory; GC enabled; warm OS cache",
        "summary": summarize(samples), "paired_ratios": paired_ratios(samples), "samples": samples,
    }
    output = args.output or ROOT / "scratch" / "operational-benchmark.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(render_markdown(report), encoding="utf-8")
    print(f"Report: {output.resolve()}")


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.worker:
        print(json.dumps(worker(arguments)))
    else:
        main(arguments)
