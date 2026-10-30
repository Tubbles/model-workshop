"""Export the socket pusher (STL), a tool printed on its own (work item
041): it pushes a Kailh Choc v1 hotswap socket down out of its pocket in
the hand-wired frame from above, the key's switch out (by the switch
pusher, export_switch_pusher.py), the backing off and the plate on, the
frame held with room under the key and the socket hanging on its wires.

The pusher is the switch pusher's base, a KEY_PITCH_MM square
BASE_THICKNESS_MM thick centered on the key's center, with a pin under
it at each of the frame's two pin holes
(layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM), where the socket's two
contact bosses sit. Pressed down through the plate's cutout and the
frame's pin holes onto the contact bosses' tops, the pins push the
socket down until the base's underside rests on the plate's top, which
is the stop. The push is the pocket walls' depth plus
SOCKET_UNDER_MOUTH_MM, so the socket's top ends that far under the
walls' mouth (push()), and the pins are the plate's thickness, plus the
depth from the frame's top face to the contact bosses' tops, plus the
push, all as printed (pin_length()). Each pin passes its frame hole at
the slip fit, both as printed (pin_diameter()). The middle pin, over
the footprint's hole south of the key's center, would reach past the
plate's top layer cutout, so it is flattened on its south side to keep
PLATE_CLEARANCE_MM from that edge as printed (flat_from_axis()), since
the plate's place over the frame is not exact. A key's footprint seen
from above is the same on both halves (DESIGN.md, Frame and units), so
one pusher serves both.

This script builds the pusher as it is used, base up and pins down in
the key's frame, measures it against DESIGN.md's figures, which it
transcribes itself (the DESIGN_* constants below), prints its figures,
and fails where a pin as printed does not pass its frame hole as
printed at the slip fit, comes within PLATE_CLEARANCE_MM of either
layer of the plate's cutout as printed, or leaves the socket's top less
than SOCKET_UNDER_MOUTH_MM under the walls' mouth at the full push. It
writes the pusher turned over, as it prints, as one closed mesh, base
down on z = 0, the pins up, nothing to support. Turned back over to be
used, its pins stand over the frame's pin holes.

Runs headless under FreeCAD's console interpreter (see
freecad_common.py for the freecadcmd quirks that shape the
invocation):

    freecadcmd model/kbdkid5/scripts/export_socket_pusher.py --pass <pusher.stl>
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

# The base, the switch pusher's, built as used: its south west corner on
# the origin, its underside, which rests on the plate's top at the full
# push, on z = 0, the key's center under its middle and the pins hanging
# below it.
BASE_THICKNESS_MM = 3.0
KEY_CENTER_MM = (layout.KEY_PITCH_MM / 2.0, layout.KEY_PITCH_MM / 2.0)
# The socket's two contact bosses, 2.90 across in the frame's pin holes,
# reach this far over its bottom on Kailh's drawing (doc/components.md,
# section 7).
CONTACT_BOSSES_REACH_MM = 3.05
# How far under the pocket walls' mouth the socket's top ends at the
# full push, as printed.
SOCKET_UNDER_MOUTH_MM = 0.5
# How near the pins may come to the plate's cutouts as printed, since
# the plate's place over the frame is not exact.
PLATE_CLEARANCE_MM = 0.2
# The pins, at layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM in its order:
# the one by the west peg, and the middle one, south of the key's
# center, the footprint turned 90 degrees.
PIN_NAMES = ("peg side pin", "middle pin")
# The plate's layers, each cutout a square centered on the key's
# center, the top layer's the narrower. The lower layer's notch only
# widens its square, so the square alone is checked.
PLATE_LAYERS = (
    ("top layer", layout.PLATE_TOP_LAYER_CUTOUT_MM),
    ("lower layer", layout.PLATE_LOWER_LAYER_CUTOUT_MM),
)

# DESIGN.md's figures, transcribed independently of the constants above
# and layout.py, each compared within half its last digit.
DESIGN_BASE_SIDE_MM = 19.05
DESIGN_BASE_THICKNESS_MM = 3.0
DESIGN_PUSH_MM = 2.30
DESIGN_PIN_LENGTH_MM = 4.95
DESIGN_PIN_DIAMETER_MM = 2.40  # as modelled
DESIGN_FLAT_FROM_AXIS_MM = 0.50  # the middle pin's, as modelled

# How far a measuring line reaches either side of its point, and how
# much a measured figure may miss a bound the export holds it to.
PROBE_REACH_MM = 20.0
MEASURE_TOLERANCE_MM = 1e-6
AXES = {"x": App.Vector(1, 0, 0), "y": App.Vector(0, 1, 0), "z": UP}

USAGE = """\
usage: freecadcmd model/kbdkid5/scripts/export_socket_pusher.py --pass <pusher.stl>"""


# The figures, from layout.py and the frame's holes.


def plate_thickness():
    """The plate's thickness as printed, its underside the print's top
    face: how far its top stands over the frame's top face, which prints
    true on the bed."""
    return layout.PLATE_THICKNESS_MM + layout.PRINT_RISE_OF_TOP_FACES_MM


def ceiling_depth():
    """The frame's underside below its top face as printed: the print's
    top face, which rises."""
    return layout.PCB_THICKNESS_MM + layout.PRINT_RISE_OF_TOP_FACES_MM


def mouth_depth():
    """The pocket walls' mouth below the frame's top face as printed:
    the walls' depth under the ceiling, which their mouth rises with."""
    return ceiling_depth() + cells.wall_depth()


