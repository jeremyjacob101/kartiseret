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

# Write output to log AND also to stdout
exec > >(tee -a "$LOG_FILE") 2>&1

echo "==== cron run start: $(date '+%Y-%m-%dT%H:%M:%S%z') ===="

# 1) Sync code (safe even if main was force-pushed)
git fetch origin main
git checkout main
git reset --hard origin/main
git clean -fd -e backend/config/cron/

# 2) Run the job
"$PYTHON" -u -m backend.config.runner "$@"

# 3) Stage artifacts + log AFTER all output has been written
if [[ -d "$ARTIFACT_DIR" ]]; then
  git add "$ARTIFACT_DIR"
fi
git add "$LOG_FILE"

if ! git diff --cached --quiet; then
  git commit -m "[W-RUN] weekly artifacts and log $(date +%Y-%m-%d_%H-%M-%S)"

  # Rebase/push only after ensuring there are no local changes
  git fetch origin main
  git rebase origin/main
  git push origin main
fi

echo "==== cron run end: $(date '+%Y-%m-%dT%H:%M:%S%z') ===="
