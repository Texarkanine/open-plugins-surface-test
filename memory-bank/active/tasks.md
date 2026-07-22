# Task: lsp-open-question

* Task ID: lsp-open-question
* Complexity: Level 2
* Type: simple enhancement (bounded open-question resolution)

Ship the DESIGN-proposed LSP resolution: `.lsp.json` + PEP 723 `servers/probe_lsp.py` that writes `work/observations/lsp.launched` on LSP `initialize`, step-11 observer with uv-absent skip, passive prompt 11, and JSONL `"claim":"launched"`. Do **not** cut — stdlib initialize→marker PoC confirmed the approach is not awkward.

## Test Plan (TDD)

### Behaviors to Verify

- [Marker present]: `work/observations/lsp.launched` exists and uv available → `observed: true`
- [Marker absent]: no marker file, uv available → `observed: false` (exit 0)
- [uv skip]: `run.json` `uv_version == "unavailable"` (or key missing) → `observed: null`, detail `skipped: uv not found` (exit 0)
- [Skip wins over planted marker]: uv unavailable + marker planted → still skipped
- [Registry bind]: `STEP_REGISTRY[11]["observe"]` is `observe_l1_lsp`; path is `launched`
- [Claim on record]: step-11 JSONL row includes `"claim":"launched"` (observed / not observed / skipped)
- [CLI smoke]: `check.py 11` exit 0 for observed, not observed, and skipped
- [Server marker writer]: `write_launch_marker(work)` creates `work/observations/lsp.launched`
- [Server initialize]: initialize handshake (Content-Length framing) writes the marker under the resolved work root
- [Work root resolution]: server honors `CONFORMANCE_WORK` when set; else `$PLUGIN_ROOT/work` derived from `__file__`
- [.lsp.json wiring]: top-level server entry (no wrap key); `uv run --script ${PLUGIN_ROOT}/servers/probe_lsp.py`; required `extensionToLanguage` for unique `.lspprobe`
- [Fixture seed]: setup regenerates `work/fixtures/probe.lspprobe`
- [Prompt 11 passive / no leakage]: prompt asks only to open the fixture; no fingerprint/checker vocabulary; no `lsp.launched` / claim strings
- [DESIGN open question closed]: DESIGN.md no longer lists LSP observability as open; documents launch-marker claim

### Edge Cases

- Missing `run.json` / missing work dir → infrastructure error (existing harness behavior; do not weaken)
- Empty observations dir is fine; marker creation must `mkdir` parents
- Marker under `observations/` (not `artifacts/`) so setup wipe cannot erase launch evidence mid-session
- Unique `.lspprobe` extension so R2/R3 `.js`/`.py` surfaces cannot credit LSP launch

### Test Infrastructure

- Framework: pytest via `uv run pytest` (`pyproject.toml`)
- Test location: `tests/`
- Conventions: flat `test_<area>.py`, function tests, `_load_check_module` / `_write_run_json` / `_run_check` / `work` fixture (mirror `tests/test_m1_mcp.py`); `CONFORMANCE_WORK` for CLI
- New test files: `tests/test_l1_lsp.py`
- Existing files to extend: `tests/test_setup.py` (assert `probe.lspprobe` regenerated); any DESIGN/doc assertions live in `test_l1_lsp.py` or a small docstring/content check there

## Implementation Plan

1. **Observer + claim + CLI tests (failing)**
   - Files: `tests/test_l1_lsp.py`
   - Changes: Add failing cases for `observe_l1_lsp` skip/marker/bind, step-11 JSONL `claim: launched`, and subprocess `check.py 11` smoke (observed / not observed / skipped / skip-wins) — **no** `check.py` edits in this step

2. **Implement `observe_l1_lsp` + bind + claim emission**
   - Files: `scripts/check.py`
   - Changes: Add `observe_l1_lsp` (reuse `uv_unavailable`; marker existence under `work/observations/lsp.launched`); bind `STEP_REGISTRY[11]`; extend `observe_step` so records include `"claim": "launched"` when registry entry carries `claim` (add optional `claim` on `_entry` / step 11 only); update module docstring (steps 1–11 real); run step-1 tests until green

3. **Server unit + initialize handshake tests (failing)**
   - Files: `tests/test_l1_lsp.py`
   - Changes: Assert `write_launch_marker`, work-root resolution, and a client-driven initialize writes the marker (stdlib framing, no `pygls`) — **no** server file yet

4. **Implement `servers/probe_lsp.py`**
   - Files: `servers/probe_lsp.py` (new)
   - Changes: PEP 723 script (`requires-python` only; no deps — stdlib JSON-RPC stdio); pure `resolve_work_root()` + `write_launch_marker(work)`; `main()` loop handles `initialize` (write marker + capabilities), `shutdown`/`exit`; keep unit-testable helpers at module top; run step-3 tests until green

5. **`.lsp.json` wiring tests (failing)**
   - Files: `tests/test_l1_lsp.py`
   - Changes: Assert top-level server entry (no wrap key); `uv run --script ${PLUGIN_ROOT}/servers/probe_lsp.py`; `extensionToLanguage` for `.lspprobe` — **no** `.lsp.json` file yet

