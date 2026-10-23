#!/usr/bin/env python3
"""P4 lifecycle-gravity proof — REPAIRED 2026-10-22.

Contract under test (current canonical law):
  SpatialAuthority._wells filters well candidates through
  canonical_lifecycle.is_active(program, uid), which requires ALL of:
    - accepted: the proposal was confirmed through the WO-5.1
      acceptance-policy boundary (Program.confirm_proposal);
    - a valid ACTIVE revision (supersession.inspect_revision);
    - non-faded presence (TPP-I, form/lifecycle.py set_presence).
  SUPERSEDED ideas do NOT participate ordinarily (WO-5.3: superseded
  was removed from _ACTIVE_STATES deliberately, Director 2026-10-05).
  Units with NO canonical record attract by explicit legacy
  compatibility policy (documented in canonical_lifecycle, not a
  silent default). Malformed records fail closed.

Repair history: the original version of this proof constructed
lifecycle states by writing ``lifecycle_state`` directly onto
UNCONFIRMED Nursery proposals (a Phase-3-era fixture). Phase 5
(WO-5.1/5.2/5.3) made acceptance + revision + presence the
load-bearing dimensions of is_active, so that fixture described
non-participating state and the proof decayed to 13/17 at HEAD
(b852210) — invisibly, because no P4 proof was registered in
form/regress.py. A discriminating probe (2026-10-22) proved the
PRODUCT correct through the production boundary (add -> review ->
confirm => is_active True => well forms), so this repair rebuilds
the fixtures on production boundaries only. Direct record writes
remain ONLY where the fixture's purpose is corruption (the
malformed case). Expectations are re-based on current law; the
superseded expectation INVERTED versus the Phase-3 table because
the law changed, not because the product regressed.

Checks:
- confirmed active -> attracts; pending -> no; rejected -> no
- confirmed + faded presence -> no; unfade (restore) -> attracts
- superseded -> no (WO-5.3); its confirmed successor -> attracts
- legacy no-record -> attracts (explicit compatibility)
- malformed record -> no (fail-closed)
- explicit gravity wells filtered the same way; score-fallback too
- CAUSAL MUTANT: removing is_active from _wells must FAIL this proof
"""

import os
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, REPO)
os.chdir(REPO)

CHECKS, FAILED = [], []


def rec(name, ok, detail=""):
    CHECKS.append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}", flush=True)
    if not ok:
        FAILED.append(name)


def _clean(owner):
    from form.persist import _safe_owner
    d = os.path.join(REPO, "form/state", f"ideas_{_safe_owner(owner)}")
    shutil.rmtree(d, ignore_errors=True)
    for suffix in (f"program_{owner}.json", f"nursery_{owner}.json"):
        try:
            os.remove(os.path.join(REPO, "form/state", suffix))
        except OSError:
            pass


def _prog(owner):
    from form.open import Program
    return Program(owner=owner)


def _place_pair(p):
    p.cube.session.plane.units.clear()
    p.place("anchor", "anchor idea", x=0.0, y=0.0)


def _confirmed(p, label, x=50.0, y=0.0):
    """Build a confirmed, active idea through the production boundary:
    nursery.add -> place -> make_review_context -> confirm_proposal
    (the WO-5.1 acceptance-policy path). Returns the proposal id."""
    prop = p.nursery.add(label, words="test", kind="new")
    pid = prop.id
    p.place(pid, label, x=x, y=y)
    p.nursery.save()
    ctx = p.make_review_context(pid, reviewer="p4proof")
    res = p.confirm_proposal(pid, _producer="repl_user",
                             _review_context=ctx)
    assert res.get("ok"), f"confirm failed for {pid}: {res}"
    return pid


def _wells_for(p, uid):
    """True iff a fallback well exists at uid's current position."""
    scores = {uid: 10.0}
    wells = p.spatial._wells(p, p.cube.session.plane, scores)
    pa = p.cube.session.plane
    u = pa.units[uid]
    return any(abs(wx - u.x) < 1e-9 and abs(wy - u.y) < 1e-9
               for wx, wy, _ in wells)


