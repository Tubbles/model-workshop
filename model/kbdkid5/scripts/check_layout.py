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
tray, clear of the parts, the sockets, the standoffs and the joint, no
void in the cavity below
the floor's top, the clamp's tab within its strain and under the PCB,
and the openings around what passes them as printed, the shell
wherever its play lets it go, and the board going in past the clamp's
foot (work item 010). The nice!nano's seat leaves the pads beside it
and the socket strips' tails under it room as printed, and the strips
on the board with the room over them up to the PCB keep clear of the
tray as printed, through their pockets in the bay's walls and the column
1/2 step's ledge (the user's request of 2026-10-20). The strips, each an insulator
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

The rules a standoff (its drill, body and bore) and a hand-wired
frame's boss (the boss and its screw head) meet where they stand are
records, PlacementRules, one per feature and obstacle, built from the
obstacle functions by standoff_rules() and frame_boss_rules(): the
feature, the obstacle, their heights, the minimum, where the feature
may merge with the tray instead and which rule then still holds, and
the sockets' flats. The checks iterate the records, and a placement
solver (work item 016) reads the same records, so the two cannot
drift. The standoffs' and the bosses' centers come in as arguments,
the checks passing layout.py's.
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
DESIGN_SLANT_LENGTH_MM = 81.76
DESIGN_SLANT_SOUTH_OF_THUMB_CORNER_MM = 19.251  # along the slant
DESIGN_SLANT_ANGLE_FROM_NORTH_DEGREES = 17.74
DESIGN_HALF_SIZE_MM = (138.3, 82.6)
DESIGN_MIRROR_LINE_X_MM = 69.133
DESIGN_HEIGHTS_Z_MM = (  # (what, z)
    ("socket bottoms", 7.48),
    ("PCB top", 11.1),
    ("plate top", 13.3),
    ("tray rim", 13.4),
)
DESIGN_TRAY_HEIGHT_MM = 14.6
DESIGN_NANO_SIZE_MM = (18.20, 33.20)  # along x, along y
DESIGN_NANO_FROM_STEP_LEDGE_FACE_MM = 0.3
DESIGN_NANO_EAST_OF_COLUMN_2_MM = 0.475
DESIGN_NANO_USB_MOUTH_BEHIND_OUTER_FACE_MM = 0.5
DESIGN_POWER_SWITCH_KNOB_PROUD_MM = {False: 3.2, True: 2.8}  # as modelled, as printed
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
    ("S140", (75.724, 62.785), 0.487, 0.787),
)
DESIGN_STANDOFF_FLAT_BOTTOM_Z_MM = 6.48
# The right half's sockets (DESIGN.md, "Tray"): no tab notches, the
# thumb's tab clear of the joint block since the slant ran on south, the
# bottom row's reliefs, and no flats.
DESIGN_RIGHT_TAB_NOTCH_KEYS = set()
DESIGN_RIGHT_THUMB_TAB_FROM_JOINT_BLOCK_MM = 0.890
DESIGN_RIGHT_LEDGE_RELIEF_KEYS = {"S103", "S113", "S123", "S133", "S143", "S153", "S163"}
DESIGN_RIGHT_STANDOFF_FLATS = ()
DESIGN_RIGHT_CLOSEST_SOCKET_TO_STANDOFF_MM = 1.114
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
DESIGN_DOWEL_BOSSES_INSIDE_SLANT_ENDS_MM = (19.251, 0.006)
# The plastic around the standoffs' bores where the joint's slots and
# holes come nearest: the sixth standoff's, merged with the joint block,
# beside the magnet slot at 67.511 along the slant, on both halves.
DESIGN_STANDOFF_BORE_FROM_JOINT_VOIDS_MM = 0.832
DESIGN_PARKING_PIN_PROUD_MM = 1.5
DESIGN_PARKING_BOSS_FROM_SOCKETS_MM = 1.763  # on both halves, the thumb's
DESIGN_MAGNET_SLOT_ABOVE_BED_MM = 0.5
DESIGN_PIN_OFF_HOLE_MM = 0.05  # each blade from its 3.0 hole, along footprint x
DESIGN_PULL_IN_MM = 0.2
DESIGN_DEFAULT_SLIT_MM = (0.6, 1.6)  # across the blade, along it
DESIGN_SLIT_CLEARANCE_MM = (0.2, 0.4)  # per side as modelled: across the blade, along it
# The parts' mounts (work item 004).
DESIGN_MOUNT_FROM_OTHER_PARTS_MM = 0.5  # every mount body from every part but its own
DESIGN_MOUNTS_LEAST_FROM_OTHER_PARTS_MM = 4.0  # the nice!nano's east wall, from the reset button
DESIGN_MOUNT_VOIDS_FROM_STANDOFFS_MM = 0.5
DESIGN_MOUNT_VOIDS_LEAST_FROM_STANDOFFS_MM = 15.467  # the pry slot, from the center one
DESIGN_NANO_FREE_MIDDLE_X_MM = (40.729, 54.519)
# The nice!nano's bay (work item 010): the pocket, the east wall, the
# north block, at the default fits.
DESIGN_NANO_POCKET_MM = 18.7  # across, from the column 1/2 step's ledge face (38.224)
DESIGN_NANO_PLAY_PRINTED_MM = {"across": 0.1, "along": 0.1}
DESIGN_NANO_POCKET_LENGTH_MM = 33.56  # the foot's face to the north block's
DESIGN_NANO_END_FACE_SWELLING_MM = 0.13  # each, calipered on the first heavy duty bay
DESIGN_NANO_EAST_WALL_X_MM = (56.924, 59.124)
DESIGN_NANO_EAST_WALL_Y_MM = (43.278, 79.648)
DESIGN_NANO_EAST_WALL_TOP_Z_MM = 5.2
DESIGN_NANO_WEST_WALL_X_MM = (36.124, 38.224)
DESIGN_NANO_WEST_WALL_Y_MM = (43.278, 65.3)
DESIGN_NANO_RAISED_WALLS_Y_MM = {
    "west": ((49.710, 59.837),),
    "east": ((43.278, 47.931), (53.581, 66.981), (72.631, 79.648)),
}
DESIGN_NANO_RAISED_WALL_TOP_Z_MM = 9.5
DESIGN_NANO_NORTH_BLOCK_X_MM = (38.024, 57.224)  # the ledge cut-away's
DESIGN_NANO_NORTH_BLOCK_Y_MM = (80.328, 80.648)
DESIGN_NANO_NORTH_BLOCK_TOP_Z_MM = 6.16
# The nice!nano's seat and the channels beside it (the user's request to
# raise the bay, 2026-10-20).
DESIGN_NANO_SEAT_TOP_Z_MM = 1.2
DESIGN_NANO_SEAT_X_MM = (41.429, 53.819)
DESIGN_NANO_SEAT_Y_MM = (46.768, 80.328)  # the foot's face to the north block's
DESIGN_NANO_CHANNELS_BEYOND_PADS_PRINTED_MM = 0.5  # the seat's edges from the pads' inner edges
DESIGN_NANO_TAILS_OVER_CHANNELS_MM = {False: 0.39, True: 0.057}  # nominal modelled, worst printed
# The socket strips on the board (Mill-Max 315-43-112-41-003000) and
# their pockets, at their worst case.
DESIGN_NANO_STRIP_X_MM = {"west": (38.249, 41.549), "east": (53.699, 56.999)}
DESIGN_NANO_STRIP_Y_MM = (46.6445, 77.7515)
DESIGN_NANO_STRIP_TOP_Z_MM = 5.213
DESIGN_NANO_STRIP_INSULATOR_BOTTOM_Z_MM = 3.41  # 0.61 over the board's top
DESIGN_NANO_STRIP_PAST_BOARD_END_MM = 0.2335  # the insulator, over the clamp's foot
DESIGN_NANO_INSULATOR_OVER_FOOT_PRINTED_MM = 0.56  # the foot's top rising as a top face
DESIGN_NANO_STRIP_POCKET_X_MM = (37.749, 57.499)  # the west wall's and step ledge's face, the east wall's
DESIGN_NANO_STRIP_POCKET_Y_MM = (46.1445, 78.4215)
DESIGN_NANO_STRIPS_CLEAR_PRINTED_MM = 0.25  # of the tray up to the PCB's underside, the board west
DESIGN_NANO_STRIPS_CLEAR_WORST_SPLIT_MM = 0.19  # the same, the end faces' swelling split worst
DESIGN_NANO_STRIPS_UNDER_SOCKETS_MM = 2.267
DESIGN_NANO_STRIP_SOCKET_KEYS = {False: {"S120", "S121", "S130", "S131"}, True: {"S120", "S121"}}
# The nice!nano's screw clamp (work items 009 and 010), at the default
# press.
DESIGN_CLAMP_TAB_X_MM = (44.724, 50.524)
DESIGN_CLAMP_BLOCK_X_MM = (36.124, 59.124)
DESIGN_CLAMP_BLOCK_Y_MM = (37.478, 43.278)
DESIGN_CLAMP_FOOT_FROM_BOARD_MM = 0.11  # the foot's north face from the board's south end
DESIGN_CLAMP_FOOT_X_MM = (38.224, 56.924)
DESIGN_CLAMP_FOOT_TOP_Z_MM = 2.8
DESIGN_CLAMP_SCREW_FROM_BOARD_MM = 6.5  # the screw's axis from the board's south end
DESIGN_CLAMP_BLOCK_TOP_Z_MM = 4.8
DESIGN_CLAMP_INSERT_ROOM_PRINTED_MM = 4.6  # the bore's bottom counted 0.2 higher
DESIGN_CLAMP_INSERT_LENGTH_MM = 3.0  # M2 x 3
DESIGN_CLAMP_SCREW_REACH_MM = 2.8  # an M2 x 4 through the tab as printed
DESIGN_CLAMP_TAB_Y_MM = (37.478, 48.378)
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
DESIGN_CLAMP_HEAD_FROM_SOCKETS_MM = 1.587  # S121's, on both halves
DESIGN_CLAMP_TAB_UNDER_SOCKET_MM = 1.38  # the plate as printed, lifted by the press
DESIGN_CLAMP_SOCKET_KEYS = {"S121"}  # over the tab
DESIGN_KNOB_IN_SLOT_PRINTED_MM = 0.25  # per side
# The power switch's retainer as printed and fitted: under the switches'
# center posts and side pegs where it lies under them, still in its
# socket lifted to the PCB, from the sockets in plan on both halves, and
# its opening from the leads, beside them and over them.
DESIGN_RETAINER_UNDER_POSTS_MM = 0.5
DESIGN_RETAINER_IN_SOCKET_AT_PCB_MM = 1.1
DESIGN_RETAINER_FROM_SOCKETS_MM = 2.649  # S100's
DESIGN_RETAINER_BESIDE_LEADS_PRINTED_MM = 0.25
DESIGN_RETAINER_OVER_LEADS_MM = 0.5
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
DESIGN_RESET_PIN_HOLE_AXIS_MM = (66.199, 3.095)  # x, z
DESIGN_MOUNTS_FROM_PCB_ZONE_PRINTED_MM = 0.0  # the nice!nano's west wall
DESIGN_WIRE_ROOM_BEHIND_LEADS_MM = 3.0
DESIGN_WIRE_ROOM_OVER_PADS_MM = 3.0
DESIGN_WIRE_ROOM_LEAST_CLEARANCE_PRINTED_MM = 0.2
# The nice!nano's pad rooms its own socket strips' insulators reach
# into, per half (False the left one, in the left half's frame), (room,
# strip): (how far in plan, decimals). The B+ and B- rooms meet the
# insulators' north ends, the P1.01/P1.02/P1.07 room the B- row's
# insulator (0.31 if the render's insets moved together). The P1 pads
# are unused for now (the user, 2026-10-21). Any other overlap fails.
DESIGN_NANO_ROOMS_INTO_STRIPS_MM = {
    False: {("over the B- pad", "west"): (0.1235, 4), ("over the B+ pad", "east"): (0.1235, 4),
            ("over the P1.01/P1.02/P1.07 pads", "west"): (0.44, 2)},
    True: {("over the B+ pad", "west"): (0.1235, 4), ("over the B- pad", "east"): (0.1235, 4),
           ("over the P1.01/P1.02/P1.07 pads", "east"): (0.44, 2)},
}
# The nice!nano's pry slot and recess (work item 010).
DESIGN_FRAME_BOSS_COUNT = {False: 28, True: 27}
DESIGN_FRAME_BACKING_TOP_Z_MM = 7.233  # on the bosses' ends, 2.267 under the frame
DESIGN_FRAME_BACKING_UNDERSIDE_PRINTED_Z_MM = 6.383
DESIGN_FRAME_SCREW_HEADS_BOTTOM_Z_MM = 4.883
DESIGN_FRAME_TAB_SLOT_WIDTH_MM = 3.18
DESIGN_FRAME_TAB_SLOT_PAST_TIP_MM = 0.5
# The frame's footprint holes as modelled, in layout.CHOC_FOOTPRINT_HOLES_MM's
# order: the post, the pegs, the blades, the NC pad's.
DESIGN_FRAME_HOLE_DIAMETERS_MM = (3.42, 1.90, 1.90, 3.2, 3.2, 1.6)
DESIGN_PRY_SLOT_X_MM = (39.224, 44.224)
DESIGN_PRY_SLOT_Y_MM = (37.478, 46.768)  # through the clamp's block and foot
DESIGN_PRY_SLOT_FROM_LEDGE_MM = 1.0
DESIGN_PRY_SLOT_FROM_INSERT_BORE_MM = 1.8
DESIGN_PRY_RECESS_Y_MM = (37.478, 48.878)
DESIGN_PRY_RECESS_UNDER_BOARD_MM = 2.0
DESIGN_PRY_RECESS_BOTTOM_Z_MM = 0.0  # the floor's top, the seat left out
DESIGN_PRY_RECESS_FLOOR_UNDER_MM = 1.2  # the whole floor
DESIGN_PRY_TOOTHPICK_ANGLE_DEGREES = 18.0  # the least, over the rim, the board north
DESIGN_PRY_TOOTHPICK_REACH_PRINTED_MM = 1.68  # its point under the board, the board north
DESIGN_PRY_TOOTHPICK_REACH_WORST_SPLIT_MM = 1.55  # the same, the end faces' split worst
DESIGN_PRY_TOOTHPICK_LANE_X_MM = (41.229, 44.024)  # as printed, east of the west row's last tail
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
    """An Envelope's or a MountBox's plan."""
    return layout.plan_corners(envelope)


