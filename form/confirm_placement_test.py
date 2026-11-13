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

Build lane (2026-11-13): registered in form/regress.py LIST after
form.dock_wall_test. T15-T18 added by the build lane per DESIGN.md
SS9 proof plan: T15 = P2 checkpoint rollback across a boxed confirm;
T16 = P3 mid-write revocation compensation cleanliness (via the
confirm_lineage._BETWEEN_STAGES hook); T17 = P4 intent-journal
recovery consistency; T18 = P5 generation-race loser cleanliness.
(P1 = the T1/T7 save/reload arms above.) Expected: 18/18.

Repair lane (2026-11-13, Director mail 1a1d5f2f58738b15 — design
ambiguity A1 decided: NO silent adoption of a pre-existing
auto_staging record): T19 = staging-id collision refuses
fail-closed with positive identity validation (exact reserved
label); T20 = stage/restore validation (staged membership + label
survive save/reload; release via Plane.unbox and re-box works
after reload); T21 = forced PARTIAL Plane.box mutation (record
side mutated, unit side untouched, then raise) still compensates
cleanly — no dangling member_ids, no placed unit, proposal
preserved and retryable; T22 = the collision refusal on the real
sweep path is an explicit counted failure (never a silent skip)
and the preserved proposal still confirms manually afterwards.
Expected: 22/22.

Gate-2 lane (2026-11-13, Director mail 1a1d6d1d64b72589): the
Director ruled label equality alone is not unforgeable
provenance. Provenance contract: staging ownership is verified
by TWO durable facts on the canonical Sandbox record — the exact
reserved label AND a provenance marker (STAGING_PROVENANCE)
that Plane.box stamps only at record creation and never
rewrites, that only the staging writer passes, and that the
persist pair round-trips verbatim. A record missing either fact
(foreign same-label record, pre-provenance save, pack import)
fails closed for staging use. Residual, disclosed: hand-edited
save files can forge the marker — the same disclosed class as
F-d malformed claims; no claim is made against out-of-band file
editing. T23 = same-label foreign box refuses the direct
grow_auto confirm with zero mutation; T24 = the sweep counts it
as an explicit failure and the refusal survives save/load;
T25 = positive control — the program's own staging box carries
the marker live and after reload, stages again after reload,
and release via unbox + re-box still works. Failing-first at
49e2e64: T23/T24 FAIL (the same-label foreign box was ADOPTED —
proposals confirmed into it); T25 cannot import the marker.
Expected: 25/25.

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


# ------------------------------------------------- proof plan (DESIGN §9)
def t15():
    """P2: checkpoint rollback to the generation before a boxed
    confirm — the child is absent AND no box member_ids reference
    it; the pre-confirm generation restores exactly."""
    owner = "CPQ3T15"
    p = build(owner)
    pid_a = seed(p, "t15 anchor", "harbor lantern t15a", [])
    manual_confirm(p, pid_a)
    from form.mandell.checkpoint_generation import \
        committed_generation_state
    g_a = committed_generation_state(owner)[1]
    pid_b = seed(p, "t15 boxed child", "harbor lantern t15b",
                 ["in_a", "in_b"])
    res_b = manual_confirm(p, pid_b)
    from form.dell_matrix import rollback_authority as ra
    frozen = ra.freeze_rollback_target(owner, g_a)
    data = ra.rollback_content(frozen, ra._live_fingerprints(owner))
    issued = p.acceptance_policy.issue_approval(
        operation=ra.ROLLBACK_OPERATION, target=g_a, reviewer="human",
        data=data, note="confirm-placement P2 proof")
    rr = p.confirm_rollback(
        g_a,
        _review_context={"approval_id": issued["context"]["approval_id"]},
        _subject="human", _producer="repl-human")
    rw_b, boxes = reloaded_wall(owner, pid_b)
    rw_a, _ = reloaded_wall(owner, pid_a)
    ok = (res_b.get("ok") and rr.get("ok") and rw_b is None
          and pid_b not in boxes.get("vault1", [])
          and boxes.get("vault1") == ["in_a", "in_b"]
          and rw_a is not None and not rw_a["sandboxed"])
    check("T15 P2 rollback across boxed confirm restores exactly", ok,
          f"rollback_ok={rr.get('ok')} child={rw_b} "
          f"vault1={boxes.get('vault1')} anchor={rw_a}")
    cleanup(owner)


