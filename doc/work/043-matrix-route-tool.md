# 043 The matrix route as a documented tool

Status: todo (2026-10-30)

The matrix's route under the hand-wired frame was worked out on 2026-10-28 in untracked scratch (`tmp/matrix_route/`): a DO-35 diode beside each socket's west tab, its anode lead from that tab, a column wire chaining the east tabs, a row wire chaining the cathodes, and a lead from every row and column to the backing's opening (work item 028), drawn as each half's underside. The user, 2026-10-30, on rerunning it once the bosses are replanned: "Yes and promote this to full documentation".

Specification:

- The pipeline becomes kbdkid5 scripts in `model/kbdkid5/scripts/`, run in the `placement` image as `place.py` is: slice the frame's and the tray's STLs from a CI artifact into the room under the frame, route both halves, write each half's routes as JSON with every net's chain and lead length and every squeeze, and draw the top and underside pictures. The STL reader it borrows from `tmp/battery_mesh/` comes with it. The scratch scripts that only served the first look (`show_slice.py`, `free.py`, `bottleneck.py`) stay behind; `squeeze_parts.py`'s report of what bounds each squeeze comes along.
- The opening and the bosses come from `layout.py`, not copies, and the room comes from the current frame, so the tubes (work item 034) are in it.
- DESIGN.md gets a Matrix wiring section under Hand-wired frame: what goes where (the diodes, the anode leads, the column and row chains, the leads to the opening), the room it routes in and the rules it keeps (the enamelled wire's 0.4, the diode's body and leads, what counts as a squeeze and which sides a wire can slip under). The lengths and squeezes stay in the tool's output, not in the docs. kbdkid5's README gets the commands and how to read the pictures.
- No CI job: it runs by hand like `place.py`.

Verify: the tool runs in the `placement` image on the latest kbdkid5 artifact, and its pictures for both halves go to the user. After the bosses are replanned, it runs again on their artifact.
