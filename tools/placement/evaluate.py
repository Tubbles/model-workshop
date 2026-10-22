"""Rule instances and their rows. An instance is one rule held by one
feature of one part against one obstacle in one context, or a PairRule
between two parts; a row is how far it keeps at the parts' poses,
measured exactly (geometry.py). explain() lists what a pose breaks and
free_heights() which heights are free at a plan pose."""

import dataclasses
import itertools

from placement import geometry
from placement.problem import INSIDE, MERGE, bound_of, free_degrees, part_named

APART = "apart"  # a PairRule's relation in a row
MULTIPLIER_FLOOR = 1e-9  # a multiplier above it marks its row binding
WINDOW_SLACK = 1.0  # rows are kept for obstacles this much past where a rule could bind


@dataclasses.dataclass(frozen=True)
class Instance:
    rule: object
    part: str
    feature: object
    context: str
    obstacle: object = None
    other_part: object = None
    other_feature: object = None
    conditional: object = None


@dataclasses.dataclass(frozen=True)
class Row:
    """An instance at the parts' poses. value is its measure, margin the
    value less the minimum, z_overlap how far the heights overlap
    (negative by their gap, None where either is every height), and the
    points the pair the measure was taken between. status is holds,
    breaks, merged (a MERGE overlapping by -value), apart (a MERGE that
    does not reach), apart in height (a part moving in z), or waived by
    the conditional that fired for it."""

    rule: str
    relation: str
    part: str
    feature: str
    obstacle: str
    kind: str
    context: str
    value: float
    minimum: float
    margin: float
    z_overlap: object
    feature_point: tuple
    obstacle_point: tuple
    status: str
    survivor: object = None
    multiplier: object = None
    binding: bool = False


@dataclasses.dataclass(frozen=True)
class Fired:
    """A Conditional that fired for a part: its margin and its note."""

    conditional: str
    rule: str
    part: str
    context: str
    margin: float
    note: str
    status: str
    multiplier: object = None
    binding: bool = False


def moves_in_z(part):
    return "z" in free_degrees(part)


def feature_heights(feature, pose):
    return geometry.shifted(feature.prism.z_range, pose.z)


def heights_meet(first, second, tolerance):
    overlap = geometry.z_overlap(first, second)
    return overlap is None or overlap > tolerance


def relation_of(rule):
    return getattr(rule, "relation", APART)


def minimum_of(rule):
    return 0.0 if relation_of(rule) == MERGE else rule.minimum


def conditional_lookup(problem):
    """(rule name, obstacle name, context) to the Conditional that may
    stand in for that instance."""
    return {(conditional.rule, name, conditional.context): conditional
            for conditional in problem.conditionals for name in conditional.obstacles}


def obstacles_by_kind(problem):
    kinds = {}
    for obstacle in problem.obstacles:
        kinds.setdefault(obstacle.kind, []).append(obstacle)
    return kinds


def rule_instances(problem, part):
    """Every instance of the problem's rules for a part in its contexts,
    in the rules' order, those whose heights cannot meet left out unless
    the part moves in z."""
    lookup = conditional_lookup(problem)
    kinds = obstacles_by_kind(problem)
    instances = []
    for rule in problem.rules:
        for feature in part.features:
            if feature.name != rule.feature:
                continue
            heights = feature_heights(feature, part.start)
            for obstacle in (obstacle for kind in rule.kinds for obstacle in kinds.get(kind, ())):
                if obstacle.context not in part.contexts:
                    continue
                if not moves_in_z(part) and not heights_meet(heights, obstacle.prism.z_range,
                                                             problem.tolerance):
                    continue
                conditional = lookup.get((rule.name, obstacle.name, obstacle.context))
                instances.append(Instance(rule, part.name, feature, obstacle.context, obstacle,
                                          conditional=conditional))
    return tuple(instances)


def pair_instances(problem, parts):
    """Every PairRule instance between two of the parts that share a
    context, in the first shared one."""
    instances = []
    for rule in problem.pair_rules:
        holders = [(part, feature) for part in parts for feature in part.features
                   if feature.name == rule.feature]
        for (first, first_feature), (second, second_feature) in itertools.combinations(holders, 2):
            shared = [context for context in first.contexts if context in second.contexts]
            if not shared:
                continue
            fixed = not moves_in_z(first) and not moves_in_z(second)
            if fixed and not heights_meet(feature_heights(first_feature, first.start),
                                          feature_heights(second_feature, second.start),
                                          problem.tolerance):
                continue
            instances.append(Instance(rule, first.name, first_feature, shared[0],
                                      other_part=second.name, other_feature=second_feature))
    return tuple(instances)


