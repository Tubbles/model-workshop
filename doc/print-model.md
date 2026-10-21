# Print model

How the user's printer prints, as measured on test prints, for anyone who designs a fit. All figures are in mm. Each one carries its source: a decision log (`doc/log/`), a work item (`doc/work/`), a file in this repository, or a commit. Commits marked `kbdkid4` are in Tubbles/kbdkid4, the others in this repository (README.md, History).

## Printer and material

- Printer: the user's stock Creality Ender 3 V2 (model/camera-arm/CLAUDE.md and the docstring of `model/camera-arm/scripts/export_camera_arm.py`). kbdkid4 053755b mentions the printer's Klipper host Pi standing on its base rail.
- Material: PETG. The user, 2026-10-17: "I am using petg which is a little softer and grips the blades neatly" (doc/log/2026-10-17.md). The 2 % strain limit that the snap hook, the clamp tab and the scrapped socket fingers were checked against is a PLA figure (doc/log/2026-10-17.md, doc/log/2026-10-18.md).
- Layer height: 0.2. kbdkid4 7255b7e leaves "three 0.2 mm layers" over the diode pit, kbdkid4 75cdde7 found "the single 0.2 mm layer" over the lead recesses showing through, and the first backing's pads stepped 0.05 "under a 0.2 layer" (doc/log/2026-10-18.md).
- Nozzle: not recorded. A comment in `model/kbdkid4/scripts/export_tray.py` calls the power switch pocket's 0.4 skin "one nozzle width" (`POWER_SWITCH_POCKET_SKIN_MM`).
- Slicer: not recorded. model/kbdkid5/DESIGN.md (Slit test strip) notes that PrusaSlicer's "Slice gap closing radius" defaults to 0.049, which fills any crack under 0.098 while slicing, and says to lower it for the slit strip.

## The model the scripts use

From `model/kbdkid5/scripts/layout.py` (Printed fits) unless noted:

- `PRINT_SWELLING_PER_SIDE_MM` = 0.2: a vertical face moves 0.2 out of the plastic, so a hole or slot prints 0.2 per side smaller than modelled. kbdkid4 set the same 0.2 as the PCB replica's `pull_in` default, "the expected print swelling per side" (model/kbdkid4/CLAUDE.md, kbdkid4 ced2070, 2026-09-26). No measurement of it is recorded before the bay pocket confirmed it across (Measurements, below).
- `printed_fit(nominal, fit)`: a fit is modelled as the nominal size plus the swelling on both sides plus the fit's clearance, `SNUG_FIT_MM` 0.0 ("holds a part pressed in by hand") or `SLIP_FIT_MM` 0.1 ("lets a part slide in, or leaves room for glue"). Introduced after the 003 review found the first joint fits ignored the swelling (doc/log/2026-10-17.md, #fit #joint).
- `PRINT_SWELLING_AT_45_DEGREES_MM` = 0.283: a 45 degree face swells 0.2 along its normal, 0.283 along x, y or z (doc/log/2026-10-17.md, #hook #fit). Derived, not measured.
- `PRINT_RISE_OF_UP_FACING_BOTTOMS_MM` = 0.2: the floor of a notch, slot, recess or blind bore that a part must fit over is counted 0.2 higher as printed, and the plastic left under it is counted where modelled, the thinner reading (doc/log/2026-10-17.md, #print #fit). Not measured: it "stays until one is measured" (doc/log/2026-10-19.md).
- `PRINT_RISE_OF_TOP_FACES_MM` = 0.05: a print's top face, the face that is up on the bed, comes out 0.05 high. Measured (below).
- The face on the bed: the user, 2026-10-19, it "probably sees very little" (doc/log/2026-10-19.md). Not measured.
- `NANO_POCKET_END_FACE_SWELLING_MM` = 0.13: the nice!nano bay's two end faces, from a measured sum (below).

## Measurements

| What | Modelled | By the model | Printed | What follows | Source |
|---|---|---|---|---|---|
| Wide opening across, vertical faces (nice!nano bay pocket) | 18.8 | 18.4 | 18.41 to 18.46, calipered | The 0.2 per side holds across a wide opening | doc/log/2026-10-20.md, model/kbdkid5/DESIGN.md (nice!nano) |
| Short end faces along the same pocket (the clamp foot's and the north block's faces) | 33.8 apart | 33.4 | 33.54, calipered | The two faces swelled 0.26 together, not 0.4. Only the sum was measured, taken as 0.13 per face, cause not known | doc/log/2026-10-20.md, `layout.NANO_POCKET_END_FACES_SWELLING_MM` |
| Top face (the frame body of the socket pocket strip, printed top face down) | 1.6 thick | 1.8 (the 0.2 rise then applied) | "roughly 1.65, measured with the calipers touching as large an area as possible" | A top face rises 0.05. The user's reading: the top face is rough rather than swollen, "as the nozzle sweeps over the surface it melts material and dispenses new material" | doc/log/2026-10-19.md, 3958d91 |
| Holes about 3 across (hole strip, around the hotswap socket's 2.90 bosses) | 3.5 to 3.0 in 0.1 steps | 3.3 would print 2.90 | 3.2 held best, 3.1 and 3.0 would not take the socket, 3.5 to 3.3 loose | A hole this size prints about 0.15 per side smaller than modelled, not 0.2. Friction only, so the 0.15 is inferred from feel | doc/log/2026-10-18.md, model/kbdkid5/DESIGN.md (Hole strip), 211c423 |
| Switch post and peg holes (switch hole strip, around the calipered 3.17 post and 1.65 pegs) | post 3.42 to 3.62 and pegs 1.90 to 2.10 in 0.05 steps in cells 1 to 5, cell 6 3.8 and 2.3 | 0.05 tight to 0.15 loose, taking the hole strip's 0.15 per side | Cell 1 (3.42 and 1.90) fit best, "slightly smaller than the posts themselves but the holes deforms and hugs the posts as the switch gets pushed in, allowing for a really nice and tight friction fit". Judged by feel, not calipered | A real frame's post and peg holes are cell 1's. Cell 1 was the tightest cell, so the result is consistent with a slight interference but measures no shrink at the pegs' size | doc/log/2026-10-21.md, doc/work/012-switch-hole-test.md, model/kbdkid5/DESIGN.md (Switch hole strip) |
| Narrow slits, first slit strip (switch plate cells on it) | 0.5 to 1.0 | | "the blades goes through the smallest slits easily", the 0.4 blade through the 0.5 | The 0.2 per side does not close slits this small. 0.5 slits print open. On this strip the plate "grips onto the sides so its hard to read the blade friction" | doc/log/2026-10-17.md |
| Narrow slits, second slit strip (no plate, one slit per blade) | blade plus -0.15 to +0.10 | | Cell 6, the +0.10, held a switch best: 0.50 for the 0.4 blade, 0.30 for the 0.2 blade | Slits are sized as modelled with no `pull_in` | doc/log/2026-10-17.md, doc/work/007-slit-test-round-2.md |
| Socket pocket, first pocket strip (around the Kailh socket body, 9.55 x 6.85) | fits -0.10 to +0.15 | | "3 and 5 are the only ones binding at all, all the others are loose" | Pockets print larger than the model says | doc/log/2026-10-17.md |
| Socket pocket, third pocket strip (walls built whole, around the tray's rectangle cover of the socket) | fits -0.40 to -0.15 | | Cell 5, the -0.20: "nice satisfying snap and good press fit" | Superseded by the fourth strip | doc/log/2026-10-18.md |
| Socket pocket, fourth pocket strip (walls on the socket's real outline) | fits -0.40 to -0.15 | 9.40 x 6.70 at -0.15 | "its number 6 is good, I was barely able to push the socket into number 5 so that's too tight" | -0.15 is the frame's pocket fit | doc/log/2026-10-18.md, model/kbdkid5/DESIGN.md (Pocket strip) |
| Backing pads under the pocket strip | pad tops -0.10 to +0.15 against the socket's bottom, 0.05 steps | | Only cell 1 (-0.10) let the backing sit flush on the bosses | Steps under a layer do not print: at 0.2 layers cells 1 to 3 print at one height (0.4), cells 4 to 6 at another (0.6). Step by whole layers | doc/log/2026-10-18.md |
| Thin wall sliver (the west peg's hole drilled through a pocket wall) | 0.1 to 0.2 left | | "The walls came out good" | A sliver this thin prints | doc/log/2026-10-18.md |
| One 0.2 layer over a recess (kbdkid4's plate lead recesses) | 0.2 skin | | "showed through" | Two layers, 0.4 | kbdkid4 75cdde7, 2026-10-13 |
| One 0.2 layer over a 6.25 x 2.56 pit (kbdkid4's covered plate) | 0.2 skin | | "printed translucent" | Three layers, 0.6. kbdkid5's covered plate keeps three (`model/kbdkid5/scripts/plate_shape.py`) | kbdkid4 7255b7e, 2026-10-12 |
| Plate hole pattern against the fabricated board (kbdkid4) | no shift | | The first printed plates sat right in the tray, their holes about 1 off toward the nice!nano side by the thumb key, the reset button and the rightmost screw. With a 0.5 shift they came out offset about as far the other way | `pattern_shift` 0.25 along +x. Cause not found (Unmeasured or inferred, below) | kbdkid4 9864702 (2026-10-09), kbdkid4 278a6a7 (2026-10-10) |
| Plate width in the tray (kbdkid4) | | | "a snug fit across the tray's width" | `side_shave` 0.1 off the west and east edges | kbdkid4 186266d, 2026-10-10 |
| Populated board in the printed tray (kbdkid4) | Clearances at nominal: 0.03 (nice!nano to the north ledge), 0.17 (west socket tabs to the wall), 0.38 (bottom row sockets to the south ledge) | | "The soldered board would not seat" | Ledge reliefs beside any body within 0.5 of the ledge (`relief_clearance`), wall pockets keeping the socket tabs 0.5 from the wall, standoff flats at 1.0 | kbdkid4 e677e0b and babfc60 (2026-10-11), kbdkid4 5a43865 (2026-10-12) |

The PCB replica's and the PCB mock's `pull_in` (0.2, outline moved in and every hole out) is the model's swelling, not a measurement. Their thickness stays as modelled, "because a print's height follows its layer count rather than bead spread" (kbdkid4 ced2070). The top face measurement above came later and found 0.05.

## Unmeasured or inferred

- How holes at the switch's peg size print: still unmeasured. The switch hole test strip (8ebfb81) took the hole strip's 0.15 per side, "That is unmeasured for holes the pegs' size" (8ebfb81). Its cell 1, the tightest, 1.90 as modelled for the 1.65 pegs, fit best by feel, which is consistent with a slight interference but calipers nothing (doc/work/012-switch-hole-test.md).
- The rise of up-facing bottoms (0.2) and the face on the bed: see the model above.
- How the bay end faces' 0.26 splits between the two faces, and why short end faces swell less than long ones: not known (`model/kbdkid5/scripts/layout.py`, the comment on `NANO_POCKET_END_FACES_SWELLING_MM`). The scripts take every figure that depends on the split at its worst (doc/log/2026-10-20.md).
- How much larger than the model the pockets print: only that they fit looser than modelled (doc/log/2026-10-17.md, doc/log/2026-10-18.md).
- The cause of kbdkid4's plate hole drift (Measurements, above). Checked 2026-10-09 (kbdkid4 9864702): kbdkid4's `boards/board_1.1/board.lp` has every switch pitch at exactly 19.05, kbdkid4's committed Excellon files put the 3.4 switch drills and the 2.4 mounting drills at the same positions, the kbdkid3 plate model's cutouts match the switch grid to 0.0005, the exported plate STL has every cutout, screw hole and the reset hole at its design x within 0.08, and the tray STL's standoff bores sit at the mounting drills to 0.001. Both parts were printed unscaled. A drift of 1 over 125 is 0.8 %, the size of a print scale or shrinkage error, but a plate shrunk that much should sit loose in the tray, which it does not. A linear 1 drift would have left the 0.5 shift's plate with both ends 0.5 off in opposite directions, not offset the other way (kbdkid4 278a6a7). SUGGESTIONS.md (kbdkid4) lists the measurements that would find the cause.
- Elephant foot: not measured. The designs chamfer bed edges against it, 0.4 at 45 degrees on the joint face (model/kbdkid5/DESIGN.md, The joint) and on slots that must stay open (doc/log/2026-10-17.md, #hook #print).

## Test prints

| Date | Print | Tested | Settled | Source |
|---|---|---|---|---|
| by 2026-10-09 | kbdkid4 switch plates | The plate on the fabricated board in the tray | Holes drift about 1 toward the nice!nano side, `pattern_shift` 0.5 | kbdkid4 9864702 |
| 2026-10-10 | kbdkid4 plate with the 0.5 shift | The shift | Offset about as far the other way, `pattern_shift` 0.25. The plate is snug across the tray, `side_shave` 0.1 | kbdkid4 278a6a7, kbdkid4 186266d |
| 2026-10-11 | kbdkid4 tray with the soldered board | Seating | The board did not seat, ledge reliefs (`relief_clearance` 0.5) | kbdkid4 e677e0b, kbdkid4 babfc60 |
| 2026-10-12 | kbdkid4 assembled first print | The nice!nano's depth, the USB window, the power switch body's place | Measured on the parts (doc/components.md, section 11) | kbdkid4 bb2d1d9, kbdkid4 26bddb5, kbdkid4 eb6fb7b |
| 2026-10-12 | kbdkid4 covered plate | The diode pit's skin | One layer translucent, three layers | kbdkid4 7255b7e |
| 2026-10-13 | kbdkid4 plate | The lead recesses' skin | One layer shows through, two layers | kbdkid4 75cdde7 |
| 2026-10-17 | kbdkid5 first slit test strip | Slits 0.5 to 1.0 for the switch's blades, with plate cells | No slit grips, the plate hides the friction | doc/log/2026-10-17.md |
| 2026-10-17 | kbdkid5 second slit test strip (c2885ea) | One slit per blade, blade plus -0.15 to +0.10 | +0.10 holds best: 0.50 and 0.30 | doc/log/2026-10-17.md, doc/work/007-slit-test-round-2.md |
| 2026-10-17 | kbdkid5 first socket pocket strip (cf676e8) | Pocket fits -0.10 to +0.15 | Loose but cells 3 and 5. Test the pocket alone, with pin holes that do not bind | doc/log/2026-10-17.md |
| 2026-10-18 | kbdkid5 hole strip | Pin holes 3.5 to 3.0 | 3.2 | doc/log/2026-10-18.md |
| 2026-10-18 | kbdkid5 first backing | Pads -0.10 to +0.15 | Cell 1 (-0.10). Pads smaller in plan, steps by whole layers | doc/log/2026-10-18.md |
| 2026-10-18 | kbdkid5 second pocket strip | Pocket fits -0.40 to -0.15 | No fit result recorded. The walls are built whole with the holes drilled through (99709b8) | doc/log/2026-10-18.md, model/kbdkid5/DESIGN.md (Frame cells) |
| 2026-10-18 | kbdkid5 third pocket strip | The same fits, walls whole | -0.20 around the cover. The whole walls print | doc/log/2026-10-18.md |
| 2026-10-18 | kbdkid5 fourth pocket strip (90f702a) | The same fits, walls on the socket's outline | -0.15, the frame's pocket fit | doc/log/2026-10-18.md |
| 2026-10-19 | kbdkid5 lip strip | Lips on fingers holding the socket | Scrapped: "I don't think this will be strong enough to push in a switch, regardless of finger size" | doc/log/2026-10-19.md |
| 2026-10-19 | kbdkid5 pocket strip's frame body | Its thickness | 1.65 for 1.6, a top face rises 0.05 | doc/log/2026-10-19.md |
| 2026-10-19 | kbdkid5 nice!nano bay test strip (work item 006) | Three bays with the screw clamp of work item 009, pressing the board 0.0, 0.1 and 0.2 | "It needs a lot of improvements": a heavy duty pocket (work item 010) | doc/log/2026-10-19.md, doc/work/009-nano-screw-clamp.md, doc/work/010-heavy-duty-nano-bay.md |
| 2026-10-20 | kbdkid5 single test bay (507370b) | The heavy duty pocket | "the idea flies". 18.41 to 18.46 across, 33.54 along: the pocket resized (work item 011) | doc/log/2026-10-20.md, doc/work/011-socket-strips-and-raise.md |
| 2026-10-21 | kbdkid5 switch hole test strip (8ebfb81) | Post and peg holes printing -0.05 to +0.15 over the calipered post and pegs | Cell 1: post 3.42 and pegs 1.90 as modelled, "a really nice and tight friction fit" | doc/log/2026-10-21.md, doc/work/012-switch-hole-test.md |

Exported but not printed yet, as far as the sources go: the wide slit test strip (1d33328, open in doc/work/007-slit-test-round-2.md and model/kbdkid5/DESIGN.md) and kbdkid4's carrying case ("nobody has handled a printed case yet", SUGGESTIONS.md, kbdkid4).
