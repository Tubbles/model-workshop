# 039 Switch pusher

Status: implemented (2026-10-30)

The user, 2026-10-30: "I would like to have a small new tool I can print, a choc v1 pusher, for removing the switches from the frame board. Let's make it big as a single switch's footprint and square, and have holes for the electrical pins. It shall Then have slight raises for the side pegs, and a larger for the center post. The post pusher shall have a slight simple [dimple] in it as well for alignment. I think the pegs are too small for a dimple to print correctly." On how it is used: "Plate on, that's fine, and backing off, but the hotswap sockets populated. Only need to push it betong [beyond] the plate grip so I can lift the rest by hand".

Specification:

- A part of its own: a 19.05 square base 3.0 thick, a frame cell centered on the switch's post, with three raises on its top at the post and the pegs (`layout.CHOC_FOOTPRINT_HOLES_MM`). Pressed up under a key of the frame, backing off, sockets in, plate on.
- The push is the plate's thickness as printed: then all of the switch under its flange stands above the plate, and its clips are free whatever their shape, which is not on record.
- The raises are the push, plus the depth from the post's and pegs' ends (`SWITCH_POSTS_BELOW_PCB_MM` below the frame's body) to the bosses' ends (`boss_end_depth()`, the deepest part under the frame), plus 0.5, all as printed. At the full push the base stays 0.5 under the bosses' ends, clear of the pocket walls, the sockets and the tubes. All three are the same height: the post and pegs end level.
- For the last part of the push the raises go up into the frame's post and peg holes (3.42 and 1.90 as modelled), so each raise as printed fits its hole as printed at the slip fit (doc/print-model.md). That also keeps them out of the pocket walls, which the holes are cut through, and the bosses, which keep 0.5 from the holes.
- The post's raise has a cone dimple centered in its top, 1.5 across and 0.4 deep. The pegs' raises are flat.
- Holes through the base for the switch's two pins (`layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM`), at the frame's blade holes' 3.2.
- Printed base down, raises up.
- `model/kbdkid5/scripts/export_switch_pusher.py`, run in the `kbdkid5-frame` job into the kbdkid5 artifact as `kbdkid5-switch-pusher.stl`. It prints the figures above and fails where a raise as printed does not pass its hole as printed, or where the base at the full push comes within 0.5 of the bosses' ends.

Verify: `check_layout.py` passes. CI's export passes and prints the figures, and every other STL comes out as 184bbde's. The user prints it and pushes a switch out of the plate with it.
