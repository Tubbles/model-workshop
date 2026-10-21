# model-workshop

FreeCAD scripts that build 3D-printable models, run headless in a container. The projects are under `model/`, listed in [model/README.md](model/README.md).

## Getting the STLs

Every push runs the CI workflow, which exports every part in the FreeCAD image built from `docker/freecad.Dockerfile`. Open the run on the repository's Actions tab and download its artifacts. Each is named after its project, its kind and the commit it was built from, `<project>-<kind>-<short commit hash>` (for example `kbdkid5-tray-<short commit hash>`), or `<project>-<short commit hash>` for the projects with one artifact (`solder-spool-axle`, `camera-arm`). The project READMEs list the files in each artifact.

The STLs come from those artifacts: CI runs every export, with the commands the project READMEs show. kbdkid5's layout check is plain Python and runs anywhere: `python3 model/kbdkid5/scripts/check_layout.py`.

kbdkid4's parts are built from the board of [Tubbles/kbdkid4](https://github.com/Tubbles/kbdkid4): the STEP model its latest successful CI run on main made, and the board files of that run's commit ([model/kbdkid4/README.md](model/kbdkid4/README.md)).

## How the printer prints, and the parts

- [doc/print-model.md](doc/print-model.md): how prints come out against the model (swelling, hole sizes, slits, layers), every test print and what it settled.
- [doc/components.md](doc/components.md): the keyboards' parts, their dimensions from datasheets and calipers, with sources.

## License

CC0 1.0 Universal, see [LICENSE.txt](LICENSE.txt).
