"""The placement solver (work item 016): where to put a part so that it
keeps its rules against what is around it, nearest a target, with most
clearance or with least move, and why. Generic: it never imports a
project; a project's script builds a Problem from its own rule
functions.

- problem.py: the Problem, frozen dataclasses, and problem_json().
- geometry.py: the shapes and the exact distances every margin comes
  from.
- evaluate.py: the rule instances, their rows at a pose, explain() and
  free_heights().
- space.py: the configuration space map of a part that only translates.
- solver.py: solve(), the maps, SLSQP and COBYQA, and the Report.
- report.py: the Report as text and as JSON.
- picture.py: the PNG of one context.

Lengths are millimetres: the figures the core holds itself are, such
as WINDOW_SLACK (evaluate.py), CLEARANCE_BOUND (solver.py) and the
picture's margins, so a problem in other units needs them scaled.

It runs in the placement image (docker/placement.Dockerfile, README.md
has the commands)."""

from placement.evaluate import explain, free_heights, least_lift
from placement.geometry import Circle, Convex, Outline
from placement.problem import (CLEAR, INSIDE, LEAST_MOVE, MERGE, MOST_CLEARANCE, NEAREST,
                               Alternatives, Conditional, Feature, Obstacle, Option, PairRule,
                               Part, Pose, Prism, Problem, Rule, SharedVariable, Term,
                               problem_json)
from placement.report import report_json, report_text
from placement.solver import solve

__all__ = [
    "CLEAR", "INSIDE", "LEAST_MOVE", "MERGE", "MOST_CLEARANCE", "NEAREST", "Alternatives",
    "Circle", "Conditional", "Convex", "Feature", "Obstacle", "Option", "Outline", "PairRule",
    "Part", "Pose", "Prism", "Problem", "Rule", "SharedVariable", "Term", "explain",
    "free_heights", "least_lift", "problem_json", "report_json", "report_text", "solve",
]
