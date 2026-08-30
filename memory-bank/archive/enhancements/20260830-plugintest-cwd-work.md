---
task_id: plugintest-cwd-work
complexity_level: 2
date: 2026-08-30
status: completed
---

# TASK ARCHIVE: plugintest-cwd-work

## SUMMARY

Moved the conformance run from `$PLUGIN_ROOT/work` (plugin install / marketplace cache) to `$PWD/plugintest/<UTC-stamp>/` with `plugintest/CURRENT` as the shared pointer. `${PLUGIN_ROOT}` remains the install tree (scripts, servers, prompts). `CONFORMANCE_WORK` still overrides. LSP finds the cwd run via `$PLUGIN_ROOT/.conformance-work`. Setup's reset boundary is unchanged.

## REQUIREMENTS

- Default work root is `$PWD/plugintest/<UTC-datestamp>/`, not `$PLUGIN_ROOT/work`.
- `plugintest/CURRENT` (relative symlink) so SessionStart, setup, and `check.py` share one stamp; no opaque `mktemp` as the only identity.
- `CONFORMANCE_WORK` still wins for pytest and operators.
- Prompts, skills, agent, and docs name workspace-relative `plugintest/CURRENT/...` paths; do not `cd` into the plugin cache to run setup.
- Setup wipes artifacts and regenerates fixtures; never clears observations.
- gitignore `plugintest/` and `.conformance-work`; keep leftover `work/`.

## IMPLEMENTATION

Shared resolver `scripts/work_root.py` (`ensure` CLI, always `create=True`): `CONFORMANCE_WORK` → existing `$PLUGIN_ROOT/.conformance-work` pointer (if that dir exists) → cwd `plugintest/CURRENT` → mkdir stamp, relative `CURRENT` symlink, write pointer. Never mkdir `$PLUGIN_ROOT/work`.

Callers: `setup.sh` and `hook_record.sh` capture `python3 "$PLUGIN_ROOT/scripts/work_root.py" ensure` with process cwd = launch workspace. `check.py` and `servers/probe_lsp.py` insert `scripts/` on `sys.path` before `import work_root` because tests load those files via importlib without adding the script directory.

Operator-facing paths rewritten to `plugintest/CURRENT/...`. Entrypoint skill runs `bash "$PLUGIN_ROOT/scripts/setup.sh"` from the launch cwd. README, DESIGN, `techContext.md`, and `systemPatterns.md` record the cwd-run contract.

## TESTING

TDD: `tests/test_work_root.py` (override, create+CURRENT+pointer, reuse, pointer-when-cwd-differs); caller tests without override in a tmp cwd (setup reset boundary, hook_record under CURRENT, importlib-loaded `check.py` default resolve, LSP default resolve); gitignore contract. Existing `CONFORMANCE_WORK` pytest contracts kept green.

Preflight PASS WITH ADVISORY (optional `work_root.py status`; optional e2e setup+hook_record+check without override — not implemented). QA PASS with two non-blocking advisories: duplicated `_without_plugin_pointer()` helper (matches this suite's per-file helpers); unset-override tests briefly write `.conformance-work` into the real checkout (safe single-worker). Full suite 182 passed.

## LESSONS LEARNED

- Tests that load `scripts/*.py` via `importlib.util.spec_from_file_location` do not put that file's directory on `sys.path`. A sibling import that works as a CLI fails there unless the module inserts its own directory first.
- Pointer-before-CURRENT is the LSP-without-workspace-cwd mechanism, not a defect: a stale pointer from a prior cwd wins over a fresh local `CURRENT`.
- Plugin-root `work/` was never a viable default once marketplace install and workspace sandboxing are assumed.

## PROCESS IMPROVEMENTS

- When a module is both a CLI and importlib-loaded in tests, encode the `sys.path` insert *and* a default-resolve test on that module as explicit TDD steps. Preflight flagged the `check.py` hole twice; the second plan stuck because the test was named in the plan.
- Prompt/skill wording grep tests are change-detectors; keep them out of the executable TDD units (preflight struck them).

## TECHNICAL IMPROVEMENTS

- Optional: `python3 scripts/work_root.py status` for non-destructive CURRENT/pointer diagnostics.
- Optional: single-process e2e smoke of setup + hook_record + check without `CONFORMANCE_WORK`.
- Unset-override tests that exercise real `PLUGIN_ROOT` would race under `pytest -n auto` because they write/restore `.conformance-work` in the checkout.
- Leftover `work/` gitignore can drop later if those local dirs are gone.

## NEXT STEPS

- Re-run an attended harness pass in a workspace that is not the plugin cache (the original motivation). Writes should land under that cwd's `plugintest/CURRENT/`.
- None required for this task itself.
