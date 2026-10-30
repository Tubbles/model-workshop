# 042 Pry slots on the pushers, the socket pusher recentered with a pilot

Status: implemented (2026-10-30, 9849358)

A follow-up to work items 039 to 041. The user, 2026-10-30: "Make the socket pins center on the base plate. And for both prints, could you add a small slot along the underside where i can slide a small tool and pry it off the print bed? say 6 mm wide and 4 mm deep, and 1.5 mm high (half the base side height)". Then, on the socket pusher: "the hotswap socket pusher's pins are way too high, i just need it to nudge the socket out of the pocket, I expect it to become half as high or even shorter", "add a pilot pin for the post hole for the socket pusher" and "and then re-center the whole thing". A smaller socket pusher was made and dropped (the user chose to drop it rather than grow it to carry the pilot).

Specification:

- Socket pusher, `kbdkid5-socket-pusher.stl`: a 19.05 square base, centered on the middle of its three pins' extent in plan as modelled, about (-2.45, -2.92) from the key's center as used. Used on the frame with its top side empty (no plate, no switches), the base stopping on the frame's top face. The user: "the top side of the frame board is completely empty so there is nothing it could snag into anyway".
- Push pins: round, at `layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM`. The push is the pocket walls' depth, which leaves the socket's top level with the walls' mouth, out of the pocket. The pins are that plus the depth from the frame's top face to the contact bosses' tops, all as printed: 2.20.
- Pilot pin: in the switch's post hole at the key's center, as wide as the switch pusher's post raise (it passes the same hole at the slip fit as printed), 1.0 longer than the push pins, so it is in its hole before they reach theirs, with a 0.5 chamfer at 45 degrees round its tip to find the hole. Nothing stands under the post hole below the frame's body.
- Both pushers get a pry slot in the face on the bed, at the middle of one base edge: 6 wide along the edge, 4 deep into the base and 1.5 high, half the 3.0 base. It prints as a 6 bridge. On the switch pusher it goes in the north edge (as used), away from the pin holes, which lie south. On the socket pusher it goes in the north edge as used.
- The exports print the slot, the socket pusher's base and its pins, and check them against DESIGN.md as they do the rest. The switch pusher's raises and holes and the socket pusher's push pins do not move relative to the key.

Verify: CI's exports pass and print the new figures, and every other STL comes out as e6d086b's. The user prints both and pries them off the bed by the slot.
