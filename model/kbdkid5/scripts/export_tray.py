"""Export a half's 3D-printable tray shell and joint (STL) from the layout.

tray_shape.py builds the tray (see its docstring): walls, floor, ledge
and joint block, the shelves on the ledge's face, standoffs bored for
M2 heat-set inserts, the dowel pin and parking bosses with their
fills, the ledge cut-aways and the sockets' cuts as layout.py gives
them, the parts' mounts, the reliefs under the switches' center posts
and side pegs, the magnet
slots, the flat-topped teardrop pin holes and parking hole, and the
joint face's bottom chamfer. This script mirrors it for the right half,
measures it and prints what it found against DESIGN.md's figures, which
it transcribes itself (the DESIGN_* constants below), never against the
constants the tray is built from: the outside's size, the walls, the
floor, the ledge and the joint block, the shelves under the hand-wired
frame's backing (each straight run of their face, its height and
reach, and the notches for the backing's screw heads), the standoffs
and their bores, their tops at the hand-wired frame's tubes' mouth
(the one merged with the joint block, its bore's plastic toward the
magnet slot cut through it and the block's inner face beside its axis
over its top), the joint face's angle, place and bottom
chamfer, the pin holes (depth, diameter, the plastic behind and over
them, the flat top, the lead-in),
the magnet slots, the parking hole, the reliefs under the switches'
center posts and side pegs (across at the mouth, the bottom, open over
the post's or peg's place), the sockets' clearance from the
tray as built, the hand-wired frame's pocket walls' clearance from it
(work item 026) and its tubes' (work item 034), the standoffs they
stand on left out, and the mounts: the USB shell's channel and the USB
window, the nice!nano's north block with the bar over the shell, the
screw clamp (its block and foot, the insert bore, and its tab,
tray_shape.py's, seated on the block, overlapping nothing of the
tray), the pocket and the west and east walls with their raised
pieces, the seat with its channels and the socket strips' pockets, the pry slot
and recess, the knob slot, the power switch's stop (with how far the
knob's peaks and trough stand from the outer face as built, as
modelled and as printed) and the cradle, the reset pin hole and the
back wall, and that the PCB connector's zone, layout.py's wire rooms
and the nice!nano's socket strips with the rooms over them hold no
plastic as printed.
build_tray() itself checks that no void reaches the floor's underside,
and this script prints the underside it found closed. Then it builds the
other half too and joins them as DESIGN.md describes, each half turned
17.74 degrees so the outer slant faces touch, and checks that the trays
do not overlap, that the pin holes line up into one channel at least
1.0 longer than the pin, and that the magnet slots face each other.
Last, it writes the tray as built, floor on the bed, as one closed mesh.

Runs headless under FreeCAD's console interpreter (see
freecad_common.py for the freecadcmd quirks that shape the
invocation):

    freecadcmd model/kbdkid5/scripts/export_tray.py --pass <tray.stl> [right] [key=value ...]

The word "right" makes the right half: the tray built with that half's
socket cuts and its slip fit pin holes, mirrored across the layout's
right-half mirror line. The key=value words (USAGE lists them) override
a fit for a test print: pin_hole_diameter the half's pin hole fit
(layout.py: the left half's snug, the right half's slip, as modelled),
the others the mounts' fits that wait on a caliper or a test print
(layout.MountFits).
A measured figure that is an override is then checked against it
instead of DESIGN.md's, and the figures that follow from it (the pin
holes' flat top and the plastic over them, the room the clamp's bore
leaves the insert) are only printed. The other half, built for the
joined check, keeps the defaults.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App
import Part

import layout
import socket_test_shape as cells
from freecad_common import check_closed_mesh, export_stl, run_and_exit, script_arguments
from tray_shape import UP, build_clamp_tab, build_tray, mirror_for_right_half

# DESIGN.md's figures, transcribed independently of layout.py, each
# compared within half its last digit.
DESIGN_TRAY_OUTSIDE_MM = (134.8, 85.0, 14.6)  # along x, along y, tall
DESIGN_FLOOR_UNDERSIDE_Z_MM = -1.2
DESIGN_RIM_Z_MM = 13.4
DESIGN_GAP_MM = 0.4
DESIGN_WALL_MM = 0.8
DESIGN_FLOOR_MM = 1.2
DESIGN_LEDGE_WIDTH_MM = 1.0
DESIGN_LEDGE_UNDER_PCB_MM = 0.6
DESIGN_LEDGE_TOP_Z_MM = 9.5  # the PCB's underside, also the block's top
DESIGN_STANDOFF_TOP_Z_MM = 7.7  # the hand-wired frame's tubes' mouth (work item 034)
DESIGN_STANDOFF_DIAMETER_MM = 5.8
DESIGN_STANDOFF_BORE_MM = 3.2
DESIGN_MOUNTING_DRILLS_MM = (
    (18.574, 18.732),
    (18.574, 56.832),
    (56.091, 23.460),
    (75.724, 62.785),
    (114.141, 19.765),
    (113.824, 59.214),
)
# The sixth standoff merges with the joint block, the magnet slot at
# 48.26 along the slant cut through it, and its bore keeps this much
# plastic toward the slot. Over its top the block's inner face stands
# this far from its axis, beside an insert pressed in from above. The
# axis lies across the slot, which opens toward the cavity over the
# standoff's top, so the face is probed this far south of the slot.
DESIGN_MERGED_STANDOFF_BORE_WALL_MM = 0.83
DESIGN_MERGED_STANDOFF_AXIS_FROM_BLOCK_MM = 2.432
MERGED_AXIS_PROBE_PAST_SLOT_MM = 0.5
DESIGN_MIRROR_LINE_X_MM = 66.199
DESIGN_SLANT_ENDS_MM = ((132.398, 18.335), (113.348, 77.867))  # south, north
DESIGN_SLANT_ANGLE_FROM_NORTH_DEGREES = 17.74
DESIGN_JOINT_FACE_OUT_OF_SLANT_MM = 1.2
DESIGN_JOINT_FACE_BOTTOM_CHAMFER_MM = 0.4
DESIGN_JOINT_BLOCK_THICKNESS_MM = 4.0
DESIGN_DOWEL_PIN_ALONGS_MM = (3.5, 59.0)
DESIGN_DOWEL_PIN_SPACING_MM = 55.5
DESIGN_DOWEL_PIN_Z_MM = 4.15  # midway between the bed and the PCB
# Per half, False the left one, True the right one: the left half's
# holes snug and the pin's stop, the right half's slip.
DESIGN_DOWEL_HOLE_DIAMETER_MM = {False: 4.4, True: 4.5}
DESIGN_DOWEL_HOLE_DEPTH_MM = {False: 8.2, True: 9.0}
DESIGN_DOWEL_BOSS_BEHIND_HOLE_MM = {False: 1.2, True: 1.0}
DESIGN_DOWEL_BOSS_REACH_MM = {False: 9.4, True: 10.0}
DESIGN_DOWEL_HOLE_LEAD_IN_MM = {False: 0.0, True: 0.3}
DESIGN_DOWEL_HOLE_FLAT_MM = {False: 1.82, True: 1.86}  # the flat top's width
DESIGN_PLASTIC_OVER_DOWEL_HOLES_MM = {False: 3.15, True: 3.1}
DESIGN_DOWEL_BOSS_ACROSS_MM = 7.0
DESIGN_DOWEL_PIN_LENGTH_MM = 16.0
DESIGN_PIN_CHANNEL_MARGIN_MM = 1.0  # the joined channel's length past the pin's, as modelled
DESIGN_MAGNET_ALONGS_MM = (14.24, 25.58, 36.92, 48.26)
DESIGN_MAGNET_SLOT_MM = (8.5, 3.5)  # along the slant, across it
DESIGN_MAGNET_SLOT_BOTTOM_Z_MM = -0.7
DESIGN_MAGNET_SKIN_MM = 0.5
DESIGN_MAGNETS_APART_JOINED_MM = 1.0
DESIGN_THUMB_EAST_EDGE_X_MM = 132.398
DESIGN_PARKING_HOLE_DIAMETER_MM = 4.5
DESIGN_PARKING_HOLE_FLAT_MM = 1.86
DESIGN_PLASTIC_OVER_PARKING_HOLE_MM = 3.85
DESIGN_PARKING_HOLE_Y_MM = 13.1
DESIGN_PARKING_HOLE_Z_MM = 3.4
DESIGN_PARKING_HOLE_DEPTH_MM = 16.5  # the pin's 14.5 and the magnet's 2.0
DESIGN_PARKING_BOSS_ACROSS_MM = 7.0
DESIGN_PARKING_BOSS_BEHIND_HOLE_MM = 1.5
# The reliefs under the switches' center posts and side pegs (work item
# 023), at the same places on both halves in the left half's frame:
# (the left half's key, its post or peg and the body, the post's or
# peg's center, its footprint hole across, the way into the body the
# relief is cut into, the relief across), the right half's named for
# the key's right twin. "slant" is the slant's direction north,
# ("corner", point) the way toward that corner of the body: the raised
# east wall's pieces give way to the frame's pocket walls of S131 and
# S130 (S231 and S230 on the right half, work item 026), so their pegs'
# reliefs cross the pieces' south east corners. The posts and pegs end
# at z 8.1.
DESIGN_POST_RELIEFS = (
    ("S163", "post in the parking boss", (123.349, 9.207), 3.4, (0.0, 1.0), 4.8),
    ("S163", "peg in the parking boss", (117.849, 9.207), 1.9, (0.0, 1.0), 3.3),
    ("S163", "peg in the parking boss", (128.849, 9.207), 1.9, (0.0, 1.0), 3.3),
    ("S150", "peg in the upper dowel boss", (109.799, 68.739), 1.9, "slant", 3.3),
    ("S131", "peg in the nice!nano's raised east wall", (60.699, 54.451), 1.9,
     ("corner", (59.124, 54.503)), 3.3),
    ("S130", "peg in the nice!nano's raised east wall", (60.699, 73.501), 1.9,
     ("corner", (59.124, 73.553)), 3.3),
)
DESIGN_POST_RELIEF_BOTTOM_Z_MM = 7.4
DESIGN_POST_ENDS_Z_MM = 8.1
DESIGN_SOCKET_BOTTOM_Z_MM = 7.48
# The least any socket keeps from the tray as cut: the ledge relief's
# and the tab pocket's clearance.
DESIGN_LEAST_SOCKET_CLEARANCE_MM = 0.5
# The hand-wired frame's pocket walls, whole (work item 026): their
# outer face out of the socket, their heights in the tray, the frame in
# the PCB's place, and the least the tray as cut keeps from them. It
# may come up to FRAME_WALL_ARC_TOLERANCE_MM nearer: layout.py cuts the
# tray for the walls with the socket's arcs in steps of 3 degrees, and
# the walls here have the true arcs.
DESIGN_FRAME_WALL_REACH_MM = 0.925
DESIGN_FRAME_WALLS_Z_MM = (7.7, 9.5)
DESIGN_FRAME_WALL_CLEARANCE_MM = 0.5
FRAME_WALL_ARC_TOLERANCE_MM = 0.001
# The hand-wired frame's tubes (work item 034): the standoffs' circles
# over the walls' heights, their mouth on the standoffs' tops, the one
# whose standoff merges with the joint block cut the walls' clearance
# short of the block's inner face, and the least the tray as cut keeps
# from them.
DESIGN_FRAME_TUBES_FROM_TRAY_MM = 0.5
# The walls and the tubes are measured against the tray less its
# standoffs (tray_without_standoffs()), each cut away as a cylinder this
# much wider than it, from this height to this far past its top.
STANDOFF_CUTTER_MARGIN_MM = 0.01
STANDOFF_CUTTER_BOTTOM_Z_MM = 0.5
STANDOFF_CUTTER_PAST_TOP_MM = 1.0
# The shelves under the hand-wired frame's backing's edges (DESIGN.md,
# "Tray", Shelves), the left half's: their face as modelled, sharp, in
# two runs, from the outer edge's shelf's start at the ledge's face to
# the thumb's ledge and from the north edges' start at the ledge's face
# to column 3's north ledge, each running as the outline does, the
# cavity on its left. Every inward corner (a right turn) is rounded as
# the ledge's are, and each end meets the ledge's face square.
DESIGN_SHELF_FACE_MM = (
    (0.6, 61.346), (3.6, 61.346), (3.6, 3.6), (34.024, 3.6), (34.024, 8.363), (53.074, 8.363),
    (53.074, 10.744), (79.324, 10.744), (79.324, 8.363), (98.374, 8.363), (98.374, 5.981),
    (117.424, 5.981), (117.424, 3.6), (131.798, 3.6),
)
DESIGN_SHELF_NORTH_FACE_MM = (
    (104.468, 77.267), (104.468, 74.267), (91.174, 74.267), (91.174, 76.648), (72.124, 76.648),
    (72.124, 82.029),
)
DESIGN_SHELF_TOP_Z_MM = 6.0
DESIGN_SHELF_REACH_MM = 3.0  # in from the ledge's inner face
REACH_PROBE_PAST_NOTCH_MM = 0.5  # the reach is probed this far clear of a notch
DESIGN_SHELF_ROUND_MM = 2.13  # the ledge's inner face's, wherever the outline steps in
# Per half, the notches for the backing's screw heads, by kind: (count,
# deep, long).
DESIGN_SHELF_NOTCHES = {
    False: ((3, 0.102, 1.408), (1, 1.223, 4.298), (1, 1.954, 4.880)),
    True: ((1, 1.223, 4.298),),
}
# The parts' mounts (DESIGN.md, "Parts in the tray"), the left half's,
# placed on either half by half_point(). The nice!nano's mounts follow
# the board, so they are given from its edges, and the board from its
# fixed corner (the west edge and the USB end), its size DESIGN.md's
# unless a key=value word overrides it. The board lies on column 2, 0.3
# from the column 1/2 step's ledge face, the pocket's west face.
DESIGN_PRINT_SWELLING_PER_SIDE_MM = 0.2  # a 45 degree face: this times the square root of 2
DESIGN_NANO_WEST_X_MM = 38.524
DESIGN_NANO_USB_END_Y_MM = 80.078
DESIGN_NANO_SIZE_MM = (18.20, 33.20)  # along x, along y
DESIGN_NANO_SEAT_Z_MM = 1.2  # the board's underside, the seat's top
DESIGN_NANO_TOP_Z_MM = 2.8
DESIGN_NANO_FROM_STEP_LEDGE_FACE_MM = 0.3
DESIGN_SHELL_WIDTH_MM = 8.94
DESIGN_SHELL_TOP_Z_MM = 4.36
DESIGN_SHELL_PAST_BOARD_MM = 0.87  # the shell's mouth past the board's USB end
DESIGN_NORTH_EDGES_Y_MM = {"nice!nano": 80.248, "power switch": 75.486, "reset button": 82.629}
DESIGN_USB_WINDOW_MM = (10.5, 4.5)  # along x, along z
DESIGN_USB_WINDOW_CENTER_Z_MM = 2.78
DESIGN_USB_WINDOW_CORNER_RADIUS_MM = 1.95
DESIGN_USB_WINDOW_CHAMFER_MM = {"outer": 0.2, "inner": 0.0}
DESIGN_NANO_END_GAP_MM = 0.25  # the board's USB end to the north block
DESIGN_NANO_FOOT_GAP_MM = 0.11  # the board's south end to the clamp's foot
DESIGN_NANO_BAR_OPENING_MM = 9.44
DESIGN_NANO_BAR_CLEARANCE_MM = 0.1  # over the shell's top, as printed
DESIGN_NANO_BAR_HEIGHT_MM = 1.5
DESIGN_NANO_BAR_DEPTH_MM = 0.62  # to the shell's mouth
DESIGN_USB_CHANNEL_PAST_MOUTH_MM = 0.32  # its width the bar's opening, its top the bar's underside
DESIGN_NANO_NORTH_BLOCK_PAST_BOARD_MM = 0.5  # its ends past the board's edges, the cut-away's
# The pocket across: the board as a fit from the pocket's west face, its
# swelling and DESIGN_NANO_POCKET_FIT_MM's clearance. The walls beside
# it, their raised pieces up to the PCB's underside over the stretches
# given, along y.
DESIGN_NANO_POCKET_FIT_MM = 0.1
DESIGN_NANO_EAST_WALL_OUTER_X_MM = 59.124
DESIGN_NANO_WEST_WALL_OUTER_X_MM = 36.124
DESIGN_NANO_EAST_WALL_TOP_Z_MM = 5.2
DESIGN_NANO_WALLS_NORTH_Y_MM = {"west": 65.3, "east": 79.648}
DESIGN_NANO_RAISED_WALLS_Y_MM = {
    "west": ((49.710, 59.110),),
    "east": ((43.278, 47.003), (54.503, 66.053), (73.553, 79.648)),
}
DESIGN_NANO_RAISED_WALL_TOP_Z_MM = 9.5
# The seat under the board and the socket strips' pockets over its top
# (the user's request of 2026-10-20), given from the board's edges: the
# seat's edges inside its long edges, the pockets' faces in the west
# ledge and the east wall outside them, the pockets' ends from its USB
# end.
DESIGN_NANO_SEAT_INSIDE_EDGES_MM = 2.905
DESIGN_NANO_STRIP_POCKETS_OUTSIDE_EDGES_MM = 0.775
DESIGN_NANO_STRIP_POCKETS_FROM_USB_END_MM = (1.6565, 33.9335)  # north end, south end
# The screw clamp at the board's south end (work items 009 and 010), at
# the default press: the foot across the pocket, the block from the west
# wall's outer face to the east wall's, its bore on the board's center
# line.
DESIGN_CLAMP_FOOT_TOP_Z_MM = 2.8
DESIGN_CLAMP_SCREW_FROM_BOARD_MM = 6.5  # the bore's axis from the board's south end
DESIGN_CLAMP_BLOCK_ALONG_MM = 5.8
DESIGN_CLAMP_BLOCK_TOP_Z_MM = 4.8  # the board's top plus the nose's depth less the press
DESIGN_CLAMP_NOSE_DEPTH_MM = 2.1
DESIGN_CLAMP_BORE_MM = 3.2
DESIGN_CLAMP_INSERT_ROOM_PRINTED_MM = 4.6  # the bore's bottom counted 0.2 higher
# The pry slot through the clamp's block and foot and the recess under
# it and the board's south end (work item 010).
DESIGN_PRY_SLOT_FROM_LEDGE_FACE_MM = 1.0
DESIGN_PRY_SLOT_WIDTH_MM = 5.0
DESIGN_PRY_RECESS_UNDER_BOARD_MM = 2.0
DESIGN_PRY_RECESS_FLOOR_UNDER_MM = 1.2  # the whole floor, the seat left out over it
DESIGN_POWER_SWITCH_CENTER_X_MM = 9.049
DESIGN_KNOB_SLOT_MM = (7.5, 4.1)  # along x, along z, through the stop, the ledge and the wall
DESIGN_KNOB_SLOT_CENTER_Z_MM = 2.8
DESIGN_POWER_SWITCH_STOP_DEPTH_MM = 2.04  # from the ledge's face, the body's north face on it
DESIGN_POWER_SWITCH_STOP_ACROSS_MM = 13.8  # the cradle's span
DESIGN_POWER_SWITCH_STOP_TOP_Z_MM = 5.6  # the body's top
DESIGN_KNOB_LENGTH_MM = 5.0  # past the body's north face
DESIGN_KNOB_TROUGH_SHORT_OF_TIP_MM = 0.76
# The knob's tip past the outer face, as modelled and as printed (the
# stop's face swollen south, pushing the body, the outer face north).
DESIGN_KNOB_PEAKS_PROUD_MM = {False: 1.16, True: 0.76}
DESIGN_KNOB_TROUGH_PROUD_MM = {False: 0.4, True: 0.0}
DESIGN_CRADLE_OPENING_MM = 11.4
DESIGN_CRADLE_END_MM = 1.2
DESIGN_CRADLE_END_LENGTH_MM = 6.0  # from the stop's face
DESIGN_CRADLE_TOP_Z_MM = 3.0
DESIGN_RETAINER_GROOVE_MM = 1.65  # along y, from the end blocks' south ends
DESIGN_RETAINER_SOCKET_ACROSS_MM = 12.6  # between the grooves' walls
DESIGN_RETAINER_LIP_MM = 1.2  # along y
DESIGN_RESET_CENTER_X_MM = 66.199
DESIGN_RESET_PIN_HOLE_MM = 3.0
DESIGN_RESET_PIN_HOLE_AXIS_Z_MM = 3.095
DESIGN_RESET_PIN_HOLE_FLAT_MM = 1.24
DESIGN_RESET_BACK_WALL_DEPTH_MM = 4.9  # from the wall's inner face
DESIGN_RESET_BACK_WALL_MM = 1.2
DESIGN_RESET_BACK_WALL_TOP_Z_MM = 6.19
DESIGN_RESET_NOTCH_WIDTH_MM = 1.2
DESIGN_RESET_NOTCH_FROM_CENTER_MM = 2.5  # each notch's middle
DESIGN_RESET_NOTCH_BOTTOM_Z_MM = 2.645
DESIGN_RESET_BACK_WALL_BEYOND_NOTCHES_MM = 1.0
DESIGN_RESET_SIDE_WALLS_APART_MM = 6.59
DESIGN_RESET_SIDE_WALL_MM = 1.2
DESIGN_RESET_FRONT_STOP_MM = 2.0  # along x
DESIGN_RESET_FRONT_STOP_DEPTH_MM = 0.9  # from the wall's inner face
DESIGN_RESET_FRONT_STOP_TOP_Z_MM = 0.945
DESIGN_PCB_CONNECTOR_ZONE_MM = ((20.0, 37.0), (65.5, 74.5))

# The walls are measured at these points of DESIGN.md's outline, (where,
# point on an outline edge, outward unit vector), at WALL_PROBE_Z_MM,
# above the ledge and clear of every cut. The slant's is its middle,
# between two magnet slots. The ledge is measured at the west one.
WALL_PROBE_Z_MM = 10.0
# Under the ledge's top, over the shelves' and under the tab notches'
# bottoms (z 6.5).
LEDGE_PROBE_Z_MM = 6.25
FLOOR_PROBE_MM = (60.0, 40.0)  # open floor, clear of every standoff and boss
SLANT_PROBE_ALONG_MM = 31.25

# How far a measuring line reaches either side of its point.
PROBE_REACH_MM = 30.0
# The plastic over a horizontal hole is sampled this far apart along it.
HOLE_SAMPLE_STEP_MM = 0.25
# Two places count as the same within this.
SAME_PLACE_MM = 1e-6
# The joined trays overlap or part by less than this.
JOINED_TOLERANCE_MM = 1e-6
JOINED_OVERLAP_TOLERANCE_MM3 = 1e-3

USAGE = f"""\
usage: freecadcmd model/kbdkid5/scripts/export_tray.py --pass <tray.stl> [right]
           [pin_hole_diameter=<mm>] [nano_length=<mm>] [nano_width=<mm>]
           [nano_pocket_fit=<mm>] [clamp_press=<mm>] [bar_clearance=<mm>]

  right              export the right half: cut for its own sockets, its pin
                     holes the slip fit, mirrored across the layout's right-half
                     mirror line, x = {layout.RIGHT_HALF_MIRROR_X_MM:.3f}
  pin_hole_diameter  the dowel pin holes' diameter as modelled, mm, instead of
                     the half's fit ({layout.DOWEL_HOLE_SNUG_DIAMETER_MM:.1f} snug on the left, \
{layout.DOWEL_HOLE_SLIP_DIAMETER_MM:.1f} slip
                     on the right, both less {layout.PRINT_SWELLING_PER_SIDE_MM} per side once \
