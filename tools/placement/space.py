"""The configuration space map of a part that only translates, one per
context, with shapely: each rule instance's obstacle grown by the
feature's radius and the rule's minimum (for INSIDE, its region shrunk
by them), shifted by the feature's offset in the part, and the free
region the window less their union. Arcs are polygons of QUAD_SEGMENTS
per quarter circle, so a map finds answers and the exact measures
(geometry.py) check them.

A map leaves out the MERGE rules, which hold no plan region, and the
instances a Conditional may stand in for, whose margin is the
project's function rather than a shape: so the free region may be too
large there, and the solver checks the answer with every rule."""

import dataclasses
import math

import shapely
import shapely.affinity
import shapely.ops
from shapely.geometry import Point, Polygon, box

from placement import geometry
from placement.problem import INSIDE, MERGE, free_degrees

QUAD_SEGMENTS = 64
# How far inside an arc its polygon's chords come, per unit of radius.
ARC_SAGITTA = 1.0 - math.cos(math.pi / (4 * QUAD_SEGMENTS))


@dataclasses.dataclass(frozen=True)
class Map:
    """A part's free region in one context, with the configuration
    space obstacles of the CLEAR rules and the regions the INSIDE rules
    allow, each as (rule name, geometry)."""

    part: str
    context: str
    window: tuple
    free: object
    blocked: tuple
    allowed: tuple


def mappable(part):
    """Whether a part's answer comes from a map: it moves in x and y
    alone and its features are circles."""
    return (set(free_degrees(part)) == {"x", "y"}
            and all(isinstance(feature.prism.shape, geometry.Circle) for feature in part.features))


def grown(shape, distance):
    """A shape's region grown by distance, shrunk for a negative one."""
    if isinstance(shape, geometry.Circle):
        radius = shape.radius + distance
        if radius <= 0.0:
            return Polygon()
        return Point(shape.center).buffer(radius, quad_segs=QUAD_SEGMENTS)
    return Polygon(shape.points).buffer(distance, quad_segs=QUAD_SEGMENTS)


def arc_error(shape, reach):
    """The most grown(shape, reach)'s polygon lies off its arcs, twice
    over, as the arcs' radius may grow a little with a loosened reach."""
    radius = abs(reach) + (shape.radius if isinstance(shape, geometry.Circle) else 0.0)
    return 2.0 * ARC_SAGITTA * radius


def instance_region(instance, angle, slack=0.0):
    """Where the part's origin puts the feature against the obstacle:
    for CLEAR the region that breaks the rule, for INSIDE the region
    that keeps it. A slack loosens the rule by that much more than its
    arcs' polygons are off (arc_error()), so the region holds every pose
    within the slack of keeping the rule."""
    shape = instance.obstacle.prism.shape
    feature = instance.feature.prism.shape
    offset = geometry.turned(feature.center, angle)
    reach = feature.radius + instance.rule.minimum
    if slack > 0.0:
        reach -= slack + arc_error(shape, reach)
    sign = -1.0 if instance.rule.relation == INSIDE else 1.0
    region = grown(shape, sign * reach)
    return shapely.affinity.translate(region, -offset[0], -offset[1])


def mapped(instance):
    return instance.rule.relation != MERGE and instance.conditional is None


def context_map(part, context, instances, window, slack=0.0):
    """The part's Map in one context from its instances there, each
    rule loosened by slack (instance_region())."""
    chosen = [instance for instance in instances
              if instance.context == context and instance.obstacle is not None and mapped(instance)]
    blocked = tuple((instance.rule.name, instance_region(instance, part.start.angle, slack))
                    for instance in chosen if instance.rule.relation != INSIDE)
    allowed = tuple((instance.rule.name, instance_region(instance, part.start.angle, slack))
                    for instance in chosen if instance.rule.relation == INSIDE)
    free = box(*window)
    for _name, region in allowed:
        free = free.intersection(region)
    free = free.difference(shapely.union_all([region for _name, region in blocked]))
    return Map(part.name, context, window, polygonal(free), blocked, allowed)


def polygon_pieces(geometry):
    """The polygons in a geometry, collections opened, the lines and
    points an intersection leaves where two edges meet left out."""
    if isinstance(geometry, Polygon):
        return [] if geometry.is_empty else [geometry]
    return [piece for part in getattr(geometry, "geoms", ()) for piece in polygon_pieces(part)]


def polygonal(geometry):
    """A geometry's polygons alone, as one MultiPolygon: a free region
    of no area is nowhere a part can go."""
    return shapely.MultiPolygon(polygon_pieces(geometry))


def within_reach(part, region, slack=0.0):
    """A free region less where the part's origin lies beyond its reach
    of its target, the region itself for a part with no reach or no
    target. The reach's circle is a polygon inside it, or with a slack
    one that much larger beyond its arcs' error (arc_error())."""
    if part.reach is None or part.target is None:
        return region
    center = geometry.Circle((part.target.x, part.target.y), 0.0)
    reach = part.reach
    if slack > 0.0:
        reach += slack + arc_error(center, reach)
    return polygonal(region.intersection(grown(center, reach)))


def free_region(maps):
    """Where the part is free in every context at once."""
    free = maps[0].free
    for other in maps[1:]:
        free = free.intersection(other.free)
    return polygonal(free)


def nearest_free(free, point):
    """The free point nearest a point, the point itself where it is
    free, None where nothing is."""
    if free.is_empty:
        return None
    if free.covers(Point(point)):
        return tuple(point)
    nearest, _ = shapely.ops.nearest_points(free, Point(point))
    return (nearest.x, nearest.y)


def pockets(free):
    """The free region's separate pieces, largest first."""
    return sorted(polygon_pieces(free), key=lambda piece: -piece.area)


def inscribed_circle(piece):
    """((x, y), radius) of the largest circle in one pocket."""
    line = shapely.maximum_inscribed_circle(piece)
    center, edge = line.coords[0], line.coords[1]
    return ((center[0], center[1]), Point(center).distance(Point(edge)))


def most_clearance(free):
    """((x, y), radius) of the largest circle in the free region,
    whichever pocket holds it (not always the largest by area): the
    point farthest from every rule's configuration space obstacle and
    from the window's edges. None where nothing is free."""
    circles = [inscribed_circle(piece) for piece in pockets(free)]
    return max(circles, key=lambda circle: circle[1], default=None)
