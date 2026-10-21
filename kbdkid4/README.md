# kbdkid4

The 3D printed parts of [kbdkid4](https://github.com/Tubbles/kbdkid4), a split wireless keyboard designed in [LibrePCB](https://librepcb.org): a tray, a switch plate, a PCB replica and a carrying case. The keyboard's design lives in the kbdkid4 repository, and these scripts build the parts from its board files: the STEP model `output/v1/kbdkid4_v1.step`, `boards/boards.lp` with the default board it lists, and `circuit/circuit.lp`. They read those files relative to the working directory, so they run inside a kbdkid4 checkout. The commands below run from this repository's root with kbdkid4 checked out at `external/kbdkid4`, the way CI runs them.

CI checks out kbdkid4's default branch for every run and uploads each part as an artifact named after this repository's commit. A push to kbdkid4 does not start this repository's CI, so after a board change run the CI workflow by hand from the Actions tab to export from kbdkid4's latest main.

## 3D printed tray

`kbdkid4/scripts/export_tray.py` builds a 3D-printable tray for the board from the exported STEP model, running FreeCAD headless. The board outline is located automatically (no hardcoded face indices); see the script's docstring for how and for the tray parameters.

    git clone https://github.com/Tubbles/kbdkid4 external/kbdkid4
    docker build -t freecad-headless -f docker/freecad.Dockerfile docker
    docker run --rm -v "$PWD":/work -w /work/external/kbdkid4 freecad-headless \
        freecadcmd /work/kbdkid4/scripts/export_tray.py --pass output/v1/kbdkid4_v1.step /work/tray.stl [key=value ...] [flip]

The parameters (gap, wall, floor, depth, standoff and ledge dimensions) and their defaults are listed in the script's usage header and constants block (gap, wall, floor, depth and standoff height in `kbdkid4/scripts/tray_shape.py`).

`kbdkid4/scripts/export_plate.py` likewise exports the switch plate: the kbdkid3 plate model (`resources/kbdkid3-plate-left.FCStd`), aligned onto the board by matching its switch cutouts to the board's switch grid, trimmed at the outer edges to fit the tray, extended over the microcontroller corner so it covers the whole board (with a conical recess on the underside at every soldered lead, 0.4 mm short of the top face, and for the reset switch a 3.0 mm hole to press it with a SIM ejector pin plus a 1.0 mm deep pocket in the underside over the switch and its pads), and cut with head-sized clearance holes at the board's mounting drills: the screws clamp the PCB onto the standoffs, the plate sits over their heads and is held down by the switches. The nice!view display is not fitted for now, so its header gets no recess. The whole hole pattern (cutouts, screw holes, lead recesses, reset hole and pocket) is then shifted `pattern_shift` mm along +X relative to the outline, 0.25 mm by default: the first printed plates sat right in the tray but their holes drifted off the board's features toward the nice!nano side, and a plate printed with a 0.5 mm shift came out offset about as far the other way; the cause is still open. Last, `side_shave` mm (0.1 by default) comes off the plate's west and east edges, since the printed plate is a snug fit across the tray's width. The plate STL is written upside down (top face on the bed, lead recesses opening upward) so it prints as is without supports. The word `covered` makes the variant for a half without the bottom row's third key (S123, hard to reach): its switch cutout is filled in solid, flush with the plate's faces, with a pit in the underside for the diode that stays soldered under it (the diode's pads and body plus 0.5 mm per side, 1.6 mm deep for the 1.14 mm tall diode, leaving 0.6 mm of the top face). CI exports both halves, plain and covered, as the `kbdkid4-plate-stl-<short commit hash>` artifact: `kbdkid4_v1_Plate_Left.stl`, `kbdkid4_v1_Plate_Right.stl` mirrored across the board's center line (the word `right`), `kbdkid4_v1_Plate_Left_Covered.stl` and `kbdkid4_v1_Plate_Right_Covered.stl`.

CI runs this against kbdkid4's committed STEP model, `output/v1/kbdkid4_v1.step`.

