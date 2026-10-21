"""Check layout.py's geometry, and DESIGN.md's figures against it.

    python3 model/kbdkid5/scripts/check_layout.py

Plain Python, no FreeCAD. The checks run in order. Each one prints a
line with the tightest margin it found; the first one that fails
prints every offending item it found, with the numbers, and the script
exits 1. A failure is a conflict in the design (or between DESIGN.md
and layout.py): fix the design, not the check.

layout.py holds the values the geometry is built from. The DESIGN_*
constants below are DESIGN.md's figures that follow from them,
transcribed independently, so a slip on either side fails here.

Every check that involves the sockets or the dowel bosses and holes
runs on both halves: the right half's sockets differ (layout.py's
module docstring), so its tray gets its own cuts, and its dowel holes
are a deeper slip fit in deeper bosses. The right half is checked in
the left half's frame, its sockets mirrored back across the mirror
line, against a tray whose outline, ledge, standoffs, magnet slots and
parking hole are the left half's there. The other checks would only
repeat the left half's numbers, so they run once.

The parts' mounts (work item 004) are layout.py's MountBoxes, the
bodies the tray adds and the voids it cuts, checked as boxes (the USB
window and the reset pin hole lie inside theirs), the nice!nano's
clamp tab and screw head (work item 009) with the bodies: inside the
tray, clear of the parts, the sockets, the standoffs (but the one the
nice!nano's bodies take in) and the joint, no void in the cavity below
the floor's top, the clamp's tab within its strain and under the PCB,
and the openings around what passes them as printed, the shell
wherever its play lets it go, and the board going in past the clamp's
foot (work item 010). The nice!nano's seat leaves the pads beside it
and the socket strips' tails under it room as printed, and the strips
on the board with the room over them up to the PCB keep clear of the
tray as printed, through their pockets in the west ledge and the east
wall (the user's request of 2026-10-20). The strips, each an insulator
over its sleeves, and their tails are nice!nano part envelopes, so
every check of the parts covers them, and the nice!nano's own pad rooms
are checked against them, the overlaps DESIGN.md names printed and any
other failing. Figures that move with the board, its strips' clearance,
the clamp's nose on it and a toothpick's reach under it, are taken
wherever the board can lie between its stops as printed, at the worst
of those places. They and the strips' corner going in and the nose
beside the foot are printed at the even split of the end faces'
measured swelling and at its worst, all of it on either face, where
the checks hold them. The wire rooms behind the parts' leads must stay clear
of all of it as printed. Those that meet the sockets, the joint or
the wire room over the nice!nano's P1.01/P1.02/P1.07 pads, which
differs between the halves, run on both halves. The nice!nano's pry slot (work item 010) is
checked in plan against everything else whatever the heights, since a
toothpick comes into it from above the floor, and a toothpick coming in
over the rim and the south ledge must get its point under the board,
in a lane of the slot clear of the west row's last tail. The mount
checks' problem functions take a layout.MountFits (the default unless
given), so export_nano_bay_test.py runs them for its test bay's fits.

Distances are in plan. Two bodies are checked against each other only
where their z ranges overlap, since one can pass over the other. The
tray is modelled as layout.py's sharp-cornered polygons: the wall
between the cavity and the outer face (whole but for the sockets' tab
pockets, since its windows and the magnet slots' cut-backs only take
more away), the ledge (cut away where DESIGN.md says and where the
sockets get notches and reliefs, the joint block in its place along
the slant) and the standoffs (with the sockets' flats). The tray
rounds its convex corners inside with the wall's inner radius (0.4 on
kbdkid4's tray), so a part within that of a convex cavity corner has
less room than reported here.
"""

import dataclasses
import itertools
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import layout

# Overlap below this counts as touching, not as a collision.
TOLERANCE_MM = 1e-6

# This check's own threshold, not DESIGN.md's: a key center, footprint
# hole or mounting drill closer than this to the outline would leave a
# sliver at the board edge.
INSIDE_OUTLINE_MINIMUM_MARGIN_MM = 0.5

# This check's own tolerance for the outline's edges against the key
# cells moved by the insets: DESIGN.md rounds both to 0.001, from
# kbdkid4's board.lp, whose north edge of columns 0 and 1, for
# example, lies at 75.485625, 0.396375 inside the cells' 75.882.
OUTLINE_ON_CELLS_TOLERANCE_MM = 0.0015

# This check's own threshold: a magnet drops into its slot from above,
# through what the wall leaves open there, with at least the least
# clearance DESIGN.md gives a slot as printed (3.1 across for the 3.0
# magnet).
MAGNET_DROP_IN_CLEARANCE_MM = 0.1

# DESIGN.md's figures, each compared within half its last digit.
DESIGN_SLANT_OFFSET_MM = 0.574
DESIGN_SLANT_LENGTH_MM = 62.51
DESIGN_SLANT_ANGLE_FROM_NORTH_DEGREES = 17.74
DESIGN_HALF_SIZE_MM = (132.4, 82.6)
DESIGN_MIRROR_LINE_X_MM = 66.199
DESIGN_HEIGHTS_Z_MM = (  # (what, z)
    ("socket bottoms", 7.48),
    ("PCB top", 11.1),
    ("plate top", 13.3),
    ("tray rim", 13.4),
)
DESIGN_TRAY_HEIGHT_MM = 14.6
DESIGN_MINIMUM_PCB_UNDERSIDE_Z_MM = 6.63
DESIGN_NANO_SIZE_MM = (18.20, 33.20)  # along x, along y
DESIGN_NANO_FROM_WEST_LEDGE_FACE_MM = 0.3
DESIGN_NANO_USB_MOUTH_BEHIND_OUTER_FACE_MM = 0.5
DESIGN_POWER_SWITCH_LEVER_PROUD_MM = {False: 2.2, True: 1.8}  # as modelled, as printed
DESIGN_BATTERY_SIZE_MM = (34.37, 51.53)  # along x, along y
DESIGN_BATTERY_FROM_STANDOFFS_MM = 0.53
DESIGN_BATTERY_FROM_LEDGE_MM = 0.36
DESIGN_BATTERY_BELOW_SOCKETS_MM = 3.37
DESIGN_BATTERY_COLUMNS = {1, 2}
DESIGN_PCB_CONNECTOR_CLEAR_ZONE_FROM_LEDGE_MM = 0.39
DESIGN_TAB_NOTCH_KEYS = {"S100", "S101", "S102", "S103"}
DESIGN_TAB_TIP_PAST_WEST_EDGE_MM = 0.231
DESIGN_TAB_TIP_FROM_CAVITY_WALL_MM = 0.169
DESIGN_TAB_POCKET_DEPTH_MM = 0.331
DESIGN_WALL_LEFT_AT_TAB_POCKETS_MM = 0.469
DESIGN_LEDGE_RELIEF_KEYS = {
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
}
DESIGN_LEDGE_RELIEF_BOTTOM_Z_MM = 6.98
DESIGN_BOTTOM_ROW_FROM_SOUTH_LEDGE_FACE_MM = 0.39
DESIGN_STANDOFF_FLATS = (
    # (key, standoff, its socket's clearance before the flat, plastic
    # the flat leaves around the bore)
    ("S141", (76.041, 43.260), 0.627, 0.927),
    ("S150", (94.774, 60.404), 0.487, 0.787),
)
DESIGN_STANDOFF_FLAT_BOTTOM_Z_MM = 6.48
# The right half's sockets (DESIGN.md, "Tray"): the thumb's tab past the
# thumb's outer edge, notched and pocketed like column 0's on the left
# (the same pocket figures), the bottom row's reliefs, and no flats.
DESIGN_RIGHT_TAB_NOTCH_KEYS = {"S163"}
DESIGN_RIGHT_TAB_TIP_PAST_THUMB_EDGE_MM = 0.231
DESIGN_RIGHT_LEDGE_RELIEF_KEYS = {"S103", "S113", "S123", "S133", "S143", "S153", "S163"}
DESIGN_RIGHT_STANDOFF_FLATS = ()
DESIGN_RIGHT_CLOSEST_SOCKET_TO_STANDOFF_MM = 1.391
# Along the slant: boss, four slots, boss.
DESIGN_BOSS_TO_SLOT_GAP_MM = 2.99
DESIGN_SLOT_TO_SLOT_GAP_MM = 2.84
DESIGN_DOWEL_PIN_SPACING_MM = 55.5
DESIGN_DOWEL_PIN_Z_MM = 4.15
# Per half, False the left one, True the right one: how close the
# dowel bosses and their fills come to a socket (S150's on both), and
# the least plastic between two of the joint's holes and slots (the
# lower dowel hole and the parking hole on both).
DESIGN_BOSSES_FROM_SOCKETS_MM = {False: 3.701, True: 1.144}
DESIGN_LEAST_PLASTIC_BETWEEN_VOIDS_MM = {False: 2.09, True: 1.80}
DESIGN_DOWEL_PIN_SLANT_Y_MM = (21.7, 74.5)
# How far the lower boss's south end and the upper boss's north end lie
# inside the outline slant's ends.
DESIGN_DOWEL_BOSSES_INSIDE_SLANT_ENDS_MM = (0.0, 0.006)
DESIGN_PARKING_PIN_PROUD_MM = 1.5
DESIGN_PARKING_BOSS_FROM_SOCKETS_MM = 1.763  # on both halves, the thumb's
DESIGN_MAGNET_SLOT_ABOVE_BED_MM = 0.5
DESIGN_PIN_OFF_HOLE_MM = 0.05  # each blade from its 3.0 hole, along footprint x
DESIGN_PULL_IN_MM = 0.2
DESIGN_DEFAULT_SLIT_MM = (0.6, 1.6)  # across the blade, along it
DESIGN_SLIT_CLEARANCE_MM = (0.2, 0.4)  # per side as modelled: across the blade, along it
# The parts' mounts (work item 004).
DESIGN_MOUNT_FROM_OTHER_PARTS_MM = 0.5  # every mount body from every part but its own
DESIGN_MOUNTS_LEAST_FROM_OTHER_PARTS_MM = 0.5  # the nice!nano's, from the battery
DESIGN_MOUNT_VOIDS_FROM_STANDOFFS_MM = 0.5
DESIGN_MOUNT_VOIDS_LEAST_FROM_STANDOFFS_MM = 9.074  # the pry slot, from the one it runs past
DESIGN_MERGED_STANDOFF_MM = (18.574, 37.782)  # the nice!nano's clamp block, foot and east wall
DESIGN_NANO_FREE_MIDDLE_X_MM = (3.105, 16.895)
# The nice!nano's bay (work item 010): the pocket, the east wall, the
# north block, at the default fits.
DESIGN_NANO_POCKET_MM = 18.7  # across, from the west ledge's face (0.6)
DESIGN_NANO_PLAY_PRINTED_MM = {"across": 0.1, "along": 0.1}
DESIGN_NANO_POCKET_LENGTH_MM = 33.56  # the foot's face to the north block's
DESIGN_NANO_END_FACE_SWELLING_MM = 0.13  # each, calipered on the first heavy duty bay
DESIGN_NANO_EAST_WALL_X_MM = (19.3, 21.5)
DESIGN_NANO_EAST_WALL_Y_MM = (38.516, 65.3)
DESIGN_NANO_EAST_WALL_TOP_Z_MM = 5.2
DESIGN_NANO_NORTH_BLOCK_X_MM = (0.4, 19.6)  # the ledge cut-away's
DESIGN_NANO_NORTH_BLOCK_Y_MM = (75.566, 75.886)
DESIGN_NANO_NORTH_BLOCK_TOP_Z_MM = 6.16
# The nice!nano's seat and the channels beside it (the user's request to
# raise the bay, 2026-10-20).
DESIGN_NANO_SEAT_TOP_Z_MM = 1.2
DESIGN_NANO_SEAT_X_MM = (3.805, 16.195)
DESIGN_NANO_SEAT_Y_MM = (42.006, 75.566)  # the foot's face to the north block's
DESIGN_NANO_CHANNELS_BEYOND_PADS_PRINTED_MM = 0.5  # the seat's edges from the pads' inner edges
DESIGN_NANO_TAILS_OVER_CHANNELS_MM = {False: 0.39, True: 0.057}  # nominal modelled, worst printed
# The socket strips on the board (Mill-Max 315-43-112-41-003000) and
# their pockets, at their worst case.
DESIGN_NANO_STRIP_X_MM = {"west": (0.625, 3.925), "east": (16.075, 19.375)}
DESIGN_NANO_STRIP_Y_MM = (41.8825, 72.9895)
DESIGN_NANO_STRIP_TOP_Z_MM = 5.213
DESIGN_NANO_STRIP_INSULATOR_BOTTOM_Z_MM = 3.41  # 0.61 over the board's top
DESIGN_NANO_STRIP_PAST_BOARD_END_MM = 0.2335  # the insulator, over the clamp's foot
DESIGN_NANO_INSULATOR_OVER_FOOT_PRINTED_MM = 0.56  # the foot's top rising as a top face
DESIGN_NANO_STRIP_POCKET_X_MM = (0.125, 19.875)  # the west ledge's face, the east wall's
DESIGN_NANO_STRIP_POCKET_Y_MM = (41.3825, 73.6595)
DESIGN_NANO_STRIPS_CLEAR_PRINTED_MM = 0.25  # of the tray up to the PCB's underside, the board west
DESIGN_NANO_STRIPS_CLEAR_WORST_SPLIT_MM = 0.19  # the same, the end faces' swelling split worst
DESIGN_NANO_STRIPS_UNDER_SOCKETS_MM = 2.267
DESIGN_NANO_STRIP_SOCKET_KEYS = {False: {"S100", "S101", "S110", "S111"}, True: {"S100", "S101"}}
# The nice!nano's screw clamp (work items 009 and 010), at the default
# press.
DESIGN_CLAMP_TAB_X_MM = (7.1, 12.9)
DESIGN_CLAMP_BLOCK_X_MM = (0.6, 21.5)
DESIGN_CLAMP_BLOCK_Y_MM = (32.716, 38.516)
DESIGN_CLAMP_FOOT_FROM_BOARD_MM = 0.11  # the foot's north face from the board's south end
DESIGN_CLAMP_FOOT_X_MM = (0.6, 19.3)
DESIGN_CLAMP_FOOT_TOP_Z_MM = 2.8
DESIGN_CLAMP_SCREW_FROM_BOARD_MM = 6.5  # the screw's axis from the board's south end
DESIGN_CLAMP_BLOCK_TOP_Z_MM = 4.8
DESIGN_CLAMP_INSERT_ROOM_PRINTED_MM = 4.6  # the bore's bottom counted 0.2 higher
DESIGN_CLAMP_INSERT_LENGTH_MM = 3.0  # M2 x 3
DESIGN_CLAMP_SCREW_REACH_MM = 2.8  # an M2 x 4 through the tab as printed
DESIGN_CLAMP_TAB_Y_MM = (32.716, 43.616)
DESIGN_CLAMP_TAB_REACH_MM = 1.5  # onto the board
DESIGN_CLAMP_NOSE_FROM_BOARD_END_MM = (0.5, 1.5)
DESIGN_CLAMP_TAB_THICKNESS_MM = {True: 1.2, False: 1.0}  # as printed, as modelled
DESIGN_CLAMP_NOSE_DEPTH_MM = 2.1  # below the plate's underside
DESIGN_CLAMP_PRESS_MM = 0.1  # as printed
DESIGN_CLAMP_ARM_MM = 5.115
DESIGN_CLAMP_STRAIN_PERCENT = {True: 0.69, False: 0.57}  # as printed, as modelled
DESIGN_CLAMP_MAXIMUM_STRAIN_PERCENT = 2.0  # PLA, the removed snap hook's
DESIGN_CLAMP_NOSE_FROM_FOOT_PRINTED_MM = 0.28
DESIGN_CLAMP_NOSE_FROM_FOOT_WORST_SPLIT_MM = 0.15  # all of the end faces' swelling on the foot
DESIGN_CLAMP_NOSE_ONTO_BOARD_PRINTED_MM = (0.18, 0.28)  # the board at its north stop, its south
DESIGN_CLAMP_NOSE_ONTO_BOARD_WORST_SPLIT_MM = 0.05  # the least, the end faces' split worst
DESIGN_CLAMP_HEAD_TOP_Z_MM = 8.0
DESIGN_CLAMP_UNDER_PCB_MM = 1.5  # the head
DESIGN_CLAMP_MINIMUM_UNDER_PCB_MM = 0.5
DESIGN_CLAMP_HEAD_FROM_SOCKETS_MM = 1.586  # S101's, on both halves
DESIGN_CLAMP_TAB_UNDER_SOCKET_MM = 1.38  # the plate as printed, lifted by the press
DESIGN_CLAMP_SOCKET_KEYS = {"S101"}  # over the tab
DESIGN_LEVER_IN_SLOT_PRINTED_MM = 0.05  # per side
DESIGN_NANO_BAR_DEPTH_MM = 0.62
DESIGN_SHELL_PLAY_MM = {"west": 0.05, "east": 0.0, "north": 0.12}  # as printed
DESIGN_SHELL_IN_CHANNEL_PRINTED_MM = {"sides": 0.0, "top": 0.1, "end": 0.0}
DESIGN_NANO_INSERTION_CLEARANCE_PRINTED_MM = 0.06  # the board's south end over the foot
DESIGN_NANO_STOPS_APART_PRINTED_MM = 33.3  # the foot's face to the north block's
DESIGN_NANO_LONGEST_BOARD_MM = 33.26  # that tilts in between them
DESIGN_NANO_LEAST_SHELL_OVERHANG_MM = 0.81  # for the board with its shell to tilt in
DESIGN_NANO_REMOVAL_CLEARANCE_PRINTED_MM = 0.061  # the south edge from the foot's face
DESIGN_NANO_REMOVAL_SLIDE_MM = 0.08  # from the north stop until the south end clears the foot
# Going in, the west strip's north top corner from the west pocket's
# north end as printed, and the steepest the board may tilt with its USB
# end on the north block before that corner meets the ledge, at the end
# faces' even split and at the worst, all of the swelling on the foot,
# where the corner keeps at least the least clearance.
DESIGN_NANO_STRIP_TILT_CLEARANCE_PRINTED_MM = 0.231
DESIGN_NANO_STRIP_TILT_STEEPEST_DEGREES = 7.82
DESIGN_NANO_STRIP_TILT_CLEARANCE_WORST_SPLIT_MM = 0.101
DESIGN_NANO_STRIP_TILT_STEEPEST_WORST_SPLIT_DEGREES = 5.02
DESIGN_NANO_STRIP_TILT_LEAST_CLEARANCE_MM = 0.1
# With all of the end faces' calipered 0.26 on the foot (only the sum
# was measured): the shell's mouth past its channel's end as printed and
# its box's corners into the window's corner rounds as printed, at its
# play across. The real shell's ends are rounded and clear the rounds.
DESIGN_SHELL_PAST_CHANNEL_ALL_ON_FOOT_MM = 0.13
DESIGN_SHELL_INTO_WINDOW_ROUND_ALL_ON_FOOT_MM = 0.018
DESIGN_RESET_PIN_HOLE_AXIS_MM = (66.199, 1.75)  # x, z
DESIGN_MOUNTS_FROM_PCB_ZONE_PRINTED_MM = 0.0  # the nice!nano's east wall
DESIGN_WIRE_ROOM_BEHIND_LEADS_MM = 3.0
DESIGN_WIRE_ROOM_OVER_PADS_MM = 3.0
DESIGN_WIRE_ROOM_LEAST_CLEARANCE_PRINTED_MM = 0.147
# The nice!nano's pad rooms its own socket strips' insulators reach
# into, per half (False the left one, in the left half's frame), (room,
# strip): (how far in plan, decimals). The B+ and B- rooms meet the
# insulators' north ends, the P1.01/P1.02/P1.07 room the B- row's
# insulator (0.31 if the render's insets moved together), and whether
# the P1 pads get wired is an open question to the user. Any other
# overlap fails.
DESIGN_NANO_ROOMS_INTO_STRIPS_MM = {
    False: {("over the B- pad", "west"): (0.1235, 4), ("over the B+ pad", "east"): (0.1235, 4),
            ("over the P1.01/P1.02/P1.07 pads", "west"): (0.44, 2)},
    True: {("over the B+ pad", "west"): (0.1235, 4), ("over the B- pad", "east"): (0.1235, 4),
           ("over the P1.01/P1.02/P1.07 pads", "east"): (0.44, 2)},
}
# The nice!nano's pry slot and recess (work item 010).
DESIGN_PRY_SLOT_X_MM = (1.6, 6.6)
DESIGN_PRY_SLOT_Y_MM = (32.716, 42.006)  # through the clamp's block and foot
DESIGN_PRY_SLOT_FROM_LEDGE_MM = 1.0
DESIGN_PRY_SLOT_FROM_INSERT_BORE_MM = 1.8
DESIGN_PRY_RECESS_Y_MM = (32.716, 44.116)
DESIGN_PRY_RECESS_UNDER_BOARD_MM = 2.0
DESIGN_PRY_RECESS_BOTTOM_Z_MM = 0.0  # the floor's top, the seat left out
DESIGN_PRY_RECESS_FLOOR_UNDER_MM = 1.2  # the whole floor
DESIGN_PRY_TOOTHPICK_ANGLE_DEGREES = 18.0  # the least, over the rim, the board north
DESIGN_PRY_TOOTHPICK_REACH_PRINTED_MM = 1.68  # its point under the board, the board north
DESIGN_PRY_TOOTHPICK_REACH_WORST_SPLIT_MM = 1.55  # the same, the end faces' split worst
DESIGN_PRY_TOOTHPICK_LANE_X_MM = (3.605, 6.4)  # as printed, east of the west row's last tail
DESIGN_PRY_LAST_TAIL_FROM_BOARD_END_MM = 0.969  # the west row's, its south edge

