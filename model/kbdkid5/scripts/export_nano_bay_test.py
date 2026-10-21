"""Export the nice!nano test bay (STL): one bay cut out of the left
tray, its pocket at the default slip fit across the board, the user's
choice to shorten the print, to settle the bay on a real board before
printing whole trays (work items 006, 009, 010 and 011). BAY_FITS can
step the fit over several bays again, side by side in one strip.

Each bay is build_tray()'s left tray (tray_shape.py) with the bay's
layout.MountFits, cut by one box around the nice!nano's corner, so the
bay is the tray's geometry and not a copy of it. The box reaches past
the tray's west and north faces, so it holds the floor, the west and
north walls at full height with the ledge and the west socket strip's
pocket in it, the USB window, the north block, the screw clamp's block
and foot with the standoff at (18.574, 37.782) they take in, the east
wall with the east strip's pocket, the seat the board lies on, the pry
slot and the pry recess the seat leaves free.
Its east face (BAY_EAST_X_MM) cuts the floor and the north wall and
ledge east of the battery's northwest rib, its south face
(BAY_SOUTH_Y_MM) the floor and the west wall and ledge south of the
clamp's block, so the bay keeps that standoff and the rib whole and
floor beyond the rib and the block to join and to hold.
The box crosses nothing else: every other feature of the tray lies
wholly inside it or wholly outside, at least BAY_BOX_MARGIN_MM from
its faces, and the faces keep BAY_BOX_MARGIN_MM plus the corner's
radius from every vertex of the outer face's, the cavity wall's and
the ledge's outlines, so they cut no rounded corner, which the script
checks.

The bays sit BAY_GAP_MM apart along x, bay 1 the westernmost, each
joined to the next by a bridge of the floor's thickness across the
gap, and are fused into one solid. Bay k (from 1) has k notches in its
floor's south edge, so a printed bay names itself.

The bays can step the pocket's fit across the board (BAY_FITS), the
east wall's inner face standing further east from bay to bay. There is
one bay now, at the default slip fit. The clamp's press and the bar's
clearance are the defaults in every bay, under one tab
(export_clamp_tab.py's, the same for every bay and both halves). The
words nano_length and nano_width size the board for every bay.

Every bay passes the mount checks the default tray passes:
check_layout.py's problem functions with the bay's fits (the mounts
inside the tray and clear of the parts, the sockets, the standoffs and
the joint, the clamp's tab within its strain and under the PCB, no
void below the floor's top, the openings around the shell and the
knob, the board going in past the foot, the seat, the socket strips
clear of the tray, the pry slot, the wire rooms), on top of
build_tray()'s own probes of what it built, its closed floor among
them. Any problem stops the export.

Runs headless under FreeCAD's console interpreter (see
freecad_common.py for the freecadcmd quirks that shape the
invocation):

    freecadcmd model/kbdkid5/scripts/export_nano_bay_test.py --pass <bay.stl>
        [nano_length=<mm>] [nano_width=<mm>]

It prints the box, the clamp's and the bar's figures common to the
bays, and each bay's (the pocket as modelled and as printed, the east
wall's inner face), checks
the strip for one valid solid of the bays' and bridges' volume,
every bay's notch count, and a closed mesh, and writes it floor down,
as the tray prints, the floor's underside on z = 0.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App
import Part

import check_layout
import layout
from freecad_common import check_closed_mesh, export_stl, run_and_exit, script_arguments
from tray_shape import (
    CUT_EXTRA_MM,
    DEFAULT_GAP_MM,
    DEFAULT_LEDGE_WIDTH_MM,
    DEFAULT_WALL_MM,
    FLOOR_UNDERSIDE_Z_MM,
    INSIDE_TOLERANCE_MM,
    RIM_Z_MM,
    build_tray,
    layout_polygon_wire,
    require_one_valid_solid,
    require_volume,
    tray_corner_radius,
)

# Each bay's pocket fit across the board (nano_pocket_fit), west to
# east. A snug pocket's east wall would come inside the board as printed
# (layout.py's NANO_POCKET_FIT_MM). One bay at the default slip fit, the
# user's choice to shorten the print (doc/log/2026-10-19.md), where the
# first strip of this bay stepped 0.1, 0.2 and 0.3.
BAY_FITS = (0.1,)
DEFAULT_BAY_INDEX = 0

# The box each bay is cut by: east and south faces through the floor
# (and the walls and the ledge they meet), the others past the tray's
# outside by CUT_EXTRA_MM. Every feature of the tray but the walls, the
# ledge and the floor keeps BAY_BOX_MARGIN_MM from its faces, inside or
# outside.
BAY_EAST_X_MM = 28.0
BAY_SOUTH_Y_MM = 31.0
BAY_BOX_MARGIN_MM = 0.5

# The bays lie this far apart, bridged by the floor's thickness from
# the box's south face to the north ledge's face, short of the next
# bay's corner round.
BAY_GAP_MM = 2.0

# The notches that number the bays, through the floor from its south
# edge, south of the clamp's block and its pry recess.
NOTCH_WIDTH_MM = 1.0
NOTCH_DEPTH_MM = 0.8
NOTCH_PITCH_MM = 2.0
NOTCH_MIDDLE_X_MM = 7.0

USAGE = f"""\
usage: freecadcmd model/kbdkid5/scripts/export_nano_bay_test.py --pass <bay.stl>
           [nano_length=<mm>] [nano_width=<mm>]

  nano_length  the nice!nano's board length the bays are fitted to
               (default {layout.NANO_LENGTH_MM}), its USB end staying put
  nano_width   its width (default {layout.NANO_WIDTH_MM}), its west edge staying put\
