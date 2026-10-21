"""The socket retention test strips' shapes (work item 008): a frame
printed in place of the PCB that holds Kailh Choc hotswap sockets in
pockets on its underside, for a keyboard wired by hand, in three
stackable strips of CELL_COUNT cells at the key pitch. Also the switch
hole strip (work item 012, SWITCH below), the frame's body alone.

A frame strip (POCKET or HOLES) has a body of the PCB's thickness, each
cell with one key's footprint holes grown by pull_in like the PCB
mock's, so the switch's pins reach the socket's contacts as through a
PCB, but for the two pin holes the socket's bosses sit in: on the
pocket strip they are POCKET_STRIP_PIN_HOLE_DIAMETER_MM as modelled,
so they leave the bosses free and the pocket alone locates the socket,
and on the hole strip they step across the cells.
Under each cell, pocket walls around the socket's plastic body, open
at the bottom, against which the socket's top face rests on the
underside of the frame's body (the ceiling). They follow the body's
outline, curves and all (layout.HOTSWAP_SOCKET_OUTLINE_MM, from the
socket's STEP, not the cover layout.HOTSWAP_SOCKET_LOBES_MM and
HOTSWAP_SOCKET_FILLS_MM give the tray): in plan they are the region
between the outline moved out by the pocket's gap (pocket_gap(), their
inner face) and by the gap plus WALL_THICKNESS_MM (their outer face),
corners extended to their intersections. The walls are
layout.HOTSWAP_SOCKET_BODY_HEIGHT_MM deep, the socket body's height on
Kailh's drawing (1.80, to the bumps on its top that bear on a board),
not layout.HOTSWAP_SOCKET_REACH_MM: kbdkid4's STEP hangs its 1.85 body
0.17 below the PCB, which a socket pressed against a printed ceiling
does not do. The walls are built whole, and every footprint hole runs
on from the frame's body down through them to their mouth, so the
switch's center post and side pegs, which reach below the frame's body,
pass them: the west peg's hole bores through lobe B's north wall (the
socket's lobe passes that hole by 0.42), leaving a sliver of the wall's
inner side at the tighter fits and none at the hole strip's. No other
hole meets a wall (cell_wall_bores() finds the ones that do in the
walls' plan): the center post's hole, 1.9 in radius at the default
pull_in, keeps 2.36 from its center to the walls' outer face around lobe
B's round toward lobe A at the pocket strip's -0.15, the frame's fit.
The walls are slotted through their full depth where the socket's two
metal end tabs leave the body's ends. The slots are wider than the
straight part of either end between its chamfers or its round and step,
so they take the walls' inner face along those parts, but for at most
0.1 of the east end's beside each slot at the looser fits.

The tabs: the user solders a wire to each tab before pressing the
socket in from below, since an iron on a tab in its pocket would melt
the plastic around it (the tab lies against the ceiling, the wall 0.2
beside it). So each tab's slot is open at the walls' mouth, wide enough
for the tab with TAB_SOLDER_PER_SIDE_MM of solder on both sides at the
slip fit, and runs on into a recess in the ceiling over the tab, which
leaves room for solder on the tab's top face.

The strips print upside down, the frame's top face on the bed, the
walls growing up. In the project's print model (layout.py's printed
fits) every vertical face swells PRINT_SWELLING_PER_SIDE_MM, so the
pockets are printed_fit() of the socket's body and the footprint holes
are grown by pull_in. The ceiling (the underside the socket fits
against), the walls' mouths and the bosses' ends face up on the bed
and rise together, so relative to the ceiling they stay where they are
modelled. The model counted that rise as
PRINT_RISE_OF_UP_FACING_BOTTOMS_MM, 0.2, which boss_end_depth() keeps;
measured on the pocket strip the body came out 1.65 thick, a rise of
PRINT_RISE_OF_TOP_FACES_MM, which the backing's top shares.

POCKET: the pocket's fit steps across the cells (cell_pocket_fit()),
the pin holes at POCKET_STRIP_PIN_HOLE_DIAMETER_MM. Any pocket can be
glued.

HOLES: every pocket at HOLE_STRIP_POCKET_FIT_MM, loose, and the pin
holes stepping down from the pocket strip's across the cells
(cell_pin_hole_diameter()), so only the holes can hold the socket.

The frame strips carry the same bosses, at every cell boundary and at
both ends of the strip, BOSS_NORTH_OF_KEY_ROW_MM north and
BOSS_SOUTH_OF_KEY_ROW_MM south of the key row, the tray's standoffs'
diameter, bored for the tray's M2 heat-set inserts. They end
boss_end_depth() below the ceiling, past the walls' mouth, so the
backing on them stands clear of the walls. The frame's body reaches
BOSS_EDGE_MARGIN_MM past the bosses.

BACKING: BACKING_THICKNESS_MM thick, with clearance holes for
M2 screws under the bosses and, under each of the body's lobes, a pad of
the cover's lobe rectangle (PAD_LOBE_RECTANGLES_MM) moved in by
PAD_INSET_MM, whose top relative to the socket's bottom steps across
the cells (cell_pad_offset()). The backing prints bottom down, so its
top and its pads' tops rise together and the pads stand where they are
modelled relative to the bosses' ends and so to the ceiling.

Cell k (from 1, west to east) has k notches in its south edge on every
strip, as on the slit test strip, the frame strips' through the frame
south of the pockets and the backing's in line with them. The pocket
strip also has five notches (MARK_WIDTH_MM, MARK_DEPTH_MM) in its north
edge (POCKET_STRIP_MARK_XS_MM), one at every cell boundary, clear of
the bosses and the switches, which tell it from the first pocket strip,
which had none, the second, which had the two between cells 2 and 3
and between cells 4 and 5, and the third, which had four, at every
boundary but the middle one. The hole strip has three
(HOLE_STRIP_MARK_XS_MM), between cells 1 and 2, 3 and 4 and 5 and 6.
The backing has two (BACKING_MARK_XS_MM), between cells 2 and 3 and
between cells 4 and 5, which tell it from the second backing, which
had one in the middle and pads 0.1 larger each way, and from the
first, which had none and pads 0.3 larger each way.

SWITCH: the switch hole strip, to find the holes for the switch's
center post and side pegs that hold it without play sideways (the
user, 2026-10-20: "On eg. the hotswap socket test strip these pin
holes are too wide and doesn't aid in sideways stability of the
switch"). Its cells are 19.05 squares of the frame's body with each
cell's footprint holes and the notches in their south edge, and
nothing else: no walls, bosses, tab recesses or marks. The post's and
both pegs' holes step together across cells 1 to 5, each printing the
cell's clearance over the calipered parts by the shrink the hole strip
measured (MEASURED_HOLE_SHRINK_PER_SIDE_MM), and cell 6 has the socket
strips' holes, grown by pull_in, as the reference
(switch_strip_hole_radius()). The pin holes are the frame's 3.2, so
the blades pass freely and only the post and pegs hold the switch. It
prints top face down like the frame strips, so the switch's housing
sits on the face that was on the bed.

A switch is the same on both halves, so is the frame: the footprint is
the left half's (layout.footprint_holes() at FOOTPRINT_ROTATION_DEGREES).

Coordinates: the strip's frame, the cells' south west corner at (0, 0),
cell index (from 0) at cell_key_center(index), z 0 on the ceiling, the
frame's body up to the PCB's thickness, walls and bosses below. The
backing is built with its bottom on z = 0 and stacked by
stacked_backing().

Like the other *_shape.py modules this one has no entry point, so
probes and the export script can import it.
"""

