#!/usr/bin/env bash
# Shared Claude/Codex memory; installer substitutes safely quoted local paths.
set -euo pipefail
exec __PYTHON_COMMAND__ __RUNTIME_PATH__ load
