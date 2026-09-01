# Project Brief

## User Story

As a conformance test operator, I want the `conformance-run` driver skill to make clear to the driving model that the exercises evaluate the harness rather than the model, so that driving models follow prompts without inspecting checkers or modifying artifacts after a check runs, while avoiding negative priming (no mention of reverse-engineering or opening `scripts/check.py`).

## Use-Case(s)

### Use-Case 1: Driving an attended conformance run

An operator invokes `/open-plugins-conformance:conformance-run` in a harness (such as Claude Code running Haiku). The driving agent reads the skill instructions, sets up the run, and executes step 1. If step 1 results in `not observed`, the agent reports the observation and waits for `next` without inspecting checkers or modifying artifacts post-check.

## Requirements

1. Update `skills/conformance-run/SKILL.md` to add framing and concise instructions explaining that the exercises evaluate the harness rather than the driving model.
2. Clarify that missing expected output or a `not observed` result is an acceptable, valid measurement outcome that must not be edited or retried.
3. Apply George Orwell's 6 rules for writing (`/style-orwell-6`) and prompt-authoring principles to keep the prose concise, active, and direct without filler.
4. Keep the Step 2 constraint focused and clean ("Run each check only once. Do not edit artifacts after running a check.") without mentioning `scripts/check.py` or reverse-engineering (per operator instruction to avoid negative priming).
5. Ensure all existing unit tests and lints pass (`uv run pytest`).

## Constraints

1. Do not leak sentinels or probe secrets into the skill body (enforced by `tests/test_leakage_lint.py`).
2. Maintain observational language (`observed`, `not observed`, `skipped`) and avoid coaching/judgment words (enforced by `tests/test_entrypoint_readme.py`).
3. Keep the addition concise (a couple of sentences) and placed prominently near the opening of `skills/conformance-run/SKILL.md`.

## Acceptance Criteria

1. `skills/conformance-run/SKILL.md` contains the anti-remediation / harness-testing framing at the top of the skill.
2. Step 2 instructs to run each check only once and not edit artifacts after running a check, with no mention of reverse-engineering.
3. Prose adheres to Orwell's 6 rules and prompt authoring guidelines.
4. `uv run pytest` passes cleanly with zero lint or test failures.
