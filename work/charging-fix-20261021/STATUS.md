# Charging fix — staged, NOT INSTALLED

User asked how to resolve charger attach during suspend and stale battery state.
Prepared targeted update on 21Oct2026. Runtime on Thor still7.1.2-thorch19.
Bundle is fully staged /home/thords/charging-fix-20261021, all8 payload checksum
entries verified on Thor. User must run an admin command and reboot:
ssh -t thords@192.168.0.143 'sudo bash /home/thords/charging-fix-20261021/install.sh --reboot'
Keep charger connected, lidopen, save game. Password must be entered in user's
terminal; never request password in chat. Existing sudo requires password.

Root cause candidate: old local0009 removed IRQF_NO_SUSPEND globally from Qualcomm
IPCC. Latest Armada0504 explicitly replaces this blanket change, preserving
message interrupts in s2idle so attaching a charger asleep can complete. It
masks summary IRQ only for PM_SUSPEND_MEM on SM8550/SM8750, unlazy. Pinned exact
upstream d2bcf6fd33435f670f59a164c926842af91730f1 in provenance.json/UPSTREAM.json.
Applied by reversing original0009 in cached source then cleanly applying0504.
Repository old0009 deleted/new0009 state-aware patch added. linux-thorch pkgrel20.

Rebuilt kernel and matching modules7.1.2-thorch20 in cached Colima build volume.
First link failed from Mac disk exhaustion and aborted build-volume journal.
Stopped Docker/containerd; unmounted ALL vdb1 bind mounts; e2fsck repaired journal
and free counters. Mounted, removed failed/recreatable link intermediates only,
trimmed free space, restored mounts/services; host reclaimed22+GiB. Retried all
link/BTF/module/install/repack stages successfully, status0. Failed log retained
as kernel-build.failed1.log. No failed artifact packaged. Kernel config differs
only in LOCALVERSION; prior config and driver source captured.

Package built using same PKGBUILD in cached Arch root with makepkg --nodeps;
package.sh records recipe. Package metadata release verified; raw Image equals
its embedded Android boot-image Image, all13 DTBs byte-identical to previous
package AND live bootKERNEL. Binder config/build checks passed, module release
verified. New sampler syntax passes; on-device sampling JSON and nonfatal history
permission failure verified. Source helper hashes match livebaseline preupdate.
All proofs under this directory.

Installed firmware hashes already match Thor's own Android-derived ADSP/DTB
and Armada reference. No firmware replacement, sleep mode change, emulator,
controls, sound, splash, charging limits, or percentage interpolation introduced.
Updated sampler logs USB state/open-circuit voltage. Sleep guard archives at
most200 pre/post snapshots(100cycles) while retaining latest-pre/latest-post.

Installer pins currentdevice/kernel/package/helper/Image hashes, requires USB
online and>=10%, validates bundle, backs up boot/modules/helpers and kernel19
package under /var/lib/thords/charging-fix-backup-20261021, installs20 via normal
pacman boot-transaction hooks, extractsbootImage and compares to moduleImage20,
then installs two diagnostic helpers. --reboot triggers reboot only on success.
Rollback script downgrades to19 and restores helper backups; requires root.

After user says booted: verify uname20 and package20, no new failed services,
new archive helper versions, charging while awake, then repeat short charger-
attach-AFTER-lid-close test. Gauge refresh and overnight reliability still need
hardware verification; do not claim fixed until new-kernel test passes. No long
sleep tests requested. Do not revive FPS/OpenGL task during charging work.

During investigation journal -b -1 confirmed earlier shutdown was CLEAN at2%
from thords-low-battery-shutdown, not an unexplained abrupt power cut.

### 22:26 installer preflight correction
User ran installer at 22:06:58 (sudo journal confirms), but it exited before backup/transaction. Kernel/package still19. Stale `/run/thords-sleep/rgb.json` from21:31 persisted despite completed resume and caused overly strict installer check. Replaced marker-file check with actual inactive state checks for sleep.target, suspend.target and systemd-suspend.service. Updated bundle checksum and uploaded installer+SHA256SUMS; verified remote all checksums and syntax. No kernel installation performed yet; user must rerun sudo installer. Existing RGB restoration issue is separate and not changed by this preflight correction.

### 22:29 successful installation verified
After user reran installer, Thor rebooted at approx22:27. Live uname7.1.2-thorch20, pacmanlinux-thorch7.1.2-20. Installed sampler98f2b7f7679944f7cb3202d78625fa8b26591921a2488e4127753532fa7193fa and guard403064e0de8a3c5209ab766a4214e2852e0c5c4cdef22ecceec46edbe544dac1 match bundle. Boot transaction validation passed22:27:06. Awake22:29:46 Charging60%,3441600uAh,current+3760713uA,USBonline1,8.585V/2.812A. Only failed unit is preexisting bottom-panel backlight restore. Await short unplug-open, close, attach-asleep test; fix effectiveness not yet verified.

### 22:37 charger-attached-asleep retest PASSED
Running thorch20. New pre timestamp1792618259.3208723 Discharging61%,3537964uAh,USBoffline; post1792618632.6668477 Charging72%,4174660uAh,USBonlinePD. Duration373.346s (6m13s), reported gain636.696mAh. First wake snapshot already shows gain, so this cannot be explained by charge accumulated during later awake observation. Followup19.079s later73%,4207356uAh stillcharging. This reproduces previously failing cable-after-close order and now succeeds. Short-test evidence supports targeted fix; overnight/full-charge and gauge accuracy not independently established. Evidence: after-fix-sleep-test.txt, after-fix-sleep-journal.txt, after-fix-result.json.

### 22:44 battery reporting follow-up
Live kernel gauge currently Charging81%,4676560uAh,+3869480uA,4.237873V terminal/4.201419V OCV. Earlier61->72->73->81 rise is consistent with charging but does not prove discharge gauge accuracy. Gross38->2 correction earlier was present in kernel capacity AND charge_counter, so display-only smoothing cannot fix source. New IPCC patch restores ADSP battery-manager doorbells during s2idle and may address stale updates too; not independently demonstrated. Keep critical-battery shutdown intact (three10s confirmations, default5%; prior service threshold may override). Need ordinary discharge/resume evidence before claiming gauge fixed or prescribing calibration; avoid deliberate full drain or firmware reset.
