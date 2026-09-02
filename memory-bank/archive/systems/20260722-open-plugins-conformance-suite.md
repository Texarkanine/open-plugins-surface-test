---
task_id: open-plugins-conformance-suite
complexity_level: 4
date: 2026-07-22
status: completed
---

# TASK ARCHIVE: open-plugins-conformance-suite

## SUMMARY

Built an open-plugins conformance measurement instrument: a probe plugin plus attended driver loop that exercises rules, skills, agents, hooks, MCP, and LSP at real prompt boundaries and emits a one-run capability report (`observed` / `not observed` / `skipped`) with a JSONL audit trail. Ten sequential milestones delivered the skeleton, setup/check harness, full probe matrix, and operator entrypoint/README — ending at 168 green pytest contracts.

## REQUIREMENTS

- Implement the instrument per `DESIGN.md`: probe plugin, driver loop (setup / prompts / checks / entrypoint skill), observation records, and capability-report summary.
- Cover the probe matrix (R1–R4 create/edit, skill, agent, hooks battery, MCP, LSP).
- Honor design invariants: no expectation leakage; setup never clears observations; checks observe and do not judge; arbitrary probe-local demanded behavior; gitignored regenerated fixtures; one probe per prompt boundary (except H1); observational wording only.
- Resolve DESIGN open questions or cut explicitly (LSP shipped, not cut).
- Measurement instrument, not a pass/fail suite — non-zero exit only for infrastructure errors.
- Commands and manual `@`-rule activation out of scope; headless/batch driving is a footnote only.

## IMPLEMENTATION

Greenfield probe plugin under the DESIGN layout:

- **Bootstrap:** `.plugin/plugin.json`, `work/` gitignore, `uv`/pytest harness, README stub → full operator README.
- **Session plumbing:** `scripts/setup.sh` (pinned reset: wipe artifacts/fixtures, preserve `work/observations/`, seed fib fixtures, create-if-absent `work/run.json`); `scripts/check.py` (step/`--summary` CLI, STEP_REGISTRY, append-only JSONL, observe-not-judge exits, emoji capability table, discretionary marks for steps 6–8).
- **Probe surfaces:** rules R1–R4, `skills/build-stamp/`, `agents/listing-auditor.md`, `hooks/hooks.json` + `scripts/hook_record.sh`, PEP 723 `servers/probe_mcp.py` + `.mcp.json`, PEP 723 `servers/probe_lsp.py` + `.lsp.json`, prompts 01–11.
- **Driver & hygiene:** `skills/conformance-run/` (operator-only, `disable-model-invocation: true`), `scripts/lint_leakage.py` (prompts + entrypoint sentinel scan).

Cross-milestone invariants from `milestones.md` held for the whole project (no leakage into prompts/entrypoint, sacred observations, observe-not-judge, probe-local fingerprints, regenerated fixtures, observational vocabulary).

## TESTING

Each milestone followed TDD: checker/contract tests before production probe components and prompts; leakage-lint tests before entrypoint/README prose. Suite grew approximately 2 → 14 → 31 → 40 → 66 → 93 → 112 → 131 → 148 → 168. Every sub-run completed `/niko-qa` PASS before reflect. Capstone state: full suite green at 168; build-time leakage lint gated by pytest planted-tree contracts.

## LESSONS LEARNED

- Keep probe checkers as replaceable `STEP_REGISTRY` callables so CLI/JSONL/`--summary` stay frozen while milestones swap fingerprints in place.
- Prefer `CONFORMANCE_WORK` over mutating real `work/` in tests for reset-boundary proofs.
- Parameterize shared-axis fingerprints by distinct N (or equivalent); AND edit-path fingerprint with fixture inequality so no-ops are visible in detail.
- Description-mode probes: trigger language in description, fingerprints only in body; closing-line equality is stricter than substring contains for create paths.
- Observational detail that must emit canonical event names cannot use naive substring bans on judgment words (`fail` ⊂ `PostToolUseFailure`); use word-boundary checks. "Tolerant JSONL parse" means skip bad lines — not swallow `OSError` when callers need missing vs unreadable.
- PEP 723 probe servers: pure formatter at module top, defer SDK imports to `main()` so pytest avoids installing server runtime deps into the harness venv. Skip gates should read the same `run.json` header the summary prints.
- Weaker conformance claims belong on optional JSONL `claim` metadata (LSP `launched`), not squeezed into `detail`.
- When a driver must *report* observational status, anti-leakage rules cannot copy the prompt leak catalog — share the sentinel catalog, keep a separate allowlist for reporting vocabulary.
- `importlib.util` + `@dataclass` + postponed annotations needs `sys.modules[spec.name] = module` before exec on Python 3.13.
- False compound modes (`alwaysApply+globs`) are plan bugs that look like DESIGN fidelity — challenge matrix labels against harness-real modes before locking registry strings.

