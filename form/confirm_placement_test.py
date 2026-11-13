#!/usr/bin/env python3
"""Confirm-placement suite — FAILING-FIRST (design lane, 2026-11-13).

Contract: DESIGN.md in hidden_files/confirm_place/ (Q-U.3 + Q-U.4 +
Q-U.5 + AUTO => SANDBOX FIRST, Ace/Director rulings 2026-11-13).

The shared confirm writer (form/dell_matrix/confirm_lineage.py) places
every confirmed proposal with NO sandbox arguments — placement is
wall-blind by construction at the base this suite was written against
(main 1b52179b). Expected at base: 2/14 (only the two controls T9/T10
pass — behavior that is already correct and must not regress).
Expected after the DESIGN.md build: 14/14.

NOT registered in form/regress.py LIST by this lane (design-lane
deliverable; the build lane registers it).

Field (same GS-4 / U-probe field, so results are falsifiable against
the published probe logs):
  in_a, in_b   boxed into sandbox 'vault1'
  out_a        outside near-twin of in_a
  out_b        outside, moderate overlap
  out_c        outside, distant tokens
Manual confirms use the exact REPL call (form/repl.py:2849ff):
confirm_proposal(pid, _producer="repl_user",
                 _review_context=make_review_context(pid, "repl_user")).
Auto confirms use the real sweep: set_auto_confirm_grow(True) then
grow_ideas(1); assertions target the seeded proposal's pid (the sweep
also processes growth's own proposals, by design).
"""
from __future__ import annotations

import glob
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")

INSIDE = ["in_a", "in_b"]
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

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"CHECK {name}: {'PASS' if ok else 'FAIL'} — {detail}", flush=True)
    return bool(ok)


def cleanup(owner):
    # Standing rule: cleanup errors FAIL LOUDLY, never swallowed.
    for f in glob.glob(os.path.join(STATE_DIR, f"*{owner}*")):
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)


def build(owner):
    from form.open import open_program
    cleanup(owner)
    p = open_program(owner)
    plane = p.cube.session.plane
    plane.units.clear()
    plane.sandboxes.clear()
    p.nursery.proposals.clear()
    for uid, label, words in FIELD:
        p.place(uid, label, words=words, x=0.0, y=0.0)
    plane.box(list(INSIDE), "vault1", label="gs4 vault")
    return p


def seed(p, label, words, parents):
    prop = p.nursery.add(label=label, words=words, kind="new",
                         parents=list(parents), origin="suite:seeded",
                         reason="confirm-placement suite")
    return prop.id


def manual_confirm(p, pid, **kw):
    return p.confirm_proposal(
        pid, _producer="repl_user",
        _review_context=p.make_review_context(pid, "repl_user"), **kw)


def wall_of(p, uid):
    u = p.cube.session.plane.units.get(uid)
    if u is None:
        return None
    return {"sandboxed": bool(u.sandboxed), "sandbox_id": u.sandbox_id}


def members(p, sid):
    sb = p.cube.session.plane.sandboxes.get(sid)
    return list(sb.member_ids) if sb else None


def reloaded_wall(owner, uid):
    from form.open import Program
    p2 = Program.load(owner)
    return wall_of(p2, uid), {sid: list(sb.member_ids)
                              for sid, sb in
                              p2.cube.session.plane.sandboxes.items()}


def status_of(p, pid):
    prop = p.nursery.proposals.get(pid)
    return getattr(prop, "status", None)


def sweep(p):
    p.set_auto_confirm_grow(True)
    return p.grow_ideas(1)


# ---------------------------------------------------------------- T1
def t1():
    owner = "CPQ3T01"
    p = build(owner)
    pid = seed(p, "t1 both boxed cross", "harbor lantern t1 seeded",
               ["in_a", "in_b"])
    res = manual_confirm(p, pid)
    w = wall_of(p, pid)
    rw, boxes = reloaded_wall(owner, pid)
    ok = (res.get("ok") and w and w["sandboxed"]
          and w["sandbox_id"] == "vault1"
          and pid in (members(p, "vault1") or [])
          and rw == w and pid in boxes.get("vault1", []))
    check("T1 same-wall manual inherits wall + membership + reload", ok,
          f"res_ok={res.get('ok')} wall={w} members={members(p, 'vault1')} "
          f"reloaded={rw}")
    cleanup(owner)


def t2():
    owner = "CPQ3T02"
    p = build(owner)
    pid = seed(p, "t2 both boxed cross", "harbor lantern t2 seeded",
               ["in_a", "in_b"])
    sweep(p)
    w = wall_of(p, pid)
    ok = (status_of(p, pid) == "confirmed" and w and w["sandboxed"]
          and w["sandbox_id"] == "vault1"
          and pid in (members(p, "vault1") or []))
    check("T2 same-wall auto (sweep) inherits parents' wall", ok,
          f"status={status_of(p, pid)} wall={w} "
          f"members={members(p, 'vault1')}")
    cleanup(owner)


