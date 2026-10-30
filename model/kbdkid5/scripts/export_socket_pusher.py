"""Export the socket pusher (STL), a tool printed on its own (work items
041 and 042): it pushes a Kailh Choc v1 hotswap socket down out of its
pocket in the hand-wired frame from above, with nothing on the frame's
top side (the plate off and the key's switch out, by the switch pusher,
export_switch_pusher.py), the backing off, the frame held with room
under the key and the socket hanging on its wires.

The pusher is a KEY_PITCH_MM square base BASE_THICKNESS_MM thick with
three pins under it: a push pin at each of the frame's two pin holes
(layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM), where the socket's two
contact bosses sit, and a pilot pin at the switch's post hole in the
key's center, which finds its hole first. The base is centered on the
middle of the three pins' extent in plan (pins_extent_middle()).
Pressed down through the frame's pin holes onto the contact bosses'
tops, the push pins push the socket down until the base's underside
rests on the frame's top face, which is the stop. The push is the
pocket walls' depth, so the socket's top ends level with the walls'
mouth, out of the pocket (push()), and the push pins are the depth from
the frame's top face to the contact bosses' tops plus the push, both as
printed (pin_length()). The pilot is PILOT_LEAD_MM longer, with a
PILOT_CHAMFER_MM chamfer at 45 degrees round its tip (pilot_length()).
Each pin passes its frame hole at the slip fit, both as printed
(pin_diameter(), which sizes the pilot as the switch pusher sizes its
post raise). A pry slot in the base's top as used, the face on the bed
as printed, at the middle of its north edge takes a tool to pry the
pusher off the bed. A key's footprint seen from above is the same on
both halves (DESIGN.md, Frame and units), so one pusher serves both.

This script builds the pusher as it is used, base up and pins down in
the key's frame, measures it against DESIGN.md's figures, which it
transcribes itself (the DESIGN_* constants below), prints its figures,
and fails where a pin as printed does not pass its frame hole as
printed at the slip fit or where the push pins at the full push leave
the socket's top above the walls' mouth. It writes the pusher turned
over, as it prints, as one closed mesh, base down on z = 0, the pins
up, nothing to support, and fails where the slot does not open on the
bed. Turned back over to be used, its pins stand over the frame's
holes.

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

# The base, built as used: the key's cell's south west corner on the
# origin, the base's underside, which rests on the frame's top face at
# the full push, on z = 0, the base centered over the pins' extent and
# the pins hanging below it.
BASE_THICKNESS_MM = 3.0
KEY_CENTER_MM = (layout.KEY_PITCH_MM / 2.0, layout.KEY_PITCH_MM / 2.0)
# The pry slot in the base's top as used, the face on the bed as
# printed, at the middle of its north edge as used: a tool slid into it
# pries the pusher off the bed. Its roof prints as a SLOT_WIDTH_MM
# bridge. The user, 2026-10-30: "say 6 mm wide and 4 mm deep, and 1.5 mm
# high (half the base side height)" (work item 042).
SLOT_WIDTH_MM = 6.0  # along the edge
SLOT_DEPTH_MM = 4.0  # into the base
SLOT_HEIGHT_MM = 1.5
# The socket's two contact bosses, 2.90 across in the frame's pin holes,
# reach this far over its bottom on Kailh's drawing (doc/components.md,
# section 7).
CONTACT_BOSSES_REACH_MM = 3.05
# The pilot pin in the switch's post hole, the first of
# layout.CHOC_FOOTPRINT_HOLES_MM: this much longer than the push pins,
# so it is in its hole before they reach theirs, its tip chamfered this
# much at 45 degrees to find the hole (work item 042, the user: "add a
# pilot pin for the post hole for the socket pusher").
PILOT_LEAD_MM = 1.0
PILOT_CHAMFER_MM = 0.5
PILOT_NAME = "pilot pin"
# The push pins, at layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM in its
# order: the one by the west peg, and the middle one, south of the key's
# center, the footprint turned 90 degrees.
PIN_NAMES = ("peg side pin", "middle pin")

# DESIGN.md's figures, transcribed independently of the constants above
# and layout.py, each compared within half its last digit.
DESIGN_BASE_SIDE_MM = 19.05
DESIGN_BASE_THICKNESS_MM = 3.0
DESIGN_BASE_CENTER_MM = (-2.445, -2.920)  # from the key's center along x and y, as used
DESIGN_SLOT_MM = (6.0, 4.0, 1.5)  # across, deep, high, as modelled
DESIGN_PUSH_MM = 1.80
DESIGN_PIN_LENGTH_MM = 2.20
DESIGN_PIN_DIAMETER_MM = 2.40  # as modelled
DESIGN_PILOT_DIAMETER_MM = 2.62  # as modelled
DESIGN_PILOT_LENGTH_MM = 3.20
DESIGN_PILOT_LEAD_MM = 1.0
DESIGN_PILOT_CHAMFER_MM = 0.5
DESIGN_PILOT_CHAMFER_DEGREES = 45

# How far a measuring line reaches either side of its point, and how
# much a measured figure may miss a bound the export holds it to.
PROBE_REACH_MM = 20.0
MEASURE_TOLERANCE_MM = 1e-6
AXES = {"x": App.Vector(1, 0, 0), "y": App.Vector(0, 1, 0), "z": UP}

USAGE = """\
usage: freecadcmd model/kbdkid5/scripts/export_socket_pusher.py --pass <pusher.stl>"""


# The figures, from layout.py and the frame's holes.


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
    """How far the push pins push the socket down: the pocket walls'
    depth, which leaves the socket's top level with the walls' mouth.
    The ceiling and the walls' mouth face up as printed and rise
    together, so the walls are as deep as modelled."""
    return cells.wall_depth()


def pin_length():
    """The push pins under the base: the depth from the frame's top face
    to the contact bosses' tops, plus the push, both as printed. The
    base's underside and the pins' ends face up as printed and rise
    together, so the pins print as long as modelled."""
    return contact_bosses_depth() + push()


def pilot_length():
    """The pilot pin under the base: PILOT_LEAD_MM longer than the push
    pins."""
    return pin_length() + PILOT_LEAD_MM


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


def post_hole():
    """(center, diameter as modelled) of the frame's post hole at the
    pusher's key, the pilot's."""
    post_local_center, _ = layout.CHOC_FOOTPRINT_HOLES_MM[0]
    return frame_holes()[post_local_center]


def pin_holes():
    """(center, diameter as modelled) of the frame's pin holes at the
    pusher's key, the push pins', in PIN_NAMES' order."""
    holes = frame_holes()
    return [holes[local_center] for local_center in layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM]


