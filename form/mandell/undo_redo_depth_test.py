#!/usr/bin/env python3
"""Q-LC.1 — undo/redo correction tests (Director EXE 6965138959 on PR #434;
plan: director-reports/QLC1_UNDO_REDO_CORRECTION_PLAN_2026-11-15.md §5).

Contract under test (session ACTION stack only — the snapshot stack is a
separate authority and must stay untouched):
  T1 default depth is exactly 30 (not the old bare literal 32)
  T2 depth is Ace-adjustable per owner, persists across save/load,
     refusals at 0 and above UNDO_DEPTH_MAX change nothing
  T3 drops at the bound are counted + displayed (no silent loss)
  T4 redo re-applies undone steps in original order, incl. full
     place-record restoration
  T5 a new action after undo invalidates the redo tail
  T6 redo tail is bounded by the same depth, far end drops first
  T7 refusal honesty: revision-owned undo refuses; redo onto a
     re-taken id refuses and mutates nothing; empty stacks answer
     their honest nothings
  T8 undo/redo walk state, never records (generation/outcomes stable)
  B  boundaries 0 / 30 / 31 at the working bound
  S  snapshot stack (Core II) compatibility: cap 64 + counted drops,
     fully independent of the action stack
  M  mixed place + edit_detail + edit_goals undo/redo round-trip

Isolation: every block uses its own owner; canonical state files for
that owner are removed first and the starting stacks are verified
empty (a new Program() is NOT assumed fresh — the starting state is
checked, per project law).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from form.open import open_program, Program
from form.persist import _STATE_DIR, _safe_owner
from form.dell_matrix.needs import (
    parse_and_place, set_detail, set_goals,
    push_action, undo_last, history_report,
)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {detail}" if detail and not cond else ""))


def _cleanup(owner):
    safe = _safe_owner(owner)
    try:
        for name in os.listdir(_STATE_DIR):
            if safe not in name or ".dmtmp." in name:
                continue
            p = os.path.join(_STATE_DIR, name)
            try:
                if os.path.isfile(p):
                    os.remove(p)
            except OSError:
                pass
    except OSError:
        pass


def _fresh(owner):
    _cleanup(owner)
    p = open_program(owner)
    # Verify the isolation boundary instead of assuming it.
    assert len(getattr(p, "action_stack", None) or []) == 0, f"{owner}: action stack not empty at start"
    return p


def _redo(p):
    fn = getattr(p, "redo", None)
    if fn is None:
        raise AttributeError("Program.redo does not exist")
    return fn()


def _set_depth(p, n):
    from form.dell_matrix import needs
    fn = getattr(needs, "set_undo_depth", None)
    if fn is None:
        raise AttributeError("needs.set_undo_depth does not exist")
    return fn(p, n)


def _depth(p):
    return getattr(p, "undo_depth", None)


def _dropped(p):
    return getattr(p, "action_dropped_total", None)


def _redo_stack(p):
    return getattr(p, "redo_stack", None)


def _place(p, label, detail="d0", goals="g0"):
    return parse_and_place(p, f"create an idea called {label} detail: {detail} goals: {goals}")


def run_all():
    # ── T1 + B: default 30; boundary 30/31 ─────────────────────────────
    try:
        p = _fresh("qlc1_t1")
        check("T1.default_is_30", _depth(p) == 30, f"undo_depth={_depth(p)!r}")
        ids = []
        for i in range(30):
            ids.append(_place(p, f"Qone {i}")["id"])
        check("B.at_30_no_drop", len(p.action_stack) == 30 and _dropped(p) == 0,
              f"len={len(p.action_stack)} dropped={_dropped(p)!r}")
        ids.append(_place(p, "Qone 30")["id"])
        check("T1.bound_30", len(p.action_stack) == 30, f"len={len(p.action_stack)}")
        check("T3.counter_1", _dropped(p) == 1, f"dropped={_dropped(p)!r}")
        # Undo to exhaustion: ids[1..30] reverse; ids[0] was evicted.
        n_ok = 0
        while True:
            r = undo_last(p)
            if not r.get("ok"):
                break
            n_ok += 1
        check("T1.exhaust_30", n_ok == 30, f"undid {n_ok}")
        check("T1.first_evicted", ids[0] in p.cube.session.plane.units
              and all(i not in p.cube.session.plane.units for i in ids[1:]),
              "eviction victim wrong")
        _cleanup("qlc1_t1")
    except Exception as e:
        check("T1.block", False, f"{type(e).__name__}: {e}")

    # ── T3 display ──────────────────────────────────────────────────────
    try:
        p = _fresh("qlc1_t3")
        for i in range(31):
            _place(p, f"Qthree {i}")
        rep = "\n".join(history_report(p))
        check("T3.display", ("30/30" in rep and "dropped" in rep.lower()),
              f"history_report lacks depth/drop display: {rep[-200:]}")
        _cleanup("qlc1_t3")
    except Exception as e:
        check("T3.block", False, f"{type(e).__name__}: {e}")

    # ── T2: adjustability, refusals, persistence, per-owner ────────────
    try:
        p = _fresh("qlc1_t2")
        for i in range(30):
            _place(p, f"Qtwo {i}")
        r = _set_depth(p, 5)
        check("T2.trim_reports", r.get("ok") and r.get("dropped") == 25 and len(p.action_stack) == 5,
              f"set 5 -> {r}, len={len(p.action_stack)}")
        r = _set_depth(p, 50)
        check("T2.grow_no_resurrect", r.get("ok") and len(p.action_stack) == 5 and _depth(p) == 50,
              f"set 50 -> {r}, len={len(p.action_stack)}")
        r0 = _set_depth(p, 0)
        r201 = _set_depth(p, 201)
        check("B.depth_0_refused", r0.get("ok") is False and _depth(p) == 50, f"set 0 -> {r0}")
        check("T2.above_max_refused", r201.get("ok") is False and _depth(p) == 50, f"set 201 -> {r201}")
        p.save()
        p2 = Program.load("qlc1_t2")
        check("T2.depth_persists", _depth(p2) == 50, f"reloaded depth={_depth(p2)!r}")
        check("T2.stacks_ephemeral", len(getattr(p2, "action_stack", []) or []) == 0
              and len(_redo_stack(p2) or []) == 0, "stacks must not survive save/load")
        p3 = _fresh("qlc1_t2b")
        check("T2.per_owner", _depth(p3) == 30, f"second owner depth={_depth(p3)!r}")
        _cleanup("qlc1_t2")
        _cleanup("qlc1_t2b")
    except Exception as e:
        check("T2.block", False, f"{type(e).__name__}: {e}")

    # ── T4: redo re-applies in order, place record restored whole ──────
    try:
        p = _fresh("qlc1_t4")
        res = _place(p, "Qfour B", detail="orig detail", goals="goal one")
        bid = res["id"]
        set_detail(p, bid, "edited detail")
        r = undo_last(p)
        u = p.cube.session.plane.units.get(bid)
        check("T4.undo_edit", r.get("ok") and u is not None and u.detail == "orig detail",
              f"undo edit -> {r}, detail={u.detail if u else None!r}")
        r = undo_last(p)
        check("T4.undo_place", r.get("ok") and bid not in p.cube.session.plane.units,
              f"undo place -> {r}")
        r = _redo(p)
        u = p.cube.session.plane.units.get(bid)
        check("T4.redo_place_full_record", r.get("ok") and u is not None
              and u.label == "Qfour B" and u.detail == "orig detail"
              and list(u.goals) == ["goal one"] and (u.words or "") != "",
              f"redo place -> {r}, unit={u}")
        r = _redo(p)
        u = p.cube.session.plane.units.get(bid)
        check("T4.redo_edit", r.get("ok") and u is not None and u.detail == "edited detail",
              f"redo edit -> {r}")
        check("T4.redo_exhausted", _redo(p).get("ok") is False, "redo past end must refuse")
        _cleanup("qlc1_t4")
    except Exception as e:
        check("T4.block", False, f"{type(e).__name__}: {e}")

    # ── T5: tail invalidation ───────────────────────────────────────────
    try:
        p = _fresh("qlc1_t5")
        _place(p, "Qfive A")
        undo_last(p)
        _place(p, "Qfive B")
        r = _redo(p)
        check("T5.invalidated", r.get("ok") is False and "nothing to redo" in str(r.get("reason") or r.get("msg") or ""),
              f"redo after new action -> {r}")
        check("T5.redo_stack_empty", len(_redo_stack(p) or []) == 0, f"redo_stack={_redo_stack(p)!r}")
        _cleanup("qlc1_t5")
    except Exception as e:
        check("T5.block", False, f"{type(e).__name__}: {e}")

    # ── T6: redo bound semantics ────────────────────────────────────────
    try:
        p = _fresh("qlc1_t6")
        _set_depth(p, 3)
        for lbl in ("Qsix A", "Qsix B", "Qsix C"):
            _place(p, lbl)
        for _ in range(3):
            undo_last(p)
        check("T6.tail_3", len(_redo_stack(p) or []) == 3, f"tail={_redo_stack(p)!r}")
        oks = sum(1 for _ in range(3) if _redo(p).get("ok"))
        check("T6.three_redos", oks == 3, f"redos ok={oks}")
        check("T6.fourth_refuses", _redo(p).get("ok") is False, "4th redo must refuse")
        # Shrink with a live tail: 3 undos again, then depth 2 trims tail.
        for _ in range(3):
            undo_last(p)
        _set_depth(p, 2)
        check("T6.shrink_trims_tail", len(_redo_stack(p) or []) == 2, f"tail={_redo_stack(p)!r}")
        _cleanup("qlc1_t6")
    except Exception as e:
        check("T6.block", False, f"{type(e).__name__}: {e}")

    # ── T7: refusal honesty ─────────────────────────────────────────────
    try:
        p = _fresh("qlc1_t7")
        check("T7.empty_undo", undo_last(p).get("reason") == "nothing to undo", "empty undo dishonest")
        r = _redo(p)
        check("T7.empty_redo", r.get("ok") is False and "nothing to redo" in str(r.get("reason") or ""),
              f"empty redo -> {r}")
        # Redo onto a re-taken id refuses and mutates nothing.
        res = _place(p, "Qseven X")
        xid = res["id"]
        undo_last(p)  # X removed; redo tail holds its place record
        p.place(xid, "Qseven Impostor", words="impostor")
        before = p.cube.session.plane.units[xid].label
        r = _redo(p)
        check("T7.retaken_refuses", r.get("ok") is False
              and p.cube.session.plane.units[xid].label == before,
              f"redo onto retaken id -> {r}")
        _cleanup("qlc1_t7")
    except Exception as e:
        check("T7.block", False, f"{type(e).__name__}: {e}")
    try:
        # Revision-owned undo still refuses (PAC-I M2 pattern).
        from form.mandell.supersession import supersede_proposal
        p = _fresh("qlc1_t7r")
        prop = p.nursery.add("Qseven Rev")
        p.confirm_proposal(prop.id, _producer="test", _review_context=p.make_review_context(prop.id, "test"))
        pid = prop.id
        p.place(pid, "Qseven Rev", words="rev words")
        p.acceptance_policy.grant_opt_in("test", scope="test")
        sres = supersede_proposal(p, pid, "qseven successor", label="Qseven Rev 2", _producer="test")
        check("T7.setup_supersede", sres.get("ok") is True, f"supersede setup: {sres}")
        push_action(p, {"kind": "place", "id": pid, "label": "Qseven Rev"})
        r = undo_last(p)
        check("T7.revision_refused", r.get("ok") is False and r.get("reason") == "revision_authority"
              and pid in p.cube.session.plane.units, f"revision undo -> {r}")
        check("T7.refusal_feeds_no_redo", len(_redo_stack(p) or []) == 0,
              f"refused undo fed redo tail: {_redo_stack(p)!r}")
        _cleanup("qlc1_t7r")
    except Exception as e:
        check("T7r.block", False, f"{type(e).__name__}: {e}")

    # ── M: mixed place/edit round-trip + T8 records untouched ──────────
    try:
        p = _fresh("qlc1_tm")
        gen0 = p.duo.generation
        outcomes0 = len(getattr(p, "outcome_records", {}) or {})
        a = _place(p, "Qmix A", detail="a detail", goals="ga")
        b = _place(p, "Qmix B", detail="b detail", goals="gb")
        set_detail(p, a["id"], "a detail v2")
        set_goals(p, b["id"], "gb1; gb2")
        snap = {}
        for uid in (a["id"], b["id"]):
            u = p.cube.session.plane.units[uid]
            snap[uid] = (u.label, u.words, u.detail, list(u.goals), u.x, u.y)
        for _ in range(4):
            undo_last(p)
        check("M.all_undone", a["id"] not in p.cube.session.plane.units
              and b["id"] not in p.cube.session.plane.units, "mixed undo incomplete")
        for _ in range(4):
            _redo(p)
        same = True
        for uid, want in snap.items():
            u = p.cube.session.plane.units.get(uid)
            if u is None or (u.label, u.words, u.detail, list(u.goals), u.x, u.y) != want:
                same = False
        check("M.redo_restores_all", same, "mixed redo did not restore exact pre-undo state")
        check("T8.records_untouched", p.duo.generation == gen0
              and len(getattr(p, "outcome_records", {}) or {}) == outcomes0,
              f"gen {gen0}->{p.duo.generation}, outcomes {outcomes0}->"
              f"{len(getattr(p, 'outcome_records', {}) or {})}")
        _cleanup("qlc1_tm")
    except Exception as e:
        check("M.block", False, f"{type(e).__name__}: {e}")

    # ── S: snapshot stack compatibility (separate authority, untouched) ─
    try:
        from form.mandell.core_ii_exec import CoreIIState, append_snapshot, SNAPSHOTS_CAP
        check("S.cap_still_64", SNAPSHOTS_CAP == 64, f"SNAPSHOTS_CAP={SNAPSHOTS_CAP}")
        st = CoreIIState()
        for _ in range(65):
            append_snapshot(st)
        check("S.snapshot_trim_counted", len(st.snapshots) == 64 and st.snapshots_dropped_total == 1,
              f"len={len(st.snapshots)} dropped={st.snapshots_dropped_total}")
        p = _fresh("qlc1_ts")
        _place(p, "Qsnap A")
        undo_last(p)
        _redo(p)
        check("S.independent", len(st.snapshots) == 64 and len(p.action_stack) == 1,
              "action/snapshot stacks leaked into each other")
        _cleanup("qlc1_ts")
    except Exception as e:
        check("S.block", False, f"{type(e).__name__}: {e}")

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"=== UNDO_REDO_DEPTH {passed}/{len(RESULTS)} ===")
    return passed == len(RESULTS)


def smoke() -> bool:
    try:
        return bool(run_all())
    except Exception as e:
        print(f"UNDO_REDO_DEPTH SMOKE FAILED: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