CI exports both halves as the `kbdkid4-tray-stl-<short commit hash>` artifact: `kbdkid4_v1_Tray_Left.stl` as described, and `kbdkid4_v1_Tray_Right.stl` built with the board's other side up (the word `right`), where the right half's switches and hotswap sockets sit, then turned over so it prints opening-up. That is not a mirror of the left tray: the right half's sockets do not reach the board edge, so that tray has no ledge notches, and the ledge reliefs (the ledge cut away beside any underside body, the nice!nano, a hotswap socket or the battery connector, that comes within `relief_clearance` of it, so a populated board seats despite print swelling) follow that half's parts. For the same reason the left tray's wall is pocketed where the west socket tabs reach it, leaving them 0.5 mm from it, and a standoff that any of those bodies comes within 1 mm of gets a flat on that side. The nice!nano's depth there is measured, not taken from its package model: it sits flush on 2.56 mm sockets on the left half and 4.3 mm ones on the right.

## 3D printed PCB replica

`kbdkid4/scripts/export_pcb.py` exports a printable stand-in for the bare board, for test-fitting the tray, plate, switches and screws before the fabricated boards arrive: the outline extruded to the board thickness with every drill hole, no components. Printed parts come out slightly larger than modelled, so the replica is pulled in by `pull_in` (default 0.2 mm) per side: the outline moves inward and every hole grows outward by that much. The thickness stays as modelled unless overridden with `thickness=`.

    docker run --rm -v "$PWD":/work -w /work/external/kbdkid4 freecad-headless \
        freecadcmd /work/kbdkid4/scripts/export_pcb.py --pass output/v1/kbdkid4_v1.step /work/pcb.stl [right] [pull_in=0.2] [thickness=1.6]

CI uploads both halves as the `kbdkid4-pcb-stl-<short commit hash>` artifact: `kbdkid4_v1_Pcb_Left.stl`, and `kbdkid4_v1_Pcb_Right.stl` mirrored across the board's center line (the word `right`). A bare board turned over would be its own mirror image, but a print is not: its bed side and its top side come out with different surfaces.

## 3D printed carrying case

`kbdkid4/scripts/export_case.py` exports a carrying case for both halves, in two shells that close around them: the halves lie sole to sole with their keys facing outward, each in its own shell, and the shells meet where the soles touch. Each half goes into its shell keys first, in its tray: the tray sits in a pocket 0.3 mm larger per side than the tray's outside, and its rim rests on a step at the bottom of that pocket, so the keycaps keep 1 mm from the floor's padding and no key is held down. The wall by the USB port has a notch over each of the tray's windows, one for the power switch and one wide enough for a USB plug, so both halves can be switched and charged with the case closed. The closed case measures 142.4 x 90.4 x 56 mm.

Magnets hold the shells together, with a Velcro band as a backup. To finish the case, buy and fit:

- Eight 5 x 3 mm disc magnets, four per shell, glued into the pockets in the face where the shells meet. Glue all of one shell's magnets with the same pole facing out and all of the other shell's with the other pole out, so the shells attract. The pockets are 0.3 mm deeper than the magnets, which leaves room for the glue and keeps the magnets below the face, so they never hold the shells apart.
- A 10 mm wide, 2 mm thick Velcro band, around the closed case the short way: through the tunnel in each long wall of both shells, and across the outside of both floors.
- 1 mm thick padding glued onto each shell's floor, inside. The walls and the step get none.

The case assumes a 1.0 mm rubber sole glued under each tray, a half 24 mm tall from the underside of its sole to the top of its keycaps, and a USB plug whose grip (the part you hold) measures 13 x 7 mm. If yours differ, change `SOLE_THICKNESS_MM`, `KEY_HEIGHT_MM`, `USB_PLUG_GRIP_WIDTH_MM` or `USB_PLUG_GRIP_HEIGHT_MM` in the constants at the top of the script. The tray's own dimensions come from `kbdkid4/scripts/tray_shape.py`.

    docker run --rm -v "$PWD":/work -w /work/external/kbdkid4 freecad-headless \
        freecadcmd /work/kbdkid4/scripts/export_case.py --pass output/v1/kbdkid4_v1.step /work/case.stl [right]

Without `right` it exports the left half's shell, with `right` the right half's. Both come out floor down and opening up, so they print without supports. CI uploads both as the `kbdkid4-case-stl-<short commit hash>` artifact: `kbdkid4_v1_Case_Left.stl` and `kbdkid4_v1_Case_Right.stl`.
