# Active Context

## Current Task: r2-r3-indent
**Phase:** BUILD - COMPLETE

## What Was Done
- Shared indent helpers (`indent_widths`, `indent_multiples_of`, detail formatter) matching setup-test dialect
- `file_modified` + create/edit observers for steps 2–5 (JS N=7, PY N=5)
- `STEP_REGISTRY` modes: steps 2–3 `alwaysApply` (not compound); wired real observers
- Rules: `r2-js-indent.mdc` (alwaysApply only), `r3-py-indent.mdc` (globs `**/*.py`)
- Prompts 02–05 without indent-width leakage
- DESIGN.md: R2 alwaysApply-only; sample JSONL mode fixed; matrix steps 4–5 → 5-space
- Full suite: 66 passed (26 new in `tests/test_r2_r3_indent.py`)

## Files Created or Modified
- Created: `tests/test_r2_r3_indent.py`, `rules/r2-js-indent.mdc`, `rules/r3-py-indent.mdc`, `prompts/02–05-*.md`
- Modified: `scripts/check.py`, `tests/test_check.py`, `DESIGN.md`

## Deviations from Plan
- None — built to plan (prompt leakage test allows `# Step N` titles while still banning bare 5/7 in body)

## Next Step
- QA phase runs next (`/niko-qa` / automatic L3 transition)
