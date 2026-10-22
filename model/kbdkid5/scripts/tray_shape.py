"""The tray's shape: its builder, and what parts built around it need
to know of it.

The outline helpers its walls are built from (sharp-corner rebuild,
uniform corner fillets), the corner radius those walls get, and the
tray's dimensions. Ported from kbdkid4's tray_shape.py, its helpers
as they were there, less what kbdkid4 read off its PCB: the power
switch and USB window helpers with their constants,
tray_opens_toward_positive_axis(), component_protrusions(),
projected_interval(), the board_step import, and the depth and
standoff height defaults (layout.py has kbdkid5's heights). kbdkid5's
parts sit in the tray, not on the PCB, and come from layout.py. Added
are the dimensions re-exported from layout.py under kbdkid4's names,
the ledge width among them, which kbdkid4 kept in export_tray.py.

build_tray() builds a half's tray shell and joint (work item 003) from
layout.py, kbdkid4's export_tray.py on the layout instead of a STEP.
First the walls and floor, every corner bent with the same concentric
pair of radii, the ledge with the joint block in its place along the
slant, the shelves on the ledge's face under the edges of the
hand-wired frame's backing (work item 020), notched for its screw
heads, the standoffs bored for M2 heat-set inserts, and the dowel pin
bosses and the parking hole's boss, up to the PCB's underside, with the
fills that close the crevices beside them. Then the cuts, all exactly as
layout.py gives them: the ledge cut-aways layout.py declares for the
parts in the tray, the west socket strip's pocket in the column 1/2
step's ledge,
the sockets' notches, pockets and reliefs, and the standoffs' flats.
Every cut but the sockets' wall pockets is clipped to the cavity so it
never reaches the wall, and a cut that finds nothing left to remove (a
tab's relief inside its notch) is skipped. Then the parts' mounts
(work item 004), layout.py's boxes in its order: the power switch's
cradle with its retainer's socket, the reset button's back wall, side
walls and front stop, then the nice!nano's north block with the sill
under its opening, its screw clamp's block and foot (work items
009 and 010), its west and east walls, cut back over the board's top
for the socket strips, with their raised pieces up to the PCB's
underside, and the seat the board lies on, which leaves the pry
recess free, no body filling a standoff's bore, then the USB shell's
channel and the USB window, the knob slot through the ledge and the
north wall, the reset pin hole through the north wall, the nice!nano's
pry slot through the clamp's block and foot and the clamp block's
insert bore. Then
the magnet slots, open toward the cavity (but the south 2.165 of the
one at 48.26 along the slant, which the sixth standoff walls off), with
the wall cut back over them, the flat-topped teardrop pin holes (the
half's fit and depth, the right half's with a lead-in at the mouth),
the flat-topped teardrop parking hole and the chamfer along the joint
face's bottom edge. Each
step checks its volume and probes what it made. Last the floor is
checked closed: its underside is the void-free footprint's, so no void
reaches it (work item 009).

The right half is built in the left half's frame, cut for its own
sockets (layout.py's module docstring), and mirrored across the
layout's mirror line by mirror_for_right_half(), so the halves' pins
and magnets sit at the same places along the slant. build_tray()
returns the tray unmirrored, so work that extends it (a carrying case)
can add to it in the layout's frame first.

Like freecad_common.py this module has no entry point, so it is safe
to import from the export scripts and probes.
"""

import itertools
import math
from dataclasses import dataclass

import FreeCAD as App
import Part

import layout

# The tray's dimensions, all in mm (DESIGN.md, "Heights": all as
# kbdkid4). layout.py holds them, so check_layout.py can use them
# without FreeCAD; these are the names kbdkid4's tray code knows them
# by.
DEFAULT_GAP_MM = layout.TRAY_GAP_MM  # clearance between PCB edge and cavity wall
DEFAULT_WALL_MM = layout.TRAY_WALL_MM  # wall thickness (two nozzle widths)
DEFAULT_FLOOR_MM = layout.TRAY_FLOOR_MM  # floor thickness
DEFAULT_LEDGE_WIDTH_MM = layout.TRAY_LEDGE_WIDTH_MM  # PCB support ledge from the cavity wall

# Implementation tuning, rarely worth touching.
CORNER_FIT_SAFETY = 0.95  # margin on the largest corner radius that fits
MINIMUM_FILLET_RADIUS_MM = 0.01  # below this a fillet is skipped as moot
SHARPEN_MAX_CORNER_RADIUS_MM = 3.0  # outline arcs above this are not corners
CUT_EXTRA_MM = 1.0  # cutters overshoot open faces for a clean cut
NOTHING_LEFT_MM3 = 1e-3  # a cut removing less than this found nothing to remove
PROBE_OFFSET_MM = 0.3  # probes this far beside a cut's edges
INSIDE_TOLERANCE_MM = 1e-6

UP = App.Vector(0.0, 0.0, 1.0)


def outline_straight_segments(outline_wire):
    """The outline's straight segments in wire order, as (point,
    direction) pairs. The small corner arcs between them are dropped;
    a large arc means the outline has a curved edge the tray's
    uniform-corner rebuild cannot represent, so that is an error."""
    segments = []
    for edge in outline_wire.OrderedEdges:
        curve = edge.Curve
        if isinstance(curve, Part.Line):
            start = edge.valueAt(edge.FirstParameter)
            end = edge.valueAt(edge.LastParameter)
            segments.append((start, end.sub(start)))
        elif isinstance(curve, Part.Circle):
            if curve.Radius > SHARPEN_MAX_CORNER_RADIUS_MM:
                raise SystemExit(
                    f"error: outline contains an arc of radius "
                    f"{curve.Radius:.2f} mm, too large to be treated as a "
                    "corner round"
                )
        else:
            raise SystemExit(
                f"error: unsupported outline edge type "
                f"{type(curve).__name__}"
            )
    if len(segments) < 3:
        raise SystemExit("error: outline has fewer than 3 straight segments")
    return segments


def intersect_in_plane(point_a, direction_a, point_b, direction_b, normal):
    """Intersection of two lines lying in the plane with the given
    normal, or None for (near) parallel lines."""
    denominator = direction_a.cross(direction_b).dot(normal)
    if abs(denominator) < 1e-9 * direction_a.Length * direction_b.Length:
        return None
    parameter = point_b.sub(point_a).cross(direction_b).dot(normal) / denominator
    return point_a.add(direction_a * parameter)


def sharpen_outline(outline_wire, normal):
    """Rebuild the outline as a sharp-corner polygon: keep the straight
    segments and extend neighbours to their intersections, dropping the
    corner rounds the board outline already carries. This is what makes
    a single uniform corner radius possible later on."""
    segments = outline_straight_segments(outline_wire)
    corner_points = []
    for index, (point_a, direction_a) in enumerate(segments):
        point_b, direction_b = segments[(index + 1) % len(segments)]
        corner = intersect_in_plane(
            point_a, direction_a, point_b, direction_b, normal
        )
        if corner is None:
            raise SystemExit(
                "error: successive parallel outline segments, cannot "
                "rebuild a sharp-corner outline"
            )
        corner_points.append(corner)
    return Part.makePolygon(corner_points + [corner_points[0]])


def is_vertical_line_edge(edge, up):
    if not isinstance(edge.Curve, Part.Line):
        return False
    direction = edge.valueAt(edge.LastParameter).sub(
        edge.valueAt(edge.FirstParameter)
    )
    if direction.Length < 1e-9:
        return False
    return abs(direction.normalize().dot(up)) > 0.999


def vertex_key(point):
    return (round(point.x, 4), round(point.y, 4), round(point.z, 4))


def polygon_corner_convexity(polygon_wire, up):
    """Map each polygon vertex position to whether its corner is convex
    (material angle below 180 degrees), keyed by vertex_key()."""
    points = [vertex.Point for vertex in polygon_wire.OrderedVertexes]
    count = len(points)
    directions = [
        points[(index + 1) % count].sub(points[index]).normalize()
        for index in range(count)
    ]
    turns = []
    for index in range(count):
        cross = directions[index - 1].cross(directions[index]).dot(up)
        dot = directions[index - 1].dot(directions[index])
        turns.append(math.atan2(cross, dot))
    orientation = 1.0 if sum(turns) > 0 else -1.0
    return {
        vertex_key(points[index]): turns[index] * orientation > 0
        for index in range(count)
    }


def corner_edges(solid, up, convexity_by_vertex, want_convex):
    """The solid's vertical edges standing on polygon corners of the
    requested convexity. Seam edges from earlier fillets stand on no
    polygon corner and are skipped by the position match."""
    selected = []
    for edge in solid.Edges:
        if not is_vertical_line_edge(edge, up):
            continue
        for parameter in (edge.FirstParameter, edge.LastParameter):
            key = vertex_key(edge.valueAt(parameter))
            if key in convexity_by_vertex:
                if convexity_by_vertex[key] == want_convex:
                    selected.append(edge)
                break
    return selected


def fillet_prism_corners(prism, polygon, up, convex_radius, concave_radius):
    """Fillet a prism's vertical corner edges, with one radius for the
    polygon's convex corners and another for its concave ones."""
    convexity = polygon_corner_convexity(polygon, up)
    result = prism
    for want_convex, radius in ((True, convex_radius), (False, concave_radius)):
        if radius < MINIMUM_FILLET_RADIUS_MM:
            continue
        edges = corner_edges(result, up, convexity, want_convex)
        if edges:
            result = result.makeFillet(radius, edges)
    return result


