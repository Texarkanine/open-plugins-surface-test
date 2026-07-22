# Task: lsp-open-question

* Task ID: lsp-open-question
* Complexity: Level 2
* Type: simple enhancement (bounded open-question resolution)

Ship the DESIGN-proposed LSP resolution: `.lsp.json` + PEP 723 `servers/probe_lsp.py` that writes `work/observations/lsp.launched` on LSP `initialize`, step-11 observer with uv-absent skip, passive prompt 11, and JSONL `"claim":"launched"`. Do **not** cut — stdlib initialize→marker PoC confirmed the approach is not awkward.

## Test Plan (TDD)

### Behaviors to Verify

- [x] [Marker present]: `work/observations/lsp.launched` exists and uv available → `observed: true`
- [x] [Marker absent]: no marker file, uv available → `observed: false` (exit 0)
- [x] [uv skip]: `run.json` `uv_version == "unavailable"` (or key missing) → `observed: null`, detail `skipped: uv not found` (exit 0)
- [x] [Skip wins over planted marker]: uv unavailable + marker planted → still skipped
- [x] [Registry bind]: `STEP_REGISTRY[11]["observe"]` is `observe_l1_lsp`; path is `launched`
- [x] [Claim on record]: step-11 JSONL row includes `"claim":"launched"` (observed / not observed / skipped)
- [x] [CLI smoke]: `check.py 11` exit 0 for observed, not observed, and skipped
- [x] [Server marker writer]: `write_launch_marker(work)` creates `work/observations/lsp.launched`
- [x] [Server initialize]: initialize handshake (Content-Length framing) writes the marker under the resolved work root
- [x] [Work root resolution]: server honors `CONFORMANCE_WORK` when set; else `$PLUGIN_ROOT/work` derived from `__file__`
- [x] [.lsp.json wiring]: top-level server entry (no wrap key); `uv run --script ${PLUGIN_ROOT}/servers/probe_lsp.py`; required `extensionToLanguage` for unique `.lspprobe`
- [x] [Fixture seed]: setup regenerates `work/fixtures/probe.lspprobe`
- [x] [Prompt 11 passive / no leakage]: prompt asks only to open the fixture; no fingerprint/checker vocabulary; no `lsp.launched` / claim strings
- [x] [DESIGN open question closed]: DESIGN.md no longer lists LSP observability as open; documents launch-marker claim

### Test Infrastructure

- Framework: pytest via `uv run pytest` (`pyproject.toml`)
- Test location: `tests/`
- Conventions: flat `test_<area>.py`, function tests, `_load_check_module` / `_write_run_json` / `_run_check` / `work` fixture (mirror `tests/test_m1_mcp.py`); `CONFORMANCE_WORK` for CLI
- New test files: `tests/test_l1_lsp.py`
- Existing files to extend: `tests/test_setup.py` (assert `probe.lspprobe` regenerated); DESIGN assertions in `test_l1_lsp.py`

## Implementation Plan

1. [x] **Observer + claim + CLI tests (failing)** → `tests/test_l1_lsp.py`
2. [x] **Implement `observe_l1_lsp` + bind + claim emission** → `scripts/check.py`
3. [x] **Server unit + initialize handshake tests (failing)** → `tests/test_l1_lsp.py`
4. [x] **Implement `servers/probe_lsp.py`**
5. [x] **`.lsp.json` wiring tests (failing)** → `tests/test_l1_lsp.py`
6. [x] **Implement `.lsp.json`**
7. [x] **Setup fixture tests (failing)** → `tests/test_setup.py`
8. [x] **Implement setup fixture seed** → `scripts/setup.sh`
9. [x] **Prompt leakage tests (failing)** → `tests/test_l1_lsp.py`
10. [x] **Implement prompt 11** → `prompts/11-l1-lsp.md`
11. [x] **DESIGN close-out tests (failing)** → `tests/test_l1_lsp.py`
12. [x] **Close DESIGN open question** → `DESIGN.md`
13. [x] **Full suite** → 148 passed

## Technology Validation

No new packaged dependency. Stdlib-only Content-Length JSON-RPC LSP PoC confirmed. Launch via `uv run --script` for MCP parity + uv skip gate.

## Dependencies

- Existing: `uv_unavailable`, `observe_step` / JSONL append, setup fixture regeneration, `.plugin/plugin.json` already declares `"lspServers": "./.lsp.json"`
- Spec shape: open-plugins `.lsp.json` top-level map — https://open-plugins.com/agent-builders/components/lsp-servers

## Challenges & Mitigations

- **`${PLUGIN_ROOT}` in `.lsp.json`:** Matched MCP/hooks substitution.
- **Work root from LSP process:** `CONFORMANCE_WORK` then `$PLUGIN_ROOT/work` from `__file__`.
- **Claim field is new on JSONL:** Optional registry `claim` merged only into step-11 records.
- **Passive ≠ zero prompt:** Unique `.lspprobe` fixture + open prompt.
- **Avoid pygls/SDK deps:** Stdlib framing; dep-free PEP 723 script.

## Pre-Mortem

- Covered by Challenges; ship path held through build.

## Preflight Amendments

- Split former combined steps into explicit test-before-code pairs.
- Folded CLI smoke into step 1.
- Confirmed optional `claim` compatible with `REQUIRED_RECORD_KEYS <= set(record)`.

## Status

- [x] Initialization complete
- [x] Test planning complete (TDD)
- [x] Implementation plan complete
- [x] Technology validation complete
- [x] Pre-Mortem complete
- [x] Preflight
- [x] Build
- [ ] QA