def t16():
    """P3: mid-write revocation (reviewed content mutated between
    stages via the _BETWEEN_STAGES hook) denies a BOXED confirm at
    pre_commit; compensation leaves no unit and NO dangling
    member_ids entry — live or reloaded."""
    owner = "CPQ3T16"
    p = build(owner)
    pid = seed(p, "t16 boxed child", "harbor lantern t16",
               ["in_a", "in_b"])
    from form.dell_matrix import confirm_lineage

    def hook(program, _pid, _auth):
        program.nursery.proposals[_pid].words = "mutated mid-write"

    confirm_lineage._BETWEEN_STAGES = hook
    try:
        res = manual_confirm(p, pid)
    finally:
        confirm_lineage._BETWEEN_STAGES = None
    rw, boxes = reloaded_wall(owner, pid)
    ok = (not res.get("ok") and res.get("stage") == "pre_commit"
          and status_of(p, pid) == "pending"
          and wall_of(p, pid) is None
          and pid not in (members(p, "vault1") or [])
          and rw is None and pid not in boxes.get("vault1", []))
    check("T16 P3 revocation compensation leaves no dangling member",
          ok, f"res={ {k: res.get(k) for k in ('ok', 'reason', 'stage')} } "
              f"live_members={members(p, 'vault1')} reloaded={rw} "
              f"reloaded_members={boxes.get('vault1')}")
    cleanup(owner)


def t17():
    """P4: intent-journal recovery treats a boxed confirm
    consistently — recovery runs without raising, mutates nothing
    (child stays boxed, membership intact), and clears the journal."""
    owner = "CPQ3T17"
    p = build(owner)
    pid = seed(p, "t17 boxed child", "harbor lantern t17",
               ["in_a", "in_b"])
    res = manual_confirm(p, pid)
    from form.mandell.core_i_recovery import write_confirm_intent, \
        recover_confirmation_intent
    write_confirm_intent(owner, pid)
    outcome = recover_confirmation_intent(owner)
    rw, boxes = reloaded_wall(owner, pid)
    again = recover_confirmation_intent(owner)
    ok = (res.get("ok")
          and outcome in ("already_complete", "no_change")
          and rw and rw["sandboxed"] and rw["sandbox_id"] == "vault1"
          and pid in boxes.get("vault1", [])
          and again == "none")
    check("T17 P4 intent-journal recovery consistent for boxed confirm",
          ok, f"outcome={outcome} again={again} wall={rw}")
    cleanup(owner)


def t18():
    """P5: generation race — two live instances confirm the same
    boxed proposal; the loser is refused (nursery_conflict) and the
    durable state holds the child exactly once, boxed, with exactly
    one membership entry (the winner's placement intact)."""
    owner = "CPQ3T18"
    p1 = build(owner)
    pid = seed(p1, "t18 race child", "harbor lantern t18",
               ["in_a", "in_b"])
    p1.save()
    p1.nursery.save()
    from form.open import Program
    p2 = Program.load(owner)
    r1 = p1.confirm_proposal(
        pid, _producer="repl_user",
        _review_context=p1.make_review_context(pid, "repl_user"))
    r2 = p2.confirm_proposal(
        pid, _producer="repl_user",
        _review_context=p2.make_review_context(pid, "repl_user"))
    rw, boxes = reloaded_wall(owner, pid)
    ok = (r1.get("ok") and not r2.get("ok")
          and rw and rw["sandboxed"] and rw["sandbox_id"] == "vault1"
          and (boxes.get("vault1") or []).count(pid) == 1)
    check("T18 P5 race loser clean, winner placement intact", ok,
          f"winner={r1.get('ok')} loser_reason={r2.get('reason')} "
          f"wall={rw} members={boxes.get('vault1')}")
    cleanup(owner)


# --------------------------------- A1 repair (Director 2026-11-13)
def _user_staging_box(p):
    """A pre-existing USER-owned box carrying the staging id: the
    user's own label, holding the user's own unit. Built through
    the same Plane.box writer a user surface uses."""
    p.place("user_gem", "my private gem", words="private keepsake",
            x=0.0, y=0.0)
    p.cube.session.plane.box(["user_gem"], "auto_staging",
                             label="My private vault")


