# 026 Whole pocket walls in the frame, the tray making room

Status: implemented

The user, 2026-10-23, on the hand-wired frame's socket pockets: "Looking at the frame's hotswap socket pockets, on the lowest row, both left and right variants are missing geometry on two places on every pocket, what is that supposed to be? Looks like it's drawn by a drunk person", then: "The three rightmost pockets also have a second notch close to the tray wall corner. These pockets are so fine in detail that its paramount they are 100% intact. I see along the vertical edge they have been cut off as well. They print like shit when they are cut into like this, cause extreme blobbing and stringing", and: "The three rightmost have 3 cuts, I didn't see the second you found so its 3 now actually".

What cuts them: `frame_shape.py` cuts each pocket's walls back to `layout.FRAME_TRAY_CLEARANCE_MM` (0.5) from whatever of the tray stands within the walls' heights (`wall_tray_obstacles()`). The tray's bodies keep the PCB version's clearances from the sockets, not from the frame's walls, whose outer face lies 0.925 outside the socket (gap 0.125 at the frame's fit, wall 0.8). On the bottom row the ledge stands 0.632 from the sockets, and its notch under each socket's south lobe, lowered to z 6.98 below the walls, is about 0.5 longer than the lobe at each end, so the wall's two south corners are cut back to 0.5 from the full height ledge either side. CI run 39834968878 (c2b6220) lists every key it cut, as "walls: cut back from the tray at":

- left half: S100, S101, S102 (1.44 mm2 each), S103 (2.33), S113, S123, S133 (0.89 each), S130, S131 (2.80 each), S140 (0.64), S143, S153, S163 (1.03 each)
- right half: S103 (0.89), S110 (0.31), S113 (0.89), S122 (0.25), S123 (1.03), S133, S143, S153 (0.89 each), S150 (0.17), S163 (2.33)

S143's, S153's and S163's extra 0.14 on the left half, and S123's on the right, come from the ledge at the outline's step west of them (edges 4 and 5, 6 and 7, 8 and 9, and 3 and 4 on the right).

Scope:

- Every socket's pocket walls in the frame, on both halves, are whole: the strip's ring at the frame's fit (`socket_test_shape.wall_ring()`), less only the tab slots and the key's footprint holes, as on the pocket strip. Nothing of the tray cuts them, and the frame's export fails if anything would.
- The tray makes the room instead. Wherever a tray body stands within the walls' heights and within `FRAME_TRAY_CLEARANCE_MM` of a wall's outer face in plan, that body gives way by its own rule, widened from the socket to the wall: the ledge's socket reliefs (`socket_ledge_reliefs()`), the step corners, the cavity wall where it reaches, the nice!nano's raised wall pieces (`nano_raised_wall_boxes()`), the standoffs' flats, the joint block and the dowel boss, and whatever else the walls' list above traces back to.
- Each body keeps its own minimums as it gives way (DESIGN.md: the joint's 1.0 between voids, the standoffs' plastic around the insert bore, the nice!nano bay's fit and the raised walls' shortest stretch). Where a body cannot give way without breaking one, that conflict is reported with its figures, not settled by cutting a wall or a minimum.
- `check_layout.py` holds every pocket wall to the clearance from every tray body on both halves, so a later tray change cannot cut a wall again.
- DESIGN.md, the module docstrings, kbdkid5's README and CLAUDE.md follow. doc/print-model.md gets the user's observation that cut pocket walls print with heavy blobbing and stringing.

Done:

- Every pocket's walls stand whole on both halves but S140's on the left half (below). The tray gives way to them (model/kbdkid5/DESIGN.md, Tray, Frame pocket walls): the ledge's socket reliefs reach the walls' outer face plus 0.5 at both ends, down to the same z 6.98; the bottom row's walls get a 0.041 pocket in the cavity wall (0.040 beside S153); the nice!nano's raised walls stop 0.5 short of the walls; on the right half the standoff at (56.091, 23.460) gets a flat for S122's walls, leaving 1.049 of plastic around the bore, and the upper dowel boss a notch for S150's walls, 1.073 from the joint's voids.
- `frame_shape.py` no longer trims the walls. It checks that the tray keeps 0.5 from them, and the frame's export fails where it does not. `check_layout.py`'s walls check holds every pocket's walls to the 0.5 on both halves, and fails on exactly the keys CI run 39834968878 cut when the tray's changes are taken out. `export_tray.py` measures the clearance on the built tray.
- doc/print-model.md has the user's observation of cut walls.
- CI run 39973159940 (f4b3145) built both: the frame's walls whole around 24 of 25 sockets on the left half (S140's cut back) and 25 of 25 on the right, and the built trays at least 0.500 from them. Its first run, 39971231975 (94633a8), failed on S140's cut back (a boolean result handed to makeOffset2D) and on the bottom row's wall pockets ending at the walls' top, which left the cavity wall 0.459 from their top edge. check_layout.py now takes every body within 0.5 above or below the walls' heights.
- S140 on the left half: its walls come 2.471 from the center of the standoff at (75.724, 62.785). A flat 0.5 short of them would leave 0.371 of plastic around the bore against the 0.6 minimum, so its walls stay cut back 0.5 from the standoff as flattened, as before (`layout.FRAME_WALLS_CUT_BACK`), which shaves the walls' rounded corner along the flat for S140's socket. Offered on 2026-10-23, with an overlay of each (`tmp/frame_pockets/s140_options.py`, untracked): 1, the standoff moved 0.56 to (75.911, 62.262), the placement solver's nearest spot keeping every standoff rule and the bore 1.1 from every frame wall (a probe, `tmp/frame_pockets/s140_standoff.py`), leaving 0.66 around the bore and the plate's head hole 0.50 from S131's cutout, its 0.5 minimum; 2, the standoff kept and its flat moved in, 0.37 around the bore; 3, as today. The user: "S140 3 keep it as today".

Nothing is open.
