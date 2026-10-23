#!/usr/bin/env bash
set -euo pipefail
[[ $(id -u) == 0 ]] || { echo 'Run this installer with sudo.'; exit 1; }
stage=/home/thords
backup=/var/lib/thords/startup-backups/$(date +%Y%m%d-%H%M%S)
mkdir -p "$backup"
for name in thords-session thords-azahar thords-window-manager; do
  bash -n "$stage/$name"
  cp -a "/usr/bin/$name" "$backup/$name"
done
cp -a /etc/thords/sway.conf "$backup/sway.conf"
cp -a /usr/share/thords/boot-splash.png "$backup/boot-splash.png"
for name in thords-session thords-azahar thords-window-manager; do
  install -m755 "$stage/$name" "/usr/bin/$name"
  if [[ -e "$stage/.local/bin/$name" ]]; then
    cp -a "$stage/.local/bin/$name" "$backup/$name.user-local"
  fi
  ln -sfn "/usr/bin/$name" "$stage/.local/bin/$name"
  chown -h thords:thords "$stage/.local/bin/$name"
done
install -m644 "$stage/sway.conf" /etc/thords/sway.conf
install -m644 "$stage/boot-splash.png" /usr/share/thords/boot-splash.png
printf 'Startup installed. Backup: %s\n' "$backup"
systemctl restart thords-session.service
