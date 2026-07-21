# Task: setup-script

* Task ID: setup-script
* Complexity: Level 2
* Type: simple enhancement

Implement `scripts/setup.sh` as the session reset + seed step: wipe `work/artifacts/`, wipe and regenerate `work/fixtures/` (`fib.js` / `fib.py` at 4-space recursive), prompt for harness label + model (default if declined), create `work/run.json` only when absent, and never touch `work/observations/`.

## Test Plan (TDD)

### Behaviors to Verify

- [Wipe artifacts]: after planting a file under `work/artifacts/`, running setup → that path is gone (directory empty or recreated empty)
- [Preserve observations]: after planting evidence under `work/observations/`, running setup → file content and path unchanged
- [Regenerate fixtures]: after planting junk under `work/fixtures/`, running setup → junk gone; `fib.js` and `fib.py` present
- [Fixture shape]: seeded `fib.js` / `fib.py` → recursive Fibonacci-style implementations whose indentation uses 4-space multiples (not tabs; not 7-space)
- [No fixture leakage]: fixture bodies → contain no probe sentinels / demanded behaviors (no 7-space instruction, Scottish-flag guidance, or other probe tokens)
- [Create run.json if absent]: with no `work/run.json`, running setup with harness/model on stdin → `work/run.json` exists with harness, model, OS, and `uv` version fields
- [Default declined prompts]: empty stdin answers for harness/model → `run.json` uses harness `"unknown"` and model `"unspecified"`
- [Preserve existing run.json]: with `work/run.json` already present, running setup with different stdin → file content unchanged
- [Idempotent second run]: run setup twice → second run still preserves observations, reseeds fixtures, leaves existing `run.json` alone
- [Missing work/]: with no `work/` directory, running setup → creates needed wipe/seed targets and `run.json` without creating or clearing `work/observations/` solely to "initialize" it

### Test Infrastructure

- Framework: pytest via `uv run pytest` (existing)
- Test location: `tests/`
- Conventions: `test_*.py`, plain assert, repo-root `Path` helpers as in `tests/test_plugin_skeleton.py`
- New test files: `tests/test_setup.py`
- Invocation seam: tests set `CONFORMANCE_WORK` to a `tmp_path` work root so setup never mutates a shared tree; script defaults to `$PLUGIN_ROOT/work` when unset

## Implementation Plan

1. Write failing setup contract tests (TDD red)
   - Files: `tests/test_setup.py`
   - Changes: subprocess-invoke `scripts/setup.sh` with controlled stdin and `CONFORMANCE_WORK`; assert wipe/preserve/seed/`run.json` behaviors above
2. Implement `scripts/setup.sh` to green the suite
   - Files: `scripts/setup.sh` (new)
   - Changes: resolve plugin root from script location; `WORK_DIR=${CONFORMANCE_WORK:-$PLUGIN_ROOT/work}`; delete `artifacts/`; delete+recreate `fixtures/` with embedded 4-space recursive `fib.js`/`fib.py`; prompt harness+model (defaults `"unknown"` / `"unspecified"` on empty); write `run.json` only if absent (keys: `harness`, `model`, `os`, `uv_version`; include OS + `uv --version` when available); never read/write/delete under `observations/`
3. Confirm full self-check suite green
   - Files: none (verification only)
   - Changes: `uv run pytest` — skeleton + setup contracts

## Technology Validation

No new technology - validation not required. Reuses POSIX shell + existing pytest/`uv` self-check harness.

## Dependencies

- DESIGN.md reset-boundary diagram and `work/run.json` header fields (harness, model, OS, uv version)
- Existing `tests/` + `pyproject.toml` pytest setup from plugin-skeleton
- Later milestones depend on seeded fixtures and preserved observations; this milestone does not implement `check.py` or probes

## Challenges & Mitigations

- [Interactive prompts break CI/tests]: Drive prompts via stdin in tests; empty input selects documented defaults
- [Accidental observation wipe via `rm -rf work/`]. Never wipe `work/` wholesale — only `artifacts/` and `fixtures/` paths
- [Fixture content under-specified]: Assert structural contracts (4-space indent, recursion, paths) rather than byte-identical golden files, so implementation can choose a small clear fib
- [uv absent on some hosts]: Record a clear placeholder / empty `uv_version` rather than failing setup — setup must not require probe-server tooling

## Pre-Mortem

- [Setup wiped observations via over-broad cleanup]: already covered by Challenge 2; tests must plant observation evidence before any green implementation
- [Tests asserted prose/README instead of reset contracts]: keep scope to wipe/preserve/seed/`run.json` only — README remains stub until entrypoint milestone
- [Fixtures accidentally taught indent/probe expectations]: leakage assertion in test plan; fixtures stay behaviorally boring recursive fib only

## Status

- [x] Initialization complete
- [x] Test planning complete (TDD)
- [x] Implementation plan complete
- [x] Technology validation complete
- [x] Pre-Mortem complete
- [x] Preflight
- [ ] Build
- [ ] QA

## Preflight Findings

- PASS: TDD ordering explicit (tests step before `setup.sh` implementation)
- PASS: Paths match DESIGN (`scripts/setup.sh`, `tests/test_setup.py`)
- Amendment: pinned declined-prompt defaults (`unknown` / `unspecified`) and `run.json` key names
