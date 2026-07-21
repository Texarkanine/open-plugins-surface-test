# Active Context

## Current Task: setup-script
**Phase:** BUILD - COMPLETE

## What Was Done
- Added `tests/test_setup.py` (12 contracts) and `scripts/setup.sh`
- Reset boundary: wipe artifacts, regenerate 4-space recursive fib fixtures, never touch observations
- `run.json` create-if-absent with harness/model/os/uv_version; defaults `unknown`/`unspecified`
- Full suite green: 14 passed

## Files
- `/home/mobaxterm/git/oplugin-test-suite/scripts/setup.sh` (created)
- `/home/mobaxterm/git/oplugin-test-suite/tests/test_setup.py` (created)

## Key Decisions
- `CONFORMANCE_WORK` env seam for tmp work roots in tests
- `python3` one-liner to emit `run.json` (safe escaping; no jq dependency)
- Interactive prompts only when stdin is a TTY; non-TTY reads two lines

## Deviations
- Used `python3` for JSON write instead of pure-shell printf — escaping safety for free-form harness/model labels

## Next Step
- QA review
