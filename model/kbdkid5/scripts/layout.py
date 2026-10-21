"""kbdkid5's geometry as data, the ground truth until a PCB exists.

DESIGN.md specifies kbdkid5 in prose and tables. This module holds the
same numbers for the scripts: the keys and their footprints, the
outline with its slant, the mounting drills, the heights, the tray's
dimensions, the parts mounted in the tray and the joint between the
halves. It is plain Python with no FreeCAD import, so check_layout.py
checks it anywhere and the export scripts read it under freecadcmd.
Each value cites its source: DESIGN.md, kbdkid4's files
(~/dev/kbdkid4, https://github.com/Tubbles/kbdkid4) or
doc/components.md. When this module and DESIGN.md disagree, one of
them has a bug. This module holds the values the geometry is built
from. DESIGN.md's figures that follow from them (sizes, clearances,
spacings) are check_layout.py's DESIGN_* constants, transcribed
independently so the check catches a slip on either side.

Points are (x, y) tuples and ranges (low, high) tuples, in mm, in the
left half's frame (DESIGN.md, "Frame and units"): kbdkid4's board
coordinates, x east, y north, z above the tray floor's top face.
Polygons are tuples of points, counter-clockwise.

The right half is the left one mirrored across the vertical line
x = RIGHT_HALF_MIRROR_X_MM, the outline's center line: through
mirror_for_right_half() for points, across that line for FreeCAD
shapes. Every export uses this one line, a constant of the layout
rather than each part's own center: kbdkid4 mirrored its replica and
plate across their own bounding box centers, which only line up while
every part has the same extent in x, and kbdkid5's plate reaches past
the slant while the tray reaches past the outline everywhere. The
outline's center line rather than x = 0 keeps a right part on the same
spot as its left one (the same bounding box, on the print bed and in a
viewer), as kbdkid4's mirrored parts were.

A switch cannot be mirrored, so neither can what its footprint places
(its pins and holes, its socket): on the right half a key's footprint
sits at the mirrored key center with the left half's rotation, as
kbdkid4's right half (its board turned over) has it seen from above.
DESIGN.md makes that a constraint on the PCB design. Call the
footprint functions with mirror_for_right_half(key_center) for that.

The right half's tray is built like the left one, in the left half's
frame, and mirrored at the end, so what it is cut for comes in that
frame: socket_polygons_on_half() and the socket rule functions with
right=True give the right half's sockets mirrored back across the
mirror line, which is the footprint's mirror image at the left half's
key center, not the left half's socket.
"""

import math
from dataclasses import dataclass, replace

# Keys (DESIGN.md, "Keys", from kbdkid4's boards/board_1.1/board.lp,
# where every S1xx device has (rotation 90.0) (flip false)). Names are
# kbdkid4's: S1<column><row>, row 0 at the top.
KEY_PITCH_MM = 19.05
COLUMN_X_MM = (9.049, 28.099, 47.149, 66.199, 85.249, 104.299)
COLUMN_ROWS_Y_MM = (
    (66.357, 47.307, 28.257, 9.207),  # column 0
    (66.357, 47.307, 28.257, 9.207),  # column 1, as column 0
    (71.120, 52.070, 33.020, 13.970),  # column 2
    (73.501, 54.451, 35.401, 16.351),  # column 3
    (71.120, 52.070, 33.020, 13.970),  # column 4, as column 2
    (68.739, 49.689, 30.639, 11.589),  # column 5
)
THUMB_KEY_NAME = "S163"
THUMB_KEY_CENTER_MM = (123.349, 9.207)
TOP_ROW_KEY_OF_COLUMN_5 = "S150"


def column_key_name(column, row):
    return f"S1{column}{row}"


KEY_CENTERS_MM = {
    column_key_name(column, row): (x, y)
    for column, (x, rows) in enumerate(zip(COLUMN_X_MM, COLUMN_ROWS_Y_MM))
    for row, y in enumerate(rows)
}
KEY_CENTERS_MM[THUMB_KEY_NAME] = THUMB_KEY_CENTER_MM


def key_cell_top_right_corner(key_center):
    """The top right corner of a key's 19.05 square cell."""
    half = KEY_PITCH_MM / 2.0
    return (key_center[0] + half, key_center[1] + half)


# Every key's footprint sits as on kbdkid4's left half (DESIGN.md,
# "Keys"): rotated 90 degrees, on the top side.
FOOTPRINT_ROTATION_DEGREES = 90.0


def footprint_point(key_center, local_point):
    """A footprint-local point in board coordinates, the way kbdkid4's
    board_step.Placement.map_point maps it (LibrePCB's Transform::map:
    mirror when flipped, rotate, translate), for an unflipped footprint
    at FOOTPRINT_ROTATION_DEGREES."""
    angle = math.radians(FOOTPRINT_ROTATION_DEGREES)
    x, y = local_point
    return (
        key_center[0] + x * math.cos(angle) - y * math.sin(angle),
        key_center[1] + x * math.sin(angle) + y * math.cos(angle),
    )


def footprint_polygon(key_center, local_polygon):
    return tuple(footprint_point(key_center, point) for point in local_polygon)


# The Choc hotswap footprint's holes, (footprint-local center,
# diameter): kbdkid4's KHA-PG1350 package,
# library/pkg/23d245ff-14f8-48ad-af68-56ebb3a76786/package.lp,
# footprint "hot-swap hand solder", which most of kbdkid4's switches
# use. Its "hot-swap" and "hot-swap high-density" footprints have the
# same six holes.
CHOC_FOOTPRINT_HOLES_MM = (
    ((0.0, 0.0), 3.4),  # the switch's center post
    ((0.0, 5.5), 1.9),  # its side pegs
    ((0.0, -5.5), 1.9),
    ((-3.75, 5.0), 3.0),  # its pins, into the socket's contacts
    ((-5.95, 0.0), 3.0),
    ((4.2, -5.22), 1.2),  # where the solder footprint has its NC pad
)


# Of those, the holes the switch's two pins pass through.
CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM = ((-3.75, 5.0), (-5.95, 0.0))


def footprint_holes(key_center):
    """A key's footprint holes as (center, diameter) in board
    coordinates."""
    return tuple(
        (footprint_point(key_center, local_center), diameter)
        for local_center, diameter in CHOC_FOOTPRINT_HOLES_MM
    )


def footprint_holes_without_pin_holes(key_center):
    """A key's footprint holes but the two its pins pass through."""
    return tuple(
        (footprint_point(key_center, local_center), diameter)
        for local_center, diameter in CHOC_FOOTPRINT_HOLES_MM
        if local_center not in CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM
    )


# The switch's two contact pins, flat blades: measured on kbdkid4's
# switch model (library/pkg/23d245ff-14f8-48ad-af68-56ebb3a76786/
# b20b765a-8655-4947-a9b7-18864444346f.step, "PG1350", which the
# package places with 3d_rotation 0 0 180), model figures, not a
# caliper's. Each blade is CHOC_PIN_BLADE_THICKNESS_MM thick along
# footprint x and CHOC_PIN_BLADE_WIDTH_MM wide along footprint y, the
# same from the housing's underside (on the PCB) down to
# CHOC_PIN_FULL_WIDTH_DEPTH_MM below it, then narrowing to the
# thickness at its tip, CHOC_PIN_LENGTH_MM below the housing. The
# footprint's pin holes sit 0.05 off the blades' centers along
# footprint x, its solder pads on them.
CHOC_PIN_CENTERS_MM = ((-3.8, 5.0), (-5.9, 0.0))
CHOC_PIN_BLADE_THICKNESS_MM = 0.2
CHOC_PIN_BLADE_WIDTH_MM = 0.8
CHOC_PIN_FULL_WIDTH_DEPTH_MM = 2.65
CHOC_PIN_LENGTH_MM = 3.0

# The blades' thicknesses along footprint x, in CHOC_PIN_CENTERS_MM's
# order: the user's caliper figures on a real switch (2026-10-17), the
# pin near a side peg about 0.4, the middle one about 0.2. The model
# said 0.2 for both (CHOC_PIN_BLADE_THICKNESS_MM). The second slit
# test strip (export_slit_test.py) sizes its slits from these.
CHOC_PIN_CALIPERED_BLADE_THICKNESSES_MM = (0.4, 0.2)


def footprint_rectangle(key_center, local_center, size_along_x, size_along_y):
    """A rectangle around a footprint-local center, its sides along the
    footprint's axes, in board coordinates, counter-clockwise."""
    half_x = size_along_x / 2.0
    half_y = size_along_y / 2.0
    center_x, center_y = local_center
    return footprint_polygon(
        key_center,
        (
            (center_x - half_x, center_y - half_y),
            (center_x + half_x, center_y - half_y),
            (center_x + half_x, center_y + half_y),
            (center_x - half_x, center_y + half_y),
        ),
    )


def pin_slits(key_center, slit_length, slit_width):
    """A key's two slits for the switch's pins, centered on the blades:
    slit_length along each blade's width, slit_width across it."""
    return pin_slits_of_widths(key_center, slit_length, (slit_width,) * len(CHOC_PIN_CENTERS_MM))


def pin_slits_of_widths(key_center, slit_length, slit_widths):
    """A key's two pin slits like pin_slits(), each with its own width
    across its blade, slit_widths in CHOC_PIN_CENTERS_MM's order."""
    return tuple(
        footprint_rectangle(key_center, pin_center, slit_width, slit_length)
        for pin_center, slit_width in zip(CHOC_PIN_CENTERS_MM, slit_widths, strict=True)
    )


# The fused mock's default slits (DESIGN.md, "Plate and mocks"), for a
# print that swells by pull_in per side: across the blade the model's
# thickness plus pull_in per side (0.6 at the default pull_in), meant
# as a nominal zero clearance as printed, and along it its width plus
# pull_in per side plus SLIT_LENGTH_CLEARANCE_MM, so only the slit's
# width grips the blade. The width was the first slit test strip's
# default, and the user's print of that strip showed it does not grip
# (doc/log/2026-10-17.md). It stays until the second strip
# (export_slit_test.py) has been tried.
SLIT_LENGTH_CLEARANCE_MM = 0.4


def default_slit_width(pull_in):
    return CHOC_PIN_BLADE_THICKNESS_MM + 2.0 * pull_in


def default_slit_length(pull_in):
    return CHOC_PIN_BLADE_WIDTH_MM + 2.0 * pull_in + SLIT_LENGTH_CLEARANCE_MM


# The hotswap socket (Kailh CPG135001S001) under each key, in
# footprint-local coordinates, as convex polygons, corners in order
# around each, whose union holds the whole socket. The two offset lobes
# and the two 1.7 mm end tabs are kbdkid4's HOTSWAP_SOCKET_POLYGONS_MM
# and HOTSWAP_SOCKET_TAB_TIP_MM (model/kbdkid4/scripts/export_tray.py),
# measured there on LibrePCB's populated STEP export. The lobe nearer the tab tip has
# its corner beside the tab chamfered, just outside the body's 0.8 mm
# round. The lobes meet in sharp inside corners, which the body fills,
# as the socket's own STEP in kbdkid4's library
# (pkg/23d245ff-14f8-48ad-af68-56ebb3a76786, model 0c4954f5) shows at
# every height and Kailh's plan view too: at (-6.02, 2.25) the first
# lobe's face runs on to y 2.680 and meets the second lobe's side in a
# 0.75 radius, at (-3.57, 2.25) the second lobe reaches down to the
# first lobe's side in a 1.5 radius. HOTSWAP_SOCKET_FILLS_MM covers
# them, rectangles from that STEP's faces rounded outward to 0.01 (the
# 0.75 corner as two, the band along the first lobe and the radius's
# square), and a step on the second lobe's end from x -2.12 to -1.37,
# 0.08 past the lobe. Each rectangle covers its radius with some room to
# spare, so the polygons keep no acute corner. Elsewhere the STEP's
# outline lies inside the lobes and tabs (it chamfers or rounds their
# corners) or at most 0.003 past them, where their faces are rounded to
# 0.01 (the lobes' faces at x -8.22 and -6.02, the tabs' at -5.06 and
# -2.86). Mapped onto the board they span x from center - 9.28 to
# center + 3.87 and y from center - 8.22 to center - 1.37 (DESIGN.md,
# "Keys"). Each socket hangs HOTSWAP_SOCKET_REACH_MM below the PCB.
# These polygons are a cover of the body, not its outline: the lobes
# meet at y 2.25, 0.43 short of the real step between them at y 2.68
# (HOTSWAP_SOCKET_OUTLINE_MM below), so the second lobe's corner there,
# a 0.75 round, is squared off, and the fills cover the radii with
# rectangles. The tray's socket cuts and check_layout.py use them as
# such a cover. The socket test strips' pockets follow
# HOTSWAP_SOCKET_OUTLINE_MM instead.
HOTSWAP_SOCKET_LOBES_MM = (
    ((-8.22, -2.25), (-3.57, -2.25), (-3.57, 2.25), (-8.22, 2.25)),
    ((-6.02, 2.25), (-1.37, 2.25), (-1.37, 7.60), (-5.47, 7.60), (-6.02, 7.05)),
)
HOTSWAP_SOCKET_TABS_MM = (
    ((-4.54, 7.60), (-2.86, 7.60), (-2.86, 9.28), (-4.54, 9.28)),
    ((-6.74, -3.87), (-5.06, -3.87), (-5.06, -2.25), (-6.74, -2.25)),
)
HOTSWAP_SOCKET_FILLS_MM = (
    ((-7.91, 2.25), (-6.02, 2.25), (-6.02, 2.69), (-7.91, 2.69)),
    ((-6.78, 2.68), (-6.02, 2.68), (-6.02, 3.44), (-6.78, 3.44)),
    ((-3.57, 1.27), (-3.12, 1.27), (-3.12, 2.25), (-3.57, 2.25)),
    ((-2.12, 7.48), (-1.37, 7.48), (-1.37, 7.69), (-2.12, 7.69)),
)
HOTSWAP_SOCKET_POLYGONS_MM = HOTSWAP_SOCKET_LOBES_MM + HOTSWAP_SOCKET_TABS_MM + (
    HOTSWAP_SOCKET_FILLS_MM
)
HOTSWAP_SOCKET_TAB_TIP_MM = (-3.70, 9.28)

# The socket's plastic body along the tabs' axis (local y), from that
# STEP's end faces: 9.55, Kailh's plan view's 9.55 +-0.05
# (doc/components.md). The lobes above reach past it, to y -2.25 and
# 7.60, over the tabs' roots.
HOTSWAP_SOCKET_BODY_ENDS_MM = (-2.07, 7.48)
HOTSWAP_SOCKET_REACH_MM = 2.02

# The socket's plastic body as it is, in the same footprint-local frame:
# the outline of that STEP's body (solid 1 of
# library/pkg/23d245ff-14f8-48ad-af68-56ebb3a76786/
# 0c4954f5-24c7-4f36-a4b7-4bbd2ff10646.step) sectioned at mid-height,
# the two tabs left out and the body's ends straight across their
# roots. A start point, then lines to their end and arcs through a
# point on them to their end, clockwise. The first lobe is 4.75 long
# along the tabs' axis (y), from the body's end at -2.07 to the step at
# 2.68 (Kailh's plan view's 4.75 from the end), the second 4.80, from
# the step to the other end at 7.48. The arcs' centers and radii,
# recovered from the section (three points of each lie on the circle
# within 0.002): the 0.75 fill inside the step at (-6.773, 3.430), the
# second lobe's 0.75 rounds at (-5.273, 6.730) and (-2.123, 3.430), and
# the 1.5 fill between the second lobe and the first lobe's side at
# (-2.073, 1.180), tangent to y 2.68 at x -2.073. The STEP has a 0.05
# flat between that round and that fill, which the arc from the round's
# end absorbs within 0.001.
HOTSWAP_SOCKET_OUTLINE_MM = (
    (-4.323, -2.070),
    (
        ("line", (-7.473, -2.070)),  # the body's end, y -2.07
        ("line", (-8.223, -1.320)),  # a 0.75 chamfer
        ("line", (-8.223, 1.930)),  # the first lobe's west face
        ("line", (-7.473, 2.680)),  # a 0.75 chamfer
        ("line", (-6.773, 2.680)),  # the first lobe's north face, the step
        ("arc", (-6.243, 2.900), (-6.023, 3.430)),  # the 0.75 fill
        ("line", (-6.023, 6.730)),  # the second lobe's west face
        ("arc", (-5.803, 7.260), (-5.273, 7.480)),  # a 0.75 round
        ("line", (-2.115, 7.480)),  # the body's end, y 7.48
        ("line", (-2.115, 7.680)),  # a 0.2 step on that end
        ("line", (-1.373, 7.680)),
        ("line", (-1.373, 3.430)),  # the second lobe's east face
        ("arc", (-1.593, 2.900), (-2.123, 2.680)),  # a 0.75 round
        ("arc", (-3.134, 2.241), (-3.573, 1.180)),  # the 1.5 fill
        ("line", (-3.573, -1.320)),  # the first lobe's east face
        ("line", (-4.323, -2.070)),  # a 0.75 chamfer, back to the start
    ),
)

# The socket body's height, from its bottom to the bumps on its top face
# that bear on a board: Kailh's drawing (CPG135001S30 data sheet,
# doc/components.md), 1.80 +-0.05, its end tabs' tops 1.85 +-0.1. The
# STEP above models the body as one 1.85 block hung 0.17 below the PCB,
# hence the 2.02 reach. A socket pressed against a printed frame instead
# of soldered under a PCB hangs this far below it (work item 008).
HOTSWAP_SOCKET_BODY_HEIGHT_MM = 1.80


def socket_polygons(key_center):
    """A key's hotswap socket footprint in board coordinates, as convex
    polygons."""
    return tuple(
        footprint_polygon(key_center, polygon) for polygon in HOTSWAP_SOCKET_POLYGONS_MM
    )


def socket_tab_tip(key_center):
    return footprint_point(key_center, HOTSWAP_SOCKET_TAB_TIP_MM)


def mirrored_back_polygon(polygon):
    """A right half polygon mirrored back into the left half's frame,
    counter-clockwise again (mirroring reverses the order)."""
    return tuple(reversed([mirror_for_right_half(point) for point in polygon]))


