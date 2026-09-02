"""Contracts for R2/R3 indent checkers, rules, and prompts."""

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
RULE_R2 = ROOT / "rules" / "r2-js-indent.mdc"
RULE_R3 = ROOT / "rules" / "r3-py-indent.mdc"
PROMPT_02 = ROOT / "prompts" / "02-r2-js-create.md"
PROMPT_03 = ROOT / "prompts" / "03-r2-js-edit.md"
PROMPT_04 = ROOT / "prompts" / "04-r3-py-create.md"
PROMPT_05 = ROOT / "prompts" / "05-r3-py-edit.md"

JS7_NESTED = (
    "function reverse(s) {\n"
    "       if (!s) {\n"
    "              return '';\n"
    "       }\n"
    "       return s.split('').reverse().join('');\n"
    "}\n"
)
PY5_NESTED = (
    "def strrev(s):\n"
    "     if not s:\n"
    "          return ''\n"
    "     return s[::-1]\n"
)
JS4 = "function fib(n) {\n    if (n < 2) {\n        return n;\n    }\n    return fib(n - 1) + fib(n - 2);\n}\n"
PY4 = "def fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\n"

LEAK_PATTERNS = (
    re.compile(r"7[-\s]?space", re.IGNORECASE),
    re.compile(r"5[-\s]?space", re.IGNORECASE),
    re.compile(r"\bseven\b", re.IGNORECASE),
    re.compile(r"\bfive\b", re.IGNORECASE),
    re.compile(r"indent", re.IGNORECASE),
    re.compile(r"\bspaces?\b", re.IGNORECASE),
    re.compile(r"scottish", re.IGNORECASE),
    re.compile(r"flag", re.IGNORECASE),
    re.compile(r"check\.py", re.IGNORECASE),
    re.compile(r"observed", re.IGNORECASE),
)
# Bare width numerals after stripping the "# Step N" title line.
BARE_WIDTH = re.compile(r"[^0-9]([57])[^0-9]|^[57][^0-9]|[^0-9][57]$|^[57]$")


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


def _assert_no_prompt_leakage(text: str) -> None:
    for pattern in LEAK_PATTERNS:
        assert pattern.search(text) is None, f"prompt leaked: {pattern.pattern}"
    body = re.sub(r"(?m)^#\s*Step\s+\d+\s*$", "", text)
    assert BARE_WIDTH.search(body) is None, "prompt leaked bare width numeral 5 or 7"


@pytest.fixture
def work(tmp_path: Path) -> Path:
    work_dir = tmp_path / "work"
    _write_run_json(work_dir)
    return work_dir


# --- indent width extraction ---


def test_indent_widths_empty_and_unindented() -> None:
    """No indented non-blank lines → empty width set."""
    check = _load_check_module()
    assert check.indent_widths("") == set()
    assert check.indent_widths("hello\nworld\n") == set()


def test_indent_widths_skips_blank_lines() -> None:
    """Blank lines do not contribute indent widths."""
    check = _load_check_module()
    source = "def f():\n       x = 1\n\n       y = 2\n"
    assert check.indent_widths(source) == {7}


def test_indent_widths_leading_spaces_only() -> None:
    """Count leading ASCII spaces; collect positive widths."""
    check = _load_check_module()
    source = "function f() {\n       a();\n              b();\n}\n"
    assert check.indent_widths(source) == {7, 14}


def test_indent_widths_leading_tab_is_marker() -> None:
    """Leading tab yields non-compliant marker (-1), not a positive width."""
    check = _load_check_module()
    source = "def f():\n\tx = 1\n"
    assert check.indent_widths(source) == {-1}


# --- multiples-of-N predicate ---


def test_indent_multiples_of_n_accepts_compliant() -> None:
    """All positive widths divisible by N, no tab marker → True."""
    check = _load_check_module()
    assert check.indent_multiples_of({7, 14}, 7) is True
    assert check.indent_multiples_of({5, 10}, 5) is True


