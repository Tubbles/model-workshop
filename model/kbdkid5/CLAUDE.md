# CLAUDE.md

Guidance for Claude Code working on kbdkid5, in `model/kbdkid5/`. Read its [README.md](README.md) (the parts, how they print and go together, the commands and the CI artifacts) and [DESIGN.md](DESIGN.md) (the design with every figure) first, since this file does not repeat them. The workshop's layout, workflow and conventions are in the root [CLAUDE.md](../../CLAUDE.md).

## Scripts

Each module's docstring says what it builds or checks and how, and its constants and the comments on its steps give the details. In `model/kbdkid5/scripts/`:

- `layout.py`: the geometry as data, the ground truth until a PCB exists.
- `check_layout.py`: the layout and DESIGN.md's figures, in plain Python. To run every check without stopping at the first failure, import it and call each of `CHECKS`.
- `freecad_common.py`: the STL export and the freecadcmd scaffolding.
- `pcb_shape.py`: the PCB mock, and the fused mock's fusing and measuring. `export_pcb.py` and `export_mock.py` export them, `export_slit_test.py` the slit test strips.
- `plate_shape.py`: the switch plate. `export_plate.py` exports it.
- `socket_test_shape.py`: the hand-wired frame's test strips and the switch hole strip. `export_socket_test.py` exports them.
- `tray_shape.py`: the tray and the nice!nano clamp's tab. `export_tray.py` and `export_clamp_tab.py` export them, and `export_nano_bay_test.py` cuts the test bay out of the left tray.

## Conventions

- When DESIGN.md and `layout.py` disagree, find which one has the bug and fix it, never pick one silently.
- `layout.py` imports normally without FreeCAD (put `model/kbdkid5/scripts/` on `sys.path`), as `check_layout.py` does. The FreeCAD modules (`freecad_common.py`, `tray_shape.py`, `plate_shape.py`, `pcb_shape.py`, `socket_test_shape.py` and the export scripts) need FreeCAD, so they run in CI only (root CLAUDE.md, Workflow).
