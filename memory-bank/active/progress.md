# Progress

Add Claude Code and Cursor marketplace manifests that catalog this repo's existing open-plugins conformance plugin so the operator can add the git branch as a marketplace and install from there.

**Complexity:** Level 2

## 2026-08-30 - COMPLEXITY-ANALYSIS - COMPLETE

* Work completed
    - Intent restated and approved: `.claude-plugin/marketplace.json` and `.cursor-plugin/marketplace.json` listing this repo's plugin; operator pushes and registers the branch.
    - Classified as Level 2 (self-contained catalog add; probe tree unchanged).
* Decisions made
    - Local path install is out of scope.
    - Live harness confirmation after push is operator work, not a build gate.
* Insights
    - Claude marketplace and plugin manifests both live under `.claude-plugin/`; if the plugin source is repo root, `marketplace.json` and a Claude `plugin.json` would share that directory — plan must pick a valid source/strict layout.

## 2026-08-30 - PLAN - COMPLETE

* Work completed
    - Wrote Level 2 plan: `tests/test_marketplace.py` contracts, four JSON manifests, README marketplace-add section.
    - Pinned names, `./` vs `.` sources, thin vendor `plugin.json` beside each catalog, probe tree stays at repo root.
* Decisions made
    - Default `strict: true` plus vendor `plugin.json` rather than `strict: false` component lists in the catalog.
    - Cursor marketplace plugin entries limited to `name` / `source` / `description`.
    - Live harness install is operator-after-push, not a pytest gate.
* Insights
    - Claude docs explicitly allow `source: "./"` (marketplace root is the plugin). Cursor's single-plugin template drops marketplace.json; we keep it because the install path is marketplace-add of this branch.
