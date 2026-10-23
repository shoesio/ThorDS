# HOME brightness bridge

Installed as a per-user systemd service, using ~/.local/bin/thords-home-brightness.
Reads the 0x00050001 block in the emulated CFG save; never modifies NAND. HOME level 3 was confirmed by the user against raw block value 0x0300 (levels are 1–5).

Levels map to bottom-panel 10/25/45/70/90 percent; top panel gets 10 extra percentage points, matching the existing balancing approach. These are electrical percentages, not measured luminance.

Only changes physical brightness after two matching reads of a changed HOME level. Initial startup preserves existing brightness. Select+D-pad hotkeys still work and are not overridden unless HOME's level changes. HOME may need its settings panel closed before it saves a change.

Parser rejects truncated saves, unexpected headers, missing blocks and out-of-range levels. Tested all five levels against fake backlight files, safe bounds and invalid values. Runtime HOME interaction verification pending.

Disable: systemctl --user disable --now thords-home-brightness.service
