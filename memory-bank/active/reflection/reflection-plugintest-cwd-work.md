---
task_id: plugintest-cwd-work
date: 2026-08-30
complexity_level: 2
---

# Reflection: plugintest-cwd-work

## Summary

Moved the conformance run from `$PLUGIN_ROOT/work` to `$PWD/plugintest/<UTC-stamp>/` (via `CURRENT` plus an install-tree pointer for LSP). Built to plan; QA passed with two non-blocking advisories.

## Requirements vs Outcome

All acceptance criteria landed: unset-override callers share cwd `plugintest/CURRENT`, `CONFORMANCE_WORK` still wins, prompts/skill/docs are workspace-relative, gitignore covers `plugintest/` and `.conformance-work`. Preflight advisories (`work_root.py status`, e2e smoke) were left unimplemented, correctly treated as optional.

## Plan Accuracy

The sequence was right. The surprises were already in the plan: importlib-loaded `check.py` needs a `sys.path` insert (preflight caught this twice), and `ensure` must use process cwd so SessionStart and setup share one stamp. No extra units. The pointer-before-CURRENT order is the LSP mechanism, not a later fix.

## Build & QA Observations

Build was linear TDD (red resolver, red callers, red gitignore). QA did not find gaps; it noted duplicated `_without_plugin_pointer()` (matches this suite's per-file helpers) and that unset-override tests briefly write `.conformance-work` into the real checkout (safe single-worker).

## Insights

### Technical
- Tests that load `scripts/*.py` via `importlib.util.spec_from_file_location` do not put that file's directory on `sys.path`. A sibling import that works as a CLI (`python3 scripts/check.py`) fails in those tests unless the module inserts its own directory first.

### Process
- Preflight twice flagged the same importlib/`sys.path` hole. Encoding the `check.py` default-resolve test as an explicit TDD step was what made the second pass actually stick.

### Million-Dollar Question

What we built is the elegant form: one resolver, cwd run, install-tree pointer only for processes that do not share workspace cwd. A plugin-root `work/` default was never a viable foundation once marketplace install + workspace sandboxing are assumed. Nothing to unwind beyond deleting leftover `work/` gitignore later if those dirs are gone.