def plan_side_lengths(envelope):
    """(first side, second side) of a box's plan."""
    first, second, third, _fourth = box_polygon(envelope)
    return math.dist(first, second), math.dist(second, third)


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


# The rules a placed feature meets (work item 016), one record per
# feature and obstacle: what the checks below iterate and what a
# placement solver reads. A rule holds in plan wherever the feature's
# and the obstacle's heights overlap.

CLEAR = "clear"  # the feature keeps the minimum from the obstacle
INSIDE = "inside"  # the feature stays the minimum inside the obstacle, an outline
MERGE = "merge"  # the feature may run into the obstacle, the rule named survivor still holding
APART = "apart"  # the feature keeps the minimum from the same feature of every other part


@dataclasses.dataclass(frozen=True)
class PlacementRule:
    """A rule a feature of a placed part meets against one obstacle. The
    feature is a circle of radius about the part's center over
    feature_z_range, with the flats cut into it there; the obstacle is a
    circle_clearance() kind and shape over obstacle_z_range. A z range
    of None means any height: the rule holds in plan whatever the
    heights. A rule with a flat_key lets a flat stand in for its minimum:
    that key's socket, coming within it, gets a flat
    (layout.socket_standoff_flats()), which layout.SOCKET_STANDOFF_FLATS
    must declare and which must leave
    layout.STANDOFF_RELIEF_MINIMUM_WALL_MM of plastic around the bore
    (check_socket_tray_rules())."""

    name: str
    feature: str
    radius: float
    feature_z_range: object
    obstacle: str
    kind: str
    shape: object
    obstacle_z_range: object = None
    relation: str = CLEAR
    minimum: float = 0.0
    flats: tuple = ()
    flat_key: object = None
    survivor: object = None


def heights_meet(rule):
    """Whether a rule's feature and obstacle stand at heights that meet,
    so the rule holds in plan."""
    if rule.feature_z_range is None or rule.obstacle_z_range is None:
        return True
    return ranges_overlap(rule.feature_z_range, rule.obstacle_z_range)


def circle_clearance(center, radius, kind, shape):
    """A circle's clearance from an obstacle, negative when they
    overlap."""
    if kind == "circle":
        other_center, other_radius = shape
        return math.dist(center, other_center) - radius - other_radius
    if kind == "outline":
        return -signed_point_distance(center, shape) - radius
    return circle_separation(center, radius, shape)


def rule_clearance(center, rule):
    """How far a rule's feature at center keeps from its obstacle, or
    with INSIDE how far it stays inside it: negative when it reaches in,
    or out."""
    if rule.relation == INSIDE:
        return signed_point_distance(center, rule.shape) - rule.radius
    if rule.flats:
        return standoff_clearance(center, rule.flats, rule.shape)
    return circle_clearance(center, rule.radius, rule.kind, rule.shape)


def rule_tallies(rules):
    """A Tightest for each rule name among the rules, in their order."""
    return {name: Tightest() for name in dict.fromkeys(rule.name for rule in rules)}


# A standoff's rules, its drill's, body's and bore's, by the checks that
# hold them. standoff_rules() gathers them for a standoff at a center.


def standoff_body_rule(name, obstacle, polygon, z_range=None, minimum=0.0):
    """A rule of a standoff's body, clear of a convex polygon by the
    minimum where their heights meet."""
    return PlacementRule(name, "body", layout.STANDOFF_DIAMETER_MM / 2.0, standoff_z_range(),
                         obstacle, "polygon", polygon, z_range, CLEAR, minimum)


def standoff_drill_rules():
    """The mounting drill INSIDE_OUTLINE_MINIMUM_MARGIN_MM inside the
    outline and clear of every key's footprint holes and socket on the
    left half, at any height, since it runs through the PCB
    (check_mounting_drills())."""
    radius = layout.MOUNTING_DRILL_DIAMETER_MM / 2.0
    rules = [PlacementRule("drill inside the outline", "drill", radius, None, "the outline",
                           "outline", layout.OUTLINE_VERTICES_MM, None, INSIDE,
                           INSIDE_OUTLINE_MINIMUM_MARGIN_MM)]
    rules.extend(
        PlacementRule("drill from the switch holes", "drill", radius, None,
                      f"{name}'s {diameter} hole", "circle", (hole_center, diameter / 2.0))
        for name, center in layout.KEY_CENTERS_MM.items()
        for hole_center, diameter in layout.footprint_holes(center)
    )
    rules.extend(
        PlacementRule("drill from the sockets", "drill", radius, None, f"{name}'s socket",
                      "polygon", polygon)
        for name, polygon in socket_footprints()
    )
    return rules


