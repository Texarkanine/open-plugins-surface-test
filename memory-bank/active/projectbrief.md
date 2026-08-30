# Project Brief

## User Story

As an operator, I want this repo to be addable as a Claude Code and Cursor marketplace (on the current git branch) so that I can install the existing open-plugins conformance plugin after local path install failed.

## Use-Case(s)

### Use-Case 1

Operator pushes this branch, adds `Texarkanine/open-plugins-surface-test` (this branch as ref) as a marketplace in Claude Code and Cursor, and can install the listed plugin from that catalog.

### Use-Case 2

The existing probe plugin (repo-root surfaces + `.plugin/plugin.json`) remains the thing installed; marketplace files only catalog it.

## Requirements

1. Add `.claude-plugin/marketplace.json` listing this repo's plugin.
2. Add `.cursor-plugin/marketplace.json` listing this repo's plugin.
3. Each marketplace catalog points at the existing plugin in this repository (not a new plugin tree).
4. Local path install is out of scope; git-branch marketplace add is the install path.

## Constraints

1. Do not restructure the probe plugin or move `rules/`, `skills/`, `agents/`, hooks, or servers.
2. Do not treat local `--plugin-dir` / path install as a success criterion.
3. Operator pushes and registers the branch in harnesses; this task does not require a live harness install to complete.

## Acceptance Criteria

1. `.claude-plugin/marketplace.json` exists at repo root and lists the existing plugin.
2. `.cursor-plugin/marketplace.json` exists at repo root and lists the existing plugin.
3. Source paths resolve to this repo's plugin (the current tree), not an external repo or a new subdirectory of probes.
4. Existing `.plugin/plugin.json` and probe surfaces are unchanged except as required for the marketplace entries to be valid.
