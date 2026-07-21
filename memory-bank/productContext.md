# Product Context

## Target Audience

Operators and plugin authors who need to know which [open-plugins](https://open-plugins.com/plugin-builders/specification) customization surfaces a given AI coding harness actually honors — especially when comparing harnesses or filing evidence-backed bugs against a vendor.

## Use Cases

- Run a single attended pass against the harness in front of you and leave with a capability report (observed / not observed / skipped) for each probed surface.
- Paste that report into an issue or discussion so a missing surface is obvious without reading raw logs.
- Re-run one discretionary step when a soft `not observed` needs a second look before believing it.
- Optionally drive the same suite headlessly from another harness; the product optimizes for the attended pass, not batch CI.

## Key Benefits

- Measures delivery of plugin surfaces (rules, skills, agents, hooks, MCP, LSP) at a real prompt boundary, not by static inspection of configs.
- Treats results as observations, not pass/fail judgments — wording stays honest about what one run can and cannot prove.
- Keeps probes mutually isolated so one surface's compliance cannot mask another's.

## Success Criteria

- One run produces a readable capability table covering the probe matrix, with an audit trail of per-step observation records.
- A missing or unsupported surface is visible at a glance without interpreting JSONL.
- Results remain meaningful: demanded behaviors are arbitrary enough that accidental compliance is negligible, and setup never destroys evidence that can only be collected once per session (e.g. SessionStart hooks).

## Key Constraints

- This is a measurement instrument, not a test suite: checks must not exit non-zero for `not observed`.
- Probe expectations must not leak into prompts, the entrypoint skill, or fixtures — otherwise the suite measures instruction-following of leaked hints, not surface delivery.
- Create vs. edit paths for glob-scoped rules are separate probes; file types must not collide across probes.
- Commands and manual rule activation (`@`-reference) are out of scope — the suite assumes the operator can point the harness at files.
- Performance, cost, and output-quality measurement are out of scope.
