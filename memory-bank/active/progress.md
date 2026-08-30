# Progress

Move conformance run scratch from `$PLUGIN_ROOT/work` to `$PWD/plugintest/<UTC-datestamp>/` (with `CURRENT`) so workspace-sandboxed writes stay in the launch cwd. Keep `CONFORMANCE_WORK` as the test/operator override. Preserve the setup reset boundary.

**Complexity:** Level 2

## 2026-08-30 - COMPLEXITY-ANALYSIS - COMPLETE

* Work completed
    - Intent approved: cwd `plugintest/<stamp>/` + `CURRENT`; not plugin-cache `work/`.
    - Classified Level 2 (work-root subsystem; multiple callers, one layout).
* Decisions made
    - Opaque `mktemp` names are not the run identity; dated dir plus `CURRENT` is.
    - `CONFORMANCE_WORK` remains the override.
* Insights
    - LSP may not share workspace `pwd`; plan must cover a pointer so `lsp.launched` lands in the same run dir.

## 2026-08-30 - PLAN - COMPLETE

* Work completed
    - Wrote Level 2 plan: shared `work_root.py`, caller wiring, workspace-relative prompts/skill, gitignore, docs.
* Decisions made
    - `$PLUGIN_ROOT/.conformance-work` is a one-line absolute pointer for LSP, not the run tree.
    - CURRENT symlink target is the relative stamp directory.
    - Entrypoint skill must not `cd` to plugin root for the run.
* Insights
    - If setup's process cwd is the cache, CURRENT would be created there again; skill wording is load-bearing.

## 2026-08-30 - PLAN - COMPLETE (re-plan after preflight FAIL fixable)

* Work completed
    - Unit 2 now requires `check.py` to insert its directory on `sys.path` before `import work_root` (importlib test loader does not).
    - CLI `ensure` pinned as `create=True`. Unit 3 remains prose/policy.
* Decisions made
    - Same `sys.path` treatment for `check.py` as for `probe_lsp.py`.

## 2026-08-30 - PLAN - COMPLETE (second re-plan)

* Work completed
    - Unit 2 stub tests now include importlib-loaded `check.py` with `CONFORMANCE_WORK` unset resolving cwd `plugintest/CURRENT`.
* Decisions made
    - Encode `check.py` default resolve in the TDD steps, not only `work_root.py` unit tests.
* Insights
    - Cross-process setup/hook/check integration test left advisory.

## 2026-08-30 - PREFLIGHT - COMPLETE (FAIL (fixable))

* Work completed
    - Verified plan touchpoints against codebase ground truth (all `scripts/`, `tests/`, `prompts/`, skills, docs named in the plan).
    - Struck a scheduled change-detector test in Unit 3 (prompt/skill wording grep assertions) and relabeled that unit `prose/policy`; removed its `tests/test_work_root.py` file reference.
* Decisions made
    - Unit 3 owes no tests (operator-facing prose/skill wording, out of scope per `always-tdd.mdc`).
* Insights
    - `check.py` and `probe_lsp.py` are both loaded in tests via `importlib.util.spec_from_file_location`, which does not add the loaded module's directory to `sys.path`. The plan gives `probe_lsp.py` an explicit cross-directory `sys.path` fix for importing `work_root` but omits the equivalent same-directory fix for `check.py` — this will raise `ModuleNotFoundError` under every existing test that loads `check.py`. Routed back to plan.

## 2026-08-30 - PREFLIGHT - COMPLETE (FAIL (fixable))

* Work completed
    - Revalidated the re-planned work-root migration against the present scripts, tests, prompts, skills, documentation, and gitignore.
    - Confirmed that the revised shared-resolver import handling and CLI creation semantics address the prior preflight finding.
* Decisions made
    - The plan must add an explicit test for `check.py` resolving the default shared cwd run when `CONFORMANCE_WORK` is unset.
* Insights
    - Unit 2 specifies `check.py` delegation as executable behavior but schedules caller tests only for setup, hook recorder, and LSP; without a direct check.py test, an implementer can satisfy all numbered tests while omitting or breaking that delegation.

## 2026-08-30 - PREFLIGHT - COMPLETE (PASS WITH ADVISORY)

* Work completed
    - Revalidated the updated implementation plan (Unit 2 check.py test added, TDD sequencing verified across all units).
    - Verified convention compliance, dependency touchpoints, conflict avoidance, and completeness against project requirements.
* Decisions made
    - Plan passes preflight with advisory status.
* Insights
    - All executable units now strictly enforce test-first implementation steps, and import isolation for both `check.py` and `probe_lsp.py` is explicitly planned.

## 2026-08-30 - BUILD - COMPLETE

* Work completed
    - `scripts/work_root.py` resolves `CONFORMANCE_WORK`, then the install-tree pointer, then `plugintest/CURRENT`, else creates a UTC stamp dir with a relative `CURRENT` symlink.
    - Wired `setup.sh`, `hook_record.sh`, `check.py`, and `probe_lsp.py` to that resolver. Prompts/skills/agent/docs use `plugintest/CURRENT/...`. gitignore covers `plugintest/` and `.conformance-work`.
    - Full suite: 182 passed (`uv run pytest`).
* Decisions made
    - Unset-override tests isolate `.conformance-work` and chdir to tmp so the repo is not the launch cwd.
* Insights
    - `check.py` importlib loading still requires the `sys.path` insert; without it `import work_root` fails in every existing checker test.

## 2026-08-30 - QA - COMPLETE (PASS)

* Work completed
    - Reviewed the full build-phase diff (32 files) against `projectbrief.md`, `tasks.md`, and `systemPatterns.md`; cross-checked every Test Plan behavior against its implementing test; re-ran the full suite (182 passed).
* Decisions made
    - PASS with two advisories, neither blocking: duplicated `_without_plugin_pointer()` test helper (matches pre-existing per-file-helper convention in this suite) and the pointer-file test side effect on the real repo checkout (safe single-worker, would need isolation under xdist).
* Insights
    - The pointer-then-CURRENT precedence in `work_root.resolve_work_dir` intentionally lets a stale pointer from a prior cwd win over a fresh local `plugintest/CURRENT` — this matches the plan's diagram and is the mechanism that makes LSP-without-workspace-cwd work, not a defect.

## 2026-08-30 - REFLECT - COMPLETE

* Work completed
    - Reflection at `memory-bank/active/reflection/reflection-plugintest-cwd-work.md`.
    - Reconciled persistent files: `systemPatterns.md` (cwd-run assumption), `techContext.md` (`work_root.py` pointer).
* Decisions made
    - `productContext.md` skip — work-root location is an implementation contract, not a change to who the instrument serves.
* Insights
    - importlib script loading does not add the script directory to `sys.path`; that is why `check.py` must insert it before `import work_root`.

