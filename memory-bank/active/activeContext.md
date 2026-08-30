# Active Context

## Current Task: harness-marketplace-manifests
**Phase:** BUILD - COMPLETE (rework — lockstep contract)

## What Was Done
- QA blocking finding: added `test_plugin_identity_lockstep` (red on a drifted Cursor description, then green after restore). Canonical identity is `.plugin/plugin.json`; both vendor `plugin.json` files and both marketplace entry descriptions must match `name`/`version`/`description`.
- Full suite: 175 passed (7 marketplace tests).

## Next Step
- Re-run QA
