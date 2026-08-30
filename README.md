# open-plugins conformance suite

A measurement instrument that probes open-plugins customization surfaces at real prompt boundaries and records `observed` / `not observed` / `skipped`.

## Install

Add this git repository as a plugin marketplace, then install `open-plugins-conformance` from that catalog. Choose the branch (or other ref) when you add the marketplace — catalogs live at `.claude-plugin/marketplace.json` and `.cursor-plugin/marketplace.json`. The vendor-neutral probe manifest is still `.plugin/plugin.json`.

Repo: `Texarkanine/open-plugins-surface-test`. Marketplace name: `open-plugins-surface-test`. Plugin name: `open-plugins-conformance`.

Claude Code (GitHub shorthand; append `@<ref>` for a non-default branch):

```text
/plugin marketplace add Texarkanine/open-plugins-surface-test@<branch>
/plugin install open-plugins-conformance@open-plugins-surface-test
```

A full git URL uses `#<ref>` instead of `@<ref>`. Cursor: add the same GitHub repo as a marketplace (set the branch/ref in that flow), then install `open-plugins-conformance`.

Local plugin-path load (point the harness at this repo, or symlink it under a search path such as `.agents/plugins/`) is an unverified alternative. Prefer the marketplace add.

You need a POSIX shell, core Unix utilities, and Python 3. `uv` is required for the MCP and LSP probes; without it those steps record `skipped` rather than a false negative.

Self-checks for this repo:

```bash
uv run pytest
```

That suite includes the build-time sentinel-leakage lint over `prompts/` and the entrypoint skill.

## Launch

Start your harness in an **empty working directory** (or a clean worktree) with this plugin loaded. SessionStart hooks may write into `work/observations/` before you invoke the driver — do not delete that directory between launch and setup.

## Invoke

Run the operator-only entrypoint skill. With open-plugins namespacing the usual form is:

```text
/open-plugins-conformance:conformance-run
```

Some harnesses shorten or alter the slash-command shape (`/plugin:skill` vs `/skill`). If the namespaced form above is not offered, invoke the `conformance-run` skill from this plugin by whatever mechanism your harness uses for explicitly invoked skills.

The skill will:

1. Run `scripts/setup.sh` (harness / model prompts; resets fixtures and artifacts; never clears observations).
2. Walk steps 1–11: follow each `prompts/NN-*.md`, run `scripts/check.py N`, report the observation, wait for you to say `next`.
3. Print `scripts/check.py --summary`.

## Reading the capability table

The summary header shows harness, model, OS, and `uv` version from `work/run.json`. Each row is one probe step with a status:

| Status | Meaning |
| --- | --- |
| ✅ observed | The probe fingerprint appeared in the expected artifact |
| ❌ not observed | It did not appear on this run |
| ⊘ skipped | The step could not run (for example `uv` unavailable) |

This is a measurement instrument, not a pass/fail suite. Soft `not observed` results are common on a single distracted turn.

Rows marked `(discretionary)` are description-matched surfaces (description-only rule, skill, agent). Re-run those once before treating a soft miss as a harness gap.

`SessionEnd` appears on its own summary line from the hooks log. It is structurally unobservable mid-run; a miss there often means the prior session never closed cleanly, not that the harness lacks the event.

Full per-step records append to `work/observations/run.jsonl`.

## Re-run a single step

`scripts/setup.sh` is idempotent for fixtures and artifacts. To re-check one step after a soft miss:

1. Ensure fixtures are fresh if the step needs them (`bash scripts/setup.sh`).
2. Follow that step's prompt again (`prompts/NN-*.md`).
3. Run `python scripts/check.py N` for that step number.
4. Re-print the table with `python scripts/check.py --summary` (latest record per step wins).

## Headless and batch driving

Headless or batch driving of the prompt loop is a footnote, not a supported product path. The operator gate exists because several surfaces only appear across turn boundaries.
