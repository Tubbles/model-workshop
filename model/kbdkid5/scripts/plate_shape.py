"""The switch plate, built from the kbdkid3 plate model onto the layout.

kbdkid4's plate pipeline (its scripts/export_plate.py), with
layout.py as its input instead of kbdkid4's board files. The kbdkid3
plate model (resources/kbdkid3-plate-left.FCStd) is a parametric
switch cell replicated by a point array, one cell per key, with a
mirrored right plate in the same document that is not used. Its cells
are the layout's 19.05 key cells, but it does not share the layout's
origin, so the model is aligned by matching its switch cutout centers
to the layout's keys, refusing anything but a pure translation, and
put on the PCB. Its outer edges are trimmed so it fits the tray.

The switch-free corner between column 5, the thumb key and the slant
gets a slab, flush with the cells beside it, out to the slant moved
out by CORNER_OVERHANG_MM. The screws clamp the PCB onto the tray's
standoffs and the plate sits over their heads, held down by the
switches, so head clearance holes go through it at the mounting
drills. Every drill is cut, even one in mostly open plate area:
whatever sliver reaches into the screw's path must go. Unlike
kbdkid4's plate there are no lead recesses and no reset hole, since
nothing on the PCB is through-hole any more and the reset button sits
in the tray's north wall (DESIGN.md).

With covered, the plate is the variant for a half without the key at
COVERED_KEY_NAME (the bottom row's third key, hard to reach): its
cutout is filled in solid, flush with the plate's top and bottom
faces, and the key's diode gets a rectangular pit in the underside.

Then kbdkid4's two print corrections. The whole pattern of cutouts,
holes and the pit moves pattern_shift along +x while the outline stays
where it is: kbdkid4's printed plates sat right in the tray but their
holes drifted off the board's features toward the nice!nano side, and
a plate printed with a 0.5 shift came out about as far off the other
way, so 0.25 is kbdkid4's current try (the drift's cause is still
open there). Then side_shave comes off the plate's west and east
extremes and its slanted edge, since kbdkid4's printed plate was a
snug fit across the tray's width: its east edge, like the slanted
edge here, started 0.05 short of the cavity wall.

Last, the plate's touching solids (the kbdkid3 cells, the corner slab,
any cover and the strips the pattern shift fills) are fused into one,
so slicers get a single closed mesh instead of one with coincident
internal walls at every solid's boundary.

build_plate() returns the left half's plate in the layout's frame,
resting on the PCB (z PCB_TOP_Z_MM to PLATE_TOP_Z_MM), for
export_plate.py and any other script to build on. Like
freecad_common.py this module has no entry point, so it is safe to
import from the export scripts and probes.
"""

import math
import os
from dataclasses import dataclass

import FreeCAD as App
import Part

import layout
from freecad_common import offset_outline

# The left plate object in the model's document (the right plate is
# its mirror and is not used).
PLATE_MODEL_FILE = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        os.pardir,
        os.pardir,
        os.pardir,
        "resources",
        "kbdkid3-plate-left.FCStd",
    )
)
PLATE_OBJECT_NAME = "PointArray"

# The plate's holes swallow the screw heads (DESIGN.md, "Mounting": M2
# screws as on kbdkid4), with kbdkid4's figures.
SCREW_HEAD_DIAMETER_MM = 3.77  # measured on kbdkid4's screws
SCREW_HEAD_CLEARANCE_MM = 0.4  # extra so a printed hole clears the head
PLATE_HOLE_DIAMETER_MM = SCREW_HEAD_DIAMETER_MM + SCREW_HEAD_CLEARANCE_MM

# Every cutout has to agree on the alignment within this (kbdkid4's).
ALIGNMENT_RESIDUAL_LIMIT_MM = 0.05

# The model overhangs the tray, so its outer edges are trimmed by this
# much, as on kbdkid4.
PLATE_EDGE_TRIM_MM = 0.4

# The corner slab reaches this far past the outline's slant
# (DESIGN.md), like kbdkid4's covered corner past its board's edge: 0.05
# short of the cavity wall at the tray's 0.4 gap, until the side shave
# moves the slanted edge in.
CORNER_OVERHANG_MM = 0.35

