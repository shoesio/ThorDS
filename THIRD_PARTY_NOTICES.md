# Third-party sources and attribution

ThorDS builds on existing handheld Linux and emulator work. This repository
preserves source provenance in [state/checkouts.json](state/checkouts.json).
A snapshot patch is relative to the commit named there; restore that upstream
checkout to obtain its original source, notices, and license files.

| Component | Origin and license information |
| --- | --- |
| Thorch | `https://github.com/thorch-os/thorch` — GPL-2.0-or-later for Thorch-specific source; see restored `LICENSE` |
| ROCKNIX | `https://github.com/ROCKNIX/distribution` — component-specific licenses; hardware enablement, recipes, and runtime provenance remain upstream |
| Azahar / AzaharPlus | Origins and commits in the checkout manifest — GPL-2.0-or-later; preserve `license.txt` and upstream artwork notices |
| MAKO | `https://github.com/eugeniosegala/MAKO` — package declares GPL-3.0-or-later; use restored `LICENSE.md` and `THIRD_PARTY_NOTICES.md` |
| Armada splash and kernel references | `https://github.com/armada-os/armada` — retained `Armada-LICENSE.md`, splash `LICENSE.md`, and `UPSTREAM` notices |
| libssc and sensor integration references | `work/gyro-20261018/libssc/LICENSE`, adjacent `COPYING`, and source SPDX headers; GPL-3.0-or-later |
| hexagonrpc | `work/gyro-20261018/hexagonrpc-0.5.0/COPYING` and source headers |
| stb headers | Notices embedded in the retained headers; follow their individual license options |

The splash source and notices are under
`state/checkouts/build/thorch-work/untracked/packages/thords-kiosk/early-splash/`.
The two explicitly included splash assets are the artwork already used by this
ThorDS development tree; no game screenshots or console dumps are included.

Downloaded firmware, packaged applications, and other image inputs keep their
own licenses. This is a source publication, not a distribution of a complete
operating-system image or console system files. ThorDS is not an official AYN,
Nintendo, ROCKNIX, Thorch, or emulator-team product.
