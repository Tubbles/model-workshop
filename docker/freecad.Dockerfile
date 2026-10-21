# Headless FreeCAD for every project's export scripts, which run in CI
# only, where .github/actions/freecad-image builds and caches the image.
# From the repository root, for example kbdkid5's PCB mock:
#
#     docker build -t freecad-headless -f docker/freecad.Dockerfile docker
#     docker run --rm -v "$PWD":/work -w /work freecad-headless \
#         freecadcmd kbdkid5/scripts/export_pcb.py --pass <mock.stl> [right]
#
# Debian trixie ships FreeCAD 1.x; freecad-python3 is the GUI-less subset
# that provides /usr/bin/freecadcmd.
FROM debian:trixie-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends freecad-python3 \
    && rm -rf /var/lib/apt/lists/*
