# Plan

## Workshop

The user, 2026-10-21: "From this new model workshop repo I can then develop further things like integrations to my automatic slicer".

## kbdkid5

The goal: a smaller wireless split keyboard than kbdkid4 that also joins into one Alice-like board, firm enough for the lap. See [DESIGN.md](kbdkid5/DESIGN.md).

1. **Printed mock (now).** Tray, PCB mock and plate for both halves from `kbdkid5/scripts/layout.py`, to get a feel for size, height and the joined angle, and the fused mock (PCB mock and plate in one print) to mount switches in. Work items in [doc/work/](doc/work/).
2. **Fit check with real parts.** The nice!nano is calipered and work item 010's bay test printed. Work item 011's raised bay, with the socket strips, is not printed yet (doc/components.md says what is measured and what is not). Fit it with its socket strips, the switch, reset button, battery connector, battery, magnets and dowel pins in a printed tray, and correct the layout.
3. **PCB design** in LibrePCB: sockets, diodes and the off-board connector on the outline, keys and mounting drills of the layout. Being tried as an alternative: no PCB, a printed frame in its place holding the sockets, wired by hand (work item 008, DESIGN.md "Hand-wired frame test").
4. **Switch the exports to the PCB's STEP**, the way kbdkid4's scripts read its board, so the PCB design becomes the ground truth.
5. **Carrying case**, following kbdkid4's.
