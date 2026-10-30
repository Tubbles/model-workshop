# 021 Fewer bosses on the hand-wired frame

Status: implemented

The user, 2026-10-22, with 50 M2 x 4 screws on hand against the 56 the two backings took (doc/components.md, section 10): "I think we can remove 3 bosses from each half without issue", then, from the numbered overlay (L1 to L28 and R1 to R28 in `FRAME_BOSS_CENTERS_MM`'s order): "I think we can remove L4 L9 L10 L18 L23 L24 R1 R10 R15 R20 R25, what do you think?", and to taking R4 in R1's place: "Yes that sounds good, go ahead".

Scope:

- Take out the left half's L4 (18.574, 12.307), L9 (25.049, 70.607), L10 (37.624, 17.070), L18 (75.724, 19.451), L23 (82.199, 75.370) and L24 (94.774, 17.070), and the right half's R4 (18.574, 12.307), R10 (37.624, 12.307), R15 (56.416, 17.115), R20 (75.724, 19.451) and R25 (94.774, 17.070). That leaves 22 and 23, 45 inserts and screws, and with the nice!nano clamps' two M2 x 4, 47 of the user's 50.
- Each one taken out stands 6.3 to 6.6 from a boss that stays. On the left only one of S140's pads gets a nearest boss more than 0.1 farther (8.2 to 9.9, L19 for L23). R4 rather than R1: without R1, S262's and S263's farther pads would lie 10.6 and 13.0 from a boss instead of 9.4 and 10.6, and without R4 only S243's move, by 0.1 (`tmp/bosses/removal_and_s130.py`, `tmp/bosses/removal_r4.py`, untracked).
- The placement solver's `frame-bosses` run would put them back: it has to leave out the places the user took out, so that it still finds the committed set.
- No boss can stand north of S130 on the left half or S230 on the right: the screw head would meet the reset button by up to 2.2, and the boss would come 0.227 too close to the key's switch hole. The right half's S230 also loses its east corner to S230's mirrored socket walls (0.216). Its socket has one boss near it, R19 at 9.4, the next 17.9 away.

Done:

- `layout.py`'s `FRAME_BOSS_CENTERS_MM` holds the 22 and 23 bosses that stay and `check_layout.py` counts them. The frame's bosses, the backing's screw holes and the shelves' notches follow from it: the left half keeps its three column 0 notches and the right half still has none.
- `place.py`'s boss search leaves out the seeds whose answers merged into the places taken out (`TAKEN_OUT_BOSS_SEEDS`, with the numbers above), so the `frame-bosses` run finds the 45 that stay, each where it found it before, and nothing else, and `test_place.py` passes.
- DESIGN.md (Hand-wired frame, Bosses) says what the removal leaves the backing and has the figures that moved, README.md the 45 inserts and screws and the sockets to watch on a first print, and work item 014's open points S110's and S140's sockets and the bottom row's corners.

Still open: printing them.
