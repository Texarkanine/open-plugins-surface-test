"""Contracts for L1 LSP checker, server, .lsp.json, and prompt 11."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check.py"
SERVER = ROOT / "servers" / "probe_lsp.py"
LSP_JSON = ROOT / ".lsp.json"
PROMPT_11 = ROOT / "prompts" / "11-l1-lsp.md"
DESIGN = ROOT / "DESIGN.md"

PROMPT_LEAK_PATTERNS = (
    re.compile(r"check\.py", re.IGNORECASE),
    re.compile(r"\bobserved\b", re.IGNORECASE),
    re.compile(r"sentinel", re.IGNORECASE),
    re.compile(r"fingerprint", re.IGNORECASE),
    re.compile(r"lsp\.launched", re.IGNORECASE),
    re.compile(r"\bclaim\b", re.IGNORECASE),
)


@contextmanager
def _without_plugin_pointer():
    pointer = ROOT / ".conformance-work"
    backup = pointer.read_text(encoding="utf-8") if pointer.is_file() else None
    if pointer.is_file():
        pointer.unlink()
    try:
        yield
    finally:
        if backup is not None:
            pointer.write_text(backup, encoding="utf-8")
        elif pointer.is_file():
            pointer.unlink()


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


def _plant_marker(work: Path) -> Path:
    marker = work / "observations" / "lsp.launched"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("launched\n", encoding="utf-8")
    return marker


def _read_jsonl_record(work: Path) -> dict[str, object]:
    return json.loads(
        (work / "observations" / "run.jsonl").read_text(encoding="utf-8").strip()
    )


@pytest.fixture
def work(tmp_path: Path) -> Path:
    work_dir = tmp_path / "work"
    _write_run_json(work_dir)
    return work_dir


# --- Step 11 L1 observer ---


def test_observe_l1_skip_when_uv_unavailable(work: Path) -> None:
    """uv_version unavailable → observed=null; detail is skipped: uv not found."""
    check = _load_check_module()
    _write_run_json(work, uv_version="unavailable")
    result = check.observe_l1_lsp(11, work)
    assert result["observed"] is None
    assert result["detail"] == "skipped: uv not found"


def test_observe_l1_skip_when_uv_key_missing(work: Path) -> None:
    """Missing uv_version key → skip (same default as summary)."""
    check = _load_check_module()
    _write_run_json(work, uv_version=None)
    result = check.observe_l1_lsp(11, work)
    assert result["observed"] is None
    assert result["detail"] == "skipped: uv not found"


def test_observe_l1_marker_absent(work: Path) -> None:
    """uv present, missing lsp.launched → not observed; detail names the marker."""
    check = _load_check_module()
    result = check.observe_l1_lsp(11, work)
    assert result["observed"] is False
    assert "lsp.launched" in result["detail"].lower()


def test_observe_l1_marker_present(work: Path) -> None:
    """lsp.launched exists → observed."""
    check = _load_check_module()
    _plant_marker(work)
    result = check.observe_l1_lsp(11, work)
    assert result["observed"] is True


def test_step11_registry_binds_observe_l1_lsp() -> None:
    """STEP_REGISTRY[11] observe is observe_l1_lsp; path launched; claim launched."""
    check = _load_check_module()
    entry = check.STEP_REGISTRY[11]
    assert entry["observe"] is check.observe_l1_lsp
    assert entry["path"] == "launched"
    assert entry["claim"] == "launched"
    assert entry["surface"] == "lsp"
    assert entry["mode"] == "server"
    assert entry["probe"] == "l1-probe-lsp"


# --- CLI smoke step 11 ---


def test_check_cli_step11_observed_includes_claim(work: Path) -> None:
    """CLI step 11 with marker → observed; JSONL includes claim: launched."""
    _plant_marker(work)
    result = _run_check(work, ["11"])
    assert result.returncode == 0
    assert "observed" in result.stdout.lower()
    assert "not observed" not in result.stdout.lower()
    assert "probe checker not implemented" not in result.stdout.lower()
    record = _read_jsonl_record(work)
    assert record["step"] == 11
    assert record["surface"] == "lsp"
    assert record["mode"] == "server"
    assert record["probe"] == "l1-probe-lsp"
    assert record["path"] == "launched"
    assert record["observed"] is True
    assert record["claim"] == "launched"
    assert "pass" not in str(record["detail"]).lower()
    assert "fail" not in str(record["detail"]).lower()
    assert "unsupported" not in str(record["detail"]).lower()


def test_check_cli_step11_not_observed_exit_zero_includes_claim(work: Path) -> None:
    """CLI step 11 without marker → not observed, exit 0; claim still present."""
    result = _run_check(work, ["11"])
    assert result.returncode == 0
    assert "not observed" in result.stdout.lower()
    assert "probe checker not implemented" not in result.stdout.lower()
    record = _read_jsonl_record(work)
    assert record["observed"] is False
    assert record["claim"] == "launched"


def test_check_cli_step11_skipped_exit_zero_includes_claim(work: Path) -> None:
    """CLI step 11 with uv unavailable → skipped, exit 0; claim still present."""
    _write_run_json(work, uv_version="unavailable")
    result = _run_check(work, ["11"])
    assert result.returncode == 0
    assert "skipped" in result.stdout.lower()
    assert "not observed" not in result.stdout.lower()
    record = _read_jsonl_record(work)
    assert record["observed"] is None
    assert record["detail"] == "skipped: uv not found"
    assert record["claim"] == "launched"


def test_check_cli_step11_skip_wins_over_planted_marker(work: Path) -> None:
    """uv unavailable skips even when lsp.launched is planted."""
    _write_run_json(work, uv_version="unavailable")
    _plant_marker(work)
    result = _run_check(work, ["11"])
    assert result.returncode == 0
    assert "skipped" in result.stdout.lower()
    record = _read_jsonl_record(work)
    assert record["observed"] is None
    assert record["detail"] == "skipped: uv not found"
    assert record["claim"] == "launched"


# --- Server ---


def _load_server_module():
    spec = importlib.util.spec_from_file_location("probe_lsp", SERVER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _send_lsp(proc: subprocess.Popen[bytes], msg: dict[str, object]) -> None:
    assert proc.stdin is not None
    raw = json.dumps(msg).encode("utf-8")
    proc.stdin.write(f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii"))
    proc.stdin.write(raw)
    proc.stdin.flush()


def _read_lsp(proc: subprocess.Popen[bytes]) -> dict[str, object]:
    assert proc.stdout is not None
    headers = b""
    while not headers.endswith(b"\r\n\r\n"):
        chunk = proc.stdout.read(1)
        assert chunk, "LSP server closed stdout before headers finished"
        headers += chunk
    length = 0
    for line in headers.decode("ascii").split("\r\n"):
        if line.lower().startswith("content-length:"):
            length = int(line.split(":", 1)[1].strip())
    body = proc.stdout.read(length)
    return json.loads(body.decode("utf-8"))


def test_write_launch_marker_creates_observations_file(work: Path) -> None:
    """write_launch_marker creates work/observations/lsp.launched."""
    server = _load_server_module()
    marker = server.write_launch_marker(work)
    assert marker == work / "observations" / "lsp.launched"
    assert marker.is_file()


def test_resolve_work_root_honors_conformance_work(
    work: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """resolve_work_root returns CONFORMANCE_WORK when set."""
    server = _load_server_module()
    monkeypatch.setenv("CONFORMANCE_WORK", str(work))
    assert server.resolve_work_root() == work.resolve()


def test_resolve_work_root_defaults_to_cwd_plugintest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without CONFORMANCE_WORK, resolve_work_root is cwd plugintest/CURRENT."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CONFORMANCE_WORK", raising=False)
    with _without_plugin_pointer():
        server = _load_server_module()
        result = server.resolve_work_root()
        current = (tmp_path / "plugintest" / "CURRENT").resolve()
        assert result == current
        assert result != (ROOT / "work").resolve()


def test_probe_lsp_has_pep723_script_header() -> None:
    """servers/probe_lsp.py declares PEP 723 script metadata."""
    assert SERVER.is_file()
    text = SERVER.read_text(encoding="utf-8")
    assert "# /// script" in text
    assert "requires-python" in text


def test_initialize_writes_launch_marker(work: Path) -> None:
    """Client initialize handshake causes server to write lsp.launched."""
    assert SERVER.is_file()
    env = os.environ.copy()
    env["CONFORMANCE_WORK"] = str(work)
    proc = subprocess.Popen(
        [sys.executable, str(SERVER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=str(ROOT),
    )
    try:
        _send_lsp(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "processId": None,
                    "rootUri": None,
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0"},
                },
            },
        )
        resp = _read_lsp(proc)
        assert resp.get("id") == 1
        assert "result" in resp
        _send_lsp(proc, {"jsonrpc": "2.0", "method": "initialized", "params": {}})
        _send_lsp(proc, {"jsonrpc": "2.0", "id": 2, "method": "shutdown", "params": None})
        _read_lsp(proc)
        _send_lsp(proc, {"jsonrpc": "2.0", "method": "exit"})
        proc.wait(timeout=5)
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)

    marker = work / "observations" / "lsp.launched"
    assert marker.is_file()
    assert proc.returncode == 0


# --- .lsp.json ---


def test_lsp_json_launches_uv_script_with_plugin_root() -> None:
    """.lsp.json top-level entry uses uv run --script with ${PLUGIN_ROOT} path."""
    assert LSP_JSON.is_file()
    data = json.loads(LSP_JSON.read_text(encoding="utf-8"))
    assert "lspServers" not in data
    assert isinstance(data, dict) and data
    entry = data.get("probe-lsp")
    assert isinstance(entry, dict)
    assert entry.get("command") == "uv"
    args = entry.get("args")
    assert isinstance(args, list)
    assert "run" in args
    assert "--script" in args
    script_args = [a for a in args if isinstance(a, str) and "probe_lsp.py" in a]
    assert script_args, "args must include path to probe_lsp.py"
    assert any("${PLUGIN_ROOT}" in a for a in script_args)
    assert any(
        "${PLUGIN_ROOT}/servers/probe_lsp.py" in a for a in script_args
    )
    ext_map = entry.get("extensionToLanguage")
    assert isinstance(ext_map, dict)
    assert ext_map.get(".lspprobe") == "lspprobe"


# --- Prompt 11 ---


def _assert_no_prompt_leakage(text: str) -> None:
    for pattern in PROMPT_LEAK_PATTERNS:
        assert pattern.search(text) is None, f"prompt leaked: {pattern.pattern}"


def test_prompt_11_lsp_passive_no_leakage() -> None:
    """Prompt 11 opens probe.lspprobe only; no marker/claim/checker leakage."""
    assert PROMPT_11.is_file()
    text = PROMPT_11.read_text(encoding="utf-8")
    assert text.strip(), "prompt must not be empty"
    assert "probe.lspprobe" in text
    assert "fixtures" in text.lower()
    _assert_no_prompt_leakage(text)


# --- DESIGN open-question close-out ---


def test_design_lsp_open_question_resolved() -> None:
    """DESIGN.md resolves LSP observability with launch marker + claim: launched."""
    text = DESIGN.read_text(encoding="utf-8")
    open_section = text.split("## Open Questions", 1)[1].split("## Implementation Plan", 1)[0]
    assert "LSP observability" not in open_section
    assert "lsp.launched" in text
    assert '"claim":"launched"' in text or '"claim": "launched"' in text