# The covered variant (kbdkid4's). Its diode is a SOD-123 (measured
# 1.14 tall on kbdkid4's board) on kbdkid4's "Hand Soldering"
# footprint: the pads' copper spans DIODE_PAD_SPAN_MM along the body
# axis, the body is DIODE_BODY_WIDTH_MM wide across it. The pit clears
# both by DIODE_PIT_MARGIN_MM per side (solder fillets, print
# swelling) and is DIODE_PIT_DEPTH_MM deep, leaving three 0.2 print
# layers of the 2.2 plate over it: a single layer printed translucent
# over a pit this wide. The pit lies where layout.py puts the key's
# diode.
COVERED_KEY_NAME = "S123"
DIODE_PAD_SPAN_MM = 5.25
DIODE_BODY_WIDTH_MM = 1.56
DIODE_PIT_MARGIN_MM = 0.5
DIODE_PIT_DEPTH_MM = 1.6

# kbdkid4's print corrections: the pattern shift relative to the
# outline, along +x (east), the way kbdkid4's holes drifted (toward
# its nano there, cause unknown), mirrored to -x on the right half
# along with everything else, and what comes off the west and east
# extremes, so the plate comes out 2 x DEFAULT_SIDE_SHAVE_MM
# narrower, and off the slanted edge, along its normal. The north and
# south edges stay as they are.
DEFAULT_PATTERN_SHIFT_MM = 0.25
DEFAULT_SIDE_SHAVE_MM = 0.1

# Below this much surrounding plate material a head hole is a
# clearance cut in mostly open plate area rather than a supported hole.
# Only affects reporting: every drill is cut either way.
SUPPORTED_HOLE_THRESHOLD = 0.5

# The plate's solids only touch, so fusing them into one must keep the
# volume: equal within 1e-13 (relative) on FreeCAD 1.0 for kbdkid4's
# plate. This allows for numerical noise and still catches the loss of
# anything larger than about 0.01 mm3.
FUSE_VOLUME_TOLERANCE = 1e-6  # relative

# Implementation tuning, rarely worth touching.
CUT_EXTRA_MM = 1.0  # cutters overshoot the plate's faces for a clean cut
EDGE_TOLERANCE_MM = 0.01  # silhouette edges and bounding boxes, as kbdkid4's
FACE_TOLERANCE_MM = 0.001  # a face lying on a plane

UP = App.Vector(0.0, 0.0, 1.0)


@dataclass
class Corner:
    """The corner slab and where it was bounded."""

    slab: Part.Shape
    west_x: float  # column 5's east edge
    south_y: float  # the thumb cell's top edge
    east_x: float  # the thumb cell's east edge
    north_y: float  # column 5's top edge


@dataclass
class DiodePit:
    center: tuple  # before the pattern shift
    length: float  # along the diode's body
    width: float
    depth: float


@dataclass
class Plate:
    """build_plate()'s result: the fused solid and how it came about."""

    solid: Part.Shape
    alignment: App.Vector  # moved the model by this onto the layout
    alignment_residual: float
    corner: Corner
    diode_pit: object  # a DiodePit when covered, else None
    hole_supports: list  # (drill center, supported fraction)
    hole_diameter: float
    pattern_shift: float
    side_shave: float
    solid_count: int  # fused into the one solid


def outline_polygon_wire(z):
    """The layout's outline, sharp-cornered, at height z."""
    points = [App.Vector(x, y, z) for x, y in layout.OUTLINE_VERTICES_MM]
    return Part.makePolygon(points + [points[0]])


def inside_any(shape, point):
    return any(solid.isInside(point, 1e-6, True) for solid in shape.Solids)