printed)
  nano_length        the nice!nano's board length the mounts are fitted to
                     (default {layout.NANO_LENGTH_MM}), its USB end staying put
  nano_width         its width (default {layout.NANO_WIDTH_MM}), its west edge staying put
  nano_pocket_fit    the pocket's clearance across the board as printed, the
                     east wall's inner face moving with it (default
                     {layout.NANO_POCKET_FIT_MM}, the slip fit)
  clamp_press        how far the clamp's tab presses the board as printed, its
                     block's top that much under the tab's seat on the board
                     (default {layout.NANO_CLAMP_PRESS_MM})
  bar_clearance      the north block's bar's clearance over the USB-C shell as
                     printed (default {layout.NANO_BAR_CLEARANCE_MM})\
"""

# The key=value words, each a number: the pin holes' diameter and the
# mounts' fits (layout.MountFits' fields).
OPTION_KEYS = (
    "pin_hole_diameter",
    "nano_length",
    "nano_width",
    "nano_pocket_fit",
    "clamp_press",
    "bar_clearance",
)


class Arguments:
    def __init__(self):
        self.stl_file = None
        self.right = False
        for key in OPTION_KEYS:
            setattr(self, key, None)

    def mount_fits(self):
        """layout.MountFits with the overrides given."""
        given = {
            key: getattr(self, key) for key in OPTION_KEYS[1:] if getattr(self, key) is not None
        }
        return layout.MountFits(**given)


def parse_arguments(argument_list):
    arguments = Arguments()
    positionals = []
    for argument in argument_list:
        if argument == "right":
            arguments.right = True
        elif "=" in argument:
            key, _, value = argument.partition("=")
            if key not in OPTION_KEYS:
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


# DESIGN.md's geometry on either half.


def half_point(point, right):
    """A left-half DESIGN.md point on the given half."""
    return (2.0 * DESIGN_MIRROR_LINE_X_MM - point[0], point[1]) if right else point


def half_vector(vector, right):
    return (-vector[0], vector[1]) if right else vector


def design_slant_frame(right):
    """(south end, unit direction north, unit outward normal) of
    DESIGN.md's slant on the given half."""
    (south_x, south_y), (north_x, north_y) = DESIGN_SLANT_ENDS_MM
    length = math.hypot(north_x - south_x, north_y - south_y)
    direction = ((north_x - south_x) / length, (north_y - south_y) / length)
    outward = (direction[1], -direction[0])  # the outline runs counter-clockwise
    south = half_point((south_x, south_y), right)
    return south, half_vector(direction, right), half_vector(outward, right)


def slant_place(right, along, outward, z):
    """The point along and outward of DESIGN.md's slant on the given
    half, at height z."""
    south, direction, normal = design_slant_frame(right)
    return App.Vector(
        south[0] + along * direction[0] + outward * normal[0],
        south[1] + along * direction[1] + outward * normal[1],
        z,
    )


def vector(plan, z=0.0):
    return App.Vector(plan[0], plan[1], z)


def wall_probes(right):
    """(where, point on DESIGN.md's outline, outward unit vector), named
    on the given half."""
    probes = [
        (("west", "east"), (0.0, 34.0), (-1.0, 0.0)),
        (("south", "south"), (18.8, 0.0), (0.0, -1.0)),
        (("north of column 4", "north of column 4"), (85.249, 80.248), (0.0, 1.0)),
        (("thumb's east", "thumb's west"), (DESIGN_THUMB_EAST_EDGE_X_MM, 10.0), (1.0, 0.0)),
    ]
    probes = [
        (names[right], half_point(point, right), half_vector(outward, right))
        for names, point, outward in probes
    ]
    _south, _direction, normal = design_slant_frame(right)
    middle = slant_place(right, SLANT_PROBE_ALONG_MM, 0.0, 0.0)
    probes.append(("slant", (middle.x, middle.y), normal))
    return probes


# Measuring along lines.


def material_intervals(shape, start, direction, length):
    """The sorted (low, high) stretches, as distances from start along
    the unit direction, where the segment lies inside the shape."""
    edge = Part.LineSegment(start, start.add(direction * length)).toShape()
    intervals = []
    for piece in shape.common(edge).Edges:
        ends = [vertex.Point.sub(start).dot(direction) for vertex in piece.Vertexes]
        intervals.append((min(ends), max(ends)))
    intervals.sort()
    merged = []
    for low, high in intervals:
        if merged and low <= merged[-1][1] + SAME_PLACE_MM:
            merged[-1] = (merged[-1][0], max(merged[-1][1], high))
        else:
            merged.append((low, high))
    return merged


def run_through(shape, point, direction, material):
    """(low, high) of the material (or, with material False, the empty)
    stretch through point along the unit direction, as signed distances
    from point. An open end reads as PROBE_REACH_MM."""
    start = point.sub(direction * PROBE_REACH_MM)
    intervals = [
        (low - PROBE_REACH_MM, high - PROBE_REACH_MM)
        for low, high in material_intervals(shape, start, direction, 2.0 * PROBE_REACH_MM)
    ]
    if material:
        for low, high in intervals:
            if low <= 0.0 <= high:
                return low, high
        raise SystemExit(f"error: no plastic at {format_vector(point)} to measure")
    low, high = -PROBE_REACH_MM, PROBE_REACH_MM
    for interval_low, interval_high in intervals:
        if interval_low <= 0.0 <= interval_high:
            raise SystemExit(f"error: plastic at {format_vector(point)}, where a gap was measured")
        if interval_high < 0.0:
            low = max(low, interval_high)
        if interval_low > 0.0:
            high = min(high, interval_low)
    return low, high


def format_vector(point):
    return f"({point.x:.3f}, {point.y:.3f}, {point.z:.3f})"


class Figures:
    """Measured figures against DESIGN.md's, each within half its last
    digit. A figure off DESIGN.md stops the export."""

    def __init__(self):
        self.problems = []

    def check(self, label, measured, stated, decimals):
        tolerance = 0.5 * 10.0**-decimals + 1e-6
        shown = round(measured, decimals + 2) + 0.0  # no "-0.00"
        text = f"{label} {shown:.{decimals + 2}f} (DESIGN.md {stated})"
        if abs(measured - stated) > tolerance:
            self.problems.append(text)
        return text

    def at_least(self, label, measured, minimum, decimals):
        shown = round(measured, decimals + 2) + 0.0
        text = f"{label} {shown:.{decimals + 2}f} (DESIGN.md at least {minimum})"
        if measured < minimum - 1e-6:
            self.problems.append(text)
        return text

    def report(self, label, measured, decimals):
        """A figure DESIGN.md does not give (a test print's)."""
        return f"{label} {measured:.{decimals + 2}f}"

    def stop_on_problems(self):
        if self.problems:
            raise SystemExit("error: off DESIGN.md's figures:\n  " + "\n  ".join(self.problems))


# The measurements.


def measure_outside(tray, figures):
    box = tray.BoundBox
    texts = [
        figures.check(f"{what} outside", length, stated, 1)
        for what, length, stated in zip(
            ("x", "y", "z"), (box.XLength, box.YLength, box.ZLength), DESIGN_TRAY_OUTSIDE_MM
        )
    ]
    texts.append(figures.check("floor underside z", box.ZMin, DESIGN_FLOOR_UNDERSIDE_Z_MM, 1))
    texts.append(figures.check("rim z", box.ZMax, DESIGN_RIM_Z_MM, 1))
    return f"outside:    {', '.join(texts)} (x {box.XMin:.3f} to {box.XMax:.3f})"