## PROCESS IMPROVEMENTS

- Preflight amendments that look pedantic (skill vs prompt vocabulary; SessionEnd with empty `run.jsonl`; missing `uv_version` → unavailable) were high leverage when the same words/defaults are forbidden in one surface and required in another.
- Operator plan amendments after preflight (R2/R3 mode exclusivity; distinct indent bases) prevented shipping confidently wrong capability modes — treat matrix labels as challengeable.
- Plan-phase SDK/stdlib PoCs (FastMCP, LSP initialize marker) removed the main build risk for first-time server surfaces; creative was correctly skipped when DESIGN + prior probe patterns already pinned the approach.
- Stub registry rows ahead of observers let later milestones treat binding as a one-line wire — check registry readiness in preflight for similar slices.
- Including discretionary summary marks in the final milestone (rather than deferring the DESIGN pre-mortem gap again) kept README teaching and summary rendering aligned without a follow-up task.

## TECHNICAL IMPROVEMENTS

- Advisory only (called out in entrypoint preflight): adding CI that runs `uv run pytest` was out of the final milestone's brief; pytest remains the local gate.
- Headless/batch driving remains a README footnote, not a supported product path — intentional DESIGN scope.
- Empirical attended runs against real harnesses will validate soft risks that unit tests cannot (e.g. model refusal of nonstandard indent) — those are measurement outcomes, not suite defects.

## NEXT STEPS

- Run attended capability passes against target harnesses and paste summary tables into gap issues as needed.
- Optionally add CI that runs `uv run pytest` (and leakage lint via the existing test gate).
- None required for instrument completeness relative to DESIGN.md.

## Milestone List

Original ordered list (all completed). No milestones were added, removed, or reordered. One in-flight re-scope:

- **R2/R3 indent probes:** checklist text still said `alwaysApply+globs` JS; operator/preflight amendments made **alwaysApply-only JS (N=7)** and **globs-only Python (N=5)** authoritative — no false compound mode; distinct indent bases so probes cannot cross-credit.

Full checklist as archived:

1. Create plugin skeleton: `.plugin/plugin.json`, `.gitignore` for `work/`, and a README stub
2. Implement `scripts/setup.sh` with pinned reset boundary, 4-space recursive `fib.js`/`fib.py` fixtures, harness-label prompt, and `work/run.json` header
3. Implement `scripts/check.py` with step arg parsing, JSONL append to `work/observations/run.jsonl`, observe-not-judge exits, and `--summary` capability table
4. Deliver R1 end-to-end: `rules/r1-global-scots.mdc`, prompt 01, and Scottish-flag codepoint checker for `cats.md`
5. Deliver R2/R3 indent probes: alwaysApply JS and globs-only Python rules, prompts 02–05, shared indent checker, and edit-path file-modified recording *(re-scoped as noted above)*
6. Deliver R4, S1, and A1 probes: description-only poem rule, `skills/build-stamp/`, `agents/listing-auditor.md`, prompts 06–08, and their token/sentinel checkers
7. Deliver H1 hooks probe: `hooks/hooks.json`, `scripts/hook_record.sh`, step-09 action battery prompt, and per-event presence checker over accumulated `hooks.jsonl`
8. Deliver M1 MCP probe: PEP 723 `servers/probe_mcp.py`, `.mcp.json` with `${PLUGIN_ROOT}`, prompt 10, `mcp.txt` checker, and uv-absent skip path
9. Resolve LSP open question: ship `.lsp.json` + PEP 723 `probe_lsp.py` writing `lsp.launched` with `claim: launched` *(shipped; not cut)*
10. Deliver entrypoint skill `skills/conformance-run/`, build-time sentinel-leakage lint, and README (install → launch → invoke, how to read the capability table, single-step re-run)

## Sub-Run Summaries

### plugin-skeleton (L2)

Delivered plugin skeleton plus minimal `uv`/pytest self-check harness; README stub pointing at DESIGN. Surprise: `uv init --package false` treated `false` as a path — fixed with `--bare --no-package --vcs none`. Operator test-scope bias kept the suite to two contract tests on load-bearing files.

### setup-script (L2)

Delivered `scripts/setup.sh` with pytest contracts locking the DESIGN reset boundary, fib fixtures, and create-if-absent `run.json`. Added `CONFORMANCE_WORK` as the test/operator work-root seam. Dual TTY/non-TTY prompt path and `python3` JSON emission were small build-time choices.

### check-harness (L3)

Delivered `scripts/check.py`: step/`--summary` CLI, STEP_REGISTRY stubs for probes 1–11, append-only JSONL, stable `run_id`, emoji capability table. Seventeen new contracts; stub observers kept fingerprint logic out of this milestone. Preflight-pinned registry metadata removed invent-ids risk.

