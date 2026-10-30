# 019 The triangle east of the thumb out again

Status: implemented

The user, 2026-10-22: "Also I don't like the shape of the tray after we added the triangle east of the thumb key, could we remove that again?"

Scope: undo work item 017's outline. The slant ends at the thumb's top right corner again and the thumb cell's east edge runs down to the south edge, as before 433cbf9. Everything that follows the outline follows it back: the tray, the plate (its triangle from 19eaff7 goes too, since the plate must stay inside the tray), the mocks, the hand-wired frame and its backing. The dowel pins and the magnets keep their places on the keyboard, measured along the slant from the thumb's corner again. The pin parking hole goes back to running square through the thumb's short east wall, and the right half's S203 tab notch comes back if its tab needs it. The mirror line follows the outline's middle.

Done:

- The outline, the tray, the plate, the mocks and the frame are back on the outline from before 433cbf9, done by hand on today's code, the plate keeping what it gained since 19eaff7. DESIGN.md (Outline, The joint, Plate and mocks, Hand-wired frame) has the figures.
- The dowel pins and the magnets are back at their places from before 017, 0.00015 further south along the slant than 017 had them: 017 added the rounded 19.251 to their alongs, while its south end lay 19.25085 from the thumb's corner.
- The pin parking hole runs square through the thumb's east wall again, and the right half's S203 tab takes its notch and pocket again by the tab rule. The mirror line is back at x 66.199, so the right half's STL coordinates shift back.
- The parking boss, back where it was, takes the left half's frame boss at (113.749, 13.477), which work item 016's solver had found while the parking boss stood further east (DESIGN.md, Hand-wired frame, Bosses).
- CI built the tray, the plate, the mocks and the frame (run 39748728369).

Still open: printing them.
