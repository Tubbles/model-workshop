# CLAUDE.md

Guidance for Claude Code working in this repository: only what is for agents. Read [README.md](README.md) (what the workshop is, how CI builds and names the STLs, the history) and [model/README.md](model/README.md) (the projects) first, since this file does not repeat them. Each project's own CLAUDE.md has what is specific to it.

## Layout

- `model/<project>/`: one directory per project, set up as Starting a project says. kbdkid5's also has its `DESIGN.md`.
- `docker/freecad.Dockerfile`: the one FreeCAD image every export runs in. `.github/actions/freecad-image` provides it to a CI job. Their header comments have the details.
- `docker/placement.Dockerfile`: the placement solver's Python image (work item 016), run locally through podman. Its header comment has the details, README.md the commands.
- `tools/placement/`: the placement solver's generic core, which never imports a project. Its package docstring (`__init__.py`) is the code map. kbdkid5's problems for it are `model/kbdkid5/scripts/place.py` (kbdkid5's CLAUDE.md).
- `resources/kbdkid3-plate-left.FCStd`: the kbdkid3 plate model that kbdkid4's and kbdkid5's plates are cut from.
- `.github/workflows/ci.yml`: the one workflow, with every project's jobs. Its comments explain how the jobs are laid out and which changes run no CI.
- The documents: Conventions says what goes where.

## FreeCAD scripts

The module docstrings of `model/kbdkid4/scripts/board_step.py` and `model/kbdkid5/scripts/freecad_common.py` document freecadcmd's quirks and the scaffolding that works around them. Read one before writing a FreeCAD script here.

## Starting a project

- A directory under `model/` named for the model, with `CLAUDE.md`, `README.md` and `scripts/`, and a row in `model/README.md`'s project table.
- A job in `.github/workflows/ci.yml` named after the project, its directory's name (or the project plus a kind, when it has several artifacts), in the style of the jobs there: checkout, the `SHORT_SHA` step, `.github/actions/freecad-image`, the export with the repository mounted at `/work`, and `actions/upload-artifact`, its artifact named as README.md says (Getting the STLs) with `${{ env.SHORT_SHA }}` for the hash.
- Sections in PLAN.md, TODO.md and SUGGESTIONS.md when it has entries for them.

## Workflow

- **FreeCAD exports run in CI only, never locally.** The user, 2026-10-20: "Ok don't do exports solely to run cmp on them. If you make a doc change then you can assume nothing gets changed on the model exports. In fact, change it so all freedcad export are done in CI, never locally." To see an export, push and read its job's log. A question about built geometry becomes a figure the export script prints, so it runs in CI. Plain Python (`model/kbdkid5/scripts/check_layout.py`, `python3 -m py_compile`) runs locally. Brief every subagent with this rule, implementers and reviewers alike. Why: an hour went to serial review rounds in which each agent re-ran exports locally to compare them, while a print the user wanted waited.
- **Never export, or compare exports, to prove a part unchanged.** The user, 2026-10-20: "I actually think its completely redundant, so let's remove it". The one exception, agreed the same day ("we can do that check when we do a massive redactor in that case?"): after a large refactor meant to change no geometry, offer to compare the STLs of the CI runs before and after it. Download both runs' artifacts and sha256 each STL. GitHub's artifact `digest` hashes the zip, which differs between runs even for identical STLs.
- **Don't wait for or check CI after a change to documentation or comments alone.** The user, 2026-10-21: "Like always, no need to check CI output in case you only make document changes". A change to comments alone builds the same parts as before.
- **Test prints go fast.** The printer is the bottleneck of the design loop. The user, 2026-10-17: "the printer has been idling during this wait, wasting precious print time. I need iterations to be much faster." The user fetches STLs from CI's artifacts ("I always fetch stls from github som make sure to commit and push"), so a test print is committed and pushed as soon as its change is ready and the plain Python checks pass, with the CI run's link. Review and docs follow in later commits while it prints, and a defect a review finds goes into the next print. Brief an implementer for that one code change and its export, with a report the moment it passes: on 2026-10-17 a bundled brief turned a one-constant change into a 19 minute round, and the user asked "How is that still building??? Its like a single line change, it should be checked in within a minute". Scope a test print's work item to the printable: a change to shared code that pulls in other parts is its own item. The export's own checks are enough: no mesh to solid conversions (one such probe ran over 13 minutes without output), no verification rounds beyond what the item asks. While one part prints, prepare the next.
- **Every test print comes with how to try it**: what to do with the part, what a good, a loose and a too tight result feel like, and what to report back. The user, 2026-10-17: "it was hard to understand what I was supposed to feel".
- **A test print the user is waiting for goes ahead of review, fix and docs rounds.** On 2026-10-20 the switch hole test strip waited about an hour behind three review rounds. The user: "Just wondering how finding such a small snag could take an hour. I would have assumed the switch hole test strip would be done by now." Tell the user plainly which print is current and whether anything pushed since changes it.
- **Artifact names carry the project and the commit**, by README.md's scheme (Getting the STLs), so a zip's name alone tells what it holds. The user, 2026-10-17: "we need to start name the github zip files that I download with e.g. kbdkid5-mock-stl-<short commit hash>", and 2026-10-21: "Also remove the redundant "stl" part of the final CI artifact names".
- **Commit and push completed changes without asking**, every file, docs and CLAUDE.md included. The user: "always commit and push" (2026-07-22), and again "feel free to commit and push as you wish" (2026-07-25) after finished changes were left uncommitted with an offer to commit them. Committing is part of finishing the work.
- **Refactor without asking.** The user, 2026-10-21, asked whether check_layout.py could be refactored first: "Yes absolutely, no need to even ask permission for that? Refactors are encouraged". A refactor is its own commit and changes no behavior, which the plain Python checks' output, identical before and after, shows.
- **Tools come through a Dockerfile in the repository**, not a downloaded AppImage. The user, 2026-07-22: "why did you download an app image? just do a dockerfile directly or something". A Dockerfile is reproducible and pinnable, and the same image runs in CI.
- **Choose a bought part with the `component-engineering` skill**, to the rules in doc/components.md (How parts are chosen).
- **Never quote a PDF from a WebFetch summary.** On 2026-07-26 WebFetch returned a sentence that does not exist in the PDF it summarized. Download with `curl -L -o` and quote from `pdftotext -layout` output, or read the pages as images for drawings.
- **After `fmt -w 72` on a commit message**, put the `Assisted-by:` and `Claude-Session:` trailers back on lines of their own: fmt joins them into one paragraph, which breaks git's trailer parsing. Leave the `Claude-Session:` line out of the width check, since its URL alone is over 72 columns.

## Conventions

- Every piece of information has one place. The user, 2026-10-21: "every piece of information shall only be present in its correct place. E.g. instructions only for agents go into CLAUDE, while stuff of interest also for humans go into README". Anywhere else it gets at most a pointer (file and section), and saying it again in other words still counts as a copy. Only a decision log may repeat what one other file holds. The places:
  - `README.md` (the root's, `model/README.md` and each project's): everything of interest to a human, such as what a part is, how to get, print, assemble and use it, the CI artifacts and their files, and the commands. Agents read them too, so a CLAUDE.md never repeats them.
  - `CLAUDE.md` (this one and each project's): only what is for agents, such as workflow rules, a code map that points at the modules' docstrings, tooling gotchas and how to change the code safely. Each says near its top which documents to read first.
  - The scripts' docstrings and comments: how the code works.
  - `model/kbdkid5/DESIGN.md`: kbdkid5's design, its decisions and figures.
  - `doc/print-model.md` and `doc/components.md`, as README.md describes them. A new measurement goes into one of them, with its date and source.
  - `doc/work/NNN-name.md`: a work item, with the request in the user's words, its scope, a `Status:` line (todo, implemented, verified) and what is still open. It points at DESIGN.md, print-model.md or components.md for figures, and stays when done.
  - `doc/log/`: decisions, in a new dated file, written once and never edited, each entry tagged with `#topic` words.
  - `PLAN.md`: long term goals. `TODO.md` and `SUGGESTIONS.md`: what their headers say, and nothing that is already a work item.
- What an agent learns goes into this repository's docs, in its place above, never into an agent's local memory. The user, 2026-10-21: "Make sure that stuff you put in "local memories" that are of any importance are put into the repos CLAUDE.md, as appropriate."
- Keep the docs a change touches current in the same commit: the project's README.md, CLAUDE.md and DESIGN.md, the work items' status, the comments in the scripts.
- Cite a kbdkid4 commit as kbdkid4's (`kbdkid4 9864702`), since part of the history is in Tubbles/kbdkid4 (README.md, History). It is checked out at `~/dev/kbdkid4`.
- `tmp/` is scratch space. `work/` holds untracked notes, research downloads (`work/research/downloads/`) and probe scripts (`work/kbdkid4-probes/`). Neither is committed.
- Markdown: one paragraph per line, never reflowed.
