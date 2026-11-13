#!/usr/bin/env python3
"""Q-U.2 DOCK-LANDING WALL ADMISSIBILITY suite (failing-first origin:
the U2 probe evidence in director-reports/
SANDBOX_DOCK_CONFIRM_DEFECT_2026-11-13.md; repair scope CONFIRMED by
Director mail 1a1d44118259b159, 2026-11-13).

The defect (INTEGRATION evidence, repo's scripted-FakeProvider dock
harness at main 6d5f821): the inference dock's DIRECT verbs —
synthesize / relate / relate_field — landed PENDING proposals whose
parents span a sandbox wall. 'sandbox' occurred 0 times in
form/dell_matrix/inference_dock.py; the field snapshot carried no
wall fields; landing validation checked only parents-subset
conditions. Reproduced: synthesize([in_a, out_a]) -> PENDING
docked_cross_7748; relate(in_a, out_c) -> PENDING cross-wall;
relate_field(in_a) -> wall-blind pre-filter, PENDING with parents on
both sides of the wall.

The authorized contract (Q-U.2): enforce canonical parent-wall
admissibility on dock landing for the three direct verbs, BEFORE
pending proposal persistence, with an explicit refusal receipt.
Canonical wall semantics are GS-4's (form/dell_matrix/
ringed_growth.py _wall_key / _malformed_boxed, read from the Plane's
own box records): all parents share ONE wall key; a malformed box
claim (sandboxed=True, id missing / unknown / membership-
inconsistent) refuses fail-closed, never collapsed to unboxed;
unboxed parents share the unboxed key. Enforcement is the host's —
never the docked judge's. Snapshot wall fields are NOT in this
circuit; confirm placement and the auto-confirm sweep are separate
circuits (Q-U.3 / Q-U.5); Q-U.4 (manual cross-wall confirm) is on
Director HOLD and untouched here.

CONTROL that must keep working: the growth path — RingedGrowth
hands only wall-mate pairs to session.synthesize (GS-4 filter,
pairs_excluded_cross_sandbox receipted), and those docked pairs
still land (checks G1/G2).

Field: the GS-4 / PR #403 field — in_a/in_b boxed into 'vault1';
out_a near-twin, out_b moderate, out_c distant, all unboxed.
Evidence class: INTEGRATION (real Program/Nursery via production
loaders, scripted provider — the dock_proposal_b_test pattern).
smoke() is the regress-harness entry point (returns bool).
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.open import open_program

OWNER_TAG = "DOCKWALL1113"
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


def _build(owner, box_inside=True):
    _cleanup(owner)
    p = open_program(owner)
    plane = p.cube.session.plane
    plane.units.clear()
    plane.sandboxes.clear()
    p.nursery.proposals.clear()
    for uid, label, words in FIELD:
        p.place(uid, label, words=words, x=0.0, y=0.0)
    if box_inside:
        plane.box(list(INSIDE), "vault1", label="dock wall vault")
    return p


def _make_session(p):
    """The U2 probe's session: dock() + the MaximalJudge — a
    compliant scripted judge whose parents are exactly the targets
    it was shown (the maximal acceptance a real model's output
    could receive)."""
    from form.dell_matrix import inference_dock as idock

    class MaximalJudge(idock.FakeProvider):
        def generate(self, prompt, *, timeout_s, max_chars):
            self.calls += 1
            self.last_prompt = prompt
            targets = []
            marker = "[targets]\n"
            if marker in prompt:
                raw = prompt.split(marker, 1)[1]
                end = raw.find("\n\n[")
                if end != -1:
                    raw = raw[:end]
                try:
                    entries = json.loads(raw)
                    targets = [e.get("uid") or e.get("pid")
                               for e in entries
                               if isinstance(e, dict)]
                except Exception:
                    targets = []
            return json.dumps({
                "label": "Docked Cross",
                "words": "docked judge synthesis words",
                "detail": "authored from all shown targets",
                "goals": ["probe goal"],
                "reason": "scripted judge accepts all shown targets",
                "parents": targets,
            })

    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    sess._provider = MaximalJudge("valid")
    return sess


def _shown_ids(sess):
    """Target ids in the judge's last prompt (target first)."""
    prompt = sess._provider.last_prompt or ""
    if "[targets]\n" not in prompt:
        return []
    raw = prompt.split("[targets]\n", 1)[1]
    end = raw.find("\n\n[")
    if end != -1:
        raw = raw[:end]
    try:
        return [e.get("uid") or e.get("pid") for e in json.loads(raw)]
    except Exception:
        return []


def _cross_wall_props(p):
    in_set, out_set = set(INSIDE), set(OUTSIDE)
    return [pid for pid, prop in p.nursery.proposals.items()
            if set(prop.parents or []) & in_set
            and set(prop.parents or []) & out_set]