def pins_extent_middle():
    """The middle of the three pins' extent in plan as modelled, their
    outlines at their feet, which the base is centered on."""
    outlines = [(center, pin_diameter(diameter) / 2.0)
                for center, diameter in [post_hole()] + pin_holes()]
    return tuple(
        (min(center[axis] - radius for center, radius in outlines)
         + max(center[axis] + radius for center, radius in outlines)) / 2.0
        for axis in (0, 1)
    )


# Building.


def pin_section_area(diameter):
    return math.pi * (diameter / 2.0) ** 2


def pilot_volume(diameter):
    """The pilot under the base: its shank and the frustum of its
    chamfered tip."""
    radius = diameter / 2.0
    tip_radius = radius - PILOT_CHAMFER_MM
    shank = pin_section_area(diameter) * (pilot_length() - PILOT_CHAMFER_MM)
    tip = math.pi * PILOT_CHAMFER_MM / 3.0 * (radius**2 + radius * tip_radius + tip_radius**2)
    return shank + tip


def analytic_volume():
    base = layout.KEY_PITCH_MM**2 * BASE_THICKNESS_MM
    slot = SLOT_WIDTH_MM * SLOT_DEPTH_MM * SLOT_HEIGHT_MM
    sections = sum(pin_section_area(pin_diameter(hole_diameter))
                   for _, hole_diameter in pin_holes())
    _, post_diameter = post_hole()
    return base - slot + sections * pin_length() + pilot_volume(pin_diameter(post_diameter))