def load_plate_model():
    """The model's left plate, a compound of one solid per cell. The
    document is closed again, so the plate can be built more than
    once in a run."""
    document = App.openDocument(PLATE_MODEL_FILE)
    try:
        plate_object = document.getObject(PLATE_OBJECT_NAME)
        if plate_object is None:
            raise SystemExit(f"error: no '{PLATE_OBJECT_NAME}' object in {PLATE_MODEL_FILE}")
        shape = Part.getShape(plate_object).copy()
    finally:
        App.closeDocument(document.Name)
    if shape.isNull() or not shape.Solids:
        raise SystemExit(f"error: '{PLATE_OBJECT_NAME}' has no solid geometry")
    if abs(shape.BoundBox.ZLength - layout.PLATE_THICKNESS_MM) > FACE_TOLERANCE_MM:
        raise SystemExit(
            f"error: the plate model is {shape.BoundBox.ZLength:.3f} thick, the layout's "
            f"plate {layout.PLATE_THICKNESS_MM}"
        )
    return shape


def cutout_centers(plate):
    """Center of each cell's switch cutout: the inner boundary of the
    cell's top face (kbdkid4's)."""
    centers = []
    for solid in plate.Solids:
        for face in solid.Faces:
            surface = face.Surface
            if not isinstance(surface, Part.Plane):
                continue
            normal = face.normalAt(*surface.parameter(face.CenterOfMass))
            if normal.z < 0.999:
                continue
            inner_wires = [wire for wire in face.Wires if not wire.isSame(face.OuterWire)]
            if not inner_wires:
                continue
            box = inner_wires[0].BoundBox
            for wire in inner_wires[1:]:
                box.add(wire.BoundBox)
            centers.append(App.Vector(box.Center.x, box.Center.y, 0.0))
            break
    if not centers:
        raise SystemExit("error: no switch cutouts found in the plate model")
    return centers


def nearest_key_index(keys, point):
    return min(range(len(keys)), key=lambda index: keys[index].sub(point).Length)


def alignment_offset(plate):
    """(offset, worst residual): the translation in plan that puts the
    model onto the layout's keys, found by matching every switch
    cutout to its nearest key. As on kbdkid4 the match must be a pure
    translation, all cutouts agreeing on the offset within
    ALIGNMENT_RESIDUAL_LIMIT_MM. kbdkid5's layout has the model's 25
    keys, so every key must also get its own cutout."""
    keys = [App.Vector(x, y, 0.0) for x, y in layout.KEY_CENTERS_MM.values()]
    centers = cutout_centers(plate)
    if len(centers) != len(keys):
        raise SystemExit(
            f"error: the plate model has {len(centers)} switch cutouts, the layout "
            f"{len(keys)} keys"
        )
    matched = [nearest_key_index(keys, center) for center in centers]
    if len(set(matched)) != len(keys):
        raise SystemExit("error: two of the plate model's cutouts match the same key")
    deltas = [keys[index].sub(center) for index, center in zip(matched, centers)]
    mean = App.Vector(
        sum(delta.x for delta in deltas) / len(deltas),
        sum(delta.y for delta in deltas) / len(deltas),
        0.0,
    )
    worst = max(delta.sub(mean).Length for delta in deltas)
    if worst > ALIGNMENT_RESIDUAL_LIMIT_MM:
        raise SystemExit(
            f"error: the plate model's cutouts do not match the layout's keys by a pure "
            f"translation (worst residual {worst:.3f} mm)"
        )
    return mean, worst


def place_on_layout(plate):
    """Move the model onto the layout's keys and onto the PCB. Returns
    (plate, offset in plan, worst residual)."""
    offset, residual = alignment_offset(plate)
    lift = layout.PLATE_TOP_Z_MM - plate.BoundBox.ZMax
    plate.translate(App.Vector(offset.x, offset.y, lift))
    return plate, offset, residual


def plate_silhouette_bottom_face(plate):
    """The bottom face of the fused plate, whose outer wire is the
    plate's silhouette."""
    silhouette = plate.Solids[0]
    if len(plate.Solids) > 1:
        silhouette = plate.Solids[0].multiFuse(plate.Solids[1:]).removeSplitter()
    bottom = silhouette.BoundBox.ZMin
    bottom_faces = [
        face
        for face in silhouette.Faces
        if isinstance(face.Surface, Part.Plane)
        and abs(face.BoundBox.ZMin - bottom) < FACE_TOLERANCE_MM
        and abs(face.BoundBox.ZMax - bottom) < FACE_TOLERANCE_MM
    ]
    if len(bottom_faces) != 1:
        raise SystemExit(f"error: expected one plate bottom face, found {len(bottom_faces)}")
    return bottom_faces[0]