import math

import FreeCAD as App
import Part

import layout
import pcb_shape
from freecad_common import offset_outline
from tray_shape import (CUT_EXTRA_MM, UP, layout_polygon_wire, plan_prism,
                        require_one_valid_solid)

POCKET = "pocket"
BACKING = "backing"
HOLES = "holes"
SWITCH = "switch"
STRIP_KINDS = (POCKET, BACKING, HOLES, SWITCH)
# The frame strips the backing is stacked under and checked against.
FRAME_KINDS = (POCKET,)

CELL_COUNT = 6

# The steps across the cells, cell 1's figure and the step: the pocket's
# fit and the pads' tops relative to the socket's bottom (negative a
# gap, positive pressing). The pocket's fits are all tighter than snug:
# on the first pocket strip, -0.10 to +0.15, every pocket but cells 3
# and 5 printed loose (doc/log/2026-10-17.md).
FIRST_POCKET_FIT_MM = -0.40
POCKET_FIT_STEP_MM = 0.05
FIRST_PAD_OFFSET_MM = -0.10
PAD_OFFSET_STEP_MM = 0.05

# The pocket strip's two pin holes (layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM),
# which the socket's 2.90 bosses sit in, as modelled whatever pull_in.
# On the first pocket strip they were the footprint's 3.0 grown to 3.4,
# and its pockets' result mixed the bosses' fit with the pocket's, so
# these must leave the bosses free and let the pocket alone locate the
# socket. 3.5 is the user's "something like 3.5 mm", within the 3.54 at
# which the tab recess keeps RECESS_HOLE_CLEARANCE_MM (export) from the
# hole.
POCKET_STRIP_PIN_HOLE_DIAMETER_MM = 3.5

# The hole strip: every pocket at the first pocket strip's cell 6 fit,
# which the user found loose, so only the pin holes can hold the
# socket, the pin holes stepping down from the pocket strip's across the
# cells (cell_pin_hole_diameter()), as modelled whatever pull_in.
HOLE_STRIP_POCKET_FIT_MM = 0.15
HOLE_STRIP_PIN_HOLE_STEP_MM = 0.10

# The switch hole strip: the switch's center post and side pegs as the
# user calipered them on a real Kailh Choc v1, 2026-10-20: "Post is 3.17
# and pegs are 1.65 mm diameter".
SWITCH_POST_CALIPERED_DIAMETER_MM = 3.17
SWITCH_PEG_CALIPERED_DIAMETER_MM = 1.65
# How much smaller than modelled a hole prints, per side: on the hole
# strip 3.2 as modelled held the socket's 2.9 bosses best, and 3.3, the
# zero clearance cell by the print model's PRINT_SWELLING_PER_SIDE_MM
# (0.2), was loose (DESIGN.md, "Hole strip"). That was measured on 3.x
# holes. No hole as small as the pegs' has been measured, so theirs is
# taken to shrink the same.
MEASURED_HOLE_SHRINK_PER_SIDE_MM = 0.15
# Cells 1 to 5 step the post's and both pegs' holes together through
# these diametral clearances as printed over the calipered parts, from
# slightly tight to loose. Cell 6 has the socket strips' holes (the
# footprint's grown by pull_in) as the reference.
FIRST_SWITCH_HOLE_CLEARANCE_MM = -0.05
SWITCH_HOLE_CLEARANCE_STEP_MM = 0.05
SWITCH_REFERENCE_CELL_INDEX = CELL_COUNT - 1
# The two pin holes, which the switch's blades pass through: the
# frame's, the hole strip's cell 4 (DESIGN.md, "Hole strip"), as
# modelled whatever pull_in, so the blades pass freely and only the
# post and pegs hold the switch. The NC pad's hole stays as the frame
# strips have it, grown by pull_in.
SWITCH_STRIP_PIN_HOLE_DIAMETER_MM = 3.2

# The pocket walls, as thick as the tray's (two lines). The switch's
# center post and side pegs, whose holes are
# layout.CHOC_FOOTPRINT_HOLES_MM's first three, reach below the frame's body.
WALL_THICKNESS_MM = layout.TRAY_WALL_MM
SWITCH_PROTRUDING_HOLE_COUNT = 3

# The tabs' slots and recesses: the tab with this much solder on each
# side passes its slot at the slip fit, and the recess reaches this far
# past the tab's tip and this deep into the frame (its bottom faces up
# as printed, so it leaves 0.3 of room over the tab's top face).
TAB_SOLDER_PER_SIDE_MM = 0.5
TAB_RECESS_PAST_TIP_MM = 0.5
TAB_RECESS_DEPTH_MM = 0.5