# Only the sum of the bay's end faces' swelling was calipered (layout.py's
# NANO_POCKET_END_FACES_SWELLING_MM). EVEN_SPLIT holds the north block's
# share the pocket is sized for, half the sum, and WORST_SPLITS the ends
# of its range, all of the sum on the foot or all on the block. Over
# the whole range the board's places lie between its stops at those two
# ends, which nano_board_places() takes as its extreme places, and the
# other figures that depend on the split move linearly with it, so
# taking both ends finds the worst.
EVEN_SPLIT = (layout.NANO_POCKET_END_FACE_SWELLING_MM,)
WORST_SPLITS = (0.0, layout.NANO_POCKET_END_FACES_SWELLING_MM)


class CheckFailure(Exception):
    pass


def require_figure(label, computed, stated, decimals):
    """A DESIGN.md figure, stated to `decimals` decimals, against the
    layout's: (ok, description)."""
    tolerance = 0.5 * 10.0**-decimals + TOLERANCE_MM
    ok = abs(computed - stated) <= tolerance
    shown = round(computed, decimals + 2) + 0.0  # no "-0.00"
    return ok, f"{label} {shown:.{decimals + 2}f} (DESIGN.md {stated})"


def require_figure_for_all(label, computed_values, stated, decimals):
    """require_figure on the value farthest from the stated one."""
    if not computed_values:
        return False, f"{label}: nothing to measure (DESIGN.md {stated})"
    worst = max(computed_values, key=lambda value: abs(value - stated))
    return require_figure(label, worst, stated, decimals)


def failed(figures):
    return [text for ok, text in figures if not ok]


def joined(figures):
    return ", ".join(text for _, text in figures)


def fail_on(problems, what):
    if problems:
        raise CheckFailure(f"{what}:\n  " + "\n  ".join(problems))


# Plane geometry.


def vector_between(start, end):
    return (end[0] - start[0], end[1] - start[1])


def cross(first, second):
    return first[0] * second[1] - first[1] * second[0]


def dot(first, second):
    return first[0] * second[0] + first[1] * second[1]


def edges(polygon):
    count = len(polygon)
    return [(polygon[index], polygon[(index + 1) % count]) for index in range(count)]


def point_segment_distance(point, start, end):
    segment = vector_between(start, end)
    length_squared = dot(segment, segment)
    if length_squared == 0.0:
        return math.dist(point, start)
    parameter = dot(vector_between(start, point), segment) / length_squared
    parameter = max(0.0, min(1.0, parameter))
    closest = (start[0] + parameter * segment[0], start[1] + parameter * segment[1])
    return math.dist(point, closest)


def segments_cross(first_start, first_end, second_start, second_end):
    """Whether two segments cross at a point inside both."""
    first = vector_between(first_start, first_end)
    second = vector_between(second_start, second_end)
    side_of_second_start = cross(first, vector_between(first_start, second_start))
    side_of_second_end = cross(first, vector_between(first_start, second_end))
    side_of_first_start = cross(second, vector_between(second_start, first_start))
    side_of_first_end = cross(second, vector_between(second_start, first_end))
    return (
        side_of_second_start * side_of_second_end < 0.0
        and side_of_first_start * side_of_first_end < 0.0
    )


def segment_distance(first_start, first_end, second_start, second_end):
    if segments_cross(first_start, first_end, second_start, second_end):
        return 0.0
    return min(
        point_segment_distance(first_start, second_start, second_end),
        point_segment_distance(first_end, second_start, second_end),
        point_segment_distance(second_start, first_start, first_end),
        point_segment_distance(second_end, first_start, first_end),
    )


def boundary_distance(first_polygon, second_polygon):
    return min(
        segment_distance(*first_edge, *second_edge)
        for first_edge in edges(first_polygon)
        for second_edge in edges(second_polygon)
    )


def point_boundary_distance(point, polygon):
    return min(point_segment_distance(point, *edge) for edge in edges(polygon))


def point_in_polygon(point, polygon):
    """Ray casting; a point on the boundary may land on either side."""
    inside = False
    for start, end in edges(polygon):
        if (start[1] > point[1]) != (end[1] > point[1]):
            fraction = (point[1] - start[1]) / (end[1] - start[1])
            if point[0] < start[0] + fraction * (end[0] - start[0]):
                inside = not inside
    return inside


def signed_point_distance(point, polygon):
    """Distance to the polygon's boundary, negative outside."""
    distance = point_boundary_distance(point, polygon)
    if distance <= TOLERANCE_MM or point_in_polygon(point, polygon):
        return distance
    return -distance


def is_convex(polygon):
    turns = [
        cross(vector_between(before, corner), vector_between(corner, after))
        for before, corner, after in zip(
            polygon[-1:] + polygon[:-1], polygon, polygon[1:] + polygon[:1]
        )
    ]
    return all(turn >= -TOLERANCE_MM for turn in turns) or all(
        turn <= TOLERANCE_MM for turn in turns
    )


def separating_axis_gap(first_polygon, second_polygon):
    """The widest gap between two convex polygons' projections onto any
    edge normal: positive when separated, its negative the overlap."""
    best = -math.inf
    for polygon in (first_polygon, second_polygon):
        for start, end in edges(polygon):
            edge = vector_between(start, end)
            length = math.hypot(*edge)
            axis = (edge[1] / length, -edge[0] / length)
            first_values = [dot(point, axis) for point in first_polygon]
            second_values = [dot(point, axis) for point in second_polygon]
            gap = max(
                min(second_values) - max(first_values),
                min(first_values) - max(second_values),
            )
            best = max(best, gap)
    return best


def convex_separation(first_polygon, second_polygon):
    """Clearance between two convex polygons: the distance between them,
    zero when they touch, negative (by how much) when they overlap."""
    gap = separating_axis_gap(first_polygon, second_polygon)
    if gap < -TOLERANCE_MM:
        return gap
    return boundary_distance(first_polygon, second_polygon)


def circle_separation(center, radius, convex_polygon):
    """Clearance between a circle and a convex polygon, negative when
    they overlap."""
    distance = point_boundary_distance(center, convex_polygon)
    if point_in_polygon(center, convex_polygon):
        distance = -distance
    return distance - radius


def containment_margin(inner_polygon, outer_polygon):
    """How far a convex polygon stays inside a simple one: its distance
    to the outer boundary, negative (by how much) when it pokes out."""
    corner_depths = [signed_point_distance(corner, outer_polygon) for corner in inner_polygon]
    if min(corner_depths) < -TOLERANCE_MM:
        return min(corner_depths)
    poking_in = [
        point_boundary_distance(vertex, inner_polygon)
        for vertex in outer_polygon
        if point_in_polygon(vertex, inner_polygon)
        and point_boundary_distance(vertex, inner_polygon) > TOLERANCE_MM
    ]
    if poking_in:
        return -max(poking_in)
    return boundary_distance(inner_polygon, outer_polygon)


def clip_to_half_plane(polygon, normal, limit):
    """The part of a convex polygon where dot(point, normal) <= limit."""
    clipped = []
    for start, end in edges(polygon):
        start_value = dot(start, normal) - limit
        end_value = dot(end, normal) - limit
        if start_value <= 0.0:
            clipped.append(start)
        if start_value * end_value < 0.0:
            fraction = start_value / (start_value - end_value)
            clipped.append(
                (
                    start[0] + fraction * (end[0] - start[0]),
                    start[1] + fraction * (end[1] - start[1]),
                )
            )
    return tuple(clipped)


def half_planes(polygon):
    """(normal, limit) of a counter-clockwise convex polygon's sides: a
    point inside has dot(point, normal) <= limit for each."""
    planes = []
    for start, end in edges(polygon):
        side = vector_between(start, end)
        length = math.hypot(*side)
        normal = (side[1] / length, -side[0] / length)
        planes.append((normal, dot(start, normal)))
    return planes


def split_cells(cells, normal, limit):
    """Convex cells cut in two along the line dot(point, normal) =
    limit, slivers dropped."""
    opposite = (-normal[0], -normal[1])
    halves = []
    for cell in cells:
        halves.append(clip_to_half_plane(cell, normal, limit))
        halves.append(clip_to_half_plane(cell, opposite, -limit))
    return [half for half in halves if len(half) >= 3 and polygon_area(half) > TOLERANCE_MM]


def polygon_area(polygon):
    return abs(layout.polygon_signed_area(polygon))


def polygon_centroid(polygon):
    """The vertices' mean: inside a convex polygon."""
    count = len(polygon)
    return (sum(x for x, _ in polygon) / count, sum(y for _, y in polygon) / count)


def box_polygon(envelope):
    (low_x, high_x), (low_y, high_y) = envelope.x_range, envelope.y_range
    return ((low_x, low_y), (high_x, low_y), (high_x, high_y), (low_x, high_y))


def ranges_overlap(first, second):
    return min(first[1], second[1]) - max(first[0], second[0]) > TOLERANCE_MM


def subtract_ranges(kept_range, removed_ranges):
    """What is left of a range with others taken out, as ranges."""
    remaining = [kept_range]
    for removed_low, removed_high in removed_ranges:
        split = []
        for low, high in remaining:
            split.append((low, min(high, removed_low)))
            split.append((max(low, removed_high), high))
        remaining = [(low, high) for low, high in split if high - low > TOLERANCE_MM]
    return remaining


def describe_envelope(envelope):
    return f"{envelope.part} {envelope.piece}"


def describe_piece(label, z_range):
    return f"{label} (z {z_range[0]:.2f} to {z_range[1]:.2f})"


def describe_extent(polygon):
    xs = [x for x, _ in polygon]
    ys = [y for _, y in polygon]
    return f"x {min(xs):.3f} to {max(xs):.3f}, y {min(ys):.3f} to {max(ys):.3f}"


class Tightest:
    """The smallest margin seen, and where."""

    def __init__(self):
        self.value = math.inf
        self.where = "nothing checked"

    def update(self, value, where):
        if value < self.value:
            self.value = value
            self.where = where

    def __str__(self):
        return f"{self.value:.3f} ({self.where})"


# The tray and the sockets as obstacles.


def socket_z_range():
    return (layout.SOCKET_BOTTOM_Z_MM, layout.PCB_UNDERSIDE_Z_MM)


def standoff_z_range():
    return (0.0, layout.STANDOFF_HEIGHT_MM)


def ledge_z_range():
    return (0.0, layout.PCB_UNDERSIDE_Z_MM)


def wall_z_range():
    return (layout.FLOOR_UNDERSIDE_Z_MM, layout.TRAY_RIM_Z_MM)


def half_label(right):
    """What starts a check's line for the right half."""
    return "right half: " if right else ""


def socket_footprints(right=False):
    """(key name, convex polygon) for every socket polygon on the given
    half, in the left half's frame."""
    return [
        (name, polygon)
        for name in layout.KEY_CENTERS_MM
        for polygon in layout.socket_polygons_on_half(name, right)
    ]


def ring_pieces(outer_polygon, inner_polygon):
    """The quadrilaterals between two offsets of the outline, one per
    outline edge: piece i lies between the polygons' edges i."""
    count = len(outer_polygon)
    return [
        (
            outer_polygon[index],
            outer_polygon[(index + 1) % count],
            inner_polygon[(index + 1) % count],
            inner_polygon[index],
        )
        for index in range(count)
    ]


def cutaway_cut(cutaway):
    """A ledge cut-away as layout.py cuts it."""
    try:
        return layout.ledge_cutaway_cut(cutaway)
    except ValueError as error:
        raise CheckFailure(str(error))


def cut_piece(label, polygon, z_range, cuts):
    """(label, convex polygon, z range) of what the cuts leave of a
    convex tray piece standing over z_range: the piece split along the
    sides of every cut reaching into it, each cell keeping z_range less
    the cuts over it."""
    rectangles = [(cut, layout.tray_cut_polygon(cut)) for cut in cuts]
    reaching = [
        (cut, rectangle)
        for cut, rectangle in rectangles
        if convex_separation(polygon, rectangle) < -TOLERANCE_MM
    ]
    cells = [polygon]
    for _cut, rectangle in reaching:
        for normal, limit in half_planes(rectangle):
            cells = split_cells(cells, normal, limit)
    pieces = []
    for cell in cells:
        middle = polygon_centroid(cell)
        removed = [
            cut.z_range for cut, rectangle in reaching if point_in_polygon(middle, rectangle)
        ]
        pieces.extend((label, cell, remaining) for remaining in subtract_ranges(z_range, removed))
    return pieces


def ledge_pieces(right=False, fits=layout.DEFAULT_MOUNT_FITS):
    """(label, convex polygon, z range) of the given half's ledge and
    joint block as cut: DESIGN.md's cut-aways, the nice!nano's over the
    board the fits size, the west socket strip's pocket, and the sockets'
    notches, pockets and reliefs taken out."""
    cuts = [cutaway_cut(cutaway) for cutaway in layout.ledge_cutaways(fits)]
    cuts.append(layout.nano_strip_ledge_pocket(fits))
    cuts.extend(layout.all_socket_tray_cuts(right))
    rings = ring_pieces(layout.tray_cavity_polygon(), layout.ledge_inner_polygon())
    pieces = []
    for index, ring_piece in enumerate(rings):
        if index == layout.SLANT_EDGE_INDEX:
            label = "joint block"
        else:
            label = f"ledge along outline edge {index}"
        pieces.extend(cut_piece(label, ring_piece, ledge_z_range(), cuts))
    return pieces


def wall_pieces(right=False):
    """(label, convex polygon, z range) of the given half's wall between
    the cavity and the outer face, the sockets' tab pockets taken out of
    it."""
    pockets = [cut for cut in layout.all_socket_tray_cuts(right) if cut.cuts_wall]
    rings = ring_pieces(layout.tray_outer_polygon(), layout.tray_cavity_polygon())
    pieces = []
    for index, ring_piece in enumerate(rings):
        label = f"wall along outline edge {index}"
        pieces.extend(cut_piece(label, ring_piece, wall_z_range(), pockets))
    return pieces


def standoff_bands(center, right=False):
    """(z range, flats) of a standoff's height bands on the given half,
    with the sockets' flats cut into each band."""
    flats = [
        flat
        for flat in layout.all_socket_standoff_flats(right)
        if flat.standoff_center == center
    ]
    bounds = sorted(set(standoff_z_range()) | {z for flat in flats for z in flat.z_range})
    return [
        (
            (low, high),
            [
                flat
                for flat in flats
                if flat.z_range[0] <= low + TOLERANCE_MM and high <= flat.z_range[1] + TOLERANCE_MM
            ],
        )
        for low, high in zip(bounds, bounds[1:])
    ]


def standoff_clearance(center, flats, convex_polygon):
    """The clearance between a convex polygon and a standoff with flats,
    bounded from below: the larger of the full circle's and, for each
    flat, how far the polygon lies beyond the flat's plane. Exact
    without flats, and where the polygon's nearest point faces a flat's
    middle, as the rule places each flat."""
    bound = circle_separation(center, layout.STANDOFF_DIAMETER_MM / 2.0, convex_polygon)
    for flat in flats:
        nearest = min(
            dot(vector_between(center, corner), flat.toward) for corner in convex_polygon
        )
        bound = max(bound, nearest - flat.plane_distance)
    return bound


def socket_clearances(obstacles, minimum, right=False):
    """(problems, tightest) of every socket polygon on the given half
    against (label, convex polygon, z range) obstacles wherever their z
    ranges overlap."""
    problems = []
    tightest = Tightest()
    for name, socket in socket_footprints(right):
        for label, polygon, z_range in obstacles:
            if not ranges_overlap(z_range, socket_z_range()):
                continue
            clearance = convex_separation(socket, polygon)
            where = f"{name}'s socket and the {describe_piece(label, z_range)}"
            tightest.update(clearance, where)
            if clearance < minimum - TOLERANCE_MM:
                problems.append(f"{where}: {clearance:.3f}, less than {minimum}")
    return problems, tightest


# The checks, in order.


def outline_shape_problems(polygon):
    """What keeps a polygon from being a closed counter-clockwise one
    with no zero-length edge and no doubling back."""
    problems = [f"only {len(polygon)} vertices"] if len(polygon) < 3 else []
    for index, (start, end) in enumerate(edges(polygon)):
        if math.dist(start, end) <= TOLERANCE_MM:
            problems.append(f"edge {index} has no length")
    for index, turn in enumerate(layout.corner_turn_angles(polygon)):
        if abs(abs(turn) - math.pi) < 1e-9:
            problems.append(f"the outline doubles back at vertex {index} {polygon[index]}")
    area = layout.polygon_signed_area(polygon)
    if area <= 0.0:
        problems.append(f"signed area {area:.3f}: not counter-clockwise")
    return problems


def non_adjacent_edge_problems(polygon):
    """(problems, tightest) over the pairs of edges that share no
    vertex: any that touch or cross."""
    all_edges = edges(polygon)
    count = len(all_edges)
    problems = []
    tightest = Tightest()
    for first, second in itertools.combinations(range(count), 2):
        if second - first == 1 or (first == 0 and second == count - 1):
            continue  # adjacent
        distance = segment_distance(*all_edges[first], *all_edges[second])
        tightest.update(distance, f"edges {first} and {second}")
        if distance <= TOLERANCE_MM:
            problems.append(f"edges {first} and {second} touch or cross")
    return problems, tightest


def check_outline():
    polygon = layout.OUTLINE_VERTICES_MM
    edge_problems, tightest = non_adjacent_edge_problems(polygon)
    fail_on(
        outline_shape_problems(polygon) + edge_problems,
        "the outline is not a simple closed polygon",
    )
    width = max(x for x, _ in polygon) - min(x for x, _ in polygon)
    height = max(y for _, y in polygon) - min(y for _, y in polygon)
    figures = [
        require_figure("width", width, DESIGN_HALF_SIZE_MM[0], 1),
        require_figure("height", height, DESIGN_HALF_SIZE_MM[1], 1),
        require_figure(
            "mirror line x", layout.RIGHT_HALF_MIRROR_X_MM, DESIGN_MIRROR_LINE_X_MM, 3
        ),
    ]
    fail_on(failed(figures), "the half's size or mirror line differs from DESIGN.md")
    area = layout.polygon_signed_area(polygon)
    return (
        f"outline:   simple, closed, counter-clockwise, {len(polygon)} corners, "
        f"{area:.1f} mm2, closest non-adjacent edges {tightest}; " + joined(figures)
    )


def key_cells():
    """(x range, y range) of every key's 19.05 square cell."""
    half = layout.KEY_PITCH_MM / 2.0
    return [
        ((x - half, x + half), (y - half, y + half)) for x, y in layout.KEY_CENTERS_MM.values()
    ]


def horizontal_edge_target(start, end):
    """(what, the edge's y moved by its inset, the cell y values it may
    meet) of a horizontal outline edge. The outline runs
    counter-clockwise, so a south edge runs east."""
    x_range = (min(start[0], end[0]), max(start[0], end[0]))
    y_ranges = [y_range for cell_x, y_range in key_cells() if ranges_overlap(cell_x, x_range)]
    if not y_ranges:
        return "a cell", start[1], []
    if end[0] > start[0]:
        lowest = min(low for low, _ in y_ranges)
        what = "the lowest cell's bottom moved in by the south inset"
        return what, start[1] - layout.CELL_INSET_SOUTH_MM, [lowest]
    highest = max(high for _, high in y_ranges)
    what = "the highest cell's top moved in by the north inset"
    return what, start[1] + layout.CELL_INSET_NORTH_MM, [highest]


def vertical_edge_target(start, end, outline_x_range):
    """(what, the edge's x moved by its inset, the cell x values it may
    meet) of a vertical outline edge: the west and east edges are inset,
    the risers between steps lie on a cell's side."""
    y_range = (min(start[1], end[1]), max(start[1], end[1]))
    x_ranges = [x_range for x_range, cell_y in key_cells() if ranges_overlap(cell_y, y_range)]
    if not x_ranges:
        return "a cell", start[0], []
    if abs(start[0] - outline_x_range[0]) <= TOLERANCE_MM:
        westmost = min(low for low, _ in x_ranges)
        what = "the westmost cell's west side moved in by the west inset"
        return what, start[0] - layout.CELL_INSET_WEST_MM, [westmost]
    if abs(start[0] - outline_x_range[1]) <= TOLERANCE_MM:
        eastmost = max(high for _, high in x_ranges)
        what = "the eastmost cell's east side moved in by the east inset"
        return what, start[0] + layout.CELL_INSET_EAST_MM, [eastmost]
    return "a cell's west or east side", start[0], [x for x_range in x_ranges for x in x_range]