def max_uniform_corner_radius(polygon_wire):
    """Largest fillet radius all corners of a polygon can share.

    A fillet with radius R at a corner with turn angle t consumes
    R * tan(t / 2) of each adjacent edge, so every edge must be at
    least as long as the demands of the fillets at its two ends.
    """
    points = [vertex.Point for vertex in polygon_wire.OrderedVertexes]
    count = len(points)
    directions = []
    lengths = []
    for index in range(count):
        vector = points[(index + 1) % count].sub(points[index])
        lengths.append(vector.Length)
        directions.append(vector.normalize())
    demands = []
    for index in range(count):
        cosine = max(-1.0, min(1.0, directions[index - 1].dot(directions[index])))
        demands.append(math.tan(math.acos(cosine) / 2.0))
    radius_limit = None
    for index in range(count):
        demand_sum = demands[index] + demands[(index + 1) % count]
        if demand_sum < 1e-9:
            continue
        limit = lengths[index] / demand_sum
        if radius_limit is None or limit < radius_limit:
            radius_limit = limit
    if radius_limit is None:
        raise SystemExit("error: outline polygon has no corners to fillet")
    return radius_limit


def tray_corner_radius(outer_wire, gap, wall):
    """The corner radius on the outside of every bend of the tray's
    wall: gap + wall, capped by what the outer wall's sharp-corner
    polygon (`outer_wire`, the sharpened outline offset by gap + wall)
    can fit at all of its corners, less the CORNER_FIT_SAFETY margin
    and rounded down to 0.01 mm."""
    return min(
        gap + wall,
        math.floor(100.0 * CORNER_FIT_SAFETY * max_uniform_corner_radius(outer_wire))
        / 100.0,
    )


def nearest_outline_segment(segments, position):
    """(index, closest point on segment, direction) of the outline
    segment nearest a position."""
    best = None
    for index, (start, vector) in enumerate(segments):
        length = vector.Length
        direction = App.Vector(vector).normalize()
        along = max(0.0, min(length, direction.dot(position.sub(start))))
        closest = start.add(direction * along)
        distance = position.sub(closest).Length
        if best is None or distance < best[0]:
            best = (distance, index, closest, direction)
    return best[1], best[2], best[3]


def wall_outward(outline_wire, center_on_edge, direction, up):
    """The horizontal direction pointing out of the board at a point on
    the outline, perpendicular to the wall direction there: the side of
    the segment on which a point just off the outline lies outside the
    board (the bounding box center would mislead on the short risers of
    a stepped edge)."""
    outward = direction.cross(up)
    probe = center_on_edge.add(outward * 0.05)
    if Part.Face(outline_wire).isInside(probe, 1e-6, True):
        outward = outward.negative()
    return outward


# The tray builder (see the module docstring).

FLOOR_UNDERSIDE_Z_MM = layout.FLOOR_UNDERSIDE_Z_MM
LEDGE_TOP_Z_MM = layout.PCB_UNDERSIDE_Z_MM  # also the joint block's and the standoffs' tops
RIM_Z_MM = layout.TRAY_RIM_Z_MM


@dataclass
class Tray:
    """build_tray()'s result: the solid in the layout's frame, the right
    half's unmirrored, and how it came about."""

    solid: Part.Shape
    right: bool
    corner_radius: float  # on the outside of every bend
    pin_hole_diameter: float
    pin_hole_depth: float
    pin_hole_lead_in: float
    cuts: list  # (label, removed volume) of the ledge, wall and standoff cuts
    skipped_cuts: list  # labels of the cuts that found nothing left to remove
    fits: layout.MountFits  # the mounts' fits the tray was built with
    mounts: list  # (label, added volume) of the mounts' bodies
    bed_area: float  # the floor's underside, closed
    shelves: float  # the volume the shelves under the backing's edges added
    shelf_notches: tuple  # their notches for the backing's screw heads (layout.TrayCut)


def layout_polygon_wire(polygon, z):
    """A closed wire through a layout polygon's points at height z."""
    points = [App.Vector(x, y, z) for x, y in polygon]
    return Part.makePolygon(points + [points[0]])


def plan_prism(polygon, bottom, top):
    """A layout polygon extruded from z bottom to z top."""
    return Part.Face(layout_polygon_wire(polygon, bottom)).extrude(UP * (top - bottom))


def rounded_prism(polygon, bottom, top, convex_radius, concave_radius):
    """plan_prism() with its vertical corner edges rounded, with one
    radius at the polygon's convex corners and another at its concave
    ones."""
    wire = layout_polygon_wire(polygon, bottom)
    prism = Part.Face(wire).extrude(UP * (top - bottom))
    return fillet_prism_corners(prism, wire, UP, convex_radius, concave_radius)


def outer_prism(top, corner_radius):
    """The tray's outside from the floor's underside up to z top."""
    return rounded_prism(
        layout.tray_outer_polygon(),
        FLOOR_UNDERSIDE_Z_MM,
        top,
        corner_radius,
        corner_radius - DEFAULT_WALL_MM,
    )


def cavity_prism(corner_radius):
    """The cavity from the floor's top up past the rim."""
    return rounded_prism(
        layout.tray_cavity_polygon(),
        0.0,
        RIM_Z_MM + CUT_EXTRA_MM,
        corner_radius - DEFAULT_WALL_MM,
        corner_radius,
    )


def is_solid_at(shape, point):
    return shape.isInside(point, INSIDE_TOLERANCE_MM, True)


def require_one_valid_solid(shape, what):
    if not shape.isValid() or len(shape.Solids) != 1:
        raise SystemExit(
            f"error: {what} gave {len(shape.Solids)} solids (valid: {shape.isValid()}), "
            "expected one valid solid"
        )


def require_volume(what, measured, expected, relative_tolerance):
    if abs(measured - expected) > relative_tolerance * expected + NOTHING_LEFT_MM3:
        raise SystemExit(
            f"error: {what} came to {measured:.4f} mm3, expected {expected:.4f} mm3; "
            "geometry is off"
        )


def build_walls(corner_radius):
    """The outside less the cavity: the walls up to the rim and the
    floor. Returns (tray, cavity prism)."""
    shell = outer_prism(RIM_Z_MM, corner_radius)
    cavity = cavity_prism(corner_radius)
    tray = shell.cut(cavity)
    require_one_valid_solid(tray, "cutting the cavity")
    # The cavity prism is a straight extrusion lying inside the shell in
    # plan, so the part of it inside the shell scales with height.
    expected = shell.Volume - cavity.Volume * RIM_Z_MM / (RIM_Z_MM + CUT_EXTRA_MM)
    require_volume("the walls and floor", tray.Volume, expected, 1e-6)
    return tray, cavity


def add_ledge(tray, corner_radius):
    """Fuse the ledge along the cavity wall, its top level with the
    standoffs', with the joint block in its place along the slant (both
    in layout.ledge_inner_polygon()). The well inside it continues the
    concentric corners inward: its convex corners have run out of radius
    (sharp), its concave ones grow by the ledge's width."""
    well = rounded_prism(
        layout.ledge_inner_polygon(),
        0.0,
        LEDGE_TOP_Z_MM + CUT_EXTRA_MM,
        corner_radius - DEFAULT_WALL_MM - DEFAULT_LEDGE_WIDTH_MM,
        corner_radius + DEFAULT_LEDGE_WIDTH_MM,
    )
    ring = outer_prism(LEDGE_TOP_Z_MM, corner_radius).cut(well)
    result = tray.fuse(ring)
    require_one_valid_solid(result, "fusing the ledge")
    # The sharp polygons' area between the cavity wall and the well. The
    # corner rounds change it by a few percent.
    nominal = (
        layout.polygon_signed_area(layout.tray_cavity_polygon())
        - layout.polygon_signed_area(layout.ledge_inner_polygon())
    ) * LEDGE_TOP_Z_MM
    require_volume("the ledge and the joint block", result.Volume - tray.Volume, nominal, 0.05)
    return result


def backing_shelf_body(corner_radius, right):
    """The shelves under the backing's edges (layout.py's
    backing_shelf_polygon()) with the ledge and the walls behind them, up
    to the shelves' top: the outside less the well inside the shelves'
    face, its corners rounded as add_ledge() rounds the ledge's well
    (sharp where they have run out of radius, 2.13 at every inward
    corner), less the notches for the half's backing screw heads. Fused
    onto the tray it adds the shelves and, below their top, fills the
    ledge's rounded corners beside them."""
    top = layout.BACKING_SHELF_TOP_Z_MM
    well = rounded_prism(
        layout.backing_shelf_polygon(),
        0.0,
        top + CUT_EXTRA_MM,
        corner_radius - DEFAULT_WALL_MM - DEFAULT_LEDGE_WIDTH_MM,
        corner_radius + DEFAULT_LEDGE_WIDTH_MM,
    )
    body = outer_prism(top, corner_radius).cut(well)
    notches = [
        plan_prism(layout.tray_cut_polygon(notch), FLOOR_UNDERSIDE_Z_MM - CUT_EXTRA_MM,
                   top + CUT_EXTRA_MM)
        for notch in layout.backing_shelf_notches(right)
    ]
    if notches:
        body = body.cut(Part.makeCompound(notches))
    return body


def notch_area_in_shelf(notch):
    """The plan area a shelf's notch takes from the shelf: from the
    shelves' face to the notch's far side, over its length."""
    along_low, along_high = notch.along_range
    depth = notch.across_range[1] + layout.backing_shelf_face_reach()
    return (along_high - along_low) * depth


