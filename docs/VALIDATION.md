# Validation status — 23 October 2026

This publication is experimental developer source. Checks below were performed
in a separate restored source tree; no Thor, SD card, bootloader, installed
system, settings, games, or saves were modified.

## Checks completed locally

| Check | Result |
| --- | --- |
| Restore main Thorch checkout from its public upstream commit and apply the saved patch | Passed |
| Restore nested AzaharPlus and its additional nested reference checkouts | Passed |
| Restore kiosk splash assets, executable files, and systemd masks | Passed |
| Restore-tool tests: successful recovery plus refusal of existing destinations, modified content, changed symlinks, and unknown checkout | 5 passed |
| Restored package-manifest validation | 21 packages, 11 image-profile packages; passed |
| ThorDS frame-generation integration checks | Passed |
| Power-policy tests against simulated hardware | 5 passed |
| Native Linux AArch64 splash renderer compilation with libdrm | Passed |
| Kiosk package payload assembly, renderer executable, splash asset, and service mask checks | Passed |

The Linux checks ran in the existing Thorch builder container against a new
source restore, without using the active build source or writing a device.
The package-assembly check calls the saved recipe's package function; it does
not resolve/install every runtime dependency or create a complete OS image.

The [Source checks workflow](../.github/workflows/source-checks.yml) repeats
restoration, package metadata/runtime tests, and renderer/payload assembly on
GitHub's Linux runner. Its status is visible on the repository's Actions page.

## Not established by this publication

- A complete clean kernel, emulator, package-set, and image build.
- Reproducibility while image/runtime/rootfs/package downloads are rolling.
- Integration of all historical clock, gyro, and device-side changes into the
  image recipes.
- New-account provisioning and console-data import on a clean ThorDS image.
- Physical SD writing, fresh boot, recovery, panel/input/audio behavior,
  suspend/resume, gyro orientation, or charging behavior on that fresh image.
- Overnight charging reliability or battery-gauge accuracy.

A full clean image rebuild was not attempted on this Mac because only about
13 GiB of host space remained after source validation. Building within a Linux
VM does not remove that physical-host constraint. Existing caches do not count
as proof of a clean build.

Historical on-device results remain in dated `work/` folders. In particular,
the charging notes record a successful short charger-after-sleep test on
`7.1.2-thorch20`, and the gyro notes record a user-confirmed in-game motion test.
These describe the existing development installation, not a new GitHub build.

Before distributing an installable image, complete the checks in
[the SD testing guide](INSTALLATION.md) using a separate card and record the
image checksum and source revisions.

## Subsequent live-device alignment audit

A read-only audit confirmed that the historical build recipe differs from the
running development Thor. The captured deployment and effective source changes
are preserved separately; see [device alignment](DEVICE_ALIGNMENT.md). The
old frame-generation checks above validate the old recipe, not the current
native-launch deployment. No hardware state was changed during the audit.
