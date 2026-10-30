"""The PCB mock's shape, built from the layout, and what the fused mock
adds to it.

kbdkid5 has no PCB design yet. Until it does, a printed stand-in for
the bare board test-fits the tray and the plate: the outline from
layout.py extruded to the PCB's thickness, with every key's Choc
hotswap footprint holes and the mounting drills, and nothing else (no
sockets). FDM prints come out slightly larger than modelled (the
extruded bead spreads, and the first layer squashes wider still), so
the mock is pulled in from all sides: the outline moves inward by
pull_in and every hole grows outward by pull_in, so the printed part
measures like the real board instead of binding in the tray or
refusing the switches. The thickness stays as modelled, since a
print's height follows its layer count and does not swell the same
way.

The outline and the holes move in opposite directions, so they are
built separately: FreeCAD's makeOffset2D on the whole face would
shrink the holes along with the outline. The outline's sharp polygon
moves in with sharp joins and is then rounded with the layout's corner
radius less pull_in at its convex corners and plus pull_in at its
concave ones, which is the rounded outline moved in (the arcs stay
concentric). Each hole is made pull_in larger in radius.

The right half has the outline and the mounting drills mirrored
across the layout's right-half mirror line and each key's footprint
holes the left half's at the mirrored key center, since a switch
cannot be mirrored (see layout.py): half_outline(), half_key_centers(),
half_drills() and all_holes() give either half.

The fused mock (export_mock.py) and its slit test strip
(export_slit_test.py) replace each key's two pin holes with slits that
grip the switch's pin blades: rectangles at the size given, which
pull_in does not grow (it only sets the default sizes, in layout.py).
The helpers at the end of this module fuse the fused mock's PCB layer
with the plate and measure the openings of a part's faces, the latter
for the strip too.

build_mock() returns the mock with its bottom face on z = 0. Like
freecad_common.py this module has no entry point, so it is safe to
import from the export scripts and probes.
"""

import math

import FreeCAD as App
import Part

import layout
from freecad_common import offset_outline
from plate_shape import ALIGNMENT_RESIDUAL_LIMIT_MM
from tray_shape import MINIMUM_FILLET_RADIUS_MM, fillet_prism_corners

# How far the printed part is expected to swell per side, in mm: the
# outline moves inward and every hole grows outward by this much. The
# tray's printed fits allow for the same swelling.
DEFAULT_PULL_IN_MM = layout.PRINT_SWELLING_PER_SIDE_MM

# Implementation tuning, rarely worth touching.
CUT_EXTRA_MM = 1.0  # hole cutters overshoot both faces for a clean cut
VOLUME_RELATIVE_TOLERANCE = 1e-6  # against the analytic volume
FACE_TOLERANCE_MM = 1e-6  # a face lying on a plane
# An opening further than this from where the layout puts it is not
# that key's or pin's at all.
FEATURE_MATCH_RADIUS_MM = 1.0
# A slit's measured sides must equal the modelled ones to within this.
SLIT_SIZE_TOLERANCE_MM = 1e-6

UP = App.Vector(0.0, 0.0, 1.0)


def half_point(point, right):
    """A left-half layout point on the given half."""
    return layout.mirror_for_right_half(point) if right else point


def half_outline(right):
    """The outline on the given half, counter-clockwise."""
    if not right:
        return layout.OUTLINE_VERTICES_MM
    mirrored = [layout.mirror_for_right_half(point) for point in layout.OUTLINE_VERTICES_MM]
    return tuple(reversed(mirrored))


def half_key_centers(right):
    """{key name on the half: center} on the given half."""
    return {name: half_point(center, right)
            for name, center in layout.key_centers_on_half(right).items()}


def half_drills(right):
    """The mounting drills on the given half as (center, diameter)."""
    return [
        (half_point(center, right), layout.MOUNTING_DRILL_DIAMETER_MM)
        for center in layout.MOUNTING_DRILL_CENTERS_MM
    ]


def all_holes(right=False):
    """Every hole of the bare board on the given half as (center,
    diameter): each key's footprint holes, unmirrored at its key center,
    then the mounting drills."""
    holes = [
        hole
        for center in half_key_centers(right).values()
        for hole in layout.footprint_holes(center)
    ]
    holes.extend(half_drills(right))
    return holes


