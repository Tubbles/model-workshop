"""Export the slit test strip (STL): a row of single-key cells of the
fused mock's PCB layer alone, whose pin slits differ in width only, to
find the slits that grip a switch's pins.

This is the second strip (work item 007): the first one's slits, 0.5
to 1.0 wide under a plate cell, all let the blades through easily, and
its plate cells gripped the switch's sides, which hid the blades'
friction (doc/log/2026-10-17.md). The blades' calipered thicknesses
differ (layout.CHOC_PIN_CALIPERED_BLADE_THICKNESSES_MM), so here each
pin's slit is its own blade's thickness plus the cell's clearance as
modelled, with no pull_in, the same clearance on both pins of a cell,
stepping by SLIT_CLEARANCE_STEP_MM from FIRST_SLIT_CLEARANCE_MM: -0.15
to +0.10, which makes the middle pin's slits 0.05 to 0.30 and the
peg-side pin's 0.25 to 0.50. The last cell's 0.50 repeats the first
strip's loose 0.5 for the thick blade as a reference, and cell 1's
middle slit needs the slicer's gap closing lowered (DESIGN.md). Every
slit has the fused mock's default length (layout.default_slit_length()),
which keeps pull_in, since only the width grips.

The word wide makes the wide strip instead, the first strip's widths
at the default pull_in without its plate: 0.5 to 1.0 stepping by
WIDE_SLIT_WIDTH_STEP_MM from WIDE_FIRST_SLIT_WIDTH_MM, as modelled
whatever the pull_in, the same width on both pins of a cell. The user
prints in PETG, and on the second strip its widest cell held a switch
best (doc/log/2026-10-17.md).

Each cell is a 19.05 square of the PCB layer with one key's footprint
holes (grown by pull_in) and its two pin slits, the cells side by side
at the key pitch, with no plate. Cell k (from 1, west to east) has k
notches in its south edge, so a printed cell names itself. The strip
prints like the fused mock's PCB layer, its underside on z = 0, 1.6
thick.

A switch is the same on both halves, so is the strip: the footprint is
the left half's, which the right half's fused mock uses too.

Runs headless under FreeCAD's console interpreter (see
freecad_common.py for the freecadcmd quirks that shape the
invocation):

    freecadcmd model/kbdkid5/scripts/export_slit_test.py --pass <strip.stl> [wide]
        [pull_in=0.2]

It prints each cell's clearance (or width) and slit widths and checks
for one valid solid of the PCB layer's volume less the notches, every
slit centered on its pin at its own size and at DESIGN.md's width, the
notch count of every cell, and a closed mesh.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App
import Part

import layout
import pcb_shape
from freecad_common import check_closed_mesh, export_stl, run_and_exit, script_arguments

CELL_COUNT = 6
# Cell 1's clearance, each slit's width less its blade's calipered
# thickness, and the step from one cell to the next.
FIRST_SLIT_CLEARANCE_MM = -0.15
SLIT_CLEARANCE_STEP_MM = 0.05

# The wide strip's (the word wide) cell 1 width, as modelled and on
# both pins, and the step from one cell to the next.
WIDE_FIRST_SLIT_WIDTH_MM = 0.5
WIDE_SLIT_WIDTH_STEP_MM = 0.1

# The pins as the strip prints them, in layout.CHOC_PIN_CENTERS_MM's
# order.
PIN_NAMES = ("peg-side pin", "middle pin")

# DESIGN.md's slit widths, cell 1 to cell 6, transcribed independently
# of the constants the slits are built from, as check_layout.py's
# DESIGN_* are, and each compared within half its last digit.
DESIGN_PEG_SIDE_SLIT_WIDTHS_MM = (0.25, 0.30, 0.35, 0.40, 0.45, 0.50)
DESIGN_MIDDLE_SLIT_WIDTHS_MM = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30)
DESIGN_FIGURE_DECIMALS = 2
# The wide strip's, the same on both pins. DESIGN.md gives them to one
# decimal, so the two decimals' tolerance above is the stricter.
DESIGN_WIDE_SLIT_WIDTHS_MM = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)

# The notches that number the cells, cut through the whole strip from
# its south edge.
NOTCH_WIDTH_MM = 1.0
NOTCH_DEPTH_MM = 0.8
NOTCH_PITCH_MM = 2.0

USAGE = f"""\
usage: freecadcmd model/kbdkid5/scripts/export_slit_test.py --pass <strip.stl> [wide]
           [pull_in={pcb_shape.DEFAULT_PULL_IN_MM}]

  wide       the wide strip: both slits of cell 1 {WIDE_FIRST_SLIT_WIDTH_MM} wide as modelled,
             each next cell's {WIDE_SLIT_WIDTH_STEP_MM} wider
  pull_in    swelling allowance per side, mm: the footprint holes grow outward
             by this much, and the slit length follows it\
