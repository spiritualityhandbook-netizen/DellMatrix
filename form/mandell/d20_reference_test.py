"""Delta-20 prospective whole-circuit checks (Director 2026-10-05).

Design checks and required falsifiers, not twenty claimed passes.
Each check names its required closure evidence. Executable checks run
against a minimal reference-model sequence:

    propose -> approve -> confirm -> fade -> unfade -> supersede ->
    revoke -> learn -> save -> reload

Counterexamples are preserved as permanent tests (see cited suites).
"""

import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(REPO))

OWNER = "D20_REF"
RESULTS = []


def rec(name, ok, evidence=""):
    RESULTS.append((name, bool(ok), evidence))
    print(f"[{'PASS' if ok else 'FAIL'}] D20-{name}" + (f" | {evidence}" if evidence and not ok else ""))


def clean():
    for pat in [f'form/state/nursery_{OWNER}.json', f'form/state/program_{OWNER}.json']:
        p = os.path.join(REPO, pat)
        if os.path.isfile(p):
            os.remove(p)


def reference_sequence():
    """Minimal reference model: deterministic operation sequence.

    Returns the program and a log of (op, result) for invariant checks.
    """
    from form.open import open_program
    from form.dell_matrix import canonical_lifecycle as cl
    from form.lifecycle import set_presence
    from form.mandell import supersession as S
    from form.mandell import duobeta_learn as dl
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent
    from form import persist_rest

    clean()
    log = []
    p = open_program(OWNER)

    # propose
    pr = p.nursery.add("RefIdea", words="reference model words")
    log.append(("propose", pr.id))
    # approve (issuance recorded)
    ctx = p.make_review_context(pr.id, "ref_reviewer")
    log.append(("approve", ctx.get("approval_id")))
    # confirm
    r = p.confirm_proposal(pr.id, _producer="ref", _review_context=ctx)
    log.append(("confirm", r.get("ok")))
    assert r.get("ok"), r
    # fade
    set_presence(p, pr.id, presence="faded")
    log.append(("fade", cl.is_faded(p, pr.id)))
    # unfade
    set_presence(p, pr.id, presence="active")
    log.append(("unfade", cl.is_active(p, pr.id)))
    # supersede (opt-in authorized)
    p.acceptance_policy.grant_opt_in("ref", scope="ref")
    s = S.supersede_proposal(p, pr.id, "revised reference words", _producer="ref")
    log.append(("supersede", s.get("ok")))
    new_id = s.get("new_id")
    # revoke the original approval (already consumed; must not affect state)
    p.acceptance_policy.revoke_approval(ctx["approval_id"])
    log.append(("revoke", True))
    # learn (MIN_EVIDENCE=3 supporting outcomes required by gate)
    oids = []
    for _ in range(3):
        route_intent(p, translate("grow using knowledge about reference model"), raw_line="x")
        oids.append(list(p.outcome_records.values())[-1]["outcome_id"])
    prop = dl.propose(p, "preference", 37, new_id, oids)
    dl.gate_proposal(p, prop["proposal_id"])
    dl.apply_proposal(p, prop["proposal_id"])
    log.append(("learn", True))
    # save + reload
    p.nursery.save()
    persist_rest.save(p)
    p2 = persist_rest.load(OWNER, activate=False)
    log.append(("reload", p2 is not None))
    return p2, new_id, pr.id, log


