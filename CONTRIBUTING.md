# Contributing

Start with [the build guide](docs/BUILD.md) and
[validation status](docs/VALIDATION.md). Contributions currently target the
experimental sources rather than a supported binary release.

Run the restore-tool tests with `python3 -m unittest discover -s tests -v`.
After source restoration, validate package metadata with
`python3 scripts/package-manifest.py validate` inside the restored tree.
The source-checks workflow additionally exercises runtime policy tests and
compiles/assembles the kiosk payload on Linux.

Make changes in the appropriate restored checkout. Run
`python3 scripts/snapshot-sources.py` from this repository's root before
committing, then inspect the resulting patches and source files. Refreshing
snapshots intentionally removes stale extra files that no longer exist in
the nested checkout. Preserve all upstream licenses and attribution.

Do not submit console dumps, credentials, firmware dumps, games, saves,
personal logs containing secrets, or images seeded with private test data.
For hardware reports, provide the source commit/image checksum, device variant,
kernel version, steps to reproduce, and a small relevant log excerpt with
personal information removed. State whether the observation came from a
fresh SD image or an existing development installation.

The most useful next work is a full clean image build with pinned download
inputs, integration of the remaining device-side fixes, account/data
provisioning, and a documented spare-card boot test. No change should require
writing to an existing user's working installation merely to run source tests.
