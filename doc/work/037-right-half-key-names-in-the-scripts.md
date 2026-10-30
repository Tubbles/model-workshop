# 037 Right half key names in the scripts

Status: implemented (2026-10-30)

The docs call the right half's keys by their own names, S2xx, since 6154fa4 (doc/log/2026-10-30.md). Asked whether the code should follow, the user, 2026-10-30: "Yes switch code too".

Specification:

- Every key name kbdkid5's scripts declare, print or assert for the right half is its S2xx name (DESIGN.md, Keys): the right half's rule data in `layout.py` (`RIGHT_*`), the figures transcribed for it in `check_layout.py` and the exports, the labels on their right half lines, and `test_place.py`'s expectations. The left half's names stay.
- The geometry does not change. The key centers and footprints stay in the left half's frame under the left names, and `layout.py` holds the one mapping between the names: the right twin of S1<column><row> is S2<6 minus column><row>.
- Comments and docstrings that name a right half key use its S2xx name.

Verify: `check_layout.py` passes, its output changed only in the right half's key names. `test_place.py` passes. CI's exports pass, their output changed only in those names, and the STLs come out as 685dd08's. kbdkid5's CLAUDE.md drops the note that the scripts use the left names.
