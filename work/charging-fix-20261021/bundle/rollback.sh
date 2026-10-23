#!/usr/bin/env bash
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Run with sudo.' >&2; exit 1; }
[[ ${1:-} == '' || ${1:-} == --reboot ]] || exit 2
[[ $(tr -d '\0' </proc/device-tree/model) == 'AYN Thor' ]] || exit 1
backup=/var/lib/thords/charging-fix-backup-20261021
[[ -f $backup/prior-kernel-and-boot.tar && -f $backup/thords-power-sample && -f $backup/thords-sleep-guard ]] || exit 1
case "$(pacman -Q linux-thorch)" in
 'linux-thorch 7.1.2-19'|'linux-thorch 7.1.2-20') ;;
 *) echo 'Kernel package changed; stop and recheck before rollback.' >&2; exit 1;;
esac
pacman -U --noconfirm "$backup/linux-thorch-7.1.2-19-aarch64.pkg.tar.xz"
install -m0755 -o root -g root "$backup/thords-power-sample" /usr/bin/thords-power-sample
install -m0755 -o root -g root "$backup/thords-sleep-guard" /usr/bin/thords-sleep-guard
sync
echo 'Previous kernel and sleep diagnostics restored. Reboot required.'
if [[ ${1:-} == --reboot ]]; then systemctl reboot; fi
