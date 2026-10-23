#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
kiosk="$root/packages/thords-kiosk"

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

# The pinned Azahar build does not implement duplicate-frame suppression.
# Verify the actual fixed-2x presentation contract instead.
grep -q '^export MAKO_FRAME_GENERATION_TOP_ONLY=1$' \
  "$kiosk/rootfs/usr/bin/thords-azahar" ||
  fail 'MAKO must target the large 120 Hz surface'
grep -q 'THORDS_FRAMEGEN_TARGET_FPS=120' \
  "$kiosk/rootfs/usr/bin/thords-azahar" ||
  fail '120 FPS target is not exported at the launch boundary'
grep -q 'mako-launch' "$kiosk/rootfs/usr/bin/thords-azahar" ||
  fail 'MAKO launch hook is missing'
grep -q '\.local/mako/bin/mako-launch' "$kiosk/rootfs/usr/bin/thords-azahar" ||
  fail 'user-local MAKO install path is not supported'
grep -q 'adaptive = false' "$kiosk/rootfs/usr/bin/thords-azahar" ||
  fail 'MAKO must use fixed cadence'
grep -q '^multiplier = 2$' \
  "$kiosk/rootfs/usr/bin/thords-azahar" ||
  fail 'MAKO must use the verified 2x multiplier'
grep -q 'target_fps = 120' "$kiosk/rootfs/usr/bin/thords-azahar" ||
  fail 'MAKO 120 FPS target is not configured'
grep -q 'mako-120.toml' "$kiosk/rootfs/usr/bin/thords-framegen" ||
  fail 'runtime toggle is not connected to the MAKO profile'
grep -q 'DSI-2 mode 1920x1080@120Hz' \
  "$kiosk/rootfs/etc/thords/sway.conf" ||
  fail 'top-panel 120 Hz mode is not requested'
grep -q 'BTN_THUMBL' "$kiosk/rootfs/usr/bin/thords-framegen-input" ||
  fail 'L3 input handling is missing'
grep -q 'BTN_THUMBR' "$kiosk/rootfs/usr/bin/thords-framegen-input" ||
  fail 'R3 input handling is missing'

bash -n "$kiosk/rootfs/usr/bin/thords-framegen"
bash -n "$kiosk/rootfs/usr/bin/thords-azahar"
bash -n "$kiosk/rootfs/usr/bin/thords-session"
bash -n "$kiosk/rootfs/usr/bin/thords-window-manager"
python3 -m py_compile "$kiosk/rootfs/usr/bin/thords-framegen-input"
jq empty "$root/manifests/packages.json"
printf 'thords frame-generation integration checks passed\n'
