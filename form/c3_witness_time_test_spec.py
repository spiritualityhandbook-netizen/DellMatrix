#!/usr/bin/env python3
"""C3 Witness & Time — failing-first (Part I, MWL #131-#136, #173).

Contracts (Unified Edition §14.3 C3 cards):
- #131 C3.MirrorCompare: Mirror gains the true compare — pair
  comparison through the C3 comparator, honest pagination.
- #132 C3.Trace (DD-52): Trace covers the entire current process —
  full retrieval beyond 512 entries without silent loss, with
  shown/total truthfulness.
- #133 C3.FailureDoors (DD-32): Analyze / Revert / Retry per Ace's
  failure doctrine — Retry targets an identified failure.
- #134 C3.Rooms (DD-53): Rooms are Ace's to close — chosen-room
  operations cannot overwrite another room's later work.
- #135 C3.Undo (DD-54) RETAINED REMAINDER: the session-local slice
  is settled (PR #481, scoped PARTIAL per Director 7040476004);
  what remains is room/multi-actor undo and Core II snapshot-stack
  unification. This suite pins the remainder: undo must survive a
  save/load boundary (the stack is one stack, not session-local).
- #136 C3.Alpha: history member + close ceremony — old generations
  freeze/confirm/restore under new code.
- #173 (design prerequisite): the retention/compaction contract —
  full-fidelity history at capture (no silent 24-entry cut). The
  deep retention battery lives in form/r5d_history_retention_test.py
  (R5-D prep, HELD for implementation); the capture-side check here
  is the C3.Trace witness of the same cut.

STATUS: FAILING-FIRST. Controls pass today. NO product code is
changed by this file.
"""
from __future__ import annotations

import glob
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.open import Program, open_program

OWNER = "C3WITNESS1112"


def _cleanup(owner):
    state = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
    for f in glob.glob(os.path.join(state, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            raise RuntimeError(f"cleanup failed for {f}: {e}")


def smoke() -> bool:
    print("=== C3 WITNESS & TIME (FAILING-FIRST) ===")
    fails = []

    def check(name, cond, detail=""):
        print(f"[{'PASS' if cond else 'FAIL'}] {name}"
              + (f" :: {detail}" if detail else ""))
        if not cond:
            fails.append(name)

    _cleanup(OWNER)
    p = open_program(OWNER)

    # CONTROL — session-local undo/redo exist (the settled Q-LC.1
    # slice; PR #481). This control guards the remainder checks
    # below from reading as "undo does not exist at all".
    undo_api = callable(getattr(p, "undo", None)) and callable(
        getattr(p, "redo", None))
    check("CONTROL Program.undo/redo exist (session-local slice)",
          undo_api, f"undo={callable(getattr(p, 'undo', None))} "
                    f"redo={callable(getattr(p, 'redo', None))}")

    # #132/#173 — capture-side: 40 noted entries must ALL be
    # retrievable in-process. Today the in-memory history is cut at
    # capture (form/open.py history cap), so early entries are
    # silently gone — the Trace witness of the retention defect.
    for i in range(40):
        p.note(f"c3 trace entry {i:02d}")
    lines = p.history_lines(10000)
    blob = "\n".join(lines)
    first_kept = "c3 trace entry 00" in blob
    last_kept = "c3 trace entry 39" in blob
    check("#132 Trace retrieves the entire current process "
          "(no silent capture cut)",
          first_kept and last_kept and len(lines) >= 40,
          f"retrieved={len(lines)} of 40 noted; "
          f"entry00_present={first_kept} entry39_present={last_kept}")

    # #135 REMAINDER — undo across the save/load boundary: note an
    # action, save, load a FRESH Program, and undo must still reach
    # the pre-save action (one unified stack). Session-local stacks
    # fail this by construction.
    _cleanup(OWNER)
    p2 = open_program(OWNER)
    p2.note("c3 undo boundary marker")
    try:
        p2.save()
    except Exception as e:
        check("#135 undo survives save/load (unified stack)", False,
              f"save raised {type(e).__name__}: {e}")
        p2 = None
    if p2 is not None:
        p3 = Program.load(OWNER)
        try:
            res = p3.undo()
            undone = isinstance(res, dict) and res.get("ok") is True
            detail = f"fresh-load undo result={res!r}"[:160]
        except Exception as e:
            undone = False
            detail = f"fresh-load undo raised {type(e).__name__}: {e}"
        check("#135 undo survives save/load (unified stack)", undone,
              detail)

    # #131 — Mirror compare surface: a C3 comparator door with
    # pagination, distinct from the H4 bare coherence float.
    mirror_surface = [n for n in dir(p) if "mirror" in n.lower()]
    mirror_mod = None
    for modname in ("form.dell_matrix.mirror", "form.mirror"):
        try:
            mirror_mod = __import__(modname, fromlist=["x"])
        except ImportError:
            pass
    check("#131 Mirror true-compare surface exists",
          bool(mirror_surface) or mirror_mod is not None,
          f"Program mirror symbols={mirror_surface or 'none'}; "
          f"mirror module={'present' if mirror_mod else 'ABSENT'}")

    # #133 — Failure doors: Analyze / Revert / Retry as typed doors.
    doors = {n: callable(getattr(p, n, None))
             for n in ("analyze_failure", "revert", "retry",
                       "analyze", "retry_last")}
    present = [k for k, v in doors.items() if v]
    check("#133 Analyze/Revert/Retry failure doors exist",
          len(present) >= 2,
          f"door symbols present={present or 'none'} "
          f"(undo alone is not the failure-door set)")

    # #134 — Rooms: a chosen-room WRITE/close surface (Ace closes
    # rooms). list_rooms/set_view are view-layer only today.
    from form.dell_matrix import view_rooms
    rooms = view_rooms.list_rooms()
    room_write = [n for n in dir(p)
                  if "room" in n.lower() and not n.startswith("_")]
    closers = [n for n in room_write if "close" in n or "open" in n
               or "enter" in n or "switch" in n]
    check("CONTROL view_rooms.list_rooms returns the room roster",
          isinstance(rooms, list) and len(rooms) >= 1,
          f"rooms={len(rooms) if isinstance(rooms, list) else rooms!r}")
    check("#134 chosen-room write/close surface exists on Program",
          bool(closers),
          f"Program room symbols={room_write or 'none'}; "
          f"write/close symbols={closers or 'none'} "
          f"(set_view is view-only)")

    # #136 — Alpha close ceremony: generations can be frozen and
    # confirmed as a ceremony (not only checkpoint mechanics).
    from form import persist_rest
    ceremony = [n for n in dir(persist_rest)
                if "alpha" in n.lower() or "ceremony" in n.lower()
                or "freeze_generation" in n.lower()]
    check("#136 Alpha freeze/confirm/restore ceremony surface exists",
          bool(ceremony),
          f"persist_rest ceremony symbols={ceremony or 'none'} "
          f"(checkpoint mechanics exist; the Alpha ceremony does not)")

    total = 8
    print(f"C3 WITNESS TIME: {total - len(fails)}/{total} checks passed"
          + (f"; FAILING: {fails}" if fails else ""))
    _cleanup(OWNER)
    return not fails


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
