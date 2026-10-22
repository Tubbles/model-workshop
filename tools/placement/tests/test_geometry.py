"""The exact measures on shapes with known answers."""

import math
import unittest

from shapely.geometry import Polygon

from placement import geometry
from placement.geometry import Circle, Convex, Outline

SQUARE = ((-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0))
L_SHAPE = ((0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (2.0, 2.0), (2.0, 4.0), (0.0, 4.0))
# A square with a slit 0.2 wide from its north edge down to y 2.
SLIT = ((0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (5.1, 10.0), (5.1, 2.0), (4.9, 2.0), (4.9, 10.0),
        (0.0, 10.0))


class MeasureTest(unittest.TestCase):
    def test_circle_from_circle(self):
        found = geometry.measure(Circle((0.0, 0.0), 1.0), Circle((5.0, 0.0), 2.0))
        self.assertAlmostEqual(found.value, 2.0)
        self.assertEqual(found.feature_point, (1.0, 0.0))
        self.assertEqual(found.obstacle_point, (3.0, 0.0))

    def test_circle_inside_circle(self):
        found = geometry.measure(Circle((1.0, 0.0), 1.0), Circle((0.0, 0.0), 3.0), inside=True)
        self.assertAlmostEqual(found.value, 1.0)

    def test_circle_from_convex_outside_and_inside(self):
        outside = geometry.measure(Circle((3.0, 0.5), 0.5), Convex(SQUARE))
        self.assertAlmostEqual(outside.value, 1.5)
        self.assertEqual(outside.obstacle_point, (1.0, 0.5))
        inside = geometry.measure(Circle((0.5, 0.0), 0.25), Convex(SQUARE))
        self.assertAlmostEqual(inside.value, -0.75)

    def test_circle_inside_concave_outline(self):
        # Near the reflex corner (2, 2) the distance is to the vertex.
        found = geometry.measure(Circle((1.5, 1.5), 0.25), Outline(L_SHAPE), inside=True)
        self.assertAlmostEqual(found.value, math.hypot(0.5, 0.5) - 0.25)
        self.assertEqual(found.obstacle_point, (2.0, 2.0))

    def test_circle_from_concave_outline(self):
        found = geometry.measure(Circle((3.0, 3.0), 0.5), Outline(L_SHAPE))
        # In the L's notch, a unit from both of its inner edges.
        self.assertAlmostEqual(found.value, 1.0 - 0.5)

    def test_polygons_apart_at_angles_against_shapely(self):
        bar = Convex(((-1.5, -0.25), (1.5, -0.25), (1.5, 0.25), (-1.5, 0.25)))
        gaps_differ = False
        for x, y, angle in ((3.0, 3.0, 0.0), (3.5, -2.0, 30.0), (-2.5, 3.0, 45.0),
                            (0.5, -4.0, 10.0), (4.0, 1.0, 70.0)):
            placed = geometry.placed(bar, x, y, angle)
            found = geometry.measure(placed, Convex(SQUARE))
            expected = Polygon(placed.points).distance(Polygon(SQUARE))
            self.assertGreater(expected, 0.0)
            self.assertAlmostEqual(found.value, expected, places=12)
            self.assertAlmostEqual(math.dist(found.feature_point, found.obstacle_point), expected,
                                   places=12)
            gap = geometry.separating_gap(placed.points, SQUARE)
            gaps_differ = gaps_differ or abs(gap - expected) > 0.01
        self.assertTrue(gaps_differ)

    def test_polygons_apart_and_overlapping(self):
        apart = geometry.measure(geometry.placed(Convex(SQUARE), 3.0, 0.0), Convex(SQUARE))
        self.assertAlmostEqual(apart.value, 1.0)
        overlapping = geometry.measure(geometry.placed(Convex(SQUARE), 1.5, 0.25), Convex(SQUARE))
        self.assertAlmostEqual(overlapping.value, -0.5)

    def test_polygon_inside_region_and_circle(self):
        inner = geometry.placed(Convex(((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))),
                                0.25, 0.0)
        self.assertAlmostEqual(geometry.measure(inner, Convex(SQUARE), inside=True).value, 0.25)
        poking = geometry.placed(inner, 0.5, 0.0)
        self.assertAlmostEqual(geometry.measure(poking, Convex(SQUARE), inside=True).value, -0.25)
        in_circle = geometry.measure(inner, Circle((0.0, 0.0), 2.0), inside=True)
        self.assertAlmostEqual(in_circle.value, 2.0 - math.hypot(0.75, 0.5))

    def test_a_slit_across_a_polygon_breaks_its_containment(self):
        across = Convex(((3.0, 4.0), (7.0, 4.0), (7.0, 6.0), (3.0, 6.0)))
        # The slit's walls reach 1.0 deep into the polygon, at y 5,
        # whichever way round its points go.
        for feature in (across, Convex(tuple(reversed(across.points)))):
            found = geometry.measure(feature, Outline(SLIT), inside=True)
            self.assertAlmostEqual(found.value, -1.0)
            self.assertAlmostEqual(found.obstacle_point[1], 5.0)
        beside = geometry.placed(across, -2.5, 0.0)
        clear = geometry.measure(beside, Outline(SLIT), inside=True)
        self.assertAlmostEqual(clear.value, 0.4)
        self.assertAlmostEqual(clear.value,
                               Polygon(SLIT).exterior.distance(Polygon(beside.points)))

    def test_a_keyhole_pokes_out_by_a_lower_bound(self):
        # A room around the square's middle (5, 5), 5 from its edges,
        # reached by a channel 0.2 wide: the room's walls lie 3 deep.
        square = Convex(((0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)))
        keyhole = Outline(((-1.0, -1.0), (4.9, -1.0), (4.9, 3.0), (3.0, 3.0), (3.0, 7.0),
                           (7.0, 7.0), (7.0, 3.0), (5.1, 3.0), (5.1, -1.0), (11.0, -1.0),
                           (11.0, 11.0), (-1.0, 11.0)))
        found = geometry.measure(square, keyhole, inside=True)
        self.assertAlmostEqual(found.value, -3.0)

    def test_repeated_and_collinear_vertices_are_dropped(self):
        # As shapely gives a ring, its first point again at its end, and
        # a vertex midway along an edge.
        closed = Convex(SQUARE + (SQUARE[0],))
        midway = Outline(((-1.0, -1.0), (0.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)))
        for shape in (closed, midway):
            self.assertEqual(set(shape.points), set(SQUARE))
        found = geometry.measure(geometry.placed(Convex(SQUARE), 3.0, 0.0), closed)
        self.assertAlmostEqual(found.value, 1.0)
        inner = Convex(((-0.5, -0.5), (0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)))
        self.assertAlmostEqual(geometry.measure(inner, closed, inside=True).value, 0.5)
        for points in (((0.0, 0.0), (1.0, 0.0), (2.0, 0.0)), ((0.0, 0.0), (1.0, 1.0), (0.0, 0.0)),
                       ((0.0, 0.0), (2.0, 0.0), (1.0, 0.0), (3.0, 0.0))):
            with self.subTest(points=points), self.assertRaises(ValueError):
                Convex(points)

    def test_a_slit_of_no_width_stays(self):
        # The slit's end folds back on its line: the vertex bounds the
        # slit, which runs up through the feature's middle at x 2.
        slit = ((0.0, 0.0), (2.0, 0.0), (2.0, 3.0), (2.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0))
        self.assertEqual(Outline(slit).points, slit)
        feature = Convex(((1.0, 1.0), (3.0, 1.0), (3.0, 2.0), (1.0, 2.0)))
        self.assertAlmostEqual(geometry.measure(feature, Outline(slit), inside=True).value, -0.5)

    def test_turned_placement(self):
        bar = Convex(((-2.0, -0.1), (2.0, -0.1), (2.0, 0.1), (-2.0, 0.1)))
        upright = geometry.placed(bar, 1.0, 1.0, 90.0)
        xs = [x for x, _ in upright.points]
        ys = [y for _, y in upright.points]
        self.assertAlmostEqual(max(xs) - min(xs), 0.2)
        self.assertAlmostEqual(max(ys) - min(ys), 4.0)
        self.assertAlmostEqual(min(ys), -1.0)

    def test_heights(self):
        self.assertAlmostEqual(geometry.z_overlap((5.0, 6.5), (3.5, 5.25)), 0.25)
        self.assertAlmostEqual(geometry.z_separation((5.0, 6.5), (3.5, 5.25)), -0.25)
        self.assertAlmostEqual(geometry.z_separation((6.0, 7.0), (1.0, 5.0)), 1.0)
        self.assertIsNone(geometry.z_overlap(None, (0.0, 1.0)))

    def test_polygon_from_outline_is_refused(self):
        with self.assertRaises(ValueError):
            geometry.measure(Convex(SQUARE), Outline(L_SHAPE))

    def test_an_outline_feature_is_measured_against_circles_alone(self):
        notch = geometry.measure(Outline(L_SHAPE), Circle((3.0, 3.0), 0.5))
        self.assertAlmostEqual(notch.value, 0.5)
        held = geometry.measure(Outline(L_SHAPE), Circle((2.0, 2.0), 3.0), inside=True)
        self.assertAlmostEqual(held.value, 3.0 - math.hypot(2.0, 2.0))
        # In the L's notch, 1.0 from it, where its hull would overlap.
        in_notch = Convex(((3.0, 3.0), (4.0, 3.0), (4.0, 4.0), (3.0, 4.0)))
        for inside in (False, True):
            with self.subTest(inside=inside), self.assertRaises(ValueError):
                geometry.measure(Outline(L_SHAPE), in_notch, inside)


if __name__ == "__main__":
    unittest.main()
