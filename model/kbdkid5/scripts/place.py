"""kbdkid5's placement problems (work item 016), built from
check_layout.py's rule records (PlacementRule) and solved by
tools/placement/, one subcommand per run that validates the solver.

model/kbdkid5/README.md (Placing parts) lists the subcommands and has
the commands. Each writes its problem as JSON, its report as text and
JSON and one picture per context to tmp/place/<subcommand>/, and
prints the figures to compare with DESIGN.md's.

A record becomes an Obstacle of the kind OBSTACLE_KINDS gives its rule
(one Obstacle for records of several rules with the same kind, label,
shape and heights) and a Rule against that kind (rule_name()), so each
rule instance stands for exactly one record: Adapted.records maps
(rule, obstacle, context) back to it, which test_place.py holds the
margins to. Each
socket's SocketFlat becomes a Conditional per half, its margin
check_layout.flat_margin(). The halves are two contexts of one part, the
right half in the left half's frame as check_layout.py checks it.

The frame's bosses go as the search that placed FRAME_BOSS_CENTERS_MM
did (boss_seeds()): every key's own place and the bottom row's corners
each solved on its own, a key's corners its Alternatives, the answers
merged into the first place nearer than the bosses' spacing, and the
places solved again together under the pair rule. The seeds of the
places the user took out since (TAKEN_OUT_BOSS_SEEDS) are left out.

The standoffs' rules do not depend on where the other standoffs are,
nor the bosses' on where the other bosses are, so the part being placed
comes out of the layout's list only in the check pass (check_pass()),
which substitutes the answers, to 0.001 as layout.py states them
(layout_point(), layout_points()), into layout.py's values in memory
and runs every
check, recording the DESIGN.md figures that would move instead of
failing on them."""

import argparse
import dataclasses
import functools
import math
import os
import sys
import time

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
REPOSITORY = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPTS)))
sys.path.insert(0, os.path.join(REPOSITORY, "tools"))
sys.path.insert(0, SCRIPTS)

import check_layout  # noqa: E402
import layout  # noqa: E402
import placement  # noqa: E402
from placement import evaluate, geometry, picture  # noqa: E402
from placement.problem import (  # noqa: E402
    Alternatives, Conditional, Feature, Obstacle, Option, PairRule, Part, Pose, Prism, Problem,
    Rule, Term)
from placement.report import answer_lines  # noqa: E402

OUTPUT = os.path.join(REPOSITORY, "tmp", "place")
CONTEXTS = ((False, "left"), (True, "right"))

# The obstacle kind of each rule's records. A rule's kind is its own
# unless its records are the same obstacles as another rule's (the
# frame's tray, which a boss and its head both keep from).
OBSTACLE_KINDS = {
    "drill inside the outline": "outline",
    "drill from the switch holes": "switch hole",
    "drill from the sockets": "socket, at any height",
    "body from the sockets": "socket",
    "body from the parts": "part",
    "body from the joint's plastic": "joint plastic",
    "bore from the joint's voids": "joint void",
    "body from the parking hole": "parking hole",
    "body from the mount bodies": "mount body",
    "body from the mount voids": "mount void",
    "body as printed from the wire rooms": "wire room",
    "body as printed from the nice!nano's strips": "nice!nano strip place",
    check_layout.plate_head_hole_rule_name("top"): "plate's top layer cutout",
    check_layout.plate_head_hole_rule_name("lower"): "plate's lower layer cutout",
    "body merging with the tray": "tray to merge with",
    "body from the tray, as scan.py held it": "tray, as scan.py held it",
    "boss from the frame": "frame",
    "boss from the tray": "tray",
    "head from the tray": "tray",
    "boss inside the outline": "frame's outline",
    "head on the backing": "backing's outline",
    "head from the backing's cutouts": "backing cutout",
}
# Colours by kind, tmp/standoff_overlay.py's where it had one.
COLOURS = {
    "socket": "#787878", "socket, at any height": "#787878", "joint plastic": "#966e46",
    "joint void": "#c8a078", "tray to merge with": "#b4966e", "tray, as scan.py held it": "#b4966e",
    "part": "#78aa78", "nice!nano strip place": "#78aa78", "mount body": "#aaaaaa",
    "mount void": "#d2d2d2", "wire room": "#aac8f0", "plate's top layer cutout": "#becde1",
    "plate's lower layer cutout": "#9fb4d2", "switch hole": "#5a5a5a", "outline": "#282828",
    "frame": "#5a7896", "frame's tab wire room": "#aac8f0", "tray": "#b4966e",
    "frame's outline": "#282828", "backing's outline": "#646464", "backing cutout": "#e6c8c8",
}

