# 027 The nice!nano's standard tail socket strips

Status: todo

The user, 2026-10-24, calipering their nice!nano with its socket strips soldered: the tails "From the boards bottom I calipered the tails to roughly 1.6 mm", the strips' tops over the board's top "Roughly 4.23 mm. The board is roughly 1.6 mm high", then: "Ok I see now that I've picked the wrong strips. Its not easy to swap these unfortunately". Those are Mill-Max's series 310 standard solder tail strips (doc/components.md, section 8), where the bay is built for the 315-43-112-41-003000: tops 2.413 over the board, tails 0.813 under it.

What they break in today's layout (the board z 1.2 to 2.8, the channels down to the floor's top at z 0, the backing's underside at z 6.433, 6.383 as printed):

- The tails reach 0.4 into the floor as modelled, 0.6 as printed, so the board cannot come down onto its seat, and the USB-C shell, 0.1 under the bar as printed, cannot pass under it.
- The strips' tops stand at z 7.03, 0.60 into the backing as modelled (0.65 as printed) where it covers them, by S120's and S121's pads over the B- row's pins 4, 5 and 12, where they stood 1.17 under it.
- With a PCB the tops come 0.45 under the sockets over them, where they stood 2.267 under them.

Ways to fit them, offered 2026-10-24 (probes in `tmp/strips310/`, untracked). All three take the tails clipped to at most 0.94 below the board after soldering, which today's channels take with the 0.057 as printed, and `NANO_STRIP_POCKET_NORTH_EXTENSION_MM` from 0.17 to 0.26, since tilted in at 2.76 degrees the taller strip's north top corner keeps only 0.014 from the step's ledge against the 0.1 minimum:

1. The backing cut out over each strip's whole length. The tray's heights and floor stay. One pad each of S120's and S121's is trimmed: on the left half they keep 3.85 of 9.16 mm2, on the right they lose 29%. A 24 AWG wire bent over a strip keeps 0.16 under the sockets.
2. The board lowered about 1.2, onto the floor's top. Every pad stays whole, but the tails are clipped to about 0.5 into channels in the floor (0.5 of floor left), the pry recess goes into the floor, the USB window notches the floor's north edge, and a wire bent over a strip under the backing fits only as 26 AWG (0.14).
3. Everything over the floor raised 1.157. Pads and bay stay whole, the tray grows from 14.6 to 15.757 tall.

Parked: the user, the same day, "I think I found a way to desolder the strips, but let's put a pin in that". With the 315-43-112-41-003000 strips the layout fits as it is.
