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


# --- Step 10 M1 observer ---


def test_observe_m1_skip_when_uv_unavailable(work: Path) -> None:
    """uv_version unavailable → observed=null; detail is skipped: uv not found."""
    check = _load_check_module()
    _write_run_json(work, uv_version="unavailable")
    result = check.observe_m1_mcp(10, work)
    assert result["observed"] is None
    assert result["detail"] == "skipped: uv not found"


def test_observe_m1_skip_when_uv_key_missing(work: Path) -> None:
    """Missing uv_version key → skip (same default as summary)."""
    check = _load_check_module()
    _write_run_json(work, uv_version=None)
    result = check.observe_m1_mcp(10, work)
    assert result["observed"] is None
    assert result["detail"] == "skipped: uv not found"


def test_observe_m1_missing_mcp_txt(work: Path) -> None:
    """uv present, missing mcp.txt → not observed; detail names the file."""
    check = _load_check_module()
    result = check.observe_m1_mcp(10, work)
    assert result["observed"] is False
    assert "mcp.txt" in result["detail"].lower()


def test_observe_m1_token_absent(work: Path) -> None:
    """mcp.txt without token → not observed."""
    check = _load_check_module()
    artifact = work / "artifacts" / "mcp.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("tool returned something else\n", encoding="utf-8")
    result = check.observe_m1_mcp(10, work)
    assert result["observed"] is False


def test_observe_m1_wrong_name_token(work: Path) -> None:
    """mcp.txt with MCP-OBSERVED-dogs only → not observed (prompt demands cats)."""
    check = _load_check_module()
    artifact = work / "artifacts" / "mcp.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("MCP-OBSERVED-dogs\n", encoding="utf-8")
    result = check.observe_m1_mcp(10, work)
    assert result["observed"] is False


def test_observe_m1_token_present(work: Path) -> None:
    """mcp.txt containing MCP-OBSERVED-cats → observed."""
    check = _load_check_module()
    artifact = work / "artifacts" / "mcp.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(f"note: {MCP_CATS_TOKEN}\n", encoding="utf-8")
    result = check.observe_m1_mcp(10, work)
    assert result["observed"] is True


def test_step10_registry_binds_observe_m1_mcp() -> None:
    """STEP_REGISTRY[10] observe is observe_m1_mcp (not stub)."""
    check = _load_check_module()
    assert check.STEP_REGISTRY[10]["observe"] is check.observe_m1_mcp


# --- CLI smoke step 10 ---


def test_check_cli_step10_observed(work: Path) -> None:
    """CLI step 10 with token → observed; mcp / server / m1-probe-mcp / create."""
    artifact = work / "artifacts" / "mcp.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(f"{MCP_CATS_TOKEN}\n", encoding="utf-8")
    result = _run_check(work, ["10"])
    assert result.returncode == 0
    assert "observed" in result.stdout.lower()
    assert "not observed" not in result.stdout.lower()
    assert "probe checker not implemented" not in result.stdout.lower()
    record = json.loads(
        (work / "observations" / "run.jsonl").read_text(encoding="utf-8").strip()
    )
    assert record["step"] == 10
    assert record["surface"] == "mcp"
    assert record["mode"] == "server"
    assert record["probe"] == "m1-probe-mcp"
    assert record["path"] == "create"
    assert record["observed"] is True
    assert "pass" not in record["detail"].lower()
    assert "fail" not in record["detail"].lower()
    assert "unsupported" not in record["detail"].lower()


def test_check_cli_step10_not_observed_exit_zero(work: Path) -> None:
    """CLI step 10 without artifact → not observed, exit 0."""
    result = _run_check(work, ["10"])
    assert result.returncode == 0
    assert "not observed" in result.stdout.lower()
    assert "probe checker not implemented" not in result.stdout.lower()


def test_check_cli_step10_skipped_exit_zero(work: Path) -> None:
    """CLI step 10 with uv unavailable → skipped, exit 0; no judgment language."""
    _write_run_json(work, uv_version="unavailable")
    result = _run_check(work, ["10"])
    assert result.returncode == 0
    assert "skipped" in result.stdout.lower()
    assert "not observed" not in result.stdout.lower()
    record = json.loads(
        (work / "observations" / "run.jsonl").read_text(encoding="utf-8").strip()
    )
    assert record["observed"] is None
    assert record["detail"] == "skipped: uv not found"
    assert "pass" not in record["detail"].lower()
    assert "fail" not in record["detail"].lower()
    assert "unsupported" not in record["detail"].lower()


def test_check_cli_step10_skip_wins_over_planted_artifact(work: Path) -> None:
    """uv unavailable skips even when mcp.txt with token is planted."""
    _write_run_json(work, uv_version="unavailable")
    artifact = work / "artifacts" / "mcp.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(f"{MCP_CATS_TOKEN}\n", encoding="utf-8")
    result = _run_check(work, ["10"])
    assert result.returncode == 0
    assert "skipped" in result.stdout.lower()
    record = json.loads(
        (work / "observations" / "run.jsonl").read_text(encoding="utf-8").strip()
    )
    assert record["observed"] is None
    assert record["detail"] == "skipped: uv not found"


# --- Server ---


def _load_server_module():
    spec = importlib.util.spec_from_file_location("probe_mcp", SERVER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_format_probe_hello_cats() -> None:
    """format_probe_hello('cats') returns MCP-OBSERVED-cats."""
    server = _load_server_module()
    assert server.format_probe_hello("cats") == MCP_CATS_TOKEN


def test_probe_mcp_has_pep723_mcp_dependency() -> None:
    """servers/probe_mcp.py declares PEP 723 script metadata with mcp dep."""
    assert SERVER.is_file()
    text = SERVER.read_text(encoding="utf-8")
    assert "# /// script" in text
    assert "dependencies" in text
    assert '"mcp"' in text or "'mcp'" in text


def test_probe_mcp_defines_probe_hello_tool() -> None:
    """Server source registers a probe_hello tool wired to the formatter."""
    text = SERVER.read_text(encoding="utf-8")
    assert "def probe_hello" in text
    assert "format_probe_hello" in text
    assert "FastMCP" in text
    assert "mcp.run()" in text or "mcp.run(" in text


# --- .mcp.json ---


def test_mcp_json_launches_uv_script_with_plugin_root() -> None:
    """.mcp.json mcpServers entry uses uv run --script with ${PLUGIN_ROOT} path."""
    assert MCP_JSON.is_file()
    data = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    assert "mcpServers" in data
    servers = data["mcpServers"]
    assert isinstance(servers, dict) and servers
    entry = next(iter(servers.values()))
    assert entry.get("command") == "uv"
    args = entry.get("args")
    assert isinstance(args, list)
    assert "run" in args
    assert "--script" in args
    script_args = [a for a in args if isinstance(a, str) and "probe_mcp.py" in a]
    assert script_args, "args must include path to probe_mcp.py"
    assert any("${PLUGIN_ROOT}" in a for a in script_args)
    assert any(
        "${PLUGIN_ROOT}/servers/probe_mcp.py" in a for a in script_args
    )


# --- Prompt 10 ---


def test_prompt_10_mcp_no_fingerprint_leakage() -> None:
    """Prompt 10 calls probe_hello(cats) + mcp.txt path; no fingerprint leakage."""
    assert PROMPT_10.is_file()
    text = PROMPT_10.read_text(encoding="utf-8")
    assert text.strip(), "prompt must not be empty"
    assert "probe_hello" in text
    assert "cats" in text
    assert "mcp.txt" in text
    assert "artifacts" in text.lower()
    _assert_no_prompt_leakage(text)
