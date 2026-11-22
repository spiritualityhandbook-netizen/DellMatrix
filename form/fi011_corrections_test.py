#!/usr/bin/env python3
"""FI-011 corrections — A7 / A8 / A12 / A9 (Director ruling 7085151190
item 1 on issue #512, selecting the remediation packets
FI011_REMEDIATION_PACKETS_2026-11-22).

Failing-first suite for the four selected designs. At the pre-build
head every attack leg FAILs (the Lane C shapes re-measured); after
the build every leg must hold WITHOUT weakening the controls:

- A7 grant replay: presentment binding (target == pid AND
  content_hash == live acceptance hash) for nursery.confirm grants;
  two-phase single-use consumption (reserve -> commit/release) with
  a durable receipt in the owner Nursery store's
  __grant_use_receipts__ section, committed atomically with the
  confirmation; denials/aborted writes never consume; replay refuses
  typed (via="grant_replay"). checkpoint.rollback grants excluded.
- A8 raw Nursery.confirm RETIRED: the direct store door no longer
  exists; the Lane C attack shape gets AttributeError, zero
  mutation, original bytes identical. A grep gate keeps any
  production reference to the retired door out of form/.
- A12 sweep origin eligibility: positive allowlist {"", "repl_user",
  "growth"} enforced on producer == "grow_auto" only, in the
  writer's placement resolution BEFORE the mixed-wall term, refusal
  reason auto_origin_noneligible; sweep reporting gains
  skipped_origin_noneligible + skipped_origin_ids + confirmed_bred.
- A9 load-time status membership: a PRESENT status outside
  {pending, confirmed, rejected} refuses the WHOLE load typed
  (NurseryLoadError naming file/record/value/lawful set), zero
  source mutation; ABSENT status stays legacy pending; a forged
  valid "confirmed" stays inside the disclosed file-tamper boundary
  (pinned, not "fixed").

Labels: INTEGRATION (Program legs) + UNIT (raw store legs on temp
files) + CROSS_PROCESS (A7-T7 crash legs). State hygiene: unique
tagged owners per leg group, loud cleanup; store legs use temp
dirs only.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"CHECK {name}: {'PASS' if ok else 'FAIL'} - {detail}", flush=True)
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


def seed(p, label, origin="repl_user", parents=("w4pa", "w4pb")):
    prop = p.nursery.add(label=label, words=f"words for {label}",
                         kind="new", parents=list(parents),
                         origin=origin, reason="fi011 corrections suite")
    return prop.id


def status_of(p, pid):
    prop = p.nursery.proposals.get(pid)
    return getattr(prop, "status", None)


def grant_receipts(p, pid=None):
    recs = getattr(p.nursery, "grant_use_receipts", {}) or {}
    out = [r for r in recs.values() if isinstance(r, dict)]
    if pid is not None:
        out = [r for r in out if r.get("pid") == pid]
    return out


def manual_confirm(p, pid):
    return p.confirm_proposal(
        pid, _producer="repl_user",
        _review_context=p.make_review_context(pid, "repl_user"))


# ---------------------------------------------------------------- controls
def controls():
    from form.dell_matrix.agent_authority import bind_agent, issue_root_grant
    owner = "FI011CA"
    p = build(owner)
    # C0 - owner manual confirm works; re-confirm is refused.
    pid = seed(p, "fi011 c0 manual control")
    res = manual_confirm(p, pid)
    res2 = manual_confirm(p, pid)
    check("C0_owner_manual_confirm_works",
          bool(res.get("ok")) and status_of(p, pid) == "confirmed"
          and p.cube.session.plane.units.get(pid) is not None
          and not res2.get("ok"),
          f"res_ok={res.get('ok')} re_ok={res2.get('ok')} "
          f"status={status_of(p, pid)}")
    # C1 - fully bound grant, first use works.
    pid2 = seed(p, "fi011 c1 grant control")
    g = issue_root_grant(p, issuer="ace", subject="helper",
                         target=pid2, content_pid=pid2)
    res3 = bind_agent(p, "helper").confirm(pid2, g["grant_id"])
    check("C1_bound_grant_confirm_works",
          bool(res3.get("ok")) and status_of(p, pid2) == "confirmed",
          f"res_ok={res3.get('ok')} status={status_of(p, pid2)}")
    # C2 - denial battery: fabricated / wrong subject / cross-target /
    # revoked all deny with proposals pending.
    pid3 = seed(p, "fi011 c2 target one")
    pid4 = seed(p, "fi011 c2 target two")
    g2 = issue_root_grant(p, issuer="ace", subject="helper",
                          target=pid3, content_pid=pid3)
    ep = bind_agent(p, "helper")
    d_fab = ep.confirm(pid3, "grant_" + "0" * 32)
    d_subj = bind_agent(p, "mallory").confirm(pid3, g2["grant_id"])
    d_cross = ep.confirm(pid4, g2["grant_id"])
    g3 = issue_root_grant(p, issuer="ace", subject="helper",
                          target=pid4, content_pid=pid4)
    p.acceptance_policy.revoke_grant(g3["grant_id"])
    d_rev = ep.confirm(pid4, g3["grant_id"])
    check("C2_grant_denial_battery_holds",
          all(not d.get("ok") for d in (d_fab, d_subj, d_cross, d_rev))
          and status_of(p, pid3) == "pending"
          and status_of(p, pid4) == "pending",
          f"fab={d_fab.get('ok')} subj={d_subj.get('ok')} "
          f"cross={d_cross.get('ok')} rev={d_rev.get('ok')}")
    cleanup(owner)


# ---------------------------------------------------------------- A7
def a7_t1_t4_t9():
    from form.dell_matrix.agent_authority import bind_agent, issue_root_grant
    from form.dell_matrix.nursery import owner_nursery_path
    owner = "FI011CB"
    p = build(owner)
    pid1 = seed(p, "fi011 a7 t1 replay target")
    g = issue_root_grant(p, issuer="ace", subject="helper",
                         target=pid1, content_pid=pid1)
    gid = g["grant_id"]
    seq = p.acceptance_policy._issued_grants[gid]["seq"]
    ep = bind_agent(p, "helper")
    r1 = ep.confirm(pid1, gid)
    r2 = ep.confirm(pid1, gid)
    detail2 = str(r2.get("detail") or "")
    audit = p.acceptance_policy.audit_log()
    check("A7_T1_same_target_replay_denied",
          bool(r1.get("ok")) and not r2.get("ok")
          and r2.get("reason") == "acceptance_policy_denied"
          and "already used to confirm" in detail2 and pid1 in detail2
          and any(e.get("action") == "deny" and e.get("via") == "grant_replay"
                  for e in audit),
          f"first_ok={r1.get('ok')} second_ok={r2.get('ok')} "
          f"detail={detail2!r}")
    # T4 - durable receipt after a full save/load cycle.
    from form.open import Program
    p2 = Program.load(owner)
    recs = grant_receipts(p2, pid1)
    with open(owner_nursery_path(owner), "r", encoding="utf-8") as f:
        blob = f.read()
    data = json.loads(blob)
    section = data.get("__grant_use_receipts__") or {}
    check("A7_T4_durable_receipt_atomic_with_confirmation",
          status_of(p2, pid1) == "confirmed" and len(recs) == 1
          and len(section) == 1
          and recs[0].get("receipt_id") == f"gu_{seq}_{pid1}"
          and recs[0].get("grant_seq") == seq
          and recs[0].get("subject") == "helper"
          and recs[0].get("operation") == "nursery.confirm"
          and bool(recs[0].get("content_hash"))
          and gid not in blob,
          f"recs={recs} section_keys={list(section)}")
    # T9 - operator visibility: describe_grants + audit by seq only.
    desc = {d.get("seq"): d for d in p.acceptance_policy.describe_grants()}
    entry = desc.get(seq) or {}
    check("A7_T9_operator_visibility",
          entry.get("consumed") is True
          and entry.get("receipt_pid") == pid1
          and bool(entry.get("receipt_at"))
          and any(e.get("action") == "grant_use"
                  and e.get("grant_seq") == seq for e in audit)
          and gid not in json.dumps(audit),
          f"desc={entry}")
    cleanup(owner)


def a7_t2():
    from form.dell_matrix.agent_authority import (attenuate_for,
                                                  bind_agent,
                                                  issue_root_grant)
    owner = "FI011CC"
    p = build(owner)
    pid = seed(p, "fi011 a7 t2 unbound target")
    root = issue_root_grant(p, issuer="ace", subject="helper")
    ep = bind_agent(p, "helper")
    r = ep.confirm(pid, root["grant_id"])
    check("A7_T2_unbound_presentment_denied",
          not r.get("ok")
          and "unbound" in str(r.get("detail") or "").lower()
          and status_of(p, pid) == "pending",
          f"ok={r.get('ok')} detail={r.get('detail')!r}")
    child = attenuate_for(p, root["grant_id"], target=pid,
                          content_pid=pid)
    r2 = ep.confirm(pid, child["grant_id"])
    check("A7_T2b_attenuated_child_confirms_after_denial",
          bool(r2.get("ok")) and status_of(p, pid) == "confirmed",
          f"ok={r2.get('ok')}")
    cleanup(owner)


def a7_t3():
    from form.dell_matrix.agent_authority import (attenuate_for,
                                                  bind_agent,
                                                  issue_root_grant)
    owner = "FI011CD"
    p = build(owner)
    pid1 = seed(p, "fi011 a7 t3 first")
    pid2 = seed(p, "fi011 a7 t3 second")
    root = issue_root_grant(p, issuer="ace", subject="helper",
                            max_depth=1)
    child = attenuate_for(p, root["grant_id"], target=pid1,
                          content_pid=pid1)
    ep = bind_agent(p, "helper")
    r1 = ep.confirm(pid1, child["grant_id"])
    r2 = ep.confirm(pid1, child["grant_id"])
    r3 = ep.confirm(pid2, child["grant_id"])
    consumed = getattr(p.acceptance_policy, "_consumed_grants",
                       {}).get(child["grant_id"]) or {}
    check("A7_T3_attenuated_child_single_use",
          bool(r1.get("ok")) and not r2.get("ok")
          and "already used to confirm" in str(r2.get("detail") or "")
          and not r3.get("ok")
          and "target" in str(r3.get("detail") or "").lower()
          and status_of(p, pid2) == "pending"
          and consumed.get("pid") == pid1
          and len(grant_receipts(p)) == 1,
          f"r1={r1.get('ok')} r2={r2.get('ok')} r3={r3.get('ok')} "
          f"consumed={consumed}")
    cleanup(owner)


def a7_t5():
    from form.dell_matrix import confirm_lineage
    from form.dell_matrix.agent_authority import bind_agent, issue_root_grant
    owner = "FI011CE"
    p = build(owner)
    # Leg 1: content mutation after issuance denies; restoring the
    # content makes the SAME grant presentable again (no consumption).
    pid = seed(p, "fi011 a7 t5 mutation target")
    g = issue_root_grant(p, issuer="ace", subject="helper",
                         target=pid, content_pid=pid)
    ep = bind_agent(p, "helper")
    prop = p.nursery.proposals[pid]
    orig_words = prop.words
    prop.words = "mutated after issuance"
    r1 = ep.confirm(pid, g["grant_id"])
    prop.words = orig_words
    r2 = ep.confirm(pid, g["grant_id"])
    check("A7_T5_content_denial_does_not_consume",
          not r1.get("ok") and bool(r2.get("ok"))
          and status_of(p, pid) == "confirmed",
          f"denied_ok={r1.get('ok')} retry_ok={r2.get('ok')}")
    # Leg 2: a writer abort (mid-write content mutation via the
    # stage hook) releases the reservation; the grant confirms after.
    pid2 = seed(p, "fi011 a7 t5 abort target")
    g2 = issue_root_grant(p, issuer="ace", subject="helper",
                          target=pid2, content_pid=pid2)
    prop2 = p.nursery.proposals[pid2]
    orig2 = prop2.words
    state = {"done": False}

    def hook(program, _pid, _auth):
        if not state["done"]:
            state["done"] = True
            prop2.words = orig2 + " mid-write mutation"

    confirm_lineage._BETWEEN_STAGES = hook
    try:
        r3 = ep.confirm(pid2, g2["grant_id"])
    finally:
        confirm_lineage._BETWEEN_STAGES = None
    prop2.words = orig2
    r4 = ep.confirm(pid2, g2["grant_id"])
    check("A7_T5_writer_abort_does_not_consume",
          not r3.get("ok") and bool(r4.get("ok"))
          and status_of(p, pid2) == "confirmed"
          and len(grant_receipts(p, pid2)) == 1,
          f"abort_ok={r3.get('ok')} retry_ok={r4.get('ok')}")
    cleanup(owner)


def a7_t6():
    from form.dell_matrix import confirm_lineage
    from form.dell_matrix.agent_authority import bind_agent, issue_root_grant
    owner = "FI011CF"
    p = build(owner)
    pid = seed(p, "fi011 a7 t6 race target")
    g = issue_root_grant(p, issuer="ace", subject="helper",
                         target=pid, content_pid=pid)
    ep = bind_agent(p, "helper")
    calls = {"n": 0}

    def hook(program, _pid, _auth):
        calls["n"] += 1
        if calls["n"] == 1:
            time.sleep(0.6)

    results = {}

    def run(tag):
        results[tag] = ep.confirm(pid, g["grant_id"])

    confirm_lineage._BETWEEN_STAGES = hook
    try:
        t1 = threading.Thread(target=run, args=("a",))
        t1.start()
        time.sleep(0.25)  # first act is staged + inside the hook
        t2 = threading.Thread(target=run, args=("b",))
        t2.start()
        t1.join(30)
        t2.join(30)
    finally:
        confirm_lineage._BETWEEN_STAGES = None
    oks = [r for r in results.values() if r and r.get("ok")]
    check("A7_T6_concurrent_second_use_blocked",
          len(results) == 2 and len(oks) == 1
          and status_of(p, pid) == "confirmed"
          and len(grant_receipts(p, pid)) == 1
          and p.nursery.summary().get("confirmed") == 1,
          f"results={ {k: (v or {}).get('ok') for k, v in results.items()} } "
          f"receipts={len(grant_receipts(p, pid))}")
    cleanup(owner)


_CHILD = r'''
import json, os, sys
sys.path.insert(0, sys.argv[1])
OWNER = sys.argv[2]
MODE = sys.argv[3]
from form.open import open_program
from form.dell_matrix.agent_authority import bind_agent, issue_root_grant
from form.dell_matrix import confirm_lineage
p = open_program(OWNER)
plane = p.cube.session.plane
plane.units.clear(); plane.sandboxes.clear(); p.nursery.proposals.clear()
p.place("w4pa", "w4 parent a", words="harbor lantern parent a", x=0.0, y=0.0)
p.place("w4pb", "w4 parent b", words="harbor lantern parent b", x=1.0, y=0.0)
prop = p.nursery.add(label="fi011 a7 t7 crash target",
                     words="words for crash target", kind="new",
                     parents=["w4pa", "w4pb"], origin="repl_user",
                     reason="fi011 corrections suite")
g = issue_root_grant(p, issuer="ace", subject="helper",
                     target=prop.id, content_pid=prop.id)
from form import persist_rest
persist_rest.save(p)
print(json.dumps({"pid": prop.id}), flush=True)
if MODE == "die_mid_write":
    confirm_lineage._BETWEEN_STAGES = lambda *a: os._exit(42)
ep = bind_agent(p, "helper")
r = ep.confirm(prop.id, g["grant_id"])
print(json.dumps({"ok": bool(r.get("ok"))}), flush=True)
if MODE == "die_after_commit":
    os._exit(0)
'''


def a7_t7():
    owner = "FI011CG"
    cleanup(owner)
    with tempfile.TemporaryDirectory() as td:
        script = os.path.join(td, "child.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write(_CHILD)
        from form.open import Program
        # Leg 1: killed between staging and commit -> pending, no
        # receipt, baseline state.
        out = subprocess.run(
            [sys.executable, script, REPO, owner, "die_mid_write"],
            capture_output=True, text=True, timeout=120)
        pid = json.loads(out.stdout.strip().splitlines()[0])["pid"]
        p = Program.load(owner)
        check("A7_T7_crash_before_commit_pending_no_receipt",
              out.returncode == 42
              and status_of(p, pid) == "pending"
              and len(grant_receipts(p, pid)) == 0,
              f"rc={out.returncode} status={status_of(p, pid)}")
        cleanup(owner)
        # Leg 2: killed after commit -> confirmed + receipt together.
        out2 = subprocess.run(
            [sys.executable, script, REPO, owner, "die_after_commit"],
            capture_output=True, text=True, timeout=120)
        lines = out2.stdout.strip().splitlines()
        pid2 = json.loads(lines[0])["pid"]
        p2 = Program.load(owner)
        check("A7_T7_crash_after_commit_confirmed_with_receipt",
              out2.returncode == 0
              and json.loads(lines[1]).get("ok") is True
              and status_of(p2, pid2) == "confirmed"
              and len(grant_receipts(p2, pid2)) == 1,
              f"rc={out2.returncode} status={status_of(p2, pid2)} "
              f"receipts={len(grant_receipts(p2, pid2))}")
    cleanup(owner)


def a7_t8():
    owner = "FI011CH"
    p = build(owner)
    pid = seed(p, "fi011 a7 t8 rollback fence")
    policy = p.acceptance_policy
    g = policy.issue_grant(issuer="ace", subject="helper", owner=owner,
                           operation="checkpoint.rollback")
    d = policy.check("agent:helper", pid, {"grant_id": g["grant_id"]},
                     proposal_version=None,
                     operation="checkpoint.rollback",
                     subject="helper", owner=owner)
    check("A7_T8_rollback_grants_excluded",
          d.get("allowed") is True
          and g["grant_id"] not in getattr(policy, "_consumed_grants", {})
          and g["grant_id"] not in getattr(policy, "_reserved_grants", {}),
          f"allowed={d.get('allowed')}")
    cleanup(owner)


# ---------------------------------------------------------------- A8
def a8_legs():
    import form.dell_matrix.nursery as nursery_mod
    Nursery = nursery_mod.Nursery
    # T1 - the Lane C attack verbatim: the old call shape attempted
    # on a loaded store. Post-retirement: AttributeError, proposal
    # pending, file bytes hash-identical.
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "nursery_a8.json")
        n = Nursery(path=path)
        prop = n.add("fi011 a8 raw door target", words="w", kind="new",
                     origin="repl_user", reason="fi011 corrections suite")
        n.save()
        with open(path, "rb") as f:
            before = hashlib.sha256(f.read()).hexdigest()
        outcome = "no error (door live)"
        try:
            n.confirm(prop.id)
            outcome = "returned without error"
        except AttributeError:
            outcome = "AttributeError"
        except Exception as e:
            outcome = f"{type(e).__name__}"
        with open(path, "rb") as f:
            after = hashlib.sha256(f.read()).hexdigest()
        check("A8_T1_retired_door_cannot_mutate",
              outcome == "AttributeError"
              and not hasattr(Nursery, "confirm")
              and n.proposals[prop.id].status == "pending"
              and before == after,
              f"outcome={outcome} status={n.proposals[prop.id].status} "
              f"bytes_same={before == after}")
    # T2 - grep gate: no non-test module under form/ references the
    # retired door (call shape or a re-added method definition).
    form_dir = os.path.join(REPO, "form")
    offenders = []
    for root, _dirs, files in os.walk(form_dir):
        for fn in files:
            if not fn.endswith(".py") or fn.endswith("_test.py"):
                continue
            fp = os.path.join(root, fn)
            with open(fp, "r", encoding="utf-8") as f:
                text = f.read()
            if "nursery.confirm(" in text or ".nursery.confirm(" in text:
                offenders.append(fp)
            if fn == "nursery.py" and re.search(r"def confirm\(", text):
                offenders.append(fp + ":def confirm")
    check("A8_T2_grep_gate_no_production_reference",
          offenders == [], f"offenders={offenders}")
    # T3 - the race suite's N-case re-vehicled onto the property it
    # proves: two instances, one file; the stale instance's mutation
    # is refused with NurseryConflictError + in-memory rollback,
    # exercised through organize_proposal (a real guarded door that
    # rides the same save()).
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "nursery_race.json")
        n0 = Nursery(path=path)
        prop = n0.add("fi011 a8 race target", words="w", kind="new",
                      origin="repl_user", reason="fi011 corrections suite")
        n0.save()
        a = Nursery.load(path)
        b = Nursery.load(path)
        b_topic_before = b.proposals[prop.id].topic
        ra = a.organize_proposal(prop.id, actor="suite:a", topic="alpha")
        outcome_b = "no error"
        try:
            b.organize_proposal(prop.id, actor="suite:b", topic="beta")
        except nursery_mod.NurseryConflictError:
            outcome_b = "NurseryConflictError"
        except Exception as e:
            outcome_b = type(e).__name__
        fresh = Nursery.load(path)
        recs = [r for r in fresh.organization_edit_receipts.values()
                if isinstance(r, dict)
                and r.get("proposal_id") == prop.id]
        check("A8_T3_stale_instance_refusal_via_organize",
              isinstance(ra, dict) and outcome_b == "NurseryConflictError"
              and b.proposals[prop.id].topic == b_topic_before
              and fresh.proposals[prop.id].topic == "alpha"
              and len(recs) == 1,
              f"a_ok={isinstance(ra, dict)} b={outcome_b} "
              f"b_topic={b.proposals[prop.id].topic!r} "
              f"fresh_topic={fresh.proposals[prop.id].topic!r} "
              f"receipts={len(recs)}")


# ---------------------------------------------------------------- A12
def _mixed_parents(p):
    """Parents spanning two walls: w4pa boxed, w4pb outside."""
    plane = p.cube.session.plane
    plane.box(["w4pa"], "vault1", label="fi011 vault")
    return ["w4pa", "w4pb"]


def a12_legs():
    owner = "FI011CJ"
    p = build(owner)
    # T1 - agent/dock origins skipped by the sweep; repl_user control
    # confirmed; reporting names the bucket and the ids.
    pid_ctrl = seed(p, "fi011 a12 t1 control", origin="repl_user")
    pid_agent = seed(p, "fi011 a12 t1 agent", origin="agent:psalm")
    pid_dock = seed(p, "fi011 a12 t1 dock", origin="dock:provider:model")
    p.set_auto_confirm_grow(True)
    res = p.grow_ideas(1)
    ac = res.get("auto_confirm") or {}
    check("A12_T1_agent_dock_skipped_control_confirmed",
          status_of(p, pid_ctrl) == "confirmed"
          and status_of(p, pid_agent) == "pending"
          and status_of(p, pid_dock) == "pending"
          and ac.get("skipped_origin_noneligible") == 2
          and sorted(ac.get("skipped_origin_ids") or [])
              == sorted([pid_agent, pid_dock])
          and ac.get("failed") == 0,
          f"ac={ac}")
    # T2 - a growth-produced child carrying dock authorship is still
    # skipped: origin follows the author, not the mechanism.
    pid_dockchild = seed(p, "fi011 a12 t2 dock child",
                         origin="dock:provider:model")
    res2 = p.grow_ideas(1)
    ac2 = res2.get("auto_confirm") or {}
    check("A12_T2_dock_bred_child_skipped",
          status_of(p, pid_dockchild) == "pending"
          and pid_dockchild in (ac2.get("skipped_origin_ids") or []),
          f"ac={ac2}")
    # T3 - a growth:token child confirms in the sweep and is counted
    # in confirmed_bred; the repl_user confirmation is not.
    owner3 = "FI011CK"
    p3 = build(owner3)
    pid_bred = seed(p3, "fi011 a12 t3 bred", origin="growth:token")
    pid_user = seed(p3, "fi011 a12 t3 user", origin="repl_user")
    p3.set_auto_confirm_grow(True)
    res3 = p3.grow_ideas(1)
    ac3 = res3.get("auto_confirm") or {}
    check("A12_T3_bred_child_confirmed_and_counted",
          status_of(p3, pid_bred) == "confirmed"
          and status_of(p3, pid_user) == "confirmed"
          and (ac3.get("confirmed_bred") or 0) >= 1
          and (ac3.get("confirmed") or 0)
              - (ac3.get("confirmed_bred") or 0) >= 1,
          f"ac={ac3}")
    cleanup(owner3)
    # T4 - manual owner confirm of the exact proposal T1 skipped.
    r4 = manual_confirm(p, pid_agent)
    check("A12_T4_manual_path_untouched",
          bool(r4.get("ok")) and status_of(p, pid_agent) == "confirmed",
          f"ok={r4.get('ok')}")
    # T5 - origin term precedes mixed-wall: a proposal failing both
    # reports the origin reason only.
    pid_t5 = seed(p, "fi011 a12 t5 both", origin="agent:psalm",
                  parents=_mixed_parents(p))
    r5 = p.confirm_proposal(pid_t5, _producer="grow_auto")
    check("A12_T5_origin_term_precedes_mixed_wall",
          not r5.get("ok")
          and r5.get("reason") == "auto_origin_noneligible"
          and status_of(p, pid_t5) == "pending",
          f"reason={r5.get('reason')}")
    # T6 - mixed-wall control unchanged for a human-origin proposal.
    pid_t6 = seed(p, "fi011 a12 t6 mixed", origin="repl_user",
                  parents=["w4pa", "w4pb"])
    r6 = p.confirm_proposal(pid_t6, _producer="grow_auto")
    res6 = p.grow_ideas(1)
    ac6 = res6.get("auto_confirm") or {}
    check("A12_T6_mixed_wall_control_unchanged",
          not r6.get("ok")
          and r6.get("reason") == "auto_mixed_wall_noneligible"
          and pid_t6 in (ac6.get("skipped_ids") or [])
          and status_of(p, pid_t6) == "pending",
          f"reason={r6.get('reason')} ac={ac6}")
    # T7 - legacy "" origin stays sweep-eligible. Seeded
    # parentless: by this point in the shared sequence the w4
    # parents sit on diverged walls, so a default-parents seed
    # would fall to the mixed-wall term instead - this leg
    # isolates the ORIGIN term only.
    pid_t7 = seed(p, "fi011 a12 t7 legacy", origin="", parents=())
    res7 = p.grow_ideas(1)
    check("A12_T7_legacy_empty_origin_eligible",
          status_of(p, pid_t7) == "confirmed",
          f"status={status_of(p, pid_t7)} ac={res7.get('auto_confirm')}")
    # T8 - unknown family is NOT eligible (positive allowlist).
    pid_t8 = seed(p, "fi011 a12 t8 weird", origin="weird:thing")
    r8 = p.confirm_proposal(pid_t8, _producer="grow_auto")
    check("A12_T8_unknown_family_not_eligible",
          not r8.get("ok")
          and r8.get("reason") == "auto_origin_noneligible"
          and status_of(p, pid_t8) == "pending",
          f"reason={r8.get('reason')}")
    # T9 - sweep off / opt-in revoked: nothing confirms.
    pid_t9 = seed(p, "fi011 a12 t9 off", origin="repl_user")
    p.set_auto_confirm_grow(False)
    res9 = p.grow_ideas(1)
    ac9 = res9.get("auto_confirm") or {}
    check("A12_T9_sweep_off_confirms_nothing",
          status_of(p, pid_t9) == "pending" and ac9.get("on") is False,
          f"ac={ac9}")
    # T10 - the origin term does not leak to other producers: a
    # dock-origin proposal confirmed through the grant path is
    # governed by grant law, not the sweep term.
    from form.dell_matrix.agent_authority import bind_agent, issue_root_grant
    # Seeded parentless for the same reason as T7: this leg
    # isolates producer-scoping, not placement.
    pid_t10 = seed(p, "fi011 a12 t10 grant path", origin="dock:x:y",
                   parents=())
    g10 = issue_root_grant(p, issuer="ace", subject="helper",
                           target=pid_t10, content_pid=pid_t10)
    r10 = bind_agent(p, "helper").confirm(pid_t10, g10["grant_id"])
    check("A12_T10_term_scoped_to_grow_auto",
          bool(r10.get("ok")) and status_of(p, pid_t10) == "confirmed",
          f"ok={r10.get('ok')}")
    cleanup(owner)


# ---------------------------------------------------------------- A9
def _nursery_file(td, records_status):
    """Author a nursery file whose records carry the given statuses
    (None = status key absent). Returns (path, [pids])."""
    import form.dell_matrix.nursery as nursery_mod
    path = os.path.join(td, "nursery_a9.json")
    n = nursery_mod.Nursery(path=path)
    pids = []
    for i, _st in enumerate(records_status):
        prop = n.add(f"fi011 a9 record {i}", words="w", kind="new",
                     origin="repl_user", reason="fi011 corrections suite")
        pids.append(prop.id)
    n.save()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for pid, st in zip(pids, records_status):
        if st is None:
            data[pid].pop("status", None)
        else:
            data[pid]["status"] = st
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return path, pids


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def a9_legs():
    import form.dell_matrix.nursery as nursery_mod
    Nursery = nursery_mod.Nursery
    NurseryLoadError = nursery_mod.NurseryLoadError
    # T1 - unknown status refused typed; bytes unchanged.
    with tempfile.TemporaryDirectory() as td:
        path, pids = _nursery_file(td, ["bogus_status_value"])
        before = _sha(path)
        err = None
        try:
            Nursery.load(path)
        except NurseryLoadError as e:
            err = str(e)
        check("A9_T1_unknown_status_refused_typed",
              err is not None and pids[0] in err
              and "bogus_status_value" in err and "pending" in err
              and "confirmed" in err and "rejected" in err
              and _sha(path) == before,
              f"err={err!r}")
    # T2 - one bad record refuses the WHOLE load.
    with tempfile.TemporaryDirectory() as td:
        path, pids = _nursery_file(
            td, ["pending", "confirmed", "rejected", "bogus_status_value"])
        before = _sha(path)
        err = None
        try:
            Nursery.load(path)
        except NurseryLoadError as e:
            err = str(e)
        check("A9_T2_one_bad_record_refuses_whole_load",
              err is not None and pids[3] in err and _sha(path) == before,
              f"err={err!r}")
    # T3 - absent status defaults to legacy pending.
    with tempfile.TemporaryDirectory() as td:
        path, pids = _nursery_file(td, [None])
        n = Nursery.load(path)
        check("A9_T3_absent_status_defaults_pending",
              n.proposals[pids[0]].status == "pending"
              and n.summary()["pending"] == 1,
              f"summary={n.summary()}")
    # T4 - the lawful set loads; the accounting invariant holds.
    with tempfile.TemporaryDirectory() as td:
        path, pids = _nursery_file(td, ["pending", "confirmed", "rejected"])
        n = Nursery.load(path)
        s = n.summary()
        check("A9_T4_lawful_set_loads_invariant_holds",
              s["pending"] + s["confirmed"] + s["rejected"] == s["total"] == 3,
              f"summary={s}")
    # T5 - torn file still refuses (Lane C A9c control re-run).
    with tempfile.TemporaryDirectory() as td:
        path, pids = _nursery_file(td, ["pending"])
        with open(path, "rb") as f:
            blob = f.read()
        with open(path, "wb") as f:
            f.write(blob[: len(blob) // 2])
        err = None
        try:
            Nursery.load(path)
        except NurseryLoadError as e:
            err = str(e)
        check("A9_T5_torn_file_still_refuses", err is not None,
              f"err={err!r}")
    # T6 - a stale instance cannot resave over a refused file; a
    # second owner's file is untouched throughout.
    with tempfile.TemporaryDirectory() as td:
        path, pids = _nursery_file(td, ["pending"])
        stale = Nursery.load(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data[pids[0]]["status"] = "bogus_status_value"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        before = _sha(path)
        load_err = None
        try:
            Nursery.load(path)
        except NurseryLoadError as e:
            load_err = str(e)
        save_outcome = "no error"
        try:
            stale.save()
        except nursery_mod.NurseryConflictError:
            save_outcome = "NurseryConflictError"
        except Exception as e:
            save_outcome = type(e).__name__
        path_b = os.path.join(td, "nursery_b.json")
        nb = nursery_mod.Nursery(path=path_b)
        nb.add("fi011 a9 owner b", words="w", kind="new",
               origin="repl_user", reason="fi011 corrections suite")
        nb.save()
        nb2 = Nursery.load(path_b)
        check("A9_T6_resave_cannot_drop_original",
              load_err is not None
              and save_outcome == "NurseryConflictError"
              and _sha(path) == before
              and nb2.summary()["total"] == 1,
              f"load_err={'yes' if load_err else 'no'} save={save_outcome}")
    # T7 - forged VALID "confirmed" still loads: the retained
    # file-tamper boundary, pinned deliberately.
    with tempfile.TemporaryDirectory() as td:
        path, pids = _nursery_file(td, ["confirmed"])
        n = Nursery.load(path)
        check("A9_T7_forged_lawful_value_boundary_pinned",
              n.proposals[pids[0]].status == "confirmed"
              and n.summary()["confirmed"] == 1,
              f"summary={n.summary()}")
    # T8 - lifecycle_state is NOT status: untouched by the check.
    with tempfile.TemporaryDirectory() as td:
        path, pids = _nursery_file(td, ["confirmed"])
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data[pids[0]]["lifecycle_state"] = "superseded"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        n = Nursery.load(path)
        check("A9_T8_lifecycle_state_untouched",
              n.proposals[pids[0]].status == "confirmed"
              and n.proposals[pids[0]].lifecycle_state == "superseded",
              f"lifecycle={n.proposals[pids[0]].lifecycle_state!r}")
    # Negative controls: present-but-empty, non-string, case variant.
    for label, bad in (("empty", ""), ("nonstr", 123),
                       ("case", "Confirmed")):
        with tempfile.TemporaryDirectory() as td:
            path, pids = _nursery_file(td, [bad])
            err = None
            try:
                Nursery.load(path)
            except NurseryLoadError as e:
                err = str(e)
            check(f"A9_NEG_status_{label}_refused", err is not None,
                  f"err={err!r}")


def main() -> int:
    print("=== FI-011 CORRECTIONS (A7/A8/A12/A9) ===")
    controls()
    a7_t1_t4_t9()
    a7_t2()
    a7_t3()
    a7_t5()
    a7_t6()
    a7_t7()
    a7_t8()
    a8_legs()
    a12_legs()
    a9_legs()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"FI011_CORRECTIONS {passed}/{len(RESULTS)}")
    for name, ok in RESULTS:
        if not ok:
            print(f"  FAILING: {name}")
    return 0 if passed == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