def add_backing_shelves(tray, corner_radius, right):
    """Fuse the shelves (backing_shelf_body()) and check them. They add
    their sharp pieces' volume less the notches' within 1%: the rounds
    of their face take off as much as they fill in the ledge's rounded
    corners beside them, but for the round where the outer edge's shelf
    starts. Each piece is solid in its middle below the top and open
    over it, and each notch is open. Returns (tray, added volume)."""
    top = layout.BACKING_SHELF_TOP_Z_MM
    notches = layout.backing_shelf_notches(right)
    result = tray.fuse(backing_shelf_body(corner_radius, right))
    require_one_valid_solid(result, "fusing the shelves")
    pieces = layout.backing_shelf_pieces()
    area = (sum(layout.polygon_signed_area(piece) for _label, _index, piece in pieces)
            - sum(notch_area_in_shelf(notch) for notch in notches))
    added = result.Volume - tray.Volume
    require_volume("the shelves", added, area * top, 0.01)
    for label, _index, piece in pieces:
        x = sum(point[0] for point in piece) / len(piece)
        y = sum(point[1] for point in piece) / len(piece)
        if not is_solid_at(result, App.Vector(x, y, top / 2.0)):
            raise SystemExit(f"error: the {label} is not solid in its middle")
        if is_solid_at(result, App.Vector(x, y, top + PROBE_OFFSET_MM)):
            raise SystemExit(f"error: the {label} is not open over its top")
    for notch in notches:
        along = sum(notch.along_range) / 2.0
        across = (notch.across_range[1] - layout.backing_shelf_face_reach()) / 2.0
        x, y = layout.outline_edge_point(notch.edge_index, along, across)
        if is_solid_at(result, App.Vector(x, y, top / 2.0)):
            raise SystemExit(f"error: the {notch.label} is not open")
    return result, added


def standoff_area_in_joint_block(center):
    """The plan area of a standoff's ring inside the joint block, which a
    standoff near the slant merges with: its circle's segment beyond the
    block's inner face, 0 for a standoff standing free in the cavity. The
    bore must stay clear of the block and the segment on the block's
    straight run, short of the slant's ends."""
    radius = layout.STANDOFF_DIAMETER_MM / 2.0
    south_x, south_y = layout.slant_point(0.0, 0.0)
    offset = (center[0] - south_x, center[1] - south_y)
    normal = layout.slant_outward_normal()
    direction = layout.slant_direction()
    inner_face = layout.JOINT_FACE_OUTWARD_MM - layout.JOINT_BLOCK_THICKNESS_MM
    into_cavity = inner_face - (offset[0] * normal[0] + offset[1] * normal[1])
    if into_cavity >= radius:
        return 0.0
    along = offset[0] * direction[0] + offset[1] * direction[1]
    if (into_cavity <= layout.STANDOFF_BORE_DIAMETER_MM / 2.0
            or not radius < along < layout.slant_length() - radius):
        raise SystemExit(f"error: the standoff at {center} meets the joint block other than by "
                         "a segment of its ring")
    return circular_segment_area(radius, into_cavity)


def add_standoffs(tray):
    """Fuse a standoff at each mounting drill, from the floor's
    underside (so the fuse leaves no seam) to the ledge top, bored for a
    heat-set insert down to the floor's top, which backs the insert with
    the floor's thickness (kbdkid4's). One near the slant merges with the
    joint block, whose slots and holes are cut through both later."""
    radius = layout.STANDOFF_DIAMETER_MM / 2.0
    bore_radius = layout.STANDOFF_BORE_DIAMETER_MM / 2.0
    bodies = []
    bores = []
    for x, y in layout.MOUNTING_DRILL_CENTERS_MM:
        bodies.append(
            Part.makeCylinder(
                radius,
                LEDGE_TOP_Z_MM - FLOOR_UNDERSIDE_Z_MM,
                App.Vector(x, y, FLOOR_UNDERSIDE_Z_MM),
                UP,
            )
        )
        bores.append(
            Part.makeCylinder(
                bore_radius, LEDGE_TOP_Z_MM + CUT_EXTRA_MM, App.Vector(x, y, 0.0), UP
            )
        )
    result = tray.fuse(Part.makeCompound(bodies)).cut(Part.makeCompound(bores))
    require_one_valid_solid(result, "adding the standoffs")
    # Each adds its whole ring but the segment already in the joint block.
    ring_area = math.pi * (radius**2 - bore_radius**2)
    expected = LEDGE_TOP_Z_MM * sum(ring_area - standoff_area_in_joint_block(center)
                                    for center in layout.MOUNTING_DRILL_CENTERS_MM)
    require_volume("the standoffs", result.Volume - tray.Volume, expected, 1e-6)
    return result


def dowel_boss_body(along, right):
    """A dowel boss beyond the joint block: the half's boss in plan from
    its inner end to the block's middle (the block fills the rest of its
    reach), from the floor's underside to the boss's top."""
    face = layout.JOINT_FACE_OUTWARD_MM
    outward_range = (
        face - layout.dowel_boss_reach(right),
        face - layout.JOINT_BLOCK_THICKNESS_MM / 2.0,
    )
    polygon = layout.slant_rectangle(along, layout.DOWEL_BOSS_DIAMETER_MM, outward_range)
    return plan_prism(polygon, FLOOR_UNDERSIDE_Z_MM, layout.DOWEL_BOSS_TOP_Z_MM)


def require_inside(body, outside, what):
    poking = body.cut(outside).Volume
    if poking > NOTHING_LEFT_MM3:
        raise SystemExit(f"error: {what} pokes {poking:.4f} mm3 past the tray's outer face")


def boss_bodies(corner_radius, right):
    """(label, body) of the half's dowel bosses, the parking hole's boss
    and the fills that close the crevices beside the bosses, each
    checked to lie inside the tray's rounded outer face as the layout
    gives it (a dowel boss up to the joint face)."""
    outside = outer_prism(RIM_Z_MM, corner_radius)
    bodies = []
    for along in layout.DOWEL_PIN_ALONGS_MM:
        label = f"the dowel boss at {along} along the slant"
        full = plan_prism(
            layout.dowel_boss_polygon(along, right),
            FLOOR_UNDERSIDE_Z_MM,
            layout.DOWEL_BOSS_TOP_Z_MM,
        )
        require_inside(full, outside, label)
        bodies.append((label, dowel_boss_body(along, right)))
    under_the_pcb = (
        ("the parking hole's boss", layout.parking_boss_polygon()),
        ("the parking boss's fill", layout.parking_boss_fill_polygon()),
        ("the upper dowel boss's fill", layout.upper_boss_fill_polygon(right)),
    )
    for label, polygon in under_the_pcb:
        body = plan_prism(polygon, FLOOR_UNDERSIDE_Z_MM, layout.PCB_UNDERSIDE_Z_MM)
        require_inside(body, outside, label)
        bodies.append((label, body))
    return bodies


def add_bosses(tray, corner_radius, right):
    """Fuse the bosses and fills one by one (the lower dowel boss and the
    parking boss overlap, which one boolean with both would not take),
    each adding plastic but no more than its own volume, and solid at
    its center of mass afterwards."""
    for label, body in boss_bodies(corner_radius, right):
        result = tray.fuse(body)
        require_one_valid_solid(result, f"adding {label}")
        added = result.Volume - tray.Volume
        if not NOTHING_LEFT_MM3 < added <= body.Volume + NOTHING_LEFT_MM3:
            raise SystemExit(
                f"error: {label} added {added:.3f} mm3, its body is {body.Volume:.3f} mm3"
            )
        if not is_solid_at(result, body.CenterOfMass):
            raise SystemExit(f"error: {label} is not solid at its center of mass")
        tray = result
    return tray


def ledge_cutter(cut, cavity):
    """A TrayCut's box as a cutter. A pocket is cut as given. Any other
    cut is clipped to the cavity and runs on above the ledge top through
    the open cavity when it reaches that top."""
    bottom, top = cut.z_range
    if not cut.cuts_wall and abs(top - LEDGE_TOP_Z_MM) < 1e-9:
        top += CUT_EXTRA_MM
    cutter = plan_prism(layout.tray_cut_polygon(cut), bottom, top)
    if cut.cuts_wall:
        return cutter
    return cutter.common(cavity)


def edge_probe(cut, along, across, z):
    x, y = layout.outline_edge_point(cut.edge_index, along, across)
    return App.Vector(x, y, z)


def check_ledge_cut(before, after, cut):
    """A ledge cut opened the ledge, in the middle of its part of the
    ledge's width, and left the wall behind it wherever the wall was
    (kbdkid4's probes)."""
    low, high = cut.along_range
    middle_z = sum(cut.z_range) / 2.0
    in_ledge = (max(cut.across_range[0], -layout.ledge_reach())
                + min(cut.across_range[1], layout.TRAY_GAP_MM)) / 2.0
    if is_solid_at(after, edge_probe(cut, (low + high) / 2.0, in_ledge, middle_z)):
        raise SystemExit(f"error: the {cut.label} did not open the ledge")
    in_wall = layout.TRAY_GAP_MM + layout.TRAY_WALL_MM / 2.0
    for along in (low + 0.2, (low + high) / 2.0, high - 0.2):
        probe = edge_probe(cut, along, in_wall, middle_z)
        if is_solid_at(before, probe) and not is_solid_at(after, probe):
            raise SystemExit(f"error: the {cut.label} cut into the wall")


def check_pocket(after, cut):
    """A pocket opened the wall's inner face over its width, left the
    wall's outer skin, and left the wall beside it (kbdkid4's probes)."""
    low, high = cut.along_range
    middle_z = sum(cut.z_range) / 2.0
    pocket_side = cut.across_range[1]
    pocket_middle = (layout.TRAY_GAP_MM + pocket_side) / 2.0
    skin_middle = (pocket_side + layout.TRAY_GAP_MM + layout.TRAY_WALL_MM) / 2.0
    for along in (low + PROBE_OFFSET_MM, high - PROBE_OFFSET_MM):
        if is_solid_at(after, edge_probe(cut, along, pocket_middle, middle_z)):
            raise SystemExit(f"error: the {cut.label} did not open the wall's inner face")
        if not is_solid_at(after, edge_probe(cut, along, skin_middle, middle_z)):
            raise SystemExit(f"error: the {cut.label} cut through the wall's skin")
    for along in (low - PROBE_OFFSET_MM, high + PROBE_OFFSET_MM):
        if not is_solid_at(after, edge_probe(cut, along, pocket_middle, middle_z)):
            raise SystemExit(f"error: the wall beside the {cut.label} is missing")


