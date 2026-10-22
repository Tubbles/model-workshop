# 024 One CI artifact per project

Status: implemented

The user, 2026-10-22: "Also let's tidy up the artifact names and structure. Let's adhere to the format [project]-[shortsha], and then have every model in the zip be named [project]-[model], where model shall include "mock" or "test" accordingly. That way well have one single kbdkid5-[shortsha].zip to download each time, and in it we'll find all the models related to kbdkid5, and its easy to tell the actual models from the tests and mocks. I guess we'll have 4 artifacts after this change, two keyboards, the camera arm and the spool axle".

Scope:

- Four artifacts per CI run: `kbdkid5-<short commit hash>`, `kbdkid4-<short commit hash>`, `camera-arm-<short commit hash>` and `solder-spool-axle-<short commit hash>`, each holding every STL of its project in one flat folder.
- Every STL named `<project>-<model>.stl`, lower case with hyphens, its model naming what it is and, for a mock or a test print, saying so: for example `kbdkid5-tray-left.stl`, `kbdkid5-pcb-mock-left.stl`, `kbdkid5-socket-test-pocket.stl`, `kbdkid5-nano-bay-test.stl`, `kbdkid4-case-right.stl`, `camera-arm-t-nut.stl`. kbdkid4's files drop the board's `_v1`. A project with one model names its file after the project alone (`solder-spool-axle.stl`), since `<project>-<model>` would repeat it.
- The keyboards' jobs stay separate, so they still build in parallel. Each uploads its files as an intermediate artifact, and one job per keyboard merges them into the project's artifact and deletes the intermediates. The merge runs once the keyboard's export jobs have finished, even if one failed, so a failing export does not hold back the other files. The run is red then. Changed after the review: the merge runs only once every export passed (below).
- README.md (Getting the STLs), each project's README (the files in its artifact), CLAUDE.md (the artifact naming bullet and Starting a project) and the workflow's comments follow.

Done:

- CI uploads the four artifacts, each with its project's STLs in one folder.
- Every STL is named `<project>-<model>.stl`, the side last (`kbdkid5-frame-backing-left.stl`). The PCB mocks, kbdkid4's PCB replica included, are `pcb-mock`, the fused mock `fused-mock` and the covered plates `plate-covered`. The camera arm's arm is `camera-arm.stl`, after the project alone, since `camera-arm-arm` would repeat it. The project READMEs list every file.
- The camera arm's export script names its four files itself, so they are renamed there, in `PART_FILE_NAMES`.
- The keyboards' export jobs upload their STLs as intermediate artifacts, `<project>-<kind>-<short commit hash>`, the names their artifacts had before. The `kbdkid5` and `kbdkid4` jobs merge them with `actions/upload-artifact/merge@v4` and delete them, once every one of the keyboard's export jobs has passed. The review found that a merge after a failed export leaves its partial artifact beside the full one a rerun makes, under the same name, since the merge action cannot overwrite and an attempt's artifacts stay. Merging only after every export passed, with each export job uploading once at its end (the PCB mock now goes into `kbdkid5-mock-<short commit hash>` with the fused mock and the slit test strips), leaves one artifact per project. After a failed export the job artifacts stay on the run page and rerunning the failed jobs merges them.

CI run 39824435442 (dd2b37a) ended with exactly the four artifacts, flat, and no intermediates: kbdkid5 with 23 STLs, kbdkid4 with 10, camera-arm with 4 and solder-spool-axle with 1, named as above. Nothing is open.