def t_lifecycle_well_gating():
    """Each producible lifecycle state: who attracts, who does not."""
    from form.lifecycle import do_fade
    from form.mandell.supersession import supersede_proposal

    # confirmed active -> attracts
    owner = "P4LG_active"
    try:
        p = _prog(owner)
        _place_pair(p)
        pid = _confirmed(p, "probe idea")
        rec("gravity::active_well", _wells_for(p, pid),
            "confirmed active idea attracts")
    finally:
        _clean(owner)

    # pending proposal (never confirmed) -> no attraction
    owner = "P4LG_pending"
    try:
        p = _prog(owner)
        _place_pair(p)
        prop = p.nursery.add("pending idea", words="test", kind="new")
        p.place(prop.id, "pending idea", x=50.0, y=0.0)
        p.nursery.save()
        rec("gravity::pending_no_well", not _wells_for(p, prop.id),
            "unconfirmed proposal does not attract (WO-5.1)")
    finally:
        _clean(owner)

    # rejected proposal -> no attraction
    owner = "P4LG_rejected"
    try:
        p = _prog(owner)
        _place_pair(p)
        prop = p.nursery.add("rejected idea", words="test", kind="new")
        p.place(prop.id, "rejected idea", x=50.0, y=0.0)
        p.nursery.reject(prop.id)
        p.nursery.save()
        rec("gravity::rejected_well", not _wells_for(p, prop.id),
            "rejected proposal does not attract")
    finally:
        _clean(owner)

    # confirmed + faded presence -> no attraction
    owner = "P4LG_faded"
    try:
        p = _prog(owner)
        _place_pair(p)
        pid = _confirmed(p, "fading idea")
        do_fade(p, pid, "p4proof")
        rec("gravity::faded_well", not _wells_for(p, pid),
            "faded presence does not attract (TPP-I)")
    finally:
        _clean(owner)

    # superseded -> no attraction under WO-5.3 ordinary participation;
    # its confirmed successor -> attracts (positive control)
    owner = "P4LG_superseded"
    try:
        p = _prog(owner)
        _place_pair(p)
        pid = _confirmed(p, "original idea")
        ctx = p.make_supersede_context(pid, reviewer="p4proof",
                                       words="revised idea words")
        res = supersede_proposal(p, pid, words="revised idea words",
                                 _producer="repl_user",
                                 _review_context=ctx)
        assert res.get("ok"), f"supersede failed: {res}"
        rec("gravity::superseded_well", not _wells_for(p, pid),
            "superseded does not attract (WO-5.3 ordinary participation)")
        succ = res.get("successor_id") or res.get("new_id")
        assert succ, f"no successor in supersede result: {res}"
        rec("gravity::successor_well", _wells_for(p, succ),
            "confirmed successor attracts")
    finally:
        _clean(owner)


def t_unknown_malformed_no_attract():
    """Legacy no-record attracts (explicit policy); malformed does not."""
    owner = "P4LG_unknown"
    try:
        p = _prog(owner)
        p.cube.session.plane.units.clear()
        p.place("probe", "probe idea", x=50.0, y=0.0)
        p.place("anchor", "anchor idea", x=0.0, y=0.0)
        # No proposal -> legacy compatibility -> ACTIVE (documented)
        is_well = _wells_for(p, "probe")
        rec("gravity::legacy_no_proposal_active", is_well,
            f"well={is_well} (explicit legacy compatibility)")
        # Corruption fixture (the ONLY direct write in this proof):
        # a record whose lifecycle_state is garbage must fail closed.
        from form.dell_matrix.nursery import Proposal
        p.nursery.proposals["probe"] = Proposal(
            id="probe", label="probe", words="test", kind="new",
            status="confirmed", lifecycle_state="not_a_real_state_xyz")
        p.nursery.save()
        is_well2 = _wells_for(p, "probe")
        rec("gravity::malformed_no_well", not is_well2,
            f"well={is_well2} (fail-closed)")
    finally:
        _clean(owner)


def t_explicit_well_filtered():
    """Explicit gravity wells are lifecycle-filtered identically."""
    from form.lifecycle import do_fade
    owner = "P4LG_explicit"
    try:
        p = _prog(owner)
        _place_pair(p)
        pid = _confirmed(p, "explicit one")
        do_fade(p, pid, "p4proof")
        p.forces.gravity.wells = [{"id": pid, "x": 50.0, "y": 0.0}]
        wells = p.spatial._wells(p, p.cube.session.plane, {})
        rec("gravity::explicit_faded_filtered", len(wells) == 0,
            f"wells={len(wells)}")
        # Control: a confirmed active idea's explicit well passes.
        pid2 = _confirmed(p, "explicit two", x=-50.0)
        p.forces.gravity.wells = [{"id": pid2, "x": -50.0, "y": 0.0}]
        wells2 = p.spatial._wells(p, p.cube.session.plane, {})
        rec("gravity::explicit_active_passes", len(wells2) == 1,
            f"wells={len(wells2)}")
    finally:
        _clean(owner)


