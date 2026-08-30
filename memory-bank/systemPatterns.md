# System Patterns

## How This System Works

This repository is an open-plugins plugin plus a driver loop. The plugin embeds probes (rules, skills, agents, hooks, MCP/LSP servers). An entrypoint skill walks the operator through one prompt boundary per probe: follow a prompt, then run a checker that records whether the probe's fingerprint appeared in the expected artifact.

Two load-bearing assumptions dominate everything else:

1. **Observation over judgment.** Checkers append `observed` / `not observed` (or skip). Infrastructure errors may fail the process; a missing fingerprint must not.
2. **Reset boundary.** Setup may wipe fixtures and artifacts. It must never touch the observation log: SessionStart evidence is written before the entrypoint runs and cannot be regenerated in the same session.
3. **Run lives in the launch cwd.** `${PLUGIN_ROOT}` is the install tree (scripts, servers, prompts). The run — fixtures, artifacts, observations — is `$PWD/plugintest/<stamp>/` via `CURRENT`. Documenting artifact paths as relative to plugin root, or writing them into the install cache, makes workspace-sandboxed harnesses miss every checker. `CONFORMANCE_WORK` is the test/operator override; `$PLUGIN_ROOT/.conformance-work` is a pointer for processes whose cwd is not the workspace (LSP).

If any assumption is violated, the capability report is meaningless even when the rest of the suite looks correct.

## Probe → Prompt → Artifact

Every surface uses the same shape: a plugin component demands arbitrary behavior, a prompt provokes it, and an artifact either carries a fingerprint or does not. Demanded behavior lives only in the component under test — never in prompts, the entrypoint skill, or fixture comments.

## One Probe Per Prompt Boundary

Surfaces that only exist across turn boundaries (and interference between probes) require a stepped loop with an operator "next," not a single mega-prompt. Hooks are the deliberate exception: one step aggregates many events from an accumulated log.

## Create vs Edit Observation

Create-path checks look only at the artifact fingerprint. Edit-path checks require the fingerprint **and** that the artifact differs from the seeded fixture — otherwise a no-op turn can look like delivery. Rule frontmatter modes are mutually exclusive: do not combine `alwaysApply` with `globs` on one rule (`alwaysApply` subsumes).
