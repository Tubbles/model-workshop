# 020 Shelves under the backing's edges

Status: implemented

The user, 2026-10-22: "However I see that close to the edge there isn't much supporting the backing, and the backing plate itself is kind of floppy, especially in PETG. Is it possible to utilize the tray rim/ledge by pulling it in, giving the backing some more needed support along the edges?", then, on shelves or a thicker backing, "Yeah let's try shelves first."

Why not the whole ledge: the bottom row's sockets stand 0.387 from the south ledge's face, so the ledge cannot come in at its full height. The backing hangs lower (z 6.383 as printed to 7.233), and the ledge is solid from the floor up, so a step on the ledge's face below the backing can reach in under the backing's edge, and the frame with its backing still drops in from above: nothing of it hangs below the backing but its screw heads.

Scope:

- A shelf on the ledge's inner face along the south edge (all its steps) and the outer edge (west on the left half), on both halves, its top at z 6.0 as modelled, reaching 2.5 in under the backing's edge (3.0 from the ledge's face). At the usual print model that leaves 0.33 between the shelf and the backing as printed, 0.18 if the shelf's top rises like an up-facing bottom (doc/print-model.md), so the shelf catches a sagging backing rather than holding it up: a shelf above the backing's underside would lift the frame off its standoffs or press the pads into the sockets.
- The shelf keeps 0.5 in plan from every screw head it would reach (the left half's column 0 bosses on the outer edge) and stops where the power switch's cradle, body and retainer stand at the north end of the outer edge.
- Not now: the slant, where the magnet slots open in the joint face along most of the free length, and the north edge, mostly taken by the power switch, the PCB connector's zone, the nice!nano and the reset button. A first print shows whether the shelves help.
- `check_layout.py` checks the shelf against the backing's underside, the screw heads and the parts near it, with DESIGN.md's figures.

Done (DESIGN.md, Tray, Shelves under the backing, has the figures):

- `layout.py` holds the shelves (`BACKING_SHELF_TOP_Z_MM`, `BACKING_SHELF_REACH_MM`, `backing_shelf_pieces()`, `backing_shelf_polygon()`, `backing_shelf_notches()`), `tray_shape.py` fuses them onto both trays right after the ledge, rounded like the ledge's face, and checks what they added, and `export_tray.py` measures each straight run of their face, its heights and reach, and the notches. The nice!nano test bay keeps the shelves outside its box, so its STL does not change, and no other export builds from the tray: the frame's walls are cut back from the tray only within their own heights, above the shelves.
- The outer edge's shelf stops 0.5 short of the power switch's body on its way into the cradle, not only of the seated switch: with the knob going first through its slot, the body starts the knob's length south of its seat, and its west face lies inside the shelf's reach.
- The left half's three column 0 screw heads get a notch each. The placement solver's answers for those bosses, which test_place.py's check pass puts in their place, would need none, so `check_layout.py` prints the notches and `export_tray.py` holds them to DESIGN.md's figures.
- `check_layout.py` checks the shelves' face, top and reach against DESIGN.md, their gap under the backing as printed both ways their top may rise, the outer edge's shelf's end, their clearance from the heads by the heads' gathered rule and from the parts and the tray's other bodies and voids, and takes them wherever it takes the tray's pieces (the frame's bosses and heads, the standoffs' merges, the wire rooms and strips as printed, the pry slot and the toothpick), so the placement solver sees them too.

Open: the export's figures, which only CI shows, and a first print: whether the frame still sits flat on its six standoffs and whether the backing gives less along the south and outer edges (README.md, 3D printed hand-wired frame).
