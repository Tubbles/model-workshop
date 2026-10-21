# 007 Slit test strip, round 2

Status: implemented

The user printed the first slit strip (005): "the blades goes through the smallest slits easily", so even the 0.5 cell does not grip, and the fused mock's 0.6 default does not either. The plate cells also grip the switch's sides, "so its hard to read the blade friction". The user then measured the blades with calipers: the pin near a side peg (footprint-local (-3.8, 5.0)) is about 0.4 thick, the middle pin ((-5.9, 0.0)) about 0.2. The model gave 0.2 for both.

Asked: an even smaller strip, without the plate. Chosen: `model/kbdkid5/scripts/export_slit_test.py` keeps its file name and makes this strip instead of the old one. Six cells of the PCB layer alone, printed underside down like the fused mock, cell k with k notches. Each pin gets its own slit, the blade's calipered thickness plus the cell's clearance, the same clearance on both pins of a cell: -0.15 to +0.10 in 0.05 steps, so the middle pin's slits run 0.05 to 0.30 and the peg-side pin's 0.25 to 0.50. Cell 6's 0.50 repeats the first strip's loose 0.5 for the thick blade as a reference. The thinnest slits may print closed. The fused mock keeps its slits until this strip has been tried.

Printed (doc/log/2026-10-17.md): cell 6, the +0.10 clearance, held a switch best in the user's PETG, 0.50 slits for the 0.4 blade and 0.30 for the 0.2 blade. The user then asked for the first strip's widths again without the plate, the wide slit test strip (`export_slit_test.py wide`, DESIGN.md). Still open: the fused mock's slits, whose `slit_width` sets both pins alike, once the wide strip has been tried.
