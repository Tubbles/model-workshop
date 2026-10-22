# Python for the placement solver (work item 016, tools/placement/) and
# the scripts that use it, run locally through podman and by CI's
# placement job, which builds it on every run.
# From the repository root, for example kbdkid5's layout check:
#
#     podman build -t placement -f docker/placement.Dockerfile docker
#     podman run --rm -v "$PWD":/work -w /work placement \
#         python3 model/kbdkid5/scripts/check_layout.py
#
# Every package is pinned, matplotlib's own dependencies too, each to a
# release at least two weeks old on 2026-10-21, and comes from a wheel.
# CPython 3.14.8 on Debian trixie, the FreeCAD image's release, has a
# wheel of each (numpy, SciPy and contourpy need 3.12 or later). The
# digest pins the base image's build, so a rebuild starts from the same
# one: a newer base changes the tag and the digest together.
FROM python:3.14.8-slim-trixie@sha256:fbecd461fc72d21b2143c6eaba25143738079154a6d0ea3da3aec724f50eed4a

RUN pip install --no-cache-dir --only-binary=:all: \
        numpy==2.5.3 scipy==1.18.1 shapely==2.2.0 matplotlib==3.11.2 pillow==12.3.0 \
        contourpy==1.4.0 cycler==0.12.1 fonttools==4.66.1 kiwisolver==1.5.1 packaging==26.3 \
        pyparsing==3.3.3 python-dateutil==2.9.0.post0 six==1.17.0
