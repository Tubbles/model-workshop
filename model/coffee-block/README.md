# Coffee block

`model/coffee-block/scripts/export_coffee_block.py` exports a plain block, 40 x 60 x 120 mm, to stand a large container on under the coffee machine's spout while it is descaled. The STL lies on one of its 60 x 120 faces, the way it prints: 40 mm high, the lowest and steadiest way on the bed. Any face can go up in use, for a lift of 40, 60 or 120 mm.

CI runs the export from this repository's root:

    mkdir -p coffee
    docker run --rm -v "$PWD":/work -w /work freecad-headless \
        freecadcmd model/coffee-block/scripts/export_coffee_block.py --pass coffee/coffee-block.stl

CI uploads it as the `coffee-block-<short commit hash>` artifact: `coffee-block.stl`. The job's log prints the block's size.