SIXTH_STANDOFF_TARGET = (113.824, 59.214)  # the user's spot (DESIGN.md, Mounting)
SIXTH_STANDOFF_START = (113.324, 59.214)  # an agent's try, 0.5 west of it (doc/work/016)
NORTH_EAST_STANDOFF_TARGET = (75.724, 62.785)  # S140's flat's standoff (DESIGN.md, Standoff flats)
STANDOFF_WINDOW = 8.0  # around the target

# The frame's bosses as DESIGN.md (Hand-wired frame, Bosses) places them:
# north of each socket at (-2.8, +4.0) from its center, mirrored on the
# right half, the bottom row also at the strips' north corners
# (+-9.525, +3.1), which stand in for a key's own place where nothing
# keeps the rules within BOSS_REACH of it. BOSS_REACH and the merging of
# places nearer than the bosses' spacing are tmp/frame015/search2.py's,
# whose run on the committed scripts (tmp/tray_move/boss_search.py)
# gave FRAME_BOSS_CENTERS_MM, with the places the user took out below.
BOSS_NORTH_OFFSET = (-2.8, 4.0)
BOSS_CORNER_OFFSETS = (("west", (-9.525, 3.1)), ("east", (9.525, 3.1)))
BOSS_REACH = 3.0

# The search's places the user took out (doc/work/021: 50 M2 x 4 screws
# on hand against the 56 the two backings took), per half, each as the
# labels of the seeds whose answers merged into it, which boss_seeds()
# leaves out so that the search finds the bosses that stay. The comments
# give the work item's numbers (FRAME_BOSS_CENTERS_MM's order before it)
# and the places.
TAKEN_OUT_BOSS_SEEDS = {
    False: (
        ("S103's east corner", "S113's west corner"),  # L4 (18.574, 12.307)
        ("S110 north",),  # L9 (25.049, 70.607)
        ("S123's west corner",),  # L10 (37.624, 17.070)
        ("S133's east corner", "S143's west corner"),  # L18 (75.724, 19.451)
        ("S140 north",),  # L23 (82.199, 75.370)
        ("S143's east corner", "S153's west corner"),  # L24 (94.774, 17.070)
    ),
    True: (
        ("S103's east corner", "S113's west corner"),  # R4 (18.574, 12.307)
        ("S113's east corner", "S123's west corner"),  # R10 (37.624, 12.307)
        ("S123's east corner", "S133's west corner"),  # R15 (56.416, 17.115)
        ("S133's east corner", "S143's west corner"),  # R20 (75.724, 19.451)
        ("S143's east corner", "S153's west corner"),  # R25 (94.774, 17.070)
    ),
}

# A plan point over the west strip's insulator (layout.part_envelopes()),
# for the screw head lifted in z: its middle.
HEAD_OVER_STRIP_POINT = (39.899, 62.198)
HEAD_LIFT_BOUNDS = (-3.0, 3.0)


@dataclasses.dataclass(frozen=True)
class Adapted:
    """A Problem's obstacles, rules, features and flats' conditionals
    from records, and records, (rule, obstacle, context) to the record
    that instance stands for."""

    obstacles: tuple
    rules: tuple
    features: tuple
    conditionals: tuple
    records: dict


def context_name(right):
    return "right" if right else "left"


def obstacle_kind(record):
    if record.name == "boss from the frame" and "tab wire room" in record.obstacle:
        return "frame's tab wire room"
    return OBSTACLE_KINDS[record.name]


def rule_name(record, kind):
    """The Rule's name for a record: the record's own, with the kind
    where it is not the rule's own (the frame's tab wire rooms, whose
    minimum differs), since the core keys rules on their names."""
    return record.name if kind == OBSTACLE_KINDS[record.name] else f"{record.name} ({kind})"


