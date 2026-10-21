"""Export a 3D-printable mock of the PCB (STL) from the layout.

kbdkid5 has no PCB design yet. Until it does, this printed stand-in
for the bare board test-fits the tray and the plate: the outline from
layout.py extruded to the PCB's thickness, with every key's Choc
hotswap footprint holes and the mounting drills, and nothing else (no
sockets), pulled in by pull_in so the print measures like the real
board. pcb_shape.py builds it (its docstring says how) and checks it.
To mount switches, print the fused mock (export_mock.py) instead.

Runs headless under FreeCAD's console interpreter (see
freecad_common.py for the freecadcmd quirks that shape the
invocation):

    freecadcmd kbdkid5/scripts/export_pcb.py --pass <mock.stl> [right] [pull_in=0.2]

The mock's x and y are the layout's, its bottom face on z = 0, while
in the layout's frame z = 0 is the tray floor's top (the PCB's
underside sits at z 9.5 there): a print lies on the bed. The word
"right" makes the right half like the fused mock's PCB layer: the
outline and the drills mirrored across the layout's right-half mirror
line, each key's footprint holes the left half's at the mirrored key
center, since a switch cannot be mirrored (see layout.py).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import layout
from freecad_common import check_closed_mesh, export_stl, run_and_exit, script_arguments
from pcb_shape import DEFAULT_PULL_IN_MM, all_holes, build_mock, half_outline

USAGE = f"""\
usage: freecadcmd kbdkid5/scripts/export_pcb.py --pass <mock.stl> [right] [pull_in={DEFAULT_PULL_IN_MM}]

  right      export the right half: outline and drills mirrored across the
             layout's right-half mirror line, x = {layout.RIGHT_HALF_MIRROR_X_MM:.3f},
             the switch footprints the left half's at the mirrored key centers
  pull_in    swelling allowance per side, mm: the outline moves inward and
             every hole grows outward by this much\
"""


class Arguments:
    def __init__(self):
        self.stl_file = None
        self.pull_in = DEFAULT_PULL_IN_MM
        self.right = False


def parse_arguments(argument_list):
    arguments = Arguments()
    positionals = []
    for argument in argument_list:
        if argument == "right":
            arguments.right = True
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


def hole_census():
    """{diameter: count} of the layout's holes."""
    counts = {}
    for _center, diameter in all_holes():
        counts[diameter] = counts.get(diameter, 0) + 1
    return counts


def main():
    arguments = parse_arguments(script_arguments(sys.argv))
    thickness = layout.PCB_THICKNESS_MM

    mock, expected_volume = build_mock(
        arguments.pull_in, thickness, half_outline(arguments.right), all_holes(arguments.right)
    )
    mesh = export_stl(mock, arguments.stl_file)
    check_closed_mesh(arguments.stl_file)

    outline = layout.OUTLINE_VERTICES_MM
    width = max(x for x, _ in outline) - min(x for x, _ in outline)
    height = max(y for _, y in outline) - min(y for _, y in outline)
    box = mock.BoundBox
    print(f"layout:     outline {width:.2f} x {height:.2f} mm, "
          f"{len(outline)} corners rounded {layout.OUTLINE_CORNER_RADIUS_MM} mm, "
          f"{len(layout.KEY_CENTERS_MM)} keys, {len(layout.MOUNTING_DRILL_CENTERS_MM)} "
          f"mounting drills, {thickness} mm thick")
    print(f"mock:       {box.XLength:.2f} x {box.YLength:.2f} x {box.ZLength:.2f} mm "
          f"(x {box.XMin:.3f} to {box.XMax:.3f}), pulled in {arguments.pull_in} mm per "
          f"side, volume {mock.Volume:.3f} mm3 (analytic {expected_volume:.3f} mm3)")
    for diameter, count in sorted(hole_census().items()):
        print(f"holes:      {count:3d} x {diameter:.2f} mm -> "
              f"{diameter + 2.0 * arguments.pull_in:.2f} mm")
    half = "left"
    if arguments.right:
        half = (f"right, outline and drills mirrored across x = "
                f"{layout.RIGHT_HALF_MIRROR_X_MM:.3f}, switch footprints the left half's at "
                "the mirrored key centers")
    print(f"half:       {half}")
    print(f"wrote:      {arguments.stl_file} ({mesh.CountFacets} facets), "
          "one closed manifold shell")


run_and_exit(main)
