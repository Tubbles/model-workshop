"""place.py's problems against check_layout.py and the validation runs
of work item 016 (its research's section 7): the core's margins equal
check_layout's at the committed layout, the flats' conditionals fire
where check_layout cuts flats, and each run reproduces DESIGN.md's
figures. Run in the placement image (README.md, The placement solver):

    python3 model/kbdkid5/scripts/test_place.py
"""

import contextlib
import io
import math
import re
import unittest

import place
from place import check_layout, layout, placement
from placement import evaluate, geometry
from placement.problem import (CLEAR, Conditional, Feature, Obstacle, PairRule, Part, Pose,
                               Prism, Problem, Rule)

TOLERANCE = 1e-9
# A boss beyond layout.py's as print_frame_half() prints it, the point
# first as layout.py would state it.
EXTRA_BOSS = re.compile(r"beyond layout\.py's: .*? at \((-?[\d.]+), (-?[\d.]+)\)")


def measured_against_records(test, problem, gathered, part, center):
    """Check every rule instance of a part at center against its record,
    and that the instances are exactly the records whose heights meet."""
    instances = evaluate.rule_instances(problem, part)
    poses = {part.name: Pose(*center)}
    for instance in instances:
        record = gathered.records[(instance.rule.name, instance.obstacle.name, instance.context)]
        value = evaluate.instance_measure(instance, poses).value
        expected = check_layout.rule_clearance(center, record)
        test.assertLessEqual(abs(value - expected), TOLERANCE,
                             f"{record.name}, {record.obstacle} at {center}: {value} {expected}")
    meeting = [key for key, record in gathered.records.items()
               if check_layout.heights_meet(record) and key[2] in part.contexts]
    test.assertEqual(len(instances), len(meeting))
    return len(instances)


