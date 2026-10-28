# 033 The camera arm's bends with a radius

Status: implemented (2026-10-28, e032dd8)

The user, 2026-10-28, on work item 032's arm: "the first elbow is wonky, it doesn't join correctly and create sharp edges. Its the first elbow closest to the foot, it feels like there are two distinct pieces meeting up haphazardly". Asked whether there is a tool or technique for sweeping a rectangle along a path without such edges, and told a path with a bend radius: "Yes do it like that, with a minimum path bend radius".

## Done

- Every bend of the arm is an arc of 8.5 mm on the center line, half the 15 mm side plus a 1 mm inside radius, the rectangle swept along it.
- The run's corner keeps its two bends, up and then back, so the riser keeps its 15 mm side along x. Their arcs meet end to end, which starts the leg 19.6 mm up and leans it 45.7 degrees from plumb. The waist, the riser, the bar and the camera stay where they were.

## Open

- The print (camera-arm-e032dd8): the elbow by the foot one smooth curve, then 032's checks.
- The loft by the camera case keeps a zero radius kink at each end, 17.4 and 14.2 degrees (SUGGESTIONS.md).
