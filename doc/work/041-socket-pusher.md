# 041 Socket pusher

Status: implemented (2026-10-30)

The user, 2026-10-30, after the switch pusher (work items 039, 040): "Now make a similar thing, but for pushing out the hotswap sockets".

Specification:

- A part of its own, used like the switch pusher: frame out of the tray, backing off, plate on. The key's switch is out first (by the switch pusher). Pressed down from above through the plate's cutout and the frame's two pin holes onto the socket's two contact bosses, it pushes the socket down out of its pocket. The frame is held with room under the key, and the socket hangs on its wires.
- Base: the switch pusher's, a 19.05 square 3.0 thick centered on the key's center. At the full push its face rests on the plate's top, which is the stop.
- Two pins on the base at `layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM`, the frame's pin holes, where the socket's bosses sit (2.90 across, 1.25 above the socket's top: doc/components.md, section 7).
- The push is the pocket walls' depth plus 0.5, so the socket's top ends 0.5 below the walls' mouth, all as printed. The pins' length is the plate's thickness, plus the depth from the frame's top face to the bosses' tops, plus the push, all as printed.
- The pins pass the frame's pin holes (3.2 as modelled) at the slip fit, both as printed, by doc/print-model.md and the hole strip's measurement of holes this size.
- The pin over the middle contact, 5.95 from the key's center, reaches past the plate's top layer cutout (`layout.PLATE_TOP_LAYER_CUTOUT_MM`, 14.1 square). It is flattened on that side to keep 0.2 from that edge as printed, since the plate's place over the frame is not exact. The other pin, and both against the plate's lower layer, keep at least that much.
- Printed base down, pins up.
- An export, `kbdkid5-socket-pusher.stl`, in the `kbdkid5-frame` job and the kbdkid5 artifact, with a DESIGN.md section and a README.md section like the switch pusher's. It prints the figures above and fails where a pin as printed does not pass its frame hole at the slip fit, comes within 0.2 of the plate's cutout as printed, or leaves the socket's top above the walls' mouth plus 0.5 at the full push.

Verify: `check_layout.py` passes. CI's export passes and prints the figures, the switch pusher's STL comes out as 477bae7's, and every other STL as before. The user prints it and pushes a socket out with it.
