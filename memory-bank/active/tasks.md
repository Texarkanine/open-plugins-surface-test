# Task: R1 end-to-end (alwaysApply Scots flag)

* Task ID: r1-e2e
* Complexity: Level 2
* Type: simple enhancement

First probe vertical slice: wire step 1 from stub observer to a real Scottish-flag codepoint checker over `work/artifacts/cats.md`, add `rules/r1-global-scots.mdc` (`alwaysApply: true`, no globs) that demands the flag, and add `prompts/01-*.md` that provokes writing `cats.md` without leaking the fingerprint. Validates the probe → prompt → artifact → check loop.

Pinned fingerprint (DESIGN Challenges): full Scotland flag tag sequence — U+1F3F4 U+E0067 U+E0062 U+E0073 U+E0063 U+E0074 U+E007F — matched in Python by substring/codepoint containment, never shell `grep`.

## Test Plan (TDD)

### Behaviors to Verify

- [Pure helper]: `contains_scots_flag(text)` is True iff the full 7-codepoint sequence is a substring; False for empty, ASCII-only, black-flag-only, and incomplete tag prefixes
- [Flag present]: `work/artifacts/cats.md` contains the full sequence → observer returns `observed: true` with a detail noting presence
- [Flag absent]: artifact exists but lacks the full sequence → `observed: false`, exit 0, observational wording
- [Missing artifact]: no `cats.md` → `observed: false` (not infra failure), exit 0
- [Partial sequence]: artifact contains only U+1F3F4 (black flag) or an incomplete tag prefix → `observed: false`
- [Harness wiring]: `check.py 1` with planted flag artifact appends JSONL with step-1 registry metadata and `observed: true`
- [Harness empty work]: `check.py 1` with no artifact still exits 0; update `test_step_append_shape` away from stub detail `"probe checker not implemented"`
- [Rule present]: `rules/r1-global-scots.mdc` exists with `alwaysApply: true` and no `globs`; body demands the Scotland flag when writing about cats / `cats.md`
- [Prompt present]: `prompts/01-*.md` instructs writing `cats.md` (domestic felines, ≤2 paragraphs) under `work/artifacts/`
- [No leakage]: prompt body must not contain the flag sequence, "Scottish flag", or equivalent fingerprint spoilers; rule body must contain the demand
- [Regression]: existing `tests/test_check.py` contracts for other steps/summary/infra remain green

### Test Infrastructure

- Framework: pytest via `uv run pytest` (`pyproject.toml`)
- Test location: `tests/`
- Conventions: `test_*.py`; behavioral contracts; subprocess CLI where appropriate; load `check.py` via `importlib` for callable/monkeypatch cases; `CONFORMANCE_WORK` temp work dirs
- New test files: `tests/test_r1_scots.py` (flag checker + rule/prompt presence/leakage). Update `tests/test_check.py` only where step-1 stub assumptions break

## Implementation Plan

1. **Red — flag helper + observer contracts**
   - Files: `tests/test_r1_scots.py` (new)
   - Changes: tests for pure `contains_scots_flag` (present / empty / black-flag-only / incomplete prefix) and for `observe_r1_scots` (present / absent / missing file); pin expected codepoints in tests until the constant is exported from `check.py`

2. **Green — implement helper + step-1 observer**
   - Files: `scripts/check.py`
   - Changes: add `SCOTS_FLAG` constant, `contains_scots_flag(text: str) -> bool`, and `observe_r1_scots(step, work) -> ObservationResult` that reads `work/artifacts/cats.md` as UTF-8 and uses the helper; wire `STEP_REGISTRY[1]` via `_entry(..., observe=observe_r1_scots)`; leave steps 2–11 on `observe_stub`

3. **Red/green — harness step-1 contract update**
   - Files: `tests/test_check.py`
   - Changes: rewrite `test_step_append_shape` (and any stub-detail assertions) for real observer semantics when artifact missing; add/adjust CLI case with planted flag → `observed: true`

4. **Red — rule + prompt presence and leakage**
   - Files: `tests/test_r1_scots.py`
   - Changes: assert rule frontmatter/mode and fingerprint demand; assert prompt path/content provoke `cats.md` without fingerprint leakage

5. **Green — rule and prompt**
   - Files: `rules/r1-global-scots.mdc`, `prompts/01-r1-cats.md` (name pinned: `01-r1-cats.md`)
   - Changes: rule with `alwaysApply: true`, no globs, demand Scotland flag in `cats.md` content; prompt asks for ≤2-paragraph feline praise saved as `work/artifacts/cats.md` with no flag mention

6. **Full suite**
   - Files: all under `tests/`
   - Changes: run `uv run pytest`; fix only regressions caused by this milestone

7. **Docs**
   - Files: `scripts/check.py` module docstring (brief)
   - Changes: note step 1 has a real observer; README install/invoke deferred to entrypoint/README milestone

## Technology Validation

No new technology - validation not required

## Dependencies

- Existing: `scripts/check.py` `STEP_REGISTRY` / `ObservationResult` / observe-not-judge CLI
- Existing: `.plugin/plugin.json` already declares `"rules": "./rules/"`
- Design authority: `DESIGN.md` probe matrix row 1 + Challenges (tag-sequence matching)
- Out of scope: entrypoint skill, summary README, R2–R11 checkers, sentinel-leakage lint framework (later milestone)

## Challenges & Mitigations

- [Tag-sequence false negatives]: Matching must require the full 7 codepoints, not "🏴" alone — pin constant and partial-sequence test
- [Stub contract drift]: `test_step_append_shape` hard-codes stub detail — update in the same build as wiring the observer
- [Expectation leakage]: Prompt must not mention the flag; focused leakage assertions in `test_r1_scots.py` (full build-time lint is a later milestone)
- [Artifact path ambiguity]: Pin `work/artifacts/cats.md` per DESIGN runtime diagram ("agent writes into work/artifacts/")

## Pre-Mortem

- [Checker accepts black flag only → false positives]: already covered by partial-sequence Challenge/test
- [Prompt spoils the probe → suite measures instruction-following]: already covered by leakage Challenge/tests
- [Wrong work-relative path → always not observed in real runs]: pin `artifacts/cats.md` in plan, tests, rule, and prompt wording
- [Over-scope into R2/indent or leakage-lint framework]: out-of-scope list; stop at step-1 wiring + rule + prompt

## Status

- [x] Initialization complete
- [x] Test planning complete (TDD)
- [x] Implementation plan complete
- [x] Technology validation complete
- [x] Pre-Mortem complete
- [x] Preflight
- [x] Build
- [x] QA

## Preflight Amendments

- Split fingerprint matching into a pure `contains_scots_flag(text)` helper tested before filesystem observer wiring (keeps tag-sequence edge cases unit-testable without temp dirs).
