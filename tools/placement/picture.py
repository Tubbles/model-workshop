"""The picture of a solved problem, one PNG per context, as work item
016's research (section 5) has it. In plan: the obstacles by kind, the
least margin over every rule as filled contours behind them (red where
negative), each part's configuration space obstacles outlined and
labelled by rule with its free region, the targets as crosses and the
answers' features with each rule's keep-out ring dashed. Beside it: a
zoom on one answer, the binding rows and, for a part that moves in z,
a strip with every obstacle under the answer as a bar over its z
range, the feature's range across them. A part with no pose is drawn
dotted at its least broken pose, with its target, its least margin and
a red line across each rule it breaks there, listed beside the plan.

The contours are sampled on a grid with shapely's distances, which are
exact for polygons and need no arcs, and a project's conditional
margins where they fire, asked only where the instances they stand in
for break (where a flat's conditional can fire at all). They are a
picture. The report's margins are geometry.py's."""

import matplotlib

matplotlib.use("Agg")

import textwrap  # noqa: E402

import matplotlib.colors  # noqa: E402
import matplotlib.patches  # noqa: E402
import matplotlib.pyplot as pyplot  # noqa: E402
import numpy  # noqa: E402
import shapely  # noqa: E402
from shapely.geometry import Polygon  # noqa: E402

from placement import evaluate, geometry  # noqa: E402
from placement.problem import INSIDE, MERGE  # noqa: E402

GRID_POINTS = 120  # samples across a window's wider side
VIEW_MARGIN = 4.0  # around the windows
TEXT_ROWS = 28
TEXT_WIDTH = 105  # characters a text line wraps at
MARGIN_RANGE = 3.0  # the contours' colours saturate past it


def shape_patch(shape, **style):
    if isinstance(shape, geometry.Circle):
        return matplotlib.patches.Circle(shape.center, shape.radius, **style)
    return matplotlib.patches.Polygon(shape.points, closed=True, **style)


def outline_lines(axes, region, **style):
    """Draw a shapely region's rings."""
    for polygon in getattr(region, "geoms", [region]):
        if polygon.is_empty or not hasattr(polygon, "exterior"):
            continue
        for ring in [polygon.exterior, *polygon.interiors]:
            xs, ys = ring.xy
            axes.plot(xs, ys, **style)
            style = {**style, "label": None}


def kind_colours(problem, colours):
    """A colour per obstacle kind: the project's, else the tab20 cycle."""
    cycle = pyplot.get_cmap("tab20").colors
    kinds = sorted({obstacle.kind for obstacle in problem.obstacles})
    chosen = {kind: cycle[index % len(cycle)] for index, kind in enumerate(kinds)}
    chosen.update(colours or {})
    return chosen


def view_box(problem, report, context):
    """The plan view around the context's maps, the answers, the least
    broken poses of the parts with none and the parts' starts."""
    boxes = [each.window for each in report.maps if each.context == context]
    poses = [pose for answer in report.answers for pose in (answer.pose, answer.best)
             if pose is not None]
    poses += [part.start for part in problem.parts if context in part.contexts]
    boxes += [(pose.x - 6.0, pose.y - 6.0, pose.x + 6.0, pose.y + 6.0) for pose in poses]
    low_x = min(each[0] for each in boxes) - VIEW_MARGIN
    low_y = min(each[1] for each in boxes) - VIEW_MARGIN
    high_x = max(each[2] for each in boxes) + VIEW_MARGIN
    high_y = max(each[3] for each in boxes) + VIEW_MARGIN
    return (low_x, low_y, high_x, high_y)


def draw_obstacles(axes, problem, context, view, colours):
    seen = set()
    for obstacle in problem.obstacles:
        if obstacle.context != context:
            continue
        shape = obstacle.prism.shape
        if geometry.box_gap(geometry.bounding_box(shape), view) > 0.0:
            continue
        label = None if obstacle.kind in seen else obstacle.kind
        seen.add(obstacle.kind)
        fill = not isinstance(shape, geometry.Outline)
        axes.add_patch(shape_patch(shape, facecolor=colours[obstacle.kind] if fill else "none",
                                   edgecolor=colours[obstacle.kind], alpha=0.45 if fill else 0.9,
                                   linewidth=0.8, label=label))


def signed_distances(shape, xs, ys):
    """The signed distance of every grid point to a shape's region,
    positive outside."""
    if isinstance(shape, geometry.Circle):
        return numpy.hypot(xs - shape.center[0], ys - shape.center[1]) - shape.radius
    polygon = Polygon(shape.points)
    points = shapely.points(xs, ys)
    distance = shapely.distance(points, polygon.exterior)
    return numpy.where(shapely.contains_xy(polygon, xs, ys), -distance, distance)


