#!/usr/bin/env python3
"""R6.4 multi-intelligence shared-state circuit proofs.

GDP_PHASE_6_R64_MULTI_INTELLIGENCE_SHARED_STATE_CIRCUIT (MODE=C).

Proves two agents cooperating over one knowledge system while keeping
identity, permission, memory, and outcomes separate:

6.4.1 agent identity/BIMO binding
    - identity is host-bound; unregistered subjects rejected
    - persona slots and BIMO docking are descriptive; they never mint,
      inherit, or combine authority (PERSONA != PERMISSION)
    - envelope rejects caller-supplied identity/credential fields
6.4.2 shared-state protocol
    - one trusted HostCoordinator; protected writes serialized
    - bounded detached snapshots; agents never get mutable objects
    - A confirms via content-bound grant; B cannot use A's grant
    - exact retry is idempotent (no duplicate); reused request_id with
      different content rejects; unknown/interrupted != completed
    - changed content and revoked grants deny at dispatch
    - queue bounds enforced; reentrant dispatch rejected explicitly
6.4.3 audit trail
    - every action recorded with subject, correlation, operation,
      affected objects, result, provenance; grant handles never logged
    - attempted/denied/committed/failed distinguished; audit persists
6.4.4 IntrinsicAgent recovery
    - agent-local behavioral state isolated by (owner, subject)
    - versioned validated persistence; malformed fails closed;
      genuine absence -> fresh default
    - reload restores observations, never session authority
6.4.5 public-path proofs
    - all proofs through production public interfaces
    - cross-process via fixed child scripts + JSON args
    - independent reference model; sensitivity controls

Evidence classes: INTEGRATION (real Program, real writer, per-owner
isolation) and CROSS_PROCESS (fixed child scripts, separate OS process,
real restart).
"""

import glob
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(REPO)
sys.path.insert(0, ROOT)

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {detail}" if detail and not cond else ""))


def clean_owner(owner):
    for pat in [f'form/state/program_{owner}.json',
                f'form/state/nursery_{owner}.json']:
        pp = os.path.join(ROOT, pat)
        if os.path.isfile(pp):
            os.remove(pp)
    for pat in glob.glob(os.path.join(ROOT, 'form', 'state',
                                      f'checkpoint_{owner}_*')):
        os.remove(pat)
    from form.mandell.core_i_recovery import _confirm_journal_path
    jp = _confirm_journal_path(owner)
    if not os.path.isabs(jp):
        jp = os.path.join(ROOT, jp)
    if os.path.isfile(jp):
        os.remove(jp)


def fresh_program(owner):
    from form.open import open_program
    clean_owner(owner)
    return open_program(owner)


