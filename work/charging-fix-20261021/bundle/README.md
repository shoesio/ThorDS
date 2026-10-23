# ThorDS charging update — 21 October 2026

Prepared, not yet installed. Kernel 7.1.2-thorch20 replaces the blanket removal
of IRQF_NO_SUSPEND with Armada's state-aware IPCC interrupt handling. During
suspend-to-idle the message interrupt stays live so a charger attached after
sleep can complete negotiation. Suspend-to-RAM masking remains in place for
SM8550/SM8750. ThorDS stays on s2idle.

Upstream source, pinned in UPSTREAM.json:
https://github.com/armada-os/armada/blob/d2bcf6fd33435f670f59a164c926842af91730f1/packages/kernel/patches/0504-mailbox-qcom-ipcc-mask-summary-irq-for-suspend-to-ram.patch

Battery sampler adds charger state and open-circuit voltage to sleep snapshots.
The sleep guard retains 200 timestamped pre/post records (100 cycles), in
/var/log/thords/sleep/history, while keeping latest-pre.json/latest-post.json.
History write failure does not prevent sampling. No guessed battery percentages,
charge limits, firmware replacements or different sleep mode are introduced.

Validation: upstream patch applied cleanly to retained 7.1.2 source; native ARM64
kernel and modules build passed. Config differs only in LOCALVERSION. Package
metadata, matching raw Image/Android boot image, module release, Binder config
and 13 DTBs verified. DTBs are byte-identical to the live boot image. Rollback
package Image matches the current kernel. New sampler ran on Thor and handled
an unwritable history directory without blocking its normal JSON output.

Keep lid open and charger connected; save your game. Install as root:
sudo bash /home/thords/charging-fix-20261021/install.sh --reboot

Installer checks device, old kernel/package and helper hashes; verifies bundle;
backs up current boot files, modules and helpers to
/var/lib/thords/charging-fix-backup-20261021; installs the kernel; verifies the
boot image contains the new Image; installs diagnostic helpers; then reboots.
No Android partitions or bootloader are written. The existing guarded Linux boot
update hooks handle initramfs and /boot/KERNEL.

Rollback, if needed, as root:
sudo bash /home/thords/charging-fix-20261021/rollback.sh --reboot

After reboot verify uname is 7.1.2-thorch20 and repeat a brief charger-attach-
while-already-asleep test. Hardware charging and gauge behavior on the new kernel
remain unverified until that test. Short success does not establish overnight
reliability. Existing evidence lives on the Mac in work/charging-20261021.