def apply_tray_cut(tray, cut, cavity):
    """(tray, removed volume) after a TrayCut, or (tray, None) when it
    finds nothing left to remove."""
    cutter = ledge_cutter(cut, cavity)
    removable = tray.common(cutter).Volume if cutter.Solids else 0.0
    if removable < NOTHING_LEFT_MM3:
        return tray, None
    result = tray.cut(cutter)
    require_one_valid_solid(result, f"the {cut.label}")
    require_volume(f"the {cut.label}", tray.Volume - result.Volume, removable, 0.02)
    if cut.cuts_wall:
        check_pocket(result, cut)
    else:
        check_ledge_cut(tray, result, cut)
    return result, tray.Volume - result.Volume


def circular_segment_area(radius, chord_distance):
    """The area of the part of a circle beyond a chord at chord_distance
    from its center."""
    half_chord = math.sqrt(radius**2 - chord_distance**2)
    return radius**2 * math.acos(chord_distance / radius) - chord_distance * half_chord


def standoff_flat_cutter(flat):
    """The half-space beyond a flat's plane, as far as the standoff
    reaches, over the flat's height and on through the open cavity."""
    reach = layout.STANDOFF_DIAMETER_MM / 2.0 + 0.5
    center = App.Vector(flat.standoff_center[0], flat.standoff_center[1], flat.z_range[0])
    toward = App.Vector(flat.toward[0], flat.toward[1], 0.0)
    along_flat = toward.cross(UP)
    corners = [
        center.add(toward * flat.plane_distance).add(along_flat * -reach),
        center.add(toward * flat.plane_distance).add(along_flat * reach),
        center.add(toward * reach).add(along_flat * reach),
        center.add(toward * reach).add(along_flat * -reach),
    ]
    height = flat.z_range[1] - flat.z_range[0] + CUT_EXTRA_MM
    return Part.Face(Part.makePolygon(corners + [corners[0]])).extrude(UP * height)


def check_standoff_flat(before, after, flat):
    """The flat opened beyond its plane, kept the bore's wall, and did
    not reach below its bottom (kbdkid4's probes)."""
    radius = layout.STANDOFF_DIAMETER_MM / 2.0
    bore_radius = layout.STANDOFF_BORE_DIAMETER_MM / 2.0
    toward = App.Vector(flat.toward[0], flat.toward[1], 0.0)
    bottom, top = flat.z_range

    def probe(radial, z):
        return App.Vector(flat.standoff_center[0], flat.standoff_center[1], z).add(toward * radial)

    middle = (bottom + top) / 2.0
    beyond = (flat.plane_distance + radius) / 2.0
    if is_solid_at(after, probe(beyond, middle)):
        raise SystemExit(f"error: the {flat.label} did not open the flat")
    if not is_solid_at(after, probe((bore_radius + flat.plane_distance) / 2.0, middle)):
        raise SystemExit(f"error: the {flat.label} cut into the bore's wall")
    below = probe(beyond, bottom - PROBE_OFFSET_MM)
    if is_solid_at(before, below) and not is_solid_at(after, below):
        raise SystemExit(f"error: the {flat.label} reaches too low")


def apply_standoff_flat(tray, flat):
    """(tray, removed volume) after a standoff flat, or (tray, None)
    when an earlier flat on the standoff already opened it."""
    cutter = standoff_flat_cutter(flat)
    removable = tray.common(cutter).Volume
    if removable < NOTHING_LEFT_MM3:
        return tray, None
    height = flat.z_range[1] - flat.z_range[0]
    segment = (
        circular_segment_area(layout.STANDOFF_DIAMETER_MM / 2.0, flat.plane_distance) * height
    )
    if removable > 1.002 * segment + NOTHING_LEFT_MM3:
        raise SystemExit(
            f"error: the {flat.label} would remove {removable:.3f} mm3, more than the "
            f"standoff's {segment:.3f} mm3 beyond the flat: it reaches something else"
        )
    result = tray.cut(cutter)
    require_one_valid_solid(result, f"the {flat.label}")
    require_volume(f"the {flat.label}", tray.Volume - result.Volume, removable, 0.02)
    check_standoff_flat(tray, result, flat)
    return result, tray.Volume - result.Volume


def slant_probe(along, outward, z):
    x, y = layout.slant_point(along, outward)
    return App.Vector(x, y, z)


def cut_magnet_slot(tray, along):
    """Cut a magnet slot from its bottom up through the block's top and
    on to the rim, which also cuts the wall back to the slot's face side
    above the block. All of it lies in plastic: the slot in the block
    and the floor, the cut-back in the wall. The slot's inner side lies
    on the block's inner face, so it opens toward the cavity, but where
    a standoff merges with the block: the sixth standoff walls off the
    south 2.165 of the slot at 48.26 along the slant, flush with that
    face, so the slot still prints 3.1 across there and the magnet still
    drops in from the top."""
    bottom = layout.MAGNET_SLOT_BOTTOM_Z_MM
    cutter = plan_prism(layout.magnet_slot_polygon(along), bottom, RIM_Z_MM + CUT_EXTRA_MM)
    result = tray.cut(cutter)
    label = f"the magnet slot at {along} along the slant"
    require_one_valid_solid(result, label)
    cutback = layout.magnet_wall_cutback_outward()
    expected = layout.MAGNET_SLOT_ALONG_MM * (
        layout.MAGNET_SLOT_ACROSS_MM * (layout.JOINT_BLOCK_TOP_Z_MM - bottom)
        + (cutback - layout.TRAY_GAP_MM) * (RIM_Z_MM - layout.JOINT_BLOCK_TOP_Z_MM)
    )
    require_volume(label, tray.Volume - result.Volume, expected, 1e-6)
    inner_side, face_side = layout.magnet_slot_outward_range()
    face = layout.JOINT_FACE_OUTWARD_MM
    middle_z = (bottom + layout.JOINT_BLOCK_TOP_Z_MM) / 2.0
    wall_z = (layout.JOINT_BLOCK_TOP_Z_MM + RIM_Z_MM) / 2.0
    for outward, z, want_solid, what in (
        ((inner_side + face_side) / 2.0, middle_z, False, "open"),
        (inner_side - PROBE_OFFSET_MM, middle_z, False, "open toward the cavity"),
        ((face_side + face) / 2.0, middle_z, True, "behind its skin"),
        ((inner_side + face_side) / 2.0, bottom - 0.25, True, "above its floor"),
        ((layout.TRAY_GAP_MM + cutback) / 2.0, wall_z, False, "open through the cut-back"),
        ((cutback + face) / 2.0, wall_z, True, "behind the cut-back's wall"),
    ):
        if is_solid_at(result, slant_probe(along, outward, z)) != want_solid:
            raise SystemExit(f"error: {label} is not {what}")
    return result


def teardrop_flat_half_width(radius):
    """Half the flat of a flat-topped teardrop: where its 45 degree
    sides cross the circle's top."""
    return radius * (math.sqrt(2.0) - 1.0)


def teardrop_area(radius):
    """A circle with a 45 degree point, cut flat at the circle's top:
    three quarters of the circle and the radius squared of the point's
    kite, less the triangle above the flat."""
    return 0.75 * math.pi * radius**2 + radius**2 - teardrop_flat_half_width(radius) ** 2


def teardrop_wire(center, axis, radius):
    """A flat-topped teardrop in the plane square to the horizontal unit
    axis through center: a circle of radius with a 45 degree point up,
    so the hole prints horizontal without support, cut flat at the
    circle's top, so the pin bears upward on that flat's bridge."""
    side = UP.cross(axis)
    tangent = radius / math.sqrt(2.0)
    flat = teardrop_flat_half_width(radius)

    def point(along_side, height):
        return center.add(side * along_side).add(UP * height)

    return Part.Wire(
        [
            Part.Arc(
                point(tangent, tangent), point(0.0, -radius), point(-tangent, tangent)
            ).toShape(),
            Part.LineSegment(point(-tangent, tangent), point(-flat, radius)).toShape(),
            Part.LineSegment(point(-flat, radius), point(flat, radius)).toShape(),
            Part.LineSegment(point(flat, radius), point(tangent, tangent)).toShape(),
        ]
    )


def teardrop_prism(start, axis, radius, length):
    """A flat-topped teardrop prism from start along the horizontal unit
    axis."""
    return Part.Face(teardrop_wire(start, axis, radius)).extrude(axis * length)


def cut_teardrop_hole(tray, mouth, axis, radius, depth, label):
    """Cut a teardrop hole depth deep into the tray from its mouth on an
    outer face along axis, its cutter starting CUT_EXTRA_MM outside. All
    of the hole lies in plastic, with plastic past its bottom, below it
    and above its point."""
    cutter = teardrop_prism(mouth.sub(axis * CUT_EXTRA_MM), axis, radius, depth + CUT_EXTRA_MM)
    result = tray.cut(cutter)
    require_one_valid_solid(result, label)
    require_volume(label, tray.Volume - result.Volume, teardrop_area(radius) * depth, 1e-4)
    middle = mouth.add(axis * (depth / 2.0))
    for point, want_solid, what in (
        (middle, False, "open"),
        (mouth.add(axis * (depth + 0.1)), True, "closed at its bottom"),
        (middle.add(UP * (radius + 0.2)), True, "under plastic"),
        (middle.add(UP * -(radius + 0.2)), True, "over plastic"),
    ):
        if is_solid_at(result, point) != want_solid:
            raise SystemExit(f"error: {label} is not {what}")
    return result