def outline_edge_target(start, end, outline_x_range):
    if abs(start[1] - end[1]) <= TOLERANCE_MM:
        return horizontal_edge_target(start, end)
    if abs(start[0] - end[0]) <= TOLERANCE_MM:
        return vertical_edge_target(start, end, outline_x_range)
    return None


def check_outline_on_cells():
    """Every outline edge but the slant lies on the key cells moved in
    by DESIGN.md's insets (the slant has its own check)."""
    outline = layout.OUTLINE_VERTICES_MM
    outline_x_range = (min(x for x, _ in outline), max(x for x, _ in outline))
    problems = []
    worst_error, worst_where = 0.0, "no edge"
    for index, (start, end) in enumerate(edges(outline)):
        if index == layout.SLANT_EDGE_INDEX:
            continue
        where = f"edge {index} {start} to {end}"
        target = outline_edge_target(start, end, outline_x_range)
        if target is None:
            problems.append(f"{where} is neither the slant nor parallel to an axis")
            continue
        what, coordinate, candidates = target
        if not candidates:
            problems.append(f"{where} has no key cell beside it")
            continue
        error = min(abs(coordinate - candidate) for candidate in candidates)
        if error > worst_error:
            worst_error, worst_where = error, where
        if error > OUTLINE_ON_CELLS_TOLERANCE_MM:
            problems.append(f"{where} lies {error:.4f} off {what}")
    fail_on(problems, "the outline does not follow the key cells and DESIGN.md's insets")
    return (
        f"cells:     every outline edge but the slant on the key cells moved in by the insets, "
        f"off by {worst_error:.4f} at most ({worst_where})"
    )


def check_slant():
    thumb_corner = layout.key_cell_top_right_corner(layout.THUMB_KEY_CENTER_MM)
    column_5_corner = layout.key_cell_top_right_corner(
        layout.KEY_CENTERS_MM[layout.TOP_ROW_KEY_OF_COLUMN_5]
    )
    inset = (-layout.CELL_INSET_EAST_MM, -layout.CELL_INSET_NORTH_MM)
    problems = []
    worst_end_error = 0.0
    for label, corner, end in (
        ("south", thumb_corner, layout.SLANT_SOUTH_END_MM),
        ("north", column_5_corner, layout.SLANT_NORTH_END_MM),
    ):
        expected = (corner[0] + inset[0], corner[1] + inset[1])
        error = math.dist(expected, end)
        worst_end_error = max(worst_end_error, error)
        if error > 0.0005:
            problems.append(
                f"the {label} end {end} is {error:.4f} from the cell corner {corner} "
                f"moved in by the insets, {expected}"
            )
    corner_line = vector_between(thumb_corner, column_5_corner)
    slant = layout.slant_vector()
    sine = cross(corner_line, slant) / (math.hypot(*corner_line) * math.hypot(*slant))
    if abs(sine) > 1e-9:
        problems.append(f"the slant is not parallel to the corner to corner line (sine {sine:.2e})")
    offset = -dot(
        vector_between(thumb_corner, layout.SLANT_SOUTH_END_MM), layout.slant_outward_normal()
    )
    angle = math.degrees(math.atan2(-slant[0], slant[1]))
    figures = [
        require_figure(
            "offset inside the corner to corner line", offset, DESIGN_SLANT_OFFSET_MM, 3
        ),
        require_figure("length", layout.slant_length(), DESIGN_SLANT_LENGTH_MM, 2),
        require_figure("degrees from north", angle, DESIGN_SLANT_ANGLE_FROM_NORTH_DEGREES, 2),
    ]
    fail_on(problems + failed(figures), "the slant does not run as DESIGN.md states")
    return (
        f"slant:     ends at the cell corners less the insets (off by {worst_end_error:.4f} at "
        f"most), " + joined(figures)
    )


def check_keys_and_holes():
    outline = layout.OUTLINE_VERTICES_MM
    minimum = INSIDE_OUTLINE_MINIMUM_MARGIN_MM
    problems = []
    centers = Tightest()
    holes = Tightest()
    hole_count = 0
    for name, center in layout.KEY_CENTERS_MM.items():
        margin = signed_point_distance(center, outline)
        centers.update(margin, name)
        if margin < minimum:
            problems.append(f"{name}'s center {center} is {margin:.3f} inside the outline")
        for hole_center, diameter in layout.footprint_holes(center):
            hole_count += 1
            margin = signed_point_distance(hole_center, outline) - diameter / 2.0
            where = f"{name}'s {diameter} hole at ({hole_center[0]:.3f}, {hole_center[1]:.3f})"
            holes.update(margin, where)
            if margin < minimum:
                problems.append(f"{where} is {margin:.3f} inside the outline")
    fail_on(problems, f"keys or holes closer than {minimum} to the outline")
    return (
        f"keys:      {len(layout.KEY_CENTERS_MM)} centers inside the outline, tightest "
        f"{centers}; {hole_count} footprint holes, tightest edge {holes}"
    )


def footprint_extents(key_center, polygon):
    """((low, high) along footprint x, (low, high) along footprint y)
    of a polygon around a key's footprint origin."""
    origin = layout.footprint_point(key_center, (0.0, 0.0))
    extents = []
    for unit in ((1.0, 0.0), (0.0, 1.0)):
        axis = vector_between(origin, layout.footprint_point(key_center, unit))
        values = [dot(vector_between(origin, point), axis) for point in polygon]
        extents.append((min(values), max(values)))
    return extents


def pin_hole_problems():
    """Where a blade (the STEP model's) and its 3.0 hole (the package's)
    are not a pair: not a 3.0 hole, or off along footprint y."""
    problems = []
    holes = dict(layout.CHOC_FOOTPRINT_HOLES_MM)
    pairs = zip(layout.CHOC_PIN_CENTERS_MM, layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM)
    for pin, hole in pairs:
        if holes.get(hole) != 3.0:
            problems.append(f"the pin hole at {hole} is not one of the footprint's 3.0 holes")
        if abs(pin[1] - hole[1]) > TOLERANCE_MM:
            problems.append(f"the blade at {pin} is off its hole at {hole} along footprint y")
    if len(layout.CHOC_PIN_CENTERS_MM) != len(layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM):
        problems.append("the blades and the pin holes differ in number")
    return problems


def blade_slit_margins():
    """(slit sizes, blade margins) of every key's blades in their
    default slits, each as (across the blade, along it): the blade's
    thickness along footprint x, its slit's width likewise."""
    width = layout.default_slit_width(DESIGN_PULL_IN_MM)
    length = layout.default_slit_length(DESIGN_PULL_IN_MM)
    sizes = []
    margins = []
    for center in layout.KEY_CENTERS_MM.values():
        slits = layout.pin_slits(center, length, width)
        for pin, slit in zip(layout.CHOC_PIN_CENTERS_MM, slits):
            blade = layout.footprint_rectangle(
                center, pin, layout.CHOC_PIN_BLADE_THICKNESS_MM, layout.CHOC_PIN_BLADE_WIDTH_MM
            )
            slit_extents = footprint_extents(center, slit)
            blade_extents = footprint_extents(center, blade)
            sizes.append(tuple(high - low for low, high in slit_extents))
            margins.append(tuple(
                min(blade_low - slit_low, slit_high - blade_high)
                for (slit_low, slit_high), (blade_low, blade_high)
                in zip(slit_extents, blade_extents)
            ))
    return sizes, margins


def check_switch_pins():
    fail_on(pin_hole_problems(), "the blades against the footprint's pin holes")
    offsets = [
        abs(pin[0] - hole[0])
        for pin, hole in zip(layout.CHOC_PIN_CENTERS_MM, layout.CHOC_FOOTPRINT_PIN_HOLE_CENTERS_MM)
    ]
    sizes, margins = blade_slit_margins()
    figures = [
        require_figure_for_all("blades from their 3.0 holes", offsets, DESIGN_PIN_OFF_HOLE_MM, 2),
        require_figure_for_all(
            "default slits across", [size[0] for size in sizes], DESIGN_DEFAULT_SLIT_MM[0], 1
        ),
        require_figure_for_all(
            "along", [size[1] for size in sizes], DESIGN_DEFAULT_SLIT_MM[1], 1
        ),
        require_figure_for_all(
            "blade clearance per side across",
            [margin[0] for margin in margins],
            DESIGN_SLIT_CLEARANCE_MM[0],
            1,
        ),
        require_figure_for_all(
            "along", [margin[1] for margin in margins], DESIGN_SLIT_CLEARANCE_MM[1], 1
        ),
    ]
    fail_on(failed(figures), "the blades or their slits off DESIGN.md's figures")
    return f"pins:      {len(margins)} blades, " + joined(figures)


def drill_switch_problems(drill, radius):
    """(problems, tightest from the holes, tightest from the sockets) of
    a mounting drill against every key's footprint holes and socket."""
    problems = []
    from_holes = Tightest()
    from_sockets = Tightest()
    for name, center in layout.KEY_CENTERS_MM.items():
        for hole_center, diameter in layout.footprint_holes(center):
            clearance = math.dist(drill, hole_center) - radius - diameter / 2.0
            from_holes.update(clearance, f"drill {drill} and {name}'s {diameter} hole")
            if clearance < -TOLERANCE_MM:
                problems.append(
                    f"drill {drill} overlaps {name}'s {diameter} hole by {-clearance:.3f}"
                )
    for name, polygon in socket_footprints():
        clearance = circle_separation(drill, radius, polygon)
        from_sockets.update(clearance, f"drill {drill} and {name}'s socket")
        if clearance < -TOLERANCE_MM:
            problems.append(f"drill {drill} overlaps {name}'s socket by {-clearance:.3f}")
    return problems, from_holes, from_sockets


def check_mounting_drills():
    outline = layout.OUTLINE_VERTICES_MM
    radius = layout.MOUNTING_DRILL_DIAMETER_MM / 2.0
    problems = []
    inside = Tightest()
    from_holes = Tightest()
    from_sockets = Tightest()
    for drill in layout.MOUNTING_DRILL_CENTERS_MM:
        margin = signed_point_distance(drill, outline) - radius
        inside.update(margin, f"drill {drill}")
        if margin < INSIDE_OUTLINE_MINIMUM_MARGIN_MM:
            problems.append(f"drill {drill} is {margin:.3f} inside the outline")
        switch_problems, holes, sockets = drill_switch_problems(drill, radius)
        problems.extend(switch_problems)
        from_holes.update(holes.value, holes.where)
        from_sockets.update(sockets.value, sockets.where)
    fail_on(problems, "mounting drills off the board or on a switch")
    return (
        f"drills:    {len(layout.MOUNTING_DRILL_CENTERS_MM)} inside the outline, tightest edge "
        f"{inside}; clear of the switch holes by {from_holes}, of the sockets by {from_sockets}"
    )


def check_heights():
    computed = (
        layout.SOCKET_BOTTOM_Z_MM,
        layout.PCB_TOP_Z_MM,
        layout.PLATE_TOP_Z_MM,
        layout.TRAY_RIM_Z_MM,
    )
    figures = [
        require_figure(what, z, stated, 2)
        for (what, stated), z in zip(DESIGN_HEIGHTS_Z_MM, computed)
    ]
    tray_height = layout.TRAY_RIM_Z_MM - layout.FLOOR_UNDERSIDE_Z_MM
    figures.append(require_figure("tray height", tray_height, DESIGN_TRAY_HEIGHT_MM, 1))
    figures.append(
        require_figure(
            "lowest PCB underside",
            layout.MINIMUM_PCB_UNDERSIDE_Z_MM,
            DESIGN_MINIMUM_PCB_UNDERSIDE_Z_MM,
            2,
        )
    )
    problems = failed(figures)
    if layout.PCB_UNDERSIDE_Z_MM < layout.MINIMUM_PCB_UNDERSIDE_Z_MM:
        problems.append(
            f"the PCB underside at {layout.PCB_UNDERSIDE_Z_MM} is below the "
            f"{layout.MINIMUM_PCB_UNDERSIDE_Z_MM:.2f} the battery needs under the sockets"
        )
    fail_on(problems, "the heights differ from DESIGN.md's table")
    return f"heights:   PCB underside {layout.PCB_UNDERSIDE_Z_MM}, " + joined(figures)


def nano_figures():
    west_ledge_face_x = min(x for x, _ in layout.OUTLINE_VERTICES_MM) + layout.ledge_reach()
    nano = layout.NANO_BOARD
    north_outer_face_y = layout.outer_face_y(layout.NORTH_EDGE_Y_OF_COLUMNS_0_AND_1_MM)
    return [
        require_figure(
            "nice!nano width", nano.x_range[1] - nano.x_range[0], DESIGN_NANO_SIZE_MM[0], 2
        ),
        require_figure(
            "nice!nano length", nano.y_range[1] - nano.y_range[0], DESIGN_NANO_SIZE_MM[1], 1
        ),
        require_figure(
            "nice!nano from the west ledge's face",
            nano.x_range[0] - west_ledge_face_x,
            DESIGN_NANO_FROM_WEST_LEDGE_FACE_MM,
            1,
        ),
        require_figure(
            "USB mouth behind the north wall's outer face",
            north_outer_face_y - layout.NANO_USB_SHELL.y_range[1],
            DESIGN_NANO_USB_MOUTH_BEHIND_OUTER_FACE_MM,
            1,
        ),
    ]


def power_switch_figures():
    north_edge_y = layout.NORTH_EDGE_Y_OF_COLUMN_2_MM
    return [
        require_figure(
            "power switch's north face past the cavity wall",
            layout.POWER_SWITCH_BODY.y_range[1] - layout.cavity_wall_y(north_edge_y),
            0.0,
            3,
        ),
        require_figure(
            "lever proud of the outer face",
            layout.POWER_SWITCH_LEVER.y_range[1] - layout.outer_face_y(north_edge_y),
            DESIGN_POWER_SWITCH_LEVER_PROUD_MM[False],
            1,
        ),
        require_figure(
            "as printed", lever_proud_as_printed(), DESIGN_POWER_SWITCH_LEVER_PROUD_MM[True], 1
        ),
    ]


def lever_proud_as_printed():
    """The lever's tip past the outer face as printed: the swollen wall
    pushes the snug body south, and the outer face swells north."""
    north_edge_y = layout.NORTH_EDGE_Y_OF_COLUMN_2_MM
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    lever_past_body = layout.POWER_SWITCH_LEVER.y_range[1] - layout.POWER_SWITCH_BODY.y_range[1]
    tip = layout.cavity_wall_y(north_edge_y) - swelling + lever_past_body
    return tip - (layout.outer_face_y(north_edge_y) + swelling)


def battery_figures():
    battery = layout.BATTERY
    return [
        require_figure(
            "battery width", battery.x_range[1] - battery.x_range[0], DESIGN_BATTERY_SIZE_MM[0], 2
        ),
        require_figure(
            "battery length", battery.y_range[1] - battery.y_range[0], DESIGN_BATTERY_SIZE_MM[1], 2
        ),
    ]


def check_part_figures():
    figures = nano_figures() + power_switch_figures() + battery_figures()
    fail_on(failed(figures), "parts placed off DESIGN.md's figures")
    return "figures:   " + joined(figures)


def check_part_containment():
    cavity = layout.tray_cavity_polygon()
    outer = layout.tray_outer_polygon()
    problems = []
    in_cavity = Tightest()
    in_outer = Tightest()
    for envelope in layout.part_envelopes():
        if envelope.containment == layout.PROUD:
            continue
        inside_cavity = envelope.containment == layout.CAVITY
        region = cavity if inside_cavity else outer
        margin = containment_margin(box_polygon(envelope), region)
        (in_cavity if inside_cavity else in_outer).update(margin, describe_envelope(envelope))
        if margin < -TOLERANCE_MM:
            boundary = "cavity wall" if inside_cavity else "outer face"
            problems.append(
                f"{describe_envelope(envelope)} pokes {-margin:.3f} past the {boundary}"
            )
    fail_on(problems, "parts outside the tray")
    return (
        f"parts:     inside the cavity wall by {in_cavity}; through the wall, inside its outer "
        f"face by {in_outer}"
    )


def part_ledge_problems(pieces):
    """(problems, tightest) of every part against the ledge pieces."""
    problems = []
    tightest = Tightest()
    for envelope in layout.part_envelopes():
        box = box_polygon(envelope)
        for label, piece, z_range in pieces:
            if not ranges_overlap(envelope.z_range, z_range):
                continue
            clearance = convex_separation(box, piece)
            where = f"{describe_envelope(envelope)} and the {describe_piece(label, z_range)}"
            tightest.update(clearance, where)
            if clearance < -TOLERANCE_MM:
                problems.append(
                    f"{describe_envelope(envelope)} reaches {-clearance:.3f} into the "
                    f"{describe_piece(label, z_range)} ({describe_extent(piece)})"
                )
    return problems, tightest


def ledge_clearance(envelope, pieces):
    return min(
        convex_separation(box_polygon(envelope), piece)
        for _label, piece, z_range in pieces
        if ranges_overlap(envelope.z_range, z_range)
    )


def check_part_ledge():
    pieces = ledge_pieces()
    broken = [
        f"the {describe_piece(label, z_range)} is not convex"
        for label, piece, z_range in pieces
        if not is_convex(piece)
    ]
    fail_on(broken, "the ledge model is broken")
    problems, tightest = part_ledge_problems(pieces)
    cut_away_for = ", ".join(cutaway.part for cutaway in layout.ledge_cutaways())
    fail_on(problems, f"parts in the ledge (DESIGN.md cuts it away only over the {cut_away_for})")
    figures = [
        require_figure(
            "battery from the ledge",
            ledge_clearance(layout.BATTERY, pieces),
            DESIGN_BATTERY_FROM_LEDGE_MM,
            2,
        ),
        require_figure(
            "PCB connector clear zone from the ledge",
            ledge_clearance(layout.PCB_CONNECTOR_CLEAR_ZONE, pieces),
            DESIGN_PCB_CONNECTOR_CLEAR_ZONE_FROM_LEDGE_MM,
            2,
        ),
    ]
    fail_on(failed(figures), "ledge clearances off DESIGN.md's figures")
    return f"ledge:     parts clear of the ledge and the joint block by {tightest}; " + joined(
        figures
    )


def check_part_standoffs():
    radius = layout.STANDOFF_DIAMETER_MM / 2.0
    problems = []
    tightest = Tightest()
    for envelope in layout.part_envelopes():
        if not ranges_overlap(envelope.z_range, standoff_z_range()):
            continue
        for center in layout.MOUNTING_DRILL_CENTERS_MM:
            clearance = circle_separation(center, radius, box_polygon(envelope))
            where = f"{describe_envelope(envelope)} and the standoff at {center}"
            tightest.update(clearance, where)
            if clearance < -TOLERANCE_MM:
                problems.append(f"{where} overlap by {-clearance:.3f}")
    fail_on(problems, "parts on the standoffs")
    battery = min(
        circle_separation(center, radius, box_polygon(layout.BATTERY))
        for center in layout.MOUNTING_DRILL_CENTERS_MM
    )
    ok, text = require_figure(
        "battery from the standoffs", battery, DESIGN_BATTERY_FROM_STANDOFFS_MM, 2
    )
    fail_on([] if ok else [text], "the battery's standoff clearance is off DESIGN.md's figure")
    return f"standoffs: parts clear by {tightest}; {text}"


def check_parts_apart():
    problems = []
    tightest = Tightest()
    for first, second in itertools.combinations(layout.part_envelopes(), 2):
        if first.part == second.part or not ranges_overlap(first.z_range, second.z_range):
            continue
        clearance = convex_separation(box_polygon(first), box_polygon(second))
        where = f"{describe_envelope(first)} and {describe_envelope(second)}"
        tightest.update(clearance, where)
        if clearance < -TOLERANCE_MM:
            problems.append(f"{where} overlap by {-clearance:.3f}")
    fail_on(problems, "parts on each other (the PCB connector's clear zone counts as a part)")
    return f"apart:     parts and the PCB connector's clear zone clear of each other by {tightest}"


def check_part_sockets(right=False):
    problems = []
    tightest = Tightest()
    for envelope in layout.part_envelopes():
        if not ranges_overlap(envelope.z_range, socket_z_range()):
            continue
        for name, polygon in socket_footprints(right):
            clearance = convex_separation(box_polygon(envelope), polygon)
            where = f"{describe_envelope(envelope)} and {name}'s socket"
            tightest.update(clearance, where)
            if clearance < -TOLERANCE_MM:
                problems.append(f"{where} overlap by {-clearance:.3f}")
    fail_on(problems, "parts under the sockets at their height")
    highest_other = max(
        envelope.z_range[1]
        for envelope in layout.part_envelopes()
        if not ranges_overlap(envelope.z_range, socket_z_range())
    )
    return (
        f"sockets:   {half_label(right)}parts reaching their height clear in plan by {tightest}; "
        f"every other part stays {layout.SOCKET_BOTTOM_Z_MM - highest_other:.3f} below them"
    )


