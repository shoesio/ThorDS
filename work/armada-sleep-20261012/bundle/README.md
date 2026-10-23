# Armada sleep port for ThorDS

Pinned Armada source: `fd0ed0f1a285fbbccc5fa63969d4e176cb0ae4e6`.

The current Armada suspend dispatcher selects native `s2idle`; it does not
offer `deep`. ThorDS already uses native `s2idle`, USB autosuspend, lid wake
gating, PCIe sleep bandwidth floors, regulator sleep-state votes, and the
gamepad/UART sleep fixes. Keep those existing integrations.

This update adds the missing audio changes from Armada:

- 0528: suspend the sound card and its streams instead of ignoring suspend.
- 0529: fail graph creation correctly when the DSP rejects the request.
- 0530: release AudioReach stream/port graphs during suspend, then restore
  source graphs before sink graphs on resume.

0528 and 0529 are copied directly. 0530 is adapted to the existing ThorDS
7.1.2 source, which lacks Armada's push-pull buffer bookkeeping fields.
The suspend/resume ordering and graph lifecycle follow Armada's patch.
The original patches and pre/adapted source files are retained in the Mac workspace at /Users/admin/ThorDS/work/armada-sleep-20261012/.

The RGB policy follows Armada's 45-armada-rgb sleep hook using the existing
ThorDS LED interfaces. It stops the battery RGB updater if active, records
current LED brightness, turns off the LEDs, then restores brightness and the
previous updater state at wake. It does not change the saved RGB configuration.

The SN3112 controller patch applies to other handheld hardware; the Thor uses
HTR3212 LEDs, so that patch is not imported. The fake-suspend Gamescope process
freezer is not used by Armada's native-suspend path and is not imported.

Validation: patches apply to the existing kernel source; kernel compilation
and packaging logs are retained here. RGB restoration checks cover active and
inactive updater state, repeated pre/post recovery, and unrelated LED channels.
Hardware wake/audio/charging checks remain pending installation.

Build status: complete. A clean kernel rebuild succeeded after an offline
filesystem check repaired the build disk. The new package is linux-thorch
7.1.2-19. The local package repository validation passed (12 packages, 4754
uniquely owned files). Kernel logs and package logs are retained in that Mac workspace. The
rollback package uses the exact Image currently installed on Thor (matching
SHA-256), version 7.1.2-18. The earlier failed output was not packaged.

`install.sh` checks device, running kernel, file hashes and sleep-guard version,
backs up the prior kernel/modules/sleep guard and package database entry, then
installs the kernel package and RGB sleep helper. It does not reboot.

Console service audit: Linux reaches graphical.target in 9.442 seconds, while
the latest emulator render-windows-visible marker is 22.68 seconds. Most RAM
use is emulator/graphics, with over 8 GiB available; there is no memory pressure.
The live account is an ordinary /etc/passwd user and homectl lists no home areas.
The installer masks the optional units listed in console-units.list: managed
homes, container/namespace/extension managers, report/update notification sockets,
the full core-dump manager, serial login prompt, and automatic hardware report
timer. Existing service states are recorded for rollback. Keep account lookup,
networking/DNS, input, audio, fan/battery safety, SSH and journaling. Keep OpenSave
save backups per the user's explicit preference. XWayland is currently required
by the installed Azahar wrapper.

Early loading image: build Armada's splash renderer without X11 and preserve
the existing ThorDS image colours (gain 1.0). Convert the PNG to Armada's ASP1
format without changing artwork. Start from a mkinitcpio early hook and retain
the drawer across switch-root. The real-root service adopts the existing drawer
through its root-owned PID file. Before Sway starts, use Armada's takeover
handshake to drop DRM master but retain the framebuffer until Sway commits.
The daemon exits after handoff. Keep Sway's existing loading image for the
remaining emulator startup interval. No bootloader flashing is involved.

The installation bundle also includes a local, on-device autodetect drop-in.
It shrinks the normal initramfs using this Thor's sysfs hardware inventory;
the fallback preset skips autodetect and remains complete. It is deliberately
not packaged into generic images generated on a VM. Installation rebuilds both
images through the existing kernel package hooks and boot transaction.

Use install.sh --reboot for the combined update and reboot. rollback.sh restores
the previous kernel package and saved service states, removes early splash and
local autodetect policies, and restores the prior sleep guard. Hardware boot,
audio, controls, charging and a brief lid-close/wake check remain pending.
