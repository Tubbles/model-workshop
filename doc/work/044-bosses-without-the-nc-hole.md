# 044 The frame's bosses replanned without the NC hole

Status: in progress (2026-10-30)

The bosses kept clear of the NC pad's hole after work item 035 took it out of the frame, so they stayed where they were. The user, 2026-10-30: "replanning the bosses is a good idea since the NC pin is gone, maybe there are more that can be added or moved to a better spot, let's have a look". Shown the options (`tmp/boss_look/`, untracked), the user: "Just go with your recommendation".

Specification:

- The bosses' rules drop the NC hole (`check_layout.py`'s `DESIGN_FRAME_BOSS_NC_PAD_HOLE_DIAMETER_MM` and `frame_boss_footprint_holes()`), since the frame has none (035).
- The right half gets the boss the search now finds at (75.967, 76.248) in the left half's frame, "S230's east corner" in `place.py`'s seed labels, its north-west corner as printed. It brings S230's west pad from 11.25 to about 8.10 from its nearest boss.
- The left half gets back its boss north of S140, at (82.199, 75.370) as before work item 021. It brings S140's west pad from 9.85 to 8.15.
- The search's other new place, the right half's "S210's west corner" (95.958, 73.343), brings no pad nearer and stays out: `TAKEN_OUT_BOSS_SEEDS` lists it with the others, so `place.py frame-bosses` finds the committed set. The left half's S140 north seed comes off that list.
- 23 bosses on the left half and 24 on the right: 47 backing screws, 49 of the user's 50 M2 x 4 with the nice!nano clamps' two. The tray's shelves get a notch for each new head wherever one reaches them, as `layout.py` cuts them.
- The bosses that the search would move 0.03 to 0.23 off the old search's 0.25 grid stay where they are: no pad gets more than 0.19 nearer.
- DESIGN.md (Hand-wired frame, Bosses, and Tray, Shelves under the backing) and anything else that counts the bosses or screws follow, and `check_layout.py`'s figures with them.

Verify: `check_layout.py` passes, `test_place.py` passes in the `placement` image, and CI's frame and tray export logs print 23 and 24 bosses and the new notches. The matrix route runs again on the new frame (work item 043).
