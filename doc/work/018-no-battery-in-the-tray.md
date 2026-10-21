# 018 No battery in the tray

Status: implemented

The battery's place had been searched twice on 2026-10-21 (the user: "its placement is completely free, it doesn't need to align to anything arbitrary, whatever position and rotation is needed for the whole assembly to work", and later "Have we tries rotating the battery roughly 90 degrees, so it lays in the opposite diagonal?"). Then the user: "You know what, just skip the battery altogether, skip any bay or pocket or boss you have planned, just forget there is a battery at all, and I'll handle it myself. Remove the battery jst socket and all accommodations for it as well".

Done (959c377): the pouch, its ribs and its turned place, the JST PH header with its pocket and the wire rooms behind both, the `battery_shoulder` option, the battery's heights and figures, and `layout.py`'s support for turned boxes, which only the battery used, are gone. Every height stays as it was. The wire rooms over the nice!nano's B+ and B- pads stay, since those are the pads the nice!nano takes a battery on (doc/components.md, section 1). DESIGN.md (Parts in the tray, Battery) says what is left.

Still open: where the battery goes and how it connects is the user's. The six battery headers in the Electrokit order (doc/components.md, section 13) are not used by the tray.
