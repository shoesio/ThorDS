# OpenGL comparison, 20 October 2026

User authorized checking plausibility and switching Azahar to OpenGL for Captain
Toad's steady slowdown. Confirmed game saved and restart authorized.

Installed AzaharPlus 2126.1.B-12 has ENABLE_OPENGL=OFF. Current Vulkan log:
Mesa Turnip 26.1.6, Adreno 740, Vulkan 1.4.354. On-device EGL probe confirms
hardware OpenGL 4.6 compatibility context, vendor freedreno, renderer FD740.
No settings or installed binary changed so far.

Device work: /home/thords/opengl-test-20261020. Native standalone CMake 4.1.2
(downloaded official Kitware AArch64 release) configures a copy of the retained
installed source. Preserved cached BOOL feature flags and Release build, enabled
OpenGL alongside Vulkan. Included the installed live-clock replacement source
from azahar-build/clock-fix-20261018/shared_page.cpp. Original installed executable
matches that clock-fix binary SHA256:
47186fdc18c6b4b1e9003ad75538cadd7a6689daaaac7ab51ae88917432870d3.

Build is detached on Thor: nice -n10 ninja -C build -j4 azahar.
Logs build.log, completion build.status. Installed package and original build
remain untouched. Build progress is not an ETA.

run-test.py is staged but NOT RUN. It pauses the user-owned kiosk supervisor,
closes its original emulator using the existing clean restart helper, copies
current config to an isolated XDG_CONFIG_HOME, sets renderer=1 and explicit
default=false in the copied settings, then launches the test binary using the
original process environment and xcb. Original NAND/data and game saves remain
in their normal locations; no second emulator runs concurrently. On exit it
resumes the original Vulkan kiosk, preserving the installed binary/settings.
Touch device work/stop-test to request a clean close and resume Vulkan.

Still required: successful build, ldd/--help checks, launch test, inspect log for
hardware OpenGL (not software fallback), verify both windows and user-visible
HOME, then ask user to compare Captain Toad in the same troublesome scene.
Build must finish before performance assessment to avoid compiler load bias.

## Verified running

Build finished with exit 0. Runtime libraries resolve, offscreen --help succeeds.
Test launched after clean exit of original emulator PID1211. Supervisor PID1002
is paused for the test; candidate PID77906. Candidate SHA256:
dd1b0ccfdddbe86c775939461c0fe33085729ff42ba7fbbbdaf71e0955c473b3.
Installed executable SHA unchanged. OpenGL log confirms core-profile OpenGL 4.6,
Mesa26.1.6-thorch1, freedreno, FD740. Both render windows visible (1920x1080 top,
1240x1080 bottom). Screenshot visually checked: HOME present on both screens.
Shader cache logs one old transferable cache version rejection/rebuild; no
subsequent OpenGL errors during startup. Config is isolated under test/config;
original global config was not switched. CPU compiler tasks have finished.

Awaiting user Captain Toad gameplay comparison. Right-eye rendering stays
disabled. Test can be stopped with: touch /home/thords/opengl-test-20261020/stop-test
which cleanly closes candidate and resumes original Vulkan kiosk. No reboot
required. Do not invoke the usual restart helper for the candidate directly: its
process check intentionally matches the installed /usr/bin/azahar only.
