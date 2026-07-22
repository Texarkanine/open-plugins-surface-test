#!/usr/bin/env python3
"""Observe-not-judge check harness for open-plugins conformance probes.

CLI modes:
  scripts/check.py <step>     Observe a single step (1–11), append JSONL, exit 0
  scripts/check.py --summary  Render capability table from recorded observations

Steps 1–11 have real observers (Scots flag, JS/Python indent create/edit,
R4 closing-line sentinel, S1/A1 token presence, H1 hooks event presence,
M1 MCP token / uv-skip, L1 LSP launch-marker / uv-skip). Summary also
prints a SessionEnd line from hooks.jsonl. Exit non-zero only on
infrastructure errors — never on not observed / skipped.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypedDict


class ObservationResult(TypedDict):
    """Return shape from a step observer callable."""

    observed: bool | None
    detail: str


Observer = Callable[[int, Path], ObservationResult]

PLUGIN_ROOT = Path(__file__).resolve().parent.parent

# Scotland flag emoji tag sequence (U+1F3F4 + gbsct tags + cancel).
SCOTS_FLAG = "\U0001f3f4\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f"


def contains_scots_flag(text: str) -> bool:
    """Return True if text contains the full Scotland flag tag sequence."""
    return SCOTS_FLAG in text


def indent_widths(source: str) -> set[int]:
    """Collect leading-space indent widths from non-blank lines.

    Blank lines are ignored. Leading ASCII spaces contribute their count when
    positive. A leading tab yields the marker ``-1`` (not a positive width).
    Semantics match ``tests/test_setup.py::_indent_widths``.
    """
    widths: set[int] = set()
    for line in source.splitlines():
        if not line.strip():
            continue
        if line.startswith("\t"):
            widths.add(-1)
            continue
        leading = len(line) - len(line.lstrip(" "))
        if leading:
            widths.add(leading)
    return widths


def indent_multiples_of(widths: set[int], n: int) -> bool:
    """Return True if widths is non-empty and every positive width is a multiple of n.

    The tab marker ``-1`` makes the set non-compliant. An empty set is not
    observed (nothing to credit).
    """
    if not widths:
        return False
    if -1 in widths:
        return False
    return all(width % n == 0 for width in widths)


def format_indent_widths_detail(widths: set[int]) -> str:
    """Format indent detail as ``indent widths seen: […]`` (sorted unique positives)."""
    positives = sorted(width for width in widths if width > 0)
    return f"indent widths seen: [{', '.join(str(w) for w in positives)}]"


def file_modified(artifact: Path, fixture: Path) -> bool:
    """Return True when artifact exists and its text differs from fixture text.

    Missing artifact → False. Equal content → False. Different content → True.
    """
    if not artifact.is_file():
        return False
    if not fixture.is_file():
        return True
    return artifact.read_text(encoding="utf-8") != fixture.read_text(encoding="utf-8")


def observe_r1_scots(_step: int, work: Path) -> ObservationResult:
    """Observe whether work/artifacts/cats.md carries the Scotland flag fingerprint."""
    artifact = work / "artifacts" / "cats.md"
    if not artifact.is_file():
        return {"observed": False, "detail": "cats.md not found"}
    text = artifact.read_text(encoding="utf-8")
    if contains_scots_flag(text):
        return {"observed": True, "detail": "scottish flag present"}
    return {"observed": False, "detail": "scottish flag not present"}


def observe_indent_create(
    _step: int,
    work: Path,
    *,
    relative: str,
    n: int,
) -> ObservationResult:
    """Observe create-path indent fingerprint for ``work/artifacts/<relative>``.

    Missing artifact → not observed. Empty or non-compliant widths for ``n`` →
    not observed with indent detail. Compliant multiples of ``n`` → observed.
    """
    name = Path(relative).name
    artifact = work / "artifacts" / relative
    if not artifact.is_file():
        return {"observed": False, "detail": f"{name} not found"}
    widths = indent_widths(artifact.read_text(encoding="utf-8"))
    detail = format_indent_widths_detail(widths)
    if indent_multiples_of(widths, n):
        return {"observed": True, "detail": detail}
    return {"observed": False, "detail": detail}


def observe_indent_edit(
    _step: int,
    work: Path,
    *,
    relative: str,
    n: int,
) -> ObservationResult:
    """Observe edit-path indent fingerprint plus file-modified vs fixture seed.

    ``observed`` is true only when the artifact differs from
    ``work/fixtures/<relative>`` and indent widths are multiples of ``n``.
    Detail always includes indent widths and ``file_modified: true|false``.
    """
    name = Path(relative).name
    artifact = work / "artifacts" / relative
    fixture = work / "fixtures" / relative
    if not artifact.is_file():
        return {
            "observed": False,
            "detail": f"{name} not found; file_modified: false",
        }
    modified = file_modified(artifact, fixture)
    widths = indent_widths(artifact.read_text(encoding="utf-8"))
    indent_detail = format_indent_widths_detail(widths)
    modified_detail = f"file_modified: {'true' if modified else 'false'}"
    detail = f"{indent_detail}; {modified_detail}"
    observed = modified and indent_multiples_of(widths, n)
    return {"observed": observed, "detail": detail}


def observe_r2_js_create(step: int, work: Path) -> ObservationResult:
    """Step 2: observe ``reverse.js`` for multiples of 7."""
    return observe_indent_create(step, work, relative="reverse.js", n=7)


def observe_r2_js_edit(step: int, work: Path) -> ObservationResult:
    """Step 3: observe ``fib.js`` edit path (modified + multiples of 7)."""
    return observe_indent_edit(step, work, relative="fib.js", n=7)


def observe_r3_py_create(step: int, work: Path) -> ObservationResult:
    """Step 4: observe ``strrev.py`` for multiples of 5."""
    return observe_indent_create(step, work, relative="strrev.py", n=5)


def observe_r3_py_edit(step: int, work: Path) -> ObservationResult:
    """Step 5: observe ``fib.py`` edit path (modified + multiples of 5)."""
    return observe_indent_edit(step, work, relative="fib.py", n=5)


SEA_POEM_SENTINEL = "SEA-POEM-OBSERVED"
BUILD_STAMP_TOKEN = "BUILD-STAMP-OBSERVED"
LISTING_AUDITOR_TOKEN = "LISTING-AUDITOR-OBSERVED"
MCP_CATS_TOKEN = "MCP-OBSERVED-cats"


def uv_unavailable(work: Path) -> bool:
    """Return True when ``run.json`` reports uv as unavailable.

    Uses the same default as ``render_summary``: a missing ``uv_version`` key
    is treated as ``"unavailable"``. Caller must ensure ``run.json`` exists
    and is valid JSON (as ``observe_step`` / ``ensure_run_id`` already require).
    """
    with (work / "run.json").open(encoding="utf-8") as fh:
        header = json.load(fh)
    return header.get("uv_version", "unavailable") == "unavailable"


def last_nonempty_line(text: str) -> str:
    """Return the last non-empty line of text, stripped; else an empty string."""
    for line in reversed(text.splitlines()):
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def artifact_contains(path: Path, token: str) -> bool:
    """Return True when path exists and its text contains token."""
    if not path.is_file():
        return False
    return token in path.read_text(encoding="utf-8")


def closing_line_equals(path: Path, sentinel: str) -> bool:
    """Return True when path exists and its last non-empty line equals sentinel."""
    if not path.is_file():
        return False
    return last_nonempty_line(path.read_text(encoding="utf-8")) == sentinel


def observe_r4_sea_poem(_step: int, work: Path) -> ObservationResult:
    """Step 6: observe ``poem.txt`` closing line equals SEA-POEM-OBSERVED."""
    artifact = work / "artifacts" / "poem.txt"
    if not artifact.is_file():
        return {"observed": False, "detail": "poem.txt not found"}
    if closing_line_equals(artifact, SEA_POEM_SENTINEL):
        return {"observed": True, "detail": "closing line sentinel present"}
    return {"observed": False, "detail": "closing line sentinel not present"}


def observe_s1_build_stamp(_step: int, work: Path) -> ObservationResult:
    """Step 7: observe ``stamp.txt`` contains BUILD-STAMP-OBSERVED."""
    artifact = work / "artifacts" / "stamp.txt"
    if not artifact.is_file():
        return {"observed": False, "detail": "stamp.txt not found"}
    if artifact_contains(artifact, BUILD_STAMP_TOKEN):
        return {"observed": True, "detail": "build stamp token present"}
    return {"observed": False, "detail": "build stamp token not present"}


def observe_a1_listing_auditor(_step: int, work: Path) -> ObservationResult:
    """Step 8: observe ``agent.txt`` contains LISTING-AUDITOR-OBSERVED."""
    artifact = work / "artifacts" / "agent.txt"
    if not artifact.is_file():
        return {"observed": False, "detail": "agent.txt not found"}
    if artifact_contains(artifact, LISTING_AUDITOR_TOKEN):
        return {"observed": True, "detail": "listing auditor token present"}
    return {"observed": False, "detail": "listing auditor token not present"}


# DESIGN step-9 mid-run catalog (SessionEnd is summary-only).
SESSION_END_EVENT = "SessionEnd"
MID_RUN_HOOK_EVENTS: tuple[str, ...] = (
    "SessionStart",
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "BeforeReadFile",
    "AfterFileEdit",
    "BeforeShellExecution",
    "AfterShellExecution",
    "Stop",
    "SubagentStart",
    "SubagentStop",
)


def hooks_log_path(work: Path) -> Path:
    """Return ``work/observations/hooks.jsonl``."""
    return work / "observations" / "hooks.jsonl"


def event_names_from_hooks_jsonl(path: Path) -> set[str]:
    """Collect distinct ``event`` string values from a hooks JSONL log.

    Missing files yield an empty set. Blank lines and malformed JSON lines are
    skipped (tolerant parse — never raises for bad line content).
    OSError from reading an existing path propagates to the caller.
    """
    if not path.is_file():
        return set()
    names: set[str] = set()
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        event = row.get("event")
        if isinstance(event, str) and event:
            names.add(event)
    return names


def format_hook_events_detail(present: set[str]) -> str:
    """Format mid-run hook presence as ``Name=present|absent`` in catalog order."""
    parts: list[str] = []
    for name in MID_RUN_HOOK_EVENTS:
        marker = "present" if name in present else "absent"
        parts.append(f"{name}={marker}")
    return " ".join(parts)


def observe_h1_hooks(_step: int, work: Path) -> ObservationResult:
    """Step 9: observe per-event presence of mid-run hooks in hooks.jsonl.

    SessionEnd is excluded from ``observed`` / detail (reported by summary).
    Any mid-run event present → observed=true; incomplete sets are fine.
    """
    path = hooks_log_path(work)
    if not path.is_file():
        return {"observed": False, "detail": "hooks.jsonl not found"}
    try:
        present = event_names_from_hooks_jsonl(path)
    except OSError:
        return {"observed": False, "detail": "hooks.jsonl not readable"}
    mid_present = {name for name in present if name in MID_RUN_HOOK_EVENTS}
    detail = format_hook_events_detail(present)
    if not mid_present:
        return {"observed": False, "detail": detail}
    return {"observed": True, "detail": detail}


def observe_m1_mcp(_step: int, work: Path) -> ObservationResult:
    """Step 10: observe ``mcp.txt`` for MCP-OBSERVED-cats, or skip if uv absent.

    Skip when ``run.json`` uv_version is unavailable (or missing). Otherwise
    look for the cats fingerprint substring in ``work/artifacts/mcp.txt``.
    """
    if uv_unavailable(work):
        return {"observed": None, "detail": "skipped: uv not found"}
    artifact = work / "artifacts" / "mcp.txt"
    if not artifact.is_file():
        return {"observed": False, "detail": "mcp.txt not found"}
    if artifact_contains(artifact, MCP_CATS_TOKEN):
        return {"observed": True, "detail": "mcp token present"}
    return {"observed": False, "detail": "mcp token not present"}


def observe_l1_lsp(_step: int, work: Path) -> ObservationResult:
    """Step 11: observe ``lsp.launched`` marker, or skip if uv absent.

    Skip when ``run.json`` uv_version is unavailable (or missing). Otherwise
    look for ``work/observations/lsp.launched`` (server-written on initialize).
    """
    if uv_unavailable(work):
        return {"observed": None, "detail": "skipped: uv not found"}
    marker = work / "observations" / "lsp.launched"
    if not marker.is_file():
        return {"observed": False, "detail": "lsp.launched not found"}
    return {"observed": True, "detail": "lsp.launched marker present"}


def observe_stub(step: int, work: Path) -> ObservationResult:
    """Placeholder observer until probe-specific checkers land."""
    return {"observed": False, "detail": "probe checker not implemented"}


def _entry(
    surface: str,
    mode: str,
    probe: str,
    path: str,
    observe: Observer = observe_stub,
    claim: str | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "surface": surface,
        "mode": mode,
        "probe": probe,
        "path": path,
        "observe": observe,
    }
    if claim is not None:
        entry["claim"] = claim
    return entry


STEP_REGISTRY: dict[int, dict[str, Any]] = {
    1: _entry(
        "rules",
        "alwaysApply",
        "r1-global-scots",
        "create",
        observe=observe_r1_scots,
    ),
    2: _entry(
        "rules",
        "alwaysApply",
        "r2-js-indent",
        "create",
        observe=observe_r2_js_create,
    ),
    3: _entry(
        "rules",
        "alwaysApply",
        "r2-js-indent",
        "edit",
        observe=observe_r2_js_edit,
    ),
    4: _entry(
        "rules",
        "globs",
        "r3-py-indent",
        "create",
        observe=observe_r3_py_create,
    ),
    5: _entry(
        "rules",
        "globs",
        "r3-py-indent",
        "edit",
        observe=observe_r3_py_edit,
    ),
    6: _entry(
        "rules",
        "description",
        "r4-sea-poem",
        "create",
        observe=observe_r4_sea_poem,
    ),
    7: _entry(
        "skills",
        "description",
        "s1-build-stamp",
        "create",
        observe=observe_s1_build_stamp,
    ),
    8: _entry(
        "agents",
        "description",
        "a1-listing-auditor",
        "create",
        observe=observe_a1_listing_auditor,
    ),
    9: _entry(
        "hooks",
        "events",
        "h1-hooks-battery",
        "aggregate",
        observe=observe_h1_hooks,
    ),
    10: _entry(
        "mcp",
        "server",
        "m1-probe-mcp",
        "create",
        observe=observe_m1_mcp,
    ),
    11: _entry(
        "lsp",
        "server",
        "l1-probe-lsp",
        "launched",
        observe=observe_l1_lsp,
        claim="launched",
    ),
}


def resolve_work_dir() -> Path:
    """Return CONFORMANCE_WORK override or default $PLUGIN_ROOT/work."""
    override = os.environ.get("CONFORMANCE_WORK")
    if override:
        return Path(override)
    return PLUGIN_ROOT / "work"


def ensure_run_id(run_json_path: Path) -> str:
    """Read run.json; add run_id if missing; return the run_id."""
    with run_json_path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    run_id = data.get("run_id")
    if not run_id:
        run_id = str(uuid.uuid4())
        data["run_id"] = run_id
        with run_json_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
    return str(run_id)


def append_observation(work: Path, record: dict[str, Any]) -> None:
    """Append one JSON object as a line to work/observations/run.jsonl."""
    observations = work / "observations"
    observations.mkdir(parents=True, exist_ok=True)
    path = observations / "run.jsonl"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _status_phrase(observed: bool | None) -> str:
    if observed is True:
        return "observed"
    if observed is False:
        return "not observed"
    return "skipped"


def _status_emoji(observed: bool | None) -> str:
    if observed is True:
        return "✅ observed"
    if observed is False:
        return "❌ not observed"
    return "⊘ skipped"


def observe_step(step: int, work: Path) -> int:
    """Run stub/registry observe for step, append JSONL, print status, return exit code."""
    if not work.is_dir():
        print(f"error: work directory does not exist: {work}", file=sys.stderr)
        return 1

    run_json = work / "run.json"
    if not run_json.is_file():
        print(f"error: missing run.json in {work}", file=sys.stderr)
        return 1

    meta = STEP_REGISTRY.get(step)
    if meta is None:
        print(f"error: unknown step {step}; expected 1–11", file=sys.stderr)
        return 1

    try:
        run_id = ensure_run_id(run_json)
        observer: Observer = meta["observe"]
        result = observer(step, work)
        record = {
            "run_id": run_id,
            "step": step,
            "surface": meta["surface"],
            "mode": meta["mode"],
            "probe": meta["probe"],
            "path": meta["path"],
            "observed": result["observed"],
            "detail": result["detail"],
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        if "claim" in meta:
            record["claim"] = meta["claim"]
        append_observation(work, record)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(_status_phrase(result["observed"]))
    return 0


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        records.append(json.loads(line))
    return records


def session_end_summary_line(work: Path) -> str:
    """Observational SessionEnd status from hooks.jsonl (missing/unreadable → not observed)."""
    try:
        present = event_names_from_hooks_jsonl(hooks_log_path(work))
    except OSError:
        present = set()
    return f"SessionEnd: {_status_emoji(SESSION_END_EVENT in present)}"


def render_summary(work: Path) -> int:
    """Load run.json + JSONL and print capability table; return exit code."""
    if not work.is_dir():
        print(f"error: work directory does not exist: {work}", file=sys.stderr)
        return 1

    run_json = work / "run.json"
    if not run_json.is_file():
        print(f"error: missing run.json in {work}", file=sys.stderr)
        return 1

    try:
        with run_json.open(encoding="utf-8") as fh:
            header = json.load(fh)
        records = _load_jsonl(work / "observations" / "run.jsonl")
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    harness = header.get("harness", "unknown")
    model = header.get("model", "unspecified")
    os_name = header.get("os", "unknown")
    uv_version = header.get("uv_version", "unavailable")

    print(f"Harness: {harness}")
    print(f"Model:   {model}")
    print(f"OS:      {os_name}")
    print(f"uv:      {uv_version}")
    print()

    if not records:
        print("(no observations recorded)")
        print()
        print(session_end_summary_line(work))
        return 0

    # One row per step that has a JSONL record (latest wins if re-checked).
    by_step: dict[int, dict[str, Any]] = {}
    for record in records:
        by_step[int(record["step"])] = record

    headers = ("step", "surface", "mode", "probe", "path", "status")
    rows: list[tuple[str, ...]] = []
    for step in sorted(by_step):
        rec = by_step[step]
        rows.append(
            (
                str(step),
                str(rec.get("surface", "")),
                str(rec.get("mode", "")),
                str(rec.get("probe", "")),
                str(rec.get("path", "")),
                _status_emoji(rec.get("observed")),
            )
        )

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt(cells: tuple[str, ...]) -> str:
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    print(fmt(headers))
    print(fmt(tuple("-" * w for w in widths)))
    for row in rows:
        print(fmt(row))
    print()
    print(session_end_summary_line(work))
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse args and dispatch to step mode or --summary."""
    args = list(sys.argv[1:] if argv is None else argv)
    work = resolve_work_dir()

    if len(args) != 1:
        print(
            "usage: check.py <step>|--summary\n"
            "  <step>      integer step in 1–11\n"
            "  --summary   render capability table",
            file=sys.stderr,
        )
        return 1

    arg = args[0]
    if arg == "--summary":
        return render_summary(work)

    if arg.startswith("-"):
        print(f"error: unknown flag: {arg}", file=sys.stderr)
        return 1

    try:
        step = int(arg)
    except ValueError:
        print(f"error: step must be an integer, got {arg!r}", file=sys.stderr)
        return 1

    if step not in STEP_REGISTRY:
        print(f"error: unknown step {step}; expected 1–11", file=sys.stderr)
        return 1

    return observe_step(step, work)


if __name__ == "__main__":
    raise SystemExit(main())
