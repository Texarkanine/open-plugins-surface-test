"""Contracts for the conformance-run entrypoint skill, README, and DESIGN close-out."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "conformance-run" / "SKILL.md"
README = ROOT / "README.md"
DESIGN = ROOT / "DESIGN.md"
LINT = ROOT / "scripts" / "lint_leakage.py"
PROMPTS = ROOT / "prompts"

COACHING_BAN = (
    re.compile(r"\bfingerprint\b", re.IGNORECASE),
    re.compile(r"\bsentinel\b", re.IGNORECASE),
    re.compile(r"\bunsupported\b", re.IGNORECASE),
)
# Judgment pass/fail — allow "password" etc. by requiring word boundaries around judgment sense.
JUDGMENT_PASS_FAIL = re.compile(r"\b(pass|fail|passed|failed|passing|failing)\b", re.IGNORECASE)

REQUIRED_OBSERVATIONAL = ("observed", "not observed", "skipped")


def _load_lint_module():
    spec = importlib.util.spec_from_file_location("lint_leakage", LINT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _frontmatter(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match is not None, "missing YAML frontmatter"
    return match.group(1)


def test_entrypoint_skill_frontmatter() -> None:
    """name matches directory; description present; disable-model-invocation true."""
    assert SKILL.is_file()
    text = SKILL.read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert re.search(r"(?m)^name:\s*conformance-run\s*$", fm)
    assert re.search(r"(?m)^description:\s*\S", fm)
    assert re.search(r"(?m)^disable-model-invocation:\s*true\s*$", fm)


def test_entrypoint_skill_driver_shape() -> None:
    """Body orders setup.sh → steps 1–11 (prompt, check, report, next) → summary."""
    text = SKILL.read_text(encoding="utf-8")
    body = text.split("---", 2)[-1]
    assert "scripts/setup.sh" in body or "setup.sh" in body
    assert "check.py --summary" in body or "--summary" in body

    # Each step 1–11 referenced with a matching prompt file pattern and check.py N.
    for step in range(1, 12):
        assert re.search(rf"\bcheck\.py\s+{step}\b", body), f"missing check.py {step}"
        prompt_glob = f"{step:02d}-"
        assert prompt_glob in body or f"prompts/{step:02d}" in body, (
            f"missing prompt reference for step {step}"
        )

    # Operator gate vocabulary.
    assert re.search(r"\bnext\b", body, re.IGNORECASE)

    # Setup appears before the first check; summary after the last step check.
    setup_pos = body.find("setup.sh")
    first_check = body.find("check.py 1")
    last_check = body.find("check.py 11")
    summary_pos = body.find("--summary")
    assert setup_pos != -1 and first_check != -1 and last_check != -1 and summary_pos != -1
    assert setup_pos < first_check < last_check < summary_pos


def test_entrypoint_skill_observational_wording() -> None:
    """Driver uses observed / not observed / skipped; no pass/fail / unsupported judgment."""
    text = SKILL.read_text(encoding="utf-8")
    body = text.split("---", 2)[-1]
    lowered = body.lower()
    for phrase in REQUIRED_OBSERVATIONAL:
        assert phrase in lowered, f"missing observational phrase {phrase!r}"
    for pattern in COACHING_BAN:
        assert pattern.search(body) is None, f"coaching leak: {pattern.pattern}"
    assert JUDGMENT_PASS_FAIL.search(body) is None, "judgment pass/fail language in skill"


def test_entrypoint_skill_no_sentinel_catalog_leakage() -> None:
    """Skill body fails the same sentinel catalog as prompts."""
    assert SKILL.is_file()
    lint = _load_lint_module()
    findings = [f for f in lint.find_leaks(ROOT) if "conformance-run" in str(f.path)]
    assert findings == [], f"entrypoint skill leaked sentinels: {findings}"


def test_prompt_files_exist_for_steps_1_through_11() -> None:
    """Each step 1–11 has a matching prompts/NN-*.md file (driver dependency)."""
    for step in range(1, 12):
        matches = list(PROMPTS.glob(f"{step:02d}-*.md"))
        assert matches, f"missing prompt for step {step}"


def test_readme_has_required_sections() -> None:
    """README covers install, launch, invoke, table reading, re-run, headless footnote."""
    assert README.is_file()
    text = README.read_text(encoding="utf-8")
    lowered = text.lower()

    # Must no longer defer operator instructions to DESIGN-only.
    assert "until then" not in lowered
    assert "land with the entrypoint" not in lowered

    assert re.search(r"(?im)^#+ .*install", text)
    assert re.search(r"(?im)^#+ .*launch", text)
    assert re.search(r"(?im)^#+ .*invoke", text)
    assert "capability" in lowered and ("table" in lowered or "summary" in lowered)
    assert "discretionary" in lowered
    assert "sessionend" in lowered
    assert "re-run" in lowered or "rerun" in lowered
    assert "headless" in lowered or "batch" in lowered

    assert "open-plugins-conformance:conformance-run" in text
    assert ".agents/plugins" in text or ".agents/plugins/" in text
    assert "uv run pytest" in text
    assert "scripts/setup.sh" in text or "setup.sh" in text
    assert "check.py" in text


def test_readme_no_sentinel_catalog_leakage() -> None:
    """README text does not contain probe sentinel catalog strings."""
    lint = _load_lint_module()
    catalog = lint.sentinel_catalog()
    text = README.read_text(encoding="utf-8")
    for label, needle in catalog:
        assert needle not in text, f"README leaked {label}: {needle!r}"


def test_design_steps_12_and_13_delivered() -> None:
    """Implementation Plan treats entrypoint skill and README as delivered, not deferred."""
    text = DESIGN.read_text(encoding="utf-8")
    # Locate the Implementation Plan section and the step 12–13 lines.
    plan_match = re.search(
        r"## Implementation Plan\n(.*?)(?=\n---\n|\n## )",
        text,
        re.DOTALL,
    )
    assert plan_match is not None, "missing Implementation Plan section"
    plan = plan_match.group(1)

    step12 = re.search(r"(?m)^12\.\s+\*\*Entrypoint skill\.\*\*(.*)$", plan)
    step13 = re.search(r"(?m)^13\.\s+\*\*README\.\*\*(.*)$", plan)
    assert step12 is not None, "missing step 12"
    assert step13 is not None, "missing step 13"

    for label, line in (("12", step12.group(0)), ("13", step13.group(0))):
        lowered = line.lower()
        assert "written last" not in lowered, f"step {label} still deferred"
        assert "once the loop" not in lowered, f"step {label} still deferred"
        # Delivered marker: done / delivered / complete (light-touch close-out).
        assert any(
            marker in lowered for marker in ("done", "delivered", "complete")
        ), f"step {label} not marked delivered: {line}"
