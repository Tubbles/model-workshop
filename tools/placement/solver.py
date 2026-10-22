"""Solving a placement problem, by the families work item 016's
research recommends (its section 4), in its order. Each part goes
first on its own, trying its target and then its Alternatives in
order, held within its reach: by its map where it only translates
(space.py), the exact measures checking the map's point and SLSQP
moving it onto the exact boundary where the arcs left it short, or by
SLSQP alone where it turns, moves in z or finds its map empty but for
the arcs (place_by_map()). Then SLSQP runs over each
whole group of parts that PairRules, SharedVariables or one
MOST_CLEARANCE term join, unless their own answers stand
(solved_already()), starting from those answers and from their starts,
each part held within its reach. COBYQA runs where no SLSQP run ends
successful and feasible. Every margin in the Report is measured exactly
at the answer (evaluate.py), and the KKT multipliers come from the
SLSQP run that placed each part. Where no run keeps every rule, the
part's Answer has no pose, only the least broken run's, with what
breaks there (explain()): for a part on its own, the run that raises
its least margin as far as it goes (least_broken_alone()).

In a run each MOST_CLEARANCE term (problem.Term) is a variable of its
own between zero and CLEARANCE_BOUND, which every clearance constraint
of the parts it concerns must reach and the objective raises. The
least broken runs let it fall below zero."""

import dataclasses
import math

import numpy
import scipy.optimize

from placement import evaluate, space
from placement.problem import (LEAST_MOVE, MERGE, MOST_CLEARANCE, NEAREST, Term, free_degrees,
                               options_of, terms_for, with_option)

STEP = 1e-6  # the central difference step of the constraints' gradients
CLEARANCE_BOUND = 1e3  # the largest a MOST_CLEARANCE term's least margin is taken as
LOOSENING = 1e-6  # the least loosened_free() loosens a rule by, whatever the tolerance


@dataclasses.dataclass(frozen=True)
class Variable:
    """A variable of an SLSQP run: one part's degree of freedom, or a
    SharedVariable's, as ((part, degree), ...)."""

    name: str
    members: tuple
    low: float
    high: float


@dataclasses.dataclass(frozen=True)
class Constraint:
    """A margin that must not be negative: one instance's, a
    conditional's together with the instances it may waive (its margin
    where it fires, else theirs), or a part's reach in a group run. key
    is what its multiplier is reported under. A clearance constraint
    counts toward the MOST_CLEARANCE terms of its parts, a reach does
    not."""

    key: object
    parts: tuple
    margin: object
    clearance: bool = True


@dataclasses.dataclass(frozen=True)
class Attempt:
    """One run: its method, the parts it moved, their poses at its start
    and its end, its objective at its end (run_objective()), the least
    margin of its constraints there and how it ended."""

    method: str
    parts: tuple
    start: tuple
    end: tuple
    objective: float
    least_margin: float
    status: str


@dataclasses.dataclass(frozen=True)
class MapSummary:
    """A part's map in one context, or in all of them at once (context
    None): the free area, its pockets, whether the target is free there,
    the nearest free point and the point of most clearance with its
    radius."""

    context: object
    free_area: float
    pockets: int
    target_free: bool
    nearest: object
    most_clearance: object


@dataclasses.dataclass(frozen=True)
class Answer:
    """A part's placement: its pose, which keeps every rule, the option
    it came from, whether that is the part's own target rather than one
    of its Alternatives, its plan distance from that option's target,
    what came of every option tried (and of its group's runs) and its
    maps. Where no pose keeps every rule within reach, pose and option
    are None, best is the pose of the least broken run and breaks is
    what breaks there, (rows, fired) as explain() gives them with the
    other parts at their answers."""

    part: str
    pose: object
    option: object
    own: bool
    distance: object
    tried: tuple
    maps: tuple
    best: object = None
    breaks: tuple = ((), ())


@dataclasses.dataclass(frozen=True)
class Report:
    """The answers and whether each has a pose, the rows of the rule
    instances each part's runs held (part_instances()) and of the pairs
    between the parts, and the conditionals that fired, all at the
    parts' poses (a coupled group's at its least broken run where none
    kept every rule), every run with its start, the NEAREST and
    LEAST_MOVE terms' value there, and for the picture the parts as
    placed (with the option each took) and their maps (space.Map)."""

    name: str
    answers: tuple
    feasible: bool
    rows: tuple
    fired: tuple
    attempts: tuple
    objective: float
    parts: tuple
    maps: tuple


