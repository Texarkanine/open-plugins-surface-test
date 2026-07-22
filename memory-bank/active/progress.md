# Progress

Deliver entrypoint skill `skills/conformance-run/`, build-time sentinel-leakage lint, and README (install → launch → invoke, how to read the capability table, single-step re-run) — TDD: leakage-lint tests against planted sentinels before entrypoint skill body and README prose.

**Complexity:** Level 3

## 2026-07-21 - COMPLEXITY-ANALYSIS - COMPLETE

* Work completed
    - Checked off completed L4 milestone (LSP open-question resolution)
    - Cleared sub-run ephemeral files; preserved `milestones.md`, `projectbrief.md`, `reflection/`
    - Selected first unchecked L4 milestone (entrypoint skill + leakage lint + README) as classification target
    - Classified as Level 3 (Intermediate Feature)
* Decisions made
    - Decision tree: not a bug fix; not a small self-contained enhancement alone; complete feature spanning entrypoint skill, build-time lint, and operator-facing README without system-wide architectural redesign → L3
    - Preserved L4 `projectbrief.md` and `milestones.md`; created fresh sub-run `progress.md`
* Insights
    - Milestone estimate (L3) matches the decision-tree outcome; this is the final unchecked L4 milestone before capstone archive

## 2026-07-21 - PLAN - COMPLETE

* Work completed
    - Component analysis: `skills/conformance-run/`, `scripts/lint_leakage.py`, README, discretionary `check.py --summary` marks
    - TDD plan ordered: leakage lint → summary marks → skill → README → DESIGN close-out
    - No open questions; creative phase skipped
* Decisions made
    - Entrypoint uses `disable-model-invocation: true` (operator-only)
    - Leakage lint is pytest-gated stdlib script scanning `prompts/` + entrypoint only
    - README stays vendor-neutral (open-plugins install + namespaced invoke); no invented harness CLIs
    - Include discretionary summary marks now (DESIGN pre-mortem gap; required for readable table)
* Insights
    - Indent leaks need phrase patterns, not bare digits; token probes can import check.py constants

## 2026-07-21 - PREFLIGHT - COMPLETE

* Work completed
    - Validated TDD pairs, conventions (`scripts/` + `skills/<name>/SKILL.md`), dependency impact on `test_check.py` summary contracts
    - Amended plan for DESIGN test-before-code and skill vs prompt vocabulary split
    - Wrote `.preflight-status` PASS
* Decisions made
    - No rearchitect; ship path stands
    - Advisory only: adding CI that runs `uv run pytest` is out of this milestone's brief (pytest remains the gate)
* Insights
    - Prompt leak patterns that ban `observed` must not be copied onto the entrypoint skill
