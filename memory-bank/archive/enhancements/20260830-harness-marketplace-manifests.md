---
task_id: harness-marketplace-manifests
complexity_level: 2
date: 2026-08-30
status: completed
---

# TASK ARCHIVE: harness-marketplace-manifests

## SUMMARY

Added Claude Code and Cursor marketplace catalogs at repo root so this git repo (on a chosen branch) can be added as a marketplace and `open-plugins-conformance` installed from it. Probe tree and `.plugin/plugin.json` were left in place. Thin vendor `plugin.json` files share `.claude-plugin/` / `.cursor-plugin/` with the catalogs. README Install now leads with marketplace add. One QA rework added identity lockstep tests.

## REQUIREMENTS

- `.claude-plugin/marketplace.json` and `.cursor-plugin/marketplace.json` listing this repo's plugin (source this tree, not a new subdirectory).
- Existing probe surfaces and vendor-neutral `.plugin/plugin.json` unchanged except as required for valid catalogs.
- Local path install out of scope; live harness confirmation is operator-after-push, not a build gate.

## IMPLEMENTATION

Marketplace name `open-plugins-surface-test`, plugin `open-plugins-conformance`, owner `Texarkanine`. Claude `source` is `"./"`; Cursor `source` is `"."` with marketplace plugin entries limited to `name` / `source` / `description`. Vendor `plugin.json` files carry `name` / `version` `0.1.0` / `description` matching `.plugin/plugin.json`; marketplace entries omit `version` (avoid dual-pin). README documents `Texarkanine/open-plugins-surface-test@<branch>` and `open-plugins-conformance@open-plugins-surface-test`; local path kept as an unverified alternative. `techContext.md` records marketplace-add as the load path and the lockstep contract.

## TESTING

TDD on `tests/test_marketplace.py`: empty `{}` stubs red, filled catalogs green. Preflight PASS WITH ADVISORY (struck a README change-detector). First QA FAIL: unguarded triplicated identity. Rework added `test_plugin_identity_lockstep` (red on a drifted Cursor description, then green). Second QA PASS. Full suite 175 passed. Probe tree and `.plugin/plugin.json` unchanged across the task range.

## LESSONS LEARNED

- A single-plugin repo that *is* the marketplace: catalogs at `.claude-plugin/` and `.cursor-plugin/`, `source` the repo root, thin vendor `plugin.json` in those same directories, pytest lockstep with `.plugin/plugin.json`. Do not nest probes under `plugins/`.
- Adding harness-native manifests next to `.plugin/plugin.json` is an identity contract. Pin `name` / `version` / `description` lockstep when the second copy appears, not after QA names the drift.

## PROCESS IMPROVEMENTS

- Preflight's change-detector cut on README copy was high leverage; keep marketplace-add prose as docs, not pytest.
- The plan's own pre-mortem ("catalogs disagree per harness") only pinned `name`. When triplicating manifests, put lockstep in the original test plan.

## TECHNICAL IMPROVEMENTS

- Residual, operator-verified after push: whether Cursor accepts bare `"."` as root `source`, and whether Claude default folder discovery covers every component type under a thin `plugin.json`.
- Advisory (not done): skip-on-absence shell-out from pytest to `claude plugin validate` / Cursor `validate-plugins.mjs` would exercise upstream schemas without a live marketplace-add.

## NEXT STEPS

- Push this branch and add `Texarkanine/open-plugins-surface-test@<branch>` as a marketplace in Claude Code and Cursor, then install `open-plugins-conformance`.
- Confirm the two residual runtime questions above on that attended pass.