def record_shape(record):
    if record.kind == "circle":
        center, radius = record.shape
        return geometry.Circle(tuple(center), radius)
    points = tuple(tuple(point) for point in record.shape)
    return geometry.Outline(points) if record.kind == "outline" else geometry.Convex(points)


def unique_name(label, kind, context, taken):
    """The label, numbered from its second shape of a kind in a context
    on (a socket's two polygons)."""
    count = taken.get((label, kind, context), 0) + 1
    taken[(label, kind, context)] = count
    return label if count == 1 else f"{label} #{count}"


def require_same(settings, key, value, what):
    if settings.setdefault(key, value) != value:
        raise ValueError(f"the records of {key} differ in their {what}: {settings[key]}, {value}")


def flat_fires(record, pose):
    return bool(check_layout.flats_cut((pose.x, pose.y), record))


def flat_margin(record, pose):
    return check_layout.flat_margin((pose.x, pose.y), record)


def flat_note(record, pose):
    """The flats the rule cuts at the pose and the declaration that
    layout.py would need for them."""
    flats = check_layout.flats_cut((pose.x, pose.y), record)
    cut = ", ".join(f"plane {flat.plane_distance:.3f} from the center leaving "
                    f"{check_layout.flat_plastic(flat):.3f} around the bore" for flat in flats)
    table = "RIGHT_SOCKET_STANDOFF_FLATS" if record.flat.right else "SOCKET_STANDOFF_FLATS"
    return f"{cut}; declare (({pose.x:.3f}, {pose.y:.3f}), \"{record.flat.key}\") in {table}"


def flat_conditionals(flat_records):
    """A Conditional per socket and half from the records with a
    SocketFlat, ((record, obstacle name, context), ...)."""
    grouped = {}
    for record, name, context in flat_records:
        grouped.setdefault((record.flat.key, context), (record, []))[1].append(name)
    return tuple(Conditional(f"{key}'s flat", record.name, tuple(names), context,
                             functools.partial(flat_fires, record),
                             functools.partial(flat_margin, record),
                             functools.partial(flat_note, record))
                 for (key, context), (record, names) in grouped.items())


def adapted(records_by_context):
    """Adapted from ((context, records), ...)."""
    obstacles, taken, rule_settings, features, records, flat_records = {}, {}, {}, {}, {}, []
    for context, gathered in records_by_context:
        for record in gathered:
            kind = obstacle_kind(record)
            shape = record_shape(record)
            key = (kind, record.obstacle, shape, record.obstacle_z_range, context)
            if key not in obstacles:
                name = unique_name(record.obstacle, kind, context, taken)
                prism = Prism(shape, record.obstacle_z_range)
                obstacles[key] = Obstacle(name, kind, prism, context)
            obstacle = obstacles[key]
            name = rule_name(record, kind)
            require_same(rule_settings, (name, record.feature, kind),
                         (record.relation, record.minimum, record.survivor), "relation or minimum")
            require_same(features, record.feature, (record.radius, record.feature_z_range),
                         "feature")
            records[(name, obstacle.name, context)] = record
            if record.flat is not None:
                flat_records.append((record, obstacle.name, context))
    rules = tuple(Rule(name, feature, (kind,), relation, minimum, survivor)
                  for (name, feature, kind), (relation, minimum, survivor) in rule_settings.items())
    part_features = tuple(Feature(name, Prism(geometry.Circle((0.0, 0.0), radius), z_range))
                          for name, (radius, z_range) in features.items())
    return Adapted(tuple(obstacles.values()), rules, part_features,
                   flat_conditionals(flat_records), records)


def scan_rule_records(right):
    """The body 0.0 from every ledge piece and magnet slot, the rule
    tmp/standoffs/scan.py held in place of the merges."""
    pieces = check_layout.ledge_pieces(right) + check_layout.magnet_slots()
    return [check_layout.standoff_body_rule("body from the tray, as scan.py held it", label,
                                            polygon, z_range)
            for label, polygon, z_range in pieces]


def standoff_records(right, scan_rule=False):
    merges = scan_rule_records(right) if scan_rule else check_layout.standoff_merges(right)
    return check_layout.standoff_rules(right) + merges


