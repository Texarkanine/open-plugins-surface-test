"""Contracts for M1 MCP checker, server, .mcp.json, and prompt 10."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check.py"
SERVER = ROOT / "servers" / "probe_mcp.py"
MCP_JSON = ROOT / ".mcp.json"
PROMPT_10 = ROOT / "prompts" / "10-m1-mcp.md"

MCP_CATS_TOKEN = "MCP-OBSERVED-cats"
MCP_PREFIX = "MCP-OBSERVED"

PROMPT_LEAK_PATTERNS = (
    re.compile(r"check\.py", re.IGNORECASE),
    re.compile(r"\bobserved\b", re.IGNORECASE),
    re.compile(r"sentinel", re.IGNORECASE),
    re.compile(r"fingerprint", re.IGNORECASE),
)


def _load_check_module():
    spec = importlib.util.spec_from_file_location("check_harness", CHECK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_run_json(work: Path, *, uv_version: str | None = "test-uv") -> None:
    work.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "harness": "test-harness",
        "model": "test-model",
        "os": "test-os",
    }
    if uv_version is not None:
        payload["uv_version"] = uv_version
    (work / "run.json").write_text(
        json.dumps(payload, indent=2) + "\n",
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


def _assert_no_prompt_leakage(text: str) -> None:
    assert MCP_PREFIX not in text, "prompt leaked MCP-OBSERVED fingerprint"
    for pattern in PROMPT_LEAK_PATTERNS:
        assert pattern.search(text) is None, f"prompt leaked: {pattern.pattern}"


@pytest.fixture
def work(tmp_path: Path) -> Path:
    work_dir = tmp_path / "work"
    _write_run_json(work_dir)
    return work_dir


# --- uv_unavailable helper ---


def test_uv_unavailable_true_when_unavailable(work: Path) -> None:
    """uv_unavailable is True when uv_version is the unavailable sentinel."""
    check = _load_check_module()
    _write_run_json(work, uv_version="unavailable")
    assert check.uv_unavailable(work) is True


def test_uv_unavailable_true_when_key_missing(work: Path) -> None:
    """uv_unavailable is True when uv_version key is missing (summary default)."""
    check = _load_check_module()
    _write_run_json(work, uv_version=None)
    assert check.uv_unavailable(work) is True


def test_uv_unavailable_false_for_real_version(work: Path) -> None:
    """uv_unavailable is False when uv_version is a real version string."""
    check = _load_check_module()
    _write_run_json(work, uv_version="0.6.14")
    assert check.uv_unavailable(work) is False
