"""Export the printable parts of a Raspberry Pi Camera Module 2 arm for
a stock Ender 3 V2 (STL files, each in its print orientation).

The arm stands on the printer base's right 4040 rail (the one running
front to back at bed level), in front of the right upright, behind the
user's Raspberry Pi mount (Printables 277420) near the rail's front
end. Nothing clamps it: two T-rails under its base slide in the rail's
two top slots, and the slots hold, from the upright forward, a spacer
rail each, the arm's base, the Pi mount and one or two shims each,
closed by the rail's stock end cap. The spacer rails start at the bolts
that hold the upright and stay below the rail's top face, so their
length sets where the arm stands. A post rises from the base between
the print head's reach and the back of the Pi's case, and a bar
against the camera case's back face carries the case from the post's
top forward over the Pi case, looking at the bed's center from the
front and to the right at one fixed angle.
The case is two shells around the camera board, closed by four M2
screws through the board's holes into heat-set inserts in the back
shell, and fixed to the arm by two M2 screws through ears on the back
shell into inserts in the arm's bar. The 15 pin ribbon leaves the
case's bottom through a socket that takes the end of a cable sock.

Runs headless under FreeCAD's console interpreter (see board_step.py
for the freecadcmd quirks that shape the invocation):

    freecadcmd model/camera-arm/scripts/export_camera_arm.py --pass <output directory>

and writes camera-arm.stl, camera-arm-spacer.stl, camera-arm-shim.stl,
camera-arm-case-back.stl and camera-arm-case-front.stl there, each
lying on z = 0 the way it prints. The spacer and shim
files hold one rail each, for one slot. It also prints the fits, the
clearances to the printer, the Pi and the cable, and what part of the
bed the camera sees over the Y travel.

Print orientations. The arm prints on its back: the base's back end on
the bed, the T-rails standing on it with their profile in the layer
plane, as the Pi mount prints them, and the post hanging over the bed
on the slicer's supports (the user prints it with supports). The
spacer rails lie on their undersides, the shims stand on an end.

Assembly: take off the rail's end cap, slide in the two spacer rails,
the arm, the Pi mount and the shims that fill the slots to the rail's
end, and put the cap back on. Close the case around the board and
screw it to the arm through the ears from the front, where a straight
driver up to 5 mm across passes the front shell.

Sources (downloads kept under work/research/):

- Raspberry Pi Camera Module V2.1 mechanical drawing (RPI-CAM-V2_1,
  2015-11-12), https://datasheets.raspberrypi.com/camera/
  camera-module-2-mechanical-drawing.pdf: the board is 25 x 23.862 mm
  with 2.0 mm corner radii and four 2.2 mm holes, 2 mm in from the
  side edges, one row 2 mm and one 14.5 mm from the edge away from the
  connector (12.5 x 21 mm apart). The 8.5 x 8.5 mm lens block sits
  centered across the board on the 14.5 mm row, the 20.8 mm wide
  ribbon connector takes the 5.5 mm next to the other edge. The
  drawing also gives 9.462 mm from that row to the connector edge,
  which with 14.5 mm makes 23.962, not 23.862: the 0.1 mm goes into
  the case's gap. It gives no thicknesses and does not say which
  side its components are on.
- Raspberry Pi documentation, camera hardware specification
  (github.com/raspberrypi/documentation, documentation/asciidoc/
  accessories/camera/hardware_specification.adoc): Camera Module 2 is
  "around 25 x 24 x 9 mm", 62.2 degrees horizontal and 48.8 degrees
  vertical field of view, 3.04 mm focal length, focus from about 10
  cm.
- Creality's Ender-3 V2 firmware configuration (github.com/
  CrealityOfficial/Ender-3V2, Marlin/Configuration.h): Z_MAX_POS 250.
- The user's Klipper configuration (homelab repository, roles/
  klipper_host/files/printer-config/): X and Y run 0 to 235
  (hardware.cfg, position_max 235) and safe_z_home homes at 117.5,
  117.5 (probe.cfg), so the print area here is the whole 235 mm plate
  and the Y travel 235.
- Creality's mechanical CAD of the Ender-3, the V2's predecessor
  (github.com/Creality3DPrinting/Ender-3, Ender-3 Mechanical/STP/
  Ender3.STEP and 4040 profile.step, PDF/4040 profile1-3.PDF). Creality
  publishes no V2 CAD there (CrealityOfficial/Ender-3V2 holds firmware
  only, the V2 download page firmware and the manual), so the printer
  numbers below are the Ender-3's, measured in FreeCAD. They agree with
  the user's description of the rail: 4040 profiles 290 mm long run
  front to back on both sides of the base. On that drawing the right
  upright (2040) stands centered on the rail, the bed plate (235 mm)
  sits 60.96 mm above the rail's top face with its right edge 7.3 mm
  short of the rail's inner side, and the nozzle is 63.7 mm in front of
  the upright's back face. The top slots are 20 mm apart; the end
  face's vertices in 4040 profile.step (work/research/downloads/
  creality-4040/) give each a 45 degree mouth chamfer through the whole
  1.8 mm lip, 9.6 mm wide at the top face and 6.0 mm at its bottom
  corner, the lip's underside there, a 10.42 mm cavity down to 3.8 mm,
  then a 45 degree taper to 6.02 mm at the 6.0 mm deep floor.
- The Ender-3 V2's assembly guides (not downloaded here): each upright
  is held by M5 x 45 screws from below through the base rail into the
  2040's center bores, so a 5.0 mm shank crosses each top slot under
  the upright's middle, 7.5 mm behind its front face. The spacer rails
  stop there. That is calculated, not measured.
- The user's Pi mount and case, Printables 277420 (work/research/
  downloads/printables-277420/: case_mount.stl and
  rpi4-hyperpixel-case.stl, sliced): the mount is 40 mm long, its face
  slopes 34 degrees down toward the front, it has a leg down the rail's
  outer side face, and its T-rails are the profile this arm's T-rails
  copy, which fits the user's rail snugly. The case is 104 x 64 x 32 mm,
  tilted on the mount's face with its 104 across the rail.
- The user's measurements on the printer: the Pi mount's back end 95 mm
  in front of the upright's front face, the rail's top face free for
  136 to 137 mm in front of it (hard to measure), the Pi case's rearmost
  point about 92 mm in front of it (the STLs give 91.1) and its left
  side in line with the rail's left side, the print head's reach (fan
  casing included) 80 mm in front of the upright (taken as from its
  front face, unconfirmed), over the whole rail and past its outer
  side, its lowest point (nozzle excluded) about 1 cm over the Pi
  case's top.

Assumed without a source, to be measured on the real parts: the board
1.0 mm thick, the case's room for components 3.0 mm in front of the
board (the lens block passes through a window) and 4.0 mm behind it;
the ribbon 16 mm wide (15 contacts at 1 mm pitch); the sock's end
about 8 to 10 mm across round, or flattened around the flat ribbon. The
spacer rails' stop at the upright's bolts (see above): if they stop
elsewhere, the arm and the Pi mount shift along the rail by the
difference, and a shift toward the upright eats into the post's 3 mm
to the print head's reach.

Frames: the printer frame has x to the right (seen from the front), y
toward the back and z up, its origin on the right rail's top face, on
the rail's center line, level with the right upright's back face. The
upright's front face is at y = -20; positions along the rail are given
as the distance in front of that face (y = -20 - distance), heights as
z, the height above the rail's top face, and the side profiles below
as (distance in front of the upright, height) pairs extruded across x.
The case frame has u along the board's 25 mm side, v along its 23.862
mm side from the connector edge, w through the board toward the lens,
the board's back face at w = 0.
"""

import math
import os
import sys

# The STL export and the freecadcmd scaffolding live in kbdkid4's board_step.py.
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, "kbdkid4", "scripts"))

import FreeCAD as App
import Part

from board_step import check_closed_mesh, export_stl, run_and_exit, script_arguments

# Camera Module 2, from the mechanical drawing, in the case frame.
BOARD_WIDTH_MM = 25.0  # along u
BOARD_HEIGHT_MM = 23.862  # along v, connector edge at v = 0
BOARD_CORNER_RADIUS_MM = 2.0
BOARD_HOLE_DIAMETER_MM = 2.2
BOARD_HOLE_CENTERS_MM = ((2.0, 21.862), (23.0, 21.862), (2.0, 9.362), (23.0, 9.362))
LENS_CENTER_MM = (12.5, 9.362)
LENS_BLOCK_SIDE_MM = 8.5
CONNECTOR_WIDTH_MM = 20.8
CONNECTOR_DEPTH_MM = 5.5

