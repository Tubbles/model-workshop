"""solve() on synthetic problems with known answers, no project
imported."""

import dataclasses
import json
import math
import os
import tempfile
import unittest
from unittest import mock

import numpy

from placement import evaluate
from placement import solver as solve_module
from placement import (CLEAR, INSIDE, LEAST_MOVE, MERGE, MOST_CLEARANCE, NEAREST, Alternatives,
                       Circle, Conditional, Convex, Feature, Obstacle, Option, Outline, PairRule,
                       Part, Pose, Prism, Problem, Rule, SharedVariable, Term, explain,
                       free_heights, least_lift, picture, problem_json, report_json, report_text,
                       solve)
from placement.report import merge_text
from shapely.geometry import MultiPolygon

SQUARE = ((-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0))


def disc(name, radius, z_range=None, center=(0.0, 0.0)):
    return Feature(name, Prism(Circle(center, radius), z_range))


def around(target, reach):
    return (("x", target.x - reach, target.x + reach), ("y", target.y - reach, target.y + reach))


def one_part(target, radius=1.0, window=4.0, start=None, **part):
    return Part("part", (disc("body", radius),), start or target, target, around(target, window),
                **part)


def box_obstacle(name, low, high, kind="block", z_range=None):
    points = ((low[0], low[1]), (high[0], low[1]), (high[0], high[1]), (low[0], high[1]))
    return Obstacle(name, kind, Prism(Convex(points), z_range))


def square_obstacle(name="block", kind="block", center=(0.0, 0.0), z_range=None):
    return box_obstacle(name, (center[0] - 1.0, center[1] - 1.0),
                        (center[0] + 1.0, center[1] + 1.0), kind, z_range)


def clear_rule(minimum=0.5, kind="block", feature="body"):
    return Rule("body from the block", feature, (kind,), CLEAR, minimum)


def line_parts(positions, low=-10.0, high=10.0):
    """Points on the x axis, free in x alone, each its own target."""
    return tuple(Part(name, (disc("body", 0.0),), Pose(x, 0.0), Pose(x, 0.0), (("x", low, high),))
                 for name, x in positions)


def pose_of(report, name="part"):
    return next(answer.pose for answer in report.answers if answer.part == name)


def rooms_problem(apart, objective):
    """Two bodies, each held inside a room of its own context, the rooms
    apart on the x axis, and a pair rule in a context both share."""
    rule = Rule("body inside its room", "body", ("room",), INSIDE, 0.0)
    parts = tuple(Part(name, (disc("body", 0.1),), Pose(x, 0.0), None,
                       (("x", x - 6.0, x + 6.0), ("y", -6.0, 6.0)), (f"room {name}", "shared"))
                  for name, x in (("a", 0.0), ("b", apart)))
    rooms = tuple(Obstacle(f"{name}'s room", "room", Prism(Circle((x, 0.0), 5.0)), f"room {name}")
                  for name, x in (("a", 0.0), ("b", apart)))
    return Problem(parts, rooms, (rule,), (PairRule("bodies apart", "body", 0.5),),
                   objective=objective)


def far_rooms():
    """(parts, rooms, rules, pair rules) of two bodies 98 apart, each its
    own target, a in a room of 5 around (0, 0), b in one of 1 around
    itself."""
    rule = Rule("body inside its room", "body", ("room",), INSIDE, 0.0)
    parts = (Part("a", (disc("body", 0.1),), Pose(2.0, 0.0), Pose(2.0, 0.0),
                  around(Pose(2.0, 0.0), 4.0), ("room a", "shared")),
             Part("b", (disc("body", 0.1),), Pose(100.0, 0.0), Pose(100.0, 0.0),
                  around(Pose(100.0, 0.0), 2.0), ("room b", "shared")))
    rooms = (Obstacle("a's room", "room", Prism(Circle((0.0, 0.0), 5.0)), "room a"),
             Obstacle("b's room", "room", Prism(Circle((100.0, 0.0), 1.0)), "room b"))
    return parts, rooms, (rule,), (PairRule("bodies apart", "body", 0.5),)


def lens_rooms():
    """(rooms, rule, the lens's middle) of two rooms that overlap by
    1e-4 along a direction midway between their polygons' corners, less
    than their chords come inside the arcs: the map is empty, the rooms
    are not."""
    angle = math.pi / (4 * 64)
    direction = (math.cos(angle), math.sin(angle))
    rooms = tuple(Obstacle(name, "room", Prism(Circle((distance * direction[0],
                                                       distance * direction[1]), 5.0)))
                  for name, distance in (("west room", 0.0), ("east room", 10.0 - 1e-4)))
    rule = Rule("body inside the rooms", "body", ("room",), INSIDE, 0.0)
    return rooms, rule, Pose((5.0 - 5e-5) * direction[0], (5.0 - 5e-5) * direction[1])