def standoff_adapted(scan_rule=False):
    return adapted([(context_name(right), standoff_records(right, scan_rule))
                    for right, _name in CONTEXTS])


def around(point, reach):
    return (("x", point[0] - reach, point[0] + reach), ("y", point[1] - reach, point[1] + reach))


def standoff_part(name, gathered, target, start=None, window=STANDOFF_WINDOW):
    start = start or target
    return Part(name, gathered.features, Pose(*start), Pose(*target), around(target, window),
                tuple(name for _right, name in CONTEXTS))


def standoff_problem(name, target, start=None, scan_rule=False):
    gathered = standoff_adapted(scan_rule)
    part = standoff_part("standoff", gathered, target, start)
    return Problem((part,), gathered.obstacles, gathered.rules,
                   conditionals=gathered.conditionals, name=name), gathered


def frame_adapted(right, standoff_centers=None):
    """Adapted from the half's frame boss rules, the standoffs at
    standoff_centers (layout.py's unless given), less those against the
    shelves under the backing: the shelves are notched for each head
    wherever it stands (layout.backing_shelf_notches()), as far as the
    ledge, which the heads keep their own rule from. check_layout.py's
    shelves are notched for FRAME_BOSS_CENTERS_MM, so they would hold a
    head to the notch cut for layout.py's boss instead (doc/work/022)."""
    centers = standoff_centers or layout.MOUNTING_DRILL_CENTERS_MM
    shelves = {label for label, _piece, _z_range in check_layout.shelf_pieces(right)}
    records = [record for record in check_layout.frame_boss_rules(centers, right)
               if record.obstacle not in shelves]
    return adapted([(context_name(right), records)])


def pair_rules():
    return tuple(PairRule(record.name, record.feature, record.minimum)
                 for record in check_layout.frame_boss_pair_rules())


def bottom_row():
    return {layout.column_key_name(column, 3) for column in range(6)} | {layout.THUMB_KEY_NAME}


def boss_seeds(right):
    """(label, target, fallback (label, target) or None) in the order
    the frame's search took them: each key's own place, else each of its
    north corners, then the bottom row's corners, less the seeds of the
    places the user took out (TAKEN_OUT_BOSS_SEEDS)."""
    sign = -1.0 if right else 1.0
    taken_out = {label for labels in TAKEN_OUT_BOSS_SEEDS[right] for label in labels}
    seeds = []
    for key, (x, y) in layout.KEY_CENTERS_MM.items():
        north = (x + sign * BOSS_NORTH_OFFSET[0], y + BOSS_NORTH_OFFSET[1])
        corners = [(side, (x + offset_x, y + offset_y))
                   for side, (offset_x, offset_y) in BOSS_CORNER_OFFSETS]
        seeds += [(f"{key} north", north, (f"{key}'s {side} corner, its fallback", corner))
                  for side, corner in corners]
        if key in bottom_row():
            seeds += [(f"{key}'s {side} corner", corner, None) for side, corner in corners]
    return [seed for seed in seeds if seed[0] not in taken_out]


def boss_part(name, gathered, target, context):
    return Part(name, gathered.features, Pose(*target), Pose(*target), around(target, BOSS_REACH),
                (context,), reach=BOSS_REACH)


def seed_problem(right, gathered):
    """Every seed as a part on its own, each fallback an Alternatives."""
    context = context_name(right)
    parts, alternatives = [], []
    for index, (label, target, fallback) in enumerate(boss_seeds(right)):
        name = f"seed {index}: {label}"
        parts.append(boss_part(name, gathered, target, context))
        if fallback is not None:
            option = Option(fallback[0], Pose(*fallback[1]), around(fallback[1], BOSS_REACH))
            alternatives.append(Alternatives(name, (option,)))
    return Problem(tuple(parts), gathered.obstacles, gathered.rules,
                   alternatives=tuple(alternatives), name=f"frame boss seeds, {context} half")


