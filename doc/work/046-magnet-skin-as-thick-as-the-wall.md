# 046 The magnet slots' skin as thick as the wall

Status: implemented (2026-11-02)

The 0.5 skin between the magnet slots and the joint face showed the slots through the face as printed. The user, 2026-11-02: "There is still significant patterning on the outside of the joint slant wall from the magnet pockets. Move the magnets back so that the wall thickness is respected, so the patterning disappears."

Specification:

- The skin is the wall's 0.8, so the slot's face side lies on the wall's inner face. The slot keeps its 3.5 x 8.5 fit and runs 0.3 past the block's inner face, into the floor there. No holder walls: the block's 3.2 holds the whole magnet as printed (the user's choice).
- The slot at 48.26 moves 1.2 north to 49.46, so the sixth standoff's bore keeps the 0.6 rule from it (the user's choice).

Verify: `check_layout.py` and `test_place.py` pass, and CI's tray export logs measure a 0.8 skin on every slot and 1.6 between opposing magnets.