def contact_boss_height():
    """The socket's contact bosses over its top, the bumps on it that
    rest against the ceiling."""
    return CONTACT_BOSSES_REACH_MM - layout.HOTSWAP_SOCKET_BODY_HEIGHT_MM


def contact_bosses_depth():
    """The contact bosses' tops below the frame's top face as printed,
    the socket's top against the ceiling."""
    return ceiling_depth() - contact_boss_height()


def push():
    """How far the pins push the socket down: the pocket walls' depth
    plus SOCKET_UNDER_MOUTH_MM. The ceiling and the walls' mouth face up
    as printed and rise together, so the walls are as deep as
    modelled."""
    return cells.wall_depth() + SOCKET_UNDER_MOUTH_MM


def pin_length():
    """The pins under the base: the plate's thickness, plus the depth
    from the frame's top face to the contact bosses' tops, plus the
    push, all as printed. The base's underside and the pins' ends face
    up as printed and rise together, so the pins print as long as
    modelled."""
    return plate_thickness() + contact_bosses_depth() + push()


def pin_diameter(hole_diameter):
    """A pin as modelled in the frame's hole hole_diameter across as
    modelled: the hole as printed, by the hole strip's measurement of
    holes this size (cells.printed_switch_hole_diameter()), less the
    slip fit, less the pin's own swelling on both sides."""
    printed_hole = cells.printed_switch_hole_diameter(hole_diameter)
    return printed_hole - layout.SLIP_FIT_MM - 2.0 * layout.PRINT_SWELLING_PER_SIDE_MM


def printed_reach(modelled):
    """A pin's side as printed, modelled from its axis."""
    return modelled + layout.PRINT_SWELLING_PER_SIDE_MM


def cutout_half_as_printed(cutout):
    """How far a plate cutout cutout across stands from the key's center
    on each side as printed: an opening this wide prints the print
    model's swelling per side smaller (doc/print-model.md)."""
    return cutout / 2.0 - layout.PRINT_SWELLING_PER_SIDE_MM


def flat_from_axis(center, diameter):
    """How far south of its axis the pin at center, diameter across as
    modelled, is flattened as modelled, or None where the round pin as
    printed keeps PLATE_CLEARANCE_MM from the plate's top layer cutout's
    south edge as printed. The flat as printed, swollen, keeps that
    clearance. Only the middle pin comes that near, and only to the
    south edge. plate_text() holds every pin to every edge of both
    layers."""
    room = (cutout_half_as_printed(layout.PLATE_TOP_LAYER_CUTOUT_MM) - PLATE_CLEARANCE_MM
            - (KEY_CENTER_MM[1] - center[1]))
    if printed_reach(diameter / 2.0) <= room:
        return None
    return room - layout.PRINT_SWELLING_PER_SIDE_MM