def merged_places(report):
    """[(answer, labels)] of the seeds' answers, each joining the first
    place nearer than the bosses' spacing, as the frame's search merged
    them: center to center, the pair rule's record's two radii and its
    minimum (check_layout.pair_clearance())."""
    record = check_layout.frame_boss_pair_rules()[0]
    spacing = 2.0 * record.radius + record.minimum
    places = []
    for answer in report.answers:
        if answer.pose is None:
            continue
        label = answer.part.split(": ", 1)[1] if answer.own else answer.option
        point = (answer.pose.x, answer.pose.y)
        for place in places:
            if math.dist(point, (place[0].pose.x, place[0].pose.y)) < spacing:
                if label not in place[1]:
                    place[1].append(label)
                break
        else:
            places.append((answer, [label]))
    return places


def boss_problem(right, gathered, places, seeds_report):
    """The merged places as the frame's bosses, each nearest the target
    of the seed it came from, every two apart by the pair rule."""
    context = context_name(right)
    placed = {part.name: part for part in seeds_report.parts}
    parts = tuple(dataclasses.replace(placed[answer.part], name=" and ".join(labels))
                  for answer, labels in places)
    return Problem(parts, gathered.obstacles, gathered.rules, pair_rules(),
                   name=f"the frame's bosses, {context} half")


# The check pass.


def flat_declarations(declared, old_center, new_center, fired, context):
    kept = tuple(entry for entry in declared if entry[0] != old_center)
    added = tuple((new_center, record.conditional.split("'s flat")[0]) for record in fired
                  if record.context == context)
    return kept + added


def recording_figures(moved):
    original = check_layout.require_figure

    def recording(label, computed, stated, decimals):
        ok, text = original(label, computed, stated, decimals)
        if not ok:
            moved.append(text)
        return True, text

    return original, recording


def check_pass(substitutions):
    """(failures, moved) of every check in CHECKS with layout.py's
    values substituted in memory ({name: value}) and restored after:
    the checks that fail, (name, message), and the DESIGN.md figures
    that would move, recorded instead of failing."""
    saved = {name: getattr(layout, name) for name in substitutions}
    moved, failures = [], []
    original, recording = recording_figures(moved)
    try:
        for name, value in substitutions.items():
            setattr(layout, name, value)
        check_layout.require_figure = recording
        for check in check_layout.CHECKS:
            try:
                check()
            except check_layout.CheckFailure as failure:
                failures.append((check.__name__, str(failure)))
    finally:
        check_layout.require_figure = original
        for name, value in saved.items():
            setattr(layout, name, value)
    return failures, moved


def standoff_substitutions(index, problem, report):
    """layout.py's values with standoff index at the report's answer, to
    0.001 (layout_point()), and the flats the answer fires declared on
    it."""
    new, _clean = layout_point(problem, report.parts[0], report.answers[0].pose, {})
    old = layout.MOUNTING_DRILL_CENTERS_MM[index]
    drills = list(layout.MOUNTING_DRILL_CENTERS_MM)
    drills[index] = new
    return {
        "MOUNTING_DRILL_CENTERS_MM": tuple(drills),
        "SOCKET_STANDOFF_FLATS": flat_declarations(layout.SOCKET_STANDOFF_FLATS, old, new,
                                                   report.fired, "left"),
        "RIGHT_SOCKET_STANDOFF_FLATS": flat_declarations(layout.RIGHT_SOCKET_STANDOFF_FLATS, old,
                                                         new, report.fired, "right"),
    }


# Running and writing.


def output_directory(name):
    directory = os.path.join(OUTPUT, name)
    os.makedirs(directory, exist_ok=True)
    return directory


def write_outputs(name, problem, report, contexts):
    directory = output_directory(name)
    with open(os.path.join(directory, "problem.json"), "w") as file:
        file.write(placement.problem_json(problem))
    with open(os.path.join(directory, "report.json"), "w") as file:
        file.write(placement.report_json(report))
    with open(os.path.join(directory, "report.txt"), "w") as file:
        file.write("\n".join(placement.report_text(report)) + "\n")
    for context in contexts:
        picture.draw(problem, report, context, os.path.join(directory, f"{context}.png"),
                     colours=COLOURS)
    return directory


def placed(report):
    """Whether every part of a report has a pose, the lines of those
    that have none printed instead (report.py's answer_lines())."""
    for answer in report.answers:
        if answer.pose is None:
            print("\n".join("  " + line for line in answer_lines(answer)))
    return report.feasible


