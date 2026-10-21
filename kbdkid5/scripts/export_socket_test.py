"""Export one of the socket retention test strips (STL), work item 008:
a frame printed in place of the PCB, holding Kailh Choc hotswap sockets
in pockets on its underside, to try a keyboard wired by hand. Or the
switch hole strip, work item 012, the frame's body alone.

The word chooses the strip (socket_test_shape.py builds them and its
docstring has the design):

  pocket   the pocket's fit steps across the cells, -0.40 to -0.15 in
           0.05 steps, the two pin holes 3.5 across as modelled so the
           pocket alone locates the socket; any pocket can be glued
  backing  screwed under either frame strip with M2 screws into
           heat-set inserts in the frame's bosses, a pad under each
           socket lobe whose top relative to the socket's bottom steps
           from -0.10 (a gap) to +0.15 (pressing) in 0.05 steps
  holes    every pocket loose (+0.15), the two pin holes stepping 3.5 to
           3.0 across as modelled in 0.1 steps, so only they hold the
           socket
  switch   the switch hole strip: no pockets or bosses, the center
           post's and side pegs' holes printing -0.05 to +0.15 over the
           calipered post and pegs in cells 1 to 5, cell 6 the socket
           strips' holes, the pin holes 3.2 so only the post and pegs
           hold the switch

Cell k (from 1, west to east) has k notches in its south edge on every
strip; the pocket strip also has five in its north edge, one at every
cell boundary, the hole strip three, between cells 1 and 2, 3 and 4,
and 5 and 6. The frame strips and the switch hole strip print upside
down, the frame's top face on z = 0; the backing prints bottom down.

Runs headless under FreeCAD's console interpreter (see
freecad_common.py for the freecadcmd quirks that shape the
invocation):

    freecadcmd kbdkid5/scripts/export_socket_test.py --pass <strip.stl> pocket|backing|holes|switch
        [pull_in=0.2] [insert_length=<mm>]

A frame strip is checked for one valid solid of its analytic volume,
each pocket's walls at its fit's gap outside every straight face of the
socket's outline they keep, on all four sides, so the pocket is its fit
as printed around the body, the walls' depth, the tab slots' width,
the pin holes' size, the footprint holes through the walls (the
switch's post and pegs clear of the frame, only the west peg's hole
boring a wall, lobe B's north wall open on it and whole beside it, the
sliver of the wall the hole leaves), every bore on its boss at the
insert's depth, the tab recesses' and the bosses' clearances, the
notches and the marks, and a closed mesh. The backing is checked for
one valid solid of its analytic volume, each pad's height against the
socket's bottom and its place under the socket's outline, the screw
holes, and stacked under the pocket strip: nothing overlapping, the
backing touching only the bosses' ends, the pads' distance to the
walls, clear of them as printed, every bore over its screw hole, the
tabs' wire rooms clear, and the battery clearance in the real tray,
the backing's and its screw heads'. It also prints where the backing
and the heads stand over the nice!nano's socket strips, which only
states a constraint on a real frame: the heads come below the strips'
tops, so its backing screws must keep off the strips in plan.
The switch hole strip is checked for one valid solid of its analytic
volume, every footprint hole of every cell measured off its faces (one
cylinder from the top face to the underside, at its size as built and
at the hand-worked figures below), and it prints each cell's post and
peg holes as modelled and as printed by the measured shrink with their
clearance over the calipered post and pegs, the pin holes against the
blades, the least plastic between two holes of each cell (measured,
at least MINIMUM_HOLE_WEB_MM) and the notches per cell.
Every strip's mesh must have its lowest point on z = 0, the bed.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App
import Part

import layout
import pcb_shape
import socket_test_shape as shape
from freecad_common import check_closed_mesh, export_stl, run_and_exit, script_arguments
from tray_shape import UP, layout_polygon_wire, plan_prism

# DESIGN.md's figures ("Hand-wired frame test"), transcribed
# independently of the constants the strips are built from, each
# compared within half its last digit.
DESIGN_POCKET_FITS_MM = (-0.40, -0.35, -0.30, -0.25, -0.20, -0.15)
DESIGN_POCKET_PRINTED_X_MM = (9.15, 9.20, 9.25, 9.30, 9.35, 9.40)
DESIGN_POCKET_PRINTED_Y_MM = (6.45, 6.50, 6.55, 6.60, 6.65, 6.70)
DESIGN_POCKET_PIN_HOLE_DIAMETER_MM = 3.50
DESIGN_HOLE_STRIP_HOLES_MM = (3.50, 3.40, 3.30, 3.20, 3.10, 3.00)
DESIGN_HOLE_STRIP_POCKET_FIT_MM = 0.15
DESIGN_HOLE_STRIP_POCKET_PRINTED_MM = (9.70, 7.00)
DESIGN_PAD_OFFSETS_MM = (-0.10, -0.05, 0.00, 0.05, 0.10, 0.15)
DESIGN_WALL_DEPTHS_MM = {shape.POCKET: 1.80, shape.HOLES: 1.80}
DESIGN_TAB_SLOT_WIDTH_MM = 3.18
DESIGN_BOSS_HEIGHT_MM = 3.87
DESIGN_LONGEST_INSERT_MM = 3.067
DESIGN_BACKING_THICKNESS_MM = 0.80
DESIGN_BATTERY_CLEARANCE_AS_PRINTED_MM = 2.27
DESIGN_SCREW_HEADS_OVER_BATTERY_PRINTED_MM = 0.77  # the backing's, 1.5 tall
DESIGN_STRIP_MARK_XS_MM = {shape.POCKET: (19.05, 38.10, 57.15, 76.20, 95.25),
                           shape.HOLES: (19.05, 57.15, 95.25)}
DESIGN_FIGURE_DECIMALS = 2

# The switch hole strip's figures (work item 012), worked out by hand
# from the user's calipered post (3.17) and pegs (1.65), the clearances
# as printed and the 0.15 per side a hole prints smaller than modelled,
# compared like DESIGN.md's above: cells 1 to 5's clearance as printed
# and their post's and pegs' holes as modelled, and the pin holes as
# modelled. Cell 6's post and pegs and every cell's NC pad hole are
# checked against the pocket strip's, which follow pull_in.
DESIGN_SWITCH_HOLE_CLEARANCES_MM = (-0.05, 0.00, 0.05, 0.10, 0.15)
DESIGN_SWITCH_POST_HOLES_MM = (3.42, 3.47, 3.52, 3.57, 3.62)
DESIGN_SWITCH_PEG_HOLES_MM = (1.90, 1.95, 2.00, 2.05, 2.10)
DESIGN_SWITCH_PIN_HOLE_DIAMETER_MM = 3.20

# The footprint's holes as the switch hole strip's report names them, in
# layout.CHOC_FOOTPRINT_HOLES_MM's order (the footprint is turned 90
# degrees, its +y along the board's -x), the pins' as the slit test
# strip names them.
SWITCH_STRIP_HOLE_NAMES = ("post", "west peg", "east peg", "peg-side pin", "middle pin",
                           "NC pad")
# The least plastic the switch hole strip keeps between two holes of a
# cell as modelled: two lines.
MINIMUM_HOLE_WEB_MM = 0.8

# Clearances the checks ask for, as modelled: the bosses from the walls,
# the tabs' wire rooms, the switch's protruding parts and the footprint
# holes. The tabs' recesses in the ceiling start at the body's ends,
# where the tabs, 0.05 taller than the body's bumps, leave it, which
# brings the south tab's within 0.5 of its pin hole: they keep
# RECESS_HOLE_CLEARANCE_MM, more as printed, where the hole and the
# recess each print 0.2 smaller. The walls and bosses beside the wire
# rooms must stay out of them as printed.
FEATURE_CLEARANCE_MM = 0.5
RECESS_HOLE_CLEARANCE_MM = 0.3
WIRE_ROOM_PRINTED_CLEARANCE_MM = layout.PRINT_SWELLING_PER_SIDE_MM

# How the switch's center post and side pegs reach below the frame's
# body (DESIGN.md, "Fused mock").
SWITCH_PARTS_BELOW_FRAME_BODY_MM = 1.4

# The center post's and the west peg's holes, by their footprint-local
# centers (layout.CHOC_FOOTPRINT_HOLES_MM): the peg's bores lobe B's
# north wall, and DESIGN.md says no other hole meets a wall. That wall
# is probed solid at these footprint-local y at its mid depth: beside
# the hole, where the wall was cut back before the holes ran through it
# (4.0, 7.0), and farther along (3.0, around lobe B's round, and 7.3).
CENTER_POST_HOLE_MM = layout.CHOC_FOOTPRINT_HOLES_MM[0][0]
WEST_PEG_HOLE_MM = layout.CHOC_FOOTPRINT_HOLES_MM[1][0]
WALL_PROBE_LOCAL_YS_MM = (3.0, 4.0, 7.0, 7.3)

# The stack's contact check sinks the frame this far into the backing.
CONTACT_PROBE_DEPTH_MM = 0.01
CONTACT_VOLUME_RELATIVE_TOLERANCE = 1e-4
MEASURE_TOLERANCE_MM = 1e-6
# A thickness measured between two edges, each found by bisection
# within isInside()'s tolerance.
THICKNESS_TOLERANCE_MM = 3.0 * MEASURE_TOLERANCE_MM
# Where a hole leaves no sliver of a wall, the probe that the hole is
# open at the wall's inner face sits this far inside the hole: on the
# face itself it would lie on the hole's edge at a sliver of exactly
# zero, which isInside counts as solid.
OPEN_PROBE_STEP_MM = 0.01
WINDOW_MM = 0.5

USAGE = f"""\
usage: freecadcmd kbdkid5/scripts/export_socket_test.py --pass <strip.stl> pocket|backing|holes|switch
           [pull_in={pcb_shape.DEFAULT_PULL_IN_MM}] [insert_length=<mm>]

  pocket         the pocket strip, its pocket's fit stepping across the cells
  backing        the backing strip, its pads' height stepping across the cells
  holes          the hole strip, its pin holes stepping across the cells
  switch         the switch hole strip, its post's and pegs' holes stepping
                 across the cells
  pull_in        swelling allowance per side, mm: the footprint holes grow by it
                 (all but the pin holes, 3.5 as modelled on the pocket strip,
                 stepping on the hole strip, 3.2 on the switch hole strip, and
                 the switch hole strip's post and pegs but in its cell 6)
  insert_length  the heat-set inserts' length, mm, which sets the bores' depth:
                 at most (and by default) the longest the bosses hold,
                 {shape.longest_insert_length():.3f}\
"""


class Arguments:
    def __init__(self):
        self.stl_file = None
        self.kind = None
        self.pull_in = pcb_shape.DEFAULT_PULL_IN_MM
        self.insert_length = shape.longest_insert_length()


def parse_number(key, value):
    try:
        return float(value)
    except ValueError:
        raise SystemExit(f"error: '{key}' needs a number, got '{value}'")


def parse_arguments(argument_list):
    arguments = Arguments()
    positionals = []
    for argument in argument_list:
        if "=" in argument:
            key, _, value = argument.partition("=")
            if key not in ("pull_in", "insert_length"):
                raise SystemExit(f"error: unknown option '{key}'\n{USAGE}")
            setattr(arguments, key, parse_number(key, value))
        elif argument in shape.STRIP_KINDS:
            if arguments.kind is not None:
                raise SystemExit(f"error: choose one strip\n{USAGE}")
            arguments.kind = argument
        else:
            positionals.append(argument)
    if len(positionals) != 1 or arguments.kind is None:
        raise SystemExit(USAGE)
    arguments.stl_file = positionals[0]
    return arguments


def design_tolerance():
    return 0.5 * 10.0**-DESIGN_FIGURE_DECIMALS + MEASURE_TOLERANCE_MM


def require_design(what, measured, design):
    if abs(measured - design) > design_tolerance():
        raise SystemExit(f"error: {what} is {measured:.4f}, DESIGN.md says {design:.2f}")


# Faces.


def planar_faces_along(solid, axis_index):
    """The solid's planar faces whose normal lies along an axis (0 x, 1
    y, 2 z)."""
    faces = []
    for face in solid.Faces:
        if isinstance(face.Surface, Part.Plane):
            normal = face.Surface.Axis
            if abs((normal.x, normal.y, normal.z)[axis_index]) > 0.999:
                faces.append(face)
    return faces


def face_coordinate(face, axis_index):
    center = face.CenterOfMass
    return (center.x, center.y, center.z)[axis_index]


def face_normal(face):
    """A face's normal at its parameter range's middle, out of the
    solid."""
    u_low, u_high, v_low, v_high = face.ParameterRange
    return face.normalAt((u_low + u_high) / 2.0, (v_low + v_high) / 2.0)


def upward(face):
    return face_normal(face).z > 0.0


def vertical_planar_faces(solid):
    return [face for face in solid.Faces
            if isinstance(face.Surface, Part.Plane) and abs(face.Surface.Axis.z) < 1e-6]


def socket_extents(key_center):
    """(x range, y range) of the socket's plastic body: between its end
    faces (layout.HOTSWAP_SOCKET_BODY_ENDS_MM) and between its outline's
    two outermost faces across them."""
    local_xs = [x for x, _ in shape.outline_local_points()]
    corners = [layout.footprint_point(key_center, (x, end))
               for x in (min(local_xs), max(local_xs))
               for end in layout.HOTSWAP_SOCKET_BODY_ENDS_MM]
    xs = [x for x, _ in corners]
    ys = [y for _, y in corners]
    return (min(xs), max(xs)), (min(ys), max(ys))


def outline_straight_edges(key_center):
    """The socket outline's straight edges in plan as (start, unit
    direction, length, unit normal out of the body)."""
    outline = shape.outline_face(key_center)
    edges = []
    for edge in outline.Edges:
        if not isinstance(edge.Curve, Part.Line):
            continue
        start, end = edge.Vertexes[0].Point, edge.Vertexes[-1].Point
        length = (end - start).Length
        along = (end - start) * (1.0 / length)
        outward = App.Vector(along.y, -along.x, 0.0)
        if outline.isInside((start + end) * 0.5 + outward * OPEN_PROBE_STEP_MM,
                            MEASURE_TOLERANCE_MM, True):
            outward = outward * -1.0
        edges.append((start, along, length, outward))
    return edges


def wall_face_gap(faces, key_center, edge):
    """How far the pocket walls' inner face along a straight edge of the
    socket's outline lies outside it, None where the cuts took that face
    whole: the nearest of the frame's vertical planar faces below the
    ceiling within the cell that face the edge from its outer side,
    within WINDOW_MM of it, and lie along it within WINDOW_MM of its
    ends."""
    start, along, length, outward = edge
    gaps = []
    for face in faces:
        center = face.CenterOfMass
        if (center.z >= 0.0 or abs(center.x - key_center[0]) > layout.KEY_PITCH_MM / 2.0
                or face_normal(face).dot(outward) > -0.999):
            continue
        gap = (center - start).dot(outward)
        positions = [(vertex.Point - start).dot(along) for vertex in face.Vertexes]
        if (-MEASURE_TOLERANCE_MM <= gap <= WINDOW_MM and min(positions) >= -WINDOW_MM
                and max(positions) <= length + WINDOW_MM):
            gaps.append(gap)
    return min(gaps) if gaps else None


def measured_pocket(faces, key_center):
    """[(the edge's outward normal, the gap)] of each straight edge of a
    cell's socket outline whose walls' inner face is left."""
    measured = []
    for edge in outline_straight_edges(key_center):
        gap = wall_face_gap(faces, key_center, edge)
        if gap is not None:
            measured.append((edge[3], gap))
    return measured


def faces_every_side(measured):
    """Whether the measured faces bound the pocket on all four sides."""
    normals = [normal for normal, _ in measured]
    return all(any(normal.x * side_x + normal.y * side_y > 0.5 for normal in normals)
               for side_x, side_y in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)))


def design_pocket_size(kind, index):
    """DESIGN.md's pocket as printed."""
    if kind == shape.HOLES:
        return DESIGN_HOLE_STRIP_POCKET_PRINTED_MM
    return DESIGN_POCKET_PRINTED_X_MM[index], DESIGN_POCKET_PRINTED_Y_MM[index]


def check_pockets(kind, frame):
    """Each pocket's walls from their inner faces: at the fit's gap
    outside every straight face of the socket's outline the cuts leave
    them, on all four sides, so the pocket is the fit's size around the
    body between its end faces and its outermost faces across them."""
    swelling = 2.0 * layout.PRINT_SWELLING_PER_SIDE_MM
    faces = vertical_planar_faces(frame)
    edge_count = len(outline_straight_edges(shape.cell_key_center(0)))
    for index in range(shape.CELL_COUNT):
        key_center = shape.cell_key_center(index)
        fit = shape.cell_pocket_fit(kind, index)
        measured = measured_pocket(faces, key_center)
        if not faces_every_side(measured):
            raise SystemExit(f"error: cell {index + 1}'s walls keep their inner face on only "
                             f"{len(measured)} of the outline's straight faces, not on all sides")
        expected = shape.pocket_gap(fit)
        worst = max(abs(gap - expected) for _, gap in measured)
        if worst > MEASURE_TOLERANCE_MM:
            raise SystemExit(f"error: cell {index + 1}'s walls stand up to {worst:.6f} off the "
                             f"gap {expected:.4f} of the fit {fit:+.2f}")
        gap = sum(gap for _, gap in measured) / len(measured)
        (x_low, x_high), (y_low, y_high) = socket_extents(key_center)
        x_size, y_size = x_high - x_low + 2.0 * gap, y_high - y_low + 2.0 * gap
        design = design_pocket_size(kind, index)
        require_design(f"cell {index + 1}'s pocket along x as printed", x_size - swelling,
                       design[0])
        require_design(f"cell {index + 1}'s pocket along y as printed", y_size - swelling,
                       design[1])
        if kind == shape.POCKET:
            require_design(f"cell {index + 1}'s fit", fit, DESIGN_POCKET_FITS_MM[index])
        if kind == shape.HOLES:
            require_design(f"cell {index + 1}'s fit", fit, DESIGN_HOLE_STRIP_POCKET_FIT_MM)
        print(f"cell {index + 1}:     pocket fit {fit:+.2f}, walls {gap:.4f} outside the outline "
              f"on {len(measured)} of its {edge_count} straight faces (within {worst:.1e}), "
              f"{x_size:.3f} x {y_size:.3f} modelled, {x_size - swelling:.3f} x "
              f"{y_size - swelling:.3f} printed")


def check_wall_depth(kind, frame):
    mouths = [face for face in planar_faces_along(frame, 2)
              if not upward(face) and face_coordinate(face, 2) < -MEASURE_TOLERANCE_MM]
    depths = sorted({round(-face_coordinate(face, 2), 6) for face in mouths})
    walls = shape.wall_depth()
    expected = sorted({walls, shape.boss_end_depth()})
    if len(depths) != len(expected) or any(
            abs(found - wanted) > MEASURE_TOLERANCE_MM for found, wanted in zip(depths, expected)):
        raise SystemExit(f"error: the walls' and bosses' mouths lie at {depths} below the "
                         f"ceiling, expected {expected}")
    require_design("the walls' depth", walls, DESIGN_WALL_DEPTHS_MM[kind])
    print(f"walls:      {shape.WALL_THICKNESS_MM} thick, {walls:.3f} deep below the ceiling "
          f"(the socket's body {shape.socket_height()}), mouths at {sorted(depths)}")


def first_solid(solid, start, direction, length):
    """How far from start along a unit direction the solid begins, open
    at start and solid at length, by bisection."""
    def at(distance):
        return solid.isInside(start + direction * distance, MEASURE_TOLERANCE_MM, True)

    if at(0.0) or not at(length):
        raise SystemExit(f"error: no edge to measure from {start} along {direction}")
    low, high = 0.0, length
    for _ in range(24):
        middle = (low + high) / 2.0
        low, high = (low, middle) if at(middle) else (middle, high)
    return high


def require_open(solid, point, what):
    if solid.isInside(point, MEASURE_TOLERANCE_MM, True):
        raise SystemExit(f"error: {what} is not open at {point}")


def require_solid(solid, point, what):
    if not solid.isInside(point, MEASURE_TOLERANCE_MM, True):
        raise SystemExit(f"error: {what} is missing at {point}")


def check_tab_slots(kind, frame):
    """Probe each slot at the walls' middle: open across its width, the
    wall present just past both sides."""
    depth = shape.wall_depth()
    for index in range(shape.CELL_COUNT):
        key_center = shape.cell_key_center(index)
        gap = shape.pocket_gap(shape.cell_pocket_fit(kind, index))
        for x_center, width, face, tip in shape.socket_tab_specs():
            half = shape.tab_slot_width(width) / 2.0
            in_wall = face + math.copysign(gap + shape.WALL_THICKNESS_MM / 2.0, tip - face)
            for across, open_expected in ((0.0, True), (half - 0.01, True), (-half + 0.01, True),
                                          (half + 0.01, False), (-half - 0.01, False)):
                x, y = layout.footprint_point(key_center, (x_center + across, in_wall))
                point = App.Vector(x, y, -depth / 2.0)
                (require_open if open_expected else require_solid)(
                    frame, point, f"cell {index + 1}'s tab slot")
    width = shape.tab_slot_width(shape.socket_tab_specs()[0][1])
    require_design("the tab slots' width", width, DESIGN_TAB_SLOT_WIDTH_MM)
    printed = width - 2.0 * layout.PRINT_SWELLING_PER_SIDE_MM
    print(f"tab slots:  {width:.3f} wide modelled, {printed:.3f} printed, for the "
          f"{shape.socket_tab_specs()[0][1]:.2f} tab with {shape.TAB_SOLDER_PER_SIDE_MM} of "
          f"solder each side, from the body's ends; recess {shape.TAB_RECESS_DEPTH_MM} deep "
          f"({shape.TAB_RECESS_DEPTH_MM - layout.PRINT_RISE_OF_UP_FACING_BOTTOMS_MM:.1f} printed) "
          f"to {shape.TAB_RECESS_PAST_TIP_MM} past the tip")


def bore_faces(solid, radius):
    """{(x, y): (bottom z, top z)} of the solid's vertical cylinders of
    a radius that reach below the ceiling."""
    bores = {}
    for face in solid.Faces:
        surface = face.Surface
        if (isinstance(surface, Part.Cylinder)
                and abs(surface.Radius - radius) < MEASURE_TOLERANCE_MM
                and abs(surface.Axis.z) > 0.999):
            key = (round(surface.Center.x, 6), round(surface.Center.y, 6))
            box = face.BoundBox
            low, high = bores.get(key, (box.ZMin, box.ZMax))
            bores[key] = (min(low, box.ZMin), max(high, box.ZMax))
    return bores


def require_on_boss_centers(centers, what):
    expected = {(round(x, 6), round(y, 6)) for x, y in shape.boss_centers()}
    if set(centers) != expected:
        raise SystemExit(f"error: {len(centers)} {what}, not one on each of the "
                         f"{len(expected)} bosses")


def check_bores(frame, insert_length):
    bores = bore_faces(frame, shape.INSERT_BORE_DIAMETER_MM / 2.0)
    bores = {center: span for center, span in bores.items() if span[0] < -MEASURE_TOLERANCE_MM}
    require_on_boss_centers(bores, "insert bores")
    end_depth = shape.boss_end_depth()
    for low, high in bores.values():
        if (abs(low + end_depth) > MEASURE_TOLERANCE_MM
                or abs(high - low - shape.insert_bore_depth(insert_length)) > MEASURE_TOLERANCE_MM):
            raise SystemExit(f"error: a bore runs from z {low:.4f} to {high:.4f}")
    require_design("the bosses' height", shape.boss_height(), DESIGN_BOSS_HEIGHT_MM)
    require_design("the longest insert", shape.longest_insert_length(), DESIGN_LONGEST_INSERT_MM)
    floor = layout.PCB_THICKNESS_MM - (insert_length - end_depth
                                       + layout.PRINT_RISE_OF_UP_FACING_BOTTOMS_MM)
    print(f"bosses:     {len(bores)}, {shape.BOSS_DIAMETER_MM} across, {shape.boss_height():.3f} "
          f"tall from the frame's top, bored {shape.INSERT_BORE_DIAMETER_MM} for an insert "
          f"{insert_length:.3f} long ({shape.insert_bore_depth(insert_length):.3f} deep, its "
          f"bottom rising {layout.PRINT_RISE_OF_UP_FACING_BOTTOMS_MM} as printed), floor "
          f"{floor:.3f}; the longest insert they hold {shape.longest_insert_length():.3f}")


def measured_pin_holes(frame, index, radius):
    """The centers of cell index's vertical cylinders of a radius that
    run through the frame's body, its top face to the ceiling."""
    key_x, _ = shape.cell_key_center(index)
    return {center for center, (low, high) in bore_faces(frame, radius).items()
            if abs(low) < MEASURE_TOLERANCE_MM
            and abs(high - layout.PCB_THICKNESS_MM) < MEASURE_TOLERANCE_MM
            and abs(center[0] - key_x) < layout.KEY_PITCH_MM / 2.0}


def design_pin_hole(kind, index):
    """DESIGN.md's pin holes as modelled, or None where they follow
    from pull_in."""
    if kind == shape.POCKET:
        return DESIGN_POCKET_PIN_HOLE_DIAMETER_MM
    if kind == shape.HOLES:
        return DESIGN_HOLE_STRIP_HOLES_MM[index]
    return None


def check_pin_holes(kind, frame, pull_in):
    """The two holes the socket's bosses sit in, in every cell, through
    the frame's body at the cell's size."""
    local = layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM[0]
    diameters = []
    for index in range(shape.CELL_COUNT):
        radius = shape.hole_radius(kind, index, local, dict(layout.CHOC_FOOTPRINT_HOLES_MM)[local],
                                   pull_in)
        expected = {(round(x, 6), round(y, 6))
                    for x, y in (layout.footprint_point(shape.cell_key_center(index), center)
                                 for center in layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM)}
        found = measured_pin_holes(frame, index, radius)
        if found != expected:
            raise SystemExit(f"error: cell {index + 1} has {len(found)} pin holes "
                             f"{2.0 * radius:.3f} across through the frame's body, expected "
                             f"{len(expected)}")
        design = design_pin_hole(kind, index)
        if design is not None:
            require_design(f"cell {index + 1}'s pin holes", 2.0 * radius, design)
        diameters.append(2.0 * radius)
    swelling = 2.0 * layout.PRINT_SWELLING_PER_SIDE_MM
    print(f"pin holes:  {2 * shape.CELL_COUNT}, cells 1 to {shape.CELL_COUNT} "
          + ", ".join(f"{diameter:.3f}" for diameter in diameters) + " across modelled, "
          + ", ".join(f"{diameter - swelling:.3f}" for diameter in diameters) + " printed")


def switch_part_columns(key_center):
    """The switch's center post and side pegs below the frame's body,
    their holes' nominal size plus the walls' swelling."""
    columns = []
    holes = layout.footprint_holes(key_center)[: shape.SWITCH_PROTRUDING_HOLE_COUNT]
    for (x, y), diameter in holes:
        radius = diameter / 2.0 + layout.PRINT_SWELLING_PER_SIDE_MM
        columns.append(Part.makeCylinder(radius, SWITCH_PARTS_BELOW_FRAME_BODY_MM,
                                         App.Vector(x, y, -SWITCH_PARTS_BELOW_FRAME_BODY_MM), UP))
    return columns


def switch_hole_columns(kind, pull_in):
    """The switch's center post and side pegs at their holes' size as
    modelled, from SWITCH_PARTS_BELOW_FRAME_BODY_MM below the frame's
    body up through it."""
    height = SWITCH_PARTS_BELOW_FRAME_BODY_MM + layout.PCB_THICKNESS_MM
    return [
        Part.makeCylinder(radius, height, App.Vector(x, y, -SWITCH_PARTS_BELOW_FRAME_BODY_MM), UP)
        for index in range(shape.CELL_COUNT)
        for (x, y), radius in shape.cell_holes(kind, index, pull_in)[
            : shape.SWITCH_PROTRUDING_HOLE_COUNT]
    ]


def measured_sliver(frame, at, inner, hole_center, radius, expected):
    """The sliver of a wall's inner side between its inner face, at
    footprint-local x `inner`, and a hole's edge, along the footprint's
    x through the hole's center, where it is thinnest: from the pocket
    to the face and from the hole's center to its edge. at(local x,
    local y) gives the probe point."""
    local_x, local_y = hole_center
    start = at(inner - WINDOW_MM, local_y)
    outward = at(inner, local_y) - start
    outward.normalize()
    face = first_solid(frame, start, outward, WINDOW_MM + expected / 2.0)
    edge = first_solid(frame, at(local_x, local_y), outward * -1.0, radius + expected / 2.0)
    return (local_x - edge) - (inner - WINDOW_MM + face)


def check_holes_through_walls(kind, frame, pull_in):
    """The footprint holes through the walls: the switch's post and pegs
    at their holes' size clear of the frame, only the west peg's hole
    boring a wall in the walls' plan, open through lobe B's north wall
    at its mid depth in the wall's middle on the hole's center line (the
    hole's axis itself lies outside the wall's outer face), the wall
    whole along it, and the sliver of its inner side the hole leaves,
    measured where it is thinnest, or the hole open OPEN_PROBE_STEP_MM
    past the inner face where none is left (on the face itself the probe
    would sit on the hole's edge at a sliver of exactly zero)."""
    overlap = frame.common(Part.makeCompound(switch_hole_columns(kind, pull_in))).Volume
    if overlap > MEASURE_TOLERANCE_MM:
        raise SystemExit(f"error: the switch's post and pegs overlap the {kind} strip by "
                         f"{overlap:.6f} mm3")
    post, peg = CENTER_POST_HOLE_MM, WEST_PEG_HOLE_MM
    lobe_x = max(x for x, _ in shape.outline_local_points())
    middle_z = -shape.wall_depth() / 2.0
    slivers = []
    bores = []
    for index in range(shape.CELL_COUNT):
        key_center = shape.cell_key_center(index)

        def at(local_x, local_y):
            return App.Vector(*layout.footprint_point(key_center, (local_x, local_y)), middle_z)

        holes = {local_center: hole for (local_center, _), hole in zip(
            layout.CHOC_FOOTPRINT_HOLES_MM, shape.cell_holes(kind, index, pull_in))}
        radius = holes[peg][1]
        inner = lobe_x + shape.pocket_gap(shape.cell_pocket_fit(kind, index))
        wall_middle = inner + shape.WALL_THICKNESS_MM / 2.0
        what = f"cell {index + 1}'s lobe B north wall"
        require_open(frame, at(wall_middle, peg[1]), f"{what} on the west peg's hole")
        for local_y in WALL_PROBE_LOCAL_YS_MM:
            require_solid(frame, at(wall_middle, local_y), what)
        expected = peg[0] - radius - inner
        if expected > MEASURE_TOLERANCE_MM:
            sliver = measured_sliver(frame, at, inner, peg, radius, expected)
            if abs(sliver - expected) > THICKNESS_TOLERANCE_MM:
                raise SystemExit(f"error: {what}'s sliver is {sliver:.6f}, expected "
                                 f"{expected:.6f}")
        else:
            require_open(frame, at(inner + OPEN_PROBE_STEP_MM, peg[1]),
                         f"{what}'s inner face on the west peg's hole")
            sliver = expected
        slivers.append(sliver)
        area = shape.cell_wall_bores(kind, index, pull_in)
        if set(area) != {peg}:
            raise SystemExit(f"error: cell {index + 1}'s walls are bored by the holes at "
                             f"{sorted(area)}, not by the west peg's alone")
        post_hole = shape.circle_face(*holes[post])
        post_gap = shape.cell_walls_plan(kind, index).distToShape(post_hole)[0]
        bores.append((area[peg], area.get(post, 0.0), post_gap))
    probes = ", ".join(f"{local_y:.1f}" for local_y in WALL_PROBE_LOCAL_YS_MM)
    print(f"holes:      every footprint hole through the frame's body and the walls to their "
          f"mouth; the switch's post and pegs at their holes' size, "
          f"{SWITCH_PARTS_BELOW_FRAME_BODY_MM} below the frame's body, overlap the frame by "
          f"{overlap:.1e} mm3; cells 1 to {shape.CELL_COUNT}'s walls "
          "bored " + ", ".join(f"{peg_area:.3f}" for peg_area, _, _ in bores) + " mm2 by the "
          "west peg's hole and by no other, " + ", ".join(
              f"{post_area:.3f}" for _, post_area, _ in bores) + " mm2 by the center post's, "
          "which keeps " + ", ".join(f"{post_gap:.3f}" for _, _, post_gap in bores) + " from "
          f"them; lobe B's north wall open through its middle on the peg's hole, solid at "
          f"footprint-local y {probes}, all at its mid depth")
    print(f"sliver:     lobe B's north wall's inner face to the west peg's hole, cells 1 to "
          f"{shape.CELL_COUNT} " + ", ".join(f"{sliver:.3f}" for sliver in slivers)
          + " (measured where positive; negative, the hole reaches past the face into the "
          "pocket)")


def wire_room_boxes(bottom, top):
    return [
        plan_prism(shape.tab_wire_room(shape.cell_key_center(index), tab), bottom, top)
        for index in range(shape.CELL_COUNT)
        for tab in shape.socket_tab_specs()
    ]


def least_distance(first, second):
    return Part.makeCompound(first).distToShape(Part.makeCompound(second))[0]


def require_clearance(what, distance, least):
    if distance < least - MEASURE_TOLERANCE_MM:
        raise SystemExit(f"error: {what} keep {distance:.4f}, less than {least}")
    return distance


def check_frame_clearances(kind, pull_in):
    walls, bosses = shape.frame_walls_and_bosses(kind)
    columns = [column for index in range(shape.CELL_COUNT)
               for column in switch_part_columns(shape.cell_key_center(index))]
    rooms = wire_room_boxes(-shape.boss_end_depth(), 0.0)
    recesses = []
    holes = []
    for index in range(shape.CELL_COUNT):
        key_center = shape.cell_key_center(index)
        recesses.extend(plan_prism(shape.tab_slot(key_center, tab), 0.0, shape.TAB_RECESS_DEPTH_MM)
                        for tab in shape.socket_tab_specs())
        holes.extend(shape.hole_cutter(center, radius, layout.PCB_THICKNESS_MM)
                     for center, radius in shape.cell_holes(kind, index, pull_in))
    recess_web = require_clearance("the tabs' recesses from the footprint holes",
                                   least_distance(recesses, holes), RECESS_HOLE_CLEARANCE_MM)
    tab_count, hole_count = len(shape.socket_tab_specs()), len(layout.CHOC_FOOTPRINT_HOLES_MM)
    cell_webs = [least_distance(recesses[index * tab_count:(index + 1) * tab_count],
                                holes[index * hole_count:(index + 1) * hole_count])
                 for index in range(shape.CELL_COUNT)]
    print(f"recesses:   {recess_web:.3f} from the footprint holes as modelled, "
          f"{recess_web + 2.0 * layout.PRINT_SWELLING_PER_SIDE_MM:.3f} as printed; cells 1 to "
          f"{shape.CELL_COUNT} " + ", ".join(f"{web:.3f}" for web in cell_webs) + " as modelled")
    figures = [
        ("bosses from the walls", least_distance(bosses, walls)),
        ("bosses from the wire rooms", least_distance(bosses, rooms)),
        ("bosses from the switch's post and pegs", least_distance(bosses, columns)),
        ("bosses from the footprint holes", least_distance(bosses, holes)),
    ]
    for what, distance in figures:
        require_clearance(what, distance, FEATURE_CLEARANCE_MM)
    print("clearances: " + ", ".join(f"{what} {distance:.3f}" for what, distance in figures))


def check_notches(strip, z):
    _, (y_low, _) = shape.frame_body_rectangle()
    check_notches_from(strip, y_low, z)


def check_notches_from(strip, south_y, z):
    """Cell k (from 1) open at its first k notch places in a south edge
    at south_y and solid at the others."""
    for index in range(shape.CELL_COUNT):
        for number, x in enumerate(shape.notch_x_centers(index), start=1):
            point = App.Vector(x, south_y + shape.NOTCH_DEPTH_MM / 2.0, z)
            if strip.isInside(point, MEASURE_TOLERANCE_MM, True) != (number > index + 1):
                raise SystemExit(f"error: cell {index + 1} has the wrong notches")


def check_marks(kind, frame):
    """The strip's marks at DESIGN.md's places, its north edge open at
    them and solid at every other strip's that is not also its own (the
    hole strip's three are among the pocket strip's five)."""
    _, (_, y_high) = shape.frame_body_rectangle()
    own = shape.strip_mark_xs(kind)
    design = DESIGN_STRIP_MARK_XS_MM[kind]
    if len(own) != len(design):
        raise SystemExit(f"error: the {kind} strip has {len(own)} marks, DESIGN.md says "
                         f"{len(design)}")
    for x, design_x in zip(own, design):
        require_design(f"the {kind} strip's mark", x, design_x)
    for x in sorted({x for mark_kind in shape.STRIP_KINDS for x in shape.strip_mark_xs(mark_kind)}):
        point = App.Vector(x, y_high - shape.MARK_DEPTH_MM / 2.0,
                           layout.PCB_THICKNESS_MM / 2.0)
        if frame.isInside(point, MEASURE_TOLERANCE_MM, True) == (x in own):
            raise SystemExit(f"error: the {kind} strip's north edge is wrong at x {x:.2f}")


def export_frame(arguments):
    kind = arguments.kind
    frame, expected = shape.build_frame(kind, arguments.pull_in, arguments.insert_length)
    (x_low, x_high), (y_low, y_high) = shape.frame_body_rectangle()
    print(f"strip:      {kind}, {shape.CELL_COUNT} cells at {layout.KEY_PITCH_MM} pitch, the "
          f"frame's body {x_high - x_low:.3f} x {y_high - y_low:.3f} x {layout.PCB_THICKNESS_MM}, "
          f"footprint holes grown by {arguments.pull_in}")
    print(f"volume:     {frame.Volume:.3f} mm3 (analytic {expected:.3f} mm3)")
    check_pockets(kind, frame)
    check_wall_depth(kind, frame)
    check_tab_slots(kind, frame)
    check_pin_holes(kind, frame, arguments.pull_in)
    check_holes_through_walls(kind, frame, arguments.pull_in)
    check_bores(frame, arguments.insert_length)
    check_frame_clearances(kind, arguments.pull_in)
    check_notches(frame, layout.PCB_THICKNESS_MM / 2.0)
    check_marks(kind, frame)
    marks = ", ".join(f"{x:.2f}" for x in shape.strip_mark_xs(kind))
    print(f"notches:    cell k has k in the south edge; marks in the north edge at x {marks}")
    return shape.turned_for_printing(frame)


# The backing.


def check_pads(backing):
    thickness = shape.BACKING_THICKNESS_MM
    tops = [face for face in planar_faces_along(backing, 2)
            if upward(face) and face_coordinate(face, 2) > thickness + MEASURE_TOLERANCE_MM]
    for index in range(shape.CELL_COUNT):
        key_center = shape.cell_key_center(index)
        cell_tops = [face for face in tops
                     if abs(face.CenterOfMass.x - key_center[0]) < layout.KEY_PITCH_MM / 2.0]
        if len(cell_tops) != len(shape.PAD_LOBE_RECTANGLES_MM):
            raise SystemExit(f"error: cell {index + 1} has {len(cell_tops)} pads")
        heights = {round(face_coordinate(face, 2) - thickness, 6) for face in cell_tops}
        if len(heights) != 1:
            raise SystemExit(f"error: cell {index + 1}'s pads differ in height")
        height = heights.pop()
        offset = round(height - (shape.boss_end_depth() - shape.socket_height()), 6) + 0.0
        require_design(f"cell {index + 1}'s pads against the socket's bottom", offset,
                       DESIGN_PAD_OFFSETS_MM[index])
        outline = shape.outline_face(key_center)
        for face in cell_tops:
            point = face.CenterOfMass
            flat = face.copy()
            flat.translate(App.Vector(0.0, 0.0, -point.z))
            if flat.cut(outline).Area > MEASURE_TOLERANCE_MM:
                raise SystemExit(f"error: a pad of cell {index + 1} at ({point.x:.3f}, "
                                 f"{point.y:.3f}) is not under the socket's outline")
        print(f"cell {index + 1}:     pads {height:.3f} tall, top {offset:+.3f} against the "
              "socket's bottom")


def check_screw_holes(backing):
    holes = bore_faces(backing, shape.SCREW_CLEARANCE_HOLE_DIAMETER_MM / 2.0)
    require_on_boss_centers(holes, "screw holes")
    return holes


def check_stack(kind, stacked, frame):
    if frame.common(stacked).Volume > MEASURE_TOLERANCE_MM:
        raise SystemExit(f"error: the backing overlaps the {kind} strip")
    sunk = frame.copy()
    sunk.translate(App.Vector(0.0, 0.0, -CONTACT_PROBE_DEPTH_MM))
    contact = sunk.common(stacked).Volume / CONTACT_PROBE_DEPTH_MM
    expected = len(shape.boss_centers()) * math.pi * (
        (shape.BOSS_DIAMETER_MM / 2.0) ** 2 - (shape.INSERT_BORE_DIAMETER_MM / 2.0) ** 2)
    if abs(contact - expected) > CONTACT_VOLUME_RELATIVE_TOLERANCE * expected:
        raise SystemExit(f"error: the backing touches the {kind} strip over {contact:.4f} mm2, "
                         f"the bosses' ends are {expected:.4f} mm2")
    return contact


def stacked_pads():
    top = -shape.boss_end_depth()
    return [
        plan_prism(polygon, top, top + shape.pad_height(index))
        for index in range(shape.CELL_COUNT)
        for polygon in shape.pad_polygons(shape.cell_key_center(index))
    ]


def pads_to_outline(key_center):
    """The least distance in plan from a cell's pads to its socket's
    outline, which they lie inside."""
    outline = shape.outline_wire(key_center)
    return min(Part.Face(layout_polygon_wire(pad, 0.0)).distToShape(outline)[0]
               for pad in shape.pad_polygons(key_center))


def expected_pad_distance(kind):
    """(distance, its horizontal part) from the pads to the nearest of
    the pocket walls, which the lowest pads pass under, their inner
    faces the pocket's gap outside the socket's outline."""
    nearest = None
    for index in range(shape.CELL_COUNT):
        key_center = shape.cell_key_center(index)
        gap = shape.pocket_gap(shape.cell_pocket_fit(kind, index))
        horizontal = pads_to_outline(key_center) + gap
        vertical = max(0.0, shape.pad_top_depth(index) - shape.wall_depth())
        candidate = (math.hypot(horizontal, vertical), horizontal)
        nearest = candidate if nearest is None else min(nearest, candidate)
    return nearest


def check_pads_clear(kind, frame):
    """(distance, across as printed) from the pads to the walls,
    measured on the walls and on the whole frame: the pads stay clear of
    the walls as printed, beside which they lie under the socket."""
    pads = Part.makeCompound(stacked_pads())
    walls, _ = shape.frame_walls_and_bosses(kind)
    distance, horizontal = expected_pad_distance(kind)
    for what, body in (("walls", Part.makeCompound(walls)), ("frame", frame)):
        measured = body.distToShape(pads)[0]
        if abs(measured - distance) > MEASURE_TOLERANCE_MM:
            raise SystemExit(f"error: the pads come {measured:.4f} from the {kind} strip's "
                             f"{what}, expected {distance:.4f}")
    # The pad's face and the wall's each swell toward the other.
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    printed = horizontal - swelling - swelling
    if printed < -MEASURE_TOLERANCE_MM:
        raise SystemExit(f"error: the pads come {printed:.4f} from the {kind} strip's walls "
                         "as printed")
    return distance, printed


def check_bores_over_holes(frame, holes):
    bores = bore_faces(frame, shape.INSERT_BORE_DIAMETER_MM / 2.0)
    bores = {center for center, span in bores.items() if span[0] < -MEASURE_TOLERANCE_MM}
    stacked_holes = set(holes)
    if bores != stacked_holes:
        raise SystemExit("error: the bores and the screw holes do not line up")
    return len(bores)


def check_wire_rooms(kind, frame, stacked):
    """The tabs' wire rooms, from the ceiling to the backing's top: no
    plastic inside, and the walls and bosses far enough beside them to
    stay out as printed. Returns that clearance."""
    rooms = wire_room_boxes(-shape.boss_end_depth(), 0.0)
    for solid in (frame, stacked):
        inside = solid.common(Part.makeCompound(rooms)).Volume
        if inside > MEASURE_TOLERANCE_MM:
            raise SystemExit(f"error: {inside:.4f} mm3 of plastic in the wire rooms under the "
                             f"{kind} strip")
    walls, bosses = shape.frame_walls_and_bosses(kind)
    distance = least_distance(rooms, walls + bosses)
    return require_clearance(f"the walls and bosses beside the wire rooms of the {kind} strip",
                             distance, WIRE_ROOM_PRINTED_CLEARANCE_MM)


def battery_figures():
    """(the socket's bottom with the frame in the PCB's place, the pads'
    room under it, the backing's underside as printed, its clearance
    from the battery's top)."""
    socket_bottom = layout.PCB_UNDERSIDE_Z_MM - shape.socket_height()
    pads_room = shape.boss_end_depth() - shape.socket_height()
    underside = shape.backing_underside_z_as_printed()
    return socket_bottom, pads_room, underside, underside - layout.BATTERY_TOP_Z_MM


def check_battery():
    socket_bottom, pads_room, underside, clearance = battery_figures()
    limit = shape.backing_thickness_limit()
    heads_bottom = shape.backing_screw_heads_bottom_z()
    heads_clearance = heads_bottom - layout.BATTERY_TOP_Z_MM
    require_clearance("the backing from the battery as printed", clearance,
                      layout.MINIMUM_BATTERY_TO_SOCKET_CLEARANCE_MM)
    require_clearance("the backing's screw heads from the battery as printed", heads_clearance,
                      layout.MINIMUM_BATTERY_TO_SOCKET_CLEARANCE_MM)
    require_design("the backing's thickness", shape.BACKING_THICKNESS_MM,
                   DESIGN_BACKING_THICKNESS_MM)
    require_design("the battery clearance as printed", clearance,
                   DESIGN_BATTERY_CLEARANCE_AS_PRINTED_MM)
    require_design("the screw heads' battery clearance as printed", heads_clearance,
                   DESIGN_SCREW_HEADS_OVER_BATTERY_PRINTED_MM)
    rise = layout.PRINT_RISE_OF_TOP_FACES_MM
    print(f"battery:    in the tray the frame in the PCB's place puts the socket's bottom at "
          f"z {socket_bottom:.3f} (under a PCB {layout.SOCKET_BOTTOM_Z_MM:.2f}); below it the "
          f"pads' room takes {pads_room:.3f} and the backing {shape.BACKING_THICKNESS_MM} (of "
          f"{limit:.3f} the battery allows), its bottom at z {underside + rise:.3f}, "
          f"{underside:.3f} as printed (its top face rises {rise}, measured), "
          f"{clearance:.3f} over the battery's top {layout.BATTERY_TOP_Z_MM} as printed "
          f"(at least {layout.MINIMUM_BATTERY_TO_SOCKET_CLEARANCE_MM}), its screw heads "
          f"{shape.BACKING_SCREW_HEAD_HEIGHT_MM} tall to z {heads_bottom:.3f}, "
          f"{heads_clearance:.3f} over it")
    strips_top = max(strip.z_range[1] for strip in layout.nano_strip_envelopes())
    print(f"strips:     the backing's underside {underside - strips_top:.3f} over the "
          f"nice!nano's socket strips' top z {strips_top:.3f} as printed, its screw heads "
          f"{heads_bottom - strips_top:.3f}, so a frame's backing screws must keep off the "
          "strips in plan")


def export_backing(arguments):
    backing, expected = shape.build_backing()
    (x_low, x_high), (y_low, y_high) = shape.frame_body_rectangle()
    print(f"strip:      backing, {x_high - x_low:.3f} x {y_high - y_low:.3f} x "
          f"{shape.BACKING_THICKNESS_MM}, pads {shape.PAD_INSET_MM:.2f} inside each socket lobe")
    print(f"volume:     {backing.Volume:.3f} mm3 (analytic {expected:.3f} mm3)")
    check_pads(backing)
    holes = check_screw_holes(backing)
    print(f"holes:      {len(holes)}, {shape.SCREW_CLEARANCE_HOLE_DIAMETER_MM:.2f} modelled "
          f"({layout.MOUNTING_DRILL_DIAMETER_MM} printed) for M2 screws")
    stacked = shape.stacked_backing(backing)
    for kind in shape.FRAME_KINDS:
        frame, _ = shape.build_frame(kind, arguments.pull_in, arguments.insert_length)
        contact = check_stack(kind, stacked, frame)
        distance, printed = check_pads_clear(kind, frame)
        bores = check_bores_over_holes(frame, holes)
        rooms = check_wire_rooms(kind, frame, stacked)
        print(f"stack:      under the {kind} strip nothing overlaps, contact {contact:.3f} mm2 "
              f"(the bosses' ends), pads {distance:.3f} from its walls ({printed:.3f} across as "
              f"printed), {bores} bores over their screw holes, wire rooms {rooms:.3f} clear")
    check_battery()
    check_notches(backing, shape.BACKING_THICKNESS_MM / 2.0)
    print("notches:    cell k has k in the south edge")
    return backing


# The switch hole strip.


def require_figure(what, measured, figure):
    if abs(measured - figure) > design_tolerance():
        raise SystemExit(f"error: {what} is {measured:.4f}, expected {figure:.2f}")


def vertical_cylinder_faces(solid):
    return [face for face in solid.Faces
            if isinstance(face.Surface, Part.Cylinder) and abs(face.Surface.Axis.z) > 0.999]


def measured_through_hole(faces, center, what):
    """(diameter, faces) of the hole on a plan center: the vertical
    cylinder faces on that axis, which must share one radius and run
    from the underside to the top face."""
    on_axis = [face for face in faces
               if math.hypot(face.Surface.Center.x - center[0],
                             face.Surface.Center.y - center[1]) < MEASURE_TOLERANCE_MM]
    if not on_axis:
        raise SystemExit(f"error: {what} is missing")
    radii = [face.Surface.Radius for face in on_axis]
    low = min(face.BoundBox.ZMin for face in on_axis)
    high = max(face.BoundBox.ZMax for face in on_axis)
    if (max(radii) - min(radii) > MEASURE_TOLERANCE_MM or abs(low) > MEASURE_TOLERANCE_MM
            or abs(high - layout.PCB_THICKNESS_MM) > MEASURE_TOLERANCE_MM):
        raise SystemExit(f"error: {what} is not one cylinder through the strip: radii "
                         + ", ".join(f"{radius:.4f}" for radius in radii)
                         + f", z {low:.4f} to {high:.4f}")
    return 2.0 * radii[0], on_axis


def measured_cell_holes(faces, index, pull_in):
    """Cell index's footprint holes as measured, [(diameter, faces)] in
    layout.CHOC_FOOTPRINT_HOLES_MM's order, each at its size as built."""
    measured = []
    for name, (center, radius) in zip(SWITCH_STRIP_HOLE_NAMES,
                                      shape.cell_holes(shape.SWITCH, index, pull_in), strict=True):
        what = f"cell {index + 1}'s {name} hole"
        diameter, hole_faces = measured_through_hole(faces, center, what)
        if abs(diameter - 2.0 * radius) > MEASURE_TOLERANCE_MM:
            raise SystemExit(f"error: {what} is {diameter:.6f} across, built as "
                             f"{2.0 * radius:.6f}")
        measured.append((diameter, hole_faces))
    return measured


def holes_where(measured, keep):
    """[(name, diameter)] of a cell's measured holes whose footprint-local
    center keep() accepts."""
    return [(name, diameter) for name, (local_center, _), (diameter, _) in zip(
        SWITCH_STRIP_HOLE_NAMES, layout.CHOC_FOOTPRINT_HOLES_MM, measured, strict=True)
        if keep(local_center)]


def is_switch_part_hole(local_center):
    return local_center in shape.switch_part_calipered_diameters()


def is_other_hole(local_center):
    """The NC pad's: neither a pin hole nor the post's or a peg's."""
    return not shape.is_pin_hole(local_center) and not is_switch_part_hole(local_center)


def transcribed_switch_holes(index, pull_in):
    """Cell index's holes as modelled by the hand-worked figures, in
    layout.CHOC_FOOTPRINT_HOLES_MM's order: the post and pegs
    DESIGN_SWITCH_POST_HOLES_MM's and DESIGN_SWITCH_PEG_HOLES_MM's, past
    those (cell 6) the pocket strip's, the pin holes
    DESIGN_SWITCH_PIN_HOLE_DIAMETER_MM, the NC pad's the pocket strip's."""
    pocket_strip = [2.0 * radius for _, radius in shape.cell_holes(shape.POCKET, index, pull_in)]
    figures = []
    for (local_center, _), pocket_strip_diameter in zip(layout.CHOC_FOOTPRINT_HOLES_MM,
                                                        pocket_strip, strict=True):
        if shape.is_pin_hole(local_center):
            figures.append(DESIGN_SWITCH_PIN_HOLE_DIAMETER_MM)
        elif is_switch_part_hole(local_center) and index < len(DESIGN_SWITCH_POST_HOLES_MM):
            figures.append((DESIGN_SWITCH_POST_HOLES_MM if local_center == CENTER_POST_HOLE_MM
                            else DESIGN_SWITCH_PEG_HOLES_MM)[index])
        else:
            figures.append(pocket_strip_diameter)
    return figures


def check_switch_cell(index, measured, pull_in):
    """Cell index's measured holes against the hand-worked figures.
    Returns [(name, modelled, printed, clearance over the calipered
    part)] for the post and both pegs, cells 1 to 5's clearance checked
    against DESIGN_SWITCH_HOLE_CLEARANCES_MM."""
    for name, (diameter, _), figure in zip(SWITCH_STRIP_HOLE_NAMES, measured,
                                           transcribed_switch_holes(index, pull_in), strict=True):
        require_figure(f"cell {index + 1}'s {name} hole as modelled", diameter, figure)
    calipered = shape.switch_part_calipered_diameters()
    parts = []
    for (name, diameter), part in zip(holes_where(measured, is_switch_part_hole),
                                      calipered.values(), strict=True):
        printed = shape.printed_switch_hole_diameter(diameter)
        parts.append((name, diameter, printed, printed - part))
    if index < len(DESIGN_SWITCH_HOLE_CLEARANCES_MM):
        for name, _, _, clearance in parts:
            require_figure(f"cell {index + 1}'s {name} hole's clearance as printed", clearance,
                           DESIGN_SWITCH_HOLE_CLEARANCES_MM[index])
    return parts


def print_switch_cell(index, parts, pull_in):
    if index == shape.SWITCH_REFERENCE_CELL_INDEX:
        step = f"the socket strips' holes, grown by pull_in {pull_in}"
    else:
        step = f"clearance {shape.cell_switch_hole_clearance(index):+.2f} as printed"
    holes = "; ".join(f"{name} {modelled:.3f} modelled, {printed:.3f} printed, {clearance:+.3f} "
                      "over the part" for name, modelled, printed, clearance in parts)
    print(f"cell {index + 1}:     {step}: {holes}")


def blade_reach(hole_center, blade_center, thickness):
    """How far a blade's farthest edge lies from its hole's center in
    plan: its calipered thickness along footprint x, the model's width
    along y."""
    along_x = abs(blade_center[0] - hole_center[0]) + thickness / 2.0
    along_y = abs(blade_center[1] - hole_center[1]) + layout.CHOC_PIN_BLADE_WIDTH_MM / 2.0
    return math.hypot(along_x, along_y)


def check_switch_pin_holes(measured_cells, pull_in):
    """Every cell's pin holes and NC pad's hole as measured (each
    already checked against its figure), and the room the blades leave
    in the smallest pin hole as printed, which must be positive."""
    pins = [diameter for measured in measured_cells
            for _, diameter in holes_where(measured, shape.is_pin_hole)]
    others = [diameter for measured in measured_cells
              for _, diameter in holes_where(measured, is_other_hole)]
    printed_radius = shape.printed_switch_hole_diameter(min(pins)) / 2.0
    pin_names = [name for name, _ in holes_where(measured_cells[0], shape.is_pin_hole)]
    blades = []
    for name, hole_center, blade_center, thickness in zip(
            pin_names, layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM, layout.CHOC_PIN_CENTERS_MM,
            layout.CHOC_PIN_CALIPERED_BLADE_THICKNESSES_MM, strict=True):
        reach = blade_reach(hole_center, blade_center, thickness)
        if reach >= printed_radius:
            raise SystemExit(f"error: the {name}'s blade reaches {reach:.3f} from its hole's "
                             f"center, past the hole's {printed_radius:.3f} radius as printed")
        blades.append(f"{name} {reach:.3f}")
    print(f"pin holes:  {len(pins)}, {min(pins):.3f} to {max(pins):.3f} modelled whatever "
          f"pull_in, {2.0 * printed_radius:.3f} printed; the blades (calipered thickness, the "
          f"model's width) reach {', '.join(blades)} from their holes' centers, inside the "
          f"{printed_radius:.3f} radius as printed")
    print(f"NC pads:    {len(others)} holes, {min(others):.3f} to {max(others):.3f} modelled "
          f"(the footprint's grown by pull_in {pull_in})")


def cell_hole_webs(index, measured, pull_in):
    """[(web, first name, second name)] between every two of cell
    index's holes: the least distance between their measured faces,
    checked against the plan's from the holes' centers and radii."""
    holes = shape.cell_holes(shape.SWITCH, index, pull_in)
    webs = []
    for first in range(len(measured)):
        for second in range(first + 1, len(measured)):
            web = least_distance(measured[first][1], measured[second][1])
            (first_center, first_radius), (second_center, second_radius) = (holes[first],
                                                                            holes[second])
            plan = math.dist(first_center, second_center) - first_radius - second_radius
            names = (SWITCH_STRIP_HOLE_NAMES[first], SWITCH_STRIP_HOLE_NAMES[second])
            if abs(web - plan) > MEASURE_TOLERANCE_MM:
                raise SystemExit(f"error: cell {index + 1}'s {names[0]} and {names[1]} holes "
                                 f"keep {web:.6f} between them, {plan:.6f} in plan")
            webs.append((web, *names))
    return webs


def check_switch_hole_webs(measured_cells, pull_in):
    """The least plastic between two holes of each cell, at least
    MINIMUM_HOLE_WEB_MM as modelled."""
    least = []
    for index, measured in enumerate(measured_cells):
        web, first, second = min(cell_hole_webs(index, measured, pull_in))
        require_clearance(f"cell {index + 1}'s {first} and {second} holes", web,
                          MINIMUM_HOLE_WEB_MM)
        least.append((web, first, second))
    growth = 2.0 * shape.MEASURED_HOLE_SHRINK_PER_SIDE_MM
    print(f"webs:       the least plastic between two holes, cells 1 to {shape.CELL_COUNT}: "
          + ", ".join(f"{web:.3f} ({first} to {second})" for web, first, second in least)
          + f" modelled (at least {MINIMUM_HOLE_WEB_MM}), "
          + ", ".join(f"{web + growth:.3f}" for web, _, _ in least) + " printed")


def export_switch_holes(arguments):
    pull_in = arguments.pull_in
    strip, expected = shape.build_switch_strip(pull_in)
    (x_low, x_high), (y_low, y_high) = shape.switch_strip_rectangle()
    print(f"strip:      switch, {shape.CELL_COUNT} cells at {layout.KEY_PITCH_MM} pitch, the "
          f"frame's body {x_high - x_low:.3f} x {y_high - y_low:.3f} x "
          f"{layout.PCB_THICKNESS_MM} with each cell's footprint holes, no walls, bosses or "
          "recesses")
    print(f"volume:     {strip.Volume:.3f} mm3 (analytic {expected:.3f} mm3)")
    print(f"switch:     post {shape.SWITCH_POST_CALIPERED_DIAMETER_MM} and pegs "
          f"{shape.SWITCH_PEG_CALIPERED_DIAMETER_MM} across, calipered; a hole taken to print "
          f"{shape.MEASURED_HOLE_SHRINK_PER_SIDE_MM} per side smaller than modelled (the hole "
          "strip's, measured on 3.x holes, the pegs' smaller holes not yet measured)")
    faces = vertical_cylinder_faces(strip)
    measured_cells = [measured_cell_holes(faces, index, pull_in)
                      for index in range(shape.CELL_COUNT)]
    for index, measured in enumerate(measured_cells):
        print_switch_cell(index, check_switch_cell(index, measured, pull_in), pull_in)
    check_switch_pin_holes(measured_cells, pull_in)
    check_switch_hole_webs(measured_cells, pull_in)
    check_notches_from(strip, y_low, layout.PCB_THICKNESS_MM / 2.0)
    print(f"notches:    cells 1 to {shape.CELL_COUNT} have "
          + ", ".join(str(index + 1) for index in range(shape.CELL_COUNT))
          + " in the south edge, every other notch place solid")
    return shape.turned_for_printing(strip)


def main():
    arguments = parse_arguments(script_arguments(sys.argv))
    if arguments.kind == shape.BACKING:
        strip = export_backing(arguments)
    elif arguments.kind == shape.SWITCH:
        strip = export_switch_holes(arguments)
    else:
        strip = export_frame(arguments)
    mesh = export_stl(strip, arguments.stl_file)
    check_closed_mesh(arguments.stl_file)
    if abs(mesh.BoundBox.ZMin) > MEASURE_TOLERANCE_MM:
        raise SystemExit(f"error: the mesh's lowest point lies at z {mesh.BoundBox.ZMin:.4f}, "
                         "not on the bed")
    box = strip.BoundBox
    print(f"print:      {'bottom' if arguments.kind == shape.BACKING else 'frame top'} on z = 0, "
          f"{box.XLength:.2f} x {box.YLength:.2f} x {box.ZLength:.2f} mm")
    print(f"wrote:      {arguments.stl_file} ({mesh.CountFacets} facets), one closed "
          "manifold shell")


run_and_exit(main)