def wall_middle(point, outward, z):
    """The point halfway through DESIGN.md's wall out of an outline
    point."""
    return vector(point, z).add(vector(outward) * (DESIGN_GAP_MM + DESIGN_WALL_MM / 2.0))


def measure_walls(tray, right, figures):
    lines = []
    for where, point, outward in wall_probes(right):
        middle = wall_middle(point, outward, WALL_PROBE_Z_MM)
        low, high = run_through(tray, middle, vector(outward), True)
        inner = DESIGN_GAP_MM + DESIGN_WALL_MM / 2.0 + low
        texts = [
            figures.check("inner face out of the outline", inner, DESIGN_GAP_MM, 1),
            figures.check("thick", high - low, DESIGN_WALL_MM, 1),
        ]
        lines.append(f"wall:       {where}: {', '.join(texts)}")
    return lines


def measure_floor(tray, right, figures):
    plan = half_point(FLOOR_PROBE_MM, right)
    point = vector(plan, DESIGN_FLOOR_UNDERSIDE_Z_MM / 2.0)
    low, high = run_through(tray, point, UP, True)
    bottom, top = point.z + low, point.z + high
    texts = [
        figures.check("thick", top - bottom, DESIGN_FLOOR_MM, 1),
        figures.check("top z", top, 0.0, 1),
    ]
    return f"floor:      at ({plan[0]:.3f}, {plan[1]:.3f}): {', '.join(texts)}"


def measure_ledge(tray, right, figures):
    where, point, outward = wall_probes(right)[0]
    direction = vector(outward)
    low, high = run_through(tray, wall_middle(point, outward, LEDGE_PROBE_Z_MM), direction, True)
    reach = -(DESIGN_GAP_MM + DESIGN_WALL_MM / 2.0 + low)
    in_ledge = vector(point, 0.0).sub(direction * (DESIGN_LEDGE_UNDER_PCB_MM / 2.0))
    _bottom, top = run_through(tray, in_ledge, UP, True)
    texts = [
        figures.check("under the PCB", reach, DESIGN_LEDGE_UNDER_PCB_MM, 1),
        figures.check("wide", reach + DESIGN_GAP_MM, DESIGN_LEDGE_WIDTH_MM, 1),
        figures.check("top z", top, DESIGN_LEDGE_TOP_Z_MM, 1),
    ]
    return f"ledge:      {where}: {', '.join(texts)}"


def shelf_segments():
    """(start, length, unit direction, unit normal toward the cavity,
    (inward at its start, at its end)) of each straight run of DESIGN.md's
    shelf face, both runs of it, in the left half's frame. The face runs
    as the outline does, so the cavity lies on its left, and a corner
    where it turns right is an inward one, rounded. Its ends meet the
    ledge's face."""
    segments = []
    for points in (DESIGN_SHELF_FACE_MM, DESIGN_SHELF_NORTH_FACE_MM):
        inward = [False]
        for before, corner, after in zip(points, points[1:], points[2:]):
            cross = ((corner[0] - before[0]) * (after[1] - corner[1])
                     - (corner[1] - before[1]) * (after[0] - corner[0]))
            inward.append(cross < 0.0)
        inward.append(False)
        for index, (start, end) in enumerate(zip(points, points[1:])):
            length = math.dist(start, end)
            direction = ((end[0] - start[0]) / length, (end[1] - start[1]) / length)
            normal = (-direction[1], direction[0])
            segments.append((start, length, direction, normal,
                             (inward[index], inward[index + 1])))
    return segments


def planar_faces_facing(tray, right, normal):
    """(vertices in the left half's frame, z range) of the tray's planar
    faces on the given half whose outward normal is the left half's
    normal there."""
    wanted = half_vector(normal, right)
    found = []
    for face in tray.Faces:
        if not isinstance(face.Surface, Part.Plane):
            continue
        face_normal = face.normalAt(*face.Surface.parameter(face.CenterOfMass))
        if face_normal.x * wanted[0] + face_normal.y * wanted[1] < 1.0 - 1e-9:
            continue
        points = [half_point((vertex.Point.x, vertex.Point.y), right) for vertex in face.Vertexes]
        found.append((points, (face.BoundBox.ZMin, face.BoundBox.ZMax)))
    return found


def faces_along(faces, start, length, direction, normal, offset):
    """((low, high) along the run, z range) of the faces lying offset
    along the normal from a straight run, within its length."""
    found = []
    for points, z_range in faces:
        alongs = [(x - start[0]) * direction[0] + (y - start[1]) * direction[1] for x, y in points]
        offsets = [(x - start[0]) * normal[0] + (y - start[1]) * normal[1] for x, y in points]
        if (max(abs(each - offset) for each in offsets) < 1e-4
                and min(alongs) > -1e-4 and max(alongs) < length + 1e-4):
            found.append(((min(alongs), max(alongs)), z_range))
    return found


def notch_bottoms(faces, start, length, direction, normal):
    """(how deep, (low, high) along the run) of the faces facing the
    cavity behind a straight run of the shelves' face, short of the
    ledge's face: the notches' bottoms."""
    found = []
    for points, _z_range in faces:
        alongs = [(x - start[0]) * direction[0] + (y - start[1]) * direction[1] for x, y in points]
        offsets = [(x - start[0]) * normal[0] + (y - start[1]) * normal[1] for x, y in points]
        depth = -offsets[0]
        if (max(offsets) - min(offsets) < 1e-4 and 1e-3 < depth < DESIGN_SHELF_REACH_MM - 1e-2
                and min(alongs) > -1e-4 and max(alongs) < length + 1e-4):
            found.append((depth, (min(alongs), max(alongs))))
    return found


def reach_probe_along(length, notches):
    """Where along a run its reach is probed: the middle, or, where a
    notch for a screw head takes the middle, the nearer of the notch's
    ends moved REACH_PROBE_PAST_NOTCH_MM out of it."""
    along = length / 2.0
    for _depth, (low, high) in notches:
        if low - REACH_PROBE_PAST_NOTCH_MM < along < high + REACH_PROBE_PAST_NOTCH_MM:
            along = (low - REACH_PROBE_PAST_NOTCH_MM if along - low < high - along
                     else high + REACH_PROBE_PAST_NOTCH_MM)
    return along


def shelf_reach(tray, right, start, along, direction, normal):
    """How far the shelf reaches in from the ledge's face at along on a
    straight run: from 0.5 behind its face, the plastic's end toward the
    cavity at half the shelf's height and the open stretch's back to the
    ledge's face just over its top."""
    middle = (start[0] + direction[0] * along - normal[0] * 0.5,
              start[1] + direction[1] * along - normal[1] * 0.5)
    toward_cavity = vector(half_vector(normal, right))
    _low, face = run_through(tray, vector(half_point(middle, right), DESIGN_SHELF_TOP_Z_MM / 2.0),
                             toward_cavity, True)
    ledge, _high = run_through(tray, vector(half_point(middle, right), LEDGE_PROBE_Z_MM),
                               toward_cavity, False)
    return face - ledge


def measure_shelves(tray, right, figures):
    """Each straight run of the shelves' face: its plane DESIGN.md's, its
    straight length (DESIGN.md's less the round at an inward end, or
    less the notch that runs into that round), its z range (from the
    floor's top to the shelves' top), on the long runs their reach in
    from the ledge's face, and the notches behind it for the backing's
    screw heads, of each kind as many as DESIGN.md has."""
    lines = []
    notches = []
    for start, length, direction, normal, inward_ends in shelf_segments():
        faces = planar_faces_facing(tray, right, normal)
        pieces = faces_along(faces, start, length, direction, normal, 0.0)
        if not pieces:
            raise SystemExit(f"error: no shelf face on the run from {start} along {direction}")
        low = min(along[0] for along, _z in pieces)
        high = max(along[1] for along, _z in pieces)
        run_notches = notch_bottoms(faces, start, length, direction, normal)
        straight_low = DESIGN_SHELF_ROUND_MM if inward_ends[0] else 0.0
        straight_high = length - (DESIGN_SHELF_ROUND_MM if inward_ends[1] else 0.0)
        for _depth, (notch_low, notch_high) in run_notches:
            if notch_low < straight_low < notch_high:
                straight_low = notch_high
            if notch_low < straight_high < notch_high:
                straight_high = notch_low
        straight = straight_high - straight_low
        where = half_point(start, right)
        texts = [
            figures.check("straight", high - low, round(straight, 3), 2),
            figures.check("from z", min(z[0] for _along, z in pieces), 0.0, 2),
            figures.check("to", max(z[1] for _along, z in pieces), DESIGN_SHELF_TOP_Z_MM, 2),
            f"in {len(pieces)} {'piece' if len(pieces) == 1 else 'pieces'}",
        ]
        if straight > 2.0 * DESIGN_SHELF_ROUND_MM:
            reach = shelf_reach(tray, right, start, reach_probe_along(length, run_notches),
                                direction, normal)
            texts.append(figures.check("reach", reach, DESIGN_SHELF_REACH_MM, 2))
        notches.extend(run_notches)
        lines.append(f"shelf:      from ({where[0]:.3f}, {where[1]:.3f}), {length:.3f} long as "
                     f"modelled: {', '.join(texts)}")
    kinds = DESIGN_SHELF_NOTCHES[right]
    texts = [figures.check("notches", len(notches), sum(count for count, _deep, _long in kinds), 0)]
    for count, depth, notch_length in kinds:
        alike = [along for each, along in notches
                 if abs(each - depth) < 5e-4 and abs(along[1] - along[0] - notch_length) < 5e-4]
        texts.append(figures.check(f"{depth} deep and {notch_length} long", len(alike), count, 0))
    lines.append(f"shelf:      for the backing's screw heads, {', '.join(texts)}")
    return lines


def measure_block(tray, right, figures):
    _south, _direction, normal = design_slant_frame(right)
    point = slant_place(right, SLANT_PROBE_ALONG_MM, 0.0, LEDGE_PROBE_Z_MM)
    low, high = run_through(tray, point, vector(normal), True)
    in_block = slant_place(right, SLANT_PROBE_ALONG_MM, -1.6, 0.0)
    _bottom, top = run_through(tray, in_block, UP, True)
    texts = [
        figures.check("thick", high - low, DESIGN_JOINT_BLOCK_THICKNESS_MM, 1),
        figures.check("outer face out of the slant", high, DESIGN_JOINT_FACE_OUT_OF_SLANT_MM, 1),
        figures.check("top z", top, DESIGN_LEDGE_TOP_Z_MM, 1),
    ]
    return f"block:      at {SLANT_PROBE_ALONG_MM} along the slant: {', '.join(texts)}"


def vertical_cylinders(tray, radius):
    """{rounded (x, y): (x, y, z low, z high)} of the vertical
    cylindrical faces of the given radius, merged per axis."""
    found = {}
    for face in tray.Faces:
        surface = face.Surface
        if not isinstance(surface, Part.Cylinder) or abs(surface.Radius - radius) > 1e-6:
            continue
        if abs(abs(surface.Axis.z) - 1.0) > 1e-9:
            continue
        key = (round(surface.Center.x, 3), round(surface.Center.y, 3))
        box = face.BoundBox
        low, high = box.ZMin, box.ZMax
        if key in found:
            low, high = min(low, found[key][2]), max(high, found[key][3])
        found[key] = (surface.Center.x, surface.Center.y, low, high)
    return found


def nearest_found(found, target, what):
    """The one found (x, y, ...) entry within 0.01 of target."""
    near = [entry for entry in found.values() if math.dist(entry[:2], target) < 0.01]
    if len(near) != 1:
        raise SystemExit(f"error: found {len(near)} {what}s at {target}, expected one")
    return near[0]


def design_slant_coordinates(point):
    """(along, outward) of a left-half point in DESIGN.md's slant frame."""
    south, direction, normal = design_slant_frame(False)
    offset = (point[0] - south[0], point[1] - south[1])
    return (offset[0] * direction[0] + offset[1] * direction[1],
            offset[0] * normal[0] + offset[1] * normal[1])


def merged_bore_walls(tray, right):
    """The plastic between each bore of a standoff that reaches the joint
    block and the slot cut through it, along the slant's normal from the
    bore's face."""
    block_inner_face = DESIGN_JOINT_FACE_OUT_OF_SLANT_MM - DESIGN_JOINT_BLOCK_THICKNESS_MM
    _south, _direction, normal = design_slant_frame(right)
    walls = []
    for drill in DESIGN_MOUNTING_DRILLS_MM:
        along, outward = design_slant_coordinates(drill)
        if outward + DESIGN_STANDOFF_DIAMETER_MM / 2.0 <= block_inner_face:
            continue
        point = slant_place(right, along, outward + DESIGN_STANDOFF_BORE_MM / 2.0 + 0.05,
                            LEDGE_PROBE_Z_MM)
        low, high = run_through(tray, point, vector(normal), True)
        walls.append(high - low)
    return walls


def merged_axes_from_block(tray, right):
    """How far the joint block's inner face stands from the axis of each
    standoff that reaches the block, over the standoff's top, along the
    slant's normal: open there, the standoff ending at the frame's tubes'
    mouth and the block standing whole to its top. The face is planar,
    so it is probed just south of a magnet slot the axis lies across,
    which opens toward the cavity over the standoff's top."""
    block_inner_face = DESIGN_JOINT_FACE_OUT_OF_SLANT_MM - DESIGN_JOINT_BLOCK_THICKNESS_MM
    _south, _direction, normal = design_slant_frame(right)
    over_top = (DESIGN_STANDOFF_TOP_Z_MM + DESIGN_LEDGE_TOP_Z_MM) / 2.0
    distances = []
    for drill in DESIGN_MOUNTING_DRILLS_MM:
        along, outward = design_slant_coordinates(drill)
        if outward + DESIGN_STANDOFF_DIAMETER_MM / 2.0 <= block_inner_face:
            continue
        probe_along = along
        for slot_along in DESIGN_MAGNET_ALONGS_MM:
            slot_south = slot_along - DESIGN_MAGNET_SLOT_MM[0] / 2.0
            if slot_south <= along <= slot_along + DESIGN_MAGNET_SLOT_MM[0] / 2.0:
                probe_along = slot_south - MERGED_AXIS_PROBE_PAST_SLOT_MM
        _low, high = run_through(tray, slant_place(right, probe_along, outward, over_top),
                                 vector(normal), False)
        distances.append(high)
    return distances


def measure_standoffs(tray, right, figures):
    """The standoffs and their bores, their tops, and the plastic a
    merged one's bore keeps toward the joint's slot and how far the
    block's inner face stands from its axis over its top. The nice!nano
    clamp's insert bore is the only other bore that size, measured with
    the clamp."""
    bores = vertical_cylinders(tray, DESIGN_STANDOFF_BORE_MM / 2.0)
    posts = vertical_cylinders(tray, DESIGN_STANDOFF_DIAMETER_MM / 2.0)
    drills = [half_point(drill, right) for drill in DESIGN_MOUNTING_DRILLS_MM]
    if len(bores) != len(drills) + 1 or len(posts) != len(drills):
        raise SystemExit(
            f"error: {len(bores)} bores and {len(posts)} standoffs for {len(drills)} drills and "
            "the clamp's bore"
        )
    worst = 0.0
    bore_lows, bore_highs, post_highs, floors = [], [], [], []
    for drill in drills:
        bore = nearest_found(bores, drill, "bore")
        post = nearest_found(posts, drill, "standoff")
        worst = max(worst, math.dist(bore[:2], drill), math.dist(post[:2], drill))
        bore_lows.append(bore[2])
        bore_highs.append(bore[3])
        post_highs.append(post[3])
        low, high = run_through(tray, App.Vector(drill[0], drill[1], -0.6), UP, True)
        floors.append(high - low)
    texts = [
        f"{len(drills)} on DESIGN.md's drills within {worst:.6f}",
        figures.check("bore bottoms z", max(bore_lows, key=abs), 0.0, 1),
        figures.check("tops z", min(post_highs), DESIGN_STANDOFF_TOP_Z_MM, 1),
        figures.check("to", max(post_highs), DESIGN_STANDOFF_TOP_Z_MM, 1),
        figures.check("plastic under the inserts", min(floors), DESIGN_FLOOR_MM, 1),
        f"{DESIGN_STANDOFF_DIAMETER_MM} across, {DESIGN_STANDOFF_BORE_MM} bores (by radius)",
    ]
    walls = merged_bore_walls(tray, right)
    if len(walls) != 1:
        figures.problems.append(f"{len(walls)} standoffs reach the joint block, DESIGN.md has one")
    else:
        texts.append(figures.check("the merged one's bore from the magnet slot", walls[0],
                                   DESIGN_MERGED_STANDOFF_BORE_WALL_MM, 2))
    axes = merged_axes_from_block(tray, right)
    if len(axes) == 1:
        texts.append(figures.check("the block's inner face from its axis over its top", axes[0],
                                   DESIGN_MERGED_STANDOFF_AXIS_FROM_BLOCK_MM, 3))
    return f"standoffs:  {', '.join(texts)}"