def lead_in_volume(radius, lead_in):
    """What a lead-in chamfer removes at a flat-topped teardrop hole's
    mouth: the teardrop growing from radius to radius plus lead_in over
    the lead_in toward the mouth, less the hole there."""
    per_radius_squared = teardrop_area(1.0)
    grown = per_radius_squared * ((radius + lead_in) ** 3 - radius**3) / 3.0
    return grown - per_radius_squared * radius**2 * lead_in


def cut_lead_in(tray, mouth, axis, radius, lead_in, label):
    """Chamfer a flat-topped teardrop hole's mouth by lead_in at 45
    degrees: a ruled loft from the hole's own teardrop lead_in inside
    the mouth out to one 2 lead_in larger in radius lead_in outside it,
    so it crosses the face at radius plus lead_in."""
    inner = teardrop_wire(mouth.add(axis * lead_in), axis, radius)
    outer = teardrop_wire(mouth.sub(axis * lead_in), axis, radius + 2.0 * lead_in)
    cutter = Part.makeLoft([outer, inner], True, True)
    result = tray.cut(cutter)
    require_one_valid_solid(result, label)
    require_volume(label, tray.Volume - result.Volume, lead_in_volume(radius, lead_in), 1e-3)
    side = UP.cross(axis)
    at_face = mouth.add(axis * 0.05)
    for point, want_solid, what in (
        (at_face.add(side * (radius + lead_in - 0.1)), False, "open at the face"),
        (at_face.add(side * (radius + lead_in + 0.1)), True, "no wider than its size"),
        (mouth.add(axis * (lead_in + 0.05)).add(side * (radius + 0.05)), True, "this short"),
    ):
        if is_solid_at(result, point) != want_solid:
            raise SystemExit(f"error: {label} is not {what}")
    return result


def cut_dowel_hole(tray, along, radius, depth, lead_in):
    normal = layout.slant_outward_normal()
    mouth = slant_probe(along, layout.JOINT_FACE_OUTWARD_MM, layout.DOWEL_PIN_Z_MM)
    axis = App.Vector(-normal[0], -normal[1], 0.0)
    label = f"the dowel pin hole at {along} along the slant"
    tray = cut_teardrop_hole(tray, mouth, axis, radius, depth, label)
    if lead_in > 0.0:
        tray = cut_lead_in(tray, mouth, axis, radius, lead_in, f"{label}'s lead-in")
    return tray


def cut_parking_hole(tray):
    mouth = App.Vector(
        layout.parking_hole_x_range()[1], layout.PARKING_HOLE_Y_MM, layout.PARKING_HOLE_Z_MM
    )
    return cut_teardrop_hole(
        tray,
        mouth,
        App.Vector(-1.0, 0.0, 0.0),
        layout.PARKING_HOLE_DIAMETER_MM / 2.0,
        layout.PARKING_HOLE_DEPTH_MM,
        "the parking hole",
    )


def joint_chamfer_wedge(corner_radius):
    """The wedge beyond the joint face's bottom chamfer's plane, along
    the slant and a corner radius past each of its ends, where the
    chamfer runs out on the corner rounds."""
    size = layout.JOINT_FACE_BOTTOM_CHAMFER_MM
    face = layout.JOINT_FACE_OUTWARD_MM
    bed = FLOOR_UNDERSIDE_Z_MM
    start = -corner_radius
    length = layout.slant_length() + 2.0 * corner_radius
    corners = [
        slant_probe(start, face - size - CUT_EXTRA_MM, bed - CUT_EXTRA_MM),
        slant_probe(start, face + CUT_EXTRA_MM, bed - CUT_EXTRA_MM),
        slant_probe(start, face + CUT_EXTRA_MM, bed + size + CUT_EXTRA_MM),
    ]
    direction_x, direction_y = layout.slant_direction()
    return Part.Face(Part.makePolygon(corners + [corners[0]])).extrude(
        App.Vector(direction_x, direction_y, 0.0) * length
    )


def chamfer_joint_face_bottom(tray, corner_radius):
    """Chamfer the joint face's bottom edge at 45 degrees, along the
    slant and a corner radius past each of its ends, where the chamfer
    runs out on the corner rounds: cut the wedge beyond the chamfer's
    plane, extruded along the slant."""
    size = layout.JOINT_FACE_BOTTOM_CHAMFER_MM
    face = layout.JOINT_FACE_OUTWARD_MM
    bed = FLOOR_UNDERSIDE_Z_MM
    length = layout.slant_length() + 2.0 * corner_radius
    result = tray.cut(joint_chamfer_wedge(corner_radius))
    require_one_valid_solid(result, "the joint face's bottom chamfer")
    removed = tray.Volume - result.Volume
    per_length = size**2 / 2.0
    if not per_length * layout.slant_length() <= removed <= per_length * length:
        raise SystemExit(
            f"error: the joint face's bottom chamfer removed {removed:.4f} mm3, expected "
            f"{per_length * layout.slant_length():.4f} to {per_length * length:.4f} mm3"
        )
    middle = layout.slant_length() / 2.0
    for outward, z, want_solid, what in (
        (face - size / 4.0, bed + size / 4.0, False, "open at the edge"),
        (face - size - PROBE_OFFSET_MM, bed + 0.05, True, "this short on the bed"),
        (face - 0.05, bed + size + PROBE_OFFSET_MM, True, "this short up the face"),
    ):
        if is_solid_at(result, slant_probe(middle, outward, z)) != want_solid:
            raise SystemExit(f"error: the joint face's bottom chamfer is not {what}")
    return result


# The floor stays closed (work item 009): no void the tray cuts may
# reach the floor's underside, which lies on the bed. The underside is
# checked against the void-free footprint, the outside's bottom face
# less the joint face's bottom chamfer, so a hole anywhere in it, or a
# notch at its edge, shows as footprint the underside lacks.
BED_OPENING_TOLERANCE_MM2 = 1e-4


def bed_faces(shape):
    """The shape's planar faces lying on the floor's underside."""
    return [
        face for face in shape.Faces
        if isinstance(face.Surface, Part.Plane)
        and abs(face.BoundBox.ZMin - FLOOR_UNDERSIDE_Z_MM) < INSIDE_TOLERANCE_MM
        and abs(face.BoundBox.ZMax - FLOOR_UNDERSIDE_Z_MM) < INSIDE_TOLERANCE_MM
    ]


def void_free_footprint(corner_radius):
    """The floor's underside as it is with no void: the outside's bottom
    face less the joint face's bottom chamfer."""
    outside = outer_prism(FLOOR_UNDERSIDE_Z_MM + 1.0, corner_radius)
    bottom = Part.makeCompound(bed_faces(outside))
    return bottom.cut(joint_chamfer_wedge(corner_radius))


def check_floor_closed(tray, corner_radius):
    """Fail when any void reaches the floor's underside: the footprint
    the underside lacks must be none. Returns the underside's area."""
    footprint = void_free_footprint(corner_radius)
    underside = Part.makeCompound(bed_faces(tray))
    openings = [face for face in footprint.cut(underside).Faces
                if face.Area > BED_OPENING_TOLERANCE_MM2]
    if openings:
        where = ", ".join(
            f"{face.Area:.3f} mm2 at x {face.BoundBox.XMin:.3f} to {face.BoundBox.XMax:.3f}, "
            f"y {face.BoundBox.YMin:.3f} to {face.BoundBox.YMax:.3f}"
            for face in openings
        )
        raise SystemExit(f"error: {len(openings)} voids reach the floor's underside: {where}")
    area = sum(face.Area for face in bed_faces(tray))
    if abs(area - footprint.Area) > BED_OPENING_TOLERANCE_MM2:
        raise SystemExit(f"error: the floor's underside is {area:.4f} mm2, the void-free "
                         f"footprint {footprint.Area:.4f} mm2")
    return area


# The parts' mounts (work item 004): layout.py gives every body and void
# as a MountBox. The bodies are fused one by one after the standoffs'
# flats, so a body can fill a ledge cut-away's margins, then the
# voids are cut. A body is built without the standoffs' bores it
# reaches, so a standoff a body met would keep its bore. Each is
# checked against a volume worked
# out from the layout alone where the tray around it is known (the
# nice!nano's bodies, the voids in the wall, the clamp's block and
# foot), and probed.


def box_prism(box, extra_below=0.0, extra_above=0.0):
    """A MountBox as a solid, its z range run on by the
    given extras."""
    return plan_prism(layout.plan_corners(box), box.z_range[0] - extra_below,
                      box.z_range[1] + extra_above)


def box_point(box, x_fraction=0.5, y_fraction=0.5, z=None):
    """A point inside a box at the given fractions of its x and y ranges,
    at its middle height unless z is given."""
    (low_x, high_x), (low_y, high_y) = box.x_range, box.y_range
    if z is None:
        z = sum(box.z_range) / 2.0
    return App.Vector(
        low_x + x_fraction * (high_x - low_x), low_y + y_fraction * (high_y - low_y), z
    )


def range_overlap(first, second):
    return max(0.0, min(first[1], second[1]) - max(first[0], second[0]))


def box_overlap_volume(first, second):
    return (
        range_overlap(first.x_range, second.x_range)
        * range_overlap(first.y_range, second.y_range)
        * range_overlap(first.z_range, second.z_range)
    )


def box_volume(box):
    return box_overlap_volume(box, box)


