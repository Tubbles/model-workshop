"""Exact plane geometry: the shapes a placement problem is built from
and the distances between them. Every margin the solver reports comes
from here. Shapely's polygons, whose arcs are approximated (space.py),
only find answers.

A shape is a Circle, a Convex polygon or an Outline, a simple polygon
that may be concave. As an obstacle each stands for the region it
bounds. Points are (x, y) tuples and polygons tuples of points in
either orientation. A Measure is how far a placed feature keeps from
an obstacle, negative by how much they overlap, or with inside how far
it stays inside one, negative by how much it pokes out, with the pair
of points it was measured between."""

import dataclasses
import itertools
import math


@dataclasses.dataclass(frozen=True)
class Circle:
    center: tuple
    radius: float


@dataclasses.dataclass(frozen=True)
class Convex:
    """A convex polygon, its points cleaned() as it is made."""

    points: tuple

    def __post_init__(self):
        object.__setattr__(self, "points", cleaned(self.points))


@dataclasses.dataclass(frozen=True)
class Outline:
    """A simple polygon, concave or not, its points cleaned() as it is
    made."""

    points: tuple

    def __post_init__(self):
        object.__setattr__(self, "points", cleaned(self.points))


@dataclasses.dataclass(frozen=True)
class Measure:
    value: float
    feature_point: tuple
    obstacle_point: tuple


def vector_between(start, end):
    return (end[0] - start[0], end[1] - start[1])


def dot(first, second):
    return first[0] * second[0] + first[1] * second[1]


def cross(first, second):
    return first[0] * second[1] - first[1] * second[0]


def edges(points):
    count = len(points)
    return [(points[index], points[(index + 1) % count]) for index in range(count)]


def bounds_nothing(points, index):
    """Whether a polygon's vertex repeats the one before it or lies
    between its neighbours on one straight edge. A vertex where the
    boundary folds back on its line, the end of a slit of no width,
    bounds the slit."""
    before, point, after = points[index - 1], points[index], points[(index + 1) % len(points)]
    coming, going = vector_between(before, point), vector_between(point, after)
    return point == before or (cross(coming, going) == 0.0 and dot(coming, going) > 0.0)


def cleaned(points):
    """A polygon's points less the vertices that bound nothing
    (bounds_nothing()), such as shapely's closing point that repeats
    the first, since an edge of no length has no normal. The region and
    its boundary stay the same. A ValueError where they enclose no
    area."""
    kept = [tuple(point) for point in points]
    while len(kept) >= 3:
        index = next((index for index in range(len(kept)) if bounds_nothing(kept, index)), None)
        if index is None:
            break
        del kept[index]
    if len(kept) < 3 or signed_area(kept) == 0.0:
        raise ValueError(f"a polygon needs three corners off one line, not {tuple(points)}")
    return tuple(kept)


def closest_on_segment(point, start, end):
    """The point of a segment nearest a point."""
    segment = vector_between(start, end)
    length_squared = dot(segment, segment)
    if length_squared == 0.0:
        return start
    parameter = dot(vector_between(start, point), segment) / length_squared
    parameter = max(0.0, min(1.0, parameter))
    return (start[0] + parameter * segment[0], start[1] + parameter * segment[1])


def closest_on_boundary(point, points):
    """(distance, nearest point) from a point to a polygon's boundary."""
    nearest = [closest_on_segment(point, start, end) for start, end in edges(points)]
    return min(((math.dist(point, closest), closest) for closest in nearest),
               key=lambda pair: pair[0])


def contains(point, points):
    """Whether a point lies inside a polygon, by ray casting: a point on
    the boundary may land on either side."""
    inside = False
    for start, end in edges(points):
        if (start[1] > point[1]) != (end[1] > point[1]):
            fraction = (point[1] - start[1]) / (end[1] - start[1])
            if point[0] < start[0] + fraction * (end[0] - start[0]):
                inside = not inside
    return inside


def region_distance(point, points):
    """(signed distance, nearest boundary point) from a point to the
    region a polygon bounds: positive outside, negative inside."""
    distance, closest = closest_on_boundary(point, points)
    return (-distance if contains(point, points) else distance), closest


def along(start, toward, length):
    """The point length from start on the line to toward, away from it
    for a negative length, start itself where the two coincide."""
    distance = math.dist(start, toward)
    if distance == 0.0:
        return start
    scale = length / distance
    return (start[0] + scale * (toward[0] - start[0]), start[1] + scale * (toward[1] - start[1]))


def turned(point, angle):
    """A point turned about the origin by angle degrees, counter-clockwise."""
    if angle == 0.0:
        return point
    cosine, sine = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    return (cosine * point[0] - sine * point[1], sine * point[0] + cosine * point[1])


def placed_point(point, x, y, angle=0.0):
    turned_point = turned(point, angle)
    return (turned_point[0] + x, turned_point[1] + y)


