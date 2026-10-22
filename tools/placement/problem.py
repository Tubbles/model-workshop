"""A placement problem as plain frozen dataclasses: parts with their
features, the obstacles, the rules between them and the objective. A
project's script builds one from its own rule functions, so the core
never imports a project. problem_json() prints one for inspection, a
function a Conditional carries shown by its name.

A rule holds in plan wherever the heights of the feature and the
obstacle overlap by more than the problem's tolerance. Every shape here
is a prism, a plan shape over a z range, so that is exact in 3D."""

import dataclasses
import functools
import json

CLEAR = "clear"  # the feature keeps the minimum from the obstacle
INSIDE = "inside"  # the feature stays the minimum inside the obstacle
MERGE = "merge"  # the feature may run into the obstacle, the rule named survivor still holding
NEAREST = "nearest"  # the squared distance from the part's target over its free degrees of freedom
LEAST_MOVE = "least move"  # the same from the part's start
MOST_CLEARANCE = "most clearance"  # the least margin of its parts, as large as it can be


@dataclasses.dataclass(frozen=True)
class Pose:
    """A part's degrees of freedom, angle in degrees about z,
    counter-clockwise."""

    x: float
    y: float
    z: float = 0.0
    angle: float = 0.0


@dataclasses.dataclass(frozen=True)
class Prism:
    """A plan shape (geometry.py) over a z range, None for every
    height."""

    shape: object
    z_range: object = None


@dataclasses.dataclass(frozen=True)
class Feature:
    """A named prism in its part's frame, whose origin is the part's
    pose."""

    name: str
    prism: Prism


@dataclasses.dataclass(frozen=True)
class Part:
    """A movable part: its features, its start and its target, the
    contexts it is placed in at once (a model's two halves, say), and
    its free degrees of freedom with their bounds as (name, low, high),
    the others held at the start. reach, when given, is how far from its
    target in plan an answer may lie and still count, so a part with
    Alternatives tries the next one beyond it."""

    name: str
    features: tuple
    start: Pose
    target: object = None
    bounds: tuple = ()
    contexts: tuple = ("",)
    reach: object = None


@dataclasses.dataclass(frozen=True)
class Obstacle:
    """A fixed prism of a kind (a socket, a joint void) in one
    context."""

    name: str
    kind: str
    prism: Prism
    context: str = ""


@dataclasses.dataclass(frozen=True)
class Rule:
    """A rule the feature of that name meets, on every part that has it,
    against every obstacle of the kinds in the part's contexts: CLEAR by
    the minimum, INSIDE by the minimum, or MERGE, which lets the feature
    run into the obstacle and reports how deep while the rule named
    survivor (which a MERGE must have) still holds."""

    name: str
    feature: str
    kinds: tuple
    relation: str = CLEAR
    minimum: float = 0.0
    survivor: object = None


@dataclasses.dataclass(frozen=True)
class PairRule:
    """A rule between the feature of that name on every two parts that
    share a context: the minimum apart."""

    name: str
    feature: str
    minimum: float = 0.0


@dataclasses.dataclass(frozen=True)
class Conditional:
    """A rule that may stand in for others, its margin a project's
    function of the pose. Where fires(pose) is true for a part, the
    instances of the rule named rule against the named obstacles in the
    context are waived, and margin(pose) must not be negative instead.
    note(pose) says what firing means, such as the declaration the
    project should add."""

    name: str
    rule: str
    obstacles: tuple
    context: str
    fires: object
    margin: object
    note: object


@dataclasses.dataclass(frozen=True)
class Option:
    """A target and bounds for a part to try instead of its own."""

    label: str
    target: Pose
    bounds: tuple


@dataclasses.dataclass(frozen=True)
class Alternatives:
    """The options a part tries in order once its own target finds no
    free pose within its reach."""

    part: str
    options: tuple


@dataclasses.dataclass(frozen=True)
class SharedVariable:
    """One value that several parts' free degrees of freedom take, the
    members as (part, degree of freedom), within low and high."""

    name: str
    members: tuple
    low: float
    high: float


@dataclasses.dataclass(frozen=True)
class Term:
    """A term of the objective for one part, or for every part when part
    is None, its weight (never negative) times its value, the terms
    summed. NEAREST and LEAST_MOVE add each part's squared distance.
    MOST_CLEARANCE takes away the least margin over every rule instance
    of the parts it concerns, their pairs (PairRule) and conditionals
    included, held at zero or more so that it never trades a rule for
    distance. One term over several parts is one least margin, which
    joins them in one group: for each part's own least margin, give each
    part a term of its own."""

    kind: str
    part: object = None
    weight: float = 1.0


