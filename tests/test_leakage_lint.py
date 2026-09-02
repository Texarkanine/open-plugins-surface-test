"""Build-time sentinel-leakage lint for prompts/ and the entrypoint skill."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINT = ROOT / "scripts" / "lint_leakage.py"
CHECK = ROOT / "scripts" / "check.py"

# Owning component files that must still contain each catalog needle.
OWNING_COMPONENTS: list[tuple[str, Path]] = [
    ("SCOTS_FLAG", ROOT / "rules" / "r1-global-scots.mdc"),
    ("SEA_POEM_SENTINEL", ROOT / "rules" / "r4-sea-poem.mdc"),
    ("BUILD_STAMP_TOKEN", ROOT / "skills" / "build-stamp" / "SKILL.md"),
    ("LISTING_AUDITOR_TOKEN", ROOT / "agents" / "listing-auditor.md"),
    ("MCP_OBSERVED_PREFIX", ROOT / "servers" / "probe_mcp.py"),
    ("INDENT_7_SPACES", ROOT / "rules" / "r2-js-indent.mdc"),
    ("INDENT_5_SPACES", ROOT / "rules" / "r3-py-indent.mdc"),
    ("LSP_LAUNCHED", ROOT / "servers" / "probe_lsp.py"),
]


def _load_lint_module():
    spec = importlib.util.spec_from_file_location("lint_leakage", LINT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_check_module():
    spec = importlib.util.spec_from_file_location("check_harness", CHECK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_tree(
    root: Path,
    *,
    prompt_body: str = "Create a file.\n",
    skill_body: str = "Run setup then step through prompts.\n",
) -> None:
    prompts = root / "prompts"
    skill = root / "skills" / "conformance-run"
    prompts.mkdir(parents=True)
    skill.mkdir(parents=True)
    (prompts / "01-example.md").write_text(prompt_body, encoding="utf-8")
    (skill / "SKILL.md").write_text(skill_body, encoding="utf-8")
    # Out-of-scope locations that may contain sentinels without failing the lint.
    rules = root / "rules"
    rules.mkdir(parents=True)
    (rules / "probe.mdc").write_text("BUILD-STAMP-OBSERVED\n", encoding="utf-8")
    stamp = root / "skills" / "build-stamp"
    stamp.mkdir(parents=True)
    (stamp / "SKILL.md").write_text("BUILD-STAMP-OBSERVED\n", encoding="utf-8")


def test_catalog_covers_probe_sentinels() -> None:
    """Scanner catalog includes check.py tokens, MCP prefix, indent phrases, lsp.launched."""
    lint = _load_lint_module()
    check = _load_check_module()
    catalog = {label: needle for label, needle in lint.sentinel_catalog()}

    assert catalog["SCOTS_FLAG"] == check.SCOTS_FLAG
    assert catalog["SEA_POEM_SENTINEL"] == check.SEA_POEM_SENTINEL
    assert catalog["BUILD_STAMP_TOKEN"] == check.BUILD_STAMP_TOKEN
    assert catalog["LISTING_AUDITOR_TOKEN"] == check.LISTING_AUDITOR_TOKEN
    assert catalog["MCP_OBSERVED_PREFIX"] == "MCP-OBSERVED"
    assert catalog["LSP_LAUNCHED"] == "lsp.launched"

    needles_lower = {needle.casefold() for _, needle in lint.sentinel_catalog()}
    for phrase in ("7-space", "7 spaces", "5-space", "5 spaces"):
        assert phrase.casefold() in needles_lower, f"missing indent phrase {phrase!r}"


def test_catalog_tokens_still_live_in_owning_components() -> None:
    """Each catalog needle still appears in its owning probe component (no drift)."""
    lint = _load_lint_module()
    catalog = {label: needle for label, needle in lint.sentinel_catalog()}
    for label, owner in OWNING_COMPONENTS:
        assert owner.is_file(), f"missing owning component for {label}: {owner}"
        text = owner.read_text(encoding="utf-8")
        needle = catalog[label]
        assert needle in text, f"{label} needle {needle!r} missing from {owner}"


def test_clean_repo_tree_has_no_findings() -> None:
    """Current prompts/ + entrypoint skill (if present) produce no leak findings."""
    lint = _load_lint_module()
    findings = lint.find_leaks(ROOT)
    assert findings == [], f"unexpected leaks: {findings}"


def test_planted_prompt_leak_fails_naming_file_and_sentinel(tmp_path: Path) -> None:
    """Prompt containing a sentinel → findings name the file and sentinel label."""
    lint = _load_lint_module()
    _write_tree(tmp_path, prompt_body="Please emit SEA-POEM-OBSERVED.\n")
    findings = lint.find_leaks(tmp_path)
    assert findings, "expected at least one finding"
    assert any(
        f.label == "SEA_POEM_SENTINEL" and f.path.name == "01-example.md" for f in findings
    )


def test_planted_skill_leak_fails(tmp_path: Path) -> None:
    """Entrypoint skill body containing a sentinel → lint fails."""
    lint = _load_lint_module()
    _write_tree(tmp_path, skill_body="Write BUILD-STAMP-OBSERVED to the artifact.\n")
    findings = lint.find_leaks(tmp_path)
    assert findings, "expected at least one finding"
    assert any(
        f.label == "BUILD_STAMP_TOKEN" and "conformance-run" in str(f.path)
        for f in findings
    )


def test_out_of_scope_probe_components_ignored(tmp_path: Path) -> None:
    """Sentinels inside rules/ or skills/build-stamp/ do not fail the lint."""
    lint = _load_lint_module()
    _write_tree(tmp_path)
    findings = lint.find_leaks(tmp_path)
    assert findings == []


def test_indent_phrase_variants_detected(tmp_path: Path) -> None:
    """Digit-led indent phrases (7-space / 7 spaces / 5-space / 5 spaces) are leaks."""
    lint = _load_lint_module()
    phrases = ("7-space", "7 spaces", "5-space", "5 spaces")
    for phrase in phrases:
        tree = tmp_path / phrase.replace(" ", "_")
        _write_tree(tree, prompt_body=f"Use {phrase} indentation.\n")
        findings = lint.find_leaks(tree)
        assert findings, f"expected leak for {phrase!r}"
        assert any("INDENT_" in f.label for f in findings), findings


def test_cli_exit_nonzero_on_findings(tmp_path: Path) -> None:
    """CLI exits non-zero and prints file:line when a leak is planted."""
    _write_tree(tmp_path, prompt_body="token MCP-OBSERVED-cats here\n")
    result = subprocess.run(
        [sys.executable, str(LINT), str(tmp_path)],
        text=True,
        capture_output=True,
        cwd=str(ROOT),
        check=False,
    )
    assert result.returncode != 0
    combined = f"{result.stdout}\n{result.stderr}"
    assert "01-example.md" in combined
    assert "MCP_OBSERVED_PREFIX" in combined or "MCP-OBSERVED" in combined


def test_cli_exit_zero_when_clean(tmp_path: Path) -> None:
    """CLI exits 0 on a clean temp tree."""
    _write_tree(tmp_path)
    result = subprocess.run(
        [sys.executable, str(LINT), str(tmp_path)],
        text=True,
        capture_output=True,
        cwd=str(ROOT),
        check=False,
    )
    assert result.returncode == 0
