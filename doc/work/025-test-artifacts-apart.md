# 025 Test prints and mocks in an artifact of their own

Status: implemented

The user, 2026-10-22, after work item 024: "Actually could we move out all test and mock models to their own artifact, eg. kbdkid5-test-[shortsha].zip?"

Scope:

- Each keyboard gets two artifacts: `<project>-<short commit hash>` with its real parts and `<project>-test-<short commit hash>` with its test prints and mocks, every STL whose name says "test" or "mock" (work item 024's naming, which stays). camera-arm and solder-spool-axle have none and keep their one artifact, so a run ends with six.
- Every export job's files are all parts or all tests, so each job still uploads one intermediate artifact at its end. kbdkid5's tray job also exports the nice!nano bay test, so that test moves to a job of its own.
- The intermediates' names tell the two apart, so that each merge's pattern matches its own group only and never a merged artifact: `<project>-part-<kind>-<short commit hash>` and `<project>-test-<kind>-<short commit hash>`. A group whose files come from one job alone is uploaded by that job straight under the group's artifact name, without a merge.
- Each group's merge is its own job, needing only its group's export jobs, so a failing test export does not hold back the real parts.
- README.md (Getting the STLs), the project READMEs (which artifact each file is in), CLAUDE.md, the workflow's comments and work item 024's notes follow.

Done:

- Every keyboard export job's STLs are all parts or all tests, and it uploads them once at its end as `<project>-part-<kind>-<short commit hash>` or `<project>-test-<kind>-<short commit hash>`. The nice!nano bay test moved out of `kbdkid5-tray` into a job of its own, `kbdkid5-nano-bay-test`, which uploads `kbdkid5-test-nano-bay-<short commit hash>`.
- The `kbdkid5` and `kbdkid4` jobs merge the parts (`<project>-part-*-<short commit hash>`) into `kbdkid5-<short commit hash>` and `kbdkid4-<short commit hash>`, and the `kbdkid5-test` job merges kbdkid5's test prints and mocks (`kbdkid5-test-*-<short commit hash>`) into `kbdkid5-test-<short commit hash>`. Each needs only its group's export jobs and runs once they all passed, deleting the intermediates. kbdkid4's PCB mocks are its only test files and come from one job, so `kbdkid4-pcb` uploads them straight as `kbdkid4-test-<short commit hash>`.
- A merge's pattern needs a kind between `part-` or `test-` and the hash, so it never matches a merged artifact or the other group's intermediates. Checked with Python's fnmatch against every artifact name the workflow makes. The merge action matches with minimatch, which agrees with fnmatch here, since no pattern or name has a slash, a leading dot or a brace.
- README.md (Getting the STLs), the kbdkid5 and kbdkid4 READMEs, CLAUDE.md (the artifact bullet and Starting a project), the two projects' CLAUDE.md, the workflow's header comment, work item 024 and SUGGESTIONS.md follow.

Open: CI's first run with this change should end with the six artifacts and no intermediates: kbdkid5 with 12 STLs, kbdkid5-test with 11, kbdkid4 with 8, kbdkid4-test with 2, camera-arm with 4 and solder-spool-axle with 1.