def joint_face(tray, right):
    """The planar face of the tray whose outward normal is the slant's,
    farthest out: (face, its distance out of DESIGN.md's slant)."""
    south, _direction, normal = design_slant_frame(right)
    candidates = []
    for face in tray.Faces:
        if not isinstance(face.Surface, Part.Plane):
            continue
        face_normal = face.normalAt(*face.Surface.parameter(face.CenterOfMass))
        if face_normal.x * normal[0] + face_normal.y * normal[1] < 1.0 - 1e-9:
            continue
        point = face.Vertexes[0].Point
        offset = (point.x - south[0]) * normal[0] + (point.y - south[1]) * normal[1]
        candidates.append((offset, face))
    if not candidates:
        raise SystemExit("error: the tray has no face along the slant")
    offset, face = max(candidates, key=lambda candidate: candidate[0])
    return face, offset


def measure_joint_face(tray, right, figures):
    face, offset = joint_face(tray, right)
    face_normal = face.normalAt(*face.Surface.parameter(face.CenterOfMass))
    angle = math.degrees(math.atan2(abs(face_normal.y), abs(face_normal.x)))
    south, direction, _normal = design_slant_frame(right)
    alongs = [
        (vertex.Point.x - south[0]) * direction[0] + (vertex.Point.y - south[1]) * direction[1]
        for vertex in face.Vertexes
    ]
    box = face.BoundBox
    holes = len(face.Wires) - 1
    texts = [
        figures.check("out of the slant", offset, DESIGN_JOINT_FACE_OUT_OF_SLANT_MM, 1),
        figures.check("degrees from north", angle, DESIGN_SLANT_ANGLE_FROM_NORTH_DEGREES, 2),
        f"flat from {min(alongs):.4f} to {max(alongs):.4f} along the slant, z {box.ZMin:.3f} to "
        f"{box.ZMax:.3f}, {holes} openings",
    ]
    if holes != len(DESIGN_DOWEL_PIN_ALONGS_MM):
        raise SystemExit(f"error: the joint face has {holes} openings, expected the pin holes")
    lowest_boss = min(DESIGN_DOWEL_PIN_ALONGS_MM) - DESIGN_DOWEL_BOSS_ACROSS_MM / 2.0
    highest_boss = max(DESIGN_DOWEL_PIN_ALONGS_MM) + DESIGN_DOWEL_BOSS_ACROSS_MM / 2.0
    if lowest_boss < min(alongs) or highest_boss > max(alongs):
        raise SystemExit(
            f"error: the bosses span {lowest_boss} to {highest_boss} along the slant, past the "
            "joint face's flat part"
        )
    return f"joint face: {', '.join(texts)}, the bosses' {lowest_boss} to {highest_boss} on it"


def horizontal_cylinders(tray, radius, axis):
    """Axis points of the cylindrical faces of the given radius whose
    axis lies along the horizontal unit axis, one per axis line."""
    found = []
    for face in tray.Faces:
        surface = face.Surface
        if not isinstance(surface, Part.Cylinder) or abs(surface.Radius - radius) > 1e-6:
            continue
        if abs(abs(surface.Axis.dot(axis)) - 1.0) > 1e-9:
            continue
        center = surface.Center
        side = App.Vector(-axis.y, axis.x, 0.0)  # square to the axis, so it tells axes apart
        key = (center.dot(side), center.z)
        if all(math.dist(key, other) > 1e-3 for other, _center in found):
            found.append((key, center))
    return [center for _key, center in found]


def sample_depths(start, end):
    """Depths from start to end, HOLE_SAMPLE_STEP_MM apart."""
    count = int((end - start) / HOLE_SAMPLE_STEP_MM)
    return [start + index * HOLE_SAMPLE_STEP_MM for index in range(count + 1)]


def least_plastic_over(tray, mouth, axis, depths):
    """(the least plastic over a horizontal hole, the depth from its
    mouth along the unit axis where it lies) over the given depths."""
    least = (math.inf, None)
    for depth in depths:
        point = mouth.add(axis * depth)
        _down, up = run_through(tray, point, UP, False)
        _low, high = run_through(tray, point.add(UP * (up + 0.01)), UP, True)
        least = min(least, (high + 0.01, depth))
    return least


def flat_top(tray, point, side):
    """(how far a flat-topped teardrop's top lies above the point on its
    axis, the flat's width, measured along side just under it)."""
    _down, up = run_through(tray, point, UP, False)
    low, high = run_through(tray, point.add(UP * (up - 0.001)), side, False)
    return up, high - low - 0.002


def hole_design(right, pin_hole_diameter):
    """(diameter, flat width, plastic over) DESIGN.md gives the half's
    dowel holes, or for a test print's pin_hole_diameter that diameter
    and no other figures."""
    if pin_hole_diameter is None:
        return (
            DESIGN_DOWEL_HOLE_DIAMETER_MM[right],
            DESIGN_DOWEL_HOLE_FLAT_MM[right],
            DESIGN_PLASTIC_OVER_DOWEL_HOLES_MM[right],
        )
    return (pin_hole_diameter, None, None)


def check_or_report(figures, label, measured, stated, decimals):
    if stated is None:
        return figures.report(label, measured, decimals)
    return figures.check(label, measured, stated, decimals)


def measure_pin_hole(tray, right, along, radius, design, figures):
    """The figures of the dowel hole found at `along`: its depth and
    diameter, the boss behind it, its flat top, the plastic over it and
    its mouth's lead-in."""
    _south, direction, normal = design_slant_frame(right)
    outward = vector(normal)
    face = DESIGN_JOINT_FACE_OUT_OF_SLANT_MM
    z = DESIGN_DOWEL_PIN_Z_MM
    diameter, flat_stated, over_stated = design
    bottom_low, _ = run_through(tray, slant_place(right, along, face - 1.0, z), outward, False)
    bottom = face - 1.0 + bottom_low
    back_low, _ = run_through(tray, slant_place(right, along, bottom - 0.1, z), outward, True)
    boss_end = bottom - 0.1 + back_low
    inside = slant_place(right, along, (face + bottom) / 2.0, z)
    across_low, across_high = run_through(tray, inside, vector(direction), False)
    top, flat = flat_top(tray, inside, vector(direction))
    mouth = slant_place(right, along, face, z)
    depths = sample_depths(0.1, face - bottom - 0.1)
    over, where = least_plastic_over(tray, mouth, outward * -1.0, depths)
    at_face = slant_place(right, along, face - 0.05, z)
    face_low, face_high = run_through(tray, at_face, vector(direction), False)
    widening = (face_high - face_low) / 2.0 - radius
    lead_in = widening + 0.05 if widening > 1e-6 else 0.0
    over_text = check_or_report(figures, "least plastic over it", over, over_stated, 2)
    return [
        figures.check("deep", face - bottom, DESIGN_DOWEL_HOLE_DEPTH_MM[right], 1),
        check_or_report(figures, "across", across_high - across_low, diameter, 1),
        figures.check(
            "plastic behind", bottom - boss_end, DESIGN_DOWEL_BOSS_BEHIND_HOLE_MM[right], 1
        ),
        figures.check("boss reach", face - boss_end, DESIGN_DOWEL_BOSS_REACH_MM[right], 1),
        f"top {top:.3f} above the axis ({top / radius:.4f} radii)",
        check_or_report(figures, "flat top", flat, flat_stated, 2),
        f"{over_text} (at {where:.2f} in)",
        figures.check("lead-in", lead_in, DESIGN_DOWEL_HOLE_LEAD_IN_MM[right], 1),
    ]


def measure_pin_holes(tray, right, radius, design, figures):
    south, direction, normal = design_slant_frame(right)
    centers = horizontal_cylinders(tray, radius, vector(normal))
    if len(centers) != len(DESIGN_DOWEL_PIN_ALONGS_MM):
        raise SystemExit(f"error: found {len(centers)} pin holes of radius {radius}, expected two")
    alongs = sorted(
        (center.x - south[0]) * direction[0] + (center.y - south[1]) * direction[1]
        for center in centers
    )
    heights = [center.z for center in centers]
    lines = []
    for along, stated in zip(alongs, DESIGN_DOWEL_PIN_ALONGS_MM):
        texts = [figures.check("at", along, stated, 1)]
        texts.extend(measure_pin_hole(tray, right, along, radius, design, figures))
        lines.append(f"pin hole:   {', '.join(texts)}")
    texts = [
        figures.check("pin holes apart", alongs[1] - alongs[0], DESIGN_DOWEL_PIN_SPACING_MM, 1),
        figures.check(
            "axes z",
            max(heights, key=lambda height: abs(height - DESIGN_DOWEL_PIN_Z_MM)),
            DESIGN_DOWEL_PIN_Z_MM,
            2,
        ),
        "axes square to the joint face (by their direction)",
    ]
    lines.append(f"pin holes:  {', '.join(texts)}")
    return lines


def measure_magnet_slots(tray, right, figures):
    _south, direction, normal = design_slant_frame(right)
    face = DESIGN_JOINT_FACE_OUT_OF_SLANT_MM
    slot_middle = face - DESIGN_MAGNET_SKIN_MM - DESIGN_MAGNET_SLOT_MM[1] / 2.0
    block_inner_face = face - DESIGN_JOINT_BLOCK_THICKNESS_MM
    in_floor_z = DESIGN_MAGNET_SLOT_BOTTOM_Z_MM / 2.0
    lines = []
    for stated in DESIGN_MAGNET_ALONGS_MM:
        point = slant_place(right, stated, slot_middle, LEDGE_PROBE_Z_MM)
        along_low, along_high = run_through(tray, point, vector(direction), False)
        inward_low, face_high = run_through(tray, point, vector(normal), False)
        if slot_middle + inward_low > block_inner_face - 1.0:
            raise SystemExit(f"error: the magnet slot at {stated} is not open toward the cavity")
        recess = slant_place(right, stated, slot_middle, in_floor_z)
        across_low, across_high = run_through(tray, recess, vector(normal), False)
        bottom, _top = run_through(tray, point, UP, False)
        cutback = slant_place(right, stated, face - 0.05, WALL_PROBE_Z_MM)
        wall_low, wall_high = run_through(tray, cutback, vector(normal), True)
        texts = [
            figures.check("at", stated + (along_low + along_high) / 2.0, stated, 2),
            figures.check("long", along_high - along_low, DESIGN_MAGNET_SLOT_MM[0], 1),
            figures.check(
                "across in the floor", across_high - across_low, DESIGN_MAGNET_SLOT_MM[1], 1
            ),
            figures.check("skin", face - (slot_middle + face_high), DESIGN_MAGNET_SKIN_MM, 1),
            figures.check("bottom z", point.z + bottom, DESIGN_MAGNET_SLOT_BOTTOM_Z_MM, 1),
            "open toward the cavity from the block's inner face",
            figures.check(
                "wall left above the block", wall_high - wall_low, DESIGN_MAGNET_SKIN_MM, 1
            ),
        ]
        lines.append(f"magnet:     {', '.join(texts)}")
    return lines


def measure_parking_hole(tray, right, figures):
    inward = vector(half_vector((-1.0, 0.0), right))
    across = App.Vector(0, 1, 0)
    face_x = DESIGN_THUMB_EAST_EDGE_X_MM + DESIGN_GAP_MM + DESIGN_WALL_MM
    mouth_plan = half_point((face_x, DESIGN_PARKING_HOLE_Y_MM), right)
    mouth = vector(mouth_plan, DESIGN_PARKING_HOLE_Z_MM)
    _, to_bottom = run_through(tray, mouth.add(inward * 0.5), inward, False)
    depth = to_bottom + 0.5
    middle = mouth.add(inward * (depth / 2.0))
    across_low, across_high = run_through(tray, middle, across, False)
    down, _up = run_through(tray, middle, UP, False)
    top, flat = flat_top(tray, middle, across)
    back_low, back_high = run_through(tray, mouth.add(inward * (depth + 0.1)), inward, True)
    over, where = least_plastic_over(tray, mouth, inward, sample_depths(0.1, depth - 0.1))
    # The boss's own width 1.0 short of the hole's bottom: nearer the
    # mouth it merges with the lower dowel boss.
    beside = mouth.add(inward * (depth - 1.0)).add(
        UP * (DESIGN_PARKING_HOLE_DIAMETER_MM / 2.0 + 0.5)
    )
    boss_low, boss_high = run_through(tray, beside, across, True)
    _boss_bottom, boss_top = run_through(tray, beside, UP, True)
    over_text = figures.check("least plastic over it", over, DESIGN_PLASTIC_OVER_PARKING_HOLE_MM, 2)
    texts = [
        figures.check("deep", depth, DESIGN_PARKING_HOLE_DEPTH_MM, 1),
        figures.check("across", across_high - across_low, DESIGN_PARKING_HOLE_DIAMETER_MM, 1),
        figures.check(
            "at y", middle.y + (across_low + across_high) / 2.0, DESIGN_PARKING_HOLE_Y_MM, 1
        ),
        figures.check(
            "axis z",
            middle.z + down + DESIGN_PARKING_HOLE_DIAMETER_MM / 2.0,
            DESIGN_PARKING_HOLE_Z_MM,
            1,
        ),
        f"top {top:.3f} above the axis",
        figures.check("flat top", flat, DESIGN_PARKING_HOLE_FLAT_MM, 2),
        f"{over_text} (at {where:.2f} in)",
        figures.check(
            "boss behind the bottom",
            back_high - back_low,
            DESIGN_PARKING_BOSS_BEHIND_HOLE_MM,
            1,
        ),
        figures.check("boss across", boss_high - boss_low, DESIGN_PARKING_BOSS_ACROSS_MM, 1),
        figures.check("boss top z", beside.z + boss_top, DESIGN_LEDGE_TOP_Z_MM, 1),
    ]
    return f"parking:    {', '.join(texts)}"


def relief_way_in(right, center, into):
    """The unit way from a relief's center into its body on the given
    half (DESIGN_POST_RELIEFS)."""
    if into == "slant":
        return design_slant_frame(right)[1]
    if into[0] == "corner":
        plan, corner = half_point(center, right), half_point(into[1], right)
        length = math.dist(plan, corner)
        return ((corner[0] - plan[0]) / length, (corner[1] - plan[1]) / length)
    return half_vector(into, right)