# Assumed: not in the drawing. The lens block and connector heights only
# feed the fit check (a part model of the board inside the case).
BOARD_THICKNESS_MM = 1.0
LENS_BLOCK_HEIGHT_MM = 5.5  # above the board's front
CONNECTOR_HEIGHT_MM = 2.5  # below the board's back
RIBBON_WIDTH_MM = 16.0

HORIZONTAL_FIELD_OF_VIEW_DEGREES = 62.2  # along u
VERTICAL_FIELD_OF_VIEW_DEGREES = 48.8  # along v

# The printer, in the printer frame, from the Ender-3 CAD, the V2
# firmware and the user's Klipper configuration (see the module
# docstring).
RAIL_HALF_WIDTH_MM = 20.0
RAIL_SLOT_CENTERS_X_MM = (-10.0, 10.0)
# A top slot, from 4040 profile.step. The mouth chamfer runs at 45
# degrees from SLOT_NECK_WIDTH_MM at its bottom corner, so the mouth is
# 6.0 + 2 x 1.8 = 9.6 mm wide at the top face. Its depth is the one
# figure the user has not confirmed on the rail.
SLOT_MOUTH_CHAMFER_DEPTH_MM = 1.8
SLOT_NECK_WIDTH_MM = 6.0  # at the chamfer's bottom corner
SLOT_LIP_THICKNESS_MM = 1.8  # the lips' undersides
SLOT_INNER_WIDTH_MM = 10.42
SLOT_TAPER_START_DEPTH_MM = 3.8  # below the rail's face, 45 degrees from there
SLOT_DEPTH_MM = 6.0
UPRIGHT_BOX_MM = ((-20.0, 20.0), (-20.0, 0.0), (0.0, 400.0))
# The M5 screws through the base rail into the upright's center bores,
# in the middle of the upright's depth along the rail.
UPRIGHT_BOLT_DIAMETER_MM = 5.0
# The X gantry's right end (wheel plate, wheels, belt tensioner) at its
# lowest, nozzle on the bed; it sweeps up from there.
GANTRY_RIGHT_END_BOX_MM = ((-63.4, 61.56), (-49.85, -4.9), (52.46, 147.56))
X_BEAM_BOX_MM = ((-308.09, 36.91), (-46.85, -26.85), (90.0, 110.0))  # at its lowest
BED_PLATE_X_MM = (-262.3, -27.3)
BED_PLATE_SIZE_MM = 235.0
BED_TOP_Z_MM = 60.96
BED_PLATE_THICKNESS_MM = 3.0
LEVELLING_KNOB_INSET_MM = 32.5  # knob centers from the plate's edges
LEVELLING_KNOB_RADIUS_MM = 30.0  # the CAD's bounding box, the knob is smaller
LEVELLING_KNOB_Z_MM = (27.5, 38.0)
NOZZLE_Y_MM = -63.7
PRINT_AREA_SIZE_MM = 235.0  # centered on the plate: Klipper's X and Y run 0 to 235
Y_TRAVEL_MM = 235.0
MAXIMUM_PRINT_HEIGHT_MM = 250.0
BUILD_VOLUME_MM = (220.0, 220.0, 250.0)  # for the arm's own print

# The user's figures along the rail, in front of the upright's front
# face. The print head's reach, fan casing included, runs over the
# whole rail and past its outer side by an amount the user did not
# give: HEAD_REACH_RIGHT_X_MM reaches past everything of the arm. Its
# lowest point (nozzle excluded) is about 1 cm over the Pi case's top,
# about 71 mm up; the keep-out starts lower, at the bed top.
RAIL_FREE_TOP_FACE_MM = (136.0, 137.0)  # to the rail's front end
HEAD_REACH_MM = 80.0
HEAD_REACH_RIGHT_X_MM = 100.0
HEAD_CLEARANCE_MM = 3.0

# The Pi mount and its case, from the Printables 277420 STLs placed by
# the user's measurements, as side profiles across x. The mount's back
# end is at 95, the user's figure. Its leg runs down the rail's outer
# side face, braced out to the mount's outer end: (x, height) across
# the mount's length.
PI_MOUNT_SIDE_PROFILE_MM = ((95.0, 0.0), (95.0, 30.0), (96.5, 30.6), (135.0, 4.6), (135.0, 0.0))
PI_MOUNT_X_MM = (-20.0, 60.0)
PI_MOUNT_LEG_PROFILE_MM = ((20.0, -37.0), (23.0, -37.0), (60.0, 0.0), (20.0, 0.0))
# The case's corners: its rearmost, the top of its back face, the front
# of its top face, the bottom front.
PI_CASE_SIDE_PROFILE_MM = ((91.1, 34.4), (109.0, 61.0), (162.1, 25.2), (144.2, -1.4))
PI_CASE_X_MM = (-19.6, 84.4)
PI_CASE_CLEARANCE_MM = 2.0

# The rail parts: the arm's base and the spacer and shim rails share
# the T-rail profile of the user's Pi mount (case_mount.stl, sliced),
# which fits the user's rail snugly: its right half as (x from the
# slot's center, z below the rail's top face), mirrored. It is copied,
# not drawn by the swelling rules below. The spacer and shim rails are
# cut off at the mouth chamfer's bottom corner, so nothing of them
# reaches into the chamfer or above the top face. The spacers run from
# the upright's bolts to the arm's base; the shims go between the Pi
# mount and the end cap.
T_RAIL_HALF_PROFILE_MM = (
    (2.5, 0.0), (2.5, -2.1), (4.9, -2.1), (4.9, -3.164), (4.85, -3.47), (4.77, -3.65),
    (4.58, -3.9), (3.04, -5.33), (2.75, -5.52), (2.36, -5.6),
)
SPACER_LENGTH_MM = 62.5
SHIM_LENGTH_MM = 1.0
ARM_BASE_LENGTH_MM = 40.0
ARM_BASE_PLATE_HEIGHT_MM = 8.0  # at most: the Pi case overhangs the base

# Print fits, by kbdkid4's conventions: a printed part swells about 0.2
# mm per side (export_pcb.py's pull_in), so holes are drawn 0.4 mm over
# size and screw clearance holes another 0.2 mm for play; the M2
# heat-set insert bore is the tray's (export_tray.py's
# DEFAULT_STANDOFF_HOLE_DIAMETER_MM, standoff 5.8 mm across).
PRINT_SWELLING_PER_SIDE_MM = 0.2
INSERT_BORE_DIAMETER_MM = 3.2
INSERT_STANDOFF_DIAMETER_MM = 5.8
M2_CLEARANCE_DIAMETER_MM = 2.6
M2_HEAD_COUNTERBORE_DIAMETER_MM = 4.6  # 3.8 mm socket head
M2_HEAD_COUNTERBORE_DEPTH_MM = 2.0

# The camera's pose: the lens at LENS_X_MM, LENS_IN_FRONT_OF_UPRIGHT_MM
# along the rail and LENS_HEIGHT_SHARE_OF_FIRST_ARM of the first arm's
# lens height (the user: "shrink the height of the arm by 1/3"), aimed
# at the bed's center at mid travel, the image's long side horizontal.
# The first arm's pose stays for that height and the comparison: its
# optical axis 225 degrees from +x and 40 degrees down, its bar
# FIRST_ARM_BAR_THICKNESS_MM thick with the back face's center at
# FIRST_ARM_HEAD_BAR_BACK_CENTER_MM, its bracket rising
# FIRST_ARM_BRACKET_RISE_MM over that to its highest point.
LENS_X_MM = -8.0
LENS_IN_FRONT_OF_UPRIGHT_MM = 105.0
LENS_HEIGHT_SHARE_OF_FIRST_ARM = 2.0 / 3.0
FIRST_ARM_CAMERA_YAW_DEGREES = 225.0
FIRST_ARM_CAMERA_PITCH_DEGREES = 40.0
FIRST_ARM_BAR_THICKNESS_MM = 7.0
FIRST_ARM_HEAD_BAR_BACK_CENTER_MM = (3.0, 90.0, 198.0)
FIRST_ARM_BRACKET_RISE_MM = 8.0

