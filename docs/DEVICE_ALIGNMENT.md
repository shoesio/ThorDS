# GitHub versus the running Thor — 23 October 2026

**The historical image recipe does not reproduce the current development
Thor.** A read-only live audit confirmed drift and saved the missing deployed
source/configuration separately in
[state/deployed/thor-20261023](../state/deployed/thor-20261023/README.md).

## Confirmed differences

| Area | Historical image snapshot | Running development Thor |
| --- | --- | --- |
| Emulator launch | MAKO frame-generation launcher | Native XWayland launcher; no MAKO launch environment |
| Kiosk package | Recipe `0.2.0-2` | Installed package `0.2.0-4`, with further direct file edits |
| Emulator source | Package pinned to `AZAHAR_PLUS_2126_1_B`; original source snapshot at `7407e4f7…` | Retained source at `415d04c8866cb10ebcbf9ff381e82dbe924564af`, plus device changes and a separate clock replacement |
| Window readiness | Two-second stability wait plus MAKO checks | One-second stability wait; MAKO checks removed |
| D-pad and gyro | Axis-based D-pad mappings; missing motion setting | Hat-based D-pad mappings and `cemuhookudp` motion |
| Startup helpers | Earlier package payload | Additional CIA inbox and user-service drop-ins |
| Sensors | Some archived sources/patches outside the image profile | Live motion/sensor services, locally built libssc and hexagonrpc, and Android-derived matching DSP firmware |

Package labels alone were insufficient: package-file verification confirms that
the installed Azahar and several kiosk files differ from their installed package
records. The installed Azahar SHA256 exactly matches the clock-fixed candidate
already archived in `work/clock-fix-20261018/manifest.json`, confirming that fix
is installed despite the old status note's initial “not installed” heading.

## Preserved and checked

- 44 deployed project scripts/configuration/service files, including previously
  missing native launch/session/window helpers.
- Effective emulator changes against the correct upstream commit, including the
  separately built clock source. The patch applies cleanly to that commit.
- Twelve sensor-library/daemon source differences, the sampler source, and the
  loader configuration. Another 122 retained sensor-source files match the
  previously archived sources.
- Fingerprints for the emulator, sensor binaries/library, splash renderer,
  Android-derived ADSP/DTB firmware, and the installed OpenSave executable.
  Binary executables and firmware were not copied into GitHub.
- A second read verified all 52 captured deployment fingerprints, seven selected
  package versions, and the running kernel against the saved manifest.

Charging sampler and sleep guard, performance helpers, the power policy,
Sway configuration, and the splash assets match their saved build-source copies.
The matching kernel is `7.1.2-thorch20`; installed `linux-thorch` is `7.1.2-20`.

The audit did not use sudo. Two package-owned sudoers files could not be read.
It did not capture personal emulator state, Wi-Fi credentials, save-sync
credentials/database, console data, games, saves, or a full disk image.

## What remains

The running scripts and retained source changes are now separately preserved,
but the historical build profile still needs deliberate integration of this
native-launch deployment, sensor packages/provisioning, and the correct emulator
source. The old frame-generation integration test checks the old recipe; it
must not be presented as proof of alignment with the live Thor.

The deployment verifier provides a read-only drift check for the captured paths.
It is not a full system audit, a device installer, or proof of a reproducible
image. A full build and spare-card boot test remain necessary before calling a
new image equivalent to the working development setup.

No service was stopped or restarted, and no system configuration, boot files,
bootloader, games, saves, or running emulator were changed during this audit.
