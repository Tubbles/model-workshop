# model-workshop

FreeCAD scripts that build 3D-printable models, run headless in a container. Each project has a directory of its own with its scripts and a README that describes its parts.

| Directory | What it holds | README |
|---|---|---|
| `kbdkid5/` | kbdkid5, a wireless split keyboard whose halves join into one board: its tray, switch plate, PCB mock, fused mock and test strips | [kbdkid5/README.md](kbdkid5/README.md) |
| `kbdkid4/` | The printed parts of kbdkid4, a split wireless keyboard designed in LibrePCB: its tray, switch plate, PCB replica and carrying case | [kbdkid4/README.md](kbdkid4/README.md) |
| `solder-spool-axle/` | The axle of a solder spool holder | [solder-spool-axle/README.md](solder-spool-axle/README.md) |
| `camera-arm/` | An arm that holds a Raspberry Pi Camera Module 2 over a stock Ender 3 V2 | [camera-arm/README.md](camera-arm/README.md) |

## Getting the STLs

Every push runs the CI workflow, which exports every part in the FreeCAD image built from `docker/freecad.Dockerfile`. Open the run on the repository's Actions tab and download its artifacts. Each is named after its project, its kind and the commit it was built from, `<project>-<kind>-stl-<short commit hash>` (for example `kbdkid5-tray-stl-<short commit hash>`), or `<project>-stl-<short commit hash>` for the projects with one artifact (`solder-spool-axle`, `camera-arm`). The project READMEs list the files in each artifact.

The FreeCAD exports run in CI only, never locally. What runs locally is plain Python, such as kbdkid5's layout check, `python3 kbdkid5/scripts/check_layout.py`.

kbdkid4's parts are built from the board files in [Tubbles/kbdkid4](https://github.com/Tubbles/kbdkid4): its STEP model, `boards/boards.lp` with the default board it lists, and `circuit/circuit.lp`. CI checks out kbdkid4's default branch for every run. A push to kbdkid4 does not start this repository's CI, so after a board change run the workflow by hand from the Actions tab.

## How the printer prints, and the parts

- [doc/print-model.md](doc/print-model.md): how prints come out against the model (swelling, hole sizes, slits, layers), every test print and what it settled.
- [doc/components.md](doc/components.md): the keyboards' parts, their dimensions from datasheets and calipers, with sources.

## License

CC0 1.0 Universal, see [LICENSE.txt](LICENSE.txt).