def check_battery(right=False):
    battery = box_polygon(layout.BATTERY)
    covering_keys = sorted(
        {
            name
            for name, polygon in socket_footprints(right)
            if convex_separation(battery, polygon) < -TOLERANCE_MM
        }
    )
    clearance = layout.SOCKET_BOTTOM_Z_MM - layout.BATTERY.z_range[1]
    ok, clearance_text = require_figure(
        "below them", clearance, DESIGN_BATTERY_BELOW_SOCKETS_MM, 2
    )
    problems = [] if ok else [clearance_text]
    if not covering_keys:
        problems.append("no socket lies over the battery")
    columns = {int(name[2]) for name in covering_keys if name != layout.THUMB_KEY_NAME}
    if columns != DESIGN_BATTERY_COLUMNS:
        problems.append(
            f"it lies under the sockets of columns {sorted(columns)}, DESIGN.md says columns "
            f"{sorted(DESIGN_BATTERY_COLUMNS)}"
        )
    fail_on(problems, "the battery does not sit under the sockets as DESIGN.md states")
    return (
        f"battery:   {half_label(right)}under the sockets of {', '.join(covering_keys)}, "
        f"{clearance_text}"
    )


def design_socket_cut_keys(right):
    """(tab notch keys, ledge relief keys, standoff flats as (key,
    standoff)) of the given half, as DESIGN.md states them."""
    if right:
        flats = {(key, center) for key, center, _, _ in DESIGN_RIGHT_STANDOFF_FLATS}
        return DESIGN_RIGHT_TAB_NOTCH_KEYS, DESIGN_RIGHT_LEDGE_RELIEF_KEYS, flats
    flats = {(key, center) for key, center, _, _ in DESIGN_STANDOFF_FLATS}
    return DESIGN_TAB_NOTCH_KEYS, DESIGN_LEDGE_RELIEF_KEYS, flats


def declared_set_problems(right=False):
    """Where the sockets layout.py gives notches, reliefs and flats on
    the given half differ from DESIGN.md's."""
    design_notches, design_reliefs, design_flats = design_socket_cut_keys(right)
    declared = (
        ("tab notches", set(layout.socket_tab_notch_keys(right)), design_notches),
        ("ledge reliefs", set(layout.socket_ledge_relief_keys(right)), design_reliefs),
        (
            "standoff flats",
            {(key, center) for center, key in layout.socket_standoff_flat_declarations(right)},
            design_flats,
        ),
    )
    return [
        f"{what} for {sorted(in_layout)} in layout.py, for {sorted(in_design)} in DESIGN.md"
        for what, in_layout, in_design in declared
        if in_layout != in_design
    ]


def uncut_declaration_problems(right=False):
    """Sockets named for a cut that kbdkid4's rule does not make on the
    given half."""
    problems = []
    for key in layout.socket_tab_notch_keys(right):
        if not any(not cut.cuts_wall for cut in layout.socket_tab_cuts(key, right)):
            problems.append(f"{key}'s tab tip is not near enough the ledge for the rule's notch")
    for key in layout.socket_ledge_relief_keys(right):
        if not layout.socket_ledge_reliefs(key, right):
            problems.append(f"{key}'s socket is not near enough the ledge for the rule's relief")
    for center, key in layout.socket_standoff_flat_declarations(right):
        if center not in layout.MOUNTING_DRILL_CENTERS_MM:
            problems.append(f"{key}'s flat is on {center}, where there is no mounting drill")
        elif not layout.socket_standoff_flats(center, key, right):
            problems.append(
                f"{key}'s socket is not near enough the standoff at {center} for a flat"
            )
    return problems


def flat_plastic(flat):
    """The plastic a flat leaves between it and the insert bore."""
    return flat.plane_distance - layout.STANDOFF_BORE_DIAMETER_MM / 2.0


def thin_flat_problems(right=False):
    minimum = layout.STANDOFF_RELIEF_MINIMUM_WALL_MM
    return [
        f"the {flat.label} on the standoff at {flat.standoff_center} leaves "
        f"{flat_plastic(flat):.3f} around the bore, less than {minimum}"
        for flat in layout.all_socket_standoff_flats(right)
        if flat_plastic(flat) < minimum - TOLERANCE_MM
    ]


def tab_figures(right=False):
    keys = layout.socket_tab_notch_keys(right)
    tips = [layout.socket_tab_tip_on_edge(key, right) for key in keys]
    past_edge = [past for _index, _along, past in tips]
    pockets = [cut for key in keys for cut in layout.socket_tab_cuts(key, right) if cut.cuts_wall]
    depths = [cut.across_range[1] - layout.TRAY_GAP_MM for cut in pockets]
    if right:
        past_figure = require_figure_for_all(
            "tab tip past the thumb's outer edge",
            past_edge,
            DESIGN_RIGHT_TAB_TIP_PAST_THUMB_EDGE_MM,
            3,
        )
    else:
        past_figure = require_figure_for_all(
            "tab tips past the west edge", past_edge, DESIGN_TAB_TIP_PAST_WEST_EDGE_MM, 3
        )
    return [
        past_figure,
        require_figure_for_all(
            "from the cavity wall",
            [layout.TRAY_GAP_MM - past for past in past_edge],
            DESIGN_TAB_TIP_FROM_CAVITY_WALL_MM,
            3,
        ),
        require_figure_for_all("pockets", depths, DESIGN_TAB_POCKET_DEPTH_MM, 3),
        require_figure_for_all(
            "wall left",
            [layout.TRAY_WALL_MM - depth for depth in depths],
            DESIGN_WALL_LEFT_AT_TAB_POCKETS_MM,
            3,
        ),
    ]


def south_ledge_face_y(x):
    """The south ledge's inner face at x: the south outline edge there
    (running east, the outline being counter-clockwise) moved in by the
    ledge's reach."""
    for start, end in edges(layout.OUTLINE_VERTICES_MM):
        if start[1] == end[1] and start[0] < x < end[0]:
            return start[1] + layout.ledge_reach()
    raise CheckFailure(f"no south outline edge under x {x}")


def relief_figures(right=False):
    reliefs = [
        cut
        for key in layout.socket_ledge_relief_keys(right)
        for cut in layout.socket_ledge_reliefs(key, right)
    ]
    bottom_row = [layout.column_key_name(column, 3) for column in range(6)]
    bottom_row.append(layout.THUMB_KEY_NAME)
    above_face = []
    for key in bottom_row:
        center = layout.KEY_CENTERS_MM[key]
        polygons = layout.socket_polygons_on_half(key, right)
        lowest = min(y for polygon in polygons for _, y in polygon)
        above_face.append(lowest - south_ledge_face_y(center[0]))
    return [
        require_figure_for_all(
            "relief bottoms z",
            [cut.z_range[0] for cut in reliefs],
            DESIGN_LEDGE_RELIEF_BOTTOM_Z_MM,
            2,
        ),
        require_figure_for_all(
            "bottom row's sockets above the south ledge's face",
            above_face,
            DESIGN_BOTTOM_ROW_FROM_SOUTH_LEDGE_FACE_MM,
            2,
        ),
    ]


def closest_socket_to_standoffs(right=False):
    radius = layout.STANDOFF_DIAMETER_MM / 2.0
    return min(
        circle_separation(center, radius, polygon)
        for center in layout.MOUNTING_DRILL_CENTERS_MM
        for _name, polygon in socket_footprints(right)
    )


def flat_figures(right=False):
    if right:
        return [
            require_figure(
                "sockets from the standoffs, without flats",
                closest_socket_to_standoffs(right),
                DESIGN_RIGHT_CLOSEST_SOCKET_TO_STANDOFF_MM,
                3,
            )
        ]
    radius = layout.STANDOFF_DIAMETER_MM / 2.0
    figures = []
    for key, center, stated_clearance, stated_plastic in DESIGN_STANDOFF_FLATS:
        polygons = layout.socket_polygons_on_half(key)
        clearance = min(circle_separation(center, radius, polygon) for polygon in polygons)
        plastic = min(flat_plastic(flat) for flat in layout.socket_standoff_flats(center, key))
        figures.append(
            require_figure(f"{key}'s socket from its standoff", clearance, stated_clearance, 3)
        )
        figures.append(require_figure("plastic left by the flat", plastic, stated_plastic, 3))
    bottoms = [flat.z_range[0] for flat in layout.all_socket_standoff_flats()]
    figures.append(
        require_figure_for_all("flat bottoms z", bottoms, DESIGN_STANDOFF_FLAT_BOTTOM_Z_MM, 2)
    )
    return figures


def check_socket_tray_rules(right=False):
    """The sockets layout.py gives notches, reliefs and flats on the
    given half are DESIGN.md's, kbdkid4's rule cuts each, no flat leaves
    the bore too thin, and the cuts come out at DESIGN.md's figures."""
    fail_on(
        declared_set_problems(right)
        + uncut_declaration_problems(right)
        + thin_flat_problems(right),
        f"{half_label(right)}the sockets' notches, reliefs or flats are off",
    )
    figures = tab_figures(right) + relief_figures(right) + flat_figures(right)
    fail_on(failed(figures), f"{half_label(right)}the sockets' cuts off DESIGN.md's figures")
    return "cuts:      " + half_label(right) + joined(figures)


def check_socket_ledge(right=False):
    minimum = layout.LEDGE_RELIEF_CLEARANCE_MM
    problems, tightest = socket_clearances(ledge_pieces(right), minimum, right)
    fail_on(
        problems,
        f"{half_label(right)}sockets closer than {minimum} to the ledge or the joint block, as cut",
    )
    return (
        f"ledge:     {half_label(right)}sockets clear of the ledge and the joint block, as cut, "
        f"by {tightest}"
    )


def check_socket_wall(right=False):
    minimum = layout.LEDGE_NOTCH_CLEARANCE_MM
    problems, tightest = socket_clearances(wall_pieces(right), minimum, right)
    fail_on(problems, f"{half_label(right)}sockets closer than {minimum} to the wall, as pocketed")
    return f"wall:      {half_label(right)}sockets clear of the wall, as pocketed, by {tightest}"


def check_socket_standoffs(right=False):
    minimum = layout.STANDOFF_RELIEF_CLEARANCE_MM
    problems = []
    tightest = Tightest()
    for center in layout.MOUNTING_DRILL_CENTERS_MM:
        for z_range, flats in standoff_bands(center, right):
            if not ranges_overlap(z_range, socket_z_range()):
                continue
            for name, socket in socket_footprints(right):
                clearance = standoff_clearance(center, flats, socket)
                standoff = describe_piece(f"standoff at {center}", z_range)
                where = f"{name}'s socket and the {standoff}"
                if flats:
                    where += f" with {len(flats)} flat{'s' if len(flats) > 1 else ''}"
                tightest.update(clearance, where)
                if clearance < minimum - TOLERANCE_MM:
                    problems.append(f"{where}: {clearance:.3f}, less than {minimum}")
    fail_on(
        problems, f"{half_label(right)}sockets closer than {minimum} to the standoffs, as flattened"
    )
    return (
        f"posts:     {half_label(right)}sockets clear of the standoffs, as flattened, by "
        f"{tightest}"
    )


def joint_features(right=False):
    """(label, plan polygon, z range) of the magnet slots and the half's
    dowel bosses."""
    return magnet_slots() + dowel_bosses(right)


def magnet_slots():
    return [
        (
            f"magnet slot at {along} along the slant",
            layout.magnet_slot_polygon(along),
            layout.magnet_slot_z_range(),
        )
        for along in layout.MAGNET_ALONGS_MM
    ]


def dowel_bosses(right=False):
    return [
        (
            f"dowel boss at {along} along the slant",
            layout.dowel_boss_polygon(along, right),
            layout.dowel_boss_z_range(),
        )
        for along in layout.DOWEL_PIN_ALONGS_MM
    ]


def boss_fills(right=False):
    """(label, plan polygon, z range) of the plastic filling the
    crevices beside the bosses, up to the PCB's underside."""
    z_range = (0.0, layout.PCB_UNDERSIDE_Z_MM)
    return [
        ("upper dowel boss's fill", layout.upper_boss_fill_polygon(right), z_range),
        ("parking boss's fill", layout.parking_boss_fill_polygon(), z_range),
    ]


def joint_voids(right=False):
    """(label, plan polygon, z range) of the half's holes and slots in
    the joint and the thumb's wall."""
    dowel_holes = [
        (
            f"dowel hole at {along} along the slant",
            layout.dowel_hole_polygon(along, right),
            layout.horizontal_hole_z_range(
                layout.DOWEL_PIN_Z_MM, layout.dowel_hole_diameter(right)
            ),
        )
        for along in layout.DOWEL_PIN_ALONGS_MM
    ]
    parking = (
        "parking hole",
        layout.parking_hole_polygon(),
        layout.horizontal_hole_z_range(layout.PARKING_HOLE_Z_MM, layout.PARKING_HOLE_DIAMETER_MM),
    )
    return magnet_slots() + dowel_holes + [parking]


def dowel_boss_inside_slant_ends():
    """(lower, upper): how far the lower boss's south end and the upper
    boss's north end lie inside the outline slant's ends."""
    half_width = layout.DOWEL_BOSS_DIAMETER_MM / 2.0
    lower = min(layout.DOWEL_PIN_ALONGS_MM) - half_width
    upper = layout.slant_length() - (max(layout.DOWEL_PIN_ALONGS_MM) + half_width)
    return lower, upper


def dowel_pin_figures():
    first_along, second_along = layout.DOWEL_PIN_ALONGS_MM
    slant_ys = [layout.slant_point(along, 0.0)[1] for along in (first_along, second_along)]
    lower_inside, upper_inside = dowel_boss_inside_slant_ends()
    return [
        require_figure(
            "dowel pin spacing along the slant",
            second_along - first_along,
            DESIGN_DOWEL_PIN_SPACING_MM,
            1,
        ),
        require_figure("lower dowel pin's slant y", slant_ys[0], DESIGN_DOWEL_PIN_SLANT_Y_MM[0], 1),
        require_figure("upper dowel pin's slant y", slant_ys[1], DESIGN_DOWEL_PIN_SLANT_Y_MM[1], 1),
        require_figure(
            "lower boss inside the slant's south end",
            lower_inside,
            DESIGN_DOWEL_BOSSES_INSIDE_SLANT_ENDS_MM[0],
            3,
        ),
        require_figure(
            "upper boss inside its north end",
            upper_inside,
            DESIGN_DOWEL_BOSSES_INSIDE_SLANT_ENDS_MM[1],
            3,
        ),
        require_figure("dowel pin height", layout.DOWEL_PIN_Z_MM, DESIGN_DOWEL_PIN_Z_MM, 2),
        require_figure(
            "midway between the bed and the PCB",
            (layout.FLOOR_UNDERSIDE_Z_MM + layout.PCB_UNDERSIDE_Z_MM) / 2.0,
            DESIGN_DOWEL_PIN_Z_MM,
            2,
        ),
        require_figure(
            "parked pin proud of the wall",
            layout.DOWEL_PIN_LENGTH_MM - layout.PARKING_PIN_INSERTION_MM,
            DESIGN_PARKING_PIN_PROUD_MM,
            1,
        ),
        require_figure(
            "print swelling per side",
            layout.PRINT_SWELLING_PER_SIDE_MM,
            DESIGN_PULL_IN_MM,
            1,
        ),
    ]


def features_along_slant():
    """(along, kind, plan polygon) of the dowel bosses and magnet slots,
    in their order along the slant."""
    slots = [
        (along, "slot", layout.magnet_slot_polygon(along)) for along in layout.MAGNET_ALONGS_MM
    ]
    bosses = [
        (along, "boss", layout.dowel_boss_polygon(along)) for along in layout.DOWEL_PIN_ALONGS_MM
    ]
    return sorted(slots + bosses)


def joint_gaps():
    """(boss to slot gaps, slot to slot gaps): the plan clearance
    between each pair of neighbours along the slant among the dowel
    bosses and magnet slots."""
    features = features_along_slant()
    to_bosses = []
    between_slots = []
    for (_, first_kind, first), (_, second_kind, second) in zip(features, features[1:]):
        gap = convex_separation(first, second)
        (between_slots if first_kind == second_kind else to_bosses).append(gap)
    return to_bosses, between_slots


def magnet_figures():
    to_bosses, between_slots = joint_gaps()
    return [
        require_figure_for_all(
            "slots from the bosses along the slant", to_bosses, DESIGN_BOSS_TO_SLOT_GAP_MM, 2
        ),
        require_figure_for_all("slots apart", between_slots, DESIGN_SLOT_TO_SLOT_GAP_MM, 2),
        require_figure(
            "magnet slot bottom above the bed",
            layout.MAGNET_SLOT_BOTTOM_Z_MM - layout.FLOOR_UNDERSIDE_Z_MM,
            DESIGN_MAGNET_SLOT_ABOVE_BED_MM,
            1,
        ),
    ]


def check_joint_figures():
    kinds = [kind for _, kind, _ in features_along_slant()]
    if kinds[0] != "boss" or kinds[-1] != "boss":
        raise CheckFailure(f"the magnets do not sit between the pins: {kinds} along the slant")
    figures = dowel_pin_figures() + magnet_figures()
    fail_on(failed(figures), "the joint off DESIGN.md's figures")
    return "joint:     " + joined(figures)


def printed(modelled):
    """A hole's or slot's size once the print has swollen into it."""
    return modelled - 2.0 * layout.PRINT_SWELLING_PER_SIDE_MM


def magnet_slot_opening_problems(opening_across, wall_left):
    """Where a magnet would not drop into its slot as printed: the slot
    or the opening above it too tight for it with
    MAGNET_DROP_IN_CLEARANCE_MM, the slot not open toward the cavity,
    or the cut-back through the wall."""
    clearance = MAGNET_DROP_IN_CLEARANCE_MM
    thickness = layout.MAGNET_THICKNESS_MM
    diameter = layout.MAGNET_DIAMETER_MM
    needed_across = thickness + clearance
    needed_along = diameter + clearance
    across = printed(layout.MAGNET_SLOT_ACROSS_MM)
    along = printed(layout.MAGNET_SLOT_ALONG_MM)
    problems = []
    if across < needed_across - TOLERANCE_MM:
        problems.append(
            f"the slot prints {across:.3f} across, the {thickness} magnet needs {needed_across:.3f}"
        )
    if along < needed_along - TOLERANCE_MM:
        problems.append(
            f"the slot prints {along:.3f} along the slant, the {diameter} magnet needs "
            f"{needed_along:.3f}"
        )
    if printed(opening_across) < needed_across - TOLERANCE_MM:
        problems.append(
            f"the opening above each slot prints {printed(opening_across):.3f} across, the "
            f"{thickness} magnet needs {needed_across:.3f}"
        )
    inner_side = layout.magnet_slot_outward_range()[0]
    block_inner_face = layout.JOINT_FACE_OUTWARD_MM - layout.JOINT_BLOCK_THICKNESS_MM
    if inner_side > block_inner_face + TOLERANCE_MM:
        problems.append(
            f"the slot's inner side lies {inner_side - block_inner_face:.3f} out of the block's "
            "inner face, which leaves a wall there"
        )
    if wall_left <= TOLERANCE_MM:
        problems.append(f"the cut-back leaves {wall_left:.3f} of wall at the face")
    return problems


def check_magnet_slot_opening():
    """Each slot runs through the block to its inner face, and above the
    block the wall would overhang its outer side, so the wall's inner
    face is cut back to the slot: as printed, the slot and the opening
    above it must take the magnet with MAGNET_DROP_IN_CLEARANCE_MM."""
    cutback = layout.magnet_wall_cutback_outward()
    low, high = layout.magnet_slot_opening_outward_range(cutback)
    low_uncut, high_uncut = layout.magnet_slot_opening_outward_range(layout.TRAY_GAP_MM)
    wall_left = layout.JOINT_FACE_OUTWARD_MM - cutback
    fail_on(
        magnet_slot_opening_problems(high - low, wall_left),
        "the magnets cannot drop into their slots",
    )
    return (
        f"slots:     {layout.MAGNET_SLOT_ACROSS_MM:.1f} x {layout.MAGNET_SLOT_ALONG_MM:.1f} "
        f"modelled, {printed(layout.MAGNET_SLOT_ACROSS_MM):.1f} x "
        f"{printed(layout.MAGNET_SLOT_ALONG_MM):.1f} printed, for the "
        f"{layout.MAGNET_THICKNESS_MM} x {layout.MAGNET_DIAMETER_MM} magnet, open toward the "
        f"cavity and above the block {high - low:.3f} across ({high_uncut - low_uncut:.3f} "
        f"without the cut-back), the cut-back leaving {wall_left:.3f} of wall from z "
        f"{layout.JOINT_BLOCK_TOP_Z_MM} to {layout.MAGNET_WALL_CUTBACK_TOP_Z_MM}"
    )


