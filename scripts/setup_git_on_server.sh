#!/bin/bash
# One-time on VPS: turn /opt/hh-job-scout into a git checkout (keeps data/ and .env).
set -euo pipefail
ROOT="${1:-/opt/hh-job-scout}"
REPO="${2:-https://github.com/estttn/job-scout.git}"

cd "$ROOT"
if [ ! -f .env ]; then
  echo "WARN: no .env in $ROOT — create it before restart"
fi

if [ ! -d .git ]; then
  git init
  git remote add origin "$REPO"
fi
git remote set-url origin "$REPO" 2>/dev/null || true
git fetch origin main
git reset --hard origin/main
chmod +x deploy.sh run.sh scripts/*.sh 2>/dev/null || true
echo "OK: $ROOT is on $(git rev-parse --short HEAD)"