def measure_post_relief(tray, right, relief, figures):
    """A relief under a switch's post or peg (DESIGN_POST_RELIEFS): across
    at its mouth, twice the run from its center the way into its body to
    its wall 0.25 under the body's top; its bottom, in the middle of what
    it cuts, between the body's face 0.25 under the bottom and that wall;
    and open over the post's or peg's place, its hole's edge farthest into
    the body, from no higher than the bottom up past the rim."""
    key, post_or_peg, center, hole, into, diameter = relief
    what = f"{layout.key_name_on_half(key, right)}'s {post_or_peg}"
    way = vector(relief_way_in(right, center, into))
    plan = half_point(center, right)
    end = DESIGN_POST_ENDS_Z_MM
    _back, radius = run_through(tray, vector(plan, DESIGN_LEDGE_TOP_Z_MM - 0.25), way, False)
    _back, face = run_through(tray, vector(plan, DESIGN_POST_RELIEF_BOTTOM_Z_MM - 0.25), way,
                              False)
    middle = vector(plan, end).add(way * ((face + radius) / 2.0))
    bottom = end + run_through(tray, middle, UP, False)[0]
    low, high = run_through(tray, vector(plan, end).add(way * (hole / 2.0)), UP, False)
    if end + low > bottom + SAME_PLACE_MM or end + high < DESIGN_RIM_Z_MM:
        figures.problems.append(f"the relief for {what} is not open over its place")
    texts = [
        figures.check(f"{what} at ({plan[0]:.3f}, {plan[1]:.3f}), across at its mouth",
                      2.0 * radius, diameter, 1),
        f"{radius - face:.3f} into the body",
        figures.check("bottom z", bottom, DESIGN_POST_RELIEF_BOTTOM_Z_MM, 1),
        "open over its place",
    ]
    return f"relief:     {', '.join(texts)}"


def measure_joint_face_chamfer(tray, right, figures):
    """The joint face's bottom edge chamfer at the slant's middle: how
    far it reaches in along the bed and up the face."""
    _south, _direction, normal = design_slant_frame(right)
    face = DESIGN_JOINT_FACE_OUT_OF_SLANT_MM
    bed = DESIGN_FLOOR_UNDERSIDE_Z_MM
    on_bed = slant_place(right, SLANT_PROBE_ALONG_MM, face - 1.0, bed + 0.001)
    _low, high = run_through(tray, on_bed, vector(normal), True)
    on_face = slant_place(right, SLANT_PROBE_ALONG_MM, face - 0.001, bed + 1.0)
    low, _high = run_through(tray, on_face, UP, True)
    size = DESIGN_JOINT_FACE_BOTTOM_CHAMFER_MM
    texts = [
        figures.check("in along the bed", 1.0 - high + 0.001, size, 1),
        figures.check("up the face", 1.0 + low + 0.001, size, 1),
    ]
    return (
        f"chamfer:    the joint face's bottom edge at {SLANT_PROBE_ALONG_MM} along the slant: "
        f"{', '.join(texts)}"
    )


def half_sockets(right):
    """(key name on the half, polygon) of every socket polygon of the
    given half in its own frame: on the right half the left footprint at
    the mirrored key center (layout.py's module docstring)."""
    for name, center in layout.key_centers_on_half(right).items():
        placed = layout.mirror_for_right_half(center) if right else center
        for polygon in layout.socket_polygons(placed):
            yield name, polygon


def measure_socket_clearance(tray, right, figures):
    """Every socket of the half, a prism from its bottom to the PCB's
    underside, against the exported tray itself: the end to end check
    that the cuts landed where the sockets are, mirroring included."""
    closest = (math.inf, "nothing")
    count = 0
    for name, polygon in half_sockets(right):
        points = [App.Vector(x, y, DESIGN_SOCKET_BOTTOM_Z_MM) for x, y in polygon]
        prism = Part.Face(Part.makePolygon(points + [points[0]])).extrude(
            UP * (DESIGN_LEDGE_TOP_Z_MM - DESIGN_SOCKET_BOTTOM_Z_MM)
        )
        distance = prism.distToShape(tray)[0]
        count += 1
        if distance < closest[0]:
            closest = (distance, name)
    if closest[0] < DESIGN_LEAST_SOCKET_CLEARANCE_MM - 1e-6:
        raise SystemExit(
            f"error: {closest[1]}'s socket comes {closest[0]:.4f} from the tray, DESIGN.md "
            f"keeps {DESIGN_LEAST_SOCKET_CLEARANCE_MM}"
        )
    text = figures.check("least clearance", closest[0], DESIGN_LEAST_SOCKET_CLEARANCE_MM, 1)
    return (
        f"sockets:    {count} socket polygons of {len(layout.KEY_CENTERS_MM)} keys (z "
        f"{DESIGN_SOCKET_BOTTOM_Z_MM} to {DESIGN_LEDGE_TOP_Z_MM}) against the tray as cut: "
        f"{text}, at {closest[1]}'s"
    )


def frame_wall_prism(key_center):
    """A frame pocket's walls' outer face as a prism over their heights:
    the socket's outline moved out by DESIGN_FRAME_WALL_REACH_MM, its
    corners extended, as frame_shape.py builds it."""
    bottom, top = DESIGN_FRAME_WALLS_Z_MM
    prism = cells.pocket_face(key_center, DESIGN_FRAME_WALL_REACH_MM).extrude(UP * (top - bottom))
    prism.translate(UP * bottom)
    return prism


def tray_without_standoffs(tray, right):
    """The tray less its standoffs, which the frame's walls and tubes are
    measured against: the standoffs end at the walls' mouth, where the
    tubes stand on them (work item 034), so a wall or a tube meets one
    only in that plane, where the frame stands on it. Each goes as a
    cylinder STANDOFF_CUTTER_MARGIN_MM wider than it, which takes the
    merged one's share of the joint block below the cylinder's top with
    it. The block stands in plan over it as it does below, up to the
    walls' and the tubes' top, so they measure the same against it."""
    radius = DESIGN_STANDOFF_DIAMETER_MM / 2.0 + STANDOFF_CUTTER_MARGIN_MM
    bottom = STANDOFF_CUTTER_BOTTOM_Z_MM
    height = DESIGN_STANDOFF_TOP_Z_MM + STANDOFF_CUTTER_PAST_TOP_MM - bottom
    cutters = [Part.makeCylinder(radius, height, vector(half_point(drill, right), bottom), UP)
               for drill in DESIGN_MOUNTING_DRILLS_MM]
    return tray.cut(Part.makeCompound(cutters))


def measure_frame_wall_clearance(tray, right, figures):
    """Every pocket's walls of the hand-wired frame on the half (on the
    right half the left one's at the mirrored key center, as
    half_sockets()) against the exported tray less its standoffs
    (tray_without_standoffs()): the walls stand whole, so the tray gives
    way to them."""
    closest = (math.inf, "nothing")
    cut_back = {key for key, _body in layout.frame_walls_cut_back(right)}
    for name, center in layout.key_centers_on_half(right).items():
        if name in cut_back:
            continue
        placed = layout.mirror_for_right_half(center) if right else center
        distance = frame_wall_prism(placed).distToShape(tray)[0]
        if distance < closest[0]:
            closest = (distance, name)
    if closest[0] < DESIGN_FRAME_WALL_CLEARANCE_MM - FRAME_WALL_ARC_TOLERANCE_MM:
        raise SystemExit(
            f"error: {closest[1]}'s frame pocket walls come {closest[0]:.4f} from the tray, "
            f"DESIGN.md keeps {DESIGN_FRAME_WALL_CLEARANCE_MM}"
        )
    text = figures.check("least clearance", closest[0], DESIGN_FRAME_WALL_CLEARANCE_MM, 1)
    bottom, top = DESIGN_FRAME_WALLS_Z_MM
    left_out = f", {', '.join(sorted(cut_back))}'s left out, still cut back" if cut_back else ""
    return (
        f"frame:      the hand-wired frame's pocket walls of "
        f"{len(layout.KEY_CENTERS_MM) - len(cut_back)} keys ({DESIGN_FRAME_WALL_REACH_MM} out of "
        f"the socket, z {bottom} to {top}) against the tray as cut, its standoffs left out: "
        f"{text} ({closest[0]:.4f}), at {closest[1]}'s{left_out}"
    )


def frame_tube_prism(drill, right):
    """The frame's tube on the standoff at a DESIGN.md drill as a prism
    over its heights on the given half: the standoff's circle (its
    flats, which only take more away, left out), cut
    DESIGN_FRAME_WALL_CLEARANCE_MM short of the joint block's inner face
    where it would come nearer."""
    bottom, top = DESIGN_STANDOFF_TOP_Z_MM, DESIGN_FRAME_WALLS_Z_MM[1]
    radius = DESIGN_STANDOFF_DIAMETER_MM / 2.0
    prism = Part.makeCylinder(radius, top - bottom, vector(half_point(drill, right), bottom), UP)
    along, outward = design_slant_coordinates(drill)
    limit = (DESIGN_JOINT_FACE_OUT_OF_SLANT_MM - DESIGN_JOINT_BLOCK_THICKNESS_MM
             - DESIGN_FRAME_WALL_CLEARANCE_MM)
    if outward + radius <= limit:
        return prism
    reach = DESIGN_STANDOFF_DIAMETER_MM
    corners = [slant_place(right, along + side, out, bottom - 1.0)
               for side, out in ((-reach, limit), (reach, limit), (reach, limit + reach),
                                 (-reach, limit + reach))]
    beyond = Part.Face(Part.makePolygon(corners + [corners[0]])).extrude(UP * (top - bottom + 2.0))
    return prism.cut(beyond)


def measure_frame_tube_clearance(tray, right, figures):
    """The hand-wired frame's tubes (frame_tube_prism()) against the
    exported tray less its standoffs (tray_without_standoffs())."""
    closest = (math.inf, "nothing")
    for drill in DESIGN_MOUNTING_DRILLS_MM:
        distance = frame_tube_prism(drill, right).distToShape(tray)[0]
        if distance < closest[0]:
            closest = (distance, half_point(drill, right))
    if closest[0] < DESIGN_FRAME_TUBES_FROM_TRAY_MM - FRAME_WALL_ARC_TOLERANCE_MM:
        raise SystemExit(
            f"error: the frame's tube at {closest[1]} comes {closest[0]:.4f} from the tray, "
            f"DESIGN.md keeps {DESIGN_FRAME_TUBES_FROM_TRAY_MM}"
        )
    text = figures.check("least clearance", closest[0], DESIGN_FRAME_TUBES_FROM_TRAY_MM, 1)
    return (
        f"frame:      the hand-wired frame's {len(DESIGN_MOUNTING_DRILLS_MM)} tubes (the "
        f"standoffs' {DESIGN_STANDOFF_DIAMETER_MM} circles, z {DESIGN_STANDOFF_TOP_Z_MM} to "
        f"{DESIGN_FRAME_WALLS_Z_MM[1]}) against the tray as cut, its standoffs left out: {text} "
        f"({closest[0]:.4f}), at the one at ({closest[1][0]:.3f}, {closest[1][1]:.3f})"
    )


# The parts' mounts.


class Board:
    """The nice!nano's board where DESIGN.md places it, its size
    DESIGN.md's or a test print's: its edges in the left half's frame.
    The west edge and the USB end stay put whatever the size."""

    def __init__(self, width, length):
        self.west = DESIGN_NANO_WEST_X_MM
        self.east = DESIGN_NANO_WEST_X_MM + width
        self.north = DESIGN_NANO_USB_END_Y_MM
        self.south = DESIGN_NANO_USB_END_Y_MM - length
        self.center = (self.west + self.east) / 2.0
        self.width = width
        self.ledge_face = self.west - DESIGN_NANO_FROM_STEP_LEDGE_FACE_MM  # the pocket's west face


class MountDesign:
    """What the mounts are measured against: DESIGN.md's figures, a test
    print's key=value overrides in their place. A figure that is an
    override is checked against it, one that follows from an override
    only printed."""

    def __init__(self, arguments):
        width = DESIGN_NANO_SIZE_MM[0] if arguments.nano_width is None else arguments.nano_width
        length = DESIGN_NANO_SIZE_MM[1] if arguments.nano_length is None else arguments.nano_length
        self.board = Board(width, length)
        self.pocket_fit = (DESIGN_NANO_POCKET_FIT_MM if arguments.nano_pocket_fit is None
                           else arguments.nano_pocket_fit)
        self.clamp_press_overridden = arguments.clamp_press is not None
        self.clamp_press = arguments.clamp_press  # None: DESIGN.md's
        self.bar_clearance = (
            DESIGN_NANO_BAR_CLEARANCE_MM
            if arguments.bar_clearance is None
            else arguments.bar_clearance
        )


def half_place(right, point):
    """A left half's (x, y, z) on the given half."""
    x, y, z = point
    return vector(half_point((x, y), right), z)


def run_span(tray, right, point, axis, material):
    """(low, high) along "x", "y" or "z" in the left half's frame of the
    material (or, with material False, the empty) run through the left
    half's point, measured on the given half. An open end reads
    PROBE_REACH_MM away."""
    direction = {"x": App.Vector(1, 0, 0), "y": App.Vector(0, 1, 0), "z": UP}[axis]
    if axis == "x" and right:
        direction = direction * -1.0
    low, high = run_through(tray, half_place(right, point), direction, material)
    origin = point["xyz".index(axis)]
    return origin + low, origin + high


def span_length(span):
    return span[1] - span[0]


def span_middle(span):
    return (span[0] + span[1]) / 2.0


def worst_offset(measured, expected):
    """The measured edge farthest from its expected place, signed."""
    offsets = [got - want for got, want in zip(measured, expected)]
    return max(offsets, key=abs)


def north_wall_faces(part):
    """(inner, outer) y of DESIGN.md's north wall behind the part."""
    edge = DESIGN_NORTH_EDGES_Y_MM[part]
    return edge + DESIGN_GAP_MM, edge + DESIGN_GAP_MM + DESIGN_WALL_MM


def opening_chamfer(tray, right, point, width):
    """A 45 degree chamfer's size from an opening's width along x 0.05
    inside a face, as measure_pin_hole() reads a lead-in."""
    widening = (span_length(run_span(tray, right, point, "x", False)) - width) / 2.0
    return widening + 0.05 if widening > 1e-6 else 0.0


def window_corner_radius(tray, right, x, y, top, half_width):
    """The window's corner radius from its half width 0.2 under its top:
    a corner of radius r takes a off the width and b off the height
    where (r - a)^2 + (r - b)^2 = r^2."""
    below_top = 0.2
    across = run_span(tray, right, (x, y, top - below_top), "x", False)
    off_width = half_width - span_length(across) / 2.0
    return off_width + below_top + math.sqrt(2.0 * off_width * below_top)


def shell_mouth_y(board):
    return board.north + DESIGN_SHELL_PAST_BOARD_MM


def channel_top_z(design):
    return DESIGN_SHELL_TOP_Z_MM + DESIGN_PRINT_SWELLING_PER_SIDE_MM + design.bar_clearance