def socket_polygons_on_half(key, right=False):
    """A key's socket polygons on the given half, in the left half's
    frame (see the module docstring), counter-clockwise."""
    center = KEY_CENTERS_MM[key]
    if not right:
        return socket_polygons(center)
    return tuple(
        mirrored_back_polygon(polygon)
        for polygon in socket_polygons(mirror_for_right_half(center))
    )


def socket_tab_tip_on_half(key, right=False):
    """A key's socket tab tip on the given half, in the left half's
    frame."""
    center = KEY_CENTERS_MM[key]
    if not right:
        return socket_tab_tip(center)
    return mirror_for_right_half(socket_tab_tip(mirror_for_right_half(center)))


# The diodes sit on the top side under the plate (DESIGN.md, "Keys").
# kbdkid5 places none until its PCB is designed, but the plate's
# covered variant needs one for the pit over its key's diode, so it
# takes kbdkid4's place: in kbdkid4's boards/board_1.1/board.lp every
# left-half diode D1xx sits 4.28 north of its key S1xx's center,
# rotated 180 degrees on the top side, its body along x (D123 at
# (47.149, 18.25) for S123 at (47.149, 13.97)).
DIODE_OFFSET_FROM_KEY_MM = (0.0, 4.28)
DIODE_ROTATION_DEGREES = 180.0


def diode_center(key_center):
    return (
        key_center[0] + DIODE_OFFSET_FROM_KEY_MM[0],
        key_center[1] + DIODE_OFFSET_FROM_KEY_MM[1],
    )


# The outline (DESIGN.md, "Outline"): kbdkid4's, with its
# microcontroller corner replaced by the slant. DESIGN.md rounds the
# vertices to 0.001 mm; kbdkid4's board.lp has, for example, 37.62375
# for 37.624. The cells are inset 0.476 at the west and the east, 0.318
# at the south and 0.397 at the north. Every corner is rounded with
# kbdkid4's 0.47625 (its board.lp outline arcs), also on the north
# edge west of x 95.3, which kbdkid4 rounds with 0.5 (DESIGN.md: kbdkid5
# uses 0.476 throughout).
CELL_INSET_WEST_MM = 0.476
CELL_INSET_EAST_MM = 0.476
CELL_INSET_SOUTH_MM = 0.318
CELL_INSET_NORTH_MM = 0.397
OUTLINE_CORNER_RADIUS_MM = 0.47625

# The slant runs from the thumb cell's top right corner to column 5's
# top cell's top right corner, both moved in by the east and north
# insets (DESIGN.md): parallel to the corner to corner line, 0.574
# inside it.
SLANT_SOUTH_END_MM = (132.398, 18.335)
SLANT_NORTH_END_MM = (113.348, 77.867)

OUTLINE_VERTICES_MM = (
    (0.0, 0.0),
    (37.624, 0.0),
    (37.624, 4.763),
    (56.674, 4.763),
    (56.674, 7.144),
    (75.724, 7.144),
    (75.724, 4.763),
    (94.774, 4.763),
    (94.774, 2.381),
    (113.824, 2.381),
    (113.824, 0.0),
    (132.398, 0.0),
    SLANT_SOUTH_END_MM,  # the east edge of the thumb, then the slant
    SLANT_NORTH_END_MM,
    (94.774, 77.867),
    (94.774, 80.248),
    (75.724, 80.248),
    (75.724, 82.629),
    (56.674, 82.629),
    (56.674, 80.248),
    (37.624, 80.248),
    (37.624, 75.486),
    (0.0, 75.486),
)
SLANT_EDGE_INDEX = OUTLINE_VERTICES_MM.index(SLANT_SOUTH_END_MM)


def slant_vector():
    return (
        SLANT_NORTH_END_MM[0] - SLANT_SOUTH_END_MM[0],
        SLANT_NORTH_END_MM[1] - SLANT_SOUTH_END_MM[1],
    )


def slant_length():
    return math.hypot(*slant_vector())


def slant_direction():
    """The unit vector along the slant, from its south end north."""
    vector_x, vector_y = slant_vector()
    length = slant_length()
    return (vector_x / length, vector_y / length)


def slant_outward_normal():
    """The unit vector across the slant, out of the half (east of
    north): the outline runs counter-clockwise, so its outside is on
    the right."""
    direction_x, direction_y = slant_direction()
    return (direction_y, -direction_x)


def slant_point(along, outward):
    """The point `along` mm from the slant's south end along it and
    `outward` mm out of the half across it."""
    direction = slant_direction()
    normal = slant_outward_normal()
    return (
        SLANT_SOUTH_END_MM[0] + along * direction[0] + outward * normal[0],
        SLANT_SOUTH_END_MM[1] + along * direction[1] + outward * normal[1],
    )


def slant_rectangle(along_center, along_width, outward_range):
    """A rectangle square to the slant, in plan: along_width wide along
    it around along_center, over outward_range across it. Outward lies
    clockwise of along, so going out first keeps the corners
    counter-clockwise."""
    low_along = along_center - along_width / 2.0
    high_along = along_center + along_width / 2.0
    low_outward, high_outward = outward_range
    return (
        slant_point(low_along, low_outward),
        slant_point(low_along, high_outward),
        slant_point(high_along, high_outward),
        slant_point(high_along, low_outward),
    )


# The mirror line for the right half (DESIGN.md, "Frame and units", and
# the module docstring): the outline's center line, x = 66.199.
RIGHT_HALF_MIRROR_X_MM = (
    min(x for x, _ in OUTLINE_VERTICES_MM) + max(x for x, _ in OUTLINE_VERTICES_MM)
) / 2.0


def mirror_for_right_half(point):
    """A left-half point's place on the right half. Mirroring reverses a
    polygon's orientation."""
    return (2.0 * RIGHT_HALF_MIRROR_X_MM - point[0], point[1])


# Mounting (DESIGN.md, "Mounting"): 2.4 mm drills, as kbdkid4's
# board.lp mounting pads, for M2 screws into heat-set inserts in the
# tray's standoffs. kbdkid4's (18.574, 56.832) moved to (18.574,
# 37.782), out from under the nice!nano.
MOUNTING_DRILL_DIAMETER_MM = 2.4
MOUNTING_DRILL_CENTERS_MM = (
    (18.574, 18.732),
    (18.574, 37.782),
    (76.041, 43.260),
    (94.774, 60.404),
    (114.141, 19.765),
)

# The tray (DESIGN.md, "Heights": all as kbdkid4). tray_shape.py
# re-exports these under kbdkid4's names.
TRAY_GAP_MM = 0.4  # PCB edge to the cavity wall
TRAY_WALL_MM = 0.8
TRAY_FLOOR_MM = 1.2
TRAY_LEDGE_WIDTH_MM = 1.0  # from the cavity wall, so it reaches 0.6 under the PCB
STANDOFF_DIAMETER_MM = 5.8
STANDOFF_BORE_DIAMETER_MM = 3.2

# Heights, z above the floor's top face (DESIGN.md, "Heights"). The PCB
# underside was kbdkid4's 8.0 (the user's choice for this first
# iteration: room for padding and margin around the parts) and went up
# 1.5 to 9.5, with the rim, so the hand-wired frame's backing clears
# the nice!nano's socket strips while the floor stays whole (the user,
# 2026-10-20: "Raise the frame assembly and the rim and the rim ledge
# accordingly. The whole thing becomes 1.5 mm taller, to accommodate
# the need for 1.5 mm higher ceiling in the tray cave. I don't want
# holes in the tray floor"). The screw heads under the backing then
# keep 0.773 from the battery (the user, the same day: "The M2 pan head
# screws I have today have roughly 1.5 mm high heads btw", by
# socket_test_shape.py's backing_screw_heads_bottom_z()). The parts on
# the floor stay where they are. The battery under the sockets sets the
# lowest the PCB could go, MINIMUM_PCB_UNDERSIDE_Z_MM: the battery, the
# 0.5 clearance and a socket.
BATTERY_THICKNESS_MM = 4.11
MINIMUM_BATTERY_TO_SOCKET_CLEARANCE_MM = 0.5
PCB_THICKNESS_MM = 1.6
PLATE_THICKNESS_MM = 2.2  # resting on the PCB
RIM_ABOVE_PLATE_MM = 0.1  # as on kbdkid4
PCB_UNDERSIDE_Z_MM = 9.5  # also the standoff and ledge tops
MINIMUM_PCB_UNDERSIDE_Z_MM = (
    BATTERY_THICKNESS_MM + MINIMUM_BATTERY_TO_SOCKET_CLEARANCE_MM + HOTSWAP_SOCKET_REACH_MM
)  # 6.63
FLOOR_UNDERSIDE_Z_MM = -TRAY_FLOOR_MM  # the 1.0 rubber sole goes under it
BATTERY_TOP_Z_MM = BATTERY_THICKNESS_MM
SOCKET_BOTTOM_Z_MM = PCB_UNDERSIDE_Z_MM - HOTSWAP_SOCKET_REACH_MM  # 7.48
PCB_TOP_Z_MM = PCB_UNDERSIDE_Z_MM + PCB_THICKNESS_MM  # 11.1
PLATE_TOP_Z_MM = PCB_TOP_Z_MM + PLATE_THICKNESS_MM  # 13.3
TRAY_RIM_Z_MM = PLATE_TOP_Z_MM + RIM_ABOVE_PLATE_MM  # 13.4
STANDOFF_HEIGHT_MM = PCB_UNDERSIDE_Z_MM


# The parts in the tray (DESIGN.md, "Parts in the tray"), as boxes:
# the bodies DESIGN.md gives, then the leads, pins and posts from the
# parts' datasheets and the battery header's mated plug, each a piece
# of its part. The mounts that hold them and the room their wires need
# come last in this module (work item 004).
# `containment` says where a box must lie: CAVITY inside the cavity
# wall and clear of the ledge (except where the ledge is cut away for
# it, ledge_cutaways()), THROUGH_WALL inside the tray's outer face (it
# passes a window in the wall), PROUD nowhere (it stands out past the
# wall by design).
CAVITY = "cavity"
THROUGH_WALL = "through the wall"
PROUD = "proud of the wall"


@dataclass(frozen=True)
class Envelope:
    part: str
    piece: str
    x_range: tuple
    y_range: tuple
    z_range: tuple
    containment: str


def cavity_wall_y(outline_edge_y):
    """The cavity wall's y behind a north outline edge at the given y."""
    return outline_edge_y + TRAY_GAP_MM


def outer_face_y(outline_edge_y):
    """The tray's outer face's y beyond a north outline edge."""
    return outline_edge_y + TRAY_GAP_MM + TRAY_WALL_MM


# North outline edges, by column (OUTLINE_VERTICES_MM).
NORTH_EDGE_Y_OF_COLUMNS_0_AND_1_MM = 75.486
NORTH_EDGE_Y_OF_COLUMN_2_MM = 80.248
NORTH_EDGE_Y_OF_COLUMN_3_MM = 82.629

# nice!nano v2 (DESIGN.md): the board, its flat underside on a seat
# NANO_SEAT_HEIGHT_MM over the floor's top (the user, 2026-10-20:
# "Could you raise up the whole bay the nano rests in and pocket the two
# 12 pin strips on the sides?"), which the socket strips' solder tails
# under the board clear by 0.387 (nano_tail_envelopes()). Its west edge
# 0.3 from the west ledge's face, its USB end where the shell's mouth
# lies 0.5 behind the north wall's outer face. Its size is the user's
# caliper of 2026-10-20: the width the middle of "The nano width is
# 18.17~18.23 mm", which supersedes the 18.30 read with the shell on
# 2026-10-19 ("The nano measures, with the usb connector included: 18.30
# x 34.17", doc/log/2026-10-19.md), the length "Board length 33.20",
# which replaces the 33.3 derived from the render. It is 1.6 thick
# (doc/components.md). The USB-C shell, flush with the board's
# underside, 8.94 wide and 3.16 tall, reaching 0.87 past the board's
# north end, 6.5 long (doc/components.md: the C168688 drawing's front
# to rear of the body), centered on the board. The 0.87 is the render's
# and has not been measured: the user's 34.17 with the shell less the
# 33.20 board would make it 0.97, and the mouth would then lie 0.4
# behind the wall's outer face.
NANO_SEAT_HEIGHT_MM = 1.2
NANO_WEST_X_MM = 0.9
NANO_USB_END_Y_MM = 75.316
NANO_WIDTH_MM = 18.20
NANO_LENGTH_MM = 33.20
NANO_BOARD_THICKNESS_MM = 1.6
NANO_BOARD = Envelope(
    "nice!nano",
    "board",
    (NANO_WEST_X_MM, NANO_WEST_X_MM + NANO_WIDTH_MM),
    (NANO_USB_END_Y_MM - NANO_LENGTH_MM, NANO_USB_END_Y_MM),
    (NANO_SEAT_HEIGHT_MM, NANO_SEAT_HEIGHT_MM + NANO_BOARD_THICKNESS_MM),
    CAVITY,
)
NANO_USB_SHELL_WIDTH_MM = 8.94
NANO_USB_SHELL_HEIGHT_MM = 3.16
NANO_USB_SHELL_PAST_BOARD_MM = 0.87
NANO_USB_SHELL_LENGTH_MM = 6.5
NANO_USB_SHELL_CENTER_X_MM = sum(NANO_BOARD.x_range) / 2.0
NANO_USB_SHELL = Envelope(
    "nice!nano",
    "USB-C shell",
    (NANO_USB_SHELL_CENTER_X_MM - NANO_USB_SHELL_WIDTH_MM / 2.0,
     NANO_USB_SHELL_CENTER_X_MM + NANO_USB_SHELL_WIDTH_MM / 2.0),
    (
        NANO_BOARD.y_range[1] + NANO_USB_SHELL_PAST_BOARD_MM - NANO_USB_SHELL_LENGTH_MM,
        NANO_BOARD.y_range[1] + NANO_USB_SHELL_PAST_BOARD_MM,
    ),
    (NANO_BOARD.z_range[0], NANO_BOARD.z_range[0] + NANO_USB_SHELL_HEIGHT_MM),
    THROUGH_WALL,
)

# Power switch, SOFNG SS-12D00-G3 (DESIGN.md): the body 8.8 along x
# (the lever's travel), 3.5 along y, 3.9 tall, centered at x 47.149 with
# its north face against column 2's cavity wall (DESIGN.md: y 80.648).
# The lever, 1.5 x 1.5 x 3 on the body's north face, swept over its 2
# travel (doc/components.md) around the body's center, through a slot
# in the wall, centered on the face's 3.9 like the three pins on the
# opposite face (the SOFNG drawing's end view,
# work/research/downloads/ss12d00/sofng_SS-12D00-G3.pdf). The pins,
# 0.5 along x and 0.3 thick, 2.5 apart along x around the center (its
# side view and PCB layout), point south 3.0 from the body.
POWER_SWITCH_CENTER_X_MM = 47.149
POWER_SWITCH_BODY_X_MM = 8.8
POWER_SWITCH_BODY_Y_MM = 3.5
POWER_SWITCH_BODY_Z_MM = 3.9
POWER_SWITCH_LEVER_WIDTH_MM = 1.5
POWER_SWITCH_LEVER_LENGTH_MM = 3.0
POWER_SWITCH_LEVER_TRAVEL_MM = 2.0
POWER_SWITCH_NORTH_FACE_Y_MM = 80.648
POWER_SWITCH_BODY = Envelope(
    "power switch",
    "body",
    (
        POWER_SWITCH_CENTER_X_MM - POWER_SWITCH_BODY_X_MM / 2.0,
        POWER_SWITCH_CENTER_X_MM + POWER_SWITCH_BODY_X_MM / 2.0,
    ),
    (POWER_SWITCH_NORTH_FACE_Y_MM - POWER_SWITCH_BODY_Y_MM, POWER_SWITCH_NORTH_FACE_Y_MM),
    (0.0, POWER_SWITCH_BODY_Z_MM),
    CAVITY,
)
POWER_SWITCH_LEVER_REACH_X_MM = (
    POWER_SWITCH_LEVER_TRAVEL_MM / 2.0 + POWER_SWITCH_LEVER_WIDTH_MM / 2.0
)
POWER_SWITCH_LEVER_Z_MM = POWER_SWITCH_BODY_Z_MM / 2.0  # its middle
POWER_SWITCH_LEVER = Envelope(
    "power switch",
    "lever, over its travel",
    (
        POWER_SWITCH_CENTER_X_MM - POWER_SWITCH_LEVER_REACH_X_MM,
        POWER_SWITCH_CENTER_X_MM + POWER_SWITCH_LEVER_REACH_X_MM,
    ),
    (
        POWER_SWITCH_NORTH_FACE_Y_MM,
        POWER_SWITCH_NORTH_FACE_Y_MM + POWER_SWITCH_LEVER_LENGTH_MM,
    ),
    (
        POWER_SWITCH_LEVER_Z_MM - POWER_SWITCH_LEVER_WIDTH_MM / 2.0,
        POWER_SWITCH_LEVER_Z_MM + POWER_SWITCH_LEVER_WIDTH_MM / 2.0,
    ),
    PROUD,
)
POWER_SWITCH_PIN_PITCH_MM = 2.5
POWER_SWITCH_PIN_WIDTH_MM = 0.5
POWER_SWITCH_PIN_THICKNESS_MM = 0.3
POWER_SWITCH_PIN_LENGTH_MM = 3.0
POWER_SWITCH_PINS_REACH_X_MM = POWER_SWITCH_PIN_PITCH_MM + POWER_SWITCH_PIN_WIDTH_MM / 2.0
POWER_SWITCH_PINS = Envelope(
    "power switch",
    "pins",
    (
        POWER_SWITCH_CENTER_X_MM - POWER_SWITCH_PINS_REACH_X_MM,
        POWER_SWITCH_CENTER_X_MM + POWER_SWITCH_PINS_REACH_X_MM,
    ),
    (
        POWER_SWITCH_BODY.y_range[0] - POWER_SWITCH_PIN_LENGTH_MM,
        POWER_SWITCH_BODY.y_range[0],
    ),
    (
        POWER_SWITCH_LEVER_Z_MM - POWER_SWITCH_PIN_THICKNESS_MM / 2.0,
        POWER_SWITCH_LEVER_Z_MM + POWER_SWITCH_PIN_THICKNESS_MM / 2.0,
    ),
    CAVITY,
)

