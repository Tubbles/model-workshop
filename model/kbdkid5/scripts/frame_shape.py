"""The hand-wired frame and its backing (work item 014), both halves:
the first iteration, without diode cradles or wire grooves, the wires
running between the frame's underside and the backing.

The frame is printed in the PCB's place: the PCB mock's body
(pcb_shape.py: the outline pulled in by pull_in with its rounded
corners, the mounting drills grown by it, 1.6 thick) with every key's
footprint holes at the switch hole strip's cell 1 (the center post's
3.42 and the side pegs' 1.90 as modelled, the blades' 3.2, the NC pad's
1.2 grown by pull_in), and, from socket_test_shape.py's cells, each
socket's tab recesses in its underside (the ceiling) and its pocket
walls at layout.FRAME_POCKET_FIT_MM below it. The walls stand whole on
every pocket (work item 026: cut walls print with heavy blobbing and
stringing). The tray gives way to them instead, keeping
layout.FRAME_TRAY_CLEARANCE_MM in plan from their outer face wherever
it stands within their heights (layout.py's cuts for the frame's walls,
held by check_layout.py's check_frame_walls()), and the build fails
where anything of it, or of the parts in it, comes nearer. The
footprint holes run on through the walls, as on the strips. Under the
ceiling stand the bosses at layout.frame_boss_centers()
(socket_test_shape.py's bosses: 5.8 across, ending boss_end_depth()
below the ceiling, bored for an M2 heat-set insert), which the backing
screws up to.

The backing: layout.frame_backing_outline(), 0.8 thick, with the
strips' 2.8 clearance hole for an M2 screw under each boss, the
cutouts layout.py gives (around the standoffs and the tray's bodies
that stand into its heights, and over the nice!nano's socket strips),
and under every socket the pads of the third backing strip's cell 1,
their tops 0.1 under the socket's bottom.

The right half has the outline, the drills, the bosses, the backing's
outline and cutouts and the tray's pieces mirrored across the layout's
right-half mirror line, and each key's socket and holes the left half's
at the mirrored key center, since a socket cannot be mirrored
(layout.py's module docstring). Coordinates: the half's own, z 0 on the
ceiling, the frame's body up to the PCB's thickness, the walls and
bosses below it. The backing is built with its bottom on z = 0.

Every build is checked to be one valid solid of the volume its plan
faces give (each face's area from FreeCAD's 2D booleans, so the 3D
fuses and cuts are checked against them). Like the other *_shape.py
modules this one has no entry point.
"""

import math

import FreeCAD as App
import Part

import check_layout
import layout
import pcb_shape
import socket_test_shape as cells
from tray_shape import CUT_EXTRA_MM, UP, plan_prism, require_one_valid_solid

PULL_IN_MM = pcb_shape.DEFAULT_PULL_IN_MM
# The switch hole strip's cell whose post and peg holes the user chose
# (DESIGN.md, "Switch hole strip").
SWITCH_HOLE_CELL_INDEX = 0
# The pads' figure across the third backing strip: cell 1's.
PAD_CELL_INDEX = 0
# How much nearer than layout.FRAME_TRAY_CLEARANCE_MM the tray may come
# to the walls as built: layout.py steps the socket's arcs by 3 degrees,
# so the walls it gives the tray's cuts lie up to about 0.0005 off the
# walls' true arcs.
WALL_TRAY_TOLERANCE_MM = 0.001
# A circle as a polygon around it, for the keep-out of a standoff the
# walls are still cut back from.
CIRCLE_SEGMENTS = 96
VOLUME_RELATIVE_TOLERANCE = cells.VOLUME_RELATIVE_TOLERANCE


# The half's plan geometry.


def half_point(point, right):
    return layout.mirror_for_right_half(point) if right else point


def half_polygon(polygon, right):
    """A left half's frame polygon on the given half, counter-clockwise."""
    return layout.counter_clockwise([half_point(point, right) for point in polygon])


def half_key_centers(right):
    return pcb_shape.half_key_centers(right)


