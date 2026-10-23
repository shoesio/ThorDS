#!/usr/bin/env bash
set -euo pipefail
cd /Users/admin/ThorDS
for container in thords-sleep-kernel-build thords-power-packages; do
  if docker inspect "$container" >/dev/null 2>&1; then
    status=$(docker wait "$container")
    [[ "$status" == 0 ]] || { echo "$container failed: $status"; exit 1; }
  fi
done
grep -q 'Thorch source-built feature kernel ready' work/power-sleep-v2/kernel-build.log
docker run --rm --privileged --name thords-kernel-package \
  -v thorch-build-3258668861:/build \
  -v thorch-build-3258668861:/repo/.thords-native \
  -v thorch-rocknix-3258668861:/repo/.rocknix-native \
  -v /Users/admin/ThorDS/build/thorch-work:/repo -w /repo \
  -e THORCH_BUILD_DIR=/build -e THORCH_PACKAGE_JOBS=2 \
  ghcr.io/thorch-os/thorch-build:latest \
  bash scripts/build-packages.sh --packages linux-thorch