def corner_radii(pull_in):
    """(convex, concave) corner radii of the outline moved in by
    pull_in: concentric with the layout's rounds."""
    return (
        max(layout.OUTLINE_CORNER_RADIUS_MM - pull_in, 0.0),
        layout.OUTLINE_CORNER_RADIUS_MM + pull_in,
    )


def rounded_polygon_area(polygon, convex_radius, concave_radius):
    """The area of a counter-clockwise polygon with its corners rounded,
    as fillet_prism_corners() rounds them: a round of radius r at a
    corner turning by t takes r^2 (tan(t / 2) - t / 2) off a convex
    corner and adds as much at a concave one."""
    area = layout.polygon_signed_area(polygon)
    for turn in layout.corner_turn_angles(polygon):
        radius = convex_radius if turn > 0.0 else concave_radius
        if radius < MINIMUM_FILLET_RADIUS_MM:
            continue
        half_turn = abs(turn) / 2.0
        corner_area = radius**2 * (math.tan(half_turn) - half_turn)
        area += -corner_area if turn > 0.0 else corner_area
    return area


def analytic_mock_area(pull_in, outline, holes, slits):
    """The mock's area from the layout alone, without FreeCAD's offset
    or fillets: the outline moved in, rounded, less the grown holes and
    the slits."""
    moved = layout.offset_polygon(outline, -pull_in)
    outline_area = rounded_polygon_area(moved, *corner_radii(pull_in))
    holes_area = sum(math.pi * (diameter / 2.0 + pull_in) ** 2 for _center, diameter in holes)
    slits_area = sum(layout.polygon_signed_area(slit) for slit in slits)
    return outline_area - holes_area - slits_area


def polygon_wire(polygon, z=0.0):
    points = [App.Vector(x, y, z) for x, y in polygon]
    return Part.makePolygon(points + [points[0]])


def outline_body(pull_in, thickness, outline):
    """The outline moved in by pull_in, rounded, extruded upward."""
    polygon = polygon_wire(outline)
    moved = polygon if pull_in == 0 else offset_outline(polygon, -pull_in)
    prism = Part.Face(moved).extrude(UP * thickness)
    convex_radius, concave_radius = corner_radii(pull_in)
    return fillet_prism_corners(prism, moved, UP, convex_radius, concave_radius)


def hole_cutter(center, diameter, pull_in, thickness):
    circle = Part.Wire(
        Part.makeCircle(diameter / 2.0 + pull_in, App.Vector(center[0], center[1], 0.0))
    )
    cutter = Part.Face(circle).extrude(UP * (thickness + 2.0 * CUT_EXTRA_MM))
    cutter.translate(UP * -CUT_EXTRA_MM)
    return cutter


def slit_cutter(polygon, thickness):
    cutter = Part.Face(polygon_wire(polygon)).extrude(UP * (thickness + 2.0 * CUT_EXTRA_MM))
    cutter.translate(UP * -CUT_EXTRA_MM)
    return cutter


def build_mock(pull_in, thickness, outline=layout.OUTLINE_VERTICES_MM, holes=None, slits=()):
    """(mock, its analytic volume): the outline (counter-clockwise)
    with the holes (center, diameter) grown by pull_in and the slits
    (polygons) at their own size. The bare board's holes by default."""
    holes = all_holes() if holes is None else holes
    body = outline_body(pull_in, thickness, outline)
    cutters = [hole_cutter(center, diameter, pull_in, thickness) for center, diameter in holes]
    cutters.extend(slit_cutter(slit, thickness) for slit in slits)
    mock = body.cut(Part.makeCompound(cutters))
    return mock, validate_mock(mock, pull_in, thickness, outline, holes, slits)


def bottom_face(mock):
    """The mock's face on z = 0."""
    faces = [
        face
        for face in mock.Faces
        if isinstance(face.Surface, Part.Plane)
        and abs(face.Surface.Axis.z) > 0.999
        and abs(face.CenterOfMass.z) < 1e-6
    ]
    if len(faces) != 1:
        raise SystemExit(f"error: the mock has {len(faces)} faces on z = 0, expected one")
    return faces[0]