def key_holes(key_center):
    """A key's footprint holes as (center, radius as modelled)."""
    return [
        (center, cells.switch_strip_hole_radius(SWITCH_HOLE_CELL_INDEX, local_center, diameter,
                                                PULL_IN_MM))
        for (center, diameter), (local_center, _) in zip(layout.footprint_holes(key_center),
                                                          layout.CHOC_FOOTPRINT_HOLES_MM)
    ]


def frame_holes(right):
    """Every hole through the frame's body as (center, radius): the
    keys' and the mounting drills, grown by pull_in like the mock's."""
    holes = [hole for center in half_key_centers(right).values() for hole in key_holes(center)]
    holes.extend((center, diameter / 2.0 + PULL_IN_MM)
                 for center, diameter in pcb_shape.half_drills(right))
    return holes


def boss_centers(right):
    return [half_point(center, right) for center in layout.frame_boss_centers(right)]


def beyond_flat_polygon(center, flat):
    """A square beyond a standoff flat's plane that covers the rest of
    the standoff, in the left half's frame."""
    reach = layout.STANDOFF_DIAMETER_MM
    toward = flat.toward
    along = (-toward[1], toward[0])

    def point(out, side):
        return (center[0] + toward[0] * out + along[0] * side,
                center[1] + toward[1] * out + along[1] * side)

    return [point(flat.plane_distance, -reach), point(flat.plane_distance, reach),
            point(reach, reach), point(reach, -reach)]


def flattened_standoff_face(center, flats, right):
    """A standoff's band in plan on the given half with its flats: the
    circle less what lies beyond each flat's plane."""
    circle = cells.circle_face(half_point(center, right), layout.STANDOFF_DIAMETER_MM / 2.0)
    if not flats:
        return circle
    beyond = [cells.plan_face(half_polygon(beyond_flat_polygon(center, flat), right))
              for flat in flats]
    return circle.cut(Part.makeCompound(beyond)).Faces[0]


def flattened_standoff_polygon(center, flats):
    """A standoff's band in plan with its flats, as a convex polygon
    around the circle, in the left half's frame."""
    radius = layout.STANDOFF_DIAMETER_MM / 2.0 / math.cos(math.pi / CIRCLE_SEGMENTS)
    polygon = tuple(
        (center[0] + radius * math.cos(2.0 * math.pi * index / CIRCLE_SEGMENTS),
         center[1] + radius * math.sin(2.0 * math.pi * index / CIRCLE_SEGMENTS))
        for index in range(CIRCLE_SEGMENTS)
    )
    for flat in flats:
        limit = flat.plane_distance + check_layout.dot(center, flat.toward)
        polygon = check_layout.clip_to_half_plane(polygon, flat.toward, limit)
    return polygon


def cut_back_keepouts(key, right):
    """The plan faces on the given half that a key's walls are still cut
    back by (layout.frame_walls_cut_back()): each body's convex polygon
    grown by layout.FRAME_TRAY_CLEARANCE_MM."""
    bodies = {body for cut_key, body in layout.frame_walls_cut_back(right) if cut_key == key}
    polygons = [polygon for label, polygon, _z_range in check_layout.frame_wall_tray_pieces(right)
                if label in bodies]
    polygons.extend(flattened_standoff_polygon(center, flats)
                    for label, center, _z_range, flats
                    in check_layout.frame_wall_standoff_bands(right) if label in bodies)
    return [cells.plan_face(half_polygon(layout.offset_polygon(polygon,
                                                               layout.FRAME_TRAY_CLEARANCE_MM),
                                         right))
            for polygon in polygons]


def wall_tray_obstacles(right):
    """(label, plan face) on the given half of what of the tray, and of
    the parts in it, stands within the walls' heights:
    check_layout.frame_wall_tray_pieces() and the standoffs' bands as
    flattened (check_layout.frame_wall_standoff_bands())."""
    obstacles = [(label, cells.plan_face(half_polygon(polygon, right)))
                 for label, polygon, _z_range in check_layout.frame_wall_tray_pieces(right)]
    obstacles.extend((label, flattened_standoff_face(center, flats, right))
                     for label, center, _z_range, flats
                     in check_layout.frame_wall_standoff_bands(right))
    return obstacles


