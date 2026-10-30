"""Export the 3D-printable coffee block (STL).

A plain block that raises a large container under the coffee machine's
spout while it is descaled. The user, 2026-10-30: "a simple rectangle
block of 4x6x12 cm".

Runs headless under FreeCAD's console interpreter (see board_step.py
for the freecadcmd quirks that shape the invocation):

    freecadcmd model/coffee-block/scripts/export_coffee_block.py --pass <block.stl>

The block lies the way it prints, on one of its two largest faces on
z = 0: the lowest print, and the steadiest on the bed.
"""

import os
import sys

# The STL export and the freecadcmd scaffolding live in kbdkid4's board_step.py.
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, "kbdkid4", "scripts"))

import Part

from board_step import check_closed_mesh, export_stl, run_and_exit, script_arguments

# The block's sides, largest last; it prints on the face of the two largest.
BLOCK_SIDES_MM = (40.0, 60.0, 120.0)

VOLUME_TOLERANCE = 1e-9  # relative

USAGE = """\
usage: freecadcmd model/coffee-block/scripts/export_coffee_block.py --pass <block.stl>\
"""


def build_block():
    """The block lying on its largest face: the longest side along x,
    the middle one along y, the shortest up."""
    height, width, length = BLOCK_SIDES_MM
    return Part.makeBox(length, width, height)


def check_block(block):
    expected = BLOCK_SIDES_MM[0] * BLOCK_SIDES_MM[1] * BLOCK_SIDES_MM[2]
    if len(block.Solids) != 1 or not block.isValid():
        raise SystemExit(f"error: the block is {len(block.Solids)} solids or not valid")
    if abs(block.Volume - expected) > VOLUME_TOLERANCE * expected:
        raise SystemExit(f"error: the block is {block.Volume:.1f} mm3, expected {expected:.1f} mm3")


def main():
    arguments = script_arguments(sys.argv)
    if len(arguments) != 1:
        raise SystemExit(USAGE)
    stl_file = arguments[0]
    block = build_block()
    check_block(block)
    mesh = export_stl(block, stl_file)
    check_closed_mesh(stl_file)

    box = block.BoundBox
    print(f"block:  {box.XLength:.1f} x {box.YLength:.1f} mm on the bed, {box.ZLength:.1f} mm high, "
          f"{block.Volume / 1000.0:.0f} cm3")
    print(f"wrote:  {stl_file} ({mesh.CountFacets} facets)")


run_and_exit(main)
