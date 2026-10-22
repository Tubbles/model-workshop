# 024 One CI artifact per project

Status: todo

The user, 2026-10-22: "Also let's tidy up the artifact names and structure. Let's adhere to the format [project]-[shortsha], and then have every model in the zip be named [project]-[model], where model shall include "mock" or "test" accordingly. That way well have one single kbdkid5-[shortsha].zip to download each time, and in it we'll find all the models related to kbdkid5, and its easy to tell the actual models from the tests and mocks. I guess we'll have 4 artifacts after this change, two keyboards, the camera arm and the spool axle".

Scope:

- Four artifacts per CI run: `kbdkid5-<short commit hash>`, `kbdkid4-<short commit hash>`, `camera-arm-<short commit hash>` and `solder-spool-axle-<short commit hash>`, each holding every STL of its project in one flat folder.
- Every STL named `<project>-<model>.stl`, lower case with hyphens, its model naming what it is and, for a mock or a test print, saying so: for example `kbdkid5-tray-left.stl`, `kbdkid5-pcb-mock-left.stl`, `kbdkid5-socket-test-pocket.stl`, `kbdkid5-nano-bay-test.stl`, `kbdkid4-case-right.stl`, `camera-arm-t-nut.stl`. kbdkid4's files drop the board's `_v1`. A project with one model names its file after the project alone (`solder-spool-axle.stl`), since `<project>-<model>` would repeat it.
- The keyboards' jobs stay separate, so they still build in parallel. Each uploads its files as an intermediate artifact, and one job per keyboard merges them into the project's artifact and deletes the intermediates. The merge runs once the keyboard's export jobs have finished, even if one failed, so a failing export does not hold back the other files. The run is red then.
- README.md (Getting the STLs), each project's README (the files in its artifact), CLAUDE.md (the artifact naming bullet and Starting a project) and the workflow's comments follow.
