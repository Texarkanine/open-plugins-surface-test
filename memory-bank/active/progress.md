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
