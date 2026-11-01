# 045 The tray's wall whole over the magnet slots

Status: implemented (2026-11-01)

Above the joint block the slanted wall was cut back over each magnet slot, up to the rim, so a magnet could drop straight down into its slot. The user, 2026-11-01: "Make it so the wall is full, right now it looks really bad with four visible cuts in the wall when the whole thing is assembled", "I'll push it in from the inside", and "Just don't touch anything except the topmost wall".

Specification:

- The slot cut stops at the block's top, so the wall above it stands whole and overhangs each slot's face side by 0.3. Nothing else of the tray changes.
- The magnet at 48.26, whose slot the sixth standoff walls off on the cavity side, passes 2.8 as printed between the wall and the standoff for its 3.0. Asked, the user chose to force it.

Verify: `check_layout.py` passes, and CI's tray export logs measure the wall over each slot as the 0.8 wall.
