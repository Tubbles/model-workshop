# CLAUDE.md

Guidance for Claude Code working on the solder spool axle, in `model/solder-spool-axle/`.

## What this is

`model/solder-spool-axle/scripts/export_spool_axle.py` exports the axle of a solder spool holder (a 19 x 39.5 mm body with a 7.9 x 2.6 mm stub on each end for the cradle), built from Part primitives with no STEP input. A groove in the body takes the rim inside the spool's bore at one face, so the spool lies flat. Its position assumes the rim flush with that face of a 27 mm spool centered on the body (`SPOOL_RIM_CENTER_FROM_FACE_MM`). The script checks the solid's volume against the analytic value, rounded edges included.

It imports `board_step.py` from `model/kbdkid4/scripts/` for the STL export with its closed mesh check and for the freecadcmd scaffolding. The freecadcmd quirks are in the root [CLAUDE.md](../../CLAUDE.md) (FreeCAD scripts). Read them before changing the script.

## CI

The `solder-spool-axle` job in `.github/workflows/ci.yml` exports the axle from the repository root into `spool/` and uploads `Solder_Spool_Axle.stl` as the `solder-spool-axle-<short commit hash>` artifact. The hash is this repository's commit, the pull request head's for pull requests (`github.sha` is a merge commit there). The job's log prints the axle's figures.
