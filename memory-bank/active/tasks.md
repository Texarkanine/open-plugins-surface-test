# Task: r2-r3-indent

* Task ID: r2-r3-indent
* Complexity: Level 3
* Type: feature

Deliver R2/R3 indent probes end-to-end: `rules/r2-js-indent.mdc` (**alwaysApply only** — no globs), `rules/r3-py-indent.mdc` (globs only), prompts 02–05, shared indent fingerprint checker, and edit-path file-modified recording for steps 2–5 — TDD: shared indent + modified-file checker tests before rules, fixtures assumptions, and prompts.

## Pinned Info

### Probe → artifact → check flow

Pinned because create vs edit share one indent predicate but diverge on file-modified and artifact paths; the diagram keeps that boundary visible during build.

```mermaid
flowchart LR
    subgraph Rules
        R2["r2-js-indent.mdc<br/>alwaysApply only"]
        R3["r3-py-indent.mdc<br/>globs **/*.py"]
    end

    subgraph Create["Create path"]
        P2["prompt 02 → artifacts/reverse.js"]
        P4["prompt 04 → artifacts/strrev.py"]
    end

    subgraph Edit["Edit path"]
        FJS["fixtures/fib.js"]
        FPY["fixtures/fib.py"]
        P3["prompt 03 → artifacts/fib.js"]
        P5["prompt 05 → artifacts/fib.py"]
        FJS --> P3
        FPY --> P5
    end

    R2 --> P2
    R2 --> P3
    R3 --> P4
    R3 --> P5

    P2 --> IND["indent multiples of 7"]
    P4 --> IND
    P3 --> IND
    P5 --> IND
    P3 --> MOD["≠ fixture seed"]
    P5 --> MOD
    IND --> OBS["observe steps 2–5"]
    MOD --> OBS
```

### Invariants for this sub-run

1. No expectation leakage: 7-space demand lives only in the two rule files — never in prompts 02–05 or fixture comments.
2. Shared indent predicate for JS and Python (probe matrix Observation column: both use 7-space multiples). DESIGN probe-map diagram label "5 spaces" for `*.py` is stale; matrix + Challenges + Pre-Mortem win.
3. Create vs edit split: edit observations require indent fingerprint **and** content differing from the seeded fixture; detail reports both dimensions so a no-op turn is visible.
4. Checks observe; missing artifacts / non-compliant indent → `observed: false`, exit 0.
5. Fixtures remain setup-owned 4-space recursive seeds; this milestone does not change `setup.sh` unless a contract gap appears (expected: none — fixtures already land).
6. One probe per prompt boundary; JS vs PY extensions prevent cross-credit.
7. **One frontmatter mode per rule.** `alwaysApply` and `globs` are not combined — `alwaysApply+globs` is not a real mode (alwaysApply subsumes). R2 is `alwaysApply: true` with **no** `globs:` key; JS targeting lives in the rule body. R3 is globs-only with **no** `alwaysApply: true`. Registry/JSONL `mode` for steps 2–3 is `alwaysApply` (not `alwaysApply+globs`).

## Component Analysis

### Affected Components

- **`scripts/check.py`**: today steps 2–5 use `observe_stub` and incorrectly label mode `alwaysApply+globs`. Add pure indent helpers, file-modified helper, create/edit observers, wire `STEP_REGISTRY[2–5]`, **and correct mode to `alwaysApply` for steps 2–3**.
- **`rules/r2-js-indent.mdc`** (new): `alwaysApply: true` only — **no globs**; body demands 7-space (multiple) indentation when writing/editing JS.
- **`rules/r3-py-indent.mdc`** (new): globs `**/*.py`, no alwaysApply; same indent demand for Python.
- **`prompts/02-r2-js-create.md` … `05-r3-py-edit.md`** (new): provoke create/edit without naming indent widths, "7", or "spaces" as a style demand.
- **`tests/`**: new `tests/test_r2_r3_indent.py`; update `tests/test_check.py` wherever it plants `mode: "alwaysApply+globs"`.
- **`scripts/setup.sh` / fixtures**: already seed `fib.js` / `fib.py` at 4-space recursive — **no change expected**.
- **`DESIGN.md`**: correct R2 labeling from `alwaysApply + globs` / `alwaysApply+globs` to alwaysApply-only (mermaid node, probe matrix row, sample JSONL). Also fix ART3 "5 spaces" → 7 while there.