"""

OPTION_KEYS = ("nano_length", "nano_width")


class Arguments:
    def __init__(self):
        self.stl_file = None
        self.board_size = {}  # the MountFits fields given


def parse_arguments(argument_list):
    arguments = Arguments()
    positionals = []
    for argument in argument_list:
        if "=" in argument:
            key, _, value = argument.partition("=")
            if key not in OPTION_KEYS:
                raise SystemExit(f"error: unknown option '{key}'\n{USAGE}")
            try:
                arguments.board_size[key] = float(value)
            except ValueError:
                raise SystemExit(f"error: '{key}' needs a number, got '{value}'")
        else:
            positionals.append(argument)
    if len(positionals) != 1:
        raise SystemExit(USAGE)
    arguments.stl_file = positionals[0]
    return arguments


def bay_fits(index, board_size):
    return layout.MountFits(nano_pocket_fit=BAY_FITS[index], **board_size)


# The mount checks, check_layout.py's, with a bay's fits.


def mount_problems(fits):
    """Every problem check_layout.py's mount checks find with the fits on
    the left half."""
    right = False
    return (
        check_layout.mount_containment_problems(fits)[0]
        + check_layout.mount_part_clearances(fits)[3]
        + check_layout.mount_socket_problems(right, fits)[0]
        + check_layout.mount_standoff_clearances(fits)[0]
        + check_layout.mount_joint_problems(right, fits)[0]
        + check_layout.clamp_problems(fits)
        + check_layout.opening_problems(fits)
        + check_layout.insertion_problems(fits)
        + check_layout.nano_seat_problems(fits)
        + check_layout.nano_strip_clearances(right, fits)[0]
        + check_layout.pry_slot_problems(right, fits)
        + check_layout.wire_room_problems(right, fits)[0]
    )


def bar_clearance_as_printed(fits):
    """The bar's underside over the shell's top, the underside sagging
    the swelling once printed."""
    shell_top = layout.nano_usb_shell_envelope(fits).z_range[1]
    return layout.nano_bar_underside_z(fits) - layout.PRINT_SWELLING_PER_SIDE_MM - shell_top


def common_figures(fits):
    return (
        f"the clamp pressing {fits.clamp_press:.1f} as printed, its block's top at z "
        f"{layout.nano_clamp_block_top_z(fits):.1f}, the tab's strain "
        f"{100.0 * layout.nano_clamp_strain(fits):.2f} % as printed, bar "
        f"{bar_clearance_as_printed(fits):.2f} over the shell as printed"
    )


def bay_figures(fits):
    pocket = layout.nano_pocket_east_x(fits) - layout.west_ledge_face_x()
    printed = pocket - 2.0 * layout.PRINT_SWELLING_PER_SIDE_MM
    return (
        f"the pocket {pocket:.1f} across as modelled, {printed:.1f} as printed, the east wall's "
        f"inner face at x {layout.nano_pocket_east_x(fits):.1f}"
    )


# The box against the tray's features, in plan.


def tray_outer_west_x():
    return min(x for x, _ in layout.tray_outer_polygon())


def tray_outer_north_y():
    """The north wall's outer face behind the nice!nano."""
    return layout.outer_face_y(layout.NORTH_EDGE_Y_OF_COLUMNS_0_AND_1_MM)


def bay_box_plan():
    """(x range, y range) of the box each bay is cut by."""
    return (
        (tray_outer_west_x() - CUT_EXTRA_MM, BAY_EAST_X_MM),
        (BAY_SOUTH_Y_MM, tray_outer_north_y() + CUT_EXTRA_MM),
    )


