# Getting started with ThorDS

## What you can do with this repository

ThorDS targets the AYN Thor: Linux boots into a dedicated Wayland/Azahar session
with an emulated 3DS HOME Menu. This repository is a development source backup.
There is no ready-to-flash release image or verified end-to-end clean build here.

A developer can restore the modified build source using the steps below and
inspect the hardware work. A new user cannot yet reproduce the current device
just by cloning and running one command. Some fixes were installed separately
on the development device and have not been integrated into the image build.

The repository is private; collaborators need GitHub access before cloning.

## Restore the main build source

You need Git, Python 3 for the snapshot tooling, and access to the recorded
upstream repositories. Source restoration itself does not need administrator
access and can be performed before setting up a Linux build environment.

From a new directory:

```sh
git clone https://github.com/shoesio/ThorDS.git
cd ThorDS
git clone https://github.com/thorch-os/thorch.git build/thorch-work
git -C build/thorch-work checkout --detach 82e7472e6cad5c08a55c3aef92ef5be218621b2c
git -C build/thorch-work apply ../../state/checkouts/build/thorch-work/changes.patch
cp -Rp state/checkouts/build/thorch-work/untracked/. build/thorch-work/
```

Use an empty destination for the nested checkout. Do not apply the patch a
second time to an already restored checkout. These commands restore source;
they do not install anything on the Thor.

Read `build/thorch-work/README.md`, `Makefile`, and `config/thorch.conf` after
restoration. The README there is inherited from Thorch and also describes
features outside ThorDS, including internal installation. It is not a ThorDS
installation guide.

For other nested checkouts, `state/checkouts.json` lists the URL and commit.
Clone into the recorded path, check out that commit, apply the corresponding
`state/checkouts/<path>/changes.patch` if nonempty, then copy the contents of
its `untracked/` directory into the checkout. These snapshots combine staged
and unstaged tracked changes; they do not preserve the original staging state.

## Build entry points and outstanding gaps

The restored build expects an Arch-compatible Linux build environment. Its
README lists host dependencies and its Makefile provides container support,
including a native Linux volume for case-sensitive build files on macOS.
Check those files before choosing a host. Image creation needs privileged
Linux facilities; source restoration alone does not provide those facilities.

The existing build targets are:

| Target | Purpose |
| --- | --- |
| `make help` | Show the available options |
| `make doctor` | Check build-host prerequisites |
| `make sync` | Fetch public ROCKNIX source/firmware inputs |
| `make kernel` | Fetch runtime inputs and build the kernel |
| `make packages` | Build local packages |
| `make build` | Assemble the SD image |

Run these inside `build/thorch-work`. These are entry points found in the
saved Makefile, not a clean-build sequence verified for this GitHub snapshot.
Resolve the following before treating an image as reproducible:

- Binary assets were excluded from the initial backup. For example,
  `packages/thords-kiosk/PKGBUILD` expects
  `rootfs/usr/share/thords/boot-splash.png`; the source snapshot does not
  include that asset. Supply an appropriate asset or deliberately revise the
  package recipe before building it.
- Downloaded firmware, compiled packages, boot images, and build caches are
  absent. Fetch or build the matching inputs; see the restored build's
  provenance checks and configuration.
- HOME Menu, game files, saves, keys, and the development device's configuration
  are not distributed here. Supply your own appropriate dumps and data.
  No setup path for these has yet been validated on a fresh device.
- Dated folders under `work/` include experiments, superseded versions, and
  device-specific installers. They are not an ordered installation sequence.
  Paths, addresses, hashes, and kernel assumptions may refer to the original
  development device.
- A fresh build and boot from a clean clone have not been verified. A release
  still needs a consolidated installation process and hardware validation.

The ThorDS image-builder is intended for SD bring-up. No device-writing command
is part of this guide. Bootloader prerequisites, SD deployment, and recovery
need a ThorDS-specific tested guide before this is suitable for new users.

## Where to find implementation and validation notes

| Area | Starting point |
| --- | --- |
| Kiosk session, controls, power helpers | `state/checkouts/build/thorch-work/untracked/packages/thords-kiosk/` |
| Build and kernel changes | `state/checkouts/build/thorch-work/changes.patch` |
| Latest saved charging test | [Charging status](../work/charging-fix-20261021/STATUS.md) — read the later updates as well as the initial heading |
| Motion / gyro bring-up | [Gyro status](../work/gyro-20261018/STATUS.md) |
| Clock correction | [Clock status](../work/clock-fix-20261018/STATUS.md) |
| Restart shortcut | [Validation](../work/restart-shortcut-20261018/VALIDATION.md) |
| Startup readiness | [Readiness notes](../work/startup-fix/READINESS.md) |
| Brightness controls | [Brightness README](../work/brightness/README.md) |
| Network investigation | [Findings](../work/network/findings.md) |

These are historical observations, not guarantees about another device or a
fresh image. For example, the charging notes record a successful short test
on kernel `7.1.2-thorch20`; they do not establish overnight reliability or
battery-gauge accuracy.

## Save further development

Run `python3 scripts/snapshot-sources.py` from the repository root before
committing changes made inside nested checkouts. Review `git diff` and
`git status`, then commit and push the outer ThorDS repository. Nested build
and reference directories are ignored, so changes there need that snapshot
step. The script captures tracked diffs plus eligible untracked UTF-8 files
up to 5 MB. Keep separate backups of device data and binary artifacts.
