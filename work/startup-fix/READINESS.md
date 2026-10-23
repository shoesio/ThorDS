# Renderer readiness instead of a fixed startup delay

The window manager now waits for two correctly sized render windows, unchanged geometry for two seconds, and (when the MAKO layer is loaded) two active renderer contexts without errors. It then applies the existing verified screen placement. The desktop controller window remains hidden by compositor policy.

Device validation on 2026-09-25:

- Latest optimized cold boot: kernel 3.233 s + userspace 12.802 s = 16.036 s for system startup (previously 26.657 s).
- Cold boot session starts at 18.45 s, emulator launches at 20.01 s, fixed-delay window reveal at 36.02 s.
- New readiness check tested through a HOME restart: emulator launches at 214.26 s, render windows revealed at 224.45 s (10.19 s).
- Warm restart and cold boot differ; this is not a measured six-second cold-boot gain.
- HOME screenshot verified, top output 120 Hz and lower output 60 Hz.
- Current process has top MAKO generation active, lower generation inactive, and no runtime errors.
- Shell integration checks pass.

The test script is running from the staged home-directory file. Permanent system installation of the updated window manager is pending administrator authentication.
