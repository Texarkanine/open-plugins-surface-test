"""Behavioral contracts for scripts/setup.sh (reset boundary + run header)."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "scripts" / "setup.sh"

PROBE_LEAK_PATTERNS = (
    re.compile(r"7[-\s]?space", re.IGNORECASE),
    re.compile(r"scottish", re.IGNORECASE),
    re.compile(r"indent(?:ation)?\s*(?:must|should|with)", re.IGNORECASE),
)


def _run_setup(work: Path, stdin: str = "cursor\ngpt-test\n") -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CONFORMANCE_WORK"] = str(work)
    return subprocess.run(
        ["bash", str(SETUP)],
        input=stdin,
        text=True,
        capture_output=True,
        env=env,
        cwd=str(ROOT),
        check=False,
    )


def _assert_setup_ok(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0, (
        f"setup.sh failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def _indent_widths(source: str) -> set[int]:
    widths: set[int] = set()
    for line in source.splitlines():
        if not line.strip():
            continue
        if line.startswith("\t"):
            widths.add(-1)
            continue
        leading = len(line) - len(line.lstrip(" "))
        if leading:
            widths.add(leading)
    return widths


def _is_recursive_fib(source: str) -> bool:
    lowered = source.lower()
    return "fib" in lowered and "fib(" in lowered.replace(" ", "")


@pytest.fixture
def work(tmp_path: Path) -> Path:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    return work_dir


def test_setup_wipes_artifacts(work: Path) -> None:
    planted = work / "artifacts" / "stale.txt"
    planted.parent.mkdir(parents=True)
    planted.write_text("keep-me-not\n", encoding="utf-8")

    result = _run_setup(work)
    _assert_setup_ok(result)

    assert not planted.exists()
    artifacts = work / "artifacts"
    assert not artifacts.exists() or not any(artifacts.iterdir())


def test_setup_preserves_observations(work: Path) -> None:
    evidence = work / "observations" / "session-start.jsonl"
    evidence.parent.mkdir(parents=True)
    payload = '{"event":"SessionStart","marker":"do-not-touch"}\n'
    evidence.write_text(payload, encoding="utf-8")

    result = _run_setup(work)
    _assert_setup_ok(result)

    assert evidence.read_text(encoding="utf-8") == payload


def test_setup_regenerates_fixtures_and_removes_junk(work: Path) -> None:
    junk = work / "fixtures" / "junk.txt"
    junk.parent.mkdir(parents=True)
    junk.write_text("stale\n", encoding="utf-8")

    result = _run_setup(work)
    _assert_setup_ok(result)

    assert not junk.exists()
    assert (work / "fixtures" / "fib.js").is_file()
    assert (work / "fixtures" / "fib.py").is_file()
    assert (work / "fixtures" / "probe.lspprobe").is_file()


@pytest.mark.parametrize("name", ["fib.js", "fib.py"])
def test_fixture_is_four_space_recursive(work: Path, name: str) -> None:
    result = _run_setup(work)
    _assert_setup_ok(result)

    source = (work / "fixtures" / name).read_text(encoding="utf-8")
    widths = _indent_widths(source)
    assert widths, f"{name} has no indented lines"
    assert -1 not in widths, f"{name} uses tabs"
    assert all(width % 4 == 0 for width in widths), f"{name} indent widths: {widths}"
    assert _is_recursive_fib(source), f"{name} is not a recursive fib"


@pytest.mark.parametrize("name", ["fib.js", "fib.py"])
def test_fixtures_have_no_probe_leakage(work: Path, name: str) -> None:
    result = _run_setup(work)
    _assert_setup_ok(result)

    source = (work / "fixtures" / name).read_text(encoding="utf-8")
    for pattern in PROBE_LEAK_PATTERNS:
        assert pattern.search(source) is None, f"{name} leaked probe expectation: {pattern.pattern}"


def test_setup_creates_run_json_when_absent(work: Path) -> None:
    result = _run_setup(work, stdin="my-harness\nmy-model\n")
    _assert_setup_ok(result)

    data = json.loads((work / "run.json").read_text(encoding="utf-8"))
    assert data["harness"] == "my-harness"
    assert data["model"] == "my-model"
    assert isinstance(data["os"], str) and data["os"]
    assert "uv_version" in data
    assert isinstance(data["uv_version"], str)


def test_setup_defaults_declined_prompts(work: Path) -> None:
    result = _run_setup(work, stdin="\n\n")
    _assert_setup_ok(result)

    data = json.loads((work / "run.json").read_text(encoding="utf-8"))
    assert data["harness"] == "unknown"
    assert data["model"] == "unspecified"


def test_setup_preserves_existing_run_json(work: Path) -> None:
    original = {
        "harness": "already-set",
        "model": "already-model",
        "os": "test-os",
        "uv_version": "test-uv",
    }
    (work / "run.json").write_text(json.dumps(original) + "\n", encoding="utf-8")

    result = _run_setup(work, stdin="other\nother-model\n")
    _assert_setup_ok(result)

    data = json.loads((work / "run.json").read_text(encoding="utf-8"))
    assert data == original


def test_setup_second_run_is_idempotent_on_observations_and_run_json(work: Path) -> None:
    evidence = work / "observations" / "keep.jsonl"
    evidence.parent.mkdir(parents=True)
    payload = '{"ok":true}\n'
    evidence.write_text(payload, encoding="utf-8")

    first = _run_setup(work, stdin="h1\nm1\n")
    _assert_setup_ok(first)
    run_after_first = (work / "run.json").read_text(encoding="utf-8")

    second = _run_setup(work, stdin="h2\nm2\n")
    _assert_setup_ok(second)

    assert evidence.read_text(encoding="utf-8") == payload
    assert (work / "run.json").read_text(encoding="utf-8") == run_after_first
    assert (work / "fixtures" / "fib.js").is_file()
    assert (work / "fixtures" / "fib.py").is_file()
    assert (work / "fixtures" / "probe.lspprobe").is_file()


def test_setup_missing_work_does_not_create_observations(tmp_path: Path) -> None:
    work = tmp_path / "missing-work"
    assert not work.exists()

    result = _run_setup(work, stdin="h\nm\n")
    _assert_setup_ok(result)

    assert work.is_dir()
    assert (work / "run.json").is_file()
    assert (work / "fixtures" / "fib.js").is_file()
    assert (work / "fixtures" / "probe.lspprobe").is_file()
    assert not (work / "observations").exists()
