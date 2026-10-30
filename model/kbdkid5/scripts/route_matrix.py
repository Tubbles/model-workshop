"""The matrix's route under kbdkid5's hand-wired frame (work item 043,
DESIGN.md, Hand-wired frame, Matrix wiring), worked out on the room
between the frame's underside and the backing as a CI artifact's STLs
build it, each half in its own frame seen from the top.

model/kbdkid5/README.md (Routing the matrix) has the command. For each
half it writes the route as JSON, with every net's chain and lead length
and every squeeze with what bounds it, and two pictures, the half from
the top and its underside, to tmp/route_matrix/, and prints the lengths
and the squeezes.

The room (Room) is the STLs sampled on ROOM_CELL_MM by ray
parity: the frame below its ceiling (its pocket walls, tubes and
bosses), turned back from its print orientation, whatever of the tray
stands between the backing's top and the ceiling, and from layout.py
the sockets and the switches' posts and pegs. The route runs on
ROUTE_CELL_MM cells of the distance from that plastic (DistanceGrid), by
Dijkstra's shortest paths over each cell's eight neighbours:

- place_diodes() puts each key's diode where its anode lead, routed from
  the socket's west tab, is shortest, its body clear of the plastic, the
  other tabs and the diodes placed before it, a cathode pointing north
  preferred, and only where the room it leaves is still one region with
  the cathode's end in it. A key whose west tab has no such place takes
  its diode on its east tab.
- Router chains each column's other tabs, top to bottom, and each row's
  cathode ends, from column 0 to column 5 with the thumb's last on row 3,
  each wire kept off the diodes' bodies and anode leads and the other
  rows' cathode leads, its cost rising near plastic, more under
  SQUEEZE_MM, and near the wires routed before it.
- Each net's lead runs from anywhere on it to a free cell inside the
  backing's opening for the leads (layout.frame_backing_opening()), the
  net farthest from it first, each lead's end 1.0 from the others'.

squeezes_along() finds the squeezes on each wire, and squeeze_bounds()
what bounds each: the classes in bound_labels() at the room's heights,
and those in wire_level_labels() at the level of a wire lying on the
backing, with the floor under it. The frame's bosses there are
layout.py's, which check_bosses() holds the artifact's frame to.
"""

import argparse
import json
import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.lines  # noqa: E402
import matplotlib.patches  # noqa: E402
import matplotlib.pyplot as pyplot  # noqa: E402
import numpy  # noqa: E402
from scipy import ndimage, sparse  # noqa: E402
from scipy.sparse import csgraph  # noqa: E402

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
REPOSITORY = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPTS)))
sys.path.insert(0, SCRIPTS)

import check_layout  # noqa: E402
import layout  # noqa: E402

OUTPUT = os.path.join(REPOSITORY, "tmp", "route_matrix")
HALVES = (("left", False), ("right", True))

# The room's cells, in a half's own frame seen from the top, wide enough
# for either half.
ROOM_CELL_MM = 0.1
ROOM_XS = numpy.arange(-1.0, 134.0, ROOM_CELL_MM)
ROOM_YS = numpy.arange(-1.0, 84.0, ROOM_CELL_MM)
NORTH_EDGE_Y_MM = max(y for _, y in layout.OUTLINE_VERTICES_MM)

# The heights the STLs are sampled at, each in its own STL's z. The
# frame lies as printed (frame_shape.turned_for_printing()), its y
# turned about the half's middle: its top face at z 0, its ceiling at
# 1.6, the pocket walls' and the tubes' mouths at 3.4 and the bosses'
# ends at 3.867, so FRAME_BOSS_LEVEL_Z_MM finds the bosses alone.
FRAME_BODY_Z_MM = 0.8
FRAME_WALL_LEVEL_Z_MM = (1.7, 3.0)
FRAME_BOSS_LEVEL_Z_MM = 3.6
# The tray keeps layout.py's z: the room between the backing's top
# (7.233) and the ceiling (9.5), the last of which only a tray body
# reaching the ceiling stands in; a wire lying on the backing, or where
# the backing is cut out on what is under it; and the floors there.
TRAY_ROOM_Z_MM = (7.3, 8.0, 8.7, 9.4)
TRAY_WIRE_LEVEL_Z_MM = (7.0, 7.3, 7.5, 7.65)
TRAY_FLOOR_Z_MM = (6.0, 6.5, 6.9)
# The backing lies as printed, its plate from z 0 to 0.8.
BACKING_Z_MM = 0.4

# The switches' center post and side pegs as the user calipered them
# (doc/components.md, section 9), at their footprint holes
# (layout.CHOC_FOOTPRINT_HOLES_MM' first three), reaching
# layout.SWITCH_POSTS_BELOW_PCB_MM below the frame's ceiling.
POST_DIAMETER_MM = 3.17
PEG_DIAMETER_MM = 1.65

# On a socket's tabs, from the key center, in a half's own frame from
# the top: the middle of each tab's stretch outside its pocket wall
# (the wall's outer face at -8.35 and +2.95, the tips at -9.28 and
# +3.87). The west tab is kbdkid4's pad 1 (the diode's anode), the east
# tab its pad 2 (the column).
WEST_TAB = (-8.8, -3.70)
EAST_TAB = (3.4, -5.90)

ROUTE_CELL_MM = 0.2
DIODE_BODY_MM = 3.9  # Diotec's DO-35, 3.9 +-0.4 long (doc/components.md, section 12)
DIODE_RADIUS_MM = 1.0  # its 1.9 +-0.1 across
LEAD_RADIUS_MM = 0.27  # its 0.5 lead
WIRE_RADIUS_MM = 0.2  # the enamelled wire's 0.215, so a 0.4 gap passes it, pressed
SQUEEZE_MM = 0.45  # a wire's center nearer than this to plastic costs SQUEEZE_COST per mm
SQUEEZE_COST = 10.0
NEAR_TAB_RADIUS_MM = 0.22  # kept from plastic within NEAR_TAB_MM of a tab or a cathode's end
NEAR_TAB_MM = 1.3
CATHODE_STUB_MM = 1.6  # the cathode's lead to where the row wire takes it
LEAD_REACH_MM = 9.0  # the longest anode lead
# A squeeze is reported once it runs this many SQUEEZE_STEP_MM samples,
# and a picture circles those whose least clearance is under
# DRAWN_SQUEEZE_MM.
SQUEEZE_STEP_MM = 0.1
SQUEEZE_SAMPLES = 5
DRAWN_SQUEEZE_MM = 0.35

