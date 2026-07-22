#!/usr/bin/env python3
"""Build-time sentinel-leakage scanner for prompts and the entrypoint skill.

Scans ``prompts/`` and ``skills/conformance-run/`` for probe sentinel strings
(tokens, Scots flag, indent-width phrases, ``lsp.launched``). Probe components
themselves may contain sentinels; this lint does not scan them.

Exit codes:
  0 — no findings
  1 — one or more leaks, or usage/infrastructure error
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Finding:
    """One sentinel occurrence in a scanned file."""

    path: Path
    line: int
    needle: str
    label: str


def _load_check_module():
    """Load ``scripts/check.py`` for shared sentinel constants."""
    check_path = PLUGIN_ROOT / "scripts" / "check.py"
    spec = importlib.util.spec_from_file_location("check_harness_for_lint", check_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {check_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sentinel_catalog() -> list[tuple[str, str]]:
    """Return ``(label, needle)`` pairs the scanner looks for.

    Token needles are imported from ``check.py`` where possible so the catalog
    cannot silently drift from live probe fingerprints.
    """
    check = _load_check_module()
    return [
        ("SCOTS_FLAG", check.SCOTS_FLAG),
        ("SEA_POEM_SENTINEL", check.SEA_POEM_SENTINEL),
        ("BUILD_STAMP_TOKEN", check.BUILD_STAMP_TOKEN),
        ("LISTING_AUDITOR_TOKEN", check.LISTING_AUDITOR_TOKEN),
        ("MCP_OBSERVED_PREFIX", "MCP-OBSERVED"),
        ("INDENT_7_HYPHEN", "7-space"),
        ("INDENT_7_SPACES", "7 spaces"),
        ("INDENT_5_HYPHEN", "5-space"),
        ("INDENT_5_SPACES", "5 spaces"),
        ("LSP_LAUNCHED", "lsp.launched"),
    ]


def scan_roots(root: Path) -> list[Path]:
    """Return files under ``prompts/`` and ``skills/conformance-run/`` to scan."""
    roots = [root / "prompts", root / "skills" / "conformance-run"]
    files: list[Path] = []
    for base in roots:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file():
                files.append(path)
    return files


def find_leaks(root: Path) -> list[Finding]:
    """Scan ``root`` for sentinel leakage; return findings (possibly empty)."""
    catalog = sentinel_catalog()
    findings: list[Finding] = []
    for path in scan_roots(root):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise RuntimeError(f"unable to read {path}: {exc}") from exc
        for line_no, line in enumerate(text.splitlines(), start=1):
            for label, needle in catalog:
                if needle in line:
                    findings.append(
                        Finding(path=path, line=line_no, needle=needle, label=label)
                    )
    return findings


def main(argv: list[str] | None = None) -> int:
    """CLI entry: scan a root (default: plugin root); print findings; exit on leaks."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) > 1:
        print(
            "usage: lint_leakage.py [root]\n"
            "  root   directory containing prompts/ and skills/ (default: plugin root)",
            file=sys.stderr,
        )
        return 1

    root = Path(args[0]).resolve() if args else PLUGIN_ROOT
    if not root.is_dir():
        print(f"error: root is not a directory: {root}", file=sys.stderr)
        return 1

    try:
        findings = find_leaks(root)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not findings:
        return 0

    for finding in findings:
        print(f"{finding.path}:{finding.line}: {finding.label} ({finding.needle!r})")
    print(f"error: {len(findings)} sentinel leak(s) in prompts/entrypoint", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
