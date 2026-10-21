# 015 nice!nano on column 2, and the standoffs

Status: implemented

The user, 2026-10-21, with the plate printed: "Ive just printed the plate and I saw that you've moved some of the tray backing stand offs, such as the one in the top corner opposite of the thumb key, it moved south. Now that corner isn't as well supported anymore and might flex when i type on it. Do you agree? Do you need to do some math?", then "I think we could move the nano to be centered on the third key column from the outside, ie. "WSX<blank>" column on the left half, and "OL.<blank>" column on the right half. Then we can move back the standoff, as well as add back the ledge, giving much needed corner strength. Then we might need to shift the center standoff down one key and towards the outside one key, in order to accomodate the battery?" For the power switch: "Yeah the power switch is much easier to situate I think." Asked about the layout, the user chose "Yes, and raise the bay walls".

Later the same day: "What do you think about moving the north-east standoff one key to the left? And then adding a new standoff south east of the north easternmost key?", then "Yes queue that", and "Yes, both" for the two. First "Make sure it clears the magnet slot", then "Remember we can merge geometry and walls together as well, the standoff doesn't have to be 100 % clear of everything, the inner bore is more important". When the battery went (work item 018), the user left the center standoff where it was.

Done:

- The nice!nano 0.475 east of column 2's center line, its bay with a west wall of its own and both walls raised to the PCB's underside wherever they keep 0.5 from the sockets of either half. The power switch on column 0's north wall. kbdkid4's standoff at (18.574, 56.832) and the north ledge over columns 0 and 1 back. The center standoff at (56.091, 23.460), a key south and a key west and then 0.9 west and 0.75 south, for the plate's head hole (df02939). The north block's east end measured on the block, past the ledge's rounded corner (3160768).
- The north-east standoff one key west, at (75.724, 62.785), with S140's flat, and a sixth at (113.824, 59.214), merged with the joint block, the magnet slot at 67.511 cut through it. `check_layout.py` holds every standoff's bore 0.6 from the joint's voids, 0.832 at the sixth, and FreeCAD measured 0.8316 on both trays (c412684, CI run 39657567625).
- DESIGN.md (Mounting, Tray, Parts in the tray) has the figures and why.

The sixth standoff's ring does not clear the magnet slot: the slot cuts 0.468 into it, and only the bore keeps clear of it, by 0.832, as the user's later message allows. Square to the slant, the standoff would have to stand 0.468 further in for its ring to clear the slot.

Still open:

- None of it is printed. Plates and frames printed before df02939 have their head holes and drills at the old standoffs.
- The frame's walls lose 2.80 mm2 each at S130 and S131 to the raised east wall, the most of any socket (DESIGN.md, Hand-wired frame).