def rounded_corner_count(pull_in, outline):
    """How many of the mock outline's corners fillet_prism_corners()
    rounds: all but those whose radius it skips as moot."""
    convex_radius, concave_radius = corner_radii(pull_in)
    return sum(
        1
        for turn in layout.corner_turn_angles(outline)
        if (convex_radius if turn > 0.0 else concave_radius) >= MINIMUM_FILLET_RADIUS_MM
    )


def validate_mock(mock, pull_in, thickness, outline, holes, slits):
    """Check the mock against the layout and return its analytic
    volume."""
    if not mock.isValid() or len(mock.Solids) != 1:
        raise SystemExit("error: cutting the holes broke the mock solid")
    expected_volume = analytic_mock_area(pull_in, outline, holes, slits) * thickness
    deviation = abs(mock.Volume - expected_volume)
    if deviation > VOLUME_RELATIVE_TOLERANCE * expected_volume:
        raise SystemExit(
            f"error: mock volume {mock.Volume:.4f} mm3 deviates from the analytic "
            f"{expected_volume:.4f} mm3 by {deviation:.4f}; geometry is off"
        )
    face = bottom_face(mock)
    opening_count = len(face.Wires) - 1
    if opening_count != len(holes) + len(slits):
        raise SystemExit(
            f"error: the mock has {opening_count} holes, the layout {len(holes) + len(slits)}"
        )
    # The volume only just tells a missing round at the default pull_in
    # (a right-angle corner rounded with 0.276 loses 0.026 mm3, against a
    # tolerance of 0.013 mm3) and misses smaller rounds, so count them.
    arc_count = sum(1 for edge in face.OuterWire.Edges if isinstance(edge.Curve, Part.Circle))
    if arc_count != rounded_corner_count(pull_in, outline):
        raise SystemExit(
            f"error: the mock's outline has {arc_count} rounded corners, the layout "
            f"{rounded_corner_count(pull_in, outline)}"
        )
    return expected_volume


# The fused mock: a PCB layer and the plate printed as one part.


def key_holes_and_slits(key_centers, slit_length, slit_width):
    """(holes, slits) of the keys at key_centers: each key's footprint
    holes but its pin holes, and a slit on each pin instead."""
    holes = [
        hole
        for center in key_centers
        for hole in layout.footprint_holes_without_pin_holes(center)
    ]
    slits = [
        slit for center in key_centers for slit in layout.pin_slits(center, slit_length, slit_width)
    ]
    return holes, slits


def fuse_layers(pcb_layer, plate_layer):
    """The PCB layer and the plate on it fused into one valid solid,
    which must have both parts' volume, since they only share a face."""
    volume_before = pcb_layer.Volume + plate_layer.Volume
    fused = pcb_layer.fuse(plate_layer).removeSplitter()
    if not fused.isValid() or len(fused.Solids) != 1:
        raise SystemExit(
            f"error: fusing the PCB layer and the plate gave {len(fused.Solids)} solids "
            f"(valid: {fused.isValid()}), expected one valid solid"
        )
    if abs(fused.Volume - volume_before) > VOLUME_RELATIVE_TOLERANCE * volume_before:
        raise SystemExit(
            f"error: fusing changed the volume from {volume_before:.4f} to {fused.Volume:.4f} "
            "mm3, so the PCB layer and the plate overlap"
        )
    return fused.Solids[0]


def horizontal_face(shape, z):
    """The shape's one planar face lying on height z."""
    faces = [
        face
        for face in shape.Faces
        if isinstance(face.Surface, Part.Plane)
        and abs(face.BoundBox.ZMin - z) < FACE_TOLERANCE_MM
        and abs(face.BoundBox.ZMax - z) < FACE_TOLERANCE_MM
    ]
    if len(faces) != 1:
        raise SystemExit(f"error: expected one face on z = {z}, found {len(faces)}")
    return faces[0]


