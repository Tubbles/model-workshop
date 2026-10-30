"""Export the switch pusher (STL), a tool printed on its own (work item
039): it pushes a Kailh Choc v1 switch up out of the hand-wired frame
from below, the backing off, the sockets in their pockets and the plate
on, past the plate's grip, so the switch lifts out by hand.

The pusher is a frame cell, a KEY_PITCH_MM square BASE_THICKNESS_MM
thick centered on the switch's post, with a raise on its top under the
post and under each side peg and a hole through it under each of the
switch's two pins, at the frame's footprint holes as frame_shape.py
places them. The raises push the switch by the plate's thickness as
printed (push()): then all of the switch under its flange stands above
the plate, so its clips are free whatever their shape. They stand that
push, plus the depth from the post's and pegs' ends to the frame
bosses' ends, the deepest part under the frame, plus
BASE_UNDER_BOSSES_MM, all as printed (raise_height()), all three alike
so the post and pegs end level, and at the full push the base stays
that far under the bosses' ends. For the last part of the push the
raises go up into the frame's post and peg holes, so each passes its
hole at the slip fit, both as printed (raise_diameter()). The post's
raise has a cone dimple centered in its top, the pegs' are flat. A
switch's footprint is the same on both halves (DESIGN.md, Frame and
units), so one pusher serves both.

This script builds the pusher, measures it against DESIGN.md's figures,
which it transcribes itself (the DESIGN_* constants below), prints its
figures, and fails where a raise as printed does not pass its hole as
printed at the slip fit or where the base at the full push comes within
BASE_UNDER_BOSSES_MM of the bosses' ends. It writes the pusher as one
closed mesh as it prints, base down on z = 0, the raises up, nothing to
support.

Runs headless under FreeCAD's console interpreter (see
freecad_common.py for the freecadcmd quirks that shape the
invocation):

    freecadcmd model/kbdkid5/scripts/export_switch_pusher.py --pass <pusher.stl>
"""

import math
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App
import Part

import frame_shape
import layout
import pcb_shape
import socket_test_shape as cells
from freecad_common import check_closed_mesh, export_stl, run_and_exit, script_arguments
from tray_shape import CUT_EXTRA_MM, UP, require_one_valid_solid

# The base, as thick as the user asked, built with its south west
# corner on the origin and its bottom on z = 0, the key's center over
# its middle.
BASE_THICKNESS_MM = 3.0
KEY_CENTER_MM = (layout.KEY_PITCH_MM / 2.0, layout.KEY_PITCH_MM / 2.0)
# How far under the frame bosses' ends the base stays at the full push,
# as printed.
BASE_UNDER_BOSSES_MM = 0.5
# The cone dimple centered in the post's raise's top, for alignment.
# The pegs' raises are flat, the user: "I think the pegs are too small
# for a dimple to print correctly".
DIMPLE_DIAMETER_MM = 1.5
DIMPLE_DEPTH_MM = 0.4
# The raises, under the first cells.SWITCH_PROTRUDING_HOLE_COUNT of
# layout.CHOC_FOOTPRINT_HOLES_MM, in its order, the footprint turned 90
# degrees.
RAISE_NAMES = ("post", "west peg", "east peg")

# DESIGN.md's figures, transcribed independently of the constants above
# and layout.py, each compared within half its last digit.
DESIGN_BASE_SIDE_MM = 19.05
DESIGN_BASE_THICKNESS_MM = 3.0
DESIGN_PUSH_MM = 2.25
DESIGN_RAISE_HEIGHT_MM = 3.667
DESIGN_RAISE_DIAMETERS_MM = (2.62, 1.10, 1.10)  # as modelled, in RAISE_NAMES' order
DESIGN_DIMPLE_MM = (1.5, 0.4)  # across, deep
DESIGN_PIN_HOLE_DIAMETER_MM = 3.2

# How far a measuring line reaches either side of its point, and how
# much a measured figure may miss a bound the export holds it to.
PROBE_REACH_MM = 20.0
MEASURE_TOLERANCE_MM = 1e-6
AXES = {"x": App.Vector(1, 0, 0), "y": App.Vector(0, 1, 0), "z": UP}

USAGE = """\
usage: freecadcmd model/kbdkid5/scripts/export_switch_pusher.py --pass <pusher.stl>"""


# The figures, from layout.py and the frame's holes.


def push():
    """How far the raises push the switch up: the plate's thickness as
    printed, its underside the print's top face."""
    return layout.PLATE_THICKNESS_MM + layout.PRINT_RISE_OF_TOP_FACES_MM


