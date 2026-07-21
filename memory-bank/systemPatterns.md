# System Patterns

## How This System Works

This repository is an open-plugins plugin plus a driver loop. The plugin embeds probes (rules, skills, agents, hooks, MCP/LSP servers). An entrypoint skill walks the operator through one prompt boundary per probe: follow a prompt, then run a checker that records whether the probe's fingerprint appeared in the expected artifact.

Two load-bearing assumptions dominate everything else:

1. **Observation over judgment.** Checkers append `observed` / `not observed` (or skip). Infrastructure errors may fail the process; a missing fingerprint must not.
2. **Reset boundary.** Setup may wipe fixtures and artifacts. It must never touch the observation log: SessionStart evidence is written before the entrypoint runs and cannot be regenerated in the same session.

If either assumption is violated, the capability report is meaningless even when the rest of the suite looks correct.

## Probe → Prompt → Artifact

Every surface uses the same shape: a plugin component demands arbitrary behavior, a prompt provokes it, and an artifact either carries a fingerprint or does not. Demanded behavior lives only in the component under test — never in prompts, the entrypoint skill, or fixture comments.

## One Probe Per Prompt Boundary

Surfaces that only exist across turn boundaries (and interference between probes) require a stepped loop with an operator "next," not a single mega-prompt. Hooks are the deliberate exception: one step aggregates many events from an accumulated log.
