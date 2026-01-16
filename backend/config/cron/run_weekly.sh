#!/bin/bash
set -euo pipefail

export JJ_INTEL_MAC_WEEKLY_RUN="true"
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export GIT_SSH_COMMAND="ssh -i /Users/jeremyjacob/.ssh/id_ed25519_kartiseret -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"

PROJECT_ROOT="/Users/jeremyjacob/Documents/Coding Projects/Kartiseret/NewScraping-August2025"
PYTHON="$PROJECT_ROOT/venv/bin/python"
ARTIFACT_DIR="$PROJECT_ROOT/utils/log/logger_artifacts"

cd "$PROJECT_ROOT"

echo "==== cron run start: $(date '+%Y-%m-%dT%H:%M:%S%z') ===="

# 1) Sync code (safe even if main was force-pushed)
git fetch origin main
git checkout main

# Reset everything EXCEPT the cron directory
git checkout origin/main -- .
git restore --source=origin/main --staged --worktree -- :!backend/config/cron/
git clean -fd -e backend/config/cron/

# 2) Run the job
"$PYTHON" -u -m backend.config.runner "$@"

# 3) Commit & push artifacts if they changed
if [[ -d "$ARTIFACT_DIR" ]]; then
  git add "$ARTIFACT_DIR"

  if ! git diff --cached --quiet; then
    git commit -m "chore: weekly logger artifacts $(date +%Y-%m-%d)"

    # If main moved while we ran, rebase then push
    git fetch origin main
    git rebase origin/main
    git push origin main
  fi
fi

echo "==== cron run end: $(date '+%Y-%m-%dT%H:%M:%S%z') ===="