def check_joint_inside(right=False):
    outer = layout.tray_outer_polygon()
    problems = []
    tightest = Tightest()
    for label, polygon, _z_range in joint_features(right) + boss_fills(right):
        margin = containment_margin(polygon, outer)
        tightest.update(margin, label)
        if margin < -TOLERANCE_MM:
            problems.append(f"the {label} pokes {-margin:.3f} past the tray's outer face")
    fail_on(problems, f"{half_label(right)}joint features outside the tray")
    return (
        f"joint:     {half_label(right)}magnet slots, dowel bosses and their fills inside the "
        f"tray's outer face by {tightest}"
    )


def joint_tray_problems(label, polygon, z_range, right=False, sockets_too=True):
    """(problems, tightest from the sockets, tightest from the
    standoffs) of one joint feature on the given half. Plastic standing
    under the PCB keeps the ledge's clearance from the sockets, as the
    ledge and the parking boss do. Without sockets_too (a slot, empty
    space) only the standoffs count."""
    minimum = layout.LEDGE_RELIEF_CLEARANCE_MM
    standoff_radius = layout.STANDOFF_DIAMETER_MM / 2.0
    problems = []
    from_sockets = Tightest()
    from_standoffs = Tightest()
    if sockets_too and ranges_overlap(z_range, socket_z_range()):
        for name, socket in socket_footprints(right):
            clearance = convex_separation(polygon, socket)
            from_sockets.update(clearance, f"{label} and {name}'s socket")
            if clearance < minimum - TOLERANCE_MM:
                problems.append(
                    f"the {label} comes {clearance:.3f} from {name}'s socket, less than {minimum}"
                )
    if ranges_overlap(z_range, standoff_z_range()):
        for center in layout.MOUNTING_DRILL_CENTERS_MM:
            clearance = circle_separation(center, standoff_radius, polygon)
            from_standoffs.update(clearance, f"{label} and the standoff at {center}")
            if clearance < -TOLERANCE_MM:
                problems.append(
                    f"the {label} overlaps the standoff at {center} by {-clearance:.3f}"
                )
    return problems, from_sockets, from_standoffs


def fill_problems(right):
    """A fill that came out no triangle: the boss's inner corner at or
    past the ledge's face, or the dowel boss's side past the parking
    boss's."""
    return [
        f"the {label} is no triangle (area {layout.polygon_signed_area(polygon):.4f})"
        for label, polygon, _z_range in boss_fills(right)
        if layout.polygon_signed_area(polygon) <= TOLERANCE_MM
    ]


def check_joint_clearances(right=False):
    problems = fill_problems(right)
    from_sockets = Tightest()
    from_standoffs = Tightest()
    plastic = dowel_bosses(right) + boss_fills(right)
    features = [(feature, True) for feature in plastic] + [
        (slot, False) for slot in magnet_slots()
    ]
    for (label, polygon, z_range), sockets_too in features:
        feature_problems, sockets, standoffs = joint_tray_problems(
            label, polygon, z_range, right, sockets_too
        )
        problems.extend(feature_problems)
        from_sockets.update(sockets.value, sockets.where)
        from_standoffs.update(standoffs.value, standoffs.where)
    ok, text = require_figure(
        "bosses from the sockets", from_sockets.value, DESIGN_BOSSES_FROM_SOCKETS_MM[right], 3
    )
    if not ok:
        problems.append(text)
    fail_on(
        problems,
        f"{half_label(right)}joint plastic too close to the sockets, or the joint in the "
        "standoffs' way",
    )
    return (
        f"joint:     {half_label(right)}{text} ({from_sockets.where}), clear of the "
        f"standoffs by {from_standoffs}"
    )


def check_joint_voids(right=False):
    """Every two of the joint's holes and slots keep
    JOINT_LEAST_PLASTIC_BETWEEN_VOIDS_MM of plastic between them in plan
    wherever their heights overlap."""
    minimum = layout.JOINT_LEAST_PLASTIC_BETWEEN_VOIDS_MM
    problems = []
    tightest = Tightest()
    for first, second in itertools.combinations(joint_voids(right), 2):
        first_label, first_polygon, first_z = first
        second_label, second_polygon, second_z = second
        if not ranges_overlap(first_z, second_z):
            continue
        plastic = convex_separation(first_polygon, second_polygon)
        where = f"{first_label} and {second_label}"
        tightest.update(plastic, where)
        if plastic < minimum - TOLERANCE_MM:
            problems.append(f"the {where} leave {plastic:.3f} of plastic, less than {minimum}")
    ok, text = require_figure(
        "least plastic between the voids",
        tightest.value,
        DESIGN_LEAST_PLASTIC_BETWEEN_VOIDS_MM[right],
        2,
    )
    if not ok:
        problems.append(text)
    fail_on(problems, f"{half_label(right)}the joint's holes and slots too close")
    return f"voids:     {half_label(right)}{text} ({tightest.where})"


def parking_boss_problems(right):
    """(problems, figure text) of the parking hole's boss and its fill
    against the sockets: they stand to the PCB's underside like the
    ledge, so they keep the ledge's clearance from them."""
    minimum = layout.LEDGE_RELIEF_CLEARANCE_MM
    bodies = (
        ("parking boss", layout.parking_boss_polygon()),
        ("parking boss's fill", layout.parking_boss_fill_polygon()),
    )
    problems = []
    tightest = Tightest()
    for label, body in bodies:
        for name, polygon in socket_footprints(right):
            clearance = convex_separation(body, polygon)
            tightest.update(clearance, f"the {label} and {name}'s socket")
            if clearance < minimum - TOLERANCE_MM:
                problems.append(f"the {label} comes {clearance:.3f} from {name}'s socket")
    ok, text = require_figure(
        "the boss from the sockets", tightest.value, DESIGN_PARKING_BOSS_FROM_SOCKETS_MM, 3
    )
    return problems + ([] if ok else [text]), f"{text}, {tightest.where}"


def check_parking_hole(right=False):
    """The parking hole runs through the thumb's east wall, its magnet's
    seat no wider than the hole itself (one teardrop serves both). The
    hole is kept clear in plan of the sockets (the thumb's above all)
    and the standoffs (the one at (114.141, 19.765) above all) at any
    height, and of the joint's other voids by check_joint_voids(). Its
    boss may merge with the tray's other plastic, but keeps the ledge's
    clearance from the sockets."""
    hole = layout.parking_hole_polygon()
    east_edge_low_y = 0.0
    east_edge_high_y = layout.SLANT_SOUTH_END_MM[1]
    low_y = min(y for _, y in hole)
    high_y = max(y for _, y in hole)
    wall_margin = min(low_y - east_edge_low_y, east_edge_high_y - high_y)
    problems = []
    if wall_margin < -TOLERANCE_MM:
        problems.append(
            f"the hole spans y {low_y:.3f} to {high_y:.3f}, past the thumb's east edge "
            f"(y {east_edge_low_y} to {east_edge_high_y})"
        )
    if layout.PARKING_MAGNET_SEAT_DIAMETER_MM > layout.PARKING_HOLE_DIAMETER_MM + TOLERANCE_MM:
        problems.append(
            f"the magnet's seat ({layout.PARKING_MAGNET_SEAT_DIAMETER_MM:.2f}) is wider than the "
            f"hole ({layout.PARKING_HOLE_DIAMETER_MM:.2f}), which is cut in one diameter"
        )
    from_sockets = Tightest()
    for name, polygon in socket_footprints(right):
        from_sockets.update(convex_separation(hole, polygon), f"{name}'s socket")
    from_standoffs = Tightest()
    for center in layout.MOUNTING_DRILL_CENTERS_MM:
        from_standoffs.update(
            circle_separation(center, layout.STANDOFF_DIAMETER_MM / 2.0, hole),
            f"the standoff at {center}",
        )
    for tightest in (from_sockets, from_standoffs):
        if tightest.value < -TOLERANCE_MM:
            problems.append(f"the parking hole overlaps {tightest.where} by {-tightest.value:.3f}")
    boss_problems, boss_text = parking_boss_problems(right)
    fail_on(problems + boss_problems, f"{half_label(right)}the parking hole or its boss collides")
    return (
        f"parking:   {half_label(right)}hole {layout.PARKING_HOLE_DIAMETER_MM:.1f} across through "
        f"the thumb's east wall ({wall_margin:.3f} from its ends), clear of the sockets by "
        f"{from_sockets} and the standoffs by {from_standoffs}, {boss_text}"
    )


# The parts' mounts (work item 004): layout.py's mount bodies and voids
# (MountBox) and the wire rooms, against the tray, the parts and the
# sockets. The round openings are checked as their bounding boxes,
# which hold them. The nice!nano's clamp tab and screw head (work item
# 009) stand in the cavity like the bodies and are checked with them.


def describe_mount(box):
    return f"{box.label} ({box.part})"


def standing_bodies(fits=layout.DEFAULT_MOUNT_FITS):
    """The mount bodies and the clamp's tab and screw head on its block."""
    return layout.mount_bodies(fits) + layout.nano_clamp_part_boxes(fits)


def mount_pieces(boxes):
    """(label, plan polygon, z range) of mount boxes."""
    return [(describe_mount(box), box_polygon(box), box.z_range) for box in boxes]


def mount_containment_problems(fits=layout.DEFAULT_MOUNT_FITS):
    """(problems, tightest) of the mounts in the tray: the bodies, the
    clamp's tab and screw head and the pry slot inside the cavity, the
    pry slot and recess, the voids in the cavity, down to the floor's top
    and no further, so the floor stays whole and closed (work item 009),
    and the wall's voids from the cavity wall to the outer face."""
    cavity = layout.tray_cavity_polygon()
    outer = layout.tray_outer_polygon()
    problems = []
    tightest = Tightest()
    inside = standing_bodies(fits) + (layout.nano_pry_slot_box(fits),)
    for box in inside:
        margin = containment_margin(box_polygon(box), cavity)
        tightest.update(margin, describe_mount(box))
        if margin < -TOLERANCE_MM:
            problems.append(f"the {describe_mount(box)} pokes {-margin:.3f} past the cavity wall")
    for box in (layout.nano_pry_slot_box(fits), layout.nano_pry_recess_box(fits)):
        if box.z_range[0] < -TOLERANCE_MM:
            problems.append(f"the {describe_mount(box)} reaches z {box.z_range[0]}, below the "
                            "floor's top")
    for opening in layout.wall_openings(fits):
        problems.extend(wall_opening_problems(opening, cavity, outer))
    return problems, tightest


def wall_opening_problems(opening, cavity, outer):
    """An opening's boxes, from the cavity out, run through the wall:
    the first from the cavity wall, each on from where the one before
    it ends, the last out to the outer face."""
    middle_x = sum(opening[0].x_range) / 2.0
    problems = []
    inner = point_boundary_distance((middle_x, opening[0].y_range[0]), cavity)
    outside = point_boundary_distance((middle_x, opening[-1].y_range[1]), outer)
    if max(inner, outside) > TOLERANCE_MM:
        problems.append(
            f"the {describe_mount(opening[0])} runs {inner:.3f} off the cavity wall and the "
            f"{describe_mount(opening[-1])} {outside:.3f} off the outer face, not through the wall"
        )
    for before, after in zip(opening, opening[1:]):
        if after.y_range[0] > before.y_range[1] + TOLERANCE_MM:
            problems.append(f"the {describe_mount(after)} starts "
                            f"{after.y_range[0] - before.y_range[1]:.3f} past the "
                            f"{describe_mount(before)}")
    return problems


def check_mount_containment():
    problems, tightest = mount_containment_problems()
    fail_on(problems, "mounts outside the tray")
    return (
        f"mounts:    bodies, the clamp's tab and screw head and the pry slot inside the cavity "
        f"wall by {tightest}, the pry slot and recess down to the floor's top only, the shell's "
        "channel and the window, the lever slot and the pin hole through the wall"
    )


def mount_part_clearances(fits=layout.DEFAULT_MOUNT_FITS):
    """(own, other, zone): the Tightest clearance in plan of the mount
    bodies and the clamp's tab and screw head from their own part's
    envelopes, from the other parts' and, as printed, from the PCB
    connector's clear zone, wherever their heights overlap, and the
    problems: a body in its own part or the zone, or nearer than
    DESIGN_MOUNT_FROM_OTHER_PARTS_MM to another part."""
    own, other, zone = Tightest(), Tightest(), Tightest()
    problems = []
    for box in standing_bodies(fits):
        for envelope in layout.part_envelopes(fits):
            if not ranges_overlap(box.z_range, envelope.z_range):
                continue
            clearance = convex_separation(box_polygon(box), box_polygon(envelope))
            where = f"the {describe_mount(box)} and the {describe_envelope(envelope)}"
            if envelope is layout.PCB_CONNECTOR_CLEAR_ZONE:
                clearance -= layout.PRINT_SWELLING_PER_SIDE_MM
                tightest, minimum = zone, 0.0
            elif envelope.part == box.part:
                tightest, minimum = own, 0.0
            else:
                tightest, minimum = other, DESIGN_MOUNT_FROM_OTHER_PARTS_MM
            tightest.update(clearance, where)
            if clearance < minimum - TOLERANCE_MM:
                problems.append(f"{where}: {clearance:.3f}, less than {minimum}")
    return own, other, zone, problems


def check_mount_parts():
    own, other, zone, problems = mount_part_clearances()
    fail_on(problems, "mounts in the parts' way")
    figures = [
        require_figure(
            "from the other parts", other.value, DESIGN_MOUNTS_LEAST_FROM_OTHER_PARTS_MM, 1
        ),
        require_figure("from the PCB connector's zone as printed", zone.value,
                       DESIGN_MOUNTS_FROM_PCB_ZONE_PRINTED_MM, 1),
    ]
    fail_on(failed(figures), "the mounts' clearance from the other parts is off DESIGN.md")
    return (
        f"mounts:    bodies clear of their own parts by {own}; {figures[0][1]} ({other.where}); "
        f"{figures[1][1]} ({zone.where})"
    )


def mount_socket_problems(right, fits=layout.DEFAULT_MOUNT_FITS):
    """(problems, tightest in plan of the bodies reaching the sockets'
    height, the least height under the sockets of the bodies within
    the ledge's clearance of one in plan)."""
    minimum = layout.LEDGE_RELIEF_CLEARANCE_MM
    bodies = standing_bodies(fits)
    problems, in_plan = socket_clearances(mount_pieces(bodies), minimum, right)
    under = Tightest()
    for box in bodies:
        for name, socket in socket_footprints(right):
            if convex_separation(box_polygon(box), socket) >= minimum - TOLERANCE_MM:
                continue
            height = layout.SOCKET_BOTTOM_Z_MM - box.z_range[1]
            under.update(height, f"the {describe_mount(box)} under {name}'s socket")
            if height < minimum - TOLERANCE_MM:
                problems.append(f"the {describe_mount(box)} stands {height:.3f} under {name}'s")
    return problems, in_plan, under


def check_mount_sockets(right=False):
    """The mounts keep the ledge's clearance from the sockets: in plan
    where they reach the sockets' height, and in height where they come
    under one."""
    problems, in_plan, under = mount_socket_problems(right)
    fail_on(problems, f"{half_label(right)}mounts too close to the sockets")
    reaching = (
        f"bodies at the sockets' height clear in plan by {in_plan}"
        if in_plan.value < math.inf
        else "no body reaches the sockets' height"
    )
    return f"mounts:    {half_label(right)}{reaching}; under a socket by at least {under}"


def merges_standoff(box, center, fits):
    """Whether the body takes in the standoff: the nice!nano's bodies the
    one at layout.NANO_MERGED_STANDOFF_MM, standing under its top, whose
    bore tray_shape.py keeps open."""
    return (center == layout.NANO_MERGED_STANDOFF_MM and box in layout.nano_bodies(fits)
            and box.z_range[1] < layout.STANDOFF_HEIGHT_MM)


def mount_standoff_clearances(fits=layout.DEFAULT_MOUNT_FITS):
    """(problems, bodies, voids, merged): the bodies and the clamp's tab
    and screw head clear of the standoffs (the standoffs are the same on
    both halves in the left half's frame) unless they take one in, the
    voids DESIGN_MOUNT_VOIDS_FROM_STANDOFFS_MM from them, so their bases
    stay whole, with the Tightest of each, and the labels of the bodies
    that take in a standoff."""
    radius = layout.STANDOFF_DIAMETER_MM / 2.0
    problems = []
    bodies, voids = Tightest(), Tightest()
    merged = []
    for boxes, tightest, minimum in (
        (standing_bodies(fits), bodies, 0.0),
        (layout.mount_voids(fits), voids, DESIGN_MOUNT_VOIDS_FROM_STANDOFFS_MM),
    ):
        for box in boxes:
            for center in layout.MOUNTING_DRILL_CENTERS_MM:
                clearance = circle_separation(center, radius, box_polygon(box))
                if clearance < -TOLERANCE_MM and merges_standoff(box, center, fits):
                    merged.append(box.label)
                    continue
                where = f"the {describe_mount(box)} and the standoff at {center}"
                tightest.update(clearance, where)
                if clearance < minimum - TOLERANCE_MM:
                    problems.append(f"{where}: {clearance:.3f}, less than {minimum}")
    return problems, bodies, voids, merged


def check_mount_standoffs():
    problems, bodies, voids, merged = mount_standoff_clearances()
    figures = [
        require_figure("voids from the standoffs", voids.value,
                       DESIGN_MOUNT_VOIDS_LEAST_FROM_STANDOFFS_MM, 3),
        require_figure("the standoff taken in at x", layout.NANO_MERGED_STANDOFF_MM[0],
                       DESIGN_MERGED_STANDOFF_MM[0], 3),
        require_figure("y", layout.NANO_MERGED_STANDOFF_MM[1], DESIGN_MERGED_STANDOFF_MM[1], 3),
    ]
    fail_on(problems + failed(figures), "mounts on the standoffs")
    return (f"mounts:    bodies clear of the standoffs by {bodies}, but the {', '.join(merged)}, "
            f"which take in the one at {layout.NANO_MERGED_STANDOFF_MM}; {figures[0][1]} "
            f"({voids.where}); {joined(figures[1:])}")


def mount_joint_problems(right, fits=layout.DEFAULT_MOUNT_FITS):
    """(problems, tightest) of the mounts against the joint's plastic
    and its voids, the voids by the joint's least plastic between
    voids."""
    minimum = layout.JOINT_LEAST_PLASTIC_BETWEEN_VOIDS_MM
    problems = []
    tightest = Tightest()
    joint = joint_features(right) + boss_fills(right) + joint_voids(right)
    mounts = [(box, 0.0) for box in standing_bodies(fits)]
    mounts.extend((box, minimum) for box in layout.mount_voids(fits))
    for box, needed in mounts:
        for label, polygon, z_range in joint:
            if not ranges_overlap(box.z_range, z_range):
                continue
            clearance = convex_separation(box_polygon(box), polygon)
            where = f"the {describe_mount(box)} and the {label}"
            tightest.update(clearance, where)
            if clearance < needed - TOLERANCE_MM:
                problems.append(f"{where}: {clearance:.3f}, less than {needed}")
    return problems, tightest


def check_mount_joint(right=False):
    """The mounts clear of the joint's plastic and its voids."""
    problems, tightest = mount_joint_problems(right)
    fail_on(problems, f"{half_label(right)}mounts in the joint")
    return f"mounts:    {half_label(right)}clear of the joint's features and voids by {tightest}"


def clamp_under_sockets(fits=layout.DEFAULT_MOUNT_FITS):
    """(least height under them, the keys) of the sockets over the
    clamp's tab and screw head in plan, on the left half."""
    keys = set()
    least = math.inf
    for box in layout.nano_clamp_part_boxes(fits):
        for name, socket in socket_footprints():
            if convex_separation(box_polygon(box), socket) < -TOLERANCE_MM:
                keys.add(name)
                least = min(least, layout.SOCKET_BOTTOM_Z_MM - box.z_range[1])
    return least, keys


def clamp_head_from_sockets(fits=layout.DEFAULT_MOUNT_FITS):
    """The screw head's bounding box from the nearest socket in plan,
    the least of both halves: it stands at the sockets' height."""
    head = box_polygon(layout.nano_clamp_part_boxes(fits)[-1])
    return min(convex_separation(head, socket)
               for right in (False, True) for _, socket in socket_footprints(right))


def clamp_nose_from_foot(fits=layout.DEFAULT_MOUNT_FITS, block_shares=WORST_SPLITS):
    """The least, over the end faces' splits, of the nose's south face
    from the foot's north face as printed, both swollen toward each
    other, the foot's face by its share of the pocket's measured end face
    swelling: the nose comes down beside the foot, whose top stands as
    high as the board's."""
    nose_south = layout.nano_clamp_nose_y_range(fits)[0] - layout.PRINT_SWELLING_PER_SIDE_MM
    return min(nose_south - layout.nano_south_stop_y_as_printed(fits, share)
               for share in block_shares)