@dataclasses.dataclass(frozen=True)
class Setup:
    """What every run over some parts shares: their variables and
    constraints, the MOST_CLEARANCE terms that concern them, the rows of
    the constraint values (epigraph_rows()), the bounds and
    run_functions()."""

    variables: tuple
    constraints: tuple
    terms: tuple
    rows: tuple
    bounds: tuple
    functions: tuple


@dataclasses.dataclass(frozen=True)
class Optimized:
    """The best of some runs: its poses, whether they keep every
    constraint and its multipliers by constraint key, with every run and
    the keys of every constraint the runs held."""

    poses: dict
    feasible: bool
    multipliers: dict
    attempts: tuple
    keys: tuple


@dataclasses.dataclass(frozen=True)
class Placed:
    """One part placed on its own: its Answer, the part with the option
    it took, its runs, their multipliers and its maps."""

    answer: Answer
    candidate: object
    attempts: tuple
    multipliers: dict
    maps: tuple


def shared_lookup(problem):
    return {member: shared for shared in problem.shared for member in shared.members}


def variables_for(problem, parts):
    """The variables of a run over the parts: each free degree of
    freedom, a SharedVariable's members among the parts once."""
    lookup = shared_lookup(problem)
    names = {part.name for part in parts}
    variables, seen = [], set()
    for part in parts:
        for degree, low, high in part.bounds:
            shared = lookup.get((part.name, degree))
            if shared is None:
                variables.append(Variable(f"{part.name} {degree}", ((part.name, degree),), low,
                                          high))
            elif shared.name not in seen:
                seen.add(shared.name)
                members = tuple(member for member in shared.members if member[0] in names)
                variables.append(Variable(shared.name, members, shared.low, shared.high))
    return tuple(variables)


def poses_at(vector, variables, base):
    poses = dict(base)
    for value, variable in zip(vector, variables):
        for part, degree in variable.members:
            poses[part] = dataclasses.replace(poses[part], **{degree: float(value)})
    return poses


def vector_at(poses, variables):
    return numpy.array([getattr(poses[variable.members[0][0]], variable.members[0][1])
                        for variable in variables], dtype=float)


def instance_constraint(instance, moving_in_z):
    def margin(poses):
        return evaluate.instance_margin(instance, poses, moving_in_z)

    parts = (instance.part,)
    if instance.other_part is not None:
        parts += (instance.other_part,)
    return Constraint(instance, parts, margin)


def conditional_constraint(conditional, part_name, covered, moving_in_z):
    def margin(poses):
        pose = poses[part_name]
        if conditional.fires(pose):
            return conditional.margin(pose)
        return min(evaluate.instance_margin(instance, poses, moving_in_z) for instance in covered)

    key = evaluate.conditional_key(part_name, conditional.name, conditional.context)
    return Constraint(key, (part_name,), margin)


def reach_constraint(part):
    """How far inside its reach of its target a part stays in plan."""
    def margin(poses):
        pose = poses[part.name]
        return part.reach - math.dist((pose.x, pose.y), (part.target.x, part.target.y))

    return Constraint(("reach", part.name), (part.name,), margin, clearance=False)


def reach_constraints(part):
    """A part's reach_constraint(), none where it has no reach or no
    target."""
    if part.reach is None or part.target is None:
        return ()
    return (reach_constraint(part),)


def constraints_for(parts, instances):
    """The constraints of the instances: one each, but MERGE rules', and
    one per conditional and part for the instances it may waive."""
    moving = {part.name: evaluate.moves_in_z(part) for part in parts}
    covered = {}
    constraints = []
    for instance in instances:
        if evaluate.relation_of(instance.rule) == MERGE:
            continue
        if instance.conditional is not None:
            covered.setdefault((instance.part, instance.conditional), []).append(instance)
            continue
        in_z = moving[instance.part] or moving.get(instance.other_part, False)
        constraints.append(instance_constraint(instance, in_z))
    for (part_name, conditional), instances_covered in covered.items():
        constraints.append(conditional_constraint(conditional, part_name, tuple(instances_covered),
                                                  moving[part_name]))
    return tuple(constraints)


def least_margin(constraints, poses):
    return min((constraint.margin(poses) for constraint in constraints), default=math.inf)