def pin_holes():
    """(center, diameter as modelled) of the frame's pin holes at the
    pusher's key, as frame_shape.py cuts them, in PIN_NAMES' order."""
    local_centers = [local_center for local_center, _ in layout.CHOC_FOOTPRINT_HOLES_MM
                     if local_center != layout.CHOC_FOOTPRINT_NC_PAD_HOLE_CENTER_MM]
    holes = {
        local_center: (center, 2.0 * radius)
        for local_center, (center, radius)
        in zip(local_centers, frame_shape.key_holes(KEY_CENTER_MM), strict=True)
    }
    return [holes[local_center] for local_center in layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM]


# Building.


def pin_section_area(diameter, flat):
    """A pin's cross section: its circle, less the segment south of its
    flat."""
    radius = diameter / 2.0
    circle = math.pi * radius**2
    if flat is None:
        return circle
    segment = radius**2 * math.acos(flat / radius) - flat * math.sqrt(radius**2 - flat**2)
    return circle - segment


def analytic_volume():
    base = layout.KEY_PITCH_MM**2 * BASE_THICKNESS_MM
    sections = 0.0
    for center, hole_diameter in pin_holes():
        diameter = pin_diameter(hole_diameter)
        sections += pin_section_area(diameter, flat_from_axis(center, diameter))
    return base + sections * pin_length()


def build_pin(center, diameter):
    """A pin pin_length() under the base's underside, reaching
    CUT_EXTRA_MM up into the base for a clean fuse, flattened where
    flat_from_axis() says."""
    radius = diameter / 2.0
    pin = Part.makeCylinder(radius, pin_length() + CUT_EXTRA_MM,
                            App.Vector(center[0], center[1], -pin_length()), UP)
    flat = flat_from_axis(center, diameter)
    if flat is None:
        return pin
    reach = radius + CUT_EXTRA_MM
    cutter = Part.makeBox(2.0 * reach, reach - flat, pin_length() + 3.0 * CUT_EXTRA_MM,
                          App.Vector(center[0] - reach, center[1] - reach,
                                     -pin_length() - CUT_EXTRA_MM))
    return pin.cut(cutter)


def build_pusher():
    """The pusher as used, checked to be one valid solid of its analytic
    volume."""
    base = Part.makeBox(layout.KEY_PITCH_MM, layout.KEY_PITCH_MM, BASE_THICKNESS_MM)
    pins = [build_pin(center, pin_diameter(hole_diameter))
            for center, hole_diameter in pin_holes()]
    pusher = base.fuse(pins).removeSplitter()
    require_one_valid_solid(pusher, "building the socket pusher")
    expected = analytic_volume()
    if abs(pusher.Volume - expected) > pcb_shape.VOLUME_RELATIVE_TOLERANCE * expected:
        raise SystemExit(f"error: the pusher's volume is {pusher.Volume:.4f} mm3, analytic "
                         f"{expected:.4f} mm3")
    return pusher.Solids[0]


def turned_for_printing(pusher):
    """The pusher upside down, base down on z = 0 and the pins up, at
    the same x and its y turned about the base's middle."""
    turned = pusher.copy()
    turned.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 180.0)
    turned.translate(App.Vector(0.0, layout.KEY_PITCH_MM, BASE_THICKNESS_MM))
    return turned


# Measuring.


@dataclass
class MeasuredPin:
    """A pin as measured on the pusher as used, as modelled, along x and
    y through its hole's axis halfway down it."""

    name: str
    center: tuple  # its frame hole's axis, in plan
    hole_diameter: float  # the frame's hole it passes, as modelled
    along_x: tuple  # its west and east ends
    along_y: tuple  # its south and north ends
    length: float  # under the base's underside