def silhouette_prism(plate, overshoot):
    """The plate's silhouette extruded over its thickness plus
    `overshoot` beyond both faces."""
    box = plate.BoundBox
    outline = plate_silhouette_bottom_face(plate).OuterWire
    prism = Part.Face(outline).extrude(UP * (box.ZLength + 2.0 * overshoot))
    prism.translate(UP * (box.ZMin - overshoot - outline.BoundBox.ZMin))
    return prism


def common_solid_by_solid(plate, tool):
    """The plate's solids, each cut down to `tool`, as a compound. A
    common() of the whole compound silently drops a cell (observed on
    FreeCAD 1.0 in kbdkid4), the per-solid ones do not."""
    solids = []
    for solid in plate.Solids:
        solids.extend(solid.common(tool).Solids)
    return Part.makeCompound(solids)


def trim_outer_edges(plate, trim):
    """Shrink the plate's outer silhouette by `trim` on all outer edges,
    leaving the cutouts untouched. kbdkid4 cut the whole compound at
    once. Here it goes solid by solid, and no cell may go missing."""
    outline = offset_outline(plate_silhouette_bottom_face(plate).OuterWire, -trim)
    keep_prism = Part.Face(outline).extrude(UP * (plate.BoundBox.ZLength + 2.0 * CUT_EXTRA_MM))
    keep_prism.translate(UP * -CUT_EXTRA_MM)
    trimmed = common_solid_by_solid(plate, keep_prism)
    if len(trimmed.Solids) != len(plate.Solids):
        raise SystemExit(
            f"error: trimming left {len(trimmed.Solids)} of the plate's "
            f"{len(plate.Solids)} cells"
        )
    old_box = plate.BoundBox
    new_box = trimmed.BoundBox
    for old_length, new_length in (
        (old_box.XLength, new_box.XLength),
        (old_box.YLength, new_box.YLength),
    ):
        if abs(old_length - new_length - 2.0 * trim) > EDGE_TOLERANCE_MM:
            raise SystemExit(
                f"error: edge trim changed a plate side from {old_length:.2f} to "
                f"{new_length:.2f} mm, expected minus {2.0 * trim:.2f} mm"
            )
    return trimmed


def vertical_silhouette_edges(plate):
    """The silhouette's edges along y, as (x, low y, high y)."""
    edges = []
    for edge in plate_silhouette_bottom_face(plate).OuterWire.Edges:
        start = edge.valueAt(edge.FirstParameter)
        end = edge.valueAt(edge.LastParameter)
        if abs(start.x - end.x) > EDGE_TOLERANCE_MM:
            continue
        edges.append((start.x, min(start.y, end.y), max(start.y, end.y)))
    return edges


def corner_bounds(plate):
    """(west x, south y, east x, north y) of the switch-free corner: the
    plate's rightmost vertical edge is the thumb cell's east edge, its
    top is the thumb cell's top edge, and the rightmost vertical edge
    above that is column 5's east edge, its top column 5's top edge."""
    edges = vertical_silhouette_edges(plate)
    east_x, _thumb_low_y, south_y = max(edges)
    if abs(east_x - plate.BoundBox.XMax) > EDGE_TOLERANCE_MM:
        raise SystemExit("error: the plate's rightmost vertical edge is not its east extreme")
    above_thumb = [
        (x, high_y)
        for x, low_y, high_y in edges
        if low_y > south_y - EDGE_TOLERANCE_MM and x < east_x - EDGE_TOLERANCE_MM
    ]
    if not above_thumb:
        raise SystemExit("error: no vertical silhouette edge above the thumb cell")
    west_x, north_y = max(above_thumb)
    return west_x, south_y, east_x, north_y