def squared_distance(pose, reference, degrees):
    return sum((getattr(pose, degree) - getattr(reference, degree)) ** 2 for degree in degrees)


def term_reference(term, part):
    if term.kind == NEAREST and part.target is not None:
        return part.target
    return part.start


def term_kinds(problem, part):
    return {term.kind for term in terms_for(problem, part)}


def distance_terms(problem, parts):
    """(term, part) of the NEAREST and LEAST_MOVE terms over the parts."""
    return [(term, part) for part in parts for term in terms_for(problem, part)
            if term.kind in (NEAREST, LEAST_MOVE)]


def clearance_terms(problem, parts):
    """The MOST_CLEARANCE terms that concern the parts, each once."""
    terms = []
    for part in parts:
        for term in terms_for(problem, part):
            if term.kind == MOST_CLEARANCE and all(term is not other for other in terms):
                terms.append(term)
    return tuple(terms)


def epigraph_rows(constraints, terms, parts):
    """(constraint index, term index or None) of every row of a run's
    constraint values: a clearance constraint's margin less the variable
    of each term that concerns one of its parts, else its margin."""
    names = {part.name for part in parts}
    concerned = [names if term.part is None else {term.part} & names for term in terms]
    rows = []
    for index, constraint in enumerate(constraints):
        covering = [number for number, members in enumerate(concerned)
                    if constraint.clearance and members & set(constraint.parts)]
        rows += [(index, number) for number in covering] or [(index, None)]
    return tuple(rows)


def term_leasts(constraints, terms, rows, poses):
    """Each term's least margin at the poses over the constraints it
    concerns, CLEARANCE_BOUND where it concerns none or they all keep
    more."""
    margins = [constraint.margin(poses) for constraint in constraints]
    return [min([margins[index] for index, covering in rows if covering == number]
                + [CLEARANCE_BOUND]) for number in range(len(terms))]


def objective_value(problem, parts, poses):
    """The NEAREST and LEAST_MOVE terms' weighted sum at the poses."""
    return sum(term.weight * squared_distance(poses[part.name], term_reference(term, part),
                                              free_degrees(part))
               for term, part in distance_terms(problem, parts))


def run_objective(problem, parts, constraints, poses):
    """The whole objective a run over the parts minimizes, at the poses:
    the distance terms less each MOST_CLEARANCE term's weight times its
    least margin."""
    terms = clearance_terms(problem, parts)
    leasts = term_leasts(constraints, terms, epigraph_rows(constraints, terms, parts), poses)
    return objective_value(problem, parts, poses) - sum(
        term.weight * least for term, least in zip(terms, leasts))


def objective_center(problem, part):
    """The plan point where the part's NEAREST and LEAST_MOVE terms are
    least: their references' mean by weight, since their weighted sum of
    squared distances is the total weight times the squared distance
    from that mean, plus a constant. Its target or start where the terms
    weigh nothing."""
    pulls = [(term.weight, term_reference(term, part)) for term, _part in
             distance_terms(problem, (part,))]
    total = sum(weight for weight, _reference in pulls)
    if total == 0.0:
        reference = part.target or part.start
        return (reference.x, reference.y)
    return (sum(weight * reference.x for weight, reference in pulls) / total,
            sum(weight * reference.y for weight, reference in pulls) / total)


def constraint_gradients(constraints, dependencies, vector, count, variables, base):
    """Each constraint's central difference gradient over the run's
    variables, a row each."""
    gradients = numpy.zeros((len(constraints), len(vector)))
    for row, (constraint, indexes) in enumerate(zip(constraints, dependencies)):
        for index in indexes:
            ahead, behind = vector.copy(), vector.copy()
            ahead[index] += STEP
            behind[index] -= STEP
            gradients[row, index] = (constraint.margin(poses_at(ahead[:count], variables, base))
                                     - constraint.margin(poses_at(behind[:count], variables,
                                                                  base))) / (2.0 * STEP)
    return gradients