def standoff_square(center):
    """A standoff's bounding square: inside an axis-aligned box exactly
    when the standoff is, and outside it at least as far as the
    standoff."""
    radius = layout.STANDOFF_DIAMETER_MM / 2.0
    (x, y) = center
    return ((x - radius, y - radius), (x + radius, y - radius), (x + radius, y + radius),
            (x - radius, y + radius))


def bay_features(fits):
    """(label, convex plan polygon, must lie inside) of every feature of
    the left tray but the walls, the ledge and the floor: the mounts'
    boxes (the nice!nano's must lie inside), the ledge cut-aways, the
    west socket strip's pocket and the sockets' cuts, the standoffs
    (their flats lie on them) and the joint."""
    boxes = layout.mount_bodies(fits) + layout.mount_voids(fits)
    mounts = [(check_layout.describe_mount(box), check_layout.box_polygon(box),
               box.part == "nice!nano") for box in boxes]
    cuts = [layout.ledge_cutaway_cut(cutaway) for cutaway in layout.ledge_cutaways(fits)]
    cuts.append(layout.nano_strip_ledge_pocket(fits))
    cuts.extend(layout.all_socket_tray_cuts())
    tray_cuts = [(cut.label, layout.tray_cut_polygon(cut), False) for cut in cuts]
    standoffs = [(f"standoff at {center}", standoff_square(center), False)
                 for center in layout.MOUNTING_DRILL_CENTERS_MM]
    joint = [(label, polygon, False) for label, polygon, _ in
             check_layout.joint_features() + check_layout.boss_fills() + check_layout.joint_voids()]
    joint.append(("parking hole's boss", layout.parking_boss_polygon(), False))
    return mounts + tray_cuts + standoffs + joint


def inside_margin(polygon, x_range, y_range):
    """The least distance of the polygon's corners inside the box's
    faces, negative when one lies outside."""
    return min(
        min(x - x_range[0], x_range[1] - x, y - y_range[0], y_range[1] - y) for x, y in polygon
    )


def bay_box_problems(fits):
    """(problems, least margin inside, least clearance outside): the
    box holds every feature it must and crosses no feature, each at
    least BAY_BOX_MARGIN_MM from its faces."""
    x_range, y_range = bay_box_plan()
    box = ((x_range[0], y_range[0]), (x_range[1], y_range[0]), (x_range[1], y_range[1]),
           (x_range[0], y_range[1]))
    problems = []
    inside, outside = check_layout.Tightest(), check_layout.Tightest()
    minimum = BAY_BOX_MARGIN_MM - check_layout.TOLERANCE_MM
    for label, polygon, must_be_inside in bay_features(fits):
        margin = inside_margin(polygon, x_range, y_range)
        clearance = check_layout.convex_separation(box, polygon)
        if margin >= minimum:
            inside.update(margin, label)
        elif clearance >= minimum and not must_be_inside:
            outside.update(clearance, label)
        elif must_be_inside:
            problems.append(f"the {label} lies {margin:.3f} inside the box, less than "
                            f"{BAY_BOX_MARGIN_MM}")
        else:
            problems.append(f"the box crosses the {label} (inside by {margin:.3f}, outside by "
                            f"{clearance:.3f})")
    return problems, inside, outside


def outline_corner_radii(corner_radius):
    """(label, sharp polygon, its convex corners' radius, its concave
    corners' radius) of each outline the walls, the ledge and the floor
    are rounded from, as tray_shape.py rounds them (a ledge corner out
    of radius is sharp)."""
    wall, ledge = DEFAULT_WALL_MM, DEFAULT_LEDGE_WIDTH_MM
    return (
        ("outer face", layout.tray_outer_polygon(), corner_radius, corner_radius - wall),
        ("cavity wall", layout.tray_cavity_polygon(), corner_radius - wall, corner_radius),
        ("ledge's inner face", layout.ledge_inner_polygon(),
         max(0.0, corner_radius - wall - ledge), corner_radius + ledge),
    )


def box_cutting_faces():
    """(label, start, end) of the box's faces that cut the tray, in plan."""
    (west, east), (south, north) = bay_box_plan()
    return (("east face", (east, south), (east, north)),
            ("south face", (west, south), (east, south)))


def segment_distance(point, start, end):
    along = (end[0] - start[0], end[1] - start[1])
    offset = (point[0] - start[0], point[1] - start[1])
    fraction = (offset[0] * along[0] + offset[1] * along[1]) / (along[0]**2 + along[1]**2)
    fraction = max(0.0, min(1.0, fraction))
    return math.dist(point, (start[0] + fraction * along[0], start[1] + fraction * along[1]))