def placed(shape, x, y, angle=0.0):
    """A shape given in a part's frame, the part at (x, y) turned by
    angle degrees."""
    if isinstance(shape, Circle):
        return Circle(placed_point(shape.center, x, y, angle), shape.radius)
    moved = tuple(placed_point(point, x, y, angle) for point in shape.points)
    return dataclasses.replace(shape, points=moved)


def circle_from_circle(feature, obstacle):
    distance = math.dist(feature.center, obstacle.center)
    return Measure(distance - feature.radius - obstacle.radius,
                   along(feature.center, obstacle.center, feature.radius),
                   along(obstacle.center, feature.center, obstacle.radius))


def circle_inside_circle(feature, obstacle):
    distance = math.dist(feature.center, obstacle.center)
    return Measure(obstacle.radius - distance - feature.radius,
                   along(feature.center, obstacle.center, -feature.radius),
                   along(obstacle.center, feature.center, obstacle.radius))


def circle_from_region(feature, points):
    """A circle's clearance from a polygon's region, exact for any simple
    polygon: the center's signed distance less the radius."""
    distance, closest = region_distance(feature.center, points)
    reach = feature.radius if distance >= 0.0 else -feature.radius
    return Measure(distance - feature.radius, along(feature.center, closest, reach), closest)


def circle_inside_region(feature, points):
    distance, closest = region_distance(feature.center, points)
    reach = feature.radius if distance <= 0.0 else -feature.radius
    return Measure(-distance - feature.radius, along(feature.center, closest, reach), closest)


def separating_gap(first, second):
    """The widest gap between two convex polygons' projections on any
    edge normal: positive when they are apart, else the negative of
    their least overlap, which for convex polygons is the depth they
    overlap by."""
    best = -math.inf
    for polygon in (first, second):
        for start, end in edges(polygon):
            edge = vector_between(start, end)
            length = math.hypot(*edge)
            axis = (edge[1] / length, -edge[0] / length)
            first_values = [dot(point, axis) for point in first]
            second_values = [dot(point, axis) for point in second]
            best = max(best, min(second_values) - max(first_values),
                       min(first_values) - max(second_values))
    return best


def segment_crossing(first_start, first_end, second_start, second_end):
    """Where two segments cross at a point inside both, or None."""
    first = vector_between(first_start, first_end)
    second = vector_between(second_start, second_end)
    denominator = cross(first, second)
    if denominator == 0.0:
        return None
    offset = vector_between(first_start, second_start)
    first_parameter = cross(offset, second) / denominator
    second_parameter = cross(offset, first) / denominator
    if 0.0 < first_parameter < 1.0 and 0.0 < second_parameter < 1.0:
        return (first_start[0] + first_parameter * first[0],
                first_start[1] + first_parameter * first[1])
    return None


def closest_between_boundaries(first, second):
    """(distance, point on the first, point on the second) between two
    polygons' boundaries: zero where they cross, else at a vertex of
    one of them, as for any two segments in the plane that do not
    cross."""
    for first_start, first_end in edges(first):
        for second_start, second_end in edges(second):
            crossing = segment_crossing(first_start, first_end, second_start, second_end)
            if crossing is not None:
                return (0.0, crossing, crossing)
    candidates = [(distance, vertex, closest) for vertex in first
                  for distance, closest in [closest_on_boundary(vertex, second)]]
    candidates += [(distance, closest, vertex) for vertex in second
                   for distance, closest in [closest_on_boundary(vertex, first)]]
    return min(candidates, key=lambda candidate: candidate[0])


def polygon_from_polygon(feature_points, obstacle_points):
    """A convex polygon's clearance from a convex polygon."""
    gap = separating_gap(feature_points, obstacle_points)
    distance, feature_point, obstacle_point = closest_between_boundaries(feature_points,
                                                                         obstacle_points)
    return Measure(gap if gap < 0.0 else distance, feature_point, obstacle_point)


def polygon_from_circle(feature_points, obstacle):
    distance, closest = region_distance(obstacle.center, feature_points)
    reach = obstacle.radius if distance >= 0.0 else -obstacle.radius
    return Measure(distance - obstacle.radius, closest, along(obstacle.center, closest, reach))


def polygon_inside_circle(feature_points, obstacle):
    farthest = max(feature_points, key=lambda point: math.dist(point, obstacle.center))
    return Measure(obstacle.radius - math.dist(farthest, obstacle.center), farthest,
                   along(obstacle.center, farthest, obstacle.radius))


def signed_area(points):
    return sum(cross(start, end) for start, end in edges(points)) / 2.0


def inward_lines(points):
    """(unit normal, offset) of each edge of a convex polygon, the normal
    pointing in: dot(normal, point) - offset is how far a point lies
    inside that edge's line, and the least of them over the edges is a
    point's depth inside the polygon."""
    turn = 1.0 if signed_area(points) > 0.0 else -1.0
    lines = []
    for start, end in edges(points):
        edge = vector_between(start, end)
        length = math.hypot(*edge)
        normal = (-turn * edge[1] / length, turn * edge[0] / length)
        lines.append((normal, dot(normal, start)))
    return lines


