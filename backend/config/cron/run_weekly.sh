#!/bin/bash
set -euo pipefail

export JJ_INTEL_MAC_WEEKLY_RUN="true"
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export GIT_SSH_COMMAND="ssh -i /Users/jeremyjacob/.ssh/id_ed25519_kartiseret -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"

PROJECT_ROOT="/Users/jeremyjacob/Documents/Coding Projects/Kartiseret/NewScraping-August2025"
PYTHON="$PROJECT_ROOT/venv/bin/python"
ARTIFACT_DIR="$PROJECT_ROOT/backend/utils/log/logger_artifacts"
LOG_DIR="$PROJECT_ROOT/backend/config/cron/run_weekly_logs"

cd "$PROJECT_ROOT"

TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
LOG_FILE="$LOG_DIR/cron_weekly_${TIMESTAMP}.log"
mkdir -p "$LOG_DIR"

# --------------------
# Phase 1: run everything and write output to the log (and terminal)
# --------------------
run_phase() {
  echo "==== cron run start: $(date '+%Y-%m-%dT%H:%M:%S%z') ===="

  # Sync code (robust even if main was force-pushed)
  git fetch origin main
  git checkout main
  git reset --hard origin/main
  git clean -fd -e backend/config/cron/

  # Run the job
  "$PYTHON" -u -m backend.config.runner "$@"

  echo "==== cron run end: $(date '+%Y-%m-%dT%H:%M:%S%z') ===="
}

# Capture ALL output of the run phase. After this returns, the log file is DONE being written.
run_phase "$@" 2>&1 | tee "$LOG_FILE"

# --------------------
# Phase 2: git add/commit/rebase/push (NO tee running now)
# --------------------

# Stage artifacts and the log
if [[ -d "$ARTIFACT_DIR" ]]; then
  git add "$ARTIFACT_DIR"
fi
git add "$LOG_FILE"

# If nothing staged, we’re done
if git diff --cached --quiet; then
  exit 0
fi

git commit -m "[W-RUN] weekly artifacts and log $(date +%Y-%m-%d_%H-%M-%S)"

# Update again in case main moved while the job ran, then push
git fetch origin main
git rebase origin/main
git push origin main
