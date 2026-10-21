"""Export the fused mock (STL): the PCB mock and the switch plate printed
as one part, to mount switches in for a feel of the layout.

The PCB layer is the PCB mock (pcb_shape.py, z 9.5 to 11.1 in the
layout's frame) with each key's two pin holes replaced by slits that
grip the switch's pin blades, the way a hotswap socket's contacts do:
slit_width across the blade, slit_length along it. pull_in sets their
defaults but does not grow a given slit_width or slit_length. By
default the width is the model's blade thickness plus pull_in per
side, meant as a nominal zero clearance once the print swells as
expected. The user's print of the first slit test strip showed it
does not grip, and it stays until the second strip
(export_slit_test.py) has been tried. The length is the blade's width
plus pull_in per side plus layout.SLIT_LENGTH_CLEARANCE_MM, so only
the width grips. Every other hole is the mock's, grown by pull_in.

The plate on it is plate_shape.py's (z 11.1 to 13.3), plain, with its
side shave but no pattern shift: kbdkid4's shift corrects its printed
plates against its fabricated board, and here the plate and the PCB
layer are one print, so a shift would only move each cutout off the
holes beneath it. Its head holes stay as counterbores over the
mounting drills, so the screw heads sit on the PCB layer as in the
real build.

The part prints PCB side down, since plate side down the PCB layer
would bridge over every switch cutout. The plate's 1.0 step inside
each cutout then becomes a lip overhanging by 0.15 (0.4 at the
cutout's south notch). Around the perimeter the plate also reaches
past the PCB layer below it, since the PCB layer's outline is pulled
in and the plate's is not: a lip of 0.118 to 0.197 along the straight
outer edges and 0.45 along the slant, kept as it is. So the STL has the
PCB's underside on z = 0.

The word "right" makes the right half: the outline, the plate and the
drills mirrored across the layout's right-half mirror line, each key's
footprint holes and slits the left half's at the mirrored key center
(a switch cannot be mirrored, see layout.py), so real switches seat in
it as in the left one.

Runs headless under FreeCAD's console interpreter (see
freecad_common.py for the freecadcmd quirks that shape the
invocation):

    freecadcmd model/kbdkid5/scripts/export_mock.py --pass <mock.stl> [right] [key=value ...]

It checks for one valid solid with both layers' volume, every plate
cutout centered on its key's center hole, every slit centered on its
pin at its size, and a closed mesh.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App

import layout
import pcb_shape
from freecad_common import check_closed_mesh, export_stl, run_and_exit, script_arguments
from plate_shape import build_plate

USAGE = f"""\
usage: freecadcmd model/kbdkid5/scripts/export_mock.py --pass <mock.stl> [right]
           [pull_in={pcb_shape.DEFAULT_PULL_IN_MM}] [slit_width=...] [slit_length=...]

  right        export the right half: outline, plate and drills mirrored across
               x = {layout.RIGHT_HALF_MIRROR_X_MM:.3f}, the switch footprints the left
               half's at the mirrored key centers
  pull_in      swelling allowance per side, mm: the PCB layer's outline moves
               inward and its holes grow outward by this much; it sets the
               slits' defaults but does not grow a given slit size
  slit_width   the pin slits across the blade, mm (default the model blade's
               {layout.CHOC_PIN_BLADE_THICKNESS_MM} plus pull_in per side)
  slit_length  the pin slits along the blade, mm (default the blade's
               {layout.CHOC_PIN_BLADE_WIDTH_MM} plus pull_in per side, plus
               {layout.SLIT_LENGTH_CLEARANCE_MM} so only the width grips)\
