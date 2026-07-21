"""Behavioral contracts for scripts/check.py (observe-not-judge harness)."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check.py"
SETUP = ROOT / "scripts" / "setup.sh"
REPO_WORK = ROOT / "work"

REQUIRED_RECORD_KEYS = {
    "run_id",
    "step",
    "surface",
    "mode",
    "probe",
    "path",
    "observed",
    "detail",
    "ts",
}

JUDGMENT_BAN = ("pass", "fail", "unsupported")


def _load_check_module():
    spec = importlib.util.spec_from_file_location("check_harness", CHECK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_run_json(work: Path, **fields: Any) -> None:
    data = {
        "harness": "test-harness",
        "model": "test-model",
        "os": "test-os",
        "uv_version": "test-uv",
    }
    data.update(fields)
    work.mkdir(parents=True, exist_ok=True)
    (work / "run.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _run_check(
    work: Path | None,
    args: list[str],
    *,
    env_extra: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if work is not None:
        env["CONFORMANCE_WORK"] = str(work)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(CHECK), *args],
        text=True,
        capture_output=True,
        env=env,
        cwd=str(ROOT),
        check=False,
    )


def _jsonl_lines(work: Path) -> list[str]:
    path = work / "observations" / "run.jsonl"
    if not path.is_file():
        return []
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _assert_no_judgment_language(text: str) -> None:
    lowered = text.lower()
    for banned in JUDGMENT_BAN:
        assert banned not in lowered, f"judgment language {banned!r} found in:\n{text}"


@pytest.fixture
def work(tmp_path: Path) -> Path:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    _write_run_json(work_dir)
    return work_dir


def test_usage_no_args(work: Path) -> None:
    result = _run_check(work, [])
    assert result.returncode != 0
    assert _jsonl_lines(work) == []


def test_usage_non_integer_step(work: Path) -> None:
    result = _run_check(work, ["abc"])
    assert result.returncode != 0
    assert _jsonl_lines(work) == []


def test_usage_unknown_flag(work: Path) -> None:
    result = _run_check(work, ["--wat"])
    assert result.returncode != 0
    assert _jsonl_lines(work) == []


def test_unknown_step_out_of_range(work: Path) -> None:
    result = _run_check(work, ["0"])
    assert result.returncode != 0
    assert _jsonl_lines(work) == []

    result = _run_check(work, ["12"])
    assert result.returncode != 0
    assert _jsonl_lines(work) == []


def test_missing_work_dir(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"
    assert not missing.exists()
    result = _run_check(missing, ["1"])
    assert result.returncode != 0


def test_missing_run_json(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    result = _run_check(work, ["1"])
    assert result.returncode != 0
    assert _jsonl_lines(work) == []


def test_step_append_shape(work: Path) -> None:
    result = _run_check(work, ["1"])
    assert result.returncode == 0

    lines = _jsonl_lines(work)
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert REQUIRED_RECORD_KEYS <= set(record)
    assert record["step"] == 1
    assert record["surface"] == "rules"
    assert record["mode"] == "alwaysApply"
    assert record["probe"] == "r1-global-scots"
    assert record["path"] == "create"
    assert record["observed"] is False
    assert record["detail"] == "probe checker not implemented"
    assert isinstance(record["run_id"], str) and record["run_id"]
    assert isinstance(record["ts"], str) and record["ts"]


def test_observe_not_judge_exit_zero(work: Path) -> None:
    result = _run_check(work, ["1"])
    assert result.returncode == 0
    combined = f"{result.stdout}\n{result.stderr}"
    assert "not observed" in combined.lower()
    _assert_no_judgment_language(combined)


def test_skipped_status_wording(
    work: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    check = _load_check_module()

    def skip_observer(step: int, work_dir: Path) -> dict[str, Any]:
        return {"observed": None, "detail": "skipped for test"}

    monkeypatch.setitem(check.STEP_REGISTRY[9], "observe", skip_observer)
    monkeypatch.setenv("CONFORMANCE_WORK", str(work))

    code = check.observe_step(9, work)
    assert code == 0
    captured = capsys.readouterr()
    combined = f"{captured.out}\n{captured.err}"
    assert "skipped" in combined.lower()
    _assert_no_judgment_language(combined)

    lines = _jsonl_lines(work)
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["observed"] is None
    assert record["step"] == 9


def test_append_only_preserves_first_line(work: Path) -> None:
    first = _run_check(work, ["1"])
    assert first.returncode == 0
    lines_after_first = _jsonl_lines(work)
    assert len(lines_after_first) == 1
    first_line = lines_after_first[0]

    second = _run_check(work, ["2"])
    assert second.returncode == 0
    lines = _jsonl_lines(work)
    assert len(lines) == 2
    assert lines[0] == first_line
    assert json.loads(lines[1])["step"] == 2


def test_run_id_stable_across_checks(work: Path) -> None:
    first = _run_check(work, ["1"])
    assert first.returncode == 0
    run_data = json.loads((work / "run.json").read_text(encoding="utf-8"))
    assert "run_id" in run_data
    run_id = run_data["run_id"]
    assert run_data["harness"] == "test-harness"
    assert run_data["model"] == "test-model"

    second = _run_check(work, ["2"])
    assert second.returncode == 0
    run_data_2 = json.loads((work / "run.json").read_text(encoding="utf-8"))
    assert run_data_2["run_id"] == run_id

    records = [json.loads(line) for line in _jsonl_lines(work)]
    assert [r["run_id"] for r in records] == [run_id, run_id]


def test_summary_empty_jsonl(work: Path) -> None:
    result = _run_check(work, ["--summary"])
    assert result.returncode == 0
    combined = f"{result.stdout}\n{result.stderr}"
    _assert_no_judgment_language(combined)


def test_summary_status_vocabulary(work: Path) -> None:
    observations = work / "observations"
    observations.mkdir(parents=True)
    planted = [
        {
            "run_id": "rid",
            "step": 1,
            "surface": "rules",
            "mode": "alwaysApply",
            "probe": "r1-global-scots",
            "path": "create",
            "observed": True,
            "detail": "ok",
            "ts": "t1",
        },
        {
            "run_id": "rid",
            "step": 2,
            "surface": "rules",
            "mode": "alwaysApply+globs",
            "probe": "r2-js-indent",
            "path": "create",
            "observed": False,
            "detail": "nope",
            "ts": "t2",
        },
        {
            "run_id": "rid",
            "step": 9,
            "surface": "hooks",
            "mode": "events",
            "probe": "h1-hooks-battery",
            "path": "aggregate",
            "observed": None,
            "detail": "skipped",
            "ts": "t3",
        },
    ]
    (observations / "run.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in planted),
        encoding="utf-8",
    )

    result = _run_check(work, ["--summary"])
    assert result.returncode == 0
    out = result.stdout
    assert "✅ observed" in out
    assert "❌ not observed" in out
    assert "⊘ skipped" in out
    _assert_no_judgment_language(out)


def test_summary_includes_run_header(work: Path) -> None:
    result = _run_check(work, ["--summary"])
    assert result.returncode == 0
    out = result.stdout
    assert "test-harness" in out
    assert "test-model" in out
    assert "test-os" in out
    assert "test-uv" in out


def test_conformance_work_isolates_mutations(work: Path) -> None:
    before_repo = None
    if REPO_WORK.exists():
        before_repo = {
            p.relative_to(REPO_WORK): p.read_bytes() if p.is_file() else None
            for p in REPO_WORK.rglob("*")
        }

    result = _run_check(work, ["1"])
    assert result.returncode == 0
    assert (work / "observations" / "run.jsonl").is_file()

    if before_repo is None:
        assert not (REPO_WORK / "observations" / "run.jsonl").exists()
    else:
        after_repo = {
            p.relative_to(REPO_WORK): p.read_bytes() if p.is_file() else None
            for p in REPO_WORK.rglob("*")
        }
        assert after_repo == before_repo


def test_cli_round_trip_step_then_summary(work: Path) -> None:
    step = _run_check(work, ["2"])
    assert step.returncode == 0

    summary = _run_check(work, ["--summary"])
    assert summary.returncode == 0
    out = summary.stdout
    assert "r2-js-indent" in out
    assert "❌ not observed" in out
    assert "create" in out


def test_coexistence_with_setup(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()

    env = os.environ.copy()
    env["CONFORMANCE_WORK"] = str(work)
    setup = subprocess.run(
        ["bash", str(SETUP)],
        input="cursor\ngpt-test\n",
        text=True,
        capture_output=True,
        env=env,
        cwd=str(ROOT),
        check=False,
    )
    assert setup.returncode == 0, setup.stderr

    fib_js = (work / "fixtures" / "fib.js").read_text(encoding="utf-8")
    fib_py = (work / "fixtures" / "fib.py").read_text(encoding="utf-8")

    check = _run_check(work, ["1"])
    assert check.returncode == 0
    assert len(_jsonl_lines(work)) == 1

    assert (work / "fixtures" / "fib.js").read_text(encoding="utf-8") == fib_js
    assert (work / "fixtures" / "fib.py").read_text(encoding="utf-8") == fib_py
    assert (work / "artifacts").is_dir()
