---
task_id: r1-e2e
date: 2026-07-21
complexity_level: 2
---

# Reflection: r1-e2e

## Summary

Delivered the first probe vertical slice: Scots-flag codepoint checker wired to step 1, `rules/r1-global-scots.mdc`, and `prompts/01-r1-cats.md`. Full suite 40 green; QA clean.

## Requirements vs Outcome

Matched the milestone and plan: pure `contains_scots_flag`, `observe_r1_scots` over `work/artifacts/cats.md`, alwaysApply rule with live tag-sequence demand, prompt that provokes `cats.md` without fingerprint leakage. Nothing descoped; nothing added beyond the planned helper split from preflight.

## Plan Accuracy

Sequence held (helper/observer → harness contract → rule/prompt). Challenges that mattered (partial-sequence false positives, stub-detail drift, leakage) were the ones planned. No surprises that forced reordering.

## Build & QA Observations

Clean TDD cycles; red/green behaved as expected. QA found only a style nit (`del step` → `_step`). No rework loop.

## Insights

### Technical
- Embedding the live Scotland flag tag sequence in the rule (and asserting its absence from the prompt) makes the no-leakage invariant enforceable without waiting for the later build-time sentinel lint.

### Process
- Nothing notable — L2 plan → preflight → build → QA without creative phase was the right weight for a DESIGN-specified first probe.

### Million-Dollar Question

Same shape we built: a pure fingerprint predicate plus a thin observer registered on `STEP_REGISTRY[1]`, with demanded behavior only in `rules/` and provocation only in `prompts/`. Foundational from day one would not have changed the R1 surface.