def test_indent_multiples_of_n_rejects_empty_widths() -> None:
    """Empty widths → False (nothing to credit)."""
    check = _load_check_module()
    assert check.indent_multiples_of(set(), 7) is False
    assert check.indent_multiples_of(set(), 5) is False


def test_indent_multiples_of_n_rejects_wrong_base_and_tabs() -> None:
    """Non-multiples or tab marker → False."""
    check = _load_check_module()
    assert check.indent_multiples_of({4}, 7) is False
    assert check.indent_multiples_of({7, 8}, 7) is False
    assert check.indent_multiples_of({-1}, 7) is False
    assert check.indent_multiples_of({7, -1}, 7) is False


def test_indent_multiples_cross_n_negative() -> None:
    """7-only widths fail N=5; 5-only widths fail N=7."""
    check = _load_check_module()
    assert check.indent_multiples_of({7, 14}, 5) is False
    assert check.indent_multiples_of({5, 10}, 7) is False


# --- detail formatting ---


def test_indent_widths_detail_format() -> None:
    """Detail uses DESIGN shape: indent widths seen: [sorted unique positives]."""
    check = _load_check_module()
    assert check.format_indent_widths_detail({14, 7}) == "indent widths seen: [7, 14]"
    assert check.format_indent_widths_detail(set()) == "indent widths seen: []"
    assert check.format_indent_widths_detail({-1, 7}) == "indent widths seen: [7]"


# --- file_modified ---


def test_file_modified_missing_artifact(work: Path) -> None:
    """Missing artifact → False."""
    check = _load_check_module()
    fixture = work / "fixtures" / "fib.js"
    fixture.parent.mkdir(parents=True)
    fixture.write_text(JS4, encoding="utf-8")
    assert check.file_modified(work / "artifacts" / "fib.js", fixture) is False


def test_file_modified_equal_and_different(work: Path) -> None:
    """Equal text → False; different text → True."""
    check = _load_check_module()
    fixture = work / "fixtures" / "fib.js"
    artifact = work / "artifacts" / "fib.js"
    fixture.parent.mkdir(parents=True)
    artifact.parent.mkdir(parents=True)
    fixture.write_text(JS4, encoding="utf-8")
    artifact.write_text(JS4, encoding="utf-8")
    assert check.file_modified(artifact, fixture) is False
    artifact.write_text(JS7_NESTED, encoding="utf-8")
    assert check.file_modified(artifact, fixture) is True


# --- create observers ---


def test_observe_js_create_missing_and_noncompliant(work: Path) -> None:
    """Step 2: missing → false; non-compliant indent → false with widths detail."""
    check = _load_check_module()
    missing = check.observe_r2_js_create(2, work)
    assert missing["observed"] is False
    assert "reverse.js" in missing["detail"].lower()

    artifact = work / "artifacts" / "reverse.js"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(JS4, encoding="utf-8")
    bad = check.observe_r2_js_create(2, work)
    assert bad["observed"] is False
    assert "indent widths seen:" in bad["detail"]
    assert "4" in bad["detail"]


def test_observe_js_create_compliant(work: Path) -> None:
    """Step 2: multiples of 7 → observed true."""
    check = _load_check_module()
    artifact = work / "artifacts" / "reverse.js"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(JS7_NESTED, encoding="utf-8")
    result = check.observe_r2_js_create(2, work)
    assert result["observed"] is True
    assert "indent widths seen:" in result["detail"]
    assert "7" in result["detail"]


def test_observe_py_create_compliant_and_cross_n(work: Path) -> None:
    """Step 4: multiples of 5 observed; 7-only not observed for Python."""
    check = _load_check_module()
    artifact = work / "artifacts" / "strrev.py"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(PY5_NESTED, encoding="utf-8")
    good = check.observe_r3_py_create(4, work)
    assert good["observed"] is True
    assert "5" in good["detail"]

    artifact.write_text(
        "def strrev(s):\n       return s[::-1]\n",
        encoding="utf-8",
    )
    cross = check.observe_r3_py_create(4, work)
    assert cross["observed"] is False
    assert "indent widths seen:" in cross["detail"]