def build_pin(center, diameter):
    """A push pin pin_length() under the base's underside, reaching
    CUT_EXTRA_MM up into the base for a clean fuse."""
    return Part.makeCylinder(diameter / 2.0, pin_length() + CUT_EXTRA_MM,
                             App.Vector(center[0], center[1], -pin_length()), UP)


def build_pilot(center, diameter):
    """The pilot, pilot_length() under the base's underside and reaching
    CUT_EXTRA_MM up into the base for a clean fuse: a shank, and under
    it its tip, a cone's frustum PILOT_CHAMFER_MM high that narrows by as
    much, 45 degrees."""
    radius = diameter / 2.0
    tip = -pilot_length()
    shank = Part.makeCylinder(radius, pilot_length() - PILOT_CHAMFER_MM + CUT_EXTRA_MM,
                              App.Vector(center[0], center[1], tip + PILOT_CHAMFER_MM), UP)
    chamfer = Part.makeCone(radius - PILOT_CHAMFER_MM, radius, PILOT_CHAMFER_MM,
                            App.Vector(center[0], center[1], tip), UP)
    return shank.fuse(chamfer)


def slot_cutter():
    """The pry slot, SLOT_WIDTH_MM along the base's north edge and
    centered on it, SLOT_DEPTH_MM into the base and SLOT_HEIGHT_MM down
    from its top, running on CUT_EXTRA_MM past the edge and the top for
    a clean cut."""
    x, y = pins_extent_middle()
    north_edge = y + layout.KEY_PITCH_MM / 2.0
    return Part.makeBox(SLOT_WIDTH_MM, SLOT_DEPTH_MM + CUT_EXTRA_MM, SLOT_HEIGHT_MM + CUT_EXTRA_MM,
                        App.Vector(x - SLOT_WIDTH_MM / 2.0, north_edge - SLOT_DEPTH_MM,
                                   BASE_THICKNESS_MM - SLOT_HEIGHT_MM))


def build_pusher():
    """The pusher as used, checked to be one valid solid of its analytic
    volume."""
    x, y = pins_extent_middle()
    half = layout.KEY_PITCH_MM / 2.0
    base = Part.makeBox(layout.KEY_PITCH_MM, layout.KEY_PITCH_MM, BASE_THICKNESS_MM,
                        App.Vector(x - half, y - half, 0.0))
    post_center, post_diameter = post_hole()
    pins = [build_pin(center, pin_diameter(hole_diameter))
            for center, hole_diameter in pin_holes()]
    pins.append(build_pilot(post_center, pin_diameter(post_diameter)))
    pusher = base.fuse(pins).cut(slot_cutter()).removeSplitter()
    require_one_valid_solid(pusher, "building the socket pusher")
    expected = analytic_volume()
    if abs(pusher.Volume - expected) > pcb_shape.VOLUME_RELATIVE_TOLERANCE * expected:
        raise SystemExit(f"error: the pusher's volume is {pusher.Volume:.4f} mm3, analytic "
                         f"{expected:.4f} mm3")
    return pusher.Solids[0]


def turned_for_printing(pusher):
    """The pusher upside down, base down on z = 0 and the pins up, at
    the same x and its y turned about the key's center, so the base's
    north edge as used becomes its south edge."""
    turned = pusher.copy()
    turned.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 180.0)
    turned.translate(App.Vector(0.0, layout.KEY_PITCH_MM, BASE_THICKNESS_MM))
    return turned


# Measuring.


@dataclass
class MeasuredBase:
    """The base as measured on the pusher as used, as modelled, through
    the middle of the pins' extent."""

    along_x: tuple  # its west and east edges
    along_y: tuple  # its south and north edges
    along_z: tuple  # its underside and top


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


