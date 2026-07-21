#!/usr/bin/env python3
"""Observe-not-judge check harness for open-plugins conformance probes.

CLI modes:
  scripts/check.py <step>     Observe a single step (1–11), append JSONL, exit 0
  scripts/check.py --summary  Render capability table from recorded observations

Steps 1–8 have real observers (Scots flag, JS/Python indent create/edit,
R4 closing-line sentinel, S1/A1 token presence); steps 9–11 still use stubs
that return observed=false with detail "probe checker not implemented".
Exit non-zero only on infrastructure errors — never on not observed / skipped.
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


def observe_stub(step: int, work: Path) -> ObservationResult:
    """Placeholder observer until probe-specific checkers land."""
    return {"observed": False, "detail": "probe checker not implemented"}


def _entry(
    surface: str,
    mode: str,
    probe: str,
    path: str,
    observe: Observer = observe_stub,
) -> dict[str, Any]:
    return {
        "surface": surface,
        "mode": mode,
        "probe": probe,
        "path": path,
        "observe": observe,
    }


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
    9: _entry("hooks", "events", "h1-hooks-battery", "aggregate"),
    10: _entry("mcp", "server", "m1-probe-mcp", "create"),
    11: _entry("lsp", "server", "l1-probe-lsp", "launched"),
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
