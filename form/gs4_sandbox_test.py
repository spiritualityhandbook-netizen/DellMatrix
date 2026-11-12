#!/usr/bin/env python3
"""GS-4 sandbox containment — FAILING-FIRST suite (Director mail
1a1d05d91f6401dc, 2026-11-12).

The wall contract (Ace's Growth Selection Doctrine, 2026-11-12): "a
sandbox that doesn't effect anything outside of it" — growth involving
boxed (sandboxed) units must not use material from outside the wall.

The defect (reproduced independently twice on merged main @074b30f;
PR #403 + PR #402 comment 6827580827): default RingedGrowth pair
enumeration is wall-blind — cross-sandbox pairs are scored like any
pair (the wall enters only as _affinity's soft in_scope 0.2 penalty)
and produce (a) two-parent Solstice proposals spanning the wall and
(b) single-parent Equinox/Standstill drift offspring of boxed units
carrying outside units' tokens under inside-only lineage.

This suite pins the contract the GS-4 containment build must satisfy.
At publication (on main @074b30f, no implementation) the two
manifestation checks FAIL verbatim — that failure IS the evidence.
The controls PASS today and must keep passing after the build:
scope_ids containment, unboxed backward-compat, empty scope, and
invalid scope refusal are pre-existing lawful behavior the build
must not break.

Field (5 co-located units; same field as the PR #403 independent
probe so this suite is falsifiable against its published log):
  in_a, in_b   boxed into sandbox 'vault1'
  out_a        outside near-twin of in_a
  out_b        outside, moderate overlap
  out_c        outside, distant tokens (drift source)
Outside-only tokens are computed mechanically from the field texts.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.open import open_program

OWNER_TAG = "GS4SANDBOX1112"
INSIDE = ["in_a", "in_b"]
OUTSIDE = ["out_a", "out_b", "out_c"]

FIELD = [
    ("in_a", "harbor lantern inkeep",
     "harbor lantern craft timber copper kettle song inkeep cellar vault"),
    ("in_b", "harbor lantern inforge",
     "harbor lantern craft timber copper kettle song inforge cellar vault"),
    ("out_a", "harbor lantern outkeep",
     "harbor lantern craft timber copper kettle song outkeep cellar vault "
     "axolotl azurite"),
    ("out_b", "harbor copper outdrift",
     "harbor lantern craft copper song outdrift axolotl azurite basalt"),
    ("out_c", "glacier tundra outpost",
     "glacier tundra obsidian wolf outpost fjord"),
]


def _cleanup(owner):
    import glob
    import shutil
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


def _raw_words(text):
    return set(re.findall(r"[a-z]+", (text or "").lower()))


def _build(owner, box_inside):
    _cleanup(owner)
    p = open_program(owner)
    plane = p.cube.session.plane
    plane.units.clear()
    plane.sandboxes.clear()
    p.nursery.proposals.clear()
    for uid, label, words in FIELD:
        p.place(uid, label, words=words, x=0.0, y=0.0)
    if box_inside:
        plane.box(list(INSIDE), "vault1", label="gs4 vault")
    return p


def _snapshot(p):
    return [{
        "pid": pid,
        "kind": getattr(prop, "kind", None),
        "label": prop.label,
        "words": prop.words,
        "parents": list(prop.parents or []),
    } for pid, prop in p.nursery.proposals.items()]


def smoke() -> bool:
    print("=== GS-4 SANDBOX CONTAINMENT (FAILING-FIRST) ===")
    fails = []

    def check(name, ok, detail):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} :: {detail}")
        if not ok:
            fails.append(name)

    in_set, out_set = set(INSIDE), set(OUTSIDE)
    inside_words, outside_words = set(), set()
    for uid, label, words in FIELD:
        (inside_words if uid in in_set else outside_words).update(
            _raw_words(label) | _raw_words(words))
    out_only_tokens = outside_words - inside_words

    # --- RUN A: boxed field, default growth — THE WALL CONTRACT ------
    p = _build(f"{OWNER_TAG}A", box_inside=True)
    res = p.grow_ideas(1)
    steps = res.get("steps") or [{}]
    pairs_scanned = steps[0].get("pairs_scanned")
    props = _snapshot(p)

    # A0 setup truth: the wall exists in the plane's own authority.
    check("A0 wall is real in plane authority",
          list(p.cube.session.plane.enhance_scope("in_a")) == ["in_b"],
          f"enhance_scope(in_a)={p.cube.session.plane.enhance_scope('in_a')}")

    # A1 enumeration: 5 units = 10 pairs; wall-respecting scans 4
    # (1 inside-inside + 3 outside-outside), never the 6 cross-wall.
    check("A1 enumeration excludes cross-wall pairs",
          pairs_scanned == 4,
          f"pairs_scanned={pairs_scanned} (10 = all pairs incl. 6 cross-wall; "
          f"4 = wall-respecting)")

    # A2 manifestation 1: no proposal's parents span the wall.
    cross = [pr for pr in props
             if set(pr["parents"]) & in_set and set(pr["parents"]) & out_set]
    check("A2 no proposal parents span the wall",
          len(cross) == 0,
          f"cross-parented proposals={len(cross)} "
          f"{[(pr['pid'], pr['parents']) for pr in cross]}")

    # A3 manifestation 2: no single-parent (drift) offspring of a boxed
    # unit carries any outside-only token.
    drift = []
    for pr in props:
        if pr["parents"] and set(pr["parents"]) <= in_set:
            hits = sorted(out_only_tokens
                          & _raw_words(pr["label"] + " " + pr["words"]))
            if hits:
                drift.append((pr["pid"], pr["parents"], hits))
    check("A3 no boxed drift offspring carries outside-only tokens",
          len(drift) == 0,
          f"drift offspring carrying outside-only tokens={drift}")

    # --- RUN B (control): same field, NO sandbox — backward compat ---
    p2 = _build(f"{OWNER_TAG}B", box_inside=False)
    res2 = p2.grow_ideas(1)
    props2 = _snapshot(p2)
    steps2 = res2.get("steps") or [{}]
    check("B1 unboxed control still scans all pairs",
          steps2[0].get("pairs_scanned") == 10,
          f"pairs_scanned={steps2[0].get('pairs_scanned')} (10 expected)")
    sig_a = sorted((pr["kind"], tuple(pr["parents"]), pr["label"])
                   for pr in props)
    sig_b = sorted((pr["kind"], tuple(pr["parents"]), pr["label"])
                   for pr in props2)
    check("B2 boxed default output equals unboxed output (defect pin: "
          "boxing must change growth output; today it changes nothing)",
          sig_a != sig_b,
          f"boxed proposals={len(props)} unboxed proposals={len(props2)}; "
          f"identical={(sig_a == sig_b)}")

    # --- RUN C (control): scope_ids door contains — pre-existing -----
    p3 = _build(f"{OWNER_TAG}C", box_inside=True)
    res3 = p3.grow_ideas(1, scope_ids=list(INSIDE))
    props3 = _snapshot(p3)
    steps3 = res3.get("steps") or [{}]
    leaks3 = [pr for pr in props3
              if set(pr["parents"]) & out_set
              or (out_only_tokens
                  & _raw_words(pr["label"] + " " + pr["words"]))]
    check("C1 scope_ids growth scans only the selected pair",
          steps3[0].get("pairs_scanned") == 1,
          f"pairs_scanned={steps3[0].get('pairs_scanned')} (1 expected)")
    check("C2 scope_ids growth has zero leaks",
          len(leaks3) == 0,
          f"leaks={len(leaks3)}")

    # --- RUN D (controls): empty + invalid scope — pre-existing ------
    p4 = _build(f"{OWNER_TAG}D", box_inside=True)
    raised = None
    try:
        p4.grow_ideas(1, scope_ids=["missing_unit_xyz"])
    except ValueError as e:
        raised = str(e)
    check("D1 invalid scope ID refuses with ValueError",
          raised is not None and "not on plane" in raised,
          f"ValueError={raised!r}")
    res4 = p4.grow_ideas(1, scope_ids=[])
    props4 = _snapshot(p4)
    check("D2 empty scope grows nothing (no silent fallback to full)",
          len(props4) == 0,
          f"proposals={len(props4)} scope_mode={res4.get('scope_mode')}")

    total = 10
    print(f"GS-4 SANDBOX: {total - len(fails)}/{total} checks passed"
          + (f"; FAILING (failing-first, defect present): {fails}"
             if fails else ""))
    for owner in ("A", "B", "C", "D"):
        _cleanup(f"{OWNER_TAG}{owner}")
    return not fails


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