class MarginsTest(unittest.TestCase):
    """At the committed layout the core's margin of every rule instance
    equals check_layout's to 1e-9."""

    def test_every_standoff(self):
        problem, gathered = place.standoff_problem("standoffs", place.SIXTH_STANDOFF_TARGET)
        count = 0
        for center in layout.MOUNTING_DRILL_CENTERS_MM:
            part = place.standoff_part("standoff", gathered, center)
            count += measured_against_records(self, problem, gathered, part, center)
        self.assertGreater(count, 6 * 1000)

    def test_every_frame_boss(self):
        for right, context in place.CONTEXTS:
            gathered = place.frame_adapted(right)
            centers = layout.frame_boss_centers(right)
            parts = tuple(place.boss_part(f"boss at {center}", gathered, center, context)
                          for center in centers)
            problem = Problem(parts, gathered.obstacles, gathered.rules, place.pair_rules())
            for part, center in zip(parts, centers):
                measured_against_records(self, problem, gathered, part, center)
            poses = {part.name: part.start for part in parts}
            pair = check_layout.frame_boss_pair_rules()[0]
            instances = evaluate.pair_instances(problem, parts)
            self.assertEqual(len(instances), len(centers) * (len(centers) - 1) // 2)
            for instance in instances:
                first, second = poses[instance.part], poses[instance.other_part]
                expected = check_layout.pair_clearance((first.x, first.y), (second.x, second.y),
                                                       pair)
                value = evaluate.instance_measure(instance, poses).value
                self.assertLessEqual(abs(value - expected), TOLERANCE)


def cut_flats(flat_records, center):
    """{(key, context): records} of the sockets whose rule check_layout
    cuts flats for at center (flats_cut())."""
    cut = {}
    for record, context in flat_records:
        if check_layout.flats_cut(center, record):
            cut.setdefault((record.flat.key, context), []).append(record)
    return cut


def least_plastic(records, center):
    return min(check_layout.flat_plastic(flat) for record in records
               for flat in check_layout.flats_cut(center, record))


class FlatsTest(unittest.TestCase):
    """The flats' conditionals by check_layout's own functions: they fire
    where flats_cut() cuts flats, their margin is the least plastic the
    flats leave less the minimum wall, they break where thin_flats()
    finds a flat thin, and at the committed layout they fire where
    layout.py declares flats."""

    def test_flats_fire_as_check_layout_cuts_them(self):
        problem, gathered = place.standoff_problem("flats", place.SIXTH_STANDOFF_TARGET)
        flat_records = [(record, context) for (_rule, _name, context), record
                        in gathered.records.items() if record.flat is not None]
        north_east = place.NORTH_EAST_STANDOFF_TARGET
        nudged = [(north_east[0] + offset_x, north_east[1] + offset_y)
                  for offset_x in (-0.6, -0.3, 0.0, 0.3, 0.6) for offset_y in (-0.6, 0.0, 0.6)]
        seen_thin = False
        for center in tuple(layout.MOUNTING_DRILL_CENTERS_MM) + tuple(nudged):
            part = place.standoff_part("standoff", gathered, center)
            fired = {(record.conditional.split("'s flat")[0], record.context): record
                     for record in evaluate.fired_conditionals(problem, (part,),
                                                               {part.name: Pose(*center)})}
            cut = cut_flats(flat_records, center)
            self.assertEqual(set(fired), set(cut), center)
            for key, records in cut.items():
                minimum_wall = records[0].flat.minimum_wall
                self.assertEqual(fired[key].margin, least_plastic(records, center) - minimum_wall)
                thin = any(check_layout.thin_flats(center, record) for record in records)
                self.assertEqual(fired[key].status == "breaks", thin, (center, key))
                seen_thin = seen_thin or thin
        self.assertTrue(seen_thin)
        for center in layout.MOUNTING_DRILL_CENTERS_MM:
            part = place.standoff_part("standoff", gathered, center)
            fired = {(record.conditional.split("'s flat")[0], record.context) for record in
                     evaluate.fired_conditionals(problem, (part,), {part.name: Pose(*center)})}
            declared = {(key, context) for right, context in place.CONTEXTS
                        for declared_center, key in layout.socket_standoff_flat_declarations(right)
                        if declared_center == center}
            self.assertEqual(fired, declared, center)


def rows_named(report, rule, context):
    return [row for row in report.rows if row.rule == rule and row.context == context]


class StandoffRunsTest(unittest.TestCase):
    def test_sixth_standoff(self):
        problem, _gathered = place.standoff_problem(
            "sixth", place.SIXTH_STANDOFF_TARGET, place.SIXTH_STANDOFF_START)
        report = placement.solve(problem)
        pose = report.answers[0].pose
        self.assertLessEqual(math.dist((pose.x, pose.y), place.SIXTH_STANDOFF_TARGET), TOLERANCE)
        self.assertEqual(report.fired, ())
        for right, context in place.CONTEXTS:
            bore = min(rows_named(report, "bore from the joint's voids", context),
                       key=lambda row: row.value)
            self.assertEqual(round(bore.value, 3),
                             check_layout.DESIGN_STANDOFF_BORE_FROM_JOINT_VOIDS_MM)
            self.assertIn("magnet slot at 48.26", bore.obstacle)
            merged = {row.obstacle: row.value for row in report.rows
                      if row.status == "merged" and row.context == context}
            self.assertEqual(round(-merged["joint block"], 3), 0.468)
            self.assertEqual(round(place.socket_values(report, context)["S150"], 3),
                             1.391 if right else 3.404)
        drill = rows_named(report, "drill inside the outline", "left")[0]
        self.assertEqual(round(drill.value, 3), 4.032)

    def test_sixth_standoff_by_scan_rule(self):
        problem, _gathered = place.standoff_problem(
            "sixth by scan.py's rule", place.SIXTH_STANDOFF_TARGET, place.SIXTH_STANDOFF_START,
            scan_rule=True)
        report = placement.solve(problem)
        self.assertFalse(report.answers[0].maps[-1].target_free)
        breaks, _fired = placement.explain(problem, "standoff", Pose(*place.SIXTH_STANDOFF_TARGET))
        broken = {(row.obstacle, row.context) for row in breaks}
        for _right, context in place.CONTEXTS:
            self.assertIn(("joint block", context), broken)
            self.assertIn(("magnet slot at 48.26 along the slant", context), broken)

    def test_north_east_standoff(self):
        problem, _gathered = place.standoff_problem("north-east", place.NORTH_EAST_STANDOFF_TARGET)
        report = placement.solve(problem)
        pose = report.answers[0].pose
        self.assertLessEqual(math.dist((pose.x, pose.y), place.NORTH_EAST_STANDOFF_TARGET),
                             TOLERANCE)
        self.assertEqual([(record.conditional, record.context) for record in report.fired],
                         [("S140's flat", "left")])
        flat = report.fired[0]
        key, center, clearance, plastic = check_layout.DESIGN_STANDOFF_FLATS[0]
        self.assertEqual(round(flat.margin + layout.STANDOFF_RELIEF_MINIMUM_WALL_MM, 3), plastic)
        for figure in ("plane 2.387", f"leaving {plastic:.3f}", "leaving 1.203",
                       f'(({center[0]:.3f}, {center[1]:.3f}), "{key}") in SOCKET_STANDOFF_FLATS'):
            self.assertIn(figure, flat.note)
        self.assertEqual(round(place.socket_values(report, "left")[key], 3), clearance)
        right = place.socket_values(report, "right")
        self.assertEqual((round(right["S130"], 3), round(right["S140"], 3)), (2.408, 2.976))


class HeadOverStripTest(unittest.TestCase):
    def test_lift(self):
        # The west insulator's top over the heads' bottom.
        lift = round(check_layout.DESIGN_NANO_STRIP_TOP_Z_MM
                     - check_layout.DESIGN_FRAME_SCREW_HEADS_BOTTOM_Z_MM, 3)
        problem = place.head_problem()
        start = Pose(*place.HEAD_OVER_STRIP_POINT)
        breaks, _fired = placement.explain(problem, "screw head", start)
        insulator = next(row for row in breaks if "west socket strip's insulator" in row.obstacle)
        self.assertEqual(round(insulator.z_overlap, 3), lift)
        free = placement.free_heights(problem, "screw head", start)
        self.assertEqual(round(placement.least_lift(free, 0.0), 3), lift)
        report = placement.solve(problem)
        self.assertEqual(round(report.answers[0].pose.z, 3), lift)


class LayoutPointTest(unittest.TestCase):
    def test_a_layout_point_keeps_the_pair_rules(self):
        # Rounded to the nearest, the second boss would stand 6.300 from
        # the first, short of the pair rule's 6.3002.
        boss = Feature("boss", Prism(geometry.Circle((0.0, 0.0), 0.0)))
        parts = tuple(Part(name, (boss,), Pose(x, 0.0), Pose(x, 0.0), place.around((x, 0.0), 1.0))
                      for name, x in (("first", 0.0), ("second", 6.3004)))
        problem = Problem(parts, (), (), (PairRule("bosses apart", "boss", 6.3002),))
        others = {"first": Pose(0.0, 0.0)}
        self.assertTrue(place.breaks_at(problem, parts[1], (6.3, 0.0), others))
        self.assertEqual(place.layout_point(problem, parts[1], Pose(6.3004, 0.0), others),
                         ((6.301, 0.0), True))

    def test_a_layout_point_is_the_nearest_its_target(self):
        # Of 0.000 and 0.001 around the answer, 0.0006 east of the
        # target, 0.000 is nearer the target and 0.001 the answer.
        boss = Feature("boss", Prism(geometry.Circle((0.0, 0.0), 0.0)))
        part = Part("boss", (boss,), Pose(0.0, 0.0), Pose(0.0, 0.0), place.around((0.0, 0.0), 1.0))
        self.assertEqual(place.layout_point(Problem((part,), (), ()), part, Pose(0.0006, 0.0), {}),
                         ((0.0, 0.0), True))

    def test_layout_points_keep_the_pair_rules_among_themselves(self):
        # The answers stand 6.3008 apart, at their targets. The first
        # rounds east to 0.001, so the second, rounded to the nearest
        # (6.301), would stand 6.300 from it, short of 6.3002, although
        # it stands 6.3004 from the first's answer.
        boss = Feature("boss", Prism(geometry.Circle((0.0, 0.0), 0.0)))
        parts = tuple(Part(name, (boss,), Pose(x, 0.0), Pose(x, 0.0), place.around((x, 0.0), 1.0))
                      for name, x in (("first", 0.0006), ("second", 6.3014)))
        problem = Problem(parts, (), (), (PairRule("bosses apart", "boss", 6.3002),))
        points = place.layout_points(problem, placement.solve(problem))
        self.assertEqual(points, [((0.001, 0.0), True), ((6.302, 0.0), True)])
        self.assertGreaterEqual(math.dist(points[0][0], points[1][0]), 6.3002)

    def test_a_fired_conditional_that_breaks_breaks_the_point(self):
        boss = Feature("boss", Prism(geometry.Circle((0.0, 0.0), 0.0)))
        block = Obstacle("block", "block", Prism(geometry.Circle((0.0, 0.0), 0.5)))
        rule = Rule("boss from the block", "boss", ("block",), CLEAR, 0.0)
        part = Part("part", (boss,), Pose(2.0, 0.0), Pose(2.0, 0.0), place.around((2.0, 0.0), 1.0))
        for margin, breaks in ((-1.0, True), (1.0, False)):
            # The rule holds at (2, 0), by 1.5, but the conditional fires
            # everywhere, standing in for it.
            flat = Conditional("flat", rule.name, ("block",), "", lambda pose: True,
                               lambda pose, margin=margin: margin, lambda pose: "a flat")
            problem = Problem((part,), (block,), (rule,), conditionals=(flat,))
            with self.subTest(margin=margin):
                self.assertEqual(place.breaks_at(problem, part, (2.0, 0.0), {}), breaks)


class FrameAndCheckPassTest(unittest.TestCase):
    def test_frame_bosses(self):
        matched = {}
        for right, context in place.CONTEXTS:
            problem, report, _places = place.solve_frame_half(right)
            points = place.layout_points(problem, report)
            self.assertTrue(all(clean for _point, clean in points))
            rows, _extras = place.committed_comparison(report, points, right)
            self.assertEqual(len(rows), len(layout.frame_boss_centers(right)))
            for boss, _answer, _point, _target, distance, committed in rows:
                self.assertLessEqual(distance, committed + TOLERANCE, boss)
            matched[right] = tuple(point for _boss, _answer, point, *_rest in rows)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                place.print_frame_half(report, points, right, context)
            extras = tuple((round(float(x), 3), round(float(y), 3))
                           for x, y in EXTRA_BOSS.findall(printed.getvalue()))
            self.assertEqual(extras, (), context)
        self.assertEqual(place.check_pass({"FRAME_BOSS_CENTERS_MM": matched}), ([], []))

    def test_standoffs_pass_every_check(self):
        for index, target, start in ((5, place.SIXTH_STANDOFF_TARGET, place.SIXTH_STANDOFF_START),
                                     (3, place.NORTH_EAST_STANDOFF_TARGET, None)):
            problem, _gathered = place.standoff_problem("check pass", target, start)
            report = placement.solve(problem)
            substitutions = place.standoff_substitutions(index, problem, report)
            self.assertEqual(substitutions["MOUNTING_DRILL_CENTERS_MM"][index], target)
            self.assertEqual(place.check_pass(substitutions), ([], []))

    def test_check_pass_records_moved_figures(self):
        drills = list(layout.MOUNTING_DRILL_CENTERS_MM)
        drills[5] = place.SIXTH_STANDOFF_START
        _failures, moved = place.check_pass({"MOUNTING_DRILL_CENTERS_MM": tuple(drills)})
        self.assertTrue(any("standoff bores from the joint's voids" in text for text in moved))
        self.assertEqual(layout.MOUNTING_DRILL_CENTERS_MM[5], place.SIXTH_STANDOFF_TARGET)


if __name__ == "__main__":
    unittest.main()