### Cross-Module Dependencies

- Rules → prompts: prompts must not restate rule demands; prompts name artifact paths only.
- Fixtures → edit observers: `file_modified` compares `work/artifacts/fib.{js,py}` to `work/fixtures/fib.{js,py}` (byte/text inequality after normalize newlines as needed).
- Shared indent helpers → all four step observers.
- `STEP_REGISTRY` steps 2–5: wire observers **and** fix mode string for 2–3 (`alwaysApply+globs` → `alwaysApply`).

### Boundary Changes

- Public CLI of `check.py` unchanged (`<step>` / `--summary`).
- Observation JSONL schema unchanged; `mode` value for steps 2–3 becomes `alwaysApply` (breaking vs the stub label / DESIGN sample — intentional correction).
- `detail` vocabulary expands to include indent widths and, on edit steps, `file_modified: true|false`.
- New rule/prompt files are additive plugin surface.

## Open Questions

None - operator corrected false `alwaysApply+globs` mode; approach otherwise clear from DESIGN Challenges, R1 pattern, and setup fixtures.

## Test Plan (TDD)

### Behaviors to Verify

- Indent widths: leading-space widths on non-blank lines → set/list of widths; blank lines ignored; no indented lines → empty widths (treat as not observed for fingerprint — nothing to credit).
- Multiples-of-7: all seen widths divisible by 7 → true; any width not divisible by 7 → false; tabs / mixed leading whitespace that is not pure spaces → not a compliant 7-space indent (fail fingerprint).
- Create observe (JS/PY): missing artifact → `observed: false`, detail names file; non-compliant indent → false + `indent widths seen: [...]`; compliant → true + widths detail.
- Edit observe: missing artifact → false; artifact equals fixture → `file_modified: false` and `observed: false` even if indent somehow compliant; artifact differs + non-compliant indent → false with both dimensions in detail; differs + compliant → `observed: true`.
- Registry/CLI: `check.py 2` (and at least one edit step) appends JSONL with `mode: "alwaysApply"`, correct probe/path, exits 0 on not observed.
- Rule R2: frontmatter `alwaysApply: true`; **`globs:` absent**; body demands 7-space indentation for JS; no Scottish-flag / other probe leakage.
- Rule R3: globs `**/*.py`, no `alwaysApply: true`; same indent demand.
- Prompts 02–05: name correct artifact (and fixture source on edit); no leakage of `7`, indent-width demands, or "spaces" as style instruction; no checker/sentinel spoilers.
- Cross-extension: JS observer ignores Python artifacts and vice versa (path selection only).
- Harness/docs cleanup: no remaining `alwaysApply+globs` in `check.py`, `tests/test_check.py`, or `DESIGN.md` for R2.

### Test Infrastructure

- Framework: pytest via `uv run pytest` (`pyproject.toml`)
- Test location: `tests/`
- Conventions: load `check.py` via `importlib` (see `tests/test_r1_scots.py`); `CONFORMANCE_WORK` tmp workdirs; observational wording bans from `tests/test_check.py`
- New test files: `tests/test_r2_r3_indent.py`
- Update: `tests/test_check.py` summary fixture mode string

### Integration Tests

- CLI step 2 with compliant `reverse.js` → stdout `observed`, JSONL `observed: true`, `mode: "alwaysApply"`, detail includes widths
- CLI step 3 with modified compliant `fib.js` → observed; with unmodified copy of fixture → not observed + `file_modified: false` in detail

## Implementation Plan

1. **Pure indent helpers (TDD)**
    - Files: `tests/test_r2_r3_indent.py`, `scripts/check.py`
    - Changes: add failing tests for indent-width extraction + multiples-of-N predicate; implement helpers whose **leading-space algorithm matches** `tests/test_setup.py::_indent_widths` (skip blank lines; count leading ASCII spaces only; leading tab → non-compliant marker, not a positive width). Cover empty, 4-space, 7/14, mixed, tabs. Detail format pinned to DESIGN: `indent widths seen: […]` with sorted unique positive widths.

2. **File-modified helper (TDD)**
    - Files: same
    - Changes: `file_modified(artifact: Path, fixture: Path) -> bool` — missing artifact → false; equal text → false; different → true

3. **Create-path observers + mode correction (TDD)**
    - Files: same + `STEP_REGISTRY` wiring for steps 2 and 4
    - Changes: observers for `work/artifacts/reverse.js` / `strrev.py`; set steps 2–3 `mode` to `alwaysApply`; step 4 stays `globs`