# The case. The board sits CASE_GAP_MM inside the walls on four
# standoffs bored for the inserts; bosses on the front shell press it
# down, reaching FRONT_BOSS_PRESS_MM past the assumed board thickness,
# so the shells close on the board, not on each other: the seam stays
# that far open on a 1.0 mm board.
CASE_GAP_MM = 0.4
CASE_WALL_MM = 1.6
FRONT_CAVITY_MM = 3.0  # above the board's front face
BACK_CAVITY_MM = 4.0  # below the board's back face
INSERT_BORE_DEPTH_MM = 5.0  # from the board's back face
FRONT_BOSS_DIAMETER_MM = 6.0
FRONT_BOSS_PRESS_MM = 0.2
LENS_WINDOW_SIDE_MM = LENS_BLOCK_SIDE_MM + 2.0 * (PRINT_SWELLING_PER_SIDE_MM + 0.3)
# The ribbon leaves through a slot in the bottom wall into a socket for
# the sock's end: an 18.4 x 8.8 mm stadium, SOCK_SOCKET_DEPTH_MM deep,
# which takes a round sock end up to about 8.4 mm squeezed to an oval
# (a 10 mm sock's 31 mm perimeter fits it easily) or a sock flattened
# around the flat ribbon. The narrower ribbon slot is the sock's stop.
RIBBON_SLOT_WIDTH_MM = RIBBON_WIDTH_MM + 1.4
RIBBON_SLOT_W_MM = (-BACK_CAVITY_MM, BOARD_THICKNESS_MM)
SOCK_SOCKET_WIDTH_MM = 18.4
SOCK_SOCKET_HEIGHT_MM = 8.8
SOCK_SOCKET_DEPTH_MM = 8.0
SOCK_SOCKET_WALL_MM = 1.2
# The sock's path, which the arm keeps clear of: CABLE_CORRIDOR_WIDTH_MM
# across, from the socket's mouth along the case's -v for
# CABLE_CORRIDOR_RUN_MM, then straight down to the Pi case's top.
CABLE_CORRIDOR_WIDTH_MM = 12.0
CABLE_CORRIDOR_RUN_MM = 15.0
CABLE_CLEARANCE_MM = 2.0
# Ears on the back shell for the two screws into the arm, beyond the
# front shell's sides, so the screws go in from the front.
EAR_CENTERS_U_MM = (-4.8, BOARD_WIDTH_MM + 4.8)
EAR_RADIUS_MM = 3.6
EAR_THICKNESS_MM = 3.0
EAR_SCREW_DRIVER_DIAMETER_MM = 5.0  # the shaft that must pass the front shell's side
# The arm's bar, which carries the case on its back face and takes the
# ear screws in inserts BAR_INSERT_DEPTH_MM deep: BAR_THICKNESS_MM
# thick behind the case's back face, from BAR_DROP_MM below the ears'
# centers to BAR_RISE_MM above them, from BAR_REACH_BEYOND_EARS_MM
# beyond the +u ear to BAR_REACH_INTO_POST_MM beyond the -u one, which
# puts its -u end inside the post.
BAR_REACH_BEYOND_EARS_MM = 4.0
BAR_REACH_INTO_POST_MM = 9.0
BAR_RISE_MM = 4.0
BAR_DROP_MM = 10.0
BAR_THICKNESS_MM = 15.0
BAR_INSERT_DEPTH_MM = 5.5

# The arm, in the printer frame, its side profiles in distances in
# front of the upright and heights. The post's back face stands
# HEAD_CLEARANCE_MM off the head's reach. Its front face stands
# POST_CASE_GAP_MM off the Pi case's rearmost corner, leans forward
# along the case's back face at that gap and stands straight again at
# POST_FRONT_MM, short of the cable's corridor. Across x it spans
# POST_X_MM: left of POST_SPLIT_X_MM it stops at POST_LEFT_TOP_MM, under
# the camera's socket and out of its view, except behind the case's
# back face, where it runs up to POST_TOP_MM as it does right of the
# split, past the bar's -u end.
POST_CASE_GAP_MM = 2.1  # PI_CASE_CLEARANCE_MM and 0.1 to spare
POST_FRONT_MM = 101.5
POST_X_MM = (-20.0, 36.0)
POST_SPLIT_X_MM = 18.0
POST_LEFT_TOP_MM = 95.0
POST_TOP_MM = 140.0

# Checks.
OVERHANG_NORMAL_LIMIT = -0.7072  # a face pointing down more than 45 degrees
COVERAGE_GRID = 21  # bed samples per side
COVERAGE_TRAVEL_STEPS = 12
CUT_EXTRA_MM = 1.0
CONTACT_VOLUME_LIMIT_MM3 = 0.01
CLEARANCE_TOLERANCE_MM = 1e-6
VIEW_CHECK_DEPTH_MM = (1.0, 300.0)  # the field of view the arm stays out of, from the lens

USAGE = """\
usage: freecadcmd model/camera-arm/scripts/export_camera_arm.py --pass <output directory>\
"""

PART_FILE_NAMES = {
    "arm": "camera-arm.stl",
    "spacer": "camera-arm-spacer.stl",
    "shim": "camera-arm-shim.stl",
    "case_back": "camera-arm-case-back.stl",
    "case_front": "camera-arm-case-front.stl",
}


# Vectors as plain tuples, for the pure geometry.

def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def scale(a, factor):
    return tuple(x * factor for x in a)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def normalized(a):
    return scale(a, 1.0 / math.sqrt(dot(a, a)))


def along_axes(axes, coordinates):
    """The vector with these coordinates along the three axes."""
    return add(scale(axes[0], coordinates[0]), add(scale(axes[1], coordinates[1]), scale(axes[2], coordinates[2])))


# Positions along the rail.

def y_in_front_of_upright(distance):
    """The printer frame's y that far in front of the upright's front face."""
    return UPRIGHT_BOX_MM[1][0] - distance


def distance_in_front_of_upright(y):
    return UPRIGHT_BOX_MM[1][0] - y


def rail_y_range(distance_range):
    """The y range of a stretch of the rail given in distances in front of the upright."""
    return y_in_front_of_upright(distance_range[1]), y_in_front_of_upright(distance_range[0])


def upright_bolt_front():
    """Where the shank of the bolt under the upright's middle starts, in
    front of the upright's front face (negative: under the upright)."""
    axis_y = (UPRIGHT_BOX_MM[1][0] + UPRIGHT_BOX_MM[1][1]) / 2.0
    return distance_in_front_of_upright(axis_y - UPRIGHT_BOLT_DIAMETER_MM / 2.0)


def spacer_range():
    bolt = upright_bolt_front()
    return bolt, bolt + SPACER_LENGTH_MM


def arm_base_range():
    back = spacer_range()[1]
    return back, back + ARM_BASE_LENGTH_MM


def pi_mount_range():
    return PI_MOUNT_SIDE_PROFILE_MM[0][0], PI_MOUNT_SIDE_PROFILE_MM[-1][0]


def shim_range():
    front_of_mount = pi_mount_range()[1]
    return front_of_mount, front_of_mount + SHIM_LENGTH_MM


def t_rail_depth():
    return -min(z for _, z in T_RAIL_HALF_PROFILE_MM)


# The camera's pose.

def camera_axes(yaw_degrees, pitch_degrees):
    """(forward, right, up) of a level camera with that yaw and pitch."""
    yaw = math.radians(yaw_degrees)
    pitch = math.radians(pitch_degrees)
    forward = (math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), -math.sin(pitch))
    right = normalized((forward[1], -forward[0], 0.0))
    return forward, right, cross(right, forward)


def case_axes_for(yaw_degrees, pitch_degrees):
    """The case frame's u, v, w in the printer frame: u runs to the
    camera's left, which keeps the frame right handed."""
    forward, right, up = camera_axes(yaw_degrees, pitch_degrees)
    return scale(right, -1.0), up, forward


def case_outline_center_v():
    return BOARD_HEIGHT_MM / 2.0


def first_arm_bar_back_center_in_case():
    return (BOARD_WIDTH_MM / 2.0, case_outline_center_v(), case_back_w() - FIRST_ARM_BAR_THICKNESS_MM)


def case_back_w():
    return -BACK_CAVITY_MM - CASE_WALL_MM


def case_front_w():
    return BOARD_THICKNESS_MM + FRONT_CAVITY_MM + CASE_WALL_MM


def lens_in_case():
    """The lens window's center on the case's front face."""
    return (LENS_CENTER_MM[0], LENS_CENTER_MM[1], case_front_w())


def first_arm_lens():
    """The first arm's lens in the printer frame, from its pose."""
    axes = case_axes_for(FIRST_ARM_CAMERA_YAW_DEGREES, FIRST_ARM_CAMERA_PITCH_DEGREES)
    offset = subtract(lens_in_case(), first_arm_bar_back_center_in_case())
    return add(FIRST_ARM_HEAD_BAR_BACK_CENTER_MM, along_axes(axes, offset))


def first_arm_top():
    return FIRST_ARM_HEAD_BAR_BACK_CENTER_MM[2] + FIRST_ARM_BRACKET_RISE_MM


def lens_position():
    height = LENS_HEIGHT_SHARE_OF_FIRST_ARM * first_arm_lens()[2]
    return (LENS_X_MM, y_in_front_of_upright(LENS_IN_FRONT_OF_UPRIGHT_MM), height)


