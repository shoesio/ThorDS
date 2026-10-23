# Development Thor deployment captured 23 October 2026

This is a read-only source/configuration snapshot of the running development
Thor. It is separate from the historical image-builder snapshot under
`state/checkouts/`. **It is not an installer or an overlay to copy onto a device.**

`rootfs/` preserves 44 deployed project text files with their observed modes,
including session/launch/window helpers, controller fixes, motion/restart
services, startup drop-ins, and CIA inbox handling. Paths beneath `rootfs/`
correspond to their original absolute paths. No game content, saves, private
console data, credentials, or firmware binaries are included.

The service override `20-user-services.conf` refers to UID 966 on this Thor.
That value is device-specific. Do not apply it blindly to a new installation.
The project account in the historical image recipe uses different defaults.

## Emulator source

The installed binary is the clock-fixed executable fingerprinted in
`manifest.json`. The retained device source declares upstream commit
`415d04c8866cb10ebcbf9ff381e82dbe924564af`, not the old image recipe's tag.

`emulator/changes.patch` contains the five changed upstream source files. It
combines the device's retained main source with the separate `shared_page.cpp`
used by the clock-object rebuild. That clock source matches the existing
`work/clock-fix-20261018/shared_page.cpp`, and the installed executable matches
the saved clock-fix candidate hash. The patch was checked against the exact
upstream commit. A complete rebuild matching the installed binary has not
been performed.

To recover this source into a new directory, from the outer ThorDS root:

```sh
git clone --filter=blob:none https://github.com/AzaharPlus/AzaharPlus.git output/deployed-emulator-source
git -C output/deployed-emulator-source checkout --detach 415d04c8866cb10ebcbf9ff381e82dbe924564af
git -C output/deployed-emulator-source apply ../../state/deployed/thor-20261023/emulator/changes.patch
```

This only restores source. Inspect the source's submodule/build requirements
before building. The on-device clock rebuild/link procedure is archived in
`work/clock-fix-20261018/`; it assumes that device's existing build cache and
is not a clean-build guide.

## Sensor source

The base sources remain in `work/gyro-20261018/libssc/` and
`work/gyro-20261018/hexagonrpc-0.5.0/`. The live retained sources matched 122
of those files, with 12 changed effective source files saved under
`sensor-source/`. To reconstruct them locally, copy those two base directories
into a new work area, then overlay the matching directories from `sensor-source/`.
The adjacent `ssc-sampler.c` is the retained device sampler source.
`manifest.json` records hashes for these overlays and the installed binaries.
No sensor binary was rebuilt during the audit. Original licenses and headers
in the base sources continue to apply.

## Verify the saved snapshot or a running Thor

From the outer repository root:

```sh
python3 scripts/verify-deployed-snapshot.py
python3 scripts/verify-deployed-snapshot.py --host thords@YOUR_THOR_IP
```

The optional SSH comparison reads only files and package versions. It does not
restart services, edit configuration, install packages, touch game state, or
request administrator access. It compares only the captured paths, not all
system files or personal data. A successful result does not mean that the
historical image recipe has been updated to reproduce this deployment.

At capture, all 52 fingerprinted deployed paths and the seven recorded package
versions matched on a second read; the kernel was `7.1.2-thorch20`. Two sudoers
files were unreadable without elevation and were not captured or verified.
Android-derived ADSP/DTB firmware was fingerprinted only, not copied; its hashes
match the earlier gyro bring-up notes.