def deepest_on_segment(start, end, lines):
    """(depth, point) of the point of a segment deepest inside a convex
    polygon, by its inward_lines(). Along the segment each line's depth
    is linear and the polygon's is their least, so the deepest point is
    an end or where two lines' depths cross."""
    segment = vector_between(start, end)
    pieces = [(dot(normal, start) - offset, dot(normal, segment)) for normal, offset in lines]
    parameters = {0.0, 1.0}
    for (first_value, first_slope), (second_value, second_slope) in itertools.combinations(
            pieces, 2):
        if first_slope != second_slope:
            parameter = (second_value - first_value) / (first_slope - second_slope)
            if 0.0 < parameter < 1.0:
                parameters.add(parameter)

    def depth(parameter):
        return min(value + slope * parameter for value, slope in pieces)

    deepest = max(parameters, key=depth)
    return depth(deepest), (start[0] + deepest * segment[0], start[1] + deepest * segment[1])


def polygon_inside_region(feature_points, points):
    """How far a convex polygon stays inside a simple polygon's region:
    where it is inside, the distance between the boundaries, which then
    do not cross. Where it pokes out, the negative of the deeper of its
    corner farthest out of the region and the point of the region's
    boundary deepest inside it (a notch's corner, or a slit across it).
    That depth is a lower bound on how far it pokes out, not the exact
    depth: the outside can reach deeper into the polygon than its
    boundary does, as a room around the polygon's middle through a
    narrow channel. The sign is exact, and the value is zero exactly
    where the two touch."""
    (outward, closest), corner = max(((region_distance(corner, points), corner)
                                      for corner in feature_points), key=lambda item: item[0][0])
    lines = inward_lines(feature_points)
    inward, point = max((deepest_on_segment(start, end, lines) for start, end in edges(points)),
                        key=lambda item: item[0])
    if max(outward, inward) <= 0.0:
        distance, feature_point, obstacle_point = closest_between_boundaries(feature_points,
                                                                             points)
        return Measure(distance, feature_point, obstacle_point)
    if outward >= inward:
        return Measure(-outward, corner, closest)
    return Measure(-inward, closest_on_boundary(point, feature_points)[1], point)


def measure(feature, obstacle, inside=False):
    """How far a placed feature keeps from an obstacle, or with inside
    how far it stays inside it. A Circle feature is measured against any
    obstacle and any polygon feature against a Circle. A Convex feature
    is measured inside a polygon and clear of a Convex one. The rest, a
    Convex feature's clearance from an Outline and an Outline feature
    against any polygon, raise a ValueError."""
    if isinstance(feature, Circle):
        if isinstance(obstacle, Circle):
            return (circle_inside_circle if inside else circle_from_circle)(feature, obstacle)
        return (circle_inside_region if inside else circle_from_region)(feature, obstacle.points)
    if isinstance(obstacle, Circle):
        return (polygon_inside_circle if inside else polygon_from_circle)(feature.points, obstacle)
    if isinstance(feature, Outline):
        raise ValueError("an Outline feature is measured against a Circle alone")
    if inside:
        return polygon_inside_region(feature.points, obstacle.points)
    if isinstance(obstacle, Outline):
        raise ValueError("a polygon feature's clearance from a concave outline is not measured")
    return polygon_from_polygon(feature.points, obstacle.points)


def bounding_box(shape):
    """(low x, low y, high x, high y) of a shape."""
    if isinstance(shape, Circle):
        (x, y), radius = shape.center, shape.radius
        return (x - radius, y - radius, x + radius, y + radius)
    xs = [x for x, _ in shape.points]
    ys = [y for _, y in shape.points]
    return (min(xs), min(ys), max(xs), max(ys))


def box_gap(first, second):
    """How far two boxes keep apart, zero where they meet."""
    across = max(first[0] - second[2], second[0] - first[2], 0.0)
    along_y = max(first[1] - second[3], second[1] - first[3], 0.0)
    return math.hypot(across, along_y)


def reach(shape):
    """How far a shape in a part's frame reaches from its origin, at any
    angle."""
    if isinstance(shape, Circle):
        return math.hypot(*shape.center) + shape.radius
    return max(math.hypot(*point) for point in shape.points)


def z_overlap(first, second):
    """How far two z ranges overlap, negative by their gap, None where
    either is None, every height."""
    if first is None or second is None:
        return None
    return min(first[1], second[1]) - max(first[0], second[0])


def z_separation(first, second):
    """How far two z ranges keep apart, negative by the least move along
    z that parts them, None where either is every height."""
    if first is None or second is None:
        return None
    return max(first[0] - second[1], second[0] - first[1])


def shifted(z_range, offset):
    return None if z_range is None else (z_range[0] + offset, z_range[1] + offset)
