# Project Brief

## User Story

As an operator, I want the conformance run scratch to live under the launch workspace (`$PWD/plugintest/<datestamp>/`) so harness workspace sandboxing can write artifacts, instead of under the harness plugin-install tree.

## Use-Case(s)

### Use-Case 1

Operator launches the harness in some workspace, runs setup and the driver loop. Fixtures, artifacts, and observations appear at `$PWD/plugintest/<UTC-stamp>/` with `plugintest/CURRENT` pointing at that run. SessionStart, setup, and `check.py` share that directory.

### Use-Case 2

Pytest keeps using `CONFORMANCE_WORK` as an explicit override so tests do not depend on `pwd`.

## Requirements

1. Default work root is `$PWD/plugintest/<UTC-datestamp>/`, not `$PLUGIN_ROOT/work`.
2. `plugintest/CURRENT` points at the active run so SessionStart (before setup) and later scripts resolve the same directory.
3. `CONFORMANCE_WORK` still overrides when set.
4. Plugin code stays under `${PLUGIN_ROOT}`; prompts/skill/hooks/LSP/README use the workspace-relative layout so sandboxed writes are not steered into the install cache.
5. Reset boundary unchanged: setup wipes artifacts and regenerates fixtures; never clears observations.

## Constraints

1. Do not use an opaque `mktemp` name as the only identity of a run.
2. Do not put the run (fixtures/artifacts/observations) in the plugin install dump.
3. Sacred SessionStart log: first writer may create the dated dir; setup must not wipe `observations/`.

## Acceptance Criteria

1. With `CONFORMANCE_WORK` unset, setup/check/hook_record resolve a directory under `$PWD/plugintest/` and keep `CURRENT` in sync.
2. `CONFORMANCE_WORK` still wins in existing pytest contracts.
3. Prompts and the entrypoint skill name workspace-relative artifact paths (not plugin-root `work/`).
4. `.gitignore` ignores `plugintest/`.
5. README/DESIGN/`techContext.md` describe the cwd `plugintest/` default, not `$PLUGIN_ROOT/work`.
