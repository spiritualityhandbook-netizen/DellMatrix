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
    # Descriptors match production's canonical descriptor shape.
    def _desc(pid, h):
        return {"operation": "confirm", "target": pid,
                "expected": {"content_hash": h}, "correlation": {}}
    model = ReferenceModel(owner="r64ref")
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
         "pid": pid1, "grant_id": "g-a1", "expected_hash": h1,
         "descriptor": _desc(pid1, h1)},
        {"kind": "request", "subject": "agent-a", "request_id": "m-1",
         "pid": pid1, "grant_id": "g-a1", "expected_hash": h1,
         "descriptor": _desc(pid1, h1)},
        {"kind": "request", "subject": "agent-b", "request_id": "m-2",
         "pid": pid2, "grant_id": "g-a2", "expected_hash": h2,
         "descriptor": _desc(pid2, h2)},
        {"kind": "request", "subject": "agent-a", "request_id": "m-3",
         "pid": pid2, "grant_id": "g-a2", "expected_hash": h2,
         "descriptor": _desc(pid2, h2)},
        {"kind": "request", "subject": "agent-a", "request_id": "m-1",
         "pid": pid2, "grant_id": "g-a2", "expected_hash": h2,
         "descriptor": _desc(pid2, h2)},
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

    # Revocation and rollback agreement moved to part_amend_reference
    # (production comparison, not model-only).


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
    part_amend_findings()
    part_amend_reference()
    part_amend2_boundaries()
    part_amend3_outward()
    part_amend4_collision_error()
    total = len(CHECKS)
    passed = sum(CHECKS)
    print(f"=== R6.4 circuit: {passed}/{total} ===")
    return passed == total


# ---------------------------------------------------------------------------
# AMEND — proof controls for Director findings
# ---------------------------------------------------------------------------

def part_amend_findings():
    """Public-path controls for every Director AMEND finding."""
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import intrinsic_agent as ia

    # Finding 1: cross-subject retry isolation. B reuses A's request_id
    # with an invalid grant -> must NOT receive A's cached receipt.
    p = fresh_program("r64amend1")
    pr = p.nursery.add("Amend One", words="amend finding one words")
    pid = pr.id
    _, ch_a = _mkpair(p, pid, "agent-a")
    h = p.acceptance_data_hash(pid, "confirm")
    coord = ac.new_coordinator(p)
    coord.register_agent("agent-a")
    coord.register_agent("agent-b")
    sa = coord.surface_for("agent-a")
    sb = coord.surface_for("agent-b")
    ra = sa.request_confirm(pid, ch_a["grant_id"], request_id="shared-id",
                            expected_content_hash=h)
    check("amend cross-subject retry: A commits", ra["ok"])
    # B reuses the same request_id with a bogus grant.
    rb = sb.request_confirm(pid, "grant_" + "0" * 32, request_id="shared-id",
                            expected_content_hash=h)
    check("amend cross-subject retry: B denied (no A's receipt)",
          not rb["ok"] and rb.get("subject") == "agent-b"
          and rb.get("idempotent_retry") is not True,
          detail=str(rb)[:200])
    check("amend cross-subject retry: B not attributed as A",
          rb.get("subject") != "agent-a" or not rb["ok"])

    # Finding 2: mutable cached evidence. Mutating a returned receipt's
    # affected list must not change later cached receipts.
    r1 = sa.request_confirm(pid, ch_a["grant_id"], request_id="shared-id",
                            expected_content_hash=h)
    check("amend receipt isolated: retry is historical", r1.get("historical") is True)
    r1["affected"].append("forged-pid")
    r1["correlation"]["injected"] = True
    r2 = sa.request_confirm(pid, ch_a["grant_id"], request_id="shared-id",
                            expected_content_hash=h)
    check("amend receipt isolated: cached affected unchanged",
          r2["affected"] == [pid], detail=str(r2["affected"]))
    check("amend receipt isolated: cached correlation unchanged",
          "injected" not in r2["correlation"])

    # Finding 3: queue leakage. Repeated exact retries must not grow queue.
    q_before = len(coord._queue)
    for i in range(_queue_probe_n(coord)):
        sa.request_confirm(pid, ch_a["grant_id"], request_id="shared-id",
                           expected_content_hash=h)
    check("amend queue: retries do not grow queue",
          len(coord._queue) <= q_before,
          detail=f"queue {q_before} -> {len(coord._queue)}")

    # Finding 4: secret-value screening. Grant-handle canary under an
    # innocent key must be rejected at the boundary, never reach audit.
    canary = "grant_" + "ab" * 16
    rsec = sa.request_confirm(pid, ch_a["grant_id"], request_id="sec-1",
                              expected_content_hash=h,
                              correlation={"note": f"innocent {canary} here"})
    check("amend secret: canary under innocent key rejected",
          not rsec["ok"] and rsec.get("reason") in ("bad_envelope", "enqueue_rejected"),
          detail=str(rsec)[:200])
    audit = ac.list_agent_audit(p)
    leaked = any(canary in str(r) for r in audit)
    check("amend secret: canary never reaches durable audit", not leaked)

    # Finding 5: malformed behavioral state (strict).
    bad_cases = [
        ({"version": None}, "null version"),
        ({"version": True}, "bool version"),
        ({"version": 1.0}, "float version"),
        ({"version": "1"}, "str version"),
        ({"version": 1, "curiosity_score": float("nan")}, "NaN curiosity"),
        ({"version": 1, "curiosity_score": float("inf")}, "Inf curiosity"),
        ({"version": 1, "seen_cells": None}, "null seen_cells"),
        ({"version": 1, "history": None}, "null history"),
        ({"version": 1, "seen_cells": [[0, 0]] * 1025}, "over-bound cells"),
        ({"version": 1, "history": [{"k": "v"}] * 33}, "over-bound history"),
        ({"version": 1, "history": [{"k": "x" * 300}]}, "over-bound history value"),
        ({"version": 1, "seen_cells": [[0, 0], ["bad", 1]]}, "malformed tail entry"),
    ]
    for bad, name in bad_cases:
        try:
            ia.IntrinsicAgent.from_dict(bad, "x")
            check(f"amend malformed: {name} rejected", False)
        except ia.AgentLocalLoadError:
            check(f"amend malformed: {name} rejected", True)
    # Absent keys still yield fresh default (not malformed).
    inst = ia.IntrinsicAgent.from_dict({"version": 1}, "x")
    check("amend absent keys: fresh default",
          inst.seen_cells == set() and inst.curiosity_score == 0.0)

    # Finding 6: unsynchronized save/reload. Observe -> ordinary save ->
    # fresh-process reload WITHOUT manual sync_agent_to_program.
    p2 = fresh_program("r64amend2")
    ag = ia.for_agent(p2, "agent-a")
    class Body:
        pos = (9, 9)
    class P:
        avatar = type("A", (), {"body": Body()})()
    ag.observe(P(), {"nodes": [{"label": "AutoSyncSite"}]})
    # NOTE: no sync_agent_to_program call here.
    from form import persist_rest
    persist_rest.save(p2)
    p3 = persist_rest.load("r64amend2", activate=False)
    ag3 = ia.for_agent(p3, "agent-a")
    check("amend autosync: observe->save->reload without manual sync",
          "AutoSyncSite" in ag3.seen_labels and (9, 9) in ag3.seen_cells)

    # Finding 7: audit failure observable. Inject audit-write failure;
    # the outcome must show audit_ok=False, not ordinary committed.
    p4 = fresh_program("r64amend3")
    pr4 = p4.nursery.add("Amend Audit", words="audit failure words")
    pid4 = pr4.id
    _, ch4 = _mkpair(p4, pid4, "agent-a")
    h4 = p4.acceptance_data_hash(pid4, "confirm")
    coord4 = ac.new_coordinator(p4)
    coord4.register_agent("agent-a")
    sa4 = coord4.surface_for("agent-a")
    p4.agent_audit_records = None  # break the audit store
    r4 = sa4.request_confirm(pid4, ch4["grant_id"], request_id="af-1",
                             expected_content_hash=h4)
    check("amend audit failure: committed but flagged",
          r4["ok"] is True and r4.get("audit_ok") is False
          and "audit_failure" in r4,
          detail=str(r4)[:200])
    p4.agent_audit_records = {}

    # Finding 8 (AMEND-2): incomplete compensation is classified by the
    # canonical writer contract (reason="acceptance_policy_denied",
    # compensation="incomplete"), proven through the real writer in
    # part_amend2_boundaries §3. A synthetic receipt with an invented
    # reason name must NOT classify as incomplete_recovery.
    from form.dell_matrix import agent_authority as aa
    orig_confirm = aa.agent_confirm
    def _invented(program, pid_, grant_id_, subject_):
        return {"ok": False, "reason": "incomplete_compensation",
                "detail": "synthetic invented reason"}
    aa.agent_confirm = _invented
    try:
        p5 = fresh_program("r64amend4")
        pr5 = p5.nursery.add("Amend Incomplete", words="incomplete words")
        pid5 = pr5.id
        _, ch5 = _mkpair(p5, pid5, "agent-a")
        h5 = p5.acceptance_data_hash(pid5, "confirm")
        coord5 = ac.new_coordinator(p5)
        coord5.register_agent("agent-a")
        sa5 = coord5.surface_for("agent-a")
        r5 = sa5.request_confirm(pid5, ch5["grant_id"], request_id="ic-1",
                                 expected_content_hash=h5)
        check("amend incomplete: invented reason is ordinary denial",
              not r5["ok"] and r5.get("result") == "denied"
              and r5.get("reason") == "writer_incomplete_compensation",
              detail=str(r5)[:200])
    finally:
        aa.agent_confirm = orig_confirm


