# Camera arm

An arm that holds a Raspberry Pi Camera Module 2 over a stock Ender 3 V2, looking down at the bed's center from the front and to the right at one fixed angle. It slides onto the printer base's right 4040 rail (the one running front to back at bed level) without screws: two T-rails under its base, the profile of the Pi mount from Printables 277420, run in the rail's two top slots. From the upright forward the slots hold two spacer rails, the arm, that Pi mount with its case, and one or two shims, closed by the rail's stock end cap. The spacer rails stay below the rail's top face and stop at the bolts that hold the upright, which sets where the arm stands. A post rises between the print head's reach and the back of the Pi case, and a bar carries the camera case forward over the Pi case. The case is two shells around the camera board, and the 15 pin ribbon leaves the case's bottom through a socket that takes the end of a cable sock.

## Printed parts

`model/camera-arm/scripts/export_camera_arm.py` writes five STLs, each lying on the bed the way it prints:

- `camera-arm.stl`, the arm, on its back: the base's back end on the bed, the T-rails standing up from it with their profile in the layer plane, and the post hanging over the bed, so it prints with supports.
- `camera-arm-spacer.stl`, one spacer rail, 62.5 mm long, lying on its underside. Print two, one per slot. Its lower taper overhangs a little past 45 degrees.
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
3. Slide the arm in behind them, its T-rails in both slots. Its base's back end then stands about 55 mm in front of the upright.
4. Hang the Pi case on its mount first, then slide the mount in. The case comes off its keyholes by sliding about 12 mm up the mount's slope, straight toward the arm's post, which stands 2.1 mm away, so with the arm in place the case neither goes on nor comes off: take the mount out with the case on it.
5. Push in shims, one or two per slot, until the stack reaches the rail's end, and put the cap back on.
6. Close the camera case around the board and screw it to the arm through the ears, from the front.

## Where the numbers come from

The board's outline, holes, lens block and connector come from Raspberry Pi's mechanical drawing of the Camera Module V2.1, the field of view (62.2 degrees horizontal, 48.8 degrees vertical) from Raspberry Pi's camera documentation, the print area and travel from the printer's Klipper configuration (X and Y 0 to 235), the rail's slots from Creality's 4040 profile model for the Ender-3, and the upright, the bed plate and the gantry from Creality's mechanical CAD of the Ender-3, since Creality publishes no CAD for the V2. The Pi mount and case are the Printables STLs, placed by measurements on the printer: the mount's back end 95 mm in front of the upright, the case's left side in line with the rail's, its rearmost point about 92 mm in front of the upright, and the print head's reach 80 mm in front of the upright, its lowest point about 1 cm over the Pi case. The script's docstring cites each source.

Calculated, not measured: the spacer rails stop at the upright's M5 bolts, which V2 assembly guides put up through the base rail into the 2040's center bores, 7.5 mm behind the upright's front face at the bolts' shanks. If they stop elsewhere, the arm moves along the rail by the difference. Taken from the Ender-3's CAD, not the V2's: the bed's height above the rail, the nozzle's line and the bed's right edge, which set where the camera aims, and the slot's mouth chamfer, which sets how high the spacer rails reach. The print head's reach is taken from the upright's front face. Assumed without a source, to be measured on the real parts: the board 1.0 mm thick, room for components 3.0 mm in front of the board (the lens block passes through a window) and 4.0 mm behind it, the ribbon 16 mm wide, the sock's end about 8 to 10 mm across round, or flattened around the flat ribbon.
