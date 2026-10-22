# CLAUDE.md

Guidance for Claude Code working on kbdkid5, in `model/kbdkid5/`. Read its [README.md](README.md) (the parts, how they print and go together, the commands and the CI artifacts) and [DESIGN.md](DESIGN.md) (the design with every figure) first, since this file does not repeat them. The workshop's layout, workflow and conventions are in the root [CLAUDE.md](../../CLAUDE.md).

## Scripts

Each module's docstring says what it builds or checks and how, and its constants and the comments on its steps give the details. In `model/kbdkid5/scripts/`:

- `layout.py`: the geometry as data, the ground truth until a PCB exists.
- `check_layout.py`: the layout and DESIGN.md's figures, in plain Python. To run every check without stopping at the first failure, import it and call each of `CHECKS`. A scan or a placement script takes the standoffs' and the frame bosses' rules from its records (`standoff_rules()`, `frame_boss_rules()`), never from a copy: `tmp/standoffs/scan.py`'s own copy drifted from the checks (work item 016).
- `freecad_common.py`: the STL export and the freecadcmd scaffolding.
- `pcb_shape.py`: the PCB mock, and the fused mock's fusing and measuring. `export_pcb.py` and `export_mock.py` export them, `export_slit_test.py` the slit test strips.
- `plate_shape.py`: the switch plate. `export_plate.py` exports it.
- `socket_test_shape.py`: the hand-wired frame's test strips and the switch hole strip. `export_socket_test.py` exports them.
- `frame_shape.py`: the hand-wired frame and its backing, from `socket_test_shape.py`'s cells and `pcb_shape.py`'s body. `export_frame.py` exports them.
- `tray_shape.py`: the tray, the nice!nano clamp's tab and the power switch's retainer. `export_tray.py`, `export_clamp_tab.py` and `export_power_switch_retainer.py` export them, and `export_nano_bay_test.py` cuts the test bay out of the left tray.
- `place.py` and `test_place.py` (README.md, Placing parts): `place.py` imports `check_layout.py`, never the reverse, so `check_layout.py` stays standard library only, and both run in the placement image only.

## Conventions

- When DESIGN.md and `layout.py` disagree, find which one has the bug and fix it, never pick one silently.
- `layout.py`'s tray polygons (`tray_cavity_polygon()`, `ledge_inner_polygon()`) are sharp, but `tray_shape.py` rounds every bend: `add_ledge()` rounds the ledge's inner face 2.13 wherever the outline steps in, which takes the ledge's corner away there (DESIGN.md, Tray). A FreeCAD probe or a mount near an outline corner must not count on plastic the sharp model has there: `export_tray.py`'s probe of the nice!nano north block's east end, past the column 2/3 step, found no ledge there and failed CI run 39637825633 (fixed in 3160768).
- `layout.py` imports normally without FreeCAD (put `model/kbdkid5/scripts/` on `sys.path`), as `check_layout.py` does. The FreeCAD modules (`freecad_common.py`, `tray_shape.py`, `plate_shape.py`, `pcb_shape.py`, `socket_test_shape.py`, `frame_shape.py` and the export scripts) need FreeCAD, so they run in CI only (root CLAUDE.md, Workflow).
