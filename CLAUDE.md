# CLAUDE.md

Guidance for Claude Code working in this repository. Each project's own CLAUDE.md has what is specific to it.

## What this is

A workshop for 3D-printable models, each built by FreeCAD scripts that run headless in a container. The user's request that started it (2026-10-21): "Ok its time we create a dedicated repo for these models that doesn't really belong here. I am thinking all of them, including everything we did for kbdkid4 and kbdkid5, the trays, plates, everything." The decisions behind the layout are in [doc/log/2026-10-21.md](doc/log/2026-10-21.md).

## Layout

- One directory per project (`kbdkid5/`, `kbdkid4/`, `solder-spool-axle/`, `camera-arm/`), each with a `CLAUDE.md` for agents, a `README.md` for humans and `scripts/`. kbdkid5 also has its `DESIGN.md`.
- `docker/freecad.Dockerfile`: the one FreeCAD image every export runs in (Debian trixie's FreeCAD). `.github/actions/freecad-image` restores it from the Actions cache, keyed on the Dockerfile, or builds it.
- `resources/kbdkid3-plate-left.FCStd`: the kbdkid3 plate model that kbdkid4's and kbdkid5's plates are cut from.
- `.github/workflows/ci.yml`: one workflow whose jobs run in parallel, each job's name starting with its project's directory.
- `doc/print-model.md`: how the user's printer prints, every measurement with its source, and every test print. `doc/components.md`: the parts' research and calipered dimensions. `doc/log/`: dated decision logs. `doc/work/`: work items.
- `PLAN.md`, `TODO.md` and `SUGGESTIONS.md` at the root, with a section for each project that has entries.

## History

This repository continues kbdkid5's history up to 8ebfb81, so the commit hashes that kbdkid5's docs, logs and work items cite resolve here. `kbdkid4/scripts/`, `solder-spool-axle/scripts/` and `camera-arm/scripts/` hold Tubbles/kbdkid4's model scripts as of its 155110d, and their history up to that commit is in Tubbles/kbdkid4 under `scripts/` (`~/dev/kbdkid4` locally). Mark a kbdkid4 commit as kbdkid4's when citing it (`kbdkid4 9864702`).

## kbdkid4's board files

kbdkid4's parts read the board files from a checkout of Tubbles/kbdkid4 ([kbdkid4/CLAUDE.md](kbdkid4/CLAUDE.md), Board files). The direction is one way: kbdkid4 holds the board design and no model code, and reads nothing from here. The user (2026-10-21): "I want that agent to reference this repo for measurements etc, instead of the other way around, so kbdkid4 becomes a pure librepcb repo again."

## FreeCAD scripts

freecadcmd exits 0 even when the script raised, sets `__name__` to the file's stem, runs a script twice and intercepts dash arguments even after `--pass`. Two module docstrings document it and the scaffolding that works around it (`key=value` arguments, leaving through `run_and_exit` and `os._exit`): `kbdkid4/scripts/board_step.py`'s and `kbdkid5/scripts/freecad_common.py`'s. Read them before writing a FreeCAD script here. A Python failure stays hidden unless the script leaves through `run_and_exit`. The spool axle's and the camera arm's scripts import kbdkid4's `board_step.py` for the STL export and the scaffolding.

## Starting a project

- A directory named for the model, with `CLAUDE.md`, `README.md` (what it is, the printed parts and how each prints, the artifact and its files) and `scripts/`.
- A job in `.github/workflows/ci.yml` named after the directory (or the directory plus a kind, when the project has several artifacts), in the style of the jobs there: checkout, the `SHORT_SHA` step, `.github/actions/freecad-image`, the export with the repository mounted at `/work`, and `actions/upload-artifact`.
- The artifact named `<project>-<kind>-stl-${{ env.SHORT_SHA }}`, or `<project>-stl-${{ env.SHORT_SHA }}` for a project with one artifact.
- A row in README.md's project table, and sections in PLAN.md, TODO.md and SUGGESTIONS.md when it has entries for them.

## Workflow

- **FreeCAD exports run in CI only, never locally.** The user, 2026-10-20: "Ok don't do exports solely to run cmp on them. If you make a doc change then you can assume nothing gets changed on the model exports. In fact, change it so all freedcad export are done in CI, never locally." To see an export, push and read its job's log. A question about built geometry becomes a figure the export script prints, so it runs in CI. Plain Python (`kbdkid5/scripts/check_layout.py`, `python3 -m py_compile`) runs locally. Why: an hour went to serial review rounds in which each agent re-ran exports locally to compare them, while a print the user wanted waited.
- **Never export, or compare exports, to prove a part unchanged.** The user, 2026-10-20: "I actually think its completely redundant, so let's remove it". The one exception, agreed the same day ("we can do that check when we do a massive redactor in that case?"): after a large refactor meant to change no geometry, offer to compare the STLs of the CI runs before and after it. Download both runs' artifacts and sha256 each STL. GitHub's artifact `digest` hashes the zip, which differs between runs even for identical STLs.
- **Test prints go fast.** The printer is the bottleneck of the design loop. The user, 2026-10-17: "the printer has been idling during this wait, wasting precious print time. I need iterations to be much faster." The user fetches STLs from CI's artifacts ("I always fetch stls from github som make sure to commit and push"), so a test print is committed and pushed as soon as its change is ready and the plain Python checks pass, with the CI run's link. Review and docs follow in later commits while it prints, and a defect a review finds goes into the next print. Brief an implementer for that one code change and its export, with a report the moment it passes. Scope a test print's work item to the printable: a change to shared code that pulls in other parts is its own item. The export's own checks are enough: no mesh to solid conversions (one such probe ran over 13 minutes without output), no verification rounds beyond what the item asks. While one part prints, prepare the next.
- **Every test print comes with how to try it**: what to do with the part, what a good, a loose and a too tight result feel like, and what to report back. The user, 2026-10-17: "it was hard to understand what I was supposed to feel".
- **A test print the user is waiting for goes ahead of review, fix and docs rounds.** On 2026-10-20 the switch hole test strip waited about an hour behind three review rounds. The user: "Just wondering how finding such a small snag could take an hour. I would have assumed the switch hole test strip would be done by now." Tell the user plainly which print is current and whether anything pushed since changes it.
- **Artifact names carry the project and the commit** (the user, 2026-10-17: "we need to start name the github zip files that I download with e.g. kbdkid5-mock-stl-<short commit hash>"), so a zip's name alone tells what it holds. The hash is the pull request head's for pull requests, since `github.sha` is a merge commit there.
- **Commit and push completed changes without asking**, every file, docs and CLAUDE.md included. The user: "always commit and push" (2026-07-22), and again "feel free to commit and push as you wish" (2026-07-25) after finished changes were left uncommitted with an offer to commit them. Committing is part of finishing the work.
- **Tools come through a Dockerfile in the repository**, not a downloaded AppImage. The user, 2026-07-22: "why did you download an app image? just do a dockerfile directly or something". A Dockerfile is reproducible and pinnable, and the same image runs in CI.
- **Never quote a PDF from a WebFetch summary.** On 2026-07-26 WebFetch returned a sentence that does not exist in the PDF it summarized. Download with `curl -L -o` and quote from `pdftotext -layout` output, or read the pages as images for drawings.
- **After `fmt -w 72` on a commit message**, put the `Assisted-by:` and `Claude-Session:` trailers back on lines of their own: fmt joins them into one paragraph, which breaks git's trailer parsing. Leave the `Claude-Session:` line out of the width check, since its URL alone is over 72 columns.

## Conventions

- `tmp/` is scratch space. `work/` holds untracked notes, research downloads (`work/research/downloads/`) and probe scripts (`work/kbdkid4-probes/`). Neither is committed.
- Keep the docs a change touches current in the same commit: the project's README.md, CLAUDE.md and DESIGN.md, the work items' status, the comments in the scripts.
- A new measurement goes into `doc/print-model.md` (how a print comes out against the model) or `doc/components.md` (a part's dimensions), with its date and source.
- Decisions go in a new dated file in `doc/log/`, written once and never edited, each entry tagged with `#topic` words.
- Work items live in `doc/work/` as `NNN-name.md` with a `Status:` line (todo, implemented, verified), and stay there when done. `TODO.md` is the user's inbox: an item moves to `doc/work/` once it is fleshed out.
- Markdown: one paragraph per line, never reflowed.