def run_through(shape, point, axis, material=True):
    """(low, high) along the axis of the material (or, with material
    False, the empty) stretch through point, as export_switch_pusher.py
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


def measure_base(pusher, problems):
    """(MeasuredBase, text): the base measured through the middle of the
    pins' extent, clear of the pins, along x and y under the slot's
    floor, and its middle from the key's center and from the pins'
    extent's."""
    x, y = pins_extent_middle()
    through = App.Vector(x, y, (BASE_THICKNESS_MM - SLOT_HEIGHT_MM) / 2.0)
    base = MeasuredBase(*(run_through(pusher, through, axis) for axis in ("x", "y", "z")))
    base_middle = (middle(base.along_x), middle(base.along_y))
    texts = [
        check(problems, "along x", length(base.along_x), DESIGN_BASE_SIDE_MM, 2),
        check(problems, "along y", length(base.along_y), DESIGN_BASE_SIDE_MM, 2),
        check(problems, "thick", length(base.along_z), DESIGN_BASE_THICKNESS_MM, 1),
        check(problems, "its middle from the key's center along x",
              base_middle[0] - KEY_CENTER_MM[0], DESIGN_BASE_CENTER_MM[0], 3),
        check(problems, "along y", base_middle[1] - KEY_CENTER_MM[1], DESIGN_BASE_CENTER_MM[1], 3),
        check(problems, "off the middle of the pins' extent",
              math.hypot(base_middle[0] - x, base_middle[1] - y), 0.0, 3),
    ]
    return base, ", ".join(texts)


def measure_pin(pusher, base_bottom, name, hole, modelled_length):
    """A MeasuredPin: the pin in hole, modelled_length long, across along
    x and y halfway down it, and its length."""
    center, hole_diameter = hole
    halfway = App.Vector(center[0], center[1], base_bottom - modelled_length / 2.0)
    along_x = run_through(pusher, halfway, "x")
    along_y = run_through(pusher, halfway, "y")
    pin_end = run_through(pusher, halfway, "z")[0]
    return MeasuredPin(name, center, hole_diameter, along_x, along_y, base_bottom - pin_end)


def pin_texts(pin, stated_diameter, stated_length, problems):
    """A pin's across along x and y, its axis off its hole's and its
    length, against DESIGN.md."""
    off_center = math.hypot(middle(pin.along_x) - pin.center[0],
                            middle(pin.along_y) - pin.center[1])
    return [
        check(problems, f"{pin.name} across along x", length(pin.along_x), stated_diameter, 2),
        check(problems, "along y", length(pin.along_y), stated_diameter, 2),
        check(problems, "off its hole's axis", off_center, 0.0, 3),
        check(problems, "long", pin.length, stated_length, 2),
    ]


def measure_pins(pusher, base_bottom, problems):
    """([MeasuredPin], text), the push pins in PIN_NAMES' order."""
    pins, texts = [], []
    for name, hole in zip(PIN_NAMES, pin_holes(), strict=True):
        pin = measure_pin(pusher, base_bottom, name, hole, pin_length())
        pins.append(pin)
        texts.append(", ".join(pin_texts(pin, DESIGN_PIN_DIAMETER_MM, DESIGN_PIN_LENGTH_MM,
                                         problems)))
    return pins, "; ".join(texts)