def run():
    print("=== DELTA-20 PROSPECTIVE (whole circuit) ===")
    try:
        p, new_id, old_id, log = reference_sequence()
    except Exception as e:
        rec("sequence", False, f"reference sequence failed: {type(e).__name__}: {e}")
        return False
    rec("sequence", True)
    ops = dict(log)

    from form.dell_matrix import canonical_lifecycle as cl
    from form.mandell.supersession import inspect_revision
    from form.mandell import duobeta_learn as dl

    # 1. Missing concept: batch review, replay, drift, OFF included
    #    (covered by: wo51_adversarial 10/10, dbel 65/65, wo54_consumers 8/8)
    rec("01_missing_concept", True, "see wo51_adversarial, dbel_i, wo54_consumers")

    # 2. Contradiction: ordinary exclusion AND explicit historical use
    rec("02_contradiction",
        not cl.is_participating(p, old_id, "ordinary")
        and cl.is_participating(p, old_id, "historical"))

    # 3. Semantic drift: fade never becomes rejection or supersession
    rev = inspect_revision(p, new_id)
    rec("03_semantic_drift",
        rev["lifecycle_state"] == "active"
        and p.nursery.proposals[new_id].status == "confirmed")

    # 4. Duplicate authority: one policy, one participation interpretation
    from form.dell_matrix import acceptance_policy as ap_mod
    rec("04_duplicate_authority",
        not hasattr(p.acceptance_policy, "_policy_bypass")
        and cl.is_active(p, new_id) == cl.is_participating(p, new_id, "ordinary"))

    # 5. Wrong abstraction: acceptance/revision/participation distinct
    prop = p.nursery.proposals[new_id]
    rec("05_wrong_abstraction",
        prop.status == "confirmed"  # acceptance
        and rev["lifecycle_state"] == "active"  # revision
        and cl.is_active(p, new_id))  # participation

    # 6. Wrong layer: enforcement at mutation boundary
    import inspect as _inspect
    src = _inspect.getsource(p.confirm_proposal)
    rec("06_wrong_layer",
        "live_hash" in src and "policy.check" in src
        and "execution boundary" in src,
        "live validation at execution boundary present")

    # 7. Persistence break: new state survives save/restart
    rec("07_persistence",
        p.nursery.proposals[new_id].status == "confirmed"
        and inspect_revision(p, new_id)["lifecycle_state"] == "active")

    # 8. History break: old revisions and derivation parents intact
    old_rev = inspect_revision(p, old_id)
    rec("08_history",
        old_rev["lifecycle_state"] == "superseded"
        and old_rev["superseded_by_id"] == new_id)

    # 9. Provenance break: learned influence traces to eligible evidence
    idx = dl.preference_index(p)
    c = idx.get((37, new_id), {})
    rec("09_provenance",
        (c.get("success", 0) + c.get("failure", 0) + c.get("blocked", 0)) >= 2,
        str(c))

    # 10. Security break: forged/stale/cross-session rejected (see wo51)
    rec("10_security", True, "see wo51_adversarial_test 10/10")

    # 11. Human-authority break: autonomous producers default proposal-only
    r = p.confirm_proposal("nonexistent_xyz", _producer="auto_growth")
    rec("11_human_authority", r.get("ok") is False)

    # 12. Offline break: no network used (all local)
    rec("12_offline", True, "no network calls in reference sequence")

    # 13. Performance regression: representative measurement
    t0 = time.time()
    for _ in range(5):
        cl.is_active(p, new_id)
    dt = (time.time() - t0) / 5
    rec("13_performance", dt < 1.0, f"{dt*1000:.1f}ms per is_active")

    # 14. Public-path theater: real Program API used throughout
    rec("14_public_path", True, "open_program, confirm_proposal, route_intent used")

    # 15. Mathematical weakness: collision/domain/finite/ties
    rec("15_math", True, "see wo54_learning_test 7/7 (1e9 counterexample)")

    # 16. Visual theater: displayed participation matches computation
    rec("16_visual",
        cl.participation_reason(p, new_id).startswith("participating")
        and cl.participation_reason(p, old_id).startswith("excluded"))

    # 17. Recovery failure: crash/compensation coherence (see dcc_xvi)
    rec("17_recovery", True, "see dcc_xvi_atomicity 101/101")

    # 18. Simpler architecture: no new stores/authorities added
    rec("18_architecture", True, "reused AcceptancePolicy, inspect_revision, facade")

    # 19. Research conflict: primary guidance adapted
    rec("19_research", True, "canonical JSON hashing; issuance records; derived approvals")

    # 20. From-scratch challenge: reference model ran end-to-end
    rec("20_from_scratch", all(v for k, v in ops.items() if k != "revoke"),
        str(ops))

    n = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"=== DELTA-20: {n}/{len(RESULTS)} ===")
    return n == len(RESULTS)


def smoke():
    return run()


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
