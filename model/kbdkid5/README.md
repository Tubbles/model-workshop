# kbdkid5

A wireless split keyboard whose halves also join into one board, the successor of [kbdkid4](https://github.com/Tubbles/kbdkid4). Its design, with every dimension, is in [DESIGN.md](DESIGN.md), and the parts to buy are below. The part choices and their sources are in [doc/components.md](../../doc/components.md), and the plan is in [PLAN.md](../../PLAN.md).

CI runs each export below with the command shown, from this repository's root. A right half part (the word `right`) is the left one mirrored, but for what DESIGN.md (Frame and units) lists. CI also runs the layout check, `python3 model/kbdkid5/scripts/check_layout.py`, which checks the layout and DESIGN.md's figures against it. It is plain Python that runs anywhere. In CI it is a job of its own beside the exports, so a failing check fails the run while the STLs still upload.

## 3D printed PCB mock

`model/kbdkid5/scripts/export_pcb.py` exports a printable stand-in for the PCB until the real one is designed, to test-fit the printed tray and plate: the outline with every key's hotswap footprint holes and the mounting drills, and no sockets (DESIGN.md, Plate and mocks). To mount switches, print the fused mock below. `pull_in` (default 0.2 mm) moves the outline in and every hole out by that much, for the print's swelling (doc/print-model.md).

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_pcb.py --pass pcb.stl [right] [pull_in=0.2]

CI uploads both halves as the `kbdkid5-pcb-<short commit hash>` artifact: `kbdkid5_Pcb_Left.stl` and `kbdkid5_Pcb_Right.stl`.

## 3D printed switch plate

`model/kbdkid5/scripts/export_plate.py` exports the switch plate: kbdkid3's plate cells on the layout's keys, the switch-free corner by the slant covered, holes over the screw heads at the mounting drills, and kbdkid4's print corrections, `pattern_shift` along x with the outline held and `side_shave` off the west, east and slanted edges. The word `covered` makes the plate for a half without the hard-to-reach key S123: its cutout is filled in and a pit in the underside clears its diode. DESIGN.md (Plate and mocks) has the figures. The plate is written upside down, its top face on the bed.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_plate.py --pass plate.stl [right] [covered] \
        [pattern_shift=0.25] [side_shave=0.1] [hole_diameter=4.17]

CI uploads both halves, plain and covered, as the `kbdkid5-plate-<short commit hash>` artifact: `kbdkid5_Plate_Left.stl`, `kbdkid5_Plate_Right.stl`, `kbdkid5_Plate_Left_Covered.stl` and `kbdkid5_Plate_Right_Covered.stl`.

## 3D printed fused mock

`model/kbdkid5/scripts/export_mock.py` exports the PCB mock and the switch plate fused into one part, to mount switches in and get a feel of the layout. Each key's two pin holes become narrow slits in the PCB layer that grip the switch's flat pin blades, `slit_width` across the blade and `slit_length` along it (DESIGN.md, Plate and mocks, has their defaults). `pull_in` sets those defaults but does not grow a given `slit_width` or `slit_length`. The part is written PCB side down. Check in the slicer preview that every slit is still open in the first layers, since elephant foot and XY or hole compensation change slits this small. A mounted switch's pins, center post and pegs reach below the part, so raise it off the table.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_mock.py --pass mock.stl [right] \
        [pull_in=0.2] [slit_width=0.6] [slit_length=1.6]

`model/kbdkid5/scripts/export_slit_test.py` exports a strip of six single-key cells of the PCB layer alone, with no plate, to find the slits that grip the switch's pins: each pin gets its own slit, its blade's thickness plus a clearance that steps from cell to cell. `wide` exports the wide strip instead, the first slit strip's widths again without its plate, the same on both pins of a cell. DESIGN.md (Plate and mocks) has both strips' figures and their marks. Lower PrusaSlicer's "Slice gap closing radius" for the plain strip, whose narrowest slit it fills at its default (DESIGN.md, Slit test strip), and check every slit in the slicer preview. Elephant foot on the bed face matters too, as for the fused mock.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_slit_test.py --pass strip.stl [wide] [pull_in=0.2]

CI uploads both halves of the fused mock and the slit strips as the `kbdkid5-mock-<short commit hash>` artifact: `kbdkid5_Mock_Left.stl`, `kbdkid5_Mock_Right.stl`, `kbdkid5_Slit_Test.stl` and `kbdkid5_Slit_Test_Wide.stl`.

## 3D printed socket test strips

`model/kbdkid5/scripts/export_socket_test.py` exports three stackable test strips for a keyboard without a PCB: a printed frame as thick as the PCB takes its place, each hotswap socket held in a pocket on the frame's underside, and the switches wired by hand. `pocket` steps the pocket's fit across its six cells, its pin holes loose enough that only the pocket holds the socket. `holes` has loose pockets and steps the two pin holes, so only the holes hold the socket. `backing` screws under either frame strip with M2 screws into heat-set inserts in the frame's bosses, its pads pressing each socket by a different amount in each cell. Solder a wire to each socket tab before pressing the socket in: the tab and its wire slide up a slot in the pocket wall. The frame strips print upside down, the backing bottom down. `insert_length` sets the bores for inserts shorter than the longest the bosses hold.

`switch` exports the switch hole strip instead, to find the holes for the switch's center post and side pegs that keep it from wobbling sideways, since the socket strips' holes are too wide for that. It is the frame's body alone, its six cells stepping the post's and pegs' holes together, the blades' holes wide enough that only the post and the pegs hold the switch. It prints top face down.

DESIGN.md (Hand-wired frame test) has the strips' figures, the marks that tell them and their earlier prints apart, and what each print settled.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_socket_test.py --pass strip.stl pocket|backing|holes|switch \
        [pull_in=0.2] [insert_length=<mm>]

To try the pocket strip, push a socket into each pocket by hand from the open (wall) side. A good pocket takes it with a light push, lets it sit flat against the ceiling, keeps it in when the strip is turned over and tapped, and does not let it shift when nudged sideways. Loose means it falls out or rattles, too tight means it needs a tool or will not sit flat. The pocket alone does not have to survive a switch being pressed in: the backing does that. Report the cell number (its south notches) of the best one, or "all loose" or "all tight".

To try the hole strip, push a socket in so its two posts enter the holes. The pocket is loose on purpose and will not hold anything. The best cell is the tightest whose posts still go fully in by hand and sit flat, and whose socket stays in when the strip is turned over and tapped. Report the best cell, or "all loose" or "all tight".

To try the switch hole strip, push a switch into each cell from the face that was on the bed and wiggle it sideways. A good cell takes the switch fully in by hand, lets it sit flat and holds it without play sideways. Loose means it wobbles, too tight means it will not go fully in or sit flat. Report the tightest cell the switch goes fully into by hand and sits flat in, which cells still let it wobble, and whether the post or the pegs seem to bind first.

CI uploads the socket strips and the switch hole strip from a job of their own as the `kbdkid5-socket-<short commit hash>` artifact: `kbdkid5_Socket_Test_Pocket.stl`, `kbdkid5_Socket_Test_Holes.stl`, `kbdkid5_Socket_Test_Backing.stl` and `kbdkid5_Switch_Hole_Test.stl`, ready a few minutes after a push.

## 3D printed tray

`model/kbdkid5/scripts/export_tray.py` exports a half's tray: walls, floor and the ledge the PCB rests on, standoffs bored for M2 heat-set inserts at the mounting drills, the cuts that clear the switches' hotswap sockets, the joint along the slanted edge, and the mounts for the parts that are not on the PCB (DESIGN.md: Tray, Parts in the tray, The joint). The tray is written floor on the bed.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_tray.py --pass tray.stl [right] [pin_hole_diameter=<mm>] \
        [nano_length=33.2] [nano_width=18.2] [nano_pocket_fit=0.1] [clamp_press=0.1] \
        [bar_clearance=0.1] [battery_shoulder=0]

For a test print, `pin_hole_diameter` overrides the half's pin hole fit as modelled, and the others the figures the mounts rest on: the nice!nano's board length and width (the defaults are the user's caliper, so these suit another board), how much wider than the board its pocket prints, how hard the clamp's tab presses the board (how far below the tab's seat on the board its block's top stands), the bar's clearance over the USB-C shell, and lips reaching that far onto the battery header's front rim (none by default, DESIGN.md says why).

Glue a magnet into each of the joint's slots, against the thin skin at the joint face, with alternating poles along the joint, the right half opposite to the left, so the halves pull together and center themselves. To join the halves, press the dowel pins into the left half's holes, then push the right half on. Glue an S-04-02-N magnet to the bottom of the parking hole in each half's thumb key east wall, where it holds a pin while the halves are used apart. Glue the battery header into its pocket and the reset button to the floor.

To fit the nice!nano, solder its socket strips on first, press the M2 x 3 heat-set insert into the block south of it, lay the board in nose first, its USB-C shell under the bar at the USB window, put the clamp's tab (below) on with its nose over the board's south edge and screw it down with an M2 x 4. To take it out, with the PCB out, undo the screw and lift the tab off, bring a toothpick down the pry slot from over the south rim, through the slot's east part, the 2.8 mm beside the face nearest the screw, so it passes the last solder tail of the board's west row, its point down the recess and under the board's south edge, and lift.

`model/kbdkid5/scripts/export_clamp_tab.py` exports the nice!nano clamp's tab, the same for both halves and the test bay below, printed top face down, the nose standing up, with nothing to support.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_clamp_tab.py --pass tab.stl

`model/kbdkid5/scripts/export_nano_bay_test.py` exports one nice!nano bay cut out of the left tray at the tray's defaults, to settle the bay on a real board before printing whole trays (DESIGN.md, the nice!nano's bullets). `nano_length` and `nano_width` fit the bay to a calipered board.

To try it, fit the board as in the tray, with an M2 x 4, or on the test bay an M2 x 6 with an M2 nut under its head (the trays take only the M2 x 4). Push a USB-C cable in and pull it out: the board should not move or ride up. Wiggle the board across and along: loose means it rattles, too tight means it would not drop in flat on the seat. Then take the tab off and lift the board out with a toothpick as in the tray. Note whether the board went in and sat flat, whether it is loose, snug or tight across and along, whether the strips and their tails touched anything, whether it held under the cable, and whether the toothpick got it out.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_nano_bay_test.py --pass bay.stl \
        [nano_length=33.2] [nano_width=18.2]

CI uploads both halves, the tab and the test bay as the `kbdkid5-tray-<short commit hash>` artifact: `kbdkid5_Tray_Left.stl`, `kbdkid5_Tray_Right.stl`, `kbdkid5_Nano_Clamp_Tab.stl` and `kbdkid5_Nano_Bay_Test.stl`.

## Parts to buy

For both halves:

- The power switches, reset buttons, battery headers and, for the hand-wired frame, the key diodes: [doc/components.md](../../doc/components.md), section 13, lists them with their quantities, Electrokit article numbers and prices.
- PHR-2 housings and SPH-002T-P0.5S contacts if a battery lead needs re-terminating.
- 8 supermagnete S-08-03-N disc magnets for the joint, 2 S-04-02-N for the pin parking.
- 2 hardened ISO 8734 (or DIN 6325 m6) 4 x 16 dowel pins in plain steel, not stainless (DESIGN.md, Pin parking, says why).
- M2 heat-set inserts and screws as on kbdkid4, and per half an M2 x 3 heat-set insert and an M2 x 4 screw for the nice!nano's clamp.
- 4 Mill-Max 315-43-112-41-003000 socket strips (12 pins), two per nice!nano, and solid 24 or 26 AWG wire to plug into them.
