# 031 The camera arm inside the Pi case's east edge

Status: implemented (2026-10-28, 0cad1b7)

The user, 2026-10-28, on work item 030's arm, which reached 17.8 mm past the Pi case's east edge: "I don't want it "past the pi case", the pi case already extends far to the right, making the square footprint of the printer wider. This camera will make it even wider. Pull it back in so the outer wall aligns with the Pi's outer wall." Asked to measure the keyholes' slide: "I don't want to measure, do your best".

## Done

- Nothing of the arm or the camera lies east of the Pi case's east edge, which the export checks. The riser's east face is on that edge, the bar behind the camera 3.6 inside it (the camera's tilt leans the case's back plane, which the upper leg and the bar follow).
- The riser rises behind the Pi case: it leans back under the case's rearmost corner, then forward along its back (3.0 off the head's reach, 7.0 off the case), then plumb.
- The arm reaches 14 mm behind the run's back face there, so it prints resting on that bend, the run on supports, as 029 allowed.
- The keyholes' slide, measured in the mount's STL, is 11.2 mm, and the case slides 5.0 toward the arm. So the case hangs on the mount before the mount slides in, as with 8a8eb48.

## Open

- The print, now of 032's arm, which superseded 0cad1b7's before it was printed.
