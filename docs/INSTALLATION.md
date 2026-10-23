# Experimental SD testing and recovery

There is no supported ready-to-install ThorDS release yet. These notes explain
the existing SD writer and the remaining hardware validation; they are not a
claim that a clean installation has been tested.

## Keep an existing setup intact

Use a separate, expendable SD card. Keep your working card, backups, games,
saves, and internal installation unchanged. The source checks and builds can
all run on a computer without connecting or changing a Thor.

The device needs an existing, compatible Linux-capable ABL boot path. This
repository does not establish or flash that prerequisite. Do not follow a
bootloader flashing or internal-storage installation procedure just to try
this source snapshot. If you do not already have a known working Linux SD boot
and recovery path, stop before device testing.

The inherited Thorch tree contains internal-storage installers, including
modes that can erase Android userdata. They are outside this SD-only guide.

## Prepare a separate SD card on Linux

Only proceed after the complete image has built and passed its checker.
From the restored build tree:

```sh
make check IMAGE=output/thorch-arch-aarch64.img
lsblk -o NAME,MODEL,SIZE,TYPE,RM,MOUNTPOINTS
```

Identify the spare card by its physical device, model, and size. Unmount all its
partitions through your normal disk tool. The existing writer requires a
removable whole-disk Linux block device, sufficient capacity, and no mounted
partitions. It shows the target and requires you to type the exact device
path. It overwrites that card.

For a card you have positively identified as `/dev/sdX` (a placeholder to
replace, never a name to guess):

```sh
make write IMAGE=output/thorch-arch-aarch64.img DEVICE=/dev/sdX
sudo scripts/check-thorch-image.sh /dev/sdX
```

The card writer/checker path has not been exercised against physical media as
part of the source publication. No card or Thor was written during publication.

## Fresh-boot acceptance checks

Before calling a build installable, record the image checksum, source commit,
Thor hardware variant, boot prerequisites, and all of the following:

- Boot from the spare card and confirm the mounted root is on that card.
- Confirm account/password provisioning works and no shared credential exists.
- Confirm both panels, their placement, touch mapping, audio, and controls.
- Configure the emulator with your own console data; verify HOME and a title.
- Verify clean shutdown and repeated cold boots, preserving settings and saves.
- Verify clock advancement, gyro orientation, lid suspend/resume, charging
  when the cable is attached during sleep, and battery reporting.
- Confirm the original working setup still boots after removing the test card.

Historical tests under `work/` are useful comparisons, not a substitute for
these checks on a fresh image. Do not run the dated update installers as a
sequence: they often pin a specific old package, device, or helper hash.

## Diagnostics and recovery

For an already configured system, collect service failures with
`systemctl --failed`, inspect `journalctl -b -u thords-session.service`, and
review `/var/log/thords/`. The inherited build may also write
`/boot/thorch-debug-report.txt`. Network access depends on the actual account,
password, and network configuration; no development-device address is a
universal connection address.

If a configured HOME Menu repeatedly fails, the saved session supports a
`~/.config/thords/disable-home-autoboot` marker to bypass automatic HOME boot.
Its UI visibility still needs checking on a fresh image; do not depend on
this as your only recovery mechanism.

For SD-only testing, power down fully, remove the spare card, and return to
your known working boot path. If boot fails before Linux, changing emulator
settings cannot fix it. The inherited docs describe DTB and `/KERNEL` checks;
recheck the spare card on the build host rather than altering a working
internal installation. Hardware boot-selection behavior remains unverified
for this source snapshot.
