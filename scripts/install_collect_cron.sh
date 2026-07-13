#!/bin/bash
# Install systemd timer: daily HH collect at 18:00 Europe/Moscow
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE=/etc/systemd/system/hh-job-scout-collect.service
TIMER=/etc/systemd/system/hh-job-scout-collect.timer

chmod +x "${ROOT}/scripts/collect_daily.sh"

cat >"$SERVICE" <<EOF
[Unit]
Description=FitLetter daily HH vacancy collect
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=${ROOT}
ExecStart=${ROOT}/scripts/collect_daily.sh
User=root
EnvironmentFile=-${ROOT}/.env
EOF

cat >"$TIMER" <<'EOF'
[Unit]
Description=FitLetter daily collect at 18:00 MSK

[Timer]
OnCalendar=*-*-* 18:00:00 Europe/Moscow
Persistent=true
RandomizedDelaySec=120

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now hh-job-scout-collect.timer
systemctl status hh-job-scout-collect.timer --no-pager || true
echo "Next run:"
systemctl list-timers hh-job-scout-collect.timer --no-pager || true
