# CLAUDE.md

Guidance for Claude Code working on the coffee block, in `model/coffee-block/`. Read its [README.md](README.md) first (the block, the command, the CI artifact), since this file does not repeat it. The workshop's rules are in the root [CLAUDE.md](../../CLAUDE.md).

## The script

`model/coffee-block/scripts/export_coffee_block.py` builds the block from one `Part.makeBox` and checks it is one valid solid of the expected volume. The freecadcmd quirks it works around are in the module docstring of `model/kbdkid4/scripts/board_step.py`.