def post_ends_depth():
    """How far the switch's post and pegs reach below the frame's top
    face, the switch's housing on it: layout.SWITCH_POSTS_BELOW_PCB_MM
    past a body as thick as a PCB. The top face prints on the bed, as
    modelled."""
    return layout.PCB_THICKNESS_MM + layout.SWITCH_POSTS_BELOW_PCB_MM


def ceiling_depth():
    """The frame's underside below its top face as printed: the print's
    top face, which rises."""
    return layout.PCB_THICKNESS_MM + layout.PRINT_RISE_OF_TOP_FACES_MM


def boss_ends_depth():
    """The frame bosses' ends, the deepest part under the frame, below
    its top face as printed: layout.boss_end_depth() under the ceiling,
    which they rise with."""
    return ceiling_depth() + layout.boss_end_depth()


def raise_height():
    """The raises over the base's top: the push, plus the depth from the
    post's and pegs' ends to the bosses' ends, plus
    BASE_UNDER_BOSSES_MM. The base's top and the raises' tops face up as
    printed and rise together, so the raises print as tall as
    modelled."""
    return push() + boss_ends_depth() - post_ends_depth() + BASE_UNDER_BOSSES_MM


def raise_diameter(hole_diameter):
    """A raise as modelled under the frame's hole hole_diameter across as
    modelled: the hole as printed, by the shrink the frame's post and
    peg holes were sized by (cells.printed_switch_hole_diameter()), less
    the slip fit, less the raise's own swelling on both sides."""
    printed_hole = cells.printed_switch_hole_diameter(hole_diameter)
    return printed_hole - layout.SLIP_FIT_MM - 2.0 * layout.PRINT_SWELLING_PER_SIDE_MM


def printed_raise_diameter(modelled):
    return modelled + 2.0 * layout.PRINT_SWELLING_PER_SIDE_MM


def frame_holes():
    """{footprint-local center: (center, diameter as modelled)} of the
    frame's footprint holes at the pusher's key, as frame_shape.py cuts
    them, the NC pad's left out."""
    local_centers = [local_center for local_center, _ in layout.CHOC_FOOTPRINT_HOLES_MM
                     if local_center != layout.CHOC_FOOTPRINT_NC_PAD_HOLE_CENTER_MM]
    return {
        local_center: (center, 2.0 * radius)
        for local_center, (center, radius)
        in zip(local_centers, frame_shape.key_holes(KEY_CENTER_MM), strict=True)
    }


def raise_holes():
    """(center, diameter as modelled) of the frame's holes over the
    raises, in RAISE_NAMES' order."""
    holes = frame_holes()
    return [holes[local_center] for local_center, _
            in layout.CHOC_FOOTPRINT_HOLES_MM[:cells.SWITCH_PROTRUDING_HOLE_COUNT]]


def pin_holes():
    """(center, diameter) of the base's holes under the switch's pins:
    the frame's blade holes'."""
    holes = frame_holes()
    return [holes[local_center] for local_center in layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM]


# Building.


def analytic_volume():
    base = layout.KEY_PITCH_MM**2 * BASE_THICKNESS_MM
    pins = sum(math.pi * (diameter / 2.0) ** 2 for _, diameter in pin_holes()) * BASE_THICKNESS_MM
    raises = sum(math.pi * (raise_diameter(diameter) / 2.0) ** 2
                 for _, diameter in raise_holes()) * raise_height()
    dimple = math.pi * (DIMPLE_DIAMETER_MM / 2.0) ** 2 * DIMPLE_DEPTH_MM / 3.0
    return base - pins + raises - dimple


def dimple_cutter(center, top):
    """The cone, its apex DIMPLE_DEPTH_MM under the post's raise's top and
    DIMPLE_DIAMETER_MM across there, running on CUT_EXTRA_MM above it at
    the same slope for a clean cut."""
    widening = DIMPLE_DIAMETER_MM / 2.0 / DIMPLE_DEPTH_MM
    height = DIMPLE_DEPTH_MM + CUT_EXTRA_MM
    return Part.makeCone(0.0, widening * height, height,
                         App.Vector(center[0], center[1], top - DIMPLE_DEPTH_MM), UP)


