---
task_id: lsp-open-question
date: 2026-07-21
complexity_level: 2
---

# Reflection: lsp-open-question

## Summary

Resolved the LSP open question by shipping (not cutting): stdlib PEP 723 `servers/probe_lsp.py` writes `work/observations/lsp.launched` on `initialize`, `.lsp.json` + unique `.lspprobe` fixture, step-11 observer with uv skip and JSONL `"claim":"launched"`. Build and QA both clean; suite 148 green.

## Requirements vs Outcome

All planned requirements shipped: observer + claim emission, server handshake, `.lsp.json`, setup seed, passive prompt 11, DESIGN moved to Resolved Design Choices. No descopes or unplanned additions. README left to the entrypoint milestone as planned.

## Plan Accuracy

Preflight's TDD split (test-then-code for wiring/setup/prompt/DESIGN) was right — build followed it without reordering. Planned challenges (work-root resolution, matching-files lifecycle, optional claim) were the ones that mattered; no mid-build surprises. Stdlib PoC from plan phase held.

## Build & QA Observations

Smooth TDD build. QA found no defects. The only DESIGN polish beyond the plan text was dropping the unused mermaid `classDef open` once L1 left the open styling.

## Insights

### Technical
- Weaker conformance claims belong on the JSONL record (`claim`), not squeezed into `detail` — optional per-registry-entry metadata keeps steps 1–10 schemas stable.
- When a harness starts servers only for matching file types, seed a probe-owned extension under fixtures and keep the prompt passive; demanded behavior stays in the server.

### Process
- Nothing notable — L2 ship-vs-cut was decided at plan via PoC; that removed the only real ambiguity before build.

### Million-Dollar Question

If launch-marker observation had been a foundational assumption, the suite would still look like this: optional registry `claim`, marker under `observations/`, stdlib initialize handler. No sweeping redesign — the M1 skip-gate pattern plus one claim field is the elegant shape.
