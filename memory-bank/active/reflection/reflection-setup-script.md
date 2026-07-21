---
task_id: setup-script
date: 2026-07-21
complexity_level: 2
---

# Reflection: setup-script

## Summary

Delivered `scripts/setup.sh` with pytest contracts locking the DESIGN reset boundary, 4-space recursive fib fixtures, and create-if-absent `run.json`. Full suite green (14 tests).

## Requirements vs Outcome

Matched the milestone and plan: wipe artifacts, regenerate fixtures, never touch observations, harness/model prompts with `unknown`/`unspecified` defaults, OS + uv version in `run.json`. No README expansion (deferred). Added `CONFORMANCE_WORK` as a test/operator work-root seam.

## Plan Accuracy

Plan sequence held. Dual TTY/non-TTY prompt path and `python3` JSON emission were small build-time choices, not plan surprises. Challenges that mattered (over-broad wipe, stdin for prompts) were the ones we planned for.

## Build & QA Observations

Clean TDD cycle (red stub → green). QA only required the techContext note for setup/`CONFORMANCE_WORK`; no code rework.

## Insights

### Technical
- Prefer a work-root env override (`CONFORMANCE_WORK`) over mutating the real `work/` tree in tests — keeps reset-boundary proofs isolated and parallel-safe.

### Process
- Nothing notable — L2 plan → preflight → build → QA flowed without re-leveling.

### Million-Dollar Question

Nothing notable — a single shell script with heredoc fixtures and create-if-absent `run.json` is the right foundational shape; extracting fixture templates would be premature.
