---
task_id: r4-s1-a1-probes
date: 2026-07-21
complexity_level: 3
---

# Reflection: r4-s1-a1-probes

## Summary

Delivered R4 (description-only sea-poem rule), S1 (`skills/build-stamp/`), and A1 (`agents/listing-auditor.md`) with prompts 06–08 and check.py observers for steps 6–8. Full suite green (93 tests); QA clean.

## Requirements vs Outcome

Plan deliverables matched outcome: shared presence/closing-line helpers, three observers bound to existing registry metadata, three components with fingerprints only in bodies, three prompts without fingerprint leakage. No descoping, no unplanned additions. DESIGN.md and `.plugin/plugin.json` left untouched as planned.

## Plan Accuracy

Sequence (helpers → observers → CLI → components/prompts) held without reordering. Registry metadata for steps 6–8 was already correct — only observer binding was needed. Anticipated challenges (closing-line vs contains, frontmatter mode purity, description strength without token leak) were covered by tests and did not surprise during build. No creative phase was required; that deferral was correct.

## Creative Phase Review

Skipped during plan (approach clear from DESIGN + R1 pattern). Build confirmed that: closing-line equality, substring tokens, and description-only frontmatter needed no design exploration.

## Build & QA Observations

TDD cycle was straightforward — 27 new tests failed on stubs, then passed after a single implementation pass. QA found no substantive issues; only a docstring wording cleanup. Parallel S1/A1 observers were left un-merged intentionally to match named per-probe style.

## Cross-Phase Analysis

Preflight's confirmation that steps 6–8 registry rows already existed removed a class of build risk. Planning fingerprints and frontmatter constraints into the test plan meant QA had little to catch — the leakage and mode-purity gates were load-bearing before components existed.

## Insights

### Technical
- Description-mode probes need two distinct description strengths: enough trigger language for description-matched invocation, and zero fingerprint tokens in that same description field — body-only fingerprints are the safe split.
- Closing-line equality (last non-empty stripped line) is a meaningfully stricter create-path fingerprint than substring contains; mid-file sentinel tests are the load-bearing guard against over-claiming.

### Process
- When registry metadata lands ahead of observers (stub rows), the next milestone's plan can treat binding as a one-line wire rather than a schema design step — worth checking registry readiness in preflight for similar slices.