def run_functions(problem, parts, variables, constraints, terms, rows, base):
    """(objective, constraint values, their jacobian) of a run's vector:
    the variables, then one per MOST_CLEARANCE term (epigraph_rows())."""
    count = len(variables)
    dependencies = [[index for index, variable in enumerate(variables)
                     if any(member[0] in constraint.parts for member in variable.members)]
                    for constraint in constraints]
    row_constraints = [index for index, _number in rows]

    def objective(vector):
        value = objective_value(problem, parts, poses_at(vector[:count], variables, base))
        return value - sum(term.weight * vector[count + number] for number, term in
                           enumerate(terms))

    def values(vector):
        poses = poses_at(vector[:count], variables, base)
        margins = [constraint.margin(poses) for constraint in constraints]
        return numpy.array([margins[index] - (0.0 if number is None else vector[count + number])
                            for index, number in rows])

    def jacobian(vector):
        gradients = constraint_gradients(constraints, dependencies, vector, count, variables,
                                         base)[row_constraints]
        for row, (_index, number) in enumerate(rows):
            if number is not None:
                gradients[row, count + number] = -1.0
        return gradients

    return objective, values, jacobian


def run_method(method, functions, start, bounds, constrained):
    objective, values, jacobian = functions
    if method == "SLSQP":
        constraints = [{"type": "ineq", "fun": values, "jac": jacobian}] if constrained else []
        return scipy.optimize.minimize(objective, start, method="SLSQP", bounds=bounds,
                                       constraints=constraints,
                                       options={"maxiter": 300, "ftol": 1e-12})
    constraints = ([scipy.optimize.NonlinearConstraint(values, 0.0, numpy.inf)]
                   if constrained else [])
    return scipy.optimize.minimize(objective, start, method="COBYQA", bounds=bounds,
                                   constraints=constraints,
                                   options={"maxfev": 5000, "final_tr_radius": 1e-9})


def run_setup(problem, parts, instances, base, extra=(), floor=0.0):
    """The Setup of the runs over the parts: the instances' constraints
    and the extra ones, each MOST_CLEARANCE term's variable between
    floor and CLEARANCE_BOUND."""
    variables = variables_for(problem, parts)
    constraints = constraints_for(parts, instances) + tuple(extra)
    terms = clearance_terms(problem, parts)
    rows = epigraph_rows(constraints, terms, parts)
    bounds = [(variable.low, variable.high) for variable in variables]
    bounds += [(floor, CLEARANCE_BOUND)] * len(terms)
    return Setup(variables, constraints, terms, rows, tuple(bounds),
                 run_functions(problem, parts, variables, constraints, terms, rows, base))


def start_vector(setup, start_poses):
    """A run's start, each term's variable at its least margin there,
    within its bounds."""
    leasts = term_leasts(setup.constraints, setup.terms, setup.rows, start_poses)
    floors = [low for low, _high in setup.bounds[len(setup.variables):]]
    return numpy.append(vector_at(start_poses, setup.variables),
                        [max(least, floor) for least, floor in zip(leasts, floors)])


def run_once(problem, parts, setup, method, start_poses, base):
    """(Attempt, end poses, whether it succeeded, its multipliers) of one
    run from the start poses."""
    result = run_method(method, setup.functions, start_vector(setup, start_poses),
                        list(setup.bounds), bool(setup.rows))
    end = poses_at(result.x[:len(setup.variables)], setup.variables, base)
    attempt = Attempt(method, tuple(part.name for part in parts),
                      tuple((part.name, start_poses[part.name]) for part in parts),
                      tuple((part.name, end[part.name]) for part in parts),
                      run_objective(problem, parts, setup.constraints, end),
                      least_margin(setup.constraints, end), result.message)
    return attempt, end, result.success, getattr(result, "multipliers", None)


def best_run(outcomes, tolerance):
    """The feasible run of least objective, else the run of largest
    least margin."""
    feasible = [outcome for outcome in outcomes if outcome[0].least_margin >= -tolerance]
    if feasible:
        return min(feasible, key=lambda outcome: outcome[0].objective)
    return max(outcomes, key=lambda outcome: outcome[0].least_margin)


def multipliers_by_key(setup, multipliers):
    """Each constraint's key to its multiplier, the sum over its rows,
    which SLSQP gives in the rows' order (COBYQA gives none)."""
    if multipliers is None:
        return {}
    totals = {}
    for (index, _number), value in zip(setup.rows, multipliers):
        key = setup.constraints[index].key
        totals[key] = totals.get(key, 0.0) + float(value)
    return totals


