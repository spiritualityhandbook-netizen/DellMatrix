#!/usr/bin/env python3
"""FI-011 remediation wave 1 — A7 / A8 / A12 (PR #507 remediation
matrix rows 1-3, Director-accepted design map 7066291209).

The Part VI adversarial probe (Q-FI011.4) landed three attacks
against the confirmation surfaces. This suite is the registered
failing-first control for their fixes; each attack leg must read
HELD here without weakening the probe's conditions:

- A7 REPLAY: one broad grant (no target/content binding) confirmed
  TWO distinct proposals, the second receipt indistinguishable from
  a first use. Contract: grant consumption is single-use — a second
  confirm under the same grant is refused typed, and the one
  successful use is recorded on the policy (grant, target, ordinal).
- A8 CORE ENFORCEMENT: raw ``Nursery.confirm(pid)`` succeeded with
  no actor, no grant, and NO confirmation receipt. Contract: the
  store door itself refuses a confirm without an identified actor
  (typed NurseryConfirmError), and every successful confirmation —
  raw door or canonical writer — writes an attributed, durable
  confirmation receipt (actor, grant, target).
- A12 ORIGIN-BLIND SWEEP: the owner opt-in auto-confirm sweep
  confirmed a docked-AI-authored proposal (origin agent:psalm);
  under FI-011 an agent/docked producer may only propose PENDING.
  Contract: the sweep refuses agent/dock origin classes with a
  typed refusal recorded in the sweep receipt, while eligible
  program-authored proposals still confirm.

Controls C0/C1 pin the legitimate paths (owner manual confirm,
target-bound grant confirm) so the fixes cannot pass by breaking
confirmation itself. A11's save-failure revert is re-pinned here
in its post-fix shape (authorized actor, failing save).

Labels: INTEGRATION (Program legs) + UNIT (raw store legs on temp
files). State hygiene: unique tagged owners per leg group, loud
cleanup; store legs use temp dirs only.
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
                         origin=origin, reason="fi011 remediation suite")
    return prop.id


def status_of(p, pid):
    prop = p.nursery.proposals.get(pid)
    return getattr(prop, "status", None)


def receipts_for(p, pid):
    recs = getattr(p.nursery, "confirmation_receipts", {}) or {}
    return [r for r in recs.values()
            if isinstance(r, dict) and r.get("proposal_id") == pid]


def manual_confirm(p, pid):
    return p.confirm_proposal(
        pid, _producer="repl_user",
        _review_context=p.make_review_context(pid, "repl_user"))


# ---------------------------------------------------------------- controls
def controls():
    owner = "FI011RA"
    p = build(owner)
    # C0 — owner manual confirm works AND leaves an attributed,
    # durable confirmation receipt at the core store.
    pid = seed(p, "fi011 c0 manual control")
    res = manual_confirm(p, pid)
    recs = receipts_for(p, pid)
    check("C0_control_manual_confirm_works",
          bool(res.get("ok")) and status_of(p, pid) == "confirmed"
          and p.cube.session.plane.units.get(pid) is not None,
          f"res_ok={res.get('ok')} status={status_of(p, pid)}")
    check("C0_confirmation_receipt_attributed",
          len(recs) == 1 and bool(recs[0].get("actor")),
          f"receipts={recs}")
    from form.open import Program
    p2 = Program.load(owner)
    recs2 = receipts_for(p2, pid)
    check("C0_confirmation_receipt_durable",
          status_of(p2, pid) == "confirmed" and len(recs2) == 1
          and recs2[0].get("actor") == recs[0].get("actor"),
          f"reloaded_status={status_of(p2, pid)} receipts={recs2}")
    # C1 — target-bound grant confirm works (single legitimate use).
    from form.dell_matrix.agent_authority import bind_agent, issue_root_grant
    pid2 = seed(p, "fi011 c1 grant control")
    g = issue_root_grant(p, issuer="ace", subject="helper", target=pid2)
    res2 = bind_agent(p, "helper").confirm(pid2, g["grant_id"])
    recs3 = receipts_for(p, pid2)
    want_seq = p.acceptance_policy.grant_seq_for(g["grant_id"])
    check("C1_control_grant_confirm_works",
          bool(res2.get("ok")) and status_of(p, pid2) == "confirmed"
          and len(recs3) == 1
          and recs3[0].get("grant_seq") == want_seq
          and recs3[0].get("actor") == "helper",
          f"res_ok={res2.get('ok')} status={status_of(p, pid2)} "
          f"receipts={recs3} want_seq={want_seq}")
    # R6.1 no-leak: the grant HANDLE is a secret — it must appear
    # neither in the confirm result nor in the durable nursery file;
    # receipts name the grant by issuance seq only.
    from form.dell_matrix.nursery import owner_nursery_path
    with open(owner_nursery_path(owner), "r", encoding="utf-8") as f:
        nursery_blob = f.read()
    check("C1_grant_handle_never_recorded",
          g["grant_id"] not in json.dumps(res2)
          and g["grant_id"] not in nursery_blob
          and "grant_id" not in recs3[0],
          f"handle_in_result={g['grant_id'] in json.dumps(res2)} "
          f"handle_in_file={g['grant_id'] in nursery_blob}")
    cleanup(owner)


# ---------------------------------------------------------------- A7 replay
def replay():
    from form.dell_matrix.agent_authority import bind_agent, issue_root_grant
    owner = "FI011RB"
    p = build(owner)
    pid1 = seed(p, "fi011 a7 replay one")
    pid2 = seed(p, "fi011 a7 replay two")
    g = issue_root_grant(p, issuer="ace", subject="helper")
    ep = bind_agent(p, "helper")
    res1 = ep.confirm(pid1, g["grant_id"])
    res2 = ep.confirm(pid2, g["grant_id"])
    consumption = None
    policy = getattr(p, "acceptance_policy", None)
    if policy is not None and hasattr(policy, "grant_consumption"):
        consumption = policy.grant_consumption(g["grant_id"])
    check("A7_replay_one_grant_two_proposals",
          bool(res1.get("ok")) and not res2.get("ok")
          and res2.get("reason") == "acceptance_policy_denied"
          and "consum" in str(res2.get("detail") or "").lower()
          and status_of(p, pid2) == "pending",
          f"first_ok={res1.get('ok')} second_ok={res2.get('ok')} "
          f"second_reason={res2.get('reason')} "
          f"second_detail={res2.get('detail')} "
          f"status2={status_of(p, pid2)}")
    check("A7_consumption_recorded_with_ordinal",
          isinstance(consumption, dict)
          and consumption.get("target") == pid1
          and consumption.get("use") == 1,
          f"consumption={consumption}")
    check("A7_no_receipt_for_refused_replay",
          len(receipts_for(p, pid2)) == 0
          and len(receipts_for(p, pid1)) == 1,
          f"pid1_receipts={len(receipts_for(p, pid1))} "
          f"pid2_receipts={len(receipts_for(p, pid2))}")
    cleanup(owner)


# ---------------------------------------------------------------- A12 sweep
def auto_sweep():
    owner = "FI011RC"
    p = build(owner)
    pid_psalm = seed(p, "fi011 a12 psalm authored", origin="agent:psalm")
    pid_dock = seed(p, "fi011 a12 dock authored", origin="dock:psalm")
    pid_growth = seed(p, "fi011 a12 growth authored", origin="growth:token")
    p.set_auto_confirm_grow(True)
    res = p.grow_ideas(1)
    ac = res.get("auto_confirm") or {}
    refusals = {r.get("id"): r for r in ac.get("skipped_origin_ineligible") or []
                if isinstance(r, dict)}
    check("A12_widen_auto_sweep_origin_blind",
          status_of(p, pid_psalm) == "pending"
          and status_of(p, pid_dock) == "pending",
          f"psalm_status={status_of(p, pid_psalm)} "
          f"dock_status={status_of(p, pid_dock)}")
    check("A12_sweep_refusals_receipted",
          refusals.get(pid_psalm, {}).get("reason") == "auto_origin_ineligible"
          and refusals.get(pid_dock, {}).get("reason") == "auto_origin_ineligible",
          f"auto_confirm={ac}")
    check("A12_eligible_growth_still_confirms",
          status_of(p, pid_growth) == "confirmed",
          f"growth_status={status_of(p, pid_growth)} auto_confirm={ac}")
    cleanup(owner)


# ---------------------------------------------------------------- A8 store
def store_legs():
    import form.dell_matrix.nursery as nursery_mod
    Nursery = nursery_mod.Nursery
    # Pre-fix these names are absent: fall back to sentinels so the
    # legs report FAIL (attack landed) instead of dying on import.
    NurseryConfirmError = getattr(
        nursery_mod, "NurseryConfirmError", type("Missing", (Exception,), {}))
    CONFIRMATION_RECEIPT_SECTION_KEY = getattr(
        nursery_mod, "CONFIRMATION_RECEIPT_SECTION_KEY",
        "__confirmation_receipts__")
    # A8a — raw confirm with NO actor is refused typed; nothing moves.
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "nursery_a8.json")
        n = Nursery(path=path)
        prop = n.add("fi011 a8 raw store confirm", words="w", kind="new",
                     origin="suite:seeded", reason="fi011 suite")
        refused = None
        try:
            n.confirm(prop.id)
            refused = "NOT REFUSED (returned)"
        except NurseryConfirmError as exc:
            refused = f"NurseryConfirmError: {exc}"
        check("A8_bypass_raw_store_confirm_refused",
              refused.startswith("NurseryConfirmError")
              and n.proposals[prop.id].status == "pending",
              f"outcome={refused} status={n.proposals[prop.id].status}")
        # A8b — confirm WITH an identified actor succeeds and writes
        # an attributed receipt that persists in the store file.
        try:
            out = n.confirm(prop.id, actor="suite:operator")
        except TypeError:
            out = None  # pre-fix door takes no actor at all
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        section = data.get(CONFIRMATION_RECEIPT_SECTION_KEY) or {}
        file_recs = [r for r in section.values()
                     if isinstance(r, dict)
                     and r.get("proposal_id") == prop.id]
        n2 = Nursery.load(path)
        check("A8_attributed_confirm_receipted_and_durable",
              out is not None and out.status == "confirmed"
              and len(file_recs) == 1
              and file_recs[0].get("actor") == "suite:operator"
              and len([r for r in getattr(
                  n2, "confirmation_receipts", {}).values()
                       if r.get("proposal_id") == prop.id]) == 1,
              f"status={out.status if out else None} "
              f"file_receipts={file_recs}")
    # A8c/A11 — save failure inside an authorized confirm reverts
    # status AND retains no receipt; the failure propagates.
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "nursery_a8c.json")
        n = Nursery(path=path)
        prop = n.add("fi011 a8c save failure", words="w", kind="new",
                     origin="suite:seeded", reason="fi011 suite")

        def boom(**kw):
            raise RuntimeError("staged save failure (suite)")

        n.save = boom  # staging only; the revert logic is the target
        try:
            n.confirm(prop.id, actor="suite:operator")
            outcome = "no exception (silent)"
        except RuntimeError:
            outcome = "RuntimeError propagated"
        except TypeError:
            outcome = "TypeError (no actor door)"
        check("A8c_confirm_save_failure_reverts",
              outcome.startswith("RuntimeError")
              and n.proposals[prop.id].status == "pending"
              and len([r for r in getattr(
                  n, "confirmation_receipts", {}).values()
                       if r.get("proposal_id") == prop.id]) == 0,
              f"outcome={outcome} status={n.proposals[prop.id].status}")


def main() -> int:
    print("=== FI011 REMEDIATION WAVE 1 (A7/A8/A12) ===")
    controls()
    replay()
    auto_sweep()
    store_legs()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"FI011_REMEDIATION {passed}/{len(RESULTS)}")
    for name, ok in RESULTS:
        if not ok:
            print(f"  ATTACK LANDED / CONTRACT OPEN: {name}")
    return 0 if passed == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