def camera_target():
    """The bed's center at mid travel, which is under the nozzle."""
    return (BED_PLATE_X_MM[1] - BED_PLATE_SIZE_MM / 2.0, NOZZLE_Y_MM, BED_TOP_Z_MM)


def camera_yaw_and_pitch():
    delta = subtract(camera_target(), lens_position())
    yaw = math.degrees(math.atan2(delta[1], delta[0]))
    pitch = math.degrees(math.atan2(-delta[2], math.hypot(delta[0], delta[1])))
    return yaw, pitch


def case_axes():
    return case_axes_for(*camera_yaw_and_pitch())


def case_to_printer(point):
    """A case frame point in the printer frame."""
    return add(lens_position(), along_axes(case_axes(), subtract(point, lens_in_case())))


def matrix_from_axes(x_axis, y_axis, z_axis, origin):
    """The matrix taking a frame with these axes and origin to its parent."""
    return App.Matrix(
        x_axis[0], y_axis[0], z_axis[0], origin[0],
        x_axis[1], y_axis[1], z_axis[1], origin[1],
        x_axis[2], y_axis[2], z_axis[2], origin[2],
        0.0, 0.0, 0.0, 1.0,
    )


def case_matrix(front_offset_w=0.0):
    u_axis, v_axis, w_axis = case_axes()
    return matrix_from_axes(u_axis, v_axis, w_axis, case_to_printer((0.0, 0.0, front_offset_w)))


# Shape helpers.

def vector(point):
    return App.Vector(*point)


def box_between(x_range, y_range, z_range):
    return Part.makeBox(
        x_range[1] - x_range[0], y_range[1] - y_range[0], z_range[1] - z_range[0],
        App.Vector(x_range[0], y_range[0], z_range[0]),
    )


def edges_along_z(shape):
    edges = []
    for edge in shape.Edges:
        delta = edge.Vertexes[-1].Point.sub(edge.Vertexes[0].Point)
        if abs(delta.x) < 1e-7 and abs(delta.y) < 1e-7 and abs(delta.z) > 1e-7:
            edges.append(edge)
    return edges


def rounded_box(x_range, y_range, z_range, radius):
    """A box with its edges along z rounded."""
    solid = box_between(x_range, y_range, z_range)
    return solid.makeFillet(radius, edges_along_z(solid))


def cylinder_z(center, radius, z_range):
    return Part.makeCylinder(
        radius, z_range[1] - z_range[0], App.Vector(center[0], center[1], z_range[0])
    )


def prism_from_polygon(points, direction):
    """Points of a closed planar polygon, extruded along direction."""
    wire = Part.makePolygon([vector(point) for point in points] + [vector(points[0])])
    return Part.Face(wire).extrude(vector(direction))


def side_profile_prism(points, x_range):
    """A (distance in front of the upright, height) polygon extruded across x."""
    return prism_from_polygon(
        [(x_range[0], y_in_front_of_upright(distance), height) for distance, height in points],
        (x_range[1] - x_range[0], 0.0, 0.0),
    )


def cross_section_prism(outline, distance_range):
    """An (x, z) outline across the rail extruded along it over that stretch."""
    y_back = y_in_front_of_upright(distance_range[0])
    return prism_from_polygon(
        [(x, y_back, z) for x, z in outline], (0.0, -(distance_range[1] - distance_range[0]), 0.0)
    )


def distinct_points(points):
    """The points without repeats of the one before (zero length edges)."""
    kept = []
    for point in points:
        if not kept or max(abs(a - b) for a, b in zip(point, kept[-1])) > 1e-9:
            kept.append(point)
    return kept


def mirrored_outline(slot_x, half):
    """A half outline (x from the slot's center) and its mirror image, as one outline."""
    return [(slot_x + x, z) for x, z in half] + [(slot_x - x, z) for x, z in reversed(half)]


def single_solid(shape):
    shape = shape.removeSplitter()
    if len(shape.Solids) != 1:
        raise SystemExit(f"error: expected one solid, got {len(shape.Solids)}")
    return shape.Solids[0]


# The rail and the rail parts, in the printer frame.

def slot_outline(slot_x):
    """A top slot's open cross-section as (x, z), from just above the top
    face: the mouth chamfer, the lips' undersides, the cavity and the 45
    degree taper to the floor."""
    neck = SLOT_NECK_WIDTH_MM / 2.0
    inner = SLOT_INNER_WIDTH_MM / 2.0
    floor = inner - (SLOT_DEPTH_MM - SLOT_TAPER_START_DEPTH_MM)
    mouth = neck + SLOT_MOUTH_CHAMFER_DEPTH_MM
    half = [
        (mouth + CUT_EXTRA_MM, CUT_EXTRA_MM), (neck, -SLOT_MOUTH_CHAMFER_DEPTH_MM),
        (neck, -SLOT_LIP_THICKNESS_MM), (inner, -SLOT_LIP_THICKNESS_MM),
        (inner, -SLOT_TAPER_START_DEPTH_MM), (floor, -SLOT_DEPTH_MM),
    ]
    return distinct_points(mirrored_outline(slot_x, half))


def rail_top_metal(distance_range):
    """The rail's top down to 2 mm below its slots' floor, slots cut, for the fit checks."""
    block = box_between(
        (-RAIL_HALF_WIDTH_MM, RAIL_HALF_WIDTH_MM), rail_y_range(distance_range), (-SLOT_DEPTH_MM - 2.0, 0.0)
    )
    longer = (distance_range[0] - CUT_EXTRA_MM, distance_range[1] + CUT_EXTRA_MM)
    slots = [cross_section_prism(slot_outline(slot_x), longer) for slot_x in RAIL_SLOT_CENTERS_X_MM]
    return block.cut(Part.makeCompound(slots))


def t_rail(slot_x, distance_range):
    return cross_section_prism(mirrored_outline(slot_x, T_RAIL_HALF_PROFILE_MM), distance_range)


def build_rail_part(distance_range):
    """One spacer or shim rail in the outer slot, cut off at the mouth
    chamfer's bottom corner."""
    slot_x = RAIL_SLOT_CENTERS_X_MM[1]
    below_chamfer = box_between(
        (slot_x - RAIL_HALF_WIDTH_MM / 2.0, slot_x + RAIL_HALF_WIDTH_MM / 2.0),
        rail_y_range((distance_range[0] - CUT_EXTRA_MM, distance_range[1] + CUT_EXTRA_MM)),
        (-SLOT_DEPTH_MM - CUT_EXTRA_MM, -SLOT_MOUTH_CHAMFER_DEPTH_MM),
    )
    return single_solid(t_rail(slot_x, distance_range).common(below_chamfer))


# The case, in the case frame.

def case_outline_prism(offset, w_range):
    return rounded_box(
        (-offset, BOARD_WIDTH_MM + offset), (-offset, BOARD_HEIGHT_MM + offset), w_range,
        BOARD_CORNER_RADIUS_MM + offset,
    )


def outer_offset():
    return CASE_GAP_MM + CASE_WALL_MM


def sock_socket_box(w_range):
    """The socket's outside below the case's bottom wall, for one shell."""
    half_width = SOCK_SOCKET_WIDTH_MM / 2.0 + SOCK_SOCKET_WALL_MM
    center_u = BOARD_WIDTH_MM / 2.0
    bottom = -outer_offset() - SOCK_SOCKET_DEPTH_MM
    return box_between((center_u - half_width, center_u + half_width), (bottom, -CASE_GAP_MM), w_range)


def sock_socket_bore():
    """The stadium the sock's end goes into, along v up to the wall."""
    radius = SOCK_SOCKET_HEIGHT_MM / 2.0
    straight = SOCK_SOCKET_WIDTH_MM / 2.0 - radius
    center_u = BOARD_WIDTH_MM / 2.0
    bottom = -outer_offset() - SOCK_SOCKET_DEPTH_MM - CUT_EXTRA_MM
    length = SOCK_SOCKET_DEPTH_MM + CUT_EXTRA_MM
    middle = box_between((center_u - straight, center_u + straight), (bottom, bottom + length), (-radius, radius))
    ends = [
        Part.makeCylinder(radius, length, App.Vector(center_u + side * straight, bottom, 0.0), App.Vector(0, 1, 0))
        for side in (-1.0, 1.0)
    ]
    return middle.fuse(ends)


def sock_socket_mouth():
    """The center of the socket's open end, on the seam."""
    return (BOARD_WIDTH_MM / 2.0, -outer_offset() - SOCK_SOCKET_DEPTH_MM, 0.0)


def ribbon_slot():
    center_u = BOARD_WIDTH_MM / 2.0
    half_width = RIBBON_SLOT_WIDTH_MM / 2.0
    return box_between(
        (center_u - half_width, center_u + half_width),
        (-outer_offset() - CUT_EXTRA_MM, -CASE_GAP_MM + CUT_EXTRA_MM),
        RIBBON_SLOT_W_MM,
    )


