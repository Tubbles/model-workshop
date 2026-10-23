# 026 Whole pocket walls in the frame, the tray making room

Status: todo

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
