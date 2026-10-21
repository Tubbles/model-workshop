# 004 Parts in the tray

Status: implemented

The nice!nano bay (USB window, hold-down bar, snap hook, ribs, grooves), the power switch, reset button and battery connector mounts in the north wall, the battery's locating ribs, and the clear zone for the PCB connector. Clearance checks for every part in `model/kbdkid5/scripts/check_layout.py`.

`model/kbdkid5/scripts/layout.py` gives every mount as an axis-aligned box in the left half's frame (`MountBox`): `mount_bodies()` the plastic the tray adds, `mount_voids()` what it cuts, `wire_rooms()` the room the wires need behind every lead. Every printed fit goes through `printed_fit()`. The figures that wait on a caliper are `MountFits` (the nice!nano's length and width, the hook's lip, the bar's clearance, the battery header's front lips), which `export_tray.py`'s key=value words override for a test print. `build_tray()` fuses the bodies one by one (the hook's lip as its 45 degree triangle) and cuts the voids (the USB shell's channel and the USB window, kbdkid4's rounded window with an outer chamfer, from the shell's mouth out, the reset pin hole as a flat-topped teardrop, the hook's slots with their bed edges and the blade's chamfered), each checked by its volume and probed. DESIGN.md, "Parts in the tray", has every figure, the bridges, the wire room and what mirrors how. On both halves `check_layout.py` checks the mounts against the tray, the parts, the sockets, the standoffs and the joint, the hook's strain and the wire rooms, and `export_tray.py` measures every mount against DESIGN.md figures it transcribes and finds no plastic in the PCB connector's zone as printed or the wire rooms.

What was decided on the way, the review's fixes included, is in doc/log/2026-10-17.md (tags #mounts, #nano, #hook, #window, #battery, #wires, #mirror, #check).

Still open, all waiting on the parts in hand or a test print:

- A caliper on the nice!nano: the board's length and width (33.3 x 18.0 from the render, `nano_length` and `nano_width`), its pin rows' insets (1.31 and 1.44, which side is which), the P1.01/P1.02/P1.07 pads and the shell's tab slots (11.08 between centers or across outsides), which the grooves cover both readings of. A board wider than 18.1 runs the north rib into the PCB connector's zone as printed.
- The snap hook and the bar printed and tried: the lip's 0.8 onto the board (`hook_lip`), its 0.1 over the board's edge and the bar's 0.1 over the shell as printed (`bar_clearance`), whether the blade flexes far enough without breaking (1.61 % strain as printed by the cantilever formula, not tested) and whether the lip lets the board go with a firm pull.
- The east ribs' places (2.0 from the board's ends) against the parts on the nano's edge.
- Dropped 2026-10-21: the battery header's hold (the `battery_shoulder` lips or a strap). The tray no longer holds the battery or its connector (work item 018).
- None of the power switch's and the reset button's fits (cradle, retainer and its socket, the reset button's socket, slots, notches) has been printed. Their parts' figures come from drawings, and work item 013 has what is open on them. The reset button sits in its socket under a blob of hot glue.
- Whether a USB-C plug seats fully. The window opens at the shell's mouth, and as printed the wall face it opens from, around the channel, swells 0.2 north of the mouth, so an overmold that has to reach the mouth would stop 0.2 short of it (0.25 with the board at its farthest south). Where the plug's overmold stops against the receptacle is not known here: try a cable in the printed bay.