def smoke() -> bool:
    print("=== Q-U.2 DOCK-LANDING WALL ADMISSIBILITY ===")
    fails = []

    def check(name, ok, detail):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} :: {detail}")
        if not ok:
            fails.append(name)

    # --- Build A: the walled field --------------------------------
    p = _build(f"{OWNER_TAG}A", box_inside=True)
    sess = _make_session(p)
    plane = p.cube.session.plane

    # A0 setup truth: the wall exists in the plane's own authority.
    check("A0 wall is real in plane authority",
          list(plane.enhance_scope("in_a")) == ["in_b"],
          f"enhance_scope(in_a)={plane.enhance_scope('in_a')}")

    # (a) synthesize across the wall: refused, receipted, no landing.
    n0 = len(p.nursery.proposals)
    r = sess.synthesize(["in_a", "out_a"])
    check("A1 synthesize cross-wall refused with explicit receipt",
          r.get("ok") is False
          and r.get("reason") == "cross_wall_parents"
          and set(r.get("parents") or []) == {"in_a", "out_a"}
          and not r.get("pid"),
          f"receipt={r}")
    check("A2 refused synthesize persisted nothing",
          len(p.nursery.proposals) == n0
          and len(_cross_wall_props(p)) == 0,
          f"proposals={len(p.nursery.proposals)} (was {n0}) "
          f"cross_wall={_cross_wall_props(p)}")

    # (b) relate across the wall: refused likewise.
    r = sess.relate("in_a", "out_c")
    check("A3 relate cross-wall refused, nursery unchanged",
          r.get("ok") is False
          and r.get("reason") == "cross_wall_parents"
          and set(r.get("parents") or []) == {"in_a", "out_c"}
          and len(p.nursery.proposals) == n0,
          f"receipt={r} proposals={len(p.nursery.proposals)}")

    # (c) relate_field on a boxed target: the pre-filter is
    # constrained to the target's wall — outside candidates are
    # never shown to the judge — and the landing is wall-clean.
    r = sess.relate_field("in_a")
    shown = _shown_ids(sess)
    check("A4 relate_field shows only same-wall candidates",
          shown == ["in_a", "in_b"],
          f"shown={shown} (wall-blind BEFORE: in_a, in_b, out_a, out_b)")
    prop = p.nursery.proposals.get(r.get("pid", "")) if r.get("ok") else None
    check("A5 relate_field lands wall-clean PENDING",
          r.get("ok") is True and prop is not None
          and prop.status == "pending"
          and set(prop.parents or []) == {"in_a", "in_b"}
          and len(_cross_wall_props(p)) == 0,
          f"receipt ok={r.get('ok')} pid={r.get('pid')} "
          f"parents={list(prop.parents or []) if prop else None}")

    # (c, mirror) relate_field on an unboxed target: boxed entries
    # are across its wall and are never shown either.
    r = sess.relate_field("out_b")
    shown = _shown_ids(sess)
    prop = p.nursery.proposals.get(r.get("pid", "")) if r.get("ok") else None
    check("A6 relate_field unboxed target: boxed never shown, lands clean",
          shown == ["out_b", "out_a"]
          and r.get("ok") is True and prop is not None
          and set(prop.parents or []) == {"out_a", "out_b"},
          f"shown={shown} ok={r.get('ok')} "
          f"parents={list(prop.parents or []) if prop else None}")

    # (d) same-wall synthesize still lands PENDING, as before.
    n0 = len(p.nursery.proposals)
    r = sess.synthesize(["in_a", "in_b"])
    prop = p.nursery.proposals.get(r.get("pid", "")) if r.get("ok") else None
    check("A7 same-wall synthesize lands PENDING",
          r.get("ok") is True and prop is not None
          and prop.status == "pending"
          and set(prop.parents or []) == {"in_a", "in_b"}
          and len(p.nursery.proposals) == n0 + 1,
          f"receipt={r}")

    # (e) both-unboxed synthesize still lands.
    r = sess.synthesize(["out_a", "out_b"])
    prop = p.nursery.proposals.get(r.get("pid", "")) if r.get("ok") else None
    check("A8 both-unboxed synthesize lands PENDING",
          r.get("ok") is True and prop is not None
          and prop.status == "pending"
          and set(prop.parents or []) == {"out_a", "out_b"},
          f"receipt={r}")

    # relate's positive side, same wall.
    r = sess.relate("in_a", "in_b")
    prop = p.nursery.proposals.get(r.get("pid", "")) if r.get("ok") else None
    check("A9 same-wall relate lands PENDING",
          r.get("ok") is True and prop is not None
          and prop.status == "pending"
          and set(prop.parents or []) == {"in_a", "in_b"},
          f"receipt={r}")

    # --- Build F: malformed box claims refuse fail-closed ---------
    # The malformed states are constructed by direct field
    # assignment — the same states a verbatim save restore can
    # produce (persist_rest restores sandboxed/sandbox_id
    # unvalidated; GS-4 suite run F). A malformed claim must never
    # be collapsed to unboxed (None == None fail-open).
    pf = _build(f"{OWNER_TAG}F", box_inside=False)
    planf = pf.cube.session.plane
    pf.place("malf", "harbor lantern malformed",
             words="harbor lantern craft timber copper kettle song "
                   "malformed cellar vault", x=0.0, y=0.0)
    pf.place("ok_b", "harbor lantern okpeer",
             words="harbor lantern craft timber copper kettle song "
                   "okpeer cellar vault", x=0.0, y=0.0)
    um = planf.units["malf"]
    um.sandboxed = True
    um.sandbox_id = None
    sessf = _make_session(pf)
    nf0 = len(pf.nursery.proposals)
    r = sessf.synthesize(["malf", "ok_b"])
    check("F1 malformed (id absent) synthesize refused fail-closed",
          r.get("ok") is False
          and r.get("reason") == "malformed_wall_claim"
          and "malf" in (r.get("malformed") or [])
          and len(pf.nursery.proposals) == nf0,
          f"receipt={r} proposals={len(pf.nursery.proposals)}")
    r = sessf.relate("malf", "ok_b")
    check("F2 malformed (id absent) relate refused fail-closed",
          r.get("ok") is False
          and r.get("reason") == "malformed_wall_claim"
          and len(pf.nursery.proposals) == nf0,
          f"receipt={r} proposals={len(pf.nursery.proposals)}")

    # Ghost variant: sandbox_id names no Sandbox record.
    pg = _build(f"{OWNER_TAG}F3", box_inside=False)
    plang = pg.cube.session.plane
    pg.place("ghost", "harbor lantern ghostbox",
             words="harbor lantern craft timber copper kettle song "
                   "ghostbox cellar vault", x=0.0, y=0.0)
    pg.place("ok_b", "harbor lantern okpeer",
             words="harbor lantern craft timber copper kettle song "
                   "okpeer cellar vault", x=0.0, y=0.0)
    ug = plang.units["ghost"]
    ug.sandboxed = True
    ug.sandbox_id = "no_such_box"
    sessg = _make_session(pg)
    ng0 = len(pg.nursery.proposals)
    r = sessg.synthesize(["ghost", "ok_b"])
    check("F3 malformed (unknown sandbox_id) refused fail-closed",
          r.get("ok") is False
          and r.get("reason") == "malformed_wall_claim"
          and "ghost" in (r.get("malformed") or [])
          and len(pg.nursery.proposals) == ng0,
          f"receipt={r} proposals={len(pg.nursery.proposals)}")

    # --- Build G (control): the growth path still lands -----------
    pgm = _build(f"{OWNER_TAG}G", box_inside=True)
    sessgm = _make_session(pgm)
    res = pgm.grow_ideas(1, session=sessgm)
    steps = res.get("steps") or [{}]
    docked_pairs = {(d.get("a"), d.get("b"))
                    for d in (res.get("docked_pairs") or [])}
    docked_landed = all(
        (pgm.nursery.proposals.get(d.get("pid")) is not None
         and pgm.nursery.proposals[d["pid"]].status == "pending")
        for d in (res.get("docked_pairs") or []))
    check("G1 growth-path docked pairs still land PENDING",
          res.get("growth_mode") == "docked"
          and docked_pairs == {("in_a", "in_b"), ("out_a", "out_b")}
          and docked_landed
          and len(_cross_wall_props(pgm)) == 0,
          f"growth_mode={res.get('growth_mode')} "
          f"docked_pairs={sorted(docked_pairs)} "
          f"docked_new={res.get('docked_new')} "
          f"cross_wall={_cross_wall_props(pgm)}")
    check("G2 GS-4 wall filter receipts intact on the growth path",
          steps[0].get("pairs_excluded_cross_sandbox") == 6
          and res.get("pairs_excluded_cross_sandbox") == 6,
          f"step={steps[0].get('pairs_excluded_cross_sandbox')} "
          f"total={res.get('pairs_excluded_cross_sandbox')} (6 expected)")

    total = 15
    print(f"DOCK WALL: {total - len(fails)}/{total} checks passed"
          + (f"; FAILING: {fails}" if fails else ""))
    for owner in ("A", "F", "F3", "G"):
        _cleanup(f"{OWNER_TAG}{owner}")
    return not fails


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
