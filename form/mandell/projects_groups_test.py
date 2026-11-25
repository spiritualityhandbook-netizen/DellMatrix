"""Phase M — named projects (groups) + perspectives (README program).

README §2 listed "Nested projects / perspectives" as PLANNED / not
implemented. Grounding at 0a78783 found: no project authority existed;
perspectives were already implemented in three layers (Plane
perspective/zoom persisted, R7.1 compose_views, R7.2 Perspective
Studio) but had no single user-path proof; the grouping authority
that exists is the Plane Sandbox, whose label did NOT persist
(persist.py serialized member ids only; the restorer re-boxed with
the default label).

Ace chose Option 1 (2026-10-25): a project is a named Plane sandbox
group. This phase therefore:

  - fixes Sandbox.label persistence in the persist writer/restorer
    pair (restorer stays backward-compatible with the legacy
    {sid: [member_ids]} shape);
  - adds REPL group commands (create / add / remove / show / delete /
    groups) on Plane.box/unbox — no new authority;
  - proves perspectives at the real user path in the same suite.

Project semantics are stated, not hidden: a group is a sandbox, so
Plane.enhance_scope scopes a member's enhancement to its group-mates.

Proof standard: CROSS_PROCESS + REAL_USER_PATH — separate OS
processes of the actual REPL (`python3 -m form.repl`), using only the
documented contract: work, `save`, restart with `--load`.

  proc A  create two ideas; group create; add both by label;
          duplicate add refused; missing-group add honest; zoom one
          idea; save
  proc B  --load: group NAME and membership survived (the label fix);
          page shows the zoomed idea (zoom persisted); cross-group
          add refused naming the current group; remove one; save
  proc C  --load: removal persisted; delete the group; save
  proc D  --load: group gone, honest miss on show
  studio  --load: perspective studio compose + legend + leave
          (session saved through the canonical save)
  legacy  separate owner: state file rewritten to the legacy
          {sid: [members]} shape loads with members intact and the
          default label — old saves never lose their groups
  control no-save: group work in a process that exits without `save`
          is absent from a later plain start

Isolation: unique owner per run; owner state absence verified before
proc A. Cleanup removes exactly the owners' files via canonical
paths; a cleanup failure other than an absent file fails loudly.
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import uuid

CHECKS: list = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))


def _cleanup(owner: str) -> None:
    """Remove the test owner's state files via canonical paths.

    Absent files are fine. Any other cleanup error is raised — a
    swallowed cleanup failure would silently contaminate later runs.
    """
    from form.dell_matrix.nursery import owner_nursery_path
    from form.persist import _path
    paths = [owner_nursery_path(owner), _path(owner)]
    paths += glob.glob(f"form/state/checkpoint_{owner}_*")
    errors = []
    for path in paths:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except OSError as exc:
            errors.append(f"{path}: {exc}")
    try:
        shutil.rmtree(f"form/state/ideas_{owner}")
    except FileNotFoundError:
        pass
    except OSError as exc:
        errors.append(f"ideas_{owner}: {exc}")
    if errors:
        raise AssertionError("cleanup failed: " + "; ".join(errors))


def _repl(commands: list, owner: str, load: bool,
          timeout: int = 120):
    cwd = os.path.abspath(".")
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if load:
        args.append("--load")
    env = {**os.environ, "PYTHONPATH": cwd}
    result = subprocess.run(
        args, cwd=cwd, env=env, input="\n".join(commands) + "\n",
        capture_output=True, text=True, timeout=timeout)
    return result.returncode, result.stdout


def smoke() -> bool:
    from form.persist import _path
    owner = f"mproj_{uuid.uuid4().hex[:8]}"
    legacy_owner = f"mleg_{uuid.uuid4().hex[:8]}"
    try:
        check("setup: owner state absent before proc A",
              not os.path.exists(_path(owner)))

        # ── Proc A: build the group, zoom, save ──────────────────
        rc, out = _repl([
            "create an idea called alpha",
            "create an idea called beta",
            "group create research",
            "group add alpha to research",
            "group add beta to research",
            "group add alpha to research",
            "group add alpha to nosuchgroup",
            "group show research",
            "zoom beta",
            "save", "quit",
        ], owner, load=False)
        check("A: exits clean", rc == 0)
        check("A: group created on the sandbox authority",
              "Group created: research [project_research]" in out,
              out[-600:])
        check("A: members added by label",
              "Added alpha (alpha) to group 'research'" in out
              and "Added beta (beta) to group 'research'" in out,
              out[-600:])
        check("A: duplicate add refused honestly",
              "alpha is already in group 'research'" in out, out[-600:])
        check("A: add to a missing group is an honest miss",
              "No group named 'nosuchgroup'" in out, out[-600:])
        check("A: show lists both members",
              "Group 'research' [project_research] · 2 member(s)" in out,
              out[-600:])
        check("A: zoom by label opens the idea page",
              "Idea page · beta" in out, out[-600:])
        check("A: session saved", "Session saved." in out)

        # ── Proc B: --load — name + membership + zoom persisted ──
        rc, out = _repl([
            "groups",
            "group show research",
            "page",
            "group create other",
            "group add beta to other",
            "group remove alpha from research",
            "save", "quit",
        ], owner, load=True)
        check("B: exits clean", rc == 0)
        check("B: group NAME survived save/load (label persistence)",
              "research [project_research] · 2 member(s)" in out,
              out[-800:])
        check("B: membership survived save/load",
              "alpha · alpha" in out and "beta · beta" in out,
              out[-800:])
        check("B: zoom target survived save/load",
              "Idea page · beta" in out, out[-800:])
        check("B: cross-group add refused, naming current group",
              "beta is in group 'research' — remove it from there first"
              in out, out[-800:])
        check("B: remove works",
              "Removed alpha (alpha) from group 'research'" in out,
              out[-800:])

        # ── Proc C: --load — removal persisted; delete the group ─
        rc, out = _repl([
            "group show research",
            "group delete research",
            "groups",
            "save", "quit",
        ], owner, load=True)
        check("C: exits clean", rc == 0)
        check("C: removal persisted across the process boundary",
              "Group 'research' [project_research] · 1 member(s)" in out,
              out[-800:])
        check("C: delete releases members and removes the group",
              "Group 'research' deleted · 1 member(s) released" in out,
              out[-800:])

        # ── Proc D: --load — deletion persisted ──────────────────
        rc, out = _repl([
            "groups",
            "group show research",
            "quit",
        ], owner, load=True)
        check("D: exits clean", rc == 0)
        check("D: deleted group stays deleted; other group remains",
              "other [project_other] · 0 member(s)" in out
              and "No group named 'research'" in out, out[-800:])

        # ── Studio proc: perspectives at the real user path ──────
        rc, out = _repl([
            "perspective studio",
            'compose [{"id":"v1","role":"user","pos":[0,0],'
            '"facing":"E","mode":"whole"}]',
            "legend",
            "leave",
            "quit",
        ], owner, load=True)
        check("studio: exits clean", rc == 0)
        check("studio: compose_views surface composes a real view",
              "Composed 1 view(s) [REAL]" in out
              and "source=program.cube.session.plane.units" in out,
              out[-800:])
        check("studio: leave saves the session canonically",
              "Studio session saved" in out, out[-800:])

        # ── Legacy control: pre-Phase-M save shape still loads ───
        rc, out = _repl([
            "create an idea called gamma",
            "group create archive",
            "group add gamma to archive",
            "save", "quit",
        ], legacy_owner, load=False)
        check("legacy: setup session saved", "Session saved." in out)
        state_path = _path(legacy_owner)
        with open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)
        sandboxes = state["plane"]["sandboxes"]
        check("legacy: writer now stores label + members",
              sandboxes.get("project_archive", {}).get("label")
              == "archive"
              and sandboxes["project_archive"]["members"] == ["gamma"],
              json.dumps(sandboxes))
        state["plane"]["sandboxes"] = {
            sid: list(entry["members"])
            for sid, entry in sandboxes.items()}
        with open(state_path, "w", encoding="utf-8") as fh:
            json.dump(state, fh)
        rc, out = _repl(["groups", "group show project_archive", "quit"],
                        legacy_owner, load=True)
        check("legacy: old-shape save loads, members intact",
              "sandbox [project_archive] · 1 member(s)" in out
              and "gamma · gamma" in out, out[-800:])

        # ── No-save control: unsaved group work does not persist ──
        rc, out = _repl([
            "create an idea called delta",
            "group create ephemeral",
            "group add delta to ephemeral",
            "quit",
        ], owner, load=False)
        check("control: unsaved session ran", rc == 0
              and "Added delta (delta) to group 'ephemeral'" in out)
        rc, out = _repl(["groups", "quit"], owner, load=False)
        check("control: without save, a plain start has no groups",
              "No groups yet" in out, out[-500:])

        passed = sum(1 for _, ok in CHECKS if ok)
        print(f"PROJECTS_GROUPS: {passed}/{len(CHECKS)}")
        return all(ok for _, ok in CHECKS)
    finally:
        _cleanup(owner)
        _cleanup(legacy_owner)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