def cover_slant_corner(plate):
    """Cover the switch-free corner between column 5, the thumb key and
    the slant with a slab from column 5's east edge and the thumb
    cell's top edge out to the outline moved out by
    CORNER_OVERHANG_MM, which bounds it along the slant. It goes no
    further north than column 5's top edge, so it stays flush with the
    cells beside it (kbdkid4's rule), and no further east than the
    thumb cell's east edge, so the plate's east edge stays straight
    there (kbdkid4's corner had a tab below it out to the same reach,
    beside its nice!nano, which kbdkid5 does not have). The slab abuts
    the cells without overlapping them, like the cells abut each
    other. Returns (plate, Corner)."""
    west_x, south_y, east_x, north_y = corner_bounds(plate)
    box = plate.BoundBox
    reach = offset_outline(outline_polygon_wire(box.ZMin), CORNER_OVERHANG_MM)
    prism = Part.Face(reach).extrude(UP * box.ZLength)
    region = Part.makeBox(
        east_x - west_x,
        north_y - south_y,
        box.ZLength,
        App.Vector(west_x, south_y, box.ZMin),
    )
    slab = prism.common(region)
    if len(slab.Solids) != 1 or slab.Volume <= 0:
        raise SystemExit("error: the corner slab is not a single solid")
    slab_box = slab.BoundBox
    for expected, actual, side in (
        (west_x, slab_box.XMin, "x min"),
        (south_y, slab_box.YMin, "y min"),
        (east_x, slab_box.XMax, "x max"),
        (north_y, slab_box.YMax, "y max"),
    ):
        if abs(expected - actual) > EDGE_TOLERANCE_MM:
            raise SystemExit(
                f"error: the corner slab's {side} is {actual:.3f}, expected {expected:.3f}"
            )
    covered = Part.makeCompound(list(plate.Solids) + [slab.Solids[0]])
    return covered, Corner(slab.Solids[0], west_x, south_y, east_x, north_y)


def solid_bottom_outline(solid):
    """The outer wire of a solid's bottom face."""
    bottom = solid.BoundBox.ZMin
    bottom_faces = [
        face
        for face in solid.Faces
        if isinstance(face.Surface, Part.Plane)
        and abs(face.BoundBox.ZMin - bottom) < FACE_TOLERANCE_MM
        and abs(face.BoundBox.ZMax - bottom) < FACE_TOLERANCE_MM
    ]
    if len(bottom_faces) != 1:
        raise SystemExit(
            f"error: expected one bottom face on the covered cell, found {len(bottom_faces)}"
        )
    return bottom_faces[0].OuterWire


def cutout_bounding_volume(cell):
    """An upper bound for the volume of a cell's cutout: the bounding
    box around every inner wire of the cell's horizontal faces (the
    cutout's openings and the steps inside it), times the cell's
    thickness."""
    inner_wires = [
        wire
        for face in cell.Faces
        if isinstance(face.Surface, Part.Plane) and abs(face.Surface.Axis.z) > 0.999
        for wire in face.Wires
        if not wire.isSame(face.OuterWire)
    ]
    if not inner_wires:
        raise SystemExit("error: the covered cell has no cutout openings")
    box = inner_wires[0].BoundBox
    for wire in inner_wires[1:]:
        box.add(wire.BoundBox)
    return box.XLength * box.YLength * cell.BoundBox.ZLength


def cell_index_at(plate, position):
    """The index of the one solid whose bounding box contains the
    point in plan."""
    indices = [
        index
        for index, solid in enumerate(plate.Solids)
        if solid.BoundBox.XMin < position[0] < solid.BoundBox.XMax
        and solid.BoundBox.YMin < position[1] < solid.BoundBox.YMax
    ]
    if len(indices) != 1:
        raise SystemExit(
            f"error: expected one plate cell at ({position[0]:.2f}, {position[1]:.2f}) to "
            f"cover, found {len(indices)}"
        )
    return indices[0]


