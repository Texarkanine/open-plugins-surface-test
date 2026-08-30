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