class MapTest(unittest.TestCase):
    def test_free_target_is_the_answer(self):
        problem = Problem((one_part(Pose(6.0, 0.0)),), (square_obstacle(),), (clear_rule(),))
        report = solve(problem)
        self.assertEqual(pose_of(report), Pose(6.0, 0.0))
        self.assertEqual(report.attempts[0].method, "map")
        self.assertTrue(report.answers[0].maps[-1].target_free)
        self.assertTrue(report.answers[0].own)

    def test_nearest_free_on_a_straight_edge(self):
        problem = Problem((one_part(Pose(0.5, 0.0)),), (square_obstacle(),), (clear_rule(),))
        pose = pose_of(solve(problem))
        self.assertAlmostEqual(pose.x, 2.5, places=7)
        self.assertAlmostEqual(pose.y, 0.0, places=7)

    def test_nearest_free_on_an_arc_is_moved_onto_the_exact_circle(self):
        problem = Problem((one_part(Pose(2.0, 2.0)),), (square_obstacle(),), (clear_rule(),))
        report = solve(problem)
        pose = pose_of(report)
        self.assertAlmostEqual(math.dist((pose.x, pose.y), (1.0, 1.0)), 1.5, places=7)
        self.assertAlmostEqual(pose.x, pose.y, places=6)
        self.assertGreaterEqual(report.rows[0].margin, -1e-9)
        self.assertTrue(report.rows[0].binding)
        self.assertGreater(report.rows[0].multiplier, 0.0)

    def test_nearest_and_least_move_meet_halfway(self):
        # Nothing in the way, so the answer is where the two terms'
        # sum is least, not the target.
        part = one_part(Pose(4.0, 0.0), start=Pose(0.0, 0.0))
        problem = Problem((part,), (), (), objective=(Term(NEAREST), Term(LEAST_MOVE)))
        report = solve(problem)
        self.assertAlmostEqual(pose_of(report).x, 2.0, places=7)
        self.assertAlmostEqual(pose_of(report).y, 0.0, places=7)
        self.assertAlmostEqual(report.objective, 8.0, places=6)

    def test_nearest_and_least_move_by_their_weights(self):
        part = one_part(Pose(4.0, 0.0), start=Pose(0.0, 0.0))
        problem = Problem((part,), (), (),
                          objective=(Term(NEAREST, weight=3.0), Term(LEAST_MOVE, weight=1.0)))
        self.assertAlmostEqual(pose_of(solve(problem)).x, 3.0, places=7)

    def test_an_empty_map_reports_its_least_broken_pose(self):
        problem = Problem((one_part(Pose(0.2, 0.1), window=0.5),), (square_obstacle(),),
                          (clear_rule(),))
        report = solve(problem)
        answer = report.answers[0]
        self.assertIsNone(answer.pose)
        self.assertIsNotNone(answer.best)
        rows, _fired = answer.breaks
        self.assertEqual([row.obstacle for row in rows], ["block"])
        # The body breaks the rule least on the window's east edge, 0.3
        # into the block: by its radius 1.0, the minimum 0.5 and that 0.3.
        self.assertAlmostEqual(rows[0].margin, -1.8, places=6)
        self.assertAlmostEqual(answer.best.x, 0.7, places=6)
        self.assertTrue(answer.tried[0][1].startswith("no free pose in its window, the least "
                                                      "broken"))

    def test_the_least_broken_pose_has_the_largest_least_margin(self):
        # A point body inside a block reaching from the west and two
        # from the east breaks them least at x 0.5, each by 0.5, though
        # its target is at x 0.2.
        blocks = (box_obstacle("west block", (-10.0, -10.0), (1.0, 10.0)),
                  box_obstacle("east block", (0.0, -10.0), (10.0, 10.0)),
                  box_obstacle("east block again", (0.0, -10.0), (10.0, 10.0)))
        part = Part("part", (disc("body", 0.0),), Pose(0.2, 0.0), Pose(0.2, 0.0),
                    (("x", 0.0, 1.0), ("y", -0.1, 0.1)))
        answer = solve(Problem((part,), blocks, (clear_rule(0.0),))).answers[0]
        self.assertAlmostEqual(answer.best.x, 0.5, places=6)
        for row in answer.breaks[0]:
            self.assertAlmostEqual(row.margin, -0.5, places=6)

    def test_a_free_region_of_no_area_finds_the_exact_room(self):
        # The room shrunk by the body meets the window along x 1 alone.
        room = box_obstacle("room", (0.0, 0.0), (10.0, 10.0), "room")
        rule = Rule("body inside the room", "body", ("room",), INSIDE, 0.0)
        problem = Problem((one_part(Pose(-1.0, 5.0), window=2.0),), (room,), (rule,))
        report = solve(problem)
        self.assertEqual(report.answers[0].maps[-1].free_area, 0.0)
        # A line is no free region, so the map has no nearest point.
        self.assertIsNone(report.answers[0].maps[-1].nearest)
        self.assertAlmostEqual(pose_of(report).x, 1.0, places=6)
        self.assertAlmostEqual(pose_of(report).y, 5.0, places=6)

    def test_a_free_lens_the_arcs_lose_is_found(self):
        rooms, rule, middle = lens_rooms()
        report = solve(Problem((one_part(middle, radius=0.0, window=0.01),), rooms, (rule,)))
        self.assertEqual(report.answers[0].maps[-1].free_area, 0.0)
        self.assertIsNotNone(pose_of(report))
        self.assertGreaterEqual(min(row.margin for row in report.rows), -1e-6)

    def test_a_free_pose_is_found_where_the_map_has_no_area(self):
        rooms, rule, middle = lens_rooms()
        lens = Problem((one_part(middle, radius=0.0, window=0.01),), rooms, (rule,),
                       tolerance=0.0)
        pinned = Problem((Part("part", (disc("body", 0.5),), Pose(5.0, 0.0), Pose(5.0, 0.0),
                               (("x", 5.0, 5.0), ("y", -2.0, 2.0))),),
                         (square_obstacle(),), (clear_rule(),))
        for what, problem in (("tolerance 0", lens), ("x pinned by equal bounds", pinned)):
            with self.subTest(what):
                self.assertIsNotNone(pose_of(solve(problem)))
        # Were the loosened map empty after all, the least broken run
        # would find the target free, and the runs from it take it.
        with mock.patch.object(solve_module, "loosened_free", lambda *arguments: MultiPolygon()):
            pose = pose_of(solve(pinned))
        self.assertAlmostEqual(pose.x, 5.0, places=6)
        self.assertAlmostEqual(pose.y, 0.0, places=6)

    def test_a_part_alone_keeps_its_reach(self):
        # Every pose within reach 1 of the target (0, 0) is free, and
        # the objective pulls beyond it.
        block = box_obstacle("block", (-20.0, -20.0), (-1.0, 20.0))
        for kind, start in ((MOST_CLEARANCE, Pose(0.0, 0.0)), (LEAST_MOVE, Pose(4.0, 0.0))):
            part = Part("part", (disc("body", 0.5),), start, Pose(0.0, 0.0),
                        (("x", -1.0, 5.0), ("y", -5.0, 5.0)), reach=1.0)
            report = solve(Problem((part,), (block,), (clear_rule(0.0),), objective=(Term(kind),)))
            with self.subTest(kind):
                self.assertIsNotNone(pose_of(report))
                self.assertAlmostEqual(pose_of(report).x, 1.0, places=6)
                self.assertAlmostEqual(pose_of(report).y, 0.0, places=6)

    def test_most_clearance_starts_in_every_pocket(self):
        # A closed room keeps 2 at most, a strip along the window's north
        # edge 3 at its east end: the map's circle, which counts the
        # window's edges, is the room's.
        walls = tuple(box_obstacle(name, low, high, "wall") for name, low, high in (
            ("west of the room", (-5.0, -5.0), (1.0, 15.0)), ("south", (-5.0, -5.0), (25.0, 1.0)),
            ("between", (5.0, -5.0), (10.0, 15.0)), ("north of the room", (-5.0, 5.0), (5.0, 15.0)),
            ("under the strip", (10.0, -5.0), (25.0, 7.0))))
        part = Part("part", (disc("body", 0.0),), Pose(3.0, 3.0), None,
                    (("x", 0.0, 20.0), ("y", 0.0, 10.0)))
        report = solve(Problem((part,), walls, (clear_rule(0.0, "wall"),),
                               objective=(Term(MOST_CLEARANCE),)))
        self.assertAlmostEqual(min(row.margin for row in report.rows), 3.0, places=6)
        self.assertAlmostEqual(pose_of(report).y, 10.0, places=6)

    def test_nearest_and_most_clearance_start_in_every_pocket(self):
        # The target sits in a corridor, the map's most clearance in a
        # room beyond its end, whatever the term's weight.
        walls = tuple(box_obstacle(name, low, high, "wall") for name, low, high in (
            ("corridor top", (-3.0, 1.0), (10.0, 7.0)),
            ("corridor bottom", (-3.0, -7.0), (10.0, -1.0)),
            ("corridor end", (-3.0, -7.0), (-2.0, 7.0)), ("door", (9.0, -1.0), (10.0, 1.0)),
            ("room top", (10.0, 6.0), (22.0, 7.0)), ("room bottom", (10.0, -7.0), (22.0, -6.0)),
            ("room end", (21.0, -7.0), (22.0, 7.0))))
        part = Part("part", (disc("body", 0.1),), Pose(0.0, 0.0), Pose(0.0, 0.0),
                    (("x", -1.9, 20.9), ("y", -5.9, 5.9)))
        for weight in (0.0, 1.0, 10.0):
            problem = Problem((part,), walls, (clear_rule(0.0, "wall"),),
                              objective=(Term(NEAREST), Term(MOST_CLEARANCE, weight=weight)))
            with self.subTest(weight=weight):
                pose = pose_of(solve(problem))
                self.assertAlmostEqual(pose.x, 0.0, places=6)
                self.assertAlmostEqual(pose.y, 0.0, places=6)

    def test_inside_an_outline(self):
        outline = Obstacle("outline", "outline",
                           Prism(Outline(((0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)))))
        rule = Rule("body inside the outline", "body", ("outline",), INSIDE, 0.5)
        problem = Problem((one_part(Pose(0.0, 5.0)),), (outline,), (rule,))
        pose = pose_of(solve(problem))
        self.assertAlmostEqual(pose.x, 1.5, places=7)
        self.assertAlmostEqual(pose.y, 5.0, places=7)

    def test_heights_that_never_meet_are_no_rule(self):
        part = Part("part", (disc("body", 1.0, (5.0, 9.0)),), Pose(0.5, 0.0), Pose(0.5, 0.0),
                    around(Pose(0.5, 0.0), 4.0))
        problem = Problem((part,), (square_obstacle(z_range=(0.0, 5.0)),), (clear_rule(),))
        report = solve(problem)
        self.assertEqual(pose_of(report), Pose(0.5, 0.0))
        self.assertEqual(report.rows, ())

    def test_most_clearance_in_a_corridor(self):
        walls = (square_obstacle("west", center=(-2.0, 0.0)),
                 square_obstacle("east", center=(3.0, 0.0)))
        part = Part("part", (disc("body", 0.5),), Pose(0.0, 0.0), None,
                    (("x", -1.0, 2.0), ("y", -0.5, 0.5)))
        problem = Problem((part,), walls, (clear_rule(0.0),), objective=(Term(MOST_CLEARANCE),))
        report = solve(problem)
        self.assertAlmostEqual(pose_of(report).x, 0.5, places=6)
        self.assertAlmostEqual(report.rows[0].margin, 1.0, places=6)

    def test_most_clearance_takes_the_pocket_of_the_largest_circle(self):
        # A 3 x 3 room and a corridor 1.1 wide, the corridor's free area
        # the larger.
        walls = (((-1.0, -1.0), (21.0, 0.0)), ((-1.0, 3.0), (4.0, 4.0)),
                 ((-1.0, -1.0), (0.0, 4.0)), ((3.0, -1.0), (4.0, 4.0)),
                 ((4.0, 1.1), (21.0, 4.0)), ((20.0, -1.0), (21.0, 4.0)))
        obstacles = tuple(box_obstacle(f"wall {index}", low, high)
                          for index, (low, high) in enumerate(walls))
        part = Part("part", (disc("body", 0.05),), Pose(10.0, 0.5), None,
                    (("x", 0.0, 20.0), ("y", 0.0, 3.0)))
        problem = Problem((part,), obstacles, (clear_rule(0.0),),
                          objective=(Term(MOST_CLEARANCE),))
        report = solve(problem)
        pose = pose_of(report)
        self.assertAlmostEqual(pose.x, 1.5, places=5)
        self.assertAlmostEqual(pose.y, 1.5, places=5)
        self.assertAlmostEqual(report.rows[0].margin, 1.45, places=6)

    def test_most_clearance_keeps_the_run_of_most_clearance(self):
        # From its start a run ends 0.3 clear in the narrow room, from its
        # target 2.9 clear in the wide one.
        walls = ((-10.0, 0.0), (0.8, 1.0), (7.0, 20.0))
        obstacles = tuple(box_obstacle(f"wall {index}", (low, -1.0), (high, 1.0))
                          for index, (low, high) in enumerate(walls))
        part = Part("part", (disc("body", 0.1),), Pose(0.4, 0.0), Pose(4.0, 0.0),
                    (("x", 0.0, 7.0),))
        problem = Problem((part,), obstacles, (clear_rule(0.0),),
                          objective=(Term(MOST_CLEARANCE),))
        report = solve(problem)
        self.assertAlmostEqual(pose_of(report).x, 4.0, places=6)
        self.assertAlmostEqual(report.rows[0].margin, 2.9, places=6)

    def test_most_clearance_counts_obstacles_beyond_the_window(self):
        # The east wall stands 3 past the window, beyond where it could
        # bind, yet it is the nearer one at the window's east end.
        walls = (box_obstacle("west wall", (-5.0, -1.0), (0.0, 1.0)),
                 box_obstacle("east wall", (13.0, -1.0), (18.0, 1.0)))
        part = Part("part", (disc("body", 0.05),), Pose(1.0, 0.0), None, (("x", 0.0, 10.0),))
        problem = Problem((part,), walls, (clear_rule(0.0),), objective=(Term(MOST_CLEARANCE),))
        report = solve(problem)
        self.assertAlmostEqual(pose_of(report).x, 6.5, places=6)
        self.assertEqual({row.obstacle for row in report.rows}, {"west wall", "east wall"})
        self.assertAlmostEqual(report.rows[0].margin, 6.45, places=6)

    def test_most_clearance_never_trades_a_rule_for_distance(self):
        # At the target the body is 2.5 short of its rule, which costs
        # less than the 6.25 the nearest pose that keeps it does.
        problem = Problem((one_part(Pose(0.0, 0.0)),), (square_obstacle(),), (clear_rule(),),
                          objective=(Term(NEAREST), Term(MOST_CLEARANCE)))
        report = solve(problem)
        self.assertTrue(report.feasible)
        self.assertGreaterEqual(report.rows[0].margin, -1e-6)


