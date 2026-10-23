#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
[[ ${1:-} == '' || ${1:-} == --reboot ]] || exit 2
[[ $EUID == 0 ]] || { echo 'Run this installer with sudo.' >&2; exit 1; }
[[ $(tr -d '\0' </proc/device-tree/model) == 'AYN Thor' ]] || exit 1
[[ $(uname -r) == 7.1.2-thorch19 ]] || { echo 'Running kernel changed; stop and recheck.' >&2; exit 1; }
[[ $(pacman -Q linux-thorch) == 'linux-thorch 7.1.2-19' ]] || exit 1
[[ $(cat /sys/class/power_supply/qcom-battmgr-usb/online) == 1 ]] || { echo 'Keep the charger connected during this update.' >&2; exit 1; }
capacity=$(cat /sys/class/power_supply/battery/capacity)
[[ $capacity =~ ^[0-9]+$ ]] && (( capacity >= 10 )) || { echo 'Charge to at least 10% first.' >&2; exit 1; }
for unit in sleep.target suspend.target systemd-suspend.service; do
    [[ $(systemctl show "$unit" -p ActiveState --value) == inactive ]] || { echo 'Finish waking Thor before installing.' >&2; exit 1; }
done
sha256sum -c SHA256SUMS
[[ $(pacman -Qp ./linux-thorch-7.1.2-20-aarch64.pkg.tar.xz) == 'linux-thorch 7.1.2-20' ]] || exit 1
[[ $(sha256sum /usr/bin/thords-sleep-guard | cut -d ' ' -f1) == b70edc39d6cc1b2b0a79cb8d8b274031f71e77148a4a5aadd151b437ccad3cbb ]] || { echo 'Sleep helper changed; stop and recheck.' >&2; exit 1; }
[[ $(sha256sum /usr/bin/thords-power-sample | cut -d ' ' -f1) == 1c08b59c2b58a0b7aeffb4ea1407eeb2f2f9720929c0372c4d2d67ee754f628c ]] || { echo 'Battery sampler changed; stop and recheck.' >&2; exit 1; }
[[ $(sha256sum /usr/lib/modules/7.1.2-thorch19/Image | cut -d ' ' -f1) == 50dcba238a14aa2646a93c0a2807b0915bc054518f51e3344fbd7293b2ee4c2e ]] || exit 1
backup=/var/lib/thords/charging-fix-backup-20261021
[[ ! -e $backup ]] || { echo 'A backup already exists; stop and recheck.' >&2; exit 1; }
install -d -m 0700 "$backup"
cp -a /usr/bin/thords-power-sample /usr/bin/thords-sleep-guard "$backup/"
cp linux-thorch-7.1.2-19-aarch64.pkg.tar.xz "$backup/"
paths=(boot/KERNEL boot/initramfs-linux-thorch.img boot/initramfs-linux-thorch-fallback.img usr/lib/modules/7.1.2-thorch19 etc/mkinitcpio.d/linux-thorch.preset var/lib/pacman/local/linux-thorch-7.1.2-19)
[[ ! -f /boot/KERNEL.previous ]] || paths+=(boot/KERNEL.previous)
tar -C / -cpf "$backup/prior-kernel-and-boot.tar" "${paths[@]}"
cp SHA256SUMS "$backup/update-SHA256SUMS"
trap 'echo "Update did not finish. Do not reboot; keep the error output for diagnosis. Backup: $backup" >&2' ERR
pacman -U --noconfirm ./linux-thorch-7.1.2-20-aarch64.pkg.tar.xz
[[ $(pacman -Q linux-thorch) == 'linux-thorch 7.1.2-20' ]]
grep -aFq '7.1.2-thorch20' /usr/lib/modules/7.1.2-thorch20/Image
verified=$(mktemp /run/thords-charge-image.XXXXXX)
python3 /usr/lib/thorch/boot_image.py extract-kernel /boot/KERNEL "$verified" --require-thor
if ! cmp -s "$verified" /usr/lib/modules/7.1.2-thorch20/Image; then
    rm -f "$verified"
    echo 'Boot image does not contain the new kernel; stop before rebooting.' >&2
    exit 1
fi
rm -f "$verified"
install -m 0755 -o root -g root thords-power-sample /usr/bin/thords-power-sample
install -m 0755 -o root -g root thords-sleep-guard /usr/bin/thords-sleep-guard
sync
trap - ERR
printf 'Charging interrupt fix and sleep-history logging installed. Backup: %s\n' "$backup"
echo 'Reboot required to load kernel 7.1.2-thorch20.'
if [[ ${1:-} == --reboot ]]; then systemctl reboot; fi
