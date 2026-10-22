# 022 Shelves under the backing along the north edge

Status: implemented

The user, 2026-10-22: "Also we could think about adding backing shelf support to the north wall as well", then, to a shelf over columns 4 and 5 and column 3's east part, notched for the screw heads it meets: "Yes that sounds good, go ahead".

Scope:

- Work item 020's shelves on along the north edge from the slant to the reset button: outline edges 13 to 17, on both halves, from 0.5 clear of the upper dowel boss and its fill at the slant's end to 0.5 short of the reset button's east side wall, by 020's rules (DESIGN.md, Tray, Shelves under the backing).
- Notched for the screw heads it reaches, after work item 021: the left half's (101.249, 72.989) on edge 13 and (75.724, 76.101) at the inward corner where edges 15 and 16 meet, and the right half's (88.299, 75.370) on edge 15, about 1.2 to 2.0 deep of the shelf's 3.0. The one by the inward corner is the case SUGGESTIONS.md says `backing_shelf_notch()` does not handle.
- Not now: columns 0 to 2 and column 3 west of the reset button, taken by the power switch, the PCB connector's clear zone (which a shelf there would give up for a future PCB), the nice!nano and its strips, and the reset button (`tmp/bosses/north_shelf.py`, untracked, samples the edge).

Done:

- `layout.py` runs the shelves on along the north edges from the slant, outline edges 13 to 16, on both halves, and notches them for the three heads above. `tray_shape.py` builds them with the others, `export_tray.py` measures them, and `check_layout.py` holds their face and start to DESIGN.md (Tray, Shelves under the backing), which has the figures.
- The run ends with the column 3/4 step's shelf (edge 16), which runs up to column 3's north ledge, not on edge 17 at 0.5 short of the reset button's east side wall: the face left along edge 17 would be shorter than the 2.13 round at the run's end (DESIGN.md says so).
- `backing_shelf_notch()` takes the part of the head's circle that lies in each shelf piece it reaches, so a head next to an inward corner gets a notch in each piece its circle reaches, and SUGGESTIONS.md's entry on it is gone. The head at (75.724, 76.101) reaches only edge 15's piece, so it gets one notch, which runs into the round at the column 3/4 step.
- `place.py` leaves the shelves out of the frame bosses' problem, since they are notched for each head wherever it stands. With them in, notched for `FRAME_BOSS_CENTERS_MM`, the `frame-bosses` run moved three answers onto those notches. Its answers are again what they were before the north shelves, and SUGGESTIONS.md's entry on it is gone too.

Open: the CI run's tray export, and a first print: whether the backing gives less along the north edge over columns 4 and 5 (README.md, 3D printed hand-wired frame).
