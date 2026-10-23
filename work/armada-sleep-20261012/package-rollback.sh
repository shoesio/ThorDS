#!/usr/bin/env bash
set -euo pipefail
root=/build/pkg-root
install -Dm755 /repo/packages/thorch-bsp/payload/usr/lib/thorch/boot_image.py "$root/usr/lib/thorch/boot_image.py"
cp /repo/packages/linux-thorch/waydroid-kernel.config "$root/thords-rollback-package/"
mount -t proc proc "$root/proc"
trap 'umount "$root/proc"' EXIT
chroot "$root" bash -c 'cd /thords-rollback-package; chown -R builder:builder .; su builder -c "env THORCH_ROCKNIX_KERNEL_DIR=/thords-rollback-kernel makepkg --nodeps --noconfirm --force"'
cp "$root/thords-rollback-package/linux-thorch-7.1.2-18-aarch64.pkg.tar.xz" /port/
