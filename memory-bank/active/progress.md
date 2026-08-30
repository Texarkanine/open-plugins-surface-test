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

## 2026-08-30 - PREFLIGHT - COMPLETE (PASS WITH ADVISORY)

* Work completed
    - Ran TDD Plan Encoding, Convention Compliance, Dependency Impact, Conflict Detection, and Completeness Precheck against `tasks.md`.
    - Struck a scheduled change-detector test (README marketplace-add phrasing) from Unit 2; that unit is docs content and owes no tests. Unit 1 (four JSON manifests) confirmed correctly TDD-staged and untouched.
    - Web-verified Claude Code and Cursor plugin/marketplace schemas against current docs: `source: "./"` + shared `.claude-plugin/` vendor manifest, omitted marketplace-entry `version`, and the Cursor `additionalProperties: false` entry allowlist are all confirmed correct.
* Decisions made
    - First line of `.preflight-status`: `PASS WITH ADVISORY`.
* Insights
    - Residual runtime uncertainty (Cursor bare `"."` source; Claude default component discovery under a thin `plugin.json`) is real but already correctly scoped by the plan as post-push operator verification, not a build gate.
    - Advisory: shelling out to the harnesses' own upstream validators (`cursor/plugins`' `validate-plugins.mjs`, `claude plugin validate`) from pytest, skip-on-absence, would close most of that residual gap without a live install — not applied, plan is acceptable as-is.

## 2026-08-30 - BUILD - COMPLETE

* Work completed
    - Stubbed then implemented `tests/test_marketplace.py`; filled Claude/Cursor marketplace and vendor `plugin.json` files; README Install rewritten around git marketplace add.
    - `uv run pytest`: 174 passed (6 new).
* Decisions made
    - Claude add recipe uses `owner/repo@<branch>`; full git URL uses `#<ref>`.
    - Local path install remains in README as an unverified alternative.
* Insights
    - Empty `{}` stubs produced the expected KeyError red run; `test_probe_tree_unmoved` was already green (surfaces already at repo root).

## 2026-08-30 - QA - COMPLETE (FAIL)

* Work completed
    - Semantic review of commit `e6e0bd8` against the preflight-amended plan: four manifests, `tests/test_marketplace.py`, README Install rewrite. Re-ran `uv run pytest` (174 passed) and confirmed a clean tree.
    - One blocking finding, three advisories, recorded in `.qa-validation-status` and `tasks.md`.
* Decisions made
    - First line of `.qa-validation-status`: `FAIL`. Build must rerun to add a manifest lockstep contract test.
    - Advisory duplication in `test_source_resolves_to_repo_root_plugin` and the exact-set vendor-directory assertions accepted as-is; both were planned.
* Insights
    - Adding harness-native manifests turned plugin identity into three copies (five for `description`). The plan pinned `name` in all of them but never pinned `version` or `description`, so the very drift the plan feared ("catalogs disagree, install commands differ per harness") is only half-guarded.
    - The project's TDD rule already carves out manifest/version lockstep as a legitimate contract test, so closing this gap needs no rule exception.

## 2026-08-30 - BUILD - COMPLETE (rework)

* Work completed
    - Added `test_plugin_identity_lockstep` in `tests/test_marketplace.py`. Proved red with a drifted Cursor `description`, then restored lockstep.
    - `uv run pytest`: 175 passed.
* Decisions made
    - Canonical identity remains `.plugin/plugin.json`; vendor manifests and marketplace descriptions must match, not the other way around.
* Insights
    - A lockstep test is the right guard for triplicated manifests; generating one file from another was unnecessary for two small JSON objects.

## 2026-08-30 - QA - COMPLETE (PASS)

* Work completed
    - Re-reviewed commit `12b6266` against the preflight-amended plan; diffed against the prior FAILed QA commit and confirmed the rework touched only `test_plugin_identity_lockstep`. Re-ran `uv run pytest` (175 passed) and confirmed `.plugin/plugin.json` and the probe tree are unchanged across the whole task range.
    - Zero blocking findings; two advisories carried forward unchanged from the first QA pass.
* Decisions made
    - First line of `.qa-validation-status`: `PASS`. Task may proceed to Reflect.
* Insights
    - The lockstep test fully closes the drift gap the first QA pass identified: it now asserts every copy of `name`/`version`/`description` this task introduced, not just `name`.

## 2026-08-30 - REFLECT - COMPLETE

* Work completed
    - Reflection written; `techContext.md` updated for marketplace load path and identity lockstep.
* Decisions made
    - productContext / systemPatterns: no update (product and probe architecture unchanged).
* Insights
    - Harness-native `plugin.json` next to `.plugin/plugin.json` is an identity contract; test lockstep when the second copy is introduced.
