# Active Context

## Current Task: entrypoint-readme
**Phase:** BUILD - COMPLETE

## What Was Done
- Leakage lint: `scripts/lint_leakage.py` + `tests/test_leakage_lint.py` (catalog from check.py constants + indent phrases + `lsp.launched`; scans prompts + entrypoint only)
- Discretionary summary: steps 6–8 marked `(discretionary)` in `check.py --summary`
- Entrypoint: `skills/conformance-run/SKILL.md` (`disable-model-invocation: true`, setup → 1–11 → summary)
- README: install → launch → invoke → table reading → re-run → headless footnote
- DESIGN steps 12–13 marked Delivered
- Full suite: 168 passed

## Files Created or Modified
- `scripts/lint_leakage.py` (new)
- `tests/test_leakage_lint.py` (new)
- `tests/test_entrypoint_readme.py` (new)
- `skills/conformance-run/SKILL.md` (new)
- `scripts/check.py` (discretionary registry + summary)
- `tests/test_check.py` (discretionary summary tests)
- `README.md`, `DESIGN.md`

## Deviations from Plan
- None — built to plan

## Next Step
- QA review (`/niko-qa` / automatic L3 transition)
