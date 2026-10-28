# 030 The camera arm as one bent bar, the camera at the Pi case's east end

Status: implemented

The user, 2026-10-28, after printing 029's arm (8a8eb48): "I printed the arm now, I realized after the fact that its a big block in the middle, like a backing for the pi, why? I want a consistent arm cross area and size (except where it tapers down to the extrusion foot) that snakes as needed. The foot and rail works, but its unnecessarily large, make it extend to the outer bound of the arm projected down, no more. And lower the height of the camera mount by half of the difference between the camera house's lowest point and the screen's highest point. Render the final product in the report with measurements of the things I've mentioned just now so we can review it together". Then: "Also move the camera mount away from the bed, closer to the outer eastward edge of the pi when viewed from above", and asked how far: "East end but I don't want it flush, since it still needs to be angled toward the print bed center. Actually let's angle it slightly in front of the center, ie. A little bit south of the center when viewed from above. Say 5 cm".

## Done

- The arm is one bar of the camera bar's 14 x 15 mm section, carried along a path through three rounded bends: a run along the rail's top face, a riser just east of the Pi case, an upper leg in the camera case's back plane and the bar behind the case (0422d3d, the review's fixes in 45bbac5). The run's west end is the foot, so nothing tapers and nothing of the foot reaches past the arm seen from above: 14 along the rail, 34.9 across.
- The camera comes down by half of 8a8eb48's gap from its case's lowest point (105.0 above the rail) to the Pi case's top edge (61.0), 22.0. It tilts less now, so its case ends up 20.9 over the screen.
- The camera's case has its east corner on the Pi case's east edge and aims 50 mm in front of the bed's center at mid travel. More of the bed is in view: 71 % on average over the Y travel, 65 % with the gantry and the upright in the way, against 58 % and 46 %.
- The run lies against the Pi mount, so the spacer rails grow to 88.5. The Pi case now goes on and comes off its keyholes with the arm in place.
- The review page (claude.ai artifact 7m3q4LQ8Grw6GJURG1GjPU) shows CI's STLs on the printer with the Pi mount and case, dimensioned.

## Open

- The print: whether the run sits flat on the rail, the riser's gap to the Pi case (2.1) and the arm's to the print head, whether the camera wobbles when the bed moves, and a snapshot to judge the aim.
- The arm reaches 17.8 mm past the Pi case's east edge, since its riser and the bar stand east of the camera's case. Whether that is acceptable is the user's call.
- 029's open measurements still stand: the bed's height, the nozzle's line and the bed's right edge from the Ender-3's CAD, the head reach's reference face, the ribbon's way into the Pi case.