def standoff_part_rules(fits=layout.DEFAULT_MOUNT_FITS):
    """The body clear of the parts' envelopes where their heights meet
    (check_part_standoffs())."""
    return [standoff_body_rule("body from the parts", describe_envelope(envelope),
                               box_polygon(envelope), envelope.z_range)
            for envelope in layout.part_envelopes(fits)]


def standoff_socket_rules(center, right=False):
    """The body layout.STANDOFF_RELIEF_CLEARANCE_MM from every socket on
    the given half where their heights meet, band by band of its height
    with the flats layout.py declares at center cut into it
    (standoff_bands(), check_socket_standoffs()). A socket coming closer
    gets a flat (flat_key)."""
    return [
        PlacementRule("body from the sockets", "body", layout.STANDOFF_DIAMETER_MM / 2.0, z_range,
                      f"{name}'s socket", "polygon", socket, socket_z_range(), CLEAR,
                      layout.STANDOFF_RELIEF_CLEARANCE_MM, tuple(flats), name)
        for z_range, flats in standoff_bands(center, right)
        for name, socket in socket_footprints(right)
    ]


def standoff_joint_rules(right=False):
    """The body clear of the half's dowel bosses and their fills where
    their heights meet (check_joint_clearances())."""
    return [standoff_body_rule("body from the joint's plastic", label, polygon, z_range)
            for label, polygon, z_range in dowel_bosses(right) + boss_fills(right)]


def standoff_bore_rules(right=False):
    """The insert bore layout.STANDOFF_RELIEF_MINIMUM_WALL_MM from the
    half's joint slots and holes where their heights meet, so a standoff
    merging with the joint block keeps its bore whole
    (check_standoff_bores())."""
    return [PlacementRule("bore from the joint's voids", "bore",
                          layout.STANDOFF_BORE_DIAMETER_MM / 2.0, standoff_z_range(), label,
                          "polygon", polygon, z_range, CLEAR,
                          layout.STANDOFF_RELIEF_MINIMUM_WALL_MM)
            for label, polygon, z_range in joint_voids(right)]


def standoff_parking_hole_rules():
    """The body clear of the parking hole at any height
    (check_parking_hole())."""
    return [standoff_body_rule("body from the parking hole", "parking hole",
                               layout.parking_hole_polygon())]


def standoff_mount_rules(fits=layout.DEFAULT_MOUNT_FITS):
    """The body clear of the mount bodies and the clamp's tab and screw
    head, none taking one in, and DESIGN_MOUNT_VOIDS_FROM_STANDOFFS_MM
    from the mount voids, so their bases stay whole, at any height
    (mount_standoff_clearances())."""
    bodies = [standoff_body_rule("body from the mount bodies", describe_mount(box),
                                 box_polygon(box))
              for box in standing_bodies(fits)]
    voids = [standoff_body_rule("body from the mount voids", describe_mount(box), box_polygon(box),
                                minimum=DESIGN_MOUNT_VOIDS_FROM_STANDOFFS_MM)
             for box in layout.mount_voids(fits)]
    return bodies + voids


def standoff_printed_rule(name, envelope):
    """A rule of a standoff's body as printed, grown by the print's
    swelling, clear of an envelope in plan at any height."""
    radius = layout.STANDOFF_DIAMETER_MM / 2.0 + layout.PRINT_SWELLING_PER_SIDE_MM
    return PlacementRule(name, "body as printed", radius, standoff_z_range(),
                         describe_envelope(envelope), "polygon", box_polygon(envelope))


def standoff_wire_room_rules(rooms):
    """The body as printed clear of the wire rooms
    (wire_room_problems())."""
    return [standoff_printed_rule("body as printed from the wire rooms", room) for room in rooms]


def standoff_nano_strip_rules(places):
    """The body as printed clear of the nice!nano's strips and the rooms
    over them at the board's places (nano_strip_places(),
    nano_strip_clearances())."""
    return [standoff_printed_rule("body as printed from the nice!nano's strips", moved)
            for moved in places]


def standoff_merges(right=False, fits=layout.DEFAULT_MOUNT_FITS):
    """Where the body may run into the tray instead of keeping clear of
    it: it merges with the half's ledge and joint block as cut, and the
    joint's magnet slots and dowel holes may cut through it, its bore
    keeping its wall from them (standoff_bore_rules()), as the sixth
    standoff merges with the joint block (DESIGN.md, Tray)."""
    pieces = ledge_pieces(right, fits) + magnet_slots() + dowel_holes(right)
    return [PlacementRule("body merging with the tray", "body", layout.STANDOFF_DIAMETER_MM / 2.0,
                          standoff_z_range(), label, "polygon", polygon, z_range, MERGE,
                          survivor="bore from the joint's voids")
            for label, polygon, z_range in pieces]


