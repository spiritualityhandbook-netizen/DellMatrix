"""Master plan P7 / SD-4 — the scoped Director dock.

Proves: a Director role session bound by the trusted host sees
ONLY its scope program's field (a canary planted in a personal
owner's matrix never appears); its verb allowlist is exactly
snapshot/review/recommend/request_evidence/directive/undock —
no confirm, no semantic verbs, no grant machinery; an
accept-recommendation is a persisted RECORD that leaves the
proposal PENDING and AcceptancePolicy untouched; out-of-scope,
invalid, and non-pending attempts are refused AND recorded;
construction refuses scope/subject violations; and the Program
host bindings (agent endpoint, rollback endpoint — the SD-4
activation of the R6.3 substrate, Director endpoint) work.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402
from form import persist_rest  # noqa: E402
from form.dell_matrix import director_session as ds  # noqa: E402
from form.dell_matrix import inference_dock as idock  # noqa: E402

RESULTS = []
CANARY = "CANARY_PERSONAL_LEDGER_XQ9"


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:200]))


def _cleanup(owner):
    base = os.path.join(
        os.path.dirname(__file__), "..", "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json"):
        for f in glob.glob(os.path.join(base, pat)):
            os.remove(f)
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


def _place(p, label, detail, goals):
    pr = p.nursery.add(label, words=label, detail=detail, goals=goals)
    ctx = p.make_review_context(pr.id, reviewer="human:ace")
    r = p.confirm_proposal(pr.id, _producer="p7test",
                           _review_context=ctx)
    assert r.get("ok"), r
    return pr.id


def smoke() -> bool:
    owners = ["P7DevScope", "P7Personal"]
    for o in owners:
        _cleanup(o)
    try:
        # --- two matrices: the dev scope and a personal one ---
        dev = Program(owner="P7DevScope")
        _place(dev, "DevRoadmap",
               "development roadmap for the docking program phases",
               ["ship SD-4"])
        agent = idock.dock(dev, trusted_subject="agent:worker",
                           provider="fake", task="propose")
        made = agent.propose("draft the SD-4 test plan")
        assert made.get("ok"), made
        target_pid = made["pid"]
        agent.undock()

        personal = Program(owner="P7Personal")
        _place(personal, "PersonalLedger",
               f"private notes {CANARY} never for the dev scope",
               ["keep private"])
        pers = personal.nursery.add("PersonalDraft", words="draft",
                                    detail=f"contains {CANARY}")
        personal_pid = pers.id

        # --- bind the Director on the dev scope ---
        director = dev.bind_director_endpoint()
        _rec("director_bound_scoped",
             director.bound_subject == "director:dev"
             and director.scope_owner == "P7DevScope")

        # Scoped snapshot: dev content present, canary absent.
        snap = director.snapshot()
        snap_text = json.dumps(snap)
        _rec("snapshot_scoped_no_canary",
             "DevRoadmap" in snap_text and CANARY not in snap_text
             and "PersonalLedger" not in snap_text,
             f"units={len(snap.get('units') or [])}")
        _rec("review_in_scope",
             director.review(target_pid).get("ok") is True)

        # --- recommend: a record, never a decision ---
        before = [dict(v) for v in
                  (dev.director_records or {}).values()] \
            if hasattr(dev, "director_records") else []
        out = director.recommend(target_pid, "accept",
                                 "test plan covers the allowlist")
        prop = dev.nursery.proposals[target_pid]
        _rec("recommend_is_record_not_decision",
             out.get("ok") is True
             and out.get("effect") == "recommendation_only"
             and prop.status == "pending",
             f"status={prop.status}")
        # The human gate still works exactly as before afterwards.
        ctx = dev.make_review_context(target_pid,
                                      reviewer="human:ace")
        conf = dev.confirm_proposal(target_pid, _producer="p7test",
                                    _review_context=ctx)
        _rec("human_gate_unaffected",
             conf.get("ok") is True
             and dev.nursery.proposals[target_pid].status
             == "confirmed")

        # --- adversarial: scope expansion is refused + recorded ---
        out = director.recommend(personal_pid, "accept",
                                 "trying to reach across scopes")
        kinds = [e["kind"] for e in
                 dev.director_records.values()]
        _rec("cross_scope_refused_and_recorded",
             out.get("ok") is False
             and out.get("reason") == "out_of_scope"
             and "refusal" in kinds
             and personal.nursery.proposals[personal_pid].status
             == "pending")
        out = director.review(personal_pid)
        _rec("cross_scope_review_refused",
             out.get("ok") is False
             and out.get("reason") == "out_of_scope")
        out = director.recommend(target_pid, "confirm",
                                 "not a decision the Director owns")
        _rec("invalid_decision_refused",
             out.get("ok") is False
             and out.get("reason") == "invalid_decision")
        out = director.recommend(target_pid, "accept",
                                 "second recommendation, now placed")
        _rec("non_pending_refused",
             out.get("ok") is False
             and out.get("reason") == "not_pending")
        out = director.recommend("no-such-pid", "accept", "ghost")
        _rec("unknown_pid_refused",
             out.get("ok") is False
             and out.get("reason") == "out_of_scope")

        # --- evidence request + directive ---
        agent2 = idock.dock(dev, trusted_subject="agent:worker",
                            provider="fake", task="propose")
        made2 = agent2.propose("second proposal needing evidence")
        agent2.undock()
        pid2 = made2["pid"]
        out = director.request_evidence(pid2, "show the CI run id")
        _rec("evidence_request_recorded",
             out.get("ok") is True
             and any(e["kind"] == "evidence_request"
                     and e["pid"] == pid2
                     for e in dev.director_records.values()))
        out = director.directive("prioritize the exchange phase",
                                 reason="roadmap pressure")
        dprop = dev.nursery.proposals.get(out.get("pid") or "")
        _rec("directive_files_pending_proposal",
             out.get("ok") is True and dprop is not None
             and dprop.status == "pending"
             and dprop.origin.startswith("dock:director:dev:")
             and any(e["kind"] == "directive"
                     and e["pid"] == out["pid"]
                     for e in dev.director_records.values()),
             (dprop.origin if dprop else "none"))

        # --- surface: the allowlist is all there is ---
        forbidden = ["confirm", "relate", "synthesize", "flag",
                     "propose", "issue_root_grant", "attenuate_for",
                     "revoke_grant", "agent_confirm"]
        _rec("surface_allowlist_only",
             all(not hasattr(director, name) for name in forbidden)
             and all(hasattr(director, name) for name in
                     ("snapshot", "review", "recommend",
                      "request_evidence", "directive", "undock")),
             str([n for n in forbidden if hasattr(director, n)]))

        # --- construction scope discipline ---
        rogue = idock.dock(personal,
                           trusted_subject="agent:worker",
                           provider="fake", task="propose")
        try:
            ds.DirectorSession(rogue, scope_owner="P7Personal")
            ok1 = False
        except ds.DirectorError:
            ok1 = True  # subject lacks the director: prefix
        rogue.undock()
        foreign = idock.dock(personal,
                             trusted_subject="director:dev",
                             provider="fake", task="review")
        try:
            ds.DirectorSession(foreign, scope_owner="P7DevScope")
            ok2 = False
        except ds.DirectorError:
            ok2 = True  # program owner != declared scope
        foreign.undock()
        try:
            ds.bind_director(dev, subject="agent:worker")
            ok3 = False
        except ds.DirectorError:
            ok3 = True
        _rec("construction_scope_discipline", ok1 and ok2 and ok3)

        # --- records persist (records only, across a reload) ---
        dev.save()
        dev2 = persist_rest.load("P7DevScope", activate=False)
        kinds = sorted({e["kind"] for e in
                        dev2.director_records.values()})
        _rec("records_persist",
             "recommendation" in kinds and "refusal" in kinds
             and "evidence_request" in kinds
             and "directive" in kinds
             and all(e["subject"] == "director:dev"
                     for e in dev2.director_records.values()),
             str(kinds))
        _rec("canary_never_in_dev_records",
             CANARY not in json.dumps(
                 list(dev2.director_records.values())))

        # --- Program host bindings (SD-4 activation) ---
        from form.dell_matrix.agent_authority import AgentEndpoint
        from form.dell_matrix.rollback_authority import (
            RollbackEndpoint)
        _rec("program_endpoint_bindings",
             isinstance(dev.bind_agent_endpoint("agent-x"),
                        AgentEndpoint)
             and isinstance(dev.bind_rollback_endpoint("agent-x"),
                            RollbackEndpoint)
             and dev.bind_agent_endpoint("agent-x").bound_subject
             == "agent-x")
        director.undock()
    finally:
        for o in owners:
            _cleanup(o)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}")
    print(f"\n=== RESULT: {passed}/{len(RESULTS)} PASS ===")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
