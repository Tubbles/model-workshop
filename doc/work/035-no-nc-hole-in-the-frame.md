# 035 No NC pad hole in the frame

Status: implemented (2026-10-29, f13fcf5)

The user, 2026-10-29: "let's also remove the redundant switch hole: there is a hole at NE of each switch footprint that isn't used for anything".

Specification:

- The frame's footprint holes, both halves, leave out the 1.2 hole at footprint-local (4.2, -5.22), where kbdkid4's hand solder footprint has its NC pad: 5.22 east and 4.2 north of each key's center. No part of the switch reaches it (doc/components.md, section 9).
- The PCB mock, the plate and the socket test strips keep it. The frame's bosses stay where they are.

Verify: `check_layout.py` passes. CI's frame export passes and counts five holes per key. DESIGN.md follows.