def box_ranges(box):
    return (box.x_range, box.y_range, box.z_range)


def union_overlap_volume(box, others):
    """The volume a box shares with the union of other boxes: the box cut
    into cells at every face of the others, each cell counted whole when
    its middle lies inside one of them."""
    cuts = []
    for axis, (low, high) in enumerate(box_ranges(box)):
        values = {low, high}
        for other in others:
            values.update(min(max(value, low), high) for value in box_ranges(other)[axis])
        cuts.append(sorted(values))
    volume = 0.0
    for cell in itertools.product(*(zip(values, values[1:]) for values in cuts)):
        middle = [(low + high) / 2.0 for low, high in cell]
        if any(all(low < value < high for value, (low, high) in zip(middle, box_ranges(other)))
               for other in others):
            volume += math.prod(high - low for low, high in cell)
    return volume


def disc_quadrant_area(x, y, radius):
    """The disc's area about the origin between the axes and the point
    (x, y), signed negative when one of x and y is."""
    sign = math.copysign(1.0, x) * math.copysign(1.0, y)
    return sign * disc_corner_area(min(abs(x), radius), min(abs(y), radius), radius)


def rectangle_disc_area(x_range, y_range, center, radius):
    """The area a rectangle shares with the disc about center."""
    return sum(
        x_sign * y_sign * disc_quadrant_area(x - center[0], y - center[1], radius)
        for x, x_sign in zip(x_range, (-1.0, 1.0))
        for y, y_sign in zip(y_range, (-1.0, 1.0))
    )


def standoff_overlap_volume(box):
    """The volume a box shares with the standoffs, bores and all."""
    radius = layout.STANDOFF_DIAMETER_MM / 2.0
    height = range_overlap(box.z_range, (FLOOR_UNDERSIDE_Z_MM, LEDGE_TOP_Z_MM))
    return height * sum(rectangle_disc_area(box.x_range, box.y_range, center, radius)
                        for center in layout.MOUNTING_DRILL_CENTERS_MM)


def mount_body_solid(box):
    """A mount body's box less the standoffs' bores it reaches, so the
    fuse leaves them open."""
    body = box_prism(box)
    radius = layout.STANDOFF_BORE_DIAMETER_MM / 2.0
    for x, y in layout.MOUNTING_DRILL_CENTERS_MM:
        if rectangle_disc_area(box.x_range, box.y_range, (x, y), radius) > 0.0:
            height = LEDGE_TOP_Z_MM + CUT_EXTRA_MM
            body = body.cut(Part.makeCylinder(radius, height, App.Vector(x, y, 0.0), UP))
    require_one_valid_solid(body, f"the {box.label}'s body")
    return body.Solids[0]


def fuse_mount_body(tray, label, body):
    """(tray, added volume) after fusing a mount body: one valid solid,
    more plastic but no more than the body, solid at the body's center
    of mass."""
    result = tray.fuse(body)
    require_one_valid_solid(result, f"adding the {label}")
    added = result.Volume - tray.Volume
    if not NOTHING_LEFT_MM3 < added <= body.Volume + NOTHING_LEFT_MM3:
        raise SystemExit(
            f"error: the {label} added {added:.3f} mm3, its body is {body.Volume:.3f} mm3"
        )
    if not is_solid_at(result, body.CenterOfMass):
        raise SystemExit(f"error: the {label} is not solid at its center of mass")
    return result, added


def require_solid_at(tray, point, want_solid, what):
    if is_solid_at(tray, point) != want_solid:
        raise SystemExit(f"error: {what}")


def stands_on(box, point, others):
    """Whether one of the other boxes stands on the box's top at the
    point in plan, as the walls' raised pieces stand on the walls."""
    return any(abs(other.z_range[0] - box.z_range[1]) < 1e-9
               and other.x_range[0] < point.x < other.x_range[1]
               and other.y_range[0] < point.y < other.y_range[1]
               for other in others)


def body_probe_fractions(box, others=()):
    """Where in a body's box, as fractions of its x and y ranges, to probe
    its top: its middle, or failing that the middle of a tenth of the box
    at one of its faces, or a point along its middle line, the first
    clear of the standoffs and of the other boxes that stand on it."""
    radius = layout.STANDOFF_DIAMETER_MM / 2.0
    candidates = ((0.5, 0.5), (0.5, 0.95), (0.5, 0.05), (0.95, 0.5), (0.05, 0.5)) + tuple(
        (0.5, index / 20.0) for index in range(1, 20))
    for fractions in candidates:
        point = box_point(box, *fractions)
        if (all(math.hypot(point.x - x, point.y - y) > radius + 0.05
                for x, y in layout.MOUNTING_DRILL_CENTERS_MM)
                and not stands_on(box, point, others)):
            return fractions
    raise SystemExit(f"error: no point in the {box.label} clear of the standoffs and the "
                     "bodies on it to probe")


def check_nano_bodies(tray, fits):
    """The nice!nano's bodies stand this tall and no taller, where no
    other body stands on them, and the foot's north face is where the
    board's south end stops."""
    bodies = layout.nano_bodies(fits)
    for box in bodies:
        top = box.z_range[1]
        fractions = body_probe_fractions(box, bodies)
        require_solid_at(tray, box_point(box, *fractions, z=top - 0.05), True,
                         f"the {box.label} is not this tall")
        require_solid_at(tray, box_point(box, *fractions, z=top + 0.05), False,
                         f"the {box.label} is taller")
    foot = layout.nano_clamp_boxes(fits)[1]
    stop_y = foot.y_range[1]
    middle_x = sum(layout.nano_clamp_tab_x_range(fits)) / 2.0
    # Over the seat, which runs on north from the stop.
    over_seat = (layout.NANO_SEAT_HEIGHT_MM + foot.z_range[1]) / 2.0
    for y, want_solid, how in ((stop_y - 0.05, True, "ending at the stop"),
                               (stop_y + 0.05, False, "open in front of the stop")):
        require_solid_at(tray, App.Vector(middle_x, y, over_seat), want_solid,
                         f"the clamp's foot is not {how}")


def add_mounts(tray, fits):
    """Fuse every mount body layout.py gives, in its order. Returns
    (tray, (label, added volume) of each). The nice!nano's bodies stand
    on the open floor, against the ledge's and the wall's faces, so each
    adds its box less what the bodies fused before it and the standoffs
    took of it, no body fused before them meeting a standoff and no two
    of them overlapping inside one."""
    bodies = layout.mount_bodies(fits)
    added_volumes = []
    for index, box in enumerate(bodies):
        tray, added = fuse_mount_body(tray, box.label, mount_body_solid(box))
        if box.part == "nice!nano":
            expected = (box_volume(box) - union_overlap_volume(box, bodies[:index])
                        - standoff_overlap_volume(box))
            require_volume(f"the {box.label}", added, expected, 1e-6)
        added_volumes.append((box.label, added))
    check_nano_bodies(tray, fits)
    return tray, added_volumes


def rounded_rectangle_wire(center, along_axis, up_axis, half_width, half_height, radius):
    """A rectangle with rounded corners in the plane spanned by two unit
    vectors, centered on `center`: `half_width` along `along_axis`,
    `half_height` along `up_axis`. Its edges always run arc, line, arc,
    line, ... from the same corner, so two such wires loft edge to edge
    (kbdkid4's export_tray.py)."""

    def point(along, height):
        return center.add(along_axis * along).add(up_axis * height)

    inner_along = half_width - radius
    inner_height = half_height - radius
    corner_centers = (  # counterclockwise from the bottom one along +along_axis
        (inner_along, -inner_height),
        (inner_along, inner_height),
        (-inner_along, inner_height),
        (-inner_along, -inner_height),
    )
    arcs = []
    for index, (corner_along, corner_height) in enumerate(corner_centers):
        start = -90.0 + 90.0 * index
        arcs.append([
            point(
                corner_along + radius * math.cos(math.radians(start + step)),
                corner_height + radius * math.sin(math.radians(start + step)),
            )
            for step in (0.0, 45.0, 90.0)
        ])
    edges = []
    for index, arc in enumerate(arcs):
        edges.append(Part.Arc(*arc).toShape())
        edges.append(Part.LineSegment(arc[2], arcs[(index + 1) % 4][0]).toShape())
    return Part.Wire(edges)


def rounded_rectangle_area(half_width, half_height, radius):
    return 4.0 * half_width * half_height - (4.0 - math.pi) * radius**2


def rounded_rectangle_perimeter(half_width, half_height, radius):
    return 4.0 * (half_width + half_height) - 2.0 * (4.0 - math.pi) * radius


def chamfer_volume(perimeter, size):
    """The volume a 45 degree chamfer of `size` takes out of a face
    around a rounded rectangle opening of the given perimeter
    (kbdkid4's)."""
    return perimeter * size**2 / 2.0 + math.pi * size**3 / 3.0


def disc_corner_area(width, height, radius):
    """The area of the box [0, width] x [0, height] inside the disc of
    the given radius about the origin, width no more than the radius."""
    knee = math.sqrt(radius**2 - min(height, radius) ** 2)
    if knee >= width:
        return width * height

    def under_arc(x):
        return (x * math.sqrt(radius**2 - x**2) + radius**2 * math.asin(x / radius)) / 2.0

    return height * knee + under_arc(width) - under_arc(knee)