def ears():
    """The two ears, from inside the back shell's side walls outward."""
    v = case_outline_center_v()
    w_range = (case_back_w(), case_back_w() + EAR_THICKNESS_MM)
    shapes = []
    for center_u in EAR_CENTERS_U_MM:
        wall_u = -CASE_GAP_MM if center_u < 0 else BOARD_WIDTH_MM + CASE_GAP_MM
        u_range = (min(center_u, wall_u), max(center_u, wall_u))
        tab = box_between(u_range, (v - EAR_RADIUS_MM, v + EAR_RADIUS_MM), w_range)
        shapes.append(tab.fuse(cylinder_z((center_u, v), EAR_RADIUS_MM, w_range)))
    return shapes


def ear_holes():
    v = case_outline_center_v()
    w_range = (case_back_w() - CUT_EXTRA_MM, case_back_w() + EAR_THICKNESS_MM + CUT_EXTRA_MM)
    return [cylinder_z((center_u, v), M2_CLEARANCE_DIAMETER_MM / 2.0, w_range) for center_u in EAR_CENTERS_U_MM]


def build_case_back():
    """Floor, walls up to the seam at w = 0 (the board's back face),
    four standoffs with insert bores, the ears and the socket's back half."""
    back = case_back_w()
    shell = case_outline_prism(outer_offset(), (back, 0.0))
    shell = shell.fuse([sock_socket_box((back, 0.0))] + ears())
    standoffs = [
        cylinder_z(center, INSERT_STANDOFF_DIAMETER_MM / 2.0, (-BACK_CAVITY_MM, 0.0))
        for center in BOARD_HOLE_CENTERS_MM
    ]
    cavity = case_outline_prism(CASE_GAP_MM, (-BACK_CAVITY_MM, CUT_EXTRA_MM)).cut(standoffs)
    bores = [
        cylinder_z(center, INSERT_BORE_DIAMETER_MM / 2.0, (-INSERT_BORE_DEPTH_MM, CUT_EXTRA_MM))
        for center in BOARD_HOLE_CENTERS_MM
    ]
    cutters = [cavity, ribbon_slot(), sock_socket_bore()] + bores + ear_holes()
    return single_solid(shell.cut(Part.makeCompound(cutters)))


def build_case_front():
    """Walls from the seam, the front plate with the lens window, the
    bosses that press the board, counterbored screw holes and the
    socket's front half."""
    front = case_front_w()
    ceiling = BOARD_THICKNESS_MM + FRONT_CAVITY_MM
    boss_bottom = BOARD_THICKNESS_MM - FRONT_BOSS_PRESS_MM
    shell = case_outline_prism(outer_offset(), (0.0, front)).fuse(sock_socket_box((0.0, front)))
    bosses = [
        cylinder_z(center, FRONT_BOSS_DIAMETER_MM / 2.0, (boss_bottom, ceiling + CUT_EXTRA_MM))
        for center in BOARD_HOLE_CENTERS_MM
    ]
    cavity = case_outline_prism(CASE_GAP_MM, (-CUT_EXTRA_MM, ceiling)).cut(bosses)
    holes = [
        cylinder_z(center, M2_CLEARANCE_DIAMETER_MM / 2.0, (boss_bottom - CUT_EXTRA_MM, front + CUT_EXTRA_MM))
        for center in BOARD_HOLE_CENTERS_MM
    ]
    counterbores = [
        cylinder_z(center, M2_HEAD_COUNTERBORE_DIAMETER_MM / 2.0,
                   (front - M2_HEAD_COUNTERBORE_DEPTH_MM, front + CUT_EXTRA_MM))
        for center in BOARD_HOLE_CENTERS_MM
    ]
    half_window = LENS_WINDOW_SIDE_MM / 2.0
    window = box_between(
        (LENS_CENTER_MM[0] - half_window, LENS_CENTER_MM[0] + half_window),
        (LENS_CENTER_MM[1] - half_window, LENS_CENTER_MM[1] + half_window),
        (ceiling - CUT_EXTRA_MM, front + CUT_EXTRA_MM),
    )
    cutters = [cavity, window, ribbon_slot(), sock_socket_bore()] + holes + counterbores
    return single_solid(shell.cut(Part.makeCompound(cutters)))


def board_model():
    """The camera board as drawn, with the assumed heights: the board,
    the lens block in front, the connector behind."""
    board = rounded_box((0.0, BOARD_WIDTH_MM), (0.0, BOARD_HEIGHT_MM), (0.0, BOARD_THICKNESS_MM),
                        BOARD_CORNER_RADIUS_MM)
    holes = [cylinder_z(center, BOARD_HOLE_DIAMETER_MM / 2.0, (-1.0, 2.0)) for center in BOARD_HOLE_CENTERS_MM]
    half_block = LENS_BLOCK_SIDE_MM / 2.0
    lens_block = box_between(
        (LENS_CENTER_MM[0] - half_block, LENS_CENTER_MM[0] + half_block),
        (LENS_CENTER_MM[1] - half_block, LENS_CENTER_MM[1] + half_block),
        (BOARD_THICKNESS_MM, BOARD_THICKNESS_MM + LENS_BLOCK_HEIGHT_MM),
    )
    half_connector = CONNECTOR_WIDTH_MM / 2.0
    connector = box_between(
        (BOARD_WIDTH_MM / 2.0 - half_connector, BOARD_WIDTH_MM / 2.0 + half_connector),
        (0.0, CONNECTOR_DEPTH_MM), (-CONNECTOR_HEIGHT_MM, 0.0),
    )
    return board.cut(holes).fuse([lens_block, connector])


def bar_in_case_frame():
    """The arm's bar behind the case, and its insert bores."""
    v = case_outline_center_v()
    bar = box_between(
        (EAR_CENTERS_U_MM[0] - BAR_REACH_INTO_POST_MM, EAR_CENTERS_U_MM[1] + BAR_REACH_BEYOND_EARS_MM),
        (v - BAR_DROP_MM, v + BAR_RISE_MM),
        (case_back_w() - BAR_THICKNESS_MM, case_back_w()),
    )
    bores = [
        cylinder_z((center_u, v), INSERT_BORE_DIAMETER_MM / 2.0,
                   (case_back_w() - BAR_INSERT_DEPTH_MM, case_back_w() + CUT_EXTRA_MM))
        for center_u in EAR_CENTERS_U_MM
    ]
    return bar, bores


def behind_case_in_case_frame():
    """Everything behind the plane of the case's back face, as a big box."""
    big = 1000.0
    return box_between((-big, big), (-big, big), (-big, case_back_w()))


# The arm, in the printer frame.

def post_back():
    return HEAD_REACH_MM + HEAD_CLEARANCE_MM


def post_front_profile():
    """The post's front face from the base's top: POST_CASE_GAP_MM in
    front of the Pi case's rearmost corner, then leaning forward along
    the case's back face at that gap until POST_FRONT_MM."""
    (corner_d, corner_h), (top_d, top_h) = PI_CASE_SIDE_PROFILE_MM[0], PI_CASE_SIDE_PROFILE_MM[1]
    length = math.hypot(top_d - corner_d, top_h - corner_h)
    away = ((corner_h - top_h) / length, (top_d - corner_d) / length)  # back and up, off the face
    start = (corner_d + POST_CASE_GAP_MM * away[0], corner_h + POST_CASE_GAP_MM * away[1])
    rise_per_mm = (top_h - corner_h) / (top_d - corner_d)
    lower_front = corner_d - POST_CASE_GAP_MM

    def lean_height(distance):
        return start[1] + (distance - start[0]) * rise_per_mm

    return [
        (lower_front, ARM_BASE_PLATE_HEIGHT_MM), (lower_front, lean_height(lower_front)),
        (POST_FRONT_MM, lean_height(POST_FRONT_MM)),
    ]


def post_profile(top):
    back = post_back()
    return [(back, ARM_BASE_PLATE_HEIGHT_MM)] + post_front_profile() + [(POST_FRONT_MM, top), (back, top)]


def build_arm():
    """Base plate and T-rails, the post and the bar, in the printer
    frame."""
    base = arm_base_range()
    rail_width = (-RAIL_HALF_WIDTH_MM, RAIL_HALF_WIDTH_MM)
    left = (POST_X_MM[0], POST_SPLIT_X_MM)
    right = (POST_SPLIT_X_MM, POST_X_MM[1])
    from_case = case_matrix()
    plate = box_between(rail_width, rail_y_range(base), (0.0, ARM_BASE_PLATE_HEIGHT_MM))
    rails = [t_rail(slot_x, base) for slot_x in RAIL_SLOT_CENTERS_X_MM]
    behind_case = behind_case_in_case_frame().transformed(from_case)
    posts = [
        side_profile_prism(post_profile(POST_LEFT_TOP_MM), left),
        side_profile_prism(post_profile(POST_TOP_MM), left).common(behind_case),
        side_profile_prism(post_profile(POST_TOP_MM), right),
    ]
    bar, bar_bores = bar_in_case_frame()
    arm = plate.fuse(rails + posts + [bar.transformed(from_case)])
    return single_solid(arm.cut(Part.makeCompound([bore.transformed(from_case) for bore in bar_bores])))