def optimize(problem, parts, instances, starts, base, extra=(), methods=("SLSQP", "COBYQA"),
             floor=0.0):
    """The Optimized of the runs over the parts from the starts (each a
    {part: Pose}), the extra constraints held too: SLSQP from each, then
    COBYQA from each where no SLSQP run ends successful and feasible,
    the best by best_run(). floor is the run_setup()'s."""
    setup = run_setup(problem, parts, instances, base, extra, floor)
    outcomes = []
    for method in methods:
        outcomes += [run_once(problem, parts, setup, method, {**base, **start}, base)
                     for start in starts]
        if any(success and attempt.least_margin >= -problem.tolerance
               for attempt, _end, success, _multipliers in outcomes):
            break
    attempt, end, _success, multipliers = best_run(outcomes, problem.tolerance)
    return Optimized(end, attempt.least_margin >= -problem.tolerance,
                     multipliers_by_key(setup, multipliers),
                     tuple(outcome[0] for outcome in outcomes),
                     tuple(constraint.key for constraint in setup.constraints))


def part_instances(problem, part):
    """The rule instances a part's runs hold: those that could bind in
    its window (evaluate.window_instances()), or every one for a part a
    MOST_CLEARANCE term concerns, whose least margin may come from an
    obstacle well away from the window."""
    if MOST_CLEARANCE in term_kinds(problem, part):
        return evaluate.rule_instances(problem, part)
    return evaluate.window_instances(problem, part)


def map_points(problem, part, free):
    """Where the map starts the part's runs: the free point nearest
    objective_center(), where on the map the distance terms are least,
    or with a MOST_CLEARANCE term each pocket's point of most clearance
    and its point nearest objective_center(), since the map's clearance
    counts the window's edges and the runs' does not, and the term
    trades against the distance terms: any pocket may hold the answer."""
    center = objective_center(problem, part)
    if MOST_CLEARANCE not in term_kinds(problem, part):
        nearest = space.nearest_free(free, center)
        return [] if nearest is None else [nearest]
    points = []
    for piece in space.pockets(free):
        for point in (space.inscribed_circle(piece)[0], space.nearest_free(piece, center)):
            if point not in points:
                points.append(point)
    return points


def map_summary(context, free, part):
    target = part.target or part.start
    point = (target.x, target.y)
    return MapSummary(context, free.area, len(space.pockets(free)),
                      not free.is_empty and free.covers(space.Point(point)),
                      space.nearest_free(free, point), space.most_clearance(free))


def part_maps(part, instances):
    """(maps, the free region in every context, the summaries) of a part
    that only translates."""
    window = evaluate.window_box(part)
    maps = tuple(space.context_map(part, context, instances, window) for context in part.contexts)
    free = space.free_region(maps)
    summaries = tuple(map_summary(each.context, each.free, part) for each in maps)
    return maps, free, summaries + (map_summary(None, free, part),)


def loosened_free(problem, part, instances):
    """The part's free region within its reach in every context, with
    its window grown and each rule and its reach loosened by LOOSENING
    and twice the problem's tolerance, beyond what the map's arcs are
    off (space.instance_region()). Every pose that keeps every rule the
    maps hold within reach, within the tolerance, lies inside with room
    around it, so where this is empty no pose keeps every rule within
    reach. The grown window has area where a degree is pinned by equal
    bounds."""
    slack = LOOSENING + 2.0 * problem.tolerance
    low_x, low_y, high_x, high_y = evaluate.window_box(part)
    window = (low_x - slack, low_y - slack, high_x + slack, high_y + slack)
    free = space.free_region(tuple(space.context_map(part, context, instances, window, slack)
                                   for context in part.contexts))
    return space.within_reach(part, free, slack)


def map_is_answer(problem, part, point, least):
    """Whether the map's point stands as the answer: the objective has
    only distance terms, the point is where they are least, and it keeps
    every rule."""
    return (MOST_CLEARANCE not in term_kinds(problem, part)
            and point == objective_center(problem, part) and least >= -problem.tolerance)


def run_starts(part):
    """A part's runs' starts: its start and its target."""
    starts = [{part.name: part.start}]
    if part.target is not None:
        starts.append({part.name: part.target})
    return starts


def place_by_runs(problem, part, instances, extra=(), methods=("SLSQP", "COBYQA"), starts=()):
    """(pose, attempts, multipliers) of the runs by the methods from the
    starts given and the part's start and its target, the extra
    constraints held too."""
    found = optimize(problem, (part,), instances, list(starts) + run_starts(part),
                     {part.name: part.start}, extra, methods)
    return found.poses[part.name], found.attempts, found.multipliers


