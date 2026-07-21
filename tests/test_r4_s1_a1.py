"""Contracts for R4/S1/A1 checkers, components, and prompts 06–08."""

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
RULE_R4 = ROOT / "rules" / "r4-sea-poem.mdc"
SKILL_S1 = ROOT / "skills" / "build-stamp" / "SKILL.md"
AGENT_A1 = ROOT / "agents" / "listing-auditor.md"
PROMPT_06 = ROOT / "prompts" / "06-r4-poem.md"
PROMPT_07 = ROOT / "prompts" / "07-s1-stamp.md"
PROMPT_08 = ROOT / "prompts" / "08-a1-audit.md"

SEA_POEM_SENTINEL = "SEA-POEM-OBSERVED"
BUILD_STAMP_TOKEN = "BUILD-STAMP-OBSERVED"
LISTING_AUDITOR_TOKEN = "LISTING-AUDITOR-OBSERVED"
ALL_FINGERPRINTS = (SEA_POEM_SENTINEL, BUILD_STAMP_TOKEN, LISTING_AUDITOR_TOKEN)

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


def _assert_no_fingerprint_leakage(text: str) -> None:
    for token in ALL_FINGERPRINTS:
        assert token not in text, f"prompt leaked fingerprint {token}"
    for pattern in PROMPT_LEAK_PATTERNS:
        assert pattern.search(text) is None, f"prompt leaked: {pattern.pattern}"


@pytest.fixture
def work(tmp_path: Path) -> Path:
    work_dir = tmp_path / "work"
    _write_run_json(work_dir)
    return work_dir


# --- Shared helpers ---


def test_last_nonempty_line_empty_and_whitespace() -> None:
    """last_nonempty_line returns "" for empty or whitespace-only text."""
    check = _load_check_module()
    assert check.last_nonempty_line("") == ""
    assert check.last_nonempty_line("   \n\t\n  ") == ""


def test_last_nonempty_line_strips_and_picks_last() -> None:
    """last_nonempty_line returns the last non-empty line, stripped."""
    check = _load_check_module()
    assert check.last_nonempty_line("alpha\nbeta\n") == "beta"
    assert check.last_nonempty_line("alpha\n  beta  \n\n") == "beta"
    assert check.last_nonempty_line("only\n") == "only"


def test_artifact_contains_missing_absent_present(work: Path) -> None:
    """artifact_contains: missing False; token absent False; token present True."""
    check = _load_check_module()
    path = work / "artifacts" / "stamp.txt"
    assert check.artifact_contains(path, BUILD_STAMP_TOKEN) is False
    path.parent.mkdir(parents=True)
    path.write_text("no token here\n", encoding="utf-8")
    assert check.artifact_contains(path, BUILD_STAMP_TOKEN) is False
    path.write_text(f"hello {BUILD_STAMP_TOKEN} world\n", encoding="utf-8")
    assert check.artifact_contains(path, BUILD_STAMP_TOKEN) is True


def test_closing_line_equals_missing_mismatch_match(work: Path) -> None:
    """closing_line_equals: missing/mismatch False; last non-empty equals True."""
    check = _load_check_module()
    path = work / "artifacts" / "poem.txt"
    assert check.closing_line_equals(path, SEA_POEM_SENTINEL) is False
    path.parent.mkdir(parents=True)
    path.write_text("waves crash\non rocks\n", encoding="utf-8")
    assert check.closing_line_equals(path, SEA_POEM_SENTINEL) is False
    path.write_text(f"waves\n{SEA_POEM_SENTINEL}\n\n", encoding="utf-8")
    assert check.closing_line_equals(path, SEA_POEM_SENTINEL) is True
    path.write_text(f"waves\n{SEA_POEM_SENTINEL}  \n", encoding="utf-8")
    assert check.closing_line_equals(path, SEA_POEM_SENTINEL) is True


# --- Step 6 R4 observer ---


def test_observe_r4_missing_poem(work: Path) -> None:
    """Missing poem.txt → not observed; detail names the file."""
    check = _load_check_module()
    result = check.observe_r4_sea_poem(6, work)
    assert result["observed"] is False
    assert "poem.txt" in result["detail"].lower()


def test_observe_r4_no_sentinel_closing_line(work: Path) -> None:
    """Poem without sentinel closing line → not observed."""
    check = _load_check_module()
    artifact = work / "artifacts" / "poem.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("The sea is wide.\nSalt on the wind.\n", encoding="utf-8")
    result = check.observe_r4_sea_poem(6, work)
    assert result["observed"] is False


def test_observe_r4_sentinel_mid_file_not_closing(work: Path) -> None:
    """Sentinel only mid-file (not closing line) → not observed."""
    check = _load_check_module()
    artifact = work / "artifacts" / "poem.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        f"Line one\n{SEA_POEM_SENTINEL}\nLine three\n",
        encoding="utf-8",
    )
    result = check.observe_r4_sea_poem(6, work)
    assert result["observed"] is False


