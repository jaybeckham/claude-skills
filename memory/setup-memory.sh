#!/usr/bin/env bash
# Install shared Claude/Codex memory. Local continuity needs only Python 3.10+.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
for candidate in python3 python3.14 python3.13 python3.12 python3.11 python3.10; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
        exec "$candidate" "$SCRIPT_DIR/scripts/setup_memory.py" --source "$SCRIPT_DIR" "$@"
    fi
done
echo 'Python 3.10+ is required to install local memory.' >&2
exit 1