def box_corner_problems(corner_radius):
    """(problems, least clearance beyond the margin): each cutting face
    of the box keeps BAY_BOX_MARGIN_MM plus the corner's radius from
    every vertex of the sharp outlines, so it cuts no rounded corner. No
    corner of the outline turns more than 90 degrees, so its rounding
    ends within its radius of the vertex."""
    problems, clearance = [], check_layout.Tightest()
    for outline, polygon, convex, concave in outline_corner_radii(corner_radius):
        turns = layout.corner_turn_angles(polygon)
        for index, vertex in enumerate(polygon):
            radius = convex if turns[index] > 0 else concave
            for face, start, end in box_cutting_faces():
                distance = segment_distance(vertex, start, end)
                clearance.update(distance - BAY_BOX_MARGIN_MM - radius,
                                 f"{outline}'s vertex {index} from the {face}")
                if distance < BAY_BOX_MARGIN_MM + radius - check_layout.TOLERANCE_MM:
                    problems.append(
                        f"the box's {face} lies {distance:.3f} from the {outline}'s corner at "
                        f"{format_point(vertex)}, less than {BAY_BOX_MARGIN_MM} plus its "
                        f"radius {radius:.2f}"
                    )
    return problems, clearance


# The strip.


def cut_bay(tray):
    """The tray's part inside the box, over its whole height."""
    (low_x, high_x), (low_y, high_y) = bay_box_plan()
    low_z = FLOOR_UNDERSIDE_Z_MM - CUT_EXTRA_MM
    box = Part.makeBox(high_x - low_x, high_y - low_y, RIM_Z_MM + CUT_EXTRA_MM - low_z,
                       App.Vector(low_x, low_y, low_z))
    bay = tray.common(box)
    require_one_valid_solid(bay, "cutting the bay")
    return bay.Solids[0]


def bay_pitch():
    return BAY_EAST_X_MM - tray_outer_west_x() + BAY_GAP_MM


def bridge(index):
    """The floor's bridge from bay index (from 0) to the next one."""
    west = BAY_EAST_X_MM + index * bay_pitch()
    north = (layout.cavity_wall_y(layout.NORTH_EDGE_Y_OF_COLUMNS_0_AND_1_MM)
             - layout.TRAY_LEDGE_WIDTH_MM)
    return Part.makeBox(BAY_GAP_MM, north - BAY_SOUTH_Y_MM, layout.TRAY_FLOOR_MM,
                        App.Vector(west, BAY_SOUTH_Y_MM, FLOOR_UNDERSIDE_Z_MM))


def join_bays(bays, bridges):
    """The bays and the bridges, which only touch, fused into one solid
    of their volume with the faces the fuse split merged."""
    pieces = bays + bridges
    if len(pieces) == 1:
        return pieces[0]
    fused = pieces[0].multiFuse(pieces[1:]).removeSplitter()
    require_one_valid_solid(fused, "joining the bays")
    require_volume("the joined bays", fused.Volume, sum(piece.Volume for piece in pieces), 1e-6)
    return fused.Solids[0]


def notch_x_centers(index):
    """The x centers of bay index's (from 0) possible notches, west to
    east, in the strip's frame before it is moved onto the bed."""
    middle = (len(BAY_FITS) + 1) / 2.0
    return [index * bay_pitch() + NOTCH_MIDDLE_X_MM + (number - middle) * NOTCH_PITCH_MM
            for number in range(1, len(BAY_FITS) + 1)]


def notch_cutters():
    """Bay k (from 1) gets its first k notches, through the floor."""
    cutters = []
    for index in range(len(BAY_FITS)):
        for x in notch_x_centers(index)[: index + 1]:
            cutters.append(Part.makeBox(
                NOTCH_WIDTH_MM,
                NOTCH_DEPTH_MM + CUT_EXTRA_MM,
                layout.TRAY_FLOOR_MM + 2.0 * CUT_EXTRA_MM,
                App.Vector(x - NOTCH_WIDTH_MM / 2.0, BAY_SOUTH_Y_MM - CUT_EXTRA_MM,
                           FLOOR_UNDERSIDE_Z_MM - CUT_EXTRA_MM),
            ))
    return cutters