"""

NUMBER_OPTIONS = ("pull_in", "slit_width", "slit_length")


class Arguments:
    def __init__(self):
        self.stl_file = None
        self.pull_in = pcb_shape.DEFAULT_PULL_IN_MM
        self.slit_width = None  # the default follows pull_in
        self.slit_length = None
        self.right = False


def parse_arguments(argument_list):
    arguments = Arguments()
    positionals = []
    for argument in argument_list:
        if argument == "right":
            arguments.right = True
        elif "=" in argument:
            key, _, value = argument.partition("=")
            if key not in NUMBER_OPTIONS:
                raise SystemExit(f"error: unknown option '{key}'\n{USAGE}")
            try:
                setattr(arguments, key, float(value))
            except ValueError:
                raise SystemExit(f"error: '{key}' needs a number, got '{value}'")
        else:
            positionals.append(argument)
    if len(positionals) != 1:
        raise SystemExit(USAGE)
    arguments.stl_file = positionals[0]
    if arguments.slit_width is None:
        arguments.slit_width = layout.default_slit_width(arguments.pull_in)
    if arguments.slit_length is None:
        arguments.slit_length = layout.default_slit_length(arguments.pull_in)
    return arguments


def mirror_across_half_line(shape):
    return shape.mirror(
        App.Vector(layout.RIGHT_HALF_MIRROR_X_MM, 0.0, 0.0), App.Vector(1.0, 0.0, 0.0)
    )


def build_pcb_layer(arguments):
    """(layer, its analytic volume, holes, slits): the PCB mock with
    slits, on the exported half, at the PCB's height in the layout's
    frame."""
    key_holes, slits = pcb_shape.key_holes_and_slits(
        pcb_shape.half_key_centers(arguments.right).values(),
        arguments.slit_length,
        arguments.slit_width,
    )
    holes = key_holes + pcb_shape.half_drills(arguments.right)
    outline = pcb_shape.half_outline(arguments.right)
    layer, expected_volume = pcb_shape.build_mock(
        arguments.pull_in, layout.PCB_THICKNESS_MM, outline, holes, slits
    )
    layer.translate(App.Vector(0.0, 0.0, layout.PCB_UNDERSIDE_Z_MM))
    return layer, expected_volume, holes, slits


def build_plate_layer(right):
    """(layer, the build): the plain plate without the pattern shift, on
    the exported half."""
    build = build_plate(covered=False, pattern_shift=0.0)
    layer = mirror_across_half_line(build.solid) if right else build.solid
    return layer, build


def print_layers(arguments, pcb_layer, pcb_expected, holes, slits, plate_build):
    print(f"layout:     {len(layout.KEY_CENTERS_MM)} keys, "
          f"{len(layout.MOUNTING_DRILL_CENTERS_MM)} mounting drills, PCB layer "
          f"{layout.PCB_THICKNESS_MM} (z {layout.PCB_UNDERSIDE_Z_MM} to {layout.PCB_TOP_Z_MM}) "
          f"under the plate {layout.PLATE_THICKNESS_MM} (to z {layout.PLATE_TOP_Z_MM})")
    print(f"blades:     {layout.CHOC_PIN_BLADE_THICKNESS_MM} x {layout.CHOC_PIN_BLADE_WIDTH_MM} mm "
          f"(kbdkid4's switch model) to {layout.CHOC_PIN_FULL_WIDTH_DEPTH_MM} below the housing, "
          f"tips {layout.CHOC_PIN_LENGTH_MM - layout.PCB_THICKNESS_MM:.2f} below the PCB layer, "
          f"slits {arguments.slit_width:.2f} across x {arguments.slit_length:.2f} along the "
          "blade, not grown by pull_in")
    print(f"pcb layer:  outline pulled in {arguments.pull_in}, {len(holes)} holes grown by "
          f"{arguments.pull_in}, {len(slits)} slits, volume {pcb_layer.Volume:.3f} mm3 "
          f"(analytic {pcb_expected:.3f} mm3)")
    print(f"plate:      plain, pattern shift {plate_build.pattern_shift:+.2f}, side shave "
          f"{plate_build.side_shave:.2f}, {len(plate_build.hole_supports)} head holes "
          f"{plate_build.hole_diameter:.2f} as counterbores, volume "
          f"{plate_build.solid.Volume:.3f} mm3")


def main():
    arguments = parse_arguments(script_arguments(sys.argv))
    pcb_layer, pcb_expected, holes, slits = build_pcb_layer(arguments)
    plate_layer, plate_build = build_plate_layer(arguments.right)
    print_layers(arguments, pcb_layer, pcb_expected, holes, slits, plate_build)
    mock = pcb_shape.fuse_layers(pcb_layer, plate_layer)
    print(f"fused:      one solid, volume {mock.Volume:.3f} mm3 (layers "
          f"{pcb_layer.Volume + plate_layer.Volume:.3f} mm3)")
    cutout_count, cutout_worst = pcb_shape.check_cutouts_on_center_holes(
        mock, pcb_shape.half_key_centers(arguments.right).values(), arguments.pull_in
    )
    print(f"cutouts:    {cutout_count} plate cutouts, each on its key's center hole, worst "
          f"offset {cutout_worst:.4f} mm")
    measured = pcb_shape.measured_slits(mock, slits)
    sizes = sorted({(round(x_length, 4), round(y_length, 4)) for _, x_length, y_length in measured})
    size_text = ", ".join(f"{x_length:.3f} x {y_length:.3f}" for x_length, y_length in sizes)
    print(f"slits:      {len(measured)} slits, each on its pin, worst offset "
          f"{max(offset for offset, _, _ in measured):.4f} mm, {size_text} mm along x by y")
    half = "left"
    if arguments.right:
        half = (f"right, outline, plate and drills mirrored across x = "
                f"{layout.RIGHT_HALF_MIRROR_X_MM:.3f}, switch footprints the left half's at "
                "the mirrored key centers")
    print(f"half:       {half}")

    mock.translate(App.Vector(0.0, 0.0, -layout.PCB_UNDERSIDE_Z_MM))
    mesh = export_stl(mock, arguments.stl_file)
    check_closed_mesh(arguments.stl_file)
    box = mock.BoundBox
    print(f"print:      PCB side down, its underside on z = 0, {box.XLength:.2f} x "
          f"{box.YLength:.2f} x {box.ZLength:.2f} mm (x {box.XMin:.3f} to {box.XMax:.3f})")
    print(f"wrote:      {arguments.stl_file} ({mesh.CountFacets} facets), one closed "
          "manifold shell")


run_and_exit(main)