def boxes_within(first, second, distance):
    """Whether two bounding boxes come within distance of each other in
    plan."""
    return (first.XMin - distance <= second.XMax and second.XMin - distance <= first.XMax
            and first.YMin - distance <= second.YMax and second.YMin - distance <= first.YMax)


def wall_plan(key_center, keepouts=()):
    """A socket's pocket walls in plan: the strips' ring at the frame's
    fit less the tab slots, the key's footprint holes and any keep-outs
    it is still cut back by (cut_back_keepouts())."""
    ring = cells.wall_ring(key_center, layout.FRAME_POCKET_FIT_MM)
    cutters = [cells.plan_face(cutter) for cutter in cells.wall_cutters(key_center)]
    cutters.extend(cells.circle_face(center, radius) for center, radius in key_holes(key_center))
    cutters.extend(keepouts)
    return ring.cut(Part.makeCompound(cutters)).Faces


def walls_too_near_the_tray(key, faces, obstacles):
    """Where a socket's walls come nearer an obstacle than
    layout.FRAME_TRAY_CLEARANCE_MM, as messages."""
    walls = Part.makeCompound(faces)
    minimum = layout.FRAME_TRAY_CLEARANCE_MM - WALL_TRAY_TOLERANCE_MM
    return [
        f"{key}'s walls and the {label}: {distance:.4f}"
        for label, face in obstacles
        if boxes_within(walls.BoundBox, face.BoundBox, minimum)
        for distance in (walls.distToShape(face)[0],)
        if distance < minimum
    ]


def all_wall_plans(right):
    """{key: its walls' plan faces}, whole but where
    layout.frame_walls_cut_back() still cuts them back from a body of the
    tray, after checking that nothing else of the tray comes nearer them
    than layout.FRAME_TRAY_CLEARANCE_MM."""
    obstacles = wall_tray_obstacles(right)
    cut_back = layout.frame_walls_cut_back(right)
    plans = {key: wall_plan(center, cut_back_keepouts(key, right))
             for key, center in half_key_centers(right).items()}
    problems = [problem for key, faces in plans.items()
                for problem in walls_too_near_the_tray(
                    key, faces, [(label, face) for label, face in obstacles
                                 if (key, label) not in cut_back])]
    if problems:
        raise SystemExit(
            f"error: the tray comes nearer the pocket walls than "
            f"{layout.FRAME_TRAY_CLEARANCE_MM}, the walls standing whole (work item 026): "
            + "; ".join(problems)
        )
    return plans


# The frame.


def outline_face(right):
    """The frame's outline, pulled in and rounded like the mock's, as a
    plan face on z = 0."""
    prism = pcb_shape.outline_body(PULL_IN_MM, layout.PCB_THICKNESS_MM, pcb_shape.half_outline(right))
    return pcb_shape.bottom_face(prism), prism


def tab_recess_polygons(right):
    return [cells.tab_slot(center, tab) for center in half_key_centers(right).values()
            for tab in cells.socket_tab_specs()]