# Reset button, C&K PTS636 SL43 LFS (DESIGN.md), lying on its side:
# 6.0 along x centered at x 66.199, 3.5 along z, 4.3 from its back to
# the stem's top along y, the stem ending 0.2 short of column 3's
# cavity wall. Its housing is 3.3 of those 4.3 (doc/components.md, the
# PTS636 datasheet), the 3 x 1.5 stem the rest, centered on the
# housing along x and, its 1.5 along z, on the housing's 3.5 (the
# datasheet's end view, work/research/downloads/pts636/pts636_lcsc.pdf,
# page 2). The two leads, 1 wide along z and centered on it too, leave
# the housing's ends at its back, kink out to 7.7 across their outsides
# 2.0 behind it and run on at 6.4 pitch to 3.9 behind it, each figure
# +-0.2 (RESET_BUTTON_TOLERANCE_MM). Their thickness along x is not in
# the datasheet: RESET_BUTTON_LEAD_THICKNESS_MM is assumed.
RESET_BUTTON_CENTER_X_MM = 66.199
RESET_BUTTON_BODY_X_MM = 6.0
RESET_BUTTON_BODY_Z_MM = 3.5
RESET_BUTTON_TO_STEM_TOP_MM = 4.3
RESET_BUTTON_HOUSING_DEPTH_MM = 3.3
RESET_BUTTON_STEM_WIDTH_MM = 3.0  # along x
RESET_BUTTON_STEM_THICKNESS_MM = 1.5  # along z
RESET_BUTTON_STEM_SHORT_OF_WALL_MM = 0.2
RESET_BUTTON_STEM_TOP_Y_MM = (
    cavity_wall_y(NORTH_EDGE_Y_OF_COLUMN_3_MM) - RESET_BUTTON_STEM_SHORT_OF_WALL_MM
)
RESET_BUTTON_BACK_Y_MM = RESET_BUTTON_STEM_TOP_Y_MM - RESET_BUTTON_TO_STEM_TOP_MM
RESET_BUTTON_HOUSING = Envelope(
    "reset button",
    "housing",
    (
        RESET_BUTTON_CENTER_X_MM - RESET_BUTTON_BODY_X_MM / 2.0,
        RESET_BUTTON_CENTER_X_MM + RESET_BUTTON_BODY_X_MM / 2.0,
    ),
    (RESET_BUTTON_BACK_Y_MM, RESET_BUTTON_BACK_Y_MM + RESET_BUTTON_HOUSING_DEPTH_MM),
    (0.0, RESET_BUTTON_BODY_Z_MM),
    CAVITY,
)
RESET_BUTTON_STEM = Envelope(
    "reset button",
    "stem",
    (
        RESET_BUTTON_CENTER_X_MM - RESET_BUTTON_STEM_WIDTH_MM / 2.0,
        RESET_BUTTON_CENTER_X_MM + RESET_BUTTON_STEM_WIDTH_MM / 2.0,
    ),
    (RESET_BUTTON_BACK_Y_MM + RESET_BUTTON_HOUSING_DEPTH_MM, RESET_BUTTON_STEM_TOP_Y_MM),
    (
        (RESET_BUTTON_BODY_Z_MM - RESET_BUTTON_STEM_THICKNESS_MM) / 2.0,
        (RESET_BUTTON_BODY_Z_MM + RESET_BUTTON_STEM_THICKNESS_MM) / 2.0,
    ),
    CAVITY,
)
RESET_BUTTON_LEAD_PITCH_MM = 6.4
RESET_BUTTON_LEAD_KINK_SPAN_MM = 7.7  # across the leads' outsides
RESET_BUTTON_LEAD_WIDTH_MM = 1.0  # along z
RESET_BUTTON_LEAD_LENGTH_MM = 3.9  # behind the housing
RESET_BUTTON_LEAD_THICKNESS_MM = 0.4  # assumed
RESET_BUTTON_TOLERANCE_MM = 0.2


def reset_button_lead_band():
    """(inside, outside) of either lead from the button's center along
    x, over every place the datasheet's figures allow."""
    inside = (
        RESET_BUTTON_LEAD_PITCH_MM - RESET_BUTTON_TOLERANCE_MM - RESET_BUTTON_LEAD_THICKNESS_MM
    ) / 2.0
    outside = (RESET_BUTTON_LEAD_KINK_SPAN_MM + RESET_BUTTON_TOLERANCE_MM) / 2.0
    return inside, outside


def reset_button_lead_z_range():
    half = (RESET_BUTTON_LEAD_WIDTH_MM + RESET_BUTTON_TOLERANCE_MM) / 2.0
    middle = RESET_BUTTON_BODY_Z_MM / 2.0
    return (middle - half, middle + half)


def reset_button_lead(side, label):
    """A lead's envelope, side -1 the west one and 1 the east one: from
    its tip at the most the tolerance allows to RESET_BUTTON_HOUSING's
    back, and on along the housing's end as far as the housing's back
    third."""
    inside, outside = reset_button_lead_band()
    reach = sorted(
        (RESET_BUTTON_CENTER_X_MM + side * inside, RESET_BUTTON_CENTER_X_MM + side * outside)
    )
    tip_y = RESET_BUTTON_BACK_Y_MM - RESET_BUTTON_LEAD_LENGTH_MM - RESET_BUTTON_TOLERANCE_MM
    along_housing_y = RESET_BUTTON_BACK_Y_MM + RESET_BUTTON_HOUSING_DEPTH_MM / 3.0
    return Envelope(
        "reset button",
        label,
        tuple(reach),
        (tip_y, along_housing_y),
        reset_button_lead_z_range(),
        CAVITY,
    )


RESET_BUTTON_WEST_LEAD = reset_button_lead(-1.0, "west lead")
RESET_BUTTON_EAST_LEAD = reset_button_lead(1.0, "east lead")

# Battery connector, JST PH B2B-PH-K-S laid on its side (DESIGN.md):
# the header, 4.5 tall like the mated plug and header. Its two posts,
# 0.64 square at 2.0 pitch along y around the header's middle, reach
# 3.4 east of it, along z 1.78 from one of its 4.5 faces (JST's PH
# catalogue, work/research/downloads/jst-ph/eph2.pdf, page 3: the
# B2B-PH-K-S side view, measured on its drawing), so their box takes
# that place from either face. Mated, the PHR-2 plug's housing (5.8
# along y, 4.5 along z by the catalogue) stands 2.0 out of the
# header's entry face: mated 8 tall against the header's 6.0. The
# header's middle sits at y 74.6, far enough south that the wire room
# behind its posts (wire_rooms()) keeps 0.35 from the ledge where the
# north edge steps in to column 5's at x 94.774.
BATTERY_CONNECTOR = Envelope(
    "battery connector", "header", (85.0, 91.0), (71.65, 77.55), (0.0, 4.5), CAVITY
)
BATTERY_CONNECTOR_MIDDLE_Y_MM = sum(BATTERY_CONNECTOR.y_range) / 2.0
BATTERY_CONNECTOR_POST_PITCH_MM = 2.0
BATTERY_CONNECTOR_POST_SIZE_MM = 0.64
BATTERY_CONNECTOR_POST_LENGTH_MM = 3.4
BATTERY_CONNECTOR_POST_FROM_FACE_MM = 1.78
BATTERY_PLUG_WIDTH_MM = 5.8
BATTERY_PLUG_DEPTH_MM = 4.5
BATTERY_PLUG_OUT_OF_HEADER_MM = 8.0 - 6.0


def battery_connector_posts_z_range():
    height = BATTERY_CONNECTOR.z_range[1]
    half = BATTERY_CONNECTOR_POST_SIZE_MM / 2.0
    return (
        BATTERY_CONNECTOR_POST_FROM_FACE_MM - half,
        height - BATTERY_CONNECTOR_POST_FROM_FACE_MM + half,
    )


BATTERY_CONNECTOR_POSTS_REACH_Y_MM = (
    BATTERY_CONNECTOR_POST_PITCH_MM + BATTERY_CONNECTOR_POST_SIZE_MM
) / 2.0
BATTERY_CONNECTOR_POSTS = Envelope(
    "battery connector",
    "posts",
    (
        BATTERY_CONNECTOR.x_range[1],
        BATTERY_CONNECTOR.x_range[1] + BATTERY_CONNECTOR_POST_LENGTH_MM,
    ),
    (
        BATTERY_CONNECTOR_MIDDLE_Y_MM - BATTERY_CONNECTOR_POSTS_REACH_Y_MM,
        BATTERY_CONNECTOR_MIDDLE_Y_MM + BATTERY_CONNECTOR_POSTS_REACH_Y_MM,
    ),
    battery_connector_posts_z_range(),
    CAVITY,
)
BATTERY_PLUG = Envelope(
    "battery connector",
    "mated plug",
    (
        BATTERY_CONNECTOR.x_range[0] - BATTERY_PLUG_OUT_OF_HEADER_MM,
        BATTERY_CONNECTOR.x_range[0],
    ),
    (
        BATTERY_CONNECTOR_MIDDLE_Y_MM - BATTERY_PLUG_WIDTH_MM / 2.0,
        BATTERY_CONNECTOR_MIDDLE_Y_MM + BATTERY_PLUG_WIDTH_MM / 2.0,
    ),
    (0.0, BATTERY_PLUG_DEPTH_MM),
    CAVITY,
)

# Battery (DESIGN.md): the 34.37 x 51.53 x 4.11 pouch.
BATTERY = Envelope(
    "battery", "pouch", (22.0, 56.37), (8.1, 59.63), (0.0, BATTERY_TOP_Z_MM), CAVITY
)

# The PCB connector's clear zone (DESIGN.md): no tray feature above
# z 0 there, up to the PCB's underside.
PCB_CONNECTOR_CLEAR_ZONE = Envelope(
    "PCB connector",
    "clear zone",
    (20.0, 37.0),
    (65.5, 74.5),
    (0.0, PCB_UNDERSIDE_Z_MM),
    CAVITY,
)

PART_ENVELOPES = (
    NANO_BOARD,
    NANO_USB_SHELL,
    POWER_SWITCH_BODY,
    POWER_SWITCH_LEVER,
    POWER_SWITCH_PINS,
    RESET_BUTTON_HOUSING,
    RESET_BUTTON_STEM,
    RESET_BUTTON_WEST_LEAD,
    RESET_BUTTON_EAST_LEAD,
    BATTERY_CONNECTOR,
    BATTERY_CONNECTOR_POSTS,
    BATTERY_PLUG,
    BATTERY,
    PCB_CONNECTOR_CLEAR_ZONE,
)


# Where DESIGN.md cuts the north ledge away, as (part, x range along the
# north outline edge at the given y): over the nice!nano's width, the
# power switch body and the reset button, each plus 0.5 on either side.
# The nice!nano's follows the board's width as the mounts' fits size it,
# so ledge_cutaways() gives them all, with the mounts below.
LEDGE_CUTAWAY_MARGIN_MM = 0.5


@dataclass(frozen=True)
class LedgeCutaway:
    part: str
    x_range: tuple
    north_edge_y: float


def ledge_cutaway(part, x_range, north_edge_y):
    low_x, high_x = x_range
    return LedgeCutaway(
        part,
        (low_x - LEDGE_CUTAWAY_MARGIN_MM, high_x + LEDGE_CUTAWAY_MARGIN_MM),
        north_edge_y,
    )


SWITCH_AND_BUTTON_LEDGE_CUTAWAYS = (
    ledge_cutaway("power switch", POWER_SWITCH_BODY.x_range, NORTH_EDGE_Y_OF_COLUMN_2_MM),
    ledge_cutaway("reset button", RESET_BUTTON_HOUSING.x_range, NORTH_EDGE_Y_OF_COLUMN_3_MM),
)


# The sockets against the tray (DESIGN.md, "Tray"): kbdkid4's rules
# (model/kbdkid4/scripts/export_tray.py), on the outline's sharp
# edges where kbdkid4 used the straight stretches between the corner
# rounds. Along an edge is measured from its start vertex, across it
# outward (outline_edge_frame()). The layout names the sockets each rule
# applies to, for each half, and the functions below work out the cuts
# by the rule, the right half's in the left half's frame. check_layout.py
# checks that the sockets then keep the rules' clearances from the
# ledge, the wall and the standoffs on both halves, so a socket left out
# fails there.
#
# Ledge cuts run through the ledge's full width: from
# LEDGE_CUT_OVERSHOOT_MM inside its inner face, where kbdkid4's cutters
# started (at a corner that takes the end of the next edge's ledge
# too), out to the wall's inner face.
LEDGE_CUT_OVERSHOOT_MM = 0.5

# Tab notches and pockets: a socket's tab tip (socket_tab_tip()) within
# LEDGE_NOTCH_CLEARANCE_MM of the ledge's inner face, alongside an
# outline edge rather than nearest one of its ends, gets a notch in the
# ledge LEDGE_NOTCH_WIDTH_MM along the edge, centered on the tip, from
# the ledge top LEDGE_NOTCH_DEPTH_MM down (the socket and its solder
# need 2 of each). Where the tip then lies closer than that clearance
# to the wall, the wall's inner face gets a pocket over the notch's
# width, deep enough to leave the tip the clearance, from the notch's
# bottom to the clearance above the ledge top, since the tab's top
# sits just under the PCB.
LEDGE_NOTCH_WIDTH_MM = 3.0
LEDGE_NOTCH_DEPTH_MM = 3.0
LEDGE_NOTCH_CLEARANCE_MM = 0.5
SOCKET_TAB_NOTCH_KEYS = ("S100", "S101", "S102", "S103")  # column 0, along the west edge
# On the right half the thumb's tab, along the thumb's outer edge (the
# east edge in the left half's frame).
RIGHT_SOCKET_TAB_NOTCH_KEYS = ("S163",)

# Ledge reliefs: wherever a socket polygon comes within
# LEDGE_RELIEF_CLEARANCE_MM of the ledge's inner face along an outline
# edge but the slant (the joint block takes the ledge's place there),
# the ledge is cut through its full width over the polygon's extent
# along the edge plus the clearance at both ends, from the ledge top
# down to the socket's reach below the PCB plus
# LEDGE_RELIEF_MARGIN_BELOW_MM. A stub shorter than
# LEDGE_RELIEF_SHORTEST_STUB_MM left at an edge's end goes too: the cut
# then runs past the corner by the ledge's width and the gap.
LEDGE_RELIEF_CLEARANCE_MM = 0.5
LEDGE_RELIEF_MARGIN_BELOW_MM = 0.5
LEDGE_RELIEF_SHORTEST_STUB_MM = 1.0
# Column 0's tabs (inside their notches), and the bottom row's lobes
# beside the south ledge.
SOCKET_LEDGE_RELIEF_KEYS = (
    "S100",
    "S101",
    "S102",
    "S103",
    "S113",
    "S123",
    "S133",
    "S143",
    "S153",
    "S163",
)
# On the right half the bottom row's lobes, and the thumb's tab (inside
# its notch).
RIGHT_SOCKET_LEDGE_RELIEF_KEYS = ("S103", "S113", "S123", "S133", "S143", "S153", "S163")

# Standoff flats: wherever a socket polygon comes within
# STANDOFF_RELIEF_CLEARANCE_MM of a standoff in plan, the standoff gets
# a vertical flat facing the polygon's nearest point, the clearance
# short of it, from the socket's reach plus the clearance below the PCB
# (never below the floor) up to the standoff top. kbdkid4 took twice
# the ledge's clearance here, since the board can shift about 0.2 in
# the cavity before the screws pull it into place and the standoffs
# have plastic to spare. A flat must leave
# STANDOFF_RELIEF_MINIMUM_WALL_MM of plastic around the insert bore.
STANDOFF_RELIEF_CLEARANCE_MM = 1.0
STANDOFF_RELIEF_MINIMUM_WALL_MM = 0.6
SOCKET_STANDOFF_FLATS = (  # (standoff center, key)
    ((76.041, 43.260), "S141"),
    ((94.774, 60.404), "S150"),
)
# No right half socket comes within the clearance of a standoff.
RIGHT_SOCKET_STANDOFF_FLATS = ()


def socket_tab_notch_keys(right=False):
    return RIGHT_SOCKET_TAB_NOTCH_KEYS if right else SOCKET_TAB_NOTCH_KEYS


def socket_ledge_relief_keys(right=False):
    return RIGHT_SOCKET_LEDGE_RELIEF_KEYS if right else SOCKET_LEDGE_RELIEF_KEYS


def socket_standoff_flat_declarations(right=False):
    """(standoff center, key) of the given half's flats."""
    return RIGHT_SOCKET_STANDOFF_FLATS if right else SOCKET_STANDOFF_FLATS


@dataclass(frozen=True)
class TrayCut:
    """A box cut out of the ledge, and with cuts_wall out of the wall's
    inner face too: in plan the rectangle over along_range and
    across_range in outline edge edge_index's frame
    (tray_cut_polygon()), over z_range."""

    label: str
    edge_index: int
    along_range: tuple
    across_range: tuple
    z_range: tuple
    cuts_wall: bool = False


@dataclass(frozen=True)
class StandoffFlat:
    """A vertical flat on the standoff at standoff_center, square to the
    unit vector `toward` the socket's nearest point (socket_distance
    away), plane_distance from the center, over z_range."""

    label: str
    standoff_center: tuple
    toward: tuple
    plane_distance: float
    socket_distance: float
    z_range: tuple


def ledge_reach():
    """How far the ledge reaches in under the PCB from the outline."""
    return TRAY_LEDGE_WIDTH_MM - TRAY_GAP_MM


def ledge_cut_across_range():
    return (-(ledge_reach() + LEDGE_CUT_OVERSHOOT_MM), TRAY_GAP_MM)


def socket_tab_tip_on_edge(key, right=False):
    """(edge index, along, past the edge) of a key's tab tip on the
    given half against the outline edge nearest it, or None when that
    edge's nearest point is one of its ends: the tip is beside a corner,
    not alongside an edge."""
    tip = socket_tab_tip_on_half(key, right)
    index = nearest_outline_edge_index(tip)
    along, past_edge = outline_edge_coordinates(tip, index)
    if not 0.0 < along < outline_edge_length(index):
        return None
    return index, along, past_edge


