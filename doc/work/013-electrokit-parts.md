# 013 Tray mounts for the parts from Electrokit

Status: todo

The user, 2026-10-21: "Also I saw you've selected the SOFNG SS-12D00-G3 etc. Make sure that you pick parts that are rohs, in stock, and readily available from multiple distributors, especially in the EU (mouser, tme, electrokit). I think this switch is a jlcpcb specific, obsolete, somewhat unknown part, no? Look at what others use for e.g. custom keyboard projects, and in our case, are not smd parts. Tht or chassi mounts should work for the pcb-less kbdkid5. Remember in the repo", and "Compare price (including shipping and taxes), availability, MOQ, etc and pick a cheap set of components for me that I can order".

The picks and the order are in doc/components.md (How parts are chosen, sections 2, 3, 4, 12 and 13). Two of them change the tray:

- The power switch becomes the Knitter-switch MFP 120-R, a right angle switch larger than the SOFNG SS-12D00-G3 the cradle and the lever slot are built for, with its knob reaching 5 past the body and its leads bent down.
- The reset button becomes the TE FSM2JRT, a 6 x 6 tactile switch, where the back wall and the pin hole are built for the 6 x 3.5 C&K PTS636.

The battery header stays the JST PH B2B-PH-K-S, and the key diodes belong to the hand-wired frame (TODO.md).

To do: both parts' figures in `model/kbdkid5/scripts/layout.py` and DESIGN.md, their mounts in the tray behind the north wall, and `check_layout.py`'s and the export's figures, on both halves. The FSM2JRT's drawing is not downloaded yet (TE's product sheet has none), and the MFP 120-R's figures come from a small catalogue drawing, so a caliper on the parts in hand settles both.