6. **Implement `.lsp.json`**
   - Files: `.lsp.json` (new)
   - Changes: Server name `probe-lsp`; `command`/`args` as asserted; `extensionToLanguage`: `{".lspprobe":"lspprobe"}`; run step-5 tests until green

7. **Setup fixture tests (failing)**
   - Files: `tests/test_setup.py`
   - Changes: Assert setup regenerates `work/fixtures/probe.lspprobe` — **no** `setup.sh` edits in this step

8. **Implement setup fixture seed**
   - Files: `scripts/setup.sh`
   - Changes: Regenerate empty (or one-line neutral) `work/fixtures/probe.lspprobe`; run step-7 tests until green

9. **Prompt leakage tests (failing)**
   - Files: `tests/test_l1_lsp.py`
   - Changes: Assert `prompts/11-l1-lsp.md` will exist and must not leak marker name, claim, checker vocabulary, `observed` — **no** prompt file yet

10. **Implement prompt 11**
    - Files: `prompts/11-l1-lsp.md` (new)
    - Changes: Passive prompt — open `work/fixtures/probe.lspprobe` and wait; run step-9 tests until green

11. **DESIGN close-out tests (failing)**
    - Files: `tests/test_l1_lsp.py`
    - Changes: Assert DESIGN.md no longer lists LSP observability under Open Questions and documents launch-marker + `claim: launched` — **no** DESIGN edits in this step

12. **Close DESIGN open question**
    - Files: `DESIGN.md`
    - Changes: Move LSP observability from Open Questions to resolved approach (launch marker + `claim: launched`); keep probe matrix/component tree aligned; no full README rewrite (entrypoint README is a later milestone); run step-11 tests until green

13. **Full suite**
    - Run `uv run pytest`; fix any registry/docstring/stub fallout

## Preflight Amendments

- Split former combined steps (wiring/setup/prompt/DESIGN) so each unit is explicitly **tests-before-code**.
- Folded CLI smoke into step 1 so CLI contracts fail before `check.py` changes.
- Confirmed `tests/test_check.py` uses `REQUIRED_RECORD_KEYS <= set(record)` — optional step-11 `claim` does not break other steps.

## Technology Validation

No new packaged dependency. Stdlib-only Content-Length JSON-RPC LSP PoC (2026-07-21) confirmed: client `initialize` → server writes `work/observations/lsp.launched` → clean shutdown. Launch still goes through `uv run --script` for parity with MCP and the existing uv skip gate.

## Dependencies

- Existing: `uv_unavailable`, `observe_step` / JSONL append, setup fixture regeneration, `.plugin/plugin.json` already declares `"lspServers": "./.lsp.json"`
- Spec shape: open-plugins `.lsp.json` is a top-level map of server name → `{command, extensionToLanguage, args?}` (no `lspServers` wrap key) — https://open-plugins.com/agent-builders/components/lsp-servers
- Lifecycle constraint: harness starts LSP when plugin enabled **and matching files are present** → unique `.lspprobe` fixture + passive open prompt

## Challenges & Mitigations

- **`${PLUGIN_ROOT}` in `.lsp.json`:** Spec page is silent vs MCP; mitigate by matching MCP/hooks substitution already used in-repo. If a harness fails to expand it, the suite correctly records `not observed` (measurement), not a checker false skip.
- **Work root from LSP process:** Harness cwd may not be plugin root. Mitigate with `CONFORMANCE_WORK` then `Path(__file__).resolve().parent.parent / "work"` (same default as `check.py` / `hook_record.sh`).
- **Claim field is new on JSONL:** Keep `ObservationResult` unchanged; add optional registry `claim` merged only into the appended record for step 11 so other steps' schemas stay stable.
- **Passive ≠ zero prompt:** Spec requires matching files; prompt only opens the fixture — demanded behavior still lives in the server (`initialize` → marker), not in the prompt.
- **Avoid pygls/SDK deps:** Stdlib framing keeps PEP 723 dep-free and unit-testable without harness-venv installs (same motivation as M1 deferred FastMCP import).

## Pre-Mortem

- **Plan failed because we treated LSP like MCP (agent-written artifact):** Would put marker under `artifacts/` or demand a tool call — already rejected; observation is server-written under `observations/` with `claim: launched`.
- **Plan failed because harness never launches without a matching extension:** Covered by `.lspprobe` fixture + prompt open; unique extension avoids cross-probe credit.
- **Plan failed because we cut too early / shipped an SDK-heavy server:** PoC already showed stdlib is enough; no cut pivot unless build hits a hard harness-incompatible blocker not visible in unit tests (then document cut in a follow-up — out of this plan's happy path).
- **Plan failed by changing every step's JSONL shape:** Mitigated by optional per-entry `claim`, not a global required field.

## Status

- [x] Initialization complete
- [x] Test planning complete (TDD)
- [x] Implementation plan complete
- [x] Technology validation complete
- [x] Pre-Mortem complete
- [x] Preflight
- [ ] Build
- [ ] QA
