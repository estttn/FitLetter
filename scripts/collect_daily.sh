#!/bin/bash
# Daily HH collect for all active users/resumes. Logs to data/collect.log
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p data
LOG="${ROOT}/data/collect.log"
{
  echo "=== $(date -Iseconds) collect start ==="
  ./venv/bin/python scripts/collect_all.py
  echo "=== $(date -Iseconds) collect done ==="
} >>"$LOG" 2>&1
