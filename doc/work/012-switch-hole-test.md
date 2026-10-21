# 012 Switch hole test strip

Status: implemented (8ebfb81, exported in CI, not printed yet)

The user, 2026-10-20: "I need another test strip: testing the switch holes that the center pin and the two side pins goes through. On eg. the hotswap socket test strip these pin holes are too wide and doesn't aid in sideways stability of the switch".

Measured by the user with calipers on a real switch (2026-10-20): "Post is 3.17 and pegs are 1.65 mm diameter". The footprint's holes are 3.4 and 1.9 (layout.CHOC_FOOTPRINT_HOLES_MM, kbdkid4's PCB drills), grown by pull_in (0.2) on the socket strips, so 3.8 and 2.3 as modelled. The hole strip found that 3.x holes print about 0.15 per side smaller than modelled (DESIGN.md, Hole strip), so the post hole prints about 3.5, about 0.33 over the post. The peg holes print about 1.9 by the print model, about 0.25 over the pegs, with no measurement of how holes this small print.

Planned: six single-key cells at 19.05 pitch of the frame's body (1.6 thick), printed top face down as the frame prints, with no walls, bosses or sockets. Each cell steps the post hole and both peg holes together through six clearances from slightly tight to the socket strips' holes, cell 6 repeating those as the reference. The blades' holes stay at the frame's 3.2, so only the post and pegs hold the switch. Cell k has k notches. Push a switch in from the top and wiggle it: the best cell is the tightest the switch still goes fully into by hand and sits flat in, without play sideways.

Implemented (8ebfb81): `kbdkid5/scripts/export_socket_test.py switch`, built by `socket_test_shape.build_switch_strip()`. Cells 1 to 5 print -0.05 to +0.15 over the calipered post and pegs in 0.05 steps, taking a hole to print 0.15 per side small, cell 6 has the socket strips' holes. In CI as `kbdkid5_Switch_Hole_Test.stl` in the `kbdkid5-socket-stl` artifact. DESIGN.md (Switch hole strip) has the figures, README.md how to try it.
