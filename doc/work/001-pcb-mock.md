# 001 PCB mock and the layout module

Status: implemented

`model/kbdkid5/scripts/layout.py` holds DESIGN.md's geometry as data. `model/kbdkid5/scripts/check_layout.py` checks it without FreeCAD. `model/kbdkid5/scripts/export_pcb.py` exports the printed PCB mock for both halves. CI runs the check and the export.
