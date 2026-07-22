# Progress

Resolve LSP open question: ship `.lsp.json` + PEP 723 `probe_lsp.py` writing `lsp.launched` with `claim: launched`, or explicitly cut LSP from the suite and document the cut — TDD: launched-marker/skip checker tests before server/config (or cut-documentation assertions before README cut notes).

**Complexity:** Level 2

## 2026-07-21 - COMPLEXITY-ANALYSIS - COMPLETE

* Work completed
    - Checked off completed L4 milestone (M1 MCP probe)
    - Cleared sub-run ephemeral files; preserved `milestones.md`, `projectbrief.md`, `reflection/`
    - Selected first unchecked L4 milestone (LSP open-question resolution) as classification target
    - Classified as Level 2 (Simple Enhancement)
* Decisions made
    - Decision tree: not a bug fix; small enhancement / bounded open-question resolution; self-contained (ship LSP launch marker + config/server/check OR cut + document) without system-wide architectural redesign → L2
    - Preserved L4 `projectbrief.md` and `milestones.md`; created fresh sub-run `progress.md`
* Insights
    - Milestone estimate (L2) matches the decision-tree outcome; DESIGN already names the proposed resolution and the designated cut if it fights back

## 2026-07-21 - PLAN - COMPLETE

* Work completed
    - Component analysis: step-11 stub, M1 template, open-plugins `.lsp.json` schema, setup fixtures
    - TDD plan: observer + claim → CLI → server helpers/handshake → `.lsp.json` → setup `.lspprobe` → prompt 11 → DESIGN close
    - Technology PoC: stdlib Content-Length LSP writes `lsp.launched` on `initialize`
    - Decision: ship (not cut) — approach is not awkward
* Decisions made
    - Unique `.lspprobe` extension + seeded fixture so harness lifecycle ("matching files present") can launch the server
    - Optional registry `claim` merged into step-11 JSONL only; `ObservationResult` unchanged
    - Stdlib server (no pygls); still launched via `uv run --script` for skip-gate parity with MCP
    - Work root: `CONFORMANCE_WORK` else `$PLUGIN_ROOT/work` from `__file__`
* Insights
    - open-plugins `.lsp.json` has no wrap key (unlike `.mcp.json`); `extensionToLanguage` is required
    - Marker must live under `observations/` so setup artifact wipes cannot erase launch evidence