def map_attempt(problem, part, constraints, start):
    """The Attempt of a map's point: from the part's start to it."""
    return Attempt("map", (part.name,), ((part.name, part.start),),
                   ((part.name, start[part.name]),),
                   run_objective(problem, (part,), constraints, start),
                   least_margin(constraints, start), "the map's point")


def place_by_map(problem, part, instances, constraints, reaches):
    """(pose, attempts, multipliers, maps, summaries) of a part that only
    translates: the best of SLSQP's runs from the map's points within
    its reach (map_points()), unless the one point is the answer
    (map_is_answer()). Where no point is free within reach, SLSQP's pose,
    unless the map loosened is empty too (loosened_free()), so no pose
    keeps every rule within reach: then no pose and no run, since the
    runs are slow and only a part that no option places reports its
    least broken pose (solve_part()). The map's free region holds the
    exact one but where an INSIDE circle's arcs cut it, so COBYQA would
    find no room there either."""
    maps, free, summaries = part_maps(part, instances)
    points = map_points(problem, part, space.within_reach(part, free))
    if not points:
        if loosened_free(problem, part, instances).is_empty:
            return None, (), {}, maps, summaries
        return (*place_by_runs(problem, part, instances, reaches, ("SLSQP",)), maps, summaries)
    starts = [{part.name: dataclasses.replace(part.start, x=point[0], y=point[1])}
              for point in points]
    attempts = tuple(map_attempt(problem, part, constraints, start) for start in starts)
    if map_is_answer(problem, part, points[0], attempts[0].least_margin):
        return starts[0][part.name], attempts, {}, maps, summaries
    found = optimize(problem, (part,), instances, starts, {part.name: part.start}, reaches)
    return found.poses[part.name], attempts + found.attempts, found.multipliers, maps, summaries


def place_alone(problem, part):
    """(pose, attempts, multipliers, maps, summaries) of a part on its
    own, in the window its bounds give, held within its reach."""
    instances = part_instances(problem, part)
    reaches = reach_constraints(part)
    constraints = constraints_for((part,), instances) + reaches
    if space.mappable(part):
        return place_by_map(problem, part, instances, constraints, reaches)
    return (*place_by_runs(problem, part, instances, reaches), (), ())


def plan_distance(pose, target):
    if pose is None or target is None:
        return None
    return math.dist((pose.x, pose.y), (target.x, target.y))


def pose_least_margin(pose, attempts):
    """The least margin of the runs that ended at the pose, infinite for
    none."""
    return min((attempt.least_margin for attempt in attempts if attempt.end[0][1] == pose),
               default=math.inf)


def map_is_empty(summaries):
    return bool(summaries) and summaries[-1].free_area == 0.0


def option_outcome(problem, part, pose, least, empty):
    """(accepted, what came of an option), empty where its map was. The
    least margin counts the part's reach, which its runs hold."""
    if pose is None:
        return False, "no free pose in its window"
    distance = plan_distance(pose, part.target)
    where = f"({pose.x:.3f}, {pose.y:.3f})"
    if least < -problem.tolerance:
        prefix = "no free pose in its window, the least broken " if empty else ""
        return False, f"{prefix}{where} breaks a rule by {-least:.3f}"
    placed = f"placed alone at {where}"
    return True, placed if distance is None else f"{placed}, {distance:.3f} from it"


def least_broken_alone(problem, part):
    """(pose, attempts, least margin) of a part on its own no pose of
    which keeps every rule: SLSQP's runs from the start and the target
    that raise its least margin as far as it goes, below zero too, its
    reach held, the attempts with the problem's own objective. Such a
    run is feasible, so SLSQP converges, but only to where the least
    margin stops rising: from a start where it is stationary, such as
    the middle of a symmetric block, it stays there."""
    instances = part_instances(problem, part)
    reaches = reach_constraints(part)
    widest = dataclasses.replace(problem, objective=(Term(MOST_CLEARANCE, part=part.name),))
    found = optimize(widest, (part,), instances, run_starts(part), {part.name: part.start},
                     reaches, ("SLSQP",), floor=-CLEARANCE_BOUND)
    constraints = constraints_for((part,), instances) + reaches
    attempts = tuple(dataclasses.replace(attempt, objective=run_objective(
        problem, (part,), constraints, dict(attempt.end))) for attempt in found.attempts)
    pose = found.poses[part.name]
    return pose, attempts, pose_least_margin(pose, attempts)