def clamp_nose_onto_board(fits=layout.DEFAULT_MOUNT_FITS, block_shares=WORST_SPLITS):
    """(least, most) the nose's south face as printed, swollen toward the
    foot, lies onto the board's south end, the board anywhere between its
    stops at the end faces' splits (nano_board_places())."""
    nose_south = layout.nano_clamp_nose_y_range(fits)[0] - layout.PRINT_SWELLING_PER_SIDE_MM
    shifts = [dy for _, dy in nano_board_places(fits, block_shares)]
    board_south = layout.nano_south_end_y(fits)
    return nose_south - (board_south + max(shifts)), nose_south - (board_south + min(shifts))


def box_overlap(first, second):
    """The volume two MountBoxes share."""
    volume = 1.0
    for low_high in zip((first.x_range, first.y_range, first.z_range),
                        (second.x_range, second.y_range, second.z_range)):
        (first_low, first_high), (second_low, second_high) = low_high
        volume *= max(0.0, min(first_high, second_high) - max(first_low, second_low))
    return volume


def clamp_problems(fits=layout.DEFAULT_MOUNT_FITS):
    """The rules DESIGN.md sets the clamp, apart from its figures."""
    problems = []
    strain = 100.0 * layout.nano_clamp_strain(fits)
    if strain > DESIGN_CLAMP_MAXIMUM_STRAIN_PERCENT:
        problems.append(f"the tab's arm strains {strain:.2f} % as printed, over "
                        f"{DESIGN_CLAMP_MAXIMUM_STRAIN_PERCENT} %")
    low_x, high_x = layout.nano_clamp_tab_x_range(fits)
    middle_low, middle_high = layout.nano_free_middle_x_range(fits)
    if low_x < middle_low - TOLERANCE_MM or high_x > middle_high + TOLERANCE_MM:
        problems.append(f"the tab's nose (x {low_x:.3f} to {high_x:.3f}) leaves the board's free "
                        f"middle (x {middle_low:.3f} to {middle_high:.3f})")
    room = layout.nano_clamp_insert_room(fits)
    for what, length in (("insert", layout.NANO_CLAMP_INSERT_LENGTH_MM),
                         ("screw", layout.nano_clamp_screw_reach(fits))):
        if length > room + TOLERANCE_MM:
            problems.append(f"the {what} reaches {length:.3f} into the bore, which leaves "
                            f"{room:.3f} as printed")
    under_pcb = layout.PCB_UNDERSIDE_Z_MM - max(box.z_range[1]
                                                for box in layout.nano_clamp_part_boxes(fits))
    if under_pcb < DESIGN_CLAMP_MINIMUM_UNDER_PCB_MM - TOLERANCE_MM:
        problems.append(f"the clamp stands {under_pcb:.3f} under the PCB, less than "
                        f"{DESIGN_CLAMP_MINIMUM_UNDER_PCB_MM}")
    if clamp_nose_from_foot(fits) < -TOLERANCE_MM:
        problems.append(f"the tab's nose reaches {-clamp_nose_from_foot(fits):.3f} into the foot "
                        "as printed")
    if clamp_nose_onto_board(fits)[0] < TOLERANCE_MM:
        problems.append("the tab's nose comes off the board's south end as printed")
    for part in layout.nano_clamp_part_boxes(fits):
        for body in layout.mount_bodies(fits):
            if box_overlap(part, body) > TOLERANCE_MM:
                problems.append(f"the {describe_mount(part)} overlaps the {describe_mount(body)}")
    return problems


def clamp_figures():
    clamp_x = layout.nano_clamp_tab_x_range()
    block, foot = layout.nano_clamp_boxes()
    tab_y = layout.nano_clamp_tab_y_range()
    nose_y = layout.nano_clamp_nose_y_range()
    board = layout.NANO_BOARD
    head = layout.nano_clamp_part_boxes()[-1]
    middle_low, middle_high = layout.nano_free_middle_x_range()
    under, keys = clamp_under_sockets()
    screw_y = layout.nano_clamp_screw_center()[1]
    return [
        require_figure("tab from x", clamp_x[0], DESIGN_CLAMP_TAB_X_MM[0], 2),
        require_figure("to", clamp_x[1], DESIGN_CLAMP_TAB_X_MM[1], 2),
        require_figure("in the free middle from x", middle_low, DESIGN_NANO_FREE_MIDDLE_X_MM[0], 3),
        require_figure("to", middle_high, DESIGN_NANO_FREE_MIDDLE_X_MM[1], 3),
        require_figure("block from x", block.x_range[0], DESIGN_CLAMP_BLOCK_X_MM[0], 1),
        require_figure("to", block.x_range[1], DESIGN_CLAMP_BLOCK_X_MM[1], 1),
        require_figure("y", block.y_range[0], DESIGN_CLAMP_BLOCK_Y_MM[0], 3),
        require_figure("to", block.y_range[1], DESIGN_CLAMP_BLOCK_Y_MM[1], 3),
        require_figure("block top z", block.z_range[1], DESIGN_CLAMP_BLOCK_TOP_Z_MM, 1),
        require_figure("foot from x", foot.x_range[0], DESIGN_CLAMP_FOOT_X_MM[0], 1),
        require_figure("to", foot.x_range[1], DESIGN_CLAMP_FOOT_X_MM[1], 1),
        require_figure("foot from the board", board.y_range[0] - foot.y_range[1],
                       DESIGN_CLAMP_FOOT_FROM_BOARD_MM, 2),
        require_figure("foot top z", foot.z_range[1], DESIGN_CLAMP_FOOT_TOP_Z_MM, 1),
        require_figure("screw from the board", board.y_range[0] - screw_y,
                       DESIGN_CLAMP_SCREW_FROM_BOARD_MM, 1),
        require_figure("insert room as printed", layout.nano_clamp_insert_room(),
                       DESIGN_CLAMP_INSERT_ROOM_PRINTED_MM, 1),
        require_figure("insert", layout.NANO_CLAMP_INSERT_LENGTH_MM,
                       DESIGN_CLAMP_INSERT_LENGTH_MM, 1),
        require_figure("screw's reach", layout.nano_clamp_screw_reach(),
                       DESIGN_CLAMP_SCREW_REACH_MM, 1),
        require_figure("tab from y", tab_y[0], DESIGN_CLAMP_TAB_Y_MM[0], 3),
        require_figure("to", tab_y[1], DESIGN_CLAMP_TAB_Y_MM[1], 3),
        require_figure("onto the board", tab_y[1] - board.y_range[0], DESIGN_CLAMP_TAB_REACH_MM, 1),
        require_figure("nose from the board's end", nose_y[0] - board.y_range[0],
                       DESIGN_CLAMP_NOSE_FROM_BOARD_END_MM[0], 1),
        require_figure("to", nose_y[1] - board.y_range[0], DESIGN_CLAMP_NOSE_FROM_BOARD_END_MM[1],
                       1),
        require_figure("thick as printed", layout.nano_clamp_tab_thickness(),
                       DESIGN_CLAMP_TAB_THICKNESS_MM[True], 1),
        require_figure("as modelled", layout.nano_clamp_tab_thickness(printed=False),
                       DESIGN_CLAMP_TAB_THICKNESS_MM[False], 1),
        require_figure("nose deep", layout.NANO_CLAMP_NOSE_DEPTH_MM, DESIGN_CLAMP_NOSE_DEPTH_MM, 1),
        require_figure("press", layout.DEFAULT_MOUNT_FITS.clamp_press, DESIGN_CLAMP_PRESS_MM, 1),
        require_figure("arm", layout.nano_clamp_arm_length(), DESIGN_CLAMP_ARM_MM, 3),
        require_figure("strain as printed %", 100.0 * layout.nano_clamp_strain(),
                       DESIGN_CLAMP_STRAIN_PERCENT[True], 2),
        require_figure("as modelled %", 100.0 * layout.nano_clamp_strain(printed=False),
                       DESIGN_CLAMP_STRAIN_PERCENT[False], 2),
        require_figure("nose from the foot as printed",
                       clamp_nose_from_foot(block_shares=EVEN_SPLIT),
                       DESIGN_CLAMP_NOSE_FROM_FOOT_PRINTED_MM, 2),
        require_figure("at the worst split", clamp_nose_from_foot(),
                       DESIGN_CLAMP_NOSE_FROM_FOOT_WORST_SPLIT_MM, 2),
        require_figure("onto the board, the board north",
                       clamp_nose_onto_board(block_shares=EVEN_SPLIT)[0],
                       DESIGN_CLAMP_NOSE_ONTO_BOARD_PRINTED_MM[0], 2),
        require_figure("south", clamp_nose_onto_board(block_shares=EVEN_SPLIT)[1],
                       DESIGN_CLAMP_NOSE_ONTO_BOARD_PRINTED_MM[1], 2),
        require_figure("at the worst split", clamp_nose_onto_board()[0],
                       DESIGN_CLAMP_NOSE_ONTO_BOARD_WORST_SPLIT_MM, 2),
        require_figure("head top z", head.z_range[1], DESIGN_CLAMP_HEAD_TOP_Z_MM, 1),
        require_figure("under the PCB", layout.PCB_UNDERSIDE_Z_MM - head.z_range[1],
                       DESIGN_CLAMP_UNDER_PCB_MM, 1),
        require_figure("head from the sockets in plan", clamp_head_from_sockets(),
                       DESIGN_CLAMP_HEAD_FROM_SOCKETS_MM, 3),
        require_figure(f"tab under {', '.join(sorted(keys))}", under,
                       DESIGN_CLAMP_TAB_UNDER_SOCKET_MM, 2),
    ]


def nano_play_as_printed(fits=layout.DEFAULT_MOUNT_FITS):
    """{way: play} of the board in its pocket as printed: across between
    the west ledge's face and the east wall's inner face, along between
    the foot's face and the north block's, swollen by the pocket's
    measured end face swelling."""
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    across = ((layout.nano_pocket_east_x(fits) - swelling)
              - (layout.west_ledge_face_x() + swelling) - fits.nano_width)
    along = (layout.nano_north_stop_y_as_printed(fits) - layout.nano_south_stop_y_as_printed(fits)
             - fits.nano_length)
    return {"across": across, "along": along}


def nano_bay_figures():
    """The pocket, the board's play in it as printed, the east wall and
    the north block at the default fits."""
    pocket = layout.nano_pocket_east_x() - layout.west_ledge_face_x()
    outer, under_pocket, _south_of_pocket = layout.nano_east_wall_boxes()
    west_side, east_side = layout.nano_north_block_boxes()[:2]
    bar = layout.nano_north_block_boxes()[-1]
    play = nano_play_as_printed()
    return [
        require_figure("pocket across", pocket, DESIGN_NANO_POCKET_MM, 1),
        require_figure("along", layout.nano_pocket_length(), DESIGN_NANO_POCKET_LENGTH_MM, 2),
        require_figure("its end faces' swelling", layout.NANO_POCKET_END_FACE_SWELLING_MM,
                       DESIGN_NANO_END_FACE_SWELLING_MM, 2),
    ] + [
        require_figure(f"the board's play {way} as printed", play[way],
                       DESIGN_NANO_PLAY_PRINTED_MM[way], 2)
        for way in DESIGN_NANO_PLAY_PRINTED_MM
    ] + [
        require_figure("east wall from x", under_pocket.x_range[0], DESIGN_NANO_EAST_WALL_X_MM[0],
                       1),
        require_figure("to", outer.x_range[1], DESIGN_NANO_EAST_WALL_X_MM[1], 1),
        require_figure("y", outer.y_range[0], DESIGN_NANO_EAST_WALL_Y_MM[0], 3),
        require_figure("to", outer.y_range[1], DESIGN_NANO_EAST_WALL_Y_MM[1], 1),
        require_figure("top z", outer.z_range[1], DESIGN_NANO_EAST_WALL_TOP_Z_MM, 1),
        require_figure("north block from x", west_side.x_range[0],
                       DESIGN_NANO_NORTH_BLOCK_X_MM[0], 1),
        require_figure("to", east_side.x_range[1], DESIGN_NANO_NORTH_BLOCK_X_MM[1], 1),
        require_figure("y", west_side.y_range[0], DESIGN_NANO_NORTH_BLOCK_Y_MM[0], 3),
        require_figure("to", west_side.y_range[1], DESIGN_NANO_NORTH_BLOCK_Y_MM[1], 3),
        require_figure("top z", bar.z_range[1], DESIGN_NANO_NORTH_BLOCK_TOP_Z_MM, 2),
    ]


def check_nano_bay():
    figures = nano_bay_figures()
    fail_on(failed(figures), "the nice!nano's bay off DESIGN.md")
    return "bay:       " + joined(figures)


def check_nano_clamp():
    figures = clamp_figures()
    _, keys = clamp_under_sockets()
    problems = clamp_problems() + failed(figures)
    if keys != DESIGN_CLAMP_SOCKET_KEYS:
        problems.append(f"the sockets over the clamp are {sorted(keys)}, DESIGN.md says "
                        f"{sorted(DESIGN_CLAMP_SOCKET_KEYS)}")
    fail_on(problems, "the nice!nano's screw clamp off DESIGN.md")
    return "clamp:     " + joined(figures)


def nano_shell_play(fits=layout.DEFAULT_MOUNT_FITS):
    """{direction: how far} the shell can move from its modelled place
    as printed: west and east the board between the west ledge's face
    and the east wall's and the shell between the north block's sides,
    north the board's USB end before the block."""
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    shell = layout.nano_usb_shell_envelope(fits)
    board = layout.nano_board_envelope(fits)
    west_side, east_side = layout.nano_north_block_boxes(fits)[:2]
    return {
        "west": min(board.x_range[0] - (layout.west_ledge_face_x() + swelling),
                    shell.x_range[0] - (west_side.x_range[1] + swelling)),
        "east": min((layout.nano_pocket_east_x(fits) - swelling) - board.x_range[1],
                    (east_side.x_range[0] - swelling) - shell.x_range[1]),
        "north": layout.nano_north_stop_y_as_printed(fits) - board.y_range[1],
    }


def shell_in_channel_margins(fits=layout.DEFAULT_MOUNT_FITS):
    """{where: margin} as printed of the shell in its channel wherever
    its play lets it go: across at both sides, over its top, and its
    mouth before the channel's north end, past which the window's
    corner rounds would reach it."""
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    shell = layout.nano_usb_shell_envelope(fits)
    channel = layout.usb_shell_channel_box(fits)
    play = nano_shell_play(fits)
    return {
        "sides": min(shell.x_range[0] - play["west"] - (channel.x_range[0] + swelling),
                     (channel.x_range[1] - swelling) - (shell.x_range[1] + play["east"])),
        "top": (channel.z_range[1] - swelling) - shell.z_range[1],
        "end": (channel.y_range[1] - swelling) - (shell.y_range[1] + play["north"]),
    }


def lever_in_slot_margin():
    """The least, as printed, between the lever's swept box and its
    slot."""
    lever = layout.POWER_SWITCH_LEVER
    slot = layout.power_switch_lever_slot_box()
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    margins = []
    for lever_range, slot_range in ((lever.x_range, slot.x_range), (lever.z_range, slot.z_range)):
        margins.append(lever_range[0] - (slot_range[0] + swelling))
        margins.append((slot_range[1] - swelling) - lever_range[1])
    return min(margins)


# Going in (DESIGN.md), the board is lowered nose first, its shell into
# the north block's opening, its USB end's top edge held against the
# block's south face as printed and the shell's mouth's bottom edge on
# the seat's level, the channel's bottom. Tilted by an angle a, every
# point of its south face lies north of the face's bottom edge (the face
# leans back toward the mouth), so that edge is the one to clear the
# foot's top edge. With the USB end's top edge, the board's thickness t
# over its underside, on the block's face, the bottom edge lies the
# board's length B times cos a plus t sin a south of that face,
# (B + e) sin a over the seat's level, e the shell's reach past the
# board. Its clearance from the foot's face as printed, the block's face
# less B cos a + t sin a less the foot's face, is least at tan a = t / B,
# or where the edge comes down to the foot's top as printed if it is
# there first. The shell's top meanwhile passes under the bar as
# printed: it rises toward the south, so it comes highest under the
# bar's south face. Heights are taken over the seat's level, and the end
# faces as printed are swollen by the pocket's measured end face
# swelling (layout.py's NANO_POCKET_END_FACE_SWELLING_MM).
def nano_insertion_figures(fits=layout.DEFAULT_MOUNT_FITS):
    """(the south end's clearance from the foot as printed, the angle in
    degrees where it is least, the shell's top under the bar there as
    printed)."""
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    board = layout.nano_board_envelope(fits)
    seat = board.z_range[0]
    block_face = layout.nano_north_stop_y_as_printed(fits)
    foot_face = layout.nano_south_stop_y_as_printed(fits)
    foot_top = layout.NANO_CLAMP_FOOT_HEIGHT_MM + layout.PRINT_RISE_OF_TOP_FACES_MM - seat
    length = board.y_range[1] - board.y_range[0]
    thickness = board.z_range[1] - board.z_range[0]
    past_board = layout.nano_usb_shell_mouth_y() - board.y_range[1]
    angle = min(math.atan2(thickness, length), math.asin(foot_top / (length + past_board)))
    clearance = block_face - foot_face - length * math.cos(angle) - thickness * math.sin(angle)
    mouth = block_face + past_board * math.cos(angle) - thickness * math.sin(angle)
    shell = layout.nano_usb_shell_envelope(fits)
    shell_top = shell.z_range[1] - shell.z_range[0]
    behind_mouth = (mouth + shell_top * math.sin(angle) - block_face) / math.cos(angle)
    shell_under_bar = behind_mouth * math.sin(angle) + shell_top * math.cos(angle)
    bar_margin = layout.nano_bar_underside_z(fits) - swelling - seat - shell_under_bar
    return clearance, math.degrees(angle), bar_margin


def nano_tilt_limits(fits=layout.DEFAULT_MOUNT_FITS):
    """(the foot's face and the north block's face apart as printed, the
    longest board that tilts in between them, its side's diagonal
    spanning that gap, and the least shell overhang that keeps a board
    of the fits' length with its shell within that longest board)."""
    board = layout.nano_board_envelope(fits)
    apart = layout.nano_north_stop_y_as_printed(fits) - layout.nano_south_stop_y_as_printed(fits)
    thickness = board.z_range[1] - board.z_range[0]
    longest = math.sqrt(apart**2 - thickness**2)
    with_shell = layout.nano_usb_shell_mouth_y() - board.y_range[0]
    return apart, longest, with_shell - longest


def nano_removal_slide(fits=layout.DEFAULT_MOUNT_FITS):
    """How far the board slides south from its north stop as it is
    lifted at its south end, until that end clears the foot's top as
    printed: it turns about the shell's mouth's bottom edge on the
    seat's level, its north end's top edge riding up the north block's
    face. That is the pose it goes in by, so its south edge keeps the
    going-in clearance from the foot (nano_insertion_figures())."""
    board = layout.nano_board_envelope(fits)
    length = board.y_range[1] - board.y_range[0]
    thickness = board.z_range[1] - board.z_range[0]
    past_board = layout.nano_usb_shell_mouth_y() - board.y_range[1]
    foot_top = (layout.NANO_CLAMP_FOOT_HEIGHT_MM + layout.PRINT_RISE_OF_TOP_FACES_MM
                - board.z_range[0])
    clear = math.asin(foot_top / (length + past_board))
    return past_board * (1.0 - math.cos(clear)) + thickness * math.sin(clear)


# Going in, the board's top rises toward its south end, so the strips
# on it lean north: the west strip's north top corner, its insulator's
# worst case, comes closest to the west pocket's north end, north of
# which the ledge's face as printed stands over the strip's west edge.
# The corner moves north the more the board tilts, so with its USB end
# on the north block the board goes in no steeper than the angle at
# which the corner still clears.
def nano_strip_tilt_figures(fits=layout.DEFAULT_MOUNT_FITS, block_shares=WORST_SPLITS):
    """(the west strip's north top corner from the west pocket's north
    end as printed at the going-in angle, the steepest angle in degrees
    at which it clears), the least of each over the end faces' splits."""
    figures = [nano_strip_tilt_at_split(fits, share) for share in block_shares]
    return min(clearance for clearance, _ in figures), min(steepest for _, steepest in figures)


def nano_strip_tilt_at_split(fits, block_swelling):
    """nano_strip_tilt_figures() with block_swelling of the end faces'
    swelling on the north block, whose face the board's USB end is held
    against."""
    board = layout.nano_board_envelope(fits)
    strip = layout.nano_strip_insulators(fits)[0]
    block_face = layout.nano_north_stop_y_as_printed(fits, block_swelling)
    pocket_end = layout.nano_strip_pocket_y_range()[1] - layout.PRINT_SWELLING_PER_SIDE_MM
    behind = board.y_range[1] - strip.y_range[1]
    over = strip.z_range[1] - board.z_range[1]
    tilt = math.radians(nano_insertion_figures(fits)[1])
    corner = block_face - behind * math.cos(tilt) + over * math.sin(tilt)
    steepest = (math.acos((block_face - pocket_end) / math.hypot(behind, over))
                - math.atan2(over, behind))
    return pocket_end - corner, math.degrees(steepest)