# The bosses: the tray's standoff diameter and insert bore, on every
# boundary between cells and at both ends of the strip, north and south
# of the key row (the north row set 0.5 clear of the cover's walls
# around the fill at the body's north west corner in a +0.15 pocket, the
# first pocket strip's loosest, 0.584 from the outline's walls on the
# hole strip, the south row where it was set 0.5 clear of the scrapped
# lip strip's fingers' slots, which filled the cells' south edge). The
# bore's floor keeps the frame's top face whole, three layers.
BOSS_DIAMETER_MM = layout.STANDOFF_DIAMETER_MM
INSERT_BORE_DIAMETER_MM = layout.STANDOFF_BORE_DIAMETER_MM
BOSS_NORTH_OF_KEY_ROW_MM = 3.1
BOSS_SOUTH_OF_KEY_ROW_MM = -12.5
INSERT_BORE_FLOOR_MM = 0.6
BOSS_EDGE_MARGIN_MM = 0.5

# The backing: its thickness (the battery clearance in the real tray
# allows backing_thickness_limit(), four layers fit under it), the
# screws' clearance holes (the PCB's mounting drills, printed), and how
# far each pad lies inside its socket lobe as modelled: 0.95, set for
# the scrapped lip strip (its largest lip's 0.35 reach as printed, the
# 0.1 its walls stood inside the lobe as printed at -0.20, the pad's 0.2
# swelling and 0.3 of clearance to that lip) and kept so the third
# backing stays. The user wants the pads smaller in plan, not a perfect
# fit (doc/log/2026-10-18.md).
BACKING_THICKNESS_MM = 0.8
# The backing's M2 screws go up through it into the frame's inserts, so
# their heads hang below its underside (the user, 2026-10-20: "Also we
# need to take the backing screws sticking out below the backing piece
# into the calculation"), as tall as the user's pan heads ("The M2 pan
# head screws I have today have roughly 1.5 mm high heads btw").
BACKING_SCREW_HEAD_HEIGHT_MM = 1.5
SCREW_CLEARANCE_HOLE_DIAMETER_MM = layout.printed_fit(
    layout.MOUNTING_DRILL_DIAMETER_MM, layout.SNUG_FIT_MM
)
PAD_INSET_MM = 0.95

# The pads' rectangles before PAD_INSET_MM, in footprint-local
# coordinates (x range, y range): the cover's lobes
# (layout.HOTSWAP_SOCKET_LOBES_MM) cut back to the body's ends, which the
# third backing was printed with, the lobes' north and south faces at
# the outline's, 0.003 from the cover's rounded ones (moved there with
# the scrapped lip strip's lips, which sat on those faces, in the same
# print). Lobe B's reaches down to the cover's y 2.25, so on the outline
# its pad's corner beside the 1.5 fill lies 0.534 inside the body, the
# nearest the pads come to its edge, where the pockets' walls follow it.
PAD_LOBE_RECTANGLES_MM = (
    ((-8.223, -3.573), (-2.07, 2.25)),
    ((-6.023, -1.373), (2.25, 7.48)),
)

# The notches that number the cells, as on the slit test strip, through
# each strip from its south edge, and the marks in each strip's north
# edge, 3.0 wide at cell boundaries, so each lies over a boss, 2.0 north
# of it: the pocket strip five, the hole strip three, the third backing
# the second pocket strip's two (the second backing had one in the
# middle).
NOTCH_WIDTH_MM = 1.0
NOTCH_DEPTH_MM = 0.8
NOTCH_PITCH_MM = 2.0
MARK_WIDTH_MM = 3.0
MARK_DEPTH_MM = 1.5
POCKET_STRIP_MARK_XS_MM = tuple(boundary * layout.KEY_PITCH_MM for boundary in range(1, CELL_COUNT))
HOLE_STRIP_MARK_XS_MM = (1 * layout.KEY_PITCH_MM, 3 * layout.KEY_PITCH_MM,
                         5 * layout.KEY_PITCH_MM)
BACKING_MARK_XS_MM = tuple(boundary * layout.KEY_PITCH_MM for boundary in (2, 4))

VOLUME_RELATIVE_TOLERANCE = pcb_shape.VOLUME_RELATIVE_TOLERANCE
AREA_TOLERANCE_MM2 = 1e-9
LENGTH_TOLERANCE_MM = 1e-9


# Plane geometry, plain Python.


def cross(origin, point_a, point_b):
    return (point_a[0] - origin[0]) * (point_b[1] - origin[1]) - (
        point_a[1] - origin[1]
    ) * (point_b[0] - origin[0])


def clip_convex(subject, clip):
    """The part of a convex counter-clockwise polygon inside another
    (Sutherland-Hodgman), possibly empty. A point on a clip edge's line
    (within rounding, as where two cutters meet) counts as inside, so an
    edge along that line is kept whole rather than crossed."""
    output = list(subject)
    for index in range(len(clip)):
        edge_start, edge_end = clip[index], clip[(index + 1) % len(clip)]
        points, output = output, []
        for point_index, point in enumerate(points):
            before = points[point_index - 1]
            point_inside = cross(edge_start, edge_end, point) >= -AREA_TOLERANCE_MM2
            before_inside = cross(edge_start, edge_end, before) >= -AREA_TOLERANCE_MM2
            if point_inside != before_inside:
                output.append(segment_line_crossing(before, point, edge_start, edge_end))
            if point_inside:
                output.append(point)
        if not output:
            return ()
    return tuple(output)


def segment_line_crossing(start, end, line_start, line_end):
    direction = (end[0] - start[0], end[1] - start[1])
    line_direction = (line_end[0] - line_start[0], line_end[1] - line_start[1])
    return layout.line_intersection(start, direction, line_start, line_direction)


def convex_area(polygons):
    """The area common to convex counter-clockwise polygons."""
    common = polygons[0]
    for polygon in polygons[1:]:
        common = clip_convex(common, polygon)
        if len(common) < 3:
            return 0.0
    return layout.polygon_signed_area(common)


def rectangle(x_range, y_range):
    return (
        (x_range[0], y_range[0]),
        (x_range[1], y_range[0]),
        (x_range[1], y_range[1]),
        (x_range[0], y_range[1]),
    )


# The cells and their steps.


