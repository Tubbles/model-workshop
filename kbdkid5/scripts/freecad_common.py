"""Shared helpers for this repo's headless FreeCAD scripts.

STL export with a check that the written mesh is closed, an outline
offset, plus the scaffolding that makes freecadcmd usable as a
script interpreter. Unlike the export scripts this module has no entry
point, so it is safe to import from probes and other scripts.

The scaffolding exists because freecadcmd (observed on 1.0.0) executes
command line scripts with __name__ set to the file's stem, runs them
twice, always exits 0 even when the script raised, and its option
parser intercepts dash-prefixed arguments even after "--pass". Hence
scripts take key=value words, parse everything after "--pass", and
leave through run_and_exit(), which flushes and calls os._exit() so CI
sees a real exit code and the second run never happens.
"""

import math
import os
import sys
import traceback

import Mesh
import MeshPart
import Part

MESH_LINEAR_DEFLECTION_MM = 0.05
MESH_ANGULAR_DEFLECTION_DEGREES = 15.0

# makeOffset2D's join types: corners extended to their intersection,
# or rounded with arcs around the original corners.
SHARP_JOIN = 2
ROUND_JOIN = 0


def script_arguments(argv):
    """Return the arguments meant for this script.

    Under freecadcmd, sys.argv contains freecadcmd's own arguments too;
    everything after "--pass" is ours. Under a plain python interpreter
    the usual convention applies.
    """
    if "--pass" in argv:
        return argv[argv.index("--pass") + 1 :]
    return argv[1:]


def offset_outline(wire, distance, join=SHARP_JOIN):
    """Offset a closed wire by `distance`, by default with sharp corners
    (SHARP_JOIN, corners extended to their intersection), with
    ROUND_JOIN rounded around them: positive is outward, negative
    inward. makeOffset2D's own sign follows the wire's orientation, so
    pick the candidate whose area moved the right way.
    """
    original_area = Part.Face(wire).Area
    wants_growth = distance > 0

    def moved_correctly(candidate_wire):
        area = Part.Face(candidate_wire).Area
        return area > original_area if wants_growth else area < original_area

    candidate = wire.makeOffset2D(distance, join)
    if not moved_correctly(candidate):
        candidate = wire.makeOffset2D(-distance, join)
    if not moved_correctly(candidate):
        raise SystemExit(f"error: offsetting the outline by {distance} mm failed")
    return candidate


def export_stl(shape, stl_file):
    mesh = MeshPart.meshFromShape(
        Shape=shape,
        LinearDeflection=MESH_LINEAR_DEFLECTION_MM,
        AngularDeflection=math.radians(MESH_ANGULAR_DEFLECTION_DEGREES),
        Relative=False,
    )
    mesh.write(stl_file)
    return mesh


def check_closed_mesh(stl_file):
    """Fail on an STL that is not one closed, manifold shell free of
    self-intersections, read back from the file itself since STL
    stores single precision coordinates. Remove a failing file: it
    must never be left behind as if it were fine."""
    mesh = Mesh.Mesh(stl_file)
    problems = []
    if not mesh.isSolid():
        problems.append("not closed")
    if mesh.hasNonManifolds():
        problems.append("non-manifold")
    components = mesh.countComponents()
    if components != 1:
        problems.append(f"{components} separate components")
    if mesh.hasSelfIntersections():
        problems.append("self-intersecting")
    if problems:
        os.remove(stl_file)
        raise SystemExit(
            f"error: the mesh is {', '.join(problems)}, removed {stl_file}"
        )


def run_and_exit(main_function):
    """Run a script's main() and leave through os._exit(), giving CI a
    real exit code and preventing freecadcmd's second run (see the
    module docstring)."""
    exit_code = 0
    try:
        main_function()
    except SystemExit as stop:
        if isinstance(stop.code, str):
            print(stop.code, file=sys.stderr)
            exit_code = 1
        else:
            exit_code = stop.code or 0
    except Exception:
        traceback.print_exc()
        exit_code = 1
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(exit_code)
