# /// script
# requires-python = ">=3.10"
# ///
"""L1 probe LSP server: write work/observations/lsp.launched on initialize."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
MARKER_NAME = "lsp.launched"


def resolve_work_root() -> Path:
    """Return CONFORMANCE_WORK override or default $PLUGIN_ROOT/work."""
    override = os.environ.get("CONFORMANCE_WORK")
    if override:
        return Path(override).resolve()
    return (PLUGIN_ROOT / "work").resolve()


def write_launch_marker(work: Path) -> Path:
    """Create ``work/observations/lsp.launched`` and return its path."""
    marker = work / "observations" / MARKER_NAME
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("launched\n", encoding="utf-8")
    return marker


def _read_message() -> dict[str, object] | None:
    headers: dict[str, str] = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        key, _, value = line.decode("utf-8").partition(":")
        headers[key.strip().lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    body = sys.stdin.buffer.read(length)
    return json.loads(body.decode("utf-8"))


def _write_message(msg: dict[str, object]) -> None:
    raw = json.dumps(msg).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii"))
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.flush()


def main() -> None:
    """Serve a minimal stdio LSP that records launch on initialize."""
    work = resolve_work_root()
    while True:
        msg = _read_message()
        if msg is None:
            break
        method = msg.get("method")
        mid = msg.get("id")
        if method == "initialize":
            write_launch_marker(work)
            _write_message(
                {
                    "jsonrpc": "2.0",
                    "id": mid,
                    "result": {
                        "capabilities": {},
                        "serverInfo": {"name": "probe-lsp", "version": "0.1.0"},
                    },
                }
            )
        elif method == "initialized":
            continue
        elif method == "shutdown":
            _write_message({"jsonrpc": "2.0", "id": mid, "result": None})
        elif method == "exit":
            break


if __name__ == "__main__":
    main()