def build_frame(right, insert_length=None):
    """(frame, its expected volume, {key: wall area in plan}), checked
    to be one valid solid of that volume."""
    insert_length = cells.longest_insert_length() if insert_length is None else insert_length
    if not 0.0 < insert_length <= cells.longest_insert_length() + 1e-9:
        raise SystemExit(
            f"error: an insert {insert_length} long does not fit the boss, which holds up to "
            f"{cells.longest_insert_length():.3f}"
        )
    thickness = layout.PCB_THICKNESS_MM
    face, body = outline_face(right)
    holes = frame_holes(right)
    recesses = tab_recess_polygons(right)
    cutters = [cells.hole_cutter(center, radius, thickness) for center, radius in holes]
    cutters.extend(plan_prism(recess, -CUT_EXTRA_MM, cells.TAB_RECESS_DEPTH_MM)
                   for recess in recesses)
    body = body.cut(Part.makeCompound(cutters))
    require_one_valid_solid(body, "cutting the frame's body")

    depth = cells.wall_depth()
    plans = all_wall_plans(right)
    walls = [cells.face_prism(wall_face, depth) for faces in plans.values()
             for wall_face in faces]
    centers = boss_centers(right)
    bosses = cells.build_bosses(cells.boss_end_depth(), centers)
    frame = body.fuse(walls + bosses).removeSplitter()
    require_one_valid_solid(frame, "fusing the walls and bosses to the frame's body")
    frame = frame.cut(Part.makeCompound(cells.build_bores(cells.boss_end_depth(), insert_length,
                                                          centers)))
    require_one_valid_solid(frame, "boring the bosses")

    recess_area = sum(face.common(cells.plan_face(recess)).Area for recess in recesses)
    figures = {key: sum(wall_face.Area for wall_face in faces) for key, faces in plans.items()}
    wall_area = sum(figures.values())
    boss_area = math.pi * (cells.BOSS_DIAMETER_MM / 2.0) ** 2
    bore_area = math.pi * (cells.INSERT_BORE_DIAMETER_MM / 2.0) ** 2
    expected = (
        (face.Area - sum(math.pi * radius**2 for _center, radius in holes)) * thickness
        - recess_area * cells.TAB_RECESS_DEPTH_MM
        + wall_area * depth
        + len(centers) * boss_area * cells.boss_end_depth()
        - len(centers) * bore_area * cells.insert_bore_depth(insert_length)
    )
    if abs(frame.Volume - expected) > VOLUME_RELATIVE_TOLERANCE * expected:
        raise SystemExit(
            f"error: the frame's volume is {frame.Volume:.4f} mm3, its plan gives {expected:.4f} mm3"
        )
    return frame.Solids[0], expected, figures


def turned_for_printing(frame):
    """The frame upside down, its top face on z = 0, at the same x and
    its y turned about the half's middle."""
    turned = frame.copy()
    turned.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 180.0)
    north = max(y for _, y in layout.OUTLINE_VERTICES_MM)
    turned.translate(App.Vector(0.0, north, layout.PCB_THICKNESS_MM))
    return turned


# The backing.


def backing_face(right):
    """The backing in plan: its outline less its cutouts and the screw
    holes."""
    outline = cells.plan_face(half_polygon(layout.frame_backing_outline(), right))
    cutters = [cells.circle_face(half_point(center, right), radius)
               for _label, center, radius
               in layout.frame_backing_circle_cutouts(layout.MOUNTING_DRILL_CENTERS_MM)]
    cutters.extend(cells.plan_face(half_polygon(polygon, right))
                   for _label, polygon in layout.frame_backing_polygon_cutouts(right))
    radius = cells.SCREW_CLEARANCE_HOLE_DIAMETER_MM / 2.0
    cutters.extend(cells.circle_face(center, radius) for center in boss_centers(right))
    return outline.cut(Part.makeCompound(cutters))


def backing_pads(right):
    return [pad for center in half_key_centers(right).values()
            for pad in cells.pad_polygons(center)]


def build_backing(right):
    """(backing with its bottom on z = 0, its expected volume), checked
    to be one valid solid of that volume."""
    thickness = cells.BACKING_THICKNESS_MM
    face = backing_face(right)
    if len(face.Faces) != 1:
        raise SystemExit(f"error: the backing's plan came to {len(face.Faces)} pieces, expected one")
    body = face.Faces[0].extrude(UP * thickness)
    height = cells.pad_height(PAD_CELL_INDEX)
    pads = backing_pads(right)
    prisms = [plan_prism(pad, thickness, thickness + height) for pad in pads]
    backing = body.fuse(prisms).removeSplitter()
    require_one_valid_solid(backing, "fusing the pads to the backing")
    expected = (face.Area * thickness
                + sum(layout.polygon_signed_area(pad) for pad in pads) * height)
    if abs(backing.Volume - expected) > VOLUME_RELATIVE_TOLERANCE * expected:
        raise SystemExit(
            f"error: the backing's volume is {backing.Volume:.4f} mm3, its plan gives "
            f"{expected:.4f} mm3"
        )
    return backing.Solids[0], expected


def stacked_backing(backing):
    """The backing under the frame, its top on the bosses' ends."""
    return cells.stacked_backing(backing)
