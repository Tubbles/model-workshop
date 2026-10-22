# CLAUDE.md

Guidance for Claude Code working on kbdkid4's printed parts, in `model/kbdkid4/`. Read its [README.md](README.md) first (the parts, where the board comes from, the commands and the CI artifact), since this file does not repeat it. The workshop's layout, workflow and conventions are in the root [CLAUDE.md](../../CLAUDE.md).

## The kbdkid4 repository

Tubbles/kbdkid4 has no model code and never reads anything from here. The user (2026-10-21): "I want that agent to reference this repo for measurements etc, instead of the other way around, so kbdkid4 becomes a pure librepcb repo again." The scripts read kbdkid4's own board files, never a copy. The STEP is the output of the one STEP job in kbdkid4's `project/jobs.lp`, taken from kbdkid4's CI and not from its committed `output/v1/`. The user (2026-10-21): "Yeah fetch the step from the CI output instead".

## Scripts

Each script's module docstring says what it builds and how, and its constants and the comments on its steps give the details. Beyond them:

- `model/kbdkid4/scripts/board_step.py`: the shared helpers, the freecadcmd scaffolding among them. The solder spool axle's and the camera arm's export scripts import it too, so a change to it reaches their STLs.
- `model/kbdkid4/scripts/tray_shape.py`: what the tray export shares with the case export.
- An export script ends in `run_and_exit(main)`, so importing one would run it. Shared code goes into `board_step.py` or `tray_shape.py`, which an export script imports from its own directory on `sys.path`.
- `model/kbdkid4/scripts/export_pcb.py` offsets the outline's wire and each hole's wire separately, since FreeCAD's `makeOffset2D` on the whole face would shrink the holes along with the outline.
- `build_case` in `model/kbdkid4/scripts/export_case.py` returns a shell in the STEP frame. A probe set it against the tray there for both halves and found no overlap, the rim flat on the step and 0.3 mm around the tray.

## Conventions

- kbdkid4's default board file (the first entry in its `boards/boards.lp`, currently `boards/board_1.1/board.lp`) is the design ground truth (outline polygon vertices, mounting drills). Cross-check what the script detects from the STEP against it rather than trusting either alone. The scripts resolve it through `boards/boards.lp`, so renaming a board directory needs no script change.
- Probes for kbdkid4's geometry, which go into the export script (root CLAUDE.md, Workflow): census cylinder-face radii, sample wall thickness with `distToShape`, compare volumes against analytic values.
- LibrePCB's populated STEP export imports as one `App::Part` per component, the switch package (two 3D models) with a second container nested inside. `Part.getShape` on a component's container returned those switch bodies unplaced in x and y while single-level components came out right; walking each container's tree and multiplying the ancestor placements onto every `Part::Feature` shape places everything correctly. It comes from kbdkid4's STEP job with `(variant default)` instead of `(variant none)`, run from a temporary jobs file, kept untracked at `work/kbdkid4-probes/jobs_step_populated.lp`:

  ```
  (librepcb_jobs
   (job dfaf1cb4-a033-430d-a16f-ffa28a439fd6 (name "STEP Model")
    (type 3d_model)
    (board default)
    (variant default)
    (output "{{PROJECT}}_{{VERSION}}.step")
   )
  )
  ```