def build_pusher():
    """The pusher, checked to be one valid solid of its analytic volume.
    The raises reach CUT_EXTRA_MM down into the base for a clean fuse."""
    top = BASE_THICKNESS_MM + raise_height()
    root = BASE_THICKNESS_MM - CUT_EXTRA_MM
    base = Part.makeBox(layout.KEY_PITCH_MM, layout.KEY_PITCH_MM, BASE_THICKNESS_MM)
    raises = [Part.makeCylinder(raise_diameter(diameter) / 2.0, top - root,
                                App.Vector(center[0], center[1], root), UP)
              for center, diameter in raise_holes()]
    cutters = [pcb_shape.hole_cutter(center, diameter, 0.0, BASE_THICKNESS_MM)
               for center, diameter in pin_holes()]
    post_center, _ = raise_holes()[0]
    cutters.append(dimple_cutter(post_center, top))
    pusher = base.fuse(raises).cut(Part.makeCompound(cutters)).removeSplitter()
    require_one_valid_solid(pusher, "building the switch pusher")
    expected = analytic_volume()
    if abs(pusher.Volume - expected) > pcb_shape.VOLUME_RELATIVE_TOLERANCE * expected:
        raise SystemExit(f"error: the pusher's volume is {pusher.Volume:.4f} mm3, analytic "
                         f"{expected:.4f} mm3")
    return pusher.Solids[0]


# Measuring.


@dataclass
class MeasuredRaise:
    """A raise as measured on the pusher, as modelled."""

    name: str
    hole_diameter: float  # the frame's hole over it, as modelled
    diameter: float
    off_center: float  # its axis from the hole's, in plan
    height: float  # over the base's top


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


def across(shape, point, material=True):
    """(diameter, its center's distance from point in plan) of the round
    material or hole at point, measured along x and along y."""
    along_x = run_through(shape, point, "x", material)
    along_y = run_through(shape, point, "y", material)
    off_center = math.hypot(middle(along_x) - point.x, middle(along_y) - point.y)
    return min(length(along_x), length(along_y)), off_center


def measure_base(pusher, problems):
    """(base's top z, text): the base measured near its north east
    corner, clear of the raises and the pin holes."""
    in_base = App.Vector(layout.KEY_PITCH_MM - 1.0, layout.KEY_PITCH_MM - 1.0,
                         BASE_THICKNESS_MM / 2.0)
    thick = run_through(pusher, in_base, "z")
    texts = [
        check(problems, "along x", length(run_through(pusher, in_base, "x")),
              DESIGN_BASE_SIDE_MM, 2),
        check(problems, "along y", length(run_through(pusher, in_base, "y")),
              DESIGN_BASE_SIDE_MM, 2),
        check(problems, "thick", length(thick), DESIGN_BASE_THICKNESS_MM, 1),
    ]
    return thick[1], ", ".join(texts)


def measure_raises(pusher, base_top, problems):
    """([MeasuredRaise], text), in RAISE_NAMES' order: each raise
    measured across at half its height and down through its top, the
    post's on its rim between the dimple and its side."""
    raises, texts = [], []
    for name, (center, hole_diameter), stated in zip(RAISE_NAMES, raise_holes(),
                                                     DESIGN_RAISE_DIAMETERS_MM, strict=True):
        at_half_height = App.Vector(center[0], center[1], base_top + raise_height() / 2.0)
        diameter, off_center = across(pusher, at_half_height)
        dimpled = name == RAISE_NAMES[0]
        rim = (DIMPLE_DIAMETER_MM / 2.0 + diameter / 2.0) / 2.0 if dimpled else 0.0
        in_base = App.Vector(center[0] + rim, center[1], base_top / 2.0)
        height = run_through(pusher, in_base, "z")[1] - base_top
        raises.append(MeasuredRaise(name, hole_diameter, diameter, off_center, height))
        texts.append(", ".join([
            check(problems, f"{name} across", diameter, stated, 2),
            check(problems, "tall", height, DESIGN_RAISE_HEIGHT_MM, 3),
            check(problems, "off its hole's axis", off_center, 0.0, 3),
        ]))
    return raises, "; ".join(texts)


def measure_dimple(pusher, rim_top, problems):
    """The dimple's text: across at its rim and deep, from how wide it is
    a quarter and a half of its depth down, since a cone's width falls
    evenly to its apex."""
    post_center, _ = raise_holes()[0]
    depths = (DIMPLE_DEPTH_MM / 4.0, DIMPLE_DEPTH_MM / 2.0)
    widths = [across(pusher, App.Vector(post_center[0], post_center[1], rim_top - depth),
                     material=False)
              for depth in depths]
    narrowing = (widths[0][0] - widths[1][0]) / (depths[1] - depths[0])  # per mm down
    rim_width = widths[0][0] + narrowing * depths[0]
    texts = [
        check(problems, "across", rim_width, DESIGN_DIMPLE_MM[0], 1),
        check(problems, "deep", rim_width / narrowing, DESIGN_DIMPLE_MM[1], 1),
        check(problems, "off the post's axis", max(off for _, off in widths), 0.0, 3),
    ]
    return ", ".join(texts)


