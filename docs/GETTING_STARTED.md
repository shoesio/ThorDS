# Getting started

ThorDS is an experimental source publication for developers. For an overview,
read [the README](../README.md). There is no ready-to-flash release or verified
clean-install workflow.

## Restore the source

Install Git and Python 3.9 or newer, then:

```sh
git clone https://github.com/shoesio/ThorDS.git
cd ThorDS
python3 scripts/restore-sources.py
```

The script verifies the saved file hashes, executable flags, and symlink
targets; clones the recorded commits; applies tracked changes; and copies
additional files. It includes the nested AzaharPlus checkout, its package
recipes/patches, the service masks, and both required splash assets.
The result is `build/thorch-work`. Nothing is installed on a device.

For an independent copy:

```sh
python3 scripts/restore-sources.py --destination /path/to/a/new/directory
```

Existing destinations are refused. No restore operation should be run over an
active build checkout. To restore another recorded reference, use
`--checkout work/mako-source --destination /path/to/a/new/mako-directory`.

Next read [the build guide](BUILD.md). The restored Thorch README and Makefile
provide the original build interface, but also describe desktop and internal
installation flows outside this ThorDS SD-only experiment.

## Find implementation and historical tests

| Area | Starting point |
| --- | --- |
| Kiosk session, controls, power helpers | `state/checkouts/build/thorch-work/untracked/packages/thords-kiosk/` |
| Build and kernel changes | `state/checkouts/build/thorch-work/changes.patch` |
| Emulator package and source changes | `state/checkouts/build/thorch-work/packages/azahar/` |
| Charging test | [Charging status](../work/charging-fix-20261021/STATUS.md) — read later updates too |
| Motion / gyro | [Gyro status](../work/gyro-20261018/STATUS.md) |
| Clock correction | [Clock status](../work/clock-fix-20261018/STATUS.md) |
| Restart shortcut | [Validation](../work/restart-shortcut-20261018/VALIDATION.md) |
| Startup readiness | [Readiness notes](../work/startup-fix/READINESS.md) |
| Brightness controls | [Brightness README](../work/brightness/README.md) |
| Network investigation | [Findings](../work/network/findings.md) |

Dated notes describe the original development device and may include its local
paths, old kernel assumptions, or superseded observations. They are not a
sequence of installation instructions. Refer to [current validation status](VALIDATION.md)
and [SD testing and recovery](INSTALLATION.md) before hardware testing.
