# CLAUDE.md

Guidance for Claude Code working on the camera arm, in `model/camera-arm/`. Read its [README.md](README.md) first (the parts, the hardware, the assembly, where the numbers come from, the CI artifact), since this file does not repeat it. The workshop's rules are in the root [CLAUDE.md](../../CLAUDE.md).

## The script

`model/camera-arm/scripts/export_camera_arm.py` builds every part from Part primitives, with no STEP input. Its docstring has the sources, the assumptions and the frames. The freecadcmd quirks it works around are in the module docstring of `model/kbdkid4/scripts/board_step.py`.

- `CAMERA_YAW_DEGREES`, `CAMERA_PITCH_DEGREES` and `HEAD_BAR_BACK_CENTER_MM` set the case's fixed pose.
- The arm is clipped at its print frame's bed plane, so its axis-aligned base gets 45 degree faces at worst.
- The layout depends on the assembly order (README.md, Assembly).
- The script checks each part is one valid solid with a closed mesh, probes its key features (the arm's bolt hole, counterbore and bar insert bores among them), checks the T-nut's margins in the slot (neck, turn, plate overlap on the lips, bolt engagement), flags planar faces facing down past 45 degrees in the print orientation, checks the board model, shells and arm do not overlap and a 5 mm straight driver reaches the ear screws past the front shell, measures the clearance to the upright, the gantry's right end, the bed and knobs over the travel and the print volume, and works out how much of the print area the lens sees at each bed Y position, plain and with the upright, the gantry end and the X beam at their lowest as occluders.

`work/camera-arm.md` holds its design notes.
