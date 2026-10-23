# ThorDS startup mark — version 2

The built-in image generation tool edited the first startup splash. The saved production asset is [boot-splash.png](../../build/thorch-work/packages/thords-kiosk/rootfs/usr/share/thords/boot-splash.png).

## Final edit prompt

Edit this startup splash. Remove ALL text, the lightning bolt, cyan color, button dots, and every decorative detail. Keep only two simple horizontal rounded rectangle OUTLINES stacked vertically, centered on pure black. The upper rectangle outline is pure white. The lower rectangle outline is medium gray (#808080). Both have black interiors, same width and height, same clean uniform stroke, a modest gap between them, and subtly rounded corners. Keep the two-rectangle symbol at the existing icon size and move it to the exact center of the canvas now that the wordmark is removed. Absolutely no letters, text, lightning bolt, dots, shadows, glows, gradients, or additional shapes. Flat minimalist console startup mark. Preserve the landscape black canvas.

## Display policy

Only DSI-2 displays the startup mark. Other outputs have solid black backgrounds. The working Azahar hide/reveal and fixed-2x frame-generation policy is retained.

## Boot changes and measurements

Before changes: systemd reports 3.793 seconds kernel + 22.863 seconds userspace = 26.657 seconds to finish system startup. Sway starts at approximately 15.78 seconds, the session helper at 28.44 seconds, and Azahar at 30.46 seconds after kernel start. These figures do not prove HOME is interactive at those times.

Settings rewrites were consolidated. A device-side test using disposable copies of the actual configuration produced byte-for-byte identical output, taking 0.173 seconds before and 0.027 seconds after on a warm system. This is a small measured saving; it is not a cold-boot improvement claim.

The boot hardware report, previously taking 11.113 seconds during boot, is deferred to a 90-second timer. It was not a direct dependency of the console session; the purpose is to reduce competing startup work. The console's separate GPU/hardware diagnostic is deferred by 60 seconds. The existing performance governor is now applied before the console service, rather than after multi-user.target. The 12-second renderer settling guard remains in place to preserve the stable frame-generation startup.

Timing markers in /var/log/thords/boot-timing.log record session, settings, seed, controls, performance, emulator launch and render-window reveal milestones. A fresh installed boot must be measured before claiming an overall boot-time reduction.