def cell_key_center(index):
    """Cell index's (from 0) key center in the strip's frame."""
    half_pitch = layout.KEY_PITCH_MM / 2.0
    return (half_pitch + index * layout.KEY_PITCH_MM, half_pitch)


def cell_pocket_fit(kind, index):
    if kind == HOLES:
        return HOLE_STRIP_POCKET_FIT_MM
    return FIRST_POCKET_FIT_MM + index * POCKET_FIT_STEP_MM


def cell_pad_offset(index):
    return FIRST_PAD_OFFSET_MM + index * PAD_OFFSET_STEP_MM


def pocket_gap(fit):
    """How far a pocket wall's inner face lies outside the socket, as
    modelled."""
    return layout.half_fit_gap(0.0, fit)


# Heights, below the ceiling (positive numbers, the strip's z is their
# negative).


def socket_height():
    return layout.HOTSWAP_SOCKET_BODY_HEIGHT_MM


def wall_depth():
    """The pocket walls' depth below the ceiling: the socket's height."""
    return socket_height()


def boss_end_depth():
    """Where the bosses end and the backing's top sits on them: 2.267,
    kept from the scrapped lip strip (doc/log/2026-10-19.md), whose
    largest lip's 45 degree lead-in met its wall there. That is the
    lip's retaining face, the socket's height below the ceiling as
    printed (which rises), plus the lip's 0.35 reach past the walls'
    inner faces as printed less the lead-in's growth past the walls'
    swelling. The fourth pocket strip, the hole strip and the third
    backing are printed and stay, so the figure is computed as before,
    not rounded: the STLs store float32, where a rounded figure would
    move the bosses' ends and the pads."""
    largest_reach_as_printed = 0.35
    lead_in_tip_growth = (
        layout.PRINT_SWELLING_AT_45_DEGREES_MM - layout.PRINT_SWELLING_PER_SIDE_MM
    )
    return (socket_height() + layout.PRINT_RISE_OF_UP_FACING_BOTTOMS_MM
            + (largest_reach_as_printed - lead_in_tip_growth))


def boss_height():
    """From the frame's top face to the boss's end."""
    return layout.PCB_THICKNESS_MM + boss_end_depth()


def longest_insert_length():
    """The longest insert the boss holds: its height less the bore's
    floor and the rise of the bore's bottom, which faces up as printed."""
    return boss_height() - INSERT_BORE_FLOOR_MM - layout.PRINT_RISE_OF_UP_FACING_BOTTOMS_MM


def insert_bore_depth(insert_length):
    return insert_length + layout.PRINT_RISE_OF_UP_FACING_BOTTOMS_MM


def pad_top_depth(index):
    return socket_height() - cell_pad_offset(index)


def pad_height(index):
    """Cell index's pads above the backing's top."""
    return boss_end_depth() - pad_top_depth(index)


def backing_thickness_limit(socket_bottom_z=None):
    """The thickest backing the battery allows in the real tray: from
    the socket's bottom with the frame in the PCB's place, less the
    pads' room (from the socket's bottom to the backing's top), the
    backing's own rise as printed (its top face rises
    PRINT_RISE_OF_TOP_FACES_MM, so its bottom lies that much lower), the
    screw heads under it and the clearance to the battery."""
    if socket_bottom_z is None:
        socket_bottom_z = layout.PCB_UNDERSIDE_Z_MM - socket_height()
    pads_room = boss_end_depth() - socket_height()
    return (
        socket_bottom_z
        - pads_room
        - layout.PRINT_RISE_OF_TOP_FACES_MM
        - BACKING_SCREW_HEAD_HEIGHT_MM
        - layout.MINIMUM_BATTERY_TO_SOCKET_CLEARANCE_MM
        - layout.BATTERY_TOP_Z_MM
    )


def backing_underside_z_as_printed(socket_bottom_z=None):
    """The backing's underside in the real tray, the frame in the PCB's
    place: the socket's bottom less the pads' room and the backing's
    thickness, and lower by the backing's own rise as printed, its top
    face resting on the bosses' ends."""
    if socket_bottom_z is None:
        socket_bottom_z = layout.PCB_UNDERSIDE_Z_MM - socket_height()
    pads_room = boss_end_depth() - socket_height()
    return (socket_bottom_z - pads_room - BACKING_THICKNESS_MM
            - layout.PRINT_RISE_OF_TOP_FACES_MM)


def backing_screw_heads_bottom_z(socket_bottom_z=None):
    """Where the backing's screw heads end below it in the real tray, as
    printed."""
    return backing_underside_z_as_printed(socket_bottom_z) - BACKING_SCREW_HEAD_HEIGHT_MM


# The socket and its pocket in plan.


def outline_local_points():
    """The outline's points in footprint-local coordinates: its start
    and every line's and arc's points."""
    start, segments = layout.HOTSWAP_SOCKET_OUTLINE_MM
    return [start] + [point for _, *points in segments for point in points]


def board_vector(key_center, local_point):
    return App.Vector(*layout.footprint_point(key_center, local_point), 0.0)


def outline_wire(key_center):
    """The socket's plastic body's outline (layout.HOTSWAP_SOCKET_OUTLINE_MM)
    in board coordinates, a closed wire on z = 0."""
    start, segments = layout.HOTSWAP_SOCKET_OUTLINE_MM
    current = board_vector(key_center, start)
    edges = []
    for kind, *points in segments:
        through = [board_vector(key_center, point) for point in points]
        curve = (Part.LineSegment(current, *through) if kind == "line"
                 else Part.Arc(current, *through))
        edges.append(curve.toShape())
        current = through[-1]
    wire = Part.Wire(edges)
    if not wire.isClosed():
        raise SystemExit("error: the socket's outline does not close")
    return wire


def outline_face(key_center):
    return Part.Face(outline_wire(key_center))


def pocket_face(key_center, distance):
    """The outline moved out by distance, its corners extended to their
    intersections, as a plan face. Inward (a negative pocket gap, a fit
    under -0.40) is refused: makeOffset2D returns nothing for this
    outline moved inward with sharp joins, and the pocket strip tests no
    such fit."""
    wire = outline_wire(key_center)
    if distance < -LENGTH_TOLERANCE_MM:
        raise ValueError(f"the outline cannot be moved inward ({distance:.4f} mm)")
    if distance < LENGTH_TOLERANCE_MM:
        return Part.Face(wire)
    return Part.Face(offset_outline(wire, distance))


