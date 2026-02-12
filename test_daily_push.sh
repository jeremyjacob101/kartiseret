#!/bin/bash
set -euo pipefail

export JJ_INTEL_MAC_TEST_RUN="true"
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Only matters if your git remote is SSH (git@github.com:...)
export GIT_SSH_COMMAND="ssh -i /Users/jeremyjacob/.ssh/id_ed25519_kartiseret -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"

PROJECT_ROOT="/Users/jeremyjacob/Documents/Coding Projects/Kartiseret/NewScraping-August2025"
LOG_DIR="$PROJECT_ROOT/backend/config/cron/run_daily_test_logs"

cd "$PROJECT_ROOT"

TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
LOG_FILE="$LOG_DIR/cron_test_${TIMESTAMP}.log"
mkdir -p "$LOG_DIR"

run_phase() {
  echo "==== cron test run start: $(date '+%Y-%m-%dT%H:%M:%S%z') ===="
  echo "Project: $PROJECT_ROOT"
  echo "User: $(whoami)"
  echo "PWD:  $(pwd)"
  echo "PATH: $PATH"
  echo "Remote (origin): $(git remote get-url origin)"

  # Sync code (robust even if main was force-pushed)
  git fetch origin main
  git checkout main
  git reset --hard origin/main
  git clean -fd -e backend/config/cron/

  # --- The "job" ---
  printf "%s\n" "i'm a test" > testing.txt
  printf "%s - i'm a test\n" "$(date '+%Y-%m-%dT%H:%M:%S%z')" >> testing.log

  echo "Wrote: $(pwd)/testing.txt"
  echo "Appended: $(pwd)/testing.log"
  echo "==== cron test run end: $(date '+%Y-%m-%dT%H:%M:%S%z') ===="
}

# Capture ALL output of the run phase to a per-run log (and terminal)
run_phase "$@" 2>&1 | tee "$LOG_FILE"

# --------------------
# Phase 2: git add/commit/rebase/push (NO tee running now)
# --------------------

git add testing.txt testing.log
git add "$LOG_FILE"

# If nothing staged, we’re done
if git diff --cached --quiet; then
  exit 0
fi

git commit -m "[TEST] daily cron test $(date '+%Y-%m-%d_%H-%M-%S')"

# Update again in case main moved while the job ran, then push
git fetch origin main
git rebase origin/main
git push origin main