def socket_tab_cuts(key, right=False):
    """The notch and the pocket (TrayCut) the tab rule cuts for a key's
    socket on the given half: either, both or neither."""
    on_edge = socket_tab_tip_on_edge(key, right)
    if on_edge is None:
        return ()
    index, along, past_edge = on_edge
    half_width = LEDGE_NOTCH_WIDTH_MM / 2.0
    along_range = (along - half_width, along + half_width)
    bottom = PCB_UNDERSIDE_Z_MM - LEDGE_NOTCH_DEPTH_MM
    cuts = []
    if past_edge >= -(ledge_reach() + LEDGE_NOTCH_CLEARANCE_MM):
        notch_z_range = (bottom, PCB_UNDERSIDE_Z_MM)
        cuts.append(
            TrayCut(f"{key} tab notch", index, along_range, ledge_cut_across_range(), notch_z_range)
        )
    # The tip's distance to the wall does not depend on the ledge.
    pocket_depth = LEDGE_NOTCH_CLEARANCE_MM - (TRAY_GAP_MM - past_edge)
    if pocket_depth > 0.0:
        across_range = (ledge_cut_across_range()[0], TRAY_GAP_MM + pocket_depth)
        pocket_z_range = (bottom, PCB_UNDERSIDE_Z_MM + LEDGE_NOTCH_CLEARANCE_MM)
        cuts.append(
            TrayCut(f"{key} tab pocket", index, along_range, across_range, pocket_z_range, True)
        )
    return tuple(cuts)


def ledge_relief(label, polygon, index):
    """The relief (a TrayCut, in a tuple) along outline edge `index` for
    a socket polygon, or none when the polygon is not alongside that
    edge's ledge."""
    coordinates = [outline_edge_coordinates(corner, index) for corner in polygon]
    alongs = [along for along, _ in coordinates]
    acrosses = [across for _, across in coordinates]
    length = outline_edge_length(index)
    low = min(alongs) - LEDGE_RELIEF_CLEARANCE_MM
    high = max(alongs) + LEDGE_RELIEF_CLEARANCE_MM
    if max(acrosses) < -(ledge_reach() + LEDGE_RELIEF_CLEARANCE_MM):
        return ()  # clear of this edge's ledge
    if min(acrosses) > TRAY_GAP_MM or high < 0.0 or low > length:
        return ()  # not alongside this edge
    past_corner = TRAY_LEDGE_WIDTH_MM + TRAY_GAP_MM
    if low < LEDGE_RELIEF_SHORTEST_STUB_MM:
        low = -past_corner
    if length - high < LEDGE_RELIEF_SHORTEST_STUB_MM:
        high = length + past_corner
    bottom = PCB_UNDERSIDE_Z_MM - HOTSWAP_SOCKET_REACH_MM - LEDGE_RELIEF_MARGIN_BELOW_MM
    z_range = (bottom, PCB_UNDERSIDE_Z_MM)
    return (TrayCut(label, index, (low, high), ledge_cut_across_range(), z_range),)


def socket_ledge_reliefs(key, right=False):
    """The reliefs the rule cuts for a key's socket on the given half,
    one per socket polygon and outline edge it lies alongside."""
    return tuple(
        relief
        for polygon in socket_polygons_on_half(key, right)
        for index in range(len(OUTLINE_VERTICES_MM))
        if index != SLANT_EDGE_INDEX
        for relief in ledge_relief(f"{key} socket relief", polygon, index)
    )


def socket_standoff_flats(standoff_center, key, right=False):
    """The flats the rule cuts into a standoff for a key's socket on the
    given half, one per socket polygon within
    STANDOFF_RELIEF_CLEARANCE_MM of it."""
    reach_below_pcb = HOTSWAP_SOCKET_REACH_MM + STANDOFF_RELIEF_CLEARANCE_MM
    z_range = (max(PCB_UNDERSIDE_Z_MM - reach_below_pcb, 0.0), STANDOFF_HEIGHT_MM)
    flats = []
    for polygon in socket_polygons_on_half(key, right):
        distance, nearest = nearest_polygon_point(standoff_center, polygon)
        plane_distance = distance - STANDOFF_RELIEF_CLEARANCE_MM
        if plane_distance >= STANDOFF_DIAMETER_MM / 2.0:
            continue  # the polygon clears this standoff
        toward = (
            (nearest[0] - standoff_center[0]) / distance,
            (nearest[1] - standoff_center[1]) / distance,
        )
        flats.append(
            StandoffFlat(
                f"{key} socket flat", standoff_center, toward, plane_distance, distance, z_range
            )
        )
    return tuple(flats)


def all_socket_tray_cuts(right=False):
    """Every notch, pocket and relief the given half's sockets get, the
    tab cuts first."""
    tab_cuts = tuple(
        cut for key in socket_tab_notch_keys(right) for cut in socket_tab_cuts(key, right)
    )
    reliefs = tuple(
        cut for key in socket_ledge_relief_keys(right) for cut in socket_ledge_reliefs(key, right)
    )
    return tab_cuts + reliefs


def all_socket_standoff_flats(right=False):
    return tuple(
        flat
        for center, key in socket_standoff_flat_declarations(right)
        for flat in socket_standoff_flats(center, key, right)
    )


def ledge_cutaway_edge_index(cutaway):
    """The north outline edge a ledge cut-away lies on: horizontal at
    the cut-away's y, covering its x range, running west (the outline
    runs counter-clockwise)."""
    low_x, high_x = cutaway.x_range
    for index in range(len(OUTLINE_VERTICES_MM)):
        start, end = outline_edge_ends(index)
        if (
            abs(start[1] - cutaway.north_edge_y) < 1e-9
            and abs(end[1] - cutaway.north_edge_y) < 1e-9
            and end[0] <= low_x
            and high_x <= start[0]
        ):
            return index
    raise ValueError(
        f"no north outline edge at y {cutaway.north_edge_y} covers the "
        f"{cutaway.part}'s ledge cut-away over x {cutaway.x_range}"
    )


def ledge_cutaway_cut(cutaway):
    """A ledge cut-away as a cut through the ledge's full width and
    height. Its north edge runs west, so along it is the start's x less
    x."""
    index = ledge_cutaway_edge_index(cutaway)
    start_x = OUTLINE_VERTICES_MM[index][0]
    low_x, high_x = cutaway.x_range
    return TrayCut(
        f"{cutaway.part} cut-away",
        index,
        (start_x - high_x, start_x - low_x),
        ledge_cut_across_range(),
        (0.0, PCB_UNDERSIDE_Z_MM),
    )


def tray_cut_polygon(cut):
    """A cut's rectangle in plan, counter-clockwise (outward lies
    clockwise of along)."""
    (low_along, high_along), (low_across, high_across) = cut.along_range, cut.across_range
    return tuple(
        outline_edge_point(cut.edge_index, along, across)
        for along, across in (
            (low_along, low_across),
            (low_along, high_across),
            (high_along, high_across),
            (high_along, low_across),
        )
    )


# The joint (DESIGN.md, "The joint"). Positions along the slant are
# measured from its south end (slant_point()), across it from the
# outline outward; the tray's outer face, the joint face, lies
# TRAY_GAP_MM + TRAY_WALL_MM out.
JOINT_FACE_OUTWARD_MM = TRAY_GAP_MM + TRAY_WALL_MM

# The block: the slanted wall 4.0 thick from the joint face, from the
# floor up to the ledge top, in place of the ledge.
JOINT_BLOCK_THICKNESS_MM = 4.0
JOINT_BLOCK_TOP_Z_MM = PCB_UNDERSIDE_Z_MM

# The joint face's bottom edge is chamfered, so elephant foot (the first
# layers squashed out past the face) cannot keep the faces apart.
JOINT_FACE_BOTTOM_CHAMFER_MM = 0.4

# Printed fits. A print swells PRINT_SWELLING_PER_SIDE_MM per side (the
# PCB mock's pull_in), so a hole or slot comes out that much smaller per
# side than modelled. Each fit is modelled as the part's nominal size
# plus the swelling on both sides plus the fit's clearance, so that it
# prints as the nominal size plus the clearance. A 45 degree face swells
# as much along its normal, which moves it PRINT_SWELLING_AT_45_DEGREES_MM
# along x, y or z.
PRINT_SWELLING_PER_SIDE_MM = 0.2
PRINT_SWELLING_AT_45_DEGREES_MM = PRINT_SWELLING_PER_SIDE_MM * math.sqrt(2.0)
SNUG_FIT_MM = 0.0  # holds a part pressed in by hand
SLIP_FIT_MM = 0.1  # lets a part slide in, or leaves room for glue


def printed_fit(nominal, fit):
    return nominal + 2.0 * PRINT_SWELLING_PER_SIDE_MM + fit


# An up-facing bottom that a part must fit over (a notch's, a slot's, the
# pry recess's) is counted this much higher as printed, as the fits above
# count it. The floor left under such a bottom is counted where it is
# modelled, the thinner reading.
PRINT_RISE_OF_UP_FACING_BOTTOMS_MM = PRINT_SWELLING_PER_SIDE_MM

# A print's top surface, the face that faces up on the bed, comes out
# this much higher than modelled: measured 2026-10-19 on the socket
# pocket strip, whose 1.6 frame body came out "roughly 1.65, measured
# with the calipers touching as large an area as possible"
# (doc/log/2026-10-19.md). The user's reading: the face on the bed is
# true to the model and the top face is rough rather than swollen, as
# the nozzle melts and lays material over it. The hand-wired frame's
# ceiling, the switch plate's underside (both print top face down) and
# the backing's top are such faces. The floors of notches, slots,
# recesses and blind bores keep PRINT_RISE_OF_UP_FACING_BOTTOMS_MM
# until one is measured.
PRINT_RISE_OF_TOP_FACES_MM = 0.05


# Magnets: four supermagnete S-08-03-N (8 x 3) standing on edge, each
# glued against a 0.5 skin at the face, which takes its pull. Its slot
# is a notch through the rest of the block, open at the top and toward
# the cavity: the skin and a 3.0 magnet's printed fit across fill the
# block's 4.0, which leaves no room for a wall on the slot's inner side.
# The slots run from z -0.7 up (0.5 above the bed), between the pins at
# the given centers along the slant: spread evenly between the bosses
# when the slots were 8.2 long (3.14 from each boss and from each
# other), now 2.99 from the bosses and 2.84 apart.
MAGNET_DIAMETER_MM = 8.0
MAGNET_THICKNESS_MM = 3.0
MAGNET_SLOT_ALONG_MM = printed_fit(MAGNET_DIAMETER_MM, SLIP_FIT_MM)
MAGNET_SLOT_ACROSS_MM = printed_fit(MAGNET_THICKNESS_MM, SLIP_FIT_MM)
MAGNET_SLOT_BOTTOM_Z_MM = -0.7
MAGNET_SKIN_MM = 0.5
MAGNET_ALONGS_MM = (14.24, 25.58, 36.92, 48.26)

# Above the block the wall's inner face is cut back to each slot, from
# the block's top to the rim, over the slot's width along the slant: the
# full wall, its inner face TRAY_GAP_MM out, would overhang the slot by
# 0.3, so a magnet could not go straight down into its place against
# the skin.
MAGNET_WALL_CUTBACK_TOP_Z_MM = TRAY_RIM_Z_MM

# Dowel pins: two hardened ISO 8734 4 x 16, normal to the face,
# midway between the bed and the PCB's underside, at the given centers
# along the slant (DESIGN.md: slant y 21.7
# and 74.5, 55.5 apart), 8 embedded in each half, each in a boss 7
# across reaching from the face into the tray past its hole's bottom,
# from the floor up to the PCB's underside like the block. The pins and
# magnets sit at the same places along the slant on both halves, since
# the halves mate face to face. The pins are as far apart as the joint
# face allows: each boss ends where the outline's slant ends (the upper
# one 0.006 short), which keeps it on the face's flat part between the
# tray's corner rounds. At 55.5, where the upper pin first sat, its boss
# overlapped the right half's S150 socket.
DOWEL_PIN_DIAMETER_MM = 4.0
DOWEL_PIN_LENGTH_MM = 16.0
DOWEL_PIN_EMBEDDED_MM = 8.0
DOWEL_PIN_Z_MM = (FLOOR_UNDERSIDE_Z_MM + PCB_UNDERSIDE_Z_MM) / 2.0  # 4.15
DOWEL_PIN_ALONGS_MM = (3.5, 59.0)
DOWEL_BOSS_DIAMETER_MM = 7.0
DOWEL_BOSS_TOP_Z_MM = PCB_UNDERSIDE_Z_MM

# The pin holes are teardrops, their point up since they print
# horizontal, with the point cut flat at the circle's top, so the pin
# bears upward on a bridge instead of on the point's flanks. The left
# half's hold a pin pressed in by hand (snug) and are its stop: as deep
# as the embedded length once the bottom swells, with 1.2 of the boss
# behind. The right half's let it slide (slip), 9.0 deep with 1.0
# behind, so the channel through both halves is 17.2 as modelled (16.8
# printed) for the 16 pin. The right half's mouths get a lead-in
# chamfer, so the pin standing out of the left half finds them. No fit
# has been printed yet.
DOWEL_HOLE_SNUG_DIAMETER_MM = printed_fit(DOWEL_PIN_DIAMETER_MM, SNUG_FIT_MM)  # the left half's
DOWEL_HOLE_SLIP_DIAMETER_MM = printed_fit(DOWEL_PIN_DIAMETER_MM, SLIP_FIT_MM)  # the right half's
DOWEL_HOLE_SNUG_DEPTH_MM = DOWEL_PIN_EMBEDDED_MM + PRINT_SWELLING_PER_SIDE_MM
DOWEL_HOLE_SLIP_DEPTH_MM = 9.0
DOWEL_BOSS_SNUG_BEHIND_HOLE_MM = 1.2
DOWEL_BOSS_SLIP_BEHIND_HOLE_MM = 1.0
DOWEL_HOLE_SLIP_LEAD_IN_MM = 0.3

# Plastic the tray keeps between any two of the joint's voids: the
# dowel holes, the magnet slots and the parking hole.
JOINT_LEAST_PLASTIC_BETWEEN_VOIDS_MM = 1.0


def dowel_hole_diameter(right=False):
    return DOWEL_HOLE_SLIP_DIAMETER_MM if right else DOWEL_HOLE_SNUG_DIAMETER_MM


def dowel_hole_depth(right=False):
    return DOWEL_HOLE_SLIP_DEPTH_MM if right else DOWEL_HOLE_SNUG_DEPTH_MM


def dowel_hole_lead_in(right=False):
    return DOWEL_HOLE_SLIP_LEAD_IN_MM if right else 0.0


def dowel_boss_reach(right=False):
    """How far the half's dowel bosses reach from the face into the
    tray: the hole and the plastic behind it."""
    behind = DOWEL_BOSS_SLIP_BEHIND_HOLE_MM if right else DOWEL_BOSS_SNUG_BEHIND_HOLE_MM
    return dowel_hole_depth(right) + behind


def magnet_slot_outward_range():
    face_side = JOINT_FACE_OUTWARD_MM - MAGNET_SKIN_MM
    return (face_side - MAGNET_SLOT_ACROSS_MM, face_side)


def magnet_slot_polygon(along):
    return slant_rectangle(along, MAGNET_SLOT_ALONG_MM, magnet_slot_outward_range())


def magnet_slot_z_range():
    return (MAGNET_SLOT_BOTTOM_Z_MM, JOINT_BLOCK_TOP_Z_MM)


def magnet_wall_cutback_outward():
    """The wall's inner face over each slot, cut back to the slot's face
    side, so the wall keeps the slot's 0.5 skin there."""
    return magnet_slot_outward_range()[1]


def magnet_slot_opening_outward_range(wall_inner_face_outward):
    """Across the slant, what is open above a slot from the block's top
    to the rim, as far as the slot reaches inward: from the slot's inner
    side to the wall's inner face."""
    inner_side, face_side = magnet_slot_outward_range()
    return (inner_side, min(face_side, wall_inner_face_outward))


def dowel_boss_polygon(along, right=False):
    return slant_rectangle(
        along,
        DOWEL_BOSS_DIAMETER_MM,
        (JOINT_FACE_OUTWARD_MM - dowel_boss_reach(right), JOINT_FACE_OUTWARD_MM),
    )


def dowel_boss_z_range():
    return (0.0, DOWEL_BOSS_TOP_Z_MM)


def dowel_hole_polygon(along, right=False):
    """A dowel hole in plan: its flat top stands right over the circle,
    so it is the hole's diameter wide."""
    return slant_rectangle(
        along,
        dowel_hole_diameter(right),
        (JOINT_FACE_OUTWARD_MM - dowel_hole_depth(right), JOINT_FACE_OUTWARD_MM),
    )


def horizontal_hole_z_range(axis_z, diameter):
    """A flat-topped teardrop hole reaches its radius above and below
    its axis."""
    return (axis_z - diameter / 2.0, axis_z + diameter / 2.0)


def slant_line_crossing_y(along, y):
    """The point with the given y on the line square to the slant at
    `along`."""
    on_slant_x, on_slant_y = slant_point(along, 0.0)
    normal = slant_outward_normal()
    outward = (y - on_slant_y) / normal[1]
    return (on_slant_x + outward * normal[0], y)


def slant_line_crossing_x(along, x):
    """The point with the given x on the line square to the slant at
    `along`."""
    on_slant_x, on_slant_y = slant_point(along, 0.0)
    normal = slant_outward_normal()
    outward = (x - on_slant_x) / normal[0]
    return (x, on_slant_y + outward * normal[1])


def upper_boss_fill_polygon(right=False):
    """The plastic filling the crevice that would open between the upper
    dowel boss's north side, the north ledge's face and the block, out
    to the boss's inner end: a triangle with one side on the boss's
    north side, one on the ledge's face and one running north from the
    boss's inner corner."""
    north_side = max(DOWEL_PIN_ALONGS_MM) + DOWEL_BOSS_DIAMETER_MM / 2.0
    ledge_face_y = SLANT_NORTH_END_MM[1] - ledge_reach()
    inner_corner = slant_point(north_side, JOINT_FACE_OUTWARD_MM - dowel_boss_reach(right))
    return (
        inner_corner,
        slant_line_crossing_y(north_side, ledge_face_y),
        (inner_corner[0], ledge_face_y),
    )


