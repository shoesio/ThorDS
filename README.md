# ThorDS — experimental developer sources

ThorDS is a Linux/Azahar console-session experiment for the AYN Thor:

    power -> Linux -> Wayland -> Azahar -> emulated 3DS HOME Menu

This repository publishes the development sources, patches, configuration,
and historical hardware notes. **It is not a supported operating-system release.**
There is no ready-to-flash image, and a complete clean build and fresh-device
installation have not been verified. Some updates tested on the original
Thor remain separate experiments rather than integrated image components.

## Start here

- [Getting started](docs/GETTING_STARTED.md) — restore and inspect the sources.
- [Build guide](docs/BUILD.md) — environment, commands, private-data handling, and remaining build gaps.
- [SD testing and recovery](docs/INSTALLATION.md) — spare-card testing and acceptance criteria.
- [Validation status](docs/VALIDATION.md) — exactly what has and has not passed.
- [Contributing](CONTRIBUTING.md) and [third-party notices](THIRD_PARTY_NOTICES.md).

```sh
git clone https://github.com/shoesio/ThorDS.git
cd ThorDS
python3 scripts/restore-sources.py
```

This restores source into `build/thorch-work`; it does not build an image,
connect to a Thor, or modify a device. Python 3.9+ and Git are required. Choose
`--destination /path/to/a/new/directory` to restore elsewhere. Existing
checkouts are never overwritten.

## Repository layout

| Path | Contents |
| --- | --- |
| `scripts/` | Snapshot and restore tooling |
| `state/checkouts.json` | Upstream URLs and exact commits |
| `state/checkouts/` | Local patches and extra source/assets for those checkouts |
| `state/source-hashes.json` | Snapshot file hashes, executable flags, and symlink targets |
| `work/` | Historical scripts, experiments, and validation records |
| `docs/` | Current developer setup and testing guides |
| `build/thorch-work/` | Restored working source; generated locally and ignored by this repository |
| `upstream/`, `output/`, `backups/`, `testdata/` | Local-only reference sources, outputs, and data; excluded |

## Protect an existing setup

Source checks run on a development computer. Hardware testing requires a
separate expendable SD card and an already working Linux boot/recovery path.
This project does not provide a bootloader flashing procedure. The inherited
Thorch source contains internal-storage installers; those are outside the
ThorDS SD-only testing guide and can erase data if explicitly invoked.

No console keys, HOME Menu, games, saves, device backups, downloaded firmware,
or complete images are included. Two explicitly listed splash assets are
included because the kiosk package needs them. Do not publish images built
with private console data or personal credentials.

## Save development changes

Before committing changes inside nested source checkouts, run:

```sh
python3 scripts/snapshot-sources.py
git status
git diff
```

Then commit and push this outer repository. Review the generated snapshots:
build and reference directories themselves are ignored. The snapshot records
tracked changes plus eligible additional source files, safe symlinks, and the
two splash assets. It does not back up your device or binary build products.

## License and acknowledgements

See [LICENSE](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md).
ThorDS builds on Thorch, ROCKNIX, Azahar/AzaharPlus, Armada, MAKO, libssc,
hexagonrpc, and their contributors. Each component retains its own notices.
