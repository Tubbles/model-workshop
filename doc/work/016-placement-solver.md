# 016 Placement solver

Status: todo

The user, 2026-10-21: "And honestly we need a better tool for "jiggling" stuff in place, a subagent trying every possibility of a N dimensional problem is extremely wasteful. There has to be some algorithm we can leverage for that", and "Yes let's create that next, make sure to make it very generic so we can use it for any model in the workshop repo. Data oriented. Do deep research into the topic first so we get a robust tool".

Why: on 2026-10-21 every placement question was answered by a grid scan written from scratch, each taking most of an hour: the hand-wired frame's bosses (tmp/frame014, tmp/frame015), the battery's place and turn (tmp/tray_move/battery_search.py), and the sixth standoff by S150 (tmp/standoffs). A scan's own rules also drifted from the project's checks: tmp/standoffs/scan.py held magnet slots to 0.0, where the tray keeps voids 0.5 from a standoff.

Scope:

- Research first, written up before any code: configuration space and Minkowski sums, no-fit polygons from 2D nesting, separating axis and penetration depth push-out from physics engines, constrained optimization (sequential quadratic programming, penalty and augmented Lagrangian methods, derivative-free methods such as Nelder-Mead), signed distance fields, and how existing tools (for example libnest2d, SVGnest, shapely, scipy.optimize) solve the same problems. What each is good at, where each fails, and which fits this repository.
- A generic tool for every model in the workshop, not kbdkid5's alone, data oriented: the movable parts, their degrees of freedom and limits, the fixed obstacles, the clearance each pair needs (or a merge allowed, with the rule that still holds, such as plastic around a bore) and the objective (nearest to a preferred pose, most clearance, fewest moves) given as data, and a report of the solved poses, each constraint's margin and which constraints bind.
- A project keeps one source of its rules: kbdkid5's obstacles and clearances come from what `check_layout.py` already checks, not from a second copy.
- Libraries are open: the user, 2026-10-21: "I can install anything you need". The research names what to install and why, and the user installs it (in the repository's container or a project venv, by the repository's tooling rule). Runs locally, like `check_layout.py`.
- A picture of the solution and the feasible region, like tmp/standoff_overlay.py's overlay, so the user can see why a spot is or is not free.

Open: where the tool lives in the workshop, how heights (z ranges) enter a mostly plan view problem, and which solver families the research recommends.
