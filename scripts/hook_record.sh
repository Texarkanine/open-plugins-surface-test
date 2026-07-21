#!/usr/bin/env bash
# Append one hooks observation line to work/observations/hooks.jsonl.
#
# Usage: hook_record.sh <EventName>
# Optional: CONFORMANCE_WORK=/path/to/work overrides the default $PLUGIN_ROOT/work.
# Stdin (optional): host hook payload JSON; matcher_context is derived from it.
set -euo pipefail

if [[ $# -lt 1 || -z "${1:-}" ]]; then
    echo "usage: hook_record.sh <EventName>" >&2
    exit 1
fi

EVENT="$1"
PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="${CONFORMANCE_WORK:-$PLUGIN_ROOT/work}"
LOG_DIR="$WORK_DIR/observations"
LOG_FILE="$LOG_DIR/hooks.jsonl"

mkdir -p "$LOG_DIR"

# Host may pass JSON on stdin; tolerate empty or non-JSON payloads.
STDIN_DATA="$(cat || true)"

python3 - "$LOG_FILE" "$EVENT" "$STDIN_DATA" <<'PY'
import json
import sys
from datetime import datetime, timezone

path, event, raw = sys.argv[1], sys.argv[2], sys.argv[3]

matcher_context = "-"
if raw.strip():
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        matcher_context = raw[:200]
    else:
        if isinstance(data, dict):
            for key in ("matcher", "tool_name", "toolName", "tool"):
                value = data.get(key)
                if value is not None and value != "":
                    matcher_context = str(value)
                    break
            else:
                matcher_context = raw[:200]
        else:
            matcher_context = raw[:200]

record = {
    "event": event,
    "matcher_context": matcher_context,
    "ts": datetime.now(timezone.utc).isoformat(),
}
with open(path, "a", encoding="utf-8") as fh:
    fh.write(json.dumps(record, separators=(",", ":")) + "\n")
PY
