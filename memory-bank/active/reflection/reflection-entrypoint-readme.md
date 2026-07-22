---
task_id: entrypoint-readme
date: 2026-07-22
complexity_level: 3
---

# Reflection: entrypoint-readme

## Summary

Delivered the attended-run driver (`skills/conformance-run/`), build-time sentinel-leakage lint, discretionary summary marks, and operator README — closing DESIGN steps 12–13. Full suite green (168); QA clean.

## Requirements vs Outcome

All milestone requirements landed: operator-only entrypoint loop, lint over `prompts/` + entrypoint, README install → launch → invoke / table reading / re-run / headless footnote, and discretionary marks for steps 6–8. Nothing descoped; nothing added beyond the plan (preflight amendments only).

## Plan Accuracy

The TDD sequence (lint → discretionary summary → skill → README → DESIGN close-out) held without reordering. Challenges that materialized were the ones planned: indent phrase forms (not bare digits), skill vs prompt vocabulary split (`observed` required in the driver), and avoiding judgment words even in innocuous noun phrases (`capability pass` → `capability run`). No surprise dependencies.

## Creative Phase Review

Creative was correctly skipped — no open design choices; namespaced invoke remained a README concern per DESIGN.

## Build & QA Observations

Build was straightforward once the vocabulary split was pinned in preflight. One mechanical gotcha: importlib-loading a `@dataclass` module under Python 3.13 requires registering it in `sys.modules` before `exec_module`. QA found no substantive or trivial fixes.

## Cross-Phase Analysis

Preflight's skill-vocabulary amendment prevented a real build trap (copying prompt leak patterns that ban `observed` onto the driver). Including discretionary summary marks in this milestone (rather than deferring the DESIGN pre-mortem gap again) kept README teaching and summary rendering aligned without a follow-up task.

## Insights

### Technical
- When a driver must *report* observational status, its anti-leakage rules cannot be a copy of the prompt leak catalog — share the sentinel catalog, keep a separate allowlist for reporting vocabulary.
- `importlib.util` + `@dataclass` + `from __future__ import annotations` needs `sys.modules[spec.name] = module` before exec on Python 3.13.

### Process
- Preflight amendments that look pedantic (skill vs prompt vocabulary) are high leverage when the same words are forbidden in one surface and required in another.
