# Tech Context

Greenfield open-plugins conformance instrument: shell setup, Python checkers, and small PEP 723 inline-script servers launched with `uv`. Product shape and probe matrix are defined in `DESIGN.md`.

## Environment Setup

- POSIX shell and core Unix utilities for `scripts/setup.sh` and hook recorders.
- `uv` required for MCP/LSP probe servers (`uv run --script`). Absence is a skip, not a false negative — see design challenges in `DESIGN.md`.
- Target harness must load the plugin from this repo (vendor-neutral `.plugin/plugin.json` layout).

## Build Tools

- No application build pipeline yet; deliverable is the plugin tree plus `scripts/`.
- MCP/LSP servers are single-file PEP 723 scripts (deps in the script header), not a packaged Python project, unless a server outgrows one file.

## Testing Process

- Runtime checks are observation recorders (`scripts/check.py`), not a pass/fail unit suite.
- Repo self-checks planned around invariant enforcement (e.g. sentinel leakage lint over `prompts/` and the entrypoint skill). Exact CI wiring lives with whatever config lands in-repo.
