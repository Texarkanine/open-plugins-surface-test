---
task_id: anti-remediation-framing
date: 2026-09-01
complexity_level: 2
---

# Reflection: Anti-Remediation Framing

## Summary

Added explicit harness-testing and anti-remediation framing to `skills/conformance-run/SKILL.md` to prevent driving models from reflexively reverse-engineering check expectations or editing artifacts post-check. The implementation succeeded and passed all test and lint suites without regressions.

## Requirements vs Outcome

Delivered all requested items: opening framing explaining that the exercises evaluate the harness rather than the model and that `not observed` is a normal, valid measurement outcome; simplified Step 2 constraints stating single execution and no post-check artifact editing; adhered strictly to Orwell's 6 rules for writing and prompt-authoring principles without negative priming or mention of `scripts/check.py`.

## Plan Accuracy

The plan was accurate in scope and classification as a prose/policy artifact. During execution, the operator explicitly refined the Step 2 wording to omit mention of reverse-engineering or opening checker scripts, avoiding negative priming.

## Build & QA Observations

The build was clean and passed all 182 pytest cases including sentinel leakage and observational vocabulary lints. A race condition occurred during QA when an asynchronous subagent completed after an operator refinement, which was clarified and resolved cleanly.

## Insights

### Technical
- Mentioning prohibited actions explicitly (e.g. "do not open scripts/check.py to reverse-engineer expectations") can act as negative priming for instruction-following models. Stating direct imperative constraints ("Run each check only once. Do not edit artifacts after running a check.") is cleaner and avoids suggesting the very action to avoid.

### Process
- When an operator provides real-time refinements to a skill prompt during a turn, synchronous handling avoids background subagent collisions.

### Million-Dollar Question

Framing the entire test session upfront as a collaborative evaluation of the environment ("we are testing the harness together") addresses the core RLHF reward hacking instinct across all steps simultaneously, rather than trying to patch individual tool behaviors.
