# Progress

Move conformance run scratch from `$PLUGIN_ROOT/work` to `$PWD/plugintest/<UTC-datestamp>/` (with `CURRENT`) so workspace-sandboxed writes stay in the launch cwd. Keep `CONFORMANCE_WORK` as the test/operator override. Preserve the setup reset boundary.

**Complexity:** Level 2

## 2026-08-30 - COMPLEXITY-ANALYSIS - COMPLETE

* Work completed
    - Intent approved: cwd `plugintest/<stamp>/` + `CURRENT`; not plugin-cache `work/`.
    - Classified Level 2 (work-root subsystem; multiple callers, one layout).
* Decisions made
    - Opaque `mktemp` names are not the run identity; dated dir plus `CURRENT` is.
    - `CONFORMANCE_WORK` remains the override.
* Insights
    - LSP may not share workspace `pwd`; plan must cover a pointer so `lsp.launched` lands in the same run dir.

## 2026-08-30 - PLAN - COMPLETE

* Work completed
    - Wrote Level 2 plan: shared `work_root.py`, caller wiring, workspace-relative prompts/skill, gitignore, docs.
* Decisions made
    - `$PLUGIN_ROOT/.conformance-work` is a one-line absolute pointer for LSP, not the run tree.
    - CURRENT symlink target is the relative stamp directory.
    - Entrypoint skill must not `cd` to plugin root for the run.
* Insights
    - If setup's process cwd is the cache, CURRENT would be created there again; skill wording is load-bearing.

## 2026-08-30 - PLAN - COMPLETE (re-plan after preflight FAIL fixable)

* Work completed
    - Unit 2 now requires `check.py` to insert its directory on `sys.path` before `import work_root` (importlib test loader does not).
    - CLI `ensure` pinned as `create=True`. Unit 3 remains prose/policy.
* Decisions made
    - Same `sys.path` treatment for `check.py` as for `probe_lsp.py`.
* Insights
    - Sibling scripts are not a package when loaded via `spec_from_file_location`.

## 2026-08-30 - PREFLIGHT - COMPLETE (FAIL (fixable))

* Work completed
    - Verified plan touchpoints against codebase ground truth (all `scripts/`, `tests/`, `prompts/`, skills, docs named in the plan).
    - Struck a scheduled change-detector test in Unit 3 (prompt/skill wording grep assertions) and relabeled that unit `prose/policy`; removed its `tests/test_work_root.py` file reference.
* Decisions made
    - Unit 3 owes no tests (operator-facing prose/skill wording, out of scope per `always-tdd.mdc`).
* Insights
    - `check.py` and `probe_lsp.py` are both loaded in tests via `importlib.util.spec_from_file_location`, which does not add the loaded module's directory to `sys.path`. The plan gives `probe_lsp.py` an explicit cross-directory `sys.path` fix for importing `work_root` but omits the equivalent same-directory fix for `check.py` — this will raise `ModuleNotFoundError` under every existing test that loads `check.py`. Routed back to plan.