def insertion_problems(fits=layout.DEFAULT_MOUNT_FITS):
    clearance, angle, bar_margin = nano_insertion_figures(fits)
    problems = []
    if min(clearance, bar_margin) < -TOLERANCE_MM:
        problems.append(f"going in at {angle:.2f} degrees, the board's south end clears the foot "
                        f"by {clearance:.4f} and its shell the bar by {bar_margin:.4f} as printed")
    tilt_clearance, _steepest = nano_strip_tilt_figures(fits)
    if tilt_clearance < DESIGN_NANO_STRIP_TILT_LEAST_CLEARANCE_MM - TOLERANCE_MM:
        problems.append(f"going in at {angle:.2f} degrees, the west strip's corner keeps "
                        f"{tilt_clearance:.4f} from the ledge north of its pocket as printed, "
                        f"less than {DESIGN_NANO_STRIP_TILT_LEAST_CLEARANCE_MM}")
    return problems


# Only the sum of the end faces' swelling was calipered. Put all of it
# on the foot and the north block's face stands as modelled, so the
# shell's mouth gets past its channel's end as printed, into the
# window, whose corner rounds its box's corners then reach into. The
# real shell's ends are rounded and stay clear of the rounds.
def window_round_reach(x_range, z_range, fits=layout.DEFAULT_MOUNT_FITS):
    """How far a box's corners (its x and z ranges) reach out of the USB
    window's corner rounds as printed, where they lie beyond a round's
    center on both axes, minus infinity where none does."""
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    center_x, center_z = layout.usb_window_center(fits)
    radius = layout.USB_WINDOW_CORNER_RADIUS_MM
    inset_x = layout.USB_WINDOW_WIDTH_MM / 2.0 - radius
    inset_z = layout.USB_WINDOW_HEIGHT_MM / 2.0 - radius
    reach = -math.inf
    for x, x_sign in zip(x_range, (-1.0, 1.0)):
        for z, z_sign in zip(z_range, (-1.0, 1.0)):
            out_x = x_sign * (x - center_x) - inset_x
            out_z = z_sign * (z - center_z) - inset_z
            if out_x > 0.0 and out_z > 0.0:
                reach = max(reach, math.hypot(out_x, out_z) - (radius - swelling))
    return reach


def shell_with_end_swelling_on_foot(fits=layout.DEFAULT_MOUNT_FITS):
    """(how far the shell's mouth gets past its channel's end as printed,
    how far its box's corners then reach into the window's corner rounds
    as printed at its play across) with the north block's face as
    modelled."""
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    shell = layout.nano_usb_shell_envelope(fits)
    board = layout.nano_board_envelope(fits)
    channel = layout.usb_shell_channel_box(fits)
    north = layout.nano_north_block_south_y(fits) - board.y_range[1]
    past = shell.y_range[1] + north - (channel.y_range[1] - swelling)
    play = nano_shell_play(fits)
    reach = max(window_round_reach((shell.x_range[0] + dx, shell.x_range[1] + dx),
                                   shell.z_range, fits)
                for dx in (-play["west"], play["east"]))
    return past, reach


def opening_problems(fits=layout.DEFAULT_MOUNT_FITS):
    """The lever and the shell, wherever its play lets it go, clear of
    their openings as printed."""
    in_channel = shell_in_channel_margins(fits)
    if lever_in_slot_margin() < -TOLERANCE_MM or min(in_channel.values()) < -TOLERANCE_MM:
        return ["the lever or the shell does not clear its opening as printed"]
    return []


def check_mount_openings():
    """The lever passes its slot and the shell its channel as printed,
    the shell wherever its play lets it go, the bar reaches the shell's
    mouth, the board goes in past the foot, and the pin hole's axis lies
    where DESIGN.md puts it."""
    play = nano_shell_play()
    in_channel = shell_in_channel_margins()
    hole_x, hole_z = layout.reset_pin_hole_center()
    clearance, angle, bar_margin = nano_insertion_figures()
    apart, longest, overhang = nano_tilt_limits()
    tilt_clearance, steepest = nano_strip_tilt_figures(block_shares=EVEN_SPLIT)
    tilt_worst, steepest_worst = nano_strip_tilt_figures()
    past_channel, into_round = shell_with_end_swelling_on_foot()
    figures = [
        require_figure("lever in its slot as printed", lever_in_slot_margin(),
                       DESIGN_LEVER_IN_SLOT_PRINTED_MM, 2),
        require_figure("bar deep to the shell's mouth", layout.nano_bar_depth(),
                       DESIGN_NANO_BAR_DEPTH_MM, 2),
    ] + [
        require_figure(f"shell's play {direction}", play[direction],
                       DESIGN_SHELL_PLAY_MM[direction], 2)
        for direction in DESIGN_SHELL_PLAY_MM
    ] + [
        require_figure(f"in its channel as printed at the {where}", in_channel[where],
                       DESIGN_SHELL_IN_CHANNEL_PRINTED_MM[where], 2)
        for where in DESIGN_SHELL_IN_CHANNEL_PRINTED_MM
    ] + [
        require_figure("the board going in over the foot as printed", clearance,
                       DESIGN_NANO_INSERTION_CLEARANCE_PRINTED_MM, 2),
        require_figure("coming out", clearance, DESIGN_NANO_REMOVAL_CLEARANCE_PRINTED_MM, 3),
        require_figure("sliding south from its north stop", nano_removal_slide(),
                       DESIGN_NANO_REMOVAL_SLIDE_MM, 2),
        require_figure("stops apart as printed", apart, DESIGN_NANO_STOPS_APART_PRINTED_MM, 1),
        require_figure("the longest board that tilts in", longest,
                       DESIGN_NANO_LONGEST_BOARD_MM, 2),
        require_figure("the least shell overhang", overhang,
                       DESIGN_NANO_LEAST_SHELL_OVERHANG_MM, 2),
        require_figure("the west strip's north top corner from its pocket's north end as printed",
                       tilt_clearance, DESIGN_NANO_STRIP_TILT_CLEARANCE_PRINTED_MM, 3),
        require_figure("the steepest going in with the USB end on the block, degrees", steepest,
                       DESIGN_NANO_STRIP_TILT_STEEPEST_DEGREES, 2),
        require_figure("at the end faces' worst split, the corner", tilt_worst,
                       DESIGN_NANO_STRIP_TILT_CLEARANCE_WORST_SPLIT_MM, 3),
        require_figure("the steepest, degrees", steepest_worst,
                       DESIGN_NANO_STRIP_TILT_STEEPEST_WORST_SPLIT_DEGREES, 2),
        require_figure("with the end faces' swelling all on the foot, the shell past its channel",
                       past_channel, DESIGN_SHELL_PAST_CHANNEL_ALL_ON_FOOT_MM, 2),
        require_figure("its box into the window's corner rounds as printed", into_round,
                       DESIGN_SHELL_INTO_WINDOW_ROUND_ALL_ON_FOOT_MM, 3),
        require_figure("pin hole's axis x", hole_x, DESIGN_RESET_PIN_HOLE_AXIS_MM[0], 3),
        require_figure("z", hole_z, DESIGN_RESET_PIN_HOLE_AXIS_MM[1], 2),
    ]
    fail_on(failed(figures) + opening_problems() + insertion_problems(),
            "the mounts' openings off DESIGN.md")
    return (f"openings:  {joined(figures)} (least at {angle:.2f} degrees, the shell then "
            f"{bar_margin:.3f} under the bar as printed)")


def wire_room_depths():
    """(behind the leads, over the nice!nano's pads): each lead room's
    smaller extent in plan, the room behind the lead, and each pad
    room's height."""
    behind = [
        min(room.x_range[1] - room.x_range[0], room.y_range[1] - room.y_range[0])
        for room in layout.lead_wire_rooms()
    ]
    over = [room.z_range[1] - room.z_range[0] for room in layout.nano_wire_rooms()]
    return behind, over


def printed_tray_obstacles(right, fits=layout.DEFAULT_MOUNT_FITS):
    """(label, plan polygon, z range, swelling) of the given half's tray
    as cut, its plastic with the print's swelling, and the clamp screw's
    steel head without it. The standoffs are apart (standoff_problems())."""
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    tray = (ledge_pieces(right, fits) + wall_pieces(right) + joint_features(right)
            + boss_fills(right) + mount_pieces(layout.mount_bodies(fits)
                                               + layout.nano_clamp_part_boxes(fits)[:-1]))
    printed = [(label, polygon, z_range, swelling) for label, polygon, z_range in tray]
    steel = [(label, polygon, z_range, 0.0)
             for label, polygon, z_range in mount_pieces(layout.nano_clamp_part_boxes(fits)[-1:])]
    return printed + steel


def wire_room_obstacles(right, fits=layout.DEFAULT_MOUNT_FITS):
    """(label, plan polygon, z range, swelling) of everything a wire room
    must keep clear of on the given half, the printed plastic with the
    print's swelling, the parts' envelopes as (label, part, polygon, z
    range) apart, since a room may lie against its own part."""
    sockets = [(f"{name}'s socket", polygon, socket_z_range(), 0.0)
               for name, polygon in socket_footprints(right)]
    parts = [(describe_envelope(envelope), envelope.part, box_polygon(envelope), envelope.z_range)
             for envelope in layout.part_envelopes(fits)]
    return printed_tray_obstacles(right, fits) + sockets, parts


def clearance_problems(envelope, obstacles, tightest):
    """The problems of an envelope reaching into (label, plan polygon, z
    range, swelling) obstacles wherever their heights overlap, the
    Tightest updated."""
    problems = []
    polygon = box_polygon(envelope)
    for label, obstacle, z_range, grown in obstacles:
        if not ranges_overlap(envelope.z_range, z_range):
            continue
        clearance = convex_separation(polygon, obstacle) - grown
        tightest.update(clearance, f"the {describe_envelope(envelope)} and the {label}")
        if clearance < -TOLERANCE_MM:
            problems.append(f"the {describe_envelope(envelope)} reaches {-clearance:.3f} into "
                            f"the {describe_piece(label, z_range)}")
    return problems


def standoff_problems(envelope, tightest):
    """The problems of an envelope reaching into a standoff as printed,
    the Tightest updated."""
    radius = layout.STANDOFF_DIAMETER_MM / 2.0 + layout.PRINT_SWELLING_PER_SIDE_MM
    problems = []
    for center in layout.MOUNTING_DRILL_CENTERS_MM:
        clearance = circle_separation(center, radius, box_polygon(envelope))
        tightest.update(clearance,
                        f"the {describe_envelope(envelope)} and the standoff at {center}")
        if clearance < -TOLERANCE_MM:
            problems.append(f"the {describe_envelope(envelope)} reaches into the standoff at "
                            f"{center}")
    return problems


def nano_strip_pieces(fits=layout.DEFAULT_MOUNT_FITS):
    """The labels of the nice!nano's socket strips and their tails, the
    pieces of its own a room over its pads must keep clear of."""
    return {describe_envelope(envelope)
            for envelope in layout.nano_strip_envelopes(fits) + layout.nano_tail_envelopes(fits)}


def room_into_strips(room, strips, tightest):
    """{(room's piece, strip's label): how far} in plan a room reaches
    into the (label, polygon, z range) strip pieces where their heights
    overlap, the ones it clears counted in the Tightest."""
    found = {}
    polygon = box_polygon(room)
    for label, strip, z_range in strips:
        if not ranges_overlap(room.z_range, z_range):
            continue
        clearance = convex_separation(polygon, strip)
        if clearance < -TOLERANCE_MM:
            found[(room.piece, label)] = -clearance
        else:
            tightest.update(clearance, f"the {describe_envelope(room)} and the {label}")
    return found


def named_room_overlaps(right):
    """{(room's piece, strip's label): (how far, decimals)} DESIGN.md
    names."""
    return {(f"wire room {room}", f"nice!nano {side} socket strip's insulator"): figure
            for (room, side), figure in DESIGN_NANO_ROOMS_INTO_STRIPS_MM[right].items()}


def wire_room_problems(right, fits=layout.DEFAULT_MOUNT_FITS):
    """(problems, tightest, overlaps) of every wire room against its
    obstacles and the standoffs, the printed plastic as printed, and of
    the nice!nano's pad rooms against its own strips and tails: those
    overlaps as {(room's piece, strip's label): how far}, any DESIGN.md
    does not name a problem."""
    obstacles, parts = wire_room_obstacles(right, fits)
    strips = nano_strip_pieces(fits)
    named = named_room_overlaps(right)
    problems = []
    overlaps = {}
    tightest = Tightest()
    for room in layout.wire_rooms(fits, right):
        candidates = list(obstacles)
        candidates.extend((label, polygon, z_range, 0.0) for label, part, polygon, z_range in parts
                          if part != room.part)
        problems.extend(clearance_problems(room, candidates, tightest))
        problems.extend(standoff_problems(room, tightest))
        own = [(label, polygon, z_range) for label, part, polygon, z_range in parts
               if part == room.part and label in strips]
        overlaps.update(room_into_strips(room, own, tightest))
    problems.extend(f"the nice!nano's {room} reaches {overlaps[(room, strip)]:.4f} into its {strip}"
                    for room, strip in sorted(set(overlaps) - set(named)))
    return problems, tightest, overlaps


def check_wire_rooms(right=False):
    """Every wire room clear of the tray as cut, the mounts, the
    standoffs and the joint as printed, the sockets and the other
    parts, and the nice!nano's pad rooms of its strips but where
    DESIGN.md names an overlap."""
    behind, over = wire_room_depths()
    problems, tightest, overlaps = wire_room_problems(right)
    named = named_room_overlaps(right)
    problems.extend(f"the nice!nano's {room} no longer reaches into its {strip}"
                    for room, strip in sorted(set(named) - set(overlaps)))
    figures = [
        require_figure_for_all("behind every lead", behind, DESIGN_WIRE_ROOM_BEHIND_LEADS_MM, 1),
        require_figure_for_all("over the nice!nano's pads", over, DESIGN_WIRE_ROOM_OVER_PADS_MM, 1),
        require_figure("clear as printed by", tightest.value,
                       DESIGN_WIRE_ROOM_LEAST_CLEARANCE_PRINTED_MM, 3),
    ] + [
        require_figure(f"the {room} into the {strip.removeprefix('nice!nano ')}",
                       overlaps[(room, strip)], stated, decimals)
        for (room, strip), (stated, decimals) in sorted(named.items()) if (room, strip) in overlaps
    ]
    fail_on(problems + failed(figures), f"{half_label(right)}the wires' room taken")
    return f"wires:     {half_label(right)}{joined(figures)} ({tightest.where})"


# The nice!nano's seat, its channels and the socket strips (the user's
# request of 2026-10-20 to raise the bay and pocket the strips). The
# seat's edges keep the channels' allowances from the pads beside them
# as printed, the strips' tails hang over the channels' bottom, the
# floor's top, as printed, and the strips with the rooms over them up to
# the PCB's underside keep clear of the tray as printed, which their
# pockets in the west ledge and the east wall see to. How far the
# strips' tops stay under the sockets over them is reported for both
# halves.


def nano_channels_beyond_pads(fits=layout.DEFAULT_MOUNT_FITS):
    """The least, as printed, between the seat's edges and the inner
    edges of the pads beside them, the pin rows' and B+ and B-'s, at the
    render's inset that brings them closest."""
    low, high = layout.nano_seat_x_range(fits)
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    west_pads = max(layout.nano_row_x_range(fits, True)[1],
                    layout.nano_battery_pad_x_range(fits, True)[1])
    east_pads = min(layout.nano_row_x_range(fits, False)[0],
                    layout.nano_battery_pad_x_range(fits, False)[0])
    return min((low - swelling) - west_pads, east_pads - (high + swelling))


def nano_tails_over_channels(printed, fits=layout.DEFAULT_MOUNT_FITS):
    """How far the tails' tips stay over the channels' bottom, the floor's
    top: as modelled the datasheet's tail, as printed the longest tail
    over the bottom counted higher, as any slot's."""
    underside = layout.nano_board_envelope(fits).z_range[0]
    if printed:
        lowest = layout.nano_tail_envelopes(fits)[0].z_range[0]
        return lowest - layout.PRINT_RISE_OF_UP_FACING_BOTTOMS_MM
    return underside - (layout.NANO_STRIP_TAIL_LENGTH_MM - layout.NANO_BOARD_THICKNESS_MM)


def nano_seat_problems(fits=layout.DEFAULT_MOUNT_FITS):
    """The pads and the tails clear of the seat and the channels' bottom
    as printed, and the pry recess wholly over the seat's southwest
    corner, so the seat's two boxes leave it free."""
    problems = []
    beyond = nano_channels_beyond_pads(fits)
    if beyond < -TOLERANCE_MM:
        problems.append(f"the seat reaches {-beyond:.3f} under the pads beside it as printed")
    over = nano_tails_over_channels(True, fits)
    if over < -TOLERANCE_MM:
        problems.append(f"the longest tails reach {-over:.3f} into the channels' bottom as printed")
    recess = layout.nano_pry_recess_box(fits)
    low, high = layout.nano_seat_x_range(fits)
    if not recess.x_range[0] <= low < recess.x_range[1] < high:
        problems.append(f"the pry recess (x {recess.x_range[0]:.3f} to {recess.x_range[1]:.3f}) "
                        f"does not take the seat's southwest corner (x {low:.3f} to {high:.3f})")
    return problems


def check_nano_seat():
    seat, beside_recess = layout.nano_seat_boxes()
    figures = [
        require_figure("seat top z", seat.z_range[1], DESIGN_NANO_SEAT_TOP_Z_MM, 1),
        require_figure("the board on it from z", layout.NANO_BOARD.z_range[0],
                       DESIGN_NANO_SEAT_TOP_Z_MM, 1),
        require_figure("from x", seat.x_range[0], DESIGN_NANO_SEAT_X_MM[0], 3),
        require_figure("to", seat.x_range[1], DESIGN_NANO_SEAT_X_MM[1], 3),
        require_figure("y", beside_recess.y_range[0], DESIGN_NANO_SEAT_Y_MM[0], 3),
        require_figure("to", seat.y_range[1], DESIGN_NANO_SEAT_Y_MM[1], 3),
        require_figure("the channels beyond the pads as printed", nano_channels_beyond_pads(),
                       DESIGN_NANO_CHANNELS_BEYOND_PADS_PRINTED_MM, 1),
        require_figure("the tails over the channels' bottom", nano_tails_over_channels(False),
                       DESIGN_NANO_TAILS_OVER_CHANNELS_MM[False], 2),
        require_figure("the longest as printed", nano_tails_over_channels(True),
                       DESIGN_NANO_TAILS_OVER_CHANNELS_MM[True], 3),
    ]
    fail_on(nano_seat_problems() + failed(figures), "the nice!nano's seat off DESIGN.md")
    return "seat:      " + joined(figures)


def nano_board_places(fits=layout.DEFAULT_MOUNT_FITS, block_shares=WORST_SPLITS):
    """(dx, dy) from its modelled place of each extreme place the board
    can take in its pocket as printed: across as far as the shell's play
    lets it, along from the foot's face to the north block's at each of
    the end faces' splits. At the even split the modelled place lies 0.02
    into the foot as printed, so every place is north of it."""
    play = nano_shell_play(fits)
    board = layout.nano_board_envelope(fits)
    along = sorted({stop for share in block_shares for stop in (
        layout.nano_south_stop_y_as_printed(fits, share) - board.y_range[0],
        layout.nano_north_stop_y_as_printed(fits, share) - board.y_range[1])})
    return [(dx, dy) for dx in (-play["west"], play["east"]) for dy in along]


def shifted_envelope(envelope, offset):
    """The envelope moved in plan by (dx, dy), which its label tells."""
    dx, dy = offset
    return dataclasses.replace(
        envelope, piece=f"{envelope.piece} moved ({dx:+.2f}, {dy:+.2f})",
        x_range=(envelope.x_range[0] + dx, envelope.x_range[1] + dx),
        y_range=(envelope.y_range[0] + dy, envelope.y_range[1] + dy),
    )


def nano_strip_clearances(right, fits=layout.DEFAULT_MOUNT_FITS, block_shares=WORST_SPLITS):
    """(problems, tightest) of the strips and the rooms over them against
    the half's tray as printed, the standoffs included, the board at
    each of its extreme places at the end faces' splits
    (nano_board_places())."""
    obstacles = printed_tray_obstacles(right, fits)
    problems = []
    tightest = Tightest()
    for offset in nano_board_places(fits, block_shares):
        for envelope in layout.nano_strip_envelopes(fits) + layout.nano_strip_rooms(fits):
            moved = shifted_envelope(envelope, offset)
            problems.extend(clearance_problems(moved, obstacles, tightest))
            problems.extend(standoff_problems(moved, tightest))
    return problems, tightest


def nano_insulator_over_foot(fits=layout.DEFAULT_MOUNT_FITS):
    """(how far the strips' insulators reach past the board's south end,
    how far they then stay over the clamp foot's top as printed, which
    rises as a top face)."""
    insulator = layout.nano_strip_insulators(fits)[0]
    past = layout.nano_south_end_y(fits) - insulator.y_range[0]
    foot_top = layout.NANO_CLAMP_FOOT_HEIGHT_MM + layout.PRINT_RISE_OF_TOP_FACES_MM
    return past, insulator.z_range[0] - foot_top