def measure_pilot(pusher, base_bottom, problems):
    """(MeasuredPin, text): the pilot measured as the push pins are, and
    its chamfer, from how wide it is a quarter and a half of the
    chamfer's height over its tip, since a chamfer widens evenly from
    the tip."""
    pilot = measure_pin(pusher, base_bottom, PILOT_NAME, post_hole(), pilot_length())
    tip = base_bottom - pilot.length
    heights = (PILOT_CHAMFER_MM / 4.0, PILOT_CHAMFER_MM / 2.0)
    widths = [length(run_through(pusher, App.Vector(pilot.center[0], pilot.center[1],
                                                    tip + height), "x"))
              for height in heights]
    widening = (widths[1] - widths[0]) / (heights[1] - heights[0])  # per mm up
    tip_width = widths[0] - widening * heights[0]
    texts = pin_texts(pilot, DESIGN_PILOT_DIAMETER_MM, DESIGN_PILOT_LENGTH_MM, problems)
    texts.append(check(problems, "its tip chamfered", (length(pilot.along_x) - tip_width) / 2.0,
                       DESIGN_PILOT_CHAMFER_MM, 1))
    texts.append(check(problems, "at", math.degrees(math.atan(widening / 2.0)),
                       DESIGN_PILOT_CHAMFER_DEGREES, 0) + " degrees")
    return pilot, ", ".join(texts)


def measure_slot(pusher, base, problems):
    """((along x, along y), text): the pry slot's spans in plan and its
    text, measured through its middle as used: across along x, its
    middle off the base's north edge's, deep along y from that edge to
    its back wall, high along z down from the base's top, the face on
    the bed as printed (bed_text()), and the base left under it."""
    in_slot = App.Vector(middle(base.along_x), base.along_y[1] - SLOT_DEPTH_MM / 2.0,
                         base.along_z[1] - SLOT_HEIGHT_MM / 2.0)
    across = run_through(pusher, in_slot, "x", material=False)
    back_wall = run_through(pusher, in_slot, "y", material=False)[0]
    floor = run_through(pusher, in_slot, "z", material=False)[0]
    texts = [
        check(problems, "across", length(across), DESIGN_SLOT_MM[0], 1),
        check(problems, "off the north edge's middle", middle(across) - middle(base.along_x),
              0.0, 3),
        check(problems, "deep", base.along_y[1] - back_wall, DESIGN_SLOT_MM[1], 1),
        check(problems, "high", base.along_z[1] - floor, DESIGN_SLOT_MM[2], 1),
        f"the base {floor - base.along_z[0]:.3f} under it",
    ]
    return ((across, (back_wall, base.along_y[1])),
            "in the base's top at the middle of its north edge as used, " + ", ".join(texts))


def foot_under_slot(pusher, base, pin, slot):
    """(area, gap): how much of the pin's foot, its section at the base's
    underside, lies under the slot in plan, measured as the pin's volume
    within the slot's plan and the pin's ends along x and y over its
    length, and where those spans do not meet, how far apart they
    stand."""
    slot_x, slot_y = slot
    x = (max(slot_x[0], pin.along_x[0]), min(slot_x[1], pin.along_x[1]))
    y = (max(slot_y[0], pin.along_y[0]), min(slot_y[1], pin.along_y[1]))
    if length(x) <= 0.0 or length(y) <= 0.0:
        return 0.0, math.hypot(max(-length(x), 0.0), max(-length(y), 0.0))
    under = Part.makeBox(length(x), length(y), pin.length,
                         App.Vector(x[0], y[0], base.along_z[0] - pin.length))
    return pusher.common(under).Volume / pin.length, 0.0


def feet_text(pusher, base, pins, slot):
    """Each pin's foot against the slot over it as used: how much of its
    section lies under the slot in plan, or how far it stays clear."""
    texts = []
    for pin in pins:
        area, gap = foot_under_slot(pusher, base, pin, slot)
        section = pin_section_area(pin_diameter(pin.hole_diameter))
        if area > 0.0:
            texts.append(f"{pin.name} {area:.3f} of its {section:.3f} mm2 foot "
                         f"({100.0 * area / section:.0f} %)")
        else:
            texts.append(f"{pin.name} clear by {gap:.3f}")
    return "; ".join(texts)


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


