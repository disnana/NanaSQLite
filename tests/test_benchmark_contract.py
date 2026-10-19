"""Ensure benchmark success actually requires correct public-API outcomes."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

from nanasqlite import NanaSQLite

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("operational_benchmark", ROOT / "scripts/benchmark_operational.py")
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


def arguments(tmp_path, case, phase="time"):
    return SimpleNamespace(source=ROOT / "src", worker=case, phase=phase,
                           rows=9, operations=20, writes=3, db_dir=tmp_path)


def test_measurement_rejects_silently_lost_writes(tmp_path, monkeypatch):
    monkeypatch.setattr(NanaSQLite, "__setitem__", lambda *args: None)
    with pytest.raises(AssertionError):
        benchmark.worker(arguments(tmp_path, "disk_update"))


def test_measurement_rejects_wrong_export_with_same_count(tmp_path, monkeypatch):
    original = NanaSQLite.iter_items

    def corrupted(db, batch_size):
        for key, value in original(db, batch_size):
            yield key, {**value, "i": -1}

    monkeypatch.setattr(NanaSQLite, "iter_items", corrupted)
    with pytest.raises(AssertionError):
        benchmark.worker(arguments(tmp_path, "export_stream"))


def test_timing_does_not_enable_allocation_tracing(tmp_path, monkeypatch):
    def forbidden():
        raise AssertionError("allocation tracing would contaminate time samples")

    monkeypatch.setattr(benchmark.tracemalloc, "start", forbidden)
    result = benchmark.worker(arguments(tmp_path, "export_items"))
    assert result["seconds"] > 0
    assert result["verified_rows"] == 9
    assert "python_peak_bytes" not in result


def test_memory_result_does_not_report_contaminated_timing(tmp_path):
    result = benchmark.worker(arguments(tmp_path, "export_stream", "memory"))
    assert result["python_peak_bytes"] > 0
    assert "seconds" not in result
    assert "ns_per_operation" not in result


def test_requested_source_cannot_silently_fall_back_to_installed_package(tmp_path):
    args = arguments(tmp_path, "cached_get")
    args.source = tmp_path / "missing-source"
    with pytest.raises(AssertionError, match="requested source"):
        benchmark.worker(args)


def test_snapshot_comparison_does_not_require_git(tmp_path, monkeypatch):
    def forbidden_git(*args, **kwargs):
        raise AssertionError("Snapshot comparison must work without git installed")

    output = tmp_path / "comparison.json"
    monkeypatch.setattr(benchmark.subprocess, "check_output", forbidden_git)
    monkeypatch.setattr(benchmark.sys, "argv", [
        "benchmark_operational.py", "--baseline-source", str(ROOT / "src"),
        "--source", str(ROOT / "src"), "--repeats", "1", "--cases", "cached_get",
        "--rows", "9", "--operations", "20", "--writes", "3", "--output", str(output),
    ])
    benchmark.main(benchmark.parse_args())
    import json

    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["baseline_revision"] is None
    assert report["source_sha256"]["baseline"] == report["source_sha256"]["candidate"]
    assert {sample["label"] for sample in report["samples"]} == {"baseline", "candidate"}
