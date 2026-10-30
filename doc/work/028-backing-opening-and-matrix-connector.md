# 028 The backing's opening for the matrix's leads, and an inline connector

Status: todo

The user, 2026-10-24, on the hand-wired frame's leads to the nice!nano: "there needs to be some wire slack that'll get stuffed into the tray when closing it up" and "let's look at where the backing hole could go, it doesn't need to be close to the bay necessarily". On the first pick, S110 north of column 1: "Hmm I am not sure that's the best pick, remember I want a bundled up wire nest so there is slack enough that I can remove the whole matrix assembly to access the tray pocket, so I can work in it, do repairs, rewire, etc.". On the next, S122 south of the bay: "That's still very huddled up close to the nano, and just next to the battery. I think S102 is a better fit". Then: "I'm thinking I might want a cable connector between the nano wire bundle and matrix wire bundle, is there something neat that could fit? Then the wire nest doesn't need to be so big, just big enough to get in with the hands and disconnect the connector to separate the matrix assembly from the tray", and on the kit below: "Yes I'll order this kit and use one 13 cm cable for each side of the connector, and skip the ethernet cabling. That'll be 22 cables per half, or 44 in total, and 2x each of 6p and 5p male and female housings. That'll be 26 cm in total between the matrix and nano, I think that'll be enough".

## Decided

- The opening goes in the backing under S102 on the left half and S262 on the right. The floor under the backing is one free region over each half (6,687 mm2 on the left half and 6,668 on the right, 6.38 clear, 4.88 under the backing's screw heads), so the leads' slack lies on it between the opening and the bay. The largest rectangle there that keeps the backing's rules (1.0 from the pads, clear of the screw heads, the bosses' ends and the walls' outer faces) over free floor, in the left half's frame: 9.7 x 12.2 at x 8.9 to 18.6, y 25.6 to 37.8 on the left half, 5.6 x 12.2 at x 3.6 to 9.2, y 25.6 to 37.8 on the right (`tmp/slack_hole/probe.py`, untracked, with its output in `left.txt` and `right.txt`).
- The connector: elechawk's PicoBlade compatible 1.25 mm kit (model 125BOXMF, Amazon.se B08RMQP6YP, 209 kr on 2026-10-24), male and female housings of 2 to 6 positions and 180 pre-crimped 13 cm silicone wires, each with a male terminal at one end and a female one at the other (the listing's photos). Per half a 6P and a 5P pair carry the 11 signals, with one 13 cm wire per signal on each side and no Ethernet cores: 44 wires in all and two each of the 6P and 5P male and female housings. The two sizes cannot be swapped, and each housing mates one way. Molex's own PicoBlade housings have a friction lock and are polarized to their mating part (the 51021 and 51047 product sheets, `tmp/connector/picoblade-51021-drawings/`). The kit is a clone, so its lock is unverified, and the listing gives neither the wire's gauge nor the housings' size.
- The nano side's wires end in clipped 1N4148 leads (0.5 at most) as the pins in the strips, held by hot glue (doc/log/2026-10-24.md).
- Power, ground and reset stay in the tray and plug into the strips like the matrix: the battery's negative on a GND pin, its positive through the power switch on RAW, the reset button on RST and GND. B+ and B- stay empty. The user: "I mean b- and b+ is not populated by the strip". nicekeyboards: "RAW and GND are the respective equivalents to B+ and B-" (doc/components.md, section 1). None of these wires pass the opening.

## The nice!nano's pins

kbdkid4's, since "the matrix wiring will be the same as in kbdkid3/4" (the user), traced in kbdkid4's `circuit/circuit.lp` through its reversible board's jumpers: its U1 and U2 carry each signal on the same pin. The nice!nano lies the same side up on both halves, its B+ row (RAW, GND, RST, VCC) east and its B- row west as built. Pins are counted from the USB end. C0 is the outer column, C6 the thumb (S163, S203 on the right half), R0 the top row.

| Strip | Pin | Signal |
|---|---|---|
| East (B+ row) | 1 | RAW, the battery's positive through the power switch |
| | 2 | GND |
| | 3 | RST, the reset button |
| | 4 | VCC, free |
| | 5 | C6, P0.31 |
| | 6 | C5, P0.29 |
| | 7 | C4, P0.02 |
| | 8 | C1, P1.15 |
| | 9 | C3, P1.13 |
| | 10 | C2, P1.11 |
| | 11 | C0, P0.10 |
| | 12 | R3, P0.09 |
| West (B- row) | 3 and 4 | GND |
| | 10 | R0, P0.11 |
| | 11 | R1, P1.04 |
| | 12 | R2, P1.06 |

The west strip's other pins are free. kbdkid4 also wires a display's CS, MOSI and SCK to west pins 1, 5 and 6, and kbdkid5 has none. West pins 4, 5 and 12 lie under the backing by S120's and S121's pads (S240's and S241's on the right half), and pin 11 at its cutout's end (DESIGN.md, Wires to the nice!nano), so R1, R2 and a GND on west pin 4 take a lead bent flat over the strip, 1.17 under the backing.

## Routes in the tray

From the probe, in the left half's frame, where the right half's west strip is its B+ row:

- Under the backing from the opening to the strips' pin 12: on the left half 26 to the B- strip's and 42 to the B+ strip's, on the right 35 to the B+ strip's and 51 to the B- strip's.
- Into the bay: over the clamp's block south of the board, two lanes 8.6 wide with 1.58 clear. Beside the west strip, the wall's low stretches at y 43.3 to 49.7 and 59.1 to 65.3, and no wall north of y 65.3 for 9.6, to y 74.9. Beside the east strip, low stretches at y 47.0 to 54.5 and 66.05 to 73.55. The low stretches keep 1.18 clear, one layer of wire. The north block and the raised wall pieces are closed.
- The 0.5 lead crosses the strip and the low wall, and its joint to the silicone wire lies beyond them, since 1.17 and 1.18 are clear there.
- On the left half the reset button lies east of the bay, beside RST and GND, and the power switch west in column 0, so its wire crosses the board's USB end to RAW. On the right half the switch lies east by RAW and the reset button west of the bay, on the mirror line, so its RST wire crosses the board to the east strip. Its GND can be west pin 3.

## The matrix side's lengths

From each column's nearest key center to the opening, in plan (Derived): on the left half C0 0, C1 9, C2 29, C3 48, C4 67, C5 86 and C6 106, on the right C0 0, C1 19, C2 38, C3 57, C4 76, C5 95 and C6 115. The row wires cross the whole half and pass the opening. A 13 cm wire with its far terminal cut off and its end stripped leaves about 12.4, and a lead also comes down from the frame's underside through the backing to the connector on the floor, so C6's lead on both halves and C5's on the right have little or none to spare. Run west under the frame, their enamelled wire would bring them nearer the opening.

## Scope

- The backing gets the opening on both halves, and `check_layout.py` holds it to the backing's rules and to free floor under it.
- DESIGN.md (Hand-wired frame, Wires to the nice!nano) and kbdkid5's README (putting a half together) follow.

## Open

- Calipering the kit when it comes: a 6P pair mated and lying flat, against the 6.38 clear (4.88 under the screw heads), and the wire's outer diameter.
- C5's and C6's leads on the matrix side (above).
- Whether the wire rooms over B+ and B- go, now that the pads stay empty.
