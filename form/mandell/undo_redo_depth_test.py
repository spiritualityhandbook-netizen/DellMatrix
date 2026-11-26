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
  C  Codex P2 regressions on PR #481 (review 6965599145; Director HOLD
     6965753487 requirement 1): C1 the place record preserves the
     canonical Idea pointer (idea_id) across undo/redo; C2 a refused
     redo keeps its tail entry so removing the conflict and retrying
     succeeds; C3 redo restores exactly the saved sandbox membership
     (gate auto-box membership is removed first — never dual member-
     ship, never a dangling entry after the next undo); C4 sibling of
     C2 on the undo side: a revision-refused undo keeps its entry.
     C5/C6 Director §42 DELTA 6968119456 (PR #481, exact head 82e2dde6):
     an injected plane.box (C5) or plane.unbox (C6) failure during
     redo's sandbox-membership restore must refuse honestly — no
     ok=True, no consumed redo entry, no half-restored unit — and the
     kept entry must retry cleanly once the fault is removed.

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

    # ── C: Codex P2 regressions (PR #481) ──────────────────────────────
    try:
        # C1: the captured place record carries the canonical Idea
        # pointer; redo restores the unit still bound to its Idea.
        p = _fresh("qlc1_c1")
        p.place("c1unit", "Qcodex Bound", words="bound words", idea_id="idea-c1")
        push_action(p, {"kind": "place", "id": "c1unit", "label": "Qcodex Bound"})
        r = undo_last(p)
        check("C1.undo_ok", r.get("ok") is True and "c1unit" not in p.cube.session.plane.units,
              f"undo bound place -> {r}")
        r = _redo(p)
        u = p.cube.session.plane.units.get("c1unit")
        check("C1.idea_id_preserved", r.get("ok") is True and u is not None
              and getattr(u, "idea_id", None) == "idea-c1",
              f"redo -> {r}, idea_id={getattr(u, 'idea_id', None)!r}")
        _cleanup("qlc1_c1")
    except Exception as e:
        check("C1.block", False, f"{type(e).__name__}: {e}")
    try:
        # C2: a refused redo (re-taken id) keeps its tail entry; removing
        # the conflict and retrying re-applies the original place.
        p = _fresh("qlc1_c2")
        res = _place(p, "Qcodex Retry")
        xid = res["id"]
        undo_last(p)  # X removed; redo tail holds its place record
        p.place(xid, "Qcodex Impostor", words="impostor")
        r = _redo(p)
        check("C2.refusal_keeps_entry", r.get("ok") is False
              and len(_redo_stack(p) or []) == 1,
              f"refused redo -> {r}, tail={_redo_stack(p)!r}")
        p.cube.session.plane.remove(xid)  # conflict removed
        r = _redo(p)
        u = p.cube.session.plane.units.get(xid)
        check("C2.retry_succeeds", r.get("ok") is True and u is not None
              and u.label == "Qcodex Retry",
              f"retry redo -> {r}, unit={u}")
        _cleanup("qlc1_c2")
    except Exception as e:
        check("C2.block", False, f"{type(e).__name__}: {e}")
    try:
        # C3: redo restores exactly the saved sandbox membership even
        # when the global gate auto-boxes the re-place first.
        p = _fresh("qlc1_c3")
        res = _place(p, "Qcodex Boxed")
        uid = res["id"]
        plane = p.cube.session.plane
        plane.box([uid], "vault")
        undo_last(p)  # record captured: sandboxed, sandbox_id=vault
        p.sandbox.turn_on()
        r = _redo(p)
        u = plane.units.get(uid)
        auto = plane.sandboxes.get("auto_sandbox")
        check("C3.single_membership", r.get("ok") is True and u is not None
              and u.sandbox_id == "vault"
              and uid in (plane.sandboxes.get("vault").member_ids if plane.sandboxes.get("vault") else [])
              and not (auto and uid in auto.member_ids),
              f"redo -> {r}, sandbox_id={getattr(u, 'sandbox_id', None)!r}, "
              f"boxes={ {k: list(v.member_ids) for k, v in plane.sandboxes.items()} }")
        undo_last(p)  # restored place undone again: no dangling member
        dangling = [k for k, sb in plane.sandboxes.items() if uid in sb.member_ids]
        check("C3.no_dangling_after_undo", uid not in plane.units and not dangling,
              f"dangling memberships after undo: {dangling}")
        p.sandbox.turn_off()
        _cleanup("qlc1_c3")
    except Exception as e:
        check("C3.block", False, f"{type(e).__name__}: {e}")
    try:
        # C4 (C2 sibling, undo side): a revision-refused undo keeps its
        # action-stack entry instead of silently consuming it.
        from form.mandell.supersession import supersede_proposal
        p = _fresh("qlc1_c4")
        prop = p.nursery.add("Qcodex Rev")
        p.confirm_proposal(prop.id, _producer="test", _review_context=p.make_review_context(prop.id, "test"))
        pid = prop.id
        p.place(pid, "Qcodex Rev", words="rev words")
        p.acceptance_policy.grant_opt_in("test", scope="test")
        sres = supersede_proposal(p, pid, "qcodex successor", label="Qcodex Rev 2", _producer="test")
        check("C4.setup_supersede", sres.get("ok") is True, f"supersede setup: {sres}")
        push_action(p, {"kind": "place", "id": pid, "label": "Qcodex Rev"})
        depth_before = len(p.action_stack)
        r = undo_last(p)
        check("C4.refusal_keeps_entry", r.get("ok") is False
              and r.get("reason") == "revision_authority"
              and len(p.action_stack) == depth_before,
              f"revision undo -> {r}, stack {depth_before}->{len(p.action_stack)}")
        _cleanup("qlc1_c4")
    except Exception as e:
        check("C4.block", False, f"{type(e).__name__}: {e}")
    try:
        # C5 (Director §42 DELTA 6968119456): an injected plane.box
        # failure during redo's sandbox-membership restore must refuse
        # honestly — no ok=True, no consumed redo entry, no
        # half-restored unit left in the plane — and the kept entry
        # must retry cleanly once the fault is removed.
        p = _fresh("qlc1_c5")
        res = _place(p, "Qdelta Boxfail")
        uid = res["id"]
        plane = p.cube.session.plane
        plane.box([uid], "vault")
        undo_last(p)  # record captured: sandboxed, sandbox_id=vault
        orig_box = plane.box

        def _boom_box(*a, **k):
            raise RuntimeError("injected box failure")

        plane.box = _boom_box
        r = _redo(p)
        plane.box = orig_box
        member_of = [k for k, sb in plane.sandboxes.items() if uid in sb.member_ids]
        check("C5.refusal_honest", r.get("ok") is False and "sandbox" in str(r.get("reason") or ""),
              f"box-failed redo -> {r}")
        check("C5.entry_kept", len(_redo_stack(p) or []) == 1,
              f"tail after refused redo: {_redo_stack(p)!r}")
        check("C5.membership_coherent", uid not in plane.units and not member_of,
              f"unit present={uid in plane.units}, member_of={member_of}")
        r = _redo(p)
        u = plane.units.get(uid)
        vault = plane.sandboxes.get("vault")
        check("C5.retry_succeeds", r.get("ok") is True and u is not None
              and u.sandbox_id == "vault" and vault is not None and uid in vault.member_ids,
              f"retry redo -> {r}, sandbox_id={getattr(u, 'sandbox_id', None)!r}")
        _cleanup("qlc1_c5")
    except Exception as e:
        check("C5.block", False, f"{type(e).__name__}: {e}")
    try:
        # C6 (C5 sibling on the unbox leg): the global gate auto-boxes
        # the re-place; an injected plane.unbox failure while removing
        # that auto membership must refuse the same way — and the
        # rollback may not depend on the very door that is failing
        # (plane.remove routes through unbox).
        p = _fresh("qlc1_c6")
        res = _place(p, "Qdelta Unboxfail")
        uid = res["id"]
        plane = p.cube.session.plane
        plane.box([uid], "vault")
        undo_last(p)  # record captured: sandboxed, sandbox_id=vault
        p.sandbox.turn_on()
        orig_unbox = plane.unbox

        def _boom_unbox(*a, **k):
            raise RuntimeError("injected unbox failure")

        plane.unbox = _boom_unbox
        r = _redo(p)
        plane.unbox = orig_unbox
        member_of = [k for k, sb in plane.sandboxes.items() if uid in sb.member_ids]
        check("C6.refusal_honest", r.get("ok") is False and "sandbox" in str(r.get("reason") or ""),
              f"unbox-failed redo -> {r}")
        check("C6.entry_kept", len(_redo_stack(p) or []) == 1,
              f"tail after refused redo: {_redo_stack(p)!r}")
        check("C6.membership_coherent", uid not in plane.units and not member_of,
              f"unit present={uid in plane.units}, member_of={member_of}")
        r = _redo(p)
        u = plane.units.get(uid)
        auto = plane.sandboxes.get("auto_sandbox")
        check("C6.retry_succeeds", r.get("ok") is True and u is not None
              and u.sandbox_id == "vault"
              and uid in (plane.sandboxes.get("vault").member_ids if plane.sandboxes.get("vault") else [])
              and not (auto and uid in auto.member_ids),
              f"retry redo -> {r}, sandbox_id={getattr(u, 'sandbox_id', None)!r}")
        p.sandbox.turn_off()
        _cleanup("qlc1_c6")
    except Exception as e:
        check("C6.block", False, f"{type(e).__name__}: {e}")

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