def plan_face(polygon):
    return Part.Face(layout_polygon_wire(polygon, 0.0))


def circle_face(center, radius):
    return Part.Face(Part.Wire(Part.makeCircle(radius, App.Vector(center[0], center[1], 0.0))))


def socket_tab_specs():
    """Each end tab as (footprint-local x center, its width, the y of
    the body's end it leaves, the y of its tip)."""
    low, high = layout.HOTSWAP_SOCKET_BODY_ENDS_MM
    specs = []
    for polygon in layout.HOTSWAP_SOCKET_TABS_MM:
        xs = [x for x, _ in polygon]
        ys = [y for _, y in polygon]
        if min(ys) >= high:
            face, tip = high, max(ys)
        elif max(ys) <= low:
            face, tip = low, min(ys)
        else:
            raise SystemExit("error: a socket tab does not leave the body's end")
        specs.append(((min(xs) + max(xs)) / 2.0, max(xs) - min(xs), face, tip))
    return specs


def tab_slot_width(tab_width):
    return layout.printed_fit(tab_width + 2.0 * TAB_SOLDER_PER_SIDE_MM, layout.SLIP_FIT_MM)


def footprint_span_rectangle(key_center, x_center, width, y_from, y_to):
    """A rectangle in board coordinates, footprint-local x center and
    width, between two footprint-local y."""
    return layout.footprint_rectangle(
        key_center, (x_center, (y_from + y_to) / 2.0), width, abs(y_to - y_from)
    )


def tab_slot(key_center, tab):
    """The tab's slot through the walls and recess into the frame in
    plan: from the body's end past the tip."""
    x_center, width, face, tip = tab
    end = tip + math.copysign(TAB_RECESS_PAST_TIP_MM, tip - face)
    return footprint_span_rectangle(key_center, x_center, tab_slot_width(width), face, end)


def tab_wire_room(key_center, tab):
    """Room for the wire soldered to the tab, by layout.py's wire room
    rule: WIRE_ROOM_BEHIND_LEADS_MM past the tip, the tab and
    WIRE_ROOM_BESIDE_LEADS_MM beside it."""
    x_center, width, face, tip = tab
    end = tip + math.copysign(layout.WIRE_ROOM_BEHIND_LEADS_MM, tip - face)
    room_width = width + 2.0 * layout.WIRE_ROOM_BESIDE_LEADS_MM
    return footprint_span_rectangle(key_center, x_center, room_width, tip, end)


def wall_cutters(key_center):
    """The tab slots, cut out of every cell's pocket walls, which do not
    overlap."""
    cutters = [tab_slot(key_center, tab) for tab in socket_tab_specs()]
    for first in range(len(cutters)):
        for second in range(first + 1, len(cutters)):
            if convex_area((cutters[first], cutters[second])) > AREA_TOLERANCE_MM2:
                raise SystemExit("error: two of a pocket's wall cutters overlap")
    return cutters


def wall_ring(key_center, fit):
    """A cell's pocket walls in plan before their cuts: between the
    outline moved out by the pocket's gap (the walls' inner face) and by
    the gap plus WALL_THICKNESS_MM (their outer face)."""
    gap = pocket_gap(fit)
    return pocket_face(key_center, gap + WALL_THICKNESS_MM).cut(pocket_face(key_center, gap))


def cell_walls_plan(kind, index):
    """Cell index's walls in plan less their cutters, before the
    footprint holes bore them."""
    key_center = cell_key_center(index)
    cutters = [plan_face(cutter) for cutter in wall_cutters(key_center)]
    ring = wall_ring(key_center, cell_pocket_fit(kind, index))
    return ring.cut(Part.makeCompound(cutters))


def cell_wall_bores(kind, index, pull_in):
    """{footprint-local center: the area its hole bores out of cell
    index's walls} for every footprint hole that meets their plan. The
    holes do not overlap, so their shares add up."""
    walls = cell_walls_plan(kind, index)
    bores = {}
    for (local_center, _), (center, radius) in zip(layout.CHOC_FOOTPRINT_HOLES_MM,
                                                   cell_holes(kind, index, pull_in)):
        area = walls.common(circle_face(center, radius)).Area
        if area > AREA_TOLERANCE_MM2:
            bores[local_center] = area
    return bores


def wall_area(kind, index, pull_in):
    """Cell index's walls in plan as built: less their cutters and the
    footprint holes."""
    bores = cell_wall_bores(kind, index, pull_in)
    return cell_walls_plan(kind, index).Area - sum(bores.values())


# The frame's body, bosses and notches in plan.


def boss_centers():
    _, key_row_y = cell_key_center(0)
    return [
        (boundary * layout.KEY_PITCH_MM, key_row_y + offset)
        for boundary in range(CELL_COUNT + 1)
        for offset in (BOSS_NORTH_OF_KEY_ROW_MM, BOSS_SOUTH_OF_KEY_ROW_MM)
    ]


def frame_body_rectangle():
    """The strip's outline: the cells, reaching BOSS_EDGE_MARGIN_MM past
    the bosses at the ends and the south."""
    reach = BOSS_DIAMETER_MM / 2.0 + BOSS_EDGE_MARGIN_MM
    _, key_row_y = cell_key_center(0)
    return (
        (-reach, CELL_COUNT * layout.KEY_PITCH_MM + reach),
        (key_row_y + BOSS_SOUTH_OF_KEY_ROW_MM - reach, layout.KEY_PITCH_MM),
    )


def frame_body_area():
    (x_low, x_high), (y_low, y_high) = frame_body_rectangle()
    return (x_high - x_low) * (y_high - y_low)


def notch_x_centers(index):
    """The x centers of cell index's possible notches, west to east."""
    key_x, _ = cell_key_center(index)
    middle = (CELL_COUNT + 1) / 2.0
    return [key_x + (number - middle) * NOTCH_PITCH_MM for number in range(1, CELL_COUNT + 1)]