def t19():
    owner = "CPQ3T19"
    p = build(owner)
    _user_staging_box(p)
    pid = seed(p, "t19 unboxed parents cross", "harbor lantern t19",
               ["out_a", "out_b"])
    p.set_auto_confirm_grow(True)
    res = p.confirm_proposal(pid, _producer="grow_auto")
    plane = p.cube.session.plane
    sb = plane.sandboxes.get("auto_staging")
    ok = (not res.get("ok")
          and res.get("reason") == "staging_box_conflict"
          and res.get("sandbox_id") == "auto_staging"
          and res.get("existing_label") == "My private vault"
          and status_of(p, pid) == "pending"
          and wall_of(p, pid) is None
          and sb is not None and sb.label == "My private vault"
          and list(sb.member_ids) == ["user_gem"])
    check("T19 staging-id collision refuses (no silent adoption)", ok,
          f"res={ {k: res.get(k) for k in ('ok', 'reason', 'sandbox_id', 'existing_label')} } "
          f"status={status_of(p, pid)} unit={wall_of(p, pid)} "
          f"box_label={sb.label if sb else None} "
          f"box_members={list(sb.member_ids) if sb else None}")
    cleanup(owner)


def t20():
    owner = "CPQ3T20"
    p = build(owner)
    pid = seed(p, "t20 staged child", "harbor lantern t20",
               ["out_a", "out_b"])
    sweep(p)
    from form.dell_matrix.confirm_lineage import STAGING_BOX_LABEL
    live_sb = p.cube.session.plane.sandboxes.get("auto_staging")
    rw, boxes = reloaded_wall(owner, pid)
    from form.open import Program
    p2 = Program.load(owner)
    sb2 = p2.cube.session.plane.sandboxes.get("auto_staging")
    intact = (rw and rw["sandboxed"]
              and rw["sandbox_id"] == "auto_staging"
              and pid in boxes.get("auto_staging", [])
              and live_sb is not None
              and live_sb.label == STAGING_BOX_LABEL
              and sb2 is not None and sb2.label == STAGING_BOX_LABEL)
    # Release via the existing machinery AFTER reload, then re-box.
    rel = p2.cube.session.plane.unbox(pid)
    w_after = wall_of(p2, pid)
    p2.cube.session.plane.box([pid], "vault1")
    ok = (status_of(p, pid) == "confirmed" and intact and rel
          and w_after and not w_after["sandboxed"]
          and w_after["sandbox_id"] is None
          and pid not in (members(p2, "auto_staging") or [])
          and pid in (members(p2, "vault1") or []))
    check("T20 staged unit survives reload; release + re-box work",
          ok, f"status={status_of(p, pid)} reloaded={rw} "
              f"reloaded_members={boxes.get('auto_staging')} "
              f"label_ok={sb2 is not None and sb2.label == STAGING_BOX_LABEL} "
              f"released={rel} after={w_after}")
    cleanup(owner)


def t21():
    """Forced PARTIAL Plane.box mutation: the record side is
    mutated (child appended to member_ids) and box() raises BEFORE
    the unit side is touched. Compensation must still leave no
    dangling member_ids and no placed unit — live or reloaded —
    and the proposal must stay pending and retryable."""
    owner = "CPQ3T21"
    p = build(owner)
    pid = seed(p, "t21 boxed child", "harbor lantern t21",
               ["in_a", "in_b"])
    from form.dell_matrix.plane import Plane, Sandbox
    orig_box = Plane.box

    def partial_box(self, unit_ids, sandbox_id="box1", label=None,
                    **kw):
        sb = self.sandboxes.get(sandbox_id) or Sandbox(id=sandbox_id)
        if label is not None:
            sb.label = label
        for uid in unit_ids:
            if uid not in sb.member_ids:
                sb.member_ids.append(uid)
        self.sandboxes[sandbox_id] = sb
        raise RuntimeError("forced partial box fault (suite)")

    Plane.box = partial_box
    raised = None
    try:
        manual_confirm(p, pid)
    except RuntimeError as e:
        raised = e
    finally:
        Plane.box = orig_box
    plane = p.cube.session.plane
    dangling = [sid for sid, sb in plane.sandboxes.items()
                if pid in sb.member_ids]
    rw, boxes = reloaded_wall(owner, pid)
    reloaded_dangling = [sid for sid, ms in boxes.items()
                         if pid in ms]
    clean = (raised is not None
             and getattr(raised, "_compensation_incomplete",
                         None) is None
             and status_of(p, pid) == "pending"
             and wall_of(p, pid) is None
             and not dangling and not reloaded_dangling
             and rw is None)
    # Preservation is functional: with the fault removed the same
    # proposal confirms cleanly into the parents' wall.
    res2 = manual_confirm(p, pid)
    ok = (clean and res2.get("ok")
          and pid in (members(p, "vault1") or []))
    check("T21 partial box() mutation compensates fully + retry", ok,
          f"raised={type(raised).__name__ if raised else None} "
          f"dangling={dangling} reloaded_dangling={reloaded_dangling} "
          f"status={status_of(p, pid)} retry_ok={res2.get('ok')}")
    cleanup(owner)