# Checks.

def check_probes(name, shape, probes):
    for point, solid in probes:
        if shape.isInside(vector(point), 1e-6, True) != solid:
            raise SystemExit(f"error: {name} is {'open' if solid else 'solid'} at {point}")


def check_valid(name, shape):
    if not shape.isValid():
        raise SystemExit(f"error: {name} is not a valid solid")


def downward_faces(shape):
    """Planar faces off the bed that face down by more than 45 degrees,
    in the print orientation."""
    bed = shape.BoundBox.ZMin
    flagged = []
    for face in shape.Faces:
        if not isinstance(face.Surface, Part.Plane):
            continue
        u0, u1, v0, v1 = face.ParameterRange
        normal = face.normalAt((u0 + u1) / 2.0, (v0 + v1) / 2.0)
        if normal.z < OVERHANG_NORMAL_LIMIT and face.BoundBox.ZMin > bed + 1e-3:
            flagged.append(face)
    return flagged


def overhang_report(shape):
    flagged = downward_faces(shape)
    if not flagged:
        return "none"
    largest = max(flagged, key=lambda face: face.Area)
    box = largest.BoundBox
    return (f"{len(flagged)} faces, {sum(face.Area for face in flagged):.1f} mm2, largest "
            f"{max(box.XLength, box.YLength):.1f} mm across")


def bed_contact(shape):
    """The area of the planar faces lying on the bed, in the print
    orientation, and whether the center of mass is over their extent."""
    bed = shape.BoundBox.ZMin
    faces = [face for face in shape.Faces
             if isinstance(face.Surface, Part.Plane) and face.BoundBox.ZMax < bed + 1e-3]
    if not faces:
        return 0.0, False
    box = Part.makeCompound(faces).BoundBox
    center = shape.Solids[0].CenterOfMass
    over = box.XMin <= center.x <= box.XMax and box.YMin <= center.y <= box.YMax
    return sum(face.Area for face in faces), over


def check_case(case_back, case_front):
    check_valid("the back shell", case_back)
    check_valid("the front shell", case_front)
    v = case_outline_center_v()
    hole = BOARD_HOLE_CENTERS_MM[0]
    socket_v = -outer_offset() - SOCK_SOCKET_DEPTH_MM / 2.0
    check_probes("the back shell", case_back, [
        ((BOARD_WIDTH_MM / 2.0, 16.0, -1.0), False),  # cavity
        ((hole[0] + INSERT_BORE_DIAMETER_MM / 2.0 + 0.3, hole[1], -1.0), True),  # standoff
        ((hole[0], hole[1], -INSERT_BORE_DEPTH_MM + 0.2), False),  # insert bore
        ((hole[0], hole[1], -INSERT_BORE_DEPTH_MM - 0.2), True),  # floor under it
        ((BOARD_WIDTH_MM / 2.0, -1.2, -2.0), False),  # ribbon slot
        ((BOARD_WIDTH_MM / 2.0, socket_v, -SOCK_SOCKET_HEIGHT_MM / 2.0 + 0.2), False),  # socket
        ((BOARD_WIDTH_MM / 2.0, socket_v, -SOCK_SOCKET_HEIGHT_MM / 2.0 - 0.2), True),
        ((EAR_CENTERS_U_MM[0], v, case_back_w() + 1.0), False),  # ear hole
        ((EAR_CENTERS_U_MM[0] - 2.0, v, case_back_w() + 1.0), True),  # ear
    ])
    front = case_front_w()
    check_probes("the front shell", case_front, [
        ((BOARD_WIDTH_MM / 2.0, 16.0, 2.0), False),  # cavity
        ((LENS_CENTER_MM[0], LENS_CENTER_MM[1], front - 0.5), False),  # lens window
        ((hole[0], hole[1], 2.0), False),  # screw hole
        ((hole[0] + 2.0, hole[1], 2.0), True),  # boss
        ((hole[0] + 2.0, hole[1], front - 0.5), False),  # counterbore
        ((BOARD_WIDTH_MM / 2.0, 20.0, front - 0.5), True),  # front plate
    ])


def t_rail_head_probes(slot_x, y):
    """Inside a T-rail's head by its side and just outside that side,
    halfway down the side (the profile's third and fourth points)."""
    head_x, head_top = T_RAIL_HALF_PROFILE_MM[2]
    z = (head_top + T_RAIL_HALF_PROFILE_MM[3][1]) / 2.0
    return [((slot_x + head_x - 0.3, y, z), True), ((slot_x + head_x + 0.3, y, z), False)]


def check_arm(arm):
    """Probe the T-rails (stems and heads) and the bar's insert bores on
    the arm in the printer frame."""
    y = y_in_front_of_upright(sum(arm_base_range()) / 2.0)
    head_top = T_RAIL_HALF_PROFILE_MM[1][1]
    probes = []
    for slot_x in RAIL_SLOT_CENTERS_X_MM:
        probes += [((slot_x, y, head_top / 2.0), True)] + t_rail_head_probes(slot_x, y)  # stem, head
    v = case_outline_center_v()
    bore_middle = case_back_w() - BAR_INSERT_DEPTH_MM / 2.0
    bore_wall = INSERT_BORE_DIAMETER_MM / 2.0 + 0.4
    for center_u in EAR_CENTERS_U_MM:
        probes += [
            (case_to_printer((center_u, v, bore_middle)), False),  # insert bore
            (case_to_printer((center_u, v + bore_wall, bore_middle)), True),  # bar around it
            (case_to_printer((center_u, v, case_back_w() - BAR_INSERT_DEPTH_MM - 0.5)), True),  # bore floor
        ]
    check_probes("the arm", arm, probes)


def check_rail_part(name, shape, distance_range):
    """Probe a spacer or shim rail: its stem's stub, its head, and nothing
    in the mouth chamfer above it."""
    slot_x = RAIL_SLOT_CENTERS_X_MM[1]
    y = y_in_front_of_upright(sum(distance_range) / 2.0)
    top = -SLOT_MOUTH_CHAMFER_DEPTH_MM
    head_top = T_RAIL_HALF_PROFILE_MM[1][1]
    check_valid(name, shape)
    check_probes(name, shape, [
        ((slot_x, y, (top + head_top) / 2.0), True),  # stub of the stem
        ((slot_x, y, top / 2.0), False),  # in the chamfer
    ] + t_rail_head_probes(slot_x, y))


def check_no_overlap(name, first, second):
    volume = first.common(second).Volume
    if volume > CONTACT_VOLUME_LIMIT_MM3:
        raise SystemExit(f"error: {name} overlap by {volume:.3f} mm3")


def check_board_fit(case_back, case_front_assembled):
    board = board_model()
    check_no_overlap("the board and the back shell", board, case_back)
    check_no_overlap("the board and the front shell", board, case_front_assembled)


# The printer's keep-outs, the Pi, the cable and the camera's view, in
# the printer frame.

def bed_plate_y_range(travel_position):
    front = NOZZLE_Y_MM - travel_position - (BED_PLATE_SIZE_MM - PRINT_AREA_SIZE_MM) / 2.0
    return front, front + BED_PLATE_SIZE_MM


def keep_out_boxes():
    """Boxes the arm and case must stay clear of, over the whole travel
    and print height."""
    swept_front = bed_plate_y_range(Y_TRAVEL_MM)[0]
    swept_back = bed_plate_y_range(0.0)[1]
    margin = (BED_PLATE_SIZE_MM - PRINT_AREA_SIZE_MM) / 2.0
    knob_x = BED_PLATE_X_MM[1] - LEVELLING_KNOB_INSET_MM
    print_top = BED_TOP_Z_MM + MAXIMUM_PRINT_HEIGHT_MM
    gantry = GANTRY_RIGHT_END_BOX_MM
    return {
        "right upright": UPRIGHT_BOX_MM,
        "X gantry's right end, swept up": (gantry[0], gantry[1], (gantry[2][0], 450.0)),
        "bed plate over the travel": (
            BED_PLATE_X_MM, (swept_front, swept_back),
            (BED_TOP_Z_MM - BED_PLATE_THICKNESS_MM, BED_TOP_Z_MM),
        ),
        "levelling knobs over the travel": (
            (knob_x - LEVELLING_KNOB_RADIUS_MM, knob_x + LEVELLING_KNOB_RADIUS_MM),
            (swept_front, swept_back), LEVELLING_KNOB_Z_MM,
        ),
        "print volume over the travel": (
            (BED_PLATE_X_MM[0] + margin, BED_PLATE_X_MM[1] - margin),
            (swept_front + margin, swept_back - margin), (BED_TOP_Z_MM, print_top),
        ),
    }


