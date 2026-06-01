#!/bin/bash
grep -q 'hh-job-scout/.env' /etc/systemd/system/hh-job-scout.service || \
  sed -i '/\[Service\]/a EnvironmentFile=-/opt/hh-job-scout/.env' /etc/systemd/system/hh-job-scout.service
systemctl daemon-reload
systemctl restart hh-job-scout