class MultiplierTest(unittest.TestCase):
    def test_a_binding_row_gets_its_multiplier_and_a_slack_row_none(self):
        far = Obstacle("far post", "block", Prism(Circle((3.0, 3.5), 0.25)))
        problem = Problem((one_part(Pose(0.5, 0.0)),), (square_obstacle(), far), (clear_rule(),))
        report = solve(problem)
        rows = {row.obstacle: row for row in report.rows}
        self.assertAlmostEqual(pose_of(report).x, 2.5, places=7)
        # The objective's gradient at (2.5, 0), 2 (2.5 - 0.5), over the
        # margin's, 1.
        self.assertAlmostEqual(rows["block"].multiplier, 4.0, places=4)
        self.assertTrue(rows["block"].binding)
        self.assertGreater(rows["far post"].margin, 1.0)
        self.assertLess(abs(rows["far post"].multiplier), 1e-9)
        self.assertFalse(rows["far post"].binding)


class RuleKindsTest(unittest.TestCase):
    def test_merge_is_reported_with_its_depth_and_its_survivor_holds(self):
        part = Part("part", (disc("body", 1.0), disc("bore", 0.5)), Pose(0.0, 1.5),
                    Pose(0.0, 1.5), around(Pose(0.0, 1.5), 3.0))
        void = Obstacle("void", "void", Prism(Circle((0.0, -1.0), 0.5)))
        rules = (Rule("body merging with the block", "body", ("block",), MERGE,
                      survivor="bore from the voids"),
                 Rule("bore from the voids", "bore", ("void",), CLEAR, 0.6))
        report = solve(Problem((part,), (square_obstacle(), void), rules))
        self.assertEqual(pose_of(report), Pose(0.0, 1.5))
        merged = [row for row in report.rows if row.status == "merged"]
        self.assertEqual(len(merged), 1)
        self.assertAlmostEqual(merged[0].value, -0.5)
        self.assertAlmostEqual(next(row.margin for row in report.rows if row.feature == "bore"),
                               2.5 - 1.0 - 0.6)
        self.assertTrue(any("bore from the voids at +0.9000, holds" in line
                            for line in report_text(report)))

    def test_merge_text_gives_its_survivors_own_margin(self):
        part = Part("part", (disc("body", 1.0), disc("bore", 0.5)), Pose(0.0, 0.5),
                    Pose(0.0, 0.5), around(Pose(0.0, 0.5), 3.0))
        void = Obstacle("void", "void", Prism(Circle((0.0, -1.0), 0.5)))
        rules = (Rule("body merging with the block", "body", ("block",), MERGE,
                      survivor="bore from the voids"),
                 Rule("bore from the voids", "bore", ("void",), CLEAR, 0.6))
        problem = Problem((part,), (square_obstacle(), void), rules)
        rows, _fired = evaluate.evaluate(problem, evaluate.rule_instances(problem, part),
                                         {"part": part.start}, (part,))
        merged = next(row for row in rows if row.status == "merged")
        self.assertIn("bore from the voids at -0.1000, breaks", merge_text(merged, rows))

    def test_a_merges_survivor_must_name_a_rule(self):
        rule = Rule("body merging with the block", "body", ("block",), MERGE,
                    survivor="no such rule")
        for survivor in ("no such rule", None):
            with self.subTest(survivor), self.assertRaises(ValueError):
                Problem((one_part(Pose(0.0, 0.0)),), (square_obstacle(),),
                        (Rule(rule.name, "body", ("block",), MERGE, survivor=survivor),))

    def test_a_negative_weight_is_refused(self):
        for term in (Term(NEAREST, weight=-1.0), Term(LEAST_MOVE, weight=-2.0),
                     Term(MOST_CLEARANCE, weight=-0.5)):
            with self.subTest(term.kind), self.assertRaises(ValueError):
                Problem((one_part(Pose(0.0, 0.0)),), (), (), objective=(term,))

    def test_unknown_kinds_relations_and_parts_are_refused(self):
        cases = {
            "a term kind": {"objective": (Term("MOST_CLEARANCE"),)},
            "a rule relation": {"rules": (Rule("body in the block", "body", ("block",), "Inside",
                                               0.0),)},
            "a term's part": {"objective": (Term(NEAREST, "nobody"),)},
        }
        for what, change in cases.items():
            arguments = {"parts": (one_part(Pose(0.0, 0.0)),), "obstacles": (square_obstacle(),),
                         "rules": (clear_rule(),), **change}
            with self.subTest(what), self.assertRaises(ValueError):
                Problem(**arguments)

    def test_repeated_names_are_refused(self):
        part = one_part(Pose(0.0, 0.0))
        twice = Part("part", (disc("body", 1.0), disc("body", 2.0)), Pose(0.0, 0.0),
                     Pose(0.0, 0.0), around(Pose(0.0, 0.0), 1.0))
        flat = Conditional("flat", "body from the block", ("block",), "", bool, abs, str)
        shared = SharedVariable("lift", (("part", "x"),), 0.0, 1.0)
        other = SharedVariable("other lift", (("part", "x"),), 0.0, 1.0)
        cases = {
            "parts": {"parts": (part, part)},
            "features": {"parts": (twice,)},
            "obstacles": {"obstacles": (square_obstacle(), square_obstacle())},
            "rules": {"rules": (clear_rule(), clear_rule(0.2))},
            "pair rules": {"pair_rules": (PairRule("apart", "body"), PairRule("apart", "body"))},
            "conditionals": {"conditionals": (flat, flat)},
            "shared variables": {"shared": (shared, shared)},
            "shared members": {"shared": (shared, other)},
        }
        for what, change in cases.items():
            arguments = {"parts": (part,), "obstacles": (square_obstacle(),),
                         "rules": (clear_rule(),), **change}
            with self.subTest(what), self.assertRaises(ValueError):
                Problem(**arguments)

    def test_conditional_stands_in_and_its_margin_moves_the_answer(self):
        socket = Obstacle("socket", "socket", Prism(Circle((0.0, 0.0), 0.5)))
        rule = Rule("body from the sockets", "body", ("socket",), CLEAR, 1.0)

        def flat_fires(pose):
            return math.hypot(pose.x, pose.y) - 1.5 < 1.0

        def flat_margin(pose):
            return math.hypot(pose.x, pose.y) - 2.0

        def flat_note(pose):
            return f"a flat at {math.hypot(pose.x, pose.y) - 1.5:.3f}"

        flat = Conditional("the socket's flat", "body from the sockets", ("socket",), "",
                           flat_fires, flat_margin, flat_note)
        problem = Problem((one_part(Pose(1.5, 0.0)),), (socket,), (rule,), conditionals=(flat,))
        report = solve(problem)
        self.assertAlmostEqual(pose_of(report).x, 2.0, places=6)
        self.assertEqual(len(report.fired), 1)
        self.assertAlmostEqual(report.fired[0].margin, 0.0, places=6)
        self.assertTrue(report.rows[-1].status.startswith("waived by"))
        dumped = json.loads(problem_json(problem))
        self.assertEqual(dumped["conditionals"][0]["margin"]["function"],
                         "RuleKindsTest.test_conditional_stands_in_and_its_margin_moves_the_"
                         "answer.<locals>.flat_margin")
        breaks, fired = explain(problem, "part", Pose(1.0, 0.0))
        self.assertEqual(breaks, ())
        self.assertAlmostEqual(fired[0].margin, -1.0)

    def test_a_conditional_waives_its_own_contexts_rule_alone(self):
        # One name in both contexts: the left one firing leaves the right
        # one's rule standing.
        rule = Rule("body from the sockets", "body", ("socket",), CLEAR, 1.0)
        sockets = tuple(Obstacle("socket", "socket", Prism(Circle((0.0, 0.0), 0.5)), context)
                        for context in ("left", "right"))

        def flat(context):
            return Conditional("the flat", rule.name, ("socket",), context,
                               lambda _pose: context == "left", lambda _pose: 1.0,
                               lambda _pose: "a flat")

        part = one_part(Pose(1.5, 0.0), contexts=("left", "right"))
        problem = Problem((part,), sockets, (rule,), conditionals=(flat("left"), flat("right")))
        report = solve(problem)
        rows = {row.context: row for row in report.rows}
        self.assertEqual(rows["left"].status, "waived by the flat")
        self.assertEqual(rows["right"].status, "holds")
        self.assertAlmostEqual(pose_of(report).x, 2.5, places=6)

    def test_explain_names_what_a_pose_breaks(self):
        problem = Problem((one_part(Pose(0.5, 0.0)),), (square_obstacle(),), (clear_rule(),))
        breaks, _fired = explain(problem, "part", Pose(0.5, 0.0))
        self.assertEqual([row.obstacle for row in breaks], ["block"])
        self.assertAlmostEqual(breaks[0].margin, -0.5 - 1.0 - 0.5)

    def test_alternatives_in_order(self):
        part = one_part(Pose(0.0, 0.0), window=0.5, reach=0.5)
        later = Option("the east spot", Pose(5.0, 0.0), around(Pose(5.0, 0.0), 0.5))
        problem = Problem((part,), (square_obstacle(),), (clear_rule(),),
                          alternatives=(Alternatives("part", (later,)),))
        report = solve(problem)
        answer = report.answers[0]
        self.assertEqual(answer.option, "the east spot")
        self.assertFalse(answer.own)
        self.assertEqual(answer.pose, Pose(5.0, 0.0))
        # The first window is blocked even with the rules loosened, so
        # no run looks for its least broken pose.
        self.assertEqual(answer.tried[0][1], "no free pose in its window")
        self.assertEqual({attempt.method for attempt in report.attempts}, {"map"})
        self.assertEqual(answer.tried[1][1], "placed alone at (5.000, 0.000), 0.000 from it")