# Pin parking: in split mode each half carries one pin in a teardrop
# hole through the thumb key's short east wall (the outline's east
# edge, x 132.398 up to the slant), running along -x at y 13.1 and
# z 3.4, in a boss under the PCB, the pin's slip fit like the right
# half's dowel holes. The pin goes in 14.5 and a supermagnete S-04-02-N
# (4 x 2) glued at the hole's bottom holds it, so the hole reaches
# 14.5 + 2.0 from the tray's outer face, its last 2.0 the magnet's seat,
# whose glued fit comes to the hole's own diameter. The boss is 7 across
# like the dowel bosses, reaches 1.5 behind the hole's bottom (the
# dowel bosses' plastic around a pin) and stands from the floor to the
# PCB's underside, which rests on it, so it keeps the ledge's clearance
# from the sockets. North of it, up to the lower dowel boss, a fill
# closes the crevice between the two. In plan both are given here up to
# the outline's east edge: the ledge and the wall fill the rest.
THUMB_EAST_EDGE_X_MM = SLANT_SOUTH_END_MM[0]  # the edge ends at the slant
PARKING_HOLE_DIAMETER_MM = printed_fit(DOWEL_PIN_DIAMETER_MM, SLIP_FIT_MM)
PARKING_HOLE_Y_MM = 13.1
PARKING_HOLE_Z_MM = 3.4
PARKING_PIN_INSERTION_MM = 14.5
PARKING_MAGNET_DIAMETER_MM = 4.0
PARKING_MAGNET_THICKNESS_MM = 2.0
PARKING_MAGNET_SEAT_DIAMETER_MM = printed_fit(PARKING_MAGNET_DIAMETER_MM, SLIP_FIT_MM)
PARKING_HOLE_DEPTH_MM = PARKING_PIN_INSERTION_MM + PARKING_MAGNET_THICKNESS_MM
PARKING_BOSS_ACROSS_MM = DOWEL_BOSS_DIAMETER_MM
PARKING_BOSS_BEHIND_HOLE_MM = 1.5
PARKING_BOSS_TOP_Z_MM = PCB_UNDERSIDE_Z_MM


def parking_hole_x_range():
    """From the hole's bottom to the tray's outer face east of the
    thumb."""
    outer_face_x = THUMB_EAST_EDGE_X_MM + TRAY_GAP_MM + TRAY_WALL_MM
    return (outer_face_x - PARKING_HOLE_DEPTH_MM, outer_face_x)


def parking_hole_polygon():
    """The parking hole in plan: its flat top stands right over the
    circle, so it is the hole's diameter wide."""
    low_x, high_x = parking_hole_x_range()
    radius = PARKING_HOLE_DIAMETER_MM / 2.0
    low_y = PARKING_HOLE_Y_MM - radius
    high_y = PARKING_HOLE_Y_MM + radius
    return ((low_x, low_y), (high_x, low_y), (high_x, high_y), (low_x, high_y))


def parking_boss_polygon():
    """The parking hole's boss in plan, up to the outline's east edge."""
    low_x = parking_hole_x_range()[0] - PARKING_BOSS_BEHIND_HOLE_MM
    half_across = PARKING_BOSS_ACROSS_MM / 2.0
    low_y = PARKING_HOLE_Y_MM - half_across
    high_y = PARKING_HOLE_Y_MM + half_across
    return (
        (low_x, low_y),
        (THUMB_EAST_EDGE_X_MM, low_y),
        (THUMB_EAST_EDGE_X_MM, high_y),
        (low_x, high_y),
    )


def parking_boss_fill_polygon():
    """The parking boss's extension north to the lower dowel boss: the
    triangle between the boss's north side, the outline's east edge and
    the dowel boss's south side."""
    boss_north_y = PARKING_HOLE_Y_MM + PARKING_BOSS_ACROSS_MM / 2.0
    south_side = min(DOWEL_PIN_ALONGS_MM) - DOWEL_BOSS_DIAMETER_MM / 2.0
    return (
        slant_line_crossing_y(south_side, boss_north_y),
        (THUMB_EAST_EDGE_X_MM, boss_north_y),
        slant_line_crossing_x(south_side, THUMB_EAST_EDGE_X_MM),
    )


def parking_boss_z_range():
    return (0.0, PARKING_BOSS_TOP_Z_MM)


# Plane geometry on the outline, for the checks and the PCB mock's
# analytic volume.


def polygon_signed_area(polygon):
    """The shoelace area: positive for a counter-clockwise polygon."""
    count = len(polygon)
    return 0.5 * sum(
        polygon[index][0] * polygon[(index + 1) % count][1]
        - polygon[(index + 1) % count][0] * polygon[index][1]
        for index in range(count)
    )


def corner_turn_angles(polygon):
    """Each vertex's turn in radians, walking the counter-clockwise
    polygon: positive at a convex corner, negative at a concave one."""
    count = len(polygon)
    turns = []
    for index in range(count):
        before = polygon[index - 1]
        corner = polygon[index]
        after = polygon[(index + 1) % count]
        incoming = (corner[0] - before[0], corner[1] - before[1])
        outgoing = (after[0] - corner[0], after[1] - corner[1])
        cross = incoming[0] * outgoing[1] - incoming[1] * outgoing[0]
        dot = incoming[0] * outgoing[0] + incoming[1] * outgoing[1]
        turns.append(math.atan2(cross, dot))
    return turns


def line_intersection(point_a, direction_a, point_b, direction_b):
    denominator = direction_a[0] * direction_b[1] - direction_a[1] * direction_b[0]
    if abs(denominator) < 1e-12:
        raise ValueError("parallel lines do not intersect")
    offset = (point_b[0] - point_a[0], point_b[1] - point_a[1])
    parameter = (offset[0] * direction_b[1] - offset[1] * direction_b[0]) / denominator
    return (point_a[0] + parameter * direction_a[0], point_a[1] + parameter * direction_a[1])


def offset_polygon(polygon, distances):
    """The counter-clockwise polygon with its edge i (from vertex i to
    vertex i + 1) moved distances[i] outward (negative inward), corners
    extended to their intersections, like freecad_common's
    offset_outline. A single number moves every edge."""
    count = len(polygon)
    if isinstance(distances, (int, float)):
        distances = (distances,) * count
    lines = []
    for index in range(count):
        start = polygon[index]
        end = polygon[(index + 1) % count]
        length = math.dist(start, end)
        direction = ((end[0] - start[0]) / length, (end[1] - start[1]) / length)
        outward = (direction[1], -direction[0])
        moved_start = (
            start[0] + distances[index] * outward[0],
            start[1] + distances[index] * outward[1],
        )
        lines.append((moved_start, direction))
    return tuple(
        line_intersection(*lines[index - 1], *lines[index]) for index in range(count)
    )


def outline_offset_distances(default_distance, slant_distance):
    """Per-edge offsets of the outline: one for the slant edge, another
    for every other edge."""
    return tuple(
        slant_distance if index == SLANT_EDGE_INDEX else default_distance
        for index in range(len(OUTLINE_VERTICES_MM))
    )


def outline_edge_ends(index):
    """Outline edge `index`'s start and end: vertices index and
    index + 1."""
    count = len(OUTLINE_VERTICES_MM)
    return OUTLINE_VERTICES_MM[index], OUTLINE_VERTICES_MM[(index + 1) % count]


def outline_edge_length(index):
    return math.dist(*outline_edge_ends(index))


def outline_edge_frame(index):
    """(start vertex, direction, outward) of outline edge `index`: unit
    vectors along it and out of the half, on its right since the
    outline runs counter-clockwise."""
    start, end = outline_edge_ends(index)
    length = math.dist(start, end)
    direction = ((end[0] - start[0]) / length, (end[1] - start[1]) / length)
    return start, direction, (direction[1], -direction[0])


def outline_edge_coordinates(point, index):
    """(along, across) of a point in outline edge `index`'s frame: along
    it from its start vertex, across it outward."""
    start, direction, outward = outline_edge_frame(index)
    offset = (point[0] - start[0], point[1] - start[1])
    return (
        offset[0] * direction[0] + offset[1] * direction[1],
        offset[0] * outward[0] + offset[1] * outward[1],
    )


def outline_edge_point(index, along, across):
    """The point at (along, across) in outline edge `index`'s frame."""
    start, direction, outward = outline_edge_frame(index)
    return (
        start[0] + along * direction[0] + across * outward[0],
        start[1] + along * direction[1] + across * outward[1],
    )


def closest_point_on_segment(point, start, end):
    segment = (end[0] - start[0], end[1] - start[1])
    offset = (point[0] - start[0], point[1] - start[1])
    fraction = (offset[0] * segment[0] + offset[1] * segment[1]) / (
        segment[0] ** 2 + segment[1] ** 2
    )
    fraction = max(0.0, min(1.0, fraction))
    return (start[0] + fraction * segment[0], start[1] + fraction * segment[1])


def nearest_outline_edge_index(point):
    return min(
        range(len(OUTLINE_VERTICES_MM)),
        key=lambda index: math.dist(
            point, closest_point_on_segment(point, *outline_edge_ends(index))
        ),
    )


def nearest_polygon_point(point, polygon):
    """(distance, point) to the nearest point of a polygon's boundary."""
    count = len(polygon)
    candidates = [
        closest_point_on_segment(point, polygon[index], polygon[(index + 1) % count])
        for index in range(count)
    ]
    nearest = min(candidates, key=lambda candidate: math.dist(point, candidate))
    return math.dist(point, nearest), nearest


def tray_cavity_polygon():
    """The cavity wall's inner face, sharp-cornered: the outline moved
    out by the gap."""
    return offset_polygon(OUTLINE_VERTICES_MM, TRAY_GAP_MM)


def tray_outer_polygon():
    """The tray's outer face, sharp-cornered: the outline moved out by
    the gap and the wall."""
    return offset_polygon(OUTLINE_VERTICES_MM, TRAY_GAP_MM + TRAY_WALL_MM)


def ledge_inner_polygon():
    """The inner face of the ledge, and of the joint block along the
    slant, sharp-cornered."""
    return offset_polygon(
        OUTLINE_VERTICES_MM,
        outline_offset_distances(
            TRAY_GAP_MM - TRAY_LEDGE_WIDTH_MM,
            JOINT_FACE_OUTWARD_MM - JOINT_BLOCK_THICKNESS_MM,
        ),
    )


def west_ledge_face_x():
    """The west ledge's inner face, which locates the nice!nano's west
    edge."""
    return min(x for x, _ in OUTLINE_VERTICES_MM) + ledge_reach()


# The parts' mounts (DESIGN.md, "Parts in the tray", and work item 004).
# Everything the tray adds to hold a part, and every void it cuts for
# one, is an axis-aligned box in the left half's frame (MountBox), so
# check_layout.py checks the mounts the way it checks the parts. Two
# shapes are not boxes and lie inside theirs: the USB window with its
# rounded corners and outer chamfer, and the reset pin hole, a
# flat-topped teardrop. The nice!nano's clamp block is bored for its
# insert like a standoff, the bore no box of its own, and the standoff
# that the block, the foot and the east wall merge
# (NANO_MERGED_STANDOFF_MM) keeps its own bore: tray_shape.py builds no
# body into a standoff's bore. The clamp's tab and screw head are no
# part of the tray, but check_layout.py checks them with the mount
# bodies (nano_clamp_part_boxes()). The right tray is built in the left
# half's frame and mirrored (the module docstring), which is right for a
# mount wherever its part maps onto itself under that mirror or lies
# mirrored on the right half. DESIGN.md, "Mirroring", works that out for
# each part, and every mount mirrors rightly. Only the wire room over
# the nice!nano's P1.01/P1.02/P1.07 pads takes the half
# (nano_wire_rooms()).
#
# Every printed fit is printed_fit(): a pocket or slot as the part plus
# the print's swelling on both sides plus the fit's clearance, so it
# prints as the part plus the clearance. A fit split over two ends gives
# each end half the difference.


@dataclass(frozen=True)
class MountBox:
    """A box the tray adds (a mount body) or cuts (a mount void): in plan
    x_range by y_range, over z_range. `part` is the part it serves."""

    label: str
    part: str
    x_range: tuple
    y_range: tuple
    z_range: tuple


def centered_range(middle, width):
    return (middle - width / 2.0, middle + width / 2.0)


def grown_range(value_range, by):
    return (value_range[0] - by, value_range[1] + by)


def half_fit_gap(nominal, fit):
    """What a printed fit adds at each of its two ends."""
    return (printed_fit(nominal, fit) - nominal) / 2.0


# The nice!nano's figures the mounts rest on. The width and the length
# are the user's caliper (NANO_WIDTH_MM and NANO_LENGTH_MM, with
# NANO_BOARD). The underside is flat with nothing below it (the user,
# doc/log/2026-10-19.md). The pads are the render's (doc/components.md,
# +-0.1), measured on its 18.0 wide board from the long edges: two pin
# rows of 12 at 2.54 pitch, pin 1 3.91 from the USB end, the rows'
# centers 1.31 and 1.44 in from the long edges (which is which the
# render leaves open, so a wire room covers both), pads 1.53 across, the
# B+ and B- pads 1.14 across in line with the rows 1.38 from the USB
# end, the P1.01, P1.02 and P1.07 pads in a row across the board 26.8
# from the USB end, 2.54, 5.08 and 7.62 from the B- row (taken as the
# pin pads' size). Seen from above with the USB end north, B- is on the
# west (the render's top view), and so are the P1 pads, on both halves,
# since the right half's nano is the same part the same side up.
NANO_PIN_PITCH_MM = 2.54
NANO_PINS_PER_ROW = 12
NANO_PIN_1_FROM_USB_END_MM = 3.91
NANO_ROW_INSETS_MM = (1.31, 1.44)
NANO_PIN_PAD_DIAMETER_MM = 1.53
NANO_BATTERY_PADS_FROM_USB_END_MM = 1.38
NANO_BATTERY_PAD_DIAMETER_MM = 1.14
NANO_EXTRA_PADS_FROM_USB_END_MM = 26.8
NANO_EXTRA_PADS_FROM_B_MINUS_ROW_MM = (2.54, 5.08, 7.62)

# The mounts' figures that wait on a caliper or the parts in hand (work
# item 004). export_tray.py's key=value words override them for a test
# print: the nano's length and width, the pocket's fit across the board
# (the nice!nano test bay's export can step it over several bays, work
# item 010), the clamp's press on the board and the bar's clearance
# over the shell (work items 006 and 009), and the battery header's
# front lips (none by default, DESIGN.md says why). The pocket's fit
# is a slip fit at the least: the board lies 0.3 from the west ledge's
# face, 0.1 from it as printed, so at the slip fit the east wall's inner
# face as printed meets the board's east edge, where a snug pocket's
# would come 0.1 inside the board. The user calipered the slip fit
# pocket of the first heavy duty test bay (work item 010) against the
# print model's 18.4 for the 18.30 board it was fitted to: "The bay
# inside width is 18.41~18.46. The nano width is 18.17~18.23 mm"
# (2026-10-20).
NANO_POCKET_FIT_MM = SLIP_FIT_MM
NANO_CLAMP_PRESS_MM = 0.1  # as printed
NANO_BAR_CLEARANCE_MM = 0.1
BATTERY_HEADER_SHOULDER_MM = 0.0


@dataclass(frozen=True)
class MountFits:
    nano_length: float = NANO_LENGTH_MM
    nano_width: float = NANO_WIDTH_MM
    nano_pocket_fit: float = NANO_POCKET_FIT_MM
    clamp_press: float = NANO_CLAMP_PRESS_MM
    bar_clearance: float = NANO_BAR_CLEARANCE_MM
    battery_shoulder: float = BATTERY_HEADER_SHOULDER_MM


DEFAULT_MOUNT_FITS = MountFits()


def nano_usb_end_y():
    """The board's USB end, which stays put: the shell's mouth sits 0.5
    behind the north wall's outer face whatever the board's length."""
    return NANO_BOARD.y_range[1]


def nano_south_end_y(fits):
    return nano_usb_end_y() - fits.nano_length


def nano_west_x():
    """The board's west edge, 0.3 from the west ledge's face whatever
    its width."""
    return NANO_BOARD.x_range[0]


def nano_east_x(fits):
    return nano_west_x() + fits.nano_width


def nano_center_x(fits):
    """The board's center line, which the USB shell is centered on."""
    return nano_west_x() + fits.nano_width / 2.0


# The pocket along the board, from the clamp foot's face to the north
# block's. The user calipered the first heavy duty test bay (work item
# 010), whose end faces stood 33.8 apart as modelled, 33.4 by the print
# model: "Board length 33.20, bay inside length 33.54" (2026-10-20). So
# these two faces swelled 33.8 - 33.54 = 0.26 together, not the print
# model's 0.4, while across the print model held (18.8 modelled, 18.4 by
# the model, 18.41 to 18.46 calipered). Only that sum was calipered
# (NANO_POCKET_END_FACES_SWELLING_MM). The pocket is sized for 0.13 on
# each face, but how the sum really splits is not known, so the stops
# as printed take the north block's share of it, and check_layout.py
# takes every figure that depends on the split at its worst, all of
# the sum on either face. Why the faces swell less is not known
# either: they are short faces, the reading is a caliper's on a
# printed part, or both. The pocket is the board's slip fit along with
# that swelling, so its end faces stand the board's length and the
# slip fit's 0.1 apart as printed however the sum splits. The north
# block stays where it stood, the print model's slip fit gap north of
# the board's USB end, so the shell's mouth stays put, and the foot's
# face follows the pocket's length.
NANO_POCKET_END_FACES_SWELLING_MM = 0.26
NANO_POCKET_END_FACE_SWELLING_MM = NANO_POCKET_END_FACES_SWELLING_MM / 2.0


def nano_north_end_gap(fits):
    """The gap between the board's USB end and the north block's face as
    modelled: the print model's half of a slip fit's gap, where the block
    stood when the test bay was calipered."""
    return half_fit_gap(fits.nano_length, SLIP_FIT_MM)


def nano_pocket_length(fits=DEFAULT_MOUNT_FITS):
    """The foot's face to the north block's as modelled."""
    return fits.nano_length + 2.0 * NANO_POCKET_END_FACE_SWELLING_MM + SLIP_FIT_MM


def nano_north_stop_y_as_printed(fits=DEFAULT_MOUNT_FITS,
                                 block_swelling=NANO_POCKET_END_FACE_SWELLING_MM):
    """The north block's face as printed, the board's north stop, the
    face swollen by block_swelling, its share of the end faces' sum."""
    return nano_north_block_south_y(fits) - block_swelling


def nano_south_stop_y_as_printed(fits=DEFAULT_MOUNT_FITS,
                                 block_swelling=NANO_POCKET_END_FACE_SWELLING_MM):
    """The foot's face as printed, the board's south stop, the face
    swollen by what the north block's share, block_swelling, leaves of
    the end faces' sum."""
    return nano_clamp_stop_y(fits) + NANO_POCKET_END_FACES_SWELLING_MM - block_swelling