def head_reach_box():
    """The print head's reach, fan casing included, swept up as the gantry's end is."""
    return (
        (BED_PLATE_X_MM[0], HEAD_REACH_RIGHT_X_MM),
        (y_in_front_of_upright(HEAD_REACH_MM), UPRIGHT_BOX_MM[1][0]),
        (BED_TOP_Z_MM, 450.0),
    )


def pi_case():
    return side_profile_prism(PI_CASE_SIDE_PROFILE_MM, PI_CASE_X_MM)


def pi_mount():
    leg = cross_section_prism(PI_MOUNT_LEG_PROFILE_MM, pi_mount_range())
    return side_profile_prism(PI_MOUNT_SIDE_PROFILE_MM, PI_MOUNT_X_MM).fuse(leg)


def keep_outs():
    """What the arm and case must stay clear of, with the clearance each
    needs: any gap to the printer, more to the head and the Pi case."""
    shapes = {name: (box_between(*box), 0.0) for name, box in keep_out_boxes().items()}
    shapes["print head's reach"] = (box_between(*head_reach_box()), HEAD_CLEARANCE_MM)
    shapes["Pi case"] = (pi_case(), PI_CASE_CLEARANCE_MM)
    return shapes


def pi_case_top_height(distance):
    """The height of the Pi case's top face that far in front of the
    upright, along its edge from the top of the back face forward."""
    (back_d, back_h), (front_d, front_h) = PI_CASE_SIDE_PROFILE_MM[1], PI_CASE_SIDE_PROFILE_MM[2]
    return back_h + (front_h - back_h) * (distance - back_d) / (front_d - back_d)


def cable_corridor():
    """The sock's path from the socket's mouth: along the case's -v, then
    straight down onto the Pi case (down to its top face's height under
    the corridor's front edge, the Pi case cut away)."""
    radius = CABLE_CORRIDOR_WIDTH_MM / 2.0
    _, v_axis, _ = case_axes()
    down_v = scale(v_axis, -1.0)
    mouth = case_to_printer(sock_socket_mouth())
    bend = add(mouth, scale(down_v, CABLE_CORRIDOR_RUN_MM))
    lowest = pi_case_top_height(distance_in_front_of_upright(bend[1]) + radius)
    along = Part.makeCylinder(radius, CABLE_CORRIDOR_RUN_MM, vector(mouth), vector(down_v))
    elbow = Part.makeSphere(radius, vector(bend))
    drop = Part.makeCylinder(radius, bend[2] - lowest, vector(bend), App.Vector(0, 0, -1))
    return along.fuse([elbow, drop]).cut(pi_case())