def instance_field(instance, xs, ys, angle):
    """An instance's margin over the grid of the part's origin, for a
    circle feature."""
    feature = instance.feature.prism.shape
    offset = geometry.turned(feature.center, angle)
    distance = signed_distances(instance.obstacle.prism.shape, xs + offset[0], ys + offset[1])
    if instance.rule.relation == INSIDE:
        return -distance - feature.radius - instance.rule.minimum
    return distance - feature.radius - instance.rule.minimum


def conditional_field(conditional, part, xs, ys, covered_field):
    """Where the conditional fires its margin, else the covered
    instances' least margin, the conditional asked only where they
    break."""
    field = covered_field.copy()
    for index in zip(*numpy.nonzero(covered_field < 0.0)):
        pose = type(part.start)(float(xs[index]), float(ys[index]), part.start.z, part.start.angle)
        if conditional.fires(pose):
            field[index] = conditional.margin(pose)
    return field


def margin_field(problem, part, context, window):
    """(xs, ys, least margin) over a part's window in a context, its
    origin sampled on the grid."""
    width, height = window[2] - window[0], window[3] - window[1]
    step = max(width, height) / GRID_POINTS
    xs, ys = numpy.meshgrid(numpy.arange(window[0], window[2] + step / 2, step),
                            numpy.arange(window[1], window[3] + step / 2, step))
    least = numpy.full(xs.shape, numpy.inf)
    covered = {}
    for instance in evaluate.window_instances(problem, part):
        if instance.context != context or instance.rule.relation == MERGE:
            continue
        field = instance_field(instance, xs, ys, part.start.angle)
        if instance.conditional is None:
            least = numpy.minimum(least, field)
        else:
            previous = covered.get(instance.conditional, numpy.full(xs.shape, numpy.inf))
            covered[instance.conditional] = numpy.minimum(previous, field)
    for conditional, field in covered.items():
        least = numpy.minimum(least, conditional_field(conditional, part, xs, ys, field))
    return xs, ys, least


def context_fields(problem, report, context):
    """(xs, ys, least margin) of every part in the context whose
    features are circles and which moves in plan, placed or not."""
    fields = []
    names = {part.name for part in report.parts}
    unplaced = tuple(part for _answer, part in unplaced_answers(problem, report)
                     if part.name not in names)
    for part in report.parts + unplaced:
        if context not in part.contexts:
            continue
        if not all(isinstance(feature.prism.shape, geometry.Circle) for feature in part.features):
            continue
        window = evaluate.window_box(part)
        if window[0] == window[2] or window[1] == window[3]:
            continue
        fields.append(margin_field(problem, part, context, window))
    return fields


def draw_fields(axes, fields):
    norm = matplotlib.colors.TwoSlopeNorm(vmin=-MARGIN_RANGE, vcenter=0.0, vmax=MARGIN_RANGE)
    levels = numpy.linspace(-MARGIN_RANGE, MARGIN_RANGE, 25)
    shown = None
    for xs, ys, least in fields:
        shown = axes.contourf(xs, ys, numpy.clip(least, -MARGIN_RANGE, MARGIN_RANGE),
                              levels=levels, cmap="RdYlGn", norm=norm, alpha=0.55, zorder=0)
    return shown


def draw_maps(axes, report, context):
    cycle = pyplot.get_cmap("Dark2").colors
    rule_colours = {}
    for each in report.maps:
        if each.context != context:
            continue
        regions = [(name, region, "-") for name, region in each.blocked]
        regions += [(name, region, "--") for name, region in each.allowed]
        for name, region, style in regions:
            first = name not in rule_colours
            colour = rule_colours.setdefault(name, cycle[len(rule_colours) % len(cycle)])
            outline_lines(axes, region, color=colour, linewidth=0.7, linestyle=style,
                          label=f"configuration space: {name}" if first else None)
        outline_lines(axes, each.free, color="black", linewidth=1.6, label=None)


def keep_out_rings(problem, part):
    """(feature, radius) of every distinct keep-out ring of a part's
    features: the feature grown by a CLEAR rule's minimum."""
    rings = set()
    for rule in problem.rules:
        if rule.relation == MERGE or rule.relation == INSIDE or rule.minimum <= 0.0:
            continue
        for feature in part.features:
            if feature.name == rule.feature and isinstance(feature.prism.shape, geometry.Circle):
                rings.add((feature.name, feature.prism.shape.radius + rule.minimum))
    return sorted(rings)