def measure_usb_window(tray, right, design, figures):
    """The window between the shell's mouth and the outer chamfer, and
    its chamfers. The shell's channel runs on past the mouth there, into
    the outer chamfer's depth for the board's play north, but it lies
    inside the window's outline except at the corners, so it meets
    neither the middle lines nor the line under the window's top that
    gives the corner."""
    board = design.board
    _inner, outer = north_wall_faces("nice!nano")
    mouth = shell_mouth_y(board)
    width, height = DESIGN_USB_WINDOW_MM
    straight_y = (mouth + outer - DESIGN_USB_WINDOW_CHAMFER_MM["outer"]) / 2.0
    middle = (board.center, straight_y, DESIGN_USB_WINDOW_CENTER_Z_MM)
    across = run_span(tray, right, middle, "x", False)
    up = run_span(tray, right, middle, "z", False)
    half_width = span_length(across) / 2.0
    radius = window_corner_radius(tray, right, middle[0], middle[1], up[1], half_width)
    outer_chamfer = opening_chamfer(tray, right, (middle[0], outer - 0.05, middle[2]), width)
    inner_chamfer = opening_chamfer(tray, right, (middle[0], mouth + 0.05, middle[2]), width)
    texts = [
        figures.check("wide", span_length(across), width, 1),
        figures.check("tall", span_length(up), height, 1),
        figures.check("off the shell's middle", span_middle(across) - board.center, 0.0, 2),
        figures.check("middle z", span_middle(up), DESIGN_USB_WINDOW_CENTER_Z_MM, 2),
        figures.check(
            "bottom z", up[0], round(DESIGN_USB_WINDOW_CENTER_Z_MM - height / 2.0, 2), 2
        ),
        figures.check("corners", radius, DESIGN_USB_WINDOW_CORNER_RADIUS_MM, 2),
        figures.check("outer chamfer", outer_chamfer, DESIGN_USB_WINDOW_CHAMFER_MM["outer"], 1),
        figures.check("inner chamfer", inner_chamfer, DESIGN_USB_WINDOW_CHAMFER_MM["inner"], 1),
    ]
    return f"USB window: {', '.join(texts)}"


def measure_usb_channel(tray, right, design, figures):
    """The shell's channel through the wall's inner part: across and up
    in the wall, its end past the shell's mouth at a top corner, where
    it reaches out of the window's corner round."""
    board = design.board
    inner, _outer = north_wall_faces("nice!nano")
    mouth = shell_mouth_y(board)
    in_wall = (board.center, (inner + mouth) / 2.0, DESIGN_NANO_SEAT_Z_MM + 1.0)
    across = run_span(tray, right, in_wall, "x", False)
    up = run_span(tray, right, in_wall, "z", False)
    corner = (board.center + DESIGN_NANO_BAR_OPENING_MM / 2.0 - 0.1, in_wall[1],
              channel_top_z(design) - 0.05)
    end = run_span(tray, right, corner, "y", False)[1]
    over_shell = up[1] - DESIGN_PRINT_SWELLING_PER_SIDE_MM - DESIGN_SHELL_TOP_Z_MM
    texts = [
        figures.check("wide", span_length(across), DESIGN_NANO_BAR_OPENING_MM, 2),
        figures.check("off the shell's middle", span_middle(across) - board.center, 0.0, 2),
        figures.check("from z", up[0], DESIGN_NANO_SEAT_Z_MM, 2),
        figures.check("over the shell as printed", over_shell, design.bar_clearance, 2),
        figures.check("past the shell's mouth", end - mouth, DESIGN_USB_CHANNEL_PAST_MOUTH_MM, 2),
    ]
    return f"channel:    {', '.join(texts)}"


def measure_nano_north_block(tray, right, design, figures):
    """The north block between the board's USB end and the wall: its
    opening for the shell with the sill under it and the bar over it,
    its south faces, and its ends, where it stands to its top: the west
    one at the ledge cut-away's, the east one free in column 3's
    cavity."""
    board = design.board
    inner, _outer = north_wall_faces("nice!nano")
    y = inner - 0.1
    in_opening = (board.center, y, DESIGN_NANO_SEAT_Z_MM + 1.0)
    opening = run_span(tray, right, in_opening, "x", False)
    under = run_span(tray, right, in_opening, "z", False)
    in_bar = (board.center, y, under[1] + 0.1)
    bar = run_span(tray, right, in_bar, "z", True)
    # Over the seat, which runs on south from the block's sides.
    sides = [(opening[0] - 1.0, y, in_opening[2]), (opening[1] + 1.0, y, in_opening[2])]
    south_faces = [run_span(tray, right, point, "y", True)[0] for point in [in_bar] + sides]
    south_gap = worst_offset(south_faces, [board.north] * 3)
    west_end = run_span(tray, right, (board.center, y, bar[1] + 0.5), "x", False)[0]
    # The east end stands past column 2's north edge, in column 3's
    # cavity, where the built tray rounds the step's ledge corner away:
    # nothing stops a run over the block there, so this one runs
    # through the block's east side.
    east_end = run_span(tray, right, sides[1], "x", True)[1]
    end_tops = [run_span(tray, right, (x, y, 1.0), "z", True)[1]
                for x in (west_end + 0.05, east_end - 0.05)]
    mouth = shell_mouth_y(board)
    over_channel = (channel_top_z(design) + DESIGN_USB_WINDOW_CENTER_Z_MM
                    + DESIGN_USB_WINDOW_MM[1] / 2.0) / 2.0
    deep = run_span(tray, right, (board.center, mouth - 0.1, over_channel), "y", True)
    past = DESIGN_NANO_NORTH_BLOCK_PAST_BOARD_MM
    texts = [
        figures.check("opening", span_length(opening), DESIGN_NANO_BAR_OPENING_MM, 2),
        figures.check("off the shell's middle", span_middle(opening) - board.center, 0.0, 2),
        figures.check("its sill's top z", under[0], DESIGN_NANO_SEAT_Z_MM, 2),
        figures.check(
            "bar over the shell as printed",
            under[1] - DESIGN_PRINT_SWELLING_PER_SIDE_MM - DESIGN_SHELL_TOP_Z_MM,
            design.bar_clearance,
            2,
        ),
        figures.check("bar tall", span_length(bar), DESIGN_NANO_BAR_HEIGHT_MM, 1),
        figures.check("deep", span_length(deep), DESIGN_NANO_BAR_DEPTH_MM, 2),
        figures.check("to the shell's mouth", deep[1] - mouth, 0.0, 2),
        figures.check("from the board's USB end", south_gap, DESIGN_NANO_END_GAP_MM, 2),
        figures.check("from x", west_end, round(board.west - past, 3), 3),
        figures.check("to", east_end, round(board.east + past, 3), 3),
        figures.check("its top z at both ends",
                      max(end_tops, key=lambda top: abs(top - bar[1])),
                      round(channel_top_z(design) + DESIGN_NANO_BAR_HEIGHT_MM, 2), 2),
    ]
    return f"block:      north: {', '.join(texts)}"


def unless(overridden, stated):
    """A DESIGN.md figure to check against, or None (only print it) when
    it follows from a test print's override."""
    return None if overridden else stated


def clamp_block_top_z(design):
    """The block's top: DESIGN.md's, or the board's top plus the nose's
    depth less a clamp_press override."""
    if design.clamp_press is None:
        return DESIGN_CLAMP_BLOCK_TOP_Z_MM
    return DESIGN_NANO_TOP_Z_MM + DESIGN_CLAMP_NOSE_DEPTH_MM - design.clamp_press


def clamp_block_south_y(board):
    return board.south - DESIGN_CLAMP_SCREW_FROM_BOARD_MM - DESIGN_CLAMP_BLOCK_ALONG_MM / 2.0


def measure_nano_clamp(tray, right, design, figures):
    """The clamp's foot, its north face against the board's end gap, the
    block with its top, its east face and the insert bore, the bore's
    axis from the board's south end, the floor left under it and the
    room it leaves the insert as printed."""
    board = design.board
    stop_face = board.south - DESIGN_NANO_FOOT_GAP_MM
    in_foot = (board.center, stop_face - 0.5, DESIGN_CLAMP_FOOT_TOP_Z_MM / 2.0)
    foot_along = run_span(tray, right, in_foot, "y", True)
    foot_up = run_span(tray, right, in_foot, "z", True)
    screw_y = board.south - DESIGN_CLAMP_SCREW_FROM_BOARD_MM
    block_middle_z = (DESIGN_CLAMP_FOOT_TOP_Z_MM + DESIGN_CLAMP_BLOCK_TOP_Z_MM) / 2.0
    in_block = (board.center + (DESIGN_CLAMP_BORE_MM + DESIGN_CLAMP_BLOCK_ALONG_MM) / 4.0, screw_y,
                block_middle_z)
    block_along = run_span(tray, right, in_block, "y", True)
    block_east = run_span(tray, right, in_block, "x", True)[1]
    block_top = run_span(tray, right, in_block, "z", True)[1]
    in_bore = (board.center, screw_y, block_middle_z)
    bore_across = run_span(tray, right, in_bore, "x", False)
    bore_along = run_span(tray, right, in_bore, "y", False)
    bore_bottom = run_span(tray, right, in_bore, "z", False)[0]
    under_bore = run_span(tray, right, (board.center, screw_y, bore_bottom - 0.1), "z", True)
    room = block_top - bore_bottom - DESIGN_PRINT_SWELLING_PER_SIDE_MM
    follows = design.clamp_press_overridden
    texts = [
        figures.check("foot from the board's south end", board.south - foot_along[1],
                      DESIGN_NANO_FOOT_GAP_MM, 2),
        figures.check("foot top z", foot_up[1], DESIGN_CLAMP_FOOT_TOP_Z_MM, 1),
        figures.check("block along", span_length(block_along), DESIGN_CLAMP_BLOCK_ALONG_MM, 1),
        figures.check("from y", block_along[0], round(clamp_block_south_y(board), 3), 3),
        figures.check("its east face x", block_east, DESIGN_NANO_EAST_WALL_OUTER_X_MM, 1),
        figures.check("top z", block_top, clamp_block_top_z(design), 2),
        figures.check("bore", span_length(bore_across), DESIGN_CLAMP_BORE_MM, 1),
        figures.check("its axis from the board's south end", board.south - span_middle(bore_along),
                      DESIGN_CLAMP_SCREW_FROM_BOARD_MM, 2),
        figures.check("off the board's middle", span_middle(bore_across) - board.center, 0.0, 2),
        figures.check("bore down to z", bore_bottom, 0.0, 2),
        figures.check("floor under it", span_length(under_bore), DESIGN_FLOOR_MM, 1),
        check_or_report(figures, "the insert's room as printed", room,
                        unless(follows, DESIGN_CLAMP_INSERT_ROOM_PRINTED_MM), 2),
    ]
    return f"clamp:      {', '.join(texts)}"


def pocket_east_x(design):
    """The pocket's east face: the board as a fit from the pocket's west
    face, the print's swelling on both sides and the fit's clearance."""
    board = design.board
    return (board.ledge_face + board.width + 2.0 * DESIGN_PRINT_SWELLING_PER_SIDE_MM
            + design.pocket_fit)


def unraised_y(side, south):
    """The middle of the first stretch of a wall that does not rise,
    from its south end north."""
    for low, high in DESIGN_NANO_RAISED_WALLS_Y_MM[side]:
        if low > south + 1e-6:
            return (south + low) / 2.0
        south = high
    return (south + DESIGN_NANO_WALLS_NORTH_Y_MM[side]) / 2.0


def measure_raised_pieces(tray, right, side, outer_x, figures):
    """(texts) of a wall's raised pieces: each one's ends along y and its
    top, at its middle in the wall's outer part."""
    inward = 1.0 if side == "west" else -1.0
    x = outer_x + inward * 0.5
    texts = []
    for low, high in DESIGN_NANO_RAISED_WALLS_Y_MM[side]:
        point = (x, (low + high) / 2.0, (DESIGN_NANO_EAST_WALL_TOP_Z_MM
                                          + DESIGN_NANO_RAISED_WALL_TOP_Z_MM) / 2.0)
        along = run_span(tray, right, point, "y", True)
        top = run_span(tray, right, point, "z", True)[1]
        texts.extend([
            figures.check("raised from y", along[0], low, 3),
            figures.check("to", along[1], high, 3),
            figures.check("top z", top, DESIGN_NANO_RAISED_WALL_TOP_Z_MM, 1),
        ])
    return texts


def measure_nano_walls(tray, right, design, figures):
    """The pocket across the board, from its west face to its east face,
    and each wall: its outer face, its top where it does not rise, its
    north face, its south end running into the clamp's block, and its
    raised pieces."""
    board = design.board
    middle_y = (board.south + DESIGN_NANO_WALLS_NORTH_Y_MM["west"]) / 2.0
    over_seat = (DESIGN_NANO_SEAT_Z_MM + DESIGN_NANO_TOP_Z_MM) / 2.0
    pocket = run_span(tray, right, (board.center, middle_y, over_seat), "x", False)
    texts = [
        figures.check("pocket from x", pocket[0], round(board.ledge_face, 3), 3),
        figures.check("across", span_length(pocket), round(pocket_east_x(design) - board.ledge_face,
                                                             3), 3),
        figures.check("the east wall's inner face from the board's east edge",
                      pocket[1] - board.east, round(pocket_east_x(design) - board.east, 3), 3),
    ]
    block_north = clamp_block_south_y(board) + DESIGN_CLAMP_BLOCK_ALONG_MM
    for side, outer_x, outer_end in (("west", DESIGN_NANO_WEST_WALL_OUTER_X_MM, 0),
                                     ("east", DESIGN_NANO_EAST_WALL_OUTER_X_MM, 1)):
        inward = 1.0 if side == "west" else -1.0
        in_wall = (outer_x + inward * 0.5, unraised_y(side, block_north), 2.0)
        across = run_span(tray, right, in_wall, "x", True)
        along = run_span(tray, right, in_wall, "y", True)
        top = run_span(tray, right, in_wall, "z", True)[1]
        texts.extend([
            figures.check(f"the {side} wall's outer face x", across[outer_end], outer_x, 3),
            figures.check("top z", top, DESIGN_NANO_EAST_WALL_TOP_Z_MM, 1),
            figures.check("north face y", along[1], DESIGN_NANO_WALLS_NORTH_Y_MM[side], 3),
            figures.check("running into the clamp's block, to its south face y", along[0],
                          round(clamp_block_south_y(board), 3), 3),
        ])
        texts.extend(measure_raised_pieces(tray, right, side, outer_x, figures))
    return f"walls:      {', '.join(texts)}"


def strip_pockets_middle_y(board):
    north, south = DESIGN_NANO_STRIP_POCKETS_FROM_USB_END_MM
    return board.north - (north + south) / 2.0


def measure_nano_seat(tray, right, design, figures):
    """The seat under the board, its top and its edges, and the channels
    beside it, from the pocket's side faces down to the floor's top,
    halfway along the strips' pockets."""
    board = design.board
    y = strip_pockets_middle_y(board)
    in_seat = (board.center, y, DESIGN_NANO_SEAT_Z_MM / 2.0)
    across = run_span(tray, right, in_seat, "x", True)
    top = run_span(tray, right, in_seat, "z", True)[1]
    channels = [run_span(tray, right, (x, y, DESIGN_NANO_SEAT_Z_MM / 2.0), "x", False)
                for x in (board.west + 1.0, board.east - 1.0)]
    bottoms = [run_span(tray, right, (x, y, DESIGN_NANO_SEAT_Z_MM / 2.0), "z", False)[0]
               for x in (board.west + 1.0, board.east - 1.0)]
    inside = DESIGN_NANO_SEAT_INSIDE_EDGES_MM
    texts = [
        figures.check("top z", top, DESIGN_NANO_SEAT_Z_MM, 2),
        figures.check("from x", across[0], round(board.west + inside, 3), 3),
        figures.check("to", across[1], round(board.east - inside, 3), 3),
        figures.check("west channel from x", channels[0][0], round(board.ledge_face, 3), 3),
        figures.check("east channel to x", channels[1][1], round(pocket_east_x(design), 3), 3),
        figures.check("their bottoms z", max(bottoms, key=abs), 0.0, 2),
    ]
    return f"seat:       {', '.join(texts)}"


