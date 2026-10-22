"""A Report as text for a terminal and as JSON for a file: the answers
(or for a part no pose places, what breaks at the best one), the
conditionals that fired, the merges with their depth and their
survivor's margin, the runs and the rows sorted by margin, binding ones
marked with their KKT multiplier."""

import json

from placement.problem import plain


def point_text(point):
    return "none" if point is None else f"({point[0]:.3f}, {point[1]:.3f})"


def pose_text(pose):
    if pose is None:
        return "none"
    text = f"({pose.x:.3f}, {pose.y:.3f}"
    if pose.z:
        text += f", z {pose.z:+.3f}"
    if pose.angle:
        text += f", {pose.angle:.3f} degrees"
    return text + ")"


def summary_text(summary):
    where = "every context" if summary.context is None else summary.context
    most = summary.most_clearance
    clearance = "none" if most is None else f"{point_text(most[0])} by {most[1]:.3f}"
    target = "free" if summary.target_free else "not free"
    return (f"{where}: {summary.free_area:.3f} free in {summary.pockets} pockets, the target "
            f"{target}, the nearest free point {point_text(summary.nearest)}, the most "
            f"clearance at {clearance}")


def break_text(row):
    return (f"breaks {row.rule} by {-row.margin:.4f}: {row.part}'s {row.feature} and "
            f"{row.obstacle} ({row.context or 'its context'})")


def fired_break_text(record):
    return (f"breaks {record.conditional} by {-record.margin:.4f} "
            f"({record.context or 'its context'}): {record.note}")


def unplaced_lines(answer):
    """The lines of an answer with no pose: where its least broken run
    ended and what breaks there, never as a placement (its tried lines
    say where a reach broke)."""
    if answer.best is None:
        return [f"{answer.part}: not placed"]
    rows, fired = answer.breaks
    return ([f"{answer.part}: not placed, the least broken run ends at {pose_text(answer.best)}"]
            + ["  " + break_text(row) for row in rows]
            + ["  " + fired_break_text(record) for record in fired])


def answer_lines(answer):
    if answer.pose is None:
        lines = unplaced_lines(answer)
    else:
        distance = "" if answer.distance is None else f", {answer.distance:.3f} from its target"
        lines = [f"{answer.part}: {pose_text(answer.pose)} by {answer.option}{distance}"]
    lines += [f"  tried {label}: {outcome}" for label, outcome in answer.tried]
    lines += [f"  map, {summary_text(summary)}" for summary in answer.maps]
    return lines


def height_text(row):
    if row.z_overlap is None:
        return ""
    if row.z_overlap > 0.0:
        return f", heights overlapping {row.z_overlap:.3f}"
    return f", heights {-row.z_overlap:.3f} apart"


def row_text(row):
    mark = "*" if row.binding else " "
    multiplier = "" if row.multiplier is None else f", multiplier {row.multiplier:.4g}"
    return (f"{mark} {row.margin:+9.4f}  {row.rule}: {row.part}'s {row.feature} and "
            f"{row.obstacle} ({row.kind}, {row.context or 'its context'}): {row.value:.4f} "
            f"against {row.minimum}{height_text(row)}, {row.status}{multiplier}, between "
            f"{point_text(row.feature_point)} and {point_text(row.obstacle_point)}")


def survivor_text(row, rows):
    """How a merge's survivor stands among the rows: its least margin
    over its enforced rows of the same part and context."""
    own = [other for other in rows if other.rule == row.survivor and other.part == row.part
           and other.context == row.context and other.status in ("holds", "breaks")]
    if not own:
        return f"no enforced row of {row.survivor}"
    least = min(own, key=lambda other: other.margin)
    return f"{row.survivor} at {least.margin:+.4f}, {least.status}"


def merge_text(row, rows):
    return (f"{row.part}'s {row.feature} merged {-row.value:.4f} into {row.obstacle} "
            f"({row.context or 'its context'}), {survivor_text(row, rows)}")


def fired_text(record):
    mark = "*" if record.binding else " "
    multiplier = "" if record.multiplier is None else f", multiplier {record.multiplier:.4g}"
    return (f"{mark} {record.margin:+9.4f}  {record.conditional} for {record.part} "
            f"({record.context or 'its context'}), standing in for {record.rule}: "
            f"{record.note}, {record.status}{multiplier}")


def attempt_text(attempt):
    starts = ", ".join(f"{name} {pose_text(pose)}" for name, pose in attempt.start)
    ends = ", ".join(f"{name} {pose_text(pose)}" for name, pose in attempt.end)
    return (f"{attempt.method} from {starts} to {ends}: objective {attempt.objective:.6g}, "
            f"least margin {attempt.least_margin:+.4f}, {attempt.status}")


def report_text(report):
    """The report as lines of text."""
    lines = [f"{report.name}"]
    if not report.feasible:
        lines.append("not placed: " + ", ".join(answer.part for answer in report.answers
                                                if answer.pose is None))
    lines.append("answers:")
    lines += ["  " + line for answer in report.answers for line in answer_lines(answer)]
    lines.append(f"objective {report.objective:.6g}")
    lines.append("conditionals that fired:")
    lines += ["  " + fired_text(record) for record in report.fired] or ["  none"]
    merged = [row for row in report.rows if row.status == "merged"]
    lines.append("merges:")
    lines += ["  " + merge_text(row, report.rows) for row in merged] or ["  none"]
    lines.append("runs:")
    lines += ["  " + attempt_text(attempt) for attempt in report.attempts] or ["  none"]
    enforced = [row for row in report.rows if row.status in ("holds", "breaks") or row.binding]
    lines.append(f"rows, by margin ({len(enforced)} enforced, * binding):")
    lines += ["  " + row_text(row) for row in enforced]
    others = [row for row in report.rows
              if row.status not in ("holds", "breaks", "merged") and not row.binding]
    lines.append(f"rows not enforced ({len(others)}): "
                 + ", ".join(sorted({row.status for row in others})))
    return lines


def report_json(report):
    """The report as JSON, its maps left out (shapely geometries, which
    the picture draws) and the parts as placed (their answers say which
    option each took)."""
    data = plain(report)
    data.pop("maps")
    data.pop("parts")
    return json.dumps(data, indent=1)
