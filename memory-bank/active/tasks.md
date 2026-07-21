# Task: plugin-skeleton

* Task ID: plugin-skeleton
* Complexity: Level 2
* Type: simple enhancement (L4 milestone 1)

Create the plugin skeleton from DESIGN.md implementation plan §1: `.plugin/plugin.json` (name + explicit component path declarations), root `.gitignore` covering `work/`, and a README stub. Introduce the repo's self-check harness (`uv` + pytest) with a minimal contract suite — only the load-bearing skeleton invariants, not prose or helper noise.

## Operator decisions

- Self-check stack: Python + pytest via `uv`
- Test scope bias: unit-test only crucial logic; skip TDD for prompts, prose, light helpers. Prefer action over exhaustive coverage.

## Test Plan (TDD)

### Behaviors to Verify

- Manifest contract: reading `.plugin/plugin.json` → JSON object with required `name` satisfying open-plugins constraints (1–64 chars; `a-z0-9-.`; start/end alphanumeric; no `--` / `..`) and explicit relative path fields for `rules`, `skills`, `agents`, `hooks`, `mcpServers`, `lspServers` (all `./…`)
- Gitignore contract: root `.gitignore` → contains a `work/` ignore entry so runtime fixtures/artifacts/observations stay out of git

### Explicitly out of test scope

- README stub prose
- pytest/uv bootstrap wiring itself (smoke by running the suite)
- Future probe/component files (later milestones)

### Test Infrastructure

- Framework: pytest, managed with `uv`
- Test location: `tests/` at repo root (new)
- Conventions: `test_*.py`, plain assert; no parallel harnesses
- New test files: `tests/test_plugin_skeleton.py`

## Implementation Plan

1. Bootstrap `uv` + pytest (no production logic yet)
   - Files: `pyproject.toml`, `uv.lock` (via `uv add --dev pytest`), `.python-version` if `uv` creates one
   - Changes: declare project + pytest dev dependency; document run command as `uv run pytest`
2. TDD — failing contract tests for skeleton invariants
   - Files: `tests/test_plugin_skeleton.py`
   - Changes: assert manifest name + component path fields; assert `.gitignore` ignores `work/`
3. Implement skeleton files to satisfy tests
   - Files: `.plugin/plugin.json`, `.gitignore`
   - Changes: vendor-neutral manifest with `name` (e.g. `open-plugins-conformance`) and explicit `./` component paths per DESIGN.md layout; root `.gitignore` with `work/` plus Python/pytest noise (`.venv/`, `__pycache__/`, `.pytest_cache/`, `*.pyc`)
4. README stub (prose — no tests)
   - Files: `README.md` (replace empty stub)
   - Changes: short placeholder: purpose one-liner + pointer that install/launch/invoke docs land in the entrypoint milestone
5. Run suite green
   - Files: none
   - Changes: `uv run pytest` passes

## Technology Validation

- New: `uv` project + pytest as dev dependency
- Validation: `uv add --dev pytest` then `uv run pytest` (expected fail until step 3, pass after)

## Dependencies

- `uv` available on PATH
- DESIGN.md component layout + open-plugins manifest rules (`name` + optional path fields)
- L4 invariants: no probe logic in this milestone; fixtures stay gitignored via `work/`

## Challenges & Mitigations

- No prior test tree: introduce once here; keep to one file / two contracts — Mitigation: operator-approved pytest+uv + scope bias
- Manifest path field names/shape may vary by host docs: Mitigation: follow open-plugins spec fields shown in DESIGN (`rules`, `skills`, `agents`, `hooks`, `mcpServers`/`lspServers` → `./…`); keep values conventional so later milestones can add files without renaming
- Empty `README.md` already exists: Mitigation: overwrite with stub, not a second file

## Pre-Mortem

- Overbuilt test suite for static files delays the vertical slice: already covered by operator scope bias + out-of-scope list
- Manifest field names wrong for target harnesses: already covered by Challenge on path fields; skeleton only needs loadable metadata, not probe behavior
- Forgetting to gitignore `work/` before setup seeds fixtures: already covered by gitignore contract test

## Preflight Amendments

- Extended `.gitignore` step to also ignore `.venv/`, `__pycache__/`, `.pytest_cache/`, and `*.pyc` now that pytest lands in this milestone (keeps the contract test focused on `work/`; extras are hygiene).

## Preflight Findings

- Greenfield confirmed: no `.plugin/`, no `.gitignore`, empty `README.md`, no `tests/`
- TDD ordering explicit per unit: step 2 tests before step 3 production files; README prose excluded by operator scope
- `uv` 0.8.22 present on PATH

## Status

- [x] Initialization complete
- [x] Test planning complete (TDD)
- [x] Implementation plan complete
- [x] Technology validation complete
- [x] Pre-Mortem complete
- [x] Preflight
- [ ] Build
- [ ] QA
