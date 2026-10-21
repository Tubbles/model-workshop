# Solder spool axle

`model/solder-spool-axle/scripts/export_spool_axle.py` exports the axle of a solder spool holder, which a cradle holds by a stub on each end while the spool hangs on it by its bore. The body is 19 mm across and 39.5 mm long, the stubs 7.9 mm across and 2.6 mm long. The spools it is for have a rim about 2 mm wide and 2 mm high inside the bore at one face, which keeps them from lying flat on a plain cylinder, so the body has a 2.6 mm wide, 2.4 mm deep groove under that rim, placed for a 27 mm long spool centered on the body. Turn the axle over for a spool put on the other way round.

CI runs the export from this repository's root, in the image built from `docker/freecad.Dockerfile`:

    mkdir -p spool
    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/solder-spool-axle/scripts/export_spool_axle.py --pass spool/Solder_Spool_Axle.stl

CI uploads it as the `solder-spool-axle-<short commit hash>` artifact: `Solder_Spool_Axle.stl`.