def measure_nano_strip_pockets(tray, right, design, figures):
    """The socket strips' pockets over the board's top: the walls' inner
    faces cut back, both open from the board's top up, the west one's
    ends, its north end in the column 1/2 step's ledge, and the east
    one's south end."""
    board = design.board
    y = strip_pockets_middle_y(board)
    z = (DESIGN_NANO_TOP_Z_MM + DESIGN_NANO_EAST_WALL_TOP_Z_MM) / 2.0
    outside = DESIGN_NANO_STRIP_POCKETS_OUTSIDE_EDGES_MM
    west_point = (board.west - outside / 2.0, y, z)
    east_point = (board.east + outside / 2.0, y, z)
    across = run_span(tray, right, west_point, "x", False)
    west_along = run_span(tray, right, west_point, "y", False)
    east_south = run_span(tray, right, east_point, "y", False)[0]
    bottoms = [run_span(tray, right, point, "z", False)[0] for point in (west_point, east_point)]
    north, south = DESIGN_NANO_STRIP_POCKETS_FROM_USB_END_MM
    texts = [
        figures.check("west face x", across[0], round(board.west - outside, 3), 3),
        figures.check("east face x", across[1], round(board.east + outside, 3), 3),
        figures.check("from z", max(bottoms, key=lambda bottom: abs(bottom - DESIGN_NANO_TOP_Z_MM)),
                      DESIGN_NANO_TOP_Z_MM, 2),
        figures.check("the west one from y", west_along[0], round(board.north - south, 4), 4),
        figures.check("to", west_along[1], round(board.north - north, 4), 4),
        figures.check("the east one from y", east_south, round(board.north - south, 4), 4),
    ]
    return f"strips:     pockets: {', '.join(texts)}"


def measure_nano_pry_slot(tray, right, design, figures):
    """The pry slot through the clamp's block and foot, open across its
    width at mid height in each, solid beside it and open above, and the
    recess under the board's south end, the seat left out: its east face
    from the ledge's face (the west channel runs on into it), its end
    under the board, its bottom, the floor's top, and the floor under
    it."""
    board = design.board
    slot_west = board.ledge_face + DESIGN_PRY_SLOT_FROM_LEDGE_FACE_MM
    middle_x = slot_west + DESIGN_PRY_SLOT_WIDTH_MM / 2.0
    in_block = (middle_x, board.south - DESIGN_CLAMP_SCREW_FROM_BOARD_MM,
                DESIGN_CLAMP_BLOCK_TOP_Z_MM / 2.0)
    in_foot = (middle_x, board.south - DESIGN_NANO_FOOT_GAP_MM - 0.5,
               DESIGN_CLAMP_FOOT_TOP_Z_MM / 2.0)
    widths = [run_span(tray, right, point, "x", False) for point in (in_block, in_foot)]
    ups = [run_span(tray, right, point, "z", False) for point in (in_block, in_foot)]
    if min(up[1] for up in ups) < DESIGN_RIM_Z_MM:
        figures.problems.append("the pry slot is not open above")
    in_recess = (middle_x, board.south + DESIGN_PRY_RECESS_UNDER_BOARD_MM / 2.0,
                 DESIGN_NANO_SEAT_Z_MM / 2.0)
    recess_across = run_span(tray, right, in_recess, "x", False)
    recess_along = run_span(tray, right, in_recess, "y", False)
    bottom = run_span(tray, right, in_recess, "z", False)[0]
    floor = run_span(tray, right, (middle_x, in_recess[1], bottom - 0.1), "z", True)
    texts = [
        figures.check("across in the block and the foot",
                      max((span_length(width) for width in widths),
                          key=lambda width: abs(width - DESIGN_PRY_SLOT_WIDTH_MM)),
                      DESIGN_PRY_SLOT_WIDTH_MM, 1),
        figures.check("from the ledge's face", worst_offset([width[0] for width in widths],
                                                            [board.ledge_face] * 2),
                      DESIGN_PRY_SLOT_FROM_LEDGE_FACE_MM, 1),
        "open above",
        figures.check("recess's east face from the ledge's face",
                      recess_across[1] - board.ledge_face,
                      DESIGN_PRY_SLOT_FROM_LEDGE_FACE_MM + DESIGN_PRY_SLOT_WIDTH_MM, 1),
        figures.check("under the board", recess_along[1] - board.south,
                      DESIGN_PRY_RECESS_UNDER_BOARD_MM, 1),
        figures.check("bottom z", bottom, 0.0, 1),
        figures.check("floor under it", span_length(floor), DESIGN_PRY_RECESS_FLOOR_UNDER_MM, 1),
    ]
    return f"pry slot:   {', '.join(texts)}"


def knob_proud_texts(stop_face, outer_face, figures):
    """How far the knob's peaks (its tip) and trough stand past the
    outer face as built, the body's north face on the stop's: as
    modelled, and as printed, the stop's face swollen south pushing the
    body that far and the outer face swollen north."""
    texts = []
    for where, short_of_tip, stated in (("peaks", 0.0, DESIGN_KNOB_PEAKS_PROUD_MM),
                                        ("trough", DESIGN_KNOB_TROUGH_SHORT_OF_TIP_MM,
                                         DESIGN_KNOB_TROUGH_PROUD_MM)):
        for printed in (False, True):
            swelling = DESIGN_PRINT_SWELLING_PER_SIDE_MM if printed else 0.0
            point = stop_face - swelling + DESIGN_KNOB_LENGTH_MM - short_of_tip
            label = f"{where} proud of the outer face {'as printed' if printed else 'as modelled'}"
            texts.append(figures.check(label, point - (outer_face + swelling), stated[printed], 2))
    return texts


def measure_power_switch(tray, right, figures):
    center = DESIGN_POWER_SWITCH_CENTER_X_MM
    inner, outer = north_wall_faces("power switch")
    ledge_face = inner - DESIGN_LEDGE_WIDTH_MM
    in_slot = (center, (inner + outer) / 2.0, DESIGN_KNOB_SLOT_CENTER_Z_MM)
    across = run_span(tray, right, in_slot, "x", False)
    up = run_span(tray, right, in_slot, "z", False)
    through = run_span(tray, right, in_slot, "y", False)
    # Beside the slot the stop, the ledge and the wall are one run of
    # plastic, from the stop's face to the outer face.
    beside_slot = (across[0] - 0.5, (ledge_face + inner) / 2.0, DESIGN_KNOB_SLOT_CENTER_Z_MM)
    stop_face, outer_face = run_span(tray, right, beside_slot, "y", True)
    if through[0] > stop_face or through[1] < outer:
        figures.problems.append("the knob slot does not pass through the stop, the ledge and the "
                                "wall")
    in_stop = (center, (stop_face + ledge_face) / 2.0, DESIGN_KNOB_SLOT_CENTER_Z_MM)
    stop_opening_across = run_span(tray, right, in_stop, "x", False)
    stop_opening_up = run_span(tray, right, in_stop, "z", False)
    over_opening = (DESIGN_KNOB_SLOT_CENTER_Z_MM + DESIGN_KNOB_SLOT_MM[1] / 2.0
                    + DESIGN_POWER_SWITCH_STOP_TOP_Z_MM) / 2.0
    stop_across = run_span(tray, right, (center, in_stop[1], over_opening), "x", True)
    stop_top = run_span(tray, right, (beside_slot[0], in_stop[1], 1.5), "z", True)[1]
    body_y = stop_face - 2.0
    opening = run_span(tray, right, (center, body_y, 1.5), "x", False)
    ends = [
        run_span(tray, right, (opening[0] - 0.1, body_y, 1.5), "x", True),
        run_span(tray, right, (opening[1] + 0.1, body_y, 1.5), "x", True),
    ]
    in_end = (ends[0][1] - 0.3, body_y, 1.5)  # east of the groove's wall
    end_south = run_span(tray, right, in_end, "y", True)[0]
    top = run_span(tray, right, in_end, "z", True)[1]
    in_groove = (in_end[0], end_south - DESIGN_RETAINER_GROOVE_MM / 2.0, 1.5)
    groove = run_span(tray, right, in_groove, "y", False)
    socket = run_span(tray, right, in_groove, "x", False)
    lip = run_span(tray, right, (in_end[0], groove[0] - 0.1, 1.5), "y", True)
    slot_texts = [
        figures.check("wide", span_length(across), DESIGN_KNOB_SLOT_MM[0], 1),
        figures.check("tall", span_length(up), DESIGN_KNOB_SLOT_MM[1], 1),
        figures.check("off x", span_middle(across) - center, 0.0, 2),
        figures.check("middle z", span_middle(up), DESIGN_KNOB_SLOT_CENTER_Z_MM, 2),
    ]
    stop_texts = [
        figures.check("from the ledge's face", ledge_face - stop_face,
                      DESIGN_POWER_SWITCH_STOP_DEPTH_MM, 2),
        figures.check("across", span_length(stop_across), DESIGN_POWER_SWITCH_STOP_ACROSS_MM, 1),
        figures.check("off x", span_middle(stop_across) - center, 0.0, 2),
        figures.check("top z", stop_top, DESIGN_POWER_SWITCH_STOP_TOP_Z_MM, 1),
        figures.check("the slot through it wide", span_length(stop_opening_across),
                      DESIGN_KNOB_SLOT_MM[0], 1),
        figures.check("tall", span_length(stop_opening_up), DESIGN_KNOB_SLOT_MM[1], 1),
        figures.check("middle z", span_middle(stop_opening_up), DESIGN_KNOB_SLOT_CENTER_Z_MM, 2),
    ]
    cradle_texts = [
        figures.check("opening", span_length(opening), DESIGN_CRADLE_OPENING_MM, 1),
        figures.check("off x", span_middle(opening) - center, 0.0, 2),
        figures.check("ends", min(span_length(end) for end in ends), DESIGN_CRADLE_END_MM, 1),
        figures.check("ends from the stop's face", stop_face - end_south,
                      DESIGN_CRADLE_END_LENGTH_MM, 1),
        figures.check("top z", top, DESIGN_CRADLE_TOP_Z_MM, 1),
        figures.check("retainer's groove", span_length(groove), DESIGN_RETAINER_GROOVE_MM, 2),
        figures.check("from the ends", end_south - groove[1], 0.0, 2),
        figures.check("its socket across", span_length(socket), DESIGN_RETAINER_SOCKET_ACROSS_MM,
                      1),
        figures.check("off x", span_middle(socket) - center, 0.0, 2),
        figures.check("lip", span_length(lip), DESIGN_RETAINER_LIP_MM, 1),
    ]
    knob_texts = knob_proud_texts(stop_face, outer_face, figures)
    return [f"knob slot:  {', '.join(slot_texts)}", f"stop:       {', '.join(stop_texts)}",
            f"knob:       {', '.join(knob_texts)}", f"cradle:     {', '.join(cradle_texts)}"]


def measure_reset_button(tray, right, figures):
    center = DESIGN_RESET_CENTER_X_MM
    inner, outer = north_wall_faces("reset button")
    in_hole = (center, (inner + outer) / 2.0, DESIGN_RESET_PIN_HOLE_AXIS_Z_MM)
    across = run_span(tray, right, in_hole, "x", False)
    up = run_span(tray, right, in_hole, "z", False)
    through = run_span(tray, right, in_hole, "y", False)
    if through[0] > inner or through[1] < outer:
        figures.problems.append("the reset pin hole does not pass through the wall")
    radius = span_length(across) / 2.0
    _top, flat = flat_top(tray, half_place(right, in_hole), App.Vector(1, 0, 0))
    in_front = run_span(tray, right, (center, inner - 1.0, DESIGN_RESET_BACK_WALL_TOP_Z_MM - 0.1),
                        "y", False)
    in_wall = (center, in_front[0] - DESIGN_RESET_BACK_WALL_MM / 2.0, 2.0)
    wall = run_span(tray, right, in_wall, "y", True)
    wall_top = run_span(tray, right, in_wall, "z", True)[1]
    in_notch_z = DESIGN_RESET_NOTCH_BOTTOM_Z_MM + 0.5
    notch_texts = []
    for side in (-1.0, 1.0):
        notch_point = (center + side * DESIGN_RESET_NOTCH_FROM_CENTER_MM, in_wall[1], in_notch_z)
        notch = run_span(tray, right, notch_point, "x", False)
        bottom = run_span(tray, right, notch_point, "z", False)[0]
        outer_edge = notch[1] if side > 0 else notch[0]
        end = run_span(tray, right, (outer_edge + side * 0.1, in_wall[1], in_notch_z), "x", True)
        notch_texts.extend([
            figures.check("notch", span_length(notch), DESIGN_RESET_NOTCH_WIDTH_MM, 2),
            figures.check("from the middle", abs(span_middle(notch) - center),
                          DESIGN_RESET_NOTCH_FROM_CENTER_MM, 2),
            figures.check("bottom z", bottom, DESIGN_RESET_NOTCH_BOTTOM_Z_MM, 3),
            figures.check("wall beyond", span_length(end), DESIGN_RESET_BACK_WALL_BEYOND_NOTCHES_MM,
                          1),
        ])
    in_socket = (center, in_front[0] + 2.0, DESIGN_RESET_BACK_WALL_TOP_Z_MM - 0.5)
    apart = run_span(tray, right, in_socket, "x", False)
    side_wall = run_span(tray, right, (apart[0] - DESIGN_RESET_SIDE_WALL_MM / 2.0, in_socket[1],
                                       in_socket[2]), "x", True)
    in_stop = (center, inner - DESIGN_RESET_FRONT_STOP_DEPTH_MM / 2.0, 0.5)
    stop_across = run_span(tray, right, in_stop, "x", True)
    stop_south = run_span(tray, right, in_stop, "y", True)[0]
    stop_top = run_span(tray, right, in_stop, "z", True)[1]
    socket_texts = [
        figures.check("side walls apart", span_length(apart), DESIGN_RESET_SIDE_WALLS_APART_MM, 2),
        figures.check("off x", span_middle(apart) - center, 0.0, 2),
        figures.check("thick", span_length(side_wall), DESIGN_RESET_SIDE_WALL_MM, 1),
        figures.check("front stop", span_length(stop_across), DESIGN_RESET_FRONT_STOP_MM, 1),
        figures.check("off x", span_middle(stop_across) - center, 0.0, 2),
        figures.check("from the wall's inner face", inner - stop_south,
                      DESIGN_RESET_FRONT_STOP_DEPTH_MM, 1),
        figures.check("top z", stop_top, DESIGN_RESET_FRONT_STOP_TOP_Z_MM, 3),
    ]
    hole_texts = [
        figures.check("pin hole across", span_length(across), DESIGN_RESET_PIN_HOLE_MM, 1),
        figures.check("off x", span_middle(across) - center, 0.0, 2),
        figures.check("axis z", up[0] + radius, DESIGN_RESET_PIN_HOLE_AXIS_Z_MM, 3),
        f"top {up[1] - up[0] - radius:.3f} above the axis",
        figures.check("flat top", flat, DESIGN_RESET_PIN_HOLE_FLAT_MM, 2),
    ]
    wall_texts = [
        figures.check("back wall from the wall's inner face", in_front[1] - in_front[0],
                      DESIGN_RESET_BACK_WALL_DEPTH_MM, 1),
        figures.check("thick", span_length(wall), DESIGN_RESET_BACK_WALL_MM, 1),
        figures.check("top z", wall_top, DESIGN_RESET_BACK_WALL_TOP_Z_MM, 2),
    ] + notch_texts
    return [f"reset:      {', '.join(hole_texts)}", f"back wall:  {', '.join(wall_texts)}",
            f"socket:     {', '.join(socket_texts)}"]