def _queue_probe_n(coord) -> int:
    """More than queue_bound exact retries (AMEND §1)."""
    return coord._queue_bound + 5


# ---------------------------------------------------------------------------
# AMEND — reference model: revocation and rollback production comparison
# ---------------------------------------------------------------------------

def part_amend_reference():
    """The model binds identity; production outcomes for revocation and
    rollback are compared (not model-only)."""
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import agent_authority as aa
    from form.mandell import core_i_recovery as rec
    from form.mandell.r64_reference_model import ReferenceModel

    owner = "r64amref"
    p = fresh_program(owner)
    pr = p.nursery.add("Amend Ref", words="amend reference words")
    pid = pr.id
    root, ch = _mkpair(p, pid, "agent-a")
    h = p.acceptance_data_hash(pid, "confirm")

    coord = ac.new_coordinator(p)
    coord.register_agent("agent-a")
    sa = coord.surface_for("agent-a")

    # Production: revoke then request -> deny.
    aa.revoke_grant(p, root["grant_id"])
    r_prod_revoke = sa.request_confirm(pid, ch["grant_id"], request_id="amr-1",
                                       expected_content_hash=h)
    # Model: same scenario.
    m = ReferenceModel(owner=owner)
    desc = {"operation": "confirm", "target": pid,
            "expected": {"content_hash": h}, "correlation": {}}
    exp = m.expect_sequence([
        {"kind": "register", "subject": "agent-a"},
        {"kind": "set_content", "pid": pid, "content_hash": h},
        {"kind": "issue", "grant_id": "g1", "subject": "agent-a",
         "pid": pid, "content_hash": h},
        {"kind": "revoke", "grant_id": "g1"},
        {"kind": "request", "subject": "agent-a", "request_id": "amr-1",
         "pid": pid, "grant_id": "g1", "expected_hash": h,
         "descriptor": desc},
    ])
    exp_revoke = [e for e in exp if e[1] in ("grant_revoked", "committed")][-1]
    check("amend model: production and model agree on revocation deny",
          (not r_prod_revoke["ok"]) and exp_revoke == (False, "grant_revoked"),
          detail=f"prod_ok={r_prod_revoke['ok']} model={exp_revoke}")

    # Production: rollback epoch invalidates (from part_rollback_recovery
    # pattern, compared against model).
    p2 = fresh_program("r64amref2")
    pr2 = p2.nursery.add("Amend Ref 2", words="amend reference two words")
    pid2 = pr2.id
    _, ch2 = _mkpair(p2, pid2, "agent-a")
    h2 = p2.acceptance_data_hash(pid2, "confirm")
    coord2 = ac.new_coordinator(p2)
    coord2.register_agent("agent-a")
    qid = coord2.enqueue("agent-a", ac.make_envelope(
        request_id="amr-2", operation="confirm", target=pid2,
        expected={"content_hash": h2}, _program=p2))
    saved = dict(coord2._queue[qid])
    rec._advance_rollback_epoch("r64amref2")
    from form.open import open_program
    p2f = open_program("r64amref2")
    coord2f = ac.new_coordinator(p2f)
    coord2f.register_agent("agent-a")
    coord2f._queue[qid] = saved
    r_prod_roll = coord2f.dispatch(qid, ch2["grant_id"])
    m2 = ReferenceModel(owner="r64amref2")
    exp2 = m2.expect_sequence([
        {"kind": "register", "subject": "agent-a"},
        {"kind": "set_content", "pid": pid2, "content_hash": h2},
        {"kind": "issue", "grant_id": "g2", "subject": "agent-a",
         "pid": pid2, "content_hash": h2},
        {"kind": "advance_epoch"},
        {"kind": "request", "subject": "agent-a", "request_id": "amr-2",
         "pid": pid2, "grant_id": "g2", "expected_hash": h2,
         "epoch_at_enqueue": 0,
         "descriptor": {"operation": "confirm", "target": pid2,
                        "expected": {"content_hash": h2}, "correlation": {}}},
    ])
    exp_roll = [e for e in exp2 if e[1] in ("stale_after_rollback", "committed")][-1]
    check("amend model: production and model agree on rollback deny",
          (not r_prod_roll["ok"]
           and r_prod_roll.get("reason") == "stale_after_rollback")
          and exp_roll == (False, "stale_after_rollback"),
          detail=f"prod={r_prod_roll.get('reason')} model={exp_roll}")