def t_fallback_well_filtered():
    """Score-fallback wells skip inactive ideas, keep active ones."""
    from form.lifecycle import do_fade
    owner = "P4LG_fallback"
    try:
        p = _prog(owner)
        _place_pair(p)
        faded = _confirmed(p, "faded high score")
        do_fade(p, faded, "p4proof")
        active = _confirmed(p, "active low score", x=-50.0)
        scores = {faded: 10.0, active: 0.1}
        wells = p.spatial._wells(p, p.cube.session.plane, scores)
        pa = p.cube.session.plane
        uf, ua = pa.units[faded], pa.units[active]
        faded_is_well = any(abs(wx - uf.x) < 1e-9 and abs(wy - uf.y) < 1e-9
                            for wx, wy, _ in wells)
        active_is_well = any(abs(wx - ua.x) < 1e-9 and abs(wy - ua.y) < 1e-9
                             for wx, wy, _ in wells)
        rec("gravity::fallback_skips_faded", not faded_is_well,
            f"faded_in_wells={faded_is_well}")
        rec("gravity::fallback_keeps_active", active_is_well,
            f"active_in_wells={active_is_well}")
    finally:
        _clean(owner)


def t_restore_reattracts():
    """Fade -> unfade (restore presence) -> attracts again."""
    from form.lifecycle import do_fade, do_unfade
    owner = "P4LG_restore"
    try:
        p = _prog(owner)
        _place_pair(p)
        pid = _confirmed(p, "restorable idea")
        w0 = _wells_for(p, pid)
        do_fade(p, pid, "p4proof")
        w1 = _wells_for(p, pid)
        do_unfade(p, pid, "p4proof")
        w2 = _wells_for(p, pid)
        rec("gravity::restore_reattracts",
            w0 and not w1 and w2,
            f"active={w0} faded_well={w1} restored_well={w2}")
    finally:
        _clean(owner)


def t_causal_mutant():
    """CAUSAL: removing is_active from _wells MUST fail this proof."""
    from form.lifecycle import do_fade
    owner = "P4LG_mutant"
    try:
        p = _prog(owner)
        _place_pair(p)
        pid = _confirmed(p, "mutant probe")
        do_fade(p, pid, "p4proof")
        orig = p.spatial._wells

        def _mutant_wells(self, program, plane, scores):
            wells = []
            for wid, s in sorted(scores.items(),
                                 key=lambda kv: (-kv[1], kv[0]))[:3]:
                if wid in plane.units:
                    u = plane.units[wid]
                    wells.append((u.x, u.y, s + 0.5))
            return wells

        import types
        p.spatial._wells = types.MethodType(_mutant_wells, p.spatial)
        try:
            is_well = _wells_for(p, pid)
            rec("causal::mutant_detected", is_well,
                f"mutant well={is_well} (must be True to prove "
                f"detection works)")
        finally:
            p.spatial._wells = orig
        is_well_real = _wells_for(p, pid)
        rec("causal::real_gates", not is_well_real,
            f"real well={is_well_real}")
    finally:
        _clean(owner)


def main():
    print("=== P4 LIFECYCLE-GRAVITY PROOF ===", flush=True)
    t_lifecycle_well_gating()
    t_unknown_malformed_no_attract()
    t_explicit_well_filtered()
    t_fallback_well_filtered()
    t_restore_reattracts()
    t_causal_mutant()
    print(f"P4 LIFECYCLE-GRAVITY: {len(CHECKS) - len(FAILED)}/{len(CHECKS)}"
          f" pass; failed={FAILED}", flush=True)
    return 0 if not FAILED else 1


if __name__ == "__main__":
    sys.exit(main())


def smoke() -> bool:
    """Canonical-runner adapter (form/regress.py): True iff the
    full proof passes. Added 2026-10-22 (P4 coverage repair)."""
    return main() == 0
