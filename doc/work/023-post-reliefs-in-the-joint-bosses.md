# 023 Reliefs for the switch posts in the parking and upper dowel bosses

Status: implemented

The user, 2026-10-22, asked about the clash work item 014 left open, the thumb switch's center post and side pegs over the parking boss and S150's peg over the upper dowel boss, then chose from the fixes offered (reliefs in the bosses' tops, the bosses lowered, the post and pegs clipped): "Alright yeah do the relief holes I'm the bosses tops".

Scope:

- The post and pegs reach `SWITCH_POSTS_BELOW_PCB_MM` (1.4) below the PCB's underside, to z 8.1, and both bosses stand solid from the floor to the PCB's underside (z 9.5), which rests on them. Measured on the calipered post (3.17) and pegs (1.65), in plan on both halves: S163's post reaches 1.192 into the parking boss and its pegs 0.432 each, and S150's peg at (109.799, 68.739) in the left half's frame 0.219 into the upper dowel boss (`tmp/bosses/pin_clash.py`, untracked). A switch there would stand up to 1.4 proud.
- A relief open at the top of each boss under each post and peg that comes near it, by the rule the power switch's retainer keeps from S100's (`retainer_under_posts()` in `check_layout.py`): the posts and pegs at their footprint holes' size, 0.5 clear of the boss in plan and the relief's bottom 0.5 under their ends, both as printed. Whatever else of the tray comes under any switch's post or pegs gets the same check.
- The reliefs keep the bosses' plastic around the parking hole and the dowel hole, by the joint's 1.0 between voids (DESIGN.md, The joint, Voids), and the rest of the bosses' tops stay to carry the frame and the PCB.

Done:

- `layout.py` gives the reliefs by the rule (`switch_post_reliefs()`), `tray_shape.py` cuts them into both trays after the mounts, and `export_tray.py` measures each one's diameter at its mouth and its bottom on the built tray, and that it is open over its post's or peg's place. DESIGN.md (The joint, Post reliefs) has the figures.
- On both halves, the same in the left half's frame: the parking boss has three, for S163's post (4.8 across) and both its pegs (3.3), and the upper dowel boss one, for S150's peg (3.3), all from z 7.4 up. They keep at least 1.838 of plastic to the parking hole, and 1.835 to the upper dowel hole on the left half, 1.785 on the right.
- The rule found one body besides the two bosses: the nice!nano's raised east wall comes 0.425 as printed from the holes of S130's and S131's west pegs (0.55 from the calipered pegs), so it has a relief for each, 0.075 deep into its outer face. The nice!nano test bay takes them too.
- `check_layout.py`'s `check_post_reliefs()` holds every body of the tray to the rule on both halves. Without the reliefs it fails on the parking boss, the upper dowel boss and the raised east wall.

Open: a print, whether the thumb switch and S150 seat fully (README.md, 3D printed hand-wired frame).