def rectangle_in_window_area(x_range, z_range, center, half_width, half_height, radius):
    """The area of an upright rectangle inside a window with rounded
    corners around center (x, z), for a rectangle across the window's
    corner centers both ways: the rectangle within the window's bounds
    less, at each corner, what lies beyond the corner's round."""
    center_x, center_z = center
    low_x = max(x_range[0], center_x - half_width)
    high_x = min(x_range[1], center_x + half_width)
    low_z = max(z_range[0], center_z - half_height)
    high_z = min(z_range[1], center_z + half_height)
    area = (high_x - low_x) * (high_z - low_z)
    for beyond_x in (high_x - (center_x + half_width - radius),
                     (center_x - half_width + radius) - low_x):
        for beyond_z in (high_z - (center_z + half_height - radius),
                         (center_z - half_height + radius) - low_z):
            width, height = max(beyond_x, 0.0), max(beyond_z, 0.0)
            area -= width * height - disc_corner_area(width, height, radius)
    return area


def check_usb_window(tray, middle, half_width, half_height, radius, chamfer, thickness):
    """kbdkid4's probes of its rounded window, on the wall's outer face
    only: open inside its edges and solid just outside them in the wall,
    the chamfer open just outside the edges near the outer face but no
    wider than the chamfer, and the corners rounded. `middle` lies on
    the window's south face, the shell's mouth, the wall `thickness`
    along +y from it. The wall is probed halfway to the chamfer, where
    the shell's channel runs on past the mouth (into the chamfer's
    depth, for the board's play north) but lies inside the window's
    outline except at the corners, short of the corner probes' solid
    points."""
    across = App.Vector(1.0, 0.0, 0.0)
    through = App.Vector(0.0, 1.0, 0.0)

    def solid(along, depth, height):
        return is_solid_at(tray, middle.add(across * along).add(through * depth).add(UP * height))

    mid_wall = (thickness - chamfer) / 2.0
    near_face = thickness - chamfer / 4.0
    if solid(0.0, mid_wall, 0.0):
        raise SystemExit("error: the USB window did not open the wall")
    for along_sign, height_sign in ((1, 0), (-1, 0), (0, 1), (0, -1)):

        def beyond_edge(distance):
            return (along_sign * (half_width + distance), height_sign * (half_height + distance))

        along, height = beyond_edge(-0.05)
        if solid(along, mid_wall, height):
            raise SystemExit("error: the USB window is smaller than intended")
        along, height = beyond_edge(0.05)
        if not solid(along, mid_wall, height):
            raise SystemExit("error: the USB window is larger than intended")
        if solid(along, near_face, height):
            raise SystemExit("error: the USB window's chamfer is missing")
        along, height = beyond_edge(chamfer + 0.1)
        if not solid(along, near_face, height):
            raise SystemExit("error: the USB window's chamfer is too wide")
    for along_sign in (1, -1):
        for height_sign in (1, -1):
            corner_along = along_sign * (half_width - radius)
            corner_height = height_sign * (half_height - radius)
            for fraction, want_solid in ((0.6, False), (0.9, True)):
                offset = fraction * radius
                if solid(corner_along + along_sign * offset, mid_wall,
                         corner_height + height_sign * offset) != want_solid:
                    raise SystemExit(
                        f"error: the USB window's corners are not rounded with {radius} mm"
                    )


def cut_usb_shell_channel(tray, fits):
    """The shell's channel through the wall's inner part, its cutter run
    on into the north block's opening under its bar, so it removes its
    box from the solid wall."""
    box = layout.usb_shell_channel_box(fits)
    inner, north = box.y_range
    cutter_box = layout.MountBox(
        box.label, box.part, box.x_range, (inner - 0.5, north), box.z_range
    )
    result = tray.cut(box_prism(cutter_box))
    require_one_valid_solid(result, "the USB shell's channel")
    require_volume("the USB shell's channel", tray.Volume - result.Volume, box_volume(box), 1e-6)
    middle = box_point(box)
    in_wall = App.Vector(middle.x, (inner + layout.nano_usb_shell_mouth_y()) / 2.0, middle.z)
    for point, want_solid, what in (
        (in_wall, False, "open"),
        (App.Vector(in_wall.x, in_wall.y, box.z_range[1] + 0.05), True, "closed above"),
        (App.Vector(in_wall.x, in_wall.y, box.z_range[0] - 0.05), True, "closed below"),
        (App.Vector(box.x_range[0] - 0.05, in_wall.y, in_wall.z), True, "closed on the west"),
        (App.Vector(box.x_range[1] + 0.05, in_wall.y, in_wall.z), True, "closed on the east"),
    ):
        if is_solid_at(result, point) != want_solid:
            raise SystemExit(f"error: the USB shell's channel is not {what}")
    return result


def check_bar_to_mouth(tray, fits):
    """Over the shell's channel the wall stands on to the shell's mouth,
    where the window opens: the bar's depth."""
    center_x, _center_z = layout.usb_window_center(fits)
    mouth = layout.nano_usb_shell_mouth_y()
    window_top = layout.usb_window_box(fits).z_range[1]
    over_channel = (layout.nano_bar_underside_z(fits) + window_top) / 2.0
    for y, want_solid, what in ((mouth - 0.05, True, "reach"), (mouth + 0.05, False, "stop at")):
        if is_solid_at(tray, App.Vector(center_x, y, over_channel)) != want_solid:
            raise SystemExit(f"error: the bar does not {what} the shell's mouth")


def cut_usb_window(tray, fits):
    """The shell's channel, then kbdkid4's window with rounded corners
    through the north wall from the shell's mouth out, its outer face
    chamfered at 45 degrees (layout.py says why only there): the profile
    at the mouth extruded out past the outer face, and a ruled loft from
    the profile grown by the chamfer and a little more just outside the
    outer face to the profile itself at the chamfer's depth. The wall is
    solid over the whole profile, the floor's thickness below the
    cavity's floor included, but where the channel runs on past the
    mouth, so the cut removes the profile's area through the wall and
    the chamfer, less the channel's part inside the profile."""
    tray = cut_usb_shell_channel(tray, fits)
    box = layout.usb_window_box(fits)
    channel = layout.usb_shell_channel_box(fits)
    center_x, center_z = layout.usb_window_center(fits)
    mouth, outer = box.y_range
    half_width = layout.USB_WINDOW_WIDTH_MM / 2.0
    half_height = layout.USB_WINDOW_HEIGHT_MM / 2.0
    radius = layout.USB_WINDOW_CORNER_RADIUS_MM
    chamfer = layout.USB_WINDOW_CHAMFER_MM
    overshoot = 0.05
    across = App.Vector(1.0, 0.0, 0.0)

    def profile(y, grow):
        return rounded_rectangle_wire(
            App.Vector(center_x, y, center_z), across, UP,
            half_width + grow, half_height + grow, radius + grow,
        )

    through = Part.Face(profile(mouth, 0.0)).extrude(
        App.Vector(0.0, outer - mouth + CUT_EXTRA_MM, 0.0)
    )
    outer_chamfer = Part.makeLoft(
        [profile(outer + overshoot, chamfer + overshoot), profile(outer - chamfer, 0.0)], True, True
    )
    cutter = through.fuse(outer_chamfer)
    if not cutter.isValid() or len(cutter.Solids) != 1:
        raise SystemExit("error: the USB window's cutter is not one solid")
    result = tray.cut(cutter)
    require_one_valid_solid(result, "the USB window")
    area = rounded_rectangle_area(half_width, half_height, radius)
    perimeter = rounded_rectangle_perimeter(half_width, half_height, radius)
    channel_past = channel.y_range[1] - mouth
    in_channel = channel_past * rectangle_in_window_area(
        channel.x_range, channel.z_range, (center_x, center_z), half_width, half_height, radius
    )
    expected = area * (outer - mouth) + chamfer_volume(perimeter, chamfer) - in_channel
    require_volume("the USB window", tray.Volume - result.Volume, expected, 2e-3)
    middle = App.Vector(center_x, mouth, center_z)
    check_usb_window(result, middle, half_width, half_height, radius, chamfer, outer - mouth)
    check_bar_to_mouth(result, fits)
    return result


def cut_knob_slot(tray):
    """The power switch knob's slot through the ledge and the north wall,
    its cutter run on into the open cavity where the switch's body lies
    and out past the outer face, so it removes the slot through the ledge
    and the wall alone."""
    box = layout.power_switch_knob_slot_box()
    inner, outer = box.y_range
    cutter_box = layout.MountBox(
        box.label, box.part, box.x_range, (inner - 0.5, outer + CUT_EXTRA_MM), box.z_range
    )
    result = tray.cut(box_prism(cutter_box))
    require_one_valid_solid(result, "the knob slot")
    require_volume("the knob slot", tray.Volume - result.Volume, box_volume(box), 1e-6)
    middle = box_point(box)
    for point, want_solid, what in (
        (middle, False, "open"),
        (box_point(box, z=box.z_range[1] + 0.05), True, "closed above"),
        (box_point(box, z=box.z_range[0] - 0.05), True, "closed below"),
        (App.Vector(box.x_range[0] - 0.05, middle.y, middle.z), True, "closed on the west"),
        (App.Vector(box.x_range[1] + 0.05, middle.y, middle.z), True, "closed on the east"),
    ):
        if is_solid_at(result, point) != want_solid:
            raise SystemExit(f"error: the knob slot is not {what}")
    return result