def conditionals_for(problem, part):
    """The Conditionals that may fire for a part: in one of its contexts,
    standing in for a rule of one of its features."""
    names = {feature.name for feature in part.features}
    return tuple(conditional for conditional in problem.conditionals
                 if conditional.context in part.contexts
                 and any(rule.name == conditional.rule and rule.feature in names
                         for rule in problem.rules))


def window_box(part):
    """(low x, low y, high x, high y) the part's origin may take."""
    x_range = bound_of(part, "x") or (part.start.x, part.start.x)
    y_range = bound_of(part, "y") or (part.start.y, part.start.y)
    return (x_range[0], y_range[0], x_range[1], y_range[1])


def near_window(instance, box):
    """Whether an instance could bind, or come within WINDOW_SLACK of
    it, for the part anywhere in the box."""
    if instance.obstacle is None or instance.rule.relation == INSIDE:
        return True
    reach = geometry.reach(instance.feature.prism.shape) + instance.rule.minimum + WINDOW_SLACK
    return geometry.box_gap(geometry.bounding_box(instance.obstacle.prism.shape), box) <= reach


def window_instances(problem, part):
    box = window_box(part)
    return tuple(instance for instance in rule_instances(problem, part)
                 if near_window(instance, box))


def placed_feature(feature, pose):
    return geometry.placed(feature.prism.shape, pose.x, pose.y, pose.angle)


def instance_heights(instance, poses):
    own = feature_heights(instance.feature, poses[instance.part])
    if instance.obstacle is None:
        return own, feature_heights(instance.other_feature, poses[instance.other_part])
    return own, instance.obstacle.prism.z_range


def instance_measure(instance, poses):
    shape = placed_feature(instance.feature, poses[instance.part])
    if instance.obstacle is None:
        other = placed_feature(instance.other_feature, poses[instance.other_part])
        return geometry.measure(shape, other)
    return geometry.measure(shape, instance.obstacle.prism.shape,
                            instance.rule.relation == INSIDE)


def instance_margin(instance, poses, moving_in_z):
    """The instance's margin as a constraint: its measure less its
    minimum. Where the parts move in z and the plan margin is negative,
    it is how far the heights keep apart instead (negative by the least
    move along z that parts them), so a part held in plan still has a
    gradient to climb by."""
    margin = instance_measure(instance, poses).value - minimum_of(instance.rule)
    if not moving_in_z:
        return margin
    separation = geometry.z_separation(*instance_heights(instance, poses))
    if separation is None:
        return margin
    return max(margin, separation) if margin >= 0.0 else separation


def row_status(relation, value, margin, overlap, waived_by, tolerance):
    if waived_by is not None:
        return f"waived by {waived_by}"
    if overlap is not None and overlap <= tolerance:
        return "apart in height"
    if relation == MERGE:
        return "merged" if value < 0.0 else "apart"
    return "breaks" if margin < -tolerance else "holds"


def instance_row(instance, poses, waived_by, tolerance):
    measured = instance_measure(instance, poses)
    overlap = geometry.z_overlap(*instance_heights(instance, poses))
    rule = instance.rule
    minimum = minimum_of(rule)
    margin = measured.value - minimum
    if instance.obstacle is None:
        name, kind = f"{instance.other_part}'s {instance.other_feature.name}", "part"
    else:
        name, kind = instance.obstacle.name, instance.obstacle.kind
    status = row_status(relation_of(rule), measured.value, margin, overlap, waived_by, tolerance)
    return Row(rule.name, relation_of(rule), instance.part, instance.feature.name, name, kind,
               instance.context, measured.value, minimum, margin, overlap, measured.feature_point,
               measured.obstacle_point, status, getattr(rule, "survivor", None))


def fired_conditionals(problem, parts, poses):
    """(Fired) of every Conditional that fires for one of the parts at
    its pose."""
    fired = []
    for part in parts:
        pose = poses[part.name]
        for conditional in conditionals_for(problem, part):
            if not conditional.fires(pose):
                continue
            margin = conditional.margin(pose)
            status = "breaks" if margin < -problem.tolerance else "holds"
            fired.append(Fired(conditional.name, conditional.rule, part.name, conditional.context,
                               margin, conditional.note(pose), status))
    return tuple(fired)