class CoupledTest(unittest.TestCase):
    def test_pair_rule_couples_two_parts(self):
        parts = tuple(Part(name, (disc("body", 1.0),), Pose(x, 0.0), Pose(x, 0.0),
                           around(Pose(x, 0.0), 2.0))
                      for name, x in (("west", -0.5), ("east", 0.5)))
        problem = Problem(parts, (), (), pair_rules=(PairRule("bodies apart", "body", 0.5),))
        report = solve(problem)
        self.assertAlmostEqual(pose_of(report, "west").x, -1.25, places=6)
        self.assertAlmostEqual(pose_of(report, "east").x, 1.25, places=6)
        self.assertEqual(report.attempts[-1].parts, ("west", "east"))

    def test_pair_rules_couple_every_part_they_join(self):
        # Solving the broken pair alone would move b to 1.75, 0.75 short
        # of c.
        parts = line_parts((("a", 0.0), ("b", 1.0), ("c", 3.5)))
        problem = Problem(parts, (), (), pair_rules=(PairRule("bodies apart", "body", 2.5),))
        report = solve(problem)
        self.assertTrue(report.feasible)
        self.assertEqual([row.status for row in report.rows], ["holds"] * 3)
        for name, x in (("a", -1.0), ("b", 1.5), ("c", 4.0)):
            self.assertAlmostEqual(pose_of(report, name).x, x, places=6)
        self.assertAlmostEqual(report.objective, 1.5, places=6)

    def test_a_group_whose_pairs_hold_keeps_its_own_answers(self):
        parts = line_parts((("a", 0.0), ("b", 3.0)))
        problem = Problem(parts, (), (), pair_rules=(PairRule("bodies apart", "body", 2.5),))
        report = solve(problem)
        self.assertAlmostEqual(pose_of(report, "a").x, 0.0, places=12)
        self.assertAlmostEqual(pose_of(report, "b").x, 3.0, places=12)
        self.assertEqual({attempt.parts for attempt in report.attempts}, {("a",), ("b",)})

    def test_a_group_no_run_places_says_what_breaks(self):
        parts = line_parts((("a", 0.0), ("b", 1.0)), low=0.0, high=1.0)
        problem = Problem(parts, (), (), pair_rules=(PairRule("bodies apart", "body", 2.5),))
        report = solve(problem)
        self.assertFalse(report.feasible)
        for answer in report.answers:
            self.assertIsNone(answer.pose)
            self.assertIsNotNone(answer.best)
            rows, _fired = answer.breaks
            self.assertEqual([row.rule for row in rows], ["bodies apart"])
            self.assertLessEqual(rows[0].margin, -1.5 + 1e-6)
        self.assertEqual(report.answers[0].tried[-1], ("with b", "no run keeps every rule"))
        text = report_text(report)
        self.assertTrue(any(line.startswith("  a: not placed, the least broken run ends at")
                            for line in text))
        self.assertTrue(any("breaks bodies apart" in line for line in text))
        self.assertFalse(any(line.startswith("  a: (") for line in text))
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "unplaced.png")
            picture.draw(problem, report, "", path)
            self.assertGreater(os.path.getsize(path), 10000)

    def test_a_group_holds_each_parts_reach(self):
        parts = tuple(dataclasses.replace(part, reach=0.5)
                      for part in line_parts((("a", 0.0), ("b", 1.0)), low=-3.0, high=4.0))
        report = solve(Problem(parts, (), (), pair_rules=(PairRule("apart", "body", 4.0),)))
        self.assertFalse(report.feasible)
        for answer in report.answers:
            self.assertIsNone(answer.pose)
            self.assertFalse(answer.own)
            _label, outcome = answer.tried[-1]
            self.assertIn("beyond its reach 0.5", outcome)
        wide = tuple(dataclasses.replace(part, reach=2.0) for part in parts)
        report = solve(Problem(wide, (), (), pair_rules=(PairRule("apart", "body", 4.0),)))
        self.assertAlmostEqual(pose_of(report, "a").x, -1.5, places=6)
        self.assertAlmostEqual(pose_of(report, "b").x, 2.5, places=6)

    def test_one_most_clearance_term_is_one_least_margin_over_the_parts(self):
        # Each part in a room of its own, the pair in a context they
        # share. The least margin over both rooms and the pair is
        # 4.9 - s against 2.3 + 2 s for the rooms 3 apart, the pair
        # holding at the parts' own answers, and 4.9 - s against
        # 2 s - 0.1 for the rooms 0.6 apart, the pair breaking there.
        for apart, spread, least in ((3.0, 2.6 / 3.0, 4.9 - 2.6 / 3.0),
                                     (0.6, 5.0 / 3.0, 4.9 - 5.0 / 3.0)):
            with self.subTest(apart=apart):
                report = solve(rooms_problem(apart, (Term(MOST_CLEARANCE),)))
                self.assertAlmostEqual(pose_of(report, "a").x, -spread, places=5)
                self.assertAlmostEqual(pose_of(report, "b").x, apart + spread, places=5)
                self.assertAlmostEqual(report.rows[0].margin, least, places=6)

    def test_one_most_clearance_term_over_two_far_parts(self):
        # b's small room bounds the one least margin at 0.9, so a stays
        # at its target, where its own term would pull it to 1.5.
        far = Problem(*far_rooms(), objective=(Term(NEAREST), Term(MOST_CLEARANCE)))
        self.assertAlmostEqual(pose_of(solve(far), "a").x, 2.0, places=6)
        own = Problem(*far_rooms(), objective=(Term(NEAREST), Term(MOST_CLEARANCE, "a"),
                                               Term(MOST_CLEARANCE, "b")))
        self.assertAlmostEqual(pose_of(solve(own), "a").x, 1.5, places=6)
        # The one term joins the parts without the pair rule too.
        parts, rooms, rules, _pairs = far_rooms()
        unpaired = Problem(parts, rooms, rules, objective=(Term(NEAREST), Term(MOST_CLEARANCE)))
        self.assertAlmostEqual(pose_of(solve(unpaired), "a").x, 2.0, places=6)

    def test_turning_a_bar_clear_of_two_pins(self):
        bar = Feature("bar", Prism(Convex(((-2.0, -0.2), (2.0, -0.2), (2.0, 0.2), (-2.0, 0.2)))))
        part = Part("bar", (bar,), Pose(0.0, 0.0, 0.0, 5.0), Pose(0.0, 0.0, 0.0, 0.0),
                    (("angle", 0.0, 90.0),))
        pins = tuple(Obstacle(f"pin {x}", "pin", Prism(Circle((x, 0.0), 0.1)))
                     for x in (-1.5, 1.5))
        rule = Rule("bar from the pins", "bar", ("pin",), CLEAR, 0.0)
        report = solve(Problem((part,), pins, (rule,)))
        self.assertAlmostEqual(pose_of(report, "bar").angle, math.degrees(math.asin(0.2)), places=4)