def nano_board_envelope(fits=DEFAULT_MOUNT_FITS):
    """NANO_BOARD as the fits size it, its west edge and USB end staying
    put."""
    return replace(
        NANO_BOARD,
        x_range=(nano_west_x(), nano_east_x(fits)),
        y_range=(nano_south_end_y(fits), nano_usb_end_y()),
    )


def nano_usb_shell_envelope(fits=DEFAULT_MOUNT_FITS):
    """NANO_USB_SHELL centered on the board the fits size."""
    return replace(
        NANO_USB_SHELL, x_range=centered_range(nano_center_x(fits), NANO_USB_SHELL_WIDTH_MM)
    )


def part_envelopes(fits=DEFAULT_MOUNT_FITS):
    """PART_ENVELOPES with the nice!nano's board and shell as the fits
    size them, which is where the mounts hold them, and the nice!nano's
    socket strips and their tails on that board."""
    sized = {NANO_BOARD: nano_board_envelope(fits), NANO_USB_SHELL: nano_usb_shell_envelope(fits)}
    return (tuple(sized.get(envelope, envelope) for envelope in PART_ENVELOPES)
            + nano_strip_envelopes(fits) + nano_tail_envelopes(fits))


def nano_ledge_cutaway(fits=DEFAULT_MOUNT_FITS):
    """The north ledge's cut-away over the board the fits size."""
    return ledge_cutaway(
        "nice!nano", nano_board_envelope(fits).x_range, NORTH_EDGE_Y_OF_COLUMNS_0_AND_1_MM
    )


def ledge_cutaways(fits=DEFAULT_MOUNT_FITS):
    """Every ledge cut-away, the nice!nano's over the board the fits
    size."""
    return (nano_ledge_cutaway(fits),) + SWITCH_AND_BUTTON_LEDGE_CUTAWAYS


# The USB window: kbdkid4's (model/kbdkid4/scripts/export_tray.py,
# USB_WINDOW_WIDTH_MM, USB_WINDOW_CORNER_RADIUS_MM and
# USB_WINDOW_CHAMFER_MM, and model/kbdkid4/scripts/tray_shape.py,
# USB_WINDOW_HEIGHT_MM, measured there on the soldered left half),
# centered on the shell. It
# opens the wall from the shell's mouth out, as far in as the plug's
# overmold goes, its chamfer on the wall's outer face only. Between the
# cavity face and the mouth the wall stands on over and beside the
# shell, which passes it in a channel of its own: the shell's section as
# a slip fit (the north block's opening across, up to the bar's
# underside), run on past the mouth as far as the board's play north
# and the print's swelling take it (nano_usb_channel_past_mouth()). So
# the wall
# carries the north block's bar and sides on to the mouth, and wherever
# they let the shell go, the window's corner rounds stay clear of it as
# printed.
USB_WINDOW_WIDTH_MM = 10.5
USB_WINDOW_HEIGHT_MM = 4.5
USB_WINDOW_CORNER_RADIUS_MM = 1.95
USB_WINDOW_CHAMFER_MM = 0.2


def usb_window_center(fits=DEFAULT_MOUNT_FITS):
    """(x, z) of the window's middle: the shell's."""
    return (nano_center_x(fits), sum(NANO_USB_SHELL.z_range) / 2.0)


def nano_usb_shell_mouth_y():
    return NANO_USB_SHELL.y_range[1]


def usb_window_box(fits=DEFAULT_MOUNT_FITS):
    x, z = usb_window_center(fits)
    return MountBox(
        "USB window",
        "nice!nano",
        centered_range(x, USB_WINDOW_WIDTH_MM),
        (nano_usb_shell_mouth_y(), outer_face_y(NORTH_EDGE_Y_OF_COLUMNS_0_AND_1_MM)),
        centered_range(z, USB_WINDOW_HEIGHT_MM),
    )


def usb_shell_channel_box(fits=DEFAULT_MOUNT_FITS):
    return MountBox(
        "USB shell's channel",
        "nice!nano",
        centered_range(nano_center_x(fits), nano_bar_opening()),
        (
            cavity_wall_y(NORTH_EDGE_Y_OF_COLUMNS_0_AND_1_MM),
            nano_usb_shell_mouth_y() + nano_usb_channel_past_mouth(fits),
        ),
        (NANO_USB_SHELL.z_range[0], nano_bar_underside_z(fits)),
    )


def nano_usb_channel_past_mouth(fits=DEFAULT_MOUNT_FITS):
    """How far the shell's channel runs on past the shell's mouth: the
    board's play north, to the north block's face as printed, and the
    print's swelling of the channel's end, so the mouth stays inside the
    channel as printed."""
    play_north = nano_north_stop_y_as_printed(fits) - nano_usb_end_y()
    return play_north + PRINT_SWELLING_PER_SIDE_MM


def usb_opening_boxes(fits=DEFAULT_MOUNT_FITS):
    """The shell's channel and the window, from the cavity out."""
    return (usb_shell_channel_box(fits), usb_window_box(fits))


# The north block, one block across the pocket against the north wall's
# inner face, between the board's USB end and the wall (work item 010,
# the user: "make the cradle more of a heavy duty pocket in an
# extrusion"). It reaches over the ledge cut-away's whole width, so it
# merges with the ledge at both ends, and from the floor to the bar's
# top. Its south face, nano_north_end_gap() north of the board's USB
# end, is the board's north stop. The shell passes it in an opening of its own, the
# shell's slip fit across (the shell plus 0.5), from the board's seat up
# to the bar's underside, bar_clearance over the shell's top as printed,
# which the shell's channel continues through the wall (the USB window's
# comment). So the block is four boxes: its sides beside the opening,
# the sill under it, as high as the seat, and the bar over it, which
# holds the shell down and is over nothing but the shell, B+ and B-
# included. The block is no deeper than the
# old bar: the board goes in nose first, its shell into the opening,
# and its south end comes down with its USB end against the block
# (check_layout.py's insertion check).
NANO_BAR_HEIGHT_MM = 1.5


def nano_bar_opening():
    return printed_fit(NANO_USB_SHELL_WIDTH_MM, SLIP_FIT_MM)


def nano_bar_underside_z(fits=DEFAULT_MOUNT_FITS):
    return NANO_USB_SHELL.z_range[1] + PRINT_SWELLING_PER_SIDE_MM + fits.bar_clearance


def nano_north_block_south_y(fits=DEFAULT_MOUNT_FITS):
    return nano_usb_end_y() + nano_north_end_gap(fits)


def nano_bar_depth(fits=DEFAULT_MOUNT_FITS):
    """The bar's depth over the shell, from the block's south face to
    the shell's mouth, where the window opens."""
    return nano_usb_shell_mouth_y() - nano_north_block_south_y(fits)


def nano_north_block_boxes(fits=DEFAULT_MOUNT_FITS):
    """The block's west and east sides, from the floor to the bar's top,
    the sill under the opening between them, from the floor to the seat,
    and the bar over the opening."""
    low_x, high_x = nano_ledge_cutaway(fits).x_range
    opening = centered_range(nano_center_x(fits), nano_bar_opening())
    y_range = (nano_north_block_south_y(fits), cavity_wall_y(NORTH_EDGE_Y_OF_COLUMNS_0_AND_1_MM))
    underside = nano_bar_underside_z(fits)
    top = underside + NANO_BAR_HEIGHT_MM
    return (
        MountBox("north block's west side", "nice!nano", (low_x, opening[0]), y_range, (0.0, top)),
        MountBox("north block's east side", "nice!nano", (opening[1], high_x), y_range, (0.0, top)),
        MountBox("north block's sill", "nice!nano", opening, y_range, (0.0, NANO_SEAT_HEIGHT_MM)),
        MountBox("north block's bar", "nice!nano", opening, y_range, (underside, top)),
    )


# The screw clamp at the board's south end (work items 009 and 010): a
# tab of its own print over the board's south edge, pulled down by an M2
# screw into an M2 heat-set insert in the clamp block south of the
# board. Nothing flexes in the tray, and its floor stays closed. The
# block runs across the pocket from the west ledge's face on to the east
# wall's outer face, NANO_CLAMP_BLOCK_DEPTH_MM along y, so it takes in
# the standoff at NANO_MERGED_STANDOFF_MM with the foot and the east
# wall, and is bored for the insert on the board's center line down to
# the floor's top, like the standoffs, the floor's thickness under it.
# A foot up to the board's top runs on north from it across the pocket
# to the pocket's length south of the north block's face
# (nano_pocket_length()): its north face is the board's south stop,
# which a board pushed south (a USB-C plug going in) meets over all of
# its width but the 5.0 the pry slot takes out of the foot's face (the
# user: "Could you increase its height so it it at least as high as the
# nano board itself?", work item 010).
# The block stands with the screw NANO_CLAMP_SCREW_FROM_BOARD_END_MM
# from the board's south end, so the head keeps clear of the socket
# over the board's end in plan and the tab's arm is long enough to bend.
#
# The tab is a plate on the block's top reaching NANO_CLAMP_TAB_REACH_MM
# onto the board, with a nose NANO_CLAMP_NOSE_LENGTH_MM long under that
# end, NANO_CLAMP_NOSE_DEPTH_MM below the plate's underside. The nose
# starts far enough onto the board that its south face clears the
# foot's as printed, both swollen toward each other (check_layout.py).
# The block's top lies the fits' clamp_press under where the plate's
# underside would be with the nose on the board's top, so tightening the
# screw bends the tab's arm, from the head's edge to the nose's south
# face, where the board pushes it up, up by the press, which is how hard
# it holds the board down. The block's top and the seat's top, which the
# board rests on, face up in the same print and rise together, and so do
# the plate's underside and the nose's bottom, the tab printed top face
# down, so the press prints as modelled. The tab is the same for every
# press, which the block's top sets. Its plan is symmetric about the
# board's center line, so the right half takes the same tab.
NANO_CLAMP_TAB_WIDTH_MM = STANDOFF_DIAMETER_MM  # along x, the boss's it came with
NANO_CLAMP_BLOCK_DEPTH_MM = STANDOFF_DIAMETER_MM  # along y, the boss's it replaces
NANO_CLAMP_SCREW_FROM_BOARD_END_MM = 6.5
NANO_CLAMP_FOOT_HEIGHT_MM = NANO_BOARD.z_range[1]  # as tall as the board
NANO_CLAMP_TAB_THICKNESS_MM = 1.0
NANO_CLAMP_TAB_REACH_MM = 1.5  # onto the board
NANO_CLAMP_NOSE_LENGTH_MM = 1.0  # along y, at the tab's north end
NANO_CLAMP_NOSE_DEPTH_MM = 2.1  # below the plate's underside
NANO_CLAMP_BORE_DIAMETER_MM = STANDOFF_BORE_DIAMETER_MM  # an M2 heat-set insert's, the standoffs'
NANO_CLAMP_INSERT_LENGTH_MM = 3.0  # M2 x 3
NANO_CLAMP_SCREW_LENGTH_MM = 4.0  # M2 x 4, under the head
# The screw's head: kbdkid4's measured diameter (plate_shape.py's
# SCREW_HEAD_DIAMETER_MM) and, unmeasured, the largest height ISO 4762
# gives an M2 socket head. The tab's hole is the PCB's mounting drill's
# printed fit, 2.4 as printed.
NANO_CLAMP_SCREW_HEAD_DIAMETER_MM = 3.77
NANO_CLAMP_SCREW_HEAD_HEIGHT_MM = 2.0
NANO_CLAMP_SCREW_HOLE_DIAMETER_MM = printed_fit(MOUNTING_DRILL_DIAMETER_MM, SNUG_FIT_MM)
# The standoff the clamp block, the foot and the east wall take in
# (DESIGN.md, Mounting: moved there out from under the nice!nano).
NANO_MERGED_STANDOFF_MM = MOUNTING_DRILL_CENTERS_MM[1]


def nano_clamp_tab_x_range(fits=DEFAULT_MOUNT_FITS):
    return centered_range(nano_center_x(fits), NANO_CLAMP_TAB_WIDTH_MM)


def nano_clamp_stop_y(fits=DEFAULT_MOUNT_FITS):
    """The foot's north face, the board's south stop, the pocket's length
    south of the north block's face."""
    return nano_north_block_south_y(fits) - nano_pocket_length(fits)


def nano_clamp_screw_center(fits=DEFAULT_MOUNT_FITS):
    """(x, y) of the screw's axis, the bore's and the tab's hole's."""
    return (nano_center_x(fits), nano_south_end_y(fits) - NANO_CLAMP_SCREW_FROM_BOARD_END_MM)


def nano_clamp_block_top_z(fits=DEFAULT_MOUNT_FITS):
    return NANO_BOARD.z_range[1] + NANO_CLAMP_NOSE_DEPTH_MM - fits.clamp_press


def nano_clamp_boxes(fits=DEFAULT_MOUNT_FITS):
    """The block, from the west ledge's face to the east wall's outer
    face about the screw's axis, and the foot, from the block on to the
    stop across the pocket."""
    block_y = centered_range(nano_clamp_screw_center(fits)[1], NANO_CLAMP_BLOCK_DEPTH_MM)
    west = west_ledge_face_x()
    return (
        MountBox("clamp's block", "nice!nano", (west, nano_east_wall_outer_x()), block_y,
                 (0.0, nano_clamp_block_top_z(fits))),
        MountBox("clamp's foot", "nice!nano", (west, nano_pocket_east_x(fits)),
                 (block_y[1], nano_clamp_stop_y(fits)), (0.0, NANO_CLAMP_FOOT_HEIGHT_MM)),
    )


def nano_clamp_insert_room(fits=DEFAULT_MOUNT_FITS):
    """The bore's depth under the block's top as printed, its bottom,
    which faces up, counted higher."""
    return nano_clamp_block_top_z(fits) - PRINT_RISE_OF_UP_FACING_BOTTOMS_MM


def nano_clamp_tab_thickness(printed=True):
    """The plate's thickness: its underside faces up as printed."""
    return NANO_CLAMP_TAB_THICKNESS_MM + (PRINT_RISE_OF_UP_FACING_BOTTOMS_MM if printed else 0.0)


def nano_clamp_tab_y_range(fits=DEFAULT_MOUNT_FITS):
    """From the block's south face to the tab's reach onto the board."""
    south = nano_clamp_boxes(fits)[0].y_range[0]
    return (south, nano_south_end_y(fits) + NANO_CLAMP_TAB_REACH_MM)


def nano_clamp_nose_y_range(fits=DEFAULT_MOUNT_FITS):
    north = nano_clamp_tab_y_range(fits)[1]
    return (north - NANO_CLAMP_NOSE_LENGTH_MM, north)


def nano_clamp_tab_boxes(fits=DEFAULT_MOUNT_FITS):
    """The tab as modelled, seated on the block's top: its plate and its
    nose, which reaches the press below the board's top."""
    x_range = nano_clamp_tab_x_range(fits)
    top = nano_clamp_block_top_z(fits)
    return (
        MountBox("clamp tab's plate", "nice!nano", x_range, nano_clamp_tab_y_range(fits),
                 (top, top + NANO_CLAMP_TAB_THICKNESS_MM)),
        MountBox("clamp tab's nose", "nice!nano", x_range, nano_clamp_nose_y_range(fits),
                 (top - NANO_CLAMP_NOSE_DEPTH_MM, top)),
    )


def nano_clamp_part_boxes(fits=DEFAULT_MOUNT_FITS):
    """The tab and the screw's head where they sit with the tab on the
    board, which bends its arm up by the press: the plate from the
    block's top to its top as printed, the press over it, the nose from
    the board's top to the plate, and the head, its bounding box, on the
    plate as printed, which the screw holds on the block's top."""
    x_range = nano_clamp_tab_x_range(fits)
    top = nano_clamp_block_top_z(fits)
    board_top = NANO_BOARD.z_range[1]
    nose_top = board_top + NANO_CLAMP_NOSE_DEPTH_MM
    head_bottom = top + nano_clamp_tab_thickness()
    x, y = nano_clamp_screw_center(fits)
    return (
        MountBox("clamp tab's plate", "nice!nano", x_range, nano_clamp_tab_y_range(fits),
                 (top, nose_top + nano_clamp_tab_thickness())),
        MountBox("clamp tab's nose", "nice!nano", x_range, nano_clamp_nose_y_range(fits),
                 (board_top, nose_top)),
        MountBox("clamp screw's head", "nice!nano",
                 centered_range(x, NANO_CLAMP_SCREW_HEAD_DIAMETER_MM),
                 centered_range(y, NANO_CLAMP_SCREW_HEAD_DIAMETER_MM),
                 (head_bottom, head_bottom + NANO_CLAMP_SCREW_HEAD_HEIGHT_MM)),
    )


def nano_clamp_arm_length():
    """The tab's arm that bends, from the head's edge, where the screw
    holds the plate on the block, to the nose's south face, where the
    board pushes the arm up as it bends."""
    nose_south_from_screw = (NANO_CLAMP_SCREW_FROM_BOARD_END_MM + NANO_CLAMP_TAB_REACH_MM
                             - NANO_CLAMP_NOSE_LENGTH_MM)
    return nose_south_from_screw - NANO_CLAMP_SCREW_HEAD_DIAMETER_MM / 2.0


def nano_clamp_strain(fits=DEFAULT_MOUNT_FITS, printed=True):
    """The arm's bending strain at the head's edge, bent up by the press
    at the nose's south face."""
    return cantilever_strain(
        fits.clamp_press, nano_clamp_tab_thickness(printed), nano_clamp_arm_length()
    )


def nano_clamp_screw_reach(fits=DEFAULT_MOUNT_FITS):
    """How far the screw reaches into the bore below the block's top."""
    return NANO_CLAMP_SCREW_LENGTH_MM - nano_clamp_tab_thickness()


def cantilever_strain(deflection, thickness, length):
    """The root's bending strain of a cantilever deflected at `length`
    from its root by a point load there: 3 deflection thickness / (2
    length squared)."""
    return 3.0 * deflection * thickness / (2.0 * length**2)


def nano_free_middle_x_range(fits=DEFAULT_MOUNT_FITS):
    """The middle of the board's far end, between the last pins' pads of
    both rows, at the larger of the render's row insets."""
    clear = max(NANO_ROW_INSETS_MM) + NANO_PIN_PAD_DIAMETER_MM / 2.0
    return (nano_west_x() + clear, nano_east_x(fits) - clear)