def strips_under_sockets(right, fits=layout.DEFAULT_MOUNT_FITS):
    """(least height under them, keys) of the sockets over the strips in
    plan on the given half."""
    least, keys = math.inf, set()
    for strip in layout.nano_strip_insulators(fits):
        for name, socket in socket_footprints(right):
            if convex_separation(box_polygon(strip), socket) < -TOLERANCE_MM:
                keys.add(name)
                least = min(least, layout.SOCKET_BOTTOM_Z_MM - strip.z_range[1])
    return least, keys


def nano_strip_figures():
    """The strips' worst case, their insulators over the clamp's foot,
    and their pockets as built: the west one the ledge's cut, the east
    one the east wall's boxes."""
    west, east = layout.nano_strip_insulators()
    past_board, over_foot = nano_insulator_over_foot()
    ledge_pocket = layout.tray_cut_polygon(layout.nano_strip_ledge_pocket())
    outer, _under_pocket, south_of_pocket = layout.nano_east_wall_boxes()
    return [
        require_figure("west strip from x", west.x_range[0], DESIGN_NANO_STRIP_X_MM["west"][0], 3),
        require_figure("to", west.x_range[1], DESIGN_NANO_STRIP_X_MM["west"][1], 3),
        require_figure("east strip from x", east.x_range[0], DESIGN_NANO_STRIP_X_MM["east"][0], 3),
        require_figure("to", east.x_range[1], DESIGN_NANO_STRIP_X_MM["east"][1], 3),
        require_figure("both from y", west.y_range[0], DESIGN_NANO_STRIP_Y_MM[0], 4),
        require_figure("to", west.y_range[1], DESIGN_NANO_STRIP_Y_MM[1], 4),
        require_figure("top z", west.z_range[1], DESIGN_NANO_STRIP_TOP_Z_MM, 3),
        require_figure("the insulators from z", west.z_range[0],
                       DESIGN_NANO_STRIP_INSULATOR_BOTTOM_Z_MM, 2),
        require_figure("past the board's south end", past_board,
                       DESIGN_NANO_STRIP_PAST_BOARD_END_MM, 4),
        require_figure("over the foot's top as printed", over_foot,
                       DESIGN_NANO_INSULATOR_OVER_FOOT_PRINTED_MM, 2),
        require_figure("the ledge's pocket face x", min(x for x, _ in ledge_pocket),
                       DESIGN_NANO_STRIP_POCKET_X_MM[0], 3),
        require_figure("from y", min(y for _, y in ledge_pocket), DESIGN_NANO_STRIP_POCKET_Y_MM[0],
                       4),
        require_figure("to", max(y for _, y in ledge_pocket), DESIGN_NANO_STRIP_POCKET_Y_MM[1], 4),
        require_figure("the east wall's pocket face x", outer.x_range[0],
                       DESIGN_NANO_STRIP_POCKET_X_MM[1], 3),
        require_figure("from y", south_of_pocket.y_range[1], DESIGN_NANO_STRIP_POCKET_Y_MM[0], 4),
    ]


def check_nano_strips(right=False):
    """The strips' worst case and their pockets, the strips and the
    rooms over them clear of the tray as printed, and the sockets over
    them."""
    problems, worst = nano_strip_clearances(right)
    tightest = nano_strip_clearances(right, block_shares=EVEN_SPLIT)[1]
    under, keys = strips_under_sockets(right)
    if nano_insulator_over_foot()[1] < TOLERANCE_MM:
        problems.append("the strips' insulators come down on the clamp's foot as printed")
    figures = nano_strip_figures() + [
        require_figure("clear of the tray as printed up to the PCB's underside, the board at its "
                       "worst place, by", tightest.value, DESIGN_NANO_STRIPS_CLEAR_PRINTED_MM, 3),
        require_figure("at the end faces' worst split", worst.value,
                       DESIGN_NANO_STRIPS_CLEAR_WORST_SPLIT_MM, 3),
        require_figure(f"under {', '.join(sorted(keys))}'s sockets by", under,
                       DESIGN_NANO_STRIPS_UNDER_SOCKETS_MM, 3),
    ]
    if keys != DESIGN_NANO_STRIP_SOCKET_KEYS[right]:
        problems.append(f"the sockets over the strips are {sorted(keys)}, DESIGN.md says "
                        f"{sorted(DESIGN_NANO_STRIP_SOCKET_KEYS[right])}")
    fail_on(problems + failed(figures), f"{half_label(right)}the nice!nano's strips off DESIGN.md")
    return (f"strips:    {half_label(right)}{joined(figures)} ({tightest.where}; at the worst "
            f"split {worst.where})")


# The pry slot and recess (work item 010): the slot through the clamp's
# block and foot, which a toothpick comes down into from the south, is
# checked in plan against everything else in the tray, the wire rooms
# and the other parts whatever the heights, since the toothpick crosses
# them from above the floor. The recess, in the floor under it and the
# board's south end, leaves the floor under it, and the voids' checks
# keep it from the standoffs and the joint.


def pry_slot_obstacles(right, fits=layout.DEFAULT_MOUNT_FITS):
    """(label, plan polygon) of everything the pry slot keeps clear of:
    the half's ledge, walls and joint, the standing bodies but the
    clamp's block and foot, which it runs through, the wire rooms and the
    parts but the nice!nano."""
    block_and_foot = layout.nano_clamp_boxes(fits)
    tray = (ledge_pieces(right, fits) + wall_pieces(right) + joint_features(right)
            + boss_fills(right))
    obstacles = [(label, polygon) for label, polygon, _ in tray]
    obstacles.extend((describe_mount(box), box_polygon(box)) for box in standing_bodies(fits)
                     if box not in block_and_foot)
    obstacles.extend((describe_envelope(room), box_polygon(room))
                     for room in layout.wire_rooms(fits, right))
    obstacles.extend((describe_envelope(envelope), box_polygon(envelope))
                     for envelope in layout.part_envelopes(fits) if envelope.part != "nice!nano")
    return obstacles


def pry_slot_clearance(right, fits=layout.DEFAULT_MOUNT_FITS):
    """The Tightest of the slot in plan from its obstacles."""
    slot = box_polygon(layout.nano_pry_slot_box(fits))
    tightest = Tightest()
    for label, polygon in pry_slot_obstacles(right, fits):
        tightest.update(convex_separation(slot, polygon), f"the {label}")
    return tightest


def pry_slot_from_insert_bore(fits=layout.DEFAULT_MOUNT_FITS):
    """The clamp block's plastic between the slot and the insert's bore."""
    radius = layout.NANO_CLAMP_BORE_DIAMETER_MM / 2.0
    return circle_separation(layout.nano_clamp_screw_center(fits), radius,
                             box_polygon(layout.nano_pry_slot_box(fits)))


# The toothpick, 2.0 across with a round point on its axis tapering over
# its last 5.0 (layout.py), lies along y in the slot, the tab and the PCB
# off. It comes in from the south over the rim and the south ledge and
# down the slot to its point on the recess's bottom, the floor's top, all
# as printed. At an angle a below the horizontal its shaft, of radius R,
# clears a corner (y, z) of what it crosses if the point lies at least
# y + R / sin a + (z - bottom) / tan a north (the full radius even near
# the point, the cautious reading), and the cone's top, at a plus the
# taper's half angle, stays under the board's underside, h over the
# bottom, if the point lies at most h / tan(a + half angle) past the
# board's south edge. Both limits fall as a grows, the first faster, so
# the least angle at which they meet gives the farthest reach. The
# corners are taken over the slot's whole width, the cautious reading,
# though the toothpick goes in east of the west row's last tail, which
# lies within its reach (pry_toothpick_lane()).


def band_y_range(polygon, x_range):
    """(low, high) y of a convex polygon's part between two x, None
    where it has none."""
    clipped = clip_to_half_plane(polygon, (1.0, 0.0), x_range[1])
    if len(clipped) >= 3:
        clipped = clip_to_half_plane(clipped, (-1.0, 0.0), -x_range[0])
    if len(clipped) < 3 or polygon_area(clipped) < TOLERANCE_MM:
        return None
    ys = [y for _, y in clipped]
    return (min(ys), max(ys))


def circle_band_y_range(center, radius, x_range):
    """(low, high) y of a circle's part between two x, None where it has
    none."""
    x, y = center
    nearest = min(max(x, x_range[0]), x_range[1])
    if abs(nearest - x) >= radius:
        return None
    half = math.sqrt(radius**2 - (nearest - x) ** 2)
    return (y - half, y + half)


def pry_toothpick_corners(right, fits=layout.DEFAULT_MOUNT_FITS):
    """(label, (y, z)) as printed of the north top edge of everything
    the toothpick crosses south of the board within the slot's width,
    the half's ledge, walls, dowel bosses and fills, the standing bodies
    but the clamp's block and foot, which the slot runs through, the
    standoffs and the parts but the nice!nano, the tray's grown by the
    swelling and its tops by a top face's rise."""
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    rise = layout.PRINT_RISE_OF_TOP_FACES_MM
    band = layout.nano_pry_slot_box(fits).x_range
    board_south = layout.nano_south_end_y(fits)
    block_and_foot = layout.nano_clamp_boxes(fits)
    tray = (ledge_pieces(right, fits) + wall_pieces(right) + dowel_bosses(right)
            + boss_fills(right)
            + mount_pieces([box for box in standing_bodies(fits) if box not in block_and_foot]))
    corners = []
    for label, polygon, z_range in tray:
        y_range = band_y_range(polygon, band)
        if y_range is not None and y_range[1] < board_south:
            corners.append((label, (y_range[1] + swelling, z_range[1] + rise)))
    radius = layout.STANDOFF_DIAMETER_MM / 2.0 + swelling
    for center in layout.MOUNTING_DRILL_CENTERS_MM:
        y_range = circle_band_y_range(center, radius, band)
        if y_range is not None and y_range[1] < board_south:
            corners.append((f"standoff at {center}",
                            (y_range[1], layout.STANDOFF_HEIGHT_MM + rise)))
    for envelope in layout.part_envelopes(fits):
        if envelope.part in ("nice!nano", layout.PCB_CONNECTOR_CLEAR_ZONE.part):
            continue
        y_range = band_y_range(box_polygon(envelope), band)
        if y_range is not None and y_range[1] < board_south:
            corners.append((describe_envelope(envelope), (y_range[1], envelope.z_range[1])))
    return corners


def toothpick_half_angle():
    return math.atan2(layout.NANO_PRY_TOOTHPICK_DIAMETER_MM / 2.0,
                      layout.NANO_PRY_TOOTHPICK_TAPER_MM)


def toothpick_point_over(corner, angle, bottom):
    """The least y of the point on the bottom at which the shaft clears
    the corner."""
    y, z = corner
    radius = layout.NANO_PRY_TOOTHPICK_DIAMETER_MM / 2.0
    return y + radius / math.sin(angle) + (z - bottom) / math.tan(angle)


def pry_toothpick_pose(right, fits=layout.DEFAULT_MOUNT_FITS, board_shift=0.0):
    """(the least angle in degrees, how far the point then gets under
    the board's south edge, the recess left north of it, the corner that
    sets the angle), as printed, the board moved board_shift north of
    its modelled place. Where no angle brings the point under the board,
    the reach is minus infinity at the steepest angle tried, and the
    corner is the one that stops it there."""
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    recess = layout.nano_pry_recess_box(fits)
    bottom = recess.z_range[0] + layout.PRINT_RISE_OF_UP_FACING_BOTTOMS_MM
    under_board = layout.nano_board_envelope(fits).z_range[0] - bottom
    board_south = layout.nano_south_end_y(fits) + board_shift
    recess_end = recess.y_range[1] - swelling
    corners = pry_toothpick_corners(right, fits)

    def farthest(angle):
        reach = under_board / math.tan(angle + toothpick_half_angle())
        return min(board_south + reach, recess_end)

    def nearest(angle):
        return max(toothpick_point_over(corner, angle, bottom) for _, corner in corners)

    def setting(angle):
        return max(corners, key=lambda item: toothpick_point_over(item[1], angle, bottom))[0]

    low, high = toothpick_half_angle(), math.pi / 2.0 - toothpick_half_angle()
    if nearest(high) > farthest(high):
        return math.degrees(high), -math.inf, 0.0, setting(high)
    for _ in range(60):
        middle = (low + high) / 2.0
        if nearest(middle) <= farthest(middle):
            high = middle
        else:
            low = middle
    point = farthest(high)
    return math.degrees(high), point - board_south, recess_end - point, setting(high)


def pry_toothpick_worst_pose(right, fits=layout.DEFAULT_MOUNT_FITS, block_shares=WORST_SPLITS):
    """pry_toothpick_pose() with the board at whichever of its stops as
    printed, at the end faces' splits, leaves the point the least far
    under it."""
    shifts = sorted({dy for _, dy in nano_board_places(fits, block_shares)})
    return min((pry_toothpick_pose(right, fits, shift) for shift in shifts),
               key=lambda pose: pose[1])


def pry_recess_floor_under(fits=layout.DEFAULT_MOUNT_FITS):
    return layout.nano_pry_recess_box(fits).z_range[0] - layout.FLOOR_UNDERSIDE_Z_MM


def pry_toothpick_lane(fits=layout.DEFAULT_MOUNT_FITS):
    """(low, high) x as printed of the slot's part a toothpick can come
    down clear of the west row's last tail, its pad and its solder: from
    the pad's inner edge at the larger inset and the channel's
    allowances beyond it to the slot's east face."""
    slot = layout.nano_pry_slot_box(fits).x_range
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    beside_tail = (layout.nano_row_x_range(fits, True)[1] + layout.NANO_TAIL_FILLET_ALLOWANCE_MM
                   + layout.NANO_BOARD_PLAY_ALLOWANCE_MM)
    return (max(slot[0] + swelling, beside_tail), slot[1] - swelling)


def pry_last_tail_from_board_end(fits=layout.DEFAULT_MOUNT_FITS):
    """How far north of the board's south edge the west row's last tail
    starts."""
    return layout.nano_tail_envelopes(fits)[0].y_range[0] - layout.nano_south_end_y(fits)


def pry_slot_problems(right, fits=layout.DEFAULT_MOUNT_FITS):
    """The slot clear of its obstacles, the recess leaving the floor
    under it, and a toothpick's point getting under the board within the
    recess."""
    problems = []
    clearance = pry_slot_clearance(right, fits)
    if clearance.value < -TOLERANCE_MM:
        problems.append(f"the pry slot reaches {-clearance.value:.3f} into {clearance.where}")
    if pry_slot_from_insert_bore(fits) < TOLERANCE_MM:
        problems.append("the pry slot reaches the clamp's insert bore")
    floor_under = pry_recess_floor_under(fits)
    if floor_under < DESIGN_PRY_RECESS_FLOOR_UNDER_MM - TOLERANCE_MM:
        problems.append(f"the pry recess leaves {floor_under:.3f} of floor under it, less than "
                        f"{DESIGN_PRY_RECESS_FLOOR_UNDER_MM}")
    low, high = pry_toothpick_lane(fits)
    if high - low < layout.NANO_PRY_TOOTHPICK_DIAMETER_MM - TOLERANCE_MM:
        problems.append(f"the slot leaves the toothpick {high - low:.3f} beside the west row's "
                        "last tail as printed, less than its "
                        f"{layout.NANO_PRY_TOOTHPICK_DIAMETER_MM}")
    angle, reach, _room, where = pry_toothpick_worst_pose(right, fits)
    if reach == -math.inf:
        problems.append(f"no angle up to {angle:.2f} degrees brings a toothpick's point under "
                        f"the board past the {where}")
    elif reach < TOLERANCE_MM:
        problems.append(f"a toothpick's point gets {reach:.3f} under the board, at {angle:.2f} "
                        f"degrees over the {where}")
    return problems


def check_pry_slot(right=False):
    """The pry slot's and recess's size and place, the slot clear of
    everything else in the tray, the wire rooms and the other parts in
    plan, the recess's floor, a toothpick's reach under the board and its
    lane past the west row's last tail."""
    slot = layout.nano_pry_slot_box()
    recess = layout.nano_pry_recess_box()
    board = layout.NANO_BOARD
    angle, reach, room, where = pry_toothpick_worst_pose(right, block_shares=EVEN_SPLIT)
    worst_reach = pry_toothpick_worst_pose(right)[1]
    lane = pry_toothpick_lane()
    figures = [
        require_figure("slot from x", slot.x_range[0], DESIGN_PRY_SLOT_X_MM[0], 1),
        require_figure("to", slot.x_range[1], DESIGN_PRY_SLOT_X_MM[1], 1),
        require_figure("from the ledge's face", slot.x_range[0] - layout.west_ledge_face_x(),
                       DESIGN_PRY_SLOT_FROM_LEDGE_MM, 1),
        require_figure("from the insert's bore", pry_slot_from_insert_bore(),
                       DESIGN_PRY_SLOT_FROM_INSERT_BORE_MM, 2),
        require_figure("y", slot.y_range[0], DESIGN_PRY_SLOT_Y_MM[0], 3),
        require_figure("to", slot.y_range[1], DESIGN_PRY_SLOT_Y_MM[1], 3),
        require_figure("recess from y", recess.y_range[0], DESIGN_PRY_RECESS_Y_MM[0], 3),
        require_figure("to", recess.y_range[1], DESIGN_PRY_RECESS_Y_MM[1], 3),
        require_figure("under the board", recess.y_range[1] - board.y_range[0],
                       DESIGN_PRY_RECESS_UNDER_BOARD_MM, 1),
        require_figure("down to z", recess.z_range[0], DESIGN_PRY_RECESS_BOTTOM_Z_MM, 1),
        require_figure("floor under it", pry_recess_floor_under(),
                       DESIGN_PRY_RECESS_FLOOR_UNDER_MM, 1),
        require_figure("a 2.0 toothpick's least angle, the board at its worst stop", angle,
                       DESIGN_PRY_TOOTHPICK_ANGLE_DEGREES, 1),
        require_figure("its point under the board as printed", reach,
                       DESIGN_PRY_TOOTHPICK_REACH_PRINTED_MM, 2),
        require_figure("at the end faces' worst split", worst_reach,
                       DESIGN_PRY_TOOTHPICK_REACH_WORST_SPLIT_MM, 2),
        require_figure("past the west row's last tail, from the board's end",
                       pry_last_tail_from_board_end(), DESIGN_PRY_LAST_TAIL_FROM_BOARD_END_MM, 3),
        require_figure("in the slot east of it as printed from x", lane[0],
                       DESIGN_PRY_TOOTHPICK_LANE_X_MM[0], 3),
        require_figure("to", lane[1], DESIGN_PRY_TOOTHPICK_LANE_X_MM[1], 2),
    ]
    fail_on(pry_slot_problems(right) + failed(figures),
            f"{half_label(right)}the nice!nano's pry slot off DESIGN.md")
    clearance = pry_slot_clearance(right)
    return (f"pry slot:  {half_label(right)}{joined(figures)}; the slot clear in plan by "
            f"{clearance}; the toothpick's angle set by the {where}, its point {room:.3f} short "
            "of the recess's end")


def on_right_half(check):
    """The check run on the right half, as a check of its own."""

    def check_right_half():
        return check(right=True)

    check_right_half.__name__ = f"{check.__name__}_on_right_half"
    return check_right_half


CHECKS = (
    check_outline,
    check_outline_on_cells,
    check_slant,
    check_keys_and_holes,
    check_switch_pins,
    check_mounting_drills,
    check_heights,
    check_part_figures,
    check_part_containment,
    check_part_ledge,
    check_part_standoffs,
    check_parts_apart,
    check_part_sockets,
    on_right_half(check_part_sockets),
    check_battery,
    on_right_half(check_battery),
    check_socket_tray_rules,
    on_right_half(check_socket_tray_rules),
    check_socket_ledge,
    on_right_half(check_socket_ledge),
    check_socket_wall,
    on_right_half(check_socket_wall),
    check_socket_standoffs,
    on_right_half(check_socket_standoffs),
    check_joint_figures,
    check_joint_inside,
    on_right_half(check_joint_inside),
    check_joint_clearances,
    on_right_half(check_joint_clearances),
    check_joint_voids,
    on_right_half(check_joint_voids),
    check_magnet_slot_opening,
    check_parking_hole,
    on_right_half(check_parking_hole),
    check_mount_containment,
    check_mount_parts,
    check_mount_sockets,
    on_right_half(check_mount_sockets),
    check_mount_standoffs,
    check_mount_joint,
    on_right_half(check_mount_joint),
    check_nano_bay,
    check_nano_seat,
    check_nano_strips,
    on_right_half(check_nano_strips),
    check_nano_clamp,
    check_mount_openings,
    check_pry_slot,
    on_right_half(check_pry_slot),
    check_wire_rooms,
    on_right_half(check_wire_rooms),
)


def main():
    for check in CHECKS:
        try:
            print(check())
        except CheckFailure as failure:
            sys.stdout.flush()
            print(f"FAILED: {failure}", file=sys.stderr)
            return 1
    print(f"all {len(CHECKS)} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
