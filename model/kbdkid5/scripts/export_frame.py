"""Export the hand-wired frame or its backing (STL), work item 014, for
either half: the first iteration, without diode cradles or wire
grooves. frame_shape.py builds them and its docstring has the design.

  frame    the frame in the PCB's place, upside down for printing, its
           top face on z = 0: the switches' holes, the sockets' pockets
           at -0.15 with their tab slots and recesses, the bosses bored
           for M2 heat-set inserts, the mounting drills with a tube
           under each that stands on the tray's standoff
  backing  the backing that screws up under the sockets, bottom down,
           with a pad under each socket lobe and its cutouts around the
           tray; checked stacked under the frame, which it builds too

Runs headless under FreeCAD's console interpreter (see
freecad_common.py for the freecadcmd quirks that shape the
invocation):

    freecadcmd model/kbdkid5/scripts/export_frame.py --pass <part.stl> frame|backing [right]
        [insert_length=<mm>]

Either part is checked for one valid solid of the volume its plan
faces give and written as one closed mesh. The frame's pocket walls
are whole but those layout.frame_walls_cut_back() lists (none since
work item 034), and the export fails where the tray comes nearer them
or the tubes than layout.FRAME_TRAY_CLEARANCE_MM (frame_shape.py). The
backing is also checked
stacked under the frame: nothing overlapping, the backing touching only
the bosses' ends, every pad 0.1 under its socket's bottom.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App
import Part

import layout
import frame_shape as shape
import socket_test_shape as cells
from freecad_common import check_closed_mesh, export_stl, run_and_exit, script_arguments

KINDS = ("frame", "backing")
MEASURE_TOLERANCE_MM = 1e-6
CONTACT_PROBE_DEPTH_MM = 0.01
CONTACT_VOLUME_RELATIVE_TOLERANCE = 1e-3

USAGE = """\
usage: freecadcmd model/kbdkid5/scripts/export_frame.py --pass <part.stl> frame|backing [right]
    [insert_length=<mm>]

  right          the right half: outline, drills, bosses and backing mirrored
                 across the layout's right-half mirror line, every socket the
                 left half's at the mirrored key center
  insert_length  the heat-set inserts' length, which sets the bores' depth
                 (default the longest the bosses hold)\
