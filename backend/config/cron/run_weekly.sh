#!/bin/bash
set -euo pipefail

export JJ_INTEL_MAC_WEEKLY_RUN="true"
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

PROJECT_ROOT="/Users/jeremyjacob/Documents/Coding Projects/Kartiseret/NewScraping-August2025"
PYTHON="$PROJECT_ROOT/venv/bin/python"
cd "$PROJECT_ROOT"

"$PYTHON" -u -m backend.config.runner "$@"