def solve_part(problem, part):
    """The Placed of one part on its own, its options in order: the
    first whose pose keeps every rule within the part's reach, else no
    pose, with the least broken one the options' runs found, those of
    the options with no pose run last (least_broken_alone()). Where such
    a run finds a pose that keeps every rule after all, the runs by the
    objective start from it too and the option stands."""
    tried, attempts, broken, empty = [], [], [], []
    for index, option in enumerate(options_of(problem, part)):
        candidate = with_option(part, option)
        pose, option_attempts, multipliers, maps, summaries = place_alone(problem, candidate)
        attempts.extend(option_attempts)
        least = pose_least_margin(pose, option_attempts)
        accepted, outcome = option_outcome(problem, candidate, pose, least,
                                           map_is_empty(summaries))
        tried.append((option.label, outcome))
        if accepted:
            answer = Answer(part.name, pose, option.label, index == 0,
                            plan_distance(pose, candidate.target), tuple(tried), summaries)
            return Placed(answer, candidate, tuple(attempts), multipliers, maps)
        if pose is None:
            empty.append((index, candidate, maps, summaries))
        elif least < -problem.tolerance:
            broken.append((least, pose))
    for index, candidate, option_maps, option_summaries in empty:
        pose, option_attempts, least = least_broken_alone(problem, candidate)
        multipliers = {}
        if least >= -problem.tolerance:
            pose, more, multipliers = place_by_runs(
                problem, candidate, part_instances(problem, candidate),
                reach_constraints(candidate), starts=[{candidate.name: pose}])
            option_attempts += more
            least = pose_least_margin(pose, more)
        attempts.extend(option_attempts)
        accepted, outcome = option_outcome(problem, candidate, pose, least, True)
        tried[index] = (tried[index][0], outcome)
        if accepted:
            answer = Answer(part.name, pose, tried[index][0], index == 0,
                            plan_distance(pose, candidate.target), tuple(tried), option_summaries)
            return Placed(answer, candidate, tuple(attempts), multipliers, option_maps)
        broken.append((least, pose))
    best = max(broken, key=lambda item: item[0])[1] if broken else None
    answer = Answer(part.name, None, None, False, None, tuple(tried), summaries, best)
    return Placed(answer, part, tuple(attempts), {}, maps)


def links(problem, names, pairs):
    """(part, part) of every PairRule instance, SharedVariable and
    MOST_CLEARANCE term of every part that joins two of the parts
    named."""
    joined = [(instance.part, instance.other_part) for instance in pairs]
    for shared in problem.shared:
        members = [part for part, _degree in shared.members if part in names]
        joined += list(zip(members, members[1:]))
    if any(term.kind == MOST_CLEARANCE and term.part is None for term in problem.objective):
        members = list(names)
        joined += list(zip(members, members[1:]))
    return joined


def coupled_groups(problem, parts, pairs):
    """The groups of more than one part to solve together, in the parts'
    order: the connected components of the parts that links() joins,
    whether or not a pair keeps its rule at the parts' own answers,
    since solving a group moves its parts."""
    group_of = {part.name: {part.name} for part in parts}
    for first, second in links(problem, group_of, pairs):
        merged = group_of[first] | group_of[second]
        for name in merged:
            group_of[name] = merged
    groups = []
    for part in parts:
        if len(group_of[part.name]) > 1 and group_of[part.name] not in groups:
            groups.append(group_of[part.name])
    return [tuple(part for part in parts if part.name in group) for group in groups]


def solved_already(problem, group, pairs, poses):
    """Whether a group's own answers stand as its answer: no
    SharedVariable joins its parts, no MOST_CLEARANCE term concerns them
    (whose least margin spans their pairs), and every pair between them
    keeps its rule there. The objective is then a sum over the parts,
    each part's own answer is the least of its terms, and together they
    keep the pairs, so no joint run can do better."""
    names = {part.name: part for part in group}
    if any(member[0] in names for shared in problem.shared for member in shared.members):
        return False
    if any(MOST_CLEARANCE in term_kinds(problem, part) for part in group):
        return False
    return all(evaluate.instance_margin(instance, poses, evaluate.moves_in_z(names[instance.part])
                                        or evaluate.moves_in_z(names[instance.other_part]))
               >= -problem.tolerance for instance in pairs if instance.part in names)