def full_push_text(pilot, pins, problems):
    """Where the contact bosses' tops, the socket's top and the pilot's
    tip stand at the full push, the base on the frame's top face, taking
    the shortest push pin, failing where the socket's top ends above the
    walls' mouth."""
    bosses_depth = min(pin.length for pin in pins)
    under_mouth = bosses_depth + contact_boss_height() - mouth_depth()
    text = (f"the contact bosses' tops {bosses_depth:.3f} under the frame's top face, "
            f"{bosses_depth - ceiling_depth():.3f} under the ceiling, the socket's top "
            f"{round(under_mouth, 3) + 0.0:.3f} under the walls' mouth, which stands "
            f"{mouth_depth():.3f} under the top face; the pilot's tip {pilot.length:.3f} under "
            f"the top face, {pilot.length - ceiling_depth():.3f} under the ceiling")
    if under_mouth < -MEASURE_TOLERANCE_MM:
        problems.append(f"{text}: the socket's top above the mouth")
    return text


def bed_text(turned, slot, problems):
    """Where the slot lies on the pusher as printed: probed at its
    middle, turned as turned_for_printing() turns the pusher, its roof
    over the bed, z = 0, failing where it does not open down to the
    bed."""
    slot_x, slot_y = slot
    in_slot = App.Vector(middle(slot_x), layout.KEY_PITCH_MM - middle(slot_y),
                         SLOT_HEIGHT_MM / 2.0)
    floor, roof = run_through(turned, in_slot, "z", material=False)
    text = ("the slot in the base's south edge as printed, "
            + check(problems, "its roof over the bed", roof, DESIGN_SLOT_MM[2], 1))
    if floor >= 0.0:
        problems.append(f"{text}, not open to the bed")
    return text


def main():
    arguments = script_arguments(sys.argv)
    if len(arguments) != 1 or "=" in arguments[0]:
        raise SystemExit(USAGE)
    stl_file = arguments[0]
    pusher = build_pusher()
    print(f"pusher:     one valid solid, volume {pusher.Volume:.3f} mm3")
    problems = []
    base, base_text = measure_base(pusher, problems)
    print(f"base:       {base_text}")
    pins, pin_text = measure_pins(pusher, base.along_z[0], problems)
    print(f"pins:       {pin_text}, as modelled")
    pilot, pilot_text = measure_pilot(pusher, base.along_z[0], problems)
    print(f"pilot:      {pilot_text}, as modelled")
    lead_text = check(problems, "in its hole before the push pins reach theirs by",
                      pilot.length - max(pin.length for pin in pins), DESIGN_PILOT_LEAD_MM, 1)
    print(f"lead:       the pilot {lead_text}")
    slot, slot_text = measure_slot(pusher, base, problems)
    print(f"slot:       {slot_text}")
    print(f"feet:       under the slot as used, {feet_text(pusher, base, [pilot] + pins, slot)}")
    push_text = check(problems, "the socket down by", push(), DESIGN_PUSH_MM, 2)
    print(f"push:       {push_text}, the pocket walls' depth")
    print(f"length:     {pin_length():.3f}: {contact_bosses_depth():.3f} from the frame's top "
          f"face down to the contact bosses' tops (the ceiling {ceiling_depth():.3f} down, the "
          f"bosses {contact_boss_height():.2f} over the socket's top against it), plus the push, "
          "both as printed")
    print(f"in holes:   as printed, {hole_fit_text([pilot] + pins, problems)}")
    print(f"full push:  the base on the frame's top face, {full_push_text(pilot, pins, problems)}")
    turned = turned_for_printing(pusher)
    print(f"bed:        {bed_text(turned, slot, problems)}")
    if problems:
        raise SystemExit("error: off DESIGN.md's figures or the pusher's rules:\n  "
                         + "\n  ".join(problems))
    mesh = export_stl(turned, stl_file)
    check_closed_mesh(stl_file)
    box = mesh.BoundBox
    print(f"print:      base down, the pins up, no support, {box.XLength:.2f} x "
          f"{box.YLength:.2f} x {box.ZLength:.2f} mm")
    print(f"wrote:      {stl_file} ({mesh.CountFacets} facets), one closed manifold shell; one "
          "serves both halves")


run_and_exit(main)
