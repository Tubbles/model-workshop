# Camera arm

An arm that holds a Raspberry Pi Camera Module 2 over a stock Ender 3 V2, looking down at the bed from behind and to the right at one fixed angle. The arm stands on the top face of the printer base's right 4040 rail (the one running front to back at bed level), behind the right upright, clamped by one M3 bolt into a printed twist-in T-nut with a captive M3 nut in the rail's outer top slot. Two ribs under its base sit in both top slots' mouths, so the bolt alone holds it square. A post rises to a bracket that carries the camera case. The case is two shells around the camera board, and the 15 pin ribbon leaves the case's bottom through a socket that takes the end of a cable sock.

## Printed parts

`model/camera-arm/scripts/export_camera_arm.py` writes four STLs, each lying on the bed the way it prints, without support:

- `Camera_Arm.stl`, the arm, on its side: its profile, in the vertical plane of the camera's viewing direction, lies on the bed, and the part is built up from there along the case's width.
- `Camera_T_Nut.stl`, the T-nut, with the face that bears on the slot's lips on the bed and the pocket for its M3 nut opening upward.
- `Camera_Case_Back.stl`, the back shell, its back face on the bed.
- `Camera_Case_Front.stl`, the front shell, its front face with the lens window on the bed.

CI runs the export from this repository's root:

    mkdir -p camera
    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/camera-arm/scripts/export_camera_arm.py --pass camera

CI uploads the four as the `camera-arm-<short commit hash>` artifact. The job's log also lists the fits, the clearances to the printer and what part of the bed the camera sees over the Y travel.

## Hardware

- One M3 x 10 socket head bolt and one M3 nut (5.5 mm across flats, 2.4 mm thick), pressed into the T-nut.
- Six M2 heat-set inserts, in bores 3.2 mm across: four in the back shell's standoffs and two in the arm's bar.
- Six M2 screws: four through the camera board's holes into the back shell, closing the case, and two through the ears on the back shell into the arm. The ear screws go in from the front, where a straight driver up to 5 mm across passes the front shell.
- A cable sock over the ribbon, its end in the 18.4 x 8.8 mm socket under the case. The socket takes a round sock end up to about 8.4 mm, squeezed to an oval (a 10 mm sock's 31 mm perimeter fits it easily), or a sock flattened around the flat ribbon.

## Assembly

1. Fix the arm to the rail before the case goes on. The back shell sits over the M3 bolt's axis, so once the case is on, only an L key reaches the bolt, not a straight driver.
2. Press the M3 nut into the T-nut and thread the bolt through the arm's base two or three turns into it.
3. Set the base on the rail with the T-nut down the outer slot lengthwise.
4. Pull the bolt up so the T-nut bears on the slot's lips, and turn it clockwise: the T-nut turns with it to its stop, then the bolt tightens. Loose on the slot's floor the T-nut sits 0.3 mm lower in the slot's taper, where neither its corners nor the nut's have room to turn.
5. Close the case around the board and screw it to the arm through the ears.

## Where the numbers come from

The board's outline, holes, lens block and connector come from Raspberry Pi's mechanical drawing of the Camera Module V2.1, the field of view (62.2 degrees horizontal, 48.8 degrees vertical) from Raspberry Pi's camera documentation, the bed size and travel from Creality's Ender-3 V2 firmware configuration, and the rail, its slot, the upright, the bed plate and the gantry from Creality's mechanical CAD of the Ender-3, since Creality publishes no CAD for the V2. The script's docstring cites each source.

Assumed without a source, to be measured on the real parts: the board 1.0 mm thick, room for components 3.0 mm in front of the board (the lens block passes through a window) and 4.0 mm behind it, the ribbon 16 mm wide, the sock's end about 8 to 10 mm across round, or flattened around the flat ribbon. On the Ender-3 the power supply stands on the rail behind the right upright. On the V2 it moved into the base, and that the rail is free there is assumed, not drawn.