def solve_group(problem, group, instances, pairs, poses):
    """The Optimized of a coupled group over its parts' instances, the
    pairs between them and each part's reach, from its parts' own
    answers and from their starts."""
    names = {part.name for part in group}
    group_instances = [instance for part in group for instance in instances[part.name]]
    group_instances += [instance for instance in pairs
                        if instance.part in names and instance.other_part in names]
    reaches = [reach_constraint(part) for part in group
               if part.reach is not None and part.target is not None]
    starts = [{part.name: poses[part.name] for part in group},
              {part.name: part.start for part in group}]
    return optimize(problem, group, group_instances, starts, poses, reaches)


def solve_groups(problem, chosen, instances, pairs, poses):
    """(poses, multipliers, attempts, {part: its group's names} of the
    parts whose group no run placed) once every coupled group that is
    not solved_already() is solved as one. A group's multipliers replace
    its parts' own, None where COBYQA placed it."""
    poses, multipliers, attempts, unplaced = dict(poses), {}, (), {}
    for group in coupled_groups(problem, chosen, pairs):
        if solved_already(problem, group, pairs, poses):
            continue
        found = solve_group(problem, group, instances, pairs, poses)
        poses.update({part.name: found.poses[part.name] for part in group})
        multipliers.update({key: found.multipliers.get(key) for key in found.keys})
        attempts += found.attempts
        if not found.feasible:
            unplaced.update({part.name: tuple(each.name for each in group) for part in group})
    return poses, multipliers, attempts, unplaced


def with_breaks(problem, answer, poses):
    """An answer with no pose, with what breaks at its best pose, the
    other parts at poses."""
    if answer.best is None:
        return answer
    others = {name: pose for name, pose in poses.items() if name != answer.part}
    return dataclasses.replace(answer,
                               breaks=evaluate.explain(problem, answer.part, answer.best, others))


def group_outcome(problem, part, group, best):
    """(label, what came of) a part's group whose runs all broke a rule
    or the part's reach."""
    distance = plan_distance(best, part.target)
    label = "with " + ", ".join(name for name in group if name != part.name)
    if None not in (part.reach, distance) and distance > part.reach + problem.tolerance:
        return label, (f"the least broken run ends {distance:.3f} from its target, beyond its "
                       f"reach {part.reach}")
    return label, "no run keeps every rule"


def final_answer(problem, answer, part, poses, unplaced):
    """A part's answer once the groups are solved: at its pose, or with
    none where its group's runs all broke a rule or a reach."""
    if answer.part in unplaced:
        best = poses[answer.part]
        answer = dataclasses.replace(
            answer, pose=None, option=None, own=False, distance=None, best=best,
            tried=answer.tried + (group_outcome(problem, part, unplaced[answer.part], best),))
    elif answer.pose is not None:
        answer = dataclasses.replace(answer, pose=poses[answer.part],
                                     distance=plan_distance(poses[answer.part], part.target))
    return with_breaks(problem, answer, poses)


def solve(problem):
    """The Report of a problem's answer."""
    placed = [solve_part(problem, part) for part in problem.parts]
    chosen = [each.candidate for each in placed if each.answer.pose is not None]
    instances = {part.name: part_instances(problem, part) for part in chosen}
    pairs = evaluate.pair_instances(problem, chosen)
    own_poses = {each.answer.part: each.answer.pose for each in placed
                 if each.answer.pose is not None}
    poses, group_multipliers, group_attempts, unplaced = solve_groups(problem, chosen, instances,
                                                                      pairs, own_poses)
    multipliers = {key: value for each in placed for key, value in each.multipliers.items()}
    multipliers.update(group_multipliers)
    every_instance = tuple(instance for part in chosen for instance in instances[part.name])
    rows, fired = evaluate.evaluate(problem, every_instance + pairs, poses, chosen, multipliers)
    answers = tuple(final_answer(problem, each.answer, each.candidate, poses, unplaced)
                    for each in placed)
    attempts = tuple(attempt for each in placed for attempt in each.attempts) + group_attempts
    maps = tuple(each_map for each in placed for each_map in each.maps)
    return Report(problem.name, answers, all(answer.pose is not None for answer in answers), rows,
                  fired, attempts, objective_value(problem, chosen, poses), tuple(chosen), maps)