4. **Edit-path observers (TDD)**
    - Files: same + registry steps 3 and 5
    - Changes: observe `work/artifacts/fib.js` / `fib.py` vs fixtures; `observed` true only if modified **and** indent fingerprint; detail includes both indent widths and `file_modified: …`

5. **Harness CLI / fixture smoke (TDD)**
    - Files: `tests/test_r2_r3_indent.py`, `tests/test_check.py`
    - Changes: steps 2–5 not stub; `test_check.py` planted records use `mode: "alwaysApply"` for R2; exit 0 on not observed

6. **Rule R2 + prompt 02 (TDD)**
    - Files: `tests/test_r2_r3_indent.py`, `rules/r2-js-indent.mdc`, `prompts/02-r2-js-create.md`
    - Changes: assert alwaysApply present and **`globs:` absent**; then rule + prompt

7. **Rule R2 edit prompt 03 (TDD)**
    - Files: tests + `prompts/03-r2-js-edit.md`
    - Changes: provoke copy/adapt from `work/fixtures/fib.js` into `work/artifacts/fib.js` and make iterative; no indent leakage

8. **Rule R3 + prompts 04–05 (TDD)**
    - Files: `rules/r3-py-indent.mdc`, `prompts/04-r3-py-create.md`, `prompts/05-r3-py-edit.md`, tests
    - Changes: globs-only rule; create `strrev.py`; edit path via `fib.py` fixture → `work/artifacts/fib.py`

9. **DESIGN.md mode/label cleanup**
    - Files: `DESIGN.md`
    - Changes: R2 = alwaysApply only (no "+ globs"); sample JSONL `mode: "alwaysApply"`; ART3 7 spaces

10. **Full suite verification**
    - Files: none new
    - Changes: `uv run pytest` — all existing + new green

## Technology Validation

No new technology - validation not required

## Challenges & Mitigations

- **False mode `alwaysApply+globs`:** Operator correction — never combine. Fix registry, tests, DESIGN, and rule frontmatter together so the instrument does not advertise a mode that is not real.
- **Stale DESIGN diagram (5-space Python):** Fix to 7 in the DESIGN cleanup step.
- **Indent measurement ambiguity (comments, tabs, mixed):** Match existing setup-test helper semantics (`_indent_widths`). Do **not** invent a second indent dialect.
- **Empty / single-line no-indent files:** No positive widths → not observed. Detail explains widths `[]`.
- **Edit no-op vs indent failure:** Detail always carries `file_modified` on edit steps; `observed` requires both.
- **Prompt leakage of "7" / "indent":** Focused absence tests on prompts (mirror R1).
- **Agent writes edit result into fixtures instead of artifacts:** Prompts state artifacts paths; checker only credits `work/artifacts/fib.*`.

## Pre-Mortem

- **Shipped alwaysApply+globs anyway because DESIGN/matrix still said it:** Invariant #7 + step 9 + tests asserting `globs:` absent on R2 block that.
- **Treated file-modified as detail-only and marked edit steps observed on indent alone:** Step 4 behaviors require both for `observed: true`.
- **Put indent demands in prompts "to help the model":** Leakage tests are a hard gate.
- **Over-scoped into setup.sh rewrite:** Fixtures already exist; scope stays checkers → rules → prompts → DESIGN label fix.

## Status

- [x] Component analysis complete
- [x] Open questions resolved
- [x] Test planning complete (TDD)
- [x] Implementation plan complete
- [x] Technology validation complete
- [x] Pre-Mortem complete
- [x] Preflight
- [ ] Build
- [ ] QA

## Preflight Findings

- **PASS** — TDD ordering explicit per implementation step; conventions match R1 observer/registry pattern; setup fixtures already present; no blocking conflicts.
- **Amendment (preflight):** Indent helper must reuse `tests/test_setup.py::_indent_widths` semantics; detail format pinned to DESIGN example shape.
- **Amendment (operator, post-preflight):** R2 is alwaysApply **only** — do not put `globs` on the same rule; registry/DESIGN `alwaysApply+globs` is a false mode and must be corrected during build.
- **Advisory:** Milestone checklist line still says "alwaysApply+globs JS" (L4 milestones.md lifecycle — leave until archive/reconcile); plan + DESIGN + code are the build sources of truth.
