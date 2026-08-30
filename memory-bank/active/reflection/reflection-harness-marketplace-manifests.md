---
task_id: harness-marketplace-manifests
date: 2026-08-30
complexity_level: 2
---

# Reflection: harness-marketplace-manifests

## Summary

Added Claude Code and Cursor marketplace catalogs at repo root that list this repo's existing plugin, plus thin vendor `plugin.json` files and README marketplace-add instructions. Succeeded after one QA rework (identity lockstep test).

## Requirements vs Outcome

Delivered: both catalogs point at this tree (`./` / `.`), probe surfaces and `.plugin/plugin.json` untouched, local path demoted in README. Added (required for loaders, allowed by the brief): vendor `plugin.json` beside each catalog. Added after QA: `test_plugin_identity_lockstep`. Live harness install remains operator-after-push, as specified.

## Plan Accuracy

File list and `source: "./"` vs `"."` were right. Preflight correctly struck a README change-detector. The real miss was not treating triplicated `version`/`description` as a contract in the original test plan — we only pinned `name`. Cursor `"."` and Claude default component discovery are still unproven at runtime, as planned.

## Build & QA Observations

Empty `{}` stubs gave a clean red run; filling catalogs went green on the first try. QA FAIL was the right catch: three `plugin.json` files can drift per harness. Rework was one test, proved red on a drifted Cursor description, then green.

## Insights

### Technical
- Adding harness-native manifests next to `.plugin/plugin.json` creates an identity contract on day one. Pin `name`/`version`/`description` lockstep in the first test file, not after QA names the copies.

### Process
- Preflight's change-detector cut was high leverage (README). QA's lockstep finding was the packaging analogue of the plan's own pre-mortem ("catalogs disagree per harness") — half-applied to `name` only.

### Million-Dollar Question

A single-plugin repo that *is* the marketplace: catalogs at `.claude-plugin/` and `.cursor-plugin/`, `source` the repo root, thin vendor `plugin.json` sharing those directories, pytest lockstep with `.plugin/plugin.json`. Do not nest probes under `plugins/`. That is what we built; the L4 skeleton would have included the catalogs if git-marketplace-add had been the install path from the start.