def standoff_rules(center, right=False, fits=layout.DEFAULT_MOUNT_FITS):
    """Every rule a standoff at center meets on the given half, as the
    checks hold them, and where it may merge instead (standoff_merges()):
    the drill's (on the left half, where check_mounting_drills() holds
    them), the body's from the parts, the sockets (with the flats
    declared at center), the joint's plastic, the parking hole and the
    mounts, the bore's from the joint's voids, and the body's as printed
    from the wire rooms and the nice!nano's strips wherever the board
    can lie. The frame's bosses keep from the standoffs by their own
    rules (frame_boss_rules())."""
    drill = [] if right else standoff_drill_rules()
    return (drill + standoff_part_rules(fits) + standoff_socket_rules(center, right)
            + standoff_joint_rules(right) + standoff_bore_rules(right)
            + standoff_parking_hole_rules() + standoff_mount_rules(fits)
            + standoff_wire_room_rules(layout.wire_rooms(fits, right))
            + standoff_nano_strip_rules(nano_strip_places(fits))
            + standoff_merges(right, fits))


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
    """The slant runs through the thumb cell's and column 5's top cell's
    top right corners moved in by the insets, ends at the latter, and
    runs on south past the former to the outline's south edge."""
    thumb_corner = layout.key_cell_top_right_corner(layout.THUMB_KEY_CENTER_MM)
    column_5_corner = layout.key_cell_top_right_corner(
        layout.KEY_CENTERS_MM[layout.TOP_ROW_KEY_OF_COLUMN_5]
    )
    inset = (-layout.CELL_INSET_EAST_MM, -layout.CELL_INSET_NORTH_MM)
    problems = []
    worst_end_error = 0.0
    for label, corner, point in (
        ("thumb's corner", thumb_corner, layout.SLANT_THUMB_CORNER_MM),
        ("north end", column_5_corner, layout.SLANT_NORTH_END_MM),
    ):
        expected = (corner[0] + inset[0], corner[1] + inset[1])
        error = math.dist(expected, point)
        worst_end_error = max(worst_end_error, error)
        if error > 0.0005:
            problems.append(
                f"the slant's {label} {point} is {error:.4f} from the cell corner {corner} "
                f"moved in by the insets, {expected}"
            )
    off_slant = abs(dot(vector_between(layout.SLANT_SOUTH_END_MM, layout.SLANT_THUMB_CORNER_MM),
                        layout.slant_outward_normal()))
    if off_slant > 1e-9:
        problems.append(f"the thumb's corner lies {off_slant:.2e} off the slant")
    south_edge_y = min(y for _, y in layout.OUTLINE_VERTICES_MM)
    if abs(layout.SLANT_SOUTH_END_MM[1] - south_edge_y) > 1e-9:
        problems.append(
            f"the slant's south end {layout.SLANT_SOUTH_END_MM} is not on the south edge "
            f"(y {south_edge_y})"
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
        require_figure(
            "of it south of the thumb's corner",
            math.dist(layout.SLANT_SOUTH_END_MM, layout.SLANT_THUMB_CORNER_MM),
            DESIGN_SLANT_SOUTH_OF_THUMB_CORNER_MM,
            3,
        ),
        require_figure("degrees from north", angle, DESIGN_SLANT_ANGLE_FROM_NORTH_DEGREES, 2),
    ]
    fail_on(problems + failed(figures), "the slant does not run as DESIGN.md states")
    return (
        f"slant:     through the cell corners less the insets (off by {worst_end_error:.4f} at "
        f"most) on to the south edge at x {layout.SLANT_SOUTH_END_MM[0]:.3f}, " + joined(figures)
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


def check_mounting_drills():
    """The drills by their rules (standoff_drill_rules()), the margin
    inside the outline held without the touching tolerance."""
    drills = layout.MOUNTING_DRILL_CENTERS_MM
    rules = standoff_drill_rules()
    problems = []
    tightest = rule_tallies(rules)
    for drill in drills:
        for rule in rules:
            if not heights_meet(rule):
                continue
            margin = rule_clearance(drill, rule)
            if rule.relation == INSIDE:
                tightest[rule.name].update(margin, f"drill {drill}")
                if margin < rule.minimum:
                    problems.append(f"drill {drill} is {margin:.3f} inside the outline")
                continue
            tightest[rule.name].update(margin, f"drill {drill} and {rule.obstacle}")
            if margin < rule.minimum - TOLERANCE_MM:
                problems.append(f"drill {drill} overlaps {rule.obstacle} by {-margin:.3f}")
    fail_on(problems, "mounting drills off the board or on a switch")
    return (
        f"drills:    {len(drills)} inside the outline, tightest edge "
        f"{tightest['drill inside the outline']}; clear of the switch holes by "
        f"{tightest['drill from the switch holes']}, of the sockets by "
        f"{tightest['drill from the sockets']}"
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
    fail_on(failed(figures), "the heights differ from DESIGN.md's table")
    return f"heights:   PCB underside {layout.PCB_UNDERSIDE_Z_MM}, " + joined(figures)


def nano_figures():
    step_ledge_face_x = layout.COLUMN_1_2_STEP_X_MM + layout.ledge_reach()
    nano = layout.NANO_BOARD
    north_outer_face_y = layout.outer_face_y(layout.NANO_NORTH_EDGE_Y_MM)
    return [
        require_figure(
            "nice!nano width", nano.x_range[1] - nano.x_range[0], DESIGN_NANO_SIZE_MM[0], 2
        ),
        require_figure(
            "nice!nano length", nano.y_range[1] - nano.y_range[0], DESIGN_NANO_SIZE_MM[1], 1
        ),
        require_figure(
            "nice!nano from the column 1/2 step's ledge face",
            nano.x_range[0] - step_ledge_face_x,
            DESIGN_NANO_FROM_STEP_LEDGE_FACE_MM,
            1,
        ),
        require_figure(
            "its center line east of column 2's",
            sum(nano.x_range) / 2.0 - layout.COLUMN_X_MM[2],
            DESIGN_NANO_EAST_OF_COLUMN_2_MM,
            3,
        ),
        require_figure(
            "USB mouth behind the north wall's outer face",
            north_outer_face_y - layout.NANO_USB_SHELL.y_range[1],
            DESIGN_NANO_USB_MOUTH_BEHIND_OUTER_FACE_MM,
            1,
        ),
    ]


def power_switch_figures():
    north_edge_y = layout.POWER_SWITCH_NORTH_EDGE_Y_MM
    return [
        require_figure(
            "power switch on column 0, off its center line by",
            layout.POWER_SWITCH_CENTER_X_MM - layout.COLUMN_X_MM[0], 0.0, 3,
        ),
        require_figure(
            "power switch's north face past the ledge's face",
            layout.POWER_SWITCH_BODY.y_range[1] - layout.ledge_face_y(north_edge_y),
            0.0,
            3,
        ),
        require_figure(
            "knob proud of the outer face",
            layout.POWER_SWITCH_KNOB.y_range[1] - layout.outer_face_y(north_edge_y),
            DESIGN_POWER_SWITCH_KNOB_PROUD_MM[False],
            1,
        ),
        require_figure(
            "as printed", knob_proud_as_printed(), DESIGN_POWER_SWITCH_KNOB_PROUD_MM[True], 1
        ),
    ]


def knob_proud_as_printed():
    """The knob's tip past the outer face as printed: the swollen ledge
    face pushes the snug body south, and the outer face swells north."""
    north_edge_y = layout.POWER_SWITCH_NORTH_EDGE_Y_MM
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    knob_past_body = layout.POWER_SWITCH_KNOB.y_range[1] - layout.POWER_SWITCH_BODY.y_range[1]
    tip = layout.ledge_face_y(north_edge_y) - swelling + knob_past_body
    return tip - (layout.outer_face_y(north_edge_y) + swelling)


def check_part_figures():
    figures = nano_figures() + power_switch_figures()
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
    """(problems, tightest) of every part against the ledge pieces. A
    part proud of the wall passes the ledge and the wall in an opening of
    its own, which check_mount_openings() checks it against."""
    problems = []
    tightest = Tightest()
    for envelope in layout.part_envelopes():
        if envelope.containment == layout.PROUD:
            continue
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
    centers = layout.MOUNTING_DRILL_CENTERS_MM
    problems = []
    tightest = Tightest()
    for rule in standoff_part_rules():
        if not heights_meet(rule):
            continue
        for center in centers:
            clearance = rule_clearance(center, rule)
            where = f"{rule.obstacle} and the standoff at {center}"
            tightest.update(clearance, where)
            if clearance < rule.minimum - TOLERANCE_MM:
                problems.append(f"{where} overlap by {-clearance:.3f}")
    fail_on(problems, "parts on the standoffs")
    return f"standoffs: parts clear by {tightest}"


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


def uncut_declaration_problems(standoff_centers, right=False):
    """Sockets named for a cut that kbdkid4's rule does not make on the
    given half, with the standoffs at standoff_centers."""
    problems = []
    for key in layout.socket_tab_notch_keys(right):
        if not any(not cut.cuts_wall for cut in layout.socket_tab_cuts(key, right)):
            problems.append(f"{key}'s tab tip is not near enough the ledge for the rule's notch")
    for key in layout.socket_ledge_relief_keys(right):
        if not layout.socket_ledge_reliefs(key, right):
            problems.append(f"{key}'s socket is not near enough the ledge for the rule's relief")
    for center, key in layout.socket_standoff_flat_declarations(right):
        if center not in standoff_centers:
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


def thumb_tab_from_joint_block(right=True):
    """How far the thumb's tab tip on the given half lies inside the
    joint block's inner face, the slant's ledge."""
    tip = layout.socket_tab_tip_on_half(layout.THUMB_KEY_NAME, right)
    inside_slant = -dot(vector_between(layout.SLANT_SOUTH_END_MM, tip),
                        layout.slant_outward_normal())
    return inside_slant - (layout.JOINT_BLOCK_THICKNESS_MM - layout.JOINT_FACE_OUTWARD_MM)


def tab_figures(right=False):
    if right:
        return [
            require_figure(
                "the thumb's tab tip from the joint block",
                thumb_tab_from_joint_block(right),
                DESIGN_RIGHT_THUMB_TAB_FROM_JOINT_BLOCK_MM,
                3,
            )
        ]
    keys = layout.socket_tab_notch_keys(right)
    tips = [layout.socket_tab_tip_on_edge(key, right) for key in keys]
    past_edge = [past for _index, _along, past in tips]
    pockets = [cut for key in keys for cut in layout.socket_tab_cuts(key, right) if cut.cuts_wall]
    depths = [cut.across_range[1] - layout.TRAY_GAP_MM for cut in pockets]
    return [
        require_figure_for_all(
            "tab tips past the west edge", past_edge, DESIGN_TAB_TIP_PAST_WEST_EDGE_MM, 3
        ),
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


def closest_socket_to_standoffs(standoff_centers, right=False):
    radius = layout.STANDOFF_DIAMETER_MM / 2.0
    return min(
        circle_separation(center, radius, polygon)
        for center in standoff_centers
        for _name, polygon in socket_footprints(right)
    )


def flat_figures(standoff_centers, right=False):
    if right:
        return [
            require_figure(
                "sockets from the standoffs, without flats",
                closest_socket_to_standoffs(standoff_centers, right),
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
    centers = layout.MOUNTING_DRILL_CENTERS_MM
    fail_on(
        declared_set_problems(right)
        + uncut_declaration_problems(centers, right)
        + thin_flat_problems(right),
        f"{half_label(right)}the sockets' notches, reliefs or flats are off",
    )
    figures = tab_figures(right) + relief_figures(right) + flat_figures(centers, right)
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
    centers = layout.MOUNTING_DRILL_CENTERS_MM
    minimum = layout.STANDOFF_RELIEF_CLEARANCE_MM
    problems = []
    tightest = Tightest()
    for center in centers:
        for rule in standoff_socket_rules(center, right):
            if not heights_meet(rule):
                continue
            clearance = rule_clearance(center, rule)
            standoff = describe_piece(f"standoff at {center}", rule.feature_z_range)
            where = f"{rule.obstacle} and the {standoff}"
            if rule.flats:
                where += f" with {len(rule.flats)} flat{'s' if len(rule.flats) > 1 else ''}"
            tightest.update(clearance, where)
            if clearance < rule.minimum - TOLERANCE_MM:
                problems.append(f"{where}: {clearance:.3f}, less than {rule.minimum}")
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


def dowel_holes(right=False):
    return [
        (
            f"dowel hole at {along} along the slant",
            layout.dowel_hole_polygon(along, right),
            layout.horizontal_hole_z_range(
                layout.DOWEL_PIN_Z_MM, layout.dowel_hole_diameter(right)
            ),
        )
        for along in layout.DOWEL_PIN_ALONGS_MM
    ]


def joint_voids(right=False):
    """(label, plan polygon, z range) of the half's holes and slots in
    the joint and the thumb's wall."""
    parking = (
        "parking hole",
        layout.parking_hole_polygon(),
        layout.horizontal_hole_z_range(layout.PARKING_HOLE_Z_MM, layout.PARKING_HOLE_DIAMETER_MM),
    )
    return magnet_slots() + dowel_holes(right) + [parking]


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
    or the cut-back through the wall. The sixth standoff walls off the
    south 2.165 of the slot at 67.511 along the slant, flush with the
    block's inner face, so the slot still prints 3.1 across there and the
    magnet still drops in from the top."""
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


def joint_socket_problems(label, polygon, z_range, right=False):
    """(problems, tightest) of a piece of the joint's plastic against the
    sockets on the given half: under the PCB it keeps the ledge's
    clearance from them, as the ledge and the parking boss do. It stays
    off the standoffs by their rules (standoff_joint_rules())."""
    minimum = layout.LEDGE_RELIEF_CLEARANCE_MM
    problems = []
    from_sockets = Tightest()
    if ranges_overlap(z_range, socket_z_range()):
        for name, socket in socket_footprints(right):
            clearance = convex_separation(polygon, socket)
            from_sockets.update(clearance, f"{label} and {name}'s socket")
            if clearance < minimum - TOLERANCE_MM:
                problems.append(
                    f"the {label} comes {clearance:.3f} from {name}'s socket, less than {minimum}"
                )
    return problems, from_sockets


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
    """The dowel bosses and their fills clear of the sockets
    (joint_socket_problems()) and of the standoffs by the standoffs'
    rules (standoff_joint_rules())."""
    centers = layout.MOUNTING_DRILL_CENTERS_MM
    problems = fill_problems(right)
    from_sockets = Tightest()
    for label, polygon, z_range in dowel_bosses(right) + boss_fills(right):
        feature_problems, sockets = joint_socket_problems(label, polygon, z_range, right)
        problems.extend(feature_problems)
        from_sockets.update(sockets.value, sockets.where)
    from_standoffs = Tightest()
    for rule in standoff_joint_rules(right):
        if not heights_meet(rule):
            continue
        for center in centers:
            clearance = rule_clearance(center, rule)
            from_standoffs.update(clearance, f"{rule.obstacle} and the standoff at {center}")
            if clearance < rule.minimum - TOLERANCE_MM:
                problems.append(
                    f"the {rule.obstacle} overlaps the standoff at {center} by {-clearance:.3f}"
                )
    ok, text = require_figure(
        "bosses from the sockets", from_sockets.value, DESIGN_BOSSES_FROM_SOCKETS_MM[right], 3
    )
    if not ok:
        problems.append(text)
    fail_on(
        problems,
        f"{half_label(right)}joint plastic too close to the sockets, or in the standoffs' way",
    )
    return (
        f"joint:     {half_label(right)}{text} ({from_sockets.where}), clear of the "
        f"standoffs by {from_standoffs}"
    )


def check_standoff_bores(right=False):
    """Every standoff's insert bore keeps
    layout.STANDOFF_RELIEF_MINIMUM_WALL_MM of plastic from the joint's
    slots and holes in plan wherever their heights meet, so a standoff
    merging with the joint block keeps its bore whole when they are cut
    through it (standoff_bore_rules())."""
    centers = layout.MOUNTING_DRILL_CENTERS_MM
    rules = standoff_bore_rules(right)
    problems = []
    tightest = Tightest()
    for center in centers:
        for rule in rules:
            if not heights_meet(rule):
                continue
            wall = rule_clearance(center, rule)
            where = f"the bore at {center} and the {rule.obstacle}"
            tightest.update(wall, where)
            if wall < rule.minimum - TOLERANCE_MM:
                problems.append(f"{where} leave {wall:.3f} of plastic, less than {rule.minimum}")
    ok, text = require_figure(
        "standoff bores from the joint's voids", tightest.value,
        DESIGN_STANDOFF_BORE_FROM_JOINT_VOIDS_MM, 3
    )
    if not ok:
        problems.append(text)
    fail_on(problems, f"{half_label(right)}a standoff's bore too close to the joint's voids")
    return f"bores:     {half_label(right)}{text} ({tightest.where})"


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


def joint_face_along(y):
    """How far along the slant the joint face crosses y."""
    face_point = (layout.slant_x_at_y(y, layout.JOINT_FACE_OUTWARD_MM), y)
    return dot(vector_between(layout.SLANT_SOUTH_END_MM, face_point), layout.slant_direction())


def check_parking_hole(right=False):
    """The parking hole runs in through the joint face, between the
    slant's ends, its magnet's seat no wider than the hole itself (one
    teardrop serves both). The hole is kept clear in plan of the sockets
    (the thumb's above all) and the standoffs (the one at (114.141,
    19.765) above all, by standoff_parking_hole_rules()) at any height,
    and of the joint's other voids by check_joint_voids(). Its boss may
    merge with the tray's other plastic, but keeps the ledge's clearance
    from the sockets."""
    centers = layout.MOUNTING_DRILL_CENTERS_MM
    hole = layout.parking_hole_polygon()
    low_y, high_y = layout.parking_hole_y_range()
    mouth = (joint_face_along(low_y), joint_face_along(high_y))
    face_margin = min(mouth[0], layout.slant_length() - mouth[1])
    problems = []
    if face_margin < -TOLERANCE_MM:
        problems.append(
            f"the hole's mouth runs from {mouth[0]:.3f} to {mouth[1]:.3f} along the slant, past "
            "the joint face's ends"
        )
    if layout.PARKING_MAGNET_SEAT_DIAMETER_MM > layout.PARKING_HOLE_DIAMETER_MM + TOLERANCE_MM:
        problems.append(
            f"the magnet's seat ({layout.PARKING_MAGNET_SEAT_DIAMETER_MM:.2f}) is wider than the "
            f"hole ({layout.PARKING_HOLE_DIAMETER_MM:.2f}), which is cut in one diameter"
        )
    from_sockets = Tightest()
    for name, polygon in socket_footprints(right):
        from_sockets.update(convex_separation(hole, polygon), f"{name}'s socket")
    from_standoffs = Tightest()  # beyond the rule's minimum
    for rule in standoff_parking_hole_rules():
        if not heights_meet(rule):
            continue
        for center in centers:
            from_standoffs.update(rule_clearance(center, rule) - rule.minimum,
                                  f"the standoff at {center}")
    for tightest in (from_sockets, from_standoffs):
        if tightest.value < -TOLERANCE_MM:
            problems.append(f"the parking hole overlaps {tightest.where} by {-tightest.value:.3f}")
    boss_problems, boss_text = parking_boss_problems(right)
    fail_on(problems + boss_problems, f"{half_label(right)}the parking hole or its boss collides")
    return (
        f"parking:   {half_label(right)}hole {layout.PARKING_HOLE_DIAMETER_MM:.1f} across in "
        f"through the joint face, its mouth from {mouth[0]:.3f} to {mouth[1]:.3f} along the "
        f"slant, clear of the sockets by {from_sockets} and the standoffs by {from_standoffs}, "
        f"{boss_text}"
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
    and the wall's voids from the cavity wall, or the ledge's face where
    they run through the ledge too, to the outer face."""
    cavity = layout.tray_cavity_polygon()
    outer = layout.tray_outer_polygon()
    ledge = layout.ledge_inner_polygon()
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
        problems.extend(wall_opening_problems(opening, cavity, ledge, outer))
    return problems, tightest


def wall_opening_problems(opening, cavity, ledge, outer):
    """An opening's boxes, from the cavity out, run through the wall:
    the first from the cavity wall, or from the ledge's face where it
    runs through the ledge too, each on from where the one before it
    ends, the last out to the outer face."""
    middle_x = sum(opening[0].x_range) / 2.0
    problems = []
    start = (middle_x, opening[0].y_range[0])
    inner = min(point_boundary_distance(start, cavity), point_boundary_distance(start, ledge))
    outside = point_boundary_distance((middle_x, opening[-1].y_range[1]), outer)
    if max(inner, outside) > TOLERANCE_MM:
        problems.append(
            f"the {describe_mount(opening[0])} runs {inner:.3f} off the cavity wall or the "
            f"ledge's face and the {describe_mount(opening[-1])} {outside:.3f} off the outer "
            "face, not through the wall"
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
        "channel and the window and the pin hole through the wall, the knob slot through the "
        "ledge and the wall"
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


def mount_standoff_clearances(standoff_centers, fits=layout.DEFAULT_MOUNT_FITS):
    """(problems, bodies, voids): the mounts against the standoffs at
    standoff_centers by the standoffs' rules (standoff_mount_rules(); the
    standoffs are the same on both halves in the left half's frame),
    with the Tightest of the bodies and of the voids."""
    rules = standoff_mount_rules(fits)
    problems = []
    tightest = {"body from the mount bodies": Tightest(), "body from the mount voids": Tightest()}
    for rule in rules:
        if not heights_meet(rule):
            continue
        for center in standoff_centers:
            clearance = rule_clearance(center, rule)
            where = f"the {rule.obstacle} and the standoff at {center}"
            tightest[rule.name].update(clearance, where)
            if clearance < rule.minimum - TOLERANCE_MM:
                problems.append(f"{where}: {clearance:.3f}, less than {rule.minimum}")
    return (problems, tightest["body from the mount bodies"],
            tightest["body from the mount voids"])


def check_mount_standoffs():
    problems, bodies, voids = mount_standoff_clearances(layout.MOUNTING_DRILL_CENTERS_MM)
    figures = [
        require_figure("voids from the standoffs", voids.value,
                       DESIGN_MOUNT_VOIDS_LEAST_FROM_STANDOFFS_MM, 3),
    ]
    fail_on(problems + failed(figures), "mounts on the standoffs")
    return (f"mounts:    bodies clear of the standoffs by {bodies}; {figures[0][1]} "
            f"({voids.where})")


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
    the pocket's west face and its east face, along between the foot's
    face and the north block's, swollen by the pocket's measured end
    face swelling."""
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    across = ((layout.nano_pocket_east_x(fits) - swelling)
              - (layout.nano_pocket_west_x() + swelling) - fits.nano_width)
    along = (layout.nano_north_stop_y_as_printed(fits) - layout.nano_south_stop_y_as_printed(fits)
             - fits.nano_length)
    return {"across": across, "along": along}


def raised_wall_stretches(side):
    """The y ranges of a wall's raised pieces."""
    return [box.y_range for box in layout.nano_raised_wall_boxes()
            if box.label.startswith(f"{side} wall's")]


def raised_wall_figures():
    """Each wall's raised pieces against DESIGN.md's, and their top."""
    figures = []
    for side, stated in DESIGN_NANO_RAISED_WALLS_Y_MM.items():
        stretches = raised_wall_stretches(side)
        if len(stretches) != len(stated):
            figures.append((False, f"the {side} wall rises over {len(stretches)} stretches, "
                                   f"DESIGN.md says {len(stated)}"))
            continue
        for (low, high), (stated_low, stated_high) in zip(stretches, stated):
            figures.append(require_figure(f"the {side} wall raised from y", low, stated_low, 3))
            figures.append(require_figure("to", high, stated_high, 3))
    tops = {box.z_range[1] for box in layout.nano_raised_wall_boxes()}
    figures.append(require_figure_for_all("their top z", sorted(tops),
                                          DESIGN_NANO_RAISED_WALL_TOP_Z_MM, 1))
    return figures


def nano_bay_figures():
    """The pocket, the board's play in it as printed, the walls and the
    north block at the default fits."""
    pocket = layout.nano_pocket_east_x() - layout.nano_pocket_west_x()
    outer, under_pocket, _south_of_pocket = layout.nano_east_wall_boxes()
    west_outer, west_under_pocket, _ = layout.nano_west_wall_boxes()
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
        require_figure("west wall from x", west_outer.x_range[0], DESIGN_NANO_WEST_WALL_X_MM[0],
                       3),
        require_figure("to", west_under_pocket.x_range[1], DESIGN_NANO_WEST_WALL_X_MM[1], 3),
        require_figure("y", west_outer.y_range[0], DESIGN_NANO_WEST_WALL_Y_MM[0], 3),
        require_figure("to", west_outer.y_range[1], DESIGN_NANO_WEST_WALL_Y_MM[1], 1),
    ] + raised_wall_figures() + [
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
    as printed: west and east the board between the pocket's faces and
    the shell between the north block's sides,
    north the board's USB end before the block."""
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    shell = layout.nano_usb_shell_envelope(fits)
    board = layout.nano_board_envelope(fits)
    west_side, east_side = layout.nano_north_block_boxes(fits)[:2]
    return {
        "west": min(board.x_range[0] - (layout.nano_pocket_west_x() + swelling),
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


def knob_in_slot_margin():
    """The least, as printed, between the knob's swept box and its
    slot."""
    knob = layout.POWER_SWITCH_KNOB
    slot = layout.power_switch_knob_slot_box()
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    margins = []
    for knob_range, slot_range in ((knob.x_range, slot.x_range), (knob.z_range, slot.z_range)):
        margins.append(knob_range[0] - (slot_range[0] + swelling))
        margins.append((slot_range[1] - swelling) - knob_range[1])
    return min(margins)


def power_switch_path_problems():
    """The power switch's body and leads, swept south by the knob's
    length, the path they slide north along with the knob going first
    through its closed slot (DESIGN.md), clear of every mount body."""
    sweep = layout.POWER_SWITCH_KNOB_LENGTH_MM
    problems = []
    for envelope in (layout.POWER_SWITCH_BODY, layout.POWER_SWITCH_LEADS):
        south, north = envelope.y_range
        path = dataclasses.replace(envelope, y_range=(south - sweep, north))
        problems.extend(f"the {describe_mount(body)} stands in the way of the power switch's "
                        f"{envelope.piece} going in"
                        for body in standing_bodies() if box_overlap(path, body) > TOLERANCE_MM)
    return problems


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


def retainer_under_posts(envelope):
    """(least height under them, keys) of the switches' center posts
    and side pegs, at their holes' size, that come within
    DESIGN_MOUNT_FROM_OTHER_PARTS_MM of the retainer in plan."""
    polygon = box_polygon(envelope)
    bottom = layout.PCB_UNDERSIDE_Z_MM - layout.SWITCH_POSTS_BELOW_PCB_MM
    keys = sorted({
        name for name, center in layout.KEY_CENTERS_MM.items()
        for hole_center, diameter in layout.footprint_holes(center)[:3]
        if circle_separation(hole_center, diameter / 2.0, polygon)
        < DESIGN_MOUNT_FROM_OTHER_PARTS_MM
    })
    return bottom - envelope.z_range[1], keys


def retainer_from_sockets(envelope, right):
    polygon = box_polygon(envelope)
    tightest = Tightest()
    for name, socket in socket_footprints(right):
        tightest.update(convex_separation(polygon, socket), f"{name}'s socket")
    return tightest


def check_power_switch_retainer(right=False):
    """The retainer under the posts and pegs over it, kept in its
    socket by the PCB, clear of the sockets in plan, its opening clear of
    the leads as printed and the leads' shortest cut behind it."""
    envelope = layout.power_switch_retainer_envelope()
    under, keys = retainer_under_posts(envelope)
    in_socket = layout.POWER_SWITCH_CRADLE_TOP_Z_MM - (layout.PCB_UNDERSIDE_Z_MM
                                                       - envelope.z_range[1])
    sockets = retainer_from_sockets(envelope, right)
    half_opening, opening_top = layout.power_switch_retainer_opening()
    leads = layout.POWER_SWITCH_LEADS
    beside = (half_opening - layout.PRINT_SWELLING_PER_SIDE_MM
              - (leads.x_range[1] - leads.x_range[0]) / 2.0)
    past = layout.POWER_SWITCH_SHORTEST_LEAD_MM - layout.power_switch_retainer_printed_thickness()
    figures = [
        require_figure("under the posts and pegs of " + ", ".join(keys), under,
                       DESIGN_RETAINER_UNDER_POSTS_MM, 1),
        require_figure("in its socket lifted to the PCB", in_socket,
                       DESIGN_RETAINER_IN_SOCKET_AT_PCB_MM, 1),
        require_figure("from the sockets in plan", sockets.value, DESIGN_RETAINER_FROM_SOCKETS_MM,
                       3),
        require_figure("its opening beside the leads as printed", beside,
                       DESIGN_RETAINER_BESIDE_LEADS_PRINTED_MM, 2),
        require_figure("over them", opening_top - leads.z_range[1], DESIGN_RETAINER_OVER_LEADS_MM,
                       1),
    ]
    problems = failed(figures)
    if sockets.value < DESIGN_MOUNT_FROM_OTHER_PARTS_MM - TOLERANCE_MM:
        problems.append(f"the retainer comes {sockets.value:.3f} from {sockets.where}")
    if past < TOLERANCE_MM:
        problems.append("the power switch's leads cut to the shortest end inside the retainer")
    fail_on(problems, f"{half_label(right)}the power switch's retainer off DESIGN.md")
    return (f"retainer:  {half_label(right)}{joined(figures)} ({sockets.where}); the shortest "
            f"leads {past:.2f} past it")


def opening_problems(fits=layout.DEFAULT_MOUNT_FITS):
    """The knob over its whole sweep and the shell, wherever its play lets
    it go, clear of their openings as printed, and the power switch's
    way in clear."""
    in_channel = shell_in_channel_margins(fits)
    problems = power_switch_path_problems()
    if knob_in_slot_margin() < -TOLERANCE_MM or min(in_channel.values()) < -TOLERANCE_MM:
        problems.append("the knob or the shell does not clear its opening as printed")
    return problems


def check_mount_openings():
    """The knob passes its slot and the shell its channel as printed,
    the power switch slides in with its knob through the slot, the shell
    wherever its play lets it go, the bar reaches the shell's
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
        require_figure("knob in its slot as printed", knob_in_slot_margin(),
                       DESIGN_KNOB_IN_SLOT_PRINTED_MM, 2),
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
        require_figure("z", hole_z, DESIGN_RESET_PIN_HOLE_AXIS_MM[1], 3),
    ]
    fail_on(failed(figures) + opening_problems() + insertion_problems(),
            "the mounts' openings off DESIGN.md")
    return (f"openings:  {joined(figures)} (least at {angle:.2f} degrees, the shell then "
            f"{bar_margin:.3f} under the bar as printed)")


def wire_room_depths():
    """(behind the leads, over the nice!nano's pads): each lead room's
    smaller extent in plan, the room behind the lead, and each pad
    room's height."""
    behind = [min(plan_side_lengths(room)) for room in layout.lead_wire_rooms()]
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


def standoff_problems(standoff_centers, rules, tightest):
    """The problems of envelopes reaching into the standoffs at
    standoff_centers as printed, by the standoffs' rules
    (standoff_printed_rule()), the Tightest updated."""
    problems = []
    for rule in rules:
        if not heights_meet(rule):
            continue
        for center in standoff_centers:
            clearance = rule_clearance(center, rule)
            tightest.update(clearance, f"the {rule.obstacle} and the standoff at {center}")
            if clearance < rule.minimum - TOLERANCE_MM:
                problems.append(f"the {rule.obstacle} reaches into the standoff at {center}")
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


def wire_room_problems(standoff_centers, right, fits=layout.DEFAULT_MOUNT_FITS):
    """(problems, tightest, overlaps) of every wire room against its
    obstacles and the standoffs at standoff_centers, the printed plastic
    as printed, and of the nice!nano's pad rooms against its own strips
    and tails: those overlaps as {(room's piece, strip's label): how
    far}, any DESIGN.md does not name a problem."""
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
        problems.extend(standoff_problems(standoff_centers, standoff_wire_room_rules([room]),
                                          tightest))
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
    problems, tightest, overlaps = wire_room_problems(layout.MOUNTING_DRILL_CENTERS_MM, right)
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
# pockets in the bay's walls and the step's ledge see to. How far the
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


def nano_strip_places(fits=layout.DEFAULT_MOUNT_FITS, block_shares=WORST_SPLITS):
    """The strips and the rooms over them moved to each of the board's
    extreme places at the end faces' splits (nano_board_places())."""
    return [shifted_envelope(envelope, offset)
            for offset in nano_board_places(fits, block_shares)
            for envelope in layout.nano_strip_envelopes(fits) + layout.nano_strip_rooms(fits)]


def nano_strip_clearances(standoff_centers, right, fits=layout.DEFAULT_MOUNT_FITS,
                          block_shares=WORST_SPLITS):
    """(problems, tightest) of the strips and the rooms over them against
    the half's tray as printed, the standoffs at standoff_centers
    included, at each of the board's places (nano_strip_places())."""
    obstacles = printed_tray_obstacles(right, fits)
    problems = []
    tightest = Tightest()
    for moved in nano_strip_places(fits, block_shares):
        problems.extend(clearance_problems(moved, obstacles, tightest))
        problems.extend(standoff_problems(standoff_centers, standoff_nano_strip_rules([moved]),
                                          tightest))
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
    centers = layout.MOUNTING_DRILL_CENTERS_MM
    problems, worst = nano_strip_clearances(centers, right)
    tightest = nano_strip_clearances(centers, right, block_shares=EVEN_SPLIT)[1]
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


def pry_toothpick_corners(standoff_centers, right, fits=layout.DEFAULT_MOUNT_FITS):
    """(label, (y, z)) as printed of the north top edge of everything
    the toothpick crosses south of the board within the slot's width,
    the half's ledge, walls, dowel bosses and fills, the standing bodies
    but the clamp's block and foot, which the slot runs through, the
    standoffs at standoff_centers and the parts but the nice!nano, the
    tray's grown by the swelling and its tops by a top face's rise."""
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
    for center in standoff_centers:
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


def pry_toothpick_pose(standoff_centers, right, fits=layout.DEFAULT_MOUNT_FITS, board_shift=0.0):
    """(the least angle in degrees, how far the point then gets under
    the board's south edge, the recess left north of it, the corner that
    sets the angle), as printed, the board moved board_shift north of
    its modelled place, the standoffs at standoff_centers. Where no
    angle brings the point under the board, the reach is minus infinity
    at the steepest angle tried, and the corner is the one that stops it
    there."""
    swelling = layout.PRINT_SWELLING_PER_SIDE_MM
    recess = layout.nano_pry_recess_box(fits)
    bottom = recess.z_range[0] + layout.PRINT_RISE_OF_UP_FACING_BOTTOMS_MM
    under_board = layout.nano_board_envelope(fits).z_range[0] - bottom
    board_south = layout.nano_south_end_y(fits) + board_shift
    recess_end = recess.y_range[1] - swelling
    corners = pry_toothpick_corners(standoff_centers, right, fits)

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


def pry_toothpick_worst_pose(standoff_centers, right, fits=layout.DEFAULT_MOUNT_FITS,
                             block_shares=WORST_SPLITS):
    """pry_toothpick_pose() with the board at whichever of its stops as
    printed, at the end faces' splits, leaves the point the least far
    under it."""
    shifts = sorted({dy for _, dy in nano_board_places(fits, block_shares)})
    return min((pry_toothpick_pose(standoff_centers, right, fits, shift) for shift in shifts),
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


def pry_slot_problems(standoff_centers, right, fits=layout.DEFAULT_MOUNT_FITS):
    """The slot clear of its obstacles, the recess leaving the floor
    under it, and a toothpick's point getting under the board within the
    recess, past the standoffs at standoff_centers."""
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
    angle, reach, _room, where = pry_toothpick_worst_pose(standoff_centers, right, fits)
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
    centers = layout.MOUNTING_DRILL_CENTERS_MM
    angle, reach, room, where = pry_toothpick_worst_pose(centers, right, block_shares=EVEN_SPLIT)
    worst_reach = pry_toothpick_worst_pose(centers, right)[1]
    lane = pry_toothpick_lane()
    figures = [
        require_figure("slot from x", slot.x_range[0], DESIGN_PRY_SLOT_X_MM[0], 1),
        require_figure("to", slot.x_range[1], DESIGN_PRY_SLOT_X_MM[1], 1),
        require_figure("from the pocket's west face", slot.x_range[0] - layout.nano_pocket_west_x(),
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
    fail_on(pry_slot_problems(centers, right) + failed(figures),
            f"{half_label(right)}the nice!nano's pry slot off DESIGN.md")
    clearance = pry_slot_clearance(right)
    return (f"pry slot:  {half_label(right)}{joined(figures)}; the slot clear in plan by "
            f"{clearance}; the toothpick's angle set by the {where}, its point {room:.3f} short "
            "of the recess's end")


# The hand-wired frame (work item 014): its bosses and its backing, in
# the left half's frame on both halves. The tray's pieces are taken
# where their z ranges reach the bosses (from the backing's top up to
# the frame's underside), the screw heads under the backing (as printed)
# or the backing itself.


def frame_key_center(key, right):
    center = layout.KEY_CENTERS_MM[key]
    return layout.mirror_for_right_half(center) if right else center


def frame_left_point(point, right):
    return layout.mirror_for_right_half(point) if right else point


def frame_local_box(key, right, x_range, y_range):
    """A footprint-local box on the half, in the left half's frame."""
    center = frame_key_center(key, right)
    points = [frame_left_point(layout.footprint_point(center, corner), right)
              for corner in layout.box_corners(x_range, y_range)]
    return layout.counter_clockwise(points)


def frame_tab_pieces(key, right):
    """(slots, wire rooms) of a socket's two tabs: the slot from the
    body's end to DESIGN_FRAME_TAB_SLOT_PAST_TIP_MM past the tip,
    DESIGN_FRAME_TAB_SLOT_WIDTH_MM wide, and the room past the tip by
    layout.py's wire room rule."""
    low, high = layout.HOTSWAP_SOCKET_BODY_ENDS_MM
    slots, rooms = [], []
    for polygon in layout.HOTSWAP_SOCKET_TABS_MM:
        xs = [x for x, _ in polygon]
        ys = [y for _, y in polygon]
        face, tip = (high, max(ys)) if min(ys) >= high else (low, min(ys))
        outward = 1.0 if tip > face else -1.0
        middle = (min(xs) + max(xs)) / 2.0
        width = max(xs) - min(xs)
        slot_end = tip + outward * DESIGN_FRAME_TAB_SLOT_PAST_TIP_MM
        slots.append(frame_local_box(key, right, layout.centered_range(middle, DESIGN_FRAME_TAB_SLOT_WIDTH_MM),
                                     tuple(sorted((face, slot_end)))))
        room_end = tip + outward * layout.WIRE_ROOM_BEHIND_LEADS_MM
        rooms.append(frame_local_box(
            key, right, layout.centered_range(middle, width + 2.0 * layout.WIRE_ROOM_BESIDE_LEADS_MM),
            tuple(sorted((tip, room_end)))))
    return slots, rooms


def frame_own_obstacles(right):
    """(label, kind, shape, minimum) of the frame's features a boss keeps
    from: the walls (their outer face, not convex), the tab slots and
    wire rooms and the footprint holes as the frame has them."""
    obstacles = []
    for key in layout.KEY_CENTERS_MM:
        obstacles.append((f"{key}'s walls", "outline", layout.frame_wall_outer_polygon(key, right),
                          layout.FRAME_BOSS_FROM_FRAME_MM))
        slots, rooms = frame_tab_pieces(key, right)
        obstacles.extend((f"{key}'s tab slot", "polygon", slot, layout.FRAME_BOSS_FROM_FRAME_MM)
                         for slot in slots)
        obstacles.extend((f"{key}'s tab wire room", "polygon", room,
                          layout.FRAME_BOSS_FROM_WIRE_ROOMS_MM) for room in rooms)
        holes = layout.footprint_holes(frame_key_center(key, right))
        obstacles.extend(
            (f"{key}'s {diameter} hole", "circle",
             (frame_left_point(center, right), diameter / 2.0), layout.FRAME_BOSS_FROM_FRAME_MM)
            for (center, _), diameter in zip(holes, DESIGN_FRAME_HOLE_DIAMETERS_MM)
        )
    return obstacles


def frame_tray_obstacles(standoff_centers, right):
    """(label, kind, shape, z range) of the tray as the frame meets it:
    the ledge as cut, the cavity wall, the joint's bosses and fills, the
    parking boss, the standoffs at standoff_centers (whole, without the
    sockets' flats), the mounts, the parts (but the PCB connector's
    zone, which the frame does not have) and the wire rooms."""
    obstacles = [(label, "polygon", polygon, z_range) for label, polygon, z_range in
                 ledge_pieces(right) + wall_pieces(right) + dowel_bosses(right) + boss_fills(right)]
    obstacles.append(("parking boss", "polygon", layout.parking_boss_polygon(),
                      layout.parking_boss_z_range()))
    obstacles.extend((f"standoff at {center}", "circle", (center, layout.STANDOFF_DIAMETER_MM / 2.0),
                      standoff_z_range()) for center in standoff_centers)
    boxes = list(layout.mount_bodies()) + list(layout.nano_clamp_part_boxes())
    obstacles.extend((describe_mount(box), "polygon", box_polygon(box), box.z_range) for box in boxes)
    envelopes = [envelope for envelope in layout.part_envelopes() if envelope.part != "PCB connector"]
    envelopes.extend(layout.wire_rooms(right=right))
    obstacles.extend((describe_envelope(envelope), "polygon", box_polygon(envelope), envelope.z_range)
                     for envelope in envelopes)
    return obstacles


def frame_boss_z_range():
    """A boss's heights: from the backing's top to the frame's
    underside."""
    return (DESIGN_FRAME_BACKING_TOP_Z_MM, layout.PCB_UNDERSIDE_Z_MM)


def frame_head_z_range():
    """A boss's screw head's heights, under the backing as printed."""
    return (DESIGN_FRAME_SCREW_HEADS_BOTTOM_Z_MM, DESIGN_FRAME_BACKING_UNDERSIDE_PRINTED_Z_MM)


def frame_boss_clearance_rules(standoff_centers, right):
    """(PlacementRule) of a boss of the half's frame against what is
    around it, by layout.py's rules: the boss clear of the frame's own
    features at any height (frame_own_obstacles()), the boss and its
    screw head layout.FRAME_TRAY_CLEARANCE_MM from the tray where their
    heights meet (frame_tray_obstacles(), with the standoffs at
    standoff_centers), the boss layout.FRAME_BOSS_EDGE_MARGIN_MM inside
    the outline pulled in by the print's swelling, and
    layout.FRAME_BOSS_FROM_FRAME_MM from the other bosses (APART)."""
    radius = layout.STANDOFF_DIAMETER_MM / 2.0
    head_radius = layout.FRAME_BACKING_SCREW_HEAD_DIAMETER_MM / 2.0
    boss_z = frame_boss_z_range()
    head_z = frame_head_z_range()
    tray_minimum = layout.FRAME_TRAY_CLEARANCE_MM
    rules = [PlacementRule("boss from the frame", "boss", radius, boss_z, label, kind, shape, None,
                           CLEAR, minimum)
             for label, kind, shape, minimum in frame_own_obstacles(right)]
    for label, kind, shape, z_range in frame_tray_obstacles(standoff_centers, right):
        rules.append(PlacementRule("boss from the tray", "boss", radius, boss_z, label, kind, shape,
                                   z_range, CLEAR, tray_minimum))
        rules.append(PlacementRule("head from the tray", "head", head_radius, head_z, label, kind,
                                   shape, z_range, CLEAR, tray_minimum))
    outline = layout.offset_polygon(layout.OUTLINE_VERTICES_MM, -DESIGN_PULL_IN_MM)
    rules.append(PlacementRule("boss inside the outline", "boss", radius, boss_z,
                               "the frame's outline", "outline", outline, None, INSIDE,
                               layout.FRAME_BOSS_EDGE_MARGIN_MM))
    rules.append(PlacementRule("bosses apart", "boss", radius, boss_z, "the other bosses", "circle",
                               None, boss_z, APART, layout.FRAME_BOSS_FROM_FRAME_MM))
    return rules


def frame_head_backing_rules(right):
    """(PlacementRule) of a boss's screw head on the half's backing, in
    plan: inside the backing's outline and clear of its cutouts
    (check_frame_backing())."""
    head_radius = layout.FRAME_BACKING_SCREW_HEAD_DIAMETER_MM / 2.0
    head_z = frame_head_z_range()
    rules = [PlacementRule("head on the backing", "head", head_radius, head_z, "the outline",
                           "outline", layout.frame_backing_outline(), None, INSIDE)]
    rules.extend(PlacementRule("head from the backing's cutouts", "head", head_radius, head_z,
                               f"the cutout {label}", kind, shape)
                 for label, kind, shape in frame_backing_cutouts(right))
    return rules


def frame_boss_rules(standoff_centers, right):
    """Every rule a boss of the half's frame meets, the standoffs at
    standoff_centers: its clearances (frame_boss_clearance_rules()) and
    its screw head's on the backing (frame_head_backing_rules())."""
    return frame_boss_clearance_rules(standoff_centers, right) + frame_head_backing_rules(right)


def frame_boss_where(center, rule):
    """How check_frame_bosses() names a rule of the boss at center."""
    if rule.obstacle_z_range is None:
        return f"{center} and {rule.obstacle}"
    feature = f"{center}'s head" if rule.feature == "head" else f"{center}"
    return f"{feature} and the {describe_piece(rule.obstacle, rule.obstacle_z_range)}"


def frame_boss_figures(boss_centers, standoff_centers, right):
    """(problems, {rule name: tightest beyond the rule}) of the bosses at
    boss_centers by their rules (frame_boss_clearance_rules())."""
    rules = frame_boss_clearance_rules(standoff_centers, right)
    problems = []
    tightest = rule_tallies(rules)

    def tally(rule, value, where):
        tightest[rule.name].update(value - rule.minimum, where)
        if value < rule.minimum - TOLERANCE_MM:
            problems.append(f"the boss at {where}: {value:.3f}, less than {rule.minimum}")

    for center in boss_centers:
        for rule in rules:
            if rule.relation != APART and heights_meet(rule):
                tally(rule, rule_clearance(center, rule), frame_boss_where(center, rule))
    for rule in rules:
        if rule.relation == APART:
            for first, second in itertools.combinations(boss_centers, 2):
                tally(rule, math.dist(first, second) - 2.0 * rule.radius,
                      f"{first} and the boss at {second}")
    return problems, tightest


def check_frame_bosses(right=False):
    """The frame's bosses by layout.py's rules, their count DESIGN.md's."""
    boss_centers = layout.frame_boss_centers(right)
    problems, tightest = frame_boss_figures(boss_centers, layout.MOUNTING_DRILL_CENTERS_MM, right)
    figures = [require_figure("bosses", len(boss_centers), DESIGN_FRAME_BOSS_COUNT[right], 0)]
    fail_on(problems + failed(figures), f"{half_label(right)}the frame's bosses off their rules")
    return (f"frame:     {half_label(right)}{joined(figures)}, beyond their rules by at least "
            f"{tightest['boss from the frame']} from the frame, {tightest['boss from the tray']} "
            f"from the tray, {tightest['head from the tray']} with their heads, "
            f"{tightest['boss inside the outline']} inside the outline, "
            f"{tightest['bosses apart']} apart")


def frame_backing_cutouts(right):
    """(label, kind, shape) of the backing's cutouts."""
    cutouts = [(label, "circle", (center, radius))
               for label, center, radius in layout.frame_backing_circle_cutouts()]
    cutouts.extend((label, "polygon", polygon)
                   for label, polygon in layout.frame_backing_polygon_cutouts(right))
    return cutouts


def tray_piece_handled(kind, shape, outline, cutouts):
    """How far a tray piece standing into the backing's heights keeps
    from the backing: outside its outline, or inside one of its
    cutouts, whichever leaves more."""
    if kind == "circle":
        center, radius = shape
        best = -signed_point_distance(center, outline) - radius
        for _label, cutout_kind, cutout in cutouts:
            if cutout_kind == "circle":
                best = max(best, cutout[1] - math.dist(center, cutout[0]) - radius)
        return best
    outside = [-signed_point_distance(corner, outline) for corner in shape]
    best = -math.inf
    if min(outside) > 0.0 and not any(point_in_polygon(vertex, shape) for vertex in outline):
        best = boundary_distance(shape, outline)
    for _label, cutout_kind, cutout in cutouts:
        if cutout_kind == "polygon":
            best = max(best, containment_margin(shape, cutout))
    return best


def check_frame_backing(right=False):
    """The backing: every pad inside its outline and clear of its
    cutouts, every screw head on it, and every tray piece standing into
    its heights outside it or inside a cutout, the heads by their rules
    (frame_head_backing_rules())."""
    boss_centers = layout.frame_boss_centers(right)
    standoff_centers = layout.MOUNTING_DRILL_CENTERS_MM
    outline = layout.frame_backing_outline()
    cutouts = frame_backing_cutouts(right)
    pads = layout.frame_pad_boxes(right)
    backing_z = (DESIGN_FRAME_BACKING_UNDERSIDE_PRINTED_Z_MM, DESIGN_FRAME_BACKING_TOP_Z_MM)
    problems = []
    pad_room, head_room, tray_room = Tightest(), Tightest(), Tightest()
    for key, x_range, y_range in pads:
        pad = layout.box_corners(x_range, y_range)
        pad_room.update(containment_margin(pad, outline), f"{key}'s pad and the outline")
        for label, kind, shape in cutouts:
            clearance = (circle_separation(shape[0], shape[1], pad) if kind == "circle"
                         else convex_separation(pad, shape))
            pad_room.update(clearance, f"{key}'s pad and the cutout {label}")
    head_rules = frame_head_backing_rules(right)
    for center in boss_centers:
        for rule in head_rules:
            if heights_meet(rule):
                head_room.update(rule_clearance(center, rule) - rule.minimum,
                                 f"the head at {center} and {rule.obstacle}")
    for label, kind, shape, z_range in frame_tray_obstacles(standoff_centers, right):
        if ranges_overlap(z_range, backing_z):
            tray_room.update(tray_piece_handled(kind, shape, outline, cutouts),
                             f"the {describe_piece(label, z_range)}")
    if len(pads) != 2 * len(layout.KEY_CENTERS_MM):
        problems.append(f"{len(pads)} pads for {len(layout.KEY_CENTERS_MM)} sockets")
    if pad_room.value < layout.FRAME_TRAY_CLEARANCE_MM - TOLERANCE_MM:
        problems.append(f"a pad keeps {pad_room}")
    if head_room.value < -TOLERANCE_MM:
        problems.append(f"a screw head is off the backing by {head_room}")
    if tray_room.value < layout.FRAME_TRAY_CLEARANCE_MM - TOLERANCE_MM:
        problems.append(f"the tray reaches the backing: {tray_room}")
    fail_on(problems, f"{half_label(right)}the frame's backing")
    strips = len(layout.frame_strip_cutouts(right))
    return (f"backing:   {half_label(right)}{len(pads)} pads inside it and clear of its cutouts by "
            f"{pad_room}, the screw heads on it by {head_room}, the tray clear of it by "
            f"{tray_room}, {strips} cutouts over the nice!nano's strips")


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
    check_standoff_bores,
    on_right_half(check_standoff_bores),
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
    check_power_switch_retainer,
    on_right_half(check_power_switch_retainer),
    check_pry_slot,
    on_right_half(check_pry_slot),
    check_wire_rooms,
    on_right_half(check_wire_rooms),
    check_frame_bosses,
    on_right_half(check_frame_bosses),
    check_frame_backing,
    on_right_half(check_frame_backing),
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
