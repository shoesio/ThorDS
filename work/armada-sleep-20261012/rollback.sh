#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
[[ $EUID == 0 ]] || { echo 'Run with sudo.' >&2; exit 1; }
backup=/var/lib/thords/armada-sleep-backup-20261012
[[ -r "$backup/prior-kernel-and-sleep.tar" && -r "$backup/service-state.tsv" ]] || exit 1
sha256sum -c SHA256SUMS
systemctl disable --now thords-early-splash.service || true
rm -f /etc/systemd/system/thords-early-splash.service \
  /etc/systemd/system/thords-session.service.d/40-early-splash.conf \
  /etc/mkinitcpio.conf.d/95-thords-splash.conf \
  /etc/mkinitcpio.conf.d/96-thords-console-autodetect.conf \
  /usr/lib/initcpio/install/thords-splash /usr/lib/initcpio/hooks/thords-splash
tar -xOf "$backup/prior-kernel-and-sleep.tar" usr/bin/thords-sleep-guard >/usr/bin/thords-sleep-guard
chmod 0755 /usr/bin/thords-sleep-guard
pacman -U --noconfirm ./linux-thorch-7.1.2-18-aarch64.pkg.tar.xz
systemctl daemon-reload
while IFS=$'\t' read -r unit enabled active; do
  if [[ "$enabled" != masked && "$enabled" != masked-runtime ]]; then
    systemctl unmask "$unit"
    case "$enabled" in
      enabled) systemctl enable "$unit" ;;
      enabled-runtime) systemctl enable --runtime "$unit" ;;
    esac
    [[ "$active" != active ]] || systemctl start "$unit"
  fi
done <"$backup/service-state.tsv"
sync
echo 'Prior kernel and service settings restored. Reboot to load kernel 7.1.2-thorch18.'
