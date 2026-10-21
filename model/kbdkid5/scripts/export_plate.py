"""Export the 3D-printable switch plate (STL) from the layout.

plate_shape.py builds the plate (see its docstring): the kbdkid3 plate
model aligned onto layout.py's keys, trimmed, the corner by the slant
covered, head clearance holes at the mounting drills, kbdkid4's print
corrections and, with "covered", S123's cutout filled with a pit for
its diode. This script mirrors it for the right half, checks the
result against the layout and prints what it measured: the plate
inside the tray's cavity wall, its slanted edge's distance from the
outline's slant, every cutout on its key and every head hole on its
drill (both moved by the pattern shift), and the plate each head hole
leaves to the nearest switch cutout. Then it writes the plate
upside down, its top face on z = 0, so the covered variant's pit opens
upward and it prints as is without supports.

Runs headless under FreeCAD's console interpreter (see
freecad_common.py for the freecadcmd quirks that shape the
invocation):

    freecadcmd model/kbdkid5/scripts/export_plate.py --pass <plate.stl> [right] [covered] [key=value ...]

The word "right" mirrors the plate across the layout's right-half
mirror line (see layout.py), the pit and the pattern shift included.
The shift goes along +x (east) on the left half, the direction
kbdkid4's drift went (toward its nano there, cause unknown), and so
along -x on the right half.

The cavity is checked as the outline moved out by the tray's gap with
round corners: the tray's cavity rounds its convex corners with at
most the gap around the outline's corners and its concave ones
outward (kbdkid4's tray), so it only has more room than that.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App
import Part

import layout
from freecad_common import (
    ROUND_JOIN,
    check_closed_mesh,
    export_stl,
    offset_outline,
    run_and_exit,
    script_arguments,
)
from plate_shape import (
    ALIGNMENT_RESIDUAL_LIMIT_MM,
    CORNER_OVERHANG_MM,
    COVERED_KEY_NAME,
    DEFAULT_PATTERN_SHIFT_MM,
    DEFAULT_SIDE_SHAVE_MM,
    PLATE_EDGE_TRIM_MM,
    PLATE_HOLE_DIAMETER_MM,
    PLATE_MODEL_FILE,
    PLATE_OBJECT_NAME,
    SCREW_HEAD_CLEARANCE_MM,
    SCREW_HEAD_DIAMETER_MM,
    SUPPORTED_HOLE_THRESHOLD,
    build_plate,
    inside_any,
    outline_polygon_wire,
    plate_silhouette_bottom_face,
)

# A cutout or hole further than this from where the layout puts it is
# not its key's or drill's at all.
FEATURE_MATCH_RADIUS_MM = 1.0
# The slant edge's two ends must lie this close to the same offset
# from the slant. An edge counts as along the slant when its direction
# is off by less than PARALLEL_TOLERANCE radians.
SLANT_OFFSET_TOLERANCE_MM = 1e-6
PARALLEL_TOLERANCE = 1e-6

# DESIGN.md's figures for the plate, transcribed independently of the
# constants it is built from, as check_layout.py's DESIGN_* are, and
# each compared within half its last digit: the slanted edge's offset
# out of the outline's slant after the shave, and the least the plate
# keeps from the cavity wall (along that edge). kbdkid4's plate
# printed snug at 0.05 from the wall.
DESIGN_SLANT_EDGE_OFFSET_MM = 0.25
DESIGN_LEAST_CAVITY_CLEARANCE_MM = 0.15
DESIGN_FIGURE_DECIMALS = 2
FACE_TOLERANCE_MM = 0.001
# Probes this far into the plate from a face (kbdkid4's).
PROBE_DEPTH_MM = 0.3

USAGE = f"""\
usage: freecadcmd model/kbdkid5/scripts/export_plate.py --pass <plate.stl> [right] [covered]
           [hole_diameter={PLATE_HOLE_DIAMETER_MM:.2f}]
           [pattern_shift={DEFAULT_PATTERN_SHIFT_MM}]
           [side_shave={DEFAULT_SIDE_SHAVE_MM}]

  right          export the right half: the plate mirrored across the layout's
                 right-half mirror line, x = {layout.RIGHT_HALF_MIRROR_X_MM:.3f}
  covered        fill the switch cutout of {COVERED_KEY_NAME} solid, with a pit in its
                 underside for the key's diode, for a plate without that key
  pattern_shift  move every cutout and hole this far along +x (east, the way
                 kbdkid4's holes drifted, cause unknown) while the outline
                 stays put, mm
  side_shave     take this much off the plate's west and east edges and its
                 slanted edge, mm
  hole_diameter  clearance holes over the screw heads, mm (the measured
                 {SCREW_HEAD_DIAMETER_MM} mm head plus {SCREW_HEAD_CLEARANCE_MM} mm)\
"""

NUMBER_OPTIONS = ("hole_diameter", "pattern_shift", "side_shave")


class Arguments:
    def __init__(self):
        self.stl_file = None
        self.hole_diameter = PLATE_HOLE_DIAMETER_MM
        self.pattern_shift = DEFAULT_PATTERN_SHIFT_MM
        self.side_shave = DEFAULT_SIDE_SHAVE_MM
        self.right = False
        self.covered = False


def parse_arguments(argument_list):
    arguments = Arguments()
    positionals = []
    for argument in argument_list:
        if argument == "right":
            arguments.right = True
        elif argument == "covered":
            arguments.covered = True
        elif "=" in argument:
            key, _, value = argument.partition("=")
            if key not in NUMBER_OPTIONS:
                raise SystemExit(f"error: unknown option '{key}'\n{USAGE}")
            try:
                setattr(arguments, key, float(value))
            except ValueError:
                raise SystemExit(f"error: '{key}' needs a number, got '{value}'")
        else:
            positionals.append(argument)
    if len(positionals) != 1:
        raise SystemExit(USAGE)
    arguments.stl_file = positionals[0]
    return arguments


def mirror_across_half_line(shape):
    return shape.mirror(
        App.Vector(layout.RIGHT_HALF_MIRROR_X_MM, 0.0, 0.0), App.Vector(1.0, 0.0, 0.0)
    )


def mirror_for_right_half(plate):
    """Mirror the plate across the layout's right-half mirror line. This
    has to run before turn_upside_down: Shape.mirror works on the
    geometry and drops a placement set by rotate or translate
    (observed on FreeCAD 1.0 in kbdkid4), which would silently undo
    the turn."""
    volume_before = plate.Volume
    mirrored = mirror_across_half_line(plate)
    if not mirrored.isValid() or abs(mirrored.Volume - volume_before) > 1e-6 * volume_before:
        raise SystemExit("error: mirroring the plate changed its volume")
    return mirrored


def half_point(point, right):
    """A left-half layout point on the exported half."""
    return layout.mirror_for_right_half(point) if right else point


def half_vector(vector, right):
    return (-vector[0], vector[1]) if right else vector


def placed_point(point, shift, right):
    """Where a pattern feature at a left-half layout point ends up: moved
    with the pattern, then onto the exported half."""
    return half_point((point[0] + shift, point[1]), right)


def subtract(first, second):
    return (first[0] - second[0], first[1] - second[1])


def dot(first, second):
    return first[0] * second[0] + first[1] * second[1]


def distance(first, second):
    return math.hypot(*subtract(first, second))


def design_figure_tolerance():
    return 0.5 * 10.0**-DESIGN_FIGURE_DECIMALS + SLANT_OFFSET_TOLERANCE_MM


def cavity_wire(z, right):
    """The tray's cavity wall as checked here: the outline moved out by
    the gap with round corners, at height z, on the exported half."""
    cavity = offset_outline(outline_polygon_wire(z), layout.TRAY_GAP_MM, ROUND_JOIN)
    return mirror_across_half_line(cavity) if right else cavity


def measure_cavity(plate, right):
    """(clearance, where, side clearances): the plate's silhouette must
    lie inside the cavity, at least DESIGN_LEAST_CAVITY_CLEARANCE_MM from
    its wall. The clearance is its least distance to the cavity wall, the
    side clearances the bounding boxes' per side."""
    silhouette = plate_silhouette_bottom_face(plate).OuterWire
    cavity = cavity_wire(silhouette.BoundBox.ZMin, right)
    outside_area = Part.Face(silhouette).cut(Part.Face(cavity)).Area
    if outside_area > 1e-9:
        raise SystemExit(
            f"error: {outside_area:.4f} mm2 of the plate lies outside the tray's cavity wall"
        )
    clearance, pairs, _info = silhouette.distToShape(cavity)
    if clearance < DESIGN_LEAST_CAVITY_CLEARANCE_MM - design_figure_tolerance():
        where = pairs[0][0]
        raise SystemExit(
            f"error: the plate comes {clearance:.3f} mm from the tray's cavity wall at "
            f"({where.x:.3f}, {where.y:.3f}), DESIGN.md asks for at least "
            f"{DESIGN_LEAST_CAVITY_CLEARANCE_MM}"
        )
    plate_box, cavity_box = silhouette.BoundBox, cavity.BoundBox
    sides = {
        "west": plate_box.XMin - cavity_box.XMin,
        "east": cavity_box.XMax - plate_box.XMax,
        "south": plate_box.YMin - cavity_box.YMin,
        "north": cavity_box.YMax - plate_box.YMax,
    }
    return clearance, pairs[0][0], sides


def line_edge_ends(edge):
    start = edge.valueAt(edge.FirstParameter)
    end = edge.valueAt(edge.LastParameter)
    return (start.x, start.y), (end.x, end.y)


def is_parallel(edge, direction):
    start, end = line_edge_ends(edge)
    length = distance(start, end)
    along = subtract(end, start)
    cross = along[0] * direction[1] - along[1] * direction[0]
    return length > 0.0 and abs(cross) < PARALLEL_TOLERANCE * length


def measure_slant_edge(plate, right):
    """(offset, ends) of the plate silhouette's one edge along the
    slant: how far out of the outline's slant it lies, in the slant's
    outward normal, which both its ends must agree on, against
    DESIGN_SLANT_EDGE_OFFSET_MM."""
    south = half_point(layout.SLANT_SOUTH_END_MM, right)
    direction = half_vector(layout.slant_direction(), right)
    outward = half_vector(layout.slant_outward_normal(), right)
    silhouette = plate_silhouette_bottom_face(plate).OuterWire
    edges = [
        edge
        for edge in silhouette.Edges
        if isinstance(edge.Curve, Part.Line) and is_parallel(edge, direction)
    ]
    if len(edges) != 1:
        raise SystemExit(f"error: the plate has {len(edges)} edges along the slant, expected one")
    ends = line_edge_ends(edges[0])
    offsets = [dot(subtract(end, south), outward) for end in ends]
    if abs(offsets[0] - offsets[1]) > SLANT_OFFSET_TOLERANCE_MM:
        raise SystemExit(
            f"error: the plate's slanted edge runs from {offsets[0]:.4f} to "
            f"{offsets[1]:.4f} out of the slant, not along it"
        )
    if abs(offsets[0] - DESIGN_SLANT_EDGE_OFFSET_MM) > design_figure_tolerance():
        raise SystemExit(
            f"error: the plate's slanted edge lies {offsets[0]:.4f} out of the slant, "
            f"DESIGN.md says {DESIGN_SLANT_EDGE_OFFSET_MM}"
        )
    return offsets[0], ends


def top_face(plate):
    top = plate.BoundBox.ZMax
    faces = [
        face
        for face in plate.Faces
        if isinstance(face.Surface, Part.Plane)
        and abs(face.BoundBox.ZMin - top) < FACE_TOLERANCE_MM
        and abs(face.BoundBox.ZMax - top) < FACE_TOLERANCE_MM
    ]
    if len(faces) != 1:
        raise SystemExit(f"error: expected one plate top face, found {len(faces)}")
    return faces[0]


def top_openings(plate):
    """(cutout centers, head holes as (center, radius)): the top face's
    inner wires, a hole being a ring of arcs around one center, a
    switch cutout anything else, centered on its bounding box."""
    face = top_face(plate)
    cutouts = []
    holes = []
    for wire in face.Wires:
        if wire.isSame(face.OuterWire):
            continue
        curves = [edge.Curve for edge in wire.Edges]
        if all(isinstance(curve, Part.Circle) for curve in curves):
            center = curves[0].Center
            holes.append(((center.x, center.y), curves[0].Radius))
        else:
            box = wire.BoundBox
            cutouts.append((box.Center.x, box.Center.y))
    return cutouts, holes


def hole_cutout_clearances(plate):
    """(hole center, least distance to a switch cutout's edge, that
    cutout's center) of every head hole on the plate's top face, measured
    between the face's inner wires."""
    face = top_face(plate)
    holes, cutouts = [], []
    for wire in face.Wires:
        if wire.isSame(face.OuterWire):
            continue
        if all(isinstance(edge.Curve, Part.Circle) for edge in wire.Edges):
            holes.append(wire)
        else:
            cutouts.append(wire)
    clearances = []
    for hole in holes:
        center = hole.Edges[0].Curve.Center
        distance, nearest = min(((hole.distToShape(cutout)[0], cutout) for cutout in cutouts),
                                key=lambda pair: pair[0])
        box = nearest.BoundBox
        clearances.append(((center.x, center.y), distance, (box.Center.x, box.Center.y)))
    return clearances


def match_features(found, expected, what):
    """The worst distance between each expected (label, point) and the
    one found point within FEATURE_MATCH_RADIUS_MM of it. Every found
    point must belong to one expected."""
    worst = 0.0
    used = set()
    for label, point in expected:
        near = [
            index
            for index, other in enumerate(found)
            if distance(other, point) < FEATURE_MATCH_RADIUS_MM
        ]
        if len(near) != 1:
            raise SystemExit(f"error: found {len(near)} {what}s at {label}, expected one")
        used.add(near[0])
        worst = max(worst, distance(found[near[0]], point))
    if len(used) != len(found):
        raise SystemExit(
            f"error: the plate has {len(found) - len(used)} {what}s the layout does not place"
        )
    if worst > ALIGNMENT_RESIDUAL_LIMIT_MM:
        raise SystemExit(f"error: a {what} lies {worst:.4f} mm off its layout position")
    return worst


def expected_cutouts(arguments):
    return [
        (name, placed_point(center, arguments.pattern_shift, arguments.right))
        for name, center in layout.KEY_CENTERS_MM.items()
        if not (arguments.covered and name == COVERED_KEY_NAME)
    ]


def expected_holes(arguments):
    return [
        (f"the drill at {center}", placed_point(center, arguments.pattern_shift, arguments.right))
        for center in layout.MOUNTING_DRILL_CENTERS_MM
    ]


def measure_openings(plate, arguments):
    """(cutout count, worst cutout residual, hole count, worst hole
    residual) of the plate's top face against the layout."""
    cutouts, holes = top_openings(plate)
    hole_radius = arguments.hole_diameter / 2.0
    for center, radius in holes:
        if abs(radius - hole_radius) > FACE_TOLERANCE_MM:
            raise SystemExit(f"error: a hole at {center} is {2.0 * radius:.3f} mm across")
    hole_centers = [center for center, _radius in holes]
    cutout_worst = match_features(cutouts, expected_cutouts(arguments), "switch cutout")
    hole_worst = match_features(hole_centers, expected_holes(arguments), "head hole")
    return len(cutouts), cutout_worst, len(holes), hole_worst


def turn_upside_down(plate, recess_centers):
    """Rotate the plate 180 degrees about the x axis through its center
    and drop it onto z = 0, so it prints with its top face on the bed
    and the recesses at `recess_centers` (the diode pit) opening
    upward. Returns the turned plate."""
    center = plate.BoundBox.Center
    plate.rotate(center, App.Vector(1, 0, 0), 180)
    plate.translate(App.Vector(0, 0, -plate.BoundBox.ZMin))
    box = plate.BoundBox
    for recess in recess_centers:
        turned = App.Vector(recess[0], 2.0 * center.y - recess[1], 0.0)
        if not inside_any(plate, turned.add(App.Vector(0, 0, PROBE_DEPTH_MM))):
            raise SystemExit("error: after turning, the skin above a recess is not at the bottom")
        if inside_any(plate, turned.add(App.Vector(0, 0, box.ZMax - PROBE_DEPTH_MM))):
            raise SystemExit("error: after turning, a recess does not open at the top")
    return plate


def format_point(point):
    return f"({point[0]:.3f}, {point[1]:.3f})"


def print_build(build):
    corner = build.corner
    print(f"layout:     {len(layout.KEY_CENTERS_MM)} keys, "
          f"{len(layout.MOUNTING_DRILL_CENTERS_MM)} mounting drills, plate "
          f"{layout.PLATE_THICKNESS_MM} mm thick on the PCB (z {layout.PCB_TOP_Z_MM} to "
          f"{layout.PLATE_TOP_Z_MM})")
    print(f"model:      '{PLATE_OBJECT_NAME}' from "
          f"{os.path.relpath(PLATE_MODEL_FILE, os.getcwd())}")
    print(f"aligned:    moved ({build.alignment.x:+.3f}, {build.alignment.y:+.3f}) mm onto the "
          f"layout's keys (worst residual {build.alignment_residual:.4f} mm), outer edges "
          f"trimmed {PLATE_EDGE_TRIM_MM} mm")
    print(f"corner:     covered from x {corner.west_x:.3f} (column 5) and y "
          f"{corner.south_y:.3f} (the thumb cell) to the slant plus {CORNER_OVERHANG_MM} mm, "
          f"east to x {corner.east_x:.3f} (the thumb cell), north to y {corner.north_y:.3f} "
          f"(column 5), {corner.slab.Volume / layout.PLATE_THICKNESS_MM:.1f} mm2")
    if build.diode_pit is not None:
        pit = build.diode_pit
        key = layout.KEY_CENTERS_MM[COVERED_KEY_NAME]
        print(f"cover:      {COVERED_KEY_NAME}'s cutout at {format_point(key)} filled solid, "
              f"{pit.length:.2f} x {pit.width:.2f} mm pit {pit.depth:.2f} mm deep in the "
              f"underside for its diode at {format_point(pit.center)}, rotated "
              f"{layout.DIODE_ROTATION_DEGREES:.0f} degrees, "
              f"{layout.PLATE_THICKNESS_MM - pit.depth:.2f} mm of plate left above it")
    for center, support in build.hole_supports:
        note = ""
        if support < SUPPORTED_HOLE_THRESHOLD:
            note = " (mostly open plate area, clearance cut only)"
        print(f"hole:       {format_point(center)} {build.hole_diameter:.2f} mm, "
              f"{support * 100.0:5.1f} % supported{note}")
    print(f"shift:      hole pattern moved {build.pattern_shift:+.2f} mm along x relative to "
          f"the outline, which stays put")
    print(f"sides:      {build.side_shave:.2f} mm shaved off the west and east edges and "
          "the slanted edge")
    print(f"fused:      {build.solid_count} solids into one, volume {build.solid.Volume:.3f} mm3")


def print_measurements(plate, arguments):
    clearance, where, sides = measure_cavity(plate, arguments.right)
    side_text = ", ".join(f"{side} {value:.3f}" for side, value in sides.items())
    print(f"cavity:     inside the tray's cavity wall (outline plus {layout.TRAY_GAP_MM}), at "
          f"least {clearance:.3f} mm from it (DESIGN.md at least "
          f"{DESIGN_LEAST_CAVITY_CLEARANCE_MM}), at ({where.x:.3f}, {where.y:.3f}), by "
          f"side {side_text} mm")
    offset, ends = measure_slant_edge(plate, arguments.right)
    print(f"slant:      the plate's slanted edge {offset:.4f} mm out of the outline's slant "
          f"(DESIGN.md {DESIGN_SLANT_EDGE_OFFSET_MM}), from {format_point(ends[0])} to "
          f"{format_point(ends[1])}, {layout.TRAY_GAP_MM - offset:.3f} mm short of the cavity "
          f"wall")
    cutout_count, cutout_worst, hole_count, hole_worst = measure_openings(plate, arguments)
    shift = half_vector((arguments.pattern_shift, 0.0), arguments.right)[0]
    print(f"cutouts:    {cutout_count} switch cutouts, each on its key moved {shift:+.2f} "
          f"along x, worst residual {cutout_worst:.4f} mm")
    print(f"holes:      {hole_count} head holes, each on its drill moved {shift:+.2f} along "
          f"x, worst residual {hole_worst:.4f} mm")
    for center, distance, cutout in hole_cutout_clearances(plate):
        print(f"hole:       {format_point(center)} {distance:.3f} mm of plate to the nearest "
              f"switch cutout, centered at {format_point(cutout)}")


def recess_centers(build, arguments):
    if build.diode_pit is None:
        return []
    return [placed_point(build.diode_pit.center, arguments.pattern_shift, arguments.right)]


def main():
    arguments = parse_arguments(script_arguments(sys.argv))
    build = build_plate(
        arguments.covered, arguments.pattern_shift, arguments.side_shave, arguments.hole_diameter
    )
    print_build(build)
    plate = build.solid
    half = "left"
    if arguments.right:
        plate = mirror_for_right_half(plate)
        half = (f"right, mirrored across x = {layout.RIGHT_HALF_MIRROR_X_MM:.3f} (the lines "
                "above are the left half's build, the lines below the right half's)")
    print(f"half:       {half}")
    print_measurements(plate, arguments)
    plate = turn_upside_down(plate, recess_centers(build, arguments))
    mesh = export_stl(plate, arguments.stl_file)
    check_closed_mesh(arguments.stl_file)

    box = plate.BoundBox
    print(f"print:      written upside down, top face on z = 0, {box.XLength:.2f} x "
          f"{box.YLength:.2f} x {box.ZLength:.2f} mm (x {box.XMin:.3f} to {box.XMax:.3f})")
    print(f"wrote:      {arguments.stl_file} ({mesh.CountFacets} facets), one closed "
          "manifold shell")


run_and_exit(main)