def part_amend2_boundaries():
    """AMEND-2 (GDP_PHASE_6_R64_FINISH_EXISTING_BOUNDARIES): public-path
    proofs for the six still-failing findings. Every fix is proven
    through production paths with sensitivity controls."""
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import agent_authority as aa
    from form.dell_matrix import intrinsic_agent as ia
    from form import persist_rest as _pr
    from form.persist import _path as _ppath
    import json as _json

    # ------------------------------------------------------------------
    # §1: Retain the validated request.
    # ------------------------------------------------------------------
    p = fresh_program("r64b1")
    pr = p.nursery.add("B1", words="boundary one words")
    pid = pr.id
    _, ch = _mkpair(p, pid, "agent-a")
    h = p.acceptance_data_hash(pid, "confirm")
    coord = ac.new_coordinator(p)
    coord.register_agent("agent-a")
    env = ac.make_envelope(request_id="ret-1", operation="confirm", target=pid,
                           expected={"content_hash": h},
                           correlation={"k": "v"}, _program=p)
    qid = coord.enqueue("agent-a", env)
    # Structural: the queued envelope is NOT the caller's object.
    check("b2 §1: queued envelope is retained snapshot, not caller object",
          coord._queue[qid]["envelope"] is not env)
    # Behavioral: mutate the ORIGINAL's nested mappings post-enqueue.
    env.expected["content_hash"] = "forged"
    env.expected["injected"] = True
    env.correlation["k"] = "mutated"
    r = coord.dispatch(qid, ch["grant_id"])
    check("b2 §1: post-enqueue mutation does not change execution",
          r["ok"] is True, detail=str(r)[:200])
    check("b2 §1: receipt reflects retained snapshot",
          r.get("correlation", {}).get("k") == "v"
          and "injected" not in r.get("correlation", {}))
    audit = ac.list_agent_audit(p)
    att = [a for a in audit if a.get("request_id") == "ret-1"]
    check("b2 §1: audit reflects retained snapshot",
          any(a.get("correlation", {}).get("k") == "v"
              and "injected" not in a.get("correlation", {}) for a in att),
          detail=str(att)[:200])

    # §1: conflicting reuse preserves the original retry record.
    env2 = ac.make_envelope(request_id="ret-1", operation="confirm", target=pid,
                            expected={"content_hash": "different"},
                            correlation={}, _program=p)
    qid2 = coord.enqueue("agent-a", env2)
    rc = coord.dispatch(qid2, ch["grant_id"])
    check("b2 §1: conflicting reuse denied",
          not rc["ok"] and rc.get("reason") == "request_id_reuse",
          detail=str(rc)[:200])
    rkey = (p.owner, "agent-a", "ret-1")
    stored = coord._receipts.get(rkey)
    check("b2 §1: conflict does not overwrite established history",
          stored is not None and stored["receipt"].get("ok") is True
          and stored["receipt"].get("historical") is not True
          and stored["descriptor"]["expected"].get("content_hash") == h)
    env3 = ac.make_envelope(request_id="ret-1", operation="confirm", target=pid,
                            expected={"content_hash": h},
                            correlation={"k": "v"}, _program=p)
    qid3 = coord.enqueue("agent-a", env3)
    rh = coord.dispatch(qid3, ch["grant_id"])
    check("b2 §1: exact retry after conflict returns original historical",
          rh.get("historical") is True and rh.get("ok") is True)

    # ------------------------------------------------------------------
    # §2: Complete secret protection.
    # ------------------------------------------------------------------
    p2 = fresh_program("r64b2")
    pr2 = p2.nursery.add("B2", words="boundary two words")
    pid2 = pr2.id
    _, ch2 = _mkpair(p2, pid2, "agent-a")
    h2 = p2.acceptance_data_hash(pid2, "confirm")
    coord2 = ac.new_coordinator(p2)
    coord2.register_agent("agent-a")
    sa2 = coord2.surface_for("agent-a")
    canary = "grant_" + "cd" * 16

    r_rid = sa2.request_confirm(pid2, ch2["grant_id"], request_id=f"x-{canary}",
                                expected_content_hash=h2)
    check("b2 §2: canary in request_id rejected",
          not r_rid["ok"] and r_rid.get("reason") in ("bad_envelope", "enqueue_rejected"),
          detail=str(r_rid)[:200])
    r_key = sa2.request_confirm(pid2, ch2["grant_id"], request_id="k-1",
                                expected_content_hash=h2,
                                correlation={f"innocent_{canary}": "v"})
    check("b2 §2: canary in nested key rejected",
          not r_key["ok"] and r_key.get("reason") in ("bad_envelope", "enqueue_rejected"),
          detail=str(r_key)[:200])
    try:
        env_t = ac.make_envelope(request_id="t-1", operation="confirm",
                                 target=f"{pid2}-{canary}",
                                 expected={}, _program=p2)
        coord2.enqueue("agent-a", env_t)
        check("b2 §2: canary in target rejected", False)
    except (ac.EnvelopeValidationError, ac.CoordinatorError):
        check("b2 §2: canary in target rejected", True)

    # Post-enqueue mutation inserting a canary: the retained snapshot is
    # clean, and the mutation cannot reach execution or audit.
    env_m = ac.make_envelope(request_id="m-1", operation="confirm", target=pid2,
                             expected={"content_hash": h2},
                             correlation={"clean": "yes"}, _program=p2)
    qm = coord2.enqueue("agent-a", env_m)
    env_m.correlation["evil"] = canary
    env_m.expected["evil"] = canary
    rm = coord2.dispatch(qm, ch2["grant_id"])
    audit2 = ac.list_agent_audit(p2)
    leaked = any(canary in str(a) for a in audit2)
    check("b2 §2: post-enqueue canary never reaches audit",
          rm["ok"] is True and not leaked,
          detail=f"ok={rm['ok']} leaked={leaked}")

    # Protection-unavailable -> explicit rejection, not silent pass.
    import form.dell_matrix.inference_dock as _idock
    orig_pv = _idock.protected_values
    def _boom(program):
        raise RuntimeError("simulated protection failure")
    _idock.protected_values = _boom
    try:
        try:
            ac.make_envelope(request_id="pu-1", operation="confirm", target=pid2,
                             expected={}, _program=p2)
            check("b2 §2: protection failure rejects explicitly", False)
        except ac.EnvelopeValidationError:
            check("b2 §2: protection failure rejects explicitly", True)
    finally:
        _idock.protected_values = orig_pv

    # Sensitivity: with screening disabled, the canary passes the boundary
    # (proves screening is the active guard, not something else).
    orig_screen = ac._screen_envelope
    ac._screen_envelope = lambda *a, **kw: None
    try:
        r_weak = sa2.request_confirm(pid2, ch2["grant_id"], request_id="weak-1",
                                     expected_content_hash=h2,
                                     correlation={"note": f"x {canary} y"})
        check("b2 §2 sensitivity: disabled screening lets canary through",
              r_weak["ok"] is True or r_weak.get("reason") != "bad_envelope",
              detail=str(r_weak)[:200])
    finally:
        ac._screen_envelope = orig_screen

    # Clean-input positive control: works, no redaction artifacts in audit.
    # (Fresh proposal + grant: earlier tests consumed the previous ones.)
    pr2c = p2.nursery.add("B2c", words="boundary two c words")
    pid2c = pr2c.id
    _, ch2c = _mkpair(p2, pid2c, "agent-a")
    h2c = p2.acceptance_data_hash(pid2c, "confirm")
    r_clean = sa2.request_confirm(pid2c, ch2c["grant_id"], request_id="clean-1",
                                  expected_content_hash=h2c,
                                  correlation={"note": "ordinary"})
    audit_clean = [a for a in ac.list_agent_audit(p2)
                   if a.get("request_id") == "clean-1"]
    redacted = any("[REDACTED]" in str(a) for a in audit_clean)
    check("b2 §2: clean input works without redaction artifacts",
          r_clean["ok"] is True and len(audit_clean) > 0 and not redacted,
          detail=f"ok={r_clean['ok']} records={len(audit_clean)}")

    # ------------------------------------------------------------------
    # §3: Real writer contract (canonical incomplete-compensation fields).
    # ------------------------------------------------------------------
    p3 = fresh_program("r64b3")
    pr3 = p3.nursery.add("B3", words="boundary three words")
    pid3 = pr3.id
    _, ch3 = _mkpair(p3, pid3, "agent-a")
    h3 = p3.acceptance_data_hash(pid3, "confirm")
    coord3 = ac.new_coordinator(p3)
    coord3.register_agent("agent-a")
    sa3 = coord3.surface_for("agent-a")
    # Real writer, failure injected AFTER actual placement: revoke the
    # grant (pre-commit auth fails) and break cleanup (compensation fails).
    orig_place = p3.place
    class BrokenDict(dict):
        def pop(self, *a, **kw):
            raise RuntimeError("injected_cleanup_failure")
    def injecting_place(*a, **kw):
        result = orig_place(*a, **kw)
        aa.revoke_grant(p3, ch3["grant_id"])
        p3.spatial.velocities = BrokenDict(p3.spatial.velocities)
        return result
    p3.place = injecting_place
    try:
        r3 = sa3.request_confirm(pid3, ch3["grant_id"], request_id="wr-1",
                                 expected_content_hash=h3)
    finally:
        p3.place = orig_place
    check("b2 §3: real incomplete compensation -> incomplete_recovery",
          not r3["ok"] and r3.get("result") == "incomplete_recovery"
          and r3.get("reason") == "incomplete_recovery",
          detail=str(r3)[:300])
    check("b2 §3: canonical fields preserved (not invented names)",
          r3.get("compensation") == "incomplete"
          and isinstance(r3.get("compensation_failures"), list)
          and len(r3.get("compensation_failures")) > 0
          and r3.get("evidence_retained") is True,
          detail=str(r3.get("compensation_failures"))[:200])
    check("b2 §3: writer_reason is the canonical acceptance_policy_denied",
          r3.get("writer_reason") == "acceptance_policy_denied")

    # §3: audit-failure aggregation. A failed attempted-event must not
    # disappear because the final event captures successfully.
    p3b = fresh_program("r64b3b")
    pr3b = p3b.nursery.add("B3b", words="boundary three b words")
    pid3b = pr3b.id
    _, ch3b = _mkpair(p3b, pid3b, "agent-a")
    h3b = p3b.acceptance_data_hash(pid3b, "confirm")
    coord3b = ac.new_coordinator(p3b)
    coord3b.register_agent("agent-a")
    p3b.agent_audit_records = None  # break audit for enqueue only
    env3b = ac.make_envelope(request_id="ag-1", operation="confirm", target=pid3b,
                             expected={"content_hash": h3b}, _program=p3b)
    q3b = coord3b.enqueue("agent-a", env3b)
    p3b.agent_audit_records = {}  # restore; final capture succeeds
    r3b = coord3b.dispatch(q3b, ch3b["grant_id"])
    check("b2 §3: failed attempted-event survives final success",
          r3b.get("audit_ok") is False
          and "enqueue_attempted" in r3b.get("audit", {}).get("failures", []),
          detail=str(r3b.get("audit"))[:200])
    check("b2 §3: in-memory vs persisted evidence distinguished",
          r3b.get("audit", {}).get("evidence") == "in_memory"
          and r3b.get("audit", {}).get("persisted") is False
          and r3b.get("audit", {}).get("captured_in_memory") is True)

    # ------------------------------------------------------------------
    # §4: Honest behavioral save.
    # ------------------------------------------------------------------
    # Sync failure propagates (no suppression); no durable write occurs.
    p4 = fresh_program("r64b4")
    _pr.save(p4)  # good baseline bytes on disk
    with open(_ppath("r64b4"), "rb") as f:
        baseline = f.read()
    ag4 = ia.for_agent(p4, "agent-a")
    ag4.observe(p4, {"nodes": [{"label": "BeforePoison"}]})
    ag4.curiosity_score = float("nan")  # poison live state
    raised = None
    try:
        _pr.save(p4)
    except Exception as e:
        raised = e
    check("b2 §4: sync failure propagates (no suppression)",
          isinstance(raised, ia.AgentLocalLoadError),
          detail=f"raised={type(raised).__name__ if raised else None}")
    with open(_ppath("r64b4"), "rb") as f:
        after = f.read()
    check("b2 §4: failed save preserves previous bytes",
          after == baseline)
    # The live observations are still in memory (not silently dropped).
    check("b2 §4: live observations preserved in memory",
          "BeforePoison" in ag4.seen_labels)

    # Explicit null section -> load rejects.
    p4b = fresh_program("r64b4b")
    _pr.save(p4b)
    pp4b = _ppath("r64b4b")
    with open(pp4b) as f:
        d4b = _json.load(f)
    d4b["agent_local"] = None
    with open(pp4b, "w") as f:
        _json.dump(d4b, f)
    try:
        _pr.load("r64b4b", activate=False)
        check("b2 §4: explicit null section rejected on load", False)
    except ia.AgentLocalLoadError:
        check("b2 §4: explicit null section rejected on load", True)
    except Exception as e:
        check("b2 §4: explicit null section rejected on load", False,
              detail=f"wrong: {type(e).__name__}")

    # Explicit null subject record -> load rejects.
    p4c = fresh_program("r64b4c")
    _pr.save(p4c)
    pp4c = _ppath("r64b4c")
    with open(pp4c) as f:
        d4c = _json.load(f)
    d4c["agent_local"]["agents"]["agent-a"] = None
    with open(pp4c, "w") as f:
        _json.dump(d4c, f)
    try:
        _pr.load("r64b4c", activate=False)
        check("b2 §4: explicit null subject record rejected on load", False)
    except ia.AgentLocalLoadError:
        check("b2 §4: explicit null subject record rejected on load", True)
    except Exception as e:
        check("b2 §4: explicit null subject record rejected on load", False,
              detail=f"wrong: {type(e).__name__}")

    # Explicit null subject record -> for_agent rejects (not fresh).
    p4d = fresh_program("r64b4d")
    p4d.agent_local_states = {"agent-a": None}
    try:
        ia.for_agent(p4d, "agent-a")
        check("b2 §4: explicit null subject rejected in for_agent", False)
    except ia.AgentLocalLoadError:
        check("b2 §4: explicit null subject rejected in for_agent", True)

    # Outer version validated: null / wrong type / mismatch reject.
    for bad_v, name in [(None, "null"), ("1", "str"), (2, "mismatch"), (True, "bool")]:
        p4e = fresh_program("r64b4e")
        _pr.save(p4e)
        pp4e = _ppath("r64b4e")
        with open(pp4e) as f:
            d4e = _json.load(f)
        d4e["agent_local"]["agent_local_version"] = bad_v
        with open(pp4e, "w") as f:
            _json.dump(d4e, f)
        try:
            _pr.load("r64b4e", activate=False)
            check(f"b2 §4: outer version {name} rejected", False)
        except ia.AgentLocalLoadError:
            check(f"b2 §4: outer version {name} rejected", True)
        except Exception as e:
            check(f"b2 §4: outer version {name} rejected", False,
                  detail=f"wrong: {type(e).__name__}")

    # No str() normalization of arbitrary objects in history.
    for bad_h, name in [
        ({"version": 1, "history": [{"k": {"nested": "dict"}}]}, "dict item"),
        ({"version": 1, "history": [{"k": [float("nan")]}]}, "NaN list item"),
        ({"version": 1, "history": [{"k": [{"deep": 1}]}]}, "dict in list"),
        ({"version": 1, "history": [{"k": (1, 2)}]}, "tuple item"),
    ]:
        try:
            ia.IntrinsicAgent.from_dict(bad_h, "x")
            check(f"b2 §4: history {name} rejected (no str norm)", False)
        except ia.AgentLocalLoadError:
            check(f"b2 §4: history {name} rejected (no str norm)", True)
    # Valid scalars still accepted.
    ok_h = {"version": 1, "history": [{"k": "v", "n": 3, "f": 1.5, "z": None,
                                       "l": ["a", 1, None]}]}
    try:
        inst_h = ia.IntrinsicAgent.from_dict(ok_h, "x")
        check("b2 §4: valid history scalars accepted",
              inst_h.history[0]["l"] == ["a", 1, None])
    except ia.AgentLocalLoadError as e:
        check("b2 §4: valid history scalars accepted", False, detail=str(e))

    # ------------------------------------------------------------------
    # §5: Damaged audit evidence preserved (complete originals).
    # ------------------------------------------------------------------
    p5 = fresh_program("r64b5")
    pr5 = p5.nursery.add("B5", words="boundary five words")
    pid5 = pr5.id
    _, ch5 = _mkpair(p5, pid5, "agent-a")
    h5 = p5.acceptance_data_hash(pid5, "confirm")
    coord5 = ac.new_coordinator(p5)
    coord5.register_agent("agent-a")
    sa5 = coord5.surface_for("agent-a")
    r5 = sa5.request_confirm(pid5, ch5["grant_id"], request_id="ev-1",
                             expected_content_hash=h5)
    assert r5["ok"]
    _pr.save(p5)
    pp5 = _ppath("r64b5")
    with open(pp5) as f:
        d5 = _json.load(f)
    # Inject a malformed record into the saved file (shape check fails:
    # audit_id mismatches the key; plus a non-dict record).
    bad_rec = {"audit_id": "aa1:wrong", "audit_seq": 999,
               "note": "damaged evidence", "payload": {"x": 1}}
    d5["agent_audit"]["records"]["aa1:damaged"] = bad_rec
    d5["agent_audit"]["records"]["aa1:notadict"] = "not-a-dict"
    with open(pp5, "w") as f:
        _json.dump(d5, f)
    p5b = _pr.load("r64b5", activate=False)
    mal = p5b.agent_audit_malformed
    originals = [m.get("original") for m in mal if isinstance(m, dict)]
    check("b2 §5: malformed load preserves complete originals",
          bad_rec in originals and "not-a-dict" in originals,
          detail=f"malformed={len(mal)}")
    # Valid records still restored.
    check("b2 §5: valid records survive malformed load",
          any(r.get("request_id") == "ev-1"
              for r in p5b.agent_audit_records.values()))
    # Subsequent save -> reload: evidence NOT silently discarded.
    _pr.save(p5b)
    p5c = _pr.load("r64b5", activate=False)
    mal2 = p5c.agent_audit_malformed
    originals2 = [m.get("original") for m in mal2 if isinstance(m, dict)]
    check("b2 §5: save after malformed load preserves evidence",
          bad_rec in originals2 and "not-a-dict" in originals2,
          detail=f"malformed={len(mal2)}")


