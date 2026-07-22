# Active Context

## Current Task: lsp-open-question
**Phase:** BUILD - COMPLETE

## What Was Done
- Shipped L1 LSP probe: `observe_l1_lsp` + JSONL `claim: launched`, stdlib `servers/probe_lsp.py`, `.lsp.json`, setup `probe.lspprobe`, passive prompt 11, DESIGN open-question → Resolved
- Full suite: 148 passed (17 new in `tests/test_l1_lsp.py`)

## Files Created or Modified
- `/home/mobaxterm/git/oplugin-test-suite/tests/test_l1_lsp.py` (new)
- `/home/mobaxterm/git/oplugin-test-suite/servers/probe_lsp.py` (new)
- `/home/mobaxterm/git/oplugin-test-suite/.lsp.json` (new)
- `/home/mobaxterm/git/oplugin-test-suite/prompts/11-l1-lsp.md` (new)
- `/home/mobaxterm/git/oplugin-test-suite/scripts/check.py`
- `/home/mobaxterm/git/oplugin-test-suite/scripts/setup.sh`
- `/home/mobaxterm/git/oplugin-test-suite/tests/test_setup.py`
- `/home/mobaxterm/git/oplugin-test-suite/DESIGN.md`

## Key Decisions
- Stdlib JSON-RPC (no pygls); optional registry `claim` on step 11 only
- Unique `.lspprobe` fixture for harness lifecycle matching-files rule

## Deviations from Plan
- None — built to plan (removed unused mermaid `classDef open` as part of DESIGN close-out)

## Next Step
- QA review (automatic for Level 2)
