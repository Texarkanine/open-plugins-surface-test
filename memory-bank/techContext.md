# Tech Context

Greenfield open-plugins conformance instrument: shell setup, Python checkers, and small PEP 723 inline-script servers launched with `uv`. Product shape and probe matrix are defined in `DESIGN.md`.

## Environment Setup

- POSIX shell and core Unix utilities for `scripts/setup.sh` and hook recorders.
- `scripts/setup.sh` resets `work/artifacts/` and regenerates `work/fixtures/`; it never touches `work/observations/`. Optional `CONFORMANCE_WORK` overrides the work root (defaults to `$PLUGIN_ROOT/work`).
- `uv` required for MCP/LSP probe servers (`uv run --script`). Absence is a skip, not a false negative — see design challenges in `DESIGN.md`.
- Target harness loads this plugin by adding the git repo as a marketplace (`.claude-plugin/marketplace.json`, `.cursor-plugin/marketplace.json`); vendor-neutral identity remains `.plugin/plugin.json`. Harness-native `plugin.json` files beside those catalogs must lockstep `name`/`version`/`description` with `.plugin/plugin.json` (enforced by `tests/test_marketplace.py`).

## Build Tools

- No application build pipeline yet; deliverable is the plugin tree plus `scripts/`.
- MCP/LSP servers are single-file PEP 723 scripts (deps in the script header), not a packaged Python project, unless a server outgrows one file.

## Testing Process

- Repo self-checks: `uv run pytest` (pytest as a `uv` dev dependency in `pyproject.toml`; tests under `tests/`).
- Runtime capability checks are observation recorders (`scripts/check.py`), not a pass/fail unit suite — keep those separate from pytest.
- Prefer testing only load-bearing logic/contracts; skip prompts, prose, and trivial helpers.