def cut_notches(strip):
    """The strip with the bays' notches, checked by volume and by
    probing every place a notch could be."""
    cutters = notch_cutters()
    notched = strip.cut(Part.makeCompound(cutters))
    require_one_valid_solid(notched, "cutting the notches")
    expected = len(cutters) * NOTCH_WIDTH_MM * NOTCH_DEPTH_MM * layout.TRAY_FLOOR_MM
    require_volume("the notches", strip.Volume - notched.Volume, expected, 1e-6)
    solid = notched.Solids[0]
    for index in range(len(BAY_FITS)):
        for number, x in enumerate(notch_x_centers(index), start=1):
            point = App.Vector(x, BAY_SOUTH_Y_MM + NOTCH_DEPTH_MM / 2.0, FLOOR_UNDERSIDE_Z_MM / 2.0)
            if solid.isInside(point, INSIDE_TOLERANCE_MM, True) != (number > index + 1):
                raise SystemExit(f"error: bay {index + 1} has the wrong notches")
    return solid, len(cutters)


def on_the_bed(strip):
    """The strip moved so the floor's underside lies on z = 0 and the
    westernmost bay's southwest corner on x = y = 0."""
    moved = strip.copy()
    moved.translate(App.Vector(-tray_outer_west_x(), -BAY_SOUTH_Y_MM, -FLOOR_UNDERSIDE_Z_MM))
    return moved


def format_range(value_range):
    return f"{value_range[0]:.3f} to {value_range[1]:.3f}"


def format_point(point):
    return f"({point[0]:.3f}, {point[1]:.3f})"


def main():
    arguments = parse_arguments(script_arguments(sys.argv))
    x_range, y_range = bay_box_plan()
    corner_radius = tray_corner_radius(layout_polygon_wire(layout.tray_outer_polygon(), 0.0),
                                       DEFAULT_GAP_MM, DEFAULT_WALL_MM)
    corner_problems, corner_clearance = box_corner_problems(corner_radius)
    if corner_problems:
        raise SystemExit("error: the box cuts a rounded corner:\n  " + "\n  ".join(corner_problems))
    print(f"box:        x {format_range(x_range)}, y {format_range(y_range)}, over the tray's "
          f"height: its east face cuts the floor, the north wall and the ledge at x "
          f"{BAY_EAST_X_MM}, its south face the floor, the west wall and the ledge at y "
          f"{BAY_SOUTH_Y_MM}, each {BAY_BOX_MARGIN_MM} plus the corner's radius from every "
          f"outline vertex and beyond that by at least {corner_clearance}")
    print(f"clamp:      in every bay {common_figures(bay_fits(0, arguments.board_size))}")
    bays = []
    for index in range(len(BAY_FITS)):
        fits = bay_fits(index, arguments.board_size)
        box_problems, inside, outside = bay_box_problems(fits)
        problems = box_problems + mount_problems(fits)
        if problems:
            raise SystemExit(f"error: bay {index + 1} fails:\n  " + "\n  ".join(problems))
        bay = cut_bay(build_tray(False, None, fits).solid)
        default = " (the defaults)" if index == DEFAULT_BAY_INDEX else ""
        notches = "1 notch" if index == 0 else f"{index + 1} notches"
        print(f"bay {index + 1}:      {notches}, {bay_figures(fits)}{default}, the board "
              f"{fits.nano_width} x {fits.nano_length}, volume {bay.Volume:.3f} mm3")
        print(f"            the mount checks pass; features inside the box by at least {inside}, "
              f"outside it by at least {outside}")
        moved = bay.copy()
        moved.translate(App.Vector(index * bay_pitch(), 0.0, 0.0))
        bays.append(moved)
    bridges = [bridge(index) for index in range(len(BAY_FITS) - 1)]
    strip = join_bays(bays, bridges)
    pieces = ("one bay" if len(bays) == 1
              else f"{len(bays)} bays {BAY_GAP_MM} apart and {len(bridges)} floor bridges")
    print(f"joined:     {pieces}, one solid, volume {strip.Volume:.3f} mm3")
    strip, notch_count = cut_notches(strip)
    print(f"notches:    {notch_count}, {NOTCH_WIDTH_MM} wide and {NOTCH_DEPTH_MM} deep through the "
          f"floor, volume {strip.Volume:.3f} mm3")
    strip = on_the_bed(strip)
    mesh = export_stl(strip, arguments.stl_file)
    check_closed_mesh(arguments.stl_file)
    box = mesh.BoundBox
    print(f"print:      floor down, its underside on z = 0, {box.XLength:.2f} x "
          f"{box.YLength:.2f} x {box.ZLength:.2f} mm")
    print(f"wrote:      {arguments.stl_file} ({mesh.CountFacets} facets), one closed manifold "
          "shell; each bay takes export_clamp_tab.py's tab")


run_and_exit(main)
