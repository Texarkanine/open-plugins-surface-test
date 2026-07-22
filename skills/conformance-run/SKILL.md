---
name: conformance-run
description: Operator-driven open-plugins conformance attended run — setup, stepped probes, and capability summary. Invoke only when the operator starts an attended conformance run.
disable-model-invocation: true
---

# Conformance Run

Drive one attended capability run for this plugin. Paths below are relative to the plugin root (the directory that contains `.plugin/`, `scripts/`, and `prompts/`). If your harness exposes `$PLUGIN_ROOT`, use that as the root.

This skill reports what was **observed**, **not observed**, or **skipped**. It does not judge harness support.

## 1. Setup

From the plugin root, run:

```bash
bash scripts/setup.sh
```

Answer the harness / model prompts. Setup resets fixtures and artifacts; it must not clear `work/observations/`.

## 2. Stepped probes

For each step below, in order:

1. Open the listed prompt file under `prompts/`.
2. Follow that prompt in this session (one probe boundary per step).
3. When the turn is done, run the matching check from the plugin root.
4. Tell the operator the check result using only **observed**, **not observed**, or **skipped** (plus any detail the checker printed).
5. Stop and wait for the operator to say **next** before continuing.

| Step | Prompt | Check |
| --- | --- | --- |
| 1 | `prompts/01-r1-cats.md` | `python scripts/check.py 1` |
| 2 | `prompts/02-r2-js-create.md` | `python scripts/check.py 2` |
| 3 | `prompts/03-r2-js-edit.md` | `python scripts/check.py 3` |
| 4 | `prompts/04-r3-py-create.md` | `python scripts/check.py 4` |
| 5 | `prompts/05-r3-py-edit.md` | `python scripts/check.py 5` |
| 6 | `prompts/06-r4-poem.md` | `python scripts/check.py 6` |
| 7 | `prompts/07-s1-stamp.md` | `python scripts/check.py 7` |
| 8 | `prompts/08-a1-audit.md` | `python scripts/check.py 8` |
| 9 | `prompts/09-h1-hooks-battery.md` | `python scripts/check.py 9` |
| 10 | `prompts/10-m1-mcp.md` | `python scripts/check.py 10` |
| 11 | `prompts/11-l1-lsp.md` | `python scripts/check.py 11` |

Do not open `scripts/check.py` to reverse-engineer expectations. Run it only after following the prompt for that step.

## 3. Summary

After step 11 and the operator's final **next** (or when they ask for the table), run:

```bash
python scripts/check.py --summary
```

Show the operator the full capability table. Rows may be marked **(discretionary)** — those soft **not observed** results often warrant a single-step re-run before drawing conclusions. The table may also include a SessionEnd line from the hooks log.