def t3():
    owner = "CPQ3T03"
    p = build(owner)
    pid = seed(p, "t3 single boxed parent", "harbor lantern t3 seeded",
               ["in_a"])
    res = manual_confirm(p, pid)
    w = wall_of(p, pid)
    ok = (res.get("ok") and w and w["sandboxed"]
          and w["sandbox_id"] == "vault1"
          and pid in (members(p, "vault1") or []))
    check("T3 single boxed parent manual inherits wall", ok,
          f"res_ok={res.get('ok')} wall={w}")
    cleanup(owner)


def t4():
    owner = "CPQ3T04"
    p = build(owner)
    pid = seed(p, "t4 mixed wall cross", "harbor lantern t4 seeded",
               ["in_a", "out_a"])
    res = manual_confirm(p, pid)
    opts = res.get("options") or []
    opt_ids = sorted(str(o.get("sandbox_id")) for o in opts
                     if isinstance(o, dict) and o.get("sandbox_id"))
    has_outside = any(isinstance(o, dict) and o.get("outside")
                      for o in opts)
    ok = (not res.get("ok")
          and res.get("reason") == "placement_choice_required"
          and opt_ids == ["vault1"] and has_outside
          and status_of(p, pid) == "pending"
          and wall_of(p, pid) is None)
    check("T4 mixed manual without choice asks (no silent placement)", ok,
          f"res={ {k: res.get(k) for k in ('ok', 'reason')} } "
          f"options={opts} status={status_of(p, pid)} "
          f"unit={wall_of(p, pid)}")
    cleanup(owner)


def t5():
    owner = "CPQ3T05"
    p = build(owner)
    pid1 = seed(p, "t5 mixed choice wall", "harbor lantern t5a seeded",
                ["in_a", "out_a"])
    pid2 = seed(p, "t5 mixed choice outside", "harbor lantern t5b seeded",
                ["in_b", "out_b"])
    try:
        res1 = manual_confirm(p, pid1, _placement="vault1")
        res2 = manual_confirm(p, pid2, _placement="outside")
    except TypeError as e:
        check("T5 mixed manual with choice places per choice + receipt",
              False, f"TypeError (no _placement surface at base): {e}")
        cleanup(owner)
        return
    w1, w2 = wall_of(p, pid1), wall_of(p, pid2)
    pl1 = (res1.get("placement") or {})
    pl2 = (res2.get("placement") or {})
    ok = (res1.get("ok") and w1 and w1["sandbox_id"] == "vault1"
          and pid1 in (members(p, "vault1") or [])
          and pl1.get("mode") == "manual_choice"
          and pl1.get("choice") == "vault1"
          and res2.get("ok") and w2 and not w2["sandboxed"]
          and pl2.get("mode") == "manual_choice"
          and pl2.get("choice") == "outside")
    check("T5 mixed manual with choice places per choice + receipt", ok,
          f"w1={w1} pl1={pl1} w2={w2} pl2={pl2}")
    cleanup(owner)


def t6():
    owner = "CPQ3T06"
    p = build(owner)
    pid = seed(p, "t6 mixed wall cross", "harbor lantern t6 seeded",
               ["in_a", "out_a"])
    res = sweep(p)
    ac = res.get("auto_confirm") or {}
    skipped = ac.get("skipped_ids") or []
    ok = (status_of(p, pid) == "pending" and wall_of(p, pid) is None
          and pid in skipped
          and int(ac.get("skipped_noneligible", 0)) >= 1)
    check("T6 mixed auto (sweep) skipped non-eligible + receipt", ok,
          f"status={status_of(p, pid)} unit={wall_of(p, pid)} "
          f"auto_confirm={ac}")
    cleanup(owner)


def t7():
    owner = "CPQ3T07"
    p = build(owner)
    pid = seed(p, "t7 unboxed parents cross", "harbor lantern t7 seeded",
               ["out_a", "out_b"])
    sweep(p)
    w = wall_of(p, pid)
    rw, boxes = reloaded_wall(owner, pid)
    ok = (status_of(p, pid) == "confirmed" and w and w["sandboxed"]
          and w["sandbox_id"] == "auto_staging"
          and pid in (members(p, "auto_staging") or [])
          and rw == w and pid in boxes.get("auto_staging", []))
    check("T7 unboxed-parents auto lands in staging box (+reload)", ok,
          f"status={status_of(p, pid)} wall={w} reloaded={rw}")
    cleanup(owner)


def t8():
    owner = "CPQ3T08"
    p = build(owner)
    pid = seed(p, "t8 parentless proposal", "harbor lantern t8 seeded", [])
    sweep(p)
    w = wall_of(p, pid)
    ok = (status_of(p, pid) == "confirmed" and w and w["sandboxed"]
          and w["sandbox_id"] == "auto_staging"
          and pid in (members(p, "auto_staging") or []))
    check("T8 parentless auto lands in staging box", ok,
          f"status={status_of(p, pid)} wall={w}")
    cleanup(owner)