@dataclasses.dataclass(frozen=True)
class Problem:
    """Everything a solve needs. tolerance is how far a margin may fall
    below zero, or heights overlap, and still count as holding, or as
    apart, and a row within binding of its minimum is binding. A Problem
    refuses what problem_errors() finds."""

    parts: tuple
    obstacles: tuple
    rules: tuple
    pair_rules: tuple = ()
    conditionals: tuple = ()
    alternatives: tuple = ()
    shared: tuple = ()
    objective: tuple = (Term(NEAREST),)
    tolerance: float = 1e-6
    binding: float = 1e-3
    name: str = ""

    def __post_init__(self):
        problems = problem_errors(self)
        if problems:
            raise ValueError("\n".join(problems))


def repeated(keys):
    """The keys that occur more than once, in their first order."""
    seen, twice = set(), []
    for key in keys:
        if key in seen and key not in twice:
            twice.append(key)
        seen.add(key)
    return twice


def keyed_names(problem):
    """(what, keys) of every name the solver keys on, which must not
    repeat: rules and pair rules share one namespace, since a survivor
    and the rows name both."""
    return (
        ("part", [part.name for part in problem.parts]),
        ("feature of a part", [(part.name, feature.name) for part in problem.parts
                               for feature in part.features]),
        ("obstacle of a kind in a context", [(obstacle.name, obstacle.kind, obstacle.context)
                                             for obstacle in problem.obstacles]),
        ("rule", [rule.name for rule in (*problem.rules, *problem.pair_rules)]),
        ("conditional in a context", [(conditional.name, conditional.context)
                                      for conditional in problem.conditionals]),
        ("conditional for a rule, an obstacle and a context",
         [(conditional.rule, name, conditional.context) for conditional in problem.conditionals
          for name in conditional.obstacles]),
        ("shared variable", [shared.name for shared in problem.shared]),
        ("shared variable for a degree of freedom", [member for shared in problem.shared
                                                     for member in shared.members]),
    )


def problem_errors(problem):
    """What a problem repeats of the names the solver keys on, every
    MERGE rule whose survivor names no rule, every rule relation and
    term kind it does not know, which it would otherwise solve as
    something else or leave out, every term naming no part, and every
    term of negative weight, which would make the solver look for the
    worst pose."""
    problems = [f"more than one {what}: {key}" for what, keys in keyed_names(problem)
                for key in repeated(keys)]
    names = {rule.name for rule in problem.rules}
    problems += [f"the merge {rule.name}'s survivor {rule.survivor} names no rule"
                 for rule in problem.rules if rule.relation == MERGE and rule.survivor not in names]
    problems += [f"the rule {rule.name}'s relation {rule.relation!r} is none of "
                 f"{(CLEAR, INSIDE, MERGE)}"
                 for rule in problem.rules if rule.relation not in (CLEAR, INSIDE, MERGE)]
    problems += [f"the term kind {term.kind!r} is none of {(NEAREST, LEAST_MOVE, MOST_CLEARANCE)}"
                 for term in problem.objective
                 if term.kind not in (NEAREST, LEAST_MOVE, MOST_CLEARANCE)]
    parts = {part.name for part in problem.parts}
    problems += [f"the {term.kind} term's part {term.part} names no part"
                 for term in problem.objective if term.part is not None and term.part not in parts]
    problems += [f"the {term.kind} term's weight {term.weight} is negative"
                 for term in problem.objective if term.weight < 0.0]
    return problems


def free_degrees(part):
    return tuple(name for name, _low, _high in part.bounds)


def bound_of(part, degree):
    for name, low, high in part.bounds:
        if name == degree:
            return (low, high)
    return None


def part_named(problem, name):
    for part in problem.parts:
        if part.name == name:
            return part
    raise KeyError(f"no part named {name}")


def options_of(problem, part):
    """The part's own target and bounds as the first Option, then its
    Alternatives' in order."""
    own = Option("its own target", part.target, part.bounds)
    later = [option for alternatives in problem.alternatives if alternatives.part == part.name
             for option in alternatives.options]
    return (own, *later)


def with_option(part, option):
    return dataclasses.replace(part, target=option.target, bounds=option.bounds)


def terms_for(problem, part):
    """The objective's terms that concern a part, NEAREST where none
    does."""
    terms = tuple(term for term in problem.objective if term.part in (None, part.name))
    return terms or (Term(NEAREST, part.name),)


def function_name(function):
    if isinstance(function, functools.partial):
        return function_name(function.func)
    return getattr(function, "__qualname__", repr(function))


def plain(value):
    """A problem's value as JSON data: a dataclass as an object with its
    type's name, a function as its name."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        fields = {field.name: plain(getattr(value, field.name))
                  for field in dataclasses.fields(value)}
        return {"type": type(value).__name__, **fields}
    if isinstance(value, (tuple, list)):
        return [plain(item) for item in value]
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if callable(value):
        return {"function": function_name(value)}
    return value


def problem_json(problem):
    return json.dumps(plain(problem), indent=1)
