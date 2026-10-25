# CLAUDE.md

Guidance for Claude Code working on the camera arm, in `model/camera-arm/`. Read its [README.md](README.md) first (the parts, the hardware, the assembly, where the numbers come from, the CI artifact), since this file does not repeat it. The workshop's rules are in the root [CLAUDE.md](../../CLAUDE.md). The current design is work item 029.

## The script

`model/camera-arm/scripts/export_camera_arm.py` builds every part from Part primitives, with no STEP input. Its docstring has the sources, the assumptions, the print orientations and the frames. The freecadcmd quirks it works around are in the module docstring of `model/kbdkid4/scripts/board_step.py`.

- `LENS_X_MM`, `LENS_IN_FRONT_OF_UPRIGHT_MM` and `LENS_HEIGHT_SHARE_OF_FIRST_ARM` place the lens, and `camera_yaw_and_pitch()` aims it at the bed's center at mid travel, so the case's pose follows from them. The `FIRST_ARM_*` constants are the first print's pose, which the lens height and the height report are worked out from.
- The rail stack is laid out from the upright's bolt (`upright_bolt_front()`): `SPACER_LENGTH_MM`, the arm base and the Pi mount, then the shims. A change to the spacer's length or the bolt moves the arm along the rail, and its post stands exactly `HEAD_CLEARANCE_MM` off the head's reach.
- The arm, the spacer and the shim share `T_RAIL_HALF_PROFILE_MM`. The spacer and shim are cut off at `SLOT_MOUTH_CHAMFER_DEPTH_MM`.
- The script checks each part is one valid solid with a closed mesh, probes the T-rails, the spacer and shim rails (nothing in the slot's mouth chamfer) and the bar's insert bores, checks the shells, the board model, the arm, the rail, the spacer, the Pi mount and the camera's field of view do not overlap, checks a 5 mm straight driver reaches the ear screws past the front shell, lists planar faces facing down past 45 degrees in the print orientation, and measures the clearances to the upright, the gantry's right end, the bed and knobs over the travel, the print volume, the print head's reach, the Pi case and the cable's corridor, and how much of the print area the lens sees at each bed Y position, plain and with the upright, the gantry end and the X beam at their lowest as occluders.
- The face check reads planar faces only: curved ones, such as the insert bores' ceilings, are not listed.