def cut_reset_pin_hole(tray):
    """The flat-topped teardrop pin hole through the north wall over the
    reset button's actuator, its cutter run on past both faces."""
    box = layout.reset_pin_hole_box()
    inner, outer = box.y_range
    x, z = layout.reset_pin_hole_center()
    radius = layout.RESET_PIN_HOLE_DIAMETER_MM / 2.0
    axis = App.Vector(0.0, -1.0, 0.0)
    start = App.Vector(x, outer + CUT_EXTRA_MM, z)
    cutter = teardrop_prism(start, axis, radius, outer - inner + 2.0 * CUT_EXTRA_MM)
    result = tray.cut(cutter)
    require_one_valid_solid(result, "the reset pin hole")
    require_volume(
        "the reset pin hole",
        tray.Volume - result.Volume,
        teardrop_area(radius) * (outer - inner),
        1e-4,
    )
    middle = App.Vector(x, (inner + outer) / 2.0, z)
    for point, want_solid, what in (
        (middle, False, "open"),
        (middle.add(UP * (radius - 0.05)), False, "open up to its flat"),
        (middle.add(UP * (radius + 0.05)), True, "closed above its flat"),
        (middle.add(UP * -(radius + 0.05)), True, "closed below"),
        (middle.add(App.Vector(radius + 0.05, 0.0, 0.0)), True, "this narrow"),
    ):
        if is_solid_at(result, point) != want_solid:
            raise SystemExit(f"error: the reset pin hole is not {what}")
    return result


def cut_nano_pry_slot(tray, fits):
    """The pry slot through the clamp's block and foot, its cutter run on
    past both their faces along y and above the block's top, through the
    open cavity: it removes the slot's part of each and leaves the floor
    under it and the block and foot beside it."""
    box = layout.nano_pry_slot_box(fits)
    (south, north), (_bottom, top) = box.y_range, box.z_range
    cutter_box = layout.MountBox(box.label, box.part, box.x_range, (south - 0.5, north + 0.5),
                                 box.z_range)
    result = tray.cut(box_prism(cutter_box, 0.0, CUT_EXTRA_MM))
    require_one_valid_solid(result, "the pry slot")
    expected = sum(box_overlap_volume(box, body) for body in layout.nano_clamp_boxes(fits))
    require_volume("the pry slot", tray.Volume - result.Volume, expected, 1e-6)
    block, foot = layout.nano_clamp_boxes(fits)
    for body in (block, foot):
        middle_y = sum(body.y_range) / 2.0
        middle_z = body.z_range[1] / 2.0
        for x, want_solid, how in ((sum(box.x_range) / 2.0, False, "open at mid height"),
                                   (box.x_range[0] - 0.05, True, "closed on the west"),
                                   (box.x_range[1] + 0.05, True, "closed on the east")):
            require_solid_at(result, App.Vector(x, middle_y, middle_z), want_solid,
                             f"the pry slot is not {how} through the {body.label}")
        require_solid_at(result, App.Vector(sum(box.x_range) / 2.0, middle_y, top + 0.05), False,
                         f"the pry slot is not open above the {body.label}")
    return result


def cut_nano_clamp_bore(tray, fits):
    """Bore the clamp's block for its insert from its top down to the
    floor's top, like a standoff, its cutter run on above the top: it
    removes the bore's cylinder from the block and leaves the floor and
    the block around it."""
    block = layout.nano_clamp_boxes(fits)[0]
    x, y = layout.nano_clamp_screw_center(fits)
    radius = layout.NANO_CLAMP_BORE_DIAMETER_MM / 2.0
    top = block.z_range[1]
    cutter = Part.makeCylinder(radius, top + CUT_EXTRA_MM, App.Vector(x, y, 0.0), UP)
    result = tray.cut(cutter)
    what = "the clamp's insert bore"
    require_one_valid_solid(result, what)
    require_volume(what, tray.Volume - result.Volume, math.pi * radius**2 * top, 1e-6)
    for point, want_solid, how in (
        (App.Vector(x, y, top / 2.0), False, "open"),
        (App.Vector(x, y, -0.05), True, "closed under it"),
        (App.Vector(x + radius + 0.05, y, top / 2.0), True, "this wide"),
    ):
        if is_solid_at(result, point) != want_solid:
            raise SystemExit(f"error: {what} is not {how}")
    return result


def cut_mount_voids(tray, fits):
    """Cut every mount void layout.py gives, in its order: the shell's
    channel and the window, the knob slot and the pin hole through the
    north wall, the pry slot through the clamp's block and foot, and
    bore the clamp's block."""
    tray = cut_usb_window(tray, fits)
    tray = cut_knob_slot(tray)
    tray = cut_reset_pin_hole(tray)
    tray = cut_nano_pry_slot(tray, fits)
    return cut_nano_clamp_bore(tray, fits)


def finish(tray):
    """Merge the faces the booleans split, keeping one valid solid of
    the same volume."""
    merged = tray.removeSplitter()
    require_one_valid_solid(merged, "merging the faces")
    require_volume("the merged tray", merged.Volume, tray.Volume, 1e-9)
    return merged.Solids[0]


def build_tray(right=False, pin_hole_diameter=None, fits=None):
    """The half's tray as one solid in the layout's frame (the right
    half's unmirrored, see the module docstring), and how it came about
    (a Tray). pin_hole_diameter is the half's fit in layout.py unless
    given, fits the mounts' (a layout.MountFits) layout.py's defaults
    unless given."""
    if pin_hole_diameter is None:
        pin_hole_diameter = layout.dowel_hole_diameter(right)
    if fits is None:
        fits = layout.DEFAULT_MOUNT_FITS
    pin_hole_depth = layout.dowel_hole_depth(right)
    lead_in = layout.dowel_hole_lead_in(right)
    outer_wire = layout_polygon_wire(layout.tray_outer_polygon(), 0.0)
    corner_radius = tray_corner_radius(outer_wire, DEFAULT_GAP_MM, DEFAULT_WALL_MM)
    tray, cavity = build_walls(corner_radius)
    tray = add_ledge(tray, corner_radius)
    tray, shelves = add_backing_shelves(tray, corner_radius, right)
    tray = add_standoffs(tray)
    tray = add_bosses(tray, corner_radius, right)
    cuts = []
    skipped = []
    tray_cuts = [layout.ledge_cutaway_cut(cutaway) for cutaway in layout.ledge_cutaways(fits)]
    tray_cuts.append(layout.nano_strip_ledge_pocket(fits))
    tray_cuts.extend(layout.all_socket_tray_cuts(right))
    for cut in tray_cuts:
        tray, removed = apply_tray_cut(tray, cut, cavity)
        if removed is None:
            skipped.append(cut.label)
        else:
            cuts.append((cut.label, removed))
    for flat in layout.all_socket_standoff_flats(right):
        tray, removed = apply_standoff_flat(tray, flat)
        if removed is None:
            skipped.append(flat.label)
        else:
            cuts.append((flat.label, removed))
    tray, mounts = add_mounts(tray, fits)
    tray = cut_mount_voids(tray, fits)
    for along in layout.MAGNET_ALONGS_MM:
        tray = cut_magnet_slot(tray, along)
    for along in layout.DOWEL_PIN_ALONGS_MM:
        tray = cut_dowel_hole(tray, along, pin_hole_diameter / 2.0, pin_hole_depth, lead_in)
    tray = cut_parking_hole(tray)
    tray = chamfer_joint_face_bottom(tray, corner_radius)
    tray = finish(tray)
    bed_area = check_floor_closed(tray, corner_radius)
    return Tray(
        tray,
        right,
        corner_radius,
        pin_hole_diameter,
        pin_hole_depth,
        lead_in,
        cuts,
        skipped,
        fits,
        mounts,
        bed_area,
        shelves,
        layout.backing_shelf_notches(right),
    )


def build_clamp_tab(fits=None):
    """The nice!nano clamp's tab (work item 009), a print of its own, as
    modelled and seated on the fits' block (layout.py's defaults unless
    given) in the layout's frame: the plate on the block's top reaching
    onto the board, the nose under its end, the screw's hole through the
    plate. Checked one valid solid of the plate and the nose less the
    hole."""
    if fits is None:
        fits = layout.DEFAULT_MOUNT_FITS
    plate, nose = layout.nano_clamp_tab_boxes(fits)
    x, y = layout.nano_clamp_screw_center(fits)
    radius = layout.NANO_CLAMP_SCREW_HOLE_DIAMETER_MM / 2.0
    thickness = plate.z_range[1] - plate.z_range[0]
    hole = Part.makeCylinder(radius, thickness + 2.0 * CUT_EXTRA_MM,
                             App.Vector(x, y, plate.z_range[0] - CUT_EXTRA_MM), UP)
    tab = box_prism(plate).fuse(box_prism(nose)).cut(hole).removeSplitter()
    require_one_valid_solid(tab, "the clamp's tab")
    expected = box_volume(plate) + box_volume(nose) - math.pi * radius**2 * thickness
    require_volume("the clamp's tab", tab.Volume, expected, 1e-6)
    return tab.Solids[0]


def build_power_switch_retainer():
    """The power switch's retainer, a print of its own, as modelled and
    fitted in the layout's frame: its legs beside the leads and the bar
    over them. Checked one valid solid of the three boxes' volume."""
    boxes = layout.power_switch_retainer_boxes()
    retainer = box_prism(boxes[0])
    for box in boxes[1:]:
        retainer = retainer.fuse(box_prism(box))
    retainer = retainer.removeSplitter()
    require_one_valid_solid(retainer, "the power switch's retainer")
    require_volume("the power switch's retainer", retainer.Volume,
                   sum(box_volume(box) for box in boxes), 1e-6)
    return retainer.Solids[0]


def mirror_for_right_half(shape):
    """The shape mirrored across the layout's right-half mirror line,
    checked to keep its volume. Mirror before any rotate or translate:
    Shape.mirror drops a placement set by those (observed on FreeCAD 1.0
    in kbdkid4)."""
    mirrored = shape.mirror(
        App.Vector(layout.RIGHT_HALF_MIRROR_X_MM, 0.0, 0.0), App.Vector(1.0, 0.0, 0.0)
    )
    require_one_valid_solid(mirrored, "mirroring the tray")
    require_volume("the mirrored tray", mirrored.Volume, shape.Volume, 1e-9)
    return mirrored