"""


class Arguments:
    def __init__(self):
        self.stl_file = None
        self.kind = None
        self.right = False
        self.insert_length = None


def parse_arguments(argument_list):
    arguments = Arguments()
    positionals = []
    for argument in argument_list:
        if argument == "right":
            arguments.right = True
        elif "=" in argument:
            key, _, value = argument.partition("=")
            if key != "insert_length":
                raise SystemExit(f"error: unknown option '{key}'\n{USAGE}")
            try:
                arguments.insert_length = float(value)
            except ValueError:
                raise SystemExit(f"error: '{key}' needs a number, got '{value}'")
        else:
            positionals.append(argument)
    if len(positionals) != 2 or positionals[1] not in KINDS:
        raise SystemExit(USAGE)
    arguments.stl_file, arguments.kind = positionals
    return arguments


def boss_end_area_on_backing(right):
    """The bosses' ends' rings where the backing lies under them in
    plan. Two of the left half's bosses by the nice!nano stand 0.8 over
    the west strip's cutout, so the backing takes less than the whole
    ring there."""
    plan = shape.backing_face(right)
    return sum(
        cells.circle_face(center, cells.BOSS_DIAMETER_MM / 2.0)
        .cut(cells.circle_face(center, cells.INSERT_BORE_DIAMETER_MM / 2.0))
        .common(plan).Area
        for center in shape.boss_centers(right))


def check_stack(frame, stacked, right):
    """Nothing overlapping, and the backing touching the frame over the
    bosses' ends' rings alone, where it lies under them."""
    if frame.common(stacked).Volume > MEASURE_TOLERANCE_MM:
        raise SystemExit("error: the backing overlaps the frame")
    sunk = frame.copy()
    sunk.translate(App.Vector(0.0, 0.0, -CONTACT_PROBE_DEPTH_MM))
    contact = sunk.common(stacked).Volume / CONTACT_PROBE_DEPTH_MM
    expected = boss_end_area_on_backing(right)
    if abs(contact - expected) > CONTACT_VOLUME_RELATIVE_TOLERANCE * expected:
        raise SystemExit(f"error: the backing touches the frame over {contact:.4f} mm2, the "
                         f"bosses' ends over it are {expected:.4f} mm2")
    return contact


def check_pad_tops(stacked, right):
    """Every pad's top as stacked, at its offset from the socket's
    bottom."""
    target = -cells.socket_height() + cells.cell_pad_offset(shape.PAD_CELL_INDEX)
    tops = [face.BoundBox.ZMax for face in stacked.Faces
            if isinstance(face.Surface, Part.Plane) and abs(face.Surface.Axis.z) > 0.999
            and abs(face.BoundBox.ZMax - target) < 1e-6 and abs(face.BoundBox.ZMin - target) < 1e-6]
    expected = len(shape.backing_pads(right))
    if len(tops) != expected:
        raise SystemExit(f"error: {len(tops)} pad tops at z {target:.3f}, expected {expected}")
    return target



def main():
    arguments = parse_arguments(script_arguments(sys.argv))
    right = arguments.right
    half = "right" if right else "left"
    if arguments.kind == "frame":
        frame, expected, figures, (tubes, nearest) = shape.build_frame(right,
                                                                       arguments.insert_length)
        part = shape.turned_for_printing(frame)
        print(f"frame:      {half} half, {len(figures)} sockets at fit "
              f"{layout.FRAME_POCKET_FIT_MM}, {len(shape.boss_centers(right))} bosses, volume "
              f"{frame.Volume:.3f} mm3 (plan {expected:.3f} mm3)")
        cut_back = layout.frame_walls_cut_back(right)
        print(f"walls:      whole around {len(figures) - len(cut_back)} of {len(figures)} sockets, "
              f"{sum(figures.values()):.3f} mm2 in plan, the tray at least "
              f"{layout.FRAME_TRAY_CLEARANCE_MM} from them")
        for key, body in cut_back:
            print(f"            {key}'s cut back from the {body} (work item 026, kept by the user), "
                  f"{figures[key]:.3f} mm2 left")
        depth = cells.wall_depth()
        print(f"tubes:      {len(tubes)} under the drills, {depth:.3f} deep, the walls' depth (z "
              f"{layout.PCB_UNDERSIDE_Z_MM - depth:.3f} to {layout.PCB_UNDERSIDE_Z_MM} in the "
              f"tray, their mouth on the standoffs' top at {layout.STANDOFF_HEIGHT_MM:.3f}), each "
              f"the standoff's {layout.STANDOFF_DIAMETER_MM} circle with its flats less the "
              f"drill, {sum(tubes.values()):.3f} mm2 in plan, the tray at least "
              f"{nearest[0]:.4f} from them ({nearest[1]})")
        for center, area in tubes.items():
            cut = layout.frame_tube_block_cut(center)
            stop = (f", stopped {cut[1]:.3f} from its axis, {layout.FRAME_TRAY_CLEARANCE_MM} short "
                    "of the joint block" if cut is not None else "")
            flats = len(shape.standoff_flats(center, right))
            print(f"            at {center}: {area:.3f} mm2, {flats} flats{stop}")
    else:
        backing, expected = shape.build_backing(right)
        frame, _, _, _ = shape.build_frame(right, arguments.insert_length)
        stacked = shape.stacked_backing(backing)
        contact = check_stack(frame, stacked, right)
        top = check_pad_tops(stacked, right)
        part = backing
        print(f"backing:    {half} half, {len(shape.backing_pads(right))} pads, "
              f"{len(shape.boss_centers(right))} screw holes, volume {backing.Volume:.3f} mm3 "
              f"(plan {expected:.3f} mm3)")
        print(f"stack:      touching the bosses' ends over {contact:.3f} mm2 alone, the pads' "
              f"tops at {top:.3f} under the ceiling, the sockets' bottoms at "
              f"{-cells.socket_height():.3f}")
    mesh = export_stl(part, arguments.stl_file)
    check_closed_mesh(arguments.stl_file)
    box = part.BoundBox
    print(f"part:       {box.XLength:.2f} x {box.YLength:.2f} x {box.ZLength:.2f} mm")
    print(f"wrote:      {arguments.stl_file} ({mesh.CountFacets} facets), one closed manifold shell")


run_and_exit(main)
