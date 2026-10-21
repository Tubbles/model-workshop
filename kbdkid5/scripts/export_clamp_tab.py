"""Export the nice!nano screw clamp's tab (STL), a print of its own
(work item 009).

tray_shape.py's build_clamp_tab() builds the tab from layout.py: a
plate on the clamp's block reaching onto the board's south end, a nose
under that end that bears on the board beside the clamp's foot, and
the M2 screw's hole through the plate. The tab is symmetric about the
board's center line, so one tab serves both halves, and its shape is
the same whatever the clamp presses, since the block's top sets the
press, so the nice!nano test bay takes it too.

This script measures the tab against DESIGN.md's figures, which it
transcribes itself (the DESIGN_* constants below), turns it over, so
it prints top face down with the nose standing up and nothing to
support, and writes it as one closed mesh, its top face on z = 0.

Runs headless under FreeCAD's console interpreter (see
freecad_common.py for the freecadcmd quirks that shape the
invocation):

    freecadcmd kbdkid5/scripts/export_clamp_tab.py --pass <tab.stl>
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App
import Part

from freecad_common import check_closed_mesh, export_stl, run_and_exit, script_arguments
from tray_shape import UP, build_clamp_tab

# DESIGN.md's figures, transcribed independently of layout.py, each
# compared within half its last digit.
DESIGN_TAB_WIDTH_MM = 5.8  # along x
DESIGN_TAB_LENGTH_MM = 10.9  # along y, from the block's south face to 1.5 onto the board
DESIGN_TAB_THICKNESS_MM = 1.0  # the plate, as modelled
DESIGN_NOSE_LENGTH_MM = 1.0  # along y, at the tab's north end
DESIGN_NOSE_DEPTH_MM = 2.1  # below the plate's underside
DESIGN_HOLE_MM = 2.8  # 2.4 as printed
DESIGN_HOLE_FROM_SOUTH_END_MM = 2.9  # its axis from the tab's south end

# How far a measuring line reaches either side of its point.
PROBE_REACH_MM = 20.0
AXES = {"x": App.Vector(1, 0, 0), "y": App.Vector(0, 1, 0), "z": UP}

USAGE = """\
usage: freecadcmd kbdkid5/scripts/export_clamp_tab.py --pass <tab.stl>"""


def run_through(shape, point, axis, material=True):
    """(low, high) along the axis of the material (or, with material
    False, the empty) stretch through point."""
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


def measure(tab):
    """The tab's figures, as modelled, in the layout's frame: the plate,
    the nose at its north end and the hole."""
    box = tab.BoundBox
    plate_bottom = box.ZMax - DESIGN_TAB_THICKNESS_MM
    in_plate = App.Vector(box.XMin + 0.5, box.YMin + 0.5, (plate_bottom + box.ZMax) / 2.0)
    thick = run_through(tab, in_plate, "z")
    wide = run_through(tab, in_plate, "x")
    along = run_through(tab, in_plate, "y")
    in_nose = App.Vector(box.XMin + 0.5, box.YMax - 0.5, plate_bottom - 0.5)
    nose_along = run_through(tab, in_nose, "y")
    nose_down = run_through(tab, in_nose, "z")
    hole_middle = App.Vector(middle((box.XMin, box.XMax)), box.YMin + DESIGN_HOLE_FROM_SOUTH_END_MM,
                             in_plate.z)
    hole_across = run_through(tab, hole_middle, "x", material=False)
    hole_along = run_through(tab, hole_middle, "y", material=False)
    problems = []
    texts = [
        check(problems, "plate thick", length(thick), DESIGN_TAB_THICKNESS_MM, 1),
        check(problems, "wide", length(wide), DESIGN_TAB_WIDTH_MM, 1),
        check(problems, "long", length(along), DESIGN_TAB_LENGTH_MM, 1),
        check(problems, "nose along y", length(nose_along), DESIGN_NOSE_LENGTH_MM, 1),
        check(problems, "at the north end", box.YMax - nose_along[1], 0.0, 2),
        check(problems, "below the plate", plate_bottom - nose_down[0], DESIGN_NOSE_DEPTH_MM, 1),
        check(problems, "hole across", length(hole_across), DESIGN_HOLE_MM, 1),
        check(problems, "along", length(hole_along), DESIGN_HOLE_MM, 1),
        check(problems, "its axis from the south end", middle(hole_along) - box.YMin,
              DESIGN_HOLE_FROM_SOUTH_END_MM, 2),
        check(problems, "off the middle", middle(hole_across) - middle((box.XMin, box.XMax)),
              0.0, 2),
    ]
    if problems:
        raise SystemExit("error: off DESIGN.md's figures:\n  " + "\n  ".join(problems))
    return ", ".join(texts)


def turned_for_printing(tab):
    """The tab turned over about a line along y, its top face on z = 0
    and its bounding box's corner on x = y = 0, checked to lie on the bed
    over its whole plate."""
    turned = tab.copy()
    box = tab.BoundBox
    turned.rotate(App.Vector(middle((box.XMin, box.XMax)), 0.0, middle((box.ZMin, box.ZMax))),
                  App.Vector(0.0, 1.0, 0.0), 180.0)
    turned_box = turned.BoundBox
    turned.translate(App.Vector(-turned_box.XMin, -turned_box.YMin, -turned_box.ZMin))
    bed_area = sum(
        face.Area for face in turned.Faces
        if isinstance(face.Surface, Part.Plane) and abs(face.BoundBox.ZMax) < 1e-6
    )
    plate_area = sum(
        face.Area for face in tab.Faces
        if isinstance(face.Surface, Part.Plane) and abs(face.BoundBox.ZMin - box.ZMax) < 1e-6
    )
    if abs(bed_area - plate_area) > 1e-6 or plate_area <= 0.0:
        raise SystemExit(f"error: the turned tab lies {bed_area:.4f} mm2 on the bed, its top "
                         f"face is {plate_area:.4f} mm2")
    return turned, bed_area


def main():
    arguments = script_arguments(sys.argv)
    if len(arguments) != 1 or "=" in arguments[0]:
        raise SystemExit(USAGE)
    stl_file = arguments[0]
    tab = build_clamp_tab()
    print(f"tab:        one valid solid, volume {tab.Volume:.3f} mm3")
    print(f"measured:   {measure(tab)}")
    turned, bed_area = turned_for_printing(tab)
    mesh = export_stl(turned, stl_file)
    check_closed_mesh(stl_file)
    box = mesh.BoundBox
    print(f"print:      top face down, {bed_area:.3f} mm2 on the bed, the nose standing up, no "
          f"support, {box.XLength:.2f} x {box.YLength:.2f} x {box.ZLength:.2f} mm")
    print(f"wrote:      {stl_file} ({mesh.CountFacets} facets), one closed manifold shell; print "
          "one per half and one for the nice!nano test bay")


run_and_exit(main)
