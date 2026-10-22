# model-workshop

FreeCAD scripts that build 3D-printable models, run headless in a container. The projects are under `model/`, listed in [model/README.md](model/README.md).

## Getting the STLs

Every push runs the CI workflow, which exports every part in the FreeCAD image built from `docker/freecad.Dockerfile`. A push that changes only markdown files and `LICENSE.txt` builds nothing, so the newest artifacts are those of the last commit that changed anything else. Open the run on the repository's Actions tab and download its artifacts. Each is named after its project, its kind and the commit it was built from, `<project>-<kind>-<short commit hash>` (for example `kbdkid5-tray-<short commit hash>`), or `<project>-<short commit hash>` for the projects with one artifact (`solder-spool-axle`, `camera-arm`). For a pull request the hash is its head commit's. The project READMEs list the files in each artifact and show the command CI runs for each export. To run one by hand, build the image first, from the repository root:

    docker build -t freecad-headless -f docker/freecad.Dockerfile docker

## The placement solver

`tools/placement/` finds where a part can go so that it keeps its rules against what is around it (work item 016): nearest a target, with the most clearance or with the least move, in x, y and z and turning about z, several parts at once where they must keep apart. It reports the answer with every rule's margin there, which rules bind and why a spot is not free (where no pose keeps every rule, it says so and what breaks at the best one it found), and draws a picture of each context: the obstacles, the least margin as contours, the region where the part is free, the target and the answer. It is generic: a project's script hands it the problem as data, as kbdkid5's `model/kbdkid5/scripts/place.py` does ([model/kbdkid5/README.md](model/kbdkid5/README.md), Placing parts, has its runs).

It and the scripts that use it run locally, in an image of their own built from `docker/placement.Dockerfile`, which holds the solver's pinned Python libraries. Build it once from the repository root, and check that the libraries import:

    podman build -t placement -f docker/placement.Dockerfile docker
    podman run --rm placement python3 -c "import matplotlib, numpy, PIL, scipy, shapely; print(numpy.__version__, scipy.__version__, shapely.__version__, matplotlib.__version__, PIL.__version__)"

The second command prints `2.5.3 1.18.1 2.2.0 3.11.2 12.3.0`. A script runs with the repository mounted at `/work`, from the repository root, for example kbdkid5's layout check:

    podman run --rm -v "$PWD":/work -w /work placement python3 model/kbdkid5/scripts/check_layout.py

The solver's own tests, on made up problems with known answers:

    podman run --rm -v "$PWD":/work -w /work placement python3 -m unittest discover -s tools/placement/tests -t tools

CI's `placement` job builds the image and runs these tests and kbdkid5's (`model/kbdkid5/scripts/test_place.py`) on every push.

## How the printer prints, and the parts

- [doc/print-model.md](doc/print-model.md): how prints come out against the model (swelling, hole sizes, slits, layers), every test print and what it settled.
- [doc/components.md](doc/components.md): the keyboards' parts, their dimensions from datasheets and calipers, with sources.

## History

This repository continues kbdkid5's history up to 8ebfb81, so the commit hashes that kbdkid5's docs, logs and work items cite resolve here. `model/kbdkid4/scripts/`, `model/solder-spool-axle/scripts/` and `model/camera-arm/scripts/` hold [Tubbles/kbdkid4](https://github.com/Tubbles/kbdkid4)'s model scripts as of its 155110d, and their history up to that commit is in Tubbles/kbdkid4 under `scripts/`.

## License

CC0 1.0 Universal, see [LICENSE.txt](LICENSE.txt).
