# Progress

Add anti-remediation and harness-testing framing to `skills/conformance-run/SKILL.md` to prevent driving models from reverse-engineering checker expectations.

**Complexity:** Level 2

## 2026-09-01 - COMPLEXITY ANALYSIS - COMPLETE

* Work completed
    - Clarified intent with operator regarding anti-remediation framing in the `conformance-run` entrypoint skill
    - Determined complexity level: Level 2 (Simple Enhancement)
* Decisions made
    - Selected Level 2 (Simple Enhancement) workflow for single-component skill enhancement with test/lint verification
    - Adopted Orwell's 6 rules for writing to keep the instruction direct, concise, and close to operator's proposed wording
* Insights
    - Driving models reflexively treat `not observed` as an error to fix; explicit framing that the harness is being evaluated removes the impulse to inspect checkers and modify artifacts post-check

## 2026-09-01 - PLAN - COMPLETE

* Work completed
    - Created detailed Level 2 implementation plan in `memory-bank/active/tasks.md`
    - Defined TDD plan, technology validation, challenges/mitigations, and pre-mortem
* Decisions made
    - Classified the enhancement as a prose/policy artifact (no change-detector unit tests added; verified via existing leakage lint and structural test suite)
    - Structured the wording to place core framing in the opening section and an explicit negative constraint in Step 2
* Insights
    - Preserving observational vocabulary (`observed`, `not observed`, `skipped`) while avoiding judgment/coaching terms ensures full alignment with existing test suite