ROWS = 4
COLUMNS = 6
DIRECTIONS = [(round(math.cos(math.radians(angle)), 6), round(math.sin(math.radians(angle)), 6))
              for angle in range(0, 360, 45)]

# What bounds a squeeze, looked for this far out either side of it in
# steps of BOUND_STEP_MM, across it and up to 30 degrees off.
BOUND_STEP_MM = 0.02
BOUND_REACH_MM = 3.0


# The STLs.


def read_triangles(path):
    """A binary STL's triangles, as (count, 3 corners, xyz)."""
    with open(path, "rb") as stream:
        stream.read(80)
        count = int(numpy.frombuffer(stream.read(4), dtype="<u4")[0])
        record = numpy.dtype([("normal", "<f4", 3), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")])
        return numpy.frombuffer(stream.read(count * record.itemsize), dtype=record)["vertices"].astype(float)


def ray_crossings(triangles, y, z):
    """The x of every crossing of the line at (y, z) along x with the
    mesh, sorted."""
    first, second, third = triangles[:, 0], triangles[:, 1], triangles[:, 2]
    to_second, to_third = second[:, 1:] - first[:, 1:], third[:, 1:] - first[:, 1:]
    offset = numpy.array([y, z]) - first[:, 1:]
    determinant = to_second[:, 0] * to_third[:, 1] - to_second[:, 1] * to_third[:, 0]
    keep = numpy.abs(determinant) > 1e-12
    safe = numpy.where(keep, determinant, 1.0)
    along_second = (offset[:, 0] * to_third[:, 1] - offset[:, 1] * to_third[:, 0]) / safe
    along_third = (to_second[:, 0] * offset[:, 1] - to_second[:, 1] * offset[:, 0]) / safe
    hit = keep & (along_second >= 0) & (along_third >= 0) & (along_second + along_third <= 1)
    x = first[:, 0] + along_second * (second[:, 0] - first[:, 0]) + along_third * (third[:, 0] - first[:, 0])
    return numpy.sort(x[hit])


def solid_at(triangles, xs, ys, z):
    """Where the mesh is solid at height z, rows along ys, by the parity
    of each row's crossings. The rays are nudged off the grid's round
    figures so that none runs along an edge."""
    z = z + 2.345e-5
    heights = triangles[:, :, 2]
    triangles = triangles[(heights.min(axis=1) <= z) & (heights.max(axis=1) >= z)]
    solid = numpy.zeros((len(ys), len(xs)), dtype=bool)
    for row, y in enumerate(ys):
        crossings = ray_crossings(triangles, y + 1.234e-5, z)
        for start, end in zip(crossings[0::2], crossings[1::2]):
            solid[row, (xs >= start) & (xs <= end)] = True
    return solid


def artifact_stl(artifact, part, right):
    return os.path.join(artifact, f"kbdkid5-{part}-{'right' if right else 'left'}.stl")


# The room.


def on_half(point, right):
    """A point in the left half's frame in the half's own frame."""
    return layout.mirror_for_right_half(point) if right else tuple(point)


def key_center(key, right):
    return on_half(layout.KEY_CENTERS_MM[key], right)


def empty_cells():
    return numpy.zeros((len(ROOM_YS), len(ROOM_XS)), dtype=bool)


def disc_cells(center, diameter):
    delta_x = ROOM_XS[None, :] - center[0]
    delta_y = ROOM_YS[:, None] - center[1]
    return delta_x * delta_x + delta_y * delta_y <= (diameter / 2.0) ** 2


def convex_polygon_cells(polygon):
    """The cells inside a convex polygon, either winding, worked out over
    its bounding box alone."""
    polygon = list(polygon)
    xs = [point[0] for point in polygon]
    ys = [point[1] for point in polygon]
    columns = numpy.flatnonzero((ROOM_XS >= min(xs) - ROOM_CELL_MM) & (ROOM_XS <= max(xs) + ROOM_CELL_MM))
    rows = numpy.flatnonzero((ROOM_YS >= min(ys) - ROOM_CELL_MM) & (ROOM_YS <= max(ys) + ROOM_CELL_MM))
    window_xs, window_ys = ROOM_XS[columns], ROOM_YS[rows]
    inside_left = numpy.ones((len(rows), len(columns)), dtype=bool)
    inside_right = numpy.ones((len(rows), len(columns)), dtype=bool)
    for start, end in zip(polygon, polygon[1:] + polygon[:1]):
        cross = ((end[0] - start[0]) * (window_ys[:, None] - start[1])
                 - (end[1] - start[1]) * (window_xs[None, :] - start[0]))
        inside_left &= cross >= 0.0
        inside_right &= cross <= 0.0
    cells = empty_cells()
    cells[numpy.ix_(rows, columns)] = inside_left | inside_right
    return cells


def socket_cells(right):
    """The sockets' bodies and tabs (layout.py's cover polygons), which
    hang from the frame's ceiling in their pockets."""
    cells = empty_cells()
    for key in layout.KEY_CENTERS_MM:
        for polygon in layout.socket_polygons(key_center(key, right)):
            cells |= convex_polygon_cells(polygon)
    return cells


def post_and_peg_cells(right):
    cells = empty_cells()
    holes = layout.CHOC_FOOTPRINT_HOLES_MM[:3]
    for key in layout.KEY_CENTERS_MM:
        for (local_center, _), diameter in zip(holes, (POST_DIAMETER_MM, PEG_DIAMETER_MM, PEG_DIAMETER_MM)):
            cells |= disc_cells(layout.footprint_point(key_center(key, right), local_center), diameter)
    return cells


class Room:
    """A half's room, each a grid of cells on ROOM_XS and ROOM_YS (rows
    along ROOM_YS), in the half's own frame from the top."""

    def __init__(self, artifact, right):
        self.right = right
        frame = read_triangles(artifact_stl(artifact, "frame", right))
        turned_ys = NORTH_EDGE_Y_MM - ROOM_YS
        self.frame_body = solid_at(frame, ROOM_XS, turned_ys, FRAME_BODY_Z_MM)
        self.frame_wall_level = empty_cells()
        for z in FRAME_WALL_LEVEL_Z_MM:
            self.frame_wall_level |= solid_at(frame, ROOM_XS, turned_ys, z)
        self.frame_boss_level = solid_at(frame, ROOM_XS, turned_ys, FRAME_BOSS_LEVEL_Z_MM)
        tray = read_triangles(artifact_stl(artifact, "tray", right))
        heights = sorted(set(TRAY_ROOM_Z_MM + TRAY_WIRE_LEVEL_Z_MM + TRAY_FLOOR_Z_MM))
        self.tray = {z: solid_at(tray, ROOM_XS, ROOM_YS, z) for z in heights}
        backing = read_triangles(artifact_stl(artifact, "frame-backing", right))
        self.backing = solid_at(backing, ROOM_XS, ROOM_YS, BACKING_Z_MM)
        self.sockets = socket_cells(right)
        self.posts_and_pegs = post_and_peg_cells(right)

    def frame_below_ceiling(self):
        return self.frame_wall_level | self.frame_boss_level

    def tray_in(self, heights):
        cells = empty_cells()
        for z in heights:
            cells |= self.tray[z]
        return cells

    def switch_parts(self):
        return self.sockets | self.posts_and_pegs

    def plastic(self):
        return self.frame_below_ceiling() | self.tray_in(TRAY_ROOM_Z_MM) | self.switch_parts()


def boss_centers_on_half(right):
    return [on_half(center, right) for center in layout.frame_boss_centers(right)]


def check_bosses(room, artifact):
    """Stop unless the artifact's frame has its bosses where layout.py
    has them, since the squeezes' bounds take the bosses, and the leads
    the opening, from layout.py: each of what the frame has at the
    bosses' level, a ring, centered within 0.2 of one of layout.py's."""
    labels, count = ndimage.label(room.frame_boss_level)
    middles = ndimage.center_of_mass(room.frame_boss_level, labels, range(1, count + 1))
    found = [(ROOM_XS[0] + column * ROOM_CELL_MM, ROOM_YS[0] + row * ROOM_CELL_MM) for row, column in middles]
    expected = boss_centers_on_half(room.right)
    missing = [point for point in expected if not any(math.dist(point, other) < 0.2 for other in found)]
    extra = [point for point in found if not any(math.dist(point, other) < 0.2 for other in expected)]
    if missing or extra:
        sys.exit(f"{artifact}: its {'right' if room.right else 'left'} frame's bosses are not layout.py's"
                 f" (none at {[tuple(round(value, 3) for value in point) for point in missing]},"
                 f" one more near {[tuple(round(value, 1) for value in point) for point in extra]})."
                 " Run on the artifact of the commit checked out.")


# The route.


def column_keys(column):
    if column == COLUMNS:
        return [layout.THUMB_KEY_NAME]
    return [layout.column_key_name(column, row) for row in range(ROWS)]


def row_keys(row):
    keys = [layout.column_key_name(column, row) for column in range(COLUMNS)]
    return keys + [layout.THUMB_KEY_NAME] if row == ROWS - 1 else keys


class DistanceGrid:
    """The distance from the room's plastic on ROUTE_CELL_MM cells, with
    each cell's x and y. A node is a cell's index in the flattened
    grid."""

    def __init__(self, plastic):
        step = int(round(ROUTE_CELL_MM / ROOM_CELL_MM))
        distance = ndimage.distance_transform_edt(~plastic) * ROOM_CELL_MM
        self.distance = distance[::step, ::step]
        self.xs = ROOM_XS[::step]
        self.ys = ROOM_YS[::step]
        self.shape = self.distance.shape
        rows, columns = numpy.mgrid[0:self.shape[0], 0:self.shape[1]]
        self.x = self.xs[columns]
        self.y = self.ys[rows]

    def index(self, point):
        return (int(round((point[1] - self.ys[0]) / ROUTE_CELL_MM)),
                int(round((point[0] - self.xs[0]) / ROUTE_CELL_MM)))

    def point(self, node):
        row, column = divmod(int(node), self.shape[1])
        return (float(self.xs[column]), float(self.ys[row]))

    def near(self, points, radius):
        """The cells within radius of any of the points."""
        mask = numpy.zeros(self.shape, dtype=bool)
        for point in points:
            mask |= numpy.hypot(self.x - point[0], self.y - point[1]) < radius
        return mask

    def near_segment(self, start, end, radius):
        delta_x, delta_y = end[0] - start[0], end[1] - start[1]
        length_squared = delta_x * delta_x + delta_y * delta_y or 1e-12
        fraction = numpy.clip(((self.x - start[0]) * delta_x + (self.y - start[1]) * delta_y) / length_squared,
                              0.0, 1.0)
        return numpy.hypot(self.x - (start[0] + fraction * delta_x),
                           self.y - (start[1] + fraction * delta_y)) < radius

    def near_path(self, points, radius):
        mask = numpy.zeros(self.shape, dtype=bool)
        for start, end in zip(points, points[1:]):
            mask |= self.near_segment(start, end, radius)
        return mask


def neighbour_graph(grid, hard, cost):
    """Each free cell joined to its free neighbours, each edge weighed
    its length times its two cells' mean cost."""
    free = ~hard
    rows, columns = grid.shape
    ids = numpy.arange(rows * columns).reshape(grid.shape)
    sources, targets, weights = [], [], []
    for row_step, column_step in ((0, 1), (1, 0), (1, 1), (1, -1)):
        from_rows, to_rows = slice(0, rows - row_step), slice(row_step, rows)
        if column_step >= 0:
            from_columns, to_columns = slice(0, columns - column_step), slice(column_step, columns)
        else:
            from_columns, to_columns = slice(-column_step, columns), slice(0, columns + column_step)
        both = free[from_rows, from_columns] & free[to_rows, to_columns]
        weight = (math.hypot(row_step, column_step) * ROUTE_CELL_MM * 0.5
                  * (cost[from_rows, from_columns] + cost[to_rows, to_columns]))
        sources.append(ids[from_rows, from_columns][both])
        targets.append(ids[to_rows, to_columns][both])
        weights.append(weight[both])
    size = rows * columns
    return sparse.coo_matrix(
        (numpy.concatenate(weights), (numpy.concatenate(sources), numpy.concatenate(targets))),
        shape=(size, size)).tocsr()


def shortest_paths(grid, hard, cost, start_nodes):
    """(distance, predecessor) of every node from the nearest of the
    start nodes."""
    return csgraph.dijkstra(neighbour_graph(grid, hard, cost), directed=False,
                            indices=sorted(set(start_nodes)), return_predecessors=True, min_only=True)[:2]


def path_to(grid, predecessors, node):
    nodes = [int(node)]
    while predecessors[nodes[-1]] >= 0:
        nodes.append(int(predecessors[nodes[-1]]))
    return [grid.point(item) for item in reversed(nodes)]


def shifted_minimum(field, direction, length):
    """For each cell, the least of field along a segment of length from
    it in direction (cells off the grid count as -inf)."""
    result = field.copy()
    rows, columns = field.shape
    for step in range(1, int(round(length / ROUTE_CELL_MM)) + 1):
        column_shift = int(round(step * direction[0]))
        row_shift = int(round(step * direction[1]))
        shifted = numpy.full(field.shape, -numpy.inf)
        target_rows = slice(max(0, -row_shift), min(rows, rows - row_shift))
        target_columns = slice(max(0, -column_shift), min(columns, columns - column_shift))
        source_rows = slice(max(0, row_shift), min(rows, rows + row_shift))
        source_columns = slice(max(0, column_shift), min(columns, columns + column_shift))
        shifted[target_rows, target_columns] = field[source_rows, source_columns]
        result = numpy.minimum(result, shifted)
    return result


def nodes_near(grid, hard, point):
    """The free nodes within NEAR_TAB_MM of point."""
    rows, columns = numpy.nonzero(grid.near([point], NEAR_TAB_MM) & ~hard)
    return [int(row * grid.shape[1] + column) for row, column in zip(rows, columns)]


def place_diode(grid, tab, forbidden, taken):
    """A diode on the tab at tab: (anode lead path, anode end, cathode
    end, row point) with the shortest lead, a cathode pointing north
    preferred, or None. Its body keeps clear of the forbidden points (the
    other tabs) and of what is taken, and the room it leaves stays one
    region with the row point in it."""
    taken_distance = ndimage.distance_transform_edt(~taken) * ROUTE_CELL_MM
    relaxed = grid.near([tab], NEAR_TAB_MM)
    hard = numpy.where(relaxed, grid.distance < NEAR_TAB_RADIUS_MM, grid.distance < LEAD_RADIUS_MM)
    hard |= taken_distance < LEAD_RADIUS_MM + 0.2
    hard |= grid.near(forbidden, 1.0)
    starts = nodes_near(grid, hard, tab)
    if not starts:
        return None
    lead_distance, predecessors = shortest_paths(grid, hard, numpy.ones(grid.shape), starts)
    lead_distance = lead_distance.reshape(grid.shape)
    body_field = numpy.minimum.reduce([
        grid.distance - (DIODE_RADIUS_MM + 0.15),
        taken_distance - (DIODE_RADIUS_MM + 0.3),
        numpy.where(grid.near(forbidden, DIODE_RADIUS_MM + 1.0), -1.0, 1.0),
    ])
    stub_field = numpy.minimum(grid.distance - LEAD_RADIUS_MM, taken_distance - (LEAD_RADIUS_MM + 0.2))
    candidates = []
    for direction in DIRECTIONS:
        body_fits = shifted_minimum(body_field, direction, DIODE_BODY_MM) >= 0.0
        stub_fits = shifted_minimum(stub_field, direction, DIODE_BODY_MM + CATHODE_STUB_MM) >= 0.0
        bonus = -1.5 if direction == (0.0, 1.0) else (0.8 if direction[0] and direction[1] else 0.0)
        score = numpy.where(body_fits & stub_fits & (lead_distance <= LEAD_REACH_MM) & (lead_distance >= 0.8),
                            lead_distance + bonus, numpy.inf)
        for node in numpy.argsort(score, axis=None)[:40]:
            if math.isfinite(score.flat[node]):
                candidates.append((score.flat[node], int(node), direction))
    candidates.sort()
    open_room = ~(grid.distance < WIRE_RADIUS_MM) & ~(taken_distance < DIODE_RADIUS_MM)
    for _, node, direction in candidates:
        anode = grid.point(node)
        cathode = (anode[0] + DIODE_BODY_MM * direction[0], anode[1] + DIODE_BODY_MM * direction[1])
        row_point = (cathode[0] + CATHODE_STUB_MM * direction[0], cathode[1] + CATHODE_STUB_MM * direction[1])
        lead = path_to(grid, predecessors, node)
        room_left = (open_room & ~grid.near_segment(anode, cathode, DIODE_RADIUS_MM + 0.35)
                     & ~grid.near_path(lead, LEAD_RADIUS_MM + 0.3))
        labels, _count = ndimage.label(room_left)
        sizes = numpy.bincount(labels.ravel())
        sizes[0] = 0
        reached = labels[grid.near([row_point], NEAR_TAB_MM) & room_left]
        if reached.size and sizes[reached].max() == sizes.max():
            return (simplify(lead), anode, cathode, row_point)
    return None


def place_diodes(grid, west_tabs, east_tabs, right):
    """Each key's diode on its west tab (kbdkid4's pad 1), or on its east
    tab where the west one has no room, the keys in the order of their
    left half names. Returns the diodes and each key's column tab, the
    other one."""
    taken = numpy.zeros(grid.shape, dtype=bool)
    diodes = {}
    column_tabs = dict(east_tabs)
    for key in sorted(west_tabs):
        others = list(east_tabs.values()) + [point for name, point in west_tabs.items() if name != key]
        diode = place_diode(grid, west_tabs[key], others, taken)
        if diode is None:
            others = list(west_tabs.values()) + [point for name, point in east_tabs.items() if name != key]
            diode = place_diode(grid, east_tabs[key], others, taken)
            if diode is None:
                print("no diode place for", layout.key_name_on_half(key, right))
                continue
            print("diode on the east tab for", layout.key_name_on_half(key, right))
            column_tabs[key] = west_tabs[key]
        diodes[key] = diode
        lead, anode, cathode, row_point = diode
        taken |= grid.near_segment(anode, cathode, DIODE_RADIUS_MM) | grid.near_path(lead, LEAD_RADIUS_MM)
        taken |= grid.near_segment(cathode, row_point, LEAD_RADIUS_MM)
    return diodes, column_tabs


class Router:
    """The wires routed so far over a grid, and what they cost the next
    one. No wire comes near a diode's body or its anode lead, nor near the
    bare cathode lead of a diode in another row, from the body's end to
    the row point where that row's wire is soldered (hard_for())."""

    def __init__(self, grid, endpoints, diodes, row_nets):
        self.grid = grid
        relaxed = grid.near(endpoints, NEAR_TAB_MM)
        self.hard = numpy.where(relaxed, grid.distance < NEAR_TAB_RADIUS_MM, grid.distance < WIRE_RADIUS_MM)
        for lead, anode, cathode, _row_point in diodes.values():
            self.hard |= grid.near_segment(anode, cathode, DIODE_RADIUS_MM + 0.35)
            self.hard |= grid.near_path(lead, LEAD_RADIUS_MM + 0.3)
        self.cathode_leads = [(row_nets[key], grid.near_segment(cathode, row_point, LEAD_RADIUS_MM + 0.3))
                              for key, (_lead, _anode, cathode, row_point) in diodes.items()]
        self.wires = numpy.zeros(grid.shape, dtype=bool)
        self.wire_distance = numpy.full(grid.shape, numpy.inf)
        self.leads = numpy.zeros(grid.shape, dtype=bool)
        self.lead_distance = numpy.full(grid.shape, numpy.inf)

    def cost(self):
        """Per mm: 1, more within 1.2 of plastic, 10 more under
        SQUEEZE_MM, 6 more within 0.7 of a wire, and half beside a lead
        to the opening, so the leads run together."""
        clearance = numpy.clip(1.2 - self.grid.distance, 0.0, None)
        crowd = numpy.where(self.wire_distance < 0.7, 6.0, 0.0)
        squeeze = numpy.where(self.grid.distance < SQUEEZE_MM, SQUEEZE_COST, 0.0)
        follow = numpy.where((self.lead_distance >= 0.5) & (self.lead_distance < 1.1), 0.5, 1.0)
        return (1.0 + 2.5 * clearance + crowd + squeeze) * follow

    def hard_for(self, net):
        """Where the net's wires cannot go: what no wire can, and the
        cathode leads of the other rows, kept as far as an anode lead."""
        hard = self.hard.copy()
        for row_net, cathode_lead in self.cathode_leads:
            if row_net != net:
                hard |= cathode_lead
        return hard

    def route(self, start_points, target_nodes, net):
        hard = self.hard_for(net)
        starts = []
        for point in start_points:
            starts += nodes_near(self.grid, hard, point)
        if not starts:
            return None
        distances, predecessors = shortest_paths(self.grid, hard, self.cost(), starts)
        best = min(target_nodes, key=lambda node: distances[node])
        if not math.isfinite(distances[best]):
            return None
        return path_to(self.grid, predecessors, best)

    def route_points(self, first, second, net):
        targets = nodes_near(self.grid, self.hard_for(net), second)
        if not targets:
            return None
        path = self.route([first], targets, net)
        return None if path is None else [first] + path + [second]

    def mark(self, points, lead=False):
        self.wires |= self.grid.near_path(points, 0.1)
        self.wire_distance = ndimage.distance_transform_edt(~self.wires) * ROUTE_CELL_MM
        if lead:
            self.leads |= self.grid.near_path(points, 0.1)
            self.lead_distance = ndimage.distance_transform_edt(~self.leads) * ROUTE_CELL_MM


def point_segment_distance(point, start, end):
    delta_x, delta_y = end[0] - start[0], end[1] - start[1]
    length_squared = delta_x * delta_x + delta_y * delta_y
    fraction = 0.0 if length_squared == 0 else max(0.0, min(1.0, (
        (point[0] - start[0]) * delta_x + (point[1] - start[1]) * delta_y) / length_squared))
    return math.dist(point, (start[0] + fraction * delta_x, start[1] + fraction * delta_y))


def simplify(points, tolerance=0.05):
    """Douglas-Peucker."""
    if len(points) < 3:
        return points
    start, end = points[0], points[-1]
    distances = [point_segment_distance(point, start, end) for point in points[1:-1]]
    worst = int(numpy.argmax(distances)) + 1
    if distances[worst - 1] <= tolerance:
        return [start, end]
    return simplify(points[:worst + 1], tolerance)[:-1] + simplify(points[worst:], tolerance)


def path_length(points):
    return sum(math.dist(first, second) for first, second in zip(points, points[1:]))


def opening_on_half(right):
    """The backing's opening for the leads, (x range, y range) in the
    half's own frame."""
    _key, x_range, y_range = layout.frame_backing_opening(right)
    if right:
        x_range = tuple(sorted(2.0 * layout.RIGHT_HALF_MIRROR_X_MM - x for x in x_range))
    return x_range, y_range


def route_chains(router, keys, ends, net, right):
    """A net's chain from key to key along keys, each piece from the
    previous key's end to the next one's."""
    pieces = []
    keys = [key for key in keys if key in ends]
    for first, second in zip(keys, keys[1:]):
        path = router.route_points(ends[first], ends[second], net)
        if path is None:
            print("no route", net, layout.key_name_on_half(first, right), layout.key_name_on_half(second, right))
            continue
        router.mark(path)
        pieces.append(path)
    return pieces


def route_leads(grid, router, routes, column_tabs, right):
    """Each net's lead to the opening, the net farthest from its middle
    first."""
    opening_x, opening_y = opening_on_half(right)
    opening_middle = (sum(opening_x) / 2.0, sum(opening_y) / 2.0)
    net_points = {net: [point for piece in pieces for point in piece] for net, pieces in routes.items()}
    net_points[f"C{COLUMNS}"] = [column_tabs[layout.THUMB_KEY_NAME]]
    inside = ((grid.x >= opening_x[0] + 1.0) & (grid.x <= opening_x[1] - 1.0)
              & (grid.y >= opening_y[0] + 1.0) & (grid.y <= opening_y[1] - 1.0))
    leads = {}
    ends = []
    for net in sorted(net_points, key=lambda net: -min(math.dist(point, opening_middle)
                                                         for point in net_points[net])):
        target_mask = inside & ~router.hard_for(net) & ~grid.near(ends, 1.0)
        path = router.route(net_points[net], [int(node) for node in numpy.flatnonzero(target_mask)], net)
        if path is None:
            print("no lead for", net)
            continue
        router.mark(path, lead=True)
        ends.append(path[-1])
        leads[net] = path
    return leads


def squeezes_along(grid, net, points, own_ends):
    """Each stretch of a path at least SQUEEZE_SAMPLES samples long whose
    center comes nearer than SQUEEZE_MM to plastic, away from its own
    net's ends (own_ends, its tabs or its row points), so that a squeeze
    by another net's tab or row point shows: where it starts and ends,
    how long it is and its least clearance."""
    squeezes = []
    stretch = []

    def close_stretch():
        if len(stretch) >= SQUEEZE_SAMPLES:
            squeezes.append({"net": net, "start": stretch[0][0], "end": stretch[-1][0],
                             "length": len(stretch) * SQUEEZE_STEP_MM,
                             "least": float(min(clearance for _, clearance in stretch))})
        stretch.clear()

    for start, end in zip(points, points[1:]):
        steps = max(1, int(math.dist(start, end) / SQUEEZE_STEP_MM))
        for index in range(steps):
            fraction = index / steps
            point = (start[0] + fraction * (end[0] - start[0]), start[1] + fraction * (end[1] - start[1]))
            row, column = grid.index(point)
            clearance = grid.distance[row, column]
            at_end = any(math.dist(point, other) < NEAR_TAB_MM + 0.3 for other in own_ends)
            if clearance < SQUEEZE_MM and not at_end:
                stretch.append((point, clearance))
            elif stretch:
                close_stretch()
    if stretch:
        close_stretch()
    return squeezes


def route_half(room):
    """The half's route, as written to its JSON but for the squeezes'
    bounds, keys by their names on the half."""
    right = room.right
    grid = DistanceGrid(room.plastic())
    centers = {key: key_center(key, right) for key in layout.KEY_CENTERS_MM}
    east_tabs = {key: (center[0] + EAST_TAB[0], center[1] + EAST_TAB[1]) for key, center in centers.items()}
    west_tabs = {key: (center[0] + WEST_TAB[0], center[1] + WEST_TAB[1]) for key, center in centers.items()}

    diodes, column_tabs = place_diodes(grid, west_tabs, east_tabs, right)
    row_points = {key: diode[3] for key, diode in diodes.items()}
    endpoints = list(column_tabs.values()) + list(row_points.values())
    row_nets = {key: f"R{row}" for row in range(ROWS) for key in row_keys(row)}
    router = Router(grid, endpoints, diodes, row_nets)
    routes = {}
    for column in range(COLUMNS + 1):
        routes[f"C{column}"] = route_chains(router, column_keys(column), column_tabs, f"C{column}", right)
    for row in range(ROWS):
        routes[f"R{row}"] = route_chains(router, row_keys(row), row_points, f"R{row}", right)
    leads = route_leads(grid, router, routes, column_tabs, right)

    own_ends = {f"C{column}": [column_tabs[key] for key in column_keys(column)] for column in range(COLUMNS + 1)}
    own_ends.update({f"R{row}": [row_points[key] for key in row_keys(row) if key in row_points]
                     for row in range(ROWS)})
    squeezes = []
    for net in sorted(routes):
        for piece in routes[net] + ([leads[net]] if net in leads else []):
            squeezes += squeezes_along(grid, net, piece, own_ends[net])

    def named(mapping):
        return {layout.key_name_on_half(key, right): value for key, value in mapping.items()}

    opening_x, opening_y = opening_on_half(right)
    return {
        "right": right,
        "lengths": {net: {"chain": sum(path_length(piece) for piece in routes[net]),
                          "lead": path_length(leads.get(net, []))}
                    for net in sorted(routes)},
        "diodes": named({key: {"lead": lead, "anode": anode, "cathode": cathode, "row_point": row_point}
                         for key, (lead, anode, cathode, row_point) in diodes.items()}),
        "diode_tabs": named({key: (west_tabs if column_tabs[key] == east_tabs[key] else east_tabs)[key]
                             for key in centers}),
        "column_tabs": named(column_tabs),
        "routes": {net: [simplify(piece) for piece in pieces] for net, pieces in routes.items()},
        "leads": {net: simplify(path) for net, path in leads.items()},
        "opening": [list(opening_x), list(opening_y)],
        "squeezes": squeezes,
    }


# What bounds a squeeze, and whether a wire can slip under it: the pocket
# walls end at the socket's height under the ceiling and the posts and
# pegs SWITCH_POSTS_BELOW_PCB_MM under it, both over the backing's top,
# while a boss stands on the backing and a tube on its standoff.
WALL_GAP_MM = (layout.PCB_UNDERSIDE_Z_MM - layout.HOTSWAP_SOCKET_BODY_HEIGHT_MM) - layout.backing_top_z()
POST_GAP_MM = (layout.PCB_UNDERSIDE_Z_MM - layout.SWITCH_POSTS_BELOW_PCB_MM) - layout.backing_top_z()
NOTHING, BOSS, WALL, TUBE, TRAY_TO_CEILING, TRAY_LOW, TRAY, SOCKET, POST, DIODE = range(10)
BOUND_NAMES = (
    "nothing",
    "frame boss (to the backing)",
    f"pocket wall ({WALL_GAP_MM:.3f} over the backing)",
    "tube on its standoff",
    "tray body (to the ceiling)",
    "tray body (low)",
    "tray body",
    "socket or tab",
    f"post or peg ({POST_GAP_MM:.3f} over the backing)",
    "diode body",
)


def boss_cells(right):
    """The frame's bosses at layout.py's places."""
    cells = empty_cells()
    for center in boss_centers_on_half(right):
        cells |= disc_cells(center, layout.STANDOFF_DIAMETER_MM)
    return cells


def tube_cells(right):
    """The frame's tubes in plan, which are their standoffs' tops
    (check_layout.frame_tube_polygon())."""
    cells = empty_cells()
    for center in layout.MOUNTING_DRILL_CENTERS_MM:
        polygon = check_layout.frame_tube_polygon(center, right)
        cells |= convex_polygon_cells([on_half(point, right) for point in polygon])
    return cells


def segment_cells(start, end, radius):
    start, end = numpy.array(start), numpy.array(end)
    from_x = ROOM_XS[None, :] - start[0]
    from_y = ROOM_YS[:, None] - start[1]
    along = end - start
    fraction = numpy.clip((from_x * along[0] + from_y * along[1]) / along.dot(along), 0.0, 1.0)
    across_x = from_x - fraction * along[0]
    across_y = from_y - fraction * along[1]
    return across_x * across_x + across_y * across_y <= radius * radius


def diode_cells(diodes):
    cells = empty_cells()
    for diode in diodes.values():
        cells |= segment_cells(diode["anode"], diode["cathode"], DIODE_RADIUS_MM)
    return cells


def labelled(layers):
    """Each cell labelled with the last of the layers it lies in."""
    labels = numpy.zeros((len(ROOM_YS), len(ROOM_XS)), dtype=int)
    for value, mask in layers:
        labels[mask] = value
    return labels


def bound_labels(room, diodes, tubes, bosses):
    """What stands in the room, across all its heights."""
    return labelled([
        (DIODE, diode_cells(diodes)),
        (POST, room.posts_and_pegs & ~room.sockets),
        (SOCKET, room.sockets),
        (TRAY_LOW, room.tray_in(TRAY_ROOM_Z_MM[:-1])),
        (TRAY_TO_CEILING, room.tray[TRAY_ROOM_Z_MM[-1]]),
        (WALL, room.frame_wall_level),
        (TUBE, tubes & room.frame_wall_level),
        (BOSS, bosses),
    ])


def wire_level_labels(room, diodes, tubes, bosses):
    """What stands at a wire's level when it lies on the backing, or on
    what is under it where the backing is cut out: the pocket walls and
    the posts and pegs left out, since it passes under them."""
    tray = room.tray_in(TRAY_WIRE_LEVEL_Z_MM)
    return labelled([
        (DIODE, diode_cells(diodes)),
        (SOCKET, room.sockets),
        (TRAY, tray),
        (TUBE, tubes & tray),
        (BOSS, bosses),
    ])


def label_at(labels, point):
    column = int(round((point[0] - ROOM_XS[0]) / ROOM_CELL_MM))
    row = int(round((point[1] - ROOM_YS[0]) / ROOM_CELL_MM))
    return labels[row, column]


def cast(labels, point, direction):
    """The distance along direction to the first labelled cell, and its
    label."""
    for step in range(1, int(BOUND_REACH_MM / BOUND_STEP_MM)):
        value = label_at(labels, point + direction * step * BOUND_STEP_MM)
        if value:
            return step * BOUND_STEP_MM, value
    return BOUND_REACH_MM, NOTHING


def narrowest(labels, squeeze):
    """(gap, point, (distance, label) on one side, on the other) where a
    squeeze is narrowest, across it at 11 points along it, or None where
    every point lies in a labelled cell."""
    start, end = numpy.array(squeeze["start"]), numpy.array(squeeze["end"])
    along = end - start
    along = along / numpy.linalg.norm(along)
    best = None
    for fraction in numpy.linspace(0.0, 1.0, 11):
        point = start + (end - start) * fraction
        if label_at(labels, point):
            continue
        for angle in numpy.radians(numpy.arange(-30, 31, 5)):
            turned = numpy.array([along[0] * numpy.cos(angle) - along[1] * numpy.sin(angle),
                                  along[0] * numpy.sin(angle) + along[1] * numpy.cos(angle)])
            normal = numpy.array([-turned[1], turned[0]])
            one_side, other_side = cast(labels, point, normal), cast(labels, point, -normal)
            gap = one_side[0] + other_side[0]
            if best is None or gap < best[0]:
                best = (gap, point, one_side, other_side)
    return best


def floor_at(room, point):
    if label_at(room.backing, point):
        return "backing"
    for z in sorted(TRAY_FLOOR_Z_MM, reverse=True):
        if label_at(room.tray[z], point):
            return f"tray under z {z}"
    return f"open below z {min(TRAY_FLOOR_Z_MM)}"


def bound(found):
    if found is None:
        return None
    gap, point, one_side, other_side = found
    return {"gap": float(gap), "at": [float(value) for value in point],
            "sides": [[BOUND_NAMES[side[1]], float(side[0])] for side in (one_side, other_side)]}


def squeeze_bounds(room, result):
    """Each squeeze's bounds, across it and at a wire's level, added to
    it."""
    tubes = tube_cells(room.right)
    bosses = boss_cells(room.right)
    labels = bound_labels(room, result["diodes"], tubes, bosses)
    wire_level = wire_level_labels(room, result["diodes"], tubes, bosses)
    for squeeze in result["squeezes"]:
        squeeze["across"] = bound(narrowest(labels, squeeze))
        squeeze["at_wire_level"] = bound(narrowest(wire_level, squeeze))
        if squeeze["at_wire_level"] is not None:
            squeeze["at_wire_level"]["floor"] = floor_at(room, squeeze["at_wire_level"]["at"])


def bound_line(found):
    if found is None:
        return "every sample inside an obstacle"
    (one_name, one_distance), (other_name, other_distance) = found["sides"]
    return f"gap {found['gap']:.2f} between {one_name} ({one_distance:.2f}) and {other_name} ({other_distance:.2f})"


def report(result):
    for net, lengths in result["lengths"].items():
        print(f"{net}: chain {lengths['chain']:.0f} mm, lead to the opening {lengths['lead']:.0f} mm")
    for squeeze in result["squeezes"]:
        first, last = squeeze["start"], squeeze["end"]
        print(f"  squeeze {squeeze['net']}: ({first[0]:.1f}, {first[1]:.1f}) to ({last[0]:.1f}, {last[1]:.1f}),"
              f" {squeeze['length']:.1f} mm, least clearance {squeeze['least']:.2f}")
        print(f"    across: {bound_line(squeeze['across'])}")
        wire_level = squeeze["at_wire_level"]
        floor = "" if wire_level is None else f", floor: {wire_level['floor']}"
        print(f"    at the wire's level: {bound_line(wire_level)}{floor}")


# The pictures.

NET_COLOURS = {
    "C0": "#1f77b4", "C1": "#2ca02c", "C2": "#9467bd", "C3": "#8c564b", "C4": "#e377c2",
    "C5": "#17becf", "C6": "#bcbd22",
    "R0": "#d62728", "R1": "#ff7f0e", "R2": "#7f7f00", "R3": "#000000",
}


def draw(room, result, under, title, path):
    """The half's route over its room. From the top in its own frame, or
    its underside as the frame lies upside down, turned about its x axis:
    west stays left, the north edge comes toward you (the bottom of the
    picture)."""
    right = room.right

    def flip(point):
        return (point[0], NORTH_EDGE_Y_MM - point[1]) if under else (point[0], point[1])

    def xy(points):
        flipped = [flip(point) for point in points]
        return [point[0] for point in flipped], [point[1] for point in flipped]

    image = numpy.ones(room.frame_body.shape + (3,))
    image[room.frame_body] = (0.93, 0.93, 0.93)
    image[room.tray_in(TRAY_ROOM_Z_MM)] = (0.72, 0.80, 0.93)
    image[room.switch_parts()] = (0.95, 0.82, 0.82)
    image[room.frame_below_ceiling()] = (0.55, 0.55, 0.55)
    extent = (ROOM_XS[0], ROOM_XS[-1], ROOM_YS[0], ROOM_YS[-1])
    if under:
        image = image[::-1]
        extent = (ROOM_XS[0], ROOM_XS[-1], NORTH_EDGE_Y_MM - ROOM_YS[-1], NORTH_EDGE_Y_MM - ROOM_YS[0])
    figure, axes = pyplot.subplots(figsize=(26, 17))
    axes.imshow(image, origin="lower", extent=extent)

    for key in layout.KEY_CENTERS_MM:
        center = key_center(key, right)
        axes.annotate(layout.key_name_on_half(key, right), flip((center[0] - 2.0, center[1] + 1.0)),
                      color="#333333", fontsize=9, fontweight="bold")
        for polygon in layout.HOTSWAP_SOCKET_TABS_MM:
            corners = numpy.array([flip(point) for point in layout.footprint_polygon(center, polygon)])
            axes.fill(corners[:, 0], corners[:, 1], color="#c8a000", alpha=0.9, zorder=3)

    for net, pieces in result["routes"].items():
        for piece in pieces:
            axes.plot(*xy(piece), color=NET_COLOURS[net], linewidth=2.2, zorder=4)
    for net, lead in result["leads"].items():
        axes.plot(*xy(lead), color=NET_COLOURS[net], linewidth=2.2, linestyle=(0, (4, 1.5)), zorder=4)
        axes.annotate(net, flip(lead[-1]), color=NET_COLOURS[net], fontsize=10, fontweight="bold", zorder=6)

    for diode in result["diodes"].values():
        axes.plot(*xy(diode["lead"] + [diode["anode"]]), color="#b0b0b0", linewidth=1.6, zorder=4)
        axes.plot(*xy([diode["cathode"], diode["row_point"]]), color="#b0b0b0", linewidth=1.6, zorder=4)
        anode, cathode = numpy.array(flip(diode["anode"])), numpy.array(flip(diode["cathode"]))
        along = cathode - anode
        angle = numpy.degrees(numpy.arctan2(along[1], along[0]))
        normal = numpy.array([-along[1], along[0]]) / numpy.linalg.norm(along)
        axes.add_patch(matplotlib.patches.Rectangle(anode - normal * 0.95, numpy.linalg.norm(along), 1.9,
                                                    angle=angle, color="#ff9db0", zorder=5))
        band = anode + along * 0.8 - normal * 0.95
        axes.add_patch(matplotlib.patches.Rectangle(band, numpy.linalg.norm(along) * 0.15, 1.9, angle=angle,
                                                    color="#202020", zorder=5))

    opening_x, opening_y = result["opening"]
    corners = [flip((opening_x[0], opening_y[0])), flip((opening_x[1], opening_y[1]))]
    axes.add_patch(matplotlib.patches.Rectangle(
        (min(corner[0] for corner in corners), min(corner[1] for corner in corners)),
        opening_x[1] - opening_x[0], opening_y[1] - opening_y[0],
        fill=False, edgecolor="#d62728", linewidth=1.5, linestyle="--", zorder=6))

    for squeeze in [item for item in result["squeezes"] if item["least"] < DRAWN_SQUEEZE_MM]:
        middle = flip(((squeeze["start"][0] + squeeze["end"][0]) / 2, (squeeze["start"][1] + squeeze["end"][1]) / 2))
        radius = max(1.5, squeeze["length"] / 2 + 0.8)
        axes.add_patch(matplotlib.patches.Circle(middle, radius, fill=False, edgecolor="red", linewidth=2.0, zorder=7))

    handles = [matplotlib.lines.Line2D([], [], color=NET_COLOURS[net], linewidth=2.5, label=net)
               for net in sorted(NET_COLOURS)]
    handles.append(matplotlib.lines.Line2D([], [], color="#555555", linewidth=2.5, linestyle=(0, (4, 1.5)),
                                           label="lead to the opening"))
    handles.append(matplotlib.patches.Patch(color="#ff9db0", label="1N4148, black end = band (cathode)"))
    handles.append(matplotlib.patches.Patch(color="#c8a000", label="socket tab"))
    handles.append(matplotlib.lines.Line2D([], [], color="#b0b0b0", linewidth=2, label="diode's own lead"))
    handles.append(matplotlib.patches.Circle((0, 0), 1, fill=False, edgecolor="red",
                                             label=f"squeeze: wire center under {DRAWN_SQUEEZE_MM} from plastic"))
    handles.append(matplotlib.patches.Patch(fill=False, edgecolor="#d62728", linestyle="--",
                                            label="backing opening (item 028)"))
    axes.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=12)
    axes.set_title(title, fontsize=16)
    axes.set_aspect("equal")
    axes.set_xticks(numpy.arange(0, 135, 10))
    axes.set_yticks(numpy.arange(0, 85, 10))
    axes.grid(True, alpha=0.25)
    figure.savefig(path, dpi=90, bbox_inches="tight")
    pyplot.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("artifact", help="the folder of a kbdkid5-<short commit hash> artifact's STLs")
    parser.add_argument("half", nargs="?", choices=[name for name, _ in HALVES], help="one half only")
    arguments = parser.parse_args()
    artifact = os.path.normpath(arguments.artifact)
    source = os.path.basename(artifact)
    os.makedirs(OUTPUT, exist_ok=True)
    for name, right in HALVES:
        if arguments.half not in (None, name):
            continue
        print(f"== {name} half, {source}")
        room = Room(artifact, right)
        check_bosses(room, artifact)
        result = route_half(room)
        squeeze_bounds(room, result)
        result["artifact"] = source
        report(result)
        with open(os.path.join(OUTPUT, f"{name}.json"), "w") as stream:
            json.dump(result, stream, indent=1)
        half = name.capitalize()
        draw(room, result, False, f"{half} half from the top ({source})",
             os.path.join(OUTPUT, f"{name}-top.png"))
        draw(room, result, True, f"{half} half underside: the frame upside down, turned toward you"
             f" (north edge at the bottom, west still on the left), {source}",
             os.path.join(OUTPUT, f"{name}-underside.png"))


if __name__ == "__main__":
    main()