def t22():
    owner = "CPQ3T22"
    p = build(owner)
    _user_staging_box(p)
    pid = seed(p, "t22 unboxed parents cross", "harbor lantern t22",
               ["out_a", "out_b"])
    res = sweep(p)
    ac = res.get("auto_confirm") or {}
    plane = p.cube.session.plane
    sb = plane.sandboxes.get("auto_staging")
    preserved = (status_of(p, pid) == "pending"
                 and wall_of(p, pid) is None
                 and pid not in (ac.get("skipped_ids") or [])
                 and int(ac.get("failed", 0)) >= 1
                 and sb is not None and sb.label == "My private vault"
                 and pid not in list(sb.member_ids))
    # Preservation is functional: the same proposal still confirms
    # manually afterwards (D6: unboxed parents, manual -> unboxed).
    res2 = manual_confirm(p, pid)
    w2 = wall_of(p, pid)
    ok = (preserved and res2.get("ok") and w2
          and not w2["sandboxed"] and w2["sandbox_id"] is None)
    check("T22 sweep collision = explicit failure; proposal preserved",
          ok, f"auto_confirm={ac} status_after_sweep=pending "
              f"manual_retry_ok={res2.get('ok')} wall={w2}")
    cleanup(owner)


# ----------------------- gate-2 (Director mail 1a1d6d1d64b72589)
def _foreign_staging_box(p):
    """A FOREIGN box carrying BOTH the staging id and the EXACT
    reserved label, created through the same Plane.box writer a
    user surface uses — but NOT by the staging writer, so it
    carries no program provenance. Holding the user's own unit.
    Gate-2 (Director 2026-11-13 15:30 CST): label equality alone
    is not unforgeable provenance; this box must never be
    adopted as the program's staging box."""
    from form.dell_matrix.confirm_lineage import STAGING_BOX_LABEL
    p.place("user_gem", "my private gem", words="private keepsake",
            x=0.0, y=0.0)
    p.cube.session.plane.box(["user_gem"], "auto_staging",
                             label=STAGING_BOX_LABEL)


def t23():
    owner = "CPQ3T23"
    p = build(owner)
    _foreign_staging_box(p)
    pid = seed(p, "t23 unboxed parents cross", "harbor lantern t23",
               ["out_a", "out_b"])
    p.set_auto_confirm_grow(True)
    res = p.confirm_proposal(pid, _producer="grow_auto")
    plane = p.cube.session.plane
    sb = plane.sandboxes.get("auto_staging")
    ok = (not res.get("ok")
          and res.get("reason") == "staging_box_conflict"
          and status_of(p, pid) == "pending"
          and wall_of(p, pid) is None
          and sb is not None
          and list(sb.member_ids) == ["user_gem"])
    check("T23 same-label foreign box refuses direct auto confirm "
          "(label is not provenance)", ok,
          f"res={ {k: res.get(k) for k in ('ok', 'reason')} } "
          f"status={status_of(p, pid)} unit={wall_of(p, pid)} "
          f"box_members={list(sb.member_ids) if sb else None}")
    cleanup(owner)