def row_order(row):
    """Enforced rows by margin first, then the merges by depth, then the
    rest."""
    group = {"breaks": 0, "holds": 0, "merged": 1}.get(row.status, 2)
    return (group, row.margin)


def is_binding(margin, multiplier, problem):
    return margin <= problem.binding or (multiplier or 0.0) > MULTIPLIER_FLOOR


def with_multiplier(record, multiplier, problem):
    """A row or a Fired with its KKT multiplier and whether it binds: by
    its margin, or for a row apart in height by the heights' gap."""
    if record.status == "apart in height":
        return dataclasses.replace(record, multiplier=multiplier,
                                   binding=is_binding(-record.z_overlap, multiplier, problem))
    if record.status not in ("holds", "breaks"):
        return record
    return dataclasses.replace(record, multiplier=multiplier,
                               binding=is_binding(record.margin, multiplier, problem))


def conditional_key(part, name, context):
    """What a conditional's multiplier and firing are keyed on for a
    part: its name repeats across contexts (a socket's flat on each
    half)."""
    return (part, name, context)


def evaluate(problem, instances, poses, parts, multipliers=None):
    """(rows, fired) of the instances at the parts' poses, the rows in
    row_order(), an instance a fired conditional stands in for waived.
    multipliers maps an instance, or a conditional's conditional_key(),
    to its KKT multiplier from the solve that placed it."""
    multipliers = multipliers or {}
    fired = tuple(with_multiplier(record, multipliers.get(
        conditional_key(record.part, record.conditional, record.context)), problem)
                  for record in fired_conditionals(problem, parts, poses))
    fired_keys = {conditional_key(record.part, record.conditional, record.context)
                  for record in fired}
    rows = []
    for instance in instances:
        conditional = instance.conditional
        waived = conditional is not None and conditional_key(
            instance.part, conditional.name, conditional.context) in fired_keys
        row = instance_row(instance, poses, conditional.name if waived else None,
                           problem.tolerance)
        rows.append(with_multiplier(row, multipliers.get(instance), problem))
    return tuple(sorted(rows, key=row_order)), fired


def explain(problem, part_name, pose, others=None):
    """(rows, fired) a part at pose breaks, worst first, over every rule
    instance of the part with no window, the other parts at their poses
    in others ({name: Pose}) or at their starts: the rows that break and
    the fired conditionals whose margin is negative."""
    part = part_named(problem, part_name)
    poses = {other.name: other.start for other in problem.parts}
    poses.update(others or {})
    poses[part_name] = pose
    pairs = tuple(instance for instance in pair_instances(problem, problem.parts)
                  if part_name in (instance.part, instance.other_part))
    rows, fired = evaluate(problem, rule_instances(problem, part) + pairs, poses, (part,))
    return (tuple(row for row in rows if row.status == "breaks"),
            tuple(record for record in fired if record.status == "breaks"))


def blocked_heights(instance, poses, tolerance):
    """The z values of the part at which an instance short of its
    minimum in plan would have its heights overlap by more than the
    tolerance, as an open (low, high) interval, None where either height
    is every height."""
    pose = poses[instance.part]
    feature_z, obstacle_z = instance_heights(instance, poses)
    if feature_z is None or obstacle_z is None:
        return None
    return (pose.z + obstacle_z[0] - feature_z[1] + tolerance,
            pose.z + obstacle_z[1] - feature_z[0] - tolerance)


def free_heights(problem, part_name, pose):
    """The part's z values within its z bounds (pose.z alone without
    them) at which none of its rules breaks with its plan at pose, as
    closed (low, high) intervals: every instance short of its minimum in
    plan blocks the heights where it would meet. MERGE rules and
    conditionals do not take part."""
    part = part_named(problem, part_name)
    poses = {other.name: other.start for other in problem.parts}
    poses[part_name] = pose
    low, high = bound_of(part, "z") or (pose.z, pose.z)
    free = [(low, high)]
    for instance in rule_instances(problem, part):
        if instance.rule.relation == MERGE:
            continue
        short = instance_measure(instance, poses).value - instance.rule.minimum
        if short >= -problem.tolerance:
            continue
        blocked = blocked_heights(instance, poses, problem.tolerance)
        if blocked is None:
            return ()
        free = [piece for start, end in free
                for piece in ((start, min(end, blocked[0])), (max(start, blocked[1]), end))
                if piece[0] <= piece[1]]
    return tuple(free)


def least_lift(intervals, z):
    """How far above z the nearest free height lies, None if none does."""
    above = [max(low, z) for low, high in intervals if high >= z]
    return min(above) - z if above else None
