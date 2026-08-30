# Active Context

## Current Task: harness-marketplace-manifests
**Phase:** QA - COMPLETE (FAIL)

## What Was Done
- TDD: `tests/test_marketplace.py` (6 contracts) went red on empty `{}` stubs, then green on filled catalogs.
- Added `/Users/tex/git/open-plugins-surface-test/.claude-plugin/marketplace.json` and `plugin.json`; `/Users/tex/git/open-plugins-surface-test/.cursor-plugin/marketplace.json` and `plugin.json`.
- README Install now leads with git marketplace add (`Texarkanine/open-plugins-surface-test@<branch>`, plugin `open-plugins-conformance@open-plugins-surface-test`); local path kept as unverified alternative.
- Full suite: 174 passed (6 new). No deviations from the preflight-amended plan.

## Next Step
- QA FAILED (1 blocking finding: unguarded triplicated plugin identity across the three `plugin.json` manifests). Rerun `/niko-build` to add a lockstep contract test test-first, then rerun `/niko-qa`. Details in `memory-bank/active/.qa-validation-status`.
