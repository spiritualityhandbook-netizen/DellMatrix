#!/usr/bin/env python3
"""C6 Boxes / Freeze / Scope-Group / Placement — failing-first
(Part I, MWL #144-#147).

Contracts (Unified Edition §14.3 C6 cards):
- #144 Boxes (DD-17): standing/named sandboxes — owner put/take,
  multiple boxes, the standing private box, all as one contract.
- #145 Freeze (DD-22): room/item pause — paused items stay visible,
  retain contents/position, stop aging/growth.
- #146 Scope/Group: the 53<->82 partnership as one pair; a named
  Group is never automatically a scope.
- #147 Placement (DD-50 grounding): idea/body/both, AUTO/BIND —
  replacement retains intended position; child placement respects
  the parent.

STATUS: FAILING-FIRST. Controls pass today (plane.box/unbox and
scoped growth are GS-4-proven machinery). Contract checks fail
where the C6 surface is absent. NO product code is changed by this
file.
"""
from __future__ import annotations

import glob
import inspect
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.open import open_program

OWNER = "C6BOXES1112"


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
    print("=== C6 BOXES / FREEZE / SCOPE-GROUP / PLACEMENT (FAILING-FIRST) ===")
    fails = []

    def check(name, cond, detail=""):
        print(f"[{'PASS' if cond else 'FAIL'}] {name}"
              + (f" :: {detail}" if detail else ""))
        if not cond:
            fails.append(name)

    _cleanup(OWNER)
    p = open_program(OWNER)
    plane = p.cube.session.plane
    plane.units.clear()
    plane.sandboxes.clear()
    for uid in ("c6_a", "c6_b", "c6_c", "c6_d"):
        p.place(uid, uid, words=f"{uid} harbor lantern", x=0.0, y=0.0)

    # CONTROL — plane.box/unbox roundtrip (GS-4-proven machinery).
    plane.box(["c6_a", "c6_b"], "c6vault", label="c6 vault")
    membership = getattr(plane, "sandboxes", {})
    in_box = "c6_a" in repr(membership) and "c6vault" in repr(membership)
    unboxed = plane.unbox("c6_a")
    check("CONTROL plane.box/unbox roundtrip works",
          in_box and unboxed is True,
          f"sandboxes={list(membership) if isinstance(membership, dict) else membership!r} "
          f"unbox={unboxed}")

    # #144a — multiple named boxes coexist with disjoint membership.
    plane.box(["c6_a"], "boxA", label="A")
    plane.box(["c6_c"], "boxB", label="B")
    boxes = getattr(plane, "sandboxes", {})
    both = "boxA" in repr(boxes) and "boxB" in repr(boxes)
    check("#144 multiple named boxes coexist", both,
          f"sandbox keys visible in repr: boxA={'boxA' in repr(boxes)} "
          f"boxB={'boxB' in repr(boxes)}")

    # #144b — the standing private box: an owner-private box exists
    # by standing rule, not only by explicit creation.
    private_markers = [k for k in repr(boxes).split()
                       if "private" in k.lower()]
    has_private_api = any("private" in n.lower() and "box" in n.lower()
                          for n in dir(plane)) or any(
        "private_box" in n.lower() for n in dir(p))
    check("#144 standing private box exists per owner",
          bool(private_markers) or has_private_api,
          f"private markers in sandboxes={private_markers or 'none'}; "
          f"private-box API={'present' if has_private_api else 'ABSENT'}")

    # #144c — owner put/take as a typed door (not raw plane surgery).
    put_take = [n for n in dir(p) + dir(plane)
                if n.lower() in ("put_in_box", "take_from_box", "box_put",
                                 "box_take", "put", "take")]
    check("#144 owner put/take typed door exists",
          bool(put_take),
          f"put/take symbols={put_take or 'none'} "
          f"(only plane.box/unbox list surgery exists)")

    # #145 — Freeze: a pause operation on an item, with the frozen
    # item retained (visible, contents/position intact).
    freeze_surface = [n for n in dir(p) + dir(plane)
                      if "freeze" in n.lower() or "pause" in n.lower()]
    check("#145 freeze/pause operation exists for items",
          bool(freeze_surface),
          f"freeze/pause symbols={freeze_surface or 'none'}")

    # #146a — Scope/Group: a named Group concept distinct from scope.
    group_surface = [n for n in dir(p)
                     if "group" in n.lower() and not n.startswith("_")]
    check("#146 named Group surface exists (distinct from scope)",
          bool(group_surface),
          f"Program group symbols={group_surface or 'none'}")

    # CONTROL — growth scope selection exists (GS-4-proven): the
    # grow_ideas scope_ids parameter is the scope door a Group must
    # never silently become.
    sig = inspect.signature(p.grow_ideas)
    check("CONTROL grow_ideas exposes explicit scope_ids selection",
          "scope_ids" in sig.parameters,
          f"grow_ideas parameters={sorted(sig.parameters)}")

    # #147a — placement retains intended position (behavioral
    # control-grade check on plane.place).
    p.place("c6_pos", "c6 positioned", words="c6 positioned harbor",
            x=4.5, y=-2.5)
    unit = plane.units.get("c6_pos")
    pos_ok = unit is not None and abs(getattr(unit, "x", 999) - 4.5) < 1e-9 \
        and abs(getattr(unit, "y", 999) + 2.5) < 1e-9
    check("#147 plane.place retains intended position", pos_ok,
          f"unit pos=({getattr(unit, 'x', None)}, {getattr(unit, 'y', None)})")

    # #147b — AUTO/BIND typed placement modes on the confirm
    # placement path (idea/body/both).
    from form.dell_matrix import confirm_lineage
    place_fn = getattr(confirm_lineage, "place", None) or getattr(
        confirm_lineage, "confirm_proposal", None)
    psig = inspect.signature(place_fn) if place_fn else None
    pparams = set(psig.parameters) if psig else set()
    check("#147 confirm placement accepts AUTO/BIND placement modes",
          bool(pparams & {"mode", "placement_mode", "bind", "auto"}),
          f"{getattr(place_fn, '__name__', 'none')} parameters="
          f"{sorted(pparams) or 'none'} (no placement-mode parameter)")

    total = 9
    print(f"C6 BOXES FREEZE: {total - len(fails)}/{total} checks passed"
          + (f"; FAILING: {fails}" if fails else ""))
    _cleanup(OWNER)
    return not fails


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
