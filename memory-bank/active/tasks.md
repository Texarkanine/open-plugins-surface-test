# Task: anti-remediation-framing

* Task ID: anti-remediation-framing
* Complexity: Level 2
* Type: simple enhancement

Add harness-testing and anti-remediation framing to `skills/conformance-run/SKILL.md` to prevent driving models from inspecting checker scripts or altering artifacts after checks run.

## Test Plan (TDD)

### Behaviors to Verify

No new executable behavior. (Prose/policy enhancement in agent skill instructions; verified against existing leakage lints and observational vocabulary tests in `tests/test_entrypoint_readme.py` and `tests/test_leakage_lint.py`).

### Test Infrastructure

- Framework: pytest (`uv run pytest`)
- Test location: `tests/`
- Conventions: PEP 8 / pytest test functions asserting structural properties and absence of leaks
- New test files: none (change-detectors prohibited on prose/policy artifacts)

## Implementation Plan

### 1. Update conformance-run entrypoint skill — prose/policy

- Files: `skills/conformance-run/SKILL.md`
- No tests: prose/policy artifact

1. [x] Re-read `skills/conformance-run/SKILL.md` and check opening structure.
2. [x] Add the harness-testing framing and anti-remediation instruction to the opening section and step 2 guidance using Orwell's 6 rules and prompt authoring guidelines.
3. [x] Run `uv run pytest` to ensure existing structural gates, leakage lints, and observational vocabulary checks pass cleanly.

## Technology Validation

No new technology - validation not required

## Dependencies

- Existing `tests/test_entrypoint_readme.py` and `tests/test_leakage_lint.py` test suite

## Challenges & Mitigations

- [Coaching / judgment word leak]: Ensure the added prose avoids banned tokens (`pass`, `fail`, `fingerprint`, `sentinel`, `unsupported`) verified by `tests/test_entrypoint_readme.py`.
- [Over-complicating prompt]: Strictly apply Orwell's 6 rules to keep the instructions concise (2-3 sentences), active, and direct.

## Pre-Mortem

- [Model still cheats because instructions are buried in a long document]: Place the framing right at the top of `SKILL.md` in the opening section and repeat the negative constraint in Step 2.

## Status

- [x] Initialization complete
- [x] Test planning complete (TDD)
- [x] Implementation plan complete
- [x] Technology validation complete
- [x] Pre-Mortem complete
- [x] Preflight
- [x] Build
- [ ] QA