def placed_answers(report):
    """(answer, part as placed) of every answer with a pose."""
    parts = {part.name: part for part in report.parts}
    return [(answer, parts[answer.part]) for answer in report.answers if answer.pose is not None]


def unplaced_answers(problem, report):
    """(answer, part as the problem gives it) of every answer with no
    pose but a least broken one."""
    parts = {part.name: part for part in problem.parts}
    return [(answer, parts[answer.part]) for answer in report.answers
            if answer.pose is None and answer.best is not None]


def draw_unplaced(axes, problem, report, context):
    """Each part with no pose dotted at its least broken pose, its
    target and a red line across every rule it breaks there, between
    the points its margin was measured between."""
    for answer, part in unplaced_answers(problem, report):
        if context not in part.contexts:
            continue
        if part.target is not None:
            axes.plot(part.target.x, part.target.y, marker="x", color="black", markersize=9,
                      markeredgewidth=2, zorder=5)
        for index, feature in enumerate(part.features):
            shape = evaluate.placed_feature(feature, answer.best)
            axes.add_patch(shape_patch(shape, facecolor="none", edgecolor="#7b2fbe",
                                       linestyle=":", linewidth=1.4, zorder=6,
                                       label=f"{answer.part}, least broken" if index == 0
                                       else None))
        for row in answer.breaks[0]:
            if row.context != context:
                continue
            (feature_x, feature_y), (obstacle_x, obstacle_y) = row.feature_point, row.obstacle_point
            axes.plot([feature_x, obstacle_x], [feature_y, obstacle_y], color="#d21e1e",
                      linewidth=1.6, zorder=7)
            axes.annotate(f"{row.rule} {row.margin:+.3f}", (obstacle_x, obstacle_y), fontsize=6,
                          color="#d21e1e", zorder=7)


def draw_answers(axes, problem, report, context):
    for answer, part in placed_answers(report):
        if context not in part.contexts:
            continue
        if part.target is not None:
            axes.plot(part.target.x, part.target.y, marker="x", color="black", markersize=9,
                      markeredgewidth=2, zorder=5)
        pose = answer.pose
        for feature in part.features:
            shape = evaluate.placed_feature(feature, pose)
            axes.add_patch(shape_patch(shape, facecolor="none", edgecolor="#d21e1e",
                                       linewidth=1.4, zorder=6))
        for name, radius in keep_out_rings(problem, part):
            offset = next(feature.prism.shape.center for feature in part.features
                          if feature.name == name)
            center = geometry.placed_point(offset, pose.x, pose.y, pose.angle)
            axes.add_patch(matplotlib.patches.Circle(center, radius, facecolor="none",
                                                     edgecolor="#f07800", linestyle="--",
                                                     linewidth=0.9, zorder=6))


def focus_part(report, context, focus):
    placed = [(answer, part) for answer, part in placed_answers(report)
              if context in part.contexts]
    if not placed:
        return None
    if focus is not None:
        return next(pair for pair in placed if pair[0].part == focus)
    tightest = {}
    for row in report.rows:
        if row.status in ("holds", "breaks") and row.context == context:
            tightest[row.part] = min(tightest.get(row.part, numpy.inf), row.margin)
    return min(placed, key=lambda pair: tightest.get(pair[0].part, numpy.inf))


def plan_axes(axes, problem, report, context, view, colours, fields):
    shown = draw_fields(axes, fields)
    draw_obstacles(axes, problem, context, view, colours)
    draw_maps(axes, report, context)
    draw_answers(axes, problem, report, context)
    draw_unplaced(axes, problem, report, context)
    axes.set_xlim(view[0], view[2])
    axes.set_ylim(view[1], view[3])
    axes.set_aspect("equal")
    axes.grid(color="#e1e1e1", linewidth=0.5)
    return shown


def enforced_line(row):
    multiplier = "" if row.multiplier is None else f" multiplier {row.multiplier:.3g}"
    return (f"{row.margin:+.3f} {row.rule}: {row.part}'s {row.feature} and {row.obstacle}, "
            f"{row.value:.3f} against {row.minimum}{multiplier}")


