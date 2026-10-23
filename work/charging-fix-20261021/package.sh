#!/usr/bin/env bash
set -euo pipefail
root=/build/pkg-root
install -Dm755 /repo/packages/thorch-bsp/payload/usr/lib/thorch/boot_image.py "$root/usr/lib/thorch/boot_image.py"
install -d "$root/charging-kernel20-package" "$root/charging-kernel20-input"
cp /repo/packages/linux-thorch/PKGBUILD /repo/packages/linux-thorch/waydroid-kernel.config "$root/charging-kernel20-package/"
mount --bind /build/vendor/rocknix-kernel "$root/charging-kernel20-input"
mount -t proc proc "$root/proc"
trap 'umount "$root/proc"; umount "$root/charging-kernel20-input"' EXIT
chroot "$root" bash -c 'cd /charging-kernel20-package; chown -R builder:builder .; su builder -c "env THORCH_ROCKNIX_KERNEL_DIR=/charging-kernel20-input makepkg --nodeps --noconfirm --force"'
cp "$root/charging-kernel20-package/linux-thorch-7.1.2-20-aarch64.pkg.tar.xz" /port/bundle/
