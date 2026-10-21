# 017 The slanted edge down to the south edge

Status: implemented

The user, 2026-10-21: "Also just below the thumb key, to the side, the slanted edge where the joint lives is not drawn all the way to the south end of the keyboard. Do you think we can do that change?" Then "The tray is missing the extra triangle next to the thumb key", "Sorry I meant the plate", "Ah yeah sorry, I want it, thanks for prioritizing it up", and "Do the plate first so I finally can get another print up".

Done:

- The plate first: its slanted edge runs on from the thumb's top right corner to the plate's south edge (19eaff7). The fused mock from 19eaff7 has the triangle with nothing under it and is not for printing.
- The outline, the tray, the mocks and the frame: the slant runs on to the south edge at x 138.265 (433cbf9). The dowel pins and the magnets keep their places along the slant, now measured from its new south end. The pin parking hole keeps its axis and enters the joint face aslant, since a hole square to the face could not keep 0.5 from S163's socket and 1.0 of plastic to the lower dowel hole. The right half's S163 tab notch goes. The mirror line follows the outline's middle to x 69.133, so the right half's STL coordinates shift, though nothing moves on the keyboard.
- The joined trays' check computes the slant's end and the mirror line from the exact corners, as the trays do (73b127f, after CI run 39645482478 failed on the rounded figures).
- DESIGN.md (Outline, The joint, Plate and mocks) has the figures.

Still open: print the plate, and the trays to go with it. A plate from 19eaff7 on fits only the trays from 433cbf9 on.