# The east wall along the board's east edge (work item 010, the user:
# "Make them tall, thick walls that really cover the nano"): from the
# pocket's east face, the board's width as the pocket's fit from the
# west ledge's face, to the battery's northwest rib's inner face, so
# that rib merges into it, NANO_EAST_WALL_ABOVE_BOARD_MM over the
# board's top (the 4.0 tall wall the user accepted with the board on
# the floor, doc/log/2026-10-19.md), from the clamp's block north to
# where its north face as printed meets the PCB connector's zone, which
# keeps tray features out above the floor. North of that the board's
# east edge has no wall. Over the board's top its inner part is cut
# back for the east socket strip (nano_strip_pocket_x_range()), so the
# wall is three boxes: its outer part beyond the strip's pocket at full
# height, its inner part up to the board's top, which locates the
# board's east edge, and its inner part south of the strip's pocket at
# full height.
NANO_EAST_WALL_ABOVE_BOARD_MM = 2.4


def nano_pocket_east_x(fits=DEFAULT_MOUNT_FITS):
    """The pocket's east face, the east wall's inner face."""
    return west_ledge_face_x() + printed_fit(fits.nano_width, fits.nano_pocket_fit)


def nano_east_wall_top_z():
    return NANO_BOARD.z_range[1] + NANO_EAST_WALL_ABOVE_BOARD_MM


def nano_east_wall_outer_x():
    """The east wall's outer face, the battery's northwest rib's inner
    face."""
    return battery_rib_pocket()[0][0]


def nano_east_wall_boxes(fits=DEFAULT_MOUNT_FITS):
    """The wall's outer part, its inner part under the strip's pocket's
    floor the wall's whole length and its inner part over that floor
    south of the pocket. The inner boxes do not overlap, so neither
    shares with the other the standoff both reach."""
    inner = nano_pocket_east_x(fits)
    pocket_face = nano_strip_pocket_x_range(fits)[1]
    pocket_south = nano_strip_pocket_y_range()[0]
    south = nano_clamp_boxes(fits)[0].y_range[1]
    north = PCB_CONNECTOR_CLEAR_ZONE.y_range[0] - PRINT_SWELLING_PER_SIDE_MM
    top = nano_east_wall_top_z()
    return (
        MountBox("east wall", "nice!nano", (pocket_face, nano_east_wall_outer_x()),
                 (south, north), (0.0, top)),
        MountBox("east wall under the strip's pocket", "nice!nano", (inner, pocket_face),
                 (south, north), (0.0, NANO_BOARD.z_range[1])),
        MountBox("east wall south of the strip's pocket", "nice!nano", (inner, pocket_face),
                 (south, pocket_south), (NANO_BOARD.z_range[1], top)),
    )


# The pads' and pins' extents, which the seat's channels under the board,
# the socket strips over it and the wire rooms over the battery and
# P1 pads cover (nano_seat_x_range(), nano_strip_envelopes(),
# nano_wire_rooms()).


def nano_row_axis_x_range(fits, west):
    """A pin row's pins' axes across x, at either of the render's
    insets."""
    near, far = min(NANO_ROW_INSETS_MM), max(NANO_ROW_INSETS_MM)
    if west:
        return (nano_west_x() + near, nano_west_x() + far)
    return (nano_east_x(fits) - far, nano_east_x(fits) - near)


def nano_row_x_range(fits, west):
    """A pin row's pads across x, at either of the render's insets."""
    return grown_range(nano_row_axis_x_range(fits, west), NANO_PIN_PAD_DIAMETER_MM / 2.0)


def nano_pin_y(number):
    """The y of pin `number` of either row, pin 1 nearest the USB end."""
    return nano_usb_end_y() - NANO_PIN_1_FROM_USB_END_MM - (number - 1) * NANO_PIN_PITCH_MM


def nano_pins_y_range():
    """From the last pin's axis to pin 1's."""
    return (nano_pin_y(NANO_PINS_PER_ROW), nano_pin_y(1))


def nano_battery_pad_x_range(fits, west):
    """The B+ or B- pad across x, in line with its row, at either of the
    render's insets."""
    return grown_range(nano_row_axis_x_range(fits, west), NANO_BATTERY_PAD_DIAMETER_MM / 2.0)


def nano_battery_pads_y_range():
    return centered_range(nano_usb_end_y() - NANO_BATTERY_PADS_FROM_USB_END_MM,
                          NANO_BATTERY_PAD_DIAMETER_MM)


def nano_extra_pads_x_range(fits=DEFAULT_MOUNT_FITS, right=False):
    """The P1.01/P1.02/P1.07 pads across x, on the B- row's side: the
    west on the left half and, in the left half's frame, the east on the
    right one (the comment on the nice!nano's figures)."""
    pad = NANO_PIN_PAD_DIAMETER_MM / 2.0
    near_inset, far_inset = min(NANO_ROW_INSETS_MM), max(NANO_ROW_INSETS_MM)
    nearest = min(NANO_EXTRA_PADS_FROM_B_MINUS_ROW_MM)
    farthest = max(NANO_EXTRA_PADS_FROM_B_MINUS_ROW_MM)
    if not right:
        west = nano_west_x()
        return (west + near_inset + nearest - pad, west + far_inset + farthest + pad)
    east = nano_east_x(fits)
    return (east - far_inset - farthest - pad, east - near_inset - nearest + pad)


def nano_extra_pads_y_range():
    return centered_range(
        nano_usb_end_y() - NANO_EXTRA_PADS_FROM_USB_END_MM, NANO_PIN_PAD_DIAMETER_MM
    )


# The socket strips on the board's top (the user, 2026-10-20: "I want
# to solder 2 x 12 pin low profile socket strips on top of the nano so I
# don't have to solder wires directly to it. I've ordered "Mill Max
# 315-43-112-41-003000""): one over each row's pins 1 to 12, "only the
# 12 southmost pins will get the socket strips", which leaves B+ and B-
# free, as nicekeyboards asks ("Do not install sockets or post headers
# to the B+ or B- pins", doc/components.md). Mill-Max's datasheet and
# catalog page 65 (work/research/downloads/millmax-315-43-112-41-003000/):
# the insulator is the pins times .100" long and .100" wide, centered on
# the pins, its top .095" (2.413) over the board's top and itself .071"
# (1.803) tall, so it stands 0.61 clear of the board on the sleeves
# under it (Fig. 4), the solder tails .030" (0.762) across and .095"
# (2.413) long below the seating plane, the board's top, so 0.813 below
# the underside of the 1.6 board. Its tolerances: the length +-.005"
# (0.127), the insulator's width +-.005" (0.13), the pins' length
# +-.005" (0.13), assembly +-.010" (0.25), and the insulator's height
# +-.005" (0.13), which is not modelled: 0.13 taller under the same
# top, it would stand 0.43 over the clamp's foot as printed, still
# clear. A strip is two envelopes.
# The insulator is its worst case in plan: at either of the render's
# row insets, its length and width tolerances split over both ends and
# sides, the assembly tolerance on every side. The sleeves stand on the
# pins' pads at either inset, since the drawing gives no sleeve
# diameter. Their heights are the datasheet's. A tail's envelope is the
# row's tails at either inset, down to the longest pin's tip.
NANO_STRIP_WIDTH_MM = 2.54
NANO_STRIP_HEIGHT_MM = 2.413  # over the board's top
NANO_STRIP_INSULATOR_HEIGHT_MM = 1.803
NANO_STRIP_TAIL_DIAMETER_MM = 0.762
NANO_STRIP_TAIL_LENGTH_MM = 2.413  # below the board's top
NANO_STRIP_LENGTH_TOLERANCE_MM = 0.127
NANO_STRIP_WIDTH_TOLERANCE_MM = 0.13
NANO_STRIP_PIN_LENGTH_TOLERANCE_MM = 0.13
NANO_STRIP_ASSEMBLY_TOLERANCE_MM = 0.25


def nano_strip_y_range():
    """The insulator, a pitch per pin long, centered on the pins."""
    length = (NANO_PINS_PER_ROW * NANO_PIN_PITCH_MM + NANO_STRIP_LENGTH_TOLERANCE_MM
              + 2.0 * NANO_STRIP_ASSEMBLY_TOLERANCE_MM)
    return centered_range(sum(nano_pins_y_range()) / 2.0, length)


def nano_strip_x_range(fits, west):
    half_width = (NANO_STRIP_WIDTH_MM / 2.0 + NANO_STRIP_WIDTH_TOLERANCE_MM / 2.0
                  + NANO_STRIP_ASSEMBLY_TOLERANCE_MM)
    return grown_range(nano_row_axis_x_range(fits, west), half_width)


def nano_strip_insulator_bottom_z(fits=DEFAULT_MOUNT_FITS):
    return (nano_board_envelope(fits).z_range[1] + NANO_STRIP_HEIGHT_MM
            - NANO_STRIP_INSULATOR_HEIGHT_MM)


def nano_strip_insulators(fits=DEFAULT_MOUNT_FITS):
    """The west and the east strip's insulator, over its sleeves."""
    top = nano_board_envelope(fits).z_range[1] + NANO_STRIP_HEIGHT_MM
    return tuple(
        Envelope("nice!nano", f"{side} socket strip's insulator",
                 nano_strip_x_range(fits, side == "west"), nano_strip_y_range(),
                 (nano_strip_insulator_bottom_z(fits), top), CAVITY)
        for side in ("west", "east")
    )


def nano_strip_sleeves(fits=DEFAULT_MOUNT_FITS):
    """The west and the east strip's sleeves, from the board's top up to
    the insulator, on the pins' pads."""
    top = nano_board_envelope(fits).z_range[1]
    return tuple(
        Envelope("nice!nano", f"{side} socket strip's sleeves",
                 nano_row_x_range(fits, side == "west"),
                 grown_range(nano_pins_y_range(), NANO_PIN_PAD_DIAMETER_MM / 2.0),
                 (top, nano_strip_insulator_bottom_z(fits)), CAVITY)
        for side in ("west", "east")
    )


def nano_strip_envelopes(fits=DEFAULT_MOUNT_FITS):
    """The strips on the board's top, insulators and sleeves."""
    return nano_strip_insulators(fits) + nano_strip_sleeves(fits)


def nano_tail_tip_below_board():
    """How far the longest tail reaches below the board's underside."""
    return (NANO_STRIP_TAIL_LENGTH_MM - NANO_BOARD_THICKNESS_MM
            + NANO_STRIP_PIN_LENGTH_TOLERANCE_MM)


def nano_tail_envelopes(fits=DEFAULT_MOUNT_FITS):
    """The west and the east row's tails under the board."""
    underside = nano_board_envelope(fits).z_range[0]
    radius = NANO_STRIP_TAIL_DIAMETER_MM / 2.0
    return tuple(
        Envelope("nice!nano", f"{side} strip's tails",
                 grown_range(nano_row_axis_x_range(fits, side == "west"), radius),
                 grown_range(nano_pins_y_range(), radius),
                 (underside - nano_tail_tip_below_board(), underside), CAVITY)
        for side in ("west", "east")
    )


# The room over each strip, from its top up to the PCB's underside,
# which no tray body may reach into as printed, for whatever plugs into
# the strip. The sockets of the keys over it hang into it from the PCB
# (check_layout.py reports how far they stay over the strips' tops).
def nano_strip_rooms(fits=DEFAULT_MOUNT_FITS):
    return tuple(
        Envelope("nice!nano", f"room over the {side} socket strip", strip.x_range, strip.y_range,
                 (strip.z_range[1], PCB_UNDERSIDE_Z_MM), CAVITY)
        for side, strip in zip(("west", "east"), nano_strip_insulators(fits))
    )


# The strips' pockets: over the board's top the west ledge's face and
# the east wall's inner face are cut back over each strip's worst case
# grown by the print's swelling and NANO_BOARD_PLAY_ALLOWANCE_MM, open
# above, so that as printed they clear it by that allowance wherever the
# board moves in its pocket: the most the user's caliper leaves it
# across ("The bay inside width is 18.41~18.46. The nano width is
# 18.17~18.23 mm", 2026-10-20: 18.46 less 18.17 is 0.29), about the
# third of a millimeter the user felt along it ("maybe 1/3 of a
# millimeter lengthwise"). Below the board's top the faces still locate
# its edges. The west pocket is a TrayCut out of the ledge
# (nano_strip_ledge_pocket()), the east one splits the east wall
# (nano_east_wall_boxes()). Both run NANO_STRIP_POCKET_NORTH_EXTENSION_MM
# further north for the board going in tilted (check_layout.py's tilt
# figures): its top rises toward its south end, so the strips lean
# north and the west strip's north top corner comes toward the ledge
# north of its pocket. With all of the end faces' swelling on the foot,
# the north block's face standing as modelled, the corner reached
# 0.069 into the ledge there as printed. The extension, the
# least in 0.01 steps, keeps it 0.1 clear at that split. The east
# pocket's north end lies north of the east wall's, so only the ledge
# changes.
NANO_BOARD_PLAY_ALLOWANCE_MM = 0.3
NANO_STRIP_POCKET_NORTH_EXTENSION_MM = 0.17


def nano_strip_pocket_margin():
    return PRINT_SWELLING_PER_SIDE_MM + NANO_BOARD_PLAY_ALLOWANCE_MM


def nano_strip_pocket_x_range(fits=DEFAULT_MOUNT_FITS):
    """(the west pocket's face, the east pocket's face)."""
    margin = nano_strip_pocket_margin()
    return (nano_strip_x_range(fits, True)[0] - margin, nano_strip_x_range(fits, False)[1] + margin)


def nano_strip_pocket_y_range():
    south, north = grown_range(nano_strip_y_range(), nano_strip_pocket_margin())
    return (south, north + NANO_STRIP_POCKET_NORTH_EXTENSION_MM)


def west_outline_edge_index():
    """The outline's west edge, x = 0, which the west ledge runs along."""
    west_x = min(x for x, _ in OUTLINE_VERTICES_MM)
    return nearest_outline_edge_index((west_x, sum(nano_strip_pocket_y_range()) / 2.0))


def nano_strip_ledge_pocket(fits=DEFAULT_MOUNT_FITS):
    """The west strip's pocket in the west ledge, from the board's top up
    through the ledge's top, from the pocket's face out past the ledge's
    face like the other ledge cuts."""
    index = west_outline_edge_index()
    face_x = nano_strip_pocket_x_range(fits)[0]
    ends = [outline_edge_coordinates((face_x, y), index) for y in nano_strip_pocket_y_range()]
    along_range = tuple(sorted(along for along, _ in ends))
    across_range = (ledge_cut_across_range()[0], ends[0][1])
    return TrayCut("west strip's pocket", index, along_range, across_range,
                   (nano_board_envelope(fits).z_range[1], PCB_UNDERSIDE_Z_MM))


# The seat under the board's middle (NANO_SEAT_HEIGHT_MM, the user's
# request to raise the bay): from the foot's face to the north block's,
# between two channels along the board's long edges, down to the
# floor's top, in which the strips' tails, their solder and the B+ and
# B- pads (battery wires get soldered there) hang free. Each channel
# runs from the pocket's side face to the inner edge of its row's pads
# at the larger of the render's insets plus, as printed,
# NANO_TAIL_FILLET_ALLOWANCE_MM for a solder fillet spilling past its
# pad (taken, not measured) and NANO_BOARD_PLAY_ALLOWANCE_MM for the
# board moving across its pocket. The pry recess (nano_pry_recess_box())
# is left out of the seat's southwest corner, so the seat is two boxes.
NANO_TAIL_FILLET_ALLOWANCE_MM = 0.2


def nano_seat_margin():
    """The seat's edges from the pads' inner edges as modelled."""
    return (NANO_TAIL_FILLET_ALLOWANCE_MM + NANO_BOARD_PLAY_ALLOWANCE_MM
            + PRINT_SWELLING_PER_SIDE_MM)


def nano_seat_x_range(fits=DEFAULT_MOUNT_FITS):
    margin = nano_seat_margin()
    return (nano_row_x_range(fits, True)[1] + margin, nano_row_x_range(fits, False)[0] - margin)


def nano_seat_boxes(fits=DEFAULT_MOUNT_FITS):
    """The seat north of the pry recess and the seat east of it."""
    low_x, high_x = nano_seat_x_range(fits)
    recess = nano_pry_recess_box(fits)
    z_range = (0.0, NANO_SEAT_HEIGHT_MM)
    return (
        MountBox("seat", "nice!nano", (low_x, high_x),
                 (recess.y_range[1], nano_north_block_south_y(fits)), z_range),
        MountBox("seat beside the pry recess", "nice!nano", (recess.x_range[1], high_x),
                 (nano_clamp_stop_y(fits), recess.y_range[1]), z_range),
    )


# The pry slot and recess (work item 010, the user's request once the
# foot stood as tall as the board: "Can you open up a 5 mm pry slot in
# the south wall with a pry recess in the floor to go along with it? So
# I can pry with e.g. a toothpick"). The slot runs through the clamp's
# block and foot, NANO_PRY_SLOT_WIDTH_MM across from
# NANO_PRY_SLOT_FROM_LEDGE_MM east of the west ledge's face, west of the
# screw, from the floor up through their tops. The recess is the seat
# left out under the slot's width from the foot's face to
# NANO_PRY_RECESS_UNDER_BOARD_MM under the board's south end, down to
# the floor's top, as the slot is (nano_seat_boxes()), so the floor
# stays whole under it. A toothpick coming down the slot from over the
# south rim gets its tapered point under the board's edge
# (check_layout.py works out the least angle that clears the rim and the
# ledge, and how far the point then gets), in the slot's part east of
# the west row's last tail and its solder (check_layout.py's lane).
# With the tab off, the toothpick lifts the board's south end, and the
# board pitches up rather than rolling about its east edge. Its north
# end's top edge rides up the north block's face as it turns about the
# shell's mouth on the seat, so it slides south a little, its south
# edge staying clear of the foot's face as printed, as when it goes in
# (check_layout.py's insertion figures), or it pivots on the shell's top
# against the bar. Either way its whole south end comes up over the
# foot, and it then slides south out of the shell's channel.
NANO_PRY_SLOT_WIDTH_MM = 5.0
NANO_PRY_SLOT_FROM_LEDGE_MM = 1.0
NANO_PRY_RECESS_UNDER_BOARD_MM = 2.0
# The toothpick check_layout.py fits in: 2.0 across, tapering to a
# round point on its axis over its last 5.0.
NANO_PRY_TOOTHPICK_DIAMETER_MM = 2.0
NANO_PRY_TOOTHPICK_TAPER_MM = 5.0