def test_observe_r4_sentinel_closing_line(work: Path) -> None:
    """Last non-empty line equals SEA-POEM-OBSERVED → observed."""
    check = _load_check_module()
    artifact = work / "artifacts" / "poem.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        f"Tide pulls away\n{SEA_POEM_SENTINEL}\n",
        encoding="utf-8",
    )
    result = check.observe_r4_sea_poem(6, work)
    assert result["observed"] is True


# --- Step 7 S1 observer ---


def test_observe_s1_missing_stamp(work: Path) -> None:
    """Missing stamp.txt → not observed."""
    check = _load_check_module()
    result = check.observe_s1_build_stamp(7, work)
    assert result["observed"] is False
    assert "stamp.txt" in result["detail"].lower()


def test_observe_s1_token_absent(work: Path) -> None:
    """stamp.txt without token → not observed."""
    check = _load_check_module()
    artifact = work / "artifacts" / "stamp.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("build stamped at noon\n", encoding="utf-8")
    result = check.observe_s1_build_stamp(7, work)
    assert result["observed"] is False


def test_observe_s1_token_present(work: Path) -> None:
    """stamp.txt with BUILD-STAMP-OBSERVED → observed."""
    check = _load_check_module()
    artifact = work / "artifacts" / "stamp.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(f"ok {BUILD_STAMP_TOKEN}\n", encoding="utf-8")
    result = check.observe_s1_build_stamp(7, work)
    assert result["observed"] is True


# --- Step 8 A1 observer ---


def test_observe_a1_missing_agent(work: Path) -> None:
    """Missing agent.txt → not observed."""
    check = _load_check_module()
    result = check.observe_a1_listing_auditor(8, work)
    assert result["observed"] is False
    assert "agent.txt" in result["detail"].lower()


def test_observe_a1_token_absent(work: Path) -> None:
    """agent.txt without token → not observed."""
    check = _load_check_module()
    artifact = work / "artifacts" / "agent.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("listing looks fine\n", encoding="utf-8")
    result = check.observe_a1_listing_auditor(8, work)
    assert result["observed"] is False


def test_observe_a1_token_present(work: Path) -> None:
    """agent.txt with LISTING-AUDITOR-OBSERVED → observed."""
    check = _load_check_module()
    artifact = work / "artifacts" / "agent.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(f"audit {LISTING_AUDITOR_TOKEN}\n", encoding="utf-8")
    result = check.observe_a1_listing_auditor(8, work)
    assert result["observed"] is True


# --- Cross-probe path isolation ---


def test_cross_probe_poem_does_not_satisfy_stamp_or_agent(work: Path) -> None:
    """Compliant poem.txt does not credit stamp or agent observers."""
    check = _load_check_module()
    artifact = work / "artifacts" / "poem.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(f"waves\n{SEA_POEM_SENTINEL}\n", encoding="utf-8")
    assert check.observe_r4_sea_poem(6, work)["observed"] is True
    assert check.observe_s1_build_stamp(7, work)["observed"] is False
    assert check.observe_a1_listing_auditor(8, work)["observed"] is False


# --- CLI smoke steps 6–8 ---