def t24():
    owner = "CPQ3T24"
    p = build(owner)
    _foreign_staging_box(p)
    pid = seed(p, "t24 unboxed parents cross", "harbor lantern t24",
               ["out_a", "out_b"])
    res = sweep(p)
    ac = res.get("auto_confirm") or {}
    plane = p.cube.session.plane
    sb = plane.sandboxes.get("auto_staging")
    sweep_refused = (status_of(p, pid) == "pending"
                     and wall_of(p, pid) is None
                     and pid not in (ac.get("skipped_ids") or [])
                     and int(ac.get("failed", 0)) >= 1
                     and sb is not None
                     and pid not in list(sb.member_ids)
                     and "user_gem" in list(sb.member_ids))
    # The refusal is durable: after save/load the foreign box is
    # STILL foreign — a fresh proposal in the reloaded program is
    # refused the same way, and the user's membership is intact.
    from form.open import Program
    p2 = Program.load(owner)
    sb2 = p2.cube.session.plane.sandboxes.get("auto_staging")
    pid2 = seed(p2, "t24 post-reload cross", "harbor lantern t24b",
                ["out_a", "out_b"])
    p2.set_auto_confirm_grow(True)
    res2 = p2.confirm_proposal(pid2, _producer="grow_auto")
    reload_refused = (not res2.get("ok")
                      and res2.get("reason") == "staging_box_conflict"
                      and status_of(p2, pid2) == "pending"
                      and sb2 is not None
                      and list(sb2.member_ids) == ["user_gem"])
    ok = sweep_refused and reload_refused
    check("T24 same-label foreign box: sweep counted failure + "
          "refusal survives reload", ok,
          f"auto_confirm={ac} sweep_refused={sweep_refused} "
          f"reload_res={ {k: res2.get(k) for k in ('ok', 'reason')} } "
          f"reloaded_members={list(sb2.member_ids) if sb2 else None}")
    cleanup(owner)


def t25():
    """Positive control for the provenance invariant: the
    program's OWN staging box — created by the staging writer,
    carrying the reserved provenance marker — keeps working
    across save/load: a second auto confirm after reload stages
    into the SAME box, and release via unbox + re-box still
    works."""
    owner = "CPQ3T25"
    p = build(owner)
    pid = seed(p, "t25 staged child", "harbor lantern t25",
               ["out_a", "out_b"])
    sweep(p)
    from form.dell_matrix.confirm_lineage import (
        STAGING_BOX_LABEL, STAGING_PROVENANCE)
    sb = p.cube.session.plane.sandboxes.get("auto_staging")
    marked_live = (sb is not None
                   and sb.label == STAGING_BOX_LABEL
                   and getattr(sb, "provenance", None)
                   == STAGING_PROVENANCE)
    from form.open import Program
    p2 = Program.load(owner)
    sb2 = p2.cube.session.plane.sandboxes.get("auto_staging")
    marked_reloaded = (sb2 is not None
                       and sb2.label == STAGING_BOX_LABEL
                       and getattr(sb2, "provenance", None)
                       == STAGING_PROVENANCE
                       and pid in list(sb2.member_ids))
    pid2 = seed(p2, "t25 second staged child", "harbor lantern t25b",
                ["out_a", "out_c"])
    res2 = sweep(p2)
    w2 = wall_of(p2, pid2)
    staged_again = (status_of(p2, pid2) == "confirmed" and w2
                    and w2["sandboxed"]
                    and w2["sandbox_id"] == "auto_staging"
                    and pid2 in (members(p2, "auto_staging") or []))
    rel = p2.cube.session.plane.unbox(pid)
    w_after = wall_of(p2, pid)
    p2.cube.session.plane.box([pid], "vault1")
    released = (rel and w_after and not w_after["sandboxed"]
                and pid not in (members(p2, "auto_staging") or [])
                and pid in (members(p2, "vault1") or []))
    ok = (marked_live and marked_reloaded and staged_again
          and released)
    check("T25 own staging box: provenance marker durable, reuse "
          "after reload, release + re-box work", ok,
          f"marked_live={marked_live} marked_reloaded="
          f"{marked_reloaded} staged_again={staged_again} "
          f"released={released} sweep2={res2.get('auto_confirm')}")
    cleanup(owner)


def smoke() -> bool:
    RESULTS.clear()
    for fn in (t1, t2, t3, t4, t5, t6, t7, t8, t9, t10,
               t11, t12, t13, t14, t15, t16, t17, t18,
               t19, t20, t21, t22, t23, t24, t25):
        try:
            fn()
        except Exception as e:
            check(fn.__name__.upper(), False,
                  f"EXCEPTION {type(e).__name__}: {e}")
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"CONFIRM_PLACEMENT: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS) and len(RESULTS) == 25


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
