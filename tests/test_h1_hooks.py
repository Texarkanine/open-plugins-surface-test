"""Contracts for H1 hooks probe: helpers, step-9 observer, summary SessionEnd, recorder, config, prompt."""

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
HOOK_RECORD = ROOT / "scripts" / "hook_record.sh"


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


HOOKS_JSON = ROOT / "hooks" / "hooks.json"
PROMPT_09 = ROOT / "prompts" / "09-h1-hooks-battery.md"

ALL_HOOK_EVENTS = (
    "SessionStart",
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "BeforeReadFile",
    "AfterFileEdit",
    "BeforeShellExecution",
    "AfterShellExecution",
    "Stop",
    "SubagentStart",
    "SubagentStop",
    "SessionEnd",
)

MID_RUN_HOOK_EVENTS = tuple(e for e in ALL_HOOK_EVENTS if e != "SessionEnd")

PROMPT_LEAK_PATTERNS = (
    re.compile(r"check\.py", re.IGNORECASE),
    re.compile(r"\bobserved\b", re.IGNORECASE),
    re.compile(r"hooks\.jsonl", re.IGNORECASE),
    re.compile(r"fingerprint", re.IGNORECASE),
    re.compile(r"sentinel", re.IGNORECASE),
)

JUDGMENT_BAN_RE = re.compile(r"\b(pass|fail|unsupported)\b", re.IGNORECASE)


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


def _plant_hooks_jsonl(work: Path, events: list[str]) -> Path:
    path = work / "observations" / "hooks.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps({"event": name, "matcher_context": "-", "ts": "t"}) + "\n"
        for name in events
    ]
    path.write_text("".join(lines), encoding="utf-8")
    return path


def _assert_no_judgment_language(text: str) -> None:
    # Word-boundary match: DESIGN event PostToolUseFailure contains the substring "fail".
    match = JUDGMENT_BAN_RE.search(text)
    assert match is None, f"judgment language {match.group(0)!r} found in:\n{text}"


@pytest.fixture
def work(tmp_path: Path) -> Path:
    work_dir = tmp_path / "work"
    _write_run_json(work_dir)
    return work_dir


# --- Helpers ---


def test_mid_run_constants_exclude_session_end() -> None:
    """MID_RUN_HOOK_EVENTS is the DESIGN catalog minus SessionEnd; SESSION_END_EVENT is SessionEnd."""
    check = _load_check_module()
    assert check.SESSION_END_EVENT == "SessionEnd"
    assert "SessionEnd" not in check.MID_RUN_HOOK_EVENTS
    assert tuple(check.MID_RUN_HOOK_EVENTS) == MID_RUN_HOOK_EVENTS
    assert len(check.MID_RUN_HOOK_EVENTS) == 12


def test_hooks_log_path(work: Path) -> None:
    """hooks_log_path returns work/observations/hooks.jsonl."""
    check = _load_check_module()
    assert check.hooks_log_path(work) == work / "observations" / "hooks.jsonl"


def test_event_names_from_hooks_jsonl_missing_empty(work: Path) -> None:
    """Missing file → empty set; empty file → empty set."""
    check = _load_check_module()
    path = check.hooks_log_path(work)
    assert check.event_names_from_hooks_jsonl(path) == set()
    path.parent.mkdir(parents=True)
    path.write_text("", encoding="utf-8")
    assert check.event_names_from_hooks_jsonl(path) == set()