def cover_switch_cell(plate, position):
    """Fill the switch cutout at `position` solid: the cell holding it
    is replaced by a full-thickness prism of its outer boundary, so its
    outline and its contact with the neighbouring cells stay as they
    are and the other solids are left alone. Returns the plate."""
    index = cell_index_at(plate, position)
    cell = plate.Solids[index]
    box = plate.BoundBox
    middle = App.Vector(position[0], position[1], box.Center.z)
    if cell.isInside(middle, 1e-6, True):
        raise SystemExit(
            f"error: the cell at ({position[0]:.2f}, {position[1]:.2f}) has no switch "
            "cutout to cover"
        )
    cover = Part.Face(solid_bottom_outline(cell)).extrude(UP * box.ZLength)
    if cell.cut(cover).Volume > 0.001:
        raise SystemExit("error: the cover does not enclose the cell it replaces")
    cover_box = cover.BoundBox
    if (
        abs(cover_box.ZMin - box.ZMin) > FACE_TOLERANCE_MM
        or abs(cover_box.ZMax - box.ZMax) > FACE_TOLERANCE_MM
    ):
        raise SystemExit(
            f"error: the cover spans z {cover_box.ZMin:.3f} to {cover_box.ZMax:.3f}, not "
            f"the plate's {box.ZMin:.3f} to {box.ZMax:.3f}"
        )
    filled_volume = cover.Volume - cell.Volume
    cutout_bound = cutout_bounding_volume(cell)
    if not 0 < filled_volume < cutout_bound:
        raise SystemExit(
            f"error: covering the cell filled {filled_volume:.2f} mm3, expected more than 0 "
            f"and less than the {cutout_bound:.2f} mm3 box around the cutout"
        )
    solids = list(plate.Solids)
    solids[index] = cover
    covered = Part.makeCompound(solids)
    if not inside_any(covered, middle):
        raise SystemExit(
            f"error: the cutout at ({position[0]:.2f}, {position[1]:.2f}) is still open "
            "after covering"
        )
    return covered


def cut_diode_pit(plate, center, rotation_degrees):
    """Cut a rectangular pit into the plate's underside for the diode
    under the cover, its length along the diode's body, rotated with
    it, DIODE_PIT_DEPTH_MM deep. Returns (plate, DiodePit)."""
    box = plate.BoundBox
    length = DIODE_PAD_SPAN_MM + 2.0 * DIODE_PIT_MARGIN_MM
    width = DIODE_BODY_WIDTH_MM + 2.0 * DIODE_PIT_MARGIN_MM
    depth = DIODE_PIT_DEPTH_MM
    pit = Part.makeBox(
        length,
        width,
        depth + CUT_EXTRA_MM,
        App.Vector(-length / 2.0, -width / 2.0, box.ZMin - CUT_EXTRA_MM),
    )
    pit.rotate(App.Vector(0, 0, 0), UP, rotation_degrees)
    pit.translate(App.Vector(center[0], center[1], 0.0))
    volume_before = plate.Volume
    cut = plate.cut(pit)
    removed_volume = volume_before - cut.Volume
    expected_volume = length * width * depth
    if abs(removed_volume - expected_volume) > 0.01 * expected_volume:
        raise SystemExit(
            f"error: the diode pit removed {removed_volume:.2f} mm3, expected "
            f"{expected_volume:.2f} mm3, so it is not fully inside plate material"
        )
    skin_middle_z = box.ZMax - (box.ZLength - depth) / 2.0
    if inside_any(cut, App.Vector(center[0], center[1], box.ZMin + 0.3)):
        raise SystemExit("error: the diode pit did not open the underside")
    if not inside_any(cut, App.Vector(center[0], center[1], skin_middle_z)):
        raise SystemExit("error: the diode pit broke through the plate's top")
    return cut, DiodePit(center, length, width, depth)