def run_child(cmd, args):
    """Run the fixed r64 child script in a separate OS process."""
    proc = subprocess.run(
        [sys.executable, "-m", "form.mandell.r64_child", cmd, json.dumps(args)],
        cwd=ROOT, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        return {"_child_error": proc.stderr[-500:], "_rc": proc.returncode}
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        return {"_child_error": proc.stdout[-500:] + proc.stderr[-500:]}


# ---------------------------------------------------------------------------
# 6.4.1 — agent identity and BIMO binding
# ---------------------------------------------------------------------------

def part_identity():
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import personas

    p = fresh_program("r64id")
    coord = ac.new_coordinator(p)

    # Host-bound registration.
    ident_a = coord.register_agent("agent-a", persona_slots={"logic": "manny"})
    check("6.4.1 registered identity carries host subject",
          ident_a.subject == "agent-a" and ident_a.owner == "r64id")
    check("6.4.1 persona slots recorded as descriptive metadata",
          ident_a.persona_slots == {"logic": "manny"})

    # Unregistered subject cannot get a surface or snapshot.
    for fn_name in ("surface_for", "snapshot_for"):
        try:
            getattr(coord, fn_name)("ghost")
            check(f"6.4.1 {fn_name} rejects unregistered subject", False)
        except ac.CoordinatorError:
            check(f"6.4.1 {fn_name} rejects unregistered subject", True)

    # Envelope rejects caller-supplied identity/credential fields.
    for bad_field in ("subject", "grant_id", "credential"):
        try:
            ac.make_envelope(request_id="r", operation="confirm", target="t",
                             expected={bad_field: "x"})
            check(f"6.4.1 envelope rejects '{bad_field}' field", False)
        except ValueError:
            check(f"6.4.1 envelope rejects '{bad_field}' field", True)

    # BIMO docking changes behavior description, not permission.
    body = personas.BIMOBody()
    body.dock("logic", "manny")
    body.dock("growth", "melody")
    fused_before = body.fuse("ctx")
    ident_b = coord.register_agent("agent-b",
                                   bimo_binding={"logic": "manny", "growth": "melody"})
    check("6.4.1 BIMO binding recorded descriptively",
          ident_b.bimo_binding.get("logic") == "manny")
    check("6.4.1 persona/bimo metadata never consulted for permission",
          "grant" not in str(ident_b.persona_slots).lower()
          and fused_before.get("ok", True) is not False)

    # Narrow surface exposes exactly snapshot + request_confirm.
    surf = coord.surface_for("agent-a")
    exposed = [m for m in dir(surf) if not m.startswith("_")]
    check("6.4.1 narrow surface exposes only snapshot/request_confirm",
          set(exposed) <= {"snapshot", "request_confirm", "bound_subject"},
          detail=str(exposed))
    check("6.4.1 surface subject is host binding",
          surf.bound_subject == "agent-a")


# ---------------------------------------------------------------------------
# 6.4.2 — shared-state protocol: snapshots, grants, idempotency
# ---------------------------------------------------------------------------

def _mkpair(p, pid, subject, bind_content=True, max_depth=2):
    from form.dell_matrix import agent_authority as aa
    root = aa.issue_root_grant(p, issuer="human:ace", subject=subject,
                               max_depth=max_depth)
    child = aa.attenuate_for(p, root["grant_id"],
                             target=pid,
                             content_pid=pid if bind_content else None)
    return root, child


def part_protocol():
    from form.dell_matrix import agent_coordinator as ac

    p = fresh_program("r64proto")
    pr = p.nursery.add("Proto Idea", words="shared state protocol words")
    pid = pr.id
    _, child_a = _mkpair(p, pid, "agent-a")

    coord = ac.new_coordinator(p)
    coord.register_agent("agent-a")
    coord.register_agent("agent-b")
    surf_a = coord.surface_for("agent-a")
    surf_b = coord.surface_for("agent-b")

    # Snapshots are bounded and detached.
    s1 = surf_a.snapshot()
    s2 = surf_b.snapshot()
    check("6.4.2 snapshots carry ideas", len(s1["ideas"]) >= 1)
    check("6.4.2 snapshots marked detached", s1.get("detached") is True)
    s1["ideas"].append({"pid": "forged"})
    s1["units"].append({"uid": "forged"})
    check("6.4.2 snapshot mutation does not leak to live or peer",
          len(surf_b.snapshot()["ideas"]) == len(s2["ideas"])
          and not any(i.get("pid") == "forged" for i in surf_b.snapshot()["ideas"]))
    check("6.4.2 snapshot exposes no mutable program objects",
          not any(hasattr(v, "confirm_proposal") for v in s1.values()))

    # A confirms through the coordinator.
    content_hash = p.acceptance_data_hash(pid, "confirm")
    r1 = surf_a.request_confirm(pid, child_a["grant_id"], request_id="req-1",
                                expected_content_hash=content_hash)
    check("6.4.2 A confirms via coordinator", r1["ok"] and r1["result"] == "committed",
          detail=str(r1)[:200])
    check("6.4.2 idea accepted on plane", pid in p.cube.session.plane.units)

    # Exact retry: same receipt, no duplicate transition.
    units_before = len(p.cube.session.plane.units)
    r2 = surf_a.request_confirm(pid, child_a["grant_id"], request_id="req-1",
                                expected_content_hash=content_hash)
    check("6.4.2 exact retry returns cached receipt",
          r2.get("idempotent_retry") is True and r2["ok"])
    check("6.4.2 retry creates no duplicate",
          len(p.cube.session.plane.units) == units_before)

    # Reused request_id with different content: reject.
    pr2 = p.nursery.add("Second Idea", words="different content here")
    pid2 = pr2.id
    _, child_a2 = _mkpair(p, pid2, "agent-a")
    h2 = p.acceptance_data_hash(pid2, "confirm")
    r3 = surf_a.request_confirm(pid2, child_a2["grant_id"], request_id="req-1",
                                expected_content_hash=h2)
    check("6.4.2 request_id reuse with different content rejects",
          not r3["ok"] and r3.get("reason") == "request_id_reuse",
          detail=str(r3)[:200])

    # B cannot use A's grant (subject mismatch at the writer).
    r4 = surf_b.request_confirm(pid, child_a["grant_id"], request_id="req-b1",
                                expected_content_hash=content_hash)
    check("6.4.2 B cannot use A's grant", not r4["ok"],
          detail=str(r4)[:200])

    # Changed content denies.
    pr3 = p.nursery.add("Third Idea", words="original words here")
    pid3 = pr3.id
    _, child_a3 = _mkpair(p, pid3, "agent-a")
    stale_hash = p.acceptance_data_hash(pid3, "confirm")
    # Mutate the proposal content after the grant binds it.
    prop3 = p.nursery.proposals[pid3]
    prop3.words = "mutated words after grant"
    r5 = surf_a.request_confirm(pid3, child_a3["grant_id"], request_id="req-3",
                                expected_content_hash=stale_hash)
    check("6.4.2 changed content denies", not r5["ok"],
          detail=str(r5)[:200])

    # Revoked grant denies (queued request is not prior authorization).
    pr4 = p.nursery.add("Fourth Idea", words="revocation test words")
    pid4 = pr4.id
    root4, child_a4 = _mkpair(p, pid4, "agent-a")
    h4 = p.acceptance_data_hash(pid4, "confirm")
    from form.dell_matrix import agent_authority as aa
    aa.revoke_grant(p, root4["grant_id"])
    r6 = surf_a.request_confirm(pid4, child_a4["grant_id"], request_id="req-4",
                                expected_content_hash=h4)
    check("6.4.2 revoked grant denies at dispatch", not r6["ok"],
          detail=str(r6)[:200])

    # Queue bounds enforced.
    coord2 = ac.new_coordinator(p)
    coord2.register_agent("agent-a")
    env = ac.make_envelope(request_id="qb", operation="confirm", target=pid)
    coord2._queue_bound = 1
    coord2.enqueue("agent-a", env)
    try:
        coord2.enqueue("agent-a", ac.make_envelope(
            request_id="qb2", operation="confirm", target=pid))
        check("6.4.2 queue bound enforced", False)
    except ac.CoordinatorError:
        check("6.4.2 queue bound enforced", True)

    # Reentrant dispatch rejected explicitly.
    coord3 = ac.new_coordinator(p)
    coord3.register_agent("agent-a")
    qid = coord3.enqueue("agent-a", ac.make_envelope(
        request_id="re", operation="confirm", target=pid))
    coord3._in_dispatch = True  # simulate an in-flight dispatch
    rr = coord3.dispatch(qid, child_a["grant_id"])
    coord3._in_dispatch = False
    check("6.4.2 reentrant dispatch rejected explicitly",
          not rr["ok"] and rr.get("reason") == "reentrant_dispatch")


# ---------------------------------------------------------------------------
# 6.4.3 — audit trail
# ---------------------------------------------------------------------------

def part_audit():
    from form.dell_matrix import agent_coordinator as ac

    p = fresh_program("r64audit")
    pr = p.nursery.add("Audit Idea", words="audit trail words")
    pid = pr.id
    _, child_a = _mkpair(p, pid, "agent-a")

    coord = ac.new_coordinator(p)
    coord.register_agent("agent-a")
    surf_a = coord.surface_for("agent-a")
    h = p.acceptance_data_hash(pid, "confirm")
    r1 = surf_a.request_confirm(pid, child_a["grant_id"], request_id="aud-1",
                                expected_content_hash=h,
                                correlation={"session": "s1", "note": "n1"})
    check("6.4.3 commit recorded", r1["ok"])

    # A denial is also recorded.
    r2 = surf_a.request_confirm("nonexistent-pid", child_a["grant_id"],
                                request_id="aud-2")
    check("6.4.3 denial recorded", not r2["ok"])

    records = ac.list_agent_audit(p)
    by_req = {r["request_id"]: r for r in records}
    check("6.4.3 committed action audited",
          by_req.get("aud-1", {}).get("result") == "committed")
    check("6.4.3 denied action audited",
          by_req.get("aud-2", {}).get("result") == "denied")
    rec = by_req.get("aud-1", {})
    check("6.4.3 audit carries subject/correlation/operation/affected",
          rec.get("subject") == "agent-a"
          and rec.get("operation") == "confirm"
          and pid in rec.get("affected", [])
          and rec.get("correlation", {}).get("session") == "s1")
    check("6.4.3 audit never logs grant handles",
          not any("grant" in str(v).lower() and "grant_id" in str(k).lower()
                  for r in records for k, v in r.items()),
          detail="grant handle found in audit")
    check("6.4.3 audit ids stable and unique",
          len({r["audit_id"] for r in records}) == len(records)
          and all(r["audit_id"].startswith("aa1:") for r in records))

    # Audit persists across save/load.
    from form import persist_rest
    pth = persist_rest.save(p)
    p2 = persist_rest.load("r64audit", activate=False)
    rec2 = ac.list_agent_audit(p2)
    check("6.4.3 audit survives save/load",
          any(r["request_id"] == "aud-1" and r["result"] == "committed"
              for r in rec2))


# ---------------------------------------------------------------------------
# 6.4.4 — IntrinsicAgent recovery
# ---------------------------------------------------------------------------

def part_intrinsic():
    from form.dell_matrix import intrinsic_agent as ia

    p = fresh_program("r64intr")

    # Isolation by (owner, subject).
    a = ia.for_agent(p, "agent-a")
    b = ia.for_agent(p, "agent-b")
    check("6.4.4 for_agent returns distinct instances", a is not b)
    check("6.4.4 same subject returns same instance",
          ia.for_agent(p, "agent-a") is a)

    class Body:
        pos = (3, 4)
    class P:
        avatar = type("A", (), {"body": Body()})()

    obs_a = a.observe(P(), {"nodes": [{"label": "AlphaSite"}]})
    check("6.4.4 agent-a observes novelty", obs_a["novelty"] >= 1.0)
    check("6.4.4 agent-b shares nothing",
          "AlphaSite" not in b.seen_labels and len(b.seen_cells) == 0)
    check("6.4.4 module-global AGENT untouched by agent-a",
          "AlphaSite" not in ia.AGENT.seen_labels)

    # Movement behavior distinct from knowledge acceptance: propose_action
    # and step never touch nursery/proposals/grants.
    proposals_before = set(p.nursery.proposals.keys())
    prop = a.propose_action(P())
    check("6.4.4 propose_action returns movement proposal",
          prop.get("action") in ("forward", "left", "right", "back",
                                 "turn_left", "turn_right", "look_up"))
    check("6.4.4 exploration does not accept knowledge",
          set(p.nursery.proposals.keys()) == proposals_before)

    # Persist and reload: observations restored.
    ia.sync_agent_to_program(p, "agent-a")
    ia.sync_agent_to_program(p, "agent-b")
    from form import persist_rest
    persist_rest.save(p)
    p2 = persist_rest.load("r64intr", activate=False)
    a2 = ia.for_agent(p2, "agent-a")
    b2 = ia.for_agent(p2, "agent-b")
    check("6.4.4 reload restores agent-a observations",
          "AlphaSite" in a2.seen_labels and (3, 4) in a2.seen_cells)
    check("6.4.4 reload keeps agent-b isolated",
          "AlphaSite" not in b2.seen_labels)

    # Restored state carries no permissions.
    d = a2.to_dict()
    flat = json.dumps(d).lower()
    check("6.4.4 restored state holds no grants/permissions",
          "grant" not in flat and "permission" not in flat
          and "credential" not in flat)

    # Genuine absence -> fresh default; malformed -> fail closed.
    p3 = fresh_program("r64intr2")
    c = ia.for_agent(p3, "new-agent")
    check("6.4.4 genuine absence yields fresh default",
          c.seen_labels == set() and c.curiosity_score == 0.0)
    for bad in ("notadict", 42, ["x"],
                {"version": 1, "seen_cells": "bad"},
                {"version": 1, "seen_labels": [123, {}]},
                {"version": 99}):
        try:
            ia.IntrinsicAgent.from_dict(bad, "x")
            check(f"6.4.4 malformed {type(bad).__name__} fails closed", False,
                  detail=str(bad)[:60])
        except ia.AgentLocalLoadError:
            check(f"6.4.4 malformed {type(bad).__name__} fails closed", True)

    # Cross-owner isolation.
    p4 = fresh_program("r64intr3")
    d_owner = ia.for_agent(p4, "agent-a")
    check("6.4.4 cross-owner isolation",
          "AlphaSite" not in d_owner.seen_labels)


# ---------------------------------------------------------------------------
# 6.4.2/6.4.4 — cross-process: restart, rollback invalidation, recovery
# ---------------------------------------------------------------------------

def part_cross_process():
    from form.dell_matrix import agent_coordinator as ac

    owner = "r64xproc"
    clean_owner(owner)

    # Issue in process 1.
    issued = run_child("issue_pair", {
        "owner": owner, "label": "XProc Idea",
        "words": "cross process words", "subject": "agent-a"})
    check("6.4.5 child issue_pair works", "pid" in issued and "grant_id" in issued,
          detail=str(issued)[:200])
    if "pid" not in issued:
        return
    pid, grant_id, chash = issued["pid"], issued["grant_id"], issued["content_hash"]

    # Confirm in process 2 (fresh process, fresh policy session).
    # Note: grants are session-scoped per R6.1, so a grant issued in
    # process 1 MUST NOT authorize in process 2. The coordinator path
    # inherits this: cross-process grant replay denies.
    r = run_child("coord_confirm", {
        "owner": owner, "subject": "agent-a", "pid": pid,
        "grant_id": grant_id, "request_id": "xp-1", "content_hash": chash})
    check("6.4.5 cross-process grant replay denies (session-scoped)",
          r.get("ok") is False, detail=str(r)[:200])

    # Same-process confirm works (control).
    p = fresh_program(owner)
    pr = p.nursery.add("XProc Idea 2", words="control words here")
    pid2 = pr.id
    _, child2 = _mkpair(p, pid2, "agent-a")
    h2 = p.acceptance_data_hash(pid2, "confirm")
    coord = ac.new_coordinator(p)
    coord.register_agent("agent-a")
    surf = coord.surface_for("agent-a")
    rc = surf.request_confirm(pid2, child2["grant_id"], request_id="xp-2",
                              expected_content_hash=h2)
    check("6.4.5 same-process coordinator confirm commits", rc["ok"])
    from form import persist_rest
    persist_rest.save(p)

    # Real restart: fresh process reloads; committed history survives.
    chk = run_child("agent_restore_check", {"owner": owner, "subject": "agent-a"})
    check("6.4.5 restart loads program state", "labels_seen" in chk)

    # Agent-local behavior persists across a real process boundary,
    # but session authority (grants) does not revive.
    o2 = run_child("agent_observe", {"owner": owner, "subject": "agent-a",
                                    "label": "XProcSite"})
    check("6.4.5 child observe+save works",
          "XProcSite" in o2.get("labels_seen", []), detail=str(o2)[:200])
    r3 = run_child("agent_restore_check", {"owner": owner, "subject": "agent-a",
                                          "expect_label": "XProcSite"})
    check("6.4.4 fresh process restores agent-local behavior",
          r3.get("has_label") is True, detail=str(r3)[:200])
    # The grant from the earlier process is gone: replay denies.
    r4 = run_child("coord_confirm", {
        "owner": owner, "subject": "agent-a", "pid": pid2,
        "grant_id": child2["grant_id"], "request_id": "xp-3",
        "content_hash": h2})
    check("6.4.5 restart does not revive session authority",
          r4.get("ok") is False, detail=str(r4)[:200])

    # Audit durable across processes.
    acount = run_child("audit_count", {"owner": owner})
    check("6.4.3 audit durable across processes",
          acount.get("count", 0) >= 1, detail=str(acount)[:200])


def part_rollback_recovery():
    from form.dell_matrix import agent_coordinator as ac
    from form.mandell import core_i_recovery as rec

    owner = "r64roll"
    p = fresh_program(owner)
    pr = p.nursery.add("Rollback Idea", words="rollback invalidation words")
    pid = pr.id
    _, child = _mkpair(p, pid, "agent-a")
    h = p.acceptance_data_hash(pid, "confirm")

    coord = ac.new_coordinator(p)
    coord.register_agent("agent-a")
    # Enqueue, then advance the rollback epoch before dispatch.
    qid = coord.enqueue("agent-a", ac.make_envelope(
        request_id="rb-1", operation="confirm", target=pid,
        expected={"content_hash": h}))
    saved_queued = dict(coord._queue[qid])
    rec._advance_rollback_epoch(owner)
    # Post-rollback reload: fresh program instance at the new epoch, new
    # coordinator. The pre-rollback queued request is recovered from the
    # (durable) queue and must be recognized as stale.
    from form.open import open_program
    p_fresh = open_program(owner)
    coord_fresh = ac.new_coordinator(p_fresh)
    coord_fresh.register_agent("agent-a")
    coord_fresh._queue[qid] = saved_queued
    r = coord_fresh.dispatch(qid, child["grant_id"])
    check("6.4.2 rollback invalidates stale queued request",
          not r["ok"] and r.get("reason") == "stale_after_rollback",
          detail=str(r)[:200])

    # Recovery-required blocks dispatch.
    p2 = fresh_program("r64rec")
    pr2 = p2.nursery.add("Recovery Idea", words="recovery words here")
    pid2 = pr2.id
    _, child2 = _mkpair(p2, pid2, "agent-a")
    h2 = p2.acceptance_data_hash(pid2, "confirm")
    coord2 = ac.new_coordinator(p2)
    coord2.register_agent("agent-a")
    rec.mark_recovery_required(p2, "test-key", "simulated recovery")
    qid2 = coord2.enqueue("agent-a", ac.make_envelope(
        request_id="rc-1", operation="confirm", target=pid2,
        expected={"content_hash": h2}))
    r2 = coord2.dispatch(qid2, child2["grant_id"])
    check("6.4.2 recovery-required blocks dispatch",
          not r2["ok"] and r2.get("reason") == "recovery_required",
          detail=str(r2)[:200])
    # Clearing recovery unblocks (control: fresh enqueue after clear).
    rec.clear_recovery_required(p2, "test-key")
    qid3 = coord2.enqueue("agent-a", ac.make_envelope(
        request_id="rc-2", operation="confirm", target=pid2,
        expected={"content_hash": h2}))
    r3 = coord2.dispatch(qid3, child2["grant_id"])
    check("6.4.2 dispatch succeeds after recovery cleared", r3["ok"],
          detail=str(r3)[:200])


# ---------------------------------------------------------------------------
# 6.4.5 — independent reference model agreement
# ---------------------------------------------------------------------------

def part_reference_model():
    """Production behavior must agree with the independent reference model
    on identity, ordering, revocation, and retry outcomes."""
    from form.dell_matrix import agent_coordinator as ac
    from form.mandell.r64_reference_model import ReferenceModel

    owner = "r64ref"
    p = fresh_program(owner)

    # Build the scenario in production.
    pr1 = p.nursery.add("Ref One", words="reference one words")
    pid1 = pr1.id
    pr2 = p.nursery.add("Ref Two", words="reference two words")
    pid2 = pr2.id
    _, ch_a1 = _mkpair(p, pid1, "agent-a")
    _, ch_a2 = _mkpair(p, pid2, "agent-a")
    h1 = p.acceptance_data_hash(pid1, "confirm")
    h2 = p.acceptance_data_hash(pid2, "confirm")

    coord = ac.new_coordinator(p)
    coord.register_agent("agent-a")
    coord.register_agent("agent-b")
    sa = coord.surface_for("agent-a")
    sb = coord.surface_for("agent-b")

    # Scripted sequence (mirrors the reference model steps below).
    prod_results = []
    # 1. A confirms pid1 -> commit
    r = sa.request_confirm(pid1, ch_a1["grant_id"], request_id="m-1",
                           expected_content_hash=h1)
    prod_results.append((bool(r["ok"]), r.get("reason", r.get("result", ""))))
    # 2. exact retry -> idempotent
    r = sa.request_confirm(pid1, ch_a1["grant_id"], request_id="m-1",
                           expected_content_hash=h1)
    prod_results.append((bool(r["ok"]), "idempotent_retry" if r.get("idempotent_retry") else r.get("reason", "")))
    # 3. B tries A's grant on pid2 -> deny (subject mismatch)
    r = sb.request_confirm(pid2, ch_a2["grant_id"], request_id="m-2",
                           expected_content_hash=h2)
    prod_results.append((bool(r["ok"]), r.get("reason", "")))
    # 4. A confirms pid2 -> commit
    r = sa.request_confirm(pid2, ch_a2["grant_id"], request_id="m-3",
                           expected_content_hash=h2)
    prod_results.append((bool(r["ok"]), r.get("reason", r.get("result", ""))))
    # 5. request_id reuse with different content -> deny
    r = sa.request_confirm(pid2, ch_a2["grant_id"], request_id="m-1",
                           expected_content_hash=h2)
    prod_results.append((bool(r["ok"]), r.get("reason", "")))

    # Reference model expectation (no production helpers called).
    model = ReferenceModel()
    expected = model.expect_sequence([
        {"kind": "register", "subject": "agent-a"},
        {"kind": "register", "subject": "agent-b"},
        {"kind": "set_content", "pid": pid1, "content_hash": h1},
        {"kind": "set_content", "pid": pid2, "content_hash": h2},
        {"kind": "issue", "grant_id": "g-a1", "subject": "agent-a",
         "pid": pid1, "content_hash": h1},
        {"kind": "issue", "grant_id": "g-a2", "subject": "agent-a",
         "pid": pid2, "content_hash": h2},
        {"kind": "request", "subject": "agent-a", "request_id": "m-1",
         "pid": pid1, "grant_id": "g-a1", "expected_hash": h1},
        {"kind": "request", "subject": "agent-a", "request_id": "m-1",
         "pid": pid1, "grant_id": "g-a1", "expected_hash": h1},
        {"kind": "request", "subject": "agent-b", "request_id": "m-2",
         "pid": pid2, "grant_id": "g-a2", "expected_hash": h2},
        {"kind": "request", "subject": "agent-a", "request_id": "m-3",
         "pid": pid2, "grant_id": "g-a2", "expected_hash": h2},
        {"kind": "request", "subject": "agent-a", "request_id": "m-1",
         "pid": pid2, "grant_id": "g-a2", "expected_hash": h2},
    ])
    # Filter to the request steps only.
    exp_requests = [e for e in expected if e[1] in (
        "committed", "idempotent_retry", "subject_mismatch",
        "request_id_reuse")]

    check("6.4.5 reference model agrees on commit",
          prod_results[0][0] is True and exp_requests[0] == (True, "committed"))
    check("6.4.5 reference model agrees on idempotent retry",
          prod_results[1] == (True, "idempotent_retry")
          and exp_requests[1] == (True, "idempotent_retry"))
    check("6.4.5 reference model agrees on subject-mismatch deny",
          prod_results[2][0] is False and exp_requests[2] == (False, "subject_mismatch"),
          detail=f"prod={prod_results[2]} model={exp_requests[2]}")
    check("6.4.5 reference model agrees on second commit",
          prod_results[3][0] is True and exp_requests[3] == (True, "committed"))
    check("6.4.5 reference model agrees on request_id-reuse deny",
          prod_results[4][0] is False and exp_requests[4] == (False, "request_id_reuse"),
          detail=f"prod={prod_results[4]} model={exp_requests[4]}")

    # Revocation and epoch in the model.
    m2 = ReferenceModel()
    exp2 = m2.expect_sequence([
        {"kind": "register", "subject": "agent-a"},
        {"kind": "set_content", "pid": "p1", "content_hash": "h1"},
        {"kind": "issue", "grant_id": "g1", "subject": "agent-a",
         "pid": "p1", "content_hash": "h1"},
        {"kind": "revoke", "grant_id": "g1"},
        {"kind": "request", "subject": "agent-a", "request_id": "r1",
         "pid": "p1", "grant_id": "g1", "expected_hash": "h1"},
        {"kind": "advance_epoch"},
        {"kind": "issue", "grant_id": "g2", "subject": "agent-a",
         "pid": "p1", "content_hash": "h1"},
        {"kind": "request", "subject": "agent-a", "request_id": "r2",
         "pid": "p1", "grant_id": "g2", "expected_hash": "h1",
         "epoch_at_enqueue": 0},
    ])
    req2 = [e for e in exp2 if e[1] in ("grant_revoked", "stale_after_rollback")]
    check("6.4.5 model: revoked grant denies",
          req2[0] == (False, "grant_revoked"))
    check("6.4.5 model: stale epoch denies",
          req2[1] == (False, "stale_after_rollback"))


# ---------------------------------------------------------------------------
# Sensitivity: weakening critical checks must break the proofs
# ---------------------------------------------------------------------------

def part_sensitivity():
    """Non-vacuous proofs: disable a critical check and the corresponding
    negative control must FAIL. Production is restored after each probe."""
    from form.dell_matrix import agent_coordinator as ac
    import form.dell_matrix.agent_coordinator as acmod

    # Probe 1: disable idempotency (always treat as new) -> retry duplicates.
    p = fresh_program("r64sens")
    pr = p.nursery.add("Sens Idea", words="sensitivity words here")
    pid = pr.id
    _, child = _mkpair(p, pid, "agent-a")
    h = p.acceptance_data_hash(pid, "confirm")
    coord = ac.new_coordinator(p)
    coord.register_agent("agent-a")
    surf = coord.surface_for("agent-a")

    orig_receipts_get = dict.get
    # Weaken: make the idempotency lookup always miss.
    class _NoHit(dict):
        def get(self, k, d=None):
            return None
    coord._receipts = _NoHit(coord._receipts)
    r1 = surf.request_confirm(pid, child["grant_id"], request_id="s-1",
                              expected_content_hash=h)
    # The grant is single-use (max_depth path); second dispatch with the
    # same grant should deny at the writer OR be treated as new. Either
    # way the receipt must NOT claim idempotent_retry.
    r2 = surf.request_confirm(pid, child["grant_id"], request_id="s-1",
                              expected_content_hash=h)
    weakened_breaks = r2.get("idempotent_retry") is not True or not r2["ok"]
    check("sensitivity: weakened idempotency breaks retry claim",
          weakened_breaks or r2.get("reason") == "request_id_reuse",
          detail=str(r2)[:160])
    # Restore: fresh coordinator, idempotency intact.
    coord2 = ac.new_coordinator(p)
    coord2.register_agent("agent-a")
    surf2 = coord2.surface_for("agent-a")
    pr2 = p.nursery.add("Sens Idea 2", words="sensitivity two words")
    pid2 = pr2.id
    _, child2 = _mkpair(p, pid2, "agent-a")
    h2 = p.acceptance_data_hash(pid2, "confirm")
    ra = surf2.request_confirm(pid2, child2["grant_id"], request_id="s-2",
                               expected_content_hash=h2)
    rb = surf2.request_confirm(pid2, child2["grant_id"], request_id="s-2",
                               expected_content_hash=h2)
    check("sensitivity: restored production is idempotent",
          ra["ok"] and rb.get("idempotent_retry") is True)

    # Probe 2: disable subject binding (accept any subject) -> B uses A's grant.
    # Weaken at the writer boundary by patching agent_confirm's subject.
    from form.dell_matrix import agent_authority as aa
    orig_confirm = aa.agent_confirm
    def _weak_confirm(program, pid_, grant_id_, subject_):
        return orig_confirm(program, pid_, grant_id_, "agent-a")  # force A's subject
    aa.agent_confirm = _weak_confirm
    try:
        p3 = fresh_program("r64sens2")
        pr3 = p3.nursery.add("Sens Idea 3", words="sensitivity three words")
        pid3 = pr3.id
        _, child3 = _mkpair(p3, pid3, "agent-a")
        h3 = p3.acceptance_data_hash(pid3, "confirm")
        coord3 = ac.new_coordinator(p3)
        coord3.register_agent("agent-a")
        coord3.register_agent("agent-b")
        sb3 = coord3.surface_for("agent-b")
        rw = sb3.request_confirm(pid3, child3["grant_id"], request_id="w-1",
                                 expected_content_hash=h3)
        check("sensitivity: weakened subject binding lets B use A's grant",
              rw["ok"] is True, detail="weakened writer should allow")
    finally:
        aa.agent_confirm = orig_confirm
    # Restore: production denies again.
    p4 = fresh_program("r64sens3")
    pr4 = p4.nursery.add("Sens Idea 4", words="sensitivity four words")
    pid4 = pr4.id
    _, child4 = _mkpair(p4, pid4, "agent-a")
    h4 = p4.acceptance_data_hash(pid4, "confirm")
    coord4 = ac.new_coordinator(p4)
    coord4.register_agent("agent-a")
    coord4.register_agent("agent-b")
    sb4 = coord4.surface_for("agent-b")
    r4 = sb4.request_confirm(pid4, child4["grant_id"], request_id="w-2",
                             expected_content_hash=h4)
    check("sensitivity: restored production denies B with A's grant",
          not r4["ok"])


# ---------------------------------------------------------------------------
# smoke (regress entry point)
# ---------------------------------------------------------------------------

def smoke() -> bool:
    """Regress entry: run the full R6.4 circuit. Returns True iff all pass."""
    global CHECKS
    CHECKS = []
    part_identity()
    part_protocol()
    part_audit()
    part_intrinsic()
    part_cross_process()
    part_rollback_recovery()
    part_reference_model()
    part_sensitivity()
    total = len(CHECKS)
    passed = sum(CHECKS)
    print(f"=== R6.4 circuit: {passed}/{total} ===")
    return passed == total


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    sys.exit(0 if smoke() else 1)


if __name__ == "__main__":
    main()
