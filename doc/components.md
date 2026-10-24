# kbdkid5 component research

Research date: 2026-10-16. All dimensions in mm, forces in N (kgf in brackets where a vendor quotes kg).

How to read the confidence marks:

- **Confirmed**: read off a primary source (manufacturer datasheet, drawing, product page or catalogue) in this session.
- **Derived**: measured or computed by me from a primary source (for example pixels on the manufacturer's render, or a calculation). The method is stated.
- **Unconfirmed**: from a secondary source (retailer, review, community footprint, the kbdkid4 package model) or an assumption. What it rests on is stated.

Downloads (datasheets, renders, pages) are in `work/research/downloads/<name>/`. The magnet model is in `work/research/scripts/` (run with `podman run --rm -v <dir>:/probe:ro localhost/freecad-headless python3 /probe/magnet_force.py`, the image has scipy).

## How parts are chosen

The user, 2026-10-21: "Make sure that you pick parts that are rohs, in stock, and readily available from multiple distributors, especially in the EU (mouser, tme, electrokit). I think this switch is a jlcpcb specific, obsolete, somewhat unknown part, no? Look at what others use for e.g. custom keyboard projects, and in our case, are not smd parts. Tht or chassi mounts should work for the pcb-less kbdkid5", then "Those shops are just examples, but preferred in the EU. Darnell, RS, elfa etc works as well", "Branding is not needed if purchasing from e.g. electrokit" and "Compare price (including shipping and taxes), availability, MOQ, etc and pick a cheap set of components for me that I can order". So a bought part is:

- RoHS compliant, by its datasheet or its seller.
- In stock, and sold by more than one distributor, EU ones first (Electrokit, TME, Mouser, Farnell, RS). An unbranded part from a shop like Electrokit counts, with the shop's datasheet.
- Through hole or chassis mount for kbdkid5, whose parts in the tray are wired by hand. No SMD.
- What keyboard builders use, where there is a choice.
- Cheap as a whole order, with shipping, VAT and minimum quantities counted (section 13).

## Summary of recommendations

| Item | Recommendation | Key dimensions |
|---|---|---|
| 1. nice!nano v2 | Grip the far (antenna) end and the USB shell, not the long edges. Mill-Max 315-43-112-41-003000 socket strips on pins 1 to 12 of each row (section 8) | 18.20 x 33.20 board (the user's caliper), 1.6 PCB, USB-C shell 8.94 x 3.16, flush with the underside, 0.87 past the board end on the render |
| 2. Power switch | Knitter-switch MFP 120-R, right angle through hole SPDT, its knob through the north wall (section 2) | body 11.0 x 6 x 5.6, knob 3.4 x 3.2 reaching 5 past the body, 3 leads at 3.2 pitch leaving the back at mid height, bent down to 4.2 below the body, 350 mA 30 VDC |
| 3. Reset button | TE FSM2JRT, 6 x 6 tactile switch with 2 through-hole leads, pressed through a pin hole (section 3) | 6.19 square, the cover 3.60 and the 3.5 actuator 4.3 over the base, 2 leads 5.00 apart, 160 gf, 50 mA 24 VDC |
| 4. Battery connector | None in the tray since 2026-10-21: the user handles the battery and how it connects (section 4). Researched before: JST PH 2.0 mm, B2B-PH-K-S (top entry) laid on its side in a pocket, wires on the posts | 5.9 x 4.5 x 6.0 body, posts 3.4, mated length 8 |
| 5. Joint | Two hardened steel dowel pins carry the bending; 4 magnet pairs of 10 x 3 discs (12 mm face) or 5 pairs of 8 x 3 (10 mm face) only hold the halves together | pins 4 x 24 (12 embedded per side) or 3 x 20 |
| 6. PCB connector | JST SH SM12B-SRSS-TB side entry on the PCB underside, JST pre-crimped leads | 14.0 x 4.95 x 2.9 header, 2.95 mated height |

## 1. nice!nano v2 mechanics

### What the manufacturer publishes

nice!keyboards publishes no dimension drawing, footprint or 3D model. What it does publish:

- "Mid mount USB-C port making the board a 3.2mm total thickness" (Confirmed, https://nicekeyboards.com/docs/nice-nano/). The product page repeats "only 3.2mm thick" and "mid-mount USB-C port" (https://nicekeyboards.com/nice-nano).
- A pinout render of both sides and the v2 schematic (https://nicekeyboards.com/docs/nice-nano/pinout-schematic). The 2000 px version of the render is `work/research/downloads/nicenano-site/pinout-v2-2000.png` (from https://nicekeyboards.com/static/1788ac663060fd510f4894b286cd97b1/e8950/pinout-v2.png), the 1949 px schematic is `work/research/downloads/nicenano-site/schematic_nice_nano_v2-1949.png`.
- The schematic names the USB receptacle "J1 USB C C168688" (an LCSC part number) and the charger BQ24075, the 3.3 V regulator XC6220B331MR, the MCU nRF52840.

### Measurements taken from the manufacturer's render (Derived)

Method: in the 2000 px render, the 11 pitches between the first and last of the 12 pins measure 639.5 px, so 58.14 px per 2.54 mm = 22.89 px/mm. Board edges, holes and the shell were found by scanning pixel rows and columns (hole pixels are transparent in the PNG). One pixel is 0.044 mm; with edge antialiasing, read every figure below as about ±0.1. The pin pitch matching in both axes (15.25 for the 15.24 row spacing) suggests an orthographic render.

| Feature | Value (Derived) |
|---|---|
| Board length (USB end to far end) | 33.3 |
| Board width | 18.0 |
| USB-C shell front past the board's USB end | 0.87 |
| USB-C shell width | 8.91 (datasheet 8.94, below) |
| Pin rows | 2 x 12, 2.54 pitch, rows 15.25 apart |
| Pin 1 (nearest USB) from the USB end | 3.91 |
| Pin 12 from the far end | 1.44 |
| Row centres from the long edges | 1.31 and 1.44 (3 px asymmetry, real or render) |
| Pin hole diameter | about 0.83 (transparent pixels; plated, finished size unknown) |
| Pin pad outer diameter | about 1.53 |
| Battery pads B+ / B- | in line with the two rows, one pitch beyond pin 1: 1.38 from the USB end; hole about 0.61, pad about 1.14; B- is the square pad |
| Extra pads P1.01, P1.02, P1.07 | plated through holes in one row across the board at the level of pin 10, 26.8 from the USB end, at 2.54, 5.08 and 7.62 from the row on the B- side (P1.07 on the centre line) |
| Shell tab slots | 4.02 apart along the board, the front pair 2.05 behind the shell front (datasheet 4.00 and 2.09) |

Cross-checks:

- The extra pad positions match the community footprint `bstiq/nice-nano-kicad` (pads 31 to 33 at the pin-10 position, 5.08, 2.54 and 0 from the centre line; https://github.com/bstiq/nice-nano-kicad/blob/HEAD/nice_nano.kicad_mod).
- Community footprints draw the outline as 33.02 x 17.78 (1.3 x 0.7 in, the Pro Micro outline), with pin 1 at 3.81 from the USB end (marbastlib `nice_nano_H_USBup`, https://github.com/ebastler/marbastlib/blob/HEAD/footprints/marbastlib-xp-promicroish.pretty/nice_nano_H_USBup.kicad_mod; bstiq as above). These are drawn outlines, not measurements (Unconfirmed).
- The kbdkid4 package model (`library/pkg/e86c9147-c7a4-4cf8-9447-455cd70fafbc/` in the Tubbles/kbdkid4 repository, STEP "nice!nano v2.step", exported 2025-01-29 by Autodesk Translation Framework, origin not recorded) has a 33.2 x 17.8 x 1.4 PCB (probed with FreeCAD this session). The kbdkid4 scripts already record that the model is wrong in thickness (1.4 vs the measured 1.6) and in the receptacle height (`model/kbdkid4/scripts/export_tray.py` lines 198 to 205).
- kbdkid4's `MCU_USB_END_OFFSET_MM = 18.7` (connector end from the centre of the pin rows, `model/kbdkid4/scripts/tray_shape.py`) agrees with the render: 3.91 + 13.97 + 0.87 = 18.75.

The render and the drawn footprints disagree by about 0.3 in length and 0.2 in width. The user's caliper on a real board, first with the shell (doc/log/2026-10-19.md): "The nano measures, with the usb connector included: 18.30 x 34.17", then the board alone (doc/log/2026-10-20.md): "The nano width is 18.17~18.23 mm", "Board length 33.20". That makes the board 18.20 x 33.20 (Confirmed: calipered), 0.2 wider and 0.1 shorter than the render's. The 34.17 with the shell less the 33.20 board puts the shell 0.97 past the board, against the render's 0.87 (Unconfirmed: the shell is not measured on its own).

### Thickness and the USB-C receptacle

The schematic's part C168688 is the Jing Extension (Shenzhen Jing Tuo Jin) 918-418K2024S40000 16-pin mid-mount ("Recessed") Type-C receptacle (LCSC listing https://www.lcsc.com/product-detail/C168688.html, drawing https://datasheet.lcsc.com/datasheet/pdf/c26680a47779df2150f1403f3fec276a.pdf, saved as `work/research/downloads/usbc-c168688/C168688_real.pdf`). The drawing's title block reads 918-418K2023S40033, a slightly different number from the LCSC listing; the dimensions below are from that drawing (Confirmed for the drawing; that every nice!nano v2 carries exactly this part rests on the schematic label only).

| Drawing dimension | Value |
|---|---|
| Shell width at the mouth | 8.94 ±0.05 |
| Shell height | 3.16 ±0.1 |
| SMD foot plane from one shell face | 1.6 ±0.05 (so 1.56 from the other) |
| Across the hold-down wings | 11.15 ±0.1 |
| Length, front to rear of body | 6.5 ±0.1 (7.2 ±0.15 with the 0.7 terminals) |
| Front face to front tab centre | 2.09 ±0.1 |
| Tab slots in the land pattern | 4 x 0.65 wide, 1.40 and 1.70 long, 4.00 apart, 11.08 across |
| Signal pads | 16 x 0.30 |

Cross-check against the owner's measurement: the feet sit on the board's top copper and the shell sinks through a cutout. With the measured 1.6 board, one face of the shell lies 1.6 from the foot plane and the other 1.56, so the shell ends within 0.04 of the underside (flush) and stands 1.56 to 1.6 above the top side. Total 3.16 to 3.2, which matches the vendor's "3.2mm total thickness". This supports the owner's numbers (1.6 PCB, flush shell, 3.16 shell, about 1.56 above the top). The kbdkid4 model's receptacle ("usb4520-03-0-a v1", a different part) straddles the board and is inconsistent with this drawing.

Whether the shell's four tabs or their solder protrude below the underside was open: the render shows the four plated slots on the underside, and the owner measured the shell flush. The user settled it on a real board: "the nano is absolutely flat on its underside. There is nothing sticking out downwards" (doc/log/2026-10-19.md). So the tray floor under it is flat, with no relief under the slots.

### Top side parts

- Upper bound from the manufacturer: total thickness 3.2 minus the 1.6 board leaves 1.6 above the top side, and the USB shell already uses about 1.56 of it. So no part on the top side is taller than about 1.6 (Derived from https://nicekeyboards.com/docs/nice-nano/).
- Owner's kbdkid4 measurement: the nano sits flush on 2.56 mm sockets with the component side toward the keyboard PCB (`model/kbdkid4/scripts/tray_shape.py` lines 50 to 60), which bounds the top-side parts at 2.56, weaker than the bound above but consistent. Measured on kbdkid4's soldered left half (the user, 2026-10-12, kbdkid4 commit bb2d1d9). The right half's nano goes on 4.3 mm sockets, the user's figure for a half not yet soldered then (kbdkid4 commit 5dc598e, `RIGHT_NANO_SOCKET_HEIGHT_MM`).
- Identified packages (heights from primary sources): regulator XC6220B331MR in SOT-25, 1.1 ±0.1, 1.3 max (Torex datasheet via https://datasheet.lcsc.com/datasheet/pdf/a2ba3a0a4d164b74a2b24c8a2a4beaa9.pdf, page 24); charger BQ24075 in RGT0016C, "VQFN - 1 mm max height", 3.00 x 3.00 (TI, https://www.ti.com/lit/ds/symlink/bq24075.pdf). The nRF52840 aQFN73 is 7 x 7 and about 0.85 tall (Unconfirmed: distributor listings only, one lists 0.77; Nordic's product specification was not opened). The LEDs, inductors, crystals (32 MHz XRCGB32M000F1H50R0 and 32.768 kHz FC-12M per the schematic) were not looked up. The SOT-25 regulator, at 1.3 max, is the tallest part I could confirm.
- Antenna: the schematic shows only an `ANTENNA` net after a matching network (R10, C18, L2, C19, C20), no antenna component, and the render shows no parts near the far end. That points to a PCB trace antenna at the far end (Unconfirmed: inferred from the schematic and render).
- Approximate positions from the render (Derived, ±0.5): the LEDs sit either side of the board 7 to 9 from the USB end; the SOT-25 regulator 9 to 12 from the USB end, toward the B- long edge; the 3 x 3 charger 8.5 to 12 from the USB end, toward the B+ edge; the 7 x 7 nRF52840 about 16.6 to 23.8 from the USB end, centred; small passives reach about 27 from the USB end. From about 27.5 to the far end (33.3) the top side carries only the last two pins of each row and silkscreen; the extra pads sit just before, at 26.8.

### Reset, battery and extra pads

- Reset: RST is a regular pin, third from the USB end on the row that starts with RAW (RAW, GND, RST, VCC, ...), 3.91 + 2 x 2.54 = 9.0 from the USB end, GND next to it at 6.4 (pin order from the render and the schematic's Pro-Micro-Pin-Out J2; https://nicekeyboards.com/docs/nice-nano/pinout-schematic). The getting-started page: "double tap RST and GND pins" enters the bootloader (https://nicekeyboards.com/docs/nice-nano/getting-started).
- Battery: B+ and B- are the two extra through-hole pads at the USB end, in line with the rows (positions above). The getting-started page: "If you choose to solder your battery, use the B+ and B- pins", "Do not install sockets or post headers to the B+ or B- pins", "RAW and GND are the respective equivalents to B+ and B-" (same URL). Battery wires and the power switch go to B+ and B- on the top side.
- Charge rate: 100 mA, 500 mA with the BOOST jumper on the underside bridged (pinout render legend, URL above). This sets the power switch rating (section 2).
- SWD/SWC are small SMD pads on the underside only (render), not needed here.
- Pins are plated through holes with full annular rings 1.3 to 1.4 inside the long edges, not castellated (render).

### Where the board can be held

- Far (antenna) end, top side: free of parts from about 27.5 to 33.3 from the USB end (the render's board end, the calipered board ends at 33.2), across the middle between the pads of the last pin of each row: 13.7 on the render's 18.0 board (18.0 minus 2 x (1.37 row inset + 0.77 pad radius)), and 13.79 on the calipered 18.20 board with the pads at the larger of the render's insets, 1.44, from each long edge. The nice!nano clamp's tab grips here (model/kbdkid5/DESIGN.md, nice!nano). Plastic over a PCB antenna detunes it a little, so what reaches over it stays small (Unconfirmed: general RF practice, not measured).
- USB end: the metal shell stands 1.56 above the top face across 8.94. The north wall's USB window can bear down on the shell top and hold that end down; no pads or parts are touched. B+ and B- sit at the two corners of this end, 1.38 from the edge, and will carry soldered wires: no lips at those corners.
- Long edges: pads every 2.54 along the whole length; the strip outside the pads is only about 0.6 wide (1.37 inset minus 0.77 pad radius), and the gaps between pads about 1.0. With socket strips soldered over the pads (section 8), no lips here; locate the long edges with plain side walls.
- Underside: flat, with nothing below it (Thickness and the USB-C receptacle, above). The shallow grooves this note once suggested under the two pin rows and under B+/B- and P1.xx were printed in the first nice!nano bay test strip and removed as unnecessary. With the socket strips soldered, their tails stand about 1.6 below it on the user's board, as calipered (section 8), 0.81 for the strips the layout was built for.

## 2. Power switch

Requirement check: the switch sits in series with the battery. splitkb tells users to switch on while charging (https://docs.splitkb.com/product-guides/nice-nano/frequently-asked-questions), so charge current runs through it: 100 mA by default, 500 mA with BOOST bridged (nice!nano pinout render).

| | SS-12D00-G3 (SOFNG) | OS102011MA1QN1 (C&K) | MSK12C02 (Shou Han) | SSSS811101 (ALPS) |
|---|---|---|---|---|
| Source | https://datasheet.lcsc.com/datasheet/pdf/7357551f1ab94cd5763cc9d7033faef8.pdf (LCSC C22355741) | C&K OS catalogue 8 Aug 17, page I-42, https://datasheet.lcsc.com/datasheet/pdf/9e68893bade4341f8dc17b91bf8fc979.pdf | https://datasheet.lcsc.com/datasheet/pdf/5162155576bfd231c35aa9a893d25c8c.pdf (LCSC C431540) | https://tech.alpsalpine.com/cms.media/product_catalog_sw_02_ssss8_en_e99db3d0b9.pdf (drawing no. 7) |
| Type | vertical, through hole | right angle, through hole | right angle, SMD | right angle (horizontal), SMD |
| Body | 8.8 x 3.9 x 3.5 (the datasheet header gives H 7.2 overall) | 8.6 x 4.4, 4.7 tall | 8.0 ±0.2 (with tabs) x 2.8 ±0.1 x 1.4 ±0.1 | 6.7 x 2.6 x 1.4 (7.7 over the ground tabs) |
| Actuator | 1.5 x 1.5, 2 / 3 / 4 / 10 long (G2 to G10) | 2.0 wide, 4.0 past the body | 1.3 ±0.1 wide, about 1.45 past the body | 1.3 wide, about 0.9 past the body |
| Travel | 2 | 2.0 | 1.6 | 1.5 |
| Operating force | 3.5 N | not stated | 150 ±100 gf | 1.5 N |
| Leads | 3 pins 0.5 x 0.3, 3.0 below body, 2.5 pitch | 3 pins 0.4 x 0.5 at 2.00 pitch, 2.8 long, plus 2 mounting legs (Ø1.5 holes, 8.2 apart) | 3 gull-wing pads at 1.5 / 3 spacing plus 4 tabs, 2 Ø0.75 pegs | 3 gull-wing terminals 0.4 wide at 1.5 / 3 spacing, 2 Ø0.8 pegs, ground tabs |
| Rating | 0.5 A 24 VDC | 0.1 A 12 VDC | 50 mA 12 VDC | 0.3 A 5 VDC |
| Availability | LCSC C22355741: 20,881 in stock, about 0.05 USD (https://www.lcsc.com/product-detail/C22355741.html, 2026-10-16) | listed at Farnell, RS, TME, Digi-Key (search results, stock not checked) | LCSC/JLCPCB C431540, "Extended" (https://jlcpcb.com/partdetail/C431540) | ALPS product page lists it (https://tech.alpsalpine.com/e/products/detail/SSSS811101/), distributor stock not checked |

Notes:

- "SS-12D00" is a generic number made by many factories. Dimensions differ between makers: hobby retailers list the SS-12D00G3 at 8 x 4 x 3.8 with 2.54 pitch and 0.5 A 50 VDC (https://www.hobbyelectronica.nl/en/product/ss12d00g3-schuif-schakelaar/, Unconfirmed). Buy one maker's part (SOFNG via LCSC) and print the pocket from its drawing, or measure the parts in hand.
- The C&K OS102011MA1QN1 is rated 0.1 A, the MSK12C02 50 mA. Both are below the 0.3 A target and at or below the default 100 mA charge current. splitkb ships the MSK12C02 in its wireless kit (https://splitkb.com/collections/keyboard-parts/products/wireless-controller-expansion-bundle), so it works in practice, but it runs outside its rating while charging.
- The ALPS part meets 0.3 A, but its 0.4 wide gull-wing terminals are fiddly to solder wires to, and its lever stands only about 0.9 proud of the body, too short to reach through a printed wall without an extension.

**Recommendation until 2026-10-21: SOFNG SS-12D00-G3**, which the tray's cradle and lever slot were built for until work item 013. G4 if the wall in front of the switch is thicker than about 1.5. Lay it in a pocket behind the north wall with the lever pointing north through a slot and the three 3.0 long pins pointing south into the tray, where wires solder easily. Slot about 1.5 + 2 travel + clearance long (about 4.0) by about 2.0 wide (my sizing, not from a source). Its 0.5 A rating also covers the 500 mA BOOST charge rate.

### Against the buying rules (2026-10-21)

The SOFNG part turned up only at LCSC, JLCPCB's parts store (C22355741), in no Mouser or TME listing (web search, 2026-10-21). The SS-12D00 type itself is generic: Electrokit sells Kinghelm's KH-SS12D01-G3-5.0 (41035350, 3.50 SEK, at least 4), 8.7 x 3.7 x 3.6 with a 1.5 lever, 2 travel and pins at 2.5 by its drawing (`work/research/downloads/electrokit-41035350/`), but neither the drawing, Electrokit nor LCSC (C5274456) gives a rating or a RoHS statement.

| | MFP 120-R (Knitter-switch) | EG1218 (E-Switch) |
|---|---|---|
| Source | Knitter-switch's catalogue page "Miniature Slide Switches", page 100, from Electrokit 41011898 (`work/research/downloads/electrokit-41011898-knitter-mfp120/`) | E-Switch drawing P040040 rev C, from LCSC C273394 |
| Type | right angle, through hole | vertical, through hole |
| Body | 11.0 long, 6 deep, 5.6 tall (the drawing, A for the MFP 120) | 11.60 x 4.00 x 5.40 |
| Actuator | knob 3.4 wide, 3.2 tall, 5 past the body's face, in a window B 6.6 long. Travel 3.2 (B less the knob, Derived) | 2.00 x 2.00, 2.00 past the body, 2.5 travel, 250 ±100 gf |
| Leads | 3, 0.8 x 0.5, at 3.2 pitch, leaving the back at the body's mid height and bent down, the bent run's outer face 1.5 behind the body, to 4.2 below it | 3, 0.60 x 0.50, 4.70 long, at 2.50 pitch |
| Rating | 350 mA 30 VDC | 200 mA 30 VDC |
| RoHS | "RoHS-conform" mark on the catalogue page | not on the drawing, only in distributor listings (Unconfirmed) |
| Lifecycle | not published by Knitter-switch that we found | Active at LCSC, which is LCSC's view, not E-Switch's |
| Availability | Electrokit 41011898, 75 in stock (its page). Distrelec (MFP 120-R, 135-11-212) and RS (7023542), TME's MFP 120 with 0 in stock, all from web search results, the pages not opened | LCSC 1,471 in stock (its page). Mouser, TME, Digi-Key and Farnell from web search results, the pages not opened. Electrokit's similar 41004098 is discontinued |

The MFP 120-R's figures, read again on 2026-10-21 from the catalogue page rendered at 1200 dpi: its right angle drawing is the MFP 140-R's, an embedded raster without tolerances, with A and B from the table for the MFP 120-R.

- Confirmed (the drawing): the knob and its window are drawn centered on the body's 5.6, and the leads leave the back face on that center line, as the vertical MFP 140's end view has them leave the body's middle. The "1.5" of the end view runs from the back face to the outer face of the leads' bent run, which is 0.5 thick, so that run lies 1.0 to 1.5 behind the body.
- Confirmed (Electrokit's page): SPDT, "Rastermått: 3.2mm", so 3 leads.
- Derived: straightened, a lead reaches at most 8.25 behind the body, the bent run's middle 1.25 behind it plus the 2.8 down to the body's bottom and the 4.2 below it, the bend taken sharp.
- Unconfirmed: where the MFP 120-R's window and three leads sit along the body. The drawing shows the MFP 140-R's five leads, centered on its body, and its window about 0.25 off the body's middle as drawn, within the drawing's accuracy. Both are taken centered.
- Not published: tolerances, the slide force, the leads' bend radius.

Keyboard builds: a nice!nano holder for the Dactyl Manuform names Adafruit's SPDT slide switch (product 805) for power (https://github.com/nathanielks/nice-nano-holder), and a hand-wired wireless Skeletyl glues an unnamed SPDT slide switch to its case (https://elescia.wordpress.com/2022/02/27/handwired-wireless-skeletyl/7/). The PCB kits use the MSK12C02 (above), which is SMD.

**Recommendation since 2026-10-21: Knitter-switch MFP 120-R**, from Electrokit with the other parts (section 13). RoHS by its catalogue, sold by several distributors, and its knob reaches 5 past the body, far enough through a printed wall, where the EG1218's lever stands 2.0 proud. No second source shares its footprint, so the tray's pocket fits this part only. Its 350 mA covers the 100 mA default charge current but not the 500 mA BOOST rate, so BOOST stays unbridged. The tray holds it behind the north wall with its leads straightened by hand (model/kbdkid5/DESIGN.md, Power switch).

## 3. Reset button

| | TL3315NF100Q (E-Switch) | PTS636 SL43 LFS (C&K), 6 x 3.5, top actuated | PTS645 V (C&K), 6 x 6, right angle |
|---|---|---|---|
| Source | https://media.digikey.com/pdf/Data%20Sheets/E-Switch%20PDFs/TL3315.pdf | C&K PTS636 datasheet 14 Nov 22, https://datasheet.lcsc.com/datasheet/pdf/068f7f6df8f843e9b2889464250ad819.pdf | C&K PTS645 datasheet 6 Feb 18, https://datasheet.lcsc.com/datasheet/pdf/562a3ff7cc4a11dfb85e5324391a4dcf.pdf |
| Body | 4.50 x 4.50 (4.75 over terminals), 0.55 tall | 6.0 ±0.2 x 3.5 ±0.2, housing 3.3 ±0.2, stem top at H = 4.3 or 5.0 ±0.2; stem 3 x 1.5 | 7.5 wide (8.5 over the legs) x 6.2 tall; Ø3.5 actuator, its axis 4.05 above the board, reaching 3.15 / 3.85 / 5.85 / 8.35 past the front leads (options 31 / 39 / 58 / 83) |
| Force | 100 ±30 gf (F100) | 130, 180, 250 or 320 ±50 gf (L, M, K, P) | 130, 160, 200 or 260 gf |
| Travel | 0.20 | 0.25 ±0.1 | not stated in the datasheet |
| Leads | 4 gull-wing SMD terminals (two pairs) | 2 straight leads 1 wide, 3.9 ±0.2 below the body, 6.4 pitch | 2 pins at 4.5 pitch plus 2 support pegs (Ø1.3 holes, 7 apart) |
| Rating | 50 mA 15 VDC | 50 mA 12 VDC | 50 mA 12 VDC |

Notes:

- The "3 x 6 mm 2-pin" tactile switches sold on marketplaces appear to be the same 6 x 3.5 body class as the PTS636 (listings name them 3x6x4.3 and 3x6x5.0 2-pin; https://makerselectronics.com/ar/product/push-button-3x6x5-0mm-dip-2pin/). Their datasheets were not found, so their dimensions are Unconfirmed.
- The TL3315 needs a PCB: its terminals are 0.5 wide gull wings, and with 0.2 travel and 0.55 height there is little to locate in a printed pocket.
- The PTS645 V is made for a PCB at right angles to the actuator; air-wired, its pegs and bent legs only get in the way, and its 7.5 x 6.2 face is the largest of the three.

**Recommendation until 2026-10-21: C&K PTS636 SL43 LFS** (130 gf, 4.3), which the tray's back wall and pin hole were built for until work item 013. Lay it on its side in a pocket behind the north wall: the 6.0 side along the wall, the 3.5 side vertical, the stem facing north behind a pin hole of about Ø1.5 (sized for a SIM ejector pin like kbdkid4's), the two leads pointing south for the RST and GND wires. Use SK43 (250 gf) instead if it should resist presses through a larger opening. The reset line carries microamps, so the 50 mA rating is irrelevant.

### Against the buying rules (2026-10-21)

The PTS636 SL43 LFS is at Mouser and Digi-Key but turned up at neither TME nor Farnell (web search results, the pages not opened), and Electrokit has no 6 x 3.5 through-hole tactile switch (only an SMD 6 x 3, 41024337). Electrokit's 2-lead 6 x 6 switches are TE's (Alcoswitch FSM):

- FSM2JRT (41024339): 6 x 6 x 4.3, 2 leads 5 apart, 1.6 N, 50 mA 24 VDC, 293 in stock. "ACTIVE" and "EU RoHS Directive 2011/65/EU Compliant" on TE's product sheet (`work/research/downloads/electrokit-41024339-te-fsm2jrt/`), which has no drawing. Its drawing is below.
- FSM4JRT (41019151): the same switch 5 tall, 4.90 SEK, 895 in stock, and at Mouser, Digi-Key and RS by web search results (the pages not opened). Its 2 leads 5 apart match the FSM2JRT's, but its actuator is 0.7 longer, more than the tray's back wall leaves room for (model/kbdkid5/DESIGN.md, Reset button), so it is no drop-in second source.

The nice!nano holder above names Adafruit's 6 mm slim tactile switch (product 1489) for reset.

**Recommendation since 2026-10-21: TE FSM2JRT**, from Electrokit with the other parts (section 13), the lower of the two. The tray holds it behind the pin hole (model/kbdkid5/DESIGN.md, Reset button).

### FSM2JRT drawing (2026-10-21)

te.com answers curl with 403 for its customer drawings, so the drawing is the FSMJRT series' in Tyco Electronics' tactile switch catalogue 8-1773450-9 (issued 09/2008), page C16, https://media.masterelectronics.com/productfiles/mf-ao/tyco-tactile.pdf, saved as `work/research/downloads/te-fsm2jrt-drawing/tyco-tactile-masterelectronics.pdf` (page 16 of the PDF). Its drawing is vector graphics, read by rendering the page with pdftoppm. It is drawn as the FSM4JRT, the actuator's length set by its code, 2 (4.3) for the FSM2JRT, which the page's table lists as 2-1437565-6 with 1.6 ± 0.5 N. The same folder holds TE's overview catalogue from Octopart (`octopart-FSM2JH-datasheet-20867703.pdf`), which has no drawing.

- Confirmed (the drawing): body 6.19 square (".244 TYP"). From the base's bottom face, the face that sits on a PCB: a step in the base at 1.01 (3.60 less the 2.59 from the cover's top), the steel cover's top at 3.60, bumps at the cover's corners up to 0.40 over it (printed ".016 (.040) MAX."), and the round actuator, 3.50 across, to 4.3 for code 2, 0.7 over the cover, as TE's product sheet gives (button width 3.5, height 4.3, actuator length 0.7). Travel 0.25 on average (page C15).
- Derived (the drawing's top view, measured on the rendered page): the four bumps sit at the cover's corners, each about 1.4 across, centered about 0.8 in from both edges, so they come no nearer the middle of a side than about 1.6.
- Confirmed (the drawing): two leads 5.00 ± 0.10 apart (the PCB layout, holes 0.99 +0.10/-0.00) on the body's center line, running straight out of the base along the actuator's axis, 0.60 wide near the body and 0.50 further on, 0.30 thick and 0.40 at the crimp the radial tape leaves. The body may sit up to 10 degrees off its leads ("10 0' Max."). The tape view gives the pitch as ".197 ± .004) 4.83 ± 0.10)", where 0.197 in is 5.00, taken as a misprint.
- Derived: the leads' length is not dimensioned. On the tape the base's bottom face stands 18.00 ± 0.20 over the sprocket holes' axis, which the drawing puts in the middle of the 18.00 tape, 9.0 below its top edge, and the leads run on about 6.0 into the tape (the hold-down tape's 5.99), so they reach at least 9 and at most about 15 below the base. How Electrokit cuts them is not stated (its page: "två långa ben").
- Unconfirmed: the base's underside. The tape view, not to scale, shows a channel about 1.0 deep across it between the leads, about a third of the body's width.

## 4. Battery connector

The tray no longer has a place for the battery or this connector. The user, 2026-10-21: "just forget there is a battery at all, and I'll handle it myself. Remove the battery jst socket and all accommodations for it as well" (model/kbdkid5/DESIGN.md, Battery). The research below stays for the user's own choice. Its space figures are from before the 1.5 raise (DESIGN.md, Heights).

Common choice: JST PH, 2.0 mm pitch, 2 pins. SparkFun's 110 mAh cell "Comes terminated with a standard 2-pin JST-PH connector" (https://www.sparkfun.com/lithium-ion-battery-110mah.html), and splitkb's wireless kit uses S2B-PH-K-S(LF)(SN) headers with PHR-2 housings and SPH-002T-P0.5S contacts (https://splitkb.com/collections/keyboard-parts/products/wireless-controller-expansion-bundle). Other connectors exist (Keebio ships 301230 cells with Molex Pico-EZmate, https://keeb.io/products/lithium-ion-battery-90mah), but PH is the one most batteries come with. Polarity varies between battery makers: "Some batteries come with positive on the first pin and some come with negative on the first pin" (https://nicekeyboards.com/docs/nice-nano/getting-started). Check every battery before plugging it in.

JST PH data (Confirmed, JST PH catalogue https://www.jst-mfg.com/product/pdf/eng/ePH.pdf, saved as `work/research/downloads/jst-ph/eph2.pdf`):

| | B2B-PH-K-S (top entry, through hole) | S2B-PH-K-S (side entry, through hole) |
|---|---|---|
| Body | 5.9 wide (B) x 4.5 deep x 6.0 tall | 5.9 wide x 7.6 deep x 4.8 tall |
| Posts | 2 at 2.0 ±0.05, (3.4) below the body, PCB hole Ø0.7 +0.1/0 | same, (3.4) |
| Mated size | (8) mounting height with the plug | (4.8) tall, (9.6) long with the plug |
| Rating | 2 A (AWG 24), 100 V | same |
| Plug | PHR-2 housing 5.8 x 4.5 x 6.85, SPH-002T-P0.5S contacts (AWG 30 to 24) | same |

Space: the PCB rests about 8 above the tray floor with sockets 2.0 below it, leaving about 6. A B2B standing upright with its plug (8 tall) does not fit under the PCB; an S2B lying flat fits (4.8) but its posts point into the floor.

**Recommendation: B2B-PH-K-S laid on its side** in a floor pocket: envelope 5.9 x 4.5 (now the height) x 6.0, plus the 3.4 posts pointing back horizontally, where the battery-side wires solder without any slot in the floor. The plug enters horizontally. Lying on its 5.9 x 6.0 face, header and PHR-2 plug are both 4.5 thick, so the mated pair is 4.5 tall, under the 6 available; on the other face it would be 5.9 tall, with no margin (housing sizes from the table above; the mated height on its side is my arithmetic, Derived). The pocket must hold the header's front shoulders, since the plug pulls out toward the front. SparkFun warns PH plugs "can stick in pretty good" (URL above).

Electrokit sells JST's straight 2-pin PH header (41004562, "Stiftlist JST-PH 2-pol 2.0mm", brand JST, 3979 in stock), with JST's PH catalogue as its datasheet (`work/research/downloads/electrokit-41004562-jst-ph/`), so the B2B-PH-K-S above. Its listing names no suffix, so whether it is the RoHS (LF)(SN) version is not stated. It is also at RS as B2B-PH-K-S(LF)(SN) (1667311).

## 5. Magnets for the joint

### Vendor figures (Confirmed, supermagnete.de product pages, 2026-10-16)

| Magnet | Grade | Adhesive force to steel | Displacement (shear) force | Weight | Price (smallest pack) | URL |
|---|---|---|---|---|---|---|
| S-06-03-N disc 6 x 3 | N45 | 0.99 kg (9.71 N) | 1.93 N | 0.64 g | 0.36 EUR | https://www.supermagnete.de/eng/disc-magnets-neodymium/disc-magnet-6mm-3mm_S-06-03-N |
| S-08-03-N disc 8 x 3 | N45 | 1.5 kg (14.7 N) | 2.88 N | 1.1 g | 0.43 EUR | https://www.supermagnete.de/eng/disc-magnets-neodymium/disc-magnet-8mm-3mm_S-08-03-N |
| S-10-02-N disc 10 x 2 | N42 | 1.3 kg (12.7 N) | 2.48 N | 1.2 g | 0.42 EUR | https://www.supermagnete.de/eng/disc-magnets-neodymium/disc-magnet-10mm-2mm_S-10-02-N |
| S-10-03-N disc 10 x 3 | N42 | 1.8 kg (17.7 N) | 3.55 N | 1.8 g | 0.50 EUR | https://www.supermagnete.de/eng/disc-magnets-neodymium/disc-magnet-10mm-3mm_S-10-03-N |
| S-12-03-N disc 12 x 3 | N45 | 2.4 kg (23.5 N) | 4.76 N | 2.6 g | 0.54 EUR | https://www.supermagnete.de/eng/disc-magnets-neodymium/disc-magnet-12mm-3mm_S-12-03-N |
| Q-10-05-02-N block 10 x 5 x 2 | N50 | 1.2 kg (11.8 N) | 2.35 N | 0.76 g | 0.45 EUR | https://www.supermagnete.de/eng/block-magnets-neodymium/block-magnet-10mm-5mm-2mm_Q-10-05-02-N |
| Q-20-10-02-N block 20 x 10 x 2 | N45 | 2.1 kg (20.6 N) | 4.12 N | 3 g | 0.97 EUR | https://www.supermagnete.de/eng/block-magnets-neodymium/block-magnet-20mm-10mm-2mm_Q-20-10-02-N |

All are ±0.1 tolerance, nickel plated, 80 °C maximum, blocks magnetised through the 2 thickness. supermagnete measures on 2 cm steel and calls the figure "a theoretical maximum value"; "Even a small gap of half a millimetre can reduce the adhesive force by half" (https://www.supermagnete.de/eng/faq/force). Remanence by grade: N42 1.29 to 1.32 T, N45 1.32 to 1.37 T, N50 1.40 to 1.46 T (https://www.supermagnete.de/eng/physical-magnet-data).

The pin parking's magnet (model/kbdkid5/DESIGN.md, The joint), an S-04-02-N disc 4 x 2 in N45, pulls about 4.1 N to steel (Unconfirmed: recorded in 1168630 without its source).

Air gap: only the S-10-03-N page carries a chart, "Adhesive force in relation to the air gap between magnet and steel plate" (`work/research/downloads/supermagnete/chart_S-10-03-N.png`, from https://img.supermagnete.de/photos/orig/4611.png). Read off it (Derived, ±0.01 kg): 0 mm 1.58 kg, 1 mm 0.54 kg, 2 mm 0.22 kg, 3 mm 0.084 kg, 4 mm 0.044 kg. So 1 mm of air to steel leaves 34 % of the contact value.

Magnet to magnet: neither vendor gives numbers I could read. supermagnete states none; K&J's magnet-to-magnet ("Case 3") charts exist per product but the chart pages refused automated access (HTTP 403, for example https://www.kjmagnetics.com/pull-force-graph.asp?CI=3&pName=D62). K&J's article gives two useful anchors: the D82 disc (12.7 x 3.18, N42) pulls 6.44 lb to steel, and about 10 sheets of paper (about 0.76 mm) reduce that to 3 lb (https://www.kjmagnetics.com/blog/how-much-will-a-magnet-hold).

### Magnet to magnet across the gap (Derived)

I computed the attraction of two identical coaxial magnets with the rigid surface-charge model (uniform axial magnetisation, relative permeability 1; Bessel-integral form for discs, numerical face integral for blocks; `work/research/scripts/magnet_force.py`). Magnet to an ideal steel plate at gap d equals magnet to its mirror image at 2d, which lets the model be checked against the vendor figures (`work/research/scripts/magnet_validate.py`):

| Check | Vendor | Model | Vendor / model |
|---|---|---|---|
| K&J D82 to steel, contact | 6.44 lb | 7.2 to 7.7 lb | 0.84 to 0.89 |
| K&J D82 to steel, 0.76 mm | about 3 lb | 3.2 to 3.4 lb | 0.88 to 0.94 |
| K&J D62-N52 to steel, contact (https://www.kjmagnetics.com/proddetail.asp?prod=D62-N52) | 5.46 lb | 6.2 to 6.75 lb | 0.81 to 0.88 |
| supermagnete S-10-03-N chart, 0 mm | 1.58 kg | 2.37 kg | 0.67 |
| supermagnete S-10-03-N chart, 1 mm | 0.54 kg | 0.79 kg | 0.68 |

The model is 10 to 20 % above K&J and 50 % above supermagnete's chart (part of that is real steel saturating, which does not happen between two magnets, and part is supermagnete's conservative rating). For design I derate the model by 0.67 (the supermagnete ratio), the conservative end.

Magnet-to-magnet attraction, model at the grade's minimum remanence (maximum remanence about 3 to 8 % higher), and derated by 0.67:

| Pair | 0 mm | 0.8 mm | 1.0 mm | 1.0 mm derated |
|---|---|---|---|---|
| 6 x 3 N45 | 12.3 N | 6.1 N | 5.4 N | 3.6 N |
| 8 x 3 N45 | 18.3 N | 9.9 N | 8.9 N | 6.0 N |
| 10 x 2 N42 | 16.8 N | 8.6 N | 7.7 N | 5.2 N |
| 10 x 3 N42 | 23.3 N | 13.3 N | 12.0 N | 8.0 N |
| 12 x 3 N45 | 30.4 N | 17.9 N | 16.3 N | 10.9 N |
| 10 x 5 x 2 N50 | 16.4 N | 7.6 N | 6.7 N | 4.5 N |
| 20 x 10 x 2 N45 | 33.0 N | 17.2 N | 15.5 N | 10.4 N |

Two 0.4 skins give 0.8; with 0.2 print tolerance, design at 1.0. Between 0 and 1.0 the pull falls to 41 to 54 % of contact for these sizes. Lateral misalignment lowers it further (not modelled).

### What the joint must carry (Derived; the loads are assumptions)

Model: the joined board is a beam on two supports under the outer ends, span 2 x 140 = 280, joint at mid-span.

- Self weight: each half W = 0.2 kg x 9.81 = 1.96 N, centroid about 70 from the joint (assumed uniform). Each support carries W. Moment at the joint: M = R x 140 - W x 70 = W x 70 = 1.96 N x 0.070 m = **0.137 N m**.
- One keystroke at the joint: Rempel et al. measured subject mean peak keystroke forces of 1.6 to 5.3 N (J Biomech 1994;27(8):1101-4, PMID 8089165, https://pubmed.ncbi.nlm.nih.gov/8089165/). Point load P at mid-span: M = P x 280 / 4 = 5.3 N x 0.070 m = 0.371 N m, total **0.51 N m**.
- A hand resting on the middle: assumed 20 N (about 2 kgf; an assumption, no source): M = 1.40 N m, total **1.54 N m**.

Sagging closes the joint at the top and opens it at the bottom, so the halves hinge about the top edge of the joint face. A magnet resists with its pull times its distance from that edge. Magnets centred in a 12 tall face sit 6 below the top edge.

- Pull needed for self weight: 0.137 / 0.006 = 23 N. For one keystroke: 0.51 / 0.006 = 85 N. For a resting hand: 1.54 / 0.006 = 256 N.
- Four 10 x 3 pairs at 1.0 (they fit a 62 x 12 face with 1 of plastic above and below): 4 x 12.0 = 48 N model, 32 N derated, so 0.29 N m model, 0.19 N m derated.
- Five 8 x 3 pairs in a 10 tall face (5 below the top edge): 5 x 8.9 = 45 N model, 30 N derated, so 0.22 / 0.15 N m.

So magnets alone just hold the board's own weight (factor 1.1 to 2.1), and a single keystroke at the joint already needs 1.8 to 3.4 times what they give. In a 10 to 13 tall face, magnets cannot carry lap use: the joint would hinge open under every press near the middle and snap back.

### How others key the joint

- Ultimate Hacking Keyboard: "The halves are connected by precision-machined, hardened-steel guides mounted to the stainless steel plates", "combined with a pair of neodymium magnets", plus an optional "Lock screw ... for permanently connecting the keyboard halves" (https://www.crowdsupply.com/ugl/ultimate-hacking-keyboard).
- Dygma Raise: "We have added enough magnets and adjusted the tolerances of the metal pins to have the feeling we want for the joint", "You can hold it with one hand and it feels like it's one solid piece" (Nov 16, 2018 update, https://dygmaigg.backerkit.com/hosted_preorders/project_updates?page=8). Raise 2: "a succession of male and female pins", "magnets inside the keyboard to help keep both halves aligned", tension adjustable with hidden screws (https://dygma.com/blogs/product-development/this-is-what-an-overengineered-keyboard-looks-like).
- Cloud Nine C989M: "a large smart media knob and magnets (for extra strength) dovetail the two halves together" (review site, Unconfirmed: https://www.setupgamers.com/split-mechanical-keyboard/).
- HalFrgrd/SplitKeyboard (DIY, layered acrylic): an interlocking split line and 24 magnets of 4 x 2 in pockets of 6, a desk board (https://github.com/HalFrgrd/SplitKeyboard).
- bettsmatt/fuse (DIY, Choc, nice!nano, work in progress): "3D printed case with embedded magnets to allow the two split boards to snap together into a single board", keying not described (https://github.com/bettsmatt/fuse).
- r/ErgoMechKeyboards: I found no thread describing a magnetic join for lap use (search returned none; reddit itself was not reachable).

The commercial boards that join into one rigid piece use steel guides or pins for the stiffness and magnets for the closing force. None of the sources discusses lap use.

### Keying for kbdkid5 (Derived)

Steel dowel pins perpendicular to the joint face carry the bending: when the joint tries to rotate, each pin bears against its socket walls over its embedded length, and the pin itself transfers the moment across the joint face.

- Elastic bearing over an embedded length e: M = p_max x d x e^2 / 6 per pin, with d the pin diameter.
- Two Ø4 pins, 12 embedded on each side (4 x 24), resting-hand case (0.77 N m per pin): p_max = 6 x 0.77 / (0.004 x 0.012^2) = 8.0 MPa on the printed socket; bending stress in the pin at the joint face 0.77 / (pi x 0.004^3 / 32) = 123 MPa.
- Two Ø3 pins, 10 embedded (3 x 20): 15.4 MPa bearing, 290 MPa in the pin for the resting hand; 5.1 MPa and 96 MPa for the keystroke case.
- Hardened ISO 8734 pins are about 60 HRC (https://www.berger-tools.co.uk/Dowel_Pins__Extractable_Dowel_Pins/Iso8734a_Dowel_Pin_Through_Hardened_Din_6325/PartCode/ISO8734A-1[COMMA]0-4); DIN 6325 m6 is functionally equivalent (https://www.mcmaster.com/products/dowel-pins/specifications-met~iso-8734/). The pin stresses above are well within hardened steel. A safe bearing stress for printed PLA or PETG is my assumption (around 10 to 20 MPa, Unconfirmed), which makes 4 x 24 the comfortable choice and 3 x 20 marginal for a resting hand.
- Clearance: a diametral clearance c lets the joint open by about 12 x c / e at the bottom before the pins bear: 0.05 clearance over 12 embedded opens 0.05. Press the pins into one half, by hand so they pull out again for a new print; in the other, a printed hole reamed to size. The pin holes run horizontally, so print them as teardrops; the bearing load presses the layers together, the strong direction.
- Placement: both pins parallel and perpendicular to the slanted face, as far apart along the 62 as the bosses allow, at mid-height of the face, each in a solid boss reaching 12 into its tray. They also take the vertical shear between the halves (magnets resist shear with only about 1/5 of their pull, per the displacement forces above).
- All-printed alternative: a tongue on one tray's floor entering a groove in the other's carries the moment the same way (bearing couple over its length) but loads printed plastic in bending at the tongue root. Not sized here.

**Recommendation:**

- Face 12 tall or more: 4 pairs of S-10-03-N (10 x 3, N42) per joint, closing force about 32 N derated (48 N model) at 1.0. Face 10 tall: 5 pairs of S-08-03-N (8 x 3, N45), about 30 N derated.
- Two hardened dowel pins, 4 x 24 (or 3 x 20 if the bosses cannot reach 12 deep), fixed in one half, sliding fit in the other.
- The magnets then only close the joint; the pins carry the bending and shear. If the halves are too hard to pull apart with 4 pairs, drop to 3 pairs; pull-apart comfort is not something I could check.

## 6. Off-board connector on the PCB

11 matrix lines (4 x 7); 12 positions leave one spare. About 6 of height under the PCB.

| | JST SH SM12B-SRSS-TB | JST GH SM12B-GHS-TB | Wires soldered straight to PCB pads |
|---|---|---|---|
| Source | https://www.jst-mfg.com/product/pdf/eng/eSH.pdf (`work/research/downloads/jst-sh/eSH.pdf`) | https://www.jst-mfg.com/product/pdf/eng/eGH.pdf (`work/research/downloads/jst-gh/eGH.pdf`) | |
| Pitch | 1.0 | 1.25, with a latch | |
| Header | 14.0 (B) x 4.25 + 0.7 leads x 2.9 tall (+0.05) | 18.25 x 4.05 + 0.8 x 4.25 tall (+0.1) | none |
| Mated | (2.95) tall, (6.25) long | (4.35) tall, (7.15) long | wire and solder, under 1.5 |
| Rating | 1.0 A (AWG 28), 50 V | 1.0 A (AWG 26) | |
| Wire | AWG 32 to 28, insulation Ø0.4 to 0.8 | AWG 30 to 26, insulation Ø0.76 to 1.0 | any |
| Plug housing | SHR-12V-S(-B) | GHR-12V-S, 16.25 wide, 4.15 x 5.7 | |
| Cable | JST pre-crimped leads ASSHSSH28K (both ends SSH-003T-P0.2-H, UL1571 28 AWG, 51 / 102 / 152 / 254 / 305 long; https://www.farnell.com/datasheets/4788967.pdf), cut in half, one end into the housing, the other soldered to the nano | crimp yourself or buy pre-made | |

**Recommendation: JST SH SM12B-SRSS-TB**, side entry, on the PCB underside near the edge facing the nano, so the plug and cable run horizontally along the floor. It leaves 3 of the 6 free, has the smallest header, and JST sells pre-crimped 28 AWG leads, so no SH crimping tool is needed. GH adds a latch but needs 4.35 of height and 18.25 of width. Soldering the wires straight to pads is the lowest, but then the PCB cannot come out of the tray without desoldering.

## 7. Hotswap socket heights (2026-10-17)

Kailh CPG135001S30, the Choc v1 hotswap socket. Source: Kailh's product specification KH-PS-1702-35 rev. B with drawing KHA-PG135D-005EN, https://www.kailhswitch.com/Content/upload/pdf/202115927/CPG135001S30-data-sheet.pdf?rnd=914 (`work/research/downloads/kailh-cpg135001s30/`). Its drawing is vector graphics, read by rendering the page with pdftoppm.

- Confirmed (the drawing): body 1.80 ±0.05 thick, measured to the small bumps on its top face, 3.05 ±0.05 over its two contact bosses (2.90 ±0.05 across, they sit in the PCB's 3.0 holes), 1.85 ±0.1 at the end tabs, 13.15 ±0.15 tab to tab, 6.85 ±0.05 across both lobes, 4.65 per lobe, tabs 1.68 ±0.05 wide. The plastic body is 9.55 ±0.05 long along the tabs' axis (the plan view). The side view's 9.95 ±0.15 is between the tabs' inner ends, not the body. Mating force 3.0 kgf max, unmating 200 gf min.
- Derived (pixels on the drawing's front view, 1.85 = 167 px): the body's flat top 1.69 above its bottom, the tabs' tops level with the 1.85, their bottoms 0.37 above the body's bottom, so a tab is about 1.5 tall.
- The kbdkid4 package model's STEP (`library/pkg/23d245ff-14f8-48ad-af68-56ebb3a76786/0c4954f5-24c7-4f36-a4b7-4bbd2ff10646.step` in the Tubbles/kbdkid4 repository, probed with FreeCAD this session) matches the drawing's overall figures (13.15 tab to tab, 6.85 across, the body 9.55 between its end faces) but models the body and tabs as one 1.85 block whose top lies 0.17 under the PCB's underside, with bosses 2.9 across rising 1.15 above it: that gap is where kbdkid4's 2.02 reach comes from. Its section is the same over the body's height (probed at five heights), and its inside corners between the lobes are filled with a 1.5 and a 0.75 radius, as on the drawing's plan view, which `layout.HOTSWAP_SOCKET_FILLS_MM` covers for the tray. `layout.HOTSWAP_SOCKET_OUTLINE_MM` is the body's outline from that section at mid-height, the tabs left out, for the socket test strips' pockets: lobe A 4.75 long from its end to the step between the lobes, as on the drawing, and lobe B 4.80 from there, 0.75 chamfers on lobe A's outer corners and 0.75 rounds on lobe B's, and a 0.2 step on lobe B's end.

## 8. nice!nano socket strips (2026-10-20)

The user: "I want to solder 2 x 12 pin low profile socket strips on top of the nano so I don't have to solder wires directly to it. I've ordered "Mill Max 315-43-112-41-003000"", one per row over pins 1 to 12, "only the 12 southmost pins will get the socket strips", which leaves B+ and B- free, as nicekeyboards asks (section 1). Sources: Mill-Max's datasheet, https://www.mill-max.com/products/datasheet/315-43-112-41-003000, and catalog page 65 (series 310, 311 and 315), https://www.mill-max.com/sites/default/files/external/catalog/2017-11/065.pdf, whose Fig. 4 is this part's section and whose plan view gives the strip's outline, both saved in `work/research/downloads/millmax-315-43-112-41-003000/`. Read with pdftotext and from the rendered catalog page.

- Confirmed (datasheet): 12 pins at .100" (2.54), single row, through hole solder mount in .038" (0.965) holes, accepting round leads .015" to .022" (0.381 to 0.559). Above board height .095" (2.413), insulator height .071" (1.803), solder tail .030" (0.762) across and .095" (2.413) long. Tolerances: assembly ±.010" (0.25), the length ±.005" (0.127) up to 2", the insulator's width and height ±.005" (0.13), the pin length ±.005" (0.13).
- Confirmed (catalog page 65): the plan view draws the insulator the number of pins times .100" long and .100" wide, a pin every .100". Fig. 4 shows the insulator .071" tall with its top .095" over the board, so it stands .024" (0.61) clear of the board on the pins' sleeves, and the tail .095" long below the board's top, 0.813 below a 1.6 board's underside.
- Confirmed (calipered, 2026-10-24): the strips soldered on the user's nice!nano are not this part. Their tops stand about 4.23 over the board's top and their tails about 1.6 below its underside, the board about 1.6 thick. That is Mill-Max's series 310 standard solder tail (catalog page 65, Fig. 1): the top .165" (4.191) over the board, the insulator .110" (2.794) tall, the tail .125" (3.175) long below the board's top and .020" (0.508) across, accepting leads .015" to .025". The user: "Ok I see now that I've picked the wrong strips. Its not easy to swap these unfortunately". The layout still has this part's figures (work item 027).
- Not on either: the sleeves' diameter. `model/kbdkid5/scripts/layout.py` takes them as wide as the pads, 1.53 (Unconfirmed).
- Mating: the strips take round leads only, so the wires go in as solid 24 AWG (0.51) or 26 AWG (0.41) wire, pushed straight in and bent over (the user: "Yeah solid wire it is", doc/log/2026-10-20.md). Square header pins (0.64) are outside the range.

## 9. Choc v1 switch, calipered (2026-10-17 and 2026-10-20)

Kailh Choc v1, kbdkid4's `KHA-PG1350` package. The user's caliper on a real switch:

- Confirmed (calipered, 2026-10-20): center post 3.17 and side pegs 1.65 across, "Post is 3.17 and pegs are 1.65 mm diameter" (doc/work/012-switch-hole-test.md). The footprint's holes for them are 3.4 and 1.9 (`layout.CHOC_FOOTPRINT_HOLES_MM`).
- Confirmed (calipered, 2026-10-17): the contact blades are not equally thick, the pin near a side peg (footprint-local (-3.8, 5.0)) about 0.4, the middle one ((-5.9, 0.0)) about 0.2 (doc/log/2026-10-17.md, `layout.CHOC_PIN_CALIPERED_BLADE_THICKNESSES_MM`).
- Unconfirmed (kbdkid4's switch model, the `PG1350` STEP in kbdkid4's `KHA-PG1350` package): both blades 0.2 thick and 0.8 wide (`layout.CHOC_PIN_BLADE_THICKNESS_MM`, `CHOC_PIN_BLADE_WIDTH_MM`), from the housing's underside down to 2.65 below it, then narrowing to 0.2 at the tip, 3.0 below.

## 10. Screws

- Confirmed (the user, 2026-10-20): the M2 pan head screws on hand have "roughly 1.5 mm high heads" (doc/log/2026-10-20.md), the socket test backing's screws (`layout.BACKING_SCREW_HEAD_HEIGHT_MM`).
- Confirmed (measured, kbdkid4 commit 9c59d24, 2026-07-23): kbdkid4's screw heads are 3.77 across (`SCREW_HEAD_DIAMETER_MM` in `model/kbdkid4/scripts/export_plate.py`, `MOUNTING_SCREW_HEAD_DIAMETER_MM` in `model/kbdkid5/scripts/layout.py`).
- Unconfirmed: those heads' height, which the nice!nano clamp's screw takes at an assumed figure (model/kbdkid5/DESIGN.md, nice!nano, doc/log/2026-10-17.md, `layout.NANO_CLAMP_SCREW_HEAD_HEIGHT_MM`).
- On hand (the user, 2026-10-22): flat slotted head M2 screws with heads "1.42 mm high", "About 3.7 mm diameter, fully flat head", 50 each of M2 x 4, M2 x 5 and M2 x 8. Also a kit of 30 M2 x 6, 30 M2 x 8, 25 M2 x 10, 25 M2 x 12, 25 M2 x 16 and 20 M2 x 20, each in socket cap and in hex pan heads, with M2 washers and nuts, and Loctite "to lock the screws in if needed, for further vibration resistance".

## 11. Measured on kbdkid4's assembled board (2026-10-12)

The first print of kbdkid4's tray with the soldered left half in it. The nice!nano's depth is in section 1 (Top side parts).

- Confirmed (measured, kbdkid4 commit 26bddb5): the USB window around the left nice!nano's receptacle is 10.5 x 4.5, sized by what the user measured around the connector on the first print, with the receptacle's mouth 0.56 behind the tray's outer face (`USB_WINDOW_WIDTH_MM` in `model/kbdkid4/scripts/export_tray.py`, `USB_WINDOW_HEIGHT_MM` in `model/kbdkid4/scripts/tray_shape.py`). Derived: the right half's window, 1.74 lower for its taller sockets (kbdkid4 commit 5dc598e, `model/kbdkid4/scripts/tray_shape.py`).
- Confirmed (measured, kbdkid4 commit eb6fb7b): the power switch body's outer face 1.13 from the tray's outer face, so 0.07 past the board edge and 0.33 from the wall's inner face, where the package model puts it 0.09 inside the edge (`model/kbdkid4/scripts/export_tray.py`, the power switch comment). By the same measurement it sits 0.73 from its wall pocket's back, closer than the package model puts it (SUGGESTIONS.md, kbdkid4).
- Confirmed (measured, kbdkid4 commit 7255b7e): the key diode D123, a SOD-123 (package SOD3717X135), is 1.14 tall on the soldered board (`model/kbdkid4/scripts/export_plate.py`, the covered variant's comment).

## 12. Through-hole diodes (2026-10-17)

For the hand-wired frame's diodes (TODO.md).

- Confirmed (Diotec's 1N4148 datasheet, version 2017-08-25, from Electrokit 40310010, `work/research/downloads/electrokit-40310010-diotec-1n4148/`): the DO-35 body Ø1.9 ±0.1 and 3.9 ±0.4 long, the leads Ø0.5 at most, 62.5 ±3 end to end. "Compliant to RoHS, REACH". Electrokit has 2048 in stock. The distributor listings first recorded here gave 4.3 to 4.6 long.

## 13. Order list (2026-10-21)

Everything from Electrokit, prices with 25 % VAT, the least each listing sells, for both halves. The user placed this order on 2026-10-21, due a couple of days later.

| Part | Electrokit | Each | Least | Buy | SEK |
|---|---|---|---|---|---|
| Power switch, Knitter-switch MFP 120-R (section 2) | 41011898 | 19 | 1 | 2 | 38.00 |
| Reset button, TE FSM2JRT (section 3) | 41024339 | 4.50 | 2 | 2 | 9.00 |
| Battery header, JST PH 2-pin straight (section 4), no longer used by the tray | 41004562 | 2.30 | 6 | 6 | 13.80 |
| Key diodes, Diotec 1N4148 DO-35, 25 keys a half (section 12), only for the hand-wired frame | 40310010 | 0.25 | 50 | 50 | 12.50 |
| Thumb slide joystick, to try as a pointer (section 14) | 41003908 | 99 | 1 | 1 | 99.00 |
| Shipping | | | | | from 35 |

That is 172.30 SEK of parts and about 207 SEK with the cheapest shipping, or 73.30 and 108 without the joystick. Electrokit prices its shipping at checkout, from 35 SEK, and pickup at its Malmö store is free (its consumer terms). The other shops lose on shipping alone for an order this small: Mouser ships free only from 615 to 800 SEK (its Swedish pages differ), Elfa Distrelec closed its web shop on 2026-05-18 and sends its customers to RS, and TME had no MFP 120 in stock. Not in this order: the socket strips (section 8, the user's own order), the hotswap sockets, the nice!nano, the battery and the magnets.

## 14. Thumb slide joystick (2026-10-21)

For trying a pointer on the keyboard (TODO.md).

- Confirmed (Electrokit's page, 41003908 "Joystick - tum, glid", 7 in stock): a resistive analog slide joystick "liknande den som används i PSP1000", 5 kΩ, with no push button. Seen from below its pins are 1 the X output, 2 +5 V, 3 the Y output and 4 ground, on SMD pads 2 apart. Its rubber thumb pad comes off. On an Arduino each axis reads about 128 to 775.
- Unconfirmed (SparkFun's product page for the same joystick, COM-09426, which links no datasheet): pin 4 is the one nearest the two mounting tabs on one side. No drawing was found, so its size needs a caliper.
- Derived: across the nice!nano's 3.3 V each 5 kΩ track draws 0.66 mA, all the time unless its supply is switched.
- Not checked: which of the nice!nano's free pins can read an analog voltage, and how ZMK takes an analog pointer.

## Not confirmed

- nice!nano pad positions: measured on the manufacturer's render, ±0.1, not on a drawing or a board. The board is calipered (18.20 x 33.20), but the pads' insets were measured from the long edges of the render's 18.0 board and have not been measured on a real one. The shell's reach past the board is the render's 0.87, where the user's two calipers give 0.97. Footprints say 33.02 x 17.78, the kbdkid4 model 33.2 x 17.8.
- That every nice!nano v2 uses the C168688 receptacle: from the schematic label; the render's shell width (8.91) and tab spacing (4.02) agree with its drawing.
- The nano's finished hole size (render shows about 0.83).
- Heights of the nRF52840 (about 0.85 from distributors), LEDs, inductors and crystals; that the antenna is a PCB trace at the far end.
- That plastic over the antenna end detunes it only a little.
- SS-12D00 dimensions from makers other than SOFNG (retailers say 8 x 4 x 3.8, 2.54 pitch).
- The MFP 120-R's figures: from an untoleranced raster drawing of the MFP 140-R, its window's and leads' places taken centered, its slide force not published (section 2).
- The FSM2JRT's figures: from Tyco's 2008 catalogue drawing, not TE's current customer drawing, its leads' length as sold and its base's underside not known (section 3).
- Marketplace "3 x 6 mm" tactile switch dimensions; the PTS645's travel.
- Magnet-to-magnet forces: computed, not vendor data; derated to supermagnete's to-steel chart. K&J's magnet-to-magnet charts could not be read.
- The resting-hand load (20 N), the safe bearing stress of printed plastic, and the comfort of pulling 4 magnet pairs apart.
- Stock levels except LCSC C22355741.