def test_event_names_from_hooks_jsonl_distinct_and_tolerant(work: Path) -> None:
    """Parse distinct event names; skip blank and malformed lines without raising."""
    check = _load_check_module()
    path = work / "observations" / "hooks.jsonl"
    path.parent.mkdir(parents=True)
    path.write_text(
        "\n".join(
            [
                json.dumps({"event": "SessionStart", "matcher_context": "-", "ts": "t1"}),
                "",
                "not-json",
                json.dumps({"event": "PreToolUse", "matcher_context": "Bash", "ts": "t2"}),
                json.dumps({"event": "SessionStart", "matcher_context": "-", "ts": "t3"}),
                json.dumps({"no_event": True}),
                json.dumps({"event": 123}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    assert check.event_names_from_hooks_jsonl(path) == {"SessionStart", "PreToolUse"}


def test_format_hook_events_detail_covers_all_mid_run() -> None:
    """Detail lists every mid-run event with present/absent markers in catalog order."""
    check = _load_check_module()
    present = {"SessionStart", "PreToolUse"}
    detail = check.format_hook_events_detail(present)
    for name in MID_RUN_HOOK_EVENTS:
        assert name in detail
    assert "SessionEnd" not in detail
    # Present markers for the two events; absent for others
    assert re.search(r"SessionStart[^\n]*present", detail)
    assert re.search(r"PreToolUse[^\n]*present", detail)
    assert re.search(r"UserPromptSubmit[^\n]*absent", detail)
    # Order follows MID_RUN_HOOK_EVENTS
    positions = [detail.index(name) for name in MID_RUN_HOOK_EVENTS]
    assert positions == sorted(positions)


# --- Observer ---


def test_observe_h1_hooks_missing_log(work: Path) -> None:
    """Missing hooks.jsonl → not observed; detail names the file."""
    check = _load_check_module()
    result = check.observe_h1_hooks(9, work)
    assert result["observed"] is False
    assert "hooks.jsonl" in result["detail"]
    _assert_no_judgment_language(result["detail"])


def test_observe_h1_hooks_empty_log(work: Path) -> None:
    """Empty log → not observed; detail marks all 12 mid-run events absent."""
    check = _load_check_module()
    path = check.hooks_log_path(work)
    path.parent.mkdir(parents=True)
    path.write_text("", encoding="utf-8")
    result = check.observe_h1_hooks(9, work)
    assert result["observed"] is False
    for name in MID_RUN_HOOK_EVENTS:
        assert name in result["detail"]
        assert re.search(rf"{name}[^\n]*absent", result["detail"])
    assert "SessionEnd" not in result["detail"]


def test_observe_h1_hooks_partial_mid_run(work: Path) -> None:
    """Any mid-run event → observed; detail shows present/absent; incomplete set is fine."""
    check = _load_check_module()
    _plant_hooks_jsonl(work, ["SessionStart", "PreToolUse"])
    result = check.observe_h1_hooks(9, work)
    assert result["observed"] is True
    assert re.search(r"SessionStart[^\n]*present", result["detail"])
    assert re.search(r"PreToolUse[^\n]*present", result["detail"])
    assert re.search(r"Stop[^\n]*absent", result["detail"])
    assert "SessionEnd" not in result["detail"]
    _assert_no_judgment_language(result["detail"])


def test_observe_h1_hooks_only_session_end(work: Path) -> None:
    """Only SessionEnd in log → step 9 not observed (SessionEnd excluded from mid-run)."""
    check = _load_check_module()
    _plant_hooks_jsonl(work, ["SessionEnd"])
    result = check.observe_h1_hooks(9, work)
    assert result["observed"] is False
    for name in MID_RUN_HOOK_EVENTS:
        assert re.search(rf"{name}[^\n]*absent", result["detail"])


def test_step_registry_9_binds_observe_h1_hooks() -> None:
    """STEP_REGISTRY[9] uses observe_h1_hooks with hooks/events/h1-hooks-battery/aggregate."""
    check = _load_check_module()
    entry = check.STEP_REGISTRY[9]
    assert entry["surface"] == "hooks"
    assert entry["mode"] == "events"
    assert entry["probe"] == "h1-hooks-battery"
    assert entry["path"] == "aggregate"
    assert entry["observe"] is check.observe_h1_hooks


# --- CLI step 9 ---


def test_check_cli_step9_observed(work: Path) -> None:
    """CLI step 9 with mid-run events → observed; JSONL metadata; non-stub detail."""
    _plant_hooks_jsonl(work, ["SessionStart", "AfterShellExecution"])
    result = _run_check(work, ["9"])
    assert result.returncode == 0
    assert "observed" in result.stdout.lower()
    assert "not observed" not in result.stdout.lower()
    assert "probe checker not implemented" not in result.stdout.lower()
    record = json.loads(
        (work / "observations" / "run.jsonl").read_text(encoding="utf-8").strip()
    )
    assert record["step"] == 9
    assert record["surface"] == "hooks"
    assert record["mode"] == "events"
    assert record["probe"] == "h1-hooks-battery"
    assert record["path"] == "aggregate"
    assert record["observed"] is True
    assert "SessionStart" in record["detail"]
    assert "probe checker not implemented" not in record["detail"]
    _assert_no_judgment_language(record["detail"])
    _assert_no_judgment_language(result.stdout)


def test_check_cli_step9_not_observed_exit_zero(work: Path) -> None:
    """CLI step 9 without hooks log → not observed, exit 0."""
    result = _run_check(work, ["9"])
    assert result.returncode == 0
    assert "not observed" in result.stdout.lower()
    assert "probe checker not implemented" not in result.stdout.lower()


# --- Summary SessionEnd ---


def test_summary_session_end_observed(work: Path) -> None:
    """Summary prints SessionEnd observed when present in hooks.jsonl; exit 0."""
    _plant_hooks_jsonl(work, ["SessionStart", "SessionEnd"])
    (work / "observations" / "run.jsonl").write_text(
        json.dumps(
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
            }
        )
        + "\n",
        encoding="utf-8",
    )
    result = _run_check(work, ["--summary"])
    assert result.returncode == 0
    assert re.search(r"SessionEnd:\s*✅\s*observed", result.stdout)
    _assert_no_judgment_language(result.stdout)


def test_summary_session_end_not_observed_empty_run(work: Path) -> None:
    """Summary prints SessionEnd not observed even when run.jsonl is empty; exit 0."""
    result = _run_check(work, ["--summary"])
    assert result.returncode == 0
    assert "(no observations recorded)" in result.stdout
    assert re.search(r"SessionEnd:\s*❌\s*not observed", result.stdout)
    _assert_no_judgment_language(result.stdout)


def test_summary_session_end_only_in_hooks_log(work: Path) -> None:
    """SessionEnd-only hooks log → summary observes SessionEnd; step table may be empty."""
    _plant_hooks_jsonl(work, ["SessionEnd"])
    result = _run_check(work, ["--summary"])
    assert result.returncode == 0
    assert re.search(r"SessionEnd:\s*✅\s*observed", result.stdout)


# --- Recorder ---


def test_hook_record_appends_jsonl(work: Path) -> None:
    """hook_record.sh EventName appends valid JSONL under CONFORMANCE_WORK/observations."""
    assert HOOK_RECORD.is_file()
    assert os.access(HOOK_RECORD, os.X_OK)
    env = os.environ.copy()
    env["CONFORMANCE_WORK"] = str(work)
    proc = subprocess.run(
        ["bash", str(HOOK_RECORD), "PreToolUse"],
        input='{"matcher":"Bash","tool_name":"Bash"}',
        text=True,
        capture_output=True,
        env=env,
        cwd=str(ROOT),
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    path = work / "observations" / "hooks.jsonl"
    assert path.is_file()
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["event"] == "PreToolUse"
    assert isinstance(row["matcher_context"], str) and row["matcher_context"]
    assert isinstance(row["ts"], str) and row["ts"]


def test_hook_record_without_override_writes_under_current(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without CONFORMANCE_WORK, hook_record appends under plugintest/CURRENT."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CONFORMANCE_WORK", raising=False)
    env = os.environ.copy()
    env.pop("CONFORMANCE_WORK", None)
    with _without_plugin_pointer():
        proc = subprocess.run(
            ["bash", str(HOOK_RECORD), "PreToolUse"],
            input='{"matcher":"Bash","tool_name":"Bash"}',
            text=True,
            capture_output=True,
            env=env,
            cwd=str(tmp_path),
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        current = tmp_path / "plugintest" / "CURRENT"
        path = current / "observations" / "hooks.jsonl"
        assert path.is_file()
        lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(lines) == 1
        row = json.loads(lines[0])
        assert row["event"] == "PreToolUse"


def test_hook_record_then_observer_sees_event(work: Path) -> None:
    """Recorder → observer integration: recorded event is visible to observe_h1_hooks."""
    env = os.environ.copy()
    env["CONFORMANCE_WORK"] = str(work)
    proc = subprocess.run(
        ["bash", str(HOOK_RECORD), "SessionStart"],
        input="",
        text=True,
        capture_output=True,
        env=env,
        cwd=str(ROOT),
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    check = _load_check_module()
    result = check.observe_h1_hooks(9, work)
    assert result["observed"] is True
    assert re.search(r"SessionStart[^\n]*present", result["detail"])


# --- hooks.json ---


def test_hooks_json_routes_all_thirteen_events() -> None:
    """hooks.json wrapper; all 13 events; command uses ${PLUGIN_ROOT}/scripts/hook_record.sh."""
    assert HOOKS_JSON.is_file()
    data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    assert "hooks" in data
    hooks = data["hooks"]
    for event in ALL_HOOK_EVENTS:
        assert event in hooks, f"missing event key {event}"
        rules = hooks[event]
        assert isinstance(rules, list) and rules
        found_recorder = False
        for rule in rules:
            for action in rule.get("hooks", []):
                if action.get("type") != "command":
                    continue
                command = action.get("command", "")
                assert "${PLUGIN_ROOT}" in command
                assert "CLAUDE_PLUGIN_ROOT" not in command
                if "hook_record.sh" in command and event in command:
                    found_recorder = True
        assert found_recorder, f"{event} does not route to hook_record.sh with event name"


# --- Prompt ---


def test_prompt_09_action_battery_no_leakage() -> None:
    """Prompt 09 instructs write/edit/read/shell/fail; no checker or event laundry list."""
    assert PROMPT_09.is_file()
    text = PROMPT_09.read_text(encoding="utf-8")
    assert text.strip(), "prompt must not be empty"
    lowered = text.lower()
    assert "write" in lowered or "create" in lowered
    assert "edit" in lowered
    assert "read" in lowered
    assert "shell" in lowered or "command" in lowered
    assert "non-zero" in lowered or "nonzero" in lowered or "exit code" in lowered
    for pattern in PROMPT_LEAK_PATTERNS:
        assert pattern.search(text) is None, f"prompt leaked: {pattern.pattern}"
    # Event-name laundry list: more than a couple of DESIGN event names is leakage
    named = sum(1 for event in ALL_HOOK_EVENTS if event in text)
    assert named <= 1, f"prompt lists too many hook event names ({named})"