def rows_of(report, rule, context=None, obstacle=None):
    return [row for row in report.rows if row.rule == rule
            and (context is None or row.context == context)
            and (obstacle is None or obstacle in row.obstacle)]


def socket_values(report, context):
    """{key: least value} of the body from every socket in a context."""
    values = {}
    for row in rows_of(report, "body from the sockets", context):
        key = row.obstacle.split("'s socket")[0]
        values[key] = min(values.get(key, math.inf), row.value)
    return values


def print_standoff_figures(report):
    pose = report.answers[0].pose
    print(f"answer ({pose.x:.4f}, {pose.y:.4f}), {report.answers[0].distance:.6f} from the target")
    for _right, context in CONTEXTS:
        for bore in sorted(rows_of(report, "bore from the joint's voids", context),
                           key=lambda row: row.value)[:1]:
            print(f"  {context}: bore {bore.value:.4f} from the {bore.obstacle} (margin "
                  f"{bore.margin:.4f} over {bore.minimum})")
        merged = [row for row in report.rows if row.status == "merged" and row.context == context]
        for row in merged:
            print(f"  {context}: body merged {-row.value:.4f} into the {row.obstacle}")
        nearest = sorted(socket_values(report, context).items(), key=lambda item: item[1])[:2]
        print(f"  {context}: nearest sockets to the body " +
              ", ".join(f"{key} {value:.3f}" for key, value in nearest))
    for row in rows_of(report, "drill inside the outline"):
        print(f"  drill {row.value:.4f} inside the outline")
    bore_circle = geometry.Circle((pose.x, pose.y), layout.STANDOFF_BORE_DIAMETER_MM / 2.0)
    outer = geometry.Outline(tuple(layout.tray_outer_polygon()))
    print(f"  bore {geometry.measure(bore_circle, outer, inside=True).value:.4f} inside the tray's "
          "outer face (a figure: no record holds it)")
    for record in report.fired:
        print(f"  fired: {record.conditional} ({record.context}), margin {record.margin:.4f}: "
              f"{record.note}")
    if not report.fired:
        print("  no flat fires")


def run_sixth_standoff(arguments):
    name = "sixth-standoff-scan-rule" if arguments.scan_rule else "sixth-standoff"
    began = time.monotonic()
    problem, _gathered = standoff_problem(name, SIXTH_STANDOFF_TARGET, SIXTH_STANDOFF_START,
                                          arguments.scan_rule)
    report = placement.solve(problem)
    solved = time.monotonic() - began
    directory = write_outputs(name, problem, report, [context for _right, context in CONTEXTS])
    print(f"{name}: solved in {solved:.2f} s, written to {directory}")
    print(f"  the target {'free' if report.answers[0].maps[-1].target_free else 'not free'} "
          "in both halves' map")
    if not placed(report):
        return
    print_standoff_figures(report)
    breaks, fired = placement.explain(problem, "standoff", Pose(*SIXTH_STANDOFF_TARGET))
    broken = [f"{row.rule}: {row.obstacle} ({row.context}) by {-row.margin:.4f}" for row in breaks]
    broken += [f"{record.conditional} by {-record.margin:.4f}" for record in fired]
    print("  at the target, breaking: " + ("; ".join(broken) or "nothing"))


def run_north_east_standoff(_arguments):
    name = "north-east-standoff"
    began = time.monotonic()
    problem, _gathered = standoff_problem(name, NORTH_EAST_STANDOFF_TARGET)
    report = placement.solve(problem)
    solved = time.monotonic() - began
    directory = write_outputs(name, problem, report, [context for _right, context in CONTEXTS])
    print(f"{name}: solved in {solved:.2f} s, written to {directory}")
    if placed(report):
        print_standoff_figures(report)


def head_problem():
    """A backing screw head held in plan over the west strip's insulator,
    free in z, by the heads' rules from the tray."""
    gathered = adapted([("left", check_layout.rules_named(
        check_layout.frame_boss_rules(layout.MOUNTING_DRILL_CENTERS_MM, False),
        ("head from the tray",)))])
    head = tuple(feature for feature in gathered.features if feature.name == "head")
    part = Part("screw head", head, Pose(*HEAD_OVER_STRIP_POINT), None,
                (("z", *HEAD_LIFT_BOUNDS),), ("left",))
    return Problem((part,), gathered.obstacles, gathered.rules,
                   objective=(Term(placement.LEAST_MOVE),), name="head-over-strip")


