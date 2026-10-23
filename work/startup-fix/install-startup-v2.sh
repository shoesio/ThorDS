#!/usr/bin/env bash
set -euo pipefail
[[ $(id -u) == 0 ]] || { echo 'Run this installer with sudo.'; exit 1; }
stage=/home/thords/startup-v2
backup=/var/lib/thords/startup-backups/$(date +%Y%m%d-%H%M%S)
mkdir -p "$backup"
scripts=(thords-session thords-azahar thords-window-manager thords-configure-controls thords-configure-performance)
for name in "${scripts[@]}"; do
  bash -n "$stage/after/$name"
  cp -a "/usr/bin/$name" "$backup/$name"
done
cp -a /etc/thords/sway.conf "$backup/sway.conf"
cp -a /usr/share/thords/boot-splash.png "$backup/boot-splash.png"
for name in thords-session.service thords-performance.service; do
  cp -a "/usr/lib/systemd/system/$name" "$backup/$name"
done
systemctl is-enabled thorch-debug-report.service >"$backup/debug-report-enabled.txt" || true
for name in "${scripts[@]}"; do
  install -m755 "$stage/after/$name" "/usr/bin/$name"
  if [[ -e "/home/thords/.local/bin/$name" ]]; then
    cp -a "/home/thords/.local/bin/$name" "$backup/$name.user-local"
    ln -sfn "/usr/bin/$name" "/home/thords/.local/bin/$name"
    chown -h thords:thords "/home/thords/.local/bin/$name"
  fi
done
install -m644 "$stage/sway.conf" /etc/thords/sway.conf
install -m644 "$stage/boot-splash.png" /usr/share/thords/boot-splash.png
for name in thords-session.service thords-performance.service thorch-debug-report.timer; do
  install -m644 "$stage/$name" "/usr/lib/systemd/system/$name"
done
systemctl daemon-reload
systemctl disable thorch-debug-report.service
systemctl enable thorch-debug-report.timer
printf 'Startup installed. Backup: %s\n' "$backup"
if [[ ${1:-} == --reboot ]]; then
  systemctl reboot
else
  systemctl stop thords-session.service
  # The older session leaked helpers into a PAM scope outside the service.
  pkill -TERM -u thords -f '^bash (/usr/bin|/home/thords/.local/bin)/thords-(session|azahar|window-manager)( |$)' || true
  pkill -TERM -u thords -f '^python3 /usr/bin/thords-(brightness-hotkeys|framegen-input)( |$)' || true
  pkill -TERM -u thords -x azahar || true
  sleep 2
  pkill -KILL -u thords -x azahar || true
  systemctl start thords-session.service
fi
