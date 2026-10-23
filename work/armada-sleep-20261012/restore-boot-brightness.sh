#!/usr/bin/env bash
set -euo pipefail
[[ $EUID == 0 ]] || exit 1
units=(systemd-backlight@backlight:ae94000.dsi.0.service systemd-backlight@backlight:ae96000.dsi.0.service)
systemctl unmask "${units[@]}"
systemctl daemon-reload
printf '%s\n' 'Boot brightness restoration enabled again. Current screen brightness is unchanged.'
