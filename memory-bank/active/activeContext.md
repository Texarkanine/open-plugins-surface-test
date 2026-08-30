# Active Context

## Current Task: plugintest-cwd-work
**Phase:** QA - COMPLETE (PASS)

## Files created or modified
- `/Users/tex/git/open-plugins-surface-test/scripts/work_root.py` (new)
- `/Users/tex/git/open-plugins-surface-test/tests/test_work_root.py` (new)
- `/Users/tex/git/open-plugins-surface-test/scripts/setup.sh`
- `/Users/tex/git/open-plugins-surface-test/scripts/hook_record.sh`
- `/Users/tex/git/open-plugins-surface-test/scripts/check.py`
- `/Users/tex/git/open-plugins-surface-test/servers/probe_lsp.py`
- `/Users/tex/git/open-plugins-surface-test/tests/test_l1_lsp.py`
- `/Users/tex/git/open-plugins-surface-test/tests/test_setup.py`
- `/Users/tex/git/open-plugins-surface-test/tests/test_h1_hooks.py`
- `/Users/tex/git/open-plugins-surface-test/tests/test_check.py`
- `/Users/tex/git/open-plugins-surface-test/tests/test_plugin_skeleton.py`
- `/Users/tex/git/open-plugins-surface-test/.gitignore`
- `/Users/tex/git/open-plugins-surface-test/prompts/*.md`
- `/Users/tex/git/open-plugins-surface-test/skills/conformance-run/SKILL.md`
- `/Users/tex/git/open-plugins-surface-test/skills/build-stamp/SKILL.md`
- `/Users/tex/git/open-plugins-surface-test/agents/listing-auditor.md`
- `/Users/tex/git/open-plugins-surface-test/README.md`
- `/Users/tex/git/open-plugins-surface-test/DESIGN.md`
- `/Users/tex/git/open-plugins-surface-test/memory-bank/techContext.md`

## Key decisions
- Shared resolver `scripts/work_root.py` with CLI `ensure`; bash callers capture its stdout as `WORK_DIR`.
- `check.py` and `probe_lsp.py` insert `scripts/` on `sys.path` before `import work_root` because tests load those files via importlib without adding the script dir.
- Unset-override tests chdir to `tmp_path` and isolate `$PLUGIN_ROOT/.conformance-work` so they do not create `plugintest/` in the repo or leak a pointer across tests.
- Entrypoint skill addresses plugin scripts via `$PLUGIN_ROOT` and keeps `pwd` as the launch workspace.

## Deviations
None — built to plan. Preflight advisory (`work_root.py status`, e2e smoke without override) not implemented.

## Next Step
QA passed — proceed to `/niko-reflect`
