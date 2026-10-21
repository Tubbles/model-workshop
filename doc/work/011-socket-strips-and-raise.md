# 011 Socket strips on the nice!nano and a 1.5 raise

Status: implemented

The user printed work item 010's test bay (507370b): "Ok the test bay works well, the idea flies. However I can rock the nano a full millimeter sideways, and maybe 1/3 of a millimeter lengthwise, can you shrink the bay margins accordingly? Also I've realized I want to solder 2 x 12 pin low profile socket strips on top of the nano so I don't have to solder wires directly to it. I've ordered "Mill Max 315-43-112-41-003000" for the purpose. Could you raise up the whole bay the nano rests in and pocket the two 12 pin strips on the sides? The nano has 13 pins on each side but the one closest to the USB connector will not get soldered, so only the 12 southmost pins will get the socket strips." Then the caliper: "The bay inside width is 18.41~18.46. The nano width is 18.17~18.23 mm. So a full millimeter might be too much", "Board length 33.20, bay inside length 33.54".

The strips meet the hand-wired frame's backing under S100 and S101, and the user chose to raise everything over the floor: "Option 1. Raise the frame assembly and the rim and the rim ledge accordingly. The whole thing becomes 1.5 mm taller, to accommodate the need for 1.5 mm higher ceiling in the tray cave. I don't want holes in the tray floor, that would make the rubber sole mandatory which I don't want." The wires go into the strips as solid wire ("Yeah solid wire it is"), and the backing's screws are the user's pan heads: "The M2 pan head screws I have today have roughly 1.5 mm high heads btw". doc/log/2026-10-20.md has the whole exchange.

Implemented:

- The board is 18.20 x 33.20, calipered. The pocket stays the slip fit both ways for 0.1 of play as printed, along it with the end faces' measured swelling (0.13 per face, only their 0.26 together calipered).
- The board rests on a 1.2 seat with channels for the strips' tails down to the floor's top along both rows. The north block gets a sill under the shell's opening at the seat's height, the shell's channel and the USB window rise with the shell, and the pry recess is the seat left out under the slot, so the floor stays whole and 1.2 thick everywhere.
- The west ledge's face and the east wall's inner face are pocketed over the board's top for each strip's worst case. `check_layout.py` models each strip as Fig. 4 draws it (the insulator on its sleeves) and its tails, and checks them against the tray as printed with the board anywhere between its stops, the sockets over them, the going-in pose and the nice!nano's own wire rooms, whose overlaps with the strips are printed figures.
- The PCB plane is 1.5 higher (9.5), the rim 13.4, the tray 14.6 tall. The clamp keeps its 2.1 nose and rises with the board, so the tab printed from 507370b still fits. The dowel pins follow their midway rule to z 4.15.
- `socket_test_shape.py` counts the backing's 1.5 pan heads: 0.773 over the battery in the tray.
- The second review: the figures that depend on how the end faces' 0.26 splits are also taken at the worst split, all of it on either face. There the west strip's corner going in reached 0.069 into the ledge, so both strip pockets run 0.17 further north (to y 73.6595), which keeps it 0.101 clear.
- The P1.01/P1.02/P1.07 pads stay unwired: "P1 pads are unused for now, let's ignore them for now" (the user, 2026-10-21). Their wire room reaches 0.44 into a strip's worst case, the B+ and B- rooms 0.1235.

DESIGN.md (Heights, the nice!nano's bullets, the joint, In the tray) has the figures.

Open:

- Print the bay with the strips soldered: whether the board drops in on the seat, the tails clear the channels, the strips clear their pockets, the board holds still while a USB-C cable goes in and out (work item 010 left that open), and the toothpick lifts it out, coming in through the slot's east part (x 3.6 to 6.4) past the last tail.
- The shell's overhang past the board: the render's 0.87, kept, against 0.97 from the user's two calipers (34.17 with the shell, 33.20 without). At 0.97 the mouth lies 0.4 behind the wall's outer face and the shell's channel ends 0.1 short of the mouth at the board's north stop.
- How the end faces' 0.26 of swelling splits between the foot and the north block. With all of it on the foot, the shell passes its channel's end by 0.13 and its box comes 0.018 into the window's corner rounds as printed. The other figures hold at either end of the split (DESIGN.md).
