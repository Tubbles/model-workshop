# 006 nice!nano bay test print

Status: implemented

The user's ask: test prints of the tray's nice!nano corner, "either a couple of variations or a single model with variations, like the blade test strip", to settle the bay on a real board before printing whole trays. `model/kbdkid5/scripts/export_nano_bay_test.py` exports one strip like `Slit_Test`: three bays, each `build_tray()`'s left tray with its own fits cut by one box, joined by their floors, bay k with k notches. The hook's lip, the bar's clearance and the hook's room step together, the defaults in bay 2. The room became a `MountFits` field with an `export_tray.py` override, `hook_room`. A pry recess for taking the board out went into the tray itself, so every bay has it too. In CI as `kbdkid5_Nano_Bay_Test.stl` in the `kbdkid5-tray` artifact. DESIGN.md (the nice!nano's bullets) has the figures.

Still open: the print itself. Which bay's hook holds the board and lets it go with a firm pull, which bar clearance holds the shell without lifting the board, whether a USB-C plug seats in the window (004's overmold question), and whether a tool tip levers the board out through the recess.