class HeightTest(unittest.TestCase):
    def test_least_lift_in_z(self):
        head = Part("head", (disc("head", 2.0, (5.0, 6.5)),), Pose(0.0, 0.0), None,
                    (("z", 0.0, 3.0),))
        strip = square_obstacle("strip", "strip", z_range=(3.5, 5.25))
        above = square_obstacle("socket", "strip", center=(0.0, 8.0), z_range=(7.0, 9.5))
        rule = Rule("head from the strip", "head", ("strip",), CLEAR, 0.5)
        problem = Problem((head,), (strip, above), (rule,), objective=(Term(LEAST_MOVE),))
        report = solve(problem)
        self.assertAlmostEqual(pose_of(report, "head").z, 0.25, places=6)
        free = free_heights(problem, "head", Pose(0.0, 0.0))
        self.assertAlmostEqual(least_lift(free, 0.0), 0.25, places=5)
        row = next(row for row in report.rows if row.obstacle == "strip")
        self.assertEqual(row.status, "apart in height")

    def test_a_part_moving_in_z_keeps_a_rule_its_start_heights_miss(self):
        # At its start the body is under the block, at its target in it.
        part = Part("part", (disc("body", 1.0, (0.0, 1.0)),), Pose(0.0, 0.0),
                    Pose(0.0, 0.0, 2.5), (("z", 0.0, 3.0),))
        problem = Problem((part,), (square_obstacle(z_range=(2.0, 3.0)),), (clear_rule(),))
        report = solve(problem)
        self.assertAlmostEqual(pose_of(report).z, 3.0, places=6)
        self.assertEqual([row.obstacle for row in report.rows], ["block"])

    def test_shared_variable_takes_the_larger_lift(self):
        parts = tuple(Part(name, (disc("head", 1.0, (0.0, 1.0)),), Pose(x, 0.0), None,
                           (("z", 0.0, 2.0),)) for name, x in (("west", -10.0), ("east", 10.0)))
        obstacles = (square_obstacle("west strip", "strip", (-10.0, 0.0), (-1.0, 0.3)),
                     square_obstacle("east strip", "strip", (10.0, 0.0), (-1.0, 0.5)))
        rule = Rule("head from the strips", "head", ("strip",), CLEAR, 0.0)
        shared = SharedVariable("backing z", (("west", "z"), ("east", "z")), 0.0, 2.0)
        problem = Problem(parts, obstacles, (rule,), shared=(shared,),
                          objective=(Term(LEAST_MOVE),))
        report = solve(problem)
        self.assertAlmostEqual(pose_of(report, "west").z, 0.5, places=6)
        self.assertAlmostEqual(pose_of(report, "east").z, 0.5, places=6)