def run_head_over_strip(_arguments):
    began = time.monotonic()
    problem = head_problem()
    report = placement.solve(problem)
    start = Pose(*HEAD_OVER_STRIP_POINT)
    free = placement.free_heights(problem, "screw head", start)
    solved = time.monotonic() - began
    directory = write_outputs("head-over-strip", problem, report, ["left"])
    print(f"head-over-strip: solved in {solved:.2f} s, written to {directory}")
    breaks, _fired = placement.explain(problem, "screw head", start)
    for row in breaks:
        print(f"  at z +0: {row.obstacle}, {row.value:.3f} in plan against {row.minimum}, "
              f"heights overlapping {row.z_overlap:.4f}")
    print(f"  free heights {[(round(low, 6), round(high, 6)) for low, high in free]}, least lift "
          f"{placement.least_lift(free, 0.0):.6f}")
    if placed(report):
        print(f"  SLSQP's answer z {report.answers[0].pose.z:+.6f}")


def solve_frame_half(right):
    """(problem, report, places) of one half's bosses."""
    gathered = frame_adapted(right)
    seeds_report = placement.solve(seed_problem(right, gathered))
    places = merged_places(seeds_report)
    problem = boss_problem(right, gathered, places, seeds_report)
    return problem, placement.solve(problem), places


def breaks_at(problem, part, point, others):
    """Whether a part at a plan point breaks one of its rules, its
    conditionals or a pair rule with the problem's parts at their poses
    in others ({name: Pose})."""
    pose = dataclasses.replace(part.start, x=point[0], y=point[1])
    near = [other for other in problem.parts if other.name in others and other.name != part.name]
    pairs = tuple(instance for instance in evaluate.pair_instances(problem, (part, *near))
                  if part.name in (instance.part, instance.other_part))
    rows, fired = evaluate.evaluate(problem, evaluate.window_instances(problem, part) + pairs,
                                    {**others, part.name: pose}, (part,))
    return any(record.status == "breaks" for record in rows + fired)


def layout_point(problem, part, pose, others, decimals=3):
    """An answer as layout.py states a center, to decimals: of the four
    points of that grid around it, the nearest the part's target at
    which no rule breaks (breaks_at(), the other parts at others), since
    an answer on a rule's boundary rounded to the nearest can break it
    by up to half a step. (point, whether it keeps every rule)."""
    step = 10.0 ** -decimals
    xs = {round(math.floor(pose.x / step) * step, decimals),
          round(math.ceil(pose.x / step) * step, decimals)}
    ys = {round(math.floor(pose.y / step) * step, decimals),
          round(math.ceil(pose.y / step) * step, decimals)}
    reference = part.target or part.start
    candidates = sorted(((x, y) for x in xs for y in ys),
                        key=lambda point: math.dist(point, (reference.x, reference.y)))
    for candidate in candidates:
        if not breaks_at(problem, part, candidate, others):
            return candidate, True
    return candidates[0], False


def layout_points(problem, report):
    """layout_point() of every answer in order, each held to the pair
    rules against the points before it and the answers after it, so the
    points keep the pair rules among themselves."""
    parts = {part.name: part for part in report.parts}
    poses = {answer.part: answer.pose for answer in report.answers}
    points = []
    for answer in report.answers:
        others = {name: pose for name, pose in poses.items() if name != answer.part}
        point, clean = layout_point(problem, parts[answer.part], answer.pose, others)
        points.append((point, clean))
        poses[answer.part] = dataclasses.replace(answer.pose, x=point[0], y=point[1])
    return points


def committed_comparison(report, points, right):
    """(layout.py's boss, the answer nearest it, its point to 0.001, the
    answer's target, the answer's and layout.py's distances from that
    target) per boss of layout.py's, and the answers nearest none of
    them."""
    parts = {part.name: part for part in report.parts}
    rows, matched = [], set()
    for boss in layout.frame_boss_centers(right):
        index = min(range(len(points)), key=lambda each: math.dist(points[each][0], boss))
        matched.add(index)
        answer = report.answers[index]
        target = parts[answer.part].target
        rows.append((boss, answer, points[index][0], target,
                     math.dist((answer.pose.x, answer.pose.y), (target.x, target.y)),
                     math.dist(boss, (target.x, target.y))))
    extras = [index for index in range(len(points)) if index not in matched]
    return rows, extras


