# Camera arm

An arm that holds a Raspberry Pi Camera Module 2 over a stock Ender 3 V2, at the east end of the Pi case on the printer's front right, looking across the bed at a point 5 cm in front of its center at one fixed angle. The arm is one bar of constant section, 14 x 15 mm, bent along its way in smooth bends of 8.5 mm radius at its middle: it lies on the printer base's right 4040 rail (the one running front to back at bed level), runs east low behind the Pi case, rises behind it and turns into the bar behind the camera's case. Nothing of it reaches past the Pi case's east side, so the printer's footprint stays the Pi case's. It slides onto the rail without screws: two T-rails under the part of the bar that lies on the rail, the profile of the Pi mount from Printables 277420, run in the rail's two top slots. From the upright forward the slots hold two spacer rails, the arm, that Pi mount with its case, and one or two shims, closed by the rail's stock end cap. The arm lies against the Pi mount's back end, and the spacer rails stay below the rail's top face and run from the bolts that hold the upright to the arm. The case is two shells around the camera board, and the 15 pin ribbon leaves the case's bottom through a socket that takes the end of a cable sock.

## Printed parts

`model/camera-arm/scripts/export_camera_arm.py` writes five STLs, each lying on the bed the way it prints:

- `camera-arm.stl`, the arm, on its back: the riser's back face on the bed, the part that lies on the rail 15 mm over it with the T-rails standing up from its back face, their profile in the layer plane. It stands on supports from the build plate, since its center of mass lies outside the riser's face.
- `camera-arm-spacer.stl`, one spacer rail, 88.5 mm long, lying on its underside. Print two, one per slot. Its lower taper overhangs a little past 45 degrees.
- `camera-arm-shim.stl`, one 1 mm shim with the spacer's profile, standing on an end. Print four, for one or two per slot.
- `camera-arm-case-back.stl`, the back shell, its back face on the bed.
- `camera-arm-case-front.stl`, the front shell, its front face with the lens window on the bed.

CI runs the export from this repository's root:

    mkdir -p camera
    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/camera-arm/scripts/export_camera_arm.py --pass camera

CI uploads the five as the `camera-arm-<short commit hash>` artifact. The job's log also lists the fits, the rail stack, the clearances to the printer, the Pi case and the cable, and what part of the bed the camera sees over the Y travel.

## Hardware

- Six M2 heat-set inserts, in bores 3.2 mm across: four in the back shell's standoffs and two in the arm's bar.
- Six M2 screws: four through the camera board's holes into the back shell, closing the case, and two through the ears on the back shell into the arm. The ear screws go in from the front, where a straight driver up to 5 mm across passes the front shell.
- A cable sock over the ribbon, its end in the 18.4 x 8.8 mm socket under the case. The socket takes a round sock end up to about 8.4 mm, squeezed to an oval (a 10 mm sock's 31 mm perimeter fits it easily), or a sock flattened around the flat ribbon.

## Assembly

1. Take off the rail's end cap.
2. Slide both spacer rails into the top slots until they stop under the upright, at its bolts.
3. Slide the arm in behind them, its T-rails in both slots, the bent end east of the rail. Its back face then stands about 81 mm in front of the upright.
4. Slide in the Pi mount, against the arm. The Pi case goes on and comes off its keyholes with the arm in place: it slides 11.2 mm up the mount's slope toward the riser, which stands 2 mm behind it at the end of that slide.
5. Push in shims, one or two per slot, until the stack reaches the rail's end, and put the cap back on.
6. Close the camera case around the board and screw it to the arm through the ears, from the front.

## Where the numbers come from

The board's outline, holes, lens block and connector come from Raspberry Pi's mechanical drawing of the Camera Module V2.1, the field of view (62.2 degrees horizontal, 48.8 degrees vertical) from Raspberry Pi's camera documentation, the print area and travel from the printer's Klipper configuration (X and Y 0 to 235), the rail's slots from Creality's 4040 profile model for the Ender-3, and the upright, the bed plate and the gantry from Creality's mechanical CAD of the Ender-3, since Creality publishes no CAD for the V2. The Pi mount and case are the Printables STLs, placed by measurements on the printer: the mount's back end 95 mm in front of the upright, the case's left side in line with the rail's, its rearmost point about 92 mm in front of the upright, and the print head's reach 80 mm in front of the upright and 10 mm past the rail's outer side, its lowest point about 1 cm over the Pi case. The keyholes' slide, 11.2 mm from a peg's place at the end of its slot to the hole it lifts out of, is measured in the mount's STL. The script's docstring cites each source.

Calculated from those: the camera's height. The previous arm (8a8eb48) held its case's lowest point 105.0 mm above the rail, 44.0 over the Pi case's top edge at 61.0, the screen's highest point, and the camera comes down by half that, 22.0. The camera's place along x puts the bar's back, at the camera case's north end, on the Pi case's east edge, where the riser's east face is too. The arm's run lies against the Pi mount, which sets the spacer rails' length. Behind the Pi case the riser leans back under its rearmost corner and stands plumb 2 mm behind where that corner gets to when the case slides off its keyholes.

Calculated, not measured: the spacer rails stop at the upright's M5 bolts, which V2 assembly guides put up through the base rail into the 2040's center bores, 7.5 mm behind the upright's front face at the bolts' shanks. If they stop elsewhere, the arm moves along the rail by the difference. Taken from the Ender-3's CAD, not the V2's: the bed's height above the rail, the nozzle's line and the bed's right edge, which set where the camera aims, and the slot's mouth chamfer, which sets how high the spacer rails reach. The print head's reach is taken from the upright's front face. Assumed without a source, to be measured on the real parts: the board 1.0 mm thick, room for components 3.0 mm in front of the board (the lens block passes through a window) and 4.0 mm behind it, the ribbon 16 mm wide, the sock's end about 8 to 10 mm across round, or flattened around the flat ribbon.
