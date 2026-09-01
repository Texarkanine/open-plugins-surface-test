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

## 2026-09-01 - PREFLIGHT - COMPLETE

* Work completed
    - Validated the prose/policy implementation plan against the existing entrypoint skill, pytest contracts, and leakage lint coverage
    - Confirmed the plan has no executable unit that requires new test-first steps
* Decisions made
    - Recorded `PASS WITH ADVISORY` in `.preflight-status`
* Insights
    - The proposed Step 2 instruction extends the existing pre-checker prohibition to prevent post-check artifact remediation without overlapping existing behavior

## 2026-09-01 - BUILD - COMPLETE

* Work completed
    - Updated `skills/conformance-run/SKILL.md` with opening harness-testing framing and Step 2 anti-remediation guidance
    - Refined Step 2 to omit any mention of reverse engineering or opening `scripts/check.py` per operator instruction to avoid negative priming ("Run each check only once. Do not edit artifacts after running a check.")
    - Ran full pytest suite: 182/182 passing tests, 0 errors, clean leakage and structural lint checks
* Decisions made
    - Followed Orwell's 6 rules for writing: active voice, short words, no filler, clear imperative instructions
    - Avoided negative priming by removing "reverse-engineer" and "do not open scripts/check.py"
* Insights
    - Mentioning "do not open scripts/check.py to reverse-engineer" primes the model with the exact unwanted action; stating only the direct positive/negative constraints ("Run each check only once. Do not edit artifacts after running a check.") is cleaner and more effective
