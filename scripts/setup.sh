#!/usr/bin/env bash
# Reset work/artifacts and regenerate work/fixtures; create work/run.json if absent.
# Never touches work/observations/.
#
# Usage: scripts/setup.sh
# Optional: CONFORMANCE_WORK=/path/to/work overrides the default $PLUGIN_ROOT/work.
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="${CONFORMANCE_WORK:-$PLUGIN_ROOT/work}"

mkdir -p "$WORK_DIR"

# Wipe artifacts (recreate empty directory for a clean write target).
rm -rf "$WORK_DIR/artifacts"
mkdir -p "$WORK_DIR/artifacts"

# Wipe and regenerate fixtures.
rm -rf "$WORK_DIR/fixtures"
mkdir -p "$WORK_DIR/fixtures"

cat > "$WORK_DIR/fixtures/fib.js" <<'EOF'
function fib(n) {
    if (n <= 1) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

module.exports = { fib };
EOF

cat > "$WORK_DIR/fixtures/fib.py" <<'EOF'
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
EOF

# Neutral matching file so harness LSP lifecycle can start the probe server.
: > "$WORK_DIR/fixtures/probe.lspprobe"

# Create run.json only when absent.
if [[ ! -f "$WORK_DIR/run.json" ]]; then
    if [[ -t 0 ]]; then
        printf "Harness label (e.g. cursor, claude-code) [unknown]: "
        read -r harness || true
        printf "Model label [unspecified]: "
        read -r model || true
    else
        IFS= read -r harness || true
        IFS= read -r model || true
    fi

    harness="${harness:-unknown}"
    model="${model:-unspecified}"
    os_name="$(uname -s 2>/dev/null || echo unknown)"
    if command -v uv >/dev/null 2>&1; then
        uv_version="$(uv --version 2>/dev/null || echo unavailable)"
    else
        uv_version="unavailable"
    fi

    # Minimal JSON without requiring jq.
    python3 - "$WORK_DIR/run.json" "$harness" "$model" "$os_name" "$uv_version" <<'PY'
import json
import sys

path, harness, model, os_name, uv_version = sys.argv[1:]
with open(path, "w", encoding="utf-8") as fh:
    json.dump(
        {
            "harness": harness,
            "model": model,
            "os": os_name,
            "uv_version": uv_version,
        },
        fh,
        indent=2,
    )
    fh.write("\n")
PY
fi