"""


class Arguments:
    def __init__(self):
        self.stl_file = None
        self.wide = False
        self.pull_in = pcb_shape.DEFAULT_PULL_IN_MM


def parse_arguments(argument_list):
    arguments = Arguments()
    positionals = []
    for argument in argument_list:
        if argument == "wide":
            arguments.wide = True
        elif "=" in argument:
            key, _, value = argument.partition("=")
            if key != "pull_in":
                raise SystemExit(f"error: unknown option '{key}'\n{USAGE}")
            try:
                arguments.pull_in = float(value)
            except ValueError:
                raise SystemExit(f"error: '{key}' needs a number, got '{value}'")
        else:
            positionals.append(argument)
    if len(positionals) != 1:
        raise SystemExit(USAGE)
    arguments.stl_file = positionals[0]
    return arguments


def cell_key_center(index):
    """The key center of cell index (from 0) in the strip's frame."""
    half_pitch = layout.KEY_PITCH_MM / 2.0
    return (half_pitch + index * layout.KEY_PITCH_MM, half_pitch)


def cell_slit_clearance(index):
    return FIRST_SLIT_CLEARANCE_MM + index * SLIT_CLEARANCE_STEP_MM


def cell_wide_slit_width(index):
    return WIDE_FIRST_SLIT_WIDTH_MM + index * WIDE_SLIT_WIDTH_STEP_MM


def cell_slit_widths(index, wide):
    """Cell index's slit widths, in layout.CHOC_PIN_CENTERS_MM's order:
    each pin's calipered blade thickness plus the cell's clearance, or
    for the wide strip the cell's width on both pins."""
    if wide:
        return (cell_wide_slit_width(index),) * len(layout.CHOC_PIN_CENTERS_MM)
    clearance = cell_slit_clearance(index)
    return tuple(
        thickness + clearance for thickness in layout.CHOC_PIN_CALIPERED_BLADE_THICKNESSES_MM
    )


def strip_holes_and_slits(pull_in, wide):
    """(holes, slits per cell): the footprint holes of every cell and
    each cell's two slits."""
    holes = [
        hole
        for index in range(CELL_COUNT)
        for hole in layout.footprint_holes_without_pin_holes(cell_key_center(index))
    ]
    slit_length = layout.default_slit_length(pull_in)
    slits = [
        layout.pin_slits_of_widths(
            cell_key_center(index), slit_length, cell_slit_widths(index, wide)
        )
        for index in range(CELL_COUNT)
    ]
    return holes, slits


def build_pcb_layer(pull_in, holes, slits):
    """The PCB layer, a box of the cells less the holes and slits,
    checked against its analytic volume."""
    thickness = layout.PCB_THICKNESS_MM
    length = CELL_COUNT * layout.KEY_PITCH_MM
    box = Part.makeBox(length, layout.KEY_PITCH_MM, thickness)
    cutters = [
        pcb_shape.hole_cutter(center, diameter, pull_in, thickness) for center, diameter in holes
    ]
    cutters.extend(pcb_shape.slit_cutter(slit, thickness) for slit in slits)
    layer = box.cut(Part.makeCompound(cutters))
    area = length * layout.KEY_PITCH_MM - sum(
        math.pi * (diameter / 2.0 + pull_in) ** 2 for _center, diameter in holes
    ) - sum(layout.polygon_signed_area(slit) for slit in slits)
    expected = area * thickness
    if not layer.isValid() or len(layer.Solids) != 1:
        raise SystemExit("error: cutting the holes broke the PCB layer")
    if abs(layer.Volume - expected) > pcb_shape.VOLUME_RELATIVE_TOLERANCE * expected:
        raise SystemExit(
            f"error: PCB layer volume {layer.Volume:.4f} mm3, analytic {expected:.4f} mm3"
        )
    return layer.Solids[0], expected


def notch_x_centers(index):
    """The x centers of cell index's possible notches, west to east."""
    key_x, _ = cell_key_center(index)
    middle = (CELL_COUNT + 1) / 2.0
    return [key_x + (number - middle) * NOTCH_PITCH_MM for number in range(1, CELL_COUNT + 1)]


def notch_cutters(height):
    """Cell k (from 1) gets its first k notches."""
    cutters = []
    for index in range(CELL_COUNT):
        for x in notch_x_centers(index)[: index + 1]:
            cutter = Part.makeBox(
                NOTCH_WIDTH_MM,
                NOTCH_DEPTH_MM + pcb_shape.CUT_EXTRA_MM,
                height + 2.0 * pcb_shape.CUT_EXTRA_MM,
            )
            extra = pcb_shape.CUT_EXTRA_MM
            cutter.translate(App.Vector(x - NOTCH_WIDTH_MM / 2.0, -extra, -extra))
            cutters.append(cutter)
    return cutters


