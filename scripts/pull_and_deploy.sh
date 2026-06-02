#!/bin/bash
# Pull latest main and restart (triggered by POST /api/hooks/deploy)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -d .git ]; then
  echo "ERROR: $ROOT is not a git repo. See README — one-time setup on VPS." >&2
  exit 1
fi

git fetch origin main
git reset --hard origin/main
chmod +x deploy.sh run.sh 2>/dev/null || true
exec "$ROOT/deploy.sh"