def notch_rectangles():
    """Cell k (from 1) gets its first k notches, in the frame's body's
    south edge."""
    _, (y_low, _) = frame_body_rectangle()
    return notch_rectangles_from(y_low)


def notch_rectangles_from(south_y):
    """Cell k (from 1) gets its first k notches, in a south edge at
    south_y."""
    return [
        rectangle((x - NOTCH_WIDTH_MM / 2.0, x + NOTCH_WIDTH_MM / 2.0),
                  (south_y, south_y + NOTCH_DEPTH_MM))
        for index in range(CELL_COUNT)
        for x in notch_x_centers(index)[: index + 1]
    ]


def strip_mark_xs(kind):
    """The x centers of a strip's marks in its north edge."""
    marks = {POCKET: POCKET_STRIP_MARK_XS_MM, HOLES: HOLE_STRIP_MARK_XS_MM,
             BACKING: BACKING_MARK_XS_MM}
    return marks.get(kind, ())


def mark_rectangle(x):
    _, (_, y_high) = frame_body_rectangle()
    half = MARK_WIDTH_MM / 2.0
    return rectangle(
        (x - half, x + half),
        (y_high - MARK_DEPTH_MM, y_high),
    )


def edge_cut_rectangles(kind):
    """The notches, and the strip's marks."""
    return notch_rectangles() + [mark_rectangle(x) for x in strip_mark_xs(kind)]


# Analytic volumes, from the plan geometry above alone: the walls' areas
# from 2D booleans of their plan faces (wall_area()), the rest from
# plain Python, so the solids' 3D fuses and cuts are checked against
# them.


def is_pin_hole(local_center):
    return local_center in layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM


def cell_pin_hole_diameter(index):
    """The hole strip's cell index's pin holes as modelled."""
    return POCKET_STRIP_PIN_HOLE_DIAMETER_MM - index * HOLE_STRIP_PIN_HOLE_STEP_MM


def hole_radius(kind, index, local_center, diameter, pull_in):
    """Cell index's footprint hole's radius as modelled: grown by
    pull_in, but the pocket strip's pin holes
    POCKET_STRIP_PIN_HOLE_DIAMETER_MM across, the hole strip's
    cell_pin_hole_diameter() and the switch hole strip's
    switch_strip_hole_radius()."""
    if kind == SWITCH:
        return switch_strip_hole_radius(index, local_center, diameter, pull_in)
    if kind == POCKET and is_pin_hole(local_center):
        return POCKET_STRIP_PIN_HOLE_DIAMETER_MM / 2.0
    if kind == HOLES and is_pin_hole(local_center):
        return cell_pin_hole_diameter(index) / 2.0
    return diameter / 2.0 + pull_in


def cell_holes(kind, index, pull_in):
    """Cell index's footprint holes as (center, radius as modelled), in
    layout.CHOC_FOOTPRINT_HOLES_MM's order."""
    return [(center, hole_radius(kind, index, local_center, diameter, pull_in))
            for (center, diameter), (local_center, _) in zip(
                layout.footprint_holes(cell_key_center(index)), layout.CHOC_FOOTPRINT_HOLES_MM)]


def hole_cutter(center, radius, thickness):
    return pcb_shape.hole_cutter(center, 2.0 * radius, 0.0, thickness)


def strip_holes(kind, pull_in):
    """Every cell's footprint holes as (center, radius) in the frame."""
    return [hole for index in range(CELL_COUNT)
            for hole in cell_holes(kind, index, pull_in)]


def strip_tab_slots():
    return [tab_slot(cell_key_center(index), tab)
            for index in range(CELL_COUNT) for tab in socket_tab_specs()]


def frame_analytic_volume(kind, pull_in, insert_length):
    thickness = layout.PCB_THICKNESS_MM
    holes = sum(math.pi * radius**2 for _center, radius in strip_holes(kind, pull_in))
    recesses = sum(layout.polygon_signed_area(slot) for slot in strip_tab_slots())
    walls = sum(wall_area(kind, index, pull_in) for index in range(CELL_COUNT))
    edge_cuts = sum(layout.polygon_signed_area(cut) for cut in edge_cut_rectangles(kind))
    boss_count = len(boss_centers())
    bosses = boss_count * math.pi * (BOSS_DIAMETER_MM / 2.0) ** 2 * boss_end_depth()
    bores = (
        boss_count * math.pi * (INSERT_BORE_DIAMETER_MM / 2.0) ** 2
        * insert_bore_depth(insert_length)
    )
    return (
        (frame_body_area() - holes - edge_cuts) * thickness
        - recesses * TAB_RECESS_DEPTH_MM
        + walls * wall_depth()
        + bosses
        - bores
    )


def pad_polygons(key_center):
    """The pads: each of PAD_LOBE_RECTANGLES_MM moved in by PAD_INSET_MM.
    The rectangle rather than the cover's chamfered lobe B, whose 0.608
    chamfer edge collapses under an inset past 0.73 and turned the pad
    inside out at 0.85."""
    inset = PAD_INSET_MM
    pads = []
    for local_range in PAD_LOBE_RECTANGLES_MM:
        corners = layout.footprint_polygon(key_center, rectangle(*local_range))
        xs = [x for x, _ in corners]
        ys = [y for _, y in corners]
        pads.append(rectangle((min(xs) + inset, max(xs) - inset),
                              (min(ys) + inset, max(ys) - inset)))
    return pads


def backing_analytic_volume():
    hole_area = math.pi * (SCREW_CLEARANCE_HOLE_DIAMETER_MM / 2.0) ** 2
    edge_cuts = sum(layout.polygon_signed_area(cut) for cut in edge_cut_rectangles(BACKING))
    body = (frame_body_area() - len(boss_centers()) * hole_area - edge_cuts) * BACKING_THICKNESS_MM
    pads = sum(
        layout.polygon_signed_area(polygon) * pad_height(index)
        for index in range(CELL_COUNT)
        for polygon in pad_polygons(cell_key_center(index))
    )
    return body + pads


# FreeCAD solids.


def vertical_cutter(polygon, bottom, top):
    """A plan polygon as a prism overshooting bottom and top."""
    return plan_prism(polygon, bottom - CUT_EXTRA_MM, top + CUT_EXTRA_MM)