def row_lines(report, context):
    """The text beside the plan: what breaks at each least broken pose
    of a part with no pose, the conditionals that fired, the merges and
    the binding or breaking rows, or the tightest rows where none
    binds."""
    lines = []
    for answer in report.answers:
        breaking = [row for row in answer.breaks[0] if row.context == context]
        if answer.pose is None and answer.best is not None and breaking:
            lines += [f"not placed: {answer.part}, at its least broken pose "
                      f"({answer.best.x:.3f}, {answer.best.y:.3f}):"]
            lines += [enforced_line(row) for row in breaking]
    lines += [f"fired {record.margin:+.3f} {record.conditional} ({record.part}): {record.note}"
              for record in report.fired if record.context == context]
    rows = [row for row in report.rows if row.context == context]
    lines += [f"merged {-row.value:.3f} {row.part}'s {row.feature} into {row.obstacle}"
              for row in rows if row.status == "merged"]
    binding = [row for row in rows if row.binding or row.status == "breaks"]
    if binding:
        return lines + ["binding:"] + [enforced_line(row) for row in binding]
    tightest = [row for row in rows if row.status == "holds"][:8]
    return lines + ["none binding; the tightest:"] + [enforced_line(row) for row in tightest]


def draw_height_strip(axes, problem, report, part, answer):
    """The z strip: every obstacle short of its rule in plan at the
    answer as a bar over its z range, the features' ranges across them
    at the answer and, dashed, at the start."""
    by_name = {obstacle.name: obstacle for obstacle in problem.obstacles}
    short = sorted({row.obstacle for row in report.rows if row.part == part.name
                    and row.relation != MERGE and row.value - row.minimum < 0.0
                    and row.obstacle in by_name and by_name[row.obstacle].prism.z_range})
    for index, name in enumerate(short):
        low, high = by_name[name].prism.z_range
        axes.bar(index, high - low, bottom=low, width=0.6, color="#8c8c8c", edgecolor="black")
    for feature in part.features:
        heights = evaluate.feature_heights(feature, answer.pose)
        start = evaluate.feature_heights(feature, part.start)
        if heights is None:
            continue
        axes.axhspan(*heights, color="#d21e1e", alpha=0.3, label=f"{feature.name} at the answer")
        axes.axhline(start[0], color="#d21e1e", linestyle="--", linewidth=0.8)
        axes.axhline(start[1], color="#d21e1e", linestyle="--", linewidth=0.8,
                     label=f"{feature.name} at its start")
    axes.set_xticks(range(len(short)))
    axes.set_xticklabels(short, rotation=80, fontsize=6)
    axes.set_ylabel("z")
    axes.set_title("under the answer, in z", fontsize=9)
    axes.legend(fontsize=6, loc="upper right")


def draw(problem, report, context, path, colours=None, focus=None, title=None):
    """Write the picture of one context to path."""
    colours = kind_colours(problem, colours)
    chosen = focus_part(report, context, focus)
    moves_in_z = chosen is not None and evaluate.moves_in_z(chosen[1])
    columns = [3.0, 2.0, 1.0] if moves_in_z else [3.0, 2.0]
    figure = pyplot.figure(figsize=(19 if moves_in_z else 17, 11), dpi=110, layout="constrained")
    grid = figure.add_gridspec(2, len(columns), width_ratios=columns, height_ratios=[1.0, 1.0])
    plan = figure.add_subplot(grid[:, 0])
    view = view_box(problem, report, context)
    fields = context_fields(problem, report, context)
    shown = plan_axes(plan, problem, report, context, view, colours, fields)
    plan.set_title(title or f"{report.name}: {context or 'the plan'}")
    if shown is not None:
        figure.colorbar(shown, ax=plan, shrink=0.6, label="least margin")
    zoom = figure.add_subplot(grid[0, 1])
    if chosen is not None:
        answer, part = chosen
        size = max(geometry.reach(feature.prism.shape) for feature in part.features) + 2.0
        zoom_view = (answer.pose.x - size, answer.pose.y - size, answer.pose.x + size,
                     answer.pose.y + size)
        plan_axes(zoom, problem, report, context, zoom_view, colours, fields)
        zoom.set_title(f"{answer.part} at ({answer.pose.x:.3f}, {answer.pose.y:.3f})", fontsize=9)
    text = figure.add_subplot(grid[1, 1])
    text.axis("off")
    wrapped = [piece for line in row_lines(report, context)
               for piece in textwrap.wrap(line, TEXT_WIDTH, subsequent_indent="    ")]
    text.text(0.0, 1.0, "\n".join(wrapped[:TEXT_ROWS]), fontsize=6,
              family="monospace", verticalalignment="top")
    handles, labels = plan.get_legend_handles_labels()
    text.legend(handles, labels, loc="lower left", fontsize=6, ncol=2, frameon=False)
    if moves_in_z:
        answer, part = chosen
        draw_height_strip(figure.add_subplot(grid[:, 2]), problem, report, part, answer)
    figure.savefig(path)
    pyplot.close(figure)
