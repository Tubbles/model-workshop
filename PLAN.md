# Plan

## Workshop

The user, 2026-10-21: "From this new model workshop repo I can then develop further things like integrations to my automatic slicer".

## kbdkid5

The keyboard [DESIGN.md](model/kbdkid5/DESIGN.md) describes, in phases:

1. **Printed mock (now).** Tray, PCB mock and plate for both halves from `model/kbdkid5/scripts/layout.py`, to get a feel for size, height and the joined angle, and the fused mock to mount switches in. Work items in [doc/work/](doc/work/).
2. **Fit check with real parts.** Fit the nice!nano with its socket strips, the switch, reset button, magnets and dowel pins in a printed tray, and correct the layout. The work items say what has been printed, doc/components.md what is measured.
3. **PCB design** in LibrePCB: sockets, diodes and the off-board connector on the outline, keys and mounting drills of the layout. Being tried as an alternative: the hand-wired frame (DESIGN.md "Hand-wired frame test", work item 008).
4. **Switch the exports to the PCB's STEP**, the way kbdkid4's scripts read its board, so the PCB design becomes the ground truth.
5. **Carrying case**, following kbdkid4's.