class FallbackTest(unittest.TestCase):
    def test_cobyqa_runs_where_slsqp_stalls(self):
        original = solve_module.run_method

        def stalling(method, functions, start, bounds, constrained):
            result = original(method, functions, start, bounds, constrained)
            if method == "SLSQP":
                result.success = False
            return result

        problem = Problem((one_part(Pose(2.0, 2.0)),), (square_obstacle(),), (clear_rule(),))
        with mock.patch.object(solve_module, "run_method", stalling):
            report = solve(problem)
        cobyqa = [attempt for attempt in report.attempts if attempt.method == "COBYQA"]
        self.assertEqual(len(cobyqa), 1)
        end = cobyqa[0].end[0][1]
        self.assertAlmostEqual(math.dist((end.x, end.y), (1.0, 1.0)), 1.5, places=5)

    def test_a_group_cobyqa_placed_leaves_no_multipliers_of_the_parts_own(self):
        # On their own both bodies end on the block's top, binding with
        # multipliers. Their pair breaks there, and COBYQA moves them
        # apart along the block, SLSQP's group runs held at their start.
        original = solve_module.run_method

        def stalling_in_groups(method, functions, start, bounds, constrained):
            result = original(method, functions, start, bounds, constrained)
            if method == "SLSQP" and len(start) == 4:
                result.x, result.success = numpy.array(start), False
            return result

        parts = tuple(Part(name, (disc("body", 0.5),), Pose(x, 1.2), Pose(x, 1.2),
                           around(Pose(x, 1.2), 3.0)) for name, x in (("west", 0.0), ("east", 0.3)))
        problem = Problem(parts, (square_obstacle(),), (clear_rule(),),
                          pair_rules=(PairRule("bodies apart", "body", 0.5),))
        alone = solve(Problem(parts[:1], (square_obstacle(),), (clear_rule(),)))
        self.assertGreater(alone.rows[0].multiplier, 0.0)
        with mock.patch.object(solve_module, "run_method", stalling_in_groups):
            report = solve(problem)
        self.assertEqual(report.attempts[-1].method, "COBYQA")
        self.assertGreater(pose_of(report, "east").x - pose_of(report, "west").x, 1.4)
        for row in report.rows:
            self.assertIsNone(row.multiplier, row)
        self.assertTrue(all(row.binding == (row.margin <= problem.binding) for row in report.rows))


