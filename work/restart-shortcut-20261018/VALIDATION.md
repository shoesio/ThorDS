# Home + Back recovery shortcut

Installed on Thor, 18 October 2026.

- Hold Home (virtual Xbox BTN_MODE) with either RGB button (Back/KEY_RECORD,
  or the F24 hardware shortcut) for three continuous seconds.
- Release either button before three seconds to cancel.
- Fire once until both buttons are released; do not act on autorepeat.
- Solo RGB actions are deferred to release so a recovery chord preserves lights.
- Read input without grabbing it, preserving normal HOME functionality.
- Keep input descriptors across rescans, clear held state on device loss.
- Ask the hidden Azahar controller window to close through Sway. Set
  confirmClose=false at startup so the close can flush saves without a dialog.
- Wait eight seconds for clean exit, then TERM with three seconds grace; KILL
  only if still stuck. pidfds prevent signals from reaching a reused PID.
- Target only Azahar descended from thords-session. Never launch a second
  process: the existing session supervisor relaunches HOME after exit.

Checks: hold timing, early release, repeated hold latch, solo RGB, device loss,
Python compilation, shell syntax. Full deployed input-path test injected a
3.3-second Home + Back hold through the virtual controller: service fired once,
Azahar PID 1219 closed cleanly and PID 4820 replaced it. No force signal was
needed. User confirmed pictures returned after an initial black-screen boot.

Backups: /var/lib/thords/restart-backup-20261018/ on the Thor.
Installed files: /usr/bin/thords-hardware-buttons,
/usr/bin/thords-configure-controls,
/usr/local/libexec/thords/thords-restart-azahar,
/etc/systemd/system/thords-restart-azahar.service.

Reset cannot preserve unsaved game progress. If the emulator is hung, a forced
termination cannot guarantee completion of any save already in progress.
