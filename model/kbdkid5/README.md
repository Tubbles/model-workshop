# kbdkid5

A wireless split keyboard whose halves also join into one board, the successor of [kbdkid4](https://github.com/Tubbles/kbdkid4). Its design, with every dimension, is in [DESIGN.md](DESIGN.md), and the parts to buy are below. The part choices and their sources are in [doc/components.md](../../doc/components.md), and the plan is in [PLAN.md](../../PLAN.md).

CI runs each export below with the command shown, from this repository's root, and puts the parts' STLs in the `kbdkid5-<short commit hash>` artifact and the test prints' and mocks' in `kbdkid5-test-<short commit hash>` (the root [README.md](../../README.md), Getting the STLs). A right half part (the word `right`) is the left one mirrored, but for what DESIGN.md (Frame and units) lists. CI also runs the layout check, `python3 model/kbdkid5/scripts/check_layout.py`, which checks the layout and DESIGN.md's figures against it. It is plain Python that runs anywhere. In CI it is a job of its own beside the exports, so a failing check fails the run while the STLs still upload.

## 3D printed PCB mock

`model/kbdkid5/scripts/export_pcb.py` exports a printable stand-in for the PCB until the real one is designed, to test-fit the printed tray and plate: the outline with every key's hotswap footprint holes and the mounting drills, and no sockets (DESIGN.md, Plate and mocks). To mount switches, print the fused mock below. `pull_in` (default 0.2 mm) moves the outline in and every hole out by that much, for the print's swelling (doc/print-model.md).

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_pcb.py --pass pcb.stl [right] [pull_in=0.2]

CI exports both halves as `kbdkid5-pcb-mock-left.stl` and `kbdkid5-pcb-mock-right.stl`, in `kbdkid5-test-<short commit hash>`.

## 3D printed switch plate

`model/kbdkid5/scripts/export_plate.py` exports the switch plate: kbdkid3's plate cells on the layout's keys, the switch-free corner by the slant covered, holes over the screw heads at the mounting drills, and kbdkid4's `side_shave` off the west, east and slanted edges. `pattern_shift` moves the hole pattern along x with the outline held, 0 by default. The word `covered` makes the plate for a half without the hard-to-reach key S123: its cutout is filled in and a pit in the underside clears its diode. DESIGN.md (Plate and mocks) has the figures. The plate is written upside down, its top face on the bed.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_plate.py --pass plate.stl [right] [covered] \
        [pattern_shift=0] [side_shave=0.1] [hole_diameter=4.17]

CI exports both halves, plain and covered, as `kbdkid5-plate-left.stl`, `kbdkid5-plate-right.stl`, `kbdkid5-plate-covered-left.stl` and `kbdkid5-plate-covered-right.stl`, in `kbdkid5-<short commit hash>`.

## 3D printed fused mock

`model/kbdkid5/scripts/export_mock.py` exports the PCB mock and the switch plate fused into one part, to mount switches in and get a feel of the layout. Each key's two pin holes become narrow slits in the PCB layer that grip the switch's flat pin blades, `slit_width` across the blade and `slit_length` along it (DESIGN.md, Plate and mocks, has their defaults). `pull_in` sets those defaults but does not grow a given `slit_width` or `slit_length`. The part is written PCB side down. Check in the slicer preview that every slit is still open in the first layers, since elephant foot and XY or hole compensation change slits this small. A mounted switch's pins, center post and pegs reach below the part, so raise it off the table.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_mock.py --pass mock.stl [right] \
        [pull_in=0.2] [slit_width=0.6] [slit_length=1.6]

`model/kbdkid5/scripts/export_slit_test.py` exports a strip of six single-key cells of the PCB layer alone, with no plate, to find the slits that grip the switch's pins: each pin gets its own slit, its blade's thickness plus a clearance that steps from cell to cell. `wide` exports the wide strip instead, the first slit strip's widths again without its plate, the same on both pins of a cell. DESIGN.md (Plate and mocks) has both strips' figures and their marks. Lower PrusaSlicer's "Slice gap closing radius" for the plain strip, whose narrowest slit it fills at its default (DESIGN.md, Slit test strip), and check every slit in the slicer preview. Elephant foot on the bed face matters too, as for the fused mock.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_slit_test.py --pass strip.stl [wide] [pull_in=0.2]

CI exports both halves of the fused mock and the slit strips as `kbdkid5-fused-mock-left.stl`, `kbdkid5-fused-mock-right.stl`, `kbdkid5-slit-test.stl` and `kbdkid5-slit-test-wide.stl`, in `kbdkid5-test-<short commit hash>`.

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

CI exports the socket strips and the switch hole strip as `kbdkid5-socket-test-pocket.stl`, `kbdkid5-socket-test-holes.stl`, `kbdkid5-socket-test-backing.stl` and `kbdkid5-switch-hole-test.stl`, in `kbdkid5-test-<short commit hash>`.

## 3D printed hand-wired frame

`model/kbdkid5/scripts/export_frame.py` exports a half's hand-wired frame or its backing. The frame takes the PCB's place in the tray: the switches sit in it, each hotswap socket in a pocket on its underside, and its bosses take M2 heat-set inserts. The backing screws up under the sockets with a pad under each, so a socket stays put while a switch is pressed into it. This first iteration has no diode cradles and no wire grooves: the wires run in the room between the frame and the backing. DESIGN.md (Hand-wired frame) has the design.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_frame.py --pass part.stl frame|backing [right] \
        [insert_length=<mm>]

CI exports both halves of both parts as `kbdkid5-frame-left.stl`, `kbdkid5-frame-right.stl`, `kbdkid5-frame-backing-left.stl` and `kbdkid5-frame-backing-right.stl`, in `kbdkid5-<short commit hash>`.

Print the frame as written, its top face on the bed, the walls and bosses standing up, and the backing as written, bottom down with its pads on top. Neither needs supports.

To put a half together, press an M2 x 3 heat-set insert into every boss. Solder a wire to each socket tab, then push each socket into its pocket from the open side, the tab and its wire sliding up the slot in the wall. Screw the backing on with M2 x 4 screws, its pads under the sockets. Lay the frame in the tray on the ledge and the standoffs and screw it down at the six drills, the plate on top, as with the PCB. The wires reach the nice!nano's socket strips through the backing's cutouts over them.

What to check and report:

- Each socket in its pocket before the backing goes on: good is a light push, flat against the frame, and it stays in when the frame is turned over and tapped. Loose means it falls out or rattles, too tight means it needs a tool or will not sit flat.
- The backing: it sits flat on every boss without rocking and without pushing any socket out of its pocket.
- A switch pressed into each socket: the socket must not move or tilt, and the switch sits flat on the frame without wobbling sideways. Report every socket that gives, especially the thumb's (no boss near it), S100's, S130's and the bottom row's, and S110's and S140's on the left half and S122's and S150's on the right (no boss north of them).
- In the tray: the frame drops in by hand and sits flat on all six standoffs, the walls touch nothing, and nothing under the backing rubs. The thumb switch's center post and pegs and S150's peg by the joint come down into reliefs in the tray's parking boss and upper dowel boss (DESIGN.md, The joint, Post reliefs): report whether those switches seat fully. With a tray that has the shelves under the backing's edges (DESIGN.md, Tray), the frame must still drop in and sit flat on all six standoffs without rocking: if it does not, the backing stands on a shelf, so report where.
- Along the south edge, the outer edge (the west edge on the left half, the east one on the right) and the north edge over columns 4 and 5, from the joint to the reset button, press the keys over the backing's edge: the backing should give less than before and stop on the shelf under it. Report each stretch where it still gives as much as before.
- Report each of these as good, loose or tight, with the key names.

## 3D printed tray

`model/kbdkid5/scripts/export_tray.py` exports a half's tray: walls, floor and the ledge the PCB rests on, the shelves along the south and outer edges and the north edge over columns 4 and 5 that catch the hand-wired frame's backing, standoffs bored for M2 heat-set inserts at the mounting drills, the cuts that clear the switches' hotswap sockets, the joint along the slanted edge, reliefs where a switch's center post or pegs come down over the tray, and the mounts for the parts that are not on the PCB (DESIGN.md: Tray, Parts in the tray, The joint). The tray is written floor on the bed.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_tray.py --pass tray.stl [right] [pin_hole_diameter=<mm>] \
        [nano_length=33.2] [nano_width=18.2] [nano_pocket_fit=0.1] [clamp_press=0.1] \
        [bar_clearance=0.1]

For a test print, `pin_hole_diameter` overrides the half's pin hole fit as modelled, and the others the figures the mounts rest on: the nice!nano's board length and width (the defaults are the user's caliper, so these suit another board), how much wider than the board its pocket prints, how hard the clamp's tab presses the board (how far below the tab's seat on the board its block's top stands), and the bar's clearance over the USB-C shell.

Every part goes into its socket in the tray, and then gets a blob of hot glue on top, which only keeps it down against vibration. Use hot glue and nothing permanent, so every part can come out undamaged and go into a new print (DESIGN.md, Parts in the tray).

Put a magnet into each of the joint's slots, against the thin skin at the joint face, with alternating poles along the joint, the right half opposite to the left, so the halves pull together and center themselves, and hold it with a blob of hot glue. To join the halves, press the dowel pins into the left half's holes, then push the right half on. Hot glue an S-04-02-N magnet to the bottom of the parking hole in each half's thumb key east wall, where it holds a pin while the halves are used apart.

The power switch's three leads come bent down. Straighten each with flat-nose pliers so it points straight back from the body, level with where it leaves it, and cut off the lead the wiring leaves unused if you like. Slide the switch north along the floor behind column 0's north wall, knob first through the slot, between the cradle's end blocks, until its face meets the ledge, then drop its retainer (below) into the grooves behind it, the retainer's opening over the leads. To take the switch out, lift the PCB off, pull the retainer out and slide the switch back south. Cut the reset button's two leads to taste, then press the button down into its socket behind the pin hole in column 3's north wall, between the side walls, its actuator toward the hole, its cover against the stop on the floor and its leads in the notches of the wall behind it. Cut no lead of either part shorter than 2 mm behind the body (the reset button's measured from its base's bottom face), which leaves the power switch's solder joints behind its retainer and room for the wires behind both (DESIGN.md, Parts in the tray).

To fit the nice!nano, solder its socket strips on first, press the M2 x 3 heat-set insert into the block south of it, lay the board in nose first, its USB-C shell under the bar at the USB window, put the clamp's tab (below) on with its nose over the board's south edge and screw it down with an M2 x 4. To take it out, with the PCB out, undo the screw and lift the tab off, bring a toothpick down the pry slot from over the south rim, through the slot's east part, the 2.8 mm beside the face nearest the screw, so it passes the last solder tail of the board's west row, its point down the recess and under the board's south edge, and lift.

`model/kbdkid5/scripts/export_clamp_tab.py` exports the nice!nano clamp's tab, the same for both halves and the test bay below, printed top face down, the nose standing up, with nothing to support.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_clamp_tab.py --pass tab.stl

`model/kbdkid5/scripts/export_power_switch_retainer.py` exports the power switch's retainer, the same for both halves, printed flat with the face that bears on the switch on the bed.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_power_switch_retainer.py --pass retainer.stl

`model/kbdkid5/scripts/export_nano_bay_test.py` exports one nice!nano bay cut out of the left tray at the tray's defaults, to settle the bay on a real board before printing whole trays (DESIGN.md, the nice!nano's bullets). `nano_length` and `nano_width` fit the bay to a calipered board.

To try it, fit the board as in the tray, with an M2 x 4, or on the test bay an M2 x 6 with an M2 nut under its head (the trays take only the M2 x 4). Push a USB-C cable in and pull it out: the board should not move or ride up. Wiggle the board across and along: loose means it rattles, too tight means it would not drop in flat on the seat. Then take the tab off and lift the board out with a toothpick as in the tray. Note whether the board went in and sat flat, whether it is loose, snug or tight across and along, whether the strips and their tails touched anything, whether it held under the cable, and whether the toothpick got it out.

    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/kbdkid5/scripts/export_nano_bay_test.py --pass bay.stl \
        [nano_length=33.2] [nano_width=18.2]

CI exports both halves, the tab and the retainer as `kbdkid5-tray-left.stl`, `kbdkid5-tray-right.stl`, `kbdkid5-nano-clamp-tab.stl` and `kbdkid5-power-switch-retainer.stl`, in `kbdkid5-<short commit hash>`, and the test bay as `kbdkid5-nano-bay-test.stl`, in `kbdkid5-test-<short commit hash>`. The test bay takes the trays' clamp tab, so trying it takes both zips.

## Placing parts

`scripts/place.py` asks the placement solver (the root [README.md](../../README.md), The placement solver) where a standoff or the hand-wired frame's bosses can go by the rules `check_layout.py` checks, and writes each run's report (`report.txt`, `report.json`), its problem (`problem.json`) and a picture per half to `tmp/place/<run>/`. From the repository root:

    podman run --rm -v "$PWD":/work -w /work placement python3 model/kbdkid5/scripts/place.py <run>

The runs, each one of the checks of the solver that work item 016 names:

- `sixth-standoff`: the sixth standoff, from 0.5 west of the user's spot. It finds the spot itself, with DESIGN.md's figures for its bore and its merge (Mounting, and Tray, Merged standoff). With `--scan-rule` it holds the body clear of the ledge and the magnet slots instead, the rule the first scan used, and finds the spot taken by the joint block and the slot.
- `north-east-standoff`: the north-east standoff (DESIGN.md, Mounting), where S140's socket gets its flat, and the declaration `layout.py` holds for it.
- `head-over-strip`: a backing screw head over the west socket strip, and how far it must rise to clear the strip.
- `frame-bosses`: the frame's bosses on both halves by DESIGN.md's rule (Hand-wired frame, Bosses), each against `layout.py`'s, then every check with them in place.
- `check-pass`: every check with the two standoffs' answers in place.

Its tests hold the solver's margins to `check_layout.py`'s and the runs to DESIGN.md's figures:

    podman run --rm -v "$PWD":/work -w /work placement python3 model/kbdkid5/scripts/test_place.py

## Parts to buy

For both halves:

- The power switches, reset buttons and, for the hand-wired frame, the key diodes: [doc/components.md](../../doc/components.md), section 13, lists them with their quantities, Electrokit article numbers and prices.
- A LiPo per half and whatever joins it to the nice!nano's B+ and B- pads, your own choice: the tray has no place for either (DESIGN.md, Battery).
- 8 supermagnete S-08-03-N disc magnets for the joint, 2 S-04-02-N for the pin parking.
- 2 hardened ISO 8734 (or DIN 6325 m6) 4 x 16 dowel pins in plain steel, not stainless (DESIGN.md, Pin parking, says why).
- M2 heat-set inserts and screws as on kbdkid4, and per half an M2 x 3 heat-set insert and an M2 x 4 screw for the nice!nano's clamp.
- For the hand-wired frame, 45 M2 x 3 heat-set inserts and 45 M2 x 4 screws (22 for the left half's backing, 23 for the right's), their heads flat underneath and at most 4.0 across and 1.5 tall.
- 4 Mill-Max 315-43-112-41-003000 socket strips (12 pins), two per nice!nano. Not Mill-Max's series 310 standard tail strips, which stand too tall for the bay and the backing (doc/components.md, section 8).
- For the hand-wired frame's wiring: enamelled 0.40 copper wire for the rows and columns (Electrokit 41004114, solderable through the enamel), Ethernet cable cores for the leads down to the nice!nano, and clipped diode leads soldered to their ends as the pins that plug into the strips.
