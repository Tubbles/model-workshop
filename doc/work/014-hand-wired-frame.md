# 014 Hand-wired frame and backing

Status: implemented

The user, 2026-10-21: "I guess the next step is for me to print all these things, the pcb-replacement frame board, the plate, the tray, and start populating the components and see how it all fits together?", and for the frame: "the frame board left and right after that". Asked how far the frame should go, the user chose "Full wiring frame" (the whole half, a DO-35 diode cradle beside each socket, grooves for the row and column wires) and "One piece per half" for the backing.

Then the scope cut, the same day: "Ok let's just skip the diode and wire fittings, first iteration is just the frame board and backing standoffs". So this iteration is the frame and one backing per half, both halves, with no diode cradles and no wire grooves: the wires run between the frame's underside and the backing, as on the socket test strips. The cradles and grooves wait in TODO.md.

Done: `model/kbdkid5/scripts/frame_shape.py` and `export_frame.py`, the `kbdkid5-frame` CI job, the frame's plan geometry in `layout.py` and its checks in `check_layout.py`. DESIGN.md (Hand-wired frame) has the design and its choices, README.md (3D printed hand-wired frame) how to print and try it.

Still open:

- The thumb's socket has no boss near it on either half (DESIGN.md, Hand-wired frame, Bosses), so its backing reaches it unsupported and only its pocket holds it against a switch going in.
- The sockets of S100 and S130 on both halves, and S122 and S150 on the right half, have no boss north of them, only south of them and at their corners (S120 and S102 until the nice!nano moved, work item 015).
- The bottom row's sockets have no room for a boss south of them, so the backing under them reaches out past the bosses north of them.
- In the tray, the thumb switch's center post and pegs, which reach 1.4 below the frame, overlap the parking boss in plan, and S150's east peg (the west one on the right half) the upper dowel boss, as they would under a PCB. That goes to the user before the tray changes.
- Nothing has been printed yet.
