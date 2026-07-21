"""Contracts for R1 Scots-flag checker, rule, and prompt."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check.py"
RULE = ROOT / "rules" / "r1-global-scots.mdc"
PROMPT = ROOT / "prompts" / "01-r1-cats.md"

# Scotland flag tag sequence (DESIGN Challenges): U+1F3F4 + gbsct tags + cancel.
SCOTS_FLAG = "\U0001f3f4\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f"
BLACK_FLAG_ONLY = "\U0001f3f4"
INCOMPLETE_PREFIX = "\U0001f3f4\U000e0067\U000e0062\U000e0073"


def _load_check_module():
    spec = importlib.util.spec_from_file_location("check_harness", CHECK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_run_json(work: Path) -> None:
    work.mkdir(parents=True, exist_ok=True)
    (work / "run.json").write_text(
        json.dumps(
            {
                "harness": "test-harness",
                "model": "test-model",
                "os": "test-os",
                "uv_version": "test-uv",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _run_check(work: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CONFORMANCE_WORK"] = str(work)
    return subprocess.run(
        [sys.executable, str(CHECK), *args],
        text=True,
        capture_output=True,
        env=env,
        cwd=str(ROOT),
        check=False,
    )


@pytest.fixture
def work(tmp_path: Path) -> Path:
    work_dir = tmp_path / "work"
    _write_run_json(work_dir)
    return work_dir


def test_contains_scots_flag_full_sequence() -> None:
    check = _load_check_module()
    assert check.contains_scots_flag(f"hello {SCOTS_FLAG} cats") is True


def test_contains_scots_flag_rejects_empty_and_ascii() -> None:
    check = _load_check_module()
    assert check.contains_scots_flag("") is False
    assert check.contains_scots_flag("domestic felines are delightful") is False


def test_contains_scots_flag_rejects_partial_sequences() -> None:
    check = _load_check_module()
    assert check.contains_scots_flag(BLACK_FLAG_ONLY) is False
    assert check.contains_scots_flag(INCOMPLETE_PREFIX) is False
    assert check.contains_scots_flag(BLACK_FLAG_ONLY + "gbsct") is False


def test_observe_r1_missing_artifact(work: Path) -> None:
    check = _load_check_module()
    result = check.observe_r1_scots(1, work)
    assert result["observed"] is False
    assert "cats.md" in result["detail"].lower()


def test_observe_r1_flag_absent(work: Path) -> None:
    check = _load_check_module()
    artifact = work / "artifacts" / "cats.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("Cats are wonderful companions.\n", encoding="utf-8")
    result = check.observe_r1_scots(1, work)
    assert result["observed"] is False
    assert "not present" in result["detail"].lower() or "absent" in result["detail"].lower()


def test_observe_r1_flag_present(work: Path) -> None:
    check = _load_check_module()
    artifact = work / "artifacts" / "cats.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(f"Cats are lovely. {SCOTS_FLAG}\n", encoding="utf-8")
    result = check.observe_r1_scots(1, work)
    assert result["observed"] is True
    assert "present" in result["detail"].lower()


def test_check_cli_step1_observed_with_flag(work: Path) -> None:
    artifact = work / "artifacts" / "cats.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(f"Praise for cats {SCOTS_FLAG}\n", encoding="utf-8")
    result = _run_check(work, ["1"])
    assert result.returncode == 0
    assert "observed" in result.stdout.lower()
    assert "not observed" not in result.stdout.lower()
    lines = [
        line
        for line in (work / "observations" / "run.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["step"] == 1
    assert record["probe"] == "r1-global-scots"
    assert record["observed"] is True


def test_rule_always_apply_no_globs_demands_flag() -> None:
    assert RULE.is_file()
    text = RULE.read_text(encoding="utf-8")
    assert "alwaysApply: true" in text or "alwaysApply:true" in text
    assert "globs:" not in text
    assert SCOTS_FLAG in text or "U+1F3F4" in text or "scotland" in text.lower()
    assert "cats.md" in text.lower() or "cats" in text.lower()


def test_prompt_provokes_cats_without_flag_leakage() -> None:
    assert PROMPT.is_file()
    text = PROMPT.read_text(encoding="utf-8")
    assert "cats.md" in text
    assert "artifacts" in text.lower()
    assert "paragraph" in text.lower()
    assert SCOTS_FLAG not in text
    assert "scottish" not in text.lower()
    assert "flag" not in text.lower()
    assert "1f3f4" not in text.lower()
    assert "u+1f3f4" not in text.lower()