### r1-e2e (L2)

First probe vertical slice: Scots-flag codepoint checker on `cats.md`, alwaysApply rule with live tag-sequence demand, prompt that provokes without fingerprint leakage. Embedding the live Scotland flag sequence in the rule (and asserting its absence from the prompt) made the no-leakage invariant enforceable before build-time sentinel lint existed.

### r2-r3-indent (L3)

Shared parameterized indent checker + create/edit observers; JS N=7 alwaysApply-only and Python N=5 globs-only; prompts 02–05; edit-path `file_modified` recording. Operator amendments (no compound mode; distinct N) were the high-leverage interventions. Edit-path `observed` ANDs fingerprint with fixture inequality.

### r4-s1-a1-probes (L3)

R4 description-only sea-poem rule, S1 build-stamp skill, A1 listing-auditor agent; prompts 06–08; shared presence/closing-line helpers. Closing-line equality is meaningfully stricter than substring contains; description-mode needs trigger language without fingerprint tokens in the same field.

### h1-hooks-probe (L3)

All 13 DESIGN hook events via `hook_record.sh`; prompt 09 action battery; step 9 mid-run presence; SessionEnd in `--summary`. QA restored unreadable-log contract after tolerant parse accidentally swallowed `OSError`. Word-boundary checks needed so `PostToolUseFailure` is not banned as judgment vocabulary.

### m1-mcp-probe (L3)

PEP 723 FastMCP server (`probe_hello` → `MCP-OBSERVED-<name>`), `.mcp.json` with `uv run --script` + `${PLUGIN_ROOT}`, prompt 10, skip-first uv gate consuming `run.json`. Deferred FastMCP import to `main()` so formatter unit-tests without installing `mcp` into the harness venv.

### lsp-open-question (L2)

Shipped (not cut): stdlib LSP server writes `lsp.launched` on `initialize`; `.lsp.json` + unique `.lspprobe` fixture; step 11 observer with uv skip and JSONL `"claim":"launched"`. Million-dollar shape: optional registry `claim` + marker under observations + M1 skip-gate pattern — no sweeping redesign.

### entrypoint-readme (L3)

Operator-only `skills/conformance-run/`, `scripts/lint_leakage.py`, discretionary summary marks for steps 6–8, README (install → launch → invoke / table reading / re-run / headless footnote), DESIGN steps 12–13 closed. Driver reporting vocabulary must be allowlisted separately from prompt leak catalogs.

## System State

What exists now that did not before:

- A complete open-plugins probe plugin with manifest, rules, skill, agent, hooks, MCP, LSP, prompts 01–11, setup/check/lint scripts, and attended entrypoint skill.
- Operator-facing README documenting harness-neutral install → launch → invoke, how to read the capability table, single-step re-run, and headless footnote.
- `DESIGN.md` open questions resolved (LSP shipped); steps 12–13 closed.
- Pytest suite at 168 contracts enforcing reset boundary, observe-not-judge exits, per-probe fingerprints, skip paths, leakage lint, and summary rendering.
- Persistent memory-bank context (`productContext`, `systemPatterns`, `techContext`) oriented to this instrument; ephemeral L4 working state cleared by this archive.

End-to-end integration: operator installs plugin → launches harness → invokes `conformance-run` → setup seeds session → walks prompts → `check.py` records observations → `--summary` prints the capability table; leakage lint prevents probe fingerprints from appearing in prompts or the entrypoint body.

## Cross-Run Insights

- **Frozen harness, swappable observers:** Establishing `check.py` + stub registry early let every later probe milestone be a fingerprint swap — the strongest multi-run architectural bet, and it held through MCP/LSP claim metadata without breaking steps 1–10 schemas.
- **Leakage as a progressive constraint:** R1 proved the invariant with pairwise tests; the final milestone generalized it into build-time lint. The trap was copying prompt bans onto the driver — reporting vocabulary needs its own allowlist.
- **Skip vs false-negative:** MCP and LSP both taught that environment gates must consume the session header (`run.json`), not live PATH probes, and that skip-first ordering is a load-bearing integration contract.
- **Plan bugs that look like fidelity:** R2/R3's false compound mode and H1's judgment-word substring collision both looked like "follow DESIGN/spec carefully" until challenged against harness-real modes and literal event names.
- **Creative consistently skippable:** Across L3 probe milestones, DESIGN + prior patterns were sufficient; plan-phase PoCs replaced creative for server surfaces. Process weight stayed plan → preflight → build → QA.
- **Million-dollar question (LSP):** Launch-marker observation as a foundational assumption would still look like optional `claim` + observations marker + skip gate — confirming the late LSP ship did not force a redesign of earlier milestones.