def t9():
    owner = "CPQ3T09"
    p = build(owner)
    pid = seed(p, "t9 unboxed parents cross", "harbor lantern t9 seeded",
               ["out_a", "out_b"])
    res = manual_confirm(p, pid)
    w = wall_of(p, pid)
    ok = res.get("ok") and w and not w["sandboxed"] and w["sandbox_id"] is None
    check("T9 CONTROL unboxed-parents manual lands unboxed", ok,
          f"res_ok={res.get('ok')} wall={w}")
    cleanup(owner)


def t10():
    owner = "CPQ3T10"
    p = build(owner)
    pid = seed(p, "t10 parentless proposal", "harbor lantern t10 seeded", [])
    res = manual_confirm(p, pid)
    w = wall_of(p, pid)
    ok = res.get("ok") and w and not w["sandboxed"]
    check("T10 CONTROL parentless manual lands unboxed", ok,
          f"res_ok={res.get('ok')} wall={w}")
    cleanup(owner)


def _bad_unit(p, uid):
    p.place(uid, f"{uid} crafted parent", words="harbor lantern crafted",
            x=0.0, y=0.0)
    return p.cube.session.plane.units[uid]


def t11():
    owner = "CPQ3T11"
    p = build(owner)
    bad = _bad_unit(p, "bad_a")
    bad.sandboxed = True
    bad.sandbox_id = "ghost_box"  # names no Sandbox record -> malformed
    pid = seed(p, "t11 malformed parent child", "harbor lantern t11",
               ["bad_a", "out_b"])
    res = manual_confirm(p, pid)
    ok = (not res.get("ok")
          and res.get("reason") == "malformed_wall_claim"
          and res.get("culprit") == "bad_a"
          and status_of(p, pid) == "pending"
          and wall_of(p, pid) is None)
    check("T11 malformed parent (ghost box) manual refuses fail-closed",
          ok, f"res={ {k: res.get(k) for k in ('ok', 'reason', 'culprit')} } "
              f"status={status_of(p, pid)} unit={wall_of(p, pid)}")
    cleanup(owner)


def t12():
    owner = "CPQ3T12"
    p = build(owner)
    _bad_unit(p, "bad_b")
    plane = p.cube.session.plane
    plane.box(["bad_b"], "vaultX")
    plane.sandboxes["vaultX"].member_ids.remove("bad_b")  # claim/record split
    pid = seed(p, "t12 membership split child", "harbor lantern t12",
               ["bad_b", "in_b"])
    res = manual_confirm(p, pid)
    ok = (not res.get("ok")
          and res.get("reason") == "malformed_wall_claim"
          and status_of(p, pid) == "pending"
          and wall_of(p, pid) is None)
    check("T12 malformed parent (membership split) manual refuses", ok,
          f"res={ {k: res.get(k) for k in ('ok', 'reason', 'culprit')} } "
          f"status={status_of(p, pid)} unit={wall_of(p, pid)}")
    cleanup(owner)


def t13():
    owner = "CPQ3T13"
    p = build(owner)
    bad = _bad_unit(p, "bad_a")
    bad.sandboxed = True
    bad.sandbox_id = "ghost_box"
    pid = seed(p, "t13 malformed parent child", "harbor lantern t13",
               ["bad_a"])
    sweep(p)
    ok = status_of(p, pid) == "pending" and wall_of(p, pid) is None
    check("T13 malformed parent auto (sweep) never confirms", ok,
          f"status={status_of(p, pid)} unit={wall_of(p, pid)}")
    cleanup(owner)


def t14():
    owner = "CPQ3T14"
    p = build(owner)
    bad = _bad_unit(p, "bad_a")
    bad.sandboxed = True
    bad.sandbox_id = "ghost_box"
    pid = seed(p, "t14 malformed mixed child", "harbor lantern t14",
               ["bad_a", "in_a"])
    try:
        res = manual_confirm(p, pid, _placement="vault1")
    except TypeError as e:
        check("T14 choice cannot launder a malformed claim", False,
              f"TypeError (no _placement surface at base): {e}")
        cleanup(owner)
        return
    ok = (not res.get("ok")
          and res.get("reason") == "malformed_wall_claim"
          and status_of(p, pid) == "pending"
          and wall_of(p, pid) is None)
    check("T14 choice cannot launder a malformed claim", ok,
          f"res={ {k: res.get(k) for k in ('ok', 'reason', 'culprit')} } "
          f"status={status_of(p, pid)} unit={wall_of(p, pid)}")
    cleanup(owner)


def smoke() -> bool:
    RESULTS.clear()
    for fn in (t1, t2, t3, t4, t5, t6, t7, t8, t9, t10,
               t11, t12, t13, t14):
        try:
            fn()
        except Exception as e:
            check(fn.__name__.upper(), False,
                  f"EXCEPTION {type(e).__name__}: {e}")
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"CONFIRM_PLACEMENT: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS) and len(RESULTS) == 14


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
