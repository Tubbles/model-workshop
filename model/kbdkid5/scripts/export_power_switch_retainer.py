"""Export the power switch's retainer (STL), a print of its own (work
item 013).

tray_shape.py's build_power_switch_retainer() builds the retainer from
layout.py: a plate that drops into its socket behind the power switch
once the switch is slid in, knob first, its two legs beside the
switch's leads and the bar over them. It is the same on both halves,
one per half.

This script measures the retainer against DESIGN.md's figures, which it
transcribes itself (the DESIGN_* constants below), lays it flat, the
face that bears on the switch on the bed, so nothing needs support, and
writes it as one closed mesh, that face on z = 0.

Runs headless under FreeCAD's console interpreter (see
freecad_common.py for the freecadcmd quirks that shape the
invocation):

    freecadcmd model/kbdkid5/scripts/export_power_switch_retainer.py --pass <retainer.stl>
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App
import Part

from freecad_common import check_closed_mesh, export_stl, run_and_exit, script_arguments
from tray_shape import UP, build_power_switch_retainer

# DESIGN.md's figures, transcribed independently of layout.py, each
# compared within half its last digit.
DESIGN_RETAINER_WIDTH_MM = 11.7  # along x
DESIGN_RETAINER_HEIGHT_MM = 6.8  # along z as fitted
DESIGN_RETAINER_THICKNESS_MM = 1.2  # along y as fitted
DESIGN_RETAINER_OPENING_MM = (8.1, 3.55)  # across, up from the lower edge

# How far a measuring line reaches either side of its point.
PROBE_REACH_MM = 20.0
AXES = {"x": App.Vector(1, 0, 0), "y": App.Vector(0, 1, 0), "z": UP}

USAGE = """\
usage: freecadcmd model/kbdkid5/scripts/export_power_switch_retainer.py --pass <retainer.stl>"""


def run_through(shape, point, axis, material=True):
    """(low, high) along the axis of the material (or, with material
    False, the empty) stretch through point, as export_clamp_tab.py
    measures (importing it would run it)."""
    direction = AXES[axis]
    start = point.sub(direction * PROBE_REACH_MM)
    edge = Part.LineSegment(start, start.add(direction * (2.0 * PROBE_REACH_MM))).toShape()
    origin = point.dot(direction)
    pieces = sorted(
        (min(ends), max(ends))
        for ends in ([vertex.Point.dot(direction) for vertex in piece.Vertexes]
                     for piece in shape.common(edge).Edges)
    )
    if material:
        for low, high in pieces:
            if low <= origin <= high:
                return low, high
        raise SystemExit(f"error: no plastic at {point} to measure")
    low, high = origin - PROBE_REACH_MM, origin + PROBE_REACH_MM
    for piece_low, piece_high in pieces:
        if piece_low <= origin <= piece_high:
            raise SystemExit(f"error: plastic at {point}, where a gap was measured")
        if piece_high < origin:
            low = max(low, piece_high)
        if piece_low > origin:
            high = min(high, piece_low)
    return low, high


def length(span):
    return span[1] - span[0]


def middle(span):
    return (span[0] + span[1]) / 2.0


def check(problems, label, measured, stated, decimals):
    tolerance = 0.5 * 10.0**-decimals + 1e-6
    shown = round(measured, decimals + 2) + 0.0  # no "-0.00"
    text = f"{label} {shown:.{decimals + 2}f} (DESIGN.md {stated})"
    if abs(measured - stated) > tolerance:
        problems.append(text)
    return text


def measure(retainer):
    """The retainer's figures, as modelled, as fitted in the layout's
    frame: the plate and the opening up from its lower edge."""
    box = retainer.BoundBox
    in_leg = App.Vector(box.XMin + 0.5, middle((box.YMin, box.YMax)), box.ZMin + 0.5)
    in_bar = App.Vector(middle((box.XMin, box.XMax)), in_leg.y, box.ZMax - 0.5)
    in_opening = App.Vector(in_bar.x, in_leg.y, box.ZMin + 0.5)
    opening_across = run_through(retainer, in_opening, "x", material=False)
    opening_up = run_through(retainer, in_opening, "z", material=False)
    problems = []
    texts = [
        check(problems, "wide", length(run_through(retainer, in_bar, "x")),
              DESIGN_RETAINER_WIDTH_MM, 1),
        check(problems, "tall", length(run_through(retainer, in_leg, "z")),
              DESIGN_RETAINER_HEIGHT_MM, 1),
        check(problems, "thick", length(run_through(retainer, in_bar, "y")),
              DESIGN_RETAINER_THICKNESS_MM, 1),
        check(problems, "opening across", length(opening_across), DESIGN_RETAINER_OPENING_MM[0],
              1),
        check(problems, "off the middle", middle(opening_across) - middle((box.XMin, box.XMax)),
              0.0, 2),
        check(problems, "up from the lower edge", opening_up[1] - box.ZMin,
              DESIGN_RETAINER_OPENING_MM[1], 2),
    ]
    if problems:
        raise SystemExit("error: off DESIGN.md's figures:\n  " + "\n  ".join(problems))
    return ", ".join(texts)


def laid_flat(retainer):
    """The retainer turned about a line along x so the face that bears on
    the switch, its north face as fitted, lies on z = 0, its bounding
    box's corner on x = y = 0, checked to lie on the bed with that whole
    face."""
    turned = retainer.copy()
    box = retainer.BoundBox
    turned.rotate(App.Vector(0.0, box.YMax, box.ZMin), App.Vector(1.0, 0.0, 0.0), -90.0)
    turned_box = turned.BoundBox
    turned.translate(App.Vector(-turned_box.XMin, -turned_box.YMin, -turned_box.ZMin))
    bed_area = sum(
        face.Area for face in turned.Faces
        if isinstance(face.Surface, Part.Plane) and abs(face.BoundBox.ZMax) < 1e-6
    )
    north_area = sum(
        face.Area for face in retainer.Faces
        if isinstance(face.Surface, Part.Plane) and abs(face.BoundBox.YMin - box.YMax) < 1e-6
    )
    if abs(bed_area - north_area) > 1e-6 or north_area <= 0.0:
        raise SystemExit(f"error: the laid retainer lies {bed_area:.4f} mm2 on the bed, its "
                         f"north face is {north_area:.4f} mm2")
    if abs(turned.BoundBox.ZLength - DESIGN_RETAINER_THICKNESS_MM) > 1e-6:
        raise SystemExit(f"error: the laid retainer stands {turned.BoundBox.ZLength:.4f} tall")
    return turned, bed_area


def main():
    arguments = script_arguments(sys.argv)
    if len(arguments) != 1 or "=" in arguments[0]:
        raise SystemExit(USAGE)
    stl_file = arguments[0]
    retainer = build_power_switch_retainer()
    print(f"retainer:   one valid solid, volume {retainer.Volume:.3f} mm3")
    print(f"measured:   {measure(retainer)}")
    turned, bed_area = laid_flat(retainer)
    mesh = export_stl(turned, stl_file)
    check_closed_mesh(stl_file)
    box = mesh.BoundBox
    print(f"print:      flat, the face on the switch down, {bed_area:.3f} mm2 on the bed, no "
          f"support, {box.XLength:.2f} x {box.YLength:.2f} x {box.ZLength:.2f} mm")
    print(f"wrote:      {stl_file} ({mesh.CountFacets} facets), one closed manifold shell; print "
          "one per half")


run_and_exit(main)
