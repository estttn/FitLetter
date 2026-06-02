#!/bin/bash
# Production deploy on server (called from GitHub Actions or manually)
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d venv ]; then
  python3 -m venv venv
fi

./venv/bin/pip install -q -r requirements.txt

mkdir -p data
if [ ! -f profile.json ] && [ -f profile.example.json ]; then
  cp profile.example.json profile.json
fi

mkdir -p data
if REV="$(git rev-parse --short HEAD 2>/dev/null)"; then
  echo "$REV" > data/deploy_rev.txt
elif [ ! -s data/deploy_rev.txt ]; then
  echo "local" > data/deploy_rev.txt
fi
REV="$(cat data/deploy_rev.txt)"

systemctl daemon-reload
systemctl restart hh-job-scout
systemctl is-active --quiet hh-job-scout
echo "OK: deployed ${REV}"