def drill_holes(plate, hole_centers, hole_diameter):
    """Cut a through hole at each center and return the drilled plate
    along with each hole's supported fraction, as (center, fraction).

    Every center is cut regardless of support: a position in mostly
    open plate area still needs whatever sliver protrudes into the
    screw's path removed."""
    box = plate.BoundBox
    radius = hole_diameter / 2.0
    full_volume = math.pi * radius**2 * box.ZLength
    drills = []
    supports = []
    for center in hole_centers:
        drill = Part.makeCylinder(
            radius,
            box.ZLength + 2.0 * CUT_EXTRA_MM,
            App.Vector(center[0], center[1], box.ZMin - CUT_EXTRA_MM),
            UP,
        )
        supports.append((center, plate.common(drill).Volume / full_volume))
        drills.append(drill)
    volume_before = plate.Volume
    removed_volume = plate.common(Part.makeCompound(drills)).Volume
    drilled = plate.cut(Part.makeCompound(drills))
    if abs(volume_before - drilled.Volume - removed_volume) > 0.001 * volume_before:
        raise SystemExit("error: drilling did not remove the expected volume")
    # A drill can sever a narrow web (splitting a cell in two is fine),
    # but a piece must never lose contact with the rest.
    fused = drilled.Solids[0].multiFuse(drilled.Solids[1:])
    if len(fused.Solids) != 1:
        raise SystemExit(f"error: drilling left {len(fused.Solids)} disconnected plate pieces")
    return drilled, supports


def shift_pattern(plate, shift):
    """Move every cutout, hole and the pit by `shift` along +x while the
    outline stays where it is: translate the plate, clip it back to its
    original silhouette solid by solid, and fill the strips that open
    along the edges it moved away from. Returns the plate."""
    if shift == 0:
        return plate
    box = plate.BoundBox
    prism = silhouette_prism(plate, CUT_EXTRA_MM)
    moved_prism = prism.copy()
    moved_prism.translate(App.Vector(shift, 0, 0))
    moved = plate.copy()
    moved.translate(App.Vector(shift, 0, 0))
    clipped = common_solid_by_solid(moved, prism)
    # The prism overshoots the plate's faces, so trim the fill to the
    # plate's own thickness.
    fill = prism.cut(moved_prism).common(
        Part.makeBox(
            box.XLength + 2.0,
            box.YLength + 2.0,
            box.ZLength,
            App.Vector(box.XMin - 1.0, box.YMin - 1.0, box.ZMin),
        )
    )
    result = Part.makeCompound(list(clipped.Solids) + list(fill.Solids))
    new_box = result.BoundBox
    for before, after, side in (
        (box.XMin, new_box.XMin, "x min"),
        (box.XMax, new_box.XMax, "x max"),
        (box.YMin, new_box.YMin, "y min"),
        (box.YMax, new_box.YMax, "y max"),
    ):
        if abs(before - after) > EDGE_TOLERANCE_MM:
            raise SystemExit(
                f"error: shifting the pattern moved the outline's {side} from {before:.3f} "
                f"to {after:.3f}"
            )
    if abs(result.Volume - plate.Volume) > 0.005 * plate.Volume:
        raise SystemExit(
            f"error: shifting the pattern changed the plate volume from {plate.Volume:.1f} "
            f"to {result.Volume:.1f} mm3: a hole must sit within the shift of an edge"
        )
    return result


def slant_keep_prism(plate, shave):
    """Everything on the half's side of the corner slab's slanted edge
    moved in by `shave` along its normal, over the plate's thickness
    plus CUT_EXTRA_MM beyond both faces."""
    box = plate.BoundBox
    reach = layout.slant_length() + 2.0 * (box.XLength + box.YLength)
    polygon = layout.slant_rectangle(
        layout.slant_length() / 2.0, reach, (-reach, CORNER_OVERHANG_MM - shave)
    )
    points = [App.Vector(x, y, box.ZMin - CUT_EXTRA_MM) for x, y in polygon]
    face = Part.Face(Part.makePolygon(points + [points[0]]))
    return face.extrude(UP * (box.ZLength + 2.0 * CUT_EXTRA_MM))


