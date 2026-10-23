# ThorDS clock update — 18 October 2026

Built and staged, NOT INSTALLED. User must run:
`sudo python3 /home/thords/install-clock-fix.py`
after saving and closing their game.

Linux date, NTP and PMIC RTC matched reference UTC when checked. The current
Azahar shared-page clock instead uses launch time plus emulated ticks, which
lose suspended time and lag when emulation runs slowly.

Built against the exact installed source/build retained on the Thor:
/home/thords/azahar-build/azaharplus-unified-source-20260917-415d04c88,
baseline executable SHA256 in manifest.json. Compiled just shared_page.cpp,
replaced that member in a copy of libcitra_core.a and relinked a separate binary.
The existing build tree, original binary and running emulator were not changed.
The cached link command named old Qt 6.11.1 paths, so the isolated link uses
the installed Qt6 .so.6 SONAMEs, as does the current executable. No system
library or dependency updates were needed. Disabled use of a potentially stale
precompiled header for the single-object compilation only.

SystemTime mode without a movie clock override now samples host wall time
with existing local-time/offset conversion. FixedTime and movie overrides use
the original emulated tick progression. Shared-page time updates every second,
rather than every five emulated seconds, to correct HOME shortly after resume.
No class layout or save-state serialization changes.

Tests extract the changed functions from the production source into a stubbed
C++ harness: suspend with no guest progress, slow emulation, millisecond
precision, configured date offset, fixed clock, and movie override all pass.
Native AArch64 object compilation and relink passed. ldd resolves every library;
new executable --help succeeds offscreen. Installer syntax passed; baseline and
candidate hashes are pinned. Actual HOME/sleep behaviour awaits installation.

Installer backs up /usr/bin/azahar and configuration, pauses the session
supervisor, closes the old Azahar through the existing recovery helper,
atomically replaces the executable, and resumes the supervisor. No system clock
setting changes, no save modifications, no reboot or persistent sudo grant.

Separately verified that the previously requested D-pad and 3x resolution fixes
are now installed on the Thor (the user applied their staged installers).