class OutputTest(unittest.TestCase):
    def test_the_picture_draws_a_part_with_no_pose(self):
        problem = Problem((one_part(Pose(0.2, 0.1), window=0.5),), (square_obstacle(),),
                          (clear_rule(),))
        report = solve(problem)
        lines = picture.row_lines(report, "")
        self.assertTrue(lines[0].startswith("not placed: part, at its least broken pose"))
        self.assertIn("body from the block", lines[1])
        self.assertEqual(len(picture.context_fields(problem, report, "")), 1)
        figure, axes = picture.pyplot.subplots()
        picture.draw_unplaced(axes, problem, report, "")
        # The target's cross and the line across the broken rule, and
        # the body at its least broken pose.
        self.assertEqual((len(axes.lines), len(axes.patches)), (2, 1))
        picture.pyplot.close(figure)

    def test_report_json_and_pictures(self):
        problem = Problem((one_part(Pose(2.0, 2.0)),), (square_obstacle(),), (clear_rule(),))
        report = solve(problem)
        self.assertIn("answers", json.loads(report_json(report)))
        head = Part("head", (disc("head", 2.0, (5.0, 6.5)),), Pose(0.0, 0.0), None,
                    (("z", 0.0, 3.0),))
        rule = Rule("head from the strip", "head", ("block",), CLEAR, 0.5)
        lifted = Problem((head,), (square_obstacle(z_range=(3.5, 5.25)),), (rule,),
                         objective=(Term(LEAST_MOVE),))
        with tempfile.TemporaryDirectory() as directory:
            for name, each in (("plan", problem), ("lift", lifted)):
                path = os.path.join(directory, f"{name}.png")
                picture.draw(each, solve(each), "", path)
                self.assertGreater(os.path.getsize(path), 10000)


if __name__ == "__main__":
    unittest.main()
