# 020 Shelves under the backing's edges

Status: implemented

The user, 2026-10-22: "However I see that close to the edge there isn't much supporting the backing, and the backing plate itself is kind of floppy, especially in PETG. Is it possible to utilize the tray rim/ledge by pulling it in, giving the backing some more needed support along the edges?", then, on shelves or a thicker backing, "Yeah let's try shelves first."

Scope:

- A shelf on the ledge's inner face along the south edge (all its steps) and the outer edge, on both halves, under the backing's edge and below its underside, so it catches a sagging backing rather than holding it up: a shelf above the backing's underside would lift the frame off its standoffs or press the pads into the sockets. DESIGN.md (Tray, Shelves under the backing) has why the whole ledge cannot come in, and the shelves' figures.
- The shelf keeps clear of every screw head it would reach and of the power switch at the north end of the outer edge.
- Not now: the slant, where the magnet slots open in the joint face along most of the free length, and the north edge, mostly taken by the power switch, the PCB connector's zone, the nice!nano and the reset button. A first print shows whether the shelves help.
- `check_layout.py` checks the shelf against the backing's underside, the screw heads and the parts near it.

Done (68b0797):

- `layout.py` holds the shelves, `tray_shape.py` fuses them onto both trays right after the ledge, and `export_tray.py` measures them. CI run 39758435587 built them with every figure as DESIGN.md has it. The nice!nano test bay's STL does not change, and no other export builds from the tray.
- The left half's three column 0 screw heads each get a notch in the outer edge's shelf. kbdkid5's CLAUDE.md (Conventions) says why `export_tray.py`, not `check_layout.py`, holds the notches to DESIGN.md.
- `check_layout.py` checks the shelves' face, top, reach, gap under the backing and clearances, and gives them to the frame's boss and head rules, so the placement solver sees them too.

Open: a first print: whether the frame still sits flat on its six standoffs and whether the backing gives less along the south and outer edges (README.md, 3D printed hand-wired frame).