def build_frame_body(kind, pull_in):
    """The frame's body with every cell's footprint holes, the tabs'
    recesses and the edge cuts."""
    (x_low, x_high), (y_low, y_high) = frame_body_rectangle()
    thickness = layout.PCB_THICKNESS_MM
    body = Part.makeBox(x_high - x_low, y_high - y_low, thickness, App.Vector(x_low, y_low, 0))
    cutters = []
    for index in range(CELL_COUNT):
        key_center = cell_key_center(index)
        cutters.extend(
            hole_cutter(center, radius, thickness)
            for center, radius in cell_holes(kind, index, pull_in)
        )
        cutters.extend(
            plan_prism(tab_slot(key_center, tab), -CUT_EXTRA_MM, TAB_RECESS_DEPTH_MM)
            for tab in socket_tab_specs()
        )
    cutters.extend(vertical_cutter(cut, 0.0, thickness) for cut in edge_cut_rectangles(kind))
    body = body.cut(Part.makeCompound(cutters))
    require_one_valid_solid(body, "cutting the frame's body")
    return body.Solids[0]


def face_prism(face, depth):
    """A plan face extruded from the ceiling down to depth."""
    prism = face.extrude(UP * depth)
    prism.translate(UP * -depth)
    return prism


def build_cell_walls(key_center, fit, depth):
    """A cell's pocket walls below the ceiling, in pieces: the prism of
    the walls' outer face less that of their inner face, then their
    cutters."""
    gap = pocket_gap(fit)
    outer, inner = (face_prism(pocket_face(key_center, distance), depth)
                    for distance in (gap + WALL_THICKNESS_MM, gap))
    ring = outer.cut(inner)
    cutters = [vertical_cutter(cutter, -depth, 0.0) for cutter in wall_cutters(key_center)]
    return ring.cut(Part.makeCompound(cutters)).removeSplitter()


def build_bosses(depth):
    radius = BOSS_DIAMETER_MM / 2.0
    return [
        Part.makeCylinder(radius, depth, App.Vector(x, y, -depth), UP) for x, y in boss_centers()
    ]


def build_bores(depth, insert_length):
    radius = INSERT_BORE_DIAMETER_MM / 2.0
    bore = insert_bore_depth(insert_length)
    return [
        Part.makeCylinder(
            radius, bore + CUT_EXTRA_MM, App.Vector(x, y, -depth - CUT_EXTRA_MM), UP
        )
        for x, y in boss_centers()
    ]


def frame_walls_and_bosses(kind):
    """(walls of every cell, bosses) before fusing and before the
    footprint holes run on through the walls, for the build and for
    clearance probes."""
    depth = wall_depth()
    walls = [build_cell_walls(cell_key_center(index), cell_pocket_fit(kind, index), depth)
             for index in range(CELL_COUNT)]
    return walls, build_bosses(boss_end_depth())


def footprint_hole_bores(kind, pull_in):
    """Every cell's footprint holes from the frame's top face down to the
    walls' mouth, overshooting both."""
    depth = wall_depth()
    bores = []
    for center, radius in strip_holes(kind, pull_in):
        bore = hole_cutter(center, radius, layout.PCB_THICKNESS_MM + depth)
        bore.translate(App.Vector(0.0, 0.0, -depth))
        bores.append(bore)
    return bores


def walls_bored_volume(kind, pull_in):
    """What the footprint holes bore out of every cell's walls."""
    return wall_depth() * sum(
        sum(cell_wall_bores(kind, index, pull_in).values())
        for index in range(CELL_COUNT)
    )


def bore_footprint_holes(frame, kind, pull_in):
    """The frame with its footprint holes run on through the walls, its
    body's already cut, checked to take the walls' share from their
    plan (cell_wall_bores()) within VOLUME_RELATIVE_TOLERANCE of it (1e-5
    to 1.5e-5 mm3 at the defaults), so the holes take no boss nor more
    than a graze of one; the export checks the switch's post and pegs
    clear of the frame."""
    bored = frame.cut(Part.makeCompound(footprint_hole_bores(kind, pull_in)))
    require_one_valid_solid(bored, "boring the footprint holes through the walls")
    removed = frame.Volume - bored.Volume
    expected = walls_bored_volume(kind, pull_in)
    if abs(removed - expected) > VOLUME_RELATIVE_TOLERANCE * expected:
        raise SystemExit(
            f"error: the footprint holes take {removed:.6f} mm3 below the frame's body, the walls' "
            f"share is {expected:.6f} mm3"
        )
    return bored


def build_frame(kind, pull_in, insert_length):
    """(frame strip, its analytic volume), checked to be one valid solid
    of that volume."""
    if not 0.0 < insert_length <= longest_insert_length() + 1e-9:
        raise SystemExit(
            f"error: an insert {insert_length} long does not fit the boss, which holds up to "
            f"{longest_insert_length():.3f}"
        )
    body = build_frame_body(kind, pull_in)
    walls, bosses = frame_walls_and_bosses(kind)
    frame = body.fuse(walls + bosses).removeSplitter()
    require_one_valid_solid(frame, "fusing the walls and bosses to the frame's body")
    frame = bore_footprint_holes(frame, kind, pull_in)
    frame = frame.cut(Part.makeCompound(build_bores(boss_end_depth(), insert_length)))
    require_one_valid_solid(frame, "boring the bosses")
    expected = frame_analytic_volume(kind, pull_in, insert_length)
    if abs(frame.Volume - expected) > VOLUME_RELATIVE_TOLERANCE * expected:
        raise SystemExit(
            f"error: the {kind} strip's volume is {frame.Volume:.4f} mm3, analytic "
            f"{expected:.4f} mm3"
        )
    return frame.Solids[0], expected


