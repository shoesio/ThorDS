#!/usr/bin/env bash
set -euo pipefail
[[ $EUID == 0 && "$(uname -r)" == 7.1.2-thorch19 ]] || exit 1
backup=/var/lib/thords/armada-sleep-backup-20261012
[[ -d "$backup" && -f "$backup/service-state.tsv" ]] || exit 1
units=(systemd-backlight@backlight:ae94000.dsi.0.service systemd-backlight@backlight:ae96000.dsi.0.service)
for unit in "${units[@]}"; do
  if ! grep -Fq "$unit" "$backup/service-state.tsv"; then
    printf '%s\t%s\t%s\n' "$unit" "$(systemctl is-enabled "$unit" 2>/dev/null || true)" \
      "$(systemctl is-active "$unit" 2>/dev/null || true)" >> "$backup/service-state.tsv"
  fi
done
# ThorDS hardware defaults and HOME brightness already own both panels.
# This follows Armada's policy of masking stale systemd-backlight restores.
systemctl mask --now "${units[@]}"
systemctl reset-failed "${units[@]}"
echo 'Redundant backlight restoration disabled. Current brightness is unchanged; no reboot needed.'
