# ThorDS startup identity

Generated with the built-in image generation tool. Installed asset:
`../../build/thorch-work/packages/thords-kiosk/rootfs/usr/share/thords/boot-splash.png`

## Final generation prompt

Use case: logo-brand. Create a finished startup splash image for ThorDS, a premium dual-screen handheld gaming console. 1920x1080 landscape. Pure black background. A very small, precisely centered original minimalist emblem suggesting two stacked screens and a subtle lightning slash, above the exact wordmark "ThorDS". Crisp flat white geometry, one tiny electric cyan accent. Restrained, sophisticated, timeless console boot identity, excellent negative space: entire emblem and wordmark occupy only the central 22 percent of image width and 30 percent of height. Elegant custom geometric sans typography. No glow, no gradients, no metallic rendering, no 3D bevels, no extra text, no loading indicators, no mockup, no Nintendo marks. A single production-ready clean splash, not a concept sheet.

## Startup fixes

- System startup uses the same fixed-2x, top-only XWayland launcher as the working live session.
- Force XWayland even before its socket exists during cold startup.
- Hide both Qt Wayland and XWayland windows on mapping; reveal only settled game surfaces.
- Keep the verified output mapping: DSI-2 large top image at 120 Hz; DSI-1 lower touch image at 60 Hz.
- Preserve the 12-second per-process settling interval before window placement.
- The button helper closes the parent session lock descriptor.
- The session watches its compositor socket and terminates helpers when that compositor exits.
- Repeated short HOME launch failures retry HOME with native rendering for that session instead of opening the desktop launcher.
- Installer backs up system assets and replaces old user-local overrides with links to the system scripts.