def view_frustum(lens, axes):
    """The camera's field of view as a solid, over VIEW_CHECK_DEPTH_MM."""
    forward, right, up = axes
    across = math.tan(math.radians(HORIZONTAL_FIELD_OF_VIEW_DEGREES / 2.0))
    upward = math.tan(math.radians(VERTICAL_FIELD_OF_VIEW_DEGREES / 2.0))

    def rectangle(depth):
        center = add(lens, scale(forward, depth))
        corners = [add(center, add(scale(right, side * across * depth), scale(up, rise * upward * depth)))
                   for side, rise in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
        return Part.makePolygon([vector(corner) for corner in corners + corners[:1]])

    return Part.makeLoft([rectangle(depth) for depth in VIEW_CHECK_DEPTH_MM], True, True)


def bed_points(travel_position):
    """A grid over the print area with the bed at that Y position."""
    left = BED_PLATE_X_MM[0] + (BED_PLATE_SIZE_MM - PRINT_AREA_SIZE_MM) / 2.0
    step = PRINT_AREA_SIZE_MM / (COVERAGE_GRID - 1)
    return [
        (left + column * step, NOZZLE_Y_MM - travel_position + row * step, BED_TOP_Z_MM)
        for column in range(COVERAGE_GRID) for row in range(COVERAGE_GRID)
    ]


def in_view(point, lens, axes):
    forward, right, up = axes
    offset = tuple(p - q for p, q in zip(point, lens))
    depth = dot(offset, forward)
    if depth <= 0.0:
        return False
    across = math.degrees(math.atan2(abs(dot(offset, right)), depth))
    upward = math.degrees(math.atan2(abs(dot(offset, up)), depth))
    return across <= HORIZONTAL_FIELD_OF_VIEW_DEGREES / 2.0 and upward <= VERTICAL_FIELD_OF_VIEW_DEGREES / 2.0


def segment_hits_box(start, end, box):
    low, high = 0.0, 1.0
    for axis in range(3):
        minimum, maximum = box[axis]
        delta = end[axis] - start[axis]
        if abs(delta) < 1e-12:
            if not minimum <= start[axis] <= maximum:
                return False
            continue
        first, second = sorted(((minimum - start[axis]) / delta, (maximum - start[axis]) / delta))
        low, high = max(low, first), min(high, second)
        if low > high:
            return False
    return True


def coverage_by_travel(lens, axes, occluders):
    """For each sampled Y position, the share of the print area in view
    and not hidden behind an occluder."""
    shares = []
    for step in range(COVERAGE_TRAVEL_STEPS):
        travel_position = Y_TRAVEL_MM * step / (COVERAGE_TRAVEL_STEPS - 1)
        points = bed_points(travel_position)
        seen = [
            point for point in points
            if in_view(point, lens, axes) and not any(segment_hits_box(lens, point, box) for box in occluders)
        ]
        shares.append((travel_position, len(seen) / len(points)))
    return shares


# Print orientations.

def standing_on_back_end(shape):
    """Up in the print is forward on the printer: a part stands on its
    end toward the upright, a rail's profile in the layer plane. The
    arm prints this way, on its back, and the shim."""
    return shape.transformed(App.Matrix(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1))


def case_back_print(shape):
    return shape.transformed(App.Matrix(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, -case_back_w(), 0, 0, 0, 1))


def case_front_print(shape):
    return shape.transformed(App.Matrix(1, 0, 0, 0, 0, -1, 0, 0, 0, 0, -1, case_front_w(), 0, 0, 0, 1))


def on_bed_origin(shape):
    box = shape.BoundBox
    moved = shape.copy()
    moved.translate(App.Vector(-box.XMin, -box.YMin, -box.ZMin))
    return moved


def check_ear_screw_access(case_back, case_front_assembled, arm_in_case):
    """A straight driver reaches each ear screw's head from the front:
    a cylinder EAR_SCREW_DRIVER_DIAMETER_MM across from the ear's front
    face forward along the screw's axis, past the front shell's side,
    clear of both shells and the arm (case frame)."""
    v = case_outline_center_v()
    start = case_back_w() + EAR_THICKNESS_MM
    for center_u in EAR_CENTERS_U_MM:
        driver = cylinder_z((center_u, v), EAR_SCREW_DRIVER_DIAMETER_MM / 2.0, (start, start + 60.0))
        check_no_overlap("an ear screw's driver and the back shell", driver, case_back)
        check_no_overlap("an ear screw's driver and the front shell", driver, case_front_assembled)
        check_no_overlap("an ear screw's driver and the arm", driver, arm_in_case)


def check_clearances(assembly):
    """The distance from the assembly to each keep-out, failing below what it needs."""
    clearances = {}
    for name, (shape, minimum) in keep_outs().items():
        distance = assembly.distToShape(shape)[0]
        if distance <= 0.0 or distance < minimum - CLEARANCE_TOLERANCE_MM:
            raise SystemExit(f"error: the arm or case is {distance:.2f} mm from the {name}, needs {minimum:.1f}")
        clearances[name] = (distance, minimum)
    return clearances


def stack_report():
    """The rail stack from the upright's bolt to the rail's front end."""
    bolt = upright_bolt_front()
    mount_length = pi_mount_range()[1] - pi_mount_range()[0]
    stack = SPACER_LENGTH_MM + ARM_BASE_LENGTH_MM + mount_length
    left = [free - bolt - stack for free in RAIL_FREE_TOP_FACE_MM]
    gap = pi_mount_range()[0] - arm_base_range()[1]
    return (f"rail:       from the upright's bolt at {bolt:.1f}: spacer {SPACER_LENGTH_MM} + arm base "
            f"{ARM_BASE_LENGTH_MM:.0f} + Pi mount {mount_length:.0f} = {stack:.1f} mm, leaving {left[0]:.1f} to "
            f"{left[1]:.1f} mm to the rail's front end for {SHIM_LENGTH_MM} mm shims; the arm base takes "
            f"{arm_base_range()[0]:.1f} to {arm_base_range()[1]:.1f} in front of the upright, {gap:.1f} mm from the "
            f"Pi mount's back end at {pi_mount_range()[0]:.0f} (the user's measurement)")


def post_report(arm_box):
    lower_front, lean_bottom = post_front_profile()[1]
    lean_top = post_front_profile()[2][1]
    return (f"post:       {post_back():.1f} to {POST_FRONT_MM} in front of the upright, leaning "
            f"{POST_CASE_GAP_MM} mm off the Pi case's back from {lean_bottom:.1f} to {lean_top:.1f} mm up "
            f"({lower_front:.1f} below that); x {POST_X_MM[0]:.0f} to {POST_SPLIT_X_MM:.0f} up to "
            f"{POST_LEFT_TOP_MM:.0f} mm (behind the case's back face up to {POST_TOP_MM:.0f}), x "
            f"{POST_SPLIT_X_MM:.0f} to {POST_X_MM[1]:.0f} up to {POST_TOP_MM:.0f}; the arm spans x "
            f"{arm_box.XMin:.1f} to {arm_box.XMax:.1f}")


def main():
    arguments = script_arguments(sys.argv)
    if len(arguments) != 1:
        raise SystemExit(USAGE)
    output_directory = arguments[0]
    if not os.path.isdir(output_directory):
        raise SystemExit(f"error: {output_directory} is not a directory")

    case_back = build_case_back()
    case_front = build_case_front()
    check_case(case_back, case_front)
    front_assembled_in_case = case_front.copy()
    front_assembled_in_case.translate(App.Vector(0, 0, FRONT_BOSS_PRESS_MM))
    check_no_overlap("the shells", case_back, front_assembled_in_case)
    check_board_fit(case_back, front_assembled_in_case)
    arm = build_arm()
    check_valid("the arm", arm)
    check_arm(arm)
    spacer = build_rail_part(spacer_range())
    check_rail_part("the spacer", spacer, spacer_range())
    shim = build_rail_part(shim_range())
    check_rail_part("the shim", shim, shim_range())
    check_ear_screw_access(case_back, front_assembled_in_case, arm.transformed(case_matrix().inverse()))

    placed_back = case_back.transformed(case_matrix())
    placed_front = case_front.transformed(case_matrix(FRONT_BOSS_PRESS_MM))
    check_no_overlap("the arm and the back shell", arm, placed_back)
    check_no_overlap("the arm and the front shell", arm, placed_front)
    rail = rail_top_metal((spacer_range()[0], RAIL_FREE_TOP_FACE_MM[1]))
    for name, part in (("arm", arm), ("spacer", spacer), ("shim", shim)):
        check_no_overlap(f"the {name} and the rail", part, rail)
    check_no_overlap("the arm and the spacer", arm, spacer)
    check_no_overlap("the arm and the Pi mount", arm, pi_mount())
    lens = lens_position()
    yaw, pitch = camera_yaw_and_pitch()
    axes = camera_axes(yaw, pitch)
    frustum = view_frustum(lens, axes)
    check_no_overlap("the arm and the camera's field of view", arm, frustum)
    clearances = check_clearances(Part.makeCompound([arm, placed_back, placed_front]))
    cable_clearance = arm.distToShape(cable_corridor())[0]
    if cable_clearance < CABLE_CLEARANCE_MM - CLEARANCE_TOLERANCE_MM:
        raise SystemExit(f"error: the arm is {cable_clearance:.2f} mm from the cable's corridor, "
                         f"needs {CABLE_CLEARANCE_MM}")

    prints = {
        "arm": on_bed_origin(standing_on_back_end(arm)),
        "spacer": on_bed_origin(spacer),  # lying on its underside, as it sits in the slot
        "shim": on_bed_origin(standing_on_back_end(shim)),
        "case_back": on_bed_origin(case_back_print(case_back)),
        "case_front": on_bed_origin(case_front_print(case_front)),
    }
    arm_print_box = prints["arm"].BoundBox
    if sorted((arm_print_box.XLength, arm_print_box.YLength))[1] > BUILD_VOLUME_MM[0] \
            or arm_print_box.ZLength > BUILD_VOLUME_MM[2]:
        raise SystemExit("error: the arm does not fit the printer's build volume")
    for part, shape in prints.items():
        stl_file = os.path.join(output_directory, PART_FILE_NAMES[part])
        mesh = export_stl(shape, stl_file)
        check_closed_mesh(stl_file)
        box = shape.BoundBox
        contact_area, over_contact = bed_contact(shape)
        print(f"{part + ':':12s}{box.XLength:.1f} x {box.YLength:.1f} x {box.ZLength:.1f} mm as printed, "
              f"{shape.Volume / 1000.0:.1f} cm3, {contact_area / 100.0:.1f} cm2 on the bed with the center of "
              f"mass {'over' if over_contact else 'outside'} it, downward faces past 45 degrees: "
              f"{overhang_report(shape)}, wrote {stl_file} ({mesh.CountFacets} facets)")

    print(f"case:       {BOARD_WIDTH_MM + 2 * outer_offset():.1f} x {BOARD_HEIGHT_MM + 2 * outer_offset():.1f} x "
          f"{case_front_w() - case_back_w():.1f} mm, {LENS_WINDOW_SIDE_MM:.1f} mm lens window, sock socket "
          f"{SOCK_SOCKET_WIDTH_MM} x {SOCK_SOCKET_HEIGHT_MM} mm, {SOCK_SOCKET_DEPTH_MM} mm deep; the seam "
          f"stays {FRONT_BOSS_PRESS_MM} mm open on a {BOARD_THICKNESS_MM} mm board")
    print(stack_report())
    print(f"T-rails:    {2 * T_RAIL_HALF_PROFILE_MM[0][0]:.1f} mm stems, {2 * T_RAIL_HALF_PROFILE_MM[2][0]:.1f} mm "
          f"heads, {t_rail_depth():.1f} mm deep: a spacer rail clears the slot's walls by "
          f"{spacer.distToShape(rail)[0]:.2f} mm, its top {SLOT_MOUTH_CHAMFER_DEPTH_MM} mm down at the mouth "
          f"chamfer's bottom corner")
    arm_box = arm.BoundBox
    print(post_report(arm_box))

    first_lens = first_arm_lens()
    right_edge = BED_PLATE_X_MM[1] - (BED_PLATE_SIZE_MM - PRINT_AREA_SIZE_MM) / 2.0
    print(f"camera:     lens at x {lens[0]:.1f}, {distance_in_front_of_upright(lens[1]):.1f} mm in front of the "
          f"upright, {lens[2]:.1f} mm up ({LENS_HEIGHT_SHARE_OF_FIRST_ARM:.3f} of the first arm's "
          f"{first_lens[2]:.1f}): {lens[2] - BED_TOP_Z_MM:.1f} mm above the bed, {lens[0] - right_edge:.1f} mm right "
          f"of the print area, {NOZZLE_Y_MM - lens[1]:.1f} mm in front of the nozzle; aimed at the bed's center at "
          f"mid travel: yaw {yaw:.1f} degrees ({180.0 - yaw:.1f} from straight left toward the back), pitch "
          f"{pitch:.1f} degrees down")
    case_top = max(placed_back.BoundBox.ZMax, placed_front.BoundBox.ZMax)
    print(f"height:     the arm's highest point {arm_box.ZMax:.1f} mm above the rail's top face (the first arm's "
          f"{first_arm_top():.1f}), the case's {case_top:.1f}")
    for label, occluders in (("in view", []), ("unhidden", [UPRIGHT_BOX_MM, GANTRY_RIGHT_END_BOX_MM, X_BEAM_BOX_MM])):
        shares = coverage_by_travel(lens, axes, occluders)
        mean = sum(share for _, share in shares) / len(shares)
        listed = ", ".join(f"{position:.0f}: {share * 100:.0f}" for position, share in shares)
        print(f"coverage:   {label}, % of the print area by bed Y position: {listed}; mean {mean * 100:.0f} %")
    for name, (distance, minimum) in clearances.items():
        needed = f" ({minimum:.0f} needed)" if minimum > 0.0 else ""
        print(f"clearance:  {distance:.1f} mm to the {name}{needed}")
    print(f"clearance:  {cable_clearance:.1f} mm from the arm to the cable's corridor "
          f"({CABLE_CLEARANCE_MM:.0f} needed), {arm.distToShape(frustum)[0]:.1f} mm to the camera's field of view")


run_and_exit(main)
