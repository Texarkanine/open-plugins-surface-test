"""Resolve the conformance run directory (cwd plugintest, not plugin install work/)."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path

SUITE_DIR = "plugintest"
CURRENT_NAME = "CURRENT"
POINTER_NAME = ".conformance-work"
STAMP_FORMAT = "%Y%m%dT%H%M%SZ"


def resolve_work_dir(
    *,
    create: bool,
    cwd: Path,
    plugin_root: Path,
    env: Mapping[str, str] | None = None,
) -> Path:
    """Return CONFORMANCE_WORK, existing CURRENT/pointer, or a newly created stamp dir."""
    environ = os.environ if env is None else env
    override = environ.get("CONFORMANCE_WORK")
    if override:
        return Path(override)

    pointer = plugin_root / POINTER_NAME
    if pointer.is_file():
        target = Path(pointer.read_text(encoding="utf-8").strip())
        if target.is_dir():
            return target.resolve()

    current = cwd / SUITE_DIR / CURRENT_NAME
    if current.exists():
        return current.resolve()

    if not create:
        raise FileNotFoundError(f"no conformance work dir under {cwd / SUITE_DIR}")

    stamp = datetime.now(timezone.utc).strftime(STAMP_FORMAT)
    run = cwd / SUITE_DIR / stamp
    run.mkdir(parents=True, exist_ok=True)
    suite = cwd / SUITE_DIR
    link = suite / CURRENT_NAME
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(stamp, target_is_directory=True)
    pointer.write_text(str(run.resolve()) + "\n", encoding="utf-8")
    return run.resolve()


def main(argv: list[str] | None = None) -> int:
    """CLI: ``ensure`` creates or reuses the run dir and prints its path."""
    args = sys.argv[1:] if argv is None else argv
    if args != ["ensure"]:
        print("usage: work_root.py ensure", file=sys.stderr)
        return 2
    plugin_root = Path(__file__).resolve().parent.parent
    work = resolve_work_dir(
        create=True, cwd=Path.cwd(), plugin_root=plugin_root, env=os.environ
    )
    print(work)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