def cut_notches(strip):
    """The strip with the cells' notches, checked by volume and by
    probing every place a notch could be."""
    height = strip.BoundBox.ZLength
    cutters = notch_cutters(height)
    notched = strip.cut(Part.makeCompound(cutters))
    if not notched.isValid() or len(notched.Solids) != 1:
        raise SystemExit("error: cutting the notches broke the strip")
    removed = strip.Volume - notched.Volume
    expected = len(cutters) * NOTCH_WIDTH_MM * NOTCH_DEPTH_MM * height
    if abs(removed - expected) > pcb_shape.VOLUME_RELATIVE_TOLERANCE * strip.Volume:
        raise SystemExit(f"error: the notches took {removed:.4f} mm3, expected {expected:.4f}")
    solid = notched.Solids[0]
    for index in range(CELL_COUNT):
        for number, x in enumerate(notch_x_centers(index), start=1):
            point = App.Vector(x, NOTCH_DEPTH_MM / 2.0, height / 2.0)
            if solid.isInside(point, 1e-6, True) != (number > index + 1):
                raise SystemExit(f"error: cell {index + 1} has the wrong notches")
    return solid, len(cutters)


def design_slit_widths(index, wide):
    """DESIGN.md's slit widths of cell index, in PIN_NAMES' order."""
    if wide:
        return (DESIGN_WIDE_SLIT_WIDTHS_MM[index],) * len(PIN_NAMES)
    return (DESIGN_PEG_SIDE_SLIT_WIDTHS_MM[index], DESIGN_MIDDLE_SLIT_WIDTHS_MM[index])


def design_figure_tolerance():
    return 0.5 * 10.0**-DESIGN_FIGURE_DECIMALS + pcb_shape.SLIT_SIZE_TOLERANCE_MM


def check_cell_slit_widths(index, cell_measured, wide):
    """Cell index's slits as measured, (offset, x length, y length)
    each, against DESIGN.md's widths. The footprint is turned 90
    degrees, so across a blade is along board y."""
    design_widths = design_slit_widths(index, wide)
    for name, (_, _, y_length), width in zip(PIN_NAMES, cell_measured, design_widths):
        if abs(y_length - width) > design_figure_tolerance():
            raise SystemExit(
                f"error: cell {index + 1}'s {name} slit is {y_length:.4f} wide, DESIGN.md says "
                f"{width:.2f}"
            )


def cell_step_label(index, wide):
    """What sets cell index's slits: its width or its clearance."""
    if wide:
        return f"width {cell_wide_slit_width(index):.2f} on both pins"
    return f"clearance {cell_slit_clearance(index):+.2f}"


def print_cell(index, cell_measured, wide):
    notches = "1 notch" if index == 0 else f"{index + 1} notches"
    design_widths = design_slit_widths(index, wide)
    widths = ", ".join(
        f"{y_length:.3f} ({name}, DESIGN.md {width:.2f})"
        for name, (_, _, y_length), width in zip(PIN_NAMES, cell_measured, design_widths)
    )
    lengths = {round(x_length, 4) for _, x_length, _ in cell_measured}
    worst = max(offset for offset, _, _ in cell_measured)
    print(f"cell {index + 1}:     {notches}, {cell_step_label(index, wide)}, slits "
          f"{widths} wide, {', '.join(f'{length:.3f}' for length in sorted(lengths))} long, "
          f"worst offset {worst:.4f} mm")


def main():
    arguments = parse_arguments(script_arguments(sys.argv))
    holes, slits_per_cell = strip_holes_and_slits(arguments.pull_in, arguments.wide)
    slits = [slit for cell_slits in slits_per_cell for slit in cell_slits]
    pcb_layer, pcb_expected = build_pcb_layer(arguments.pull_in, holes, slits)
    print(f"cells:      {CELL_COUNT} at {layout.KEY_PITCH_MM} pitch, each a PCB layer "
          f"{layout.PCB_THICKNESS_MM} with {len(holes) // CELL_COUNT} footprint holes grown by "
          f"{arguments.pull_in} and 2 slits, no plate")
    blades = ", ".join(
        f"{thickness} ({name})"
        for name, thickness in zip(PIN_NAMES, layout.CHOC_PIN_CALIPERED_BLADE_THICKNESSES_MM)
    )
    sizing = "the cell's width" if arguments.wide else "its blade plus the cell's clearance"
    print(f"blades:     calipered {blades} thick (the model's "
          f"{layout.CHOC_PIN_BLADE_THICKNESS_MM}), each slit {sizing}")
    print(f"pcb layer:  volume {pcb_layer.Volume:.3f} mm3 (analytic {pcb_expected:.3f} mm3)")
    strip, notch_count = cut_notches(pcb_layer)
    print(f"notches:    {notch_count}, {NOTCH_WIDTH_MM} wide and {NOTCH_DEPTH_MM} deep, volume "
          f"{strip.Volume:.3f} mm3")
    measured = pcb_shape.measured_slits(strip, slits)
    for index in range(CELL_COUNT):
        cell_measured = measured[2 * index : 2 * index + 2]
        check_cell_slit_widths(index, cell_measured, arguments.wide)
        print_cell(index, cell_measured, arguments.wide)
    mesh = export_stl(strip, arguments.stl_file)
    check_closed_mesh(arguments.stl_file)
    box = strip.BoundBox
    print(f"print:      underside on z = 0, {box.XLength:.2f} x {box.YLength:.2f} x "
          f"{box.ZLength:.2f} mm")
    print(f"wrote:      {arguments.stl_file} ({mesh.CountFacets} facets), one closed "
          "manifold shell")


run_and_exit(main)