# --- edit observers ---


def test_observe_js_edit_unmodified_fixture(work: Path) -> None:
    """Step 3: artifact equals fixture → file_modified false, not observed."""
    check = _load_check_module()
    fixture = work / "fixtures" / "fib.js"
    artifact = work / "artifacts" / "fib.js"
    fixture.parent.mkdir(parents=True)
    artifact.parent.mkdir(parents=True)
    fixture.write_text(JS4, encoding="utf-8")
    artifact.write_text(JS4, encoding="utf-8")
    result = check.observe_r2_js_edit(3, work)
    assert result["observed"] is False
    assert "file_modified: false" in result["detail"]
    assert "indent widths seen:" in result["detail"]


def test_observe_js_edit_modified_compliant(work: Path) -> None:
    """Step 3: differs + multiples of 7 → observed; detail has both dimensions."""
    check = _load_check_module()
    fixture = work / "fixtures" / "fib.js"
    artifact = work / "artifacts" / "fib.js"
    fixture.parent.mkdir(parents=True)
    artifact.parent.mkdir(parents=True)
    fixture.write_text(JS4, encoding="utf-8")
    artifact.write_text(
        "function fib(n) {\n"
        "       let a = 0, b = 1;\n"
        "       for (let i = 0; i < n; i++) {\n"
        "              [a, b] = [b, a + b];\n"
        "       }\n"
        "       return a;\n"
        "}\n",
        encoding="utf-8",
    )
    result = check.observe_r2_js_edit(3, work)
    assert result["observed"] is True
    assert "file_modified: true" in result["detail"]
    assert "indent widths seen:" in result["detail"]


def test_observe_py_edit_modified_noncompliant(work: Path) -> None:
    """Step 5: differs but wrong indent → not observed; both dimensions in detail."""
    check = _load_check_module()
    fixture = work / "fixtures" / "fib.py"
    artifact = work / "artifacts" / "fib.py"
    fixture.parent.mkdir(parents=True)
    artifact.parent.mkdir(parents=True)
    fixture.write_text(PY4, encoding="utf-8")
    artifact.write_text(
        "def fib(n):\n"
        "    a, b = 0, 1\n"
        "    for _ in range(n):\n"
        "        a, b = b, a + b\n"
        "    return a\n",
        encoding="utf-8",
    )
    result = check.observe_r3_py_edit(5, work)
    assert result["observed"] is False
    assert "file_modified: true" in result["detail"]
    assert "indent widths seen:" in result["detail"]


# --- registry / CLI ---


def test_registry_modes_and_observers_wired() -> None:
    """Steps 2–3 mode alwaysApply; 4–5 globs; observers not stubs."""
    check = _load_check_module()
    assert check.STEP_REGISTRY[2]["mode"] == "alwaysApply"
    assert check.STEP_REGISTRY[3]["mode"] == "alwaysApply"
    assert check.STEP_REGISTRY[4]["mode"] == "globs"
    assert check.STEP_REGISTRY[5]["mode"] == "globs"
    assert "alwaysApply+globs" not in {
        check.STEP_REGISTRY[n]["mode"] for n in range(1, 12)
    }
    assert check.STEP_REGISTRY[2]["observe"] is check.observe_r2_js_create
    assert check.STEP_REGISTRY[3]["observe"] is check.observe_r2_js_edit
    assert check.STEP_REGISTRY[4]["observe"] is check.observe_r3_py_create
    assert check.STEP_REGISTRY[5]["observe"] is check.observe_r3_py_edit


def test_check_cli_step2_observed(work: Path) -> None:
    """CLI step 2 with compliant reverse.js → observed JSONL alwaysApply."""
    artifact = work / "artifacts" / "reverse.js"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(JS7_NESTED, encoding="utf-8")
    result = _run_check(work, ["2"])
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
    assert record["step"] == 2
    assert record["probe"] == "r2-js-indent"
    assert record["mode"] == "alwaysApply"
    assert record["path"] == "create"
    assert record["observed"] is True
    assert "indent widths seen:" in record["detail"]