def shave_sides(plate, shave):
    """Take `shave` off the plate's west and east edges (its extremes
    along x) and off its slanted edge, along that edge's normal,
    leaving the north and south edges and the hole pattern where they
    are. Returns the plate."""
    if shave == 0:
        return plate
    box = plate.BoundBox
    keep = Part.makeBox(
        box.XLength - 2.0 * shave,
        box.YLength + 2.0,
        box.ZLength + 2.0,
        App.Vector(box.XMin + shave, box.YMin - 1.0, box.ZMin - 1.0),
    ).common(slant_keep_prism(plate, shave))
    # What should go: the silhouette prism outside the kept region,
    # which equals the plate there as long as no cutout reaches a
    # shaved edge.
    expected_removed = silhouette_prism(plate, 0.0).cut(keep).Volume
    shaved = common_solid_by_solid(plate, keep)
    new_box = shaved.BoundBox
    for expected, actual, side in (
        (box.XMin + shave, new_box.XMin, "x min"),
        (box.XMax - shave, new_box.XMax, "x max"),
        (box.YMin, new_box.YMin, "y min"),
        (box.YMax, new_box.YMax, "y max"),
    ):
        if abs(expected - actual) > EDGE_TOLERANCE_MM:
            raise SystemExit(
                f"error: shaving the sides put the outline's {side} at {actual:.3f}, "
                f"expected {expected:.3f}"
            )
    removed = plate.Volume - shaved.Volume
    if abs(removed - expected_removed) > 0.01 * expected_removed:
        raise SystemExit(
            f"error: shaving the sides removed {removed:.2f} mm3, expected "
            f"{expected_removed:.2f} mm3: a cutout must reach a shaved edge"
        )
    return shaved


def fuse_into_one_solid(plate):
    """Fuse the plate's touching solids into one, so the STL is a single
    closed shell without internal walls. A boolean on the whole
    compound has silently dropped a cell before (see
    common_solid_by_solid), hence the checks: the result must be one
    valid solid with the compound's volume, since the solids only
    touch and nothing may be lost. Returns the solid."""
    volume_before = plate.Volume
    fused = plate.Solids[0].multiFuse(plate.Solids[1:]).removeSplitter()
    if not fused.isValid() or len(fused.Solids) != 1:
        raise SystemExit(
            f"error: fusing the plate gave {len(fused.Solids)} solids (valid: "
            f"{fused.isValid()}), expected one valid solid"
        )
    if abs(fused.Volume - volume_before) > FUSE_VOLUME_TOLERANCE * volume_before:
        raise SystemExit(
            f"error: fusing the plate changed its volume from {volume_before:.4f} to "
            f"{fused.Volume:.4f} mm3: a solid was lost or two overlapped"
        )
    return fused.Solids[0]


def build_plate(
    covered=False,
    pattern_shift=DEFAULT_PATTERN_SHIFT_MM,
    side_shave=DEFAULT_SIDE_SHAVE_MM,
    hole_diameter=PLATE_HOLE_DIAMETER_MM,
):
    """The left half's plate as one solid in the layout's frame, resting
    on the PCB, and how it came about (a Plate). pattern_shift=0 gives
    the plate with every cutout and hole on its layout position."""
    plate, alignment, residual = place_on_layout(load_plate_model())
    plate = trim_outer_edges(plate, PLATE_EDGE_TRIM_MM)
    plate, corner = cover_slant_corner(plate)
    diode_pit = None
    if covered:
        key_center = layout.KEY_CENTERS_MM[COVERED_KEY_NAME]
        plate = cover_switch_cell(plate, key_center)
        plate, diode_pit = cut_diode_pit(
            plate, layout.diode_center(key_center), layout.DIODE_ROTATION_DEGREES
        )
    plate, supports = drill_holes(plate, layout.MOUNTING_DRILL_CENTERS_MM, hole_diameter)
    plate = shift_pattern(plate, pattern_shift)
    plate = shave_sides(plate, side_shave)
    solid_count = len(plate.Solids)
    return Plate(
        fuse_into_one_solid(plate),
        alignment,
        residual,
        corner,
        diode_pit,
        supports,
        hole_diameter,
        pattern_shift,
        side_shave,
        solid_count,
    )
