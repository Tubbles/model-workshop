# CLAUDE.md

Guidance for Claude Code working on the solder spool axle, in `model/solder-spool-axle/`. Read its [README.md](README.md) first (the axle and its figures, the command, the CI artifact), since this file does not repeat it. The workshop's rules are in the root [CLAUDE.md](../../CLAUDE.md).

## The script

`model/solder-spool-axle/scripts/export_spool_axle.py` builds the axle from Part primitives, with no STEP input, and checks the solid's volume against the analytic value, rounded edges included. The freecadcmd quirks it works around are in the module docstring of `model/kbdkid4/scripts/board_step.py`.
