#!/bin/bash
# Append deploy public key to ~/.ssh/authorized_keys (run once on VPS).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PUB="$ROOT/deploy-keys/fitletter_github_actions.pub"
MARKER="fitletter-github-actions@job-scout"

if [ ! -f "$PUB" ]; then
  echo "Missing $PUB — copy deploy-keys from repo first." >&2
  exit 1
fi

mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

if grep -qF "$MARKER" ~/.ssh/authorized_keys 2>/dev/null; then
  echo "OK: deploy key already in authorized_keys"
  exit 0
fi

cat "$PUB" >> ~/.ssh/authorized_keys
echo "OK: added deploy public key for $MARKER"