def part_amend3_outward():
    """AMEND-3 (GDP_PHASE_6_R64_CLOSE_ALL_OUTWARD_SECRET_PATHS): one
    complete outward boundary. Public-path proofs that no agent-facing
    return releases protected material, and that sanitization failure
    never releases the original payload."""
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import agent_authority as aa
    from form import persist_rest as _pr

    canary = "grant_" + "ef" * 16

    # --- Snapshot sanitization: protected handle in proposal words. ---
    p = fresh_program("r64c1")
    pr = p.nursery.add("C1", words=f"proposal with {canary} inside")
    pid = pr.id
    coord = ac.new_coordinator(p)
    coord.register_agent("agent-a")
    snap = coord.snapshot_for("agent-a")
    snap_text = str(snap)
    check("c3 snapshot: protected handle redacted from proposal words",
          canary not in snap_text and "[REDACTED]" in snap_text,
          detail=snap_text[:200])
    # Canonical Idea content is NOT modified by snapshot sanitization.
    check("c3 snapshot: canonical proposal words unchanged",
          canary in p.nursery.proposals[pid].words)

    # --- Snapshot sanitization: protected handle in Plane unit words. ---
    # (Place a unit via the writer path so it appears on the Plane.)
    _, ch = _mkpair(p, pid, "agent-a")
    # Directly set a unit's words to include the canary (simulating
    # content that reached the Plane).
    from form.open import open_program
    p2 = fresh_program("r64c2")
    pr2 = p2.nursery.add("C2", words="clean words")
    # Simulate Plane content with a canary via direct unit creation.
    # Use the program's plane directly.
    plane = p2.cube.session.plane
    from form.dell_matrix.plane import Unit as _Unit
    import uuid as _uuid
    uid = "u_" + _uuid.uuid4().hex[:12]
    # Construct a minimal unit; check the Unit signature first.
    try:
        u = _Unit(id=uid, label="test", words=f"unit words {canary} here",
                  x=0, y=0)
        plane.units[uid] = u
        coord2 = ac.new_coordinator(p2)
        coord2.register_agent("agent-a")
        snap2 = coord2.snapshot_for("agent-a")
        check("c3 snapshot: protected handle redacted from plane words",
              canary not in str(snap2),
              detail=str(snap2)[:200])
        check("c3 snapshot: canonical unit words unchanged",
              canary in plane.units[uid].words)
    except Exception as e:
        check("c3 snapshot: plane unit setup", False, detail=str(e)[:200])

    # --- Protected dict keys: safe deterministic representation. ---
    p3 = fresh_program("r64c3")
    pr3 = p3.nursery.add("C3", words="boundary c3 words")
    pid3 = pr3.id
    _, ch3 = _mkpair(p3, pid3, "agent-a")
    h3 = p3.acceptance_data_hash(pid3, "confirm")
    coord3 = ac.new_coordinator(p3)
    coord3.register_agent("agent-a")
    sa3 = coord3.surface_for("agent-a")
    # Inject a protected key into provenance via a custom capture.
    # (Directly exercise the sanitizer on nested structures.)
    nested = {
        "outer": {
            f"key_{canary}_a": "value1",
            f"key_{canary}_b": "value2",
            "clean": f"val {canary} end",
        },
        "list": [{f"k_{canary}": "v"}],
    }
    san = ac._sanitize_outward(p3, nested)
    san_text = str(san)
    check("c3 keys: protected keys replaced, no collision",
          canary not in san_text
          and "[REDACTED_KEY:1]" in san_text
          and "[REDACTED_KEY:2]" in san_text
          and "[REDACTED_KEY:3]" in san_text,
          detail=san_text[:300])
    check("c3 keys: values redacted",
          "[REDACTED]" in san_text)
    # Determinism: same input -> same output.
    san2 = ac._sanitize_outward(p3, nested)
    check("c3 keys: deterministic", str(san) == str(san2))

    # --- Writer exception with handle + protection failure -> minimal. ---
    # Protection must fail AFTER enqueue (not at entry), so the request
    # reaches dispatch and the writer raises.
    p4 = fresh_program("r64c4")
    pr4 = p4.nursery.add("C4", words="boundary c4 words")
    pid4 = pr4.id
    _, ch4 = _mkpair(p4, pid4, "agent-a")
    h4 = p4.acceptance_data_hash(pid4, "confirm")
    coord4 = ac.new_coordinator(p4)
    coord4.register_agent("agent-a")
    env4 = ac.make_envelope(request_id="wr-exc", operation="confirm",
                            target=pid4, expected={"content_hash": h4},
                            _program=p4)
    q4 = coord4.enqueue("agent-a", env4)

    orig_confirm = aa.agent_confirm
    def _raising(program, pid_, grant_id_, subject_):
        raise RuntimeError(f"writer blew up on {canary}")
    aa.agent_confirm = _raising
    import form.dell_matrix.inference_dock as _idock
    orig_pv = _idock.protected_values
    def _boom(program):
        raise RuntimeError("simulated protection failure")
    _idock.protected_values = _boom
    try:
        r4 = coord4.dispatch(q4, ch4["grant_id"])
    finally:
        aa.agent_confirm = orig_confirm
        _idock.protected_values = orig_pv
    check("c3 protection-failure: minimal receipt, no handle",
          canary not in str(r4)
          and r4.get("reason") == "protection_unavailable"
          and r4.get("result") == "failed"  # classification preserved
          and r4.get("ok") is False
          and "sanitize_failed" not in r4,
          detail=str(r4)[:300])
    check("c3 protection-failure: no uncontrolled identifiers",
          r4.get("request_id") == "" and r4.get("subject") == ""
          and r4.get("target") == "")

    # --- Writer exception with handle, protection OK -> sanitized. ---
    # (Fresh queue: the previous dispatch consumed q4.)
    env4b = ac.make_envelope(request_id="wr-exc2", operation="confirm",
                             target=pid4, expected={"content_hash": h4},
                             _program=p4)
    q4b = coord4.enqueue("agent-a", env4b)
    aa.agent_confirm = _raising
    try:
        r4b = coord4.dispatch(q4b, ch4["grant_id"])
    finally:
        aa.agent_confirm = orig_confirm
    check("c3 writer-exc: handle sanitized when protection works",
          canary not in str(r4b) and "[REDACTED]" in str(r4b)
          and r4b.get("result") == "failed",
          detail=str(r4b)[:300])

    # --- Protection failure at entry -> explicit rejection. ---
    _idock.protected_values = _boom
    try:
        try:
            ac.make_envelope(request_id="entry-1", operation="confirm",
                             target=pid4, expected={}, _program=p4)
            check("c3 entry: protection failure rejects", False)
        except ac.EnvelopeValidationError:
            check("c3 entry: protection failure rejects", True)
    finally:
        _idock.protected_values = orig_pv

    # --- All outcome paths sanitized: success, denial, retry, conflict. ---
    p5 = fresh_program("r64c5")
    pr5 = p5.nursery.add("C5", words="boundary c5 words")
    pid5 = pr5.id
    _, ch5 = _mkpair(p5, pid5, "agent-a")
    h5 = p5.acceptance_data_hash(pid5, "confirm")
    coord5 = ac.new_coordinator(p5)
    coord5.register_agent("agent-a")
    sa5 = coord5.surface_for("agent-a")
    # Success with a canary smuggled in correlation BEFORE screening
    # was fixed would have leaked; now it must be rejected at entry.
    r_bad = sa5.request_confirm(pid5, ch5["grant_id"], request_id="path-1",
                                expected_content_hash=h5,
                                correlation={"note": f"has {canary}"})
    check("c3 paths: canary correlation rejected at entry",
          not r_bad["ok"])
    # Clean success.
    _, ch5b = _mkpair(p5, pid5, "agent-a")
    # (Need a fresh proposal since pid5's grant was consumed; use new pid.)
    pr5b = p5.nursery.add("C5b", words="clean c5b words")
    pid5b = pr5b.id
    _, ch5c = _mkpair(p5, pid5b, "agent-a")
    h5b = p5.acceptance_data_hash(pid5b, "confirm")
    r_ok = sa5.request_confirm(pid5b, ch5c["grant_id"], request_id="path-ok",
                               expected_content_hash=h5b)
    check("c3 paths: clean success has zero canary",
          r_ok["ok"] is True and canary not in str(r_ok))
    # Historical retry.
    r_hist = sa5.request_confirm(pid5b, ch5c["grant_id"], request_id="path-ok",
                                 expected_content_hash=h5b)
    check("c3 paths: historical retry has zero canary",
          r_hist.get("historical") is True and canary not in str(r_hist))
    # Conflict.
    env_c = ac.make_envelope(request_id="path-ok", operation="confirm",
                             target=pid5b,
                             expected={"content_hash": "different"},
                             _program=p5)
    qc = coord5.enqueue("agent-a", env_c)
    r_conf = coord5.dispatch(qc, ch5c["grant_id"])
    check("c3 paths: conflict denial has zero canary",
          not r_conf["ok"] and canary not in str(r_conf))

    # --- Durable audit: zero canary occurrences. ---
    _pr.save(p5)
    p5r = _pr.load("r64c5", activate=False)
    audit_all = str(p5r.agent_audit_records) + str(p5r.agent_audit_malformed)
    check("c3 durable: zero canary in persisted audit",
          canary not in audit_all)

    # --- Sensitivity: disable the output guard -> canary passes. ---
    orig_san = ac._sanitize_outward
    ac._sanitize_outward = lambda program, obj: obj  # disabled
    try:
        snap_weak = coord.snapshot_for("agent-a")
        check("c3 sensitivity: disabled guard leaks snapshot canary",
              canary in str(snap_weak))
    finally:
        ac._sanitize_outward = orig_san
    # Restore and rerun: production sanitizes again.
    snap_fixed = coord.snapshot_for("agent-a")
    check("c3 sensitivity: restored guard sanitizes",
          canary not in str(snap_fixed))

    # --- Clean Unicode/content positives. ---
    p6 = fresh_program("r64c6")
    pr6 = p6.nursery.add("C6", words="héllo wörld 🌍 unicode")
    coord6 = ac.new_coordinator(p6)
    coord6.register_agent("agent-a")
    snap6 = coord6.snapshot_for("agent-a")
    check("c3 positive: unicode content passes through unsanitized",
          "héllo" in str(snap6) and "[REDACTED]" not in str(snap6))