def nano_pry_slot_x_range():
    west = west_ledge_face_x() + NANO_PRY_SLOT_FROM_LEDGE_MM
    return (west, west + NANO_PRY_SLOT_WIDTH_MM)


def nano_pry_slot_box(fits=DEFAULT_MOUNT_FITS):
    """The slot through the clamp's block and foot, from the floor to
    the block's top."""
    block, foot = nano_clamp_boxes(fits)
    return MountBox("pry slot", "nice!nano", nano_pry_slot_x_range(),
                    (block.y_range[0], foot.y_range[1]), (0.0, block.z_range[1]))


def nano_pry_recess_box(fits=DEFAULT_MOUNT_FITS):
    """The room under the slot and the board's south end that the seat
    leaves free, from the slot's south end, down to the floor's top."""
    south = nano_clamp_boxes(fits)[0].y_range[0]
    north = nano_south_end_y(fits) + NANO_PRY_RECESS_UNDER_BOARD_MM
    return MountBox("pry recess", "nice!nano", nano_pry_slot_x_range(), (south, north),
                    (0.0, NANO_SEAT_HEIGHT_MM))


# The power switch: its lever's slot through the north wall, its swept
# box's slip fit, and the cradle on the floor, which holds the body
# snug between two end blocks against the 3.5 N slide force and against
# the wall by two back arms beside the pins, against a push on the
# lever's tip.
POWER_SWITCH_CRADLE_TOP_Z_MM = 3.0
POWER_SWITCH_CRADLE_END_MM = 1.2  # along x
POWER_SWITCH_CRADLE_BACK_MM = 0.8  # along y


def power_switch_lever_slot_box():
    north_edge_y = NORTH_EDGE_Y_OF_COLUMN_2_MM
    lever = POWER_SWITCH_LEVER
    return MountBox(
        "lever slot",
        "power switch",
        centered_range(
            POWER_SWITCH_CENTER_X_MM,
            printed_fit(lever.x_range[1] - lever.x_range[0], SLIP_FIT_MM),
        ),
        (cavity_wall_y(north_edge_y), outer_face_y(north_edge_y)),
        centered_range(
            POWER_SWITCH_LEVER_Z_MM, printed_fit(lever.z_range[1] - lever.z_range[0], SLIP_FIT_MM)
        ),
    )


def power_switch_cradle_boxes():
    center = POWER_SWITCH_CENTER_X_MM
    half_inside = printed_fit(POWER_SWITCH_BODY_X_MM, SNUG_FIT_MM) / 2.0
    outside = half_inside + POWER_SWITCH_CRADLE_END_MM
    wall = cavity_wall_y(NORTH_EDGE_Y_OF_COLUMN_2_MM)
    back_face = wall - printed_fit(POWER_SWITCH_BODY_Y_MM, SNUG_FIT_MM)
    back = back_face - POWER_SWITCH_CRADLE_BACK_MM
    pins = POWER_SWITCH_PINS.x_range
    half_pin_slot = printed_fit(pins[1] - pins[0], SLIP_FIT_MM) / 2.0
    z_range = (0.0, POWER_SWITCH_CRADLE_TOP_Z_MM)
    return (
        MountBox("cradle's west end", "power switch", (center - outside, center - half_inside),
                 (back, wall), z_range),
        MountBox("cradle's east end", "power switch", (center + half_inside, center + outside),
                 (back, wall), z_range),
        MountBox("cradle's west back arm", "power switch",
                 (center - outside, center - half_pin_slot), (back, back_face), z_range),
        MountBox("cradle's east back arm", "power switch",
                 (center + half_pin_slot, center + outside), (back, back_face), z_range),
    )


# The reset button: the pin hole through the north wall over the stem
# (DESIGN.md's 3.0, kbdkid4's plate reset hole, a passage for a SIM pin
# rather than a fit, so it prints about 2.6), and the back wall behind
# the housing, which takes the press. The button's depth with its stem
# 0.2 short of the wall is a snug fit between the back wall and the
# wall's inner face. The back wall is notched from its top for the
# leads, each notch the slip fit of the band the lead may lie in, down
# to the lead's band less the swelling and half the clearance.
RESET_PIN_HOLE_DIAMETER_MM = 3.0
RESET_BACK_WALL_MM = 1.2
RESET_BACK_WALL_BEYOND_NOTCHES_MM = 1.0


def reset_pin_hole_center():
    """(x, z) of the hole's axis: the stem's middle."""
    return (RESET_BUTTON_CENTER_X_MM, sum(RESET_BUTTON_STEM.z_range) / 2.0)


def reset_pin_hole_box():
    x, z = reset_pin_hole_center()
    north_edge_y = NORTH_EDGE_Y_OF_COLUMN_3_MM
    return MountBox(
        "reset pin hole",
        "reset button",
        centered_range(x, RESET_PIN_HOLE_DIAMETER_MM),
        (cavity_wall_y(north_edge_y), outer_face_y(north_edge_y)),
        horizontal_hole_z_range(z, RESET_PIN_HOLE_DIAMETER_MM),
    )


def reset_back_wall_face_y():
    depth = RESET_BUTTON_TO_STEM_TOP_MM + RESET_BUTTON_STEM_SHORT_OF_WALL_MM
    return cavity_wall_y(NORTH_EDGE_Y_OF_COLUMN_3_MM) - printed_fit(depth, SNUG_FIT_MM)


def reset_notch_x_range(side):
    """The notch for the lead on `side` (-1 west, 1 east)."""
    inside, outside = reset_button_lead_band()
    middle = (inside + outside) / 2.0
    half = printed_fit(outside - inside, SLIP_FIT_MM) / 2.0
    ends = (RESET_BUTTON_CENTER_X_MM + side * (middle - half),
            RESET_BUTTON_CENTER_X_MM + side * (middle + half))
    return (min(ends), max(ends))


def reset_notch_bottom_z():
    return reset_button_lead_z_range()[0] - half_fit_gap(0.0, SLIP_FIT_MM)


def reset_back_wall_boxes():
    face = reset_back_wall_face_y()
    y_range = (face - RESET_BACK_WALL_MM, face)
    top = RESET_BUTTON_BODY_Z_MM
    west_notch = reset_notch_x_range(-1.0)
    east_notch = reset_notch_x_range(1.0)
    west_end = west_notch[0] - RESET_BACK_WALL_BEYOND_NOTCHES_MM
    east_end = east_notch[1] + RESET_BACK_WALL_BEYOND_NOTCHES_MM
    return (
        MountBox("back wall's middle", "reset button", (west_notch[1], east_notch[0]), y_range,
                 (0.0, top)),
        MountBox("back wall's west end", "reset button", (west_end, west_notch[0]), y_range,
                 (0.0, top)),
        MountBox("back wall's east end", "reset button", (east_notch[1], east_end), y_range,
                 (0.0, top)),
        MountBox("back wall under the notches", "reset button", (west_end, east_end), y_range,
                 (0.0, reset_notch_bottom_z())),
    )


# The battery header's pocket: two side walls holding the header's 5.9
# snug, a back wall behind its base, slotted from the top for the posts,
# and the floor, open toward the plug. JST's figures leave the header's
# front rim under the mated plug's housing (DESIGN.md), so the front
# lips that would hold that rim against the plug's pull are left out
# unless battery_shoulder asks for them: then they reach that far onto
# the rim as printed, BATTERY_HEADER_LIP_MM thick along x.
BATTERY_POCKET_WALL_MM = 1.2
BATTERY_POCKET_TOP_Z_MM = BATTERY_CONNECTOR.z_range[1]
BATTERY_HEADER_LIP_MM = 1.0


def battery_pocket_y_range():
    header = BATTERY_CONNECTOR.y_range
    return centered_range(
        BATTERY_CONNECTOR_MIDDLE_Y_MM, printed_fit(header[1] - header[0], SNUG_FIT_MM)
    )


def battery_pocket_x_range():
    """From the lips' faces, half the fit's gap in front of the header's
    entry face, to the back wall's face."""
    header = BATTERY_CONNECTOR.x_range
    west = header[0] - half_fit_gap(header[1] - header[0], SNUG_FIT_MM)
    return (west, west + printed_fit(header[1] - header[0], SNUG_FIT_MM))


def battery_post_slot_y_range():
    posts = BATTERY_CONNECTOR_POSTS.y_range
    return centered_range(
        BATTERY_CONNECTOR_MIDDLE_Y_MM, printed_fit(posts[1] - posts[0], SLIP_FIT_MM)
    )


def battery_post_slot_bottom_z():
    return BATTERY_CONNECTOR_POSTS.z_range[0] - half_fit_gap(0.0, SLIP_FIT_MM)


def battery_pocket_boxes(fits=DEFAULT_MOUNT_FITS):
    low_y, high_y = battery_pocket_y_range()
    west, east = battery_pocket_x_range()
    wall = BATTERY_POCKET_WALL_MM
    z_range = (0.0, BATTERY_POCKET_TOP_Z_MM)
    slot_low, slot_high = battery_post_slot_y_range()
    back = (east, east + wall)
    boxes = [
        MountBox("pocket's south wall", "battery connector", (west, east), (low_y - wall, low_y),
                 z_range),
        MountBox("pocket's north wall", "battery connector", (west, east),
                 (high_y, high_y + wall), z_range),
        MountBox("back wall south of the post slot", "battery connector", back,
                 (low_y - wall, slot_low), z_range),
        MountBox("back wall north of the post slot", "battery connector", back,
                 (slot_high, high_y + wall), z_range),
        MountBox("back wall under the post slot", "battery connector", back,
                 (slot_low, slot_high), (0.0, battery_post_slot_bottom_z())),
    ]
    if fits.battery_shoulder > 0.0:
        header = BATTERY_CONNECTOR.y_range
        opening = printed_fit(header[1] - header[0] - 2.0 * fits.battery_shoulder, SNUG_FIT_MM)
        lips_x = (west - BATTERY_HEADER_LIP_MM, west)
        middle = BATTERY_CONNECTOR_MIDDLE_Y_MM
        boxes.append(MountBox("south front lip", "battery connector", lips_x,
                              (low_y - wall, middle - opening / 2.0), z_range))
        boxes.append(MountBox("north front lip", "battery connector", lips_x,
                              (middle + opening / 2.0, high_y + wall), z_range))
    return tuple(boxes)


# The battery's corner ribs: an L at three corners, the pouch a fit with
# 0.5 per side as modelled (0.3 as printed, since pouches vary), and
# none at the corner its lead leaves, the northeast (DESIGN.md).
BATTERY_RIB_FIT_MM = 0.6
BATTERY_RIB_HEIGHT_MM = 1.0
BATTERY_RIB_THICKNESS_MM = 0.8
BATTERY_RIB_ARM_MM = 6.0
BATTERY_LEAD_CORNER = (1, 1)  # (east, north)


def battery_rib_pocket():
    """(x range, y range) the ribs' inner faces bound."""
    return tuple(
        centered_range(sum(value_range) / 2.0,
                       printed_fit(value_range[1] - value_range[0], BATTERY_RIB_FIT_MM))
        for value_range in (BATTERY.x_range, BATTERY.y_range)
    )


def corner_name(east, north):
    return ("north" if north > 0 else "south") + ("east" if east > 0 else "west")


def battery_rib_boxes():
    (low_x, high_x), (low_y, high_y) = battery_rib_pocket()
    thickness = BATTERY_RIB_THICKNESS_MM
    z_range = (0.0, BATTERY_RIB_HEIGHT_MM)
    boxes = []
    for east in (-1, 1):
        for north in (-1, 1):
            if (east, north) == BATTERY_LEAD_CORNER:
                continue
            corner_x = high_x if east > 0 else low_x
            corner_y = high_y if north > 0 else low_y
            outer_x = corner_x + east * thickness
            outer_y = corner_y + north * thickness
            name = corner_name(east, north)
            boxes.append(MountBox(
                f"battery's {name} rib along x",
                "battery",
                tuple(sorted((outer_x, corner_x - east * BATTERY_RIB_ARM_MM))),
                tuple(sorted((corner_y, outer_y))),
                z_range,
            ))
            boxes.append(MountBox(
                f"battery's {name} rib along y",
                "battery",
                tuple(sorted((corner_x, outer_x))),
                tuple(sorted((outer_y, corner_y - north * BATTERY_RIB_ARM_MM))),
                z_range,
            ))
    return tuple(boxes)


def nano_bodies(fits=DEFAULT_MOUNT_FITS):
    return (nano_north_block_boxes(fits) + nano_clamp_boxes(fits) + nano_east_wall_boxes(fits)
            + nano_seat_boxes(fits))


def mount_bodies(fits=DEFAULT_MOUNT_FITS):
    """Every box of plastic the mounts add, in the order the tray
    builder fuses them: the nice!nano's last, since its east wall takes
    in the battery's northwest rib."""
    return (
        power_switch_cradle_boxes()
        + reset_back_wall_boxes()
        + battery_pocket_boxes(fits)
        + battery_rib_boxes()
        + nano_bodies(fits)
    )


def wall_openings(fits=DEFAULT_MOUNT_FITS):
    """The openings through the north wall, each as its boxes from the
    cavity out: the shell's channel and the window, the lever slot, the
    pin hole."""
    return (usb_opening_boxes(fits), (power_switch_lever_slot_box(),), (reset_pin_hole_box(),))


def mount_voids(fits=DEFAULT_MOUNT_FITS):
    """Every box the mounts cut, the window and the pin hole as their
    bounding boxes, in the order the tray builder cuts them: the
    openings through the wall and the pry slot through the clamp's block
    and foot. The clamp's insert bore is left out: it lies in the clamp's
    block, like a standoff's in the standoff. No void reaches into the
    floor: the pry recess is the seat left out (nano_seat_boxes())."""
    openings = tuple(box for opening in wall_openings(fits) for box in opening)
    return openings + (nano_pry_slot_box(fits),)


# The room the wires need (DESIGN.md: wires need room behind every
# lead): WIRE_ROOM_BEHIND_LEADS_MM beyond each lead's tip, its row's
# width and WIRE_ROOM_BESIDE_LEADS_MM to either side, from the floor to
# WIRE_ROOM_ABOVE_LEADS_MM over the lead, and WIRE_ROOM_ABOVE_PADS_MM
# above the nice!nano's B+, B- and P1 pads, WIRE_ROOM_BESIDE_PADS_MM
# beyond them, since its wires are soldered on its top side. Its pins 1
# to 12 take the socket strips instead, with the room over each strip
# (nano_strip_rooms()). The battery's lead leaves its northeast corner,
# along either edge.
WIRE_ROOM_BEHIND_LEADS_MM = 3.0
WIRE_ROOM_BESIDE_LEADS_MM = 1.0
WIRE_ROOM_ABOVE_LEADS_MM = 1.5
WIRE_ROOM_ABOVE_PADS_MM = 3.0
WIRE_ROOM_BESIDE_PADS_MM = 0.5


def wire_room(part, label, x_range, y_range, z_range):
    return Envelope(part, f"wire room {label}", x_range, y_range, z_range, CAVITY)


def lead_wire_rooms():
    behind = WIRE_ROOM_BEHIND_LEADS_MM
    beside = WIRE_ROOM_BESIDE_LEADS_MM
    above = WIRE_ROOM_ABOVE_LEADS_MM
    pins = POWER_SWITCH_PINS
    west_lead, east_lead = RESET_BUTTON_WEST_LEAD, RESET_BUTTON_EAST_LEAD
    posts = BATTERY_CONNECTOR_POSTS
    plug = BATTERY_PLUG
    battery = BATTERY
    corner_x, corner_y = battery.x_range[1], battery.y_range[1]
    return (
        wire_room("power switch", "behind the pins", grown_range(pins.x_range, beside),
                  (pins.y_range[0] - behind, pins.y_range[0]), (0.0, pins.z_range[1] + above)),
        wire_room("reset button", "behind the leads",
                  (west_lead.x_range[0] - beside, east_lead.x_range[1] + beside),
                  (west_lead.y_range[0] - behind, west_lead.y_range[0]),
                  (0.0, west_lead.z_range[1] + above)),
        wire_room("battery connector", "behind the posts",
                  (posts.x_range[1], posts.x_range[1] + behind), grown_range(posts.y_range, beside),
                  (0.0, posts.z_range[1] + above)),
        wire_room("battery connector", "behind the plug", (plug.x_range[0] - behind,
                  plug.x_range[0]), plug.y_range, plug.z_range),
        wire_room("battery", "north of its lead's corner",
                  (corner_x - BATTERY_RIB_ARM_MM, corner_x + beside),
                  (corner_y, corner_y + behind), battery.z_range),
        wire_room("battery", "east of its lead's corner", (corner_x, corner_x + behind),
                  (corner_y - BATTERY_RIB_ARM_MM, corner_y + beside), battery.z_range),
    )


def nano_wire_rooms(fits=DEFAULT_MOUNT_FITS, right=False):
    """The rooms over the B- and B+ pads, B- on the west on the left half
    and, in the left half's frame, on the east on the right one, and over
    the P1 pads."""
    beside = WIRE_ROOM_BESIDE_PADS_MM
    top = NANO_BOARD.z_range[1]
    z_range = (top, top + WIRE_ROOM_ABOVE_PADS_MM)
    pads_y = grown_range(nano_battery_pads_y_range(), beside)
    west_pad, east_pad = ("B+", "B-") if right else ("B-", "B+")
    return (
        wire_room("nice!nano", f"over the {west_pad} pad",
                  grown_range(nano_battery_pad_x_range(fits, True), beside), pads_y, z_range),
        wire_room("nice!nano", f"over the {east_pad} pad",
                  grown_range(nano_battery_pad_x_range(fits, False), beside), pads_y, z_range),
        wire_room("nice!nano", "over the P1.01/P1.02/P1.07 pads",
                  grown_range(nano_extra_pads_x_range(fits, right), beside),
                  grown_range(nano_extra_pads_y_range(), beside), z_range),
    )


def wire_rooms(fits=DEFAULT_MOUNT_FITS, right=False):
    return lead_wire_rooms() + nano_wire_rooms(fits, right)