def half_box(right, x_range, y_range, z_range):
    """A box given in the left half's frame, on the given half."""
    corners = [half_point((x, y), right) for x in x_range for y in y_range]
    low_x, high_x = min(x for x, _ in corners), max(x for x, _ in corners)
    low_y, high_y = min(y for _, y in corners), max(y for _, y in corners)
    return Part.makeBox(
        high_x - low_x,
        high_y - low_y,
        z_range[1] - z_range[0],
        App.Vector(low_x, low_y, z_range[0]),
    )


def half_prism(right, envelope):
    """An envelope's plan grown by the print's swelling, as a prism
    over its z range on the given half."""
    plan = layout.offset_polygon(layout.plan_corners(envelope), DESIGN_PRINT_SWELLING_PER_SIDE_MM)
    points = [vector(half_point(point, right), envelope.z_range[0]) for point in plan]
    face = Part.Face(Part.makePolygon(points + [points[0]]))
    return face.extrude(UP * (envelope.z_range[1] - envelope.z_range[0]))


def grown_by_swelling(value_range):
    return (value_range[0] - DESIGN_PRINT_SWELLING_PER_SIDE_MM,
            value_range[1] + DESIGN_PRINT_SWELLING_PER_SIDE_MM)


def measure_kept_clear(tray, right, fits, figures):
    """The PCB connector's zone above the floor, every wire room
    (layout.py's, the rooms DESIGN.md asks for behind every lead) and the
    nice!nano's socket strips with the rooms over them up to the PCB hold
    no plastic of the tray as printed: grown in plan by the swelling, they
    hold none as built."""
    x_range, y_range = (grown_by_swelling(span) for span in DESIGN_PCB_CONNECTOR_ZONE_MM)
    zone = half_box(right, x_range, y_range, (0.0, DESIGN_LEDGE_TOP_Z_MM)).common(tray).Volume

    def plastic_in(envelopes):
        return sum(half_prism(right, envelope).common(tray).Volume for envelope in envelopes)

    rooms = layout.wire_rooms(fits, right)
    strips = layout.nano_strip_envelopes(fits) + layout.nano_strip_rooms(fits)
    texts = [
        figures.check("plastic in the PCB connector's zone as printed, mm3", zone, 0.0, 3),
        figures.check(f"in the {len(rooms)} wire rooms as printed, mm3", plastic_in(rooms), 0.0,
                      3),
        figures.check("in the socket strips and the rooms over them as printed, mm3",
                      plastic_in(strips), 0.0, 3),
    ]
    return f"kept clear: {', '.join(texts)}"


def measure_mounts(tray, right, design, fits, figures):
    lines = [
        measure_usb_window(tray, right, design, figures),
        measure_usb_channel(tray, right, design, figures),
        measure_nano_north_block(tray, right, design, figures),
        measure_nano_clamp(tray, right, design, figures),
        measure_nano_walls(tray, right, design, figures),
        measure_nano_seat(tray, right, design, figures),
        measure_nano_strip_pockets(tray, right, design, figures),
        measure_nano_pry_slot(tray, right, design, figures),
    ]
    lines.extend(measure_power_switch(tray, right, figures))
    lines.extend(measure_reset_button(tray, right, figures))
    lines.append(measure_kept_clear(tray, right, fits, figures))
    return lines


def measure(tray, right, pin_hole_radius, design, mount_design, fits):
    """Print every measured figure against DESIGN.md's, stopping on any
    that is off."""
    figures = Figures()
    lines = [measure_outside(tray, figures)]
    lines.extend(measure_walls(tray, right, figures))
    lines.append(measure_floor(tray, right, figures))
    lines.append(measure_ledge(tray, right, figures))
    lines.extend(measure_shelves(tray, right, figures))
    lines.append(measure_block(tray, right, figures))
    lines.append(measure_standoffs(tray, right, figures))
    lines.append(measure_joint_face(tray, right, figures))
    lines.append(measure_joint_face_chamfer(tray, right, figures))
    lines.extend(measure_pin_holes(tray, right, pin_hole_radius, design, figures))
    lines.extend(measure_magnet_slots(tray, right, figures))
    lines.append(measure_parking_hole(tray, right, figures))
    lines.extend(measure_post_relief(tray, right, relief, figures)
                 for relief in DESIGN_POST_RELIEFS)
    lines.append(measure_socket_clearance(tray, right, figures))
    without_standoffs = tray_without_standoffs(tray, right)
    lines.append(measure_frame_wall_clearance(without_standoffs, right, figures))
    lines.append(measure_frame_tube_clearance(without_standoffs, right, figures))
    lines.extend(measure_mounts(tray, right, mount_design, fits, figures))
    for line in lines:
        print(line)
    figures.stop_on_problems()


# The joined check.


def design_slant_angle_degrees():
    (south_x, south_y), (north_x, north_y) = DESIGN_SLANT_ENDS_MM
    return math.degrees(math.atan2(south_x - north_x, north_y - south_y))


def joined_pair(left, right):
    """The left and right trays (each as exported) turned as DESIGN.md
    joins them: the left one clockwise and the right one anticlockwise
    by the slant's angle about their slant's south ends, so both slants
    run north, then the right one moved so its outer slant face lies on
    the left one's and the slants' south ends are level. Returns (left,
    right, the face's x)."""
    angle = design_slant_angle_degrees()
    left_south, _, _ = design_slant_frame(False)
    right_south, _, _ = design_slant_frame(True)
    left_turned = left.copy()
    left_turned.rotate(vector(left_south), UP, -angle)
    right_turned = right.copy()
    right_turned.rotate(vector(right_south), UP, angle)
    face_x = left_south[0] + DESIGN_JOINT_FACE_OUT_OF_SLANT_MM
    shift = App.Vector(
        face_x - (right_south[0] - DESIGN_JOINT_FACE_OUT_OF_SLANT_MM),
        left_south[1] - right_south[1],
        0.0,
    )
    right_turned.translate(shift)
    return left_turned, right_turned, face_x


def outermost_face_x(tray, sign):
    """The x of the planar face with outward normal (sign, 0, 0) lying
    farthest that way."""
    xs = []
    for face in tray.Faces:
        if not isinstance(face.Surface, Part.Plane):
            continue
        normal = face.normalAt(*face.Surface.parameter(face.CenterOfMass))
        if normal.x * sign > 1.0 - 1e-9:
            xs.append(face.Vertexes[0].Point.x)
    return max(xs) if sign > 0 else min(xs)


def pin_axes_along_x(tray, radius):
    """(y, z) of the pin holes' axes, running along x once joined."""
    centers = horizontal_cylinders(tray, radius, App.Vector(1.0, 0.0, 0.0))
    return sorted((center.y, center.z) for center in centers)


def joined_contact_problems(left_joined, right_joined, face_x):
    """(problems, overlap, apart) of the joined trays, which must touch
    without overlapping, both joint faces at face_x."""
    overlap = left_joined.common(right_joined).Volume
    apart = left_joined.distToShape(right_joined)[0]
    left_face = outermost_face_x(left_joined, 1.0)
    right_face = outermost_face_x(right_joined, -1.0)
    problems = []
    if overlap > JOINED_OVERLAP_TOLERANCE_MM3:
        problems.append(f"the joined trays overlap by {overlap:.4f} mm3")
    if apart > JOINED_TOLERANCE_MM:
        problems.append(f"the joined trays stand {apart:.6f} apart")
    if max(abs(left_face - face_x), abs(right_face - face_x)) > JOINED_TOLERANCE_MM:
        problems.append(
            f"the joint faces lie at x {left_face:.6f} and {right_face:.6f}, not {face_x:.6f}"
        )
    return problems, overlap, apart


def joined_pin_channels(left_joined, right_joined, face_x, radii, figures):
    """(problems, how far apart the pin holes' axes lie across the
    joint, the channels' text): each left hole coaxial with its right
    one, the two a channel at least the pin plus DESIGN.md's margin
    long."""
    left_axes = pin_axes_along_x(left_joined, radii[0])
    right_axes = pin_axes_along_x(right_joined, radii[1])
    if len(left_axes) != 2 or len(right_axes) != 2:
        raise SystemExit(f"error: joined: {len(left_axes)} and {len(right_axes)} pin holes found")
    axis_offset = max(math.dist(first, second) for first, second in zip(left_axes, right_axes))
    problems = []
    if axis_offset > SAME_PLACE_MM:
        problems.append(f"the pin holes' axes lie {axis_offset:.6f} apart across the joint")
    both = Part.makeCompound([left_joined, right_joined])
    channels = []
    for y, z in left_axes:
        low, high = run_through(both, App.Vector(face_x, y, z), App.Vector(1, 0, 0), False)
        channels.append(high - low)
    text = figures.at_least(
        "pin channels",
        min(channels),
        DESIGN_DOWEL_PIN_LENGTH_MM + DESIGN_PIN_CHANNEL_MARGIN_MM,
        1,
    )
    return problems, axis_offset, text


def joined_magnet_slots(left_joined, right_joined, face_x, figures):
    """(problems, how far apart the slots lie along the joint, the
    gap's text): each left slot facing its right one, DESIGN.md's gap
    between the opposing magnets."""
    slot_offset = 0.0
    gaps = []
    left_south, _, _ = design_slant_frame(False)
    slot_middle = DESIGN_MAGNET_SKIN_MM + DESIGN_MAGNET_SLOT_MM[1] / 2.0
    for along in DESIGN_MAGNET_ALONGS_MM:
        y = left_south[1] + along
        runs = []
        for side, tray in ((-1.0, left_joined), (1.0, right_joined)):
            point = App.Vector(face_x + side * slot_middle, y, LEDGE_PROBE_Z_MM)
            runs.append(
                (
                    run_through(tray, point, App.Vector(0, 1, 0), False),
                    run_through(tray, point, App.Vector(1, 0, 0), False),
                    point,
                )
            )
        (left_along, left_across, left_point), (right_along, right_across, right_point) = runs
        slot_offset = max(
            slot_offset,
            abs(left_along[0] - right_along[0]),
            abs(left_along[1] - right_along[1]),
        )
        gaps.append((right_point.x + right_across[0]) - (left_point.x + left_across[1]))
    text = figures.check(
        "between opposing magnet slots",
        max(gaps, key=lambda gap: abs(gap - DESIGN_MAGNETS_APART_JOINED_MM)),
        DESIGN_MAGNETS_APART_JOINED_MM,
        1,
    )
    problems = []
    if slot_offset > SAME_PLACE_MM:
        problems.append(f"the magnet slots lie {slot_offset:.6f} apart along the joint")
    return problems, slot_offset, text


def check_joined(left, right, left_radius, right_radius):
    """Join the trays and check them: no overlap, the faces touching,
    the pin holes coaxial in a channel longer than the pin, the magnet
    slots facing each other with DESIGN.md's gap. Returns the line to
    print."""
    left_joined, right_joined, face_x = joined_pair(left, right)
    figures = Figures()
    problems, overlap, apart = joined_contact_problems(left_joined, right_joined, face_x)
    pin_problems, axis_offset, channel_text = joined_pin_channels(
        left_joined, right_joined, face_x, (left_radius, right_radius), figures
    )
    slot_problems, slot_offset, gap_text = joined_magnet_slots(
        left_joined, right_joined, face_x, figures
    )
    problems.extend(pin_problems + slot_problems + figures.problems)
    if problems:
        raise SystemExit("error: joined:\n  " + "\n  ".join(problems))
    return (
        f"joined:     each half turned {design_slant_angle_degrees():.4f} degrees, the outer slant "
        f"faces both at x {face_x:.3f}: overlap {overlap:.6f} mm3, apart {apart:.6f}, pin hole "
        f"axes {axis_offset:.6f} apart, {channel_text}, magnet slots {slot_offset:.6f} apart "
        f"along the joint, {gap_text}"
    )


# The build.


def half_tray(right, pin_hole_diameter, fits=None):
    """(build, the tray on its half as exported)."""
    build = build_tray(right, pin_hole_diameter, fits)
    solid = mirror_for_right_half(build.solid) if right else build.solid
    return build, solid


def print_build(build):
    print(f"tray:       {'right' if build.right else 'left'} half, gap {layout.TRAY_GAP_MM}, wall "
          f"{layout.TRAY_WALL_MM}, floor {layout.TRAY_FLOOR_MM}, rim at z {layout.TRAY_RIM_Z_MM}, "
          f"volume {build.solid.Volume / 1000.0:.3f} cm3")
    print(f"corners:    every bend {build.corner_radius - layout.TRAY_WALL_MM:.2f} inside / "
          f"{build.corner_radius:.2f} outside, concentric")
    print(f"shelves:    under the backing's edges up to z {layout.BACKING_SHELF_TOP_Z_MM}, "
          f"{build.shelves:.3f} mm3 added, {len(build.shelf_notches)} notches for its screw heads")
    for label, removed in build.cuts:
        print(f"cut:        {label}, {removed:.3f} mm3")
    for label in build.skipped_cuts:
        print(f"skipped:    {label}, nothing left to remove")
    lead_in = f"{build.pin_hole_lead_in} lead-in" if build.pin_hole_lead_in else "no lead-in"
    print(f"pins:       holes {build.pin_hole_diameter} across "
          f"({'slip' if build.right else 'snug'} fit), {build.pin_hole_depth} deep, {lead_in}")
    fits = build.fits
    print(f"mounts:     fitted to a nice!nano {fits.nano_width} x {fits.nano_length} in a pocket "
          f"{fits.nano_pocket_fit} wider as printed, the clamp pressing it {fits.clamp_press}, the "
          f"bar {fits.bar_clearance} over its shell")
    for label, added in build.mounts:
        print(f"added:      {label}, {added:.3f} mm3")
    print(f"floor:      closed, its underside {build.bed_area:.3f} mm2, the void-free footprint's: "
          "no void reaches it")


def check_clamp_tab(build):
    """The clamp's tab, seated on the block, overlaps nothing of the tray
    and touches it, on the block's top. Returns the line to print."""
    tab = build_clamp_tab(build.fits)
    overlap = build.solid.common(tab).Volume
    apart = build.solid.distToShape(tab)[0]
    if overlap > JOINED_OVERLAP_TOLERANCE_MM3 or apart > JOINED_TOLERANCE_MM:
        raise SystemExit(f"error: the clamp's tab overlaps the tray by {overlap:.4f} mm3 and "
                         f"stands {apart:.6f} off it, expected seated on the block")
    return (f"tab:        seated on the clamp's block (tray_shape.py's tab): overlap with the tray "
            f"{overlap:.6f} mm3, touching it")


def main():
    arguments = parse_arguments(script_arguments(sys.argv))
    right = arguments.right
    fits = arguments.mount_fits()
    build, tray = half_tray(right, arguments.pin_hole_diameter, fits)
    print_build(build)
    if right:
        print(f"half:       right, mirrored across x = {layout.RIGHT_HALF_MIRROR_X_MM:.3f} (the "
              "lines above are its build in the left half's frame, the lines below the right "
              "half's)")
    else:
        print("half:       left")
    design = hole_design(right, arguments.pin_hole_diameter)
    measure(tray, right, build.pin_hole_diameter / 2.0, design, MountDesign(arguments), fits)
    print(check_clamp_tab(build))
    _other_build, other = half_tray(not right, None)
    left, right_tray = (other, tray) if right else (tray, other)
    left_diameter = layout.dowel_hole_diameter(False)
    right_diameter = layout.dowel_hole_diameter(True)
    if right:
        right_diameter = build.pin_hole_diameter
    else:
        left_diameter = build.pin_hole_diameter
    print(check_joined(left, right_tray, left_diameter / 2.0, right_diameter / 2.0))
    mesh = export_stl(tray, arguments.stl_file)
    check_closed_mesh(arguments.stl_file)
    print(f"wrote:      {arguments.stl_file} ({mesh.CountFacets} facets), floor on the bed, one "
          "closed manifold shell")


run_and_exit(main)