def face_openings(face):
    """(circles as (center, radius), others as (center, x length, y
    length)) of a face's inner wires: a circle being a ring of arcs
    around one center, anything else centered on its bounding box."""
    circles = []
    others = []
    for wire in face.Wires:
        if wire.isSame(face.OuterWire):
            continue
        curves = [edge.Curve for edge in wire.Edges]
        if all(isinstance(curve, Part.Circle) for curve in curves):
            circles.append(((curves[0].Center.x, curves[0].Center.y), curves[0].Radius))
        else:
            box = wire.BoundBox
            others.append(((box.Center.x, box.Center.y), box.XLength, box.YLength))
    return circles, others


def nearest_within(points, target, radius):
    """The one point within radius of target, or an error naming how
    many there are."""
    near = [point for point in points if math.dist(point, target) < radius]
    if len(near) != 1:
        raise SystemExit(f"error: found {len(near)} openings near {target}, expected one")
    return near[0]


def center_hole_radius(pull_in):
    """The switch's center post hole (the footprint's first) as grown."""
    _center, diameter = layout.CHOC_FOOTPRINT_HOLES_MM[0]
    return diameter / 2.0 + pull_in


def check_cutouts_on_center_holes(part, key_centers, pull_in):
    """(count, worst offset): every key's plate cutout, an opening of
    the fused part's top face, against the key's center hole, one of
    its bottom face."""
    top = horizontal_face(part, part.BoundBox.ZMax)
    bottom = horizontal_face(part, part.BoundBox.ZMin)
    _counterbores, cutouts = face_openings(top)
    circles, _slits = face_openings(bottom)
    radius = center_hole_radius(pull_in)
    center_holes = [center for center, other in circles if abs(other - radius) < 1e-6]
    key_centers = list(key_centers)
    if len(cutouts) != len(key_centers) or len(center_holes) != len(key_centers):
        raise SystemExit(
            f"error: {len(cutouts)} plate cutouts and {len(center_holes)} center holes for "
            f"{len(key_centers)} keys"
        )
    cutout_centers = [center for center, _x_length, _y_length in cutouts]
    worst = 0.0
    for key_center in key_centers:
        cutout = nearest_within(cutout_centers, key_center, FEATURE_MATCH_RADIUS_MM)
        hole = nearest_within(center_holes, key_center, FEATURE_MATCH_RADIUS_MM)
        worst = max(worst, math.dist(cutout, hole))
    if worst > ALIGNMENT_RESIDUAL_LIMIT_MM:
        raise SystemExit(f"error: a plate cutout lies {worst:.4f} mm off its key's center hole")
    return len(cutouts), worst


def polygon_center_and_size(polygon):
    """(bounding box center, x length, y length) of a polygon."""
    xs = [x for x, _ in polygon]
    ys = [y for _, y in polygon]
    center = ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0)
    return center, max(xs) - min(xs), max(ys) - min(ys)


def measured_slits(part, slits):
    """Each modelled slit's (offset, x length, y length) as measured on
    the part's bottom face, in the order of slits, each checked to lie
    on its modelled place at its modelled size."""
    _circles, found = face_openings(horizontal_face(part, part.BoundBox.ZMin))
    if len(found) != len(slits):
        raise SystemExit(f"error: the PCB layer has {len(found)} slits, the layout {len(slits)}")
    by_center = {center: (x_length, y_length) for center, x_length, y_length in found}
    measured = []
    for slit in slits:
        expected_center, x_length, y_length = polygon_center_and_size(slit)
        center = nearest_within(by_center, expected_center, FEATURE_MATCH_RADIUS_MM)
        found_x_length, found_y_length = by_center[center]
        if (
            abs(found_x_length - x_length) > SLIT_SIZE_TOLERANCE_MM
            or abs(found_y_length - y_length) > SLIT_SIZE_TOLERANCE_MM
        ):
            raise SystemExit(
                f"error: the slit at {center} is {found_x_length:.4f} x {found_y_length:.4f}, "
                f"modelled {x_length:.4f} x {y_length:.4f}"
            )
        offset = math.dist(center, expected_center)
        if offset > ALIGNMENT_RESIDUAL_LIMIT_MM:
            raise SystemExit(f"error: the slit at {center} lies {offset:.4f} mm off its pin")
        measured.append((offset, found_x_length, found_y_length))
    return measured
