# 036 Power switch's knob trough on the tray's outer face

Status: implemented (2026-10-29, 8c57242 and 685dd08)

The user, 2026-10-29: "could you move in the power switch so it doesn't stick out so much? I want the middle "trough" of the outside of the switch lever to align with the outside of the wall of the tray". Shown an overlay of the switch 2.04 further in (`tmp/power_switch/overlay.py`, untracked): "The power switch overlay looks good".

Specification:

- The trough is the V in the middle of the knob's tip, 0.76 short of the tip, read off the MFP 140 drawing with the knob's 3.4 as the scale (doc/components.md, section 2, Unconfirmed). Its sides end 0.88 short of the tip and its peaks lie 0.86 either side of the middle.
- On both halves the switch moves in until the trough lies on the tray's outer face as printed: the body's north face 2.04 from the ledge's face as modelled, since the stop's face and the outer face each swell 0.2. The peaks stand 0.8 proud.
- A stop on the ledge's face takes the body's north face, the knob slot running on through it. The cradle, the retainer's socket and the backing's cutout around the retainer move with the switch, and the outer edge's shelf ends 0.5 short of the body going in, which slides the knob's 5.0 along the floor from its new seat.
- Moved with the body, the retainer comes under S100's frame pocket walls in plan, so its top comes down to 0.5 under their mouth as printed, out of the walls' rule's heights: its part is 0.4 shorter, its opening as it was.

Verify: `check_layout.py` passes. CI's tray and frame exports pass. DESIGN.md follows.