def test_check_cli_step6_observed(work: Path) -> None:
    """CLI step 6 with compliant poem → observed; JSONL probe/mode fields."""
    artifact = work / "artifacts" / "poem.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(f"sea\n{SEA_POEM_SENTINEL}\n", encoding="utf-8")
    result = _run_check(work, ["6"])
    assert result.returncode == 0
    assert "observed" in result.stdout.lower()
    assert "not observed" not in result.stdout.lower()
    assert "probe checker not implemented" not in result.stdout.lower()
    lines = [
        line
        for line in (work / "observations" / "run.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["step"] == 6
    assert record["probe"] == "r4-sea-poem"
    assert record["mode"] == "description"
    assert record["surface"] == "rules"
    assert record["observed"] is True


def test_check_cli_step6_not_observed_exit_zero(work: Path) -> None:
    """CLI step 6 without artifact → not observed, exit 0."""
    result = _run_check(work, ["6"])
    assert result.returncode == 0
    assert "not observed" in result.stdout.lower()
    assert "probe checker not implemented" not in result.stdout.lower()


def test_check_cli_step7_observed(work: Path) -> None:
    """CLI step 7 with token → observed; skills / s1-build-stamp / description."""
    artifact = work / "artifacts" / "stamp.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(f"{BUILD_STAMP_TOKEN}\n", encoding="utf-8")
    result = _run_check(work, ["7"])
    assert result.returncode == 0
    assert "observed" in result.stdout.lower()
    assert "not observed" not in result.stdout.lower()
    record = json.loads(
        (work / "observations" / "run.jsonl").read_text(encoding="utf-8").strip()
    )
    assert record["step"] == 7
    assert record["surface"] == "skills"
    assert record["probe"] == "s1-build-stamp"
    assert record["mode"] == "description"
    assert record["observed"] is True


def test_check_cli_step7_not_observed_exit_zero(work: Path) -> None:
    """CLI step 7 without artifact → not observed, exit 0."""
    result = _run_check(work, ["7"])
    assert result.returncode == 0
    assert "not observed" in result.stdout.lower()
    assert "probe checker not implemented" not in result.stdout.lower()


def test_check_cli_step8_observed(work: Path) -> None:
    """CLI step 8 with token → observed; agents / a1-listing-auditor / description."""
    artifact = work / "artifacts" / "agent.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(f"{LISTING_AUDITOR_TOKEN}\n", encoding="utf-8")
    result = _run_check(work, ["8"])
    assert result.returncode == 0
    assert "observed" in result.stdout.lower()
    assert "not observed" not in result.stdout.lower()
    record = json.loads(
        (work / "observations" / "run.jsonl").read_text(encoding="utf-8").strip()
    )
    assert record["step"] == 8
    assert record["surface"] == "agents"
    assert record["probe"] == "a1-listing-auditor"
    assert record["mode"] == "description"
    assert record["observed"] is True


def test_check_cli_step8_not_observed_exit_zero(work: Path) -> None:
    """CLI step 8 without artifact → not observed, exit 0."""
    result = _run_check(work, ["8"])
    assert result.returncode == 0
    assert "not observed" in result.stdout.lower()
    assert "probe checker not implemented" not in result.stdout.lower()


# --- Components ---


def test_rule_r4_description_only_demands_sentinel() -> None:
    """R4: description present; no alwaysApply/globs; body demands sentinel + poem.txt."""
    assert RULE_R4.is_file()
    text = RULE_R4.read_text(encoding="utf-8")
    assert text.strip(), "rule file must not be empty"
    assert re.search(r"(?m)^description:\s*\S", text)
    assert "alwaysApply" not in text
    assert "globs:" not in text
    assert SEA_POEM_SENTINEL in text
    assert "poem.txt" in text


def test_skill_s1_frontmatter_and_token() -> None:
    """S1: name build-stamp; strong stamp/build description; body demands token + stamp.txt."""
    assert SKILL_S1.is_file()
    text = SKILL_S1.read_text(encoding="utf-8")
    assert text.strip(), "skill file must not be empty"
    assert re.search(r"(?m)^name:\s*build-stamp\s*$", text)
    assert re.search(r"(?m)^description:\s*\S", text)
    desc_match = re.search(
        r"(?ms)^description:\s*(.+?)(?=^[a-zA-Z_][\w-]*:|\n---)",
        text,
    )
    assert desc_match is not None
    description = desc_match.group(1).lower()
    assert "stamp" in description
    assert "build" in description
    assert BUILD_STAMP_TOKEN not in description
    assert BUILD_STAMP_TOKEN in text
    assert "stamp.txt" in text


def test_agent_a1_description_and_token() -> None:
    """A1: strong listing-audit description; body demands token + agent.txt."""
    assert AGENT_A1.is_file()
    text = AGENT_A1.read_text(encoding="utf-8")
    assert text.strip(), "agent file must not be empty"
    assert re.search(r"(?m)^description:\s*\S", text)
    desc_match = re.search(
        r"(?ms)^description:\s*(.+?)(?=^[a-zA-Z_][\w-]*:|\n---)",
        text,
    )
    assert desc_match is not None
    description = desc_match.group(1).lower()
    assert "audit" in description or "listing" in description
    assert "fixture" in description
    assert LISTING_AUDITOR_TOKEN not in description
    assert LISTING_AUDITOR_TOKEN in text
    assert "agent.txt" in text


# --- Prompts ---


def test_prompt_06_poem_no_fingerprint_leakage() -> None:
    """Prompt 06 provokes poem + path; no fingerprint / checker spoilers."""
    assert PROMPT_06.is_file()
    text = PROMPT_06.read_text(encoding="utf-8")
    assert text.strip(), "prompt must not be empty"
    assert "poem" in text.lower()
    assert "poem.txt" in text
    assert "artifacts" in text.lower()
    _assert_no_fingerprint_leakage(text)


def test_prompt_07_stamp_no_fingerprint_leakage() -> None:
    """Prompt 07 stamp-the-build + path; no fingerprint leakage."""
    assert PROMPT_07.is_file()
    text = PROMPT_07.read_text(encoding="utf-8")
    assert text.strip(), "prompt must not be empty"
    assert "stamp" in text.lower()
    assert "build" in text.lower()
    assert "stamp.txt" in text
    assert "artifacts" in text.lower()
    _assert_no_fingerprint_leakage(text)


def test_prompt_08_audit_no_fingerprint_leakage() -> None:
    """Prompt 08 audit fixtures listing + path; no fingerprint leakage."""
    assert PROMPT_08.is_file()
    text = PROMPT_08.read_text(encoding="utf-8")
    assert text.strip(), "prompt must not be empty"
    assert "audit" in text.lower()
    assert "fixture" in text.lower()
    assert "agent.txt" in text
    assert "artifacts" in text.lower()
    _assert_no_fingerprint_leakage(text)