def measure_pin_holes(pusher, problems):
    texts = []
    for center, _ in pin_holes():
        diameter, off_center = across(
            pusher, App.Vector(center[0], center[1], BASE_THICKNESS_MM / 2.0), material=False)
        texts.append(", ".join([
            check(problems, "across", diameter, DESIGN_PIN_HOLE_DIAMETER_MM, 1),
            check(problems, "off the blade hole's axis", off_center, 0.0, 3),
        ]))
    return "; ".join(texts)


# The checks the pusher is built for.


def hole_fit_text(raises, problems):
    """Each raise as printed in its hole as printed, failing below the
    slip fit: the clearance across, less twice the raise's axis's
    distance from the hole's."""
    texts = []
    for measured in raises:
        printed = printed_raise_diameter(measured.diameter)
        printed_hole = cells.printed_switch_hole_diameter(measured.hole_diameter)
        clearance = printed_hole - printed - 2.0 * measured.off_center
        text = (f"{measured.name} {printed:.3f} in its {measured.hole_diameter:.2f} hole's "
                f"{printed_hole:.3f}, {clearance:.3f} clearance")
        if clearance < layout.SLIP_FIT_MM - MEASURE_TOLERANCE_MM:
            problems.append(f"{text}, less than the slip fit's {layout.SLIP_FIT_MM}")
        texts.append(text)
    return "; ".join(texts)


def full_push_text(raises, problems):
    """Where the raises' tops and the base stand at the full push, taking
    the shortest raise's height, failing where the base comes within
    BASE_UNDER_BOSSES_MM of the bosses' ends."""
    raise_tops_depth = post_ends_depth() - push()
    base_depth = raise_tops_depth + min(measured.height for measured in raises)
    under_bosses = base_depth - boss_ends_depth()
    text = (f"the raises' tops {raise_tops_depth:.3f} under the frame's top face, "
            f"{ceiling_depth() - raise_tops_depth:.3f} up into their holes, the base "
            f"{under_bosses:.3f} under the bosses' ends")
    if under_bosses < BASE_UNDER_BOSSES_MM - MEASURE_TOLERANCE_MM:
        problems.append(f"{text}, less than {BASE_UNDER_BOSSES_MM}")
    return text


def main():
    arguments = script_arguments(sys.argv)
    if len(arguments) != 1 or "=" in arguments[0]:
        raise SystemExit(USAGE)
    stl_file = arguments[0]
    pusher = build_pusher()
    print(f"pusher:     one valid solid, volume {pusher.Volume:.3f} mm3")
    problems = []
    base_top, base_text = measure_base(pusher, problems)
    print(f"base:       {base_text}")
    raises, raise_text = measure_raises(pusher, base_top, problems)
    print(f"raises:     {raise_text}, as modelled")
    rim_top = base_top + raises[0].height
    print(f"dimple:     {measure_dimple(pusher, rim_top, problems)}")
    print(f"pin holes:  {measure_pin_holes(pusher, problems)}")
    push_text = check(problems, "the switch up by", push(), DESIGN_PUSH_MM, 2)
    print(f"push:       {push_text}, the plate's {layout.PLATE_THICKNESS_MM} as printed; under "
          f"the frame's top face as printed the post's and pegs' ends stand "
          f"{post_ends_depth():.3f}, the bosses' ends {boss_ends_depth():.3f}, "
          f"{boss_ends_depth() - post_ends_depth():.3f} deeper")
    print(f"in holes:   as printed, {hole_fit_text(raises, problems)}")
    print(f"full push:  {full_push_text(raises, problems)}")
    if problems:
        raise SystemExit("error: off DESIGN.md's figures or the pusher's rules:\n  "
                         + "\n  ".join(problems))
    mesh = export_stl(pusher, stl_file)
    check_closed_mesh(stl_file)
    box = mesh.BoundBox
    print(f"print:      base down, the raises up, no support, {box.XLength:.2f} x "
          f"{box.YLength:.2f} x {box.ZLength:.2f} mm")
    print(f"wrote:      {stl_file} ({mesh.CountFacets} facets), one closed manifold shell; one "
          "serves both halves")


run_and_exit(main)
