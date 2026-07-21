# Project Brief

## User Story

As an operator comparing AI coding harnesses, I want an open-plugins conformance measurement instrument that probes each customization surface at a real prompt boundary so that I can produce a one-run capability report (`observed` / `not observed` / `skipped`) for the harness in front of me.

## Use-Case(s)

### Attended capability pass

Launch the plugin in an empty worktree, invoke the entrypoint skill, step through each probe prompt, and leave with a capability table plus JSONL audit trail.

### Evidence for harness gaps

Paste the summary table into an issue so a missing surface is obvious without interpreting raw logs; re-run a single discretionary step when a soft `not observed` needs a second look.

## Requirements

1. Implement the instrument as specified in [`DESIGN.md`](../../DESIGN.md): probe plugin, driver loop (setup / prompts / checks / entrypoint skill), observation records, and capability-report summary.
2. Cover the probe matrix (rules R1–R4 including create/edit paths, skill, agent, hooks battery, MCP, LSP per open-question cut criteria).
3. Honor all design invariants (no expectation leakage, setup never clears `work/observations/`, checks observe and do not judge, arbitrary demanded behavior, gitignored regenerated fixtures, one probe per prompt boundary except H1, non-colliding file types).
4. Follow the design's component layout and implementation plan ordering, including open questions and cut criteria (e.g. LSP).

## Constraints

1. Measurement instrument, not a pass/fail test suite — non-zero exit only for infrastructure errors.
2. Probe expectations must not appear in prompts, the entrypoint skill, or fixtures.
3. Commands and manual `@`-rule activation are out of scope.
4. Performance, cost, and output-quality measurement are out of scope.
5. Headless/batch driving is a footnote, not a supported product path.

## Acceptance Criteria

1. A single attended run can produce `check.py --summary` output covering the probe matrix with per-step records in `work/observations/run.jsonl`.
2. Setup resets fixtures/artifacts without touching observations; `work/run.json` captures harness/model/environment metadata.
3. README documents install → launch → invoke per harness and how to read the capability table / re-run a step.
4. Design open questions are resolved or explicitly cut as the design allows (notably LSP).
