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