def run_through(shape, point, axis):
    """(low, high) along the axis of the material stretch through point,
    as export_switch_pusher.py measures (importing it would run it)."""
    direction = AXES[axis]
    start = point.sub(direction * PROBE_REACH_MM)
    edge = Part.LineSegment(start, start.add(direction * (2.0 * PROBE_REACH_MM))).toShape()
    origin = point.dot(direction)
    pieces = sorted(
        (min(ends), max(ends))
        for ends in ([vertex.Point.dot(direction) for vertex in piece.Vertexes]
                     for piece in shape.common(edge).Edges)
    )
    for low, high in pieces:
        if low <= origin <= high:
            return low, high
    raise SystemExit(f"error: no plastic at {point} to measure")


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


def measure_base(pusher, problems):
    """(base's underside z, text): the base measured near its north east
    corner, clear of the pins."""
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
    return thick[0], ", ".join(texts)


def measure_pins(pusher, base_bottom, problems):
    """([MeasuredPin], text), in PIN_NAMES' order: each pin across along
    x, along y or, if flattened, its flat south of its axis, its axis
    off its hole's (along y from its round north side) and its length."""
    pins, texts = [], []
    for name, (center, hole_diameter) in zip(PIN_NAMES, pin_holes(), strict=True):
        halfway = App.Vector(center[0], center[1], base_bottom - pin_length() / 2.0)
        along_x = run_through(pusher, halfway, "x")
        along_y = run_through(pusher, halfway, "y")
        pin_end = run_through(pusher, halfway, "z")[0]
        pin = MeasuredPin(name, center, hole_diameter, along_x, along_y, base_bottom - pin_end)
        pins.append(pin)
        across = length(along_x)
        off_center = math.hypot(middle(along_x) - center[0], along_y[1] - center[1] - across / 2.0)
        if flat_from_axis(center, pin_diameter(hole_diameter)) is None:
            shape_text = check(problems, "along y", length(along_y), DESIGN_PIN_DIAMETER_MM, 2)
        else:
            shape_text = (check(problems, "its flat south of its axis", center[1] - along_y[0],
                                DESIGN_FLAT_FROM_AXIS_MM, 2)
                          + f", {KEY_CENTER_MM[1] - along_y[0]:.3f} south of the key's center")
        texts.append(", ".join([
            check(problems, f"{name} across along x", across, DESIGN_PIN_DIAMETER_MM, 2),
            shape_text,
            check(problems, "off its hole's axis", off_center, 0.0, 3),
            check(problems, "long", pin.length, DESIGN_PIN_LENGTH_MM, 2),
        ]))
    return pins, "; ".join(texts)


# The checks the pusher is built for.


def farthest_reach(pin):
    """How far the pin reaches from its hole's axis in plan, as
    modelled: the farthest of its four ends along x and y."""
    x, y = pin.center
    return max(pin.along_x[1] - x, x - pin.along_x[0], pin.along_y[1] - y, y - pin.along_y[0])


def hole_fit_text(pins, problems):
    """Each pin as printed in its frame hole as printed, failing below
    the slip fit: the hole less twice the pin's farthest reach from the
    hole's axis."""
    texts = []
    for pin in pins:
        printed = 2.0 * printed_reach(farthest_reach(pin))
        printed_hole = cells.printed_switch_hole_diameter(pin.hole_diameter)
        clearance = printed_hole - printed
        text = (f"{pin.name} {printed:.3f} in its {pin.hole_diameter:.2f} hole's "
                f"{printed_hole:.3f}, {clearance:.3f} clearance")
        if clearance < layout.SLIP_FIT_MM - MEASURE_TOLERANCE_MM:
            problems.append(f"{text}, less than the slip fit's {layout.SLIP_FIT_MM}")
        texts.append(text)
    return "; ".join(texts)


