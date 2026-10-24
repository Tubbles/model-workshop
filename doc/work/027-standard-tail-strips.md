# 027 The nice!nano's standard tail socket strips

Status: todo

The user, 2026-10-24, calipering their nice!nano with its socket strips soldered: the tails "From the boards bottom I calipered the tails to roughly 1.6 mm", the strips' tops over the board's top "Roughly 4.23 mm. The board is roughly 1.6 mm high", then: "Ok I see now that I've picked the wrong strips. Its not easy to swap these unfortunately". Those are Mill-Max's series 310 standard solder tail strips (doc/components.md, section 8), where the bay is built for the 315-43-112-41-003000: tops 2.413 over the board, tails 0.813 under it.

What they break in today's layout (the board z 1.2 to 2.8, the channels down to the floor's top at z 0, the backing's underside at z 6.433, 6.383 as printed):

- The tails reach 0.4 into the floor as modelled, 0.6 as printed, so the board cannot come down onto its seat, and the USB-C shell, 0.1 under the bar as printed, cannot pass under it.
- The strips' tops stand at z 7.03, 0.60 into the backing as modelled (0.65 as printed) where it covers them, by S120's and S121's pads over the B- row's pins 4, 5 and 12, where they stood 1.17 under it.
- With a PCB the tops come 0.45 under the sockets over them, where they stood 2.267 under them.

Scope: to be settled with the user from the ways to fit the strips and their figures.
