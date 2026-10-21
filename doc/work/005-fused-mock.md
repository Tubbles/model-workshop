# 005 Fused mock

Status: implemented

The user's ask: fuse the PCB mock and the plate into one print, with the pin holes the switch friction fits into, "miniscule slits", so switches can be mounted for a feel. `kbdkid5/scripts/export_mock.py` exports it for both halves: the PCB mock with a slit on each pin in place of the two 3.0 pin holes, fused with the plain plate, printed PCB side down. `kbdkid5/scripts/export_slit_test.py` exports a strip of six single-key cells with slit widths 0.5 to 1.0 to find the width that grips. The PCB mock's builder moved into `kbdkid5/scripts/pcb_shape.py`. `kbdkid5/scripts/export_pcb.py` keeps the left half's output, and its right half now has the footprints unmirrored, like the fused mock's. Both in CI as the `mock-stl` artifact.

The slit sizes are model figures from kbdkid4's switch model, not caliper figures. The strip is there to settle the width on a real print.