def print_frame_half(report, points, right, context):
    rows, extras = committed_comparison(report, points, right)
    farther = 0
    for boss, answer, point, target, distance, committed in rows:
        flag = "" if distance <= committed + 1e-9 else "  FARTHER"
        farther += bool(flag)
        print(f"  {answer.part}: ({answer.pose.x:.4f}, {answer.pose.y:.4f}), {point} to 0.001, "
              f"{distance:.3f} from ({target.x:.3f}, {target.y:.3f}); layout.py's {boss} "
              f"{committed:.3f}{flag}")
    print(f"  {farther} of layout.py's {len(rows)} farther from their target than the answer")
    for index in extras:
        answer = report.answers[index]
        print(f"  beyond layout.py's: {answer.part} at {points[index][0]} to 0.001, solved at "
              f"({answer.pose.x:.4f}, {answer.pose.y:.4f}), {answer.distance:.3f} from its "
              "target")
    unclean = [point for point, clean in points if not clean]
    print(f"  {len(unclean)} answers with no point to 0.001 that keeps every rule {unclean}")
    least = min((row for row in report.rows if row.status in ("holds", "breaks")),
                key=lambda row: row.margin)
    print(f"  least margin {least.margin:.4f}: {least.rule}, {least.part} and {least.obstacle}")
    matched = {report.answers.index(answer) for _boss, answer, *_rest in rows}
    return (tuple(points[index][0] for index in sorted(matched)),
            tuple(point for point, _clean in points))


def run_frame_bosses(_arguments):
    matched, every = {}, {}
    for right, context in CONTEXTS:
        began = time.monotonic()
        problem, report, places = solve_frame_half(right)
        solved = time.monotonic() - began
        directory = write_outputs(f"frame-bosses-{context}", problem, report, [context])
        print(f"frame bosses, {context} half: {len(report.answers)} bosses (layout.py "
              f"{len(layout.frame_boss_centers(right))}), solved in {solved:.2f} s, written to "
              f"{directory}")
        if not placed(report):
            return
        points = layout_points(problem, report)
        matched[right], every[right] = print_frame_half(report, points, right, context)
    for what, centers in (("layout.py's bosses' answers", matched), ("every answer", every)):
        failures, moved = check_pass({"FRAME_BOSS_CENTERS_MM": centers})
        print_check_pass(f"the frame's bosses at {what}", failures, moved)


def print_check_pass(what, failures, moved):
    print(f"check pass, {what}: {len(failures)} checks fail, {len(moved)} figures move")
    for check, message in failures:
        print(f"  FAIL {check}: {message[:400]}")
    for text in moved:
        print(f"  moved: {text}")


def run_check_pass(_arguments):
    for name, index, target, start in (
            ("sixth-standoff", 5, SIXTH_STANDOFF_TARGET, SIXTH_STANDOFF_START),
            ("north-east-standoff", 3, NORTH_EAST_STANDOFF_TARGET, None)):
        problem, _gathered = standoff_problem(name, target, start)
        report = placement.solve(problem)
        if not placed(report):
            continue
        substitutions = standoff_substitutions(index, problem, report)
        failures, moved = check_pass(substitutions)
        drill = substitutions["MOUNTING_DRILL_CENTERS_MM"][index]
        print_check_pass(f"{name} at {drill}", failures, moved)


COMMANDS = {
    "sixth-standoff": run_sixth_standoff,
    "north-east-standoff": run_north_east_standoff,
    "head-over-strip": run_head_over_strip,
    "frame-bosses": run_frame_bosses,
    "check-pass": run_check_pass,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=sorted(COMMANDS))
    parser.add_argument("--scan-rule", action="store_true",
                        help="sixth-standoff: hold the body 0.0 from the ledge and the magnet "
                             "slots, as tmp/standoffs/scan.py did, instead of the merges")
    arguments = parser.parse_args()
    COMMANDS[arguments.command](arguments)


if __name__ == "__main__":
    main()
