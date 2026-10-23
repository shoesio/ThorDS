# Build the experimental sources

## Verified scope

The automated source checks restore the pinned Thorch tree and nested
AzaharPlus checkout, verify the saved source hashes, check package metadata,
run the ThorDS frame-generation and power-policy tests, and compile/assemble
the kiosk package. This does not compile the entire emulator and kernel or
produce a boot-tested SD image. See [validation status](VALIDATION.md).

## Restore source on a development machine

```sh
git clone https://github.com/shoesio/ThorDS.git
cd ThorDS
python3 scripts/restore-sources.py
cd build/thorch-work
```

Python 3.9 or newer and Git are required. The restore script clones the exact
recorded commits, applies local patches, and restores additional source,
executable permissions, service-mask symlinks, and the splash assets. It refuses
to overwrite an existing destination. To test without affecting an existing
build checkout, run it with `--destination /path/to/a/new/directory`.

The build's recipe for AzaharPlus fetches its own pinned tag and submodules;
the restored nested checkout also preserves the historical local emulator
work. These are separate records: not every device-side experiment is applied
by the package recipe.

## Linux/container build environment

Use the restored `README.md` and `docs/build.md` for the full host dependency
list. Native package and image builds need an Arch-compatible Linux environment,
AArch64 execution or working emulation, and root/chroot/loop-device facilities.
macOS cannot run those Linux build operations directly. The saved Makefile
supports Docker/Podman and stores case-sensitive build files on Linux volumes.

The existing container entry points are:

```sh
make docker-image-pull
make docker-doctor
make docker-sync
make docker-kernel
make docker-packages
make docker-build
make docker-check
```

If the published builder image is unavailable, `make docker-image-build`
builds it from the restored Dockerfile. `docker-doctor` reports the upstream
CI host requirements as well; its native fast-CI host matrix is Linux x86_64.
The package compilation tested for this snapshot ran on Linux AArch64.

These commands describe the existing build interface; they are not a verified
full-build transcript. Plan disk space for source, compiled objects, rootfs,
package caches, and a raw image at the same time. The publication check host
had only about 13 GiB free, so a full kernel/emulator/image rebuild was not
attempted. Do not assume the image's final size is the build-space requirement.

## Build configuration

Review `config/thorch.conf`, `manifests/packages.json`, and each package recipe
before building. The saved configuration still has development choices:

- `THORCH_USER` defaults to `thorch`, while the kiosk service runs as the
  separately declared `thords` account. Do not assume those are interchangeable.
- Kernel/runtime downloads use `ROCKNIX_KERNEL_RELEASE=latest`; the source
  reference is pinned, but this download is rolling. A reproducible release
  must pin a matching available image/checksum and verify its provenance.
- Upstream userspace packages and rootfs URLs are rolling inputs as well.
- Some gyro, clock, and other device-side updates remain in dated `work/`
  directories and are not integrated into the image package recipes.
- Accounts are locked when no build-time password is supplied. The inherited
  Thorch firstboot flow and ThorDS kiosk account provisioning still need
  clean-device validation. No default/shared password is published.

For development, choose your own account provisioning process and keep any
passwords outside Git. Never distribute an image containing your credentials.

## Private console data

`THORDS_TESTDATA_DIR` is an optional local-only build input. Leave it unset
for shareable output. It copies private data into the image if explicitly set;
that image must not be published. The repository contains no console keys,
HOME Menu files, games, saves, or Android firmware dumps.

The historical session expects AzaharPlus state under
`~/.local/share/azaharplus-emu` and configuration under
`~/.config/azaharplus-emu`. Its HOME autoboot currently targets a particular
European HOME Menu layout/content file and requires `sysdata/otp.bin`.
This is not a generic console-data importer. Use the emulator's own documented
setup/export process with your data and validate it before enabling kiosk
HOME autoboot on another console dump.

## After a successful image build

Use `make check IMAGE=output/thorch-arch-aarch64.img` in the restored source
tree, then follow [the SD testing and recovery notes](INSTALLATION.md).
A successful package build or image check does not establish that a new
image boots correctly on hardware.
