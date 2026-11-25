#!/usr/bin/env python3
"""FI-011 Q-FI011.4 — W4 ADVERSARIAL PROBE (Part VI — Unknowns; Uni-built
artifact for the Keeper's W4 scope ruling).

Q-FI011.4 (Keeper, exact): "W4 adversarial scope — which attack
classes the hardening wave must cover: gate-widening attempts,
origin spoofing, placement escapes, receipt completeness,
held-out probes." Decision index B5 adds: widen / spoof / replay /
cross-wall / partial-save. The HOLDs on this question (Keeper
7061156434; Director 7061260190) stand until the ACTUAL adversarial
artifacts exist. This file IS the artifact for Q-FI011.4: runnable
attacks against the CURRENT confirmation surfaces, executed, with
the outcomes recorded in the run log. It does not implement FI-011
(W1-W4 are unbuilt) and it does not settle the question — it gives
the Keeper demonstrated results to scope W4 against.

SURFACES UNDER ATTACK (current main, verified by source census
this run):
  - the canonical writer: Program.confirm_proposal
    (form/open.py) + form/dell_matrix/confirm_lineage.py, gated by
    AcceptancePolicy (form/dell_matrix/acceptance_policy.py);
  - the agent surface: form/dell_matrix/agent_authority.py
    (AgentEndpoint.confirm(pid, grant_handle); grants issued by
    issue_root_grant, narrowed by attenuate_for, killed by
    revoke_grant; a grant binds subject / owner / operation /
    target / content-hash / max_depth, session-scoped);
  - the raw store: Nursery.confirm(pid) (form/dell_matrix/
    nursery.py) — takes NO actor, NO grant, writes NO receipt;
  - the persisted store file itself (the cross-wall surface);
  - the owner opt-in auto-confirm sweep (set_auto_confirm_grow +
    grow_ideas) — today's closest analogue of an FI-011 standing
    gate, and therefore a W4 widening surface.

DOCTRINE ASSERTED (the failing-first contract):
  confirmation is the owner's sovereign act, or a capability
  grant strictly bound to (subject, owner, operation, target,
  content); nothing widens a grant, spoofs an origin, replays a
  grant across proposals, crosses the sandbox/file wall, or
  leaves a half-saved confirmation; every confirmation is
  receipted and attributable (Witness Law). A check PASSes when
  the doctrine holds; it FAILs when the attack lands. FAILs are
  the deliverable — each names its class so the Keeper can rule
  it into (or out of) W4 scope explicitly.

DISCLOSED BOUNDARIES (recorded so FAILs are read honestly):
  agent_authority's own docstring disclaims defense against
  malicious in-process Python; confirm_placement_test.py (Gate-2
  lane) discloses that hand-edited save files can forge durable
  markers. Attacks A8/A9 land inside those disclosed boundaries;
  they are still run and still FAIL the strict doctrine above,
  because (a) the receipt-completeness gap in A8 is NOT covered
  by the in-process disclaimer (the Witness Law binds trusted
  paths too), and (b) whether the disclosed residuals stay
  acceptable once Psalm workflows exist is precisely the
  Keeper's Q-FI011.4 ruling to make.

Labels: INTEGRATION (Program writer + endpoint legs, driven
through the same call shapes the REPL uses) + UNIT (raw store
legs on temp files). State hygiene: unique owners per leg group,
loud cleanup; store legs use temp dirs only. Nothing touches
another owner's state.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")

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
    p.place("w4pa", "w4 parent a", words="harbor lantern parent a",
            x=0.0, y=0.0)
    p.place("w4pb", "w4 parent b", words="harbor lantern parent b",
            x=1.0, y=0.0)
    return p


def seed(p, label, origin="suite:seeded"):
    prop = p.nursery.add(label=label, words=f"words for {label}",
                         kind="new", parents=["w4pa", "w4pb"],
                         origin=origin, reason="fi011 w4 adversarial probe")
    return prop.id


def status_of(p, pid):
    prop = p.nursery.proposals.get(pid)
    return getattr(prop, "status", None)


def manual_confirm(p, pid):
    return p.confirm_proposal(
        pid, _producer="repl_user",
        _review_context=p.make_review_context(pid, "repl_user"))


# ---------------------------------------------------------------- controls
def controls():
    from form.dell_matrix.agent_authority import bind_agent, issue_root_grant
    owner = "W4ADV01"
    p = build(owner)
    # C0 — the owner's own manual confirm (exact REPL call shape).
    pid = seed(p, "w4 c0 manual control")
    res = manual_confirm(p, pid)
    unit = p.cube.session.plane.units.get(pid)
    check("C0_control_manual_confirm_works",
          bool(res.get("ok")) and status_of(p, pid) == "confirmed"
          and unit is not None,
          f"res_ok={res.get('ok')} status={status_of(p, pid)} "
          f"placed={unit is not None} res_keys={sorted(res.keys())}")
    # A13 — receipt/provenance completeness on the canonical path:
    # the confirmed state must survive reload AND the placed unit
    # must carry provenance tying it to the confirmation.
    from form.open import Program
    p2 = Program.load(owner)
    unit2 = p2.cube.session.plane.units.get(pid)
    prov = None
    if unit2 is not None:
        for attr in ("lineage", "origin", "source", "parents"):
            v = getattr(unit2, attr, None)
            if v:
                prov = f"{attr}={v!r}"
                break
    check("A13_receipt_canonical_path_durable_and_attributed",
          status_of(p2, pid) == "confirmed" and unit2 is not None
          and prov is not None,
          f"reloaded_status={status_of(p2, pid)} placed={unit2 is not None} "
          f"provenance={prov} res_keys={sorted(res.keys())}")
    # C1 — the grant path works for the bound subject + target.
    pid2 = seed(p, "w4 c1 grant control")
    g = issue_root_grant(p, issuer="ace", subject="helper", target=pid2)
    ep = bind_agent(p, "helper")
    res2 = ep.confirm(pid2, g["grant_id"])
    check("C1_control_grant_confirm_works",
          bool(res2.get("ok")) and status_of(p, pid2) == "confirmed",
          f"res_ok={res2.get('ok')} status={status_of(p, pid2)}")
    cleanup(owner)


# ---------------------------------------------------------------- spoof / widen / stale
def spoof_widen_stale():
    from form.dell_matrix.acceptance_policy import ApprovalError
    from form.dell_matrix.agent_authority import (
        attenuate_for, bind_agent, issue_root_grant, revoke_grant)
    owner = "W4ADV02"
    p = build(owner)

    # A1 — SPOOF: a fabricated grant handle that was never issued.
    pid = seed(p, "w4 a1 fabricated grant")
    ep = bind_agent(p, "mallory")
    res = ep.confirm(pid, "grant_forged_000000000000000000000000")
    check("A1_spoof_fabricated_grant_denied",
          not res.get("ok") and status_of(p, pid) == "pending",
          f"res_ok={res.get('ok')} reason={res.get('reason')} "
          f"status={status_of(p, pid)}")

    # A2 — SPOOF: a real grant presented by the WRONG subject.
    pid = seed(p, "w4 a2 wrong subject")
    g = issue_root_grant(p, issuer="ace", subject="honest", target=pid)
    res = bind_agent(p, "mallory").confirm(pid, g["grant_id"])
    check("A2_spoof_wrong_subject_denied",
          not res.get("ok") and status_of(p, pid) == "pending",
          f"res_ok={res.get('ok')} reason={res.get('reason')} "
          f"status={status_of(p, pid)}")

    # A3 — WIDEN: a grant bound to target A presented for target B.
    pid_a = seed(p, "w4 a3 target a")
    pid_b = seed(p, "w4 a3 target b")
    g = issue_root_grant(p, issuer="ace", subject="helper", target=pid_a)
    res = bind_agent(p, "helper").confirm(pid_b, g["grant_id"])
    check("A3_widen_cross_target_denied",
          not res.get("ok") and status_of(p, pid_b) == "pending"
          and status_of(p, pid_a) == "pending",
          f"res_ok={res.get('ok')} reason={res.get('reason')} "
          f"status_b={status_of(p, pid_b)}")

    # A4 — WIDEN: attenuation must never expand (new target, or
    # greater delegation depth than the parent grant).
    widened_target = widened_depth = None
    try:
        attenuate_for(p, g["grant_id"], target=pid_b)
        widened_target = "ALLOWED"
    except ApprovalError as exc:
        widened_target = f"ApprovalError: {exc}"
    try:
        attenuate_for(p, g["grant_id"], max_depth=99)
        widened_depth = "ALLOWED"
    except ApprovalError as exc:
        widened_depth = f"ApprovalError: {exc}"
    check("A4_widen_attenuation_expansion_refused",
          widened_target.startswith("ApprovalError")
          and widened_depth.startswith("ApprovalError"),
          f"target={widened_target} depth={widened_depth}")

    # A5 — STALE: a revoked grant must deny.
    pid = seed(p, "w4 a5 revoked grant")
    g = issue_root_grant(p, issuer="ace", subject="helper", target=pid)
    revoke_grant(p, g["grant_id"])
    res = bind_agent(p, "helper").confirm(pid, g["grant_id"])
    check("A5_stale_revoked_grant_denied",
          not res.get("ok") and status_of(p, pid) == "pending",
          f"res_ok={res.get('ok')} reason={res.get('reason')} "
          f"status={status_of(p, pid)}")

    # A5b — STALE/REPLAY across sessions: a grant issued in one
    # Program session presented to a reloaded Program (new policy
    # session, same owner state) must deny — grants are
    # session-scoped issuance records, not portable tokens.
    pid = seed(p, "w4 a5b cross session")
    g = issue_root_grant(p, issuer="ace", subject="helper", target=pid)
    from form.open import Program
    p2 = Program.load(owner)
    res = bind_agent(p2, "helper").confirm(pid, g["grant_id"])
    check("A5b_stale_cross_session_grant_denied",
          not res.get("ok") and status_of(p2, pid) == "pending",
          f"res_ok={res.get('ok')} reason={res.get('reason')} "
          f"status={status_of(p2, pid)}")

    # A6 — STALE: content drift after issuance (grant bound to the
    # proposal's content hash; the record's words are then changed
    # in memory — in-process staging; the boundary under test is
    # the policy's live content check, not the staging method).
    pid = seed(p, "w4 a6 content drift")
    g = issue_root_grant(p, issuer="ace", subject="helper",
                         target=pid, content_pid=pid)
    p.nursery.proposals[pid].words = "drifted content never reviewed"
    res = bind_agent(p, "helper").confirm(pid, g["grant_id"])
    check("A6_stale_content_drift_denied",
          not res.get("ok") and status_of(p, pid) == "pending",
          f"res_ok={res.get('ok')} reason={res.get('reason')} "
          f"status={status_of(p, pid)}")
    cleanup(owner)


# ---------------------------------------------------------------- replay
def replay():
    from form.dell_matrix.agent_authority import bind_agent, issue_root_grant
    owner = "W4ADV03"
    p = build(owner)
    # A7 — REPLAY: one broad grant (no target, no content binding)
    # presented for TWO distinct proposals. Strict doctrine: a
    # grant authorizes the confirmations it was issued for; reuse
    # across proposals must deny (or, if the Keeper rules standing
    # capability lawful, each use must be receipted as a reuse —
    # the receipts are printed either way).
    pid1 = seed(p, "w4 a7 replay one")
    pid2 = seed(p, "w4 a7 replay two")
    g = issue_root_grant(p, issuer="ace", subject="helper")
    ep = bind_agent(p, "helper")
    res1 = ep.confirm(pid1, g["grant_id"])
    res2 = ep.confirm(pid2, g["grant_id"])
    check("A7_replay_one_grant_two_proposals",
          bool(res1.get("ok")) and not res2.get("ok")
          and status_of(p, pid2) == "pending",
          f"first_ok={res1.get('ok')} second_ok={res2.get('ok')} "
          f"status2={status_of(p, pid2)} "
          f"second_res_keys={sorted(res2.keys())}")
    cleanup(owner)


# ---------------------------------------------------------------- auto-sweep widening
def auto_sweep():
    owner = "W4ADV04"
    p = build(owner)
    # A12 — WIDEN (standing-gate analogue): the owner opt-in
    # auto-confirm sweep is origin-blind. A proposal authored by a
    # docked AI (origin agent:psalm — under FI-011 a Psalm may
    # only ever PROPOSE, PENDING) sits in the Nursery; the sweep
    # is switched on for growth; if the sweep confirms the
    # agent-authored proposal, the standing mechanism has no gate
    # terms at all — the exact widening W4 must scope.
    pid = seed(p, "w4 a12 psalm authored", origin="agent:psalm")
    p.set_auto_confirm_grow(True)
    p.grow_ideas(1)
    check("A12_widen_auto_sweep_origin_blind",
          status_of(p, pid) == "pending",
          f"status_after_sweep={status_of(p, pid)} "
          f"(seeded origin='agent:psalm', kind='new')")
    cleanup(owner)


# ---------------------------------------------------------------- raw store legs
def store_legs():
    from form.dell_matrix.nursery import Nursery, NurseryLoadError
    # A8 — BYPASS + RECEIPT: the raw store confirm takes no actor
    # and no grant, and leaves no receipt anywhere.
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "nursery_a8.json")
        n = Nursery(path=path)
        prop = n.add("w4 a8 raw store confirm", words="w", kind="new",
                     origin="suite:seeded", reason="w4 probe")
        out = n.confirm(prop.id)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        sections = {k: v for k, v in data.items() if k.startswith("__")}
        confirm_receipt_found = any(
            isinstance(v, dict) and any(
                isinstance(rec, dict) and rec.get("proposal_id") == prop.id
                for rec in v.values())
            for v in sections.values())
        check("A8_bypass_raw_store_confirm_unattributed_unreceipted",
              False if (out is not None and out.status == "confirmed") else True,
              f"raw_confirm_returned={out is not None} "
              f"status={out.status if out else None} "
              f"edit_receipts={len(n.organization_edit_receipts)} "
              f"file_sections={sorted(sections)} "
              f"confirm_receipt_for_pid={confirm_receipt_found} "
              f"(doctrine: every confirmation is actor-bound and "
              f"receipted; the store door enforces neither)")
    # A9 — CROSS-WALL: a hand-edited store file flips a proposal
    # to confirmed out-of-band; load must not honor a confirmation
    # no writer performed. A9b: an unknown status string must be
    # refused at load, not silently carried.
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "nursery_a9.json")
        n = Nursery(path=path)
        prop = n.add("w4 a9 forged status", words="w", kind="new",
                     origin="suite:seeded", reason="w4 probe")
        n.save()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data[prop.id]["status"] = "confirmed"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        n2 = Nursery.load(path)
        forged = n2.proposals[prop.id].status
        data[prop.id]["status"] = "bogus_status_value"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        try:
            n3 = Nursery.load(path)
            bogus = f"loaded as {n3.proposals[prop.id].status!r}"
        except NurseryLoadError as exc:
            bogus = f"refused: {exc}"
        check("A9_crosswall_forged_file_status",
              forged != "confirmed" and bogus.startswith("refused"),
              f"forged_status_loaded_as={forged!r} bogus_status={bogus} "
              f"(disclosed residual class: hand-edited save files — "
              f"Keeper rules whether W4 closes it)")
    # A10 — PARTIAL-SAVE: a torn (truncated) store file must fail
    # closed at load — never a silent empty/partial nursery.
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "nursery_a10.json")
        n = Nursery(path=path)
        n.add("w4 a10 torn file", words="w", kind="new",
              origin="suite:seeded", reason="w4 probe")
        n.save()
        with open(path, "rb") as f:
            blob = f.read()
        with open(path, "wb") as f:
            f.write(blob[: len(blob) // 2])
        try:
            Nursery.load(path)
            torn = "LOADED (silent acceptance)"
        except NurseryLoadError:
            torn = "NurseryLoadError (fail-closed)"
        check("A10_partial_torn_file_fails_closed",
              torn.startswith("NurseryLoadError"),
              f"torn_load={torn}")
    # A11 — PARTIAL-SAVE: if the save inside confirm fails, the
    # in-memory status must revert to pending and the failure
    # must propagate — no half-confirmed state.
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "nursery_a11.json")
        n = Nursery(path=path)
        prop = n.add("w4 a11 save failure", words="w", kind="new",
                     origin="suite:seeded", reason="w4 probe")

        def boom(**kw):
            raise RuntimeError("staged save failure (probe)")

        n.save = boom  # staging only; the revert logic is the target
        try:
            n.confirm(prop.id)
            outcome = "no exception (silent)"
        except RuntimeError:
            outcome = "RuntimeError propagated"
        check("A11_partial_confirm_save_failure_reverts",
              outcome.startswith("RuntimeError")
              and n.proposals[prop.id].status == "pending",
              f"outcome={outcome} status={n.proposals[prop.id].status}")


def main() -> int:
    print("=== FI011 W4 ADVERSARIAL PROBE (Q-FI011.4) ===")
    controls()
    spoof_widen_stale()
    replay()
    auto_sweep()
    store_legs()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"FI011_W4_ADVERSARIAL {passed}/{len(RESULTS)} HELD")
    for name, ok in RESULTS:
        if not ok:
            print(f"  ATTACK LANDED: {name}")
    return 0 if passed == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
