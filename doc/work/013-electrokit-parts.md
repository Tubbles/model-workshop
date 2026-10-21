# 013 Tray mounts for the parts from Electrokit

Status: implemented

The user, 2026-10-21: "Also I saw you've selected the SOFNG SS-12D00-G3 etc. Make sure that you pick parts that are rohs, in stock, and readily available from multiple distributors, especially in the EU (mouser, tme, electrokit). I think this switch is a jlcpcb specific, obsolete, somewhat unknown part, no? Look at what others use for e.g. custom keyboard projects, and in our case, are not smd parts. Tht or chassi mounts should work for the pcb-less kbdkid5. Remember in the repo", and "Compare price (including shipping and taxes), availability, MOQ, etc and pick a cheap set of components for me that I can order".

The picks and the order are in doc/components.md (How parts are chosen, sections 2, 3, 4, 12 and 13). Two of them change the tray:

- The power switch becomes the Knitter-switch MFP 120-R, a right angle switch larger than the SOFNG SS-12D00-G3 the cradle and the lever slot are built for, with its knob reaching 5 past the body and its leads bent down.
- The reset button becomes the TE FSM2JRT, a 6 x 6 tactile switch, where the back wall and the pin hole are built for the 6 x 3.5 C&K PTS636.

The battery header stays the JST PH B2B-PH-K-S, and the key diodes belong to the hand-wired frame (TODO.md).

To do: both parts' figures in `model/kbdkid5/scripts/layout.py` and DESIGN.md, their mounts in the tray behind the north wall, and `check_layout.py`'s and the export's figures, on both halves. The FSM2JRT's drawing is not downloaded yet (TE's product sheet has none), and the MFP 120-R's figures come from a small catalogue drawing, so a caliper on the parts in hand settles both.

Done (2026-10-21): both parts are in `layout.py`, `check_layout.py`, the tray's export, the new retainer's export, DESIGN.md (Parts in the tray, Power switch, Reset button), doc/components.md (sections 2 and 3, the FSM2JRT's drawing found in Tyco's 2008 catalogue) and README.md (the assembly). The choices made for it:

- The power switch's leads are straightened by hand to point south, not laid in the tray bent.
- The switch's north face rests on the north ledge's face, which stays whole in front of it, and the knob passes a slot through the ledge and the wall.
- The knob slot leaves 0.25 per side as printed around the knob's sweep, since the drawing is an untoleranced raster of a sibling model and the switch's detents set its positions.
- The reset button's leads are modelled at their longest (15) and cut to taste. The wire rooms of both parts are checked at the leads' full length and at the shortest cut README.md allows.
- The lever is called the knob throughout.
- The user's rules of 2026-10-21 (DESIGN.md, Parts in the tray): a socket in the print locates every part and takes its working forces, a blob of hot glue on top only keeps it down against vibration, and every part comes out undamaged for a new print.
- The knob goes in first through its closed slot, so nothing fixed may stand behind the switch's body, which the old cradle's back arms did. A low stop the body rocks over leaves no useful height at a socket's play, so a separate printed retainer drops in behind the body and takes a push on the knob.
- The reset button gets side walls and a front stop under its actuator, so it cannot slide north onto the wall, where its actuator would have been pressed past its travel.

Still open:

- A caliper on both parts in hand: the MFP 120-R's body, knob, window and the places of its window and leads along the body (taken centered), the FSM2JRT's body, cover, actuator and lead spacing, the length of its leads as Electrokit sells them and its base's underside.
- The MFP 120-R's slide force is not published, so the cradle is sized as the one it replaced.
- The retainer and the new sockets have not been printed: the retainer's snug fit in its grooves, the reset button's snug side walls and front stop.
- The FSM2JRT's corner bumps are placed from the drawing's top view (doc/components.md, section 3), which the reset button's front stop keeps 0.4 from as printed.
- The battery header does not meet the socket rule yet: by JST's figures the plug's housing covers its entry face but 0.05 per side, too little for lips to hold it against the plug's pull without keeping the plug from seating, so only the snug pocket's friction holds it. A caliper on the header and plug in hand settles whether `battery_shoulder` lips can be the default (DESIGN.md, Battery connector).
- TE's current customer drawing of the FSM2JRT was not obtained (te.com refuses curl), so its figures rest on the 2008 catalogue drawing.
