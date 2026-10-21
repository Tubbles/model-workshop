# model-workshop

FreeCAD scripts that build 3D-printable models, run headless in a container. The projects are under `model/`, listed in [model/README.md](model/README.md).

## Getting the STLs

Every push runs the CI workflow, which exports every part in the FreeCAD image built from `docker/freecad.Dockerfile`. A push that changes only markdown files and `LICENSE.txt` builds nothing, so the newest artifacts are those of the last commit that changed anything else. Open the run on the repository's Actions tab and download its artifacts. Each is named after its project, its kind and the commit it was built from, `<project>-<kind>-<short commit hash>` (for example `kbdkid5-tray-<short commit hash>`), or `<project>-<short commit hash>` for the projects with one artifact (`solder-spool-axle`, `camera-arm`). For a pull request the hash is its head commit's. The project READMEs list the files in each artifact and show the command CI runs for each export.

## How the printer prints, and the parts

- [doc/print-model.md](doc/print-model.md): how prints come out against the model (swelling, hole sizes, slits, layers), every test print and what it settled.
- [doc/components.md](doc/components.md): the keyboards' parts, their dimensions from datasheets and calipers, with sources.

## History

This repository continues kbdkid5's history up to 8ebfb81, so the commit hashes that kbdkid5's docs, logs and work items cite resolve here. `model/kbdkid4/scripts/`, `model/solder-spool-axle/scripts/` and `model/camera-arm/scripts/` hold [Tubbles/kbdkid4](https://github.com/Tubbles/kbdkid4)'s model scripts as of its 155110d, and their history up to that commit is in Tubbles/kbdkid4 under `scripts/`.

## License

CC0 1.0 Universal, see [LICENSE.txt](LICENSE.txt).