def plate_clearance(pin, cutout):
    """How far the pin as printed stays inside a plate cutout cutout
    across as printed: the nearest of the square's four edges to the
    pin's ends along x and y, which are its farthest points that way."""
    half = cutout_half_as_printed(cutout)
    x, y = KEY_CENTER_MM
    room = min(x + half - pin.along_x[1], pin.along_x[0] - (x - half),
               y + half - pin.along_y[1], pin.along_y[0] - (y - half))
    return room - layout.PRINT_SWELLING_PER_SIDE_MM


def plate_text(pins, problems):
    """Each pin's clearance as printed to each layer's cutout as
    printed, failing below PLATE_CLEARANCE_MM."""
    texts = []
    for pin in pins:
        layer_texts = []
        for layer, cutout in PLATE_LAYERS:
            clearance = plate_clearance(pin, cutout)
            text = f"{clearance:.3f} from the {layer}'s {cutout} cutout"
            if clearance < PLATE_CLEARANCE_MM - MEASURE_TOLERANCE_MM:
                problems.append(f"{pin.name} {text}, less than {PLATE_CLEARANCE_MM}")
            layer_texts.append(text)
        texts.append(f"{pin.name} " + " and ".join(layer_texts))
    return "; ".join(texts)


def full_push_text(pins, problems):
    """Where the contact bosses' tops and the socket's top stand at the
    full push, the base on the plate, taking the shortest pin, failing
    where the socket's top ends less than SOCKET_UNDER_MOUTH_MM under
    the walls' mouth."""
    bosses_depth = min(pin.length for pin in pins) - plate_thickness()
    under_mouth = bosses_depth + contact_boss_height() - mouth_depth()
    text = (f"the contact bosses' tops {bosses_depth:.3f} under the frame's top face, "
            f"{bosses_depth - ceiling_depth():.3f} under the ceiling, the socket's top "
            f"{under_mouth:.3f} under the walls' mouth, which stands {mouth_depth():.3f} under "
            "the top face")
    if under_mouth < SOCKET_UNDER_MOUTH_MM - MEASURE_TOLERANCE_MM:
        problems.append(f"{text}, less than {SOCKET_UNDER_MOUTH_MM}")
    return text


def main():
    arguments = script_arguments(sys.argv)
    if len(arguments) != 1 or "=" in arguments[0]:
        raise SystemExit(USAGE)
    stl_file = arguments[0]
    pusher = build_pusher()
    print(f"pusher:     one valid solid, volume {pusher.Volume:.3f} mm3")
    problems = []
    base_bottom, base_text = measure_base(pusher, problems)
    print(f"base:       {base_text}")
    pins, pin_text = measure_pins(pusher, base_bottom, problems)
    print(f"pins:       {pin_text}, as modelled")
    push_text = check(problems, "the socket down by", push(), DESIGN_PUSH_MM, 2)
    print(f"push:       {push_text}, the pocket walls' {cells.wall_depth():.2f} depth plus "
          f"{SOCKET_UNDER_MOUTH_MM}")
    print(f"length:     {pin_length():.3f}: the plate's {plate_thickness():.3f}, plus "
          f"{contact_bosses_depth():.3f} from the frame's top face down to the contact bosses' "
          f"tops (the ceiling {ceiling_depth():.3f} down, the bosses "
          f"{contact_boss_height():.2f} over the socket's top against it), plus the push, all "
          "as printed")
    print(f"in holes:   as printed, {hole_fit_text(pins, problems)}")
    print(f"plate:      as printed, {plate_text(pins, problems)}")
    print(f"full push:  {full_push_text(pins, problems)}")
    if problems:
        raise SystemExit("error: off DESIGN.md's figures or the pusher's rules:\n  "
                         + "\n  ".join(problems))
    mesh = export_stl(turned_for_printing(pusher), stl_file)
    check_closed_mesh(stl_file)
    box = mesh.BoundBox
    print(f"print:      base down, the pins up, no support, {box.XLength:.2f} x "
          f"{box.YLength:.2f} x {box.ZLength:.2f} mm")
    print(f"wrote:      {stl_file} ({mesh.CountFacets} facets), one closed manifold shell; one "
          "serves both halves")


run_and_exit(main)
