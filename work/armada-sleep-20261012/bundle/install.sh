#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
[[ "${1:-}" == '' || "${1:-}" == --reboot ]] || exit 2
[[ $EUID == 0 ]] || { echo 'Run this installer with sudo.' >&2; exit 1; }
[[ "$(tr -d '\0' </proc/device-tree/model)" == 'AYN Thor' ]] || {
  echo 'This update is only prepared for the AYN Thor.' >&2; exit 1;
}
[[ "$(uname -r)" == '7.1.2-thorch18' ]] || {
  echo 'The running kernel changed; stop and recheck the update.' >&2; exit 1;
}
[[ "$(pacman -Q linux-thorch)" == 'linux-thorch 7.1.2-18' ]] || exit 1
[[ ! -e /run/thords-sleep/rgb.json && ! -e /run/thords-sleep/restart-lavd ]] || {
  echo 'Sleep restoration is pending; finish waking the device before installing.' >&2; exit 1;
}
sha256sum -c SHA256SUMS
for path in /usr/libexec/thords/early-splash /usr/libexec/thords/early-splash-renderer /etc/mkinitcpio.conf.d/95-thords-splash.conf /etc/mkinitcpio.conf.d/96-thords-console-autodetect.conf /etc/systemd/system/thords-early-splash.service /etc/systemd/system/thords-session.service.d/40-early-splash.conf; do
  [[ ! -e "$path" && ! -L "$path" ]] || { echo "New update path already exists: $path; stop and check." >&2; exit 1; }
done
[[ "$(sha256sum /usr/bin/thords-sleep-guard | cut -d ' ' -f 1)" == "$(cat installed-guard.sha256)" ]] || {
  echo 'The installed sleep guard changed; stop and recheck the update.' >&2; exit 1;
}
backup=/var/lib/thords/armada-sleep-backup-20261012
[[ ! -e "$backup" ]] || { echo "Backup already exists: $backup; stop and check." >&2; exit 1; }
install -d -m 0700 "$backup"
tar -C / -cpf "$backup/prior-kernel-and-sleep.tar" \
  boot/KERNEL boot/KERNEL.previous boot/initramfs-linux-thorch.img \
  boot/initramfs-linux-thorch-fallback.img usr/lib/modules/7.1.2-thorch18 \
  usr/bin/thords-sleep-guard var/lib/pacman/local/linux-thorch-7.1.2-18
cp installed-guard.sha256 "$backup/"
mapfile -t console_units <console-units.list
for unit in "${console_units[@]}"; do
  printf '%s\t%s\t%s\n' "$unit" "$(systemctl is-enabled "$unit" 2>/dev/null || true)" \
    "$(systemctl is-active "$unit" 2>/dev/null || true)" >> "$backup/service-state.tsv"
done
# Install the early-boot assets before pacman rebuilds the new initramfs.
install -Dm755 -o root -g root early-splash-renderer /usr/libexec/thords/early-splash-renderer
install -Dm755 -o root -g root early-splash /usr/libexec/thords/early-splash
install -Dm644 -o root -g root boot-splash.asp /usr/share/thords/boot-splash.asp
install -Dm644 -o root -g root Armada-LICENSE.md /usr/share/licenses/thords-early-splash/LICENSE.md
install -Dm644 -o root -g root splash-UPSTREAM /usr/share/licenses/thords-early-splash/UPSTREAM
install -Dm755 -o root -g root initcpio-install /usr/lib/initcpio/install/thords-splash
install -Dm755 -o root -g root initcpio-hook /usr/lib/initcpio/hooks/thords-splash
install -Dm644 -o root -g root 95-thords-splash.conf /etc/mkinitcpio.conf.d/95-thords-splash.conf
install -Dm644 -o root -g root 96-thords-console-autodetect.conf /etc/mkinitcpio.conf.d/96-thords-console-autodetect.conf
install -Dm644 -o root -g root thords-early-splash.service /etc/systemd/system/thords-early-splash.service
install -Dm644 -o root -g root 40-early-splash.conf /etc/systemd/system/thords-session.service.d/40-early-splash.conf
pacman -U --noconfirm ./linux-thorch-7.1.2-19-aarch64.pkg.tar.xz
install -m 0755 -o root -g root thords-rgb-sleep /usr/bin/thords-rgb-sleep
install -m 0755 -o root -g root thords-sleep-guard /usr/bin/thords-sleep-guard
systemctl daemon-reload
systemctl enable thords-early-splash.service
# Keep the console's essential services and save backups; mask optional daemons.
systemctl mask --now "${console_units[@]}"
sync
printf 'Installed Armada sleep, early loading image and console service changes. Backup: %s\n' "$backup"
printf 'Reboot to load kernel 7.1.2-thorch19, then perform a brief lid-close/wake check.\n'
if [[ "${1:-}" == --reboot ]]; then systemctl reboot; fi
