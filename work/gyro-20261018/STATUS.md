# Thor gyro bring-up — 18 October 2026

LIVE AND CONFIGURED. Matching SH5001 firmware booted successfully.

Target: thords@192.168.0.143, kernel 7.1.2-thorch19. Passwordless sudo is
temporarily enabled in /etc/sudoers.d/thords-gyro-session. Remove it when done.

Original Azahar configuration and pre-change dmesg are backed up under
/var/lib/thords/gyro-backup-20261018. Azahar motion settings have NOT been changed.

Built hexagonrpc v0.5.0 and libssc v0.4.4 natively on the Thor in
/home/thords/gyro-build, using Meson 1.9.1 from its source tarball. Installed
under /usr/local, with /etc/ld.so.conf.d/thords-motion.conf. Added compiler/build
dependencies, libqmi and protobuf-c via pacman; no existing packages upgraded.
Two larger dependency transactions failed during downloads without installing
anything; a smaller transaction succeeded.

Reference: https://github.com/kettlelinux/kettlelinux at
1a3f558a3284b89374e483ca361ea0474749d505. Four hexagonrpc patches,
one libssc rate patch and android_parts.py are copied here with their license.
Source archive hashes match the reference PKGBUILDs.

Read-only copies of Android vendor config, persist sensor state and DSP
libraries are under /var/lib/thords/gyro/qcom. Android vendor has multiple
extents; device-mapper is unavailable, so prepare-sensors.py reconstructed a
temporary vendor image from read-only source reads, then mounted a read-only
loop device. All loop devices/mounts were cleaned up and the temporary image
was removed. Android persist was never written.

The kernel's soc0 omits four platform fields demanded by sns_reg_config.
qcom/socinfo overlays the earlier Thor experiment's HDK/Unknown/0/65536 files,
with symlinks to live soc_id (603) and revision (2.0). The HDK selection agrees
with this device's kailua_icm4x6xx_0.json. These are compatibility values, not
newly read Android sysfs measurements. First sensor attach lacked these fields
and the sensor PD might need reboot to reinitialize.

Enabled /etc/systemd/system/thords-sensors.service and thords-motion.service.
Sensor daemon runs as fastrpc; udev grants its group /dev/fastrpc-adsp only.
DSU bridge runs as thords on 127.0.0.1:26760, starts its SSC sampler on client
subscription, and suppresses stale/missing readings. Azahar already subscribes
to this port even while its configured motion engine is motion_emu.

Current problem: sensors service remains running inside fastrpc invocation,
but SSC QMI service 400 is absent. CLI reports SSC QMI Service not found.
No new ADSP crash or SMMU faults appeared during these attempts. A root-PD
daemon probe did not help; both transient probes were stopped. Do NOT stop
remoteproc0 to reset ADSP: upstream notes that this can reset the whole SoC.

Checks passed: strict sampler C compilation; DSU length, offsets, CRC rejection,
units/axis rotation unit checks; systemd service verification (only an unrelated
pre-existing splash warning). Live samples, orientation, boot and suspend are
still unverified. Python bridge uses Thor landscape rotation from reference;
DSU gyro axis/sign mapping still needs physical verification.

After first reboot, SSC service 400 appeared, but discovery returned no accel
or gyro, even with default-only filtering disabled in a temporary build (now
restored). Android persist has nonzero SH5001 calibration; other IMUs have zero
defaults. Installed firmware lacked every SH5001 string; this Thor's Android
firmware includes the SH5001 driver. Extracted its own Android ADSP and DTB
read-only, assembled their ELF segments, and staged them in Linux only:

- adsp.mbn SHA256 e771ab967310bc210147d5d0f9e455802c35564584d1ed26e64a2eb4e9c2470c
- adsp_dtb.mbn SHA256 660fd8f2051bd2dd8694d1b36b70bc339faf6d86b0f80462395e8d229f376477

Old firmware and all four /boot files are in gyro-backup-20261018. Used guarded
boot-transaction prepare/commit to regenerate embedded firmware and KERNEL;
validation passed, rollback retained, pending reboot. Did not stop ADSP live.
One failed extraction leaked a read-only loop device because the runtime
directory was absent; detached it explicitly, recreated directory, extraction
completed, and verified no loop devices remained. Temporary vendor image removed.

Added Home + Back shortcut in work/restart-shortcut-20261018. Live synthetic
chord closed Azahar cleanly and supervisor restarted HOME. User confirmed
pictures after initially black-screen boot. No direct display setting changed.

DSU axis transformation now follows Azahar Android ndk_motion.cpp landscape
rotation=1 and compensates for desktop UDP sign changes. Flat gravity becomes
3DS (0,-1,0); live orientation still needs user testing. Motion settings remain
unchanged pending real samples.

Second reboot was explicitly authorized and completed. Both sensors now stream
at approximately 60 Hz. Verified live DSU packets: 100-byte length, CRC32,
increasing counters, finite acceleration in g and rotation in degrees/s. Axis
algebra matches Azahar Android's landscape acceleration and gyroscope mapping.
No ADSP crash/SMMU fault in the new boot. Boot image validation passed; boot
transaction had already been automatically confirmed.

Installed the local thords-configure-controls variant to preserve physical
motion at startup. Azahar's profile motion_device is engine:cemuhookudp with
default=false; UDP remains 127.0.0.1:26760. Changed the config only while the
emulator was closed cleanly and its supervisor temporarily paused. The first
attempt correctly stopped before editing because pgrep still saw the exited
child as a zombie under its paused parent; reran checking the zombie state,
then resumed the supervisor in a finally block. Replacement emulator is running.
Verified a normal HOME picture via compositor screenshot (top-verified.png).

User confirmed: "Yes, motion works" in-game. Suspend/resume has not been tested
during this session, to avoid interrupting their game test.
Removed /etc/sudoers.d/thords-gyro-session and checked passwordless sudo is no
longer available. Final services are active; fresh sensor data is flowing.
