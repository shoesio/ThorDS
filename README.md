# ThorDS

A dedicated Linux distribution for the AYN Thor whose normal user experience is:

    power -> Linux -> Wayland -> Azahar -> emulated 3DS HOME Menu

The Linux desktop is not the product. Linux exists to expose the Thor hardware to Azahar.

## Safety

The image-builder is intentionally SD-only during bring-up.
No ThorDS script writes Android internal storage or flashes ABL automatically.

## Layout

- `upstream/thorch` — pristine hardware-enablement reference
- `upstream/azahar` — pristine Azahar source/provenance reference
- `build/thorch-work` — disposable patched build tree
- `state` — exact upstream commits used
- `output` — finished image copies/checksums

## Source backup

This repository preserves local scripts, patches, configuration, investigation notes,
and validation records. It is a development snapshot, not a tested distribution release.

`state/checkouts.json` records each nested source checkout's origin and exact commit.
`state/checkouts/<checkout-path>/changes.patch` preserves its changes against that commit
(including staged and unstaged changes). The adjacent `untracked/` directory preserves
additional UTF-8 source files up to 5 MB, retaining executable permissions. To recover a
checkout, clone its recorded origin at its recorded commit, apply `changes.patch` with
`git apply` when nonempty, then copy the contents of `untracked/` into that checkout.
Run `python3 scripts/snapshot-sources.py` before committing further nested-checkout work.

Build trees, downloaded binaries, firmware, disk images, device backups, game files,
saves, and screenshots are excluded. These remain local and need separate backup.
Upstream source history is referenced by commit rather than copied here.
