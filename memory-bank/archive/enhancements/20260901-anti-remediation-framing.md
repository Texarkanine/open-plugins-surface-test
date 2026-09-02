---
task_id: anti-remediation-framing
complexity_level: 2
date: 2026-09-01
status: completed
---

# TASK ARCHIVE: Anti-Remediation Framing

## SUMMARY

Added explicit collaborative harness-testing framing and Step 2 anti-remediation guidance to `skills/conformance-run/SKILL.md`. The prompt explains that the exercises test the surrounding harness rather than the driving model, notes that missing expected output or a `not observed` check result is a normal and valid measurement outcome, and directs models to run each check once without editing artifacts after checks run.

## REQUIREMENTS

1. Add framing to `skills/conformance-run/SKILL.md` explaining that the exercises evaluate the harness rather than the driving model.
2. Clarify that missing expected output or a `not observed` result is an acceptable, valid measurement outcome that must not be edited or retried.
3. Apply Orwell's 6 rules for writing and prompt-authoring principles to keep prose concise, active, and direct without filler.
4. Keep Step 2 instructions clean and focused ("Run each check only once. Do not edit artifacts after running a check.") without negative priming (no mention of `scripts/check.py` or reverse-engineering).
5. Ensure all existing test suites and lints pass (`uv run pytest`).

## IMPLEMENTATION

- Updated `skills/conformance-run/SKILL.md`:
  - Opening section: added "These steps test the harness you run in, not you. Do only and exactly what each prompt asks so we can evaluate the harness fairly. If expected output is missing or a check reports **not observed**, that is expected: you are not being evaluated, and we are testing the harness together."
  - Step 2 section: updated constraint to "Run each check only once. Do not edit artifacts after running a check."
- Avoided negative priming by omitting mentions of reverse-engineering or opening checker scripts.

## TESTING

- Ran full pytest suite: `uv run pytest` (182/182 passed).
- Verified structural checks in `tests/test_entrypoint_readme.py` (frontmatter, step loop, observational vocabulary, absence of coaching/judgment terms).
- Verified sentinel leakage prevention in `tests/test_leakage_lint.py`.
- Conducted semantic QA review confirming KISS, DRY, YAGNI, completeness, and process integrity.

## LESSONS LEARNED

- Direct imperative instructions ("Run each check only once. Do not edit artifacts after running a check.") establish firm boundaries without inadvertently priming the model with unwanted ideas.
- Upfront collaborative framing ("we are testing the harness together") addresses the core RLHF reflex to debug and fix non-passing checks across all test steps.

## PROCESS IMPROVEMENTS

- None notable; Level 2 workflow provided appropriate planning, preflight, build, QA, and reflection structure.

## TECHNICAL IMPROVEMENTS

- None needed; prompt instructions remain clean and lightweight without requiring additional enforcement tooling.

## NEXT STEPS

- None.