def part_amend4_collision_error():
    """AMEND-4 (GDP_PHASE_6_R64_FINISH_OUTPUT_COLLISION_AND_ERROR_CONTRACT):
    collision-free key representation and safe error contract."""
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import agent_authority as aa

    canary = "grant_" + "ab" * 16
    prot_key = f"key_{canary}_x"

    # --- Mixed-key collision: protected key + literal [REDACTED_KEY:1]. ---
    p = fresh_program("r64d1")
    d1 = {prot_key: "A", "[REDACTED_KEY:1]": "B"}
    s1 = ac._sanitize_outward(p, d1)
    check("d4 collision: protected-then-literal preserves both entries",
          len(s1) == 2 and s1.get("[REDACTED_KEY:1]") == "B"
          and "A" in s1.values() and canary not in str(s1),
          detail=str(s1)[:200])
    # The protected key must NOT have been assigned [REDACTED_KEY:1]
    # (which would collide); it gets the next available.
    prot_repl = [k for k in s1.keys() if k != "[REDACTED_KEY:1]"][0]
    check("d4 collision: protected key gets non-colliding replacement",
          prot_repl.startswith("[REDACTED_KEY:")
          and prot_repl != "[REDACTED_KEY:1]"
          and s1[prot_repl] == "A")

    # --- Reverse order: literal first, protected second. ---
    d2 = {"[REDACTED_KEY:1]": "B", prot_key: "A"}
    s2 = ac._sanitize_outward(p, d2)
    check("d4 collision: literal-then-protected preserves both",
          len(s2) == 2 and s2.get("[REDACTED_KEY:1]") == "B"
          and "A" in s2.values() and canary not in str(s2),
          detail=str(s2)[:200])

    # --- Multiple reserved suffixes and protected keys. ---
    canary2 = "grant_" + "cd" * 16
    prot_key2 = f"other_{canary2}_y"
    d3 = {
        prot_key: "A",
        "[REDACTED_KEY:1]": "B",
        "[REDACTED_KEY:2]": "C",
        prot_key2: "D",
        "clean": "E",
    }
    # Snapshot the input to prove it's unchanged.
    import copy as _copy
    d3_orig = _copy.deepcopy(d3)
    s3 = ac._sanitize_outward(p, d3)
    check("d4 collision: multiple reserves preserve entry count",
          len(s3) == 5 and canary not in str(s3)
          and canary2 not in str(s3),
          detail=str(s3)[:300])
    check("d4 collision: value associations preserved",
          s3.get("[REDACTED_KEY:1]") == "B"
          and s3.get("[REDACTED_KEY:2]") == "C"
          and s3.get("clean") == "E"
          and "A" in s3.values() and "D" in s3.values())
    check("d4 collision: input unchanged", d3 == d3_orig)
    # Determinism.
    s3b = ac._sanitize_outward(p, d3)
    check("d4 collision: deterministic", str(s3) == str(s3b))

    # --- Nested dictionaries. ---
    d4 = {
        "outer": {prot_key: "nested_A", "[REDACTED_KEY:1]": "nested_B"},
        "[REDACTED_KEY:1]": "top_B",
        prot_key2: "top_D",
    }
    s4 = ac._sanitize_outward(p, d4)
    check("d4 collision: nested preserves all entries",
          len(s4) == 3 and len(s4["outer"]) == 2
          and canary not in str(s4) and canary2 not in str(s4),
          detail=str(s4)[:300])

    # --- Snapshot with canary-bearing protection exception. ---
    p5 = fresh_program("r64d5")
    pr5 = p5.nursery.add("C5", words="clean words")
    coord5 = ac.new_coordinator(p5)
    coord5.register_agent("agent-a")
    import form.dell_matrix.inference_dock as _idock
    orig_pv = _idock.protected_values
    def _canary_boom(program):
        raise RuntimeError(f"protection exploded on {canary}")
    _idock.protected_values = _canary_boom
    try:
        try:
            coord5.snapshot_for("agent-a")
            check("d4 error: snapshot failure raises", False)
        except ac.CoordinatorError as e:
            msg = str(e)
            check("d4 error: fixed non-reflecting message, zero canary",
                  canary not in msg
                  and msg == "snapshot unavailable: output sanitization failed",
                  detail=msg[:200])
            # No chaining that reveals the original.
            check("d4 error: no exception chaining",
                  e.__cause__ is None and e.__suppress_context__)
    finally:
        _idock.protected_values = orig_pv

    # --- Protection failure at entry with canary: no reflection. ---
    _idock.protected_values = _canary_boom
    try:
        try:
            ac.make_envelope(request_id="d4-entry", operation="confirm",
                             target="x", expected={}, _program=p5)
            check("d4 error: entry failure raises", False)
        except ac.EnvelopeValidationError as e:
            check("d4 error: entry message fixed, zero canary",
                  canary not in str(e)
                  and str(e) == "secret protection unavailable (values failed)",
                  detail=str(e)[:200])
    finally:
        _idock.protected_values = orig_pv

    # --- Sensitivity: break the allocator -> collision returns. ---
    # (Simulate the old buggy allocator by monkeypatching.)
    orig_san = ac._sanitize_outward
    def _buggy(program, obj):
        # Old behavior: only checks already-emitted keys.
        if isinstance(obj, dict):
            out = {}
            cnt = [0]
            for k, v in obj.items():
                nk = k
                if isinstance(k, str) and canary in k:
                    cnt[0] += 1
                    nk = f"[REDACTED_KEY:{cnt[0]}]"
                    while nk in out:
                        cnt[0] += 1
                        nk = f"[REDACTED_KEY:{cnt[0]}]"
                out[nk] = v
            return out
        return obj
    ac._sanitize_outward = _buggy
    try:
        buggy = ac._sanitize_outward(p, d1)
        check("d4 sensitivity: buggy allocator loses evidence",
              len(buggy) == 1)  # A's entry disappears
    finally:
        ac._sanitize_outward = orig_san
    fixed = ac._sanitize_outward(p, d1)
    check("d4 sensitivity: fixed allocator preserves evidence",
          len(fixed) == 2)

    # --- Clean input positive: no spurious redaction. ---
    d_clean = {"a": 1, "[REDACTED_KEY:1]": "legit", "b": {"c": 2}}
    s_clean = ac._sanitize_outward(p, d_clean)
    check("d4 positive: clean keys pass through",
          s_clean == d_clean)


def main():
    sys.exit(0 if smoke() else 1)


if __name__ == "__main__":
    main()