def test_check_cli_step3_unmodified_exit_zero(work: Path) -> None:
    """CLI step 3 with fixture copy → not observed, exit 0, file_modified false."""
    fixture = work / "fixtures" / "fib.js"
    artifact = work / "artifacts" / "fib.js"
    fixture.parent.mkdir(parents=True)
    artifact.parent.mkdir(parents=True)
    fixture.write_text(JS4, encoding="utf-8")
    artifact.write_text(JS4, encoding="utf-8")
    result = _run_check(work, ["3"])
    assert result.returncode == 0
    assert "not observed" in result.stdout.lower()
    record = json.loads(
        (work / "observations" / "run.jsonl").read_text(encoding="utf-8").strip()
    )
    assert record["step"] == 3
    assert record["mode"] == "alwaysApply"
    assert record["observed"] is False
    assert "file_modified: false" in record["detail"]


# --- rules ---


def test_rule_r2_always_apply_no_globs_demands_seven() -> None:
    """R2: alwaysApply true, no globs key, demands 7-space JS indent."""
    assert RULE_R2.is_file()
    text = RULE_R2.read_text(encoding="utf-8")
    assert "alwaysApply: true" in text or "alwaysApply:true" in text
    assert "globs:" not in text
    assert re.search(r"\b7[-\s]?space", text, re.IGNORECASE) or "7 space" in text.lower()
    assert "javascript" in text.lower() or ".js" in text.lower() or "js" in text.lower()
    assert "scottish" not in text.lower()
    assert "🏴" not in text and "1f3f4" not in text.lower()


def test_rule_r3_globs_only_demands_five() -> None:
    """R3: globs **/*.py, no alwaysApply true, demands 5-space Python indent."""
    assert RULE_R3.is_file()
    text = RULE_R3.read_text(encoding="utf-8")
    assert "globs:" in text
    assert "**/*.py" in text
    assert "alwaysApply: true" not in text and "alwaysApply:true" not in text
    assert re.search(r"\b5[-\s]?space", text, re.IGNORECASE) or "5 space" in text.lower()
    assert "python" in text.lower() or ".py" in text.lower()


# --- prompts ---


def test_prompt_02_create_js_no_leakage() -> None:
    """Prompt 02 names reverse.js; no 7/5/indent/spaces style leakage."""
    assert PROMPT_02.is_file()
    text = PROMPT_02.read_text(encoding="utf-8")
    assert "reverse.js" in text
    assert "artifacts" in text.lower()
    _assert_no_prompt_leakage(text)


def test_prompt_03_edit_js_no_leakage() -> None:
    """Prompt 03: fib.js fixture → artifacts/fib.js; no indent leakage."""
    assert PROMPT_03.is_file()
    text = PROMPT_03.read_text(encoding="utf-8")
    assert "fib.js" in text
    assert "fixtures" in text.lower()
    assert "artifacts" in text.lower()
    assert "iterative" in text.lower()
    _assert_no_prompt_leakage(text)


def test_prompt_04_create_py_no_leakage() -> None:
    """Prompt 04 names strrev.py; no indent leakage."""
    assert PROMPT_04.is_file()
    text = PROMPT_04.read_text(encoding="utf-8")
    assert "strrev.py" in text
    assert "artifacts" in text.lower()
    _assert_no_prompt_leakage(text)


def test_prompt_05_edit_py_no_leakage() -> None:
    """Prompt 05: fib.py fixture → artifacts/fib.py; no indent leakage."""
    assert PROMPT_05.is_file()
    text = PROMPT_05.read_text(encoding="utf-8")
    assert "fib.py" in text
    assert "fixtures" in text.lower()
    assert "artifacts" in text.lower()
    assert "iterative" in text.lower()
    _assert_no_prompt_leakage(text)
