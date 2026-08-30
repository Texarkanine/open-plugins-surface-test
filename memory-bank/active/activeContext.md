# Active Context

## Current Task: plugintest-cwd-work
**Phase:** PLAN - COMPLETE (re-plan)

## What Was Done
- Preflight FAIL (fixable): `check.py` must `sys.path`-insert `scripts/` before `import work_root` because tests load it via importlib. Plan Unit 2 updated. Unit 3 remains docs-only.
- CLI `ensure` is always `create=True`.

## Next Step
- Re-run preflight
