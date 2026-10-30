# 034 Standoff tubes on the frame's underside

Status: implemented (2026-10-29, b2dc184 and 3ca0954)

The user, 2026-10-29: "Could you add a cylindrical wall around the 6 mounting holes on the underside of the frame board? Make it the same height as the hotswap pocket walls. And naturally we'll have to shrink the 6 opposing standoffs in the tray by the same amount, and I might have to use longer screws but that should be fine. That way I can lay down the wire as i am soldering it and even hot glue it down without having to worry about things getting in the way". On the tube's shape: "standoffs own outline, basically project the standoff onto the frame board's underside". kbdkid5 has no PCB, so the tray need not seat one (doc/log/2026-10-29.md).

Specification:

- Frame, both halves: under each of the six mounting drills a tube, in plan the standoff's outline as the tray builds it at its top (5.8 across with its flats) less the frame's drill, from the ceiling down the pocket walls' depth (1.80, so z 9.5 to 7.70 in the tray). The tube of the standoff merged with the joint block stops `FRAME_TRAY_CLEARANCE_MM` short of the block's inner face. Every tube keeps that clearance in plan from every tray body standing within its heights, as the walls do, and stays out of the pockets, the tab slots and the tab wires' rooms.
- Tray, both halves: the standoffs end at the tubes' mouth, z 7.70, bored down to the floor's top as now. The merged standoff drops outside the joint block, which stays as it is, and an insert pressed in from above clears the block on its way down.
- S140's walls on the left half stand whole, joined to the tube: the standoff no longer reaches their heights, so `FRAME_WALLS_CUT_BACK` empties.
- The backing keeps its cutouts around the standoffs, which still pass through its heights.
- The screws at the drills are 1.80 longer. README.md names the length.

Verify: `check_layout.py` passes. CI's frame and tray exports pass and print the tubes and the standoffs' top. DESIGN.md and README.md follow.

Deviation: three tubes reach into tab wires' rooms, by 0.142 (S122) and 0.050 (S140) on the left half and 0.179 (S220) on the right, where the standoffs stood over the rooms' full height before. They are held to those figures rather than clipped (DESIGN.md, Hand-wired frame, Tubes). S140's walls on the left half stand 0.080 from their tube as modelled, which the print's swelling closes.
