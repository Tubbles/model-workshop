# 016 Placement solver

Status: implemented

The user, 2026-10-21: "And honestly we need a better tool for "jiggling" stuff in place, a subagent trying every possibility of a N dimensional problem is extremely wasteful. There has to be some algorithm we can leverage for that", and "Yes let's create that next, make sure to make it very generic so we can use it for any model in the workshop repo. Data oriented. Do deep research into the topic first so we get a robust tool".

Why: on 2026-10-21 every placement question was answered by a grid scan written from scratch, each taking most of an hour: the hand-wired frame's bosses (tmp/frame014, tmp/frame015), the battery's place and turn (tmp/tray_move/battery_search.py), and the sixth standoff by S150 (tmp/standoffs). A scan's own rules also drifted from the project's checks: tmp/standoffs/scan.py held magnet slots to 0.0, where the tray keeps voids 0.5 from a standoff.

Scope:

- Research first, written up before any code: configuration space and Minkowski sums, no-fit polygons from 2D nesting, separating axis and penetration depth push-out from physics engines, constrained optimization (sequential quadratic programming, penalty and augmented Lagrangian methods, derivative-free methods such as Nelder-Mead), signed distance fields, and how existing tools (for example libnest2d, SVGnest, shapely, scipy.optimize) solve the same problems. What each is good at, where each fails, and which fits this repository.
- A generic tool for every model in the workshop, not kbdkid5's alone, data oriented: the movable parts, their degrees of freedom and limits, the fixed obstacles, the clearance each pair needs (or a merge allowed, with the rule that still holds, such as plastic around a bore) and the objective (nearest to a preferred pose, most clearance, fewest moves) given as data, and a report of the solved poses, each constraint's margin and which constraints bind.
- All three dimensions, not a plan view with heights bolted on: the user, 2026-10-21: "Make sure it handles all 3 dimensions as well, for e.g. backing screws". Parts and obstacles are solids, or plan shapes with z ranges where that is exact, and a pose can move along z too. The hand-wired frame's backing screws are the example: their heads hang under the backing, over the nice!nano's socket strips, where only height decides whether they fit.
- A project keeps one source of its rules: kbdkid5's obstacles and clearances come from what `check_layout.py` already checks, not from a second copy.
- Libraries are open: the user, 2026-10-21: "I can install anything you need". The research names what to install and why, and the user installs it (in the image, below). Runs locally, like `check_layout.py`.
- A picture of the solution and the feasible region, like tmp/standoff_overlay.py's overlay, so the user can see why a spot is or is not free.

Decided: the research is `work/research/placement-solver.md` (untracked), and the user answered its open questions, 2026-10-21:

- Generic: "Solver is generic, should be applyable to kbdkid as well as camera arm or any other future model". Its core never imports a project: a project's script hands it data.
- It lives in `tools/placement/` at the repository root, as the research proposes (section 6), since it serves every project under `model/` and is not one.
- It runs in an image, `docker/placement.Dockerfile`, through podman, by the root CLAUDE.md's tooling rule, rather than in the uv venv the research proposed. README.md has the commands.
- The picture is drawn with matplotlib.
- Refactors are encouraged and need no asking: "Yes absolutely, no need to even ask permission for that? Refactors are encouraged". `check_layout.py`'s standoff and frame boss rules become records, `standoff_rules()` and `frame_boss_rules()`, that its checks and the solver's kbdkid5 script both read (section 5), in a commit of their own before the tool.
- The plate's head holes against the switch cutouts become a `check_layout.py` rule at 0.5 (the user had no preference), so the solver sees it. Done: `check_plate_head_holes()`, its rules in `standoff_rules()`. The 0.5 was to be `plate_shape.py`'s `SUPPORTED_HOLE_THRESHOLD`, which is a fraction of a hole's volume rather than a distance, so the rule has its own `PLATE_HEAD_HOLE_FROM_CUTOUTS_MM`. DESIGN.md (Mounting) has what each moved standoff's hole keeps.

Done: the tool, `tools/placement/` (the root README.md, The placement solver), with the research's solver families (section 4), and kbdkid5's problems for it, `model/kbdkid5/scripts/place.py` (kbdkid5's README.md, Placing parts), whose runs reproduce the research's five validations (section 7) and whose `test_place.py` holds them. The frame's backing heights now come from `layout.py` (`backing_top_z()` and the functions beside it) rather than from DESIGN.md's figures.

The frame bosses' run found one boss place more on each half than `FRAME_BOSS_CENTERS_MM` held, and the frame took both (DESIGN.md, Hand-wired frame, Bosses). Work item 019 took the left half's away again with the parking boss back.

Open: the solver has no frontier or lexicographic objectives yet, nor the research's slabs for a part free in plan and z at once: a z degree of freedom goes through SLSQP, and `free_heights()` answers it exactly at a plan pose.