def build_backing():
    """(backing strip with its bottom on z = 0, its analytic volume)."""
    (x_low, x_high), (y_low, y_high) = frame_body_rectangle()
    thickness = BACKING_THICKNESS_MM
    body = Part.makeBox(x_high - x_low, y_high - y_low, thickness, App.Vector(x_low, y_low, 0))
    radius = SCREW_CLEARANCE_HOLE_DIAMETER_MM / 2.0
    cutters = [
        Part.makeCylinder(radius, thickness + 2.0 * CUT_EXTRA_MM,
                          App.Vector(x, y, -CUT_EXTRA_MM), UP)
        for x, y in boss_centers()
    ]
    cutters.extend(vertical_cutter(cut, 0.0, thickness) for cut in edge_cut_rectangles(BACKING))
    body = body.cut(Part.makeCompound(cutters))
    pads = [
        plan_prism(polygon, thickness, thickness + pad_height(index))
        for index in range(CELL_COUNT)
        for polygon in pad_polygons(cell_key_center(index))
    ]
    backing = body.fuse(pads).removeSplitter()
    require_one_valid_solid(backing, "fusing the pads to the backing")
    expected = backing_analytic_volume()
    if abs(backing.Volume - expected) > VOLUME_RELATIVE_TOLERANCE * expected:
        raise SystemExit(
            f"error: the backing's volume is {backing.Volume:.4f} mm3, analytic "
            f"{expected:.4f} mm3"
        )
    return backing.Solids[0], expected


def stacked_backing(backing):
    """The backing under a frame strip, its top on the bosses' ends."""
    moved = backing.copy()
    moved.translate(App.Vector(0.0, 0.0, -boss_end_depth() - BACKING_THICKNESS_MM))
    return moved


# The switch hole strip (work item 012).


def switch_part_calipered_diameters():
    """{footprint-local center: the calipered diameter of the switch's
    part in that hole} for the center post and the side pegs, the first
    SWITCH_PROTRUDING_HOLE_COUNT of layout.CHOC_FOOTPRINT_HOLES_MM."""
    calipered = (SWITCH_POST_CALIPERED_DIAMETER_MM, SWITCH_PEG_CALIPERED_DIAMETER_MM,
                 SWITCH_PEG_CALIPERED_DIAMETER_MM)
    holes = layout.CHOC_FOOTPRINT_HOLES_MM[:SWITCH_PROTRUDING_HOLE_COUNT]
    return {local_center: diameter
            for (local_center, _), diameter in zip(holes, calipered, strict=True)}


def cell_switch_hole_clearance(index):
    """Cells 1 to 5's (index 0 to 4) diametral clearance as printed over
    the calipered post and pegs."""
    return FIRST_SWITCH_HOLE_CLEARANCE_MM + index * SWITCH_HOLE_CLEARANCE_STEP_MM


def modelled_switch_hole_diameter(calipered, clearance):
    """A hole that prints clearance over a calipered part, shrinking
    MEASURED_HOLE_SHRINK_PER_SIDE_MM per side."""
    return calipered + clearance + 2.0 * MEASURED_HOLE_SHRINK_PER_SIDE_MM


def printed_switch_hole_diameter(modelled):
    return modelled - 2.0 * MEASURED_HOLE_SHRINK_PER_SIDE_MM


def switch_strip_hole_radius(index, local_center, diameter, pull_in):
    """The switch hole strip's cell index's footprint hole's radius as
    modelled: the post's and pegs' printing the cell's clearance over
    the calipered parts, but the reference cell's the socket strips'
    (grown by pull_in), the pin holes SWITCH_STRIP_PIN_HOLE_DIAMETER_MM
    across, the NC pad's grown by pull_in."""
    if is_pin_hole(local_center):
        return SWITCH_STRIP_PIN_HOLE_DIAMETER_MM / 2.0
    calipered = switch_part_calipered_diameters().get(local_center)
    if calipered is None or index == SWITCH_REFERENCE_CELL_INDEX:
        return diameter / 2.0 + pull_in
    return modelled_switch_hole_diameter(calipered, cell_switch_hole_clearance(index)) / 2.0


def switch_strip_rectangle():
    """The switch hole strip's outline: its cells alone, with no bosses
    for the body to reach past. Its north edge is the frame strips', so
    turned_for_printing() places it too."""
    return (0.0, CELL_COUNT * layout.KEY_PITCH_MM), (0.0, layout.KEY_PITCH_MM)


def switch_strip_notches():
    _, (y_low, _) = switch_strip_rectangle()
    return notch_rectangles_from(y_low)


def switch_strip_analytic_volume(pull_in):
    (x_low, x_high), (y_low, y_high) = switch_strip_rectangle()
    holes = sum(math.pi * radius**2 for _center, radius in strip_holes(SWITCH, pull_in))
    notches = sum(layout.polygon_signed_area(notch) for notch in switch_strip_notches())
    return ((x_high - x_low) * (y_high - y_low) - holes - notches) * layout.PCB_THICKNESS_MM


def build_switch_strip(pull_in):
    """(switch hole strip, its analytic volume): the frame's body of the
    cells with their footprint holes and notches, checked to be one
    valid solid of that volume."""
    (x_low, x_high), (y_low, y_high) = switch_strip_rectangle()
    thickness = layout.PCB_THICKNESS_MM
    body = Part.makeBox(x_high - x_low, y_high - y_low, thickness, App.Vector(x_low, y_low, 0))
    cutters = [hole_cutter(center, radius, thickness)
               for center, radius in strip_holes(SWITCH, pull_in)]
    cutters.extend(vertical_cutter(notch, 0.0, thickness) for notch in switch_strip_notches())
    strip = body.cut(Part.makeCompound(cutters))
    require_one_valid_solid(strip, "cutting the switch hole strip")
    expected = switch_strip_analytic_volume(pull_in)
    if abs(strip.Volume - expected) > VOLUME_RELATIVE_TOLERANCE * expected:
        raise SystemExit(
            f"error: the switch hole strip's volume is {strip.Volume:.4f} mm3, analytic "
            f"{expected:.4f} mm3"
        )
    return strip.Solids[0], expected


def turned_for_printing(frame):
    """A frame strip upside down, its top face on z = 0, placed by its
    body's own faces, not by its BoundBox, which can reach past them:
    the scrapped lip strip's reached 0.05 past its top face, which
    lifted the strip off the bed."""
    turned = frame.copy()
    turned.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 180.0)
    _, (_, y_high) = frame_body_rectangle()
    turned.translate(App.Vector(0.0, y_high, layout.PCB_THICKNESS_MM))
    return turned
