# Active Context

## Current Task: harness-marketplace-manifests
**Phase:** PREFLIGHT - COMPLETE (PASS WITH ADVISORY)

## What Was Done
- Level 2 plan: contract tests for both marketplace catalogs + thin vendor `plugin.json` files; README marketplace-add instructions.
- Pinned: marketplace name `open-plugins-surface-test`; plugin `open-plugins-conformance`; Claude `source` `./`; Cursor `source` `.`; vendor manifests share `.claude-plugin/` / `.cursor-plugin/` with their marketplace files; do not move the probe tree.
- Preflight struck a scheduled change-detector test (README marketplace-add phrasing) from Unit 2 of `tasks.md`; Unit 2 is now docs-content-only (no test steps owed). Unit 1 (JSON manifests) unaffected. Web-verified Claude/Cursor manifest schema assumptions against live docs — no plan changes needed there. Full findings in `.preflight-status`.

## Next Step
- Build
